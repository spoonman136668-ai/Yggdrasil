"""Y024: 7-active/9-retained episodic placement under frozen collision drift."""
from collections import OrderedDict
import json


def active_keys(seed, episode):
    active = [(3 * seed + 2 * episode + 5 * j) % 16 for j in range(7)]
    assert len(active) == len(set(active)) == 7
    return active


def current_neighbors(seed, episode, active):
    homes = {key: (7 * key + seed + episode) % 16 for key in active}
    for key in active[1:4]:
        homes[key] = homes[active[0]]
    return {
        key: set((home + offset) % 16 for offset in range(-2, 3))
        for key, home in homes.items()
    }


def match(active, neighbors, preferred=None):
    owners = {}
    calls = 0
    preferred = preferred or {}
    for key in active:
        cell = preferred.get(key)
        if cell is not None and cell in neighbors[key] and cell not in owners:
            owners[cell] = key

    def augment(key, seen):
        nonlocal calls
        calls += 1
        choices = sorted(
            neighbors[key],
            key=lambda cell: (cell != preferred.get(key), cell)
        )
        for cell in choices:
            if cell in seen:
                continue
            seen.add(cell)
            previous = owners.get(cell)
            if previous is None or augment(previous, seen):
                owners[cell] = key
                return True
        return False

    for key in active:
        if key not in owners.values():
            augment(key, set())
    assigned = {key: cell for cell, key in owners.items()}
    assert len(assigned) == len(active) == 7
    assert all(cell in neighbors[key] for key, cell in assigned.items())
    return assigned, calls


def evaluate_policy(seed, retain):
    cache = OrderedDict()
    previous_active = set()
    previous_placement = {}
    observed_history = {}  # evaluator-only; the stateless policy never reads this
    rows = []
    for episode in range(8):
        active = active_keys(seed, episode)
        neighbors = current_neighbors(seed, episode, active)
        preferred = {key: cache[key] for key in active if key in cache} if retain else {}
        assigned, calls = match(active, neighbors, preferred)
        returning = [key for key in active if key in observed_history]
        churn = sum(assigned[key] != observed_history[key] for key in returning)
        for key in active:
            observed_history[key] = assigned[key]
        writes = 0
        if retain:
            for key in active:
                cache.pop(key, None)
            for key in sorted(previous_active.difference(active)):
                if key in cache:
                    del cache[key]
                cache[key] = previous_placement[key]
                writes += 1
                while len(cache) > 9:
                    cache.popitem(last=False)
            assert len(cache) <= 9
            assert not set(cache).intersection(active)
            assert len(cache) + len(active) <= 16
        previous_active = set(active)
        previous_placement = assigned
        rows.append({
            "episode": episode,
            "assigned": len(assigned),
            "returning_keys": len(returning),
            "churn": churn,
            "search_calls": calls,
            "retained_entries": len(cache),
            "cache_writes": writes,
        })
    return {
        "seed": seed,
        "cohort": "development" if seed < 4 else "heldout",
        "policy": "retained" if retain else "stateless",
        "total_churn": sum(row["churn"] for row in rows),
        "total_search_calls": sum(row["search_calls"] for row in rows),
        "total_memory_writes": sum(row["cache_writes"] for row in rows),
        "episodes": rows,
    }


def run():
    rows = [
        evaluate_policy(seed, retain)
        for seed in range(8)
        for retain in (False, True)
    ]
    heldout_pairs = [
        (rows[2 * seed], rows[2 * seed + 1])
        for seed in range(4, 8)
    ]
    differences = [
        a["total_churn"] - b["total_churn"]
        for a, b in heldout_pairs
    ]
    all_matched = all(
        episode["assigned"] == 7
        for row in rows
        for episode in row["episodes"]
    )
    assert all_matched
    if sum(differences) > 0:
        classification = "RETAINED_STATE_REDUCES_CHURN"
    elif any(x > 0 for x in differences) and any(x < 0 for x in differences):
        classification = "MIXED"
    else:
        classification = "NO_RETENTION_GAIN"
    return {
        "schema": "yggdrasil.y024-7active-9retained.v1",
        "predecessor_head": "cea2086833ea27081b4619d61ce9ecb0d8c95a8a",
        "rows": rows,
        "heldout_stateless_churn": sum(a["total_churn"] for a, _ in heldout_pairs),
        "heldout_retained_churn": sum(b["total_churn"] for _, b in heldout_pairs),
        "heldout_per_seed_churn_savings": differences,
        "classification": classification,
        "model_calls": 0,
        "claim_limit": "Finite synthetic recurrent placement only; no learned semantic consolidation",
    }


if __name__ == "__main__":
    outcome = run()
    assert outcome == run()
    print(json.dumps(outcome, sort_keys=True, indent=2))
