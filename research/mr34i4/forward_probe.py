"""MR34I4: diagnose original native matmul/preactivation versus exp/sigmoid ULP.

Existing public TRAIN only; no modified native model, oracle, original DEV or
substituted higher-precision training arithmetic. All diagnostics are read-only.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
import platform
import sys
import time
import numpy as np

from research.mr34i1.train_only_numeric import (
    SOURCES, SEEDS, S4C1_SHA, original_git, sha, canon,
    source_episode_inputs, peak_rss
)
from research.mr34i2.trace_first_update import update_exact, raw_params_digest
from research.mr34i3.coordinate_probe import (
    EXPECTED_SOURCE_EVENTS, mark, dot_reference
)

FIRST="e294f1417ac5048f71be79d6db5099c5b6c40f44"
SCHEMA="mass.mr34i4.native-first-forward-arithmetic-stage.v1"
MAX_ORIGINAL_TRAIN_UPDATES=3


def unmodified_native_forward_stages(model, episode):
    """Cache original forward, reconstruct each arithmetic stage without writes."""
    original_prob, cached=model.forward(episode,cache=True)
    if len(cached)!=len(episode):
        raise ValueError("MR34I4_ORIGINAL_FORWARD_EPISODE_LENGTH")
    stages=[]
    g=model.g
    roles=model.roles
    before=raw_params_digest(model)
    for t,(f,s,read,p,ns) in enumerate(cached):
        read_dot=f@g[1]
        read_add=read_dot+roles[:,1]
        u_dot=f@g[0]
        u_role=u_dot+roles[:,0]
        state_term=s*read
        original_u=u_role+state_term
        clipped=np.clip(original_u,-35.,35.)
        negclipped=-clipped
        numpy_exponent=np.exp(negclipped)
        denominator=1.+numpy_exponent
        recomputed_p=1./denominator
        if (read_add.tobytes()!=read.tobytes() or
            recomputed_p.tobytes()!=p.tobytes() or
            recomputed_p.tobytes()!=original_prob[t].tobytes()):
            raise ValueError("MR34I4_NATIVE_FORWARD_RECONSTRUCTION_NOT_BYTE_EXACT")
        reference_read,reference_u=dot_reference(f,model,s)
        # Scalar references are NEVER substituted into the original prediction.
        scalar_exp=np.asarray([math.exp(float(x)) for x in negclipped],dtype=np.float64)
        scalar_sigmoid=np.asarray([1./(1.+math.exp(float(x))) for x in negclipped],dtype=np.float64)
        stage={
            "source_time_index":t,
            "public_features":mark(f),
            "original_prior_state":mark(s),
            "original_read_matmul":mark(read_dot),
            "original_read_after_role":mark(read_add),
            "original_cached_read":mark(read),
            "original_u_matmul":mark(u_dot),
            "original_u_after_role":mark(u_role),
            "original_recurrent_state_term":mark(state_term),
            "original_u_preactivation":mark(original_u),
            "original_clipped_u":mark(clipped),
            "original_negated_clipped_u":mark(negclipped),
            "original_numpy_exp":mark(numpy_exponent),
            "original_sigmoid_denominator":mark(denominator),
            "original_predicted_probability":mark(recomputed_p),
            "original_cached_predicted_probability":mark(p),
            "original_next_native_state":mark(ns),
            "diagnostic_readonly_fsum_read":reference_read,
            "diagnostic_readonly_fsum_u":reference_u,
            "diagnostic_readonly_scalar_math_exp":mark(scalar_exp),
            "diagnostic_readonly_scalar_math_sigmoid":mark(scalar_sigmoid)
        }
        stages.append(stage)
    if raw_params_digest(model)!=before:
        raise ValueError("MR34I4_SOURCE_NATIVE_WEIGHTS_MUTATED_BY_DIAGNOSTIC")
    return stages


def trace_source(family,root):
    from research.mr34f.prospective_controls import episodes, SOURCES as ORIGINALS
    from research.nci04_s4c1.original_native_predictive_state import (
        TRAIN,EPOCHS,LR,BETAS,EPS,L2,CLIP,protocol
    )
    from research.nci04_s4c1.native_predictive_quotient import NativePredictiveQuotient45,PARAMETERS
    if tuple(TRAIN)!=SEEDS or PARAMETERS!=45 or EPOCHS!=40 or ORIGINALS[family][0]!=SOURCES[family]:
        raise ValueError("MR34I4_ORIGINAL_NATIVE_TRAIN_SOURCE_DRIFT")
    protocol()
    data,events=episodes(root,family,SEEDS)
    source_digest=sha(canon(events).encode())
    if len(data)!=20 or source_digest!=EXPECTED_SOURCE_EVENTS[family]:
        raise ValueError("MR34I4_ORIGINAL_TRAIN_EVENT_SOURCE_CUSTODY_DRIFT")
    tensors=source_episode_inputs(data)
    model=NativePredictiveQuotient45()
    initial=sha(model.snapshot().encode())
    moments=[np.zeros_like(x) for x in model.params()]
    variances=[np.zeros_like(x) for x in model.params()]
    iterations=[]
    started=time.process_time_ns()
    for step,episode in enumerate(data[:MAX_ORIGINAL_TRAIN_UPDATES],1):
        pre=raw_params_digest(model)
        stages=unmodified_native_forward_stages(model,episode)
        # Pinned S4C1 gradient + Adam source-training equations unchanged.
        original_update=update_exact(model,episode,moments,variances,step,LR,BETAS,EPS,L2,CLIP)
        iterations.append({
            "original_training_update_number":step,
            "original_45_pre_update_weight_sha256":pre,
            "original_45_post_update_weight_sha256":original_update["post_update_parameter_float64_sha256"],
            "original_analytic_gradient_sha256":original_update["original_unregularized_gradient_sha256"],
            "original_adam_moment_sha256":[original_update["adam_first_moment_sha256"],original_update["adam_second_moment_sha256"]],
            "chronological_native_forward_stages":stages
        })
    original_git(root,SOURCES[family])
    return {
        "original_source_git_sha":SOURCES[family],
        "source_train_public_original_event_sha256":source_digest,
        "source_public_input_and_consequence_tensors":tensors,
        "native_initial_45_snapshot_sha256":initial,
        "original_training_action_count":sum(map(len,data)),
        "original_training_reset_count":len(SEEDS),
        "first_three_original_training_updates":iterations,
        "diagnostic_and_learning_total_cpu_ns":time.process_time_ns()-started,
        "original_held_or_protected_source_actions":0
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
    reports={name:trace_source(name,root) for name,root in roots.items()}
    for k,root in roots.items():
        original_git(root,SOURCES[k])
    original_git(s4c1,S4C1_SHA)
    receipt={
        "schema":SCHEMA,
        "first_protocol_only_commit":FIRST,
        "pinned_original_native_S4C1_sha":S4C1_SHA,
        "runtime_os":platform.system(),
        "python":platform.python_version(),
        "numpy":np.__version__,
        "real_original_source_reports":reports,
        "read_only_diagnostic_not_training_substitute":True,
        "previously_consumed_original_TRAIN_reset_roles_only":True,
        "no_scientific_original_held_or_protected_first_use":True,
        "scientific_admission":"NO_GO",
        "peak_process_RSS_bytes":peak_rss()
    }
    path=Path(out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(receipt,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n",encoding="utf-8")
    print("MR34I4_ORIGINAL_TRAIN_ONLY_STAGE_RECEIPT="+canon({
        "schema":SCHEMA,"os":platform.system(),
        "receipt_sha256":sha(path.read_bytes()),
        "family_source_digests":{name:r["source_train_public_original_event_sha256"] for name,r in reports.items()},
        "full_original_first_three_gradient_sha":{name:[v["original_analytic_gradient_sha256"] for v in r["first_three_original_training_updates"]] for name,r in reports.items()},
        "original_protected_first_use":False
    }))


if __name__=="__main__":
    if len(sys.argv)!=5:
        raise SystemExit("Usage: python -m research.mr34i4.forward_probe S4C1 FARAMA PYCOLAB OUT")
    main(*sys.argv[1:])
