"""MH-08 source-free mechanical fixtures: no trial/world generation."""
import json
import unittest
from research.mh08_meta_hebbian import LocalPlasticity


class MH08SourceOnly(unittest.TestCase):
    def test_prediction_is_causal_and_no_lookahead(self):
        m = LocalPlasticity()
        self.assertEqual(m.begin(0, (1, .5, 0, 0)), (0., 0., 0.))
        self.assertEqual(m.predict((1, .5, 0, 0)), (0., 0., 0.))
        with self.assertRaisesRegex(ValueError, "MID_EVENT"):
            m.checkpoint()
        m.feedback(0, (1, 0, -1))
        self.assertGreater(m.predict((1, .5, 0, 0))[0], 0)
        self.assertLess(m.predict((1, .5, 0, 0))[2], 0)

    def test_modulation_required_and_local_importance_ablation(self):
        normal = LocalPlasticity()
        unprotected = LocalPlasticity(metaplastic=False)
        frozen = LocalPlasticity(modulated=False)
        x, y = (1, 0, 0, 0), (1, 0, 0)
        for i in range(4):
            for m in (normal, unprotected, frozen):
                m.begin(i, x)
                m.feedback(i, y)
        self.assertGreater(normal.importance[0][0], 0)
        self.assertEqual(unprotected.importance[0][0], 0.)
        self.assertGreater(unprotected.weights[0][0], normal.weights[0][0])
        self.assertTrue(all(v == 0 for row in frozen.weights for v in row))

    def test_cold_replay_exact_checkpoint_and_forecast(self):
        m = LocalPlasticity()
        for idx, (x, y) in enumerate((((1, 0, 1, 0), (1, .5, -1)), ((1, -1, 0, 1), (-.5, 0, .75)))):
            m.begin(idx, x)
            m.feedback(idx, y)
        raw = m.checkpoint()
        recovered = LocalPlasticity.restore(raw)
        self.assertEqual(raw, recovered.checkpoint())
        self.assertEqual(m.predict((1, .4, -.1, .2)), recovered.predict((1, .4, -.1, .2)))
        m.begin(2, (1, 0, 0, 0))
        recovered.begin(2, (1, 0, 0, 0))
        m.feedback(2, (0, 1, -1))
        recovered.feedback(2, (0, 1, -1))
        self.assertEqual(m.checkpoint(), recovered.checkpoint())

    def test_ordering_duplicates_and_outcome_recovery(self):
        m = LocalPlasticity()
        for bad in (-1, True, 1, 0.0):
            with self.assertRaises(ValueError):
                m.begin(bad, (1, 0, 0, 0))
        with self.assertRaises(ValueError):
            m.feedback(0, (0, 0, 0))
        m.begin(0, (1, 0, 0, 0))
        with self.assertRaises(ValueError):
            m.begin(0, (1, 0, 0, 0))
        with self.assertRaises(ValueError):
            m.feedback(1, (0, 0, 0))
        with self.assertRaises(ValueError):
            m.feedback(0, (float("nan"), 0, 0))
        m.feedback(0, (0, 0, 0))
        with self.assertRaises(ValueError):
            m.feedback(0, (0, 0, 0))
        self.assertEqual(m.next_event_id, 1)

    def test_untrusted_or_private_data_rejected(self):
        m = LocalPlasticity()
        for features in ((1, 0), (1, float("inf"), 0, 0), (True, 0, 0, 0), (2, 0, 0, 0), {"phase": "A"}):
            with self.assertRaises(ValueError):
                m.begin(0, features)
        with self.assertRaises(TypeError):
            m.begin(0, (1, 0, 0, 0), hidden_regime="A")
        self.assertEqual(m.next_event_id, 0)

    def test_invalid_checkpoints_fail_closed(self):
        m = LocalPlasticity()
        good = json.loads(m.checkpoint())
        for field, value in (("schema", "wrong"), ("next_event_id", -1), ("next_event_id", True), ("weights", [[float("nan")]*4]*3), ("importance", [[-1.0]*4]*3)):
            invalid = dict(good)
            invalid[field] = value
            with self.assertRaises(ValueError, msg=field):
                LocalPlasticity.restore(json.dumps(invalid).encode("ascii"))
        with self.assertRaises(ValueError):
            LocalPlasticity.restore(b'{"schema":"truncated"}')
        with self.assertRaises(ValueError):
            LocalPlasticity.restore(b"x" * 8193)

    def test_no_rewards_generated_or_experiment_admitted(self):
        import research.mh08_meta_hebbian as mod
        self.assertEqual(mod.SCHEMA, "yggdrasil.mh08.local-plasticity.eng.v1")
        self.assertFalse(any(hasattr(mod, x) for x in ("run_trial", "reward", "source_adapter", "phase_oracle")))
        self.assertEqual(LocalPlasticity().next_event_id, 0)


if __name__ == "__main__":
    unittest.main()
