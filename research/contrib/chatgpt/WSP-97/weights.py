"""WSP97 learned passive function and numeric posterior over competing SCMs.

This is a deliberately small, interpretable hypothesis-selection algorithm,
NOT autonomous causal-program invention. Symbolic Bayesian and conventional
supervised tabular baselines see the SAME passive and active do evidence.
"""
from __future__ import annotations

import hashlib
import json
import math
from itertools import product

N_CONTEXTS=8
PASSIVE_RECORDS=32
DO_BUDGET=3
U_ONE=.20
FLIP=.02
SCHEMA="wsp97.direct-numeric-hypothesis-weight.v1"

def canonical(data:object)->str:
    return json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)

def sha(data:object)->str:
    return hashlib.sha256(canonical(data).encode("ascii")).hexdigest()

def validate_passive(record:dict)->None:
    if (not isinstance(record,dict) or
        set(record)!={"context_id","setting","action","observed_y"} or
        type(record["context_id"]) is not int or
        not(0<=record["context_id"]<N_CONTEXTS) or
        any(type(record[k]) is not int or record[k] not in (0,1)
            for k in ("setting","action","observed_y"))):
        raise ValueError("untrusted observational source record")

def validate_do(record:dict)->None:
    if (not isinstance(record,dict) or set(record)!={
         "context_id","setting","action","observed_y","probe_index"} or
        type(record["context_id"]) is not int or
        record["context_id"] not in (0,1) or
        any(type(record[k]) is not int or record[k] not in (0,1)
            for k in ("setting","action","observed_y")) or
        type(record["probe_index"]) is not int or
        not(0<=record["probe_index"]<DO_BUDGET)):
        raise ValueError("source contains nonregistered do intervention")

def validate_query(request:dict)->bool:
    return (isinstance(request,dict) and
            set(request)=={"context_id","setting","action"} and
            type(request["context_id"]) is int and
            request["context_id"] in range(2,N_CONTEXTS) and
            all(type(request[k]) is int and request[k] in (0,1)
                for k in ("setting","action")))

def key(c:int,b:int,a:int)->str:
    return f"{c}:{b}:{a}"

def likelihood(observation:int,expected:int)->float:
    return (1.0-FLIP) if observation==expected else FLIP

def evidence_log_lr(causal_expected:int,proxy_expected_0:int,
                    proxy_expected_1:int,observed_y:int)->float:
    p_causal=likelihood(observed_y,causal_expected)
    p_proxy=(1-U_ONE)*likelihood(observed_y,proxy_expected_0) + (
        U_ONE*likelihood(observed_y,proxy_expected_1))
    return math.log(p_causal)-math.log(p_proxy)

class DirectHypothesisWeights:
    def __init__(self):
        self.cells:dict[str,float]={}
        self.observed_passive=0
        self.posterior_log_odds=0.0
        self.do_count=0
        self.do_source_signatures:list[str]=[]

    def fit_passive(self,records:tuple[dict,...])->None:
        if self.observed_passive or self.cells:
            raise ValueError("cannot reuse or retune passive source")
        if not isinstance(records,tuple) or len(records)!=PASSIVE_RECORDS:
            raise ValueError("one complete original passive source required")
        for row in records:
            validate_passive(row)
            k=key(row["context_id"],row["setting"],row["action"])
            if k in self.cells:
                raise ValueError("duplicate passive source cell")
            self.cells[k]=float(row["observed_y"])
        if len(self.cells)!=PASSIVE_RECORDS:
            raise ValueError("missing passive source counterfactual table cells")
        self.observed_passive=len(records)

    def f(self,c:int,b:int,a:int)->int:
        if self.observed_passive!=PASSIVE_RECORDS:
            raise ValueError("passive source has not been learned")
        v=self.cells.get(key(c,b,a))
        if v is None:raise ValueError("unfitted passive source variable")
        return int(v>=0.5)

    def choose_probe(self,index:int)->dict:
        if type(index) is not int or not(0<=index<DO_BUDGET):
            raise ValueError("fixed active experiment index only")
        c=index%2
        candidates=[]
        for b,a in product((0,1),(0,1)):
            f0=self.f(c,b,0)
            f1=self.f(c,b,1)
            predicted=self.f(c,b,a)
            if proxy:=((1-U_ONE)*f0+U_ONE*f1):
                divergence=abs(predicted-proxy)
            else:
                divergence=abs(predicted)
            candidates.append((-divergence,b,a))
        _,b,a=min(candidates)
        return {"context_id":c,"setting":b,"action":a}

    def observe_do(self,record:dict)->None:
        validate_do(record)
        if self.observed_passive!=PASSIVE_RECORDS or record["probe_index"]!=self.do_count:
            raise ValueError("do source out of order, missing source or replayed")
        c,b,a,y=(record[k] for k in ("context_id","setting","action","observed_y"))
        self.posterior_log_odds+=evidence_log_lr(self.f(c,b,a),self.f(c,b,0),
                                                  self.f(c,b,1),y)
        self.do_source_signatures.append(sha(record))
        self.do_count+=1

    def regime(self)->str|None:
        if self.do_count!=DO_BUDGET:return None
        return "action_causal" if self.posterior_log_odds>=0 else "hidden_proxy"

    def predict(self,request:dict)->int|None:
        if not validate_query(request) or self.do_count!=DO_BUDGET:
            return None
        c,b,a=(request[k] for k in ("context_id","setting","action"))
        return self.f(c,b,a if self.posterior_log_odds>=0 else 0)

    def snapshot(self)->str:
        data={"cells":dict(sorted(self.cells.items())),
              "observed_passive":self.observed_passive,
              "posterior_log_odds":self.posterior_log_odds,
              "do_count":self.do_count,
              "do_source_signatures":list(self.do_source_signatures)}
        return canonical({"schema":SCHEMA,"data":data,"sha256":sha(data)})

    @classmethod
    def restore(cls,value:str)->"DirectHypothesisWeights":
        env=json.loads(value);data=env.get("data")
        if env.get("schema")!=SCHEMA or not isinstance(data,dict) or sha(data)!=env.get("sha256"):
            raise ValueError("numeric hypothesis memory tamper or source mismatch")
        m=cls();cells=data.get("cells",{})
        n=data.get("observed_passive")
        if (not isinstance(cells,dict) or len(cells)!=PASSIVE_RECORDS or
            type(n) is not int or n!=PASSIVE_RECORDS):
            raise ValueError("corrupt passive variable table")
        required={key(c,b,a) for c in range(N_CONTEXTS)
                  for b in (0,1) for a in (0,1)}
        if set(cells)!=required or any(type(v) is not float or v not in (0.0,1.0)
                                       for v in cells.values()):
            raise ValueError("invalid learned source weight")
        odds=data.get("posterior_log_odds");k=data.get("do_count")
        trace=data.get("do_source_signatures")
        if (type(odds) is not float or not math.isfinite(odds) or
            type(k) is not int or not(0<=k<=DO_BUDGET) or
            not isinstance(trace,list) or len(trace)!=k or
            any(not isinstance(t,str) or len(t)!=64 for t in trace)):
            raise ValueError("invalid posterior source weight or intervention receipt")
        m.cells=dict(cells);m.observed_passive=n
        m.posterior_log_odds=odds;m.do_count=k
        m.do_source_signatures=list(trace)
        return m

class IndependentSymbolicBayes:
    """Separate dictionary + separate likelihood update over identical evidence."""
    def __init__(self):
        self.observations={}
        self.log_odds=0.0
        self.trials=0

    def fit_passive(self,records:tuple[dict,...])->None:
        if self.observations:raise ValueError("independent source already consumed")
        for row in records:
            validate_passive(row)
            k=(row["context_id"],row["setting"],row["action"])
            if k in self.observations:raise ValueError("source row duplication")
            self.observations[k]=row["observed_y"]
        if len(self.observations)!=PASSIVE_RECORDS:
            raise ValueError("incomplete source")
    def observe_do(self,row:dict)->None:
        validate_do(row)
        if row["probe_index"]!=self.trials:raise ValueError("repeated do in symbolic source")
        c,b,a,y=(row[k] for k in ("context_id","setting","action","observed_y"))
        truth=self.observations
        expected_action=truth[(c,b,a)]
        p_y_if_causal=0.98 if expected_action==y else .02
        p_y_if_proxy=sum(
            prob*(.98 if truth[(c,b,u)]==y else .02)
            for u,prob in ((0,.8),(1,.2)))
        self.log_odds+=math.log(p_y_if_causal/p_y_if_proxy)
        self.trials+=1
    def regime(self):
        return None if self.trials!=DO_BUDGET else (
            "action_causal" if self.log_odds>=0 else "hidden_proxy")
    def predict(self,request:dict):
        if self.trials!=DO_BUDGET or not validate_query(request):return None
        c,b,a=(request[k] for k in ("context_id","setting","action"))
        return self.observations[(c,b,a if self.log_odds>=0 else 0)]

class ConventionalTabularBayes:
    """Actual ordinary supervised gradient learning for the passive 32-cell f.

    Competing SCMs then get an exact, equally informed conventional Bayesian
    model comparison on original do outcomes (no hidden truth labels).
    """
    def __init__(self):
        self.logits={}
        self.cells={}
        self.trials=0
        self.log_odds=0.0
        self.train_fit=0
        self.epochs=500

    def fit_passive(self,records:tuple[dict,...])->None:
        if len(records)!=PASSIVE_RECORDS:raise ValueError("ordinary source incomplete")
        ids=[]
        for row in records:
            validate_passive(row)
            k=(row["context_id"],row["setting"],row["action"])
            if k in self.logits:raise ValueError("duplicate cell in ordinary baseline")
            self.logits[k]=0.0
            ids.append((k,row["observed_y"]))
        for _ in range(self.epochs):
            for k,y in ids:
                v=self.logits[k]
                p=1.0/(1.0+math.exp(-max(-40.0,min(40.0,v))))
                self.logits[k]+=0.8*(y-p)
        self.cells={k:int(v>=0.0) for k,v in self.logits.items()}
        self.train_fit=sum(self.cells[k]==y for k,y in ids)

    def observe_do(self,record:dict)->None:
        validate_do(record)
        if record["probe_index"]!=self.trials or len(self.cells)!=PASSIVE_RECORDS:
            raise ValueError("untrained ordinary baseline or duplicate original do")
        c,b,a,y=(record[k] for k in ("context_id","setting","action","observed_y"))
        f=self.cells
        likelihood_c=(1-FLIP) if y==f[(c,b,a)] else FLIP
        likelihood_s=sum(prob*((1-FLIP) if y==f[(c,b,u)] else FLIP)
                          for u,prob in ((0,1-U_ONE),(1,U_ONE)))
        self.log_odds+=math.log(likelihood_c)-math.log(likelihood_s)
        self.trials+=1

    def regime(self):
        if self.trials!=DO_BUDGET:return None
        return "action_causal" if self.log_odds>=0 else "hidden_proxy"

    def predict(self,request:dict):
        if self.trials!=DO_BUDGET or not validate_query(request):return None
        c,b,a=(request[k] for k in ("context_id","setting","action"))
        return self.cells[(c,b,a if self.log_odds>=0 else 0)]

def original_random_probe(seed:int,trial:int)->dict:
    if type(trial) is not int or not(0<=trial<DO_BUDGET):
        raise ValueError("unregistered DO experiment")
    choices=tuple({"context_id":c,"setting":b,"action":a}
                  for c,b,a in product((0,1),(0,1),(0,1)))
    value=int.from_bytes(hashlib.sha256(
        f"WSP97/random-query/{seed}/{trial}".encode("ascii")).digest()[:8],"big")
    return dict(choices[value%len(choices)])

def passive_only_prediction(cells:dict[str,float],request:dict)->int|None:
    if not validate_query(request):return None
    c,b,a=(request[k] for k in ("context_id","setting","action"))
    return int(cells[key(c,b,a)])

def swapped_do_observation(row:dict)->dict:
    validate_do(row)
    return {**row,"observed_y":1-row["observed_y"]}
