"""WSP-09 frozen public DEV: online neural self-allocation, no OOD claim."""
from __future__ import annotations

import json
import time

from slot_graph import (
    INPUT_BITS, SLOTS, PLASTIC_COUNT, SPEC, SelfAllocatingCircuit,
)
from controls import (
    FUNCTIONS_3, FUNCTIONS_4, FIXED_4_MASKS, observed_events,
    ExactAssociative, TrainedOneHotLogistic,
)


def run_dev() -> dict:
    start = time.perf_counter()
    required = 256*8 + 72*16
    before_unknown = immediate_correct = post_complete_correct = 0
    exact_correct = exact_pre_unknown = 0
    restored = replays = isolated = fault_cases = 0
    total_worlds = full_allocation = 0
    checkpoint_bytes = []
    nonzero_plastic = []
    direct_seconds = 0.0
    trained_seconds = 0.0
    trained_worlds = trained_predictions = trained_steps = 0
    losses = []

    for bits, masks in ((3, FUNCTIONS_3), (4, FUNCTIONS_4)):
        for mask in masks:
            timer = time.perf_counter()
            model = SelfAllocatingCircuit()
            exact = ExactAssociative()
            events = observed_events(mask, bits)
            for raw, observed_label in events:
                before_unknown += int(model.predict(raw) is None)
                exact_pre_unknown += int(exact.predict(raw) is None)
                model.observe(raw, observed_label)
                exact.observe(raw, observed_label)
                immediate_correct += int(model.predict(raw) == observed_label)
            total_worlds += 1
            full_allocation += int(model.allocated_slots == len(events))
            nonzero_plastic.append(model.positive_plastic)
            state = model.snapshot()
            checkpoint_bytes.append(len(state))
            recovered = SelfAllocatingCircuit.restore(state)
            restored += int(recovered.snapshot() == state and
                            recovered.programmed_sha256() ==
                            model.programmed_sha256())
            for e in (events[0], events[1], events[-2], events[-1]):
                recovered.observe(*e)
            replays += int(recovered.snapshot() == state)

            separate = SelfAllocatingCircuit()
            separate.observe(events[0][0],events[0][1] ^ 1)
            isolated += int(model.snapshot() == state and
                            separate.programmed_sha256() !=
                            model.programmed_sha256())

            for raw, label in events:
                post_complete_correct += int(recovered.predict(raw) == label)
                exact_correct += int(exact.predict(raw) == label)

            # A previously seen context changes its outcome. That violation
            # activates a numeric synaptic fault, not a Python exception or
            # fabricated changed-world extrapolation.
            old, old_reward = events[0]
            model.observe(old, old_reward ^ 1)
            assert model.fault == 1
            assert all(model.predict(raw) is None for raw, _ in events)
            fault_cases += 1
            direct_seconds += time.perf_counter()-timer

            if bits == 4 and mask in FIXED_4_MASKS:
                timer = time.perf_counter()
                conventional = TrainedOneHotLogistic()
                conventional.fit(events)
                trained_seconds += time.perf_counter()-timer
                trained_worlds += int(conventional.converged)
                trained_steps += conventional.steps
                losses.append(conventional.loss)
                for raw, label in events:
                    trained_predictions += int(conventional.predict(raw) == label)

    assert total_worlds == 328 and required == 3200
    assert before_unknown == exact_pre_unknown == required
    assert immediate_correct == post_complete_correct == exact_correct == required
    assert full_allocation == restored == replays == isolated == fault_cases == 328
    assert (trained_worlds, trained_predictions) == (8, 128)

    return {
        "schema": "wsp09.public-dev-result.v1",
        "classification": "ENGINEERING_DEV_IF_FINAL_CI_PASS__SCIENTIFIC_UNVERIFIED",
        "exhaustive_three_bit_boolean_maps": 256,
        "deterministic_four_bit_boolean_maps": 72,
        "total_worlds": total_worlds,
        "genuine_observed_consequence_labels": required,
        "before_first_witness_abstentions": before_unknown,
        "after_each_witness_correct_recalled_labels": immediate_correct,
        "after_complete_exposure_correct_recalled_labels": post_complete_correct,
        "independent_exact_symbolic_after_exposure": exact_correct,
        "independent_exact_symbolic_before_exposure_abstentions": exact_pre_unknown,
        "homogeneous_neural_allocating_circuit": {
            "initial_blank_slot_count": SLOTS,
            "plastic_binary_weight_slots": PLASTIC_COUNT,
            "fixed_numeric_coefficients": len(SPEC.fixed_indices),
            "numerical_coefficient_slots": len(SPEC.initial_weights),
            "fixed_threshold_neuron_count": len(SPEC.thresholds),
            "fixed_directed_synapse_incidence_edges": len(SPEC.edges),
            "uniform_local_plastic_update_rules": len(SPEC.plastic_rules),
            "program_sha256": SPEC.source_sha256,
            "all_exposed_patterns_allocated_worlds": full_allocation,
            "nonzero_plastic_min": min(nonzero_plastic),
            "nonzero_plastic_max": max(nonzero_plastic),
            "gradient_training_steps": 0,
            "task_specific_Python_slot_allocator": False,
            "task_specific_Python_inference_lookup": False,
            "generic_numerical_Python_VM_required": True,
            "operator_type_family_preprogrammed": True,
            "preenumerated_input_identifiers_in_fixed_weights": False,
        },
        "retention": {
            "exact_cold_checkpoint_restores": restored,
            "four_genuine_prior_event_replays_idempotent": replays,
            "separate_world_weight_isolation": isolated,
            "checkpoint_min_bytes": min(checkpoint_bytes),
            "checkpoint_max_bytes": max(checkpoint_bytes),
        },
        "frozen_negatives": {
            "prewitness_unknown_context_abstentions": before_unknown,
            "label_changed_for_previously_seen_context_fault_triggered": fault_cases,
            "post_contradiction_global_abstention_worlds": fault_cases,
            "novel_fifth_input_dimension_unsupported": True,
            "arbitrary_unseen_truth_table_bits_predictable_without_evidence": False,
            "worst_case_4_input_independent_label_observation_lower_bound": 16,
        },
        "trained_gradient_control": {
            "architecture": "4-bit to 16-hot fixed encoder, 16 trainable logistic output weights",
            "optimizer": "full-batch Adam",
            "seed": 17,
            "learn_rate": 0.05,
            "stop_BCE": 0.02,
            "max_epochs": 3000,
            "tested_worlds": len(FIXED_4_MASKS),
            "all_worlds_converged": trained_worlds == 8,
            "converged_worlds": trained_worlds,
            "heldout_prediction_claim": False,
            "post_training_correct_observed_labels": trained_predictions,
            "gradient_steps_total": trained_steps,
            "mean_final_train_BCE": sum(losses)/len(losses),
            "equal_observational_data_for_compared_worlds": True,
            "matched_end_to_end_compute_or_capacity": False,
        },
        "wall_time_seconds": {
            "direct_numeric_training_readback_restore_replay_fault": round(direct_seconds,6),
            "trained_control_fit_only_eight_worlds": round(trained_seconds,6),
            "whole_dev_runner": round(time.perf_counter()-start,6),
            "comparison_warning": "Not matched workloads; different world counts, architecture, checkpoint/control work, and implementation overhead."
        },
        "scientific_limit": "Each observed Boolean context is memorized by a self-allocated neural address/label slot. The slot format and equality/first-free operator are preprogrammed. It does not generalize to unobserved arbitrary outcomes or construct new operator types. All data are authored public synthetic development fixtures, not independently unfamiliar causal environments."
    }


if __name__ == "__main__":
    print(json.dumps(run_dev(), sort_keys=True, indent=2))
