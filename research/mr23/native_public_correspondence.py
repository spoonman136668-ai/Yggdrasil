"""MR23: native public sensory correspondence identifiability, NOT a learner.

The original MR15 eight camera-relative sample triples are compared at two
consecutive original Farama MiniGrid steps. Triples are opaque public bytes:
no object decoding, pose, source world, reward, image labels or model oracle.
Exact byte equality is only an OBSERVATIONAL CANDIDATE, never proof of a
persistent real-world object, identity, or physical correspondence.

Frozen development-only train/control and eval seeds are supplied by the
Git-pinned protocol (committed before this source file). No model weights
or saved state are updated. Report ambiguous, absent and unique candidate
matches, with a matched-source nonadjacent-frame control; retain negatives.
"""
from collections import Counter,defaultdict
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

from research.mr15.public_view_delta import (
    PublicViewLocalDelta, SOURCE_COMMIT, public_raw_view
)

CONTRACT=Path(__file__).with_name("frozen_protocol.json")
EXPECTED="yggdrasil.mr23.public-sensory-correspondence-dev.v1"


def verified(original):
    p=json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (p["schema"]!=EXPECTED or p["original_minigrid_commit"]!=SOURCE_COMMIT
        or p["development_train_seeds"]!=[109,113]
        or p["development_eval_seeds"]!=[127,131]
        or len(p["action_scripts"]["train"])!=24
        or len(p["action_scripts"]["evaluation"])!=24
        or p["resource_limits"]["new_learner_state_bytes"]!=0):
        raise ValueError("MR23_FROZEN_DEV_PROTOCOL_NOT_AUTHENTIC")
    root=Path(original).resolve()
    head=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                                text=True).strip()
    dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],
                                 text=True).strip()
    if head!=SOURCE_COMMIT or dirty:
        raise ValueError("MR23_ORIGINAL_FARAMA_SOURCE_NOT_AUTHENTIC")
    return p,root


def tiles(raw):
    if (type(raw) not in (list,tuple) or len(raw)!=24
        or any(type(x) is not int or not 0<=x<=255 for x in raw)):
        raise ValueError("MR23_UNEXPECTED_MR15_PUBLIC_BYTES")
    return tuple(tuple(raw[i*3:i*3+3]) for i in range(8))


def candidate_counts(previous,current):
    """Number of byte-identical source candidates for each current slot."""
    a=tiles(previous)
    b=tiles(current)
    return tuple(sum(x==y for x in a) for y in b)


def aggregate(rows,decoys):
    if len(rows)!=len(decoys):
        raise ValueError("MR23_DECOY_ORIGINAL_SOURCE_MISMATCH")
    result={}
    for section,filter_fn in [
        ("all",lambda r:True),
        ("camera_turns",lambda r:r["action"] in (0,1)),
        ("other_actions",lambda r:r["action"] not in (0,1)),
        ("observed_any_public_change",lambda r:r["actual_changed_bits"]>0),
    ]:
        pool=[(r,d) for r,d in zip(rows,decoys) if filter_fn(r)]
        real=Counter()
        false=Counter()
        same_slot=0
        changed=0
        changed_slots_total=0
        for row,decoy in pool:
            actual=candidate_counts(row["before"],row["after"])
            dummy=candidate_counts(decoy,row["after"])
            for n in actual:
                real["none" if n==0 else ("unique" if n==1 else "ambiguous")]+=1
            for n in dummy:
                false["none" if n==0 else ("unique" if n==1 else "ambiguous")]+=1
            old,new=tiles(row["before"]),tiles(row["after"])
            same_slot+=sum(a==b for a,b in zip(old,new))
            changed+=int(row["before"]!=row["after"])
            changed_slots_total+=row["actual_changed_bits"]
        slots=8*len(pool)
        result[section]={
            "native_original_events":len(pool),
            "native_original_sensor_positions_compared":slots,
            "true_adjacent_unique_candidate_slots":real["unique"],
            "true_adjacent_ambiguous_candidate_slots":real["ambiguous"],
            "true_adjacent_absent_candidate_slots":real["none"],
            "nonadjacent_original_frame_unique_candidate_slots":
                false["unique"],
            "nonadjacent_original_frame_ambiguous_candidate_slots":
                false["ambiguous"],
            "nonadjacent_original_frame_absent_candidate_slots":
                false["none"],
            "same_camera_slot_byte_equal_pairs":same_slot,
            "events_with_any_sampled_view_change":changed,
            "all_observed_local_tile_change_bits":changed_slots_total,
            "true_unique_fraction":
                real["unique"]/slots if slots else None,
            "nonadjacent_control_unique_fraction":
                false["unique"]/slots if slots else None,
        }
        if slots and sum(real.values())!=slots:
            raise ValueError("MR23_CORRESPONDENCE_ACCOUNTING_DRIFT")
        if slots and sum(false.values())!=slots:
            raise ValueError("MR23_DECOY_ACCOUNTING_DRIFT")
    return result


def episode(constructor,family,seed,actions):
    env=constructor()
    try:
        original,_=env.reset(seed=seed)
        sensor=PublicViewLocalDelta()
        sensor.prime(original["image"])
        rows=[]
        for index,action in enumerate(actions):
            # All fields are PUBLIC original observations.
            before=public_raw_view(original["image"])
            old_snapshot=sensor.snapshot()
            next_obs,_reward,terminated,truncated,_info=env.step(action)
            after=public_raw_view(next_obs["image"])
            event=sensor.observe_after_native_step(action,next_obs["image"])
            if (event["observed_action"]!=action or
                event["source_commit"]!=SOURCE_COMMIT or
                event["observed_next_local_bits"]!=[
                   int(x!=y) for x,y in zip(tiles(before),tiles(after))]):
                raise ValueError("MR23_ORIGINAL_NATIVE_SOURCE_EVENT_INVALID")
            if index==9:
                snap=sensor.snapshot()
                sensor=PublicViewLocalDelta.restore(snap)
                if sensor.snapshot()!=snap:
                    raise ValueError("MR23_MR15_SENSOR_COLD_RESTART_FAILURE")
            if old_snapshot==sensor.snapshot():
                raise ValueError("MR23_NO_NATIVE_SENSOR_STEP_RECORDED")
            rows.append({
                "family":family,"seed":seed,"step":index,
                "action":action,"before":before,"after":after,
                "actual_changed_bits":sum(event["observed_next_local_bits"]),
            })
            original=next_obs
            if terminated or truncated:
                break
        return rows
    finally:
        env.close()


def matched_decoys(eval_rows,train_rows):
    """Only earlier separate original source TRAIN traces can be controls."""
    buckets=defaultdict(list)
    for r in train_rows:
        buckets[(r["family"],r["action"])].append(r["before"])
    decoys=[]
    for r in eval_rows:
        candidates=buckets.get((r["family"],r["action"]))
        if not candidates:
            raise ValueError("MR23_NO_FROZEN_SAME_SOURCE_DECOY_AVAILABLE")
        # Deterministic unrelated original frame, independent of eval result.
        decoys.append(candidates[(r["step"]+r["seed"])%len(candidates)])
    return decoys


def main(original_path):
    p,source=verified(original_path)
    sys.path.insert(0,str(source))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    constructors=[
        ("DoorKeyEnv(size=5)",lambda:DoorKeyEnv(size=5,render_mode=None)),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None))
    ]
    train=[]
    evaluation=[]
    for family,maker in constructors:
        for seed in p["development_train_seeds"]:
            train+=episode(maker,family,seed,p["action_scripts"]["train"])
        for seed in p["development_eval_seeds"]:
            evaluation+=episode(maker,family,seed,p["action_scripts"]["evaluation"])
    if not train or not evaluation:
        raise ValueError("MR23_ORIGINAL_NATIVE_SOURCE_NO_EVENTS")
    decoys=matched_decoys(evaluation,train)
    diagnostics={
        "all":aggregate(evaluation,decoys),
        "per_source":{
            family:aggregate(
                [r for r in evaluation if r["family"]==family],
                [d for r,d in zip(evaluation,decoys) if r["family"]==family])
            for family,_ in constructors},
    }
    turns=diagnostics["all"]["camera_turns"]
    # This is purely a decision over observed byte candidate quality.
    # It does NOT decide success of any learned representation.
    sufficient_for_an_exact_public_byte_correspondence_trial=(
        turns["native_original_events"]>0 and
        turns["true_adjacent_unique_candidate_slots"]>
        turns["nonadjacent_original_frame_unique_candidate_slots"] and
        turns["true_adjacent_unique_candidate_slots"]>0)
    # Only records opaque public visual bytes, no object identities.
    historical=json.dumps([
        [r["family"],r["seed"],r["step"],r["action"],
         sha256(bytes(r["before"])).hexdigest(),
         sha256(bytes(r["after"])).hexdigest()]
        for r in evaluation],sort_keys=True,separators=(",",":")).encode()
    print("MR23_ORIGINAL_NATIVE_PUBLIC_CORRESPONDENCE="+json.dumps({
        "source_commit":SOURCE_COMMIT,
        "frozen_protocol_sha256":sha256(CONTRACT.read_bytes()).hexdigest(),
        "original_native_training_development_events":len(train),
        "original_native_evaluation_development_events":len(evaluation),
        "original_public_source_history_sha256":
            sha256(historical).hexdigest(),
        "matched_dev_source_results":diagnostics,
        "byte_correspondence_candidate_trial_feasible_on_frozen_dev":
            sufficient_for_an_exact_public_byte_correspondence_trial,
        "exact_public_byte_candidate_is_not_a_world_object_identity":True,
        "many_to_one_camera_aliasing_prohibited_as_learned_role":True,
        "conventional_control":"nonadjacent original native frame same environment and action",
        "model_trained":False,
        "original_native_45_coefficients_changed":False,
        "extra_learner_state_bytes":0,
        "existing_MR15_sidecar_bytes":32,
        "privileged_original_world_state_consumed":False,
        "new_independent_scientific_source_consumed":False,
        "complete_cpu_peak_rss_wire":"NOT_QUALIFIED",
        "g29_atlas":"NOT_QUALIFIED",
        "upstream_license_discrepancy":"UNRESOLVED",
        "scientific_admission":"NO_GO",
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python -m research.mr23.native_public_correspondence UPSTREAM")
    main(sys.argv[1])
