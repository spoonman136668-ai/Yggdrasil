"""Y2-CCE01: bounded online causal-contract hypothesis ecology (development only).

No transformer, tokens, oracle identities, gradient updates, external data, or
automatic promotion. All hypotheses see only validated public (bits, action,
outcome) events. A central bounded selector is intentionally disclosed: this
pilot does not demonstrate completely decentralized structural decisions.
"""

from __future__ import annotations

import hashlib
import json
import math

MAX_EVENTS = 65535
SCHEMA = "yggdrasil.y2.cce01.v1"


def _bit(value: int) -> bool:
    return type(value) is int and value in (0, 1)


def validate_event(bits: tuple[int, int], action: int,
                   outcome: int | None = None) -> None:
    if (type(bits) is not tuple or len(bits) != 2
            or not all(_bit(v) for v in bits)
            or not _bit(action)
            or (outcome is not None and not _bit(outcome))):
        raise ValueError("CCE01_PUBLIC_EVENT_INVALID")


class CountModel:
    """One bounded Bernoulli contract keyed by selected public features + action."""

    def __init__(self, features: tuple[int, ...] = ()) -> None:
        if (type(features) is not tuple or len(features) > 2
                or any(type(f) is not int or f not in (0, 1) for f in features)
                or len(set(features)) != len(features)):
            raise ValueError("CCE01_FEATURES_INVALID")
        self.features = features
        self.counts: dict[tuple[int, ...], list[int]] = {}
        self.prequential_brier = 0.0
        self.events = 0

    def _key(self, bits: tuple[int, int], action: int) -> tuple[int, ...]:
        return tuple(bits[f] for f in self.features) + (action,)

    def predict(self, bits: tuple[int, int], action: int) -> float:
        validate_event(bits, action)
        failures, successes = self.counts.get(self._key(bits, action), (0, 0))
        return (successes + 1) / (failures + successes + 2)

    def observe(self, bits: tuple[int, int], action: int, outcome: int) -> None:
        validate_event(bits, action, outcome)
        if not _bit(outcome):
            raise ValueError("CCE01_PUBLIC_OUTCOME_INVALID")
        if self.events >= MAX_EVENTS:
            raise ValueError("CCE01_EVENT_BUDGET_EXCEEDED")
        forecast = self.predict(bits, action)
        self.prequential_brier += (forecast - outcome) ** 2
        key = self._key(bits, action)
        counts = self.counts.setdefault(key, [0, 0])
        counts[outcome] += 1
        self.events += 1

    def snapshot(self) -> dict:
        return {
            "features": list(self.features),
            "counts": [[list(key), list(value)]
                       for key, value in sorted(self.counts.items())],
            "prequential_brier": self.prequential_brier,
            "events": self.events,
        }

    @classmethod
    def from_snapshot(cls, state: dict) -> "CountModel":
        if (type(state) is not dict
                or set(state) != {"features", "counts", "prequential_brier",
                                  "events"}
                or type(state["features"]) is not list
                or type(state["counts"]) is not list):
            raise ValueError("CCE01_MODEL_STATE_INVALID")
        model = cls(tuple(state["features"]))
        events = state["events"]
        loss = state["prequential_brier"]
        if (type(events) is not int or not 0 <= events <= MAX_EVENTS
                or type(loss) not in (float, int)
                or not math.isfinite(loss) or not 0 <= loss <= events):
            raise ValueError("CCE01_MODEL_METRICS_INVALID")
        for item in state["counts"]:
            if (type(item) is not list or len(item) != 2
                    or type(item[0]) is not list or type(item[1]) is not list):
                raise ValueError("CCE01_MODEL_COUNTS_INVALID")
            key, value = item
            if (len(key) != len(model.features) + 1
                    or any(not _bit(v) for v in key)
                    or len(value) != 2
                    or any(type(v) is not int or not 0 <= v <= MAX_EVENTS
                           for v in value)):
                raise ValueError("CCE01_MODEL_COUNTS_INVALID")
            frozen_key = tuple(key)
            if frozen_key in model.counts:
                raise ValueError("CCE01_DUPLICATE_KEY")
            model.counts[frozen_key] = value[:]
        if sum(sum(v) for v in model.counts.values()) != events:
            raise ValueError("CCE01_COUNT_TOTAL_MISMATCH")
        model.events = events
        model.prequential_brier = float(loss)
        return model


class CausalContractEcology:
    """Two competing singleton-feature contracts versus pooled action memory.

    The split gate uses only pre-update losses, public arm coverage and fixed
    thresholds. Hypotheses are not given the generator's rule or hidden state.
    This first experiment does not demonstrate local identity discovery,
    multi-step planning, automatic graph growth or scientific transfer.
    """

    def __init__(self) -> None:
        self.pooled = CountModel()
        self.candidates = (CountModel((0,)), CountModel((1,)))
        self.selected_feature: int | None = None
        self.events = 0
        self.selection_step: int | None = None

    def predict(self, bits: tuple[int, int], action: int) -> float:
        validate_event(bits, action)
        model = (self.pooled if self.selected_feature is None
                 else self.candidates[self.selected_feature])
        return model.predict(bits, action)

    def observe(self, bits: tuple[int, int], action: int, outcome: int) -> None:
        validate_event(bits, action, outcome)
        if not _bit(outcome):
            raise ValueError("CCE01_PUBLIC_OUTCOME_INVALID")
        if self.events >= MAX_EVENTS:
            raise ValueError("CCE01_EVENT_BUDGET_EXCEEDED")
        for model in (self.pooled, *self.candidates):
            model.observe(bits, action, outcome)
        self.events += 1
        if self.selected_feature is not None or self.events < 48:
            return
        options = []
        for index, model in enumerate(self.candidates):
            covered = all(
                sum(model.counts.get((bit, arm), (0, 0))) >= 6
                for bit in (0, 1) for arm in (0, 1)
            )
            gain = self.pooled.prequential_brier - model.prequential_brier
            if covered and gain >= max(2.0, 0.01 * self.events):
                options.append((gain, index))
        if options:
            self.selected_feature = sorted(options, key=lambda x: (-x[0], x[1]))[0][1]
            self.selection_step = self.events

    def snapshot(self) -> bytes:
        body = json.dumps({
            "schema": SCHEMA, "events": self.events,
            "selected_feature": self.selected_feature,
            "selection_step": self.selection_step,
            "pooled": self.pooled.snapshot(),
            "candidates": [cell.snapshot() for cell in self.candidates],
        }, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        return b"CCE01." + hashlib.sha256(body).hexdigest().encode("ascii") + b"." + body

    @classmethod
    def restore(cls, checkpoint: bytes) -> "CausalContractEcology":
        if type(checkpoint) is not bytes:
            raise ValueError("CCE01_CHECKPOINT_REJECTED")
        parts = checkpoint.split(b".", 2)
        if (len(parts) != 3 or parts[0] != b"CCE01"
                or len(parts[1]) != 64
                or hashlib.sha256(parts[2]).hexdigest().encode("ascii") != parts[1]):
            raise ValueError("CCE01_CHECKPOINT_REJECTED")
        try:
            state = json.loads(parts[2])
            if (type(state) is not dict
                    or set(state) != {"schema", "events", "selected_feature",
                                      "selection_step", "pooled", "candidates"}
                    or state["schema"] != SCHEMA
                    or type(state["candidates"]) is not list
                    or len(state["candidates"]) != 2):
                raise ValueError("CCE01_CHECKPOINT_SCHEMA_INVALID")
            result = cls()
            result.pooled = CountModel.from_snapshot(state["pooled"])
            result.candidates = tuple(CountModel.from_snapshot(item)
                                      for item in state["candidates"])
            if (result.pooled.features != ()
                    or [m.features for m in result.candidates] != [(0,), (1,)]):
                raise ValueError("CCE01_CHECKPOINT_FEATURES_INVALID")
            result.events = state["events"]
            result.selected_feature = state["selected_feature"]
            result.selection_step = state["selection_step"]
            if (type(result.events) is not int
                    or not 0 <= result.events <= MAX_EVENTS
                    or any(m.events != result.events
                           for m in (result.pooled, *result.candidates))
                    or (result.selected_feature is not None
                        and (type(result.selected_feature) is not int
                             or result.selected_feature not in (0, 1)))
                    or ((result.selected_feature is None) !=
                        (result.selection_step is None))
                    or (result.selection_step is not None
                        and (type(result.selection_step) is not int
                             or not 48 <= result.selection_step <= result.events))):
                raise ValueError("CCE01_CHECKPOINT_STATE_INVALID")
            return result
        except (KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("CCE01_CHECKPOINT_REJECTED") from exc
