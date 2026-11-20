"""Source-free NCI-NOVEL-05 follow-up: single-writer, crash-safe world receipts.

No learner import, source generation, inference, scheduling, or automatic replay.
The original NCI-NOVEL-05 primary seeds remain permanently consumed.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

FORMAT = "nci-world-receipts.v1"
ZERO = "0" * 64


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canon(value)).hexdigest()


def read_verified(path: str | Path, expected_source_sha256: str) -> list[dict]:
    """Verify each hash-linked record; never repair or infer a partial world."""
    path = Path(path)
    if not path.exists():
        return []
    entries = []
    previous = ZERO
    seen: set[str] = set()
    for n, raw in enumerate(path.read_bytes().splitlines(), start=1):
        try:
            entry = json.loads(raw)
            digest = entry.pop("entry_sha256")
            if set(entry) != {"schema", "source_sha256", "world_id", "prev_sha256", "elapsed_ms", "result"}:
                raise ValueError("unexpected record fields")
            if entry["schema"] != FORMAT or entry["source_sha256"] != expected_source_sha256:
                raise ValueError("schema/source mismatch")
            if entry["prev_sha256"] != previous or digest != _sha(entry):
                raise ValueError("broken hash chain")
            if not isinstance(entry["world_id"], str) or not entry["world_id"] or entry["world_id"] in seen:
                raise ValueError("missing/duplicate world")
            if not isinstance(entry["elapsed_ms"], int) or entry["elapsed_ms"] < 0:
                raise ValueError("invalid timing")
            if not isinstance(entry["result"], dict):
                raise ValueError("missing complete world result")
            seen.add(entry["world_id"])
            previous = digest
            entries.append({**entry, "entry_sha256": digest})
        except (ValueError, TypeError, KeyError, UnicodeDecodeError) as exc:
            raise ValueError(f"invalid receipt at line {n}: {exc}") from exc
    return entries


def commit_world(path: str | Path, *, source_sha256: str, world_id: str,
                 elapsed_ms: int, result: dict) -> str:
    """Atomically commit a completed world; refusal is the default for uncertainty.

    A lock orphaned by crash is NOT automatically removed: an owner must inspect it.
    This code does not run, resume or reissue any world or action.
    """
    if len(source_sha256) != 64 or any(c not in "0123456789abcdef" for c in source_sha256):
        raise ValueError("source must be a lowercase SHA-256")
    if not isinstance(world_id, str) or not world_id or "\n" in world_id:
        raise ValueError("world ID required")
    if type(elapsed_ms) is not int or elapsed_ms < 0 or not isinstance(result, dict):
        raise ValueError("complete world result and nonnegative duration required")
    _canon(result)  # Refuse NaN, infinity and unserializable receipts before filesystem writes.
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + ".lock")
    tmp = path.with_name(path.name + ".tmp")
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.close(fd)
        entries = read_verified(path, source_sha256)
        if any(e["world_id"] == world_id for e in entries):
            raise ValueError("world already committed: no replay")
        previous = entries[-1]["entry_sha256"] if entries else ZERO
        entry = {"schema": FORMAT, "source_sha256": source_sha256,
                 "world_id": world_id, "prev_sha256": previous,
                 "elapsed_ms": elapsed_ms, "result": result}
        digest = _sha(entry)
        serialized = entries + [{**entry, "entry_sha256": digest}]
        with open(tmp, "xb") as out:
            for row in serialized:
                out.write(_canon(row) + b"\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp, path)
        if hasattr(os, "O_DIRECTORY"):
            directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        return digest
    finally:
        # Never remove a left-over tmp unless this writer created it and has finished.
        # Interrupted processes leave lock/tmp for external manual custody review.
        lock.unlink()


def budget_gate(per_family_seconds: dict[str, list[float]],
                target_worlds_per_family: int, budget_seconds: float,
                *, safety_factor: float = 1.5) -> dict:
    """Conservative upper-bound gate from >=3 fresh engineering timings/family.

    Not a scheduler and not an authorization to consume any scientific cohort.
    """
    if target_worlds_per_family < 1 or budget_seconds <= 0 or safety_factor < 1.0:
        raise ValueError("invalid budget")
    estimated = 0.0
    for family, samples in per_family_seconds.items():
        if len(samples) < 3 or any(not math.isfinite(t) or t <= 0 for t in samples):
            raise ValueError(f"unqualified timing sample: {family}")
        estimated += max(samples) * target_worlds_per_family
    projected = estimated * safety_factor
    return {"projected_seconds": round(projected, 3),
            "budget_seconds": budget_seconds, "qualified": projected <= budget_seconds}
