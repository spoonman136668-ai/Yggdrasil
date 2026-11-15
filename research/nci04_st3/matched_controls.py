"""Conventional ST3 controls trained on exactly the same PUBLIC interventions.

No world-law, source mask, pending queue, source seed or privileged truth.
The recurrent comparator has precisely 45 learned weights (8x5+5 shared)
and eight episodic recurrent scalars. All online evaluation is prequential:
score before the observed original action consequence, then update.
"""
import json
import math

from research.nci04_st3.native_credit import (
    canonical, check_bits, check_action, WARMUP, SLOTS, MAX_CLOCK, MAX_COUNT
)

SCHEMA_REC = "yggdrasil.nci04.st3.recurrent45.v1"
SCHEMA_CNT = "yggdrasil.nci04.st3.action-count8.v1"
RATE = 0.04


def brier(pred, targets):
    check_bits(targets)
    if (type(pred) not in (tuple, list) or len(pred) != 8 or
        any(type(p) not in (int, float) or not math.isfinite(p)
            or not 0 <= p <= 1 for p in pred)):
        raise ValueError("ST3_INVALID_PREACTION_BRIER")
    return sum((p-y)**2 for p,y in zip(pred,targets)) / 8.0


def public_target(raw, targets, nxt):
    check_bits(raw);check_bits(targets);check_bits(nxt)
    if tuple(a^b for a,b in zip(raw,nxt)) != tuple(targets):
        raise ValueError("ST3_CONVENTIONAL_CONSEQUENCE_DRIFT")


def sigmoid(z):
    z = min(15.,max(-15.,z))
    return 1.0/(1.0+math.exp(-z))


BINS = 6  # Six PUBLIC context views; exact counter bytes match ST3.

def new_bank():
    return {
        "counts": [
            [[[0,0] for _ in range(4)] for _ in range(8)]
            for _ in range(BINS)
        ],
        "observations":0,"last_used":0
    }


def public_context(raw, prior_action):
    check_bits(raw)
    if prior_action is not None:
        check_action(prior_action)
    # Deterministic public-bit / public-prior-action context partition.
    # The control has no rotation, delayed-credit, or hidden-law decoder.
    return (raw[0]+2*raw[3]+4*int(prior_action==2))%BINS


class ConventionalRecurrent45:
    def __init__(self):
        self.local = [[0.0]*5 for _ in range(8)]
        self.shared = [0.0]*5
        self.state = [0.0]*8
        self.prior_action = None
        self.prior_target = [0]*8
        self.steps = 0
        self.training_steps = 0

    def reset_episode(self):
        self.state = [0.0]*8
        self.prior_action = None
        self.prior_target = [0]*8
        self.steps = 0

    def features(self,raw,action,i):
        check_bits(raw);check_action(action)
        if type(i) is not int or i not in range(8):
            raise ValueError("ST3_RECURRENT_INVALID_CELL")
        # Same announced action, current public bit, prior intervention
        # and retained local state as the candidate; no private task fields.
        return (1.0, float(raw[i]), (action-1.5)/1.5,
                float(self.prior_action==2), self.state[i])

    def predict(self,raw,action):
        return [
            sigmoid(sum(
                (self.local[i][j]+self.shared[j])*v
                for j,v in enumerate(self.features(raw,action,i))
            )) for i in range(8)
        ]

    def observe(self,raw,action,targets,nxt,*,train):
        public_target(raw,targets,nxt);check_action(action)
        if type(train) is not bool or self.steps>=64:
            raise ValueError("ST3_RECURRENT_MODE_OR_STEP")
        pred=self.predict(raw,action)
        features=[self.features(raw,action,i) for i in range(8)]
        if train:
            # Full observed-data conventional online SGD; no future labels.
            for i in range(8):
                err=targets[i]-pred[i]
                for j,v in enumerate(features[i]):
                    self.local[i][j]=max(-8.,min(
                        8.,self.local[i][j]+RATE*err*v
                    ))
                    self.shared[j]=max(-8.,min(
                        8.,self.shared[j]+(RATE/8)*err*v
                    ))
            self.training_steps+=1
        for i in range(8):
            self.state[i]=.72*self.state[i]+.28*float(targets[i])
        self.prior_action=action
        self.prior_target=list(targets)
        self.steps+=1
        return pred

    def weights_snapshot(self):
        return canonical({"local":self.local,"shared":self.shared})

    def snapshot(self):
        return canonical({
            "schema":SCHEMA_REC,"local":self.local,"shared":self.shared,
            "state":self.state,"prior_action":self.prior_action,
            "prior_target":self.prior_target,"steps":self.steps,
            "training_steps":self.training_steps
        })

    @classmethod
    def restore(cls,blob):
        if type(blob) is not str or len(blob)>25000:
            raise ValueError("ST3_RECURRENT_BAD_CHECKPOINT_SIZE")
        try:
            d=json.loads(blob)
            if (type(d) is not dict or set(d)!={
                "schema","local","shared","state","prior_action",
                "prior_target","steps","training_steps"
            } or d["schema"]!=SCHEMA_REC or
                type(d["local"]) is not list or len(d["local"])!=8 or
                any(type(row) is not list or len(row)!=5 for row in d["local"]) or
                type(d["shared"]) is not list or len(d["shared"])!=5 or
                type(d["state"]) is not list or len(d["state"])!=8 or
                (d["prior_action"] is not None and
                 (type(d["prior_action"]) is not int or
                  d["prior_action"] not in range(4))) or
                type(d["prior_target"]) is not list or
                any(type(d[k]) is not int or
                    not 0 <= d[k] <= MAX_CLOCK
                    for k in ("steps","training_steps")) or
                d["steps"]>64):
                raise ValueError("ST3_RECURRENT_BAD_CHECKPOINT_SHAPE")
            check_bits(d["prior_target"])
            scalars=[v for row in d["local"] for v in row] +                 d["shared"]+d["state"]
            if any(type(v) not in (int,float) or not math.isfinite(v)
                   or abs(v)>8.000001 for v in scalars):
                raise ValueError("ST3_RECURRENT_BAD_COEFFICIENT")
            obj=cls()
            for k in ("local","shared","state","prior_action",
                      "prior_target","steps","training_steps"):
                setattr(obj,k,d[k])
            if obj.snapshot()!=blob:
                raise ValueError("ST3_RECURRENT_NONCANONICAL_CHECKPOINT")
            return obj
        except (KeyError,TypeError,OverflowError) as e:
            raise ValueError("ST3_RECURRENT_INVALID_CHECKPOINT") from e

    def accounting(self):
        return {
            "trained_coefficients":45,"retained_episode_scalars":8,
            "checkpoint_json_bytes":len(self.snapshot().encode("utf-8")),
        }


class ActionCount8:
    """Nine bounded banks x six public contexts x eight cells x four actions.

    EXACT candidate binary-counter byte budget (9*6*8*4*2 == 3456).
    All bins are actual learned count memory, not inert capacity padding.
    Additional observed current bits and prior announced action are shared.
    A simple tabular contextual count lacks native causal intervention credit.
    """
    def __init__(self):
        self.banks=[None]*SLOTS
        self.active=None
        self.preamble=[]
        self.clock=0
        self.episode_steps=0
        self.updates=0
        self.prior_action=None

    def reset_episode(self):
        self.active=None
        self.preamble=[]
        self.episode_steps=0
        self.prior_action=None

    def _predict_bank(self,bank,raw,action,prior):
        context=public_context(raw,prior)
        return [
            (1+bank["counts"][context][i][action][0])/
            (2+sum(bank["counts"][context][i][action])) for i in range(8)
        ]

    def predict(self,raw,action):
        check_bits(raw);check_action(action)
        if self.active is None:
            return [0.5]*8
        return self._predict_bank(
            self.banks[self.active],raw,action,self.prior_action
        )

    def _update_bank(self,bank,raw,action,prior,targets):
        ctx=public_context(raw,prior)
        for i,y in enumerate(targets):
            row=bank["counts"][ctx][i][action]
            if MAX_COUNT in row:
                row[0]//=2;row[1]//=2
            row[0 if y else 1]+=1
        bank["observations"]+=1
        bank["last_used"]=self.clock

    def _assign(self):
        if len(self.preamble)<WARMUP:
            return
        candidates=[]
        for i,bank in enumerate(self.banks):
            if bank is None or bank["observations"]<16:
                continue
            loss=0
            for raw,action,prior,target in self.preamble:
                p=self._predict_bank(bank,raw,action,prior)
                loss+=sum(int(256*(p[j]-target[j])**2)
                          for j in range(8))
            candidates.append((loss,i))
        best=min(candidates) if candidates else None
        if best is not None and best[0]<WARMUP*8*64:
            i=best[1]
        else:
            try:
                i=self.banks.index(None)
            except ValueError:
                i=min(range(SLOTS),key=lambda k:(
                    self.banks[k]["last_used"],k
                ))
            self.banks[i]=new_bank()
        self.active=i
        bank=self.banks[i]
        for raw,action,prior,target in self.preamble:
            self._update_bank(bank,raw,action,prior,target)
        self.preamble=[]

    def observe(self,raw,action,targets,nxt,*,learn=True):
        public_target(raw,targets,nxt);check_action(action)
        if type(learn) is not bool or self.episode_steps>=64:
            raise ValueError("ST3_COUNT_INVALID_MODE_OR_STEP")
        pred=self.predict(raw,action)
        if learn:
            self.clock+=1
            if self.active is None:
                self.preamble.append((
                    list(raw),action,self.prior_action,list(targets)
                ))
                self._assign()
            else:
                self._update_bank(self.banks[self.active],raw,action,
                                  self.prior_action,targets)
            self.updates+=1
        self.prior_action=action
        self.episode_steps+=1
        return pred

    def snapshot(self):
        return canonical({
            "schema":SCHEMA_CNT,"banks":self.banks,"active":self.active,
            "preamble":self.preamble,"clock":self.clock,
            "episode_steps":self.episode_steps,"updates":self.updates,
            "prior_action":self.prior_action
        })

    @classmethod
    def restore(cls,blob):
        if type(blob) is not str or len(blob)>250000:
            raise ValueError("ST3_COUNT_CHECKPOINT_SIZE")
        try:
            d=json.loads(blob)
            if (type(d) is not dict or
                set(d)!={"schema","banks","active","preamble","clock",
                          "episode_steps","updates","prior_action"} or
                d["schema"]!=SCHEMA_CNT or
                type(d["banks"]) is not list or len(d["banks"])!=SLOTS or
                (d["active"] is not None and (
                    type(d["active"]) is not int or
                    d["active"] not in range(SLOTS))) or
                type(d["preamble"]) is not list or
                len(d["preamble"])>=WARMUP or
                (d["prior_action"] is not None and (
                    type(d["prior_action"]) is not int or
                    d["prior_action"] not in range(4))) or
                any(type(d[k]) is not int or d[k]<0 or d[k]>MAX_CLOCK
                    for k in ("clock","updates","episode_steps")) or
                d["episode_steps"]>64):
                raise ValueError("ST3_COUNT_CHECKPOINT_SHAPE")
            for bank in d["banks"]:
                if bank is None:
                    continue
                if (type(bank) is not dict or set(bank)!={
                    "counts","observations","last_used"
                } or type(bank["counts"]) is not list or
                    len(bank["counts"])!=BINS or
                    any(type(mode) is not list or len(mode)!=8
                        for mode in bank["counts"]) or
                    any(type(r) is not list or len(r)!=4
                        for mode in bank["counts"] for r in mode) or
                    any(type(p) is not list or len(p)!=2 or
                        any(type(v) is not int or
                            v not in range(MAX_COUNT+1) for v in p)
                        for mode in bank["counts"] for r in mode for p in r) or
                    any(type(bank[k]) is not int or
                        not 0<=bank[k]<=d["clock"]
                        for k in ("observations","last_used"))):
                    raise ValueError("ST3_COUNT_BAD_BANK")
            if d["active"] is not None and d["banks"][d["active"]] is None:
                raise ValueError("ST3_COUNT_MISSING_ACTIVE")
            for row in d["preamble"]:
                if type(row) is not list or len(row)!=4:
                    raise ValueError("ST3_COUNT_BAD_PREAMBLE")
                check_bits(row[0]);check_action(row[1]);check_bits(row[3])
                if row[2] is not None:
                    check_action(row[2])
            if d["active"] is not None and d["preamble"]:
                raise ValueError("ST3_COUNT_ACTIVE_PREAMBLE_COLLISION")
            obj=cls()
            for k in ("banks","active","preamble","clock","episode_steps",
                      "updates","prior_action"):
                setattr(obj,k,d[k])
            if obj.snapshot()!=blob:
                raise ValueError("ST3_COUNT_NONCANONICAL_CHECKPOINT")
            return obj
        except (KeyError,TypeError,OverflowError) as e:
            raise ValueError("ST3_COUNT_INVALID_CHECKPOINT") from e

    def accounting(self):
        total=SLOTS*BINS*8*4*2
        return {
            "nine_profile_uint8_evidence_bytes":total,
            "native_candidate_counter_bytes":SLOTS*3*8*8*2,
            "allocated_information_capacity_equal":
                total==SLOTS*3*8*8*2,
            "public_only_context_buckets":BINS,
            "checkpoint_json_bytes":len(self.snapshot().encode("utf-8")),
        }
