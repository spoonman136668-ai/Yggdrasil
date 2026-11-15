"""FKP-09 fixed-capacity, directly written, shared 128-bit causal synapses.

Each prior context retains a bounded compensating adapter when the shared core
itself changes after 128 independently observed *new* public consequences.
No source-private coefficients or hidden source edits are model inputs.
"""
from __future__ import annotations

import hashlib
from itertools import combinations
from source import BITS,CONTEXTS,CONTEXT_PAID,parity

PAIR_INDEXES=tuple(combinations(range(BITS),2))
assert len(PAIR_INDEXES)==8128
ALL_BITS=(1<<BITS)-1
UNUSED=255

def _base_from_paid(history:tuple[tuple[int,int],...])->int:
    if (type(history) is not tuple or len(history)!=BITS or
        set(x for x,y in history)!=set(range(BITS)) or
        any(type(x) is not int or type(y) is not int or y not in (0,1)
            for x,y in history)):
        raise ValueError("FKP09_BAD_CORE_EVIDENCE")
    return sum(y<<x for x,y in history)

def _pair_from_paid(base:int,history:tuple[tuple[int,int],...])->tuple[tuple[int,int],int,int]:
    if (type(history) is not tuple or len(history)!=CONTEXT_PAID or
        len(set(mask for mask,outcome in history))!=CONTEXT_PAID or
        any(type(mask) is not int or not 0<=mask<1<<BITS or
            type(outcome) is not int or outcome not in (0,1)
            for mask,outcome in history)):
        raise ValueError("FKP09_BAD_CONTEXT_EVIDENCE")
    xor_targets=tuple(outcome ^ parity(base&mask) for mask,outcome in history)
    consistent=[]
    for a,b in PAIR_INDEXES:
        if all((((mask>>a)&1)^((mask>>b)&1))==expected
               for (mask,_),expected in zip(history,xor_targets)):
            consistent.append((a,b))
    if not consistent:
        raise ValueError("FKP09_NO_CONSISTENT_CAUSAL_EDIT_ABSTAIN")
    return consistent[0],len(consistent),len(PAIR_INDEXES)*len(history)


class SharedCausalCore:
    MAGIC=b"FK9A"
    __slots__=("base","adapters","observed_core_steps","pair_search_count")

    def __init__(self):
        self.base=None
        self.adapters={}
        self.observed_core_steps=0
        self.pair_search_count=0

    def learn_initial_core(self,observations:tuple[tuple[int,int],...])->None:
        if self.base is not None:raise ValueError("FKP09_CORE_ALREADY_INITIALIZED")
        self.base=_base_from_paid(observations)
        self.observed_core_steps=1

    def learn_context(self,context:int,history:tuple[tuple[int,int],...])->dict:
        if context not in CONTEXTS or self.base is None:
            raise ValueError("FKP09_UNKNOWN_OR_UNINITIALIZED_CONTEXT")
        if context in self.adapters:
            raise ValueError("FKP09_CONTEXT_ALREADY_LEARNED")
        pair,n,work=_pair_from_paid(self.base,history)
        self.adapters[context]=((1<<pair[0])|(1<<pair[1]))
        self.pair_search_count+=work
        return {"pair_candidates":n,"chosen_index_pair":pair,
                "genuine_public_consequences":len(history)}

    def predict(self,context:int,actions:tuple[int,...])->tuple[int,...]:
        if context not in self.adapters or self.base is None:
            raise ValueError("FKP09_CONTEXT_NOT_LEARNED_ABSTAIN")
        if (type(actions) is not tuple or
            any(type(mask) is not int or not 0<=mask<1<<BITS for mask in actions)):
            raise ValueError("FKP09_BAD_QUERY")
        causal_weights=self.base^self.adapters[context]
        return tuple(parity(causal_weights&mask) for mask in actions)

    def rebase(self,new_core_observations:tuple[tuple[int,int],...])->dict:
        """Atomically replace actual shared synapses; compensate older contexts."""
        if self.base is None:raise ValueError("FKP09_NOT_INITIALIZED")
        next_core=_base_from_paid(new_core_observations)
        diff=self.base^next_core
        if diff==0:raise ValueError("FKP09_NO_NEW_GLOBAL_CONSEQUENCE")
        next_adapters={ctx:mask^diff for ctx,mask in self.adapters.items()}
        if any(mask.bit_count()>8 for mask in next_adapters.values()):
            raise ValueError("FKP09_SHARED_CORE_REPAIR_CAPACITY_OVERFLOW")
        # Commit ONLY after validating all old contexts. Fixed 16-byte core
        # genuinely changes and no complete duplicate context law is stored.
        self.base=next_core
        self.adapters=next_adapters
        self.observed_core_steps+=1
        return {"shared_synapse_flips":diff.bit_count(),
                "changed_context_adapters":len(next_adapters),
                "max_adapter_indices":max((x.bit_count() for x in next_adapters.values()),default=0)}

    def raw_weights(self)->bytes:
        if self.base is None:raise ValueError("FKP09_MODEL_EMPTY")
        output=bytearray(self.base.to_bytes(16,"big"))
        for context in CONTEXTS:
            indices=[x for x in range(BITS) if (self.adapters.get(context,0)>>x)&1]
            if len(indices)>8:raise ValueError("FKP09_MODEL_CAPACITY_EXCEEDED")
            output.extend(bytes(indices+[UNUSED]*(8-len(indices))))
        if len(output)!=144:raise AssertionError("FKP09_CAPACITY_DRIFT")
        return bytes(output)

    def snapshot(self)->bytes:
        body=self.MAGIC+self.raw_weights()
        return body+hashlib.sha256(body).digest()

    @classmethod
    def restore(cls,checkpoint:bytes)->"SharedCausalCore":
        if (type(checkpoint) is not bytes or len(checkpoint)!=180 or
            checkpoint[:4]!=cls.MAGIC or
            hashlib.sha256(checkpoint[:-32]).digest()!=checkpoint[-32:]):
            raise ValueError("FKP09_CHECKPOINT_INTEGRITY_INVALID")
        m=cls()
        m.base=int.from_bytes(checkpoint[4:20],"big")
        remaining=checkpoint[20:-32]
        for i,context in enumerate(CONTEXTS):
            indices=remaining[i*8:(i+1)*8]
            seen_unused=False
            actual=[]
            for x in indices:
                if x==UNUSED:
                    seen_unused=True
                elif x>=BITS or seen_unused or (actual and x<=actual[-1]):
                    raise ValueError("FKP09_NONCANONICAL_ADAPTER_CHECKPOINT")
                else:
                    actual.append(x)
            if actual:m.adapters[context]=sum(1<<x for x in actual)
        return m
