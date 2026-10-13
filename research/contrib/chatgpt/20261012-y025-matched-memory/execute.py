"""Y025: matched-cache sham experiment, independent 7-key Hall oracle."""
from collections import OrderedDict
import json


def active_keys(seed, episode):
    active = [(3 * seed + 2 * episode + 5 * j) % 16 for j in range(7)]
    assert len(active) == 7 and len(set(active)) == 7
    return active


def neighborhoods(seed, episode, active):
    homes = {key: (7 * key + seed + episode) % 16 for key in active}
    for key in active[1:4]:
        homes[key] = homes[active[0]]
    return {
        key: {(home + offset) % 16 for offset in range(-2, 3)}
        for key, home in homes.items()
    }


def hall_cardinality(active, neighbor):
    maximum_deficiency = 0
    for subset in range(1, 1 << 7):
        union = set()
        for j, key in enumerate(active):
            if subset & (1 << j):
                union.update(neighbor[key])
        maximum_deficiency = max(maximum_deficiency, subset.bit_count() - len(union))
    return 7 - maximum_deficiency


def match(active, neighbors, preferred):
    owners = {}
    calls = 0
    for key in active:
        cell = preferred.get(key)
        if cell is not None and cell in neighbors[key] and cell not in owners:
            owners[cell] = key

    def augment(key, seen):
        nonlocal calls
        calls += 1
        for cell in sorted(neighbors[key], key=lambda c: (c != preferred.get(key), c)):
            if cell in seen:
                continue
            seen.add(cell)
            prior = owners.get(cell)
            if prior is None or augment(prior, seen):
                owners[cell] = key
                return True
        return False

    for key in active:
        if key not in owners.values():
            augment(key, set())
    assigned = {key: cell for cell, key in owners.items()}
    assert len(assigned) == hall_cardinality(active, neighbors)
    assert len(assigned) == 7
    assert len(set(assigned.values())) == 7
    assert all(cell in neighbors[key] for key, cell in assigned.items())
    return assigned, calls


def evaluate(seed, use_cache):
    cache = OrderedDict()
    prev_active = set()
    prev_assignment = {}
    evaluator_history = {}
    trace = []
    for episode in range(8):
        active = active_keys(seed, episode)
        neighbor = neighborhoods(seed, episode, active)
        pref = {key: cache[key] for key in active if key in cache} if use_cache else {}
        legal_pref = {k: v for k, v in pref.items() if v in neighbor[k]}
        assigned, calls = match(active, neighbor, pref)
        returning = [key for key in active if key in evaluator_history]
        churn = sum(assigned[key] != evaluator_history[key] for key in returning)
        for key in active:
            evaluator_history[key] = assigned[key]
        # Cache writes occur in BOTH arms; only the read pathway is ablated.
        for key in active:
            cache.pop(key, None)
        writes = 0
        for key in sorted(prev_active.difference(active)):
            cache.pop(key, None)
            cache[key] = prev_assignment[key]
            writes += 1
            while len(cache) > 9:
                cache.popitem(last=False)
        assert len(cache) <= 9
        assert len(cache) + len(active) <= 16
        assert not set(active).intersection(cache)
        prev_active = set(active)
        prev_assignment = assigned
        trace.append({
            "episode": episode,
            "matching_cardinality": len(assigned),
            "returning": len(returning),
            "churn": churn,
            "search_calls": calls,
            "cache_writes": writes,
            "cache_entries": len(cache),
            "legal_preference_count": len(legal_pref),
        })
    return {
        "seed": seed,
        "cohort": "development" if seed < 4 else "heldout",
        "arm": "cache_read" if use_cache else "matched_sham",
        "total_churn": sum(ep["churn"] for ep in trace),
        "total_cache_writes": sum(ep["cache_writes"] for ep in trace),
        "total_search_calls": sum(ep["search_calls"] for ep in trace),
        "total_legal_preference_count": sum(ep["legal_preference_count"] for ep in trace),
        "trace": trace,
    }


def run():
    rows = [evaluate(seed, read) for seed in range(8) for read in (False, True)]
    pairs = [(rows[2*s], rows[2*s+1]) for s in range(4, 8)]
    for a, b in pairs:
        assert a["total_cache_writes"] == b["total_cache_writes"]
        assert [
            ep["cache_entries"] for ep in a["trace"]
        ] == [ep["cache_entries"] for ep in b["trace"]]
        assert [ep["cache_writes"] for ep in a["trace"]] == [
            ep["cache_writes"] for ep in b["trace"]
        ]
    savings = [a["total_churn"] - b["total_churn"] for a, b in pairs]
    if all(s > 0 for s in savings):
        classification = "CAUSAL_CACHE_READ_BENEFIT"
    elif any(s > 0 for s in savings) and any(s < 0 for s in savings):
        classification = "MIXED"
    else:
        classification = "NO_CACHE_READ_BENEFIT"
    return {
        "schema": "yggdrasil.y025-matched-cache-read-ablation.v1",
        "predecessor_head": "71cc6c66c2623577090e4a71fb4ebb52669e06ab",
        "classification": classification,
        "heldout_per_seed_savings": savings,
        "heldout_sham_churn": sum(a["total_churn"] for a, _ in pairs),
        "heldout_cache_read_churn": sum(b["total_churn"] for _, b in pairs),
        "rows": rows,
        "model_calls": 0,
        "claim_limit": "Matched bookkeeping control on synthetic placement; not learned semantic memory",
    }


if __name__ == "__main__":
    outcome = run()
    assert outcome == run()
    print(json.dumps(outcome, sort_keys=True, indent=2))
