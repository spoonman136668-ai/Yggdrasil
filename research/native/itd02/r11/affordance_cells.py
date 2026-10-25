"""R11 source-public seven-action observable consequence cells.

Learns ONLY from R10 committed selected public action events. Public conditional
features are deliberately authored; the learning rule is sparse empirical
counts, not a discovered latent representation nor a goal-solving policy.
"""
from __future__ import annotations
import hashlib
import json

from research.native.itd02.r10.public_adapter import (
    ACTION_NAMES, DoorKeyPublicAdapter, canonical, digest, public_cues,
)

SCHEMA = "yggdrasil.itd02.r11.selected-public-affordance-cells.v1"
MAX_CONTEXTS = 512
MAX_SAMPLES = 4096
MAX_SESSIONS = 100
MAX_SNAPSHOT_BYTES = 180000
OUTCOME_BITS = 7


def _feature(front, carried, action):
    if type(action) is not int or not 0 <= action < len(ACTION_NAMES):
        raise ValueError("R11_INVALID_ACTION")
    if type(front) is not list or len(front) != 3 or any(type(x) is not int for x in front):
        raise ValueError("R11_INVALID_FRONT")
    if carried is not None and (type(carried) is not list or len(carried) != 3 or
                                any(type(x) is not int for x in carried)):
        raise ValueError("R11_INVALID_CARRY")
    # Current front type/color/state; visible held-object type/color; chosen legal action.
    # No private global pose or evaluator-provided key ownership.
    hold_kind, hold_color = (0, 0) if carried is None else (carried[0], carried[1])
    data = [*front, hold_kind, hold_color, action]
    if (not 0 <= data[0] <= 10 or not 0 <= data[1] <= 5 or not 0 <= data[2] <= 255
        or not 0 <= hold_kind <= 10 or not 0 <= hold_color <= 5):
        raise ValueError("R11_FEATURE_RANGE")
    return ":".join(map(str, data))


def _outcome(event):
    before = event["front_before"]
    after = event["front_after"]
    things = [
        before != after,
        before[0] == 4 and after[0] == 4 and before[2] != after[2],
        event["carried_before"] != event["carried_after"],
        event["heading_before"] != event["heading_after"],
        event["reward"] > 0,
        event["terminated"],
        event["truncated"],
    ]
    return sum(int(v) << i for i, v in enumerate(things))


def _decode(outcome):
    return {"front_changed": bool(outcome & 1),
            "visible_door_state_changed": bool(outcome & 2),
            "carrying_changed": bool(outcome & 4),
            "heading_changed": bool(outcome & 8),
            "positive_reward": bool(outcome & 16),
            "terminated": bool(outcome & 32),
            "truncated": bool(outcome & 64)}


class PublicAffordanceCells:
    """Learns observable, public context/action→effect distributions."""

    def __init__(self):
        self.counts = {}
        self.samples = 0
        self.session = None
        self.cursor = 0
        self.sessions = []

    def start_session(self, adapter, session_id):
        if type(adapter) is not DoorKeyPublicAdapter or adapter.current is None or adapter.pending is not None:
            raise ValueError("R11_UNAUTHENTICATED_PUBLIC_SESSION")
        if adapter.events != 0 or adapter.ledger or adapter.terminal:
            raise ValueError("R11_SOURCE_SESSION_NOT_FRESH")
        if (type(session_id) is not str or not 0 < len(session_id) <= 100 or
            session_id in self.sessions or len(self.sessions) >= MAX_SESSIONS):
            raise ValueError("R11_SESSION_REPLAY_OR_INVALID")
        self.session = session_id
        self.cursor = 0
        self.sessions.append(session_id)

    def predict(self, public_observation, action):
        cues = public_cues(public_observation)
        context = _feature(cues["front"], cues["carried"], action)
        rows = self.counts.get(context)
        if rows is None:
            return {"status": "ABSTAIN_UNOBSERVED", "samples": 0,
                    "confidence": None, "predicted": None}
        total = sum(rows.values())
        winning = min(rows, key=lambda v: (-rows[v], int(v)))
        return {"status": "LEARNED_PUBLIC_CONSEQUENCE", "samples": total,
                "confidence": rows[winning] / total, "predicted": _decode(int(winning))}

    def learn_selected(self, adapter):
        # R10 ensures only a completed public action can issue the source event.
        if type(adapter) is not DoorKeyPublicAdapter or adapter.current is None or adapter.pending is not None:
            raise ValueError("R11_UNRETURNED_OR_INVALID_PUBLIC_SOURCE")
        if self.session is None or adapter.events != self.cursor + 1 or not adapter.ledger:
            raise ValueError("R11_NOT_NEXT_SELECTED_PUBLIC_EFFECT")
        if self.samples >= MAX_SAMPLES:
            raise ValueError("R11_OBSERVATION_BUDGET")
        event = adapter.ledger[-1]
        if (event["ordinal"] != adapter.events or event["action_name"] != ACTION_NAMES[event["action"]] or
            event["after_public_sha256"] != digest(adapter.current)):
            raise ValueError("R11_UNAUTHENTICATED_PUBLIC_EVENT")
        ctx = _feature(event["front_before"], event["carried_before"], event["action"])
        out = str(_outcome(event))
        if ctx not in self.counts and len(self.counts) >= MAX_CONTEXTS:
            raise ValueError("R11_CONTEXT_BUDGET")
        old = self.counts.get(ctx, {})
        if out not in old and len(old) >= 128:
            raise ValueError("R11_OUTCOME_BUDGET")
        next_rows = dict(old)
        next_rows[out] = next_rows.get(out, 0) + 1
        self.counts[ctx] = next_rows
        self.samples += 1
        self.cursor += 1
        return {"sample_index": self.samples, "context": ctx,
                "observable_outcome": _decode(int(out)), "examples_here": sum(next_rows.values())}

    def checkpoint(self):
        state = {"schema": SCHEMA, "counts": self.counts,
                 "samples": self.samples, "session": self.session,
                 "cursor": self.cursor, "sessions": self.sessions}
        raw = canonical(state)
        if len(raw) > MAX_SNAPSHOT_BYTES:
            raise ValueError("R11_CHECKPOINT_TOO_BIG")
        return canonical({"state": state, "sha256": hashlib.sha256(raw).hexdigest()})

    @classmethod
    def restore(cls, blob):
        try:
            if type(blob) is not bytes or not 0 < len(blob) <= MAX_SNAPSHOT_BYTES:
                raise ValueError("R11_CHECKPOINT_SIZE")
            outer = json.loads(blob)
            if type(outer) is not dict or set(outer) != {"state", "sha256"}:
                raise ValueError("R11_CHECKPOINT_ENVELOPE")
            state = outer["state"]
            if (type(state) is not dict or set(state) !=
                {"schema", "counts", "samples", "session", "cursor", "sessions"} or
                state["schema"] != SCHEMA or
                hashlib.sha256(canonical(state)).hexdigest() != outer["sha256"]):
                raise ValueError("R11_CHECKPOINT_AUTH")
            if (type(state["samples"]) is not int or not 0 <= state["samples"] <= MAX_SAMPLES or
                type(state["cursor"]) is not int or not 0 <= state["cursor"] <= state["samples"] or
                type(state["sessions"]) is not list or not 0 <= len(state["sessions"]) <= MAX_SESSIONS or
                any(type(s) is not str or not 0 < len(s) <= 100 for s in state["sessions"]) or
                len(set(state["sessions"])) != len(state["sessions"]) or
                (state["session"] is not None and state["session"] != (state["sessions"][-1] if state["sessions"] else None)) or
                (state["session"] is None and (state["sessions"] or state["cursor"]))):
                raise ValueError("R11_CHECKPOINT_COUNTERS")
            counts = state["counts"]
            if type(counts) is not dict or len(counts) > MAX_CONTEXTS:
                raise ValueError("R11_CHECKPOINT_CONTEXTS")
            total = 0
            for key, group in counts.items():
                parts = key.split(":")
                if (len(parts) != 6 or any(not p.isdecimal() or str(int(p)) != p for p in parts) or
                    _feature(list(map(int, parts[:3])),
                             None if parts[3] == "0" else [int(parts[3]),int(parts[4]),0],
                             int(parts[5])) != key or
                    type(group) is not dict or not 1 <= len(group) <= 128):
                    raise ValueError("R11_CHECKPOINT_FEATURE")
                for name, count in group.items():
                    if (type(name) is not str or not name.isdecimal() or str(int(name)) != name or
                        not 0 <= int(name) < (1 << OUTCOME_BITS) or
                        type(count) is not int or not 1 <= count <= MAX_SAMPLES):
                        raise ValueError("R11_CHECKPOINT_OUTCOME")
                    total += count
            if total != state["samples"]:
                raise ValueError("R11_CHECKPOINT_SAMPLE_TOTAL")
            learner = cls()
            for k in ("counts", "samples", "session", "cursor", "sessions"):
                setattr(learner, k, state[k])
            return learner
        except (ValueError, KeyError, AttributeError, TypeError, OverflowError) as exc:
            raise ValueError("R11_UNTRUSTED_CHECKPOINT") from exc
