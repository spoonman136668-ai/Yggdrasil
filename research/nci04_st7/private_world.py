"""ST7 original private quadratic Boolean causal-rule world (in-house DEV).

Learners NEVER access this module's private true coefficient rows or law
identity. The observer sees real 8-bit states, announced action, and
genuine afteraction public changes, with the delayed consequence of
action2 only emerging on the later neutral action3.

The true operator is NOT a named/encoded menu choice in the learner:
it is a private 8x36 GF(2) coefficient matrix sampled from SHA256.
The model is told only a general quadratic feature basis, not coefficients.
"""
from hashlib import sha256
import json

SCHEMA="yggdrasil.nci04.st7.private-unknown-quadratic-world.v1"
ACTIONS=(3,0,1,2,3)
TRIALS=16
NEG_LAWS=(43,47)
NFEAT=36
MASK36=(1<<NFEAT)-1


def digest(x):
    if type(x) is not str:
        raise ValueError("ST7_ORIGINAL_INVALID_HASH_ARGUMENT")
    return sha256(x.encode("utf-8")).digest()


def byte_to_bits(x):
    if type(x) is not int or x not in range(256):
        raise ValueError("ST7_ORIGINAL_BAD_BYTE")
    return tuple((x>>j)&1 for j in range(8))


def public_byte(seq):
    if (type(seq) not in (tuple,list) or len(seq)!=8 or
        any(type(k) is not int or k not in (0,1) for k in seq)):
        raise ValueError("ST7_ORIGINAL_BAD_PUBLIC")
    return sum(v<<i for i,v in enumerate(seq))


def rol(x,shift):
    if (type(x) is not int or x not in range(256) or
        type(shift) is not int or shift not in (1,2,3)):
        raise ValueError("ST7_ORIGINAL_BAD_ROTATION")
    return ((x<<shift)|(x>>(8-shift)))&255


def features(B):
    if type(B) is not int or B not in range(256):
        raise ValueError("ST7_ORIGINAL_BAD_PUBLIC_COMPONENT")
    vals=[(B>>j)&1 for j in range(8)]
    vals.extend(vals[i]&vals[j] for i in range(8) for j in range(i+1,8))
    if len(vals)!=36:
        raise ValueError("ST7_ORIGINAL_INVALID_FEATURE_BASIS")
    return sum(v<<j for j,v in enumerate(vals))


def private_coefficient_rows(alt=False):
    domain="ST7-unknown-alternate" if alt else "ST7-rule"
    rows=[]
    for output in range(8):
        row=0
        for feat in range(NFEAT):
            v=digest(domain+"|output="+str(output)+"|feature="+str(feat))[0]&1
            row|=v<<feat
        rows.append(row)
    return tuple(rows)


def quadratic(B,alt=False):
    f=features(B)
    rows=private_coefficient_rows(alt)
    result=sum(((f&row).bit_count()&1)<<i for i,row in enumerate(rows))
    if alt:
        result^=B&rol(B,1)&rol(B,2)
    return result


def private_params(law,seed,trial):
    if (type(law) is not int or law<0 or
        type(seed) is not int or seed<0 or
        type(trial) is not int or trial not in range(TRIALS)):
        raise ValueError("ST7_ORIGINAL_PRIVATE_SCOPE_INVALID")
    s="|"+str(law)+"|"+str(seed)+"|"+str(trial)
    return (1+digest("ST7-rotation|"+str(law))[0]%3,
            digest("ST7-a"+s)[0],
            digest("ST7-b"+s)[0])


def initial_public(seed,trial):
    if (type(seed) is not int or seed<0 or
        type(trial) is not int or trial not in range(TRIALS)):
        raise ValueError("ST7_ORIGINAL_INITIAL_SCOPE")
    for nonce in range(256):
        x=digest("ST7-state|"+str(seed)+"|"+str(trial)+"|"+str(nonce))[0]
        if len({rol(x,k) for k in (1,2,3)})==3:
            return x
    raise ValueError("ST7_ORIGINAL_NO_IDENTIFIABLE_INITIAL_STATE")


def diagnostic_from_public(history):
    if type(history) not in (tuple,list) or len(history)<3:
        return None
    a,b,c=history[:3]
    if (a[1],b[1],c[1])!=(3,0,1):
        raise ValueError("ST7_ORIGINAL_PUBLIC_DIAGNOSTIC_ORDER")
    x=public_byte(a[0]);y=public_byte(a[2])
    opts=[r for r in (1,2,3) if rol(x,r)==y]
    if len(opts)!=1:
        return None
    r=opts[0]
    maskA=public_byte(b[2])^rol(public_byte(b[0]),r)
    maskB=public_byte(c[2])^rol(public_byte(c[0]),r)
    return r,maskA,maskB


class PrivateQuadraticWorld:
    __slots__=("_law","_r","_a","_b","_x","_pending","_step")

    def __init__(self,law,seed,trial):
        r,a,b=private_params(law,seed,trial)
        self._law=law
        self._r=r
        self._a=a
        self._b=b
        self._x=initial_public(seed,trial)
        self._pending=0
        self._step=0

    def public(self):
        return byte_to_bits(self._x)

    def step(self,act):
        if type(act) is not int or act not in (0,1,2,3):
            raise ValueError("ST7_ORIGINAL_BAD_ACTION")
        if self._step>=len(ACTIONS) or act!=ACTIONS[self._step]:
            raise ValueError("ST7_ORIGINAL_SOURCE_ACTION_SEQUENCE")
        x=self._x
        immediate=self._a if act==0 else self._b if act==1 else 0
        after=rol(x,self._r)^immediate^self._pending
        self._pending=(
            self._a^quadratic(self._b,self._law in NEG_LAWS)
            if act==2 else 0
        )
        self._x=after
        self._step+=1
        return byte_to_bits(after),byte_to_bits(x^after)

    def snapshot(self):
        return json.dumps({
            "schema":SCHEMA,"law":self._law,
            "r":self._r,"a":self._a,"b":self._b,
            "x":self._x,"pending":self._pending,"step":self._step
        },sort_keys=True,separators=(",",":"),allow_nan=False)

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw)>1200:
            raise ValueError("ST7_ORIGINAL_BAD_COLD_SNAPSHOT_LENGTH")
        try:
            x=json.loads(raw)
            keys={"schema","law","r","a","b","x","pending","step"}
            if (type(x) is not dict or set(x)!=keys or x["schema"]!=SCHEMA or
                any(type(x[k]) is not int for k in keys-{"schema"}) or
                x["law"]<0 or x["r"] not in (1,2,3) or
                any(x[k] not in range(256) for k in ("a","b","x","pending")) or
                x["step"] not in range(6)):
                raise ValueError("ST7_ORIGINAL_COLD_SHAPE_BAD")
            obj=cls(x["law"],100,0)
            for key in keys-{"schema","law"}:
                setattr(obj,"_"+key,x[key])
            if obj.snapshot()!=raw:
                raise ValueError("ST7_ORIGINAL_COLD_CANONICAL_BAD")
            return obj
        except (ValueError,TypeError,KeyError,OverflowError) as exc:
            raise ValueError("ST7_ORIGINAL_COLD_INVALID") from exc


def original_episode(law,seed,trial):
    world=PrivateQuadraticWorld(law,seed,trial)
    trace=[]
    for action in ACTIONS:
        before=world.public()
        after,target=world.step(action)
        if tuple(a^b for a,b in zip(before,after))!=target:
            raise ValueError("ST7_ORIGINAL_PUBLIC_CONSEQUENCE_UNAUTHENTIC")
        trace.append((before,action,after,target))
    return trace,diagnostic_from_public(trace)
