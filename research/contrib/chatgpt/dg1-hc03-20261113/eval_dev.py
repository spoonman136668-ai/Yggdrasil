"""DG1-HC03 frozen, source-only physical DEV test. Not protected science.

The hidden action physics and synthetic regime labels remain entirely here,
outside CausalProgramSociety. One continuous physical state per seed.
"""
from __future__ import annotations

import hashlib
import json
import random
import subprocess
import time
import tracemalloc
from pathlib import Path

from model import CausalProgramSociety, canonical, MAX_CHECKPOINT_BYTES, parity_context

IN_FAMILY = tuple(range(12101, 12109))
OUT_OF_FAMILY = tuple(range(12109, 12113))
PHASE_LENGTHS = (16, 8, 1)
ACTION_BUDGET = sum(PHASE_LENGTHS)


class EvaluatorOnlyWorld:
    def __init__(self, seed, *, negative=False):
        if type(seed) is not int:
            raise ValueError("INVALID_EVALUATOR_SEED")
        self.signs = tuple(random.Random(seed * 101 + action * 17).randrange(2)
                           for action in range(4))
        self.negative = negative

    def step(self, state, action, phase=0):
        offset = self.signs[action] ^ (int(phase == 1))
        effect = parity_context(state, action) ^ offset
        if self.negative:
            # Own-bit dependence cannot be represented by the learner.
            effect ^= (state >> action) & 1
        return state ^ (effect << action)


class LatestPublicLookup:
    def __init__(self):
        self.history = {}

    def observe(self, before, action, after):
        self.history[(before, action)] = after

    def predict(self, before, action):
        return self.history.get((before, action))


class LabelledSymbolicUpperBound:
    """Strong, unfair two-regime comparator: phase A/B labels supplied by harness."""

    def __init__(self):
        self.banks = (CausalProgramSociety(bank_limit=1, reactivate=False),
                      CausalProgramSociety(bank_limit=1, reactivate=False))

    def observe(self, before, action, after, phase):
        self.banks[int(phase == 1)].observe(before, action, after)

    def predict(self, before, action):
        return self.banks[0].predict(before, action)


def audit(model, world, observed, phase=0):
    correct = wrong = abstained = unseen_correct = unseen_wrong = unseen_abstained = 0
    for state in range(16):
        for action in range(4):
            expected = world.step(state, action, phase)
            prediction = model.predict(state, action)
            is_unseen = (state, action) not in observed
            if prediction is None:
                abstained += 1
                if is_unseen:
                    unseen_abstained += 1
            elif prediction == expected:
                correct += 1
                if is_unseen:
                    unseen_correct += 1
            else:
                wrong += 1
                if is_unseen:
                    unseen_wrong += 1
    return {
        "correct": correct, "wrong_confident": wrong, "abstained": abstained,
        "unseen_correct": unseen_correct,
        "unseen_wrong_confident": unseen_wrong,
        "unseen_abstained": unseen_abstained,
        "unseen_total": unseen_correct + unseen_wrong + unseen_abstained,
    }


def one_world(seed, negative=False):
    world = EvaluatorOnlyWorld(seed, negative=negative)
    candidate = CausalProgramSociety()
    single_reset = CausalProgramSociety(bank_limit=1, reactivate=False)
    no_reactivation = CausalProgramSociety(bank_limit=2, reactivate=False)
    lookup = LatestPublicLookup()
    labelled_upper = LabelledSymbolicUpperBound()
    state = seed % 16
    observed = set()
    ledger = []
    lengths = (16,) if negative else PHASE_LENGTHS
    step_index = 0
    t0 = time.perf_counter()
    for phase, phase_length in enumerate(lengths):
        for _ in range(phase_length):
            action = step_index % 4
            before = state
            after = world.step(before, action, phase)
            assert after in (before, before ^ (1 << action))
            for m in (candidate, single_reset, no_reactivation):
                m.observe(before, action, after)
            lookup.observe(before, action, after)
            if not negative:
                labelled_upper.observe(before, action, after, phase)
            ledger.append((before, action, after))
            observed.add((before, action))
            state = after
            step_index += 1
    fit_ms = round((time.perf_counter() - t0) * 1000, 5)
    cp = candidate.snapshot()
    restored = CausalProgramSociety.restore(cp)
    assert restored.snapshot() == cp
    assert candidate.updates == step_index
    assert len(candidate.banks) <= 2
    assert candidate.logical_rule_bits == 16
    assert len(cp) <= MAX_CHECKPOINT_BYTES
    assert all(candidate.predict(s, a) == restored.predict(s, a)
               for s in range(16) for a in range(4))
    report = {
        "seed": seed, "family": "out_of_family" if negative else "in_family",
        "source_actions": step_index,
        "distinct_observed_pairs": len(observed),
        "candidate": audit(candidate, world, observed, phase=0),
        "single_reset": audit(single_reset, world, observed, phase=0),
        "no_reactivation": audit(no_reactivation, world, observed, phase=0),
        "same_ledger_lookup": audit(lookup, world, observed, phase=0),
        "labelled_upper_bound": (
            audit(labelled_upper, world, observed, phase=0) if not negative else None
        ),
        "bank_count": len(candidate.banks),
        "reactivations": candidate.reactivations,
        "splits": candidate.splits,
        "unresolved": candidate.unresolved,
        "logical_rule_bits": candidate.logical_rule_bits,
        "checkpoint_bytes": len(cp),
        "cold_parity": True,
        "ledger_sha256": hashlib.sha256(canonical(ledger)).hexdigest(),
        "fit_ms": fit_ms,
    }
    return report


def main():
    tracemalloc.start()
    worlds = [one_world(s) for s in IN_FAMILY]
    negatives = [one_world(s, negative=True) for s in OUT_OF_FAMILY]
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    mean = lambda name: sum(w[name]["correct"] for w in worlds) / (64 * len(worlds))
    candidate_mean = mean("candidate")
    single_mean = mean("single_reset")
    good = all(
        w["candidate"]["correct"] >= 60 and
        w["candidate"]["wrong_confident"] == 0 and
        w["cold_parity"] and w["source_actions"] == ACTION_BUDGET and
        w["reactivations"] >= 1
        for w in worlds
    ) and candidate_mean >= single_mean + 0.40
    negative_wrong = sum(w["candidate"]["wrong_confident"] for w in negatives)
    result = {
        "schema": "yggdrasil.dg1-hc03.dev-evidence.v1",
        "dev_classification": (
            "IN_FAMILY_DEV_SIGNAL_NOT_SCIENCE" if good else "NEGATIVE_DEV"
        ),
        "out_of_family_classification": (
            "CONFIDENT_ERRORS_OBSERVED_UNSAFE" if negative_wrong else
            "NO_ERRORS_IN_SMALL_NEGATIVE_COHORT_NOT_SAFETY_PROOF"
        ),
        "scientific_acceptance": "UNVERIFIED",
        "zero_gradient": True, "test_only": True,
        "total_in_family_charged_actions": len(worlds) * ACTION_BUDGET,
        "total_negative_charged_actions": len(negatives) * 16,
        "mean_candidate_exact_accuracy": round(candidate_mean, 6),
        "mean_single_reset_exact_accuracy": round(single_mean, 6),
        "mean_lookup_exact_accuracy": round(mean("same_ledger_lookup"), 6),
        "mean_no_reactivation_exact_accuracy": round(mean("no_reactivation"), 6),
        "mean_oracle_labelled_upper_exact_accuracy": round(mean("labelled_upper_bound"), 6),
        "out_of_family_confident_errors": negative_wrong,
        "peak_python_traced_bytes": peak,
        "worlds": worlds + negatives,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
