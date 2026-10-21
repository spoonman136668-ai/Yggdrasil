"""MR32A worker: isolated original-native source+actor+auditor process.

Runs one exact unchanged MR31 public-only policy across a FROZEN native
development cohort. Entire native environment, actor, same-cost evaluator,
and episode serialization execute in this process; Python process CPU and
OS process peak resident memory include all of these, not just model code.
No other policy or model is instantiated in this source process.

The read-only retrospective world/grid labels are encoded into a diagnostic
trace AFTER the original source event. They are never returned to actor.
The trace is intentionally external evaluator custody, not cognitive state.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import pickle
import sys
import time

import psutil

from research.mr27.natural_memory import source_guard
from research.mr31.original_acquisition import episode

PROTOCOL=Path(__file__).with_name("frozen_protocol.json")
SCHEMA="yggdrasil.mr32a.isolated-native-acquisition-cost.development.v1"


def peak_os_resident_bytes():
    if sys.platform=="win32":
        info=psutil.Process().memory_info()
        peak=getattr(info,"peak_wset",0)
        if peak:
            return int(peak)
    elif sys.platform.startswith("linux"):
        import resource
        # Linux rusage maximum RSS is reported in KiB.
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1024
    # Unknown platform cannot justify an all-in peak memory claim.
    raise ValueError("MR32A_OS_PEAK_RESIDENT_MEMORY_NOT_SUPPORTED")


def load_contract():
    p=json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if (p["schema"]!=SCHEMA or
        p["parent_exact_commit"]!="bcb40f3ed66ba1e1ed8eb0bd3b1842094140dc1e" or
        p["original_farama_source_commit"]!="7f5853792ea7f04f75614661006d87fcf949f26d" or
        p["development_door_seeds"]!=[677,683,691,701,709,719,727,733] or
        p["development_empty_seeds"]!=[739,743,751,757] or
        p["stream_ids"]!=[0,1,2,3] or
        p["max_original_native_actions_per_episode"]!=256 or
        p["unchanged_public_only_actors"]!=["novelty","contrast"] or
        p["no_new_learner_or_parameter_changes"] is not True):
        raise ValueError("MR32A_UNAUTHORIZED_NATIVE_DEVELOPMENT_PROTOCOL")
    return p


def main(upstream_path,mode,output):
    p=load_contract()
    if mode not in p["unchanged_public_only_actors"]:
        raise ValueError("MR32A_UNAUTHORIZED_SOURCE_ACTOR")
    source=source_guard(upstream_path)
    sys.path.insert(0,str(source))
    from minigrid.envs.doorkey import DoorKeyEnv
    from minigrid.envs.empty import EmptyEnv
    factories=[
        ("DoorKeyEnv(size=8)",lambda:DoorKeyEnv(size=8,render_mode=None),
         p["development_door_seeds"]),
        ("EmptyEnv(size=8)",lambda:EmptyEnv(size=8,render_mode=None),
         p["development_empty_seeds"])
    ]
    start_cpu=time.process_time_ns()
    rows=[]
    receipts=[]
    for family,make,seeds in factories:
        for seed in seeds:
            for stream in p["stream_ids"]:
                events,receipt=episode(make,family,seed,stream,mode,
                    p["max_original_native_actions_per_episode"])
                rows.extend(events)
                receipts.append(receipt)
    # Native source and actor have completed; include the full explicit
    # offline evaluator diagnostic trace serialization in worker CPU/RSS.
    output=Path(output)
    if output.exists():
        raise ValueError("MR32A_UNAUTHORIZED_EXISTING_NATIVE_TRACE")
    with gzip.open(output,"wb",compresslevel=1) as fh:
        pickle.dump((rows,receipts),fh,protocol=4)
    digest=hashlib.sha256(json.dumps([
        [r["mode"],r["family"],r["seed"],r["stream"],
         r["original_native_actions"],
         r["original_native_action_history_sha256"]]
        for r in receipts
    ],sort_keys=True,separators=(",",":")).encode()).hexdigest()
    result={
        "mode":mode,
        "native_original_episode_count":len(receipts),
        "native_original_action_count":len(rows),
        "same_structural_actor_max_payload_bytes":
            receipts[0]["actor_budget_receipt"][
                "max_fixed_payload_excluding_container_and_rng_bytes"],
        "max_measured_actor_container_estimate_bytes":max(
            r["actor_budget_receipt"][
                "measured_python_container_estimate_bytes"]
            for r in receipts),
        "max_actual_actor_payload_bytes":max(
            r["actor_budget_receipt"][
                "actual_payload_excluding_container_and_rng_bytes"]
            for r in receipts),
        "rng_state_pickle_bytes_max":max(
            r["actor_budget_receipt"]["rng_getstate_pickle_bytes"]
            for r in receipts),
        "native_source_history_sha256":digest,
        "isolated_original_env_actor_and_evaluator_process_cpu_ns":
            time.process_time_ns()-start_cpu,
        "os_isolated_worker_peak_resident_bytes":
            peak_os_resident_bytes(),
        "offline_evaluator_trace_wire_bytes":output.stat().st_size,
        "all_original_source_private_labels_diagnostic_only":True,
        "learner_or_trainable_weights_instantiated":False
    }
    if len(receipts)!=48 or sum(
        r["original_native_actions"] for r in receipts)!=len(rows):
        raise ValueError("MR32A_SOURCE_NATIVE_EPISODE_COUNT_DRIFT")
    print("MR32A_ISOLATED_WORKER="+json.dumps(result,sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=4:
        raise SystemExit("Usage: python -m research.mr32a.isolated_worker SOURCE MODE OUTPUT")
    main(sys.argv[1],sys.argv[2],sys.argv[3])
