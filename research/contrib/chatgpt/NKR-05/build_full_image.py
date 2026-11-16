"""NKR-05: produce complete native Q/P/Q factual image from sealed TRAIN only.

Never opens valid/test member contents, original protected science or accepted
Yggdrasil state. Historical source is already consumed; not new first-use.
Enforces pinned WSP-102/103 source identities without importing unmerged research modules.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import heapq
import json
from pathlib import Path
import struct
import sys
import tarfile
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
# Frozen WSP102/103 historical source contract. Those experimental modules
# reside on separate *unmerged* research branches, so importing them as native
# runtime dependencies would be unsound. Retain their exact frozen constants
# and enforce the already-published checks here without any other dependency.
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ARCHIVE_SHA = "ccda8bbcd3cf599b30dd3fd8979ac26e59b48fc53d23128882a044bfbb67f878"
ARCHIVE_BYTES = 174515774
TRAIN_SHA = "2ef1a279f6393a8edfbb2b44114a2c97944272e5fe2a1bd2a7cbe48f94742f1a"
TRAIN_BYTES = 436189882
TRAIN_ROWS = 21343681
TRAIN_RELATIONS = 828
SOURCE_URL = "https://web.informatik.uni-mannheim.de/pi1/kge-datasets/wikidata5m.tar.gz"
SOURCE_HOST = "web.informatik.uni-mannheim.de"
MAX_ARCHIVE_BYTES = 268435456
MAX_ARCHIVE_DOWNLOAD_SECONDS = 600


def _positive_id(value, prefix):
    if (not value.startswith(prefix) or len(value) < 2
            or not value[1:].isdigit() or value[1:2] == b"0"):
        raise ValueError("NKR05_INVALID_QP_IDENTIFIER")
    result = int(value[1:])
    if not (0 < result <= 0xFFFFFFFF):
        raise ValueError("NKR05_INVALID_QP_UINT32_RANGE")
    return result


def parse_triple(row):
    if not row.endswith(bytes((10,))) or len(row) > 10000 or bytes((0,)) in row:
        raise ValueError("NKR05_INVALID_TRIPLE_LINE")
    pieces = row.rstrip(bytes((13, 10))).split(bytes((9,)))
    if len(pieces) != 3:
        raise ValueError("NKR05_INVALID_TRIPLE_COLUMNS")
    return (_positive_id(pieces[0], b"Q"), _positive_id(pieces[1], b"P"),
            _positive_id(pieces[2], b"Q"))


def _allowed_url(url):
    p = urlsplit(url)
    if (p.scheme != "https" or p.hostname != SOURCE_HOST
            or p.username is not None or p.password is not None
            or p.query or p.fragment or p.port not in (None, 443)
            or p.path != "/pi1/kge-datasets/wikidata5m.tar.gz"):
        raise ValueError("NKR05_HISTORICAL_HOST_DISALLOWED")
    return url


class _OnlyFrozenRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        _allowed_url(newurl)
        return super().redirect_request(request, fp, code, msg, headers, newurl)


def _download_once(destination):
    _allowed_url(SOURCE_URL)
    opener = build_opener(_OnlyFrozenRedirects())
    request = Request(SOURCE_URL, headers={
        "User-Agent": "NKR05-Historical-Train/1.0 (Yggdrasil research)",
        "Accept": "application/gzip,application/octet-stream",
    })
    started = time.monotonic()
    downloaded, checksum = 0, sha256()
    with opener.open(request, timeout=35) as response:
        _allowed_url(response.geturl())
        if response.status != 200 or "text/html" in response.headers.get(
                "Content-Type", "").lower():
            raise ValueError("NKR05_SOURCE_NOT_GZIP")
        with open(destination, "xb") as sink:
            while True:
                if time.monotonic() - started > MAX_ARCHIVE_DOWNLOAD_SECONDS:
                    raise TimeoutError("NKR05_DOWNLOAD_TIME_BUDGET")
                chunk = response.read(1 << 20)
                if not chunk:
                    break
                downloaded += len(chunk)
                if downloaded > MAX_ARCHIVE_BYTES:
                    raise MemoryError("NKR05_ARCHIVE_DOWNLOAD_TOO_LARGE")
                sink.write(chunk)
                checksum.update(chunk)
    return {"compressed_sha256": checksum.hexdigest(),
            "compressed_bytes": downloaded}


def inspect_members(path):
    members, seen = [], set()
    with tarfile.open(path, "r:gz") as archive:
        for member in archive:
            name = member.name
            if (len(members) >= 16 or not name or name in seen
                    or len(name) > 256 or name.startswith("/")
                    or chr(92) in name or chr(0) in name
                    or any(part in ("", ".", "..") for part in name.split("/"))
                    or not (member.isdir() or member.isfile())):
                raise ValueError("NKR05_UNSAFE_ARCHIVE_MEMBER")
            seen.add(name)
            if member.size < 0 or member.size > TRAIN_BYTES:
                raise ValueError("NKR05_ARCHIVE_MEMBER_SIZE_INVALID")
            members.append({"path": name,
                            "type": "directory" if member.isdir() else "file",
                            "uncompressed_bytes": member.size})
    return {"members": members}

from yggdrasil.native_factual_weights import (
    PACK, SCHEMA, NativeFactualWeights, canonical, digest,
)

# This is a consumed historical TRAIN source, not benchmark validation/test.
EXPECTED_MEMBERS = {
    ("wikidata5m", "directory", 0),
    ("wikidata5m/train.txt", "file", TRAIN_BYTES),
    ("wikidata5m/valid.txt", "file", 109498),
    ("wikidata5m/test.txt", "file", 108932),
}
CHUNK_ROWS = 500_000
MAX_SECONDS = 1500
MAX_SOURCE_BYTES = TRAIN_BYTES
MAX_SORTED_BYTES = TRAIN_ROWS * PACK.size
MAX_RUNS = 64


def _run(path, records):
    """One sorted binary run, bounded in memory by fixed chunk length."""
    records.sort()
    with open(path, "wb") as sink:
        buffer = bytearray()
        for s, p, o in records:
            buffer.extend(PACK.pack(s, p, o))
            if len(buffer) >= 1 << 20:
                sink.write(buffer)
                buffer.clear()
        if buffer:
            sink.write(buffer)


def _iter_run(path):
    with open(path, "rb", buffering=1 << 20) as source:
        while True:
            raw = source.read(PACK.size)
            if not raw:
                return
            if len(raw) != PACK.size:
                raise ValueError("NKR05_TORN_SORT_RUN")
            yield PACK.unpack(raw)


def compile_train_stream(handle, output_dir, *,
                         expected_rows=TRAIN_ROWS,
                         expected_bytes=TRAIN_BYTES,
                         expected_sha=TRAIN_SHA,
                         expected_relations=TRAIN_RELATIONS,
                         archive_sha=ARCHIVE_SHA,
                         chunk_rows=CHUNK_ROWS,
                         max_seconds=MAX_SECONDS):
    """Stream *all* original TRAIN rows into sorted, mmap-queryable full weights.

    Output remains incomplete/unpublished until every source count/hash, sorted
    source row, cold restore, and manifest receipt has passed. The original
    source order is not assumed sorted; an external sort uses bounded RAM.
    """
    if (type(chunk_rows) is not int or not 1 <= chunk_rows <= CHUNK_ROWS
            or type(expected_rows) is not int or not 1 <= expected_rows <= TRAIN_ROWS
            or type(expected_bytes) is not int or not 1 <= expected_bytes <= TRAIN_BYTES
            or type(expected_relations) is not int or not 1 <= expected_relations <= TRAIN_RELATIONS
            or type(max_seconds) not in (int, float) or max_seconds <= 0
            or type(expected_sha) is not str or len(expected_sha) != 64):
        raise ValueError("NKR05_SOURCE_BOUND_INVALID")
    started = time.monotonic()
    out = Path(output_dir)
    if (out / "facts.uint32le").exists() or (out / "manifest.json").exists():
        raise ValueError("NKR05_REFUSE_OVERWRITE")
    out.mkdir(parents=True, exist_ok=True)
    source_sha = sha256()
    source_bytes = 0
    row_count = 0
    predicates = set()
    with tempfile.TemporaryDirectory(prefix="nkr05-runs-", dir=out) as tmp:
        runs = []
        chunk = []
        for raw in handle:
            if row_count % 16384 == 0 and time.monotonic() - started > max_seconds:
                raise TimeoutError("NKR05_FULL_SOURCE_TIME_BUDGET")
            row_count += 1
            source_bytes += len(raw)
            if row_count > expected_rows or source_bytes > expected_bytes:
                raise ValueError("NKR05_FULL_TRAIN_INVENTORY_OVERFLOW")
            triple = parse_triple(raw)
            predicates.add(triple[1])
            source_sha.update(raw)
            chunk.append(triple)
            if len(chunk) == chunk_rows:
                name = Path(tmp) / f"run-{len(runs):03d}.bin"
                if len(runs) >= MAX_RUNS:
                    raise MemoryError("NKR05_EXTERNAL_RUN_LIMIT")
                _run(name, chunk)
                runs.append(name)
                chunk.clear()
        if chunk:
            name = Path(tmp) / f"run-{len(runs):03d}.bin"
            if len(runs) >= MAX_RUNS:
                raise MemoryError("NKR05_EXTERNAL_RUN_LIMIT")
            _run(name, chunk)
            runs.append(name)
            chunk.clear()
        if (row_count != expected_rows or source_bytes != expected_bytes
                or source_sha.hexdigest() != expected_sha
                or len(predicates) != expected_relations):
            raise ValueError("NKR05_FROZEN_TRAIN_SHA_COUNT_OR_BREADTH_DRIFT")
        image_tmp = out / "facts.staged.partial"
        packed_sha = sha256()
        written = 0
        duplicates = 0
        previous = None
        first, last = None, None
        with open(image_tmp, "xb") as sink:
            buffer = bytearray()
            for row in heapq.merge(*[_iter_run(r) for r in runs]):
                if written % 16384 == 0 and time.monotonic() - started > max_seconds:
                    raise TimeoutError("NKR05_SORT_TIME_BUDGET")
                if previous is not None:
                    if row < previous:
                        raise AssertionError("NKR05_SORTED_INVERSION")
                    duplicates += int(row == previous)
                if first is None:
                    first = row
                previous = row
                last = row
                binary = PACK.pack(*row)
                buffer.extend(binary)
                written += 1
                if len(buffer) >= 1 << 20:
                    sink.write(buffer)
                    packed_sha.update(buffer)
                    buffer.clear()
            if buffer:
                sink.write(buffer)
                packed_sha.update(buffer)
        if written != expected_rows or image_tmp.stat().st_size != expected_rows * PACK.size:
            raise ValueError("NKR05_FULL_IMAGE_INVENTORY_DRIFT")
        if image_tmp.stat().st_size > MAX_SORTED_BYTES:
            raise MemoryError("NKR05_FULL_IMAGE_SIZE_LIMIT")
        manifest = {
            "schema": SCHEMA,
            "data_kind": "historical-train-only-QPQ",
            "source_label": "noncanonical-historical-Wikidata5M-WSP102",
            "source_archive_sha256": archive_sha,
            "source_train_sha256": expected_sha,
            "source_bytes": source_bytes,
            "records": written,
            "numeric_bytes": written * PACK.size,
            "total_uint32_weight_slots": written * 3,
            "distinct_relation_types": len(predicates),
            "duplicate_source_rows_retained": duplicates,
            "packed_sha256": packed_sha.hexdigest(),
            "sorted_lexicographically": True,
            "first_triple": list(first),
            "last_triple": list(last),
            "cold_restore_required": True,
            "original_valid_test_read": False,
            "historical_queries_previously_consumed": True,
            "source_authenticity": "EXACT_HISTORICAL_SOURCE_BYTES_ONLY",
            "scientific_pass": False,
            "accepted_native": False,
        }
        # Write complete immutable image only after the final row passed.
        final_image = out / "facts.uint32le"
        image_tmp.replace(final_image)
        meta = canonical(manifest)
        (out / "manifest.json").write_bytes(meta)
    manifest_pin = digest(meta)
    with NativeFactualWeights(final_image, out / "manifest.json", manifest_pin) as cold:
        if len(cold) != expected_rows or cold.row_at(0) != first or cold.row_at(
                expected_rows - 1) != last:
            raise AssertionError("NKR05_COLD_MANIFEST_INDEX_DRIFT")
        if not cold.has_fact(*first) or not cold.has_fact(*last):
            raise AssertionError("NKR05_COLD_FACT_ABSENT")
    receipt = {
        "schema": "yggdrasil.nkr05.full-native-knowledge-receipt.v1",
        "classification": "FULL_HISTORICAL_TRAIN_FACTUAL_IMAGE_STAGED",
        "records": written,
        "relations": len(predicates),
        "numeric_bytes": written * PACK.size,
        "numeric_slots": written * 3,
        "duplicates_retained": duplicates,
        "manifest_sha256": manifest_pin,
        "packed_sha256": packed_sha.hexdigest(),
        "source_train_sha256": expected_sha,
        "source_archive_sha256": archive_sha,
        "full_source_cold_restore": True,
        "official_valid_test_opened": False,
        "scientific_pass": False,
        "native_accepted": False,
        "wall_seconds": time.monotonic() - started,
    }
    (out / "receipt.json").write_bytes(canonical(receipt))
    return receipt


def materialize_historical_train(output_dir):
    """Single historical source request: custody, TRAIN-only parse, full image."""
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="nkr05-source-") as d:
        archive_path = Path(d) / "historical-wikidata5m.tar.gz"
        evidence = _download_once(archive_path)
        if (evidence["compressed_sha256"] != ARCHIVE_SHA
                or evidence["compressed_bytes"] != ARCHIVE_BYTES):
            raise ValueError("NKR05_ARCHIVE_PROVENANCE_DRIFT")
        inventory = inspect_members(archive_path)
        actual = {(m["path"], m["type"], m["uncompressed_bytes"])
                  for m in inventory["members"]}
        if actual != EXPECTED_MEMBERS:
            raise ValueError("NKR05_ARCHIVE_MEMBER_INVENTORY_DRIFT")
        with tarfile.open(archive_path, "r:gz") as archive:
            # Deliberately never opens valid.txt, test.txt or other source labels.
            member = archive.getmember("wikidata5m/train.txt")
            source = archive.extractfile(member)
            if source is None or member.size != TRAIN_BYTES:
                raise ValueError("NKR05_MISSING_TRAIN_MEMBER")
            with source:
                receipt = compile_train_stream(source, output_dir)
        receipt["full_process_wall_seconds"] = time.monotonic() - start
    print("NKR05_FULL_NATIVE_FACTS=" + json.dumps(
        receipt, sort_keys=True, separators=(",", ":")), flush=True)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--historical-train-only-full-image",
                        action="store_true", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    materialize_historical_train(args.output)
