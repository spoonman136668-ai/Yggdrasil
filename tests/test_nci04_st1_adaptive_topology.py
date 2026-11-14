"""ST1 bounded structural adaptation mechanical DEV checks only.

No external environment reset, original first-use, model-science evaluation,
source-private information, controller operation or hidden causal oracle.
"""
import json
import unittest
from research.nci04_s1.local_messages import LocalPredictiveMessages45
from research.nci04_st1.adaptive_topology import (
    NativeAdaptiveTopology45, WINDOW, MAX_SWITCHES, options, canonical
)

class ST1Mechanical(unittest.TestCase):
    def setUp(self):
        self.parent = LocalPredictiveMessages45()
        self.m = NativeAdaptiveTopology45(self.parent.snapshot())
        self.raw = tuple([0] * 24)
        self.bits = tuple([0] * 8)
        self.outcomes = tuple([0] * 8)

    def test_original_ring_inference_equal_and_capacity_explicit(self):
        self.assertEqual(self.m.predict(self.raw, self.bits, 0),
                         self.parent.predict(self.raw, self.bits, 0))
        self.assertEqual(self.m.graph(), self.parent.runtime.neighbors)
        self.assertEqual(len(self.m.graph()), 8)
        self.assertTrue(all(len(g) == 2 and g[0] != g[1] and i not in g
                            for i, g in enumerate(self.m.graph())))
        a = self.m.accounting()
        self.assertEqual(a["original_neural_coefficients"], 45)
        self.assertEqual(a["inference_neighbor_scalar_reads"], 16)
        self.assertEqual(a["extra_training_candidate_scalar_reads"], 64)
        self.assertEqual(a["extra_score_float64_equivalent_bytes"], 256)
        self.assertFalse(a["scientific_first_use_qualified"])

    def test_frozen_hysteresis_and_absolute_reconfiguration_budget(self):
        # Hand-set score register is an arithmetic fixture, not experiment.
        self.m.losses[0] = [3.0, 0.0, 2.0, 2.0]
        self.m.window_seen = WINDOW
        self.m._finish_window()
        self.assertEqual(self.m.choices[0], 1)
        self.assertEqual(self.m.graph()[0], options(0)[1])
        self.m.losses[0] = [0.0, 3.0, 2.0, 2.0]
        self.m.window_seen = WINDOW
        self.m._finish_window()
        self.assertEqual(self.m.choices[0], 0)
        self.assertEqual(self.m.switches[0], MAX_SWITCHES)
        self.m.losses[0] = [3.0, 0.0, 2.0, 2.0]
        self.m.window_seen = WINDOW
        self.m._finish_window()
        self.assertEqual(self.m.choices[0], 0)
        self.assertEqual(self.m.switches[0], MAX_SWITCHES)
        self.assertEqual(self.m.accounting()["edge_reconfigurations"], 2)

    def test_measured_toy_feedback_without_weight_edits_or_fake_specialization(self):
        first = self.m.native.runtime.core.snapshot()
        for _ in range(WINDOW):
            self.m.reset_episode()
            p = self.m.observe(self.raw, self.bits, 0,
                               self.outcomes, train=True)
            self.assertEqual(len(p), 8)
        self.assertEqual(self.m.choices, [0] * 8)
        self.assertEqual(self.m.switches, [0] * 8)
        self.assertEqual(self.m.window_seen, 0)
        self.assertEqual(self.m.total_windows, 1)
        self.assertEqual(self.m.native.runtime.core.snapshot(), first)
        choice = self.m.choices[:]
        losses = [r[:] for r in self.m.losses]
        self.m.observe(self.raw, self.bits, 0, self.outcomes, train=False)
        self.assertEqual((choice, losses), (self.m.choices, self.m.losses))
        self.assertEqual(self.m.native.runtime.core.snapshot(), first)

    def test_canonical_cold_restore_and_invalid_public_calls_are_atomic(self):
        self.m.observe(self.raw, self.bits, 0, self.outcomes, train=True)
        snap = self.m.snapshot()
        self.assertEqual(NativeAdaptiveTopology45.restore(snap).snapshot(), snap)
        for thunk in (
            lambda: self.m.observe(self.raw[:-1], self.bits, 0,
                                   self.outcomes),
            lambda: self.m.observe(self.raw, self.bits, 0,
                                   self.outcomes[:-1]),
            lambda: self.m.observe(self.raw, self.bits, 0,
                                   self.outcomes, train=1),
            lambda: self.m.predict(self.raw, self.bits, 7),
        ):
            with self.assertRaises(ValueError):
                thunk()
            self.assertEqual(self.m.snapshot(), snap)
        for change in (
            lambda d: d.update(schema="broken"),
            lambda d: d["choices"].__setitem__(0, 4),
            lambda d: d["losses"][0].__setitem__(0, -1.0),
            lambda d: d["switches"].__setitem__(0, 3),
            lambda d: d.update(weights_sha256="0" * 64),
        ):
            altered = json.loads(snap)
            change(altered)
            with self.assertRaises(ValueError):
                NativeAdaptiveTopology45.restore(canonical(altered))

if __name__ == "__main__":
    unittest.main()
