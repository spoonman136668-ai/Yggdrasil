"""Y036: falsify fixed cue-parity repair against hidden SHA256 subgroup drift."""
import hashlib
import importlib.util
import json
from collections import OrderedDict
from pathlib import Path

PREVIOUS = Path(__file__).resolve().parent.parent / "20261013-y035-heterogeneous" / "execute.py"
spec = importlib.util.spec_from_file_location("y035_frozen", PREVIOUS)
assert spec and spec.loader
y35 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(y35)
y33 = y35.y33
ARMS = y35.ARMS


def hidden_group(seed, key):
    data = hashlib.sha256(("Y036/" + str(seed) + "/" + str(key)).encode("utf-8")).digest()
    return data[0] % 2


def label(seed, key, episode, condition):
    original = y33.target(seed, key, 0, "STABLE")
    if condition == "HIDDEN_SWITCH" and episode >= 6:
        return (original + (1 if hidden_group(seed, key) == 0 else 2)) % 4
    return original


def cohort_fingerprint(seed):
    activity = [y33.active_keys(seed, e) for e in range(12)]
    groups = [hidden_group(seed, key) for key in range(16)]
    canonical = json.dumps({"activity":activity,"groups":groups}, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def evaluate(seed, condition, arm):
    live = {}
    dormant = OrderedDict()
    seen = set()
    episodes = []
    for episode in range(12):
        active = y33.active_keys(seed, episode)
        guesses = {
            key: live[key] if key in live else dormant.get(key, 0)
            for key in active
        }
        # No unseen target is provided to the policy prior to predictions.
        observed = {key: label(seed, key, episode, condition) for key in active}
        old_live = [key for key in active if key in live]
        deltas = [(key,(observed[key]-live[key])%4) for key in old_live]
        unique = {delta for key,delta in deltas}
        correction = next(iter(unique)) if len(unique)==1 and 0 not in unique else 0
        evidence_parity = {key % 2 for key,delta in deltas}
        returning = [key for key in active if key in seen and key not in live]
        correct = sum(guesses[key] == observed[key] for key in active)
        dorm_correct = sum(guesses[key] == observed[key] for key in returning)
        for key in active:
            dormant.pop(key, None)
        writes = 0
        for key in sorted(set(live).difference(active)):
            dormant.pop(key, None)
            dormant[key] = live[key]
            writes += 1
            while len(dormant)>9:
                dormant.popitem(last=False)
        edits = 0
        if arm != "baseline" and correction:
            for key in tuple(dormant):
                if arm == "global_correction" or key % 2 in evidence_parity:
                    dormant[key] = (dormant[key]+correction)%4
                    edits += 1
        live = observed
        seen.update(active)
        assert len(live)==7 and len(dormant)<=9
        assert len(live)+len(dormant)<=16
        assert not set(live).intersection(dormant)
        episodes.append({
            "episode": episode, "correct": correct,
            "returning": len(returning), "returning_correct": dorm_correct,
            "writes": writes, "dormant_entries": len(dormant),
            "maintenance": edits, "overlap": len(old_live),
            "feedback_delta": correction,
        })
    return {
        "seed": seed, "condition": condition, "arm": arm,
        "cohort": "development" if seed < 92 else "heldout",
        "total_correct": sum(e["correct"] for e in episodes),
        "post_correct": sum(e["correct"] for e in episodes[7:]),
        "post_dormant_correct": sum(e["returning_correct"] for e in episodes[7:]),
        "writes": sum(e["writes"] for e in episodes),
        "maintenance": sum(e["maintenance"] for e in episodes),
        "episodes": episodes,
    }


def run():
    fingerprints = {str(seed): cohort_fingerprint(seed) for seed in range(88,96)}
    assert len(set(fingerprints.values())) == 8
    rows = []
    for condition in ("STABLE","HIDDEN_SWITCH"):
        for seed in range(88,96):
            group = [evaluate(seed,condition,arm) for arm in ARMS]
            assert len({r["writes"] for r in group}) == 1
            assert len({tuple(e["dormant_entries"] for e in r["episodes"])
                        for r in group}) == 1
            assert len({tuple(e["writes"] for e in r["episodes"])
                        for r in group}) == 1
            rows.extend(group)
    def agg(condition, arm, metric):
        return sum(r[metric] for r in rows if r["seed"]>=92
                   and r["condition"]==condition and r["arm"]==arm)
    stable = {arm:agg("STABLE",arm,"total_correct") for arm in ARMS}
    post = {arm:agg("HIDDEN_SWITCH",arm,"post_correct") for arm in ARMS}
    maintenance = {arm:agg("HIDDEN_SWITCH",arm,"maintenance") for arm in ARMS}
    mismatches = {}
    for seed in range(92,96):
        mismatches[str(seed)] = sum(hidden_group(seed,key) != key%2 for key in range(16))
    if (post["grouped_correction"]>post["baseline"]
            and post["grouped_correction"]>post["global_correction"]
            and len(set(stable.values()))==1):
        classification="PARITY_GENERALIZES"
    elif min(post["global_correction"],post["grouped_correction"]) < post["baseline"]:
        classification="FALSE_GROUP_PRIOR"
    else:
        classification="OTHERWISE_MIXED"
    return {
        "schema":"yggdrasil.y036-hidden-subgroup-repair.v1",
        "predecessor_head":"6afdac319b0b1f2dfddcea2baa84c2ca7472234c",
        "classification":classification,
        "heldout_stable_correct":stable,
        "heldout_hidden_post_correct":post,
        "heldout_maintenance_updates":maintenance,
        "heldout_true_group_vs_parity_mismatches":mismatches,
        "unique_fingerprints":True,
        "rows":rows,"model_calls":0,
        "claim_limit":"Synthetic hidden-vs-visible group mismatch, not general semantic structure learning.",
    }


if __name__=="__main__":
    result=run()
    assert result==run()
    print(json.dumps(result,sort_keys=True,indent=2))
