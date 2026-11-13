"""DG1-SL14: compact physical causal-DNA fingerprints on a distinct 6-bit world.

Prospective protocol frozen FIRST: 272cbb87542d87c779161780602cfddfb7439e8a.
Synthetic development, not native Yggdrasil architecture or scientific acceptance.
All agents receive public physical state/action/observed consequence only.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import statistics
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
FREEZE = "272cbb87542d87c779161780602cfddfb7439e8a"
PARENT = "318baa17dc239dc0f7c3851dba2c9b99afa3a6ac"
SCHEMA = "ygg.dg1-sl14.causal-dna.v1"
COHORTS = {
    "ABAB": tuple(range(107001, 107009)),
    "ABAC": tuple(range(107009, 107017)),
    "MIXED": tuple(range(107017, 107025)),
    "STABLE": tuple(range(107025, 107033)),
}
ARMS = (
    "fingerprint_active", "no_retrieval_on_active",
    "independent_bayes_on_active", "rolling_window_on_active",
    "flat_lookup_on_active", "fingerprint_passive",
)
PAIRED = ARMS[:5]
AUDITS = (24, 48, 54, 72, 78, 96)
COLD = (43, 67, 89)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


def check_x(x):
    if type(x) is not int or not 0 <= x < 8:
        raise ValueError("SL14_INVALID_PUBLIC_INPUT")


def check_action(a):
    if type(a) is not int or not 0 <= a < 3:
        raise ValueError("SL14_INVALID_PHYSICAL_ACTION")


def check_state(s):
    if type(s) is not int or not 0 <= s < 64:
        raise ValueError("SL14_INVALID_PHYSICAL_STATE")


def pair(x, a):
    check_x(x)
    check_action(a)
    i, j = ((0, 1), (1, 2), (2, 0))[a]
    return ((x >> i) & 1) | (((x >> j) & 1) << 1)


def gate(g, p):
    if type(g) is not int or not 0 <= g < 6:
        raise ValueError("SL14_BAD_GATE")
    if type(p) is not int or not 0 <= p < 4:
        raise ValueError("SL14_BAD_PAIR")
    x, y = p & 1, (p >> 1) & 1
    v = (x & y, x | y, x ^ y)
    return v[g] if g < 3 else 1 - v[g - 3]


def pack(kind, payload):
    body = {"schema": SCHEMA, "kind": kind, "payload": payload}
    data = canonical({"data": body, "sha256": digest(body)})
    if len(data) > 8192:
        raise ValueError("SL14_CHECKPOINT_CAPACITY")
    return data


def unpack(raw, kind):
    if type(raw) is not bytes or not 0 < len(raw) <= 8192:
        raise ValueError("SL14_INVALID_CHECKPOINT_BYTES")
    try:
        w = json.loads(raw)
        if type(w) is not dict or set(w) != {"data", "sha256"}:
            raise ValueError("SL14_INVALID_CHECKPOINT_WRAPPER")
        d = w["data"]
        if (type(d) is not dict or set(d) !=
                {"schema", "kind", "payload"} or
                d["schema"] != SCHEMA or d["kind"] != kind or
                digest(d) != w["sha256"] or
                canonical(w) != raw):
            raise ValueError("SL14_CHECKPOINT_HASH_OR_FORMAT")
        return d["payload"]
    except (TypeError, KeyError, UnicodeError, OverflowError,
            ValueError) as e:
        raise ValueError("SL14_CORRUPTED_CHECKPOINT") from e


class World:
    """Only this class knows phase and hidden action-conditioned rules."""
    def __init__(self, seed, cohort):
        if cohort not in COHORTS or seed not in COHORTS[cohort]:
            raise ValueError("SL14_UNREGISTERED_WORLD")
        self.cohort = cohort
        self.seed = seed
        self.paid = 0
        r_a = random.Random(seed * 103 + 17)
        r_b = random.Random(seed * 103 + 941)
        self.rules_a = tuple(r_a.randrange(3) for _ in range(3))
        self.rules_b = tuple(3 + r_b.randrange(3) for _ in range(3))
        r_c = random.Random(seed * 103 + 1789)
        variants = [g for g in range(6)
                    if g not in (self.rules_a[2], self.rules_b[2])]
        self.rules_c = (
            self.rules_a[0], self.rules_b[1],
            variants[r_c.randrange(len(variants))],
        )

    def _phase(self, step):
        if self.cohort == "STABLE":
            return "A"
        if step < 24:
            return "A"
        if step < 48:
            return "B"
        if step < 72:
            return "C" if self.cohort == "MIXED" else "A"
        if self.cohort == "ABAB":
            return "B"
        if self.cohort == "ABAC":
            return "C"
        return "A"

    def _rules(self, completed):
        tag = self._phase(completed - 1)
        return (self.rules_a if tag == "A" else
                self.rules_b if tag == "B" else self.rules_c)

    def step(self, state, step, chosen=None):
        check_state(state)
        if type(step) is not int or step != self.paid or step >= 96:
            raise ValueError("SL14_UNCHARGED_OR_REPLAYED_STEP")
        if step % 5 == 4:
            if chosen is not None:
                raise ValueError("SL14_CANNOT_OVERRIDE_PHYSICAL_PERTURBATION")
            kind, act = "perturb", (step // 5) % 3
            after = state ^ (1 << act)
        else:
            kind = "causal"
            if step < 48:
                if chosen is not None:
                    raise ValueError("SL14_ILLEGAL_PRE48_INTERVENTION")
                act = step % 3
            else:
                check_action(chosen)
                act = chosen
            rules = (self.rules_a if self._phase(step) == "A" else
                     self.rules_b if self._phase(step) == "B" else
                     self.rules_c)
            after = state ^ (gate(rules[act], pair(state & 7, act)) << (3+act))
        self.paid += 1
        return kind, act, after

    def audit_truth(self, x, a, completed):
        check_x(x)
        check_action(a)
        if type(completed) is not int or completed not in AUDITS:
            raise ValueError("SL14_PRIVATE_EVALUATOR_BOUNDARY")
        return gate(self._rules(completed)[a], pair(x, a))


def empty_bank(birth):
    return {
        "err": [[0] * 6 for _ in range(3)],
        "n_by_action": [0, 0, 0],
        "n": 0, "seen": 0, "birth": birth,
    }


class Fingerprint:
    """Compact, composable three-action six-gate causal rule evidence."""
    kind = "fingerprint"

    def __init__(self, allow_retrieval=True):
        if type(allow_retrieval) is not bool:
            raise ValueError("SL14_INVALID_RETRIEVAL_MODE")
        self.allow_retrieval = allow_retrieval
        self.banks = [empty_bank(1)]
        self.active = 0
        self.witness = []
        self.transitions = []
        self.causal_events = 0

    def _predict_bank(self, b, x, a):
        check_x(x)
        check_action(a)
        if type(b) is not int or not 0 <= b < len(self.banks):
            raise ValueError("SL14_BAD_BANK_INDEX")
        errors = self.banks[b]["err"][a]
        best = min(range(6), key=lambda j: (errors[j], j))
        return gate(best, pair(x, a))

    def predict(self, x, a):
        return self._predict_bank(self.active, x, a)

    def choose(self, x, step):
        check_x(x)
        if type(step) is not int or not 48 <= step < 96 or step % 5 == 4:
            raise ValueError("SL14_ILLEGAL_DIAGNOSTIC_ACTION")
        current = self.banks[self.active]
        archived = [
            i for i, bank in enumerate(self.banks)
            if i != self.active and bank["n"] >= 6
        ]
        scores = []
        for a in range(3):
            current_bit = self.predict(x, a)
            disagree = sum(
                int(self._predict_bank(i, x, a) != current_bit)
                for i in archived
            )
            errs = current["err"][a]
            best = sorted(range(6), key=lambda g: (errs[g], g))[:2]
            ambiguity = int(
                gate(best[0], pair(x, a)) !=
                gate(best[1], pair(x, a))
            )
            unseen = int(
                not (current["seen"] & (1 << (a * 4 + pair(x, a))))
            )
            scores.append(10 * disagree + 2 * ambiguity + unseen)
        return max(range(3), key=lambda a: (
            scores[a], -((a-step) % 3)
        ))

    def observe(self, x, a, changed):
        check_x(x)
        check_action(a)
        if type(changed) is not int or changed not in (0, 1):
            raise ValueError("SL14_NONPHYSICAL_CHANGED_BIT")
        if self.causal_events >= 77:
            raise ValueError("SL14_CAUSAL_CAPACITY")
        p = pair(x, a)
        miss = int(self.predict(x, a) != changed)
        self.witness.append([x, a, changed, miss])
        self.witness = self.witness[-4:]
        window = self.witness
        if (len(window) == 4 and
            len({(v[0], v[1]) for v in window}) >= 3 and
            self.banks[self.active]["n"] >= 6):
            active_hits = sum(
                self._predict_bank(self.active, x0, a0) == bit
                for x0, a0, bit, _ in window
            )
            candidates = []
            if self.allow_retrieval:
                for i, bank in enumerate(self.banks):
                    if i == self.active or bank["n"] < 6:
                        continue
                    hits = sum(
                        self._predict_bank(i, x0, a0) == bit
                        for x0, a0, bit, _ in window
                    )
                    if hits >= 3 and hits >= active_hits + 2:
                        candidates.append((hits, -i, i))
            target = -1
            reused = False
            if candidates:
                target = max(candidates)[2]
                reused = True
            elif (sum(item[3] for item in window) >= 3 and
                  len(self.banks) < 3):
                target = len(self.banks)
                self.banks.append(empty_bank(self.causal_events + 1))
            if target >= 0:
                source = self.active
                self.active = target
                self.transitions.append([
                    self.causal_events + 1, source, target, int(reused),
                ])
                self.witness = []
        bank = self.banks[self.active]
        for g in range(6):
            bank["err"][a][g] += int(gate(g, p) != changed)
        bank["n_by_action"][a] += 1
        bank["n"] += 1
        bank["seen"] |= 1 << (a * 4 + p)
        self.causal_events += 1

    def snapshot(self):
        return pack(self.kind, {
            "allow_retrieval": self.allow_retrieval,
            "banks": self.banks, "active": self.active,
            "witness": self.witness, "transitions": self.transitions,
            "causal_events": self.causal_events,
        })

    @classmethod
    def restore(cls, raw):
        p = unpack(raw, cls.kind)
        if (type(p) is not dict or set(p) != {
                "allow_retrieval", "banks", "active", "witness",
                "transitions", "causal_events"}):
            raise ValueError("SL14_CORRUPT_FINGERPRINT")
        out = cls(p["allow_retrieval"])
        if (type(p["banks"]) is not list or not 1 <= len(p["banks"]) <= 3 or
            type(p["active"]) is not int or
            not 0 <= p["active"] < len(p["banks"]) or
            type(p["causal_events"]) is not int or
            not 0 <= p["causal_events"] <= 77 or
            type(p["witness"]) is not list or len(p["witness"]) > 4 or
            type(p["transitions"]) is not list or
            len(p["transitions"]) > 77):
            raise ValueError("SL14_BAD_FINGERPRINT_METADATA")
        for bank in p["banks"]:
            if (type(bank) is not dict or
                set(bank) != {"err", "n_by_action", "n", "seen", "birth"} or
                type(bank["n"]) is not int or bank["n"] < 0 or
                type(bank["birth"]) is not int or
                not 1 <= bank["birth"] <= 77 or
                type(bank["seen"]) is not int or
                not 0 <= bank["seen"] < (1 << 12) or
                type(bank["n_by_action"]) is not list or
                len(bank["n_by_action"]) != 3 or
                any(type(v) is not int or v < 0 or v > 77
                    for v in bank["n_by_action"]) or
                sum(bank["n_by_action"]) != bank["n"] or
                type(bank["err"]) is not list or
                len(bank["err"]) != 3):
                raise ValueError("SL14_BAD_EARNED_MODULE")
            for a in range(3):
                if (type(bank["err"][a]) is not list or
                    len(bank["err"][a]) != 6 or
                    any(type(v) is not int or
                        v < 0 or v > bank["n_by_action"][a]
                        for v in bank["err"][a])):
                    raise ValueError("SL14_BAD_GATE_COUNTS")
        for w in p["witness"]:
            if type(w) is not list or len(w) != 4:
                raise ValueError("SL14_BAD_WITNESS")
            check_x(w[0]); check_action(w[1])
            if any(type(v) is not int or v not in (0, 1) for v in w[2:]):
                raise ValueError("SL14_BAD_WITNESS_BIT")
        last = 0
        for v in p["transitions"]:
            if (type(v) is not list or len(v) != 4 or
                any(type(k) is not int for k in v) or
                v[0] <= last or v[0] > p["causal_events"] or
                not 0 <= v[1] < len(p["banks"]) or
                not 0 <= v[2] < len(p["banks"]) or
                v[1] == v[2] or v[3] not in (0, 1) or
                (not p["allow_retrieval"] and v[3])):
                raise ValueError("SL14_BAD_SWITCH_PROVENANCE")
            last = v[0]
        if sum(b["n"] for b in p["banks"]) != p["causal_events"]:
            raise ValueError("SL14_UNEARNED_CAUSAL_EVENTS")
        out.banks = p["banks"]
        out.active = p["active"]
        out.witness = p["witness"]
        out.transitions = p["transitions"]
        out.causal_events = p["causal_events"]
        if out.snapshot() != raw:
            raise ValueError("SL14_NONCANONICAL_FINGERPRINT")
        return out


class IndependentBayes:
    """Independent six-law posterior with 0.88 physical-event forgetting."""
    kind = "independent_bayes"

    def __init__(self):
        self.cost = [[0.0]*6 for _ in range(3)]
        self.causal_events = 0

    def predict(self, x, a):
        p = pair(x, a)
        penalties = self.cost[a]
        best = min(penalties)
        weights = [math.exp(-math.log(9.0) * (v-best)) for v in penalties]
        yes = sum(w for g, w in enumerate(weights) if gate(g, p))
        return int(2*yes > sum(weights))

    def observe(self, x, a, changed):
        p = pair(x, a)
        if type(changed) is not int or changed not in (0, 1):
            raise ValueError("SL14_INVALID_BAYES_EVIDENCE")
        for j in range(3):
            for g in range(6):
                self.cost[j][g] *= 0.88
                if j == a:
                    self.cost[j][g] += int(gate(g, p) != changed)
        self.causal_events += 1

    def snapshot(self):
        return pack(self.kind, {"cost": self.cost, "n": self.causal_events})

    @classmethod
    def restore(cls, raw):
        p = unpack(raw, cls.kind)
        if (type(p) is not dict or set(p) != {"cost", "n"} or
            type(p["n"]) is not int or not 0 <= p["n"] <= 77 or
            type(p["cost"]) is not list or len(p["cost"]) != 3):
            raise ValueError("SL14_BAD_BAYES_SNAPSHOT")
        for row in p["cost"]:
            if (type(row) is not list or len(row) != 6 or
                any(type(z) not in (float, int) or
                    not math.isfinite(z) or z < 0 or z > 77 for z in row)):
                raise ValueError("SL14_BAD_BAYES_POSTERIOR")
        out = cls()
        out.cost = p["cost"]
        out.causal_events = p["n"]
        if out.snapshot() != raw:
            raise ValueError("SL14_NONCANONICAL_BAYES")
        return out


class RollingRule:
    """Independently refits public gate grammar on last 18 paid events."""
    kind = "rolling_rule"

    def __init__(self):
        self.events = []
        self.causal_events = 0

    def predict(self, x, a):
        p = pair(x, a)
        relevant = [(px, bit) for px, act, bit in self.events if act == a]
        best = min(range(6), key=lambda g: (
            sum(gate(g, pair(px, a)) != bit for px, bit in relevant), g))
        return gate(best, p)

    def observe(self, x, a, changed):
        check_x(x); check_action(a)
        if type(changed) is not int or changed not in (0, 1):
            raise ValueError("SL14_ROLLING_INVALID_EVENT")
        self.events.append([x, a, changed])
        self.events = self.events[-18:]
        self.causal_events += 1

    def snapshot(self):
        return pack(self.kind, {"events": self.events, "n": self.causal_events})

    @classmethod
    def restore(cls, raw):
        p = unpack(raw, cls.kind)
        validate_events(p, 18)
        o = cls()
        o.events, o.causal_events = p["events"], p["n"]
        if o.snapshot() != raw:
            raise ValueError("SL14_NONCANONICAL_ROLLING")
        return o


class FlatLookup:
    """No Boolean compositional grammar: local majority in last 18 events."""
    kind = "flat_lookup"

    def __init__(self):
        self.events = []
        self.causal_events = 0

    def predict(self, x, a):
        p = pair(x, a)
        outcomes = [
            bit for px, act, bit in self.events
            if act == a and pair(px, a) == p
        ]
        return int(sum(outcomes)*2 > len(outcomes)) if outcomes else 0

    def observe(self, x, a, changed):
        check_x(x); check_action(a)
        if type(changed) is not int or changed not in (0, 1):
            raise ValueError("SL14_FLAT_INVALID_EVENT")
        self.events.append([x, a, changed])
        self.events = self.events[-18:]
        self.causal_events += 1

    def snapshot(self):
        return pack(self.kind, {"events": self.events, "n": self.causal_events})

    @classmethod
    def restore(cls, raw):
        p = unpack(raw, cls.kind)
        validate_events(p, 18)
        o = cls()
        o.events, o.causal_events = p["events"], p["n"]
        if o.snapshot() != raw:
            raise ValueError("SL14_NONCANONICAL_FLAT")
        return o


def validate_events(p, limit):
    if (type(p) is not dict or set(p) != {"events", "n"} or
        type(p["n"]) is not int or not 0 <= p["n"] <= 77 or
        type(p["events"]) is not list or len(p["events"]) > limit or
        len(p["events"]) > p["n"]):
        raise ValueError("SL14_INVALID_EPISODIC_CONTROL")
    for ev in p["events"]:
        if type(ev) is not list or len(ev) != 3:
            raise ValueError("SL14_INVALID_PAID_EVENT")
        check_x(ev[0]); check_action(ev[1])
        if type(ev[2]) is not int or ev[2] not in (0, 1):
            raise ValueError("SL14_NONPHYSICAL_EVENT")


def learner(arm):
    if arm in ("fingerprint_active", "fingerprint_passive"):
        return Fingerprint()
    if arm == "no_retrieval_on_active":
        return Fingerprint(False)
    if arm == "independent_bayes_on_active":
        return IndependentBayes()
    if arm == "rolling_window_on_active":
        return RollingRule()
    if arm == "flat_lookup_on_active":
        return FlatLookup()
    raise ValueError("SL14_UNKNOWN_ARM")


def restore(x, raw):
    return type(x).restore(raw)


def audit(model, world, seen_full, seen_local, step):
    metrics = {k: 0 for k in (
        "correct", "wrong_confident",
        "unseen_correct", "unseen_wrong_confident",
        "unseen_local_correct", "unseen_local_wrong_confident"
    )}
    for x in range(8):
        for a in range(3):
            truth = world.audit_truth(x, a, step)
            hit = model.predict(x, a) == truth
            metrics["correct" if hit else "wrong_confident"] += 1
            if (x, a) not in seen_full:
                metrics["unseen_correct" if hit else
                        "unseen_wrong_confident"] += 1
            if (a, pair(x, a)) not in seen_local:
                metrics["unseen_local_correct" if hit else
                        "unseen_local_wrong_confident"] += 1
    return metrics


def trial(seed, cohort, arm, policy, replay_plan=None):
    if arm not in ARMS:
        raise ValueError("SL14_UNREGISTERED_ARM")
    if replay_plan is not None and (
        type(replay_plan) is not list or len(replay_plan) != 96):
        raise ValueError("SL14_UNAUTHORIZED_REPLAY")
    w, model = World(seed, cohort), learner(arm)
    state = seed % 64
    ledger, choices, causal_steps = [], [], []
    seen_full, seen_local = set(), set()
    audits, cold_sizes = {}, []
    cpu_ns = 0
    for step in range(96):
        # Cold snapshots are inert (the step index is NOT delivered to model).
        if step in COLD:
            snap = model.snapshot()
            rehydrated = restore(model, snap)
            if (snap != rehydrated.snapshot() or any(
                model.predict(x, a) != rehydrated.predict(x, a)
                for x in range(8) for a in range(3))):
                raise AssertionError("SL14_COLD_PREDICTION_OR_BYTE_MISMATCH")
            model = rehydrated
            cold_sizes.append(len(snap))
        pay_causal_choice = step >= 48 and step % 5 != 4
        t0 = time.perf_counter_ns()
        if pay_causal_choice:
            if replay_plan is not None:
                choice = replay_plan[step]
            elif policy == "passive":
                choice = step % 3
            elif policy == "diagnostic" and isinstance(model, Fingerprint):
                choice = model.choose(state & 7, step)
            else:
                raise ValueError("SL14_UNAUTHORIZED_ACTION_POLICY")
            check_action(choice)
        else:
            choice = None
            if replay_plan is not None and replay_plan[step] is not None:
                raise ValueError("SL14_FREE_OR_UNCHARGED_REPLAY_ACTION")
        cpu_ns += time.perf_counter_ns() - t0
        kind, action, nxt = w.step(state, step, choice)
        if kind == "causal":
            x = state & 7
            changed = int(state != nxt)
            if nxt not in (state, state ^ (1 << (3 + action))):
                raise AssertionError("SL14_PHYSICAL_NONLOCAL_TRANSITION")
            t0 = time.perf_counter_ns()
            model.observe(x, action, changed)
            cpu_ns += time.perf_counter_ns() - t0
            seen_full.add((x, action))
            seen_local.add((action, pair(x, action)))
            causal_steps.append(step)
        ledger.append([state, kind, action, nxt])
        choices.append(choice)
        state = nxt
        if step+1 in AUDITS:
            audits[str(step+1)] = audit(
                model, w, seen_full, seen_local, step+1)
    if w.paid != 96 or model.causal_events != 77 or (
        sum(e[1] == "perturb" for e in ledger) != 19):
        raise AssertionError("SL14_CHARGED_PHYSICAL_BUDGET_DRIFT")
    last = model.snapshot()
    if restore(model, last).snapshot() != last:
        raise AssertionError("SL14_FINAL_SNAPSHOT_DIVERGENCE")
    if replay_plan is not None and replay_plan != choices:
        raise AssertionError("SL14_REPLAY_ACTION_PLAN_DRIFT")
    transitions = []
    if isinstance(model, Fingerprint):
        for count, src, dst, reused in model.transitions:
            transitions.append({
                "charged_step": causal_steps[count-1],
                "from_bank": src, "to_bank": dst,
                "archived_reuse": bool(reused),
                "bank_birth_step": causal_steps[model.banks[dst]["birth"]-1],
            })
    return {
        "charged_steps": w.paid, "causal_observations": model.causal_events,
        "charged_input_perturbations": 19,
        "trace_first48_sha256": digest(ledger[:48]),
        "trace_sha256": digest(ledger),
        "physical_ledger": ledger, "action_plan": choices,
        "snapshot_bytes": cold_sizes,
        "final_snapshot_bytes": len(last),
        "final_snapshot_sha256": hashlib.sha256(last).hexdigest(),
        "transitions": transitions,
        "audits": audits,
        "cpu_ns": cpu_ns,
    }


def one_world(seed, cohort):
    primary = trial(seed, cohort, "fingerprint_active", "diagnostic")
    arms = {"fingerprint_active": primary}
    for arm in PAIRED[1:]:
        arms[arm] = trial(
            seed, cohort, arm, "replay", primary["action_plan"])
        if arms[arm]["trace_sha256"] != primary["trace_sha256"]:
            raise AssertionError("SL14_MATCHED_PHYSICAL_INFORMATION_DRIFT")
    arms["fingerprint_passive"] = trial(
        seed, cohort, "fingerprint_passive", "passive")
    if len({r["trace_first48_sha256"] for r in arms.values()}) != 1:
        raise AssertionError("SL14_PREFIX_PHYSICAL_DRIFT")
    return {"seed": seed, "cohort": cohort, "arms": arms}


def genuine_return_flags(w):
    t = w["arms"]["fingerprint_active"]["transitions"]
    return {
        "A2": any(48 <= q["charged_step"] < 72 and
                  q["archived_reuse"] and
                  q["bank_birth_step"] < 24 for q in t),
        "B2": any(72 <= q["charged_step"] < 96 and
                  q["archived_reuse"] and
                  24 <= q["bank_birth_step"] < 48 for q in t),
        "A4": any(72 <= q["charged_step"] < 96 and
                  q["archived_reuse"] and
                  q["bank_birth_step"] < 24 for q in t),
        "falseC": any(72 <= q["charged_step"] < 96 and
                      q["archived_reuse"] for q in t),
    }


def run():
    worlds = [one_world(seed, cohort) for cohort, seeds in COHORTS.items()
              for seed in seeds]
    keys = (
        "correct", "wrong_confident",
        "unseen_correct", "unseen_wrong_confident",
        "unseen_local_correct", "unseen_local_wrong_confident",
    )
    aggregates = {
        cohort: {
            arm: {
                str(t): {
                    key: sum(w["arms"][arm]["audits"][str(t)][key]
                             for w in worlds if w["cohort"] == cohort)
                    for key in keys
                }
                for t in AUDITS
            }
            for arm in ARMS
        }
        for cohort in COHORTS
    }
    counts = {
        "ABAB_A2": sum(genuine_return_flags(w)["A2"]
                       for w in worlds if w["cohort"] == "ABAB"),
        "ABAB_B2": sum(genuine_return_flags(w)["B2"]
                       for w in worlds if w["cohort"] == "ABAB"),
        "MIXED_A4": sum(genuine_return_flags(w)["A4"]
                        for w in worlds if w["cohort"] == "MIXED"),
        "ABAC_falseC": sum(genuine_return_flags(w)["falseC"]
                           for w in worlds if w["cohort"] == "ABAC"),
    }
    cand = "fingerprint_active"
    no = "no_retrieval_on_active"
    bayes = "independent_bayes_on_active"
    rolling = "rolling_window_on_active"
    flat = "flat_lookup_on_active"
    a = aggregates
    v = lambda cohort, arm, step, key="correct": a[cohort][arm][str(step)][key]
    cpu_bayes = statistics.median([
        w["arms"][cand]["cpu_ns"] /
        max(1, w["arms"][bayes]["cpu_ns"]) for w in worlds])
    cpu_no = statistics.median([
        w["arms"][cand]["cpu_ns"] /
        max(1, w["arms"][no]["cpu_ns"]) for w in worlds])
    primary_gates = {
        "ABAB_A2_retrieval": counts["ABAB_A2"] >= 5,
        "ABAB_B2_retrieval": counts["ABAB_B2"] >= 5,
        "ABAB_early_A2_vs_noarchive":
            v("ABAB", cand, 54) >= v("ABAB", no, 54) + 12,
        "ABAB_early_B2_vs_noarchive":
            v("ABAB", cand, 78) >= v("ABAB", no, 78) + 12,
        "ABAB_final_B2_vs_noarchive":
            v("ABAB", cand, 96) >= v("ABAB", no, 96) + 16,
        "ABAB_final_B2_vs_rolling":
            v("ABAB", cand, 96) >= v("ABAB", rolling, 96) + 8,
        "ABAB_final_B2_vs_bayes":
            v("ABAB", cand, 96) >= v("ABAB", bayes, 96) + 8,
        "ABAB_final_B2_vs_flat":
            v("ABAB", cand, 96) >= v("ABAB", flat, 96) + 8,
        "ABAB_B2_unseen_vs_bayes":
            v("ABAB", cand, 96, "unseen_correct") >=
            v("ABAB", bayes, 96, "unseen_correct") + 4,
        "ABAB_B2_unseen_vs_noarchive":
            v("ABAB", cand, 96, "unseen_correct") >=
            v("ABAB", no, 96, "unseen_correct") + 4,
        "ABAC_false_retrieval": counts["ABAC_falseC"] <= 2,
        "ABAC_final_noarchive_guardrail":
            v("ABAC", cand, 96) >= v("ABAC", no, 96) - 8,
        "MIXED_A4_retrieval": counts["MIXED_A4"] >= 4,
        "MIXED_A4_final_vs_noarchive":
            v("MIXED", cand, 96) >= v("MIXED", no, 96) + 8,
        "STABLE_nonregression":
            v("STABLE", cand, 96) >= v("STABLE", no, 96) - 8,
        "STABLE_confident_wrong_guardrail":
            v("STABLE", cand, 96, "wrong_confident") <=
            v("STABLE", no, 96, "wrong_confident") + 8,
        "cpu_ratio_vs_bayes": cpu_bayes <= 2.0,
        "cpu_ratio_vs_noarchive": cpu_no <= 2.5,
    }
    paid = sum(row["charged_steps"] for w in worlds
               for row in w["arms"].values())
    causal = sum(row["causal_observations"] for w in worlds
                 for row in w["arms"].values())
    if (len(worlds) != 32 or paid != 18432 or causal != 14784 or
        any(len(row["snapshot_bytes"]) != 3 or
            max(row["snapshot_bytes"] +
                [row["final_snapshot_bytes"]]) > 8192 or
            row["charged_input_perturbations"] != 19
            for w in worlds for row in w["arms"].values())):
        raise AssertionError("SL14_FROZEN_CHARGED_CUSTODY_INVALID")
    mixed = (
        counts["ABAB_A2"] > 0 or counts["ABAB_B2"] > 0 or
        v("ABAB", cand, 96) > v("ABAB", no, 96) or
        v("ABAB", cand, 96, "unseen_correct") >
        v("ABAB", no, 96, "unseen_correct")
    )
    return {
        "schema": SCHEMA, "freeze_sha": FREEZE, "parent_sha": PARENT,
        "world_count": len(worlds), "arms": list(ARMS),
        "primary_pass": all(primary_gates.values()),
        "classification": ("DEV_SIGNAL_NOT_SCIENCE"
                           if all(primary_gates.values()) else
                           "MIXED_DEV" if mixed else "NEGATIVE_DEV"),
        "scientific_acceptance": "UNVERIFIED",
        "native_model_changed": False,
        "identical_physical_information_within_replay_group": True,
        "different_information_for_passive_group": True,
        "charged_steps": paid,
        "paid_causal_observations": causal,
        "charged_input_perturbations": paid - causal,
        "archive_reuse_world_counts": counts,
        "median_cpu_ratio_candidate_vs_bayes": cpu_bayes,
        "median_cpu_ratio_candidate_vs_noarchive": cpu_no,
        "primary_gates": primary_gates,
        "aggregates": aggregates, "worlds": worlds,
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, separators=(",", ":")))
