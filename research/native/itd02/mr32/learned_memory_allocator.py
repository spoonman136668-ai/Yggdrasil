"""MR32-H: learned task-utility memory allocator pilot.

A fixed 16-slot allocator (7 active, 9 retained) learns a linear utility
predictor from explicit post-task usefulness feedback for memories actually
used. It does not use novelty or residual thresholds to decide retention.
Source-only pilot: no native-world feedback or protected cohort is included.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
import math
from typing import Iterable, Optional

SCHEMA = "yggdrasil.mr32.learned-memory-allocator.v1"
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
    key: str
    representation: list[float]
    evidence_count: int = 1
    uses: int = 0
    last_used: int = 0
    prediction_error: float = 0.0
    contradiction_rate: float = 0.0
    active: bool = False
    pending_use: bool = False


class LearnedMemoryAllocator:
    """Utility model is learned only from downstream usefulness feedback."""
    def __init__(self):
        self.memories: list[Memory] = []
        self.weights = [0.0] * (META + 1)
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
        return (1.0,) + self._metadata(memory)

    def predicted_utility(self, memory: Memory) -> float:
        raw = sum(w*x for w,x in zip(self.weights,self._features(memory)))
        # A bounded monotone transform; the learned weights, not fixed
        # novelty/contradiction thresholds, determine relative retention value.
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
        if any(m.key==key for m in self.memories):
            raise ValueError("DUPLICATE_MEMORY_KEY")
        rep = _vec(representation,REPRESENTATION,"REPRESENTATION")
        for name,value in (("evidence_count",evidence_count),):
            if isinstance(value,bool) or not isinstance(value,int) or value<1 or value>65535:
                raise ValueError(name.upper())
        for name,value in (("prediction_error",prediction_error),("contradiction_rate",contradiction_rate)):
            if not math.isfinite(value) or value<0 or value>1:
                raise ValueError(name.upper())
        self.step += 1
        self.memories.append(Memory(key,list(rep),evidence_count,0,self.step,
                                    prediction_error,contradiction_rate,False,False))
        self._rebalance()
        retained = next(m for m in self.memories if m.key==key)
        return {"key":key,"partition":"active" if retained.active else "retained",
                "total":len(self.memories),"active":sum(m.active for m in self.memories),
                "retained":sum(not m.active for m in self.memories)}

    def _rebalance(self) -> None:
        # Predicted downstream usefulness determines exact partition membership.
        ranked = sorted(self.memories,key=lambda m:(-self.predicted_utility(m),m.key))
        active_keys={m.key for m in ranked[:ACTIVE]}
        for m in self.memories:
            m.active=m.key in active_keys
        if len(self.memories)>TOTAL:
            # Evict only the lowest predicted-utility retained memory.
            victim = min((m for m in self.memories if not m.active),
                         key=lambda m:(self.predicted_utility(m),m.key))
            if victim.pending_use:
                raise RuntimeError("CANNOT_EVICT_PENDING_MEMORY_FEEDBACK")
            self.memories.remove(victim)
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
        if not math.isfinite(usefulness) or not 0.0<=usefulness<=1.0:
            raise ValueError("USEFULNESS_RANGE")
        features=self._features(memory)
        prediction=self.predicted_utility(memory)
        error=usefulness-prediction
        for i,x in enumerate(features):
            self.weights[i]=max(-WEIGHT_LIMIT,min(WEIGHT_LIMIT,self.weights[i]+LR*error*x))
        self.loss_ema=0.9*self.loss_ema+0.1*error*error
        memory.pending_use=False
        self.feedback_count+=1
        self._rebalance()
        return {"prediction_before":prediction,"observed_usefulness":usefulness,
                "squared_error":error*error,"feedback_count":self.feedback_count,
                "partition":"active" if memory.active else "retained"}

    def _get(self,key:str)->Memory:
        for memory in self.memories:
            if memory.key==key:
                return memory
        raise KeyError("UNKNOWN_MEMORY_KEY")

    def _check(self)->None:
        if len(self.memories)>TOTAL:
            raise RuntimeError("MEMORY_CAPACITY")
        if sum(m.active for m in self.memories)>ACTIVE:
            raise RuntimeError("ACTIVE_CAPACITY")
        if sum(not m.active for m in self.memories)>RETAINED:
            raise RuntimeError("RETAINED_CAPACITY")
        if len({m.key for m in self.memories})!=len(self.memories):
            raise RuntimeError("DUPLICATE_MEMORY_KEY")

    def snapshot(self)->bytes:
        if any(m.pending_use for m in self.memories):
            raise RuntimeError("CANNOT_CHECKPOINT_PENDING_MEMORY_FEEDBACK")
        self._check()
        payload={"schema":SCHEMA,"partition":{"total":TOTAL,"active":ACTIVE,"retained":RETAINED},
                 "step":self.step,"feedback_count":self.feedback_count,"loss_ema":self.loss_ema,
                 "weights":self.weights,"memories":[asdict(m) for m in sorted(self.memories,key=lambda x:x.key)]}
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
        if not isinstance(weights,list) or len(weights)!=META+1:
            raise ValueError("CHECKPOINT_WEIGHTS")
        weights=[float(v) for v in weights]
        if not all(math.isfinite(v) and abs(v)<=WEIGHT_LIMIT for v in weights):
            raise ValueError("CHECKPOINT_WEIGHT_RANGE")
        loss=float(payload.get("loss_ema"))
        if not math.isfinite(loss) or loss<0:
            raise ValueError("CHECKPOINT_LOSS")
        rows=payload.get("memories")
        if not isinstance(rows,list) or len(rows)>TOTAL:
            raise ValueError("CHECKPOINT_CAPACITY")
        model.memories=[]
        for row in rows:
            mem=Memory(**row)
            _vec(mem.representation,REPRESENTATION,"REPRESENTATION")
            if mem.pending_use:
                raise ValueError("CHECKPOINT_PENDING_USE")
            if mem.evidence_count<1 or mem.evidence_count>65535 or mem.uses<0 or mem.uses>65535 or mem.last_used<0:
                raise ValueError("CHECKPOINT_COUNTER")
            if not 0<=mem.prediction_error<=1 or not 0<=mem.contradiction_rate<=1:
                raise ValueError("CHECKPOINT_META_RANGE")
            model.memories.append(mem)
        model.step=payload["step"];model.feedback_count=payload["feedback_count"]
        model.loss_ema=loss;model.weights=weights
        model._check()
        expected={m.key for m in sorted(model.memories,key=lambda m:(-model.predicted_utility(m),m.key))[:ACTIVE]}
        if any(m.active!=(m.key in expected) for m in model.memories):
            raise ValueError("CHECKPOINT_PARTITION_INCONSISTENT")
        return model

    def stats(self)->dict:
        self._check()
        return {"total":len(self.memories),"active":sum(m.active for m in self.memories),
                "retained":sum(not m.active for m in self.memories),
                "feedback_count":self.feedback_count,"loss_ema":self.loss_ema}
