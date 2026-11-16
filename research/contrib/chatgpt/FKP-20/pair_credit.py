"""FKP-20 sparse contradiction-gated temporal interaction and strong controls.

Strictly source-independent. All input is public action-before-outcome tuples.
There is no access to the source's hidden law or counterfactual outcomes.
The candidate's pair-feature family is predesigned; selecting a new pair from
witnessed interventions is NOT invention of an unrestricted causal operator.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]/"FKP-18"))
from temporal_trace import PublicStep, PublicTransition, SparseTemporalTrace, _valid

PAIRS=((0,1),(0,2),(1,2))
MODES=("SPARSE_CONTRADICTION_PAIRS","UNARY_ONLY","NO_CONTEXT",
       "CURRENT_DISTRACTOR_ONLY","TIME_PERMUTED_CREDIT","NO_UPDATE")
MAX_BYTES=65536
OBSERVATIONS=32


def _bytes(x):
    return json.dumps(x,sort_keys=True,allow_nan=False,
                      separators=(",",":")).encode("ascii")


def _pair_observation(rows):
    if type(rows) is not tuple or len(rows)!=4:
        raise ValueError("FKP20_PHYSICAL_FOUR_STEP_TRANSCRIPT")
    steps=tuple(_valid(row) for row in rows)
    ctx=steps[0].before[0]
    if type(ctx) is not int or ctx not in (0,1):
        raise ValueError("FKP20_CONTEXT_PUBLIC_BINARY")
    actions=[]
    for phase,step in enumerate(steps):
        if step.before[0]!=ctx or step.after[0]!=ctx or (
            step.before[1]!=phase or step.after[1]!=phase+1):
            raise ValueError("FKP20_INVALID_PUBLIC_PHASE")
        if type(step.action) is not int or step.action not in (0,1):
            raise ValueError("FKP20_BINARY_PHYSICAL_ACTION")
        history=tuple(PublicTransition(x.before,x.action,x.reward,
                                       x.after,x.done) for x in steps[:phase])
        if step.history!=history:
            raise ValueError("FKP20_NONPHYSICAL_OR_FORGED_HISTORY")
        if phase<3 and (step.reward!=0.0 or step.done):
            raise ValueError("FKP20_EARLY_FUTURE_REWARD_LEAK")
        if phase==3 and (not step.done or step.reward not in (-1.0,1.0)):
            raise ValueError("FKP20_MISSING_DELAYED_PHYSICAL_REWARD")
        actions.append(step.action)
    return ctx,tuple(actions[:3]),actions[3],int(steps[-1].reward)


def _sign(x):
    return 1-2*x


def _feature(ctx,actions,pair,*,context=True):
    return (_sign(ctx) if context else 1)*_sign(actions[pair[0]])*_sign(actions[pair[1]])


def _safe_data(rows):
    if len(rows)!=OBSERVATIONS:
        raise ValueError("FKP20_NOT_FULLY_EXPLORED")
    if any(type(r) is not tuple or len(r)!=4 or
           type(r[0]) is not int or r[0] not in (0,1) or
           type(r[1]) is not tuple or len(r[1])!=3 or
           any(type(x) is not int or x not in (0,1) for x in r[1]) or
           type(r[2]) is not int or r[2] not in (0,1) or
           r[3] not in (-1,1) for r in rows):
        raise ValueError("FKP20_UNTRUSTED_LEARNED_DATA")
    return tuple(rows)


def _choose(prediction,ctx):
    if type(ctx) is not int or ctx not in (0,1):
        raise ValueError("FKP20_UNTRUSTED_CONTEXT")
    options=[((a,b,c),prediction(ctx,(a,b,c)))
             for a in (0,1) for b in (0,1) for c in (0,1)]
    # Select first lexicographic max. No unlabeled future/source evaluation.
    return max(options,key=lambda v:v[1])[0]


class SparsePairCredit:
    """Witness actual contradictions, then allocate sparse two-parent contrasts."""

    def __init__(self,mode="SPARSE_CONTRADICTION_PAIRS"):
        if mode not in MODES:
            raise ValueError("FKP20_UNKNOWN_MODE")
        self.mode=mode
        self._data=[]
        self._trace=[]
        self._frozen=False

    @property
    def learned_logical_bytes(self):
        return len(self._data)*8+len(self._trace)*32+(
            len(self._allocated_pairs())*24)

    @property
    def observed_episodes(self):
        return len(self._data)

    def observe_episode(self,public_steps,*,learn=True):
        obs=_pair_observation(public_steps)
        if type(learn) is not bool:
            raise ValueError("FKP20_INVALID_LEARN_FLAG")
        # FKP18 temporal trace consumes ONLY already physically observed acts.
        trace=SparseTemporalTrace()
        for n,step in enumerate(public_steps):
            trace.observe_public(step,event_id=n)
        if not learn:
            return None
        if self._frozen or len(self._data)>=OBSERVATIONS:
            raise ValueError("FKP20_FROZEN_AFTER_BALANCED_EXPLORATION")
        next_data=self._data+[obs]
        next_trace=self._trace+[trace.semantic_receipt()]
        candidate_bytes=len(next_data)*8+len(next_trace)*32+(
            len(self._allocated_pairs(next_data))*24)
        if candidate_bytes>MAX_BYTES:
            raise ValueError("FKP20_CAPACITY_LIMIT")
        self._data=next_data
        self._trace=next_trace
        return trace.semantic_receipt()

    def _contradictions(self,rows):
        # Two actually witnessed source rewards conflict with a pure unary
        # hypothesis conditioned on the same public state value and action.
        seen={}
        contradictions=set()
        for ctx,actions,d,reward in rows:
            for i in range(3):
                key=(ctx,i,actions[i])
                if key in seen and seen[key]!=reward:
                    contradictions.add(i)
                else:
                    seen[key]=reward
        return contradictions

    def _allocated_pairs(self,rows=None):
        if self.mode in ("NO_UPDATE","UNARY_ONLY","CURRENT_DISTRACTOR_ONLY"):
            return ()
        data=self._data if rows is None else rows
        if not data or not self._contradictions(data):
            return ()
        # The pair family is a constrained native-style mechanism, not
        # unrestricted induction of arbitrary operators.
        return PAIRS

    def freeze(self):
        if len(self._data)!=OBSERVATIONS:
            raise ValueError("FKP20_MISSING_BALANCED_EXPLORATION")
        self._frozen=True
        return self

    def inferred_pair(self):
        if not self._frozen:
            raise ValueError("FKP20_POLICY_NOT_FROZEN")
        if not self._allocated_pairs():
            return None
        context=self.mode!="NO_CONTEXT"
        powers=[sum(reward*_feature(ctx,acts,p,context=context)
                    for ctx,acts,d,reward in self._data) for p in PAIRS]
        chosen=max(range(3),key=lambda k:abs(powers[k]))
        if powers[chosen]==0:
            return None
        return (PAIRS[chosen],1 if powers[chosen]>0 else -1)

    def choose_plan(self,ctx):
        if not self._frozen or type(ctx) is not int or ctx not in (0,1):
            raise ValueError("FKP20_UNFROZEN_OR_INVALID_CONTEXT")
        pair=self.inferred_pair()
        if pair is None:
            return (0,0,0)
        relation,coefficient=pair
        if self.mode=="TIME_PERMUTED_CREDIT":
            relation=tuple(sorted(((i+1)%3 for i in relation)))
        return _choose(lambda c,acts:coefficient*_feature(c,acts,relation),ctx)

    def state_receipt(self):
        return sha256(_bytes(self._state())).hexdigest()

    def _state(self):
        return {"schema":"fkp20.sparse-pair.v1","mode":self.mode,
                "data":[[ctx,list(acts),d,y] for ctx,acts,d,y in self._data],
                "trace_receipts":list(self._trace),"frozen":self._frozen,
                "allocated":[list(p) for p in self._allocated_pairs()]}

    def checkpoint(self):
        body=self._state()
        raw=_bytes(body)
        if len(raw)>MAX_BYTES:
            raise ValueError("FKP20_SNAPSHOT_OVER_BUDGET")
        return _bytes({"body":body,"sha256":sha256(raw).hexdigest()})

    @classmethod
    def restore(cls,blob):
        if type(blob) is not bytes or len(blob)>MAX_BYTES:
            raise ValueError("FKP20_BAD_SNAPSHOT")
        try:
            payload=json.loads(blob,object_pairs_hook=_unique_pairs,
                               parse_constant=lambda _: _invalid())
        except (ValueError,TypeError,UnicodeError) as e:
            raise ValueError("FKP20_BAD_SNAPSHOT") from e
        if type(payload) is not dict or set(payload)!={"body","sha256"}:
            raise ValueError("FKP20_BAD_ENVELOPE")
        b=payload["body"]
        if type(b) is not dict or set(b)!={"schema","mode","data","trace_receipts","frozen","allocated"}:
            raise ValueError("FKP20_BAD_SNAPSHOT_SCHEMA")
        if b["schema"]!="fkp20.sparse-pair.v1" or sha256(_bytes(b)).hexdigest()!=payload["sha256"]:
            raise ValueError("FKP20_SNAPSHOT_DIGEST")
        if type(b["data"]) is not list or type(b["trace_receipts"]) is not list or (
            type(b["frozen"]) is not bool):
            raise ValueError("FKP20_SNAPSHOT_TYPES")
        if len(b["data"])!=len(b["trace_receipts"]) or len(b["data"])>OBSERVATIONS:
            raise ValueError("FKP20_SNAPSHOT_COUNT")
        converted=[]
        for row in b["data"]:
            if type(row) is not list or len(row)!=4 or type(row[1]) is not list:
                raise ValueError("FKP20_SNAPSHOT_ROW")
            converted.append((row[0],tuple(row[1]),row[2],row[3]))
        _safe_data(converted) if len(converted)==OBSERVATIONS else _validate_partial(converted)
        if any(type(v) is not str or len(v)!=64 or any(x not in "0123456789abcdef" for x in v)
               for v in b["trace_receipts"]):
            raise ValueError("FKP20_SNAPSHOT_TRACE")
        obj=cls(b["mode"])
        obj._data=converted
        obj._trace=list(b["trace_receipts"])
        obj._frozen=b["frozen"]
        if obj._frozen and len(converted)!=OBSERVATIONS:
            raise ValueError("FKP20_INCOMPLETE_FROZEN")
        if b["allocated"]!=[list(p) for p in obj._allocated_pairs()]:
            raise ValueError("FKP20_SNAPSHOT_RELATION_DRIFT")
        if obj.learned_logical_bytes>MAX_BYTES or obj.checkpoint()!=blob:
            raise ValueError("FKP20_SNAPSHOT_NONCANONICAL")
        return obj


def _validate_partial(data):
    if any(type(row) is not tuple or len(row)!=4 or
           type(row[0]) is not int or row[0] not in (0,1) or
           type(row[1]) is not tuple or len(row[1])!=3 or
           any(type(x) is not int or x not in (0,1) for x in row[1]) or
           type(row[2]) is not int or row[2] not in (0,1) or
           type(row[3]) is not int or row[3] not in (-1,1)
           for row in data):
        raise ValueError("FKP20_SNAPSHOT_INVALID_PARTIAL")


def _unique_pairs(items):
    d={}
    for k,v in items:
        if k in d:
            raise ValueError("FKP20_DUPLICATE_JSON_KEY")
        d[k]=v
    return d


def _invalid():
    raise ValueError("FKP20_NONFINITE")


class ExactVersionSpace:
    """Independent full six-hypothesis symbolic owner-neutral control."""

    def __init__(self):
        self._possible=[(pair,sign) for pair in PAIRS for sign in (1,-1)]
        self._events=0

    def observe_episode(self,rows,*,learn=True):
        ctx,actions,d,reward=_pair_observation(rows)
        if learn:
            if self._events>=OBSERVATIONS:
                raise ValueError("FKP20_VERSION_SPACE_FROZEN")
            self._possible=[(pair,sign) for pair,sign in self._possible if
                sign*_feature(ctx,actions,pair)==reward]
            self._events+=1
            if not self._possible:
                raise ValueError("FKP20_VERSION_SPACE_SOURCE_INCONSISTENT")

    def freeze(self):
        if self._events!=OBSERVATIONS or len(self._possible)!=1:
            raise ValueError("FKP20_VERSION_SPACE_NOT_IDENTIFIED")
        return self

    @property
    def learned_logical_bytes(self):
        return len(self._possible)*16

    @property
    def inferred_pair(self):
        if self._events!=OBSERVATIONS or len(self._possible)!=1:
            raise ValueError("FKP20_VERSION_SPACE_NOT_FIT")
        return self._possible[0]

    def choose_plan(self,ctx):
        pair,sign=self.inferred_pair
        return _choose(lambda c,acts:sign*_feature(c,acts,pair),ctx)

    def state_receipt(self):
        return sha256(_bytes({"possibilities":self._possible,"observations":self._events})).hexdigest()


def _feature_vector(ctx,actions,d):
    c=_sign(ctx)
    x=[_sign(a) for a in actions]
    return (1.0,float(c),*[float(v) for v in x],float(_sign(d)),
            *[float(c*x[i]*x[j]) for i,j in PAIRS])


def _sigmoid(t):
    if t>=0:
        return 1/(1+math.exp(-t))
    z=math.exp(t)
    return z/(1+z)


class FullyFittedInteractionLogistic:
    """Strong independent fully-trained nine-feature nonlinear conventional."""

    def __init__(self):
        self._evidence=[]
        self._weights=None
        self.fit_epochs=0
        self.train_bce=None

    def observe_episode(self,rows,*,learn=True):
        ctx,acts,d,y=_pair_observation(rows)
        if learn:
            if len(self._evidence)>=OBSERVATIONS or self._weights is not None:
                raise ValueError("FKP20_LOGISTIC_FROZEN")
            self._evidence.append((_feature_vector(ctx,acts,d),y))

    def fit_after_exploration(self):
        if self._weights is not None or len(self._evidence)!=OBSERVATIONS:
            raise ValueError("FKP20_LOGISTIC_NOT_FITTABLE")
        w=[0.0]*9
        for epoch in range(1,513):
            grad=[0.0]*9
            loss=0.0
            for x,y in self._evidence:
                margin=y*sum(a*b for a,b in zip(w,x))
                loss+=(math.log1p(math.exp(-margin)) if margin>-700 else -margin)
                scalar=-y*_sigmoid(-margin)/OBSERVATIONS
                for i in range(9):
                    grad[i]+=scalar*x[i]
            loss/=OBSERVATIONS
            if loss<=0.05:
                self._weights=tuple(w)
                self.fit_epochs=epoch
                self.train_bce=loss
                return self
            w=[w[i]-grad[i] for i in range(9)]
        raise ValueError("FKP20_STRONG_CONVENTIONAL_BCE_NOT_CONVERGED")

    def freeze(self):
        if self._weights is None:
            return self.fit_after_exploration()
        return self

    def choose_plan(self,ctx):
        if self._weights is None:
            raise ValueError("FKP20_LOGISTIC_NOT_TRAINED")
        def predicted(c,acts):
            return sum(_sigmoid(sum(w*f for w,f in zip(
                self._weights,_feature_vector(c,acts,d)))) for d in (0,1))/2
        return _choose(predicted,ctx)

    @property
    def learned_logical_bytes(self):
        return 9*8

    def state_receipt(self):
        if self._weights is None:
            raise ValueError("FKP20_LOGISTIC_NOT_FIT")
        return sha256(_bytes({"w":self._weights,"epoch":self.fit_epochs,"bce":self.train_bce})).hexdigest()
