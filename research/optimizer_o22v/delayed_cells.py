"""O22-V authentic R1 local-cell 3-selected-action delayed-progress research.

R1 LocalCell and nine public features are used UNMODIFIED. No source simulator,
original R3 integration, unseen counterfactual action, or future policy input.
Independent ridge/full-nine control implemented with ordinary linear algebra.
"""
from __future__ import annotations
import hashlib
import json
import math
from research.native.itd02.r1.native_policy import LocalCell,PublicGrid,features

SCHEMA="optimizer.o22v.authentic-public-three-step-progress.v1"
ACTIONS=(0,1,2)
FEATURES=9


def phi(before):
    if (type(before) is not dict or set(before)!={
        "x","y","direction","goal_x","goal_y","front_blocked"} or
        any(type(before[k]) is not int for k in (
            "x","y","direction","goal_x","goal_y")) or
        type(before["front_blocked"]) is not bool):
        raise ValueError("O22V_ONLY_EXPLICIT_SOURCE_PUBLIC_STATE")
    return features(PublicGrid(
        before["x"],before["y"],before["goal_x"],before["goal_y"],
        before["direction"],before["front_blocked"]))


def legal_action(action):
    if type(action) is not int or action not in ACTIONS:
        raise ValueError("O22V_INVALID_ACTUALLY_SELECTED_SOURCE_ACTION")


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode()


def _clip(x):
    return max(-1.,min(1.,float(x)))


class DelayedNativeCells:
    """Original R1 fast/slow LocalCell.learn; new selected 3-step training label."""

    SCHEMA=SCHEMA+".native-r1-cell"

    def __init__(self):
        self.cells={str(a):[LocalCell() for _ in range(FEATURES)] for a in ACTIONS}
        self.actions={str(a):0 for a in ACTIONS}
        self.events=0

    def predict(self,before,action):
        legal_action(action)
        x=phi(before)
        return _clip(sum(cell.output(v) for cell,v in
                         zip(self.cells[str(action)],x)))

    def learn(self,before,action,observed_delayed_progress):
        legal_action(action)
        x=phi(before)
        y=float(observed_delayed_progress)
        if not math.isfinite(y) or not -1 <= y <= 1 or self.events>=4096:
            raise ValueError("O22V_PUBLIC_DELAYED_TARGET_INVALID")
        error=_clip(y-self.predict(before,action))
        for cell,v in zip(self.cells[str(action)],x):
            cell.learn(v,error)
        self.actions[str(action)]+=1
        self.events+=1

    def propose(self,before):
        x=phi(before)
        if any(v==0 for v in self.actions.values()):
            return None
        q=[self.predict(before,a) for a in ACTIONS]
        return max(ACTIONS,key=lambda a:(q[a],-a)) if max(q)-min(q)>0.05 else None

    def checkpoint(self):
        body={"schema":self.SCHEMA,"events":self.events,"actions":self.actions,
              "cells":{a:[{"fast":c.fast,"slow":c.slow,"updates":c.updates}
                          for c in cohort] for a,cohort in self.cells.items()}}
        raw=canonical(body)
        if len(raw)>18000:raise ValueError("O22V_NATIVE_SNAPSHOT_OVERSIZE")
        return canonical({"body":body,"sha256":hashlib.sha256(raw).hexdigest()})

    @classmethod
    def restore(cls,raw):
        b=_open(raw,cls.SCHEMA,18000)
        if set(b)!={"schema","events","actions","cells"} or type(b["cells"]) is not dict or set(b["cells"])!={"0","1","2"}:
            raise ValueError("O22V_NATIVE_UNTRUSTED_CELLS")
        _counts(b)
        o=cls()
        for a,rows in b["cells"].items():
            if type(rows) is not list or len(rows)!=FEATURES:
                raise ValueError("O22V_NATIVE_CELL_WIDTH")
            c=[]
            for row in rows:
                if type(row) is not dict or set(row)!={"fast","slow","updates"}:
                    raise ValueError("O22V_NATIVE_CELL_SHAPE")
                fast,slow,updates=row["fast"],row["slow"],row["updates"]
                if (type(fast) not in (float,int) or type(slow) not in (float,int)
                    or not math.isfinite(fast) or not math.isfinite(slow)
                    or max(abs(fast),abs(slow))>32 or type(updates) is not int
                    or updates<0 or updates!=b["actions"][a]):
                    raise ValueError("O22V_NATIVE_CELL_CORRUPT")
                c.append(LocalCell(fast,slow,updates))
            o.cells[a]=c
        o.actions=b["actions"];o.events=b["events"]
        return o


def _open(raw,schema,cap=45000):
    try:
        if type(raw) is not bytes or not 0<len(raw)<=cap:
            raise ValueError("O22V_CHECKPOINT_BYTES")
        w=json.loads(raw)
        if type(w) is not dict or set(w)!={"body","sha256"}:
            raise ValueError("O22V_CHECKPOINT_WIRE")
        b=w["body"]
        if type(b) is not dict or b.get("schema")!=schema or hashlib.sha256(canonical(b)).hexdigest()!=w["sha256"]:
            raise ValueError("O22V_CHECKPOINT_DIGEST")
        return b
    except (TypeError,ValueError,OverflowError,KeyError) as e:
        raise ValueError("O22V_UNTRUSTED_CHECKPOINT") from e


def _counts(b):
    if (type(b.get("events")) is not int or not 0<=b["events"]<=4096 or
        type(b.get("actions")) is not dict or set(b["actions"])!={"0","1","2"}
        or any(type(v) is not int or v<0 for v in b["actions"].values())
        or sum(b["actions"].values())!=b["events"]):
        raise ValueError("O22V_UNTRUSTED_COUNTS")


def _solve(mat,ys):
    """Deterministic full-pivot 9x9 positive-definite ridge normal equations."""
    n=len(ys)
    rows=[list(mat[i])+[ys[i]] for i in range(n)]
    for i in range(n):
        k=max(range(i,n),key=lambda j:abs(rows[j][i]))
        if abs(rows[k][i])<1e-14:raise ValueError("O22V_RIDGE_SINGULAR")
        rows[i],rows[k]=rows[k],rows[i]
        pivot=rows[i][i]
        for j in range(i,n+1):rows[i][j]/=pivot
        for k in range(n):
            if k==i:continue
            f=rows[k][i]
            for j in range(i,n+1):rows[k][j]-=f*rows[i][j]
    return [row[-1] for row in rows]


class FittedRidge9:
    """Independent all-nine-public-feature conventional ridge via exact fit."""

    SCHEMA=SCHEMA+".full9-ridge"

    def __init__(self,action_conditioned=True):
        if type(action_conditioned) is not bool:raise ValueError("O22V_RIDGE_MODE")
        self.action_conditioned=action_conditioned
        keys=("0","1","2") if action_conditioned else ("all",)
        self.xtx={a:[[0.]*FEATURES for _ in range(FEATURES)] for a in keys}
        self.xty={a:[0.]*FEATURES for a in keys}
        self.coef={a:[0.]*FEATURES for a in keys}
        self.actions={str(a):0 for a in ACTIONS}
        self.events=0
        self.fitted=False

    def learn(self,before,action,delayed_progress):
        legal_action(action)
        x=phi(before)
        y=float(delayed_progress)
        if self.fitted or not math.isfinite(y) or not -1<=y<=1 or self.events>=4096:
            raise ValueError("O22V_RIDGE_TRAIN_INVALID")
        key=str(action) if self.action_conditioned else "all"
        for j in range(FEATURES):
            self.xty[key][j]+=x[j]*y
            for k in range(FEATURES):
                self.xtx[key][j][k]+=x[j]*x[k]
        self.events+=1;self.actions[str(action)]+=1

    def finalize(self):
        if self.fitted or self.events==0:
            raise ValueError("O22V_RIDGE_FIT_EMPTY_OR_TWICE")
        # Regularizer λ=1, frozen without a tuned grid.
        for key in self.xtx:
            m=[list(row) for row in self.xtx[key]]
            for j in range(FEATURES):m[j][j]+=1.
            self.coef[key]=_solve(m,self.xty[key])
        self.fitted=True

    def predict(self,before,action):
        legal_action(action)
        if not self.fitted:raise ValueError("O22V_RIDGE_NOT_FITTED")
        x=phi(before)
        key=str(action) if self.action_conditioned else "all"
        return _clip(sum(a*b for a,b in zip(self.coef[key],x)))

    def propose(self,before):
        if not self.fitted or any(v==0 for v in self.actions.values()):return None
        q=[self.predict(before,a) for a in ACTIONS]
        return max(ACTIONS,key=lambda a:(q[a],-a)) if max(q)-min(q)>0.05 else None

    def checkpoint(self):
        b={"schema":self.SCHEMA,"conditioned":self.action_conditioned,
           "fitted":self.fitted,"events":self.events,"actions":self.actions,
           "xtx":self.xtx,"xty":self.xty,"coef":self.coef}
        raw=canonical(b)
        if len(raw)>45000:raise ValueError("O22V_RIDGE_SNAPSHOT_OVERSIZE")
        return canonical({"body":b,"sha256":hashlib.sha256(raw).hexdigest()})

    @classmethod
    def restore(cls,raw):
        b=_open(raw,cls.SCHEMA)
        if set(b)!={"schema","conditioned","fitted","events","actions","xtx","xty","coef"} or type(b["conditioned"]) is not bool or type(b["fitted"]) is not bool:
            raise ValueError("O22V_RIDGE_WIRE_FIELDS")
        _counts(b)
        o=cls(b["conditioned"])
        for field in ("xtx","xty","coef"):
            if type(b[field]) is not dict or set(b[field])!=set(o.xtx):
                raise ValueError("O22V_RIDGE_DIMENSIONS")
        for k in o.xtx:
            mat=b["xtx"][k]
            if (type(mat) is not list or len(mat)!=FEATURES
                or any(type(row) is not list or len(row)!=FEATURES for row in mat)):
                raise ValueError("O22V_RIDGE_MATRIX")
            for row in mat:
                if any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>4096 for v in row):
                    raise ValueError("O22V_RIDGE_MATRIX_VALUE")
            for field in ("xty","coef"):
                v=b[field][k]
                if (type(v) is not list or len(v)!=FEATURES or
                    any(type(z) not in (int,float) or not math.isfinite(z) or abs(z)>4096 for z in v)):
                    raise ValueError("O22V_RIDGE_VECTOR")
        o.fitted=b["fitted"];o.events=b["events"];o.actions=b["actions"]
        o.xtx=b["xtx"];o.xty=b["xty"];o.coef=b["coef"]
        return o
