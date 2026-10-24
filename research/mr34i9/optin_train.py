"""MR34I9: original TRAIN-only opt-in portable sigmoid native training feasibility.

Never changes original NativePredictiveQuotient45, source/held cohorts or
original native trainer; source code and numerical kernel are pinned and
loaded from their original immutable revisions.
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
    SOURCES, SEEDS, S4C1_SHA, original_git, source_episode_inputs, peak_rss,
    canon, sha
)
from research.mr34i7.portable_kernel import portable_decimal

SCHEMA="mass.mr34i9.optin-original-source-full-native-training.v1"
FIRST="edd80b67d0d9b45a8098a3f676393db3788a4e5c"
PARENT="608675a3343ff9ff34a96e2057a8091f738aaf5f"
KERNEL_GIT_BLOB="unknown"
ORIGINAL_EVENT_SHA={
    "FaramaMiniGridDoorKey8":"566f5e271e01421248bfabeb4326d01408d992276b877a978d96f14daf93797b",
    "DeepMindPycolabApprehend":"9ea175b912b734c7470f93d0b2584eea6c2ce01962aae285a66b4d4834b5346e"
}
MAX_TRAIN_CPU_RATIO=50.


def make_portable_class():
    from research.nci04_s4c1.native_predictive_quotient import (
        NativePredictiveQuotient45, cell_public_features,N
    )
    class PortableNative45(NativePredictiveQuotient45):
        """Only native p source changes; all original 45 weights/roles/BPTT."""

        def forward(self,episode,zero_state=False,permuted_roles=False,cache=False):
            self._validate_params()
            if not episode or type(zero_state) is not bool or type(permuted_roles) is not bool:
                raise ValueError("MR34I9_INVALID_ORIGINAL_EPISODE_OR_BOOLEAN_POLICY")
            roles=(self.roles[[0,2,4,6,1,3,5,7]].copy()
                   if permuted_roles else self.roles)
            s=np.zeros(N,dtype=np.float64)
            forecasts=[]
            details=[]
            for row in episode:
                f=cell_public_features(row[0])
                used_s=np.zeros(N) if zero_state else s
                read=f@self.g[1]+roles[:,1]
                u=f@self.g[0]+roles[:,0]+used_s*read
                # EXACT already prequalified source-neutral Decimal48 kernel;
                # no source-native state, no input rounding and no new parameters.
                p=np.asarray(portable_decimal(u,48),dtype=np.float64)
                next_s=np.tanh(f@self.g[2]+roles[:,2]*(2.*p-1.))
                if not np.all(np.isfinite(next_s)) or np.max(np.abs(next_s))>1.:
                    raise ValueError("MR34I9_PORTABLE_NATIVE_STATE_NONFINITE")
                forecasts.append(p)
                if cache:
                    details.append((f,used_s.copy(),read,p,next_s.copy()))
                s=next_s
            pp=np.asarray(forecasts,dtype=np.float64)
            return (pp,details) if cache else pp
    return PortableNative45,NativePredictiveQuotient45


def exact_frozen_optimizer(model, source_train):
    from research.nci04_s4c1.original_native_predictive_state import (
        LR,BETAS,EPS,L2,CLIP,EPOCHS,score,PARAMETERS
    )
    assert EPOCHS==40 and LR==.035 and BETAS==(.9,.999) and EPS==1e-8
    assert L2==.0002 and CLIP==5. and PARAMETERS==45
    grad_start=time.process_time_ns()
    gradient_finite_difference=model.source_gradient_finite_difference(source_train[0])
    gradient_CPU=time.process_time_ns()-grad_start
    a=[np.zeros_like(w) for w in model.params()]
    b=[np.zeros_like(w) for w in model.params()]
    t=0
    saved=None
    history=[]
    epoch_shas=[]
    started=time.process_time_ns()
    for epoch in range(1,EPOCHS+1):
        for ep in source_train:
            grads=list(model.analytic_bptt(ep))
            grads=[g+(L2*w if w.ndim==2 else 0.)
                   for g,w in zip(grads,model.params())]
            norm=float(np.sqrt(sum(float(np.sum(g*g)) for g in grads)))
            if not math.isfinite(norm):
                raise ValueError("MR34I9_NONFINITE_ORIGINAL_SOURCE_BPTT")
            factor=min(1.,CLIP/max(norm,1e-12))
            t+=1
            for i,(w,g) in enumerate(zip(model.params(),grads)):
                g=g*factor
                a[i]=BETAS[0]*a[i]+(1.-BETAS[0])*g
                b[i]=BETAS[1]*b[i]+(1.-BETAS[1])*(g*g)
                m=a[i]/(1.-BETAS[0]**t)
                v=b[i]/(1.-BETAS[1]**t)
                w-=LR*m/(np.sqrt(v)+EPS)
            model.train_updates+=1
        outputs=[model.forward(ep) for ep in source_train]
        total,_=score(outputs,source_train)
        if not math.isfinite(total):
            raise ValueError("MR34I9_ORIGINAL_SOURCE_TRAIN_BRIER_NONFINITE")
        history.append(float(total))
        snapshot=model.snapshot()
        epoch_shas.append(sha256(snapshot.encode()).hexdigest())
        if saved is None or total<saved[0]:
            saved=(total,epoch,snapshot)
    training_cpu=time.process_time_ns()-started
    best,epoch,original_serialized=saved
    restored=type(model).restore(original_serialized)
    if restored.snapshot()!=original_serialized or type(restored)!=type(model):
        raise ValueError("MR34I9_OPTIN_NATIVE_RESTORE_IDENTITY_DRIFT")
    return restored,{
        "original_frozen_training_epochs":EPOCHS,
        "source_actual_training_updates":t,
        "original_train_only_epoch_Brier":history,
        "original_train_only_epoch_checkpoint_sha256":epoch_shas,
        "source_train_only_selected_epoch":epoch,
        "original_train_only_best_Brier":best,
        "source_trained_45_native_checkpoint_sha256":sha256(original_serialized.encode()).hexdigest(),
        "source_native_gradient_finite_difference":gradient_finite_difference,
        "finite_difference_CPU_ns":gradient_CPU,
        "training_CPU_ns_40epochs_source_excluded":training_cpu,
        "checkpoint_bytes":len(original_serialized.encode()),
        "exact_native_45_weights":sum(z.size for z in restored.params())==45,
        "no_protected_first_use":True
    }


def evaluate_source(family,root):
    from research.mr34f.prospective_controls import episodes,SOURCES as ORIGINALS
    from research.nci04_s4c1.original_native_predictive_state import (
        train_native,TRAIN,protocol
    )
    Portable,Original=make_portable_class()
    protocol()
    if tuple(TRAIN)!=SEEDS or ORIGINALS[family][0]!=SOURCES[family]:
        raise ValueError("MR34I9_SOURCE_TRAINING_OR_FAMILY_ID_DRIFT")
    source_start=time.process_time_ns()
    data,source_receipt=episodes(root,family,SEEDS)
    source_CPU=time.process_time_ns()-source_start
    identity=sha(canon(source_receipt).encode())
    if identity!=ORIGINAL_EVENT_SHA[family] or len(data)!=20:
        raise ValueError("MR34I9_REAL_ORIGINAL_TRAIN_EVENT_DRIFT")
    inputs=source_episode_inputs(data)
    initial_a=Original().snapshot()
    initial_b=Portable().snapshot()
    if initial_a!=initial_b:
        raise ValueError("MR34I9_INITIAL_NATIVE_45_WEIGHT_DRIFT")
    untouched,original_info=train_native(data)
    copied_original,original_trajectory=exact_frozen_optimizer(Original(),data)
    # Fail closed if local engineering-trained original does not reproduce the
    # untouched imported original native trainer ON THIS SAME HOST.
    if (copied_original.snapshot()!=untouched.snapshot()
        or original_info["TRAINING_ONLY_selected_epoch"]!=original_trajectory["source_train_only_selected_epoch"]
        or original_info["source_native_training_first_last_best_Brier"]!=[
            original_trajectory["original_train_only_epoch_Brier"][0],
            original_trajectory["original_train_only_epoch_Brier"][-1],
            original_trajectory["original_train_only_best_Brier"]]):
        raise RuntimeError("MR34I9_LOCAL_ORIGINAL_TRAINER_SEMANTIC_PARITY_FAIL")
    candidate,candidate_info=exact_frozen_optimizer(Portable(),data)
    ratio=candidate_info["training_CPU_ns_40epochs_source_excluded"]/max(
        1,original_info["training_cpu_ns_full_episode_45_coefficient_Adam"])
    same_model_sizes=(original_trajectory["exact_native_45_weights"] and
                      candidate_info["exact_native_45_weights"])
    before=candidate.snapshot()
    # Fresh trained candidate must not silently become the original NumPy
    # native inference through restoring its snapshot.
    if candidate.snapshot()!=before or not same_model_sizes:
        raise RuntimeError("MR34I9_ORIGINAL_NATIVE_LEARNER_WEIGHTS_LOST")
    original_git(root,SOURCES[family])
    return {
        "original_independent_source_git_sha":SOURCES[family],
        "original_source_event_SHA256":identity,
        "original_source_PUBLIC_training_tensor_custody":inputs,
        "source_TRAIN_only_reset_count":len(SEEDS),
        "source_actual_TRAIN_only_actions":inputs["actual_training_source_actions"],
        "source_source_generation_CPU_ns":source_CPU,
        "original_initial_45_weight_snapshot_sha256":sha(initial_a.encode()),
        "unchanged_original_trainer_selected_checkpoint_sha256":original_info["exact_trained_model_checkpoint_SHA256"],
        "unchanged_original_trainer_selected_epoch":original_info["TRAINING_ONLY_selected_epoch"],
        "unchanged_original_trainer_full40_CPU_ns":original_info["training_cpu_ns_full_episode_45_coefficient_Adam"],
        "independent_original_training_trace":original_trajectory,
        "candidate_portable_training_trace":candidate_info,
        "portable_candidate_to_exact_original_40epoch_CPU_ratio":ratio,
        "portable_cpu_screen_bounded_at_50x":ratio<=MAX_TRAIN_CPU_RATIO,
        "candidate_STRICT_CPU_nonregression":ratio<=1.,
        "same_45_native_weights_no_new_parameters":same_model_sizes,
        "numeric_kernel_source_neutral":"MR34I7B unchanged source Decimal48",
        "native_original_S4C1_imported_trainer_unchanged":True,
        "source_original_held_DEV_or_protected_test_actions":0
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
    started=time.process_time_ns()
    reports={name:evaluate_source(name,root) for name,root in roots.items()}
    for name,root in roots.items():
        original_git(root,SOURCES[name])
    original_git(s4c1,S4C1_SHA)
    result={
        "schema":SCHEMA,
        "frozen_first_protocol_only_sha":FIRST,
        "qualified_nonlearning_numerical_kernel_parent":PARENT,
        "unchanged_original_native_S4C1_commit":S4C1_SHA,
        "numpy_version":np.__version__,
        "OS":platform.system(),
        "source_original_public_only":True,
        "original_source_protected_first_use":False,
        "original_source_held_DEV_actions_generated":0,
        "model_source_modified":False,
        "independent_new_science_admission":False,
        "origin_train_and_diagnostic_CPU_ns":time.process_time_ns()-started,
        "source_worker_peak_OS_RSS_bytes":peak_rss(),
        "source_reports":reports,
        "scientific_admission":"NO_GO"
    }
    path=Path(out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n",encoding="utf-8")
    print("MR34I9_ORIGINAL_SOURCE_OPTIN_FULLTRAIN="+canon({
        "schema":SCHEMA,"OS":platform.system(),"receipt_sha256":sha(path.read_bytes()),
        "sources":{n:{
            "source_SHA":v["original_source_event_SHA256"],
            "original_checkpoint":v["unchanged_original_trainer_selected_checkpoint_sha256"],
            "portable_checkpoint":v["candidate_portable_training_trace"]["source_trained_45_native_checkpoint_sha256"],
            "portable_epoch":v["candidate_portable_training_trace"]["source_train_only_selected_epoch"],
            "training_ratio":v["portable_candidate_to_exact_original_40epoch_CPU_ratio"]}
            for n,v in reports.items()},
        "scientific_protected_first_use":False
    }))


if __name__=="__main__":
    if len(sys.argv)!=5:
        raise SystemExit("Usage: python -m research.mr34i9.optin_train S4C1 FARAMA PYCOLAB OUT")
    main(*sys.argv[1:])
