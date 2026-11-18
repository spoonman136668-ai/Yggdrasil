"""WSP185: read-only published physical CSV roster probe; no model training.

No model import, no source intervention, no sensor value analysis. Reads only
CSV headers, counts records, checks record shape and cryptographic integrity.
Physical source: juangamella/causal-chamber wt_walks_v1 (CC BY 4.0).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import zipfile

UPSTREAM_MD5 = "19bb4e92cbe0b8dff49299b9b509ac36"
SCHEMA = "yggdrasil.wsp185.public-physical-roster-meta.v1"
LIMIT_ZIP_BYTES = 450_000_000
LIMIT_MEMBER_BYTES = 250_000_000
LIMIT_UNCOMPRESSED_BYTES = 950_000_000
REQUIRED = frozenset(("flag", "load_in", "load_out", "hatch", "pot_1",
                       "pot_2", "rpm_in", "pressure_intake"))
REQUESTED = tuple([f"actuators_random_walk_{k}" for k in range(1, 11)]
                  + ["regime_jumps_single"])


def roster_entry(archive: zipfile.ZipFile, info: zipfile.ZipInfo) -> dict:
    if info.file_size > LIMIT_MEMBER_BYTES:
        raise ValueError("WSP185_MEMBER_BUDGET")
    digest = hashlib.sha256()
    # First pass fingerprints the physical source bytes, without parsing
    # any measured numeric sensor values.
    with archive.open(info, "r") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    # Second pass reads only row boundaries/shape. No numeric values returned,
    # cached, scored, or passed to any learning procedure.
    with archive.open(info, "r") as raw:
        txt = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
        reader = csv.reader(txt)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError("WSP185_EMPTY_CSV") from exc
        if len(header) != len(set(header)) or not header:
            raise ValueError("WSP185_INVALID_COLUMNS")
        count = empty = malformed = 0
        for row in reader:
            if not row:
                empty += 1
            else:
                count += 1
                malformed += int(len(row) != len(header))
    return {
        "file_sha256": digest.hexdigest(),
        "physical_record_count": count,
        "empty_csv_records": empty,
        "wrong_width_records": malformed,
        "field_count": len(header),
        "header_fields": header,
        "required_fields_present": sorted(REQUIRED.intersection(header)),
        "required_fields_missing": sorted(REQUIRED.difference(header)),
        "preregistered_count_10000_matches": count == 10000,
    }


def inspect(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size > LIMIT_ZIP_BYTES:
        raise ValueError("WSP185_ZIP_BUDGET")
    blob = path.read_bytes()
    md5 = hashlib.md5(blob).hexdigest()  # Author's published ZIP fingerprint
    if md5 != UPSTREAM_MD5:
        raise ValueError("WSP185_UPSTREAM_HASH_MISMATCH")
    requested = set(REQUESTED)
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        members = {}
        uncompressed = 0
        for info in archive.infolist():
            name = PurePosixPath(info.filename)
            if name.is_absolute() or ".." in name.parts:
                raise ValueError("WSP185_ZIP_PATH")
            uncompressed += info.file_size
            if uncompressed > LIMIT_UNCOMPRESSED_BYTES:
                raise ValueError("WSP185_ARCHIVE_UNCOMPRESSED_LIMIT")
            if info.is_dir() or name.stem not in requested:
                continue
            if name.suffix.lower() != ".csv" or name.stem in members:
                raise ValueError("WSP185_SOURCE_ROSTER_COLLISION")
            members[name.stem] = info
        if set(members) != requested:
            raise ValueError("WSP185_MISSING_REQUIRED_SOURCE_RUN")
        details = {name: roster_entry(archive, members[name])
                   for name in REQUESTED}
    return {
        "schema": SCHEMA,
        "archive_md5_published": md5,
        "archive_sha256": hashlib.sha256(blob).hexdigest(),
        "source_repository_commit": "juangamella/causal-chamber@967d59a42956872f37463cc561ecf6e9ceab9364",
        "dataset": "wt_walks_v1",
        "source_data_license": "CC BY 4.0; Gamella, Peters, Buehlmann (2025)",
        "metadata_only": True,
        "source_owner_first_use_allowed": False,
        "original_world_actions_this_probe": 0,
        "model_training_calls": 0,
        "scientific_pass": False,
        "notes": "Counts and schema only. No output values or model performance inspected.",
        "per_source_file": details,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.archive)
    print("WSP185_PUBLIC_ROSTER_METADATA=" + json.dumps(
        result, sort_keys=True, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main()
