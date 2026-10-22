"""MR34I6: original source first-public-logit stage + real CPU identity custody.

Original S4C1 native model and Farama / DeepMind original source engines are
executed unchanged on ONLY their already-consumed S4C1 TRAINING episodes.
This is a NONLEARNING forensic: no Adam, no protected first use, no heldout.
NumPy feature mode MUST be established before first NumPy import.
"""
import contextlib
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np
from numpy.core import _multiarray_umath as nu
import psutil

FROZEN=Path(__file__).with_name("frozen_protocol.json")
ORIGINAL_YGG="8e1561eb1a542e21307bac669c42435cf48e59bd"
SOURCES={"FaramaMiniGridDoorKey8":"7f5853792ea7f04f75614661006d87fcf949f26d",
         "DeepMindPycolabApprehend":"6504c8065dd5322438f23a2a9026649904f3322a"}
TRAIN=(1861,1867,1871,1873,1877,1879,1889,1901,1907,1913,
       1931,1933,1949,1951,1973,1979,1987,1993,1997,1999)
SOURCE_HASH={"FaramaMiniGridDoorKey8":"566f5e271e01421248bfabeb4326d01408d992276b877a978d96f14daf93797b",
             "DeepMindPycolabApprehend":"9ea175b912b734c7470f93d0b2584eea6c2ce01962aae285a66b4d4834b5346e"}
LOGITS_HASH={"FaramaMiniGridDoorKey8":"ba501812452b529cf35d4aaa176f9d5a0b5cfbb57a388d67c49dfbc547109486",
             "DeepMindPycolabApprehend":"23d9db17d29ed9646afac1b34000d0be320c2fa50ca424db2f85f1829be11bd7"}
INIT_SHA="45038837837af310f04d8dee2f91c4d5e106e2beb476e6c866b3c8b8b28e96a4"

def hash256(x):return sha256(x).hexdigest()
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def byt(v):return np.asarray(v,dtype=np.float64).tobytes(order="C")
def audit_vector(v):
    a=np.asarray(v,dtype=np.float64)
    if not a.flags.c_contiguous or not np.isfinite(a).all():
        raise ValueError("MR34I6_SOURCE_NUMERIC_ARRAY_INVALID")
    return {"sha256":hash256(byt(a)),"float64_hex":byt(a).hex(),"shape":list(a.shape)}

def verify_original(root,sha):
    root=Path(root).resolve()
    if not root.is_dir():raise ValueError("MR34I6_ORIGINAL_SOURCE_NOT_FOUND")
    current=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    dirty=subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip()
    if current!=sha or dirty:raise ValueError("MR34I6_ORIGINAL_SOURCE_SHA_OR_WORKTREE_DRIFT")
    return root

def freeze():
    cfg=json.loads(FROZEN.read_text(encoding="utf-8"))
    if (cfg["schema"]!="yggdrasil.mr34i6.real_runner_and_native_first_logit_custody.dev.v1"
        or cfg["predecessor_exact_MR34I5_SHA"]!="3af78f470d413c2f10249c7f3a0dbe0cdd62fe44"
        or cfg["original_S4C1_sha"]!=ORIGINAL_YGG
        or cfg["original_independently_authored_sources"]!=SOURCES
        or cfg["training_only_consumed_S4C1_reset_seeds"]!=list(TRAIN)
        or cfg["original_MR34I4_frozen_first_logit_SHA"]!=LOGITS_HASH
        or cfg["original_MR34I1_training_public_source_receipts"]!=SOURCE_HASH
        or cfg["original_S4C1_init_model_checkpoint_SHA"]!=INIT_SHA
        or cfg["numpy_pinned"]!="1.26.4"
        or cfg["matrix"]["expected_runs"]!=8
        or cfg["no_source_data_change"] is not True
        or cfg["no_original_model_or_optimizer_training"] is not True
        or cfg["no_held_development_source_read"] is not True
        or cfg["no_protected_third_source_first_use"] is not True):
        raise ValueError("MR34I6_PREREGISTERED_IDENTITY_DRIFT")
    return cfg

def feature_mode():
    mode=os.environ.get("MR34I6_MODE","")
    wanted=os.environ.get("NPY_DISABLE_CPU_FEATURES")
    if mode not in ("default","disable_avx2_fma3"):
        raise ValueError("MR34I6_INVALID_FROZEN_RUNNER_MODE")
    if mode=="default" and wanted is not None:
        raise ValueError("MR34I6_DEFAULT_HAS_CPU_OVERRIDE")
    if mode=="disable_avx2_fma3" and wanted!="AVX2,FMA3":
        raise ValueError("MR34I6_CPU_MODE_ENV_NOT_APPLIED_BEFORE_NUMPY_IMPORT")
    if np.__version__!="1.26.4":
        raise ValueError("MR34I6_NUMPY_VERSION_DRIFT")
    flags=dict(nu.__cpu_features__)
    if mode=="disable_avx2_fma3" and (flags.get("AVX2",True) or flags.get("FMA3",True)):
        raise ValueError("MR34I6_NUMPY_FEATURES_NOT_ACTUALLY_DISABLED")
    return {"mode":mode,"NPY_DISABLE_CPU_FEATURES":wanted,
            "numpy_runtime_cpu_features":flags,
            "numpy_build_baseline":list(nu.__cpu_baseline__),
            "numpy_build_dispatch":list(nu.__cpu_dispatch__),
            "numpy_version":np.__version__}

def hardware():
    cpu={}
    if sys.platform.startswith("linux"):
        p=Path("/proc/cpuinfo")
        if p.exists():
            group=p.read_text(encoding="utf-8",errors="replace").split("\n\n")[0]
            parsed={}
            for line in group.splitlines():
                if ":" in line:
                    k,v=line.split(":",1)
                    if k.strip() in ("vendor_id","cpu family","model","model name","stepping","microcode","flags","cpuid level","cache size"):
                        parsed[k.strip()]=v.strip()
            cpu={"linux_proc_cpuinfo":parsed,"original_first_proc_cpuinfo_block_sha256":hash256(group.encode())}
    if sys.platform=="win32":
        ps="Get-CimInstance Win32_Processor | Select-Object -First 1 Name,Manufacturer,ProcessorId,Family,Stepping,Description,NumberOfCores,NumberOfLogicalProcessors | ConvertTo-Json -Compress"
        try:
            r=subprocess.run(["powershell.exe","-NoProfile","-NonInteractive","-Command",ps],
                             stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                             text=True,timeout=25)
            if r.returncode==0:
                cpu={"win32_processor_cim":json.loads(r.stdout)}
            else:
                cpu={"win32_processor_cim_UNAVAILABLE":r.stderr[-450:]}
        except (subprocess.SubprocessError,ValueError) as e:
            cpu={"win32_processor_cim_UNAVAILABLE":str(e)}
    runtime=io.StringIO()
    with contextlib.redirect_stdout(runtime):
        np.show_runtime()
    return {
        "OS":platform.system(),"OS_release":platform.release(),"OS_version":platform.version(),
        "machine":platform.machine(),"processor_fallback":platform.processor(),
        "python_version":platform.python_version(),"python_compiler":platform.python_compiler(),
        "github_runner_image":os.environ.get("ImageOS","UNSPECIFIED"),
        "github_runner_image_version":os.environ.get("ImageVersion","UNSPECIFIED"),
        "github_runner_name":os.environ.get("RUNNER_NAME","UNSPECIFIED"),
        "processor_identity":cpu,
        "numpy_runtime_full_text":runtime.getvalue()[:20000],
        "numpy_runtime_description_sha256":hash256(runtime.getvalue().encode()),
        "BLAS_thread_env":{k:os.environ.get(k,"UNSET") for k in
                           ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS",
                            "VECLIB_MAXIMUM_THREADS","BLIS_NUM_THREADS","NUMEXPR_NUM_THREADS")}
    }

def original_source(name,root):
    from research.mr34f.prospective_controls import episodes,canon as source_canon
    from research.nci04_s4c1.original_native_predictive_state import (
        TRAIN as S4C1_TRAIN,protocol as original_protocol)
    from research.nci04_s4c1.native_predictive_quotient import (
        NativePredictiveQuotient45,cell_public_features)
    if tuple(S4C1_TRAIN)!=TRAIN:
        raise ValueError("MR34I6_ORIGINAL_S4C1_TRAIN_SEED_DRIFT")
    original_protocol()
    source_ep,source_receipts=episodes(root,name,TRAIN)
    if len(source_ep)!=20:
        raise ValueError("MR34I6_MISSING_TRAINING_SOURCE_EPISODE")
    events=hash256(source_canon(source_receipts).encode())
    if events!=SOURCE_HASH[name]:
        raise ValueError("MR34I6_REAL_SOURCE_ACTION_PUBLIC_DRIFT")
    model=NativePredictiveQuotient45()
    initial=model.snapshot()
    if hash256(initial.encode())!=INIT_SHA:
        raise ValueError("MR34I6_ORIGINAL_INITIAL_NATIVE_CHECKPOINT_DRIFT")
    logitbytes=bytearray()
    episodes_out=[]
    for seed,episode in zip(TRAIN,source_ep):
        current=episode[0][0]
        sensor=cell_public_features(current)
        dot0=sensor@model.g[0]
        dot1=sensor@model.g[1]
        roles0=model.roles[:,0]
        u_base=dot0+roles0
        # Explicitly preserve original MR34I4 first-step logit evaluation:
        # read and a zero-multiplied read term are diagnostic, never trained.
        read=dot1+model.roles[:,1]
        original_u=u_base+np.zeros(8)*read
        prob=model.forward([episode[0]])[0]
        predicted=1./(1.+np.exp(-np.clip(original_u,-35.,35.)))
        if not np.array_equal(prob.view(np.uint64),predicted.view(np.uint64)):
            raise ValueError("MR34I6_OUR_MR34I4_NATIVE_SOURCE_FORMULA_NOT_EQUIVALENT")
        logitbytes.extend(byt(original_u))
        episodes_out.append({
            "seed":seed,"real_original_episode_actions":len(episode),
            "public_input23":audit_vector(current),
            "original_cell_features_8x7":audit_vector(sensor),
            "original_f_dot_g0":audit_vector(dot0),
            "original_f_dot_g1":audit_vector(dot1),
            "original_native_role0":audit_vector(roles0),
            "original_dot0_plus_role0":audit_vector(u_base),
            "original_read_dot1_plus_role1":audit_vector(read),
            "original_MR34I4_full_first_public_logit_u":audit_vector(original_u),
            "unchanged_native_model_original_sigmoid":audit_vector(prob)})
    logitsha=hash256(bytes(logitbytes))
    if model.snapshot()!=initial or model.train_updates!=0:
        raise ValueError("MR34I6_LEARNER_WEIGHT_MUTATION_FORBIDDEN")
    return {
        "source_original_repo_head":SOURCES[name],
        "original_20_training_episodes_actions_sha256":events,
        "original_model_initial_checkpoint_sha256":INIT_SHA,
        "previous_MR34I4_public_logit_sha256":LOGITS_HASH[name],
        "measured_source_public_logit_sha256":logitsha,
        "source_first_public_logits_MATCH_original_MR34I4":logitsha==LOGITS_HASH[name],
        "per_source_training_seed_original_native_public_arithmetic":episodes_out,
        "native_original_training_source_total_actions":sum(len(e) for e in source_ep),
        "model_checkpoint_not_trained":True
    }

def main(original_ygg,farama,pycolab):
    freeze()
    mode=feature_mode()
    root=verify_original(original_ygg,ORIGINAL_YGG)
    sources={"FaramaMiniGridDoorKey8":verify_original(farama,SOURCES["FaramaMiniGridDoorKey8"]),
             "DeepMindPycolabApprehend":verify_original(pycolab,SOURCES["DeepMindPycolabApprehend"])}
    sys.path.insert(0,str(root))
    for p in sources.values():sys.path.insert(0,str(p))
    from research.mr27.natural_memory import source_guard
    source_guard(sources["FaramaMiniGridDoorKey8"])
    started=time.process_time_ns()
    hardware_evidence=hardware()
    results={}
    for name,path in sources.items():
        value=original_source(name,path)
        results[name]=value
        print("MR34I6_ORIGINAL_PUBLIC_LOGIT_PER_SOURCE="+canon({
            "source":name,"cpu_mode":mode["mode"],"data":value
        }))
    verify_original(root,ORIGINAL_YGG)
    for name,path in sources.items():verify_original(path,SOURCES[name])
    info=psutil.Process().memory_info()
    if sys.platform=="win32":
        peak=int(getattr(info,"peak_wset",0))
    elif sys.platform.startswith("linux"):
        import resource
        peak=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1024
    else:raise ValueError("MR34I6_UNSUPPORTED_RUNNER_OS")
    if peak<=0:raise ValueError("MR34I6_PROCESS_PEAK_RSS_UNAVAILABLE")
    print("MR34I6_HARDWARE_SOURCE_LOGIT_CUSTODY="+canon({
        "frozen_protocol_SHA256":hash256(FROZEN.read_bytes()),
        "actual_preimport_numpy_CPU_mode":mode,
        "actual_runner_CPU_OS_NumPy_BLAS_identity":hardware_evidence,
        "original_source_public_logit_sha256_by_family":{
            name:z["measured_source_public_logit_sha256"] for name,z in results.items()},
        "original_source_input_match_MR34I4_by_family":{
            name:z["source_first_public_logits_MATCH_original_MR34I4"] for name,z in results.items()},
        "complete_source_20seed_evidence_was_emitted_separately":True,
        "full_original_source_and_logit_provenance_CPU_ns":time.process_time_ns()-started,
        "whole_process_peak_resident_memory_bytes":peak,
        "portable_S4C1_native_checkpoint_accepted":False,
        "native_original_model_trained":False,
        "held_and_protected_third_source_first_use_consumed":False,
        "cognitive_scientific_transfer":"NO_GO",
        "G29_and_full_native_project_regression":"FAIL_CLOSED"}))
if __name__=="__main__":
    if len(sys.argv)!=4:
        raise SystemExit("Usage: python audit/research/mr34i6/runner_identity.py S4C1 FARAMA PYCOLAB")
    main(*sys.argv[1:])
