"""WSP-05 public synthetic DEV scorecard, no independent science first-use."""
from __future__ import annotations
import json
import time

from causal_signature import (
    SEEDS, PublicWorld, DirectSignatureCircuit, ExactSymbolicSignature,
    OneStepControl, IdentityControl, TrainedMLPControl
)


def run_dev() -> dict:
    start = time.perf_counter()
    score = dict(direct_weight=0, exact_symbolic=0, one_step=0,
                 state_id_memorizer=0, erased=0, trained_mlp=0)
    wrong_confident = 0
    one_step_abstain = 0
    erased_abstain = 0
    raw_identity_abstain = 0
    learned_gates = learned_binary_connections = 0
    cold_ok = replay_ok = isolation_ok = 0
    negative_wrong_pre = negative_confident_pre = negative_abstain_post = 0
    mlp_converged = mlp_steps = 0
    mlp_losses = []
    sample_bytes = []
    direct_seconds = mlp_seconds = 0.0

    for seed in SEEDS:
        w = PublicWorld(seed)
        events = w.public_experiences()
        t = time.perf_counter()
        direct, symbolic, one, identity = (
            DirectSignatureCircuit(), ExactSymbolicSignature(),
            OneStepControl(), IdentityControl())
        for e in events:
            for system in (direct, symbolic, one, identity):
                system.observe(*e)
        assert len(events) == 20
        assert len(direct.gates) == 4 and direct.learned_connections == 16
        learned_gates += len(direct.gates)
        learned_binary_connections += direct.learned_connections
        saved = direct.snapshot()
        sample_bytes.append(len(saved))
        restored = DirectSignatureCircuit.restore(saved)
        cold_ok += (restored.snapshot() == saved and
                    restored.programmed_sha256() == direct.programmed_sha256())
        for e in (events[0], events[11], events[12], events[-1]):
            restored.observe(*e)
        replay_ok += restored.snapshot() == saved

        # Cross-world IDs are not shared state. A second model cannot change
        # the first model's compact weights or checkpoint.
        other = PublicWorld((seed+1) % len(SEEDS))
        independent = DirectSignatureCircuit()
        for e in other.public_experiences():
            independent.observe(*e)
        isolation_ok += independent.snapshot() != b"" and direct.snapshot() == saved
        direct_seconds += time.perf_counter()-t

        examples = []
        for event in events[12:]:
            sig = symbolic.signature(event[0])
            assert sig is not None
            examples.append((sig, event[2]))
        training = tuple(examples)
        started_train = time.perf_counter()
        trained = TrainedMLPControl()
        trained.fit(training)
        mlp_seconds += time.perf_counter() - started_train
        mlp_losses.append(trained.loss)
        mlp_converged += trained.converged
        mlp_steps += trained.steps

        t = time.perf_counter()
        for s in w.test:
            actual = w.outcome(s, 1)[2]
            sig = symbolic.signature(s)
            assert sig is not None
            preds = {
                "direct_weight": direct.predict_a1(s),
                "exact_symbolic": symbolic.predict_a1(s),
                "one_step": one.predict_a1(s),
                "state_id_memorizer": identity.predict_a1(s),
                "erased": DirectSignatureCircuit().predict_a1(s),
                "trained_mlp": trained.predict_a1(sig)
            }
            assert preds["direct_weight"] == preds["exact_symbolic"] == actual
            for k in score:
                score[k] += preds[k] == actual
            wrong_confident += preds["direct_weight"] is not None and preds["direct_weight"] != actual
            one_step_abstain += preds["one_step"] is None
            raw_identity_abstain += preds["state_id_memorizer"] is None
            erased_abstain += preds["erased"] is None
            unseen_shift = w.outcome(s, 1, heldout_shift=True)[2]
            negative_wrong_pre += preds["direct_weight"] != unseen_shift
            negative_confident_pre += preds["direct_weight"] is not None and preds["direct_weight"] != unseen_shift

        # Observe ONE truly shifted action1 outcome. Its contradiction
        # cannot justify assuming the other three hidden labels are flipped.
        direct.observe(*w.outcome(w.test[0], 1, heldout_shift=True))
        assert direct.unsafe
        assert len(direct.gates) == 4
        for s in w.test:
            negative_abstain_post += direct.predict_a1(s) is None
        assert DirectSignatureCircuit.restore(direct.snapshot()).unsafe
        direct_seconds += time.perf_counter() - t

    assert score["direct_weight"] == score["exact_symbolic"] == 128
    assert score["one_step"] == 64
    assert score["state_id_memorizer"] == score["erased"] == 0
    assert (learned_gates, learned_binary_connections) == (128, 512)
    assert (cold_ok, replay_ok, isolation_ok) == (32, 32, 32)
    assert (negative_wrong_pre, negative_confident_pre, negative_abstain_post) == (
        128, 128, 128)
    assert (one_step_abstain, raw_identity_abstain, erased_abstain) == (64, 128, 128)

    return {
        "schema": "wsp05.public-dev-result.v1",
        "classification": "DEVELOPMENT_MECHANISM_PASS_IF_CI_PASS__SCIENCE_UNVERIFIED",
        "worlds": 32, "opaque_state_id_per_world": 12,
        "public_action0_interventions_per_world": 12,
        "public_action1_training_interventions_per_world": 8,
        "heldout_action1_reward_queries": 128,
        "all_model_scores_exact_binary_reward_abstention_is_incorrect": score,
        "public_learner": {
            "binary_threshold_signature_gates_created_total": learned_gates,
            "binary_connection_weights_written_total": learned_binary_connections,
            "connection_weights_per_gate": 4,
            "trainable_gradient_steps_direct": 0,
            "latent_class_labels_or_reward_generator_used_in_predictor": False,
            "prewitness_confident_wrong": wrong_confident
        },
        "ablations": {
            "one_step_abstentions": one_step_abstain,
            "identity_abstentions": raw_identity_abstain,
            "erased_state_abstentions": erased_abstain
        },
        "cold_memory": {
            "exact_cold_restores": cold_ok,
            "idempotent_experience_replays": replay_ok,
            "separate_world_isolation_receipts": isolation_ok,
            "checkpoint_min_bytes": min(sample_bytes),
            "checkpoint_max_bytes": max(sample_bytes)
        },
        "out_of_family_holdout_reward_shift": {
            "worlds": 32,
            "prewitness_wrong_predictions": negative_wrong_pre,
            "prewitness_wrong_confident_predictions": negative_confident_pre,
            "public_negative_action1_witness_per_world": 1,
            "postwitness_abstentions": negative_abstain_post,
            "new_shifted_rules_inferred": 0,
            "information_limit": "No public observation before the witness distinguishes four original heldout rewards from the flipped alternative; after one witness the other three remain unidentifiable."
        },
        "fully_trained_conventional_control": {
            "architecture": "2-8-1 tanh sigmoid",
            "float_trainable_parameters": 33,
            "optimizer": "deterministic full-batch Adam",
            "max_gradient_steps_per_world": 2048,
            "gradient_steps_total": mlp_steps,
            "loss_stop": 0.02,
            "converged_worlds": mlp_converged,
            "mean_train_bce": sum(mlp_losses)/len(mlp_losses),
            "worlds_with_unqualified_baseline": len(SEEDS)-mlp_converged,
            "matched_training_examples": True,
            "matched_whole_process_compute": False
        },
        "wall_clock_seconds": {
            "direct_circuit_plus_cold_negative": round(direct_seconds, 6),
            "trained_fit": round(mlp_seconds, 6),
            "whole_dev_runner": round(time.perf_counter()-start, 6),
            "interpretation": "Single-process Python timings not matched FLOPs or shared system costs."
        },
        "science_limit": "This task induces new action-consequence signatures invariant to opaque object IDs, not unknown computational primitives. The exact symbolic comparator must tie; public author-visible synthetic world lacks independent first-use. No evidence of superiority over symbolic or general intelligence."
    }


if __name__ == "__main__":
    print(json.dumps(run_dev(), sort_keys=True, indent=2))
