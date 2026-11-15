"""QTR F34 direct bit programming against first-party CC0 facts and strong exact source."""
import unittest
from f26_semantic_association import NotAdmitted
from f34_direct_bitweights import (
    BYTES, DirectBitWeights, load_triples, measurement, parse_source,
    preflight, SOURCE,
)


class F34(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_triples()

    def test_source_and_frozen_protocol(self):
        p = preflight()
        self.assertEqual(p["source_rows"], 13)
        self.assertEqual(p["source_integer_triplet_bytes"], 156)
        self.assertEqual(len(self.rows), 13)

    def test_exact_first_party_source_custody_rejects_edits(self):
        raw = SOURCE.read_bytes()
        self.assertEqual(parse_source(raw), self.rows)
        with self.assertRaises(NotAdmitted):
            parse_source(raw.replace(b'"scientific_pass":false', b'"scientific_pass":true'))
        with self.assertRaises(NotAdmitted):
            parse_source(raw + b" ")

    def test_binary_program_and_byte_exact_cold(self):
        x = DirectBitWeights()
        for triple in self.rows:
            x.program(triple)
        self.assertEqual(len(x.snapshot()), BYTES)
        cold = DirectBitWeights(x.snapshot())
        self.assertTrue(all(cold.contains(t) for t in self.rows))
        self.assertEqual(cold.snapshot(), x.snapshot())
        with self.assertRaises(NotAdmitted):
            DirectBitWeights(x.snapshot()[:-1])

    def test_finite_domain_exact_source_control_and_negative(self):
        m = measurement(self.rows)
        self.assertEqual(m["source_positive_triples"], 13)
        self.assertEqual(m["exact_sparse_control_triplet_bytes"], 156)
        self.assertEqual(m["direct_programmed_weight_payload_bytes"], 64)
        self.assertEqual(m["false_negatives"], 0)
        self.assertLessEqual(m["false_positive_rate"], 0.01)
        self.assertLess(m["shuffled_control_original_hits"], 13)
        self.assertTrue(m["exact_cold_snapshot_and_query_parity"])
        self.assertFalse(m["scientific_pass"])

    def test_frozen_only_real_source_membership_and_no_generalization_claim(self):
        m = measurement(self.rows)
        self.assertEqual(m["hashes_per_membership"], 3)
        self.assertFalse(m["source_has_real_composable_twohop_queries"])
        self.assertFalse(m["can_enumerate_objects_or_delete_fact"])
        self.assertFalse(m["neural_recipient_weights_edited"])
        self.assertTrue(m["old_source_membership_preserved_after_synthetic_additions"])

    def test_invalid_numeric_candidate_fails_closed(self):
        for triple in ((0, 31, 5), (42, 31, -1), (42, "P31", 5),
                       (42, 31), (True, 31, 5), [42, 31, 5]):
            with self.subTest(triple=triple):
                with self.assertRaises(NotAdmitted):
                    DirectBitWeights().contains(triple)


if __name__ == "__main__":
    unittest.main()
