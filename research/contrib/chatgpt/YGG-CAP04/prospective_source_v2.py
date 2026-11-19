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
import re

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


def _source_id_bytes(source_label: str) -> bytes:
    _require(type(source_label) is str and
             source_label in ENGINEERING_FIXTURES,
             "REGISTERED_FIRST_USE_FORBIDDEN")
    return source_label.encode("ascii")


def _hex_sha(text: str) -> bytes:
    _require(type(text) is str and re.fullmatch(r"[0-9a-f]{40}", text)
             is not None, "PINNED_GIT_SHA_REQUIRED")
    return text.encode("ascii")


def _key(entropy: bytes, role: bytes, source_label: str) -> bytes:
    _validate_entropy(entropy)
    _require(type(role) is bytes and role in
             (b"action", b"witness", b"world"), "PRIVATE_KEY_ROLE")
    return hmac.new(entropy, b"YGG-CAP04/v2/" + role + b"/" +
                    _source_id_bytes(source_label), hashlib.sha256).digest()


def commitment(entropy: bytes, source_label: str,
               source_tree_sha: str, prereg_blob_sha: str) -> str:
    """Opaque commitment binds source identity, qualified Git tree and prereg.

    This does not validate CSPRNG quality, custody, or the selected Git refs.
    An authorized source owner must verify those independently and retain a
    private uniqueness ledger before any protected scientific first-use.
    """
    _validate_entropy(entropy)
    label = _source_id_bytes(source_label)
    tree = _hex_sha(source_tree_sha)
    prereg = _hex_sha(prereg_blob_sha)
    material = (b"YGG-CAP04/v2/source-bound-commitment\x00" + label +
                b"\x00" + tree + b"\x00" + prereg + b"\x00" + entropy)
    return hashlib.sha256(material).hexdigest()


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


def action_at(source_label: str, entropy: bytes, t: int) -> tuple[int, int]:
    """Action is exogenous, before outcome; no hidden state, phase, or ID input."""
    _validate_entropy(entropy)
    _require(type(t) is int and 0 <= t < EPISODES, "ACTION_INDEX")
    block = t // 4
    perm = list(ACTIONS)
    key = _key(entropy, b"action", source_label)
    for step in range(3, 0, -1):
        j = _uniform_below(key, block, step, step + 1)
        perm[step], perm[j] = perm[j], perm[step]
    return perm[t % 4]


def witness_id(source_label: str, entropy: bytes, t: int) -> str:
    """Opaque public event ID; no source-label/seed/clock substring exposed."""
    _validate_entropy(entropy)
    _require(type(t) is int and 0 <= t < EPISODES, "WITNESS_INDEX")
    return _word(_key(entropy, b"witness", source_label), b"witness-id/", t).hex()


def _bit(key: bytes, t: int, label: str) -> int:
    return _word(key, b"world-" + label.encode("ascii") + b"/", t)[0] & 1


def engineering_fixture(source_label: str, entropy: bytes) -> tuple[dict, ...]:
    """Public construction tests only. Test entropy is NOT secret science data."""
    _require(type(source_label) is str and
             source_label in ENGINEERING_FIXTURES, "REGISTERED_FIRST_USE_FORBIDDEN")
    _validate_entropy(entropy)
    world_key = _key(entropy, b"world", source_label)
    u, v, w = (_bit(world_key, -1, "initial-" + str(i)) for i in range(3))
    latent = _bit(world_key, -1, "private-initial")
    previous_action = (0, 0)
    tape = []
    for t in range(EPISODES):
        a, b = action_at(source_label, entropy, t)
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
        tape.append({"id": witness_id(source_label, entropy, t),
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
