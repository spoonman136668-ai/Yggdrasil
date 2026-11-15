#!/usr/bin/env python3
"""QTR-01 read-only, bounded public Qwen donor-file custody check.

No model inference, activation editing, paid APIs, test-set use or model writes.
A published digest is a claim until this independently hashes the exact bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ATLAS_REPO = "juiceb0xc0de/qwen3.8-27b-atlas"
ATLAS_REV = "25493cfe8f844ccae2e294778b47c56ed8ae1d66"
SAE_REPO = "LeonInverse/qwen3.8-27b-scope-code"
SAE_REV = "0f965454ffedb93e826546a7dc11b51a4622188e"

@dataclass(frozen=True)
class Source:
    name: str
    url: str
    local_path: str
    max_bytes: int
    published_sha256: str | None
    kind: str

SOURCES = (
    Source("atlas_layers", f"https://huggingface.co/datasets/{ATLAS_REPO}/resolve/{ATLAS_REV}/data/layers.parquet", "atlas/layers.parquet", 20_000,
           "2abafbe4ad6114cae9c2bfa24ce544f26396c70af71ecb259c2046fb6d95a9bd", "layers"),
    Source("atlas_coactivation", f"https://huggingface.co/datasets/{ATLAS_REPO}/resolve/{ATLAS_REV}/data/coactivation.parquet", "atlas/coactivation.parquet", 1_000_000,
           "f347062207a010f63c64708cfdf9afb6c872c7a35efa52d4dfc93be535333efd", "coactivation"),
    Source("sae_utility", f"https://huggingface.co/{SAE_REPO}/resolve/{SAE_REV}/scores/utility.jsonl", "sae/scores/utility.jsonl", 262_144,
           None, "utility"),
)

class CheckError(ValueError):
    pass


def get_bounded(url: str, max_bytes: int) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "qtr01-custody/1.0"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = resp.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise CheckError("SOURCE_TOO_LARGE")
    if not data:
        raise CheckError("SOURCE_EMPTY")
    return data


def read_local(root: Path, spec: Source) -> bytes:
    path = root / spec.local_path
    if not path.is_file():
        raise CheckError(f"MISSING_FILE: {spec.local_path}")
    if path.stat().st_size > spec.max_bytes:
        raise CheckError("SOURCE_TOO_LARGE")
    data = path.read_bytes()
    if not data:
        raise CheckError("SOURCE_EMPTY")
    return data


def check_sha(spec: Source, data: bytes) -> str:
    if len(data) > spec.max_bytes or not data:
        raise CheckError("INVALID_BYTE_BOUND")
    digest = hashlib.sha256(data).hexdigest()
    if spec.published_sha256 and digest != spec.published_sha256:
        raise CheckError(f"PUBLISHED_HASH_MISMATCH: {spec.name}: got {digest}")
    return digest


def _numeric(v: object) -> bool:
    return type(v) in (int, float) and math.isfinite(v)


def check_utility(data: bytes) -> dict:
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeDecodeError as e:
        raise CheckError("UTILITY_NOT_UTF8") from e
    if not lines or len(lines) > 100_000:
        raise CheckError("UTILITY_INVALID_ROWS")
    keys: set[str] = set()
    for line in lines:
        if not line.strip():
            raise CheckError("UTILITY_BLANK_ROW")
        try:
            obj = json.loads(line, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
        except (ValueError, TypeError) as e:
            raise CheckError("UTILITY_BAD_JSON") from e
        if not isinstance(obj, dict) or not obj:
            raise CheckError("UTILITY_NOT_OBJECT")
        keys.update(obj)
        for field in ("dCE", "dM"):
            if field in obj and not _numeric(obj[field]):
                raise CheckError("UTILITY_NONFINITE_SCORE")
    # Do not invent a feature ID schema before independently inspecting first-party rows.
    # Passing here only certifies parsable and bounded JSONL, never feature semantics.
    return {"jsonl_records": len(lines), "observed_fields": sorted(keys),
            "validation": "JSONL_SYNTAX_ONLY; SEMANTIC_SCHEMA_UNVERIFIED"}


def check_parquet(data: bytes, kind: str) -> dict:
    if len(data) < 12 or data[:4] != b"PAR1" or data[-4:] != b"PAR1":
        raise CheckError("PARQUET_MAGIC_INVALID")
    try:
        import pyarrow.parquet as pq
    except ImportError as e:
        raise CheckError("PYARROW_REQUIRED_FOR_SCHEMA_CHECK") from e
    try:
        table = pq.read_table(io.BytesIO(data))
    except Exception as e:
        raise CheckError("PARQUET_DECODE_FAIL") from e
    required = ({"layer_id", "component", "feature_a", "feature_b", "correlation", "dominant_bucket"}
                if kind == "coactivation" else {"layer_id"})
    if not required.issubset(table.column_names):
        raise CheckError("PARQUET_SCHEMA_MISMATCH")
    expected = 35_412 if kind == "coactivation" else 64
    if table.num_rows != expected:
        raise CheckError(f"PARQUET_ROWCOUNT_MISMATCH: {table.num_rows} != {expected}")
    ids = table.column("layer_id").to_pylist()
    if any(type(x) is not int or not (0 <= x < 64) for x in ids):
        raise CheckError("LAYER_ID_INVALID")
    if kind == "coactivation":
        for val in table.column("correlation").to_pylist():
            if not _numeric(val) or not -1 <= val <= 1:
                raise CheckError("CORRELATION_INVALID")
    return {"rows": table.num_rows, "columns": sorted(table.column_names),
            "validation": "PARQUET_SCHEMA_AND_VALUES_CHECKED; SEMANTIC_INTERPRETATION_UNVERIFIED"}


def audit(spec: Source, data: bytes) -> dict:
    digest = check_sha(spec, data)
    checked = check_utility(data) if spec.kind == "utility" else check_parquet(data, spec.kind)
    return {"name": spec.name, "source_url": spec.url, "bytes": len(data),
            "observed_sha256": digest,
            "published_sha256_matched": spec.published_sha256 is not None,
            "source_revision_pinned": True, **checked}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--fetch", action="store_true", help="Retrieve only three pinned files from public Hugging Face; no Qwen inference")
    group.add_argument("--local-dir", type=Path, help="Read existing files under atlas/ and sae/ without network")
    args = p.parse_args(argv)
    records: list[dict] = []
    try:
        for spec in SOURCES:
            data = get_bounded(spec.url, spec.max_bytes) if args.fetch else read_local(args.local_dir, spec)
            records.append(audit(spec, data))
    except (CheckError, OSError, TimeoutError, ValueError) as e:
        print(f"QTR01_INPUTS_FAIL_CLOSED: {e}", file=sys.stderr)
        return 1
    print(json.dumps({"schema": "yggdrasil.qtr01.bounded-donor-custody.v1",
                      "status": "BYTE_AND_SCHEMA_PREFLIGHT_ONLY; NO_SCIENCE",
                      "records": records}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
