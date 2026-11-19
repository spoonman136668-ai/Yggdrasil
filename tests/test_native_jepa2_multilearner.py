"""YGG-JEPA2-02: opt-in native multi-learner invariants, no science first-use."""
import json
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience
from yggdrasil.native_jepa2_multilearner import (
    ActionLatentSpecialist, NativeMultiLearner, STEPS,
)


def episode(i):
    c = (i // 3) % 2
    x1 = i % 2
    s2 = (i * 3 // 2) % 2
    x2 = (i // 4) % 2
    y = (c ^ (x1 & s2) ^ x2)
    views = ((c, i % 2), (c, (i // 5) % 2))
    row = {"s1": c, "x1": x1, "s2": s2, "x2": x2, "y": y}
    return digest(canonical(["jepa2-dev-unit", i])), views, row


class NativeMultiLearnerTest(unittest.TestCase):
    def test_native_causal_source_is_byte_identical_and_cold_continuation(self):
        bundle = NativeMultiLearner()
        reference = NativeEpisodeExperience(repair=True)
        first = []
        for i in range(24):
            if i == 8:
                bundle, reference = bundle.begin_stream(), reference.begin_stream()
            identifier, views, row = episode(i)
            forecast = bundle.predict(views, row["x1"], row["s2"], row["x2"],
                                      stream=i >= 8)
            self.assertEqual(
                forecast["native"],
                tuple(float(reference.context_forecast(views[0], row["x1"]))
                      if i >= 8 else float(reference.forecast(views[0], row["x1"]))
                      for _ in range(1))
                + (float(reference.context_forecast(
                    views[0], row["x1"], row["s2"], row["x2"]) if i >= 8
                    else reference.forecast(views[0], row["x1"], row["s2"], row["x2"])),)
            )
            self.assertTrue(all(0 <= p <= 1 for key in forecast for p in forecast[key]))
            next_bundle = bundle.observe(identifier, views, row)
            reference = reference.observe(identifier, views, row)
            self.assertEqual(next_bundle.native.checkpoint(), reference.checkpoint())
            bundle = next_bundle
            if i in (7, 10, 23):
                raw = bundle.checkpoint()
                bundle = NativeMultiLearner.restore(raw, digest(raw))
                self.assertEqual(bundle.checkpoint(), raw)
            first.append(identifier)
        self.assertEqual(bundle.native.info()["count"], 24)
        self.assertEqual(bundle.transition.steps, 24 * STEPS)
        self.assertEqual(bundle.reward.steps, 24 * STEPS)
        self.assertEqual(len(set(first)), 24)
        self.assertEqual(bundle.native.checkpoint(), reference.checkpoint())

    def test_duplicate_idempotence_and_contradiction_atomicity(self):
        bundle = NativeMultiLearner()
        for i in range(8):
            bundle = bundle.observe(*episode(i))
        raw = bundle.checkpoint()
        self.assertIs(bundle.observe(*episode(7)), bundle)
        self.assertEqual(bundle.checkpoint(), raw)
        identifier, views, row = episode(7)
        bad = dict(row)
        bad["y"] ^= 1
        with self.assertRaises(ValueError):
            bundle.observe(identifier, views, bad)
        self.assertEqual(bundle.checkpoint(), raw)

    def test_forged_weights_even_with_valid_new_hash_are_rejected(self):
        bundle = NativeMultiLearner()
        for i in range(10):
            bundle = bundle.observe(*episode(i))
        raw = bundle.checkpoint()
        d = json.loads(raw)
        d["transition"]["encoder"][0][0] += 0.001
        forged = canonical(d)
        with self.assertRaises(ValueError):
            NativeMultiLearner.restore(forged, digest(forged))
        self.assertEqual(NativeMultiLearner.restore(raw, digest(raw)).checkpoint(), raw)

    def test_invalid_public_views_and_teacher_target_fail_closed(self):
        m = ActionLatentSpecialist("transition")
        with self.assertRaises(ValueError):
            m.observe(((0, 1), (0, 2)), (0,), 1)
        with self.assertRaises(ValueError):
            m.observe(((0, 1), (0, 1)), (0,), 2)
        with self.assertRaises(ValueError):
            m.probability(((0, 1), (0, 1)), 2)
        self.assertEqual(m.steps, 0)

    def test_native_model_unmodified_by_specialist_prediction(self):
        bundle = NativeMultiLearner()
        for i in range(12):
            bundle = bundle.observe(*episode(i))
        before = bundle.checkpoint()
        for i in range(8):
            _, views, row = episode(i)
            bundle.predict(views, row["x1"], row["s2"], row["x2"], stream=False)
        self.assertEqual(bundle.checkpoint(), before)


if __name__ == "__main__":
    unittest.main()

