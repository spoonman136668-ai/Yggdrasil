"""Independent source-safe eight-arm chosen-action and temporal seal tests."""
import ast
from hashlib import sha256
from pathlib import Path
import unittest

import blind_public_harness as harness
import source_fixture as fixture


class FakeLearner:
    def __init__(self, action):
        self.action = action
        self.events = []
        self.choices = []
        self.observations = 0

    def begin_world(self):
        self.events = []
        self.choices = []
        self.observations = 0

    def choose_public(self, state):
        if self.observations < 24:
            raise AssertionError("action selected without common exploration")
        if len(state) != 8:
            raise AssertionError("bad public state")
        self.events.append("choose")
        self.choices.append(tuple(state))
        return self.action

    def observe_public(self, row):
        self.events.append("observe")
        self.observations += 1

    def state_receipt(self):
        return sha256(repr((self.action, self.events, self.choices)).encode()).hexdigest()


class BlindActionTests(unittest.TestCase):
    def setUp(self):
        self.seed = fixture.TRAIN[5]
        self.tape = fixture.public_actions(self.seed, 24)
        self.arms = {name: FakeLearner(i % 8)
                     for i, name in enumerate(harness.ARMS)}

    def run_episode(self, factory=None):
        if factory is None:
            factory = lambda: fixture.PublicSession(self.seed)
        return harness.evaluate_training_fixture(factory, self.tape,
                                                 self.arms, self.seed)

    def test_all_eight_actions_committed_before_selected_outcome(self):
        record = self.run_episode()
        self.assertEqual(set(record["arms"]), set(harness.ARMS))
        self.assertEqual(len(record["public_exploration_actions"]), 24)
        self.assertEqual(len(record["identical_exploration_sha256"]), 64)
        self.assertFalse(record["scientific_pass"])
        self.assertFalse(record["original_dev_opened"])
        self.assertFalse(record["reserved_transfer_opened"])
        for index, name in enumerate(harness.ARMS):
            arm = self.arms[name]
            item = record["arms"][name]
            self.assertEqual(item["scored_steps"], 16)
            self.assertEqual(item["selected_actions"], [index % 8] * 16)
            self.assertEqual(arm.observations, 40)
            self.assertEqual(arm.events[:24], ["observe"] * 24)
            self.assertEqual(arm.events[24:],
                             ["choose", "observe"] * 16)
            self.assertEqual(item["shared_exploration_sha256"],
                             record["identical_exploration_sha256"])
            self.assertEqual(len(item["action_commit_sha256"]), 64)

    def test_independent_physical_reset_and_replay(self):
        first = self.run_episode()
        second = self.run_episode()
        self.assertEqual(first, second)
        # Different policies use different actually earned consequences.
        outcomes = [x["chosen_outcome_sha256"] for x in first["arms"].values()]
        self.assertGreater(len(set(outcomes)), 1)

    def test_different_exploration_world_refused(self):
        count = 0
        def different():
            nonlocal count
            count += 1
            return fixture.PublicSession(self.seed if count == 1 else
                                         fixture.TRAIN[10])
        with self.assertRaisesRegex(ValueError, "DIFFERENT_EXPLORATION_DATA"):
            self.run_episode(different)

    def test_missing_or_invalid_arm_refused_before_source_access(self):
        with self.assertRaisesRegex(ValueError, "MISSING_STRONG_ARM"):
            harness.evaluate_training_fixture(lambda: object(), self.tape,
                                               {"STRUCTURED": FakeLearner(1)},
                                               self.seed)

    def test_forbid_changed_exploration_or_unknown_actions(self):
        for bad in ((0,) * 23, (0,) * 25, tuple([8] + [0] * 23),
                    tuple([True] + [0] * 23)):
            with self.assertRaisesRegex(ValueError, "FROZEN_ACTION_TAPE"):
                harness.evaluate_training_fixture(lambda: object(), bad,
                                                   self.arms, self.seed)

    def test_forged_outcome_schema_or_wrong_action_rejected(self):
        class Forged:
            @property
            def current_public(self):
                return (0,) * 8

            def apply_public(self, action):
                return {"before": (0,) * 8, "action": action,
                        "oracle": [1] * 8}
        with self.assertRaisesRegex(ValueError, "PUBLIC_SCHEMA_MISMATCH"):
            self.run_episode(Forged)

        class Mismatch:
            @property
            def current_public(self):
                return (0,) * 8
            def apply_public(self, action):
                return fixture.PublicStep((0,) * 8, (action + 1) % 8,
                                          (0,) * 8, 0.0, False, ())
        with self.assertRaisesRegex(ValueError, "CHOICE_OUTCOME_MISMATCH"):
            self.run_episode(Mismatch)

    def test_protected_world_never_opened(self):
        with self.assertRaises(PermissionError):
            self.run_episode(lambda: fixture.PublicSession(978500))
        with self.assertRaises(PermissionError):
            self.run_episode(lambda: fixture.PublicSession(978600))

    def test_harness_never_imports_evaluator_or_native_model(self):
        src = Path(harness.__file__).read_text("utf-8")
        ast.parse(src)
        self.assertNotIn("import source_fixture", src)
        self.assertNotIn("import public_policies", src)
        self.assertNotIn("HELD_DEV", src)
        self.assertNotIn("HELD_TRANSFER", src)
        self.assertNotIn("allow_dev=True", src)


if __name__ == "__main__":
    unittest.main()
