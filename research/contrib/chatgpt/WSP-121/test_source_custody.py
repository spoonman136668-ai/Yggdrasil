"""Independent engineering-only source/custody tests: original IDs never open."""
from copy import deepcopy
from dataclasses import fields
from unittest import TestCase
from unittest.mock import patch

import source_custody as C


class IndependentCustodyTests(TestCase):
    def test_primary_and_protected_first_use_denied_before_construction(self):
        with patch.object(C, "_construct_engineering_view",
                          side_effect=AssertionError("opened sealed source")):
            for seed in (121000, 121023, 121024, 121047,
                         121800, 121863, 120800, 120863,
                         120019, 122001, True, "121900"):
                with self.subTest(seed=seed):
                    with self.assertRaises(PermissionError):
                        C.EngineeringCustodian(seed)
                    with self.assertRaises(PermissionError):
                        C.open_original(seed)
        self.assertFalse(set(C.ENGINEERING) & (C.PRIMARY | C.PROTECTED))

    def test_source_independent_public_graph_and_no_held_leak(self):
        self.assertNotIn("meta_operator", C.__dict__)
        self.assertEqual(tuple(f.name for f in fields(C.PublicView)),
                         ("seed", "graph", "legal", "held"))
        hashes = []
        for seed in sorted(C.ENGINEERING):
            c = C.EngineeringCustodian(seed)
            p = c.public
            self.assertEqual(len(p.graph), 6)
            self.assertTrue(all(len(set(relation)) == 64
                                for relation in p.graph))
            self.assertEqual((len(p.legal), len(p.held)), (40, 24))
            self.assertFalse(set(p.legal) & set(p.held))
            self.assertEqual(set(p.legal) | set(p.held), set(range(64)))
            self.assertEqual({p.feature(subject)
                              for subject in p.legal[:8]}, set(range(8)))
            self.assertEqual(p, C.EngineeringCustodian(seed).public)
            hashes.append(p.fingerprint())
        self.assertEqual(len(set(hashes)), 4)

    def test_query_budget_held_denial_duplicate_and_one_time_scoring(self):
        for seed in sorted(C.ENGINEERING):
            c = C.EngineeringCustodian(seed)
            with self.subTest(seed=seed):
                with self.assertRaises(PermissionError):
                    c.query(c.public.held[0])
                with self.assertRaises(PermissionError):
                    c.score_held_once({})
                for subject in c.public.legal[:c.budget]:
                    self.assertIn(c.query(subject), c.public.routes(subject))
                self.assertEqual(c.count, c.budget)
                for invalid in (c.public.held[0], c.public.legal[0],
                                c.public.legal[c.budget]):
                    with self.assertRaises(PermissionError):
                        c.query(invalid)
                with self.assertRaises(ValueError):
                    c.score_held_once({})
                all_abstain = {s: None for s in c.public.held}
                summary = c.score_held_once(all_abstain)
                self.assertEqual(summary["held"], 24)
                self.assertEqual(summary["abstained"], 24)
                self.assertEqual(summary["correct"], 0)
                self.assertEqual(summary["wrong_confident"], 0)
                self.assertFalse(summary["scientific_pass"])
                self.assertFalse(summary["source_first_use"])
                self.assertFalse(summary["native_admission"])
                self.assertNotIn("held_labels", summary)
                with self.assertRaises(PermissionError):
                    c.score_held_once(all_abstain)

    def test_source_receipt_parity_and_held_score_negative_controls(self):
        arms = [C.EngineeringCustodian(121900) for _ in range(3)]
        for subject in arms[0].public.legal[:arms[0].budget]:
            observed = [arm.query(subject) for arm in arms]
            self.assertEqual(len(set(observed)), 1)
        self.assertEqual(len({arm.source_sha256 for arm in arms}), 1)
        predictions = {s: arms[0].public.routes(s)[0]
                       for s in arms[0].public.held}
        receipts = [arm.score_held_once(deepcopy(predictions))
                    for arm in arms]
        self.assertEqual(receipts, [receipts[0]] * 3)
        self.assertEqual(receipts[0]["correct"] +
                         receipts[0]["wrong_confident"] +
                         receipts[0]["abstained"], 24)
        self.assertEqual(len(receipts[0]["source_sha256"]), 64)
        self.assertEqual(len(receipts[0]["held_predictions_sha256"]), 64)

    def test_malformed_or_partial_scoring_cannot_consume_held(self):
        c = C.EngineeringCustodian(121902)
        for s in c.public.legal[:c.budget]:
            c.query(s)
        template = {s: None for s in c.public.held}
        for transform in (
            lambda r: r.pop(next(iter(r))),
            lambda r: r.update({c.public.legal[0]: None}),
            lambda r: r.update({c.public.held[0]: True}),
            lambda r: r.update({c.public.held[0]: 64}),
        ):
            bad = deepcopy(template)
            transform(bad)
            with self.assertRaises(ValueError):
                c.score_held_once(bad)
        # Denied malformed attempts do not consume the single permitted scoring.
        self.assertEqual(c.score_held_once(template)["abstained"], 24)
