"""MR34I7: preregistered portable NUMERICAL SIGMOID kernel trial, NONLEARNING.

Independent first-use is untouched. Exact original MR34I4 public-source cohort
is reused; native Yggdrasil model and independently authored engines are
pinned and READ ONLY. Candidate Decimal48 is NOT installed into original
model, and 80-digit same-family reference is not mathematical proof.
"""
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from hashlib import sha256
import json
from pathlib import Path
import math
import os
import platform
import statistics
import subprocess
import sys
import time

import numpy as np

PROTO=Path(__file__).with_name("frozen_protocol.json")
ORIGINAL_S4C1="8e1561eb1a542e21307bac669c42435cf48e59bd"
ORIGINAL_SOURCES={
 "FaramaMiniGridDoorKey8":"7f5853792ea7f04f75614661006d87fcf949f26d",
 "DeepMindPycolabApprehend":"6504c8065dd5322438f23a2a9026649904f3322a"
}
EXPECTED={
 "canonical_frozen_boundaries":"d6e87d59c48e7a464f564ecaeb7c7f8d5282755fa67e9a9725617f7f9ea21718",
 "canonical_seeded_binary64_inputs":"1012ca50ca7f8a14444535c922d88a91ece8f0362a1979b73d08aff146d22b9b",
 "FaramaMiniGridDoorKey8":"ba501812452b529cf35d4aaa176f9d5a0b5cfbb57a388d67c49dfbc547109486",
 "DeepMindPycolabApprehend":"23d9db17d29ed9646afac1b34000d0be320c2fa50ca424db2f85f1829be11bd7",
}
def sha(v):return sha256(v).hexdigest()
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def raw(a):return np.asarray(a,dtype="<f8").tobytes(order="C")
def bits(v):return np.float64(v).tobytes().hex()
def ulp(a,b):
    # Outputs constrained to [0,1], so the IEEE754 unsigned binary64 bit
    # distance is the exact nonnegative-integer ULP spacing.
    from struct import unpack
    return abs(unpack("<Q",raw([a]))[0]-unpack("<Q",raw([b]))[0])

def check_git(root,expected):
    root=Path(root).resolve()
    if (subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()!=expected
        or subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip()):
        raise ValueError("MR34I7_ORIGINAL_SOURCE_GIT_SHA_OR_WORKTREE_DIRTY")
    return root

def contract():
    p=json.loads(PROTO.read_text(encoding="utf-8"))
    a=p["precommitted_acceptance"]
    if (p["schema"]!="nci04.mr34i7.portable_nonlearning_sigmoid_candidate.v1"
        or p["exact_predecessor_MR34I6_SHA"]!="cb8f61f54b49663962de59c36dbd62a7eb33e08e"
        or p["exact_original_S4C1_SHA"]!=ORIGINAL_S4C1
        or p["exact_original_authored_sources"]!=ORIGINAL_SOURCES
        or p["exact_source_input_SHA256"]!=EXPECTED
        or p["candidate_kernel"]["id"]!="decimal48_source_neutral_nonlearning_sigmoid"
        or a["measured_cost"].find("16 repeated")<0
        or p["no_original_model_patch"] is not True
        or p["no_weight_update_or_adam_training"] is not True
        or p["no_protected_held_source_task"] is not True
        or p["no_native_cognitive_transfer_claim"] is not True):
        raise ValueError("MR34I7_FROZEN_PRECODE_PROTOCOL_INVALID")
    return p

def portable_decimal(vals,precision):
    with localcontext(Context(prec=precision,rounding=ROUND_HALF_EVEN)):
        one=Decimal(1)
        ans=[]
        for x in vals:
            x=float(x)
            if not math.isfinite(x):
                raise ValueError("MR34I7_NONFINITE_ORIGINAL_SOURCE_U")
            clamped=max(-35.0,min(35.0,x))
            z=Decimal.from_float(clamped)
            ans.append(float(one/(one+(-z).exp())))
    return ans

def unchanged_numpy_original(vals):
    # Original float64 vector 8-wide NumPy source-native operation. Only the
    # final nonphysical partial block uses inert zero padding, excluded.
    expected=len(vals)
    result=[]
    for i in range(0,expected,8):
        block=list(vals[i:i+8])
        length=len(block)
        if length<8:block.extend([0.0]*(8-length))
        x=np.asarray(block,dtype=np.float64)
        p=1./(1.+np.exp(-np.clip(x,-35.,35.)))
        result.extend(float(v) for v in p[:length])
    return result

def benchmark(fn,values):
    for _ in range(3):fn(values)
    samples=[]
    for _ in range(16):
        start=time.process_time_ns()
        fn(values)
        samples.append(time.process_time_ns()-start)
    if not all(x>0 for x in samples):
        raise ValueError("MR34I7_UNMEASURED_PROCESS_CPU")
    return {"trial16_process_CPU_ns":samples,
            "median_single_490case_cohort_CPU_ns":int(statistics.median(samples)),
            "sum16_process_CPU_ns":sum(samples)}

def run_group(name,values,source_receipt=None):
    blob=raw(values)
    if sha(blob)!=EXPECTED[name]:
        raise ValueError("MR34I7_ORIGINAL_SOURCE_FLOAT64_INPUT_DRIFT_"+name)
    original=unchanged_numpy_original(values)
    candidate=portable_decimal(values,48)
    oracle=portable_decimal(values,80)
    if not(len(original)==len(candidate)==len(oracle)==len(values)):
        raise ValueError("MR34I7_CANDIDATE_SOURCE_PREDICTION_SHAPE_INVALID")
    if any(not(0.0<=x<=1.0 and math.isfinite(x))
           for series in (original,candidate,oracle) for x in series):
        raise ValueError("MR34I7_SIGMOID_NONFINITE_OUT_OF_RANGE")
    distance=[ulp(x,y) for x,y in zip(candidate,oracle)]
    original_distance=[ulp(x,y) for x,y in zip(original,oracle)]
    if name=="canonical_frozen_boundaries":
        order=sorted(zip(values,candidate),key=lambda t:t[0])
        if any(a[1]>b[1] for a,b in zip(order,order[1:])):
            raise ValueError("MR34I7_CANDIDATE_SIGMOID_MONOTONICITY_FAIL")
    orig_t=benchmark(unchanged_numpy_original,values)
    cand_t=benchmark(lambda v:portable_decimal(v,48),values)
    oracle_t=benchmark(lambda v:portable_decimal(v,80),values)
    ratio=cand_t["median_single_490case_cohort_CPU_ns"]/max(
        1,orig_t["median_single_490case_cohort_CPU_ns"])
    first_diff=next((i for i,(x,y) in enumerate(zip(original,candidate))
                     if raw([x])!=raw([y])),None)
    raw_outputs={
        "original_numpy_binary64_hex":raw(original).hex(),
        "portable_decimal48_binary64_hex":raw(candidate).hex(),
        "decimal80_reference_binary64_hex":raw(oracle).hex()}
    print("MR34I7_PORTABLE_KERNEL_RAW_SECTION="+canon({
        "cohort":name,"binary64_source_input_hex":blob.hex(),
        "source_outputs_unrounded_binary64_hex":raw_outputs}))
    result={
      "cohort":name,"original_exact_input_count":len(values),
      "original_input_SHA256":sha(blob),
      "original_NumPy_vector_p_SHA256":sha(raw(original)),
      "portable_decimal48_p_SHA256":sha(raw(candidate)),
      "decimal80_reference_p_SHA256":sha(raw(oracle)),
      "candidate_vs_80_precision_max_ULP":max(distance),
      "candidate_vs_80_precision_nonzero_ULP_count":sum(x>0 for x in distance),
      "original_NumPy_vs_80_precision_max_ULP":max(original_distance),
      "original_NumPy_vs_80_precision_nonzero_ULP_count":sum(x>0 for x in original_distance),
      "first_original_NumPy_vs_portable_candidate_unequal_index":first_diff,
      "original_numpy_benchmark":orig_t,
      "portable_decimal48_benchmark":cand_t,
      "decimal80_reference_benchmark":oracle_t,
      "same_process_candidate_to_original_CPU_median_ratio":ratio,
      "candidate_explicit_accurate_enough":max(distance)<=1,
      "candidate_within_precommitted_same_process_CPU_budget":ratio<=2000,
    }
    if source_receipt is not None:result["original_source_custody"]=source_receipt
    return result

def process_memory():
    import psutil
    mem=psutil.Process().memory_info()
    if sys.platform=="win32":
        value=getattr(mem,"peak_wset",0)
    elif sys.platform.startswith("linux"):
        import resource
        value=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
    else:
        raise ValueError("MR34I7_UNSUPPORTED_ORIGINAL_RUNNER_OS")
    if not value:raise ValueError("MR34I7_MEMORY_COST_NOT_RECORDED")
    return int(value)

def main(s4c1,farama,pycolab):
    contract()
    project=Path(__file__).resolve().parents[2]
    prior=subprocess.check_output(
        ["git","-C",str(project),"rev-parse",
         "43e1fd51fc5cd7193978b527daa67d3f02314db8:research/mr34i4/kernel_probe.py"],text=True).strip()
    current=subprocess.check_output(
        ["git","-C",str(project),"rev-parse","HEAD:research/mr34i4/kernel_probe.py"],text=True).strip()
    if prior!=current:
        raise ValueError("MR34I7_FROZEN_SOURCE_COHORT_GENERATION_CODE_MODIFIED")
    sys.path.insert(0,str(project))
    orig=check_git(s4c1,ORIGINAL_S4C1)
    source_paths={"FaramaMiniGridDoorKey8":check_git(farama,ORIGINAL_SOURCES["FaramaMiniGridDoorKey8"]),
                 "DeepMindPycolabApprehend":check_git(pycolab,ORIGINAL_SOURCES["DeepMindPycolabApprehend"])}
    sys.path.insert(0,str(orig))
    for path in source_paths.values():sys.path.insert(0,str(path))
    from research.mr34i4.kernel_probe import static_cases,original_source_u,frozen as old_frozen
    from research.mr27.natural_memory import source_guard
    source_guard(source_paths["FaramaMiniGridDoorKey8"])
    old_p=old_frozen()
    started=time.process_time_ns()
    boundaries,seeded=static_cases(old_p)
    cohort_values=[("canonical_frozen_boundaries",boundaries,None),
                   ("canonical_seeded_binary64_inputs",seeded,None)]
    for family,path in source_paths.items():
        logits,source_receipt=original_source_u(path,family)
        cohort_values.append((family,logits,source_receipt))
    sections=[run_group(name,vals,receipt) for name,vals,receipt in cohort_values]
    for family,path in source_paths.items():check_git(path,ORIGINAL_SOURCES[family])
    check_git(orig,ORIGINAL_S4C1)
    is_go=all(c["candidate_explicit_accurate_enough"] and
              c["candidate_within_precommitted_same_process_CPU_budget"]
              for c in sections)
    print("MR34I7_PORTABLE_NONLEARNING_SIGMOID_CANDIDATE="+canon({
       "preregistered_before_source_protocol_SHA256":sha(PROTO.read_bytes()),
       "pinned_original_S4C1_unmodified":ORIGINAL_S4C1,
       "candidate_identifier":"decimal48_source_neutral_nonlearning_sigmoid",
       "original_source_and_kernel_cohorts":sections,
       "frozen_candidate_local_accuracy_and_cost_GO":is_go,
       "genuine_original_public_input_cross_OS_reproducibility":"PENDING_FOUR_SOURCE_RECEIPT_COMPARISON",
       "candidate_cross_OS_bitwise_reproducibility":"PENDING_FOUR_SOURCE_RECEIPT_COMPARISON",
       "reference_is_higher_precision_SAME_decimal_algorithm_not_independent_math_proof":True,
       "process_whole_original_source_and_all_kernel_CPU_ns":time.process_time_ns()-started,
       "process_whole_original_source_and_all_kernel_peak_RSS_bytes":process_memory(),
       "native_original_45_coefficient_learner_modified_or_trained":False,
       "source_science_first_use_consumed":False,
       "third_unfamiliar_source_task_executed":False,
       "recurrent_or_cognitive_transfer_scientific_admission":"NO_GO",
       "G29_and_full_project_integration":"FAIL_CLOSED"}))

if __name__=="__main__":
    if len(sys.argv)!=4:
        raise SystemExit("Usage: python -B audit/research/mr34i7/portable_kernel.py S4C1 FARAMA PYCOLAB")
    main(*sys.argv[1:])
