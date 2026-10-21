"""MR20: native state-necessity audit using frozen MR19 learning mechanism.

Development falsifier, NOT protected scientific first use. Train on MR19's
pre-existing development-only data; freeze all learned weights, then use newly
predeclared source-native episode histories. At each pre-action prediction,
compare intact, instantaneous state-zeroed, and cell-state-permuted predictions
with precisely identical model weights, public observation, action and history.
No change to upstream MiniGrid, MR15 sensor, MR19 recurrence, or MR18 features.
"""
import copy
import hashlib
import json
import pathlib
import subprocess
import sys
import time

from research.mr15.public_view_delta import (
    PublicViewLocalDelta, SOURCE_COMMIT, public_raw_view
)
from research.mr18.native_public_learning import Native45, Recurrent45, PublicCount
from research.mr19.native_local_predictive_state import NativeLocalPredictiveState
from research.mr19.probe_original_state import TRAIN_SEEDS, TRAIN_ACTIONS

SCHEMA="yggdrasil.mr20.native-state-necessity.dev.v1"
# Frozen before any MR20 execution. Not independently protected first-use.
EVAL_SEEDS=(59,61,67,71)
EVAL_ACTIONS=(2,0,2,1,5,2,2,0,1,3,2,5,0,2,1,2,5,2,0,1,2,2,5,1)
FAMILIES=("Original DoorKeyEnv(5)","Original EmptyEnv(8)")
MODELS=("mr19_temporal","mr19_zero","mr19_rotated","mr18_feedforward",
        "recurrent45","public_count")


def original_source(path):
    root=pathlib.Path(path).resolve()
    sha=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                                text=True).strip()
    status=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],
                                   text=True).strip()
    if sha!=SOURCE_COMMIT or status:
        raise ValueError("MR20_EXTERNAL_NATIVE_SOURCE_NOT_AUTHENTIC")
    return root


def setup():
    return {
        "mr19_temporal":NativeLocalPredictiveState(),
        "mr18_feedforward":Native45("public"),
        "recurrent45":Recurrent45(),
        "public_count":PublicCount(),
    }


def cloned(models):
    return {
        "mr19_temporal":NativeLocalPredictiveState.restore(
            models["mr19_temporal"].snapshot()),
        "mr18_feedforward":Native45.restore(
            "public",models["mr18_feedforward"].snapshot()),
        "recurrent45":Recurrent45.restore(
            models["recurrent45"].snapshot()),
        "public_count":copy.deepcopy(models["public_count"]),
    }


def brier(vector,target):
    if len(vector)!=8 or len(target)!=8 or any(
        type(p) not in (int,float) or not 0<=p<=1 for p in vector):
        raise ValueError("MR20_BAD_PREDICTION")
    return sum((p-y)**2 for p,y in zip(vector,target))/8


def run_one(env,seed,actions,models,training,family,receipt):
    try:
        obs,_=env.reset(seed=seed)
        sensor=PublicViewLocalDelta()
        sensor.prime(obs["image"])
        models["mr19_temporal"].reset_episode()
        models["recurrent45"].reset_episode()
        namespace="training" if training else "evaluation"
        key=(namespace,family,seed)
        history=[]
        for j,action in enumerate(actions):
            before_raw=public_raw_view(obs["image"])
            before_bits=tuple(sensor.bits)
            if sensor.steps!=j:
                raise ValueError("MR20_SENSOR_STEP_DRIFT")
            # Native prediction happens before the original action.
            model=models["mr19_temporal"]
            pre_weights=model.runtime.snapshot()
            t=time.process_time_ns()
            intact=model.predict(before_raw,before_bits,action)
            zero=model.predict(before_raw,before_bits,action,
                               drop_temporal_state=True)
            rotated=NativeLocalPredictiveState.restore(model.snapshot())
            rotated.state=rotated.state[1:]+rotated.state[:1]
            rotated_prediction=rotated.predict(before_raw,before_bits,action)
            receipt["candidate_cpu_ns"]+=time.process_time_ns()-t
            conventional={
                "mr18_feedforward":models["mr18_feedforward"].predict(
                    before_raw,before_bits,action),
                "recurrent45":models["recurrent45"].predict(
                    before_raw,before_bits,action),
                "public_count":models["public_count"].predict(
                    before_raw,before_bits,action),
            }
            if model.runtime.snapshot()!=pre_weights:
                raise ValueError("MR20_PREDICTION_MUTATED_TRAINED_WEIGHTS")
            native_next,reward,terminated,truncated,info=env.step(action)
            event=sensor.observe_after_native_step(action,native_next["image"])
            if (event["prior_local_bits"]!=list(before_bits) or
                event["observed_action"]!=action or
                event["source_commit"]!=SOURCE_COMMIT):
                raise ValueError("MR20_ORIGINAL_NATIVE_EVENT_MISMATCH")
            y=event["observed_next_local_bits"]
            pred={
                "mr19_temporal":intact,
                "mr19_zero":zero,
                "mr19_rotated":rotated_prediction,
                **conventional,
            }
            receipt["scores"].setdefault(key,{})
            for name in MODELS:
                receipt["scores"][key].setdefault(name,[]).append(
                    brier(pred[name],y))
            if not training:
                for i in range(8):
                    row=receipt["per_cell"]
                    row["intact"][i].append((intact[i]-y[i])**2)
                    row["zero"][i].append((zero[i]-y[i])**2)
                    row["rotated"][i].append((rotated_prediction[i]-y[i])**2)
                history.append({
                    "original_source_event_step":j,
                    "model_input":(list(before_bits),action),
                    "prior_public_sample_sha256":hashlib.sha256(
                        bytes(before_raw)).hexdigest(),
                    "history_before_action_sha256":hashlib.sha256(
                        model.snapshot().encode()).hexdigest(),
                    "next_source_public_delta":list(y),
                })
            t=time.process_time_ns()
            model.observe(before_raw,before_bits,action,y,train=training)
            receipt["candidate_cpu_ns"]+=time.process_time_ns()-t
            if training:
                for name in ("mr18_feedforward","recurrent45","public_count"):
                    models[name].observe(before_raw,before_bits,action,y)
            else:
                # During evaluation: weights/associations MUST remain frozen.
                # Recurrent activation follows only the previous public input.
                models["recurrent45"].advance_public_history(before_raw)
            if j==9:
                sensor_snapshot=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(sensor_snapshot)
                if sensor.snapshot()!=sensor_snapshot:
                    raise ValueError("MR20_PUBLIC_SENSOR_RESTART_DRIFT")
                # Independent recreated native-model objects, including all
                # episodic history; not mere Python object reassignment.
                models=cloned(models)
                receipt["native_cold_roundtrips"]+=1
            obs=native_next
            if terminated or truncated:
                break
        receipt["native_steps"][key]=sensor.steps
        if not training:
            receipt["histories"][key]=history
    finally:
        env.close()
    return models


def mean(values):
    if not values:
        raise ValueError("MR20_EMPTY_REAL_NATIVE_HISTORY")
    return sum(values)/len(values)


def main(source_path):
    upstream=original_source(source_path)
    sys.path.insert(0,str(upstream))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    constructors=(
        lambda:DoorKeyEnv(size=5,render_mode=None),
        lambda:EmptyEnv(size=8,render_mode=None),
    )
    models=setup()
    r={
        "scores":{},"native_steps":{},"histories":{},
        "candidate_cpu_ns":0,"native_cold_roundtrips":0,
        "per_cell":{x:[[] for _ in range(8)]
                    for x in ("intact","zero","rotated")},
    }
    # Same MR19 original development training, no retuning or new seeds.
    for factory,family in zip(constructors,FAMILIES):
        for seed in TRAIN_SEEDS:
            models=run_one(factory(),seed,TRAIN_ACTIONS,models,True,family,r)
    training_snapshots={k:v.snapshot() for k,v in models.items()}
    models=cloned(models)
    if any(models[k].snapshot()!=training_snapshots[k] for k in models):
        raise ValueError("MR20_TRAINED_MODEL_COLD_RESTORE_FAILED")
    frozen_candidate_weights=models["mr19_temporal"].runtime.snapshot()
    frozen_mr18=models["mr18_feedforward"].snapshot()
    frozen_count=models["public_count"].snapshot()
    frozen_rec_weights=copy.deepcopy(
        (models["recurrent45"].local,models["recurrent45"].shared))
    # All audit histories are newly selected but publicly authored; NOT
    # independently protected, unseen scientific first-use task families.
    for factory,family in zip(constructors,FAMILIES):
        for seed in EVAL_SEEDS:
            models=run_one(factory(),seed,EVAL_ACTIONS,models,False,family,r)
    if (models["mr19_temporal"].runtime.snapshot()!=frozen_candidate_weights or
        models["mr18_feedforward"].snapshot()!=frozen_mr18 or
        models["public_count"].snapshot()!=frozen_count or
        (models["recurrent45"].local,models["recurrent45"].shared)!=
        frozen_rec_weights):
        raise ValueError("MR20_HIDDEN_EVALUATION_LEARNING_LEAK")
    per_source={}
    for family in FAMILIES:
        keys=[("evaluation",family,seed) for seed in EVAL_SEEDS]
        per_source[family]={
            name:mean([v for k in keys for v in r["scores"][k][name]])
            for name in MODELS
        }
    per_cell={
        name:[mean(values) for values in rows]
        for name,rows in r["per_cell"].items()
    }
    scalar_summary={
        "intact_state_beats_zero_ablation_both_sources":all(
            scores["mr19_temporal"]<scores["mr19_zero"]
            for scores in per_source.values()),
        "intact_state_beats_rotated_ablation_both_sources":all(
            scores["mr19_temporal"]<scores["mr19_rotated"]
            for scores in per_source.values()),
        "intact_state_beats_45weight_recurrent_both_sources":all(
            scores["mr19_temporal"]<scores["recurrent45"]
            for scores in per_source.values()),
        "intact_state_beats_equal_data_count_both_sources":all(
            scores["mr19_temporal"]<scores["public_count"]
            for scores in per_source.values()),
        "cells_helped_vs_zero":sum(
            a<b for a,b in zip(per_cell["intact"],per_cell["zero"])),
    }
    # All source-native individual histories get a custody digest; no
    # environment-world internals, goals or rewards in returned receipt.
    historical=json.dumps(
        {"/".join(map(str,k)):v for k,v in r["histories"].items()},
        sort_keys=True,separators=(",",":")).encode()
    out={
        "schema":SCHEMA,"original_source_commit":SOURCE_COMMIT,
        "train_seeds_from_MR19":TRAIN_SEEDS,
        "audit_development_seeds_frozen_before_run":EVAL_SEEDS,
        "eval_actions_frozen_before_run":EVAL_ACTIONS,
        "source_specific_development_brier":per_source,
        "source_native_per_cell_brier":per_cell,
        "necessary_conditions":scalar_summary,
        "native_event_history_sha256":hashlib.sha256(
            historical).hexdigest(),
        "original_source_native_event_counts":{
            "/".join(map(str,k)):v for k,v in r["native_steps"].items()
        },
        "original_trainable_coefficients":45,
        "candidate_episodic_local_activations":8,
        "nontrained_source_sensor_sidecar_bytes":32,
        "trained_serialized_checkpoint_bytes":{
            k:len(v.encode()) for k,v in training_snapshots.items()},
        "native_cold_roundtrips":r["native_cold_roundtrips"],
        "candidate_model_only_cpu_ns_not_all_in":r["candidate_cpu_ns"],
        "source_privileged_world_read":False,
        "no_eval_source_consequence_used_as_model_weight_target":True,
        "original_source_only_public_observation":True,
        "independently_qualified_sci_first_use":False,
        "full_isolated_process_cpu_peak_rss_and_wire":"NOT_QUALIFIED",
        "count_memory_parity":"NOT_QUALIFIED",
        "g29_atlas":"NOT_QUALIFIED",
        "upstream_license_reconciliation":"UNRESOLVED",
        "scientific_admission":"NO_GO",
    }
    print("MR20_NATIVE_LOCAL_STATE_NECESSITY="+json.dumps(out,sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr20.probe_state_necessity UPSTREAM")
    main(sys.argv[1])
