"""F40 exact archived source graph isolation and historical science-first-use fence."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from f40_component_isolation_audit import (
    NotAdmitted, PREREG, HERE, RESERVED, FIT,
    preregistration, read_archives, validate, build_components, audit
)


class F40(unittest.TestCase):
    def test_frozen_audit_scope_and_historical_provenance_limit(self):
        p = preregistration()
        self.assertEqual(len(p["source_archives"]), 3)
        self.assertEqual([v["expected_rows"] for v in p["source_archives"]], [13, 20, 49])
        self.assertIs(p["known_historical_boundary"]["legacy_consumed_source_ledger_complete"], False)
        self.assertEqual(p["reserved_evaluation_root_ids"], list(RESERVED))
        self.assertEqual(len(FIT), 8)

    def test_unannounced_policy_relaxation_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p = json.loads(PREREG.read_text(encoding="utf-8"))
            p["known_historical_boundary"]["legacy_consumed_source_ledger_complete"] = True
            path = Path(td) / "modified-policy.json"
            path.write_text(json.dumps(p), encoding="utf-8")
            with self.assertRaisesRegex(NotAdmitted, "FIRST_USE_POLICY_DRIFT"):
                preregistration(path)

    def test_mutated_exact_archive_bytes_are_rejected(self):
        originals = [HERE / "evidence" / k for k in (
            "f32_source_snapshot.json",
            "f35_source_depth2_snapshot.json",
            "f39_fit_breadth_source_snapshot.json",
        )]
        for i in range(3):
            with self.subTest(source_index=i), tempfile.TemporaryDirectory() as td:
                changed = Path(td) / "mutated"
                changed.write_bytes(originals[i].read_bytes() + b" ")
                paths = list(originals)
                paths[i] = changed
                with self.assertRaisesRegex(NotAdmitted, "SOURCE_HASH_MISMATCH"):
                    read_archives(paths)

    def test_real_archive_graph_isolation_and_no_global_science(self):
        r = audit()
        self.assertEqual(r["source_row_counts"], [13, 20, 49])
        self.assertEqual(r["distinct_triples"], 82)
        self.assertEqual(r["distinct_entities"], 78)
        self.assertEqual(r["distinct_subject_entities"], 26)
        self.assertEqual(r["local_graph_components"], 7)
        self.assertEqual(r["local_fit_root_independent_components"], 7)
        self.assertEqual(r["reserved_root_archived_appearance_count"], 0)
        self.assertEqual(r["f39_prior_exact_triple_overlap"], 0)
        self.assertEqual(len(r["f39_prior_entity_identity_overlap_qids"]), 4)
        self.assertIs(r["scientific_pass"], False)
        self.assertIs(r["global_historical_first_use_certified"], False)
        self.assertIs(r["science_source_admitted_for_first_use"], False)
        self.assertIs(r["protected_scientific_first_use_consumed"], False)
        self.assertEqual(r["new_source_requests"], 0)

    def test_reserved_entity_as_row_is_detected(self):
        d = deepcopy(read_archives())
        d[2]["witnessed_rows"][0]["o"] = RESERVED[0]
        with self.assertRaisesRegex(NotAdmitted, "RESERVED_HELDOUT_ID_APPEARS_IN_GRAPH"):
            validate(d)

    def test_reserved_entity_as_request_receipt_is_detected(self):
        d = deepcopy(read_archives())
        d[2]["source_receipts"][0]["entity"] = RESERVED[1]
        with self.assertRaisesRegex(NotAdmitted, "RESERVED_ROOT_REQUEST_RECEIPT_FOUND"):
            validate(d)

    def test_source_revision_must_match_original_receipt(self):
        d = deepcopy(read_archives())
        d[1]["added_witnessed_source_rows"][0]["source_revision"] += 1
        with self.assertRaisesRegex(NotAdmitted, "SOURCE_CLAIM_REVISION_UNWITNESSED"):
            validate(d)

    def test_lost_original_label_language_is_not_admitted(self):
        d = deepcopy(read_archives())
        d[0]["typed_source_rows"][0]["o_language"] = ""
        with self.assertRaisesRegex(NotAdmitted, "LANGUAGE_OR_LABEL_MISSING"):
            validate(d)

    def test_duplicate_source_statement_is_not_counted_twice(self):
        d = deepcopy(read_archives())
        d[2]["witnessed_rows"][-1] = deepcopy(d[2]["witnessed_rows"][0])
        with self.assertRaisesRegex(NotAdmitted, "DUPLICATE_OR_CROSS_ARCHIVE_TRIPLE"):
            validate(d)

    def test_fit_roots_q30_and_q95_share_a_component(self):
        r = audit()
        mapping = r["fit_root_component_anchors"]
        self.assertEqual(mapping["Q30"], mapping["Q95"])
        self.assertEqual(len(set(mapping.values())), 7)
        self.assertEqual(len(mapping), 8)

    def test_all_seven_shadow_component_folds_are_node_disjoint(self):
        r = audit()
        folds = r["component_rehearsal_folds"]
        self.assertEqual(len(folds), 7)
        self.assertEqual(sum(f["entity_count"] for f in folds), 78)
        self.assertEqual(sum(f["source_triples_in_fold"] for f in folds), 82)
        for fold in folds:
            self.assertTrue(fold["component_strictly_disjoint"])
            self.assertEqual(fold["source_triples_in_fold"] +
                             fold["other_source_triples"], 82)
        self.assertTrue(r["local_development_folds_only_not_protected_science"])

    def test_graph_components_detect_cross_component_leakage(self):
        d = read_archives()
        _, triples, _ = validate(d)
        mapping, components = build_components(triples)
        self.assertNotEqual(mapping["Q30"], mapping["Q90"])
        extension = triples + [("Q30", "P31", "Q90")]
        new_mapping, new_components = build_components(extension)
        self.assertEqual(len(new_components), len(components) - 1)
        self.assertEqual(new_mapping["Q30"], new_mapping["Q90"])

    def test_archived_receipts_are_separate_from_science_eligibility(self):
        r = audit()
        self.assertTrue(r["r182_known_incomplete_historical_source_ledger"])
        self.assertEqual(
            r["classification"],
            "LOCAL_ARCHIVE_ISOLATION_PASS_GLOBAL_FIRST_USE_UNVERIFIED"
        )
        self.assertFalse(r["fully_trained_conventional_or_native_baseline_compared"])
        self.assertFalse(r["native_model_weights_edited"])


if __name__ == "__main__":
    unittest.main()
