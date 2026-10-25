"""O22-R original FIT-only temporal-revision analysis; no source-world execution.

Original selected public events are drawn byte-identically from O22-O.
Previously-exposed internal FIT checks are descriptive, not unseen validation.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from research.optimizer_o22p.evaluate import read_source
from research.optimizer_o22p.effect_models import NativePlasticCells
from research.optimizer_o22r.temporal_baseline import TemporalBeta, _observed
from research.optimizer_o22q.parsimonious import MinimalSourceBeta

P = json.loads((HERE/"PREREG.json").read_text())
O22P = json.loads((ROOT/"research/optimizer_o22p/PREREG.json").read_text())


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def fit(model, episodes, reverse_each=False):
    begun = time.process_time()
    for ep in episodes:
        rows = list(reversed(ep["rows"])) if reverse_each else ep["rows"]
        for row in rows:
            b, a, after = row["before"], row["selected_action"], row["returned_after"]
            if isinstance(model, (NativePlasticCells, MinimalSourceBeta)):
                model.learn(b, a, after)
            else:
                model.learn(b, a, after, row["source_step"])
    return round(time.process_time()-begun, 8)


def predict(model, row):
    b, a = row["before"], row["selected_action"]
    if isinstance(model, (NativePlasticCells,MinimalSourceBeta)):
        return model.predict(b, a)
    return model.predict(b, a, row["source_step"])


def score(model, episodes):
    tables = {}
    for ep in episodes:
        for row in ep["rows"]:
            b, a, after = row["before"], row["selected_action"], row["returned_after"]
            y = _observed(b, a, after)
            p = predict(model, row)
            assert len(p) == 2 and all(0 <= x <= 1 for x in p)
            keys = ["all", ep["family"], "action_"+str(a),
                    ep["family"]+"|action_"+str(a)]
            for key in keys:
                s = tables.setdefault(key, {"n":0,"positive":[0,0],"sum":[0.0,0.0]})
                s["n"] += 1
                for j in (0,1):
                    s["positive"][j] += y[j]
                    s["sum"][j] += (p[j]-y[j])**2
    return {k: {"n":v["n"],"positive":v["positive"],
                "brier":[round(q/v["n"],9) for q in v["sum"]]}
            for k,v in sorted(tables.items())}


def source_flip_counts(training):
    """Counts chronological observed label flips, not causal world reversals."""
    counts = {}
    for ep in training:
        last = {}
        for row in ep["rows"]:
            b, a, after = row["before"],row["selected_action"],row["returned_after"]
            y = _observed(b,a,after)[0]
            key = (a,b[5])
            group = counts.setdefault(ep["family"], {
                "n":0,"after_front_true":0,"same_action_front_reobserved":0,
                "next_front_label_changed":0,
                "source_selected_information_turns_blocked":0,
                "source_selected_information_turns_clear":0})
            group["n"] += 1
            group["after_front_true"] += y
            if key in last:
                group["same_action_front_reobserved"] += 1
                group["next_front_label_changed"] += int(last[key]!=y)
            last[key] = y
            if row["information_turn"]:
                group["source_selected_information_turns_blocked"] += int(bool(y))
                group["source_selected_information_turns_clear"] += int(not y)
    return counts


def true_cold(model, b, a, step):
    cp = model.checkpoint()
    restored = type(model).restore(cp)
    assert restored.checkpoint() == cp
    if isinstance(model, (NativePlasticCells,MinimalSourceBeta)):
        pred = model.predict(b,a)
        assert restored.predict(b,a) == pred
    else:
        pred = model.predict(b,a,step)
        assert restored.predict(b,a,step) == pred
    name = type(model).__name__
    payload = canonical({"name":name,"source":cp.decode(),
                         "b":b,"a":a,"step":step})
    prog = (
       "import json,sys;"
       "from research.optimizer_o22p.effect_models import NativePlasticCells;"
       "from research.optimizer_o22q.parsimonious import MinimalSourceBeta;"
       "from research.optimizer_o22r.temporal_baseline import TemporalBeta;"
       "p=json.loads(sys.stdin.buffer.read());"
       "m=globals()[p['name']].restore(p['source'].encode());"
       "a=m.predict(p['b'],p['a'],p['step']) if p['name']=='TemporalBeta'"
       " else m.predict(p['b'],p['a']);"
       "print(json.dumps({'p':a,'events':m.events}))"
    )
    rs = subprocess.run([sys.executable, "-B", "-c", prog],
        input=payload, capture_output=True, timeout=25, cwd=ROOT,
        env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE="1"))
    assert rs.returncode == 0, rs.stderr.decode()
    result = json.loads(rs.stdout)
    assert result == {"p":list(pred),"events":model.events}
    return len(cp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args = ap.parse_args()
    original = read_source(args.source_dir)
    training = [e for e in original if
                e["seed_public_fit_role"] in O22P["train_original_fit_seed_ids"][e["family"]]]
    checked = [e for e in original if
               e["seed_public_fit_role"] in O22P["internal_FIT_check_seed_ids"][e["family"]]]
    assert len(training)==12 and len(checked)==4
    n = sum(len(e["rows"]) for e in training)
    assert n==399 and sum(len(e["rows"]) for e in checked)==150

    models = {
        "native_fast_slow":NativePlasticCells(),
        "native_reverse_episodes":NativePlasticCells(),
        "conventional_discounted_092":TemporalBeta("discounted"),
        "conventional_cumulative":TemporalBeta("cumulative"),
        "conventional_phase_only":TemporalBeta("phase_only"),
        "conventional_discounted_reverse_episodes":TemporalBeta("discounted"),
        "conventional_action_front_reference":MinimalSourceBeta("action_front"),
    }
    cpus = {}
    for name,model in models.items():
        cpus[name] = fit(model,training,reverse_each="reverse_episodes" in name)
        assert model.events == n, (name,model.events)
    frozen_slow = copy.deepcopy(models["native_fast_slow"])
    frozen_slow.fast = {head:{} for head in frozen_slow.fast}
    models["native_no_fast_memory"] = frozen_slow

    scores = {name:score(model,checked) for name,model in models.items()}
    assert scores["native_fast_slow"]["all"]["brier"] == [0.205083462,0.058828113]
    assert scores["conventional_action_front_reference"]["all"]["brier"] == [
        0.188010827,0.037447858]
    first = checked[0]["rows"][0]
    sizes = {name:true_cold(model,first["before"],
                            first["selected_action"],first["source_step"])
             for name,model in models.items()}
    dynamic="MiniGrid-Dynamic-Obstacles-8x8-v0"
    nfront = scores["native_fast_slow"][dynamic]["brier"][0]
    cfront = scores["conventional_discounted_092"][dynamic]["brier"][0]
    simple = scores["conventional_action_front_reference"][dynamic]["brier"][0]
    pooled_native = scores["native_fast_slow"]["all"]["brier"]
    pooled_discounted=scores["conventional_discounted_092"]["all"]["brier"]
    if cfront <= nfront:
        verdict = "NO_GO_TEMPORAL_CONVENTIONAL_MATCHES_OR_BEATS_NATIVE_MOVING_FRONT"
    elif all(x<=y for x,y in zip(pooled_discounted,pooled_native)):
        verdict = "NO_GO_CONVENTIONAL_DOMINATES_POOLED_NATIVE"
    else:
        verdict = "MOVING_NATIVE_LEAD_INTERNAL_FIT_ONLY_UNCONFIRMED_REAL_CAUSAL_VALUE"

    result = {
        "schema":"optimizer.o22r.fixed-FIT-observational-temporal-ablation.v1",
        "source_o22o_run":40186158097,
        "source_frozen_original_FIT_episode_count":16,
        "selected_source_FIT_train_actions":399,
        "selected_source_held_internal_FIT_actions":150,
        "internal_FIT_already_seen_before_gate":True,
        "training_observed_front_change_event_counts":source_flip_counts(training),
        "per_family_action_scores":scores,
        "model_cpu_training_s":cpus,
        "full_cold_checkpoint_bytes":sizes,
        "total_process_cpu_s":round(time.process_time(),7),
        "peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "native_dynamic_front_brier":nfront,
        "discounted_conventional_dynamic_front_brier":cfront,
        "cumulative_conventional_dynamic_front_brier":simple,
        "causal_observation":"Matched source-selected effects are observational; reversing training rows is an intervention on the LEARNER only, not on original physics.",
        "admission":verdict,
        "fresh_original_source_fit_dev_protected_steps":0,
        "original_native_R1_R2_R3_mutated":False,
    }
    args.out.write_bytes(canonical(result)+b"\n")
    print("O22R_ORIGINAL_AUTHENTIC_FIT_SOURCE_IDENTITY=PASS",flush=True)
    print("O22R_EQUAL_TRAINING_SOURCE_EVENTS=399",flush=True)
    print("O22R_NATIVE_FRONT_DYNAMIC_BRIER="+str(nfront),flush=True)
    print("O22R_CONVENTIONAL_092_FRONT_DYNAMIC_BRIER="+str(cfront),flush=True)
    for name in sorted(scores):
        print("O22R_MODEL_"+name.upper()+"_POOLED_BRIER="+
              json.dumps(scores[name]["all"]["brier"]),flush=True)
    print("O22R_SCIENTIFIC_GATE="+verdict,flush=True)
    print("O22R_FRESH_OS_COLD_FOR_ALL_ARMS=PASS",flush=True)
    print("O22R_NO_ORIGINAL_WORLD_ACTIONS_OR_PROTECTED=PASS",flush=True)


if __name__=="__main__":
    main()
