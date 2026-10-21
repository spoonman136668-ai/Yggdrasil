"""NCI-04H: local error-message-based recovery in the original fixed genome.

No lost cell role parameters or functional target labels are copied. The
damaged cell must retain its *current local sensors* and receive distinct
immediate-neighbor own-outcome residual messages produced against the same
exact source-bound native snapshot. Conflicting or uninformative neighbors
force abstention. No new learned coefficients, controller or target oracle.

This is an opt-in local update. Source snapshot checks are NOT a cryptographic
attestation of external sensor authenticity or message-body integrity.
"""
import json
import math
from .developmental import K, N, sig, softmax
from .nci04g5_local_residual import LocalResidualAdapter, local_features

class LocalCausalRepair:
    __slots__=("runtime",)
    def __init__(self,runtime):
        self.runtime=runtime

    def observe_and_recover(self,cell,local_prior,packets,source_snapshot,rate=.05):
        rt=self.runtime
        if type(cell)!=int or cell not in rt.damaged:
            raise ValueError("only a damaged native cell can relearn its role")
        if type(rate) not in (int,float) or not math.isfinite(rate) or not 0<rate<=.1:
            raise ValueError("invalid local plasticity rate")
        feat=local_features(local_prior)
        if type(source_snapshot)!=str or source_snapshot!=rt.snapshot():
            raise ValueError("source-bound local state must be exact")
        if type(packets) not in (list,tuple) or len(packets)!=2:
            raise ValueError("two intact local evidence messages required")
        adapter=LocalResidualAdapter(rt)
        expected=set(rt.neighbors[cell])
        if expected & rt.damaged:
            return {"changed":False,"abstained":True,"reason":"missing_intact_neighbor"}
        signals=[]
        observed=set()
        for wire in packets:
            evidence=adapter.verify(wire,source_snapshot)
            sender=evidence["sender"]
            if evidence["recipient"]!=cell or sender in observed:
                raise ValueError("duplicate or redirected sender evidence")
            observed.add(sender)
            signals.append(evidence["signed_residual_i8"]/127.)
        if observed!=expected:
            raise ValueError("two distinct immediate-neighbor sources required")
        # A receiver cannot infer its old function from observationally
        # inconsistent neighbors. No update, no claimed recovery.
        if any(abs(x)<.08 for x in signals) or signals[0]*signals[1]<=0:
            return {"changed":False,"abstained":True,"reason":"nonidentifiable_local_signal"}
        signal=max(-1.,min(1.,sum(signals)/2))
        experts=[sig(sum(w*x for w,x in zip(row,feat)))
                 for row in rt.core.genome]
        gate=softmax(rt.core.roles[cell])
        predicted=sum(p*w for p,w in zip(experts,gate))
        delta=[rate*signal*gate[k]*(experts[k]-predicted)
               for k in range(K)]
        if any(not math.isfinite(d) for d in delta):
            raise ValueError("nonfinite local credit")
        proposal=[max(-20.,min(20.,old+d)) for old,d in zip(rt.core.roles[cell],delta)]
        if proposal==rt.core.roles[cell]:
            return {"changed":False,"abstained":True,"reason":"zero_identifiable_plasticity"}
        # Commit only the damaged cell's K existing logits. The neighbor
        # memory, shared genome, other cells and topology remain untouched.
        rt.core.roles[cell]=proposal
        rt.steps+=1
        return {"changed":True,"abstained":False,
                "reason":"strictly_local_neighbor_residual_credit",
                "wire_bytes":len(packets[0])+len(packets[1]),
                "fixed_native_role_coefficients":N*K}
