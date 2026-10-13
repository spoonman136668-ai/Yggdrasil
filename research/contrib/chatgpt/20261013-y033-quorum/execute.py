"""Y033: frozen quorum trigger on currently legal observed-cache assignments."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PARENT = Path(__file__).resolve().parent.parent / "20261013-y032-conflict-frontier" / "execute.py"
spec = importlib.util.spec_from_file_location("y032_frozen", PARENT)
assert spec and spec.loader
y32 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(y32)
y29 = y32.y29
y25 = y32.y25

DEVELOPMENT = tuple(range(128,136))
HELDOUT = tuple(range(136,152))
REGIMES = ("drift1", "drift3", "drift5", "alternating")
POLICIES = ("matched_sham", "full", "quorum2", "quorum3")


def execute(seed, regime, policy):
    cache = OrderedDict()
    previous_active = set()
    previous_assignment = {}
    evaluator_only_observed = {}
    rows = []
    for episode in range(8):
        active = y25.active_keys(seed, episode)
        neighbors = y29.neighbors(seed, episode, active, regime)
        assert y25.hall_cardinality(active, neighbors) == 7
        legal = {key: cache[key] for key in active
                 if key in cache and cache[key] in neighbors[key]}
        minimum = {"matched_sham": 999, "full": 1,
                   "quorum2": 2, "quorum3": 3}[policy]
        preferred = legal if len(legal) >= minimum else {}
        allocation, calls = y25.match(active, neighbors, preferred)
        assert len(allocation) == 7 and len(set(allocation.values())) == 7
        returning = [key for key in active if key in evaluator_only_observed]
        churn = sum(allocation[key] != evaluator_only_observed[key]
                    for key in returning)
        for key in active:
            evaluator_only_observed[key] = allocation[key]
        for key in active:
            cache.pop(key, None)
        writes = 0
        for key in sorted(previous_active.difference(active)):
            cache.pop(key, None)
            cache[key] = previous_assignment[key]
            writes += 1
            while len(cache) > 9:
                cache.popitem(last=False)
        assert len(cache) <= 9 and len(cache) + 7 <= 16
        assert not set(cache).intersection(active)
        previous_active = set(active)
        previous_assignment = allocation
        rows.append({
            "episode": episode, "matched": len(allocation), "churn": churn,
            "search_calls": calls, "cache_writes": writes,
            "cached_keys": list(cache), "legal_cache_candidates": len(legal),
            "applied_preference_count": len(preferred),
        })
    return {
        "seed": seed, "churn": sum(x["churn"] for x in rows),
        "search_calls": sum(x["search_calls"] for x in rows),
        "cache_writes": sum(x["cache_writes"] for x in rows),
        "applied_preferences": sum(x["applied_preference_count"] for x in rows),
        "episodes": rows,
    }


def regime_result(regime):
    results = []
    for seed in DEVELOPMENT + HELDOUT:
        policies = {p: execute(seed, regime, p) for p in POLICIES}
        sham = policies["matched_sham"]
        for outcome in policies.values():
            assert sham["cache_writes"] == outcome["cache_writes"]
            for a, b in zip(sham["episodes"], outcome["episodes"]):
                assert a["cache_writes"] == b["cache_writes"]
                assert a["cached_keys"] == b["cached_keys"]
                assert a["matched"] == b["matched"] == 7
        results.append({
            "seed": seed, "cohort": "development" if seed in DEVELOPMENT else "heldout",
            "churn": {p: v["churn"] for p, v in policies.items()},
            "search_calls": {p: v["search_calls"] for p, v in policies.items()},
            "preferences": {p: v["applied_preferences"] for p, v in policies.items()},
            "paired_writes": sham["cache_writes"],
        })
    sealed = [x for x in results if x["cohort"] == "heldout"]
    totals = {p: sum(x["churn"][p] for x in sealed) for p in POLICIES}
    saved = {p: totals["matched_sham"] - totals[p] for p in POLICIES[1:]}
    return {
        "regime": regime, "heldout_churn": totals,
        "sham_relative_savings": saved,
        "heldout_preferences": {p: sum(x["preferences"][p] for x in sealed)
                               for p in POLICIES},
        "seed_rows": results,
    }


def run():
    rows = [regime_result(regime) for regime in REGIMES]
    r = {x["regime"]: x for x in rows}
    slow = r["drift1"]["sham_relative_savings"]
    improvement = {
        policy: {
            regime: r[regime]["heldout_churn"][policy] <
                    r[regime]["heldout_churn"]["full"]
            for regime in ("drift5", "alternating")
        } for policy in ("quorum2", "quorum3")
    }
    if all(improvement["quorum2"].values()) and slow["quorum2"] >= .7*slow["full"]:
        classification = "QUORUM_GAIN"
    elif any(any(m.values()) for m in improvement.values()):
        classification = "TRADEOFF"
    else:
        classification = "NO_QUORUM_GAIN"
    return {
        "schema": "yggdrasil.y033-cache-quorum.v1",
        "parent_head": "b018e50abf546553fe2790a553afcdd967b6f327",
        "classification": classification, "development_seeds": DEVELOPMENT,
        "sealed_heldout_seeds": HELDOUT, "regimes": rows,
        "model_calls": 0,
        "claim_limit": "Current-state-only synthetic cache quorum policy"
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
