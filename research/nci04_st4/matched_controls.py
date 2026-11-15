"""ST4 matched, trained PUBLIC controls for native intervention memory.

No hidden law ID, source seed/trial ID, pending mask, reward or source
oracle. Both models see identical preaction public bits, announced actions,
and previous observed public consequences as the native candidate. The
45-coefficient recurrence is fit by online logistic SGD, 8 updates per
actual training consequence; it receives extra optimization work, which
must be included in process-cost receipts, not called matched compute.

The count control has 9 x 3 x 8 x 4 x 2 x 2 = 3,456 learned uint8
counter bytes, EXACT candidate counter byte capacity, plus independently
reported housekeeping. It receives the SAME public rotation inference
as candidate but estimates public change rather than rotation residual.
"""
import json
import math

from research.nci04_st4.native_credit import (
    action_ok,bits,canonical,rotate_candidates,shifted,increment,
    BANKS,N,ACTIONS,MAX,MAX_CLOCK
)

RECUR_SCHEMA="yggdrasil.nci04.st4.recurrent45.v1"
COUNT_SCHEMA="yggdrasil.nci04.st4.lag-aware-count.v1"
RECUR_UPDATES=8
LR=0.045


def validate_transition(raw,action,target,next_public):
    bits(raw);bits(target);bits(next_public);action_ok(action)
    if [x^y for x,y in zip(raw,next_public)]!=list(target):
        raise ValueError("ST4_CONTROL_UNAUTHENTIC_SOURCE_OUTCOME")


def sigmoid(z):
    z=max(-15.,min(15.,z))
    return 1.0/(1.0+math.exp(-z))


def brier(pred,target):
    bits(target)
    if (type(pred) not in (list,tuple) or len(pred)!=N or
        any(type(x) not in (int,float) or not math.isfinite(x) or
            not 0<=x<=1 for x in pred)):
        raise ValueError("ST4_BAD_PREACTION_PREDICTIONS")
    return sum((p-t)**2 for p,t in zip(pred,target))/N


class Recurrent45:
    def __init__(self):
        self.local=[[0.0]*5 for _ in range(N)]
        self.shared=[0.0]*5
        self.state=[0.0]*N
        self.prior=None
        self.previous_change=[0]*N
        self.step=0
        self.train_steps=0

    def reset_episode(self):
        self.state=[0.0]*N
        self.prior=None
        self.previous_change=[0]*N
        self.step=0

    def _features(self,public,action,i):
        return (
            1.0,float(public[i]),(action-1.5)/1.5,
            float(self.prior==2),self.state[i],
        )

    def predict(self,public,action):
        bits(public);action_ok(action)
        return [
            sigmoid(sum((self.local[i][j]+self.shared[j])*v
                        for j,v in enumerate(self._features(public,action,i))))
            for i in range(N)
        ]

    def observe(self,public,action,target,next_public,*,train=True):
        validate_transition(public,action,target,next_public)
        if type(train) is not bool or self.step>=2:
            raise ValueError("ST4_RECURRENT_INVALID_MODE_OR_STEP")
        predicted=self.predict(public,action)
        if train:
            feats=[self._features(public,action,i) for i in range(N)]
            # Fixed multiple optimizer steps per already-observed source
            # outcome. This is conventional online training, never future
            # labels. The extra CPU operations are charged to recurrence.
            for _ in range(RECUR_UPDATES):
                for i in range(N):
                    z=sum((self.local[i][j]+self.shared[j])*v
                          for j,v in enumerate(feats[i]))
                    error=target[i]-sigmoid(z)
                    for j,value in enumerate(feats[i]):
                        self.local[i][j]=max(-8.,min(
                            8.,self.local[i][j]+LR*error*value
                        ))
                        self.shared[j]=max(-8.,min(
                            8.,self.shared[j]+LR*error*value/N
                        ))
            self.train_steps+=1
        for i in range(N):
            self.state[i]=0.65*self.state[i]+.35*target[i]
        self.previous_change=list(target)
        self.prior=action
        self.step+=1
        return predicted

    def snapshot(self):
        return canonical({
            "schema":RECUR_SCHEMA,"local":self.local,"shared":self.shared,
            "state":self.state,"prior":self.prior,
            "previous_change":self.previous_change,"step":self.step,
            "train_steps":self.train_steps,
        })

    @classmethod
    def restore(cls,snapshot):
        if type(snapshot) is not str or len(snapshot)>35000:
            raise ValueError("ST4_RECURRENT_INVALID_SNAPSHOT_SIZE")
        try:
            d=json.loads(snapshot)
            if (type(d) is not dict or set(d)!={
                "schema","local","shared","state","prior",
                "previous_change","step","train_steps"
            } or d["schema"]!=RECUR_SCHEMA or
                type(d["local"]) is not list or len(d["local"])!=N or
                any(type(row) is not list or len(row)!=5
                    for row in d["local"]) or
                type(d["shared"]) is not list or len(d["shared"])!=5 or
                type(d["state"]) is not list or len(d["state"])!=N or
                (d["prior"] is not None and
                 (type(d["prior"]) is not int or
                  d["prior"] not in range(ACTIONS))) or
                type(d["step"]) is not int or d["step"] not in range(3) or
                type(d["train_steps"]) is not int or
                not 0<=d["train_steps"]<=MAX_CLOCK):
                raise ValueError("ST4_RECURRENT_INVALID_SNAPSHOT_SHAPE")
            bits(d["previous_change"])
            if any(type(x) not in (int,float) or not math.isfinite(x)
                   or abs(x)>8.001 for row in d["local"] for x in row):
                raise ValueError("ST4_RECURRENT_BAD_LOCAL")
            if any(type(x) not in (int,float) or not math.isfinite(x)
                   or abs(x)>8.001 for x in d["shared"]+d["state"]):
                raise ValueError("ST4_RECURRENT_BAD_SHARED_OR_STATE")
            obj=cls()
            for k in ("local","shared","state","prior","previous_change",
                      "step","train_steps"):
                setattr(obj,k,d[k])
            if obj.snapshot()!=snapshot:
                raise ValueError("ST4_RECURRENT_NOT_CANONICAL")
            return obj
        except (KeyError,TypeError,OverflowError) as e:
            raise ValueError("ST4_RECURRENT_RESTORE_FAILED") from e

    def accounting(self):
        return {"trained_coefficients":45,
                "episode_recurrent_state_scalars":8,
                "optimizer_steps_per_training_action":RECUR_UPDATES,
                "checkpoint_json_bytes":len(self.snapshot().encode())}


def make_count_bank():
    return {
        "counts":[[
            [[[0,0] for _ in range(2)] for _ in range(ACTIONS)]
            for _ in range(N)
        ] for _ in range(3)],
        "seen":0,"last":0,
    }


class LagAwareCount:
    def __init__(self):
        self.banks=[None]*BANKS
        self.active=None
        self.rotation=None
        self.prior=None
        self.previous_change=[0]*N
        self.clock=0
        self.step=0
        self.updates=0

    def reset_episode(self):
        self.rotation=None
        self.prior=None
        self.previous_change=[0]*N
        self.step=0

    def _select(self):
        if self.active is not None and self.banks[self.active] is not None:
            return
        existing=[(i,b) for i,b in enumerate(self.banks)
                  if b is not None and b["seen"]>0]
        if existing:
            self.active=min(existing,key=lambda t:(-t[1]["seen"],t[0]))[0]
        else:
            self.active=self.banks.index(None)
            self.banks[self.active]=make_count_bank()

    def predict(self,public,action):
        bits(public);action_ok(action)
        if self.active is None or self.rotation is None:
            return [0.5]*N
        bank=self.banks[self.active]
        context=int(self.prior==2)
        return [
            (1+bank["counts"][self.rotation-1][i][action][context][0])/
            (2+sum(bank["counts"][self.rotation-1][i][action][context]))
            for i in range(N)
        ]

    def observe(self,public,action,target,next_public,*,train=True):
        validate_transition(public,action,target,next_public)
        if type(train) is not bool or self.step>=2 or self.clock>=MAX_CLOCK:
            raise ValueError("ST4_COUNT_INVALID_MODE_OR_LIMIT")
        prediction=self.predict(public,action)
        if train:
            self.clock+=1
            if self.rotation is None and action in (2,3):
                rot=rotate_candidates(public,next_public)
                if rot:
                    self.rotation=rot[0]
                    self._select()
            elif self.active is not None and self.rotation is not None:
                bank=self.banks[self.active]
                mode=int(self.prior==2)
                for i,y in enumerate(target):
                    increment(
                        bank["counts"][self.rotation-1][i][action][mode],y
                    )
                bank["seen"]+=1
                bank["last"]=self.clock
            self.updates+=1
        else:
            if self.rotation is None and action in (2,3):
                rot=rotate_candidates(public,next_public)
                if rot:
                    self.rotation=rot[0]
                    existing=[(i,b) for i,b in enumerate(self.banks)
                              if b is not None and b["seen"]>0]
                    if existing:
                        self.active=min(existing,key=lambda t:
                            (-t[1]["seen"],t[0]))[0]
        self.previous_change=list(target)
        self.prior=action
        self.step+=1
        return prediction

    def snapshot(self):
        return canonical({
            "schema":COUNT_SCHEMA,"banks":self.banks,"active":self.active,
            "rotation":self.rotation,"prior":self.prior,
            "previous_change":self.previous_change,"clock":self.clock,
            "step":self.step,"updates":self.updates,
        })

    @classmethod
    def restore(cls,snapshot):
        if type(snapshot) is not str or len(snapshot)>350000:
            raise ValueError("ST4_COUNT_BAD_SNAPSHOT_SIZE")
        try:
            d=json.loads(snapshot)
            if (type(d) is not dict or set(d)!={
                "schema","banks","active","rotation","prior",
                "previous_change","clock","step","updates"
            } or d["schema"]!=COUNT_SCHEMA or
                type(d["banks"]) is not list or len(d["banks"])!=BANKS or
                (d["active"] is not None and
                 (type(d["active"]) is not int or
                  d["active"] not in range(BANKS))) or
                (d["rotation"] is not None and
                 (type(d["rotation"]) is not int or
                  d["rotation"] not in (1,2,3))) or
                (d["prior"] is not None and
                 (type(d["prior"]) is not int or
                  d["prior"] not in range(ACTIONS))) or
                any(type(d[k]) is not int or d[k]<0 or d[k]>MAX_CLOCK
                    for k in ("clock","step","updates")) or d["step"]>2):
                raise ValueError("ST4_COUNT_BAD_SNAPSHOT_SHAPE")
            bits(d["previous_change"])
            if d["active"] is not None and d["banks"][d["active"]] is None:
                raise ValueError("ST4_COUNT_MISSING_BANK")
            for bank in d["banks"]:
                if bank is None:
                    continue
                if (type(bank) is not dict or set(bank)!={
                    "counts","seen","last"
                } or any(type(bank[k]) is not int or
                    not 0<=bank[k]<=MAX_CLOCK for k in ("seen","last")) or
                    type(bank["counts"]) is not list or
                    len(bank["counts"])!=3):
                    raise ValueError("ST4_COUNT_BAD_BANK")
                for rotation in bank["counts"]:
                    if type(rotation) is not list or len(rotation)!=N:
                        raise ValueError("ST4_COUNT_BAD_ROTATION")
                    for cell in rotation:
                        if type(cell) is not list or len(cell)!=ACTIONS:
                            raise ValueError("ST4_COUNT_BAD_CELL")
                        for context in cell:
                            if type(context) is not list or len(context)!=2:
                                raise ValueError("ST4_COUNT_BAD_CONTEXT")
                            for pair in context:
                                if (type(pair) is not list or len(pair)!=2 or
                                    any(type(z) is not int or z not in
                                        range(MAX+1) for z in pair)):
                                    raise ValueError("ST4_COUNT_BAD_COUNTER")
            obj=cls()
            for key in ("banks","active","rotation","prior",
                        "previous_change","clock","step","updates"):
                setattr(obj,key,d[key])
            if obj.snapshot()!=snapshot:
                raise ValueError("ST4_COUNT_NOT_CANONICAL")
            return obj
        except (KeyError,TypeError,OverflowError) as e:
            raise ValueError("ST4_COUNT_RESTORE_FAILED") from e

    def accounting(self):
        return {
            "learned_uint8_counter_bytes":BANKS*3*N*ACTIONS*2*2,
            "source_rotation_basis_shared":True,
            "checkpoint_json_bytes":len(self.snapshot().encode()),
        }
