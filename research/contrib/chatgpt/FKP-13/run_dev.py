"""FKP-13 frozen real-world closed-loop intervention experiment.

One original DEV on Linux after exact-source dual-OS qualification.
Every action is issued to original MysteryPath-v0, reward read only AFTER action.
All models share training source; DEV on-policy histories differ by design.
Never use protected/transfer source or source-private environment attributes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import random
import struct
import sys
import time

import numpy as np

import cohorts
from controller import Controller,ARMS,candidates,arm_rng,choose_index
from model import DirectMemory,brier,prior_probs
from baselines import train_all

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/"FKP-12"))
import source as source12

MAX_TOTAL=176128
BOOTSTRAPS=10000

def evidence_digest(episodes):
    h=hashlib.sha256()
    for e in episodes:
        h.update(e["seed"].to_bytes(4,"little"))
        h.update(e["policy"].encode("ascii"))
        h.update(e["source_sha256"].encode("ascii"))
        h.update(e["x"].astype("<f4",copy=False).tobytes())
        h.update(e["y"].astype("<i8",copy=False).tobytes())
    return h.hexdigest()


def score_brier(mem,episodes):
    tot=sum(len(e["y"]) for e in episodes)
    if not tot:raise ValueError("FKP13_EMPTY_VALIDATION")
    return sum(brier(mem.predict(e["x"]),e["y"])*len(e["y"])
               for e in episodes)/tot


def seal_pre_dev(direct,counts,shuffled,trained,training,validation,selected):
    h=hashlib.sha256()
    for e in (training,validation):h.update(evidence_digest(e).encode("ascii"))
    for memory in (direct,counts,shuffled):h.update(memory.snapshot())
    for name in sorted(trained):
        h.update(name.encode("ascii"))
        for key,val in sorted(trained[name].state_dict().items()):
            h.update(key.encode("utf-8"))
            h.update(val.detach().cpu().contiguous().numpy().tobytes())
    h.update(json.dumps(selected,sort_keys=True).encode("utf-8"))
    return h.hexdigest()


def play(seed,controller,upstream):
    if seed not in cohorts.DEV:raise PermissionError("FKP13_ORIGINAL_DEV_SOURCE_FENCE")
    import memory_gym  # noqa; public source registration
    rng=(cohorts.policy_rng(seed,"uniform") if controller.name=="RANDOM"
         else cohorts.policy_rng(seed,"macro8") if controller.name=="MACRO8"
         else arm_rng(seed,controller.name))
    controller.new_world()
    env,obs=cohorts.new_env(seed,upstream,dev=True)
    hash_source=hashlib.sha256()
    source12.admit.frame(hash_source,obs)
    macro=None;prev=1
    started=time.perf_counter()
    episodes_rewards=[]
    frames={hashlib.sha256(np.asarray(obs).tobytes(order="C")).digest()}
    try:
        for step in range(cohorts.CAP):
            features=None;branches=None;index=None
            if controller.name=="RANDOM":
                act=cohorts.public_policy(rng,"uniform",step)
            elif controller.name=="MACRO8":
                act=cohorts.public_policy(rng,"macro8",step,macro)
                macro=act
            else:
                features=candidates(obs,prev)
                prob,branches=controller.estimate(features)
                index=choose_index(prob,rng)
                act=(index//3,index%3)
            hash_source.update(bytes(act))
            obs,reward,done,trunc=cohorts.real_step(env,act)
            source12.admit.frame(hash_source,obs)
            hash_source.update(struct.pack("<d??",reward,done,trunc))
            frames.add(hashlib.sha256(np.asarray(obs).tobytes(order="C")).digest())
            label=source12.label(reward)
            if features is not None:
                controller.observed(features,index,branches,label)
            prev=label
            episodes_rewards.append(reward)
            if done or trunc:break
        if not episodes_rewards:raise AssertionError("FKP13_NO_GENUINE_ACTION")
        return {
            "seed":seed,"arm":controller.name,
            "steps":len(episodes_rewards),
            "return":float(round(sum(episodes_rewards),8)),
            "positive_progress":int(sum(0<r<0.5 for r in episodes_rewards)),
            "goals_from_public_rewards":int(sum(r>=0.5 for r in episodes_rewards)),
            "negative_events":int(sum(r<0 for r in episodes_rewards)),
            "terminated":bool(done or trunc),
            "distinct_public_frames":len(frames),
            "public_source_sha256":hash_source.hexdigest(),
            "wall_seconds":float(time.perf_counter()-started),
        }
    finally:env.close()


def paired_gain(rows):
    by_arm={a:np.asarray([next(r["return"] for r in rows
                if r["arm"]==a and r["seed"]==seed) for seed in cohorts.DEV],
                dtype=np.float64) for a in ARMS}
    direct=by_arm["DIRECT_ONLINE"]
    controls=[a for a in ARMS if a!="DIRECT_ONLINE"]
    best=max(controls,key=lambda a:float(by_arm[a].mean()))
    observed=float(direct.mean()-max(by_arm[c].mean() for c in controls))
    rng=random.Random(1212)
    boot=[]
    for _ in range(BOOTSTRAPS):
        idx=[rng.randrange(len(cohorts.DEV)) for _ in cohorts.DEV]
        direct_mean=float(direct[idx].mean())
        control_best=max(float(by_arm[c][idx].mean()) for c in controls)
        boot.append(direct_mean-control_best)
    boot.sort()
    return best,observed,[float(boot[249]),float(boot[9749])],{
        a:float(x.mean()) for a,x in by_arm.items()}


def run(upstream:Path):
    started=time.perf_counter()
    cpu_started=time.process_time()
    custody=cohorts.custody(upstream)
    sys.path.insert(0,str(upstream))
    train=cohorts.collect(cohorts.TRAIN,upstream)
    validation=cohorts.collect(cohorts.VALIDATE,upstream)
    train_steps=sum(e["steps"] for e in train)
    validation_steps=sum(e["steps"] for e in validation)
    if len(train)!=96 or len(validation)!=32 or train_steps>49152 or validation_steps>16384:
        raise AssertionError("FKP13_TRAIN_VALIDATION_ACTION_CUSTODY")
    direct=DirectMemory().fit(train)
    counts=DirectMemory(two_hash=False).fit(train)
    shuffled=DirectMemory().fit(train,shuffle_labels=True)
    init_probe_brier=score_brier(direct,validation)
    training_started=time.perf_counter()
    torch,trained,selected=train_all(train,validation)
    trained_wall=time.perf_counter()-training_started
    assert selected["GRU"]["full_epochs_per_seed"]==24
    assert selected["MLP"]["full_epochs_per_seed"]==24
    assert all(selected[n]["seeds_trained"]==[1212,3434]
               for n in ("GRU","MLP","LOGISTIC"))
    initial_seal=seal_pre_dev(direct,counts,shuffled,trained,train,validation,selected)
    clone=DirectMemory.restore(direct.snapshot())
    if clone.snapshot()!=direct.snapshot():
        raise AssertionError("FKP13_INITIAL_COLD_RESTORE")
    # At this line original DEV has not been accessed.
    controllers={name:Controller(name,direct,counts,trained,shuffled,torch)
                 for name in ARMS}
    report=[]
    retention=[]
    started_dev=time.perf_counter()
    for seed in cohorts.DEV:
        for name in ARMS:
            report.append(play(seed,controllers[name],upstream))
        tested=controllers["DIRECT_ONLINE"]
        checkpoint=tested.cold(validation[0]["x"][:64])
        count_checkpoint=controllers["COUNT_ONLINE"].cold(validation[0]["x"][:64])
        now_brier=score_brier(tested.memory,validation)
        retention.append({"seed":seed,"cold_sha256":checkpoint,
                          "conventional_count_cold_sha256":count_checkpoint,
                          "validation_brier":now_brier,
                          "delta_from_start":now_brier-init_probe_brier})
    dev_wall=time.perf_counter()-started_dev
    dev_steps=sum(r["steps"] for r in report)
    if len(report)!=len(ARMS)*len(cohorts.DEV) or dev_steps>110592:
        raise AssertionError("FKP13_DEV_ACTION_BUDGET")
    if train_steps+validation_steps+dev_steps>MAX_TOTAL:
        raise AssertionError("FKP13_TOTAL_SOURCE_OVERSPEND")
    best,gain,ci,means=paired_gain(report)
    positive={a:sum(r["positive_progress"] for r in report if r["arm"]==a)
              for a in ARMS}
    goals={a:sum(r["goals_from_public_rewards"] for r in report if r["arm"]==a)
           for a in ARMS}
    strongest_progress=max(positive[a] for a in ARMS if a!="DIRECT_ONLINE")
    strongest_goal=max(goals[a] for a in ARMS if a!="DIRECT_ONLINE")
    retention_pass=all(r["delta_from_start"]<=0.01 for r in retention)
    signal=(gain>=0.10 and ci[0]>0 and
            positive["DIRECT_ONLINE"]>=1.25*strongest_progress and
            goals["DIRECT_ONLINE"]>=1 and
            goals["DIRECT_ONLINE"]>=strongest_goal-1 and retention_pass)
    classification=("DEV_ACTION_SIGNAL_ONLY" if signal
                     else "DEV_NO_GO_RETENTION" if not retention_pass
                     else "DEV_MIXED_BEATS_WEAK_NOT_STRONG"
                     if means["DIRECT_ONLINE"]>means["RANDOM"] or
                        means["DIRECT_ONLINE"]>means["MACRO8"] else
                     "DEV_NO_GO_STRONG_CONVENTIONAL_OR_POLICY")
    h=hashlib.sha256()
    for r in report:
        h.update(r["seed"].to_bytes(4,"little"))
        h.update(r["arm"].encode("ascii"))
        h.update(r["public_source_sha256"].encode("ascii"))
    return {
        "schema":"fkp13.public-dev-closed-loop-consequence.v1",
        "classification":classification,
        "preregistered_dev_action_signal":signal,
        "scientific_pass":False,
        "accepted_model_modified":False,
        "protected_first_use":False,
        "reserved_transfer_opened":False,
        "original_public_dev_consumed":True,
        "source_custody":custody,
        "source_actions":{"train":train_steps,"validation":validation_steps,
                          "development":dev_steps,"total":train_steps+validation_steps+dev_steps},
        "source_episodes":{"train":len(train),"validation":len(validation),
                           "development":len(report)},
        "train_source_sha256":evidence_digest(train),
        "validation_source_sha256":evidence_digest(validation),
        "pre_dev_model_selection_seal_sha256":initial_seal,
        "development_source_sha256":h.hexdigest(),
        "positive_progress_by_arm":positive,
        "goal_events_by_arm":goals,
        "best_return_control":best,
        "mean_source_return_by_arm":means,
        "direct_return_gain_over_strongest":gain,
        "world_bootstrap_95ci_reselecting_strongest":ci,
        "retention_pre_dev_validation_brier":init_probe_brier,
        "retention_gate_pass":retention_pass,
        "retention_per_world":retention,
        "direct_weights_raw_bytes":direct.weights.nbytes,
        "end_direct_snapshot_sha256":retention[-1]["cold_sha256"],
        "end_count_snapshot_sha256":retention[-1]["conventional_count_cold_sha256"],
        "gru_online_updates":controllers["GRU_ONLINE"].learning_updates,
        "gru_full_training_receipts":selected,
        "timing":{"training_models_wall":trained_wall,"dev_controllers_wall":dev_wall,
                  "all_wall":time.perf_counter()-started,
                  "all_cpu":time.process_time()-cpu_started},
        "on_policy_action_histories_are_different":True,
        "whole_process_compute_matched":False,
        "row_metrics":report
    }


def replay_only(upstream:Path):
    custody=cohorts.custody(upstream)
    sys.path.insert(0,str(upstream))
    train=cohorts.collect(cohorts.TRAIN,upstream)
    validation=cohorts.collect(cohorts.VALIDATE,upstream)
    direct=DirectMemory().fit(train)
    consumed_dev=cohorts.source_blind_dev_receipt(upstream)
    return {"schema":"fkp13.consumed-source-replay.v1",
            "classification":"CONSUMED_SOURCE_REPLAY_ONLY",
            "source_sha":cohorts.SOURCE_SHA,
            "source_custody":custody,
            "train_source_sha256":evidence_digest(train),
            "validation_source_sha256":evidence_digest(validation),
            "source_blind_dev_receipts":consumed_dev,
            "direct_snapshot_sha256":hashlib.sha256(direct.snapshot()).hexdigest(),
            "protected_first_use":False,"reserved_transfer_opened":False,
            "scientific_pass":False}


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--public-dev",action="store_true")
    parser.add_argument("--replay-consumed",action="store_true")
    parser.add_argument("--upstream-root",type=Path,required=True)
    parser.add_argument("--protected",action="store_true")
    args=parser.parse_args()
    if args.protected or args.public_dev==args.replay_consumed:
        parser.error("FKP13_PUBLIC_OR_CONSUMED_ONLY_PROTECTED_NEVER")
    result=(run if args.public_dev else replay_only)(args.upstream_root.resolve())
    print(json.dumps(result,sort_keys=True))
