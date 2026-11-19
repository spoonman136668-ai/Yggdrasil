"""Fixture-only CAP04 checks. Never generate or consume registered DEV seeds."""
import hashlib
import random
import unittest

from yggdrasil.native_context_basis import digest
from yggdrasil.native_predictive_state_split import PredictiveStateSplit


def ident(i):
    return hashlib.sha256(f"cap04-engineering-fixture-only:{i}".encode("ascii")).hexdigest()


VIEWS = ((0, 0), (0, 0))


class PredictiveStateSplitFixtureTests(unittest.TestCase):
    def test_forecast_stage_clock_and_read_purity(self):
        model = PredictiveStateSplit()
        before = model.checkpoint()
        self.assertEqual(model.forecast(VIEWS, (0, 1), "transition"), .5)
        self.assertEqual(model.forecast(VIEWS, (0, 1), "residual", 1), .5)
        with self.assertRaisesRegex(ValueError, "FUTURE_SENSOR"):
            model.forecast(VIEWS, (0, 1), "transition", 1)
        with self.assertRaisesRegex(ValueError, "BIT"):
            model.forecast(VIEWS, (0, 1), "residual")
        self.assertEqual(model.checkpoint(), before)

    def test_actual_witnesses_train_a_history_feature(self):
        model = PredictiveStateSplit()
        rng = random.Random(41)
        previous = (0, 0)
        for i in range(512):
            pair = (rng.randrange(2), rng.randrange(2))
            # The target depends on the prior actual observed action, not a label.
            sensor = previous[0]
            reward = sensor ^ previous[1]
            model.observe(ident(i), VIEWS, pair, sensor, reward, (0, sensor, 0))
            previous = pair
        self.assertEqual(model.count, 512)
        self.assertEqual(model.selected_feature("transition"), "previous_pair")
        self.assertEqual(model.selected_feature("residual"), "previous_pair")
        forecast = model.forecast(VIEWS, (1, 0), "transition")
        if previous[0]:
            self.assertGreater(forecast, .80)
        else:
            self.assertLess(forecast, .20)
        raw = model.checkpoint()
        self.assertEqual(model.checkpoint(), raw)
        clone = PredictiveStateSplit.restore(raw, digest(raw))
        self.assertEqual(clone.checkpoint(), raw)
        self.assertEqual(clone.forecast(VIEWS, (1, 0), "transition"), forecast)

    def test_duplicate_invalid_post_and_cold_tampering_fail_closed(self):
        model = PredictiveStateSplit()
        model.observe(ident(0), VIEWS, (0, 0), 0, 1, (0, 0, 0))
        pristine = model.checkpoint()
        for action in (
            lambda: model.observe(ident(0), VIEWS, (0, 0), 0, 1, (0, 0, 0)),
            lambda: model.observe(ident(1), VIEWS, (0, 0), 0, 1, (0, 1, 0)),
            lambda: model.observe(ident(1), VIEWS, (0, 0), 0, 1, (0, 0, 2)),
        ):
            with self.assertRaises(ValueError):
                action()
            self.assertEqual(model.checkpoint(), pristine)
        forged = pristine.replace(b'"schema"', b'"not_schema"')
        with self.assertRaisesRegex(ValueError, "COLD_HASH"):
            PredictiveStateSplit.restore(forged, digest(pristine))
        with self.assertRaisesRegex(ValueError, "COLD_REJECTED"):
            PredictiveStateSplit.restore(forged, digest(forged))

    def test_existing_native_legacy_views_import_without_mutation(self):
        # Historic native public sensors can have two independent views.
        old = ((ident(700), ((0, 0), (1, 1)), 0, 1, 0, 1, (0, 1, 0)),
               (ident(701), ((0, 1), (0, 0)), 1, 0, 1, 0, (0, 0, 1)))
        before = repr(old)
        model = PredictiveStateSplit.from_native_events(old)
        self.assertEqual(model.count, 2)
        self.assertEqual(repr(old), before)
        raw = model.checkpoint()
        self.assertEqual(PredictiveStateSplit.restore(raw, digest(raw)).checkpoint(), raw)

    def test_sham_history_is_deliberately_misaligned(self):
        valid = PredictiveStateSplit()
        sham = PredictiveStateSplit(sham=True)
        for i in range(64):
            pair = (i // 3 % 2, i // 7 % 2)
            sensor = (i // 5) % 2
            for learner in (valid, sham):
                learner.observe(ident(i), VIEWS, pair, sensor, sensor,
                                (0, sensor, 0))
        self.assertNotEqual(valid.checkpoint(), sham.checkpoint())
        raw = sham.checkpoint()
        self.assertEqual(PredictiveStateSplit.restore(raw, digest(raw)).checkpoint(), raw)


if __name__ == "__main__":
    unittest.main()
