"""YGG-CAP04 prospective synthetic-source implementation, FIRST-USE LOCKED.

This module fixes a candidate A/B/A source construction without consuming its
registered cohorts. The only executable generation interface admits separately
named engineering fixtures, which are NOT scientific results or evidence of
unfamiliar-world transfer. Unlocking registered cohort generation requires a
new separately authorized, source-pinned first-use gate.
"""
from __future__ import annotations

import hashlib

SCHEMA = "yggdrasil.cap04.prospective-source.v2"
REGISTERED_DEV = (99917, 99931)
REGISTERED_PILOT = (100017, 100031)
REGISTERED_PRIMARY = (100117, 100131, 100151)
REGISTERED = REGISTERED_DEV + REGISTERED_PILOT + REGISTERED_PRIMARY
ENGINEERING_FIXTURES = ("cap04-source-structure-fixture-a", "cap04-source-structure-fixture-b")
ACTIONS = ((0, 0), (0, 1), (1, 0), (1, 1))
EPISODES = 96
BOUNDARIES = (0, 32, 72, 96)

# Frozen public, source/outcome/seed-independent four-action blocks. Each block
# contains each intervention once; predecessor order varies across blocks.
# This defeats the old alias previous_action=f(current_action). No registered
# scientific source generation is enabled by this engineering patch.
ACTION_BLOCKS = (
    ((0, 0), (0, 1), (1, 0), (1, 1)),
    ((0, 0), (1, 0), (1, 1), (0, 1)),
    ((0, 0), (1, 1), (0, 1), (1, 0)),
    ((1, 0), (0, 0), (0, 1), (1, 1)),
)


def action_at(t: int) -> tuple[int, int]:
    _require(type(t) is int and 0 <= t < EPISODES, "ACTION_CLOCK")
    return ACTION_BLOCKS[(t // len(ACTIONS)) % len(ACTION_BLOCKS)][t % len(ACTIONS)]



def _require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("CAP04_PROSPECTIVE_SOURCE_" + reason)


def _bit(identity: str, t: int, label: str) -> int:
    material = f"YGG-CAP04/prospective-v1/{identity}/{t}/{label}"
    return hashlib.sha256(material.encode("ascii")).digest()[0] & 1


def _word(identity: str, t: int, label: str) -> str:
    material = f"YGG-CAP04/public-witness-v1/{identity}/{t}/{label}"
    return hashlib.sha256(material.encode("ascii")).hexdigest()


def _simulate_fixture(identity: str) -> tuple[dict, ...]:
    """Run only allowlisted engineering identities; never registered seeds."""
    _require(type(identity) is str and identity in ENGINEERING_FIXTURES,
             "REGISTERED_FIRST_USE_FORBIDDEN")
    u, v, w = (_bit(identity, -1, f"initial-{i}") for i in range(3))
    latent = _bit(identity, -1, "initial-private-latent")
    previous_action = (0, 0)
    tape = []
    for t in range(EPISODES):
        a, b = action_at(t)
        # Fixed phase boundaries are visible here only to the source builder;
        # the returned learner observation has no phase, latent or family key.
        novel = 32 <= t < 72
        disturbance = (_bit(identity, t, "noise-0") &
                       _bit(identity, t, "noise-1") &
                       _bit(identity, t, "noise-2") &
                       _bit(identity, t, "noise-3"))
        if novel:
            s2 = previous_action[0] ^ (b & w) ^ (latent & v) ^ disturbance
            reward = s2 ^ previous_action[1] ^ (a & u) ^ (latent & previous_action[0])
        else:
            s2 = u ^ (a & v) ^ (b & w) ^ (latent & u) ^ disturbance
            reward = s2 ^ b ^ (u & v) ^ (latent & w)
        post = (v ^ a, s2, w ^ b)
        witness = {"id": _word(identity, t, "observed"),
                   "views": ((u, v), (v, w)), "action": (a, b),
                   "s2": s2, "y": reward, "post": post}
        _require(all(type(z) is int and z in (0, 1)
                     for z in (s2, reward, *post)), "BINARY")
        tape.append(witness)
        latent ^= (a & w) ^ (b & u)
        u, v, w = post
        previous_action = (a, b)
    _require(len(tape) == EPISODES and
             len({e["id"] for e in tape}) == EPISODES, "WITNESS_IDENTITY")
    _require(all(left["post"] == (right["views"][0][0],
                                  right["views"][0][1], right["views"][1][1])
                 for left, right in zip(tape, tape[1:])), "CAUSAL_CONTINUITY")
    return tuple(tape)


def engineering_fixture(identity: str) -> tuple[dict, ...]:
    """Structural testing only; these source IDs are barred from DEV scoring."""
    return _simulate_fixture(identity)


def generate_registered(seed: int) -> tuple[dict, ...]:
    """Fail-closed until a separate authorized first-use implementation gate."""
    _require(type(seed) is int and seed in REGISTERED, "UNKNOWN_REGISTERED_SEED")
    raise ValueError("CAP04_PROSPECTIVE_SOURCE_REGISTERED_FIRST_USE_FORBIDDEN")
