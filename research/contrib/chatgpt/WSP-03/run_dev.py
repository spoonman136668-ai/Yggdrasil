"""WSP-03: execute fully public DEV comparisons, not independent science."""
from __future__ import annotations
import json
import time

from weight_circuit import (
    BASIS, SEEDS, TRIPLES, TRANSFER, DirectWeightCircuit, ExactSymbolicANF,
    TrainedMLPControl, samples, world_reward, true_choice,
)


def run_dev() -> dict:
    started = time.perf_counter()
    scores = {k: 0 for k in ("weight_written", "exact_symbolic",
                             "no_growth", "state_erased", "trained_mlp")}
    decisive = ties = 0
    pre_novel_wrong = pre_novel_wrong_decisive = 0
    pre_novel_bad_reward = 0
    new_triple_connections = 0
    cold_retained = replay_idempotent = 0
    fourth_order_false_decisive = fourth_order_wrong = fourth_order_abstained = 0
    losses = []
    checkpoint_bytes = []
    max_gates = 0
    trained_seconds = direct_seconds = 0.0

    for seed in SEEDS:
        for triple in TRIPLES:
            for novelty in (0, 1):
                examples = samples(seed, triple, novelty)
                before = time.perf_counter()
                circuit = DirectWeightCircuit()
                symbolic = ExactSymbolicANF()
                no_growth = DirectWeightCircuit(max_degree=2)
                for c, a, reward in examples:
                    circuit.observe(c, a, reward)
                    symbolic.observe(c, a, reward)
                    no_growth.observe(c, a, reward)
                target = true_choice(seed, triple, novelty, TRANSFER)
                pre = circuit.choose(TRANSFER)
                if novelty:
                    pre_novel_wrong += int(pre != target)
                    pre_novel_wrong_decisive += int(pre is not None and pre != target)
                    pre_novel_bad_reward += int(
                        circuit.predict_reward(TRANSFER, 1) !=
                        world_reward(seed, triple, novelty, TRANSFER, 1))
                else:
                    assert pre == target
                assert pre == symbolic.choose(TRANSFER)
                witness = (triple, 1, world_reward(seed, triple, novelty, triple, 1))
                for arm in (circuit, symbolic, no_growth):
                    arm.observe(*witness)
                assert circuit.choose(TRANSFER) == symbolic.choose(TRANSFER)
                assert circuit.choose(TRANSFER) == target
                for a in (0, 1):
                    assert circuit.predict_reward(TRANSFER, a) == (
                        world_reward(seed, triple, novelty, TRANSFER, a))
                assert circuit.new_triple_gates == novelty
                new_triple_connections += circuit.new_triple_gates
                assert circuit.gate_count <= 30
                max_gates = max(max_gates, circuit.gate_count)
                saved = circuit.snapshot()
                checkpoint_bytes.append(len(saved))
                restored = DirectWeightCircuit.restore(saved)
                cold_retained += (restored.snapshot() == saved and
                                  restored.choose(TRANSFER) == target)
                for c, a in ((0, 0), (1, 0), (4, 1), (12, 1)):
                    restored.observe(c, a, world_reward(seed, triple, novelty, c, a))
                replay_idempotent += restored.snapshot() == saved
                if novelty:
                    # A fourth-order interaction is outside the frozen grammar.
                    true_negative = true_choice(seed, triple, novelty, TRANSFER,
                                                fourth_order=True)
                    predicted = restored.choose(TRANSFER)
                    fourth_order_wrong += predicted != true_negative
                    fourth_order_false_decisive += (
                        predicted is not None and predicted != true_negative)
                    restored.observe(TRANSFER, 1,
                                     world_reward(seed, triple, novelty,
                                                  TRANSFER, 1, fourth_order=True))
                    assert restored.unsafe
                    fourth_order_abstained += restored.choose(TRANSFER) is None
                direct_seconds += time.perf_counter() - before
                decisive += target is not None
                ties += target is None
                guesses = (circuit.choose(TRANSFER), symbolic.choose(TRANSFER),
                           no_growth.choose(TRANSFER),
                           DirectWeightCircuit().choose(TRANSFER))
                for k, v in zip(("weight_written", "exact_symbolic",
                                 "no_growth", "state_erased"), guesses):
                    scores[k] += v == target

                before_train = time.perf_counter()
                conventional = TrainedMLPControl()
                conventional.fit(examples + (witness,), triple)
                losses.append(conventional.fit_loss)
                scores["trained_mlp"] += conventional.choose(TRANSFER) == target
                trained_seconds += time.perf_counter() - before_train

    assert decisive + ties == 128
    assert scores["weight_written"] == scores["exact_symbolic"] == 128
    assert (pre_novel_wrong, pre_novel_bad_reward) == (64, 64)
    assert (new_triple_connections, cold_retained, replay_idempotent) == (64, 128, 128)
    assert (fourth_order_wrong, fourth_order_abstained) == (64, 64)

    return {
        "schema": "wsp03.public-dev-result.v1",
        "classification": "DEV_MECHANISM_IF_TESTS_PASS__SCIENCE_UNVERIFIED",
        "experiment": "WSP-03", "worlds": 128, "seeds": list(SEEDS),
        "triple_masks": list(TRIPLES), "public_baseline_observations": 22,
        "public_triple_witness_observations": 1,
        "transfer_context": TRANSFER,
        "after_witness_exact_policy_including_true_ties": scores,
        "decisive_worlds": decisive, "true_tie_worlds": ties,
        "before_witness_unmodeled_triple": {
            "wrong_policy_worlds": pre_novel_wrong,
            "wrong_confident_actions": pre_novel_wrong_decisive,
            "wrong_binary_reward_predictions_action1": pre_novel_bad_reward,
            "total_novel_worlds": 64,
        },
        "new_connection_compilation": {
            "new_3way_cells_total": new_triple_connections,
            "max_dynamic_cells_observed": max_gates,
            "connections_per_new_cell": 4,
            "output_combiner": "fixed XOR parity readout",
            "gradient_steps": 0,
            "max_degree": 3,
            "max_gates_per_action": 15,
            "binary_connection_weights_are_directly_written": True,
        },
        "retention": {
            "cold_exact_recoveries": cold_retained,
            "identical_checkpoint_after_observed_replay": replay_idempotent,
            "checkpoint_min_bytes": min(checkpoint_bytes),
            "checkpoint_max_bytes": max(checkpoint_bytes),
        },
        "degree_4_negative": {
            "cases": 64,
            "wrong_policy_without_four_way_witness": fourth_order_wrong,
            "wrong_confident_actions_without_witness": fourth_order_false_decisive,
            "post_genuine_witness_fail_closed_abstentions": fourth_order_abstained,
            "recovery_count": 0,
        },
        "trained_control": {
            "architecture": "5-10-1 tanh/sigmoid",
            "float_trainable_parameters": 71,
            "full_batch_steps_per_world": 512,
            "seed": 17, "learning_rate": 0.05,
            "mean_final_training_bce": sum(losses) / len(losses),
            "matched_total_compute": False,
            "independently_converged_strongest": False,
        },
        "wall_clock_seconds": {
            "direct_including_restore_and_negative": round(direct_seconds, 6),
            "trained_including_fit": round(trained_seconds, 6),
            "end_to_end": round(time.perf_counter() - started, 6),
            "note": "Single CI host Python dev timing, not cross-model performance parity or whole-system compute proof.",
        },
        "interpretation": "The circuit writes new binary conjunction weights from actual public reward residuals within a known bounded grammar; exact symbolic solver ties. New fourth-order mechanisms remain undiscoverable at degree 3. Synthetic author-visible data are not independent science.",
        "provenance_note": "No model API, no production integration, no independent first-use."
    }


if __name__ == "__main__":
    print(json.dumps(run_dev(), sort_keys=True, indent=2))
