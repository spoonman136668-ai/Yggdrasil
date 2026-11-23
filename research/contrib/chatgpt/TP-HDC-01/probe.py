"""TP-HDC-01 source-free fixed-byte superposition falsification (DEV ONLY)."""
from __future__ import annotations
import hashlib
import json
import random
import sys
import time
import tracemalloc
from pathlib import Path

D = 4096
SEEDS = (101, 202, 303, 404)
TASKS = ("A", "B", "A", "C")
PROBS = {"A": (0.2, 0.8, 0.75, 0.25),
         "B": (0.8, 0.2, 0.25, 0.75),
         "C": (0.5, 0.5, 0.5, 0.5)}
INPUT_SPEC = ("TP-HDC-01|v1|probabilities:A:0.2,0.8,0.75,0.25;"
              "B:0.8,0.2,0.25,0.75;C:0.5,0.5,0.5,0.5|"
              "order:A,B,A,C|contexts:0,1|actions:0,1|"
              "obs-per-cell-per-stage:32|seeds:101,202,303,404|"
              "rng:python-random-MT19937")
INPUT_SHA256 = "ca8558bf6fb863939d0c0adc51991d53ca5211e9ed8602076a007c7b12676346"
MAGIC = b"TP01"


def key_bits(task: str, context: int, action: int, outcome: int) -> bytes:
    """4096 deterministic signs, each bit expanded by SHA256 counter-mode."""
    prefix = f"TP-HDC-01/key/v1/{task}/{context}/{action}/{outcome}/".encode()
    return bytes((digest >> j) & 1
                 for block in range(16)
                 for digest in hashlib.sha256(prefix + block.to_bytes(4, "big")).digest()
                 for j in range(8))


class Superposition:
    def __init__(self, *, sham: bool = False, learn: bool = True):
        self.v = bytearray([128]) * D
        self.sham, self.learn = sham, learn
        self.clips = 0
        self.keys = {(task, c, a, y): key_bits("A" if sham else task, c, a, y)
                     for task in ("A", "B", "C")
                     for c in (0, 1) for a in (0, 1) for y in (0, 1)}

    def forecast(self, task: str, context: int, action: int) -> float:
        amounts = []
        for outcome in (0, 1):
            bits = self.keys[task, context, action, outcome]
            similarity = sum((v - 128) if b else (128 - v)
                             for v, b in zip(self.v, bits)) / D
            amounts.append(max(0.0, similarity))
        return (amounts[1] + 1.0) / (amounts[0] + amounts[1] + 2.0)

    def observe(self, task: str, context: int, action: int, outcome: int) -> None:
        if not self.learn:
            return
        bits = self.keys[task, context, action, outcome]
        for i, bit in enumerate(bits):
            n = self.v[i] + (1 if bit else -1)
            if n < 0:
                n = 0
                self.clips += 1
            elif n > 255:
                n = 255
                self.clips += 1
            self.v[i] = n

    def snapshot(self) -> bytes:
        payload = MAGIC + bytes(self.v)
        return payload + hashlib.sha256(payload).digest()

    def restore(self, snapshot: bytes) -> None:
        if (not isinstance(snapshot, bytes) or len(snapshot) != D + 36
                or snapshot[:4] != MAGIC
                or hashlib.sha256(snapshot[:-32]).digest() != snapshot[-32:]):
            raise ValueError("TP_HDC_CHECKPOINT_REJECTED")
        self.v[:] = snapshot[4:-32]


class Counter:
    """Fixed 4096-byte uint8 allocation; task-aware or pooled."""
    def __init__(self, *, pooled: bool):
        self.data = bytearray(D)
        self.pooled = pooled
        self.clips = 0

    def _index(self, task: str, c: int, a: int, y: int) -> int:
        t = 0 if self.pooled else {"A": 0, "B": 1, "C": 2}[task]
        return 8 * t + 4 * c + 2 * a + y

    def forecast(self, task: str, context: int, action: int) -> float:
        n0 = self.data[self._index(task, context, action, 0)]
        n1 = self.data[self._index(task, context, action, 1)]
        return (n1 + 1) / (n0 + n1 + 2)

    def observe(self, task: str, c: int, a: int, y: int) -> None:
        index = self._index(task, c, a, y)
        if self.data[index] == 255:
            self.clips += 1
        else:
            self.data[index] += 1

    def snapshot(self) -> bytes:
        payload = MAGIC + bytes(self.data)
        return payload + hashlib.sha256(payload).digest()

    def restore(self, snapshot: bytes) -> None:
        if (not isinstance(snapshot, bytes) or len(snapshot) != D + 36
                or snapshot[:4] != MAGIC
                or hashlib.sha256(snapshot[:-32]).digest() != snapshot[-32:]):
            raise ValueError("TP_HDC_CHECKPOINT_REJECTED")
        self.data[:] = snapshot[4:-32]


def expected_a_brier(model) -> float:
    total = 0.0
    for c in (0, 1):
        for a in (0, 1):
            p = PROBS["A"][2 * c + a]
            q = model.forecast("A", c, a)
            total += p * (1 - q)**2 + (1 - p) * q**2
    return total / 4.0


def run(seed: int) -> dict:
    models = {"tp_hdc": Superposition(), "sham": Superposition(sham=True),
              "no_update": Superposition(learn=False),
              "exact": Counter(pooled=False), "shared": Counter(pooled=True)}
    rng = random.Random(seed)
    stats = {m: {"stage_brier": [], "a_before_b": None, "a_after_b": None,
                 "clips": 0, "checkpoint_sha256": ""} for m in models}
    for stage_index, task in enumerate(TASKS):
        losses = {m: [] for m in models}
        for context in (0, 1):
            for action in (0, 1):
                p = PROBS[task][2 * context + action]
                for _ in range(32):
                    y = int(rng.random() < p)
                    for name, model in models.items():
                        q = model.forecast(task, context, action)
                        losses[name].append((q - y)**2)
                        model.observe(task, context, action, y)
        for name, model in models.items():
            stats[name]["stage_brier"].append(sum(losses[name]) / len(losses[name]))
            if stage_index == 0:
                stats[name]["a_before_b"] = expected_a_brier(model)
            if stage_index == 1:
                stats[name]["a_after_b"] = expected_a_brier(model)
            checkpoint = model.snapshot()
            assert len(checkpoint) == 4132
            clone = (Superposition(sham=model.sham, learn=model.learn)
                     if isinstance(model, Superposition)
                     else Counter(pooled=model.pooled))
            clone.restore(checkpoint)
            assert clone.snapshot() == checkpoint
            assert clone.forecast("A", 0, 0) == model.forecast("A", 0, 0)
            corrupted = bytearray(checkpoint)
            corrupted[12] ^= 1
            try:
                clone.restore(bytes(corrupted))
                raise AssertionError("corrupt checkpoint accepted")
            except ValueError:
                pass
            stats[name]["clips"] = model.clips
            stats[name]["checkpoint_sha256"] = hashlib.sha256(checkpoint).hexdigest()
    return stats


def main() -> None:
    if hashlib.sha256(INPUT_SPEC.encode()).hexdigest() != INPUT_SHA256:
        raise ValueError("FROZEN_SOURCE_IDENTITY_MISMATCH")
    started = time.process_time()
    tracemalloc.start()
    seeds = {str(seed): run(seed) for seed in SEEDS}
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    metrics = {}
    for name in ("tp_hdc", "sham", "no_update", "exact", "shared"):
        entries = [seeds[str(s)][name] for s in SEEDS]
        metrics[name] = {
            "stage_brier_mean": [sum(x["stage_brier"][i] for x in entries)/4 for i in range(4)],
            "a_expected_brier_before_b_mean": sum(x["a_before_b"] for x in entries)/4,
            "a_expected_brier_after_b_mean": sum(x["a_after_b"] for x in entries)/4,
            "a_retention_delta_by_seed": [x["a_after_b"] - x["a_before_b"] for x in entries],
            "clips_total": sum(x["clips"] for x in entries),
            "allocated_state_bytes": D,
            "used_counter_slots": (24 if name == "exact" else 8) if name in ("exact", "shared") else None,
            "checkpoint_bytes": 4132,
        }
    h = metrics["tp_hdc"]
    rules = {
        "drift_all_seeds_le_002": all(v <= 0.02 for v in h["a_retention_delta_by_seed"]),
        "return_brier_beats_shared_by_001": h["stage_brier_mean"][2] <= metrics["shared"]["stage_brier_mean"][2] - 0.01,
        "return_brier_within_exact_002": h["stage_brier_mean"][2] <= metrics["exact"]["stage_brier_mean"][2] + 0.02,
    }
    outcome = ("SYNTHETIC_DEVELOPMENT_SUPPORTED" if all(rules.values())
               else "SYNTHETIC_DEVELOPMENT_NEGATIVE_OR_MIXED")
    report = {"schema": "yggdrasil.tp-hdc01.dev-result.v1",
              "source_identity_sha256": INPUT_SHA256, "seeds": seeds,
              "aggregate": metrics, "frozen_rules": rules, "outcome": outcome,
              "cpu_seconds": time.process_time() - started,
              "tracemalloc_peak_bytes": peak,
              "limitations": "Task identity supplied; source-free synthetic storage experiment only, not native Yggdrasil science gain. Key cache is transient and not included in learned state bytes. Runtime memory and key-generation cost must be disclosed."}
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
