"""MR25: uninterrupted ORIGINAL MiniGrid source histories, fixed 45-budget learning.

Reuses exactly MR24A frozen PUBLIC-only exploration. No evaluator poses,
solver routes, grid coordinates, mission, rewards, object identities, arm IDs,
source answers or future target bits ever enter a model or action selector.

All models see identical public raw 24 bytes, previous 8 observed change
bits and announced native action, predict BEFORE original env.step, receive
its original new public 8 bits only AFTER source step. No protected first-use.
"""
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import time

import psutil

from research.mr15.public_view_delta import PublicViewLocalDelta,SOURCE_COMMIT,public_raw_view
from research.mr18.native_public_learning import Native45,Recurrent45,PublicCount
from research.mr19.native_local_predictive_state import NativeLocalPredictiveState
from research.mr24.natural_history import (
    public_only_action,source_evaluator_private_door
)

ROOT=Path(__file__).resolve().parents[2]
PROTOCOL=ROOT/"research"/"mr25"/"frozen_protocol.json"
SCORE_KEYS=("native_retained","recurrent_control","stateless_control",
            "conditional_count_control","native_ablated")


def authentic_source(root):
    root=Path(root).resolve()
    head=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip()
    if head!=SOURCE_COMMIT or dirty:
        raise ValueError("MR25_ORIGINAL_SOURCE_CUSTODY_DRIFT")
    return root


def fresh_models():
    return {"native":NativeLocalPredictiveState(),
            "recurrent":Recurrent45(),
            "stateless":Native45("public"),
            "counts":PublicCount()}


def brier(pred,target):
    if len(pred)!=8 or len(target)!=8:
        raise ValueError("MR25_INVALID_SOURCE_TARGET_WIDTH")
    return sum((p-y)**2 for p,y in zip(pred,target))/8.


def trainable_weights_snapshot(models):
    original=json.loads(models["native"].snapshot())
    recurrence=json.loads(models["recurrent"].snapshot())
    return {
        "native":original["native_runtime"]["core"],
        "recurrent":{"local":recurrence["local"],"shared":recurrence["shared"]},
        "stateless":models["stateless"].snapshot(),
        "conditional_count":models["counts"].snapshot()
    }


def original_episode(factory,family,seed,limit,models,*,train,meter):
    from minigrid.core.world_object import Key
    env=factory()
    rng=random.Random(1000003*seed+337)
    proc=psutil.Process()
    try:
        view,_=env.reset(seed=seed)
        sensor=PublicViewLocalDelta()
        sensor.prime(view["image"])
        models["native"].reset_episode()
        models["recurrent"].reset_episode()
        # EVALUATOR PRIVATE: only inspected AFTER env.step; no influence on
        # the frozen public-only action generator or model inputs.
        source_door=source_evaluator_private_door(env) if family=="DoorKeyEnv(size=8)" else None
        losses={name:[] for name in SCORE_KEYS}
        after_unlock_losses={name:[] for name in SCORE_KEYS}
        event_hash=hashlib.sha256()
        source_pickup=0
        source_unlock=0
        source_public_pickup=0
        source_public_unlock=0
        prior_has_key=False
        unlocked_before=False
        event_count=0
        original_source_ended=False
        for idx in range(limit):
            if sensor.steps!=idx:
                raise ValueError("MR25_NATIVE_STEP_HISTORY_DISCONTINUITY")
            prior_raw=public_raw_view(view["image"])
            prior_bits=tuple(sensor.bits)
            # Frozen MR24A policy receives PUBLIC original observation ONLY.
            action=public_only_action(view,rng)
            tick=time.process_time_ns()
            predictions={
                "native_retained":models["native"].predict(prior_raw,prior_bits,action),
                "native_ablated":models["native"].predict(
                    prior_raw,prior_bits,action,drop_temporal_state=True),
                "recurrent_control":models["recurrent"].predict(
                    prior_raw,prior_bits,action),
                "stateless_control":models["stateless"].predict(
                    prior_raw,prior_bits,action),
                "conditional_count_control":models["counts"].predict(
                    prior_raw,prior_bits,action),
            }
            meter["prediction_cpu_ns"]+=time.process_time_ns()-tick

            # Source step is REAL and uninterrupted; no setting env.agent_pos,
            # env.agent_dir, env.grid, env.carrying, or environment reset midrun.
            next_view,_reward,ended,truncated,_info=env.step(action)
            episode_event=sensor.observe_after_native_step(action,next_view["image"])
            after=episode_event["observed_next_local_bits"]
            new_raw=public_raw_view(next_view["image"])
            expected=[int(prior_raw[3*i:3*i+3]!=new_raw[3*i:3*i+3])
                      for i in range(8)]
            if (episode_event["prior_local_bits"]!=list(prior_bits) or
                episode_event["observed_action"]!=action or
                episode_event["source_commit"]!=SOURCE_COMMIT or
                after!=expected or episode_event["privileged_world_fields_consumed"]!=0):
                raise ValueError("MR25_ORIGINAL_PUBLIC_SOURCE_OUTCOME_PROVENANCE")
            event_count+=1
            event_hash.update(bytes([action]+list(prior_bits)+list(after)))
            for name in SCORE_KEYS:
                result=brier(predictions[name],after)
                losses[name].append(result)
                if unlocked_before:
                    after_unlock_losses[name].append(result)
            tick=time.process_time_ns()
            # ALL models obtain same public actual postaction outcomes.
            models["native"].observe(prior_raw,prior_bits,action,after,train=train)
            if train:
                models["recurrent"].observe(prior_raw,prior_bits,action,after)
                models["stateless"].observe(prior_raw,prior_bits,action,after)
                models["counts"].observe(prior_raw,prior_bits,action,after)
            else:
                models["recurrent"].advance_public_history(prior_raw)
            meter["update_cpu_ns"]+=time.process_time_ns()-tick

            # Source grid/object truth is checked ONLY by DIAGNOSTIC EVALUATOR
            # *after* real source step. No value below goes to models/policy.
            key_now=isinstance(env.carrying,Key)
            open_now=bool(source_door.is_open) if source_door is not None else False
            if key_now and not prior_has_key:
                source_pickup+=1
                source_public_pickup+=int(bool(sum(after)))
            if open_now and not unlocked_before:
                source_unlock+=1
                source_public_unlock+=int(bool(sum(after)))
            prior_has_key=key_now
            unlocked_before=open_now
            view=next_view
            meter["sampled_process_rss_max_bytes"]=max(
                meter["sampled_process_rss_max_bytes"],
                proc.memory_info().rss)
            if idx==11:
                snap=sensor.snapshot()
                restored=PublicViewLocalDelta.restore(snap)
                if restored.snapshot()!=snap:
                    raise ValueError("MR25_NATIVE_SOURCE_SENSOR_COLD_RESTART")
                sensor=restored
            if ended or truncated:
                original_source_ended=True
                break

        if event_count==0:
            raise ValueError("MR25_ZERO_ORIGINAL_NATIVE_STEPS")
        return {
            "family":family,"original_development_seed":seed,
            "training_weights_allowed":train,
            "original_native_uninterrupted_actions":event_count,
            "event_stream_sha256":event_hash.hexdigest(),
            "diagnostic_actual_source_key_pickups":source_pickup,
            "diagnostic_actual_source_door_unlocks":source_unlock,
            "diagnostic_public_MR15_pickups":source_public_pickup,
            "diagnostic_public_MR15_unlocks":source_public_unlock,
            "visible_complete_causal_experience":bool(
                source_public_pickup and source_public_unlock),
            "original_episode_ended_before_cap":original_source_ended,
            "source_prequential_brier":{
                name:sum(vals)/len(vals) for name,vals in losses.items()},
            "post_real_unlock_prequential":{
                name:(sum(vals)/len(vals) if vals else None)
                for name,vals in after_unlock_losses.items()},
            "public_temporal_sensor_checkpoint_bytes":len(sensor.snapshot().encode()),
        }
    finally:
        env.close()


def main(upstream):
    c=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if (c["schema"]!="yggdrasil.mr25.uninterrupted-original-native-learning.dev.v1" or
        c["base_yggdrasil_commit"]!="bfac577cd6b944be48f34e9a7a12216f9e1d4901" or
        c["original_farama_source_commit"]!=SOURCE_COMMIT or
        c["fixed_train_seeds"]!=[173,179,181] or
        c["fixed_development_evaluation_seed"]!=191 or
        c["per_environment_native_step_cap"]!=256):
        raise ValueError("MR25_FROZEN_NATIVE_EXPERIMENT_DRIFT")
    original=authentic_source(upstream)
    sys.path.insert(0,str(original))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factories=(
        ("DoorKeyEnv(size=8)",lambda:DoorKeyEnv(size=8,render_mode=None)),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None))
    )
    meter={
        "prediction_cpu_ns":0,"update_cpu_ns":0,
        "sampled_process_rss_max_bytes":psutil.Process().memory_info().rss
    }
    m=fresh_models()
    trained=[]
    start=time.process_time_ns()
    for family,factory in factories:
        for seed in c["fixed_train_seeds"]:
            trained.append(original_episode(
                factory,family,seed,256,m,train=True,meter=meter))
    frozen={name:model.snapshot() for name,model in m.items()}
    learned_snapshot=trainable_weights_snapshot(m)
    # Same-source exact canonical model cold restoration without changing
    # trained weights. Count table uses its frozen existing object.
    m["native"]=NativeLocalPredictiveState.restore(frozen["native"])
    m["recurrent"]=Recurrent45.restore(frozen["recurrent"])
    m["stateless"]=Native45.restore("public",frozen["stateless"])
    if any(m[name].snapshot()!=frozen[name]
           for name in ("native","recurrent","stateless")):
        raise ValueError("MR25_SOURCE_LEARNER_COLD_RESTART_FAILED")
    evaluated=[]
    for family,factory in factories:
        evaluated.append(original_episode(
            factory,family,c["fixed_development_evaluation_seed"],
            256,m,train=False,meter=meter))
    if trainable_weights_snapshot(m)!=learned_snapshot:
        raise ValueError("MR25_PUBLIC_DEVELOPMENT_EVAL_UPDATED_TRAINED_WEIGHTS")
    train_door=[x for x in trained if x["family"]=="DoorKeyEnv(size=8)"]
    eval_door=[x for x in evaluated if x["family"]=="DoorKeyEnv(size=8)"]
    train_exposure=sum(x["diagnostic_actual_source_door_unlocks"] for x in train_door)
    eval_exposure=sum(x["diagnostic_actual_source_door_unlocks"] for x in eval_door)
    comparison=eval_door[0]["source_prequential_brier"]
    accept={
        "training_history_contains_naturally_unlocked_door":train_exposure>0,
        "evaluation_history_contains_naturally_unlocked_door":eval_exposure>0,
        "native_state_improves_original_source_prediction_over_same_weights_ablated":
            comparison["native_retained"]<comparison["native_ablated"],
        "native_state_beats_equally_trained_recurrent_45_weight_and_8_state_control":
            comparison["native_retained"]<comparison["recurrent_control"],
    }
    native_weights=sum(map(len,m["native"].runtime.core.genome))+sum(
        map(len,m["native"].runtime.core.roles))
    recurrent_weights=sum(map(len,m["recurrent"].local))+len(m["recurrent"].shared)
    stateless_weights=sum(map(len,m["stateless"].rt.core.genome))+sum(
        map(len,m["stateless"].rt.core.roles))
    if (native_weights,recurrent_weights,stateless_weights)!=(45,45,45):
        raise ValueError("MR25_45_WEIGHT_CUSTODY_DRIFT")
    print("MR25_ORIGINAL_UNINTERRUPTED_SOURCE_LEARNING="+json.dumps({
        "original_independent_source_sha":SOURCE_COMMIT,
        "original_native_train_episodes":trained,
        "original_native_development_evaluation_episodes":evaluated,
        "frozen_necessary_acceptance_conditions":accept,
        "total_real_native_source_steps":sum(x["original_native_uninterrupted_actions"]
                                              for x in trained+evaluated),
        "trainable_coefficients_all_parametric_controls":[native_weights,recurrent_weights,stateless_weights],
        "extra_native_and_recurrent_ephemeral_states":8,
        "frozen_model_checkpoint_bytes":{key:len(value.encode()) for key,value in frozen.items()},
        "trained_count_control_table_bytes":len(frozen["counts"].encode()),
        "untrained_MR15_original_source_sensor_sidecar_bytes":32,
        "per_model_prediction_and_update_process_cpu_ns":meter,
        "complete_isolated_parent_child_cpu_and_peak_rss_parity":"NOT_QUALIFIED",
        "original_explorer_public_only_uninterrupted":True,
        "original_source_evaluator_privileges_not_used_in_action_selection_or_learning":True,
        "policy_source_independent_fixed_not_learned":True,
        "previously_consumed_original_development_sources":True,
        "new_protected_scientific_first_use":False,
        "upstream_original_source_license":"UNRESOLVED",
        "full_source_pinned_g29_and_system_regression":"BLOCKED",
        "scalable_local_causal_transfer_and_damage_recovery":"NOT_PROVEN",
        "scientific_admission":"NO_GO"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr25.natural_learning ORIGINAL_FARAMA_CHECKOUT")
    main(sys.argv[1])
