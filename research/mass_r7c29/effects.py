"""C29: bounded original R1-cell public successor predictor vs matched temporal Beta.

Consumes only already-authenticated C28 public FIT action events; NO original
MiniGrid environment import/reset/step; no unchosen-action labels or new DEV.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
from pathlib import Path

from research.native.itd02.r1.native_policy import PublicGrid, LocalCell, features, canonical

P=json.loads((Path(__file__).resolve().parent/"PREREG.json").read_text())
ACTIONS=(0,1,2)
SCHEMA="itd02.c29.fit-only-prediction-v1"


def check_probability(p):
    if not isinstance(p,(int,float)) or not math.isfinite(p) or not 0<p<1:
        raise ValueError("NONFINITE_OR_DEGENERATE_PREDICTION")
    return p


def view(frame):
    if type(frame) is not dict or set(frame)!={"x","y","direction","goal_x","goal_y","front_blocked"}:
        raise ValueError("SOURCE_PUBLIC_INPUT_EXTRA_OR_MISSING")
    s=PublicGrid(**frame)
    features(s)
    return s


def data_event(e):
    if type(e) is not dict or set(e)!={"family","seed","step","before","chosen_action",
          "information_turn","returned_after","returned_reward","terminated","truncated"}:
        raise ValueError("INVALID_ORIGINAL_SELECTED_EVENT")
    a=e["chosen_action"]
    if type(a) is not int or a not in ACTIONS or type(e["step"]) is not int or e["step"]<0:
        raise ValueError("INVALID_ORIGINAL_SELECTED_ACTION_OR_TIME")
    b=view(e["before"]); n=view(e["returned_after"])
    if type(e["returned_reward"]) not in (int,float) or not math.isfinite(e["returned_reward"]):
        raise ValueError("INVALID_SOURCE_REWARD")
    if type(e["information_turn"]) is not bool or type(e["terminated"]) is not bool or type(e["truncated"]) is not bool:
        raise ValueError("INVALID_SOURCE_RETURN_FLAGS")
    return b,a,int(n.front_blocked)


def sigmoid(v):
    return 1/(1+math.exp(-max(-20,min(20,v))))


class NativeCellEffect:
    """New narrow original-Ygg-R1 LocalCell offspring, not original R3 policy."""
    def __init__(self):
        self.cells={str(a):[LocalCell() for _ in range(9)] for a in ACTIONS}
        self.updates=0
    def predict(self,s,a):
        if type(a) is not int or a not in ACTIONS:
            raise ValueError("ILLEGAL_ACTION")
        phi=features(s)
        logits=sum(c.output(x) for c,x in zip(self.cells[str(a)],phi))
        return check_probability(sigmoid(logits))
    def observe(self,s,a,target,enabled=True):
        if type(enabled) is not bool or type(target) is not int or target not in (0,1):
            raise ValueError("ILLEGAL_PUBLIC_OUTCOME")
        if not enabled: return
        pred=self.predict(s,a)
        error=target-pred
        phi=features(s)
        for cell,x in zip(self.cells[str(a)],phi):
            cell.learn(x,error)
        self.updates+=1
    def snapshot(self):
        return {"kind":"native-original-r1-local-cells","updates":self.updates,
             "cells":{a:[{"fast":c.fast,"slow":c.slow,"updates":c.updates} for c in cohort]
                      for a,cohort in self.cells.items()}}
    @classmethod
    def from_snapshot(cls,raw):
        if type(raw) is not dict or set(raw)!={"kind","updates","cells"} or raw["kind"]!="native-original-r1-local-cells":
            raise ValueError("BAD_NATIVE_CELL_SNAPSHOT")
        if type(raw["updates"]) is not int or not 0<=raw["updates"]<=1000000 or type(raw["cells"]) is not dict or set(raw["cells"])!={"0","1","2"}:
            raise ValueError("BAD_NATIVE_COUNTERS")
        m=cls()
        for a,cohort in raw["cells"].items():
            if type(cohort) is not list or len(cohort)!=9:raise ValueError("BAD_CELL_COUNT")
            cells=[]
            for c in cohort:
                if type(c) is not dict or set(c)!={"fast","slow","updates"}:raise ValueError("BAD_CELL_RECORD")
                if type(c["updates"]) is not int or not 0<=c["updates"]<=m.updates:
                    raise ValueError("BAD_CELL_UPDATES")
                for n in ("fast","slow"):
                    if type(c[n]) not in (float,int) or not math.isfinite(c[n]) or abs(c[n])>32:
                        raise ValueError("BAD_CELL_VALUE")
                cells.append(LocalCell(float(c["fast"]),float(c["slow"]),c["updates"]))
            m.cells[a]=cells
        m.updates=raw["updates"]
        return m


class ConventionalBeta:
    """Independent matched-public selected-action temporal Bayes table.

    Each cue has a full lifetime posterior and decayed recent posterior.
    A time-only ablation never receives the selected-action identity.
    """
    def __init__(self,action_aware=True):
        if type(action_aware) is not bool:raise ValueError("INVALID_CONTROL")
        self.action_aware=action_aware
        self.stats={}
        self.updates=0
    def key(self,s,a):
        features(s)
        if type(a) is not int or a not in ACTIONS:raise ValueError("ILLEGAL_ACTION")
        # Matching source-public position/heading/sensor, not private source family.
        return ",".join(map(str,(a if self.action_aware else -1,s.direction,int(s.front_blocked))))
    def predict(self,s,a):
        key=self.key(s,a)
        if key not in self.stats:return 0.5
        yes,total,dy,dt,last=self.stats[key]
        return check_probability(.15*(yes+1)/(total+2)+.85*(dy+1)/(dt+2))
    def observe(self,s,a,target,enabled=True):
        if type(enabled) is not bool or type(target) is not int or target not in (0,1):
            raise ValueError("ILLEGAL_PUBLIC_OUTCOME")
        if not enabled:return
        key=self.key(s,a)
        self.updates+=1
        yes,total,dy,dt,last=self.stats.get(key,[0,0,0.,0.,self.updates-1])
        if last>=self.updates:raise ValueError("DUPLICATE_TEMPORAL_UPDATE")
        decay=.97**(self.updates-last)
        self.stats[key]=[yes+target,total+1,dy*decay+target,dt*decay+1.,self.updates]
    def snapshot(self):
        return {"kind":"conventional-temporal-beta","action_aware":self.action_aware,
            "updates":self.updates,"stats":self.stats}
    @classmethod
    def from_snapshot(cls,raw):
        if type(raw) is not dict or set(raw)!={"kind","action_aware","updates","stats"} or raw["kind"]!="conventional-temporal-beta":
            raise ValueError("BAD_BETA_SNAPSHOT")
        if type(raw["action_aware"]) is not bool or type(raw["updates"]) is not int or not 0<=raw["updates"]<=1000000 or type(raw["stats"]) is not dict or len(raw["stats"])>100:
            raise ValueError("BAD_BETA_COUNTERS")
        m=cls(raw["action_aware"]);m.updates=raw["updates"]
        for k,v in raw["stats"].items():
            if type(k) is not str or len(k)>16 or type(v) is not list or len(v)!=5:
                raise ValueError("BAD_TEMPORAL_CUE")
            y,n,dy,dt,last=v
            if (type(y) is not int or type(n) is not int or type(last) is not int or
                not 0<=y<=n<=m.updates or not 1<=last<=m.updates or
                type(dy) not in (int,float) or type(dt) not in (int,float) or
                not math.isfinite(dy) or not math.isfinite(dt) or not 0<=dy<=dt<=n):
                raise ValueError("BAD_TEMPORAL_COUNTS")
            parts=k.split(",")
            if (len(parts)!=3 or any(not z.lstrip("-").isdigit() for z in parts) or
                int(parts[0]) not in ((-1,) if not m.action_aware else ACTIONS) or
                int(parts[1]) not in range(4) or int(parts[2]) not in (0,1)):
                raise ValueError("BAD_PUBLIC_KEY")
        m.stats=copy.deepcopy(raw["stats"])
        return m


def sealed(model):
    payload={"schema":SCHEMA,"model":model.snapshot()}
    raw=canonical(payload)
    if len(raw)>262144:raise ValueError("TOO_LARGE_CHECKPOINT")
    return canonical({"payload":payload,"sha256":hashlib.sha256(raw).hexdigest()})


def unseal(blob):
    if type(blob) is not bytes or not 0<len(blob)<=262144:
        raise ValueError("INVALID_CHECKPOINT_INPUT")
    try:
        wire=json.loads(blob)
        if type(wire) is not dict or set(wire)!={"payload","sha256"}:
            raise ValueError("BAD_SEALED_WIRE")
        payload=wire["payload"]
        if type(payload) is not dict or set(payload)!={"schema","model"} or payload["schema"]!=SCHEMA:
            raise ValueError("BAD_SEALED_MODEL")
        if hashlib.sha256(canonical(payload)).hexdigest()!=wire["sha256"]:
            raise ValueError("TAMPERED_CELL_OR_CONVENTIONAL_STATE")
        raw=payload["model"]
        if raw.get("kind")=="native-original-r1-local-cells":
            return NativeCellEffect.from_snapshot(raw)
        if raw.get("kind")=="conventional-temporal-beta":
            return ConventionalBeta.from_snapshot(raw)
    except (TypeError,KeyError,OverflowError,AttributeError,ValueError) as e:
        raise ValueError("CORRUPT_STATE_OR_SIGNATURE") from e
    raise ValueError("UNKNOWN_LEARNER_KIND")


def exploratory_proxy(m,s,a,cost=.8):
    """A pre-registered proxy *query*, NOT an identified information-value policy."""
    if type(cost) not in (float,int) or not 0<cost<1:
        raise ValueError("INVALID_PROXY_COST")
    p=m.predict(s,a)
    # Conditional public next-front surprise uncertainty; all costs fixed.
    return bool(4*p*(1-p)>cost)


def prediction_metrics(model,events):
    """Score only FIT events, before updating any event target."""
    errors=[]
    for e in events:
        s,a,y=data_event(e)
        p=model.predict(s,a)
        errors.append((p-y)**2)
    return {"n":len(errors),"brier":round(sum(errors)/len(errors),9) if errors else None}


def event_split(data):
    ordered=P["source_fit_split"]
    left={(fam,seed) for fam,seeds in ordered["learn"].items() for seed in seeds}
    test={(fam,seed) for fam,seeds in ordered["internal_fit_check"].items() for seed in seeds}
    if left&test:raise ValueError("FIT_DATA_SPLIT_COLLISION")
    train=[e for e in data if (e["family"],e["seed"]) in left]
    check=[e for e in data if (e["family"],e["seed"]) in test]
    if len(train)+len(check)!=len(data) or not train or not check:
        raise ValueError("FIT_ROLE_SPLIT_MISSING_OR_EXTRA_EPISODES")
    return train,check


def make_arms():
    return {"native":NativeCellEffect(),"conventional":ConventionalBeta(),
            "time_only":ConventionalBeta(False),"shuffled_action":NativeCellEffect(),
            "frozen":NativeCellEffect()}


def train(arms,events):
    for e in events:
        s,a,y=data_event(e)
        for name,m in arms.items():
            if name=="shuffled_action":m.observe(s,(a+1)%3,y)
            elif name=="frozen":pass
            else:m.observe(s,a,y)


def query_impact(arms,queries):
    out={}
    for name,m in arms.items():
        outcomes=[{"p":round(m.predict(data_event(e)[0],data_event(e)[1]),8),
             "would_probe":exploratory_proxy(m,data_event(e)[0],data_event(e)[1])} for e in queries]
        out[name]=outcomes
    return out
