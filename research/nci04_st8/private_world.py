"""Private in-house ST8 real five-action unknown CUBIC causal environment.

The correct 8x92 coefficients are NEVER exposed to any learner. This is
an original deterministic source to falsify an existing quadratic
representation, not an independent scientific environment.
"""
from hashlib import sha256
import json

SCHEMA="yggdrasil.nci04.st8.private-cubic-intervention-world.v1"
ACTIONS=(3,0,1,2,3)
NFEAT=92
TRIALS=16
NEG_LAWS=(43,47)


def digest(text):
    if type(text) is not str:
        raise ValueError("ST8_ORIGINAL_BAD_HASH_ARGUMENT")
    return sha256(text.encode("utf-8")).digest()


def bits(x):
    if type(x) is not int or x not in range(256):
        raise ValueError("ST8_ORIGINAL_INVALID_BYTE")
    return tuple((x>>k)&1 for k in range(8))


def pack(xs):
    if (type(xs) not in (tuple,list) or len(xs)!=8 or
        any(type(x) is not int or x not in (0,1) for x in xs)):
        raise ValueError("ST8_ORIGINAL_BAD_PUBLIC_BITS")
    return sum(v<<k for k,v in enumerate(xs))


def rol(x,k):
    if (type(x) is not int or x not in range(256) or
        type(k) is not int or k not in (1,2,3)):
        raise ValueError("ST8_ORIGINAL_BAD_ROTATION")
    return ((x<<k)|(x>>(8-k)))&255


def monomials(B,degree=3):
    if (type(B) is not int or B not in range(256) or
        type(degree) is not int or degree not in (2,3)):
        raise ValueError("ST8_ORIGINAL_BAD_MONOMIAL_REQUEST")
    v=[(B>>i)&1 for i in range(8)]
    basis=list(v)
    basis.extend(v[i]&v[j] for i in range(8) for j in range(i+1,8))
    if degree==3:
        basis.extend(v[i]&v[j]&v[k] for i in range(8)
                     for j in range(i+1,8) for k in range(j+1,8))
    assert len(basis)==(92 if degree==3 else 36)
    return sum(value<<index for index,value in enumerate(basis))


def coefficient_rows(*,negative=False):
    prefix="ST8-negative" if negative else "ST8-cubic"
    return tuple(
        sum((digest(prefix+"|"+str(output)+"|"+str(feature))[0]&1)<<feature
            for feature in range(NFEAT))
        for output in range(8)
    )


def effect(B,*,negative=False):
    F=monomials(B)
    rows=coefficient_rows(negative=negative)
    out=sum(((F&row).bit_count()&1)<<k for k,row in enumerate(rows))
    if negative:
        out^=(B&1)&((B>>1)&1)&((B>>2)&1)&((B>>3)&1)
    return out


def private_params(law,seed,trial):
    if (type(law) is not int or law<0 or
        type(seed) is not int or seed<0 or
        type(trial) is not int or trial not in range(TRIALS)):
        raise ValueError("ST8_PRIVATE_SCOPE_INVALID")
    suffix="|"+str(law)+"|"+str(seed)+"|"+str(trial)
    r=1+digest("ST8-r|"+str(law))[0]%3
    A=digest("ST8-A"+suffix)[0]
    B=digest("ST8-B"+suffix)[0]
    return r,A,B


def initial(seed,trial):
    if (type(seed) is not int or seed<0 or
        type(trial) is not int or trial not in range(TRIALS)):
        raise ValueError("ST8_INITIAL_SCOPE_INVALID")
    for nonce in range(256):
        x=digest("ST8-x0|"+str(seed)+"|"+str(trial)+"|"+str(nonce))[0]
        if len({rol(x,k) for k in (1,2,3)})==3:
            return x
    raise ValueError("ST8_INITIAL_PUBLIC_ROTATION_UNIDENTIFIABLE")


def public_cue(events):
    if type(events) not in (tuple,list) or len(events)<3:
        return None
    a,b,c=events[:3]
    if (a[1],b[1],c[1])!=(3,0,1):
        raise ValueError("ST8_PUBLIC_ACTOR_DRIFT")
    x=pack(a[0]);y=pack(a[2])
    found=[r for r in (1,2,3) if rol(x,r)==y]
    if len(found)!=1:
        return None
    r=found[0]
    A=pack(b[2])^rol(pack(b[0]),r)
    B=pack(c[2])^rol(pack(c[0]),r)
    return r,A,B


class PrivateCubicWorld:
    __slots__=("_law","_r","_A","_B","_x","_pending","_step")

    def __init__(self,law,seed,trial):
        self._law=law
        self._r,self._A,self._B=private_params(law,seed,trial)
        self._x=initial(seed,trial)
        self._pending=0
        self._step=0

    def public(self):
        return bits(self._x)

    def step(self,action):
        if type(action) is not int or action not in (0,1,2,3):
            raise ValueError("ST8_REAL_BAD_ACTION")
        if self._step>=len(ACTIONS) or action!=ACTIONS[self._step]:
            raise ValueError("ST8_REAL_SOURCE_ACTOR_OR_BUDGET")
        x=self._x
        immediate=self._A if action==0 else self._B if action==1 else 0
        after=rol(x,self._r)^immediate^self._pending
        self._pending=(self._A^effect(
            self._B,negative=self._law in NEG_LAWS
        ) if action==2 else 0)
        self._x=after
        self._step+=1
        return bits(after),bits(x^after)

    def snapshot(self):
        return json.dumps({
            "schema":SCHEMA,"law":self._law,"r":self._r,
            "A":self._A,"B":self._B,"x":self._x,
            "pending":self._pending,"step":self._step
        },sort_keys=True,separators=(",",":"),allow_nan=False)

    @classmethod
    def restore(cls,raw):
        if type(raw) is not str or len(raw)>1500:
            raise ValueError("ST8_PRIVATE_SNAPSHOT_LENGTH")
        try:
            x=json.loads(raw)
            fields={"schema","law","r","A","B","x","pending","step"}
            if (type(x) is not dict or set(x)!=fields or
                x["schema"]!=SCHEMA or
                any(type(x[k]) is not int for k in fields-{"schema"}) or
                x["law"]<0 or x["r"] not in (1,2,3) or
                any(x[k] not in range(256) for k in ("A","B","x","pending")) or
                x["step"] not in range(6)):
                raise ValueError("ST8_PRIVATE_SNAPSHOT_SHAPE")
            obj=cls(x["law"],100,0)
            for name in fields-{"schema","law"}:
                setattr(obj,"_"+name,x[name])
            if obj.snapshot()!=raw:
                raise ValueError("ST8_PRIVATE_NONCANONICAL_SNAPSHOT")
            return obj
        except (ValueError,TypeError,OverflowError,KeyError) as e:
            raise ValueError("ST8_PRIVATE_COLD_RESTORE_INVALID") from e


def source_episode(law,seed,trial):
    env=PrivateCubicWorld(law,seed,trial)
    history=[]
    for action in ACTIONS:
        before=env.public()
        after,change=env.step(action)
        if tuple(a^b for a,b in zip(before,after))!=change:
            raise ValueError("ST8_REAL_ACTION_CONSEQUENCE_UNAUTHENTIC")
        history.append((before,action,after,change))
    return history,public_cue(history)
