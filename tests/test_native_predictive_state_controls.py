"""CAP04 engineering-only conventional controls; reserved DEV sources never read."""
import hashlib
import json
import random
import unittest
from yggdrasil.native_context_basis import digest
from yggdrasil.native_predictive_state_controls import ARMS, MatchedHistoryControls
from yggdrasil.native_predictive_state_split import PredictiveStateSplit

VIEWS = ((0, 0), (0, 0))

def uid(i):
    return hashlib.sha256(f"cap04-control-fixture-004/{i}".encode()).hexdigest()

class MatchedControlFixtureTests(unittest.TestCase):
    def test_exact_arms_cold_and_no_future_peek(self):
        m = MatchedHistoryControls()
        b = m.checkpoint()
        self.assertEqual(set(m.forecast(VIEWS, (0, 1), "transition")), set(ARMS))
        self.assertTrue(all(p == .5 for p in m.forecast(VIEWS, (0, 1), "transition").values()))
        self.assertEqual(m.checkpoint(), b)
        with self.assertRaisesRegex(ValueError, "FUTURE_SENSOR"):
            m.forecast(VIEWS, (0, 1), "transition", 0)
        with self.assertRaisesRegex(ValueError, "BIT"):
            m.forecast(VIEWS, (0, 1), "residual")
        for i in range(12):
            a = (i % 2, i // 3 % 2)
            v = i // 2 % 2
            m.observe(uid(i), VIEWS, a, v, v ^ (i % 2), (0, v, 0))
        raw = m.checkpoint()
        self.assertEqual(MatchedHistoryControls.restore(raw, digest(raw)).checkpoint(), raw)
        for stage, sensor in (("transition", None), ("residual", 1)):
            old = m.forecast(VIEWS, (1, 0), stage, sensor)
            new = MatchedHistoryControls.restore(raw, digest(raw)).forecast(VIEWS, (1, 0), stage, sensor)
            for a in ARMS:
                self.assertAlmostEqual(old[a], new[a], places=12)

    def test_distinct_strong_fitted_controls_and_stage2_sensor(self):
        m = MatchedHistoryControls()
        rng = random.Random(510)
        prior = (0, 0)
        for i in range(192):
            action = (rng.randrange(2), rng.randrange(2))
            s2 = prior[0]
            reward = s2 ^ action[0]
            m.observe(uid(i), VIEWS, action, s2, reward, (0, s2, 0))
            prior = action
        self.assertEqual(m.count, 192)
        transition = m.forecast(VIEWS, (1, 0), "transition")
        self.assertGreater(abs(transition["history_order1_Beta"] - transition["full_history_exact_state_action_Beta"]), .05)
        self.assertTrue(all(0 <= p <= 1 for p in transition.values()))
        first = m.forecast(VIEWS, (1, 0), "residual", 0)
        second = m.forecast(VIEWS, (1, 0), "residual", 1)
        self.assertNotEqual(first["full_history_exact_state_action_Beta"], second["full_history_exact_state_action_Beta"])

    def test_common_source_prequential_and_late_labels_no_lookahead(self):
        m = MatchedHistoryControls()
        n = PredictiveStateSplit()
        for i in range(80):
            a = (i % 2, (i // 2) % 2)
            v = i // 3 % 2
            before = m.checkpoint(), n.checkpoint()
            left = m.forecast(VIEWS, a, "transition")
            p = n.forecast(VIEWS, a, "transition")
            q = m.forecast(VIEWS, a, "residual", v)
            # Readouts cannot mutate history or ingest the simulated reward.
            self.assertEqual(before, (m.checkpoint(), n.checkpoint()))
            self.assertTrue(all(0 <= x <= 1 for x in (*left.values(), p, *q.values())))
            m.observe(uid(i), VIEWS, a, v, v, (0, v, 0))
            n.observe(uid(i), VIEWS, a, v, v, (0, v, 0))
        self.assertEqual(m.count, n.count)
        self.assertEqual(m.count, 80)

    def test_atomic_duplicate_bad_post_and_native_ledger_preservation(self):
        old = ((uid(600), ((0, 1), (1, 0)), 1, 1, 0, 0, (0, 1, 1)),
               (uid(601), ((0, 0), (1, 0)), 1, 0, 1, 1, (1, 0, 1)))
        original = repr(old)
        m = MatchedHistoryControls.from_native_events(old)
        self.assertEqual(original, repr(old))
        self.assertEqual(m.count, 2)
        readout = m.checkpoint()
        for args in ((uid(600), VIEWS, (1, 0), 1, 0, (0, 1, 0)),
                     (uid(602), VIEWS, (1, 0), 1, 0, (0, 0, 0)),
                     (uid(602), VIEWS, (1, 0), 1, 2, (0, 1, 0))):
            with self.assertRaises(ValueError):
                m.observe(*args)
            self.assertEqual(m.checkpoint(), readout)
        forged = readout.replace(b'"schema"', b'"bad"')
        with self.assertRaisesRegex(ValueError, "COLD_HASH"):
            MatchedHistoryControls.restore(forged, digest(readout))
        with self.assertRaisesRegex(ValueError, "COLD_REJECTED"):
            MatchedHistoryControls.restore(forged, digest(forged))

# Engineering negative: old source rows lack a post triple. Never invent it.
class HistoricalMissingPublicFieldsFixtureTests(unittest.TestCase):
    def test_public_history_absent_post_is_explicitly_masked_and_cold(self):
        old6 = ((uid(900), ((0,0),(1,0)), 1, 0, 0, 1),
                (uid(901), ((0,1),(1,1)), 0, 1, 1, 0))
        old7 = ((uid(902), ((0,0),(0,0)), 0, 1, 1, 0, (0,1,0)),)
        combined = old6 + old7
        for model_class in (MatchedHistoryControls, PredictiveStateSplit):
            m = model_class.from_native_events(combined)
            self.assertEqual(m.count, 3)
            self.assertIsNone(m._events[0][5])
            self.assertIsNone(m._events[1][5])
            self.assertEqual(m._events[2][5], (0, 1, 0))
            before = m.checkpoint()
            self.assertEqual(model_class.restore(before, digest(before)).checkpoint(), before)
            with self.assertRaisesRegex(ValueError, "MISSING_POST_NOT_LEGACY"):
                m.observe(uid(903), VIEWS, (0,0), 1, 0, None)
            self.assertEqual(m.checkpoint(), before)

if __name__ == '__main__': unittest.main()
