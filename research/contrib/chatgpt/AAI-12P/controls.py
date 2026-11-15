"""AAI-12P independent, fully fitted PUBLIC eight-bit/four-mediator controls.

No dependency on or import of the privileged simulator equations. All
methods get identical training/challenge observations and actual do-actions.
"""
from __future__ import annotations
import itertools
import json
import math
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import world

METHODS=("tabular_all","tabular_recent16","knn_recent32","id3_depth5",
         "logistic_pair_fullfit","causal_structure_recent8",
         "causal_structure_recent16","causal_structure_all")
CAUSAL=METHODS[-3:]
MONOMIALS=((),*((i,) for i in range(8)),
           *itertools.combinations(range(8),2))
assert len(MONOMIALS)==37
PROB_BIT=(.05,.95)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)


def expected(probs,goal,steps):
    return sum(p if g else (1-p) for p,g in zip(probs,world.bits(goal,4)))-world.COST*steps


def choose(model,row):
    world.visible(row)
    if row["actions_taken"]>=2:return None
    x=tuple(row["x"]);goal=tuple(row["goal"])
    spent=row["actions_taken"]
    best=float(row["reward"])
    selected=None
    for action in world.ACTIONS:
        x1=world.setbit(x,action)
        value=expected(model.predict(x1),goal,spent+1)
        if value>best+1e-10:
            best,selected=value,action
        if spent==0:
            for next_action in world.ACTIONS:
                x2=world.setbit(x1,next_action)
                later=expected(model.predict(x2),goal,2)
                if later>best+1e-10:
                    best,selected=later,action
    return selected


def features(x):
    x=world.bits(x,8)
    return tuple(float(math.prod(x[i] for i in mono)) for mono in MONOMIALS)


def _op(op,a,b):
    if op=="xor":return a^b
    if op=="and":return a&b
    if op=="or":return a|b
    raise ValueError("unregistered Boolean operator")


def _rule(rule,values):
    tag=rule[0]
    if tag=="bin":
        return _op(rule[1],values[rule[2]],values[rule[3]])
    if tag=="switch":
        return (values[rule[1]]^values[rule[2]]) if not values[6] else (
            values[rule[1]]|values[rule[2]])
    if tag=="flip7":
        return _op(rule[1],values[8],values[9])^values[7]
    if tag=="inhibit":
        return values[8]&(1-values[9])
    if tag=="xor4":
        return values[8]^values[9]^values[10]^values[7]
    if tag=="flip6":
        return _op(rule[1],values[10],values[rule[2]])^values[6]
    raise ValueError("illegal hypothesis rule")


def _grammar(out):
    # Every publicly described structural DAG rule family is included.
    width=(8,8,10,11)[out]
    rules=[("bin",op,i,j) for op in ("xor","and","or")
           for i,j in itertools.combinations(range(width),2)]
    if out==0:
        rules.extend(("switch",i,j) for i,j in itertools.combinations(range(6),2))
    if out==2:
        rules.extend(("flip7",op) for op in ("xor","and","or"))
        rules.append(("inhibit",))
    if out==3:
        rules.append(("xor4",))
        rules.extend(("flip6",op,k) for op in ("xor","and","or") for k in range(6))
    return tuple(rules)


GRAMMARS=tuple(_grammar(o) for o in range(4))


def _grammatical_map(rows):
    if not rows:return (0,0,0,0)
    errors=[[0]*len(a) for a in GRAMMARS]
    for x,m in rows:
        state=(*x,*m)
        for out,grammar in enumerate(GRAMMARS):
            target=m[out]
            counter=errors[out]
            for i,hypothesis in enumerate(grammar):
                counter[i]+=int(_rule(hypothesis,state)!=target)
    return tuple(min(range(len(counts)),key=lambda j:(counts[j],j))
                 for counts in errors)


def _entropy(rows,out):
    if not rows:return 0.
    p=sum(m[out] for _,m in rows)/len(rows)
    return 0. if p in (0.,1.) else -p*math.log(p)-(1-p)*math.log(1-p)


def _tree(rows,out,depth,columns):
    if not rows or depth<=0 or not columns or _entropy(rows,out)<1e-10:
        return float((1+sum(m[out] for _,m in rows))/(len(rows)+2))
    h=_entropy(rows,out)
    chosen=None
    gain=0.
    branches=None
    for i in columns:
        left=[row for row in rows if row[0][i]==0]
        right=[row for row in rows if row[0][i]==1]
        if not left or not right:continue
        quality=h-(len(left)*_entropy(left,out)+len(right)*_entropy(right,out))/len(rows)
        if quality>gain+1e-12:
            gain=quality;chosen=i;branches=(left,right)
    if chosen is None:
        return float((1+sum(m[out] for _,m in rows))/(len(rows)+2))
    cols=tuple(i for i in columns if i!=chosen)
    return (chosen,_tree(branches[0],out,depth-1,cols),
            _tree(branches[1],out,depth-1,cols))


def _tree_prob(node,x):
    if type(node) is float:return node
    index,left,right=node
    return _tree_prob(right if x[index] else left,x)


class Control:
    def __init__(self,name):
        if name not in METHODS:raise ValueError("nonregistered control")
        self.name=name
        self.rows=[]
        self.weights=[[0.]*len(MONOMIALS) for _ in range(4)] if (
            name=="logistic_pair_fullfit") else None
        self.trained=False
        self._invalidate()

    def _invalidate(self):
        self._pred={}
        self._best_rules=None
        self._trees=None

    def observe(self,public):
        x,m=world.visible(public)
        self.rows.append((x,m))
        limit={"tabular_recent16":16,"knn_recent32":32,
               "causal_structure_recent8":8,"causal_structure_recent16":16}.get(self.name)
        if limit is not None and len(self.rows)>limit:
            self.rows=self.rows[-limit:]
        if self.name=="logistic_pair_fullfit" and self.trained:
            self._online(x,m,2)
        self._invalidate()

    @staticmethod
    def _sigmoid(z):
        return 1./(1.+math.exp(-max(-24.,min(24.,z))))

    def _online(self,x,m,epochs):
        feat=features(x)
        for _ in range(epochs):
            for out in range(4):
                weights=self.weights[out]
                prob=self._sigmoid(sum(a*b for a,b in zip(weights,feat)))
                for k,f in enumerate(feat):
                    weights[k]=round(weights[k]-.20*((prob-m[out])*f+
                                     (.005*weights[k] if k else 0)),12)

    def fit_checkpoint(self):
        if self.name!="logistic_pair_fullfit":return
        if not self.rows:raise ValueError("no public rows for logistic fitting")
        data=[(features(x),m) for x,m in self.rows]
        n=len(data)
        for _ in range(250):
            grad=[[0.]*len(MONOMIALS) for _ in range(4)]
            for feat,m in data:
                for out in range(4):
                    z=sum(a*b for a,b in zip(self.weights[out],feat))
                    error=self._sigmoid(z)-m[out]
                    for i,f in enumerate(feat):grad[out][i]+=error*f
            for out in range(4):
                weights=self.weights[out]
                for i,value in enumerate(grad[out]):
                    weights[i]=round(weights[i]-.20*(value/n+
                                     (.005*weights[i] if i else 0)),12)
        self.trained=True
        self._invalidate()

    def _structure(self,x):
        if self._best_rules is None:
            self._best_rules=_grammatical_map(self.rows)
        rules=tuple(GRAMMARS[o][i] for o,i in enumerate(self._best_rules))
        state=(*x,0,0,0)
        b0=_rule(rules[0],state);b1=_rule(rules[1],state)
        p0=PROB_BIT[b0];p1=PROB_BIT[b1]
        p2=0.;p3=0.
        for m0,m1 in itertools.product((0,1),repeat=2):
            weight=(p0 if m0 else 1-p0)*(p1 if m1 else 1-p1)
            mid=(*x,m0,m1,0)
            bit2=_rule(rules[2],mid)
            q2=PROB_BIT[bit2]
            p2+=weight*q2
            for m2 in (0,1):
                p=weight*(q2 if m2 else 1-q2)
                p3+=p*PROB_BIT[_rule(rules[3],(*x,m0,m1,m2))]
        return (p0,p1,p2,p3)

    def predict(self,x):
        x=world.bits(x,8)
        if x not in self._pred:
            if self.name.startswith("tabular"):
                rows=[m for a,m in self.rows if a==x]
                result=tuple((1+sum(m[o] for m in rows))/(len(rows)+2)
                             for o in range(4))
            elif self.name=="knn_recent32":
                neighbors=sorted(enumerate(self.rows),
                                 key=lambda t:(sum(i!=j for i,j in zip(x,t[1][0])),-t[0]))
                selected=[a[1][1] for a in neighbors[:5]]
                result=tuple((1+sum(m[o] for m in selected))/(len(selected)+2)
                             for o in range(4))
            elif self.name=="id3_depth5":
                if self._trees is None:
                    self._trees=tuple(_tree(self.rows,o,5,tuple(range(8)))
                                      for o in range(4))
                result=tuple(_tree_prob(tree,x) for tree in self._trees)
            elif self.name=="logistic_pair_fullfit":
                feat=features(x)
                result=tuple(self._sigmoid(sum(w*f for w,f in zip(weights,feat)))
                             for weights in self.weights)
            else:
                result=self._structure(x)
            if len(result)!=4 or any(not math.isfinite(p) or p<0 or p>1 for p in result):
                raise AssertionError("invalid matched public predictor")
            self._pred[x]=tuple(round(float(p),12) for p in result)
        return self._pred[x]

    def choose(self,public):
        world.visible(public)
        return choose(self,public)

    def state(self):
        return {"type":"aai12p.control.v1","name":self.name,
                "rows":[[list(x),list(m)] for x,m in self.rows],
                "weights":self.weights,"trained":self.trained}


def checkpoint(model):
    if not isinstance(model,Control):
        raise TypeError("not a public matched conventional control")
    return canonical(model.state())


def restore(name,source):
    if name not in METHODS or type(source) is not str:
        raise ValueError("wrong method or checkpoint")
    d=json.loads(source)
    if (canonical(d)!=source or type(d) is not dict or
        set(d)!={"type","name","rows","weights","trained"} or
        d["type"]!="aai12p.control.v1" or d["name"]!=name or
        type(d["rows"]) is not list or type(d["trained"]) is not bool):
        raise ValueError("invalid public cold conventional snapshot")
    model=Control(name)
    if len(d["rows"])>96:raise ValueError("unapproved row history")
    for row in d["rows"]:
        if type(row) is not list or len(row)!=2:
            raise ValueError("malformed public past observation")
        model.rows.append((world.bits(row[0],8),world.bits(row[1],4)))
    if name=="logistic_pair_fullfit":
        w=d["weights"]
        if (type(w) is not list or len(w)!=4 or
            any(type(v) is not list or len(v)!=len(MONOMIALS)
                or any(type(x) not in (int,float) or not math.isfinite(x)
                       for x in v) for v in w)):
            raise ValueError("invalid fitted logistic weights")
        model.weights=w
    elif d["weights"] is not None or d["trained"]:
        raise ValueError("non-logistic model received fitted weights")
    model.trained=d["trained"]
    if checkpoint(model)!=source:raise ValueError("cold source changed")
    return model
