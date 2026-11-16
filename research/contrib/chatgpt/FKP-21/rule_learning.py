"""FKP-21 source-independent non-token causal law synthesis and controls.

All models consume public physically selected actions and earned feedback only.
The candidate constructs an 11-bit degree<=2 algebraic normal form without a
named AND/XOR/OR/threshold operator catalog. This finite feature basis is an
explicit inductive bias: NOT arbitrary primitive invention.

Independently coded exhaustive symbolic version-space control is fully fit on
the SAME 12 public actions. A direct public lookup and non-learning/shuffled
controls expose memorization and source-abstention cases.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]/"FKP-18"))
from temporal_trace import PublicStep, PublicTransition, _valid, SparseTemporalTrace

MAX_BYTES=65536
NUM_MONOMIALS=11
TRAIN_COUNT=12
FIRST_COUNT=4
MODES=("INNOVATION_GF2","INDEPENDENT_GF2_ELIMINATION",
       "EXACT_PUBLIC_LOOKUP_ABSTAIN","NO_UPDATE",
       "SHUFFLED_OBSERVATION_TO_INPUT")


def _encode(obj):
    return json.dumps(obj,sort_keys=True,allow_nan=False,
                      separators=(",",":")).encode("ascii")


def _check_input(x):
    if type(x) is not int or not 0<=x<16:
        raise ValueError("FKP21_INVALID_PUBLIC_INPUT")
    return x


def _monomials(x):
    x=_check_input(x)
    bits=tuple((x>>k)&1 for k in range(4))
    values=(1,*bits,*(bits[i]*bits[j] for i in range(4) for j in range(i+1,4)))
    return sum(v<<k for k,v in enumerate(values))


def _predict(mask,x):
    return (mask & _monomials(x)).bit_count()%2


def _actual(rows):
    if type(rows) is not tuple or len(rows)!=4:
        raise ValueError("FKP21_FOUR_PHYSICAL_STEPS_REQUIRED")
    rows=tuple(_valid(r) for r in rows)
    ctx=rows[0].before[0]
    if ctx not in (0,1) or type(ctx) is not int:
        raise ValueError("FKP21_INVALID_PUBLIC_CONTEXT")
    actions=[]
    for phase,row in enumerate(rows):
        if row.before[0]!=ctx or row.after[0]!=ctx or (
            row.before[1]!=phase or row.after[1]!=phase+1):
            raise ValueError("FKP21_FALSA_PUBLIC_PHASE")
        if row.action not in (0,1) or type(row.action) is not int:
            raise ValueError("FKP21_ACTION_NOT_BINARY")
        history=tuple(PublicTransition(r.before,r.action,r.reward,r.after,r.done)
                      for r in rows[:phase])
        if row.history!=history:
            raise ValueError("FKP21_ACTION_HISTORY_NOT_PHYSICAL")
        if phase<3 and (row.reward!=0.0 or row.done):
            raise ValueError("FKP21_EARLY_FUTURE_LABEL")
        if phase==3 and (row.reward not in (-1.0,1.0) or not row.done):
            raise ValueError("FKP21_MISSING_ACTUAL_FINAL_REWARD")
        actions.append(row.action)
    if actions[3]!=0:
        raise ValueError("FKP21_FROZEN_DISTRACTOR_MISMATCH")
    x=(ctx<<3)|actions[0]|(actions[1]<<1)|(actions[2]<<2)
    y=1 if rows[-1].reward==1.0 else 0
    # Actual action order passes through the prior physical public trace.
    trace=SparseTemporalTrace()
    for index,row in enumerate(rows):
        trace.observe_public(row,event_id=index)
    if trace.public_observations!=4:
        raise AssertionError("FKP21_FOUR_OBSERVED_ACTIONS_NOT_RECORDED")
    return x,y,trace.semantic_receipt()


def _solve_innovative(rows):
    """Gaussian elimination over GF2 with 12 witnessed equations, no oracle."""
    if len(rows)!=TRAIN_COUNT or len({x for x,y in rows})!=TRAIN_COUNT:
        raise ValueError("FKP21_INCOMPLETE_DISTINCT_PUBLIC_TRAIN")
    matrix=[_monomials(x)|(y<<NUM_MONOMIALS) for x,y in rows]
    width=(1<<NUM_MONOMIALS)-1
    rank=0
    pivots=[]
    for bit in range(NUM_MONOMIALS):
        pivot=next((j for j in range(rank,len(matrix))
                    if (matrix[j]>>bit)&1),None)
        if pivot is None:
            continue
        matrix[rank],matrix[pivot]=matrix[pivot],matrix[rank]
        for j in range(len(matrix)):
            if j!=rank and ((matrix[j]>>bit)&1):
                matrix[j]^=matrix[rank]
        pivots.append(bit)
        rank+=1
    if rank!=NUM_MONOMIALS:
        raise ValueError("FKP21_PUBLIC_EQUATIONS_NONIDENTIFIABLE_AT_DEGREE2")
    for row in matrix[rank:]:
        if (row&width)==0 and ((row>>NUM_MONOMIALS)&1):
            raise ValueError("FKP21_OUTSIDE_FROZEN_DEGREE2_BASIS")
    mask=sum(((matrix[j]>>NUM_MONOMIALS)&1)<<col for j,col in enumerate(pivots))
    if any(_predict(mask,x)!=y for x,y in rows):
        raise AssertionError("FKP21_ELIMINATION_NOT_FITTED")
    return mask


def _solve_independent(rows):
    """A separate exhaustive 2^11 version-space comparator, never code reuse."""
    if len(rows)!=TRAIN_COUNT or len({x for x,y in rows})!=TRAIN_COUNT:
        raise ValueError("FKP21_EXACT_CONTROL_INCOMPLETE_TRAIN")
    # Independent monomial construction and parity evaluation, not _predict.
    lookups=[]
    for x,y in rows:
        b=[(x>>i)&1 for i in range(4)]
        f=[1]+b+[b[i]&b[j] for i in range(4) for j in range(i+1,4)]
        lookups.append((f,y))
    survivors=[]
    for candidate in range(1<<NUM_MONOMIALS):
        if all((sum(f[j] for j in range(NUM_MONOMIALS)
                    if (candidate>>j)&1)%2)==y for f,y in lookups):
            survivors.append(candidate)
    if len(survivors)!=1:
        raise ValueError("FKP21_STRONG_VERSION_SPACE_NOT_IDENTIFIED")
    return survivors[0]


class PublicRuleArm:
    def __init__(self,mode):
        if mode not in MODES:
            raise ValueError("FKP21_UNKNOWN_ARM")
        self.mode=mode
        self._observed=[]
        self._receipts=[]
        self._repair={}
        self._fit=None
        self._frozen=False

    @property
    def observations(self):
        return len(self._observed)+len(self._repair)

    @property
    def logical_learned_bytes(self):
        return len(self._observed)*8+len(self._receipts)*32+len(self._repair)*8+16

    def observe_train(self,rows,*,event_id):
        x,y,digest=_actual(rows)
        if type(event_id) is not int or event_id!=len(self._observed) or (
            self._frozen or len(self._observed)>=TRAIN_COUNT or
            x in {key for key,_ in self._observed}):
            raise ValueError("FKP21_REPLAY_OR_UNFROZEN_OBSERVATION")
        next_rows=self._observed+[(x,y)]
        next_receipts=self._receipts+[digest]
        if len(next_rows)*8+len(next_receipts)*32+16>MAX_BYTES:
            raise ValueError("FKP21_LOGICAL_CAPACITY_LIMIT")
        self._observed=next_rows
        self._receipts=next_receipts

    def freeze(self):
        if self._frozen or len(self._observed)!=TRAIN_COUNT:
            raise ValueError("FKP21_TRAIN_NOT_COMPLETE")
        if self.mode=="INNOVATION_GF2":
            self._fit=_solve_innovative(self._observed)
        elif self.mode=="INDEPENDENT_GF2_ELIMINATION":
            self._fit=_solve_independent(self._observed)
        self._frozen=True
        return self

    def predict_first(self,x):
        _check_input(x)
        if not self._frozen:
            raise ValueError("FKP21_NO_PREOUTCOME_FIT")
        if x in self._repair:
            raise ValueError("FKP21_FIRST_PREDICTION_MUST_PRECEDE_FEEDBACK")
        if self.mode in ("INNOVATION_GF2","INDEPENDENT_GF2_ELIMINATION"):
            return _predict(self._fit,x)
        if self.mode=="EXACT_PUBLIC_LOOKUP_ABSTAIN":
            return dict(self._observed).get(x)
        if self.mode=="SHUFFLED_OBSERVATION_TO_INPUT":
            return {k^1:v for k,v in self._observed}.get(x)
        return 0

    def record_actual_feedback(self,rows,*,index):
        x,y,digest=_actual(rows)
        if not self._frozen or type(index) is not int or index!=len(self._repair):
            raise ValueError("FKP21_FEEDBACK_OUT_OF_ORDER")
        if len(self._repair)>=FIRST_COUNT or x in self._repair or x in dict(self._observed):
            raise ValueError("FKP21_DUPLICATED_OR_NOT_UNSEEN")
        if self.mode=="NO_UPDATE":
            # The no-update ablation remains frozen, including direct memory.
            self._repair[x]=None
        else:
            self._repair[x]=y
        if self.logical_learned_bytes>MAX_BYTES:
            del self._repair[x]
            raise ValueError("FKP21_PUBLIC_FEEDBACK_CAPACITY")
        return digest

    def recall(self,x):
        _check_input(x)
        if x not in self._repair:
            raise ValueError("FKP21_RECALL_NOT_YET_PHYSICALLY_SEEN")
        return self._repair[x]

    def state_receipt(self):
        return sha256(_encode(self._state())).hexdigest()

    def _state(self):
        return {"schema":"fkp21.public-rule.v1","mode":self.mode,
                "observed":self._observed,"receipt_shas":self._receipts,
                "frozen":self._frozen,"fit":self._fit,
                "feedback":[[k,v] for k,v in self._repair.items()]}

    def checkpoint(self):
        body=self._state()
        raw=_encode(body)
        if len(raw)>MAX_BYTES:
            raise ValueError("FKP21_CHECKPOINT_TOO_LARGE")
        return _encode({"body":body,"sha256":sha256(raw).hexdigest()})

    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or len(raw)>MAX_BYTES:
            raise ValueError("FKP21_BAD_CHECKPOINT")
        try:
            envelope=json.loads(raw,object_pairs_hook=_no_duplicate,
                                parse_constant=lambda _: _no_nan())
        except (ValueError,UnicodeError,TypeError) as exc:
            raise ValueError("FKP21_BAD_CHECKPOINT") from exc
        if type(envelope) is not dict or set(envelope)!={"body","sha256"}:
            raise ValueError("FKP21_BAD_CHECKPOINT_ENVELOPE")
        body=envelope["body"]
        if type(body) is not dict or set(body)!={
                "schema","mode","observed","receipt_shas","frozen","fit","feedback"}:
            raise ValueError("FKP21_BAD_CHECKPOINT_SCHEMA")
        if body["schema"]!="fkp21.public-rule.v1" or (
                sha256(_encode(body)).hexdigest()!=envelope["sha256"]):
            raise ValueError("FKP21_CHECKPOINT_CONTENT_SHA")
        obj=cls(body["mode"])
        observations=body["observed"]
        receipts=body["receipt_shas"]
        feedback=body["feedback"]
        if type(observations) is not list or type(receipts) is not list or (
                type(feedback) is not list or type(body["frozen"]) is not bool):
            raise ValueError("FKP21_CHECKPOINT_ENTRY_TYPES")
        if len(observations)>TRAIN_COUNT or len(receipts)!=len(observations) or len(feedback)>FIRST_COUNT:
            raise ValueError("FKP21_CHECKPOINT_RECORD_COUNT")
        seen=set()
        for row in observations:
            if type(row) is not list or len(row)!=2 or (
                type(row[0]) is not int or not 0<=row[0]<16 or
                type(row[1]) is not int or row[1] not in (0,1) or row[0] in seen):
                raise ValueError("FKP21_CHECKPOINT_INVALID_PUBLIC_OBSERVATION")
            seen.add(row[0])
        if any(type(x) is not str or len(x)!=64 or any(
                c not in "0123456789abcdef" for c in x) for x in receipts):
            raise ValueError("FKP21_CHECKPOINT_INVALID_TRACE")
        if body["frozen"] and len(observations)!=TRAIN_COUNT:
            raise ValueError("FKP21_CHECKPOINT_PREMATURE_FREEZE")
        obj._observed=[tuple(row) for row in observations]
        obj._receipts=list(receipts)
        obj._frozen=body["frozen"]
        if obj._frozen and obj.mode=="INNOVATION_GF2":
            obj._fit=_solve_innovative(obj._observed)
        elif obj._frozen and obj.mode=="INDEPENDENT_GF2_ELIMINATION":
            obj._fit=_solve_independent(obj._observed)
        if obj._fit!=body["fit"]:
            raise ValueError("FKP21_CHECKPOINT_FIT_MISMATCH")
        for row in feedback:
            if type(row) is not list or len(row)!=2 or (
                type(row[0]) is not int or not 0<=row[0]<16 or row[0] in seen or row[0] in obj._repair):
                raise ValueError("FKP21_CHECKPOINT_DUPLICATE_FEEDBACK")
            if row[1] is not None and (type(row[1]) is not int or row[1] not in (0,1)):
                raise ValueError("FKP21_CHECKPOINT_INVALID_FEEDBACK")
            if obj.mode!="NO_UPDATE" and row[1] is None:
                raise ValueError("FKP21_CHECKPOINT_LOST_FEEDBACK")
            if obj.mode=="NO_UPDATE" and row[1] is not None:
                raise ValueError("FKP21_CHECKPOINT_NO_UPDATE_VIOLATION")
            obj._repair[row[0]]=row[1]
        if obj.logical_learned_bytes>MAX_BYTES or obj.checkpoint()!=raw:
            raise ValueError("FKP21_CHECKPOINT_NONCANONICAL")
        return obj


def _no_duplicate(items):
    d={}
    for k,v in items:
        if k in d:
            raise ValueError("FKP21_CHECKPOINT_DUPLICATE_JSON_KEY")
        d[k]=v
    return d


def _no_nan():
    raise ValueError("FKP21_CHECKPOINT_NONFINITE")
