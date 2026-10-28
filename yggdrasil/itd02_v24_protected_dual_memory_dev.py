"""V24 opt-in protected source bank and fast ring-local adaptation envelope.

The original V22 banks are unchanged. A central, two-loss online selector
operates ONLY on previously observed public target rewards; this is NOT
distributed autonomous task inference or novel source/target representation.
"""
import hashlib
import json
import math

from .itd02_v17_neighbor_carried_learner_dev import ACTIONS, canonical
from .itd02_v18_intermediate_plasticity_dev import REWARD_LIMITS, _valid_finite
from .itd02_v22_shared_context_ring_dev import (
    SharedContextRingDev, LEARNED_SCALARS, MAX_CHECKPOINT_BYTES,
)

SCHEMA = "ygg.itd02.v24.protected_dual_timescale.source_only.v1"
CHECKPOINT_BOUND = 12288
STORED_SCALARS = 2 * LEARNED_SCALARS


class ProtectedDualMemoryRingDev:
    """Frozen learned source + fresh target learner, selected by observed loss."""

    def __init__(self, source_checkpoint):
        slow = SharedContextRingDev.restore(source_checkpoint)
        if slow.mode != "shared" or slow.cue is not None or slow.first is not None:
            raise ValueError("V24_SOURCE_MUST_BE_COMPLETED_SHARED_EPISODE")
        if slow.updates < 1:
            raise ValueError("V24_SOURCE_HAS_NO_LEARNED_MEMORY")
        slow.start_frozen_evaluation()
        self.slow = slow
        self.fast = SharedContextRingDev(mode="shared")
        self.source_sha = slow.parameters_sha256()
        self.native_ids = dict(slow.native_ids)
        if self.native_ids != self.fast.native_ids:
            raise ValueError("NATIVE_CELL_SOURCE_MISMATCH")
        self.slow_loss = 0.0
        self.fast_loss = 0.0
        self.target_updates = 0
        self.gate_fast = False
        self.gate_flips = 0
        self.frozen_sha = None

    def parameters_sha256(self):
        return hashlib.sha256(canonical({
            "slow": self.slow.parameters_sha256(),
            "fast": self.fast.parameters_sha256(),
            "source_sha": self.source_sha,
            "slow_loss": self.slow_loss, "fast_loss": self.fast_loss,
            "target_updates": self.target_updates,
            "gate_fast": self.gate_fast, "gate_flips": self.gate_flips,
        })).hexdigest()

    def _guard(self):
        if self.slow.parameters_sha256() != self.source_sha:
            raise ValueError("PROTECTED_SOURCE_MEMORY_MUTATED")
        if self.native_ids != self.slow.native_ids or self.native_ids != self.fast.native_ids:
            raise ValueError("ORIGINAL_RING_SOURCE_ID_CHANGED")
        if self.frozen_sha is not None and self.parameters_sha256() != self.frozen_sha:
            raise ValueError("V24_FROZEN_WEIGHTS_OR_SELECTOR_CHANGED")

    def start_observation(self, cue):
        self._guard()
        self.slow.start_observation(cue)
        self.fast.start_observation(cue)

    def accept_first(self, actual_first, next_observation="Nothing", reward=0):
        self._guard()
        self.slow.accept_first(actual_first, next_observation, reward)
        self.fast.accept_first(actual_first, next_observation, reward)

    def source_score(self, selected):
        self._guard()
        return self.slow.score(selected)

    def fast_score(self, selected):
        self._guard()
        return self.fast.score(selected)

    def score(self, selected):
        return self.fast_score(selected) if self.gate_fast else self.source_score(selected)

    def scores(self):
        return [self.score(action) for action in ACTIONS]

    def accept_second(self, selected, public_reward, *, learning=True, terminal=True):
        self._guard()
        if type(selected) is not str or selected not in ACTIONS:
            raise ValueError("INVALID_SELECTED_SECOND_ACTION")
        if not _valid_finite(public_reward, *REWARD_LIMITS):
            raise ValueError("INVALID_PUBLIC_REWARD")
        if type(learning) is not bool or type(terminal) is not bool or not terminal:
            raise ValueError("SECOND_PUBLIC_STEP_MUST_TERMINATE")
        if learning and self.frozen_sha is not None:
            raise ValueError("NO_LEARNING_DURING_FROZEN_READOUT")
        if self.fast.cue is None or self.fast.first is None:
            raise ValueError("PUBLIC_FIRST_ACTION_NOT_OBSERVED")
        if self.slow.cue != self.fast.cue or self.slow.first != self.fast.first:
            raise ValueError("SOURCE_FAST_CONTEXT_MISMATCH")
        if learning:
            predicted_source = self.slow.score(selected)
            predicted_fast = self.fast.score(selected)
        self.slow.accept_second(selected, 0.0, learning=False, terminal=terminal)
        self.fast.accept_second(selected, public_reward, learning=learning,
                                terminal=terminal)
        if learning:
            old_gate = self.gate_fast
            self.slow_loss += abs(float(public_reward) - predicted_source)
            self.fast_loss += abs(float(public_reward) - predicted_fast)
            self.target_updates += 1
            self.gate_fast = self.fast_loss <= self.slow_loss
            self.gate_flips += int(self.gate_fast != old_gate)
        self._guard()

    def start_frozen_evaluation(self):
        self._guard()
        if self.fast.cue is not None or self.slow.cue is not None:
            raise ValueError("PUBLIC_EPISODE_PENDING")
        self.fast.start_frozen_evaluation()
        self.frozen_sha = self.parameters_sha256()

    def checkpoint(self):
        self._guard()
        body = {
            "schema": SCHEMA, "native_ids": self.native_ids,
            "source_bank": json.loads(self.slow.checkpoint()),
            "fast_bank": json.loads(self.fast.checkpoint()),
            "source_sha": self.source_sha,
            "slow_loss": self.slow_loss, "fast_loss": self.fast_loss,
            "target_updates": self.target_updates, "gate_fast": self.gate_fast,
            "gate_flips": self.gate_flips, "frozen_sha": self.frozen_sha,
        }
        raw = canonical(body)
        if len(raw) > CHECKPOINT_BOUND:
            raise ValueError("V24_DUAL_MEMORY_CHECKPOINT_OVER_BUDGET")
        return canonical({"body": body, "sha256": hashlib.sha256(raw).hexdigest()})

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= CHECKPOINT_BOUND:
                raise ValueError("INVALID_DUAL_CHECKPOINT_LENGTH")
            envelope = json.loads(raw)
            if type(envelope) is not dict or set(envelope) != {"body","sha256"}:
                raise ValueError("INVALID_DUAL_ENVELOPE")
            b = envelope["body"]
            keys = {"schema","native_ids","source_bank","fast_bank","source_sha",
                    "slow_loss","fast_loss","target_updates","gate_fast",
                    "gate_flips","frozen_sha"}
            if (type(b) is not dict or set(b) != keys or b["schema"] != SCHEMA
                    or hashlib.sha256(canonical(b)).hexdigest() != envelope["sha256"]):
                raise ValueError("INVALID_DUAL_CHECKPOINT_DIGEST")
            slow = SharedContextRingDev.restore(canonical(b["source_bank"]))
            fast = SharedContextRingDev.restore(canonical(b["fast_bank"]))
            if (slow.mode != fast.mode or slow.mode != "shared" or
                    slow.frozen_sha is None or slow.updates < 1 or
                    type(b["source_sha"]) is not str or
                    slow.parameters_sha256() != b["source_sha"] or
                    b["native_ids"] != slow.native_ids or
                    b["native_ids"] != fast.native_ids):
                raise ValueError("INVALID_DUAL_SOURCE_IDENTITY")
            for name in ("slow_loss","fast_loss"):
                if not _valid_finite(b[name], 0.0, 1e9):
                    raise ValueError("INVALID_ONLINE_LOSS_COUNTER")
            if (type(b["target_updates"]) is not int or b["target_updates"] < 0
                    or b["target_updates"] != fast.updates or
                    type(b["gate_flips"]) is not int or
                    not 0 <= b["gate_flips"] <= b["target_updates"] or
                    type(b["gate_fast"]) is not bool or
                    b["gate_fast"] != (b["fast_loss"] <= b["slow_loss"])
                        if b["target_updates"] > 0 else b["gate_fast"] is not False):
                raise ValueError("INVALID_PUBLIC_SELECTOR_PROVENANCE")
            obj = cls.__new__(cls)
            obj.slow, obj.fast = slow, fast
            obj.native_ids = b["native_ids"]
            obj.source_sha = b["source_sha"]
            obj.slow_loss, obj.fast_loss = b["slow_loss"], b["fast_loss"]
            obj.target_updates, obj.gate_fast = b["target_updates"], b["gate_fast"]
            obj.gate_flips, obj.frozen_sha = b["gate_flips"], b["frozen_sha"]
            if obj.frozen_sha is not None and (
                    type(obj.frozen_sha) is not str or len(obj.frozen_sha) != 64
                    or fast.frozen_sha is None
                    or obj.parameters_sha256() != obj.frozen_sha):
                raise ValueError("INVALID_FROZEN_DUAL_MEMORY")
            if obj.checkpoint() != raw:
                raise ValueError("DUAL_MEMORY_CHECKPOINT_NOT_CANONICAL")
            return obj
        except (KeyError, ValueError, TypeError, AttributeError,
                OverflowError) as exc:
            raise ValueError("UNTRUSTED_V24_DUAL_CHECKPOINT") from exc
