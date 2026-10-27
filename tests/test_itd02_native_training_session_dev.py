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

    def test_completed_episode_needs_checkpoint_ack_before_reuse(self):
        source = PublicSource()
        session = NativeTrainingSessionDev(max_steps=1)
        result = session.run_episode(source)
        self.assertEqual(len(source.actions), 1)
        with self.assertRaisesRegex(ValueError, "SOURCE_OR_MODE_INVALID"):
            session.run_episode(source)
        self.assertEqual(source.resets, 1)
        saved = []
        session.persist_completed(lambda data: saved.append(data))
        self.assertEqual(saved, [result["checkpoint"]])
        session.run_episode(source)
        self.assertEqual(source.resets, 2)

    def test_failed_sink_quarantines_repeated_calls(self):
        source = PublicSource()
        session = NativeTrainingSessionDev(max_steps=1)
        def ambiguous_sink(_data):
            raise RuntimeError("DURABLE_CHECKPOINT_UNCERTAIN")
        with self.assertRaisesRegex(RuntimeError, "CHECKPOINT_UNCERTAIN"):
            session.train_bounded(source, 2, ambiguous_sink)
        self.assertEqual((source.resets, len(source.actions)), (1, 1))
        for operation in (lambda: session.run_episode(source),
                          lambda: session.train_bounded(source, 1, lambda _: None),
                          lambda: session.persist_completed(lambda _: None)):
            with self.assertRaisesRegex(ValueError, "SOURCE_OR_MODE_INVALID|CHECKPOINT_NOT_READY"):
                operation()
        self.assertEqual((source.resets, len(source.actions)), (1, 1))

    def test_ambiguous_reset_and_invalid_reset_quarantine(self):
        class AmbiguousReset(PublicSource):
            def reset_public(self):
                self.resets += 1
                raise RuntimeError("SOURCE_RESET_UNCERTAIN")
        class InvalidReset(PublicSource):
            def reset_public(self):
                self.resets += 1
                return "SOURCE_PRIVATE_VALUE"
        for source, error, pattern in ((AmbiguousReset(), RuntimeError, "SOURCE_RESET_UNCERTAIN"),
                                       (InvalidReset(), ValueError, "INITIAL_PUBLIC_OBSERVATION_INVALID")):
            session = NativeTrainingSessionDev(max_steps=1)
            with self.assertRaisesRegex(error, pattern):
                session.run_episode(source)
            with self.assertRaisesRegex(ValueError, "SOURCE_OR_MODE_INVALID"):
                session.run_episode(source)
            self.assertEqual(source.resets, 1)
            self.assertEqual(source.actions, [])

    def test_opt_in_model_owned_exploration_and_cold_restart(self):
        source = PublicSource()
        session = NativeTrainingSessionDev(max_steps=1, exploration_period=9)
        checkpoints = []
        completed = session.train_bounded(source, 6, checkpoints.append)
        self.assertEqual(len(completed), 6)
        # The exploration schedule is derived solely from model-owned,
        # checkpointed action_calls, not an evaluator's hidden optimal action.
        self.assertEqual(source.actions,
                         ["TurnAround", "TurnAround", "GoForward",
                          "GoForward", "Backup", "Backup"])
        self.assertEqual(session.model.memory.action_calls, 6)
        self.assertEqual(session.model.transitions, 6)
        self.assertEqual(len(checkpoints), 6)
        cold = NativeTrainingSessionDev(
            NativeTaskRingBridgeDev.restore(checkpoints[-1]),
            max_steps=1, exploration_period=9)
        self.assertEqual(cold.model.memory.action_calls, 6)
        other_source = PublicSource()
        expected = session.train_bounded(source, 1, lambda _: None)
        observed = cold.train_bounded(other_source, 1, lambda _: None)
        self.assertEqual(source.actions[-1], other_source.actions[-1])
        self.assertEqual(expected, observed)
        self.assertEqual(session.model.checkpoint(), cold.model.checkpoint())

    def test_invalid_exploration_and_frozen_evaluation_fail_closed(self):
        for invalid in (True, -1, 1, 65, 3.14):
            with self.assertRaisesRegex(ValueError, "EXPLORATION_INVALID"):
                NativeTrainingSessionDev(exploration_period=invalid)
        for invalid in (True, -1, 97):
            with self.assertRaisesRegex(ValueError, "EXPLORATION_INVALID"):
                NativeTrainingSessionDev(exploration_period=9,
                                         exploration_bootstrap_calls=invalid)
        session = NativeTrainingSessionDev(max_steps=1, exploration_period=9)
        native_id = session.model.model_identities()
        session.model.start_frozen_evaluation(native_id["native"],
                                              native_id["memory"])
        with self.assertRaisesRegex(ValueError, "EXPLORATION_REQUIRES_TRAINING_MODE"):
            session.model.choose_training()
        with self.assertRaisesRegex(ValueError, "SOURCE_OR_MODE_INVALID"):
            session.run_episode(PublicSource())

    def test_exploratory_training_retains_uncertain_checkpoint_quarantine(self):
        session = NativeTrainingSessionDev(max_steps=1, exploration_period=6)
        source = PublicSource()
        with self.assertRaisesRegex(RuntimeError, "DURABLE_CHECKPOINT_UNCERTAIN"):
            session.train_bounded(
                source, 2, lambda _: (_ for _ in ()).throw(
                    RuntimeError("DURABLE_CHECKPOINT_UNCERTAIN")))
        self.assertEqual(len(source.actions), 1)
        with self.assertRaisesRegex(ValueError, "SOURCE_OR_MODE_INVALID"):
            session.run_episode(source)
        self.assertEqual((source.resets, len(source.actions)), (1, 1))

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
