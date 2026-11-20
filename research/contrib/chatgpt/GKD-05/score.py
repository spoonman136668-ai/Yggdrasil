#!/usr/bin/env python3
"""GKD-05 published Sachs public-DEV condition holdout, stdlib-only.

First pre-data preregistration aafab21d6b8997ffafd355de528c9eb1cd7dfa0a.
DONOR is a static GPT-authored two-parent mask. No teacher inference, no
protected owner-world actions, no native Yggdrasil training or inference.
This is same-cell conditional prediction, NOT intervention-effect estimation.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
import sys
import time
import zipfile
from pathlib import PurePosixPath
from admit import (SOURCE_MD5, FIELDS, FIT, VALID, DEV, SIM,
                   fetch_bounded, admit_archive, guard)

TARGETS = ("Erk", "Akt", "P38", "Jnk")
PARENTS = {
    "Erk": ("Raf", "Mek"),
    "Akt": ("PIP3", "Erk"),
    "P38": ("PKC", "Plcg"),
    "Jnk": ("PKC", "Plcg"),
}
ALPHAS = (0.001, 0.1, 1.0, 10.0, 100.0, 1000.0)
ARMS = ("full_ridge", "quadratic_ridge", "top2_abs_correlation",
        "donor_mask", "same_mask_symbolic_control", "sham_shift2", "fit_target_mean")


def read_source(raw: bytes) -> dict:
    admission = admit_archive(raw)
    dataset = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        mapping = {PurePosixPath(i.filename).name: i for i in z.infolist() if not i.is_dir()}
        for group in FIT + VALID + DEV:
            with io.StringIO(z.read(mapping[group]).decode("utf-8-sig"), newline="") as f:
                rows = csv.DictReader(f)
                guard(tuple(rows.fieldnames or ()) and set(rows.fieldnames or ()) == set(FIELDS),
                      "SCORE_HEADER:" + group)
                arr = []
                for row in rows:
                    guard(set(row) == set(FIELDS) and all(row[k] is not None for k in FIELDS),
                          "SCORE_SCHEMA:" + group)
                    try:
                        record = tuple(float(row[k]) for k in FIELDS)
                    except (ValueError, TypeError):
                        raise ValueError("GKD05_SOURCE_NO_GO:NONNUMERIC:" + group) from None
                    guard(all(math.isfinite(x) for x in record), "NONFINITE:" + group)
                    arr.append(record)
                guard(len(arr) == admission[
                    "fit" if group in FIT else "valid" if group in VALID else "dev"][group]["rows"],
                    "SOURCE_ROW_PARITY:" + group)
                dataset[group] = arr
    guard(len(dataset) == 9 and not (set(dataset) & set(SIM)), "SYNTHETIC_LEAKAGE")
    return {"admission": admission, "rows": dataset}


def mean_sd(v: list[float]) -> tuple[float, float]:
    guard(len(v) >= 2, "NOT_ENOUGH_FIT")
    mean = math.fsum(v) / len(v)
    variance = math.fsum((x-mean)**2 for x in v) / len(v)
    sd = math.sqrt(variance)
    guard(math.isfinite(sd) and sd > 1e-12, "ZERO_STANDARD_DEVIATION")
    return mean, sd


def fit_prepare(rows: dict, target: str) -> dict:
    guard(target in TARGETS, "TARGET_NOT_FROZEN")
    idx = FIELDS.index(target)
    attrs = tuple(name for name in FIELDS if name != target)
    xi = [FIELDS.index(name) for name in attrs]
    pooled = [row for group in FIT for row in rows[group]]
    guard(len(pooled) > 3000, "FIT_COUNT_LOW")
    xm = [mean_sd([row[i] for row in pooled]) for i in xi]
    ym, ys = mean_sd([row[idx] for row in pooled])

    def from_group(g: str) -> list[tuple[tuple[float, ...], float]]:
        return [(tuple((row[i] - xm[j][0])/xm[j][1] for j,i in enumerate(xi)),
                 (row[idx]-ym)/ys) for row in rows[g]]

    data = {g: from_group(g) for g in FIT + VALID + DEV}
    return {"attrs": attrs, "source": data, "target_mean": ym, "target_sd": ys}


def feature_rows(data: list, arm: str, use_idx: tuple[int,...]) -> list[tuple[float,...]]:
    if arm == "quadratic_ridge":
        out = []
        for inputs,_ in data:
            z = tuple(inputs)
            out.append(z+tuple(v*v for v in z)+tuple(z[i]*z[j]
                         for i in range(len(z)) for j in range(i+1,len(z))))
        return out
    return [tuple(inputs[i] for i in use_idx) for inputs,_ in data]


def solve(a: list[list[float]], b: list[float]) -> list[float]:
    # Independent deterministic column-pivot-free Gaussian elimination with
    # max-absolute ROW pivot; diagonal ridge makes normal matrix PD.
    n = len(b)
    guard(n > 0 and len(a) == n and all(len(r) == n for r in a), "SOLVE_SIZE")
    mat = [row[:] + [b[i]] for i,row in enumerate(a)]
    for c in range(n):
        pivot = max(range(c,n), key=lambda r: abs(mat[r][c]))
        guard(abs(mat[pivot][c]) > 1e-14, "SINGULAR_FIT")
        mat[c],mat[pivot] = mat[pivot],mat[c]
        denom=mat[c][c]
        for j in range(c,n+1):
            mat[c][j] /= denom
        for row in range(c+1,n):
            f = mat[row][c]
            if f:
                for j in range(c+1,n+1):
                    mat[row][j] -= f*mat[c][j]
                mat[row][c] = 0.0
    out = [0.0]*n
    for i in range(n-1,-1,-1):
        out[i] = mat[i][n]-math.fsum(mat[i][j]*out[j] for j in range(i+1,n))
    guard(all(math.isfinite(q) for q in out), "NONFINITE_COEFFICIENTS")
    return out


def gram_and_cross(zrows: list[tuple[float,...]], y: list[float]):
    n = len(zrows)
    guard(n == len(y) and n > 10, "GRAM_ROWS")
    p=len(zrows[0])
    guard(1 <= p <= 65 and all(len(row)==p for row in zrows), "GRAM_DIM")
    mz=[math.fsum(row[j] for row in zrows)/n for j in range(p)]
    scales=[]
    for j in range(p):
        sd=math.sqrt(math.fsum((row[j]-mz[j])**2 for row in zrows)/n)
        guard(sd > 1e-12 and math.isfinite(sd), "CONSTANT_FEATURE")
        scales.append(sd)
    my=math.fsum(y)/n
    gram=[[0.0]*p for _ in range(p)]
    cross=[0.0]*p
    for row,outcome in zip(zrows,y):
        q=[(row[j]-mz[j])/scales[j] for j in range(p)]
        yc=outcome-my
        for j in range(p):
            cross[j] += q[j]*yc
            for k in range(j,p):
                gram[j][k] += q[j]*q[k]
    for j in range(p):
        for k in range(j):
            gram[j][k]=gram[k][j]
    return {"gram":gram, "cross":cross, "mx":mz, "sx":scales, "my":my}


def model_for_alpha(st: dict, alpha: float) -> dict:
    g=[r[:] for r in st["gram"]]
    for j in range(len(g)):
        g[j][j] += alpha
    return {"coef":solve(g,st["cross"]), "mx":st["mx"],"sx":st["sx"],"intercept":st["my"]}


def predict(model: dict, z: tuple[float,...]) -> float:
    out=model["intercept"]+math.fsum(
        v*(z[j]-model["mx"][j])/model["sx"][j]
        for j,v in enumerate(model["coef"]))
    guard(math.isfinite(out), "NONFINITE_PREDICTION")
    return out


def normalized_rmse(model, z, y) -> float:
    guard(len(z)==len(y)>0, "SCORING_LENGTH")
    v=math.sqrt(math.fsum((predict(model,x)-truth)**2 for x,truth in zip(z,y))/len(z))
    guard(math.isfinite(v), "NONFINITE_RMSE")
    return v


def top2_fit_only(prepared) -> tuple[int,...]:
    data=[r for g in FIT for r in prepared["source"][g]]
    attrs=prepared["attrs"]
    corrs=[]
    for j,name in enumerate(attrs):
        x=[a[j] for a,_ in data]
        y=[b for _,b in data]
        # X and target each have unit FIT std by construction.
        r=abs(math.fsum(t*v for t,v in zip(x,y))/len(data))
        corrs.append((-r,name,j))
    corrs.sort()
    return tuple(sorted(corrs[i][2] for i in range(2)))


def indexes(attrs, names) -> tuple[int,...]:
    guard(len(names)==2 and len(set(names))==2
          and all(k in attrs for k in names), "PARENT_NAMES")
    return tuple(attrs.index(k) for k in names)


def get_sham(target: str) -> tuple[str,...]:
    i=TARGETS.index(target)
    names=PARENTS[TARGETS[(i+2)%4]]
    guard(target not in names, "SHAM_TARGET_LEAK")
    return names


def fit_arm(prepared: dict, target: str, arm: str) -> dict:
    guard(arm in ARMS, "ARM_NOT_FROZEN")
    attrs=prepared["attrs"]
    if arm in ("donor_mask","same_mask_symbolic_control"):
        chosen=indexes(attrs,PARENTS[target])
    elif arm=="sham_shift2":
        chosen=indexes(attrs,get_sham(target))
    elif arm=="top2_abs_correlation":
        chosen=top2_fit_only(prepared)
    else:
        chosen=tuple(range(len(attrs)))
    data=prepared["source"]
    groups={g:feature_rows(data[g],arm,chosen) for g in FIT+VALID+DEV}
    if arm=="fit_target_mean":
        model={"coef":[],"mx":[],"sx":[],"intercept":0.0}
        # In standardized FIT-y space, constant FIT target mean=0.
        return {"arm":arm,"alpha":None,"model":model,"groups":groups,
                "selected_parents":[],"valid_rmse":math.sqrt(sum(
                  math.fsum(y*y for _,y in data[g])/len(data[g]) for g in VALID)/2)}
    fitfeatures=[row for g in FIT for row in groups[g]]
    fity=[y for g in FIT for _,y in data[g]]
    stats=gram_and_cross(fitfeatures,fity)
    best=None
    for alpha in ALPHAS:
        model=model_for_alpha(stats,alpha)
        score=math.fsum(normalized_rmse(model,groups[g],[y for _,y in data[g]])
                        for g in VALID)/len(VALID)
        if best is None or score < best["valid_rmse"]-1e-12:
            best={"arm":arm,"alpha":alpha,"model":model,"groups":groups,
                  "selected_parents":[attrs[i] for i in chosen],
                  "valid_rmse":score}
    return best


def evaluate(source: dict) -> dict:
    data=source["rows"]
    groups=FIT+VALID+DEV
    by_target={}
    for target in TARGETS:
        prepared=fit_prepare(data,target)
        arms={arm:fit_arm(prepared,target,arm) for arm in ARMS}
        # Same exact mask and fitting implementation is an intentional
        # strong equal-information tie, NOT a native advantage.
        d=arms["donor_mask"];same=arms["same_mask_symbolic_control"]
        guard(d["alpha"]==same["alpha"] and d["model"]==same["model"],
              "SAME_MASK_CONTROL_NOT_EQUAL")
        measurements={}
        for arm,mod in arms.items():
            measurements[arm]={
                group:normalized_rmse(mod["model"],mod["groups"][group],
                      [y for _,y in prepared["source"][group]])
                for group in VALID+DEV
            }
        by_target[target]={
            "fitted_alpha":{arm:arms[arm]["alpha"] for arm in ARMS},
            "parents":{arm:arms[arm]["selected_parents"] for arm in ARMS},
            "validation_rmse":{arm:arms[arm]["valid_rmse"] for arm in ARMS},
            "per_group_normalized_rmse":measurements,
            "fit_target_standard_deviation":prepared["target_sd"]
        }
    def agg(arm: str, groups: tuple[str,...]) -> float:
        return math.fsum(by_target[t]["per_group_normalized_rmse"][arm][g]
                         for t in TARGETS for g in groups)/(len(TARGETS)*len(groups))
    controls=("full_ridge","quadratic_ridge","top2_abs_correlation")
    # Control choice fixed by VALID only, no DEV outcomes.
    winner=min(controls,key=lambda m:(agg(m,VALID),controls.index(m)))
    donor_dev=agg("donor_mask",DEV);strong_dev=agg(winner,DEV)
    sham_dev=agg("sham_shift2",DEV)
    guard(strong_dev>0 and sham_dev>0, "ZERO_BASELINE_ERROR")
    positive=1-donor_dev/strong_dev
    vs_sham=1-donor_dev/sham_dev
    group_scores=[]
    for t in TARGETS:
        for g in DEV:
            a=by_target[t]["per_group_normalized_rmse"]["donor_mask"][g]
            b=by_target[t]["per_group_normalized_rmse"][winner][g]
            group_scores.append({
                "target":t,"group":g,"donor_rmse":a,"strong_rmse":b,
                "relative_gain":(1-a/b if b>0 else None),
                "no_more_than_5_percent_regression":a<=1.05*b,
                "nonregression":a<=b
            })
    no_bad=all(q["no_more_than_5_percent_regression"] for q in group_scores)
    num_nonreg=sum(q["nonregression"] for q in group_scores)
    passed=positive>=0.05 and vs_sham>=0.05 and no_bad and num_nonreg>=6
    archive=source["admission"]
    return {
        "schema":"yggdrasil.gkd05.public-real-intervention-conditional-dev.v1",
        "experiment_id":"GKD-05",
        "preregistration_commit":"aafab21d6b8997ffafd355de528c9eb1cd7dfa0a",
        "classification":"PUBLIC_DEV_SIGNAL_SCIENTIFIC_UNVERIFIED" if passed else "PUBLIC_DEV_NO_GO",
        "source_archive_md5":archive["archive_md5"],
        "source_archive_sha256":archive["archive_sha256"],
        "original_real_groups":9,"excluded_simulated_groups":5,
        "fit_row_count":sum(archive["fit"][g]["rows"] for g in FIT),
        "valid_row_count":sum(archive["valid"][g]["rows"] for g in VALID),
        "dev_row_count":sum(archive["dev"][g]["rows"] for g in DEV),
        "source_member_sha256":{
            key:archive[part][key]["sha256"] for part in ("fit","valid","dev")
            for key in archive[part]
        },
        "valid_selected_strong_control":winner,
        "validation_average_rmse_by_arm":{arm:agg(arm,VALID) for arm in ARMS},
        "dev_average_rmse_by_arm":{arm:agg(arm,DEV) for arm in ARMS},
        "donor_relative_gain_vs_valid_selected_strong_control":positive,
        "donor_relative_gain_vs_sham":vs_sham,
        "dev_target_groups_nonregressing":num_nonreg,
        "dev_target_groups_with_no_more_than_5_percent_regression":
            sum(q["no_more_than_5_percent_regression"] for q in group_scores),
        "dev_individual_groups":group_scores,
        "target_results":by_target,
        "frozen_signal_pass":passed,
        "scientific_gain_verified":False,
        "native_learner_changed":False,
        "environment_actions":0,
        "teacher_runtime_calls":0,
        "limits":[
            "Published 2005 interventional groups are previously used public DEV, not virgin scientific first use.",
            "Same-cell conditional outcome prediction under condition shift is NOT intervention-effect causal estimation.",
            "GPT author may have encountered published Sachs ground truth in pretraining or metadata search.",
            "Same-donor-knowledge conventional ridge control ties exactly; source graph not proven.",
            "Two held-out groups provide insufficient independent condition-replication significance.",
            "No accepted native Yggdrasil learner or durable knowledge state modified."
        ]
    }


def selftest() -> None:
    # Source-free numeric engineering controls. No original sample is read.
    a=[[7.0,0.0],[0.0,5.0]]
    x=solve(a,[14,10])
    guard(abs(x[0]-2)<1e-12 and abs(x[1]-2)<1e-12, "SELFTEST_SOLVER")
    samples=[((i/9, (i*i)/81), 3+2*(i/9)-.5*(i*i)/81) for i in range(1,20)]
    st=gram_and_cross([x for x,_ in samples],[y for _,y in samples])
    fit=model_for_alpha(st,0.001)
    guard(normalized_rmse(fit,[x for x,_ in samples],[y for _,y in samples])<0.0005,
          "SELFTEST_RIDGE")
    guard(get_sham("Erk") == ("PKC","Plcg")
          and get_sham("Jnk") == ("PIP3","Erk"), "SELFTEST_SHAM_SCOPE")
    guard(len(FIT)==5 and len(VALID)==2 and len(DEV)==2, "SELFTEST_SPLIT")
    print("GKD05_PUBLIC_FIT_SELFTEST_PASS; no original data")


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--selftest",action="store_true")
    p.add_argument("--score-public",action="store_true")
    options=p.parse_args()
    guard(options.selftest != options.score_public, "MODE")
    if options.selftest:
        selftest()
    else:
        started=time.perf_counter()
        source=read_source(fetch_bounded())
        result=evaluate(source)
        result["elapsed_s"]=round(time.perf_counter()-started,6)
        print("GKD05_PUBLIC_ORIGINAL_DEV_RESULT=" +
              json.dumps(result,sort_keys=True,separators=(",",":"),allow_nan=False))
        print("GKD05_PUBLIC_SCORE_COMPLETED_NO_REPLAY; do not tune consumed public DEV")


if __name__=="__main__":
    main()
