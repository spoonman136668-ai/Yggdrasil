"""MR32A: frozen, source-native full-worker causal-experience cost gate.

Run each MR31 ORIGINAL unchanged policy in a fresh dedicated Python
subprocess on a newly frozen developmental cohort. Each worker process
includes original Farama environment, source-blind actor, retained actor
cache, interpreter, original step, evaluator-only world auditor, explicit
source diagnostic trace encoding. Compare CPU, peak RSS, and diagnostic
trace output bytes. IMPORTANT: different actors alter source trajectories,
so per-step CPU comparison is descriptive, not proof of same executed work
nor a cognitive scientific win. No learner trained in this resource gate.

All candidate/novelty observational alias pairs are scored retrospectively
using the exact current full public image, existing MR15 prior 8-bit sensor
state, action and evaluator-only original native world/pose/inventory.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import pickle
import subprocess
import sys
import tempfile

from research.mr31.original_acquisition import (
    paired_prefix,original_strict_aliases
)
from research.mr32a.isolated_worker import load_contract

MODES=("novelty","contrast")
MARKER="MR32A_ISOLATED_WORKER="


def worker(path,mode,folder):
    out=Path(folder)/(mode+".pkl.gz")
    cmd=[sys.executable,"-B","-m",
         "research.mr32a.isolated_worker",str(path),mode,str(out)]
    env=dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"]="1"
    env["SDL_VIDEODRIVER"]="dummy"
    env["SDL_AUDIODRIVER"]="dummy"
    proc=subprocess.run(cmd,capture_output=True,text=True,
                        check=False,env=env)
    if proc.returncode!=0:
        raise ValueError(
            "MR32A_SOURCE_NATIVE_SUBPROCESS_FAILED_"+mode+": "+
            proc.stderr[-4000:])
    receipts=[ln[len(MARKER):] for ln in proc.stdout.splitlines()
              if ln.startswith(MARKER)]
    if len(receipts)!=1 or not out.is_file():
        raise ValueError("MR32A_MISSING_MANDATORY_CHILD_SOURCE_RECEIPT")
    report=json.loads(receipts[0])
    if report["mode"]!=mode or report[
        "offline_evaluator_trace_wire_bytes"]!=out.stat().st_size:
        raise ValueError("MR32A_UNAUTHORIZED_OR_TRUNCATED_ORIGINAL_TRACE")
    with gzip.open(out,"rb") as f:
        rows,episodes=pickle.load(f)
    if (len(episodes)!=report["native_original_episode_count"] or
        len(rows)!=report["native_original_action_count"] or
        any(r["mode"]!=mode for r in rows) or
        any(x["mode"]!=mode for x in episodes)):
        raise ValueError("MR32A_CHILD_ORIGINAL_NATIVE_EVIDENCE_DRIFT")
    digest=hashlib.sha256(json.dumps([
        [r["mode"],r["family"],r["seed"],r["stream"],
         r["original_native_actions"],
         r["original_native_action_history_sha256"]]
        for r in episodes
    ],sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if report["native_source_history_sha256"]!=digest:
        raise ValueError("MR32A_ISOLATED_ORIGINAL_NATIVE_SOURCE_DIGEST_DRIFT")
    return rows,episodes,report


def main(original):
    p=load_contract()
    if p["no_postresult_tuning"] is not True or (
        p["scientific_admission"] is not False):
        raise ValueError("MR32A_SCIENTIFIC_FIRST_USE_FROZEN_CUSTODY")
    rows=[]
    episodes=[]
    cost={}
    with tempfile.TemporaryDirectory(prefix="mr32a-source-original-") as tmp:
        for mode in MODES:
            native,receipts,report=worker(original,mode,tmp)
            rows.extend(native)
            episodes.extend(receipts)
            cost[mode]=report
    if len(episodes)!=96:
        raise ValueError("MR32A_NATIVE_SOURCE_COHORT_EPISODES_INVALID")
    maximum={x["same_structural_actor_max_payload_bytes"]
             for x in cost.values()}
    if len(maximum)!=1:
        raise ValueError("MR32A_FIXED_ACTOR_MEMORY_CAPACITY_NOT_EQUAL")
    clipped,limits=paired_prefix(rows,episodes)
    if len(limits)!=48:
        raise ValueError("MR32A_MATCHED_ORIGINAL_EPISODE_COUNT")
    results=original_strict_aliases(clipped)
    if any(v["truncated_equivalence_groups"] for v in results.values()):
        raise ValueError("MR32A_ORIGINAL_SOURCE_CAUSAL_PAIR_AUDIT_TRUNCATED")
    by_policy={}
    for mode in MODES:
        ee=[r for r in episodes if r["mode"]==mode]
        if len(ee)!=48:
            raise ValueError("MR32A_FROZEN_POLICY_EPISODE_MISMATCH")
        by_policy[mode]={
            "actual_original_native_actions":sum(
                x["original_native_actions"] for x in ee),
            "strictly_matched_source_prefix_actions":sum(limits.values()),
            "source_native_public_visible_pickup_to_unlock_episodes":sum(
                bool(x["visible_pickup_then_visible_unlock"]) for x in ee),
            "source_true_original_door_unlocks_evaluator_only":sum(
                x["original_world_door_unlocks_evaluator_only"] for x in ee),
            "source_true_original_key_pickups_evaluator_only":sum(
                x["original_world_key_pickups_evaluator_only"] for x in ee),
            "original_public_source_frame_change_events":sum(
                x["source_public_image_changed_events"] for x in ee),
            "new_original_public_frames":sum(
                x["native_actor_public_frames_discovered"] for x in ee),
            "native_original_full_worker_cpu_ns":
                cost[mode][
                    "isolated_original_env_actor_and_evaluator_process_cpu_ns"],
            "native_original_full_worker_CPU_ns_per_actual_source_action":
                cost[mode][
                    "isolated_original_env_actor_and_evaluator_process_cpu_ns"]/
                sum(x["original_native_actions"] for x in ee),
            "original_worker_OS_peak_rss_bytes":
                cost[mode]["os_isolated_worker_peak_resident_bytes"],
            "full_original_evaluator_trace_wire_bytes":
                cost[mode]["offline_evaluator_trace_wire_bytes"],
            "fixed_actor_max_payload_bytes":next(iter(maximum)),
            "max_actual_actor_payload_bytes":
                cost[mode]["max_actual_actor_payload_bytes"],
            "max_estimated_actual_actor_python_container_bytes":
                cost[mode][
                    "max_measured_actor_container_estimate_bytes"],
            "max_original_rng_state_pickle_bytes":
                cost[mode]["rng_state_pickle_bytes_max"],
        }
    novelty=by_policy["novelty"]
    contrast=by_policy["contrast"]
    seed_counts={mode:len(results[mode][
        "strict_original_reset_seed_clusters"]) for mode in MODES}
    protocol_conditions={
        "native_source_strict_alias_seed_cluster_yield_increases":
            seed_counts["contrast"]>seed_counts["novelty"],
        "native_source_original_strict_pairs_exist":
            results["contrast"][
                "strict_different_world_and_next_eightbit_pairs"]>0,
        "visible_source_native_key_to_door_acquisition_not_worse":
            contrast["source_native_public_visible_pickup_to_unlock_episodes"]>=
            novelty["source_native_public_visible_pickup_to_unlock_episodes"],
        "same_fixed_actor_storage_capacity":
            contrast["fixed_actor_max_payload_bytes"]==
            novelty["fixed_actor_max_payload_bytes"],
        "full_isolated_worker_cpu_nonregression":
            contrast["native_original_full_worker_cpu_ns"]<=
            novelty["native_original_full_worker_cpu_ns"],
        "full_os_process_peak_rss_nonregression":
            contrast["original_worker_OS_peak_rss_bytes"]<=
            novelty["original_worker_OS_peak_rss_bytes"],
        "full_evaluator_trace_wire_nonregression":
            contrast["full_original_evaluator_trace_wire_bytes"]<=
            novelty["full_original_evaluator_trace_wire_bytes"],
        "same_original_execution_workload_not_just_action_cap":False,
        "independent_first_use_scientific_transfer_proven":False,
        "new_45_weight_learned_causal_memory_advantage":False
    }
    srcdigest=hashlib.sha256(json.dumps(
        [[m,cost[m]["native_source_history_sha256"]] for m in MODES],
        sort_keys=True,separators=(",",":")).encode()).hexdigest()
    print("MR32A_ISOLATED_NATIVE_PUBLIC_CAUSAL_COST="+json.dumps({
        "original_source_git_commit":
            p["original_farama_source_commit"],
        "frozen_precode_protocol_sha256":
            hashlib.sha256(
                Path(__file__).with_name("frozen_protocol.json").read_bytes()
            ).hexdigest(),
        "source_uninterrupted_episode_count":len(episodes),
        "original_native_source_history_digest":srcdigest,
        "equal_original_source_seed_stream_prefix_actions_per_policy":
            sum(limits.values()),
        "original_source_development_evidence_per_policy":by_policy,
        "original_source_retrospective_true_causal_contrasts":results,
        "source_independent_seed_cluster_count_with_causal_contrast":
            seed_counts,
        "precommitted_evidence_and_cost_conditions":
            protocol_conditions,
        "isolated_full_process_includes_source_actor_evaluator_and_trace":True,
        "CI_parent_and_machine_power_energy_not_measured":True,
        "different_native_trajectory_workload_makes_total_time_noncausal":True,
        "no_unmatched_new_cognitive_model_parameters":True,
        "native_original_45_coefficient_learner_unmodified":True,
        "native_original_32_byte_sensor_sidecar_unchanged":True,
        "no_hidden_world_truth_supplied_to_actor":True,
        "all_private_original_world_labels_retrospective_only":True,
        "source_dev_only_not_protected_scientific_first_use":True,
        "G29_source_bound_atlas_and_full_regression":"BLOCKED",
        "external_source_license_discrepancy":"UNRESOLVED",
        "scientific_admission":"NO_GO"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr32a.original_native_cost ORIGINAL_SOURCE")
    main(sys.argv[1])
