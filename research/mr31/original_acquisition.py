"""MR31: independently frozen ORIGINAL MiniGrid causal-experience acquisition.

Two native action selectors share exactly the same structurally budgeted
policy-memory allocation and fixed source-native reset/action cap. Baseline
is *action-identical* to MR26 for an identical observation/action history.
Candidate is a different source-independent principle: maximize empirical
observable TRANSITION AMBIGUITY, not simple global image novelty.

All original source worlds/pose/inventory are read ONLY by the evaluator,
AFTER the public-only policy has already selected the original action, and
NEVER fed back into either explorer. Original next 8 sampled image-change
bits are used only to test naturally arising same-full-current-public+prior
MR15 bits+action pairs with divergent real outcomes; labels are NEVER used
to modify action probabilities. No causal learner is trained or selected.
"""
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

import psutil

from research.mr15.public_view_delta import (
    SOURCE_COMMIT,PublicViewLocalDelta,public_raw_view
)
from research.mr27.natural_memory import source_guard
from research.mr31.matched_public_actor import (
    EqualCapacityPublicActor,baseline_equivalence_selftest
)

CONFIG=Path(__file__).with_name("frozen_protocol.json")
SCHEMA="yggdrasil.mr31.original-public-acquisition-contrast.dev.v1"
FAMILIES=("DoorKeyEnv(size=8)","EmptyEnv(size=8)")
MODES=("novelty","contrast")


def contract(folder):
    cfg=json.loads(CONFIG.read_text(encoding="utf-8"))
    if (cfg["schema"]!=SCHEMA or
        cfg["exact_parent_sha"]!="7f2b66165dd4dc27dcd801a2acb168c6363b15a1" or
        cfg["original_source_sha"]!=SOURCE_COMMIT or
        cfg["door_development_seeds"]!=[
            601,607,613,617,619,631,641,643,647,653,659,661] or
        cfg["empty_development_seeds"]!=[601,607,613,617] or
        cfg["public_action_stream_ids"]!=[0,1,2,3] or
        cfg["max_original_native_actions_per_episode"]!=256 or
        cfg["source_actor_action_base"]!=[18,18,46,7,3,8] or
        cfg["protected_science_first_use"] is not False or
        cfg["no_original_45_coefficients_changed"] is not True):
        raise ValueError("MR31_FROZEN_NATIVE_SOURCE_PROTOCOL_DRIFT")
    upstream=source_guard(folder)
    baseline_equivalence_selftest()
    return cfg,upstream


def evaluator_only_state(env,door):
    carrier=env.carrying
    return {
        "pose":tuple(int(x) for x in env.agent_pos),
        "facing":int(env.agent_dir),
        "inventory":None if carrier is None else (
            type(carrier).__name__,getattr(carrier,"color",None)),
        "world":env.grid.encode().tobytes(),
        "door":None if door is None else (
            bool(door.is_locked),bool(door.is_open))
    }


def episode(make,family,seed,stream,mode,limit):
    from minigrid.core.world_object import Door,Key
    actor=EqualCapacityPublicActor(seed,mode,stream)
    env=make()
    cpu_start=time.process_time_ns()
    process=psutil.Process()
    rss_peak=process.memory_info().rss
    try:
        public,_=env.reset(seed=seed)
        sensor=PublicViewLocalDelta()
        sensor.prime(public["image"])
        original_doors=[
            obj for x in range(env.width) for y in range(env.height)
            for obj in [env.grid.get(x,y)] if isinstance(obj,Door)]
        if (family=="DoorKeyEnv(size=8)" and len(original_doors)!=1 or
            family=="EmptyEnv(size=8)" and original_doors):
            raise ValueError("MR31_ORIGINAL_NATIVE_WORLD_SOURCE_SHAPE")
        door=original_doors[0] if original_doors else None
        rows=[]
        native_digest=sha256()
        key_before=False
        visible_pickup=False
        real_unlocks=0
        unlock_after_public_pickup=0
        real_pickups=0
        observed_public_changes=0
        for t in range(limit):
            img=public["image"]
            before=img.tobytes()
            prior=tuple(sensor.bits)
            sample=public_raw_view(img)
            # Source actor is evaluated FIRST and never receives env.
            action=actor.choose(img)
            # Evaluator-only state is AFTER action-choice and cannot be
            # passed to actor.observe or included in actor memory.
            hidden=evaluator_only_state(env,door)
            preopen=bool(door.is_open) if door else False
            nxt,_reward,ended,truncated,_info=env.step(action)
            event=sensor.observe_after_native_step(action,nxt["image"])
            newer=public_raw_view(nxt["image"])
            target=tuple(event["observed_next_local_bits"])
            expected=tuple(int(sample[3*i:3*i+3]!=newer[3*i:3*i+3])
                           for i in range(8))
            if (event["source_commit"]!=SOURCE_COMMIT or
                event["observed_action"]!=action or
                tuple(event["prior_local_bits"])!=prior or
                target!=expected or sensor.steps!=t+1):
                raise ValueError("MR31_ORIGINAL_SOURCE_EVENT_AUTHENTICATION_FAILED")
            actor.observe(action,nxt["image"])
            nxt_bytes=nxt["image"].tobytes()
            observed_public_changes+=int(before!=nxt_bytes)
            key_now=isinstance(env.carrying,Key)
            pickup_now=key_now and not key_before
            unlock_now=bool(door and door.is_open and not preopen)
            real_pickups+=int(pickup_now)
            real_unlocks+=int(unlock_now)
            if pickup_now and sum(target)>0:
                visible_pickup=True
            unlock_after_public_pickup+=int(
                unlock_now and visible_pickup and sum(target)>0)
            digest_before=native_digest.hexdigest()
            native_digest.update(bytes([action]))
            native_digest.update(before)
            native_digest.update(nxt_bytes)
            rows.append({
                "mode":mode,"family":family,"seed":seed,
                "stream":stream,"step":t,"public":before,
                "priorbits":prior,"action":action,"targets":target,
                "history_before":digest_before,
                "pose":hidden["pose"],"facing":hidden["facing"],
                "inventory":hidden["inventory"],"world":hidden["world"],
                "door_truth":hidden["door"]
            })
            if t==11:
                snap=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(snap)
                if snap!=sensor.snapshot():
                    raise ValueError("MR31_ORIGINAL_NATIVE_PUBLIC_RESTART_DRIFT")
            key_before=key_now
            rss_peak=max(rss_peak,process.memory_info().rss)
            public=nxt
            if ended or truncated:
                break
        if not rows:
            raise ValueError("MR31_NO_ORIGINAL_NATIVE_SOURCE_ACTIONS")
        cap=actor.capacity_receipt()
        return rows,{
            "mode":mode,"family":family,"seed":seed,"stream":stream,
            "original_native_actions":len(rows),
            "original_native_action_history_sha256":native_digest.hexdigest(),
            "source_public_image_changed_events":observed_public_changes,
            "original_world_key_pickups_evaluator_only":real_pickups,
            "original_world_door_unlocks_evaluator_only":real_unlocks,
            "visible_pickup_then_visible_unlock":bool(unlock_after_public_pickup),
            "native_actor_public_frames_discovered":actor.total_new,
            "actor_budget_receipt":cap,
            "shared_source_process_CPU_ns_diagnostic_only":
                time.process_time_ns()-cpu_start,
            "shared_source_process_sampled_RSS_peak_bytes_not_isolated":
                rss_peak,
        }
    finally:
        env.close()


def paired_prefix(rows,receipts):
    byid=defaultdict(dict)
    for rec in receipts:
        byid[(rec["family"],rec["seed"],rec["stream"])][rec["mode"]]=rec
    paired_limits={}
    for key,policies in byid.items():
        if set(policies)!=set(MODES):
            raise ValueError("MR31_MISSING_MATCHED_ORIGINAL_SOURCE_STREAM")
        paired_limits[key]=min(
            policies[x]["original_native_actions"] for x in MODES)
    clipped=[r for r in rows if r["step"]<paired_limits[(
        r["family"],r["seed"],r["stream"])]]
    return clipped,paired_limits


def original_strict_aliases(rows):
    groups=defaultdict(list)
    for row in rows:
        groups[(row["mode"],row["family"],row["seed"],
                row["public"],row["priorbits"],row["action"])].append(row)
    result={mode:{
        "equal_full_public_current_and_action_contexts_cross_stream":0,
        "exact_entire_current_learner_input_cross_history_pairs_checked":0,
        "same_pose_and_inventory_different_world_pairs":0,
        "strict_different_world_and_next_eightbit_pairs":0,
        "strict_original_reset_seed_clusters":[],
        "original_door_truth_different_strict_pairs":0,
        "truncated_equivalence_groups":0,
        "examples":[]
    } for mode in MODES}
    seeds={mode:set() for mode in MODES}
    for members in groups.values():
        if len({x["stream"] for x in members})<2:
            continue
        mode=members[0]["mode"]
        info=result[mode]
        info["equal_full_public_current_and_action_contexts_cross_stream"]+=1
        checked=0
        for i,a in enumerate(members):
            for b in members[i+1:]:
                if a["stream"]==b["stream"] or (
                    a["history_before"]==b["history_before"]):
                    continue
                if checked>=20000:
                    info["truncated_equivalence_groups"]+=1
                    break
                checked+=1
                info[
                    "exact_entire_current_learner_input_cross_history_pairs_checked"
                ]+=1
                same_real_pose=(a["pose"]==b["pose"] and
                                a["facing"]==b["facing"] and
                                a["inventory"]==b["inventory"])
                if not same_real_pose or a["world"]==b["world"]:
                    continue
                info["same_pose_and_inventory_different_world_pairs"]+=1
                if a["targets"]==b["targets"]:
                    continue
                info["strict_different_world_and_next_eightbit_pairs"]+=1
                seeds[mode].add(a["seed"])
                info["original_door_truth_different_strict_pairs"]+=int(
                    a["door_truth"]!=b["door_truth"])
                if len(info["examples"])<6:
                    info["examples"].append({
                        "family":a["family"],"native_reset_seed":a["seed"],
                        "independent_original_source_streams":[
                            a["stream"],b["stream"]],
                        "source_original_steps":[a["step"],b["step"]],
                        "exact_same_current_public_image_sha256":
                            sha256(a["public"]).hexdigest(),
                        "same_MR15_prior_delta_bits":list(a["priorbits"]),
                        "same_original_source_action":a["action"],
                        "different_source_next_MR15_bits":[
                            list(a["targets"]),list(b["targets"])],
                        "evaluator_only_matched_pose_inventory":True,
                        "evaluator_only_original_world_grid_differs":True,
                        "source_only_public_actor":True,
                    })
            if checked>=20000:
                break
    for mode in MODES:
        result[mode]["strict_original_reset_seed_clusters"]=sorted(seeds[mode])
    return result


def main(source):
    cfg,upstream=contract(source)
    sys.path.insert(0,str(upstream))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factories=[
        ("DoorKeyEnv(size=8)",lambda:DoorKeyEnv(size=8,render_mode=None),
         cfg["door_development_seeds"]),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None),
         cfg["empty_development_seeds"])
    ]
    rows=[]
    episodes=[]
    for family,factory,seeds in factories:
        for seed in seeds:
            for stream in cfg["public_action_stream_ids"]:
                # Alternate launch order across independent source streams.
                # No hindsight outcome can select policy or source seed.
                modes=MODES if (seed+stream)%2==0 else MODES[::-1]
                for mode in modes:
                    observed,rec=episode(
                        factory,family,seed,stream,mode,
                        cfg["max_original_native_actions_per_episode"])
                    rows.extend(observed)
                    episodes.append(rec)
    if len(episodes)!=128:
        raise ValueError("MR31_FROZEN_NATIVE_EPISODE_COVERAGE")
    if any(
        x["actor_budget_receipt"][
            "max_fixed_payload_excluding_container_and_rng_bytes"
        ]!=episodes[0]["actor_budget_receipt"][
            "max_fixed_payload_excluding_container_and_rng_bytes"
        ] for x in episodes):
        raise ValueError("MR31_ACTOR_CAPACITY_NOT_MATCHED")
    prefix,limits=paired_prefix(rows,episodes)
    primary=original_strict_aliases(prefix)
    if any(r["truncated_equivalence_groups"] for r in primary.values()):
        raise ValueError("MR31_PRECOMMITTED_ALIAS_AUDIT_TRUNCATED")
    by_mode={}
    for mode in MODES:
        rr=[r for r in episodes if r["mode"]==mode]
        filtered=[x for x in prefix if x["mode"]==mode]
        by_mode[mode]={
            "original_native_episodes":len(rr),
            "true_uninterrupted_original_native_actions":
                sum(x["original_native_actions"] for x in rr),
            "matched_prefix_original_native_actions":
                len(filtered),
            "distinct_original_source_reset_seeds":len(set(
                (x["family"],x["seed"]) for x in rr)),
            "genuine_native_world_key_pickups_evaluator_only":sum(
                x["original_world_key_pickups_evaluator_only"] for x in rr),
            "genuine_original_door_unlocks_evaluator_only":sum(
                x["original_world_door_unlocks_evaluator_only"] for x in rr),
            "original_uninterrupted_visible_pickup_then_unlock_episodes":sum(
                x["visible_pickup_then_visible_unlock"] for x in rr),
            "source_public_changed_observation_events":sum(
                x["source_public_image_changed_events"] for x in rr),
            "native_source_new_public_frames_discovered":sum(
                x["native_actor_public_frames_discovered"] for x in rr),
            "source_policy_CPU_ns_not_isolated_process":sum(
                x["shared_source_process_CPU_ns_diagnostic_only"] for x in rr),
            "max_sampled_shared_process_RSS_bytes_not_isolated":max(
                x["shared_source_process_sampled_RSS_peak_bytes_not_isolated"]
                for x in rr),
        }
    independent_seed_clusters={mode:len(primary[mode][
        "strict_original_reset_seed_clusters"]) for mode in MODES}
    ready={
        "new_ambiguity_policy_has_more_independent_original_seed_clusters":
            independent_seed_clusters["contrast"]>
            independent_seed_clusters["novelty"],
        "new_policy_does_not_regress_natural_visible_pickup_to_unlock":
            by_mode["contrast"][
                "original_uninterrupted_visible_pickup_then_unlock_episodes"]>=
            by_mode["novelty"][
                "original_uninterrupted_visible_pickup_then_unlock_episodes"],
        "new_policy_produces_strict_natural_full_input_world_outcome_pairs":
            primary["contrast"][
                "strict_different_world_and_next_eightbit_pairs"]>0,
        "maximum_fixed_actor_state_bytes_exactly_matched":
            all(x["actor_budget_receipt"][
                "max_fixed_payload_excluding_container_and_rng_bytes"]==
                episodes[0]["actor_budget_receipt"][
                "max_fixed_payload_excluding_container_and_rng_bytes"]
                for x in episodes),
        "actual_memory_and_full_end_to_end_cpu_rss_wire_parity_qualified":False,
        "independent_original_unfamiliar_task_family_transfer":False,
        "protected_scientific_admission":False
    }
    digest=sha256(json.dumps([
        [row["mode"],row["family"],row["seed"],row["stream"],
         row["original_native_actions"],
         row["original_native_action_history_sha256"]]
        for row in episodes
    ],sort_keys=True,separators=(",",":")).encode()).hexdigest()
    print("MR31_ORIGINAL_NATIVE_EQUAL_BUDGET_ACQUISITION="+json.dumps({
        "source_original_commit":SOURCE_COMMIT,
        "frozen_protocol_sha256":sha256(CONFIG.read_bytes()).hexdigest(),
        "source_original_native_episode_sha256":digest,
        "source_native_total_original_executed_episodes":len(episodes),
        "source_native_matched_prefix_per_policy_steps":sum(limits.values()),
        "structural_policy_max_fifo_entries":128,
        "structural_policy_same_bytes_and_rng_state_type":True,
        "baseline_exact_native_MR26_actor_formula_selftest_passed":True,
        "source_public_only_policy_outcomes":by_mode,
        "original_strict_full_current_input_causal_alias_acquisition":primary,
        "independent_original_seed_clusters_with_natural_strict_alias":
            independent_seed_clusters,
        "preregistered_admission_conditions":ready,
        "fixed_original_Ygg_trainable_coefficient_budget":45,
        "trained_new_causal_prediction_model":False,
        "new_learner_state_bytes":0,
        "original_MR15_retained_public_sample_and_delta_bytes":32,
        "native_original_env_world_pose_inventory_diagnostic_only":True,
        "native_source_actor_received_privileged_evaluator_input":False,
        "source_evaluation_labels_never_update_actor_policy":True,
        "original_native_source_never_pose_staged":True,
        "original_source_only_existing_development_families":True,
        "complete_all_in_source_actor_CPU_peak_RSS_wire":"NOT_QUALIFIED",
        "policy_storage_actual_allocated_process_containers_not_equal":"NOT_QUALIFIED",
        "semantic_atlas_source_bound_G29":"BLOCKED",
        "Farama_upstream_license_inconsistency":"UNRESOLVED",
        "protected_scientific_first_use":False,
        "scientific_admission":"NO_GO"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr31.original_acquisition ORIGINAL_FARAMA")
    main(sys.argv[1])
