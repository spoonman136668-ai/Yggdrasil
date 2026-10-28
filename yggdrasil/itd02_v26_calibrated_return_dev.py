"""V26 preregistered public-only hysteretic return selector, source-only."""
import hashlib,json,math
from .itd02_v17_neighbor_carried_learner_dev import ACTIONS,canonical
from .itd02_v18_intermediate_plasticity_dev import REWARD_LIMITS,_valid_finite
from .itd02_v24_protected_dual_memory_dev import ProtectedDualMemoryRingDev

SCHEMA="ygg.itd02.v26.hysteretic_return.source_only.v1"
LIMIT=12288

class CalibratedReturnRingDev:
    def __init__(self, source_checkpoint):
        self.bank=ProtectedDualMemoryRingDev(source_checkpoint)
        self.evidence=[]
        self.fast=False
        self.switches=0
        self.frozen_sha=None
    def parameters_sha256(self):
        return hashlib.sha256(canonical({
            "bank":self.bank.parameters_sha256(),"evidence":self.evidence,
            "fast":self.fast,"switches":self.switches})).hexdigest()
    def guard(self):
        self.bank._guard()
        if self.frozen_sha is not None and self.parameters_sha256()!=self.frozen_sha:
            raise ValueError("V26_FROZEN_SELECTOR_CHANGED")
    def start_observation(self,cue):
        self.guard();self.bank.start_observation(cue)
    def accept_first(self,action,next_observation="Nothing",reward=0):
        self.guard();self.bank.accept_first(action,next_observation,reward)
    def score(self,action):
        self.guard()
        return self.bank.fast_score(action) if self.fast else self.bank.source_score(action)
    def scores(self):
        return [self.score(x) for x in ACTIONS]
    def accept_second(self,selected,reward,*,learning=True,terminal=True):
        self.guard()
        if type(selected) is not str or selected not in ACTIONS:
            raise ValueError("INVALID_PUBLIC_SELECTED_ACTION")
        if not _valid_finite(reward,*REWARD_LIMITS):
            raise ValueError("INVALID_PUBLIC_REWARD")
        if type(learning) is not bool or type(terminal) is not bool or not terminal:
            raise ValueError("INVALID_TERMINAL")
        if learning and self.frozen_sha is not None:
            raise ValueError("FROZEN_EVALUATION_FORBIDS_LEARNING")
        if self.bank.fast.first is None or self.bank.slow.first is None:
            raise ValueError("MISSING_ACTUAL_FIRST_PUBLIC_ACTION")
        if learning:
            source=self.bank.source_score(selected)
            fast=self.bank.fast_score(selected)
        self.bank.accept_second(selected,reward,learning=learning,terminal=terminal)
        if learning:
            d=max(-4.0,min(4.0,abs(reward-fast)-abs(reward-source)))
            self.evidence=(self.evidence+[d])[-4:]
            previous=self.fast
            if len(self.evidence)>=3:
                if self.fast and (all(x>=.15 for x in self.evidence[-2:]) and
                        sum(x>=.05 for x in self.evidence)>=3):
                    self.fast=False
                elif not self.fast and (all(x<=-.15 for x in self.evidence[-2:]) and
                        sum(x<=-.05 for x in self.evidence)>=3):
                    self.fast=True
            self.switches+=int(self.fast!=previous)
        self.guard()
    def start_frozen_evaluation(self):
        self.guard()
        if self.bank.fast.cue is not None:
            raise ValueError("PENDING_PUBLIC_EPISODE")
        self.bank.start_frozen_evaluation()
        self.frozen_sha=self.parameters_sha256()
    def checkpoint(self):
        self.guard()
        body={"schema":SCHEMA,"bank":json.loads(self.bank.checkpoint()),
              "evidence":self.evidence,"fast":self.fast,
              "switches":self.switches,"frozen_sha":self.frozen_sha}
        payload=canonical(body)
        if len(payload)>LIMIT:raise ValueError("V26_CHECKPOINT_OVER_BUDGET")
        return canonical({"body":body,"sha256":hashlib.sha256(payload).hexdigest()})
    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<=LIMIT:
                raise ValueError("SIZE")
            packet=json.loads(raw)
            if type(packet) is not dict or set(packet)!={"body","sha256"}:
                raise ValueError("ENVELOPE")
            body=packet["body"]
            if (type(body) is not dict or
                set(body)!={"schema","bank","evidence","fast","switches","frozen_sha"} or
                body["schema"]!=SCHEMA or
                hashlib.sha256(canonical(body)).hexdigest()!=packet["sha256"]):
                raise ValueError("DIGEST")
            bank=ProtectedDualMemoryRingDev.restore(canonical(body["bank"]))
            data=body["evidence"]
            if (type(data) is not list or len(data)!=min(4,bank.target_updates)
                or any(type(x) not in (float,int) or not math.isfinite(x)
                       or not -4<=x<=4 for x in data)
                or type(body["fast"]) is not bool
                or type(body["switches"]) is not int
                or not 0<=body["switches"]<=bank.target_updates):
                raise ValueError("PUBLIC_EVIDENCE")
            o=cls.__new__(cls);o.bank=bank;o.evidence=data
            o.fast=body["fast"];o.switches=body["switches"]
            o.frozen_sha=body["frozen_sha"]
            if o.frozen_sha is not None and (
                type(o.frozen_sha) is not str or len(o.frozen_sha)!=64 or
                bank.frozen_sha is None or o.frozen_sha!=o.parameters_sha256()):
                raise ValueError("FROZEN")
            if o.checkpoint()!=raw:raise ValueError("NONCANONICAL")
            return o
        except (ValueError,TypeError,KeyError,AttributeError) as exc:
            raise ValueError("UNTRUSTED_V26_CHECKPOINT") from exc
