"""AAI-11A independent tokenless protected causal graph learner and FAIR controls.

All 45/45/84 graph hypotheses are public inductive biases. The identical
hypothesis grammar, MAP prediction, and original shared planner are available
to the conventional graph_all/recent8/recent16 controls. Only actual public
do-action consequences can update counts. Never read simulator law equations.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/"AAI-11P"))
import world, controls

OPS=("xor","and","or")
GRAPH01=controls.PAIR_GRAMMAR
GRAPH2=tuple((op,i,j) for op in OPS
             for i,j in itertools.combinations(range(8),2))
assert len(GRAPH01)==45 and len(GRAPH2)==84
SIZES=(45,45,84)
MAX_ROWS=96
CONFIDENCE=(.1,.9)


def pattern(rule,values):
    op,i,j=rule
    a,b=values[i],values[j]
    if op=="xor":return a^b
    if op=="and":return a&b
    if op=="or":return a|b
    raise ValueError("unregistered operator")


def x_key(x):
    x=world.bits(x,6)
    return sum(value << (5-index) for index,value in enumerate(x))


# Fixed public grammar truth values only, no hidden simulator functions.
TRUTH01=tuple(tuple(pattern(rule,x) for rule in GRAPH01)
              for x in world.INPUTS)
TRUTH2=tuple(tuple(tuple(pattern(rule,(*x,m0,m1)) for rule in GRAPH2)
                   for m1 in (0,1))
              for m0 in (0,1))
             for x in world.INPUTS)


def public_sample(row):
    x,m=world.visible(row)
    return x,m


def empty_slot(index,prior=None):
    prior=prior if prior is not None else [([0]*n) for n in SIZES]
    return {"id":index,"rows":0,
            "mismatches":[[0]*n for n in SIZES],
            "prior":[list(p) for p in prior]}


def selected(slot):
    return tuple(
        min(range(n),key=lambda i:slot["mismatches"][out][i]+slot["prior"][out][i])
        for out,n in enumerate(SIZES)
    )


def predict_slot(slot,x):
    k=x_key(x)
    m0=TRUTH01[k][selected(slot)[0]]
    m1=TRUTH01[k][selected(slot)[1]]
    m2=TRUTH2[k][m0][m1][selected(slot)[2]]
    return (CONFIDENCE[m0],CONFIDENCE[m1],CONFIDENCE[m2])


def slot_batch_errors(slot,batch):
    s0,s1,s2=selected(slot)
    errors=0
    for x,m in batch:
        k=x_key(x)
        # Diagnostic current evidence uses OBSERVED upstream mediators.
        # Intervention prediction later uses model-predicted upstream bits.
        errors+=int(TRUTH01[k][s0]!=m[0])
        errors+=int(TRUTH01[k][s1]!=m[1])
        errors+=int(TRUTH2[k][m[0]][m[1]][s2]!=m[2])
    return errors


def apply_to_slot(slot,sample,sign):
    x,m=sample
    k=x_key(x)
    for out,patterns in enumerate((TRUTH01[k],TRUTH01[k],
                                    TRUTH2[k][m[0]][m[1]])):
        target=slot["mismatches"][out]
        observed=m[out]
        for i,value in enumerate(patterns):
            if value!=observed:
                target[i]+=sign
    slot["rows"]+=sign


def validate_slot(slot):
    if type(slot) is not dict or set(slot)!={"id","rows","mismatches","prior"}:
        raise ValueError("invalid graph slot fields")
    if type(slot["id"]) is not int or slot["id"]<0:
        raise ValueError("bad slot identity")
    rows=slot["rows"]
    if type(rows) is not int or not 0<=rows<=MAX_ROWS or rows%2:
        raise ValueError("bad slot public row count")
    for field,upper in (("mismatches",rows),("prior",1)):
        vectors=slot[field]
        if type(vectors) is not list or len(vectors)!=3:
            raise ValueError("invalid graph signatures")
        for items,n in zip(vectors,SIZES):
            if type(items) is not list or len(items)!=n:
                raise ValueError("invalid graph hypothesis width")
            if any(type(v) is not int or not 0<=v<=upper for v in items):
                raise ValueError("invalid graph error/prior count")


class ProtectedGraphBank:
    """Frozen two-public-row contradiction gate, three protected graph contexts."""

    def __init__(self,max_slots=3):
        if type(max_slots) is not int or max_slots not in (1,3):
            raise ValueError("only 1-slot ablation and 3-slot bank permitted")
        self.max_slots=max_slots
        self.slots=[empty_slot(0)]
        self.active_id=0
        self.next_id=1
        self.scratch=[]
        self.retrievals=0
        self._invalidate()

    def _invalidate(self):
        self._pred_cache={}
        self._plan_cache={}

    def active(self):
        return next(s for s in self.slots if s["id"]==self.active_id)

    def _novel_prior(self):
        if self.max_slots==1:return None
        protected=[s for s in self.slots
                   if s["id"]!=self.active_id and s["rows"]>=8]
        if not protected:return None
        oldest=min(protected,key=lambda s:s["id"])
        selected_ops=[grammar[index][0] for index,grammar in
                      zip(selected(oldest),(GRAPH01,GRAPH01,GRAPH2))]
        return [
            [0 if rule[0]==selected_ops[out] else 1 for rule in grammar]
            for out,grammar in enumerate((GRAPH01,GRAPH01,GRAPH2))
        ]

    def observe(self,row):
        sample=public_sample(row)
        self.scratch.append(sample)
        if len(self.scratch)<2:
            return
        batch=tuple(self.scratch)
        old=self.active()
        current=slot_batch_errors(old,batch)
        others=[s for s in self.slots if s["id"]!=self.active_id]
        best=min(others,key=lambda s:(slot_batch_errors(s,batch),s["id"])) if others else None
        recalled=(best is not None and slot_batch_errors(best,batch)<=current-2)
        created=False
        if recalled:
            target=best
        elif len(self.slots)<self.max_slots and old["rows"]>=8 and current>=3:
            target=empty_slot(self.next_id,self._novel_prior())
            created=True
        else:
            target=old
        if target["rows"]+2>MAX_ROWS:
            self.scratch.pop()
            # No durable slot IDs/counters, recall metrics, or active context changed.
            raise ValueError("graph signature slot saturation")
        if recalled:
            self.retrievals+=1
        if created:
            self.next_id+=1
            self.slots.append(target)
        self.active_id=target["id"]
        for sample in batch:
            apply_to_slot(target,sample,+1)
        self.scratch=[]
        self._invalidate()

    def predict(self,x):
        k=x_key(x)
        if k not in self._pred_cache:
            self._pred_cache[k]=predict_slot(self.active(),world.INPUTS[k])
        return self._pred_cache[k]

    def choose(self,row):
        world.visible(row)
        k=(x_key(row["x"]),tuple(row["goal"]),row["actions_taken"],tuple(row["mediators"]))
        if k not in self._plan_cache:
            self._plan_cache[k]=controls.plan(self,row)
        return self._plan_cache[k]

    def fit_checkpoint(self):
        # Pure bounded fixed-statistics learner. No privileged batch fitting.
        return None

    def state(self):
        return {
            "type":"aai11a.protected-graph.v1",
            "max_slots":self.max_slots,
            "slots":self.slots,
            "active_id":self.active_id,
            "next_id":self.next_id,
            "scratch":[[list(x),list(m)] for x,m in self.scratch],
            "retrievals":self.retrievals,
        }


class GraphWindow:
    """Conventional matched public-graph learner, no protected memory."""

    def __init__(self,name):
        if name not in ("graph_recent8","graph_recent16","graph_all"):
            raise ValueError("unregistered structural conventional learner")
        self.name=name
        self.limit={"graph_recent8":8,"graph_recent16":16,"graph_all":None}[name]
        self.rows=[]
        self.stats=empty_slot(0)
        self._invalidate()

    def _invalidate(self):
        self._pred_cache={}
        self._plan_cache={}

    def _append(self,sample):
        self.rows.append(sample)
        apply_to_slot(self.stats,sample,+1)
        if self.limit is not None and len(self.rows)>self.limit:
            oldest=self.rows.pop(0)
            apply_to_slot(self.stats,oldest,-1)
        self._invalidate()

    def observe(self,row):
        self._append(public_sample(row))

    def fit_checkpoint(self):
        return None

    def predict(self,x):
        k=x_key(x)
        if k not in self._pred_cache:
            self._pred_cache[k]=predict_slot(self.stats,world.INPUTS[k])
        return self._pred_cache[k]

    def choose(self,row):
        world.visible(row)
        key=(x_key(row["x"]),tuple(row["goal"]),row["actions_taken"],tuple(row["mediators"]))
        if key not in self._plan_cache:
            self._plan_cache[key]=controls.plan(self,row)
        return self._plan_cache[key]

    def state(self):
        return {"type":"aai11a.graph-window.v1","name":self.name,
                "rows":[[list(x),list(m)] for x,m in self.rows]}


CANDIDATE="protected_graph"
ABLATION="one_slot"
MATCHED_GRAPHS=("graph_recent8","graph_recent16","graph_all")
MATCHED=(*controls.METHODS,*MATCHED_GRAPHS)
NAMES=(CANDIDATE,ABLATION,*MATCHED)


def make(name):
    if name==CANDIDATE:return ProtectedGraphBank(3)
    if name==ABLATION:return ProtectedGraphBank(1)
    if name in MATCHED_GRAPHS:return GraphWindow(name)
    if name in controls.ALL:return controls.make(name)
    raise ValueError("unknown candidate or control")


def checkpoint(name,model):
    if name in (CANDIDATE,ABLATION,*MATCHED_GRAPHS):
        return controls.canonical(model.state())
    return controls.checkpoint(model)


def restore(name,payload):
    data=json.loads(payload)
    if controls.canonical(data)!=payload:
        raise ValueError("non-canonical graph checkpoint")
    if name in (CANDIDATE,ABLATION):
        if type(data) is not dict or set(data)!={
            "type","max_slots","slots","active_id","next_id","scratch","retrievals"
        } or data["type"]!="aai11a.protected-graph.v1":
            raise ValueError("wrong protected graph checkpoint")
        model=ProtectedGraphBank(3 if name==CANDIDATE else 1)
        if data["max_slots"]!=model.max_slots or type(data["slots"]) is not list:
            raise ValueError("wrong protected capacity")
        if not 1<=len(data["slots"])<=model.max_slots:
            raise ValueError("invalid slot count")
        for s in data["slots"]:validate_slot(s)
        ids=[s["id"] for s in data["slots"]]
        if ids!=list(range(len(ids))) or type(data["next_id"]) is not int or data["next_id"]!=len(ids):
            raise ValueError("non-canonical protected IDs")
        if type(data["active_id"]) is not int or data["active_id"] not in ids:
            raise ValueError("invalid active slot")
        if type(data["retrievals"]) is not int or data["retrievals"]<0:
            raise ValueError("bad recall count")
        scratch=data["scratch"]
        if type(scratch) is not list or len(scratch)>1:
            raise ValueError("bad public two-row scratch")
        parsed=[]
        for item in scratch:
            if type(item) is not list or len(item)!=2:
                raise ValueError("bad scratch row")
            parsed.append((world.bits(item[0],6),world.bits(item[1],3)))
        model.slots=data["slots"]
        model.active_id=data["active_id"]
        model.next_id=data["next_id"]
        model.scratch=parsed
        model.retrievals=data["retrievals"]
        model._invalidate()
    elif name in MATCHED_GRAPHS:
        if type(data) is not dict or set(data)!={"type","name","rows"} or (
            data["type"]!="aai11a.graph-window.v1" or data["name"]!=name or
            type(data["rows"]) is not list):
            raise ValueError("bad structural control checkpoint")
        model=GraphWindow(name)
        for row in data["rows"]:
            if type(row) is not list or len(row)!=2:
                raise ValueError("invalid graph control evidence")
            model._append((world.bits(row[0],6),world.bits(row[1],3)))
        if len(model.rows)!=len(data["rows"]):
            raise ValueError("window evidence overflow")
    elif name in controls.ALL:
        model=controls.restore(payload,name)
    else:
        raise ValueError("unknown graph method")
    if checkpoint(name,model)!=payload:
        raise ValueError("checkpoint changed under cold restore")
    return model
