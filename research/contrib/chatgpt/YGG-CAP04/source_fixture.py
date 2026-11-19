"""Engineering fixtures ONLY for CAP04 source-clock and comparator interfaces.

No registered prospective development/pilot/primary source is implemented or
reachable. These are independently fabricated engineering examples, not claims
of learned unfamiliar-world transfer, causal discovery or SCIENTIFIC_PASS.
"""
from __future__ import annotations
import hashlib

FIXTURE_IDS = ("engineering-history-01", "engineering-history-02")
MAX_FIXTURE_EVENTS = 96
ARMS = ((0, 0), (0, 1), (1, 0), (1, 1))
RESERVED_SCIENTIFIC_SEEDS = (99917, 99931, 100017, 100031, 100117, 100131, 100151)


def require(ok, tag):
    if not ok:
        raise ValueError("CAP04_FIXTURE_" + tag)


def bit(name):
    return hashlib.sha256(name.encode("ascii")).digest()[0] & 1


def generate(fixture_id="engineering-history-01", n=96):
    require(type(fixture_id) is str and fixture_id in FIXTURE_IDS,
            "REGISTERED_SCIENCE_FORBIDDEN")
    require(type(n) is int and 1 <= n <= MAX_FIXTURE_EVENTS, "BUDGET")
    u, v, w = (bit(f"{fixture_id}/start/{i}") for i in range(3))
    previous = (0, 0)
    records = []
    for t in range(n):
        views = ((u, v), (v, w))
        # Uniform intervention identity coverage in each consecutive block.
        action = ARMS[(t + (1 if fixture_id == FIXTURE_IDS[1] else 0)) % 4]
        # A/B/A drift is a KNOWN construction of fixtures, not science evidence.
        mode = "novel" if 32 <= t < 72 else "familiar"
        disturbed = bit(f"{fixture_id}/{t}/disturb") & bit(f"{fixture_id}/{t}/rare")
        if mode == "familiar":
            s2 = v ^ (action[0] & w) ^ disturbed
            reward = (s2 ^ action[1] ^ (u & v))
        else:
            # First action depends on a genuinely preceding witnessed action.
            s2 = previous[0] ^ action[1] ^ disturbed
            reward = s2 ^ previous[1] ^ (u & action[0])
        post = (v ^ action[0], s2, w ^ action[1])
        identifier = hashlib.sha256(
            f"cap04/engineering-only/{fixture_id}/{t}".encode("ascii")
        ).hexdigest()
        records.append({"id": identifier, "views": views, "action": action,
                        "s2": s2, "y": reward, "post": post})
        u, v, w = post
        previous = action
    require(len(records) == len({e["id"] for e in records}), "UNIQUE_SOURCE")
    return tuple(records)
