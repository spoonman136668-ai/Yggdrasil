#!/usr/bin/env python3
"""Read-only byte-identity verification of original ENERGY-04..18 ZIP evidence."""
from __future__ import annotations
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILENAME = "ENERGY-04-18-complete-original-evidence.zip"
EXPECTED_SHA256 = "21970d5c8b2b809ea6cc0f87359e13f4fc1aa09cad2679e44ee533dd681de09a"
EXPECTED_BYTES = 1131498

def check():
    raw = (HERE / FILENAME).read_bytes()
    if len(raw) != EXPECTED_BYTES or hashlib.sha256(raw).hexdigest() != EXPECTED_SHA256:
        raise ValueError("combined archive byte count or SHA-256 mismatch")
    custody = json.loads((HERE / "custody.json").read_text(encoding="utf-8"))
    expected = {x["filename"]: x for x in custody["zip_archives"]}
    if len(expected) != 15:
        raise ValueError("custody must contain 15 original packages")
    with zipfile.ZipFile(io.BytesIO(raw)) as outer:
        if outer.testzip() is not None:
            raise ValueError("combined ZIP CRC check failed")
        manifest = json.loads(outer.read("MANIFEST.json"))
        packages = manifest["original_packages"]
        if manifest["gate_count"] != 15 or len(packages) != 15:
            raise ValueError("combined manifest count mismatch")
        expected_paths = {"README.md", "MANIFEST.json"} | {x["path"] for x in packages}
        actual_paths = {x.filename for x in outer.infolist() if not x.is_dir()}
        if actual_paths != expected_paths:
            raise ValueError("unexpected or missing members in combined archive")
        for package in packages:
            name = package["name"]
            path = "original-zips/" + name
            if package["path"] != path or name not in expected:
                raise ValueError("unknown nested package: " + name)
            data = outer.read(path)
            if len(data) != package["bytes"] or hashlib.sha256(data).hexdigest() != package["sha256"]:
                raise ValueError("original ZIP size/hash mismatch: " + name)
            with zipfile.ZipFile(io.BytesIO(data)) as nested:
                if nested.testzip() is not None:
                    raise ValueError("original ZIP CRC failure: " + name)
                n = sum(not m.is_dir() for m in nested.infolist())
            rec = expected[name]
            if (rec["sha256"],rec["byte_size"],rec["member_count"]) != (package["sha256"],package["bytes"],n):
                raise ValueError("custody disagreement: " + name)
    if {x["name"] for x in packages} != set(expected):
        raise ValueError("original archive inventory is incomplete")
    return {"status":"PASS_ORIGINAL_15_OF_15","combined_sha256":EXPECTED_SHA256,"combined_bytes":EXPECTED_BYTES,"nested_originals":15,"nested_crc":"PASS","scientific_acceptance":"NOT_PERFORMED"}

if __name__ == "__main__":
    try:
        print(json.dumps(check(), indent=2))
    except Exception as exc:
        print(json.dumps({"status":"FAIL","error":str(exc)}))
        sys.exit(1)
