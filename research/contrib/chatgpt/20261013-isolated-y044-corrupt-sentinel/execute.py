"""Y044: corroborating early cue reports prevents contaminated cache correction."""
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

CONDITIONS = ("CLEAN_REPORT", "ONE_BAD_MAJOR_REPORT")
ARMS = ("NO_SENTINEL", "TWO_GROUP_SENTINELS", "THREE_CONSISTENCY")


def core_groups(seed):
    assert 152 <= seed <= 159
    core = y40.active(seed, 10)
    even = [key for key in core if key % 2 == 0]
    odd = [key for key in core if key % 2 == 1]
    if not even or not odd:
        return None
    return (even, odd) if len(even) > len(odd) else (odd, even)


def truth(seed, key, ep):
    original = y40.target(seed, key, 0, "STABLE")
    # No changing labels for currently active DISTRACTOR cues, even from ep6.
    if ep < 6 or key not in y40.permutation(seed)[:7]:
        return original
    return (original + 2) % 4


def fingerprint(seed):
    value = {
        "cue_permutation": y40.permutation(seed),
        "initial": [truth(seed, key, 0) for key in range(16)],
    }
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def evaluate(seed, condition, arm):
    assert condition in CONDITIONS and arm in ARMS
    major, minor = core_groups(seed)
    live = {}
    dormant = OrderedDict()
    pre_feedback = hashlib.sha256()
    rows = []
    for episode in range(12):
        keys = y40.active(seed, episode)
        reports = {}
        remaining = list(keys)
        if episode == 10 and arm != "NO_SENTINEL":
            selected = ([major[0], minor[0]] if arm == "TWO_GROUP_SENTINELS"
                        else [major[0], major[1], minor[0]])
            assert all(key in dormant for key in selected)
            # Only these designated early REPORTS, potentially noisy,
            # become visible to the policy before other forecasts.
            reports = {key: truth(seed, key, episode) for key in selected}
            if condition == "ONE_BAD_MAJOR_REPORT":
                reports[major[0]] = (reports[major[0]] + 1) % 4
            remaining = [key for key in keys if key not in reports]
        major_deltas = [(reports[key]-dormant[key])%4
                        for key in major if key in reports]
        minor_deltas = [(reports[key]-dormant[key])%4
                        for key in minor if key in reports]
        assert (not reports or
                (len(minor_deltas)==1 and len(major_deltas) ==
                 (1 if arm=="TWO_GROUP_SENTINELS" else 2)))
        majority_conflict = len(major_deltas)==2 and len(set(major_deltas))>1
        guesses = {}
        for key in remaining:
            remembered = live[key] if key in live else dormant.get(key,0)
            if not reports:
                guess=remembered
            elif key in major and majority_conflict:
                guess=None  # bounded abstention when witnesses conflict
            else:
                shift = major_deltas[0] if key in major else minor_deltas[0]
                guess=(remembered+shift)%4
            guesses[key]=guess
        assert set(guesses).isdisjoint(reports)
        assert len(guesses)+len(reports)==7
        # The evaluator now reveals all authoritative true labels.
        authoritative = {key: truth(seed,key,episode) for key in keys}
        correct=sum(guesses[key]==authoritative[key] for key in remaining)
        abstained=sum(guesses[key] is None for key in remaining)
        wrong=len(remaining)-correct-abstained
        if episode <= 9:
            pre_feedback.update(bytes((episode,)) + bytes(
                item for key in keys for item in (key,authoritative[key])))
        for key in keys:
            dormant.pop(key,None)
        writes=0
        for key in sorted(set(live).difference(keys)):
            dormant.pop(key,None)
            dormant[key]=live[key]
            writes+=1
            while len(dormant)>9:
                dormant.popitem(last=False)
        live=authoritative
        assert len(live)==7 and len(dormant)<=9
        assert len(live)+len(dormant)<=16
        assert not set(live).intersection(dormant)
        rows.append({
            "episode":episode,
            "reports":len(reports),
            "scored_opportunities":len(remaining),
            "correct":correct,"wrong":wrong,"abstained":abstained,
            "predicted":len(remaining)-abstained,
            "majority_report_conflict":majority_conflict,
            "cache_writes":writes,"cache_size":len(dormant),
        })
    return {
        "seed":seed,"cohort":"development" if seed<156 else "heldout",
        "condition":condition,"arm":arm,
        "pre_reactivation_feedback_sha256":pre_feedback.hexdigest(),
        "first_return":rows[10],
        "next_episode":rows[11],
        "total_writes":sum(r["cache_writes"] for r in rows),
        "episodes":rows,
    }


def run():
    groups={str(seed):core_groups(seed) for seed in range(152,160)}
    signatures={str(seed):fingerprint(seed) for seed in range(152,160)}
    if any(group is None for group in groups.values()):
        return {
            "schema":"yggdrasil.y044-sentinel-corroboration.v1",
            "classification":"INSUFFICIENT_MINOR_GROUP",
            "groups":groups,"fingerprints":signatures,"rows":[],
            "model_calls":0,
        }
    if len(set(signatures.values()))!=8:
        return {
            "schema":"yggdrasil.y044-sentinel-corroboration.v1",
            "classification":"NONUNIQUE_FINGERPRINT",
            "groups":groups,"fingerprints":signatures,"rows":[],
            "model_calls":0,
        }
    rows=[evaluate(seed,cond,arm)
          for seed in range(152,160)
          for cond in CONDITIONS for arm in ARMS]
    lookup={(r["seed"],r["condition"],r["arm"]):r for r in rows}
    indistinguishable=True
    for seed in range(152,160):
        a=lookup[seed,"CLEAN_REPORT","NO_SENTINEL"]
        b=lookup[seed,"ONE_BAD_MAJOR_REPORT","NO_SENTINEL"]
        indistinguishable &= (a["pre_reactivation_feedback_sha256"] ==
                               b["pre_reactivation_feedback_sha256"])
        for cond in CONDITIONS:
            items=[lookup[seed,cond,arm] for arm in ARMS]
            write_lists=[[e["cache_writes"] for e in r["episodes"]]
                         for r in items]
            occupancy_lists=[[e["cache_size"] for e in r["episodes"]]
                             for r in items]
            assert write_lists[0]==write_lists[1]==write_lists[2]
            assert occupancy_lists[0]==occupancy_lists[1]==occupancy_lists[2]
            assert all(r["next_episode"]["correct"]==7 for r in items)
    held=[r for r in rows if r["seed"]>=156]
    stats={cond:{arm:{
        metric:sum(r["first_return"][metric] for r in held
                   if r["condition"]==cond and r["arm"]==arm)
        for metric in ("reports","scored_opportunities","correct","wrong",
                       "abstained","predicted","majority_report_conflict")}
        for arm in ARMS} for cond in CONDITIONS}
    good=stats["CLEAN_REPORT"]["THREE_CONSISTENCY"]
    bad_two=stats["ONE_BAD_MAJOR_REPORT"]["TWO_GROUP_SENTINELS"]
    bad_three=stats["ONE_BAD_MAJOR_REPORT"]["THREE_CONSISTENCY"]
    if not indistinguishable:
        classification="INVALID_HIDDEN_HISTORY"
    elif (good["correct"]==16 and good["abstained"]==0
          and bad_two["wrong"]>=1 and bad_three["wrong"]==0
          and bad_three["abstained"]>=1):
        classification="CORRUPTION_CONTAINMENT"
    else:
        classification="NO_GAIN"
    return {
        "schema":"yggdrasil.y044-sentinel-corroboration.v1",
        "parent":"cff687e5ad517df553a3e57787bf8a02dabd9628",
        "classification":classification,
        "unique_fingerprints":True,"fingerprints":signatures,
        "majority_minority_groups":groups,
        "pre_reactivation_observational_equivalence":bool(indistinguishable),
        "heldout":stats,"rows":rows,"model_calls":0,
        "claim_limit":"A fixed 2-group synthetic sensor corruption with explicit additional witness budget; abstentions sacrifice coverage.",
    }


if __name__=="__main__":
    original=run()
    assert original==run()
    print(json.dumps(original,sort_keys=True,indent=2))
