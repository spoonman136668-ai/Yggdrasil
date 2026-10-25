"""O22-U retrospective public selected-action turn-cancellation admission.

Source-only decision veto, not live navigation or an original MiniGrid experiment.
Original C31/C32 R3, source histories, and learned model weights stay untouched.
"""
from __future__ import annotations
import hashlib
import json

SCHEMA = "optimizer.o22u.historical-public-turn-cancellation.v1"
MAX_STEP = 10000


def _pose(pub):
    if (type(pub) is not dict or
        set(pub) != {"x", "y", "direction", "goal_x", "goal_y", "front_blocked"} or
        any(type(pub[k]) is not int or not 0 <= pub[k] <= 64
            for k in ("x", "y", "direction", "goal_x", "goal_y")) or
        pub["direction"] not in (0, 1, 2, 3) or
        type(pub["front_blocked"]) is not bool):
        raise ValueError("O22U_UNAUTHENTICATED_PUBLIC_FRAME_GRAMMAR")
    return (pub["x"], pub["y"], pub["direction"])


def _action(a):
    if type(a) is not int or a not in (0, 1, 2):
        raise ValueError("O22U_INVALID_SOURCE_ACTION")
    return a


class SelectedActionGuard:
    """Records only public actual past selected action (no future source oracle)."""

    def __init__(self):
        self.last_action = None
        self.last_after = None
        self.last_t = None
        self.seen = 0

    def decide(self, current, source_t, original_r3, candidate):
        xyz = _pose(current)
        _action(original_r3)
        _action(candidate)
        if type(source_t) is not int or not 0 <= source_t <= MAX_STEP:
            raise ValueError("O22U_INVALID_SOURCE_ORDINAL")
        if self.last_t is not None and source_t != self.last_t + 1:
            raise ValueError("O22U_SOURCE_STEP_SEQUENCE")
        if original_r3 == candidate:
            return original_r3, False
        if original_r3 == 2 or candidate == 2 or original_r3 == candidate:
            raise ValueError("O22U_FORBIDDEN_FORWARD_CHANGE")
        if candidate != 1 - original_r3:
            raise ValueError("O22U_NON_OPPOSITE_TURN_SUBSTITUTION")
        veto = bool(
            self.last_action in (0, 1)
            and candidate == 1 - self.last_action
            and self.last_after is not None
            and xyz[:2] == tuple(self.last_after[:2])
        )
        return (original_r3 if veto else candidate), veto

    def observe_actual(self, source_t, before, chosen, after):
        b, a = _pose(before), _pose(after)
        _action(chosen)
        if type(source_t) is not int or not 0 <= source_t <= MAX_STEP:
            raise ValueError("O22U_INVALID_SELECTED_EVENT_INDEX")
        if self.last_t is None:
            if source_t != 0:
                raise ValueError("O22U_FIRST_EVENT_NOT_ZERO")
        elif source_t != self.last_t + 1 or b != tuple(self.last_after):
            # Front sensor may change at the same public pose in an evolving
            # world, but public pose must still be continuous.
            if self.last_t is None or source_t != self.last_t + 1 or b[:3] != tuple(self.last_after):
                raise ValueError("O22U_SOURCE_ACTION_CHAIN_GAP")
        if chosen in (0, 1):
            expected = ((b[2] - 1) % 4 if chosen == 0 else (b[2] + 1) % 4)
            if b[:2] != a[:2] or a[2] != expected:
                raise ValueError("O22U_FAKE_OR_MOTION_TURN")
        self.last_action = chosen
        self.last_after = list(a)
        self.last_t = source_t
        self.seen += 1

    def checkpoint(self):
        state = {"schema":SCHEMA,"last_action":self.last_action,
                 "last_after":self.last_after,"last_t":self.last_t,"seen":self.seen}
        data = json.dumps(state,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
        return json.dumps({"state":state,"sha256":hashlib.sha256(data).hexdigest()},
                          sort_keys=True,separators=(",",":")).encode()

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) < 2000:
                raise ValueError("O22U_CHECKPOINT_SIZE")
            wire = json.loads(raw)
            if type(wire) is not dict or set(wire) != {"state","sha256"}:
                raise ValueError("O22U_CHECKPOINT_ENVELOPE")
            s = wire["state"]
            if type(s) is not dict or set(s) != {"schema","last_action","last_after","last_t","seen"} or s["schema"] != SCHEMA:
                raise ValueError("O22U_CHECKPOINT_SCHEMA")
            blob = json.dumps(s,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
            if hashlib.sha256(blob).hexdigest() != wire["sha256"]:
                raise ValueError("O22U_CHECKPOINT_TAMPER")
            n = cls()
            if type(s["seen"]) is not int or not 0 <= s["seen"] <= MAX_STEP+1:
                raise ValueError("O22U_CHECKPOINT_COUNT")
            if s["seen"] == 0:
                if any(s[k] is not None for k in ("last_action","last_after","last_t")):
                    raise ValueError("O22U_CHECKPOINT_UNEXPECTED_HISTORY")
            else:
                _action(s["last_action"])
                if (type(s["last_t"]) is not int or s["last_t"] != s["seen"]-1
                    or type(s["last_after"]) is not list or len(s["last_after"]) != 3
                    or any(type(v) is not int for v in s["last_after"]) or
                    not 0 <= s["last_after"][0] <= 64 or
                    not 0 <= s["last_after"][1] <= 64 or
                    s["last_after"][2] not in (0,1,2,3)):
                    raise ValueError("O22U_CHECKPOINT_ILLEGAL_HISTORY")
            n.seen=s["seen"]
            n.last_action=s["last_action"]
            n.last_after=s["last_after"]
            n.last_t=s["last_t"]
            return n
        except (ValueError,TypeError,KeyError,OverflowError) as e:
            raise ValueError("O22U_UNTRUSTED_CHECKPOINT") from e
