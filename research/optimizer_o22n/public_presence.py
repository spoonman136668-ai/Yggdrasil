"""O22-N source-only missingness contract for future original-world information ablations.

This does NOT execute original Farama MiniGrid, run a hidden simulator, or train
a learner. A witnessed False (clear) and an UNOBSERVED front are DIFFERENT.
Existing R1/R3 accept ONLY witnessed Boolean public fronts. We fail closed
instead of fabricating a clear reading when the evaluator withholds a sensor.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
import hashlib
import json
import math
from research.native.itd02.r1.native_policy import PublicGrid, canonical, features

SCHEMA = "optimizer.o22n.public-front-observation-presence.v1"
MAX_BYTES = 32768
MAX_STORED_VIEWS = 256


@dataclass(frozen=True)
class FrontFrame:
    x: int
    y: int
    goal_x: int
    goal_y: int
    direction: int
    ordinal: int
    observed: bool
    front_blocked: bool | None

    def validate(self):
        if (any(type(v) is not int or v < 0 or v > 64
                for v in (self.x, self.y, self.goal_x, self.goal_y))
            or type(self.direction) is not int or self.direction not in range(4)
            or type(self.ordinal) is not int or not 0 <= self.ordinal <= 10000
            or type(self.observed) is not bool
            or (self.observed and type(self.front_blocked) is not bool)
            or (not self.observed and self.front_blocked is not None)):
            raise ValueError("O22N_INVALID_PUBLIC_OBSERVATION_PRESENCE")
        return self

    @classmethod
    def from_public(cls, source_public, ordinal):
        features(source_public)
        return cls(source_public.x, source_public.y, source_public.goal_x,
                   source_public.goal_y, source_public.direction, ordinal,
                   True, source_public.front_blocked).validate()

    def withhold(self):
        self.validate()
        return replace(self, observed=False, front_blocked=None)

    def require_r1_boolean(self):
        self.validate()
        if not self.observed:
            raise ValueError("O22N_UNKNOWN_CANNOT_ENTER_BOOLEAN_R1_R3")
        out = PublicGrid(self.x, self.y, self.goal_x, self.goal_y,
                         self.direction, self.front_blocked)
        features(out)
        return out

    def public_wire(self):
        self.validate()
        return {"x": self.x, "y": self.y,
                "goal_x": self.goal_x, "goal_y": self.goal_y,
                "direction": self.direction, "ordinal": self.ordinal,
                "observed": self.observed,
                "front_blocked": self.front_blocked}

    @classmethod
    def from_wire(cls, data):
        expected = {"x","y","goal_x","goal_y","direction",
                    "ordinal","observed","front_blocked"}
        if type(data) is not dict or set(data) != expected:
            raise ValueError("O22N_INVALID_FRAME_WIRE")
        return cls(**data).validate()


class PolicyPresenceLedger:
    """Stores only policy-delivered source-public knowledge, NOT hidden labels."""

    def __init__(self):
        self.views = []

    def ingest(self, frame):
        if type(frame) is not FrontFrame:
            raise ValueError("O22N_FRAME_TYPE")
        frame.validate()
        if (len(self.views) >= MAX_STORED_VIEWS
            or self.views and frame.ordinal <= self.views[-1].ordinal):
            raise ValueError("O22N_REPLAY_OR_BUDGET")
        self.views.append(frame)

    def front_status(self, edge):
        if type(edge) is not tuple or len(edge) != 3:
            raise ValueError("O22N_EDGE_KEY")
        for frame in reversed(self.views):
            if (frame.x,frame.y,frame.direction)==edge and frame.observed:
                return "BLOCKED" if frame.front_blocked else "CLEAR"
        return "UNKNOWN"

    def checkpoint(self):
        data = {"schema": SCHEMA, "views": [v.public_wire() for v in self.views]}
        payload = canonical(data)
        if len(payload) > MAX_BYTES:
            raise ValueError("O22N_CHECKPOINT_LIMIT")
        return canonical({"data": data, "sha256": hashlib.sha256(payload).hexdigest()})

    @classmethod
    def restore(cls, source):
        try:
            if type(source) is not bytes or not 0 < len(source) <= MAX_BYTES:
                raise ValueError("O22N_SOURCE_BYTES")
            obj = json.loads(source)
            if type(obj) is not dict or set(obj) != {"data","sha256"}:
                raise ValueError("O22N_ENVELOPE")
            d = obj["data"]
            if (type(d) is not dict or set(d) != {"schema","views"}
                or d["schema"] != SCHEMA or type(d["views"]) is not list
                or len(d["views"]) > MAX_STORED_VIEWS
                or hashlib.sha256(canonical(d)).hexdigest() != obj["sha256"]):
                raise ValueError("O22N_INTEGRITY")
            result = cls()
            for v in d["views"]:
                result.ingest(FrontFrame.from_wire(v))
            return result
        except (ValueError,TypeError,KeyError,AttributeError,OverflowError) as e:
            raise ValueError("O22N_UNTRUSTED_CHECKPOINT") from e


def mask_at_source_return(actual_after, chosen_action, prior_ordinal):
    """Evaluator's deliberate information ablation, NOT an original source step.

    The returned frame is the ONLY policy-visible payload of this function.
    Physical source execution is an owner-controlled future experiment; this
    helper cannot infer or simulate its effects and stores no true status.
    """
    if (type(actual_after) is not FrontFrame or not actual_after.observed
        or type(chosen_action) is not int or chosen_action not in (0,1,2)
        or type(prior_ordinal) is not int
        or actual_after.ordinal != prior_ordinal + 1):
        raise ValueError("O22N_UNAUTHENTICATED_SOURCE_RETURN_GRAMMAR")
    actual_after.validate()
    return actual_after.withhold()
