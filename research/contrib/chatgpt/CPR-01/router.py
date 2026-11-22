"""CPR-01: research-only binary conformal sidecar for immutable specialists.

No native checkpoint edits, oracle regime labels, training, or automatic spawning.
Finite-sample conformal coverage does not guarantee regime detection or revival.
"""
from collections import deque
from dataclasses import dataclass
from hashlib import sha256
import json
from math import ceil

SCALE = 1_000_000
SCHEMA = "yggdrasil.cpr01.binary-router.v1"


def _pin(value):
    return (type(value) is str and len(value) == 64
            and all(char in "0123456789abcdef" for char in value))


def _prob(value):
    if type(value) is not int or not 0 <= value <= SCALE:
        raise ValueError("CPR_PROBABILITY")
    return value


def _label(value):
    if type(value) is not int or value not in (0, 1):
        raise ValueError("CPR_LABEL")
    return value


def nonconformity(probability, label):
    """Inverse true-label probability in integer millionths."""
    p = _prob(probability)
    return p if _label(label) == 0 else SCALE - p


@dataclass(frozen=True)
class FrozenCalibration:
    name: str
    model_sha256: str
    calibration_sha256: str
    alpha_percent: int
    threshold: int
    sample_size: int

    @classmethod
    def from_holdout(cls, name, model_sha256, calibration_sha256,
                     probabilities, labels, *, alpha_percent):
        if (type(name) is not str or not name or not _pin(model_sha256)
                or not _pin(calibration_sha256)
                or model_sha256 == calibration_sha256
                or alpha_percent not in (5, 10)
                or type(alpha_percent) is not int):
            raise ValueError("CPR_CALIBRATION_IDENTITY")
        predictions, observations = tuple(probabilities), tuple(labels)
        n = len(observations)
        if n < 1 or n > 250 or n != len(predictions):
            raise ValueError("CPR_CALIBRATION_LENGTH")
        scores = sorted(nonconformity(p, y)
                        for p, y in zip(predictions, observations, strict=True))
        # Exact kth order statistic of n scores + one infinity sentinel.
        k = ceil((n + 1) * (100 - alpha_percent) / 100)
        threshold = scores[k - 1] if k <= n else SCALE + 1
        return cls(name, model_sha256, calibration_sha256,
                   alpha_percent, threshold, n)

    def validate(self):
        if (type(self.name) is not str or not self.name
                or not _pin(self.model_sha256)
                or not _pin(self.calibration_sha256)
                or self.model_sha256 == self.calibration_sha256
                or type(self.alpha_percent) is not int
                or self.alpha_percent not in (5, 10)
                or type(self.sample_size) is not int
                or not 1 <= self.sample_size <= 250
                or type(self.threshold) is not int
                or not 0 <= self.threshold <= SCALE + 1):
            raise ValueError("CPR_CALIBRATION_INVALID")
        return self


class ConformalRouter:
    """One outcome target; predict first and observe the same public outcome later.

    A source owner must independently establish holdout disjointness. Pins alone
    are identities, not proof the holdout was excluded from fitting.
    """
    def __init__(self, calibrations, *, window=8):
        frozen = tuple(calibrations)
        if (window not in (1, 8) or type(window) is not int
                or not frozen or len({c.name for c in frozen}) != len(frozen)):
            raise ValueError("CPR_CONFIGURATION")
        for c in frozen:
            c.validate()
        if len({c.alpha_percent for c in frozen}) != 1:
            raise ValueError("CPR_ALPHA_MISMATCH")
        self.calibrations = tuple(sorted(frozen, key=lambda c: c.name))
        self.window = window
        self.history = {c.name: deque(maxlen=window) for c in frozen}
        self.missing_streak = 0
        self._pending = None
        self._alarm_sent = False

    def route(self, probabilities):
        """Route using only public predictions and *past* witnessed coverage."""
        if self._pending is not None or type(probabilities) is not dict:
            raise ValueError("CPR_PENDING_OR_FORECAST")
        if set(probabilities) != set(self.history):
            raise ValueError("CPR_EXPERT_SET")
        eligible = []
        for c in self.calibrations:
            p = _prob(probabilities[c.name])
            size = int(p <= c.threshold) + int(SCALE - p <= c.threshold)
            old = self.history[c.name]
            # W8 >= 6/8; W1 must cover its one previous outcome.
            min_count = 6 if self.window == 8 else 1
            coverage_ok = len(old) < self.window or sum(old) >= min_count
            if size and coverage_ok:
                eligible.append((size, c.name))
        chosen = min(eligible)[1] if eligible else None
        self.missing_streak = 0 if chosen is not None else self.missing_streak + 1
        triggered = chosen is None and self.missing_streak >= self.window and not self._alarm_sent
        self._alarm_sent = self.missing_streak >= self.window
        self._pending = dict(probabilities)
        return {"selected": chosen, "eligible": len(eligible),
                "speciation_signal": triggered}

    def observe(self, revealed_label):
        """Update every frozen expert, including previously abstaining experts."""
        if self._pending is None:
            raise ValueError("CPR_UNMATCHED_OUTCOME")
        y = _label(revealed_label)
        for c in self.calibrations:
            p = self._pending[c.name]
            self.history[c.name].append(int(nonconformity(p, y) <= c.threshold))
        self._pending = None

    def checkpoint(self):
        """Independent readout sidecar: never changes original model checkpoint."""
        if self._pending is not None:
            raise ValueError("CPR_INFLIGHT_CHECKPOINT")
        payload = {"schema": SCHEMA, "window": self.window,
                   "calibrations": [vars(c) for c in self.calibrations],
                   "history": {name: list(values)
                               for name, values in sorted(self.history.items())},
                   "missing_streak": self.missing_streak,
                   "alarm_sent": self._alarm_sent}
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

    @classmethod
    def restore(cls, raw, expected_sha256, *, model_pins):
        if (type(raw) is not bytes or not _pin(expected_sha256)
                or sha256(raw).hexdigest() != expected_sha256):
            raise ValueError("CPR_SIDECAR_PIN")
        try:
            data = json.loads(raw)
            if (data["schema"] != SCHEMA or
                    set(data) != {"schema", "window", "calibrations", "history",
                                  "missing_streak", "alarm_sent"}):
                raise ValueError("CPR_SIDECAR_SCHEMA")
            frozen = tuple(FrozenCalibration(**item) for item in data["calibrations"])
            router = cls(frozen, window=data["window"])
            if ({c.name: c.model_sha256 for c in frozen} != model_pins
                    or set(data["history"]) != set(router.history)):
                raise ValueError("CPR_MODEL_PIN_MISMATCH")
            for name, values in data["history"].items():
                if (type(values) is not list or len(values) > router.window
                        or any(type(v) is not int or v not in (0, 1) for v in values)):
                    raise ValueError("CPR_HISTORY_INVALID")
                router.history[name].extend(values)
            missing = data["missing_streak"]
            alarm = data["alarm_sent"]
            if (type(missing) is not int or missing < 0
                    or type(alarm) is not bool
                    or alarm != (missing >= router.window)):
                raise ValueError("CPR_STREAK_INVALID")
            router.missing_streak = missing
            router._alarm_sent = alarm
            if router.checkpoint() != raw:
                raise ValueError("CPR_NONCANONICAL")
            return router
        except (TypeError, KeyError, ValueError) as exc:
            raise ValueError("CPR_SIDECAR_INVALID") from exc
