"""Independent conventional out-of-memory recovery using public tables."""
from conventional_empirical_probe import ConventionalEmpiricalProbe
from unrestricted_operation_cells import INPUTS

class RecoveringConventionalProbe(ConventionalEmpiricalProbe):
    def __init__(self):
        super().__init__()
        self.fallback=False
        self.target_counts={}
        self.public_feedback=0

    def observe_target(self,key,outcome):
        if key not in INPUTS or type(outcome) is not bool:
            raise ValueError("INVALID_PUBLIC_TARGET")
        bucket=self.target_counts.setdefault(key,[0,0])
        bucket[int(outcome)]+=1
        self.public_feedback+=1
        if key in self.observed:
            if self.observed[key]!=outcome:self.fallback=True
            return
        if self.fallback:
            self.observed[key]=outcome
            self.target_actions+=1
            return
        super().observe_target(key,outcome)
        if not self.candidates:self.fallback=True

    def predict(self,key):
        if key not in INPUTS:raise ValueError("INVALID_PUBLIC_KEY")
        if self.fallback:
            counts=self.target_counts.get(key,[0,0])
            return (counts[1]>counts[0]) if sum(counts)>=2 and counts[0]!=counts[1] else None
        return super().predict(key)

    def select_probe(self):
        if self.fallback:
            return next((key for key in INPUTS if key not in self.observed),None)
        return super().select_probe()
