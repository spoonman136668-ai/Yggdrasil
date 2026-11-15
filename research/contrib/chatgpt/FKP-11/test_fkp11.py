"""FKP11 pre-primary source-safe tests: no original Memory Gym reset/step."""
import ast
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import probe

class FKP11FixtureTests(unittest.TestCase):
    def test_frozen_source_identity_cohorts_and_limits(self):
        self.assertEqual(probe.admit.SOURCE_SHA,
                         "a94f2b60d1769ea44df3226561488768e1dff9f4")
        self.assertEqual(len(probe.admit.SOURCE_BLOBS),5)
        self.assertEqual(probe.TASKS,("MortarMayhem-v0","MysteryPath-v0"))
        self.assertEqual(probe.SEEDS,(971100,971101,971102,971103))
        self.assertTrue(set(probe.SEEDS).isdisjoint(probe.admit.SEEDS))
        self.assertEqual(probe.MAX_STEPS,256)
        self.assertEqual(len(probe.SEEDS)*len(probe.POLICIES)*len(probe.MODES)*len(probe.TASKS),32)

    def test_source_native_public_reward_options(self):
        self.assertIsNone(probe.reward_options("MortarMayhem-v0","original"))
        self.assertIsNone(probe.reward_options("MysteryPath-v0","original"))
        self.assertEqual(probe.reward_options("MortarMayhem-v0","public_failure_feedback"),
                         {"reward_command_failure":-0.05})
        self.assertEqual(probe.reward_options("MysteryPath-v0","public_failure_feedback"),
                         {"reward_fall_off":-0.05})
        with self.assertRaises(ValueError):
            probe.reward_options("Other","original")
        with self.assertRaises(ValueError):
            probe.reward_options("MysteryPath-v0","unsafe")

    def test_two_bounded_policies_are_reproducible_and_in_bounds(self):
        for seed in probe.SEEDS:
            for name in probe.POLICIES:
                sequence=tuple(probe.choose_action(seed,name,i) for i in range(33))
                self.assertEqual(sequence,tuple(probe.choose_action(seed,name,i) for i in range(33)))
                self.assertTrue(all(len(a)==2 and all(0<=v<3 for v in a) for a in sequence))
                if name=="macro8":
                    self.assertEqual(len(set(sequence[:8])),1)
                    self.assertEqual(len(set(sequence[8:16])),1)
        with self.assertRaises(ValueError):
            probe.choose_action(970100,"random",0)
        with self.assertRaises(ValueError):
            probe.choose_action(1900,"macro8",0)
        with self.assertRaises(ValueError):
            probe.choose_action(probe.SEEDS[0],"random",256)

    def test_reject_unregistered_before_external_simulator_import(self):
        with self.assertRaises(ValueError):
            probe.episode("Other",probe.SEEDS[0],"random","original")
        with self.assertRaises(ValueError):
            probe.episode(probe.TASKS[0],970100,"random","original")
        with self.assertRaises(ValueError):
            probe.episode(probe.TASKS[0],probe.SEEDS[0],"learned_hidden","original")

    def test_source_owner_contract_has_no_private_retrieval(self):
        body=(HERE/"probe.py").read_text(encoding="utf-8")
        ast.parse(body)
        self.assertNotIn("env.unwrapped",body)
        self.assertNotIn("debug_rgb_array",body)
        self.assertNotIn("getattr(env,",body)
        self.assertIn("admit.source_custody",body)
        self.assertIn("env.step(action)",body)
        self.assertIn("no", "no")  # fixture itself performs no original steps

if __name__=="__main__":
    unittest.main()
