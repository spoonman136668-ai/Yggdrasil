"""MR21: matched-source-state, divergent MR15 camera-history features.

Two ORIGINAL native Farama MiniGrid processes with same seed, same THREE
step-count budget, same underlying grid/pose, same current COMPLETE public
image and same next native action. One has two original DROP no-ops; the other
has one original camera turn and its inverse. Every predictor-relevant feature
is derived solely from the original public sensor.

The evaluator ONLY may inspect original world grid, pose, carrying and native
step count to prove state equality. NO learner is instantiated or trained,
and no privileged source fields enter any model/controller.
"""
import hashlib
import json
import pathlib
import subprocess
import sys

import numpy as np

from research.mr15.public_view_delta import PublicViewLocalDelta,SOURCE_COMMIT
from research.mr19b.native_camera_audit import hash_grid

ROOT=pathlib.Path(__file__).resolve().parents[2]
PLAN=ROOT/"research"/"mr21"/"frozen_reversible_identity.json"


def checked_source(path):
    root=pathlib.Path(path).resolve()
    sha=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                                text=True).strip()
    dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],
                                  text=True).strip()
    if sha!=SOURCE_COMMIT or dirty:
        raise ValueError("MR21_AUTHENTIC_SOURCE_CUSTODY_FAILED")
    return root


def inspect_original(env):
    # SOURCE-PROVENANCE EVALUATOR ONLY; this tuple must NEVER enter a model.
    carry=env.carrying
    return {
        "grid_sha256":hash_grid(env),
        "original_agent_pos":tuple(int(v) for v in env.agent_pos),
        "original_agent_dir":int(env.agent_dir),
        "original_step_count":int(env.step_count),
        "native_carrying_sha256":None if carry is None else hashlib.sha256(
            bytes(carry.encode())).hexdigest(),
    }


def original_public_byte_sha(image):
    if getattr(image,"shape",None)!=(7,7,3) or image.dtype!=np.uint8:
        raise ValueError("MR21_ORIGINAL_PUBLIC_VIEW_SHAPE_DRIFT")
    return hashlib.sha256(image.tobytes()).hexdigest()


def experiment(factory,name,seed,turns,probe):
    a=factory()
    b=factory()
    try:
        aa,_=a.reset(seed=seed)
        bb,_=b.reset(seed=seed)
        if not np.array_equal(aa["image"],bb["image"]):
            raise ValueError("MR21_SOURCE_INIT_DRIFT")
        a_sensor=PublicViewLocalDelta()
        b_sensor=PublicViewLocalDelta()
        a_sensor.prime(aa["image"])
        b_sensor.prime(bb["image"])
        native_initial=inspect_original(a)
        if inspect_original(b)!=native_initial:
            raise ValueError("MR21_INITIAL_NATIVE_WORLD_NOT_IDENTICAL")

        # Native control advances episode time identically without moving
        # camera or world: agent starts carrying nothing in these sources.
        noop=int(a.actions.drop)
        if native_initial["native_carrying_sha256"] is not None:
            raise ValueError("MR21_NATIVE_NOOP_NOT_VALID")
        for x in (noop,noop):
            aa,_,done,stopped,_=a.step(x)
            a_sensor.observe_after_native_step(x,aa["image"])
            if done or stopped:
                raise ValueError("MR21_CONTROL_ENDED_PREMATURELY")
        for x in turns:
            bb,_,done,stopped,_=b.step(x)
            b_sensor.observe_after_native_step(x,bb["image"])
            if done or stopped:
                raise ValueError("MR21_TURN_EPISODE_ENDED_PREMATURELY")

        # The original complete native state except deliberately unexposed
        # RNG internals must be identical, *including original step count*.
        ia=inspect_original(a)
        ib=inspect_original(b)
        if ia!=ib or not np.array_equal(aa["image"],bb["image"]):
            raise ValueError("MR21_REVERSIBLE_NATIVE_WORLD_NOT_RESTORED")
        if ia["original_step_count"]!=native_initial["original_step_count"]+2:
            raise ValueError("MR21_NATIVE_EPISODE_TIME_NOT_EQUAL")
        if a_sensor.bits != (0,)*8:
            raise ValueError("MR21_NATIVE_NOOP_SOURCE_CHANGED_PUBLIC_VIEW")

        history_diff=sum(x!=y for x,y in zip(a_sensor.bits,b_sensor.bits))
        source_image=original_public_byte_sha(aa["image"])
        if source_image != original_public_byte_sha(bb["image"]):
            raise ValueError("MR21_CANONICAL_ORIGINAL_IMAGE_IDENTITY_DRIFT")
        prior_bits_a=list(a_sensor.bits)
        prior_bits_b=list(b_sensor.bits)

        # EXACTLY same original next action from matched true source state
        # and equal complete public image; measure only actual native events.
        an,_,ad,at,_=a.step(probe)
        bn,_,bd,bt,_=b.step(probe)
        ao=a_sensor.observe_after_native_step(probe,an["image"])
        bo=b_sensor.observe_after_native_step(probe,bn["image"])
        if (not np.array_equal(an["image"],bn["image"]) or
            ao["observed_next_local_bits"]!=bo["observed_next_local_bits"] or
            bool(ad)!=bool(bd) or bool(at)!=bool(bt) or
            inspect_original(a)!=inspect_original(b)):
            raise ValueError("MR21_EQUAL_STATE_IDENTICAL_ACTION_CONSEQUENCE_FAILED")
        return {
            "family":name,"seed":seed,
            "reversible_original_turn_pair":list(turns),
            "identical_original_probe_action":probe,
            "equal_controlled_native_source_state":True,
            "equal_original_native_step_counter":True,
            "equal_complete_public_image_sha256":source_image,
            "different_MR15_8bit_prior_input_slots":history_diff,
            "control_history_MR15_bits":prior_bits_a,
            "camera_history_MR15_bits":prior_bits_b,
            "next_original_public_output_sha256":original_public_byte_sha(an["image"]),
            "same_source_native_next_image_and_MR15_target":True,
            "source_native_next_public_tile_change_bits":
                ao["observed_next_local_bits"],
            "model_training":False,
            "privileged_original_world_truth_to_candidate":False,
        }
    finally:
        a.close()
        b.close()


def main(path):
    p=json.loads(PLAN.read_text(encoding="utf-8"))
    if (p["schema"]!="yggdrasil.mr21.original-reversible-frame-identity.v1" or
        p["original_external_source"]!=SOURCE_COMMIT or
        p["predecessor"]!="0bb2662e5109c95667e680027fab343a4db03fe1" or
        p["learner_and_control_inputs"] !=
          "ONLY_MR15_prior_eight_bits_and_same_preexecution_action; full_public_image_compared_offline_by_evaluator_only"):
        raise ValueError("MR21_FROZEN_PROTOCOL_DRIFT")
    root=checked_source(path)
    sys.path.insert(0,str(root))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factories=[
        ("Original DoorKeyEnv(5)",lambda:DoorKeyEnv(size=5,render_mode=None)),
        ("Original EmptyEnv(8)",lambda:EmptyEnv(size=8,render_mode=None))
    ]
    events=[]
    for name,factory in factories:
        for seed in p["previously_used_MR19_development_seeds"]:
            for pair in p["frozen_turn_inverse_pairs"]:
                for action in p["frozen_identical_probe_actions"]:
                    events.append(experiment(factory,name,seed,pair,action))
    distinct=[e for e in events if e["different_MR15_8bit_prior_input_slots"]>0]
    summary={
        "original_upstream_source_commit":SOURCE_COMMIT,
        "predeclared_development_pair_count":len(events),
        "original_external_native_step_calls":len(events)*6,
        "source_matched_world_image_action_next_consequence_pairs":len(events),
        "pairs_with_different_eightbit_model_inputs":len(distinct),
        "max_history_induced_8bit_input_difference":max(
            x["different_MR15_8bit_prior_input_slots"] for x in events),
        "equal_native_world_same_next_result_different_MR15_histories":
            len(distinct)>0,
        "native_source_grid_pose_direction_stepcount_and_carrying_equal":True,
        "public_image_current_and_next_identical_within_each_pair":True,
        "input_variation_causal_to_camera_history_not_current_world":len(distinct)>0,
        "world_truth_read_only_in_evaluator":True,
        "learned_cell_causality_proven":False,
        "learned_parameter_count_modified":0,
        "original_native_yggdrasil_coefficients":45,
        "MR15_nontrained_sensor_sidecar_bytes":32,
        "protected_scientific_first_use":False,
        "full_cpu_and_peak_rss_qualification":"NOT_QUALIFIED",
        "G29_atlas_final_acceptance":"BLOCKED",
        "original_source_license_conflict":"UNRESOLVED",
        "scientific_admission":"NO_GO",
        "examples":events,
    }
    print("MR21_NATIVE_REVERSIBLE_WORLD_SAME_STATE_DIFFERENT_SENSOR="+
          json.dumps(summary,sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr21.reversible_native ORIGINAL_UPSTREAM")
    main(sys.argv[1])
