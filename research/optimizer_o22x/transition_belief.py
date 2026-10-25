"""O22-X: explicit TWO-step public consequence-belief composition.

Forecast first source-returned public state from ONLY available current source
six fields and chosen legal action; enumerate possible next observed front and
forward translation, and feed EACH predicted outcome (not actual source after)
to forecast the second legal source action. Original R1 LocalCell weights persist.

This is a source-FIT-only compositional preflight, not an integrated R3
controller or an authenticated new-original-world experiment.
"""
from __future__ import annotations
import hashlib,json,math
from research.native.itd02.r1.native_policy import LocalCell,PublicGrid,features,canonical
from research.optimizer_o22v.delayed_cells import _solve

SCHEMA="optimizer.o22x.compositional-public-transition-v1"
ACTIONS=(0,1,2)
PAIRS=tuple(f"{i}{j}" for i in ACTIONS for j in ACTIONS)
SAFE=tuple(p for p in PAIRS if p not in ("01","10"))
DIR=((1,0),(0,1),(-1,0),(0,-1))
CAP=4096

def check_public(s):
    if type(s) is not dict or set(s)!={"x","y","goal_x","goal_y","direction","front_blocked"}:
        raise ValueError("O22X_PUBLIC_SIX_FIELDS_ONLY")
    g=PublicGrid(s["x"],s["y"],s["goal_x"],s["goal_y"],s["direction"],s["front_blocked"])
    return features(g)

def check_transition(before,action,after):
    check_public(before);check_public(after)
    if type(action) is not int or action not in ACTIONS:
        raise ValueError("O22X_ONLY_ORIGINAL_SELECTED_LEGAL_ACTION")
    if (before["goal_x"],before["goal_y"])!=(after["goal_x"],after["goal_y"]):
        raise ValueError("O22X_SOURCE_GOAL_CHANGED")
    heading=before["direction"]
    if action in (0,1):
        want=(heading-1)%4 if action==0 else (heading+1)%4
        if (after["x"],after["y"])!=(before["x"],before["y"]) or after["direction"]!=want:
            raise ValueError("O22X_SOURCE_TURN_ILLEGAL")
    else:
        dx,dy=DIR[heading]
        delta=(after["x"]-before["x"],after["y"]-before["y"])
        if delta not in ((0,0),(dx,dy)) or after["direction"]!=heading:
            raise ValueError("O22X_SOURCE_FORWARD_ILLEGAL")
    return int(after["front_blocked"]),int((after["x"],after["y"])!=(before["x"],before["y"]))

def clip(v):
    return max(0.001,min(.999,float(v)))

def _verify(raw,identity,max_size):
    try:
        if type(raw) is not bytes or not 0<len(raw)<max_size:
            raise ValueError("O22X_CHECKPOINT_SIZE")
        x=json.loads(raw)
        if (type(x) is not dict or set(x)!={"state","sha256"} or
            type(x["state"]) is not dict or x["state"].get("schema")!=identity or
            hashlib.sha256(canonical(x["state"])).hexdigest()!=x["sha256"]):
            raise ValueError("O22X_CHECKPOINT_HASH")
        b=x["state"]
        if type(b.get("events")) is not int or not 0<=b["events"]<=CAP:
            raise ValueError("O22X_CHECKPOINT_EVENTS")
        return b
    except (ValueError,TypeError,OverflowError,KeyError) as e:
        raise ValueError("O22X_UNTRUSTED_CHECKPOINT") from e

def _cells_to_wire(cells):
    return [[[c.fast,c.slow,c.updates] for c in head] for head in cells]

def _cells_from_wire(rows,expected,action):
    if type(rows) is not list or len(rows)!=2:
        raise ValueError("O22X_BAD_CELL_HEADS")
    heads=[]
    for index,head in enumerate(rows):
        if type(head) is not list or len(head)!=9:
            raise ValueError("O22X_BAD_CELL_FEATURE_WIDTH")
        cohort=[]
        for c in head:
            if (type(c) is not list or len(c)!=3 or
                any(type(v) not in (float,int) or not math.isfinite(v) for v in c) or
                abs(c[0])>32 or abs(c[1])>32 or
                type(c[2]) is not int or c[2]!=(expected if action==2 or index==0 else 0)):
                raise ValueError("O22X_BAD_CELL_STATE")
            cohort.append(LocalCell(*c))
        heads.append(cohort)
    return heads

class NativeCausalCells:
    """Original Ygg R1 fast/slow local plasticity for source-public effects."""
    SCHEMA=SCHEMA+".original-localcell"
    def __init__(self):
        self.cells={str(a):[[LocalCell() for _ in range(9)] for _ in range(2)]
                    for a in ACTIONS}
        self.action_counts={"0":0,"1":0,"2":0}
        self.events=0
    def predict(self,s,a):
        x=check_public(s)
        if type(a) is not int or a not in ACTIONS:
            raise ValueError("O22X_PREDICT_ACTION")
        heads=self.cells[str(a)]
        front=clip(.5+sum(c.output(v) for c,v in zip(heads[0],x)))
        move=clip(.5+sum(c.output(v) for c,v in zip(heads[1],x))) if a==2 else 0.
        return (front,move)
    def learn(self,b,a,after):
        y=check_transition(b,a,after)
        if self.events>=CAP:raise ValueError("O22X_SELECTED_TRAIN_BUDGET")
        x=check_public(b);p=self.predict(b,a)
        for index in ((0,1) if a==2 else (0,)):
            err=max(-1.,min(1.,y[index]-p[index]))
            for c,v in zip(self.cells[str(a)][index],x):c.learn(v,err)
        self.events+=1;self.action_counts[str(a)]+=1
    def checkpoint(self):
        b={"schema":self.SCHEMA,"events":self.events,"actions":self.action_counts,
           "cells":{k:_cells_to_wire(v) for k,v in self.cells.items()}}
        return canonical({"state":b,"sha256":hashlib.sha256(canonical(b)).hexdigest()})
    @classmethod
    def restore(cls,raw):
        b=_verify(raw,cls.SCHEMA,80000)
        if (set(b)!={"schema","events","actions","cells"} or
            type(b["actions"]) is not dict or set(b["actions"])!={"0","1","2"} or
            type(b["cells"]) is not dict or set(b["cells"])!={"0","1","2"}):
            raise ValueError("O22X_NATIVE_CHECKPOINT_KEYS")
        if (any(type(v) is not int or v<0 for v in b["actions"].values()) or
            sum(b["actions"].values())!=b["events"]):
            raise ValueError("O22X_NATIVE_ACTION_COUNT")
        o=cls()
        for a,v in b["cells"].items():
            heads=_cells_from_wire(v,b["actions"][a],int(a))
            # Exactly ZERO local movement weight updates for turns.
            if a!="2" and any(c.updates!=0 for c in heads[1]):
                raise ValueError("O22X_TURN_MOVEMENT_LEARNED")
            o.cells[a]=heads
        o.action_counts=b["actions"];o.events=b["events"]
        return o

class ConventionalNineRidge:
    """Independent fully FIT-trained source-public per-selected-action ridge."""
    SCHEMA=SCHEMA+".independent-action-ridge"
    def __init__(self):
        self.x={str(a):[[0.]*9 for _ in range(9)] for a in ACTIONS}
        self.y={str(a):[[0.]*9 for _ in range(2)] for a in ACTIONS}
        self.w={str(a):[[0.]*9 for _ in range(2)] for a in ACTIONS}
        self.action_counts={"0":0,"1":0,"2":0};self.events=0;self.fitted=False
    def learn(self,b,a,after):
        labels=check_transition(b,a,after);x=check_public(b)
        if self.fitted or self.events>=CAP:
            raise ValueError("O22X_RIDGE_TRAIN_FROZEN")
        k=str(a)
        for i in range(9):
            for j in range(9):self.x[k][i][j]+=x[i]*x[j]
            for h in ((0,1) if a==2 else (0,)):self.y[k][h][i]+=x[i]*labels[h]
        self.events+=1;self.action_counts[k]+=1
    def finalize(self):
        if self.fitted or not self.events or min(self.action_counts.values())==0:
            raise ValueError("O22X_RIDGE_NOT_FULLY_SOURCE_FIT")
        for a in ACTIONS:
            k=str(a);gram=[list(row) for row in self.x[k]]
            for i in range(9):gram[i][i]+=1.
            for h in ((0,1) if a==2 else (0,)):
                self.w[k][h]=_solve(gram,self.y[k][h])
        self.fitted=True
    def predict(self,s,a):
        x=check_public(s)
        if type(a) is not int or a not in ACTIONS or not self.fitted:
            raise ValueError("O22X_RIDGE_PREDICTION_UNFIT")
        heads=self.w[str(a)]
        front=clip(sum(xi*wi for xi,wi in zip(x,heads[0])))
        move=clip(sum(xi*wi for xi,wi in zip(x,heads[1]))) if a==2 else 0.
        return (front,move)
    def checkpoint(self):
        b={"schema":self.SCHEMA,"events":self.events,"actions":self.action_counts,
           "x":self.x,"y":self.y,"w":self.w,"fitted":self.fitted}
        return canonical({"state":b,"sha256":hashlib.sha256(canonical(b)).hexdigest()})
    @classmethod
    def restore(cls,raw):
        b=_verify(raw,cls.SCHEMA,110000)
        if (set(b)!={"schema","events","actions","x","y","w","fitted"}
            or type(b["fitted"]) is not bool or type(b["actions"]) is not dict
            or set(b["actions"])!={"0","1","2"} or
            any(type(v) is not int or v<0 for v in b["actions"].values()) or
            sum(b["actions"].values())!=b["events"]):
            raise ValueError("O22X_RIDGE_SNAPSHOT_COUNTERS")
        o=cls()
        for field in ("x","y","w"):
            root=b[field]
            if type(root) is not dict or set(root)!={"0","1","2"}:
                raise ValueError("O22X_RIDGE_SNAPSHOT_HEADS")
            for action in ACTIONS:
                matrix=root[str(action)]
                n=9 if field=="x" else 2
                if (type(matrix) is not list or len(matrix)!=n or
                    any(type(row) is not list or len(row)!=9 for row in matrix) or
                    any(type(v) not in (float,int) or not math.isfinite(v) or abs(v)>4096
                        for row in matrix for v in row)):
                    raise ValueError("O22X_RIDGE_SNAPSHOT_WEIGHTS")
        o.events=b["events"];o.action_counts=b["actions"]
        o.x=b["x"];o.y=b["y"];o.w=b["w"];o.fitted=b["fitted"]
        return o

def one_step_belief(model,s,action):
    """Never reads actual source returned-after for any imagined action."""
    check_public(s)
    front_p,move_p=model.predict(s,action)
    d=s["direction"]
    if action==0:d=(d-1)%4
    elif action==1:d=(d+1)%4
    branches=[]
    for moved,pm in ((0,1-move_p),(1,move_p)) if action==2 else ((0,1.),):
        x,y=s["x"],s["y"]
        if moved:
            dx,dy=DIR[d];x=max(0,min(64,x+dx));y=max(0,min(64,y+dy))
        for blocked,pb in ((False,1-front_p),(True,front_p)):
            state=dict(s,x=x,y=y,direction=d,front_blocked=blocked)
            branches.append((pm*pb,state))
    if abs(sum(q for q,_ in branches)-1.)>1e-8:
        raise ValueError("O22X_BELIEF_NOT_NORMALIZED")
    return branches

def two_step_belief(model,public_before,pair):
    check_public(public_before)
    if type(pair) is not str or pair not in PAIRS:
        raise ValueError("O22X_ONLY_LEGAL_PAIR")
    d0=abs(public_before["x"]-public_before["goal_x"])+abs(public_before["y"]-public_before["goal_y"])
    prob=0.;progress=0.;front=0.;support=0
    for p1,s1 in one_step_belief(model,public_before,int(pair[0])):
        for p2,s2 in one_step_belief(model,s1,int(pair[1])):
            weight=p1*p2
            d2=abs(s2["x"]-s2["goal_x"])+abs(s2["y"]-s2["goal_y"])
            prob+=weight
            progress+=weight*max(-1.,min(1.,(d0-d2)/2.))
            front+=weight*int(s2["front_blocked"])
            support+=1
    if abs(prob-1.)>1e-8:raise ValueError("O22X_TWO_STEP_BELIEF_MASS_DRIFT")
    return (max(-1.,min(1.,progress)),clip(front))

def choose(model,s,allowed=SAFE):
    return max(allowed,key=lambda pair:(two_step_belief(model,s,pair)[0],-int(pair)))
