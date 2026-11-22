"""Source-free deterministic CPR-01 contract tests; NOT scientific acceptance."""
import importlib.util
from hashlib import sha256
from pathlib import Path
import sys
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "research/contrib/chatgpt/CPR-01/router.py")
spec = importlib.util.spec_from_file_location("cpr01_source", SOURCE)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def modules():
    a = m.FrozenCalibration.from_holdout(
        "A", "a" * 64, "1" * 64, [900_000] * 128, [1] * 128,
        alpha_percent=10)
    b = m.FrozenCalibration.from_holdout(
        "B", "b" * 64, "2" * 64, [100_000] * 128, [0] * 128,
        alpha_percent=10)
    return (a, b)


class CPR01ContractTests(unittest.TestCase):
    def test_exact_finite_sample_rank_and_infinity(self):
        a, b = modules()
        self.assertEqual((a.threshold, b.threshold), (100_000, 100_000))
        low_n = m.FrozenCalibration.from_holdout(
            "short", "c" * 64, "3" * 64, [900_000], [1], alpha_percent=5)
        self.assertEqual(low_n.threshold, m.SCALE + 1)
        with self.assertRaisesRegex(ValueError, "CALIBRATION_LENGTH"):
            m.FrozenCalibration.from_holdout(
                "bad", "d" * 64, "4" * 64, [500_000], [], alpha_percent=10)

    def test_abstain_and_revival_without_oracle(self):
        router = m.ConformalRouter(modules(), window=8)
        predictions = {"A": 900_000, "B": 100_000}
        for _ in range(16):
            decision = router.route(predictions)
            self.assertEqual(decision["selected"], "A")
            router.observe(1)
        seen_b = False
        for _ in range(16):
            decision = router.route(predictions)
            seen_b |= decision["selected"] == "B"
            router.observe(0)
        self.assertTrue(seen_b)
        revival = None
        for index in range(1, 17):
            decision = router.route(predictions)
            if decision["selected"] == "A" and revival is None:
                revival = index
            router.observe(1)
        self.assertIsNotNone(revival)
        self.assertLessEqual(revival, 12)

    def test_past_only_feedback_and_no_replay(self):
        router = m.ConformalRouter(modules())
        p = {"A": 900_000, "B": 100_000}
        first = router.route(p)
        self.assertEqual(first["selected"], "A")
        p["A"] = 100_000
        with self.assertRaisesRegex(ValueError, "PENDING"):
            router.route(p)
        router.observe(1)
        self.assertEqual(list(router.history["A"]), [1])
        with self.assertRaisesRegex(ValueError, "UNMATCHED"):
            router.observe(1)
        with self.assertRaisesRegex(ValueError, "LABEL"):
            router.route({"A": 900_000, "B": 100_000})
            router.observe(2)

    def test_exact_sidecar_restore_and_model_pin_guard(self):
        source = modules()
        router = m.ConformalRouter(source)
        for outcome in (1, 0, 1):
            router.route({"A": 900_000, "B": 100_000})
            router.observe(outcome)
        raw = router.checkpoint()
        pin = sha256(raw).hexdigest()
        expected = {c.name: c.model_sha256 for c in source}
        restored = m.ConformalRouter.restore(raw, pin, model_pins=expected)
        self.assertEqual(restored.checkpoint(), raw)
        with self.assertRaisesRegex(ValueError, "SIDECAR_INVALID"):
            m.ConformalRouter.restore(raw, pin, model_pins={"A": "f" * 64})
        with self.assertRaisesRegex(ValueError, "SIDECAR_PIN"):
            m.ConformalRouter.restore(raw + b"x", pin, model_pins=expected)

    def test_single_step_abstains_after_first_miss(self):
        router = m.ConformalRouter(modules(), window=1)
        router.route({"A": 900_000, "B": 100_000})
        router.observe(1)
        decision = router.route({"A": 900_000, "B": 100_000})
        self.assertEqual(decision["selected"], "A")
        router.observe(0)
        decision = router.route({"A": 900_000, "B": 100_000})
        self.assertEqual(decision["selected"], "B")

    def test_clustered_ten_percent_noise_falsifies_no_false_spawn(self):
        # Eight contaminated observations, exactly 10% of an 80-step stream.
        # This is a negative control, not a claimed success or original-world run.
        two_alike = (
            m.FrozenCalibration.from_holdout(
                "A", "a" * 64, "1" * 64, [900_000] * 128,
                [1] * 128, alpha_percent=10),
            m.FrozenCalibration.from_holdout(
                "C", "c" * 64, "3" * 64, [900_000] * 128,
                [1] * 128, alpha_percent=10))
        router = m.ConformalRouter(two_alike, window=8)
        alerts = 0
        for outcome in [1] * 64 + [0] * 8 + [1] * 8:
            decision = router.route({"A": 900_000, "C": 900_000})
            alerts += int(decision["speciation_signal"])
            router.observe(outcome)
        self.assertEqual(alerts, 1, "Expected a single false-speciation counterexample")

    def test_bad_inputs_rejected_without_checkpoint_change(self):
        router = m.ConformalRouter(modules())
        baseline = router.checkpoint()
        for predictions in ({"A": 2, "B": -1},
                            {"A": 700_000}, {"A": 0.9, "B": 500_000}):
            with self.assertRaises(ValueError):
                router.route(predictions)
        self.assertEqual(router.checkpoint(), baseline)


if __name__ == "__main__":
    unittest.main()
