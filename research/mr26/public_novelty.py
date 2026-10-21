"""MR26: source-independent bounded exploration of original PUBLIC MiniGrid images.

No object/class decoding. No goal, reward, map, agent world coordinates,
door/key identity, teacher action, prior secrets or evaluator feedback.
Learns only WHICH native actions have yielded PUBLIC image novelty before.
The action distribution and bounded memory were fixed in frozen_protocol.json
BEFORE this implementation. No Yggdrasil model weights are trained.
"""
from collections import OrderedDict
import hashlib
import json
import random

from research.mr15.public_view_delta import public_raw_view

BASE=(18,18,46,7,3,8)
CAP=128


def original_public_image_key(image):
    # Reads COMPLETE original PUBLIC image (not a native env or map).
    if (getattr(image,"shape",None)!=(7,7,3) or
        getattr(getattr(image,"dtype",None),"name",None)!="uint8"):
        raise ValueError("MR26_ORIGINAL_PUBLIC_UINT8_FRAME_REQUIRED")
    # Existing MR15 contract separately verifies sampled public bytes.
    if len(public_raw_view(image))!=24:
        raise ValueError("MR26_ORIGINAL_PUBLIC_SAMPLED_CUSTODY")
    return hashlib.sha256(image.tobytes()).digest()


class BoundedPublicNoveltyExplorer:
    __slots__=("rng","visited","attempts","discoveries","actions","total_new")

    def __init__(self,seed):
        if type(seed) is not int or seed<0:
            raise ValueError("MR26_SOURCE_SEED_INVALID")
        self.rng=random.Random(1000003*seed+337)
        self.visited=OrderedDict()
        self.attempts=[0]*6
        self.discoveries=[0]*6
        self.actions=[0]*6
        self.total_new=0

    def _admit(self,key):
        if key in self.visited:
            # FIFO order remains insertion order, never secret-dependent.
            return False
        if len(self.visited)>=CAP:
            self.visited.popitem(last=False)
        self.visited[key]=[0]*6
        return True

    def choose(self,public_image):
        key=original_public_image_key(public_image)
        self._admit(key)
        local=self.visited[key]
        # Frozen formula: BASE[action] times local action coverage bonus
        # times GLOBAL empirical public-novelty success estimate. Raw
        # image hashes are not decoded into semantic object identities.
        weights=[
            BASE[a]*(1.0+3.0/(1.0+local[a]))*
            (0.5+(1.0+self.discoveries[a])/(2.0+self.attempts[a]))
            for a in range(6)
        ]
        limit=sum(weights)
        pick=self.rng.random()*limit
        chosen=5
        for a,weight in enumerate(weights):
            pick-=weight
            if pick<0:
                chosen=a
                break
        local[chosen]+=1
        self.attempts[chosen]+=1
        self.actions[chosen]+=1
        return chosen

    def observe_original_next_public_image(self,action,next_public_image):
        if type(action) is not int or not 0<=action<6:
            raise ValueError("MR26_INVALID_ORIGINAL_ACTION")
        key=original_public_image_key(next_public_image)
        new=self._admit(key)
        if new:
            self.discoveries[action]+=1
            self.total_new+=1
        return new

    def snapshot(self):
        state={
            "schema":"yggdrasil.mr26.public-novelty.fifo.v1",
            "visited":[[k.hex(),v] for k,v in self.visited.items()],
            "attempts":self.attempts,
            "discoveries":self.discoveries,
            "actions":self.actions,
            "total_new":self.total_new,
            "rng":None,
        }
        # RNG serialization is not needed for qualification, and is
        # intentionally NOT called a durable restart qualification.
        return json.dumps(state,sort_keys=True,separators=(",",":"))

    def extra_untrained_policy_bytes(self):
        return len(self.snapshot().encode("utf-8"))

    def validate(self):
        if (len(self.visited)>CAP or
            len(self.actions)!=6 or
            any(type(v) is not int or v<0 for v in self.attempts) or
            self.actions!=self.attempts or
            any(d>a for d,a in zip(self.discoveries,self.attempts))):
            raise ValueError("MR26_BOUNDED_POLICY_CUSTODY_FAILED")
