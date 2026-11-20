#!/usr/bin/env python3
"""GKD-07: historically randomized, public NSW causal-effect prior falsification.

Preregistration FIRST: 872472cf6c068ac9b320491f83e2fd8fdf760564.
No original participant outcome accessed until one frozen exact-head score.
Scientific status is public development only; not an independent original RCT.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
import urllib.request

SOURCE_COMMIT = "1dcc2bf5f955cc1224a3e1307256e1fe86b68dae"
URL = ("https://raw.githubusercontent.com/vincentarelbundock/Rdatasets/"
       + SOURCE_COMMIT + "/csv/causaldata/nsw_mixtape.csv")
PREREG = "872472cf6c068ac9b320491f83e2fd8fdf760564"
FIELDS = ("data_id","treat","age","educ","black","hisp","marr","nodegree","re74","re75","re78")
ALLOWED_HEADERS = (FIELDS, ("rownames",) + FIELDS)
SOURCE_MAX = 150000
P = 185 / 445
SPLITS = {1:(111,37,37),0:(156,52,52)}
ARM_ORDER = ("pooled_randomized_diff","unconstrained_group_diff","interacted_ridge")
MODEL_NAMES = ARM_ORDER + ("donor_monotone","reverse_monotone_sham","same_donor_prior_control")

def guard(q, why):
    if not q:
        raise ValueError("GKD07_FAIL_CLOSED:" + why)

def fetch():
    req = urllib.request.Request(URL,headers={"User-Agent":"Yggdrasil-GKD07-public-historical-RCT/1"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        raw = resp.read(SOURCE_MAX + 1)
    guard(0 < len(raw) <= SOURCE_MAX,"SOURCE_BYTES")
    return raw

def parse(raw):
    guard(isinstance(raw,bytes) and 0 < len(raw) <= SOURCE_MAX,"SOURCE_BOUND")
    try:
        s=raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("GKD07_FAIL_CLOSED:UTF8") from None
    rows=[]
    with io.StringIO(s,newline="") as stream:
        c=csv.DictReader(stream)
        guard(tuple(c.fieldnames or ()) in ALLOWED_HEADERS,"PINNED_HEADER")
        seen=set()
        for row in c:
            guard(set(row)==set(c.fieldnames or ()),"SOURCE_WIDTH")
            ident=row["data_id"]
            guard(isinstance(ident,str) and ident and ident not in seen,"DATA_ID_UNIQUE")
            seen.add(ident)
            try:
                t=float(row["treat"])
                a=float(row["re74"])
                b=float(row["re75"])
                y=float(row["re78"])
            except (ValueError,TypeError):
                raise ValueError("GKD07_FAIL_CLOSED:NONNUMERIC") from None
            guard(t in (0,1) and all(math.isfinite(x) and x>=0 for x in (a,b,y)),"SOURCE_DOMAIN")
            rows.append({"id":ident,"t":int(t),"a":a,"b":b,"y":y,
                         "u":int(a==0 and b==0)})
    guard(len(rows)==445,"SOURCE_N445")
    guard(sum(r["t"] for r in rows)==185,"SOURCE_TREATMENT_BALANCE")
    return {"rows":rows,"source_sha256":hashlib.sha256(raw).hexdigest(),
            "source_bytes":len(raw),"header":list(c.fieldnames or [])}

def split(rows):
    out={"fit":[],"valid":[],"dev":[]}
    for t in (1,0):
        candidates=sorted((x for x in rows if x["t"]==t),
                          key=lambda x:(hashlib.sha256(("GKD07-fold-v1|"+x["id"]).encode()).digest(),x["id"]))
        counts=SPLITS[t]
        guard(len(candidates)==sum(counts),"FOLD_TREATMENT_BALANCE")
        i=0
        for name,n in zip(("fit","valid","dev"),counts):
            out[name].extend(candidates[i:i+n]);i+=n
    guard((len(out["fit"]),len(out["valid"]),len(out["dev"]))==(267,89,89),"SPLIT_SIZES")
    guard(set(x["id"] for group in out.values() for x in group)==
          set(x["id"] for x in rows),"SPLIT_MEMBERS")
    guard(sum(len(g) for g in out.values())==445,"FOLD_DUPLICATE")
    return out

def mean(v):
    guard(len(v)>0,"EMPTY_GROUP")
    return math.fsum(v)/len(v)

def group_effects(fit):
    cells={(u,t):[x["y"] for x in fit if x["u"]==u and x["t"]==t]
           for u in (0,1) for t in (0,1)}
    guard(all(len(v)>=5 for v in cells.values()),"TREATMENT_SUBGROUP_TOO_SMALL")
    diff={u:mean(cells[u,1])-mean(cells[u,0]) for u in (0,1)}
    counts={u:len(cells[u,0])+len(cells[u,1]) for u in (0,1)}
    return diff,counts

def pool_two(d,counts):
    return (counts[0]*d[0]+counts[1]*d[1])/(counts[0]+counts[1])

def fitted_effects(fit):
    d,counts=group_effects(fit)
    pooled=mean([x["y"] for x in fit if x["t"]==1]) - mean([x["y"] for x in fit if x["t"]==0])
    donor=dict(d)
    if donor[1]<donor[0]:
        val=pool_two(d,counts)
        donor={0:val,1:val}
    sham=dict(d)
    if sham[1]>sham[0]:
        val=pool_two(d,counts)
        sham={0:val,1:val}
    guard(donor[1]>=donor[0]-1e-8 and sham[1]<=sham[0]+1e-8,"SHAPE_CONSTRAINT")
    return {"pooled":pooled,"groups":d,"donor":donor,"sham":sham,
            "u_fit_counts":counts}

def solve(A,b):
    n=len(b)
    guard(n>0 and len(A)==n and all(len(row)==n for row in A),"SOLVER_MATRIX")
    aug=[list(A[i])+[b[i]] for i in range(n)]
    for j in range(n):
        q=max(range(j,n),key=lambda k:abs(aug[k][j]))
        guard(abs(aug[q][j])>1e-12,"SINGULAR")
        aug[q],aug[j]=aug[j],aug[q]
        for i in range(j+1,n):
            ratio=aug[i][j]/aug[j][j]
            aug[i][j]=0
            for k in range(j+1,n+1):
                aug[i][k]-=ratio*aug[j][k]
    out=[0.0]*n
    for j in range(n-1,-1,-1):
        out[j]=(aug[j][n]-math.fsum(aug[j][k]*out[k] for k in range(j+1,n)))/aug[j][j]
    guard(all(math.isfinite(x) for x in out),"SOLVER_FINITE")
    return out

def features(x,t):
    u=x["u"]
    a=math.log1p(x["a"])/10
    b=math.log1p(x["b"])/10
    return (1.0,float(t),float(u),float(t*u),a,b,float(t)*a,float(t)*b)

def ridge(fit):
    n=8;gram=[[0.0]*n for _ in range(n)];cross=[0.0]*n
    for row in fit:
        f=features(row,row["t"])
        y=row["y"]/10000
        for j in range(n):
            cross[j]+=f[j]*y
            for k in range(n):
                gram[j][k]+=f[j]*f[k]
    for i in range(n):
        for j in range(i):gram[i][j]=gram[j][i]
        if i>0:gram[i][i]+=1.0
    return solve(gram,cross)

def dot(w,f):
    return math.fsum(a*b for a,b in zip(w,f))

def models(fit):
    eff=fitted_effects(fit)
    w=ridge(fit)
    def pred(arm,x):
        if arm=="pooled_randomized_diff":return eff["pooled"]
        if arm=="unconstrained_group_diff":return eff["groups"][x["u"]]
        if arm in ("donor_monotone","same_donor_prior_control"):return eff["donor"][x["u"]]
        if arm=="reverse_monotone_sham":return eff["sham"][x["u"]]
        if arm=="interacted_ridge":
            return (dot(w,features(x,1))-dot(w,features(x,0)))*10000
        guard(False,"UNKNOWN_ARM")
    return pred,eff,w

def pseudo(x):
    return x["t"]*x["y"]/P - (1-x["t"])*x["y"]/(1-P)

def mse(rows,pred,arm):
    guard(len(rows)>0,"NO_SCORE_ROWS")
    return math.fsum((pseudo(x)-pred(arm,x))**2 for x in rows)/len(rows)

def xorshift(seed):
    s=seed
    def nextn(n):
        nonlocal s
        s^=(s<<13)&0xffffffff
        s^=s>>17
        s^=(s<<5)&0xffffffff
        s&=0xffffffff
        return s%n
    return nextn

def bootstrap(dev,pred,winner):
    nextn=xorshift(7007)
    vals=[]
    for _ in range(2000):
        sample=[dev[nextn(len(dev))] for _ in dev]
        a=math.sqrt(mse(sample,pred,"donor_monotone"))
        b=math.sqrt(mse(sample,pred,winner))
        guard(b>0,"BOOTSTRAP_DENOMINATOR")
        vals.append(1-a/b)
    vals.sort()
    return {"repetitions":2000,"gain_2_5_percentile":vals[49],
            "gain_97_5_percentile":vals[1949]}

def evaluate(source):
    fold=split(source["rows"])
    predict,eff,w=models(fold["fit"])
    val={a:math.sqrt(mse(fold["valid"],predict,a)) for a in MODEL_NAMES}
    winner=min(ARM_ORDER,key=lambda a:(val[a],ARM_ORDER.index(a)))
    dev={a:math.sqrt(mse(fold["dev"],predict,a)) for a in MODEL_NAMES}
    guard(dev["donor_monotone"]==dev["same_donor_prior_control"],"SAME_PRIOR_TIE")
    guard(dev[winner]>0 and dev["reverse_monotone_sham"]>0,"BASELINE_DOMAIN")
    gain=1-dev["donor_monotone"]/dev[winner]
    shamGain=1-dev["donor_monotone"]/dev["reverse_monotone_sham"]
    bs=bootstrap(fold["dev"],predict,winner)
    halves=sorted(fold["dev"],
            key=lambda x:hashlib.sha256(("GKD07-half-v1|"+x["id"]).encode()).digest())
    h=[halves[:44],halves[44:]]
    halfs=[{"n":len(row),"donor_rmse":math.sqrt(mse(row,predict,"donor_monotone")),
            "conventional_rmse":math.sqrt(mse(row,predict,winner)),
            "nonregressing":mse(row,predict,"donor_monotone")<=mse(row,predict,winner)}
           for row in h]
    groups={str(u):{"n":len(g),"donor_rmse":math.sqrt(mse(g,predict,"donor_monotone")),
           "conventional_rmse":math.sqrt(mse(g,predict,winner))}
           for u in (0,1) for g in [[x for x in fold["dev"] if x["u"]==u]] if g}
    success=gain>=.05 and shamGain>=.05 and bs["gain_2_5_percentile"]>0 and all(z["nonregressing"] for z in halfs)
    return {
        "schema":"yggdrasil.gkd07.public-historical-randomized-effect-dev.v1",
        "experiment_id":"GKD-07","prereg_first_commit":PREREG,
        "classification":"PUBLIC_DEV_SIGNAL_SCIENTIFIC_UNVERIFIED" if success else "PUBLIC_DEV_NO_GO",
        "source_repo_ref":SOURCE_COMMIT,"source_path":"csv/causaldata/nsw_mixtape.csv",
        "source_sha256":source["source_sha256"],"source_bytes":source["source_bytes"],
        "rows":{"fit":len(fold["fit"]),"valid":len(fold["valid"]),"dev":len(fold["dev"]),"total":445},
        "experimental_assignment_treated":185,"experimental_assignment_control":260,
        "donor_prior":"Effect for re74==0 and re75==0 is non-smaller than for other pre-earnings histories",
        "fit_u_counts":{str(k):v for k,v in eff["u_fit_counts"].items()},
        "fit_raw_randomized_ate_by_u_usd":{str(k):v for k,v in eff["groups"].items()},
        "donor_constraint_binding":eff["groups"][1]<eff["groups"][0],
        "valid_selected_control":winner,"valid_rmse_by_arm_usd":val,
        "dev_rmse_by_arm_usd":dev,"donor_relative_dev_rmse_gain":gain,
        "donor_relative_dev_gain_vs_reverse_sham":shamGain,
        "bootstrap_paired_gain_interval":bs,
        "dev_half_results":halfs,"dev_u_results":groups,
        "frozen_success":success,"teacher_runtime_calls":0,
        "historical_randomized_intervention":True,"new_interventions_performed":0,
        "native_learner_modified":False,"scientific_gain_verified":False,
        "scientific_pass":False,
        "limitations":[
            "Extensively studied public 1970s randomized trial; GPT donor may have seen earlier literature.",
            "Small single cohort: DEV n=89; wide bootstrap CI, no independent trial or blinded replication.",
            "Unbiased randomized pseudo-outcomes have high individual variance; they do not reveal individual counterfactuals.",
            "The donor effect-ordering inequality was GPT-authored before source scoring, not causally proven.",
            "Same-prior comparator intentionally uses identical algorithm, not independent implementation.",
            "This is a stand-alone source-only evaluator, not native Yggdrasil retention, autonomy or non-token mechanism induction."
        ]}

def selftest():
    known=solve([[2.0,0.0],[0.0,5.0]],[6.0,15.0])
    guard(abs(known[0]-3)<1e-12 and abs(known[1]-3)<1e-12,"SOLVER_TEST")
    f={"id":"test","t":1,"a":0,"b":0,"y":1000,"u":1}
    guard(features(f,1)[2]==1 and features(f,0)[3]==0,"FEATURE_TREATMENT")
    guard(abs(pseudo(f)-1000/P)<1e-9,"PSEUDO_TEST")
    e=[{"id":str(i),"t":t,"a":0 if i%3 else 10,"b":0,"u":int(i%3!=0),
        "y":1000+t*(100+i)} for t in (0,1) for i in range(40)]
    dd,cnt=group_effects(e)
    guard(cnt[0]>0 and cnt[1]>0,"SYNTHETIC_COUNTS")
    fits=fitted_effects(e)
    guard(fits["donor"][1]>=fits["donor"][0]-1e-8,"PRIOR_ORDER")
    guard(fits["sham"][1]<=fits["sham"][0]+1e-8,"SHAM_ORDER")
    # No real CSV opened. Verify deterministic split for synthetic 445 IDs.
    mock=[{"id":"fixture"+str(i),"t":int(i<185),"a":0,"b":0,"y":0,"u":1}
          for i in range(445)]
    folds=split(mock)
    guard([len(folds[g]) for g in ("fit","valid","dev")]==[267,89,89],"FOLD_TEST")
    r1=xorshift(7007);r2=xorshift(7007)
    guard([r1(100) for _ in range(100)]==[r2(100) for _ in range(100)],"RNG_DETERMINISTIC")
    # A malformed synthetic CSV must fail before any inference or model score.
    header=("rownames",)+FIELDS
    original=[{field:str(i) for field in header} for i in range(445)]
    for i,row in enumerate(original):
        row.update({"rownames":str(i+1),"data_id":"fixture"+str(i),
                    "treat":str(int(i<185)),"re74":"0","re75":"0","re78":"0"})
    rows=io.StringIO(newline="")
    w=csv.DictWriter(rows,fieldnames=header);w.writeheader();w.writerows(original)
    parsed=parse(rows.getvalue().encode("utf-8"))
    guard(len(parsed["rows"])==445 and
          parsed["source_sha256"]==hashlib.sha256(rows.getvalue().encode()).hexdigest(),"CSV_ROUNDTRIP")
    invalid=rows.getvalue().replace("fixture1,1,","fixture0,1,",1)
    try:parse(invalid.encode())
    except ValueError as exc:guard("DATA_ID_UNIQUE" in str(exc),"DUPLICATE_TEST")
    else:guard(False,"DUPLICATE_NOT_REJECTED")
    print("GKD07_RCT_SOURCE_FREE_SELFTEST_PASS (445 synthetic IDs, no original outcomes)")

def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest",action="store_true")
    g.add_argument("--score-public",action="store_true")
    args=ap.parse_args()
    if args.selftest:
        selftest()
    else:
        source=parse(fetch())
        result=evaluate(source)
        print("GKD07_PUBLIC_RCT_RESULT="+json.dumps(result,sort_keys=True,separators=(",",":"),allow_nan=False))
        print("GKD07_PUBLIC_RCT_SCORE_CONSUMED_NO_REPLAY")

if __name__=="__main__":
    main()
