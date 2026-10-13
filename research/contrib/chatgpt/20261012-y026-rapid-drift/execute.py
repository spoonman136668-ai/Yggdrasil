"""Y026: fresh-cohort rapid drift stress test of matched-cache causal retention."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PRIOR_SOURCE = Path(__file__).resolve().parent.parent / "20261012-y025-matched-memory" / "execute.py"
_spec = importlib.util.spec_from_file_location("y025_frozen_source", PRIOR_SOURCE)
assert _spec and _spec.loader
_prior = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_prior)


def rapid_drift_neighborhoods(seed, episode, active):
    homes = {key: (7 * key + seed + 5 * episode) % 16 for key in active}
    for key in active[1:4]:
        homes[key] = homes[active[0]]
    return {
        key: {(home + offset) % 16 for offset in range(-2, 3)}
        for key, home in homes.items()
    }


def evaluate(seed, use_cache):
    cache = OrderedDict()
    prev_active = set()
    prev_assignment = {}
    evaluator_history = {}
    episodes = []
    for ep in range(8):
        active = _prior.active_keys(seed, ep)
        neighbors = rapid_drift_neighborhoods(seed, ep, active)
        assert _prior.hall_cardinality(active, neighbors) == 7
        preferred = {key: cache[key] for key in active if key in cache} if use_cache else {}
        legal_preferred = {key: cell for key, cell in preferred.items()
                           if cell in neighbors[key]}
        assigned, calls = _prior.match(active, neighbors, preferred)
        returning = [key for key in active if key in evaluator_history]
        churn = sum(assigned[key] != evaluator_history[key] for key in returning)
        for key in active:
            evaluator_history[key] = assigned[key]
        for key in active:
            cache.pop(key, None)
        writes = 0
        for key in sorted(prev_active.difference(active)):
            cache.pop(key, None)
            cache[key] = prev_assignment[key]
            writes += 1
            while len(cache) > 9:
                cache.popitem(last=False)
        assert len(cache) <= 9 and len(cache) + len(active) <= 16
        assert not set(active).intersection(cache)
        prev_active = set(active)
        prev_assignment = assigned
        episodes.append({
            "episode": ep, "cardinality": len(assigned),
            "churn": churn, "calls": calls,
            "cache_writes": writes, "cached_entries": len(cache),
            "legal_preferred": len(legal_preferred),
        })
    return {
        "seed": seed,
        "cohort": "development" if seed < 12 else "heldout",
        "arm": "cache_read" if use_cache else "matched_sham",
        "churn": sum(r["churn"] for r in episodes),
        "search_calls": sum(r["calls"] for r in episodes),
        "cache_writes": sum(r["cache_writes"] for r in episodes),
        "legal_preferred": sum(r["legal_preferred"] for r in episodes),
        "episodes": episodes,
    }


def run():
    rows = [evaluate(seed, read) for seed in range(8, 16)
            for read in (False, True)]
    for j in range(0, len(rows), 2):
        sham, cache = rows[j:j+2]
        assert sham["cache_writes"] == cache["cache_writes"]
        assert [x["cache_writes"] for x in sham["episodes"]] == [
            x["cache_writes"] for x in cache["episodes"]]
        assert [x["cached_entries"] for x in sham["episodes"]] == [
            x["cached_entries"] for x in cache["episodes"]]
    heldout = [(rows[2*(s-8)], rows[2*(s-8)+1]) for s in range(12, 16)]
    savings = [sham["churn"] - cache["churn"] for sham, cache in heldout]
    if all(value > 0 for value in savings):
        classification = "REPEATED_DRIFT_BENEFIT"
    elif sum(savings) < 0:
        classification = "STALENESS_HARM"
    else:
        classification = "MIXED"
    return {
        "schema": "yggdrasil.y026-rapid-drift-cache.v1",
        "predecessor_head": "0337b84bd23233faba7203c2897f1b8b7ccb60f9",
        "classification": classification,
        "heldout_savings": savings,
        "heldout_sham_churn": sum(a["churn"] for a, _ in heldout),
        "heldout_cache_churn": sum(b["churn"] for _, b in heldout),
        "rows": rows,
        "model_calls": 0,
        "claim_limit": "Synthetic matched-cache geometry drift only; no learned semantics"
    }


if __name__ == "__main__":
    outcome = run()
    assert outcome == run()
    print(json.dumps(outcome, sort_keys=True, indent=2))
