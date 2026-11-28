"""Active local evidence selection when candidate probes differ in information.

The fixed source-independent family (0000,0001,0011,0111) is disclosed
to BOTH arms. They do not see which of its four target worlds is correct.
One probe divides it 2:2, another 1:3. These masks are a fixed stress
fixture, not an inferred prior or a hidden task identity.
"""
from unrestricted_operation_cells import INPUTS

HYPOTHESES=(0,1,3,7)

class LocalAsymmetricProbe:
    def __init__(self):
        self.slots={key:{mask for mask in HYPOTHESES} for key in INPUTS}
        self.remaining=set(HYPOTHESES)
        self.observed={}
        self.actions=0

    @staticmethod
    def bit(mask,key):
        return bool((mask>>INPUTS.index(key))&1)

    def observe(self,key,label):
        if key not in INPUTS or type(label) is not bool or key in self.observed:
            raise ValueError("PUBLIC_PROBE_INVALID")
        self.remaining={mask for mask in self.remaining if self.bit(mask,key)==label}
        self.observed[key]=label
        self.actions+=1
        # Each local slot retains the same surviving public evidence; the
        # shared candidate-set update is a demonstrator, not native R7.
        for slot in self.slots.values():
            slot.intersection_update(self.remaining)

    def predict(self,key):
        if key not in INPUTS:raise ValueError("PUBLIC_INPUT_INVALID")
        if not self.remaining:return None
        answers={self.bit(mask,key) for mask in self.slots[key]}
        return next(iter(answers)) if len(answers)==1 else None

    def choose(self):
        if not self.remaining:return None
        scores=[]
        for i,key in enumerate(INPUTS):
            if key in self.observed:continue
            yes=sum(self.bit(mask,key) for mask in self.remaining)
            no=len(self.remaining)-yes
            scores.append((min(yes,no),-i,key))
        return max(scores)[2] if scores else None

    def candidate_count(self):
        return len(self.remaining)
