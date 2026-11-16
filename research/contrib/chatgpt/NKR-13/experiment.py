"""NKR-13 prespecified operator-induction experiment on NKR-12 worlds.

No new or reused original scientific cohort. This is a deterministic DEV
falsification repair: data and source action observations are inherited
unchanged from NKR-12, with a separately implemented strong exact control.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_operator_discovery import NativeOperatorDiscovery
from yggdrasil.native_intervention_repair import digest
from yggdrasil.public_causal_cells import PublicCausalCells

NKR12 = Path(__file__).resolve().parents[1] / "NKR-12/experiment.py"
spec = importlib.util.spec_from_file_location("nkr12_fixed_original_env", NKR12)
nkr12 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nkr12)


def outcome_score(pred, correct):
    return int(pred is not None and pred == correct)


def run_frozen():
    start = time.monotonic()
    legacy_before = PublicCausalCells().snapshot()
    totals = {
        "worlds": 12, "noise_worlds": 4,
        "observations_per_new_world": 16,
        "cold_queries": 192, "old_retention_queries": 384,
        "mechanism_changes_detected": 0,
        "new_operators_supported": 0,
        "native_coverage": 0, "native_correct": 0,
        "native_confident_wrong": 0, "native_abstentions": 0,
        "strong_symbolic_coverage": 0, "strong_symbolic_correct": 0,
        "strong_symbolic_confident_wrong": 0,
        "prior_memory_retained": 0,
        "single_sensor_flip_refused": 0,
        "noise_false_repairs": 0,
        "cold_replay_equal": 0,
        "strong_native_prediction_mismatches": 0,
    }
    per_world = []
    for world in range(12):
        env = nkr12.IndependentActionWorld(world)
        warm = nkr12.observations(env, warm=True)
        original_raw = nkr12.bundle(f"nkr13-warm-world-{world:02d}", warm)
        original = NativeOperatorDiscovery.from_warmup(
            original_raw, digest(original_raw))
        old_bytes = original.checkpoint()
        raw_repair_records = nkr12.observations(env)
        repair_raw = nkr12.bundle(
            f"nkr13-repair-world-{world:02d}", raw_repair_records)
        successor, receipt = original.stage_public_interventions(
            repair_raw, digest(repair_raw))
        if (not successor.operator_discovered or original.operator_discovered
                or receipt["new_events"] != 16):
            raise AssertionError("NKR13_OPERATOR_PROPOSAL_NOT_PROVEN")
        totals["mechanism_changes_detected"] += 1
        if nkr12.AND_MASKS[world] not in successor.operator_masks:
            raise AssertionError("NKR13_REAL_EFFECT_NOT_WITHIN_PROPOSED_OPERATORS")
        totals["new_operators_supported"] += 1
        cold = NativeOperatorDiscovery(
            successor.checkpoint(), successor.checkpoint_sha256)
        if cold.checkpoint() != successor.checkpoint():
            raise AssertionError("NKR13_COLD_SOURCE_CHECKPOINT_DIFFERENT")
        totals["cold_replay_equal"] += 1
        strong = nkr12.independent_broader_symbolic_fit(raw_repair_records)
        before = (totals["native_correct"], totals["native_coverage"],
                  totals["native_confident_wrong"])
        for x in nkr12.COLD:
            for action in (0, 1):
                new_truth = env.execute(x, action)
                native = cold.predict(x, action)
                control = nkr12.independent_broader_symbolic_predict(
                    strong, x, action)
                if (native["native_accepted"]
                        or native["can_write_causal_owner"]
                        or native["can_write_historical_facts"]
                        or native["scientific_pass"]):
                    raise AssertionError("NKR13_UNVERIFIED_OPERATOR_PROMOTED")
                answer = native["public_outcome"]
                totals["native_correct"] += outcome_score(answer, new_truth)
                totals["native_coverage"] += int(answer is not None)
                totals["native_confident_wrong"] += int(
                    answer is not None and answer != new_truth)
                totals["native_abstentions"] += int(answer is None)
                totals["strong_symbolic_correct"] += outcome_score(
                    control, new_truth)
                totals["strong_symbolic_coverage"] += int(control is not None)
                totals["strong_symbolic_confident_wrong"] += int(
                    control is not None and control != new_truth)
                totals["strong_native_prediction_mismatches"] += int(
                    answer != control)
        for x in range(16):
            for a in (0, 1):
                old_truth = env.execute(x, a, warm=True)
                totals["prior_memory_retained"] += outcome_score(
                    cold.prior(x, a), old_truth)
        if original.checkpoint() != old_bytes:
            raise AssertionError("NKR13_PRIOR_CHECKPOINT_WAS_MUTATED")
        per_world.append({
            "world": world,
            "proposed_operator_masks": len(successor.operator_masks),
            "native_correct": totals["native_correct"] - before[0],
            "native_coverage": totals["native_coverage"] - before[1],
            "confident_wrong": totals["native_confident_wrong"] - before[2],
            "old_source_sha256": original.checkpoint_sha256,
            "new_source_sha256": cold.checkpoint_sha256,
        })
    for world in nkr12.NOISE_WORLDS:
        env = nkr12.IndependentActionWorld(world, mode="noise")
        warm = nkr12.observations(env, warm=True)
        raw = nkr12.bundle(f"nkr13-noise-warm-{world:02d}",warm)
        original = NativeOperatorDiscovery.from_warmup(raw, digest(raw))
        frozen = original.checkpoint()
        measured = nkr12.observations(
            env, inject_single_sensor_noise=True)
        if sum(original.prior(x, a) != y for _, x, a, y in measured) != 1:
            raise AssertionError("NKR13_NOISE_SOURCE_NOT_ONE_ERROR")
        payload = nkr12.bundle(f"nkr13-noise-data-{world:02d}", measured)
        next_, receipt = original.stage_public_interventions(
            payload, digest(payload))
        if next_ is not original or next_.operator_discovered:
            totals["noise_false_repairs"] += 1
        if receipt["classification"] == "INSUFFICIENT_CHANGE_EVIDENCE":
            totals["single_sensor_flip_refused"] += 1
        if original.checkpoint() != frozen:
            raise AssertionError("NKR13_NOISE_ERASED_WARM_SOURCE")
    if PublicCausalCells().snapshot() != legacy_before:
        raise AssertionError("NKR13_YPC1_OWNER_STATE_MUTATED")
    inherited = nkr12.run_frozen()["totals"]
    if inherited["native_cold_correct"] != 121 or inherited["native_confident_cold_errors"] != 23:
        raise AssertionError("NKR13_FROZEN_NKR12_COMPARATOR_DRIFT")
    meets = (
        totals["native_correct"] >= 129
        and totals["native_confident_wrong"] == 0
        and totals["native_correct"] == totals["strong_symbolic_correct"]
        and totals["native_coverage"] == totals["strong_symbolic_coverage"]
        and totals["strong_native_prediction_mismatches"] == 0
        and totals["prior_memory_retained"] == 384
        and totals["mechanism_changes_detected"] == 12
        and totals["noise_false_repairs"] == 0
        and totals["single_sensor_flip_refused"] == 4
        and totals["cold_replay_equal"] == 12)
    return {
        "schema": "yggdrasil.nkr13.operator-discovery-frozen-diagnostic.v1",
        "classification": "SYNTHETIC_OPERATOR_REPAIR_DEV_PASS"
        if meets else "SYNTHETIC_OPERATOR_REPAIR_DEV_NO_GO",
        "source_mode": "engineering_fixture_only",
        "native_operator_family_expanded_from_nkr11": True,
        "operator_grammar_prespecified": True,
        "experiment_source": "unaltered_NKR12_synthetic_worlds",
        "frozen_dev_threshold_met": meets,
        "old_nkr12_native_correct": inherited["native_cold_correct"],
        "old_nkr12_confident_wrong": inherited["native_confident_cold_errors"],
        "per_world": per_world, "totals": totals,
        "independent_strong_control_superiority": False,
        "scientific_pass": False, "accepted_native": False,
        "original_historical_knowledge_scanned": False,
        "authentic_external_causal_evidence": False,
        "new_authentic_world_relations": 0,
        "total_dev_wall_seconds": time.monotonic()-start,
    }


if __name__ == "__main__":
    print("NKR13_FROZEN_OPERATOR_DEV="+json.dumps(
        run_frozen(),sort_keys=True,separators=(",",":")),flush=True)
