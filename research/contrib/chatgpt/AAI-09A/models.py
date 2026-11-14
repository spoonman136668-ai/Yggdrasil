"""AAI-09A frozen native-data/non-token ASSOCIATION experiment, pure Python.

This independent EXTERNAL research mechanism is not Yggdrasil native cognition.
No simulator, network, API or science cohorts in this module.
Prereg was committed before model source at d9e9f3f11d04cdcf99c5e5b1e0c7a5008e0c2026.
"""
import collections
import json
import math

CAPACITY=2
SCRATCH_BLOCK=2
LOG_MARGIN=math.log(4)
CUSUM_DELTA=.2
BOCPD_HAZARD=1/12
LOGISTIC_EPOCHS=1200

class Beta:
    def __init__(self,yes=1,no=1):
        self.yes=int(yes)
        self.no=int(no)
        assert self.yes>=1 and self.no>=1
    def prob(self):
        return self.yes/(self.yes+self.no)
    def add(self,observations):
        for v in observations:
            if bool(v):
                self.yes+=1
            else:
                self.no+=1
    def state(self):
        return [self.yes,self.no]
    @classmethod
    def load(cls,data):
        return cls(data[0],data[1])

class ProtectedBank:
    def __init__(self,capacity=CAPACITY):
        assert capacity in (1,2)
        self.capacity=capacity
        self.cores=[{"id":0,"beta":Beta()}]
        self.active_id=0
        self.next_id=1
        self.scratch=[]
        self.retrievals=0
    def active(self):
        return next(core for core in self.cores if core["id"]==self.active_id)
    @staticmethod
    def score(core,block):
        p=max(1e-4,min(1-1e-4,core["beta"].prob()))
        return sum(math.log(p if v else 1-p) for v in block)
    def learn(self,event):
        self.scratch.append(bool(event))
        if len(self.scratch)<SCRATCH_BLOCK:
            return
        assert len(self.scratch)==SCRATCH_BLOCK
        batch=self.scratch
        self.scratch=[]
        active=self.active()
        current=self.score(active,batch)
        alternatives=[(self.score(core,batch),core["id"]) for core in self.cores if core["id"]!=self.active_id]
        if alternatives:
            score,core_id=max(alternatives)
            if score>=current+LOG_MARGIN:
                self.active_id=core_id
                self.active()["beta"].add(batch)
                self.retrievals+=1
                return
        if self.capacity>len(self.cores) and SCRATCH_BLOCK*math.log(.5)>=current+LOG_MARGIN:
            fresh={"id":self.next_id,"beta":Beta()}
            self.next_id+=1
            self.cores.append(fresh)
            self.active_id=fresh["id"]
            fresh["beta"].add(batch)
            return
        self.active()["beta"].add(batch)
    def prediction(self):
        return self.active()["beta"].prob()
    def choose(self):
        return 2 if self.prediction()>=.5 else 3
    def state(self):
        return {"capacity":self.capacity,
                "cores":[{"id":core["id"],"counts":core["beta"].state()} for core in self.cores],
                "active_id":self.active_id,
                "next_id":self.next_id,
                "scratch":list(self.scratch),
                "retrievals":self.retrievals}
    @classmethod
    def load(cls,data):
        x=cls(int(data["capacity"]))
        x.cores=[{"id":int(item["id"]),"beta":Beta.load(item["counts"])} for item in data["cores"]]
        x.active_id=int(data["active_id"])
        x.next_id=int(data["next_id"])
        x.scratch=[bool(y) for y in data["scratch"]]
        x.retrievals=int(data["retrievals"])
        assert len(x.cores)<=x.capacity
        assert x.active_id in [item["id"] for item in x.cores]
        return x

class Recent:
    def __init__(self,width):
        self.width=width
        self.data=collections.deque(maxlen=width)
    def learn(self,event):
        self.data.append(bool(event))
    def prediction(self):
        return (1+sum(self.data))/(2+len(self.data))
    def choose(self):
        return 2 if self.prediction()>=.5 else 3
    def state(self):
        return {"width":self.width,"data":list(self.data)}
    @classmethod
    def load(cls,data):
        x=cls(int(data["width"]))
        x.data=collections.deque(map(bool,data["data"]),maxlen=x.width)
        return x

class Stationary:
    def __init__(self):
        self.beta=Beta()
    def learn(self,event):
        self.beta.add([event])
    def prediction(self):
        return self.beta.prob()
    def choose(self):
        return 2 if self.prediction()>=.5 else 3
    def state(self):
        return self.beta.state()
    @classmethod
    def load(cls,data):
        x=cls()
        x.beta=Beta.load(data)
        return x

class BOCPD:
    """Standard Beta-Bernoulli exact online run-length posterior with fixed hazard.

    Each row: [weight, yes, no]. A transition begins with Beta(1,1), and
    applies the current observation to the fresh run length as well.
    Every observation is shared across all controls; no A/B labels.
    """
    def __init__(self):
        self.rows=[[1.0,1,1]]
    def learn(self,event):
        observed=bool(event)
        growth=[]
        restart=0.0
        for weight,yes,no in self.rows:
            p=(yes if observed else no)/(yes+no)
            growth.append([weight*(1-BOCPD_HAZARD)*p,
                           yes+int(observed),no+int(not observed)])
            restart+=weight*BOCPD_HAZARD*.5
        restarted=[restart,1+int(observed),1+int(not observed)]
        rows=[restarted]+growth
        mass=sum(row[0] for row in rows)
        assert mass>0 and math.isfinite(mass)
        self.rows=[[weight/mass,yes,no] for weight,yes,no in rows]
    def prediction(self):
        return sum(weight*yes/(yes+no) for weight,yes,no in self.rows)
    def choose(self):
        return 2 if self.prediction()>=.5 else 3
    def state(self):
        return {"rows":self.rows}
    @classmethod
    def load(cls,st):
        x=cls()
        x.rows=[[float(w),int(y),int(n)] for w,y,n in st["rows"]]
        return x

class CUSUM:
    """Fixed two-timescale conventional 4/16-window drift comparator."""
    def __init__(self):
        self.fast=Recent(4)
        self.slow=Recent(16)
    def learn(self,event):
        self.fast.learn(event)
        self.slow.learn(event)
    def prediction(self):
        a,b=self.fast.prediction(),self.slow.prediction()
        return a if abs(a-b)>=CUSUM_DELTA else b
    def choose(self):
        return 2 if self.prediction()>=.5 else 3
    def state(self):
        return {"fast":self.fast.state(),"slow":self.slow.state()}
    @classmethod
    def load(cls,data):
        x=cls()
        x.fast=Recent.load(data["fast"])
        x.slow=Recent.load(data["slow"])
        return x

class Logistic:
    """Standard fully fitted 1200-epoch intercept-only logistic."""
    def __init__(self):
        self.history=[]
        self.weight=0.0
        self.dirty=True
    def learn(self,event):
        self.history.append(bool(event))
        self.dirty=True
    def fit(self):
        if not self.history or not self.dirty:
            return
        target=sum(self.history)/len(self.history)
        for _ in range(LOGISTIC_EPOCHS):
            w=max(-40,min(40,self.weight))
            p=1/(1+math.exp(-w))
            self.weight-=.4*(p-target)
        self.dirty=False
    def prediction(self):
        self.fit()
        return 1/(1+math.exp(-max(-40,min(40,self.weight))))
    def choose(self):
        return 2 if self.prediction()>=.5 else 3
    def state(self):
        return {"history":self.history,"weight":self.weight,"dirty":self.dirty}
    @classmethod
    def load(cls,data):
        x=cls()
        x.history=list(map(bool,data["history"]))
        x.weight=float(data["weight"])
        x.dirty=bool(data["dirty"])
        return x

class AlwaysRight:
    def learn(self,event):
        return
    def prediction(self):
        return 1.0
    def choose(self):
        return 2
    def state(self):
        return {}
    @classmethod
    def load(cls,data):
        return cls()

class KnownLawOracle:
    """PRIVILEGED oracle, no matched-learner comparability.

    Receives experimenter-provided A/B probabilities and prior .2.
    Its prehistory is deliberately ignored: q=.2 at B checkpoint.
    Only the challenge observations update q.
    """
    def __init__(self,p_a,p_b,prior=.2):
        self.p_a=float(p_a)
        self.p_b=float(p_b)
        self.q=float(prior)
    def learn(self,event):
        observed=bool(event)
        a=self.q*(self.p_a if observed else 1-self.p_a)
        b=(1-self.q)*(self.p_b if observed else 1-self.p_b)
        self.q=a/(a+b)
    def prediction(self):
        return self.q*self.p_a+(1-self.q)*self.p_b
    def choose(self):
        return 2 if self.prediction()>=.5 else 3
    def state(self):
        return {"p_a":self.p_a,"p_b":self.p_b,"q":self.q}
    @classmethod
    def load(cls,data):
        return cls(data["p_a"],data["p_b"],data["q"])

NAMES=("candidate","one_slot","recent2","recent4","recent8","recent16",
       "stationary","bocpd","cusum","logistic","always_right")
MATCHED=("recent2","recent4","recent8","recent16","stationary","bocpd","cusum","logistic")
NEGATIVE=("always_right","one_slot")

def create(name):
    if name=="candidate":
        return ProtectedBank(2)
    if name=="one_slot":
        return ProtectedBank(1)
    if name.startswith("recent"):
        return Recent(int(name.removeprefix("recent")))
    return {"stationary":Stationary,"bocpd":BOCPD,"cusum":CUSUM,
            "logistic":Logistic,"always_right":AlwaysRight}[name]()

def restore(name,state):
    if name in ("candidate","one_slot"):
        return ProtectedBank.load(state)
    if name.startswith("recent"):
        return Recent.load(state)
    return {"stationary":Stationary,"bocpd":BOCPD,"cusum":CUSUM,
            "logistic":Logistic,"always_right":AlwaysRight}[name].load(state)

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"))

def checkpoint(models):
    return {name:canonical(model.state()) for name,model in models.items()}

def cold_restore(saved):
    return {name:restore(name,json.loads(serialized))
            for name,serialized in saved.items()}

def shared_observation(models,outcome):
    for model in models.values():
        model.learn(bool(outcome))

def origin_marker(bank):
    active=bank.active()
    return {"id":active["id"],"counts":active["beta"].state()}

def preserved_original(bank,marker):
    return any(item["id"]==marker["id"] and item["beta"].state()==marker["counts"]
               for item in bank.cores)

def recalled_original(bank,marker,preserved_at_B):
    return preserved_at_B and bank.active_id==marker["id"]
