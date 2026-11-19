"""Opt-in evidence-gated cold causal readout retention for native Yggdrasil.

One existing trained native + six-head cumulative learner continues witnessing
real PUBLIC intervention outcomes. The original archived native readout is
immutably pinned, with an evidence-only Bayesian gate; there are no hidden
world labels, accepted-model mutations, new controllers, or science promotion.

The two newer future-state heads persist but do not update in THIS test:
there is no precommitted 3-step future-target curriculum in the new source.
"""
from __future__ import annotations

import json
from math import isfinite

from yggdrasil.native_context_basis import canonical, digest, pin, require
from yggdrasil.native_jepa_temporal import NativeTemporalMultiLearner
from yggdrasil.native_jepa_future import NativeFutureStateLearner

SCHEMA = "yggdrasil.ret01.evidence-readout.v1"
PRIOR_ARCHIVED = 0.125
POSTERIOR_FLOOR = 1 / 32
POSTERIOR_CEIL = 31 / 32
MAX_NEW_EVENTS = 64
MAX_HISTORICAL_PROBES = 32
MAX_COLD_BYTES = 2_000_000


def _public(views, row):
    require(type(views) is tuple and len(views) == 2 and
            all(type(v) is tuple and len(v) == 2 and
                all(type(bit) is int and bit in (0, 1) for bit in v)
                for v in views), "RET01_PUBLIC_VIEWS")
    require(type(row) is dict and set(row) == {"s1", "x1", "s2", "x2", "y"} and
            all(type(x) is int and x in (0, 1) for x in row.values()),
            "RET01_PUBLIC_ROW")
    return views


def _forecast(native, views, row):
    view = views[0]
    a = float(native.context_forecast(view, row["x1"]))
    b = float(native.context_forecast(
        view, row["x1"], row["s2"], row["x2"]))
    require(isfinite(a) and isfinite(b) and 0 <= a <= 1 and 0 <= b <= 1,
            "RET01_FORECAST_RANGE")
    return a, b


def brier(pred, row):
    return ((pred[0] - row["s2"])**2 + (pred[1] - row["y"])**2) / 2


def _likelihood(pred, row):
    a, b = pred
    return ((a if row["s2"] else 1-a) *
            (b if row["y"] else 1-b))


def _advance(weight, archive, live, row):
    a, b = weight * _likelihood(archive, row), (1-weight) * _likelihood(live, row)
    require(a+b > 0, "RET01_ZERO_EVIDENCE_LIKELIHOOD")
    return min(POSTERIOR_CEIL, max(POSTERIOR_FLOOR, a/(a+b)))


def _event(identifier, views, row):
    require(pin(identifier), "RET01_EVENT_ID")
    _public(views, row)
    return {"source_id": identifier,
            "views": [list(view) for view in views],
            "row": dict(row)}


def _decode(e):
    require(type(e) is dict and set(e)=={"source_id","views","row"},
            "RET01_COLD_EVENT_FIELDS")
    return e["source_id"], tuple(tuple(v) for v in e["views"]), e["row"]


class ArchivedEvidenceReadout:
    """A pinned historical native reader, a LIVE cumulative learner, one gate."""

    def __init__(self, archived_raw, latest_raw):
        require(type(archived_raw) is bytes and type(latest_raw) is bytes,
                "RET01_INPUT_CHECKPOINT_TYPE")
        self.archive_sha = digest(archived_raw)
        self.initial_live_sha = digest(latest_raw)
        self.archived = NativeTemporalMultiLearner.restore(
            archived_raw, self.archive_sha)
        self.current = NativeFutureStateLearner.restore(
            latest_raw, self.initial_live_sha)
        old = self.archived.base.native._ledger
        live = self.current.original.base.native._ledger
        require(len(old) > 600 and len(live)>len(old) and
                tuple(live[:len(old)])==old,
                "RET01_CUMULATIVE_OLD_SOURCE_PREFIX")
        self.archived_count = len(old)
        self.initial_live_count = len(live)
        self.posterior = PRIOR_ARCHIVED
        self.negative_posterior = PRIOR_ARCHIVED
        self.negative_previous = None
        self.new_events = []
        self.old_probe_events = []

    def forecast(self, views, row):
        _public(views, row)
        frozen = _forecast(self.archived.base.native, views, row)
        live = _forecast(self.current.original.base.native, views, row)
        weight = self.posterior
        negative = self.negative_posterior
        return {
            "archive": frozen,
            "live": live,
            "gate": tuple(weight*f + (1-weight)*q
                          for f, q in zip(frozen, live)),
            "fixed_half": tuple((f+q)/2 for f,q in zip(frozen,live)),
            "mispaired_gate": tuple(negative*f+(1-negative)*q
                                    for f,q in zip(frozen,live)),
            "chance": (0.5,0.5),
        }

    def _score_after_revelation(self, forecast, row):
        original = forecast["archive"], forecast["live"]
        self.posterior = _advance(self.posterior, *original, row)
        # Exactly one intentionally mismatched past observed outcome; no
        # oracle label, future answer, or hidden regime enters this control.
        neg = self.negative_previous if self.negative_previous is not None else {
            **row, "s2": 1-row["s2"], "y": 1-row["y"]}
        self.negative_posterior = _advance(
            self.negative_posterior, *original, neg)
        self.negative_previous = dict(row)

    def observe(self, identifier, views, row, *, historical=False):
        """Atomic native update for new evidence; historical diagnostic read-only.

        Historical readout evidence may update the selector but not any
        learner; only a source-id-aligned OLD witnessed original is admitted.
        """
        event = _event(identifier, views, row)
        if historical:
            require(len(self.old_probe_events)<MAX_HISTORICAL_PROBES,
                    "RET01_HISTORICAL_PROBE_LIMIT")
            native_record = self.archived.base.native._ids.get(identifier)
            require(native_record == (identifier, views, row["x1"],
                                      row["s2"], row["x2"], row["y"]),
                    "RET01_OLD_PROBE_SOURCE_WITNESS")
            require(identifier not in {e["source_id"] for e in self.old_probe_events},
                    "RET01_REPEATED_HISTORICAL_PROBE")
            pred = self.forecast(views, row)
            self._score_after_revelation(pred, row)
            self.old_probe_events.append(event)
            return pred

        seen = self.current.original.base.native._ids.get(identifier)
        if seen is not None:
            require(seen == (identifier, views, row["x1"],
                             row["s2"], row["x2"], row["y"]),
                    "RET01_CONFLICTING_NATIVE_SOURCE")
            return None
        require(len(self.new_events)<MAX_NEW_EVENTS,
                "RET01_NEW_WITNESS_BUDGET")
        # Construct the next entire current trained model BEFORE mutating the
        # live object or evidence posterior; invalid rows fail atomically.
        updated = self.current.original.observe(identifier, views, row)
        pred = self.forecast(views, row)
        self._score_after_revelation(pred, row)
        self.current.original = updated
        self.new_events.append(event)
        require(tuple(self.current.original.base.native._ledger[:self.initial_live_count])
                == tuple(self.archived.base.native._ledger[:self.archived_count]) +
                tuple(self.current.original.base.native._ledger[
                      self.archived_count:self.initial_live_count]),
                "RET01_PREFIX_RETENTION")
        return pred

    def checkpoint(self):
        current = self.current.checkpoint()
        d = {"schema": SCHEMA, "archive_sha256": self.archive_sha,
             "initial_live_sha256": self.initial_live_sha,
             "current_sha256": digest(current),
             "current_ascii": current.decode("ascii"),
             "posterior": self.posterior,
             "negative_posterior": self.negative_posterior,
             "negative_previous": self.negative_previous,
             "new_events": self.new_events,
             "old_probe_events": self.old_probe_events}
        raw = canonical(d)
        require(len(raw)<=MAX_COLD_BYTES, "RET01_BOUNDED_COLD_BYTES")
        return raw

    @classmethod
    def restore(cls, raw, expected_sha256, archived_raw, latest_raw):
        require(type(raw) is bytes and len(raw)<=MAX_COLD_BYTES
                and pin(expected_sha256) and digest(raw)==expected_sha256,
                "RET01_COLD_SOURCE_SHA")
        try:
            data = json.loads(raw.decode("ascii"))
            require(type(data) is dict and set(data)=={
                "schema","archive_sha256","initial_live_sha256",
                "current_sha256","current_ascii","posterior",
                "negative_posterior","negative_previous",
                "new_events","old_probe_events"
            } and data["schema"] == SCHEMA and canonical(data)==raw
            and data["archive_sha256"]==digest(archived_raw)
            and data["initial_live_sha256"]==digest(latest_raw),
                    "RET01_COLD_SOURCE_CONTRACT")
            reader=cls(archived_raw, latest_raw)
            for entry in data["new_events"]:
                reader.observe(*_decode(entry))
            for entry in data["old_probe_events"]:
                reader.observe(*_decode(entry),historical=True)
            require(reader.current.checkpoint().decode("ascii")==data["current_ascii"]
                    and digest(reader.current.checkpoint())==data["current_sha256"]
                    and abs(reader.posterior-data["posterior"])<=1e-14
                    and abs(reader.negative_posterior-data["negative_posterior"])<=1e-14
                    and reader.negative_previous==data["negative_previous"]
                    and reader.checkpoint()==raw,"RET01_WITNESSED_REPLAY_PARITY")
            return reader
        except (ValueError, TypeError, KeyError, AttributeError, OverflowError,
                UnicodeError, RecursionError) as exc:
            raise ValueError("YGG_RET01_COLD_RESTORE_REJECTED") from exc

