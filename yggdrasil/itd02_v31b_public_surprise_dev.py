"""V31B preregistered public-only surprise detector, dev-only."""
from .itd02_v24_protected_dual_memory_dev import ProtectedDualMemoryRingDev
from .itd02_v17_neighbor_carried_learner_dev import ACTIONS
from .itd02_v18_intermediate_plasticity_dev import REWARD_LIMITS,_valid_finite

class PublicSurpriseRingDev:
 def __init__(self,source_checkpoint):
  self.bank=ProtectedDualMemoryRingDev(source_checkpoint)
  self.fast=False;self.recent=[];self.switches=0
 def start_observation(self,cue):self.bank.start_observation(cue)
 def accept_first(self,first,next_observation="Nothing",reward=0):
  self.bank.accept_first(first,next_observation,reward)
 def score(self,selected):
  return self.bank.fast_score(selected) if self.fast else self.bank.source_score(selected)
 def scores(self):return [self.score(a) for a in ACTIONS]
 def accept_second(self,selected,reward,*,learning=True,terminal=True):
  if type(selected) is not str or selected not in ACTIONS:raise ValueError("INVALID_PUBLIC_ACTION")
  if not _valid_finite(reward,*REWARD_LIMITS):raise ValueError("INVALID_PUBLIC_REWARD")
  if type(learning) is not bool or type(terminal) is not bool or not terminal:
   raise ValueError("INVALID_TERMINAL")
  if self.bank.fast.first is None:raise ValueError("PUBLIC_FIRST_ACTION_NOT_SEEN")
  if learning:
   es=abs(reward-self.bank.source_score(selected))
   ef=abs(reward-self.bank.fast_score(selected))
  self.bank.accept_second(selected,reward,learning=learning,terminal=terminal)
  if learning:
   self.recent=(self.recent+[(es,ef)])[-3:]
   old=self.fast
   if not self.fast and sum(s>=1.0 and s-f>=.15 for s,f in self.recent)>=2:
    self.fast=True
   elif self.fast and len(self.recent)>=2 and all(f-s>=.15 for s,f in self.recent[-2:]):
    self.fast=False
   self.switches+=int(old!=self.fast)
