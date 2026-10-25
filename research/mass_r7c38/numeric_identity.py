"""C38 diagnostic: exact original C37 numerical FIT model identity, no source worlds.

Read-only C35 FIT physical receipts, original unchanged C36 learner.
No MiniGrid import/reset/step. FIT_CHECK verified for source custody only,
not scored/used for training or science selection.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time
import numpy as np

from research.native.itd02.r1.native_policy import canonical
from research.mass_r7c36.run import (
    CausalOptions, read_C35_fit, feature, PAIRS, P as ORIGINAL,
)
HERE=Path(__file__).resolve().parent
P=json.loads((HERE/"PREREG.json").read_text(encoding="utf-8"))


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def provenance(folder):
    original_a=json.loads((folder/"process-a.json").read_bytes())
    original_b=json.loads((folder/"process-b.json").read_bytes())
    if (set(q.name for q in folder.iterdir() if q.is_file())!={
        "process-a.json","process-b.json","comparison.json","process-a.log","process-b.log"
    }):
        raise ValueError("C38_NOT_ORIGINAL_C35_ZIP_MEMBERS")
    cmp=json.loads((folder/"comparison.json").read_bytes())
    # Independently rerun original C35 whole original source producer science,
    # including ALL source public and real physically selected action receipts.
    from research.mass_r7c35.compare import compare
    if cmp!=compare(original_a,original_b) or cmp["science_identical"] is not True or (
        cmp["result"]!="NO_REPEATABLE_C35_TWO_ACTION_CAUSAL_EFFECT_PREDICTIVE_ADVANCEMENT"):
        raise ValueError("C38_C35_ORIGINAL_SCIENCE_CUSTODY_DRIFT")
    fit,motors=read_C35_fit(folder)
    if len(fit)!=31 or len({(x["family"],x["seed"]) for x in fit})!=15:
        raise ValueError("C38_C35_ORIGINAL_FIT_ROLES_CHANGED")
    return fit,motors,cmp


def diagnose(folder):
    fit,motors,receipt=provenance(folder)
    model=CausalOptions(fit,motors)
    rows=[];outcomes=[]
    for row in fit:
        for pair in PAIRS:
            branch=row["all_nine_original_physical_pairs"][f"{pair[0]}{pair[1]}"]
            if (not branch["completed_two_original_actions"] or
                [x["action"] for x in branch["actual_selected_source_actions"]]!=list(pair)):
                raise ValueError("C38_SOURCE_SELECTED_PAIR_NOT_EXECUTED")
            rows.append(feature(row,pair))
            outcomes.append(branch["real_two_step_goal_distance_improvement"])
    X=np.asarray(rows,dtype=np.float64);Y=np.asarray(outcomes,dtype=np.float64)
    if X.shape[0]!=93 or model.fitted!=93 or not np.isfinite(X).all() or not np.isfinite(Y).all():
        raise ValueError("C38_FIT_ONLY_OPTION_RIGHTS_DRIFT")
    xtx=X.T@X
    xty=X.T@Y
    reg=np.eye(X.shape[1],dtype=np.float64)*ORIGINAL["mechanism"]["frozenRidgePenalty"]
    reg[0,0]=0
    A=xtx+reg
    weights=np.asarray(model.ridge,dtype=np.float64)
    if not np.isfinite(weights).all():
        raise ValueError("C38_NONFINITE_ORIGINAL_MODEL")
    assert np.max(np.abs(A@weights-xty))<1e-6, "C38_NUMERICAL_NORMAL_EQUATION_RESIDUAL"
    motor_source=dict(motors)
    science={
        "schema":P["schema"],
        "source_C35_full_original_provider_hash":P["original_C35_zip_sha256"],
        "source_original_C35_whole_science":receipt["result"],
        "source_entire_FIT_episode_training_rights":31,
        "source_unique_physical_FIT_world_groups":15,
        "source_model_selected_original_two_action_pairs":93,
        "original_C36_unmodified_fitted_model_sha256":model.model_sha,
        "original_C37_run_A_previous_model_sha":P["original_C37_A_model_sha"],
        "original_C37_run_B_previous_model_sha":P["original_C37_B_model_sha"],
        "original_source_FIT_training_order_sha256":digest([
           {"family":r["family"],"seed":r["seed"],"tick":r["tick"],
             "prefix":r["anchor_source_sha256"]} for r in fit]),
        "real_selected_source_FIT_model_features_sha256":hashlib.sha256(X.tobytes(order="C")).hexdigest(),
        "real_selected_source_FIT_real_progress_labels_sha256":hashlib.sha256(Y.tobytes(order="C")).hexdigest(),
        "model_prior_count_sha256":digest(model.snapshot()["prior"]),
        "model_conditional_count_sha256":digest(model.snapshot()["condition"]),
        "actual_source_motor_count_sha256":digest(motor_source),
        "feature_XTX_float64_bytes_sha256":hashlib.sha256(xtx.tobytes(order="C")).hexdigest(),
        "feature_XTY_float64_bytes_sha256":hashlib.sha256(xty.tobytes(order="C")).hexdigest(),
        "normal_equations_matrix_float64_bytes_sha256":hashlib.sha256(A.tobytes(order="C")).hexdigest(),
        "original_numpy_ridge_float64_bytes_sha256":hashlib.sha256(weights.tobytes(order="C")).hexdigest(),
        "original_numpy_ridge_canonical_sha256":digest(model.ridge),
        "original_numpy_ridge_coefficients_float64":model.ridge,
        "normal_equation_absolute_max_residual":float(np.max(np.abs(A@weights-xty))),
        "fit_regularized_matrix_condition_number":float(np.linalg.cond(A)),
        "true_original_source_actions_new_in_this_gate":0,
        "source_DEV_VALID_protected_first_use":0,
        "original_R3_modified":False,
        "native_model_superiority":"NOT_TESTED",
        "source_C37_previous_cross_host_model_identity":"DRIFT_NOT_QUALIFIED"
    }
    runtime={
        "python":sys.version.split()[0],"numpy":np.__version__,
        "platform":platform.platform(),"processor":platform.processor(),
        "OPENBLAS_NUM_THREADS":os.environ.get("OPENBLAS_NUM_THREADS"),
        "PYTHONHASHSEED":os.environ.get("PYTHONHASHSEED"),
        "model_sha":model.model_sha,
    }
    return science,runtime


def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--original-fit-dir",type=Path,required=True)
    pa.add_argument("--out",type=Path,required=True)
    args=pa.parse_args()
    science,runtime=diagnose(args.original_fit_dir)
    if args.out.exists() or not args.out.parent.is_dir():
        raise ValueError("C38_SOURCE_REPORT_DESTINATION_NOT_FRESH")
    science_bytes=canonical(science)
    args.out.write_bytes(canonical({
      "science":science,"science_sha256":hashlib.sha256(science_bytes).hexdigest(),
      "runtime_not_part_of_science":runtime
    })+b"\n")
    for k in ("source_original_C35_whole_science",
              "original_C36_unmodified_fitted_model_sha256",
              "model_prior_count_sha256","model_conditional_count_sha256",
              "actual_source_motor_count_sha256",
              "feature_XTX_float64_bytes_sha256","feature_XTY_float64_bytes_sha256",
              "original_numpy_ridge_float64_bytes_sha256",
              "fit_regularized_matrix_condition_number"):
        print("C38_"+k.upper()+"="+str(science[k]),flush=True)
    print("C38_FIT_ONLY_SCIENCE_SHA256="+hashlib.sha256(science_bytes).hexdigest(),flush=True)
    print("C38_NEW_MINIGRID_SOURCE_STEPS=0; C38_PROTECTED_FIRST_USE=DENIED",flush=True)


if __name__=="__main__":
    main()
