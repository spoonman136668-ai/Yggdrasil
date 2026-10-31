"""MR31 native public-only causal experience acquisition at matched actor budget.

No native learner changes: the experiment compares source-blind exploration
policies, not cognition. The candidate samples actions based on empirical
binary PUBLIC next-frame change ambiguity conditional on observed public
frame and action. It never sees a next frame until AFTER env.step.

Same bounded representation for candidate and unchanged MR26 formula:
128 FIFO source-public SHA256 keys, six uint32 counters per key, three
six-uint32 global arrays, same Python Random state and one prior key.
Candidate packs local action attempts in low 16 bits and observed change
count in high 16 bits. Original MR26 baseline uses the same uint32 per
action as ordinary visit counts. Both may use exactly the same worst-case
memory capacity; actual Python RSS is measured separately and never
misrepresented as full process parity.
"""
from array import array
from collections import OrderedDict
from hashlib import sha256
import json
import math
import pickle
import random
import sys

from research.mr26.public_novelty import (
    BoundedPublicNoveltyExplorer,original_public_image_key,BASE,CAP
)

MAX_LOCAL=65535
GATE=["novelty","contrast"]


class EqualCapacityPublicActor:
    def __init__(self,seed,mode,stream=0):
        if type(seed) is not int or seed<0 or mode not in GATE or type(stream) is not int or stream<0:
            raise ValueError("MR31_BAD_ACTOR_SEED_OR_POLICY")
        self.mode=mode
        self.rng=random.Random(1000003*seed+337+10007*stream)
        self.visited=OrderedDict()
        self.attempts=array("I",[0]*6)
        self.discoveries=array("I",[0]*6)
        self.actions=array("I",[0]*6)
        self.total_new=0
        self.last_key=None

    def _admit(self,key):
        if key in self.visited:
            return False
        if len(self.visited)>=CAP:
            self.visited.popitem(last=False)
        self.visited[key]=array("I",[0]*6)
        return True

    def choose(self,original_public_image):
        key=original_public_image_key(original_public_image)
        self._admit(key)
        local=self.visited[key]
        weights=[]
        for a in range(6):
            if self.mode=="novelty":
                n=local[a]
                weight=(BASE[a]*(1.+3./(1.+n))*
                    (0.5+(1.+self.discoveries[a])/
                    (2.+self.attempts[a])))
            else:
                n=local[a]&65535
                changes=local[a]>>16
                if changes>n or n>MAX_LOCAL-1:
                    raise ValueError("MR31_PACKED_EXPERIENCE_CAPACITY_EXHAUSTED")
                p=(changes+1.)/(n+2.)
                ambiguity=4.*p*(1.-p)
                weight=BASE[a]*(1.+3./(1.+n))*(0.25+0.75*ambiguity)
            if not math.isfinite(weight) or weight<=0:
                raise ValueError("MR31_INVALID_EXPLORATION_DISTRIBUTION")
            weights.append(weight)
        pick=self.rng.random()*sum(weights)
        selected=5
        for a,w in enumerate(weights):
            pick-=w
            if pick<0:
                selected=a
                break
        local[selected]+=1
        self.attempts[selected]+=1
        self.actions[selected]+=1
        self.last_key=key
        return selected

    def observe(self,action,next_original_public_image):
        if type(action) is not int or action not in range(6):
            raise ValueError("MR31_BAD_ORIGINAL_NATIVE_ACTION")
        if self.last_key is None:
            raise ValueError("MR31_NO_PREACTION_PUBLIC_HISTORY")
        key=original_public_image_key(next_original_public_image)
        novel=self._admit(key)
        if novel:
            self.total_new+=1
            self.discoveries[action]+=1
        if self.mode=="contrast" and self.last_key in self.visited:
            # Nothing private: changed public bytes is known ONLY
            # after the original native source action completes.
            if key!=self.last_key:
                self.visited[self.last_key][action]+=1<<16
        self.last_key=None
        self.validate()
        return novel

    def validate(self):
        if len(self.visited)>CAP or len(self.attempts)!=6 or (
            list(self.actions)!=list(self.attempts)):
            raise ValueError("MR31_EQUAL_ACTOR_BUDGET_BREACH")
        for key,local in self.visited.items():
            if type(key) is not bytes or len(key)!=32 or (
                type(local) is not array or local.typecode!="I" or
                local.itemsize!=4 or len(local)!=6):
                raise ValueError("MR31_MEMORY_LAYOUT_DRIFT")
            if self.mode=="contrast" and any(
                ((value>>16)>(value&65535)) for value in local):
                raise ValueError("MR31_IMPOSSIBLE_PUBLIC_CHANGE_COUNT")
        if any(d>a for d,a in zip(self.discoveries,self.attempts)):
            raise ValueError("MR31_NOVELTY_COUNTS_INVALID")

    def capacity_receipt(self):
        # These are structurally identical for BOTH policies. RNG bytes
        # are separately measured, not falsely ignored.
        self.validate()
        return {
            "max_fifo_entries":CAP,
            "digest_bytes_each":32,
            "local_action_counters_each":6,
            "uint32_bytes_each":4,
            "global_action_counters":18,
            "pending_previous_key_bytes_reserved":32,
            "max_fixed_payload_excluding_container_and_rng_bytes":
                CAP*(32+6*4)+18*4+32+4,
            "rng_getstate_pickle_bytes":len(pickle.dumps(
                self.rng.getstate(),protocol=4)),
            "actual_fifo_entries":len(self.visited),
            "actual_payload_excluding_container_and_rng_bytes":
                len(self.visited)*(32+6*4)+18*4+32+4,
            "measured_python_container_estimate_bytes":
                (sys.getsizeof(self.visited)+
                 sum(sys.getsizeof(k)+sys.getsizeof(v)
                     for k,v in self.visited.items())+
                 sum(sys.getsizeof(v) for v in (
                     self.attempts,self.discoveries,self.actions))+
                 sys.getsizeof(self.rng)),
        }


def baseline_equivalence_selftest():
    """Engineering parity to MR26 control, not a scientific benchmark."""
    import numpy as np
    ref=BoundedPublicNoveltyExplorer(601)
    ours=EqualCapacityPublicActor(601,"novelty")
    for i in range(149):
        image=np.full((7,7,3),i%251,dtype=np.uint8)
        action1=ref.choose(image)
        action2=ours.choose(image)
        if action1!=action2:
            raise ValueError("MR31_CONTROL_NOT_ORIGINAL_MR26_POLICY")
        nxt=np.full((7,7,3),(i*7+1)%251,dtype=np.uint8)
        novelty1=ref.observe_original_next_public_image(action1,nxt)
        novelty2=ours.observe(action2,nxt)
        if novelty1!=novelty2:
            raise ValueError("MR31_ORIGINAL_NOVELTY_CONTROL_DRIFT")
    if (list(ref.visited)!=list(ours.visited) or
        any(list(x)!=list(y) for x,y in zip(
            ref.visited.values(),ours.visited.values())) or
        list(ours.attempts)!=ref.attempts or
        list(ours.discoveries)!=ref.discoveries or
        list(ours.actions)!=ref.actions or
        ours.total_new!=ref.total_new):
        raise ValueError("MR31_BASELINE_SOURCE_CONTROL_NOT_EQUIVALENT")
    if EqualCapacityPublicActor(601,"contrast").capacity_receipt()[
        "max_fixed_payload_excluding_container_and_rng_bytes"]!=(
        ours.capacity_receipt()[
        "max_fixed_payload_excluding_container_and_rng_bytes"]):
        raise ValueError("MR31_UNMATCHED_ACTOR_CAPACITY")
    return True
