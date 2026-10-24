"""MR34I10 — frozen Q160 sigmoid: faster fully deterministic native TRAIN-only screen.

The original S4C1 learner, 40-epoch source trainer, Decimal48 kernel and
independently authored environments remain immutable. This is engineering
portability validation, NEVER scientific first-use or model promotion.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
from pathlib import Path
import platform
import struct
import sys
import time

import numpy as np

from research.mr34i1.train_only_numeric import (
    SOURCES,SEEDS,S4C1_SHA,original_git,source_episode_inputs,peak_rss,canon,sha)
from research.mr34i7.portable_kernel import (
    EXPECTED,portable_decimal,unchanged_numpy_original,raw,ulp)
from research.mr34i9.optin_train import (
    exact_frozen_optimizer,make_portable_class,ORIGINAL_EVENT_SHA)
from research.mr34i4.kernel_probe import frozen,static_cases

SCHEMA="mass.mr34i10.q160-portable-fast-original-train.v1"
FIRST="ca07d425f16943ecfc3a3731119236465dcbbe22"
PARENT="fb09dd537183bb56ce10a96c27695883fe32cf52"
S=1<<160
MAX_CANDIDATE_TO_DECIMAL_CPU=.75
MAX_CANDIDATE_TO_ORIGINAL_CPU=2.
DECIMAL48_PROVEN_CHECKPOINT={
    "FaramaMiniGridDoorKey8":"be7f00c1ecb8d07c309b09f2bf576a7cfa15fac644ce5d4c92cdb69627466ad5",
    "DeepMindPycolabApprehend":"0673ad49f7c5921595ea17d9005ebe83226cb9d3e3fb8722714c107ec9769119"
}
DECIMAL48_PROVEN_EPOCH={"FaramaMiniGridDoorKey8":40,"DeepMindPycolabApprehend":37}


def fixed160_sigmoid(u):
    """Q160 range-reduced Taylor; source- and library-independent binary64."""
    x=float(u)
    if not math.isfinite(x):
        raise ValueError("MR34I10_Q160_INPUT_NONFINITE")
    x=max(-35.,min(35.,x))
    num,den=abs(x).as_integer_ratio()
    q=((num*S)//den)//128
    value=S
    term=S
    for k in range(1,60):
        term=-(term*q)//(S*k)
        if term==0:
            break
        value+=term
    for _ in range(7):
        value=(value*value)//S
    if not 0<=value<=S:
        raise ValueError("MR34I10_FIXEDPOINT_RANGE_INVALID")
    answer=float((S if x>=0 else value)/(S+value))
    if not(0.<=answer<=1.) or not math.isfinite(answer):
        raise ValueError("MR34I10_Q160_RESULT_NONFINITE")
    return answer


def make_fast_class():
    Portable,Original=make_portable_class()
    from research.nci04_s4c1.native_predictive_quotient import (
        cell_public_features,N)
    class Fixed160Native45(Original):
        """One changed forward op; everything else inherited verbatim."""

        def forward(self,episode,zero_state=False,permuted_roles=False,cache=False):
            self._validate_params()
            if not episode or type(zero_state) is not bool or type(permuted_roles) is not bool:
                raise ValueError("MR34I10_INVALID_ORIGINAL_EPISODE_OR_FLAG")
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
                p=np.asarray([fixed160_sigmoid(z) for z in u],dtype=np.float64)
                next_s=np.tanh(f@self.g[2]+roles[:,2]*(2.*p-1.))
                if not np.all(np.isfinite(next_s)) or np.max(np.abs(next_s))>1.:
                    raise ValueError("MR34I10_NATIVE_RECURRENT_STATE_NONFINITE")
                forecasts.append(p)
                if cache:
                    details.append((f,used_s.copy(),read,p,next_s.copy()))
                s=next_s
            predictions=np.asarray(forecasts,dtype=np.float64)
            return (predictions,details) if cache else predictions
    return Fixed160Native45,Portable,Original


def corpus_screen(cohort,values):
    """Old genuine/edge 490 binary64 corpus; candidate cannot tune to it."""
    got=sha(raw(values))
    if got!=EXPECTED[cohort]:
        raise ValueError("MR34I10_ORIGINAL_490_BINARY64_INPUT_SOURCE_DRIFT_"+cohort)
    out=[fixed160_sigmoid(z) for z in values]
    old=portable_decimal(values,48)
    oracle=portable_decimal(values,80)
    if any(not(0<=v<=1 and math.isfinite(v)) for v in out):
        raise ValueError("MR34I10_NONFINITE_OR_INVALID_OUTPUT")
    if cohort=="canonical_frozen_boundaries":
        pairs=sorted(zip(values,out),key=lambda x:x[0])
        if any(a[1]>b[1] for a,b in zip(pairs,pairs[1:])):
            raise ValueError("MR34I10_BOUNDARY_MONOTONICITY_INVALID")
    fixed_dist=[ulp(a,b) for a,b in zip(out,oracle)]
    old_dist=[ulp(a,b) for a,b in zip(old,oracle)]
    return {
        "cohort":cohort,
        "original_binary64_input_count":len(values),
        "original_binary64_input_sha256":got,
        "fixed160_output_sha256":sha(raw(out)),
        "decimal48_output_sha256":sha(raw(old)),
        "decimal80_reference_output_sha256":sha(raw(oracle)),
        "fixed160_reference_different_binary64_outputs":sum(k!=0 for k in fixed_dist),
        "fixed160_reference_max_ULP":max(fixed_dist),
        "fixed160_decimal48_mismatch_count":sum(raw([a])!=raw([b]) for a,b in zip(out,old)),
        "decimal48_reference_max_ULP":max(old_dist),
        "candidate_490_input_fidelity_PASS":max(fixed_dist)==0 and max(old_dist)==0,
        "independent_correctly_rounded_proof":False,
        "original_source_protected_first_use":False,
    }


def source_corpus(data,Original):
    from research.nci04_s4c1.native_predictive_quotient import cell_public_features
    native=Original()
    before=native.snapshot()
    logits=[]
    for ep in data:
        f=cell_public_features(ep[0][0])
        read=f@native.g[1]+native.roles[:,1]
        u=f@native.g[0]+native.roles[:,0]+np.zeros(8)*read
        actual=native.forward([ep[0]])[0]
        duplicate=1./(1.+np.exp(-np.clip(u,-35.,35.)))
        if not np.array_equal(actual.view(np.uint64),duplicate.view(np.uint64)):
            raise ValueError("MR34I10_ORIGINAL_SOURCE_NATIVE_INITIAL_PROJECTION_DRIFT")
        logits.extend(float(v) for v in u)
    if native.snapshot()!=before or len(logits)!=160:
        raise ValueError("MR34I10_ORIGINAL_NATIVE_INITIAL_SOURCE_INPUT_DRIFT")
    return logits


def source_experiment(family,root):
    from research.mr34f.prospective_controls import episodes,SOURCES as ORIGINALS
    from research.nci04_s4c1.original_native_predictive_state import (
        TRAIN,train_native,protocol)
    protocol()
    if tuple(TRAIN)!=SEEDS or ORIGINALS[family][0]!=SOURCES[family]:
        raise ValueError("MR34I10_FROZEN_ORIGINAL_TRAIN_IDENTITY_DRIFT")
    started=time.process_time_ns()
    data,events=episodes(root,family,SEEDS)
    source_CPU=time.process_time_ns()-started
    digest=sha(canon(events).encode())
    if len(data)!=20 or digest!=ORIGINAL_EVENT_SHA[family]:
        raise ValueError("MR34I10_ORIGINAL_SOURCE_EVENT_OR_RESET_SHA_MISMATCH")
    tensors=source_episode_inputs(data)
    Fixed,Portable,Original=make_fast_class()
    initial=Original().snapshot()
    if initial!=Portable().snapshot() or initial!=Fixed().snapshot():
        raise ValueError("MR34I10_SOURCE_NATIVE_45_INITIAL_WEIGHTS_CHANGED")
    u=source_corpus(data,Original)
    test=frozen()
    edges,random_values=static_cases(test)
    numerical={
        "canonical_frozen_boundaries":corpus_screen("canonical_frozen_boundaries",edges),
        "canonical_seeded_binary64_inputs":corpus_screen("canonical_seeded_binary64_inputs",random_values),
        family:corpus_screen(family,u)
    }
    old,original_info=train_native(data)
    copied,original_copy=exact_frozen_optimizer(Original(),data)
    if (copied.snapshot()!=old.snapshot()
        or original_info["TRAINING_ONLY_selected_epoch"]!=original_copy["source_train_only_selected_epoch"]
        or original_info["source_native_training_first_last_best_Brier"]!=[
            original_copy["original_train_only_epoch_Brier"][0],
            original_copy["original_train_only_epoch_Brier"][-1],
            original_copy["original_train_only_best_Brier"]]):
        raise RuntimeError("MR34I10_ORIGINAL_40EPOCH_TRAINER_LOCAL_SEMANTIC_DRIFT")
    portable,reference=exact_frozen_optimizer(Portable(),data)
    if (reference["source_trained_45_native_checkpoint_sha256"]!=DECIMAL48_PROVEN_CHECKPOINT[family]
        or reference["source_train_only_selected_epoch"]!=DECIMAL48_PROVEN_EPOCH[family]):
        raise RuntimeError("MR34I10_PREVIOUSLY_QUALIFIED_DECIMAL48_REFERENCE_DRIFT")
    fast,candidate=exact_frozen_optimizer(Fixed(),data)
    exact=(
        reference["source_trained_45_native_checkpoint_sha256"]==
            candidate["source_trained_45_native_checkpoint_sha256"]
        and reference["source_train_only_selected_epoch"]==
            candidate["source_train_only_selected_epoch"]
        and reference["original_train_only_epoch_Brier"]==
            candidate["original_train_only_epoch_Brier"]
        and reference["original_train_only_epoch_checkpoint_sha256"]==
            candidate["original_train_only_epoch_checkpoint_sha256"]
        and reference["source_actual_training_updates"]==candidate["source_actual_training_updates"]==800
    )
    if any(report["original_train_only_epoch_Brier"][0]!=
           report["original_train_only_epoch_Brier"][0]
           for report in (original_copy,reference,candidate)):
        raise RuntimeError("MR34I10_UNEXPECTED_NONFINITE_LOSS")
    cpu_decimal=reference["training_CPU_ns_40epochs_source_excluded"]
    cpu_fast=candidate["training_CPU_ns_40epochs_source_excluded"]
    cpu_baseline=original_info["training_cpu_ns_full_episode_45_coefficient_Adam"]
    if min(cpu_decimal,cpu_fast,cpu_baseline)<=0:
        raise RuntimeError("MR34I10_CPU_CLOCK_UNMEASURABLE")
    fraction=cpu_fast/cpu_decimal
    ratio=cpu_fast/cpu_baseline
    all490=all(z["candidate_490_input_fidelity_PASS"] for z in numerical.values())
    original_git(root,SOURCES[family])
    return {
        "original_authored_source_git_sha":SOURCES[family],
        "source_original_public_action_target_SHA256":digest,
        "source_original_23_69_8_public_binary64":tensors,
        "original_source_TRAIN_reset_count":20,
        "original_source_TRAIN_actions":tensors["actual_training_source_actions"],
        "source_original_generation_CPU_ns":source_CPU,
        "original_initial_45_native_snapshot_sha256":sha(initial.encode()),
        "original_490_source_neutral_numeric_fidelity":numerical,
        "all_490_original_numerical_inputs_exact":all490,
        "original_unchanged_native_40epoch_trace":original_copy,
        "original_unchanged_native_selected_checkpoint_sha256":original_info["exact_trained_model_checkpoint_SHA256"],
        "original_imported_trainer_is_bit_equal_to_engineering_copy_same_host":True,
        "portable_decimal48_reference_40epoch_trace":reference,
        "candidate_fixed160_40epoch_trace":candidate,
        "candidate_matches_reference_all40_original_training_byte_exact":exact,
        "candidate_to_Decimal48_training_CPU_ratio":fraction,
        "candidate_to_unmodified_NumPy_training_CPU_ratio":ratio,
        "candidate_le_75pct_decimal48_training_CPU":fraction<=MAX_CANDIDATE_TO_DECIMAL_CPU,
        "candidate_le_2x_NumPy_training_CPU":ratio<=MAX_CANDIDATE_TO_ORIGINAL_CPU,
        "candidate_true_CPU_nonregression_vs_original":ratio<=1.,
        "candidate_frozen_local_screen_pass":(
            all490 and exact and fraction<=MAX_CANDIDATE_TO_DECIMAL_CPU
            and ratio<=MAX_CANDIDATE_TO_ORIGINAL_CPU),
        "original_source_DEV_or_scientific_first_use_actions":0,
        "original_native_source_and_kernel_code_modified":False
    }


def main(s4c1,farama,pycolab,outfile):
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
    results={name:source_experiment(name,root) for name,root in roots.items()}
    for name,root in roots.items():
        original_git(root,SOURCES[name])
    original_git(s4c1,S4C1_SHA)
    receipt={
        "schema":SCHEMA,
        "frozen_original_first_precode_commit":FIRST,
        "MR34I9_exact_qualified_prior":PARENT,
        "unchanged_original_S4C1_git":S4C1_SHA,
        "numpy_version":np.__version__,
        "os":platform.system(),
        "genuine_original_TRAIN_ONLY":True,
        "no_held_or_protected_scientific_first_use":True,
        "native_production_or_earlier_numeric_kernel_modified":False,
        "frozen_Q160_iterations":59,
        "actual_whole_source_training_worker_CPU_ns":time.process_time_ns()-started,
        "whole_worker_OS_peak_resident_bytes":peak_rss(),
        "source_reports":results,
        "scientific_admission":"NO_GO"
    }
    path=Path(outfile)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(receipt,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n",encoding="utf-8")
    print("MR34I10_ORIGINAL_SOURCE_FIXED160_FULLTRAIN="+canon({
        "schema":SCHEMA,"os":platform.system(),"receipt_sha256":sha(path.read_bytes()),
        "sources":{name:{
            "input_sha":r["source_original_public_action_target_SHA256"],
            "original_checkpoint":r["original_unchanged_native_selected_checkpoint_sha256"],
            "decimal48_checkpoint":r["portable_decimal48_reference_40epoch_trace"]["source_trained_45_native_checkpoint_sha256"],
            "fixed160_checkpoint":r["candidate_fixed160_40epoch_trace"]["source_trained_45_native_checkpoint_sha256"],
            "fixed160_exact_40epoch":r["candidate_matches_reference_all40_original_training_byte_exact"],
            "all_original_490_numerical_exact":r["all_490_original_numerical_inputs_exact"],
            "fixed160_to_decimal48_CPU":r["candidate_to_Decimal48_training_CPU_ratio"],
            "fixed160_to_numpy_CPU":r["candidate_to_unmodified_NumPy_training_CPU_ratio"],
            "local_engineering_screen_pass":r["candidate_frozen_local_screen_pass"]}
            for name,r in results.items()},
        "protected_scientific_first_use":False
    }))


if __name__=="__main__":
    if len(sys.argv)!=5:
        raise SystemExit("Usage: python -m research.mr34i10.fixed160_train ORIGINAL_S4C1 FARAMA PYCOLAB OUTPUT")
    main(*sys.argv[1:])
