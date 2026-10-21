"""MR28: original-native prospective learned surprise-state versus controls.

Training cohorts were consumed as MR27 public DEVELOPMENT. This source freezes
NEW public DEVELOPMENT eval seeds before evaluation. Original Farama reset +
env.step is the sole source of action outcomes; evaluator source world/key/
door private truth is never passed to learner, explorer or training.

No extra latent state: eight scalar states only; compressor AND output share
original 45 coefficients. FROZEN encoder control, exact same-weights memory
ablation, conventional 45-coefficient recurrent, 45-coefficient native
stateless, and unmatched-memory count see the identical original source
observations, executed actions and next MR15 public bit consequences.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from research.mr15.public_view_delta import (
    SOURCE_COMMIT,PublicViewLocalDelta,public_raw_view
)
from research.mr26.public_novelty import BoundedPublicNoveltyExplorer
from research.mr28.predictive_surprise import PredictiveSurprise45
from research.mr19.native_local_predictive_state import NativeLocalPredictiveState
from research.mr18.native_public_learning import (
    Recurrent45,Native45,PublicCount
)

FROZEN=Path(__file__).with_name("frozen_protocol.json")
FAMILIES=("DoorKeyEnv(size=8)","EmptyEnv(size=8)")
KEYS=("predictive_surprise45","same_weights_state_zero",
      "fixed_surprise_encoder45","prior_mr19_native45",
      "conventional_recurrent45","stateless_public45",
      "public_count_unmatched_memory")
OTHER=("predictive_surprise45","fixed_surprise_encoder45",
       "prior_mr19_native45","conventional_recurrent45",
       "stateless_public45","public_count_unmatched_memory")


def verify(path):
    p=json.loads(FROZEN.read_text(encoding="utf-8"))
    if (p["schema"]!="yggdrasil.mr28.development-native-predictive-bottleneck.v1"
        or p["original_source_sha"]!=SOURCE_COMMIT
        or p["original_training_seeds_existing_consumed"]!=[
            263,269,271,277,281,283,293,307]
        or p["new_development_eval_seeds"]!=[337,347,349,353]
        or p["max_original_native_steps_per_episode"]!=256):
        raise ValueError("MR28_UNAUTHENTIC_FROZEN_NATIVE_PROTOCOL")
    root=Path(path).resolve()
    sha=subprocess.check_output(
        ["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    status=subprocess.check_output(
        ["git","-C",str(root),"status","--porcelain"],text=True).strip()
    if sha!=SOURCE_COMMIT or status:
        raise ValueError("MR28_FARAMA_ORIGINAL_SOURCE_DRIFT")
    return p,root


def make():
    return {
        "predictive_surprise45":PredictiveSurprise45(),
        "fixed_surprise_encoder45":PredictiveSurprise45(
            learn_encoder=False),
        "prior_mr19_native45":NativeLocalPredictiveState(),
        "conventional_recurrent45":Recurrent45(),
        "stateless_public45":Native45("public"),
        "public_count_unmatched_memory":PublicCount(),
    }


def restore(models):
    return {
        "predictive_surprise45":PredictiveSurprise45.restore(
            models["predictive_surprise45"].snapshot()),
        "fixed_surprise_encoder45":PredictiveSurprise45.restore(
            models["fixed_surprise_encoder45"].snapshot()),
        "prior_mr19_native45":NativeLocalPredictiveState.restore(
            models["prior_mr19_native45"].snapshot()),
        "conventional_recurrent45":Recurrent45.restore(
            models["conventional_recurrent45"].snapshot()),
        "stateless_public45":Native45.restore(
            "public",models["stateless_public45"].snapshot()),
        "public_count_unmatched_memory":copy.deepcopy(
            models["public_count_unmatched_memory"])
    }


def avg(values):
    if not values:
        raise ValueError("MR28_NO_AUTHENTIC_SOURCE_PREDICTIONS")
    return sum(values)/len(values)


def brier(probs,y):
    if len(probs)!=8 or len(y)!=8 or any(not 0<=v<=1 for v in probs):
        raise ValueError("MR28_INVALID_SOURCE_PUBLIC_PREDICTION")
    return sum((p-target)**2 for p,target in zip(probs,y))/8.


def episode(env,models,seed,phase,family,limit,receipts):
    actor=BoundedPublicNoveltyExplorer(seed)
    sensor=PublicViewLocalDelta()
    try:
        obs,_=env.reset(seed=seed)
        sensor.prime(obs["image"])
        for name in ("predictive_surprise45","fixed_surprise_encoder45",
                     "prior_mr19_native45","conventional_recurrent45"):
            models[name].reset_episode()
        losses={k:[] for k in KEYS}
        native_hash=hashlib.sha256()
        for step in range(limit):
            raw=public_raw_view(obs["image"])
            bits=tuple(sensor.bits)
            action=actor.choose(obs["image"])
            predictions={
                "predictive_surprise45":models["predictive_surprise45"].predict(
                    raw,bits,action),
                "same_weights_state_zero":models[
                    "predictive_surprise45"].predict(
                        raw,bits,action,drop_history=True),
                "fixed_surprise_encoder45":models[
                    "fixed_surprise_encoder45"].predict(raw,bits,action),
                "prior_mr19_native45":models[
                    "prior_mr19_native45"].predict(raw,bits,action),
                "conventional_recurrent45":models[
                    "conventional_recurrent45"].predict(raw,bits,action),
                "stateless_public45":models[
                    "stateless_public45"].predict(raw,bits,action),
                "public_count_unmatched_memory":models[
                    "public_count_unmatched_memory"].predict(
                        raw,bits,action)
            }
            before=obs["image"].tobytes()
            next_obs,_reward,finished,truncated,_info=env.step(action)
            event=sensor.observe_after_native_step(action,next_obs["image"])
            targets=event["observed_next_local_bits"]
            newraw=public_raw_view(next_obs["image"])
            if (event["source_commit"]!=SOURCE_COMMIT or
                event["observed_action"]!=action or
                event["prior_local_bits"]!=list(bits) or
                targets!=[int(raw[3*i:3*i+3]!=newraw[3*i:3*i+3])
                         for i in range(8)]):
                raise ValueError("MR28_ORIGINAL_SOURCE_NATIVE_EVENT_DRIFT")
            native_hash.update(bytes((action,*bits,*targets)))
            native_hash.update(hashlib.sha256(before).digest())
            native_hash.update(hashlib.sha256(
                next_obs["image"].tobytes()).digest())
            for name,prob in predictions.items():
                losses[name].append(brier(prob,targets))
            train=(phase=="train")
            for name in ("predictive_surprise45","fixed_surprise_encoder45"):
                returned=models[name].observe(raw,bits,action,targets,train)
                if returned!=predictions[name]:
                    raise ValueError("MR28_POST_NATIVE_TARGET_LEAK_IN_PREDICTION")
            models["prior_mr19_native45"].observe(
                raw,bits,action,targets,train=train)
            if train:
                for name in ("conventional_recurrent45",
                             "stateless_public45","public_count_unmatched_memory"):
                    models[name].observe(raw,bits,action,targets)
            else:
                models["conventional_recurrent45"].advance_public_history(raw)
            actor.observe_original_next_public_image(
                action,next_obs["image"])
            actor.validate()
            if step==11:
                s=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(s)
                if sensor.snapshot()!=s:
                    raise ValueError("MR28_NATIVE_SENSOR_RESTART_FAILED")
                snap={k:v.snapshot() for k,v in models.items()}
                models=restore(models)
                if any(models[k].snapshot()!=snap[k] for k in OTHER):
                    raise ValueError("MR28_NATIVE_LEARNED_STATE_RESTART_FAILED")
                receipts["cold_restart_checks"]+=1
            obs=next_obs
            if finished or truncated:
                break
        n=len(losses["predictive_surprise45"])
        if not n:
            raise ValueError("MR28_NO_UNINTERRUPTED_SOURCE_ACTIONS")
        receipts["episodes"].append({
            "original_environment":family,"seed":seed,"phase":phase,
            "native_source_steps":n,
            "source_public_history_sha256":native_hash.hexdigest(),
            "preaction_brier":{key:avg(losses[key]) for key in KEYS},
            "untrained_explorer_additional_diagnostic_bytes":
                actor.extra_untrained_policy_bytes(),
            "explorer_durable_rng_state":"NOT_QUALIFIED",
            "same_source_world_reward_labels_to_predictor":False
        })
        return models
    finally:
        env.close()


def main(original):
    c,src=verify(original)
    sys.path.insert(0,str(src))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factories=(
        lambda:DoorKeyEnv(size=8,render_mode=None),
        lambda:EmptyEnv(size=8,render_mode=None)
    )
    models=make()
    receipts={"episodes":[],"cold_restart_checks":0}
    process_start=time.process_time_ns()
    for factory,family in zip(factories,FAMILIES):
        for seed in c["original_training_seeds_existing_consumed"]:
            models=episode(factory(),models,seed,"train",
                           family,c["max_original_native_steps_per_episode"],
                           receipts)
    snapshots={k:v.snapshot() for k,v in models.items()}
    models=restore(models)
    if any(models[k].snapshot()!=snapshots[k] for k in OTHER):
        raise ValueError("MR28_FROZEN_TRAINED_NATIVE_STATE_MISMATCH")
    frozen={
        "predictive":models["predictive_surprise45"].runtime.snapshot(),
        "fixed":models["fixed_surprise_encoder45"].runtime.snapshot(),
        "mr19":models["prior_mr19_native45"].runtime.snapshot(),
        "recurrent":copy.deepcopy((
            models["conventional_recurrent45"].local,
            models["conventional_recurrent45"].shared)),
        "stateless":models["stateless_public45"].snapshot(),
        "count":models["public_count_unmatched_memory"].snapshot(),
    }
    for factory,family in zip(factories,FAMILIES):
        for seed in c["new_development_eval_seeds"]:
            models=episode(factory(),models,seed,"dev_eval",family,
                           c["max_original_native_steps_per_episode"],
                           receipts)
    if (models["predictive_surprise45"].runtime.snapshot()!=frozen["predictive"]
        or models["fixed_surprise_encoder45"].runtime.snapshot()!=frozen["fixed"]
        or models["prior_mr19_native45"].runtime.snapshot()!=frozen["mr19"]
        or (models["conventional_recurrent45"].local,
            models["conventional_recurrent45"].shared)!=frozen["recurrent"]
        or models["stateless_public45"].snapshot()!=frozen["stateless"]
        or models["public_count_unmatched_memory"].snapshot()!=frozen["count"]):
        raise ValueError("MR28_SOURCE_DEV_EVALUATION_TRAINING_LEAK")
    scores={}
    for family in FAMILIES:
        rows=[r for r in receipts["episodes"] if
              r["phase"]=="dev_eval" and r["original_environment"]==family]
        steps=sum(r["native_source_steps"] for r in rows)
        scores[family]={
            name:sum(r["preaction_brier"][name]*r["native_source_steps"]
                     for r in rows)/steps
            for name in KEYS
        }
    conditions={
        "learned_state_better_than_exact_same_weights_state_zero_both":all(
            z["predictive_surprise45"]<z["same_weights_state_zero"]
            for z in scores.values()),
        "learned_encoder_better_than_unlearned_fixed_encoder_both":all(
            z["predictive_surprise45"]<z["fixed_surprise_encoder45"]
            for z in scores.values()),
        "learned_state_better_than_trained_45_recurrent_both":all(
            z["predictive_surprise45"]<z["conventional_recurrent45"]
            for z in scores.values()),
        "learned_state_better_than_45_stateless_both":all(
            z["predictive_surprise45"]<z["stateless_public45"]
            for z in scores.values())
    }
    print("MR28_ORIGINAL_NATIVE_SURPRISE_COMPRESSION="+json.dumps({
        "original_source_commit":SOURCE_COMMIT,
        "frozen_protocol_sha256":hashlib.sha256(
            FROZEN.read_bytes()).hexdigest(),
        "original_source_native_episodes":receipts["episodes"],
        "original_native_development_scores_brier_lower_better":scores,
        "necessary_development_conditions":conditions,
        "existing_original_45_trainable_coefficients_per_parametric_model":45,
        "candidate_eight_bounded_camera_relative_history_states":8,
        "recurrent_eight_bounded_ephemeral_states":8,
        "additional_persistent_predictive_learner_state_values":0,
        "original_nonlearned_MR15_sensor_sidecar_bytes":32,
        "trained_original_model_checkpoint_serialized_bytes":{
            name:len(value.encode()) for name,value in snapshots.items()},
        "native_original_source_cold_restart_checks":
            receipts["cold_restart_checks"],
        "single_shared_process_CPU_time_ns_diagnostic":
            time.process_time_ns()-process_start,
        "entire_source_engine_and_explorer_parent_child_CPU_peak_RSS_wire":
            "NOT_QUALIFIED",
        "fully_camera_corrected_memoryless_control":"NOT_QUALIFIED",
        "informed_public_count_total_state_memory_match":False,
        "natural_identical_entire_current_input_different_outcome_pair_in_eval":
            "NOT_QUALIFIED",
        "model_encoder_update_is_one_step_proxy_not_exact_through_time":True,
        "source_evaluator_world_pose_reward_object_labels_to_model":False,
        "original_external_source_first_use":False,
        "original_g29_atlas":"BLOCKED",
        "external_source_license_metadata_conflict":"UNRESOLVED",
        "scientific_admission":"NO_GO"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr28.probe_native_surprise ORIGINAL")
    main(sys.argv[1])
