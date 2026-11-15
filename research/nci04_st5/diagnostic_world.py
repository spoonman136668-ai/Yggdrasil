"""ST5 private five-step causal source, reused unchanged ST4 transition laws.

Every actual transition occurs in THIS source. The private law/seed/trial/
rotation/masks/pending never reach a model. Models get public 8-bit state,
announced action and observed public difference only. ST4 code is imported
read-only at its frozen Git blob; no ST4 negative is reopened or retuned.

A pre-source preregistration corrigendum guarantees uniquely identifiable
first-step rotation using law-independent deterministic rejection sampling.
"""
import json

from research.nci04_st4.paired_world import (
    digest,rotation,immediate_mask,delayed_mask,rotate_byte,
    public_bits,check_public
)

SCHEMA="yggdrasil.nci04.st5.private-five-step-diagnostic-source.v1"
ACTIONS=(3,0,1,2,3)
TRIALS=16


def initial_public(seed,trial):
    if (type(seed) is not int or seed<0 or
        type(trial) is not int or trial not in range(TRIALS)):
        raise ValueError("ST5_SOURCE_BAD_SEED_OR_TRIAL")
    for nonce in range(256):
        value=digest(
            "ST5-state|"+str(seed)+"|"+str(trial)+"|"+str(nonce)
        )[0]
        if len({rotate_byte(value,1),rotate_byte(value,2),
                rotate_byte(value,3)})==3:
            return value
    raise ValueError("ST5_SOURCE_NO_IDENTIFIABLE_INITIAL_PUBLIC")


def public_rotation(before,after):
    x=check_public(before)
    y=check_public(after)
    choices=[k for k in (1,2,3) if rotate_byte(x,k)==y]
    return choices[0] if len(choices)==1 else None


def public_signature(transitions):
    """Derived only from three authentic PUBLIC diagnostic transitions."""
    if type(transitions) not in (tuple,list) or len(transitions)<3:
        return None
    a,b,c=transitions[:3]
    if (a[1],b[1],c[1])!=(3,0,1):
        raise ValueError("ST5_CUE_ACTIONS_DIFFER_FROM_FROZEN_ACTOR")
    r=public_rotation(a[0],a[2])
    if r is None:
        return None
    first=check_public(b[2])^rotate_byte(check_public(b[0]),r)
    second=check_public(c[2])^rotate_byte(check_public(c[0]),r)
    return (r,first,second)


class DiagnosticWorld:
    __slots__=("_law","_seed","_trial","_state","_pending","_step")

    def __init__(self,law,seed,trial):
        if type(law) is not int or law<0:
            raise ValueError("ST5_SOURCE_BAD_LAW")
        self._law=law
        self._seed=seed
        self._trial=trial
        self._state=initial_public(seed,trial)
        self._pending=0
        self._step=0

    def public(self):
        return public_bits(self._state)

    def step(self,action):
        if type(action) is not int or action not in range(4):
            raise ValueError("ST5_SOURCE_BAD_ACTION")
        if self._step>=len(ACTIONS) or action!=ACTIONS[self._step]:
            raise ValueError("ST5_SOURCE_ACTOR_SEQUENCE_OR_BUDGET")
        before=self._state
        nxt=(rotate_byte(before,rotation(self._law)) ^
             (immediate_mask(self._law,action) if action in (0,1) else 0)
             ^self._pending)
        self._pending=delayed_mask(self._law) if action==2 else 0
        self._state=nxt
        self._step+=1
        return public_bits(nxt),public_bits(before^nxt)

    def snapshot(self):
        return json.dumps({
            "schema":SCHEMA,"law":self._law,"seed":self._seed,
            "trial":self._trial,"state":self._state,
            "pending":self._pending,"step":self._step,
        },sort_keys=True,separators=(",",":"),allow_nan=False)

    @classmethod
    def restore(cls,payload):
        if type(payload) is not str or len(payload)>1200:
            raise ValueError("ST5_SOURCE_INVALID_SNAPSHOT_BYTES")
        try:
            d=json.loads(payload)
            keys={"schema","law","seed","trial","state","pending","step"}
            if (type(d) is not dict or set(d)!=keys or
                d["schema"]!=SCHEMA or
                any(type(d[k]) is not int for k in keys-{"schema"}) or
                min(d["law"],d["seed"])<0 or
                d["trial"] not in range(TRIALS) or
                d["state"] not in range(256) or
                d["pending"] not in range(256) or
                d["step"] not in range(6)):
                raise ValueError("ST5_SOURCE_INVALID_SNAPSHOT_SHAPE")
            result=cls(d["law"],d["seed"],d["trial"])
            for key in ("state","pending","step"):
                setattr(result,"_"+key,d[key])
            if result.snapshot()!=payload:
                raise ValueError("ST5_SOURCE_NONCANONICAL_SNAPSHOT")
            return result
        except (KeyError,TypeError,OverflowError) as e:
            raise ValueError("ST5_SOURCE_RESTORE_FAILED") from e


def run_original_episode(law,seed,trial):
    """Evaluator-only source receipt. Never provide law/cue truth to model."""
    world=DiagnosticWorld(law,seed,trial)
    history=[]
    for action in ACTIONS:
        before=world.public()
        after,target=world.step(action)
        if tuple(a^b for a,b in zip(before,after))!=target:
            raise ValueError("ST5_SOURCE_CONSEQUENCE_DRIFT")
        history.append((before,action,after,target))
    source_cue=public_signature(history)
    return history,source_cue
