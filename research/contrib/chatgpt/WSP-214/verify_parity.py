"""WSP-214 independent source-free result/parity verifier.

Checks two completed platform receipts; never trains, samples, or opens labels.
"""
import json
import math
from pathlib import Path
import sys

SCHEMA = "wsp214.gate-admission.source-free.v1"
PREREG = "905cbef5df7d1cace00231ea4bcd079c0780a1ef"
WORLDS = ((21401,"hub",24),(21402,"complete",12),
          (21403,"hub",24),(21404,"complete",12))
MODELS = ("full_refit","strict_original","budgeted_consensus",
          "budgeted_surprise","budgeted_random","always","no_update")
RESULTS = ("GATE_ADVANTAGE", "LOW_ADMISSION_DIAGNOSTIC",
           "UNDERSELECTION_OBSERVED", "NO_GAIN")
DIAGNOSTIC_KEYS = ("stage","new_addresses","eligible","sign_pass",
                   "mean_pass","both_pass","quarter_budget","k",
                   "strict_selected")
STAGE_KEYS = ("stage","new_rows","cumulative_rows","address_writes",
              "coordinate_solves","source_sha256")
STAGE_NUMERIC = ("objective","b0_mse")
SCORE_NUMERIC = ("held_rmse","b3_b0_mse")
SCORE_INTEGER = ("total_coordinate_solves","total_address_writes")


def metric(label,a,b):
    if type(a) not in (int,float) or type(b) not in (int,float):
        raise ValueError(label+": not numeric")
    if not math.isfinite(a) or not math.isfinite(b):
        raise ValueError(label+": not finite")
    if not math.isclose(a,b,rel_tol=1e-8,abs_tol=1e-8):
        raise ValueError(label+": material numerical OS drift "+str(a)+" vs "+str(b))


def same(label,a,b):
    if a!=b:
        raise ValueError(label+": mismatched source or fixed count")


def sha(label,x):
    if not isinstance(x,str) or len(x)!=64 or any(c not in "0123456789abcdef" for c in x):
        raise ValueError(label+": no canonical SHA256")


def inspect_world(w,idx):
    if (tuple(w["world"]) != WORLDS[idx] or
            w["status"] != "VALID" or w["stages_completed"] != 4 or
            w["original_source_accessed"] or w["reserved_labels_generated"]):
        raise ValueError("world not fully qualified or source accessed")
    if w["fit_groups"]<1 or w["held_groups"]<1:
        raise ValueError("empty partition")
    sha("fit",w["fit_source_sha256"])
    sha("held",w["held_source_sha256"])
    metric("zero held",w["zero_held_rmse"],w["zero_held_rmse"])
    if set(w["trace"])!=set(MODELS) or set(w["scores"])!=set(MODELS):
        raise ValueError("missing matched model")
    if len(w["diagnostics"])!=3:
        raise ValueError("B1-3 diagnostics incomplete")
    for stage,d in enumerate(w["diagnostics"],1):
        if d["stage"] != stage:
            raise ValueError("diagnosis stage identity")
        if (not 0 <= d["both_pass"] <= min(d["sign_pass"],d["mean_pass"]) or
                not max(d["sign_pass"],d["mean_pass"])<=d["eligible"]<=d["new_addresses"] or
                d["quarter_budget"]!=(d["new_addresses"]+3)//4 or
                d["k"]!=min(d["eligible"],d["quarter_budget"]) or
                d["strict_selected"]!=min(d["both_pass"],d["quarter_budget"])):
            raise ValueError("contradiction gate count not coherent")
    for mode in MODELS:
        traces=w["trace"][mode]
        scores=w["scores"][mode]
        if len(traces)!=4:
            raise ValueError("missing stage trajectory")
        for stage,t in enumerate(traces):
            if t["stage"]!=stage or t["new_rows"]<1 or t["coordinate_solves"]<0:
                raise ValueError("bad source/solve stage")
            sha("fit",t["source_sha256"])
            sha("checkpoint",t["checkpoint_sha256"])
            for key in STAGE_NUMERIC:
                metric("self_"+key,t[key],t[key])
            if stage and mode.startswith("budgeted_"):
                k=w["diagnostics"][stage-1]["k"]
                if t["address_writes"]!=k or t["coordinate_solves"]!=2*k:
                    raise ValueError("budget/control parity failure")
        if scores["total_coordinate_solves"]!=sum(x["coordinate_solves"] for x in traces):
            raise ValueError("coordinate solves accounting mismatch")
        if scores["total_address_writes"]!=sum(x["address_writes"] for x in traces):
            raise ValueError("writes accounting mismatch")
        metric("b0",scores["b3_b0_mse"],traces[-1]["b0_mse"])
        metric("held",scores["held_rmse"],scores["held_rmse"])
    c=w["scores"]["budgeted_consensus"]
    s=w["scores"]["strict_original"]
    r=w["scores"]["full_refit"]
    best=min(w["scores"][k]["held_rmse"] for k in ("budgeted_surprise","budgeted_random"))
    recovered=(c["held_rmse"]<=.90*s["held_rmse"])
    gain=(recovered and c["held_rmse"]<=.95*r["held_rmse"] and
          c["held_rmse"]<=.95*best and c["b3_b0_mse"]<=1.05*r["b3_b0_mse"] and
          c["total_coordinate_solves"]<r["total_coordinate_solves"])
    if type(w["strong_gain"]) is not bool or type(w["consensus_better_strict"]) is not bool:
        raise ValueError("untyped world result")
    if gain!=w["strong_gain"] or recovered!=w["consensus_better_strict"]:
        raise ValueError("world result not from frozen metric rules")


def classification(worlds):
    if len(worlds)!=4 or any(w.get("status")!="VALID" for w in worlds):
        return "INVALID"
    low=sum(d["k"]>0 and d["strict_selected"]<=d["k"]//2
            for w in worlds for d in w["diagnostics"])
    recovered=sum(w["consensus_better_strict"] for w in worlds)
    strong=sum(w["strong_gain"] for w in worlds)
    if strong>=3:return "GATE_ADVANTAGE"
    if low>=8 and recovered>=3:return "LOW_ADMISSION_DIAGNOSTIC"
    if low>=8:return "UNDERSELECTION_OBSERVED"
    return "NO_GAIN"


def compare_receipts(linux,windows):
    for key in ("schema","prereg_commit","classification","retired_cohorts_reused",
                "original_gfp_labels_accessed","reserved_labels_accessed",
                "native_amalgam_accessed","research_only"):
        same("root."+key,linux.get(key),windows.get(key))
    if linux.get("schema")!=SCHEMA or linux.get("prereg_commit")!=PREREG:
        raise ValueError("unfrozen prereg identity")
    if linux.get("classification") not in RESULTS:
        raise ValueError("invalid frozen study")
    if (linux.get("retired_cohorts_reused") or
            linux.get("original_gfp_labels_accessed") or
            linux.get("reserved_labels_accessed") or
            linux.get("native_amalgam_accessed") or
            not linux.get("research_only")):
        raise ValueError("source authority violation")
    if len(linux.get("worlds",[]))!=4 or len(windows.get("worlds",[]))!=4:
        raise ValueError("missing world")
    for i,(a,b) in enumerate(zip(linux["worlds"],windows["worlds"])):
        inspect_world(a,i)
        inspect_world(b,i)
        for key in ("world","status","stages_completed","fit_groups",
                    "held_groups","fit_source_sha256","held_source_sha256",
                    "strong_gain","consensus_better_strict",
                    "original_source_accessed","reserved_labels_generated"):
            same(f"world{i}.{key}",a[key],b[key])
        metric(f"world{i}.zero",a["zero_held_rmse"],b["zero_held_rmse"])
        for x,y in zip(a["diagnostics"],b["diagnostics"]):
            for key in DIAGNOSTIC_KEYS:
                same(f"world{i}.diagnostic."+key,x[key],y[key])
        for name in MODELS:
            for key in SCORE_INTEGER:
                same(f"world{i}.{name}."+key,a["scores"][name][key],b["scores"][name][key])
            for key in SCORE_NUMERIC:
                metric(f"world{i}.{name}."+key,a["scores"][name][key],b["scores"][name][key])
            for x,y in zip(a["trace"][name],b["trace"][name]):
                for key in STAGE_KEYS:
                    same(f"world{i}.{name}.stage."+key,x[key],y[key])
                for key in STAGE_NUMERIC:
                    metric(f"world{i}.{name}.stage."+key,x[key],y[key])
    expected=classification(linux["worlds"])
    if linux["classification"]!=expected:
        raise ValueError("post-result classification mismatch")
    return expected


if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("verify_parity.py linux.json windows.json")
    a=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    b=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    print("WSP214_CROSS_OS_PARITY=PASS CLASSIFICATION="+compare_receipts(a,b))
