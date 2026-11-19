"""WSP-187: source-safe learned compact temporal state on ORIGINAL physical light-tunnel data.

Preregistered BEFORE opening any new numerical measurements:
  WSP-187/prereg.json @ bcfc09c5438fc1e931eecddc60c2661415ecb75e.
A learned two-dimensional sensor-innovation subspace is NOT by itself
identifiable causal structure. Fully fitted ARX and residual-recurrence
conventional controls have precisely equal public evidence.
Never constructs an original world or issues a live physical action.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import statistics
import time
import zipfile

SOURCE = "juangamella/causal-chamber@967d59a42956872f37463cc561ecf6e9ceab9364"
DATASET = "lt_walks_v1"
UPSTREAM_MD5 = "dcad019186661a56de7a2d1db97fc2f0"
SCHEMA = "yggdrasil.wsp187.original-light-latent-public-dev.v1"
ROSTER = ("actuators_white", "color_mix", "smooth_polarizers")
INPUTS = ("red","green","blue","pol_1","pol_2","l_31","l_32")
OUTPUTS = ("vis_1","vis_2","vis_3")
FIT_STOP = 7000
PER_SOURCE_ROWS = 10000
FEAT = 1 + len(INPUTS) + 4  # 12 current-public features
RIDGE = 0.1
RANK = 2
PCA_ITERS = 48
GAIN = 0.05
PATIENCE = 3
THRESHOLD = 2.0
CAP = 0.5
DECAY = 0.995
EMA_GAIN = 0.1
MAX_ARCHIVE = 180_000_000
MAX_MEMBER = 75_000_000
MAX_EXPANDED = 350_000_000
ARMS = ("batch","arx","full_lag","lowrank","gated","ema","persistence")
CONTROLS = ("batch","arx","full_lag","lowrank","ema","persistence")


def read_float(text: str) -> float:
    try:
        val = float(text)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError("WSP187_NUMERIC_RECORD") from exc
    if not math.isfinite(val):
        raise ValueError("WSP187_NONFINITE")
    return val


def parse_recording(blob: bytes, source: str):
    reader = csv.DictReader(io.StringIO(blob.decode("utf-8-sig"), newline=""))
    cols = reader.fieldnames
    if not cols or len(cols)!=len(set(cols)) or not set(INPUTS+OUTPUTS).issubset(cols):
        raise ValueError("WSP187_ORIGINAL_SOURCE_COLUMNS")
    points=[]
    for row in reader:
        x=tuple(read_float(row[col]) for col in INPUTS)
        y=tuple(read_float(row[col]) for col in OUTPUTS)
        points.append((x,y))
        if len(points)>PER_SOURCE_ROWS:
            raise ValueError("WSP187_SOURCE_ROWCOUNT")
    if len(points)!=PER_SOURCE_ROWS:
        raise ValueError("WSP187_SOURCE_ROWCOUNT")
    return points


def admit(path: Path):
    if not path.is_file() or not 0<path.stat().st_size<=MAX_ARCHIVE:
        raise ValueError("WSP187_ARCHIVE_BYTES")
    raw=path.read_bytes()
    md5=hashlib.md5(raw).hexdigest()  # Author-published checksum only
    if md5!=UPSTREAM_MD5:
        raise ValueError("WSP187_PUBLISHED_HASH")
    details={}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        files={}
        expanded=0
        for item in archive.infolist():
            name=PurePosixPath(item.filename)
            if name.is_absolute() or ".." in name.parts:
                raise ValueError("WSP187_ZIP_TRAVERSAL")
            expanded+=item.file_size
            if item.file_size>MAX_MEMBER or expanded>MAX_EXPANDED:
                raise ValueError("WSP187_UNCOMPRESSED_BUDGET")
            if item.is_dir() or name.stem not in ROSTER:
                continue
            if name.suffix != ".csv" or name.stem in files:
                raise ValueError("WSP187_ROSTER_COLLISION")
            files[name.stem]=item
        if set(files)!=set(ROSTER):
            raise ValueError("WSP187_ORIGINAL_ROSTER")
        samples={}
        for name in ROSTER:
            with archive.open(files[name]) as stream:
                blob=stream.read(MAX_MEMBER+1)
            if len(blob)>MAX_MEMBER:
                raise ValueError("WSP187_MEMBER_BYTES")
            details[name]={"sha256":hashlib.sha256(blob).hexdigest(),
                           "bytes":len(blob)}
            samples[name]=parse_recording(blob,name)
    return samples,{"source":SOURCE,"dataset":DATASET,
                    "author_md5":md5,"zip_sha256":hashlib.sha256(raw).hexdigest(),
                    "members":details}


def norm(vec,mu,std):
    return tuple((x-a)/b for x,a,b in zip(vec,mu,std))


def stats(rows):
    columns=list(zip(*rows))
    mean=tuple(statistics.fmean(col) for col in columns)
    sd=tuple(statistics.pstdev(col) for col in columns)
    if any(not math.isfinite(v) or v<=1e-10 for v in sd):
        raise ValueError("WSP187_ZERO_FIT_VARIANCE")
    return mean,sd


def features(x, model):
    v=norm(x,model["xmu"],model["xsd"])
    # Polarizer transforms are fixed, not fitted on public DEV.
    angle1,angle2=(math.radians(2*x[k]) for k in (3,4))
    return (1.,)+v+(math.sin(angle1),math.cos(angle1),
                      math.sin(angle2),math.cos(angle2))


def solve(mat,rhs):
    d=len(rhs)
    a=[list(mat[i])+[rhs[i]] for i in range(d)]
    for i in range(d):
        pivot=max(range(i,d),key=lambda k:abs(a[k][i]))
        a[i],a[pivot]=a[pivot],a[i]
        if abs(a[i][i])<1e-13:
            raise ValueError("WSP187_FIT_SINGULAR")
        f=a[i][i]
        a[i]=[x/f for x in a[i]]
        for j in range(d):
            if j==i: continue
            q=a[j][i]
            a[j]=[x-q*y for x,y in zip(a[j],a[i])]
    return tuple(row[-1] for row in a)


def ridge(rows,dim,outputs=3,lam=RIDGE):
    gram=[[float(i==j)*lam for j in range(dim)] for i in range(dim)]
    resp=[[0.]*outputs for _ in range(dim)]
    n=0
    for x,y in rows:
        if len(x)!=dim or len(y)!=outputs:
            raise ValueError("WSP187_TRAINING_DIMENSIONS")
        n+=1
        for i in range(dim):
            xi=x[i]
            for j in range(dim):
                gram[i][j]+=xi*x[j]
            for k in range(outputs):
                resp[i][k]+=xi*y[k]
    if not n: raise ValueError("WSP187_NO_TRAINING_EXAMPLES")
    return tuple(solve(gram,tuple(resp[i][k] for i in range(dim)))
                 for k in range(outputs))


def read(weights,x):
    return tuple(sum(a*b for a,b in zip(row,x)) for row in weights)


def residual_cov(res):
    n=len(res)
    if n<8:raise ValueError("WSP187_TOO_FEW_RESIDUALS")
    return [[statistics.fmean(v[i]*v[j] for v in res)
             for j in range(3)] for i in range(3)]


def projection(res):
    """Deterministic principal FIT-only sensor-innovation subspace.

    Two learned axes from actual source FIT residual covariance; no target
    label, future source observation or original causal-graph oracle.
    """
    c=residual_cov(res)
    result=[]
    for initial in ((1.,0.67,0.31),(0.19,1.,0.73)):
        vec=list(initial)
        for _ in range(PCA_ITERS):
            nxt=[sum(c[i][j]*vec[j] for j in range(3)) for i in range(3)]
            for old in result:
                d=sum(a*b for a,b in zip(nxt,old))
                nxt=[x-d*y for x,y in zip(nxt,old)]
            mag=math.sqrt(sum(x*x for x in nxt))
            if not math.isfinite(mag) or mag<1e-12:
                raise ValueError("WSP187_DEGENERATE_LATENT")
            vec=[v/mag for v in nxt]
        eigen=sum(vec[i]*sum(c[i][j]*vec[j] for j in range(3))
                  for i in range(3))
        if eigen<1e-9:
            raise ValueError("WSP187_LATENT_NO_INFORMATION")
        major=max(range(3),key=lambda k:abs(vec[k]))
        if vec[major]<0:vec=[-v for v in vec]
        result.append(tuple(vec))
    return tuple(result)


def project(basis,residual):
    return tuple(sum(a*b for a,b in zip(axis,residual)) for axis in basis)


def fit(fit_rows):
    xm,xs=stats([r[0] for r in fit_rows])
    ym,ys=stats([r[1] for r in fit_rows])
    model={"xmu":xm,"xsd":xs,"ymu":ym,"ysd":ys}
    inputs=[features(x,model) for x,_ in fit_rows]
    outcomes=[norm(y,ym,ys) for _,y in fit_rows]
    batch=ridge(zip(inputs,outcomes),FEAT)
    residuals=[tuple(y[k]-read(batch,x)[k] for k in range(3))
               for x,y in zip(inputs,outcomes)]
    basis=projection(residuals)
    latent=[project(basis,r) for r in residuals]
    lowrank=ridge(((latent[i-1],residuals[i])
                   for i in range(1,len(residuals))),RANK)
    full_lag=ridge(((residuals[i-1],residuals[i])
                    for i in range(1,len(residuals))),3)
    arx=ridge(((inputs[i]+outcomes[i-1],outcomes[i])
               for i in range(1,len(inputs))),FEAT+3)
    innovation_std=tuple(math.sqrt(statistics.fmean(
        (residuals[i][k]-read(lowrank,latent[i-1])[k])**2
        for i in range(1,len(residuals)))) for k in range(3))
    if any(v<=1e-9 for v in innovation_std):
        raise ValueError("WSP187_NO_INNOVATION_VARIANCE")
    model.update({"batch":batch,"arx":arx,"full_lag":full_lag,
                  "basis":basis,"lowrank":lowrank,"innovation_std":innovation_std,
                  "FIT_rows":len(fit_rows)})
    return model


def frozen_core(model):
    keys=("xmu","xsd","ymu","ysd","batch","arx",
          "full_lag","basis","lowrank","innovation_std")
    return json.dumps({k:model[k] for k in keys},sort_keys=True,
                      separators=(",",":"),allow_nan=False).encode("ascii")


def observe(model,x,y,prior_x,prior_y,patch,ema,count):
    """Forecast ALL arms before touching this row's physical sensor values."""
    f=features(x,model)
    past_features=features(prior_x,model)
    current_y=norm(y,model["ymu"],model["ysd"])
    prior_y_norm=norm(prior_y,model["ymu"],model["ysd"])
    base=read(model["batch"],f)
    prior_base=read(model["batch"],past_features)
    pres=tuple(prior_y_norm[i]-prior_base[i] for i in range(3))
    z=project(model["basis"],pres)
    low=read(model["lowrank"],z)
    adaptive=tuple(sum(patch[k][i]*z[i] for i in range(RANK)) for k in range(3))
    forecast={
        "batch":base,
        "arx":read(model["arx"],f+prior_y_norm),
        "full_lag":tuple(base[k]+read(model["full_lag"],pres)[k] for k in range(3)),
        "lowrank":tuple(base[k]+low[k] for k in range(3)),
        "gated":tuple(base[k]+low[k]+adaptive[k] for k in range(3)),
        "ema":tuple(base[k]+ema[k] for k in range(3)),
        "persistence":prior_y_norm
    }
    # The following post-outcome updates are unavailable to the current
    # prediction and can affect only t+1. They never change archived core.
    err=tuple(current_y[k]-forecast["gated"][k] for k in range(3))
    contradiction=max(abs(err[k])/model["innovation_std"][k] for k in range(3))
    count = count+1 if contradiction>THRESHOLD else 0
    if count>=PATIENCE:
        denominator=1.+sum(v*v for v in z)
        for k in range(3):
            for j in range(RANK):
                patch[k][j]=max(-CAP,min(CAP,
                    patch[k][j]+GAIN*err[k]*z[j]/denominator))
    else:
        for k in range(3):
            for j in range(RANK):
                patch[k][j]*=DECAY
    for k in range(3):
        ema[k]=(1.-EMA_GAIN)*ema[k]+EMA_GAIN*(current_y[k]-base[k])
    return forecast,current_y,count


def score(seq,model,start=1,end=None):
    if end is None:end=len(seq)
    if not 1<=start<end<=len(seq):
        raise ValueError("WSP187_SCORING_RANGE")
    patch=[[0.]*RANK for _ in range(3)]
    ema=[0.]*3
    count=0
    sums={k:[0.]*3 for k in ARMS}
    previous_x,previous_y=seq[start-1]
    for i in range(start,end):
        x,y=seq[i]
        preds,actual,count=observe(model,x,y,previous_x,previous_y,patch,ema,count)
        for arm in ARMS:
            for k in range(3):
                sums[arm][k]+=(actual[k]-preds[arm][k])**2
        previous_x,previous_y=x,y
    n=end-start
    values={a:tuple(math.sqrt(sum_sq/n) for sum_sq in vals)
            for a,vals in sums.items()}
    return {"rows":n,"normalized_rmse":values,
            "mean_normalized_rmse":{k:sum(v)/3 for k,v in values.items()}}


def run(path):
    begin=time.process_time()
    samples,source=admit(path)
    base=samples["actuators_white"]
    model=fit(base[:FIT_STOP])
    frozen=frozen_core(model)
    digest=hashlib.sha256(frozen).hexdigest()
    valid=score(base,model,start=FIT_STOP)
    best_valid=min(CONTROLS,key=lambda name:
                   (valid["mean_normalized_rmse"][name],name))
    tests={n:score(samples[n],model) for n in
           ("color_mix","smooth_polarizers")}
    if any(tests[n]["rows"]!=9999 for n in tests):
        raise ValueError("WSP187_DEV_COHORT")
    if frozen!=frozen_core(model):
        raise ValueError("WSP187_PRETRAINED_CORE_DRIFT")
    decisions={}
    for name,results in tests.items():
        reference=tuple(min(results["normalized_rmse"][c][k]
                            for c in CONTROLS) for k in range(3))
        candidate=results["normalized_rmse"]["gated"]
        improvements=tuple((reference[k]-candidate[k])/reference[k]
                           if reference[k]>0 else 0. for k in range(3))
        decisions[name]={"strongest_scored_control_per_output":reference,
                         "candidate_gated":candidate,
                         "relative_gain_vs_control_per_output":improvements,
                         "preregistered_5pct_all_three":all(x>=0.05 for x in improvements)}
    return {
        "schema":SCHEMA,"original_source":SOURCE,"source_provenance":source,
        "frozen_prereg_sha":"bcfc09c5438fc1e931eecddc60c2661415ecb75e",
        "FIT_row_count":FIT_STOP,"VALID_scored":valid["rows"],
        "public_dev_scored":{k:tests[k]["rows"] for k in tests},
        "validation_selected_conventional":best_valid,"validation":valid,
        "public_dev":tests,"comparisons":decisions,
        "frozen_both_dev_sets_all_three_5pct":all(
            x["preregistered_5pct_all_three"] for x in decisions.values()),
        "pretrained_core_sha256":digest,"pretrained_core_byte_retention_pass":True,
        "behavioral_cold_retention_tested":False,
        "learned_state_rank":RANK,
        "source_first_use":False,"original_physical_new_actions":0,
        "native_yggdrasil_training":False,
        "causal_graph_identified":False,"scientific_pass":False,
        "source_type":"REAL_PUBLISHED_PHYSICAL_LIGHT_TUNNEL",
        "process_cpu_seconds":time.process_time()-begin,
        "interpretation":"Fitted linear latent innovation state on real light sensors; public developer evidence, no novel causal-law or scientific intelligence claim."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True,type=Path)
    a=p.parse_args()
    print("WSP187_PUBLIC_LIGHT_DEV_RESULT="+json.dumps(
        run(a.archive),sort_keys=True,separators=(",",":"),allow_nan=False))


if __name__=="__main__":
    main()
