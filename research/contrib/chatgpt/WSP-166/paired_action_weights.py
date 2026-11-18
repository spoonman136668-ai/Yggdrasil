"""WSP166: exactly reproducible direct programming of matched public action effects.

Source-free development only. The effect feature grammar is explicitly authored
in advance; this is classical ridge RLS in exact-rational arithmetic, NOT a
novel causality algorithm or general-intelligence discovery. Every update is
formed solely from two separately observed public action consequences at the
same fabricated state. Original external CausalGym reset/step/do count = 0.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import hmac
import json
import math
import re

from public_boundary import PublicTransition
from direct_weights import ProgrammedPublicDynamics, _state

WIDTH = 8
OUTPUTS = 4
MAX_PAIRS = 64
MAX_WIRE = 65536
MAGIC = b"YPE1"
SCHEMA = "yggdrasil.wsp166.paired-action-exact-rational-v1"


def _f(x):
    # Preserve dyadic public floating observations exactly; no libm.
    return Fraction.from_float(float(x))


def public_effect_features(observation):
    x = _state(observation,"OBS")
    s = tuple(_f(v) for v in x)
    return (Fraction(1), s[0], s[1], s[2], s[3],
            s[0]*s[1], s[1]*s[2], s[0]*s[3])


def _dot(a,b):
    return sum((x*y for x,y in zip(a,b)),Fraction(0))


def _validate(weights, inverse, seen):
    if type(seen) is not int or not 0<=seen<=MAX_PAIRS:
        raise ValueError("WSP166_PAIR_COUNT")
    if (type(weights) not in (tuple,list) or len(weights)!=OUTPUTS or
            type(inverse) not in (tuple,list) or len(inverse)!=WIDTH):
        raise ValueError("WSP166_MODEL_SHAPE")
    for matrix,cols in ((weights,WIDTH),(inverse,WIDTH)):
        for row in matrix:
            if type(row) not in (tuple,list) or len(row)!=cols or any(
                    type(v) is not Fraction for v in row):
                raise ValueError("WSP166_STATE_RATIONAL_SHAPE")
    for i in range(WIDTH):
        if inverse[i][i]<=0:
            raise ValueError("WSP166_NONPOSITIVE_COVARIANCE")
        for j in range(i):
            if inverse[i][j]!=inverse[j][i]:
                raise ValueError("WSP166_NONSYMMETRIC_COVARIANCE")


def _pair_features(action_zero,action_one):
    if type(action_zero) is not PublicTransition or type(action_one) is not PublicTransition:
        raise ValueError("WSP166_PUBLIC_PAIR_REQUIRED")
    if action_zero.action!=0 or action_one.action!=1:
        raise ValueError("WSP166_PAIR_ACTION_ORDER")
    if action_zero.observation!=action_one.observation:
        raise ValueError("WSP166_UNMATCHED_PUBLIC_STATE")
    if ((action_zero.reward,action_zero.terminated,action_zero.truncated) !=
        (action_one.reward,action_one.terminated,action_one.truncated)):
        raise ValueError("WSP166_PAIR_FLAGS_MISMATCH")
    x=public_effect_features(action_zero.observation)
    y=tuple(_f(action_one.next_observation[k])-
            _f(action_zero.next_observation[k]) for k in range(OUTPUTS))
    return x,y


def _ratio(value):
    return str(value.numerator)+"/"+str(value.denominator)


def _parse_ratio(value):
    if (type(value) is not str or len(value)>512 or not re.fullmatch(
            r"-?(?:0|[1-9][0-9]*)/[1-9][0-9]*",value)):
        raise ValueError("WSP166_NONCANONICAL_RATIONAL")
    left,right=value.split("/")
    parsed=Fraction(int(left),int(right))
    if _ratio(parsed)!=value:
        raise ValueError("WSP166_NONCANONICAL_RATIONAL")
    return parsed


class ExactPairedActionEffect:
    """One bounded 4x8 exact-rational causal contrast program.

    The immutable parent 4D static model is passed only at prediction time;
    it is NOT edited or serialized with the new effect weights. For action0
    forecast the exact parent action0 value. For action1 forecast parent
    action0 plus directly programmed paired public effect.
    """
    __slots__=("_weights","_inverse","_seen")

    def __init__(self):
        self._weights=tuple(tuple(Fraction(0) for _ in range(WIDTH))
                            for _ in range(OUTPUTS))
        self._inverse=tuple(tuple(Fraction(int(i==j)) for j in range(WIDTH))
                            for i in range(WIDTH))
        self._seen=0

    @classmethod
    def _new(cls,weights,inverse,seen):
        _validate(weights,inverse,seen)
        obj=object.__new__(cls)
        obj._weights=tuple(tuple(row) for row in weights)
        obj._inverse=tuple(tuple(row) for row in inverse)
        obj._seen=seen
        return obj

    @property
    def seen(self):
        return self._seen

    def effect(self,observation):
        x=public_effect_features(observation)
        return tuple(float(_dot(row,x)) for row in self._weights)

    def predict(self,parent,observation,action):
        if type(parent) is not ProgrammedPublicDynamics:
            raise ValueError("WSP166_PARENT_TYPE")
        if type(action) is not int or action not in (0,1):
            raise ValueError("WSP166_PREDICT_ACTION")
        base=parent.predict(observation,0)
        if action==0:
            return base
        effect=self.effect(observation)
        pred=tuple(base[k]+effect[k] for k in range(OUTPUTS))
        if not all(math.isfinite(v) for v in pred):
            raise ValueError("WSP166_PREDICT_NONFINITE")
        return pred

    def observe_pair(self,action_zero,action_one):
        if self._seen>=MAX_PAIRS:
            raise ValueError("WSP166_PAIR_LIMIT")
        x,y=_pair_features(action_zero,action_one)
        q=tuple(_dot(row,x) for row in self._inverse)
        denominator=Fraction(1)+_dot(x,q)
        if denominator<=0:
            raise ValueError("WSP166_RLS_NONPOSITIVE")
        gain=tuple(t/denominator for t in q)
        residual=tuple(y[k]-_dot(self._weights[k],x)
                       for k in range(OUTPUTS))
        weights=tuple(tuple(self._weights[k][j]+residual[k]*gain[j]
                            for j in range(WIDTH)) for k in range(OUTPUTS))
        inverse=tuple(tuple(self._inverse[i][j]-q[i]*q[j]/denominator
                            for j in range(WIDTH)) for i in range(WIDTH))
        return self._new(weights,inverse,self._seen+1)

    def checkpoint(self):
        data={
            "schema":SCHEMA,
            "pairs":self._seen,
            "w":[[_ratio(v) for v in row] for row in self._weights],
            "inv":[[_ratio(v) for v in row] for row in self._inverse],
        }
        payload=json.dumps(data,sort_keys=True,separators=(",",":"),
                           ensure_ascii=True,allow_nan=False).encode("ascii")
        wire=MAGIC+len(payload).to_bytes(4,"big")+payload
        wire+=hashlib.sha256(wire).digest()
        if len(wire)>MAX_WIRE:
            raise ValueError("WSP166_CHECKPOINT_TOO_LARGE")
        return wire

    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not 40<len(raw)<=MAX_WIRE:
            raise ValueError("WSP166_CHECKPOINT_SIZE")
        if (raw[:4]!=MAGIC or
            int.from_bytes(raw[4:8],"big")!=len(raw)-40 or
            not hmac.compare_digest(hashlib.sha256(raw[:-32]).digest(),raw[-32:])):
            raise ValueError("WSP166_CHECKPOINT_INTEGRITY")
        def unique_pairs(entries):
            out={}
            for k,v in entries:
                if k in out:
                    raise ValueError("WSP166_DUPLICATE_FIELD")
                out[k]=v
            return out
        try:
            data=json.loads(raw[8:-32].decode("ascii"),object_pairs_hook=unique_pairs)
            if type(data) is not dict or set(data)!={"schema","pairs","w","inv"} or data["schema"]!=SCHEMA:
                raise ValueError("WSP166_CHECKPOINT_SCHEMA")
            weights=tuple(tuple(_parse_ratio(v) for v in row)
                          for row in data["w"])
            inverse=tuple(tuple(_parse_ratio(v) for v in row)
                          for row in data["inv"])
            program=cls._new(weights,inverse,data["pairs"])
        except (KeyError,TypeError,ValueError,UnicodeError,OverflowError) as exc:
            raise ValueError("WSP166_CHECKPOINT_FIELDS") from exc
        if program.checkpoint()!=raw:
            raise ValueError("WSP166_CHECKPOINT_NONCANONICAL")
        return program
