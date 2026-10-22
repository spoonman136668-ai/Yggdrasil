"""NCI-04 S1: source-native local message specialization vs conventional controls.

Actual independently authored original Farama reset/step is the source of
each post-action target. There is no privileged source grid, object or pose
in model inputs, source policy, gradient, reward or target construction.
Each model forecasts BEFORE the source action. Training builds eight local
messages from just-authenticated public consequences; evaluation freezes
all weights but continues genuine observation-driven inference states.

Different learned role weights do not automatically prove self-organizing
physical-world specialization. Relative camera sample slots are given.
A positive only creates an opt-in ENGINEERING seam; independent unfamiliar
task-family transfer, damage recovery, state-budget-balanced training,
whole-process CPU/RSS and scientific admission remain unqualified.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

from research.mr15.public_view_delta import (
    SOURCE_COMMIT,PublicViewLocalDelta,public_raw_view
)
from research.mr26.public_novelty import BoundedPublicNoveltyExplorer
from research.mr27.natural_memory import source_guard
from research.mr18.native_public_learning import Recurrent45,Native45,PublicCount
from research.nci04_s1.local_messages import LocalPredictiveMessages45

CONTRACT=Path(__file__).with_name("frozen_protocol.json")
KEYS=("s1_messages","same_weights_no_neighbors","same_weights_no_state",
      "conventional_recurrent","conventional_memoryless",
      "public_count_unmatched")


def preflight(original):
    c=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (c["schema"]!="yggdrasil.nci04.s1.native-local-predictive-messaging.dev.v1" or
        c["source_parent_sha"]!="a7e85db2eefe975799acd2f2b23e981db0fcf91a" or
        c["independent_original_farama_git_sha"]!=SOURCE_COMMIT or
        c["training_development_seeds_previously_consumed"]!=
            [263,269,271,277,281,283,293,307] or
        c["new_development_only_evaluation_seeds"]!=[809,811,821,823] or
        c["max_authentic_original_steps_per_episode"]!=256 or
        c["parameters"]!=45 or c["inference_retained_scalar_states"]!=8 or
        c["no_protected_scientific_first_use"] is not True):
        raise ValueError("NCI04_S1_SOURCE_PROTOCOL_DRIFT")
    root=source_guard(original)
    return c,root


def models_new():
    return {
        "s1_messages":LocalPredictiveMessages45(),
        "conventional_recurrent":Recurrent45(),
        "conventional_memoryless":Native45("public"),
        "public_count_unmatched":PublicCount()
    }


def loss(p,y):
    if len(p)!=8 or len(y)!=8 or any(
        type(v) not in (int,float) or not 0<=v<=1 for v in p):
        raise ValueError("NCI04_S1_INVALID_PUBLIC_PREACTION_PREDICTION")
    return sum((a-b)**2 for a,b in zip(p,y))/8.


def native_episode(make,family,seed,training,models,report):
    env=make()
    actor=BoundedPublicNoveltyExplorer(seed)
    sensor=PublicViewLocalDelta()
    model=models["s1_messages"]
    recurrent=models["conventional_recurrent"]
    model.reset_episode()
    recurrent.reset_episode()
    digest=sha256()
    accum={k:0. for k in KEYS}
    per_cell_comm=[0.]*8
    steps=0
    trace_peak=0
    try:
        public,_=env.reset(seed=seed)
        sensor.prime(public["image"])
        for t in range(256):
            raw=public_raw_view(public["image"])
            bits=tuple(sensor.bits)
            action=actor.choose(public["image"])
            # Same learned coefficient values; ablations alter only
            # a pre-action connection, not the trained source data.
            preds={
                "s1_messages":model.predict(raw,bits,action),
                "same_weights_no_neighbors":model.predict(
                    raw,bits,action,drop_neighbors=True),
                "same_weights_no_state":model.predict(
                    raw,bits,action,drop_state=True),
                "conventional_recurrent":recurrent.predict(raw,bits,action),
                "conventional_memoryless":models[
                    "conventional_memoryless"].predict(raw,bits,action),
                "public_count_unmatched":models[
                    "public_count_unmatched"].predict(raw,bits,action)
            }
            original_before=public["image"].tobytes()
            next_public,_reward,terminated,truncated,_info=env.step(action)
            e=sensor.observe_after_native_step(action,next_public["image"])
            next_raw=public_raw_view(next_public["image"])
            targets=e["observed_next_local_bits"]
            if (e["source_commit"]!=SOURCE_COMMIT or
                e["observed_action"]!=action or
                e["prior_local_bits"]!=list(bits) or
                targets!=[int(raw[3*i:3*i+3]!=next_raw[3*i:3*i+3])
                          for i in range(8)]):
                raise ValueError("NCI04_S1_UNAUTHENTIC_ORIGINAL_SOURCE")
            for k in KEYS:
                accum[k]+=loss(preds[k],targets)
            for i in range(8):
                per_cell_comm[i]+=abs(
                    preds["s1_messages"][i]-
                    preds["same_weights_no_neighbors"][i])
            # After source event, move local memories. During training
            # a disclosed one-step 64-float public-only credit trace
            # also contributes to the encoder gradient.
            check=model.observe(raw,bits,action,targets,train=training)
            if check!=preds["s1_messages"]:
                raise ValueError("NCI04_S1_POST_OUTCOME_PREDICTION_LEAK")
            trace_peak=max(trace_peak,len(model.snapshot().encode()))
            if training:
                recurrent.observe(raw,bits,action,targets)
                models["conventional_memoryless"].observe(
                    raw,bits,action,targets)
                models["public_count_unmatched"].observe(
                    raw,bits,action,targets)
            else:
                recurrent.advance_public_history(raw)
            actor.observe_original_next_public_image(
                action,next_public["image"])
            actor.validate()
            digest.update(bytes((action,*bits,*targets)))
            digest.update(sha256(original_before).digest())
            digest.update(sha256(next_public["image"].tobytes()).digest())
            if t==11:
                sensor_snap=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(sensor_snap)
                if sensor.snapshot()!=sensor_snap:
                    raise ValueError("NCI04_S1_SENSOR_COLD_RESTART_DRIFT")
                state_snap=model.snapshot()
                model=LocalPredictiveMessages45.restore(state_snap)
                models["s1_messages"]=model
                if model.snapshot()!=state_snap:
                    raise ValueError("NCI04_S1_NATIVE_LOCAL_RESTART_DRIFT")
                report["native_restart_checks"]+=1
            steps+=1
            public=next_public
            if terminated or truncated:
                break
        if not steps:
            raise ValueError("NCI04_S1_NO_ORIGINAL_NATIVE_ACTIONS")
        return {
            "original_environment":family,"seed":seed,
            "phase":"development_train" if training else "frozen_development_eval",
            "original_native_steps":steps,
            "source_original_public_history_sha256":digest.hexdigest(),
            "brier_by_model":{k:accum[k]/steps for k in KEYS},
            "per_camera_slot_preaction_message_contribution_abs_mean":
                [x/steps for x in per_cell_comm],
            "peak_native_model_snapshot_bytes_including_training_trace":
                trace_peak,
            "observed_one_hop_neighbor_scalar_reads":16*steps,
            "no_evaluator_source_labels_or_rewards_consumed":True
        }
    finally:
        env.close()


def main(original):
    protocol,root=preflight(original)
    sys.path.insert(0,str(root))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factories=(
        ("DoorKeyEnv(size=8)",lambda:DoorKeyEnv(size=8,render_mode=None)),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None))
    )
    models=models_new()
    report={"native_restart_checks":0}
    episodes=[]
    start=time.process_time_ns()
    for family,make in factories:
        for seed in protocol["training_development_seeds_previously_consumed"]:
            episodes.append(native_episode(
                make,family,seed,True,models,report))
    # Authenticated native coefficients FREEZE across all subsequent
    # new DEV source episodes. Only eight public-data states change.
    frozen={
        "s1":models["s1_messages"].runtime.snapshot(),
        "recurrent":[
            [row[:] for row in models["conventional_recurrent"].local],
            models["conventional_recurrent"].shared[:]],
        "memoryless":models["conventional_memoryless"].snapshot(),
        "count":models["public_count_unmatched"].snapshot(),
    }
    checkpoints={
        "candidate_train_checkpoint_with_explicit_64float_trace":
            len(models["s1_messages"].snapshot().encode()),
        "conventional_recurrent":
            len(models["conventional_recurrent"].snapshot().encode()),
        "conventional_memoryless":
            len(models["conventional_memoryless"].snapshot().encode()),
        "public_count_unmatched":
            len(models["public_count_unmatched"].snapshot().encode())
    }
    for family,make in factories:
        for seed in protocol["new_development_only_evaluation_seeds"]:
            episodes.append(native_episode(
                make,family,seed,False,models,report))
    recurrence=models["conventional_recurrent"]
    if (models["s1_messages"].runtime.snapshot()!=frozen["s1"] or
        [recurrence.local,recurrence.shared]!=frozen["recurrent"] or
        models["conventional_memoryless"].snapshot()!=frozen["memoryless"] or
        models["public_count_unmatched"].snapshot()!=frozen["count"]):
        raise ValueError("NCI04_S1_PROSPECTIVE_DEV_WEIGHT_LEAK")
    by_family={}
    for family,_ in factories:
        e=[r for r in episodes if r["phase"]=="frozen_development_eval"
           and r["original_environment"]==family]
        n=sum(x["original_native_steps"] for x in e)
        by_family[family]={
            "native_original_source_steps":n,
            "brier_lower_better":{
                k:sum(x["original_native_steps"]*x["brier_by_model"][k]
                      for x in e)/n for k in KEYS},
            "camera_relative_cell_message_contribution_abs_mean":[
                sum(x["original_native_steps"]*
                    x["per_camera_slot_preaction_message_contribution_abs_mean"][i]
                    for x in e)/n for i in range(8)]
        }
    good={
        "message_channel_improves_over_its_same_weight_ablation_on_both":
            all(s["brier_lower_better"]["s1_messages"]<
                s["brier_lower_better"]["same_weights_no_neighbors"]
                for s in by_family.values()),
        "learned_history_improves_over_same_weight_zero_state_on_both":
            all(s["brier_lower_better"]["s1_messages"]<
                s["brier_lower_better"]["same_weights_no_state"]
                for s in by_family.values()),
        "beats_45weight_8state_trained_conventional_recurrent_both":
            all(s["brier_lower_better"]["s1_messages"]<
                s["brier_lower_better"]["conventional_recurrent"]
                for s in by_family.values()),
        "beats_45weight_conventional_public_memoryless_both":
            all(s["brier_lower_better"]["s1_messages"]<
                s["brier_lower_better"]["conventional_memoryless"]
                for s in by_family.values()),
        "has_nonzero_learned_neighbor_prediction_contribution":any(
            any(x>0 for x in s[
                "camera_relative_cell_message_contribution_abs_mean"])
            for s in by_family.values()),
        "full_source_training_and_inference_total_resource_parity":False,
        "unfamiliar_independent_source_family_transfer":False,
        "genuine_cell_role_recovery_after_damage":False
    }
    all_eval=[r for r in episodes
              if r["phase"]=="frozen_development_eval"]
    print("NCI04_S1_ORIGINAL_NATIVE_LOCAL_PREDICTIVE_COMMUNICATION="+json.dumps({
        "original_source_git_sha":SOURCE_COMMIT,
        "protocol_sha256":sha256(CONTRACT.read_bytes()).hexdigest(),
        "original_source_native_episodes":episodes,
        "prospective_dev_eval_brier":by_family,
        "predeclared_engineering_and_scientific_criteria":good,
        "original_45_native_trainable_coefficient_slots":45,
        "eight_actual_retained_episodic_scalar_states":8,
        "original_nontrained_MR15_public_sensor_sidecar_bytes":32,
        "training_only_previous_public_source_feature_outcome_buffer_scalars":64,
        "candidate_inference_extra_train_trace_scalars":0,
        "original_ring_total_eight_cell_one_hop_scalar_reads_per_step":16,
        "dev_native_observed_neighbor_scalar_reads":sum(
            r["observed_one_hop_neighbor_scalar_reads"] for r in all_eval),
        "one_hop_dev_native_scalar_payload_bytes_float64_equivalent":sum(
            r["observed_one_hop_neighbor_scalar_reads"] for r in all_eval)*8,
        "trained_model_checkpoint_bytes":checkpoints,
        "local_camera_slot_role_logits_after_training":
            models["s1_messages"].local_roles(),
        "native_original_sensor_and_model_restarts":
            report["native_restart_checks"],
        "source_actor_and_full_worker_cpu_ns_shared_process_diagnostic":
            time.process_time_ns()-start,
        "original_full_cpu_peak_rss_and_wire_parity":"NOT_QUALIFIED",
        "same_public_and_action_privileged_truth_never_model_input":True,
        "source_original_labels_rewards_goals_grid_and_pose_to_model":False,
        "camera_relative_roles_not_world_object_roles":True,
        "scientific_first_use_consumed":False,
        "complete_final_G29_semantic_atlas_and_regression":"BLOCKED",
        "original_upstream_license_conflict":"UNRESOLVED",
        "scientific_admission":"NO_GO"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.nci04_s1.original_native_messages ORIGINAL_FARAMA")
    main(sys.argv[1])
