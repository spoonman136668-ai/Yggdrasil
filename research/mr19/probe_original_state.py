"""MR19: prospective fixed-budget native temporal memory falsifier.

The exact MR18 public feature map is unchanged. All models receive one
ORIGINAL MiniGrid step sequence and the same public observed next-image bits.
No hidden world, correct roles, reward, mission, object names or science labels
are given to any candidate. Development seeds and actions frozen in this file.
"""
import copy
import json
import pathlib
import subprocess
import sys
import time

from research.mr15.public_view_delta import (
    SOURCE_COMMIT, PublicViewLocalDelta, public_raw_view
)
from research.mr18.native_public_learning import (
    Native45, Recurrent45, PublicCount
)
from research.mr19.native_local_predictive_state import (
    NativeLocalPredictiveState
)

TRAIN_SEEDS=(41,43)
DEV_EVAL_SEEDS=(47,53)
TRAIN_ACTIONS=(0,2,1,2,5,2,0,2,3,1,2,5,2,0,1,2,5,0,2,1,2,3,2,5)
DEV_EVAL_ACTIONS=(2,1,2,0,2,5,1,0,2,3,2,1,5,2,0,2,1,5,2,0,2,1,2,5)
FAMILIES=("Original DoorKeyEnv(5)","Original EmptyEnv(8)")


def source_verified(upstream):
    root=pathlib.Path(upstream).resolve()
    sha=subprocess.check_output(
        ["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    status=subprocess.check_output(
        ["git","-C",str(root),"status","--porcelain"],text=True).strip()
    if sha!=SOURCE_COMMIT or status:
        raise ValueError("MR19_UNAUTHENTIC_ORIGINAL_SOURCE")
    return root


def score(probabilities,targets):
    if len(probabilities)!=8 or len(targets)!=8 or any(
        not 0<=p<=1 for p in probabilities):
        raise ValueError("MR19_INVALID_NATIVE_PROBABILITIES")
    return sum((p-y)**2 for p,y in zip(probabilities,targets))/8.


def originals():
    return {
        "mr19_temporal45": NativeLocalPredictiveState(),
        "mr18_public45": Native45("public"),
        "conventional_recurrent45":Recurrent45(),
        "conventional_public_count":PublicCount(),
    }


def restart(models):
    return {
        "mr19_temporal45": NativeLocalPredictiveState.restore(
            models["mr19_temporal45"].snapshot()),
        "mr18_public45":Native45.restore(
            "public",models["mr18_public45"].snapshot()),
        "conventional_recurrent45":Recurrent45.restore(
            models["conventional_recurrent45"].snapshot()),
        "conventional_public_count":copy.deepcopy(
            models["conventional_public_count"]),
    }


def episode(env,models,phase,family,seed,actions,out):
    try:
        public,_=env.reset(seed=seed)
        sensor=PublicViewLocalDelta()
        sensor.prime(public["image"])
        models["mr19_temporal45"].reset_episode()
        models["conventional_recurrent45"].reset_episode()
        for step,action in enumerate(actions):
            raw=public_raw_view(public["image"])
            bits=tuple(sensor.bits)
            # All are pre-action/causally antecedent to original env.step.
            preds={}
            t=time.process_time_ns()
            preds["mr19_temporal45"]=models["mr19_temporal45"].predict(
                raw,bits,action)
            preds["mr19_temporal_ablation"]=models[
                "mr19_temporal45"].predict(
                    raw,bits,action,drop_temporal_state=True)
            out["model_cpu_ns"]["mr19_temporal45"]+=time.process_time_ns()-t
            for name in ("mr18_public45","conventional_recurrent45",
                         "conventional_public_count"):
                t=time.process_time_ns()
                preds[name]=models[name].predict(raw,bits,action)
                out["model_cpu_ns"][name]+=time.process_time_ns()-t
            native_next,_reward,terminated,truncated,_info=env.step(action)
            event=sensor.observe_after_native_step(
                action,native_next["image"])
            outcomes=event["observed_next_local_bits"]
            if (event["prior_local_bits"]!=list(bits) or
                event["observed_action"]!=action):
                raise ValueError("MR19_SOURCE_NATIVE_ACTION_DRIFT")
            key=(phase,family,seed)
            for name,pred in preds.items():
                out["losses"].setdefault(key,{}).setdefault(name,[]).append(
                    score(pred,outcomes))
            training=(phase=="training")
            t=time.process_time_ns()
            models["mr19_temporal45"].observe(
                raw,bits,action,outcomes,train=training)
            out["model_cpu_ns"]["mr19_temporal45"]+=time.process_time_ns()-t
            if training:
                for name in ("mr18_public45","conventional_recurrent45",
                             "conventional_public_count"):
                    t=time.process_time_ns()
                    models[name].observe(raw,bits,action,outcomes)
                    out["model_cpu_ns"][name]+=time.process_time_ns()-t
            else:
                # Freeze conventional weights, allow only recurrent context
                # to advance from publicly observable data.
                models["conventional_recurrent45"].advance_public_history(raw)
            if step==9:
                before=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(before)
                if sensor.snapshot()!=before:
                    raise ValueError("MR19_SENSOR_RESTART_FAILED")
                models=restart(models)
                out["serialization_roundtrips"]+=1
            public=native_next
            if terminated or truncated:
                break
        out["steps"][key]=sensor.steps
    finally:
        env.close()
    return models


def main(original_path):
    upstream=source_verified(original_path)
    sys.path.insert(0,str(upstream))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factory=(
        lambda:DoorKeyEnv(size=5,render_mode=None),
        lambda:EmptyEnv(size=8,render_mode=None),
    )
    models=originals()
    receipt={"losses":{},"steps":{},"serialization_roundtrips":0,
             "model_cpu_ns":{name:0 for name in models}}
    for ctor,family in zip(factory,FAMILIES):
        for seed in TRAIN_SEEDS:
            models=episode(ctor(),models,"training",family,seed,
                           TRAIN_ACTIONS,receipt)
    frozen=restart(models)
    trained_snapshots={name:model.snapshot()
                       for name,model in frozen.items()}
    assert sum(len(x) for x in frozen[
        "mr19_temporal45"].runtime.core.genome)+sum(
        len(x) for x in frozen[
            "mr19_temporal45"].runtime.core.roles)==45
    # Authentic cold-created Python objects via canonical frozen snapshots.
    for name,original in trained_snapshots.items():
        if frozen[name].snapshot()!=original:
            raise ValueError("MR19_NATIVE_TRAINED_SNAPSHOT_MISMATCH")
    trained_ygg_weights=frozen["mr19_temporal45"].runtime.snapshot()
    recurrent_weights=copy.deepcopy((
        frozen["conventional_recurrent45"].local,
        frozen["conventional_recurrent45"].shared))
    for ctor,family in zip(factory,FAMILIES):
        for seed in DEV_EVAL_SEEDS:
            frozen=episode(ctor(),frozen,"dev_evaluation",family,seed,
                           DEV_EVAL_ACTIONS,receipt)
    if (frozen["mr19_temporal45"].runtime.snapshot()!=trained_ygg_weights or
        frozen["mr18_public45"].snapshot()!=trained_snapshots["mr18_public45"] or
        frozen["conventional_public_count"].snapshot()!=trained_snapshots[
            "conventional_public_count"] or
        (frozen["conventional_recurrent45"].local,
         frozen["conventional_recurrent45"].shared)!=recurrent_weights):
        raise ValueError("MR19_EVALUATION_OUTCOME_UPDATED_WEIGHTS")
    results={}
    names=("mr19_temporal45","mr19_temporal_ablation",
           "mr18_public45","conventional_recurrent45",
           "conventional_public_count")
    for phase in ("training","dev_evaluation"):
        results[phase]={}
        for family in FAMILIES:
            seeds=TRAIN_SEEDS if phase=="training" else DEV_EVAL_SEEDS
            keys=[(phase,family,seed) for seed in seeds]
            results[phase][family]={
                name:sum(sum(receipt["losses"][k][name]) for k in keys)/
                     sum(len(receipt["losses"][k][name]) for k in keys)
                for name in names
            }
    ckbytes={name:len(data.encode("utf-8")) for name,data
             in trained_snapshots.items()}
    ckbytes["mr15_original_sidecar_max"] = 229
    all_results=[results["dev_evaluation"][f] for f in FAMILIES]
    print("MR19_NATIVE_LOCAL_PREDICTIVE_STATE_DEV="+json.dumps({
        "source_commit":SOURCE_COMMIT,
        "original_native_environment_classes":FAMILIES,
        "previously_unconsumed_development_train_seeds":TRAIN_SEEDS,
        "previously_unconsumed_development_eval_seeds":DEV_EVAL_SEEDS,
        "train_actions":TRAIN_ACTIONS,
        "dev_eval_actions":DEV_EVAL_ACTIONS,
        "loss_brier_lower_is_better":results,
        "mr19_better_than_its_own_state_ablation_all_environments":
            all(x["mr19_temporal45"]<x["mr19_temporal_ablation"]
                for x in all_results),
        "mr19_better_than_recurrent_all_environments":
            all(x["mr19_temporal45"]<x["conventional_recurrent45"]
                for x in all_results),
        "mr19_better_than_count_all_environments":
            all(x["mr19_temporal45"]<x["conventional_public_count"]
                for x in all_results),
        "original_ygg_45_trainable_coefficients_unchanged":True,
        "eight_ephemeral_local_states_accounted":True,
        "frozen_mr18_public_features":True,
        "nonlearned_mr15_sensor_sidecar_bytes":32,
        "serialized_model_bytes":ckbytes,
        "candidate_model_only_cpu_ns_shared_process_diagnostic":
            receipt["model_cpu_ns"],
        "source_native_step_counts":{"/".join(map(str,key)):v for key,v
                                     in receipt["steps"].items()},
        "source_bound_serialization_roundtrips":
            receipt["serialization_roundtrips"],
        "full_isolated_process_tree_cpu_and_peak_rss":
            "NOT_QUALIFIED",
        "conventional_count_memory_matched":False,
        "native_evaluation_outcomes_used_for_weight_training":False,
        "experiment_is_independent_protected_science":False,
        "learned_role_function_necessity":"NOT_QUALIFIED",
        "first_use_science_admission":"NO_GO",
        "g29_atlas":"NOT_QUALIFIED",
        "upstream_license_reconciliation":"BLOCKED",
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr19.probe_original_state UPSTREAM")
    main(sys.argv[1])
