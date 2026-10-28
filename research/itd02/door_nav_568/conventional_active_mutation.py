"""Independent conventional active-learning version-space baseline.

Receives exactly the same source bits, mutation hypothesis family and
completed public feedback; uses explicit truth tables rather than local cells.
"""
from unrestricted_operation_cells import INPUTS
from risk_aware_drift_probe import MUTATIONS

class ConventionalActiveMutation:
    def __init__(self,source_mask):
        self.candidates=[tuple(bool((source_mask^delta)>>i&1)
                               for i in range(4)) for delta in MUTATIONS]
        self.observed={}
        self.target_observations=0

    def observe(self,key,label):
        if key not in INPUTS or type(label) is not bool or key in self.observed:
            raise ValueError("INVALID_PUBLIC_OBSERVATION")
        self.observed[key]=label
        index=INPUTS.index(key)
        self.candidates=[candidate for candidate in self.candidates
                         if candidate[index]==label]
        self.target_observations+=1

    def predict(self,key):
        if key not in INPUTS:raise ValueError("INVALID_PUBLIC_QUERY")
        outcomes={candidate[INPUTS.index(key)] for candidate in self.candidates}
        return next(iter(outcomes)) if len(outcomes)==1 else None

    def select_probe(self):
        if not self.candidates:return None
        best=None
        for index,key in enumerate(INPUTS):
            if key in self.observed:continue
            yes=sum(candidate[index] for candidate in self.candidates)
            score=(min(yes,len(self.candidates)-yes),-index,key)
            if best is None or score>best:best=score
        return best[2] if best is not None else None

    def count(self):
        return len(self.candidates)
