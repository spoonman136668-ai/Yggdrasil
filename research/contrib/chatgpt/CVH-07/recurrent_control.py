"""CVH-07 fully trained conventional Elman recurrent baseline and public explorer.

No source constructor/reset/do, no original first use. Conventional control
trained on PUBLIC selected actions and their actually observed consequences.
Uses standard Python only, no pretrained/donor architecture, paid API or torch.
"""
from __future__ import annotations

from collections import namedtuple
from hashlib import sha256
import json
import math
from pathlib import Path
import random
import sys

HERE=Path(__file__).resolve().parent
CVH02=HERE.parent/"CVH-02"
if str(CVH02) not in sys.path:
    sys.path.insert(0,str(CVH02))
from public_policy import _event

FIELDS=("before","action","reward","after","terminated","truncated")
PublicConsequence=namedtuple("PublicConsequence",FIELDS)
N_INPUT=6
N_HIDDEN=8
EPOCHS=48
LR=0.06
MAX_ACTIONS=32
N_TRAIN=96
WEIGHT_SEED=1707
MASK=0xffffffff
SCHEMA_RNN="yggdrasil.cvh07.conventional-trained-recurrent-public-policy.v1"
SCHEMA_EXPLORER="yggdrasil.cvh07.seeded-public-explorer.v1"


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),
                      allow_nan=False,ensure_ascii=True).encode("ascii")


def digest(x):
    return sha256(canonical(x)).hexdigest()


def training_tape(seed):
    """EXPLICITLY FABRICATED local source-free observable consequences.

    The hidden fixture bit is not exposed in public consequence records. No
    actual upstream causal environment is read or imported. A seeded PUBLIC
    behavior logger independently chooses 8 binary actions per toy episode.
    """
    if type(seed) is not int or seed not in (
            *range(101,197),*range(301,317),*range(501,517)):
        raise PermissionError("CVH07_ONLY_FROZEN_SOURCEFREE_TOY_EPISODES")
    rng=random.Random(seed*8191+31)
    hidden=seed&1
    state=(seed*7+3)&1
    rows=[]
    for step in range(8):
        action=rng.randrange(2)
        reward=int(action==hidden)
        new_state=state^action^((seed+step)&1)
        rows.append(PublicConsequence(
            state,action,reward,new_state,False,step==7))
        state=new_state
    return tuple(rows)


def input_vector(before,action,previous_action,previous_reward,has_previous):
    if any(type(x) is not int or x not in (0,1)
           for x in (before,action,previous_action,previous_reward,has_previous)):
        raise ValueError("CVH07_PUBLIC_INPUT_BINARY_ONLY")
    return (2*before-1,2*action-1,2*previous_action-1,
            2*previous_reward-1,has_previous,1)


def sigmoid(z):
    if z>=0:
        q=math.exp(-z)
        return 1/(1+q)
    q=math.exp(z)
    return q/(1+q)


def _clamp(v):
    return max(-5.,min(5.,v))


def strict_float(v):
    return type(v) in (int,float) and math.isfinite(v) and abs(v)<1e6


class ConventionalPublicRNN:
    """Conventional 8-unit tanh Elman BPTT, trained once before test.

    Model observes previously selected public six-field outcomes only.
    Information-matched symbol/4cell comparators are outside this class.
    """
    def __init__(self):
        rng=random.Random(WEIGHT_SEED)
        self.wx=[[round(rng.uniform(-0.2,0.2),12) for j in range(N_INPUT)]
                 for i in range(N_HIDDEN)]
        self.wh=[[round(rng.uniform(-0.15,0.15),12) for j in range(N_HIDDEN)]
                 for i in range(N_HIDDEN)]
        self.b=[0.]*N_HIDDEN
        self.wo=[round(rng.uniform(-0.2,0.2),12) for _ in range(N_HIDDEN)]
        self.bo=0.
        self.trained=False
        self.epochs_completed=0
        self.h=[0.]*N_HIDDEN
        self.previous_action=0
        self.previous_reward=0
        self.has_previous=0
        self.previous_after=None
        self.history=[]
        self.outstanding=None
        self.seen=0

    def _forward(self,x,h):
        next_h=[math.tanh(self.b[i]+
                sum(self.wx[i][k]*x[k] for k in range(N_INPUT))+
                sum(self.wh[i][k]*h[k] for k in range(N_HIDDEN)))
                for i in range(N_HIDDEN)]
        p=sigmoid(self.bo+sum(v*w for v,w in zip(self.wo,next_h)))
        return next_h,p

    def _episode(self,events):
        h=[0.]*N_HIDDEN
        previous_action=previous_reward=has_previous=0
        tape=[]
        for event in events:
            b,a,r,after,done,trunc=_event(event)
            x=input_vector(b,a,previous_action,previous_reward,has_previous)
            prev_h=h
            h,p=self._forward(x,prev_h)
            tape.append((x,prev_h,h,p,r))
            previous_action,previous_reward,has_previous=a,r,1
        return tape

    def brier(self,episodes):
        losses=[]
        for ep in episodes:
            for x,prev,h,p,r in self._episode(ep):
                losses.append((p-r)**2)
        return sum(losses)/len(losses)

    def _sgd_full_episode(self,events):
        tape=self._episode(events)
        gx=[[0.]*N_INPUT for _ in range(N_HIDDEN)]
        gh=[[0.]*N_HIDDEN for _ in range(N_HIDDEN)]
        gb=[0.]*N_HIDDEN
        go=[0.]*N_HIDDEN
        gbo=0.
        future_delta=[0.]*N_HIDDEN
        old_wo=self.wo[:]
        for x,prev_h,h,p,r in reversed(tape):
            dz=2*(p-r)*p*(1-p)/len(tape)
            gbo+=dz
            for i in range(N_HIDDEN):
                go[i]+=dz*h[i]
            delta=[
                (old_wo[i]*dz+
                 sum(self.wh[j][i]*future_delta[j] for j in range(N_HIDDEN)))*
                (1-h[i]*h[i]) for i in range(N_HIDDEN)]
            for i in range(N_HIDDEN):
                gb[i]+=delta[i]
                for k in range(N_INPUT):
                    gx[i][k]+=delta[i]*x[k]
                for k in range(N_HIDDEN):
                    gh[i][k]+=delta[i]*prev_h[k]
            future_delta=delta
        # One fully reproducible sequential optimizer step per TRAIN episode.
        # Explicit 12-decimal weight quantization removes platform-only
        # 1-ULP float reduction drift, without using any held outcome.
        for i in range(N_HIDDEN):
            self.b[i]=round(self.b[i]-LR*_clamp(gb[i]),12)
            self.wo[i]=round(self.wo[i]-LR*_clamp(go[i]),12)
            for k in range(N_INPUT):
                self.wx[i][k]=round(self.wx[i][k]-LR*_clamp(gx[i][k]),12)
            for k in range(N_HIDDEN):
                self.wh[i][k]=round(self.wh[i][k]-LR*_clamp(gh[i][k]),12)
        self.bo=round(self.bo-LR*_clamp(gbo),12)

    def fit(self,training):
        if self.trained or self.epochs_completed or self.seen or self.history:
            raise ValueError("CVH07_TRAIN_ONCE_SEPARATE_UNTOUCHED_POLICY")
        if type(training) not in (list,tuple) or len(training)!=N_TRAIN:
            raise ValueError("CVH07_FIXED_96_SOURCEFREE_TRAIN_EPISODES")
        for seed,rows in zip(range(101,197),training):
            if tuple(rows)!=training_tape(seed):
                raise ValueError("CVH07_TRAIN_ONLY_AUTHENTIC_FROZEN_TOY_PUBLIC_TAPE")
        initial=self.brier(training)
        for epoch in range(EPOCHS):
            for rows in training:
                self._sgd_full_episode(rows)
            self.epochs_completed+=1
        final=self.brier(training)
        self.trained=True
        if not (math.isfinite(initial) and math.isfinite(final)):
            raise ArithmeticError("CVH07_RNN_TRAIN_NUMERICS_INVALID")
        return initial,final

    def choose(self,state,history):
        if not self.trained or self.epochs_completed!=EPOCHS:
            raise ValueError("CVH07_RECURRENT_CONTROL_NOT_FULLY_TRAINED")
        if type(state) is not int or state not in (0,1) or type(history) is not tuple:
            raise ValueError("CVH07_INVALID_PUBLIC_SOURCE_STATE")
        if self.outstanding is not None:
            raise ValueError("CVH07_UNOBSERVED_SOURCE_ACTION_NO_REPLAY")
        prior=[_event(x) for x in history]
        if prior!=self.history or len(prior)>=MAX_ACTIONS:
            raise ValueError("CVH07_PUBLIC_HISTORY_OR_BUDGET_DRIFT")
        if (self.previous_after is None and prior) or (
                self.previous_after is not None and self.previous_after!=state):
            raise ValueError("CVH07_PUBLIC_STATE_CONTINUITY")
        scored=[]
        for action in (0,1):
            x=input_vector(state,action,self.previous_action,
                           self.previous_reward,self.has_previous)
            next_h,p=self._forward(x,self.h)
            scored.append((p,next_h))
        action=1 if scored[1][0]>scored[0][0] else 0
        self.outstanding=(state,action,scored[action][1])
        return action

    def observe(self,event):
        row=_event(event)
        if (self.outstanding is None or
                tuple(row[:2])!=self.outstanding[:2]):
            raise ValueError("CVH07_RECURRENT_UNEXPECTED_OR_PRIVATE_CONSEQUENCE")
        if self.previous_after is not None and row[0]!=self.previous_after:
            raise ValueError("CVH07_RECURRENT_UNEXPECTED_PUBLIC_TRANSITION")
        if len(self.history)>=MAX_ACTIONS or (
                len(self.history)==MAX_ACTIONS-1 and not (row[4] or row[5])):
            raise ValueError("CVH07_RECURRENT_EPISODE_ACTION_BUDGET")
        _,a,r,n,done,trunc=row
        # Commit selected action only after receiving exact public evidence.
        if done or trunc:
            self.h=[0.]*N_HIDDEN
            self.previous_after=None
            self.previous_action=self.previous_reward=self.has_previous=0
            self.history=[]
        else:
            self.h=self.outstanding[2][:]
            self.previous_after=n
            self.previous_action=a
            self.previous_reward=r
            self.has_previous=1
            self.history.append(row)
        self.outstanding=None
        self.seen+=1

    def snapshot(self):
        if self.outstanding is not None:
            raise ValueError("CVH07_OUTSTANDING_SOURCE_ACTION_NO_COLD_REPLAY")
        state={
            "schema":SCHEMA_RNN,"wx":self.wx,"wh":self.wh,"b":self.b,
            "wo":self.wo,"bo":self.bo,"trained":self.trained,
            "epochs_completed":self.epochs_completed,
            "h":[round(x,12) for x in self.h],
            "previous_action":self.previous_action,
            "previous_reward":self.previous_reward,
            "has_previous":self.has_previous,
            "previous_after":self.previous_after,
            "history":self.history,"seen":self.seen,
        }
        return canonical({"payload":state,"sha256":digest(state)})

    @classmethod
    def restore(cls,blob):
        try:
            if type(blob) is not bytes or not 0<len(blob)<20000:
                raise ValueError("COLD_BYTES")
            env=json.loads(blob)
            if (type(env) is not dict or set(env)!={"payload","sha256"}
                    or canonical(env)!=blob or digest(env["payload"])!=env["sha256"]):
                raise ValueError("COLD_CANONICAL_HASH")
            p=env["payload"]
            if (type(p) is not dict or set(p)!={
                 "schema","wx","wh","b","wo","bo","trained","epochs_completed",
                 "h","previous_action","previous_reward","has_previous",
                 "previous_after","history","seen"} or p["schema"]!=SCHEMA_RNN
                or p["trained"] is not True or p["epochs_completed"]!=EPOCHS):
                raise ValueError("COLD_SCHEMA")
            if (len(p["wx"])!=N_HIDDEN or len(p["wh"])!=N_HIDDEN
                    or len(p["b"])!=N_HIDDEN or len(p["wo"])!=N_HIDDEN
                    or len(p["h"])!=N_HIDDEN or any(len(x)!=N_INPUT for x in p["wx"])
                    or any(len(x)!=N_HIDDEN for x in p["wh"])
                    or any(not strict_float(v) for x in p["wx"]+p["wh"]
                           for v in x)
                    or any(not strict_float(v) for v in
                           p["b"]+p["wo"]+p["h"]+[p["bo"]])):
                raise ValueError("COLD_DIMENSIONS")
            if (type(p["seen"]) is not int or p["seen"]<0 or p["seen"]>1_000_000
                    or any(type(p[k]) is not int or p[k] not in (0,1)
                           for k in ("previous_action","previous_reward","has_previous"))
                    or p["previous_after"] not in (0,1,None)):
                raise ValueError("COLD_PUBLIC_COUNTERS")
            hist=p["history"]
            if (type(hist) is not list or len(hist)>=MAX_ACTIONS
                    or bool(hist)!=(p["previous_after"] is not None)
                    or bool(hist)!=(p["has_previous"]==1)):
                raise ValueError("COLD_HISTORY")
            for j,record in enumerate(hist):
                if type(record) is not list or len(record)!=6:
                    raise ValueError("COLD_EVENT")
                row=PublicConsequence(*record)
                _event(row)
                if record[-2] or record[-1] or (j and hist[j-1][3]!=record[0]):
                    raise ValueError("COLD_TRANSITION")
            if hist and (hist[-1][3]!=p["previous_after"]
                         or hist[-1][1]!=p["previous_action"]
                         or hist[-1][2]!=p["previous_reward"]):
                raise ValueError("COLD_PREVIOUS_CONTEXT")
            a=cls()
            for key in ("wx","wh","b","wo","bo","h","previous_action",
                        "previous_reward","has_previous","previous_after",
                        "history","seen","trained","epochs_completed"):
                setattr(a,key,p[key])
            if a.snapshot()!=blob:
                raise ValueError("COLD_NONCANONICAL")
            return a
        except (ValueError,TypeError,KeyError,OverflowError,AttributeError) as e:
            raise ValueError("CVH07_RECURRENT_COLD_REJECTED") from e


class SeededPublicExplorer:
    """Conventional simple deterministic binary exploration, no source access."""
    def __init__(self,seed=1777):
        if type(seed) is not int or not 1<=seed<=MASK:
            raise ValueError("CVH07_EXPLORATION_SEED_BOUND")
        self.rng=seed
        self.previous_after=None
        self.history=[]
        self.outstanding=None
        self.seen=0

    def choose(self,state,history):
        if type(state) is not int or state not in (0,1) or type(history) is not tuple:
            raise ValueError("CVH07_EXP_PUBLIC_ONLY_STATE")
        if self.outstanding is not None:
            raise ValueError("CVH07_EXP_NO_UNOBSERVED_SOURCE_REPLAY")
        if [_event(row) for row in history]!=self.history or len(history)>=MAX_ACTIONS:
            raise ValueError("CVH07_EXP_HISTORY_AND_LIMIT")
        if (self.previous_after is None and history) or (
                self.previous_after is not None and state!=self.previous_after):
            raise ValueError("CVH07_EXP_PUBLIC_CONTINUITY")
        x=self.rng
        x^=(x<<13)&MASK
        x^=x>>17
        x^=(x<<5)&MASK
        self.outstanding=(state,x&1,x&MASK)
        return x&1

    def observe(self,row):
        event=_event(row)
        if (self.outstanding is None or
                tuple(event[:2])!=self.outstanding[:2]):
            raise ValueError("CVH07_EXP_UNEXPECTED_SOURCE_EVENT")
        if len(self.history)>=MAX_ACTIONS or (
                len(self.history)==MAX_ACTIONS-1
                and not (event[4] or event[5])):
            raise ValueError("CVH07_EXP_ACTION_BUDGET")
        self.rng=self.outstanding[2]
        self.history=[] if event[4] or event[5] else self.history+[event]
        self.previous_after=None if event[4] or event[5] else event[3]
        self.seen+=1
        self.outstanding=None

    def snapshot(self):
        if self.outstanding is not None:
            raise ValueError("CVH07_EXP_UNCONFIRMED_ACTION")
        p={"schema":SCHEMA_EXPLORER,"rng":self.rng,
           "previous_after":self.previous_after,"history":self.history,
           "seen":self.seen}
        return canonical({"payload":p,"sha256":digest(p)})

    @classmethod
    def restore(cls,blob):
        try:
            if type(blob) is not bytes or not 0<len(blob)<16000:
                raise ValueError("COLD")
            obj=json.loads(blob)
            if (type(obj) is not dict or set(obj)!={"payload","sha256"}
                    or canonical(obj)!=blob or digest(obj["payload"])!=obj["sha256"]):
                raise ValueError("HASH")
            p=obj["payload"]
            if (type(p) is not dict or set(p)!={
                "schema","rng","previous_after","history","seen"}
                or p["schema"]!=SCHEMA_EXPLORER
                or type(p["rng"]) is not int or not 1<=p["rng"]<=MASK
                or type(p["seen"]) is not int or not 0<=p["seen"]<=1_000_000
                or p["previous_after"] not in (None,0,1)
                or type(p["history"]) is not list or len(p["history"])>=MAX_ACTIONS):
                raise ValueError("FIELDS")
            for i,row in enumerate(p["history"]):
                if type(row) is not list or len(row)!=6:
                    raise ValueError("BAD_EVENT")
                _event(PublicConsequence(*row))
                if row[-2] or row[-1] or (i and p["history"][i-1][3]!=row[0]):
                    raise ValueError("BAD_TRANSITION")
            if bool(p["history"])!=(p["previous_after"] is not None) or (
                    p["history"] and p["history"][-1][3]!=p["previous_after"]):
                raise ValueError("HISTORY")
            res=cls(p["rng"])
            res.rng=p["rng"];res.seen=p["seen"]
            res.previous_after=p["previous_after"];res.history=p["history"]
            if res.snapshot()!=blob:
                raise ValueError("NONCANONICAL")
            return res
        except (ValueError,TypeError,KeyError,AttributeError) as e:
            raise ValueError("CVH07_EXPLORER_COLD_REJECTED") from e
