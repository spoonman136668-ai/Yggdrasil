"""FKP-17 independent Bayesian and public exemplar-control source-safe gates.

No DEV or reserved transfer worlds; no owner-protected evaluator or new claims.
"""
from collections import namedtuple
from pathlib import Path
import unittest

import public_policies as candidate
import source_fixture as fixture
import strong_controls as control


class IndependentControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.facts = tuple(row for _, _, row in fixture.foundation_facts())
        cls.symbolic = control.SymbolicBayes().fit_public_foundation(cls.facts)
        cls.retrieval = control.CountRetrieval().fit_public_foundation(cls.facts)
        cls.candidate = candidate.PublicRelationArm("STRUCTURED").fit_public_foundation(cls.facts)

    def setUp(self):
        self.symbolic.begin_world()
        self.retrieval.begin_world()
        self.candidate.begin_world()

    def test_all_32768_source_facts_identical_sha_and_memory_bound(self):
        same = control.assert_strong_public_information(
            (self.symbolic, self.retrieval), self.candidate.foundation_sha256)
        self.assertEqual(same, self.symbolic.foundation_sha256)
        self.assertEqual(same, self.retrieval.foundation_sha256)
        self.assertEqual(self.symbolic.foundation_count, 32768)
        self.assertEqual(self.retrieval.foundation_count, 32768)
        self.assertEqual(self.symbolic.memory_bytes, 65536)
        self.assertEqual(self.retrieval.memory_bytes, 589824)
        self.assertLess(self.symbolic.memory_bytes, 1048576)
        self.assertLess(self.retrieval.memory_bytes, 1048576)

    def test_only_public_state_before_future_consequence_choose(self):
        source = fixture.collect_public(fixture.TRAIN[0],
                                        fixture.public_actions(fixture.TRAIN[0], 24))
        for arm in (self.symbolic, self.retrieval):
            before_receipt = arm.state_receipt()
            choice = arm.choose_public(source[0].before)
            self.assertIn(choice, range(8))
            self.assertEqual(before_receipt, arm.state_receipt())
            self.assertEqual(choice, arm.choose_public(source[0].before))
            for row in source:
                arm.observe_public(row)
            self.assertEqual(arm.world_count, 24)
            self.assertNotEqual(before_receipt, arm.state_receipt())
            self.assertIn(arm.choose_public(source[-1].after), range(8))

    def test_world_reset_retains_prior_and_discards_local_learning(self):
        row = fixture.collect_public(fixture.TRAIN[1], (0, 1))[0]
        for arm in (self.symbolic, self.retrieval):
            baseline = arm.state_receipt()
            arm.observe_public(row)
            self.assertNotEqual(baseline, arm.state_receipt())
            arm.begin_world()
            self.assertEqual(arm.world_count, 0)
            self.assertEqual(baseline, arm.state_receipt())
            self.assertEqual(arm.foundation_count, 32768)

    def test_true_novel_public_intervention_changes_native_baseline(self):
        actions = (0, 1, 2, 3, 4, 5, 6, 7) * 3
        rows = fixture.collect_public(fixture.TRAIN[2], actions)
        for arm in (self.symbolic, self.retrieval):
            for row in rows:
                arm.observe_public(row)
            self.assertEqual(arm.world_count, 24)
        self.assertGreater(sum(self.symbolic._online), 0)
        self.assertTrue(any(self.retrieval._online))

    def test_private_future_labels_or_wrong_schema_fail_closed(self):
        row = fixture.collect_public(fixture.TRAIN[4], (3,))[0]
        Extended = namedtuple("Extended",
                              ("before", "action", "after", "reward",
                               "done", "history", "oracle_future"))
        future = Extended(*row, [1] * 8)
        for arm in (self.symbolic, self.retrieval):
            saved = arm.state_receipt()
            for bad in (future, {"future": row.after}, tuple(row)):
                with self.subTest(arm=type(arm), input=type(bad)):
                    with self.assertRaises(ValueError):
                        arm.observe_public(bad)
            self.assertEqual(saved, arm.state_receipt())
            for badstate in (row, [True] * 8, (0,) * 7, [16] * 8):
                with self.assertRaises(ValueError):
                    arm.choose_public(badstate)

    def test_action_and_reward_negative_controls_cannot_mutate_state(self):
        row = fixture.collect_public(fixture.TRAIN[5], (1,))[0]
        bad = (row._replace(action=True), row._replace(action=8),
               row._replace(reward=float("nan")), row._replace(reward=2.0),
               row._replace(after=(0,) * 7), row._replace(done=0))
        for arm in (self.symbolic, self.retrieval):
            saved = arm.state_receipt()
            for r in bad:
                with self.assertRaises(ValueError):
                    arm.observe_public(r)
            self.assertEqual(saved, arm.state_receipt())
            self.assertEqual(arm.world_count, 0)

    def test_budget_at_256_and_atomic_overflow_refusal(self):
        row = fixture.collect_public(fixture.TRAIN[6], (0,))[0]
        for arm in (self.symbolic, self.retrieval):
            for _ in range(256):
                arm.observe_public(row)
            self.assertEqual(arm.world_count, 256)
            saved = arm.state_receipt()
            with self.assertRaises(ValueError):
                arm.observe_public(row)
            self.assertEqual(arm.state_receipt(), saved)

        self.symbolic.begin_world()
        zero = fixture.PublicStep((0,) * 8, 0, (0,) * 8, 0.0, False, ())
        self.symbolic._online[control._index(0, 6, 0, 0)] = 65535
        sealed = self.symbolic.state_receipt()
        with self.assertRaises(OverflowError):
            self.symbolic.observe_public(zero)
        self.assertEqual(self.symbolic.state_receipt(), sealed)
        self.assertEqual(self.symbolic.world_count, 0)

    def test_mismatched_fact_source_or_missing_competitor_rejected(self):
        with self.assertRaises(ValueError):
            control.assert_strong_public_information((self.symbolic,),
                                                     self.candidate.foundation_sha256)
        with self.assertRaises(ValueError):
            control.assert_strong_public_information((self.symbolic, self.retrieval),
                                                     "0" * 64)
        stranger = control.CountRetrieval()
        stranger._sealed = True
        stranger.foundation_count = 32768
        with self.assertRaises(ValueError):
            control.assert_strong_public_information((self.symbolic, stranger),
                                                     self.candidate.foundation_sha256)

    def test_public_law_import_not_in_strong_control_source(self):
        data = Path(control.__file__).read_text(encoding="utf-8")
        import ast
        syntax = ast.parse(data)
        for node in ast.walk(syntax):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotIn(alias.name, ("source_fixture", "public_policies",
                                                   "memory_gym", "torch"))
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn(node.module,
                                 ("source_fixture", "public_policies",
                                  "memory_gym"))
        self.assertFalse(hasattr(control.SymbolicBayes(), "private_world"))
        self.assertFalse(hasattr(control.CountRetrieval(), "private_world"))

    def test_reproducible_training_and_cold_fresh_laws_without_held(self):
        first = fixture.collect_public(fixture.VALIDATION[0], (3, 1, 0, 5, 7))
        for arm in (self.symbolic, self.retrieval):
            baseline = arm.state_receipt()
            for row in first:
                arm.observe_public(row)
            saved = arm.state_receipt()
            arm.begin_world()
            for row in first:
                arm.observe_public(row)
            self.assertEqual(arm.state_receipt(), saved)
            arm.begin_world()
            self.assertEqual(arm.state_receipt(), baseline)


if __name__ == "__main__":
    unittest.main()
