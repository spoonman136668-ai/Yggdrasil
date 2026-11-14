"""WSP96 causal effect models consume outcome-only DO records, never hidden U.

Direct numeric weights are strictly observed outcome counts. An independent
fully-trained conventional logistic baseline gets the same DO records. A
separate observational-only control sees endogenous action/outcome logging.
"""
from __future__ import annotations

from itertools import combinations
import hashlib
import json
import math

BITS=5
MASK=31
ACTION_COUNT=6
DO_PER_ACTION=24
EPOCHS=200
LR=.8
SCHEMA="wsp96.direct-interventional-effect-counts.v1"

def canonical(x:object)->str:
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)

def sha(x:object)->str:
    return hashlib.sha256(canonical(x).encode("ascii")).hexdigest()

def validate_source(row:dict)->None:
    if (not isinstance(row,dict) or set(row)!={"action_id","trial","observed_outcome"} or
        not isinstance(row["action_id"],str) or len(row["action_id"])!=16 or
        any(x not in "0123456789abcdef" for x in row["action_id"]) or
        type(row["trial"]) is not int or row["trial"]<0 or
        type(row["observed_outcome"]) is not int or
        not(0<=row["observed_outcome"]<=MASK)):
        raise ValueError("original observed do/association source record invalid")

def choose_plan(effects:dict[str,int],actions:tuple[str,...],
                start:int,target:int,max_actions:int=3)->tuple[str,...]|None:
    if (type(start) is not int or type(target) is not int or
        not (0<=start<=MASK and 0<=target<=MASK) or max_actions!=3 or
        not isinstance(actions,tuple) or len(actions)!=ACTION_COUNT or
        len(set(actions))!=ACTION_COUNT or any(a not in effects for a in actions)):
        return None
    for n in range(4):
        for chosen in combinations(sorted(actions),n):
            value=start
            for action in chosen:
                value^=effects[action]
            if value==target:
                return tuple(chosen)
    return None

class DirectDoWeights:
    def __init__(self,actions:tuple[str,...]):
        if len(actions)!=ACTION_COUNT or len(set(actions))!=ACTION_COUNT:
            raise ValueError("six opaque registered actions required")
        self.actions=tuple(sorted(actions))
        self.n={a:0 for a in actions}
        self.ones={a:[0]*BITS for a in actions}
        self.seen=0

    def observe(self,record:dict)->None:
        validate_source(record)
        a=record["action_id"]
        if a not in self.n or record["trial"]!=self.n[a] or self.n[a]>=DO_PER_ACTION:
            raise ValueError("unknown, duplicated or reordered intervention")
        out=record["observed_outcome"]
        for bit in range(BITS):
            self.ones[a][bit]+=(out>>bit)&1
        self.n[a]+=1
        self.seen+=1

    def effects(self)->dict[str,int]:
        result={}
        for action in self.actions:
            n=self.n[action]
            if n!=DO_PER_ACTION:continue
            result[action]=sum((1<<bit) for bit in range(BITS)
                               if self.ones[action][bit]*2>n)
        return result

    def plan(self,actions:tuple[str,...],start:int,target:int,max_actions:int=3):
        return choose_plan(self.effects(),actions,start,target,max_actions)

    def snapshot(self)->str:
        body={"actions":list(self.actions),"n":dict(sorted(self.n.items())),
              "ones":{a:list(self.ones[a]) for a in self.actions},"seen":self.seen}
        return canonical({"schema":SCHEMA,"body":body,"sha256":sha(body)})

    @classmethod
    def restore(cls,text:str)->"DirectDoWeights":
        env=json.loads(text);data=env.get("body")
        if env.get("schema")!=SCHEMA or not isinstance(data,dict) or sha(data)!=env.get("sha256"):
            raise ValueError("numeric interventional memory checksum invalid")
        actions=data.get("actions")
        if not isinstance(actions,list) or len(actions)!=ACTION_COUNT:
            raise ValueError("wrong original action catalogue")
        m=cls(tuple(actions))
        if set(data.get("n",{}))!=set(actions) or set(data.get("ones",{}))!=set(actions):
            raise ValueError("corrupted count table")
        for a in actions:
            count=data["n"][a];bits=data["ones"][a]
            if (type(count) is not int or not(0<=count<=DO_PER_ACTION) or
                not isinstance(bits,list) or len(bits)!=BITS or
                any(type(v) is not int or not(0<=v<=count) for v in bits)):
                raise ValueError("invalid numeric evidence")
            m.n[a]=count;m.ones[a]=bits[:]
        m.seen=data.get("seen")
        if type(m.seen) is not int or m.seen!=sum(m.n.values()):
            raise ValueError("memory observation budget mismatch")
        return m

class ConventionalLogistic:
    """Fully trained 200-pass independent sigmoid output heads, one-hot actions."""
    def __init__(self,actions:tuple[str,...]):
        self.actions=tuple(sorted(actions))
        self.logits={a:[0.0]*BITS for a in actions}
        self.training_examples=0

    def fit(self,records:tuple[dict,...])->None:
        if len(records)!=ACTION_COUNT*DO_PER_ACTION:
            raise ValueError("ordinary model requires full original DO budget")
        counts={a:0 for a in self.actions}
        ones={a:[0]*BITS for a in self.actions}
        for row in records:
            validate_source(row);a=row["action_id"]
            if a not in counts or row["trial"]!=counts[a]:
                raise ValueError("unqualified source record order")
            counts[a]+=1
            for bit in range(BITS):
                ones[a][bit]+=(row["observed_outcome"]>>bit)&1
        if any(v!=DO_PER_ACTION for v in counts.values()):
            raise ValueError("unbalanced original interventions")
        self.training_examples=len(records)
        self.logits={a:[0.0]*BITS for a in self.actions}
        # Actual conventional full-batch gradient descent; every observed
        # record contributes through the empirical supervised sigmoid loss.
        for _ in range(EPOCHS):
            for a in self.actions:
                for bit in range(BITS):
                    z=self.logits[a][bit]
                    p=1/(1+math.exp(-max(-80,min(80,z))))
                    frequency=ones[a][bit]/counts[a]
                    self.logits[a][bit]+=LR*(frequency-p)

    def effects(self)->dict[str,int]:
        return {a:sum((1<<bit) for bit in range(BITS)
                      if self.logits[a][bit]>0.0)
                for a in self.actions}

    def plan(self,actions:tuple[str,...],start:int,target:int,max_actions:int=3):
        return choose_plan(self.effects(),actions,start,target,max_actions)

class IndependentSymbolic:
    """Independent count dictionary and independent shortest exact XOR planner."""
    def __init__(self,actions:tuple[str,...]):
        self.actions=tuple(sorted(actions))
        self.by_action={a:[0]*32 for a in actions}

    def observe(self,row:dict):
        validate_source(row)
        a=row["action_id"]
        if a not in self.by_action or sum(self.by_action[a])>=DO_PER_ACTION:
            raise ValueError("unknown action or exhausted source")
        self.by_action[a][row["observed_outcome"]]+=1

    def effects(self):
        effect={}
        for a,counts in self.by_action.items():
            n=sum(counts)
            if n!=DO_PER_ACTION:continue
            delta=0
            for bit in range(BITS):
                yes=sum(count for y,count in enumerate(counts) if (y>>bit)&1)
                if yes*2>n:delta^=1<<bit
            effect[a]=delta
        return effect

    def plan(self,actions,start,target,max_actions=3):
        effect=self.effects()
        if len(actions)!=ACTION_COUNT or any(a not in effect for a in actions):
            return None
        for size in range(max_actions+1):
            for subset in combinations(sorted(actions),size):
                diff=0
                for a in subset:diff^=effect[a]
                if start^diff==target:return tuple(subset)
        return None

class ObservationalNaive:
    """Association != intervention: only logged A,Y, U is UNOBSERVED."""
    def __init__(self,actions:tuple[str,...]):
        self.actions=tuple(sorted(actions))
        self.n={a:0 for a in actions}
        self.ones={a:[0]*BITS for a in actions}
        self.seen_trials=set()

    def observe(self,record:dict):
        validate_source(record)
        a=record["action_id"]
        if a not in self.n or record["trial"] in self.seen_trials:
            raise ValueError("invalid or repeated logged observational record")
        self.seen_trials.add(record["trial"])
        self.n[a]+=1
        for bit in range(BITS):
            self.ones[a][bit]+=(record["observed_outcome"]>>bit)&1

    def effects(self):
        return {a:sum((1<<bit) for bit in range(BITS)
                      if self.ones[a][bit]*2>self.n[a])
                for a in self.actions if self.n[a]}

    def plan(self,actions,start,target,max_actions=3):
        return choose_plan(self.effects(),actions,start,target,max_actions)

class WrongActionAssociation:
    def __init__(self,source:DirectDoWeights,control_id:str):
        eff=source.effects()
        active=sorted(a for a in source.actions if a!=control_id)
        self.map={control_id:eff[control_id]}
        self.map.update({active[(i+1)%len(active)]:eff[a]
                         for i,a in enumerate(active)})

    def plan(self,actions,start,target,max_actions=3):
        return choose_plan(self.map,actions,start,target,max_actions)

class DeterministicRandomPlan:
    def __init__(self,seed:int):self.seed=seed
    def plan(self,actions,start,target,max_actions=3,goal_index=0):
        plans=tuple(subset for n in range(max_actions+1)
                    for subset in combinations(sorted(actions),n))
        key=f"WSP96/random/{self.seed}/{goal_index}"
        choice=int.from_bytes(hashlib.sha256(key.encode("ascii")).digest()[:8],"big")
        return tuple(plans[choice%len(plans)])
