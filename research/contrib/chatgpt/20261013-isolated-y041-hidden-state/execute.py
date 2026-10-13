"""Y041: paired-world informational limit on hidden hibernation changes."""
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


def policy(seed, condition, mode):
    assert 128 <= seed <= 135
    assert condition in ("STABLE", "HIDDEN_SHIFT")
    assert mode in ("trust", "abstain_on_dormant", "zero_memory")
    capacity = 0 if mode == "zero_memory" else 9
    previous_live = {}
    dormant = OrderedDict()
    feedback_trace = hashlib.sha256()
    episodes = []
    for ep in range(12):
        current = y40.active(seed, ep)
        assert len(current) == len(set(current)) == 7
        forecasts = {}
        provenance = {}
        for key in current:
            if key in previous_live:
                forecasts[key] = previous_live[key]
                provenance[key] = "live"
            elif key in dormant:
                provenance[key] = "dormant"
                forecasts[key] = (None if mode == "abstain_on_dormant"
                                  else dormant[key])
            else:
                provenance[key] = "default"
                forecasts[key] = 0
        # The feedback trace is formed ONLY from the observations received
        # by a policy and never from dormant future labels or hidden change.
        truth = {key: y40.target(seed, key, ep, condition) for key in current}
        if ep <= 9:
            feedback_trace.update(bytes((ep,)) + bytes(
                value for key in current for value in (key, truth[key])))
        correct = sum(forecasts[key] == truth[key] for key in current)
        abstained = sum(forecasts[key] is None for key in current)
        wrong = 7-correct-abstained
        for key in current:
            dormant.pop(key, None)
        writes = 0
        for key in sorted(set(previous_live)-set(current)):
            if capacity == 0:
                continue
            dormant.pop(key, None)
            dormant[key] = previous_live[key]
            writes += 1
            while len(dormant) > capacity:
                dormant.popitem(last=False)
        previous_live = truth
        assert len(previous_live) == 7 and len(dormant) <= capacity
        assert len(previous_live) + len(dormant) <= 16
        assert not set(previous_live).intersection(dormant)
        episodes.append({
            "episode": ep, "correct": correct, "wrong": wrong,
            "abstained": abstained, "predicted": 7-abstained,
            "cache_writes": writes, "cache_size": len(dormant),
            "predictions": [forecasts[key] for key in current] if ep == 10 else None,
            "targets": [truth[key] for key in current] if ep == 10 else None,
            "prediction_origin": [provenance[key] for key in current] if ep == 10 else None,
        })
    return {
        "seed": seed, "condition": condition, "arm": mode,
        "pre_reactivation_observation_sha256": feedback_trace.hexdigest(),
        "reactivation_e10": episodes[10],
        "relearn_e11": episodes[11],
        "total_writes": sum(ep["cache_writes"] for ep in episodes),
        "episodes": episodes,
    }


def run():
    rows = [policy(seed, condition, mode)
            for seed in range(128, 136)
            for condition in ("STABLE", "HIDDEN_SHIFT")
            for mode in ("trust", "abstain_on_dormant", "zero_memory")]
    by = {(r["seed"], r["condition"], r["arm"]): r for r in rows}
    paired_checks = []
    for seed in range(128, 136):
        stable = by[seed, "STABLE", "trust"]
        changed = by[seed, "HIDDEN_SHIFT", "trust"]
        abstain_stable = by[seed, "STABLE", "abstain_on_dormant"]
        abstain_changed = by[seed, "HIDDEN_SHIFT", "abstain_on_dormant"]
        same_history = (stable["pre_reactivation_observation_sha256"] ==
                        changed["pre_reactivation_observation_sha256"])
        same_forecast = (stable["reactivation_e10"]["predictions"] ==
                         changed["reactivation_e10"]["predictions"])
        shifted_truth = all((changed["reactivation_e10"]["targets"][i] -
                             stable["reactivation_e10"]["targets"][i]) % 4 == 2
                            for i in range(7))
        assert stable["total_writes"] == abstain_stable["total_writes"]
        assert changed["total_writes"] == abstain_changed["total_writes"]
        assert [r["cache_size"] for r in stable["episodes"]] == [
            r["cache_size"] for r in abstain_stable["episodes"]]
        paired_checks.append({
            "seed": seed, "same_observed_history": same_history,
            "same_first_return_forecast": same_forecast,
            "changed_targets_plus_two": shifted_truth,
            "paired_trust_correct_sum": stable["reactivation_e10"]["correct"] +
                                        changed["reactivation_e10"]["correct"],
        })
    heldout = [r for r in rows if r["seed"] >= 132]
    def aggregate(condition, arm, ep, metric):
        return sum(r["episodes"][ep][metric] for r in heldout
                   if r["condition"] == condition and r["arm"] == arm)
    stats = {cond: {arm: {
        "e10_correct": aggregate(cond, arm, 10, "correct"),
        "e10_wrong": aggregate(cond, arm, 10, "wrong"),
        "e10_abstentions": aggregate(cond, arm, 10, "abstained"),
        "e10_predictions": aggregate(cond, arm, 10, "predicted"),
        "e11_correct": aggregate(cond, arm, 11, "correct"),
    } for arm in ("trust", "abstain_on_dormant", "zero_memory")}
             for cond in ("STABLE", "HIDDEN_SHIFT")}
    pairs_ok = all(c["same_observed_history"] and
                   c["same_first_return_forecast"] and
                   c["changed_targets_plus_two"] and
                   c["paired_trust_correct_sum"] <= 7 for c in paired_checks)
    stable = stats["STABLE"]
    shifted = stats["HIDDEN_SHIFT"]
    full = (
        pairs_ok and stable["trust"]["e10_correct"] == 28
        and shifted["trust"]["e10_correct"] == 0
        and stable["abstain_on_dormant"]["e10_abstentions"] == 28
        and shifted["abstain_on_dormant"]["e10_abstentions"] == 28
        and stable["abstain_on_dormant"]["e10_wrong"] == 0
        and shifted["abstain_on_dormant"]["e10_wrong"] == 0
        and stable["trust"]["e11_correct"] == 28
        and shifted["trust"]["e11_correct"] == 28
    )
    label = ("UNOBSERVABLE_HIDDEN_CHANGE_BOUNDARY" if full else
             "PARTIAL_BOUNDARY" if pairs_ok else "NEGATIVE")
    return {
        "schema": "yggdrasil.y041-hidden-hibernation-equivalence.v1",
        "parent": "9e98d2d2867a196085aeb0e159b56b9b29d20f75",
        "classification": label, "paired_checks": paired_checks,
        "heldout": stats, "rows": rows, "model_calls": 0,
        "claim_limit": "Synthetic counterfactual paired worlds; abstention sacrifices all first-return coverage.",
    }


if __name__ == "__main__":
    original = run()
    assert original == run()
    print(json.dumps(original, sort_keys=True, indent=2))
