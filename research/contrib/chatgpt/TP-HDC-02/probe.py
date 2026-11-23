"""TP-HDC-02: frozen source-free actual-byte memory frontier. Development only."""
from __future__ import annotations
import hashlib
import json
import random
import resource
import sys
import time
from collections import OrderedDict

import numpy as np

PREREG_COMMIT = "201b7bd0fb898a108f8e9c4e152a9d83bba0b8f9"
SEEDS = (101, 202, 303, 404)
CASES = ((128, 32), (128, 128), (512, 128), (512, 512), (2048, 512))
MAGIC = b"TP02"


def hashed(tag: str, *components: object) -> bytes:
    s = tag + "/" + "/".join(map(str, components))
    return hashlib.sha256(s.encode("ascii")).digest()


def law(seed: int, task: int, c: int, a: int) -> float:
    return 0.8 if (hashed("TP-HDC-02|law|v1", seed, task, c, a)[0] & 1) else 0.2


def read3(block: bytes | bytearray, index: int) -> int:
    shift = index * 3
    offset, bit = shift // 8, shift % 8
    value = block[offset] >> bit
    if bit > 5:
        value |= block[offset + 1] << (8 - bit)
    return value & 7


def write3(block: bytearray, index: int, value: int) -> None:
    shift = index * 3
    offset, bit = shift // 8, shift % 8
    window = block[offset] | ((block[offset + 1] << 8) if bit > 5 else 0)
    window = (window & ~(7 << bit)) | ((value & 7) << bit)
    block[offset] = window & 255
    if bit > 5:
        block[offset + 1] = (window >> 8) & 255


def count_index(c: int, a: int, outcome: int) -> int:
    return 4 * c + 2 * a + outcome


def beta(block: bytes | bytearray, c: int, a: int) -> float:
    n0, n1 = (read3(block, count_index(c, a, y)) for y in (0, 1))
    return (n1 + 1) / (n0 + n1 + 2)


def bump(block: bytearray, c: int, a: int, y: int) -> bool:
    index = count_index(c, a, y)
    old = read3(block, index)
    if old == 7:
        return True
    write3(block, index, old + 1)
    return False


def checkpoint(data: bytes) -> bytes:
    payload = MAGIC + data
    return payload + hashlib.sha256(payload).digest()


def verify_snapshot(data: bytes, byte_budget: int) -> bytes:
    if (not isinstance(data, bytes) or len(data) != byte_budget + 36
            or data[:4] != MAGIC
            or hashlib.sha256(data[:-32]).digest() != data[-32:]):
        raise ValueError("TPHDC02_CHECKPOINT_INVALID")
    return data[4:-32]


class Exact:
    """Five bytes/task including 16-bit task tag, LRU or priority retention."""
    def __init__(self, budget: int, mode: str):
        self.budget, self.mode = budget, mode
        self.capacity = budget // 5
        self.table: OrderedDict[int, bytearray] = OrderedDict()
        self.clips = 0

    def _priority(self, task: int) -> int:
        return int.from_bytes(hashed("TP-HDC-02|priority|v1", task)[:8], "little")

    def observe(self, task: int, c: int, a: int, y: int) -> None:
        if task not in self.table:
            if len(self.table) == self.capacity:
                if self.mode == "lru":
                    self.table.popitem(last=False)
                else:
                    worst = max(self.table, key=lambda t: (self._priority(t), t))
                    if (self._priority(task), task) >= (self._priority(worst), worst):
                        return
                    del self.table[worst]
            self.table[task] = bytearray(3)
        self.clips += int(bump(self.table[task], c, a, y))
        if self.mode == "lru":
            self.table.move_to_end(task)

    def forecast(self, task: int, c: int, a: int) -> float:
        buf = self.table.get(task)
        return beta(buf, c, a) if buf is not None else 0.5

    def snapshot(self) -> bytes:
        buf = bytearray(self.budget)
        for k, (task, counts) in enumerate(self.table.items()):
            pos = 5 * k
            buf[pos:pos+2] = (task + 1).to_bytes(2, "little")
            buf[pos+2:pos+5] = counts
        return checkpoint(bytes(buf))

    def restore(self, data: bytes) -> None:
        raw = verify_snapshot(data, self.budget)
        self.table.clear()
        for offset in range(0, self.capacity * 5, 5):
            t = int.from_bytes(raw[offset:offset+2], "little")
            if t:
                self.table[t-1] = bytearray(raw[offset+2:offset+5])
        if len(self.table) > self.capacity:
            raise ValueError("TPHDC02_EXACT_OVER_CAPACITY")


class Hashed:
    """Eight 3-bit counters in each 3-byte hash bucket; 3 bytes/bucket."""
    def __init__(self, budget: int):
        self.budget, self.slots = budget, budget // 3
        self.data = bytearray(budget)
        self.clips = 0

    def _start(self, task: int) -> int:
        h = hashed("TP-HDC-02|bucket|v1", task)
        return 3 * (int.from_bytes(h[:8], "little") % self.slots)

    def forecast(self, task: int, c: int, a: int) -> float:
        s = self._start(task)
        return beta(self.data[s:s+3], c, a)

    def observe(self, task: int, c: int, a: int, y: int) -> None:
        s = self._start(task)
        b = self.data[s:s+3]
        self.clips += int(bump(b, c, a, y))
        self.data[s:s+3] = b

    def snapshot(self) -> bytes:
        return checkpoint(bytes(self.data))

    def restore(self, data: bytes) -> None:
        self.data[:] = verify_snapshot(data, self.budget)


class Hypervector:
    """Int8 learned channel; regenerate deterministic keys, cache one task only."""
    def __init__(self, budget: int):
        self.budget = budget
        self.v = np.zeros(budget, dtype=np.int8)
        self.cached_task: int | None = None
        self.cache: dict[tuple[int, int, int], np.ndarray] = {}
        self.clips = 0
        self.key_cache_peak_bytes = 0

    def _key(self, task: int, c: int, a: int, outcome: int) -> np.ndarray:
        if self.cached_task != task:
            self.cache.clear()
            self.cached_task = task
        k = (c, a, outcome)
        if k not in self.cache:
            seed = int.from_bytes(hashed("TP-HDC-02|key|v1", task, c, a, outcome)[:8], "little")
            rng = np.random.Generator(np.random.PCG64(seed))
            self.cache[k] = (rng.integers(0, 2, size=self.budget, dtype=np.int8) * 2 - 1)
            self.key_cache_peak_bytes = max(self.key_cache_peak_bytes, len(self.cache) * self.budget)
        return self.cache[k]

    def forecast(self, task: int, c: int, a: int) -> float:
        v = self.v.astype(np.int32)
        x0 = max(0., float(np.dot(v, self._key(task,c,a,0).astype(np.int32))) / self.budget)
        x1 = max(0., float(np.dot(v, self._key(task,c,a,1).astype(np.int32))) / self.budget)
        return (x1 + 1.) / (x0 + x1 + 2.)

    def observe(self, task: int, c: int, a: int, y: int) -> None:
        next_value = self.v.astype(np.int16) + self._key(task, c, a, y)
        self.clips += int(np.count_nonzero((next_value > 127) | (next_value < -128)))
        np.clip(next_value, -128, 127, out=next_value)
        self.v[:] = next_value.astype(np.int8)

    def snapshot(self) -> bytes:
        return checkpoint(self.v.tobytes())

    def restore(self, data: bytes) -> None:
        self.v[:] = np.frombuffer(verify_snapshot(data, self.budget), dtype=np.int8)
        self.cache.clear()
        self.cached_task = None


class Unbounded:
    def __init__(self):
        self.table: dict[int,bytearray] = {}
    def observe(self, task:int,c:int,a:int,y:int)->None:
        bump(self.table.setdefault(task, bytearray(3)), c,a,y)
    def forecast(self,task:int,c:int,a:int)->float:
        x=self.table.get(task)
        return beta(x,c,a) if x is not None else 0.5


def score(model: object, seed: int, old_tasks: int) -> float:
    total = 0.
    for task in range(old_tasks):
        for c in (0,1):
            for a in (0,1):
                p = law(seed, task, c, a)
                q = model.forecast(task,c,a)
                total += p*(1-q)**2+(1-p)*q*q
    return total / (4 * old_tasks)


def run_case(budget: int, old_tasks: int, seed: int) -> dict:
    models = {
        "hdc": Hypervector(budget),
        "exact_lru": Exact(budget, "lru"),
        "exact_priority": Exact(budget, "priority"),
        "hashed": Hashed(budget),
        "unbounded_oracle": Unbounded(),
    }
    rng = random.Random(seed)
    update_time = {key: 0. for key in models}
    scores = {key: {} for key in models}
    for stage, tasks in (("before_B", range(old_tasks)), ("after_B", range(old_tasks, 2*old_tasks))):
        for task in tasks:
            for c in (0,1):
                for a in (0,1):
                    p = law(seed, task,c,a)
                    for _ in range(4):
                        y = int(rng.random() < p)
                        for name,model in models.items():
                            started = time.perf_counter()
                            model.observe(task,c,a,y)
                            update_time[name] += time.perf_counter() - started
        for name,model in models.items():
            scores[name][stage] = score(model, seed, old_tasks)
    result = {}
    for name, model in models.items():
        result[name] = {"A_before_B_expected_brier":scores[name]["before_B"],
                        "A_after_B_expected_brier":scores[name]["after_B"],
                        "A_drift":scores[name]["after_B"]-scores[name]["before_B"],
                        "update_cpu_wall_seconds":update_time[name]}
        if name == "unbounded_oracle":
            result[name]["persistent_bytes_for_two_stages"] = 5 * len(model.table)
            continue
        data = model.snapshot()
        assert len(data) == budget + 36, (name,len(data),budget)
        if isinstance(model, Hypervector):
            clone = Hypervector(budget)
        elif isinstance(model, Exact):
            clone = Exact(budget,model.mode)
        else:
            clone = Hashed(budget)
        clone.restore(data)
        for task in (0, old_tasks-1, old_tasks, 2*old_tasks-1):
            assert clone.forecast(task,0,0) == model.forecast(task,0,0),name
        damaged = bytearray(data)
        damaged[8] ^= 1
        try:
            clone.restore(bytes(damaged))
            raise AssertionError(name+" corruption accepted")
        except ValueError:
            pass
        result[name].update({"checkpoint_bytes":len(data),
                             "clips":model.clips,
                             "persistent_budget_bytes":budget})
        if isinstance(model,Exact):
            result[name].update({"resident_task_count":len(model.table),
                                 "resident_entry_bytes":len(model.table)*5})
        if isinstance(model,Hypervector):
            result[name]["peak_key_cache_bytes"] = model.key_cache_peak_bytes
    return result


def main() -> None:
    start = time.perf_counter()
    all_results = {}
    for budget, old_tasks in CASES:
        case = f"B{budget}_N{old_tasks}"
        all_results[case] = {str(seed):run_case(budget,old_tasks,seed) for seed in SEEDS}
    summ = {}
    for case, per_seed in all_results.items():
        arms=list(per_seed[str(SEEDS[0])].keys())
        summ[case] = {}
        for arm in arms:
            summ[case][arm]={
                "mean_post_B":sum(per_seed[str(s)][arm]["A_after_B_expected_brier"] for s in SEEDS)/len(SEEDS),
                "mean_drift":sum(per_seed[str(s)][arm]["A_drift"] for s in SEEDS)/len(SEEDS),
                "per_seed_post_B":[per_seed[str(s)][arm]["A_after_B_expected_brier"] for s in SEEDS],
                "per_seed_drift":[per_seed[str(s)][arm]["A_drift"] for s in SEEDS],
                "sum_update_wall_seconds":sum(per_seed[str(s)][arm]["update_cpu_wall_seconds"] for s in SEEDS),
            }
    candidate_cases = []
    for case, arms in summ.items():
        best = min(arms[x]["mean_post_B"] for x in ("exact_lru","exact_priority","hashed"))
        improved_mean = arms["hdc"]["mean_post_B"] <= best - 0.005
        beats_seeds = sum(all(arms["hdc"]["per_seed_post_B"][k] <= arms[x]["per_seed_post_B"][k] - 0.005
                              for x in ("exact_lru","exact_priority","hashed")) for k in range(4))
        drift_ok = all(d <= 0.02 for d in arms["hdc"]["per_seed_drift"])
        candidate_cases.append({"case":case,"hdc_mean_beats_best_by_005":improved_mean,
                                "hdc_beats_all_in_seeds":beats_seeds,"hdc_drift_all_seeds_ok":drift_ok})
    report={"schema":"yggdrasil.tp-hdc02.sourcefree-result.v1", "prereg_commit":PREREG_COMMIT,
            "source_free":True, "cases":list(map(list,CASES)), "seeds":list(SEEDS),
            "results":all_results,"summary":summ,"screen":candidate_cases,
            "positive_rule_rss_qualification":"UNVERIFIED_PER_ARM_RSS; overall-process high-water only",
            "process_maxrss_kb":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "elapsed_seconds":time.perf_counter()-start,
            "limitations":"Externally supplied task IDs; synthetic independent Bernoulli laws. Persistent state count excludes Python dictionary overhead, which is disclosed separately from learned byte cap. Per-arm RSS ratio not qualified. Not native learning or SCIENTIFIC_PASS."}
    print(json.dumps(report,sort_keys=True,separators=(",",":")))


if __name__ == "__main__":
    main()
