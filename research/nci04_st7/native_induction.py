"""ST7 native tokenless eight-cell quadratic causal constraint learner.

Learns 36 unknown Boolean feature coefficients for 8 public result bits
from real intervention consequences, using bounded GF(2) constraints.
No predefined true operator outputs, private source calls or law IDs.
This is a deliberate 36-feature polynomial family prior, NOT general
physics discovery. Strong conventional parity control is mandatory.
"""
import json

SCHEMA="yggdrasil.nci04.st7.native-quadratic8.v1"
ACTIONS=(3,0,1,2,3)
FEATURES=36
MASK=(1<<FEATURES)-1
MAX_UPDATES=10**8
VARIANTS=("causal","linear_only","no_b","erase")


def canonical(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),allow_nan=False)


def packed(v):
    if (type(v) not in (tuple,list) or len(v)!=8 or
        any(type(x) is not int or x not in (0,1) for x in v)):
        raise ValueError("ST7_NATIVE_INVALID_PUBLIC")
    return sum(x<<i for i,x in enumerate(v))


def rol(x,k):
    if type(x) is not int or x not in range(256) or type(k) is not int or k not in (1,2,3):
        raise ValueError("ST7_NATIVE_INVALID_ROTATION")
    return ((x<<k)|(x>>(8-k)))&255


def quadratic_features(component):
    if type(component) is not int or component not in range(256):
        raise ValueError("ST7_NATIVE_BAD_PUBLIC_COMPONENT")
    bits=[(component>>i)&1 for i in range(8)]
    monomials=bits+[
        bits[i]&bits[j] for i in range(8) for j in range(i+1,8)
    ]
    if len(monomials)!=FEATURES:
        raise ValueError("ST7_NATIVE_WRONG_QUADRATIC_FEATURES")
    return sum(x<<k for k,x in enumerate(monomials))


class NativeInductive8:
    def __init__(self,variant="causal"):
        if variant not in VARIANTS:
            raise ValueError("ST7_NATIVE_UNKNOWN_ABLATION")
        self.variant=variant
        self.basis=[0]*FEATURES
        self.rank=0
        self.updates=0
        self.conflicts=0
        self.rotation=None
        self.a=None
        self.b=None
        self.step=0

    def reset_episode(self):
        if self.variant=="erase":
            self.basis=[0]*FEATURES
            self.rank=0
        self.rotation=None
        self.a=None
        self.b=None
        self.step=0

    def _features(self):
        if self.b is None:
            return None
        component=0 if self.variant=="no_b" else self.b
        f=quadratic_features(component)
        return f&255 if self.variant=="linear_only" else f

    def _reduce(self,f,output=0):
        row=f|(output<<FEATURES)
        while row&MASK:
            pivot=(row&MASK).bit_length()-1
            if self.basis[pivot]:
                row^=self.basis[pivot]
            else:
                return (False,pivot,row)
        return (True,None,(row>>FEATURES)&255)

    def predict(self,public,action):
        x=packed(public)
        if (type(action) is not int or action not in (0,1,2,3) or
            self.step>=5 or action!=ACTIONS[self.step]):
            raise ValueError("ST7_NATIVE_PREDICTION_ACTION_ORDER")
        if self.step!=4 or None in (self.rotation,self.a,self.b):
            return [.5]*8
        f=self._features()
        known,_,out=self._reduce(f)
        if not known:
            return [.5]*8
        predicted=x^rol(x,self.rotation)^self.a^out
        return [(.99 if (predicted>>i)&1 else .01) for i in range(8)]

    def observe(self,public,action,target,after,*,train=True):
        x=packed(public)
        y=packed(after)
        t=packed(target)
        if (type(train) is not bool or type(action) is not int or
            self.step>=5 or action!=ACTIONS[self.step] or x^y!=t):
            raise ValueError("ST7_NATIVE_UNAUTHENTIC_PUBLIC_ACTION")
        forecast=self.predict(public,action)
        if self.step==0:
            opts=[k for k in (1,2,3) if rol(x,k)==y]
            self.rotation=opts[0] if len(opts)==1 else None
        elif self.step==1 and self.rotation is not None:
            self.a=y^rol(x,self.rotation)
        elif self.step==2 and self.rotation is not None:
            self.b=y^rol(x,self.rotation)
        elif self.step==4 and train and None not in (
            self.rotation,self.a,self.b
        ):
            if self.updates>=MAX_UPDATES:
                raise ValueError("ST7_NATIVE_BOUNDED_LEARNING_LIMIT")
            expected_output=y^rol(x,self.rotation)^self.a
            f=self._features()
            known,pivot,reduced=self._reduce(f,expected_output)
            if pivot is not None:
                self.basis[pivot]=reduced
                self.rank+=1
            elif reduced:
                self.conflicts+=1
            self.updates+=1
        self.step+=1
        return forecast

    def snapshot(self):
        return canonical({
            "schema":SCHEMA,"variant":self.variant,
            "basis":self.basis,"rank":self.rank,
            "updates":self.updates,"conflicts":self.conflicts,
            "rotation":self.rotation,"a":self.a,"b":self.b,
            "step":self.step
        })

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw)>7000:
            raise ValueError("ST7_NATIVE_COLD_SIZE")
        try:
            x=json.loads(raw)
            keys={"schema","variant","basis","rank","updates",
                  "conflicts","rotation","a","b","step"}
            if (type(x) is not dict or set(x)!=keys or
                x["schema"]!=SCHEMA or x["variant"] not in VARIANTS or
                type(x["basis"]) is not list or len(x["basis"])!=FEATURES or
                any(type(row) is not int or not 0<=row<(1<<(FEATURES+8))
                    for row in x["basis"]) or
                any(type(x[k]) is not int or not 0<=x[k]<=MAX_UPDATES
                    for k in ("rank","updates","conflicts","step")) or
                x["rank"]>FEATURES or x["step"]>5 or
                (x["rotation"] is not None and
                 (type(x["rotation"]) is not int or
                  x["rotation"] not in (1,2,3))) or
                any(x[k] is not None and
                    (type(x[k]) is not int or x[k] not in range(256))
                    for k in ("a","b")) or
                sum(row!=0 for row in x["basis"])!=x["rank"] or
                any(row and (row&MASK).bit_length()-1!=i
                    for i,row in enumerate(x["basis"]))):
                raise ValueError("ST7_NATIVE_COLD_STATE_INVALID")
            m=cls(x["variant"])
            for k in keys-{"schema","variant"}:
                setattr(m,k,x[k])
            if m.snapshot()!=raw:
                raise ValueError("ST7_NATIVE_NONCANONICAL_COLD")
            return m
        except (TypeError,KeyError,OverflowError) as e:
            raise ValueError("ST7_NATIVE_COLD_RESTORE_FAILED") from e

    def accounting(self):
        return {
            "native_causal_cells":8,
            "Boolean_polynomial_feature_priors":36,
            "learned_GF2_augmented_matrix_rows":36,
            "learned_bit_budget":36*(36+8),
            "minimum_packed_learned_bytes":36*6,
            "64bit_aligned_learned_bytes":36*8,
            "checkpoint_serialized_bytes":len(self.snapshot().encode("utf-8")),
            "source_private_law_or_coefficient_seen":False,
            "number_fixed_correct_hypothesis_menu_entries":0,
            "integer_only_cold_state":True
        }
