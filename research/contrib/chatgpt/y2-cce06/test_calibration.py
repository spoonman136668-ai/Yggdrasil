"""CCE06 tiny engineering fixtures ONLY; no frozen CAL or PRIMARY sampling."""
import copy
import unittest

from calibration_worlds import (
    FIXTURE_SEED, FAMILIES, SEEDS, _rng, _step, oracle_alias_contrast,
    public_trace, source_identity, validate_public_trace,
)
from calibration_controls import ActionHMM, FullSuffixTable, multichannel_brier, validated


class CCE06CalibrationFixtures(unittest.TestCase):
    def fixture(self, family="local_reversible", n=20):
        return public_trace(family, FIXTURE_SEED, "fixture", n)

    def test_no_calibration_sampling_without_pinned_source_lock(self):
        with self.assertRaises(PermissionError):
            public_trace(FAMILIES[0], SEEDS[0], "train", 5000)
        with self.assertRaises(ValueError):
            public_trace(FAMILIES[0], FIXTURE_SEED, "fixture", 33)
        with self.assertRaises(ValueError):
            public_trace(FAMILIES[0], 999, "fixture", 10)
        with self.assertRaises(PermissionError):
            public_trace(FAMILIES[0], SEEDS[0], "cal_eval", 1000,
                         source_lock={"generator_sha256": source_identity()["generator_sha256"]})

    def test_fixture_public_only_and_exact_reproducibility(self):
        for family in FAMILIES:
            first = self.fixture(family)
            self.assertEqual(first, self.fixture(family))
            self.assertEqual(20, len(first))
            validate_public_trace(first)
            self.assertTrue(all(set(e) == {"observation", "action", "next_observation"} for e in first))
            self.assertTrue(all(e["observation"] == first[i - 1]["next_observation"]
                                for i, e in enumerate(first) if i))
            self.assertTrue(all(type(v) is int for e in first
                                for v in e["next_observation"]))

    def test_action_null_counterfactual_action_independence(self):
        state = (0, 1, 0)
        expected = _step("action_null", state, 0, _rng("action_null", 997, "fixture", "latent"))
        for action in (1, 2):
            self.assertEqual(expected, _step("action_null", state, action,
                             _rng("action_null", 997, "fixture", "latent")))

    def test_observational_alias_has_intervention_contrast(self):
        proof = oracle_alias_contrast()
        self.assertTrue(proof["passive_equal"])
        self.assertTrue(proof["probe2_contrast"])
        self.assertTrue(proof["is_evaluator_only"])

    def test_malformed_private_or_corrupt_event_rejected(self):
        e = list(self.fixture())
        corrupt = copy.deepcopy(e)
        corrupt[0]["latent"] = [0, 1, 1]
        with self.assertRaises(ValueError):
            validate_public_trace(corrupt)
        with self.assertRaises(ValueError):
            validated(corrupt)
        corrupt = copy.deepcopy(e)
        corrupt[1]["observation"] = [9, 0]
        with self.assertRaises(ValueError):
            validate_public_trace(corrupt)
        with self.assertRaises(ValueError):
            validated(corrupt)
        corrupt = copy.deepcopy(e)
        corrupt[1]["observation"] = [0, 0] if e[0]["next_observation"] != [0, 0] else [1, 1]
        with self.assertRaises(ValueError):
            validate_public_trace(corrupt)

    def test_suffix_baseline_fit_predict_and_untrained_guard(self):
        model = FullSuffixTable(3)
        with self.assertRaises(ValueError):
            model.predict((), 1)
        model.fit([self.fixture("local_reversible"), self.fixture("gated_nonlocal")])
        self.assertEqual(40, model.samples)
        pred = model.predict(self.fixture("local_reversible", 5), 2)
        self.assertEqual(4, len(pred))
        self.assertAlmostEqual(1, sum(pred))
        self.assertTrue(0 <= multichannel_brier(pred, [1, 0]) <= 1)
        with self.assertRaises(ValueError):
            model.fit([self.fixture()])

    def test_hmm_em_uses_public_stream_only_and_normalizes(self):
        tiny = [self.fixture("local_reversible", 16), self.fixture("gated_nonlocal", 16)]
        model = ActionHMM(2, seed=119).fit(tiny, max_iters=5)
        self.assertEqual(32, model.samples)
        self.assertEqual(5, len(model.trace))
        self.assertTrue(all(model.trace[i] >= model.trace[i - 1] - 1e-5
                            for i in range(1, len(model.trace))))
        pred = model.predict(self.fixture("local_reversible", 4), 1)
        self.assertAlmostEqual(1, sum(pred))
        self.assertTrue(all(0 < p < 1 for p in pred))
        self.assertFalse(hasattr(model, "hidden_world_truth"))

    def test_invalid_hmm_and_brier_rejected(self):
        with self.assertRaises(ValueError):
            ActionHMM(1, seed=1)
        with self.assertRaises(ValueError):
            multichannel_brier((0.5, 0.5, 0.5, 0.5), [1, 0])


if __name__ == "__main__":
    unittest.main()
