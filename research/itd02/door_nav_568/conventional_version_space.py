"""Independent conventional version-space control for all binary operations.

It reads the identical completed public outcome stream. This conventional
implementation maintains consistent candidate masks directly, not cell
states. Observed outcomes require two identical public examples.
"""
from unrestricted_operation_cells import INPUTS

class ConventionalVersionSpace:
    def __init__(self):
        self.remaining=set(range(16))
        self.counts={}
        self.observations=0

    def observe(self,inputs,result):
        if inputs not in INPUTS or type(result) is not bool:
            raise ValueError("PUBLIC_FEEDBACK_INVALID")
        data=self.counts.setdefault(inputs,[0,0])
        data[int(result)]+=1
        self.observations+=1
        if sum(data)>=2 and data[0]!=data[1]:
            self.remaining={m for m in self.remaining if bool(m>>INPUTS.index(inputs)&1)==(data[1]>data[0])}

    def possible_operations(self):
        return tuple(sorted(self.remaining))

    def predict(self,inputs):
        if inputs not in INPUTS:raise ValueError("PUBLIC_INPUT_INVALID")
        answer={bool(mask>>INPUTS.index(inputs)&1) for mask in self.remaining}
        return next(iter(answer)) if len(answer)==1 else None

    def informative_probe(self,exclude=()):
        candidates=[]
        for inputs in INPUTS:
            if inputs in exclude:continue
            yes=sum((mask>>INPUTS.index(inputs))&1 for mask in self.remaining)
            no=len(self.remaining)-yes
            if min(yes,no)>0:candidates.append((min(yes,no),-INPUTS.index(inputs),inputs))
        return max(candidates)[2] if candidates else None
