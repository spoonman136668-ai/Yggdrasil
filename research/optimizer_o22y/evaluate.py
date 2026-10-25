"""O22-Y source-excluded evidence of learned decision leverage.

Entire original-world (family, seed) C35 FIT group excluded from its own
model fitting. Score only real previously executed physical two-step branches.
The previously consumed C35 FIT_CHECK is source-validated but NOT trained,
searched, checked or scored here. No MiniGrid interaction, no hidden source grid.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

from research.native.itd02.r1.native_policy import canonical
from research.optimizer_o22w.evaluate import original_c35, observed, train_pair, cold as direct_cold
from research.optimizer_o22w.pair_models import FullNineRidgePairs,geometric_pair,select,LEGAL as SAFE,PAIRS
from research.optimizer_o22x.evaluate import train as fit_transitions, cold as transition_cold
from research.optimizer_o22x.transition_belief import NativeCausalCells,ConventionalNineRidge,choose,two_step_belief

HERE=Path(__file__).resolve().parent
P=json.loads((HERE/"PREREG.json").read_text())
SOURCE=P["source_C35"]
FAMILIES=("MiniGrid-FourRooms-v0","MiniGrid-Dynamic-Obstacles-8x8-v0")


def build(others):
    models={
        "native_original_R1":NativeCausalCells(),
        "native_shuffled_negative":NativeCausalCells(),
        "native_untrained_zero":NativeCausalCells(),
        "conventional_full9_composed":ConventionalNineRidge(),
        "conventional_full9_direct_pairs":FullNineRidgePairs(),
    }
    costs={}
    for name,m in models.items():
        if name=="native_untrained_zero":
            continue
        if name=="conventional_full9_direct_pairs":
            costs[name]=train_pair(m,others)
        else:
            costs[name]=fit_transitions(m,others,action_shift=name=="native_shuffled_negative")
    expected=len(others)*18
    if any(m.events!=expected for name,m in models.items()
           if name!="conventional_full9_direct_pairs" and name!="native_untrained_zero"):
        raise ValueError("O22Y_NOT_EQUAL_SOURCE_TRANSITION_RIGHTS")
    if models["conventional_full9_direct_pairs"].n!=len(others)*9:
        raise ValueError("O22Y_DIRECT_PAIR_SOURCE_COUNT")
    return models,costs


def decision(models,state):
    return {
        "native_original_R1":choose(models["native_original_R1"],state),
        "native_shuffled_negative":choose(models["native_shuffled_negative"],state),
        "native_untrained_zero":choose(models["native_untrained_zero"],state),
        "conventional_full9_composed":choose(models["conventional_full9_composed"],state),
        "conventional_full9_direct_pairs":select(models["conventional_full9_direct_pairs"],state),
        "public_geometry":geometric_pair(state),
        "fixed_forward22":"22"
    }


def summary_record(stats):
    return {
        "anchors":stats["anchors"],
        "physical_pair_observations":stats["physical_pair_observations"],
        "native_vs_zero_different":stats["native_vs_zero_different"],
        "native_vs_shuffled_different":stats["native_vs_shuffled_different"],
        "native_vs_composed_ridge_different":stats["native_vs_composed_ridge_different"],
        "native_vs_direct_ridge_different":stats["native_vs_direct_ridge_different"],
        "native_mean_real_progress":round(stats["native_progress"]/stats["anchors"],9),
        "zero_mean_real_progress":round(stats["zero_progress"]/stats["anchors"],9),
        "shuffled_mean_real_progress":round(stats["shuffled_progress"]/stats["anchors"],9),
        "composed_ridge_mean_real_progress":round(stats["ridge_progress"]/stats["anchors"],9),
        "direct_ridge_mean_real_progress":round(stats["direct_progress"]/stats["anchors"],9),
        "forward22_mean_real_progress":round(stats["forward_progress"]/stats["anchors"],9),
        "native_mean_real_oracle_regret":round(stats["native_regret"]/stats["anchors"],9),
        "zero_mean_real_oracle_regret":round(stats["zero_regret"]/stats["anchors"],9),
        "shuffled_mean_real_oracle_regret":round(stats["shuffled_regret"]/stats["anchors"],9),
        "composed_ridge_mean_real_oracle_regret":round(stats["ridge_regret"]/stats["anchors"],9),
        "direct_ridge_mean_real_oracle_regret":round(stats["direct_regret"]/stats["anchors"],9),
        "forward22_mean_real_oracle_regret":round(stats["forward_regret"]/stats["anchors"],9),
        "native_vs_composed_ridge_progress_MSE":round(stats["native_mse"]/stats["physical_pair_observations"],9),
        "composed_ridge_progress_MSE":round(stats["ridge_mse"]/stats["physical_pair_observations"],9),
        "native_vs_composed_ridge_front_Brier":round(stats["native_front"]/stats["physical_pair_observations"],9),
        "composed_ridge_front_Brier":round(stats["ridge_front"]/stats["physical_pair_observations"],9),
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-zip",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    started=time.process_time()
    if SOURCE["provider_run"]!=40203502643 or P["governance"]["new_original_source_actions"]!=0:
        raise ValueError("O22Y_ROLE_OR_ORIGINAL_FIRST_USE_DRIFT")
    original_fit,original_exposed_check,original_receipt=original_c35(args.source_zip.read_bytes())
    if (len(original_fit)!=31 or len(original_exposed_check)!=15
        or not original_receipt["two_process_science_identical"]):
        raise ValueError("O22Y_C35_SOURCE_CUSTODY_DRIFT")
    # Authentication of FIT_CHECK happens inside original_c35; these records
    # MUST NOT enter train, find, evaluate or target outcome code below.
    del original_exposed_check
    groups=defaultdict(list)
    for anchor in original_fit:
        f,s=anchor["family"],anchor["seed"]
        if f not in FAMILIES or type(s) is not int:
            raise ValueError("O22Y_SOURCE_FAMILY_OR_WORLD_SEED")
        groups[(f,s)].append(anchor)
    if len(groups)<3:
        raise ValueError("O22Y_NOT_ENOUGH_AUTHENTIC_WORLD_GROUPS")
    original_groups=len(groups)
    output=[]
    aggregate=defaultdict(lambda:defaultdict(float))
    positive_seed=set()
    tests_for_any_cold=False
    fresh_checkpoint_bytes={}
    all_cpu=defaultdict(float)
    for (family,seed),test_anchors in sorted(groups.items()):
        train_anchors=[q for identity,items in sorted(groups.items())
                       if identity!=(family,seed) for q in items]
        if not train_anchors or any(
            q["family"]==family and q["seed"]==seed for q in train_anchors
        ):
            raise ValueError("O22Y_SOURCE_WORLD_GROUP_HOLDOUT_LEAK")
        models,cost=build(train_anchors)
        for name,value in cost.items():
            all_cpu[name]+=value
        state=test_anchors[0]["public_initial"]
        if not tests_for_any_cold:
            # All stored learned-state cells and model predictions must restore
            # exactly in true new Python processes, including direct pair model.
            for name,model in models.items():
                fresh_checkpoint_bytes[name]=(
                    direct_cold(model,state)
                    if name=="conventional_full9_direct_pairs"
                    else transition_cold(model,state)
                )
            tests_for_any_cold=True
        st=defaultdict(float)
        st["anchors"]=len(test_anchors)
        st["physical_pair_observations"]=len(test_anchors)*9
        per_anchor=[]
        group_signal=False
        for anchor in test_anchors:
            s=anchor["public_initial"]
            picked=decision(models,s)
            if any(pair not in SAFE for pair in picked.values()):
                raise ValueError("O22Y_ILLEGAL_SAFETY_PAIR_SUGGESTED")
            physically={pair:observed(anchor,pair) for pair in PAIRS}
            true_goal={pair:physically[pair]["progress"] for pair in SAFE}
            best=max(true_goal.values())
            actual={name:physically[pair]["progress"] for name,pair in picked.items()}
            rewards={name:anchor["all_nine_original_physical_pairs"][pair]["actual_source_reward_sum"]
                     for name,pair in picked.items()}
            for tag,a,b in (
                ("native_vs_zero_different","native_original_R1","native_untrained_zero"),
                ("native_vs_shuffled_different","native_original_R1","native_shuffled_negative"),
                ("native_vs_composed_ridge_different","native_original_R1","conventional_full9_composed"),
                ("native_vs_direct_ridge_different","native_original_R1","conventional_full9_direct_pairs")
            ):
                st[tag]+=int(picked[a]!=picked[b])
            for name,suffix in (
                ("native_original_R1","native"),
                ("native_untrained_zero","zero"),
                ("native_shuffled_negative","shuffled"),
                ("conventional_full9_composed","ridge"),
                ("conventional_full9_direct_pairs","direct"),
                ("fixed_forward22","forward")
            ):
                st[suffix+"_progress"]+=actual[name]
                st[suffix+"_regret"]+=best-actual[name]
            for pair in PAIRS:
                real=physically[pair]
                native=two_step_belief(models["native_original_R1"],s,pair)
                ridge=two_step_belief(models["conventional_full9_composed"],s,pair)
                st["native_mse"]+=(native[0]-real["progress"])**2
                st["ridge_mse"]+=(ridge[0]-real["progress"])**2
                st["native_front"]+=(native[1]-float(real["blocked"]))**2
                st["ridge_front"]+=(ridge[1]-float(real["blocked"]))**2
            distinct=(picked["native_original_R1"]!=picked["native_untrained_zero"]
                      and picked["native_original_R1"]!=picked["conventional_full9_composed"])
            physical_advantage=(
                actual["native_original_R1"]-actual["native_untrained_zero"]>=0.5 and
                actual["native_original_R1"]-actual["conventional_full9_composed"]>=0.5
            )
            if distinct and physical_advantage:
                group_signal=True
                positive_seed.add((family,seed))
            per_anchor.append({
                "source_original_family":family,"source_original_seed_identity":seed,
                "original_public_prefix_tick":anchor["tick"],
                "frozen_before_observing_original_selected_pair_outcomes":picked,
                "authentic_original_physical_two_step_progress_by_choice":actual,
                "authentic_original_physical_reward_by_choice":rewards,
                "oracle_best_actually_selected_legal_pair_progress":best,
                "native_is_different_from_both_untrained_and_composed_ridge":distinct,
                "native_really_beats_both_by_at_least_half_progress":physical_advantage,
                "same_world_seed_excluded_from_own_model_FIT":True
            })
        this=summary_record(st)
        for key,value in st.items():
            aggregate[family][key]+=value
            aggregate["all"][key]+=value
        output.append({
            "source_original_family":family,
            "excluded_world_seed":seed,
            "excluded_source_anchors":len(test_anchors),
            "source_real_training_anchor_count":len(train_anchors),
            "source_real_training_selected_action_events_per_model":len(train_anchors)*18,
            "source_real_training_matched_action_pair_outcomes_per_direct_ridge":len(train_anchors)*9,
            "at_least_one_genuine_native_choice_and_half_progress_difference":group_signal,
            "summary":this,
            "actual_matched_original_source_anchor_choices":per_anchor
        })
    family_summary={k:summary_record(v) for k,v in sorted(aggregate.items())}
    familiar=len({s for f,s in positive_seed if f==FAMILIES[0]})
    moving=len({s for f,s in positive_seed if f==FAMILIES[1]})
    strict=all(
        family_summary[f]["native_mean_real_oracle_regret"] < val
        for f in FAMILIES for val in (
            family_summary[f]["zero_mean_real_oracle_regret"],
            family_summary[f]["composed_ridge_mean_real_oracle_regret"],
            family_summary[f]["direct_ridge_mean_real_oracle_regret"],
            family_summary[f]["forward22_mean_real_oracle_regret"]
        )
    )
    positive=len(positive_seed)>=3 and familiar>=1 and moving>=1 and strict
    decision=("SOURCE_FIT_ONLY_DISCRIMINATING_REAL_ACTION_ROSTER_REQUIRES_FRESH_OWNER_CONFIRMATION"
              if positive else "NO_GO_EXISTING_AUTHENTIC_PHYSICAL_ROSTER_DOES_NOT_ESTABLISH_LEARNED_ACTION_LEVERAGE")
    science={
        "schema":P["schema"],
        "source_original_C35_run":SOURCE["provider_run"],
        "original_source_artifact_SHA256":SOURCE["zip_sha256"],
        "two_authentic_original_C35_source_processes_verified":True,
        "original_FIT_matched_source_anchor_count":len(original_fit),
        "distinct_world_seed_holdout_groups":original_groups,
        "C35_previous_15_FIT_CHECK_anchor_count_authenticated_only_not_used_for_analysis":15,
        "total_real_matched_source_public_intervention_pairs_scored":len(original_fit)*9,
        "native_vs_untrained_and_conventional_true_progress_half_point_signal_seeds":[
            {"family":f,"seed":s} for f,s in sorted(positive_seed)],
        "native_strictly_better_all_family_regret_controls":strict,
        "per_family_discrimination_and_actual_regret":family_summary,
        "all_leave_entire_source_world_seed_out_original_FIT_folds":output,
        "representative_true_fresh_Python_child_full_learned_checkpoint_bytes":fresh_checkpoint_bytes,
        "original_world_NEW_FIT_DEV_PROTECTED_steps":0,
        "source_physically_returned_two_step_pair_benefits_not_imputed":True,
        "unchanged_C36_C37_original_source_negative_results":True,
        "genuinely_new_unfamiliar_source_family_transfer":"NOT_TESTED",
        "protected_first_use":"DENIED_FORGE_FSA_83",
        "scientific_gate":decision
    }
    science_hash=hashlib.sha256(canonical(science)).hexdigest()
    result={
        "science":science,
        "science_canonical_SHA256":science_hash,
        "resource_accounting":{
            "total_Python_CPU_seconds":round(time.process_time()-started,8),
            "train_CPU_seconds_all_seed_folds":{k:round(v,8) for k,v in all_cpu.items()},
            "overall_peak_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "energy_and_child_RSS":"UNMEASURED_NO_PARETO_CLAIM"
        }
    }
    args.out.write_bytes(canonical(result)+b"\n")
    print("O22Y_AUTHENTIC_C35_MATCHED_ORIGINAL_SOURCE_TWO_PROCESS=PASS",flush=True)
    print("O22Y_ENTIRE_ORIGINAL_WORLD_SEED_EXCLUDED_PER_MODEL="+str(original_groups),flush=True)
    print("O22Y_ORIGINAL_MATCHED_FIT_ANCHORS="+str(len(original_fit)),flush=True)
    print("O22Y_TRUE_PHYSICAL_NATIVE_VS_UNTRAINED_AND_RIDGE_PROGRESS_SIGNAL_SEED_COUNT="+str(len(positive_seed)),flush=True)
    for fam in FAMILIES:
        print("O22Y_"+fam+"_NATIVE_VS_ZERO_DIFFERENCES="+str(int(aggregate[fam]["native_vs_zero_different"])),flush=True)
        print("O22Y_"+fam+"_NATIVE_VS_RIDGE_DIFFERENCES="+str(int(aggregate[fam]["native_vs_composed_ridge_different"])),flush=True)
    print("O22Y_SOURCE_SCIENCE_CANONICAL_SHA256="+science_hash,flush=True)
    print("O22Y_GENUINELY_NEW_SOURCE_ACTIONS=ZERO",flush=True)
    print("O22Y_SCIENTIFIC_GATE="+decision,flush=True)


if __name__=="__main__":
    main()
