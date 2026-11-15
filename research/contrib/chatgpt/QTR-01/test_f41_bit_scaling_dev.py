"""F41 frozen, source-free bit capacity and composition scaling tests."""
import json
import tempfile
import unittest
from pathlib import Path

from f26_semantic_association import NotAdmitted
from f34_direct_bitweights import DirectBitWeights
from f41_bit_scaling_dev import (
    CAPACITIES, ROOTS, POLICY, ScaledBitAssociations, get_protocol,
    frozen_graph, confusion, corrected_inventory, ERRATUM, measure,
)


class F41SourceFree(unittest.TestCase):
    def test_protocol_frozen_before_code_and_source(self):
        p = get_protocol()
        self.assertEqual(p["capacities_bits_high_to_low"], [8192, 4096, 2048, 1024, 512])
        self.assertEqual(p["source_parent_sha"], "5a6420f8af8c2cca33d1a443c3317bfe3e963303")
        self.assertEqual(p["status"], "FROZEN_BEFORE_F41_EXECUTABLE_OR_RESULT")
        self.assertEqual(p["source_frozen_component_baseline"]["triples"], 82)
        self.assertEqual(len(ROOTS), 10)

    def test_protocol_drift_rejected_even_with_identical_schema(self):
        with tempfile.TemporaryDirectory() as td:
            p = json.loads(POLICY.read_text(encoding="utf-8"))
            p["thresholds"]["twohop_precision_min"] = 0.0
            modified = Path(td) / "drift.json"
            modified.write_text(json.dumps(p), encoding="utf-8")
            with self.assertRaisesRegex(NotAdmitted, "FROZEN_PREREG_BLOB_MISMATCH"):
                get_protocol(modified)

    def test_source_inventory_erratum_preserves_original_thresholds(self):
        original = get_protocol()
        corrected = corrected_inventory()
        self.assertEqual(original["thresholds"]["minimum_candidate_vocab_charged_bytes"], 340)
        self.assertEqual(corrected["mechanical_findings"]["distinct_predicates"], 8)
        self.assertEqual(corrected["mechanical_findings"]["corrected_candidate_vocab_lower_bound_bytes"], 344)
        self.assertEqual(corrected["original_precision_threshold_min"], 0.95)
        self.assertEqual(corrected["original_false_positive_rate_threshold_max"], 0.01)
        with tempfile.TemporaryDirectory() as td:
            altered = json.loads(ERRATUM.read_text(encoding="utf-8"))
            altered["original_precision_threshold_min"] = 0.50
            filename = Path(td) / "invalid.json"
            filename.write_text(json.dumps(altered), encoding="utf-8")
            with self.assertRaisesRegex(NotAdmitted, "ERRATUM_BLOB_MISMATCH"):
                corrected_inventory(filename)

    def test_archived_sources_reuse_f40_evidence_only(self):
        first, second = frozen_graph()
        self.assertEqual((len(first), len(second)), (33, 49))
        self.assertEqual(len(set(first + second)), 82)

    def test_only_frozen_high_first_capacities_allowed(self):
        for wrong in (256, 65536, 0):
            with self.subTest(bits=wrong), self.assertRaisesRegex(NotAdmitted, "UNREGISTERED_BIT_CAPACITY"):
                ScaledBitAssociations(wrong)

    def test_blake2b_512_equivalent_to_original_f34(self):
        old, added = frozen_graph()
        first, second = ScaledBitAssociations(512), DirectBitWeights()
        for triple in old + added:
            self.assertEqual(first.slots(triple), second.slots(triple))
            first.program(triple)
            second.program(triple)
        self.assertEqual(first.snapshot(), second.snapshot())

    def test_snapshot_mutation_digest_fails_closed(self):
        m = ScaledBitAssociations(2048)
        m.program((42, 31, 5))
        snap = m.snapshot()
        bad = bytes([snap[0] ^ 1]) + snap[1:]
        with self.assertRaisesRegex(NotAdmitted, "SNAPSHOT_DIGEST_OR_SIZE"):
            ScaledBitAssociations(2048, bad, m.snapshot().hex())
        with self.assertRaisesRegex(NotAdmitted, "SNAPSHOT_DIGEST_OR_SIZE"):
            ScaledBitAssociations(2048, bad, __import__("hashlib").sha256(snap).hexdigest())

    def test_invalid_coordinate_rejected(self):
        m = ScaledBitAssociations(8192)
        for triple in ((0, 31, 42), (-1, 31, 42), (42, 31, 2**32),
                       (True, 31, 42), (42, "P31", 5), (42, 31)):
            with self.subTest(triple=triple), self.assertRaisesRegex(NotAdmitted, "INVALID_TRIPLE"):
                m.contains(triple)

    def test_source_free_cold_restore_and_addition_preserves_old(self):
        old, added = frozen_graph()
        for m in CAPACITIES:
            memory = ScaledBitAssociations(m)
            for triple in old:
                memory.program(triple)
            cold_initial = memory.restore()
            self.assertTrue(all(cold_initial.contains(x) for x in old))
            for triple in added:
                memory.program(triple)
            cold = memory.restore()
            self.assertEqual(cold.snapshot(), memory.snapshot())
            self.assertTrue(all(cold.contains(x) for x in old + added))

    def test_empty_unprogrammed_memory_cannot_invent_source(self):
        for n in CAPACITIES:
            m = ScaledBitAssociations(n)
            self.assertFalse(m.contains((42, 31, 5)))
            self.assertEqual(len(m.snapshot()), n//8)

    def test_confusion_is_exact_and_metrics_conservative(self):
        z = confusion({(1,), (2,), (4,)}, {(1,), (3,)}, 10)
        self.assertEqual((z["tp"], z["fp"], z["fn"], z["tn"]), (1, 2, 1, 6))
        self.assertAlmostEqual(z["precision"], 1/3)
        self.assertAlmostEqual(z["recall"], 1/2)
        self.assertAlmostEqual(z["false_positive_rate"], 1/4)

    def test_actual_frozen_high_first_development_screen(self):
        result = measure()
        self.assertEqual(result["source_triples"], 82)
        self.assertEqual(result["frozen_input_sizes"], [13, 20, 49])
        self.assertEqual(result["distinct_entities"], 78)
        self.assertEqual(result["distinct_predicates"], 8)
        self.assertEqual(result["exact_symbolic_raw_triplet_bytes"], 984)
        self.assertEqual(result["minimum_candidate_vocabulary_bytes"], 344)
        self.assertEqual(result["original_frozen_vocabulary_lower_bound_erroneous_bytes"], 340)
        self.assertEqual(result["capacities_tested_in_frozen_order"], list(CAPACITIES))
        self.assertEqual(len(result["capacity_results"]), 5)
        self.assertTrue(result["shuffled_endpoint_negative_changes_graph"])
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["native_recipient_weights_edited"])
        self.assertFalse(result["protected_first_use_consumed"])
        self.assertFalse(result["fully_trained_control_run"])
        for record in result["capacity_results"]:
            self.assertEqual(record["old_33_memberships_preserved"], 33)
            self.assertEqual(record["new_49_memberships_written"], 49)
            self.assertEqual(record["membership_true_positives"], 82)
            self.assertTrue(record["cold_query_parity"])
            self.assertEqual(record["twohop"]["fn"], 0)
        passed = [x for x in result["capacity_results"] if x["direct_bit_capacity_go"]]
        self.assertEqual(result["selected_smallest_passing_bits"],
                         min((x["bits"] for x in passed), default=None))
        self.assertEqual(result["classification"],
                         "DEV_CAPACITY_GO" if passed else "DEV_CAPACITY_NO_GO")


if __name__ == "__main__":
    unittest.main()
