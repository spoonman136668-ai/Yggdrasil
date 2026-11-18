"""WSP-183 real, published physical intervention recordings: OFFLINE DEVELOPMENT.

Data origin: Gamella, Peters & Bühlmann, Causal Chamber (CC BY 4.0).
Exact frozen protocol: WSP-183/prereg.json at 7bfdfe8a...
Never runs a simulator, calls remote lab, downloads inside Python, infers
hidden graph labels or assumes paired individual counterfactual outcomes.
Not a Yggdrasil-native integrated intelligence system. NOT SCIENTIFIC_PASS.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import pathlib
import statistics
import time
import zipfile
from dataclasses import dataclass

DATASET = "wt_changepoints_v1"
ARCHIVE_MD5 = "7e9f26d192674f2aaa6481f4415007eb"
LEVELS = (0.01, 0.1, 0.2, 0.5)
TARGETS = ("rpm_in", "pressure_intake")
FIT, VALID, DEV = tuple(range(6)), (6, 7), (8, 9)
REGULARIZATION = 1e-6
REPAIR_GAIN = 0.5
MAX_ARCHIVE = 100_000_000
MAX_MEMBER = 25_000_000
SCHEMA = "yggdrasil.wsp183.real-physical-offline-dev.v1"


@dataclass(frozen=True)
class Event:
    run: int
    order: int
    load: float
    targets: tuple[float, float]


def finite(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("WSP183_NONFINITE")
    return number


def aggregate(run: int, data: bytes) -> list[Event]:
    try:
        stream = io.TextIOWrapper(io.BytesIO(data), encoding="utf-8-sig", newline="")
        reader = csv.DictReader(stream)
        mandatory = {"intervention", "load_in", *TARGETS}
        if not reader.fieldnames or not mandatory.issubset(reader.fieldnames):
            raise ValueError("WSP183_MISSING_SOURCE_COLUMNS")
        segments: list[list[dict[str, str]]] = []
        for row in reader:
            flag = finite(row["intervention"])
            if flag not in (0.0, 1.0):
                raise ValueError("WSP183_FLAG_DOMAIN")
            if flag == 1.0:
                segments.append([])
            if not segments:
                raise ValueError("WSP183_INITIAL_BOUNDARY_MISSING")
            segments[-1].append(row)
        events = []
        for idx, segment in enumerate(segments):
            if len(segment) < 80:
                raise ValueError("WSP183_SHORT_PHYSICAL_SEGMENT")
            chosen = finite(segment[0]["load_in"])
            if min(abs(chosen - level) for level in LEVELS) > 0.000001:
                raise ValueError("WSP183_UNEXPECTED_LOAD")
            for row in segment:
                if abs(finite(row["load_in"]) - chosen) > 0.000001:
                    raise ValueError("WSP183_WITHIN_SEGMENT_ACTION_DRIFT")
            # PRE-REGISTERED offset window, not selected after seeing outcomes.
            window = segment[15:80]
            target = tuple(statistics.fmean(finite(row[k]) for row in window)
                           for k in TARGETS)
            events.append(Event(run, idx, chosen, target))
        if not 9 <= len(events) <= 12:
            raise ValueError("WSP183_UNEXPECTED_EVENT_COUNT")
        return events
    except (KeyError, UnicodeDecodeError) as exc:
        raise ValueError("WSP183_SOURCE_PARSE") from exc


def read_archive(path: pathlib.Path) -> tuple[list[Event], dict]:
    if not path.is_file() or path.stat().st_size > MAX_ARCHIVE:
        raise ValueError("WSP183_ARCHIVE_SIZE")
    raw = path.read_bytes()
    md5 = hashlib.md5(raw).hexdigest()  # Upstream-published ZIP checksum only
    if md5 != ARCHIVE_MD5:
        raise ValueError("WSP183_PUBLISHED_ARCHIVE_HASH")
    manifests = {}
    all_events = []
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        files = {}
        for info in z.infolist():
            if info.is_dir():
                continue
            filename = pathlib.PurePosixPath(info.filename)
            if ".." in filename.parts or info.file_size > MAX_MEMBER:
                raise ValueError("WSP183_UNTRUSTED_ZIP_MEMBER")
            if filename.suffix == ".csv" and filename.stem.startswith("load_in_seed_"):
                if filename.stem in files:
                    raise ValueError("WSP183_DUPLICATE_RUN")
                files[filename.stem] = info
        expected = {f"load_in_seed_{r}" for r in range(10)}
        if set(files) != expected:
            raise ValueError("WSP183_ORIGINAL_RUN_ROSTER")
        for run in range(10):
            name = f"load_in_seed_{run}"
            with z.open(files[name]) as fh:
                blob = fh.read(MAX_MEMBER + 1)
            if len(blob) > MAX_MEMBER:
                raise ValueError("WSP183_MEMBER_SIZE")
            manifests[name] = hashlib.sha256(blob).hexdigest()
            all_events.extend(aggregate(run, blob))
    return all_events, {"archive_sha256": hashlib.sha256(raw).hexdigest(),
                        "archive_md5_upstream": md5, "per_run_sha256": manifests}


def mean_and_scale(events: list[Event]):
    mu = tuple(statistics.fmean(e.targets[k] for e in events) for k in range(2))
    std = tuple(math.sqrt(statistics.fmean(
        (e.targets[k]-mu[k])**2 for e in events)) for k in range(2))
    if min(std) <= 0 or not all(math.isfinite(v) for v in mu+std):
        raise ValueError("WSP183_DEGENERATE_FIT")
    return mu, std


def solve(a, b):
    n=len(b)
    aug=[list(a[i])+[b[i]] for i in range(n)]
    for i in range(n):
        pivot=max(range(i,n),key=lambda r:abs(aug[r][i]))
        if abs(aug[pivot][i]) < 1e-12:
            raise ValueError("WSP183_SINGULAR_CONTROL")
        aug[pivot],aug[i]=aug[i],aug[pivot]
        d=aug[i][i]
        aug[i]=[x/d for x in aug[i]]
        for j in range(n):
            if j != i:
                f=aug[j][i]
                aug[j]=[x-f*y for x,y in zip(aug[j],aug[i])]
    return tuple(row[-1] for row in aug)


def ridge(rows, width):
    # Independently fully fitted normal equations. Each input has identical
    # public feature visibility to its compared direct-weight prediction.
    gram=[[float(i==j)*REGULARIZATION for j in range(width)]
          for i in range(width)]
    rhs=[[0.,0.] for _ in range(width)]
    for features, outcomes in rows:
        for i in range(width):
            for j in range(width):
                gram[i][j]+=features[i]*features[j]
            for k in range(2):
                rhs[i][k]+=features[i]*outcomes[k]
    return tuple(solve(gram,[rhs[i][k] for i in range(width)]) for k in range(2))


def rls(fit: list[Event]):
    # Directly programmed two-output, two-feature recursive ridge weights.
    p=[[float(i==j)/REGULARIZATION for j in range(2)] for i in range(2)]
    weights=[[0.,0.],[0.,0.]]
    for event in fit:
        x=(1., event.load)
        q=tuple(sum(p[i][j]*x[j] for j in range(2)) for i in range(2))
        denom=1. + sum(x[i]*q[i] for i in range(2))
        gain=tuple(v/denom for v in q)
        for k in range(2):
            residual=event.targets[k]-sum(weights[k][i]*x[i] for i in range(2))
            for i in range(2):
                weights[k][i]+=gain[i]*residual
        for i in range(2):
            for j in range(2):
                p[i][j]-=q[i]*q[j]/denom
    return tuple(tuple(row) for row in weights)


def predict_weight(weights, x):
    return tuple(sum(weights[k][j]*x[j] for j in range(len(x)))
                 for k in range(2))


def keyed(events):
    return {r:[e for e in events if e.run==r] for r in sorted({e.run for e in events})}


def previous_features(e, prior, fit_mu, fit_load):
    if prior is None:
        return (1.,e.load,fit_load), fit_mu
    return (1.,e.load,prior.load), prior.targets


def build_fit(events):
    fit_mu, fit_std = mean_and_scale(events)
    fit_load=statistics.fmean(e.load for e in events)
    direct=rls(events)
    batch=ridge([((1.,e.load),e.targets) for e in events],2)
    gap=max(abs(direct[k][i]-batch[k][i]) for k in range(2) for i in range(2))
    if gap > 1e-5:
        raise ValueError("WSP183_DIRECT_BATCH_MISMATCH")
    categories={}
    for level in LEVELS:
        samples=[e.targets for e in events if abs(e.load-level)<1e-6]
        if not samples:
            raise ValueError("WSP183_MISSING_FIT_LEVEL")
        categories[level]=tuple((sum(row[k] for row in samples)+fit_mu[k])/
                                (len(samples)+1) for k in range(2))
    # Fit independent ARX with exactly the public previously completed event
    # available at prediction time (never current event's future target).
    arx_rows={0:[],1:[]}
    for run, seq in keyed(events).items():
        prev=None
        for e in seq:
            front,last=previous_features(e,prev,fit_mu,fit_load)
            for k in range(2):
                arx_rows[k].append((front+(last[k],),(e.targets[k],0.)))
            prev=e
    arx=[]
    for k in range(2):
        # Separate predictor for each output; other output never included.
        rows=[(x,(y[k],0.)) for x,y in arx_rows[k]]
        arx.append(ridge(rows,4)[0])
    return {"direct":direct,"batch":batch,"category":categories,
            "arx":tuple(arx),"mu":fit_mu,"std":fit_std,"fit_load":fit_load,
            "parity_max_weight_abs_gap":gap}


def get_predictions(e,prev,model):
    x=(1.,e.load)
    base=predict_weight(model["direct"],x)
    same=predict_weight(model["batch"],x)
    level=min(LEVELS,key=lambda v:abs(e.load-v))
    cat=model["category"][level]
    if prev is None:
        persistence=model["mu"]
        correction=base
    else:
        persistence=prev.targets
        pred_old=predict_weight(model["direct"],(1.,prev.load))
        correction=tuple(base[k]+REPAIR_GAIN*(prev.targets[k]-pred_old[k])
                         for k in range(2))
    front,last=previous_features(e,prev,model["mu"],model["fit_load"])
    arx=tuple(sum(model["arx"][k][i]*v for i,v in enumerate(front+(last[k],)))
              for k in range(2))
    return {"direct":base,"direct_repair":correction,"batch":same,
            "category":cat,"arx":arx,"persistence":persistence,"mean":model["mu"]}


def score(events,model):
    sums={}
    count=0
    for _,seq in keyed(events).items():
        prior=None
        for e in seq:
            forecasts=get_predictions(e,prior,model)
            for key,pred in forecasts.items():
                if key not in sums:
                    sums[key]=[0.,0.]
                for k in range(2):
                    sums[key][k]+=(pred[k]-e.targets[k])**2
            prior=e
            count+=1
    if count==0:
        raise ValueError("WSP183_NO_EVENTS")
    rmse={m:tuple(math.sqrt(v/count) for v in vals)
          for m,vals in sums.items()}
    normalized={m:tuple(v/model["std"][k] for k,v in enumerate(vals))
                for m,vals in rmse.items()}
    avg={m:sum(vals)/2 for m,vals in normalized.items()}
    return {"events":count,"rmse":rmse,"normalized_rmse":normalized,
            "normalized_mean_rmse":avg}


def perform(path: pathlib.Path):
    start=time.process_time()
    events,manifest=read_archive(path)
    roster={r:len([e for e in events if e.run==r]) for r in range(10)}
    fit=[e for e in events if e.run in FIT]
    valid=[e for e in events if e.run in VALID]
    dev=[e for e in events if e.run in DEV]
    model=build_fit(fit)
    val_scores=score(valid,model)
    # Pre-registered validation-only choice; no DEV-driven tuning.
    direct_choice=min(("direct","direct_repair"),
                      key=lambda m:(val_scores["normalized_mean_rmse"][m],m))
    conventional=min(("batch","category","arx","persistence","mean"),
                     key=lambda m:(val_scores["normalized_mean_rmse"][m],m))
    dev_scores=score(dev,model)
    cand=dev_scores["normalized_mean_rmse"][direct_choice]
    base=dev_scores["normalized_mean_rmse"][conventional]
    relative=(base-cand)/base if base>0 else 0.
    per_output=[(dev_scores["normalized_rmse"][conventional][k]-
                 dev_scores["normalized_rmse"][direct_choice][k])/
                dev_scores["normalized_rmse"][conventional][k] for k in range(2)]
    return {
        "schema":SCHEMA,
        "public_development_only":True,"scientific_pass":False,
        "original_source_actions":0,"remote_lab_calls":0,
        "published_data_authorship":"Gamella, Peters, Buehlmann (CC BY 4.0)",
        "dataset":"wt_changepoints_v1","dataset_content":manifest,
        "seeds_fit":FIT,"seeds_validation":VALID,"seeds_public_dev":DEV,
        "observed_original_physical_intervention_segments_per_run":roster,
        "fit_events":len(fit),"validation_events":len(valid),"public_dev_events":len(dev),
        "fit_scaling_output_std":model["std"],
        "direct_batch_max_coefficient_gap":model["parity_max_weight_abs_gap"],
        "validation_scores":val_scores,
        "public_dev_scores":dev_scores,
        "fit_validation_selected_direct":direct_choice,
        "fit_validation_selected_conventional":conventional,
        "public_dev_mean_normalized_rmse_relative_gain":relative,
        "public_dev_per_output_relative_gains":per_output,
        "frozen_5pct_per_output_gain_met":all(v>=0.05 for v in per_output),
        "old_world_cold_retention_tested":False,
        "new_mechanism_transfer_tested":False,
        "authentic_public_measurements":True,
        "whole_process_training_cpu_seconds":time.process_time()-start,
        "do_not_claim":"Not first-use or native Yggdrasil training; published physical measurements, developer comparison only."
    }


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--archive",type=pathlib.Path,required=True)
    args=cli.parse_args()
    print("WSP183_REAL_PHYSICAL_DEV_RESULT="+json.dumps(
        perform(args.archive),sort_keys=True,allow_nan=False,separators=(",",":")))


if __name__=="__main__":
    main()
