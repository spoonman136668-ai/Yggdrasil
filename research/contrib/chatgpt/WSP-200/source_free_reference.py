"""WSP-205: source-free aligned/pseudo/native coordinate mapping.

This module accepts ONLY caller-supplied FABRICATED_* reference sequences and
genotype metadata. It does not fetch original FASTA/CSV, inspect measurements,
or authorize use of the published GFP data. The pinned upstream references
are independently audited as read-only source metadata.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from learner import _address_parts
from source_free_partition import (AMINO_ACIDS, SYNTHETIC_DIGEST,
                                   StructuralManifest, admit_synthetic_genotypes,
                                   parse_genotype)

# Names/identity metadata only. No actual upstream sequence bytes bundled.
DATASET_TO_FASTA_NAME = {
    "amacGFP": "amacGFP",
    "cgreGFP": "cgreGFP",
    "ppluGFP": "ppluGFP2",
}
PINNED_ORIGINAL_FASTA_BLOB = "1b8f459eb35b400a6b8b3b3dd4e4f4b49cb6e382"
PINNED_ALIGNED_FASTA_BLOB = "5e20b6fa26a4a4fa66c9be258a17da45750b630e"


def fasta_name_for_dataset(name: str) -> str:
    """Metadata-only alias lookup. Does not permit actual GFP first use."""
    try:
        return DATASET_TO_FASTA_NAME[name]
    except KeyError as exc:
        raise ValueError("unrecognized real GFP name; no first-use adapter") from exc


@dataclass(frozen=True)
class SyntheticAlignment:
    gene: str
    aligned: str
    native: str
    pseudo_to_native: tuple[int | None, ...]

    @classmethod
    def build(cls, gene: str, aligned: str, native: str) -> SyntheticAlignment:
        if not isinstance(gene, str) or not gene.startswith("FABRICATED_"):
            raise ValueError("reference is not a fabricated background")
        if not isinstance(aligned, str) or not isinstance(native, str):
            raise ValueError("reference sequences must be literal strings")
        if not (1 <= len(native) <= 10000 and len(aligned) >= len(native)):
            raise ValueError("reference lengths invalid")
        if set(native) - AMINO_ACIDS or set(aligned) - (AMINO_ACIDS | {"-"}):
            raise ValueError("non-standard residue or alignment symbol")
        if aligned.replace("-", "") != native:
            raise ValueError("aligned reference does not collapse to native reference")
        positions = []
        idx = 0
        for residue in aligned:
            if residue == "-":
                positions.append(None)
            else:
                positions.append(idx)
                idx += 1
        if idx != len(native):
            raise ValueError("alignment index and reference disagree")
        return cls(gene, aligned, native, tuple(positions))

    def translate(self, pseudo_genotype: str) -> str:
        """Validate source residues and convert zero-based pseudo positions."""
        parsed = parse_genotype(pseudo_genotype)
        if parsed is None:
            raise ValueError("nonstandard pseudo mutation must be excluded")
        if not parsed:
            return "wt"
        result = []
        for source, pseudo_position, destination in parsed:
            if pseudo_position >= len(self.pseudo_to_native):
                raise ValueError("pseudo position beyond reference")
            native_position = self.pseudo_to_native[pseudo_position]
            if native_position is None:
                raise ValueError("pseudo mutation targets alignment gap")
            if self.aligned[pseudo_position] != source:
                raise ValueError("pseudo wildtype amino acid mismatch")
            if self.native[native_position] != source:
                raise ValueError("native reference amino acid mismatch")
            result.append((source, native_position, destination))
        return ":".join(f"{aa}{position}{dest}" for aa, position, dest in
                        sorted(result, key=lambda mutation: mutation[1]))

    def aligned_position(self, native_position: int) -> int:
        if not isinstance(native_position, int) or native_position < 0:
            raise ValueError("native position invalid")
        try:
            return self.pseudo_to_native.index(native_position)
        except ValueError as exc:
            raise ValueError("native position beyond reference") from exc


def validate_fabricated_reference(
    rows: Iterable[Mapping[str, object]],
    references: Mapping[str, SyntheticAlignment],
    *, source_digest: str,
) -> StructuralManifest:
    """Cross-check both genotype columns; touch no measured outcome fields."""
    if source_digest != SYNTHETIC_DIGEST:
        raise ValueError("reference validation is synthetic-only")
    records = list(rows)
    if not references:
        raise ValueError("missing fabricated references")
    genes = {row["gene"] for row in records}
    if genes != set(references) or any(not isinstance(g, str) or
                                      not g.startswith("FABRICATED_") for g in genes):
        raise ValueError("reference background set mismatch")
    for name, reference in references.items():
        if not isinstance(reference, SyntheticAlignment) or name != reference.gene:
            raise ValueError("reference identity mismatch")
        if SyntheticAlignment.build(name, reference.aligned, reference.native) != reference:
            raise ValueError("modified or corrupt alignment mapping")
    manifest = admit_synthetic_genotypes(records, source_digest=source_digest)
    for row in records:
        pseudo = row["aa_genotype_pseudo"]
        if parse_genotype(pseudo) is None:
            continue  # Explicitly excluded high-arity/stop mutants.
        expected = references[row["gene"]].translate(pseudo)
        native_label = row["aa_genotype_native"]
        if not isinstance(native_label, str) or parse_genotype(native_label) is None:
            raise ValueError("invalid native genotype metadata")
        if parse_genotype(expected) != parse_genotype(native_label):
            raise ValueError("pseudo/native genotype coordinate mismatch")
    return manifest
