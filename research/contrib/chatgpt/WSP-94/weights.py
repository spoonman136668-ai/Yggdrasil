"""WSP94 numeric causal signature edits and matched conventional controls.

All arms see identical five REAL observed interventions per synthetic world.
No model receives hidden world signatures or the action subset that generated
any held-out composition goal.
"""
from __future__ import annotations

from itertools import combinations
import hashlib
import json
import math

ACTION_COUNT=5
BITS=5
MASK=(1<<BITS)-1
SCHEMA="wsp94.numeric-causal-slot-weights.v1"
TRAIN_EPOCHS=350
TRAIN_LR=0.8

def canonical(x:object)->str:
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)

def verify_observation(x:dict)->None:
    keys={"action_id","causal_output_before","causal_output_after",
          "nuisance_before","nuisance_after"}
    if not isinstance(x,dict) or set(x)!=keys:
        raise ValueError("untrusted action observation has wrong source schema")
    a=x["action_id"]
    if not isinstance(a,str) or len(a)!=16 or not all(c in "0123456789abcdef" for c in a):
        raise ValueError("action IDs must be opaque 16-char lowercase hex")
    for k in ("causal_output_before","causal_output_after"):
        if type(x[k]) is not int or not(0<=x[k]<=MASK):
            raise ValueError("bad observed causal-output bit vector")
    for k in ("nuisance_before","nuisance_after"):
        if type(x[k]) is not int or not(0<=x[k]<=7):
            raise ValueError("bad observed noncausal nuisance bits")

def effect_bits(x:dict)->int:
    verify_observation(x)
    return x["causal_output_before"] ^ x["causal_output_after"]

def enumerate_plans(actions:tuple[str,...],max_actions:int=3):
    for n in range(min(max_actions,len(actions))+1):
        yield from combinations(sorted(actions),n)

def find_program_plan(signatures:dict[str,int],actions:tuple[str,...],
                      start:int,goal:int,max_actions:int)->tuple[str,...]|None:
    if type(start) is not int or type(goal) is not int or not(0<=start<=MASK and 0<=goal<=MASK):
        return None
    if max_actions!=3 or len(actions)!=ACTION_COUNT or len(set(actions))!=ACTION_COUNT:
        return None
    if any(a not in signatures for a in actions):
        return None
    for plan in enumerate_plans(actions,max_actions):
        value=start
        for action in plan:
            value^=signatures[action]
        if value==goal:
            return tuple(plan)
    return None

class DirectNumeric:
    def __init__(self):
        self.weights:dict[str,tuple[float,...]]={}
        self.observed=0

    def observe(self,x:dict)->None:
        delta=effect_bits(x)
        action=x["action_id"]
        values=tuple(float((delta>>bit)&1) for bit in range(BITS))
        if action in self.weights:
            raise ValueError("repeated action; do not replay uncertain-effect probes")
        if len(self.weights)>=ACTION_COUNT:
            raise ValueError("bounded causal intervention source exceeded")
        # Literal direct numeric writes; no gradients, no generator/hidden-map
        # read, and no training on compound target goals.
        self.weights[action]=values
        self.observed+=1

    def effect(self,action:str)->int|None:
        row=self.weights.get(action)
        if row is None:return None
        return sum((1<<bit) for bit,value in enumerate(row) if value>=0.5)

    def plan(self,actions:tuple[str,...],start:int,goal:int,max_actions:int=3)->tuple[str,...]|None:
        effects={a:self.effect(a) for a in actions}
        if any(value is None for value in effects.values()):
            return None
        return find_program_plan(effects,actions,start,goal,max_actions)

    def snapshot(self)->str:
        payload={"weights":{k:list(v) for k,v in sorted(self.weights.items())},
                 "observed":self.observed}
        body=canonical(payload)
        return canonical({"schema":SCHEMA,"payload":payload,
                          "sha256":hashlib.sha256(body.encode("ascii")).hexdigest()})

    @classmethod
    def restore(cls,text:str)->"DirectNumeric":
        env=json.loads(text)
        payload=env.get("payload")
        if not isinstance(payload,dict) or env.get("schema")!=SCHEMA or (
            hashlib.sha256(canonical(payload).encode("ascii")).hexdigest()!=env.get("sha256")):
            raise ValueError("numeric causal state checksum failed")
        weights=payload.get("weights")
        n=payload.get("observed")
        if (not isinstance(weights,dict) or type(n) is not int or
            n!=len(weights) or not(0<=n<=ACTION_COUNT)):
            raise ValueError("invalid causal weight program state")
        m=cls()
        for action,row in weights.items():
            if (not isinstance(action,str) or len(action)!=16 or
                not isinstance(row,list) or len(row)!=BITS):
                raise ValueError("malformed causal action signature")
            if any(type(v) is not float or not math.isfinite(v) or v not in (0.0,1.0) for v in row):
                raise ValueError("invalid numeric action weight")
            m.weights[action]=tuple(row)
        m.observed=n
        return m

class FullyTrainedConventional:
    """Supervised five-head one-hot logistic regression on exactly same probes."""
    def __init__(self):
        self.logits:dict[str,list[float]]={}
        self.observed=0

    def fit(self,records:tuple[dict,...])->None:
        if len(records)!=ACTION_COUNT:
            raise ValueError("conventional baseline gets exactly five interventions")
        for obs in records:
            verify_observation(obs)
        if len({x["action_id"] for x in records})!=ACTION_COUNT:
            raise ValueError("one-shot intervention data requires unique actions")
        self.logits={x["action_id"]:[0.0]*BITS for x in records}
        self.observed=len(records)
        # Actual gradient-descent fitting of a conventional linear/logistic
        # one-hot intervention classifier. No extra observations supplied.
        for _ in range(TRAIN_EPOCHS):
            for row in records:
                target=effect_bits(row)
                logits=self.logits[row["action_id"]]
                for b in range(BITS):
                    z=logits[b]
                    prediction=1.0/(1.0+math.exp(-max(-80,min(80,z))))
                    logits[b]=z+TRAIN_LR*(((target>>b)&1)-prediction)

    def effect(self,action:str)->int|None:
        row=self.logits.get(action)
        if row is None:return None
        return sum(1<<b for b,logit in enumerate(row) if logit>=0.0)

    def fitted_bits(self,records:tuple[dict,...])->tuple[int,int]:
        return (sum(((self.effect(x["action_id"])^effect_bits(x))>>b)&1==0
                    for x in records for b in range(BITS)),
                ACTION_COUNT*BITS)

    def plan(self,actions:tuple[str,...],start:int,goal:int,max_actions:int=3)->tuple[str,...]|None:
        sig={a:self.effect(a) for a in actions}
        if any(v is None for v in sig.values()):return None
        return find_program_plan(sig,actions,start,goal,max_actions)

class IndependentSymbolic:
    """Independent dictionary/readout control; direct numeric expected to tie."""
    def __init__(self):
        self.map:dict[str,int]={}

    def observe(self,x:dict)->None:
        verify_observation(x)
        a=x["action_id"]
        if a in self.map:raise ValueError("duplicate evidence source")
        self.map[a]=x["causal_output_before"]^x["causal_output_after"]

    def plan(self,actions:tuple[str,...],start:int,goal:int,max_actions:int=3)->tuple[str,...]|None:
        if len(actions)!=5 or any(a not in self.map for a in actions):
            return None
        # Explicit independent algebra implementation (no numeric planning helper).
        for size in range(0,min(max_actions,5)+1):
            for seq in combinations(tuple(sorted(actions)),size):
                measured=start
                for act in seq:
                    measured=measured^self.map[act]
                if measured==goal:
                    return tuple(seq)
        return None

class WrongActionBinding:
    """Controlled intervention/action-label swap without additional actions."""
    def __init__(self,observations:tuple[dict,...]):
        names=sorted(x["action_id"] for x in observations)
        effects={x["action_id"]:effect_bits(x) for x in observations}
        self.map={names[(i+1)%len(names)]:effects[names[i]] for i in range(len(names))}

    def plan(self,actions:tuple[str,...],start:int,goal:int,max_actions:int=3)->tuple[str,...]|None:
        return find_program_plan(self.map,actions,start,goal,max_actions)

class PassiveNoIdentity:
    """Matched observed output changes but deliberately missing action identities."""
    def __init__(self,observations:tuple[dict,...]):
        pooled=0
        for x in observations:pooled^=effect_bits(x)
        self.pooled=pooled

    def plan(self,actions:tuple[str,...],start:int,goal:int,max_actions:int=3)->tuple[str,...]|None:
        return find_program_plan({a:self.pooled for a in actions},actions,start,goal,max_actions)

class DeterministicRandom:
    """No hidden-map, training, labels or target-derived action choices."""
    def __init__(self,world_seed:int):
        self.seed=world_seed

    def plan(self,actions:tuple[str,...],start:int,goal:int,
             max_actions:int=3,goal_id:int=0)->tuple[str,...]|None:
        universe=tuple(enumerate_plans(actions,max_actions))
        seed=f"WSP94/random-plan/{self.seed}/{goal_id}"
        idx=int.from_bytes(hashlib.sha256(seed.encode("ascii")).digest()[:8],"big")%len(universe)
        return tuple(universe[idx])
