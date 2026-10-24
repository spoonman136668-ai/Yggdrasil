"""Streaming no-oracle live interface for MR34J3C stage-only learners.

Online choice depends exclusively on bounded memory built from prior public
observations. A temporary, per-episode training tape is retained ONLY during
FIT so terminal-reward gradients can be computed after the action. During
HELD, no public-history tape is retained or accepted from the evaluator.
"""
from __future__ import annotations

import json
import numpy as np
from learners import (as_signal, Episode, LearnedTrace17, ConventionalRNN57,
                      ObservationOnly3, sigmoid)
from public_scaffold import KEY, BALL, ProtocolBlocked, PublicView


class PublicPolicySession:
    def __init__(self, policy, *, fit: bool = False):
        if not isinstance(policy, (LearnedTrace17, ConventionalRNN57, ObservationOnly3)):
            raise ProtocolBlocked("UNKNOWN_FROZEN_LEARNER_CLASS")
        self.policy = policy
        self.fit = bool(fit)
        self.tape = [] if fit else None
        self.seen_cue = False
        self.seen_fork = False
        self.chosen = None
        self.cue_age = 0
        self.memory = np.zeros(2, dtype=np.float64) if isinstance(policy, LearnedTrace17) else (
            np.zeros(4, dtype=np.float64) if isinstance(policy, ConventionalRNN57) else np.zeros(0, dtype=np.float64))
        self.fork = None
        self.cue_was_visible = False

    def observe(self, view: PublicView, event: str = ""):
        if self.chosen is not None or self.seen_fork:
            raise ProtocolBlocked("INPUT_AFTER_FORK_CHOICE")
        sig = as_signal(view, event)
        if event == "PUBLIC_CUE_EXPOSURE":
            if self.seen_cue:
                raise ProtocolBlocked("DUPLICATED_CUE_EXPOSURE")
            self.seen_cue = True
            self.cue_was_visible = True
        elif event == "PUBLIC_FORK_OBJECT_EXPOSURE_AND_CHOICE":
            if not self.seen_cue:
                raise ProtocolBlocked("FORK_BEFORE_CUE")
            self.seen_fork = True
            self.fork = sig[2:4].copy()
        if self.fit:
            self.tape.append(tuple(sig.tolist()))

        if isinstance(self.policy, LearnedTrace17):
            if event == "PUBLIC_CUE_EXPOSURE":
                x = sig[:2]
                self.memory = np.tanh(self.policy.weights["W"] @ x + self.policy.weights["b"])
            elif self.seen_cue and event == "":
                w = self.policy.weights
                self.memory *= np.asarray([sigmoid(v) for v in w["d"]])
                self.cue_age += 1
        elif isinstance(self.policy, ConventionalRNN57):
            w = self.policy.weights
            self.memory = np.tanh(w["Wx"] @ sig + w["Wh"] @ self.memory + w["b"])

    def _logit(self):
        if not self.seen_fork or not self.seen_cue or self.fork is None:
            raise ProtocolBlocked("DECISION_WITHOUT_PUBLIC_EXPOSURE")
        w = self.policy.weights
        if isinstance(self.policy, LearnedTrace17):
            return float(w["wm"] @ self.memory + w["wf"] @ self.fork + self.memory @ w["X"] @ self.fork + w["bo"].item())
        if isinstance(self.policy, ConventionalRNN57):
            return float(w["v"] @ self.memory + self.memory @ w["Y"] @ self.fork + w["bo"].item())
        return float(w["wf"] @ self.fork + w["bo"].item())

    def choose(self, *, evaluation: bool):
        if self.chosen is not None:
            raise ProtocolBlocked("SECOND_BRANCH_CHOICE_FORBIDDEN")
        probability=sigmoid(self._logit())
        north = probability >= 0.5 if evaluation else bool(self.policy.rng.random() < probability)
        self.chosen = "north" if north else "south"
        return self.chosen, probability

    def update_terminal_reward(self, reward: float):
        if not self.fit or self.chosen is None or self.tape is None:
            raise ProtocolBlocked("LEARNING_OUTSIDE_LEGITIMATE_FIT")
        ep = Episode(tuple(self.tape))
        # Alignment check: the training tape has no influence on online action.
        if not np.isclose(self._logit(),self.policy.logit_and_gradient(ep)[0],atol=1e-10,rtol=1e-10):
            raise ProtocolBlocked("ONLINE_AND_TRAINING_TRACE_DIVERGED")
        self.policy.update(ep, self.chosen, reward)
        self.tape = None # no replay after update

    def state_receipt(self):
        # Constant-bounded retained online state; no image history for HELD.
        if self.fit:
            raise ProtocolBlocked("FIT_TAPE_IS_NOT_PRODUCTION_MEMORY")
        return json.dumps({"class":type(self.policy).__name__, "memory":self.memory.tolist(),
                           "seen_cue":self.seen_cue,"seen_fork":self.seen_fork,
                           "cue_age":self.cue_age,
                           "fork":None if self.fork is None else self.fork.tolist(),
                           "choice":self.chosen},sort_keys=True,separators=(",", ":"))

    @classmethod
    def restore_state(cls, policy, receipt):
        x=json.loads(receipt)
        if x["class"] != type(policy).__name__:
            raise ProtocolBlocked("ONLINE_STATE_MODEL_MISMATCH")
        obj=cls(policy,fit=False)
        a=np.asarray(x["memory"],dtype=np.float64)
        if a.shape != obj.memory.shape or not np.isfinite(a).all():
            raise ProtocolBlocked("ONLINE_STATE_MEMORY_SHAPE_INVALID")
        obj.memory=a
        obj.seen_cue=bool(x["seen_cue"])
        obj.seen_fork=bool(x["seen_fork"])
        obj.cue_age=int(x["cue_age"])
        obj.fork=None if x["fork"] is None else np.asarray(x["fork"],dtype=np.float64)
        if obj.fork is not None and (obj.fork.shape!=(2,) or not np.isfinite(obj.fork).all()):
            raise ProtocolBlocked("ONLINE_FORK_INVALID")
        obj.chosen=x["choice"]
        if obj.state_receipt()!=receipt:
            raise ProtocolBlocked("ONLINE_COLD_RESTORE_MISMATCH")
        return obj


class PublicRuleSession:
    """Strong hand-coded cue cache comparator. No learned weights."""
    def __init__(self):
        self.cue = None
        self.upper = None

    def observe(self, view: PublicView, event: str):
        sig = as_signal(view,event)
        if event == "PUBLIC_CUE_EXPOSURE":
            if self.cue is not None:
                raise ProtocolBlocked("RULE_CUE_DUPLICATE")
            self.cue = int(np.argmax(sig[:2]))
        elif event == "PUBLIC_FORK_OBJECT_EXPOSURE_AND_CHOICE":
            if self.cue is None or self.upper is not None:
                raise ProtocolBlocked("RULE_FORK_OUT_OF_ORDER")
            self.upper = int(np.argmax(sig[2:4]))

    def choose(self):
        if self.cue is None or self.upper is None:
            raise ProtocolBlocked("RULE_PUBLIC_EXPOSURE_ABSENT")
        return "north" if self.cue==self.upper else "south"
