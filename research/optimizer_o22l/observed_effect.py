"""O22-L source-only observer: chosen R10 public effect provenance, no original episodes.

The experimental fast/slow count weights are fixed for a unit certificate.
This is an additive research prototype, not native architectural novelty.
R10, R11, R12 and protected evaluation remain unchanged.
"""
from __future__ import annotations

import hashlib
import json
import math
from research.native.itd02.r10.public_adapter import (
    ACTION_NAMES, DoorKeyPublicAdapter, canonical, digest, public_cues,
)
from research.native.itd02.r11.affordance_cells import _feature

SCHEMA = "optimizer.o22l.source-public-effect.v1"
DECAY = 0.5
FAST_WEIGHT = 0.85
MAX_CONTEXTS = 512
MAX_SAMPLES = 4096
MAX_SNAPSHOT_BYTES = 180000


def verified_label(event):
    """Preserve actual successor identity. Only R10-witnessed openings count."""
    action = event["action"]
    before, after = event["front_before"], event["front_after"]
    hb, ha = event["heading_before"], event["heading_after"]
    witnessed = bool(
        event["visible_door_opened"] and action == 5 and hb == ha
        and before[0] == after[0] == 4 and before[1] == after[1]
        and before[2] in (1, 2) and after[2] == 0
    )
    if witnessed:
        attribution = "R10_WITNESSED_VISIBLE_OPEN"
    elif action in (0, 1) and hb != ha:
        attribution = "CHANGED_VIEW_NOT_WORLD_EFFECT"
    elif before != after:
        attribution = "UNKNOWN_TARGET_IDENTITY"
    else:
        attribution = "NO_VERIFIED_WORLD_EFFECT"
    return [
        list(after), event["carried_after"], ha,
        witnessed, bool(event["visible_key_pickup"]),
        bool(event["reward"] > 0), bool(event["terminated"]),
        bool(event["truncated"]), attribution,
    ]


class PublicEffectProbe:
    """Selected public events only. Predictions/decisions are LOCAL, not navigation."""

    def __init__(self):
        self.slow, self.fast = {}, {}
        self.samples = 0
        self.cursor = 0
        self.session = None
        self.sessions = []
        self.previous_digest = None

    def start_session(self, adapter, session_id):
        if (type(adapter) is not DoorKeyPublicAdapter or adapter.current is None
            or adapter.pending is not None or adapter.events or adapter.ledger
            or adapter.terminal or type(session_id) is not str
            or not 0 < len(session_id) <= 100
            or session_id in self.sessions or len(self.sessions) >= 100):
            raise ValueError("O22L_UNAUTHENTICATED_PUBLIC_SESSION")
        self.session = session_id
        self.sessions.append(session_id)
        self.cursor = 0
        self.previous_digest = digest(adapter.current)

    def learn_selected(self, adapter):
        if (type(adapter) is not DoorKeyPublicAdapter or adapter.current is None
            or adapter.pending is not None or self.session is None
            or adapter.events != self.cursor + 1 or not adapter.ledger
            or self.samples >= MAX_SAMPLES):
            raise ValueError("O22L_UNRETURNED_OR_DUPLICATE_ACTION")
        event = adapter.ledger[-1]
        if (event["ordinal"] != adapter.events
            or event["action_name"] != ACTION_NAMES[event["action"]]
            or event["before_public_sha256"] != self.previous_digest
            or event["after_public_sha256"] != digest(adapter.current)):
            raise ValueError("O22L_PUBLIC_SOURCE_CHAIN_DRIFT")
        ctx = _feature(event["front_before"], event["carried_before"], event["action"])
        label = canonical(verified_label(event)).decode()
        if ctx not in self.slow and len(self.slow) >= MAX_CONTEXTS:
            raise ValueError("O22L_CONTEXT_CAP")
        old = self.slow.get(ctx, {})
        if label not in old and len(old) >= 128:
            raise ValueError("O22L_OUTCOME_CAP")
        next_slow = dict(old)
        next_slow[label] = next_slow.get(label, 0) + 1
        next_fast = {k: w * DECAY for k, w in self.fast.get(ctx, {}).items()
                     if w * DECAY > 1e-12}
        next_fast[label] = next_fast.get(label, 0) + 1.0
        self.slow[ctx], self.fast[ctx] = next_slow, next_fast
        self.samples += 1
        self.cursor += 1
        self.previous_digest = event["after_public_sha256"]
        return {"attribution": json.loads(label)[-1],
                "next_public_front": event["front_after"]}

    def predict(self, public_obs, action, mode="active"):
        if mode not in ("active", "slow", "zero"):
            raise ValueError("O22L_INVALID_ABLATION")
        cues = public_cues(public_obs)
        ctx = _feature(cues["front"], cues["carried"], action)
        rows = self.slow.get(ctx)
        if not rows or mode == "zero":
            return {"status": "ABSTAIN", "samples": 0, "open_probability": None,
                    "next_fronts": [], "probabilities": {}}
        fast = self.fast[ctx]
        stotal, ftotal = sum(rows.values()), sum(fast.values())
        weights = {}
        for label, n in rows.items():
            slow_p, fast_p = n / stotal, fast.get(label, 0.0) / ftotal
            weights[label] = (
                FAST_WEIGHT * fast_p + (1 - FAST_WEIGHT) * slow_p
                if mode == "active" else slow_p
            )
        return {"status": "LEARNED", "samples": stotal,
                "open_probability": sum(w for s, w in weights.items() if json.loads(s)[3]),
                "next_fronts": [list(t) for t in sorted({
                    tuple(json.loads(s)[0]) for s in weights
                })], "probabilities": weights}

    def choose(self, public_obs, costs=None, mode="active"):
        """Public-local desired verified door opening, not a mission/planner."""
        if costs is None:
            costs = [0.0] * len(ACTION_NAMES)
        if (type(costs) not in (tuple, list) or len(costs) != len(ACTION_NAMES)
            or any(type(v) not in (int, float) or not math.isfinite(v)
                   or not 0 <= v <= 1 for v in costs)):
            raise ValueError("O22L_INVALID_COSTS")
        actions = []
        for a in range(len(ACTION_NAMES)):
            prediction = self.predict(public_obs, a, mode)
            if prediction["status"] == "ABSTAIN":
                continue
            p = prediction["open_probability"]
            net = p - costs[a]
            if p > 0 and net > 0:
                actions.append((-net, a, p))
        if not actions:
            return {"status": "ABSTAIN", "action": None}
        neg, action, p = min(actions)
        return {"status": "SELECT", "action": action, "probability": p,
                "net_benefit": -neg}

    def checkpoint(self):
        state = {"schema": SCHEMA, "slow": self.slow, "fast": self.fast,
                 "samples": self.samples, "cursor": self.cursor,
                 "session": self.session, "sessions": self.sessions,
                 "previous_digest": self.previous_digest}
        raw = canonical(state)
        if len(raw) > MAX_SNAPSHOT_BYTES:
            raise ValueError("O22L_SNAPSHOT_OVERSIZE")
        return canonical({"state": state, "sha256": hashlib.sha256(raw).hexdigest()})

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= MAX_SNAPSHOT_BYTES:
                raise ValueError("O22L_CHECKPOINT_BYTES")
            wire = json.loads(raw)
            if type(wire) is not dict or set(wire) != {"state", "sha256"}:
                raise ValueError("O22L_CHECKPOINT_ENVELOPE")
            s = wire["state"]
            fields = {"schema", "slow", "fast", "samples", "cursor",
                      "session", "sessions", "previous_digest"}
            if (type(s) is not dict or set(s) != fields or s["schema"] != SCHEMA
                or hashlib.sha256(canonical(s)).hexdigest() != wire["sha256"]
                or type(s["samples"]) is not int or not 0 <= s["samples"] <= MAX_SAMPLES
                or type(s["cursor"]) is not int or not 0 <= s["cursor"] <= s["samples"]
                or type(s["slow"]) is not dict or type(s["fast"]) is not dict
                or len(s["slow"]) > MAX_CONTEXTS or set(s["slow"]) != set(s["fast"])
                or type(s["sessions"]) is not list or len(s["sessions"]) > 100
                or not all(type(v) is str and 0 < len(v) <= 100 for v in s["sessions"])
                or len(set(s["sessions"])) != len(s["sessions"])
                or (s["sessions"] and s["session"] != s["sessions"][-1])
                or (s["previous_digest"] is not None and
                    (type(s["previous_digest"]) is not str
                     or len(s["previous_digest"]) != 64))):
                raise ValueError("O22L_CHECKPOINT_AUTH_OR_STATE")
            total = 0
            for ctx, rows in s["slow"].items():
                if (type(ctx) is not str or type(rows) is not dict
                    or not 1 <= len(rows) <= 128 or type(s["fast"][ctx]) is not dict
                    or not set(s["fast"][ctx]).issubset(rows)):
                    raise ValueError("O22L_CHECKPOINT_CONTEXT")
                for label, count in rows.items():
                    out = json.loads(label)
                    if (type(out) is not list or len(out) != 9
                        or type(out[0]) is not list or len(out[0]) != 3
                        or any(type(v) is not int or not 0 <= v <= 255 for v in out[0])
                        or any(type(v) is not bool for v in out[3:8])
                        or type(count) is not int or not 1 <= count <= MAX_SAMPLES):
                        raise ValueError("O22L_CHECKPOINT_OUTCOME")
                    total += count
                for weight in s["fast"][ctx].values():
                    if (type(weight) not in (float, int) or not math.isfinite(weight)
                        or weight <= 0):
                        raise ValueError("O22L_CHECKPOINT_WEIGHT")
            if total != s["samples"]:
                raise ValueError("O22L_CHECKPOINT_TOTAL")
            obj = cls()
            for key in ("slow", "fast", "samples", "cursor", "session",
                        "sessions", "previous_digest"):
                setattr(obj, key, s[key])
            return obj
        except (ValueError, KeyError, TypeError, AttributeError, OverflowError) as exc:
            raise ValueError("O22L_UNTRUSTED_CHECKPOINT") from exc
