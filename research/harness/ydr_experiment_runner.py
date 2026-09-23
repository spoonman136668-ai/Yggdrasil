#!/usr/bin/env python3
"""Isolated deterministic experiment runner for Yggdrasil.

This runner is deliberately narrow:
- repository-local Python experiment entry points only;
- duplicate execution before any optional open/qualification step;
- no shell execution;
- no repository mutation;
- evidence written only to the requested output directory.

The GitHub Actions workflow that invokes this runner uses GitHub-hosted
Ubuntu and read-only repository permissions. It has no dependency on
ckb-plane, KTRADE, Windows services, or self-hosted runners.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

SCHEMA = 1
MAX_TIMEOUT_SECONDS = 1800
FORBIDDEN_TEXT = (
    "ckb-plane",
    "ktrade",
    "self-hosted",
    "actions.runner.",
    "c:\\actions-runner",
    "goprojects\\ckb",
    "goprojects\\ktrade",
)


class RunnerError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def under(root: Path, candidate: Path) -> Path:
    root = root.resolve()
    p = candidate.resolve()
    try:
        p.relative_to(root)
    except ValueError as exc:
        raise RunnerError(f"path escapes repository root: {candidate}") from exc
    return p


def validate_text(value: str, label: str):
    low = value.lower()
    for needle in FORBIDDEN_TEXT:
        if needle in low:
            raise RunnerError(f"forbidden production-coupled token in {label}: {needle}")


def verify_file(root: Path, item: dict):
    path = under(root, root / item["path"])
    if not path.is_file():
        raise RunnerError(f"verify file missing: {item['path']}")
    data = path.read_bytes()
    got = sha256_bytes(data)
    expected = item["sha256"]
    if got != expected:
        raise RunnerError(
            f"verify file hash mismatch path={item['path']} expected={expected} got={got}"
        )
    return {"path": item["path"], "bytes": len(data), "sha256": got}


def render_args(args: list[str], mapping: dict[str, str]) -> list[str]:
    rendered = []
    for raw in args:
        validate_text(raw, "argument")
        try:
            value = raw.format(**mapping)
        except KeyError as exc:
            raise RunnerError(f"unknown argument placeholder: {exc}") from exc
        validate_text(value, "rendered argument")
        rendered.append(value)
    return rendered


def run_one(
    *,
    root: Path,
    source: Path,
    args: list[str],
    stdout_path: Path,
    stderr_path: Path,
    timeout: int,
):
    argv = [sys.executable, str(source), *args]
    cp = subprocess.run(
        argv,
        cwd=root,
        text=False,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    stdout_path.write_bytes(cp.stdout)
    stderr_path.write_bytes(cp.stderr)
    if cp.returncode != 0:
        raise RunnerError(
            f"experiment failed rc={cp.returncode}; "
            f"stdout={stdout_path}; stderr={stderr_path}"
        )
    return {
        "returncode": cp.returncode,
        "stdout_bytes": len(cp.stdout),
        "stdout_sha256": sha256_bytes(cp.stdout),
        "stderr_bytes": len(cp.stderr),
        "stderr_sha256": sha256_bytes(cp.stderr),
    }


def validate_request(req: dict, root: Path):
    if req.get("schema") != SCHEMA:
        raise RunnerError("unsupported request schema")

    request_id = req.get("request_id")
    if not isinstance(request_id, str) or not request_id:
        raise RunnerError("request_id is required")
    validate_text(request_id, "request_id")

    source_rel = req.get("source")
    if not isinstance(source_rel, str) or not source_rel.endswith(".py"):
        raise RunnerError("source must be a repository-local .py file")
    validate_text(source_rel, "source")

    source = under(root, root / source_rel)
    allowed_root = under(root, root / "research" / "applications")
    try:
        source.relative_to(allowed_root)
    except ValueError as exc:
        raise RunnerError("source must live under research/applications") from exc
    if not source.is_file():
        raise RunnerError(f"source missing: {source_rel}")

    timeout = int(req.get("timeout_seconds", 600))
    if timeout < 1 or timeout > MAX_TIMEOUT_SECONDS:
        raise RunnerError(f"timeout_seconds must be in [1,{MAX_TIMEOUT_SECONDS}]")

    run_args = req.get("run_args")
    if not isinstance(run_args, list) or not all(isinstance(x, str) for x in run_args):
        raise RunnerError("run_args must be a list of strings")

    open_args = req.get("open_args")
    if open_args is not None:
        if not isinstance(open_args, list) or not all(isinstance(x, str) for x in open_args):
            raise RunnerError("open_args must be null or a list of strings")

    for item in req.get("verify_files", []):
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("path"), str)
            or not isinstance(item.get("sha256"), str)
            or len(item["sha256"]) != 64
        ):
            raise RunnerError("invalid verify_files entry")
        validate_text(item["path"], "verify path")

    expected_sha = req.get("expected_duplicate_sha256")
    if expected_sha is not None and (
        not isinstance(expected_sha, str) or len(expected_sha) != 64
    ):
        raise RunnerError("expected_duplicate_sha256 must be a 64-char SHA256")

    return source, timeout


def execute(req: dict, root: Path, out_dir: Path):
    source, timeout = validate_request(req, root)
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "schema": SCHEMA,
        "request_id": req["request_id"],
        "repository": os.environ.get("GITHUB_REPOSITORY"),
        "github_sha": os.environ.get("GITHUB_SHA"),
        "source": str(source.relative_to(root)),
        "source_file_sha256": sha256_bytes(source.read_bytes()),
        "verified_files": [],
        "duplicate": None,
        "open": None,
    }

    for item in req.get("verify_files", []):
        meta["verified_files"].append(verify_file(root, item))

    run1 = out_dir / "primary1.bin"
    run2 = out_dir / "primary2.bin"
    run1_stdout = out_dir / "run1.stdout"
    run1_stderr = out_dir / "run1.stderr"
    run2_stdout = out_dir / "run2.stdout"
    run2_stderr = out_dir / "run2.stderr"

    mapping1 = {"out": str(run1), "run1": str(run1), "run2": str(run2)}
    mapping2 = {"out": str(run2), "run1": str(run1), "run2": str(run2)}

    a1 = render_args(req["run_args"], mapping1)
    a2 = render_args(req["run_args"], mapping2)

    r1 = run_one(
        root=root, source=source, args=a1,
        stdout_path=run1_stdout, stderr_path=run1_stderr, timeout=timeout
    )
    r2 = run_one(
        root=root, source=source, args=a2,
        stdout_path=run2_stdout, stderr_path=run2_stderr, timeout=timeout
    )

    if not run1.exists() or not run2.exists():
        raise RunnerError("primary command did not create both requested outputs")

    b1 = run1.read_bytes()
    b2 = run2.read_bytes()
    same = b1 == b2
    dup_sha = sha256_bytes(b1)
    meta["duplicate"] = {
        "byte_identical": same,
        "bytes": len(b1),
        "sha256": dup_sha,
        "run1_process": r1,
        "run2_process": r2,
    }
    save_json(out_dir / "evidence.json", meta)

    if not same:
        raise RunnerError("duplicate primaries are not byte-identical")

    expected_sha = req.get("expected_duplicate_sha256")
    if expected_sha is not None and dup_sha != expected_sha:
        raise RunnerError(
            f"duplicate output hash mismatch expected={expected_sha} got={dup_sha}"
        )

    open_args = req.get("open_args")
    if open_args is not None:
        open_out = out_dir / "open.bin"
        open_stdout = out_dir / "open.stdout"
        open_stderr = out_dir / "open.stderr"
        mapping_open = {
            "out": str(open_out),
            "open_out": str(open_out),
            "run1": str(run1),
            "run2": str(run2),
        }
        oa = render_args(open_args, mapping_open)
        ro = run_one(
            root=root, source=source, args=oa,
            stdout_path=open_stdout, stderr_path=open_stderr, timeout=timeout
        )
        if open_out.exists():
            ob = open_out.read_bytes()
            meta["open"] = {
                "bytes": len(ob),
                "sha256": sha256_bytes(ob),
                "process": ro,
            }
        else:
            meta["open"] = {
                "bytes": ro["stdout_bytes"],
                "sha256": ro["stdout_sha256"],
                "process": ro,
                "output_from_stdout": True,
            }

    save_json(out_dir / "evidence.json", meta)
    print(json.dumps(meta, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    root = Path.cwd().resolve()
    request_path = under(root, root / args.request)
    req = load_json(request_path)

    out_dir = Path(args.out_dir).resolve()
    try:
        execute(req, root, out_dir)
    except (RunnerError, subprocess.TimeoutExpired) as exc:
        out_dir.mkdir(parents=True, exist_ok=True)
        failure = {
            "schema": SCHEMA,
            "error": type(exc).__name__,
            "detail": str(exc),
            "request": req.get("request_id"),
            "github_sha": os.environ.get("GITHUB_SHA"),
        }
        save_json(out_dir / "failure.json", failure)
        print(json.dumps(failure, sort_keys=True), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
