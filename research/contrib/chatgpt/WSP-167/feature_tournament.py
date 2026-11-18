"""WSP-167: bounded, source-free public action-effect feature tournament.

This chooses *one* additional feature from seven PREAUTHORED polynomial
candidates using only 36 public FIT intervention pairs and 12 separate
WITHIN-FIT selection pairs. It NEVER reads protected original source,
generating coefficients, future held outcomes, source regime or oracle mode.

This is conventional model selection + exact-rational recursive ridge, not
autonomous mathematical feature invention or demonstrated native GI.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import hmac
import json
import math

from public_boundary import PublicTransition
from direct_weights import ProgrammedPublicDynamics
from paired_action_weights import (
    public_effect_features, _pair_features, _ratio, _parse_ratio
)

SCHEMA = "yggdrasil.wsp167.public-effect-one-feature-tournament.v1"
MAGIC = b"YFT1"
CANDIDATES = ("s0*s2","s1*s3","s2*s3",
              "s0*s1*s2","s0*s1*s3","s0*s2*s3","s1*s2*s3")
RIDGE = Fraction(1,64)
MAX_PAIRS = 64
MAX_WIRE = 32768
N_SELECT_FIT = 36
N_SELECT_VALID = 12
MIN_SELECT_RMSE_GAIN = .003


def features(state, extra=None):
    base = public_effect_features(state)
    if extra is None:
        return base
    if type(extra) is not str or extra not in CANDIDATES:
        raise ValueError("WSP167_UNKNOWN_CANDIDATE")
    s0,s1,s2,s3 = base[1:5]
    optional = {
        "s0*s2":s0*s2,
        "s1*s3":s1*s3,
        "s2*s3":s2*s3,
        "s0*s1*s2":s0*s1*s2,
        "s0*s1*s3":s0*s1*s3,
        "s0*s2*s3":s0*s2*s3,
        "s1*s2*s3":s1*s2*s3,
    }
    return base+(optional[extra],)


def _dot(a,b):
    return sum((x*y for x,y in zip(a,b)),Fraction(0))


def _validate(candidate,weights,inverse,seen):
    if candidate is not None and (type(candidate) is not str or candidate not in CANDIDATES):
        raise ValueError("WSP167_CANDIDATE")
    if type(seen) is not int or not 0 <= seen <= MAX_PAIRS:
        raise ValueError("WSP167_COUNT")
    width = 8 + int(candidate is not None)
    if (type(weights) not in (tuple,list) or len(weights)!=4 or
        type(inverse) not in (tuple,list) or len(inverse)!=width):
        raise ValueError("WSP167_SHAPE")
    for matrix,cols in ((weights,width),(inverse,width)):
        if any(type(row) not in (tuple,list) or len(row)!=cols or
               any(type(v) is not Fraction for v in row) for row in matrix):
            raise ValueError("WSP167_RATIONAL_SHAPE")
    for i in range(width):
        if inverse[i][i] <= 0:
            raise ValueError("WSP167_NONPOSITIVE_INVERSE")
        for j in range(i):
            if inverse[i][j]!=inverse[j][i]:
                raise ValueError("WSP167_NONSYMMETRIC_INVERSE")


class SelectedPublicEffect:
    """One shared, immutable exact-rational 4x(8 or 9) direct-weight program."""

    __slots__=("_candidate","_weights","_inverse","_seen")

    def __init__(self,candidate=None):
        if candidate is not None and (type(candidate) is not str or candidate not in CANDIDATES):
            raise ValueError("WSP167_CANDIDATE")
        width=8+int(candidate is not None)
        self._candidate=candidate
        self._weights=tuple(tuple(Fraction(0) for _ in range(width))
                            for _ in range(4))
        self._inverse=tuple(tuple(Fraction(1,RIDGE) if i==j else Fraction(0)
                                for j in range(width)) for i in range(width))
        self._seen=0

    @classmethod
    def _new(cls,candidate,weights,inverse,seen):
        _validate(candidate,weights,inverse,seen)
        obj=object.__new__(cls)
        obj._candidate=candidate
        obj._weights=tuple(tuple(row) for row in weights)
        obj._inverse=tuple(tuple(row) for row in inverse)
        obj._seen=seen
        return obj

    @property
    def candidate(self):
        return self._candidate

    @property
    def seen(self):
        return self._seen

    def observe_pair(self,zero,one):
        if self._seen>=MAX_PAIRS:
            raise ValueError("WSP167_PAIR_LIMIT")
        original,y=_pair_features(zero,one)
        x=features(zero.observation,self._candidate)
        if x[:8]!=original:
            raise ValueError("WSP167_FEATURE_MISMATCH")
        width=len(x)
        q=tuple(_dot(self._inverse[i],x) for i in range(width))
        denominator=Fraction(1)+_dot(x,q)
        if denominator <= 0:
            raise ValueError("WSP167_UPDATE_DENOM")
        gain=tuple(v/denominator for v in q)
        residual=tuple(y[k]-_dot(self._weights[k],x) for k in range(4))
        weights=tuple(tuple(self._weights[k][j]+residual[k]*gain[j]
                            for j in range(width)) for k in range(4))
        inverse=tuple(tuple(self._inverse[i][j]-q[i]*q[j]/denominator
                            for j in range(width)) for i in range(width))
        return self._new(self._candidate,weights,inverse,self._seen+1)

    def effect(self,state):
        x=features(state,self._candidate)
        return tuple(float(_dot(row,x)) for row in self._weights)

    def predict(self,parent,state,action):
        if type(parent) is not ProgrammedPublicDynamics:
            raise ValueError("WSP167_PARENT_REQUIRED")
        if type(action) is not int or action not in (0,1):
            raise ValueError("WSP167_ACTION_INVALID")
        zero=parent.predict(state,0)
        if action==0:
            return zero
        d=self.effect(state)
        val=tuple(zero[k]+d[k] for k in range(4))
        if not all(math.isfinite(v) for v in val):
            raise ValueError("WSP167_PREDICT_NONFINITE")
        return val

    def checkpoint(self):
        obj={
            "schema":SCHEMA,
            "candidate":self._candidate,
            "seen":self._seen,
            "weights":[[_ratio(x) for x in row] for row in self._weights],
            "inverse":[[_ratio(x) for x in row] for row in self._inverse],
        }
        blob=json.dumps(obj,sort_keys=True,separators=(",",":"),
                        ensure_ascii=True,allow_nan=False).encode("ascii")
        raw=MAGIC+len(blob).to_bytes(4,"big")+blob
        raw+=hashlib.sha256(raw).digest()
        if len(raw)>MAX_WIRE:
            raise ValueError("WSP167_CHECKPOINT_TOO_BIG")
        return raw

    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not 40 < len(raw) <= MAX_WIRE:
            raise ValueError("WSP167_CHECKPOINT_SIZE")
        if (raw[:4]!=MAGIC or
            int.from_bytes(raw[4:8],"big") != len(raw)-40 or
            not hmac.compare_digest(hashlib.sha256(raw[:-32]).digest(),raw[-32:])):
            raise ValueError("WSP167_CHECKPOINT_DIGEST")
        def no_dupes(pairs):
            out={}
            for k,v in pairs:
                if k in out:
                    raise ValueError("WSP167_DUPLICATE_FIELD")
                out[k]=v
            return out
        try:
            obj=json.loads(raw[8:-32].decode("ascii"),object_pairs_hook=no_dupes)
            if type(obj) is not dict or set(obj)!={
                    "schema","candidate","seen","weights","inverse"} or obj["schema"]!=SCHEMA:
                raise ValueError("WSP167_CHECKPOINT_SCHEMA")
            model=cls._new(
                obj["candidate"],
                tuple(tuple(_parse_ratio(v) for v in row)
                      for row in obj["weights"]),
                tuple(tuple(_parse_ratio(v) for v in row)
                      for row in obj["inverse"]),obj["seen"])
        except (ValueError,KeyError,TypeError,UnicodeError,OverflowError) as exc:
            raise ValueError("WSP167_CHECKPOINT_FIELDS") from exc
        if model.checkpoint()!=raw:
            raise ValueError("WSP167_CHECKPOINT_NONCANONICAL")
        return model


def fit(pairs,candidate):
    if type(pairs) not in (tuple,list) or not 1 <= len(pairs) <= MAX_PAIRS:
        raise ValueError("WSP167_FIT_PAIR_COUNT")
    model=SelectedPublicEffect(candidate)
    for pair in pairs:
        if type(pair) not in (tuple,list) or len(pair)!=2:
            raise ValueError("WSP167_PUBLIC_PAIR_SHAPE")
        model=model.observe_pair(pair[0],pair[1])
    return model


def paired_effect_rmse(model,pairs):
    if type(model) is not SelectedPublicEffect or not pairs:
        raise ValueError("WSP167_SCORING_INPUT")
    error=[]
    for zero,one in pairs:
        _pair_features(zero,one)
        forecast=model.effect(zero.observation)
        error.extend((forecast[k]-
                      (one.next_observation[k]-zero.next_observation[k]))**2
                     for k in range(4))
    return math.sqrt(math.fsum(error)/len(error))


def select_feature(training36,selection12):
    """Source-free, frozen 36/12 INNER-FIT model selection; held never read."""
    if (type(training36) not in (tuple,list) or len(training36)!=N_SELECT_FIT or
        type(selection12) not in (tuple,list) or len(selection12)!=N_SELECT_VALID):
        raise ValueError("WSP167_INNER_SPLIT")
    keys=[]
    for pair in (*training36,*selection12):
        if type(pair) not in (tuple,list) or len(pair)!=2:
            raise ValueError("WSP167_PUBLIC_PAIR_SHAPE")
        _pair_features(pair[0],pair[1])
        keys.append(pair[0].observation)
    if len(set(keys))!=48:
        raise ValueError("WSP167_DUPLICATE_PUBLIC_FIT")
    baseline=paired_effect_rmse(fit(training36,None),selection12)
    scores={}
    for candidate in CANDIDATES:
        score=paired_effect_rmse(fit(training36,candidate),selection12)
        scores[candidate]=score
    # Fixed grammar order breaks ties, independent of source/held outcome.
    best=min(CANDIDATES,key=lambda k:(scores[k],CANDIDATES.index(k)))
    selected=best if baseline-scores[best]>=MIN_SELECT_RMSE_GAIN else None
    return selected,{
        "null_inner_rmse":baseline,
        "selected_inner_rmse":scores[best],
        "inner_rmse_gain":baseline-scores[best],
        "all_candidate_inner_rmse":scores,
    }


def fit_selected(train48):
    if type(train48) not in (tuple,list) or len(train48)!=48:
        raise ValueError("WSP167_FIT_48_REQUIRED")
    selected,diagnostics=select_feature(train48[:36],train48[36:])
    return fit(train48,selected),diagnostics
