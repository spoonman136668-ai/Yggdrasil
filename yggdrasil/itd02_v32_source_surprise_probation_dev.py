"""V32 opt-in PUBLIC selected-reward source-surprise probation, source-only.

Externally engineered source/fast selector over unchanged native V22/V26
protected banks. Not native learned gating or independent scientific first use.
"""
import hashlib
import json
from .itd02_v17_neighbor_carried_learner_dev import ACTIONS,canonical
from .itd02_v18_intermediate_plasticity_dev import _valid_finite,REWARD_LIMITS
from .itd02_v26_calibrated_return_dev import CalibratedReturnRingDev

SCHEMA="ygg.itd02.v32.source_surprise_probation.source_only.v1"
SOURCE_SURPRISE=1.50
RETURN_MARGIN=0.20
RETURN_STREAK=2
MAX_CHECKPOINT=12288


class SourceSurpriseProbationDev:
    """One fixed public-only selector, independently checkpointed."""

    def __init__(self,source_checkpoint):
        self.model=CalibratedReturnRingDev(source_checkpoint)
        self.use_fast=False
        self.streak=0
        self.switches=0
        self.events=0
        self.frozen_sha=None

    @property
    def bank(self):
        return self.model.bank

    def parameters_sha256(self):
        return hashlib.sha256(canonical({
            "model":self.model.parameters_sha256(),
            "use_fast":self.use_fast,
            "streak":self.streak,
            "switches":self.switches,
            "events":self.events})).hexdigest()

    def _guard(self):
        self.model.guard()
        if self.frozen_sha is not None and self.parameters_sha256()!=self.frozen_sha:
            raise ValueError("V32_FROZEN_SELECTOR_OR_NATIVE_DRIFT")

    def start_observation(self,cue):
        self._guard()
        self.model.start_observation(cue)

    def accept_first(self,actual_first,next_observation="Nothing",reward=0):
        self._guard()
        self.model.accept_first(actual_first,next_observation,reward)

    def source_score(self,selected):
        self._guard()
        return self.bank.source_score(selected)

    def fast_score(self,selected):
        self._guard()
        return self.bank.fast_score(selected)

    def score(self,selected):
        self._guard()
        return self.fast_score(selected) if self.use_fast else self.source_score(selected)

    def scores(self):
        return [self.score(a) for a in ACTIONS]

    def accept_second(self,selected,public_reward,*,learning=True,terminal=True):
        self._guard()
        if type(selected) is not str or selected not in ACTIONS:
            raise ValueError("V32_INVALID_SELECTED_SECOND_ACTION")
        if not _valid_finite(public_reward,*REWARD_LIMITS):
            raise ValueError("V32_INVALID_PUBLIC_REWARD")
        if type(learning) is not bool or type(terminal) is not bool or not terminal:
            raise ValueError("V32_INVALID_PUBLIC_TERMINAL")
        if learning and self.frozen_sha is not None:
            raise ValueError("V32_LEARNING_FORBIDDEN_WHILE_FROZEN")
        if self.bank.fast.first is None or self.bank.slow.first is None:
            raise ValueError("V32_ACTUAL_FIRST_OBSERVATION_REQUIRED")
        if learning:
            source=self.bank.source_score(selected)
            fast=self.bank.fast_score(selected)
        self.model.accept_second(selected,public_reward,learning=learning,terminal=terminal)
        if learning:
            source_error=abs(float(public_reward)-source)
            fast_error=abs(float(public_reward)-fast)
            before=self.use_fast
            if not self.use_fast:
                if source_error>=SOURCE_SURPRISE:
                    self.use_fast=True
                    self.streak=0
            else:
                self.streak=(self.streak+1 if source_error+RETURN_MARGIN<=fast_error else 0)
                if self.streak>=RETURN_STREAK:
                    self.use_fast=False
                    self.streak=0
            self.events+=1
            self.switches+=int(before!=self.use_fast)
        self._guard()

    def start_frozen_evaluation(self):
        self._guard()
        self.model.start_frozen_evaluation()
        self.frozen_sha=self.parameters_sha256()

    def checkpoint(self):
        self._guard()
        body={"schema":SCHEMA,"v26":json.loads(self.model.checkpoint()),
              "use_fast":self.use_fast,"streak":self.streak,
              "switches":self.switches,"events":self.events,
              "frozen_sha":self.frozen_sha}
        raw=canonical(body)
        data=canonical({"body":body,"sha256":hashlib.sha256(raw).hexdigest()})
        if len(data)>MAX_CHECKPOINT:
            raise ValueError("V32_CHECKPOINT_OVER_BUDGET")
        return data

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=MAX_CHECKPOINT:
                raise ValueError("V32_SIZE")
            packet=json.loads(raw)
            if type(packet) is not dict or set(packet)!={"body","sha256"}:
                raise ValueError("V32_ENVELOPE")
            b=packet["body"]
            keys={"schema","v26","use_fast","streak","switches","events","frozen_sha"}
            if type(b) is not dict or set(b)!=keys or b["schema"]!=SCHEMA:
                raise ValueError("V32_BODY")
            if type(packet["sha256"]) is not str or hashlib.sha256(canonical(b)).hexdigest()!=packet["sha256"]:
                raise ValueError("V32_DIGEST")
            model=CalibratedReturnRingDev.restore(canonical(b["v26"]))
            if (type(b["use_fast"]) is not bool or
                type(b["streak"]) is not int or b["streak"] not in (0,1) or
                type(b["events"]) is not int or b["events"]<0 or
                b["events"]!=model.bank.target_updates or
                type(b["switches"]) is not int or not 0<=b["switches"]<=b["events"] or
                (not b["use_fast"] and b["streak"]!=0)):
                raise ValueError("V32_SELECTOR_PROVENANCE")
            x=cls.__new__(cls)
            x.model=model
            x.use_fast=b["use_fast"]
            x.streak=b["streak"]
            x.switches=b["switches"]
            x.events=b["events"]
            x.frozen_sha=b["frozen_sha"]
            if x.frozen_sha is not None and (
                type(x.frozen_sha) is not str or len(x.frozen_sha)!=64 or
                model.frozen_sha is None or x.parameters_sha256()!=x.frozen_sha):
                raise ValueError("V32_FROZEN_SHA")
            if x.checkpoint()!=raw:
                raise ValueError("V32_NONCANONICAL")
            return x
        except (ValueError,TypeError,KeyError,AttributeError,OverflowError) as exc:
            raise ValueError("UNTRUSTED_V32_CHECKPOINT") from exc
