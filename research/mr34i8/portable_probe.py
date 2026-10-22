"""MR34I8: unintegrated deterministic Decimal80 sigmoid candidate and cost assay.

The unchanged original MiniGrid, Pycolab and Ygg S4C1 checkouts are
never edited. These are previously consumed development TRAINING inputs,
and no candidate weights, forecasts or native scientific tasks are trained.
"""
import json
import math
import os
import platform
import subprocess
import sys
import time
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from hashlib import sha256
from pathlib import Path

import numpy as np
import psutil

FILE = Path(__file__).with_name("frozen_protocol.json")
PRECODE = "64565886ca45eaa57087eebc74981194a782ed4d"
S4C1 = "8e1561eb1a542e21307bac669c42435cf48e59bd"
FARAMA = "7f5853792ea7f04f75614661006d87fcf949f26d"
PYCOLAB = "6504c8065dd5322438f23a2a9026649904f3322a"
PARENT_BLOB = "79df5303a4278d65363d8ab17a5d832c576b8722"
EXPECTED = {
    "FaramaMiniGridDoorKey8": "ba501812452b529cf35d4aaa176f9d5a0b5cfbb57a388d67c49dfbc547109486",
    "DeepMindPycolabApprehend": "23d9db17d29ed9646afac1b34000d0be320c2fa50ca424db2f85f1829be11bd7",
}
COUNT = {"canonical_frozen_boundaries": 42,
         "canonical_seeded_binary64_inputs": 128,
         "FaramaMiniGridDoorKey8": 160,
         "DeepMindPycolabApprehend": 160}
BENCHMARK_REPEATS = 32

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

def sha(b):
    return sha256(b).hexdigest()

def raw(values):
    return np.asarray(values, dtype=np.float64).tobytes(order="C")

def git(root, *arguments):
    return subprocess.check_output(["git", "-C", str(root), *arguments],
                                   text=True).strip()

def protocol(audit):
    data = json.loads(FILE.read_text(encoding="utf-8"))
    if (data["schema"] != "yggdrasil.mr34i8.frozen_portable_decimal80_nonlearning_candidate.v1"
        or data["exact_predecessor_MR34I7"] != "5f0520006d9ec17f88bc6bd67ca205df2a6fb10c"
        or data["exact_unchanged_MR34I4_kernel_probe_blob"] != PARENT_BLOB
        or data["exact_unchanged_original_ygg_s4c1"] != S4C1
        or data["independent_original_sources"] != {
            "FaramaMiniGridDoorKey8": FARAMA,
            "DeepMindPycolabApprehend": PYCOLAB}
        or data["original_MR34I4_source_public_logit_identity_sha"] != EXPECTED
        or data["cpu_benchmark"]["timed_repetitions"] != BENCHMARK_REPEATS
        or data["cpu_benchmark"]["warmup_repetitions"] != 2
        or data["no_new_model_training"] is not True
        or data["no_scientific_first_use"] is not True):
        raise ValueError("MR34I8_FROZEN_PROTOCOL_DRIFT")
    if git(audit, "log", "-1", "--format=%H", "--",
           "research/mr34i8/frozen_protocol.json") != PRECODE:
        raise ValueError("MR34I8_PROTOCOL_NOT_COMMITTED_FIRST")
    if git(audit, "hash-object", "research/mr34i4/kernel_probe.py") != PARENT_BLOB:
        raise ValueError("MR34I8_ORIGINAL_KERNEL_CHANGED")
    return data

def candidate_one(x, precision=80):
    # Exact original source clamp, then Decimal.from_float of binary64.
    v = float(x)
    if not math.isfinite(v):
        raise ValueError("MR34I8_NONFINITE_INPUT")
    c = max(-35.0, min(35.0, v))
    with localcontext(Context(prec=precision, rounding=ROUND_HALF_EVEN)):
        d = Decimal.from_float(c)
        return float(Decimal(1) / (Decimal(1) + (-d).exp()))

def candidate(values, precision=80):
    return np.asarray([candidate_one(x, precision) for x in values],
                      dtype=np.float64)

def original(values):
    vals = np.asarray(values, dtype=np.float64)
    n = len(vals)
    pad = (-n) % 8
    if pad:
        vals = np.concatenate((vals, np.zeros(pad, dtype=np.float64)))
    forecast = np.empty_like(vals)
    for i in range(0, len(vals), 8):
        u = vals[i:i+8]
        forecast[i:i+8] = 1. / (1. + np.exp(-np.clip(u, -35., 35.)))
    return forecast[:n]

def ulp_diff(a, b):
    # Sigmoid is finite and NONNEGATIVE on [-35,35]. The unsigned
    # binary64 representation therefore preserves ULP ordering.
    x = np.asarray(a, dtype=np.float64)
    y = np.asarray(b, dtype=np.float64)
    if not (np.isfinite(x).all() and np.isfinite(y).all()
            and (x >= 0).all() and (y >= 0).all()):
        raise ValueError("MR34I8_NONFINITE_OUTPUT")
    xx = x.view(np.uint64)
    yy = y.view(np.uint64)
    return [abs(int(u) - int(v)) for u, v in zip(xx, yy)]

def worker_peak_rss():
    if sys.platform == "win32":
        peak = getattr(psutil.Process().memory_info(), "peak_wset", None)
        if not peak:
            raise ValueError("MR34I8_WINDOWS_PEAK_RSS_MISSING")
        return int(peak)
    if sys.platform.startswith("linux"):
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    raise ValueError("MR34I8_UNSUPPORTED_OS")

def benchmark(fn, inp):
    for _ in range(2):
        fn(inp)
    started_cpu = time.process_time_ns()
    started_wall = time.perf_counter_ns()
    for _ in range(BENCHMARK_REPEATS):
        output = fn(inp)
        if len(output) != len(inp):
            raise ValueError("MR34I8_BENCHMARK_LENGTH_DRIFT")
    return {
        "total_process_cpu_ns": time.process_time_ns() - started_cpu,
        "total_wall_ns": time.perf_counter_ns() - started_wall,
        "repetitions": BENCHMARK_REPEATS,
    }

def main(audit, s4c1, farama, pycolab):
    audit = Path(audit).resolve()
    s4c1 = Path(s4c1).resolve()
    farama = Path(farama).resolve()
    pycolab = Path(pycolab).resolve()
    config = protocol(audit)
    for location, expected in [(s4c1,S4C1), (farama,FARAMA), (pycolab,PYCOLAB)]:
        if git(location, "rev-parse", "HEAD") != expected or git(location, "status", "--porcelain"):
            raise ValueError("MR34I8_ORIGINAL_SOURCE_IDENTITY_OR_DIRTY")
    sys.path.insert(0, str(audit))
    sys.path.insert(0, str(s4c1))
    sys.path.insert(0, str(farama))
    sys.path.insert(0, str(pycolab))
    from research.mr34i4 import kernel_probe as prior
    prior.frozen()   # Original MR34I4 freeze remains enforced.
    start_source_cpu = time.process_time_ns()
    fixed, random_values = prior.static_cases(prior.frozen())
    inputs = {
        "canonical_frozen_boundaries": fixed,
        "canonical_seeded_binary64_inputs": random_values,
    }
    source_receipts = {}
    drift = []
    for name, root in [("FaramaMiniGridDoorKey8", farama),
                       ("DeepMindPycolabApprehend", pycolab)]:
        numbers, receipt = prior.original_source_u(root, name)
        inputs[name] = numbers
        source_receipts[name] = receipt
        if receipt["source_original_first_preaction_logit_binary64_sha256"] != EXPECTED[name]:
            drift.append(name)
    source_cpu = time.process_time_ns() - start_source_cpu
    results = []
    all_inputs = []
    for name in COUNT:
        vals = inputs[name]
        if len(vals) != COUNT[name]:
            raise ValueError("MR34I8_FROZEN_COHORT_COUNT_DRIFT")
        all_inputs.extend(vals)
        obs = original(vals)
        port = candidate(vals, 80)
        high = candidate(vals, 120)
        previous_decimal = np.asarray(
            [prior.decimal_probability(max(-35., min(35., float(z))))
             for z in vals], dtype=np.float64)
        strict_high = raw(port) == raw(high)
        strict_prior = raw(port) == raw(previous_decimal)
        distances = ulp_diff(obs, port)
        results.append({
            "cohort":name,"n":len(vals),
            "exact_original_input_sha256":sha(raw(vals)),
            "unchanged_original_numpy_sigmoid_sha256":sha(raw(obs)),
            "portable_Decimal80_sigmoid_sha256":sha(raw(port)),
            "independent_Decimal120_check_sha256":sha(raw(high)),
            "unchanged_MR34I4_Decimal80_reference_sha256":sha(raw(previous_decimal)),
            "portable_matches_120_precision_on_tested_inputs":strict_high,
            "portable_matches_previous_MR34I4_oracle":strict_prior,
            "original_vs_candidate_nonzero_ULP_count":sum(d != 0 for d in distances),
            "original_vs_candidate_max_ULP":max(distances),
            "candidate_model_weights_modified":False,
        })
    if len(all_inputs) != 490:
        raise ValueError("MR34I8_NOT_490_ALREADY_CONSUMED_SOURCE_INPUTS")
    # Fixed-order microbench: diagnostic ONLY, not whole original model cost.
    baseline_cpu = benchmark(original, all_inputs)
    candidate_cpu = benchmark(candidate, all_inputs)
    # Recompute once after benchmarking and reject same-process drift.
    portable_repeat = (raw(candidate(all_inputs,80)) ==
                       raw(np.concatenate([candidate(inputs[k],80) for k in COUNT])))
    results_source = {k: {
        "original_source_event_sha256":
            r["source_native_training_public_action_receipts_sha256"],
        "frozen_previous_original_source_logit_sha256": EXPECTED[k],
        "current_original_source_logit_sha256":
            r["source_original_first_preaction_logit_binary64_sha256"],
        "source_identity_match":k not in drift,
        "original_s4c1_untrained_checkpoint":
            r["initial_original_untrained_45coefficient_checkpoint_sha256"],
    } for k,r in source_receipts.items()}
    for location, expected in [(s4c1,S4C1), (farama,FARAMA), (pycolab,PYCOLAB)]:
        if git(location,"rev-parse","HEAD") != expected or git(location,"status","--porcelain"):
            raise ValueError("MR34I8_ORIGINAL_POSTRUN_SOURCE_DRIFT")
    if git(audit,"status","--porcelain"):
        raise ValueError("MR34I8_AUDIT_WORKTREE_CHANGED")
    ratio = candidate_cpu["total_process_cpu_ns"] / max(1, baseline_cpu["total_process_cpu_ns"])
    precision_ok = all(x["portable_matches_120_precision_on_tested_inputs"] and
                       x["portable_matches_previous_MR34I4_oracle"] for x in results)
    result = {
        "schema":"yggdrasil.mr34i8.portable_fixed_math_candidate_receipt.v1",
        "precode_frozen_protocol_sha256":sha(FILE.read_bytes()),
        "original_source_pins":{"S4C1":S4C1,"Farama":FARAMA,"Pycolab":PYCOLAB},
        "per_frozen_source_corpus":results,
        "original_source_custody":results_source,
        "original_source_input_drifted_families":drift,
        "portable_decimal80_same_process_repeat_exact":portable_repeat,
        "benchmark_490_binary64_inputs_32_repetitions":{
            "original_numpy_8wide":baseline_cpu,
            "portable_decimal80":candidate_cpu,
            "portable_candidate_to_original_CPU_ratio":ratio,
            "no_cpu_regression":ratio <= 1.0,
        },
        "full_original_source_collection_process_cpu_ns":source_cpu,
        "whole_original_actor_and_candidate_worker_OS_peak_RSS":worker_peak_rss(),
        "platform":platform.platform(),
        "numpy_version":np.__version__,
        "portable_numeric_precision_dev_GO":precision_ok and portable_repeat,
        "portable_numeric_resource_nonregression_GO":ratio<=1.0,
        "all_original_source_sha_identical":len(drift)==0,
        "original_45_model_training":"NOT_PERFORMED",
        "trained_model_portable_checkpoint":"NO_GO",
        "protected_unfamiliar_first_use_consumed":False,
        "scientific_transfer_admission":"NO_GO",
        "G29_full_native_regression":"BLOCKED",
    }
    print("MR34I8_PORTABLE_FIXED_MATH_CANDIDATE="+canonical(result),flush=True)
    if not precision_ok or not portable_repeat:
        raise ValueError("MR34I8_BOUNDED_CANDIDATE_NUMERIC_PRECISION_FAIL")
    if drift:
        raise ValueError("MR34I8_FROZEN_ORIGINAL_SOURCE_INPUT_DRIFT")
    # A slow but reproducible candidate may still execute successfully;
    # resource nonregression is explicitly NO-GO from its measured ratio.

if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit("usage: python portable_probe.py AUDIT S4C1 FARAMA PYCOLAB")
    main(*sys.argv[1:])
