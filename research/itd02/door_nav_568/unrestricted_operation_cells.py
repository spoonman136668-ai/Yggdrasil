"""Four local public consequence slots: unrestricted two-input operations.

All 16 Boolean compositions are possible. Each local cell owns one
observable intermediate-message conjunction and two-count evidence.
The posterior is the set of all truth tables consistent with completed,
corroborated PUBLIC outcomes. Abstain unless every possible table agrees.

Unlike the previous six-operation fixture, this includes unfamiliar logic
functions and does not silently privilege any one hypothesis.
"""
from itertools import product

INPUTS=tuple(product((False,True),repeat=2))

class TruthSlot:
    def __init__(self):
        self.counts=[0,0]
        self.observations=0

    def observe(self,result):
        if type(result) is not bool:
            raise ValueError("COMPLETED_PUBLIC_BOOLEAN_REQUIRED")
        self.counts[int(result)]+=1
        self.observations+=1

    def value(self):
        if sum(self.counts)<2 or self.counts[0]==self.counts[1]:
            return None
        return self.counts[1]>self.counts[0]

class UnrestrictedMessageCells:
    def __init__(self):
        self.cells={inputs:TruthSlot() for inputs in INPUTS}
        self.observations=0

    @staticmethod
    def check(inputs):
        if type(inputs) is not tuple or len(inputs)!=2 or any(type(x) is not bool for x in inputs):
            raise ValueError("PUBLIC_MESSAGE_PAIR_REQUIRED")

    def observe(self,inputs,public_outcome):
        self.check(inputs)
        self.cells[inputs].observe(public_outcome)
        self.observations+=1

    def possible_operations(self):
        out=[]
        for mask in range(16):
            if all((truth:=slot.value()) is None or
                   bool((mask>>INPUTS.index(inputs))&1)==truth
                   for inputs,slot in self.cells.items()):
                out.append(mask)
        return tuple(out)

    def predict(self,inputs):
        self.check(inputs)
        possible=self.possible_operations()
        if not possible:return None
        values={bool(mask>>INPUTS.index(inputs)&1) for mask in possible}
        return next(iter(values)) if len(values)==1 else None

    def informative_probe(self,exclude=()):
        """Suggest an unresolved public message pair, never its outcome."""
        if any(x not in INPUTS for x in exclude):
            raise ValueError("UNKNOWN_EXCLUSION")
        options=self.possible_operations()
        if not options:return None
        scores=[]
        for inputs in INPUTS:
            if inputs in exclude:continue
            maskbit=INPUTS.index(inputs)
            yes=sum(bool(op>>maskbit&1) for op in options)
            no=len(options)-yes
            if min(yes,no)>0:
                scores.append((min(yes,no),-maskbit,inputs))
        return max(scores)[2] if scores else None
