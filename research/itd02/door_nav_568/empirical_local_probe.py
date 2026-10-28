"""Empirical public-world memories for evidence-selected local probing.

Candidate explanations are formed only by complete public observations of
previous worlds; they are not supplied as possible operation masks. Each
completed world is a snapshot of four independently recorded Boolean slots.
The target-world identity is unavailable. The learned support is deliberately
limited: an unfamiliar truth table may be absent from memory.
"""
from unrestricted_operation_cells import INPUTS, TruthSlot

class EmpiricalLocalProbe:
    def __init__(self):
        self.memories=[]
        self._learning=[TruthSlot() for _ in INPUTS]
        self._candidate_indices=[]
        self.observed={}
        self.target_actions=0

    def observe_source(self,key,outcome):
        if key not in INPUTS or type(outcome) is not bool:
            raise ValueError("PUBLIC_SOURCE_REQUIRED")
        self._learning[INPUTS.index(key)].observe(outcome)

    def close_source(self):
        values=tuple(cell.value() for cell in self._learning)
        if any(v is None for v in values):
            raise ValueError("SOURCE_EVIDENCE_INCOMPLETE")
        if values not in self.memories:
            if len(self.memories)>=16:
                raise ValueError("SOURCE_WORLD_CAP")
            self.memories.append(values)
        self._learning=[TruthSlot() for _ in INPUTS]

    def begin_target(self):
        if not self.memories or self.observed:
            raise ValueError("TARGET_START_INVALID")
        self._candidate_indices=list(range(len(self.memories)))

    def observe_target(self,key,outcome):
        if key not in INPUTS or type(outcome) is not bool or key in self.observed:
            raise ValueError("TARGET_PUBLIC_FEEDBACK_INVALID")
        if not self._candidate_indices:
            raise ValueError("NO_COMPATIBLE_SOURCE_MEMORY")
        index=INPUTS.index(key)
        self._candidate_indices=[i for i in self._candidate_indices
                                 if self.memories[i][index]==outcome]
        self.observed[key]=outcome
        self.target_actions+=1

    def select_probe(self):
        if not self._candidate_indices:return None
        options=[]
        for index,key in enumerate(INPUTS):
            if key in self.observed:continue
            yes=sum(self.memories[i][index] for i in self._candidate_indices)
            no=len(self._candidate_indices)-yes
            options.append((min(yes,no),-index,key))
        return max(options)[2] if options else None

    def predict(self,key):
        if key not in INPUTS:raise ValueError("PUBLIC_KEY_REQUIRED")
        if not self._candidate_indices:return None
        values={self.memories[i][INPUTS.index(key)] for i in self._candidate_indices}
        return next(iter(values)) if len(values)==1 else None

    def remaining(self):
        return len(self._candidate_indices)
