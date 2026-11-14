"""WSP101 H04: real consequence-to-numerical-weights DEV feasibility.

Not a model-intelligence gain: an independently coded symbolic solver with
the same quadratic prior is expected to tie, and cubic laws remain impossible
to identify with this source basis.
"""
from __future__ import annotations

import hashlib
import json
import time
from headroom_h04_world import (
    DEV_IDS, SOURCE_ACTIONS, HELDOUT_ACTIONS, observed_source,
    evaluator_truth_only, observed_passive
)
from headroom_h04_writer import DirectWeightBank
from headroom_h04_symbolic import SymbolicPolynomial

FREEZE_SHA = "432117de33f0c03a2926b4acddfbde2647aab1a7"


def audit():
    started = time.perf_counter_ns()
    start_cpu = time.process_time_ns()
    bank = DirectWeightBank()
    symbolic = []
    transcript = hashlib.sha256()
    fit_cpu = 0
    symbolic_fit_cpu = 0
    half_image_sha = None
    fit_snapshot = None
    for world in DEV_IDS:
        source = observed_source(world)
        transcript.update(json.dumps(source, separators=(",", ":")).encode("ascii"))
        t = time.process_time_ns()
        bank.write(world, source)
        fit_cpu += time.process_time_ns() - t
        t = time.process_time_ns()
        symbolic.append(SymbolicPolynomial(source))
        symbolic_fit_cpu += time.process_time_ns() - t
        if world == 15:
            fit_snapshot = bank.cold_image()
            half_image_sha = hashlib.sha256(fit_snapshot).hexdigest()
            cold = DirectWeightBank.restore(fit_snapshot)
            assert cold.cold_image() == fit_snapshot
    full_image = bank.cold_image()
    restored = DirectWeightBank.restore(full_image)
    if restored.cold_image() != full_image:
        raise AssertionError("H04 cold checkpoint not bit-identical")
    counts = {"numeric": 0, "symbolic": 0, "restored": 0,
              "raw_lookup_coverage": 0, "fixed_zero": 0}
    cubic_source_identical = 0
    cubic_heldout_differences = 0
    start_eval = time.process_time_ns()
    passive_expected = observed_passive(0)
    for world in DEV_IDS:
        source = observed_source(world)
        if observed_passive(world) != passive_expected:
            raise AssertionError("H04 passive distinguishes laws")
        if all(evaluator_truth_only(world, x, cubic=True) == y for x, y in source):
            cubic_source_identical += 1
        lookup = dict(source)
        for x in HELDOUT_ACTIONS:
            answer = evaluator_truth_only(world, x)
            counts["numeric"] += bank.predict(world, x) == answer
            counts["symbolic"] += symbolic[world].predict(x) == answer
            counts["restored"] += restored.predict(world, x) == answer
            counts["raw_lookup_coverage"] += x in lookup
            counts["fixed_zero"] += answer == 0
            if world == 0:
                cubic_heldout_differences += (
                    evaluator_truth_only(world, x, cubic=True) != answer
                )
    prediction_cpu = time.process_time_ns() - start_eval
    if bank.cold_image() != full_image:
        raise AssertionError("H04 target readout changed source weights")
    if fit_snapshot is None:
        raise AssertionError("H04 no cold checkpoint")
    first_half_restored = DirectWeightBank.restore(fit_snapshot)
    # The first sixteen slots must be unchanged after writing later worlds.
    first_half_stable = all(
        first_half_restored.predict(world, x) == bank.predict(world, x)
        for world in range(16) for x in HELDOUT_ACTIONS
    )
    total = len(DEV_IDS) * len(HELDOUT_ACTIONS)
    valid = (counts["numeric"] == total
             and counts["symbolic"] == total
             and counts["restored"] == total
             and counts["raw_lookup_coverage"] == 0
             and first_half_stable and cubic_source_identical == len(DEV_IDS)
             and cubic_heldout_differences == 128)
    return {
        "schema": "yggdrasil.wsp101.h04.dev-weight-programming.v1",
        "preregistration_sha": FREEZE_SHA,
        "classification": ("DEV_NATIVE_WEIGHT_PROGRAMMING_PARITY"
                           if valid else "DEV_NATIVE_WEIGHT_PROGRAMMING_NEGATIVE"),
        "arbitrary_quadratic_program_bits": 56,
        "possible_causal_laws": "2^56",
        "dev_worlds": len(DEV_IDS),
        "new_worlds_same_degree_family": 16,
        "observed_intervention_episodes": len(DEV_IDS) * len(SOURCE_ACTIONS),
        "observed_action_steps": len(DEV_IDS) * len(SOURCE_ACTIONS) * 2,
        "heldout_target_actions_per_world": len(HELDOUT_ACTIONS),
        "heldout_query_count": total,
        "correct": counts,
        "cubic_out_of_family_source_indistinguishable_worlds": cubic_source_identical,
        "cubic_out_of_family_different_heldout_actions_one_world": cubic_heldout_differences,
        "cold_retention_and_noninterference": first_half_stable,
        "packed_numeric_weight_bytes_per_world": 7,
        "packed_numeric_weight_bytes_total": bank.numeric_bytes,
        "checkpoint_bytes_total": bank.checkpoint_bytes,
        "half_written_cold_sha256": half_image_sha,
        "full_cold_sha256": hashlib.sha256(full_image).hexdigest(),
        "public_source_sha256": transcript.hexdigest(),
        "direct_fit_cpu_ns": fit_cpu,
        "symbolic_fit_cpu_ns": symbolic_fit_cpu,
        "all_prediction_and_eval_cpu_ns": prediction_cpu,
        "full_process_cpu_ns": time.process_time_ns() - start_cpu,
        "whole_process_wall_ns": time.perf_counter_ns() - started,
        "source_oracle_passed_into_writer": False,
        "scientific_superiority": False,
        "fully_trained_conventional_baseline_executed": False,
        "protected_original_worlds_used": False,
        "native_accepted_model_modified": False,
        "unfamiliar_family_transfer_demonstrated": False,
        "limitations": ("Given degree<=2 prior, independent ANF symbolic solver is "
                        "equally accurate. Added cubic interactions are observationally "
                        "indistinguishable on source and diverge at heldout. "
                        "DEV numerical encoding is not AGI or source-independent discovery."),
    }
