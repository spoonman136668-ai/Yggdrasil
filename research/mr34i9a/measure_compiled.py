"""MR34I9B one-shot, development-TRAINING-only compiled sigmoid falsifier.

Preserves the frozen MR34I9A protocol. Never trains, patches S4C1/external
originals, opens held seeds, qualifies cognitive transfer, or chooses a best
worker. Per-host CPU/RSS is an engineering kernel test, not model evidence.
"""
import ctypes
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import platform
import statistics
import struct
import subprocess
import sys
import tempfile
import time

import numpy as np

SCHEMA = "yggdrasil.mr34i9b.compiled_eightwide_development_only.v1"
PARENT = "9d0d66511fcde0d3e7c16489541c077692f08650"
MODEL = "8e1561eb1a542e21307bac669c42435cf48e59bd"
FARAMA = "7f5853792ea7f04f75614661006d87fcf949f26d"
PYCOLAB = "6504c8065dd5322438f23a2a9026649904f3322a"
EXP_BLOB = "196e71ff8f00ab9df0802f3661cbe845ff8e118c"
EXPECTED = {
    "FaramaMiniGridDoorKey8": "ba501812452b529cf35d4aaa176f9d5a0b5cfbb57a388d67c49dfbc547109486",
    "DeepMindPycolabApprehend": "23d9db17d29ed9646afac1b34000d0be320c2fa50ca424db2f85f1829be11bd7",
}
COUNTS = {"canonical_frozen_boundaries": 42, "canonical_seeded_binary64_inputs": 128,
          "FaramaMiniGridDoorKey8": 160, "DeepMindPycolabApprehend": 160}
BLOCK = ctypes.c_double * 8
POINTER = ctypes.POINTER(ctypes.c_double)


def sha(data):
    return sha256(data).hexdigest()


def pack(values):
    return b"".join(struct.pack("<d", float(x)) for x in values)


def exact(root, expected):
    root = Path(root).resolve(strict=True)
    head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"],
                                   text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"],
                                    text=True).strip()
    if head != expected or dirty:
        raise ValueError("MR34I9B_SOURCE_SHA_OR_WORKTREE_DRIFT")
    return root


def git_blob(root, file):
    return subprocess.check_output(["git", "-C", str(root), "hash-object", str(file)],
                                   text=True).strip()


def frozen(audit, model, farama, pycolab, math_source):
    for root, revision in ((model, MODEL), (farama, FARAMA), (pycolab, PYCOLAB)):
        exact(root, revision)
    if git_blob(math_source, "src/binary64/exp/exp.c") != EXP_BLOB:
        raise ValueError("MR34I9B_COREMATH_EXP_BLOB_DRIFT")
    if subprocess.check_output(["git", "-C", str(math_source), "rev-parse", "HEAD"],
                               text=True).strip() != "74fcd1094a316164c94481f40f5c9658439bee63":
        raise ValueError("MR34I9B_COREMATH_MIRROR_REVISION_DRIFT")
    for file in ("frozen_preregistration.json", "frozen_source_toolchain_lock.json"):
        last = subprocess.check_output(
            ["git", "-C", str(audit), "log", "-1", "--format=%H", "--",
             "research/mr34i9a/" + file], text=True).strip()
        if last != PARENT:
            raise ValueError("MR34I9B_FROZEN_PREREG_OR_LOCK_CHANGED")
    proposal = json.loads((audit / "research/mr34i9a/frozen_preregistration.json").read_text())
    lock = json.loads((audit / "research/mr34i9a/frozen_source_toolchain_lock.json").read_text())
    if (proposal["original_development_inputs"]["total"] != 490 or
        proposal["frozen_proposed_acceptance"]["semantic_scope"].startswith("ENGINEERING_KERNEL_ONLY") is False or
        lock["core_math"]["git_blob_sha"] != EXP_BLOB or
        lock["zig"]["version"] != "0.13.0"):
        raise ValueError("MR34I9B_FROZEN_CONTRACT_DRIFT")
    return proposal, lock


def load(libpath):
    handle = ctypes.CDLL(str(Path(libpath).resolve(strict=True)))
    guard = handle.candidate_environment_ok
    guard.argtypes = []
    guard.restype = ctypes.c_int
    if guard() != 1:
        raise ValueError("MR34I9B_FE_TONEAREST_OR_BINARY64_GUARD_FAIL")
    fn = handle.candidate_sigmoid8
    fn.argtypes = [POINTER, POINTER]
    fn.restype = None
    return fn


def compiled(values, fn):
    result = []
    for offset in range(0, len(values), 8):
        current = list(values[offset:offset + 8])
        current += [0.0] * (8 - len(current))
        inbuf, outbuf = BLOCK(*current), BLOCK()
        fn(inbuf, outbuf)
        result.extend(outbuf[:min(8, len(values) - offset)])
    x = np.asarray(result, dtype=np.float64)
    if len(x) != len(values) or not np.isfinite(x).all() or not ((x >= 0) & (x <= 1)).all():
        raise ValueError("MR34I9B_CANDIDATE_NAN_OR_RANGE_VETO")
    return x


def original(values):
    result = np.empty(len(values), dtype=np.float64)
    for i in range(0, len(values), 8):
        v = np.asarray(values[i:i + 8], dtype=np.float64)
        result[i:i + len(v)] = 1. / (1. + np.exp(-np.clip(v, -35., 35.)))
    return result


def decimal120(values):
    output = []
    for x in values:
        z = max(-35., min(35., float(x)))
        with localcontext(Context(prec=120, rounding=ROUND_HALF_EVEN)):
            q = Decimal.from_float(z)
            output.append(float(Decimal(1) / (Decimal(1) + (-q).exp())))
    return np.asarray(output, dtype=np.float64)


def extract(audit, model, farama, pycolab):
    sys.path.insert(0, str(audit))
    sys.path.insert(0, str(model))
    sys.path.insert(0, str(farama))
    sys.path.insert(0, str(pycolab))
    from research.mr34i4 import kernel_probe as prior
    static, seeded = prior.static_cases(prior.frozen())
    cohorts = {"canonical_frozen_boundaries": static,
               "canonical_seeded_binary64_inputs": seeded}
    original_custody = {}
    for name, source in (("FaramaMiniGridDoorKey8", farama),
                         ("DeepMindPycolabApprehend", pycolab)):
        numbers, receipt = prior.original_source_u(source, name)
        if receipt["source_original_first_preaction_logit_binary64_sha256"] != EXPECTED[name]:
            raise ValueError("MR34I9B_ORIGINAL_PUBLIC_TRAIN_INPUT_SHA_DRIFT")
        cohorts[name] = numbers
        original_custody[name] = receipt["source_native_training_public_action_receipts_sha256"]
    if {name: len(values) for name, values in cohorts.items()} != COUNTS:
        raise ValueError("MR34I9B_INPUT_COUNT_DRIFT")
    return cohorts, original_custody


def peak_rss():
    if sys.platform == "win32":
        import psutil
        value = getattr(psutil.Process().memory_info(), "peak_wset", None)
        if not value:
            raise ValueError("MR34I9B_WINDOWS_PEAK_RSS_UNAVAILABLE")
        return int(value)
    if sys.platform.startswith("linux"):
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    raise ValueError("MR34I9B_UNSUPPORTED_MEASUREMENT_OS")


def one_round(args):
    # Fresh isolated process: identical Python/NumPy dependency import cost,
    # with native library load and actual ctypes ABI charged to candidate.
    kind, file, lib = args
    data = json.loads(Path(file).read_text(encoding="utf-8"))
    values = [float.fromhex(x) for xs in data.values() for x in xs]
    start_load_cpu = time.process_time_ns()
    fn = load(lib) if kind == "candidate" else None
    load_cpu = time.process_time_ns() - start_load_cpu
    kernel = (lambda inputs: compiled(inputs, fn)) if fn else original
    for _ in range(3):
        if len(kernel(values)) != 490:
            raise ValueError("MR34I9B_BENCHMARK_WARMUP_DRIFT")
    start_cpu, start_wall = time.process_time_ns(), time.perf_counter_ns()
    for _ in range(256):
        if len(kernel(values)) != 490:
            raise ValueError("MR34I9B_BENCHMARK_RETURN_DRIFT")
    cpu, wall = time.process_time_ns() - start_cpu, time.perf_counter_ns() - start_wall
    if cpu <= 0 or wall <= 0:
        raise ValueError("MR34I9B_ZERO_OR_CORRUPT_PROCESS_TIMING")
    return {"kind": kind, "cpu_ns": cpu + load_cpu,
            "wall_ns": wall, "library_loading_cpu_ns": load_cpu,
            "process_peak_resident_bytes": peak_rss(), "calls": 256 * 62,
            "FFI_included": kind == "candidate"}


def benchmark(cohorts, lib):
    with tempfile.TemporaryDirectory(prefix="mr34i9b-training-only-") as tmp:
        path = Path(tmp) / "input-cohorts.json"
        path.write_text(json.dumps({n: [float(x).hex() for x in v]
                                    for n, v in cohorts.items()}, sort_keys=True))
        measured = []
        for cycle in range(5):
            pair = {}
            # Balance ABBA within each frozen paired round, with no best-of selection.
            for kind in ("baseline", "candidate", "candidate", "baseline"):
                cmd = [sys.executable, "-B", str(Path(__file__).resolve()),
                       "--bench-child", kind, str(path), str(lib)]
                data = json.loads(subprocess.check_output(cmd, text=True, stderr=None))
                pair.setdefault(kind, []).append(data)
            measured.append(pair)
        per = {name: [statistics.median(row[name][i]["cpu_ns"] / row[name][i]["calls"]
                                         for i in range(2)) for row in measured]
               for name in ("baseline", "candidate")}
        median_baseline = statistics.median(per["baseline"])
        median_candidate = statistics.median(per["candidate"])
        baseline_rss = max(k["process_peak_resident_bytes"]
                           for row in measured for k in row["baseline"])
        candidate_rss = max(k["process_peak_resident_bytes"]
                            for row in measured for k in row["candidate"])
        return {"paired_abba_rounds": measured,
                "median_cpu_ns_per_eightwide": {"baseline": median_baseline,
                                               "candidate": median_candidate},
                "peak_rss_bytes": {"baseline": baseline_rss, "candidate": candidate_rss},
                "cpu_nonregression": median_candidate <= median_baseline,
                "rss_nonregression": candidate_rss <= baseline_rss}


def run(audit, model, farama, pycolab, math_source, lib, output):
    audit, model, farama, pycolab, math_source = map(
        lambda x: Path(x).resolve(strict=True),
        (audit, model, farama, pycolab, math_source))
    frozen(audit, model, farama, pycolab, math_source)
    module_sha = sha(Path(lib).read_bytes())
    source_started = time.process_time_ns()
    cohorts, source_receipts = extract(audit, model, farama, pycolab)
    source_cpu = time.process_time_ns() - source_started
    fn = load(lib)
    outputs = {}
    total = 0
    precision_ok = True
    for name, values in cohorts.items():
        val = np.asarray(values, dtype=np.float64)
        result = compiled(val, fn)
        check = compiled(val, fn)
        baseline, high = original(val), decimal120(val)
        if pack(result) != pack(check):
            raise ValueError("MR34I9B_SAME_WORKER_OUTPUT_DRIFT")
        ulps = [abs(int(a) - int(b)) for a, b in zip(
            result.view(np.uint64), high.view(np.uint64))]
        score = max(ulps, default=-1)
        precision_ok &= score <= 1
        outputs[name] = {
            "n": len(values), "original_frozen_training_input_sha256": sha(pack(values)),
            "candidate_binary64_sha256": sha(pack(result)),
            "unchanged_original_numpy_binary64_sha256": sha(pack(baseline)),
            "decimal120_binary64_sha256": sha(pack(high)),
            "max_candidate_decimal120_ULP": score,
            "original_candidate_nonzero_ULP": sum(
                int(a) != int(b) for a, b in zip(
                    baseline.view(np.uint64), result.view(np.uint64))),
        }
        total += len(values)
    if total != 490:
        raise ValueError("MR34I9B_NOT_FROZEN_490_INPUTS")
    benchmark_result = benchmark(cohorts, lib)
    for root, pin in ((model, MODEL), (farama, FARAMA), (pycolab, PYCOLAB)):
        exact(root, pin)
    if git_blob(math_source, "src/binary64/exp/exp.c") != EXP_BLOB:
        raise ValueError("MR34I9B_COREMATH_POSTRUN_DRIFT")
    if subprocess.check_output(["git", "-C", str(audit),
                               "status", "--porcelain"], text=True).strip():
        raise ValueError("MR34I9B_AUDIT_SOURCE_DIRTY")
    decision = ("ENGINEERING_KERNEL_PASS"
                if precision_ok and benchmark_result["cpu_nonregression"]
                and benchmark_result["rss_nonregression"]
                else "ENGINEERING_KERNEL_NO_GO")
    receipt = {
        "schema": SCHEMA, "verdict": decision,
        "numeric_precision_pass": bool(precision_ok),
        "source_sha": subprocess.check_output(["git", "-C", str(audit),
                                               "rev-parse", "HEAD"], text=True).strip(),
        "original_source_pins": {"s4c1": MODEL, "farama": FARAMA,
                                 "pycolab": PYCOLAB, "cr_exp_mirror": EXP_BLOB},
        "library_sha256": module_sha, "library_bytes": Path(lib).stat().st_size,
        "original_source_collection_cpu_ns": source_cpu,
        "original_public_training_event_sha256": source_receipts,
        "cohorts": outputs, "measurements": benchmark_result,
        "python": sys.version, "numpy": np.__version__, "platform": platform.platform(),
        "original_learner_modified": False, "training_performed": False,
        "scientific_first_use": False, "cognitive_transfer": "NOT_TESTED",
        "G29_project_regression": "NOT_RUN",
    }
    Path(output).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("MR34I9B_RESULT=" + json.dumps({
        "verdict": decision, "precision": bool(precision_ok),
        "cpu": benchmark_result["cpu_nonregression"],
        "rss": benchmark_result["rss_nonregression"],
        "source": receipt["source_sha"],
        "output_hashes": {k: x["candidate_binary64_sha256"]
                          for k, x in outputs.items()}}, sort_keys=True), flush=True)


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "--bench-child":
        print(json.dumps(one_round(sys.argv[2:])))
    elif len(sys.argv) == 9 and sys.argv[1] == "--evaluate":
        run(*sys.argv[2:])
    else:
        raise SystemExit("MR34I9B_INVALID_BOUNDED_EXECUTION_ARGUMENTS")
