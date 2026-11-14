"""AAI-08B exact frozen AAI-08A regime-cache mechanism and conventional controls.

Pure Python. This is not a new intelligence substrate. No science seeds here.
Original source: Yggdrasil AAI-08A evaluate.py blob a372635b843e285d2b37f5639b73ff44fd2fc0b7.
"""
import collections
import json
import math

BLOCK = 5
THRESHOLD = math.log(3.)
LOGISTIC_EPOCHS = 1200

class Beta:
    def __init__(self):
        self.yes = 1
        self.no = 1
    def add(self, flags):
        for flag in flags:
            if flag:
                self.yes += 1
            else:
                self.no += 1
    def prob(self):
        return self.yes / (self.yes + self.no)
    def state(self):
        return [self.yes, self.no]
    @classmethod
    def from_state(cls, s):
        x = cls()
        x.yes, x.no = map(int, s)
        return x

class RegimeCache:
    """EXACT AAI-08A RegimeCache update/decision logic, unchanged."""
    def __init__(self, capacity=2):
        self.capacity = capacity
        self.slots = [Beta()]
        self.active = 0
        self.pending = []
    def learn(self, event):
        self.pending.append(bool(event))
        if len(self.pending) < BLOCK:
            return
        batch = self.pending
        self.pending = []
        def score(slot):
            p = max(.0001, min(.9999, slot.prob()))
            return sum(math.log(p) if y else math.log(1-p) for y in batch)
        active_score = score(self.slots[self.active])
        scores = [score(m) for m in self.slots]
        alt = max(range(len(scores)), key=lambda i: scores[i])
        if alt != self.active and scores[alt] > active_score + THRESHOLD:
            self.active = alt
            self.slots[self.active].add(batch)
        elif len(self.slots) < self.capacity and BLOCK * math.log(.5) > active_score + THRESHOLD:
            new = Beta()
            new.add(batch)
            self.slots.append(new)
            self.active = len(self.slots)-1
        elif self.capacity == 1 and BLOCK * math.log(.5) > active_score + THRESHOLD:
            new = Beta()
            new.add(batch)
            self.slots = [new]
            self.active = 0
        else:
            self.slots[self.active].add(batch)
    def prob(self):
        return self.slots[self.active].prob()
    def choose(self):
        return 2 if self.prob() >= .5 else 3
    def state(self):
        return {"capacity":self.capacity,"active":self.active,
                "slots":[x.state() for x in self.slots],
                "pending":self.pending}
    @classmethod
    def from_state(cls, state):
        x = cls(state["capacity"])
        x.slots = [Beta.from_state(s) for s in state["slots"]]
        x.active = int(state["active"])
        x.pending = list(state["pending"])
        return x

class Recent:
    def __init__(self, width=8):
        self.window = collections.deque(maxlen=width)
    def learn(self, flag):
        self.window.append(bool(flag))
    def choose(self):
        p = (1 + sum(self.window)) / (2 + len(self.window))
        return 2 if p >= .5 else 3
    def state(self):
        return {"width":self.window.maxlen,"window":list(self.window)}
    @classmethod
    def from_state(cls, state):
        x = cls(int(state["width"]))
        x.window = collections.deque(state["window"],maxlen=x.window.maxlen)
        return x

class Stationary:
    def __init__(self):
        self.slot = Beta()
    def learn(self, flag):
        self.slot.add([flag])
    def choose(self):
        return 2 if self.slot.prob() >= .5 else 3
    def state(self):
        return self.slot.state()
    @classmethod
    def from_state(cls, st):
        x=cls()
        x.slot=Beta.from_state(st)
        return x

class Logistic:
    """Unchanged AAI-08A intercept-only 1200-epoch full-batch logistic."""
    def __init__(self):
        self.history = []
        self.weight = 0.
        self.dirty = True
    def learn(self, flag):
        self.history.append(bool(flag))
        self.dirty = True
    def fit(self):
        if not self.dirty:
            return
        mean = sum(self.history) / len(self.history)
        for _ in range(LOGISTIC_EPOCHS):
            value = max(-40., min(40., self.weight))
            p = 1 / (1+math.exp(-value))
            self.weight -= .4 * (p-mean)
        self.dirty = False
    def choose(self):
        self.fit()
        return 2 if self.weight >= 0 else 3
    def state(self):
        return {"history":self.history, "weight":self.weight, "dirty":self.dirty}
    @classmethod
    def from_state(cls, st):
        x=cls()
        x.history=list(st["history"])
        x.weight=float(st["weight"])
        x.dirty=bool(st["dirty"])
        return x

class KnownLawBayes:
    """Privileged experimenter-likelihood oracle, excluded from matched comparisons."""
    def __init__(self, p_a=.72, p_b=.18):
        self.q=.5
        self.p_a=p_a
        self.p_b=p_b
    def learn(self, forward):
        prior=.95*self.q+.05*(1-self.q)
        a=prior*(self.p_a if forward else 1-self.p_a)
        b=(1-prior)*(self.p_b if forward else 1-self.p_b)
        self.q=a/(a+b)
    def choose(self):
        return 2 if self.q*self.p_a+(1-self.q)*self.p_b>=.5 else 3
    def state(self):
        return {"q":self.q,"p_a":self.p_a,"p_b":self.p_b}
    @classmethod
    def from_state(cls,st):
        x=cls(st["p_a"],st["p_b"])
        x.q=float(st["q"])
        return x

class AlwaysRight:
    def learn(self, flag):
        pass
    def choose(self):
        return 2
    def state(self):
        return 0
    @classmethod
    def from_state(cls,st):
        return cls()

NAMES=("candidate","one_slot","recent4","recent8","recent16",
       "stationary","logistic","oracle","always_right")
MATCHED=("recent4","recent8","recent16","stationary","logistic")

def create(name,p_a=.72,p_b=.18):
    if name=="candidate":
        return RegimeCache(2)
    if name=="one_slot":
        return RegimeCache(1)
    if name=="recent4":
        return Recent(4)
    if name=="recent8":
        return Recent(8)
    if name=="recent16":
        return Recent(16)
    if name=="stationary":
        return Stationary()
    if name=="logistic":
        return Logistic()
    if name=="oracle":
        return KnownLawBayes(p_a,p_b)
    if name=="always_right":
        return AlwaysRight()
    raise ValueError(name)

def serialize(model):
    return json.dumps(model.state(),sort_keys=True,separators=(",",":"))

def clone(name,snapshot):
    payload=json.loads(snapshot)
    if name in ("candidate","one_slot"):
        return RegimeCache.from_state(payload)
    if name.startswith("recent"):
        return Recent.from_state(payload)
    if name=="stationary":
        return Stationary.from_state(payload)
    if name=="logistic":
        return Logistic.from_state(payload)
    if name=="oracle":
        return KnownLawBayes.from_state(payload)
    if name=="always_right":
        return AlwaysRight.from_state(payload)
    raise ValueError(name)

def snapshot(models):
    return {name:serialize(model) for name,model in models.items()}

def cloned(snapshot_map):
    return {name:clone(name,s) for name,s in snapshot_map.items()}

def shared_update(models,flag):
    for m in models.values():
        m.learn(bool(flag))

def a_origin_marker(model):
    """Only evaluator reads these after training; never send it to a learner."""
    return {"index":model.active,"counts":list(model.slots[model.active].state())}

def intact_retrieval(model,origin):
    return (
        len(model.slots)>=2
        and model.active==origin["index"]
        and list(model.slots[origin["index"]].state())==origin["counts"]
    )
