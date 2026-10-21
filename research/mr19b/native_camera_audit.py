"""MR19B: original-world camera-motion falsifier of assumed local causal cells.

Original Farama MiniGrid reset/step only. Native grid bytes and agent pose
may be INSPECTED by this diagnostic evaluator to identify whether view-space
changes are due to camera rotation with NO local world-cell transition.
They are NEVER passed to any learning model, control, or action selector.

Reuses the EXACT original MR19 development-only seeds and fixed action
scripts. Not new task first-use, not training or a new model.
"""
import hashlib
import json
import pathlib
import subprocess
import sys

from research.mr15.public_view_delta import (
    PublicViewLocalDelta, SOURCE_COMMIT, public_raw_view, POSITIONS,
)
from research.mr19.probe_original_state import (
    TRAIN_SEEDS, DEV_EVAL_SEEDS, TRAIN_ACTIONS, DEV_EVAL_ACTIONS,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "research" / "mr19b" / "frozen_camera_audit.json"


def exact_original_source(repo):
    repo = pathlib.Path(repo).resolve()
    actual = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()
    dirty = subprocess.check_output(
        ["git", "-C", str(repo), "status", "--porcelain"], text=True
    ).strip()
    if actual != SOURCE_COMMIT or dirty:
        raise ValueError("MR19B_ORIGINAL_SOURCE_SHA_OR_DIRTY_CHECKOUT")
    return repo


def hash_grid(env):
    # DIAGNOSTIC EVALUATOR ONLY: original source-world bytes used solely to
    # exclude world mutation from an apparent change of local camera pixels.
    # No object semantic types, agent position, goal, mission or reward
    # enters a predictor, which is not instantiated by this audit.
    return hashlib.sha256(env.grid.encode().tobytes()).hexdigest()


def run_episode(env, family, phase, seed, actions):
    try:
        obs, _ = env.reset(seed=seed)
        sensor = PublicViewLocalDelta()
        sensor.prime(obs["image"])
        assert sensor.bits == (0,)*8
        action_counts = {}
        turn_observations = []
        turn_verified = 0
        world_mutations_nonturn = 0
        observations = 0

        for step, action in enumerate(actions):
            if type(action) is not int or not 0<=action<=6:
                raise ValueError("MR19B_FROZEN_ACTION_INVALID")
            prior_pose = tuple(map(int, env.agent_pos))
            prior_dir = int(env.agent_dir)
            prior_grid_sha = hash_grid(env)
            pre_raw = public_raw_view(obs["image"])
            frozen_sensor = sensor.snapshot()

            # Single original world process and its genuine source step.
            nxt, _reward, terminated, truncated, _info = env.step(action)
            event = sensor.observe_after_native_step(action,nxt["image"])
            after_pose = tuple(map(int,env.agent_pos))
            after_dir = int(env.agent_dir)
            after_grid_sha = hash_grid(env)
            post_raw = public_raw_view(nxt["image"])
            delta = list(event["observed_next_local_bits"])
            changed = sum(delta)
            changed_from_public_raw = sum(
                pre_raw[i*3:i*3+3]!=post_raw[i*3:i*3+3]
                for i in range(8)
            )

            if changed != changed_from_public_raw or (
                event["source_commit"] != SOURCE_COMMIT or
                event["observed_action"] != action or
                event["privileged_world_fields_consumed"] != 0
            ):
                raise ValueError("MR19B_PUBLIC_SENSOR_OR_SOURCE_DRIFT")
            if sensor.snapshot() == frozen_sensor:
                raise ValueError("MR19B_NATIVE_SOURCE_EVENT_NOT_RECORDED")

            action_kind = (
                "turn" if action in (int(env.actions.left),
                                    int(env.actions.right))
                else "forward" if action == int(env.actions.forward)
                else "other"
            )
            action_counts.setdefault(action_kind,[]).append(changed)
            if action_kind == "turn":
                # True native camera rotation: source world grid is
                # bit-for-bit unchanged, position unchanged, facing changed.
                if (prior_grid_sha!=after_grid_sha or
                    prior_pose!=after_pose or
                    after_dir == prior_dir):
                    raise ValueError("MR19B_NATIVE_TURN_WORLD_IDENTITY_DRIFT")
                turn_verified += 1
                turn_observations.append({
                    "step":step,
                    "action":action,
                    "changed_local_slots":changed,
                    "changed_mask":delta,
                    "world_grid_unchanged":True,
                    "agent_world_position_unchanged":True,
                    "camera_heading_changed":True,
                    # No original world objects, private state or view bytes
                    # are published. These are custody hashes only.
                    "pre_public_sample_sha256":hashlib.sha256(
                        bytes(pre_raw)).hexdigest(),
                    "post_public_sample_sha256":hashlib.sha256(
                        bytes(post_raw)).hexdigest(),
                })
            elif prior_grid_sha != after_grid_sha:
                world_mutations_nonturn += 1

            observations += 1
            obs = nxt
            if step == 9:
                snap=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(snap)
                if sensor.snapshot()!=snap:
                    raise ValueError("MR19B_NATIVE_SENSOR_COLD_RESTART_DRIFT")
            if terminated or truncated:
                break
        return {
            "family":family,"phase":phase,"seed":seed,
            "native_step_count":observations,
            "verified_world_static_turn_actions":turn_verified,
            "original_world_mutations_on_other_actions":world_mutations_nonturn,
            "turn_actions_with_at_least_one_view_slot_changed":sum(
                x["changed_local_slots"]>=1 for x in turn_observations),
            "turn_actions_with_at_least_two_view_slots_changed":sum(
                x["changed_local_slots"]>=2 for x in turn_observations),
            "max_slots_changed_by_one_turn":max(
                (x["changed_local_slots"] for x in turn_observations),default=0),
            "action_change_counts":{
                k:{"steps":len(v),"sum_changed_slots":sum(v)}
                for k,v in action_counts.items()
            },
            "turn_provenance_events":turn_observations,
        }
    finally:
        env.close()


def main(upstream):
    protocol=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if (protocol["schema"]!="yggdrasil.mr19b.original-camera-causal-confound.v1" or
        protocol["original_farama_commit"]!=SOURCE_COMMIT or
        not protocol["protected_scientific_first_use"] is False):
        raise ValueError("MR19B_FROZEN_PROTOCOL_DRIFT")
    source=exact_original_source(upstream)
    sys.path.insert(0,str(source))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    constructors=(
        ("Original DoorKeyEnv(5)",lambda:DoorKeyEnv(size=5,render_mode=None)),
        ("Original EmptyEnv(8)",lambda:EmptyEnv(size=8,render_mode=None))
    )
    reports=[]
    for name,ctor in constructors:
        for phase,seeds,actions in (
            ("prior_mr19_training",TRAIN_SEEDS,TRAIN_ACTIONS),
            ("prior_mr19_dev_evaluation",DEV_EVAL_SEEDS,DEV_EVAL_ACTIONS),
        ):
            for seed in seeds:
                reports.append(run_episode(ctor(),name,phase,seed,actions))
    total_turns=sum(r["verified_world_static_turn_actions"] for r in reports)
    changed_turns=sum(r["turn_actions_with_at_least_one_view_slot_changed"]
                      for r in reports)
    coupled_turns=sum(r["turn_actions_with_at_least_two_view_slots_changed"]
                      for r in reports)
    if total_turns==0:
        raise ValueError("MR19B_FROZEN_ORIGINAL_SOURCE_HAS_NO_CAMERA_TEST")

    print("MR19B_NATIVE_CAMERA_MOTION_CONFOUND="+json.dumps({
        "original_source_commit":SOURCE_COMMIT,
        "existing_mr19_development_episodes":len(reports),
        "existing_mr19_source_native_steps":sum(r["native_step_count"]
                                                for r in reports),
        "original_camera_turns_without_world_mutation":total_turns,
        "camera_turns_that_changed_public_observation_slots":changed_turns,
        "camera_turns_changing_multiple_public_slots":coupled_turns,
        "max_simultaneously_changed_public_slots_on_one_turn":max(
            r["max_slots_changed_by_one_turn"] for r in reports),
        "original_mr15_observer_relative_readout_slots":list(map(list,POSITIONS)),
        "native_public_image_only_used_by_observer":True,
        "privileged_original_world_grid_and_pose_used_by_diagnostic_evaluator_only":True,
        "learner_models_trained":0,
        "candidate_parameters_modified":0,
        "any_true_cell_identity_learned":"NOT_TESTED",
        "state_or_cognition_advantage":"NOT_DEMONSTRATED",
        "original_source_information_not_from_model_pseudo_labels":True,
        "protected_scientific_first_use":False,
        "original_upstream_license_discrepancy":"UNRESOLVED",
        "full_cpu_and_peak_rss_parity":"NOT_QUALIFIED",
        "G29_exact_source_integration":"BLOCKED",
        "scientific_admission":"NO_GO",
        "details":reports
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr19b.native_camera_audit ORIGINAL_UPSTREAM")
    main(sys.argv[1])
