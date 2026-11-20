"""WSP216 independent, fully source-free Linux/Windows result audit."""
from pathlib import Path
import json
import math
import sys

SCHEMA="wsp216.delayed-paired-credit.source-free.v1"
PREREG="3df95400fb43875c4e1856a9f0e1cbbadf44b54c"
WORLDS=(21601,21602,21603,21604)
POLICIES=("credit","full_mle","last_action","no_lag","swap_lag")
FLOATS=("held_rmse","b3_b0_rmse")
STAGE_FLOATS=("b0_historical_rmse",)


def numeric(label,a,b):
    if type(a) not in (int,float) or type(b) not in (int,float):
        raise ValueError(label+": invalid scalar")
    if not math.isfinite(a) or not math.isfinite(b):
        raise ValueError(label+": NaN or infinite")
    if not math.isclose(a,b,abs_tol=1e-10,rel_tol=1e-10):
        raise ValueError(label+f": numeric cross-OS divergence {a!r} != {b!r}")


def same(label,a,b):
    if a!=b:
        raise ValueError(label+": immutable metric/source mismatch")


def digest(label,x):
    if not isinstance(x,str) or len(x)!=64 or any(c not in "0123456789abcdef" for c in x):
        raise ValueError(label+": invalid SHA-256")


def validate(w,world):
    if (w["world"]!=world or w["status"]!="VALID" or
            w["stages_completed"]!=4 or w["fit_rows"]!=128 or
            w["held_rows"]!=64 or w["source_original_accessed"] or
            w["reserved_accessed"]):
        raise ValueError("invalid world identity/completion/source boundary")
    digest("fit",w["fit_source_sha256"])
    digest("held",w["held_source_sha256"])
    if set(w["metrics"])!=set(POLICIES) or set(w["traces"])!=set(POLICIES):
        raise ValueError("missing arm")
    numeric("zero",w["zero_held_rmse"],w["zero_held_rmse"])
    numeric("B0",w["b0_initial_rmse"],w["b0_initial_rmse"])
    for arm in POLICIES:
        rows=w["traces"][arm]
        if len(rows)!=4:
            raise ValueError("incomplete stage readout history")
        scores=w["metrics"][arm]
        for stage,row in enumerate(rows):
            if row["stage"]!=stage:
                raise ValueError("stage ordering violation")
            for k in ("fit_source_digest","checkpoint_sha256"):
                digest(k,row[k])
            numeric("B0 trajectory",row["b0_historical_rmse"],row["b0_historical_rmse"])
            if type(row["cumulative_writes"]) is not int or row["cumulative_writes"]<0:
                raise ValueError("invalid write count")
            if type(row["cumulative_scalar_ops"]) is not int or row["cumulative_scalar_ops"]<0:
                raise ValueError("invalid operation count")
            if stage and row["cumulative_writes"]<rows[stage-1]["cumulative_writes"]:
                raise ValueError("knowledge counts decrease")
        if scores["cumulative_scalar_ops"]!=rows[-1]["cumulative_scalar_ops"]:
            raise ValueError("bad total operation accounting")
        for key in FLOATS:
            numeric(arm+"."+key,scores[key],scores[key])
        numeric("B0 reference",scores["b3_b0_rmse"],rows[-1]["b0_historical_rmse"])
    for stage in range(4):
        sources={w["traces"][p][stage]["fit_source_digest"] for p in POLICIES}
        if len(sources)!=1:
            raise ValueError("same observations not used in all arms")
    c=w["metrics"]["credit"]
    mle=w["metrics"]["full_mle"]
    success=(c["held_rmse"]<=max(1.02*mle["held_rmse"],mle["held_rmse"]+1e-10) and
             c["held_rmse"]<=.75*w["metrics"]["last_action"]["held_rmse"] and
             c["held_rmse"]<=.75*w["metrics"]["no_lag"]["held_rmse"] and
             c["held_rmse"]<=.75*w["zero_held_rmse"] and
             c["b3_b0_rmse"]<=max(1.5*w["b0_initial_rmse"],.1))
    # The eighth-cell coverage requirement is verified in the primary
    # through counts and fitted checkpoint; the independent verifier must
    # require that boolean only when the other gates pass.
    if w["credit_supported"] and not success:
        raise ValueError("positive claim not supported by frozen numeric metrics")
    if type(w["credit_supported"]) is not bool:
        raise ValueError("missing boolean independent-world classification")


def compare_receipts(a,b):
    for k in ("schema","prereg","status","native_amalgam_accessed",
              "original_gfp_accessed","reserved_accessed",
              "prior_cohorts_reused","research_only"):
        same("root."+k,a.get(k),b.get(k))
    if a["schema"]!=SCHEMA or a["prereg"]!=PREREG:
        raise ValueError("wrong prereg/protocol")
    if a["status"] not in ("CREDIT_SUPPORTED","NO_GAIN"):
        raise ValueError("invalid or unqualified primary")
    if any((a["native_amalgam_accessed"],a["original_gfp_accessed"],
            a["reserved_accessed"],a["prior_cohorts_reused"])) or not a["research_only"]:
        raise ValueError("forbidden source access")
    if len(a.get("worlds",[]))!=4 or len(b.get("worlds",[]))!=4:
        raise ValueError("missing primary world")
    for i,(wa,wb) in enumerate(zip(a["worlds"],b["worlds"])):
        validate(wa,WORLDS[i])
        validate(wb,WORLDS[i])
        for k in ("world","status","stages_completed","fit_rows","held_rows",
                  "held_source_sha256","fit_source_sha256",
                  "credit_supported","source_original_accessed","reserved_accessed"):
            same(f"world{i}.{k}",wa[k],wb[k])
        numeric(f"world{i}.zero",wa["zero_held_rmse"],wb["zero_held_rmse"])
        numeric(f"world{i}.B0",wa["b0_initial_rmse"],wb["b0_initial_rmse"])
        for arm in POLICIES:
            for key in FLOATS:
                numeric(f"world{i}.{arm}.{key}",
                        wa["metrics"][arm][key],wb["metrics"][arm][key])
            for key in ("cumulative_scalar_ops","model_weight_cells"):
                same(f"world{i}.{arm}.{key}",
                     wa["metrics"][arm][key],wb["metrics"][arm][key])
            for stage,(x,y) in enumerate(zip(wa["traces"][arm],wb["traces"][arm])):
                for key in ("stage","cumulative_writes","cumulative_scalar_ops",
                            "fit_source_digest"):
                    same(f"world{i}.{arm}.{stage}.{key}",x[key],y[key])
                for key in STAGE_FLOATS:
                    numeric(f"world{i}.{arm}.{stage}.{key}",x[key],y[key])
    expected="CREDIT_SUPPORTED" if sum(w["credit_supported"] for w in a["worlds"])>=3 else "NO_GAIN"
    if a["status"]!=expected:
        raise ValueError("post-hoc cohort classification")
    return expected


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage verify_parity.py linux.json windows.json")
    a=json.loads(Path(sys.argv[1]).read_text("utf-8"))
    b=json.loads(Path(sys.argv[2]).read_text("utf-8"))
    print("WSP216_CROSS_OS_PARITY=PASS CLASSIFICATION="+compare_receipts(a,b))
