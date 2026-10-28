"""Independent conventional asymmetric version-space probe control."""
from unrestricted_operation_cells import INPUTS
from asymmetric_probe_cells import HYPOTHESES

class ConventionalAsymmetric:
    def __init__(self):
        self.tables=[tuple(bool(mask>>j&1) for j in range(4)) for mask in HYPOTHESES]
        self.candidates=list(self.tables)
        self.observed={}
        self.actions=0

    def observe(self,key,label):
        if key not in INPUTS or type(label) is not bool or key in self.observed:
            raise ValueError("PUBLIC_PROBE_INVALID")
        i=INPUTS.index(key)
        self.candidates=[table for table in self.candidates if table[i]==label]
        self.observed[key]=label
        self.actions+=1

    def predict(self,key):
        if key not in INPUTS:raise ValueError("PUBLIC_INPUT_INVALID")
        if not self.candidates:return None
        answers={table[INPUTS.index(key)] for table in self.candidates}
        return next(iter(answers)) if len(answers)==1 else None

    def choose(self):
        if not self.candidates:return None
        candidates=[]
        for i,key in enumerate(INPUTS):
            if key in self.observed:continue
            yes=sum(table[i] for table in self.candidates)
            no=len(self.candidates)-yes
            candidates.append((min(yes,no),-i,key))
        return max(candidates)[2] if candidates else None

    def candidate_count(self):
        return len(self.candidates)
