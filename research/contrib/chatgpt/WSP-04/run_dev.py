"""Frozen WSP-04 public synthetic DEV comparison; prints JSON, never dispatches."""
from __future__ import annotations
import json
import time

from circuit import (
    BASE, PAIRS, SEEDS, MODES, HELDOUT, REPLAY,
    WeightWrittenCircuit, ExactSymbolicANF, TrainedMLPControl,
    baseline_observations, public_reward, true_choice,
)


def run_dev() -> dict:
    started = time.perf_counter()
    final_scores = dict(weight_written=0, exact_symbolic=0,
                        no_growth=0, state_erased=0, trained_mlp=0)
    pre_error = middle_error = pre_confident_error = middle_confident_error = 0
    wrong_fifth = confident_fifth = absent_fifth = unsafe_after_witness = 0
    learned_fourth = cold = replayed = 0
    decisive = ties = 0
    max_gate_count = 0
    snaps = []
    mlp_loss = []
    weight_time = mlp_time = 0.0

    for seed in SEEDS:
        for pair in PAIRS:
            for mode in MODES:
                target = true_choice(seed, pair, mode, HELDOUT)
                if target is None:
                    ties += 1
                else:
                    decisive += 1
                examples = baseline_observations(seed, pair, mode)
                start_weight = time.perf_counter()
                model = WeightWrittenCircuit()
                symbolic = ExactSymbolicANF()
                limited = WeightWrittenCircuit(max_degree=3)
                for sample in examples:
                    model.observe(*sample)
                    symbolic.observe(*sample)
                    limited.observe(*sample)
                pre = model.choose(HELDOUT)
                assert pre == symbolic.choose(HELDOUT)
                pre_error += pre != target
                pre_confident_error += pre is not None and pre != target

                witnesses = tuple((mask, 1, public_reward(seed, pair, mode, mask, 1))
                                  for mask in pair)
                for system in (model, symbolic, limited):
                    system.observe(*witnesses[0])
                halfway = model.choose(HELDOUT)
                assert halfway == symbolic.choose(HELDOUT)
                middle_error += halfway != target
                middle_confident_error += halfway is not None and halfway != target

                for system in (model, symbolic, limited):
                    system.observe(*witnesses[1])
                assert model.degree_four_gates == mode
                assert model.choose(HELDOUT) == symbolic.choose(HELDOUT) == target
                assert model.gate_count <= 64
                for action in (0, 1):
                    r = public_reward(seed, pair, mode, HELDOUT, action)
                    assert model.predict_reward(HELDOUT, action) == r
                    assert symbolic.predict_reward(HELDOUT, action) == r

                final_scores["weight_written"] += model.choose(HELDOUT) == target
                final_scores["exact_symbolic"] += symbolic.choose(HELDOUT) == target
                final_scores["no_growth"] += limited.choose(HELDOUT) == target
                final_scores["state_erased"] += WeightWrittenCircuit().choose(HELDOUT) == target
                learned_fourth += model.degree_four_gates
                max_gate_count = max(max_gate_count, model.gate_count)

                saved = model.snapshot()
                snaps.append(len(saved))
                restored = WeightWrittenCircuit.restore(saved)
                cold += restored.snapshot() == saved and restored.choose(HELDOUT) == target
                for c, a in REPLAY:
                    restored.observe(c, a, public_reward(seed, pair, mode, c, a))
                replayed += restored.snapshot() == saved

                # Frozen fifth-degree OOD is not identifiable from two of five
                # four-way observed coefficients. Overconfident errors matter.
                ood_target = true_choice(seed, pair, mode, HELDOUT,
                                         fifth_negative=True)
                guess = restored.choose(HELDOUT)
                wrong_fifth += guess != ood_target
                confident_fifth += guess is not None and guess != ood_target
                absent_fifth += HELDOUT not in restored.gates[1]
                restored.observe(HELDOUT, 1,
                                 public_reward(seed, pair, mode, HELDOUT, 1,
                                               fifth_negative=True))
                assert HELDOUT not in restored.gates[1]
                assert restored.unsafe
                unsafe_after_witness += restored.choose(HELDOUT) is None

                weight_time += time.perf_counter() - start_weight
                start_mlp = time.perf_counter()
                train = TrainedMLPControl()
                train.fit(examples + witnesses, pair)
                mlp_loss.append(train.loss)
                final_scores["trained_mlp"] += train.choose(HELDOUT) == target
                mlp_time += time.perf_counter() - start_mlp

    assert decisive + ties == 120
    assert final_scores["weight_written"] == final_scores["exact_symbolic"] == 120
    assert (pre_error, middle_error, learned_fourth) == (40, 40, 120)
    assert cold == replayed == 120
    assert (wrong_fifth, absent_fifth, unsafe_after_witness) == (120, 120, 120)
    return {
        "schema": "wsp04.public-dev-result.v1",
        "classification": "ENGINEERING_DEV_MECHANISM_IF_CI_PASSES__SCIENCE_UNVERIFIED",
        "experiments": 120,
        "context_bits": 5,
        "baseline_public_contexts": len(BASE),
        "baseline_public_interventions": len(BASE) * 2,
        "observed_new_interaction_witnesses": 2,
        "transfer_context": HELDOUT,
        "true_decisive_cases": decisive, "true_tie_cases": ties,
        "post_two_witness_exact_policy_including_ties": final_scores,
        "first_order_of_exposure": {
            "incorrect_policy_before_four_way_witnesses": pre_error,
            "confidently_incorrect_before": pre_confident_error,
            "incorrect_policy_after_one_witness": middle_error,
            "confidently_incorrect_after_one": middle_confident_error,
            "correct_after_second": final_scores["weight_written"]
        },
        "construction": {
            "total_new_four_way_threshold_cells": learned_fourth,
            "binary_input_weights_per_new_cell": 5,
            "new_cell_weights_from_public_residuals": True,
            "gradient_steps_direct": 0,
            "max_gate_count_observed": max_gate_count,
            "sparse_unobserved_coefficient_prior": True
        },
        "retention": {
            "cold_exact_restores": cold, "idempotent_observation_replays": replayed,
            "checkpoint_min_bytes": min(snaps), "checkpoint_max_bytes": max(snaps)
        },
        "fifth_degree_negative": {
            "worlds": 120,
            "wrong_policies_before_any_fifth_witness": wrong_fifth,
            "wrong_confident_actions": confident_fifth,
            "refused_to_invent_fifth_gate": absent_fifth,
            "abstained_after_genuine_unidentifiable_witness": unsafe_after_witness,
            "new_fifth_degree_rules_recovered": 0,
            "information_limit": "Only two of five fourth-order subsets were observed, so a nonzero context31 residual cannot be attributed uniquely to fifth order."
        },
        "trained_control": {
            "architecture": "6-12-1 tanh/sigmoid",
            "learned_float_weights": TrainedMLPControl.PARAMETERS,
            "full_batch_epochs_per_world": TrainedMLPControl.STEPS,
            "seed": TrainedMLPControl.SEED,
            "mean_final_train_bce": sum(mlp_loss) / len(mlp_loss),
            "matched_total_compute": False,
            "qualified_fully_trained_baseline": False
        },
        "wall_clock_dev_seconds": {
            "weight_compilation_plus_restore_and_negative": round(weight_time, 5),
            "trained_control_fit_and_inference": round(mlp_time, 5),
            "total": round(time.perf_counter() - started, 5),
            "disclaimer": "Non-matched model structure, algorithmic complexity and interpreter loops. No end-to-end speed superiority claim."
        },
        "scientific_limit": "The dynamic writer constructs fourth-order neurons beyond WSP-03 degree cap but within a known sparse Boolean monomial language. Exact symbolic solver ties. Nothing discovers arbitrary new primitives or general intelligence."
    }


if __name__ == "__main__":
    print(json.dumps(run_dev(), sort_keys=True, indent=2))
