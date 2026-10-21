"""NCI-04G6: development-only local credit from a surviving cell's OWN transition.

Only the surviving sender's existing role logits are updated. Neither the
damaged target nor shared genome receives labels or updates. This cannot
qualify as source-authenticated external sensing: own_next_bit is caller
provided, and the adapter refuses to claim independent sensor attestation.
"""
import json
import math
import time
from .developmental import N, K, D, sig, softmax
from .nci04g5_local_residual import LocalResidualAdapter, local_features

class NativeSurvivorCredit:
    __slots__=("adapter",)
    def __init__(self,runtime):
        self.adapter=LocalResidualAdapter(runtime)

    def observe_own_transition(self,recipient,from_cell,prior,own_next_bit,sequence,rate=.035):
        if type(rate) not in (int,float) or not math.isfinite(rate) or not 0<rate<=.1:
            raise ValueError("invalid bounded local credit rate")
        runtime=self.adapter.runtime
        before=runtime.snapshot()
        # Emit and validate from the exact same runtime snapshot. No target
        # output or sender-independent feature vector may be supplied here.
        message=self.adapter.emit(recipient,from_cell,prior,own_next_bit,sequence)
        verified=self.adapter.verify(message,before)
        if verified["sender"]!=from_cell or verified["recipient"]!=recipient or verified["own_next_bit"]!=own_next_bit:
            raise ValueError("local custody mismatch")
        features=local_features(prior)
        experts=[sig(sum(w*v for w,v in zip(row,features)))
                 for row in runtime.core.genome]
        role=list(runtime.core.roles[from_cell])
        gate=softmax(role)
        predicted=sum(p*v for p,v in zip(gate,experts))
        delta=own_next_bit-predicted
        next_role=[max(-20.,min(20.,role[k]+rate*gate[k]*(experts[k]-predicted)*delta))
                   for k in range(K)]
        if any(not math.isfinite(v) for v in next_role):
            raise ValueError("nonfinite local credit")
        runtime.core.roles[from_cell]=next_role
        runtime.core.events+=1
        return message

    def predict_survivor(self,from_cell,local_prior):
        if type(from_cell)!=int or not 0<=from_cell<N:
            raise ValueError("invalid intact source index")
        runtime=self.adapter.runtime
        if from_cell in runtime.damaged:
            raise ValueError("damaged source cannot predict as survivor")
        features=local_features(local_prior)
        experts=[sig(sum(w*v for w,v in zip(row,features))) for row in runtime.core.genome]
        gate=softmax(runtime.core.roles[from_cell])
        return sum(p*v for p,v in zip(gate,experts))

    def resource_ledger(self,wire_count=0):
        runtime=self.adapter.runtime
        if type(wire_count)!=int or wire_count<0 or wire_count>65535:
            raise ValueError("invalid wire count")
        # No learned fields are added; report total existing native custody,
        # not an isolated new object declared to be 'free'.
        return {"native_state_serialized_bytes":len(runtime.snapshot().encode()),
                "existing_genome_coefficients":K*D,
                "existing_cell_role_coefficients":N*K,
                "new_learned_coefficients":0,
                "fixed_wire_bytes_per_message":38,
                "total_wire_bytes":38*wire_count,
                "source_attestation":"UNVERIFIED_CALLER_OWN_NEXT_BIT",
                "scientific_first_use":False}
