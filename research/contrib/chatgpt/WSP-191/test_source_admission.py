"""Source-free engineering tests. Fixtures are NOT scientific evaluation worlds."""
from __future__ import annotations

import gzip
import hashlib
import tempfile
import unittest
from pathlib import Path

import source_admission as s


class SourceAdmissionTests(unittest.TestCase):
    def fixture(self, root):
        blobs = {
            "GSE133344_filtered_genes.tsv.gz": gzip.compress(b"G1\tGene1\nG2\tGene2\n", mtime=0),
            "GSE133344_filtered_barcodes.tsv.gz": gzip.compress(b"B1\nB2\n", mtime=0),
            "GSE133344_filtered_cell_identities.csv.gz": gzip.compress(b"cell_BC,guide_identity\nB1,GUIDE_A\nB2,GUIDE_B\n", mtime=0),
            "GSE133344_filtered_matrix.mtx.gz": gzip.compress(
                b"%%MatrixMarket matrix coordinate integer general\n% metadata-only\n2 2 1\n1 2 42\n", mtime=0),
        }
        spec = {}
        for name, blob in blobs.items():
            (root / name).write_bytes(blob)
            spec[name] = (hashlib.md5(blob).hexdigest(), 20_000)
        return spec

    def test_matching_bytes_does_not_claim_science_or_admission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = self.fixture(root)
            result = s.verify(root, spec)
            self.assertEqual(result["byte_digest_and_metadata_shape_gate"], "PASS")
            self.assertTrue(result["identity_to_barcode_join_verified"])
            self.assertEqual(result["identity_join"]["joined_identity_rows"], 2)
            self.assertFalse(result["identity_join"]["guide_labels_exposed_in_receipt"])
            self.assertFalse(result["gene_pair_cohort_admitted"])
            self.assertFalse(result["training_performed"])
            self.assertFalse(result["protected_original_first_use_allowed"])
            self.assertFalse(result["matrix"]["matrix_values_parsed"])

    def test_corrupt_byte_fails_closed_before_decompression(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = self.fixture(root)
            target = root / "GSE133344_filtered_matrix.mtx.gz"
            target.write_bytes(target.read_bytes() + b"corruption")
            with self.assertRaisesRegex(s.AdmissionError, "ARCHIVED_MD5_MISMATCH"):
                s.verify(root, spec)

    def test_missing_and_symlink_not_admitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = self.fixture(root)
            missing = root / "GSE133344_filtered_barcodes.tsv.gz"
            missing.unlink()
            with self.assertRaisesRegex(s.AdmissionError, "MISSING_OR_SYMLINK"):
                s.verify(root, spec)

    def test_mismatched_gene_dimension_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = self.fixture(root)
            target = root / "GSE133344_filtered_genes.tsv.gz"
            blob = gzip.compress(b"G1\tGene1\n", mtime=0)
            target.write_bytes(blob)
            spec[target.name] = (hashlib.md5(blob).hexdigest(), 20_000)
            with self.assertRaisesRegex(s.AdmissionError, "GENES_SHAPE_MISMATCH"):
                s.verify(root, spec)

    def test_invalid_matrix_header_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = self.fixture(root)
            target = root / "GSE133344_filtered_matrix.mtx.gz"
            blob = gzip.compress(b"NOT MATRIX\n2 2 1\n", mtime=0)
            target.write_bytes(blob)
            spec[target.name] = (hashlib.md5(blob).hexdigest(), 20_000)
            with self.assertRaisesRegex(s.AdmissionError, "INVALID_MTX_HEADER"):
                s.verify(root, spec)

    def _replace_identities(self, root, spec, data):
        name = "GSE133344_filtered_cell_identities.csv.gz"
        blob = gzip.compress(data, mtime=0)
        (root / name).write_bytes(blob)
        spec[name] = (hashlib.md5(blob).hexdigest(), 20_000)

    def test_orphan_cell_identity_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = self.fixture(root)
            self._replace_identities(root, spec,
                                     b"cell_barcode,guide_identity\nB1,GUIDE_A\nB3,GUIDE_C\n")
            with self.assertRaisesRegex(s.AdmissionError, "ORPHAN_IDENTITY_BARCODES"):
                s.verify(root, spec)

    def test_duplicate_matrix_barcode_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = self.fixture(root)
            name = "GSE133344_filtered_barcodes.tsv.gz"
            blob = gzip.compress(b"B1\nB1\n", mtime=0)
            (root / name).write_bytes(blob)
            spec[name] = (hashlib.md5(blob).hexdigest(), 20_000)
            with self.assertRaisesRegex(s.AdmissionError, "DUPLICATE_MATRIX_BARCODE"):
                s.verify(root, spec)

    def test_duplicate_identity_barcode_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = self.fixture(root)
            self._replace_identities(root, spec,
                                     b"cell BC,guide_identity\nB1,GUIDE_A\nB1,GUIDE_B\n")
            with self.assertRaisesRegex(s.AdmissionError, "DUPLICATE_IDENTITY_BARCODE"):
                s.verify(root, spec)

    def test_ambiguous_join_columns_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = self.fixture(root)
            self._replace_identities(root, spec,
                                     b"cell_BC,cell_barcode,guide_identity\nB1,B1,GUIDE_A\nB2,B2,GUIDE_B\n")
            with self.assertRaisesRegex(s.AdmissionError, "IDENTITY_KEYS_MISSING_OR_AMBIGUOUS"):
                s.verify(root, spec)

    def test_partial_identity_coverage_is_reported_not_fabricated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = self.fixture(root)
            self._replace_identities(root, spec,
                                     b"cell_barcode,guide_identity\nB1,GUIDE_A\n")
            result = s.verify(root, spec)
            self.assertTrue(result["identity_to_barcode_join_verified"])
            self.assertEqual(result["identity_join"]["matrix_barcodes_without_identity"], 1)
            self.assertFalse(result["gene_pair_cohort_admitted"])

    def test_no_assigned_guides_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = self.fixture(root)
            self._replace_identities(root, spec,
                                     b"cell_BC,guide_identity\nB1,*\nB2,*\n")
            with self.assertRaisesRegex(s.AdmissionError, "NO_ASSIGNED_GUIDES"):
                s.verify(root, spec)

    def test_oversize_compressed_file_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = self.fixture(root)
            name = "GSE133344_filtered_genes.tsv.gz"
            md5, _ = spec[name]
            spec[name] = (md5, 2)
            with self.assertRaisesRegex(s.AdmissionError, "COMPRESSED_SIZE_LIMIT"):
                s.verify(root, spec)


if __name__ == "__main__":
    unittest.main()
