"""MR21: original MiniGrid learned-retention versus fixed-retention development test.

All native action sequences and development seeds are frozen in code before
execution. No protected scientific first use. Original MR20 negatives remain.
The eight retained slots are CAMERA RELATIVE, not physical specialist cells.
No correctness threshold based on the expected favorable answer: negative
comparison must PASS engineering acceptance and be retained.
"""
import copy
import json
import pathlib
import subprocess
import sys

from research.mr15.public_view_delta import (
    PublicViewLocalDelta, public_raw_view, SOURCE_COMMIT
)
from research.mr19.native_local_predictive_state import NativeLocalPredictiveState
from research.mr18.native_public_learning import Recurrent45, PublicCount, Native45
from research.mr21.native_learned_retention import LearnedRetention

TRAIN_SEEDS=(73,79)
EVALUATION_SEEDS=(83,89)
TRAIN_ACTIONS=(0,2,1,2,5,2,0,2,1,3,2,5,0,2,1,2,5,2,0,1,2,5,1,2)
EVAL_ACTIONS=(2,1,0,2,5,2,0,1,2,3,5,2,1,2,0,2,5,1,0,2,2,1,5,2)
FAMILIES=("Original DoorKeyEnv(5)","Original EmptyEnv(8)")
PREDICTORS=("learned_write","fixed_write","mr19_all_history",
            "recurrent_45","public_count","feedforward_45")


def verify_source(path):
    root=pathlib.Path(path).resolve()
    sha=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                                text=True).strip()
    status=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],
                                   text=True).strip()
    if sha!=SOURCE_COMMIT or status:
        raise ValueError("MR21_SOURCE_CUSTODY_INVALID")
    return root


def models_new():
    return {
        "learned_write":LearnedRetention(learn_selection=True),
        "fixed_write":LearnedRetention(learn_selection=False),
        "mr19_all_history":NativeLocalPredictiveState(),
        "recurrent_45":Recurrent45(),
        "public_count":PublicCount(),
        "feedforward_45":Native45("public"),
    }


def cold_models(models):
    return {
        "learned_write":LearnedRetention.restore(
            models["learned_write"].snapshot()),
        "fixed_write":LearnedRetention.restore(
            models["fixed_write"].snapshot()),
        "mr19_all_history":NativeLocalPredictiveState.restore(
            models["mr19_all_history"].snapshot()),
        "recurrent_45":Recurrent45.restore(
            models["recurrent_45"].snapshot()),
        "public_count":copy.deepcopy(models["public_count"]),
        "feedforward_45":Native45.restore(
            "public",models["feedforward_45"].snapshot()),
    }


def brier(p,y):
    if len(p)!=8 or len(y)!=8 or any(not 0<=v<=1 for v in p):
        raise ValueError("MR21_INVALID_PRE_ACTION_PREDICTION")
    return sum((a-b)**2 for a,b in zip(p,y))/8


def episode(env, models, family, seed, actions, training, metrics):
    try:
        obs,_=env.reset(seed=seed)
        sensor=PublicViewLocalDelta()
        sensor.prime(obs["image"])
        for k in ("learned_write","fixed_write","mr19_all_history",
                  "recurrent_45"):
            models[k].reset_episode()
        phase="train" if training else "dev_eval"
        for step,action in enumerate(actions):
            raw=public_raw_view(obs["image"])
            bits=tuple(sensor.bits)
            pre={
                "learned_write":models["learned_write"].predictions(
                    raw,bits,action)[0],
                "fixed_write":models["fixed_write"].predictions(
                    raw,bits,action)[0],
                "mr19_all_history":models["mr19_all_history"].predict(
                    raw,bits,action),
                "recurrent_45":models["recurrent_45"].predict(
                    raw,bits,action),
                "public_count":models["public_count"].predict(
                    raw,bits,action),
                "feedforward_45":models["feedforward_45"].predict(
                    raw,bits,action),
            }
            pre_zero=models["learned_write"].predictions(
                raw,bits,action)[1]
            pre_gates=models["learned_write"].predictions(
                raw,bits,action)[2]
            next_obs,_reward,terminated,truncated,_info=env.step(action)
            native=sensor.observe_after_native_step(action,next_obs["image"])
            if (native["source_commit"]!=SOURCE_COMMIT or
                native["prior_local_bits"]!=list(bits) or
                native["observed_action"]!=action):
                raise ValueError("MR21_NATIVE_PUBLIC_CONSEQUENCE_DRIFT")
            y=native["observed_next_local_bits"]
            key=(phase,family,seed)
            for name in PREDICTORS:
                metrics["losses"].setdefault(key,{}).setdefault(
                    name,[]).append(brier(pre[name],y))
            metrics["losses"][key].setdefault(
                "learned_write_zero_ablated",[]).append(brier(pre_zero,y))
            if not training:
                metrics["gate_summaries"].append({
                    "source":family,"seed":seed,"action":action,
                    "mean_pre_action_write_gate":
                        sum(pre_gates)/len(pre_gates),
                })
            if (models["learned_write"].step_after_native(
                    raw,bits,action,y,training)[0]!=pre["learned_write"] or
                models["fixed_write"].step_after_native(
                    raw,bits,action,y,training)[0]!=pre["fixed_write"]):
                raise ValueError("MR21_PRE_OUTCOME_PREDICTION_MISMATCH")
            models["mr19_all_history"].observe(raw,bits,action,y,
                                               train=training)
            if training:
                for name in ("recurrent_45","public_count","feedforward_45"):
                    models[name].observe(raw,bits,action,y)
            else:
                models["recurrent_45"].advance_public_history(raw)
            if step==10:
                state=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(state)
                if sensor.snapshot()!=state:
                    raise ValueError("MR21_NATIVE_SENSOR_RESTART_MISMATCH")
                models=cold_models(models)
                metrics["cold_restart_checks"]+=1
            obs=next_obs
            if terminated or truncated:
                break
        metrics["native_steps"][key]=sensor.steps
    finally:
        env.close()
    return models


def main(original):
    root=verify_source(original)
    sys.path.insert(0,str(root))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    creators=(lambda:DoorKeyEnv(size=5,render_mode=None),
              lambda:EmptyEnv(size=8,render_mode=None))
    models=models_new()
    m={"losses":{},"native_steps":{},"cold_restart_checks":0,
       "gate_summaries":[]}
    for factory,family in zip(creators,FAMILIES):
        for seed in TRAIN_SEEDS:
            models=episode(factory(),models,family,seed,TRAIN_ACTIONS,True,m)
    saved={name:obj.snapshot() for name,obj in models.items()}
    models=cold_models(models)
    if any(models[name].snapshot()!=saved[name] for name in models):
        raise ValueError("MR21_MODEL_COLD_RELOAD_DRIFT")
    # Learned weights are frozen for evaluation and remain unchanged.
    frozen_model={
        "learned_write":models["learned_write"].native.snapshot(),
        "fixed_write":models["fixed_write"].native.snapshot(),
        "mr19_all_history":models["mr19_all_history"].runtime.snapshot(),
        "recurrent_local":copy.deepcopy(models["recurrent_45"].local),
        "recurrent_shared":copy.deepcopy(models["recurrent_45"].shared),
        "public_count":models["public_count"].snapshot(),
        "feedforward_45":models["feedforward_45"].snapshot(),
    }
    for factory,family in zip(creators,FAMILIES):
        for seed in EVALUATION_SEEDS:
            models=episode(factory(),models,family,seed,
                           EVAL_ACTIONS,False,m)
    if (models["learned_write"].native.snapshot()!=frozen_model["learned_write"] or
        models["fixed_write"].native.snapshot()!=frozen_model["fixed_write"] or
        models["mr19_all_history"].runtime.snapshot()!=frozen_model[
            "mr19_all_history"] or
        models["recurrent_45"].local!=frozen_model["recurrent_local"] or
        models["recurrent_45"].shared!=frozen_model["recurrent_shared"] or
        models["public_count"].snapshot()!=frozen_model["public_count"] or
        models["feedforward_45"].snapshot()!=frozen_model["feedforward_45"]):
        raise ValueError("MR21_DEVELOPMENT_EVALUATION_UPDATED_WEIGHTS")
    means={}
    for family in FAMILIES:
        keys=[("dev_eval",family,s) for s in EVALUATION_SEEDS]
        means[family]={
            name:sum(sum(m["losses"][key][name]) for key in keys)/
                 sum(len(m["losses"][key][name]) for key in keys)
            for name in PREDICTORS+("learned_write_zero_ablated",)
        }
    candidate_wins={
        "learned_write_better_than_fixed_write_in_both":all(
            means[f]["learned_write"]<means[f]["fixed_write"] for f in FAMILIES),
        "learned_write_better_than_own_state_zero_in_both":all(
            means[f]["learned_write"]<
            means[f]["learned_write_zero_ablated"] for f in FAMILIES),
        "learned_write_better_than_recurrent_in_both":all(
            means[f]["learned_write"]<means[f]["recurrent_45"] for f in FAMILIES),
        "learned_write_better_than_count_in_both":all(
            means[f]["learned_write"]<means[f]["public_count"] for f in FAMILIES),
    }
    print("MR21_NATIVE_LEARNED_RETENTION_DEV="+json.dumps({
        "original_native_source_commit":SOURCE_COMMIT,
        "source_environments":FAMILIES,
        "training_seeds":TRAIN_SEEDS,
        "evaluation_seeds_dev_only":EVALUATION_SEEDS,
        "training_actions":TRAIN_ACTIONS,
        "evaluation_actions":EVAL_ACTIONS,
        "native_development_evaluation_Brier":means,
        "prospective_development_conditions":candidate_wins,
        "original_model_trainable_coefficients":45,
        "ephemeral_memories":8,
        "original_sensor_sidecar_bytes":32,
        "serialized_trained_model_snapshots_bytes":{
            name:len(s.encode()) for name,s in saved.items()},
        "source_native_steps":{"/".join(map(str,k)):v for k,v
                               in m["native_steps"].items()},
        "native_model_and_sensor_cold_restart_checks":
            m["cold_restart_checks"],
        "eight_slots_are_camera_relative_not_world_cells":True,
        "write_selection_uses_delayed_local_predictive_utility_surrogate":True,
        "learned_history_gating_is_not_exact_action_credit":True,
        "native_future_or_privileged_labels_consumed":False,
        "all_in_cpu_peak_rss_wire":"NOT_QUALIFIED",
        "count_memory_budget_matched":False,
        "source_license_discrepancy":"UNRESOLVED",
        "original_g29_atlas":"NOT_QUALIFIED",
        "scientific_first_use":False,
        "scientific_admission":"NO_GO",
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr21.probe_native_retention UPSTREAM")
    main(sys.argv[1])
