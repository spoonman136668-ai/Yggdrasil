"""WSP-191: read-only Norman GSE133344 filtered-source byte admission.

This script never downloads data, trains a model, reads expression matrix values,
or opens a protected source. The digest manifest is an independently archived
third-party manifest, NOT a GEO publisher signature. Even PASS here is not
scientific source-first-use admission or a native Yggdrasil qualification.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "yggdrasil.wsp191.norman-filtered-byte-custody.v1"
SOURCE = "NCBI GEO GSE133344 / Norman et al. 2019"
THIRD_PARTY_MANIFEST = (
    "datasets-mila/datasets--perturbseq--perturbseq_2019"
    "@6cf272024e0bf47010880b2660a10f092e57752e/md5sums"
)
# Git blob of the archived manifest, not an original GEO signature.
MANIFEST_BLOB = "c12edbb4f4afd9ad0ff70fac7be9cca0a925e3d6"
FILE_SPEC = {
    "GSE133344_filtered_barcodes.tsv.gz": ("cd5ca4ace0399f6b1060f342f6051927", 10_000_000),
    "GSE133344_filtered_cell_identities.csv.gz": ("5011c6e2cafc61c46a60f6ad061f90c4", 10_000_000),
    "GSE133344_filtered_genes.tsv.gz": ("60729d19b3ace133d1ae1c5ecc99d86e", 10_000_000),
    "GSE133344_filtered_matrix.mtx.gz": ("afca755d856729ee2bac1a6e23bf67df", 3_000_000_000),
}
MAX_METADATA_EXPANDED = 250_000_000
MAX_LINE = 4_000_000


class AdmissionError(ValueError):
    """Source identity, size, format or time/order custody failed."""


def digest_file(path: Path, expected_md5: str, limit: int) -> dict:
    if path.is_symlink() or not path.is_file():
        raise AdmissionError(f"MISSING_OR_SYMLINK:{path.name}")
    original_stat = path.stat()
    n = original_stat.st_size
    if not 0 < n <= limit:
        raise AdmissionError(f"COMPRESSED_SIZE_LIMIT:{path.name}")
    md5, sha = hashlib.md5(), hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            md5.update(chunk)
            sha.update(chunk)
    final_stat = path.stat()
    if original_stat.st_size != final_stat.st_size or original_stat.st_mtime_ns != final_stat.st_mtime_ns:
        raise AdmissionError(f"SOURCE_DRIFT_DURING_HASH:{path.name}")
    if md5.hexdigest() != expected_md5:
        raise AdmissionError(f"ARCHIVED_MD5_MISMATCH:{path.name}")
    return {"compressed_bytes": n, "md5": md5.hexdigest(),
            "sha256": sha.hexdigest()}


def metadata_counts(path: Path, delimiter: str, has_header: bool) -> dict:
    """Counts metadata lines only; never returns cell IDs/guide or phenotype labels."""
    count, expanded, columns, header = 0, 0, None, None
    with gzip.open(path, "rb") as stream:
        for line in stream:
            expanded += len(line)
            if len(line) > MAX_LINE or expanded > MAX_METADATA_EXPANDED:
                raise AdmissionError(f"EXPANDED_METADATA_LIMIT:{path.name}")
            try:
                decoded = line.decode("utf-8-sig")
            except UnicodeError as exc:
                raise AdmissionError(f"NOT_UTF8:{path.name}") from exc
            # csv.reader is used for structural validation, not for saving data.
            fields = next(csv.reader([decoded], delimiter=delimiter))
            if columns is None:
                columns = len(fields)
                if columns == 0:
                    raise AdmissionError(f"EMPTY_COLUMNS:{path.name}")
                if has_header:
                    header = fields
                    if any(not col for col in header) or len(set(header)) != len(header):
                        raise AdmissionError(f"INVALID_HEADER:{path.name}")
                    continue
            if len(fields) != columns:
                raise AdmissionError(f"INVALID_COLUMN_COUNT:{path.name}")
            count += 1
    if not count:
        raise AdmissionError(f"NO_METADATA_ROWS:{path.name}")
    return {"metadata_rows": count, "column_count": columns, "header_present": has_header,
            "expanded_metadata_bytes": expanded}



def validate_cell_identity_join(root: Path) -> dict:
    """Validate public barcode-to-guide assignment metadata without reading outcomes.

    Filtered Cell Ranger barcodes are matrix column identities. The author's
    reader accepts cell BC/cell_BC/cell_barcode and joins guide identities on
    that key. No per-cell barcode or guide label is returned in the receipt.
    """
    barcode_path = root / "GSE133344_filtered_barcodes.tsv.gz"
    identity_path = root / "GSE133344_filtered_cell_identities.csv.gz"
    barcodes = set()
    with gzip.open(barcode_path, "rt", encoding="utf-8-sig", newline="") as stream:
        for line in stream:
            fields = next(csv.reader([line], delimiter="\t"))
            if len(fields) != 1 or not fields[0]:
                raise AdmissionError("BAD_BARCODE_COLUMN")
            barcode = fields[0]
            if barcode in barcodes:
                raise AdmissionError("DUPLICATE_MATRIX_BARCODE")
            barcodes.add(barcode)
    if not barcodes:
        raise AdmissionError("NO_MATRIX_BARCODES")

    with gzip.open(identity_path, "rt", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise AdmissionError("IDENTITY_HEADER_INVALID")
        aliases = ("cell_barcode", "cell_BC", "cell BC")
        chosen = [name for name in aliases if name in reader.fieldnames]
        if len(chosen) != 1 or "guide_identity" not in reader.fieldnames:
            raise AdmissionError("IDENTITY_KEYS_MISSING_OR_AMBIGUOUS")
        identity_key = chosen[0]
        matched = set()
        orphan = 0
        assigned = 0
        unassigned = 0
        count = 0
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise AdmissionError("MALFORMED_IDENTITY_ROW")
            barcode = row[identity_key]
            if not barcode:
                raise AdmissionError("EMPTY_IDENTITY_BARCODE")
            if barcode in matched:
                raise AdmissionError("DUPLICATE_IDENTITY_BARCODE")
            matched.add(barcode)
            count += 1
            if barcode not in barcodes:
                orphan += 1
            if row["guide_identity"] and row["guide_identity"] != "*":
                assigned += 1
            else:
                unassigned += 1
        if not count or not (matched & barcodes):
            raise AdmissionError("NO_JOINED_IDENTITIES")
        # Identity rows not present in the filtered matrix are not valid
        # supervision and may indicate a mismatched batch/source release.
        if orphan:
            raise AdmissionError("ORPHAN_IDENTITY_BARCODES")
        if not assigned:
            raise AdmissionError("NO_ASSIGNED_GUIDES")

    return {"matrix_barcodes": len(barcodes), "identity_rows": count,
            "joined_identity_rows": len(matched),
            "matrix_barcodes_without_identity": len(barcodes - matched),
            "assigned_guide_rows": assigned, "unassigned_guide_rows": unassigned,
            "guide_labels_exposed_in_receipt": False}


def matrix_dimensions(path: Path) -> dict:
    """Read ONLY MatrixMarket header+dimension tuple, never numeric entries."""
    with gzip.open(path, "rt", encoding="ascii") as stream:
        header = stream.readline(4096).strip()
        if not header.startswith("%%MatrixMarket matrix coordinate "):
            raise AdmissionError("INVALID_MTX_HEADER")
        for _ in range(64):
            line = stream.readline(4096)
            if not line:
                break
            if line.startswith("%"):
                continue
            fields = line.split()
            if len(fields) != 3 or not all(re.fullmatch(r"[0-9]+", x) for x in fields):
                raise AdmissionError("INVALID_MTX_DIMENSIONS")
            a, b, nnz = map(int, fields)
            if not (0 < a <= 150_000 and 0 < b <= 5_000_000 and 0 <= nnz <= a*b):
                raise AdmissionError("MTX_SHAPE_LIMIT")
            return {"genes": a, "cells": b, "nonzero_entries_declared": nnz,
                    "matrix_values_parsed": False}
    raise AdmissionError("MISSING_MTX_DIMENSIONS")


def verify(root: Path, spec: dict = FILE_SPEC) -> dict:
    if not root.is_dir() or root.is_symlink():
        raise AdmissionError("SOURCE_DIRECTORY_INVALID")
    # Freeze physical file identity during digest and metadata access: a
    # concurrent dataset replacement must not combine two source versions.
    def fingerprint(path):
        if path.is_symlink() or not path.is_file():
            raise AdmissionError(f"MISSING_OR_SYMLINK:{path.name}")
        stat = path.stat()
        return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
    fingerprints = {name: fingerprint(root / name) for name in spec}
    entries = {}
    # All four compressed files must match before opening any metadata stream.
    for name, (expected, limit) in spec.items():
        entries[name] = digest_file(root / name, expected, limit)
    for name in spec:
        if name.endswith("barcodes.tsv.gz") or name.endswith("genes.tsv.gz"):
            entries[name].update(metadata_counts(root / name, "\t", False))
        elif name.endswith("cell_identities.csv.gz"):
            entries[name].update(metadata_counts(root / name, ",", True))
    matrix_name = "GSE133344_filtered_matrix.mtx.gz"
    shape = matrix_dimensions(root / matrix_name)
    if entries["GSE133344_filtered_genes.tsv.gz"]["metadata_rows"] != shape["genes"]:
        raise AdmissionError("GENES_SHAPE_MISMATCH")
    if entries["GSE133344_filtered_barcodes.tsv.gz"]["metadata_rows"] != shape["cells"]:
        raise AdmissionError("BARCODES_SHAPE_MISMATCH")
    join = validate_cell_identity_join(root)
    if join["matrix_barcodes"] != shape["cells"]:
        raise AdmissionError("IDENTITY_MATRIX_SHAPE_MISMATCH")
    if join["identity_rows"] != entries["GSE133344_filtered_cell_identities.csv.gz"]["metadata_rows"]:
        raise AdmissionError("IDENTITY_METADATA_COUNT_DRIFT")
    if any(fingerprint(root / name) != fingerprints[name] for name in spec):
        raise AdmissionError("SOURCE_DRIFT_BETWEEN_HASH_AND_METADATA")
    return {"schema": SCHEMA, "source": SOURCE,
            "third_party_manifest": THIRD_PARTY_MANIFEST,
            "manifest_git_blob": MANIFEST_BLOB,
            "byte_digest_and_metadata_shape_gate": "PASS",
            "original_geo_publisher_signature_verified": False,
            "identity_to_barcode_join_verified": True,
            "identity_join": join,
            "gene_pair_cohort_admitted": False,
            "held_expression_labels_inspected": False,
            "training_performed": False,
            "protected_original_first_use_allowed": False,
            "matrix": shape, "files": entries}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True,
                        help="local folder with four original, unmodified filtered GEO .gz files")
    args = parser.parse_args(argv)
    try:
        receipt = verify(args.root)
    except (AdmissionError, OSError, EOFError, gzip.BadGzipFile, UnicodeError, csv.Error) as exc:
        print(json.dumps({"schema": SCHEMA, "byte_digest_and_metadata_shape_gate": "FAIL",
                          "reason": str(exc), "training_performed": False}, sort_keys=True))
        return 2
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
