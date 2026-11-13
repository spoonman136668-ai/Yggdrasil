"""HC04 frozen public-only developer evaluation. NO original science authority.

Actual physics and regime membership are defined only here. The learner
receives no source labels, hidden signs, physics equation or oracle feedback.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import time
import tracemalloc
from pathlib import Path

from model import (
    CHECKPOINT_LIMIT, ConventionalConstraintControl, VersionedCausalCells,
    canonical, local_parity,
)

BASE = Path(__file__).resolve().parents[1]
PREDECESSOR = BASE / "dg1-hc03-20261113" / "model.py"
_spec = importlib.util.spec_from_file_location("hc03_original", PREDECESSOR)
hc03 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hc03)

PARITY_SEEDS = tuple(range(22101, 22105))
OWN_BIT_SEEDS = tuple(range(22105, 22109))
AND_SEEDS = tuple(range(22109, 22113))
BUDGET_PARITY = (16, 8, 1)
BUDGET_OTHER = (16,)


class PhysicalWorld:
    """Synthetic evaluator-only four-site local action mechanism."""
    def __init__(self, seed, family):
        if type(seed) is not int or family not in ("parity", "own_bit", "and"):
            raise ValueError("HC04_BAD_SOURCE")
        self.signs = tuple(
            random.Random(seed * 101 + action * 17).randrange(2)
            for action in range(4)
        )
        self.family = family

    def step(self, before, action, phase):
        own = (before >> action) & 1
        left = (before >> ((action - 1) % 4)) & 1
        right = (before >> ((action + 1) % 4)) & 1
        if self.family == "parity":
            effect = (left ^ right) ^ self.signs[action] ^ int(phase == 1)
        elif self.family == "own_bit":
            effect = (left ^ right) ^ own ^ self.signs[action]
        else:
            effect = (left & right) ^ self.signs[action]
        return before ^ (effect << action)


class LastObservedLookup:
    def __init__(self):
        self.history = {}

    def observe(self, before, action, after):
        self.history[(before, action)] = after

    def predict(self, before, action):
        return self.history.get((before, action))


class NoGateControl:
    def __init__(self, model):
        self.model = model

    def predict(self, before, action):
        return self.model.predict_ungated(before, action)


def audit(model, world, seen):
    correct = wrong = abstained = unseen_correct = unseen_wrong = unseen_abstained = 0
    for before in range(16):
        for action in range(4):
            predicted = model.predict(before, action)
            expected = world.step(before, action, 0)
            unseen = (before, action) not in seen
            if predicted is None:
                abstained += 1
                if unseen:
                    unseen_abstained += 1
            elif predicted == expected:
                correct += 1
                if unseen:
                    unseen_correct += 1
            else:
                wrong += 1
                if unseen:
                    unseen_wrong += 1
    return {
        "correct": correct, "wrong_confident": wrong, "abstained": abstained,
        "unseen_correct": unseen_correct,
        "unseen_wrong_confident": unseen_wrong,
        "unseen_abstained": unseen_abstained,
        "unseen_total": unseen_correct + unseen_wrong + unseen_abstained,
    }


def one_seed(seed, family):
    world = PhysicalWorld(seed, family)
    candidate = VersionedCausalCells()
    conventional = ConventionalConstraintControl()
    single = VersionedCausalCells(bank_limit=1, reactivate=False)
    no_reactivation = VersionedCausalCells(bank_limit=2, reactivate=False)
    old_hc03 = hc03.CausalProgramSociety()
    lookup = LastObservedLookup()
    state = seed % 16
    seen = set()
    ledger = []
    n = 0
    t0 = time.perf_counter()
    durations = BUDGET_PARITY if family == "parity" else BUDGET_OTHER
    for phase, length in enumerate(durations):
        for _ in range(length):
            action = n % 4
            after = world.step(state, action, phase)
            if after not in (state, state ^ (1 << action)):
                raise RuntimeError("HC04_SOURCE_DELTA_INVALID")
            for m in (candidate, conventional, single, no_reactivation, old_hc03, lookup):
                m.observe(state, action, after)
            ledger.append((state, action, after))
            seen.add((state, action))
            state = after
            n += 1
    fit_ms = round((time.perf_counter() - t0) * 1000, 5)
    checkpoint = candidate.snapshot()
    restored = VersionedCausalCells.restore(checkpoint)
    assert restored.snapshot() == checkpoint
    assert n == (25 if family == "parity" else 16)
    assert len(checkpoint) <= CHECKPOINT_LIMIT
    assert candidate.logical_hypothesis_bits == 32
    assert len(candidate.banks) <= 2
    assert candidate.updates == n
    assert all(candidate.predict(s, a) == restored.predict(s, a)
               for s in range(16) for a in range(4))
    assert all(candidate.predict(s, a) == conventional.predict(s, a)
               for s in range(16) for a in range(4))
    return {
        "seed": seed, "family": family, "charged_source_actions": n,
        "distinct_observed_pairs": len(seen),
        "candidate": audit(candidate, world, seen),
        "conventional_equivalent": audit(conventional, world, seen),
        "single_bank": audit(single, world, seen),
        "no_reactivation": audit(no_reactivation, world, seen),
        "hc03_baseline": audit(old_hc03, world, seen),
        "same_ledger_lookup": audit(lookup, world, seen),
        "forced_ungated": audit(NoGateControl(candidate), world, seen),
        "banks_used": len(candidate.banks),
        "reactivations": candidate.reactivations,
        "ambiguous_events": candidate.ambiguous_events,
        "unresolved": candidate.unresolved,
        "logical_hypothesis_bits": candidate.logical_hypothesis_bits,
        "checkpoint_bytes": len(checkpoint),
        "cold_parity": True,
        "ledger_sha256": hashlib.sha256(canonical(ledger)).hexdigest(),
        "fit_ms": fit_ms,
    }


def run():
    tracemalloc.start()
    results = (
        [one_seed(s, "parity") for s in PARITY_SEEDS] +
        [one_seed(s, "own_bit") for s in OWN_BIT_SEEDS] +
        [one_seed(s, "and") for s in AND_SEEDS]
    )
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    parity, own, negative = results[:4], results[4:8], results[8:]
    parity_pass = all(
        row["candidate"]["wrong_confident"] == 0 and
        row["candidate"]["correct"] >= 16 and row["cold_parity"] and
        row["charged_source_actions"] == 25 for row in parity
    )
    own_pass = all(
        row["candidate"]["wrong_confident"] == 0 and
        row["candidate"]["correct"] >= 32 and row["cold_parity"] and
        row["charged_source_actions"] == 16 for row in own
    )
    errors_out = sum(x["candidate"]["wrong_confident"] for x in negative)
    dev = ("BOTH_IN_CLASS_DEV_SIGNAL_NOT_SCIENCE" if parity_pass and own_pass
           else "MIXED_DEV" if parity_pass != own_pass else "NEGATIVE_DEV")
    return {
        "schema": "ygg.dg1-hc04.version-space-dev-result.v1",
        "exact_parent_sha": "f26efd4c01a3344f12ba2ec9bf8582aa25b99dfa",
        "classification": dev,
        "parity_cohort_pass": parity_pass, "own_bit_cohort_pass": own_pass,
        "out_of_basis_classification": (
            "UNSAFE_CONFIDENT_ERRORS" if errors_out else
            "FINITE_NEGATIVE_COHORT_NO_SAFETY_PROOF"),
        "out_of_basis_confident_errors": errors_out,
        "scientific_acceptance": "UNVERIFIED",
        "total_charged_actions": sum(row["charged_source_actions"] for row in results),
        "peak_tracemalloc_bytes": peak,
        "no_gradient_or_model_calls": True,
        "control_equivalence_verified": all(
            row["candidate"] == row["conventional_equivalent"] for row in results),
        "worlds": results,
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
