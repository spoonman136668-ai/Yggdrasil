"""MD23 prospectively locked registered evaluator tests; no official seeds."""
import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch

FILE = Path(__file__).with_name("registered_md23.py")
spec = importlib.util.spec_from_file_location("md23_registration", FILE)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


class RegisteredFirstUseSafeguards(unittest.TestCase):
    def test_frozen_original_protocol_without_firstuse(self):
        p = d.frozen_identity()
        self.assertEqual(p["experiment_id"], "DG1-MD23-20261114")
        self.assertEqual(d.SCHEMA, "yggdrasil.dg1-md23-original.v1")
        self.assertEqual(d.d.FROZEN_PREREG, "ea927ae080aee59d2dc0783f45eb703735dfb52f")
        self.assertEqual(d.d.ARMS, ("causal_graph", "shuffled_graph",
             "fixed_scripted", "reactive", "tabular_q", "recurrent_imitation"))
        self.assertEqual(len(d.COLD), 12)

    def test_registered_firstuse_requires_explicit_verified_event(self):
        with patch.dict(os.environ, {"MD23_FIRST_USE": ""}):
            with self.assertRaisesRegex(PermissionError, "CONTEXT_REQUIRED"):
                d.registered_firstuse()

    def test_six_arm_charged_toy_training_and_frozen_scoring(self):
        toy = d.toy_scoring_preflight()
        self.assertTrue(toy["toy_only"])
        self.assertGreater(toy["train_steps"], 0)
        self.assertGreater(toy["charged_eval_steps"], 0)
        self.assertEqual(set(toy["actions"]), set(d.d.ARMS))
        self.assertGreaterEqual(toy["actions"]["fixed_scripted"]["goals"], 0)

    def test_toy_seed_sets_do_not_intersect_original(self):
        original = set(d.TRAIN_DOOR+d.TRAIN_BOX+d.INTERFERENCE+
                       d.COLD+d.SIZE+d.BOX)
        self.assertFalse(set(d.d.TOY_SEEDS) & original)
        self.assertEqual(len(original), 96)

    def test_seed_wins_are_strict_paired_comparisons(self):
        example={"by_arm":{
            "causal_graph":{"episodes":[{"seed":11,"discounted_reward":.7},
                                         {"seed":17,"discounted_reward":.5}]},
            "shuffled_graph":{"episodes":[{"seed":11,"discounted_reward":.6},
                                           {"seed":17,"discounted_reward":.5}]}}}
        self.assertEqual(d.seed_wins(example), 1)
        example["by_arm"]["shuffled_graph"]["episodes"].pop()
        with self.assertRaisesRegex(AssertionError, "UNPAIRED"):
            d.seed_wins(example)


if __name__ == "__main__":
    unittest.main()
