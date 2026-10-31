"""MR32 conventional predictive controls; source-only comparators, not scientific results."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from residual_belief import (
    FEATURES, TARGETS, TOTAL_SLOTS, ACTIVE_SLOTS, RETAINED_SLOTS,
    Slot, Prediction, _vector, _distance
)


class MemorylessMean:
    """No persistent input-conditioned state: predicts the global running mean."""
    def __init__(self):
        self.count = 0
        self.total = [0.0] * TARGETS
        self.pending = False

    def predict(self, features: Iterable[float], selected_action: int) -> Prediction:
        if self.pending is not False:
            raise RuntimeError("PENDING_OUTCOME_MUST_BE_RESOLVED")
        _vector(features, FEATURES, "FEATURES")
        if isinstance(selected_action, bool) or selected_action not in (0, 1, 2):
            raise ValueError("SELECTED_ACTION_OUT_OF_RANGE")
        values = tuple(v / self.count for v in self.total) if self.count else (0.0,) * TARGETS
        self.pending = selected_action
        return Prediction(values, 1.0 if not self.count else 0.5, self.count > 0)

    def observe_selected_outcome(self, outcome: Iterable[float]) -> None:
        if self.pending is False:
            raise RuntimeError("NO_PENDING_SELECTED_ACTION")
        y = _vector(outcome, TARGETS, "OUTCOME")
        self.pending = False
        self.count += 1
        self.total = [a+b for a,b in zip(self.total,y)]

    def state_bytes(self) -> bytes:
        import json
        return json.dumps({"count":self.count,"total":self.total},
                          sort_keys=True,separators=(",",":")).encode()


class ConventionalPrototypeControl:
    """Sixteen-slot nearest-prototype/EMA control; no residual-driven promotion.

    Uses the same feature/target widths and fixed 7/9 partition. It is a
    conventional comparator, not a byte-matched result until full checkpoints,
    object overhead and runtime allocations are measured.
    """
    def __init__(self):
        self.slots = [Slot(active=(i < ACTIVE_SLOTS)) for i in range(TOTAL_SLOTS)]
        self.pending = None
        self.step = 0

    def predict(self, features: Iterable[float], selected_action: int) -> Prediction:
        if self.pending is not None:
            raise RuntimeError("PENDING_OUTCOME_MUST_BE_RESOLVED")
        x = _vector(features, FEATURES, "FEATURES")
        if isinstance(selected_action, bool) or selected_action not in (0, 1, 2):
            raise ValueError("SELECTED_ACTION_OUT_OF_RANGE")
        valid = [( _distance(x,tuple(s.features)), i, s)
                 for i,s in enumerate(self.slots) if s.valid and s.action == selected_action]
        valid.sort(key=lambda row:(row[0],row[1]))
        if not valid:
            pred = Prediction((0.0,)*TARGETS,1.0,False)
        else:
            distance, _, slot = valid[0]
            pred = Prediction(tuple(slot.target),distance,True)
        self.pending=(x,selected_action,pred.values)
        return pred

    def observe_selected_outcome(self, outcome: Iterable[float]) -> None:
        if self.pending is None:
            raise RuntimeError("NO_PENDING_SELECTED_ACTION")
        y=_vector(outcome,TARGETS,"OUTCOME")
        x,selected_action,_=self.pending
        self.pending=None
        self.step+=1
        valid=[(_distance(x,tuple(s.features)),i,s)
               for i,s in enumerate(self.slots) if s.valid and s.action == selected_action]
        if valid:
            _,index,slot=min(valid,key=lambda row:(row[0],row[1]))
            rate=1.0/(slot.support+1)
            slot.features=[a+0.05*(b-a) for a,b in zip(slot.features,x)]
            slot.target=[a+rate*(b-a) for a,b in zip(slot.target,y)]
            slot.support=min(65535,slot.support+1)
            slot.last_used=self.step
        else:
            index=0
            self.slots[index]=Slot(features=list(x),target=list(y),support=1,
                                   residual_ema=0.0,contradictions=0,
                                   last_used=self.step,active=True,action=selected_action)
        self._check()

    def _check(self):
        if len(self.slots)!=TOTAL_SLOTS:
            raise RuntimeError("CAPACITY")
        if sum(s.active for s in self.slots)!=ACTIVE_SLOTS:
            raise RuntimeError("ACTIVE_PARTITION")
        if sum(not s.active for s in self.slots)!=RETAINED_SLOTS:
            raise RuntimeError("RETAINED_PARTITION")

    def state_bytes(self) -> bytes:
        import json
        from dataclasses import asdict
        data={"step":self.step,"slots":[asdict(s) for s in self.slots],
              "partition":{"active":ACTIVE_SLOTS,"retained":RETAINED_SLOTS}}
        return json.dumps(data,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
