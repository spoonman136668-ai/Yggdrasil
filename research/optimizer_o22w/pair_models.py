"""O22-W matched original-source pair value learners.

Nine ORIGINAL Ygg R1 public nine-feature LocalCell cohorts, per TRUE executed
two-action pair. Strong separate full-nine-feature ridge per pair, two heads.
No source simulator, hidden state, private map, or generated alternative outcome.
"""
from __future__ import annotations
import hashlib,json,math
from research.native.itd02.r1.native_policy import LocalCell,PublicGrid,features,canonical
from research.optimizer_o22v.delayed_cells import _solve
PAIRS=tuple(f"{i}{j}" for i in range(3) for j in range(3))
LEGAL=tuple(p for p in PAIRS if p not in ("01","10"))
SCHEMA="optimizer.o22w.real-original-two-step-pair-values.v1"

def public(s):
    if type(s) is not dict or set(s)!={"x","y","goal_x","goal_y","direction","front_blocked"}:
        raise ValueError("O22W_NO_HIDDEN_SOURCE_FIELDS")
    return features(PublicGrid(s["x"],s["y"],s["goal_x"],s["goal_y"],
                               s["direction"],s["front_blocked"]))
def target(v):
    if type(v) is not dict or set(v)!={"progress","blocked"}:
        raise ValueError("O22W_NO_FABRICATED_TARGET_FIELDS")
    p=v["progress"];b=v["blocked"]
    if type(p) not in (float,int) or not math.isfinite(p) or not -1<=p<=1 or type(b) is not bool:
        raise ValueError("O22W_INVALID_SOURCE_TARGET")
    return (float(p),float(b))
def clip(v,front=False):
    return max(0.001,min(0.999,v)) if front else max(-1.,min(1.,v))

class NativePairCells:
    SCHEMA=SCHEMA+".original-r1-LocalCell"
    def __init__(self):
        self.cells={p:[[LocalCell() for _ in range(9)] for _ in range(2)]
                    for p in PAIRS}
        self.counts={p:0 for p in PAIRS}
        self.n=0
    def predict(self,s,pair):
        x=public(s)
        if pair not in PAIRS:raise ValueError("O22W_ILLEGAL_PAIR")
        vals=[sum(c.output(v) for c,v in zip(cohort,x))
              for cohort in self.cells[pair]]
        return (clip(vals[0]),clip(.5+vals[1],True))
    def learn(self,s,pair,observed):
        x=public(s)
        y=target(observed)
        if pair not in PAIRS or self.n>=4096:raise ValueError("O22W_SOURCE_TRAIN_BUDGET")
        before=self.predict(s,pair)
        for head,(t,pred) in enumerate(zip(y,before)):
            delta=max(-1.,min(1.,t-pred))
            for c,v in zip(self.cells[pair][head],x):c.learn(v,delta)
        self.n+=1;self.counts[pair]+=1
    def checkpoint(self):
        body={"schema":self.SCHEMA,"n":self.n,"counts":self.counts,
              "cells":{p:[[[c.fast,c.slow,c.updates] for c in head]
                           for head in self.cells[p]] for p in PAIRS}}
        wire=canonical(body)
        return canonical({"body":body,"sha256":hashlib.sha256(wire).hexdigest()})
    @classmethod
    def restore(cls,raw):
        b=_verified(raw,cls.SCHEMA,150000)
        if set(b)!={"schema","n","counts","cells"} or set(b["cells"])!=set(PAIRS):
            raise ValueError("O22W_NATIVE_BAD_BODY")
        _counts(b)
        result=cls()
        for pair,cohorts in b["cells"].items():
            if type(cohorts) is not list or len(cohorts)!=2:
                raise ValueError("O22W_NATIVE_BAD_HEADS")
            result.cells[pair]=[]
            for rows in cohorts:
                if type(rows) is not list or len(rows)!=9:
                    raise ValueError("O22W_NATIVE_BAD_WIDTH")
                cohort=[]
                for x in rows:
                    if (type(x) is not list or len(x)!=3 or
                        any(type(v) not in (int,float) or not math.isfinite(v) for v in x) or
                        any(abs(v)>32 for v in x[:2]) or
                        type(x[2]) is not int or x[2]!=b["counts"][pair]):
                        raise ValueError("O22W_NATIVE_BAD_CELL")
                    cohort.append(LocalCell(x[0],x[1],x[2]))
                result.cells[pair].append(cohort)
        result.n=b["n"];result.counts=b["counts"]
        return result

class FullNineRidgePairs:
    """Independently learned matched public-feature, pair-specific ridge L2=1."""
    SCHEMA=SCHEMA+".independent-nine-public-ridge"
    def __init__(self):
        self.x=[[[0.]*9 for _ in range(9)] for _ in PAIRS]
        self.y=[[[0.]*9 for _ in range(2)] for _ in PAIRS]
        self.weights=[[[0.]*9 for _ in range(2)] for _ in PAIRS]
        self.counts={p:0 for p in PAIRS}
        self.n=0;self.fitted=False
    def learn(self,s,pair,observed):
        x=public(s);y=target(observed)
        if pair not in PAIRS or self.n>=4096 or self.fitted:
            raise ValueError("O22W_RIDGE_FROZEN")
        i=PAIRS.index(pair)
        for j in range(9):
            for k in range(9):self.x[i][j][k]+=x[j]*x[k]
            for head,t in enumerate(y):self.y[i][head][j]+=x[j]*t
        self.counts[pair]+=1;self.n+=1
    def finalize(self):
        if self.fitted or self.n==0 or any(v==0 for v in self.counts.values()):
            raise ValueError("O22W_RIDGE_MISSING_REAL_PAIR_FIT")
        for i,p in enumerate(PAIRS):
            x=[list(row) for row in self.x[i]]
            for j in range(9):x[j][j]+=1.
            for head in range(2):self.weights[i][head]=_solve(x,self.y[i][head])
        self.fitted=True
    def predict(self,s,pair):
        x=public(s)
        if not self.fitted or pair not in PAIRS:
            raise ValueError("O22W_RIDGE_NEEDS_FIT")
        w=self.weights[PAIRS.index(pair)]
        return (clip(sum(a*b for a,b in zip(x,w[0]))),
                clip(sum(a*b for a,b in zip(x,w[1])),True))
    def checkpoint(self):
        b={"schema":self.SCHEMA,"n":self.n,"counts":self.counts,
           "fitted":self.fitted,"x":self.x,"y":self.y,"weights":self.weights}
        return canonical({"body":b,"sha256":hashlib.sha256(canonical(b)).hexdigest()})
    @classmethod
    def restore(cls,raw):
        b=_verified(raw,cls.SCHEMA,350000)
        if set(b)!={"schema","n","counts","fitted","x","y","weights"} or type(b["fitted"]) is not bool:
            raise ValueError("O22W_RIDGE_BAD_BODY")
        _counts(b)
        o=cls()
        for field,shape in (("x",(9,9,9)),("y",(9,2,9)),("weights",(9,2,9))):
            arr=b[field]
            if type(arr) is not list or len(arr)!=shape[0]:
                raise ValueError("O22W_RIDGE_BAD_DIMENSIONS")
            for group in arr:
                if type(group) is not list or len(group)!=shape[1]:
                    raise ValueError("O22W_RIDGE_BAD_ROWS")
                for row in group:
                    if type(row) is not list or len(row)!=shape[2] or any(
                        type(v) not in (float,int) or not math.isfinite(v) or abs(v)>4096 for v in row):
                        raise ValueError("O22W_RIDGE_NONFINITE_WEIGHTS")
        o.x=b["x"];o.y=b["y"];o.weights=b["weights"]
        o.counts=b["counts"];o.n=b["n"];o.fitted=b["fitted"]
        return o
def _counts(b):
    if (type(b.get("n")) is not int or not 0<=b["n"]<=4096 or
        type(b.get("counts")) is not dict or set(b["counts"])!=set(PAIRS) or
        any(type(z) is not int or z<0 for z in b["counts"].values()) or
        sum(b["counts"].values())!=b["n"]):
        raise ValueError("O22W_INCONSISTENT_SOURCE_PAIR_COUNTS")
def _verified(raw,schema,cap):
    try:
        if type(raw) is not bytes or not 0<len(raw)<=cap:
            raise ValueError("O22W_COLD_OVERSIZE")
        w=json.loads(raw)
        if (type(w) is not dict or set(w)!={"body","sha256"} or
            type(w["body"]) is not dict or w["body"].get("schema")!=schema or
            hashlib.sha256(canonical(w["body"])).hexdigest()!=w["sha256"]):
            raise ValueError("O22W_COLD_HASH")
        return w["body"]
    except (ValueError,TypeError,KeyError,OverflowError) as e:
        raise ValueError("O22W_UNTRUSTED_COLD") from e

def geometric_pair(s):
    """Public geometry; optimistic no-wall two-step motor, not a learned control."""
    public(s)
    direction=s["direction"]
    dirs=((1,0),(0,1),(-1,0),(0,-1))
    best=None
    for pair in LEGAL:
        x,y=s["x"],s["y"];d=direction
        for act in pair:
            if act==0:d=(d-1)%4
            elif act==1:d=(d+1)%4
            else:
                dx,dy=dirs[d];x+=dx;y+=dy
        progress=(abs(s["goal_x"]-s["x"])+abs(s["goal_y"]-s["y"])
                  -abs(s["goal_x"]-x)-abs(s["goal_y"]-y))/2.
        candidate=(progress,pair)
        if best is None or candidate[0]>best[0]:
            best=candidate
    return best[1]

def select(model,s,allowed=LEGAL):
    return max(allowed,key=lambda p:(model.predict(s,p)[0],-int(p)))
