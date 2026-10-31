"""MR32-H: learned task-utility memory allocator pilot.

Exactly sixteen slots are maintained at all times: seven active and nine
retained. The allocator learns a linear utility predictor from explicit
post-task usefulness feedback for memories actually used. Source-only pilot.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
import math
from typing import Iterable, Optional

SCHEMA = "yggdrasil.mr32.content-aware-memory-allocator.v1"
REPRESENTATION = 16
META = 5
TOTAL = 16
ACTIVE = 7
RETAINED = 9
LR = 0.08
WEIGHT_LIMIT = 4.0


def _vec(values: Iterable[float], size: int, name: str) -> tuple[float, ...]:
    try:
        result = tuple(float(v) for v in values)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name}_NUMERIC") from exc
    if len(result) != size:
        raise ValueError(f"{name}_DIMENSION")
    if not all(math.isfinite(v) and -1.0 <= v <= 1.0 for v in result):
        raise ValueError(f"{name}_RANGE")
    return result


@dataclass
class Memory:
    key: str = ""
    representation: list[float] | None = None
    evidence_count: int = 0
    uses: int = 0
    last_used: int = 0
    prediction_error: float = 0.0
    contradiction_rate: float = 0.0
    active: bool = False
    pending_use: bool = False
    occupied: bool = False


class ContentAwareMemoryAllocator:
    """Fixed 7/9 allocator with learned downstream-usefulness ranking."""
    def __init__(self):
        self.memories = [Memory(active=(i < ACTIVE),
                                representation=[0.0] * REPRESENTATION)
                         for i in range(TOTAL)]
        self.weights = [0.0] * (META + 1 + REPRESENTATION)
        self.step = 0
        self.feedback_count = 0
        self.loss_ema = 0.0

    def _metadata(self, memory: Memory) -> tuple[float, ...]:
        age = max(0, self.step - memory.last_used)
        return (
            min(1.0, math.log1p(memory.evidence_count) / math.log(257.0)),
            min(1.0, math.log1p(memory.uses) / math.log(257.0)),
            1.0 / (1.0 + age / 32.0),
            max(0.0, min(1.0, memory.prediction_error)),
            max(0.0, min(1.0, memory.contradiction_rate)),
        )

    def _features(self, memory: Memory) -> tuple[float, ...]:
        return (1.0,) + self._metadata(memory) + tuple(memory.representation or [0.0] * REPRESENTATION)

    def predicted_utility(self, memory: Memory) -> float:
        if not memory.occupied:
            return -1.0
        raw = sum(w*x for w,x in zip(self.weights,self._features(memory)))
        if raw >= 0:
            e = math.exp(-min(raw,40.0))
            return 1.0/(1.0+e)
        e = math.exp(max(raw,-40.0))
        return e/(1.0+e)

    def insert(self, key: str, representation: Iterable[float], *,
               evidence_count: int = 1, prediction_error: float = 0.0,
               contradiction_rate: float = 0.0) -> dict:
        if not isinstance(key,str) or not key or len(key)>128:
            raise ValueError("MEMORY_KEY")
        if any(m.occupied and m.key==key for m in self.memories):
            raise ValueError("DUPLICATE_MEMORY_KEY")
        rep = _vec(representation,REPRESENTATION,"REPRESENTATION")
        if isinstance(evidence_count,bool) or not isinstance(evidence_count,int) or not 1<=evidence_count<=65535:
            raise ValueError("EVIDENCE_COUNT")
        for name,value in (("prediction_error",prediction_error),("contradiction_rate",contradiction_rate)):
            if not math.isfinite(value) or not 0<=value<=1:
                raise ValueError(name.upper())
        self.step += 1
        candidate = Memory(key,list(rep),evidence_count,0,self.step,
                           prediction_error,contradiction_rate,False,False,True)
        empty = next((i for i,m in enumerate(self.memories) if not m.occupied),None)
        if empty is None:
            pool = [m for m in self.memories if m.occupied] + [candidate]
            ranked = sorted(pool,key=lambda m:(-self.predicted_utility(m),m.key))
            discarded = ranked[TOTAL:]
            if any(m.pending_use for m in discarded):
                raise RuntimeError("CANNOT_EVICT_PENDING_MEMORY_FEEDBACK")
            pool = ranked[:TOTAL]
        else:
            pool = [m for m in self.memories if m.occupied] + [candidate]
        self._assign(pool)
        stored = next((m for m in self.memories if m.occupied and m.key==key),None)
        stats = self.stats()
        return {"key":key,
                "partition":("evicted" if stored is None else ("active" if stored.active else "retained")),
                **stats}

    def _assign(self, pool: list[Memory]) -> None:
        occupied = sorted(pool,key=lambda m:(-self.predicted_utility(m),m.key))[:TOTAL]
        active_memories = occupied[:ACTIVE]
        retained_memories = occupied[ACTIVE:]
        active_slots = active_memories + [
            Memory(active=True,representation=[0.0]*REPRESENTATION)
            for _ in range(ACTIVE-len(active_memories))]
        retained_slots = retained_memories + [
            Memory(active=False,representation=[0.0]*REPRESENTATION)
            for _ in range(RETAINED-len(retained_memories))]
        for memory in active_slots:
            memory.active = True
        for memory in retained_slots:
            memory.active = False
        self.memories = active_slots + retained_slots
        self._check()

    def mark_use(self,key:str) -> None:
        memory=self._get(key)
        if memory.pending_use:
            raise RuntimeError("MEMORY_USE_ALREADY_PENDING")
        self.step+=1
        memory.uses=min(65535,memory.uses+1)
        memory.last_used=self.step
        memory.pending_use=True

    def observe_task_outcome(self,key:str,usefulness:float) -> dict:
        memory=self._get(key)
        if not memory.pending_use:
            raise RuntimeError("NO_PENDING_MEMORY_USE")
        if isinstance(usefulness,bool) or not math.isfinite(usefulness) or not 0<=usefulness<=1:
            raise ValueError("USEFULNESS_RANGE")
        features=self._features(memory)
        prediction=self.predicted_utility(memory)
        error=usefulness-prediction
        for i,x in enumerate(features):
            self.weights[i]=max(-WEIGHT_LIMIT,min(WEIGHT_LIMIT,self.weights[i]+LR*error*x))
        self.loss_ema=0.9*self.loss_ema+0.1*error*error
        memory.pending_use=False
        self.feedback_count+=1
        self._assign([m for m in self.memories if m.occupied])
        memory=self._get(key)
        return {"prediction_before":prediction,"observed_usefulness":usefulness,
                "squared_error":error*error,"feedback_count":self.feedback_count,
                "partition":"active" if memory.active else "retained"}

    def _get(self,key:str)->Memory:
        for memory in self.memories:
            if memory.occupied and memory.key==key:
                return memory
        raise KeyError("UNKNOWN_MEMORY_KEY")

    def _check(self)->None:
        if len(self.memories)!=TOTAL:
            raise RuntimeError("MEMORY_SLOT_COUNT")
        if sum(m.active for m in self.memories)!=ACTIVE:
            raise RuntimeError("ACTIVE_PARTITION")
        if sum(not m.active for m in self.memories)!=RETAINED:
            raise RuntimeError("RETAINED_PARTITION")
        if any(m.active!=(i<ACTIVE) for i,m in enumerate(self.memories)):
            raise RuntimeError("SLOT_ORDER")
        keys=[m.key for m in self.memories if m.occupied]
        if len(set(keys))!=len(keys):
            raise RuntimeError("DUPLICATE_MEMORY_KEY")
        if any(m.pending_use and not m.occupied for m in self.memories):
            raise RuntimeError("EMPTY_PENDING_MEMORY")

    def snapshot(self)->bytes:
        if any(m.pending_use for m in self.memories):
            raise RuntimeError("CANNOT_CHECKPOINT_PENDING_MEMORY_FEEDBACK")
        self._check()
        payload={"schema":SCHEMA,"partition":{"total":TOTAL,"active":ACTIVE,"retained":RETAINED},
                 "step":self.step,"feedback_count":self.feedback_count,"loss_ema":self.loss_ema,
                 "weights":self.weights,"memories":[asdict(m) for m in self.memories]}
        canonical=json.dumps(payload,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
        return json.dumps({"payload":payload,"sha256":hashlib.sha256(canonical).hexdigest()},
                          sort_keys=True,separators=(",",":"),allow_nan=False).encode()

    @classmethod
    def restore(cls,raw:bytes)->"LearnedMemoryAllocator":
        try:
            envelope=json.loads(raw.decode("utf-8"));payload=envelope["payload"]
            canonical=json.dumps(payload,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
        except Exception as exc:
            raise ValueError("CHECKPOINT_FORMAT") from exc
        if hashlib.sha256(canonical).hexdigest()!=envelope.get("sha256"):
            raise ValueError("CHECKPOINT_HASH_MISMATCH")
        if payload.get("schema")!=SCHEMA or payload.get("partition")!={"total":TOTAL,"active":ACTIVE,"retained":RETAINED}:
            raise ValueError("CHECKPOINT_SCHEMA_OR_PARTITION")
        model=cls()
        if not isinstance(payload.get("step"),int) or payload["step"]<0:
            raise ValueError("CHECKPOINT_STEP")
        if not isinstance(payload.get("feedback_count"),int) or payload["feedback_count"]<0:
            raise ValueError("CHECKPOINT_FEEDBACK_COUNT")
        weights=payload.get("weights")
        if not isinstance(weights,list) or len(weights)!=META+1+REPRESENTATION:
            raise ValueError("CHECKPOINT_WEIGHTS")
        weights=[float(v) for v in weights]
        if not all(math.isfinite(v) and abs(v)<=WEIGHT_LIMIT for v in weights):
            raise ValueError("CHECKPOINT_WEIGHT_RANGE")
        loss=float(payload.get("loss_ema"))
        if not math.isfinite(loss) or loss<0:
            raise ValueError("CHECKPOINT_LOSS")
        rows=payload.get("memories")
        if not isinstance(rows,list) or len(rows)!=TOTAL:
            raise ValueError("CHECKPOINT_CAPACITY")
        restored=[]
        for i,row in enumerate(rows):
            memory=Memory(**row)
            if memory.active!=(i<ACTIVE):
                raise ValueError("CHECKPOINT_PARTITION_ORDER")
            if memory.pending_use:
                raise ValueError("CHECKPOINT_PENDING_USE")
            if memory.occupied:
                if not isinstance(memory.key,str) or not memory.key or len(memory.key)>128:
                    raise ValueError("CHECKPOINT_MEMORY_KEY")
                memory.representation=list(_vec(memory.representation,REPRESENTATION,"REPRESENTATION"))
                if not 1<=memory.evidence_count<=65535 or not 0<=memory.uses<=65535 or memory.last_used<0:
                    raise ValueError("CHECKPOINT_COUNTER")
                if not 0<=memory.prediction_error<=1 or not 0<=memory.contradiction_rate<=1:
                    raise ValueError("CHECKPOINT_META_RANGE")
            else:
                if memory.key or memory.evidence_count or memory.uses or memory.last_used or memory.pending_use:
                    raise ValueError("CHECKPOINT_EMPTY_SLOT")
                memory.representation=[0.0]*REPRESENTATION
            restored.append(memory)
        model.memories=restored
        model.step=payload["step"];model.feedback_count=payload["feedback_count"]
        model.loss_ema=loss;model.weights=weights
        model._check()
        return model

    def stats(self)->dict:
        self._check()
        occupied=sum(m.occupied for m in self.memories)
        return {"total":TOTAL,"active":ACTIVE,"retained":RETAINED,"occupied":occupied,
                "active_occupied":sum(m.occupied and m.active for m in self.memories),
                "retained_occupied":sum(m.occupied and not m.active for m in self.memories),
                "feedback_count":self.feedback_count,"loss_ema":self.loss_ema}
