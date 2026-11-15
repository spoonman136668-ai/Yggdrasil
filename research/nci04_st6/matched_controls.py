"""ST6 independent strong symbolic composition selector and old controls.

The separate symbolic selector is a conventional task-aware competitor
using EXACT same eight operation priors, public diagnostic experiences
and 64 learned evidence bytes as ST6 native. A tie means composition is
achievable by conventional program selection, NOT uniquely native.
The old ST5 tokenless law-key memory and 45-weight trained recurrent are
imported without modification as deliberate transfer/learning controls.
"""
import json

from research.nci04_st5.native_memory import NativeCausalRecall8
from research.nci04_st5.matched_controls import Recurrent45,brier

SCHEMA="yggdrasil.nci04.st6.trained-symbolic-menu.v1"
K=8
ACTOR=(3,0,1,2,3)
MAX=2**31-1


def _bits(x):
    if (type(x) not in (list,tuple) or len(x)!=8 or
        any(type(t) is not int or t not in (0,1) for t in x)):
        raise ValueError("ST6_SYMBOLIC_BAD_PUBLIC")
    return sum(t<<j for j,t in enumerate(x))


def _rot(x,k):
    if type(x) is not int or x not in range(256) or type(k) is not int or k not in (1,2,3,7):
        raise ValueError("ST6_SYMBOLIC_BAD_ROTATE")
    return ((x<<k)|(x>>(8-k)))&255


def _options(a,b):
    if type(a) is not int or type(b) is not int or a not in range(256) or b not in range(256):
        raise ValueError("ST6_SYMBOLIC_BAD_ACTUATOR_EVIDENCE")
    # Intentionally independent of native_operator.py and source.
    return (a^_rot(b,1),a^b,a|b,a&b,(a+b)&255,
            a^_rot(b,2),a&(~b&255),a^_rot(b,7))


def _canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)


class SymbolicSelector:
    def __init__(self):
        self.loss=[0]*K
        self.samples=[0]*K
        self.rotation=None
        self.mask_a=None
        self.mask_b=None
        self.phase=0
        self.fitted=0

    def reset_episode(self):
        self.rotation=None
        self.mask_a=None
        self.mask_b=None
        self.phase=0

    def predict(self,public,action):
        x=_bits(public)
        if type(action) is not int or self.phase>=5 or action!=ACTOR[self.phase]:
            raise ValueError("ST6_SYMBOLIC_ACTOR_DRIFT")
        if self.phase!=4 or None in (
            self.rotation,self.mask_a,self.mask_b
        ) or not any(self.samples):
            return [.5]*8
        best=min(range(K),key=lambda j:(self.loss[j],j))
        predicted_g=_options(self.mask_a,self.mask_b)[best]
        delta=x^_rot(x,self.rotation)^predicted_g
        confidence=min(.99,(self.samples[best]+1)/(self.samples[best]+2))
        return [
            confidence if ((delta>>i)&1) else 1.-confidence
            for i in range(8)
        ]

    def observe(self,public,action,target,after,*,train=True):
        x=_bits(public);y=_bits(after)
        t=_bits(target)
        if (type(train) is not bool or
            type(action) is not int or self.phase>=5 or
            action!=ACTOR[self.phase] or x^y!=t):
            raise ValueError("ST6_SYMBOLIC_UNAUTHENTIC_PUBLIC_SOURCE")
        pred=self.predict(public,action)
        if self.phase==0:
            possible=[r for r in (1,2,3) if _rot(x,r)==y]
            self.rotation=possible[0] if len(possible)==1 else None
        elif self.phase==1 and self.rotation is not None:
            self.mask_a=y^_rot(x,self.rotation)
        elif self.phase==2 and self.rotation is not None:
            self.mask_b=y^_rot(x,self.rotation)
        elif self.phase==4 and train and None not in (
            self.rotation,self.mask_a,self.mask_b
        ):
            actual=y^_rot(x,self.rotation)
            choices=_options(self.mask_a,self.mask_b)
            if any(k>MAX-8 for k in self.samples):
                self.loss=[k//2 for k in self.loss]
                self.samples=[k//2 for k in self.samples]
            for j,v in enumerate(choices):
                self.loss[j]+=(actual^v).bit_count()
                self.samples[j]+=8
            self.fitted+=1
        self.phase+=1
        return pred

    def snapshot(self):
        return _canonical({
            "schema":SCHEMA,"loss":self.loss,"samples":self.samples,
            "rotation":self.rotation,"mask_a":self.mask_a,
            "mask_b":self.mask_b,"phase":self.phase,"fitted":self.fitted
        })

    @classmethod
    def restore(cls,payload):
        if type(payload) is not str or len(payload)>3000:
            raise ValueError("ST6_SYMBOLIC_CHECKPOINT_LENGTH")
        try:
            d=json.loads(payload)
            expected={"schema","loss","samples","rotation","mask_a",
                      "mask_b","phase","fitted"}
            if (type(d) is not dict or set(d)!=expected or
                d["schema"]!=SCHEMA or
                any(type(d[key]) is not list or len(d[key])!=K or
                    any(type(v) is not int or not 0<=v<=MAX for v in d[key])
                    for key in ("loss","samples")) or
                any(x>n for x,n in zip(d["loss"],d["samples"])) or
                (d["rotation"] is not None and
                 (type(d["rotation"]) is not int or d["rotation"] not in (1,2,3))) or
                any(d[k] is not None and
                    (type(d[k]) is not int or d[k] not in range(256))
                    for k in ("mask_a","mask_b")) or
                any(type(d[k]) is not int or not 0<=d[k]<=MAX
                    for k in ("phase","fitted")) or d["phase"]>5):
                raise ValueError("ST6_SYMBOLIC_CHECKPOINT_SHAPE")
            m=cls()
            m.loss=d["loss"];m.samples=d["samples"]
            m.rotation=d["rotation"];m.mask_a=d["mask_a"]
            m.mask_b=d["mask_b"];m.phase=d["phase"];m.fitted=d["fitted"]
            if m.snapshot()!=payload:
                raise ValueError("ST6_SYMBOLIC_CHECKPOINT_NOT_CANONICAL")
            return m
        except (TypeError,KeyError,OverflowError) as ex:
            raise ValueError("ST6_SYMBOLIC_RESTORE_FAILED") from ex

    def accounting(self):
        return {
            "learned_uint32_error_support_bytes":K*2*4,
            "fixed_task_aligned_operator_menu":8,
            "checkpoint_json_bytes":len(self.snapshot().encode("utf-8")),
            "private_law_or_source_access":False
        }


def create_models():
    from research.nci04_st6.native_operator import NativeOperator8
    return {
        "candidate":NativeOperator8("causal"),
        "symbolic8":SymbolicSelector(),
        "st5_exact_key":NativeCausalRecall8("causal"),
        "recurrent45":Recurrent45(),
        "no_b":NativeOperator8("no_b"),
        "shuffle":NativeOperator8("shuffle"),
        "erase":NativeOperator8("erase")
    }


def restore_one(name,payload):
    from research.nci04_st6.native_operator import NativeOperator8
    if name=="symbolic8":return SymbolicSelector.restore(payload)
    if name=="st5_exact_key":
        x=NativeCausalRecall8.restore(payload)
        if x.variant!="causal":raise ValueError("ST6_WRONG_FROZEN_ST5_CONTROL")
        return x
    if name=="recurrent45":return Recurrent45.restore(payload)
    x=NativeOperator8.restore(payload)
    expected="causal" if name=="candidate" else name
    if x.variant!=expected:raise ValueError("ST6_WRONG_NATIVE_ABLATION")
    return x


def restored_models(blobs):
    expected=set(create_models())
    if type(blobs) is not dict or set(blobs)!=expected:
        raise ValueError("ST6_INCOMPLETE_ORIGINAL_TRAINED_COHORT")
    models={name:restore_one(name,blob) for name,blob in blobs.items()}
    if any(models[n].snapshot()!=blobs[n] for n in models):
        raise ValueError("ST6_CHECKPOINT_BYTES_NOT_RESTORED")
    return models
