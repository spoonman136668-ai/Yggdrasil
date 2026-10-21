"""MR15 original MiniGrid public-view/8-local-cell contract qualification.

Uses the upstream 7x7 partially observed image only. Original env's
privileged grid, key/door/goal identities, mission, rewards and directions
are NOT read or provided to the adapter or any learner/control. A frozen
unoptimized action script exercises source-original step consequences.

No learner is trained. This is native environment interface engineering,
not independent novel task first-use or cellular functional recovery.
"""
import hashlib
import json
import pathlib
import subprocess
import sys

from public_view_delta import PublicViewLocalDelta, SOURCE_COMMIT, POSITIONS

ACTION_SCRIPT = (0,2,1,2,0,2,1,2,5,3,2,1,2,0,2,5)


def require_source(upstream):
    root=pathlib.Path(upstream).resolve()
    head=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    if head!=SOURCE_COMMIT:
        raise ValueError("MR15_PINNED_UPSTREAM_DRIFT")
    if subprocess.check_output(
        ["git","-C",str(root),"status","--porcelain"],text=True).strip():
        raise ValueError("MR15_UPSTREAM_NOT_CLEAN")
    return root


def probe(environment, name):
    try:
        observation,_=environment.reset(seed=11)
        # The learner-facing boundary explicitly extracts image alone.
        sensor=PublicViewLocalDelta()
        assert sensor.prime(observation["image"])==(0,)*8
        seen=[]
        restart_verified=False
        for i,action in enumerate(ACTION_SCRIPT):
            before_bits=sensor.bits
            # Prediction inputs are frozen BEFORE the original native step;
            # future observation and outcome cannot influence the prior.
            hypothetical_pre_outcome=(before_bits,action)
            next_obs,reward,terminated,truncated,info=environment.step(action)
            event=sensor.observe_after_native_step(action,next_obs["image"])
            assert (tuple(event["prior_local_bits"]),event["observed_action"])==hypothetical_pre_outcome
            assert event["additional_trainable_parameters"]==0
            assert event["privileged_world_fields_consumed"]==0
            assert event["raw_temporal_sidecar_bytes"]==24
            assert event["last_binary_observation_bits"]==8
            assert all(bit in (0,1) for bit in event["observed_next_local_bits"])
            seen.append(event)
            # Exact midstream cold restore needs no environment object, raw
            # original tile classifications or any target label.
            if i==7:
                saved=sensor.snapshot()
                cloned=PublicViewLocalDelta.restore(saved)
                assert cloned.snapshot()==saved
                sensor=cloned
                restart_verified=True
            if terminated or truncated:
                break
        changes=sum(sum(x["observed_next_local_bits"]) for x in seen)
        assert len(seen)>=8
        assert changes>0
        frozen=sensor.snapshot()
        try:
            sensor.observe_after_native_step(7, next_obs["image"])
        except ValueError:
            pass
        else:
            raise AssertionError("MR15_INVALID_ACTION_ACCEPTED")
        assert sensor.snapshot()==frozen
        assert restart_verified
        return {
            "external_native_environment":name,
            "source_commit":SOURCE_COMMIT,
            "native_steps":len(seen),
            "actual_observed_local_tile_changes":changes,
            "observable_spatial_cells":len(POSITIONS),
            "public_observation_shape":[7,7,3],
            "binary_model_inputs_per_step":8,
            "pre_outcome_action_disclosed":True,
            "public_view_bytes_retained_in_untrained_sidecar":24,
            "previous_observation_bits_retained":8,
            "added_trainable_parameters":0,
            "explicit_object_identity_in_model_features":False,
            "world_grid_accessed":False,
            "mission_reward_direction_to_candidate":False,
            "label_or_oracle_leak":False,
            "source_license_discrepancy_unresolved":True,
            "cold_sensor_state_restart":restart_verified,
            "full_snapshot_bytes":len(frozen.encode()),
            "protected_scientific_first_use":False,
            "learner_trained":False,
        }
    finally:
        environment.close()


def fail_closed_validation():
    import numpy as np
    a=PublicViewLocalDelta()
    base=np.zeros((7,7,3),dtype=np.uint8)
    a.prime(base)
    assert a.observe_after_native_step(0,base)["observed_next_local_bits"]==[0]*8
    before=a.snapshot()
    for bad in (
        {"image":base},
        np.zeros((6,7,3),dtype=np.uint8),
        np.zeros((7,7,3),dtype=np.int32),
        np.zeros((7,7),dtype=np.uint8)
    ):
        try:
            a.observe_after_native_step(0,bad)
        except ValueError:
            pass
        else:
            raise AssertionError("MR15_BAD_OR_PRIVILEGED_IMAGE_ADMITTED")
        assert a.snapshot()==before
    restored=PublicViewLocalDelta.restore(before)
    assert restored.snapshot()==before
    corrupt=json.loads(before)
    corrupt["source_commit"]="0"*40
    try:
        PublicViewLocalDelta.restore(json.dumps(corrupt,sort_keys=True,separators=(",",":")))
    except ValueError:
        pass
    else:
        raise AssertionError("MR15_SOURCE_IDENTITY_TAMPER_ACCEPTED")


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: probe.py <original-upstream-checkout>")
    root=require_source(sys.argv[1])
    sys.path.insert(0,str(root))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    fail_closed_validation()
    doorkey=probe(DoorKeyEnv(size=5,render_mode=None),"Original DoorKeyEnv(size=5)")
    empty=probe(EmptyEnv(size=8,render_mode=None),"Original EmptyEnv(size=8)")
    print("MR15_PUBLIC_NATIVE_LOCAL_OBSERVATION="+json.dumps({
        "observations":[doorkey,empty],
        "exact_source_commit":SOURCE_COMMIT,
        "no_object_role_or_teacher_labels":True,
        "runtime_is_original_minigrid_step":True,
        "two_distinct_original_native_environment_classes":True,
        "model_memory": "original 45 coefficients UNCHANGED; no model trained",
        "nonlearned_sensor_sidecar_accounted_bytes":32,
        "complete_process_cpu_peak_rss":"NOT_QUALIFIED",
        "prelesion_role_necessity":"NOT_TESTED",
        "native_cognitive_transfer":"NOT_TESTED",
        "source_licensing":"UNRESOLVED",
        "protected_scientific_first_use":False,
        "scientific_admission":"BLOCKED",
    },sort_keys=True))
