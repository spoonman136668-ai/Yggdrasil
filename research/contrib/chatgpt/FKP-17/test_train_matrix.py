"""FKP-17 frozen known TRAIN matrix bootstrap, source and timing negative gates.

No protected FKP17 DEV or TRANSFER world is instantiated here. The source-safe
fully trained recurrent checkpoint is loaded only in the separate real runner.
"""
from collections import OrderedDict
import math
from pathlib import Path
import unittest

import blind_public_harness as blind
import run_train_matrix as matrix
import source_fixture as fixture


class Fake:
    def __init__(self):
        self.updates = 0
        self.choices = 0

    def begin_world(self):
        self.updates = 0
        self.choices = 0

    def choose_public(self, state):
        assert len(state) == 8
        self.choices += 1
        return 0

    def observe_public(self, row):
        self.updates += 1

    def state_receipt(self):
        return "f" * 64


class MatrixSafetyTests(unittest.TestCase):
    def test_locked_train_seed_range_before_any_run(self):
        lock = matrix._load_lock()
        self.assertEqual((lock["seed_schedule"]["start"], lock["seed_schedule"]["end"]),
                         (978100, 978163))
        self.assertEqual(len(matrix.TRIALS), 64)
        self.assertEqual(matrix.TRIALS[0], 978100)
        self.assertEqual(matrix.TRIALS[-1], 978163)
        self.assertEqual(tuple(lock["arms"]), blind.ARMS)
        self.assertEqual(lock["primary_known_family_diagnostic"]["bootstrap_draws"], 10000)
        self.assertEqual(lock["primary_known_family_diagnostic"]["bootstrap_seed"], 1515)
        self.assertTrue(lock["held_source_rules"]["no_dev"])
        self.assertTrue(lock["held_source_rules"]["no_reserved_transfer"])

    def test_source_safe_before_checkpoint_read_denies_missing(self):
        # A missing/invalid local checkpoint must fail before any environment.
        with self.assertRaises(ValueError):
            matrix.evaluate_known_train_matrix(
                "not-a-real-checkpoint-no-file-fkp17")
        for forbidden in (978500, 978600, 976500, 979100):
            with self.assertRaises(PermissionError):
                fixture.PublicSession(forbidden)
        self.assertTrue(all(fixture.cohort(seed) == "TRAIN"
                            for seed in matrix.TRIALS))

    def test_timer_counts_only_real_action_and_feedback_events(self):
        wrapped = matrix.TimedPublicArm(Fake())
        wrapped.begin_world()
        state = (0,) * 8
        self.assertEqual(wrapped.choose_public(state), 0)
        row = fixture.collect_public(fixture.TRAIN[0], (0,))[0]
        wrapped.observe_public(row)
        self.assertEqual(wrapped.impl.choices, 1)
        self.assertEqual(wrapped.impl.updates, 1)
        with self.assertRaisesRegex(ValueError, "PHYSICAL_ACTION_COUNT"):
            wrapped.timings()
        for _ in range(15):
            wrapped.choose_public(state)
        for _ in range(39):
            wrapped.observe_public(row)
        result = wrapped.timings()
        self.assertEqual(result["inference_calls"], 16)
        self.assertEqual(result["public_observations"], 40)
        self.assertGreaterEqual(result["inference_cpu_seconds"], 0.0)
        self.assertGreaterEqual(result["update_wall_seconds"], 0.0)

    def test_frozen_paired_bootstrap_correctly_reselects_best_control(self):
        data = OrderedDict()
        for seed in matrix.TRIALS:
            data[seed] = {name: 0.5 for name in blind.ARMS}
            data[seed]["STRUCTURED"] = 1.0
            data[seed]["MINIMAL"] = 1.5
        primary = matrix._load_lock()["primary_known_family_diagnostic"]
        report = matrix.paired_bootstrap(
            data, draws=10000, seed=1515, candidate="STRUCTURED",
            control_names=primary["matched_information_controls"])
        self.assertEqual(report["means"]["STRUCTURED"], 1.0)
        self.assertEqual(report["paired_gain_vs_strongest_control"], 0.5)
        self.assertEqual(report["paired_gain_vs_minimal_prior_ablation"], -0.5)
        self.assertEqual(report["reselected_control_world_bootstrap_95_ci"], [0.5, 0.5])
        self.assertFalse(report["scientific_pass"])
        self.assertTrue(report["known_family_only"])

    def test_bootstrap_rejects_missing_arm_missing_seed_or_reordered_trial(self):
        data = OrderedDict((seed, {name: 0.0 for name in blind.ARMS})
                           for seed in matrix.TRIALS)
        names = ("FLAT", "SHUFFLED", "BAYES_SYMBOLIC")
        with self.assertRaisesRegex(ValueError, "FROZEN_BOOTSTRAP"):
            matrix.paired_bootstrap(data, draws=100, control_names=names)
        with self.assertRaisesRegex(ValueError, "CONTROL_SELECTION_INVALID"):
            matrix.paired_bootstrap(data, control_names=("STRUCTURED",))
        missing = dict(data)
        missing.pop(matrix.TRIALS[-1])
        with self.assertRaisesRegex(ValueError, "MISSING_OR_REORDERED"):
            matrix.paired_bootstrap(missing, control_names=names)
        swapped = OrderedDict(reversed(tuple(data.items())))
        with self.assertRaisesRegex(ValueError, "MISSING_OR_REORDERED"):
            matrix.paired_bootstrap(swapped, control_names=names)
        corrupt = OrderedDict((k, dict(v)) for k, v in data.items())
        corrupt[matrix.TRIALS[0]].pop("BAYES_SYMBOLIC")
        with self.assertRaisesRegex(ValueError, "INCOMPLETE_ARM_SCORES"):
            matrix.paired_bootstrap(corrupt, control_names=names)

    def test_nan_or_unknown_reward_cannot_be_summarized(self):
        data = OrderedDict((seed, {name: 0.0 for name in blind.ARMS})
                           for seed in matrix.TRIALS)
        data[matrix.TRIALS[8]]["STRUCTURED"] = math.nan
        with self.assertRaisesRegex(ValueError, "NONFINITE_RETURN"):
            matrix.paired_bootstrap(data, control_names=("FLAT",))
        self.assertEqual(matrix._model_bytes(
            type("Good", (), {"learned_bytes": 8384})()), 8384)
        for bad in (-1, 0, 1048577, 1.0, None):
            with self.assertRaisesRegex(ValueError, "MODEL_CAPACITY"):
                matrix._model_bytes(
                    type("Bad", (), {"learned_bytes": bad})())

    def test_no_rescoring_scientific_thresholds_or_private_source_entry(self):
        raw = Path(matrix.__file__).read_text("utf-8")
        self.assertIn("KNOWN_TRAIN_ONLY_NOT_UNFAMILIAR_LAW_SCIENCE", raw)
        self.assertIn("scientific_pass", raw)
        self.assertNotIn("def open_dev(", raw)
        self.assertNotIn("allow_dev=True", raw)
        self.assertNotIn("978500..978531", raw)
        self.assertNotIn("first_use()", raw)
        self.assertNotIn("def retune(", raw)


if __name__ == "__main__":
    unittest.main()
