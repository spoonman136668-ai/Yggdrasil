"""MR26: compare authentic uninterrupted public-only acquisition policies.

Predeclared novel DEVELOPMENT seeds, exactly the SAME per-episode native
action budget and same independent original MiniGrid source. Baseline calls
MR24A original policy UNMODIFIED. Novelty policy uses only original public
7x7x3 image pixels and its OWN action/public image-change history.
Evaluator-held original door/key checks occur ONLY AFTER env.step; never
enter either policy. No model training or independent scientific first use.
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
from research.mr24.natural_history import (
    public_only_action,source_evaluator_private_door
)
from research.mr26.public_novelty import (
    BoundedPublicNoveltyExplorer,original_public_image_key,BASE,CAP
)

ROOT=Path(__file__).resolve().parents[2]
FROZEN=ROOT/"research"/"mr26"/"frozen_protocol.json"


def qualified_original_source(root):
    root=Path(root).resolve()
    sha=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                                text=True).strip()
    dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],
                                  text=True).strip()
    if sha!=SOURCE_COMMIT or dirty:
        raise ValueError("MR26_ORIGINAL_SOURCE_COMMIT_OR_WORKTREE_DRIFT")
    return root


def original_source_episode(factory,family,seed,cap,policy_name):
    from minigrid.core.world_object import Key
    native=factory()
    start=time.process_time_ns()
    process=psutil.Process()
    rss_max=process.memory_info().rss
    rng=random.Random(1000003*seed+337)
    novelty=BoundedPublicNoveltyExplorer(seed) if policy_name=="novelty" else None
    audit_hash=hashlib.sha256()
    steps=0
    actions=[0]*7
    full_public_frame_changes=0
    public_frame_hashes=set()
    picked=[]
    unlocked=[]
    visible_picked=[]
    visible_unlocked=[]
    try:
        obs,_=native.reset(seed=seed)
        original_sensor=PublicViewLocalDelta()
        original_sensor.prime(obs["image"])
        source_door=(source_evaluator_private_door(native)
                     if family=="DoorKeyEnv(size=8)" else None)
        if source_door is not None and (
            not source_door.is_locked or source_door.is_open):
            raise ValueError("MR26_ORIGINAL_NATIVE_DOOR_INITIAL_DRIFT")
        previously_carrying=False
        previously_open=False
        ended=False
        truncated=False
        for index in range(cap):
            # Strict policy input API contains ORIGINAL public image only.
            key=original_public_image_key(obs["image"])
            public_frame_hashes.add(key)
            prior_public_sample=public_raw_view(obs["image"])
            prior_delta=list(original_sensor.bits)
            if policy_name=="baseline":
                action=public_only_action({"image":obs["image"]},rng)
            else:
                action=novelty.choose(obs["image"])
            if type(action) is not int or not 0<=action<=5:
                raise ValueError("MR26_PUBLIC_EXPLORER_ACTION_INVALID")
            actions[action]+=1

            nxt,_reward,ended,truncated,_info=native.step(action)
            source_event=original_sensor.observe_after_native_step(
                action,nxt["image"])
            next_sample=public_raw_view(nxt["image"])
            expected=[int(prior_public_sample[3*i:3*i+3]!=
                          next_sample[3*i:3*i+3])
                      for i in range(8)]
            if (source_event["source_commit"]!=SOURCE_COMMIT or
                source_event["observed_action"]!=action or
                source_event["prior_local_bits"]!=prior_delta or
                source_event["observed_next_local_bits"]!=expected or
                source_event["privileged_world_fields_consumed"]!=0 or
                source_event["raw_temporal_sidecar_bytes"]!=24):
                raise ValueError("MR26_ORIGINAL_PUBLIC_ACTION_RESULT_INVALID")
            if novelty is not None:
                novelty.observe_original_next_public_image(
                    action,nxt["image"])
                novelty.validate()
            newkey=original_public_image_key(nxt["image"])
            full_public_frame_changes+=int(key!=newkey)
            public_frame_hashes.add(newkey)
            audit_hash.update(bytes([action]+prior_delta+expected))
            audit_hash.update(key)
            audit_hash.update(newkey)

            # Separate private diagnostic EVALUATOR after the source event.
            # Its values NEVER return to action selection or policy credit.
            holding_key=isinstance(native.carrying,Key)
            open_door=(bool(source_door.is_open)
                       if source_door is not None else False)
            if holding_key and not previously_carrying:
                picked.append(index)
                if sum(expected)>0:
                    visible_picked.append(index)
            if open_door and not previously_open:
                unlocked.append(index)
                if sum(expected)>0:
                    visible_unlocked.append(index)
            previously_carrying=holding_key
            previously_open=open_door
            steps+=1
            obs=nxt
            rss_max=max(rss_max,process.memory_info().rss)
            if index==11:
                snap=original_sensor.snapshot()
                restored=PublicViewLocalDelta.restore(snap)
                if restored.snapshot()!=snap:
                    raise ValueError("MR26_ORIGINAL_SENSOR_RESTART_DRIFT")
                original_sensor=restored
            if ended or truncated:
                break

        if steps<=0 or steps>cap or sum(actions)!=steps:
            raise ValueError("MR26_NATIVE_ACTION_BUDGET_VIOLATION")
        qualifies=any(u>p for p in visible_picked for u in visible_unlocked)
        return {
            "family":family,"original_source_seed":seed,
            "exploration_policy":policy_name,
            "actual_original_native_steps":steps,
            "original_source_native_experience_sha256":audit_hash.hexdigest(),
            "native_action_histogram":actions,
            "original_native_key_pickups_evaluator_only":len(picked),
            "original_native_door_unlocks_evaluator_only":len(unlocked),
            "native_sampled_public_pickup_steps":visible_picked,
            "native_sampled_public_unlock_steps":visible_unlocked,
            "qualifying_natural_visible_pickup_then_unlock":qualifies,
            "complete_public_image_changes":full_public_frame_changes,
            "unique_public_frames_evaluator_only":len(public_frame_hashes),
            "native_original_terminated":bool(ended),
            "native_original_truncated":bool(truncated),
            "untrained_MR15_sensor_bytes":32,
            "candidate_policy_cache_capacity":CAP if novelty else 0,
            "additional_candidate_policy_snapshot_bytes":
                novelty.extra_untrained_policy_bytes() if novelty else 0,
            "additional_policy_state_durable_rng_restore_qualified":False,
            "single_shared_process_episode_cpu_ns":time.process_time_ns()-start,
            "sampled_shared_process_peak_rss_bytes":rss_max,
        }
    finally:
        native.close()


def main(upstream):
    p=json.loads(FROZEN.read_text(encoding="utf-8"))
    if (p["schema"]!="yggdrasil.mr26.native-public-novelty-causal-acquisition.dev.v1" or
        p["predecessor"]!="56eebe89749c3c3ddfad10ce1ce4366d78c83381" or
        p["independent_original_farama_source"]!=SOURCE_COMMIT or
        p["fresh_development_seeds"]!=[263,269,271,277,281,283,293,307] or
        p["action_budget_each_original_episode"]!=256 or
        p["action_base_weights"]!=list(BASE)):
        raise ValueError("MR26_FROZEN_DEVELOPMENT_PROTOCOL_DRIFT")
    source=qualified_original_source(upstream)
    sys.path.insert(0,str(source))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factories=(
        ("DoorKeyEnv(size=8)",lambda:DoorKeyEnv(size=8,render_mode=None)),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None))
    )
    source_results=[]
    start=time.process_time_ns()
    for family,factory in factories:
        for seed in p["fresh_development_seeds"]:
            for policy in ("baseline","novelty"):
                source_results.append(original_source_episode(
                    factory,family,seed,256,policy))
    comparisons=[]
    for seed in p["fresh_development_seeds"]:
        a=next(r for r in source_results if r["family"]=="DoorKeyEnv(size=8)"
               and r["original_source_seed"]==seed
               and r["exploration_policy"]=="baseline")
        b=next(r for r in source_results if r["family"]=="DoorKeyEnv(size=8)"
               and r["original_source_seed"]==seed
               and r["exploration_policy"]=="novelty")
        comparisons.append({
            "original_seed":seed,
            "baseline_causal_exposure":a["qualifying_natural_visible_pickup_then_unlock"],
            "novelty_causal_exposure":b["qualifying_natural_visible_pickup_then_unlock"],
            "original_budget_each":256,
            "actual_steps_baseline":a["actual_original_native_steps"],
            "actual_steps_novelty":b["actual_original_native_steps"],
            "key_pickups_baseline":a["original_native_key_pickups_evaluator_only"],
            "key_pickups_novelty":b["original_native_key_pickups_evaluator_only"],
            "unlocks_baseline":a["original_native_door_unlocks_evaluator_only"],
            "unlocks_novelty":b["original_native_door_unlocks_evaluator_only"]
        })
    b_success=sum(r["baseline_causal_exposure"] for r in comparisons)
    n_success=sum(r["novelty_causal_exposure"] for r in comparisons)
    objectives={
        "new_public_novelty_policy_reaches_authentic_training_causal_intervention":
            n_success>=1,
        "paired_native_exposure_improves_over_unchanged_original_random_policy":
            n_success>b_success,
        "same_native_per_environment_max_action_budget":True,
        "both_policies_uninterrupted_original_source_and_public_only":True
    }
    print("MR26_ORIGINAL_NATIVE_PUBLIC_EXPLORATION="+json.dumps({
        "original_independent_farama_commit":SOURCE_COMMIT,
        "previously_unconsumed_development_seeds":p["fresh_development_seeds"],
        "paired_original_door_key_causal_acquisition":comparisons,
        "native_DoorKey_exposure_successes":{
            "unchanged_baseline":b_success,"public_novelty":n_success
        },
        "original_source_native_episode_receipts":source_results,
        "predeclared_go_no_go_conditions":objectives,
        "all_original_native_steps_executed":sum(
            r["actual_original_native_steps"] for r in source_results),
        "maximum_original_native_action_steps":len(source_results)*256,
        "original_45_trainable_model_coefficients_unchanged":True,
        "models_trained_during_exploration":0,
        "separate_untrained_MR15_sensor_sidecar_bytes":32,
        "candidate_untrained_policy_cache_max_entries":CAP,
        "public_policy_uses_complete_original_7x7x3_frame_with_no_semantic_decoder":True,
        "private_source_door_and_key_only_evaluator_after_native_step":True,
        "no_evaluator_pose_staging_or_solver_routes":True,
        "original_public_policy_RNG_restart_state_not_qualified":True,
        "single_shared_process_overall_cpu_ns":time.process_time_ns()-start,
        "all_in_isolated_controller_and_model_process_cpu_peak_rss":"NOT_QUALIFIED",
        "upstream_source_licensing":"UNRESOLVED",
        "g29_exact_source_atlas_full_regression":"BLOCKED",
        "protected_scientific_first_use":False,
        "causal_memory_predictive_value":"NOT_TESTED",
        "scientific_admission":"NO_GO"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr26.audit_native ORIGINAL_FARAMA_CHECKOUT")
    main(sys.argv[1])
