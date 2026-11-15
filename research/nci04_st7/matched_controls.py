"""ST7 conventional polynomial baseline, trained logistic, old ST6 menu.

Independent full GF(2) 36-feature Gaussian elimination is a strong
conventional baseline with the SAME learned 36x44bit capacity, authentic
public action-consequence budget and frozen quadratic inductive prior
as ST7 native. If they tie, there is no uniquely native breakthrough.
No import of private source or native candidate implementation.
"""
import json
import math

from research.nci04_st6.native_operator import NativeOperator8
from research.nci04_st5.matched_controls import brier

SCHEMA="yggdrasil.nci04.st7.conventional-polynomial-gf2.v1"
LOGISTIC_SCHEMA="yggdrasil.nci04.st7.fitted-polynomial-logistic.v1"
ACTIONS=(3,0,1,2,3)
FEATURES=36
MASK=(1<<FEATURES)-1
MAX_UPDATES=10**8


def canonical(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),allow_nan=False)


def pack(x):
    if (type(x) not in (list,tuple) or len(x)!=8 or
        any(type(z) is not int or z not in (0,1) for z in x)):
        raise ValueError("ST7_CONTROL_BAD_PUBLIC_BITS")
    return sum(z<<i for i,z in enumerate(x))


def rot(x,k):
    if type(x) is not int or x not in range(256) or type(k) is not int or k not in (1,2,3):
        raise ValueError("ST7_CONTROL_BAD_PUBLIC_ROTATION")
    return ((x<<k)|(x>>(8-k)))&255


def terms(B):
    if type(B) is not int or B not in range(256):
        raise ValueError("ST7_CONTROL_BAD_ACTUATOR")
    flags=[(B>>i)&1 for i in range(8)]
    return flags+[flags[i]*flags[j] for i in range(8)
                  for j in range(i+1,8)]


def check_transition(before,action,target,after,step,train):
    x=pack(before);y=pack(after);t=pack(target)
    if (type(train) is not bool or type(action) is not int or
        type(step) is not int or step not in range(5) or
        action!=ACTIONS[step] or x^y!=t):
        raise ValueError("ST7_CONTROL_UNAUTHENTIC_PUBLIC_EVENT")
    return x,y


class GF2Conventional:
    """Independent conventional 36-row elimination, LOW pivot first."""
    def __init__(self):
        self.rows=[0]*FEATURES
        self.rank=0
        self.examples=0
        self.conflicts=0
        self.rotation=None
        self.maskA=None
        self.maskB=None
        self.phase=0

    def reset_episode(self):
        self.rotation=None
        self.maskA=None
        self.maskB=None
        self.phase=0

    def _feature(self):
        v=terms(self.maskB)
        return sum(flag<<j for j,flag in enumerate(v))

    def _eliminate(self,packedrow):
        while packedrow&MASK:
            bit=(packedrow&MASK)&-(packedrow&MASK)
            i=bit.bit_length()-1
            if self.rows[i]:
                packedrow^=self.rows[i]
            else:
                return i,packedrow
        return None,(packedrow>>FEATURES)&255

    def predict(self,public,action):
        x=pack(public)
        if type(action) is not int or self.phase>=5 or action!=ACTIONS[self.phase]:
            raise ValueError("ST7_CONTROL_GAUSSIAN_ACTOR_DRIFT")
        if self.phase!=4 or None in (self.rotation,self.maskA,self.maskB):
            return [.5]*8
        pivot,val=self._eliminate(self._feature())
        if pivot is not None:
            return [.5]*8
        outcome=x^rot(x,self.rotation)^self.maskA^val
        return [.99 if (outcome>>k)&1 else .01 for k in range(8)]

    def observe(self,public,action,target,after,*,train=True):
        x,y=check_transition(public,action,target,after,self.phase,train)
        forecast=self.predict(public,action)
        if self.phase==0:
            opts=[k for k in (1,2,3) if rot(x,k)==y]
            self.rotation=opts[0] if len(opts)==1 else None
        elif self.phase==1 and self.rotation is not None:
            self.maskA=y^rot(x,self.rotation)
        elif self.phase==2 and self.rotation is not None:
            self.maskB=y^rot(x,self.rotation)
        elif self.phase==4 and train and None not in (
            self.rotation,self.maskA,self.maskB
        ):
            if self.examples>=MAX_UPDATES:
                raise ValueError("ST7_CONTROL_GAUSSIAN_EXAMPLE_LIMIT")
            residual=y^rot(x,self.rotation)^self.maskA
            feature=self._feature()
            index,reduced=self._eliminate(feature|(residual<<FEATURES))
            if index is not None:
                self.rows[index]=reduced
                self.rank+=1
            elif reduced:
                self.conflicts+=1
            self.examples+=1
        self.phase+=1
        return forecast

    def snapshot(self):
        return canonical({
            "schema":SCHEMA,"rows":self.rows,
            "rank":self.rank,"examples":self.examples,
            "conflicts":self.conflicts,"rotation":self.rotation,
            "maskA":self.maskA,"maskB":self.maskB,"phase":self.phase
        })

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw)>7000:
            raise ValueError("ST7_GAUSSIAN_CHECKPOINT_SIZE")
        try:
            x=json.loads(raw)
            keys={"schema","rows","rank","examples","conflicts",
                  "rotation","maskA","maskB","phase"}
            if (type(x) is not dict or set(x)!=keys or
                x["schema"]!=SCHEMA or type(x["rows"]) is not list or
                len(x["rows"])!=36 or
                any(type(v) is not int or not 0<=v<(1<<44) for v in x["rows"]) or
                any(type(x[k]) is not int or not 0<=x[k]<=MAX_UPDATES
                    for k in ("rank","examples","conflicts","phase")) or
                x["rank"]>36 or x["phase"]>5 or
                sum(bool(v) for v in x["rows"])!=x["rank"] or
                any(row and ((row&MASK)&-(row&MASK)).bit_length()-1!=j
                    for j,row in enumerate(x["rows"])) or
                (x["rotation"] is not None and
                 (type(x["rotation"]) is not int or
                  x["rotation"] not in (1,2,3))) or
                any(x[k] is not None and
                    (type(x[k]) is not int or x[k] not in range(256))
                    for k in ("maskA","maskB"))):
                raise ValueError("ST7_GAUSSIAN_BAD_STATE")
            m=cls()
            for key in keys-{"schema"}:
                setattr(m,key,x[key])
            if m.snapshot()!=raw:
                raise ValueError("ST7_GAUSSIAN_NONCANONICAL_STATE")
            return m
        except (TypeError,KeyError,OverflowError) as ex:
            raise ValueError("ST7_GAUSSIAN_COLD_FAILURE") from ex

    def accounting(self):
        return {
            "GF2_learned_rows":36,
            "learned_bit_budget":36*44,
            "minimum_packed_learned_bytes":216,
            "64bit_aligned_learned_bytes":288,
            "checkpoint_serialized_bytes":len(self.snapshot().encode("utf-8")),
            "private_coefficient_or_law_seen":False
        }


class Logistic36:
    """Genuinely fitted 36-feature eight-output logistic conventional model."""
    def __init__(self):
        self.weights=[[0.0]*FEATURES for _ in range(8)]
        self.rotation=None
        self.maskA=None
        self.maskB=None
        self.phase=0
        self.fitted=0

    def reset_episode(self):
        self.rotation=None;self.maskA=None;self.maskB=None;self.phase=0

    @staticmethod
    def _sigmoid(v):
        v=max(-18.,min(18.,v))
        return 1./(1.+math.exp(-v))

    def predict(self,public,action):
        x=pack(public)
        if type(action) is not int or self.phase>=5 or action!=ACTIONS[self.phase]:
            raise ValueError("ST7_LOGISTIC_PUBLIC_ACTION_ORDER")
        if self.phase!=4 or None in (self.rotation,self.maskA,self.maskB):
            return [.5]*8
        f=terms(self.maskB)
        outcome_mask=x^rot(x,self.rotation)^self.maskA
        ps=[]
        for k in range(8):
            z=sum(self.weights[k][j]*value for j,value in enumerate(f))
            q=self._sigmoid(z)
            if (outcome_mask>>k)&1:q=1.-q
            ps.append(q)
        return ps

    def observe(self,public,action,target,after,*,train=True):
        x,y=check_transition(public,action,target,after,self.phase,train)
        predicted=self.predict(public,action)
        if self.phase==0:
            valid=[k for k in (1,2,3) if rot(x,k)==y]
            self.rotation=valid[0] if len(valid)==1 else None
        elif self.phase==1 and self.rotation is not None:
            self.maskA=y^rot(x,self.rotation)
        elif self.phase==2 and self.rotation is not None:
            self.maskB=y^rot(x,self.rotation)
        elif self.phase==4 and train and None not in (
            self.rotation,self.maskA,self.maskB
        ):
            f=terms(self.maskB)
            outcome=y^rot(x,self.rotation)^self.maskA
            # Fixed four fully executed updates, no held-loss tuning.
            for _ in range(4):
                for k in range(8):
                    z=sum(w*t for w,t in zip(self.weights[k],f))
                    residual=((outcome>>k)&1)-self._sigmoid(z)
                    for j,v in enumerate(f):
                        if v:
                            self.weights[k][j]=max(-12.,min(12.,
                                self.weights[k][j]+.03*residual))
            self.fitted+=1
        self.phase+=1
        return predicted

    def snapshot(self):
        return canonical({
            "schema":LOGISTIC_SCHEMA,"weights":self.weights,
            "rotation":self.rotation,"maskA":self.maskA,
            "maskB":self.maskB,"phase":self.phase,
            "fitted":self.fitted
        })

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw)>30000:
            raise ValueError("ST7_LOGISTIC_CHECKPOINT_SIZE")
        try:
            x=json.loads(raw)
            keys={"schema","weights","rotation","maskA","maskB","phase","fitted"}
            if (type(x) is not dict or set(x)!=keys or
                x["schema"]!=LOGISTIC_SCHEMA or
                type(x["weights"]) is not list or len(x["weights"])!=8 or
                any(type(row) is not list or len(row)!=FEATURES for row in x["weights"]) or
                any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>12.01
                    for row in x["weights"] for v in row) or
                any(type(x[k]) is not int or not 0<=x[k]<=MAX_UPDATES
                    for k in ("phase","fitted")) or x["phase"]>5 or
                (x["rotation"] is not None and
                 (type(x["rotation"]) is not int or x["rotation"] not in (1,2,3))) or
                any(x[k] is not None and
                    (type(x[k]) is not int or x[k] not in range(256))
                    for k in ("maskA","maskB"))):
                raise ValueError("ST7_LOGISTIC_BAD_CHECKPOINT")
            m=cls()
            for k in keys-{"schema"}:
                setattr(m,k,x[k])
            if m.snapshot()!=raw:
                raise ValueError("ST7_LOGISTIC_NONCANONICAL_STATE")
            return m
        except (TypeError,KeyError,OverflowError) as e:
            raise ValueError("ST7_LOGISTIC_COLD_RESTORE_FAILURE") from e

    def accounting(self):
        return {
            "trained_float_parameters":8*36,
            "SGD_updates_per_original_training_probe":4,
            "checkpoint_serialized_bytes":len(self.snapshot().encode("utf-8")),
            "private_source_coefficient_or_law_seen":False
        }


def models():
    from research.nci04_st7.native_induction import NativeInductive8
    return {
        "candidate":NativeInductive8("causal"),
        "gf2_conventional":GF2Conventional(),
        "logistic36":Logistic36(),
        "st6_menu":NativeOperator8("causal"),
        "linear_only":NativeInductive8("linear_only"),
        "no_b":NativeInductive8("no_b"),
        "erase":NativeInductive8("erase")
    }


def restore_one(name,raw):
    from research.nci04_st7.native_induction import NativeInductive8
    if name=="gf2_conventional":return GF2Conventional.restore(raw)
    if name=="logistic36":return Logistic36.restore(raw)
    if name=="st6_menu":
        m=NativeOperator8.restore(raw)
        if m.variant!="causal":raise ValueError("ST7_WRONG_ST6_MENU_CONTROL")
        return m
    m=NativeInductive8.restore(raw)
    if m.variant!=("causal" if name=="candidate" else name):
        raise ValueError("ST7_WRONG_NATIVE_ABLATION")
    return m


def restored_models(blobs):
    expected=set(models())
    if type(blobs) is not dict or set(blobs)!=expected:
        raise ValueError("ST7_MISSING_COMMON_TRAINED_MODEL")
    out={name:restore_one(name,raw) for name,raw in blobs.items()}
    if any(out[n].snapshot()!=blobs[n] for n in out):
        raise ValueError("ST7_FROZEN_CHECKPOINT_NOT_EXACT")
    return out
