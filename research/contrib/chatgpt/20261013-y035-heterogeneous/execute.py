"""Y035: heterogeneous value-change falsification with parity-scoped feedback."""
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PREVIOUS = Path(__file__).resolve().parent.parent / "20261013-y033-associative-recall" / "execute.py"
_spec = importlib.util.spec_from_file_location("y033_frozen", PREVIOUS)
assert _spec and _spec.loader
y33 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(y33)

ARMS = ("baseline", "global_correction", "grouped_correction")
CONDITIONS = ("STABLE", "MIXED_SWITCH")


def value(seed, key, episode, condition):
    initial = y33.target(seed, key, 0, "STABLE")
    if condition == "MIXED_SWITCH" and episode >= 6:
        return (initial + (1 if key % 2 == 0 else 2)) % 4
    return initial


def evaluate(seed, condition, arm):
    live = {}
    dormant = OrderedDict()
    seen = set()
    episodes = []
    for episode in range(12):
        active = y33.active_keys(seed, episode)
        prediction = {}
        for key in active:
            prediction[key] = live[key] if key in live else dormant.get(key, 0)
        # Evaluator reveals labels only once all guesses are committed.
        truth = {key: value(seed, key, episode, condition) for key in active}
        previously_live = [key for key in active if key in live]
        observed_deltas = [(key, (truth[key] - live[key]) % 4) for key in previously_live]
        correction = 0
        active_correction_parities = set()
        if observed_deltas:
            distinct = {delta for key, delta in observed_deltas}
            if len(distinct) == 1 and 0 not in distinct:
                correction = next(iter(distinct))
                active_correction_parities = {key % 2 for key, delta in observed_deltas}
        returning = [key for key in active if key in seen and key not in live]
        correct = sum(prediction[key] == truth[key] for key in active)
        dormant_correct = sum(prediction[key] == truth[key] for key in returning)
        for key in active:
            dormant.pop(key, None)
        writes = 0
        for key in sorted(set(live).difference(active)):
            dormant.pop(key, None)
            dormant[key] = live[key]
            writes += 1
            while len(dormant) > 9:
                dormant.popitem(last=False)
        maintenance = 0
        if arm != "baseline" and correction:
            for key in tuple(dormant):
                if arm == "global_correction" or key % 2 in active_correction_parities:
                    dormant[key] = (dormant[key] + correction) % 4
                    maintenance += 1
        live = truth
        seen.update(active)
        assert len(live) == 7 and len(dormant) <= 9
        assert len(live) + len(dormant) <= 16
        assert not set(live).intersection(dormant)
        episodes.append({
            "episode": episode, "correct": correct,
            "returning": len(returning), "returning_correct": dormant_correct,
            "overlap": len(previously_live), "feedback_delta": correction,
            "maintenance": maintenance, "writes": writes, "dormant_size": len(dormant)
        })
    return {
        "seed": seed, "condition": condition, "arm": arm,
        "cohort": "development" if seed < 84 else "heldout",
        "total_correct": sum(r["correct"] for r in episodes),
        "post_correct": sum(r["correct"] for r in episodes[7:]),
        "post_dormant_correct": sum(r["returning_correct"] for r in episodes[7:]),
        "writes": sum(r["writes"] for r in episodes),
        "maintenance": sum(r["maintenance"] for r in episodes),
        "episodes": episodes,
    }


def run():
    fingerprints = {str(seed): y33.signature(seed) for seed in range(80, 88)}
    assert len(set(fingerprints.values())) == 8
    rows = []
    for condition in CONDITIONS:
        for seed in range(80, 88):
            group = [evaluate(seed, condition, arm) for arm in ARMS]
            assert len({r["writes"] for r in group}) == 1
            assert len({
                tuple(e["dormant_size"] for e in r["episodes"]) for r in group
            }) == 1
            assert len({
                tuple(e["writes"] for e in r["episodes"]) for r in group
            }) == 1
            rows.extend(group)
    def aggregate(condition, arm, metric):
        return sum(r[metric] for r in rows
                   if r["seed"] >= 84 and r["condition"] == condition
                   and r["arm"] == arm)
    stable = {arm: aggregate("STABLE", arm, "total_correct") for arm in ARMS}
    post = {arm: aggregate("MIXED_SWITCH", arm, "post_correct") for arm in ARMS}
    costs = {arm: aggregate("MIXED_SWITCH", arm, "maintenance") for arm in ARMS}
    if (post["grouped_correction"] > post["global_correction"]
            and post["grouped_correction"] > post["baseline"]
            and len(set(stable.values())) == 1):
        classification = "GROUPED_MORE_ROBUST"
    elif post["global_correction"] < post["baseline"]:
        classification = "HETEROGENEOUS_HARM"
    else:
        classification = "MIXED_OR_NEGATIVE"
    return {
        "schema": "yggdrasil.y035-heterogeneous-associative-repair.v1",
        "predecessor_head": "08ab3be3bd28516b094084cc5722bf16876af7de",
        "classification": classification,
        "unique_fingerprints": True, "fingerprints": fingerprints,
        "heldout_stable_total": stable,
        "heldout_mixed_post_correct": post,
        "heldout_mixed_maintenance_updates": costs,
        "rows": rows, "model_calls": 0,
        "claim_limit": "Synthetic cue-parity-conditioned repair with fully predeclared grouping.",
    }


if __name__ == "__main__":
    outcome = run()
    assert outcome == run()
    print(json.dumps(outcome, sort_keys=True, indent=2))
