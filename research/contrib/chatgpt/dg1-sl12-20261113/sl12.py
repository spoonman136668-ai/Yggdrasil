"""DG1-SL12 genuine archived causal-program retrieval versus switch suppression.

Preregistered at 33f6cf977890033fa71398006d52a9808ce2e109 before this
implementation or any outcome. Physical input only: state, charged action,
observed consequence; hidden program/phase never enters learners.
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
FREEZE = "33f6cf977890033fa71398006d52a9808ce2e109"
PARENT = "6ff9e5b4866b0f502bd1f968d6009e84493f84bd"
SCHEMA = "ygg.dg1-sl12.physical-archive-retrieval.v1"
COHORTS = {
    "ABAB": tuple(range(105001, 105009)),
    "ABAA": tuple(range(105009, 105017)),
    "ABAC": tuple(range(105017, 105025)),
    "STABLE": tuple(range(105025, 105033)),
}
ARMS = (
    "archive_probe", "no_archive_on_probe", "sl11_on_probe",
    "noepisodic_on_probe", "bayes_on_probe", "archive_passive",
)
MATCHED = ARMS[:5]
AUDITS = (40, 44, 56, 60, 64, 72, 80)
COLD = (37, 57, 73)


def load_prior():
    spec = importlib.util.spec_from_file_location(
        "sl12_frozen_sl11", HERE.parent / "dg1-sl11-20261113/sl11.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sl11 = load_prior()
sl10 = sl11.sl10
sl09 = sl11.sl09
FLIPS = sl11.FLIPS


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


def checksum(x):
    return hashlib.sha256(canonical(x)).hexdigest()


class World(sl11.World):
    """Same public physics, fresh frozen seeds, private A-B-A-B switch times."""
    def __init__(self, seed, cohort):
        if cohort not in COHORTS or seed not in COHORTS[cohort]:
            raise ValueError("SL12_UNREGISTERED_WORLD")
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
            self._programs[("C", action)] = (
                (0, 1, 2)[rng.randrange(3)],
                (3, 4, 5)[rng.randrange(3)],
                rng.randrange(6),
            )

    def _phase(self, step):
        if self._cohort == "STABLE":
            return "A"
        if step < 20:
            return "A"
        if step < 40:
            return "B"
        if step < 60:
            return "A"
        if self._cohort == "ABAB":
            return "B"
        if self._cohort == "ABAC":
            return "C"
        return "A"

    def step(self, state, step, choice=None):
        sl09.check_state(state)
        if type(step) is not int or step != self.paid or step >= 80:
            raise ValueError("SL12_UNPAID_OR_REPLAYED_STEP")
        if step in FLIPS:
            if choice is not None:
                raise ValueError("SL12_CANNOT_OVERRIDE_PAID_FLIP")
            kind, action = "flip", (step // 8) % 4
            following = state ^ (1 << action)
        else:
            kind = "causal"
            if step < 40:
                if choice is not None:
                    raise ValueError("SL12_FORBIDDEN_PRE40_CHOICE")
                action = step % 4
            else:
                sl09.check_action(choice)
                action = choice
            bit = sl09.flip(
                self._programs[(self._phase(step), action)],
                state, action,
            )
            following = state ^ (bit << action)
        self.paid += 1
        return kind, action, following

    def audit_truth(self, state, action, completed):
        """Strict evaluator-only truth for the predeclared SL12 audit steps.

        The frozen SL09 evaluator permits only its own four audit times.
        SL12 preregistered earlier phase-return audits at 40/44/56.
        Physics and learner inputs are unchanged; this is never a training API.
        """
        if type(completed) is not int or completed not in AUDITS:
            raise ValueError("SL12_FORBIDDEN_EVALUATOR_AUDIT")
        sl09.check_state(state)
        sl09.check_action(action)
        bit = sl09.flip(
            self._programs[(self._phase(completed - 1), action)],
            state, action,
        )
        return state ^ (bit << action)


class ArchiveMemory:
    """Reactivation distinguished from creating a new physical memory bank."""
    def __init__(self, allow_archive=True):
        if type(allow_archive) is not bool:
            raise ValueError("SL12_BAD_ABLATION")
        self.model = sl09.Agent("candidate_compositional_episodic")
        self.allow_archive = allow_archive
        self.witness = []
        self.birth = [1]  # causal observation index when bank first usable
        self.transitions = []  # physical causal count only; no hidden labels

    @property
    def causal_events(self):
        return self.model.causal_events

    def predict(self, state, action):
        return self.model.predict(state, action)

    def observe(self, before, action, after):
        sl09.check_state(before)
        sl09.check_action(action)
        sl09.check_state(after)
        if after not in (before, before ^ (1 << action)):
            raise ValueError("SL12_NONLOCAL_PHYSICAL_CONSEQUENCE")
        if self.causal_events >= 70:
            raise ValueError("SL12_PHYSICAL_CAPACITY")
        model = self.model
        bit = int(before != after)
        miss = int(model.predict(before, action) != after)
        self.witness.append([before, action, bit, miss])
        self.witness = self.witness[-4:]
        if (len(self.witness) == 4 and
            len({(s, a) for s, a, _, _ in self.witness}) >= 3 and
            sum(w for _, _, _, w in self.witness) >= 3 and
            len(model.banks[model.active]) >= 8):
            active = model.active
            active_hits = sum(
                model._predict_in_bank(active, s, a) == b
                for s, a, b, _ in self.witness
            )
            archived = []
            if self.allow_archive:
                archived = [
                    (sum(model._predict_in_bank(i, s, a) == b
                         for s, a, b, _ in self.witness), -i, i)
                    for i in range(len(model.banks))
                    if i != active and len(model.banks[i]) >= 8
                ]
            best_hits, _, best_id = max(archived, default=(-1, 0, -1))
            next_index = -1
            reused = False
            if best_hits >= 3 and best_hits >= active_hits + 2:
                next_index, reused = best_id, True
            elif (sum(z[3] for z in self.witness) == 4 and
                  len(model.banks) < 3):
                next_index = len(model.banks)
                model.banks.append([])
                self.birth.append(self.causal_events + 1)
            if next_index >= 0:
                model.active = next_index
                model.switches += 1
                self.transitions.append([
                    self.causal_events + 1, active, next_index,
                    int(reused),
                ])
                self.witness = []
        model.banks[model.active].append([before, action, bit])
        model.causal_events += 1

    def rest(self):
        self.model.rest()

    def snapshot(self):
        payload = {
            "schema": SCHEMA,
            "inner": self.model.snapshot().decode("ascii"),
            "allow_archive": self.allow_archive,
            "witness": self.witness,
            "birth": self.birth,
            "transitions": self.transitions,
        }
        raw = canonical({"payload": payload, "sha256": checksum(payload)})
        if len(raw) > 8192:
            raise ValueError("SL12_TOO_MUCH_MEMORY")
        return raw

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= 8192:
                raise ValueError("SL12_BAD_SNAPSHOT_SIZE")
            w = json.loads(raw)
            if type(w) is not dict or set(w) != {"payload", "sha256"}:
                raise ValueError("SL12_BAD_SNAPSHOT_WRAPPER")
            p = w["payload"]
            if (type(p) is not dict or set(p) != {
                "schema", "inner", "allow_archive", "witness",
                "birth", "transitions",
            } or p["schema"] != SCHEMA or
                type(p["inner"]) is not str or
                type(p["allow_archive"]) is not bool or
                checksum(p) != w["sha256"]):
                raise ValueError("SL12_BAD_SNAPSHOT_FORMAT")
            model = sl09.Agent.restore(p["inner"].encode("ascii"))
            if model.arm != "candidate_compositional_episodic":
                raise ValueError("SL12_BAD_INNER_MODE")
            window, birth, moves = (p[k] for k in
                                    ("witness", "birth", "transitions"))
            if (type(window) is not list or len(window) > 4 or
                type(birth) is not list or
                len(birth) != len(model.banks) or
                birth[0] != 1 or type(moves) is not list or
                len(moves) > 70):
                raise ValueError("SL12_BAD_MEMORY_COUNTS")
            for e in window:
                if type(e) is not list or len(e) != 4:
                    raise ValueError("SL12_BAD_WITNESS")
                sl09.check_state(e[0]); sl09.check_action(e[1])
                if any(type(z) is not int or z not in (0, 1)
                       for z in e[2:]):
                    raise ValueError("SL12_BAD_WITNESS_VALUES")
            if any(type(n) is not int or not 1 <= n <=
                   max(1, model.causal_events + 1) for n in birth):
                raise ValueError("SL12_BAD_BIRTH")
            previous = 0
            for e in moves:
                if (type(e) is not list or len(e) != 4 or
                    any(type(n) is not int for n in e) or
                    not previous < e[0] <= model.causal_events or
                    e[1] < 0 or e[1] >= len(birth) or
                    e[2] < 0 or e[2] >= len(birth) or
                    e[1] == e[2] or e[3] not in (0, 1) or
                    (not p["allow_archive"] and e[3] != 0)):
                    raise ValueError("SL12_BAD_SWITCH_HISTORY")
                previous = e[0]
            out = cls(p["allow_archive"])
            out.model, out.witness = model, window
            out.birth, out.transitions = birth, moves
            if out.snapshot() != raw:
                raise ValueError("SL12_NONCANONICAL")
            return out
        except (ValueError, TypeError, KeyError, UnicodeError,
                OverflowError) as exc:
            raise ValueError("SL12_INVALID_CHECKPOINT") from exc


def learner(arm):
    if arm in ("archive_probe", "archive_passive"):
        return ArchiveMemory(True)
    if arm == "no_archive_on_probe":
        return ArchiveMemory(False)
    if arm == "sl11_on_probe":
        return sl11.EvidenceGated()
    if arm == "noepisodic_on_probe":
        return sl09.Agent("candidate_no_episodic")
    if arm == "bayes_on_probe":
        return sl10.ExactBayes()
    raise ValueError("SL12_UNKNOWN_ARM")


def restore(x, raw):
    if isinstance(x, ArchiveMemory):
        return ArchiveMemory.restore(raw)
    if isinstance(x, sl11.EvidenceGated):
        return sl11.EvidenceGated.restore(raw)
    if isinstance(x, sl10.ExactBayes):
        return sl10.ExactBayes.restore(raw)
    return sl09.Agent.restore(raw)


def choose(x, state, step, policy):
    sl09.check_state(state)
    if type(step) is not int or step < 40 or step >= 80 or step in FLIPS:
        raise ValueError("SL12_UNPAID_PROBE")
    if policy == "passive":
        return step % 4
    if policy != "probe" or not isinstance(x, ArchiveMemory):
        raise ValueError("SL12_UNAUTHORIZED_PROBE")
    model = x.model
    archived = [
        i for i, bank in enumerate(model.banks)
        if i != model.active and len(bank) >= 8
    ]
    if not archived:
        return step % 4
    scores = []
    for a in range(4):
        own = model._predict_in_bank(model.active, state, a)
        gap = sum(model._predict_in_bank(i, state, a) != own
                  for i in archived)
        novelty = int(not any(s == state and j == a
                              for s, j, _ in model.banks[model.active]))
        scores.append(4 * gap + novelty)
    return max(range(4), key=lambda a: (scores[a], -((a-step) % 4)))


def audit(x, world, seen, completed):
    tally = {k: 0 for k in (
        "correct", "wrong_confident", "abstained",
        "unseen_correct", "unseen_wrong_confident", "unseen_abstained",
    )}
    for state in range(16):
        for action in range(4):
            truth = world.audit_truth(state, action, completed)
            got = x.predict(state, action)
            key = ("abstained" if got is None else
                   "correct" if got == truth else "wrong_confident")
            tally[key] += 1
            if (state, action) not in seen:
                tally["unseen_" + key] += 1
    return tally


def trial(seed, cohort, arm, policy, replay_plan=None):
    if arm not in ARMS:
        raise ValueError("SL12_BAD_ARM")
    if replay_plan is not None and (
        type(replay_plan) is not list or len(replay_plan) != 80):
        raise ValueError("SL12_BAD_REPLAY_PLAN")
    world, x = World(seed, cohort), learner(arm)
    state, ledger, choices, causal_paid_steps, seen = (
        seed % 16, [], [], [], set()
    )
    stages, cold_bytes, cpu_ns = {}, [], 0
    prequential = {"correct": 0, "wrong_confident": 0, "abstained": 0}
    for step in range(80):
        if step in COLD:
            snap = x.snapshot()
            y = restore(x, snap)
            if snap != y.snapshot() or any(
                x.predict(s, a) != y.predict(s, a)
                for s in range(16) for a in range(4)
            ):
                raise AssertionError("SL12_COLD_RESTORE_DIVERGED")
            x = y
            cold_bytes.append(len(snap))
        paid_choice = step >= 40 and step not in FLIPS
        t0 = time.perf_counter_ns()
        if paid_choice:
            choice = (replay_plan[step] if replay_plan is not None
                      else choose(x, state, step, policy))
            sl09.check_action(choice)
        else:
            choice = None
            if replay_plan is not None and replay_plan[step] is not None:
                raise ValueError("SL12_NONCAUSAL_REPLAY_OVERRIDE")
        cpu_ns += time.perf_counter_ns() - t0
        kind, action, nxt = world.step(state, step, choice)
        if kind == "causal":
            t0 = time.perf_counter_ns()
            got = x.predict(state, action)
            result = ("abstained" if got is None else
                      "correct" if got == nxt else "wrong_confident")
            prequential[result] += 1
            x.observe(state, action, nxt)
            cpu_ns += time.perf_counter_ns() - t0
            causal_paid_steps.append(step)
            seen.add((state, action))
        ledger.append([state, kind, action, nxt])
        choices.append(choice)
        state = nxt
        if (step+1) % 8 == 0:
            t0 = time.perf_counter_ns()
            x.rest()
            cpu_ns += time.perf_counter_ns() - t0
        if step+1 in AUDITS:
            stages[str(step+1)] = audit(x, world, seen, step+1)
    if world.paid != 80 or x.causal_events != 70 or (
        sum(q[1] == "flip" for q in ledger) != 10):
        raise AssertionError("SL12_CHARGED_BUDGET_FAIL")
    snap = x.snapshot()
    if restore(x, snap).snapshot() != snap:
        raise AssertionError("SL12_FINAL_CHECKPOINT_FAIL")
    if replay_plan is not None and choices != replay_plan:
        raise AssertionError("SL12_REPLAY_DRIFT")
    transitions = []
    if isinstance(x, ArchiveMemory):
        for index, src, dest, reused in x.transitions:
            event_step = causal_paid_steps[index-1]
            created_on = causal_paid_steps[x.birth[dest]-1]
            transitions.append({
                "at_paid_step": event_step, "from_bank": src,
                "to_bank": dest, "archived_reuse": bool(reused),
                "destination_bank_birth_paid_step": created_on,
            })
    return {
        "charged_steps": world.paid, "flips": 10,
        "causal_observations": x.causal_events,
        "trace_sha256": checksum(ledger),
        "trace_first40_sha256": checksum(ledger[:40]),
        "ledger": ledger, "action_plan": choices,
        "cold_snapshot_bytes": cold_bytes,
        "final_snapshot_bytes": len(snap),
        "final_snapshot_sha256": hashlib.sha256(snap).hexdigest(),
        "memory_transitions": transitions,
        "prequential": prequential, "audits": stages,
        "cpu_ns": cpu_ns,
    }


def one_world(seed, cohort):
    probe = trial(seed, cohort, "archive_probe", "probe")
    results = {"archive_probe": probe}
    for arm in MATCHED[1:]:
        results[arm] = trial(seed, cohort, arm, "replay",
                             probe["action_plan"])
        if results[arm]["trace_sha256"] != probe["trace_sha256"]:
            raise AssertionError("SL12_PAID_TRACE_NOT_MATCHED")
    results["archive_passive"] = trial(
        seed, cohort, "archive_passive", "passive",
    )
    if len({v["trace_first40_sha256"] for v in results.values()}) != 1:
        raise AssertionError("SL12_FIRST40_TRACE_DIVERGED")
    if any(v["charged_steps"] != 80 or v["causal_observations"] != 70
           for v in results.values()):
        raise AssertionError("SL12_INCOMPLETE_PHYSICAL_PAID_HISTORY")
    return {"seed": seed, "cohort": cohort, "arms": results}


def genuine_returns(world):
    transitions = world["arms"]["archive_probe"]["memory_transitions"]
    return {
        "A2": any(40 <= e["at_paid_step"] < 60 and
                  e["archived_reuse"] and
                  e["destination_bank_birth_paid_step"] < 20
                  for e in transitions),
        "B2": any(60 <= e["at_paid_step"] < 80 and
                  e["archived_reuse"] and
                  20 <= e["destination_bank_birth_paid_step"] < 40
                  for e in transitions),
        "falseC": any(60 <= e["at_paid_step"] < 80 and
                      e["archived_reuse"]
                      for e in transitions),
    }


def run():
    worlds = [
        one_world(seed, cohort)
        for cohort, seeds in COHORTS.items() for seed in seeds
    ]
    keys = ("correct", "wrong_confident", "abstained",
            "unseen_correct", "unseen_wrong_confident", "unseen_abstained")
    aggregates = {
        cohort: {
            arm: {
                str(t): {
                    k: sum(w["arms"][arm]["audits"][str(t)][k]
                           for w in worlds if w["cohort"] == cohort)
                    for k in keys
                }
                for t in AUDITS
            }
            for arm in ARMS
        }
        for cohort in COHORTS
    }
    a, no, old, bayes = (
        "archive_probe", "no_archive_on_probe",
        "sl11_on_probe", "bayes_on_probe",
    )
    abab, abac, abaa, stable = (aggregates[k] for k in
                                ("ABAB", "ABAC", "ABAA", "STABLE"))
    at = lambda cohort, arm, step, key: cohort[arm][str(step)][key]
    med_cpu = statistics.median([
        w["arms"][a]["cpu_ns"] /
        max(1, w["arms"][no]["cpu_ns"])
        for w in worlds
    ])
    returns = {
        "ABAB_A2_worlds": sum(genuine_returns(w)["A2"] for w in worlds
                             if w["cohort"] == "ABAB"),
        "ABAB_B2_worlds": sum(genuine_returns(w)["B2"] for w in worlds
                             if w["cohort"] == "ABAB"),
        "ABAC_falseC_worlds": sum(genuine_returns(w)["falseC"] for w in worlds
                                 if w["cohort"] == "ABAC"),
    }
    gates = {
        "physical_retrieval_A2": returns["ABAB_A2_worlds"] >= 3,
        "physical_retrieval_B2": returns["ABAB_B2_worlds"] >= 3,
        "A2_60_correct_vs_no_archive":
            at(abab, a, 60, "correct") >=
            at(abab, no, 60, "correct") + 8,
        "B2_80_correct_vs_no_archive":
            at(abab, a, 80, "correct") >=
            at(abab, no, 80, "correct") + 12,
        "B2_80_unseen_vs_no_archive":
            at(abab, a, 80, "unseen_correct") >=
            at(abab, no, 80, "unseen_correct") + 6,
        "B2_80_correct_vs_SL11":
            at(abab, a, 80, "correct") >=
            at(abab, old, 80, "correct") + 8,
        "B2_80_correct_vs_Bayesian":
            at(abab, a, 80, "correct") >=
            at(abab, bayes, 80, "correct") + 8,
        "B2_80_unseen_vs_Bayesian":
            at(abab, a, 80, "unseen_correct") >=
            at(abab, bayes, 80, "unseen_correct") + 4,
        "B2_64_early_correct_vs_no_archive":
            at(abab, a, 64, "correct") >=
            at(abab, no, 64, "correct") + 8,
        "C_new_context_false_retrieval":
            returns["ABAC_falseC_worlds"] <= 2,
        "C_new_context_correct_loss":
            at(abac, a, 80, "correct") >=
            at(abac, no, 80, "correct") - 8,
        "ABAA_correct_nonregression":
            at(abaa, a, 80, "correct") >=
            at(abaa, no, 80, "correct") - 8,
        "STABLE_correct_nonregression":
            at(stable, a, 80, "correct") >=
            at(stable, no, 80, "correct") - 8,
        "STABLE_confident_error_nonregression":
            at(stable, a, 80, "wrong_confident") <=
            at(stable, no, 80, "wrong_confident") + 8,
        "cpu_ratio_vs_no_archive": med_cpu <= 2.5,
    }
    total = sum(v["charged_steps"] for w in worlds
                for v in w["arms"].values())
    causal = sum(v["causal_observations"] for w in worlds
                 for v in w["arms"].values())
    if (len(worlds) != 32 or total != 15360 or causal != 13440 or
        any(len(v["cold_snapshot_bytes"]) != 3 or
            max(v["cold_snapshot_bytes"] +
                [v["final_snapshot_bytes"]]) > 8192 or
            v["flips"] != 10
            for w in worlds for v in w["arms"].values())):
        raise AssertionError("SL12_FROZEN_PHYSICAL_CUSTODY_INVALID")
    mixed = (
        at(abab, a, 80, "correct") >
        at(abab, no, 80, "correct") or
        at(abab, a, 80, "unseen_correct") >
        at(abab, no, 80, "unseen_correct") or
        returns["ABAB_A2_worlds"] > 0 or
        returns["ABAB_B2_worlds"] > 0
    )
    return {
        "schema": SCHEMA, "freeze_sha": FREEZE, "parent_sha": PARENT,
        "world_count": len(worlds), "arms": list(ARMS),
        "primary_pass": all(gates.values()),
        "classification": ("DEV_SIGNAL_NOT_SCIENCE" if all(gates.values())
                           else "MIXED_DEV" if mixed else "NEGATIVE_DEV"),
        "scientific_acceptance": "UNVERIFIED",
        "model_integration": False,
        "charged_steps": total, "charged_flips": total-causal,
        "paid_causal_observations": causal,
        "matched_information_within_probe_replay_arms": True,
        "passive_information_different": True,
        "reused_archived_context_worlds": returns,
        "primary_gates": gates,
        "median_candidate_cpu_ratio_vs_no_archive": med_cpu,
        "aggregates": aggregates, "worlds": worlds,
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, separators=(",", ":")))
