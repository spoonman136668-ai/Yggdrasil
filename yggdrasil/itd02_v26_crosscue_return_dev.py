"""V26 source-only external cross-cue evidence selector, prereg-first.

This is NOT independently learned world change detection.  Original eight-cell
V22 native banks are unchanged; the selector sees public selected reward only.
"""
import hashlib
import json
import math

from .itd02_v17_neighbor_carried_learner_dev import ACTIONS, PUBLIC_CUES, canonical
from .itd02_v18_intermediate_plasticity_dev import REWARD_LIMITS, _valid_finite
from .itd02_v24_protected_dual_memory_dev import ProtectedDualMemoryRingDev

SCHEMA = "ygg.itd02.v26.crosscue_return.source_only.v1"
WINDOW = 4
MARGIN = 0.10
SUM_BOUND = 0.40
CHECKPOINT_BOUND = 12288
NATIVE_LEARNED_SCALARS = 326


def candidate_vote(recent, current_fast, *, require_diversity=True):
    """Only previous legal observed outcomes; never an evaluator stage label."""
    if len(recent) < WINDOW:
        return current_fast
    if len(recent) != WINDOW:
        raise ValueError("V26_WINDOW_OVERFLOW")
    d = [row[0] for row in recent]
    groups = {row[1] for row in recent}
    if not current_fast:
        return sum(v <= -MARGIN for v in d) >= 3 and sum(d) <= -SUM_BOUND
    supports = sum(v >= MARGIN for v in d) >= 3 and sum(d) >= SUM_BOUND
    if require_diversity:
        supports = (supports and groups == {0, 1}
                    and all(any(v >= MARGIN and g == group for v, g in recent)
                            for group in (0, 1)))
    return not supports


class CrossCueReturnRingDev:
    """Frozen-source / fast-target bank with simple predeclared cross-cue votes."""

    def __init__(self, source_checkpoint, *, require_diversity=True):
        if type(require_diversity) is not bool:
            raise ValueError("V26_INVALID_DIVERSITY_MODE")
        self.bank = ProtectedDualMemoryRingDev(source_checkpoint)
        self.require_diversity = require_diversity
        self.recent = []
        self.use_fast = False
        self.switches = 0
        self.reactivations = 0
        self.frozen_sha = None

    def parameters_sha256(self):
        return hashlib.sha256(canonical({
            "bank": self.bank.parameters_sha256(),
            "require_diversity": self.require_diversity,
            "recent": self.recent,
            "use_fast": self.use_fast,
            "switches": self.switches,
            "reactivations": self.reactivations,
        })).hexdigest()

    def _guard(self):
        self.bank._guard()
        if self.frozen_sha is not None and self.parameters_sha256() != self.frozen_sha:
            raise ValueError("V26_FROZEN_BANK_OR_SELECTOR_DRIFT")

    def start_observation(self, cue):
        self._guard()
        self.bank.start_observation(cue)

    def accept_first(self, actual_first, next_observation="Nothing", reward=0):
        self._guard()
        self.bank.accept_first(actual_first, next_observation, reward)

    def source_score(self, action):
        self._guard()
        return self.bank.source_score(action)

    def fast_score(self, action):
        self._guard()
        return self.bank.fast_score(action)

    def score(self, action):
        self._guard()
        return self.fast_score(action) if self.use_fast else self.source_score(action)

    def scores(self):
        return [self.score(action) for action in ACTIONS]

    def accept_second(self, selected, public_reward, *, learning=True, terminal=True):
        self._guard()
        if type(selected) is not str or selected not in ACTIONS:
            raise ValueError("INVALID_SELECTED_SECOND_ACTION")
        if not _valid_finite(public_reward, *REWARD_LIMITS):
            raise ValueError("INVALID_PUBLIC_REWARD")
        if type(learning) is not bool or type(terminal) is not bool or not terminal:
            raise ValueError("INVALID_PUBLIC_TERMINAL_STATE")
        if learning and self.frozen_sha is not None:
            raise ValueError("V26_NO_TRAINING_IN_FROZEN_READOUT")
        cue = self.bank.fast.cue
        if cue is None or self.bank.fast.first is None or cue != self.bank.slow.cue:
            raise ValueError("V26_PUBLIC_FIRST_ACTION_REQUIRED")
        if learning:
            s = self.bank.source_score(selected)
            f = self.bank.fast_score(selected)
            group = PUBLIC_CUES.index(cue) % 2
        self.bank.accept_second(selected, public_reward, learning=learning, terminal=terminal)
        if learning:
            d = abs(float(public_reward) - f) - abs(float(public_reward) - s)
            if not math.isfinite(d):
                raise ValueError("V26_INVALID_PUBLIC_RESIDUAL")
            self.recent = (self.recent + [[d, group]])[-WINDOW:]
            before = self.use_fast
            self.use_fast = candidate_vote(self.recent, self.use_fast,
                                           require_diversity=self.require_diversity)
            if before != self.use_fast:
                self.switches += 1
                if before and not self.use_fast:
                    self.reactivations += 1
        self._guard()

    def start_frozen_evaluation(self):
        self._guard()
        self.bank.start_frozen_evaluation()
        self.frozen_sha = self.parameters_sha256()

    def checkpoint(self):
        self._guard()
        body = {
            "schema": SCHEMA,
            "v24_bank": json.loads(self.bank.checkpoint()),
            "require_diversity": self.require_diversity,
            "recent": self.recent,
            "use_fast": self.use_fast,
            "switches": self.switches,
            "reactivations": self.reactivations,
            "frozen_sha": self.frozen_sha,
        }
        b = canonical(body)
        out = canonical({"body": body, "sha256": hashlib.sha256(b).hexdigest()})
        if len(out) > CHECKPOINT_BOUND:
            raise ValueError("V26_CHECKPOINT_OVER_BUDGET")
        return out

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not (0 < len(raw) <= CHECKPOINT_BOUND):
                raise ValueError("V26_INVALID_CHECKPOINT_LENGTH")
            env = json.loads(raw)
            if type(env) is not dict or set(env) != {"body", "sha256"}:
                raise ValueError("V26_ENVELOPE_SHAPE")
            b = env["body"]
            keys = {"schema","v24_bank","require_diversity","recent","use_fast",
                    "switches","reactivations","frozen_sha"}
            if (type(b) is not dict or set(b) != keys or b["schema"] != SCHEMA or
                    type(env["sha256"]) is not str or
                    hashlib.sha256(canonical(b)).hexdigest() != env["sha256"]):
                raise ValueError("V26_INVALID_CHECKPOINT_DIGEST")
            bank = ProtectedDualMemoryRingDev.restore(canonical(b["v24_bank"]))
            recent = b["recent"]
            if (type(b["require_diversity"]) is not bool or
                    type(b["use_fast"]) is not bool or
                    type(b["switches"]) is not int or b["switches"] < 0 or
                    type(b["reactivations"]) is not int or
                    not 0 <= b["reactivations"] <= b["switches"] <= bank.target_updates or
                    type(recent) is not list or
                    len(recent) != min(WINDOW, bank.target_updates) or
                    any(type(r) is not list or len(r) != 2 or
                        not _valid_finite(r[0], -1e9, 1e9) or
                        type(r[1]) is not int or r[1] not in (0, 1)
                        for r in recent)):
                raise ValueError("V26_INVALID_PUBLIC_EVIDENCE")
            obj = cls.__new__(cls)
            obj.bank = bank
            obj.require_diversity = b["require_diversity"]
            obj.recent = recent
            obj.use_fast = b["use_fast"]
            obj.switches = b["switches"]
            obj.reactivations = b["reactivations"]
            obj.frozen_sha = b["frozen_sha"]
            if obj.frozen_sha is not None and (
                    type(obj.frozen_sha) is not str or len(obj.frozen_sha) != 64 or
                    bank.frozen_sha is None or obj.parameters_sha256() != obj.frozen_sha):
                raise ValueError("V26_INVALID_FROZEN_STATE")
            if obj.checkpoint() != raw:
                raise ValueError("V26_NONCANONICAL_CHECKPOINT")
            return obj
        except (KeyError, ValueError, TypeError, AttributeError, IndexError,
                OverflowError) as exc:
            raise ValueError("UNTRUSTED_V26_CHECKPOINT") from exc
