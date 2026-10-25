"""Archived C35 FIT-only C38 independent deterministic ridge reference; no source steps."""
import argparse,hashlib,json,math,os
from pathlib import Path
from research.mass_r7c36.run import CausalOptions,feature,PAIRS,P as ORIGINAL
from research.mass_r7c38.numeric_identity import provenance
from research.mass_r7c38.deterministic_shadow import shadow_fit,compare_models,canonical,sha
HERE=Path(__file__).resolve().parent
PROTOCOL=json.loads((HERE/"DETERMINISTIC_SHADOW_PROTOCOL.json").read_text(encoding="utf-8"))
def report(original_fit_dir):
    fit,motors,prior_original_science=provenance(Path(original_fit_dir))
    # The original unchanged C36 learner sees exactly these three original
    # executed options per FIT anchor; the other six C35 forks are not used
    # for this learner and MUST NOT be retrospectively included.
    rows=[];labels=[]
    for r in fit:
        for pair in PAIRS:
            fork=r["all_nine_original_physical_pairs"][f"{pair[0]}{pair[1]}"]
            if (not fork["completed_two_original_actions"] or
                [x["action"] for x in fork["actual_selected_source_actions"]]!=list(pair)):
                raise ValueError("SHADOW_UNEXECUTED_OR_IMPUTED_PHYSICAL_PAIR")
            rows.append(feature(r,pair))
            labels.append(fork["real_two_step_goal_distance_improvement"])
    if len(fit)!=31 or len(rows)!=93 or len(PAIRS)!=3:
        raise ValueError("SHADOW_C36_93_SOURCE_FIT_ROWS_REQUIRED")
    model=CausalOptions(fit,motors) # original unchanged NumPy FIT; historical drift retained
    reference=shadow_fit(rows,labels,ORIGINAL["mechanism"]["frozenRidgePenalty"])
    if reference["fit_rows"]!=model.fitted or reference["feature_dimensions"]!=len(model.ridge):
        raise ValueError("SHADOW_ORIGINAL_RIDGE_FIT_DIMENSIONS_CHANGED")
    comparison=compare_models(model.ridge,reference,rows)
    run_cpu=reference.pop("runtime_shadow_fit_cpu_seconds")
    science={"schema":PROTOCOL["schema"],"source_original_C35_artifact":12603145885,
      "original_C35_full_source_science":prior_original_science["result"],
      "original_C36_ridge_penalty":ORIGINAL["mechanism"]["frozenRidgePenalty"],
      "original_C36_considered_action_pairs":[list(p) for p in PAIRS],
      "FIT_source_world_group_count":len({(x["family"],x["seed"]) for x in fit}),
      "FIT_full_original_public_anchor_count":len(fit),
      "FIT_physical_selected_training_options":len(rows),
      "original_C36_regression_features_sha256":sha(rows),
      "original_C36_actual_physical_labels_sha256":sha(labels),
      "deterministic_reference":reference,
      "original_vs_reference_FIT_only_diagnostic":comparison,
      "original_C37_crosshost_model_sha_drift":"STILL_NOT_QUALIFIED",
      "native_causal_superiority":"NOT_TESTED",
      "original_source_new_steps":0,
      "protected_first_use":False}
    # A separate OS-specific sidecar is never part of science digest.
    runtime={"original_unmodified_numpy_model_sha256":model.model_sha,
      "original_unmodified_numpy_float64_coefficients":model.ridge,
      "original_model_source_numerical_backend":"platform-dependent_numpy",
      "shadow_cpu_seconds":run_cpu,
      "openblas_threads":os.environ.get("OPENBLAS_NUM_THREADS")}
    return {"science":science,"science_sha256":sha(science),"runtime_not_part_of_science":runtime}
def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--original-fit-dir",type=Path,required=True)
    pa.add_argument("--out",type=Path,required=True)
    args=pa.parse_args()
    if args.out.exists() or not args.out.parent.is_dir():
        raise ValueError("SHADOW_SOURCE_REPORT_DESTINATION_NOT_FRESH")
    result=report(args.original_fit_dir)
    args.out.write_bytes(canonical(result)+b"\n")
    s=result["science"]
    print("C38_REFERENCE_SOURCE_FIT_ACTUAL_OPTIONS="+str(s["FIT_physical_selected_training_options"]))
    print("C38_REFERENCE_EXACT_COEFF_SHA256="+s["deterministic_reference"]["shadow_coefficients_sha256"])
    print("C38_REFERENCE_CROSSHOST_CANONICAL_SCIENCE_SHA256="+result["science_sha256"])
    print("C38_REFERENCE_FIT_TOP_ACTION_FLIPS="+str(s["original_vs_reference_FIT_only_diagnostic"]["original_source_FIT_three_candidate_rank_flip_count"]))
    print("C38_ORIGINAL_SOURCE_NEW_STEPS=0; C38_SCIENTIFIC_GO=FALSE",flush=True)
if __name__=="__main__":main()
