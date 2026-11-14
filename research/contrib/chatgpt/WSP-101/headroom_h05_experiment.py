"""H05 frozen DEV test of incremental numerical causal weight repair.

This script imports the evaluator only to COLLECT PUBLIC EVENTS and SCORE
heldout outcomes. Direct numerical writer and independent symbolic control
never import the evaluator or access hidden rule coefficients.
"""
from __future__ import annotations
import hashlib
import json
import time
from headroom_h05_world import (
    DEV_IDS, SOURCE_ACTIONS, REPAIR_ACTIONS, HELDOUT, observed_basis,
    observed_repair, observed_passive, evaluator_truth_only
)
from headroom_h05_writer import DirectRepairBank, _sparse_syndrome_decoder
from headroom_h05_symbolic import ExactSymbolicRepair

FREEZE = "853cf9577a466ae80955e333be86f8d932f9687b"


def audit():
    wall_start, cpu_start = time.perf_counter_ns(), time.process_time_ns()
    bank = DirectRepairBank()
    symbolic = []
    quadratic_only = []
    restored_half = None
    half_sha = None
    source_digest = hashlib.sha256()
    numeric_fit_ns = 0
    cubic_repair_ns = 0
    symbolic_fit_ns = 0
    detected = {"zero": 0, "single": 0, "double": 0}
    quadratic_immutable = True
    no_passive_information = True
    for world in DEV_IDS:
        source = observed_basis(world)
        interventions = observed_repair(world)
        source_digest.update(json.dumps(
            {"basis": source, "repair": interventions},
            sort_keys=True, separators=(",", ":")
        ).encode("ascii"))
        no_passive_information &= observed_passive(world) == observed_passive(0)
        t = time.process_time_ns()
        bank.fit_quadratic(world, source)
        numeric_fit_ns += time.process_time_ns() - t
        before = bank.base_bytes(world)
        quad_image = int.from_bytes(before, "little")
        quadratic_only.append(quad_image)
        t = time.process_time_ns()
        cardinality = bank.repair_cubic(world, interventions)
        cubic_repair_ns += time.process_time_ns() - t
        quadratic_immutable &= bank.base_bytes(world) == before
        if cardinality not in (0, 1, 2):
            raise AssertionError("H05 illegal learned cubic sparsity")
        detected[("zero", "single", "double")[cardinality]] += 1
        t = time.process_time_ns()
        symbolic.append(ExactSymbolicRepair(source, interventions))
        symbolic_fit_ns += time.process_time_ns() - t
        if world == 15:
            half_image = bank.cold_image()
            restored_half = DirectRepairBank.restore(half_image)
            half_sha = hashlib.sha256(half_image).hexdigest()
    full_image = bank.cold_image()
    cold = DirectRepairBank.restore(full_image)
    if full_image != cold.cold_image():
        raise AssertionError("H05 cold bits not preserved")

    scores = {k: 0 for k in (
        "repaired", "symbolic", "cold_repaired",
        "quadratic_only", "fixed_zero", "source_lookup_coverage"
    )}
    retain = True
    out_of_class_source_same = 0
    out_of_class_heldout_diff = 0
    scoring_start = time.process_time_ns()
    for world in DEV_IDS:
        basis, repair = observed_basis(world), observed_repair(world)
        if all(evaluator_truth_only(world, action, unknown_tenway=True) == y
               for action, y in basis + repair):
            out_of_class_source_same += 1
        known = {a for a, _ in basis + repair}
        for action in HELDOUT:
            true = evaluator_truth_only(world, action)
            scores["repaired"] += bank.predict(world, action) == true
            scores["symbolic"] += symbolic[world].predict(action) == true
            scores["cold_repaired"] += cold.predict(world, action) == true
            # The original stored seven-byte quadratic term is read without
            # applying the new cubic correction.
            from headroom_h04_writer import predict_weights
            scores["quadratic_only"] += predict_weights(quadratic_only[world], action) == true
            scores["fixed_zero"] += true == 0
            scores["source_lookup_coverage"] += action in known
            if world < 16:
                retain &= restored_half.predict(world, action) == bank.predict(world, action)
            if world == 0:
                out_of_class_heldout_diff += (
                    evaluator_truth_only(world, action, unknown_tenway=True) != true
                )
    scoring_ns = time.process_time_ns() - scoring_start
    total = len(DEV_IDS) * len(HELDOUT)
    correct_cubic_counts = (
        detected == {"zero": 11, "single": 11, "double": 10}
    )
    success = (
        len(_sparse_syndrome_decoder()) == 7261
        and scores["repaired"] == total
        and scores["symbolic"] == total
        and scores["cold_repaired"] == total
        and scores["quadratic_only"] < total
        and scores["source_lookup_coverage"] == 0
        and correct_cubic_counts
        and quadratic_immutable
        and retain
        and no_passive_information
        and out_of_class_source_same == len(DEV_IDS)
        and out_of_class_heldout_diff == 1
    )
    return {
        "schema": "yggdrasil.wsp101.h05.sparse-cubic-repair-dev-result.v1",
        "preregistration": FREEZE,
        "classification": ("DEV_SPARSE_CUBIC_WEIGHT_REPAIR_PARITY"
                           if success else "DEV_REPAIR_NEGATIVE"),
        "possible_sparse_cubic_programs": 7261,
        "distinct_source_syndromes": len(_sparse_syndrome_decoder()),
        "dev_worlds": len(DEV_IDS),
        "new_worlds_same_sparse_cubic_family": 16,
        "source_intervention_episodes": len(DEV_IDS) * (len(SOURCE_ACTIONS) + len(REPAIR_ACTIONS)),
        "source_public_action_steps": 2 * len(DEV_IDS) * (len(SOURCE_ACTIONS) + len(REPAIR_ACTIONS)),
        "heldout_queries": total,
        "heldout_actions_per_world": len(HELDOUT),
        "learned_cubic_counts": detected,
        "accuracy_counts": scores,
        "quadratic_weights_unchanged_during_cubic_repair": bool(quadratic_immutable),
        "cold_retention_and_other_world_noninterference": bool(retain),
        "same_passive_public_observations": bool(no_passive_information),
        "high_order_unidentifiable_source_worlds": out_of_class_source_same,
        "high_order_different_heldout_actions_in_world_zero": out_of_class_heldout_diff,
        "packed_numerical_bytes_per_world": 22,
        "packed_numerical_bytes_total": bank.numeric_bytes,
        "checkpoint_bytes_total": bank.checkpoint_bytes,
        "half_checkpoint_sha256": half_sha,
        "full_checkpoint_sha256": hashlib.sha256(full_image).hexdigest(),
        "public_source_sha256": source_digest.hexdigest(),
        "numeric_quadratic_fit_cpu_ns": numeric_fit_ns,
        "numeric_cubic_repair_cpu_ns": cubic_repair_ns,
        "independent_symbolic_fit_cpu_ns": symbolic_fit_ns,
        "all_prediction_and_scoring_cpu_ns": scoring_ns,
        "end_to_end_cpu_ns": time.process_time_ns() - cpu_start,
        "end_to_end_wall_ns": time.perf_counter_ns() - wall_start,
        "scientific_pass": False,
        "fully_trained_conventional_baseline_executed": False,
        "truly_unfamiliar_family_transfer_demonstrated": False,
        "protected_original_worlds_used": False,
        "accepted_model_weights_changed": False,
        "limitations": ("Sparse 0/1/2 cubic class and intervention design supplied; "
                        "the independent symbolic solver has exactly the same evidence "
                        "and known degree/sparsity prior. The unobserved ten-way "
                        "conjunction proves general unknown-family discovery impossible "
                        "under this action budget. No claimed training speedup."),
    }
