"""WSP-197: read-only exact-byte source and genotype-metadata qualification.

NO expression, input count, output count, selection value or fitness calculation.
This checker does not fit weights, select cohorts or authorize first-use.
Requires original author Git blobs, not arbitrary download mirrors.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "yggdrasil.wsp197.olson-original-byte-admission.v1"
SPEC = {
    "Olson2014_TableS2_doubles.txt": (21721634, "dc7ab871b69026fc5d7cb2f505cfe7f6dd36b950"),
    "Olson2014_TableS2_singles.txt": (19302, "de650d218e3a2aa339fa14f2849060293daa0338"),
    "Olson2014_TableS2_wildtype.txt": (43, "f9fb047a2b25b0cde656f6d1760a89524b2bc665"),
    "GB1_sequence.fasta": (61, "c1d1deef50b769ccd6a8f7909aa6da66fada68d6"),
}
AA = frozenset("ACDEFGHIKLMNPQRSTVWY")
MAX_LINE = 50000


class SourceRejected(ValueError):
    pass


def fingerprint(path: Path):
    if path.is_symlink() or not path.is_file():
        raise SourceRejected("MISSING_OR_SYMLINK_" + path.name)
    stat = path.stat()
    return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)


def hash_original(path: Path, expected_size: int, expected_sha1: str):
    before = fingerprint(path)
    if before[2] != expected_size or expected_size > 30_000_000 or expected_size <= 0:
        raise SourceRejected("SOURCE_SIZE_MISMATCH_" + path.name)
    sha = hashlib.sha1()
    sha.update(f"blob {expected_size}\0".encode("ascii"))
    sha256 = hashlib.sha256()
    with path.open("rb") as fd:
        for block in iter(lambda: fd.read(1 << 20), b""):
            sha.update(block)
            sha256.update(block)
    if fingerprint(path) != before:
        raise SourceRejected("SOURCE_CHANGED_DURING_HASH_" + path.name)
    if sha.hexdigest() != expected_sha1:
        raise SourceRejected("SOURCE_GIT_BLOB_MISMATCH_" + path.name)
    return sha256.hexdigest(), before


def lines_metadata(path: Path):
    # Importantly, counts and fitness values are NOT converted to numbers.
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        while True:
            line = f.readline(MAX_LINE + 1)
            if not line:
                return
            if len(line) > MAX_LINE:
                raise SourceRejected("SOURCE_LINE_TOO_LONG_" + path.name)
            yield line.rstrip("\n\r").split("\t")


def reference_seq(path: Path):
    with path.open("r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    if len(lines) != 2 or lines[0] != ">GB1":
        raise SourceRejected("GB1_REFERENCE_FORMAT")
    seq = lines[1]
    if len(seq) != 56 or any(x not in AA for x in seq):
        raise SourceRejected("GB1_REFERENCE_INVALID")
    return seq


def metadata(root: Path, specs=SPEC):
    if root.is_symlink() or not root.is_dir():
        raise SourceRejected("INPUT_DIRECTORY_INVALID")
    receipts = {}
    fingerprints = {}
    # Verify ALL compressed/uncompressed bytes, before ANY genotype metadata access.
    for name, (size, sha) in specs.items():
        p = root / name
        d, stat = hash_original(p, size, sha)
        receipts[name] = {"size_bytes": size, "git_blob_sha1": sha, "independent_sha256": d}
        fingerprints[name] = stat

    ref = reference_seq(root / "GB1_sequence.fasta")
    single = set()
    doubles = set()
    count_single = 0
    count_double = 0
    positions = set()

    def check_allele(parts, offset):
        if len(parts) < offset + 3:
            raise SourceRejected("MISSING_MUTATION_FIELDS")
        wt, pos, alt = parts[offset:offset + 3]
        if not re.fullmatch(r"[1-9][0-9]*", pos):
            raise SourceRejected("INVALID_MUTATION_POSITION")
        site = int(pos)
        if site > len(ref) or wt != ref[site - 1]:
            raise SourceRejected("REFERENCE_ALLELE_MISMATCH")
        if len(alt) != 1 or alt not in AA or alt == wt:
            raise SourceRejected("INVALID_ALTERNATE_ALLELE")
        return site, alt

    rows = lines_metadata(root / "Olson2014_TableS2_singles.txt")
    head = next(rows, None)
    if not head or len(head) != 5 or head[:3] != ["WT amino acid", "Position", "Mutation"]:
        raise SourceRejected("SINGLES_HEADER_SCHEMA")
    for fields in rows:
        if len(fields) != len(head):
            raise SourceRejected("SINGLES_ROW_WIDTH")
        key = check_allele(fields, 0)
        if key in single:
            raise SourceRejected("DUPLICATE_SINGLE_GENOTYPE")
        single.add(key)
        positions.add(key[0])
        count_single += 1

    rows = lines_metadata(root / "Olson2014_TableS2_doubles.txt")
    head = next(rows, None)
    if not head or len(head) < 10 or len(head) > 18:
        raise SourceRejected("DOUBLES_HEADER_SCHEMA")
    for fields in rows:
        if len(fields) != len(head):
            raise SourceRejected("DOUBLES_ROW_WIDTH")
        k1 = check_allele(fields, 0)
        k2 = check_allele(fields, 3)
        if k1[0] == k2[0]:
            raise SourceRejected("SAME_SITE_DOUBLE")
        pair = tuple(sorted((k1, k2)))
        if pair in doubles:
            raise SourceRejected("DUPLICATE_DOUBLE_GENOTYPE")
        doubles.add(pair)
        positions.update((k1[0], k2[0]))
        count_double += 1

    # Inspect only the existence of WT metadata rows, not numeric count values.
    wild = list(lines_metadata(root / "Olson2014_TableS2_wildtype.txt"))
    if len(wild) != 2 or len(wild[0]) != 2 or len(wild[1]) != 2:
        raise SourceRejected("WILDTYPE_ROW_SCHEMA")
    if not single or not doubles:
        raise SourceRejected("EMPTY_EXPERIMENTAL_COHORT")
    for name in specs:
        if fingerprint(root / name) != fingerprints[name]:
            raise SourceRejected("SOURCE_DRIFT_AFTER_PARSING_" + name)

    return {
        "schema": SCHEMA, "byte_and_genotype_metadata_gate": "PASS",
        "source_repo": "lehner-lab/DMS2structure",
        "source_commit": "3c1976b78a743d4d4c73921f047648500e671c8e",
        "files": receipts, "single_genotypes": count_single,
        "double_genotypes": count_double,
        "unique_mutation_positions": len(positions),
        "reference_length": len(ref),
        "genotype_labels_in_receipt": False,
        "count_or_fitness_values_parsed": False,
        "real_source_first_use_authorized": False,
        "science_experiment_executed": False,
        "native_yggdrasil_trained": False,
        "scientific_pass": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True, type=Path)
    args = p.parse_args()
    try:
        receipt = metadata(args.root)
    except (OSError, UnicodeError, SourceRejected, StopIteration) as exc:
        print(json.dumps({"schema": SCHEMA,
                          "byte_and_genotype_metadata_gate": "FAIL",
                          "reason": str(exc), "science_experiment_executed": False}))
        return 2
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
