"""MR25B: naturally observed identical-public-input/different-outcome pairs.

All source actions are selected by MR24A's existing public-only exploration
policy, on independently RESET original Farama MiniGrid episodes. No source
pose staging, replayed interventions, hidden-world navigation, reward,
mission, object IDs or oracle to the actor or any learner. There is NO learner.

The auditor (only AFTER sampling each trajectory) may inspect original
source world state to CLASSIFY matched public-action pairs, never to pick
actions or adapt seeds. Exact public image bytes, not lossy hashes, define
the observable match. Histories must be different BEFORE the same action.
Failures are explicitly preserved and do not invite search expansion.

"Same public and same action but different next observation" establishes
finite-development observational aliasing. It alone does NOT prove learned
memory could resolve the ambiguity, physical-object identity or intervention
causation. A stricter matched-pose/different-grid witness is reported
separately; an unlock-specific witness requires different door truth.
"""
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import random
import subprocess
import sys

from research.mr15.public_view_delta import (
    SOURCE_COMMIT, PublicViewLocalDelta, public_raw_view
)
from research.mr24.natural_history import (
    public_only_action, source_evaluator_private_door
)

PROTOCOL = Path(__file__).with_name("frozen_protocol.json")
SCHEMA = "yggdrasil.mr25b.natural-public-twins.dev.v1"
MAX_PER_KEY = 20000


def source_contract(path):
    cfg=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if (cfg["schema"]!=SCHEMA or
        cfg["original_farama_git_commit"]!=SOURCE_COMMIT or
        cfg["development_reset_seeds"]!=[223,227,229,233,239,241] or
        cfg["uninterrupted_action_stream_ids"]!=[0,1,2,3] or
        cfg["max_native_original_steps_per_stream"]!=256 or
        cfg["no_learned_model"] is not True):
        raise ValueError("MR25B_FROZEN_POLICY_OR_SOURCE_CHANGED")
    root=Path(path).resolve()
    head=subprocess.check_output(
        ["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    dirty=subprocess.check_output(
        ["git","-C",str(root),"status","--porcelain"],text=True).strip()
    if head!=SOURCE_COMMIT or dirty:
        raise ValueError("MR25B_INDEPENDENT_ORIGINAL_SOURCE_CUSTODY_INVALID")
    return cfg,root


def readonly_evaluator_truth(env, door):
    # Called strictly for the auditor, NEVER in action policy arguments.
    original_pos=tuple(int(x) for x in env.agent_pos)
    original_dir=int(env.agent_dir)
    carried=env.carrying
    carry=None if carried is None else (
        type(carried).__name__,getattr(carried,"color",None)
    )
    grid=env.grid.encode().tobytes()
    door_truth=None if door is None else (
        bool(door.is_locked),bool(door.is_open)
    )
    return original_pos,original_dir,carry,grid,door_truth


def native_trajectory(factory,family,seed,stream,maxsteps):
    env=factory()
    rng=random.Random(1000003*seed+337+10007*stream)
    try:
        obs,_=env.reset(seed=seed)
        sensor=PublicViewLocalDelta()
        sensor.prime(obs["image"])
        door=(source_evaluator_private_door(env)
              if family=="DoorKeyEnv(size=8)" else None)
        history=sha256()
        rows=[]
        native_pickups=0
        native_unlocks=0
        previously_carried=False
        for t in range(maxsteps):
            pre=obs["image"].tobytes()
            prior_raw=public_raw_view(obs["image"])
            prior_bits=tuple(sensor.bits)
            # Source evaluator can record truth but CANNOT supply it to policy.
            hidden=readonly_evaluator_truth(env,door)
            before_door_open=(bool(door.is_open) if door else False)
            action=public_only_action(obs,rng)
            before_history=history.hexdigest()
            after,reward,done,truncated,info=env.step(action)
            event=sensor.observe_after_native_step(action,after["image"])
            next_bytes=after["image"].tobytes()
            targets=tuple(event["observed_next_local_bits"])
            raw_next=public_raw_view(after["image"])
            if (event["source_commit"]!=SOURCE_COMMIT or
                event["observed_action"]!=action or
                event["prior_local_bits"]!=list(prior_bits) or
                targets!=tuple(
                    int(tuple(prior_raw[3*i:3*i+3])!=
                        tuple(raw_next[3*i:3*i+3]))
                    for i in range(8)) or
                sensor.steps!=t+1):
                raise ValueError("MR25B_NATIVE_SOURCE_EVENT_NOT_AUTHENTIC")
            if t==11:
                snap=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(snap)
                if sensor.snapshot()!=snap:
                    raise ValueError("MR25B_SENSOR_RESTART_DRIFT")
            from minigrid.core.world_object import Key
            key=bool(isinstance(env.carrying,Key))
            native_pickups+=int(key and not previously_carried)
            native_unlocks+=int(bool(door is not None and
                                     door.is_open and not before_door_open))
            # IMPORTANT: next public outcome enters historical digest only
            # AFTER the authentic source action. A current-row comparison
            # never gets to inspect future before action.
            history.update(bytes((action,)))
            history.update(pre)
            history.update(next_bytes)
            rows.append({
                "family":family, "seed":seed,"stream":stream,"step":t,
                "history_before":before_history,
                "before_public":pre, "action":action,
                "next_public":next_bytes,"next_bits":targets,
                "before_pose":hidden[0],"before_dir":hidden[1],
                "before_carried":hidden[2],
                "before_world":hidden[3],
                "before_door":hidden[4]
            })
            obs=after
            previously_carried=key
            if done or truncated:
                break
        if not rows:
            raise ValueError("MR25B_EMPTY_ORIGINAL_NATIVE_SOURCE_STREAM")
        return rows,{
            "family":family,"source_reset_seed":seed,
            "uninterrupted_stream_id":stream,
            "original_source_native_steps":len(rows),
            "original_source_native_key_pickups_evaluator_only":native_pickups,
            "original_source_native_door_unlocks_evaluator_only":native_unlocks,
            "public_native_source_history_sha256":history.hexdigest(),
            "pose_staged":False,
            "actor_received_hidden_world":False
        }
    finally:
        env.close()


def witness(a,b):
    return {
        "original_environment":a["family"],
        "original_reset_seed":a["seed"],
        "identical_full_public_image_sha256":sha256(
            a["before_public"]).hexdigest(),
        "same_source_native_action":a["action"],
        "source_streams":[a["stream"],b["stream"]],
        "source_steps":[a["step"],b["step"]],
        "different_authentic_prior_history_hashes":[
            a["history_before"],b["history_before"]],
        "original_next_MR15_bits":[list(a["next_bits"]),list(b["next_bits"])],
        "next_full_public_hashes":[
            sha256(a["next_public"]).hexdigest(),
            sha256(b["next_public"]).hexdigest()],
        "evaluator_only_same_actual_agent_pose":(
            a["before_pose"]==b["before_pose"] and
            a["before_dir"]==b["before_dir"]),
        "evaluator_only_same_carried_inventory":(
            a["before_carried"]==b["before_carried"]),
        "evaluator_only_different_source_world_grid":(
            a["before_world"]!=b["before_world"]),
        "evaluator_only_different_door_truth":(
            a["before_door"]!=b["before_door"]),
        "no_pose_staging_in_any_source_trajectory":True,
        "no_hidden_truth_sent_to_actor_or_model":True,
    }


def matched_natural_aliases(allrows):
    buckets=defaultdict(list)
    for r in allrows:
        # Exact public bytes are used to decide identity, not SHA collisions.
        buckets[(r["family"],r["seed"],r["before_public"],r["action"])].append(r)
    outcomes={
        "same_public_and_action_cross_stream_buckets":0,
        "buckets_with_different_next_full_public":0,
        "buckets_with_different_next_eight_public_bits":0,
        "buckets_with_same_pose_inventory_different_world_and_next_bits":0,
        "buckets_with_same_pose_inventory_different_door_truth_and_next_bits":0,
        "pairs_audited":0,
        "pair_groups_truncated_at_frozen_limit":0,
        "representatives":{},
    }
    for key,members in buckets.items():
        if len({r["stream"] for r in members})<2:
            continue
        outcomes["same_public_and_action_cross_stream_buckets"]+=1
        flags={
            "different_next_full_public":False,
            "different_next_eight_public_bits":False,
            "strict_hidden_world":False,
            "strict_door":False
        }
        checks=0
        truncated=False
        for i,a in enumerate(members):
            if all(flags.values()):
                break
            for b in members[i+1:]:
                if all(flags.values()):
                    break
                if a["stream"]==b["stream"] or (
                    a["history_before"]==b["history_before"]):
                    continue
                if checks>=MAX_PER_KEY:
                    truncated=True
                    break
                checks+=1
                different_full=(a["next_public"]!=b["next_public"])
                different_bits=(a["next_bits"]!=b["next_bits"])
                same_pose=(a["before_pose"]==b["before_pose"] and
                           a["before_dir"]==b["before_dir"])
                same_carry=(a["before_carried"]==b["before_carried"])
                different_grid=(a["before_world"]!=b["before_world"])
                strict=bool(different_bits and same_pose and same_carry
                            and different_grid)
                door=bool(strict and a["before_door"]!=b["before_door"])
                for condition,present in (
                    ("different_next_full_public",different_full),
                    ("different_next_eight_public_bits",different_bits),
                    ("strict_hidden_world",strict),
                    ("strict_door",door),
                ):
                    if present and not flags[condition]:
                        flags[condition]=True
                        outcomes["representatives"].setdefault(
                            condition,witness(a,b))
            if truncated:
                break
        outcomes["pairs_audited"]+=checks
        outcomes["pair_groups_truncated_at_frozen_limit"]+=int(truncated)
        outcomes["buckets_with_different_next_full_public"]+=int(
            flags["different_next_full_public"])
        outcomes["buckets_with_different_next_eight_public_bits"]+=int(
            flags["different_next_eight_public_bits"])
        outcomes[
            "buckets_with_same_pose_inventory_different_world_and_next_bits"
        ]+=int(flags["strict_hidden_world"])
        outcomes[
            "buckets_with_same_pose_inventory_different_door_truth_and_next_bits"
        ]+=int(flags["strict_door"])
    return outcomes


def main(source):
    cfg,root=source_contract(source)
    sys.path.insert(0,str(root))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    families=(
        ("DoorKeyEnv(size=8)",lambda:DoorKeyEnv(size=8,render_mode=None)),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None))
    )
    rows=[]
    receipts=[]
    for family,ctor in families:
        for seed in cfg["development_reset_seeds"]:
            for stream in cfg["uninterrupted_action_stream_ids"]:
                data,receipt=native_trajectory(
                    ctor,family,seed,stream,
                    cfg["max_native_original_steps_per_stream"])
                rows.extend(data)
                receipts.append(receipt)
    metrics=matched_natural_aliases(rows)
    # Exact history receipts are stable across OS. The larger row lists
    # are transient offline evaluator data, NOT candidate memory capacity.
    evidence=sha256(json.dumps([
        [r["family"],r["seed"],r["stream"],r["step"],r["action"],
         sha256(r["before_public"]).hexdigest(),
         sha256(r["next_public"]).hexdigest(),
         list(r["next_bits"])]
        for r in rows
    ],sort_keys=True,separators=(",",":")).encode()).hexdigest()
    print("MR25B_ORIGINAL_NATURAL_PUBLIC_TWIN_IDENTIFIABILITY="+json.dumps({
        "source_sha":SOURCE_COMMIT,
        "frozen_protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
        "native_episodes":len(receipts),
        "original_native_source_steps":len(rows),
        "source_event_history_sha256":evidence,
        "per_trajectory_source_native_receipts":receipts,
        "exact_preaction_full_public_twin_audit":metrics,
        "natural_public_alias_exists":bool(
            metrics["buckets_with_different_next_eight_public_bits"]),
        "natural_matched_pose_different_grid_and_outcome_exists":bool(
            metrics["buckets_with_same_pose_inventory_different_world_and_next_bits"]),
        "natural_matched_pose_door_specific_contrast_exists":bool(
            metrics["buckets_with_same_pose_inventory_different_door_truth_and_next_bits"]),
        "hidden_native_world_used_only_for_postcollection_classification":True,
        "same_source_seed_and_different_policy_action_histories":True,
        "no_evaluator_pose_or_object_staging":True,
        "source_only_public_image_used_by_actor":True,
        "original_MR15_retained_model_sidecar_bytes":32,
        "model_parameters_unchanged":45,
        "any_predictive_memory_learner_trained":False,
        "same_view_different_future_not_alone_proof_history_is_learnable":True,
        "bounded_finite_development_no_match_not_impossibility":True,
        "full_CPU_peak_RSS_wire":"NOT_QUALIFIED",
        "g29_source_index":"NOT_QUALIFIED",
        "original_license_custody":"UNRESOLVED",
        "scientific_first_use":False,
        "scientific_admission":"NO_GO"
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr25b.natural_twin_audit ORIGINAL")
    main(sys.argv[1])
