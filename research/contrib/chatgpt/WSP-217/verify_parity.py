"""WSP217 independently recomputes frozen result and Linux/Windows numeric parity.

Receipt verification never imports or executes primary generators.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

SCHEMA="wsp217.unmarked-delayed-credit.v1"
PREREG="273f0c4671bb4a27dcbe29f24bb0ab16339361cc"
WORLDS=(21701,21702,21703,21704)
MODES=("local","full_regression","last_action","pooled_action","shuffled_consequence")


def numeric(label,a,b):
    if type(a) not in (int,float) or type(b) not in (int,float):
        raise ValueError(label+": not a numeric result")
    if not math.isfinite(a) or not math.isfinite(b):
        raise ValueError(label+": invalid/nonfinite")
    if not math.isclose(a,b,abs_tol=1e-9,rel_tol=1e-9):
        raise ValueError(label+f": material OS drift {a!r} vs {b!r}")


def same(label,a,b):
    if a!=b: raise ValueError(label+": cross-OS identity mismatch")


def sha(label,v):
    if not isinstance(v,str) or len(v)!=64 or any(c not in "0123456789abcdef" for c in v):
        raise ValueError(label+": invalid SHA256")


def exact_active_lag(seed):
    # Postfit independent oracle check only, never accessed by primary learner.
    return hashlib.sha256(f"WSP217\0{seed}\0hidden-active-lag".encode()).digest()[0]%2


def one_world(w,seed):
    if (w.get("world")!=seed or w.get("status")!="VALID" or
            w.get("stages_completed")!=4 or w.get("fit_rows")!=200 or
            w.get("held_pairs")!=100 or
            w.get("original_gfp_accessed") or w.get("reserved_accessed")):
        raise ValueError("invalid world/cohort completion")
    for key in ("fit_sha256","held_sha256"):
        sha(key,w[key])
    if set(w["trajectories"])!=set(MODES) or set(w["metrics"])!=set(MODES):
        raise ValueError("missing bounded experiment arm")
    for num in ("zero_held_rmse","oracle_held_rmse"):
        numeric("world."+num,w[num],w[num])
    if w["hidden_lag_postfit"]!=exact_active_lag(seed):
        raise ValueError("privileged postfit lag identity inconsistent")
    if len(w["active_lag_l2_squares"])!=2:
        raise ValueError("missing active-lag weights")
    mag=w["active_lag_l2_squares"]
    for v in mag:numeric("lag magnitude",v,v)
    discovered=(mag[w["hidden_lag_postfit"]]>1.5*mag[1-w["hidden_lag_postfit"]])
    if type(w["discovered_active_lag"]) is not bool or w["discovered_active_lag"]!=discovered:
        raise ValueError("inconsistent frozen lag discovery flag")
    for mode in MODES:
        trace=w["trajectories"][mode]
        metrics=w["metrics"][mode]
        if len(trace)!=4:raise ValueError("missing cumulative stage")
        for stage,row in enumerate(trace):
            if row["stage"]!=stage or row["rows_cumulative"]!=50*(stage+1):
                raise ValueError("invalid stage/cumulative rows")
            for key in ("source_digest","checkpoint_sha256"):
                sha(key,row[key])
            numeric("B0 historical",row["b0_rmse"],row["b0_rmse"])
            if mode=="local":
                if row["coordinate_solves"]!=24*9*3*(stage+1):
                    raise ValueError("wrong local solve budget")
                if row["scalar_accumulations"]<=0:
                    raise ValueError("missing actual local accumulator proof")
            else:
                if row["coordinate_solves"]!=0:
                    raise ValueError("conventional must not claim direct local solves")
                if row["conventional_refit_rows"]!=50*(stage+1)*(stage+2)//2:
                    raise ValueError("conventional refit missing full cumulative source")
        for key in ("held_effect_rmse","b0_final_rmse"):
            numeric(mode+"."+key,metrics[key],metrics[key])
        numeric("B0 final",metrics["b0_final_rmse"],trace[-1]["b0_rmse"])
        if metrics["stored_scalar_weights"] < 0:
            raise ValueError("invalid capacity accounting")
        if mode=="local":
            if metrics["total_coordinate_solves"]!=24*9*3*4:
                raise ValueError("bad candidate solve-cost accounting")
            if metrics["cumulative_batch_rows_replayed"]!=0:
                raise ValueError("candidate must not retain/refit raw episodes")
        elif metrics["cumulative_batch_rows_replayed"]!=500:
            raise ValueError("conventional must fully refit after all stages")
    for stage in range(4):
        if len({w["trajectories"][m][stage]["source_digest"] for m in MODES})!=1:
            raise ValueError("not matched information and action exposures")
    x=w["metrics"]["local"];full=w["metrics"]["full_regression"]
    predicted=(
      x["held_effect_rmse"]<=max(1.10*full["held_effect_rmse"],full["held_effect_rmse"]+.02) and
      x["held_effect_rmse"]<=.75*w["metrics"]["last_action"]["held_effect_rmse"] and
      x["held_effect_rmse"]<=.75*w["metrics"]["pooled_action"]["held_effect_rmse"] and
      x["held_effect_rmse"]<=.75*w["metrics"]["shuffled_consequence"]["held_effect_rmse"] and
      x["held_effect_rmse"]<=.60*w["zero_held_rmse"] and
      discovered and
      x["b0_final_rmse"]<=max(1.20*w["trajectories"]["local"][0]["b0_rmse"],
                              w["trajectories"]["local"][0]["b0_rmse"]+.02))
    if type(w["world_supported"]) is not bool or w["world_supported"]!=predicted:
        raise ValueError("post-hoc world classification drift")


def compare_receipts(linux,windows):
    for key in ("schema","prereg","status","original_gfp_accessed",
                "reserved_accessed","prior_cohorts_reused",
                "native_amalgam_accessed","research_only"):
        same("root."+key,linux.get(key),windows.get(key))
    if linux.get("schema")!=SCHEMA or linux.get("prereg")!=PREREG:
        raise ValueError("unfrozen prereg or wrong source")
    if linux.get("status") not in ("UNMARKED_CREDIT_SUPPORTED","NO_GAIN"):
        raise ValueError("invalid unqualified primary")
    if (linux["original_gfp_accessed"] or linux["reserved_accessed"] or
            linux["prior_cohorts_reused"] or linux["native_amalgam_accessed"] or
            not linux["research_only"]):
        raise ValueError("authority/source fence failed")
    if len(linux.get("worlds",[]))!=4 or len(windows.get("worlds",[]))!=4:
        raise ValueError("missing frozen world")
    for i,(a,b) in enumerate(zip(linux["worlds"],windows["worlds"])):
        one_world(a,WORLDS[i]);one_world(b,WORLDS[i])
        for key in ("world","status","stages_completed","fit_rows","held_pairs",
                    "fit_sha256","held_sha256","hidden_lag_postfit",
                    "world_supported","discovered_active_lag",
                    "original_gfp_accessed","reserved_accessed"):
            same(f"world{i}.{key}",a[key],b[key])
        for key in ("zero_held_rmse","oracle_held_rmse"):
            numeric(f"world{i}.{key}",a[key],b[key])
        for j,(x,y) in enumerate(zip(a["active_lag_l2_squares"],b["active_lag_l2_squares"])):
            numeric(f"world{i}.lag{j}",x,y)
        for mode in MODES:
            for key in ("held_effect_rmse","b0_final_rmse"):
                numeric(f"world{i}.{mode}.{key}",a["metrics"][mode][key],b["metrics"][mode][key])
            for key in ("stored_scalar_weights","total_coordinate_solves",
                        "cumulative_batch_rows_replayed"):
                same(f"world{i}.{mode}.{key}",a["metrics"][mode][key],b["metrics"][mode][key])
            for stage,(x,y) in enumerate(zip(a["trajectories"][mode],b["trajectories"][mode])):
                for key in ("stage","source_digest","rows_cumulative",
                            "scalar_accumulations","coordinate_solves",
                            "conventional_refit_rows"):
                    same(f"world{i}.{mode}.stage{stage}.{key}",x[key],y[key])
                numeric(f"world{i}.{mode}.stage{stage}.B0",x["b0_rmse"],y["b0_rmse"])
    expected=("UNMARKED_CREDIT_SUPPORTED" if sum(w["world_supported"]
              for w in linux["worlds"])>=3 else "NO_GAIN")
    if linux["status"]!=expected:
        raise ValueError("frozen cohort decision not reproduced")
    return expected


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("verify_parity.py linux.json windows.json")
    a=json.loads(Path(sys.argv[1]).read_text("utf-8"))
    b=json.loads(Path(sys.argv[2]).read_text("utf-8"))
    print("WSP217_CROSS_OS_PARITY=PASS CLASSIFICATION="+compare_receipts(a,b))
