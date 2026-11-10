"""WSP-08 public-synthetic frozen 36-world adaptive representation DEV report."""
from __future__ import annotations
import json
import time

from graph import (
    SEEDS,MODES,SPEC,N,INPUT_N,PLASTIC_COUNT,PublicWorld,GrowingSynapseCircuit
)
from controls import SymbolicAdaptive,TrainedMLP


def run_dev()->dict:
    start=time.perf_counter()
    scores={k:0 for k in ("grown_numeric_representation",
                           "exact_symbolic_adaptive",
                           "fixed_one_hop","fixed_two_hop",
                           "fully_trained_41param_mlp",
                           "experience_erased")}
    selected={1:0,2:0,3:0}
    depth2_writes=depth3_writes=0
    positive=[]
    cold=replay=isolation=ablateT=ablateA1=0
    wrong_confident=after_negative_abstain=0
    compiled_seconds=trained_fit_seconds=0.0
    train_steps=train_converged=0
    train_losses=[]
    checkpoints=[]
    per_mode={str(mode):{"worlds":0,"correct_numeric":0,
                          "correct_trained":0} for mode in MODES}
    total=0

    for seed in SEEDS:
        for mode in MODES:
            w=PublicWorld(seed,mode)
            events=w.public_events()
            assert len(events)==40 and len(w.test)==8
            t0=time.perf_counter()
            numeric=GrowingSynapseCircuit()
            exact=SymbolicAdaptive(3)
            fixed1=SymbolicAdaptive(1)
            fixed2=SymbolicAdaptive(2)
            for event in events:
                numeric.observe(*event)
                for m in (exact,fixed1,fixed2):
                    m.observe(*event)
            assert numeric.fault==0
            assert numeric.depth==exact.active_depth()==mode
            selected[numeric.depth]+=1
            depth2_writes+=numeric.weights[SPEC.depth2_slot]
            depth3_writes+=numeric.weights[SPEC.depth3_slot]
            positive.append(numeric.active_plastic())
            saved=numeric.snapshot()
            checkpoints.append(len(saved))
            restored=GrowingSynapseCircuit.restore(saved)
            cold+=int(restored.snapshot()==saved and
                      restored.programmed_sha256()==numeric.programmed_sha256())
            for e in (events[0],events[23],events[24],events[-1]):
                restored.observe(*e)
            replay+=int(restored.snapshot()==saved)

            noT=GrowingSynapseCircuit.restore(saved)
            for slot in SPEC.successor_slots:
                noT.weights[slot]=0
            ablateT+=int(all(noT.predict_a1(s) is None for s in w.test))
            noA1=GrowingSynapseCircuit.restore(saved)
            for slot in SPEC.a1_coverage_slots:
                noA1.weights[slot]=0
            ablateA1+=int(all(noA1.predict_a1(s) is None for s in w.test))
            unrelated=GrowingSynapseCircuit()
            other=PublicWorld((seed+1)%len(SEEDS),mode)
            for e in other.public_events():
                unrelated.observe(*e)
            isolation+=int(numeric.snapshot()==saved and
                           numeric.programmed_sha256()!=unrelated.programmed_sha256())
            compiled_seconds+=time.perf_counter()-t0

            examples=tuple((exact.signature(e[0],3),e[2]) for e in events[24:])
            assert len(examples)==16 and all(sig is not None for sig,y in examples)
            ttrain=time.perf_counter()
            mlp=TrainedMLP()
            mlp.fit(examples)
            trained_fit_seconds+=time.perf_counter()-ttrain
            train_converged+=int(mlp.converged)
            train_steps+=mlp.steps
            train_losses.append(mlp.loss)

            t0=time.perf_counter()
            per_mode[str(mode)]["worlds"]+=1
            for s in w.test:
                correct=w.outcome(s,1)[2]
                sig=exact.signature(s,3)
                guesses={
                    "grown_numeric_representation":numeric.predict_a1(s),
                    "exact_symbolic_adaptive":exact.predict_a1(s),
                    "fixed_one_hop":fixed1.predict_a1(s),
                    "fixed_two_hop":fixed2.predict_a1(s),
                    "fully_trained_41param_mlp":mlp.predict(sig),
                    "experience_erased":GrowingSynapseCircuit().predict_a1(s),
                }
                assert guesses["grown_numeric_representation"]==guesses["exact_symbolic_adaptive"]==correct
                for name,pred in guesses.items():
                    scores[name]+=int(pred==correct)
                per_mode[str(mode)]["correct_numeric"]+=int(guesses["grown_numeric_representation"]==correct)
                per_mode[str(mode)]["correct_trained"]+=int(guesses["fully_trained_41param_mlp"]==correct)
                total+=1
                negative=w.outcome(s,1,shift=True)[2]
                wrong_confident+=int(
                    guesses["grown_numeric_representation"] is not None and
                    guesses["grown_numeric_representation"]!=negative)
            numeric.observe(*w.outcome(w.test[0],1,shift=True))
            assert numeric.fault==1
            after_negative_abstain+=sum(numeric.predict_a1(s) is None for s in w.test)
            assert GrowingSynapseCircuit.restore(numeric.snapshot()).fault==1
            compiled_seconds+=time.perf_counter()-t0

    assert total==288
    assert scores["grown_numeric_representation"]==scores["exact_symbolic_adaptive"]==288
    assert scores["fixed_one_hop"]==96 and scores["fixed_two_hop"]==192
    assert scores["experience_erased"]==0
    assert selected=={1:12,2:12,3:12}
    assert (depth2_writes,depth3_writes)==(24,12)
    assert (cold,replay,isolation,ablateT,ablateA1)==(36,36,36,36,36)
    assert wrong_confident==after_negative_abstain==288

    return {
        "schema":"wsp08.public-dev-result.v1",
        "classification":"ENGINEERING_DEV_IF_FULL_FINAL_CI_PASS__SCIENCE_UNVERIFIED",
        "worlds":36,"seeds":12,"modes":[1,2,3],
        "public_action0_transitions_per_world":24,
        "public_action1_training_events_per_world":16,
        "heldout_action1_outcomes_total":total,
        "abstention_counts_wrong":True,
        "correct_heldout_rewards":scores,
        "per_mode_accuracy":per_mode,
        "representation_growth":{
            "learned_depth_worlds":selected,
            "new_depth2_plastic_synapses_activated":depth2_writes,
            "new_depth3_plastic_synapses_activated":depth3_writes,
            "candidate_feature_family_max_hops":3,
            "programmed_candidate_hop_mechanism":True,
            "arbitrary_new_causal_operators_created":False,
            "gradient_steps_direct":0,
            "fixed_coefficient_slots":len(SPEC.fixed_indices),
            "writable_coefficient_slots":PLASTIC_COUNT,
            "total_weight_slots":len(SPEC.start_weights),
            "compiled_neuron_count":len(SPEC.threshold),
            "numeric_graph_edges":len(SPEC.edges),
            "synaptic_plasticity_rules":len(SPEC.rules),
            "neural_program_sha256":SPEC.graph_sha256,
            "min_positive_plastic_weights":min(positive),
            "max_positive_plastic_weights":max(positive),
            "runtime_custom_task_opcodes":False,
            "external_python_generic_neural_vm_still_required":True,
        },
        "retention":{
            "cold_exact_restores":cold,
            "repeated_experience_checkpoint_preservation":replay,
            "independent_world_isolation":isolation,
            "checkpoint_min_bytes":min(checkpoints),
            "checkpoint_max_bytes":max(checkpoints),
        },
        "ablations":{
            "zero_transition_memory_abstain_all_worlds":ablateT,
            "zero_action1_coverage_abstain_all_worlds":ablateA1,
        },
        "hidden_shift_negative":{
            "wrong_confident_rewards_before_heldout_witness":wrong_confident,
            "abstentions_after_one_true_contradiction":after_negative_abstain,
            "hidden_shift_rules_recovered":0,
            "information_limit":"The unobserved replica2 reward flip is indistinguishable from the unshifted world before a real replica2 outcome is observed.",
        },
        "trained_comparator":{
            "architecture":"3-8-1 tanh sigmoid",
            "trainable_float_coefficients":41,
            "optimizer":"full-batch Adam",
            "seed":17,"learning_rate":0.03,
            "BCE_stop_threshold":0.02,
            "maximum_steps_per_world":2048,
            "converged_worlds":train_converged,
            "unqualified_worlds":36-train_converged,
            "total_training_steps":train_steps,
            "mean_final_training_BCE":sum(train_losses)/len(train_losses),
            "same_public_action1_training_labels":True,
            "matched_process_compute":False,
        },
        "python_execution_seconds":{
            "numeric_training_inference_restore_ablation_negative":round(compiled_seconds,6),
            "conventional_MLP_fit_only":round(trained_fit_seconds,6),
            "complete_dev_runner":round(time.perf_counter()-start,6),
            "warning":"Workloads are not compute, energy, or whole-system matched; no speedup may be claimed.",
        },
        "science_limit":"Learns how deep a PREPROGRAMMED bounded 1-to-3-hop feature representation must be. Does not invent previously unavailable computational primitives. External public-authorized synthetic worlds cannot establish independent novel-world generalization, general intelligence, or superiority over strongest fully trained / symbolic baselines.",
    }


if __name__=="__main__":
    print(json.dumps(run_dev(),sort_keys=True,indent=2))
