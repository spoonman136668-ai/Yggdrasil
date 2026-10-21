"""MR24: original native *uninterrupted* public action-history custody, DEV.

This diagnostic is a precondition for genuine learned causal memory.
The source-independent exploratory actor is NOT a trained Yggdrasil learner:
it accepts only the actual public observation and an explicit seeded RNG.
No evaluator staged locations, hidden source grid, goal or object IDs can
select an action. The source evaluator separately checks key and door events
AFTER the original native env.step; it sends NONE to the actor or model.
Absence of a source-native causal history is a real negative for this fixed
development protocol, not proof such histories are impossible to learn.
"""
from hashlib import sha256
import json
from pathlib import Path
import random
import subprocess
import sys

from research.mr15.public_view_delta import (
    PublicViewLocalDelta,SOURCE_COMMIT,public_raw_view
)

CONTRACT=Path(__file__).with_name("frozen_protocol.json")
ACTION_BUCKET=(2,)*46+(0,)*18+(1,)*18+(3,)*7+(5,)*8+(4,)*3
assert len(ACTION_BUCKET)==100


def verify(root):
    cfg=json.loads(CONTRACT.read_text(encoding="utf8"))
    if (cfg["schema"]!="yggdrasil.mr24.natural-native-history-custody.dev.v1"
        or cfg["farama_source_sha"]!=SOURCE_COMMIT
        or cfg["development_seeds"]!=[173,179,181,191]
        or cfg["max_native_steps_per_environment"]!=256
        or cfg["no_model_trained"] is not True):
        raise ValueError("MR24_FROZEN_ORIGINAL_PROTOCOL_DRIFT")
    root=Path(root).resolve()
    sha=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                                text=True).strip()
    status=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],
                                   text=True).strip()
    if sha!=SOURCE_COMMIT or status:
        raise ValueError("MR24_ORIGINAL_FARAMA_SOURCE_CUSTODY_FAILED")
    return cfg,root


def public_only_action(observation,rng):
    # The only observation API allowed into the actor: original public image.
    # Deliberately no symbolic parsing, native agent pose, env object or oracle.
    if type(observation) is not dict or "image" not in observation:
        raise ValueError("MR24_ORIGINAL_PUBLIC_INPUT_REQUIRED")
    raw=public_raw_view(observation["image"])
    if len(raw)!=24:
        raise ValueError("MR24_ORIGINAL_PUBLIC_VIEW_INVALID")
    return ACTION_BUCKET[rng.randrange(100)]


def source_evaluator_private_door(env):
    # Diagnostic evaluator ONLY, returns raw object only to audit context.
    from minigrid.core.world_object import Door
    matches=[o for x in range(env.width) for y in range(env.height)
             for o in [env.grid.get(x,y)] if isinstance(o,Door)]
    if len(matches)!=1:
        raise ValueError("MR24_SOURCE_NATIVE_DOOR_CUSTODY_INVALID")
    return matches[0]


def native_episode(factory,family,seed,max_steps):
    from minigrid.core.world_object import Key
    env=factory()
    rng=random.Random(1000003*seed + 337)
    try:
        public,_=env.reset(seed=seed)
        # Expose ONLY action and original public observation to actor.
        sensor=PublicViewLocalDelta()
        sensor.prime(public["image"])
        door=source_evaluator_private_door(env) if family=="DoorKeyEnv(size=8)" else None
        if door is not None and (not door.is_locked or door.is_open):
            raise ValueError("MR24_NATIVE_DOOR_INITIAL_STATE_NOT_LOCKED")
        entry=[]
        prev_key=False
        prev_open=False
        for index in range(max_steps):
            prior_raw=public_raw_view(public["image"])
            action=public_only_action(public,rng)
            # EVALUATOR snapshot, not exposed to actor, before original step.
            before_open=bool(door.is_open) if door is not None else False
            next_obs,_reward,terminated,truncated,_info=env.step(action)
            frame=sensor.observe_after_native_step(action,next_obs["image"])
            next_raw=public_raw_view(next_obs["image"])
            if (frame["observed_action"]!=action or
                frame["source_commit"]!=SOURCE_COMMIT or
                sensor.steps!=index+1 or
                frame["observed_next_local_bits"]!=[
                  int(tuple(prior_raw[3*i:3*i+3])!=
                      tuple(next_raw[3*i:3*i+3])) for i in range(8)]):
                raise ValueError("MR24_UNAUTHENTIC_NATIVE_PUBLIC_CONSEQUENCE")
            # Original internal inventory/door truth ONLY the evaluator.
            holding_key=isinstance(env.carrying,Key)
            door_open=bool(door.is_open) if door is not None else False
            event={
                "step":index,"action":action,
                "sampled_delta_bits":list(frame["observed_next_local_bits"]),
                "before_public_sha256":sha256(public["image"].tobytes()).hexdigest(),
                "after_public_sha256":sha256(next_obs["image"].tobytes()).hexdigest(),
                "evaluator_only_key_acquired":bool(holding_key and not prev_key),
                "evaluator_only_door_unlocked":bool(
                    door is not None and door_open and not before_open),
                "evaluator_only_door_open":door_open,
                "original_native_terminated":bool(terminated),
                "original_native_truncated":bool(truncated),
            }
            entry.append(event)
            if index==11:
                checkpoint=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(checkpoint)
                if sensor.snapshot()!=checkpoint:
                    raise ValueError("MR24_PUBLIC_SENSOR_COLD_RESTART_FAILED")
            public=next_obs
            prev_key=holding_key
            prev_open=door_open
            if terminated or truncated:
                break
        if len(entry)==0 or len(entry)>max_steps:
            raise ValueError("MR24_ORIGINAL_NATIVE_EPISODE_BUDGET_INVALID")
        pickups=[r["step"] for r in entry if r["evaluator_only_key_acquired"]]
        unlocks=[r["step"] for r in entry if r["evaluator_only_door_unlocked"]]
        visible_pickup=[r["step"] for r in entry
                        if r["evaluator_only_key_acquired"] and
                        sum(r["sampled_delta_bits"])>0]
        visible_unlock=[r["step"] for r in entry
                        if r["evaluator_only_door_unlocked"] and
                        sum(r["sampled_delta_bits"])>0]
        return {
            "native_family":family,"seed":seed,
            "actual_original_native_steps":len(entry),
            "native_source_causal_pickup_events":len(pickups),
            "native_source_causal_door_unlock_events":len(unlocks),
            "pickup_observable_within_existing_MR15_samples":
                len(visible_pickup),
            "unlock_observable_within_existing_MR15_samples":
                len(visible_unlock),
            "full_public_frame_changed_events":sum(
                x["before_public_sha256"]!=x["after_public_sha256"]
                for x in entry),
            "native_experience_informative_for_hidden_door":
                bool(visible_pickup and visible_unlock
                     and min(visible_pickup)<max(visible_unlock)),
            "native_source_event_stream_sha256":sha256(
                json.dumps([
                    [e["step"],e["action"],e["sampled_delta_bits"],
                     e["before_public_sha256"],e["after_public_sha256"]]
                    for e in entry],
                    separators=(",",":")).encode()).hexdigest(),
            "original_env_terminated_early":entry[-1]["original_native_terminated"],
            "original_env_truncated":entry[-1]["original_native_truncated"],
        }
    finally:
        env.close()


def main(source):
    cfg,root=verify(source)
    sys.path.insert(0,str(root))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factories=[
        ("DoorKeyEnv(size=8)",lambda:DoorKeyEnv(size=8,render_mode=None)),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None)),
    ]
    receipts=[
        native_episode(factory,family,seed,cfg["max_native_steps_per_environment"])
        for family,factory in factories
        for seed in cfg["development_seeds"]
    ]
    qualifying=[
        r for r in receipts if r["native_experience_informative_for_hidden_door"]]
    print("MR24_ORIGINAL_UNINTERRUPTED_PUBLIC_CAUSAL_HISTORY="+
          json.dumps({
        "original_source_commit":SOURCE_COMMIT,
        "frozen_protocol_sha256":sha256(CONTRACT.read_bytes()).hexdigest(),
        "original_native_episode_receipts":receipts,
        "total_original_native_executed_steps":sum(
            r["actual_original_native_steps"] for r in receipts),
        "native_uninterrupted_histories_with_visible_pickup_then_unlock":
            len(qualifying),
        "MR24_natural_public_experience_ready_for_memory_training":
            bool(qualifying),
        "no_evaluator_poses_or_oracle_actions_used":True,
        "source_hidden_audit_never_given_to_policy_or_learner":True,
        "fixed_source_independent_exploration_policy_not_a_learned_agent":True,
        "no_native_memory_models_trained":True,
        "zero_novel_trainable_coefficients":True,
        "original_MR15_24bytes_plus_delta_byte_retained":True,
        "protected_scientific_first_use":False,
        "all_in_model_cpu_peak_RSS":"NOT_QUALIFIED",
        "g29_original_source_atlas":"NOT_QUALIFIED",
        "original_upstream_license_discrepancy":"UNRESOLVED",
        "scientific_admission":"NO_GO",
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr24.natural_history ORIGINAL")
    main(sys.argv[1])
