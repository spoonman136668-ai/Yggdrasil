"""WSP218 independent, read-only Linux/Windows source-free decision verifier.

No environment target generators, no learners, no original/RESERVED data imported.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
import sys

SCHEMA="wsp218.balanced-contextual-credit.v1"
PREREG="a37bced024ff959325f42d5259982dbd2197cb8f"
WORLDS=(21801,21802,21803,21804)
ACTIVE=(0,0,1,1)
MODES=("local","full_context","first_only","last_only","lag_blind",
       "context_omitted","shuffled")
FLOAT_KEYS=("held_rmse","b0_final_rmse")
INT_KEYS=("resident_numeric_scalars","coordinate_solves","cumulative_refit_rows")
TOL=1e-9


def numeric(label,a,b):
    if type(a) not in (int,float) or type(b) not in (int,float):
        raise ValueError(label+": not numeric")
    if not (math.isfinite(a) and math.isfinite(b)):
        raise ValueError(label+": NaN/nonfinite")
    if not math.isclose(a,b,abs_tol=TOL,rel_tol=TOL):
        raise ValueError(label+f": cross-platform drift {a!r} {b!r}")


def same(label,a,b):
    if a!=b:raise ValueError(label+": source/identity/cost divergence")


def digest(label,s):
    if not isinstance(s,str) or len(s)!=64 or any(
            c not in "0123456789abcdef" for c in s):
        raise ValueError(label+": invalid SHA256")


def inspect_world(w,idx):
    if (w.get("world")!=WORLDS[idx] or w.get("status")!="VALID" or
            w.get("stage_count")!=4 or w.get("fit_rows")!=200 or
            w.get("held_pairs")!=100 or
            w.get("original_gfp_accessed") or w.get("reserved_accessed")):
        raise ValueError("invalid finished world/source safety")
    for key in ("fit_source_sha256","held_sha256"):
        digest(key,w[key])
    if set(w["scores"])!=set(MODES) or set(w["traces"])!=set(MODES):
        raise ValueError("incomplete comparison arm")
    numeric("zero",w["zero_held_rmse"],w["zero_held_rmse"])
    numeric("oracle",w["oracle_held_rmse"],w["oracle_held_rmse"])
    if w["active_lag_postfit"]!=ACTIVE[idx]:
        raise ValueError("not balanced frozen true active lag")
    wrong="last_only" if ACTIVE[idx]==0 else "first_only"
    right="first_only" if ACTIVE[idx]==0 else "last_only"
    if w["wrong_control_postfit"]!=wrong or w["right_control_postfit"]!=right:
        raise ValueError("frozen truth-conditioned comparator incorrectly selected")
    mags=w["lag_energy"]
    if len(mags)!=2:raise ValueError("missing action effect lag-energy diagnostics")
    for num in mags:numeric("lag energy",num,num)
    lag_found=mags[ACTIVE[idx]]>1.5*mags[1-ACTIVE[idx]]
    if type(w["lag_identified"]) is not bool or w["lag_identified"]!=lag_found:
        raise ValueError("postfit active lag flag inconsistent")
    for mode in MODES:
        s=w["scores"][mode]
        traces=w["traces"][mode]
        if len(traces)!=4:raise ValueError("incomplete frozen four-stage memory")
        for stage,t in enumerate(traces):
            if t["stage"]!=stage or t["rows_seen"]!=50*(stage+1):
                raise ValueError("invalid/replayed stage")
            digest("staged source",t["fit_source_sha256"])
            digest("cold snapshot",t["checkpoint_sha256"])
            numeric("B0 historical",t["b0_historical_rmse"],t["b0_historical_rmse"])
            if mode=="local":
                if (t["coordinate_solves"]!=60*16*3*(stage+1) or
                        t["scalar_accumulations"]<=0 or
                        t["cumulative_refit_rows"]!=0):
                    raise ValueError("bad bounded local cost/no-raw-replay receipts")
            elif (t["coordinate_solves"]!=0 or t["scalar_accumulations"]!=0 or
                  t["cumulative_refit_rows"]!=50*(stage+1)*(stage+2)//2):
                raise ValueError("full cumulative conventional fit not executed")
        for key in FLOAT_KEYS:
            numeric(mode+"."+key,s[key],s[key])
        numeric("B0 final stage",s["b0_final_rmse"],traces[-1]["b0_historical_rmse"])
        if mode=="local":
            if (s["resident_numeric_scalars"]!=352 or
                    s["coordinate_solves"]!=60*16*3*4 or
                    s["cumulative_refit_rows"]!=0):
                raise ValueError("local fixed-footprint/nonreplay violated")
        elif s["cumulative_refit_rows"]!=500:
            raise ValueError("full-refit arm not cumulatively retrained")
    for stage in range(4):
        if len({w["traces"][mode][stage]["fit_source_sha256"] for mode in MODES})!=1:
            raise ValueError("arms not matched information/action exposures")
    local=w["scores"]["local"]
    strong=w["scores"]["full_context"]
    verdict=(
        local["held_rmse"]<=max(1.1*strong["held_rmse"],strong["held_rmse"]+.02) and
        local["held_rmse"]<=.75*w["scores"][wrong]["held_rmse"] and
        local["held_rmse"]<=.75*w["scores"]["lag_blind"]["held_rmse"] and
        local["held_rmse"]<=.75*w["scores"]["shuffled"]["held_rmse"] and
        local["held_rmse"]<=.60*w["zero_held_rmse"] and
        lag_found and
        local["b0_final_rmse"]<=max(
            1.2*w["traces"]["local"][0]["b0_historical_rmse"],
            w["traces"]["local"][0]["b0_historical_rmse"]+.02))
    if type(w["world_supported"]) is not bool or w["world_supported"]!=verdict:
        raise ValueError("posthoc world reclassification")


def compare_receipts(a,b):
    for k in ("schema","prereg","classification",
              "original_gfp_accessed","reserved_accessed",
              "prior_cohorts_reused","native_amalgam_accessed","research_only"):
        same("root."+k,a.get(k),b.get(k))
    if a.get("schema")!=SCHEMA or a.get("prereg")!=PREREG:
        raise ValueError("wrong prereg and source identity")
    if a.get("classification") not in ("BALANCED_CREDIT_SUPPORTED","NO_GAIN"):
        raise ValueError("invalid or incomplete primary is not scientific result")
    if (a["original_gfp_accessed"] or a["reserved_accessed"] or
            a["prior_cohorts_reused"] or a["native_amalgam_accessed"] or
            not a["research_only"]):
        raise ValueError("source first-use/authority fence failure")
    if len(a.get("worlds",[]))!=4 or len(b.get("worlds",[]))!=4:
        raise ValueError("cohort incomplete")
    for idx,(x,y) in enumerate(zip(a["worlds"],b["worlds"])):
        inspect_world(x,idx);inspect_world(y,idx)
        for k in ("world","status","stage_count","fit_rows","held_pairs",
                  "fit_source_sha256","held_sha256","active_lag_postfit",
                  "wrong_control_postfit","right_control_postfit",
                  "lag_identified","world_supported","original_gfp_accessed",
                  "reserved_accessed"):
            same(f"world{idx}.{k}",x[k],y[k])
        for key in ("zero_held_rmse","oracle_held_rmse"):
            numeric(f"world{idx}.{key}",x[key],y[key])
        for i,(v,w) in enumerate(zip(x["lag_energy"],y["lag_energy"])):
            numeric(f"world{idx}.lag_energy{i}",v,w)
        for mode in MODES:
            for key in FLOAT_KEYS:
                numeric(f"world{idx}.{mode}.{key}",
                        x["scores"][mode][key],y["scores"][mode][key])
            for key in INT_KEYS:
                same(f"world{idx}.{mode}.{key}",
                     x["scores"][mode][key],y["scores"][mode][key])
            for stage,(r,s) in enumerate(zip(x["traces"][mode],y["traces"][mode])):
                for key in ("stage","rows_seen","fit_source_sha256",
                            "scalar_accumulations","coordinate_solves",
                            "cumulative_refit_rows"):
                    same(f"world{idx}.{mode}.B{stage}.{key}",r[key],s[key])
                numeric(f"world{idx}.{mode}.B{stage}.retention",
                        r["b0_historical_rmse"],s["b0_historical_rmse"])
    label=("BALANCED_CREDIT_SUPPORTED" if
           sum(w["world_supported"] for w in a["worlds"])>=3 else "NO_GAIN")
    if a["classification"]!=label:
        raise ValueError("frozen aggregate classification changed")
    return label


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: verify_parity.py linux.json windows.json")
    a=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    b=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    print("WSP218_CROSS_OS_PARITY=PASS CLASSIFICATION="+compare_receipts(a,b))
