"""MR24B: original uninterrupted native prequential learned-memory development.

All original source trajectories are native ORIGINAL reset/step, using the
MR24A unaltered public-only independent actor. Training trajectories are
cryptographically compared to MR24A's previously verified eight event digests.
Fresh development evaluation seeds were committed BEFORE this file.

Candidate and all equal-information controls predict BEFORE source action,
and see only MR15 sampled public bytes, previous delta bits, native action and
AFTER-action observed public deltas. Source evaluator-only door/key events
are segregated: used for aggregate CONDITIONAL SCORING, NEVER model training,
source navigation, architecture tuning, or model input.

Known limitations: these are the SAME Farama task classes; no independent
scientific first use, no natural matched hidden-state twin contrast, and
no all-in CPU/RSS or fully geometry-normalized/source-aware stateless control.
"""
import copy
from hashlib import sha256
import json
from pathlib import Path
import random
import subprocess
import sys
import time

from research.mr15.public_view_delta import (
    SOURCE_COMMIT,PublicViewLocalDelta,public_raw_view
)
from research.mr24.natural_history import (
    public_only_action,source_evaluator_private_door
)
from research.mr19.native_local_predictive_state import NativeLocalPredictiveState
from research.mr18.native_public_learning import Native45,Recurrent45,PublicCount

CONTRACT=Path(__file__).with_name("frozen_protocol.json")
SCHEMA="yggdrasil.mr24b.source-native-natural-prequential.dev.v1"
NAMES=("ygg_local45","ygg_same_weights_zero_history",
       "native45_memoryless","conventional_recurrent45",
       "public_action_count_unmatched_state")


def verify_source(path):
    p=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (p["schema"]!=SCHEMA or p["original_farama_sha"]!=SOURCE_COMMIT
        or p["train_seeds_from_completed_mr24a"]!=[173,179,181,191]
        or p["dev_eval_seeds_frozen_before_execution"]!=[193,197,199,211]
        or p["native_max_steps_per_episode"]!=256
        or set(p["training_replay_receipts_from_mr24a"])!={
            f"{source}/{seed}" for source in p["original_source_classes"]
            for seed in p["train_seeds_from_completed_mr24a"]}):
        raise ValueError("MR24B_FROZEN_PROTOCOL_DRIFT")
    root=Path(path).resolve()
    sha=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                                text=True).strip()
    dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],
                                  text=True).strip()
    if sha!=SOURCE_COMMIT or dirty:
        raise ValueError("MR24B_ORIGINAL_NATIVE_SOURCE_INVALID")
    return p,root


def make_models():
    return {
        "ygg_local45":NativeLocalPredictiveState(),
        "native45_memoryless":Native45("public"),
        "conventional_recurrent45":Recurrent45(),
        "public_action_count_unmatched_state":PublicCount()
    }


def restart(models):
    return {
        "ygg_local45":NativeLocalPredictiveState.restore(
            models["ygg_local45"].snapshot()),
        "native45_memoryless":Native45.restore(
            "public",models["native45_memoryless"].snapshot()),
        "conventional_recurrent45":Recurrent45.restore(
            models["conventional_recurrent45"].snapshot()),
        "public_action_count_unmatched_state":copy.deepcopy(
            models["public_action_count_unmatched_state"])
    }


def brier(probs,targets):
    if (type(probs) not in (tuple,list) or len(probs)!=8 or
        type(targets) not in (tuple,list) or len(targets)!=8 or
        any(type(p) not in (int,float) or not 0<=p<=1 for p in probs) or
        any(type(y) is not int or y not in (0,1) for y in targets)):
        raise ValueError("MR24B_NON_NATIVE_PROBABILITY_OR_TARGET")
    return sum((p-y)**2 for p,y in zip(probs,targets))/8


def episode(env,models,source,seed,budget,training,metrics):
    from minigrid.core.world_object import Key
    actor_rng=random.Random(1000003*seed+337)
    try:
        public,_=env.reset(seed=seed)
        sensor=PublicViewLocalDelta()
        sensor.prime(public["image"])
        models["ygg_local45"].reset_episode()
        models["conventional_recurrent45"].reset_episode()
        # Isolated diagnostic reference, never supplied to any predictor.
        original_door=(
            source_evaluator_private_door(env)
            if source=="DoorKeyEnv(size=8)" else None
        )
        before_carry=False
        already_unlocked=False
        did_pickup=False
        did_unlock=False
        rows=[]
        raw_trace=[]
        phase="training" if training else "dev_evaluation"
        for i in range(budget):
            before_raw=public_raw_view(public["image"])
            before_bits=tuple(sensor.bits)
            action=public_only_action(public,actor_rng)
            # CRITICAL: all predictions precede original source env.step.
            pred={}
            now=time.process_time_ns()
            pred["ygg_local45"]=models["ygg_local45"].predict(
                before_raw,before_bits,action)
            pred["ygg_same_weights_zero_history"]=models[
                "ygg_local45"].predict(
                    before_raw,before_bits,action,drop_temporal_state=True)
            metrics["candidate_model_only_cpu_ns"]+=time.process_time_ns()-now
            pred["native45_memoryless"]=models[
                "native45_memoryless"].predict(before_raw,before_bits,action)
            pred["conventional_recurrent45"]=models[
                "conventional_recurrent45"].predict(before_raw,before_bits,action)
            pred["public_action_count_unmatched_state"]=models[
                "public_action_count_unmatched_state"].predict(
                    before_raw,before_bits,action)
            frozen_before=sensor.snapshot()
            before_image_sha=sha256(public["image"].tobytes()).hexdigest()
            before_door_open=(bool(original_door.is_open)
                              if original_door is not None else False)
            next_obs,_reward,terminated,truncated,_info=env.step(action)
            evt=sensor.observe_after_native_step(action,next_obs["image"])
            after_raw=public_raw_view(next_obs["image"])
            target=evt["observed_next_local_bits"]
            if (evt["source_commit"]!=SOURCE_COMMIT or
                evt["observed_action"]!=action or
                evt["prior_local_bits"]!=list(before_bits) or
                evt["observed_next_local_bits"]!=[
                   int(tuple(before_raw[3*j:3*j+3])!=
                       tuple(after_raw[3*j:3*j+3])) for j in range(8)] or
                sensor.steps!=i+1 or sensor.snapshot()==frozen_before):
                raise ValueError("MR24B_NATIVE_PUBLIC_CAUSAL_EVENT_DRIFT")
            raw_trace.append([
                i,action,list(target),before_image_sha,
                sha256(next_obs["image"].tobytes()).hexdigest()
            ])
            # Segregated source evaluator branch; diagnostics only.
            carrying_key=isinstance(env.carrying,Key)
            did_pickup_now=bool(carrying_key and not before_carry)
            did_unlock_now=bool(
                original_door is not None and original_door.is_open
                and not before_door_open)
            event_class=("unlock_event" if did_unlock_now
                         else ("pickup_event" if did_pickup_now
                         else ("after_unlock" if already_unlocked
                         else ("after_pickup" if did_pickup else "before_pickup"))))
            row={
                "stratum":event_class,
                "loss":{name:brier(pred[name],target) for name in NAMES},
                "natural_native_source_event_index":i
            }
            rows.append(row)
            # Model weights update exclusively from source-public next
            # image deltas, never from evaluator stratum or hidden door data.
            now=time.process_time_ns()
            prior_candidate=pred["ygg_local45"]
            source_prequential=models["ygg_local45"].observe(
                before_raw,before_bits,action,target,train=training)
            if source_prequential!=prior_candidate:
                raise ValueError("MR24B_POST_ACTION_PREDICTION_TAMPER")
            metrics["candidate_model_only_cpu_ns"]+=time.process_time_ns()-now
            if training:
                models["native45_memoryless"].observe(
                    before_raw,before_bits,action,target)
                models["conventional_recurrent45"].observe(
                    before_raw,before_bits,action,target)
                models["public_action_count_unmatched_state"].observe(
                    before_raw,before_bits,action,target)
            else:
                models["conventional_recurrent45"].advance_public_history(
                    before_raw)
            if i==11:
                snap=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(snap)
                if sensor.snapshot()!=snap:
                    raise ValueError("MR24B_SENSOR_COLD_RESTORE_DRIFT")
                model_snap={name:m.snapshot() for name,m in models.items()}
                models=restart(models)
                if any(models[name].snapshot()!=model_snap[name] for name in models):
                    raise ValueError("MR24B_MODEL_CANONICAL_RESTART_DRIFT")
                metrics["native_restart_receipts"]+=1
            before_carry=carrying_key
            already_unlocked=already_unlocked or did_unlock_now
            did_pickup=did_pickup or did_pickup_now
            did_unlock=did_unlock or did_unlock_now
            public=next_obs
            if terminated or truncated:
                break
        if not rows:
            raise ValueError("MR24B_ZERO_ORIGINAL_NATIVE_EVENTS")
        digest=sha256(json.dumps(raw_trace,separators=(",",":")).encode()).hexdigest()
        return models,{
            "family":source,"seed":seed,"phase":phase,
            "true_original_native_action_steps":len(rows),
            "uninterrupted_key_pickup_occurred":did_pickup,
            "uninterrupted_door_unlock_occurred":did_unlock,
            "event_count_by_evaluator_stratum":{
                k:sum(r["stratum"]==k for r in rows)
                for k in ("before_pickup","pickup_event","after_pickup",
                          "unlock_event","after_unlock")
            },
            "mean_preaction_brier_all":{
                name:sum(r["loss"][name] for r in rows)/len(rows)
                for name in NAMES
            },
            "mean_preaction_brier_by_source_stratum":{
                k:{
                    name:sum(r["loss"][name] for r in rows
                             if r["stratum"]==k)/
                         sum(r["stratum"]==k for r in rows)
                    for name in NAMES
                }
                for k in ("before_pickup","pickup_event","after_pickup",
                          "unlock_event","after_unlock")
                if any(r["stratum"]==k for r in rows)
            },
            "native_original_public_event_sha256":digest,
            "no_evaluator_staging_or_internal_policy_control":True,
        }
    finally:
        env.close()


def main(root):
    cfg,original=verify_source(root)
    sys.path.insert(0,str(original))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    creators=[
        ("DoorKeyEnv(size=8)",lambda:DoorKeyEnv(size=8,render_mode=None)),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None))
    ]
    models=make_models()
    report={"candidate_model_only_cpu_ns":0,"native_restart_receipts":0}
    receipts=[]
    for family,factory in creators:
        for seed in cfg["train_seeds_from_completed_mr24a"]:
            models,rec=episode(
                factory(),models,family,seed,
                cfg["native_max_steps_per_episode"],True,report)
            original_receipt=cfg["training_replay_receipts_from_mr24a"][
                f"{family}/{seed}"]
            if rec["native_original_public_event_sha256"]!=original_receipt:
                raise ValueError("MR24B_AUTHENTIC_MR24A_TRAINING_REPLAY_MISMATCH")
            receipts.append(rec)
    saved={name:model.snapshot() for name,model in models.items()}
    models=restart(models)
    if any(models[name].snapshot()!=saved[name] for name in models):
        raise ValueError("MR24B_FINAL_TRAINED_COLD_STATE_DRIFT")
    frozen={
        "candidate_native_weights":models["ygg_local45"].runtime.snapshot(),
        "memoryless_weights":models["native45_memoryless"].snapshot(),
        "recurrent_coefficients":copy.deepcopy(
            (models["conventional_recurrent45"].local,
             models["conventional_recurrent45"].shared)),
        "count_original_table":models[
            "public_action_count_unmatched_state"].snapshot()
    }
    for family,factory in creators:
        for seed in cfg["dev_eval_seeds_frozen_before_execution"]:
            models,rec=episode(
                factory(),models,family,seed,
                cfg["native_max_steps_per_episode"],False,report)
            receipts.append(rec)
    if (models["ygg_local45"].runtime.snapshot()!=
          frozen["candidate_native_weights"] or
        models["native45_memoryless"].snapshot()!=
          frozen["memoryless_weights"] or
        (models["conventional_recurrent45"].local,
         models["conventional_recurrent45"].shared)!=
          frozen["recurrent_coefficients"] or
        models["public_action_count_unmatched_state"].snapshot()!=
          frozen["count_original_table"]):
        raise ValueError("MR24B_DEV_EVAL_TRAINABLE_WEIGHTS_LEAK")
    evaluation=[r for r in receipts if r["phase"]=="dev_evaluation"]
    by_source={}
    for family,_ in creators:
        by_source[family]={
            name:sum(r["mean_preaction_brier_all"][name]*
                     r["true_original_native_action_steps"]
                     for r in evaluation if r["family"]==family)/
                 sum(r["true_original_native_action_steps"]
                     for r in evaluation if r["family"]==family)
            for name in NAMES
        }
    tests={
        "history_benefit_over_same_weights_ablation_both_sources":all(
            scores["ygg_local45"]<
            scores["ygg_same_weights_zero_history"]
            for scores in by_source.values()),
        "history_outperforms_trained_recurrent_both_sources":all(
            scores["ygg_local45"]<
            scores["conventional_recurrent45"]
            for scores in by_source.values()),
        "history_outperforms_action_conditioned_memoryless_both_sources":all(
            scores["ygg_local45"]<
            scores["native45_memoryless"]
            for scores in by_source.values()),
        "natural_eval_door_unlock_witness_exists":any(
            r["uninterrupted_door_unlock_occurred"]
            for r in evaluation if r["family"]=="DoorKeyEnv(size=8)")
    }
    print("MR24B_UNINTERRUPTED_NATIVE_LEARNED_HISTORY="+json.dumps({
        "source_commit":SOURCE_COMMIT,
        "frozen_protocol_sha256":sha256(CONTRACT.read_bytes()).hexdigest(),
        "source_original_training_digest_identity_all_passed":True,
        "trained_on_prior_mr24a_original_episodes":len(receipts)-len(evaluation),
        "new_dev_eval_original_episodes":len(evaluation),
        "new_dev_eval_original_steps":sum(
            r["true_original_native_action_steps"] for r in evaluation),
        "new_dev_eval_mean_brier":by_source,
        "decisive_development_conditions":tests,
        "episode_original_source_receipts":receipts,
        "original_native_Ygg_trainable_coefficients":45,
        "conventional_recurrent_coefficients":45,
        "memoryless_original_trainable_coefficients":45,
        "original_ygg_ephemeral_memory_values":8,
        "conventional_recurrent_memory_values":8,
        "original_nonlearned_sensor_raw_bytes":24,
        "original_nonlearned_sensor_prior_delta_bits":8,
        "canonical_trained_model_checkpoint_bytes":{
            name:len(value.encode()) for name,value in saved.items()},
        "native_model_sensor_restart_receipts":report[
            "native_restart_receipts"],
        "candidate_in_process_model_cpu_ns_diagnostic_only":report[
            "candidate_model_only_cpu_ns"],
        "full_source_model_process_CPU_peak_RSS_wire":"NOT_QUALIFIED",
        "fully_camera_normalized_memoryless_comparator":"NOT_QUALIFIED",
        "conventional_count_memory_budget_matched":False,
        "staged_evaluator_action_used":False,
        "hidden_evaluator_door_key_labels_never_model_input":True,
        "natural_occluded_equal_public_twin_pair_observed":False,
        "first_use_science":False,
        "original_source_redistribution_license":"UNRESOLVED",
        "original_g29_atlas_complete_regression":"BLOCKED",
        "scientific_admission":"NO_GO",
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr24b.probe_native_history UPSTREAM")
