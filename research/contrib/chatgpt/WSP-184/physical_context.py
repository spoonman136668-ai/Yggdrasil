"""WSP-184 — tokenless direct-weight and context memory development on real physical data.

Publicly recorded wind-tunnel observations only (Causal Chamber CC BY 4.0).
NO remote lab, new original-world steps, hidden regime labels in forecasts,
source graph oracle, privileged paired exogenous do-outcomes or SCIENTIFIC_PASS.
Frozen protocol WSP-184/prereg.json, first committed at 398e95dd6285...
"""
from __future__ import annotations

from dataclasses import dataclass
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

SCHEMA = "yggdrasil.wsp184.real-physical-memory-public-dev.v1"
ARCHIVE_MD5 = "19bb4e92cbe0b8dff49299b9b509ac36"
WALK = "actuators_random_walk_"
REGIME = "regime_jumps_single"
FIT_RUNS, VAL_RUNS, DEV_RUNS = tuple(range(1, 7)), (7, 8), (9, 10)
ACTUATORS = ("load_in", "load_out", "hatch", "pot_1", "pot_2")
TARGETS = ("rpm_in", "pressure_intake")
FEATURES = 1 + len(ACTUATORS) + len(TARGETS)
REG = 0.01
GAIN = 0.2
DECAY = 0.98
THRESHOLD = 1.5
PATIENCE = 3
FIRST_WINDOW = 200
EXPECTED_WALK = 10000
EXPECTED_REGIME = 320000
MAX_ZIP_BYTES = 450_000_000
MAX_MEMBER_BYTES = 250_000_000
MAX_UNCOMPRESSED_BYTES = 950_000_000
METHODS = ("direct", "batch", "ema", "gated", "persistence")
CONTROLS = ("batch", "ema", "persistence")


@dataclass(frozen=True, slots=True)
class Sample:
    src: str
    index: int
    regime: int
    actuators: tuple[float, ...]
    observed: tuple[float, float]


def finite(raw: str) -> float:
    try:
        val = float(raw)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError("WSP184_INVALID_NUMERIC") from exc
    if not math.isfinite(val):
        raise ValueError("WSP184_NONFINITE")
    return val


def parse_csv(blob: bytes, name: str) -> list[Sample]:
    reader = csv.DictReader(io.StringIO(blob.decode("utf-8-sig"), newline=""))
    fields = reader.fieldnames
    required = {*ACTUATORS, *TARGETS, "flag"}
    if (fields is None or len(set(fields)) != len(fields)
            or not required.issubset(fields)):
        raise ValueError("WSP184_MISSING_OR_DUPLICATE_COLUMNS")
    sequence: list[Sample] = []
    regime_counts = [0] * 32
    prior_regime = 0
    for i, row in enumerate(reader):
        vals = tuple(finite(row[col]) for col in ACTUATORS)
        y = tuple(finite(row[col]) for col in TARGETS)
        label = finite(row["flag"])
        if name == REGIME:
            if label != int(label) or not (0 <= label <= 31):
                raise ValueError("WSP184_REGIME_LABEL")
            regime = int(label)
            if regime != prior_regime and regime != prior_regime + 1:
                raise ValueError("WSP184_REGIME_ORDER")
            prior_regime = regime
            regime_counts[regime] += 1
        else:
            regime = 0
        sequence.append(Sample(name, i, regime, vals, y))
        if len(sequence) > EXPECTED_REGIME:
            raise ValueError("WSP184_EXCESS_SOURCE_ROWS")
    if name == REGIME:
        if (len(sequence) != EXPECTED_REGIME or
                regime_counts != [10000] * 32):
            raise ValueError("WSP184_REGIME_COUNTS")
    elif len(sequence) != EXPECTED_WALK:
        raise ValueError("WSP184_WALK_COUNTS")
    return sequence


def load_physical_archive(path: Path):
    if not path.is_file() or path.stat().st_size > MAX_ZIP_BYTES:
        raise ValueError("WSP184_ARCHIVE_BUDGET")
    raw = path.read_bytes()
    md5 = hashlib.md5(raw).hexdigest()
    if md5 != ARCHIVE_MD5:
        raise ValueError("WSP184_PUBLISHED_ARCHIVE_HASH")
    wanted = {f"{WALK}{n}" for n in range(1, 11)} | {REGIME}
    result = {}
    hashes = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        members = {}
        total = 0
        for info in z.infolist():
            name = PurePosixPath(info.filename)
            if name.is_absolute() or ".." in name.parts:
                raise ValueError("WSP184_UNSAFE_ARCHIVE_PATH")
            total += info.file_size
            if info.file_size > MAX_MEMBER_BYTES or total > MAX_UNCOMPRESSED_BYTES:
                raise ValueError("WSP184_UNCOMPRESSED_BUDGET")
            if not info.is_dir() and name.stem in wanted:
                if name.suffix != ".csv" or name.stem in members:
                    raise ValueError("WSP184_DUPLICATE_OR_INVALID_MEMBER")
                members[name.stem] = info
        if set(members) != wanted:
            raise ValueError("WSP184_ORIGINAL_ROSTER")
        for name in sorted(wanted):
            with z.open(members[name]) as stream:
                blob = stream.read(MAX_MEMBER_BYTES + 1)
            if len(blob) > MAX_MEMBER_BYTES:
                raise ValueError("WSP184_MEMBER_SIZE")
            hashes[name] = hashlib.sha256(blob).hexdigest()
            result[name] = parse_csv(blob, name)
    return result, {"upstream_zip_md5": md5,
                    "zip_sha256": hashlib.sha256(raw).hexdigest(),
                    "member_sha256": hashes}


def pairs(sequences: list[list[Sample]]):
    for seq in sequences:
        for i in range(1, len(seq)):
            cur, past = seq[i], seq[i-1]
            yield (cur.actuators + past.observed, cur.observed)


def norm(raw: tuple[float,...], mean: tuple[float,...],
         std: tuple[float,...]) -> tuple[float,...]:
    return tuple((v-m)/s for v,m,s in zip(raw,mean,std))


def fit_scaling(samples):
    cols = list(zip(*(x for x,_ in samples)))
    goals = list(zip(*(y for _,y in samples)))
    xmu = tuple(statistics.fmean(col) for col in cols)
    ymu = tuple(statistics.fmean(col) for col in goals)
    xstd = tuple(statistics.pstdev(col) for col in cols)
    ystd = tuple(statistics.pstdev(col) for col in goals)
    if (len(cols) != FEATURES-1 or min(xstd + ystd) <= 1e-12 or
            not all(math.isfinite(z) for z in xmu+ymu+xstd+ystd)):
        raise ValueError("WSP184_DEGENERATE_FIT")
    return xmu,xstd,ymu,ystd


def solve(a,b):
    n=len(b)
    m=[list(a[i])+[b[i]] for i in range(n)]
    for i in range(n):
        k=max(range(i,n),key=lambda r:abs(m[r][i]))
        if abs(m[k][i]) < 1e-12:
            raise ValueError("WSP184_SINGULAR_BATCH")
        m[k],m[i]=m[i],m[k]
        p=m[i][i]
        m[i]=[v/p for v in m[i]]
        for j in range(n):
            if j!=i:
                z=m[j][i]
                m[j]=[u-z*v for u,v in zip(m[j],m[i])]
    return tuple(row[-1] for row in m)


def train_fit(walks: list[list[Sample]]):
    observations=list(pairs(walks))
    xmu,xstd,ymu,ystd=fit_scaling(observations)
    corpus=[((1.,)+norm(x,xmu,xstd),norm(y,ymu,ystd))
            for x,y in observations]
    gram=[[REG*float(i==j) for j in range(FEATURES)]
          for i in range(FEATURES)]
    rhs=[[0.,0.] for _ in range(FEATURES)]
    p=[[float(i==j)/REG for j in range(FEATURES)]
       for i in range(FEATURES)]
    direct=[[0.]*FEATURES for _ in range(2)]
    for x,y in corpus:
        # Independent conventional fully fitted ridge sufficient statistics.
        for i in range(FEATURES):
            for j in range(FEATURES):
                gram[i][j] += x[i]*x[j]
            for k in range(2):
                rhs[i][k] += x[i]*y[k]
        # Explicit incremental weight programming on public observed FIT data.
        px=[sum(p[i][j]*x[j] for j in range(FEATURES))
            for i in range(FEATURES)]
        denom=1.+sum(x[i]*px[i] for i in range(FEATURES))
        gain=[v/denom for v in px]
        for k in range(2):
            err=y[k]-sum(direct[k][i]*x[i] for i in range(FEATURES))
            for i in range(FEATURES):
                direct[k][i]+=gain[i]*err
        for i in range(FEATURES):
            for j in range(FEATURES):
                p[i][j]-=px[i]*px[j]/denom
    conventional=[solve(gram,[rhs[i][k] for i in range(FEATURES)])
                  for k in range(2)]
    gap=max(abs(direct[k][i]-conventional[k][i])
            for k in range(2) for i in range(FEATURES))
    if gap>1e-5:
        raise ValueError("WSP184_CONVENTIONAL_PARITY_FAILED")
    residual=[]
    for k in range(2):
        mse=statistics.fmean(
            (y[k]-sum(conventional[k][i]*x[i] for i in range(FEATURES)))**2
            for x,y in corpus)
        residual.append(math.sqrt(mse))
    if min(residual) <=1e-9:
        raise ValueError("WSP184_RESIDUAL_VARIANCE")
    return {"xmu":xmu,"xstd":xstd,"ymu":ymu,"ystd":ystd,
            "direct":tuple(tuple(row) for row in direct),
            "batch":tuple(tuple(row) for row in conventional),
            "resid_std":tuple(residual),"parity":gap,
            "fit_observations":len(corpus)}


def forecast(model, current_actuators, previous_sensor, history_state):
    """No current y, regime flag, source graph, target list, or time index."""
    features=(1.,)+norm(current_actuators+previous_sensor,
                        model["xmu"],model["xstd"])
    def read(weights):
        return tuple(sum(row[i]*features[i] for i in range(FEATURES))
                     for row in weights)
    base=read(model["batch"])
    direct=read(model["direct"])
    return {"batch":base,"direct":direct,
            "ema":tuple(base[k]+history_state["ema"][k] for k in range(2)),
            "gated":tuple(direct[k]+history_state["gate"][k] for k in range(2)),
            "persistence":norm(previous_sensor,model["ymu"],model["ystd"])}


def empty_history():
    return {"ema":[0.,0.],"gate":[0.,0.],"count":[0,0]}


def observe_past(model,state,actual_y,base_forecast):
    """Called ONLY after forecasting/scoring the current observation."""
    true=norm(actual_y,model["ymu"],model["ystd"])
    for k in range(2):
        residual=true[k]-base_forecast[k]
        state["ema"][k]=(1-GAIN)*state["ema"][k]+GAIN*residual
        if abs(residual)>THRESHOLD*model["resid_std"][k]:
            state["count"][k]+=1
        else:
            state["count"][k]=0
        if state["count"][k]>=PATIENCE:
            state["gate"][k]=(1-GAIN)*state["gate"][k]+GAIN*residual
        else:
            state["gate"][k]*=DECAY


def evaluate_runs(seqs,model,select=None):
    sums={m:[0.,0.] for m in METHODS}
    count=0
    counts_per_regime={}
    for seq in seqs:
        state=empty_history()
        previous=seq[0]
        for current in seq[1:]:
            predictions=forecast(model,current.actuators,previous.observed,state)
            chosen=select is None or select(current)
            if chosen:
                expected=norm(current.observed,model["ymu"],model["ystd"])
                for m in METHODS:
                    for k in range(2):
                        sums[m][k]+=(predictions[m][k]-expected[k])**2
                count+=1
                counts_per_regime[current.regime]=counts_per_regime.get(current.regime,0)+1
            # Every pre-existing physical observation may inform the NEXT
            # prediction equally for all adaptive arms, including held steps.
            observe_past(model,state,current.observed,predictions["batch"])
            previous=current
    if count<=0:
        raise ValueError("WSP184_NO_EVALUABLE_ROWS")
    scores={m:tuple(math.sqrt(v/count) for v in sums[m]) for m in METHODS}
    return {"count":count,"normalized_rmse":scores,
            "mean_normalized_rmse":{m:sum(v)/2 for m,v in scores.items()},
            "counts_per_regime":counts_per_regime}


def checkpoint(model):
    # FIT-only core weights; adaptive state is deliberately NOT in this
    # checkpoint, so this tests SOFTWARE cold retention, not learning.
    items=("xmu","xstd","ymu","ystd","direct","batch","resid_std")
    return json.dumps({k:model[k] for k in items},sort_keys=True,
                      separators=(",",":"),allow_nan=False).encode("ascii")


def run(path:Path):
    t=time.process_time()
    data,manifest=load_physical_archive(path)
    fits=[data[WALK+str(i)] for i in FIT_RUNS]
    val=[data[WALK+str(i)] for i in VAL_RUNS]
    dev=[data[WALK+str(i)] for i in DEV_RUNS]
    changed=data[REGIME]
    model=train_fit(fits)
    before=checkpoint(model)
    h=hashlib.sha256(before).hexdigest()
    valscore=evaluate_runs(val,model)
    # Strong controls are evaluated all on same data; VALID-only operational
    # selector is reported but not an independent scientific winner.
    control_choice=min(CONTROLS,
                       key=lambda n:(valscore["mean_normalized_rmse"][n],n))
    walkscore=evaluate_runs(dev,model)
    changescore=evaluate_runs([changed],model,select=lambda e:e.regime>0)
    window=evaluate_runs([changed],model,
                        select=lambda e:e.regime>0 and e.index%10000<FIRST_WINDOW)
    if window["count"]!=31*FIRST_WINDOW:
        raise ValueError("WSP184_TRANSITION_WINDOW_CUSTODY")
    if changescore["count"]!=31*10000:
        raise ValueError("WSP184_CHANGED_REGIME_CUSTODY")
    after=checkpoint(model)
    # Deterministic protected old representation stays IDENTICAL, not just
    # numerically similar. This is not old-law behavioral transfer.
    if before!=after or h!=hashlib.sha256(after).hexdigest():
        raise ValueError("WSP184_FROZEN_CORE_DRIFT")
    baseline_per_output=tuple(
        min(window["normalized_rmse"][name][k] for name in CONTROLS)
        for k in range(2))
    gain=tuple((baseline_per_output[k]-window["normalized_rmse"]["gated"][k])/
               baseline_per_output[k] for k in range(2))
    return {
        "schema":SCHEMA,"source":"juangamella/causal-chamber@967d59a42956872f37463cc561ecf6e9ceab9364",
        "dataset":"wt_walks_v1","data":manifest,
        "science_status":"PUBLIC_OFFLINE_DEV_ONLY_NO_SCIENTIFIC_PASS","scientific_pass":False,
        "new_physical_world_actions":0,"remote_lab_calls":0,
        "source_walk_runs":list(range(1,11)),"fit_runs":FIT_RUNS,
        "valid_runs":VAL_RUNS,"public_dev_runs":DEV_RUNS,
        "fit_training_rows":model["fit_observations"],
        "direct_batch_parity_max_abs":model["parity"],
        "frozen_core_sha256":h,"frozen_core_retention_bytes_pass":before==after,
        "fit_residual_std":model["resid_std"],
        "validation_selected_conventional":control_choice,
        "validation":valscore,
        "public_dev_walk":walkscore,
        "public_dev_changed_regime_all":changescore,
        "public_dev_regime_transitions_first200":window,
        "regime_transition_control_best_per_output":baseline_per_output,
        "gated_relative_gain_vs_best_control_per_output":gain,
        "frozen_both_5pct_gain_met":all(v>=0.05 for v in gain),
        "unfamiliar_source_mechanism_transfer_proven":False,
        "native_yggdrasil_model_training":False,
        "process_cpu_seconds":time.process_time()-t,
        "interpretation":"Real pre-existing physical observations, not native intelligence or causal graph identification."
    }


def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--archive",required=True,type=Path)
    a=arg.parse_args()
    print("WSP184_PHYSICAL_CONTEXT_DEV_RESULT="+json.dumps(
        run(a.archive),sort_keys=True,separators=(",",":"),allow_nan=False))


if __name__=="__main__":
    main()
