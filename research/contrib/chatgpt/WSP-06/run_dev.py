"""WSP-06 reproducible synthetic DEV, not independent scientific first use."""
from __future__ import annotations

import json
import pathlib
import sys
import time

from numeric_circuit import (
    CompleteTaskCircuit, READ_TAPE, LEARN_TAPE, PLASTIC_COUNT,
    FIXED_COUNT, PROGRAM_SHA256, N
)

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "WSP-05"))
from causal_signature import (
    SEEDS, PublicWorld, ExactSymbolicSignature, TrainedMLPControl,
    OneStepControl, IdentityControl
)


def run_dev() -> dict:
    start = time.perf_counter()
    scores = {k:0 for k in ("numeric_weight_circuit","exact_symbolic",
                            "converged_trained_mlp","one_step","identity",
                            "erased_numeric")}
    compiled_seconds = fit_seconds = 0.0
    all_programmed = ablate_transition = ablate_signature = 0
    cold = replay = isolation = shifted_wrong = shifted_confident = shifted_abstain = 0
    trained_worlds = steps = 0
    mean_losses: list[float] = []
    weights_active: list[int] = []
    checkpoints: list[int] = []
    predictions = 0

    for seed in SEEDS:
        w = PublicWorld(seed)
        events = w.public_experiences()
        assert len(events) == 20
        started = time.perf_counter()
        net, sym, one, identity = (
            CompleteTaskCircuit(), ExactSymbolicSignature(),
            OneStepControl(), IdentityControl())
        for e in events:
            net.observe(*e)
            for other in (sym,one,identity):
                other.observe(*e)
        assert net.weights["F"] == [[0]]
        assert net.weights["C0"] == [[1]*N]
        assert net.weights["C1"] == [[1]*4]
        all_programmed += (
            sum(sum(row) for row in net.weights["T0"]) == N and
            net.learned_positive_synapses() > 0)
        weights_active.append(net.learned_positive_synapses())
        saved = net.snapshot()
        checkpoints.append(len(saved))
        restored = CompleteTaskCircuit.restore(saved)
        cold += (restored.snapshot() == saved and
                 restored.programmed_sha256() == net.programmed_sha256())
        for e in (events[0],events[11],events[12],events[-1]):
            restored.observe(*e)
        replay += restored.snapshot() == saved

        no_t0 = CompleteTaskCircuit.restore(saved)
        no_t0.weights["T0"] = [[0]*12 for _ in range(12)]
        no_sig = CompleteTaskCircuit.restore(saved)
        no_sig.weights["SIG"] = [[0]*3 for _ in range(4)]
        ablate_transition += all(no_t0.predict_a1(s) is None for s in w.test)
        ablate_signature += all(no_sig.predict_a1(s) is None for s in w.test)
        # Separate world/circuit, same raw identity namespace but not state.
        other = CompleteTaskCircuit()
        different = PublicWorld((seed+1) % len(SEEDS))
        for e in different.public_experiences():
            other.observe(*e)
        isolation += (saved == net.snapshot() and
                      net.programmed_sha256() != other.programmed_sha256())
        compiled_seconds += time.perf_counter() - started

        examples = tuple((sym.signature(e[0]),e[2]) for e in events[12:])
        assert len(examples) == 8 and all(s is not None for s,y in examples)
        started_train = time.perf_counter()
        trained = TrainedMLPControl()
        trained.fit(examples)
        fit_seconds += time.perf_counter() - started_train
        mean_losses.append(trained.loss)
        trained_worlds += trained.converged
        steps += trained.steps

        started = time.perf_counter()
        for s in w.test:
            correct = w.outcome(s,1)[2]
            sig = sym.signature(s)
            assert sig is not None
            predictions += 1
            pred = {
                "numeric_weight_circuit": net.predict_a1(s),
                "exact_symbolic": sym.predict_a1(s),
                "converged_trained_mlp": trained.predict_a1(sig),
                "one_step": one.predict_a1(s),
                "identity": identity.predict_a1(s),
                "erased_numeric": CompleteTaskCircuit().predict_a1(s)
            }
            for k,v in pred.items():
                scores[k] += v == correct
            assert pred["numeric_weight_circuit"] == pred["exact_symbolic"] == correct
            corrupted_reward = w.outcome(s,1,heldout_shift=True)[2]
            shifted_wrong += pred["numeric_weight_circuit"] != corrupted_reward
            shifted_confident += (pred["numeric_weight_circuit"] is not None and
                                  pred["numeric_weight_circuit"] != corrupted_reward)
        net.observe(*w.outcome(w.test[0],1,heldout_shift=True))
        assert net.weights["F"] == [[1]]
        shifted_abstain += sum(net.predict_a1(s) is None for s in w.test)
        assert CompleteTaskCircuit.restore(net.snapshot()).weights["F"] == [[1]]
        compiled_seconds += time.perf_counter() - started

    assert predictions == 128 and all_programmed == cold == replay == 32
    assert isolation == ablate_transition == ablate_signature == 32
    assert (shifted_wrong,shifted_confident,shifted_abstain) == (128,128,128)
    assert scores["numeric_weight_circuit"] == scores["exact_symbolic"] == 128
    assert scores["converged_trained_mlp"] == 128 and trained_worlds == 32
    assert scores["one_step"] == 64
    assert scores["identity"] == scores["erased_numeric"] == 0

    return {
        "schema":"wsp06.public-dev-result.v1",
        "classification":"ENGINEERING_DEV_IF_EXACT_CI_PASS__SCIENTIFIC_UNVERIFIED",
        "worlds":32, "raw_interventions_per_world":20,
        "unseen_action1_reward_queries":predictions,
        "score_abstentions_count_as_incorrect":scores,
        "compiled_numeric_circuit":{
            "generic_read_tape_ops":len(READ_TAPE),
            "generic_learn_tape_ops":len(LEARN_TAPE),
            "fixed_scalar_weights":FIXED_COUNT,
            "plastic_scalar_weights":PLASTIC_COUNT,
            "total_initial_and_writable_scalar_slots":FIXED_COUNT+PLASTIC_COUNT,
            "program_sha256":PROGRAM_SHA256,
            "positive_synapses_min":min(weights_active),
            "positive_synapses_max":max(weights_active),
            "correctly_compiled_full_12_transition_graphs":all_programmed,
            "gradient_updates":0,
            "identity_encoding":"fixed raw state ID to one-hot only",
            "task_specific_python_signature_or_reward_lookup":False,
            "generic_numpy_or_torch_required":False
        },
        "retention":{
            "cold_exact_restore_worlds":cold,
            "four_observation_replay_idempotent_worlds":replay,
            "cross_world_state_isolation_worlds":isolation,
            "checkpoint_min_bytes":min(checkpoints),
            "checkpoint_max_bytes":max(checkpoints)
        },
        "ablations":{
            "zero_transition_memory_blocks_all_4_predictions_worlds":ablate_transition,
            "zero_signature_weight_layer_blocks_all_4_predictions_worlds":ablate_signature,
            "experience_erased_rewards_correct":scores["erased_numeric"]
        },
        "unseen_heldout_only_shift":{
            "wrong_predictions_before_shift_witness":shifted_wrong,
            "wrong_confident_predictions_before_shift_witness":shifted_confident,
            "abstentions_after_one_public_contradiction":shifted_abstain,
            "successfully_recovered_new_shifted_rules":0
        },
        "fully_trained_conventional_control":{
            "architecture":"2-8-1 tanh sigmoid",
            "float_parameters":33,
            "optimizer":"full-batch Adam",
            "seed":17,"lr":0.03,
            "stop_bce":0.02,
            "converged_worlds":trained_worlds,
            "gradient_steps_total":steps,
            "mean_final_train_bce":sum(mean_losses)/len(mean_losses),
            "matched_public_information":True,
            "matched_end_to_end_compute":False
        },
        "wall_clock_python_seconds":{
            "numeric_compilation_cold_ablations_negatives":round(compiled_seconds,6),
            "trained_control_fit":round(fit_seconds,6),
            "total":round(time.perf_counter()-start,6),
            "interpretation":"Not matched FLOPs, execution overhead or causal feature-construction costs."
        },
        "scientific_limit":"A complete bounded WSP05 task solver is represented by numeric weights and a generic local-plasticity tape, but the external Python interpreter and its learning primitives remain necessary. The prior fixed two-hop signature wiring is supplied and symbolic/trained baselines tie; no full general intelligence or end-to-end efficiency superiority demonstrated."
    }


if __name__ == "__main__":
    print(json.dumps(run_dev(),sort_keys=True,indent=2))
