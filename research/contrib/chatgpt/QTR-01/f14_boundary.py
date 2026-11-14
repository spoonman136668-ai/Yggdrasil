"""F14 DEV boundary: serialize only public observations and action outcomes.

This encoder runs on the trusted evaluator side. Give the learner ONLY its
returned JSON string, never the underlying environment, module or raw tuple.
No external benchmark dependency; no protected data or model execution.
"""
import json
import math

_MAX_DIM = 256


def _scalar(value):
    if type(value).__module__.split(".")[0] == "numpy" and hasattr(value, "item"):
        value = value.item()
    if type(value) not in (int, float):
        raise ValueError("F14_BAD_PUBLIC_SCALAR")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("F14_NONFINITE_PUBLIC_SCALAR")
    return number


def _observation(value):
    if type(value).__module__.split(".")[0] == "numpy" and hasattr(value, "tolist"):
        value = value.tolist()
    if type(value) not in (tuple, list) or not 1 <= len(value) <= _MAX_DIM:
        raise ValueError("F14_BAD_OBSERVATION_SHAPE")
    return [_scalar(element) for element in value]


def _wire(payload):
    return json.dumps(payload, sort_keys=True, allow_nan=False,
                      separators=(",", ":"), ensure_ascii=True)


def reset_frame(raw):
    """Accept a trusted Gymnasium reset tuple; discard *all* reset info."""
    if type(raw) is not tuple or len(raw) != 2:
        raise ValueError("F14_BAD_RESET_TUPLE")
    observation, _private_info = raw
    return _wire({"observation": _observation(observation), "done": False})


def step_frame(raw):
    """Accept a trusted step tuple; discard *all* evaluator-only info."""
    if type(raw) is not tuple or len(raw) != 5:
        raise ValueError("F14_BAD_STEP_TUPLE")
    observation, reward, terminated, truncated, _private_info = raw
    if type(terminated) is not bool or type(truncated) is not bool:
        raise ValueError("F14_BAD_TERMINATION_FLAGS")
    return _wire({"observation": _observation(observation),
                  "reward": _scalar(reward), "done": terminated or truncated})
