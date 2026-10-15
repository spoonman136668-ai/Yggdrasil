"""Y-F28 development preflight: physical two-read sensor custody.

This module does not implement or qualify a learned information-value policy.
No evaluation truth, unpurchased target channel, or source descriptor enters
an action-selection callback. Source generators and neural optimization are
separate gates and must be frozen before the original experiment.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from typing import Callable

SOURCES = 4
READ_BUDGET = 2
NATIVE_CAP = 576


class CustodyViolation(ValueError):
    pass


@dataclass(frozen=True)
class PublicSensorInfo:
    # Training-anchored reliability only; not a target measurement.
    reliability: tuple[float, float, float, float]
    missingness: tuple[float, float, float, float]


@dataclass(frozen=True)
class PurchasedReading:
    sensor: int
    value: float


@dataclass(frozen=True)
class Receipt:
    trace: tuple[PurchasedReading, PurchasedReading]
    first_action: int
    second_action: int
    physical_reads: int
    native_bytes: int
    calibration_bytes: int


class _SensorPort:
    """The policy sees only purchased values, never this port or its tape."""
    def __init__(self, latent: tuple[float, float, float, float]):
        if len(latent) != SOURCES or not all(isfinite(x) for x in latent):
            raise CustodyViolation("invalid latent channel vector")
        self._latent = latent
        self._used: set[int] = set()
        self._trace: list[PurchasedReading] = []

    def acquire(self, sensor: int) -> PurchasedReading:
        if type(sensor) is not int or sensor not in range(SOURCES):
            raise CustodyViolation("invalid channel identifier")
        if len(self._trace) >= READ_BUDGET or sensor in self._used:
            raise CustodyViolation("read budget exceeded or source reacquired")
        reading = PurchasedReading(sensor, self._latent[sensor])
        self._used.add(sensor)
        self._trace.append(reading)
        return reading


def evaluate_policy(
    target_channels: tuple[float, float, float, float],
    public: PublicSensorInfo,
    first_policy: Callable[[PublicSensorInfo], int],
    second_policy: Callable[[PublicSensorInfo, PurchasedReading], int],
    native_bytes: int,
    calibration_bytes: int,
) -> Receipt:
    """Invoke callback after actual first read, not with full channel tensor.

    This function does not give the truth label to policies. Measured resource
    costs are included in the receipt; calibrator bytes are outside native core.
    """
    if not 0 <= native_bytes <= NATIVE_CAP or calibration_bytes < 0:
        raise CustodyViolation("state or calibration budget not accounted")
    if len(public.reliability) != SOURCES or len(public.missingness) != SOURCES:
        raise CustodyViolation("invalid public sensor metadata")
    if not all(isfinite(x) for x in (*public.reliability, *public.missingness)):
        raise CustodyViolation("nonfinite calibration")
    port = _SensorPort(target_channels)
    first_action = first_policy(public)
    first = port.acquire(first_action)
    second_action = second_policy(public, first)
    second = port.acquire(second_action)
    trace = (first, second)
    if len(port._trace) != READ_BUDGET or first.sensor == second.sensor:
        raise CustodyViolation("two distinct channels were not acquired")
    return Receipt(trace, first.sensor, second.sensor, len(port._trace), native_bytes, calibration_bytes)


def static_first(public: PublicSensorInfo) -> int:
    return max(range(SOURCES), key=lambda j: (abs(public.reliability[j]) - .1 * public.missingness[j], -j))


def static_second(public: PublicSensorInfo, first: PurchasedReading) -> int:
    return max((j for j in range(SOURCES) if j != first.sensor),
               key=lambda j: (abs(public.reliability[j]) - .1 * public.missingness[j], -j))


def action_switch_rate(receipts: tuple[Receipt, ...]) -> float:
    """Diagnostic only: pair receipts where the same first sensor differs in value.

    Zero is not automatically a failure for a calibrated static control, but
    a claimed evidence-conditional learned policy must show causal switching.
    """
    if len(receipts) % 2:
        raise CustodyViolation("need paired first-reading interventions")
    switched = 0
    for i in range(0, len(receipts), 2):
        a,b = receipts[i:i + 2]
        if a.first_action != b.first_action or a.trace[0].value == b.trace[0].value:
            raise CustodyViolation("counterfactual pair not aligned")
        switched += a.second_action != b.second_action
    return switched / (len(receipts) // 2) if receipts else 0.0


def validate_disjoint(train: dict[str, set[int]], test: dict[str, set[int]]) -> None:
    for key in ("seeds", "entities", "families"):
        a, b = train.get(key, set()), test.get(key, set())
        if not a or not b or a & b:
            raise CustodyViolation(f"invalid disjoint {key} split")
