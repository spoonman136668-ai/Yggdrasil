#!/usr/bin/env python3
"""Deterministic research harness for Yggdrasil Application-A experiments.

Scientific mechanisms remain in experiment modules. This harness handles
artifact integrity, stage bookkeeping, duplicate-run comparison, portable
parent recovery, and evidence serialization.

Canonical source policy:
  1. Prefer a normal readable Python source file with a frozen SHA-256.
  2. Loader + gzip/base64 payload remains supported as a legacy archive path.
  3. A broken legacy archive fails closed and is reported as an archival defect.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import gzip
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SCHEMA = 1
ALLOWED = {
    "PREREGISTERED": {"PARENT_VERIFIED"},
    "PARENT_VERIFIED": {"IMPLEMENTED"},
    "IMPLEMENTED": {"MECHANICAL_VERIFIED"},
    "MECHANICAL_VERIFIED": {"FROZEN"},
    "FROZEN": {"MANIFEST_BOUND"},
    "MANIFEST_BOUND": {"PRIMARY_VERIFIED"},
    "PRIMARY_VERIFIED": {"CLOSED"},
    "CLOSED": set(),
}


class HarnessError(RuntimeError):
    pass


class ArchivalDefect(HarnessError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def expected_from_loader(loader: Path) -> str:
    txt = loader.read_text(encoding="utf-8")
    m = re.search(r"EXPECTED=['\"]([0-9a-f]{64})['\"]", txt)
    if not m:
        raise HarnessError(f"no EXPECTED sha256 in loader: {loader}")
    return m.group(1)


def verify_plain(source: Path, expected: str):
    data = source.read_bytes()
    got = sha256_bytes(data)
    if got != expected:
        raise HarnessError(
            f"canonical source hash mismatch source={source} expected={expected} got={got}"
        )
    return got, len(data)


def materialize_archive(loader: Path, payload: Path, out: Path):
    expected = expected_from_loader(loader)
    try:
        encoded = payload.read_text(encoding="utf-8").strip()
        raw = base64.b64decode(encoded, validate=True)
    except (OSError, UnicodeError, binascii.Error, ValueError) as exc:
        raise ArchivalDefect(f"archive base64 failure payload={payload}: {exc}") from exc
    try:
        src = gzip.decompress(raw)
    except (OSError, EOFError, gzip.BadGzipFile, zlib_error()) as exc:
        raise ArchivalDefect(f"archive gzip failure payload={payload}: {exc}") from exc
    got = sha256_bytes(src)
    if got != expected:
        raise ArchivalDefect(
            f"archive source hash mismatch payload={payload} expected={expected} got={got}"
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(src)
    return got, len(src), "legacy_archive"


def zlib_error():
    # Avoid importing zlib into experiment modules through wildcard patterns.
    import zlib
    return zlib.error


def materialize_parent(parent: dict):
    expected = parent["expected_source_sha256"]
    canonical = parent.get("canonical_source")
    if canonical:
        source = Path(canonical)
        if source.exists():
            got, n = verify_plain(source, expected)
            return got, n, "canonical_source"

    loader = parent.get("loader")
    payload = parent.get("payload")
    out = parent.get("materialized_source")
    if not loader or not payload or not out:
        raise HarnessError(
            "parent has no usable canonical_source and legacy archive fields are incomplete"
        )
    got, n, mode = materialize_archive(Path(loader), Path(payload), Path(out))
    if got != expected:
        raise HarnessError("state expected parent hash differs from recovered source")
    return got, n, mode


def transition_state(state: dict, target: str):
    cur = state["status"]
    if target != cur and target not in ALLOWED.get(cur, set()):
        raise HarnessError(f"illegal transition {cur} -> {target}")
    state["status"] = target


def transition(state_path: Path, target: str, updates: dict | None = None):
    state = load_json(state_path)
    if state.get("schema") != SCHEMA:
        raise HarnessError("unsupported state schema")
    transition_state(state, target)
    if updates:
        state.update(updates)
    save_json(state_path, state)
    return state


def run_pair(command, out1: Path, out2: Path, evidence: Path):
    def one(out):
        argv = [str(out) if x == "{out}" else x for x in command]
        cp = subprocess.run(argv, text=True, capture_output=True)
        if cp.returncode:
            sys.stdout.write(cp.stdout)
            sys.stderr.write(cp.stderr)
            raise HarnessError(f"command failed rc={cp.returncode}: {argv}")
        if not out.exists():
            raise HarnessError(f"command succeeded but expected output is missing: {out}")

    out1.parent.mkdir(parents=True, exist_ok=True)
    one(out1)
    one(out2)
    b1, b2 = out1.read_bytes(), out2.read_bytes()
    same = b1 == b2
    ev = {
        "byte_identical": same,
        "run1_sha256": sha256_bytes(b1),
        "run2_sha256": sha256_bytes(b2),
        "run1_bytes": len(b1),
        "run2_bytes": len(b2),
        "command": command,
    }
    save_json(evidence, ev)
    print(json.dumps(ev, sort_keys=True))
    if not same:
        raise HarnessError("duplicate runs are not byte-identical")
    return ev


def doctor(state_path: Path):
    state = load_json(state_path)
    problems = []
    if state.get("schema") != SCHEMA:
        problems.append("unsupported_schema")
    parent = state.get("parent") or {}
    expected = parent.get("expected_source_sha256")
    if expected and not re.fullmatch(r"[0-9a-f]{64}", expected):
        problems.append("invalid_parent_sha256")
    canonical = parent.get("canonical_source")
    if canonical and Path(canonical).exists() and expected:
        try:
            verify_plain(Path(canonical), expected)
        except HarnessError as exc:
            problems.append(str(exc))
    report = {
        "experiment": state.get("experiment"),
        "status": state.get("status"),
        "parent_verified": bool(parent.get("verified")),
        "canonical_source_present": bool(canonical and Path(canonical).exists()),
        "legacy_archive_configured": bool(parent.get("loader") and parent.get("payload")),
        "problems": problems,
        "ok": not problems,
    }
    print(json.dumps(report, sort_keys=True))
    if problems:
        raise HarnessError("doctor found problems")


def apply_request(request_path: Path, state_path: Path):
    req = load_json(request_path)
    state = load_json(state_path)
    if req.get("experiment") != state.get("experiment"):
        raise HarnessError("request/state experiment mismatch")

    action = req["action"]
    if action == "materialize_parent":
        parent = state["parent"]
        got, n, mode = materialize_parent(parent)
        parent["verified"] = True
        parent["verified_bytes"] = n
        parent["verified_source_sha256"] = got
        parent["verified_via"] = mode
        state["parent"] = parent
        transition_state(state, "PARENT_VERIFIED")
        state["last_request"] = req
        save_json(state_path, state)
        print(json.dumps({
            "parent_verified": True,
            "bytes": n,
            "sha256": got,
            "mode": mode,
        }, sort_keys=True))
        return

    if action == "run_pair":
        ev = run_pair(
            req["command"],
            Path(req["out1"]),
            Path(req["out2"]),
            Path(req["evidence"]),
        )
        state["last_request"] = req
        state["last_pair"] = ev
        save_json(state_path, state)
        return

    raise HarnessError(f"unknown action: {action}")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("materialize")
    p.add_argument("--loader", required=True)
    p.add_argument("--payload", required=True)
    p.add_argument("--out", required=True)

    p = sp.add_parser("verify-source")
    p.add_argument("--source", required=True)
    p.add_argument("--sha256", required=True)

    p = sp.add_parser("transition")
    p.add_argument("--state", required=True)
    p.add_argument("--to", required=True)

    p = sp.add_parser("doctor")
    p.add_argument("--state", required=True)

    p = sp.add_parser("apply-request")
    p.add_argument("--request", required=True)
    p.add_argument("--state", required=True)

    args = ap.parse_args()
    try:
        if args.cmd == "materialize":
            got, n, mode = materialize_archive(
                Path(args.loader), Path(args.payload), Path(args.out)
            )
            print(json.dumps({"bytes": n, "sha256": got, "mode": mode}, sort_keys=True))
        elif args.cmd == "verify-source":
            got, n = verify_plain(Path(args.source), args.sha256)
            print(json.dumps({"bytes": n, "sha256": got}, sort_keys=True))
        elif args.cmd == "transition":
            transition(Path(args.state), args.to)
        elif args.cmd == "doctor":
            doctor(Path(args.state))
        elif args.cmd == "apply-request":
            apply_request(Path(args.request), Path(args.state))
    except ArchivalDefect as exc:
        print(json.dumps({"error": "ARCHIVAL_DEFECT", "detail": str(exc)}, sort_keys=True), file=sys.stderr)
        raise SystemExit(20)
    except HarnessError as exc:
        print(json.dumps({"error": "HARNESS_ERROR", "detail": str(exc)}, sort_keys=True), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
