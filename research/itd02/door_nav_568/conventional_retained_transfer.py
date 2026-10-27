"""Conventional full-table transfer control, independent of local slot logic."""
from unrestricted_operation_cells import INPUTS

class ConventionalRetainedTransfer:
    def __init__(self):
        self.table={}
        self.modes={False,True}
        self.new_observations=0

    def train_source(self,inputs,outcome):
        if inputs not in INPUTS or type(outcome) is not bool or self.new_observations:
            raise ValueError("INVALID_SOURCE_EXAMPLE")
        counts=self.table.setdefault(inputs,[0,0])
        counts[int(outcome)]+=1

    def prior(self,inputs):
        counts=self.table.get(inputs,[0,0])
        if sum(counts)<2 or counts[0]==counts[1]:return None
        return counts[1]>counts[0]

    def observe_new(self,inputs,outcome):
        if type(outcome) is not bool:raise ValueError("INVALID_TARGET_OUTCOME")
        original=self.prior(inputs)
        if original is None:raise ValueError("SOURCE_EVIDENCE_INSUFFICIENT")
        self.modes.intersection_update((outcome^original,))
        self.new_observations+=1

    def predict(self,inputs):
        original=self.prior(inputs)
        if original is None or self.new_observations==0 or len(self.modes)!=1:
            return None
        return original^next(iter(self.modes))

class ScratchConventional:
    def __init__(self):
        self.counts={}
        self.new_observations=0

    def observe_new(self,inputs,outcome):
        if inputs not in INPUTS or type(outcome) is not bool:
            raise ValueError("INVALID_NEW_EVIDENCE")
        counts=self.counts.setdefault(inputs,[0,0])
        counts[int(outcome)]+=1
        self.new_observations+=1

    def predict(self,inputs):
        counts=self.counts.get(inputs,[0,0])
        if sum(counts)<2 or counts[0]==counts[1]:return None
        return counts[1]>counts[0]
