"""Gate28 dense causal matched-budget diagnostic, not scientific first-use."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "research/contrib/chatgpt/self-assembling-topologies/gate28"))
import core
import dense_reference as dense
import full_reference
import world


class TestGate28DenseReference(unittest.TestCase):
    def test_dictionary_is_partial_but_stratified_and_true_budgeted(self):
        self.assertEqual(dense.SIZES, (768, 768, 768, 768, 768, 768, 280))
        self.assertEqual(sum(dense.SIZES), 4888)
        self.assertLess(sum(dense.SIZES), full_reference.TOTAL_HYPOTHESES)
        self.assertEqual(len(dense.BANKS), 7)
        for node, bank in enumerate(dense.BANKS):
            self.assertEqual(len(set(bank)), dense.SIZES[node])
            self.assertTrue(set(rule[0] for rule in bank).issubset(
                set(world.RULE_DICTIONARY)))
            self.assertIn("compose", set(rule[0] for rule in bank))
            self.assertIn("maj3", set(rule[0] for rule in bank))
        self.assertIn("lag_xor", set(x[0] for x in dense.BANKS[0]))
        for arm in dense.ARMS:
            s = dense.new(arm)
            receipt = dense.capacity_receipt(s)
            self.assertFalse(receipt["complete_grammar_covered"])
            self.assertTrue(receipt["fully_fitted_selected_rules"])
            self.assertLess(len(dense.pack(s)), core.MAX_STATE_BYTES)
            self.assertEqual(dense.pack(dense.unpack(dense.pack(s))),
                             dense.pack(s))

    def test_full_course_cold_source_budget_and_forced_diagnostic(self):
        w = world.HiddenWorld(900081, diagnostic=True)
        s = dense.new(dense.ARMS[0])
        worst = 0
        seen = {}
        for step in range(96):
            row = w.source(step)
            meter = core.Work()
            dense.observe(s, row.context, row.intermediates, row.action,
                          row.consequence, meter)
            worst = max(worst, meter.count)
        dense.seal_source(s)
        source = s["source"]["digest"]
        before = [dense.source_predict(s, core.as_bits(mask), 12, core.Work())
                  for mask in (3, 19, 88)]
        for phase in ("B", "R"):
            total_prequential = 0.0
            for step in range(64):
                action = w.forced_action(phase, step)
                row = w.feedback(phase, step, action)
                meter = core.Work()
                prediction = dense.predict(s, row.context, action, meter)
                total_prequential += (prediction - row.consequence) ** 2
                dense.observe(s, row.context, row.intermediates, action,
                              row.consequence, meter)
                worst = max(worst, meter.count)
            raw = dense.pack(s)
            self.assertLessEqual(len(raw), core.MAX_STATE_BYTES)
            s = dense.unpack(raw)
            self.assertEqual(source, s["source"]["digest"])
            self.assertEqual(before, [
                dense.source_predict(s, core.as_bits(mask), 12, core.Work())
                for mask in (3, 19, 88)])
            total_held = 0.0
            reward = 0
            for query in range(32):
                x = w.held_context(phase, query)
                meter = core.Work()
                a = w.forced_action(phase, query)
                pred = dense.predict(s, x, a, meter)
                choice = dense.choose(s, x, meter)
                total_held += (pred - w.held_query(
                    phase, query, a).consequence) ** 2
                reward += w.held_query(phase, query, choice).consequence
                worst = max(worst, meter.count)
            seen[phase] = {"held_forced_brier": round(total_held / 32, 9),
                           "prequential_brier": round(total_prequential / 64, 9),
                           "held_selected_reward": reward,
                           "checkpoint_bytes": len(raw)}
        self.assertEqual(s["step"], 224)
        self.assertLessEqual(worst, core.MAX_RULE_EVALS)
        self.assertEqual(dense.pack(dense.unpack(dense.pack(s))), dense.pack(s))
        print("G28_DENSE_FITTED_DIAGNOSTIC", json.dumps({
            "seed": 900081, "primary_scored": False,
            "grammatical_hypotheses": full_reference.TOTAL_HYPOTHESES,
            "fitted_subset": sum(dense.SIZES), "max_rule_work": worst,
            "phases": seen, "gain_verified": False}, sort_keys=True))

    def test_do_intervention_and_invalid_inputs_fail_closed(self):
        s = dense.new(dense.ARMS[0])
        row = world.HiddenWorld(900082, diagnostic=True).source(0)
        dense.observe(s, row.context, row.intermediates, 0,
                      row.consequence, core.Work())
        self.assertEqual(set(s["scores"][0]), {0})
        self.assertTrue(any(x != 0 for x in s["scores"][6]))
        with self.assertRaises(ValueError):
            dense.observe(s, row.context, row.intermediates[:5], 12,
                          1, core.Work())
        with self.assertRaises(ValueError):
            dense.observe(s, row.context, row.intermediates, 13,
                          1, core.Work())
        with self.assertRaises(ValueError):
            dense.observe(s, row.context, row.intermediates, 12,
                          2, core.Work())
        bad = bytearray(dense.pack(s))
        bad[40] ^= 1
        with self.assertRaises(ValueError):
            dense.unpack(bytes(bad))
        with self.assertRaises(ValueError):
            dense.unpack(b"x" * (core.MAX_STATE_BYTES + 1))

    def test_source_mutation_detection_and_eig_bounds(self):
        s = dense.new(dense.ARMS[1])
        w = world.HiddenWorld(900083, diagnostic=True)
        for step in range(96):
            row = w.source(step)
            dense.observe(s, row.context, row.intermediates,
                          row.action, row.consequence, core.Work())
        dense.seal_source(s)
        x = w.public_context("B", 0)
        meter = core.Work()
        a = dense.choose(s, x, meter)
        p = dense.predict(s, x, a, meter)
        self.assertIn(a, range(13))
        self.assertTrue(0.1 <= p <= 0.9)
        self.assertLessEqual(meter.count, core.MAX_RULE_EVALS)
        first = s["source"]["snapshot"]["prepared"][6][0]
        s["source"]["snapshot"]["prepared"][6][0] = (first[0], first[1] * 0.5)
        with self.assertRaises(ValueError):
            dense.pack(s)
