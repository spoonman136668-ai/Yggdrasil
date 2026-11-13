"""DG1-SL08: physical-error calibration under exact matched paid trajectories.

Frozen preregistration first: 66a64101af5c926f43a91e991409034b3b18be35.
Source-only synthetic DEV. No hidden phase, rules, seed or audit labels reach
any learner, action schedule or calibrator. No model weights or native edits.
"""
from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import random
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREEZE = "66a64101af5c926f43a91e991409034b3b18be35"
PARENT = "c67aca9eb03353bab5b581cbdfed63a7dc18b147"
SCHEMA = "ygg.dg1-sl08.physical-error-calibration.v1"
COHORTS = {
    "ABCA": tuple(range(101001, 101009)),
    "ABCB": tuple(range(101009, 101017)),
    "STABLE": tuple(range(101017, 101025)),
    "ABCD_OOD": tuple(range(101025, 101033)),
}
ARMS = ("native_raw", "native_action2", "native_action1", "native_global2",
        "conventional_raw", "conventional_action2")
FLIPS = (6, 14, 22, 30, 38, 46, 54, 62, 70, 78)
AUDITS = (60, 64, 72, 80)


def load_frozen():
    spec = importlib.util.spec_from_file_location(
        "sl08_frozen_sl07", ROOT / "dg1-sl07-20261113/sl07.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sl07 = load_frozen()
native = sl07.native


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


class World(sl07.World):
    """Only prospective seed registration changes frozen SL07/SL06 physics."""
    def __init__(self, seed, group):
        if group not in COHORTS or seed not in COHORTS[group]:
            raise ValueError("SL08_UNREGISTERED_WORLD")
        self.seed = seed
        self.group = "STATIONARY" if group == "STABLE" else group
        self.paid = 0
        self.rules = [[0] * 4 for _ in range(3)]
        for action in range(4):
            used = set()
            for phase in range(3):
                rng = random.Random(seed * 131 + phase * 719 + action * 47)
                h = rng.randrange(40)
                while h in used:
                    h = (h + 1) % 40
                used.add(h)
                self.rules[phase][action] = h


class Calibrated:
    """Opaque physical-event consumer with four bounded action-specific gates."""
    def __init__(self, arm):
        if arm not in ARMS:
            raise ValueError("SL08_UNKNOWN_ARM")
        self.arm = arm
        self.inner_arm = ("conventional_witness" if arm.startswith("conventional_")
                          else "native_passive")
        self.model = sl07.learner_for(self.inner_arm)
        self.trusted = [True] * 4
        self.recovery = [0] * 4
        self.causal_events = 0
        self.errors_observed = 0
        self.quarantines = 0

    def raw_predict(self, state, action):
        return self.model.predict(state, action)

    def predict(self, state, action):
        native.valid_state(state)
        native.valid_action(action)
        if self.arm.endswith("_raw"):
            return self.raw_predict(state, action)
        return self.raw_predict(state, action) if self.trusted[action] else None

    def observe(self, before, action, after):
        sl07.sl05.verified(before, action, after)
        if self.causal_events >= 70:
            raise ValueError("SL08_OBSERVATION_BUDGET")
        predicted = self.raw_predict(before, action)
        wrong = predicted is not None and predicted != after
        right = predicted is not None and predicted == after
        if wrong:
            self.errors_observed += 1
        if self.arm not in ("native_raw", "conventional_raw"):
            affected = range(4) if self.arm == "native_global2" and wrong else (action,)
            if wrong:
                for a in affected:
                    self.trusted[a] = False
                    self.recovery[a] = 0
                self.quarantines += 1
            elif right and not self.trusted[action]:
                target = 1 if self.arm == "native_action1" else 2
                self.recovery[action] = min(target, self.recovery[action] + 1)
                if self.recovery[action] >= target:
                    self.trusted[action] = True
                    self.recovery[action] = 0
        self.model.observe(before, action, after)
        self.causal_events += 1

    def rest(self):
        self.model.rest()

    def snapshot(self):
        payload = {
            "schema": SCHEMA, "arm": self.arm,
            "model_b64": base64.b64encode(self.model.snapshot()).decode("ascii"),
            "trusted": self.trusted, "recovery": self.recovery,
            "causal_events": self.causal_events,
            "errors_observed": self.errors_observed,
            "quarantines": self.quarantines,
        }
        raw = canonical({"payload": payload,
                         "sha256": hashlib.sha256(canonical(payload)).hexdigest()})
        if len(raw) > 8192:
            raise ValueError("SL08_SNAPSHOT_CAPACITY")
        return raw

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= 8192:
                raise ValueError("SL08_BAD_BYTES")
            wrap = json.loads(raw)
            if type(wrap) is not dict or set(wrap) != {"payload", "sha256"}:
                raise ValueError("SL08_BAD_WRAPPER")
            p = wrap["payload"]
            if type(p) is not dict or set(p) != {
                "schema", "arm", "model_b64", "trusted", "recovery",
                "causal_events", "errors_observed", "quarantines"
            } or p["schema"] != SCHEMA or p["arm"] not in ARMS:
                raise ValueError("SL08_BAD_SCHEMA")
            if hashlib.sha256(canonical(p)).hexdigest() != wrap["sha256"]:
                raise ValueError("SL08_BAD_HASH")
            if (type(p["trusted"]) is not list or len(p["trusted"]) != 4 or
                any(type(v) is not bool for v in p["trusted"]) or
                type(p["recovery"]) is not list or len(p["recovery"]) != 4 or
                any(type(v) is not int or not 0 <= v <= 2
                    for v in p["recovery"])):
                raise ValueError("SL08_BAD_GATE")
            if any(t and n != 0 for t, n in zip(p["trusted"], p["recovery"])):
                raise ValueError("SL08_INCONSISTENT_GATE")
            for key in ("causal_events", "errors_observed", "quarantines"):
                if type(p[key]) is not int or not 0 <= p[key] <= 70:
                    raise ValueError("SL08_BAD_COUNTER")
            if p["errors_observed"] > p["causal_events"] or (
                    p["quarantines"] > p["errors_observed"]):
                raise ValueError("SL08_BAD_RELATION")
            obj = cls(p["arm"])
            inner = base64.b64decode(p["model_b64"], validate=True)
            obj.model = sl07.restore_learner(obj.inner_arm, inner)
            obj.trusted = p["trusted"]
            obj.recovery = p["recovery"]
            for key in ("causal_events", "errors_observed", "quarantines"):
                setattr(obj, key, p[key])
            if obj.snapshot() != raw:
                raise ValueError("SL08_NONCANONICAL")
            return obj
        except (ValueError, TypeError, KeyError, OverflowError,
                UnicodeError, base64.binascii.Error) as exc:
            raise ValueError("SL08_INVALID_CHECKPOINT") from exc


def audit(agent, world, seen, completed):
    tally = {key: 0 for key in ("correct", "wrong_confident", "abstained",
                                "unseen_correct", "unseen_wrong_confident",
                                "unseen_abstained")}
    for state in range(16):
        for action in range(4):
            truth = world.audit_truth(state, action, completed)
            prediction = agent.predict(state, action)
            key = ("abstained" if prediction is None else
                   "correct" if prediction == truth else "wrong_confident")
            tally[key] += 1
            if (state, action) not in seen:
                tally["unseen_" + key] += 1
    return tally


def one_world(seed, group):
    result = {}
    receipts = []
    for arm in ARMS:
        world, agent = World(seed, group), Calibrated(arm)
        state, seen, ledger = seed % 16, set(), []
        prequential = {"correct": 0, "wrong_confident": 0, "abstained": 0}
        stages, cold_bytes = {}, 0
        elapsed_ns = 0
        for step in range(80):
            if step == 60:
                snap = agent.snapshot()
                restored = Calibrated.restore(snap)
                if snap != restored.snapshot() or any(
                    agent.predict(s, a) != restored.predict(s, a)
                    for s in range(16) for a in range(4)
                ):
                    raise AssertionError("SL08_COLD_RESTORE_FAILURE")
                agent = restored
                cold_bytes = len(snap)
            start = time.perf_counter_ns()
            chosen = (step % 4 if step >= 60 and step not in FLIPS else None)
            kind, action, nxt = world.step(state, step, chosen)
            if kind == "causal":
                before = agent.predict(state, action)
                verdict = ("abstained" if before is None else
                           "correct" if before == nxt else "wrong_confident")
                prequential[verdict] += 1
                agent.observe(state, action, nxt)
                seen.add((state, action))
            elapsed_ns += time.perf_counter_ns() - start
            ledger.append([state, kind, action, nxt])
            state = nxt
            if (step + 1) % 8 == 0:
                start = time.perf_counter_ns()
                agent.rest()
                elapsed_ns += time.perf_counter_ns() - start
            if step + 1 in AUDITS:
                stages[str(step + 1)] = audit(agent, world, seen, step + 1)
        if world.paid != 80 or agent.causal_events != 70:
            raise AssertionError("SL08_PAID_BUDGET_FAILURE")
        full = hashlib.sha256(canonical(ledger)).hexdigest()
        receipts.append(full)
        final_snap = agent.snapshot()
        if Calibrated.restore(final_snap).snapshot() != final_snap:
            raise AssertionError("SL08_FINAL_RESTORE_FAILURE")
        result[arm] = {
            "paid_steps": world.paid, "causal_observations": agent.causal_events,
            "flips": sum(e[1] == "flip" for e in ledger),
            "trace_sha256": full,
            "prequential": prequential, "stage_audits": stages,
            "cold_checkpoint_bytes": cold_bytes,
            "final_checkpoint_bytes": len(final_snap),
            "final_snapshot_sha256": hashlib.sha256(final_snap).hexdigest(),
            "errors_observed": agent.errors_observed,
            "quarantines": agent.quarantines, "cpu_ns": elapsed_ns
        }
    if len(set(receipts)) != 1:
        raise AssertionError("SL08_UNMATCHED_ACTION_DIFFICULTY")
    return {"seed": seed, "cohort": group, "identical_paid_trace_sha256": receipts[0],
            "arms": result}


def run():
    worlds = [one_world(seed, cohort) for cohort, seeds in COHORTS.items()
              for seed in seeds]
    keys = ("correct", "wrong_confident", "abstained", "unseen_correct",
            "unseen_wrong_confident", "unseen_abstained")
    aggregates = {
        cohort: {arm: {key: sum(
            w["arms"][arm]["stage_audits"]["80"][key]
            for w in worlds if w["cohort"] == cohort
        ) for key in keys} for arm in ARMS} for cohort in COHORTS
    }
    cand = "native_action2"
    ood = aggregates["ABCD_OOD"]
    return_a = aggregates["ABCA"]
    return_b = aggregates["ABCB"]
    stable = aggregates["STABLE"]
    primary = (
        ood["native_raw"]["wrong_confident"] - ood[cand]["wrong_confident"] >= 16
        and ood["conventional_action2"]["wrong_confident"]
        - ood[cand]["wrong_confident"] >= 8
        and ood[cand]["correct"] >= ood["conventional_action2"]["correct"] - 8
        and return_a[cand]["correct"] >= max(
            return_a["native_raw"]["correct"],
            return_a["conventional_action2"]["correct"]) - 16
        and return_b[cand]["correct"] >= max(
            return_b["native_raw"]["correct"],
            return_b["conventional_action2"]["correct"]) - 16
        and stable[cand]["correct"] >= max(
            stable["native_raw"]["correct"],
            stable["conventional_action2"]["correct"]) - 16
        and stable[cand]["wrong_confident"] == 0
    )
    mixed = (
        ood["native_raw"]["wrong_confident"] - ood[cand]["wrong_confident"] >= 16
        and return_a[cand]["correct"] >= return_a["native_raw"]["correct"] - 32
        and return_b[cand]["correct"] >= return_b["native_raw"]["correct"] - 32
    )
    return {
        "schema": SCHEMA, "freeze_sha": FREEZE, "source_parent": PARENT,
        "classification": ("DEV_SIGNAL_NOT_SCIENCE" if primary else
                           "MIXED_DEV" if mixed else "NEGATIVE_DEV"),
        "primary_pass": primary, "scientific_acceptance": "UNVERIFIED",
        "arms": list(ARMS), "world_count": len(worlds),
        "charged_steps": sum(v["paid_steps"] for w in worlds
                             for v in w["arms"].values()),
        "causal_observations": sum(v["causal_observations"] for w in worlds
                                   for v in w["arms"].values()),
        "exact_matched_action_difficulty": True, "compute_matched": False,
        "aggregates": aggregates, "worlds": worlds,
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, separators=(",", ":")))
