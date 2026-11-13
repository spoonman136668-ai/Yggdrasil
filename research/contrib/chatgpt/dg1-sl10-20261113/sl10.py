"""DG1-SL10: paid causal hypothesis tournaments; synthetic non-token DEV.

Predeclared before code/outcome at 43d7307c3bcaf2862c4312583c6b220766feb04e.
No hidden rules, generator seeds, evaluator labels, or oracle truths are passed
to learners/selectors. All events come from physically charged world.step.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import statistics
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
FREEZE = "43d7307c3bcaf2862c4312583c6b220766feb04e"
PARENT = "59d7153290fb85b4170d8fb2709acc376b74ada5"
SCHEMA = "ygg.dg1-sl10.paid-hypothesis-tournaments.v1"
COHORTS = {
    "RETURN_A": tuple(range(103001, 103009)),
    "RETURN_B": tuple(range(103009, 103017)),
    "STABLE": tuple(range(103017, 103025)),
    "COMPOSITION_OOD": tuple(range(103025, 103033)),
}
ARMS = (
    "candidate_active",
    "bayes_on_candidate",
    "candidate_no_episodic_on_candidate",
    "bayes_active",
    "candidate_on_bayes",
    "candidate_passive",
    "bayes_passive",
    "candidate_sham",
    "bayes_on_sham",
)
PAIRS = (
    ("candidate_active", "bayes_on_candidate",
     "candidate_no_episodic_on_candidate"),
    ("bayes_active", "candidate_on_bayes"),
    ("candidate_passive", "bayes_passive"),
    ("candidate_sham", "bayes_on_sham"),
)
FLIPS = (6, 14, 22, 30, 38, 46, 54, 62, 70, 78)
AUDITS = (60, 64, 72, 80)


def load_prior():
    spec = importlib.util.spec_from_file_location(
        "sl10_frozen_sl09", HERE.parent / "dg1-sl09-20261113/sl09.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sl09 = load_prior()
MASKS = sl09.MASKS
PROGRAMS = sl09.PROGRAMS


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


def sha256(value):
    return hashlib.sha256(canonical(value)).hexdigest()


class World(sl09.World):
    """SL09 grammar/phase; new sealed seeds and optional paid postcold actions."""
    def __init__(self, seed, cohort):
        if cohort not in COHORTS or seed not in COHORTS[cohort]:
            raise ValueError("SL10_UNREGISTERED_WORLD")
        self._seed = seed
        self._cohort = cohort
        self.paid = 0
        self._programs = {}
        for phase, alphabet in (("A", (0, 1, 2)), ("B", (3, 4, 5))):
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

    def step(self, state, step, chosen=None):
        sl09.check_state(state)
        if type(step) is not int or step != self.paid or step >= 80:
            raise ValueError("SL10_UNPAID_OR_REPLAYED_STEP")
        if step in FLIPS:
            if chosen is not None:
                raise ValueError("SL10_CANNOT_OVERRIDE_PAID_FLIP")
            kind = "flip"
            action = (step // 8) % 4
            following = state ^ (1 << action)
        else:
            kind = "causal"
            if step < 60:
                if chosen is not None:
                    raise ValueError("SL10_NO_PRE_COLD_POLICY")
                action = step % 4
            else:
                sl09.check_action(chosen)
                action = chosen
            following = state ^ (
                sl09.flip(self._programs[(self._phase(step), action)],
                          state, action) << action
            )
        self.paid += 1
        return kind, action, following


class ExactBayes:
    """Separately coded all-program Bayesian evidence and episodic routing.

    Each action posterior spans the identical complete public grammar, with
    Bernoulli error likelihood of 1:16; no hidden teacher or proxy targets.
    Hypothesis errors are constructed from paid physical event bits.
    """
    def __init__(self):
        self.banks = [[]]
        self.active = 0
        self.recent = []
        self.causal_events = 0
        self.switches = 0
        self._cache = {}

    def _p(self, bank, state, action):
        sl09.check_state(state)
        sl09.check_action(action)
        if type(bank) is not int or not 0 <= bank < len(self.banks):
            raise ValueError("SL10_BAD_BANK")
        key = (bank, action)
        if key not in self._cache:
            observations = [(s, b) for s, a, b in self.banks[bank]
                            if a == action]
            error_counts = [
                sum(((mask >> s) & 1) != b for s, b in observations)
                for mask in MASKS[action]
            ]
            top = max(error_counts, default=0)
            weights = [1 << (4 * (top - e)) for e in error_counts]
            total = sum(weights)
            ones = [
                sum(w for w, mask in zip(weights, MASKS[action])
                    if (mask >> s) & 1)
                for s in range(16)
            ]
            self._cache[key] = (total, ones)
        total, ones = self._cache[key]
        return ones[state], total

    def _bit_in(self, bank, state, action):
        n, d = self._p(bank, state, action)
        return int(2 * n > d)

    def predict(self, state, action):
        return state ^ (self._bit_in(self.active, state, action) << action)

    def uncertainty(self, state, action):
        n, d = self._p(self.active, state, action)
        ppm = n * 1000000 // d
        return ppm * (1000000 - ppm)

    def choose(self, state, step):
        sl09.check_state(state)
        if type(step) is not int or not (60 <= step < 80) or step in FLIPS:
            raise ValueError("SL10_NOT_PAID_CAUSAL_CHOICE")
        return max(range(4), key=lambda a: (
            self.uncertainty(state, a), -((a - step) % 4)))

    def observe(self, before, action, after):
        sl09.check_state(before)
        sl09.check_action(action)
        sl09.check_state(after)
        if after not in (before, before ^ (1 << action)):
            raise ValueError("SL10_NONLOCAL_EVENT")
        if self.causal_events >= 70:
            raise ValueError("SL10_OBSERVATION_LIMIT")
        observed = int(before != after)
        wrong = int(self._bit_in(self.active, before, action) != observed)
        self.recent.append([before, action, observed, wrong])
        self.recent = self.recent[-8:]
        contradictory = {(s, a) for s, a, _, miss in self.recent if miss}
        if len(self.banks[self.active]) >= 12 and len(contradictory) >= 2:
            latest = self.recent[-4:]
            scored = [
                (sum(self._bit_in(i, s, a) == b
                     for s, a, b, _ in latest), i)
                for i in range(len(self.banks)) if i != self.active
            ]
            best = max(scored, default=(-1, -1))
            if best[0] >= 3:
                self.active = best[1]
            elif len(self.banks) < 3:
                self.banks.append([])
                self.active = len(self.banks) - 1
            elif scored:
                self.active = best[1]
            self.switches += 1
            self.recent = []
        self.banks[self.active].append([before, action, observed])
        self.causal_events += 1
        self._cache.clear()

    def rest(self):
        # An evidence-only control has no offline learning or free observation.
        pass

    def snapshot(self):
        payload = {
            "schema": SCHEMA, "class": "independent_exact_bayes",
            "banks": self.banks, "active": self.active,
            "recent": self.recent, "causal_events": self.causal_events,
            "switches": self.switches,
        }
        raw = canonical({"payload": payload, "sha256": sha256(payload)})
        if len(raw) > 8192:
            raise ValueError("SL10_SNAPSHOT_CAPACITY")
        return raw

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= 8192:
                raise ValueError("SL10_BAD_CHECKPOINT_BYTES")
            wrap = json.loads(raw)
            if type(wrap) is not dict or set(wrap) != {"payload", "sha256"}:
                raise ValueError("SL10_BAD_WRAPPER")
            p = wrap["payload"]
            keys = {"schema", "class", "banks", "active", "recent",
                    "causal_events", "switches"}
            if type(p) is not dict or set(p) != keys or (
                p["schema"] != SCHEMA or
                p["class"] != "independent_exact_bayes" or
                sha256(p) != wrap["sha256"]):
                raise ValueError("SL10_BAD_FORMAT_OR_HASH")
            if (type(p["banks"]) is not list or
                not 1 <= len(p["banks"]) <= 3 or
                type(p["active"]) is not int or
                not 0 <= p["active"] < len(p["banks"]) or
                type(p["recent"]) is not list or len(p["recent"]) > 8):
                raise ValueError("SL10_BAD_ROUTER")
            for bank in p["banks"]:
                if type(bank) is not list or len(bank) > 70:
                    raise ValueError("SL10_BAD_BANK_EVENTS")
                for event in bank:
                    if type(event) is not list or len(event) != 3:
                        raise ValueError("SL10_BAD_EVENT")
                    sl09.check_state(event[0])
                    sl09.check_action(event[1])
                    if type(event[2]) is not int or event[2] not in (0, 1):
                        raise ValueError("SL10_BAD_EVENT_BIT")
            for event in p["recent"]:
                if type(event) is not list or len(event) != 4:
                    raise ValueError("SL10_BAD_RECENT")
                sl09.check_state(event[0])
                sl09.check_action(event[1])
                if any(type(v) is not int or v not in (0, 1)
                       for v in event[2:]):
                    raise ValueError("SL10_BAD_RECENT_VALUE")
            if (any(type(p[k]) is not int or not 0 <= p[k] <= 70
                    for k in ("causal_events", "switches")) or
                p["switches"] > p["causal_events"] or
                sum(len(bank) for bank in p["banks"]) != p["causal_events"]):
                raise ValueError("SL10_BAD_COUNTS")
            out = cls()
            for field in ("banks", "active", "recent",
                          "causal_events", "switches"):
                setattr(out, field, p[field])
            if out.snapshot() != raw:
                raise ValueError("SL10_NONCANONICAL")
            return out
        except (ValueError, TypeError, KeyError,
                OverflowError, UnicodeError) as exc:
            raise ValueError("SL10_INVALID_CHECKPOINT") from exc


def candidate_score(model, state, action):
    """Disagreement strictly from paid causal evidence; no oracle truth."""
    sl09.check_state(state)
    sl09.check_action(action)
    active = model.banks[model.active]
    observations = [(s, b) for s, a, b in active if a == action]
    errors = [
        sum(((mask >> s) & 1) != b for s, b in observations)
        for mask in MASKS[action]
    ]
    top = sorted(range(len(PROGRAMS)),
                 key=lambda i: (errors[i], len(set(PROGRAMS[i])),
                                sum(PROGRAMS[i]), i))[:6]
    count = sum((MASKS[action][i] >> state) & 1 for i in top)
    disagreement = count * (len(top) - count)
    cross = int(any(
        model._predict_in_bank(j, state, action) !=
        model._predict_in_bank(model.active, state, action)
        for j in range(len(model.banks)) if j != model.active
    ))
    novelty = int(not any(s == state and a == action for s, a, _ in active))
    return disagreement * 4 + cross * 9 + novelty


def candidate_choose(model, state, step, sham=False):
    sl09.check_state(state)
    if type(step) is not int or not 60 <= step < 80 or step in FLIPS:
        raise ValueError("SL10_INVALID_PAID_POLICY_STEP")
    if model.arm != "candidate_compositional_episodic":
        raise ValueError("SL10_UNAUTHORIZED_CANDIDATE_SELECTOR")
    scores = [candidate_score(model, state, a) for a in range(4)]
    if sham:
        return min(range(4), key=lambda a: (
            scores[a], (a - step) % 4))
    return max(range(4), key=lambda a: (
        scores[a], -((a - step) % 4)))


def model_for(arm):
    if arm in (
        "candidate_active", "candidate_on_bayes",
        "candidate_passive", "candidate_sham"
    ):
        return sl09.Agent("candidate_compositional_episodic")
    if arm == "candidate_no_episodic_on_candidate":
        return sl09.Agent("candidate_no_episodic")
    if arm.startswith("bayes_"):
        return ExactBayes()
    raise ValueError("SL10_UNKNOWN_ARM")


def restore_model(model, snap):
    if isinstance(model, ExactBayes):
        return ExactBayes.restore(snap)
    return sl09.Agent.restore(snap)


def choose(model, state, step, policy):
    if policy == "passive":
        return step % 4
    if policy == "candidate":
        return candidate_choose(model, state, step)
    if policy == "sham":
        return candidate_choose(model, state, step, sham=True)
    if policy == "bayes":
        if not isinstance(model, ExactBayes):
            raise ValueError("SL10_UNPAIRED_BAYES_SELECTOR")
        return model.choose(state, step)
    raise ValueError("SL10_UNAUTHORIZED_POLICY")


def trial(seed, cohort, arm, policy, replay_plan=None):
    if arm not in ARMS:
        raise ValueError("SL10_UNKNOWN_ARM")
    if replay_plan is not None and (
        type(replay_plan) is not list or len(replay_plan) != 80):
        raise ValueError("SL10_BAD_REPLAY_PLAN")
    world = World(seed, cohort)
    model = model_for(arm)
    seen = set()
    state = seed % 16
    stages, ledger, plan = {}, [], []
    prequential = {"correct": 0, "wrong_confident": 0, "abstained": 0}
    after_cold = {"correct": 0, "wrong_confident": 0, "abstained": 0}
    elapsed_ns = 0
    cold_bytes = 0
    chosen_nonpassive = 0
    for step in range(80):
        if step == 60:
            snap = model.snapshot()
            restored = restore_model(model, snap)
            if snap != restored.snapshot() or any(
                model.predict(s, a) != restored.predict(s, a)
                for s in range(16) for a in range(4)
            ):
                raise AssertionError("SL10_COLD_RESTORE_DIVERGED")
            model = restored
            cold_bytes = len(snap)
        active_step = step >= 60 and step not in FLIPS
        start = time.perf_counter_ns()
        if active_step:
            action = (replay_plan[step] if replay_plan is not None
                      else choose(model, state, step, policy))
            sl09.check_action(action)
            chosen_nonpassive += int(action != step % 4)
        else:
            action = None
        elapsed_ns += time.perf_counter_ns() - start
        kind, actual_action, nxt = world.step(state, step, action)
        if kind == "causal":
            start = time.perf_counter_ns()
            predicted = model.predict(state, actual_action)
            verdict = ("abstained" if predicted is None else
                       "correct" if predicted == nxt else "wrong_confident")
            prequential[verdict] += 1
            if step >= 60:
                after_cold[verdict] += 1
            model.observe(state, actual_action, nxt)
            elapsed_ns += time.perf_counter_ns() - start
            seen.add((state, actual_action))
        ledger.append([state, kind, actual_action, nxt])
        plan.append(action)
        state = nxt
        if (step + 1) % 8 == 0:
            start = time.perf_counter_ns()
            model.rest()
            elapsed_ns += time.perf_counter_ns() - start
        if step + 1 in AUDITS:
            stages[str(step + 1)] = sl09.audit(model, world, seen, step + 1)
    if world.paid != 80 or model.causal_events != 70 or (
            sum(row[1] == "flip" for row in ledger) != 10):
        raise AssertionError("SL10_UNMATCHED_CHARGED_BUDGET")
    final_snap = model.snapshot()
    if restore_model(model, final_snap).snapshot() != final_snap:
        raise AssertionError("SL10_FINAL_COLD_FAILURE")
    if replay_plan is not None and plan != replay_plan:
        raise AssertionError("SL10_REPLAY_ACTION_MISMATCH")
    return {
        "paid_steps": world.paid, "charged_flips": 10,
        "causal_observations": model.causal_events,
        "pre_cold_trace_sha256": sha256(ledger[:60]),
        "trace_sha256": sha256(ledger),
        "paid_trace": ledger, "action_plan": plan,
        "cold_checkpoint_bytes": cold_bytes,
        "final_checkpoint_bytes": len(final_snap),
        "final_checkpoint_sha256": hashlib.sha256(final_snap).hexdigest(),
        "prequential": prequential, "after_cold_prequential": after_cold,
        "stage_audits": stages,
        "postcold_nonpassive_choices": chosen_nonpassive,
        "cpu_ns": elapsed_ns,
    }


def one_world(seed, cohort):
    result = {}
    policies = {
        "candidate_active": "candidate",
        "bayes_active": "bayes",
        "candidate_passive": "passive",
        "candidate_sham": "sham",
    }
    for group in PAIRS:
        pilot = group[0]
        result[pilot] = trial(seed, cohort, pilot, policies[pilot])
        plan = result[pilot]["action_plan"]
        for replay in group[1:]:
            result[replay] = trial(seed, cohort, replay, "replay", plan)
        if len({result[k]["trace_sha256"] for k in group}) != 1:
            raise AssertionError("SL10_PAIRED_PAID_INFORMATION_MISMATCH")
    if set(result) != set(ARMS):
        raise AssertionError("SL10_MISSING_ARM")
    if len({r["pre_cold_trace_sha256"] for r in result.values()}) != 1:
        raise AssertionError("SL10_PRE_COLD_ACTION_DRIFT")
    return {
        "seed": seed, "cohort": cohort,
        "shared_pre_cold_trace_sha256": next(
            iter(result.values()))["pre_cold_trace_sha256"],
        "arms": result,
    }


def run():
    worlds = [one_world(seed, cohort) for cohort, seeds in COHORTS.items()
              for seed in seeds]
    keys = ("correct", "wrong_confident", "abstained",
            "unseen_correct", "unseen_wrong_confident", "unseen_abstained")
    aggregate = {
        cohort: {
            arm: {
                key: sum(w["arms"][arm]["stage_audits"]["80"][key]
                         for w in worlds if w["cohort"] == cohort)
                for key in keys
            }
            for arm in ARMS
        }
        for cohort in COHORTS
    }
    c, o = "candidate_active", "COMPOSITION_OOD"
    odd = aggregate[o]
    passive, bayes, replay, sham, ablate = (
        "candidate_passive", "bayes_active", "bayes_on_candidate",
        "candidate_sham", "candidate_no_episodic_on_candidate")
    cpu_ratios = [
        w["arms"][c]["cpu_ns"] / max(w["arms"][bayes]["cpu_ns"], 1)
        for w in worlds
    ]
    cpu_median = statistics.median(cpu_ratios)
    divergent = sum(
        w["arms"][c]["postcold_nonpassive_choices"] > 0 for w in worlds
        if w["cohort"] == o
    )
    primary = (
        odd[c]["correct"] >= odd[passive]["correct"] + 16
        and odd[c]["unseen_correct"] >= odd[passive]["unseen_correct"] + 8
        and odd[c]["wrong_confident"] <= odd[passive]["wrong_confident"] + 4
        and odd[c]["correct"] >= odd[bayes]["correct"] - 8
        and odd[c]["wrong_confident"] <= odd[bayes]["wrong_confident"] + 8
        and odd[c]["correct"] >= odd[replay]["correct"] + 8
        and odd[c]["unseen_correct"] >= odd[replay]["unseen_correct"] + 4
        and odd[c]["correct"] >= odd[sham]["correct"] + 8
        and odd[c]["correct"] >= odd[ablate]["correct"] + 8
        and all(
            aggregate[cohort][c]["correct"] >=
            aggregate[cohort][passive]["correct"] - delta
            for cohort, delta in (
                ("RETURN_A", 16), ("RETURN_B", 16), ("STABLE", 8)))
        and aggregate["STABLE"][c]["wrong_confident"] <= (
            aggregate["STABLE"][passive]["wrong_confident"] + 4)
        and divergent >= 4
        and cpu_median <= 2.0
    )
    mixed = (
        odd[c]["correct"] > odd[passive]["correct"]
        or odd[c]["unseen_correct"] > odd[passive]["unseen_correct"]
    )
    paid_steps = sum(a["paid_steps"] for w in worlds
                     for a in w["arms"].values())
    paid_causes = sum(a["causal_observations"] for w in worlds
                      for a in w["arms"].values())
    if (len(worlds) != 32 or paid_steps != 23040 or
            paid_causes != 20160 or
            not all(a["charged_flips"] == 10 and
                    a["cold_checkpoint_bytes"] <= 8192 and
                    a["final_checkpoint_bytes"] <= 8192
                    for w in worlds for a in w["arms"].values())):
        raise AssertionError("SL10_HARD_PREREG_CUSTODY_FAIL")
    return {
        "schema": SCHEMA, "freeze_sha": FREEZE, "parent_sha": PARENT,
        "world_count": len(worlds), "arms": list(ARMS),
        "primary_pass": bool(primary),
        "classification": (
            "DEV_SIGNAL_NOT_SCIENCE" if primary else
            "MIXED_DEV" if mixed else "NEGATIVE_DEV"
        ),
        "scientific_acceptance": "UNVERIFIED",
        "native_model_changed": False,
        "identical_information_within_replay_pairs": True,
        "different_information_across_active_policies": True,
        "compute_matched": False,
        "paid_steps": paid_steps, "paid_causal_observations": paid_causes,
        "charged_flips": paid_steps - paid_causes,
        "ood_worlds_nonpassive_selected": divergent,
        "median_candidate_cpu_ratio_vs_bayes_active": cpu_median,
        "aggregate": aggregate, "worlds": worlds,
    }


if __name__ == "__main__":
    print(json.dumps(run(), separators=(",", ":"), sort_keys=True))
