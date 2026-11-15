"""ST5 independent conventional controls sharing PUBLIC action histories.

Two signature-indexed conventional tabular baselines have EXACTLY the same
16 x 8 x 2 = 256 learned uint8 counter capacity as ST5 native memory:
- raw changed-bit counts, a strong public-law signature count comparator;
- rotation-normalized residual counts, an intentionally strong ALGORITHMIC
  EQUIVALENCE comparator. If native ties the latter, no unique native
  mechanism superiority may be claimed.

Fully fitted 45-weight logistic recurrent has eight local floating state
values and four fixed SGD micro-updates per authentic training consequence.
All controls get current public 8 bits, announced action and all previously
observed consequences, NEVER private law/masks/seed/trial from source.
"""
import json
import math

from research.nci04_st5.native_memory import (
    N,SLOTS,CLOCK_MAX,COUNT_MAX,ACTOR,
    canonical,validate_bits,validate_action,pack,rot,observed_rotation,
    signature_ok,fresh_bank,update_count,probability,
)

CONTROL_SCHEMA="yggdrasil.nci04.st5.public-signature-count.v1"
RECUR_SCHEMA="yggdrasil.nci04.st5.recurrent45.v1"
LR=0.045
SGD_MICROSTEPS=4


def brier(pred,target):
    validate_bits(target)
    if (type(pred) not in (tuple,list) or len(pred)!=N or
        any(type(p) not in (int,float) or not math.isfinite(p)
            or not 0<=p<=1 for p in pred)):
        raise ValueError("ST5_CONVENTIONAL_INVALID_PREACTION_PROB")
    return sum((p-y)*(p-y) for p,y in zip(pred,target))/N


def check_transition(before,action,target,after,step):
    validate_bits(before);validate_bits(target);validate_bits(after)
    validate_action(action)
    if (type(step) is not int or step not in range(5) or
        action!=ACTOR[step] or
        [u^v for u,v in zip(before,after)]!=list(target)):
        raise ValueError("ST5_CONTROL_INVALID_ORIGINAL_SOURCE_TRANSITION")


class SignatureCount8:
    """Independent cue-indexed raw/residual counter, not native class clone."""

    def __init__(self,mode="raw"):
        if mode not in ("raw","residual"):
            raise ValueError("ST5_INVALID_COUNT_MODE")
        self.mode=mode
        self.banks=[None]*SLOTS
        self.rot=None
        self.mask0=None
        self.mask1=None
        self.prior=None
        self.step=0
        self.clock=0
        self.updates=0

    def reset_episode(self):
        self.rot=None
        self.mask0=None
        self.mask1=None
        self.prior=None
        self.step=0

    def cue(self):
        if None in (self.rot,self.mask0,self.mask1):
            return None
        return (self.rot,self.mask0,self.mask1)

    def find(self,cue):
        if cue is None:
            return None
        found=[i for i,b in enumerate(self.banks)
               if b is not None and tuple(b["key"])==cue]
        if len(found)>1:
            raise ValueError("ST5_COUNT_DUPLICATE_PROFILE")
        return found[0] if found else None

    def predict(self,before,action):
        validate_bits(before);validate_action(action)
        if self.step>=len(ACTOR) or action!=ACTOR[self.step]:
            raise ValueError("ST5_COUNT_ACTOR_DRIFT")
        if self.step!=4:
            return [.5]*N
        cue=self.cue()
        idx=self.find(cue)
        if idx is None:
            return [.5]*N
        bank=self.banks[idx]
        x=pack(before)
        normal=rot(x,self.rot)
        out=[]
        for i in range(N):
            p=probability(bank["counts"][i])
            if self.mode=="residual" and (((x>>i)&1)^((normal>>i)&1)):
                p=1.-p
            out.append(p)
        return out

    def observe(self,before,action,target,after,*,train=True):
        check_transition(before,action,target,after,self.step)
        if type(train) is not bool:
            raise ValueError("ST5_COUNT_INVALID_LEARN_FLAG")
        prediction=self.predict(before,action)
        if self.step==0:
            self.rot=observed_rotation(before,after)
        elif self.step==1:
            if self.rot is not None:
                self.mask0=pack(after)^rot(pack(before),self.rot)
        elif self.step==2:
            if self.rot is not None:
                self.mask1=pack(after)^rot(pack(before),self.rot)
        elif self.step==4 and train:
            cue=self.cue()
            if cue is not None:
                if self.clock>=CLOCK_MAX:
                    raise ValueError("ST5_COUNT_CLOCK_OVERFLOW")
                self.clock+=1
                ix=self.find(cue)
                if ix is None:
                    try:
                        ix=self.banks.index(None)
                    except ValueError:
                        ix=min(range(SLOTS),key=lambda i:(
                            self.banks[i]["last"],i
                        ))
                    self.banks[ix]=fresh_bank(cue,self.clock)
                bank=self.banks[ix]
                payload=(pack(after)^rot(pack(before),self.rot)
                         if self.mode=="residual" else pack(target))
                for k in range(N):
                    update_count(bank["counts"][k],(payload>>k)&1)
                bank["last"]=self.clock
                bank["observations"]+=1
                self.updates+=1
        self.prior=action
        self.step+=1
        return prediction

    def snapshot(self):
        return canonical({
            "schema":CONTROL_SCHEMA,"mode":self.mode,
            "banks":self.banks,"rot":self.rot,
            "mask0":self.mask0,"mask1":self.mask1,
            "prior":self.prior,"step":self.step,
            "clock":self.clock,"updates":self.updates
        })

    @classmethod
    def restore(cls,payload):
        if type(payload) is not str or len(payload)>80000:
            raise ValueError("ST5_COUNT_SNAPSHOT_SIZE")
        try:
            d=json.loads(payload)
            keys={"schema","mode","banks","rot","mask0","mask1",
                  "prior","step","clock","updates"}
            if (type(d) is not dict or set(d)!=keys or
                d["schema"]!=CONTROL_SCHEMA or d["mode"] not in
                ("raw","residual") or
                type(d["banks"]) is not list or len(d["banks"])!=SLOTS or
                (d["rot"] is not None and
                 (type(d["rot"]) is not int or d["rot"] not in (1,2,3))) or
                any(d[k] is not None and
                    (type(d[k]) is not int or d[k] not in range(256))
                    for k in ("mask0","mask1")) or
                (d["prior"] is not None and
                 (type(d["prior"]) is not int or d["prior"] not in range(4))) or
                any(type(d[k]) is not int or not 0<=d[k]<=CLOCK_MAX
                    for k in ("step","clock","updates")) or d["step"]>5):
                raise ValueError("ST5_COUNT_SNAPSHOT_SHAPE")
            keyset=[]
            for bank in d["banks"]:
                if bank is None:
                    continue
                if (type(bank) is not dict or
                    set(bank)!={"key","counts","last","observations"} or
                    not signature_ok(bank["key"]) or
                    type(bank["counts"]) is not list or
                    len(bank["counts"])!=N or
                    any(type(pair) is not list or len(pair)!=2 or
                        any(type(z) is not int or
                            z not in range(COUNT_MAX+1) for z in pair)
                        for pair in bank["counts"]) or
                    any(type(bank[k]) is not int or
                        not 0<=bank[k]<=d["clock"]
                        for k in ("last","observations"))):
                    raise ValueError("ST5_COUNT_INVALID_BANK")
                keyset.append(tuple(bank["key"]))
            if len(keyset)!=len(set(keyset)):
                raise ValueError("ST5_COUNT_DUPLICATE_CUES")
            x=cls(d["mode"])
            for k in keys-{"schema","mode"}:
                setattr(x,k,d[k])
            if x.snapshot()!=payload:
                raise ValueError("ST5_COUNT_NONCANONICAL_SNAPSHOT")
            return x
        except (KeyError,TypeError,OverflowError) as e:
            raise ValueError("ST5_COUNT_RESTORE_FAILED") from e

    def accounting(self):
        return {
            "learned_uint8_counter_capacity_bytes":SLOTS*N*2,
            "bounded_profile_slots":SLOTS,
            "signature_bytes_per_bank":3,
            "checkpoint_json_bytes":len(self.snapshot().encode("utf-8")),
            "privileged_law_or_source_access":False
        }


def sigmoid(x):
    return 1./(1.+math.exp(-max(-15.,min(15.,x))))


class Recurrent45:
    def __init__(self):
        self.local=[[0.]*5 for _ in range(N)]
        self.shared=[0.]*5
        self.state=[0.]*N
        self.prior=None
        self.last_change=[0]*N
        self.step=0
        self.train_steps=0

    def reset_episode(self):
        self.state=[0.]*N
        self.prior=None
        self.last_change=[0]*N
        self.step=0

    def features(self,before,action,i):
        return (1.,float(before[i]),(action-1.5)/1.5,
                float(self.prior==2),self.state[i])

    def predict(self,before,action):
        validate_bits(before);validate_action(action)
        if self.step>=len(ACTOR) or action!=ACTOR[self.step]:
            raise ValueError("ST5_RECURRENT_ACTOR_DRIFT")
        return [sigmoid(sum(
            (self.local[i][j]+self.shared[j])*f
            for j,f in enumerate(self.features(before,action,i))
        )) for i in range(N)]

    def observe(self,before,action,target,after,*,train=True):
        check_transition(before,action,target,after,self.step)
        if type(train) is not bool:
            raise ValueError("ST5_RECURRENT_BAD_TRAIN_FLAG")
        prediction=self.predict(before,action)
        if train:
            feats=[self.features(before,action,i) for i in range(N)]
            for _ in range(SGD_MICROSTEPS):
                for i in range(N):
                    y=sigmoid(sum(
                        (self.local[i][j]+self.shared[j])*f
                        for j,f in enumerate(feats[i])
                    ))
                    diff=target[i]-y
                    for j,f in enumerate(feats[i]):
                        self.local[i][j]=max(-8.,min(
                            8.,self.local[i][j]+LR*diff*f
                        ))
                        self.shared[j]=max(-8.,min(
                            8.,self.shared[j]+(LR/N)*diff*f
                        ))
            self.train_steps+=1
        for i in range(N):
            self.state[i]=0.7*self.state[i]+0.3*target[i]
        self.last_change=list(target)
        self.prior=action
        self.step+=1
        return prediction

    def snapshot(self):
        return canonical({
            "schema":RECUR_SCHEMA,"local":self.local,"shared":self.shared,
            "state":self.state,"prior":self.prior,
            "last_change":self.last_change,"step":self.step,
            "train_steps":self.train_steps
        })

    @classmethod
    def restore(cls,payload):
        if type(payload) is not str or len(payload)>40000:
            raise ValueError("ST5_RECURRENT_SNAPSHOT_BYTES")
        try:
            d=json.loads(payload)
            keys={"schema","local","shared","state","prior",
                  "last_change","step","train_steps"}
            if (type(d) is not dict or set(d)!=keys or
                d["schema"]!=RECUR_SCHEMA or
                type(d["local"]) is not list or len(d["local"])!=N or
                any(type(row) is not list or len(row)!=5 for row in d["local"]) or
                type(d["shared"]) is not list or len(d["shared"])!=5 or
                type(d["state"]) is not list or len(d["state"])!=N or
                (d["prior"] is not None and
                 (type(d["prior"]) is not int or d["prior"] not in range(4))) or
                any(type(d[k]) is not int or
                    not 0<=d[k]<=CLOCK_MAX for k in ("step","train_steps")) or
                d["step"]>len(ACTOR)):
                raise ValueError("ST5_RECURRENT_SNAPSHOT_SHAPE")
            validate_bits(d["last_change"])
            for z in [v for row in d["local"] for v in row]+d["shared"]+d["state"]:
                if type(z) not in (int,float) or not math.isfinite(z) or abs(z)>8.00001:
                    raise ValueError("ST5_RECURRENT_INVALID_FLOAT")
            x=cls()
            for k in keys-{"schema"}:
                setattr(x,k,d[k])
            if x.snapshot()!=payload:
                raise ValueError("ST5_RECURRENT_NONCANONICAL_SNAPSHOT")
            return x
        except (TypeError,KeyError,OverflowError) as e:
            raise ValueError("ST5_RECURRENT_COLD_RESTORE_FAILED") from e

    def accounting(self):
        return {
            "learned_float_coefficients":45,
            "independent_recurrent_state_scalars":8,
            "sgd_microsteps_per_source_action":SGD_MICROSTEPS,
            "checkpoint_json_bytes":len(self.snapshot().encode("utf-8")),
            "privileged_law_or_source_access":False
        }
