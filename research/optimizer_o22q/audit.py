"""Optimizer O22-Q — preregistered minimalist-source-control check.

No new original environment interaction. All held-out examples belong to
already-exposed O22-P internal FIT and cannot establish independent transfer.
"""
import argparse
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
from research.optimizer_o22p.effect_models import NativePlasticCells, ConventionalBayesianEffects
from research.optimizer_o22q.parsimonious import MinimalSourceBeta, _outcome

P = json.loads((HERE / "PREREG.json").read_text())
MODELS = ("native", "conventional_heading", "action_front", "action", "front")


def canonical(s):
    return json.dumps(s, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def evaluate(episodes, model):
    stats = {}
    for ep in episodes:
        for row in ep["rows"]:
            b, a, aft = row["before"], row["selected_action"], row["returned_after"]
            target = _outcome(b, a, aft)
            p = model.predict(b, a)
            assert len(p) == 2 and all(0 <= v <= 1 for v in p)
            group = (ep["family"], str(a))
            for key in (("all", "all"), (ep["family"], "all"), ("all", str(a)), group):
                t = stats.setdefault("|".join(key), {
                    "n": 0, "positive_next_front": 0, "positive_movement": 0,
                    "brier_total": [0.0, 0.0]
                })
                t["n"] += 1
                t["positive_next_front"] += target[0]
                t["positive_movement"] += target[1]
                for j in (0, 1):
                    t["brier_total"][j] += (p[j] - target[j]) ** 2
    return {name: {"n": v["n"], "next_front_positive": v["positive_next_front"],
                   "translation_positive": v["positive_movement"],
                   "brier": [round(q / v["n"], 9) for q in v["brier_total"]]}
            for name, v in sorted(stats.items())}


def own_cold(model, b, a):
    if not isinstance(model, MinimalSourceBeta):
        # These have a separate true-cold certificate already in O22-P.
        cp = model.checkpoint()
        restored = type(model).restore(cp)
        assert restored.predict(b, a) == model.predict(b, a)
        return len(cp)
    cp = model.checkpoint()
    fresh = MinimalSourceBeta.restore(cp)
    assert fresh.checkpoint() == cp
    program = (
        "import json,sys;"
        "from research.optimizer_o22q.parsimonious import MinimalSourceBeta;"
        "d=json.loads(sys.stdin.buffer.read());"
        "x=MinimalSourceBeta.restore(d['checkpoint'].encode());"
        "print(json.dumps({'p':x.predict(d['before'],d['action']),"
        "'n':x.events,'mode':x.mode}))"
    )
    payload = canonical({"checkpoint": cp.decode(), "before": b, "action": a})
    r = subprocess.run([sys.executable, "-B", "-c", program],
                       input=payload, capture_output=True, timeout=20, cwd=ROOT,
                       env=dict(os.environ, PYTHONPATH=str(ROOT), PYTHONDONTWRITEBYTECODE="1"))
    assert r.returncode == 0, r.stderr.decode()
    out = json.loads(r.stdout)
    assert out == {"p": list(model.predict(b, a)), "n": model.events, "mode": model.mode}
    return len(cp)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    started = time.process_time()
    episodes = read_source(args.source)
    train = [ep for ep in episodes if ep["seed_public_fit_role"] in
             json.loads((ROOT/"research/optimizer_o22p/PREREG.json").read_text())[
                 "train_original_fit_seed_ids"][ep["family"]]]
    internal = [ep for ep in episodes if ep not in train]
    assert len(train) == 12 and len(internal) == 4
    assert sum(len(ep["rows"]) for ep in train) == 399
    assert sum(len(ep["rows"]) for ep in internal) == 150
    models = {
        "native": NativePlasticCells(),
        "conventional_heading": ConventionalBayesianEffects(),
        "action_front": MinimalSourceBeta("action_front"),
        "action": MinimalSourceBeta("action"),
        "front": MinimalSourceBeta("front")
    }
    cpu = {}
    for key in MODELS:
        m = models[key]
        t = time.process_time()
        for ep in train:
            for row in ep["rows"]:
                m.learn(row["before"], row["selected_action"], row["returned_after"])
        cpu[key] = round(time.process_time()-t, 8)
        assert m.events == 399 and m.actions == {
            "0": 100, "1": 71, "2": 228
        }, ("SOURCE_SELECTED_COUNTS_DRIFT", key, m.actions)
    checked = {k: evaluate(internal, models[k]) for k in MODELS}
    # Check previous unchanged O22-P exact reference calculation, independent
    # from this diagnostic and without changing the frozen source split.
    assert checked["native"]["all|all"]["brier"] == [0.205083462, 0.058828113]
    assert checked["conventional_heading"]["all|all"]["brier"] == [
        0.192795451, 0.036809453]
    sample = internal[0]["rows"][0]
    cpbytes = {k: own_cold(models[k], sample["before"], sample["selected_action"])
               for k in MODELS}
    # No post-hoc threshold tuning or subsequent new DEV claim.
    simple = checked["action_front"]["all|all"]["brier"]
    native = checked["native"]["all|all"]["brier"]
    conventional = checked["conventional_heading"]["all|all"]["brier"]
    simpler_better_both = all(x < y for x,y in zip(simple, native))
    if simpler_better_both:
        decision = "NO_GO_SIMPLE_ACTION_FRONT_CONTROL_OUTPERFORMS_NATIVE_BOTH_LABELS"
    else:
        decision = "NO_GO_NATIVE_SUPERIORITY_UNPROVEN_ALREADY_CONVENTIONAL_WINS_POOLED"
    result = {
        "schema": "optimizer.o22q.authentic-internal-FIT-parsimony.v1",
        "source_original_o22o_run": P["old_o22p_authentic_source_run"],
        "source_original_fit_artifact": P["old_o22p_original_FIT_artifact"],
        "old_internal_FIT_150_ALREADY_EXPOSED": True,
        "train_events": 399,
        "internal_check_events": 150,
        "measurements_by_model_family_action": checked,
        "checkpoint_bytes": cpbytes,
        "train_cpu_s_per_model": cpu,
        "process_cpu_s": round(time.process_time() - started, 8),
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "scientific_admission": decision,
        "source_simulator_resets_steps_added": 0,
        "protected_scientific_first_use": False,
        "limits": [
            "Source selected-outcome observational labels, no action causal value.",
            "These are O22P previously used internal FIT examples; no independent DEV.",
            "No new native architecture, hyperparameter tuning or source role drift.",
            "External-world novel transfer and protected FSA first-use remain unproven."
        ]
    }
    args.out.write_bytes(canonical(result) + b"\n")
    print("O22Q_REAL_SOURCE_INTERNAL_FIT_IDENTITIES=PASS", flush=True)
    print("O22Q_ORIGINAL_O22P_PREDICTION_REPRODUCTION=PASS", flush=True)
    for name in MODELS:
        print("O22Q_MODEL_" + name.upper() + "_BRIER=" +
              json.dumps(checked[name]["all|all"]["brier"]), flush=True)
    print("O22Q_SCIENTIFIC_DECISION=" + decision, flush=True)
    print("O22Q_ALL_CONVENTIONAL_COLD_RESTORES=PASS", flush=True)
    print("O22Q_NO_ORIGINAL_WORLD_DEV_OR_PROTECTED_ACTIONS=PASS", flush=True)


if __name__ == "__main__":
    main()
