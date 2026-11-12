"""WSP53 exactly 64-step raw-address gradient plus direct numerical writes.

Entity supervision comes solely from changed observable physical registers.
The learned address routes an outcome written from observed consequences, rather
than vetoing an independent writer's output. SELFTEST engineering, not science.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
import json
import math
from controls import bits, canonical, observation, state
from direct_writer import SparseAcousticWriter, segment, grounded_change

STEPS=64
RATE=0.35
MARGIN=0.15
MAX_COEFFICIENTS=300
MODES=("warm64_direct",)

class Warm64AddressWriter:
    def __init__(self, *, family):
        state((0,)*(16 if family=="anchored_effect" else 8),family)
        self.family=family
        self.direct=SparseAcousticWriter(family=family,mode="pure_direct")
        self.a=[]
        self.b=[]
        self.coefficients={}
        self.updates=0
        self.sealed=False

    def observe(self,row):
        b,raw,a=observation(row,self.family)
        if not self.sealed and len(self.a)>=48:
            raise ValueError("seal Phase A first")
        if self.sealed and len(self.b)>=12:
            raise ValueError("Phase B action cap")
        self.direct.observe(row)
        record=(b,raw,a)
        (self.b if self.sealed else self.a).append(record)

    @staticmethod
    def _features(raw):
        words=Counter(w for p in segment(raw) for w in p)
        denom=sum(words.values())
        if denom==0:
            raise ValueError("no acoustic candidates")
        return {w:n/denom for w,n in words.items()}

    def _scores(self,raw):
        scores=[0.0]*8
        for word,scale in self._features(raw).items():
            vector=self.coefficients.get(word)
            if vector:
                for k in range(8):
                    scores[k]+=vector[k]*scale
        return scores

    def seal_a(self):
        if self.sealed or len(self.a)!=48 or self.updates:
            raise ValueError("exactly 48 Phase A evidence actions required")
        informative=[]
        for b,s,a in self.a:
            signal=grounded_change(self.family,b,a)
            if signal:
                informative.append((self._features(s),signal[0]))
        if not informative:
            raise ValueError("no identifiable physical action")
        for step in range(STEPS):
            features,target=informative[step%len(informative)]
            scores=[sum(self.coefficients.setdefault(w,[0.0]*8)[i]*v
                        for w,v in features.items()) for i in range(8)]
            top=max(scores)
            exps=[math.exp(s-top) for s in scores]
            normal=sum(exps)
            for word,value in features.items():
                row=self.coefficients[word]
                for i in range(8):
                    row[i]+=RATE*value*((1 if i==target else 0)-exps[i]/normal)
            self.updates+=1
        if len(self.coefficients)>MAX_COEFFICIENTS or self.updates!=STEPS:
            raise ValueError("gradient address budget exceeded")
        self.sealed=True

    def predict(self,before,raw):
        state(before,self.family);bits(raw)
        if not self.sealed or (before,raw) in self.direct.conflicts:
            return None
        scores=self._scores(raw)
        ranked=sorted(range(8),key=lambda i:(-scores[i],i))
        if scores[ranked[0]]-scores[ranked[1]]<MARGIN:
            return None
        entity=ranked[0]
        effects=Counter()
        for words in segment(raw):
            for slot in range(3):
                if not self.direct.entities.get((slot,words[slot],entity),0):
                    continue
                others=tuple(words[i] for i in range(3) if i!=slot)
                for effect,count in self.direct.by_address.get((slot,*others),{}).items():
                    initial,_,_=effect
                    if self.family=="anchored_effect" or initial==before[entity]:
                        effects[effect]+=count
        selected=self.direct.select(effects)
        if selected is None:
            return None
        _,location,delta=selected
        out=list(before)
        out[entity]=location
        if self.family=="anchored_effect":
            out[8+entity]=(before[8+entity]+delta)%3
        return tuple(out)

    @property
    def actions(self):
        return len(self.a)+len(self.b)

    def numeric_weight_count(self):
        return self.direct.numeric_weight_count()+sum(map(len,self.coefficients.values()))

    def snapshot(self):
        payload={"schema":"wsp53.warm64-direct.v1","family":self.family,
                 "sealed":self.sealed,"updates":self.updates,
                 "a":[[list(b),s,list(a)] for b,s,a in self.a],
                 "b":[[list(b),s,list(a)] for b,s,a in self.b],
                 "coefficients":self.coefficients,"direct":self.direct.snapshot()}
        raw=canonical(payload)
        if len(raw)>9000000:
            raise OverflowError("snapshot cap")
        return canonical({"payload":payload,"sha256":sha256(raw.encode("ascii")).hexdigest()})

    @classmethod
    def restore(cls,text):
        if type(text) is not str or len(text)>10000000:
            raise ValueError("bad snapshot size")
        try:
            box=json.loads(text)
            if type(box) is not dict or set(box)!={"payload","sha256"}:
                raise ValueError("bad envelope")
            p=box["payload"]
            if (type(p) is not dict or set(p)!={"schema","family","sealed","updates",
                    "a","b","coefficients","direct"} or
                p["schema"]!="wsp53.warm64-direct.v1" or
                sha256(canonical(p).encode("ascii")).hexdigest()!=box["sha256"]):
                raise ValueError("snapshot tampered")
            obj=cls(family=p["family"])
            if (type(p["sealed"]) is not bool or type(p["updates"]) is not int or
                p["updates"]!=(STEPS if p["sealed"] else 0) or
                type(p["a"]) is not list or type(p["b"]) is not list or
                len(p["a"])>(48) or len(p["b"])>12 or
                p["sealed"]!=(len(p["a"])==48) or
                (p["b"] and not p["sealed"])):
                raise ValueError("invalid protocol counters")
            def reconstruct(rows):
                out=[]
                for row in rows:
                    if type(row) is not list or len(row)!=3:
                        raise ValueError("invalid observation")
                    b,s,a=row
                    if type(b) is not list or type(a) is not list:
                        raise ValueError("bad physical input")
                    out.append((state(tuple(b),obj.family),bits(s),state(tuple(a),obj.family)))
                return out
            obj.a=reconstruct(p["a"]);obj.b=reconstruct(p["b"])
            obj.direct=SparseAcousticWriter.restore(p["direct"])
            if (obj.direct.family!=obj.family or
                obj.direct.actions!=len(obj.a)+len(obj.b) or
                obj.direct.mode!="pure_direct" or
                type(p["coefficients"]) is not dict or
                len(p["coefficients"])>MAX_COEFFICIENTS):
                raise ValueError("numeric writer inconsistency")
            for word,weights in p["coefficients"].items():
                if (type(word) is not str or len(word) not in (4,5,6) or
                    set(word)-{"0","1"} or type(weights) is not list or len(weights)!=8
                    or any(type(x) is not float or not math.isfinite(x) for x in weights)):
                    raise ValueError("bad address coefficients")
            obj.coefficients=p["coefficients"]
            obj.updates=p["updates"];obj.sealed=p["sealed"]
            if obj.snapshot()!=text:
                raise ValueError("noncanonical snapshot")
            return obj
        except (KeyError,TypeError,IndexError,UnicodeError,json.JSONDecodeError) as ex:
            raise ValueError("malformed snapshot") from ex

    def capacity_bits(self):
        return len(self.snapshot().encode("ascii"))*8
