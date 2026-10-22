"""MR34I1 original-training-only numerical custody diagnostic.

External EXACT S4C1 source and original authored source engines checked out by
the runner. This file DOES NOT alter source, original model, original numerical
training, hyperparameters, actor, training seeds, heldout/science evidence, or
original policies. It hashes the sequential source/observable tensors and
the first native original gradient, then runs ORIGINAL S4C1 train_native as is.
Cross-job comparison decides admission; a green single job is not admission.
"""
from hashlib import sha256
from pathlib import Path
import contextlib
import io
import json
import os
import platform
import subprocess
import sys
import time

import numpy as np

FILE=Path(__file__).with_name("frozen_protocol.json")
MR34I0_SHA="06afcc66f26ef02605bdcca45ed89cada3d2ac48"
S4C1_SHA="8e1561eb1a542e21307bac669c42435cf48e59bd"
SEEDS=(1861,1867,1871,1873,1877,1879,1889,1901,1907,1913,
       1931,1933,1949,1951,1973,1979,1987,1993,1997,1999)
SOURCES={
 "FaramaMiniGridDoorKey8":"7f5853792ea7f04f75614661006d87fcf949f26d",
 "DeepMindPycolabApprehend":"6504c8065dd5322438f23a2a9026649904f3322a",
}

def sha(b):
    return sha256(b).hexdigest()

def canon(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),allow_nan=False)

def original_git(path,expected):
    root=Path(path).resolve()
    if not root.is_dir():
        raise ValueError("MR34I1_ORIGINAL_CHECKOUT_MISSING")
    current=subprocess.check_output(
        ["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    if current!=expected:
        raise ValueError("MR34I1_ORIGINAL_CHECKOUT_EXACT_HEAD_DRIFT")
    dirty=subprocess.check_output(
        ["git","-C",str(root),"status","--porcelain"],text=True)
    if dirty.strip():
        raise ValueError("MR34I1_ORIGINAL_CHECKOUT_MUTATED")
    return root

def contract():
    p=json.loads(FILE.read_text(encoding="utf-8"))
    if (p["schema"]!="yggdrasil.mr34i1.s4c1-training-only-model-numerical-source-audit.v1"
        or p["exact_MR34I0_parent_sha"]!=MR34I0_SHA
        or p["exact_yggdrasil_S4C1_experiment_sha"]!=S4C1_SHA
        or p["only_previously_consumed_S4C1_training_dev_reset_seeds"]!=list(SEEDS)
        or p["exclude_even_previously_consumed_held_dev_reset_seeds"]!=
            [2003,2011,2017,2027,2029,2039,2053,2063]
        or p["audited_source_native_step_cap"]!=96
        or p["original_source_commits"]!=SOURCES
        or p["no_original_source_mutation"] is not True
        or p["no_held_data_collection_or_access"] is not True
        or p["no_new_original_source_reset_seeds"] is not True
        or p["protected_unfamiliar_first_use"] is not False
        or p["same_OS_repeat_and_cross_OS_require_bit_exact_sha"] is not True):
        raise ValueError("MR34I1_FROZEN_NUMERIC_CUSTODY_DRIFT")
    return p

def numeric_runtime():
    out=io.StringIO()
    with contextlib.redirect_stdout(out):
        np.show_config()
    env_keys=("OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","OMP_NUM_THREADS",
              "BLIS_NUM_THREADS","NUMEXPR_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS","PYTHONHASHSEED")
    return {
      "OS_system":platform.system(),
      "OS_release":platform.release(),
      "machine":platform.machine(),
      "python_version":platform.python_version(),
      "numpy_version":np.__version__,
      "numpy_build_config_SHA256":sha(out.getvalue().encode()),
      "numpy_build_config_text":out.getvalue()[:16000],
      "numeric_environment":{k:os.environ.get(k,"UNSET") for k in env_keys},
    }

def source_episode_inputs(episodes_train):
    digest_source=sha256()
    digest_public_input=sha256()
    digest_history_input=sha256()
    digest_next_label=sha256()
    preaction=[]
    original_actions=0
    for ep in episodes_train:
        xhash=sha256()
        yhash=sha256()
        for row in ep:
            if (len(row)!=3 or row[0].shape!=(23,) or
                row[1].shape!=(69,) or row[2].shape!=(8,)):
                raise ValueError("MR34I1_ORIGINAL_PUBLIC_FEATURE_OR_TARGET_DRIFT")
            if any(z.dtype!=np.float64 or not np.isfinite(z).all()
                   for z in row):
                raise ValueError("MR34I1_ORIGINAL_FLOAT64_FEATURE_DRIFT")
            blobs=[v.tobytes(order="C") for v in row]
            if any(len(b)!=expected for b,expected in
                   zip(blobs,(23*8,69*8,8*8))):
                raise ValueError("MR34I1_FLOAT64_SOURCE_TENSOR_BYTES_DRIFT")
            digest_public_input.update(blobs[0])
            digest_history_input.update(blobs[1])
            digest_next_label.update(blobs[2])
            xhash.update(blobs[0])
            yhash.update(blobs[2])
            original_actions+=1
        preaction.append({
          "real_source_native_episode_steps":len(ep),
          "source_complete_23_float64_features_SHA256":xhash.hexdigest(),
          "original_next_public_change_target_SHA256":yhash.hexdigest(),
        })
    return {
        "actual_training_source_actions":original_actions,
        "real_episode_input_target_custody":preaction,
        "all_public_preaction_23_float64_bytes_sha256":digest_public_input.hexdigest(),
        "all_previous_public_history_69_float64_bytes_sha256":digest_history_input.hexdigest(),
        "all_native_eight_future_public_target_float64_bytes_sha256":
            digest_next_label.hexdigest(),
    }

def audit_source(family,root):
    from research.nci04_s4c1.original_native_predictive_state import (
        train_native, TRAIN, protocol)
    from research.mr34f.prospective_controls import episodes, SOURCES as OLD_SOURCES
    from research.nci04_s4c1.native_predictive_quotient import (
        NativePredictiveQuotient45, PARAMETERS, cell_public_features)
    if (tuple(TRAIN)!=SEEDS or PARAMETERS!=45 or
        OLD_SOURCES[family][0]!=SOURCES[family]):
        raise ValueError("MR34I1_S4C1_NATIVE_TRAINING_COHORT_CHANGED")
    protocol()
    start=time.process_time_ns()
    original_training,original_episode_receipts=episodes(root,family,SEEDS)
    if len(original_training)!=20:
        raise ValueError("MR34I1_S4C1_UNEXPECTED_TRAINING_EPISODES")
    source_identity=sha(canon(original_episode_receipts).encode())
    sensor=source_episode_inputs(original_training)
    native=NativePredictiveQuotient45()
    initial=native.snapshot()
    if native.g.shape!=(3,7) or native.roles.shape!=(8,3):
        raise ValueError("MR34I1_GENUINE_ORIGINAL_45_NATIVE_WEIGHTS_ABSENT")
    projection=cell_public_features(original_training[0][0][0])
    gradients=native.analytic_bptt(original_training[0])
    dg,dr=gradients
    if dg.shape!=(3,7) or dr.shape!=(8,3):
        raise ValueError("MR34I1_FIRST_GRADIENT_DIMENSION_DRIFT")
    initial_gradients={
        "first_episode_public_local_8_by_7_float64_features_SHA256":
            sha(projection.tobytes()),
        "original_native_initial_45slot_snapshot_sha256":
            sha(initial.encode()),
        "first_episode_shared_3x7_analytic_BPTT_float64_SHA256":
            sha(dg.tobytes()),
        "first_episode_local_8x3_analytic_BPTT_float64_SHA256":
            sha(dr.tobytes()),
        "first_episode_gradient_numeric_l2":float(np.sqrt(
            np.sum(dg*dg)+np.sum(dr*dr))),
        "original_first_episode_native_preaction_prediction_sha256":
            sha(native.forward(original_training[0]).tobytes())
    }
    # Original S4C1 training is executed UNMODIFIED from pinned exact Git SHA:
    # same 40 epochs, LR, loss, initial LocalTaskRuntime native 45 weights,
    # original source-train-only model selection and frozen finite-diff test.
    trained,trainer_receipt=train_native(original_training)
    checkpoint=trained.snapshot()
    original_git(root,SOURCES[family])
    return {
        "original_source_family":family,
        "exact_upstream_source_SHA":SOURCES[family],
        "previously_consumed_original_source_training_episodes":20,
        "source_native_event_identity_sha256":source_identity,
        "training_native_episode_receipts":original_episode_receipts,
        "preaction_original_full_training_tensor_identity":sensor,
        "native_initialization_and_first_analytic_gradient":initial_gradients,
        "original_S4C1_trained_native_exact_checkpoint_sha256":
            sha(checkpoint.encode()),
        "S4C1_original_unmodified_train_only_epoch":
            trainer_receipt["TRAINING_ONLY_selected_epoch"],
        "S4C1_original_40epoch_training_scores":
            trainer_receipt["source_native_training_first_last_best_Brier"],
        "S4C1_original_training_source_finite_difference_gradient":
            trainer_receipt["finite_difference_analytic_public_source_BPTT"],
        "S4C1_full_original_training_CPU_ns":
            trainer_receipt["training_cpu_ns_full_episode_45_coefficient_Adam"],
        "whole_source_grad_diagnostic_and_original_40epoch_train_CPU_ns":
            time.process_time_ns()-start,
        "trained_native_coefficient_count":45,
        "used_original_source_training_episodes_ONLY":True,
        "no_held_original_source_executed":True,
    }

def peak_rss():
    if sys.platform=="win32":
        import psutil
        v=getattr(psutil.Process().memory_info(),"peak_wset",None)
        if not v:
            raise ValueError("MR34I1_WINDOWS_PEAK_OS_RSS_NOT_RECORDED")
        return int(v)
    if sys.platform.startswith("linux"):
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*1024
    raise ValueError("MR34I1_UNSUPPORTED_OS_FOR_RESOURCE_COST")

def main(s4c1,farama,pycolab):
    p=contract()
    parent=original_git(s4c1,S4C1_SHA)
    roots={
     "FaramaMiniGridDoorKey8":original_git(farama,SOURCES["FaramaMiniGridDoorKey8"]),
     "DeepMindPycolabApprehend":original_git(
            pycolab,SOURCES["DeepMindPycolabApprehend"])
    }
    sys.path.insert(0,str(parent))
    sys.path.insert(0,str(roots["FaramaMiniGridDoorKey8"]))
    sys.path.insert(0,str(roots["DeepMindPycolabApprehend"]))
    from research.mr27.natural_memory import source_guard
    source_guard(roots["FaramaMiniGridDoorKey8"])
    start=time.process_time_ns()
    run={name:audit_source(name,roots[name]) for name in SOURCES}
    for name,root in roots.items():
        original_git(root,SOURCES[name])
    original_git(parent,S4C1_SHA)
    print("MR34I1_S4C1_TRAIN_ONLY_MODEL_CUSTODY="+canon({
        "frozen_precode_protocol_sha256":sha(FILE.read_bytes()),
        "exact_original_Yggdrasil_S4C1_git_sha":S4C1_SHA,
        "unmodified_original_source_and_native_training_results":run,
        "training_original_source_episodes_only":True,
        "all_original_S4C1_held_DEV_source_seeds_UNTOUCHED_in_this_audit":True,
        "protected_unfamiliar_third_source_family_NOT_EXECUTED":True,
        "native_checkpoint_cross_OS_bit_exact_qualifier":
            "PENDING_CROSS_JOB_RECEIPT_COMPARISON",
        "source_independent_native_observation_adapter":
            "NOT_VERIFIED",
        "runtime_environment_evidence":numeric_runtime(),
        "source_train_diagnostic_and_original_training_total_CPU_ns":
            time.process_time_ns()-start,
        "whole_process_OS_peak_resident_bytes":peak_rss(),
        "model_isolation_equal_resource_cost":"NOT_ESTABLISHED",
        "qualified_unknown_source_native_transfer":"BLOCKED",
        "G29_atlas_and_full_final_regression":"FAIL_CLOSED",
        "scientific_admission":"NO_GO",
    }))

if __name__=="__main__":
    if len(sys.argv)!=4:
        raise SystemExit("Usage: python train_only_numeric.py PINNED_YGG_S4C1 ORIGINAL_FARAMA ORIGINAL_PYCOLAB")
    main(*sys.argv[1:])
