"""Frozen WSP-07 public synthetic DEV comparison; no independent first-use."""
from __future__ import annotations

import json
import pathlib
import sys
import time

from threshold_graph import (
    INPUT_COUNT, PLASTIC_COUNT, SPEC, CompiledPlasticCircuit,
)

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/"WSP-05"))
sys.path.insert(0,str(ROOT.parent/"WSP-06"))
from causal_signature import (
    SEEDS,PublicWorld,ExactSymbolicSignature,OneStepControl,
    IdentityControl,TrainedMLPControl,
)
from numeric_circuit import CompleteTaskCircuit


def run_dev() -> dict:
    start=time.perf_counter()
    scores={name:0 for name in (
        "homogeneous_neural_graph","wsp06_opcode_numeric",
        "exact_symbolic","converged_33param_trained_mlp",
        "one_step","state_id_memorizer","erased")}
    world_qualified=cold=replayed=isolated=ablate_T=ablate_SIG=ablate_C1=0
    invalid_confident=after_fault_abstain=0
    gates_positive=[]
    checkpoint_sizes=[]
    train_steps=trained_worlds=0
    train_losses=[]
    component_seconds=trained_seconds=0.0

    for seed in SEEDS:
        env=PublicWorld(seed)
        observations=env.public_experiences()
        assert len(observations)==20
        t0=time.perf_counter()
        circuit=CompiledPlasticCircuit()
        prior=CompleteTaskCircuit()
        exact=ExactSymbolicSignature()
        one_step=OneStepControl()
        identity=IdentityControl()
        for event in observations:
            circuit.observe(*event)
            for m in (prior,exact,one_step,identity):
                m.observe(*event)
        assert circuit.fault_value()==0
        world_qualified+=1
        positive=circuit.learned_positive_weights()
        gates_positive.append(positive)
        assert positive>=34
        checkpoint=circuit.snapshot()
        checkpoint_sizes.append(len(checkpoint))
        restored=CompiledPlasticCircuit.restore(checkpoint)
        cold+=int(restored.snapshot()==checkpoint and
                  restored.programmed_sha256()==circuit.programmed_sha256())
        for e in (observations[0],observations[11],
                  observations[12],observations[-1]):
            restored.observe(*e)
        replayed+=int(restored.snapshot()==checkpoint)

        # Fault-isolated model stores only its own numeric synapses.
        alternate=PublicWorld((seed+1)%len(SEEDS))
        other=CompiledPlasticCircuit()
        for e in alternate.public_experiences(): other.observe(*e)
        isolated+=int(circuit.snapshot()==checkpoint and
                      other.programmed_sha256()!=circuit.programmed_sha256())

        without_T=CompiledPlasticCircuit.restore(checkpoint)
        for slot in SPEC.plastic_indices[:144]:
            without_T.weights[slot]=0
        ablate_T+=int(all(without_T.predict_a1(s) is None for s in env.test))
        without_SIG=CompiledPlasticCircuit.restore(checkpoint)
        for slot in SPEC.signature_indices:
            without_SIG.weights[slot]=0
        ablate_SIG+=int(all(without_SIG.predict_a1(s) is None for s in env.test))
        without_C1=CompiledPlasticCircuit.restore(checkpoint)
        for slot in SPEC.plastic_indices[172:176]:
            without_C1.weights[slot]=0
        ablate_C1+=int(all(without_C1.predict_a1(s) is None for s in env.test))
        component_seconds+=time.perf_counter()-t0

        examples=tuple((exact.signature(e[0]),e[2])
                       for e in observations[12:])
        assert len(examples)==8 and all(s is not None for s,y in examples)
        train_t=time.perf_counter()
        model=TrainedMLPControl()
        model.fit(examples)
        trained_seconds+=time.perf_counter()-train_t
        train_steps+=model.steps
        trained_worlds+=int(model.converged)
        train_losses.append(model.loss)

        infer_t=time.perf_counter()
        for state in env.test:
            truth=env.outcome(state,1)[2]
            signature=exact.signature(state)
            assert signature is not None
            predictions={
                "homogeneous_neural_graph":circuit.predict_a1(state),
                "wsp06_opcode_numeric":prior.predict_a1(state),
                "exact_symbolic":exact.predict_a1(state),
                "converged_33param_trained_mlp":model.predict_a1(signature),
                "one_step":one_step.predict_a1(state),
                "state_id_memorizer":identity.predict_a1(state),
                "erased":CompiledPlasticCircuit().predict_a1(state),
            }
            assert (predictions["homogeneous_neural_graph"]==
                    predictions["wsp06_opcode_numeric"]==
                    predictions["exact_symbolic"]==truth)
            for key,guess in predictions.items():
                scores[key]+=int(guess==truth)
            hostile=env.outcome(state,1,heldout_shift=True)[2]
            invalid_confident+=int(
                predictions["homogeneous_neural_graph"] is not None and
                predictions["homogeneous_neural_graph"]!=hostile)
        # One real action consequence contradicts a previously compiled
        # signature rule; numeric fault weight must suppress all inferences.
        circuit.observe(*env.outcome(env.test[0],1,heldout_shift=True))
        assert circuit.fault_value()==1
        after_fault_abstain+=sum(circuit.predict_a1(s) is None for s in env.test)
        assert CompiledPlasticCircuit.restore(circuit.snapshot()).fault_value()==1
        component_seconds+=time.perf_counter()-infer_t

    assert world_qualified==cold==replayed==isolated==32
    assert ablate_T==ablate_SIG==ablate_C1==32
    assert invalid_confident==after_fault_abstain==128
    assert scores["homogeneous_neural_graph"]==128
    assert scores["wsp06_opcode_numeric"]==128
    assert scores["exact_symbolic"]==128
    assert scores["converged_33param_trained_mlp"]==128
    assert scores["one_step"]==64
    assert scores["state_id_memorizer"]==scores["erased"]==0
    assert trained_worlds==32

    return {
        "schema":"wsp07.public-dev-result.v1",
        "classification":"DEV_ENGINEERING_ONLY_IF_FINAL_DUAL_OS_CI_PASS__SCIENCE_UNVERIFIED",
        "worlds":32,"public_events_each":20,"unseen_action1_queries":128,
        "abstention_counts_as_error":True,
        "heldout_binary_accuracy":scores,
        "compiled_neural_control":{
            "input_neurons":INPUT_COUNT,
            "total_neuron_nodes":len(SPEC.threshold),
            "fixed_numeric_coefficients":len(SPEC.fixed_indices),
            "plastic_numeric_coefficients":PLASTIC_COUNT,
            "total_coefficient_slots":len(SPEC.initial_weights),
            "direct_gradient_steps":0,
            "persistent_nonzero_plastic_weights_min":min(gates_positive),
            "persistent_nonzero_plastic_weights_max":max(gates_positive),
            "local_plasticity_rules":len(SPEC.plastic_rules),
            "numerical_graph_edges":len(SPEC.edges),
            "program_sha256":SPEC.graph_sha256,
            "runtime_task_specific_opcode_dispatch":False,
            "runtime_task_specific_python_state_maps":False,
            "software_generic_neural_vm_remains":True,
        },
        "retention":{
            "cold_restores_exact":cold,"repeat_public_events_idempotent":replayed,
            "separate_world_weight_isolation":isolated,
            "checkpoint_min_bytes":min(checkpoint_sizes),
            "checkpoint_max_bytes":max(checkpoint_sizes),
        },
        "numeric_ablations":{
            "without_successor_memory_abstains_all_worlds":ablate_T,
            "without_signature_fixed_edges_abstains_all_worlds":ablate_SIG,
            "without_action1_coverage_abstains_all_worlds":ablate_C1,
        },
        "out_of_family_negative":{
            "hidden_label_inversion_wrong_confident_before_witness":invalid_confident,
            "after_one_actual_contradiction_abstentions":after_fault_abstain,
            "recovered_unseen_shifted_rules":0,
            "identifiability":"20 public events are identical before hidden-only shift; never infer unseen reward labels from public clues that cannot distinguish worlds.",
        },
        "conventional_control":{
            "converged_worlds":trained_worlds,
            "trainable_float_parameters":33,
            "gradient_optimizer":"full-batch Adam",
            "gradient_steps_total":train_steps,
            "loss_stop_bce":0.02,
            "mean_training_bce":sum(train_losses)/len(train_losses),
            "matched_action_observations":True,
            "matched_whole_process_compute":False,
        },
        "wall_clock_dev_seconds":{
            "compiled_circuit_training_cold_ablations_negatives":round(component_seconds,6),
            "trained_baseline_fit_only":round(trained_seconds,6),
            "whole_dev_runner":round(time.perf_counter()-start,6),
            "warning":"Unlike workloads; includes more work in numeric component. No speedup or cost superiority can be claimed.",
        },
        "scientific_limit":"Fixed two-hop signature inductive prior and local Hebbian OR operator were compiled by Python to a numeric graph. Generic software interpreter still exists. Exact symbolic and fully converged trained controls tie. Only public synthetic test worlds, not independent general cognition.",
    }


if __name__=="__main__":
    print(json.dumps(run_dev(),sort_keys=True,indent=2))
