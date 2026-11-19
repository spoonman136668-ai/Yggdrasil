"""RET04: non-authorizing, independently replayable two-clock causal scores.

An opt-in measurement wrapper around the unchanged, cumulative RET03 native
learner. Stages and truth never move backward through time. No actor, source
lease, model promotion, or science qualification is granted by these hashes.
"""
from __future__ import annotations

import json
from math import isfinite

from yggdrasil.native_context_basis import canonical, digest, pin, require
from yggdrasil.native_staged_temporal import StagedTemporalReadout
from yggdrasil.native_temporal_context import MAX_NEW_EVENTS

SCHEMA = "yggdrasil.ret04.staged-prequential-receipt-shadow.v1"
MAX_COLD_BYTES = 10_000_000
ARMS = ("archive", "live", "temporal")


def _unique_pairs(pairs):
    fields = {}
    for key, value in pairs:
        require(key not in fields, "RET04_DUPLICATE_JSON_KEY")
        fields[key] = value
    return fields


def _loss(prediction, outcome):
    require(type(outcome) is int and outcome in (0, 1),
            "RET04_PUBLIC_OUTCOME_BIT")
    require(type(prediction) in (int, float) and
            isfinite(prediction) and 0 <= prediction <= 1,
            "RET04_PROBABILITY_RANGE")
    residual = prediction - outcome
    return residual * residual


class StagedScoreReceipts:
    """Observe exactly RET03's stages; score only the issued stage forecasts.

    Every receipt contains BOTH returned pre-revelation probabilities, BOTH
    actual witnessed outcomes, two-clock losses and hashes of the unchanged
    underlying native state before/after the *single* terminal update.
    """

    def __init__(self, archived_raw, latest_raw):
        require(type(archived_raw) is bytes and type(latest_raw) is bytes,
                "RET04_INPUT_CHECKPOINT_TYPE")
        self.archived_raw = archived_raw
        self.latest_raw = latest_raw
        self.model = StagedTemporalReadout(archived_raw, latest_raw)
        self.receipts = []

    def begin(self, source_id, public_views, first_action):
        return self.model.begin(source_id, public_views, first_action)

    def record_transition(self, source_id, observed_s2):
        return self.model.record_transition(source_id, observed_s2)

    def choose_second(self, source_id, second_action):
        return self.model.choose_second(source_id, second_action)

    def complete(self, source_id, witnessed_y):
        # Never recompute previous predictions after either outcome arrives.
        pending = self.model.pending
        require(pending is not None and
                pending.get("stage") == "second" and
                pending.get("source_id") == source_id,
                "RET04_TERMINAL_STAGE")
        require(type(witnessed_y) is int and witnessed_y in (0, 1),
                "RET04_TERMINAL_WITNESS_BIT")
        require(len(self.receipts) < MAX_NEW_EVENTS,
                "RET04_SOURCE_EVENT_CAP")
        s2 = pending["observed_s2"]
        first = dict(pending["transition"])
        second = dict(pending["reward"])
        # A strict time-separated Brier score: one score at each observation
        # clock. No labels feed the forecast and no post-update reforecast.
        losses = {}
        for arm in ARMS:
            transition = _loss(first[arm], s2)
            reward = _loss(second[arm], witnessed_y)
            losses[arm] = {"transition": transition,
                           "reward": reward,
                           "staged_brier": (transition + reward)/2}
        before = digest(self.model.native.checkpoint())
        # RET03 owns the one legal native admission. No alternate learner.
        stage_predictions = self.model.complete(source_id, witnessed_y)
        after = digest(self.model.native.checkpoint())
        receipt = {"source_id": source_id,
                   "transition_forecast": first,
                   "reward_forecast": second,
                   "observed_s2": s2, "observed_y": witnessed_y,
                   "losses": losses, "native_before_sha256": before,
                   "native_after_sha256": after,
                   "source_owner_authenticated": False,
                   "scientific_pass": False}
        require(pin(source_id) and
                len(self.receipts) + 1 == len(self.model.native.events),
                "RET04_CUMULATIVE_RECEIPT_ALIGNMENT")
        self.receipts.append(receipt)
        return {"transition": stage_predictions["transition"],
                "reward": stage_predictions["reward"],
                "losses": losses}

    def checkpoint(self):
        original = self.model.checkpoint()
        data = {"schema": SCHEMA,
                "original_archive_sha256": digest(self.archived_raw),
                "original_trained_sha256": digest(self.latest_raw),
                "ret03_sha256": digest(original),
                "ret03_ascii": original.decode("ascii"),
                "receipts": self.receipts,
                "accepted_native": False,
                "scientific_pass": False}
        raw = canonical(data)
        require(len(raw) <= MAX_COLD_BYTES,
                "RET04_COLD_BYTE_CAP")
        return raw

    @classmethod
    def restore(cls, raw, expected_sha256, archived_raw, latest_raw):
        require(type(raw) is bytes and len(raw) <= MAX_COLD_BYTES and
                pin(expected_sha256) and digest(raw) == expected_sha256,
                "RET04_COLD_SOURCE_SHA")
        try:
            data = json.loads(raw.decode("ascii"),
                              object_pairs_hook=_unique_pairs)
            require(type(data) is dict and set(data) == {
                "schema", "original_archive_sha256",
                "original_trained_sha256", "ret03_sha256", "ret03_ascii",
                "receipts", "accepted_native", "scientific_pass"
            } and data["schema"] == SCHEMA and
                    data["original_archive_sha256"] == digest(archived_raw) and
                    data["original_trained_sha256"] == digest(latest_raw) and
                    data["accepted_native"] is False and
                    data["scientific_pass"] is False and
                    type(data["receipts"]) is list and
                    len(data["receipts"]) <= MAX_NEW_EVENTS and
                    canonical(data) == raw, "RET04_COLD_CONTRACT")
            original = data["ret03_ascii"].encode("ascii")
            require(digest(original) == data["ret03_sha256"],
                    "RET04_RET03_BYTES_PIN")
            verified = StagedTemporalReadout.restore(
                original, data["ret03_sha256"], archived_raw, latest_raw)
            replayed = cls(archived_raw, latest_raw)
            for event in verified.native.events:
                require(type(event) is dict and
                        set(event) == {"source_id", "views", "row"},
                        "RET04_VERIFIED_EVENT_SHAPE")
                row = event["row"]
                views = tuple(tuple(v) for v in event["views"])
                ref = event["source_id"]
                replayed.begin(ref, views, row["x1"])
                replayed.record_transition(ref, row["s2"])
                replayed.choose_second(ref, row["x2"])
                replayed.complete(ref, row["y"])
            pend = verified.pending
            if pend is not None:
                ref = pend["source_id"]
                views = tuple(tuple(v) for v in pend["views"])
                replayed.begin(ref, views, pend["x1"])
                if pend["stage"] in ("transition", "second"):
                    replayed.record_transition(ref, pend["observed_s2"])
                if pend["stage"] == "second":
                    replayed.choose_second(ref, pend["x2"])
            require(replayed.model.checkpoint() == original and
                    replayed.receipts == data["receipts"] and
                    replayed.checkpoint() == raw,
                    "RET04_EXACT_WITNESS_AND_SCORE_REPLAY")
            return replayed
        except (ValueError, TypeError, KeyError, AttributeError, IndexError,
                UnicodeError, OverflowError, RecursionError) as exc:
            raise ValueError("YGG_RET04_COLD_RESTORE_REJECTED") from exc
