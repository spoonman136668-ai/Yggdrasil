"""MR23B: source-native intervention that tests whether useful memory is needed.

Original MiniGrid DoorKeyEnv(8) is unchanged. The EVALUATOR stages agent pose
for three genuine original actions (PICKUP, TOGGLE, DROP), versus equal-count
no-op DROP controls. End states must differ ONLY in the original door's state,
not inventory or a visible key. The evaluator then enumerates empty positions
and directions under the frozen protocol and tests the SAME next ORIGINAL
action from identical publicly observed images.

The explicit pose staging is an evaluator privilege and NOT an uninterrupted
natural policy. No learner uses native grid, door/key identity, world coords,
carried inventory, or labels. No learning or independent first-use occurs.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from research.mr15.public_view_delta import (
    PublicViewLocalDelta, SOURCE_COMMIT, public_raw_view
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "research" / "mr23b" / "frozen_protocol.json"
FACING = {(1,0):0,(0,1):1,(-1,0):2,(0,-1):3}
PROBES = (0,1,2)


def exact_source(folder):
    folder=Path(folder).resolve()
    head=subprocess.check_output(
        ["git","-C",str(folder),"rev-parse","HEAD"],text=True
    ).strip()
    dirt=subprocess.check_output(
        ["git","-C",str(folder),"status","--porcelain"],text=True
    ).strip()
    if head!=SOURCE_COMMIT or dirt:
        raise ValueError("MR23B_UNAUTHENTIC_ORIGINAL_SOURCE")
    return folder


def native_public_sha(image):
    if image.shape!=(7,7,3) or image.dtype!=np.uint8:
        raise ValueError("MR23B_INVALID_NATIVE_PUBLIC_IMAGE")
    return hashlib.sha256(image.tobytes()).hexdigest()


def original_objects(env):
    # DIAGNOSTIC EVALUATOR ONLY. Object types are never learner inputs.
    from minigrid.core.world_object import Door,Key
    found_door=[]
    found_key=[]
    for x in range(env.width):
        for y in range(env.height):
            obj=env.grid.get(x,y)
            if isinstance(obj,Door):
                found_door.append((x,y,obj))
            elif isinstance(obj,Key):
                found_key.append((x,y,obj))
    if len(found_door)!=1 or len(found_key)!=1:
        raise ValueError("MR23B_ORIGINAL_OBJECT_CUSTODY_CHANGED")
    return found_door[0],found_key[0]


def staging_neighbor(env, target):
    tx,ty=target
    # Frozen nonadaptive lexicographic choice among ORIGINAL empty tiles.
    options=[]
    for delta,(dx,dy) in enumerate(((1,0),(0,1),(-1,0),(0,-1))):
        x,y=tx-dx,ty-dy
        if 0<=x<env.width and 0<=y<env.height and env.grid.get(x,y) is None:
            options.append((x,y,FACING[(dx,dy)]))
    if not options:
        raise ValueError("MR23B_ORIGINAL_INTERVENTION_UNREACHABLE")
    return min(options)


def stage_and_step(a,b,pose,active_action):
    x,y,heading=pose
    for env in (a,b):
        env.agent_pos=(x,y)
        env.agent_dir=heading
    oa,_,end_a,cut_a,_=a.step(active_action)
    ob,_,end_b,cut_b,_=b.step(int(b.actions.drop))
    if end_a or cut_a or end_b or cut_b:
        raise ValueError("MR23B_NATIVE_ORIGINAL_EPISODE_ENDED")
    return oa,ob


def prepare_pair(seed):
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.core.world_object import Key
    a=DoorKeyEnv(size=8,render_mode=None)
    b=DoorKeyEnv(size=8,render_mode=None)
    try:
        a.reset(seed=seed)
        b.reset(seed=seed)
        if not np.array_equal(a.grid.encode(),b.grid.encode()):
            raise ValueError("MR23B_INITIAL_NATIVE_WORLD_MISMATCH")
        (dx,dy,door),(kx,ky,key)=original_objects(a)
        if not door.is_locked or door.is_open or key.color!=door.color:
            raise ValueError("MR23B_ORIGINAL_DOOR_NOT_LOCKED")
        key_pose=staging_neighbor(a,(kx,ky))
        door_pose=staging_neighbor(a,(dx,dy))

        # A: three actual original MiniGrid source actions.
        # B: original same-count no-op drops at identical staged poses.
        stage_and_step(a,b,key_pose,int(a.actions.pickup))
        if not isinstance(a.carrying,Key) or b.carrying is not None:
            raise ValueError("MR23B_NATIVE_PICKUP_DID_NOT_HAPPEN")
        stage_and_step(a,b,door_pose,int(a.actions.toggle))
        if door.is_locked or not door.is_open:
            raise ValueError("MR23B_ORIGINAL_TOGGLE_DID_NOT_OPEN")
        stage_and_step(a,b,key_pose,int(a.actions.drop))
        if a.carrying is not None or b.carrying is not None:
            raise ValueError("MR23B_NATIVE_CARRYING_WOULD_REVEAL_BRANCH")

        # Exactly one world tile is different. The previously picked key
        # has been placed back at its original native cell by source DROP.
        ga,gb=a.grid.encode(),b.grid.encode()
        changed=np.any(ga!=gb,axis=2)
        different=[(int(x),int(y))
                   for x,y in zip(*np.where(changed))]
        if different!=[(dx,dy)]:
            raise ValueError("MR23B_NONDOOR_NATIVE_WORLD_DRIFT")
        if a.step_count!=b.step_count or a.step_count!=3:
            raise ValueError("MR23B_NATIVE_STEP_COUNT_UNMATCHED")
        if a.carrying is not None or b.carrying is not None:
            raise ValueError("MR23B_ORIGINAL_NATIVE_CARRY_STATE_DRIFT")
        if native_public_sha(a.gen_obs()["image"])=="":
            raise ValueError("MR23B_IMPOSSIBLE_SOURCE_HASH")
        return a,b,{
            "native_original_setup_steps_each":3,
            "source_world_encoded_tiles_different":len(different),
            "source_difference_is_original_door_only":True,
            "source_key_restored_to_original_cell":True,
            "source_carrying_empty_in_both":True,
            "native_original_door_state_open_vs_locked":True,
            "agent_pose_staged_by_diagnostic_evaluator":True,
        }
    except Exception:
        a.close();b.close()
        raise


def witness(a,b):
    source_pairs=0
    equal_public=0
    future_different=0
    future_8bit_different=0
    best=None
    first=None
    for x in range(1,a.width-1):
        for y in range(1,a.height-1):
            if a.grid.get(x,y) is not None or b.grid.get(x,y) is not None:
                continue
            for direction in range(4):
                # Only diagnostic evaluator controls same original pose.
                for action in PROBES:
                    source_pairs+=1
                    aa=copy.deepcopy(a)
                    bb=copy.deepcopy(b)
                    try:
                        aa.agent_pos=bb.agent_pos=(x,y)
                        aa.agent_dir=bb.agent_dir=direction
                        pa,pb=aa.gen_obs(),bb.gen_obs()
                        if not np.array_equal(pa["image"],pb["image"]):
                            continue
                        equal_public+=1
                        sa,sb=PublicViewLocalDelta(),PublicViewLocalDelta()
                        # Same full source-public image, same MR15 24 raw
                        # bytes, same eight former delta bits.
                        assert sa.prime(pa["image"])==sb.prime(pb["image"])
                        prior_a=public_raw_view(pa["image"])
                        prior_b=public_raw_view(pb["image"])
                        if prior_a!=prior_b or sa.bits!=(0,)*8 or sb.bits!=(0,)*8:
                            raise ValueError("MR23B_PREACTION_PUBLIC_INPUT_NOT_EQUAL")
                        na,_,end_a,cut_a,_=aa.step(action)
                        nb,_,end_b,cut_b,_=bb.step(action)
                        if bool(end_a)!=bool(end_b) or bool(cut_a)!=bool(cut_b):
                            # Terminal source difference is itself a useful
                            # action consequence, but no reward label enters.
                            pass
                        va=sa.observe_after_native_step(action,na["image"])
                        vb=sb.observe_after_native_step(action,nb["image"])
                        next_img_different=not np.array_equal(
                            na["image"],nb["image"]
                        )
                        target_diff=sum(
                            u!=v for u,v in zip(
                                va["observed_next_local_bits"],
                                vb["observed_next_local_bits"]
                            )
                        )
                        future_different+=int(next_img_different)
                        future_8bit_different+=int(target_diff>0)
                        if next_img_different:
                            sample={
                                "source_original_agent_staging_pose":[x,y,direction],
                                "native_next_action":action,
                                "identical_complete_public_image_sha256":
                                    native_public_sha(pa["image"]),
                                "original_source_next_image_sha256_pair":[
                                    native_public_sha(na["image"]),
                                    native_public_sha(nb["image"]),
                                ],
                                "original_source_eightbit_next_targets":[
                                    va["observed_next_local_bits"],
                                    vb["observed_next_local_bits"],
                                ],
                                "target_bits_with_causal_difference":target_diff,
                                "source_next_public_image_differs":True,
                                "identical_model_visible_input":True,
                                "source_world_door_state_is_evaluator_only":True,
                                "theoretical_balanced_pair_Brier_floor":
                                    target_diff/32.0,
                            }
                            if first is None:
                                first=sample
                            if target_diff>0 and best is None:
                                best=sample
                    finally:
                        aa.close();bb.close()
    return {
        "bounded_evaluator_native_probe_pairs":source_pairs,
        "identical_preaction_full_public_image_pairs":equal_public,
        "equal_present_observation_different_future_image_pairs":
            future_different,
        "equal_present_observation_different_future_8bit_pairs":
            future_8bit_different,
        "first_identical_image_future_difference":first,
        "first_original_eight_bit_target_difference":best,
        "any_MR15_action_consequence_requires_hidden_memory_in_pair":
            best is not None,
        "positive_scope":"evaluator-staged source-native one-step contrast; not natural agent history",
    }


def main(folder):
    protocol=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (protocol["schema"]!=
        "yggdrasil.mr23b.original-hidden-door-memory-necessity.dev.v1" or
        protocol["farama_commit"]!=SOURCE_COMMIT or
        protocol["frozen_seed"]!=11 or
        protocol["max_candidate_source_pairs"]!=432):
        raise ValueError("MR23B_FROZEN_ORIGINAL_PROTOCOL_DRIFT")
    original=exact_source(folder)
    sys.path.insert(0,str(original))
    a,b,setup=prepare_pair(protocol["frozen_seed"])
    try:
        result=witness(a,b)
    finally:
        a.close();b.close()
    if result["bounded_evaluator_native_probe_pairs"]>432:
        raise ValueError("MR23B_UNBOUNDED_NATIVE_SEARCH")
    print("MR23B_SOURCE_NATIVE_OCCLUDED_MEMORY_NECESSITY="+json.dumps({
        "source_git_commit":SOURCE_COMMIT,
        "frozen_contract_source_sha256":hashlib.sha256(
            CONTRACT.read_bytes()).hexdigest(),
        "real_original_source_intervention_setup":setup,
        "source_witness":result,
        "no_world_private_state_or_object_labels_to_model":True,
        "same_24_original_public_bytes_and_prior_eight_bits_with_same_action":True,
        "original_45_trainable_coefficients_unmodified":True,
        "new_model_trainable_parameters":0,
        "number_of_models_trained":0,
        "original_MR15_retained_sidecar_bytes":32,
        "protected_scientific_first_use":False,
        "complete_cpu_peak_rss_native_broker_costs":"NOT_QUALIFIED",
        "g29_exact_source_full_integration":"BLOCKED",
        "upstream_source_license_discrepancy":"UNRESOLVED",
        "real_world_neural_cognition_demonstrated":False,
        "scientific_admission":"NO_GO",
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr23b.hidden_door ORIGINAL_FARAMA")
    main(sys.argv[1])
