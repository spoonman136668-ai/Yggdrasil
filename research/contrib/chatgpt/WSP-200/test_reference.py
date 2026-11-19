"""WSP-205 independent fabricated-only pseudo/native alignment qualification."""
import unittest

from source_free_reference import (SyntheticAlignment, fasta_name_for_dataset,
                                   validate_fabricated_reference,
                                   PINNED_ALIGNED_FASTA_BLOB,
                                   PINNED_ORIGINAL_FASTA_BLOB)
from source_free_partition import SYNTHETIC_DIGEST

GENE = "FABRICATED_ALPHA"
OTHER = "FABRICATED_BETA"


def synthetic_row(name, pseudo, native, gene=GENE):
    return {"row_id": name, "gene": gene, "aa_genotype_pseudo": pseudo,
            "aa_genotype_native": native}


def fixture():
    # Pseudo positions: M0, gap1, S2, K3, gaps4/5, G6, E7.
    # Native positions: M0, S1, K2, G3, E4.
    ref = SyntheticAlignment.build(GENE, "M-SK--GE", "MSKGE")
    rows = [synthetic_row("wt", "wt", "wt"),
            synthetic_row("s1", "S2A", "S1A"),
            synthetic_row("s2", "G6V", "G3V"),
            synthetic_row("double", "S2A:G6V", "S1A:G3V")]
    return ref, rows


class ReferenceCoordinateTests(unittest.TestCase):
    def test_gap_mapping_and_reverse_native_index(self):
        ref, _ = fixture()
        self.assertEqual((0, None, 1, 2, None, None, 3, 4),
                         ref.pseudo_to_native)
        self.assertEqual("S1A:G3V", ref.translate("S2A:G6V"))
        self.assertEqual("G3V:S1A", "G3V:S1A")  # Order-independent labels checked below.
        self.assertEqual(6, ref.aligned_position(3))
        self.assertEqual(2, ref.aligned_position(1))
        self.assertEqual("wt", ref.translate("wt"))

    def test_coordinate_correct_structural_admission(self):
        ref, rows = fixture()
        manifest = validate_fabricated_reference(
            rows, {GENE: ref}, source_digest=SYNTHETIC_DIGEST)
        self.assertEqual(1, manifest.counts["eligible_double"])
        self.assertEqual(1, manifest.counts["source_free_groups"])
        rev = list(reversed(rows))
        self.assertEqual(manifest, validate_fabricated_reference(
            rev, {GENE: ref}, source_digest=SYNTHETIC_DIGEST))

    def test_native_label_wrong_offset_and_wrong_source_rejected(self):
        ref, rows = fixture()
        for bad_native in ("S2A:G6V", "G3V:S1C", "S1A:G4V", "", "wt"):
            changed = [dict(x) for x in rows]
            changed[-1]["aa_genotype_native"] = bad_native
            with self.subTest(native=bad_native), self.assertRaises(ValueError):
                validate_fabricated_reference(changed, {GENE: ref},
                                               source_digest=SYNTHETIC_DIGEST)
        for bad_pseudo in ("S1A:G6V", "X2A:G6V", "S2A:G4V", "S2A:G999V"):
            with self.subTest(pseudo=bad_pseudo), self.assertRaises(ValueError):
                ref.translate(bad_pseudo)

    def test_nonaligned_and_unknown_reference_fail_closed(self):
        for aligned, native in (("M-SK-VE", "MSKGE"), ("M-SK--GE", "MSKVE"),
                                ("M-SK--GE", "MSKGE*"), ("M-SK..GE", "MSKGE"),
                                ("", "MSKGE")):
            with self.subTest(aligned=aligned, native=native), self.assertRaises(ValueError):
                SyntheticAlignment.build(GENE, aligned, native)
        with self.assertRaises(ValueError):
            SyntheticAlignment.build("amacGFP", "M-SK--GE", "MSKGE")

    def test_second_background_distinct_gap_coordinates(self):
        ref, rows = fixture()
        ref2 = SyntheticAlignment.build(OTHER, "MS-KG-E", "MSKGE")
        other_rows = [synthetic_row("wt2", "wt", "wt", OTHER),
                      synthetic_row("o1", "S1A", "S1A", OTHER),
                      synthetic_row("o2", "G4V", "G3V", OTHER),
                      synthetic_row("od", "S1A:G4V", "S1A:G3V", OTHER)]
        self.assertEqual("G3V", ref2.translate("G4V"))
        manifest = validate_fabricated_reference(
            rows + other_rows, {GENE: ref, OTHER: ref2},
            source_digest=SYNTHETIC_DIGEST)
        self.assertEqual(2, manifest.counts["eligible_double"])
        with self.assertRaisesRegex(ValueError, "background set mismatch"):
            validate_fabricated_reference(rows + other_rows,
                                          {GENE: ref}, source_digest=SYNTHETIC_DIGEST)
        with self.assertRaisesRegex(ValueError, "synthetic-only"):
            validate_fabricated_reference(rows, {GENE: ref}, source_digest="0" * 64)

    def test_poison_outcomes_unread_and_no_original_fasta_payload(self):
        ref, rows = fixture()
        class Poison(dict):
            def __getitem__(self, name):
                if name in ("replicates_mean_brightness", "n_replicates", "total_cell_count"):
                    raise AssertionError("outcome field read")
                return super().__getitem__(name)
        poison = [Poison(x, replicates_mean_brightness=object(),
                         total_cell_count=object(), n_replicates=object()) for x in rows]
        manifest = validate_fabricated_reference(
            poison, {GENE: ref}, source_digest=SYNTHETIC_DIGEST)
        self.assertEqual(manifest.counts["eligible_double"], 1)
        self.assertEqual(len(PINNED_ALIGNED_FASTA_BLOB), 40)
        self.assertEqual(len(PINNED_ORIGINAL_FASTA_BLOB), 40)

    def test_pinned_dataset_alias_metadata_is_not_first_use(self):
        self.assertEqual("amacGFP", fasta_name_for_dataset("amacGFP"))
        self.assertEqual("cgreGFP", fasta_name_for_dataset("cgreGFP"))
        self.assertEqual("ppluGFP2", fasta_name_for_dataset("ppluGFP"))
        with self.assertRaises(ValueError):
            fasta_name_for_dataset("avGFP")
        with self.assertRaises(ValueError):
            fasta_name_for_dataset("FABRICATED_ALPHA")


if __name__ == "__main__":
    unittest.main()
