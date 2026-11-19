"""Fresh disjoint public causal A/B/A development stream for actual JEPA2-05.

Only witnessed public paired views, exogenous announced interventions and
subsequent public post-state/reward are provided to Yggdrasil learners.
Private shift labels and hidden mediator are evaluator-only.
"""
from __future__ import annotations
import hashlib

SEEDS = {99231: 0, 99247: 1}
EVENTS = 16
HORIZON = 3

def check(cond, label):
    if not cond:
        raise ValueError("YGG_JEPA2_05_SOURCE_" + label)

def bit(seed, t, tag):
    return hashlib.sha256(
        f"YGG-JEPA2-05/FRESH/{seed}/{t}/{tag}".encode("ascii")
    ).digest()[0] & 1

def announced_plan(seed, t):
    check(seed in SEEDS and type(t) is int and 0 <= t < EVENTS,
          "UNREGISTERED_PLAN")
    return bit(seed, t, "first"), bit(seed, t, "second")

def phase(t):
    check(type(t) is int and 0 <= t < EVENTS, "INDEX")
    return "A" if t < 6 else "B" if t < 11 else "A_return"

def generate(seed):
    check(seed in SEEDS, "FRESH_SEED")
    world = SEEDS[seed]
    u, v, w = (bit(seed, -1, k) for k in ("u", "v", "w"))
    hidden = bit(seed, -1, "hidden")
    events = []
    for t in range(EVENTS):
        first, second = announced_plan(seed, t)
        shift = int(6 <= t < 11)
        shock = bit(seed, t, "shock") & bit(seed, t, "rare")
        views = ((u, v), (v, w))
        if world == 0:
            nu = v ^ (first & u) ^ (shift & hidden)
            nv = u ^ (first & w) ^ (shift & v) ^ shock
            nw = w ^ (second & nv) ^ (shift & hidden)
            reward = (second & nv) ^ (u & w) ^ (shift & first)
            new_hidden = hidden ^ (first & w) ^ (second & v)
        else:
            nu = w ^ (first & v) ^ (shift & hidden)
            nv = v ^ (first & u) ^ (shift & w) ^ shock
            nw = u ^ (second & v) ^ (shift & hidden)
            reward = (second & nw) ^ (nu & hidden) ^ shift
            new_hidden = hidden ^ (second & u) ^ (first & w)
        check(all(type(x) is int and x in (0, 1) for x in
                  (nu, nv, nw, reward)), "OUTCOME")
        identifier = hashlib.sha256(
            f"YGG-JEPA2-05/source-id/{seed}/{t}".encode("ascii")
        ).hexdigest()
        events.append({
            "source_id": identifier,
            "views": views,
            "actions": (first, second),
            "post": (nu, nv, nw),
            "row": {"s1": u, "x1": first, "s2": nv,
                    "x2": second, "y": reward},
            "index": t,
            "phase": phase(t),        # EVALUATOR ONLY
            "seed": seed,            # EVALUATOR ONLY
            "family": world,         # EVALUATOR ONLY
        })
        u, v, w, hidden = nu, nv, nw, new_hidden
    check(len(events) == EVENTS and
          len({x["source_id"] for x in events}) == EVENTS, "SOURCE_COUNT")
    for a, b in zip(events, events[1:]):
        check(a["post"] == (b["views"][0][0], b["views"][0][1],
                            b["views"][1][1]), "PUBLIC_STATE_CONTINUITY")
    return tuple(events)
