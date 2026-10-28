"""V25 opt-in public-only sequential evidence selector for protected V24 banks.

No task regime input. A central 4-observation predictor-error selector is
hand-designed, not native original-world cognition. V24 banks stay unchanged.
"""
import hashlib
import json
from .itd02_v17_neighbor_carried_learner_dev import ACTIONS, canonical
from .itd02_v18_intermediate_plasticity_dev import REWARD_LIMITS, _valid_finite
from .itd02_v24_protected_dual_memory_dev import (
    ProtectedDualMemoryRingDev, CHECKPOINT_BOUND,
)

SCHEMA = "ygg.itd02.v25.unlabeled_public_error_return.source_only.v1"
WINDOW = 4
MARGIN = 0.1
MAX_BYTES = 12288

class UnlabeledReturnRingDev:
    def __init__(self, source_checkpoint):
        self.bank = ProtectedDualMemoryRingDev(source_checkpoint)
        self.recent = []
        self.use_fast = False
        self.switches = 0
        self.frozen_sha = None

    def parameters_sha256(self):
        return hashlib.sha256(canonical({
            "bank": self.bank.parameters_sha256(),
            "recent": self.recent, "use_fast": self.use_fast,
            "switches": self.switches,
        })).hexdigest()

    def _guard(self):
        self.bank._guard()
        if self.frozen_sha is not None and self.parameters_sha256() != self.frozen_sha:
            raise ValueError("V25_FROZEN_SELECTOR_OR_BANK_MUTATED")

    def start_observation(self, cue):
        self._guard()
        self.bank.start_observation(cue)

    def accept_first(self, action, next_observation="Nothing", reward=0):
        self._guard()
        self.bank.accept_first(action, next_observation, reward)

    def score(self, action):
        self._guard()
        return (self.bank.fast_score(action) if self.use_fast
                else self.bank.source_score(action))

    def scores(self):
        return [self.score(a) for a in ACTIONS]

    def accept_second(self, selected, reward, *, learning=True, terminal=True):
        self._guard()
        if type(selected) is not str or selected not in ACTIONS:
            raise ValueError("INVALID_SELECTED_SECOND_ACTION")
        if not _valid_finite(reward,*REWARD_LIMITS):
            raise ValueError("INVALID_PUBLIC_REWARD")
        if type(learning) is not bool or type(terminal) is not bool or not terminal:
            raise ValueError("INVALID_PUBLIC_TERMINAL_STATE")
        if learning and self.frozen_sha is not None:
            raise ValueError("V25_LEARNING_DURING_FROZEN_READOUT")
        if self.bank.fast.cue is None or self.bank.fast.first is None:
            raise ValueError("NO_PUBLIC_FIRST_ACTION")
        if learning:
            slow = self.bank.source_score(selected)
            fast = self.bank.fast_score(selected)
        self.bank.accept_second(selected, reward, learning=learning, terminal=terminal)
        if learning:
            delta = abs(reward-slow)-abs(reward-fast)
            self.recent = (self.recent + [
                1 if delta > MARGIN else -1 if delta < -MARGIN else 0
            ])[-WINDOW:]
            old = self.use_fast
            if self.recent.count(1) >= 3:
                self.use_fast = True
            elif self.recent.count(-1) >= 3:
                self.use_fast = False
            self.switches += int(old != self.use_fast)
        self._guard()

    def start_frozen_evaluation(self):
        self._guard()
        self.bank.start_frozen_evaluation()
        self.frozen_sha = self.parameters_sha256()

    def checkpoint(self):
        self._guard()
        body = {
            "schema":SCHEMA,
            "v24_bank":json.loads(self.bank.checkpoint()),
            "recent":self.recent,"use_fast":self.use_fast,
            "switches":self.switches,"frozen_sha":self.frozen_sha,
        }
        raw=canonical(body)
        if len(raw)>MAX_BYTES:
            raise ValueError("V25_CHECKPOINT_BUDGET")
        return canonical({"body":body,"sha256":hashlib.sha256(raw).hexdigest()})

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=MAX_BYTES:
                raise ValueError("V25_CHECKPOINT_SIZE")
            env=json.loads(raw)
            if type(env) is not dict or set(env)!={"body","sha256"}:
                raise ValueError("V25_ENVELOPE")
            b=env["body"]
            if (type(b) is not dict or
                set(b)!={"schema","v24_bank","recent","use_fast","switches","frozen_sha"} or
                b["schema"]!=SCHEMA or
                hashlib.sha256(canonical(b)).hexdigest()!=env["sha256"]):
                raise ValueError("V25_CHECKPOINT_DIGEST")
            bank=ProtectedDualMemoryRingDev.restore(canonical(b["v24_bank"]))
            recent=b["recent"]
            if (type(recent) is not list or len(recent)>WINDOW or
                any(type(z) is not int or z not in (-1,0,1) for z in recent) or
                len(recent)!=min(WINDOW,bank.target_updates) or
                type(b["switches"]) is not int or not 0<=b["switches"]<=bank.target_updates or
                type(b["use_fast"]) is not bool):
                raise ValueError("V25_OBSERVED_EVIDENCE_PROVENANCE")
            o=cls.__new__(cls)
            o.bank=bank
            o.recent=list(recent)
            o.use_fast=b["use_fast"]
            o.switches=b["switches"]
            o.frozen_sha=b["frozen_sha"]
            if o.frozen_sha is not None and (
                type(o.frozen_sha) is not str or len(o.frozen_sha)!=64 or
                bank.frozen_sha is None or o.frozen_sha!=o.parameters_sha256()):
                raise ValueError("V25_FROZEN_PROVENANCE")
            if o.checkpoint()!=raw:
                raise ValueError("V25_NONCANONICAL_CHECKPOINT")
            return o
        except (ValueError,TypeError,KeyError,AttributeError) as exc:
            raise ValueError("UNTRUSTED_V25_CHECKPOINT") from exc
