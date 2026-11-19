"""RET05: opt-in source-witnessed two-clock gradient for native readout.

No extra native model, external world, source actor, hidden phase identity, or
new learning-rate choice. RET04 receipts and the RET03 staged prediction API
are preserved. Only the 17 *readout* weights differ after a full witness.
"""
from __future__ import annotations

import json
from math import isfinite

from yggdrasil.native_context_basis import canonical, digest, pin, require
from yggdrasil.native_staged_score_receipts import StagedScoreReceipts
from yggdrasil.native_temporal_context import (
    LR, DECAY, MAX_WEIGHT, MAX_NEW_EVENTS, WIDTH,
)

SCHEMA = "yggdrasil.ret05.two-clock-readout-credit.source-only.v1"
MAX_BYTES = 12_000_000


def _pairs(pairs):
    obj = {}
    for key, val in pairs:
        require(key not in obj, "RET05_REPEATED_JSON_FIELD")
        obj[key] = val
    return obj


def _feature(readout, views, x1, x2):
    """Public pre-outcome features; never use the current s2 or y truth."""
    row = {"s1": views[0][0], "x1": x1, "s2": 0, "x2": x2, "y": 0}
    return readout.features(views, row)


def staged_gradient(first, second, s2, y, x_first, x_second):
    """Independent two-clock derivative of average staged squared error.

    L=( (p1-s2)^2 + (p2-y)^2 )/2, p_j=w_j*A_j+(1-w_j)*B_j,
    w_j=sigmoid(theta·feature_j). The two weights are *stage-specific*;
    neither forecast may be recomputed with a later revealed outcome.
    """
    require(type(s2) is int and s2 in (0, 1) and
            type(y) is int and y in (0, 1), "RET05_WITNESSED_BITS")
    require(len(x_first) == WIDTH and len(x_second) == WIDTH and
            all(type(v) in (float, int) and isfinite(v) and abs(v) <= 1
                for v in (*x_first, *x_second)),
            "RET05_STAGE_FEATURE_SHAPE")
    result = [0.0] * WIDTH
    for issued, truth, features in ((first, s2, x_first),
                                    (second, y, x_second)):
        require(type(issued) is dict and
                {"archive", "live", "temporal", "archive_weight"}
                == set(issued), "RET05_STAGE_FORECAST_SHAPE")
        archive, live, prediction = (
            issued["archive"], issued["live"], issued["temporal"])
        w = issued["archive_weight"]
        require(all(type(v) is float and isfinite(v) and 0 <= v <= 1
                    for v in (archive, live, prediction, w)) and
                1/32 <= w <= 31/32 and
                prediction == w*archive + (1-w)*live,
                "RET05_ISSUED_MIXTURE_IDENTITY")
        coeff = (prediction-truth) * (archive-live) * w * (1-w)
        for i, feature in enumerate(features):
            result[i] += coeff * feature
    require(all(isfinite(x) for x in result),
            "RET05_FINITE_GRADIENT")
    return tuple(result)


class StagedCreditReadout(StagedScoreReceipts):
    """Replace ONLY RET02's postreveal readout update with true staged credit.

    The original RET02 native reader still sees each original source event
    exactly ONCE at terminal completion. Its causal basis, specialist heads,
    consumed source IDs and pretraining are not reset or overwritten.
    """

    def __init__(self, archived_raw, latest_raw):
        super().__init__(archived_raw, latest_raw)
        self.credit = []
        self._first_features = None
        self._second_features = None

    def begin(self, source_id, public_views, first_action):
        out = super().begin(source_id, public_views, first_action)
        self._first_features = _feature(self.model.native, public_views,
                                        first_action, 0)
        self._second_features = None
        return out

    def choose_second(self, source_id, second_action):
        out = super().choose_second(source_id, second_action)
        p = self.model.pending
        views = tuple(tuple(v) for v in p["views"])
        self._second_features = _feature(self.model.native, views,
                                         p["x1"], second_action)
        return out

    def complete(self, source_id, witnessed_y):
        p = self.model.pending
        require(p is not None and p["stage"] == "second" and
                p["source_id"] == source_id and
                type(witnessed_y) is int and witnessed_y in (0, 1) and
                self._first_features is not None and
                self._second_features is not None and
                len(self.credit) == len(self.receipts) and
                len(self.credit) < MAX_NEW_EVENTS,
                "RET05_TERMINAL_CREDIT_CUSTODY")
        readout = self.model.native
        old_weights = tuple(readout.weights)
        grad = staged_gradient(p["transition"], p["reward"],
                               p["observed_s2"], witnessed_y,
                               self._first_features, self._second_features)
        replacement = tuple(
            max(-MAX_WEIGHT, min(MAX_WEIGHT,
                old - LR*(grad[i] + (DECAY*old if i else 0.0))))
            for i, old in enumerate(old_weights))
        require(len(replacement) == WIDTH and
                all(type(v) is float and isfinite(v) for v in replacement),
                "RET05_READOUT_WEIGHT_BOUNDS")
        # Validate and compute BEFORE the one original terminal admission.
        # The original RET02 postreveal readout update happens internally,
        # then ONLY its 17 readout numbers are replaced by issued-clock
        # gradient credit. The native and all six specialists are unaffected.
        out = super().complete(source_id, witnessed_y)
        intermediate = digest(readout.checkpoint())
        readout.weights = list(replacement)
        final = digest(readout.checkpoint())
        self.credit.append({
            "source_id": source_id,
            "gradient": list(grad),
            "readout_before": list(old_weights),
            "readout_after": list(replacement),
            "original_after_sha256": intermediate,
            "staged_after_sha256": final,
            "stage_losses": self.receipts[-1]["losses"],
            "source_owner_authenticated": False,
            "scientific_pass": False,
        })
        self._first_features = None
        self._second_features = None
        return out

    def checkpoint(self):
        raw_original = self.model.checkpoint()
        data = {
            "schema": SCHEMA,
            "original_archive_sha256": digest(self.archived_raw),
            "original_trained_sha256": digest(self.latest_raw),
            "ret03_sha256": digest(raw_original),
            "ret03_ascii": raw_original.decode("ascii"),
            "ret04_receipts": self.receipts,
            "staged_credit": self.credit,
            "accepted_native": False,
            "scientific_pass": False,
        }
        raw = canonical(data)
        require(len(raw) <= MAX_BYTES, "RET05_COLD_BYTE_CAP")
        return raw

    @classmethod
    def restore(cls, raw, expected_sha256, archived_raw, latest_raw):
        require(type(raw) is bytes and len(raw) <= MAX_BYTES and
                pin(expected_sha256) and digest(raw) == expected_sha256,
                "RET05_COLD_SOURCE_PIN")
        try:
            data = json.loads(raw.decode("ascii"), object_pairs_hook=_pairs)
            require(type(data) is dict and set(data) == {
                "schema", "original_archive_sha256",
                "original_trained_sha256", "ret03_sha256", "ret03_ascii",
                "ret04_receipts", "staged_credit",
                "accepted_native", "scientific_pass"
            } and data["schema"] == SCHEMA and
                    data["original_archive_sha256"] == digest(archived_raw) and
                    data["original_trained_sha256"] == digest(latest_raw) and
                    data["accepted_native"] is False and
                    data["scientific_pass"] is False and
                    type(data["ret04_receipts"]) is list and
                    type(data["staged_credit"]) is list and
                    len(data["ret04_receipts"]) <= MAX_NEW_EVENTS and
                    len(data["staged_credit"]) <= MAX_NEW_EVENTS and
                    canonical(data) == raw, "RET05_COLD_CANONICAL")
            original = data["ret03_ascii"].encode("ascii")
            require(digest(original) == data["ret03_sha256"],
                    "RET05_ORIGINAL_CHECKPOINT_PIN")
            original_state = json.loads(original.decode("ascii"),
                                        object_pairs_hook=_pairs)
            base = json.loads(original_state["native_ascii"],
                              object_pairs_hook=_pairs)
            events = base["events"]
            require(type(events) is list and len(events) <= MAX_NEW_EVENTS,
                    "RET05_SOURCE_TAPE_BUDGET")
            restored = cls(archived_raw, latest_raw)
            for event in events:
                require(type(event) is dict and
                        set(event) == {"source_id", "views", "row"},
                        "RET05_WITNESS_SCHEMA")
                ref = event["source_id"]
                views = tuple(tuple(v) for v in event["views"])
                row = event["row"]
                restored.begin(ref, views, row["x1"])
                restored.record_transition(ref, row["s2"])
                restored.choose_second(ref, row["x2"])
                restored.complete(ref, row["y"])
            p = original_state["pending"]
            if p is not None:
                ref = p["source_id"]
                views = tuple(tuple(v) for v in p["views"])
                restored.begin(ref, views, p["x1"])
                if p["stage"] in ("transition", "second"):
                    restored.record_transition(ref, p["observed_s2"])
                if p["stage"] == "second":
                    restored.choose_second(ref, p["x2"])
            require(restored.model.checkpoint() == original and
                    restored.receipts == data["ret04_receipts"] and
                    restored.credit == data["staged_credit"] and
                    restored.checkpoint() == raw,
                    "RET05_EXACT_CAUSAL_COLD_REPLAY")
            return restored
        except (ValueError, KeyError, TypeError, AttributeError, IndexError,
                UnicodeError, RecursionError, OverflowError) as exc:
            raise ValueError("YGG_RET05_COLD_RESTORE_REJECTED") from exc
