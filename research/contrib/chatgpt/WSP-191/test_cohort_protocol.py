"""Source-free metadata-only engineering tests (not scientific experiments)."""
import unittest
import cohort_protocol as c
from source_admission import AdmissionError


class CohortProtocolTests(unittest.TestCase):
    def test_author_double_underscore_and_gene_pair(self):
        self.assertEqual(c.parse_assignment("B_A__ACTG"), ("PAIR", ("A", "B")))
        self.assertEqual(c.parse_assignment("A_B__TTTT"), ("PAIR", ("A", "B")))

    def test_controls_and_singles(self):
        self.assertEqual(c.parse_assignment("NegCtrl0_NegCtrl1"), ("CONTROL", ()))
        self.assertEqual(c.parse_assignment("NegCtrl0_A__sg"), ("SINGLE", ("A",)))
        self.assertEqual(c.parse_assignment("B_NegCtrl0"), ("SINGLE", ("B",)))
        self.assertEqual(c.parse_assignment("*"), ("UNASSIGNED", ()))

    def test_author_rhoxf2_correction(self):
        self.assertEqual(c.parse_assignment("RHOXF2_NegCtrl0"), ("SINGLE", ("RHOXF2B",)))

    def test_unknown_labels_fail_closed(self):
        with self.assertRaisesRegex(AdmissionError, "UNSUPPORTED_GUIDE_IDENTITY_FORMAT"):
            c.parse_assignment("A_B_C")
        with self.assertRaisesRegex(AdmissionError, "UNSUPPORTED_GUIDE_IDENTITY_FORMAT"):
            c.parse_assignment("A,B")
        with self.assertRaisesRegex(AdmissionError, "SELF_PAIR_NOT_NEW_TARGET"):
            c.parse_assignment("A_A")

    def test_stable_order_independent_pair_splits(self):
        pairs = [tuple(sorted((f"G{i}", f"G{j}"))) for i in range(15) for j in range(i+1, 15)]
        s = set(sum(([a,b] for a,b in pairs), []))
        t1 = c.summarize_eligible(set(pairs), s)
        t2 = c.summarize_eligible(set(reversed(pairs)), s)
        self.assertEqual(t1, t2)
        self.assertEqual(t1["eligible_pair_groups"], 105)
        self.assertEqual(sum(t1["group_counts"].values()), 105)
        self.assertFalse(t1["raw_labels_emitted"])

    def test_missing_single_parent_excluded_before_split(self):
        singles = {f"G{i}" for i in range(15)}
        pairs = {tuple(sorted((f"G{i}", f"G{j}"))) for i in range(15) for j in range(i+1, 15)}
        pairs.add(("G0", "ZZZ"))
        result = c.summarize_eligible(pairs, singles)
        self.assertEqual(result["missing_single_parent_groups"], 1)
        self.assertEqual(result["eligible_pair_groups"], 105)

    def test_too_few_pairs_fails_no_rebalancing(self):
        with self.assertRaisesRegex(AdmissionError, "INSUFFICIENT_DISJOINT_"):
            c.summarize_eligible({("A", "B")}, {"A", "B"})

    def _fixture_for_metadata_analyze(self, root, reverse=False):
        import gzip
        import hashlib
        from pathlib import Path
        records = [f"G{i}_NegCtrl0__guide" for i in range(15)]
        records += [f"G{i}_G{j}__guide" for i in range(15) for j in range(i + 1, 15)]
        if reverse:
            records.reverse()
        contents = "cell_BC,guide_identity\n" + "".join(f"C{k},{name}\n" for k, name in enumerate(records))
        data = gzip.compress(contents.encode(), mtime=0)
        name = "GSE133344_filtered_cell_identities.csv.gz"
        (root / name).write_bytes(data)
        sha = hashlib.sha256(data).hexdigest()
        receipt = {"byte_digest_and_metadata_shape_gate": "PASS",
                   "identity_to_barcode_join_verified": True,
                   "files": {name: {"sha256": sha, "metadata_rows": len(records)}}}
        return name, sha, receipt

    def test_full_metadata_cohort_path_has_no_raw_guide_labels(self):
        import json
        import tempfile
        from pathlib import Path
        from unittest import mock
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            name, sha, receipt = self._fixture_for_metadata_analyze(root)
            with mock.patch.object(c, "verify", return_value=receipt), \
                 mock.patch.object(c, "digest_file", return_value={"sha256": sha}), \
                 mock.patch.dict(c.FILE_SPEC, {name: ("dummy_md5", 100000)}, clear=True):
                result = c.analyze(root)
            self.assertEqual(result["cohort_metadata_gate"], "PASS")
            self.assertEqual(result["pair_groups"], 105)
            self.assertEqual(result["single_parent_groups"], 15)
            self.assertFalse(result["numeric_expression_values_read"])
            self.assertFalse(result["test_pair_labels_exposed"])
            self.assertNotIn("G0_G1", json.dumps(result))

    def test_metadata_source_change_after_digest_fails_closed(self):
        import tempfile
        from pathlib import Path
        from unittest import mock
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            name, _, receipt = self._fixture_for_metadata_analyze(root)
            with mock.patch.object(c, "verify", return_value=receipt), \
                 mock.patch.object(c, "digest_file", return_value={"sha256": "invalid"}), \
                 mock.patch.dict(c.FILE_SPEC, {name: ("dummy_md5", 100000)}, clear=True):
                with self.assertRaisesRegex(AdmissionError, "IDENTITY_BYTES_DRIFT_AFTER_SOURCE_GATE"):
                    c.analyze(root)

    def test_no_verified_source_stops_before_metadata_open(self):
        from unittest import mock
        with mock.patch.object(c, "verify", return_value={
             "byte_digest_and_metadata_shape_gate": "FAIL",
             "identity_to_barcode_join_verified": False}):
            with self.assertRaisesRegex(AdmissionError, "SOURCE_NOT_BYTE_ADMITTED"):
                c.analyze("nonexistent-source-root")

    def test_invalid_canonical_input(self):
        with self.assertRaisesRegex(AdmissionError, "INVALID_CANONICAL_PAIR"):
            c.split_pair(("B", "A"))


if __name__ == "__main__":
    unittest.main()
