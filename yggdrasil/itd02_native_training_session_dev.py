"""Finite, model-owned learning sessions for the existing Yggdrasil native runtime.

The source-owner supplies only PUBLIC reset/action/consequence calls. No POMDP,
simulator/oracle, model-writing assistant, scheduler, hidden information or
scientific-first-use admission is introduced here. Original cells and learning
rules remain in NativeTaskRingBridgeDev and LocalTaskRuntime.
"""
from .itd02_native_task_bridge_dev import NativeTaskRingBridgeDev
from .itd02_local_ring_memory_dev import ACTIONS, OBSERVATIONS

MAX_EPISODE_STEPS = 4096
MAX_SESSION_EPISODES = 128


class NativeTrainingSessionDev:
    """Wrap exactly one original native model and a source-owner-operated task."""

    def __init__(self, model=None, *, max_steps=128):
        if type(max_steps) is not int or not 1 <= max_steps <= MAX_EPISODE_STEPS:
            raise ValueError("YGG_SELF_TRAINING_STEP_BUDGET_INVALID")
        self.model = NativeTaskRingBridgeDev() if model is None else model
        if type(self.model) is not NativeTaskRingBridgeDev:
            raise ValueError("YGG_SELF_TRAINING_NATIVE_RUNTIME_REQUIRED")
        self.max_steps = max_steps
        # External/source-owner reconciliation remains mandatory after a fault.
        # This local latch is not a durable receipt across process restarts.
        self._quarantined = False
        self._pending_checkpoint = None

    def run_episode(self, source):
        """Act, observe, train original local cells, and cold-checkpoint.

        Source must implement reset_public() and step_public(action). A step
        returns EXACTLY (next_observation, reward, terminal), not an 'info'
        object or source-private grid. Ambiguous source writes are NEVER
        retried. A nonterminal budget exhaustion is not a fabricated terminal.
        """
        if (self._quarantined or self._pending_checkpoint is not None or
                not callable(getattr(source, "reset_public", None)) or
                not callable(getattr(source, "step_public", None)) or
                self.model._observation is not None or self.model.memory.pending or
                self.model._frozen_native is not None or
                self.model.memory._frozen_hash is not None):
            raise ValueError("YGG_SELF_TRAINING_SOURCE_OR_MODE_INVALID")
        try:
            initial = source.reset_public()
        except BaseException:
            self._quarantined = True
            raise
        if type(initial) is not str or initial not in OBSERVATIONS:
            self._quarantined = True
            raise ValueError("YGG_SELF_TRAINING_INITIAL_PUBLIC_OBSERVATION_INVALID")
        try:
            self.model.reset_episode()
        except BaseException:
            self._quarantined = True
            raise
        observation = initial
        reward_total = 0
        for step in range(self.max_steps):
            try:
                self.model.start_observation(observation)
                action = self.model.choose()
            except BaseException:
                self._quarantined = True
                raise
            if action not in ACTIONS:
                self._quarantined = True
                raise ValueError("YGG_SELF_TRAINING_NON_NATIVE_ACTION")
            # This may irrevocably advance the original environment. Do NOT
            # retry the source action if it fails or returns invalid public data.
            try:
                event = source.step_public(action)
            except BaseException:
                self._quarantined = True
                raise
            if (type(event) is not tuple or len(event) != 3 or
                    type(event[0]) is not str or event[0] not in OBSERVATIONS or
                    type(event[1]) is not int or
                    type(event[2]) is not bool):
                self._quarantined = True
                raise ValueError("YGG_SELF_TRAINING_INVALID_SOURCE_CONSEQUENCE")
            next_observation, reward, terminal = event
            try:
                self.model.accept_public_transition(
                    action, next_observation, reward, learning=True,
                    terminal=terminal)
            except BaseException:
                self._quarantined = True
                raise
            reward_total += reward
            observation = next_observation
            if terminal:
                try:
                    checkpoint = self.model.checkpoint()
                except BaseException:
                    self._quarantined = True
                    raise
                # No next episode until source-owner save confirms this state.
                self._pending_checkpoint = checkpoint
                return {"steps": step + 1,
                        "reward": reward_total,
                        "transitions": self.model.transitions,
                        "native_identities": self.model.model_identities(),
                        "checkpoint": checkpoint}
        self._quarantined = True
        raise ValueError("YGG_SELF_TRAINING_NO_SOURCE_TERMINAL")

    def persist_completed(self, save):
        """Acknowledge the exact completed checkpoint via an owner-owned sink.

        Caller must independently guarantee durable custody and external
        source reconciliation. Uncertain save leaves this session quarantined.
        """
        if (self._quarantined or self._pending_checkpoint is None or
                not callable(save)):
            raise ValueError("YGG_SELF_TRAINING_CHECKPOINT_NOT_READY")
        try:
            save(self._pending_checkpoint)
        except BaseException:
            self._quarantined = True
            raise
        self._pending_checkpoint = None

    def train_bounded(self, source, episodes, save):
        if (type(episodes) is not int or
                not 1 <= episodes <= MAX_SESSION_EPISODES or
                not callable(save)):
            raise ValueError("YGG_SELF_TRAINING_BUDGET_INVALID")
        completed = []
        for _ in range(episodes):
            result = self.run_episode(source)
            # The owner controls durable checkpoint identity and provenance.
            # Failure stops immediately, never replays a consumed episode.
            self.persist_completed(save)
            completed.append({k: v for k, v in result.items()
                              if k != "checkpoint"})
        return completed
