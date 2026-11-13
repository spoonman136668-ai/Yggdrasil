"""SL03: bounded offline selective consolidation under shared physical actions.

Preregistered at 93f91491b6235945b16ab5928c06c64f8ca84581.
No hidden regime, simulator audit, artificial dream or phase label reaches a learner.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import math
import random
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def load(label, file):
    spec = importlib.util.spec_from_file_location(label, ROOT / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

native = load("sl03_hc09_native", "dg1-hc09-20261113/model.py")
conventional = load("sl03_hc09_conventional", "dg1-hc09-20261113/conventional_control.py")
FULL = (1 << 40) - 1
SEEDS = {"ABA": range(95001, 95009),
         "majority": range(95009, 95017),
         "cubic": range(95017, 95025)}
ARMS = ("native_no_sleep", "conventional_online", "selective_sleep",
        "conventional_selective_sleep", "sham_sleep", "online_same_compute")
SCHEMA = "ygg.dg1-sl03.selective-causal-consolidation.v1"

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")

def valid_event(event):
    if type(event) is not tuple or len(event) != 3:
        raise ValueError("SL03_EVENT_SHAPE")
    s, a, after = event
    native.valid_state(s)
    native.valid_action(a)
    native.valid_state(after)
    if after not in (s, s ^ (1 << a)):
        raise ValueError("SL03_NONLOCAL_EVENT")
    return event

class PhysicalWorld:
    def __init__(self, seed, group):
        if group not in SEEDS or seed not in SEEDS[group]:
            raise ValueError("SL03_WORLD_NOT_REGISTERED")
        self.seed = seed
        self.group = group
        self.sign, self.slope = [], []
        for action in range(4):
            r = random.Random(seed * 101 + action * 31)
            self.sign.append(r.randrange(2))
            self.slope.append(r.randrange(2))
        self.paid_actions = 0

    def _transition(self, state, action, phase):
        native.valid_state(state)
        native.valid_action(action)
        if type(phase) is not int or phase not in (0, 1):
            raise ValueError("SL03_BAD_PHASE")
        left = (state >> ((action + 1) % 4)) & 1
        right = (state >> ((action + 2) % 4)) & 1
        own = (state >> action) & 1
        if self.group == "majority":
            eff = int(left + right + own >= 2)
        elif self.group == "cubic":
            eff = int(state == 15)
        else:
            eff = left ^ right ^ (own & self.slope[action])
        eff ^= self.sign[action]
        if self.group == "ABA" and phase == 1:
            eff ^= 1
        return state ^ (eff << action)

    def step(self, state, step):
        if not 0 <= step < 48 or step != self.paid_actions:
            raise ValueError("SL03_BAD_PAID_STEP")
        self.paid_actions += 1
        if step in (6, 13, 20, 27, 34, 41):
            bit = (self.seed + step) % 4
            return ("flip", bit, state ^ (1 << bit))
        action = (self.seed + step) % 4
        phase = int(self.group == "ABA" and 16 <= step < 32)
        return ("causal", action, self._transition(state, action, phase))

    def audit_truth(self, state, action, after_step):
        if after_step not in (16, 32, 48):
            raise ValueError("SL03_AUDIT_BOUNDARY")
        phase = int(self.group == "ABA" and after_step == 32)
        return self._transition(state, action, phase)

def fitted_mask(event, family):
    s, a, after = valid_event(event)
    effect = int(after != s)
    fn = native.effect if family == "native" else conventional.eval_rule
    return sum(1 << h for h in range(40) if fn(s, h) == effect)

def bank_predict(masks, state, action, family):
    native.valid_state(state)
    native.valid_action(action)
    fn = native.counts if family == "native" else conventional.posterior_counts
    zeros, ones = fn(masks[action], state)
    if zeros and ones or not (zeros or ones):
        return None
    return state ^ (int(bool(ones)) << action)

def score_model_on_events(model, events):
    result = 0
    for s, a, after in events:
        got = model.predict(s, a)
        result += 3 if got == after else -5 if got is not None else 0
    return result

def candidate_for(events, family):
    """Deterministic evidence search; enumerate latent 1, AB, ABA histories."""
    n = len(events)
    if n < 4:
        return None
    masks = [fitted_mask(e, family) for e in events]
    prefix, suffix = [[FULL] * 4], [None] * (n + 1)
    for k, event in enumerate(events):
        prev = prefix[-1][:]
        prev[event[1]] &= masks[k]
        prefix.append(prev)
    suffix[n] = [FULL] * 4
    for i in range(n - 1, -1, -1):
        val = suffix[i + 1][:]
        val[events[i][1]] &= masks[i]
        suffix[i] = val

    def rank(bank_list, penalty):
        if any(mask == 0 for bank in bank_list for mask in bank):
            return None
        return sum(math.log2(mask.bit_count() / 40) for bank in bank_list
                   for mask in bank) - penalty

    def check(kind, cuts, banks, active, penalty):
        nonlocal best, best_rank
        val = rank(banks, penalty)
        if val is None:
            return
        if best is None or val > best_rank + 1e-10:
            best_rank = val
            best = {"shape": kind, "cuts": cuts, "banks": banks,
                    "active": active}

    best, best_rank = None, float("-inf")
    check("one", [], [prefix[n]], 0, 0)
    for i in range(4, n - 3):
        check("AB", [i], [prefix[i], suffix[i]], 1, 5)
    for i in range(4, n - 7):
        middle = [FULL] * 4
        for j in range(i + 1, n - 3):
            previous = events[j-1]
            middle[previous[1]] &= masks[j-1]
            if j - i < 4:
                continue
            first_last = [prefix[i][a] & suffix[j][a] for a in range(4)]
            check("ABA", [i, j], [first_last, middle[:]], 0, 10)
    return best

def score_partition(candidate, events, family):
    cuts = candidate["cuts"]
    shape = candidate["shape"]
    outcome = 0
    for index, (s, a, after) in enumerate(events):
        bank = (0 if shape == "one" else
                (0 if index < cuts[0] else 1) if shape == "AB" else
                (0 if index < cuts[0] or index >= cuts[1] else 1))
        got = bank_predict(candidate["banks"][bank], s, a, family)
        outcome += 3 if got == after else -5 if got is not None else 0
    return outcome

class Learner:
    def __init__(self, arm):
        if arm not in ARMS:
            raise ValueError("SL03_BAD_ARM")
        self.arm = arm
        self.family = "conventional" if arm in ("conventional_online",
                          "conventional_selective_sleep") else "native"
        self.model = (native.DualRegimeCausalCells() if self.family == "native"
                      else conventional.ConventionalContextModel())
        self.events = []
        self.candidate = None
        self.offline_accepts = 0
        self.offline_attempts = 0
        self.dream_checks = 0

    def predict(self, state, action):
        native.valid_state(state)
        native.valid_action(action)
        if self.candidate is not None:
            got = bank_predict(self.candidate["banks"][self.candidate["active"]],
                               state, action, self.family)
            if got is not None:
                return got
        return self.model.predict(state, action)

    def observe(self, before, action, after):
        event = valid_event((before, action, after))
        if self.candidate is not None:
            expected = bank_predict(self.candidate["banks"][self.candidate["active"]],
                                    before, action, self.family)
            if expected is not None and expected != after:
                self.candidate = None
        self.model.observe(*event)
        self.events.append(list(event))
        self.events = self.events[-48:]

    def rest(self):
        self.offline_attempts += 1
        if self.arm in ("native_no_sleep", "conventional_online"):
            return
        events = [tuple(x) for x in self.events]
        if self.arm == "sham_sleep":
            _ = candidate_for(events, self.family)
            return
        candidate = candidate_for(events, self.family)
        if candidate is None:
            return
        if score_partition(candidate, events, self.family) <= \
           score_model_on_events(self.model, events):
            return
        self.candidate = candidate
        self.offline_accepts += 1
        # Imagined predictions are inspected but are never fitted as new evidence.
        prior = len(self.events)
        for s in range(16):
            for a in range(4):
                _ = bank_predict(candidate["banks"][candidate["active"]],
                                 s, a, self.family)
                self.dream_checks += 1
        assert len(self.events) == prior

    def snapshot(self):
        payload = {"schema": SCHEMA, "arm": self.arm,
                   "model": self.model.snapshot().decode("ascii"),
                   "events": self.events, "candidate": self.candidate,
                   "offline_accepts": self.offline_accepts,
                   "offline_attempts": self.offline_attempts,
                   "dream_checks": self.dream_checks}
        raw = canonical({"payload": payload,
                         "sha256": hashlib.sha256(canonical(payload)).hexdigest()})
        if len(raw) > 8192:
            raise ValueError("SL03_SNAPSHOT_TOO_LONG")
        return raw

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= 8192:
                raise ValueError("SL03_BAD_SNAPSHOT")
            wrapper = json.loads(raw)
            if type(wrapper) is not dict or set(wrapper) != {"payload", "sha256"}:
                raise ValueError("SL03_BAD_WRAPPER")
            p = wrapper["payload"]
            required = {"schema","arm","model","events","candidate",
                        "offline_accepts","offline_attempts","dream_checks"}
            if type(p) is not dict or set(p) != required or p["schema"] != SCHEMA:
                raise ValueError("SL03_BAD_SCHEMA")
            if hashlib.sha256(canonical(p)).hexdigest() != wrapper["sha256"]:
                raise ValueError("SL03_HASH")
            out = cls(p["arm"])
            if type(p["model"]) is not str:
                raise ValueError("SL03_MODEL_TYPE")
            cls_model = (native.DualRegimeCausalCells if out.family == "native"
                         else conventional.ConventionalContextModel)
            out.model = cls_model.restore(p["model"].encode("ascii"))
            if type(p["events"]) is not list or len(p["events"]) > 48:
                raise ValueError("SL03_EVENTS")
            for e in p["events"]:
                if type(e) is not list or len(e) != 3:
                    raise ValueError("SL03_EVENTS")
                valid_event(tuple(e))
            out.events = p["events"]
            c = p["candidate"]
            if c is not None:
                if (type(c) is not dict or set(c) != {"shape","cuts","banks","active"}
                    or c["shape"] not in ("one","AB","ABA")
                    or type(c["cuts"]) is not list
                    or len(c["cuts"]) != {"one":0,"AB":1,"ABA":2}[c["shape"]]
                    or type(c["banks"]) is not list
                    or len(c["banks"]) != (1 if c["shape"] == "one" else 2)
                    or any(type(bank) is not list or len(bank) != 4 or
                           any(type(m) is not int or not 0 < m <= FULL for m in bank)
                           for bank in c["banks"])
                    or type(c["active"]) is not int or
                    c["active"] not in range(len(c["banks"]))
                    or any(type(k) is not int or not 0 <= k <= len(out.events)
                           for k in c["cuts"])
                    or c["cuts"] != sorted(c["cuts"])):
                    raise ValueError("SL03_CANDIDATE")
            out.candidate = c
            for key in ("offline_accepts","offline_attempts","dream_checks"):
                if type(p[key]) is not int or not 0 <= p[key] <= 100000:
                    raise ValueError("SL03_COUNTER")
                setattr(out, key, p[key])
            if out.offline_accepts > out.offline_attempts:
                raise ValueError("SL03_COUNTER_RELATION")
            if out.snapshot() != raw:
                raise ValueError("SL03_NONCANONICAL")
            return out
        except (ValueError, TypeError, UnicodeError, KeyError, OverflowError):
            raise ValueError("SL03_BAD_SNAPSHOT") from None

def audit(learner, world, seen, after_step):
    out = {name: 0 for name in ("correct","wrong_confident","abstained",
                                   "unseen_correct","unseen_wrong_confident",
                                   "unseen_abstained")}
    for s in range(16):
        for a in range(4):
            expected = world.audit_truth(s, a, after_step)
            got = learner.predict(s, a)
            verdict = "abstained" if got is None else "correct" if got == expected else "wrong_confident"
            out[verdict] += 1
            if (s, a) not in seen:
                out["unseen_" + verdict] += 1
    return out

def one_world(seed, group):
    world = PhysicalWorld(seed, group)
    learners = {arm: Learner(arm) for arm in ARMS}
    state = seed % 16
    seen = set()
    receipts = []
    checkpoints = {arm: {} for arm in ARMS}
    prequential = {arm: {"correct":0,"wrong_confident":0,"abstained":0} for arm in ARMS}
    t0 = time.perf_counter_ns()
    for step in range(48):
        before = state
        kind, action, after = world.step(state, step)
        if kind == "causal":
            for arm, learner in learners.items():
                got = learner.predict(before, action)
                verdict = "abstained" if got is None else "correct" if got == after else "wrong_confident"
                prequential[arm][verdict] += 1
                learner.observe(before, action, after)
            seen.add((before, action))
        state = after
        receipts.append([before, kind, action, after])
        if (step+1) % 8 == 0:
            for learner in learners.values():
                learner.rest()
        if step+1 in (16,32,48):
            for arm, learner in learners.items():
                checkpoints[arm][str(step+1)] = audit(learner, world, seen, step+1)
    elapsed_ns = time.perf_counter_ns() - t0
    assert world.paid_actions == 48 and sum(row[1] == "flip" for row in receipts) == 6
    cold_bytes = {}
    for arm, learner in learners.items():
        raw = learner.snapshot()
        restored = Learner.restore(raw)
        assert raw == restored.snapshot()
        assert all(learner.predict(s,a) == restored.predict(s,a)
                   for s in range(16) for a in range(4))
        cold_bytes[arm] = len(raw)
    return {"seed":seed, "group":group,"charged_actions":world.paid_actions,
            "charged_flips":6,"mechanism_observations":42,
            "trace_sha256":hashlib.sha256(canonical(receipts)).hexdigest(),
            "audits":checkpoints,"prequential":prequential,
            "offline_accepts":{a:v.offline_accepts for a,v in learners.items()},
            "cold_snapshot_bytes":cold_bytes, "cold_restore_identical":True,
            "whole_process_ns":elapsed_ns}

def run():
    worlds = [one_world(seed,group) for group,seq in SEEDS.items() for seed in seq]
    keys = ("correct","wrong_confident","abstained","unseen_correct",
            "unseen_wrong_confident","unseen_abstained")
    aggregate = {group:{arm:{k:sum(w["audits"][arm]["48"][k] for w in worlds
                                       if w["group"] == group) for k in keys}
                        for arm in ARMS} for group in SEEDS}
    base = "native_no_sleep"
    conventional_arm = "conventional_online"
    candidate = "selective_sleep"
    reference = {g:{k:max(aggregate[g][base][k], aggregate[g][conventional_arm][k])
              if k.endswith("correct") and not k.startswith("wrong") else
              min(aggregate[g][base][k], aggregate[g][conventional_arm][k])
              for k in ("correct","wrong_confident","unseen_correct")}
                 for g in SEEDS}
    a = aggregate["ABA"][candidate]
    stable = aggregate["majority"][candidate]
    cubic = aggregate["cubic"][candidate]
    primary = (a["correct"] - reference["ABA"]["correct"] >= 24 and
               a["unseen_correct"] - reference["ABA"]["unseen_correct"] >= 16 and
               a["wrong_confident"] <= reference["ABA"]["wrong_confident"] + 8 and
               stable["correct"] >= reference["majority"]["correct"] - 16 and
               stable["wrong_confident"] <= reference["majority"]["wrong_confident"] + 4 and
               cubic["wrong_confident"] <= reference["cubic"]["wrong_confident"] + 8)
    sleep_ties_conventional = all(
        aggregate[g][candidate] == aggregate[g]["conventional_selective_sleep"]
        for g in SEEDS)
    timing_tie = all(
        aggregate[g][candidate] == aggregate[g]["online_same_compute"]
        for g in SEEDS)
    any_gain = (a["correct"] > reference["ABA"]["correct"] or
                a["unseen_correct"] > reference["ABA"]["unseen_correct"])
    result = {
        "schema":"ygg.dg1-sl03.prospective-frozen-dev.v1",
        "freeze_sha":"93f91491b6235945b16ab5928c06c64f8ca84581",
        "primary_pass":primary,
        "classification":"DEV_SIGNAL_NOT_SCIENCE" if primary else
                         "MIXED_DEV" if any_gain else "NEGATIVE_DEV",
        "scientific_acceptance":"UNVERIFIED",
        "conventional_sleep_tie":sleep_ties_conventional,
        "online_same_compute_tie":timing_tie,
        "same_physical_actions":True,
        "same_total_compute":False,
        "charged_actions_total":sum(w["charged_actions"] for w in worlds),
        "aggregate_final":aggregate,
        "worlds":worlds,
    }
    return result

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, separators=(",", ":")))
