"""MR16 live original MiniGrid -> Yggdrasil development-only prequential learning.

All forecasts are computed BEFORE external env.step. The learner and the
conventional controls receive the identical (prior eight public-change
bits, original action) and are updated with the identical eight publicly
measured next-change bits AFTER the real native transition. No object/role
IDs, map, reward, mission, direction, future bits or target-state oracle.
MR15's previously used 16-step script is development-only, NOT fresh science.
"""
import json
import pathlib
import subprocess
import sys
import time

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"research"/"mr15"))

from public_view_delta import PublicViewLocalDelta, SOURCE_COMMIT
from probe_original_view import ACTION_SCRIPT
from native_local_online import (
    NativeLocalActionLearner, ConditionalCount, brier
)

def original_source(root):
    root=pathlib.Path(root).resolve()
    sha=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                                text=True).strip()
    if sha != SOURCE_COMMIT or subprocess.check_output(
        ["git","-C",str(root),"status","--porcelain"],text=True).strip():
        raise ValueError("MR16_ORIGINAL_EXTERNAL_SOURCE_DRIFT")
    return root

def main(upstream):
    external=original_source(upstream)
    sys.path.insert(0,str(external))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv

    learner=NativeLocalActionLearner()
    pooled=ConditionalCount(per_cell=False)
    individual=ConditionalCount(per_cell=True)
    evidence=[]
    receipts=[]
    parent_cpu_start=time.process_time_ns()
    wall_start=time.perf_counter_ns()

    for name,env in (
        ("Original DoorKeyEnv(size=5)",DoorKeyEnv(size=5,render_mode=None)),
        ("Original EmptyEnv(size=8)",EmptyEnv(size=8,render_mode=None))
    ):
        try:
            obs,_=env.reset(seed=11)
            sensor=PublicViewLocalDelta()
            sensor.prime(obs["image"])
            losses={"candidate":[],"pooled_count":[],"cell_count":[]}
            prior_checkpoint=learner.snapshot()
            for i,action in enumerate(ACTION_SCRIPT):
                prior=sensor.bits
                pre={
                    "candidate":learner.predict(prior,action),
                    "pooled_count":pooled.predict(prior,action),
                    "cell_count":individual.predict(prior,action)
                }
                checkpoint=learner.snapshot()
                # No outcome enters the model before the original source
                # executes the action. This is a genuine prequential sequence.
                native_obs,_,terminated,truncated,_=env.step(action)
                event=sensor.observe_after_native_step(action,native_obs["image"])
                future=event["observed_next_local_bits"]
                if (tuple(event["prior_local_bits"])!=prior or
                    event["observed_action"]!=action or
                    event["privileged_world_fields_consumed"]!=0):
                    raise ValueError("MR16_SOURCE_ACTION_EVENT_REORDER_OR_ORACLE")
                for key in losses:
                    losses[key].append(brier(pre[key],future))
                evidence.append((tuple(prior),action,tuple(future)))
                learner.observe_after_original_step(prior,action,future)
                pooled.observe(prior,action,future)
                individual.observe(prior,action,future)
                if learner.snapshot()==checkpoint:
                    raise ValueError("MR16_NATIVE_LEARNER_NO_STATE_UPDATE")
                if i==7:
                    original=learner.snapshot()
                    learner=NativeLocalActionLearner.restore(original)
                    if learner.snapshot()!=original:
                        raise ValueError("MR16_LEARNED_STATE_RESTART_DRIFT")
                    sensor=PublicViewLocalDelta.restore(sensor.snapshot())
                if terminated or truncated:
                    break
            receipts.append({
                "native_source":name,
                "original_native_steps":len(losses["candidate"]),
                "candidate_prequential_brier":sum(losses["candidate"])/len(losses["candidate"]),
                "pooled_conditional_count_prequential_brier":sum(losses["pooled_count"])/len(losses["pooled_count"]),
                "individual_conditional_count_prequential_brier":sum(losses["cell_count"])/len(losses["cell_count"]),
                "original_training_events_prior_to_source":json.loads(prior_checkpoint)["core"]["events"],
                "source_seed":11,
                "data_family":"MR15_ALREADY_USED_DEVELOPMENT_TRACE",
            })
        finally:
            env.close()

    source_state=learner.snapshot()
    if NativeLocalActionLearner.restore(source_state).snapshot()!=source_state:
        raise ValueError("MR16_COLD_LEARNED_STATE_INVALID")
    if learner.rt.core.events!=len(evidence) or len(evidence)!=32:
        raise ValueError("MR16_NATIVE_TRAINING_EVENT_COUNT")
    if (sum(len(row) for row in learner.rt.core.genome)+
        sum(len(row) for row in learner.rt.core.roles)!=45):
        raise ValueError("MR16_NATIVE_45_PARAMETER_BUDGET_DRIFT")

    role_effect=learner.role_ablation_mean_effect(evidence)
    no_role=NativeLocalActionLearner.restore(source_state)
    for i in range(8):
        no_role.rt.core.roles[i]=[0.]*3
    original_dev_brier=sum(brier(learner.predict(x,a),y) for x,a,y in evidence)/32
    no_role_dev_brier=sum(brier(no_role.predict(x,a),y) for x,a,y in evidence)/32
    if learner.snapshot()!=source_state:
        raise ValueError("MR16_ABLATION_CORRUPTED_ORIGINAL_TRAINED_STATE")

    try:
        learner.observe_after_original_step([0]*8,7,[0]*8)
    except ValueError:
        pass
    else:
        raise ValueError("MR16_INVALID_ACTION_LEARNER_MUTATED")
    if learner.snapshot()!=source_state:
        raise ValueError("MR16_INVALID_ACTION_DAMAGED_CHECKPOINT")

    print("MR16_ORIGINAL_NATIVE_LOCAL_PREQUENTIAL="+json.dumps({
        "original_external_source_commit":SOURCE_COMMIT,
        "original_yggdrasil_trainable_coefficients":45,
        "additional_learned_coefficients":0,
        "upstream_original_native_step_calls":len(evidence),
        "native_environment_receipts":receipts,
        "native_source_model_inputs":"8 public-derived prior tile-change bits + explicit pre-outcome native action",
        "native_source_model_targets":"8 PUBLIC observed next tile-change bits after original native step",
        "privileged_world_or_mission_or_reward_or_role_labels_seen_by_learner":False,
        "cold_learned_state_restart":True,
        "train_only_dev_role_ablation_mean_absolute_prediction_delta":role_effect,
        "train_only_dev_brier_trained":original_dev_brier,
        "train_only_dev_brier_roles_reset":no_role_dev_brier,
        "train_only_dev_brier_role_reset_loss_increase":no_role_dev_brier-original_dev_brier,
        "conventional_controls_receive_equal_original_observations":True,
        "conditional_count_control_memory_entries_pooled":len(pooled.counts),
        "conditional_count_control_memory_entries_per_cell":len(individual.counts),
        "retained_untrained_MR15_sidecar_bytes":32,
        "retained_temporal_sensor_snapshot_bytes":229,
        "parent_process_cpu_ns_dev_only":time.process_time_ns()-parent_cpu_start,
        "parent_wall_ns_dev_only":time.perf_counter_ns()-wall_start,
        "full_process_tree_cpu_and_peak_rss_parity":"NOT_QUALIFIED",
        "unknown_task_transfer":"NOT_TESTED",
        "cellular_functional_necessity":"NOT_DEMONSTRATED_FROM_DEV_ROLE_ABLATION",
        "scientific_first_use":False,
        "independent_task_families_scientifically_admitted":0,
        "original_upstream_license_reconciliation":"BLOCKED",
        "scientific_admission":"NO_GO",
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: run_native.py <upstream original source checkout>")
    main(sys.argv[1])
