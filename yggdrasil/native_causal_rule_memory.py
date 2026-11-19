"""YGG-CAP02 opt-in evidence-selected native causal-rule memory.

An independent, tokenless causal mechanism representation: each retained
16-intervention bank learns posterior support for predeclared Boolean rules
from *witnessed public action-consequence evidence*. Banks freeze when full;
new learning is additive. Bank relevance comes only from prequential
predictive likelihood on the last six already-observed interventions.

No hidden phase labels, oracle outcome in readouts, external source actors,
controller, accepted native replacement, or transformer/token learner.
"""
from __future__ import annotations
import json
import math
from yggdrasil.native_context_basis import canonical,digest,pin,require

SCHEMA="yggdrasil.cap02.public-causal-rule-memory.v1"
NOISE=0.075
BANK_SIZE=16
EVIDENCE_WINDOW=6
MAX_BANKS=5
MAX_NEW=48
MAX_CHECKPOINT_BYTES=300*1024

def _bit(x):
    require(type(x) is int and x in (0,1),"CAP02_BINARY_PUBLIC")
    return x

def _views(views):
    require(type(views) is tuple and len(views)==2 and
            all(type(v) is tuple and len(v)==2 for v in views),
            "CAP02_PAIRED_PUBLIC_VIEW")
    for v in views:
        for val in v:
            _bit(val)
    return views

def _event(source_id,views,row,post):
    require(pin(source_id),"CAP02_PUBLIC_SOURCE_ID")
    views=_views(views)
    require(type(row) is dict and set(row)=={"s1","x1","s2","x2","y"},
            "CAP02_PUBLIC_ROW")
    for val in row.values():
        _bit(val)
    require(type(post) is tuple and len(post)==3 and
            all(type(x) is int and x in (0,1) for x in post),
            "CAP02_POST_WITNESS")
    require(row["s1"]==views[0][0] and row["s2"]==post[1],
            "CAP02_PUBLIC_CONTINUITY")
    return (source_id,views,row["x1"],row["s2"],row["x2"],row["y"],post)

def _new_to_row(event):
    return {
        "s1":event[1][0][0],"x1":event[2],
        "s2":event[3],"x2":event[4],"y":event[5],
    }

def _features(views,a,s2=None,b=None):
    views=_views(views)
    a=_bit(a)
    u,v=views[0]
    w=views[1][1]
    if s2 is None:
        require(b is None,"CAP02_NO_SECOND_ACTION_BEFORE_TRANSITION")
        return (u,v,w,a)
    return (u,v,w,a,_bit(s2),_bit(b))

def _rules(dim):
    require(dim in (4,6),"CAP02_RULE_DIM")
    rules=[("zero",),("one",)]
    for i in range(dim):
        rules.extend((("bit",i),("not",i)))
    for i in range(dim):
        for j in range(i+1,dim):
            rules.extend((("xor",i,j),("nxor",i,j),
                          ("and",i,j),("or",i,j)))
    return tuple(rules)

def _apply(rule,x):
    kind=rule[0]
    if kind=="zero":
        return 0
    if kind=="one":
        return 1
    if kind=="bit":
        return x[rule[1]]
    if kind=="not":
        return 1-x[rule[1]]
    a,b=x[rule[1]],x[rule[2]]
    if kind=="xor":
        return a^b
    if kind=="nxor":
        return 1-(a^b)
    if kind=="and":
        return a&b
    if kind=="or":
        return a|b
    raise ValueError("CAP02_UNREGISTERED_BOOLEAN_RULE")

class CausalPosterior:
    """Fitted posterior over public intervention-conditioned Boolean rules."""
    __slots__=("dim","rules","log_weights","updates")
    def __init__(self,dim):
        self.dim=dim
        self.rules=_rules(dim)
        self.log_weights=[0.0]*len(self.rules)
        self.updates=0

    def predict(self,x):
        require(type(x) is tuple and len(x)==self.dim and
                all(type(a) is int and a in (0,1) for a in x),
                "CAP02_PREDICTION_INPUT")
        reference=max(self.log_weights)
        weights=[math.exp(w-reference) for w in self.log_weights]
        z=sum(weights)
        require(math.isfinite(z) and z>0,"CAP02_POSTERIOR_NORMALIZER")
        q=sum(weight*(_apply(rule,x)*(1-2*NOISE)+NOISE)
              for weight,rule in zip(weights,self.rules))/z
        require(math.isfinite(q) and NOISE-1e-12<=q<=1-NOISE+1e-12,
                "CAP02_POSTERIOR_PROBABILITY")
        return min(1-NOISE,max(NOISE,q))

    def learn(self,x,y):
        y=_bit(y)
        require(type(x) is tuple and len(x)==self.dim,
                "CAP02_PUBLIC_FEATURE_COUNT")
        previous=self.log_weights
        out=[]
        for value,rule in zip(previous,self.rules):
            fits=(_apply(rule,x)==y)
            out.append(value+math.log(1-NOISE if fits else NOISE))
        shift=max(out)
        self.log_weights=[value-shift for value in out]
        self.updates+=1

    def snapshot(self):
        return {"dim":self.dim,"weights":self.log_weights,
                "updates":self.updates}

class _Bank:
    __slots__=("transition","reward","count","evidence")
    def __init__(self):
        self.transition=CausalPosterior(4)
        self.reward=CausalPosterior(6)
        self.count=0
        # Neutral unearned score (both unbiased binary outcomes p=.5).
        self.evidence=[-math.log(.25)]*EVIDENCE_WINDOW

    def stage1(self,views,a):
        return self.transition.predict(_features(views,a))

    def stage2(self,views,a,s2,b):
        return self.reward.predict(_features(views,a,s2,b))

    def learn(self,views,a,s2,b,y):
        require(self.count<BANK_SIZE,"CAP02_FROZEN_BANK_CANNOT_RELEARN")
        self.transition.learn(_features(views,a),s2)
        self.reward.learn(_features(views,a,s2,b),y)
        self.count+=1

    def evidence_weight(self):
        return math.exp(-sum(self.evidence))

    def snapshot(self):
        return {"count":self.count,"transition":self.transition.snapshot(),
                "reward":self.reward.snapshot(),"evidence":self.evidence}

class CausalMemory:
    """Replay-verified multi-bank learned causal memory; source owns actions.

    Initial 32 original CAP01 public source events are accepted by a separate
    read-only caller-provided pinned model. Subsequent 48 events follow the
    exact previously-witnessed public state. All evidence and learned weights
    can be reconstructed from the original source and new event tape.
    """
    def __init__(self,prior_events):
        require(type(prior_events) is tuple and len(prior_events)==32,
                "CAP02_INITIAL_32_SOURCE")
        self._prior=prior_events
        self._initial_sha=digest(canonical(prior_events))
        self._events=()
        self._banks=[]
        self._seen=set()
        self._last=None
        for e in prior_events:
            require(type(e) is tuple and len(e)==7,
                    "CAP02_PRIOR_PUBLIC_TAPE")
            self._insert(_event(e[0],e[1],_new_to_row(e),e[6]))
        require(len(self._banks)==2 and
                [x.count for x in self._banks]==[16,16],
                "CAP02_INITIAL_TWO_CAUSAL_BANKS")

    @classmethod
    def from_native(cls,model):
        require(model.new_count==32 and
                len(model._events)==32,
                "CAP02_RESTORE_CERTIFIED_CAP01_32")
        return cls(model._events)

    @property
    def prior_sha256(self):
        return self._initial_sha

    @property
    def new_count(self):
        return len(self._events)

    @property
    def total(self):
        return len(self._prior)+self.new_count

    @property
    def bank_sizes(self):
        return tuple(b.count for b in self._banks)

    def _weights(self):
        vals=[b.evidence_weight() for b in self._banks]
        # An empty bank enters the competition only AFTER an actual
        # new intervention exists; read-only forecasts never mutate counts.
        if self._banks[-1].count==BANK_SIZE:
            require(len(self._banks)<MAX_BANKS,
                    "CAP02_EVIDENCE_BANK_CAP")
            vals.append(_Bank().evidence_weight())
        z=sum(vals)
        require(z>0 and math.isfinite(z),"CAP02_GATE_NORMALIZER")
        return tuple(x/z for x in vals)

    def _available_banks(self):
        if self._banks[-1].count==BANK_SIZE:
            require(len(self._banks)<MAX_BANKS,
                    "CAP02_NO_MORE_CAUSAL_BANKS")
            return tuple(self._banks)+(_Bank(),)
        return tuple(self._banks)

    def forecast(self,views,a,s2=None,b=None,*,variant="evidence"):
        x=_features(views,a,s2,b)
        banks=self._available_banks()
        probabilities=[
            bank.stage1(views,a) if s2 is None else
            bank.stage2(views,a,s2,b)
            for bank in banks
        ]
        if variant=="evidence":
            weights=self._weights()
        elif variant=="uniform":
            weights=(1/len(banks),)*len(banks)
        elif variant=="latest":
            weights=(0.,)*(len(banks)-1)+(1.,)
        elif variant=="action_masked":
            probabilities=[
                bank.stage1(views,0) if s2 is None else
                bank.stage2(views,0,s2,0)
                for bank in banks
            ]
            weights=self._weights()
        else:
            raise ValueError("CAP02_UNKNOWN_PREDECLARED_CONTROL")
        p=sum(w*q for w,q in zip(weights,probabilities))
        require(NOISE-1e-12<=p<=1-NOISE+1e-12,
                "CAP02_FINITE_EVIDENCE_MIXTURE")
        return float(p)

    def _insert(self,event):
        identifier,views,a,s2,b,y,post=event
        require(identifier not in self._seen,
                "CAP02_DUPLICATE_SOURCE_ID")
        last=self._last
        if last is not None:
            target=(views[0][0],views[0][1],views[1][1])
            require(last[6]==target,"CAP02_PUBLIC_SEQUENCE_BREAK")
        if not self._banks or self._banks[-1].count==BANK_SIZE:
            require(len(self._banks)<MAX_BANKS,"CAP02_BANK_CAPACITY")
            self._banks.append(_Bank())
        pre=[
            (bank.stage1(views,a),bank.stage2(views,a,s2,b))
            for bank in self._banks
        ]
        for bank,(p,q) in zip(self._banks,pre):
            likelihood=(p if s2 else 1-p)*(q if y else 1-q)
            require(likelihood>0 and math.isfinite(likelihood),
                    "CAP02_PREQUENTIAL_EVIDENCE")
            bank.evidence=(bank.evidence+[-math.log(likelihood)])[
                -EVIDENCE_WINDOW:]
        self._banks[-1].learn(views,a,s2,b,y)
        self._seen.add(identifier)
        self._last=event

    def observe(self,identifier,views,row,post):
        event=_event(identifier,views,row,post)
        if identifier in self._seen:
            if event in self._prior+self._events:
                raise ValueError("CAP02_PRIOR_SOURCE_REUSE_FORBIDDEN")
            raise ValueError("CAP02_CONFLICTING_SOURCE_REPLAY")
        require(self.new_count<MAX_NEW,
                "CAP02_FIRST_USE_DEVELOPMENT_LIMIT")
        self._insert(event)
        self._events+=(event,)
        return self

    def checkpoint(self):
        data={
            "schema":SCHEMA,
            "initial_source_sha256":self._initial_sha,
            "old_count":len(self._prior),
            "new_events":self._events,
            "banks":[bank.snapshot() for bank in self._banks],
        }
        raw=canonical(data)
        require(0<len(raw)<=MAX_CHECKPOINT_BYTES,
                "CAP02_CHECKPOINT_BYTE_LIMIT")
        return raw

    @classmethod
    def restore(cls,raw,sha,prior_events):
        require(type(raw) is bytes and pin(sha) and digest(raw)==sha and
                0<len(raw)<=MAX_CHECKPOINT_BYTES,
                "CAP02_CHECKPOINT_SOURCE_HASH")
        try:
            record=json.loads(raw.decode("ascii"))
            require(type(record) is dict and set(record)=={
                "schema","initial_source_sha256","old_count",
                "new_events","banks"
            } and record["schema"]==SCHEMA and canonical(record)==raw,
                    "CAP02_CHECKPOINT_SCHEMA")
            rebuilt=cls(prior_events)
            require(record["old_count"]==32 and
                    record["initial_source_sha256"]==rebuilt.prior_sha256 and
                    len(record["new_events"])<=MAX_NEW,
                    "CAP02_CHECKPOINT_ORIGINAL_SOURCE")
            for entry in record["new_events"]:
                require(type(entry) is list and len(entry)==7,
                        "CAP02_REPLAY_ENTRY")
                identifier,view,a,s2,b,y,post=entry
                views=tuple(tuple(v) for v in view)
                rebuilt.observe(identifier,views,{
                    "s1":views[0][0],"x1":a,"s2":s2,"x2":b,"y":y,
                },tuple(post))
            require(rebuilt.checkpoint()==raw,
                    "CAP02_REHASHED_WEIGHTS_OR_EVIDENCE_FORGERY")
            return rebuilt
        except (KeyError,TypeError,AttributeError,ValueError,IndexError,
                RecursionError,UnicodeError) as exc:
            raise ValueError("CAP02_COLD_REPLAY_REJECTED") from exc
