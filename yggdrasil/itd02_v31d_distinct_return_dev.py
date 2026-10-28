"""V31D fixed distinct-public-history corroboration; development only."""
from .itd02_v31b_public_surprise_dev import PublicSurpriseRingDev
from .itd02_v17_neighbor_carried_learner_dev import ACTIONS
from .itd02_v18_intermediate_plasticity_dev import _valid_finite,REWARD_LIMITS
class DistinctReturnRingDev(PublicSurpriseRingDev):
 def __init__(self,source_checkpoint):
  super().__init__(source_checkpoint)
  self.public_history=[]
 def accept_second(self,selected,reward,*,learning=True,terminal=True):
  if type(selected) is not str or selected not in ACTIONS:raise ValueError("INVALID_SELECTED")
  if not _valid_finite(reward,*REWARD_LIMITS):raise ValueError("INVALID_PUBLIC_REWARD")
  if type(learning) is not bool or type(terminal) is not bool or not terminal:
   raise ValueError("INVALID_TERMINAL")
  if self.bank.fast.first is None:raise ValueError("MISSING_PUBLIC_CONTEXT")
  if learning:
   identity=(self.bank.fast.cue,self.bank.fast.first,selected)
   es=abs(reward-self.bank.source_score(selected))
   ef=abs(reward-self.bank.fast_score(selected))
   prior=self.fast
  # Original V31B applies its own decision; restore only its decision readout
  # before applying V31D's predeclared return gate. Bank feedback is identical.
  super().accept_second(selected,reward,learning=learning,terminal=terminal)
  if learning:
   self.public_history=(self.public_history+[(identity,es,ef)])[-3:]
   new=self.fast
   if prior:
    recent=self.public_history[-2:]
    new=not(len(recent)==2 and recent[0][0]!=recent[1][0]
       and all(f-s>=.15 for _,s,f in recent) and es<=.50)
   if new!=self.fast:self.switches+=int(new)-int(self.fast)
   self.fast=new
