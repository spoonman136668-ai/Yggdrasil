#!/usr/bin/env python3
"""GKD-05: source-only admission for public, already-published Sachs interventions.

Preregistration FIRST: aafab21d6b8997ffafd355de528c9eb1cd7dfa0a.
This component does NOT read numerical observations or score any model.
Published historical (non-virgin) DEV; no protected Yggdrasil original-world action.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import pathlib
import urllib.request
import zipfile

URL = "https://zenodo.org/records/7681811/files/sachs.zip?download=1"
SOURCE_MD5 = "d50ccd7f88bb3705bcf6eda3978bcc41"
MAX_DOWNLOAD_BYTES = 1048576
MAX_UNCOMPRESSED_BYTES = 15000000
FIELDS = ("Raf", "Mek", "Plcg", "PIP2", "PIP3", "Erk", "Akt", "PKA", "PKC", "P38", "Jnk")
FIT = ("cd3cd28.csv", "cd3cd28icam2.csv", "cd3cd28_g0076.csv",
       "cd3cd28_psitect.csv", "pma.csv")
VALID = ("cd3cd28_aktinhib.csv", "cd3cd28_u0126.csv")
DEV = ("cd3cd28_ly.csv", "b2camp.csv")
SIM = ("cd3cd28icam2_aktinhib.csv", "cd3cd28icam2_g0076.csv",
       "cd3cd28icam2_psit.csv", "cd3cd28icam2_u0126.csv", "cd3cd28icam2_ly.csv")
REQUIRED = FIT + VALID + DEV + SIM + ("Ground_Truth.csv",)
EXPECTED = set(FIELDS)


def guard(condition: bool, label: str) -> None:
    if not condition:
        raise ValueError("GKD05_SOURCE_NO_GO:" + label)


def fetch_bounded(url: str = URL) -> bytes:
    guard(url == URL, "UNPINNED_URL")
    req = urllib.request.Request(url, headers={"User-Agent": "Yggdrasil-GKD05-readonly-public-research/1"})
    with urllib.request.urlopen(req, timeout=45) as response:
        raw = response.read(MAX_DOWNLOAD_BYTES + 1)
    guard(0 < len(raw) <= MAX_DOWNLOAD_BYTES, "ARCHIVE_SIZE")
    return raw


def admit_archive(raw: bytes, expected_md5: str | None = SOURCE_MD5) -> dict:
    guard(isinstance(raw, bytes) and 0 < len(raw) <= MAX_DOWNLOAD_BYTES, "ARCHIVE_BYTES")
    md5 = hashlib.md5(raw).hexdigest()
    if expected_md5 is not None:
        guard(md5 == expected_md5, "ARCHIVE_MD5")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        files = [f for f in archive.infolist() if not f.is_dir()]
        guard(len(files) <= 64, "ZIP_MEMBER_COUNT")
        guard(sum(f.file_size for f in files) <= MAX_UNCOMPRESSED_BYTES, "ZIP_DECOMPRESSION_LIMIT")
        basenames: dict[str, zipfile.ZipInfo] = {}
        for info in files:
            p = pathlib.PurePosixPath(info.filename)
            guard(not p.is_absolute() and ".." not in p.parts and not info.filename.startswith("\\"), "ZIP_PATH")
            basename = p.name
            guard(basename not in basenames, "DUPLICATE_BASENAME")
            basenames[basename] = info
        guard(set(REQUIRED).issubset(basenames), "REQUIRED_MEMBER_MISSING")
        records = {}
        for name in FIT + VALID + DEV:
            info = basenames[name]
            guard(info.file_size < 2000000, "CSV_TOO_BIG")
            payload = archive.read(info)
            guard(len(payload) == info.file_size, "CSV_SIZE")
            with io.StringIO(payload.decode("utf-8-sig"), newline="") as handle:
                rows = csv.reader(handle)
                header = next(rows, None)
                guard(header is not None and len(header) == 11
                      and len(set(header)) == 11 and set(header) == EXPECTED,
                      "CSV_COLUMN_SCHEMA:" + name)
                # Count historical source records; DO NOT parse, inspect, log or fit values.
                count = 0
                for row in rows:
                    guard(len(row) == 11, "ROW_WIDTH:" + name)
                    count += 1
                guard(707 <= count <= 927, "ROW_COUNT:" + name)
            records[name] = {
                "rows": count, "columns": tuple(header),
                "sha256": hashlib.sha256(payload).hexdigest(), "zip_member_bytes": len(payload)
            }
        guard(not (set(FIT + VALID + DEV) & set(SIM)), "SIMULATION_INCLUDED")
        return {
            "schema": "yggdrasil.gkd05.source-admission.v1",
            "status": "SOURCE_ADMISSION_PASS_NO_NUMERICAL_SCORE",
            "original_published_experiment_count": 9,
            "simulated_experiment_count_excluded": len(SIM),
            "archive_bytes": len(raw), "archive_md5": md5,
            "archive_sha256": hashlib.sha256(raw).hexdigest(),
            "published_doi": "10.5281/zenodo.7681811",
            "source_license_declared": "CC BY 4.0 (curator assertion)",
            "fit": {x: records[x] for x in FIT},
            "valid": {x: records[x] for x in VALID},
            "dev": {x: records[x] for x in DEV},
            "original_numeric_labels_read_for_scoring": False,
            "protected_original_world_queried": False
        }


def selftest() -> None:
    # Synthetic, not published source; verifies path, group roster, headers, counts.
    buff = io.BytesIO()
    data = ",".join(FIELDS) + "\n" + (",".join(["1"] * 11) + "\n") * 707
    with zipfile.ZipFile(buff, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in REQUIRED:
            archive.writestr("sachs/" + name, data if name in FIT + VALID + DEV else "fixture")
    raw = buff.getvalue()
    r = admit_archive(raw, expected_md5=None)
    guard(r["original_published_experiment_count"] == 9
          and r["simulated_experiment_count_excluded"] == 5
          and all(x["rows"] == 707 for group in ("fit", "valid", "dev")
                  for x in r[group].values()), "SELFTEST_POSITIVE")
    for payload, message in ((b"", "EMPTY"), (b"notzip", "BAD_ARCHIVE")):
        try:
            admit_archive(payload, expected_md5=None)
        except (ValueError, zipfile.BadZipFile):
            pass
        else:
            raise AssertionError("GKD05_SELFTEST_MISSING_NEGATIVE_" + message)
    print("GKD05_SOURCE_ADMISSION_SELFTEST_PASS 9 real / 5 excluded")


def main() -> None:
    args = argparse.ArgumentParser()
    args.add_argument("--selftest", action="store_true")
    args.add_argument("--admit-public", action="store_true")
    options = args.parse_args()
    guard(options.selftest != options.admit_public, "EXACTLY_ONE_MODE")
    if options.selftest:
        selftest()
    else:
        print("GKD05_PUBLIC_SOURCE_ACCESS_ONLY; no numerical evaluation")
        result = admit_archive(fetch_bounded())
        print("GKD05_SOURCE_ADMISSION_V1=" + json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
