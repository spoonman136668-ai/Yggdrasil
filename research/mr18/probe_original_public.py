"""MR18 original MiniGrid prospective DEV-only training and evaluation.

Freeze all representation, action scripts and seed partitions in Git BEFORE
running. Evaluation events are never supplied for weight updates, early
stopping, feature selection or reruns with tuning. This is NOT protected first
use or independently unknown task-family transfer.
"""
import copy
import json
import pathlib
import subprocess
import sys
import time

from research.mr15.public_view_delta import (
    PublicViewLocalDelta, SOURCE_COMMIT, public_raw_view
)
from research.mr18.native_public_learning import (
    Native45, Recurrent45, PublicCount, REPRESENTATION, public_features
)

TRAIN_SEEDS = (23,29)
EVAL_SEEDS = (31,37)
TRAIN_ACTIONS = (0,2,1,2,5,0,2,1,3,2,0,2,5,1,2,0,2,1,2,5,0,2,1,2)
EVAL_ACTIONS = (2,0,2,1,5,2,0,2,1,2,3,5,2,0,1,2,2,5,1,0,2,1,2,5)
FAMILIES = ("Original DoorKeyEnv(5)","Original EmptyEnv(8)")


def source_verified(upstream):
    root=pathlib.Path(upstream).resolve()
    head=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                                 text=True).strip()
    status=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],
                                   text=True).strip()
    if head!=SOURCE_COMMIT or status:
        raise ValueError("MR18_ORIGINAL_SOURCE_CUSTODY_FAILURE")
    return root


def make_models():
    return {
        "ygg_public_45":Native45("public"),
        "ygg_coarse_45":Native45("coarse"),
        "recurrent_45":Recurrent45(),
        "conditional_public_count":PublicCount(),
    }


def clone_models(models):
    # Restoration before evaluation is obligatory; no carrying through
    # in-process model objects or hiding the snapshot/memory costs.
    return {
        "ygg_public_45":Native45.restore(
            "public",models["ygg_public_45"].snapshot()),
        "ygg_coarse_45":Native45.restore(
            "coarse",models["ygg_coarse_45"].snapshot()),
        "recurrent_45":Recurrent45.restore(
            models["recurrent_45"].snapshot()),
        "conditional_public_count":copy.deepcopy(
            models["conditional_public_count"]),
    }


def brier(probs,targets):
    if len(probs)!=8 or len(targets)!=8:
        raise ValueError("MR18_BAD_PROBABILITY_VECTOR")
    if any(not 0<=p<=1 for p in probs):
        raise ValueError("MR18_INVALID_PROBABILITY")
    return sum((p-y)**2 for p,y in zip(probs,targets))/8.


def episode(env, models, actions, training, phase, family, seed, receipt):
    try:
        public_obs,_=env.reset(seed=seed)
        sensor=PublicViewLocalDelta()
        sensor.prime(public_obs["image"])
        models["recurrent_45"].reset_episode()
        n=0
        for step,action in enumerate(actions):
            raw=public_raw_view(public_obs["image"])
            bits=tuple(sensor.bits)
            prior_snapshot=sensor.snapshot()
            predictions={}
            for name,model in models.items():
                start=time.process_time_ns()
                predictions[name]=model.predict(raw,bits,action)
                receipt["cpu_model_ns"][name]+=time.process_time_ns()-start
            # All model predictions frozen before the ORIGINAL env executes.
            next_obs,_reward,terminated,truncated,_info=env.step(action)
            event=sensor.observe_after_native_step(
                action,next_obs["image"])
            if event["prior_local_bits"]!=list(bits) or event["observed_action"]!=action:
                raise ValueError("MR18_NATIVE_EVENT_ORDER_VIOLATION")
            outcomes=event["observed_next_local_bits"]
            key=(phase,family,seed)
            for name,probs in predictions.items():
                receipt["losses"].setdefault(key,{}).setdefault(name,[]).append(
                    brier(probs,outcomes))
            if training:
                for name,model in models.items():
                    start=time.process_time_ns()
                    model.observe(raw,bits,action,outcomes)
                    receipt["cpu_model_ns"][name]+=time.process_time_ns()-start
            else:
                models["recurrent_45"].advance_public_history(raw)
            if step==7:
                snap=sensor.snapshot()
                restored=PublicViewLocalDelta.restore(snap)
                if restored.snapshot()!=snap:
                    raise ValueError("MR18_SENSOR_COLD_RESTART_FAILURE")
                sensor=restored
                receipt["sensor_restores"]+=1
            if prior_snapshot==sensor.snapshot():
                raise ValueError("MR18_NO_SOURCE_SENSOR_PROGRESS")
            n+=1
            public_obs=next_obs
            if terminated or truncated:
                break
        if n==0:
            raise ValueError("MR18_EMPTY_ORIGINAL_ENVIRONMENT")
        receipt["steps"][key]=n
    finally:
        env.close()


def main(source_path):
    root=source_verified(source_path)
    sys.path.insert(0,str(root))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    creators=(lambda: DoorKeyEnv(size=5,render_mode=None),
              lambda: EmptyEnv(size=8,render_mode=None))
    # Explicit fixed feature budget / no privileged key or object decoder.
    assert len(public_features((0,)*24,(0,)*8,0,0))==7
    assert public_features((0,)*24,(0,)*8,0,0)!=public_features(
        (1,0,0)+(0,)*21,(0,)*8,0,0)
    models=make_models()
    receipt={"losses":{},"cpu_model_ns":{name:0 for name in models},
             "steps":{},"sensor_restores":0}
    for creator,family in zip(creators,FAMILIES):
        for seed in TRAIN_SEEDS:
            episode(creator(),models,TRAIN_ACTIONS,True,"train",
                    family,seed,receipt)
    original_snapshots={name:m.snapshot() for name,m in models.items()}
    # Confirm unchanged 45-parameter model and complete cold restart.
    models=clone_models(models)
    assert all(models[name].snapshot()==original_snapshots[name]
               for name in models)
    frozen_public=models["ygg_public_45"].snapshot()
    frozen_coarse=models["ygg_coarse_45"].snapshot()
    frozen_count=models["conditional_public_count"].snapshot()
    frozen_recurrent_weights=copy.deepcopy((
        models["recurrent_45"].local,models["recurrent_45"].shared))
    # Evaluation native targets are used ONLY for retrospective scoring.
    for creator,family in zip(creators,FAMILIES):
        for seed in EVAL_SEEDS:
            episode(creator(),models,EVAL_ACTIONS,False,"evaluation",
                    family,seed,receipt)
    if (models["ygg_public_45"].snapshot()!=frozen_public or
        models["ygg_coarse_45"].snapshot()!=frozen_coarse or
        models["conditional_public_count"].snapshot()!=frozen_count or
        (models["recurrent_45"].local,models["recurrent_45"].shared)!=
        frozen_recurrent_weights):
        raise ValueError("MR18_EVALUATION_FEEDBACK_LEAK")
    scores={}
    for phase in ("train","evaluation"):
        scores[phase]={}
        for family in FAMILIES:
            keys=[(phase,family,seed) for seed in (
                TRAIN_SEEDS if phase=="train" else EVAL_SEEDS)]
            scores[phase][family]={
                name:sum(sum(receipt["losses"][k][name]) for k in keys)/
                         sum(len(receipt["losses"][k][name]) for k in keys)
                for name in models
            }
    snapshots={name:len(payload.encode("utf-8"))
               for name,payload in original_snapshots.items()}
    candidate_loss=sum(scores["evaluation"][f]["ygg_public_45"]
                       for f in FAMILIES)/len(FAMILIES)
    coarse_loss=sum(scores["evaluation"][f]["ygg_coarse_45"]
                    for f in FAMILIES)/len(FAMILIES)
    recurrent_loss=sum(scores["evaluation"][f]["recurrent_45"]
                       for f in FAMILIES)/len(FAMILIES)
    count_loss=sum(scores["evaluation"][f]["conditional_public_count"]
                   for f in FAMILIES)/len(FAMILIES)
    print("MR18_PROSPECTIVE_NATIVE_PUBLIC_LEARNING="+json.dumps({
        "source_commit":SOURCE_COMMIT,
        "frozen_representation":REPRESENTATION,
        "train_seeds":TRAIN_SEEDS,"development_evaluation_seeds":EVAL_SEEDS,
        "train_actions":TRAIN_ACTIONS,"evaluation_actions":EVAL_ACTIONS,
        "scores_brier_lower_better":scores,
        "public_model_vs_original_coarse_improved":candidate_loss<coarse_loss,
        "public_model_better_than_recurrent45":candidate_loss<recurrent_loss,
        "public_model_better_than_count":candidate_loss<count_loss,
        "original_ygg_public_model_trainable_coefficients":45,
        "original_coarse_model_trainable_coefficients":45,
        "conventional_recurrent_trainable_coefficients":45,
        "nonlearned_sensor_sidecar_bytes":32,
        "snapshot_serialized_bytes":snapshots,
        "model_only_cpu_ns_shared_process_diagnostic":receipt["cpu_model_ns"],
        "complete_all_in_per_candidate_CPU_peak_RSS":"NOT_QUALIFIED",
        "sensor_cold_restart_checks":receipt["sensor_restores"],
        "all_native_step_counts":{"/".join(map(str,k)):v
                                  for k,v in receipt["steps"].items()},
        "native_training_from_prior_public_images_only":True,
        "evaluation_feedback_to_models":False,
        "external_independent_scientific_first_use":False,
        "strong_public_source_inspection_control":"NOT_QUALIFIED",
        "g29_atlas":"NOT_QUALIFIED",
        "licensing_redistribution":"BLOCKED_UNRESOLVED_UPSTREAM",
        "scientific_admission":"NO_GO",
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr18.probe_original_public UPSTREAM")
    main(sys.argv[1])
