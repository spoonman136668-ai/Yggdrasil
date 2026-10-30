#!/usr/bin/env python3
"""MG91 original source-reward demonstration training, independent public learners.

DEV: run frozen human-coded MG86 teacher on 12 prospectively frozen original
Farama seeds, then fit two distinct source-public policies on exact same
original source-selected *successful* trajectories. HELDOUT: restore each
trained checkpoint in a NEW Python process and evaluate own original rewards.
Teacher-assisted imitation ≠ autonomous native causal discovery.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time
try:
    import resource
except ModuleNotFoundError:
    resource=None
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter
from research.native.itd02.mg86.public_map_repair import RepairedMapControl
from research.native.itd02.mg91.native_prototypes import PublicRewardPrototypes
from research.native.itd02.mg92.feedback_cells import PublicFeedbackGate
from research.native.itd02.mg91.independent_linear import IndependentLinearControl
from research.native.itd02.mg90.paired_original_dev import (
    public,check_original,git,verify_clean)
from research.native.itd02.r10.public_adapter import canonical,digest

UPSTREAM="7f5853792ea7f04f75614661006d87fcf949f26d"
PREREG="63120fcf4fb3a074a21346bb7f9db78fe10c8b33"
BASE="f006cb1b875a396640ec6a6daf682a856f5d7477"
SOURCE={
 "research/native/itd02/mg92/feedback_cells.py":
     "e4be6548bf04e83e1ec2464657679c1633f83784",
 "research/native/itd02/mg91/native_prototypes.py":
     "8176b310b572427e68b24d13f284ae597c05c17b",
 "research/native/itd02/mg91/independent_linear.py":
     "17a2f652d5f05f2a45bb85159341f9daa5d9266e",
 "research/native/itd02/mg86/public_map_repair.py":
     "3c4b3ce716d51b96415cb0bd5ceb56d6d7897bfb",
 "research/native/itd02/mg85/public_map_control.py":
     "cdb2a6bf4feca1093537bab2d9207ea9f5e24e07",
 "research/native/itd02/mg90/paired_original_dev.py":
     "506a2ba26f5a8bab4f8c09b665a038532c8f9633"
}
FAMILIES=(
 ("MiniGrid-KeyCorridorS3R2-v0","minigrid.envs:KeyCorridorEnv",
  (2611101,2611103,2611105,2611109),2711107),
 ("MiniGrid-KeyCorridorS4R3-v0","minigrid.envs:KeyCorridorEnv",
  (2611201,2611203,2611205,2611209),2711207),
 ("MiniGrid-ObstructedMaze-1Dl-v0","minigrid.envs:ObstructedMaze_1Dlhb",
  (2611301,2611303,2611305,2611309),2711307)
)
ROLES=("mg92_native_feedback","mg91_frozen_native_prototypes",
       "mg91_independent_linear_control","mg86_frozen_teacher")
CAP=384

def preflight():
    for ancestor in (PREREG,BASE):
        git("merge-base","--is-ancestor",ancestor,"HEAD")
    for path,sha in SOURCE.items():
        if git("hash-object",path)!=sha:
            raise RuntimeError("MG92_PINNED_SOURCE_BLOB_DRIFT "+path)
    if (git("hash-object","research/native/itd02/mg92/PREREG.md")!=
        git("rev-parse",PREREG+":research/native/itd02/mg92/PREREG.md")):
        raise RuntimeError("MG92_PROSPECTIVE_PREREG_DRIFT")
    if len({seed for _,_,seeds,held in FAMILIES for seed in (*seeds,held)})!=15:
        raise RuntimeError("MG92_SEED_CONFLICT")
    verify_clean()
    print("MG92_ORIGINAL_SOURCE_PREREG_FROZEN_PASS")

def original_step(env,adapter,before,action):
    if type(action) is not int or action not in range(7):
        raise RuntimeError("MG91_SELECTED_SOURCE_ACTION_INVALID")
    submitted=adapter.submit(action)
    if submitted!=action:
        raise RuntimeError("MG92_SOURCE_ACTION_REMAP")
    next_obs,reward,ended,truncated,_=env.step(action)
    if (type(ended) is not bool or type(truncated) is not bool
        or type(reward) not in (float,int)
        or not math.isfinite(float(reward)) or not 0<=float(reward)<=1):
        raise RuntimeError("MG91_REAL_SOURCE_TERMINAL_REWARD_INVALID")
    nxt=public(next_obs)
    adapter.complete(nxt,float(reward),ended,truncated)
    event=adapter.ledger[-1]
    if (event["action"]!=action or event["before_sha"]!=digest(before)
        or event["after_sha"]!=digest(nxt)):
        raise RuntimeError("MG91_SELECTED_SOURCE_HASH_MISMATCH")
    return nxt,float(reward),ended,truncated

def run_teacher(gym,family,entry,seed):
    env=gym.make(family)
    try:
        if gym.spec(family).entry_point!=entry or env.action_space.n!=7:
            raise RuntimeError("MG92_ORIGINAL_ACTION_REGISTRATION_CHANGED")
        start=time.perf_counter()
        raw,_=env.reset(seed=seed)
        before=public(raw)
        adapter=OriginalMissionAdapter()
        adapter.reset_public(before)
        teacher=RepairedMapControl()
        teacher.start_session(adapter,"mg92-original-teacher-"+str(seed),live=False)
        steps=[]
        terminal=False
        returned=0.0
        for _ in range(CAP):
            choice=teacher.choose(before)
            if (type(choice) is not dict or type(choice.get("action")) is not int
                or choice.get("external_fallback") is not False
                or not str(choice.get("status","")).startswith("MG86_CONVENTIONAL_")):
                raise RuntimeError("MG91_FROZEN_SOURCE_TEACHER_DRIFT")
            action=choice["action"]
            nxt,reward,ended,truncated=original_step(env,adapter,before,action)
            teacher.learn_selected(adapter,before,nxt)
            steps.append({"before":before,"before_sha":digest(before),
                          "after_sha":digest(nxt),"action":action,
                          "reward":reward,"terminated":ended})
            returned+=reward
            if ended and reward>0:
                terminal=True
            before=nxt
            if ended or truncated:
                break
        if len(steps)!=adapter.events:
            raise RuntimeError("MG92_ORIGINAL_TEACHER_STEP_CONSERVATION")
        return {"family":family,"role":ROLES[3],"seed":seed,
                "original_selected_actions":len(steps),
                "success":terminal,"return":returned,
                "source_ledger_sha256":digest(steps),
                "source_ledger":steps,
                "elapsed_wall_seconds":round(time.perf_counter()-start,6)}
    finally:
        env.close()

def run_frozen(gym,family,entry,seed,model,role):
    env=gym.make(family)
    try:
        if gym.spec(family).entry_point!=entry or env.action_space.n!=7:
            raise RuntimeError("MG92_ORIGINAL_HELDOUT_SOURCE_CHANGED")
        start=time.perf_counter()
        obs,_=env.reset(seed=seed)
        before=public(obs)
        adapter=OriginalMissionAdapter()
        adapter.reset_public(before)
        model.start_session(adapter,"mg92-original-heldout-"+role+str(seed),live=False)
        old_sha=model.data_sha
        old_count=model.training_count
        policy_memory=(model.examples if role in (ROLES[0],ROLES[1]) else model.weights)
        policy_digest=hashlib.sha256(canonical(policy_memory)).hexdigest()
        steps=[]
        returned=0.
        success=False
        for _ in range(CAP):
            choice=model.choose(before)
            required=("MG92_TRAINED_PUBLIC_FEEDBACK_ACTION" if role==ROLES[0]
                      else "MG91_TRAINED_PUBLIC_REWARD_PROTOTYPE" if role==ROLES[1]
                      else "MG91_TRAINED_INDEPENDENT_LINEAR")
            if (choice.get("status")!=required or
                choice.get("external_fallback") is not False):
                raise RuntimeError("MG91_TRAINED_POLICY_IDENTITY_DRIFT")
            action=choice["action"]
            nxt,reward,ended,truncated=original_step(env,adapter,before,action)
            model.observe_selected(adapter,before,nxt)
            steps.append({"before_sha":digest(before),"after_sha":digest(nxt),
                          "action":action,"reward":reward,"terminated":ended})
            returned+=reward
            if ended and reward>0:
                success=True
            before=nxt
            if ended or truncated:
                break
        if (old_sha!=model.data_sha or old_count!=model.training_count
            or hashlib.sha256(canonical(policy_memory)).hexdigest()!=policy_digest
            or len(steps)!=adapter.events):
            raise RuntimeError("MG92_HELDOUT_TRAINING_WEIGHTS_OR_SOURCE_CHANGED")
        return {"family":family,"role":role,"seed":seed,
                "original_selected_actions":len(steps),
                "success":success,"return":returned,
                "source_ledger_sha256":digest(steps),
                "source_ledger":steps,
                "training_data_sha256":model.data_sha,
                "elapsed_wall_seconds":round(time.perf_counter()-start,6)}
    finally:
        env.close()

def checkpoint_path(out,family,role):
    return out/("checkpoint-"+family+"-"+role+".bin")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--phase",choices=("preflight","train","heldout"),required=True)
    parser.add_argument("--source-root",type=Path)
    parser.add_argument("--output-root",type=Path)
    a=parser.parse_args()
    preflight()
    if a.phase=="preflight":
        return
    if not a.source_root or not a.output_root:
        raise RuntimeError("MG92_ORIGINAL_SOURCE_AND_OUTPUT_REQUIRED")
    gym=check_original(a.source_root)
    out=a.output_root.resolve()
    out.mkdir(parents=True,exist_ok=True)
    reports=[]
    training=[]
    if a.phase=="train":
        for family,entry,seeds,_ in FAMILIES:
            completed=[run_teacher(gym,family,entry,seed) for seed in seeds]
            reports.extend(completed)
            wins=[{"seed":ep["seed"],"success":True,"steps":ep["source_ledger"]}
                  for ep in completed if ep["success"]]
            if not wins:
                raise RuntimeError("MG92_ZERO_AUTHENTIC_TEACHER_SUCCESS_FAMILY "+family)
            feedback=PublicFeedbackGate()
            native=PublicRewardPrototypes()
            control=IndependentLinearControl()
            for model in (feedback,native,control):
                model.fit(wins)
            if len({model.data_sha for model in (feedback,native,control)})!=1:
                raise RuntimeError("MG92_TEACHER_SOURCE_TRAIN_PARITY_FAIL")
            for role,model in ((ROLES[0],feedback),(ROLES[1],native),(ROLES[2],control)):
                blob=model.checkpoint()
                cls=type(model)
                if cls.restore(blob).checkpoint()!=blob:
                    raise RuntimeError("MG92_COLD_TRAIN_CHECKPOINT_FAIL")
                checkpoint_path(out,family,role).write_bytes(blob)
            training.append({"family":family,"successful_teacher_episodes":len(wins),
                             "demonstrated_source_actions":native.training_count,
                             "all_three_train_same_source_sha256":native.data_sha,
                             "feedback_checkpoint_bytes":len(feedback.checkpoint()),
                             "native_checkpoint_bytes":len(native.checkpoint()),
                             "linear_checkpoint_bytes":len(control.checkpoint())})
    else:
        for family,entry,_,seed in FAMILIES:
            models=[]
            for role,cls in ((ROLES[0],PublicFeedbackGate),
                             (ROLES[1],PublicRewardPrototypes),
                             (ROLES[2],IndependentLinearControl)):
                wire=checkpoint_path(out,family,role).read_bytes()
                model=cls.restore(wire)
                if model.checkpoint()!=wire:
                    raise RuntimeError("MG92_COLD_SOURCE_MODEL_MISMATCH")
                models.append((role,model))
            if len({model.data_sha for _,model in models})!=1:
                raise RuntimeError("MG92_HELDOUT_MATCHED_SOURCE_SHA_MISMATCH")
            for role,model in models:
                reports.append(run_frozen(gym,family,entry,seed,model,role))
            teacher=run_teacher(gym,family,entry,seed)
            # No teacher demonstration from sealed heldout may modify trained
            # models. It is reported only as a non-parity reference.
            teacher["source_ledger"]=[{k:v for k,v in step.items() if k!="before"}
                                     for step in teacher["source_ledger"]]
            reports.append(teacher)
    expect=12 if a.phase=="train" else 12
    if len(reports)!=expect:
        raise RuntimeError("MG92_ORIGINAL_PREDECLARED_COHORT_INCOMPLETE")
    result={"schema":"yggdrasil.mg92.original-public-feedback-supervised-dev.v1",
            "phase":a.phase,"upstream":UPSTREAM,"prereg":PREREG,
            "roles":list(ROLES),"family_count":3,"episodes":reports,
            "training":training,"source_step_counts":{
                role:sum(e["original_selected_actions"] for e in reports
                         if e["role"]==role) for role in ROLES},
            "science":"TEACHER_CONDITIONED_DEV_ONLY_NO_NATIVE_AUTONOMY_CLAIM",
            "process_max_rss_kib":(
                resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                if resource is not None else None)}
    for e in reports:
        if e["original_selected_actions"]<=0:
            raise RuntimeError("MG92_ZERO_ORIGINAL_SELECTED_ACTIONS")
    payload=canonical(result)
    (out/(a.phase+".json")).write_bytes(payload)
    print("MG92_ORIGINAL_PUBLIC_"+a.phase.upper()+"_SOURCE_EVENTS_PASS "+
          hashlib.sha256(payload).hexdigest())
    verify_clean()

if __name__=="__main__":
    try:
        main()
    except Exception as error:
        print("MG92_FAIL_CLOSED: "+str(error),file=sys.stderr)
        raise
