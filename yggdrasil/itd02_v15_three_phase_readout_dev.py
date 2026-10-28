"""V15 source-public, frozen-native three-phase local readout engineering adapter.

No original-world data, fitting of native genome or ring-memory, or scientific
claims. Per-head 64 scalar weights are a toy source-public adapter, not proof
of native self-organized context routing or unseen transfer.
"""
import hashlib
import json
import math

from research.itd02_v14_three_phase_context_capacity import (
    PUBLIC_CUES, ordered_local_word, phase_bits,
)
from yggdrasil.itd02_local_ring_memory_dev import (
    ACTIONS, ACTION_SITES, OBSERVATIONS,
)
from yggdrasil.itd02_native_task_bridge_dev import (
    NativeTaskRingBridgeDev, REWARDS,
)

SCHEMA = "ygg.itd02.v15.frozen_native_local_credit.source_only.v1"
MAX_CHECKPOINT_BYTES = 65536
HEAD_ENTRIES = 64
RATE = 0.5
NATIVE_WEIGHT = 0.15


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


class FrozenNativeThreePhaseReadoutDev:
    """Frozen original eight-cell native model plus locally learned public reward."""

    def __init__(self):
        self.bridge = NativeTaskRingBridgeDev()
        self.original_ids = self.bridge.model_identities()
        self.bridge.start_frozen_evaluation(
            self.original_ids["native"], self.original_ids["memory"])
        self.heads = [[0.0] * HEAD_ENTRIES for _ in ACTION_SITES]
        self.first_context = None
        self.local_updates = 0
        self.readout_calls = 0
        self.adapter_frozen_sha = None

    def parameters_sha256(self):
        return hashlib.sha256(canonical(self.heads)).hexdigest()

    def _assert_immutable(self):
        if self.bridge.model_identities() != self.original_ids:
            raise ValueError("ORIGINAL_MODEL_PARAMETER_DRIFT")
        if self.adapter_frozen_sha is not None and self.parameters_sha256() != self.adapter_frozen_sha:
            raise ValueError("FROZEN_ADAPTER_WEIGHT_DRIFT")

    def start_observation(self, observation):
        self._assert_immutable()
        if type(observation) is not str:
            raise ValueError("INVALID_PUBLIC_OBSERVATION")
        if self.first_context is None:
            if observation not in PUBLIC_CUES:
                raise ValueError("FIRST_PUBLIC_CUE_REQUIRED")
        elif observation != "Nothing":
            raise ValueError("SECOND_PUBLIC_NOTHING_REQUIRED")
        self.bridge.start_observation(observation)

    def _candidate(self, action):
        if self.first_context is None or self.bridge._observation != "Nothing" or not self.bridge.memory.pending:
            raise ValueError("SECOND_PUBLIC_OBSERVATION_REQUIRED")
        cue, actual_first = self.first_context
        views = [phase_bits(cue, actual_first, action, p) for p in range(3)]
        site_index = ACTIONS.index(action)
        site = ACTION_SITES[site_index]
        local_word = ordered_local_word(views, site)
        return views, site_index, local_word

    def readout_scores(self):
        """Read only original native predictions and each original head's two neighbors."""
        self._assert_immutable()
        if self.first_context is None or self.bridge._observation != "Nothing" or not self.bridge.memory.pending:
            raise ValueError("SECOND_PUBLIC_OBSERVATION_REQUIRED")
        scores = []
        for action in ACTIONS:
            views, head_index, word = self._candidate(action)
            phase_native = []
            for view in views:
                predictions = self.bridge.native.predict(view)
                if len(predictions) != 8:
                    raise ValueError("ORIGINAL_NATIVE_PREDICTION_SHAPE")
                if any(not math.isfinite(float(x)) for x in predictions):
                    raise ValueError("NONFINITE_NATIVE_PREDICTION")
                phase_native.append(sum(
                    float(REWARDS[index]) * float(predictions[site])
                    for index, site in enumerate(ACTION_SITES)))
            value = self.heads[head_index][word] + NATIVE_WEIGHT * (
                sum(phase_native) / len(phase_native))
            if not math.isfinite(value):
                raise ValueError("NONFINITE_ADAPTER_SCORE")
            scores.append(value)
        self.readout_calls += 1
        self._assert_immutable()
        return scores

    def local_scores(self):
        """Site-only diagnostic, excluding the unchanged native prediction contribution."""
        self._assert_immutable()
        return [
            self.heads[index][self._candidate(action)[2]]
            for index, action in enumerate(ACTIONS)
        ]

    def choose(self):
        scores = self.readout_scores()
        return ACTIONS[max(range(len(ACTIONS)), key=lambda i: scores[i])]

    def accept_public_transition(self, action, next_observation, reward, *,
                                 learning=True, terminal=False):
        """The first actual accepted action, never an intended action, owns history."""
        self._assert_immutable()
        if type(action) is not str or action not in ACTIONS:
            raise ValueError("INVALID_PUBLIC_SELECTED_ACTION")
        if type(next_observation) is not str or next_observation not in OBSERVATIONS:
            raise ValueError("INVALID_PUBLIC_SUCCESSOR")
        if type(reward) is not int or reward not in REWARDS:
            raise ValueError("INVALID_PUBLIC_REWARD")
        if type(learning) is not bool or type(terminal) is not bool:
            raise ValueError("INVALID_PUBLIC_FLAGS")
        if self.adapter_frozen_sha is not None and learning:
            raise ValueError("FROZEN_ADAPTER_LEARNING_FORBIDDEN")
        if self.bridge._observation is None or not self.bridge.memory.pending:
            raise ValueError("NO_PENDING_PUBLIC_TRANSITION")
        if self.first_context is None:
            cue = self.bridge._observation
            if cue not in PUBLIC_CUES or next_observation != "Nothing" or terminal:
                raise ValueError("FIRST_PUBLIC_STEP_MUST_CONTINUE_TO_NOTHING")
            target = None
        else:
            if self.bridge._observation != "Nothing" or not terminal:
                raise ValueError("SECOND_PUBLIC_STEP_MUST_TERMINATE")
            target = self._candidate(action)[1:]
        backup = self.checkpoint()
        try:
            # Deliberately leave BOTH original native and memory model frozen,
            # even when the bounded local adapter is fitting.
            self.bridge.accept_public_transition(
                action, next_observation, reward, learning=False, terminal=terminal)
            if target is None:
                self.first_context = (cue, action)
            else:
                head_index, local_word = target
                if learning:
                    old = self.heads[head_index][local_word]
                    new = (1.0 - RATE) * old + RATE * float(reward)
                    self.heads[head_index][local_word] = max(
                        float(min(REWARDS)), min(float(max(REWARDS)), new))
                    self.local_updates += 1
                self.first_context = None
            self._assert_immutable()
        except Exception:
            restored = type(self).restore(backup)
            self.__dict__.update(restored.__dict__)
            raise

    def reset_episode(self):
        self._assert_immutable()
        if self.first_context is not None:
            raise ValueError("UNFINISHED_TWO_STEP_PUBLIC_EPISODE")
        self.bridge.reset_episode()

    def start_frozen_evaluation(self):
        self._assert_immutable()
        if self.first_context is not None or self.bridge._observation is not None:
            raise ValueError("PUBLIC_TRANSITION_PENDING")
        self.adapter_frozen_sha = self.parameters_sha256()

    def checkpoint(self):
        self._assert_immutable()
        body = {
            "schema": SCHEMA,
            "bridge": json.loads(self.bridge.checkpoint()),
            "original_ids": self.original_ids,
            "heads": self.heads,
            "first_context": self.first_context,
            "local_updates": self.local_updates,
            "readout_calls": self.readout_calls,
            "adapter_frozen_sha": self.adapter_frozen_sha,
        }
        encoded = canonical(body)
        if len(encoded) > MAX_CHECKPOINT_BYTES:
            raise ValueError("ADAPTER_CHECKPOINT_OVER_BUDGET")
        return canonical({
            "body": body, "sha256": hashlib.sha256(encoded).hexdigest()})

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= MAX_CHECKPOINT_BYTES:
                raise ValueError("BAD_ADAPTER_CHECKPOINT_SIZE")
            envelope = json.loads(raw)
            if type(envelope) is not dict or set(envelope) != {"body", "sha256"}:
                raise ValueError("BAD_ADAPTER_ENVELOPE")
            body = envelope["body"]
            if hashlib.sha256(canonical(body)).hexdigest() != envelope["sha256"]:
                raise ValueError("BAD_ADAPTER_DIGEST")
            required = {
                "schema", "bridge", "original_ids", "heads",
                "first_context", "local_updates", "readout_calls",
                "adapter_frozen_sha",
            }
            if type(body) is not dict or set(body) != required or body["schema"] != SCHEMA:
                raise ValueError("BAD_ADAPTER_SCHEMA")
            bridge = NativeTaskRingBridgeDev.restore(canonical(body["bridge"]))
            original_ids = body["original_ids"]
            if (type(original_ids) is not dict or
                    set(original_ids) != {"native", "memory"} or
                    bridge.model_identities() != original_ids or
                    bridge._frozen_native != original_ids["native"] or
                    bridge.memory._frozen_hash != original_ids["memory"]):
                raise ValueError("BAD_FROZEN_NATIVE_IDENTITY")
            heads = body["heads"]
            if (type(heads) is not list or len(heads) != len(ACTION_SITES) or
                    any(type(row) is not list or len(row) != HEAD_ENTRIES or
                        any(type(x) not in (int, float) or not math.isfinite(x) or
                            not min(REWARDS) <= x <= max(REWARDS) for x in row)
                        for row in heads)):
                raise ValueError("BAD_LOCAL_HEADS")
            first = body["first_context"]
            if first is not None:
                if (type(first) is not list or len(first) != 2 or
                        first[0] not in PUBLIC_CUES or first[1] not in ACTIONS or
                        bridge.temporal_eligibility is None or
                        bridge._observation not in (None, "Nothing")):
                    raise ValueError("BAD_FIRST_PUBLIC_CONTEXT")
            else:
                if bridge.temporal_eligibility is not None:
                    raise ValueError("ORPHANED_PRIOR_PUBLIC_HISTORY")
            for key in ("local_updates", "readout_calls"):
                if type(body[key]) is not int or not 0 <= body[key] <= 100000000:
                    raise ValueError("BAD_ADAPTER_COUNTER")
            obj = cls.__new__(cls)
            obj.bridge = bridge
            obj.original_ids = original_ids
            obj.heads = [[float(x) for x in row] for row in heads]
            obj.first_context = None if first is None else tuple(first)
            obj.local_updates = body["local_updates"]
            obj.readout_calls = body["readout_calls"]
            obj.adapter_frozen_sha = body["adapter_frozen_sha"]
            if obj.adapter_frozen_sha is not None:
                if (type(obj.adapter_frozen_sha) is not str or
                        len(obj.adapter_frozen_sha) != 64 or
                        obj.parameters_sha256() != obj.adapter_frozen_sha):
                    raise ValueError("BAD_ADAPTER_FROZEN_IDENTITY")
            obj._assert_immutable()
            return obj
        except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as exc:
            raise ValueError("UNTRUSTED_V15_ADAPTER_CHECKPOINT") from exc
