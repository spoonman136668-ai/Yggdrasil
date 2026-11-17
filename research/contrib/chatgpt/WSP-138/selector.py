"""WSP138 exact-behavior lazy version-space selection.

Original baseline WSP137 imported by exact file path unchanged. This module
does not import WSP138 source, hidden grammar, oracle, or evaluator data.
"""
from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

PATH=Path(__file__).resolve().parents[1]/'WSP-137'/'policy.py'
SPEC=spec_from_file_location('_wsp138_qualified_wsp137_policy',PATH)
BASE=module_from_spec(SPEC)
sys.modules[SPEC.name]=BASE
SPEC.loader.exec_module(BASE)
N=BASE.N
common_held=BASE.common_held
available_pool=BASE.available_pool
fixed_schedule=BASE.fixed_schedule

@lru_cache(maxsize=1)
def original_ranked():
    # Source-independent exact Git-pinned WSP137 SHA256 template ordering.
    return BASE.candidate_preference()

class LazyPolicy:
    """Recompute only first256 *current* surviving candidates from paid effects."""
    def __init__(self):
        self.bank=N.templates()
        self.ranked=original_ranked()
        n=len(self.bank)
        self.invalid=bytearray(n)
        self.seen=[0]*n
        self.ones=[0]*n
        self.processed=[0]*n
        self.events=[]
        self.pending=None
    def _sync(self,i):
        if self.invalid[i]:return False
        bank=self.bank[i]
        mask=self.seen[i]
        positive=self.ones[i]
        j=self.processed[i]
        # Apply exactly the full paid observation history in original order.
        while j<len(self.events):
            x,y=self.events[j]
            bit=1<<bank[x]
            if mask&bit:
                if bool(positive&bit)!=bool(y):
                    self.invalid[i]=1
                    self.processed[i]=len(self.events)
                    return False
            else:
                mask|=bit
                if y:positive|=bit
            j+=1
        self.seen[i]=mask
        self.ones[i]=positive
        self.processed[i]=j
        return True
    def choose(self,legal):
        if len(self.events)>=32:return None
        used={x for x,y in self.events}
        pool=[x for x in legal if x not in used]
        if not pool:raise ValueError('WSP138_NO_PUBLIC_ACTIONS')
        if len(self.events)<4:
            pick=fixed_schedule()[len(self.events)]
            if pick not in pool:raise ValueError('WSP138_MISSING_FIRST4')
        else:
            selected=[]
            for i in self.ranked:
                if self._sync(i):
                    selected.append(i)
                    if len(selected)>=256:break
            if not selected:
                left=[x for x in fixed_schedule() if x in pool]
                pick=left[0] if left else min(pool)
            else:
                choices=[]
                for x in pool:
                    pos=neg=unseen=0
                    for i in selected:
                        bit=1<<self.bank[i][x]
                        if not self.seen[i]&bit:unseen+=1
                        elif self.ones[i]&bit:pos+=1
                        else:neg+=1
                    choices.append((min(pos,neg),unseen,-x,x))
                pick=max(choices)[-1]
        self.pending=pick
        return pick
    def observe(self,x,y):
        if (x!=self.pending or x in {a for a,b in self.events}
                or len(self.events)>=32 or type(y) is not int or y not in (0,1)):
            raise ValueError('WSP138_LAZY_UNEXPECTED_SOURCE_EFFECT')
        self.events.append((x,y))
        self.pending=None
    def structural_capacity_bytes(self):
        # Explicit lower-bound structural model; does not claim Python heap total.
        return len(self.bank)*(3*4+1) # three integer bitset/cursor handles, one invalid byte

class FastArm(BASE.DirectArm):
    """Use the original validated WSP137 receipt+fit+predict+snapshot path,
    replacing ONLY transient action-selection machinery.
    """
    def _state(self,view,create=False):
        st=self.states.get(view.law_id)
        if st is None and create:
            if view.cohort!='probe':raise PermissionError('WSP138_ZERO_SOURCE_TRANSFER_TRAIN')
            st={'fingerprint':view.fingerprint(),'receipt':BASE.digest([view.fingerprint(),'begin']),
                'events':[],'chosen':[]}
            if self.policy=='active':st['chooser']=LazyPolicy()
            self.states[view.law_id]=st
        if st is not None and view.cohort=='probe' and st['fingerprint']!=view.fingerprint():
            raise ValueError('WSP138_PUBLIC_VIEW_DRIFT')
        return st
