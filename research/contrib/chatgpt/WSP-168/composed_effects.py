"""WSP-168: source-free compositional action-effect weights + public-law retrieval.

The only new structural operator is multiplication of the PREVIOUSLY
selected third-order public term by each public state coordinate.
Candidate identity is selected on a public 36/12 inner FIT split, NOT
from author source coefficients or held targets. A single opt-in readout
retains both the frozen old law and newly trained effect and chooses which
applies from the last *already observed* action1 public consequence.

All original source first-use calls = 0. No external simulation imports,
token model, hidden regime, original private source or real action execution.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import hmac
import json
import math

from direct_weights import ProgrammedPublicDynamics
from public_boundary import PublicTransition
from paired_action_weights import _pair_features, _parse_ratio, _ratio
from feature_tournament import features as prior_features

MAGIC=b"YCM1"
SCHEMA="yggdrasil.wsp168.sourcefree.composed-public-effect.v1"
RIDGE=Fraction(1,64)
WIDTH_BASE=9
MAX_PAIRS=64
MAX_CHECKPOINT=32768
MIN_GAIN=.01
INNER_FIT=36
INNER_SELECT=12


def constructed_features(state, factor):
    """Create product of prior public triple * one state dimension.

    No table of quartic candidate expressions is authored. This provides
    only a bounded multiplication grammar, not unrestricted new structure.
    """
    base=prior_features(state,"s0*s1*s2")
    if factor is None:
        return base
    if type(factor) is not int or factor not in range(4):
        raise ValueError("WSP168_FACTOR_INVALID")
    return base+(base[-1]*base[1+factor],)


def _dot(a,b):
    return sum((x*y for x,y in zip(a,b)),Fraction(0))


def _validate(factor,weights,inverse,seen):
    if factor is not None and (type(factor) is not int or factor not in range(4)):
        raise ValueError("WSP168_FACTOR_INVALID")
    if type(seen) is not int or not 0<=seen<=MAX_PAIRS:
        raise ValueError("WSP168_FIT_COUNT")
    width=WIDTH_BASE+int(factor is not None)
    if type(weights) not in (tuple,list) or len(weights)!=4 or type(inverse) not in (tuple,list) or len(inverse)!=width:
        raise ValueError("WSP168_SHAPE")
    for rows in (weights,inverse):
        if len(rows) != (4 if rows is weights else width):
            raise ValueError("WSP168_SHAPE")
        for row in rows:
            if type(row) not in (tuple,list) or len(row)!=width or any(type(x) is not Fraction for x in row):
                raise ValueError("WSP168_NONRATIONAL")
    for i in range(width):
        if inverse[i][i]<=0:
            raise ValueError("WSP168_NONPOSITIVE_COVARIANCE")
        for j in range(i):
            if inverse[i][j]!=inverse[j][i]:
                raise ValueError("WSP168_COVARIANCE_ASYMMETRY")


class ComposedPublicEffect:
    """A SINGLE source-blind direct exact-rational coefficient program."""

    __slots__=("_factor","_weights","_inverse","_seen")

    def __init__(self,factor=None):
        if factor is not None and (type(factor) is not int or factor not in range(4)):
            raise ValueError("WSP168_FACTOR_INVALID")
        width=WIDTH_BASE+int(factor is not None)
        self._factor=factor
        self._weights=tuple(tuple(Fraction(0) for _ in range(width)) for _ in range(4))
        self._inverse=tuple(tuple(Fraction(1,RIDGE) if i==j else Fraction(0)
                                  for j in range(width)) for i in range(width))
        self._seen=0

    @classmethod
    def _new(cls,factor,weights,inverse,seen):
        _validate(factor,weights,inverse,seen)
        o=object.__new__(cls)
        o._factor=factor
        o._weights=tuple(tuple(r) for r in weights)
        o._inverse=tuple(tuple(r) for r in inverse)
        o._seen=seen
        return o

    @property
    def factor(self):
        return self._factor

    @property
    def seen(self):
        return self._seen

    def observe_pair(self,zero,one):
        if self._seen>=MAX_PAIRS:
            raise ValueError("WSP168_PAIR_LIMIT")
        _,y=_pair_features(zero,one)
        x=constructed_features(zero.observation,self._factor)
        q=tuple(_dot(row,x) for row in self._inverse)
        d=Fraction(1)+_dot(x,q)
        if d<=0:
            raise ValueError("WSP168_DENOMINATOR")
        gain=tuple(v/d for v in q)
        error=tuple(y[k]-_dot(self._weights[k],x) for k in range(4))
        w=tuple(tuple(self._weights[k][j]+error[k]*gain[j]
                      for j in range(len(x))) for k in range(4))
        inv=tuple(tuple(self._inverse[i][j]-q[i]*q[j]/d
                        for j in range(len(x))) for i in range(len(x)))
        return self._new(self._factor,w,inv,self._seen+1)

    def effect(self,state):
        x=constructed_features(state,self._factor)
        return tuple(float(_dot(row,x)) for row in self._weights)

    def predict(self,parent,state,action):
        if type(parent) is not ProgrammedPublicDynamics:
            raise ValueError("WSP168_PARENT_REQUIRED")
        if type(action) is not int or action not in (0,1):
            raise ValueError("WSP168_ACTION_INVALID")
        base=parent.predict(state,0)
        if action==0:
            return base
        shift=self.effect(state)
        out=tuple(base[k]+shift[k] for k in range(4))
        if any(not math.isfinite(v) for v in out):
            raise ValueError("WSP168_PREDICTION_NONFINITE")
        return out

    def checkpoint(self):
        obj={
            "schema":SCHEMA, "factor":self._factor, "seen":self._seen,
            "w":[[_ratio(v) for v in row] for row in self._weights],
            "inv":[[_ratio(v) for v in row] for row in self._inverse]
        }
        payload=json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode("ascii")
        wire=MAGIC+len(payload).to_bytes(4,"big")+payload
        wire+=hashlib.sha256(wire).digest()
        if len(wire)>MAX_CHECKPOINT:
            raise ValueError("WSP168_CHECKPOINT_TOO_LARGE")
        return wire

    @classmethod
    def restore(cls,wire):
        if type(wire) is not bytes or not 40<len(wire)<=MAX_CHECKPOINT:
            raise ValueError("WSP168_CHECKPOINT_SIZE")
        if (wire[:4]!=MAGIC or int.from_bytes(wire[4:8],"big")!=len(wire)-40 or
            not hmac.compare_digest(hashlib.sha256(wire[:-32]).digest(),wire[-32:])):
            raise ValueError("WSP168_CHECKPOINT_DIGEST")
        def unique(items):
            out={}
            for k,v in items:
                if k in out:
                    raise ValueError("WSP168_DUPLICATE_JSON_FIELD")
                out[k]=v
            return out
        try:
            d=json.loads(wire[8:-32].decode("ascii"),object_pairs_hook=unique)
            if type(d) is not dict or set(d)!={"schema","factor","seen","w","inv"} or d["schema"]!=SCHEMA:
                raise ValueError("WSP168_CHECKPOINT_SCHEMA")
            model=cls._new(
                d["factor"],
                tuple(tuple(_parse_ratio(x) for x in row) for row in d["w"]),
                tuple(tuple(_parse_ratio(x) for x in row) for row in d["inv"]),
                d["seen"]
            )
        except (KeyError,ValueError,UnicodeError,TypeError,OverflowError) as exc:
            raise ValueError("WSP168_CHECKPOINT_FIELDS") from exc
        if model.checkpoint()!=wire:
            raise ValueError("WSP168_CHECKPOINT_NONCANONICAL")
        return model


def fit_public_pairs(pairs,factor):
    if type(pairs) not in (tuple,list) or not 1<=len(pairs)<=MAX_PAIRS:
        raise ValueError("WSP168_FIT_PAIR_COUNT")
    m=ComposedPublicEffect(factor)
    for pair in pairs:
        if type(pair) not in (tuple,list) or len(pair)!=2:
            raise ValueError("WSP168_FIT_PUBLIC_PAIR")
        m=m.observe_pair(pair[0],pair[1])
    return m


def selection_rmse(model,pairs):
    if type(model) is not ComposedPublicEffect or not pairs:
        raise ValueError("WSP168_SELECTION_INPUT")
    squared=[]
    for z,o in pairs:
        _,target=_pair_features(z,o)
        prediction=model.effect(z.observation)
        squared.extend((prediction[k]-float(target[k]))**2 for k in range(4))
    return math.sqrt(math.fsum(squared)/len(squared))


def choose_composition(inner_fit,inner_select):
    """A fixed grammar operator synthesizes four candidates at runtime."""
    if (type(inner_fit) not in (list,tuple) or len(inner_fit)!=INNER_FIT or
        type(inner_select) not in (list,tuple) or len(inner_select)!=INNER_SELECT):
        raise ValueError("WSP168_INNER_SPLIT")
    identities=[]
    for pair in (*inner_fit,*inner_select):
        if type(pair) not in (tuple,list) or len(pair)!=2:
            raise ValueError("WSP168_INNER_PAIR")
        _pair_features(pair[0],pair[1])
        identities.append(pair[0].observation)
    if len(set(identities))!=48:
        raise ValueError("WSP168_FIT_DUPLICATE_STATE")
    baseline=selection_rmse(fit_public_pairs(inner_fit,None),inner_select)
    scores={i:selection_rmse(fit_public_pairs(inner_fit,i),inner_select)
            for i in range(4)}
    best=min(range(4),key=lambda i:(scores[i],i))
    selected=best if baseline-scores[best]>=MIN_GAIN else None
    return selected,{"baseline_inner_rmse":baseline,"best_inner_rmse":scores[best],
                     "best_inner_gain":baseline-scores[best],"candidate_inner_rmse":scores}


def fit_constructed(pairs):
    if type(pairs) not in (tuple,list) or len(pairs)!=48:
        raise ValueError("WSP168_TRAIN48_REQUIRED")
    selected,diag=choose_composition(pairs[:36],pairs[36:])
    return fit_public_pairs(pairs,selected),diag


class RetainedPublicLaws:
    """ONE retained model with two immutable relationship memories.

    This diagnostic uses only the newest PREVIOUS witnessed public action1
    outcome. The caller never passes a source mode, causal graph, current
    future target or a promise of hidden world identity.
    """
    __slots__=("_old","_new","_old_sha")

    def __init__(self,old_parent,new_effect):
        if type(old_parent) is not ProgrammedPublicDynamics:
            raise ValueError("WSP168_ARCHIVED_PARENT_REQUIRED")
        if type(new_effect) is not ComposedPublicEffect:
            raise ValueError("WSP168_NEW_MODEL_REQUIRED")
        old_bytes=old_parent.checkpoint()
        self._old=ProgrammedPublicDynamics.restore(old_bytes)
        self._new=ComposedPublicEffect.restore(new_effect.checkpoint())
        self._old_sha=hashlib.sha256(old_bytes).hexdigest()

    @property
    def old_checkpoint_sha256(self):
        return self._old_sha

    def new_effect_checkpoint(self):
        return self._new.checkpoint()

    def choose(self,history=()):
        if type(history) not in (tuple,list) or len(history)>1:
            raise ValueError("WSP168_PUBLIC_HISTORY_WINDOW")
        if not history:
            return "old"
        prev=history[-1]
        if type(prev) is not PublicTransition:
            raise ValueError("WSP168_HISTORY_PUBLIC_ONLY")
        if prev.terminated or prev.truncated:
            raise ValueError("WSP168_EPISODE_RESET_REQUIRED")
        if prev.action!=1:
            # action0 does not distinguish the two action1 causal laws.
            return "old"
        prior_old=self._old.predict(prev.observation,1)
        prior_new=self._new.predict(self._old,prev.observation,1)
        squared_old=math.fsum((prior_old[k]-prev.next_observation[k])**2 for k in range(4))
        squared_new=math.fsum((prior_new[k]-prev.next_observation[k])**2 for k in range(4))
        return "new" if squared_new<squared_old else "old"

    def predict(self,state,action,history=()):
        if type(action) is not int or action not in (0,1):
            raise ValueError("WSP168_ACTION_INVALID")
        archived=self._old.predict(state,action)
        head=self.choose(history)  # verify history even for action0
        if action==0 or head=="old":
            return archived
        return self._new.predict(self._old,state,action)
