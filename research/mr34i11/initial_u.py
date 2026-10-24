"""MR34I11 — original TRAIN first-preaction native numeric-custody probe.

Separate source-neutral initial-dot candidate is READ-ONLY. Never substitutes
candidate arithmetic into the original source, native learner or trained model.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
import os
from pathlib import Path
import platform
import sys
import time

import numpy as np

from research.mr34i1.train_only_numeric import (
    SOURCES,SEEDS,S4C1_SHA,original_git,source_episode_inputs,peak_rss,canon,sha)
from research.mr34i7.portable_kernel import raw,EXPECTED
from research.mr34i9.optin_train import ORIGINAL_EVENT_SHA
from research.mr34i10.fixed160_train import fixed160_sigmoid

SCHEMA="mass.mr34i11.original-first-preaction-source-neutral-fsum.v1"
FIRST="a12f477b12d74e7c383cb944318ea371fbef292f"
PARENT="1ab12be5dce0502c32c532ac32d095b2378dc82c"


def mark(values):
    """Exact native binary64 identity, including all local cell coordinates."""
    data=np.asarray(values,dtype=np.float64)
    if not np.isfinite(data).all():
        raise ValueError("MR34I11_NONFINITE_NUMERIC_STAGE")
    return {
        "shape":list(data.shape),
        "sha256":sha(np.ascontiguousarray(data).tobytes(order="C")),
        "hex":[float(x).hex() for x in data.flat]
    }


def exact_initial_from_public(f,g,roles):
    """Proposed source-neutral scalar initial u; never a model update."""
    if (f.shape!=(8,7) or g.shape!=(3,7) or roles.shape!=(8,3)
        or not np.isfinite(f).all() or not np.isfinite(g).all()
        or not np.isfinite(roles).all()):
        raise ValueError("MR34I11_PUBLIC_SOURCE_MODEL_DIMENSIONS_INVALID")
    u=[]
    read=[]
    for i in range(8):
        u.append(math.fsum(
            [float(f[i,j])*float(g[0,j]) for j in range(7)]+
            [float(roles[i,0])]))
        read.append(math.fsum(
            [float(f[i,j])*float(g[1,j]) for j in range(7)]+
            [float(roles[i,1])]))
    return np.asarray(u,dtype=np.float64),np.asarray(read,dtype=np.float64)


def stages_of_source(name,root):
    from research.mr34f.prospective_controls import episodes,SOURCES as ORIGINAL
    from research.nci04_s4c1.original_native_predictive_state import TRAIN,protocol
    from research.nci04_s4c1.native_predictive_quotient import (
        NativePredictiveQuotient45,cell_public_features
    )
    if tuple(TRAIN)!=SEEDS or ORIGINAL[name][0]!=SOURCES[name] or len(SEEDS)!=20:
        raise ValueError("MR34I11_EXISTING_ORIGINAL_TRAIN_ROLES_MISMATCH")
    protocol()
    start=time.process_time_ns()
    episode,events=episodes(root,name,SEEDS)
    acquisition_cpu=time.process_time_ns()-start
    event_sha=sha(canon(events).encode())
    if len(episode)!=20 or event_sha!=ORIGINAL_EVENT_SHA[name]:
        raise ValueError("MR34I11_ORIGINAL_SOURCE_EVENT_CUSTODY_DRIFT")
    tensors=source_episode_inputs(episode)
    original=NativePredictiveQuotient45()
    original_init=original.snapshot()
    before=sha(original_init.encode())
    original_initial=[]
    candidate_initial=[]
    per_reset=[]
    orig_cpu=0
    candidate_cpu=0
    for seed,rows in zip(SEEDS,episode):
        if len(rows)==0:
            raise ValueError("MR34I11_EMPTY_ORIGINAL_SOURCE_RESET")
        public=np.asarray(rows[0][0],dtype=np.float64)
        if public.shape!=(23,):
            raise ValueError("MR34I11_PUBLIC_SOURCE_FEATURE_DRIFT")
        f=cell_public_features(public)
        start=time.process_time_ns()
        dot0=f@original.g[0]
        dot1=f@original.g[1]
        role0=original.roles[:,0].copy()
        role1=original.roles[:,1].copy()
        read=dot1+role1
        original_u=dot0+role0+np.zeros(8,dtype=np.float64)*read
        original_p=original.forward([rows[0]])[0]
        mirror=1./(1.+np.exp(-np.clip(original_u,-35.,35.)))
        orig_cpu+=time.process_time_ns()-start
        if (not np.array_equal(original_p.view(np.uint64),
                               mirror.view(np.uint64))
            or f.shape!=(8,7)):
            raise ValueError("MR34I11_UNMODIFIED_NATIVE_FORWARD_MISMATCH")
        start=time.process_time_ns()
        proposed,proposed_read=exact_initial_from_public(
            f,original.g,original.roles)
        projected=np.asarray(
            [fixed160_sigmoid(z) for z in proposed],dtype=np.float64)
        candidate_cpu+=time.process_time_ns()-start
        original_initial.extend(float(x) for x in original_u)
        candidate_initial.extend(float(x) for x in proposed)
        per_reset.append({
            "original_source_train_seed":seed,
            "original_first_public23":mark(public),
            "original_source_first_action_public_target":mark(rows[0][2]),
            "native_source_cell_features_8x7":mark(f),
            "public_action_angle_cos_sin":mark(f[0,5:7]),
            "native_original_g0_dot":mark(dot0),
            "native_original_g1_dot":mark(dot1),
            "native_original_local_role0":mark(role0),
            "native_original_local_role1":mark(role1),
            "native_original_read":mark(read),
            "native_original_u":mark(original_u),
            "native_original_p":mark(original_p),
            "source_neutral_fsum_candidate_read":mark(proposed_read),
            "source_neutral_fsum_candidate_u":mark(proposed),
            "source_neutral_fixed160_projection_only":mark(projected),
            "original_to_candidate_same_bits":[
                bool(float(a).hex()==float(b).hex())
                for a,b in zip(original_u,proposed)]
        })
    if original.snapshot()!=original_init or original.train_updates!=0:
        raise ValueError("MR34I11_ORIGINAL_NATIVE_MODEL_MUTATED")
    original_sha=sha(raw(original_initial))
    candidate_sha=sha(raw(candidate_initial))
    original_git(root,SOURCES[name])
    return {
        "original_authored_source_git_sha":SOURCES[name],
        "original_source_events_sha256":event_sha,
        "original_training_only_public_input_target_tensors":tensors,
        "original_native_initial_45_checkpoint_SHA256":before,
        "original_first_logits_sha256":original_sha,
        "previous_frozen_original_first_logits_sha256":EXPECTED[name],
        "original_first_logits_match_previous_consumed_identity":original_sha==EXPECTED[name],
        "candidate_source_neutral_first_logits_sha256":candidate_sha,
        "candidate_first_logit_count":len(candidate_initial),
        "original_to_candidate_exact_cell_count":sum(
            sum(e["original_to_candidate_same_bits"]) for e in per_reset),
        "original_source_first_only_reset_traces":per_reset,
        "source_original_acquisition_CPU_ns":acquisition_cpu,
        "source_original_first_u_CPU_ns":orig_cpu,
        "candidate_fsum_initial_u_CPU_ns":candidate_cpu,
        "protected_or_original_heldout_source_actions_generated":0,
        "native_source_and_trainer_unchanged":True
    }


def main(s4c1,farama,pycolab,output):
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
    reports={name:stages_of_source(name,root) for name,root in roots.items()}
    for name,root in roots.items():
        original_git(root,SOURCES[name])
    original_git(s4c1,S4C1_SHA)
    receipt={
        "schema":SCHEMA,"precode_frozen_protocol_commit":FIRST,
        "parent_MR34I10_exact_HEAD":PARENT,
        "original_unchanged_native_S4C1_git":S4C1_SHA,
        "source_reports":reports,
        "OS":platform.system(),
        "processor":platform.processor(),
        "Python":platform.python_version(),
        "NumPy":np.__version__,
        "NPY_DISABLE_CPU_FEATURES":os.environ.get("NPY_DISABLE_CPU_FEATURES",""),
        "genuine_original_TRAIN_only":True,
        "original_protected_first_use":False,
        "native_learning_advanced_or_modified":False,
        "source_worker_peak_OS_RSS_bytes":peak_rss(),
        "scientific_admission":"NO_GO"
    }
    p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(receipt,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n",encoding="utf-8")
    print("MR34I11_SOURCE_ONLY_FSUM_INITIAL_RECEIPT="+canon({
        "schema":SCHEMA,
        "os":platform.system(),
        "receipt_sha256":sha(p.read_bytes()),
        "sources":{name:{
            "original_event_sha256":report["original_source_events_sha256"],
            "old_original_first_logits_sha256":report["original_first_logits_sha256"],
            "old_identity_matched":report["original_first_logits_match_previous_consumed_identity"],
            "candidate_first_logits_sha256":report["candidate_source_neutral_first_logits_sha256"],
            "candidate_logit_count":report["candidate_first_logit_count"],
            "same_bits_old_to_candidate":report["original_to_candidate_exact_cell_count"]}
            for name,report in reports.items()},
        "original_protected_first_use":False
    }))


if __name__=="__main__":
    if len(sys.argv)!=5:
        raise SystemExit("Usage: python -m research.mr34i11.initial_u S4C1 FARAMA PYCOLAB OUT")
    main(*sys.argv[1:])
