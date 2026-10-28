"""Bounded risk-aware probing of retained local truth slots.

Public evidence updates a hypothesis set of six changes: unchanged,
global inversion, or one independently modified receptive slot.
This is a predefined, falsifiable mutation prior, NOT discovered structure.
Predictions require unanimity across surviving hypotheses.
"""
from unrestricted_operation_cells import INPUTS
from retained_cell_transfer import RetainedCellTransfer

MUTATIONS=(0,15,1,2,4,8)

class RiskAwareLocalProbe:
    def __init__(self,source_mask):
        if type(source_mask) is not int or not 0<=source_mask<16:
            raise ValueError("PUBLIC_SOURCE_MASK_INVALID")
        self.source_mask=source_mask
        self.possible={source_mask^mutation for mutation in MUTATIONS}
        self.observed={}
        self.target_observations=0

    def predict(self,key):
        if key not in INPUTS:raise ValueError("PUBLIC_INPUT_INVALID")
        index=INPUTS.index(key)
        values={bool(mask>>index&1) for mask in self.possible}
        return next(iter(values)) if len(values)==1 else None

    def observe(self,key,outcome):
        if key not in INPUTS or type(outcome) is not bool:
            raise ValueError("PUBLIC_FEEDBACK_INVALID")
        if key in self.observed:raise ValueError("DUPLICATE_PUBLIC_PROBE")
        self.observed[key]=outcome
        index=INPUTS.index(key)
        self.possible={mask for mask in self.possible if bool(mask>>index&1)==outcome}
        self.target_observations+=1

    def select_probe(self):
        if not self.possible:return None
        proposals=[]
        for index,key in enumerate(INPUTS):
            if key in self.observed:continue
            positives=sum(bool(mask>>index&1) for mask in self.possible)
            negatives=len(self.possible)-positives
            # All uncertainty-driven probes are selected only using
            # pre-observation public information; ties are deterministic.
            proposals.append((min(positives,negatives),-index,key))
        return max(proposals)[2] if proposals else None

    def state(self):
        return (tuple(sorted(self.possible)),self.target_observations)
