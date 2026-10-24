"""MR34I12: prospective TRAIN-only full recurrent deterministic projection/exp.

This harness never mutates any original S4C1 native learner, historical
Decimal48/Q160 kernels or authentic original-source environment.
"""
from __future__ import annotations

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
from research.mr34i9.optin_train import (
    exact_frozen_optimizer,ORIGINAL_EVENT_SHA)
from research.mr34i10.fixed160_train import (
    make_fast_class,source_corpus,DECIMAL48_PROVEN_CHECKPOINT,
    DECIMAL48_PROVEN_EPOCH,fixed160_sigmoid)

SCHEMA="mass.mr34i12.full-recurrent-portable-u-and-q160-original-train.v1"
FIRST="84790ee328d3f4c3ba8fbe6c8f9077f7844ba8fc"
PARENT="f37da027ab92618c21d47fd2a50c46d949ef6bca"
MAX_TO_NUMPY=2.50
MAX_TO_DECIMAL48=1.00
MAX_TRAIN_BRIER_DAMAGE=.01


def fsum_native_read_u(f,g,roles,s):
    """Read-only-compatible but opt-in native recurrent exact scalar projections."""
    if (f.shape!=(8,7) or g.shape!=(3,7) or roles.shape!=(8,3)
        or s.shape!=(8,) or not all(np.isfinite(x).all()
                              for x in (f,g,roles,s))):
        raise ValueError("MR34I12_ORIGINAL_NATIVE_SHAPE_OR_NONFINITE_STATE")
    read=np.asarray([
        math.fsum([float(f[i,j])*float(g[1,j]) for j in range(7)]+
                  [float(roles[i,1])])
        for i in range(8)],dtype=np.float64)
    u=np.asarray([
        math.fsum([float(f[i,j])*float(g[0,j]) for j in range(7)]+
                  [float(roles[i,0]),float(s[i])*float(read[i])])
        for i in range(8)],dtype=np.float64)
    return read,u


def make_recurrent_candidate():
    Fast,Decimal,Original=make_fast_class()
    from research.nci04_s4c1.native_predictive_quotient import (
        cell_public_features,N)
    class RecurrentFsumQ160Native45(Original):
        """Opt-in only; original genotype/analytic BPTT is wholly inherited."""

        def forward(self,episode,zero_state=False,permuted_roles=False,cache=False):
            self._validate_params()
            if not episode or type(zero_state) is not bool or type(permuted_roles) is not bool:
                raise ValueError("MR34I12_INVALID_SOURCE_EPISODE_OR_FLAG")
            roles=(self.roles[[0,2,4,6,1,3,5,7]].copy()
                   if permuted_roles else self.roles)
            s=np.zeros(N,dtype=np.float64)
            ps=[]
            details=[]
            for row in episode:
                f=cell_public_features(row[0])
                used_s=np.zeros(N,dtype=np.float64) if zero_state else s
                read,u=fsum_native_read_u(f,self.g,roles,used_s)
                p=np.asarray([fixed160_sigmoid(z) for z in u],dtype=np.float64)
                next_s=np.tanh(f@self.g[2]+roles[:,2]*(2.*p-1.))
                if not np.isfinite(next_s).all() or np.max(np.abs(next_s))>1.:
                    raise ValueError("MR34I12_NATIVE_PREDICTIVE_STATE_NONFINITE")
                ps.append(p)
                if cache:
                    details.append((f,used_s.copy(),read,p,next_s.copy()))
                s=next_s
            a=np.asarray(ps,dtype=np.float64)
            return (a,details) if cache else a
    return RecurrentFsumQ160Native45,Fast,Decimal,Original


def evaluate_original_source(family,root):
    from research.mr34f.prospective_controls import episodes,SOURCES as ORIGINALS
    from research.nci04_s4c1.original_native_predictive_state import (
        TRAIN,train_native,protocol,score
    )
    if tuple(TRAIN)!=SEEDS or len(SEEDS)!=20 or ORIGINALS[family][0]!=SOURCES[family]:
        raise ValueError("MR34I12_ORIGINAL_SOURCE_ROLE_OR_MODEL_DRIFT")
    protocol()
    source_start=time.process_time_ns()
    episodes_data,original_events=episodes(root,family,SEEDS)
    source_cpu=time.process_time_ns()-source_start
    src_digest=sha(canon(original_events).encode())
    if src_digest!=ORIGINAL_EVENT_SHA[family] or len(episodes_data)!=20:
        raise ValueError("MR34I12_ORIGINAL_AUTHORED_ACTION_AND_NEXT_TARGET_DRIFT")
    source_tensors=source_episode_inputs(episodes_data)
    Fsum,Fast,Decimal,Original=make_recurrent_candidate()
    snapshots=[c().snapshot() for c in (Fsum,Fast,Decimal,Original)]
    if len(set(snapshots))!=1:
        raise ValueError("MR34I12_ORIGINAL_INITIAL_GENOTYPE_CHANGED")
    # Observe, and preserve, original NumPy first-u drift from historical cases;
    # the new source-neutral mechanism must never erase this negative.
    original_first_u=source_corpus(episodes_data,Original)
    original_first_u_sha=sha(raw(original_first_u))
    first_old_u_equal=original_first_u_sha==EXPECTED[family]
    imported_model,imported_original=train_native(episodes_data)
    original_copy,original=exact_frozen_optimizer(Original(),episodes_data)
    if (imported_model.snapshot()!=original_copy.snapshot() or
        imported_original["TRAINING_ONLY_selected_epoch"]!=original["source_train_only_selected_epoch"] or
        imported_original["source_native_training_first_last_best_Brier"]!=[
            original["original_train_only_epoch_Brier"][0],
            original["original_train_only_epoch_Brier"][-1],
            original["original_train_only_best_Brier"]]):
        raise RuntimeError("MR34I12_IMPORTED_ORIGINAL_NATIVE_TRAINER_SEMANTIC_PARITY_FAILED")

    reference_model,reference=exact_frozen_optimizer(Decimal(),episodes_data)
    if (reference["source_trained_45_native_checkpoint_sha256"]!=
        DECIMAL48_PROVEN_CHECKPOINT[family] or
        reference["source_train_only_selected_epoch"]!=
        DECIMAL48_PROVEN_EPOCH[family]):
        raise RuntimeError("MR34I12_FROZEN_PRIOR_DECIMAL48_REPRODUCIBILITY_DRIFT")
    fast_model,fast=exact_frozen_optimizer(Fast(),episodes_data)
    candidate_model,candidate=exact_frozen_optimizer(Fsum(),episodes_data)

    def accuracy(model):
        outputs=[model.forward(ep) for ep in episodes_data]
        val,_=score(outputs,episodes_data)
        return float(val)
    # Selected training-only model predictions. No protected development scores.
    select_accuracy={
        "original_numpy":accuracy(imported_model),
        "portable_Decimal48":accuracy(reference_model),
        "portable_Q160":accuracy(fast_model),
        "candidate_fsum_Q160":accuracy(candidate_model)
    }
    q_cpu=candidate["training_CPU_ns_40epochs_source_excluded"]
    original_cpu=imported_original["training_cpu_ns_full_episode_45_coefficient_Adam"]
    decimal_cpu=reference["training_CPU_ns_40epochs_source_excluded"]
    if min(q_cpu,original_cpu,decimal_cpu)<=0:
        raise RuntimeError("MR34I12_UNMEASURABLE_ORIGINAL_SOURCE_TRAINING_CPU")
    q_to_numpy=q_cpu/original_cpu
    q_to_decimal=q_cpu/decimal_cpu
    q_to_q160=q_cpu/max(1,fast["training_CPU_ns_40epochs_source_excluded"])
    brier_delta=select_accuracy["candidate_fsum_Q160"]-select_accuracy["portable_Q160"]
    q_valid=(candidate["source_actual_training_updates"]==800 and
             candidate["exact_native_45_weights"] is True and
             len(candidate["original_train_only_epoch_Brier"])==40 and
             candidate["source_native_gradient_finite_difference"]["passed"])
    original_git(root,SOURCES[family])
    return {
        "original_authored_source_git_sha":SOURCES[family],
        "original_original_action_target_receipt_SHA256":src_digest,
        "original_public_source_23_69_8_tensors":source_tensors,
        "original_native_initial_genotype_SHA256":sha(snapshots[0].encode()),
        "previously_consumed_training_only_reset_count":len(SEEDS),
        "original_source_generation_CPU_ns":source_cpu,
        "original_first160_native_u_SHA256":original_first_u_sha,
        "historical_initial_u_SHA256_expected":EXPECTED[family],
        "original_native_u_history_matches":first_old_u_equal,
        "original_imported_trainer_local_parity":True,
        "unchanged_original_native_checkpoint_SHA256":imported_original["exact_trained_model_checkpoint_SHA256"],
        "original_full40_native_copy":original,
        "reference_Decimal48_full40":reference,
        "prior_Q160_full40":fast,
        "new_fsum_Q160_full40":candidate,
        "TRAIN_only_selected_model_Brier":select_accuracy,
        "candidate_Brier_minus_prior_Q160":brier_delta,
        "candidate_to_unmodified_original_CPU_ratio":q_to_numpy,
        "candidate_to_qualified_Decimal48_CPU_ratio":q_to_decimal,
        "candidate_to_prior_Q160_CPU_ratio":q_to_q160,
        "candidate_CPU_budget_both_sources_frozen":q_to_numpy<=MAX_TO_NUMPY and q_to_decimal<=MAX_TO_DECIMAL48,
        "candidate_TRAIN_only_selected_Brier_nonregression_screen":brier_delta<=MAX_TRAIN_BRIER_DAMAGE,
        "candidate_original_source_full40_valid":q_valid,
        "original_native_source_or_prior_candidate_unchanged":True,
        "actual_original_source_protected_first_use_or_DEV_actions":0
    }


def main(original,farama,pycolab,receipt_file):
    original_git(original,S4C1_SHA)
    roots={
        "FaramaMiniGridDoorKey8":original_git(farama,SOURCES["FaramaMiniGridDoorKey8"]),
        "DeepMindPycolabApprehend":original_git(pycolab,SOURCES["DeepMindPycolabApprehend"])
    }
    sys.path.insert(0,str(Path(original).resolve()))
    for root in roots.values():
        sys.path.insert(0,str(root))
    from research.mr27.natural_memory import source_guard
    source_guard(roots["FaramaMiniGridDoorKey8"])
    start=time.process_time_ns()
    source_reports={name:evaluate_original_source(name,path) for name,path in roots.items()}
    for name,path in roots.items():
        original_git(path,SOURCES[name])
    original_git(original,S4C1_SHA)
    receipt={
        "schema":SCHEMA,"frozen_PRECODE_original_protocol":FIRST,
        "MR34I11_unchanged_parent":PARENT,"pinned_S4C1_original_native_git":S4C1_SHA,
        "source_reports":source_reports,"OS":platform.system(),
        "numpy_version":np.__version__,"Python":platform.python_version(),
        "native_original_and_prior_numeric_implementations_untouched":True,
        "original_protected_or_DEV_first_use":False,
        "actual_whole_source_native_training_CPU_ns":time.process_time_ns()-start,
        "whole_worker_OS_peak_RSS_bytes":peak_rss(),
        "scientific_admission":"NO_GO",
    }
    p=Path(receipt_file);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(receipt,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n",encoding="utf-8")
    print("MR34I12_ORIGINAL_FULL_RECURRENCE="+canon({
        "schema":SCHEMA,"os":platform.system(),
        "receipt_sha256":sha(p.read_bytes()),
        "source_reports":{name:{
            "event_digest":z["original_original_action_target_receipt_SHA256"],
            "original_u_drift":not z["original_native_u_history_matches"],
            "candidate_checkpoint":z["new_fsum_Q160_full40"]["source_trained_45_native_checkpoint_sha256"],
            "candidate_epoch":z["new_fsum_Q160_full40"]["source_train_only_selected_epoch"],
            "baseline_Brier":z["TRAIN_only_selected_model_Brier"]["portable_Q160"],
            "candidate_Brier":z["TRAIN_only_selected_model_Brier"]["candidate_fsum_Q160"],
            "candidate_CPU_to_numpy":z["candidate_to_unmodified_original_CPU_ratio"],
            "candidate_CPU_to_decimal":z["candidate_to_qualified_Decimal48_CPU_ratio"],
            "candidate_CPU_to_Q160":z["candidate_to_prior_Q160_CPU_ratio"]}
            for name,z in source_reports.items()},
        "original_protected_first_use":False
    }))


if __name__=="__main__":
    if len(sys.argv)!=5:
        raise SystemExit("Usage: python -m research.mr34i12.portable_recurrent ORIGINAL_S4C1 FARAMA PYCOLAB RECEIPT")
    main(*sys.argv[1:])
