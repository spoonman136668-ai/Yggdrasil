"""WSP95 source-observation numeric learning and matched policy controls.

All numeric weights are directly written counts of observed 7-bit before/after
changes. The causal channel mask is selected from empirical stability; neither
the true mask nor the hidden action-effects map enters these classes.
"""
from __future__ import annotations

from itertools import combinations
import hashlib
import json
import math

N_ACTIONS=6
N_CHANNELS=7
N_STABLE=5
MASK=(1<<N_CHANNELS)-1
S=120
SGD_LR=0.6
SCHEMA="wsp95.direct-noisy-sensor-counts.v1"

def canonical(obj:object)->str:
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)

def sha(obj:object)->str:
    return hashlib.sha256(canonical(obj).encode("ascii")).hexdigest()

def hamming(x:int)->int:
    return x.bit_count()

def validate_record(row:dict)->None:
    if not isinstance(row,dict) or set(row)!={
       "action_id","probe_index","sensor_before","sensor_after"}:
        raise ValueError("invalid observed source schema")
    if not isinstance(row["action_id"],str) or len(row["action_id"])!=16:
        raise ValueError("opaque action ID invalid")
    for key in ("probe_index","sensor_before","sensor_after"):
        if type(row[key]) is not int:
            raise ValueError("non-integer observation")
    if (not 0<=row["probe_index"]<30 or
        not 0<=row["sensor_before"]<=MASK or
        not 0<=row["sensor_after"]<=MASK):
        raise ValueError("out-of-range observation")

def plan_from_estimates(effects:dict[str,int],actions:tuple[str,...],
                        start:int,target:int,max_actions:int=3)->tuple[str,...]|None:
    if (type(start) is not int or type(target) is not int or
        not (0<=start<=MASK and 0<=target<=MASK) or
        max_actions!=3 or not isinstance(actions,tuple) or
        len(actions)!=N_ACTIONS or len(set(actions))!=N_ACTIONS):
        return None
    if any(a not in effects for a in actions):
        return None
    ordered=sorted(actions)
    best=None
    for count in range(max_actions+1):
        for candidate in combinations(ordered,count):
            state=start
            for action in candidate:
                state^=effects[action]
            score=(hamming(state^target),len(candidate),candidate)
            if best is None or score<best[0]:
                best=(score,tuple(candidate))
    return best[1] if best is not None else None

class DirectCounts:
    def __init__(self,actions:tuple[str,...]):
        if len(actions)!=N_ACTIONS or len(set(actions))!=N_ACTIONS or any(
           not isinstance(a,str) or len(a)!=16 for a in actions):
            raise ValueError("action catalogue malformed")
        self.actions=tuple(sorted(actions))
        self.counts={a:[0]*N_CHANNELS for a in actions}
        self.n={a:0 for a in actions}
        self.interventions=0

    def choose_action(self)->str:
        # Frozen policy: guarantee coverage first, then use outcome
        # uncertainty for ties among least-probed actions. Under the
        # exchangeable world family this generally matches round robin
        # allocation; no claimed adaptation advantage if they tie.
        def priority(a):
            n=self.n[a]
            if n==0:uncertainty=1.75
            else:uncertainty=sum(
                (self.counts[a][j]/n)*(1-self.counts[a][j]/n)
                for j in range(N_CHANNELS))
            return (n,-uncertainty,a)
        return min(self.actions,key=priority)

    def observe(self,row:dict)->None:
        validate_record(row)
        action=row["action_id"]
        if action not in self.counts or row["probe_index"]!=self.n[action]:
            raise ValueError("unrecognized or replayed action trial")
        if self.interventions>=30:raise ValueError("intervention budget exhausted")
        diff=row["sensor_before"]^row["sensor_after"]
        for bit in range(N_CHANNELS):
            self.counts[action][bit]+=(diff>>bit)&1
        self.n[action]+=1
        self.interventions+=1

    def stable_channels(self)->tuple[int,...]:
        scores=[]
        for bit in range(N_CHANNELS):
            # Reliability computed across independently intervened actions,
            # with unknown true channel positions.
            stability=sum(
                abs((2*self.counts[a][bit]/self.n[a])-1) if self.n[a]>0 else 0.0
                for a in self.actions)/len(self.actions)
            scores.append((-stability,bit))
        return tuple(sorted(bit for _,bit in sorted(scores)[:N_STABLE]))

    def effects(self)->dict[str,int]:
        stable=self.stable_channels()
        result={}
        for action in self.actions:
            n=self.n[action]
            if n==0:continue
            effect=0
            for bit in stable:
                if 2*self.counts[action][bit]>n:effect|=1<<bit
            result[action]=effect
        return result

    def plan(self,actions:tuple[str,...],start:int,target:int,max_actions:int=3):
        return plan_from_estimates(self.effects(),actions,start,target,max_actions)

    def snapshot(self)->str:
        payload={"actions":list(self.actions),
                 "counts":{a:list(self.counts[a]) for a in self.actions},
                 "n":{a:self.n[a] for a in self.actions},
                 "interventions":self.interventions}
        return canonical({"schema":SCHEMA,"payload":payload,"sha256":sha(payload)})

    @classmethod
    def restore(cls,text:str)->"DirectCounts":
        env=json.loads(text);data=env.get("payload")
        if (env.get("schema")!=SCHEMA or not isinstance(data,dict) or
            sha(data)!=env.get("sha256")):
            raise ValueError("causal source state checksum mismatch")
        actions=data.get("actions")
        if not isinstance(actions,list) or len(actions)!=N_ACTIONS:
            raise ValueError("bad source action catalogue")
        model=cls(tuple(actions))
        counts=data.get("counts");n=data.get("n")
        if (not isinstance(counts,dict) or not isinstance(n,dict) or
            set(counts)!=set(actions) or set(n)!=set(actions)):
            raise ValueError("bad channel observation source")
        for action in actions:
            row=counts[action];count=n[action]
            if (type(count) is not int or not 0<=count<=30 or
                not isinstance(row,list) or len(row)!=N_CHANNELS or
                any(type(v) is not int or not 0<=v<=count for v in row)):
                raise ValueError("invalid numerical observation counts")
            model.n[action]=count
            model.counts[action]=row[:]
        model.interventions=data.get("interventions")
        if (type(model.interventions) is not int or
            model.interventions!=sum(model.n.values()) or
            model.interventions>30):
            raise ValueError("observation budget or count mismatch")
        return model

class SymbolicHistogram:
    """Independent symbolic counts/majority control, same active probes."""
    def __init__(self,actions:tuple[str,...]):
        self.actions=tuple(sorted(actions))
        self.hist={a:[0,0,0,0,0,0,0] for a in self.actions}
        self.num={a:0 for a in self.actions}

    def observe(self,row:dict):
        validate_record(row)
        a=row["action_id"]
        if a not in self.hist or row["probe_index"]!=self.num[a]:
            raise ValueError("independent symbolic intervention source mismatch")
        diff=row["sensor_before"]^row["sensor_after"]
        for bit in range(N_CHANNELS):
            self.hist[a][bit]+=(diff>>bit)&1
        self.num[a]+=1

    def stable(self):
        per=[]
        for bit in range(N_CHANNELS):
            stability=sum(
               abs((2*self.hist[a][bit]/self.num[a])-1)
               if self.num[a] else 0
               for a in self.actions)/len(self.actions)
            per.append((stability,bit))
        picked=sorted(per,key=lambda p:(-p[0],p[1]))[:N_STABLE]
        return tuple(sorted(bit for value,bit in picked))

    def effects(self):
        stable=self.stable()
        return {a:sum((1<<bit) for bit in stable
                    if self.hist[a][bit]*2>self.num[a])
                for a in self.actions if self.num[a]}

    def plan(self,actions,start,target,max_actions=3):
        effects=self.effects()
        if any(a not in effects for a in actions):return None
        # Independent planner, not using numerical model scoring function.
        best=None
        for n in range(0,4):
            for candidate in combinations(sorted(actions),n):
                actual=start
                for a in candidate:actual^=effects[a]
                rank=(hamming(actual^target),n,candidate)
                if best is None or rank<best[0]:
                    best=(rank,tuple(candidate))
        return best[1] if best else None

class FullyTrainedLogistic:
    """Seven logistic binary heads per action; trained on observed transitions."""
    def __init__(self,actions:tuple[str,...]):
        self.actions=tuple(sorted(actions))
        self.logits={a:[0.0]*N_CHANNELS for a in actions}
        self.records=0

    def fit(self,records:tuple[dict,...])->None:
        if len(records)!=30:raise ValueError("requires exactly 30 observed probes")
        counts={a:0 for a in self.actions}
        for obs in records:
            validate_record(obs)
            a=obs["action_id"]
            if a not in counts or obs["probe_index"]!=counts[a]:
                raise ValueError("source action trial order invalid")
            counts[a]+=1
        self.records=len(records)
        # Fully optimize independent one-hot action and channel parameters.
        for _ in range(S):
            for obs in records:
                a=obs["action_id"]
                diff=obs["sensor_before"]^obs["sensor_after"]
                for bit in range(N_CHANNELS):
                    z=self.logits[a][bit]
                    p=1.0/(1+math.exp(-max(-80,min(80,z))))
                    self.logits[a][bit]+=SGD_LR*(((diff>>bit)&1)-p)

    def stable(self):
        vals=[]
        for bit in range(N_CHANNELS):
            confidence=sum(abs(2/(1+math.exp(-self.logits[a][bit]))-1)
                           for a in self.actions)/len(self.actions)
            vals.append((-confidence,bit))
        return tuple(sorted(bit for confidence,bit in sorted(vals)[:N_STABLE]))

    def effects(self):
        stable=self.stable()
        return {a:sum((1<<bit) for bit in stable if self.logits[a][bit]>0)
                for a in self.actions}

    def plan(self,actions,start,target,max_actions=3):
        return plan_from_estimates(self.effects(),actions,start,target,max_actions)

class WrongActionAssociation:
    def __init__(self,model:DirectCounts):
        names=sorted(model.actions)
        original=model.effects()
        self.effects_map={names[(i+1)%len(names)]:original[a]
                          for i,a in enumerate(names) if a in original}

    def plan(self,actions,start,target,max_actions=3):
        return plan_from_estimates(self.effects_map,actions,start,target,max_actions)
