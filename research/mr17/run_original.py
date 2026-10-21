"""MR17: independently compare local-contrast credit with original MR16.

Run the SAME already-consumed MR15 native development action scripts on
original pinned upstream MiniGrid. All predictors forecast BEFORE env.step;
they all consume identical eight original PUBLIC image change bits afterward.
Original Yggdrasil source and all protected scientific tests remain untouched.
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

from public_view_delta import PublicViewLocalDelta,SOURCE_COMMIT
from probe_original_view import ACTION_SCRIPT
from research.mr16.native_local_online import NativeLocalActionLearner, ConditionalCount, brier
from research.mr17.contrastive_local import LocalContrastLearner


def original_source(upstream):
    root=pathlib.Path(upstream).resolve()
    sha=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    status=subprocess.check_output(
        ["git","-C",str(root),"status","--porcelain"],text=True).strip()
    if sha!=SOURCE_COMMIT or status:
        raise ValueError("MR17_ORIGINAL_EXTERNAL_SOURCE_DRIFT")
    return root


def run():
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv

    contrast=LocalContrastLearner()
    old=NativeLocalActionLearner()
    pooled=ConditionalCount(per_cell=False)
    each=ConditionalCount(per_cell=True)
    prior_only_events=[]
    results=[]
    cpu_start=time.process_time_ns()
    wall_start=time.perf_counter_ns()
    for label,environment in (
        ("Original DoorKeyEnv(size=5)",DoorKeyEnv(size=5,render_mode=None)),
        ("Original EmptyEnv(size=8)",EmptyEnv(size=8,render_mode=None))
    ):
        try:
            first,_=environment.reset(seed=11)
            sensor=PublicViewLocalDelta()
            sensor.prime(first["image"])
            scores={name:[] for name in
                    ("mr17","mr16","count_pooled","count_cell")}
            for step,action in enumerate(ACTION_SCRIPT):
                prior=tuple(sensor.bits)
                # All four predictions originate from the SAME pre-outcome
                # eight public bits and announced ORIGINAL native action.
                predictions={
                    "mr17":contrast.predict(prior,action),
                    "mr16":old.predict(prior,action),
                    "count_pooled":pooled.predict(prior,action),
                    "count_cell":each.predict(prior,action)
                }
                original_state=contrast.snapshot()
                original_sensor=sensor.snapshot()
                next_obs,_,terminated,truncated,_=environment.step(action)
                event=sensor.observe_after_native_step(action,next_obs["image"])
                next_bits=tuple(event["observed_next_local_bits"])
                if (tuple(event["prior_local_bits"])!=prior or
                    event["observed_action"]!=action or
                    event["privileged_world_fields_consumed"]!=0):
                    raise ValueError("MR17_SOURCE_OBSERVATION_REORDERED")
                for name,p in predictions.items():
                    scores[name].append(brier(p,next_bits))
                # Genuine source outcome is given to ALL trained models AFTER
                # observing the original public next image. No role labels.
                contrast.observe_after_original_step(prior,action,next_bits)
                old.observe_after_original_step(prior,action,next_bits)
                pooled.observe(prior,action,next_bits)
                each.observe(prior,action,next_bits)
                if contrast.snapshot()==original_state:
                    raise ValueError("MR17_LOCAL_MODEL_NOT_LEARNING")
                prior_only_events.append((prior,action,next_bits))
                if step==7:
                    c=contrast.snapshot()
                    o=old.snapshot()
                    s=sensor.snapshot()
                    contrast=LocalContrastLearner.restore(c)
                    old=NativeLocalActionLearner.restore(o)
                    sensor=PublicViewLocalDelta.restore(s)
                    if (contrast.snapshot()!=c or old.snapshot()!=o
                        or sensor.snapshot()!=s):
                        raise ValueError("MR17_NATIVE_COLD_RESTART_DRIFT")
                if terminated or truncated:
                    break
            results.append({
                "original_environment":label,
                "native_steps":len(scores["mr17"]),
                "prequential_brier":{k:sum(v)/len(v) for k,v in scores.items()},
                "already_consumed_development_action_script":True,
            })
        finally:
            environment.close()

    frozen=contrast.snapshot()
    frozen_old=old.snapshot()
    if len(prior_only_events)!=32 or contrast.rt.core.events!=32 or old.rt.core.events!=32:
        raise ValueError("MR17_NATIVE_STEP_EVENT_COUNT")
    if (sum(len(r) for r in contrast.rt.core.genome)+
        sum(len(r) for r in contrast.rt.core.roles)!=45):
        raise ValueError("MR17_NATIVE_FIXED_BUDGET_FAILED")

    original_mean=sum(brier(contrast.predict(p,a),y)
                      for p,a,y in prior_only_events)/32.
    missing_all=LocalContrastLearner.restore(frozen)
    for cell in range(8):
        missing_all.rt.core.roles[cell]=[0.,0.,0.]
    no_role_mean=sum(brier(missing_all.predict(p,a),y)
                     for p,a,y in prior_only_events)/32.
    roles=[]
    for cell in range(8):
        alt=contrast.ablate_cell(cell)
        effect=sum(abs(contrast.predict(p,a)[cell]-alt.predict(p,a)[cell])
                   for p,a,_ in prior_only_events)/32.
        error_delta=sum(
            (alt.predict(p,a)[cell]-y[cell])**2-
            (contrast.predict(p,a)[cell]-y[cell])**2
            for p,a,y in prior_only_events)/32.
        roles.append({"cell":cell,"mean_absolute_prediction_effect":effect,
                      "development_observed_cell_brier_loss_delta":error_delta})
    assert any(x["mean_absolute_prediction_effect"]>0 for x in roles)
    assert contrast.snapshot()==frozen
    assert old.snapshot()==frozen_old
    try:
        contrast.observe_after_original_step([0]*8,7,[0]*8)
    except ValueError:
        pass
    else:
        raise ValueError("MR17_INVALID_ACTION_ACCEPTED")
    assert contrast.snapshot()==frozen

    print("MR17_LOCAL_CAUSAL_CREDIT_NATIVE_DEV="+json.dumps({
        "source_commit":SOURCE_COMMIT,
        "candidate_architecture":"immediate-neighbor contrastive prediction residuals in eight private three-weight states",
        "original_45_trainable_coefficients":45,
        "original_shared_genome_coefficients":21,
        "original_private_role_coefficients":24,
        "new_trainable_coefficients":0,
        "source_native_prequential_32_steps":32,
        "original_environments":results,
        "mean_loss_trained_dev_replay":original_mean,
        "mean_loss_all_local_roles_reset_dev_replay":no_role_mean,
        "all_roles_reset_dev_brier_degradation":no_role_mean-original_mean,
        "each_cell_role_only_dev_ablation":roles,
        "roles_required_on_unseen_task":"NOT_TESTED",
        "per_cell_feedback_neighborhood":"self_and_two_immediate_neighbors_only",
        "intercell_feedback_transport":"LOCAL_IN_PROCESS_NOT_DISTRIBUTED_OR_WIRE_QUALIFIED",
        "native_source_info":"eight original public temporal bits plus pre-execution original action",
        "original_sensor_nontrained_sidecar_bytes":32,
        "serialized_original_sensor_checkpoint_bytes":229,
        "original_mr16_baseline_uses_same_32_native_actions":True,
        "original_conditional_counts_receives_same_data":True,
        "pooled_count_entries":len(pooled.counts),
        "per_cell_count_entries":len(each.counts),
        "parent_only_cpu_ns":time.process_time_ns()-cpu_start,
        "parent_only_wall_ns":time.perf_counter_ns()-wall_start,
        "all_in_parent_child_cpu_rss_budget":"NOT_QUALIFIED",
        "upstream_license_conflict":"UNRESOLVED",
        "protected_scientific_first_use":False,
        "transfer_proven":False,
        "local_specialized_function_proven":False,
        "scientific_admission":"BLOCKED"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: run_original.py ORIGINAL_UPSTREAM_CHECKOUT")
    upstream=original_source(sys.argv[1])
    sys.path.insert(0,str(upstream))
    run()
