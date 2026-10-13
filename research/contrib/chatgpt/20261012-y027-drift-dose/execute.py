"""Y027: preregistered drift-dose response of write-matched bounded cache."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PRIOR_SOURCE = Path(__file__).resolve().parent.parent / "20261012-y026-rapid-drift" / "execute.py"
_spec = importlib.util.spec_from_file_location("y026_frozen", PRIOR_SOURCE)
assert _spec and _spec.loader
y26 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y26)
y25 = y26._prior


def neighbors(seed, episode, active, drift):
    homes = {key: (7*key + seed + drift*episode) % 16 for key in active}
    for key in active[1:4]:
        homes[key] = homes[active[0]]
    return {
        key: {(home + offset) % 16 for offset in range(-2, 3)}
        for key, home in homes.items()
    }


def evaluate(seed, drift, use_memory):
    cache = OrderedDict()
    prev_active = set()
    prev_assignment = {}
    evaluator_history = {}
    episodes = []
    for ep in range(8):
        active = y25.active_keys(seed, ep)
        adjacency = neighbors(seed, ep, active, drift)
        assert y25.hall_cardinality(active, adjacency) == 7
        pref = {k: cache[k] for k in active if k in cache} if use_memory else {}
        legal = {k: cell for k, cell in pref.items() if cell in adjacency[k]}
        assignments, calls = y25.match(active, adjacency, pref)
        returning = [k for k in active if k in evaluator_history]
        churn = sum(assignments[k] != evaluator_history[k] for k in returning)
        for k in active:
            evaluator_history[k] = assignments[k]
        for k in active:
            cache.pop(k, None)
        writes = 0
        for k in sorted(prev_active.difference(active)):
            cache.pop(k, None)
            cache[k] = prev_assignment[k]
            writes += 1
            while len(cache) > 9:
                cache.popitem(last=False)
        assert len(cache) <= 9
        assert len(cache) + 7 <= 16
        assert not set(cache).intersection(active)
        prev_active = set(active)
        prev_assignment = assignments
        episodes.append({"episode": ep, "churn": churn, "calls": calls,
                         "writes": writes, "memory_occupancy": len(cache),
                         "legal_pref": len(legal), "matched": len(assignments)})
    return {
        "seed": seed, "cohort": "development" if seed < 20 else "heldout",
        "drift": drift, "arm": "cache_read" if use_memory else "matched_sham",
        "churn": sum(e["churn"] for e in episodes),
        "search_calls": sum(e["calls"] for e in episodes),
        "cache_writes": sum(e["writes"] for e in episodes),
        "legal_prefs": sum(e["legal_pref"] for e in episodes),
        "episodes": episodes
    }


def dose_results(drift):
    rows = [evaluate(seed, drift, read) for seed in range(16,24)
            for read in (False, True)]
    for index in range(0,len(rows),2):
        a,b=rows[index:index+2]
        assert a["cache_writes"] == b["cache_writes"]
        assert [r["memory_occupancy"] for r in a["episodes"]] == [
            r["memory_occupancy"] for r in b["episodes"]]
        assert all(ep["matched"] == 7 for r in (a,b) for ep in r["episodes"])
    heldout = [(rows[2*(seed-16)], rows[2*(seed-16)+1])
               for seed in range(20,24)]
    savings = [a["churn"]-b["churn"] for a,b in heldout]
    total = sum(savings)
    return {
        "drift": drift,
        "heldout_savings": savings,
        "heldout_total_savings": total,
        "heldout_sham_churn": sum(a["churn"] for a,b in heldout),
        "heldout_memory_churn": sum(b["churn"] for a,b in heldout),
        "heldout_legal_prefs": sum(b["legal_prefs"] for a,b in heldout),
        "heldout_sham_search_calls": sum(a["search_calls"] for a,b in heldout),
        "heldout_memory_search_calls": sum(b["search_calls"] for a,b in heldout),
        "label": "BENEFIT" if total>0 else "HARM" if total<0 else "NEUTRAL",
        "rows": rows
    }


def run():
    rows = [dose_results(drift) for drift in (1,3,5)]
    savings = [r["heldout_total_savings"] for r in rows]
    classification = "MONOTONE_DECAY" if savings[0]>savings[1]>savings[2] else "OTHERWISE_NONMONOTONE"
    return {
        "schema": "yggdrasil.y027-retention-drift-dose.v1",
        "predecessor_head": "3983e1f9a99b57786eafa28d9b4d5b0cb7be575e",
        "classification": classification,
        "drift_results": rows,
        "model_calls": 0,
        "claim_limit": "Frozen synthetic cache-dose response; no learned semantic memory"
    }


if __name__ == "__main__":
    data = run()
    assert data == run()
    print(json.dumps(data, sort_keys=True, indent=2))
