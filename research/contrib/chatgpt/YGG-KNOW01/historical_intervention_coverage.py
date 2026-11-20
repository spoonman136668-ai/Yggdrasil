"""KNOW09: retrospective action-support and identifiability limits.

Only the already-consumed archived 1,025 public intervention events are read.
No fresh source actions, model updates, new outcomes or owner state changes.
Action overlap is necessary but not sufficient for a causal effect estimate.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from historical_functional_retention import (
    EXPECTED_WITNESSES, fingerprint, canonical)
from native_cold_shadow import JOINT_SHA, NATIVE_SHA, valid_nested, require

VIEWS = ((0, 0), (0, 1), (1, 0), (1, 1))


def _occupied(cells):
    return sum(bool(count[0] + count[1]) for count in cells)


def audit(learner, *, expected=EXPECTED_WITNESSES):
    """Count retrospective public action overlap without claiming causal ID."""
    before = fingerprint(learner, expected=expected)  # frozen schema and readout validation
    ledger = learner._episode_reader()._ledger
    require(type(ledger) is tuple and len(ledger) == expected,
            "SOURCE_LEDGER_DRIFT")
    reports = []
    # Each of the two candidate views is audited separately. Never treat the
    # paired representations of one episode as two independent interventions.
    for projection in (0, 1):
        first = {(v, x): [0, 0] for v in VIEWS for x in (0, 1)}
        second = {(v, x, s, a): [0, 0]
                  for v in VIEWS for x in (0, 1) for s in (0, 1)
                  for a in (0, 1)}
        for identifier, views, x1, s2, x2, outcome in ledger:
            view = views[projection]
            first[(view, x1)][s2] += 1
            second[(view, x1, s2, x2)][outcome] += 1
        require(sum(sum(c) for c in first.values()) == expected and
                sum(sum(c) for c in second.values()) == expected,
                "SOURCE_EPISODE_COUNT")
        first_both = sum(
            bool(sum(first[(v, 0)])) and bool(sum(first[(v, 1)]))
            for v in VIEWS)
        first_eight = sum(
            min(sum(first[(v, 0)]), sum(first[(v, 1)])) >= 8
            for v in VIEWS)
        second_both = sum(
            bool(sum(second[(v, x, s, 0)])) and
            bool(sum(second[(v, x, s, 1)]))
            for v in VIEWS for x in (0, 1) for s in (0, 1))
        second_eight = sum(
            min(sum(second[(v, x, s, 0)]),
                sum(second[(v, x, s, 1)])) >= 8
            for v in VIEWS for x in (0, 1) for s in (0, 1))
        # Mixed empirical outcomes are not necessarily contradictions; the
        # actual DTR source can be stochastic and/or partly confounded.
        reports.append({
            "projection": projection,
            "witnesses": expected,
            "first_action_cells_observed_of_8": _occupied(first.values()),
            "first_view_contexts_with_both_actions_of_4": first_both,
            "first_view_contexts_with_8_each_action_of_4": first_eight,
            "first_cells_with_both_outcomes": sum(
                c[0] > 0 and c[1] > 0 for c in first.values()),
            "terminal_action_cells_observed_of_32": _occupied(second.values()),
            "terminal_public_prefixes_with_both_actions_of_16": second_both,
            "terminal_public_prefixes_with_8_each_action_of_16": second_eight,
            "terminal_cells_with_both_outcomes": sum(
                c[0] > 0 and c[1] > 0 for c in second.values()),
        })
    after = fingerprint(learner, expected=expected)
    require(before == after, "RETROSPECTIVE_READOUT_DRIFT")
    # Aggregates only. Do not publish the historical ledger, event IDs,
    # individual predictions, private source labels or unfiltered metadata.
    return {
        "schema": "yggdrasil.know09.retrospective-public-action-coverage.v1",
        "classification": "ALREADY_CONSUMED_HISTORY_DESCRIPTIVE_ONLY",
        "native_witnesses": expected,
        "candidate_view_projections": 2,
        "old_retrospective_readout_sha256": before["retrospective_readout_sha256"],
        "readouts_unchanged": True,
        "reports": reports,
        "historical_witnesses_independent_per_projection": expected,
        "new_source_actions": 0,
        "new_training": 0,
        "disjoint_scientific_evaluation": False,
        "randomized_treatment_assignment_verified": False,
        "causal_effect_identified": False,
        "counterfactual_per_unit_observed": False,
        "scientific_pass": False,
        "owner_accepted_canonical_checkpoint": "UNVERIFIED",
        "deployment": "NONE",
    }


def prove(joint_checkpoint):
    from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
    path = Path(joint_checkpoint)
    require(path.is_file() and not path.is_symlink() and
            0 < path.stat().st_size <= 32 * 1024 * 1024,
            "HISTORICAL_ARCHIVE_PATH")
    joint = path.read_bytes()
    native_raw = valid_nested(joint, JOINT_SHA, NATIVE_SHA)
    native = NativeCumulativeLearner.restore(native_raw, NATIVE_SHA)
    require(native.checkpoint() == native_raw, "COLD_NATIVE_PIN")
    out = audit(native)
    require(native.checkpoint() == native_raw, "NO_NATIVE_MUTATION")
    out["archived_joint_sha256"] = JOINT_SHA
    out["archived_native_sha256"] = NATIVE_SHA
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--joint-checkpoint", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = prove(args.joint_checkpoint)
    args.output.write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("KNOW09_RETROSPECTIVE_ACTION_SUPPORT_PASS " + json.dumps({
        "native_witnesses": result["native_witnesses"],
        "reports": result["reports"],
        "scientific_pass": False}, sort_keys=True))


if __name__ == "__main__":
    main()
