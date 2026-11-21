"""Gate28 bounded dictionary-coverage negative diagnostics; no primary seeds."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "research/contrib/chatgpt/self-assembling-topologies/gate28"))
import core
import sparse_bayes
import world


class TestGate28SparseBayes(unittest.TestCase):
    def test_full_grammar_reachable_under_bounded_state(self):
        self.assertEqual(sum(sparse_bayes.SIZES), 11424)
        self.assertEqual(len(sparse_bayes.BANKS), 7)
        self.assertEqual(sparse_bayes.PROBES_PER_NODE, 64)
        self.assertEqual(sparse_bayes.BEAM_SIZE, 16)
        for arm in sparse_bayes.ARMS:
            s = sparse_bayes.new(arm)
            self.assertLess(len(sparse_bayes.pack(s)), 16384)

    def test_resource_and_reproducible_full_course(self):
        d = sparse_bayes.diagnostic()
        self.assertEqual(d["status"], "G28_BUDGET_BAYES_DIAGNOSTIC_PASS")
        self.assertEqual(d["steps"], 224)
        self.assertLessEqual(d["maximum_work"], 8192)
        self.assertLessEqual(d["checkpoint_bytes"], 16384)
        self.assertFalse(d["primary_scored"])
        self.assertEqual(d["strength_vs_fully_trained_control"], "UNVERIFIED")
        self.assertEqual(sparse_bayes.diagnostic(), d)

    def test_intervention_skips_fitting_do_mediator(self):
        x = world.HiddenWorld(900029, diagnostic=True).source(0)
        s = sparse_bayes.new(sparse_bayes.ARMS[0])
        sparse_bayes.observe(s, x.context, x.intermediates, 0,
                             x.consequence, core.Work())
        self.assertEqual(s["cursor"][0], 0)
        self.assertEqual(s["beam"][0], [])
        self.assertEqual(s["cursor"][6], 64)
        self.assertGreater(len(s["beam"][6]), 0)

    def test_public_only_cold_source_and_corruption(self):
        s = sparse_bayes.new(sparse_bayes.ARMS[1])
        w = world.HiddenWorld(900041, diagnostic=True)
        for step in range(96):
            row = w.source(step)
            meter = core.Work()
            sparse_bayes.observe(s, row.context, row.intermediates,
                                 row.action, row.consequence, meter)
            self.assertLessEqual(meter.count, 8192)
        sparse_bayes.seal_source(s)
        before = sparse_bayes.source_predict(s, (0,) * 8, 12, core.Work())
        digest = s["source"]["digest"]
        cold = sparse_bayes.unpack(sparse_bayes.pack(s))
        for step in range(16):
            row = w.feedback("B", step, step % 13)
            sparse_bayes.observe(cold, row.context, row.intermediates,
                                 row.action, row.consequence, core.Work())
        self.assertEqual(sparse_bayes.source_predict(
            cold, (0,) * 8, 12, core.Work()), before)
        self.assertEqual(cold["source"]["digest"], digest)
        bad = bytearray(sparse_bayes.pack(cold))
        bad[25] ^= 1
        with self.assertRaises(ValueError):
            sparse_bayes.unpack(bytes(bad))
        with self.assertRaises(ValueError):
            sparse_bayes.unpack(b'X' * 16385)

    def test_invalid_consequence_mediator_and_duplicate_particle(self):
        s = sparse_bayes.new(sparse_bayes.ARMS[0])
        with self.assertRaisesRegex(ValueError, "INVALID_PUBLIC_MEDIATOR"):
            sparse_bayes.observe(s, (0,) * 8, (0,) * 5, 12, 0,
                                 core.Work())
        with self.assertRaisesRegex(ValueError, "INVALID_CONSEQUENCE"):
            sparse_bayes.observe(s, (0,) * 8, (0,) * 6, 12, 2,
                                 core.Work())
        s["beam"][0] = [[0, 1, 1], [0, 1, 1]]
        with self.assertRaisesRegex(ValueError, "SPARSE_DUPLICATE_PARTICLE"):
            sparse_bayes.pack(s)

    def test_eig_and_reward_action_budgets(self):
        for arm in sparse_bayes.ARMS:
            s = sparse_bayes.new(arm)
            for t in range(32):
                x = core.as_bits((t * 19) % 256)
                bits = (0, 1, 0, 1, 1, 0)
                work = core.Work()
                a = sparse_bayes.choose(s, x, work)
                p = sparse_bayes.predict(s, x, a, work)
                self.assertTrue(0.0 <= p <= 1.0)
                sparse_bayes.observe(s, x, bits, a, t % 2, work)
                self.assertLessEqual(work.count, 8192)
            self.assertLessEqual(len(sparse_bayes.pack(s)), 16384)
