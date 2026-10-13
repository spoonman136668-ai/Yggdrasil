"""Y028: finite alternating-drift matched-cache stress with no future peeking."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PRIOR_SOURCE = Path(__file__).resolve().parent.parent / "20261012-y027-drift-dose" / "execute.py"
_spec = importlib.util.spec_from_file_location("y027_frozen", PRIOR_SOURCE)
assert _spec and _spec.loader
y27 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y27)
y25 = y27.y25

DISPLACEMENTS = (0, 1, 6, 7, 12, 13, 18, 19)


def alternating_neighbors(seed, episode, active):
    displacement = DISPLACEMENTS[episode]
    homes = {key: (7*key+seed+displacement)%16 for key in active}
    for key in active[1:4]:
        homes[key] = homes[active[0]]
    return {
        key: {(home + d) % 16 for d in range(-2,3)}
        for key, home in homes.items()
    }


def evaluate(seed, use_cache):
    cache = OrderedDict()
    prev_active = set()
    prev_assignment = {}
    evaluator_history = {}
    rows = []
    for episode in range(8):
        active = y25.active_keys(seed, episode)
        adjacency = alternating_neighbors(seed, episode, active)
        assert y25.hall_cardinality(active, adjacency) == 7
        pref = {key: cache[key] for key in active if key in cache} if use_cache else {}
        legal_pref = {key: cell for key, cell in pref.items()
                      if cell in adjacency[key]}
        assigned, calls = y25.match(active, adjacency, pref)
        returning = [key for key in active if key in evaluator_history]
        churn = sum(assigned[key] != evaluator_history[key] for key in returning)
        for key in active:
            evaluator_history[key] = assigned[key]
        for key in active:
            cache.pop(key,None)
        writes = 0
        for key in sorted(prev_active.difference(active)):
            cache.pop(key,None)
            cache[key] = prev_assignment[key]
            writes += 1
            while len(cache)>9:
                cache.popitem(last=False)
        assert len(cache) <= 9 and len(cache)+7<=16
        assert not set(cache).intersection(active)
        prev_active = set(active)
        prev_assignment = assigned
        rows.append({"episode": episode, "displacement": DISPLACEMENTS[episode],
                     "assigned": len(assigned), "churn": churn, "calls": calls,
                     "cache_writes": writes, "cache_entries": len(cache),
                     "legal_preference_count": len(legal_pref)})
    return {
        "seed": seed, "cohort": "development" if seed<28 else "heldout",
        "arm": "cache_read" if use_cache else "matched_sham",
        "churn": sum(r["churn"] for r in rows),
        "search_calls": sum(r["calls"] for r in rows),
        "cache_writes": sum(r["cache_writes"] for r in rows),
        "legal_preference_count": sum(r["legal_preference_count"] for r in rows),
        "episodes": rows
    }


def run():
    rows = [evaluate(seed,read) for seed in range(24,32)
            for read in (False,True)]
    for i in range(0,len(rows),2):
        sham,retained=rows[i:i+2]
        assert sham["cache_writes"] == retained["cache_writes"]
        assert [e["cache_entries"] for e in sham["episodes"]] == [
            e["cache_entries"] for e in retained["episodes"]]
        assert all(e["assigned"]==7 for r in (sham,retained) for e in r["episodes"])
    pairs = [(rows[2*(seed-24)], rows[2*(seed-24)+1]) for seed in range(28,32)]
    savings = [sham["churn"]-cache["churn"] for sham,cache in pairs]
    total = sum(savings)
    classification = ("ALTERNATING_DRIFT_BENEFIT" if total>0 else
                      "HARM" if total<0 else "NEUTRAL")
    return {
        "schema": "yggdrasil.y028-alternating-drift.v1",
        "predecessor_head": "953cdd64cfac1dc84ac782653f2d49a54101e90a",
        "classification": classification,
        "displacements": DISPLACEMENTS,
        "heldout_churn_savings": savings,
        "heldout_sham_churn": sum(a["churn"] for a,b in pairs),
        "heldout_cache_churn": sum(b["churn"] for a,b in pairs),
        "heldout_legal_preferences": sum(b["legal_preference_count"] for a,b in pairs),
        "rows": rows,
        "model_calls": 0,
        "claim_limit": "Synthetic alternating-drift matching, not learned cognition"
    }


if __name__ == "__main__":
    result = run()
    assert result == run()
    print(json.dumps(result, sort_keys=True, indent=2))
