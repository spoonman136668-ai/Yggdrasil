"""Y043: explicit sentinel feedback restores dormant competence under known shift structure."""
import hashlib
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PREVIOUS = Path(__file__).resolve().parent.parent / "20261013-y040-hibernation" / "execute.py"
_spec = importlib.util.spec_from_file_location("y040_frozen", PREVIOUS)
assert _spec and _spec.loader
y40 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y40)

CONDITIONS = ("STABLE", "UNIFORM_SHIFT", "PARITY_SHIFT")
ARMS = ("NO_SENTINEL", "ONE_SENTINEL", "TWO_PARITY_SENTINELS")


def value(seed, key, episode, condition):
    assert condition in CONDITIONS and 144 <= seed <= 151
    initial = y40.target(seed, key, 0, "STABLE")
    if episode < 6 or condition == "STABLE":
        return initial
    # Only dormant CORE changes; distractor feedback through episode 9
    # remains identical across all paired hidden-world conditions.
    if key not in y40.permutation(seed)[:7]:
        return initial
    if condition == "UNIFORM_SHIFT":
        return (initial + 2) % 4
    return (initial + (2 if key % 2 == 0 else 1)) % 4


def fingerprint(seed):
    source = {
        "order": y40.permutation(seed),
        "targets_at_zero": [value(seed, key, 0, "STABLE") for key in range(16)],
    }
    return hashlib.sha256(
        json.dumps(source, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def parity_support(seed):
    core = y40.active(seed, 10)
    return bool([k for k in core if k % 2 == 0]) and bool(
        [k for k in core if k % 2 == 1])


def evaluate(seed, condition, arm):
    live = {}
    dormant = OrderedDict()
    feedback_trace = hashlib.sha256()
    episodes = []
    for episode in range(12):
        active = y40.active(seed, episode)
        assert len(active) == len(set(active)) == 7
        early_observed = {}
        remaining = list(active)
        if episode == 10 and arm != "NO_SENTINEL":
            if arm == "ONE_SENTINEL":
                sampled = [active[0]]
            else:
                evens = [key for key in active if key % 2 == 0]
                odds = [key for key in active if key % 2 == 1]
                assert evens and odds
                sampled = [evens[0], odds[0]]
            assert len(sampled) == (1 if arm == "ONE_SENTINEL" else 2)
            assert all(key in dormant for key in sampled)
            # ONLY these observed labels are revealed before the predictions
            # of the remaining six/five keys.
            for key in sampled:
                early_observed[key] = value(seed, key, episode, condition)
            remaining = [key for key in active if key not in early_observed]
        corrections = {}
        if early_observed:
            if arm == "ONE_SENTINEL":
                key = next(iter(early_observed))
                corrections["all"] = (early_observed[key] - dormant[key]) % 4
            else:
                for key, observed in early_observed.items():
                    corrections[str(key % 2)] = (observed - dormant[key]) % 4
        guesses = {}
        for key in remaining:
            if key in live:
                previous = live[key]
            else:
                previous = dormant.get(key, 0)
            if early_observed:
                assert key in dormant
                correction = (corrections["all"] if arm == "ONE_SENTINEL"
                              else corrections[str(key % 2)])
                guesses[key] = (previous + correction) % 4
            else:
                guesses[key] = previous
        assert len(guesses) + len(early_observed) == 7
        assert not set(guesses).intersection(early_observed)
        # Now and only now evaluator reveals remaining ground truth.
        revealed = dict(early_observed)
        for key in remaining:
            revealed[key] = value(seed, key, episode, condition)
        correct = sum(guesses[key] == revealed[key] for key in remaining)
        wrong = len(remaining) - correct
        if episode <= 9:
            feedback_trace.update(bytes((episode,)) + bytes(
                part for key in active for part in (key, revealed[key])))
        for key in active:
            dormant.pop(key, None)
        writes = 0
        for key in sorted(set(live).difference(active)):
            dormant.pop(key, None)
            dormant[key] = live[key]
            writes += 1
            while len(dormant) > 9:
                dormant.popitem(last=False)
        live = revealed
        assert len(live) == 7 and len(dormant) <= 9
        assert len(live) + len(dormant) <= 16
        assert not set(live).intersection(dormant)
        episodes.append({
            "episode": episode,
            "early_feedback_count": len(early_observed),
            "early_feedback_keys": sorted(early_observed),
            "scored_predictions": len(remaining),
            "correct": correct, "wrong": wrong,
            "cache_writes": writes, "cache_size": len(dormant),
            "corrections_inferred": corrections,
        })
    return {
        "seed": seed, "cohort": "development" if seed < 148 else "heldout",
        "condition": condition, "arm": arm,
        "pre_reactivation_feedback_sha256": feedback_trace.hexdigest(),
        "reactivation": episodes[10],
        "relearn": episodes[11],
        "total_cache_writes": sum(r["cache_writes"] for r in episodes),
        "episodes": episodes,
    }


def run():
    signatures = {str(seed): fingerprint(seed) for seed in range(144, 152)}
    support = {str(seed): parity_support(seed) for seed in range(144, 152)}
    if len(set(signatures.values())) < 8 or not all(support.values()):
        return {
            "schema": "yggdrasil.y043-core-only-sentinel-observed-repair.v1",
            "classification": ("NONUNIQUE_FINGERPRINT" if
                               len(set(signatures.values())) < 8 else
                               "INSUFFICIENT_PARITY_SUPPORT"),
            "fingerprints": signatures,
            "parity_support": support,
            "rows": [], "model_calls": 0,
        }
    rows = [evaluate(seed, condition, arm)
            for seed in range(144, 152)
            for condition in CONDITIONS for arm in ARMS]
    lookup = {(r["seed"], r["condition"], r["arm"]): r for r in rows}
    equivalent = True
    for seed in range(144, 152):
        histories = [lookup[seed, c, "NO_SENTINEL"][
            "pre_reactivation_feedback_sha256"] for c in CONDITIONS]
        equivalent = equivalent and len(set(histories)) == 1
        for condition in CONDITIONS:
            three = [lookup[seed, condition, arm] for arm in ARMS]
            writes = [[e["cache_writes"] for e in r["episodes"]] for r in three]
            occupancy = [[e["cache_size"] for e in r["episodes"]] for r in three]
            assert writes[0] == writes[1] == writes[2]
            assert occupancy[0] == occupancy[1] == occupancy[2]
            assert all(r["relearn"]["correct"] == 7 for r in three)
    heldout = [r for r in rows if r["seed"] >= 148]
    scores = {condition: {arm: {
        "e10_correct": sum(r["reactivation"]["correct"] for r in heldout
                           if r["condition"] == condition and r["arm"] == arm),
        "e10_wrong": sum(r["reactivation"]["wrong"] for r in heldout
                         if r["condition"] == condition and r["arm"] == arm),
        "e10_scored_predictions": sum(
            r["reactivation"]["scored_predictions"] for r in heldout
            if r["condition"] == condition and r["arm"] == arm),
        "e10_early_feedback_labels": sum(
            r["reactivation"]["early_feedback_count"] for r in heldout
            if r["condition"] == condition and r["arm"] == arm),
        "e11_correct": sum(r["relearn"]["correct"] for r in heldout
                           if r["condition"] == condition and r["arm"] == arm),
    } for arm in ARMS} for condition in CONDITIONS}
    uniform_one = scores["UNIFORM_SHIFT"]["ONE_SENTINEL"]
    parity_one = scores["PARITY_SHIFT"]["ONE_SENTINEL"]
    parity_two = scores["PARITY_SHIFT"]["TWO_PARITY_SENTINELS"]
    if not equivalent:
        result = "INVALID_WORLD_EQUIVALENCE"
    elif (uniform_one["e10_correct"] == 24
            and parity_two["e10_correct"] == 20 and
            parity_one["e10_wrong"] >= 1):
        result = "SENTINEL_CORE_ONLY_TRANSFER"
    else:
        result = "PARTIAL"
    return {
        "schema": "yggdrasil.y043-core-only-sentinel-observed-repair.v1",
        "parent": "2dcb700cb9a531a98fa8fcfeba072f2ff6ea034a",
        "classification": result, "fingerprints": signatures,
        "parity_support": support,
        "pre_reactivation_history_equivalent": equivalent,
        "heldout": scores, "rows": rows, "model_calls": 0,
        "claim_limit": "Samples receive explicit early truth feedback; different label budgets and finite synthetic shift rules.",
    }


if __name__ == "__main__":
    original = run()
    assert original == run()
    print(json.dumps(original, sort_keys=True, indent=2))
