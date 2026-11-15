"""F38 frozen source and two-hop composition, negative-control tests."""
import json
import tempfile
import unittest
from pathlib import Path

from f26_semantic_association import NotAdmitted
from f34_direct_bitweights import DirectBitWeights
from f38_composition_dev import (
    ROOTS, OLD, NEW, POLICY, verified_sources, exact_source_paths,
    exact_answer_set, bit_answer_set, shuffled_control, evaluate
)


class F38(unittest.TestCase):
    def test_original_and_extension_exact_source_sha(self):
        _, old, added = verified_sources()
        self.assertEqual((len(old), len(added)), (13, 20))
        self.assertEqual(len(exact_source_paths(old)), 0)
        self.assertEqual(len(exact_source_paths(old+added)), 20)

    def test_source_archive_byte_change_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"altered.json"
            path.write_bytes(NEW.read_bytes()+b" ")
            with self.assertRaisesRegex(NotAdmitted, "EXACT_SOURCE_SHA_MISMATCH"):
                verified_sources(new=path)
            path.write_bytes(OLD.read_bytes()+b" ")
            with self.assertRaisesRegex(NotAdmitted, "EXACT_SOURCE_SHA_MISMATCH"):
                verified_sources(old=path)

    def test_protocol_cannot_silently_relax_threshold(self):
        with tempfile.TemporaryDirectory() as directory:
            p = json.loads(POLICY.read_text(encoding="utf-8"))
            p["go_thresholds"]["bitweight_twohop_fpr_max"] = 0.99
            target = Path(directory)/"bad.json"
            target.write_text(json.dumps(p), encoding="utf-8")
            with self.assertRaisesRegex(NotAdmitted, "PROTOCOL_DRIFT"):
                verified_sources(policy=target)

    def test_frozen_source_composition_has_unmaterialized_positive(self):
        _, old, added = verified_sources()
        graph = old+added
        nodes = tuple(sorted({x for s,_,o in graph for x in (s,o)}))
        preds = tuple(sorted({p for _,p,_ in graph}))
        roots = tuple(int(r[1:]) for r in ROOTS)
        truth = exact_answer_set(graph,roots,preds,nodes)
        self.assertGreater(len(truth),0)
        self.assertEqual(len({(x[0],x[1],x[2]) for x in truth}),4)
        self.assertEqual(exact_answer_set(old,roots,preds,nodes),set())

    def test_fixed_bit_snapshot_preserves_old_and_new_memberships(self):
        _, old, added = verified_sources()
        direct = DirectBitWeights()
        for row in old: direct.program(row)
        snap_old = direct.snapshot()
        for row in added: direct.program(row)
        self.assertEqual(len(snap_old),64)
        self.assertEqual(len(direct.snapshot()),64)
        cold = DirectBitWeights(direct.snapshot())
        self.assertTrue(all(cold.contains(x) for x in old+added))
        self.assertEqual(cold.snapshot(),direct.snapshot())

    def test_real_source_candidate_exhaustion_and_no_science_claim(self):
        r = evaluate()
        self.assertEqual(r["source_witnessed_twohop_paths"],20)
        self.assertEqual(r["source_positive_query_templates"],4)
        self.assertEqual(r["original_source_facts"]+r["new_source_facts"],33)
        self.assertEqual(r["old_positive_memberships_retained"],13)
        self.assertEqual(r["new_positive_memberships_recognized"],20)
        self.assertEqual(r["exact_sparse_triplet_coordinate_bytes"],396)
        self.assertEqual(r["direct_bit_payload_bytes"],64)
        self.assertEqual(r["direct_bit_true_positives"]+r["direct_bit_false_negatives"],
                         r["source_positive_twohop_queries"])
        self.assertEqual(r["direct_bit_true_positives"]+r["direct_bit_false_positives"]+
                         r["direct_bit_false_negatives"]+r["direct_bit_true_negatives"],
                         r["candidate_query_count"])
        self.assertFalse(r["scientific_pass"])
        self.assertFalse(r["trained_recipient_comparison_performed"])
        self.assertFalse(r["neural_recipient_weights_edited"])

    def test_shuffled_objects_are_not_witnessed_source(self):
        _, old, added = verified_sources()
        nodes = tuple(sorted({x for s,_,o in old+added for x in (s,o)}))
        preds = tuple(sorted({p for _,p,_ in old+added}))
        roots = tuple(int(r[1:]) for r in ROOTS)
        self.assertNotEqual(
            exact_answer_set(old+added,roots,preds,nodes),
            exact_answer_set(old+shuffled_control(old,added),roots,preds,nodes)
        )

    def test_no_automatic_generalization_from_empty_bits(self):
        _, old, added = verified_sources()
        nodes = tuple(sorted({x for s,_,o in old+added for x in (s,o)}))
        preds = tuple(sorted({p for _,p,_ in old+added}))
        roots = tuple(int(r[1:]) for r in ROOTS)
        self.assertEqual(bit_answer_set(DirectBitWeights(), roots, preds, nodes), set())


if __name__ == "__main__":
    unittest.main()
