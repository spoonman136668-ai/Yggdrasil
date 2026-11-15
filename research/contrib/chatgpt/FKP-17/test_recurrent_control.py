"""FKP-17 GRU public-only negative/actual-gradient smoke and custody tests.

This does not run the preregistered 2×24 full epochs and is NOT science. The
smoke is explicitly forbidden from entering any original DEV/TRANSFER gate.
"""
import ast
from pathlib import Path
import unittest

import recurrent_control as recurrent
import source_fixture as source


class RecurrentSourceSafeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.examples = source.collect_public(
            source.TRAIN[0], source.public_actions(source.TRAIN[0], 24))
        cls.validation = source.collect_public(
            source.VALIDATION[0], source.public_actions(source.VALIDATION[0], 8))
        cls.smoke = recurrent.source_safe_dev_smoke(cls.examples, cls.validation)

    def setUp(self):
        self.smoke.begin_world()

    def test_really_trains_gradient_network_but_never_qualifies(self):
        m = self.smoke
        self.assertEqual(m.training_receipt["status"], "SMOKE_NOT_QUALIFIED")
        self.assertEqual(len(m.training_receipt["seeds_trained"]), 1)
        self.assertEqual(m.training_receipt["seeds_trained"][0]["seed"], 1515)
        self.assertEqual(m.training_receipt["seeds_trained"][0]["complete_epochs"], 1)
        self.assertGreater(m.training_receipt["parameters"], 0)
        self.assertGreater(m.training_receipt["learned_bytes"], 0)
        self.assertLess(m.learned_bytes, 1048576)
        self.assertTrue(m.training_receipt["validation_crossentropy_per_register"] > 0)
        self.assertEqual(m.training_receipt["foundation_public_rows"], 24)
        self.assertEqual(m.training_receipt["validation_public_rows"], 8)
        with self.assertRaisesRegex(ValueError, "NOT_FULLY_TRAINED"):
            recurrent.assert_science_ready(m, m.foundation_sha256)

    def test_frozen_24_epoch_two_seed_science_contract(self):
        self.assertEqual(recurrent.SEEDS, (1515, 2626))
        self.assertEqual(recurrent.EPOCHS, 24)
        self.assertEqual(recurrent.MAX_HISTORY, 16)
        self.assertEqual(recurrent.OUTPUT, 128)
        m = recurrent.FullyTrainedRecurrent()
        with self.assertRaisesRegex(ValueError, "FULL_FOUNDATION"):
            m.fit_public_foundation(self.examples, self.validation)
        with self.assertRaisesRegex(ValueError, "FROZEN_FIT_MISMATCH"):
            m._fit([([0.0] * 27, (0,) * 8)],
                   [([0.0] * 27, (0,) * 8)], "0" * 64,
                   seeds=(1515,), epochs=1,
                   scientific_qualification_candidate=True)
        with self.assertRaises(ValueError):
            recurrent.assert_science_ready(m, "0" * 64)

    def test_recurrent_training_receipt_cannot_be_forced_to_pass(self):
        m = self.smoke
        original = m.training_receipt
        from copy import deepcopy
        goodlooking = deepcopy(original)
        goodlooking["status"] = "FULL_TRAINED"
        m.training_receipt = goodlooking
        try:
            with self.assertRaisesRegex(ValueError, "SEED_EPOCH"):
                recurrent.assert_science_ready(m, m.foundation_sha256)
            goodlooking["seeds_trained"] = [{"seed": 1515, "complete_epochs": 24},
                                            {"seed": 2626, "complete_epochs": 24}]
            with self.assertRaisesRegex(ValueError, "SOURCE_CUSTODY"):
                recurrent.assert_science_ready(m, "1" * 64)
        finally:
            m.training_receipt = original

    def test_action_choice_blind_to_current_and_future_rewards(self):
        m = self.smoke
        row = self.examples[0]
        pre = m.state_receipt()
        a = m.choose_public(row.before)
        self.assertIn(a, range(8))
        self.assertEqual(a, m.choose_public(row.before))
        self.assertEqual(m.state_receipt(), pre)
        for bad in (row, [True] * 8, (0,) * 7, (16,) * 8):
            with self.assertRaises(ValueError):
                m.choose_public(bad)

    def test_public_feedback_is_received_only_after_observation(self):
        m = self.smoke
        before = m.state_receipt()
        for row in self.examples[:12]:
            m.observe_public(row)
        self.assertEqual(m.world_count, 12)
        self.assertNotEqual(m.state_receipt(), before)
        a = m.choose_public(self.examples[-1].after)
        self.assertIn(a, range(8))
        m.begin_world()
        self.assertEqual(m.world_count, 0)
        self.assertEqual(before, m.state_receipt())

    def test_late_world_feedback_and_forged_future_are_refused(self):
        m = self.smoke
        row = self.examples[0]
        for bad in (tuple(row), {"future_return": 1}, row._replace(action=8),
                    row._replace(reward=float("nan")), row._replace(done=1)):
            old = m.state_receipt()
            with self.assertRaises(ValueError):
                m.observe_public(bad)
            self.assertEqual(old, m.state_receipt())
        for _ in range(256):
            m.observe_public(row)
        old = m.state_receipt()
        with self.assertRaises(ValueError):
            m.observe_public(row)
        self.assertEqual(old, m.state_receipt())

    def test_standalone_model_does_not_import_source_or_native(self):
        contents = Path(recurrent.__file__).read_text("utf-8")
        tree = ast.parse(contents)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for item in node.names:
                    self.assertNotIn(item.name,
                                     ("source_fixture", "public_policies",
                                      "yggdrasil", "memory_gym"))
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn(node.module, ("source_fixture", "public_policies",
                                               "yggdrasil", "memory_gym"))
        self.assertNotIn("allow_dev=True", contents)
        self.assertNotIn("def open_dev(", contents)

    def test_negative_input_does_not_change_local_history(self):
        m = self.smoke
        row = self.examples[0]
        for bad in (row._replace(history=(False,)),
                    row._replace(before=(False,) * 8),
                    row._replace(after=(32,) * 8)):
            before = m.state_receipt()
            with self.assertRaises(ValueError):
                m.observe_public(bad)
            self.assertEqual(before, m.state_receipt())


if __name__ == "__main__":
    unittest.main()
