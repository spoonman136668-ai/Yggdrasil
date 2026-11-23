"""CCE06 CAL-only evaluator-owned public trace generator.

DO NOT IMPORT FROM A LEARNER OR CONTROL. No protected primary implementation.
No calibration sampling without an exact-source lock; fixture seed 997 only.
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

SCHEMA = "yggdrasil.y2.cce06.cal-source.v1"
SEEDS = (13, 29, 53, 71, 97)
FAMILIES = ("local_reversible", "gated_nonlocal", "action_null", "aliased_probe")
SPLITS = {"train": 5000, "cal_eval": 1000}
ACTIONS = (0, 1, 2)
FIXTURE_SEED = 997
FIXTURE_MAX = 32
PLAN_PATH = Path(__file__).with_name("calibration_plan.json")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def source_identity() -> dict:
    """These hashes pin generator/plan content; a caller's lock is not custody."""
    return {
        "generator_sha256": sha256(Path(__file__).read_bytes()),
        "plan_sha256": sha256(PLAN_PATH.read_bytes()),
    }


def _rng(family: str, seed: int, split: str, purpose: str) -> random.Random:
    material = f"{SCHEMA}|{family}|{seed}|{split}|{purpose}".encode("ascii")
    return random.Random(int.from_bytes(hashlib.sha256(material).digest(), "big"))


def _validate_request(family: str, seed: int, split: str, steps: int, lock: dict | None) -> None:
    if family not in FAMILIES or type(seed) is not int or type(steps) is not int:
        raise ValueError("CCE06_INVALID_REQUEST")
    if seed == FIXTURE_SEED and split == "fixture" and 1 <= steps <= FIXTURE_MAX:
        if lock is not None:
            raise ValueError("CCE06_FIXTURE_LOCK_FORBIDDEN")
        return
    if seed not in SEEDS or split not in SPLITS or steps != SPLITS[split]:
        raise ValueError("CCE06_UNREGISTERED_SAMPLE")
    if type(lock) is not dict or set(lock) != {"generator_sha256", "plan_sha256", "source_commit", "purpose"}:
        raise PermissionError("CCE06_CAL_SOURCE_LOCK_REQUIRED")
    identity = source_identity()
    if (lock["generator_sha256"] != identity["generator_sha256"]
            or lock["plan_sha256"] != identity["plan_sha256"]
            or type(lock["source_commit"]) is not str
            or len(lock["source_commit"]) != 40
            or any(c not in "0123456789abcdef" for c in lock["source_commit"])
            or lock["purpose"] != "CALIBRATION_ONLY"):
        raise PermissionError("CCE06_CAL_SOURCE_LOCK_MISMATCH")


def _emit(family: str, state: tuple[int, int, int], rng: random.Random) -> tuple[int, int]:
    a, b, c = state
    if family == "gated_nonlocal":
        out = (a, b)
    else:
        out = (a, c)
    return (out[0] ^ int(rng.random() < 0.02),
            out[1] ^ int(rng.random() < 0.02))


def _step(family: str, state: tuple[int, int, int], action: int,
          rng: random.Random) -> tuple[int, int, int]:
    """Evaluator-private latent dynamics. Never emit this state to a learner."""
    if type(action) is not int or action not in ACTIONS:
        raise ValueError("CCE06_INVALID_ACTION")
    x, y, z = state
    if family == "local_reversible":
        nx = x ^ int(action == 1 and rng.random() < 0.85) ^ int(rng.random() < 0.03)
        ny = y ^ int(action == 2 and rng.random() < 0.85) ^ int(rng.random() < 0.03)
        nz = z ^ int(nx == 1 and ny == 1 and rng.random() < 0.65) ^ int(rng.random() < 0.03)
    elif family == "gated_nonlocal":
        nx = x ^ int(action == 1 and z == 1 and rng.random() < 0.85) ^ int(rng.random() < 0.03)
        ny = y ^ int(action == 2 and z == 1 and rng.random() < 0.85) ^ int(rng.random() < 0.03)
        nz = z ^ int(x == 1 and y == 1 and rng.random() < 0.35) ^ int(rng.random() < 0.03)
    elif family == "action_null":
        nx = x ^ int(rng.random() < 0.13)
        ny = y ^ int(rng.random() < 0.11)
        nz = z ^ int(x == 1 and rng.random() < 0.25)
    elif family == "aliased_probe":
        nx = y if action == 2 and rng.random() < 0.90 else x
        nx ^= int(rng.random() < 0.02)
        ny = y ^ int(rng.random() < 0.08)
        nz = z ^ int(rng.random() < 0.02)
    else:
        raise ValueError("CCE06_UNKNOWN_FAMILY")
    return nx, ny, nz


def public_trace(family: str, seed: int, split: str, steps: int,
                 *, source_lock: dict | None = None) -> tuple[dict, ...]:
    """Return ONLY public events; no hidden labels, topology, reward or oracle.

    Calibration-sized generation demands separately recorded exact-source lock.
    Even a valid lock is not independent custody or scientific authority.
    """
    _validate_request(family, seed, split, steps, source_lock)
    dynamics = _rng(family, seed, split, "latent")
    actions = _rng(family, seed, split, "actions")
    sensing = _rng(family, seed, split, "sensing")
    state = tuple(dynamics.randrange(2) for _ in range(3))
    obs = _emit(family, state, sensing)
    events = []
    for _ in range(steps):
        action = actions.choice(ACTIONS)
        state = _step(family, state, action, dynamics)
        next_obs = _emit(family, state, sensing)
        events.append({"observation": list(obs), "action": action,
                       "next_observation": list(next_obs)})
        obs = next_obs
    return tuple(events)


def oracle_alias_contrast() -> dict:
    """Evaluator-only identifiability diagnostic, never passed as model input.

    Two states (0,0,0) and (0,1,0) yield same passive observation but
    different response to the idealized (noise-free) probe action 2.
    This structural witness alone does NOT prove finite-budget identifiability.
    """
    left, right = (0, 0, 0), (0, 1, 0)
    return {"passive_equal": (left[0], left[2]) == (right[0], right[2]),
            "probe2_contrast": left[1] != right[1], "is_evaluator_only": True}


def validate_public_trace(events) -> None:
    if type(events) not in (tuple, list) or not events:
        raise ValueError("CCE06_EMPTY_OR_INVALID")
    last = None
    for event in events:
        if type(event) is not dict or set(event) != {"observation", "action", "next_observation"}:
            raise ValueError("CCE06_LEAK_OR_MALFORMED_EVENT")
        for key in ("observation", "next_observation"):
            bits = event[key]
            if type(bits) is not list or len(bits) != 2 or any(type(x) is not int or x not in (0, 1) for x in bits):
                raise ValueError("CCE06_INVALID_OBSERVATION")
        if type(event["action"]) is not int or event["action"] not in ACTIONS:
            raise ValueError("CCE06_INVALID_ACTION")
        if last is not None and event["observation"] != last:
            raise ValueError("CCE06_BROKEN_SEQUENCE")
        last = event["next_observation"]


if __name__ == "__main__":
    # No CLI for calibration or primary generation. Import requires source lock.
    print(json.dumps({"schema": SCHEMA, "status": "SOURCE_ONLY_NO_SAMPLES", **source_identity()},
                     sort_keys=True))
