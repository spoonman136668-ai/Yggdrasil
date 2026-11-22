"""NKR-10: source-free negative tests for real-source masked transfer.

Development fixture is not a newly accessed authentic KB. True historical
source is accessed only by the separate full-image run after dual-OS review.
"""
from __future__ import annotations

from collections import defaultdict
import json
import unittest

from yggdrasil.native_historical_transfer import (
    P_INSTANCE, P_SUBCLASS, MAX_QUERIES, MaskedTrainingView,
    mix64, subject_selected, heldout_fact, frozen_split, evaluate_split,
)
from yggdrasil.public_causal_cells import PublicCausalCells


class FixtureRows:
    def __init__(self, rows):
        self.rows = tuple(sorted(rows))
        self.reads = 0

    def __len__(self):
        return len(self.rows)

    def row_at(self, idx):
        self.reads += 1
        return self.rows[idx]


def fixture():
    """Distinct public synthetic triples with explicit real-like motifs."""
    edges = []
    for s in range(1,257):
        cls = 10000 + s
        parent = 20000 + s
        decoy = 30000 + s
        edges.extend(((s,31,cls),(s,31,parent),(s,31,decoy),
                      (cls,279,parent)))
    return FixtureRows(edges)


class NativeHistoricalMaskedTransferTests(unittest.TestCase):
    def test_realistic_fixture_mask_preserves_original_and_retrieves_heldout(self):
        source = fixture()
        old = source.rows
        native_before = PublicCausalCells().snapshot()
        training, heldout, inventory = frozen_split(
            source, fixture=True, cohort_mod=1, bucket=0)
        result = evaluate_split(training, heldout, inventory, fixture=True)
        self.assertEqual(source.rows, old)
        self.assertEqual(source.reads, 2*len(source))
        self.assertEqual(inventory["original_rows_scanned_per_pass"], len(source))
        self.assertEqual(inventory["source_passes"], 2)
        self.assertGreaterEqual(result["eligible_masked_positive_queries"],64)
        self.assertGreaterEqual(result["real_training_motif_support_subjects"],4)
        self.assertTrue(result["rule_activated"])
        self.assertGreater(result["native_positive_recall_hits_at4"],10)
        self.assertEqual(result["native_positive_recall_hits_at4"],
                         result["symbolic_positive_recall_hits_at4"])
        self.assertTrue(result["exact_equal_information_symbolic_parity"])
        self.assertEqual(result["inferred_facts_admitted"],0)
        self.assertEqual(result["novel_relation_types_created"],0)
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["native_accepted"])
        self.assertEqual(PublicCausalCells().snapshot(),native_before)

    def test_heldout_edges_not_visible_to_learning_even_when_source_duplicate(self):
        data = fixture()
        s, p, obj = next(x for x in data.rows
                         if x[1] == 31 and heldout_fact(x[0],x[2]))
        data.rows = tuple(sorted((*data.rows,(s,p,obj))))
        training, sealed, info = frozen_split(data,fixture=True,cohort_mod=1,bucket=0)
        self.assertIn(obj,sealed[s])
        self.assertNotIn(obj,training.instances.get(s,()))
        self.assertEqual(info["masked_p31_rows"],
                         sum(1 for a,b,c in data.rows if b==31 and heldout_fact(a,c)))
        self.assertEqual(data.reads,2*len(data))

    def test_source_order_does_not_change_split_or_predictions(self):
        rows = fixture().rows
        normal = FixtureRows(rows)
        backwards = FixtureRows(tuple(reversed(rows)))
        backwards.rows = tuple(reversed(rows))
        first, a, ai = frozen_split(normal,fixture=True,cohort_mod=1,bucket=0)
        second, b, bi = frozen_split(backwards,fixture=True,cohort_mod=1,bucket=0)
        self.assertEqual(first.instances,second.instances)
        self.assertEqual(first.subclasses,second.subclasses)
        self.assertEqual(a,b)
        aa = evaluate_split(first,a,ai,fixture=True)
        bb = evaluate_split(second,b,bi,fixture=True)
        for key in ("eligible_masked_positive_queries",
                    "native_positive_recall_hits_at4",
                    "symbolic_positive_recall_hits_at4",
                    "frequency_prior_positive_hits_at4"):
            self.assertEqual(aa[key],bb[key])

    def test_no_p279_or_no_p31_returns_null_no_promoted_facts(self):
        rows = [(s,31,10000+s) for s in range(1,257)]
        inp = FixtureRows(rows)
        train,labels,inventory = frozen_split(
            inp,fixture=True,cohort_mod=1,bucket=0)
        metrics = evaluate_split(train,labels,inventory,fixture=True)
        self.assertEqual(metrics["real_training_motif_support_subjects"],0)
        self.assertFalse(metrics["rule_activated"])
        self.assertEqual(metrics["native_positive_recall_hits_at4"],0)
        self.assertFalse(metrics["scientific_pass"])
        inp = FixtureRows([(s,279,500+s) for s in range(1,65)])
        train,labels,inventory = frozen_split(
            inp,fixture=True,cohort_mod=1,bucket=0)
        metrics = evaluate_split(train,labels,inventory,fixture=True)
        self.assertEqual(metrics["eligible_masked_positive_queries"],0)
        self.assertFalse(metrics["scientific_pass"])

    def test_frozen_hash_and_unknown_relation_negative_control(self):
        self.assertEqual(mix64(0),mix64(0))
        self.assertNotEqual(mix64(1),mix64(2))
        self.assertEqual(heldout_fact(123456,789),heldout_fact(123456,789))
        with self.assertRaises(ValueError):
            mix64(-1)
        visible = MaskedTrainingView({2:{3}},{3:{4}})
        self.assertEqual(visible.candidate_counts(2,31),{4:1})
        self.assertEqual(visible.rank(2,enabled=True),(4,))
        self.assertEqual(visible.rank(2,enabled=False),())
        self.assertEqual(visible.candidate_counts(2,999),{})
        self.assertEqual(visible.rank(2,enabled=True,target_relation=999),())
        with self.assertRaises(ValueError):
            visible.candidate_counts(0,31)
        self.assertFalse(visible.candidate_counts(3,31))

    def test_non_original_source_rejected_and_nonfrozen_parameters_denied(self):
        with self.assertRaisesRegex(ValueError,"NKR10_ORIGINAL_NATIVE_WEIGHTS_REQUIRED"):
            frozen_split(fixture())
        with self.assertRaisesRegex(ValueError,"NKR10_SPLIT_NOT_FROZEN"):
            frozen_split(fixture(),fixture=True,cohort_mod=0)
        with self.assertRaisesRegex(ValueError,"NKR10_SPLIT_NOT_FROZEN"):
            frozen_split(fixture(),fixture=True,cohort_mod=32,bucket=32)
        source=FixtureRows([(1,31,3)])
        _, labels, inventory=frozen_split(source,fixture=True,cohort_mod=1,bucket=0)
        result=evaluate_split(MaskedTrainingView({},{}),labels,inventory,fixture=True)
        self.assertFalse(result["scientific_pass"])

if __name__=="__main__":
    unittest.main()
