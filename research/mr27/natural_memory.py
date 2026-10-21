"""MR27: natural original public-history learning after qualified MR26 acquisition.

No evaluator-controlled positions, object-role labels, source world state,
inventory, reward, mission, future targets, or seed/arm information reach
the action policy or any predictive model. All predictions PRECEDE original
MiniGrid env.step; real public next-image differences arrive afterward.

Eight already consumed MR26 development seeds TRAIN the unchanged 45-weight
native model and fully trained equally informed conventional controls.
Separate prospectively frozen new development seeds evaluate FROZEN weights.
This is not protected scientific first-use or causal-cognition admission.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import psutil

from research.mr15.public_view_delta import (
    PublicViewLocalDelta, SOURCE_COMMIT, public_raw_view
)
from research.mr18.native_public_learning import Native45,Recurrent45,PublicCount
from research.mr19.native_local_predictive_state import NativeLocalPredictiveState
from research.mr24.natural_history import source_evaluator_private_door
from research.mr26.public_novelty import BoundedPublicNoveltyExplorer

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/"research"/"mr27"/"frozen_protocol.json"
NAMES=("native","native_same_weights_ablated","recurrent","stateless",
       "public_count","constant_zero","constant_half")


def source_guard(root):
    path=Path(root).resolve()
    commit=subprocess.check_output(
        ["git","-C",str(path),"rev-parse","HEAD"],text=True).strip()
    modified=subprocess.check_output(
        ["git","-C",str(path),"status","--porcelain"],text=True).strip()
    if commit!=SOURCE_COMMIT or modified:
        raise ValueError("MR27_FARAMA_ORIGINAL_SOURCE_DRIFT")
    return path


def models_new():
    return {
        "native":NativeLocalPredictiveState(),
        "recurrent":Recurrent45(),
        "stateless":Native45("public"),
        "public_count":PublicCount()
    }


def trainable_weight_identity(models):
    native=json.loads(models["native"].snapshot())
    recurrent=json.loads(models["recurrent"].snapshot())
    return {
        "native_original_45_coefficients":native["native_runtime"]["core"],
        "conventional_recurrent_45_coefficients":{
            "local":recurrent["local"],"shared":recurrent["shared"]
        },
        "conventional_stateless_45_coefficients":
            models["stateless"].snapshot(),
        "larger_memory_count_table":models["public_count"].snapshot()
    }


def brier(probs,target):
    if len(probs)!=8 or len(target)!=8:
        raise ValueError("MR27_NATIVE_PREDICTION_WIDTH_DRIFT")
    if any(not 0.<=p<=1. for p in probs):
        raise ValueError("MR27_NONPROBABILITY_PREDICTION")
    return sum((p-y)*(p-y) for p,y in zip(probs,target))/8.


def causal_episode(factory,family,seed,limit,models,*,training):
    from minigrid.core.world_object import Key
    native=factory()
    explorer=BoundedPublicNoveltyExplorer(seed)
    sensor=PublicViewLocalDelta()
    native_process=psutil.Process()
    process_peak_rss=native_process.memory_info().rss
    pred_cpu={name:0 for name in ("native","recurrent","stateless","public_count")}
    upd_cpu={name:0 for name in ("native","recurrent","stateless","public_count")}
    source_clock_cpu=0
    event_hash=hashlib.sha256()
    observations={name:[] for name in NAMES}
    post_unlock={name:[] for name in NAMES}
    visible_pickups=[]
    visible_unlocks=[]
    all_pickups=[]
    all_unlocks=[]
    steps=0
    try:
        current,_=native.reset(seed=seed)
        sensor.prime(current["image"])
        models["native"].reset_episode()
        models["recurrent"].reset_episode()
        door=(source_evaluator_private_door(native)
              if family=="DoorKeyEnv(size=8)" else None)
        prev_key=False
        prev_door_open=False
        for tick in range(limit):
            if sensor.steps!=tick:
                raise ValueError("MR27_UNINTERRUPTED_NATIVE_STEP_DISCONTINUITY")
            image=current["image"]
            oldraw=public_raw_view(image)
            oldbits=tuple(sensor.bits)
            # MR26 action chooser receives the complete ORIGINAL PUBLIC
            # image ONLY, not any hidden source or target evaluator info.
            action=explorer.choose(image)
            before={}
            fn=[
                ("native",lambda:models["native"].predict(oldraw,oldbits,action)),
                ("recurrent",lambda:models["recurrent"].predict(oldraw,oldbits,action)),
                ("stateless",lambda:models["stateless"].predict(oldraw,oldbits,action)),
                ("public_count",lambda:models["public_count"].predict(oldraw,oldbits,action))
            ]
            for name,compute in fn:
                start=time.process_time_ns()
                before[name]=compute()
                pred_cpu[name]+=time.process_time_ns()-start
            # Correct same-weights state-ablation: no separate trained head.
            start=time.process_time_ns()
            before["native_same_weights_ablated"]=models["native"].predict(
                oldraw,oldbits,action,drop_temporal_state=True)
            pred_cpu["native"]+=time.process_time_ns()-start
            before["constant_zero"]=[0.]*8
            before["constant_half"]=[.5]*8

            source_start=time.process_time_ns()
            new,_ignored_reward,finished,truncated,_info=native.step(action)
            source_clock_cpu+=time.process_time_ns()-source_start
            change=sensor.observe_after_native_step(action,new["image"])
            out=tuple(change["observed_next_local_bits"])
            newerraw=public_raw_view(new["image"])
            expected=tuple(int(oldraw[i*3:i*3+3]!=newerraw[i*3:i*3+3])
                           for i in range(8))
            if (tuple(change["prior_local_bits"])!=oldbits or
                change["observed_action"]!=action or
                change["source_commit"]!=SOURCE_COMMIT or
                out!=expected or change["privileged_world_fields_consumed"]!=0):
                raise ValueError("MR27_ORIGINAL_NATIVE_SOURCE_PUBLIC_DRIFT")
            explorer.observe_original_next_public_image(action,new["image"])
            explorer.validate()
            event_hash.update(bytes((action,*oldbits,*out)))
            event_hash.update(hashlib.sha256(image.tobytes()).digest())
            event_hash.update(hashlib.sha256(new["image"].tobytes()).digest())
            for name,predict in before.items():
                loss=brier(predict,out)
                observations[name].append(loss)
                if prev_door_open:
                    post_unlock[name].append(loss)

            for name,compute in (
                ("native",lambda:models["native"].observe(
                    oldraw,oldbits,action,list(out),train=training)),
                ("recurrent",lambda:(
                    models["recurrent"].observe(oldraw,oldbits,action,list(out))
                    if training else
                    models["recurrent"].advance_public_history(oldraw))),
                ("stateless",lambda:models["stateless"].observe(
                    oldraw,oldbits,action,list(out)) if training else None),
                ("public_count",lambda:models["public_count"].observe(
                    oldraw,oldbits,action,list(out)) if training else None)
            ):
                start=time.process_time_ns()
                compute()
                upd_cpu[name]+=time.process_time_ns()-start

            # These are EVALUATOR-ONLY genuine native source checks AFTER
            # all action choices, predictions and training updates.
            key_now=isinstance(native.carrying,Key)
            open_now=bool(door.is_open) if door is not None else False
            if key_now and not prev_key:
                all_pickups.append(tick)
                if sum(out):
                    visible_pickups.append(tick)
            if open_now and not prev_door_open:
                all_unlocks.append(tick)
                if sum(out):
                    visible_unlocks.append(tick)
            prev_key=key_now
            prev_door_open=open_now
            steps+=1
            current=new
            process_peak_rss=max(process_peak_rss,native_process.memory_info().rss)
            if tick==11:
                snap=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(snap)
                if sensor.snapshot()!=snap:
                    raise ValueError("MR27_SENSOR_CANONICAL_RESTART_FAILED")
            if finished or truncated:
                break
        if steps<=0 or steps>limit:
            raise ValueError("MR27_UNQUALIFIED_NATIVE_EPISODE_LENGTH")
        qualified=any(b>a for a in visible_pickups for b in visible_unlocks)
        return {
            "original_environment":family,
            "original_source_seed":seed,
            "phase":"training" if training else "prospective_development_evaluation",
            "original_native_steps":steps,
            "original_source_event_sha256":event_hash.hexdigest(),
            "genuine_pickup_steps_diagnostic_only":all_pickups,
            "genuine_door_unlock_steps_diagnostic_only":all_unlocks,
            "visible_pickup_steps":visible_pickups,
            "visible_unlock_steps":visible_unlocks,
            "natural_complete_visible_causal_experience":qualified,
            "source_prequential_brier":{
                name:sum(vals)/len(vals) for name,vals in observations.items()},
            "post_true_door_unlock_brier":{
                name:(sum(vals)/len(vals) if vals else None)
                for name,vals in post_unlock.items()},
            "original_sensor_sidecar_untrained_bytes":32,
            "explorer_serialized_diagnostic_bytes":
                explorer.extra_untrained_policy_bytes(),
            "policy_rng_restart_state":"NOT_QUALIFIED",
            "explorer_untrained_fifo_size":len(explorer.visited),
            "per_model_prediction_cpu_ns_in_shared_process":pred_cpu,
            "per_model_update_cpu_ns_in_shared_process":upd_cpu,
            "original_native_source_step_cpu_ns_in_shared_process":source_clock_cpu,
            "sampled_same_process_peak_rss_bytes":process_peak_rss,
        }
    finally:
        native.close()


def main(upstream):
    p=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (p["schema"]!="yggdrasil.mr27.source-native-public-history-training.dev.v1" or
        p["predecessor_yggdrasil_sha"]!="8817f21047d0a97770ea686c76620e082595c2ad" or
        p["farama_original_commit"]!=SOURCE_COMMIT or
        p["consumed_MR26_development_training_seeds"]!=[263,269,271,277,281,283,293,307] or
        p["fresh_nonprotected_development_evaluation_seeds"]!=[311,313,317,331] or
        p["fixed_original_native_step_limit_each_episode"]!=256 or
        p["scientific_first_use"] is not False):
        raise ValueError("MR27_FROZEN_EXPERIMENT_PROTOCOL_DRIFT")
    src=source_guard(upstream)
    sys.path.insert(0,str(src))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv

    families=(
        ("DoorKeyEnv(size=8)",lambda:DoorKeyEnv(size=8,render_mode=None)),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None))
    )
    learner=models_new()
    overall_start=time.process_time_ns()
    training=[]
    for family,factory in families:
        for seed in p["consumed_MR26_development_training_seeds"]:
            training.append(causal_episode(
                factory,family,seed,256,learner,training=True))
    frozen_models={name:m.snapshot() for name,m in learner.items()}
    weight_identity=trainable_weight_identity(learner)
    learner["native"]=NativeLocalPredictiveState.restore(frozen_models["native"])
    learner["recurrent"]=Recurrent45.restore(frozen_models["recurrent"])
    learner["stateless"]=Native45.restore("public",frozen_models["stateless"])
    if any(learner[name].snapshot()!=frozen_models[name]
           for name in ("native","recurrent","stateless")):
        raise ValueError("MR27_TRAINED_MODEL_COLD_RESTART_DRIFT")

    evaluation=[]
    for family,factory in families:
        for seed in p["fresh_nonprotected_development_evaluation_seeds"]:
            evaluation.append(causal_episode(
                factory,family,seed,256,learner,training=False))
    if trainable_weight_identity(learner)!=weight_identity:
        raise ValueError("MR27_DEVELOPMENT_EVAL_CHANGED_FROZEN_PARAMETERS")

    def aggregate(rows):
        result={}
        for family,_ in families:
            subset=[r for r in rows if r["original_environment"]==family]
            count=sum(r["original_native_steps"] for r in subset)
            result[family]={
                "genuine_original_steps":count,
                "authentic_visible_causal_exposure_episodes":sum(
                    r["natural_complete_visible_causal_experience"] for r in subset),
                "source_Brier":{
                    name:sum(r["source_prequential_brier"][name]*
                             r["original_native_steps"] for r in subset)/count
                    for name in NAMES}
            }
        return result
    train_aggregate=aggregate(training)
    eval_aggregate=aggregate(evaluation)
    train_exposure=train_aggregate["DoorKeyEnv(size=8)"][
        "authentic_visible_causal_exposure_episodes"]
    eval_exposure=eval_aggregate["DoorKeyEnv(size=8)"][
        "authentic_visible_causal_exposure_episodes"]
    scores=eval_aggregate["DoorKeyEnv(size=8)"]["source_Brier"]
    source_loses={}
    for family in eval_aggregate:
        r=eval_aggregate[family]["source_Brier"]
        source_loses[family]={
            "native_state_improves_over_same_weights_ablated":
                r["native"]<r["native_same_weights_ablated"],
            "native_state_outperforms_fully_trained_recurrent":
                r["native"]<r["recurrent"],
            "native_prediction_better_than_constant_zero":
                r["native"]<r["constant_zero"],
            "native_prediction_better_than_constant_half":
                r["native"]<r["constant_half"]
        }

    count_weights={
        "native":sum(map(len,learner["native"].runtime.core.genome))+
                 sum(map(len,learner["native"].runtime.core.roles)),
        "conventional_recurrent":sum(
            map(len,learner["recurrent"].local))+len(learner["recurrent"].shared),
        "conventional_stateless":sum(
            map(len,learner["stateless"].rt.core.genome))+
            sum(map(len,learner["stateless"].rt.core.roles))
    }
    if any(v!=45 for v in count_weights.values()):
        raise ValueError("MR27_ORIGINAL_FIXED_MODEL_BUDGET_DRIFT")

    print("MR27_ORIGINAL_NATURAL_CAUSAL_MEMORY="+json.dumps({
        "original_farama_git_commit":SOURCE_COMMIT,
        "frozen_original_training_seed_set":p["consumed_MR26_development_training_seeds"],
        "frozen_new_development_eval_seed_set":p["fresh_nonprotected_development_evaluation_seeds"],
        "genuine_original_native_training_episodes":training,
        "genuine_original_native_development_evaluation_episodes":evaluation,
        "per_source_class_training_summary":train_aggregate,
        "per_source_class_frozen_weight_eval_summary":eval_aggregate,
        "actual_natural_train_door_unlock_histories":train_exposure,
        "actual_natural_dev_eval_door_unlock_histories":eval_exposure,
        "necessary_condition_results":{
            "genuine_visible_intervention_in_training":train_exposure>0,
            "genuine_visible_intervention_in_evaluation":eval_exposure>0,
            "prospective_development_source_controls":source_loses,
            "recurrent_and_native_have_eight_bounded_episode_values":True,
        },
        "all_trainable_coefficient_counts":count_weights,
        "candidate_and_control_eight_episodic_state_values":8,
        "checkpoint_bytes_all_model_families":{
            name:len(value.encode()) for name,value in frozen_models.items()},
        "separate_untrained_original_MR15_sensor_sidecar_bytes":32,
        "candidate_and_control_share_same_original_full_public_image_policy":True,
        "policy_memory_in_separate_per_episode_untrained_fifo":True,
        "complete_matched_total_memory":"NOT_QUALIFIED",
        "full_parent_child_isolated_cpu_peak_rss":"NOT_QUALIFIED",
        "same_source_shared_process_cpu_ns":time.process_time_ns()-overall_start,
        "source_policy_continuous_original_public_only_no_evaluator_staging":True,
        "no_original_world_grid_coords_reward_mission_or_role_labels_in_models":True,
        "protected_scientific_first_use":False,
        "original_upstream_license_conflict":"UNRESOLVED",
        "G29_original_source_atlas_full_integration":"BLOCKED",
        "learned_world_causal_specific_function_or_transfer":"NOT_PROVEN",
        "scientific_admission":"NO_GO"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr27.natural_memory ORIGINAL_FARAMA_SOURCE")
    main(sys.argv[1])
