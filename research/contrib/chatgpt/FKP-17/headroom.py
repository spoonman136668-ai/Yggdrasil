"""FKP17: genuine original 128-step Memory Gym action-consequence headroom.

No source-private world fields or hidden reward labels. All h16/h32/h64/h128
scores come from prefixes of one real h128 action trace per action plan.
No original FKP16 DEV or owner/transfer seeds can enter this source study.
"""
from __future__ import annotations
from collections import defaultdict
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import struct
import sys
import time
os.environ["SDL_VIDEODRIVER"]="dummy"
os.environ["SDL_AUDIODRIVER"]="dummy"
sys.dont_write_bytecode=True

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"FKP-16"))
import source as original_source

FIT=tuple(range(975100,975108))
AUDIT=tuple(range(975200,975208))
ANCHORS=(0,16,32,64)
HORIZONS=(16,32,64,128)
PLAN_COUNT=24
MAX_REAL_SOURCE_ACTIONS=315000
BOOTSTRAP_COUNT=10000
UPSTREAM_SHA="a94f2b60d1769ea44df3226561488768e1dff9f4"
PLAN_NAMES=tuple(
    [f"CONSTANT_{i}" for i in range(9)]
    +[f"ALTERNATE8_{i}" for i in range(9)]
    +[f"BLIND_RANDOM8_{i}" for i in range(3)]
    +[f"PUBLIC_REWARD_FEEDBACK8_{i}" for i in range(3)]
)
assert len(PLAN_NAMES)==PLAN_COUNT


def fence(seed:int,anchor:int,plan:int|None):
    if type(seed) is not int or seed not in FIT+AUDIT:
        raise PermissionError("FKP17_CONSUMED_TRAIN_VAL_ONLY")
    if type(anchor) is not int or anchor not in ANCHORS:
        raise PermissionError("FKP17_FROZEN_PUBLIC_PREFIX")
    if plan is not None and (type(plan) is not int or not 0<=plan<PLAN_COUNT):
        raise PermissionError("FKP17_FROZEN_PLAN_ONLY")


def planned_action(plan:int,seed:int,anchor:int,t:int,
                   previous_action:int|None=None,previous_block_positive:bool=False)->int:
    fence(seed,anchor,plan)
    if type(t) is not int or not 0<=t<128:raise ValueError("FKP17_ACTION_STEP")
    block=t//8
    if plan<9:return plan
    if plan<18:
        k=plan-9
        return k if block%2==0 else (k+4)%9
    if plan<21:
        salt=(seed*1000003)^(anchor*4099)^(plan*1229)^(block*7643)^0xF170123
        return random.Random(salt).randrange(9)
    variant=plan-21
    first=(seed+anchor//16+variant)%9
    if block==0:return first
    if previous_action is None:
        raise ValueError("FKP17_FEEDBACK_NEEDS_OWN_PUBLIC_PREVIOUS_ACTION")
    if previous_block_positive:return previous_action
    return (previous_action+1+variant)%9


def horizon_prefix_receipts(public_rewards:list[float],goals:list[int],positive:list[int],
                            negative:list[int])->dict:
    if (not public_rewards or len(public_rewards)>128 or
        len(public_rewards)!=len(goals) or len(goals)!=len(positive) or len(positive)!=len(negative) or
        any(not math.isfinite(float(x)) for x in public_rewards)):
        raise ValueError("FKP17_PUBLIC_TRAJECTORY_INVALID")
    scores={}
    for h in HORIZONS:
        n=min(h,len(public_rewards))
        scores[str(h)]={
            "earned_real_return":float(round(math.fsum(public_rewards[:n]),8)),
            "goal_events":int(sum(goals[:n])),
            "positive_reward_events":int(sum(positive[:n])),
            "negative_reward_events":int(sum(negative[:n])),
            "realized_source_steps":n,
            "terminated_early":len(public_rewards)<h
        }
    return scores


def single_plan(seed:int,anchor:int,plan:int,upstream:Path)->dict:
    fence(seed,anchor,plan)
    # Original FKP16 native Python source, no source function/algorithm edits.
    prefix=original_source.real_prefix(seed,anchor)
    if not prefix["valid"]:
        return {"seed":seed,"anchor":anchor,"plan":plan,
                "valid":False,"prefix_sha256":prefix["prefix_sha256"],
                "total_physical_actions":prefix["source_steps"]}
    env=prefix.pop("env")
    import gymnasium as gym
    rewards=[];goals=[];positive=[];negative=[]
    hash_stream=hashlib.sha256()
    actual=prefix["source_steps"]
    previous_action=None
    current_block_positive=False
    previous_block_positive=False
    try:
        if not isinstance(env.action_space,gym.spaces.MultiDiscrete) or tuple(int(x) for x in env.action_space.nvec)!=(3,3):
            raise ValueError("FKP17_SOURCE_ACTION_DRIFT")
        for t in range(128):
            if t%8==0 and t>0:
                previous_block_positive=current_block_positive
                current_block_positive=False
            choice=planned_action(plan,seed,anchor,t,previous_action,
                                  previous_block_positive)
            action=original_source.ACTIONS[choice]
            public_native=np.asarray(action,dtype=np.int64)
            if not env.action_space.contains(public_native):
                raise ValueError("FKP17_ILLEGAL_PUBLIC_ACTION")
            obs,reward,terminated,truncated,_unused_info=env.step(public_native)
            value=float(reward)
            if not math.isfinite(value):raise ValueError("FKP17_NONFINITE_PUBLIC_REWARD")
            hash_stream.update(bytes(action))
            original_source.public_digest(hash_stream,obs)
            hash_stream.update(struct.pack("<d??",value,bool(terminated),bool(truncated)))
            rewards.append(value)
            goal=int(value>=1 and bool(terminated))
            goals.append(goal)
            positive.append(int(value>0))
            negative.append(int(value<0))
            current_block_positive|=(value>0)
            previous_action=choice
            actual+=1
            if terminated or truncated:break
    finally:
        env.close()
    return {"seed":seed,"anchor":anchor,"plan":plan,"plan_name":PLAN_NAMES[plan],
            "valid":True,"prefix_sha256":prefix["prefix_sha256"],
            "original_128step_trace_sha256":hash_stream.hexdigest(),
            "source_prefix_actions":prefix["source_steps"],
            "future_physical_source_actions":len(rewards),
            "total_physical_actions":actual,
            "actual_native_goal_ever":bool(any(goals)),
            "by_horizon":horizon_prefix_receipts(rewards,goals,positive,negative)}


def source_rows(seeds:tuple[int,...],upstream:Path)->tuple[list[dict],dict]:
    if seeds not in (FIT,AUDIT):
        raise PermissionError("FKP17_SOURCE_ONLY_CONSUMED_FIT_OR_AUDIT")
    data=[]
    charged=0
    for seed in seeds:
        for anchor in ANCHORS:
            prior=None
            for plan in range(PLAN_COUNT):
                r=single_plan(seed,anchor,plan,upstream)
                charged+=r["total_physical_actions"]
                if prior is None:prior=r["prefix_sha256"]
                elif prior!=r["prefix_sha256"]:
                    raise AssertionError("FKP17_REAL_SOURCE_PREFIX_NOT_IDENTICAL")
                data.append(r)
    if len(data)!=len(seeds)*len(ANCHORS)*PLAN_COUNT:
        raise AssertionError("FKP17_SOURCE_PLAN_COUNT")
    packed=json.dumps(data,sort_keys=True,separators=(",",":"),allow_nan=False)
    return data,{
        "source_action_count":charged,
        "source_rollouts":len(data),
        "source_world_count":len(seeds),
        "full_genuine_public_transcript_sha256":hashlib.sha256(packed.encode()).hexdigest()
    }


def paired_world_bootstrap(rows:list[dict],a_plan_selector,b_plan_selector,h:int)->dict:
    differences=[]
    for seed in AUDIT:
        x=[r for r in rows if r["seed"]==seed and r["valid"]]
        pairs=defaultdict(dict)
        for r in x:pairs[r["anchor"]][r["plan"]]=r["by_horizon"][str(h)]["earned_real_return"]
        eligible=[p for p in pairs.values() if len(p)==PLAN_COUNT]
        if not eligible:
            raise ValueError("FKP17_NO_EVALUABLE_AUDIT_WORLD")
        diffs=[float(a_plan_selector(p))-float(b_plan_selector(p)) for p in eligible]
        differences.append(sum(diffs)/len(diffs))
    rng=random.Random(9090)
    samples=sorted(sum(differences[rng.randrange(len(differences))] for _ in differences)
                   /len(differences) for _ in range(BOOTSTRAP_COUNT))
    return {"mean_paired_gain":sum(differences)/len(differences),
            "world_cluster_ci95":[samples[249],samples[9749]],
            "audited_worlds":len(differences)}


def describe(rows:list[dict],selected_plan:int)->dict:
    per_horizon={}
    for h in HORIZONS:
        oracle_values=[];fixed_values=[];random_values=[];const_values=[]
        goal_anchors=0;goal_worlds=set()
        positive_count=0;negative_count=0;total_future=0
        for seed in AUDIT:
            for anchor in ANCHORS:
                context=[r for r in rows if r["seed"]==seed and r["anchor"]==anchor and r["valid"]]
                if len(context)!=PLAN_COUNT:
                    raise ValueError("FKP17_AUDIT_COMPLETE_24_POLICY_MATRIX_REQUIRED")
                by_id={r["plan"]:r for r in context}
                y=[by_id[i]["by_horizon"][str(h)] for i in range(PLAN_COUNT)]
                oracle_values.append(max(v["earned_real_return"] for v in y))
                const_values.append(max(v["earned_real_return"] for v in y[:9]))
                fixed_values.append(y[selected_plan]["earned_real_return"])
                random_values.append(y[18]["earned_real_return"])
                if any(v["goal_events"]>0 for v in y):
                    goal_anchors+=1
                    goal_worlds.add(seed)
                positive_count+=sum(v["positive_reward_events"] for v in y)
                negative_count+=sum(v["negative_reward_events"] for v in y)
                total_future+=sum(v["realized_source_steps"] for v in y)
        boot=paired_world_bootstrap(rows,lambda p:max(p.values()),
             lambda p:p[selected_plan],h)
        per_horizon[str(h)]={
          "audited_anchor_count":len(oracle_values),
          "goal_reachable_anchor_count":goal_anchors,
          "distinct_worlds_with_some_goal":len(goal_worlds),
          "privileged_best24_mean_return":float(np.mean(oracle_values)),
          "privileged_best_constant9_mean_return":float(np.mean(const_values)),
          "fit_selected_fixed_plan_mean_return":float(np.mean(fixed_values)),
          "source_blind_random_plan18_mean_return":float(np.mean(random_values)),
          "privileged_oracle24_minus_fixed_mean_return":boot["mean_paired_gain"],
          "paired_world_bootstrap_ci95":boot["world_cluster_ci95"],
          "source_reward_positive_events_across_all24":positive_count,
          "source_reward_negative_events_across_all24":negative_count,
          "future_steps_retrospective_no_extra_source_actions":total_future
        }
    high=per_horizon["128"]
    passed=(high["distinct_worlds_with_some_goal"]>=2
            and high["goal_reachable_anchor_count"]>=4
            and high["privileged_oracle24_minus_fixed_mean_return"]>=0.15
            and high["paired_world_bootstrap_ci95"][0]>0)
    return {"horizons":per_horizon,"source_information_signal":passed,
            "classification":"DEV_SOURCE_HEADROOM_ONLY_NOT_SCIENCE" if passed
                else "DEV_NO_GO_LONG_HORIZON_GOAL_SUFFICIENCY",
            "scientific_pass":False,
            "accepted_native_model_changed":False,
            "protected_first_use":False,
            "FKP16_fresh_dev_reused":False}


def study(upstream:Path)->dict:
    began=time.perf_counter()
    source=original_source.admit.source_custody(upstream)
    if original_source.SOURCE_SHA!=UPSTREAM_SHA:
        raise AssertionError("FKP17_UPSTREAM_SHA_DRIFT")
    sys.path.insert(0,str(upstream))
    fit,fit_receipt=source_rows(FIT,upstream)
    fit_mean=[]
    for plan in range(PLAN_COUNT):
        vals=[r["by_horizon"]["128"]["earned_real_return"] for r in fit
              if r["valid"] and r["plan"]==plan]
        if len(vals)!=len(FIT)*len(ANCHORS):
            raise ValueError("FKP17_INCOMPLETE_FIT_WORLD")
        fit_mean.append(sum(vals)/len(vals))
    fixed=int(np.argmax(fit_mean))  # selected before observing AUDIT future outcomes
    fit_choice_digest=hashlib.sha256(json.dumps({"fit_source":fit_receipt,
             "frozen_fixed_index":fixed,"plan_mean_return":fit_mean},
             sort_keys=True,separators=(",",":")).encode()).hexdigest()
    audit,audit_receipt=source_rows(AUDIT,upstream)
    total=fit_receipt["source_action_count"]+audit_receipt["source_action_count"]
    if total>MAX_REAL_SOURCE_ACTIONS:
        raise AssertionError("FKP17_REAL_SOURCE_BUDGET_EXCEEDED")
    outcome=describe(audit,fixed)
    return {
        "schema":"fkp17.high-first-native-128step-source-headroom.v1",
        "original_source_experimental_run":True,
        "first_use_frozen_cohorts":"already-consumed FKP16 TRAIN/VAL ids; NEW H128 public action consequences",
        "source":source,
        "source_original_git_sha":UPSTREAM_SHA,
        "source_action_budget":{"fit":fit_receipt["source_action_count"],
           "audit":audit_receipt["source_action_count"],"total":total,
           "cap":MAX_REAL_SOURCE_ACTIONS},
        "source_worlds":{"fit":len(FIT),"audit":len(AUDIT)},
        "source_rollouts":{"fit":fit_receipt["source_rollouts"],"audit":audit_receipt["source_rollouts"]},
        "physical_fit_source_trace_sha256":fit_receipt["full_genuine_public_transcript_sha256"],
        "physical_audit_source_trace_sha256":audit_receipt["full_genuine_public_transcript_sha256"],
        "fit_only_best_fixed_plan":fixed,
        "fit_only_best_fixed_plan_name":PLAN_NAMES[fixed],
        "fit_global_plan_return_means":fit_mean,
        "fit_selection_custody_sha256":fit_choice_digest,
        "unblinded_source_dev_only":True,
        "no_conventional_model_training":True,
        "protected_owner_private_source_unopened":True,
        "runtime_seconds":round(time.perf_counter()-began,5),
        **outcome
    }


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--public-consumed-trainval-source",action="store_true")
    ap.add_argument("--protected",action="store_true")
    ap.add_argument("--upstream-root",type=Path,required=True)
    args=ap.parse_args()
    if args.protected or not args.public_consumed_trainval_source:
        ap.error("FKP17_ONLY_ALREADY_CONSUMED_PUBLIC_TRAIN_VAL; PROTECTED_COHORT_DISARMED")
    print(json.dumps(study(args.upstream_root.resolve()),sort_keys=True,allow_nan=False))
