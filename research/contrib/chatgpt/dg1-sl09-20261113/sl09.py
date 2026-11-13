"""DG1-SL09 frozen prospective compositional causal-rule discovery DEV.

Preregistered at commit 9f760727f58058a538f4af82a0d4494b98be11c9
before implementation or outcomes. All learning uses charged physical
(state, action, next-state) observations, never hidden programs or audits.
"""
from __future__ import annotations

import base64
import hashlib
import importlib.util
import itertools
import json
import random
import statistics
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = "f5770c5a3090d90a2c25c6200f51c817ac247160"
FREEZE = "9f760727f58058a538f4af82a0d4494b98be11c9"
SCHEMA = "ygg.dg1-sl09.compositional-rule-discovery.v1"
COHORTS = {
    "RETURN_A": tuple(range(102001, 102009)),
    "RETURN_B": tuple(range(102009, 102017)),
    "STABLE": tuple(range(102017, 102025)),
    "COMPOSITION_OOD": tuple(range(102025, 102033)),
}
ARMS = (
    "candidate_compositional_episodic",
    "candidate_no_composition",
    "candidate_no_episodic",
    "independent_exact_bayes_grammar",
    "independent_tabular_episodic",
    "frozen_native_cold_three_bank",
)
FLIPS = (6, 14, 22, 30, 38, 46, 54, 62, 70, 78)
AUDITS = (60, 64, 72, 80)
PROGRAMS = tuple(itertools.product(range(6), repeat=3))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def check_state(x):
    if type(x) is not int or not 0 <= x < 16:
        raise ValueError("SL09_INVALID_STATE")


def check_action(x):
    if type(x) is not int or not 0 <= x < 4:
        raise ValueError("SL09_INVALID_ACTION")


def gate(op, x, y):
    if op == 0:
        return x & y
    if op == 1:
        return x | y
    if op == 2:
        return x ^ y
    if op == 3:
        return 1 ^ (x & y)
    if op == 4:
        return 1 ^ (x | y)
    if op == 5:
        return 1 ^ (x ^ y)
    raise ValueError("SL09_UNKNOWN_GATE")


def flip(program, state, action):
    check_state(state)
    check_action(action)
    a, b, c = program
    bits = [(state >> j) & 1 for j in range(4)]
    left = gate(a, bits[action], bits[(action + 1) % 4])
    right = gate(b, bits[(action + 2) % 4], bits[(action + 3) % 4])
    return gate(c, left, right)


# Same public, complete hypothesis grammar for native program and exact Bayes.
MASKS = {
    a: tuple(sum(flip(p, s, a) << s for s in range(16))
             for p in PROGRAMS)
    for a in range(4)
}


class World:
    """Private deterministic physics; no rule/phase/seed fields are passed out."""
    def __init__(self, seed, cohort):
        if cohort not in COHORTS or seed not in COHORTS[cohort]:
            raise ValueError("SL09_UNREGISTERED_WORLD")
        self._seed = seed
        self._cohort = cohort
        self.paid = 0
        self._programs = {}
        for phase, alphabet in (
            ("A", (0, 1, 2)), ("B", (3, 4, 5))
        ):
            for action in range(4):
                rng = random.Random(seed * 131 + action * 47 +
                                    (17 if phase == "A" else 941))
                self._programs[(phase, action)] = tuple(
                    alphabet[rng.randrange(3)] for _ in range(3))
        for action in range(4):
            rng = random.Random(seed * 131 + action * 47 + 1789)
            self._programs[("OOD", action)] = (
                (0, 1, 2)[rng.randrange(3)],
                (3, 4, 5)[rng.randrange(3)],
                rng.randrange(6),
            )

    def _phase(self, step):
        if self._cohort == "STABLE":
            return "A"
        if step < 30:
            return "A"
        if step < 60:
            return "B"
        if self._cohort == "RETURN_A":
            return "A"
        if self._cohort == "RETURN_B":
            return "B"
        return "OOD"

    def step(self, state, step):
        check_state(state)
        if type(step) is not int or step != self.paid or step >= 80:
            raise ValueError("SL09_UNPAID_OR_REPLAYED_STEP")
        if step in FLIPS:
            kind = "flip"
            action = (step // 8) % 4
            nxt = state ^ (1 << action)
        else:
            kind = "causal"
            action = step % 4
            change = flip(self._programs[(self._phase(step), action)],
                          state, action)
            nxt = state ^ (change << action)
        self.paid += 1
        return kind, action, nxt

    def audit_truth(self, state, action, completed):
        if type(completed) is not int or completed not in AUDITS:
            raise ValueError("SL09_FORBIDDEN_AUDIT")
        check_state(state)
        check_action(action)
        return state ^ (
            flip(self._programs[(self._phase(completed - 1), action)],
                 state, action) << action
        )


def native_type():
    root = HERE.parent / "dg1-sl08-20261113" / "sl08.py"
    spec = importlib.util.spec_from_file_location("sl09_parent_sl08", root)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.sl07.sl05.ColdThreeBank


Native = native_type()


class Agent:
    """Causal-only observation buffer and bounded, oracle-free regime routing."""
    def __init__(self, arm):
        if arm not in ARMS:
            raise ValueError("SL09_UNKNOWN_ARM")
        self.arm = arm
        self.native = (Native(gate=True, evict=False)
                       if arm == "frozen_native_cold_three_bank" else None)
        self.banks = [[]]
        self.active = 0
        self.recent = []
        self.causal_events = 0
        self.switches = 0

    def _program_predict(self, entries, state, action, exact_bayes):
        events = [(s, bit) for s, a, bit in entries if a == action]
        masks = MASKS[action]
        errors = [sum(((mask >> s) & 1) != bit for s, bit in events)
                  for mask in masks]
        if exact_bayes:
            # Exact finite Bayesian posterior under independent noisy
            # Bernoulli physical observations, with 1:16 noise odds.
            hi = max(errors) if errors else 0
            yes = no = 0
            for mask, err in zip(masks, errors):
                weight = 16 ** (hi - err)
                if (mask >> state) & 1:
                    yes += weight
                else:
                    no += weight
            return int(yes > no)
        # Explicit single-program minimum-counterexample induction. Favor
        # shorter primitive diversity only after equal paid-error counts.
        best = min(range(len(PROGRAMS)),
                   key=lambda i: (errors[i], len(set(PROGRAMS[i])),
                                  sum(PROGRAMS[i]), i))
        return (masks[best] >> state) & 1

    def _table_predict(self, entries, state, action, bayes):
        local = [b for s, a, b in entries if s == state and a == action]
        if not local:
            local = [b for s, a, b in entries if a == action]
        if bayes:
            return int((sum(local) + 1) * 2 > len(local) + 2)
        return int(sum(local) * 2 > len(local)) if local else 0

    def _predict_in_bank(self, index, state, action):
        entries = self.banks[index]
        if self.arm in ("candidate_compositional_episodic",
                        "candidate_no_episodic",
                        "independent_exact_bayes_grammar"):
            return self._program_predict(
                entries, state, action,
                self.arm == "independent_exact_bayes_grammar")
        return self._table_predict(
            entries, state, action,
            self.arm == "independent_tabular_episodic")

    def predict(self, state, action):
        check_state(state)
        check_action(action)
        if self.native is not None:
            return self.native.predict(state, action)
        return state ^ (
            self._predict_in_bank(self.active, state, action) << action)

    def observe(self, before, action, after):
        check_state(before)
        check_action(action)
        check_state(after)
        if after not in (before, before ^ (1 << action)):
            raise ValueError("SL09_NONLOCAL_PHYSICAL_EVENT")
        if self.causal_events >= 70:
            raise ValueError("SL09_OBSERVATION_LIMIT")
        predicted = self.predict(before, action)
        wrong = int(predicted is not None and predicted != after)
        if self.native is not None:
            self.native.observe(before, action, after)
        else:
            event = [before, action, int(before != after)]
            self.recent.append([*event, wrong])
            self.recent = self.recent[-8:]
            episodic = self.arm != "candidate_no_episodic"
            active_evidence = len(self.banks[self.active]) >= 12
            contradictions = {(s, a) for s, a, _, mismatch
                              in self.recent if mismatch}
            if episodic and active_evidence and len(contradictions) >= 2:
                # No secret clock/phase input. Select archived context using
                # actual recent physical evidence, or learn a new context.
                latest = self.recent[-4:]
                candidates = [
                    (sum(self._predict_in_bank(i, s, a) == b
                         for s, a, b, _ in latest), i)
                    for i in range(len(self.banks)) if i != self.active
                ]
                best = max(candidates, default=(-1, -1))
                if best[0] >= 3:
                    self.active = best[1]
                elif len(self.banks) < 3:
                    self.banks.append([])
                    self.active = len(self.banks) - 1
                elif candidates:
                    self.active = best[1]
                self.switches += 1
                self.recent = []
            self.banks[self.active].append(event)
        self.causal_events += 1

    def rest(self):
        if self.native is not None:
            self.native.rest()

    def snapshot(self):
        p = {
            "schema": SCHEMA, "arm": self.arm,
            "banks": self.banks, "active": self.active,
            "recent": self.recent,
            "causal_events": self.causal_events,
            "switches": self.switches,
            "native_b64": (
                base64.b64encode(self.native.snapshot()).decode("ascii")
                if self.native is not None else None),
        }
        raw = canonical({"payload": p, "sha256": digest(p)})
        if len(raw) > 8192:
            raise ValueError("SL09_CHECKPOINT_CAPACITY")
        return raw

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= 8192:
                raise ValueError("SL09_BAD_BYTES")
            wrap = json.loads(raw)
            if type(wrap) is not dict or set(wrap) != {"payload", "sha256"}:
                raise ValueError("SL09_BAD_WRAPPER")
            p = wrap["payload"]
            required = {"schema", "arm", "banks", "active", "recent",
                        "causal_events", "switches", "native_b64"}
            if type(p) is not dict or set(p) != required or (
                    p["schema"] != SCHEMA or p["arm"] not in ARMS or
                    digest(p) != wrap["sha256"]):
                raise ValueError("SL09_BAD_SCHEMA_OR_HASH")
            if (type(p["banks"]) is not list or
                not 1 <= len(p["banks"]) <= 3 or
                type(p["active"]) is not int or
                not 0 <= p["active"] < len(p["banks"]) or
                type(p["recent"]) is not list or len(p["recent"]) > 8):
                raise ValueError("SL09_BAD_BANKS")
            for bank in p["banks"]:
                if type(bank) is not list or len(bank) > 70:
                    raise ValueError("SL09_BAD_BANK_CAPACITY")
                for e in bank:
                    if type(e) is not list or len(e) != 3:
                        raise ValueError("SL09_BAD_EVENT")
                    check_state(e[0])
                    check_action(e[1])
                    if type(e[2]) is not int or e[2] not in (0, 1):
                        raise ValueError("SL09_BAD_BIT")
            for e in p["recent"]:
                if type(e) is not list or len(e) != 4:
                    raise ValueError("SL09_BAD_RECENT")
                check_state(e[0])
                check_action(e[1])
                if any(type(x) is not int or x not in (0, 1)
                       for x in e[2:]):
                    raise ValueError("SL09_BAD_RECENT_BIT")
            if any(type(p[k]) is not int or not 0 <= p[k] <= 70
                   for k in ("causal_events", "switches")) or (
                    p["switches"] > p["causal_events"]):
                raise ValueError("SL09_BAD_COUNTER")
            if p["arm"] == "frozen_native_cold_three_bank":
                if len(p["banks"]) != 1 or p["active"] != 0 or (
                        p["recent"]) or any(p["banks"]):
                    raise ValueError("SL09_NATIVE_ROUTER_POLLUTION")
                if type(p["native_b64"]) is not str:
                    raise ValueError("SL09_MISSING_NATIVE")
            else:
                if p["native_b64"] is not None:
                    raise ValueError("SL09_NATIVE_LEAK")
                if sum(map(len, p["banks"])) != p["causal_events"]:
                    raise ValueError("SL09_MISSING_CAUSAL_EVENTS")
                if (p["arm"] == "candidate_no_episodic" and
                        len(p["banks"]) != 1):
                    raise ValueError("SL09_FORBIDDEN_ARCHIVE")
            obj = cls(p["arm"])
            obj.banks = p["banks"]
            obj.active = p["active"]
            obj.recent = p["recent"]
            obj.causal_events = p["causal_events"]
            obj.switches = p["switches"]
            if obj.native is not None:
                obj.native = Native.restore(
                    base64.b64decode(p["native_b64"], validate=True))
                if obj.native.evict or not obj.native.gate:
                    raise ValueError("SL09_NATIVE_MODE")
            if obj.snapshot() != raw:
                raise ValueError("SL09_NONCANONICAL")
            return obj
        except (ValueError, TypeError, KeyError, UnicodeError,
                OverflowError, base64.binascii.Error) as exc:
            raise ValueError("SL09_INVALID_CHECKPOINT") from exc


def audit(agent, world, seen, completed):
    tally = {k: 0 for k in ("correct", "wrong_confident", "abstained",
                             "unseen_correct", "unseen_wrong_confident",
                             "unseen_abstained")}
    for s in range(16):
        for a in range(4):
            actual = world.audit_truth(s, a, completed)
            got = agent.predict(s, a)
            key = ("abstained" if got is None else
                   "correct" if got == actual else "wrong_confident")
            tally[key] += 1
            if (s, a) not in seen:
                tally["unseen_" + key] += 1
    return tally


def one_world(seed, cohort):
    world_results = {}
    all_traces = []
    for arm in ARMS:
        world, model = World(seed, cohort), Agent(arm)
        state = seed % 16
        paid_ledger, seen = [], set()
        stage = {}
        prequential = {"correct": 0, "wrong_confident": 0, "abstained": 0}
        cold_bytes = 0
        elapsed_ns = 0
        for step in range(80):
            if step == 60:
                frozen = model.snapshot()
                restored = Agent.restore(frozen)
                if restored.snapshot() != frozen or any(
                    model.predict(s, a) != restored.predict(s, a)
                    for s in range(16) for a in range(4)
                ):
                    raise AssertionError("SL09_COLD_RESTORE_MISMATCH")
                model = restored
                cold_bytes = len(frozen)
            start_ns = time.perf_counter_ns()
            kind, action, nxt = world.step(state, step)
            if kind == "causal":
                prediction = model.predict(state, action)
                verdict = ("abstained" if prediction is None else
                           "correct" if prediction == nxt else
                           "wrong_confident")
                prequential[verdict] += 1
                model.observe(state, action, nxt)
                seen.add((state, action))
            elapsed_ns += time.perf_counter_ns() - start_ns
            paid_ledger.append([state, kind, action, nxt])
            state = nxt
            if (step + 1) % 8 == 0:
                start_ns = time.perf_counter_ns()
                model.rest()
                elapsed_ns += time.perf_counter_ns() - start_ns
            if step + 1 in AUDITS:
                stage[str(step + 1)] = audit(model, world, seen, step + 1)
        if world.paid != 80 or model.causal_events != 70:
            raise AssertionError("SL09_PHYSICAL_BUDGET")
        end_snapshot = model.snapshot()
        if Agent.restore(end_snapshot).snapshot() != end_snapshot:
            raise AssertionError("SL09_FINAL_RESTORE")
        trace = digest(paid_ledger)
        all_traces.append(trace)
        world_results[arm] = {
            "trace_sha256": trace,
            "paid_steps": world.paid, "flips": 10,
            "causal_observations": model.causal_events,
            "cold_checkpoint_bytes": cold_bytes,
            "final_checkpoint_bytes": len(end_snapshot),
            "final_checkpoint_sha256": hashlib.sha256(end_snapshot).hexdigest(),
            "context_switches": model.switches,
            "prequential": prequential,
            "stage_audits": stage,
            "cpu_ns": elapsed_ns,
        }
    if len(set(all_traces)) != 1:
        raise AssertionError("SL09_UNMATCHED_PHYSICAL_TRAJECTORIES")
    return {"seed": seed, "cohort": cohort,
            "identical_paid_trace_sha256": all_traces[0],
            "arms": world_results}


def run():
    worlds = [one_world(seed, cohort) for cohort, seeds in COHORTS.items()
              for seed in seeds]
    metrics = ("correct", "wrong_confident", "abstained", "unseen_correct",
               "unseen_wrong_confident", "unseen_abstained")
    agg = {
        cohort: {
            arm: {
                k: sum(w["arms"][arm]["stage_audits"]["80"][k]
                       for w in worlds if w["cohort"] == cohort)
                for k in metrics
            }
            for arm in ARMS
        }
        for cohort in COHORTS
    }
    cand = "candidate_compositional_episodic"
    refs = ("independent_exact_bayes_grammar",
            "independent_tabular_episodic")
    abl = ("candidate_no_composition", "candidate_no_episodic")
    stronger = lambda cohort, key: max(agg[cohort][a][key] for a in refs)
    safest = lambda cohort: min(
        agg[cohort][a]["wrong_confident"] for a in refs)
    odd = agg["COMPOSITION_OOD"][cand]
    cpu = statistics.median(
        w["arms"][cand]["cpu_ns"] /
        max(1, w["arms"]["independent_exact_bayes_grammar"]["cpu_ns"])
        for w in worlds)
    primary = (
        odd["correct"] >= stronger("COMPOSITION_OOD", "correct") + 16
        and odd["unseen_correct"] >= stronger(
            "COMPOSITION_OOD", "unseen_correct") + 8
        and odd["wrong_confident"] <= safest("COMPOSITION_OOD") + 4
        and all(agg[c][cand]["correct"] >= stronger(c, "correct") - limit
                for c, limit in (("RETURN_A", 16), ("RETURN_B", 16),
                                 ("STABLE", 8)))
        and agg["STABLE"][cand]["wrong_confident"] <= safest("STABLE")
        and all(odd["correct"] >= agg["COMPOSITION_OOD"][a]["correct"] + 8
                for a in abl)
        and cpu <= 1.0
    )
    mixed = (
        odd["correct"] > stronger("COMPOSITION_OOD", "correct")
        or odd["unseen_correct"] > stronger(
            "COMPOSITION_OOD", "unseen_correct")
    )
    return {
        "schema": SCHEMA, "preregister_commit": FREEZE,
        "parent_sha": PARENT, "world_count": len(worlds),
        "arms": list(ARMS), "primary_pass": bool(primary),
        "classification": ("DEV_SIGNAL_NOT_SCIENCE" if primary else
                           "MIXED_DEV" if mixed else "NEGATIVE_DEV"),
        "scientific_acceptance": "UNVERIFIED",
        "native_integration": False,
        "exact_matched_physical_trajectories": True,
        "compute_matched": False,
        "median_candidate_cpu_ratio_vs_bayesian": cpu,
        "charged_steps": sum(
            arm["paid_steps"] for w in worlds for arm in w["arms"].values()),
        "causal_observations": sum(
            arm["causal_observations"]
            for w in worlds for arm in w["arms"].values()),
        "aggregates": agg, "worlds": worlds,
    }


if __name__ == "__main__":
    print(json.dumps(run(), separators=(",", ":"), sort_keys=True))
