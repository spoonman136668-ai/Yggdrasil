"""AAI-11P strong same-information conventional baselines and a shared do-planner.

No privileged causal simulator equation, regime label, oracle action, or
counterfactual can enter a control. All learners receive public records only.
"""
from __future__ import annotations
import itertools
import json
import math
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import world

METHODS=("tabular_all","tabular_recent16","knn_all","knn_recent32",
         "symbolic_pair_recent16","symbolic_pair_all",
         "id3_depth4_all","logistic_triple")
DIAGNOSTIC="reactive"
ALL=(*METHODS,DIAGNOSTIC)
MONOMIALS=tuple(comb for degree in range(4)
                for comb in itertools.combinations(range(6),degree))
assert len(MONOMIALS)==42
PAIR_GRAMMAR=tuple((op,i,j) for op in ("xor","and","or")
                   for i,j in itertools.combinations(range(6),2))
assert len(PAIR_GRAMMAR)==45


def canonical(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)


def features(x):
    x=world.bits(x,6)
    return tuple(float(math.prod(x[i] for i in term)) for term in MONOMIALS)


def pair_pattern(h,x):
    op,i,j=h
    a,b=x[i],x[j]
    if op=="xor":return a^b
    if op=="and":return a&b
    if op=="or":return a|b
    raise ValueError("bad public grammar")


def expected(probs,goal,steps):
    return sum(p if g else (1-p) for p,g in zip(probs,goal))-world.COST*steps


def plan(model,row):
    """Same actual known current reward and predicted 0..2 do-step futures."""
    world.visible(row)
    x=tuple(row["x"])
    goal=tuple(row["goal"])
    spent=row["actions_taken"]
    if spent>=2:return None
    best=float(row["reward"])
    selected=None
    for first in world.ACTIONS:
        x1=world.setbit(x,first)
        v=expected(model.predict(x1),goal,spent+1)
        if v>best+1e-10:
            selected,best=first,v
        if spent==0:
            for second in world.ACTIONS:
                x2=world.setbit(x1,second)
                v2=expected(model.predict(x2),goal,2)
                if v2>best+1e-10:
                    selected,best=first,v2
    return selected


def _entropy(rows,out):
    n=len(rows)
    if not n:return 0.0
    p=sum(m[out] for _,m in rows)/n
    if p in (0.,1.):return 0.0
    return -p*math.log(p)-(1-p)*math.log(1-p)


def _leaf(rows,out):
    return (1+sum(m[out] for _,m in rows))/(len(rows)+2)


def _id3(rows,out,depth,indices):
    if not rows or not indices or depth==0 or _entropy(rows,out)<1e-9:
        return _leaf(rows,out)
    parent=_entropy(rows,out)
    winner=-1
    best_gain=0.0
    chosen=None
    for i in indices:
        l=[r for r in rows if r[0][i]==0]
        r=[r for r in rows if r[0][i]==1]
        if not l or not r:continue
        gain=parent-(len(l)*_entropy(l,out)+len(r)*_entropy(r,out))/len(rows)
        if gain>best_gain+1e-12:
            winner,best_gain,chosen=i,gain,(l,r)
    if winner<0:
        return _leaf(rows,out)
    remaining=tuple(i for i in indices if i!=winner)
    return (winner,_id3(chosen[0],out,depth-1,remaining),
            _id3(chosen[1],out,depth-1,remaining))


def _tree_eval(tree,x):
    if type(tree) is float:
        return tree
    bit,left,right=tree
    return _tree_eval(right if x[bit] else left,x)


class Control:
    def __init__(self,name):
        if name not in ALL:raise ValueError("unknown control")
        self.name=name
        self.rows=[]
        self.weights=[[0.]*len(MONOMIALS) for _ in range(3)] if name=="logistic_triple" else None
        self.trained=False
        self._invalidate()

    def _invalidate(self):
        self._prediction_cache={}
        self._tree=None
        self._pair_posterior=None

    def observe(self,row):
        """Only public actual observations can update a conventional learner."""
        x,m=world.visible(row)
        if self.name==DIAGNOSTIC:return
        self.rows.append((x,m))
        limit={"tabular_recent16":16,"knn_recent32":32,
               "symbolic_pair_recent16":16}.get(self.name)
        if limit is not None:
            self.rows=self.rows[-limit:]
        if self.name=="logistic_triple" and self.trained:
            fs=features(x)
            # Ordinary online SGD only after full-batch fitting at a checkpoint.
            for _ in range(8):
                for o in range(3):
                    pred=self._sigmoid(sum(a*b for a,b in zip(self.weights[o],fs)))
                    error=pred-m[o]
                    self.weights[o]=[
                        round(w-.15*(error*f+(.01*w if k else 0)),12)
                        for k,(w,f) in enumerate(zip(self.weights[o],fs))
                    ]
        self._invalidate()

    @staticmethod
    def _sigmoid(z):
        return 1/(1+math.exp(-max(-25.,min(25.,z))))

    def fit_checkpoint(self):
        """Fully batch-fit logistic on ALL permitted public rows, no external data."""
        if self.name!="logistic_triple":
            return
        if not self.rows:raise ValueError("cannot fit empty control")
        weights=self.weights
        feats=[(features(x),m) for x,m in self.rows]
        n=len(feats)
        for _ in range(160):
            gradients=[[0.]*len(MONOMIALS) for _ in range(3)]
            for fs,m in feats:
                for o in range(3):
                    err=self._sigmoid(sum(a*b for a,b in zip(weights[o],fs)))-m[o]
                    for i in range(len(fs)):
                        gradients[o][i]+=err*fs[i]
            for o in range(3):
                for i in range(len(MONOMIALS)):
                    w=weights[o][i]
                    weights[o][i]=round(w-.15*(gradients[o][i]/n+
                                              (.01*w if i else 0)),12)
        self.trained=True
        self._invalidate()

    def _prob_tabular(self,x):
        matching=[m for y,m in self.rows if y==x]
        return tuple((1+sum(m[o] for m in matching))/(2+len(matching))
                     for o in range(3))

    def _prob_knn(self,x):
        ordered=sorted(enumerate(self.rows),
                       key=lambda t:(sum(a!=b for a,b in zip(x,t[1][0])),-t[0]))
        selected=[v[1][1] for v in ordered[:3]]
        return tuple((1+sum(m[o] for m in selected))/(2+len(selected))
                     for o in range(3))

    def _prob_pair(self,x):
        if self._pair_posterior is None:
            post=[]
            for out in range(3):
                logs=[0.]*len(PAIR_GRAMMAR)
                for old_x,m in self.rows:
                    for idx,h in enumerate(PAIR_GRAMMAR):
                        logs[idx]+=(math.log(.9) if pair_pattern(h,old_x)==m[out]
                                     else math.log(.1))
                peak=max(logs)
                norms=[math.exp(v-peak) for v in logs]
                z=sum(norms)
                post.append([q/z for q in norms])
            self._pair_posterior=tuple(post)
        return tuple(round(sum(w*pair_pattern(h,x)
                               for h,w in zip(PAIR_GRAMMAR,self._pair_posterior[o])),12)
                     for o in range(3))

    def _prob_tree(self,x):
        if self._tree is None:
            self._tree=tuple(_id3(self.rows,o,4,tuple(range(6))) for o in range(3))
        return tuple(_tree_eval(t,x) for t in self._tree)

    def _prob_logistic(self,x):
        fs=features(x)
        return tuple(round(self._sigmoid(sum(w*f for w,f in zip(row,fs))),12)
                     for row in self.weights)

    def predict(self,x):
        x=world.bits(x,6)
        if x not in self._prediction_cache:
            if self.name.startswith("tabular"):
                out=self._prob_tabular(x)
            elif self.name.startswith("knn"):
                out=self._prob_knn(x)
            elif self.name.startswith("symbolic_pair"):
                out=self._prob_pair(x)
            elif self.name=="id3_depth4_all":
                out=self._prob_tree(x)
            elif self.name=="logistic_triple":
                out=self._prob_logistic(x)
            elif self.name==DIAGNOSTIC:
                out=(.5,.5,.5)
            else:raise ValueError("bad control")
            if len(out)!=3 or any(not 0<=v<=1 for v in out):
                raise AssertionError("invalid conventional probability")
            self._prediction_cache[x]=out
        return self._prediction_cache[x]

    def choose(self,row):
        return plan(self,row)

    def state(self):
        return {"type":"aai11p.control.v1","name":self.name,
                "rows":[[list(x),list(m)] for x,m in self.rows],
                "weights":self.weights,"trained":self.trained}


def make(name):
    return Control(name)


def checkpoint(model):
    return canonical(model.state())


def restore(payload,name):
    raw=json.loads(payload)
    if canonical(raw)!=payload or type(raw) is not dict or set(raw)!={"type","name","rows","weights","trained"}:
        raise ValueError("bad checkpoint source")
    if raw["type"]!="aai11p.control.v1" or raw["name"]!=name:
        raise ValueError("wrong checkpoint type/method")
    model=make(name)
    if type(raw["rows"]) is not list:
        raise ValueError("invalid sample list")
    for item in raw["rows"]:
        if type(item) is not list or len(item)!=2:
            raise ValueError("invalid sample")
        model.rows.append((world.bits(item[0],6),world.bits(item[1],3)))
    limit={"tabular_recent16":16,"knn_recent32":32,"symbolic_pair_recent16":16}.get(name)
    if limit is not None and len(model.rows)>limit:
        raise ValueError("over-limit conventional checkpoint")
    if name=="logistic_triple":
        weights=raw["weights"]
        if type(weights) is not list or len(weights)!=3 or any(
            type(a) is not list or len(a)!=42 for a in weights):
            raise ValueError("bad logistic weights")
        if any(type(w) not in (int,float) or not math.isfinite(w)
               for row in weights for w in row):
            raise ValueError("invalid weight")
        model.weights=weights
    elif raw["weights"] is not None:
        raise ValueError("non-logistic weights")
    if type(raw["trained"]) is not bool or (name!="logistic_triple" and raw["trained"]):
        raise ValueError("bad training flag")
    model.trained=raw["trained"]
    if checkpoint(model)!=payload:
        raise ValueError("checkpoint did not round-trip exactly")
    return model
