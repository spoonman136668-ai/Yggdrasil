"""Gate28 learner integrity and negative diagnostics; zero primary scoring."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "research/contrib/chatgpt/self-assembling-topologies/gate28"))
import core


class TestGate28Core(unittest.TestCase):
    def test_diagnostic(self):
        self.assertFalse(core.diagnostic()["reserved_primary_used"])

    def test_capacity_and_cold_parity(self):
        for arm in core.ARMS:
            s = core.new(900003, arm)
            self.assertLessEqual(len(s["edges"]), core.MAX_EDGES)
            for t in range(96):
                x = core.as_bits((t * 19) & 255)
                w = core.Work()
                a = core.choose(s, x, w)
                core.observe(s, x, a, (t ^ (t >> 2)) & 1, w)
                self.assertLessEqual(w.count, core.MAX_RULE_EVALS)
            core.seal_source(s)
            cold = core.unpack(core.pack(s))
            self.assertEqual(cold, s)
            self.assertEqual(core.choose(s, core.as_bits(51), core.Work()),
                             core.choose(cold, core.as_bits(51), core.Work()))
            self.assertLessEqual(len(core.pack(s)), core.MAX_STATE_BYTES)
            self.assertLessEqual(len(s["edges"]), core.MAX_EDGES)
            self.assertEqual(s["source"]["digest"], cold["source"]["digest"])

    def test_corruption_rejected(self):
        s = core.new(900001, "adaptive")
        wire = core.pack(s)
        with self.assertRaises(ValueError):
            core.unpack(wire[:-1])
        with self.assertRaises(ValueError):
            core.unpack(wire.replace(b'"step":0', b'"step":1'))
        with self.assertRaises(ValueError):
            core.unpack(wire + b' ')
        with self.assertRaises(ValueError):
            core.unpack(b'X' * 16385)
        s["edges"] = [[0, 0, 0.0]] * 65
        with self.assertRaisesRegex(ValueError, "STRUCTURE_CAP_EXCEEDED"):
            core.pack(s)

    def test_fixed_topology_immutable(self):
        s = core.new(900002, "fixed")
        ids = [(a, f) for a, f, _ in s["edges"]]
        for t in range(130):
            core.observe(s, core.as_bits(t % 256), t % 13, t % 2, core.Work())
        self.assertEqual(ids, [(a, f) for a, f, _ in s["edges"]])
        self.assertEqual(s["edits"], 0)
        self.assertEqual(len(ids), 64)

    def test_public_only_and_reject(self):
        s = core.new(900004, "adaptive")
        with self.assertRaisesRegex(ValueError, "INVALID_ACTION"):
            core.predict(s, (0,) * 8, 13, core.Work())
        with self.assertRaisesRegex(ValueError, "INVALID_CONSEQUENCE"):
            core.observe(s, (0,) * 8, 0, 2, core.Work())
        with self.assertRaisesRegex(ValueError, "INVALID_CONTEXT"):
            core.observe(s, (0,) * 7 + (2,), 0, 0, core.Work())
        with self.assertRaisesRegex(ValueError, "RULE_BUDGET_EXCEEDED"):
            core.Work().charge(8193)
        with self.assertRaisesRegex(ValueError, "SOURCE_UNFROZEN"):
            core.source_predict(s, (0,) * 8, 0, core.Work())
        with self.assertRaisesRegex(ValueError, "SOURCE_FREEZE_REQUIRES_96_OBSERVATIONS"):
            core.seal_source(s)

    def test_reproducible_edits_only_on_seen_outcomes(self):
        a = core.new(900005, "adaptive")
        b = core.new(900005, "adaptive")
        for t in range(210):
            x = core.as_bits((t * 23) % 256)
            action = (t // 12) % 13
            y = int(x[0] ^ x[1])
            wa, wb = core.Work(), core.Work()
            core.observe(a, x, action, y, wa)
            core.observe(b, x, action, y, wb)
        self.assertEqual(core.pack(a), core.pack(b))
        self.assertLessEqual(len(a["edges"]), 64)
        self.assertEqual(min(a["edits"], core.EDGE_LOG_LIMIT), len(a["edit_log"]))
        self.assertGreater(a["edits"], 0)
