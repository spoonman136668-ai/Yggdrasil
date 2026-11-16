"""FKP-22 source-independent tokenless active causal intervention selection.

Support signatures are extracted externally from physically earned consequences.
No source fixture, hidden class, world seed, reward oracle, or future labels.
Sparse partition separation (candidate) and exact Shannon information gain
(independent strong Bayesian) use identical learned PUBLIC signature counts.

This is learned *correlation and conditional experimental design* in a fixed
four-input residual space, NOT autonomous invention of unknown operators.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import math
import random

MODES=("SPARSE_PARTITION_GAIN","INDEPENDENT_BAYES_ENTROPY",
       "FIXED_0_1","DETERMINISTIC_RANDOM_TWO","NO_SUPPORT_ABLATION")
N_PROBES=4
SUPPORT_WORLDS=16
MAX_BYTES=65536


def _canonical(x):
    return json.dumps(x,sort_keys=True,allow_nan=False,
                      separators=(",",":")).encode("ascii")


def _unique(items):
    d={}
    for k,v in items:
        if k in d:
            raise ValueError("FKP22_DUPLICATE_JSON_KEY")
        d[k]=v
    return d


def _invalid_constant(_):
    raise ValueError("FKP22_NONFINITE_JSON")


def _validate_signatures(signatures):
    if type(signatures) not in (list,tuple) or len(signatures)!=SUPPORT_WORLDS:
        raise ValueError("FKP22_SUPPORT_PHYSICAL_RECEIPTS_REQUIRED")
    if any(type(s) is not int or not 0<=s<16 for s in signatures):
        raise ValueError("FKP22_SOURCE_PUBLIC_RESIDUAL_ONLY")
    return tuple(signatures)


def _binary(x):
    if type(x) is not int or x not in (0,1):
        raise ValueError("FKP22_PUBLIC_BINARY_RESIDUAL")
    return x


def _index(x):
    if type(x) is not int or not 0<=x<N_PROBES:
        raise ValueError("FKP22_INDEX_MUST_BE_UNQUERIED")
    return x


def _counts(observations):
    return dict(Counter(observations))


class ActiveResidualPolicy:
    """One public feedback update per actual selected experimental query."""

    def __init__(self,mode,support_signatures,*,public_ordinal):
        if mode not in MODES or type(mode) is not str:
            raise ValueError("FKP22_UNKNOWN_POLICY")
        if type(public_ordinal) is not int or not 0<=public_ordinal<24:
            raise ValueError("FKP22_PUBLIC_EVAL_ORDINAL")
        self.mode=mode
        self.public_ordinal=public_ordinal
        self._support=_validate_signatures(support_signatures)
        self._observed={}
        self._chosen=[]
        self._pending=None
        self._random_order=tuple(random.Random(2200+public_ordinal).sample(
            range(N_PROBES),2))
        self._guard()

    @property
    def chosen_queries(self):
        return tuple(self._chosen)

    @property
    def logical_bytes(self):
        # Fixed-width conceptual ledger, not Python heap/RSS.
        return len(self._support)*2+len(self._observed)*2+len(self._chosen)+32

    def _guard(self):
        if self.logical_bytes>MAX_BYTES:
            raise ValueError("FKP22_LEARNED_MEMORY_CAPACITY")

    def _possible_counts(self):
        if self.mode=="NO_SUPPORT_ABLATION":
            return {}
        evidence=self._observed
        return {s:n for s,n in _counts(self._support).items()
                if all(((s>>i)&1)==bit for i,bit in evidence.items())}

    @staticmethod
    def _entropy(counts):
        total=sum(counts)
        if total==0:
            return 0.0
        return -sum(n/total*math.log2(n/total) for n in counts if n)

    def _partition_query(self,eligible):
        """Native sparse contradiction partition, not enumerated law grammar."""
        possible=self._possible_counts()
        if not possible:
            return min(eligible)
        def merit(i):
            one=sum(n for signature,n in possible.items() if (signature>>i)&1)
            zero=sum(possible.values())-one
            return min(one,zero)
        return max(eligible,key=merit)

    def _bayes_query(self,eligible):
        """Independently implemented exact expected posterior entropy."""
        hypotheses=[s for s in self._support if all(
            ((s>>i)&1)==bit for i,bit in self._observed.items())]
        if not hypotheses:
            return min(eligible)
        total=len(hypotheses)
        prior=self._entropy(list(Counter(hypotheses).values()))
        def gain(i):
            expected=0.0
            for bit in (0,1):
                sub=[s for s in hypotheses if ((s>>i)&1)==bit]
                if sub:
                    expected+=(len(sub)/total)*self._entropy(
                        list(Counter(sub).values()))
            return round(prior-expected,12)
        return max(eligible,key=gain)

    def choose_query(self):
        if self._pending is not None or len(self._chosen)>=2:
            raise ValueError("FKP22_MUST_COMPLETE_SELECTED_ACTION_FIRST")
        eligible=[x for x in range(N_PROBES) if x not in self._observed]
        if self.mode=="SPARSE_PARTITION_GAIN":
            selected=self._partition_query(eligible)
        elif self.mode=="INDEPENDENT_BAYES_ENTROPY":
            selected=self._bayes_query(eligible)
        elif self.mode=="DETERMINISTIC_RANDOM_TWO":
            selected=self._random_order[len(self._chosen)]
        else:
            selected=(0,1)[len(self._chosen)]
        if selected not in eligible:
            raise AssertionError("FKP22_CHOSE_DUPLICATE_INTERVENTION")
        self._pending=selected
        return selected

    def observe_actual_query(self,position,residual_bit):
        position=_index(position)
        bit=_binary(residual_bit)
        if self._pending!=position or position in self._observed:
            raise ValueError("FKP22_OUTCOME_WITHOUT_PREVIOUSLY_CHOSEN_PHYSICAL_PROBE")
        self._chosen.append(position)
        self._observed[position]=bit
        self._pending=None
        self._guard()

    @property
    def posterior_support_count(self):
        if len(self._observed)!=2 or self._pending is not None:
            raise ValueError("FKP22_NOT_TWO_PHYSICAL_QUERIES")
        return sum(self._possible_counts().values()) if self.mode!="NO_SUPPORT_ABLATION" else None

    def predict_unqueried(self,position):
        position=_index(position)
        if len(self._observed)!=2 or self._pending is not None or position in self._observed:
            raise ValueError("FKP22_CANNOT_READ_UNQUERIED_FUTURE")
        counts=self._possible_counts()
        if not counts:
            return 0
        total=sum(counts.values())
        ones=sum(n for s,n in counts.items() if (s>>position)&1)
        # Explicit abstention is not used in this fixed binary-reward protocol.
        return 1 if ones*2>total else 0

    def _state(self):
        return {"schema":"fkp22.active-residual.v1",
                "mode":self.mode,"ordinal":self.public_ordinal,
                "support":list(self._support),
                "chosen":list(self._chosen),
                "actual_query_evidence":[[k,self._observed[k]] for k in self._chosen],
                "pending":self._pending}

    def semantic_receipt(self):
        return sha256(_canonical(self._state())).hexdigest()

    def checkpoint(self):
        b=self._state()
        raw=_canonical(b)
        if len(raw)>MAX_BYTES:
            raise ValueError("FKP22_CHECKPOINT_SIZE")
        return _canonical({"body":b,"sha256":sha256(raw).hexdigest()})

    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or len(raw)>MAX_BYTES:
            raise ValueError("FKP22_INVALID_COLD_BYTES")
        try:
            e=json.loads(raw,object_pairs_hook=_unique,parse_constant=_invalid_constant)
        except (ValueError,TypeError,UnicodeError) as err:
            raise ValueError("FKP22_CHECKPOINT_PARSE_FAILED") from err
        if type(e) is not dict or set(e)!={"body","sha256"}:
            raise ValueError("FKP22_BAD_COLD_ENVELOPE")
        b=e["body"]
        if type(b) is not dict or set(b)!={
                "schema","mode","ordinal","support","chosen",
                "actual_query_evidence","pending"}:
            raise ValueError("FKP22_COLD_SCHEMA")
        if b["schema"]!="fkp22.active-residual.v1" or sha256(_canonical(b)).hexdigest()!=e["sha256"]:
            raise ValueError("FKP22_COLD_INTEGRITY")
        obj=cls(b["mode"],b["support"],public_ordinal=b["ordinal"])
        if type(b["chosen"]) is not list or type(b["actual_query_evidence"]) is not list:
            raise ValueError("FKP22_COLD_EVENT_TYPES")
        if len(b["chosen"])>2 or len(b["chosen"])!=len(b["actual_query_evidence"]):
            raise ValueError("FKP22_COLD_EVENT_COUNT")
        for (pos,obs) in zip(b["chosen"],b["actual_query_evidence"]):
            if type(obs) is not list or len(obs)!=2 or obs[0]!=pos:
                raise ValueError("FKP22_COLD_OBSERVATION_ID")
            expected=obj.choose_query()
            if expected!=pos:
                raise ValueError("FKP22_COLD_UNPHYSICAL_CHOICE")
            obj.observe_actual_query(pos,obs[1])
        if b["pending"] is not None:
            selected=obj.choose_query()
            if selected!=b["pending"]:
                raise ValueError("FKP22_COLD_UNPHYSICAL_PENDING_QUERY")
        if obj.checkpoint()!=raw:
            raise ValueError("FKP22_NONCANONICAL_CHECKPOINT")
        return obj
