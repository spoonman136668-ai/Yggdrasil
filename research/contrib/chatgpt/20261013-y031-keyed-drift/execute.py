"""Y031 first-use keyed geometry alternating rotation and matched-cache ablation."""
import hashlib
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PREVIOUS = Path(__file__).resolve().parent.parent / "20261012-y030-new-family" / "execute.py"
_spec = importlib.util.spec_from_file_location("y030_frozen", PREVIOUS)
assert _spec and _spec.loader
y030 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y030)

SHIFTS = (0, 1, 6, 7, 12, 13, 18, 19)


def geometry(seed, episode):
    active, neighbors = y030.geometry(seed, episode)
    rotation = SHIFTS[episode] % 16
    rotated = {
        key: {(cell + rotation) % 16 for cell in neighbors[key]}
        for key in active
    }
    assert all(len(rotated[key]) == len(neighbors[key]) == 5 for key in active)
    return active, rotated


def population_signature(seed):
    episodes = []
    for ep in range(8):
        active, neighbors = geometry(seed, ep)
        episodes.append({
            "active": active,
            "neighbor_sets": [sorted(neighbors[key]) for key in active],
        })
    canonical = json.dumps(episodes, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def evaluate(seed, read_cache):
    cache = OrderedDict()
    prev_active = set()
    prev_assignments = {}
    observation_history = {}
    rows = []
    for episode in range(8):
        active, neighbor = geometry(seed, episode)
        legal_from_memory = {
            key: cache[key] for key in active
            if key in cache and cache[key] in neighbor[key]
        }
        preferred = legal_from_memory if read_cache else {}
        matching, calls = y030.match(active, neighbor, preferred)
        assert len(matching) == 7
        prior_returning = [key for key in active if key in observation_history]
        churn = sum(matching[key] != observation_history[key] for key in prior_returning)
        for key in active:
            observation_history[key] = matching[key]
        for key in active:
            cache.pop(key, None)
        writes = 0
        for key in sorted(prev_active.difference(active)):
            cache.pop(key, None)
            cache[key] = prev_assignments[key]
            writes += 1
            while len(cache) > 9:
                cache.popitem(last=False)
        assert len(cache) <= 9 and len(cache) + len(active) <= 16
        assert not set(cache).intersection(active)
        prev_active = set(active)
        prev_assignments = matching
        rows.append({
            "episode": episode,
            "rotation": SHIFTS[episode],
            "matching_cardinality": len(matching),
            "returning": len(prior_returning),
            "churn": churn,
            "calls": calls,
            "writes": writes,
            "cache_entries": len(cache),
            "legal_preference_hits": len(preferred),
        })
    return {
        "seed": seed,
        "cohort": "development" if seed < 52 else "heldout",
        "policy": "cache_read" if read_cache else "matched_write_sham",
        "total_churn": sum(r["churn"] for r in rows),
        "total_calls": sum(r["calls"] for r in rows),
        "total_writes": sum(r["writes"] for r in rows),
        "total_legal_preferences": sum(r["legal_preference_hits"] for r in rows),
        "episodes": rows,
    }


def run():
    signatures = {str(seed): population_signature(seed) for seed in range(48, 56)}
    distinct = len(set(signatures.values())) == 8
    hall_violations = []
    for seed in range(48, 56):
        for episode in range(8):
            active, neighbor = geometry(seed, episode)
            size = y030.hall_cardinality(active, neighbor)
            if size < 7:
                hall_violations.append({"seed": seed, "episode": episode, "hall": size})
    if not distinct or hall_violations:
        return {
            "schema": "yggdrasil.y031-keyed-geometry-alternating-drift.v1",
            "predecessor_head": "72b64a2b9a5344ad3064978c9a4a823c26cac4c4",
            "classification": "NONUNIQUE_GEOMETRY" if not distinct else "GEOMETRY_DEFICIENCY",
            "signatures": signatures,
            "hall_violations": hall_violations,
            "rows": [],
            "model_calls": 0,
            "claim_limit": "Synthetic geometry falsification; deficient episodes preserved.",
        }
    rows = [evaluate(seed, read_cache) for seed in range(48, 56)
            for read_cache in (False, True)]
    for i in range(0, len(rows), 2):
        sham, retained = rows[i:i+2]
        assert sham["total_writes"] == retained["total_writes"]
        assert [r["cache_entries"] for r in sham["episodes"]] == [
            r["cache_entries"] for r in retained["episodes"]
        ]
        assert all(r["matching_cardinality"] == 7 for arm in (sham, retained)
                   for r in arm["episodes"])
    heldout = [(rows[2*(seed-48)], rows[2*(seed-48)+1])
               for seed in range(52, 56)]
    savings = [a["total_churn"] - b["total_churn"] for a, b in heldout]
    if all(s > 0 for s in savings):
        outcome = "ALL_SEED_BENEFIT"
    elif any(s > 0 for s in savings) and any(s <= 0 for s in savings):
        outcome = "MIXED"
    elif sum(savings) < 0:
        outcome = "HARM"
    else:
        outcome = "NO_BENEFIT"
    return {
        "schema": "yggdrasil.y031-keyed-geometry-alternating-drift.v1",
        "predecessor_head": "72b64a2b9a5344ad3064978c9a4a823c26cac4c4",
        "classification": outcome,
        "signatures": signatures,
        "unique_signatures": distinct,
        "heldout_savings": savings,
        "heldout_sham_churn": sum(a["total_churn"] for a, _ in heldout),
        "heldout_cached_churn": sum(b["total_churn"] for _, b in heldout),
        "heldout_sham_calls": sum(a["total_calls"] for a, _ in heldout),
        "heldout_cached_calls": sum(b["total_calls"] for _, b in heldout),
        "rows": rows,
        "model_calls": 0,
        "claim_limit": "New keyed synthetic geometry with alternating displacement only; no developmental cognitive claims.",
    }


if __name__ == "__main__":
    result = run()
    assert result == run()
    print(json.dumps(result, sort_keys=True, indent=2))
