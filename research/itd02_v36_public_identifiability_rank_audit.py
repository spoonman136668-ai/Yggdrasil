"""V36 frozen source-only information versus native decision-rank audit.

No new model or tuning. Original V35 selected-feedback training is reused.
Evaluator-only completions and full reward tables never reach learner or chooser.
"""
import hashlib
import itertools
import json
import subprocess
import time
import tracemalloc
from pathlib import Path

from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v29_observational_equivalence_audit import selected_map
from research.itd02_v35_action_conditioned_local_basis_audit import (
    WORLDS, reward_law, run, paired_controls, nonlearning_control,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS, PUBLIC_CUES, canonical
from yggdrasil.itd02_v22_shared_context_ring_dev import SharedContextRingDev, LEARNED_SCALARS

PARENT="d207cdc06ae1db303392dacfc42e4b0ac4686931"
PREREG="0360ed2f871afdacace182cfba8300ccfeacad85"
MODES=("v35_novelty","v22_shared_novelty","rls_novelty")
CONTEXTS=tuple(itertools.product(PUBLIC_CUES,ACTIONS))
PINS={
 "yggdrasil/itd02_native_task_bridge_dev.py":"71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
 "yggdrasil/itd02_local_ring_memory_dev.py":"1db0835d5c99456bcf99a013d4836f49314a9d39",
 "yggdrasil/itd02_v22_shared_context_ring_dev.py":"73dc4d7580f7f0b8ed8de1119b06504c44b0818f",
 "yggdrasil/itd02_v24_protected_dual_memory_dev.py":"9ef95a28e9060dd79105f51122d527351756a1e0",
 "yggdrasil/itd02_v25_unlabeled_return_dev.py":"f90e5029b121cbfc2e361f9e0941985eb1e69e3d",
 "yggdrasil/itd02_v26_calibrated_return_dev.py":"8a0417d34c6ba94a4eaef33d767da14a4a5c9709",
 "yggdrasil/itd02_v30_public_probe_policy_dev.py":"bcc1f0b4e2ec0fcd8b2af69dfb0e6d4d2ca27a4a",
 "yggdrasil/itd02_v32_source_surprise_probation_dev.py":"9252b554c25bfdc5b6adb733f94b0c3d2b2ec92e",
 "yggdrasil/itd02_v35_action_conditioned_ring_dev.py":"9a958c9bcae6e0ae588a0798f75216bdf79046c",
 "research/itd02_v35_action_conditioned_local_basis_audit.py":"9000000000000000000000000000000000000000",
}
def verify():
    root=Path(__file__).resolve().parents[1]
    git=lambda *a:subprocess.check_output(("git",)+a,cwd=root,text=True).strip()
    for pin in (PARENT,PREREG):
        assert git("merge-base","--is-ancestor",pin,"HEAD")=="",("WRONG_CHRONOLOGY",pin)
    for path,blob in PINS.items():
        assert git("hash-object",path)==blob,("PROTECTED_V35_BLOB_CHANGED",path)
    assert LEARNED_SCALARS==163 and len(CONTEXTS)==12

def finite_family_information(observed):
    """Compare only originally SELECTED legal feedback for known toy family."""
    histories={}
    for world in WORLDS:
        histories[world]=[round(reward_law(world,case),12) for case in observed]
    collisions=[]
    for i,x in enumerate(WORLDS):
        for y in WORLDS[i+1:]:
            indices=[j for j,(a,b) in enumerate(zip(histories[x],histories[y]))
                     if abs(a-b)>1e-12]
            if not indices:collisions.append([x,y])
    return {"original_base_feedback":histories,
            "observed_reward_history_sha":{w:hashlib.sha256(canonical(histories[w])).hexdigest()
                                          for w in WORLDS},
            "collision_pairs":collisions,
            "identifiable_in_declared_three_world_set":len(collisions)==0}

def observed_completions(events):
    """Two distinct offline reward-law completions exactly match selected data.

    Both always produce identical ACTUALLY observed public feedback; no learner
    reads the completions. Unobserved -3 or +9 truth values remain evaluator only.
    """
    observed={}
    evidence=[]
    for event in events:
        cue,first,second=event["selected_public"]
        key=(cue,first,second)
        value=float(event["reward"])
        assert -3.0<=value<=9.0,("SELECTED_REWARD_OUT_OF_LOCKED_BOUND",key,value)
        assert key not in observed or abs(observed[key]-value)<=1e-12
        observed[key]=value
        evidence.append({"selected":[cue,first,second],"reward":round(value,12)})
    assert len(evidence)==15 and len(set((c,f) for c,f,a in observed))==12
    completions={}
    for name,missing in (("LOW",-3.0),("HIGH",9.0)):
        full={(cue,first,action):observed.get((cue,first,action),missing)
              for cue,first in CONTEXTS for action in ACTIONS}
        assert len(full)==36
        assert all(full[key]==value for key,value in observed.items())
        decisions=[]
        for cue,first in CONTEXTS:
            vals=[full[(cue,first,act)] for act in ACTIONS]
            idx=max(range(3),key=lambda i:vals[i])
            decisions.append([cue,first,ACTIONS[idx]])
        completions[name]={"optimal_actions":decisions,
            "complete_evaluator_law_sha":hashlib.sha256(canonical([
                full[(cue,first,a)] for cue,first in CONTEXTS for a in ACTIONS
            ])).hexdigest()}
    disagreement=sum(a[2]!=b[2] for a,b in
        zip(completions["LOW"]["optimal_actions"],completions["HIGH"]["optimal_actions"]))
    sha=hashlib.sha256(canonical(evidence)).hexdigest()
    return {"selected_public_history_sha":sha,
        "selected_feedback_unique_count":len(observed),
        "never_selected_actions":36-len(observed),
        "low":completions["LOW"],"high":completions["HIGH"],
        "different_optimal_context_count":disagreement,
        "information_witness_at_least_6":disagreement>=6}

def frozen_rank_utilization(row):
    before=row["budget12"]
    after=row["budget15"]
    earlier=before["frozen_predictions"]
    later=after["frozen_predictions"]
    assert len(earlier)==len(later)==12
    signed=[]
    for a,b in zip(earlier,later):
        assert len(a)==len(b)==3
        signed.extend([y-x for x,y in zip(a,b)])
    delta_count=sum(abs(x)>1e-8 for x in signed)
    action_changes=sum(x[2]!=y[2] for x,y in zip(before["policy"],after["policy"]))
    margin=lambda r:round(sorted(r)[-1]-sorted(r)[-2],12)
    margins_before=[margin(x) for x in earlier]
    margins_after=[margin(x) for x in later]
    old_regret=before["regret"]
    new_regret=after["regret"]
    return {"regret_before":old_regret,"regret_after":new_regret,
        "relative_regret_improvement":round((old_regret-new_regret)/old_regret,12) if old_regret>1e-10 else None,
        "native_learned_weight_sha_before":before["native_weights_sha"],
        "native_learned_weight_sha_after":after["native_weights_sha"],
        "native_parameters_changed":before["native_weights_sha"]!=after["native_weights_sha"]
                                    if before["native_weights_sha"] is not None else None,
        "frozen_36_score_changed_count":delta_count,
        "frozen_36_score_abs_delta_sum":round(sum(abs(x) for x in signed),12),
        "frozen_36_score_max_abs_delta":round(max(map(abs,signed)),12),
        "action_rank_changes":action_changes,
        "margins_before":margins_before,"margins_after":margins_after,
        "policy_before":before["policy"],"policy_after":after["policy"],
        "prediction_error_36_before":before["absolute_error_36"],
        "prediction_error_36_after":after["absolute_error_36"],
        "selected_probe_feedback":[{"action":p["selected_public"],
                                    "selected_absolute_error":p["selected_absolute_error"]}
                                   for p in row["probes"]]}

def classify(records,finite):
    lookup={(r["world"],r["mode"]):r for r in records}
    broad=all(r["completions"]["information_witness_at_least_6"] for r in records)
    stalled=[]
    for world in WORLDS:
        r=lookup[(world,"v22_shared_novelty")]["rank"]
        stalled.append(not(r["regret_before"]>1e-10 and
                           r["regret_after"]<=0.9*r["regret_before"]))
    rank_affected=all(lookup[(w,"v22_shared_novelty")]["rank"]["native_parameters_changed"]
                      and lookup[(w,"v22_shared_novelty")]["rank"]["frozen_36_score_changed_count"]>0
                      for w in WORLDS)
    if not finite["identifiable_in_declared_three_world_set"]:
        label="V36_FIXED_TOY_FAMILY_NOT_IDENTIFIABLE__NO_SCIENCE"
    elif broad and sum(stalled)>=2 and rank_affected:
        label="V36_PUBLIC_INFORMATION_VS_NATIVE_RANK_MISMATCH__NO_SCIENCE"
    elif broad:
        label="V36_MIXED_PUBLIC_INFORMATION_RANK_DIAGNOSTIC__NO_SCIENCE"
    else:
        label="V36_INFORMATION_BOUNDARY_NOT_CONCLUSIVE__NO_SCIENCE"
    return label,{"three_family_selected_history_identifiable":
                   finite["identifiable_in_declared_three_world_set"],
                 "unrestricted_pair_witness_all_nine":broad,
                 "native_shared_family_stalled":{w:stalled[i] for i,w in enumerate(WORLDS)},
                 "shared_native_score_and_weight_response_all_three":rank_affected,
                 "native_shared_stalled_world_count":sum(stalled),
                 "per_world":{w:{mode:{
                     "regret12":lookup[(w,mode)]["rank"]["regret_before"],
                     "regret15":lookup[(w,mode)]["rank"]["regret_after"],
                     "action_rank_changes":lookup[(w,mode)]["rank"]["action_rank_changes"],
                     "changed_36_score_count":lookup[(w,mode)]["rank"]["frozen_36_score_changed_count"],
                     "hypothetical_completion_optimal_action_disagreements":
                         lookup[(w,mode)]["completions"]["different_optimal_context_count"]}
                    for mode in MODES} for w in WORLDS}}

def main():
    verify()
    wall=time.perf_counter();cpu=time.process_time();tracemalloc.start()
    source=train_source()["pretrained_shared"]
    source_sha=SharedContextRingDev.restore(source).parameters_sha256()
    observed,mapping=selected_map()
    assert len(observed)==12 and len(set(observed))==12
    finite=finite_family_information(observed)
    records=[]
    for world in WORLDS:
        for mode in MODES:
            row=run(mode,world,source,observed)
            assert row["source_sha"]==source_sha
            assert len(row["public_events"])==15
            assert row["model_updates"]==15
            controls=paired_controls(world,source,row["public_events"]) if mode=="v35_novelty" else None
            negative=nonlearning_control(row["public_events"]) if mode=="v35_novelty" else None
            if controls:
                assert all(v["updates"]==15 for v in controls.values())
                assert negative["unchanged"] and negative["updates"]==0
            completions=observed_completions(row["public_events"])
            rank=frozen_rank_utilization(row)
            if not mode.startswith("rls_"):
                assert row["native_scalars"]==163 and row["budget15"]["checkpoint_bytes"]<=12288
                assert row["budget12"]["checkpoint_bytes"]<=12288
                assert row["edge_signals"]["reverse"]>0
            records.append({"world":world,"mode":mode,
              "actual_selected_feedback":row["public_events"],
              "frozen_rank":rank,
              "rank":rank,
              "completions":completions,
              "paired_action_controls":controls,"negative_nonlearning_control":negative,
              "actual_model_updates":row["model_updates"],
              "native_scalar_count":row["native_scalars"],
              "native_edge_signal_count":row["edge_signals"],
              "budget15_checkpoint_bytes":row["budget15"]["checkpoint_bytes"],
              "protected_original_source_sha":source_sha})
    classification,gates=classify(records,finite)
    digest=hashlib.sha256(canonical({"finite":finite,"records":records})).hexdigest()
    print(json.dumps({"schema":"ygg.itd02.v36.finite_identifiability_vs_native_rank.source_only.v1",
        "classification":classification,
        "source_only":True,"scientific_first_use":False,
        "new_native_model":False,"original_source_modified":False,
        "unknown_world_information_sufficiency_claim":False,
        "worlds":list(WORLDS),"modes":list(MODES),"independent_arms":len(records),
        "original_source_training_feedback":576,"base_public_feedback":12,"extra_selected_feedback":3,
        "native_trainable_scalars":163,"source_parameters_sha":source_sha,
        "original_v35_outcomes_unmodified":True,
        "finite_world_information":finite,"predeclared_gates":gates,
        "canonical_selected_information_and_rank_sha256":digest,
        "arm_records":[{"world":r["world"],"mode":r["mode"],
          "unique_selected_cases":r["completions"]["selected_feedback_unique_count"],
          "never_selected_cases":r["completions"]["never_selected_actions"],
          "low_high_optimal_disagreements":r["completions"]["different_optimal_context_count"],
          "regret12":r["rank"]["regret_before"],
          "regret15":r["rank"]["regret_after"],
          "native_weights_changed":r["rank"]["native_parameters_changed"],
          "score_coordinate_changes":r["rank"]["frozen_36_score_changed_count"],
          "action_rank_changes":r["rank"]["action_rank_changes"],
          "native_edge_signals":r["native_edge_signal_count"],
          "checkpoint_bytes":r["budget15_checkpoint_bytes"]}
          for r in records],
        "host_only_resources":{"wall_seconds":time.perf_counter()-wall,
          "cpu_seconds":time.process_time()-cpu,
          "tracemalloc_peak_bytes":tracemalloc.get_traced_memory()[1],
          "retail_pc_evidence":False}
        },sort_keys=True,separators=(",",":")))

if __name__=="__main__":
    main()
