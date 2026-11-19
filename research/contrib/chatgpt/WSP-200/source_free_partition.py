"""WSP-204 synthetic-only genotype-partition guard; never reads brightness fields.

This is NOT the licensed/source-authorized GFP adapter. It accepts caller-owned
FABRICATED_* records and a synthetic sentinel digest only. No file I/O, network,
measurement parsing, native protein inference or outcome access is implemented.
The frozen WSP-200 preregistration remains the source of scientific authority.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Mapping
import re

from learner import fit_stage, group_bucket, pair_group

SYNTHETIC_DIGEST = "f" * 64
AMINO_ACIDS = frozenset("ACDEFGHIKLMNPQRSTVWY")
MUTATION = re.compile(r"([ACDEFGHIKLMNPQRSTVWY])(0|[1-9][0-9]*)([ACDEFGHIKLMNPQRSTVWY])\Z")


@dataclass(frozen=True)
class EligibleDouble:
    """An identity-only receipt; intentionally contains no outcome values."""

    row_id: str
    gene: str
    group: str
    parent_ids: tuple[str, str]
    bucket: str
    stage: int | None
    mutations: tuple[tuple[str, int, str], tuple[str, int, str]]


@dataclass(frozen=True)
class StructuralManifest:
    eligible: tuple[EligibleDouble, ...]
    counts: dict[str, int]
    groups_per_bucket: dict[str, int]
    # No original genotype rows, numeric outcomes, WT/single labels, or held labels.


def parse_genotype(pseudo: str) -> tuple[tuple[str, int, str], ...] | None:
    """Return strictly standard-AA mutations; None means structural exclusion.

    WT is literal wt; higher arities/nonstandard/stop symbols are excluded.
    Duplicate/reordered site identities are rejected, not silently repaired.
    """
    if pseudo == "wt":
        return ()
    if not isinstance(pseudo, str) or not pseudo:
        return None
    chunks = pseudo.split(":")
    if not 1 <= len(chunks) <= 2:
        return None
    out = []
    for chunk in chunks:
        match = MUTATION.fullmatch(chunk)
        if match is None or match[1] == match[3]:
            return None
        out.append((match[1], int(match[2]), match[3]))
    if len({mutation[1] for mutation in out}) != len(out):
        raise ValueError("two substitutions target the same native site")
    return tuple(sorted(out, key=lambda m: m[1]))


def admit_synthetic_genotypes(
    rows: Iterable[Mapping[str, object]], *, source_digest: str
) -> StructuralManifest:
    """Admit *only fabricated genotype identities* without touching measurements.

    Required structural fields: row_id, gene, aa_genotype_pseudo,
    aa_genotype_native. The last is checked for presence only: native
    identity equivalence with original reference sequences still needs an
    independently qualified source adapter before any original-data first use.
    """
    if source_digest != SYNTHETIC_DIGEST:
        raise ValueError("synthetic-only source digest fence")
    by_gene: dict[str, dict[tuple[tuple[str, int, str], ...], str]] = {}
    raw_doubles: list[tuple[str, str, tuple[tuple[str, int, str], ...]]] = []
    counts: Counter[str] = Counter()
    row_ids: set[str] = set()
    wildtypes: set[str] = set()
    source_amino: dict[tuple[str, int], str] = {}
    for row in rows:
        # Never enumerate row keys, inspect values not listed here, access a
        # target column, or deserialize the source measurements.
        rid = row["row_id"]
        gene = row["gene"]
        pseudo = row["aa_genotype_pseudo"]
        native = row["aa_genotype_native"]
        if not isinstance(rid, str) or not rid or rid in row_ids:
            raise ValueError("duplicate or invalid row receipt")
        row_ids.add(rid)
        if not isinstance(gene, str) or not gene.startswith("FABRICATED_"):
            raise ValueError("source is not demonstrably synthetic")
        if not isinstance(native, str) or not native:
            raise ValueError("native identity metadata missing")
        parsed = parse_genotype(pseudo)
        counts["observed_rows"] += 1
        if parsed is None:
            counts["excluded_nonstandard_or_higharity"] += 1
            continue
        per_gene = by_gene.setdefault(gene, {})
        if parsed in per_gene:
            raise ValueError("duplicate canonical genotype identity")
        per_gene[parsed] = rid
        for original, position, _ in parsed:
            key = (gene, position)
            if key in source_amino and source_amino[key] != original:
                raise ValueError("conflicting native reference identity")
            source_amino[key] = original
        if not parsed:
            wildtypes.add(gene)
            counts["wildtype"] += 1
        elif len(parsed) == 1:
            counts["single"] += 1
        else:
            counts["strict_double"] += 1
            raw_doubles.append((rid, gene, parsed))
    if not by_gene or wildtypes != set(by_gene):
        raise ValueError("missing exactly one wildtype per synthetic background")

    admitted: list[EligibleDouble] = []
    groups: dict[str, set[str]] = {}
    for rid, gene, (a, b) in raw_doubles:
        parents = by_gene[gene]
        if (a,) not in parents or (b,) not in parents:
            counts["excluded_missing_parent"] += 1
            continue
        group = pair_group(gene, a[1], b[1])
        bucket = group_bucket(group)
        stage = fit_stage(group) if bucket == "FIT" else None
        admitted.append(EligibleDouble(rid, gene, group,
                                       (parents[(a,)], parents[(b,)]),
                                       bucket, stage, (a, b)))
        groups.setdefault(bucket, set()).add(group)
        counts["eligible_double"] += 1
    admitted.sort(key=lambda e: (e.gene, e.group, e.mutations, e.row_id))
    counts["source_free_groups"] = sum(len(g) for g in groups.values())
    return StructuralManifest(tuple(admitted), dict(sorted(counts.items())),
                              {k: len(groups.get(k, set())) for k in
                               ("FIT", "VALID", "PUBLIC_DEV", "RESERVED_UNTOUCHED")})
