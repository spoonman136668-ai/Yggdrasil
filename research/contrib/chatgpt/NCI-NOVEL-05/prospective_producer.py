"""NCI-NOVEL-05 source-free engineering per-world producer, NOT a science runner.

Opens and verifies the frozen preprimary source archive. Runs only fresh, explicitly
reserved ENGINEERING seeds. Persistent pre-execution attempts prevent crash replay.
Never loads the original frozen PRIMARY seeds or promotes output to a learner.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import platform
import subprocess
import sys
import tarfile
import time
import types
from pathlib import Path

from receipt_guard import budget_gate, commit_world, read_verified

ARCHIVE_SHA = "532fc6a824f1b50fe4cfaf7880619407a2a25a73f888db045e145d2782568e40"
EXPERIMENT_SHA = "ce72306fa92c5b474e779427933e819bc59f262f491b849d6081bf4b24708e56"
ARCHIVE = Path(__file__).with_name("source_preprimary.tar.gz")
FAMILIES = ("fourfold", "conj_pair", "action_switch", "parity_mix",
            "unchanged", "unidentifiable", "degree_five")
ENGINEERING_SEEDS = (917201, 917203, 917207)
CONSUMED = (809001, 809011, 809033, 809057, 809089)
PROTOCOL = "nci05.engineering-world-producer.v1"


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def frozen_experiment(archive: Path = ARCHIVE) -> str:
    """Return checked original source; reject any archive drift and path substitution."""
    data = archive.read_bytes()
    if _hash(data) != ARCHIVE_SHA:
        raise ValueError("frozen archive mismatch")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        names = [m.name for m in tar.getmembers() if m.isfile()]
        if sorted(names) != ["experiment.py", "pilot.json", "test_experiment.py"]:
            raise ValueError("frozen archive members mismatch")
        src = tar.extractfile("experiment.py").read()
    if _hash(src) != EXPERIMENT_SHA:
        raise ValueError("frozen executable mismatch")
    return src.decode("utf-8")


def source_identity(archive: Path = ARCHIVE) -> str:
    """Bind receipt custody to exact archive, wrapper, guard and runtime environment."""
    frozen_experiment(archive)
    import numpy as np
    import sklearn
    components = {"schema": PROTOCOL, "archive": ARCHIVE_SHA,
                  "producer": _hash(Path(__file__).read_bytes()),
                  "guard": _hash(Path(__file__).with_name("receipt_guard.py").read_bytes()),
                  "python": platform.python_version(), "platform": platform.platform(),
                  "numpy": np.__version__, "sklearn": sklearn.__version__}
    return _hash(json.dumps(components, sort_keys=True, separators=(",", ":")).encode())


def _worker(*, archive: Path, seed: int, family: str, claim: Path,
            source_key: str, output: Path) -> None:
    """Internal child worker; rejects direct seeds without matching issued claim."""
    if type(seed) is not int or seed not in ENGINEERING_SEEDS or family not in FAMILIES:
        raise ValueError("internal worker seed/family denied")
    if source_identity(archive) != source_key:
        raise ValueError("internal worker source drift")
    if claim.is_symlink():
        raise ValueError("internal worker claim is symlink")
    receipt = json.loads(claim.read_text("utf-8"))
    if receipt != {"schema": PROTOCOL, "world_id": f"engineering:{seed}:{family}",
                   "source_sha256": source_key}:
        raise ValueError("internal worker claim mismatch")
    module = types.ModuleType("_frozen_nci05_engineering")
    module.__file__ = str(archive) + ":experiment.py"
    exec(compile(frozen_experiment(archive), module.__file__, "exec"), module.__dict__)
    result = module.single(seed, family)
    with open(output, "x", encoding="utf-8") as out:
        json.dump(result, out, sort_keys=True, allow_nan=False)
        out.flush()
        os.fsync(out.fileno())


def _engine(seed: int, family: str, archive: Path, claim: Path,
            source_key: str, timeout: float):
    """Kill the one-world child on timeout; leave claim for manual custody."""
    output = claim.with_name(claim.name + ".result")
    args = [sys.executable, str(Path(__file__).resolve()), "--internal-worker",
            "--archive", str(archive.resolve()), "--seed", str(seed),
            "--family", family, "--claim", str(claim.resolve()),
            "--source-key", source_key, "--worker-out", str(output.resolve())]
    try:
        subprocess.run(args, timeout=timeout, check=True, capture_output=True)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("engineering world timed out; seed remains consumed") from exc
    if not output.is_file() or output.is_symlink():
        raise ValueError("worker result missing or invalid")
    return json.loads(output.read_text("utf-8"))


def run_engineering_world(*, ledger: Path, archive: Path, seed: int, family: str,
                          single=None, source_key: str | None = None,
                          max_world_seconds: float = 60.0) -> str:
    """One explicitly claimed engineering world. Never automatically replay a claim."""
    if type(seed) is not int or seed not in ENGINEERING_SEEDS or seed in CONSUMED:
        raise ValueError("seed not an unused engineering-only seed")
    if family not in FAMILIES:
        raise ValueError("unknown engineering family")
    if (type(max_world_seconds) not in (int, float) or not math.isfinite(max_world_seconds)
            or max_world_seconds <= 0):
        raise ValueError("invalid bounded world timeout")
    identity = source_key if source_key is not None else source_identity(archive)
    if len(identity) != 64 or any(c not in "0123456789abcdef" for c in identity):
        raise ValueError("invalid source identity")
    world_id = f"engineering:{seed}:{family}"
    existing = read_verified(ledger, identity)
    if any(e["world_id"] == world_id for e in existing):
        raise ValueError("world already committed: no replay")
    ledger.parent.mkdir(parents=True, exist_ok=True)
    claim = ledger.with_name(f"{ledger.name}.engineering-{seed}-{family}.attempt")
    # The durable claim is written BEFORE generating a consequence. An orphan
    # is an exposed seed requiring owner review, never a retry ticket.
    fd = os.open(claim, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as out:
        out.write((json.dumps({"schema": PROTOCOL, "world_id": world_id,
                               "source_sha256": identity}, sort_keys=True) + "\n").encode())
        out.flush()
        os.fsync(out.fileno())
    t0 = time.perf_counter()
    metrics = (single(seed, family) if single is not None else
               _engine(seed, family, archive, claim, identity, max_world_seconds))
    elapsed = max(1, math.ceil((time.perf_counter() - t0) * 1000))
    if not isinstance(metrics, dict) or metrics.get("seed") != seed or metrics.get("family") != family:
        raise ValueError("world result identity mismatch: attempt remains consumed")
    payload = {"complete": True, "mode": "ENGINEERING_ONLY", "seed": seed,
               "family": family, "native_owner_admitted": False,
               "original_source_first_use": False, "metrics": metrics}
    return commit_world(ledger, source_sha256=identity, world_id=world_id,
                        elapsed_ms=elapsed, result=payload)


def qualify_budget(*, ledger: Path, source_key: str, target_worlds: int,
                   budget_seconds: float) -> dict:
    entries = read_verified(ledger, source_key)
    samples = {f: {} for f in FAMILIES}
    for row in entries:
        result = row["result"]
        seed, family = result.get("seed"), result.get("family")
        if (result.get("mode") != "ENGINEERING_ONLY" or result.get("complete") is not True
                or result.get("native_owner_admitted") is not False
                or result.get("original_source_first_use") is not False
                or type(seed) is not int or seed not in ENGINEERING_SEEDS
                or family not in FAMILIES
                or row["world_id"] != f"engineering:{seed}:{family}"):
            raise ValueError("foreign or invalid engineering receipt")
        samples[family][seed] = row["elapsed_ms"] / 1000
    if any(set(values) != set(ENGINEERING_SEEDS) for values in samples.values()):
        raise ValueError("incomplete engineering per-family profile")
    result = budget_gate({f: list(values.values()) for f, values in samples.items()},
                         target_worlds, budget_seconds)
    return {"schema": "nci05.engineering-budget-qualification.v1",
            "source_sha256": source_key, "science_executed": False,
            "worlds_measured": len(entries), "families_measured": len(FAMILIES),
            **result}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument("--engineering-world", action="store_true")
    action.add_argument("--qualify-budget", action="store_true")
    action.add_argument("--internal-worker", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--ledger", type=Path)
    p.add_argument("--archive", type=Path, default=ARCHIVE)
    p.add_argument("--seed", type=int)
    p.add_argument("--family", choices=FAMILIES)
    p.add_argument("--target-worlds", type=int, default=4)
    p.add_argument("--budget-seconds", type=float)
    p.add_argument("--max-world-seconds", type=float)
    p.add_argument("--claim", type=Path, help=argparse.SUPPRESS)
    p.add_argument("--source-key", help=argparse.SUPPRESS)
    p.add_argument("--worker-out", type=Path, help=argparse.SUPPRESS)
    opts = p.parse_args()
    if opts.internal_worker:
        if (opts.seed is None or opts.family is None or opts.claim is None or
                opts.source_key is None or opts.worker_out is None):
            p.error("internal worker requires exact claim and output")
        _worker(archive=opts.archive, seed=opts.seed, family=opts.family,
                claim=opts.claim, source_key=opts.source_key, output=opts.worker_out)
        return
    if opts.ledger is None:
        p.error("ledger required outside internal worker")
    if opts.claim is not None or opts.source_key is not None or opts.worker_out is not None:
        p.error("internal-only parameters are forbidden")
    source_key = source_identity(opts.archive)
    if opts.engineering_world:
        if (opts.seed is None or opts.family is None or opts.budget_seconds is not None
                or opts.max_world_seconds is None):
            p.error("world mode requires seed+family and forbids budget qualification")
        receipt = run_engineering_world(ledger=opts.ledger, archive=opts.archive,
                                       seed=opts.seed, family=opts.family,
                                       source_key=source_key,
                                       max_world_seconds=opts.max_world_seconds)
        print(json.dumps({"mode": "ENGINEERING_ONLY", "receipt_sha256": receipt}, sort_keys=True))
    else:
        if (opts.seed is not None or opts.family is not None or opts.budget_seconds is None
                or opts.max_world_seconds is not None):
            p.error("qualification requires only --budget-seconds")
        print(json.dumps(qualify_budget(ledger=opts.ledger, source_key=source_key,
                                        target_worlds=opts.target_worlds,
                                        budget_seconds=opts.budget_seconds), sort_keys=True))


if __name__ == "__main__":
    main()
