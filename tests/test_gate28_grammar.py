"""Gate28 complete rule dictionary diagnostic; no reserved scientific seeds."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "research/contrib/chatgpt/self-assembling-topologies/gate28"))
import grammar
import world


class TestGate28Grammar(unittest.TestCase):
    def test_full_rule_count_and_legacy_undercoverage(self):
        self.assertEqual(tuple(map(len, grammar.FULL_BANKS)),
                         grammar.EXPECTED_COUNTS)
        self.assertEqual(sum(grammar.EXPECTED_COUNTS), 11424)
        self.assertTrue(all(len(b) == 96 for b in grammar.LEGACY_BANKS))
        self.assertTrue(all(legacy < complete for legacy, complete in zip(
            map(len, grammar.LEGACY_BANKS), grammar.EXPECTED_COUNTS)))

    def test_noncommutative_operators_preserved(self):
        sig = grammar.signature
        self.assertEqual(sig("xor", (1, 2), 0), sig("xor", (2, 1), 0))
        self.assertEqual(sig("maj3", (3, 2, 1), 1),
                         sig("maj3", (1, 2, 3), 1))
        self.assertEqual(sig("compose", (1, 2, 3), 0),
                         sig("compose", (2, 1, 3), 0))
        self.assertNotEqual(sig("compose", (1, 2, 3), 0),
                            sig("compose", (1, 3, 2), 0))
        self.assertNotEqual(sig("lag_xor", (1, 2), 0),
                            sig("lag_xor", (2, 1), 0))
        with self.assertRaisesRegex(ValueError, "DUPLICATED_CAUSAL_PARENT"):
            sig("compose", (1, 2, 1), 0)

    def test_world_parent_repair_no_duplicate_diagnostic(self):
        for seed in range(900000, 900050):
            w = world.HiddenWorld(seed, diagnostic=True)
            for layer in ("A", "B"):
                for rule in w._rules[layer]:
                    self.assertEqual(len(rule.parents), len(set(rule.parents)))

    def test_private_diagnostic_coverage_not_training(self):
        result = grammar.audit()
        self.assertEqual(result["cases"], 12 * 2 * 7)
        self.assertEqual(result["complete_cases"], result["cases"])
        self.assertLess(result["legacy_96_cases"], result["cases"])
        self.assertEqual(result["scientific_control_adequacy"],
                         "FAIL_LEGACY_BAYES_UNDERCOVERS_TRUTH")
        self.assertFalse(result["primary_seeds_consumed"])
        self.assertFalse(result["scientific_gain_verified"])
