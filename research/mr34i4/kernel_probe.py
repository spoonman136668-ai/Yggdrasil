"""MR34I4: source-original nonlearning sigmoid kernel reproducibility.

The original native S4C1 model is imported unchanged. All original source
episodes have been consumed as TRAINING DEVELOPMENT in MR34I1-3. This script
does not update any parameters, select checkpoints, access heldout data or
consume unfamiliar first-use source. Decimal reference is a standalone
diagnostic, NOT a replacement of original native learning semantics.
"""
import json
import math
import os
import platform
import random
import struct
import subprocess
import sys
import time
from decimal import Decimal, localcontext, Context, ROUND_HALF_EVEN
from hashlib import sha256
from pathlib import Path

import numpy as np
import psutil

FILE=Path(__file__).with_name("frozen_protocol.json")
S4C1="8e1561eb1a542e21307bac669c42435cf48e59bd"
SOURCES={
 "FaramaMiniGridDoorKey8":"7f5853792ea7f04f75614661006d87fcf949f26d",
 "DeepMindPycolabApprehend":"6504c8065dd5322438f23a2a9026649904f3322a",
}
TRAIN=(1861,1867,1871,1873,1877,1879,1889,1901,1907,1913,
       1931,1933,1949,1951,1973,1979,1987,1993,1997,1999)
HELD=(2003,2011,2017,2027,2029,2039,2053,2063)

def sha(x):return sha256(x).hexdigest()
def canon(obj):return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False)
def bits(v):return struct.pack("<d",float(v)).hex()
def bitvalue(v):return struct.unpack("<Q",struct.pack("<d",float(v)))[0]
def pack(a):return b"".join(struct.pack("<d",float(v)) for v in a)
def exact(root,sha_expected):
    root=Path(root).resolve()
    if not root.is_dir():raise ValueError("MR34I4_MISSING_ORIGINAL_GIT_CHECKOUT")
    actual=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip()
    if actual!=sha_expected or dirty:
        raise ValueError("MR34I4_ORIGINAL_PIN_OR_DIRTY_WORKTREE")
    return root

def frozen():
    p=json.loads(FILE.read_text(encoding="utf-8"))
    q=p["canonical_test_inputs"]
    base=("-0x1.1800000000000p+5","-0x1.0000000000000p+5",
          "-0x1.0000000000000p+4","-0x1.0000000000000p+2",
          "-0x1.0000000000000p+0","-0x1.0000000000000p-3",
          "-0x0.0p+0","0x0.0p+0","0x1.0000000000000p-3",
          "0x1.0000000000000p+0","0x1.0000000000000p+2",
          "0x1.0000000000000p+4","0x1.0000000000000p+5",
          "0x1.1800000000000p+5")
    if (p["schema"]!="yggdrasil.mr34i4.original_sigmoid_nonlearning_numerical_oracle.v1"
        or p["exact_original_MR34I3_parent"]!="d01fed0738e44dce8753c00c7cca30f258a3385b"
        or p["original_unedited_model_source"]!=S4C1
        or p["authentic_source_original_commits"]!=SOURCES
        or p["reused_only_original_source_training_seeds"]!=list(TRAIN)
        or p["prohibited_held_development_seeds"]!=list(HELD)
        or tuple(q["frozen_base_binary64_hex"])!=base
        or q["frozen_seeded_random_input_count"]!=128
        or q["scalar_vector_block_size"]!=8
        or p["decimal_precision_digits"]!=80
        or len(p["comparison_candidates"])!=4
        or p["strict_safety"]!={k:True for k in (
            "no_original_model_source_patch","no_gradient_or_weight_training",
            "no_retraining_or_precision_change","no_new_seed_or_scientific_first_use",
            "no_held_or_third_source_executed","no_API_spend","no_merge",
            "no_trading_or_controller_actions")}):
        raise ValueError("MR34I4_FROZEN_KERNEL_PROTOCOL_DRIFT")
    return p

def static_cases(p):
    q=p["canonical_test_inputs"]
    cases=[]
    for literal in q["frozen_base_binary64_hex"]:
        value=float.fromhex(literal)
        cases.extend((value,float(np.nextafter(np.float64(value),np.float64(-np.inf))),
                      float(np.nextafter(np.float64(value),np.float64(np.inf)))))
    actor=random.Random(341234)
    random_values=[actor.uniform(-35.,35.) for _ in range(128)]
    return cases,random_values

def original_source_u(path,name):
    from research.mr34f.prospective_controls import episodes,canon as sourcecanon
    from research.nci04_s4c1.original_native_predictive_state import protocol as source_protocol, TRAIN as source_train
    from research.nci04_s4c1.native_predictive_quotient import (
        NativePredictiveQuotient45,cell_public_features)
    if tuple(source_train)!=TRAIN:raise ValueError("MR34I4_ORIGINAL_SOURCE_TRAIN_COHORT_DRIFT")
    source_protocol()
    ep,receipts=episodes(path,name,TRAIN)
    if len(ep)!=20:raise ValueError("MR34I4_SOURCE_EPISODE_COHORT_INCOMPLETE")
    native=NativePredictiveQuotient45()
    state_before=native.snapshot()
    logits=[]
    first_predictions=[]
    for episode in ep:
        first=episode[0]
        f=cell_public_features(first[0])
        read=f@native.g[1]+native.roles[:,1]
        u=f@native.g[0]+native.roles[:,0]+np.zeros(8)*read
        original_pred=native.forward([first])[0]
        mirrored=1./(1.+np.exp(-np.clip(u,-35.,35.)))
        if not np.array_equal(original_pred.view(np.uint64),mirrored.view(np.uint64)):
            raise ValueError("MR34I4_ACTUAL_UNCHANGED_NATIVE_FORWARD_NOT_REPRODUCED")
        if u.dtype!=np.float64 or u.shape!=(8,) or not np.isfinite(u).all():
            raise ValueError("MR34I4_NATIVE_PUBLIC_LOGIT_INVALID")
        logits.extend(float(x) for x in u)
        first_predictions.extend(float(x) for x in original_pred)
    if native.snapshot()!=state_before or native.train_updates!=0:
        raise ValueError("MR34I4_NO_TRAINING_OR_NATIVE_MUTATION")
    return logits,{
        "original_training_only_episode_count":len(ep),
        "original_source_genuine_action_count":sum(len(e) for e in ep),
        "source_native_training_public_action_receipts_sha256":sha(sourcecanon(receipts).encode()),
        "initial_original_untrained_45coefficient_checkpoint_sha256":sha(state_before.encode()),
        "source_first_preaction_original_forward_probability_bits_sha256":sha(pack(first_predictions)),
        "source_original_first_preaction_logit_binary64_sha256":sha(pack(logits)),
        "source_private_features_delivered_to_probe":False
    }

def decimal_probability(clipped):
    with localcontext(Context(prec=80,rounding=ROUND_HALF_EVEN)):
        z=Decimal.from_float(float(clipped))
        p=Decimal(1)/(Decimal(1)+(-z).exp())
        return float(p)

def evaluate_group(label,u):
    # Original expression always evaluates a FLOAT64 eight-wide vector and
    # never modifies the real S4C1 model's original source forward kernel.
    if len(u)%8!=0:
        # Precisely only last group is zero padded, and padding is reported.
        missing=8-len(u)%8
        values=list(u)+[0.]*missing
    else:
        missing=0
        values=list(u)
    a=np.asarray(values,dtype=np.float64)
    if not np.all(np.isfinite(a)):
        raise ValueError("MR34I4_SOURCE_NONFINITE_KERNEL_INPUT")
    start=time.process_time_ns()
    clipped=np.clip(a,-35.,35.)
    neg=-clipped
    # SOURCE ORIGINAL numpy eight-wide path, not altered/rewritten.
    vector_exp=np.empty_like(a)
    original_p=np.empty_like(a)
    for k in range(0,len(a),8):
        c=a[k:k+8]
        z=np.clip(c,-35.,35.)
        v=np.exp(-z)
        pp=1./(1.+v)
        vector_exp[k:k+8]=v
        original_p[k:k+8]=pp
    vector_cpu=time.process_time_ns()-start
    np_scalar_exp=[]
    math_exp=[]
    np_scalar_p=[]
    math_p=[]
    decimal_p=[]
    reference_cpu=0
    for c in clipped:
        nv=np.exp(np.float64(-c))
        mv=math.exp(float(-c))
        np_scalar_exp.append(float(nv))
        math_exp.append(float(mv))
        np_scalar_p.append(float(np.float64(1.)/(np.float64(1.)+nv)))
        math_p.append(1./(1.+mv))
        t=time.process_time_ns()
        decimal_p.append(decimal_probability(c))
        reference_cpu+=time.process_time_ns()-t
    results={
      "input_logit":list(a),
      "numpy_vector_clip":list(clipped),
      "numpy_vector_negative_clip":list(neg),
      "numpy_original_eightwide_exp":list(vector_exp),
      "numpy_original_eightwide_sigmoid":list(original_p),
      "numpy_scalar_exp":np_scalar_exp,
      "numpy_scalar_sigmoid":np_scalar_p,
      "system_math_exp":math_exp,
      "system_math_sigmoid":math_p,
      "decimal_80digit_nearest_binary64_sigmoid":decimal_p,
    }
    data={name:pack(seq).hex() for name,seq in results.items()}
    ulps=[abs(bitvalue(x)-bitvalue(y)) for x,y in zip(original_p,decimal_p)]
    if (not all(math.isfinite(v) and 0<=v<=1 for v in original_p) or
        not all(math.isfinite(v) and 0<=v<=1 for v in decimal_p)):
        raise ValueError("MR34I4_NONFINITE_PROBABILITY")
    return {
        "cohort":label,
        "real_unpadded_input_count":len(u),
        "padded_source_inert_zero_input_count":missing,
        "original_input_corpus_binary64_sha256":sha(pack(u)),
        "all_float64_stage_bytearrays_hex":data,
        "per_cohort_stage_SHA256":{key:sha(bytes.fromhex(s)) for key,s in data.items()},
        "original_vector_vs_high_precision_oracle_max_ULP_distance":max(ulps),
        "original_vector_vs_high_precision_oracle_nonzero_ULP_count":sum(v>0 for v in ulps),
        "oracle_precision_digits":80,
        "original_vector_kernel_process_cpu_ns":vector_cpu,
        "decimal_only_reference_cpu_ns":reference_cpu,
        "no_model_training_or_optimizer":True,
    }

def peak_rss():
    if sys.platform=="win32":
        mem=getattr(psutil.Process().memory_info(),"peak_wset",None)
        if not mem:raise ValueError("MR34I4_WINDOWS_PROCESS_PEAK_RSS_UNAVAILABLE")
        return int(mem)
    if sys.platform.startswith("linux"):
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1024
    raise ValueError("MR34I4_SOURCE_OS_UNSUPPORTED")

def main(modelroot,farama,pycolab):
    p=frozen()
    original_model=exact(modelroot,S4C1)
    paths={
        "FaramaMiniGridDoorKey8":exact(farama,SOURCES["FaramaMiniGridDoorKey8"]),
        "DeepMindPycolabApprehend":exact(pycolab,SOURCES["DeepMindPycolabApprehend"])}
    sys.path.insert(0,str(original_model))
    for x in paths.values():sys.path.insert(0,str(x))
    from research.mr27.natural_memory import source_guard
    source_guard(paths["FaramaMiniGridDoorKey8"])
    start=time.process_time_ns()
    base,random_inputs=static_cases(p)
    cohorts=[("canonical_frozen_boundaries",base,None),
             ("canonical_seeded_binary64_inputs",random_inputs,None)]
    for family,path in paths.items():
        logits,source_evidence=original_source_u(path,family)
        cohorts.append((family,logits,source_evidence))
    sections=[]
    for label,values,evidence in cohorts:
        v=evaluate_group(label,values)
        # Avoid fragile/truncated giant single GitHub log lines. Emit each
        # raw data section separately, and a concise final summary.
        raw=v.pop("all_float64_stage_bytearrays_hex")
        print("MR34I4_BINARY64_ORIGINAL_KERNEL_SECTION="+canon({
            "cohort":label,
            "exact_original_input_and_stage_float64_bytearray_hex":raw}))
        if evidence is not None:v["original_independent_source_custody"]=evidence
        sections.append(v)
    for root in paths.values():exact(root,SOURCES[
       next(k for k,val in paths.items() if val==root)])
    exact(original_model,S4C1)
    print("MR34I4_ORIGINAL_SIGMOID_NUMERICAL_REFERENCE="+canon({
        "frozen_before_code_protocol_sha256":sha(FILE.read_bytes()),
        "original_model_git_sha":S4C1,
        "development_ONLY_nonlearning_kernel_sections":sections,
        "canonical_input_sets_source_independent":True,
        "original_source_dev_inputs_untuned_and_unlearned":True,
        "no_frozen_checkpoint_modified_or_promoted":True,
        "all_source_and_reference_worker_process_cpu_ns":time.process_time_ns()-start,
        "whole_original_sources_and_numeric_reference_worker_OS_peak_RSS":peak_rss(),
        "user_protected_scientific_first_use_consumed":False,
        "third_source_unfamiliar_task_not_executed":True,
        "original_S4C1_training_source_not_changed":True,
        "cross_job_numeric_kernel_admission":"PENDING_FOUR_INDEPENDENT_OS_JOB_EVIDENCE_COMPARISON",
        "cognitive_transfer_scientific_admission":"NO_GO",
        "G29_atlas_and_full_OS_regressions":"FAIL_CLOSED",
    }))

if __name__=="__main__":
    if len(sys.argv)!=4:
        raise SystemExit("Use: python audit/research/mr34i4/kernel_probe.py ORIGINAL_S4C1 ORIGINAL_FARAMA ORIGINAL_PYCOLAB")
    main(*sys.argv[1:])
