"""DG1-SL11 frozen physical-witness context retrieval (synthetic DEV).

Preregistration 2717821accf3c22140b58859d7c8bc8c9fd5a2de precedes
implementation, decisions, and all prospective results.
No hidden rule, seed, phase label or evaluator audit is given to any learner.
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
FREEZE = "2717821accf3c22140b58859d7c8bc8c9fd5a2de"
PARENT = "40b5e879eea5c78cf84662bec116952dfdceab48"
SCHEMA = "ygg.dg1-sl11.physical-witness-context-retrieval.v1"
COHORTS = {
    "RETURN_A": tuple(range(104001, 104009)),
    "RETURN_B": tuple(range(104009, 104017)),
    "STABLE": tuple(range(104017, 104025)),
    "COMPOSITION_OOD": tuple(range(104025, 104033)),
}
ARMS = (
    "gated_active",
    "original_on_gated",
    "noepisodic_on_gated",
    "bayes_on_gated",
    "original_active",
    "gated_on_original",
    "gated_passive",
    "original_on_passive",
)
GROUPS = (
    ("gated_active", "original_on_gated", "noepisodic_on_gated",
     "bayes_on_gated"),
    ("original_active", "gated_on_original"),
    ("gated_passive", "original_on_passive"),
)


def load_frozen():
    spec = importlib.util.spec_from_file_location(
        "sl11_frozen_sl10", HERE.parent / "dg1-sl10-20261113/sl10.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sl10 = load_frozen()
sl09 = sl10.sl09
FLIPS = sl10.FLIPS
AUDITS = sl10.AUDITS


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def sha256_object(obj):
    return sha256_bytes(canonical(obj))


class World(sl10.World):
    """Exact frozen SL10 physics with prospectively new nonoverlapping seeds."""
    def __init__(self, seed, cohort):
        if cohort not in COHORTS or seed not in COHORTS[cohort]:
            raise ValueError("SL11_UNREGISTERED_WORLD")
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


class EvidenceGated:
    """Bounded causal witness gate around the unchanged episodic rule learner.

    Observe exactly one actually paid physical before/action/after consequence.
    No virtual evidence, no post-result correction, no external phase clock.
    """
    def __init__(self):
        self.model = sl09.Agent("candidate_compositional_episodic")
        self.witness = []

    @property
    def causal_events(self):
        return self.model.causal_events

    @property
    def switches(self):
        return self.model.switches

    def predict(self, state, action):
        return self.model.predict(state, action)

    def observe(self, before, action, after):
        sl09.check_state(before)
        sl09.check_action(action)
        sl09.check_state(after)
        if after not in (before, before ^ (1 << action)):
            raise ValueError("SL11_NONLOCAL_PHYSICAL_EVENT")
        if self.causal_events >= 70:
            raise ValueError("SL11_PHYSICAL_OBSERVATION_LIMIT")
        model = self.model
        observed = int(before != after)
        predicted = model.predict(before, action)
        wrong = int(predicted is not None and predicted != after)
        event = [before, action, observed]
        self.witness.append([before, action, observed, wrong])
        self.witness = self.witness[-6:]
        if (len(self.witness) >= 6 and
            len({(s, a) for s, a, _, _ in self.witness}) >= 3 and
            sum(wrongbit for _, _, _, wrongbit in self.witness) >= 4 and
            len(model.banks[model.active]) >= 12):
            active_index = model.active
            active_hits = sum(
                model._predict_in_bank(active_index, s, a) == bit
                for s, a, bit, _ in self.witness)
            alternatives = [
                (sum(model._predict_in_bank(i, s, a) == bit
                     for s, a, bit, _ in self.witness), i)
                for i in range(len(model.banks)) if i != active_index
            ]
            best_hits, best_index = max(alternatives, default=(-1, -1))
            if best_hits >= 4 and best_hits >= active_hits + 2:
                model.active = best_index
                model.switches += 1
                self.witness = []
            elif sum(q[3] for q in self.witness) >= 5 and (
                    len(model.banks) < 3):
                model.banks.append([])
                model.active = len(model.banks) - 1
                model.switches += 1
                self.witness = []
        model.banks[model.active].append(event)
        model.causal_events += 1

    def rest(self):
        self.model.rest()

    def snapshot(self):
        inner = self.model.snapshot().decode("ascii")
        payload = {
            "schema": SCHEMA,
            "inner": inner,
            "witness": self.witness,
        }
        raw = canonical({
            "payload": payload,
            "sha256": sha256_object(payload),
        })
        if len(raw) > 8192:
            raise ValueError("SL11_CHECKPOINT_CAPACITY")
        return raw

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= 8192:
                raise ValueError("SL11_BAD_CHECKPOINT_BYTES")
            wrap = json.loads(raw)
            if type(wrap) is not dict or set(wrap) != {"payload", "sha256"}:
                raise ValueError("SL11_BAD_WRAPPER")
            p = wrap["payload"]
            if (type(p) is not dict or
                set(p) != {"schema", "inner", "witness"} or
                p["schema"] != SCHEMA or type(p["inner"]) is not str or
                sha256_object(p) != wrap["sha256"]):
                raise ValueError("SL11_INVALID_CHECKPOINT_SCHEMA")
            witness = p["witness"]
            if type(witness) is not list or len(witness) > 6:
                raise ValueError("SL11_BAD_WITNESS_WINDOW")
            for e in witness:
                if type(e) is not list or len(e) != 4:
                    raise ValueError("SL11_BAD_WITNESS_ENTRY")
                sl09.check_state(e[0])
                sl09.check_action(e[1])
                if any(type(v) is not int or v not in (0, 1)
                       for v in e[2:]):
                    raise ValueError("SL11_BAD_WITNESS_BIT")
            model = sl09.Agent.restore(p["inner"].encode("ascii"))
            if model.arm != "candidate_compositional_episodic":
                raise ValueError("SL11_INNER_MODE_MISMATCH")
            if len(witness) > model.causal_events:
                raise ValueError("SL11_INCONSISTENT_WITNESS")
            out = cls()
            out.model = model
            out.witness = witness
            if out.snapshot() != raw:
                raise ValueError("SL11_NONCANONICAL")
            return out
        except (ValueError, TypeError, KeyError,
                OverflowError, UnicodeError) as exc:
            raise ValueError("SL11_INVALID_CHECKPOINT") from exc


def learner(arm):
    if arm not in ARMS:
        raise ValueError("SL11_UNKNOWN_ARM")
    if arm.startswith("gated_"):
        return EvidenceGated()
    if arm in ("original_active", "original_on_gated",
               "original_on_passive"):
        return sl09.Agent("candidate_compositional_episodic")
    if arm == "noepisodic_on_gated":
        return sl09.Agent("candidate_no_episodic")
    if arm == "bayes_on_gated":
        return sl10.ExactBayes()
    raise ValueError("SL11_UNREACHABLE_ARM")


def cold_restore(x, raw):
    if isinstance(x, EvidenceGated):
        return EvidenceGated.restore(raw)
    if isinstance(x, sl10.ExactBayes):
        return sl10.ExactBayes.restore(raw)
    return sl09.Agent.restore(raw)


def choose(x, state, step, policy):
    if policy == "passive":
        return step % 4
    if policy == "gated":
        if not isinstance(x, EvidenceGated):
            raise ValueError("SL11_EXPECTED_GATED_SELECTOR")
        return sl10.candidate_choose(x.model, state, step)
    if policy == "original":
        if not isinstance(x, sl09.Agent):
            raise ValueError("SL11_EXPECTED_FROZEN_SELECTOR")
        return sl10.candidate_choose(x, state, step)
    raise ValueError("SL11_UNKNOWN_SELECTION_POLICY")


def trial(seed, cohort, arm, policy, replay_plan=None):
    if arm not in ARMS:
        raise ValueError("SL11_UNKNOWN_ARM")
    if replay_plan is not None and (
        type(replay_plan) is not list or len(replay_plan) != 80):
        raise ValueError("SL11_INVALID_REPLAY_PLAN")
    world, x = World(seed, cohort), learner(arm)
    state, seen, ledger, plan = seed % 16, set(), [], []
    prequential = {"correct": 0, "wrong_confident": 0, "abstained": 0}
    after_cold = {"correct": 0, "wrong_confident": 0, "abstained": 0}
    stages, cold_bytes, cpu_ns, nonpassive = {}, 0, 0, 0
    for step in range(80):
        if step == 60:
            snap = x.snapshot()
            restored = cold_restore(x, snap)
            if snap != restored.snapshot() or any(
                x.predict(s, a) != restored.predict(s, a)
                for s in range(16) for a in range(4)
            ):
                raise AssertionError("SL11_COLD_RESTORE_DIVERGENCE")
            x = restored
            cold_bytes = len(snap)
        active = step >= 60 and step not in FLIPS
        start = time.perf_counter_ns()
        if active:
            selected = (replay_plan[step] if replay_plan is not None
                        else choose(x, state, step, policy))
            sl09.check_action(selected)
            nonpassive += int(selected != step % 4)
        else:
            selected = None
            if replay_plan is not None and replay_plan[step] is not None:
                raise ValueError("SL11_UNPAID_REPLAY_ACTION")
        cpu_ns += time.perf_counter_ns() - start
        kind, action, nxt = world.step(state, step, selected)
        if kind == "causal":
            start = time.perf_counter_ns()
            pred = x.predict(state, action)
            verdict = ("abstained" if pred is None else
                       "correct" if pred == nxt else "wrong_confident")
            prequential[verdict] += 1
            if step >= 60:
                after_cold[verdict] += 1
            x.observe(state, action, nxt)
            cpu_ns += time.perf_counter_ns() - start
            seen.add((state, action))
        ledger.append([state, kind, action, nxt])
        plan.append(selected)
        state = nxt
        if (step + 1) % 8 == 0:
            start = time.perf_counter_ns()
            x.rest()
            cpu_ns += time.perf_counter_ns() - start
        if step + 1 in AUDITS:
            stages[str(step + 1)] = sl09.audit(x, world, seen, step + 1)
    if world.paid != 80 or x.causal_events != 70 or (
        sum(e[1] == "flip" for e in ledger) != 10):
        raise AssertionError("SL11_PHYSICAL_BUDGET_FAILURE")
    final_snapshot = x.snapshot()
    if cold_restore(x, final_snapshot).snapshot() != final_snapshot:
        raise AssertionError("SL11_FINAL_COLD_FAILURE")
    if replay_plan is not None and plan != replay_plan:
        raise AssertionError("SL11_REPLAY_MISMATCH")
    return {
        "charged_steps": world.paid,
        "flips": 10,
        "paid_causal_observations": x.causal_events,
        "pre_cold_trace_sha256": sha256_object(ledger[:60]),
        "complete_trace_sha256": sha256_object(ledger),
        "paid_ledger": ledger,
        "action_plan": plan,
        "cold_checkpoint_bytes": cold_bytes,
        "final_checkpoint_bytes": len(final_snapshot),
        "final_checkpoint_sha256": sha256_bytes(final_snapshot),
        "prequential": prequential,
        "after_cold_prequential": after_cold,
        "stage_audits": stages,
        "nonpassive_chosen_after_cold": nonpassive,
        "memory_switches": x.switches,
        "cpu_ns": cpu_ns,
    }


def one_world(seed, cohort):
    output = {}
    policies = {
        "gated_active": "gated",
        "original_active": "original",
        "gated_passive": "passive",
    }
    for group in GROUPS:
        pilot = group[0]
        output[pilot] = trial(seed, cohort, pilot, policies[pilot])
        plan = output[pilot]["action_plan"]
        for arm in group[1:]:
            output[arm] = trial(seed, cohort, arm, "replay", plan)
        if len({output[a]["complete_trace_sha256"] for a in group}) != 1:
            raise AssertionError("SL11_REPLAY_PHYSICAL_INFORMATION_DRIFT")
    if len({x["pre_cold_trace_sha256"] for x in output.values()}) != 1:
        raise AssertionError("SL11_PRE_COLD_DRIFT")
    return {
        "seed": seed, "cohort": cohort,
        "shared_pre_cold_sha256":
            next(iter(output.values()))["pre_cold_trace_sha256"],
        "arms": output,
    }


def run():
    worlds = [
        one_world(seed, cohort)
        for cohort, seeds in COHORTS.items()
        for seed in seeds
    ]
    keys = ("correct", "wrong_confident", "abstained",
            "unseen_correct", "unseen_wrong_confident", "unseen_abstained")
    aggregate = {
        cohort: {
            arm: {
                k: sum(w["arms"][arm]["stage_audits"]["80"][k]
                       for w in worlds if w["cohort"] == cohort)
                for k in keys
            }
            for arm in ARMS
        }
        for cohort in COHORTS
    }
    x = "gated_active"
    orig, nop, bayes = "original_on_gated", "noepisodic_on_gated", "bayes_on_gated"
    o = aggregate["COMPOSITION_OOD"]
    a, b, st = (aggregate[c] for c in ("RETURN_A", "RETURN_B", "STABLE"))
    cpu_median = statistics.median([
        w["arms"][x]["cpu_ns"] /
        max(1, w["arms"][orig]["cpu_ns"])
        for w in worlds
    ])
    active_worlds = sum(
        w["arms"][x]["nonpassive_chosen_after_cold"] > 0 for w in worlds
        if w["cohort"] == "COMPOSITION_OOD")
    gates = {
        "returnB_gain_vs_original_same_trace":
            b[x]["correct"] >= b[orig]["correct"] + 16,
        "returnB_loss_vs_noepisodic_same_trace":
            b[x]["correct"] >= b[nop]["correct"] - 8,
        "stable_loss_vs_noepisodic_same_trace":
            st[x]["correct"] >= st[nop]["correct"] - 8,
        "stable_confident_error_vs_noepisodic":
            st[x]["wrong_confident"] <= st[nop]["wrong_confident"] + 8,
        "returnA_original_nonregression":
            a[x]["correct"] >= a[orig]["correct"] - 16,
        "ood_correct_gain_vs_original_same_trace":
            o[x]["correct"] >= o[orig]["correct"] + 16,
        "ood_unseen_gain_vs_original_same_trace":
            o[x]["unseen_correct"] >= o[orig]["unseen_correct"] + 8,
        "ood_unseen_vs_bayesian_same_trace":
            o[x]["unseen_correct"] >= o[bayes]["unseen_correct"] + 4,
        "ood_unseen_noepisodic_nonregression":
            o[x]["unseen_correct"] >= o[nop]["unseen_correct"] - 4,
        "ood_confident_error_vs_original":
            o[x]["wrong_confident"] <= o[orig]["wrong_confident"] + 4,
        "ood_policy_gain_vs_gated_passive":
            o[x]["correct"] >= o["gated_passive"]["correct"] + 8,
        "transport_to_original_policy_returnB":
            b["gated_on_original"]["correct"] >=
            b["original_active"]["correct"] + 8,
        "cpu_vs_original_same_trace":
            cpu_median <= 2.0,
        "nonpassive_in_ood_worlds":
            active_worlds >= 4,
    }
    paid_steps = sum(z["charged_steps"] for w in worlds
                     for z in w["arms"].values())
    causal = sum(z["paid_causal_observations"] for w in worlds
                 for z in w["arms"].values())
    if (len(worlds) != 32 or paid_steps != 20480 or causal != 17920 or
        any(z["flips"] != 10 or z["cold_checkpoint_bytes"] > 8192 or
            z["final_checkpoint_bytes"] > 8192
            for w in worlds for z in w["arms"].values())):
        raise AssertionError("SL11_FROZEN_PHYSICAL_CUSTODY_INVALID")
    mixed = (
        b[x]["correct"] > b[orig]["correct"] or
        o[x]["correct"] > o[orig]["correct"] or
        o[x]["unseen_correct"] > o[orig]["unseen_correct"]
    )
    return {
        "schema": SCHEMA, "freeze_sha": FREEZE, "parent_sha": PARENT,
        "world_count": len(worlds), "arms": list(ARMS),
        "classification": ("DEV_SIGNAL_NOT_SCIENCE" if all(gates.values())
                           else "MIXED_DEV" if mixed else "NEGATIVE_DEV"),
        "primary_pass": all(gates.values()),
        "scientific_acceptance": "UNVERIFIED",
        "model_integration": False,
        "same_physical_information_within_replay_groups": True,
        "not_same_information_between_policy_groups": True,
        "charged_steps": paid_steps,
        "paid_causal_observations": causal,
        "charged_flips": paid_steps - causal,
        "cpu_matched": False,
        "median_gated_cpu_ratio_vs_original_same_trace": cpu_median,
        "ood_worlds_nonpassive": active_worlds,
        "primary_gates": gates,
        "aggregates": aggregate, "worlds": worlds,
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, separators=(",", ":")))
