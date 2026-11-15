"""F35 frozen witnessed-original-revision source graph and 2-hop negatives."""
import json
import unittest

from f26_semantic_association import NotAdmitted, digest
from f35_pinned_depth2 import (
    SOURCE, SOURCE_DIGEST, PINNED, SCHEMA, preflight, original_snapshot,
    check_pinned, extract_new_edges, source_label_cache, missing_object_queries,
    complete_new_labels, twohop_analysis,
)


def entity(qid, rev=2567832181, qualified=False, wrong=False):
    return {
        "id": qid, "lastrevid": rev,
        "labels": {"en": {"language": "en", "value": "Original first-party name"}},
        "claims": {
            "P279": [{
                "id": ("Q99" if wrong else qid) + "$fixture-evidence",
                "rank": "normal",
                "mainsnak": {"snaktype": "value",
                             "datavalue": {"value":
                                           {"entity-type": "item", "id": "Q111"}}},
                **({"qualifiers": {"P580": []}} if qualified else {})
            }]
        },
    }


class F35(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = SOURCE.read_bytes()
        cls.snapshot = original_snapshot(cls.raw)

    def test_frozen_original_source_and_selection_exact(self):
        p = preflight()
        self.assertEqual(p["schema"], SCHEMA)
        self.assertEqual(len(PINNED), 5)
        self.assertEqual(p["existing_source_sha256"], SOURCE_DIGEST)
        self.assertEqual(len(self.snapshot["typed_source_rows"]), 13)
        self.assertEqual(self.snapshot["matched_symbolic_numeric_control"]["actual_observed_twohop_queries"], 0)

    def test_source_byte_changed_fails_and_pinned_source_revision_fails(self):
        with self.assertRaises(NotAdmitted):
            original_snapshot(self.raw + b" ")
        ent = entity("Q36180")
        expected = digest(ent)
        check_pinned("Q36180", ent, expected, 2567832181, expected)
        for revision, sha in ((2567832182, expected), (2567832181, "0"*64)):
            with self.assertRaises(NotAdmitted):
                check_pinned("Q36180", ent, sha, revision, expected)

    def test_original_first_party_archive_labels_preserved(self):
        names, props = source_label_cache(self.snapshot)
        self.assertEqual(names["Q36180"], ("writer", "en"))
        self.assertEqual(names["Q42"][1], "ar")
        self.assertEqual(props["P279"], ("subclass of", "en"))
        self.assertIn("Q215627", names)

    def test_pre_registered_source_edges_only_and_qualifiers_excluded(self):
        expanded = {
            qid: entity(qid, rev, qualified=qid == "Q154954")
            for qid, rev, _ in PINNED
        }
        raw, counts = extract_new_edges(expanded)
        self.assertEqual(len(raw), 4)
        self.assertGreater(counts["excluded_unqualified_or_invalid"], 0)
        expanded["Q36180"] = entity("Q36180", PINNED[0][1], wrong=True)
        filtered, _ = extract_new_edges(expanded)
        self.assertEqual(len(filtered), 3)

    def test_genuine_join_only_with_new_source_witness(self):
        orig = self.snapshot["typed_source_rows"]
        new = [{
            "s": "Q36180", "p": "P279", "o": "Q111",
            "s_label": "writer", "s_language": "en",
            "p_label": "subclass of", "p_language": "en",
            "o_label": "source object", "o_language": "en",
            "source_claim": "Q36180$fixture-evidence",
            "source_revision": PINNED[0][1],
        }]
        before = twohop_analysis(orig, [])
        self.assertEqual(before["real_twohop_queries"], 0)
        after = twohop_analysis(orig, new)
        self.assertGreaterEqual(after["real_twohop_queries"], 1)
        self.assertTrue(any(p["source"] == "Q42" and p["intermediate"] == "Q36180"
                            and p["result"] == "Q111" for p in after["depth_two_paths"]))
        self.assertTrue(after["canonical_numeric_cold_restore"])
        self.assertTrue(after["matched_exact_source_symbolic_parity"])
        self.assertFalse(after["scientific_pass"])

    def test_new_endpoint_budget_deterministic_and_not_invented(self):
        original, props = source_label_cache(self.snapshot)
        raws = [
            {"s": "Q36180", "p": "P279", "o": "Q900"},
            {"s": "Q36180", "p": "P31", "o": "Q80"},
            {"s": "Q36180", "p": "P279", "o": "Q15"},
        ]
        selected = missing_object_queries(raws, original, {})
        self.assertEqual(selected, ["Q15", "Q80", "Q900"])
        complete = [{
            "s": "Q36180", "p": "P279", "o": "Q111",
            "source_claim": "Q36180$1", "source_revision": PINNED[0][1],
        }]
        # Object with no first-party label is NOT a semantic claim.
        accepted, excluded = complete_new_labels(complete, original, props, {})
        self.assertEqual((len(accepted), excluded), (0, 1))


if __name__ == "__main__":
    unittest.main()
