"""Gate28 causal posterior diagnostic controls; no primary science."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "research/contrib/chatgpt/self-assembling-topologies/gate28"))
import bayes
import core
import world
import runner


class TestGate28Bayes(unittest.TestCase):
    def test_operator_grammar_and_capacity(self):
        kinds = {h[0] for bank in bayes.BANKS for h in bank}
        self.assertEqual(kinds, {"xor", "and", "or", "nand",
                                 "maj3", "compose", "lag_xor"})
        self.assertEqual(len(bayes.BANKS), 7)
        self.assertTrue(all(len(bank) == 96 for bank in bayes.BANKS))
        self.assertLess(len(bayes.pack(bayes.new(bayes.ARMS[0]))), 16384)

    def test_no_hidden_seed_and_only_public_rows(self):
        a, b = bayes.new(bayes.ARMS[0]), bayes.new(bayes.ARMS[0])
        self.assertEqual(a, b)
        with self.assertRaises(TypeError):
            bayes.new(bayes.ARMS[0], 501000)
        w = world.HiddenWorld(900031, diagnostic=True)
        for t in range(96):
            row = w.source(t)
            for s in (a, b):
                meter = core.Work()
                bayes.observe(s, row.context, row.intermediates, row.action,
                              row.consequence, meter)
                self.assertLessEqual(meter.count, 8192)
        self.assertEqual(bayes.pack(a), bayes.pack(b))
        bayes.seal_source(a)
        digest = a["source"]["digest"]
        prior_readout = bayes.source_predict(a, (0, 1, 0, 1, 1, 0, 0, 1), 12, core.Work())
        cold = bayes.unpack(bayes.pack(a))
        for t in range(32):
            row = w.feedback("B", t, 2)
            bayes.observe(cold, row.context, row.intermediates, row.action,
                          row.consequence, core.Work())
        self.assertEqual(digest, cold["source"]["digest"])
        self.assertEqual(prior_readout, bayes.source_predict(
            cold, (0, 1, 0, 1, 1, 0, 0, 1), 12, core.Work()))

    def test_reward_and_eig_choices_and_budget(self):
        x = (0, 1, 1, 0, 1, 0, 0, 1)
        for arm in bayes.ARMS:
            s = bayes.new(arm)
            meter = core.Work()
            choice = bayes.choose(s, x, meter)
            self.assertIn(choice, range(13))
            self.assertLessEqual(meter.count, 8192)
            self.assertTrue(0.1 <= bayes.predict(s, x, choice, core.Work()) <= 0.9)
            self.assertEqual(bayes.unpack(bayes.pack(s)), s)

    def test_do_intervention_skips_mechanism_fit(self):
        s = bayes.new(bayes.ARMS[0])
        before = list(s["scores"][0])
        row = world.HiddenWorld(900033, diagnostic=True).source(0)
        bayes.observe(s, row.context, row.intermediates, 0,
                      row.consequence, core.Work())
        self.assertEqual(s["scores"][0], before)
        self.assertTrue(any(v != 0 for v in s["scores"][6]))

    def test_corruption_and_invalid_mediator_rejection(self):
        s = bayes.new(bayes.ARMS[0])
        raw = bayes.pack(s)
        for corrupt in (raw[:-1], raw + b" ", raw.replace(
                b'"step":0', b'"step":1')):
            with self.assertRaises(ValueError):
                bayes.unpack(corrupt)
        with self.assertRaisesRegex(ValueError, "INVALID_MEDIATOR_OBSERVATION"):
            bayes.observe(s, (0,) * 8, (0,) * 5, 12, 0, core.Work())
        with self.assertRaisesRegex(ValueError, "RULE_BUDGET_EXCEEDED"):
            core.Work().charge(8193)

    def test_diagnostic_model_seed_independent_of_private_world(self):
        a = world.HiddenWorld(900031, diagnostic=True)
        b = world.HiddenWorld(900032, diagnostic=True)
        for arm in core.ARMS:
            s1 = runner._new_model(arm)
            s2 = runner._new_model(arm)
            self.assertEqual(s1["seed"], s2["seed"])
            self.assertNotIn(s1["seed"], (a.seed, b.seed))
        self.assertTrue(set(runner.MODEL_ARMS) >= set(bayes.ARMS))
