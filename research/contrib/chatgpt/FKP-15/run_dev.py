"""FKP15: one original real-source 16-step macro return study, source first-use fenced."""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import sys
import time

import numpy as np

import source as source15
from source import TRAIN,VALIDATION,DEV,ANCHORS,ACTIONS,MAX_ACTIONS
from models import DirectReturnMemory,fit_controls,predict_control,DIM

ARMS=("DIRECT_ONLINE","COUNT_ONLINE","GRU_FROZEN","MLP_FROZEN",
      "RIDGE_FROZEN","RANDOM","FIXED_MACRO","SHUFFLED_FROZEN")
BOOTSTRAPS=10000
EPSILON=0.1


def make_actions(older,now):
    return np.stack([source15.feature_pair(older,now,a) for a in range(9)])


def choose(arm,seed,anchor,scores):
    if arm not in ARMS or seed not in DEV or anchor not in ANCHORS:
        raise PermissionError("FKP15_UNREGISTERED_DEV_CHOICE")
    # All learned arms use the SAME frozen exploration draws per world/anchor.
    rng=random.Random((seed<<10)^(anchor<<3)^0xF15E7)
    if arm=="RANDOM":return rng.randrange(9)
    if arm=="FIXED_MACRO":return int(scores)
    if not isinstance(scores,np.ndarray) or scores.shape!=(9,) or not np.isfinite(scores).all():
        raise ValueError("FKP15_INVALID_CHOSEN_ACTION_SCORE")
    if rng.random()<EPSILON:return rng.randrange(9)
    ties=np.flatnonzero(np.abs(scores-np.max(scores))<1e-9)
    return int(ties[rng.randrange(len(ties))])


def paired_bootstrap(rows):
    table={(r["seed"],r["anchor"],r["arm"]):r["return"] for r in rows}
    by_world={a:np.array([np.mean([table[(s,anchor,a)] for anchor in ANCHORS])
                          for s in DEV],dtype=np.float64) for a in ARMS}
    controls=[a for a in ARMS if a!="DIRECT_ONLINE"]
    mean={a:float(v.mean()) for a,v in by_world.items()}
    strongest=max(controls,key=lambda a:mean[a])
    real_gain=mean["DIRECT_ONLINE"]-mean[strongest]
    rng=random.Random(9090)
    sample=[]
    for _ in range(BOOTSTRAPS):
        i=np.asarray([rng.randrange(len(DEV)) for _ in DEV],dtype=np.intp)
        direct=float(by_world["DIRECT_ONLINE"][i].mean())
        alternative=max(float(by_world[a][i].mean()) for a in controls)
        sample.append(direct-alternative)
    sample.sort()
    return mean,strongest,real_gain,[float(sample[249]),float(sample[9749])]


def actual_public_receipt(rows):
    h=hashlib.sha256()
    for r in rows:
        h.update(struct.pack("<IIIId",r["seed"],r["anchor"],r["action"],
                             r["future_steps"],r["return"]))
        h.update(bytes.fromhex(r["prefix_sha256"]))
        h.update(bytes.fromhex(r["branch_sha256"]))
        h.update(r["arm"].encode())
    return h.hexdigest()


def train_and_validate(upstream):
    began=time.perf_counter()
    train,train_receipt=source15.collect_all_branches(TRAIN,upstream)
    validation,val_receipt=source15.collect_all_branches(VALIDATION,upstream)
    direct=DirectReturnMemory(streams=2).fit(train)
    count=DirectReturnMemory(streams=1).fit(train)
    shuffle=DirectReturnMemory(streams=2)
    indices=list(range(len(train)))
    random.Random(1212).shuffle(indices)
    for j,r in enumerate(train):shuffle.update(r["x"],train[indices[j]]["real_return"])
    sums=np.zeros(9,dtype=np.float64)
    n=np.zeros(9,dtype=np.int32)
    for r in train:
        sums[r["action"]]+=r["real_return"]
        n[r["action"]]+=1
    assert np.all(n>0)
    fixed_action=int(np.argmax(sums/n))
    torch,trained,receipts=fit_controls(train,validation)
    val_x=np.stack([r["x"] for r in validation])
    val_y=np.asarray([r["real_return"] for r in validation])
    direct_val_mse=float(np.square(direct.predict(val_x)-val_y).mean())
    count_val_mse=float(np.square(count.predict(val_x)-val_y).mean())
    seals=hashlib.sha256()
    for value in (train_receipt["source_receipt_sha256"],val_receipt["source_receipt_sha256"]):
        seals.update(value.encode())
    for memory in (direct,count,shuffle):seals.update(memory.snapshot())
    for name in sorted(trained):
        model=trained[name]
        seals.update(name.encode())
        if isinstance(model,np.ndarray):seals.update(model.astype("<f8").tobytes())
        else:
            for key,tensor in sorted(model.state_dict().items()):
                seals.update(key.encode());seals.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return {"train":train_receipt,"validation":val_receipt,
            "direct":direct,"count":count,"shuffled":shuffle,
            "torch":torch,"controls":trained,"control_train_receipts":receipts,
            "fixed_macro_index":fixed_action,
            "validation_x":val_x,"validation_y":val_y,
            "validation_direct_initial_mse":direct_val_mse,
            "validation_count_initial_mse":count_val_mse,
            "pre_dev_selection_sha256":seals.hexdigest(),
            "training_wall_seconds":time.perf_counter()-began}


def run(upstream:Path):
    started=time.perf_counter();cpu_started=time.process_time()
    evidence=train_and_validate(upstream)
    train_steps=evidence["train"]["actions"]
    val_steps=evidence["validation"]["actions"]
    direct=evidence["direct"];count=evidence["count"]
    snapshots=(direct.snapshot(),count.snapshot(),evidence["shuffled"].snapshot())
    # Trainer/source sealed and all conventional models chosen BEFORE any DEV.
    out=[];source_actions=0
    per_world_retention=[]
    for seed in DEV:
        for anchor in ANCHORS:
            reference=source15.source_branch(seed,anchor,None,upstream,allow_dev=True)
            source_actions+=reference["prefix_steps"]
            if not reference["valid"]:
                raise ValueError("FKP15_DEV_PREFIX_INSUFFICIENT")
            past=np.asarray(reference["last_two_images"][0],dtype=np.float32)
            now=np.asarray(reference["last_two_images"][1],dtype=np.float32)
            all_features=make_actions(past,now)
            for arm in ARMS:
                if arm=="DIRECT_ONLINE":scores=direct.predict(all_features)
                elif arm=="COUNT_ONLINE":scores=count.predict(all_features)
                elif arm=="SHUFFLED_FROZEN":scores=evidence["shuffled"].predict(all_features)
                elif arm in evidence["controls"]:
                    scores=predict_control(evidence["torch"],evidence["controls"][arm],all_features)
                elif arm=="FIXED_MACRO":scores=evidence["fixed_macro_index"]
                else:scores=None
                chosen=choose(arm,seed,anchor,scores)
                response=source15.source_branch(seed,anchor,chosen,upstream,allow_dev=True)
                source_actions+=response["prefix_steps"]+response["future_steps"]
                if not response["valid"] or response["prefix_sha256"]!=reference["prefix_sha256"]:
                    raise AssertionError("FKP15_DEV_SOURCE_PREFIX_DRIFT")
                if not np.array_equal(response["x"],all_features[chosen]):
                    raise AssertionError("FKP15_DIFFERENT_PUBLIC_FEATURES")
                out.append({"seed":seed,"anchor":anchor,"arm":arm,"action":chosen,
                    "return":response["real_return"],"positive_events":response["positive_events"],
                    "negative_events":response["negative_events"],
                    "goal_events":response["true_goals"],"prefix_steps":response["prefix_steps"],
                    "future_steps":response["future_steps"],
                    "prefix_sha256":response["prefix_sha256"],
                    "branch_sha256":response["branch_sha256"]})
                # Genuine ONLINE learning only from the consequence of its
                # OWN chosen source action, never its nine counterfactuals.
                if arm=="DIRECT_ONLINE":
                    direct.update(all_features[chosen],response["real_return"])
                elif arm=="COUNT_ONLINE":
                    count.update(all_features[chosen],response["real_return"])
        probe=evidence["validation_x"]
        truth=evidence["validation_y"]
        dval=float(np.square(direct.predict(probe)-truth).mean())
        cval=float(np.square(count.predict(probe)-truth).mean())
        dr=direct.snapshot()
        clone=DirectReturnMemory.restore(dr)
        if dr!=clone.snapshot() or not np.array_equal(direct.predict(probe[:9]),clone.predict(probe[:9])):
            raise AssertionError("FKP15_COLD_RESTORE_MISMATCH")
        invalid=bytearray(dr);invalid[24]^=1
        try:DirectReturnMemory.restore(bytes(invalid))
        except ValueError:pass
        else:raise AssertionError("FKP15_COLD_TAMPER_ACCEPTED")
        per_world_retention.append({"world":seed,"direct_val_mse":dval,
             "direct_val_regression":dval-evidence["validation_direct_initial_mse"],
             "count_val_mse":cval,"direct_cold_sha256":hashlib.sha256(dr).hexdigest()})
    if len(out)!=len(DEV)*len(ANCHORS)*len(ARMS):
        raise AssertionError("FKP15_MISSING_DEV_CONTROL")
    total=train_steps+val_steps+source_actions
    if total>MAX_ACTIONS:
        raise AssertionError("FKP15_SOURCE_OVERSPEND")
    means,strongest,gain,ci=paired_bootstrap(out)
    goal_totals={arm:sum(r["goal_events"] for r in out if r["arm"]==arm) for arm in ARMS}
    positive={arm:sum(r["positive_events"] for r in out if r["arm"]==arm) for arm in ARMS}
    negative={arm:sum(r["negative_events"] for r in out if r["arm"]==arm) for arm in ARMS}
    time_means={}
    for anchor in ANCHORS:
        time_means[anchor]={arm:float(np.mean([r["return"] for r in out
                                     if r["anchor"]==anchor and r["arm"]==arm])) for arm in ARMS}
    no_anchor_regress=all(time_means[anchor]["DIRECT_ONLINE"]>=
         max(time_means[anchor][arm] for arm in ARMS if arm!="DIRECT_ONLINE")-0.01
         for anchor in ANCHORS)
    retention=all(z["direct_val_regression"]<=0.01 for z in per_world_retention)
    signal=(gain>=0.05 and ci[0]>0 and no_anchor_regress and retention and
        goal_totals["DIRECT_ONLINE"]>=max(goal_totals[a] for a in ARMS if a!="DIRECT_ONLINE")-1)
    frozen_negative=not signal
    return {
      "schema":"fkp15.public-source-16step-delayed-action-return.v1",
      "source_original_dev_consumed":True,"protected_first_use":False,
      "reserved_transfer_opened":False,"scientific_pass":False,
      "accepted_native_model_modified":False,
      "classification":"DEV_16STEP_ACTION_SIGNAL_ONLY" if signal else "DEV_NO_GO_STRONG_DELAYED_RETURN_CONTROL",
      "preregistered_gain_pass":signal,
      "source_actions":{"train":train_steps,"validation":val_steps,"dev":source_actions,"total":total},
      "source_episodes":{"train":evidence["train"]["branch_count"],"validation":evidence["validation"]["branch_count"],"dev":len(out)},
      "train_source_sha256":evidence["train"]["source_receipt_sha256"],
      "val_source_sha256":evidence["validation"]["source_receipt_sha256"],
      "original_dev_sha256":actual_public_receipt(out),
      "source_blind_random_original_dev":[[r["seed"],r["anchor"],r["action"],r["branch_sha256"]]
                 for r in out if r["arm"]=="RANDOM"],
      "original_pre_dev_all_models_sha256":evidence["pre_dev_selection_sha256"],
      "fully_fit_baseline_receipts":evidence["control_train_receipts"],
      "candidate_return_by_arm":means,"strongest_return_control":strongest,
      "direct_minus_best":gain,"paired_world_bootstrap_ci95":ci,
      "time_anchored_mean_returns":time_means,
      "true_goal_events_by_arm":goal_totals,
      "positive_events_by_arm":positive,"negative_events_by_arm":negative,
      "retention_pass":retention,"per_world_retention":per_world_retention,
      "direct_raw_bytes":direct.raw_weights_bytes,
      "count_raw_bytes":count.raw_weights_bytes,
      "direct_final_cold_sha256":per_world_retention[-1]["direct_cold_sha256"],
      "original_train_cold_sha256":hashlib.sha256(snapshots[0]).hexdigest(),
      "whole_process_compute_matched":False,
      "source_oracle_unavailable_to_dev":True,
      "timings":{"all_wall":time.perf_counter()-started,
                "all_cpu":time.process_time()-cpu_started,
                "model_fit_wall":evidence["training_wall_seconds"]},
      "per_original_dev_arm":out
    }


def replay_consumed(upstream:Path):
    """Windows verified source-only replay, never a second learned DEV trial."""
    train,train_receipt=source15.collect_all_branches(TRAIN,upstream)
    val,val_receipt=source15.collect_all_branches(VALIDATION,upstream)
    source_blind=[]
    for seed in DEV:
        for anchor in ANCHORS:
            # Same source-blind ORIGINAL RANDOM chosen action from the same
            # fixed seed, but never rerun learned on-policy controllers.
            action=choose("RANDOM",seed,anchor,None)
            row=source15.source_branch(seed,anchor,action,upstream,allow_dev=True)
            if not row["valid"]:raise ValueError("FKP15_CONSUMED_REPLAY_PREFIX_INVALID")
            source_blind.append([seed,anchor,action,row["branch_sha256"]])
    return {"schema":"fkp15.consumed-source-replay.v1",
            "train_source_sha256":train_receipt["source_receipt_sha256"],
            "val_source_sha256":val_receipt["source_receipt_sha256"],
            "source_blind_random_original_dev":source_blind,
            "protected_first_use":False,"scientific_pass":False,
            "classification":"CONSUMED_PUBLIC_SOURCE_REPLAY_ONLY"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--public-dev",action="store_true")
    p.add_argument("--replay-consumed",action="store_true")
    p.add_argument("--protected",action="store_true")
    p.add_argument("--upstream-root",type=Path,required=True)
    args=p.parse_args()
    if args.protected or args.public_dev==args.replay_consumed:
        p.error("FKP15_ONLY_ONE_PUBLIC_OR_CONSUMED_MODE; PROTECTED_DISARMED")
    result=(run if args.public_dev else replay_consumed)(args.upstream_root.resolve())
    print(json.dumps(result,sort_keys=True))
