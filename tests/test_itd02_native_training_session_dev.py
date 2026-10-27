"""Engineering-only closed-loop native Yggdrasil training contract tests."""
import unittest

from yggdrasil.itd02_native_task_bridge_dev import NativeTaskRingBridgeDev
from yggdrasil.itd02_native_training_session_dev import NativeTrainingSessionDev


class PublicSource:
    def __init__(self, *, terminal=True, wrong=False, fail=False):
        self.terminal = terminal
        self.wrong = wrong
        self.fail = fail
        self.actions = []
        self.resets = 0

    def reset_public(self):
        self.resets += 1
        return "LRV"

    def step_public(self, action):
        self.actions.append(action)
        if self.fail:
            raise RuntimeError("SOURCE_STEP_UNCERTAIN")
        if self.wrong:
            return ("MRV", 10, True, {"hidden_state": 123})
        reward = 10 if action == "TurnAround" else 0
        return ("MRV", reward, self.terminal)


class NativeTrainingSessionTests(unittest.TestCase):
    def test_actual_local_native_cells_update_and_cold_restart(self):
        source = PublicSource()
        session = NativeTrainingSessionDev(max_steps=1)
        original = session.model.model_identities()
        checkpoints = []
        observations = []
        for index in range(4):
            outcome = session.run_episode(source)
            self.assertEqual(outcome["steps"], 1)
            self.assertEqual(outcome["transitions"], index + 1)
            self.assertEqual(len(source.actions), index + 1)
            self.assertEqual(outcome["checkpoint"],
                             session.model.checkpoint())
            checkpoints.append(outcome["checkpoint"])
            observations.append(outcome["native_identities"])
            # Simulate a separate interpreter process using only persisted
            # checkpoint bytes: the original native runtime owns learning.
            session = NativeTrainingSessionDev(
                NativeTaskRingBridgeDev.restore(outcome["checkpoint"]),
                max_steps=1)
        self.assertNotEqual(observations[0], original)
        self.assertEqual(session.model.transitions, 4)
        self.assertEqual(source.resets, 4)
        self.assertNotEqual(checkpoints[0], checkpoints[-1])

    def test_ambiguous_step_is_never_reissued(self):
        source = PublicSource(fail=True)
        session = NativeTrainingSessionDev(max_steps=1)
        with self.assertRaisesRegex(RuntimeError, "SOURCE_STEP_UNCERTAIN"):
            session.run_episode(source)
        self.assertEqual(session.model.transitions, 0)
        self.assertTrue(session.model.memory.pending)
        with self.assertRaisesRegex(ValueError, "SOURCE_OR_MODE_INVALID"):
            session.run_episode(source)
        self.assertEqual(len(source.actions), 1)

    def test_hidden_info_and_nonterminal_expiration_fail_closed(self):
        for source in (PublicSource(wrong=True), PublicSource(terminal=False)):
            session = NativeTrainingSessionDev(max_steps=1)
            with self.assertRaisesRegex(ValueError, "YGG_SELF_TRAINING_"):
                session.run_episode(source)
            self.assertEqual(len(source.actions), 1)
            if source.wrong:
                self.assertEqual(session.model.transitions, 0)
                self.assertTrue(session.model.memory.pending)
            else:
                self.assertEqual(session.model.transitions, 1)
                self.assertFalse(session.model.memory.pending)

    def test_bounded_checkpoint_sink_stops_after_failure(self):
        source = PublicSource()
        session = NativeTrainingSessionDev(max_steps=1)
        persisted = []
        def save(state):
            persisted.append(state)
            if len(persisted) == 2:
                raise RuntimeError("DURABLE_CHECKPOINT_UNCERTAIN")
        with self.assertRaisesRegex(RuntimeError, "CHECKPOINT_UNCERTAIN"):
            session.train_bounded(source, 3, save)
        self.assertEqual(len(source.actions), 2)
        self.assertEqual(len(persisted), 2)
        with self.assertRaisesRegex(ValueError, "BUDGET_INVALID"):
            session.train_bounded(source, 129, lambda x: None)

    def test_original_model_frozen_mode_remains_untrainable(self):
        source = PublicSource()
        session = NativeTrainingSessionDev(max_steps=1)
        ids = session.model.model_identities()
        session.model.start_frozen_evaluation(ids["native"], ids["memory"])
        with self.assertRaisesRegex(ValueError, "SOURCE_OR_MODE_INVALID"):
            session.run_episode(source)
        self.assertEqual(source.resets, 0)


if __name__ == "__main__":
    unittest.main()
