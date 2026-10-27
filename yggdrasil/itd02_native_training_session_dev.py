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

    def run_episode(self, source):
        """Act, observe, train original local cells, and cold-checkpoint.

        Source must implement reset_public() and step_public(action). A step
        returns EXACTLY (next_observation, reward, terminal), not an 'info'
        object or source-private grid. Ambiguous source writes are NEVER
        retried. A nonterminal budget exhaustion is not a fabricated terminal.
        """
        if (not callable(getattr(source, "reset_public", None)) or
                not callable(getattr(source, "step_public", None)) or
                self.model._observation is not None or self.model.memory.pending or
                self.model._frozen_native is not None or
                self.model.memory._frozen_hash is not None):
            raise ValueError("YGG_SELF_TRAINING_SOURCE_OR_MODE_INVALID")
        initial = source.reset_public()
        if type(initial) is not str or initial not in OBSERVATIONS:
            raise ValueError("YGG_SELF_TRAINING_INITIAL_PUBLIC_OBSERVATION_INVALID")
        self.model.reset_episode()
        observation = initial
        reward_total = 0
        for step in range(self.max_steps):
            self.model.start_observation(observation)
            action = self.model.choose()
            if action not in ACTIONS:
                raise ValueError("YGG_SELF_TRAINING_NON_NATIVE_ACTION")
            # This may irrevocably advance the original environment. Do NOT
            # retry the source action if it fails or returns invalid public data.
            event = source.step_public(action)
            if (type(event) is not tuple or len(event) != 3 or
                    type(event[0]) is not str or event[0] not in OBSERVATIONS or
                    type(event[1]) is not int or
                    type(event[2]) is not bool):
                raise ValueError("YGG_SELF_TRAINING_INVALID_SOURCE_CONSEQUENCE")
            next_observation, reward, terminal = event
            self.model.accept_public_transition(
                action, next_observation, reward, learning=True,
                terminal=terminal)
            reward_total += reward
            observation = next_observation
            if terminal:
                checkpoint = self.model.checkpoint()
                return {"steps": step + 1,
                        "reward": reward_total,
                        "transitions": self.model.transitions,
                        "native_identities": self.model.model_identities(),
                        "checkpoint": checkpoint}
        raise ValueError("YGG_SELF_TRAINING_NO_SOURCE_TERMINAL")

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
            save(result["checkpoint"])
            completed.append({k: v for k, v in result.items()
                              if k != "checkpoint"})
        return completed
