"""MR30: frozen independent DEV replication of MR29's native causal-memory signal.

This experiment deliberately does NOT modify or tune the learner, its
coefficients, novelty training policy, current raw-image sensor or source
evaluation trajectories using previously observed MR29 outcomes.

The original-source native learner trains ONLY on MR26 previously consumed
development episodes. Frozen weights are scored prospectively on NEW
preregistered public-only, uninterrupted native streams. Diagnostic native
world and pose are consumed ONLY AFTER predictions have been recorded,
solely for exact observational-alias matching. Pairs from a single reset
seed are correlated, so evidence is reported by original seed cluster.
"""
import copy
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

from research.mr15.public_view_delta import SOURCE_COMMIT
from research.mr27.natural_memory import source_guard
from research.mr29.native_causal_alias import (
    audit_aliases,prepare_training,source_episode
)

PROTOCOL=Path(__file__).with_name("frozen_protocol.json")
SCHEMA="yggdrasil.mr30.independent-natural-causal-replication.dev.v1"
NAMES=("innovation","same_weights_no_state","recurrent",
       "stateless","count","zero","half")


def validate(source):
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if (p["schema"]!=SCHEMA or
        p["exact_parent_sha"]!="cc55f042adce8da6faa68d16611f0b39a73e9c57" or
        p["upstream_original_sha"]!=SOURCE_COMMIT or
        p["prior_train_development_seeds"]!=
            [263,269,271,277,281,283,293,307] or
        p["unseen_dev_replication_door_seeds"]!=
            [503,509,521,523,541,547,557,563,569,571,577,587] or
        p["unseen_dev_replication_empty_seeds"]!=[503,509,521,523] or
        p["identical_source_native_action_stream_ids"]!=[0,1,2,3] or
        p["original_steps_per_episode"]!=256 or
        p["unmodified_mr29_native_scoring"] is not True or
        p["trainable_coefficients"]!=45 or p["episodic_state_scalars"]!=8 or
        p["no_hidden_truth_to_policy_or_model"] is not True or
        p["no_evaluator_staging"] is not True):
        raise ValueError("MR30_FROZEN_PROTOCOL_IDENTITY_DRIFT")
    original=source_guard(source)
    return p,original


def by_family_loss(receipts,family):
    native=[x for x in receipts if x["family"]==family]
    size=sum(x["genuine_original_steps"] for x in native)
    if size<=0:
        raise ValueError("MR30_MISSING_ORIGINAL_SOURCE_EVALUATION")
    return {
        "genuine_original_native_steps":size,
        "original_source_preaction_brier":{
            key:sum(e["per_model_brier"][key]*e["genuine_original_steps"]
                    for e in native)/size for key in NAMES
        },
        "independent_original_seed_clusters":len(set(
            e["seed"] for e in native)),
    }


def main(original_root):
    cfg,src=validate(original_root)
    sys.path.insert(0,str(src))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factories=(
        ("DoorKeyEnv(size=8)",lambda:DoorKeyEnv(size=8,render_mode=None)),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None))
    )
    t0=time.process_time_ns()
    trained,snapshots,training=prepare_training(
        factories,cfg["prior_train_development_seeds"])
    # Frozen canonical model objects copied by source_episode for each
    # independently reset source-native evaluation stream.
    source_rows=[]
    source_receipts=[]
    for family,make in factories:
        seeds=(cfg["unseen_dev_replication_door_seeds"]
               if family=="DoorKeyEnv(size=8)"
               else cfg["unseen_dev_replication_empty_seeds"])
        for seed in seeds:
            for stream in cfg["identical_source_native_action_stream_ids"]:
                rows,receipt=source_episode(
                    make,family,seed,stream,cfg["original_steps_per_episode"],
                    snapshots,trained["public_count"])
                source_rows.extend(rows)
                source_receipts.append(receipt)
    # This is a retrospective diagnostic; no representation of its
    # matches is given to the source predictor or action policy.
    original_pairs=audit_aliases(
        source_rows,20000)
    if original_pairs["truncated_pair_groups"]>0:
        raise ValueError("MR30_FROZEN_ALIAS_PAIR_AUDIT_TRUNCATED")

    # Genuine original RESET SEED is the independent sampling unit, NOT
    # each highly correlated pair from the same world/policy streams.
    door_seeds=cfg["unseen_dev_replication_door_seeds"]
    clusters=[]
    for seed in door_seeds:
        subset=[row for row in source_rows if
                row["family"]=="DoorKeyEnv(size=8)" and row["seed"]==seed]
        original=audit_aliases(subset,20000)
        pair_count=original["strict_natural_full_input_causal_pairs"]
        score=original["predictor_per_strict_pair"]
        clusters.append({
            "original_reset_seed":seed,
            "genuine_natural_alias_pairs":pair_count,
            "candidate_signed_directional_margin":
                score["innovation"]["mean_directional_preoutcome_margin"],
            "candidate_conflicting_bit_Brier":
                score["innovation"]["mean_conflicting_bit_source_brier"],
            "same_weights_memory_disabled_conflicting_bit_Brier":
                score["same_weights_no_state"]["mean_conflicting_bit_source_brier"],
            "trained_recurrent_conflicting_bit_Brier":
                score["recurrent"]["mean_conflicting_bit_source_brier"],
            "source_alias_evaluator_only":True,
        })
    if sum(c["genuine_natural_alias_pairs"] for c in clusters)!=sum(
         audit_aliases([
             r for r in source_rows
             if r["family"]=="DoorKeyEnv(size=8)"
         ],20000)["strict_natural_full_input_causal_pairs"]
         for _ in (0,)):
        raise ValueError("MR30_DEVELOPMENT_SOURCE_CLUSTER_MEMBERSHIP_DRIFT")
    # Pair matches across different native reset seeds prohibited by MR29.
    by_family={family:by_family_loss(source_receipts,family)
               for family,_ in factories}
    strict=original_pairs["predictor_per_strict_pair"]
    pairs=original_pairs["strict_natural_full_input_causal_pairs"]
    door=by_family["DoorKeyEnv(size=8)"]["original_source_preaction_brier"]
    empty=by_family["EmptyEnv(size=8)"]["original_source_preaction_brier"]
    gate={
        "naturally_reached_strict_full_input_causal_alias":pairs>0,
        "positive_authentic_causal_directional_margin":bool(
            pairs and strict["innovation"]["mean_directional_preoutcome_margin"]>0),
        "conflicting_bit_memory_advantage_over_same_weights_erased":bool(
            pairs and
            strict["innovation"]["mean_conflicting_bit_source_brier"]<
            strict["same_weights_no_state"]["mean_conflicting_bit_source_brier"]),
        "conflicting_bit_memory_advantage_over_fully_trained_recurrent":bool(
            pairs and
            strict["innovation"]["mean_conflicting_bit_source_brier"]<
            strict["recurrent"]["mean_conflicting_bit_source_brier"]),
        "door_world_average_better_than_recurrent_and_same_weights_erased":
            door["innovation"]<min(door["recurrent"],
                                    door["same_weights_no_state"]),
        "empty_nonregression_vs_recurrent_and_public_memoryless":
            empty["innovation"]<=min(empty["recurrent"],empty["stateless"]),
        "independent_original_seed_clusters_at_least_three_with_alias":
            sum(c["genuine_natural_alias_pairs"]>0 for c in clusters)>=3,
        "complete_resource_parity_qualified":False,
        "protected_unseen_source_family_replication":False,
    }
    # Do not combine outcomes from unequal episode durations by ordinary
    # mean; absolute original source action counts are the weights.
    history_digest=sha256(json.dumps([
        [e["family"],e["seed"],e["stream"],e["genuine_original_steps"],
         e["genuine_original_source_history_sha256"]]
        for e in source_receipts],sort_keys=True,
        separators=(",",":")).encode()).hexdigest()
    print("MR30_ORIGINAL_NATIVE_CAUSAL_SIGNAL_REPLICATION="+json.dumps({
        "exact_original_source_commit":SOURCE_COMMIT,
        "predeclared_protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "frozen_development_train_source_episodes":len(training),
        "fresh_native_development_eval_episodes":len(source_receipts),
        "fresh_native_development_eval_steps":len(source_rows),
        "authentic_native_uninterrupted_history_digest":history_digest,
        "frozen_original_source_eval":by_family,
        "strict_same_entire_current_input_world_different_outcome":
            original_pairs,
        "per_independent_original_DoorKey_seed_clusters":clusters,
        "scientific_conditions":gate,
        "actual_positive_causal_pair_seed_cluster_count":sum(
            c["genuine_natural_alias_pairs"]>0 for c in clusters),
        "independent_pair_significance_not_claimed_without_seed_clusters":True,
        "matched_model_trainable_coefficients":45,
        "native_and_recurrent_ephemeral_activations":8,
        "original_MR15_sensor_sidecar_bytes":32,
        "per_model_frozen_training_snapshots_bytes":{
            k:len(v.encode()) for k,v in snapshots.items()},
        "same_source_native_predictions_made_preaction":True,
        "privileged_world_pose_inventory_labels_to_learner":False,
        "source_native_evaluator_staging":False,
        "full_isolated_process_cpu_peak_rss_all_models_and_wire":
            "NOT_QUALIFIED",
        "camera_corrected_fully_informed_memoryless_comparator":
            "NOT_QUALIFIED",
        "source_policy_fifo_rng_memory_parity":
            "NOT_QUALIFIED",
        "shared_all_models_process_cpu_ns_diagnostic":
            time.process_time_ns()-t0,
        "protected_scientific_first_use":False,
        "independent_task_family_transfer":"NOT_TESTED",
        "source_bound_G29_atlas":"BLOCKED",
        "original_farama_license_ambiguity":"UNRESOLVED",
        "scientific_admission":"NO_GO"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr30.replicate_original_causal_signal ORIGINAL_SOURCE")
    main(sys.argv[1])
