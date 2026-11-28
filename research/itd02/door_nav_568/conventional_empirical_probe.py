"""Independent conventional empirical-table memory and probe control.

This implementation stores complete source-world tuples directly, and
does not import candidate code or hardcode source-world hypotheses.
"""
from unrestricted_operation_cells import INPUTS

class ConventionalEmpiricalProbe:
    def __init__(self):
        self.archive=[]
        self.pending={}
        self.candidates=[]
        self.observed={}
        self.target_actions=0

    def observe_source(self,key,label):
        if key not in INPUTS or type(label) is not bool:
            raise ValueError("PUBLIC_SOURCE_REQUIRED")
        counts=self.pending.setdefault(key,[0,0])
        counts[int(label)]+=1

    def close_source(self):
        if len(self.pending)!=4:
            raise ValueError("SOURCE_NOT_COMPLETE")
        values=[]
        for key in INPUTS:
            counts=self.pending[key]
            if sum(counts)<2 or counts[0]==counts[1]:
                raise ValueError("SOURCE_AMBIGUOUS")
            values.append(counts[1]>counts[0])
        record=tuple(values)
        if record not in self.archive:self.archive.append(record)
        self.pending={}

    def begin_target(self):
        if not self.archive or self.observed:
            raise ValueError("TARGET_START_INVALID")
        self.candidates=list(self.archive)

    def observe_target(self,key,label):
        if key not in INPUTS or type(label) is not bool or key in self.observed:
            raise ValueError("PUBLIC_TARGET_REQUIRED")
        if not self.candidates:raise ValueError("NO_COMPATIBLE_SOURCE_MEMORY")
        i=INPUTS.index(key)
        self.candidates=[table for table in self.candidates if table[i]==label]
        self.observed[key]=label
        self.target_actions+=1

    def select_probe(self):
        if not self.candidates:return None
        best=None
        for i,key in enumerate(INPUTS):
            if key in self.observed:continue
            yes=sum(table[i] for table in self.candidates)
            next_score=(min(yes,len(self.candidates)-yes),-i,key)
            if best is None or next_score>best:best=next_score
        return best[2] if best else None

    def predict(self,key):
        if key not in INPUTS:raise ValueError("PUBLIC_KEY_REQUIRED")
        if not self.candidates:return None
        values={table[INPUTS.index(key)] for table in self.candidates}
        return next(iter(values)) if len(values)==1 else None

    def remaining(self):
        return len(self.candidates)
