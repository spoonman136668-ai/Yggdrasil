"""NKR-16 frozen source-safe intervention-choice experiment.

The actual environment is accessed ONLY after a model selects an action.
All direct observations are distinguished from predictions on unprobed cold
contexts. Matched random arms use identical budgets, no hidden data.

There are no authentic external intervention data here. Information theory
and an independent exact symbolic policy are the strong comparators.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from yggdrasil.native_active_intervention import (
    NativeActiveIntervention, source_bundle, COLD, SEED,
)
from yggdrasil.native_intervention_repair import digest, canonical
from yggdrasil.native_operator_discovery import NativeOperatorDiscovery
from yggdrasil.public_causal_cells import PublicCausalCells


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


nkr13 = load("nkr16_reference_nkr13", Path(__file__).resolve().parents[1]
             / "NKR-13/experiment.py")
nkr14 = load("nkr16_reference_nkr14", Path(__file__).resolve().parents[1]
             / "NKR-14/experiment.py")
nkr12 = nkr13.nkr12


def public_rows(original, *, prefix):
    return [(f"{prefix}-observation-{i:02d}", x, a, y)
            for i, (_, x, a, y) in enumerate(original)]


def pinned_source(records, prefix):
    name = prefix + "-" + digest(canonical(records))[:16]
    return source_bundle(name, records)


def independent_next(mode, policy, source_sha, round_index,
                     already, candidates):
    """Entirely independent decision code, no native planner calls."""
    unseen = sorted(set(COLD) - set(already))
    if not unseen:
        return None
    if policy == "random":
        payload = SEED + b":" + source_sha.encode("ascii") + b":" + (
            str(round_index).encode("ascii"))
        index = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
        return unseen[index % len(unseen)]
    if mode == "unrestricted":
        return unseen[0]
    best, top = None, -1
    for x in unseen:
        yes = sum(1 for m in candidates if (x & m) == m)
        no = len(candidates) - yes
        information_rank = yes * no
        if information_rank > top:
            best, top = x, information_rank
    return best


def independent_consensus(candidates, baseline, x):
    outcomes = {baseline ^ int((x & m) == m) for m in candidates}
    return next(iter(outcomes)) if len(outcomes) == 1 else None


def environment(world, mode):
    return (nkr14.HiddenWorld(world) if mode == "unrestricted"
            else nkr13.ComputationalEnvironment(world))


def env_outcome(env, mode, x, a, *, old=False):
    if mode == "unrestricted":
        return env.intervene(x, a, old=old)
    return env.intervene(x, a, old_mechanism=old)


def original_evidence(env, mode):
    warm = (nkr14.warmup(env) if mode == "unrestricted"
            else nkr13.collect_warmup(env))
    initial = (nkr14.source_visible_actions(env) if mode == "unrestricted"
               else nkr13.collect_paired_interventions(env))
    return (public_rows(warm, prefix="warm"),
            public_rows(initial, prefix="public"))


def run_one_world(world, mode, policy):
    env = environment(world, mode)
    warm, initial = original_evidence(env, mode)
    warm_raw = pinned_source(warm, "nkr16-warm")
    old = NativeOperatorDiscovery.from_warmup(warm_raw, digest(warm_raw))
    old_bytes = old.checkpoint()
    original_source = pinned_source(initial, "nkr16-initial")
    initial_sha = digest(original_source)
    planner = NativeActiveIntervention.from_initial_public_source(
        original_source, initial_sha, mode=mode, policy=policy)
    original_planner_sha = planner.checkpoint_sha256
    if mode == "structured":
        # Independently fitted, exhaustive positive-conjunction reference,
        # same initial sixteen action outcomes, no hidden world operator.
        strong_intercept, strong_mask, strong_masks = (
            nkr12.independent_broader_symbolic_fit(initial))
        candidates = tuple(strong_masks)
        if not candidates or candidates != planner.operator_candidates:
            raise AssertionError("NKR16_INDEPENDENT_SOURCE_CANDIDATES_DRIFT")
    else:
        candidates = None
    selected = []
    receipts = []
    budget = 4 if mode == "unrestricted" else 2
    for round_index in range(budget):
        proposal = planner.select_next_action()
        expected_context = independent_next(
            mode, policy, initial_sha, round_index, selected, candidates)
        if proposal is None or proposal["context"] != expected_context:
            raise AssertionError("NKR16_INDEPENDENT_POLICY_DECISION_DRIFT")
        x, action = proposal["context"], proposal["action"]
        if x in selected or x not in COLD or action != 1:
            raise AssertionError("NKR16_INVALID_SELECTED_PUBLIC_ACTION")
        # The only access to the actual new-world consequence happens
        # AFTER the planner and fully separate strong control select x.
        observed_y = env_outcome(env, mode, x, action)
        rows = [(f"new-intervention-{round_index:02d}", x, action, observed_y)]
        raw = pinned_source(rows, "nkr16-selected")
        before = planner.checkpoint()
        updated, receipt = planner.observe_selected_public_action(raw, digest(raw))
        if planner.checkpoint() != before:
            raise AssertionError("NKR16_MUTATED_PRIOR_PUBLIC_CHECKPOINT")
        planner = NativeActiveIntervention(
            updated.checkpoint(), updated.checkpoint_sha256)
        if planner.checkpoint() != updated.checkpoint():
            raise AssertionError("NKR16_FAILED_COLD_RECEIPT_REPLAY")
        if planner.predict(x, action)["classification"] != (
                "DIRECTLY_OBSERVED_ACTION_OUTCOME"):
            raise AssertionError("NKR16_OBSERVED_OUTCOME_LABELED_AS_PREDICTION")
        if planner.predict(x, action)["public_outcome"] != observed_y:
            raise AssertionError("NKR16_REPLAYED_ACTION_OUTCOME_DIFFERENT")
        selected.append(x)
        receipts.append(receipt["source_sha256"])
        if mode == "structured":
            baseline = strong_intercept ^ ((x & strong_mask).bit_count() & 1)
            effect = observed_y ^ baseline
            candidates = tuple(m for m in candidates if
                               int((x & m) == m) == effect)
            if candidates != planner.operator_candidates:
                raise AssertionError("NKR16_INDEPENDENT_OPERATOR_FILTER_DRIFT")
        else:
            if planner.candidate_count != 1 << (8 - len(selected)):
                raise AssertionError("NKR16_UNRESTRICTED_INFO_LIMIT_DRIFT")
    if old.checkpoint() != old_bytes:
        raise AssertionError("NKR16_OLD_MODEL_CHANGED_BY_INTERVENTION")
    if original_planner_sha == planner.checkpoint_sha256:
        raise AssertionError("NKR16_INTERVENTION_DID_NOT_STAGE_NEW_EVIDENCE")
    remaining = set(COLD) - set(selected)
    baseline_correct = 0
    generalization_correct = 0
    generalization_covered = 0
    generalization_wrong = 0
    strong_correct = 0
    strong_covered = 0
    retained = 0
    for x in COLD:
        base = planner.predict(x, 0)
        truth = env_outcome(env, mode, x, 0)
        baseline_correct += int(base["public_outcome"] == truth)
        if base["native_accepted"] or base["scientific_pass"]:
            raise AssertionError("NKR16_FIXTURE_PROMOTED_AS_REAL_WORLD")
    for x in sorted(remaining):
        answer = planner.predict(x, 1)
        prediction = answer["public_outcome"]
        truth = env_outcome(env, mode, x, 1)
        generalized = int(prediction is not None and prediction == truth)
        generalization_correct += generalized
        generalization_covered += int(prediction is not None)
        generalization_wrong += int(prediction is not None and prediction != truth)
        if mode == "structured":
            strong_base = strong_intercept ^ ((x & strong_mask).bit_count() & 1)
            strong_pred = independent_consensus(candidates, strong_base, x)
            strong_correct += int(strong_pred is not None and strong_pred == truth)
            strong_covered += int(strong_pred is not None)
            if strong_pred != prediction:
                raise AssertionError("NKR16_INDEPENDENT_EXACT_SYMBOLIC_TIE_FAIL")
        elif prediction is not None:
            raise AssertionError("NKR16_UNRESTRICTED_UNOBSERVED_EFFECT_GUESSED")
    for x in range(16):
        for a in (0, 1):
            old_truth = env_outcome(env, mode, x, a, old=True)
            retained += int(old.prior(x, a) == old_truth)
    if retained != 32 or len(receipts) != budget:
        raise AssertionError("NKR16_OLD_MEMORY_OR_ACTION_BUDGET_DRIFT")
    return {
        "world": world, "mode": mode, "policy": policy,
        "selected": selected,
        "new_actions_observed": budget,
        "old_retention": retained,
        "baseline_cold_correct": baseline_correct,
        "remaining_unprobed_effects": len(remaining),
        "unprobed_generalization_correct": generalization_correct,
        "unprobed_generalization_coverage": generalization_covered,
        "unprobed_generalization_wrong": generalization_wrong,
        "independent_strong_correct": strong_correct,
        "independent_strong_coverage": strong_covered,
        "final_version_count": planner.candidate_count,
        "public_receipt_hashes": receipts,
        "source_checkpoint_sha256": planner.checkpoint_sha256,
        "old_memory_sha256": old.checkpoint_sha256,
        "science_pass": False,
    }


def run_frozen():
    clock = time.monotonic()
    before_native = PublicCausalCells().snapshot()
    reports = []
    for mode in ("unrestricted", "structured"):
        for world in range(12):
            for policy in ("active", "random"):
                reports.append(run_one_world(world, mode, policy))
    totals = {}
    for mode in ("unrestricted", "structured"):
        totals[mode] = {}
        for policy in ("active", "random"):
            cohort = [r for r in reports if r["mode"] == mode and
                      r["policy"] == policy]
            totals[mode][policy] = {
                "worlds": len(cohort),
                "public_actions": sum(r["new_actions_observed"] for r in cohort),
                "baseline_correct": sum(r["baseline_cold_correct"] for r in cohort),
                "old_retention": sum(r["old_retention"] for r in cohort),
                "remaining_unprobed_effects": sum(
                    r["remaining_unprobed_effects"] for r in cohort),
                "unprobed_generalization_correct": sum(
                    r["unprobed_generalization_correct"] for r in cohort),
                "unprobed_generalization_coverage": sum(
                    r["unprobed_generalization_coverage"] for r in cohort),
                "unprobed_generalization_wrong": sum(
                    r["unprobed_generalization_wrong"] for r in cohort),
                "remaining_version_counts": [r["final_version_count"]
                                            for r in cohort],
            }
    u = totals["unrestricted"]
    s = totals["structured"]
    # Source-free engineering contract. A zero or negative active advantage
    # is a legitimate frozen research null, not reason to retune policy.
    for policy in ("active", "random"):
        arm = u[policy]
        if (arm["public_actions"] != 48
                or arm["baseline_correct"] != 96
                or arm["old_retention"] != 384
                or arm["remaining_unprobed_effects"] != 48
                or arm["unprobed_generalization_coverage"] != 0
                or arm["unprobed_generalization_wrong"] != 0
                or any(c != 16 for c in arm["remaining_version_counts"])):
            raise AssertionError("NKR16_UNRESTRICTED_INFORMATION_BOUND_FAIL")
        st = s[policy]
        if (st["public_actions"] != 24 or st["old_retention"] != 384
                or st["baseline_correct"] != 96
                or st["remaining_unprobed_effects"] != 72
                or st["unprobed_generalization_wrong"] != 0):
            raise AssertionError("NKR16_STRUCTURED_SOURCE_OR_RETENTION_DRIFT")
    for r in reports:
        if r["mode"] == "structured" and (
                r["unprobed_generalization_correct"] !=
                r["independent_strong_correct"]
                or r["unprobed_generalization_coverage"] !=
                r["independent_strong_coverage"]):
            raise AssertionError("NKR16_STRONG_CONTROL_RESULT_DRIFT")
    if PublicCausalCells().snapshot() != before_native:
        raise AssertionError("NKR16_ORIGINAL_OWNER_CAUSAL_CELLS_MUTATED")
    advantage = (
        s["active"]["unprobed_generalization_correct"] -
        s["random"]["unprobed_generalization_correct"])
    outcome = {
        "schema": "yggdrasil.nkr16.active-information-value-frozen-result.v1",
        "classification": (
            "STRUCTURED_ACTIVE_DEV_ADVANTAGE" if advantage >= 4
            else "STRUCTURED_ACTIVE_DEV_NO_PROVEN_ADVANTAGE"),
        "engineering_contract_pass": True,
        "structured_extra_unprobed_correct": advantage,
        "structured_active_threshold": 4,
        "no_original_science_first_use": True,
        "source_kind": "synthetic_public_action_consequences",
        "all_results_are_reused_fixture_development": True,
        "strong_control_has_same_preprogrammed_conjunction_grammar": True,
        "unrestricted_information_gain_advantage": 0,
        "unrestricted_policy_information_gain_bits_per_world": 4,
        "unrestricted_total_consistent_functions_after_4": 16,
        "novel_unrestricted_effects_inferred": 0,
        "scientific_pass": False, "native_accepted": False,
        "original_21m_historical_image_read": False,
        "totals": totals, "per_world": reports,
        "wall_seconds": time.monotonic() - clock,
    }
    return outcome


if __name__ == "__main__":
    print("NKR16_FROZEN_INFORMATION_VALUE=" + json.dumps(
        run_frozen(), sort_keys=True, separators=(",", ":")), flush=True)
