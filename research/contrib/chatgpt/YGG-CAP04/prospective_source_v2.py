"""CAP04 v2 proposed keyed, private-source engineering protocol.

No registered science source can be produced here. Owner custody must provide
unpredictable 256-bit independent source entropy through an authorized secret
channel, not a GitHub commit, CI variable printed in a job, public source seed,
or a model input. All fixture entropies in tests are deliberately public and
are NEVER usable for scientific first use.
"""
from __future__ import annotations

import hashlib
import hmac

SCHEMA = "yggdrasil.cap04.prospective-source-keyed.v2"
ENGINEERING_FIXTURES = ("cap04-v2-engineering-a", "cap04-v2-engineering-b")
REGISTERED_DEV = (99917, 99931)
REGISTERED_PILOT = (100017, 100031)
REGISTERED_PRIMARY = (100117, 100131, 100151)
REGISTERED = REGISTERED_DEV + REGISTERED_PILOT + REGISTERED_PRIMARY
ACTIONS = ((0, 0), (0, 1), (1, 0), (1, 1))
PHASE_BOUNDARIES = (0, 32, 72, 96)
EPISODES = 96

def _require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("CAP04_V2_" + reason)


def _validate_entropy(entropy: bytes) -> None:
    # This validates input type/size, NOT cryptographic unpredictability.
    _require(type(entropy) is bytes and len(entropy) == 32, "PRIVATE_256BIT_ENTROPY_REQUIRED")


def _key(entropy: bytes, role: bytes) -> bytes:
    _validate_entropy(entropy)
    _require(type(role) is bytes and role in
             (b"action", b"witness", b"world"), "PRIVATE_KEY_ROLE")
    return hmac.new(entropy, b"YGG-CAP04/v2/" + role, hashlib.sha256).digest()


def commitment(entropy: bytes) -> str:
    """Publish only after source owner verifies CSPRNG custody, before first use."""
    _validate_entropy(entropy)
    return hashlib.sha256(b"YGG-CAP04/v2/secret-commitment\x00" + entropy).hexdigest()


def _word(key: bytes, domain: bytes, t: int, index: int = 0) -> bytes:
    _require(type(t) is int and -1 <= t < EPISODES, "INDEX")
    return hmac.new(key, domain + t.to_bytes(4, "big", signed=True) +
                    index.to_bytes(4, "big"), hashlib.sha256).digest()


def _uniform_below(key: bytes, block: int, step: int, width: int) -> int:
    """Rejection sampling from a keyed PRF; no modulo-selection bias."""
    _require(0 < width <= 4 and block >= 0, "SHUFFLE")
    ceiling = 256 - (256 % width)
    for retry in range(256):
        b = hmac.new(key,
                     b"YGG-CAP04/v2/shuffle/" + block.to_bytes(4, "big") +
                     bytes([step, retry]), hashlib.sha256).digest()[0]
        if b < ceiling:
            return b % width
    raise ValueError("CAP04_V2_SHUFFLE_REJECTION_OVERFLOW")


def action_at(entropy: bytes, t: int) -> tuple[int, int]:
    """Action is exogenous, before outcome; no hidden state, phase, or ID input."""
    _validate_entropy(entropy)
    _require(type(t) is int and 0 <= t < EPISODES, "ACTION_INDEX")
    block = t // 4
    perm = list(ACTIONS)
    key = _key(entropy, b"action")
    for step in range(3, 0, -1):
        j = _uniform_below(key, block, step, step + 1)
        perm[step], perm[j] = perm[j], perm[step]
    return perm[t % 4]


def witness_id(entropy: bytes, t: int) -> str:
    """Opaque public event ID; no source-label/seed/clock substring exposed."""
    _validate_entropy(entropy)
    _require(type(t) is int and 0 <= t < EPISODES, "WITNESS_INDEX")
    return _word(_key(entropy, b"witness"), b"witness-id/", t).hex()


def _bit(key: bytes, t: int, label: str) -> int:
    return _word(key, b"world-" + label.encode("ascii") + b"/", t)[0] & 1


def engineering_fixture(source_label: str, entropy: bytes) -> tuple[dict, ...]:
    """Public construction tests only. Test entropy is NOT secret science data."""
    _require(type(source_label) is str and
             source_label in ENGINEERING_FIXTURES, "REGISTERED_FIRST_USE_FORBIDDEN")
    _validate_entropy(entropy)
    world_key = _key(entropy, b"world")
    u, v, w = (_bit(world_key, -1, "initial-" + str(i)) for i in range(3))
    latent = _bit(world_key, -1, "private-initial")
    previous_action = (0, 0)
    tape = []
    for t in range(EPISODES):
        a, b = action_at(entropy, t)
        novel = 32 <= t < 72
        disturbance = (_bit(world_key, t, "noise0") &
                       _bit(world_key, t, "noise1") &
                       _bit(world_key, t, "noise2") &
                       _bit(world_key, t, "noise3"))
        if novel:
            s2 = previous_action[0] ^ (b & w) ^ (latent & v) ^ disturbance
            reward = s2 ^ previous_action[1] ^ (a & u) ^ (latent & previous_action[0])
        else:
            s2 = u ^ (a & v) ^ (b & w) ^ (latent & u) ^ disturbance
            reward = s2 ^ b ^ (u & v) ^ (latent & w)
        post = (v ^ a, s2, w ^ b)
        tape.append({"id": witness_id(entropy, t),
                     "views": ((u, v), (v, w)), "action": (a, b),
                     "s2": s2, "y": reward, "post": post})
        latent ^= (a & w) ^ (b & u)
        u, v, w = post
        previous_action = (a, b)
    _require(len(tape) == EPISODES and len({r["id"] for r in tape}) == EPISODES,
             "PUBLIC_WITNESS_UNIQUENESS")
    _require(all(left["post"] ==
                 (right["views"][0][0], right["views"][0][1],
                  right["views"][1][1]) for left, right in zip(tape, tape[1:])),
             "PUBLIC_CAUSAL_CONTINUITY")
    return tuple(tape)


def generate_registered(seed: int, entropy: bytes | None = None) -> tuple[dict, ...]:
    """Protected original cohorts are unconditionally disabled by this module."""
    _require(type(seed) is int and seed in REGISTERED, "UNKNOWN_REGISTERED_SEED")
    raise ValueError("CAP04_V2_REGISTERED_FIRST_USE_FORBIDDEN")
