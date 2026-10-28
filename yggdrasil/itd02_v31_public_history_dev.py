"""V31 development-only public-history error calibration; Q holdout not imported.

A bounded per-context reward-history residual gate, separate from V25/V26
rolling votes. The original V22 cells remain independent and unchanged.
"""
from collections import deque
from .itd02_v24_protected_dual_memory_dev import ProtectedDualMemoryRingDev
from .itd02_v17_neighbor_carried_learner_dev import ACTIONS
from .itd02_v18_intermediate_plasticity_dev import REWARD_LIMITS,_valid_finite

class PublicHistoryGate:
    """Hand-written controller, not original local neural cognition."""
    def __init__(self,source_checkpoint):
        self.bank=ProtectedDualMemoryRingDev(source_checkpoint)
        self.history=deque(maxlen=12)
        self.fast=False
        self.switches=0

    def start_observation(self,cue):
        self.bank.start_observation(cue)
    def accept_first(self,first,next_observation="Nothing",reward=0):
        self.bank.accept_first(first,next_observation,reward)
    def score(self,action):
        return self.bank.fast_score(action) if self.fast else self.bank.source_score(action)
    def scores(self):
        return [self.score(a) for a in ACTIONS]

    def accept_second(self,selected,reward,*,learning=True,terminal=True):
        if selected not in ACTIONS or type(selected) is not str:
            raise ValueError("INVALID_ACTUAL_SECOND_ACTION")
        if not _valid_finite(reward,*REWARD_LIMITS):
            raise ValueError("INVALID_ACTUAL_PUBLIC_REWARD")
        if type(learning) is not bool or type(terminal) is not bool or not terminal:
            raise ValueError("INVALID_TERMINAL_STATE")
        if self.bank.fast.cue is None or self.bank.fast.first is None:
            raise ValueError("MISSING_ACTUAL_PUBLIC_CONTEXT")
        if learning:
            context=(self.bank.fast.cue,self.bank.fast.first,selected)
            slow=self.bank.source_score(selected)
            fast=self.bank.fast_score(selected)
        self.bank.accept_second(selected,reward,learning=learning,terminal=terminal)
        if learning:
            # Long-range context-linked observed rewards (no hidden returns,
            # unselected action reward, or evaluator stage hints).
            self.history.append((context,float(reward),float(slow),float(fast)))
            # Compare bank accuracy over recent DISTINCT public contexts;
            # cap leverage of repeated context to one most recent actual reward.
            last={}
            for ctx,y,s,f in self.history:
                last[ctx]=(y,s,f)
            evidence=[abs(y-s)-abs(y-f) for y,s,f in last.values()]
            advantage=sum(evidence)/len(evidence)
            next_fast=self.fast
            if len(last)>=4 and advantage>.30:
                next_fast=True
            elif len(last)>=4 and advantage<-.30:
                next_fast=False
            if next_fast!=self.fast:self.switches+=1
            self.fast=next_fast
