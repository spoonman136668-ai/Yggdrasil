"""WSP-159 public-only continuous transition boundary (source-free engineering).

No simulator import or execution, learned state, oracle, source-authority claim,
model selection, private wind, hidden SCM, or counterfactual information.
The external source owner must separately approve every future real action.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
import math
from typing import Any

SCHEMA = "yggdrasil.wsp159.public-transition.v1"
STATE_SIZE = 4
ACTIONS = (0, 1)
PUBLIC_FIELDS = frozenset({
    "observation", "action", "next_observation", "reward", "terminated", "truncated"
})
WIRE_FIELDS = PUBLIC_FIELDS | {"schema"}
MAX_BYTES = 2048


def _public_scalar(value: Any, label: str) -> float:
    # A qualified runner must convert upstream NumPy observations via .tolist()
    # before crossing this pure-Python boundary. Never accept arbitrary objects.
    if type(value) not in (int, float):
        raise ValueError(f"WSP159_{label}_TYPE")
    try:
        number = float(value)
    except (ValueError, OverflowError):
        raise ValueError(f"WSP159_{label}_RANGE") from None
    if not math.isfinite(number):
        raise ValueError(f"WSP159_{label}_NONFINITE")
    return 0.0 if number == 0.0 else number


def _observation(value: Any, label: str) -> tuple[float, ...]:
    if type(value) not in (tuple, list) or len(value) != STATE_SIZE:
        raise ValueError(f"WSP159_{label}_SHAPE")
    return tuple(_public_scalar(x, label) for x in value)


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError("WSP159_DUPLICATE_KEY")
        output[key] = value
    return output


def _reject_nonfinite(value: str) -> None:
    raise ValueError("WSP159_WIRE_NONFINITE")


@dataclass(frozen=True, slots=True)
class PublicTransition:
    observation: tuple[float, float, float, float]
    action: int
    next_observation: tuple[float, float, float, float]
    reward: float
    terminated: bool
    truncated: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "observation", _observation(self.observation, "OBS"))
        object.__setattr__(self, "next_observation", _observation(self.next_observation, "NEXT"))
        if type(self.action) is not int or self.action not in ACTIONS:
            raise ValueError("WSP159_ACTION_INVALID")
        object.__setattr__(self, "reward", _public_scalar(self.reward, "REWARD"))
        if type(self.terminated) is not bool or type(self.truncated) is not bool:
            raise ValueError("WSP159_TERMINAL_FLAG_TYPE")
        # Preserve both flags exactly; upstream may set both at its time limit.

    @classmethod
    def from_public(cls, **values: Any) -> "PublicTransition":
        if set(values) != PUBLIC_FIELDS:
            # Reject extras: info, u_wind, get_graph, ctf_do, hidden source.
            raise ValueError("WSP159_PUBLIC_FIELD_SET")
        return cls(**values)

    def model_input(self) -> dict[str, object]:
        """Only public values; this is not authenticated intervention custody."""
        return {
            "observation": list(self.observation),
            "action": self.action,
            "next_observation": list(self.next_observation),
            "reward": self.reward,
            "terminated": self.terminated,
            "truncated": self.truncated,
        }

    def canonical(self) -> bytes:
        record = {"schema": SCHEMA, **self.model_input()}
        return json.dumps(record, sort_keys=True, ensure_ascii=True,
                          allow_nan=False, separators=(",", ":")).encode("ascii")

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical()).hexdigest()

    @classmethod
    def restore(cls, raw: bytes, expected_sha256: str) -> "PublicTransition":
        if type(raw) is not bytes or not 0 < len(raw) <= MAX_BYTES:
            raise ValueError("WSP159_WIRE_SIZE")
        if (type(expected_sha256) is not str or len(expected_sha256) != 64 or
                any(c not in "0123456789abcdef" for c in expected_sha256) or
                not hmac.compare_digest(hashlib.sha256(raw).hexdigest(), expected_sha256)):
            raise ValueError("WSP159_WIRE_HASH")
        try:
            decoded = json.loads(raw.decode("ascii"), object_pairs_hook=_no_duplicate_keys,
                                 parse_constant=_reject_nonfinite)
        except (ValueError, UnicodeError, TypeError) as exc:
            raise ValueError("WSP159_WIRE_PARSE") from exc
        if type(decoded) is not dict or set(decoded) != WIRE_FIELDS or decoded["schema"] != SCHEMA:
            raise ValueError("WSP159_WIRE_SCHEMA")
        model = cls.from_public(**{k: v for k, v in decoded.items() if k != "schema"})
        if model.canonical() != raw:
            raise ValueError("WSP159_NONCANONICAL_WIRE")
        return model
