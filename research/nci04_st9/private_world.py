"""Private original ST9 four-bit-action / eight-bit causal consequence world.

Each two-action episode performs (0) genuine neutral rotation to identify
the public local dynamics and (1..16) an actual player-chosen intervention.
A candidate never imports this file's coefficient generator or law ID.
Effects are NOT returned until the original step actually executes.

The eight hidden output coefficients per bit are deliberately NOT a menu
of possible correct rules exposed to model construction.
"""
from hashlib import sha256
import json

ACTIONS=tuple(range(17))
SCHEMA="yggdrasil.nci04.st9.private-two-action-gf2-world.v1"
NEG_LAWS=(43,47)


def H(t):
    if type(t) is not str:raise ValueError("ST9_PRIVATE_HASH_INPUT")
    return sha256(t.encode("utf-8")).digest()


def bits(x):
    if type(x) is not int or x not in range(256):
        raise ValueError("ST9_PUBLIC_INVALID_BYTE")
    return tuple((x>>j)&1 for j in range(8))


def pack(xs):
    if (type(xs) not in (tuple,list) or len(xs)!=8 or
        any(type(x) is not int or x not in (0,1) for x in xs)):
        raise ValueError("ST9_PUBLIC_INVALID_BITS")
    return sum(z<<j for j,z in enumerate(xs))


def rol(x,r):
    if (type(x) is not int or x not in range(256) or
        type(r) is not int or r not in (1,2,3)):
        raise ValueError("ST9_PUBLIC_INVALID_ROTATION")
    return ((x<<r)|(x>>(8-r)))&255


def F(B,degree=2):
    if (type(B) is not int or B not in range(16) or
        type(degree) is not int or degree not in (1,2)):
        raise ValueError("ST9_ORIGINAL_INVALID_ACTION_FEATURE")
    x=[(B>>j)&1 for j in range(4)]
    terms=list(x)
    if degree==2:
        terms.extend((x[0]&x[1],x[1]&x[2],x[2]&x[3],x[3]&x[0]))
    return sum(v<<j for j,v in enumerate(terms))


def source_coefficients(alt=False):
    domain="ST9-alt" if alt else "ST9-rule"
    return tuple(
        sum((H(domain+"|"+str(j)+"|"+str(k))[0]&1)<<k
            for k in range(8))
        for j in range(8)
    )


def effect(B,alt=False):
    x=F(B,2);rows=source_coefficients(alt)
    y=sum(((x&row).bit_count()&1)<<j for j,row in enumerate(rows))
    if alt:
        b=[(B>>k)&1 for k in range(4)]
        y^=b[0]&b[1]&b[2]
    return y


def rotation(law):
    if type(law) is not int or law<0:
        raise ValueError("ST9_SOURCE_LAW_INVALID")
    return 1+H("ST9-r|"+str(law))[0]%3


def initial(seed,trial):
    if (type(seed) is not int or seed<0 or
        type(trial) is not int or not 0<=trial<32):
        raise ValueError("ST9_SOURCE_INITIAL_SCOPE_INVALID")
    for nonce in range(256):
        x=H("ST9-x|"+str(seed)+"|"+str(trial)+"|"+str(nonce))[0]
        if len({rol(x,r) for r in (1,2,3)})==3:
            return x
    raise ValueError("ST9_SOURCE_INITIAL_PUBLIC_ROTATION_ALIAS")


class PrivateWorld:
    __slots__=("_law","_rotation","_x","_step")

    def __init__(self,law,seed,trial):
        self._law=law
        self._rotation=rotation(law)
        self._x=initial(seed,trial)
        self._step=0

    def public(self):
        return bits(self._x)

    def step(self,action):
        if (type(action) is not int or action not in ACTIONS or
            self._step>=2 or
            (self._step==0 and action!=0) or
            (self._step==1 and not 1<=action<=16)):
            raise ValueError("ST9_SOURCE_FORBIDDEN_OR_OUT_OF_ORDER_ACTION")
        pre=self._x
        B=action-1 if self._step==1 else 0
        y=rol(pre,self._rotation)
        if self._step==1:
            y^=effect(B,self._law in NEG_LAWS)
        self._x=y
        self._step+=1
        return bits(y),bits(pre^y)

    def snapshot(self):
        return json.dumps({
            "schema":SCHEMA,"law":self._law,
            "rotation":self._rotation,"x":self._x,"step":self._step
        },sort_keys=True,separators=(",",":"),allow_nan=False)

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw)>700:
            raise ValueError("ST9_PRIVATE_COLD_SIZE")
        try:
            x=json.loads(raw)
            keys={"schema","law","rotation","x","step"}
            if (type(x) is not dict or set(x)!=keys or x["schema"]!=SCHEMA or
                any(type(x[k]) is not int for k in keys-{"schema"}) or
                x["law"]<0 or x["rotation"] not in (1,2,3) or
                x["x"] not in range(256) or x["step"] not in (0,1,2)):
                raise ValueError("ST9_PRIVATE_COLD_SHAPE")
            m=cls(x["law"],100,0)
            m._rotation=x["rotation"];m._x=x["x"];m._step=x["step"]
            if m.snapshot()!=raw:
                raise ValueError("ST9_PRIVATE_COLD_NONCANONICAL")
            return m
        except (TypeError,KeyError,ValueError,OverflowError) as e:
            raise ValueError("ST9_PRIVATE_COLD_RESTORE_REJECTED") from e


def original_episode(law,seed,trial,B):
    if type(B) is not int or B not in range(16):
        raise ValueError("ST9_SOURCE_PROBE_INVALID")
    env=PrivateWorld(law,seed,trial)
    out=[]
    for action in (0,B+1):
        before=env.public()
        after,delta=env.step(action)
        if delta!=tuple(a^b for a,b in zip(before,after)):
            raise ValueError("ST9_REAL_PUBLIC_CONSEQUENCE_MISMATCH")
        out.append((before,action,after,delta))
    return out
