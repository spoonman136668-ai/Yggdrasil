#!/usr/bin/env python3
"""Read-only verification of original ENERGY evidence ZIPs; no scientific qualification."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

def verify(root: Path, allow_incomplete: bool = False) -> tuple[int, dict]:
    custody = json.loads((root / "custody.json").read_text(encoding="utf-8"))
    records = custody["zip_archives"]
    summary = {"verified": [], "missing": [], "invalid": [], "total_expected": len(records)}
    for item in records:
        file = root / "original-zips" / item["filename"]
        if not file.is_file():
            summary["missing"].append(item["filename"])
            continue
        actual_size = file.stat().st_size
        actual_sha = hashlib.sha256(file.read_bytes()).hexdigest()
        reasons = []
        if actual_size != item["byte_size"]:
            reasons.append("size mismatch")
        if actual_sha != item["sha256"]:
            reasons.append("SHA-256 mismatch")
        try:
            with zipfile.ZipFile(file) as z:
                bad = z.testzip()
                entries = sum(not member.is_dir() for member in z.infolist())
                if bad is not None:
                    reasons.append("CRC failure")
                if entries != item["member_count"]:
                    reasons.append("member count mismatch")
        except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
            reasons.append(type(exc).__name__)
        if reasons:
            summary["invalid"].append({"filename": item["filename"], "errors": reasons})
        else:
            summary["verified"].append(item["filename"])
    summary["status"] = (
        "PASS_COMPLETE" if not summary["missing"] and not summary["invalid"]
        else "PASS_PARTIAL" if allow_incomplete and not summary["invalid"]
        else "FAIL_INCOMPLETE_OR_INVALID"
    )
    good = not summary["invalid"] and (allow_incomplete or not summary["missing"])
    return (0 if good else 1), summary

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=HERE)
    p.add_argument("--allow-incomplete", action="store_true",
                   help="Diagnostic only: missing files remain unqualified")
    args = p.parse_args()
    code, result = verify(args.root, args.allow_incomplete)
    print(json.dumps(result, indent=2))
    return code

if __name__ == "__main__":
    sys.exit(main())
