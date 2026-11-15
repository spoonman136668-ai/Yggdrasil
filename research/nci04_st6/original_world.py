"""ST6 original in-house causal-composition source.

Private to evaluator: source law ID, two actuator masks, hidden causal rule
and pending effect. Learners may consume ONLY (public preaction 8 bits,
announced action, previously observed public 8-bit consequences).
All five actions are actually executed before measuring the consequence.
ST5/ST4 remain untouched, unmerged historical control code.
"""
from hashlib import sha256
import json

ACTIONS=(3,0,1,2,3)
TRIALS=16
SCHEMA="yggdrasil.nci04.st6.original-source.v1"
ALT_LAWS=(43,47)


def h(label):
    if type(label) is not str:
        raise ValueError("ST6_SOURCE_BAD_HASH_INPUT")
    return sha256(label.encode("utf-8")).digest()


def bits(n):
    if type(n) is not int or not 0<=n<=255:
        raise ValueError("ST6_SOURCE_INVALID_BYTE")
    return tuple((n>>j)&1 for j in range(8))


def byte(raw):
    if (type(raw) not in (tuple,list) or len(raw)!=8 or
        any(type(b) is not int or b not in (0,1) for b in raw)):
        raise ValueError("ST6_SOURCE_INVALID_PUBLIC_BITS")
    return sum(b<<i for i,b in enumerate(raw))


def rotate(n,r):
    if type(n) is not int or not 0<=n<=255 or type(r) is not int or r not in (1,2,3,7):
        raise ValueError("ST6_SOURCE_INVALID_ROTATE")
    return ((n<<r)|(n>>(8-r)))&255


def law_params(law):
    if type(law) is not int or law<0:
        raise ValueError("ST6_SOURCE_BAD_PRIVATE_LAW")
    return (1+h("ST6-rot|"+str(law))[0]%3,
            h("ST6-a|"+str(law))[0],
            h("ST6-b|"+str(law))[0])


def initial_state(seed,trial):
    if (type(seed) is not int or seed<0 or
        type(trial) is not int or trial not in range(TRIALS)):
        raise ValueError("ST6_SOURCE_INVALID_SEED_TRIAL")
    for nonce in range(256):
        x=h("ST6-state|"+str(seed)+"|"+str(trial)+"|"+str(nonce))[0]
        if len({rotate(x,r) for r in (1,2,3)})==3:
            return x
    raise ValueError("ST6_SOURCE_NO_ROTATION_IDENTIFIABLE_PUBLIC_START")


def composition(a,b,mode="same_family"):
    if type(a) is not int or a not in range(256) or type(b) is not int or b not in range(256):
        raise ValueError("ST6_SOURCE_BAD_COMPOSITION")
    if mode=="same_family":
        return a^rotate(b,1)
    if mode=="different_rule":
        return a|b
    raise ValueError("ST6_SOURCE_BAD_RULE")


def public_signature(events):
    """Learnable from first THREE actually observed public transitions."""
    if type(events) not in (tuple,list) or len(events)<3:
        return None
    e0,e1,e2=events[:3]
    if (e0[1],e1[1],e2[1])!=(3,0,1):
        raise ValueError("ST6_PUBLIC_DIAGNOSTIC_ACTOR_DRIFT")
    old=byte(e0[0]);post=byte(e0[2])
    valid=[r for r in (1,2,3) if rotate(old,r)==post]
    if len(valid)!=1:
        return None
    r=valid[0]
    a=byte(e1[2])^rotate(byte(e1[0]),r)
    b=byte(e2[2])^rotate(byte(e2[0]),r)
    return (r,a,b)


def hypothesis_outputs(a,b):
    """Public hypothesis family, not knowledge of the true source rule."""
    if type(a) is not int or a not in range(256) or type(b) is not int or b not in range(256):
        raise ValueError("ST6_BAD_PUBLIC_HYPOTHESIS_CUES")
    return (
        a^rotate(b,1),
        a^b,
        a|b,
        a&b,
        (a+b)&255,
        a^rotate(b,2),
        a&(~b&255),
        a^rotate(b,7),
    )


class OriginalWorld:
    __slots__=("_law","_state","_pending","_step")

    def __init__(self,law,seed,trial):
        law_params(law)
        self._law=law
        self._state=initial_state(seed,trial)
        self._pending=0
        self._step=0

    def public(self):
        return bits(self._state)

    def step(self,action):
        if type(action) is not int or action not in (0,1,2,3):
            raise ValueError("ST6_ORIGINAL_INVALID_ACTION")
        if self._step>=5 or action!=ACTIONS[self._step]:
            raise ValueError("ST6_ORIGINAL_ACTOR_SEQUENCE_OR_LIMIT")
        r,a,b=law_params(self._law)
        immediate=(a if action==0 else b if action==1 else 0)
        post=rotate(self._state,r)^immediate^self._pending
        self._pending=(composition(a,b,
                     "different_rule" if self._law in ALT_LAWS else "same_family")
                     if action==2 else 0)
        before=self._state
        self._state=post
        self._step+=1
        return bits(post),bits(before^post)

    def snapshot(self):
        return json.dumps({
            "schema":SCHEMA,"law":self._law,"state":self._state,
            "pending":self._pending,"step":self._step,
        },sort_keys=True,separators=(",",":"),allow_nan=False)

    @classmethod
    def restore(cls,snapshot):
        if type(snapshot) is not str or len(snapshot)>1000:
            raise ValueError("ST6_ORIGINAL_CHECKPOINT_SIZE")
        try:
            obj=json.loads(snapshot)
            if (type(obj) is not dict or
                set(obj)!={"schema","law","state","pending","step"} or
                obj["schema"]!=SCHEMA or
                any(type(obj[k]) is not int for k in ("law","state","pending","step")) or
                obj["law"]<0 or obj["state"] not in range(256) or
                obj["pending"] not in range(256) or obj["step"] not in range(6)):
                raise ValueError("ST6_ORIGINAL_CHECKPOINT_SHAPE")
            w=cls(obj["law"],100,0)
            w._state=obj["state"]
            w._pending=obj["pending"]
            w._step=obj["step"]
            if w.snapshot()!=snapshot:
                raise ValueError("ST6_ORIGINAL_CHECKPOINT_NONCANONICAL")
            return w
        except (TypeError,KeyError,OverflowError) as ex:
            raise ValueError("ST6_ORIGINAL_COLD_RESTORE_ERROR") from ex


def source_episode(law,seed,trial):
    w=OriginalWorld(law,seed,trial)
    events=[]
    for act in ACTIONS:
        before=w.public()
        after,target=w.step(act)
        if tuple(a^b for a,b in zip(before,after))!=target:
            raise ValueError("ST6_ORIGINAL_PUBLIC_OUTCOME_INVALID")
        events.append((before,act,after,target))
    return events,public_signature(events)
