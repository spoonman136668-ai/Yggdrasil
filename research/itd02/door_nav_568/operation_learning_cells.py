"""Bounded local evidence selects composition operations from public outcomes.

The six candidate operations are hypotheses, not regime labels or supplied
answers. At prediction time every surviving operation must agree or the
cell abstains. Candidate pruning uses completed public outcomes only.
"""
from compositional_local_cells import CompositionalLocalCells

class OperationMessageCell:
    def __init__(self):
        self.evidence={}
        self.observations=0

    @staticmethod
    def operations(a,b):
        x=a ^ b
        y=a and b
        z=a or b
        return (x,not x,y,not y,z,not z)

    def observe(self,inputs,outcome):
        if (type(inputs) is not tuple or len(inputs)!=2 or
            any(type(v) is not bool for v in inputs) or type(outcome) is not bool):
            raise ValueError("PUBLIC_OPERATION_REQUIRED")
        if inputs not in self.evidence and len(self.evidence)>=4:
            raise ValueError("OPERATION_MEMORY_LIMIT")
        counts=self.evidence.setdefault(inputs,[0,0])
        counts[int(outcome)]+=1
        self.observations+=1

    def survivors(self):
        possibilities=set(range(6))
        confirmed=0
        for inputs,counts in self.evidence.items():
            if sum(counts)<2 or counts[0]==counts[1]:
                continue
            confirmed+=1
            observed=counts[1]>counts[0]
            predictions=self.operations(*inputs)
            possibilities={i for i in possibilities if predictions[i]==observed}
        return possibilities if confirmed>=2 else set()

    def predict(self,inputs):
        survivors=self.survivors()
        if not survivors:return None
        predictions=self.operations(*inputs)
        answers={predictions[i] for i in survivors}
        return next(iter(answers)) if len(answers)==1 else None

class OperationLearningCells(CompositionalLocalCells):
    def __init__(self):
        super().__init__()
        self.exchange=OperationMessageCell()
