"""MR34I2: source-training-only forensic localization of native S4C1 float drift.

Replicates exact PINNED original optimizer in a NEW audit process, NEVER alters
the original S4C1 model, source engine, data roles, training budget or methods.
The original original train_native() must reproduce traced selected checkpoint.
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
    original_git, SOURCES, S4C1_SHA, SEEDS, canon, source_episode_inputs, sha, peak_rss
)

FIRST="1d867b52af3062096b3f4f8df3b4726b499b2dbf"
SCHEMA="mass.mr34i2.original-source-training-only-float-divergence.v1"
WIN={"DeepMindPycolabApprehend":("18fbc598ba7139e164b2477ff18af92a76985dbca782be6c34707a73abea439a",38),
     "FaramaMiniGridDoorKey8":("4474b2e151a0053e51feedb102f4f38b1b3e1a8bcaedab8a7f188ee6a95d8e02",40)}
LIN={"DeepMindPycolabApprehend":("9faa1845ae7aab8b23c5eea0735e628ce8027701bb62bb3b823a2695a46bcf0d",34),
     "FaramaMiniGridDoorKey8":("13d5fc55cf2f8199cc7d39fc8053a0fa66b9637cf4b9d9b3fb244628728553f7",40)}


def raw_params_digest(model):
    return sha(b"".join(x.tobytes(order="C") for x in model.params()))


def update_exact(model, episode, a, b, step, LR, BETAS, EPS, L2, CLIP):
    """Byte-equivalent equations to the unchanged original original_native_train."""
    grads=list(model.analytic_bptt(episode))
    unregularized=[sha(g.tobytes(order="C")) for g in grads]
    grads=[g+(L2*w if w.ndim==2 else 0.)
           for g,w in zip(grads,model.params())]
    norm=float(np.sqrt(sum(float(np.sum(g*g)) for g in grads)))
    if not math.isfinite(norm):
        raise ValueError("ORIGINAL_NATIVE_GRADIENT_NONFINITE")
    factor=min(1.,CLIP/max(norm,1e-12))
    for i,(w,g) in enumerate(zip(model.params(),grads)):
        g=g*factor
        a[i]=BETAS[0]*a[i]+(1.-BETAS[0])*g
        b[i]=BETAS[1]*b[i]+(1.-BETAS[1])*(g*g)
        m=a[i]/(1.-BETAS[0]**step)
        v=b[i]/(1.-BETAS[1]**step)
        w-=LR*m/(np.sqrt(v)+EPS)
    model.train_updates+=1
    return {
        "step":step,
        "original_unregularized_gradient_sha256":unregularized,
        "post_regularization_and_clip_global_norm":norm,
        "post_update_parameter_float64_sha256":raw_params_digest(model),
        "post_update_model_snapshot_sha256":sha(model.snapshot().encode()),
        "adam_first_moment_sha256":sha(b"".join(x.tobytes() for x in a)),
        "adam_second_moment_sha256":sha(b"".join(x.tobytes() for x in b)),
    }


def trace_one(family, root):
    from research.nci04_s4c1.original_native_predictive_state import (
        train_native,TRAIN,EPOCHS,LR,BETAS,EPS,L2,CLIP,score,protocol)
    from research.nci04_s4c1.native_predictive_quotient import (
        NativePredictiveQuotient45,PARAMETERS)
    from research.mr34f.prospective_controls import episodes,SOURCES as ORIGINALS
    if tuple(TRAIN)!=SEEDS or EPOCHS!=40 or PARAMETERS!=45 or ORIGINALS[family][0]!=SOURCES[family]:
        raise ValueError("ORIGINAL_NATIVE_TRAINING_SOURCE_DRIFT")
    protocol()
    source_rows,original_receipts=episodes(root,family,SEEDS)
    if len(source_rows)!=20 or any(not ep for ep in source_rows):
        raise ValueError("INVALID_ORIGINAL_SOURCE_TRAIN_ONLY_ROWS")
    original_action_digest=sha(canon(original_receipts).encode())
    original_tensor_digest=source_episode_inputs(source_rows)
    start=time.process_time_ns()
    model=NativePredictiveQuotient45()
    first_snapshot=sha(model.snapshot().encode())
    initial_gradient=model.analytic_bptt(source_rows[0])
    gradient_sha=[sha(g.tobytes()) for g in initial_gradient]
    model.source_gradient_finite_difference(source_rows[0])
    a=[np.zeros_like(w) for w in model.params()]
    b=[np.zeros_like(w) for w in model.params()]
    t=0
    saved=None
    first_epoch=[]
    epoch_record=[]
    for epoch in range(1,EPOCHS+1):
        for i,ep in enumerate(source_rows):
            t+=1
            step_record=update_exact(model,ep,a,b,t,LR,BETAS,EPS,L2,CLIP)
            if epoch==1:
                first_epoch.append(step_record)
        train_scores=[model.forward(ep) for ep in source_rows]
        total,_=score(train_scores,source_rows)
        if not math.isfinite(total):
            raise ValueError("ORIGINAL_TRAIN_ONLY_BRIER_NONFINITE")
        current_snapshot=model.snapshot()
        epoch_record.append({
            "epoch":epoch,
            "train_only_source_Brier":float(total),
            "end_epoch_float64_parameter_sha256":raw_params_digest(model),
            "end_epoch_original_snapshot_sha256":sha(current_snapshot.encode())
        })
        if saved is None or total<saved[0]:
            saved=(total,epoch,current_snapshot)
    best,selected_epoch,selected=saved
    actual_sha=sha(selected.encode())
    restored=NativePredictiveQuotient45.restore(selected)
    if restored.snapshot()!=selected:
        raise ValueError("SOURCE_PINNED_ORIGINAL_SNAPSHOT_ROUNDTRIP_FAILED")
    # Independently call, without monkey patching, original S4C1 training.
    original_model,receipt=train_native(source_rows)
    original_sha=sha(original_model.snapshot().encode())
    expected=(WIN if platform.system()=="Windows" else LIN)[family]
    original_valid=(
        original_sha==actual_sha==expected[0] and
        receipt["TRAINING_ONLY_selected_epoch"]==selected_epoch==expected[1] and
        receipt["source_native_training_first_last_best_Brier"]==
            [epoch_record[0]["train_only_source_Brier"],
             epoch_record[-1]["train_only_source_Brier"],
             best]
    )
    if not original_valid:
        raise RuntimeError("MR34I2_TRACER_NOT_EXACT_PINNED_NATIVE_MODEL")
    original_git(root,SOURCES[family])
    return {
        "authentic_original_source_git_sha":SOURCES[family],
        "source_training_only_action_receipt_sha256":original_action_digest,
        "source_training_only_float64_tensor_sha256":{
            "public_23":original_tensor_digest["all_public_preaction_23_float64_bytes_sha256"],
            "previous_69":original_tensor_digest["all_previous_public_history_69_float64_bytes_sha256"],
            "next_8":original_tensor_digest["all_native_eight_future_public_target_float64_bytes_sha256"]
        },
        "source_training_reset_count":len(source_rows),
        "source_training_original_actions":sum(len(ep) for ep in source_rows),
        "native_initial_45_snapshot_sha256":first_snapshot,
        "first_original_bptt_gradient_sha256":gradient_sha,
        "first_20_original_epoch_updates":first_epoch,
        "all_40_train_only_epoch_model_snapshots":epoch_record,
        "tracer_selected_train_only_epoch":selected_epoch,
        "tracer_trained_native_snapshot_sha256":actual_sha,
        "original_imported_unchanged_trainer_snapshot_sha256":original_sha,
        "tracer_matches_unmodified_original_trainer_and_previous_MR34I1":True,
        "full_native_tracer_and_independent_original_train_cpu_ns":time.process_time_ns()-start,
        "held_original_source_resets_consumed":0,
    }


def main(s4c1, farama, pycolab):
    original_git(s4c1,S4C1_SHA)
    roots={
        "FaramaMiniGridDoorKey8":original_git(farama,SOURCES["FaramaMiniGridDoorKey8"]),
        "DeepMindPycolabApprehend":original_git(pycolab,SOURCES["DeepMindPycolabApprehend"]),
    }
    sys.path.insert(0,str(Path(s4c1).resolve()))
    for root in roots.values():
        sys.path.insert(0,str(root))
    from research.mr27.natural_memory import source_guard
    source_guard(roots["FaramaMiniGridDoorKey8"])
    all_sources={k:trace_one(k,r) for k,r in roots.items()}
    for k,root in roots.items():
        original_git(root,SOURCES[k])
    original_git(s4c1,S4C1_SHA)
    print("MR34I2_UNMODIFIED_ORIGINAL_TRAIN_STAGE_TRACE="+canon({
        "schema":SCHEMA,
        "first_protocol_only_commit":FIRST,
        "unmodified_original_S4C1_sha":S4C1_SHA,
        "source_reports":all_sources,
        "original_training_only":True,
        "previously_consumed_source_training_roles_only":True,
        "new_or_old_held_DEV_source_actions":0,
        "protected_first_use":False,
        "source_neutral_transfer":False,
        "scientific_admission":"NO_GO",
        "OS":platform.system(),
        "numpy_version":np.__version__,
        "full_audit_peak_OS_RSS_bytes":peak_rss(),
    }))


if __name__=="__main__":
    if len(sys.argv)!=4:
        raise SystemExit("Usage: python -m research.mr34i2.trace_first_update S4C1 FARAMA PYCOLAB")
    main(*sys.argv[1:])
