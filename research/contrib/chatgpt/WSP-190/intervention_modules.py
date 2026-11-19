"""WSP190: learn public intervention-conditioned physical effect modules.

Original independent light tunnel measurements by Gamella, Peters and
Buehlmann (NMI 2025), CC BY 4.0. Source verified against published MD5.
Protocol was frozen BEFORE numeric evidence at 222e14e657da5e7b41041d14860483c45a0481b9.
No new world actions, protected owner first-use, source model weights,
transformer, tokenization or trained native Yggdrasil integration.
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
DATASET = "lt_interventions_standard_v1"
SOURCE_MD5 = "476664d024f88e8b7640998bb5e9ee33"
SCHEMA = "yggdrasil.wsp190.real-intervention-module-public-dev.v1"
PRE = "222e14e657da5e7b41041d14860483c45a0481b9"
INPUTS = ("red", "green", "blue", "pol_1", "pol_2",
          "l_11", "l_12", "l_21", "l_22", "l_31", "l_32")
TARGETS = ("vis_1", "vis_2", "vis_3")
FIT_REF, VALID_REF = 8000, 2000
FIT_MID = ("uniform_red_mid", "uniform_green_mid", "uniform_blue_mid")
DEV = ("uniform_red_strong", "uniform_green_strong",
       "uniform_blue_strong", "uniform_pol_1_mid")
ROSTER = ("uniform_reference",) + FIT_MID + DEV
REQUIRED_ROWS = {name:(10000 if name == "uniform_reference" else 1000)
                 for name in ROSTER}
LAMBDA = 0.25
NULL_Z = 2.0
MAX_ARCHIVE = 450_000_000
MAX_MEMBER = 110_000_000
MAX_UNCOMPRESSED = 1_100_000_000
ARMS = ("module", "shuffled_edges", "pooled_ridge",
        "quadratic_ridge", "group_centered_ridge", "reference_mean")
CONTROLS = ("pooled_ridge", "quadratic_ridge",
            "group_centered_ridge", "reference_mean")


def finite_float(x):
    try:
        value = float(x)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("WSP190_NONNUMERIC_PUBLIC_RECORD") from exc
    if not math.isfinite(value):
        raise ValueError("WSP190_NONFINITE_PUBLIC_RECORD")
    return value


def inspect_source(path: Path):
    """Full published archive/member integrity BEFORE interpreting numbers."""
    if not path.is_file() or not 0 < path.stat().st_size <= MAX_ARCHIVE:
        raise ValueError("WSP190_ARCHIVE_LIMIT")
    raw = path.read_bytes()
    if hashlib.md5(raw).hexdigest() != SOURCE_MD5:
        raise ValueError("WSP190_UPSTREAM_MD5")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        selected = {}
        expanded = 0
        for info in archive.infolist():
            name = PurePosixPath(info.filename)
            if name.is_absolute() or ".." in name.parts:
                raise ValueError("WSP190_UNSAFE_ORIGINAL_SOURCE_PATH")
            expanded += info.file_size
            if info.file_size > MAX_MEMBER or expanded > MAX_UNCOMPRESSED:
                raise ValueError("WSP190_UNCOMPRESSED_LIMIT")
            if info.is_dir() or name.stem not in ROSTER:
                continue
            if name.suffix.lower() != ".csv" or name.stem in selected:
                raise ValueError("WSP190_SOURCE_ROSTER_COLLISION")
            selected[name.stem] = info
        if set(selected) != set(ROSTER):
            raise ValueError("WSP190_MISSING_SOURCE_RECORDING")
        blobs = {}
        sha = {}
        for name in ROSTER:
            with archive.open(selected[name]) as stream:
                blob = stream.read(MAX_MEMBER + 1)
            if len(blob) > MAX_MEMBER:
                raise ValueError("WSP190_ORIGINAL_MEMBER_LIMIT")
            blobs[name] = blob
            sha[name] = hashlib.sha256(blob).hexdigest()
    return blobs, {
        "source": SOURCE, "dataset": DATASET,
        "author_zip_md5": SOURCE_MD5,
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "selected_original_files_sha256": sha,
        "license": "CC BY 4.0 Gamella Peters Buehlmann 2025"
    }


def parse_prefix(blob: bytes, name: str):
    """Use fixed first N records, count surplus without parsing its values."""
    reader = csv.DictReader(io.StringIO(blob.decode("utf-8-sig"), newline=""))
    headers = reader.fieldnames
    if (not headers or len(headers) != len(set(headers))
            or not set(INPUTS + TARGETS).issubset(headers)):
        raise ValueError("WSP190_ORIGINAL_HEADERS")
    wanted = REQUIRED_ROWS[name]
    samples = []
    total = 0
    for row in reader:
        total += 1
        if not row or None in row:
            raise ValueError("WSP190_MALFORMED_RECORD")
        if total <= wanted:
            if any(row[k] is None for k in INPUTS + TARGETS):
                raise ValueError("WSP190_MALFORMED_RECORD")
            x = tuple(finite_float(row[k]) for k in INPUTS)
            y = tuple(finite_float(row[k]) for k in TARGETS)
            samples.append((x, y))
    if total < wanted:
        raise ValueError("WSP190_TOO_FEW_ORIGINAL_RECORDS")
    return samples, {"observed_original_records": total,
                     "frozen_prefix_used": wanted,
                     "extra_original_records_not_parsed": total - wanted,
                     "header_count": len(headers)}


def mean_std(rows):
    cols = list(zip(*rows))
    mean = tuple(statistics.fmean(col) for col in cols)
    sd = tuple(statistics.pstdev(col) for col in cols)
    if any(not math.isfinite(v) or v <= 1e-12 for v in sd):
        raise ValueError("WSP190_DEGENERATE_FIT_REFERENCE")
    return mean, sd


def normalize(vec, mean, sd):
    return tuple((a - b) / c for a, b, c in zip(vec, mean, sd))


def solve(gram, rhs):
    n = len(rhs)
    A = [list(gram[i]) + [rhs[i]] for i in range(n)]
    for i in range(n):
        pivot = max(range(i, n), key=lambda k: abs(A[k][i]))
        if abs(A[pivot][i]) < 1e-12:
            raise ValueError("WSP190_RIDGE_SINGULAR")
        A[i], A[pivot] = A[pivot], A[i]
        div = A[i][i]
        A[i] = [v / div for v in A[i]]
        for j in range(n):
            if j == i:
                continue
            scale = A[j][i]
            A[j] = [v - scale * u for v, u in zip(A[j], A[i])]
    return tuple(row[-1] for row in A)


def fit_ridge(examples, d, lam=LAMBDA):
    gram = [[float(i == j) * lam for j in range(d)] for i in range(d)]
    rhs = [[0.0] * 3 for _ in range(d)]
    n = 0
    for x, y in examples:
        if len(x) != d or len(y) != 3:
            raise ValueError("WSP190_FIT_SHAPE")
        n += 1
        for i, xi in enumerate(x):
            for j, xj in enumerate(x):
                gram[i][j] += xi * xj
            for k in range(3):
                rhs[i][k] += xi * y[k]
    if n == 0:
        raise ValueError("WSP190_NO_FIT_DATA")
    return tuple(solve(gram, tuple(rhs[i][k] for i in range(d)))
                 for k in range(3))


def predict(weights, features):
    return tuple(sum(a * b for a, b in zip(row, features))
                 for row in weights)


def quadratic(x):
    # Fully FIT-controlled polynomial baseline with MORE capacity than the
    # 3 RGB candidate modules, plus pairwise RGB interactions.
    return ((1.0,) + x + tuple(t*t for t in x) +
            (x[0]*x[1], x[0]*x[2], x[1]*x[2]))


def standardize(samples, model):
    return [(normalize(x, model["xmu"], model["xsd"]),
             normalize(y, model["ymu"], model["ysd"]))
            for x, y in samples]


def fit(groups):
    """FIT-only causal contrasts and fully fitted label-aware controls."""
    if set(groups) != {"uniform_reference", *FIT_MID}:
        raise ValueError("WSP190_FIT_GROUPS")
    reference = groups["uniform_reference"]
    if len(reference) != FIT_REF or any(len(groups[n]) != 1000 for n in FIT_MID):
        raise ValueError("WSP190_FIT_COUNT")
    xm, xs = mean_std([a for a, _ in reference])
    ym, ys = mean_std([b for _, b in reference])
    model = {"xmu": xm, "xsd": xs, "ymu": ym, "ysd": ys}
    z = {name: standardize(rows, model) for name, rows in groups.items()}
    allrows = [row for name in ("uniform_reference",) + FIT_MID
               for row in z[name]]

    # Conventional baselines: all 11 public actuator inputs, same FIT data.
    model["pooled_ridge"] = fit_ridge(
        (((1.0,) + x, y) for x, y in allrows), 12)
    model["quadratic_ridge"] = fit_ridge(
        ((quadratic(x), y) for x, y in allrows), 1+11+11+3)

    # A conventional labeled control sees EXACTLY the same FIT source
    # intervention groups used by the causal contrast candidate.
    cmeans = {}
    for name, data in z.items():
        mx = tuple(statistics.fmean(a[i] for a, _ in data)
                   for i in range(11))
        my = tuple(statistics.fmean(b[k] for _, b in data)
                   for k in range(3))
        cmeans[name] = (mx, my)
    def centered_rows():
        for name, data in z.items():
            cx, cy = cmeans[name]
            for x, y in data:
                yield (tuple(x[i]-cx[i] for i in range(11)),
                       tuple(y[k]-cy[k] for k in range(3)))
    model["group_centered_ridge"] = fit_ridge(centered_rows(), 11)
    model["reference_y_mean"] = cmeans["uniform_reference"][1]
    model["reference_x_mean"] = cmeans["uniform_reference"][0]

    # Experimentally assigned one-target MID interventions establish 3 x 3
    # source-to-sensor slopes. Null-gate uncertain edges, no oracle graph.
    ref_y = list(zip(*(y for _, y in z["uniform_reference"])))
    slopes = [[0.] * 3 for _ in range(3)]
    gates = [[False] * 3 for _ in range(3)]
    contrast_receipts = {}
    for j, name in enumerate(FIT_MID):
        data = z[name]
        dx = cmeans[name][0][j] - cmeans["uniform_reference"][0][j]
        if not math.isfinite(dx) or abs(dx) < 0.15:
            raise ValueError("WSP190_ACTUAL_INTERVENTION_WEAK")
        contrast_receipts[name] = {"source_input_index":j,
                                   "normalized_intervention_shift":dx}
        for k in range(3):
            pool = [y[k] for _, y in data]
            refpool = ref_y[k]
            dy = statistics.fmean(pool)-statistics.fmean(refpool)
            se = math.sqrt(statistics.pvariance(pool)/len(pool)
                           +statistics.pvariance(refpool)/len(refpool))
            if abs(dy) > NULL_Z*se:
                slopes[k][j] = dy/dx
                gates[k][j] = True

    def nuisance_rows(module_slopes):
        for x, y in allrows:
            effect = predict(module_slopes, x[:3])
            yield ((1.0,) + x[3:],
                   tuple(y[k]-effect[k] for k in range(3)))
    modules = tuple(tuple(row) for row in slopes)
    model["modules"] = modules
    model["module_nuisance"] = fit_ridge(nuisance_rows(modules), 1+8)

    # Frozen negative attribution: red->green, green->blue, blue->red. Refit
    # the nuisance coefficients on IDENTICAL FIT records/capacity.
    perm = tuple((row[2], row[0], row[1]) for row in modules)
    model["shuffled_modules"] = perm
    model["shuffled_nuisance"] = fit_ridge(nuisance_rows(perm), 1+8)
    model["causal_edges_active"] = tuple(tuple(row) for row in gates)
    model["fit_contrasts"] = contrast_receipts
    model["fit_samples"] = len(allrows)
    return model


def freeze(model):
    return json.dumps(model, sort_keys=True, separators=(",",":"),
                      allow_nan=False).encode("utf-8")


def predict_all(model, raw_x):
    x = normalize(raw_x, model["xmu"], model["xsd"])
    offset = model["reference_y_mean"]
    cx = tuple(x[i]-model["reference_x_mean"][i] for i in range(11))
    return {
        "module": tuple(a+b for a,b in zip(
            predict(model["modules"], x[:3]),
            predict(model["module_nuisance"], (1.,) + x[3:]))),
        "shuffled_edges": tuple(a+b for a,b in zip(
            predict(model["shuffled_modules"], x[:3]),
            predict(model["shuffled_nuisance"], (1.,) + x[3:]))),
        "pooled_ridge": predict(model["pooled_ridge"], (1.,) + x),
        "quadratic_ridge": predict(model["quadratic_ridge"], quadratic(x)),
        "group_centered_ridge": tuple(offset[k] +
            predict(model["group_centered_ridge"], cx)[k] for k in range(3)),
        "reference_mean": offset,
    }


def evaluate(rows, model):
    total = {name:[0.0]*3 for name in ARMS}
    if not rows:
        raise ValueError("WSP190_NO_EVAL_ROWS")
    for x, actual in rows:
        pred = predict_all(model,x)
        target = normalize(actual,model["ymu"],model["ysd"])
        for name in ARMS:
            for k in range(3):
                total[name][k] += (pred[name][k]-target[k])**2
    rmse = {name:tuple(math.sqrt(v/len(rows)) for v in total[name])
            for name in ARMS}
    return {"rows":len(rows),"normalized_rmse":rmse,
            "mean_normalized_rmse":{name:sum(rmse[name])/3
                                    for name in ARMS}}


def execute(path: Path):
    start = time.process_time()
    blobs,manifest = inspect_source(path)
    # Source-only size, schema and exact row-custody metadata first,
    # before any numeric learning or DEV target evaluation.
    fit_ref,src_ref = parse_prefix(blobs["uniform_reference"],"uniform_reference")
    fit_groups={"uniform_reference":fit_ref[:FIT_REF]}
    for name in FIT_MID:
        fit_groups[name],_ = parse_prefix(blobs[name],name)
    manifest["source_records"]={"uniform_reference":src_ref}
    fit_started = time.process_time()
    m = fit(fit_groups)
    trained_cpu = time.process_time()-fit_started
    checkpoint = freeze(m)
    frozen_sha = hashlib.sha256(checkpoint).hexdigest()
    valid = evaluate(fit_ref[FIT_REF:FIT_REF+VALID_REF],m)
    best_control = min(CONTROLS, key=lambda name:
                       (valid["mean_normalized_rmse"][name],name))
    dev = {}
    for name in DEV:
        samples,detail = parse_prefix(blobs[name],name)
        manifest["source_records"][name] = detail
        dev[name] = evaluate(samples,m)
    for name in FIT_MID:
        _,info = parse_prefix(blobs[name],name)
        manifest["source_records"][name] = info
    if checkpoint != freeze(m):
        raise ValueError("WSP190_COLD_CORE_DRIFT")

    strong = DEV[:3]
    def mean_aggregate(name):
        return statistics.fmean(dev[group]["mean_normalized_rmse"][name]
                                for group in strong)
    candidate = mean_aggregate("module")
    incumbent = mean_aggregate(best_control)
    shuffled = mean_aggregate("shuffled_edges")
    win = (incumbent > 0 and shuffled > 0 and
           (incumbent-candidate)/incumbent >= .05 and
           (shuffled-candidate)/shuffled >= .05 and
           sum(dev[g]["mean_normalized_rmse"]["module"] <=
               dev[g]["mean_normalized_rmse"][best_control]
               for g in strong) >= 2 and
           all(dev[g]["normalized_rmse"]["module"][k] <=
               dev[g]["normalized_rmse"][best_control][k]*1.05
               for g in strong for k in range(3)) and
           dev["uniform_pol_1_mid"]["mean_normalized_rmse"]["module"] <=
               dev["uniform_pol_1_mid"]["mean_normalized_rmse"][best_control]*1.10)
    oracle = {group:tuple(min(dev[group]["normalized_rmse"][c][k]
                              for c in CONTROLS) for k in range(3))
              for group in DEV}
    return {
        "schema":SCHEMA,"prereg_sha":PRE,
        "frozen_read_receipt":manifest,
        "fit_reference_records":FIT_REF,
        "fit_real_intervention_records":3*1000,
        "fit_total_original_records":m["fit_samples"],
        "validation_records":valid["rows"],
        "validation_selected_conventional":best_control,
        "validation":valid,
        "public_development":dev,
        "public_oracle_best_scored_control_per_sensor":oracle,
        "strong_intervention_mean_normalized_rmse":{
            "module":candidate,
            "validation_selected_conventional":incumbent,
            "shuffled_edges":shuffled,
            "candidate_gain_vs_conventional":(incumbent-candidate)/incumbent if incumbent>0 else 0.,
            "candidate_gain_vs_shuffled":(shuffled-candidate)/shuffled if shuffled>0 else 0.},
        "preregistered_development_win":win,
        "estimated_module_edges":m["modules"],
        "edge_admission_gates":m["causal_edges_active"],
        "original_fit_intervention_shift":m["fit_contrasts"],
        "fit_model_checkpoint_sha256":frozen_sha,
        "fit_checkpoint_byte_preservation":True,
        "cold_behavioral_retention_tested":False,
        "new_unfamiliar_causal_world_transfer_tested":False,
        "native_yggdrasil_model_trained":False,
        "new_source_original_physical_actions":0,
        "protected_first_use":False,
        "scientific_pass":False,
        "FIT_process_cpu_seconds":trained_cpu,
        "whole_parse_fit_score_process_cpu_seconds":time.process_time()-start,
        "conclusion":"OFFLINE PUBLIC ORIGINAL PHYSICAL INTERVENTION DEVELOPMENT ONLY; NOT native or accepted science"
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--archive",type=Path,required=True)
    args=ap.parse_args()
    print("WSP190_PUBLIC_ORIGINAL_INTERVENTION_DEV_RESULT="+json.dumps(
        execute(args.archive),sort_keys=True,separators=(",",":"),
        allow_nan=False))


if __name__=="__main__":
    main()
