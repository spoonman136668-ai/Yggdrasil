"""Gate28 unconstrained full-grammar fitted reference: diagnostic seeds only."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "research/contrib/chatgpt/self-assembling-topologies/gate28"))
import core
import full_reference as full
import grammar
import world


class TestGate28FullReference(unittest.TestCase):
    def test_full_dictionary_and_seed_isolation(self):
        self.assertEqual(full.TOTAL_HYPOTHESES, 11424)
        self.assertEqual(full.BANK_SIZES, grammar.EXPECTED_COUNTS)
        self.assertEqual(full.new(full.ARMS[0]), full.new(full.ARMS[0]))
        with self.assertRaises(TypeError):
            full.new(full.ARMS[0], 501000)
        self.assertTrue(full.DIAGNOSTIC_ONLY)

    def test_observe_all_rules_with_measured_budget_violation(self):
        w = world.HiddenWorld(900021, diagnostic=True)
        row = w.feedback("B", 0, 12)
        s = full.new(full.ARMS[0])
        meter = full.Meter()
        full.observe(s, row.context, row.intermediates,
                     row.action, row.consequence, meter)
        receipt = full.resource_receipt(s)
        self.assertEqual(s["step"], 1)
        self.assertEqual(meter.evaluations, full.TOTAL_HYPOTHESES)
        self.assertEqual(receipt["full_hypotheses"], 11424)
        self.assertFalse(receipt["matched_rule_budget_ok"])
        self.assertFalse(receipt["first_use_permitted"])
        self.assertFalse(receipt["primary_science_run"])
        self.assertFalse(receipt["matched_state_budget_ok"])
        # Identity of all candidate logits must stay independent of held queries.
        frozen = full.unpack(full.pack(s))
        self.assertEqual(full.pack(frozen), full.pack(s))

    def test_intervention_bypasses_mechanism_not_outcome_fit(self):
        row = world.HiddenWorld(900021, diagnostic=True).feedback("B", 1, 0)
        s = full.new(full.ARMS[0])
        full.observe(s, row.context, row.intermediates,
                     row.action, row.consequence, full.Meter())
        self.assertEqual(set(s["scores"][0]), {0})
        self.assertNotEqual(set(s["scores"][6]), {0})
        self.assertEqual(s["peak_fit_evaluations"],
                         full.TOTAL_HYPOTHESES - full.BANK_SIZES[0])

    def test_all_operators_reproduced_under_public_cells(self):
        s = full.new(full.ARMS[1])
        w = world.HiddenWorld(900021, diagnostic=True)
        # Check exact semantics with diagnostic-only private truth; these
        # truth rules are NEVER supplied to observe(), choose() or predict().
        for layer in ("A", "B"):
            for i, rule in enumerate(w._rules[layer]):
                sig = grammar.signature(rule.kind, rule.parents, rule.invert)
                self.assertIn(sig, full.BANKS[i])
        for i in range(8):
            row = w.source(i)
            full.observe(s, row.context, row.intermediates,
                         row.action, row.consequence, full.Meter())
        x = w.public_context("B", 1)
        for arm in full.ARMS:
            s["arm"] = arm
            meter = full.Meter()
            action = full.choose(s, x, meter)
            p = full.predict(s, x, action, meter)
            self.assertIn(action, range(13))
            self.assertTrue(0.1 <= p <= 0.9)
            self.assertGreater(meter.evaluations, 0)

    def test_cold_integrity_and_source_not_silently_modified(self):
        s = full.new(full.ARMS[0])
        w = world.HiddenWorld(900022, diagnostic=True)
        for i in range(96):
            row = w.source(i)
            full.observe(s, row.context, row.intermediates, row.action,
                         row.consequence, full.Meter())
        full.seal_source(s)
        digest = s["source"]["digest"]
        source_read = full.source_predict(s, (1, 1, 0, 1, 0, 0, 1, 0),
                                          12, full.Meter())
        cold = full.unpack(full.pack(s))
        row = w.feedback("B", 0, 12)
        full.observe(cold, row.context, row.intermediates,
                     row.action, row.consequence, full.Meter())
        self.assertEqual(digest, cold["source"]["digest"])
        self.assertEqual(source_read, full.source_predict(
            cold, (1, 1, 0, 1, 0, 0, 1, 0), 12, full.Meter()))
        self.assertEqual(cold["step"], 97)
        bad = full.pack(cold).replace(b'"step":97', b'"step":98')
        with self.assertRaises(ValueError):
            full.unpack(bad)
