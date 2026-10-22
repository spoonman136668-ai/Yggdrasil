"""MR34I5: controlled CPU feature-dispatch forensic on original source sigmoid.

The experimental mode is an environment setting applied by GitHub Actions
BEFORE the interpreter imports NumPy. This wrapper calls the exact MR34I4
nonlearning source-reference code, without modifying any native learner,
upstream source, scientific weights, or original binary64 input cohort.
"""
from contextlib import redirect_stdout
from hashlib import sha256
from pathlib import Path
import io
import json
import os
import platform
import subprocess
import sys
import time

# Actual NPY_DISABLE_CPU_FEATURES must already be in environment BEFORE import.
import numpy as np
from numpy.core import _multiarray_umath as numpy_cpu
import psutil

FILE=Path(__file__).with_name("frozen_protocol.json")
ORIGINAL_MR34I4_SHA="43e1fd51fc5cd7193978b527daa67d3f02314db8"
INPUT_SHA={
 "canonical_frozen_boundaries":"d6e87d59c48e7a464f564ecaeb7c7f8d5282755fa67e9a9725617f7f9ea21718",
 "canonical_seeded_binary64_inputs":"1012ca50ca7f8a14444535c922d88a91ece8f0362a1979b73d08aff146d22b9b",
 "FaramaMiniGridDoorKey8":"ba501812452b529cf35d4aaa176f9d5a0b5cfbb57a388d67c49dfbc547109486",
 "DeepMindPycolabApprehend":"23d9db17d29ed9646afac1b34000d0be320c2fa50ca424db2f85f1829be11bd7",
}
SOURCE_MODEL="8e1561eb1a542e21307bac669c42435cf48e59bd"

def sha(v):return sha256(v).hexdigest()
def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),allow_nan=False)

def frozen():
    p=json.loads(FILE.read_text(encoding="utf-8"))
    if (p["schema"]!="yggdrasil.mr34i5.numpy_runtime_feature_control.nonlearning.original.v1"
        or p["exact_predecessor_MR34I4_head_sha"]!=ORIGINAL_MR34I4_SHA
        or p["exact_unmodified_original_S4C1"]!=SOURCE_MODEL
        or p["exact_MR34I4_input_cohorts_sha256"]!=INPUT_SHA
        or p["precommitted_replicas"]["expected_eight_original_native_jobs"]!=8
        or p["precommitted_replicas"]["mode"]!=["default","disable_avx2_fma3"]
        or p["scientific_status"]["protected_first_use_consumed"] is not False):
        raise ValueError("MR34I5_FROZEN_SOURCE_NUMERIC_PROTOCOL_DRIFT")
    return p

def assert_exact_original_MR34I4_source():
    project=Path(__file__).resolve().parents[2]
    former=subprocess.check_output(
        ["git","-C",str(project),"rev-parse",
         ORIGINAL_MR34I4_SHA+":research/mr34i4/kernel_probe.py"],text=True).strip()
    current=subprocess.check_output(
        ["git","-C",str(project),"rev-parse",
         "HEAD:research/mr34i4/kernel_probe.py"],text=True).strip()
    if former!=current:
        raise ValueError("MR34I5_NUMERIC_SOURCE_NATIVE_ORIGINAL_CODE_CHANGED")
    return {"exact_MR34I4_original_source_blob_sha":former,
            "same_original_as_frozen_predecessor":True}

def cpu_dispatch():
    mode=os.environ.get("MR34I5_DISPATCH_MODE","")
    requested=os.environ.get("NPY_DISABLE_CPU_FEATURES")
    if (mode not in ("default","disable_avx2_fma3")
        or os.environ.get("NPY_ENABLE_CPU_FEATURES") is not None):
        raise ValueError("MR34I5_UNPREREGISTERED_CPU_DISPATCH_MODE")
    if mode=="default" and requested is not None:
        raise ValueError("MR34I5_DEFAULT_EXPECTS_UNSET_DISABLE_FEATURES")
    if mode=="disable_avx2_fma3" and requested!="AVX2,FMA3":
        raise ValueError("MR34I5_DISABLED_MODE_NOT_APPLIED_BEFORE_NUMPY_IMPORT")
    if np.__version__!="1.26.4":
        raise ValueError("MR34I5_NUMPY_RUNTIME_PIN_DRIFT")
    flags={str(k):bool(v) for k,v in numpy_cpu.__cpu_features__.items()}
    if not all(k in flags for k in ("AVX2","FMA3")):
        raise ValueError("MR34I5_NUMPY_DISPATCH_FEATURE_INTROSPECTION_UNSUPPORTED")
    if mode=="disable_avx2_fma3" and (flags["AVX2"] or flags["FMA3"]):
        raise ValueError("MR34I5_NUMPY_RUNTIME_FEATURES_NOT_DISABLED")
    return {
       "mode":mode,
       "actual_NPY_DISABLE_CPU_FEATURES":requested,
       "actual_NPY_ENABLE_CPU_FEATURES":None,
       "numpy_version":np.__version__,
       "numpy_build_baseline":list(numpy_cpu.__cpu_baseline__),
       "numpy_build_dispatch":list(numpy_cpu.__cpu_dispatch__),
       "numpy_actual_features":flags,
       "verified_cpu_AVX2_disabled_in_disabled_mode":mode=="disable_avx2_fma3" and not flags["AVX2"],
       "verified_cpu_FMA3_disabled_in_disabled_mode":mode=="disable_avx2_fma3" and not flags["FMA3"],
       "other_enabled_AVX512_or_SIMD_features":
            sorted(k for k,v in flags.items() if v and k.startswith("AVX512")),
       "python_version":platform.python_version(),
       "platform_OS":platform.system(),
       "platform_machine":platform.machine(),
    }

def main(source_model,farama,pycolab):
    p=frozen()
    original=assert_exact_original_MR34I4_source()
    controls=cpu_dispatch()
    project=str(Path(__file__).resolve().parents[2])
    if project not in sys.path:sys.path.insert(0,project)
    from research.mr34i4 import kernel_probe
    start=time.process_time_ns()
    orig_stdout=io.StringIO()
    with redirect_stdout(orig_stdout):
        kernel_probe.main(source_model,farama,pycolab)
    stdout=orig_stdout.getvalue()
    lines=stdout.splitlines()
    original_sections=[]
    original_result=None
    for line in lines:
        if line.startswith("MR34I4_BINARY64_ORIGINAL_KERNEL_SECTION="):
            payload=line.split("=",1)[1]
            section=json.loads(payload)
            original_sections.append(section)
        elif line.startswith("MR34I4_ORIGINAL_SIGMOID_NUMERICAL_REFERENCE="):
            original_result=json.loads(line.split("=",1)[1])
        else:
            raise ValueError("MR34I5_ORIGINAL_PROBE_UNEXPECTED_OUTPUT")
    if len(original_sections)!=4 or original_result is None:
        raise ValueError("MR34I5_ORIGINAL_NUMERIC_EVIDENCE_MISSING")
    if original_result["original_model_git_sha"]!=SOURCE_MODEL:
        raise ValueError("MR34I5_ORIGINAL_PINNED_45_MODEL_CHANGED")
    sections=original_result["development_ONLY_nonlearning_kernel_sections"]
    if len(sections)!=4 or {x["cohort"] for x in sections}!=set(INPUT_SHA):
        raise ValueError("MR34I5_ORIGINAL_FROZEN_CASES_CHANGED")
    for sec in sections:
        if sec["original_input_corpus_binary64_sha256"]!=INPUT_SHA[sec["cohort"]]:
            raise ValueError("MR34I5_ORIGINAL_SOURCE_FLOAT_INPUT_DRIFT_"+sec["cohort"])
        raw=next(x["exact_original_input_and_stage_float64_bytearray_hex"]
                  for x in original_sections if x["cohort"]==sec["cohort"])
        if set(raw)!=set(sec["per_cohort_stage_SHA256"]):
            raise ValueError("MR34I5_ORIGINAL_SOURCE_NUMERIC_STAGE_MISSING")
        if any(sha(bytes.fromhex(raw[k]))!=v
               for k,v in sec["per_cohort_stage_SHA256"].items()):
            raise ValueError("MR34I5_ORIGINAL_SOURCE_NUMERIC_BYTES_HASH_MISMATCH")
    # Emit all original raw float64 stage bytearrays unchanged for objective
    # per-index cross-OS and within-OS replication. Never use rounded values.
    for line in lines:
        if line.startswith("MR34I4_BINARY64_ORIGINAL_KERNEL_SECTION="):
            print(line)
    rss=psutil.Process().memory_info()
    if sys.platform=="win32":
        peak=int(getattr(rss,"peak_wset",0))
    elif sys.platform.startswith("linux"):
        import resource
        peak=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1024
    else:
        raise ValueError("MR34I5_UNSUPPORTED_CPU_DISPATCH_OS")
    if peak<=0:raise ValueError("MR34I5_OS_PEAK_RESIDENT_NOT_MEASURED")
    print("MR34I5_ORIGINAL_NUMPY_CPU_DISPATCH="+canon({
       "source_precode_protocol_sha256":sha(FILE.read_bytes()),
       "original_MR34I4_numerical_code_exact":original,
       "numpy_pre_import_CPU_dispatch_controls":controls,
       "original_unchanged_numeric_source_reference_sections":sections,
       "original_two_authored_sources_and_reference_CPU_ns":
           time.process_time_ns()-start,
       "original_source_full_process_OS_peak_RSS_bytes":peak,
       "native_original_source_held_scientific_first_use_consumed":False,
       "native_original_model_weights_updated":False,
       "source_third_unfamiliar_protected_task_opened":False,
       "original_source_kernel_cross_job_equivalence":"REQUIRES_EIGHT_JOB_COMPARISON",
       "portable_native_learned_checkpoint_admission":"NO_GO",
       "independent_cognition_transfer_scientific_admission":"NO_GO",
       "G29_atlas_full_regressions":"FAIL_CLOSED",
    }))

if __name__=="__main__":
    if len(sys.argv)!=4:
        raise SystemExit("Usage: python audit/research/mr34i5/cpu_dispatch_probe.py ORIGINAL_S4C1 ORIGINAL_FARAMA ORIGINAL_PYCOLAB")
    main(*sys.argv[1:])
