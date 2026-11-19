"""Disjoint multi-variable sequential causal development source (YGG-JEPA2-04).

This is an actual action/consequence source for the SAME native Yggdrasil
checkpoint, but is a new synthetic DEVELOPMENT family, not a physical-world
dataset or independently qualified scientific first-use. All actions in each
3-step intervention plan are publicly specified BEFORE any of its outcomes.
Only public observed views, plans, actions and consequence rows enter learners.
Private rule phases/mediators are evaluator-only and NEVER model inputs.
"""
from __future__ import annotations
import hashlib

SEEDS = (95413, 95429)
WORLDS = (0, 1)
EVENTS_PER_WORLD = 120
PHASES = ("warm", "stable_A", "early_B", "late_B", "early_return_A", "late_return_A")


def check(value, name):
    if not value:
        raise ValueError("YGG_JEPA2_04_SOURCE_" + name)


def bit(seed, world, t, label):
    raw = f"YGG-JEPA2-04/schedule/{seed}/{world}/{t}/{label}".encode()
    return hashlib.sha256(raw).digest()[0] & 1


def phase(t):
    check(type(t) is int and 0 <= t < EVENTS_PER_WORLD, "TIME")
    if t < 16:
        return "warm"
    if t < 44:
        return "stable_A"
    if t < 56:
        return "early_B"
    if t < 83:
        return "late_B"
    if t < 98:
        return "early_return_A"
    return "late_return_A"


def announced_plan(seed, world, t):
    """An exogenous announced two-intervention public action schedule."""
    check(seed in SEEDS and world in WORLDS and 0 <= t < EVENTS_PER_WORLD,
          "SCHEDULE")
    return (bit(seed, world, t, "x1"), bit(seed, world, t, "x2"))


def generate(seed, world):
    check(seed in SEEDS and world in WORLDS, "SEED_WORLD")
    u, v, w = (bit(seed, world, -1, tag) for tag in ("u", "v", "w"))
    hidden_mediator = bit(seed, world, -1, "hidden")
    out = []
    for t in range(EVENTS_PER_WORLD):
        a, b = announced_plan(seed, world, t)
        # Exogenous disturbance never supplied to native or latent learners.
        disturbance = (bit(seed, world, t, "shock")
                       & bit(seed, world, t, "rare"))
        regime = 1 if 44 <= t < 83 else 0
        views = ((u, v), (v, w))
        old_u, old_v, old_w, old_m = u, v, w, hidden_mediator
        if world == 0:
            nu = old_u ^ (a & old_v) ^ (regime & old_m)
            nv = old_v ^ (b & old_m) ^ (a & old_u) ^ disturbance
            nw = old_w ^ (a & old_m) ^ (regime & b) ^ (old_u & old_v)
            y = nw ^ (nv & b) ^ (old_m & a)
            hidden_mediator = old_m ^ (a & old_w) ^ (b & old_u)
        else:
            nu = old_v ^ (a & old_u) ^ (regime & old_w)
            nv = old_w ^ (b & old_u) ^ (a & old_m) ^ disturbance
            nw = old_u ^ (b & old_v) ^ (regime & old_m)
            y = nu ^ (nv & b) ^ (nw & a) ^ old_m
            hidden_mediator = old_m ^ (old_v & b) ^ (old_w & a)
        check(all(q in (0, 1) for q in (nu, nv, nw, y)), "BINARY_STATE")
        identifier = hashlib.sha256(
            f"YGG-JEPA2-04/public/{seed}/{world}/{t}".encode()
        ).hexdigest()
        out.append({
            "source_id": identifier,
            "views": views,  # pre-intervention public sensor projections
            "actions": (a, b),  # announced ex ante, not after observing
            "post": (nu, nv, nw),  # public observed POST-intervention sensors
            "row": {"s1": u, "x1": a, "s2": nv, "x2": b, "y": y},
            "phase": phase(t),  # evaluator ONLY, never a model input
            "world": world, "index": t, "seed": seed,
        })
        u, v, w = nu, nv, nw
    check(len(out) == EVENTS_PER_WORLD
          and len({row["source_id"] for row in out}) == EVENTS_PER_WORLD,
          "SOURCE_COUNT")
    for i in range(EVENTS_PER_WORLD - 1):
        check(tuple(out[i]["post"]) ==
              (out[i+1]["views"][0][0], out[i+1]["views"][0][1],
               out[i+1]["views"][1][1]), "PUBLIC_TRANSITION_CONTINUITY")
    return tuple(out)

