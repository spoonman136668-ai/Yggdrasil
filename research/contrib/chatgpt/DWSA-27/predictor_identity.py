"""DWSA-27: source-only learned-predictor identity guard for pinned NumPy .npz donors.

This is an engineering custody check, not a donor forward pass, training,
scientific trial, source-world action, or authorization for first use.
It fingerprints the *four original predictor tensors*, not the ZIP filename.
Uses only the Python standard library, never imports a donor or NumPy.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import math
from pathlib import Path
import re
import struct
import sys
import zipfile

SCHEMA = "yggdrasil.dwsa27.predictor-identity.v1"
MAX_ARCHIVE_BYTES = 16 * 1024 * 1024
MAX_ARRAY_BYTES = 8 * 1024 * 1024
MAX_MEMBERS = 64
# Pinned source model.py, TinyJEPA(latent_dim=32, n_actions=5), ReLU MLP.
FIELDS = (
    ("pred.0.W.npy", (37, 64)),
    ("pred.0.b.npy", (64,)),
    ("pred.1.W.npy", (64, 32)),
    ("pred.1.b.npy", (32,)),
)


class SourceRejected(ValueError):
    """A checkpoint is not a safe, compatible original predictor source."""


def _git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _read_npy(raw: bytes, shape: tuple[int, ...]) -> bytes:
    """Return canonical little-endian float32 data; reject object/pickle arrays."""
    if len(raw) < 12 or raw[:6] != b"\x93NUMPY":
        raise SourceRejected("DWSA27_NPY_MAGIC")
    version = tuple(raw[6:8])
    if version == (1, 0):
        start, length = 10, struct.unpack_from("<H", raw, 8)[0]
    elif version in ((2, 0), (3, 0)):
        start, length = 12, struct.unpack_from("<I", raw, 8)[0]
    else:
        raise SourceRejected("DWSA27_NPY_VERSION")
    if not 0 < length <= 4096 or start + length > len(raw):
        raise SourceRejected("DWSA27_NPY_HEADER_SIZE")
    try:
        head = ast.literal_eval(raw[start:start + length].decode("latin-1"))
    except (ValueError, SyntaxError, UnicodeError) as exc:
        raise SourceRejected("DWSA27_NPY_HEADER") from exc
    if not isinstance(head, dict) or set(head) != {"descr", "fortran_order", "shape"}:
        raise SourceRejected("DWSA27_NPY_SCHEMA")
    if head["descr"] not in ("<f4", "=f4", "|f4"):
        raise SourceRejected("DWSA27_NPY_DTYPE")
    if head["fortran_order"] is not False or head["shape"] != shape:
        raise SourceRejected("DWSA27_NPY_SHAPE_OR_ORDER")
    n = math.prod(shape)
    data = raw[start + length:]
    if len(data) != n * 4:
        raise SourceRejected("DWSA27_NPY_ARRAY_SIZE")
    canonical = bytearray()
    for (value,) in struct.iter_unpack("<f", data):
        if not math.isfinite(value):
            raise SourceRejected("DWSA27_NONFINITE")
        # Numerical identity, not incidental ZIP/header encoding: -0.0 == +0.0.
        canonical.extend(struct.pack("<f", 0.0 if value == 0.0 else value))
    return bytes(canonical)


def inspect(path: Path, *, expected_blob_sha1: str | None = None) -> dict[str, object]:
    """Read-only; source file identity and *predictor* identity are distinct."""
    if not path.is_file() or not 0 < path.stat().st_size <= MAX_ARCHIVE_BYTES:
        raise SourceRejected("DWSA27_ARCHIVE_SIZE")
    raw = path.read_bytes()
    sha1 = _git_blob_sha1(raw)
    if expected_blob_sha1 is not None and sha1 != expected_blob_sha1:
        raise SourceRejected("DWSA27_SOURCE_GIT_SHA1")
    digest = hashlib.sha256(b"DWSA27-PREDICTOR-IDENTITY-V1\0")
    field_digests = {}
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            infos = zf.infolist()
            if not 0 < len(infos) <= MAX_MEMBERS:
                raise SourceRejected("DWSA27_MEMBER_COUNT")
            names = [entry.filename for entry in infos]
            if len(names) != len(set(names)):
                raise SourceRejected("DWSA27_DUPLICATE_MEMBER")
            if any(entry.compress_type != zipfile.ZIP_STORED or
                   entry.flag_bits & 1 or entry.file_size > MAX_ARRAY_BYTES or
                   entry.file_size < 0 or entry.filename.startswith("/") or
                   ".." in entry.filename.split("/") for entry in infos):
                raise SourceRejected("DWSA27_UNSAFE_MEMBER")
            for name, shape in FIELDS:
                if name not in names:
                    raise SourceRejected("DWSA27_MISSING_PREDICTOR_FIELD")
                # A bounded read, with exact NPY payload length checked below.
                data = _read_npy(zf.read(name), shape)
                field_digests[name] = hashlib.sha256(data).hexdigest()
                digest.update(name.encode("ascii") + b"\0")
                digest.update(struct.pack("<I", len(shape)))
                for axis in shape:
                    digest.update(struct.pack("<I", axis))
                digest.update(data)
    except (zipfile.BadZipFile, OSError, EOFError, RuntimeError) as exc:
        raise SourceRejected("DWSA27_INVALID_ZIP") from exc
    return {
        "path": str(path),
        "git_blob_sha1": sha1,
        "predictor_sha256": digest.hexdigest(),
        "field_sha256": field_digests,
    }


def compare(paths: list[Path], expected: dict[str, str] | None = None) -> dict[str, object]:
    if len(paths) < 2 or len(paths) > 16 or len({str(p) for p in paths}) != len(paths):
        raise SourceRejected("DWSA27_SOURCE_ROSTER")
    expected = expected or {}
    if set(expected) - {str(p) for p in paths}:
        raise SourceRejected("DWSA27_UNEXPECTED_PIN")
    sources = [inspect(p, expected_blob_sha1=expected.get(str(p))) for p in paths]
    groups: dict[str, list[str]] = {}
    for source in sources:
        groups.setdefault(str(source["predictor_sha256"]), []).append(str(source["path"]))
    duplicates = [sorted(group) for group in groups.values() if len(group) > 1]
    return {
        "schema": SCHEMA,
        "status": "DUPLICATE_PREDICTOR_FOUND" if duplicates else "DISTINCT_PREDICTORS",
        "research_result": "NOT_EVALUATED",
        "source_actions": 0,
        "donor_forward_calls": 0,
        "source_count": len(sources),
        "unique_predictor_count": len(groups),
        "duplicates": sorted(duplicates),
        "sources": sources,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs="+", type=Path)
    parser.add_argument("--expected-blob", action="append", default=[],
                        metavar="PATH=GIT_SHA1")
    parser.add_argument("--require-distinct", action="store_true")
    args = parser.parse_args(argv)
    try:
        expected = {}
        for item in args.expected_blob:
            path, sep, sha1 = item.rpartition("=")
            if not sep or not re.fullmatch(r"[0-9a-f]{40}", sha1) or path in expected:
                raise SourceRejected("DWSA27_PIN_SYNTAX")
            expected[path] = sha1
        result = compare(args.archives, expected)
    except (SourceRejected, OSError) as exc:
        print("DWSA27_FAIL_CLOSED:" + str(exc), file=sys.stderr)
        return 3
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 2 if args.require_distinct and result["duplicates"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
