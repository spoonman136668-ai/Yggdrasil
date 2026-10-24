"""MR34I3: coordinate-level exact-original TRAIN-only BPTT arithmetic custody.

Observes original pinned model arithmetic. All independent scalar dot computations
are diagnostics ONLY and NEVER affect an original gradient, weight or prediction.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
from pathlib import Path
import platform
import sys
import time

import numpy as np

from research.mr34i1.train_only_numeric import (
    SEEDS, S4C1_SHA, SOURCES, original_git, canon, sha,
    source_episode_inputs, peak_rss
)
from research.mr34i2.trace_first_update import update_exact, raw_params_digest

FIRST="25fe9f6d3ec9fa44b79c814b69efb3e563b8229b"
SCHEMA="mass.mr34i3.training-only-coordinate-diagnosis.v1"
MAX_FIRST_UPDATES=11
EXPECTED_SOURCE_EVENTS={
    "FaramaMiniGridDoorKey8":"566f5e271e01421248bfabeb4326d01408d992276b877a978d96f14daf93797b",
    "DeepMindPycolabApprehend":"9ea175b912b734c7470f93d0b2584eea6c2ce01962aae285a66b4d4834b5346e"
}


def mark(arr):
    """Record float64 bits and all coordinates, with no lossy rounding."""
    a=np.asarray(arr,dtype=np.float64)
    if not np.all(np.isfinite(a)):
        raise ValueError("MR34I3_NONFINITE_NATIVE_ARITHMETIC")
    return {
        "shape":list(a.shape),
        "sha256":sha(np.ascontiguousarray(a).tobytes(order="C")),
        "hex":[float(v).hex() for v in a.flat]
    }


def dot_reference(f, native, s):
    """Read-only explicit high-precision summation, never a training substitute."""
    g=native.g
    roles=native.roles
    ref_read=np.asarray([
        math.fsum(float(f[i,k])*float(g[1,k]) for k in range(7))+float(roles[i,1])
        for i in range(8)
    ],dtype=np.float64)
    ref_u=np.asarray([
        math.fsum([float(f[i,k])*float(g[0,k]) for k in range(7)]+
                  [float(roles[i,0]),float(s[i])*float(ref_read[i])])
        for i in range(8)
    ],dtype=np.float64)
    return mark(ref_read),mark(ref_u)


def instrument_original_bptt(model,episode):
    """Match EXACT original native 45-slot BPTT, retain each intermediate stage."""
    ps,details=model.forward(episode,cache=True)
    if len(details)!=len(episode):
        raise ValueError("MR34I3_NATIVE_FORWARD_CACHE_LENGTH")
    dg=np.zeros_like(model.g)
    dr=np.zeros_like(model.roles)
    future=np.zeros(8,dtype=np.float64)
    by_time=[None]*len(episode)
    for t in range(len(episode)-1,-1,-1):
        f,s,read,p,ns=details[t]
        y=np.asarray(episode[t][2],dtype=np.float64)
        dz=future*(1.-ns*ns)
        du=(p-y)/(len(episode)*8)+dz*model.roles[:,2]*2.*p*(1.-p)
        cdg0=np.sum(du[:,None]*f,axis=0)
        cdg1=np.sum((du*s)[:,None]*f,axis=0)
        cdg2=np.sum(dz[:,None]*f,axis=0)
        dg[0]+=cdg0
        dg[1]+=cdg1
        dg[2]+=cdg2
        dr[:,0]+=du
        dr[:,1]+=du*s
        dr[:,2]+=dz*(2.*p-1.)
        next_future=du*read
        reference_read,reference_u=dot_reference(f,model,s)
        by_time[t]={
            "public_source_features":mark(f),
            "previous_episode_state":mark(s),
            "original_forward_projected_read":mark(read),
            "original_preaction_probability":mark(p),
            "original_next_recurrent_state":mark(ns),
            "original_true_afteraction_public_target":mark(y),
            "read_only_fsum_reference_read":reference_read,
            "read_only_fsum_reference_u":reference_u,
            "original_backprop_dz":mark(dz),
            "original_backprop_du":mark(du),
            "original_backprop_dg0_increment":mark(cdg0),
            "original_backprop_dg1_increment":mark(cdg1),
            "original_backprop_dg2_increment":mark(cdg2),
            "original_backprop_shared_accumulation":mark(dg),
            "original_backprop_local_accumulation":mark(dr),
            "original_backprop_future":mark(next_future)
        }
        future=next_future
    original=model.analytic_bptt(episode)
    independently=(dg,dr)
    if any(not np.array_equal(x,y) or x.tobytes()!=y.tobytes()
           for x,y in zip(original,independently)):
        raise RuntimeError("MR34I3_INVALID_INSTRUMENTED_GRADIENT_REFERENCE")
    return {
        "source_training_public_steps":len(episode),
        "original_forward_final_probabilities":mark(ps),
        "original_total_analytic_gradient_shared":mark(dg),
        "original_total_analytic_gradient_local":mark(dr),
        "chronological_original_forward_reverse_gradient_stages":by_time
    }


def original_source_training_trace(family,root):
    from research.mr34f.prospective_controls import episodes,SOURCES as ORIGINALS
    from research.nci04_s4c1.original_native_predictive_state import (
        TRAIN,EPOCHS,LR,BETAS,EPS,L2,CLIP,protocol)
    from research.nci04_s4c1.native_predictive_quotient import (
        NativePredictiveQuotient45,PARAMETERS)
    if (tuple(TRAIN)!=SEEDS or PARAMETERS!=45 or EPOCHS!=40 or
        ORIGINALS[family][0]!=SOURCES[family]):
        raise ValueError("MR34I3_PINNED_NATIVE_SOURCE_OR_TRAINING_DRIFT")
    protocol()
    source_rows,events=episodes(root,family,SEEDS)
    identity=sha(canon(events).encode())
    if identity!=EXPECTED_SOURCE_EVENTS[family] or len(source_rows)!=20:
        raise ValueError("MR34I3_ORIGINAL_TRAIN_SOURCE_EVENT_IDENTITY_MISMATCH")
    source_bytes=source_episode_inputs(source_rows)
    model=NativePredictiveQuotient45()
    initial=sha(model.snapshot().encode())
    moments=[np.zeros_like(p) for p in model.params()]
    variance=[np.zeros_like(p) for p in model.params()]
    trace=[]
    begin=time.process_time_ns()
    for update,episode in enumerate(source_rows[:MAX_FIRST_UPDATES],1):
        pre=raw_params_digest(model)
        rec=instrument_original_bptt(model,episode)
        step=update_exact(model,episode,moments,variance,update,
                          LR,BETAS,EPS,L2,CLIP)
        rec.update({
            "original_update":update,
            "original_45_pregradient_weight_sha256":pre,
            "original_45_postgradient_weight_sha256":step["post_update_parameter_float64_sha256"],
            "original_analytic_gradient_shared_sha256":step["original_unregularized_gradient_sha256"][0],
            "original_analytic_gradient_local_sha256":step["original_unregularized_gradient_sha256"][1],
            "original_adam_first_moment_sha256":step["adam_first_moment_sha256"],
            "original_adam_second_moment_sha256":step["adam_second_moment_sha256"],
        })
        if (rec["original_total_analytic_gradient_shared"]["sha256"]!=
            rec["original_analytic_gradient_shared_sha256"] or
            rec["original_total_analytic_gradient_local"]["sha256"]!=
            rec["original_analytic_gradient_local_sha256"]):
            raise RuntimeError("MR34I3_ALTERNATE_BPTT_DID_NOT_MATCH_NATIVE")
        trace.append(rec)
    original_git(root,SOURCES[family])
    return {
        "original_source_authored_SHA":SOURCES[family],
        "exact_original_training_events_sha256":identity,
        "original_public_source_training_tensors":source_bytes,
        "original_source_training_roles":list(SEEDS),
        "actual_original_source_training_actions":sum(map(len,source_rows)),
        "original_initial_45_parameter_snapshot_sha256":initial,
        "original_first_11_updates_and_coordinates":trace,
        "traced_native_training_only_CPU_ns":time.process_time_ns()-begin,
        "no_scientific_DEV_or_protected_source_actions":True
    }


def main(s4c1,farama,pycolab,out):
    original_git(s4c1,S4C1_SHA)
    roots={
        "FaramaMiniGridDoorKey8":original_git(farama,SOURCES["FaramaMiniGridDoorKey8"]),
        "DeepMindPycolabApprehend":original_git(pycolab,SOURCES["DeepMindPycolabApprehend"])
    }
    sys.path.insert(0,str(Path(s4c1).resolve()))
    for root in roots.values():
        sys.path.insert(0,str(root))
    from research.mr27.natural_memory import source_guard
    source_guard(roots["FaramaMiniGridDoorKey8"])
    results={name:original_source_training_trace(name,root) for name,root in roots.items()}
    for name,root in roots.items():
        original_git(root,SOURCES[name])
    original_git(s4c1,S4C1_SHA)
    receipt={
        "schema":SCHEMA,
        "first_precode_protocol_commit":FIRST,
        "original_pinned_unchanged_S4C1_trainer":S4C1_SHA,
        "operating_system":platform.system(),
        "python_version":platform.python_version(),
        "numpy_version":np.__version__,
        "source_results":results,
        "no_original_held_test_or_protected_first_use":True,
        "native_model_weights_or_original_source_modified":False,
        "scientific_admission":"NOT_QUALIFIED",
        "process_peak_RSS_bytes":peak_rss()
    }
    out=Path(out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n",encoding="utf-8")
    print("MR34I3_ORIGINAL_TRAIN_ONLY_COORDINATE_RECEIPT="+canon({
        "schema":SCHEMA,
        "operating_system":platform.system(),
        "receipt_sha256":sha(out.read_bytes()),
        "families":{
            k:{"source_event_sha":v["exact_original_training_events_sha256"],
               "first11_original_pre_weights":[q["original_45_pregradient_weight_sha256"]
                   for q in v["original_first_11_updates_and_coordinates"]],
               "first11_native_gradient":[q["original_total_analytic_gradient_shared"]["sha256"]
                   for q in v["original_first_11_updates_and_coordinates"]],
               "first11_native_model_after":[q["original_45_postgradient_weight_sha256"]
                   for q in v["original_first_11_updates_and_coordinates"]]}
            for k,v in results.items()},
        "scientific_first_use":False
    }))


if __name__=="__main__":
    if len(sys.argv)!=5:
        raise SystemExit("Usage: python -m research.mr34i3.coordinate_probe S4C1 FARAMA PYCOLAB RECEIPT_JSON")
    main(*sys.argv[1:])
