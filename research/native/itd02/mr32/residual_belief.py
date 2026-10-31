"""MR32 bounded predictive-belief development prototype (not native acceptance).

Consumes only caller-provided public features and the subsequently observed
selected-action outcome. No world IDs, semantic labels, private state, reward
oracle, or unselected counterfactuals are represented.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import json
import math
from typing import Iterable, Optional

SCHEMA = "yggdrasil.mr32.residual-belief.v1"
FEATURES, TARGETS = 16, 8
ACTIVE_SLOTS, RETAINED_SLOTS = 7, 9
TOTAL_SLOTS = ACTIVE_SLOTS + RETAINED_SLOTS
NOVELTY_THRESHOLD = 0.25
RESIDUAL_THRESHOLD = 0.35
CONTRADICTION_THRESHOLD = 0.30


def _vector(values: Iterable[float], size: int, name: str) -> tuple[float, ...]:
    try:
        result = tuple(float(x) for x in values)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name}_NOT_NUMERIC") from exc
    if len(result) != size:
        raise ValueError(f"{name}_DIMENSION")
    if not all(math.isfinite(x) and -1.0 <= x <= 1.0 for x in result):
        raise ValueError(f"{name}_OUT_OF_RANGE")
    return result


def _distance(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    return math.sqrt(sum((x-y)**2 for x, y in zip(a, b)) / len(a))


@dataclass
class Slot:
    features: Optional[list[float]] = None
    target: Optional[list[float]] = None
    support: int = 0
    residual_ema: float = 0.0
    contradictions: int = 0
    last_used: int = 0
    active: bool = False
    action: Optional[int] = None

    @property
    def valid(self) -> bool:
        return self.features is not None and self.target is not None and self.support > 0 and self.action in (0, 1, 2)

    def utility(self, now: int) -> float:
        if not self.valid:
            return -1.0
        age = max(0, now-self.last_used)
        return (math.log1p(self.support)/(1.0+self.residual_ema))/(1.0+age/64.0)


@dataclass(frozen=True)
class Prediction:
    values: tuple[float, ...]
    uncertainty: float
    covered: bool


class ResidualBelief:
    """Fixed-capacity predictive state updated after selected outcomes only."""

    def __init__(self) -> None:
        self.slots = [Slot(active=(i < ACTIVE_SLOTS)) for i in range(TOTAL_SLOTS)]
        self.step = 0
        self.pending: Optional[tuple[tuple[float, ...], int, tuple[float, ...], float]] = None

    @property
    def active_count(self) -> int:
        return sum(s.active for s in self.slots)

    @property
    def retained_count(self) -> int:
        return sum(not s.active for s in self.slots)

    def _check_shape(self) -> None:
        if len(self.slots) != TOTAL_SLOTS or self.active_count != ACTIVE_SLOTS or self.retained_count != RETAINED_SLOTS:
            raise RuntimeError("FIXED_SLOT_PARTITION_BROKEN")

    def predict(self, public_features: Iterable[float], selected_action: int) -> Prediction:
        if self.pending is not None:
            raise RuntimeError("PENDING_OUTCOME_MUST_BE_RESOLVED")
        x = _vector(public_features, FEATURES, "FEATURES")
        if isinstance(selected_action, bool) or selected_action not in (0, 1, 2):
            raise ValueError("SELECTED_ACTION_OUT_OF_RANGE")
        valid = []
        for index, slot in enumerate(self.slots):
            if slot.valid and slot.action == selected_action:
                valid.append((_distance(x, tuple(slot.features or ())), index, slot))
        if not valid:
            pred = Prediction((0.0,)*TARGETS, 1.0, False)
        else:
            valid.sort(key=lambda row: (row[0], row[1]))
            nearest = valid[:3]
            weights = [math.exp(-d/0.18)*math.sqrt(s.support)*(1.0 if s.active else 0.65)
                       for d, _, s in nearest]
            total = sum(weights)
            if total <= 1e-15:
                pred = Prediction((0.0,)*TARGETS, 1.0, False)
            else:
                values = tuple(sum(w*float(s.target[j]) for w, (_, _, s) in zip(weights, nearest))/total
                               for j in range(TARGETS))
                uncertainty = sum(w*d for w, (d, _, _) in zip(weights, nearest))/total
                pred = Prediction(values, uncertainty, True)
        self.pending = (x, selected_action, pred.values, pred.uncertainty)
        return pred

    def observe_selected_outcome(self, actual_outcome: Iterable[float]) -> dict:
        if self.pending is None:
            raise RuntimeError("NO_PENDING_SELECTED_ACTION")
        y = _vector(actual_outcome, TARGETS, "OUTCOME")
        x, selected_action, predicted, uncertainty = self.pending
        self.pending = None
        residual = _distance(predicted, y)
        self.step += 1
        valid = [(_distance(x, tuple(s.features or ())), i, s)
                 for i, s in enumerate(self.slots) if s.valid and s.action == selected_action]
        valid.sort(key=lambda row: (row[0], row[1]))
        nearest = valid[0] if valid else None
        novel = nearest is None or nearest[0] > NOVELTY_THRESHOLD
        contradiction = residual >= CONTRADICTION_THRESHOLD
        form_state = novel or (contradiction and residual >= RESIDUAL_THRESHOLD and
                               (nearest is None or nearest[0] > 0.08))
        if form_state:
            index = self._allocate_active()
            self.slots[index] = Slot(features=list(x), target=list(y), support=1,
                                     residual_ema=residual, contradictions=int(contradiction),
                                     last_used=self.step, active=True, action=selected_action)
            disposition = "formed_active_state"
        elif nearest is not None:
            _, index, slot = nearest
            rate = 0.50 if contradiction else 0.15
            slot.target = [max(-1.0, min(1.0, old+rate*(new-old)))
                           for old, new in zip(slot.target or (), y)]
            slot.features = [max(-1.0, min(1.0, old+0.05*(new-old)))
                             for old, new in zip(slot.features or (), x)]
            slot.support = min(65535, slot.support+1)
            slot.residual_ema = 0.9*slot.residual_ema+0.1*residual
            slot.contradictions = min(65535, slot.contradictions+int(contradiction))
            slot.last_used = self.step
            disposition = "revised_active_state" if slot.active else "revised_retained_state"
            if not slot.active and contradiction:
                self._promote_retained(index)
                disposition = "revised_and_promoted_state"
        else:
            raise RuntimeError("NO_UPDATE_TARGET")
        self._check_shape()
        return {"step": self.step, "residual": residual, "uncertainty_before": uncertainty,
                "contradiction": contradiction, "disposition": disposition,
                "active_valid": sum(s.valid and s.active for s in self.slots),
                "retained_valid": sum(s.valid and not s.active for s in self.slots)}

    def _allocate_active(self) -> int:
        active = [(i, s) for i, s in enumerate(self.slots) if s.active]
        empty = next((i for i, s in active if not s.valid), None)
        if empty is not None:
            return empty
        victim, _ = min(active, key=lambda pair: (pair[1].utility(self.step), pair[0]))
        self._move_to_retained(victim)
        return victim

    def _move_to_retained(self, active_index: int) -> None:
        source = self.slots[active_index]
        retained = [(i, s) for i, s in enumerate(self.slots) if not s.active]
        empty = next((i for i, s in retained if not s.valid), None)
        if empty is None:
            empty = min(retained, key=lambda pair: (pair[1].utility(self.step), pair[0]))[0]
        self.slots[empty] = Slot(features=None if not source.valid else source.features[:],
                                 target=None if not source.valid else source.target[:],
                                 support=source.support, residual_ema=source.residual_ema,
                                 contradictions=source.contradictions, last_used=source.last_used,
                                 active=False, action=source.action)
        self.slots[active_index] = Slot(active=True)

    def _promote_retained(self, retained_index: int) -> None:
        moved = self.slots[retained_index]
        if not moved.valid or moved.active:
            raise RuntimeError("INVALID_RETAINED_PROMOTION_TARGET")
        preserved = Slot(features=moved.features[:], target=moved.target[:],
                         support=moved.support, residual_ema=moved.residual_ema,
                         contradictions=moved.contradictions, last_used=self.step, active=True, action=moved.action)
        active = [(i, s) for i, s in enumerate(self.slots) if s.active]
        victim, victim_slot = min(active, key=lambda pair: (pair[1].utility(self.step), pair[0]))
        self.slots[retained_index] = Slot(
            features=victim_slot.features[:], target=victim_slot.target[:],
            support=victim_slot.support, residual_ema=victim_slot.residual_ema,
            contradictions=victim_slot.contradictions, last_used=victim_slot.last_used,
            active=False, action=victim_slot.action)
        self.slots[victim] = preserved

    def snapshot(self) -> bytes:
        if self.pending is not None:
            raise RuntimeError("CANNOT_CHECKPOINT_PENDING_OUTCOME")
        self._check_shape()
        payload = {"schema": SCHEMA, "step": self.step,
                   "partition": {"active": ACTIVE_SLOTS, "retained": RETAINED_SLOTS},
                   "slots": [asdict(s) for s in self.slots]}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        envelope = {"payload": payload, "sha256": hashlib.sha256(canonical).hexdigest()}
        return json.dumps(envelope, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

    @classmethod
    def restore(cls, raw: bytes) -> "ResidualBelief":
        try:
            envelope = json.loads(raw.decode("utf-8"))
            payload = envelope["payload"]
            canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        except Exception as exc:
            raise ValueError("CHECKPOINT_FORMAT") from exc
        if hashlib.sha256(canonical).hexdigest() != envelope.get("sha256"):
            raise ValueError("CHECKPOINT_HASH_MISMATCH")
        if payload.get("schema") != SCHEMA or payload.get("partition") != {"active": ACTIVE_SLOTS, "retained": RETAINED_SLOTS}:
            raise ValueError("CHECKPOINT_SCHEMA_OR_PARTITION")
        if not isinstance(payload.get("step"), int) or payload["step"] < 0:
            raise ValueError("CHECKPOINT_STEP")
        rows = payload.get("slots")
        if not isinstance(rows, list) or len(rows) != TOTAL_SLOTS:
            raise ValueError("CHECKPOINT_CAPACITY")
        model = cls()
        model.step = payload["step"]
        try:
            model.slots = [Slot(**row) for row in rows]
            for i, slot in enumerate(model.slots):
                if slot.active != (i < ACTIVE_SLOTS):
                    raise ValueError("CHECKPOINT_SLOT_PARTITION")
                if slot.support < 0 or slot.support > 65535 or slot.contradictions < 0 or slot.contradictions > 65535:
                    raise ValueError("CHECKPOINT_COUNTER_RANGE")
                if not math.isfinite(slot.residual_ema) or slot.residual_ema < 0:
                    raise ValueError("CHECKPOINT_RESIDUAL")
                if slot.valid:
                    if slot.action not in (0, 1, 2):
                        raise ValueError("CHECKPOINT_ACTION")
                    slot.features = list(_vector(slot.features, FEATURES, "FEATURES"))
                    slot.target = list(_vector(slot.target, TARGETS, "OUTCOME"))
                elif slot.features is not None or slot.target is not None or slot.support != 0 or slot.action is not None:
                    raise ValueError("CHECKPOINT_PARTIAL_SLOT")
        except (TypeError, KeyError) as exc:
            raise ValueError("CHECKPOINT_SLOT_FORMAT") from exc
        model._check_shape()
        return model

    def stats(self) -> dict:
        self._check_shape()
        return {"total_slots": TOTAL_SLOTS, "active_slots": ACTIVE_SLOTS,
                "retained_slots": RETAINED_SLOTS,
                "active_valid": sum(s.valid and s.active for s in self.slots),
                "retained_valid": sum(s.valid and not s.active for s in self.slots),
                "step": self.step}
