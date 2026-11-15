"""FKP-08 bounded direct-numeric shared-base and cumulative learned causal patches.

Only true observed consequences are used. No source secret or hidden motif ID
enters fitting. The conventional same-information delta format is an exact
semantic/control tie by design, not a competitor to quietly exclude.
"""
from __future__ import annotations
import hashlib
import itertools
import struct
import zlib
from source import CONTEXTS,STATES,MOTIF_MASKS

CANDIDATES=tuple(itertools.combinations(range(len(MOTIF_MASKS)),2))
CANDIDATE_DIFF=tuple(MOTIF_MASKS[a]^MOTIF_MASKS[b] for a,b in CANDIDATES)
assert len(CANDIDATES)==6216
MASK256=(1<<STATES)-1

class Memory:
    """32 source contexts x 32-byte base, plus 3 x 2-byte motif IDs each."""
    __slots__=("bases","patches")
    MAGIC=b"FKP8"
    def __init__(self):
        self.bases={}
        self.patches={}
    def set_base(self,context:int,history:tuple[tuple[int,int],...]):
        if context not in CONTEXTS or len(history)!=256 or set(x for x,y in history)!=set(range(256)):
            raise ValueError("FKP08_BASE_SOURCE_HISTORY_INVALID")
        if any(y not in (0,1) or type(y) is not int for x,y in history):
            raise ValueError("FKP08_BAD_BASE_OBSERVATION")
        if context in self.bases:raise ValueError("FKP08_BASE_ALREADY_LEARNED")
        self.bases[context]=sum(y<<x for x,y in history)
    def rule(self,context:int,revision:int)->int:
        if context not in self.bases:raise ValueError("FKP08_UNKNOWN_CONTEXT")
        if type(revision) is not int or not 0<=revision<=3:
            raise ValueError("FKP08_BAD_REVISION")
        result=self.bases[context]
        for version in range(1,revision+1):
            pair=self.patches.get((context,version))
            if pair is None:raise ValueError("FKP08_VERSION_NOT_LEARNED")
            a,b=pair
            result^=MOTIF_MASKS[a]^MOTIF_MASKS[b]
        return result
    def fit(self,context:int,revision:int,history:tuple[tuple[int,int],...]):
        if type(revision) is not int or not 1<=revision<=3:
            raise ValueError("FKP08_FIT_VERSION_INVALID")
        if (context,revision) in self.patches or len(history)!=16 or len(set(x for x,y in history))!=16:
            raise ValueError("FKP08_FIT_HISTORY_INVALID")
        if any(type(x) is not int or not 0<=x<256 or type(y) is not int or y not in (0,1) for x,y in history):
            raise ValueError("FKP08_FIT_ACTION_OR_OUTCOME_INVALID")
        old=self.rule(context,revision-1)
        input_mask=sum(1<<x for x,y in history)
        changes=sum(((old>>x)&1 ^y)<<x for x,y in history)
        # Smallest error on actual paid consequences; ties are frozen lexical.
        best_misses=17
        tied=[]
        for (a,b),patch in zip(CANDIDATES,CANDIDATE_DIFF):
            misses=((patch^changes)&input_mask).bit_count()
            if misses<best_misses:
                best_misses=misses;tied=[(a,b)]
            elif misses==best_misses:tied.append((a,b))
        # Never silently claim exact identification if source evidence is
        # incompatible with prior stored rule. The repair remains observable.
        chosen=tied[0]
        self.patches[(context,revision)]=chosen
        return {"best_mismatches":best_misses,"consistent_hypotheses":len(tied),
                "pair":chosen,"source_actions":len(history)}
    def predict(self,context:int,revision:int,states:tuple[int,...])->tuple[int,...]:
        value=self.rule(context,revision)
        return tuple((value>>x)&1 for x in states)
    def raw_weights(self)->bytes:
        if len(self.bases)!=len(CONTEXTS) or len(self.patches)!=len(CONTEXTS)*3:
            raise ValueError("FKP08_CHECKPOINT_INCOMPLETE")
        raw=b"".join(self.bases[c].to_bytes(32,"big") for c in CONTEXTS)
        raw+=b"".join(bytes(self.patches[(c,v)]) for c in CONTEXTS for v in (1,2,3))
        assert len(raw)==1216
        return raw
    def snapshot(self)->bytes:
        data=self.raw_weights()
        body=self.MAGIC+data
        return body+hashlib.sha256(body).digest()
    @classmethod
    def restore(cls,data:bytes):
        if type(data) is not bytes or len(data)!=1252 or data[:4]!=cls.MAGIC or hashlib.sha256(data[:-32]).digest()!=data[-32:]:
            raise ValueError("FKP08_CHECKPOINT_REJECTED")
        out=cls()
        data=data[4:-32]
        for i,c in enumerate(CONTEXTS):out.bases[c]=int.from_bytes(data[i*32:(i+1)*32],"big")
        offset=1024
        for i,c in enumerate(CONTEXTS):
            for j,v in enumerate((1,2,3)):
                a,b=data[offset+6*i+2*j:offset+6*i+2*j+2]
                if not (a<b<len(MOTIF_MASKS)):
                    raise ValueError("FKP08_PATCH_ID_INVALID")
                out.patches[(c,v)]=(a,b)
        return out

def standard_baseline_sizes(memory:Memory)->dict:
    # These are SAME learned source observations/predictions, NOT oracle laws.
    all_snapshots=b"".join(memory.rule(c,v).to_bytes(32,"big")
                          for c in CONTEXTS for v in range(4))
    delta=memory.raw_weights()
    return {"bitsets_raw":len(all_snapshots),
            "bitsets_zlib9":len(zlib.compress(all_snapshots,9)),
            "learned_delta_raw":len(delta),
            "learned_delta_zlib9":len(zlib.compress(delta,9)),
            "conventional_exact_delta_ties_candidate":True}
