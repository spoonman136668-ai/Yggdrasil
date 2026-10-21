"""MR23B original MiniGrid native-view covariance prospectivity, DEV only.

All development cohorts and comparison geometry were frozen in
frozen_protocol.json before candidate creation. Original Farama public
7x7x3 observation is permitted TEMPORARY input; retained history remains
the same original MR15 24-byte raw sample plus eight prior bits.
No source world object, pose, mission, reward or task label enters training.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from research.mr15.public_view_delta import (
    PublicViewLocalDelta,SOURCE_COMMIT,public_raw_view
)
from research.mr23b.native_covariance import (
    NativeSourceCorrespondence,public_source_scores
)

MANIFEST=Path(__file__).with_name("frozen_protocol.json")
CLASSES=("DoorKeyEnv(size=5)","EmptyEnv(size=8)")


def verified(original):
    p=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if (p["schema"]!="yggdrasil.mr23b.native-action-view-covariance.dev.v1" or
        p["farama_exact_sha"]!=SOURCE_COMMIT or
        p["training_development_seeds"]!=[137,139] or
        p["evaluation_development_seeds"]!=[149,151] or
        len(p["action_script_training"])!=24 or
        len(p["action_script_evaluation"])!=24 or
        p["common_valid_previous_points_all_hypotheses"]!=[[3,3],[3,5]] or
        p["original_existing_sensor_persistent_memory_bytes"]!=32 or
        p["new_persistent_learner_extra_bytes"]!=0):
        raise ValueError("MR23B_FROZEN_SOURCE_PROTOCOL_DRIFT")
    root=Path(original).resolve()
    sha=subprocess.check_output(
        ["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    dirty=subprocess.check_output(
        ["git","-C",str(root),"status","--porcelain"],text=True).strip()
    if sha!=SOURCE_COMMIT or dirty:
        raise ValueError("MR23B_FARAMA_ORIGINAL_SOURCE_NOT_EXACT")
    return p,root


def one(env,model,actions,seed,family,training,metrics):
    try:
        original,_=env.reset(seed=seed)
        sensor=PublicViewLocalDelta()
        sensor.prime(original["image"])
        for index,action in enumerate(actions):
            prior_raw=public_raw_view(original["image"])
            # Frozen, source-independent model predicts correspondence
            # geometry only using the original known preexecution action.
            probabilities=model.predict_before_native_step(action)
            argmax=max(range(3),key=lambda h:probabilities[h])
            next_original,_reward,terminated,truncated,_info=env.step(action)
            observed=sensor.observe_after_native_step(
                action,next_original["image"])
            if (observed["source_commit"]!=SOURCE_COMMIT or
                observed["observed_action"]!=action or
                sensor.steps!=index+1):
                raise ValueError("MR23B_NATIVE_SOURCE_STEP_NOT_AUTHENTIC")
            if action in (0,1):
                # Scores from ONLY two source-cache points that are visible
                # for EVERY hypothesis -- prevents unequal overlap bias.
                scores=public_source_scores(
                    prior_raw,next_original["image"])
                if len(scores)!=3 or any(not 0<=v<=1 for v in scores):
                    raise ValueError("MR23B_PUBLIC_IMAGE_SCORE_INVALID")
                record={
                    "family":family,"seed":seed,"step":index,
                    "source_action":action,
                    "pre_action_hypothesis_distribution":probabilities,
                    "observed_source_public_agreement":scores,
                    "model":scores[argmax],
                    "action_geometry_A":scores[1 if action==0 else 2],
                    "action_geometry_B":scores[2 if action==0 else 1],
                    "static_camera":scores[0],
                    "hindsight_best_not_a_predictive_control":max(scores),
                    "informative":max(scores)>min(scores),
                }
                metrics["events"]["training" if training else "evaluation"].append(record)
                if training:
                    model.update_after_original_source(
                        action,probabilities,scores)
            if index==9:
                prior_sensor=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(prior_sensor)
                if sensor.snapshot()!=prior_sensor:
                    raise ValueError("MR23B_MR15_NATIVE_SENSOR_RESTART_DRIFT")
                snap=model.snapshot()
                model=NativeSourceCorrespondence.restore(snap)
                if model.snapshot()!=snap:
                    raise ValueError("MR23B_NATIVE_LEARNER_RESTART_DRIFT")
                metrics["native_cold_restarts"]+=1
            original=next_original
            if terminated or truncated:
                break
    finally:
        env.close()
    return model


def averages(rows):
    if not rows:
        raise ValueError("MR23B_NO_NATIVE_CAMERA_TURN_EVENTS")
    labels=("model","action_geometry_A","action_geometry_B",
            "static_camera","hindsight_best_not_a_predictive_control")
    return {
        "camera_turn_events":len(rows),
        "informative_events_where_geometry_changes_score":
            sum(x["informative"] for x in rows),
        "original_prior_byte_triplets_per_candidate":2,
        "original_public_byte_comparisons_per_event":6,
        "mean_exact_triple_agreement":{
            name:sum(e[name] for e in rows)/len(rows) for name in labels
        },
        "candidate_preaction_action_hypothesis_counts":{
            str(i):sum(max(range(3),key=lambda h:
                e["pre_action_hypothesis_distribution"][h])==i
                for e in rows)
            for i in range(3)
        },
    }


def main(source_path):
    p,root=verified(source_path)
    sys.path.insert(0,str(root))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factories=[
        ("DoorKeyEnv(size=5)",lambda:DoorKeyEnv(size=5,render_mode=None)),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None))
    ]
    trained=NativeSourceCorrespondence()
    untrained_state=trained.snapshot()
    data={"events":{"training":[],"evaluation":[]},"native_cold_restarts":0}
    for family,factory in factories:
        for seed in p["training_development_seeds"]:
            trained=one(factory(),trained,p["action_script_training"],
                        seed,family,True,data)
    trained_checkpoint=trained.snapshot()
    if trained_checkpoint==untrained_state:
        raise ValueError("MR23B_NO_REAL_NATIVE_SOURCE_LEARNING")
    candidate=NativeSourceCorrespondence.restore(trained_checkpoint)
    for family,factory in factories:
        for seed in p["evaluation_development_seeds"]:
            candidate=one(factory(),candidate,
                          p["action_script_evaluation"],
                          seed,family,False,data)
    if candidate.snapshot()!=trained_checkpoint:
        raise ValueError("MR23B_EVALUATION_SOURCE_TUNING_LEAK")
    results={
        "all":averages(data["events"]["evaluation"]),
        "by_source":{
            family:averages([
                e for e in data["events"]["evaluation"]
                if e["family"]==family])
            for family,_ in factories
        }
    }
    def beats_both(report):
        scores=report["mean_exact_triple_agreement"]
        return (scores["model"]>scores["action_geometry_A"] and
                scores["model"]>scores["action_geometry_B"] and
                report["informative_events_where_geometry_changes_score"]>0)
    manifest_sha=hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    provenance=hashlib.sha256(json.dumps(
        [[v["family"],v["seed"],v["step"],v["source_action"],
          v["observed_source_public_agreement"]]
         for v in data["events"]["evaluation"]],
        sort_keys=True,separators=(",",":")).encode()).hexdigest()
    print("MR23B_SOURCE_NATIVE_RESOURCE_NEUTRAL_VIEW_COVARIANCE="+json.dumps({
        "source_commit":SOURCE_COMMIT,
        "frozen_protocol_sha256":manifest_sha,
        "public_source_event_history_sha256":provenance,
        "development_train_seeds":p["training_development_seeds"],
        "development_eval_seeds":p["evaluation_development_seeds"],
        "native_experiment":results,
        "candidate_beats_both_fixed_action_cameras_each_source":
            all(beats_both(v) for v in results["by_source"].values()),
        "public_rotation_matching_does_not_identify_physical_objects":True,
        "only_common_valid_camera_sample_positions_compared":True,
        "original_45_native_trainable_coefficient_slots":45,
        "shared_native_coefficients_used_for_action_mapping":21,
        "existing_local_coefficient_slots_frozen":24,
        "previous_original_public_sample_sidecar_bytes":24,
        "previous_original_public_last_delta_bits":8,
        "extra_persistent_learner_memory_bytes":0,
        "full_current_source_7x7x3_temporary_input_bytes":147,
        "learned_model_canonical_snapshot_bytes":
            len(trained_checkpoint.encode()),
        "native_original_source_sensor_model_restarts":
            data["native_cold_restarts"],
        "all_in_original_engine_plus_model_CPU_peak_RSS":
            "NOT_QUALIFIED",
        "strong_fixed_geometry_controls_from_public_action_only":True,
        "hindsight_best_is_not_a_predictive_control":True,
        "independent_protected_science_consumed":False,
        "G29_atlas_exact_source":"NOT_QUALIFIED",
        "upstream_original_license_ambiguity":"UNRESOLVED",
        "scientific_admission":"NO_GO",
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr23b.probe_original_covariance UPSTREAM")
    main(sys.argv[1])
