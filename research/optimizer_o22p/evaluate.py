"""O22-P: evaluate two independently fitted models on split ORIGINAL FIT histories.

This program cannot reset/step a source environment or read unrelated DEV.
The held-back records are INTERNAL FIT checks, not unseen science/holdouts.
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
from research.optimizer_o22p.effect_models import (
    NativePlasticCells, ConventionalBayesianEffects, _public
)

P = json.loads((HERE / "PREREG.json").read_text())
EXPECTED = P["source_artifact"]


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def read_source(root):
    files = []
    for name, expected in (("fit-1.json", EXPECTED["fit1_file_sha256"]),
                           ("fit-2.json", EXPECTED["fit2_file_sha256"])):
        blob = (root / name).read_bytes()
        assert hashlib.sha256(blob).hexdigest() == expected, "ORIGINAL_FIT_BLOB_DRIFT"
        data = json.loads(blob)
        assert data["schema"] == "optimizer.o22o.authentic-original-selected-action-fit.v1", "ORIGINAL_SCHEMA"
        assert data["source"] == P["original_upstream"]
        assert data["source_original_motor_fit_rows"] == 12
        assert data["selected_actions"] == {"0": 139, "1": 97, "2": 313}
        assert data["fit_role_only"] is True
        assert data["development_reset_count"] == data["protected_reset_count"] == 0
        files.append(data)
    science_keys = (
        "schema", "source", "original_owner", "protocol_sha256",
        "source_original_motor_fit_sha256", "source_original_motor_fit_rows",
        "source_original_motor_fit_counts", "fit_role_only",
        "development_reset_count", "protected_reset_count", "policy",
        "by_family", "selected_actions", "episodes", "scientific_admission"
    )
    for key in science_keys:
        assert files[0][key] == files[1][key], ("SOURCE_TWO_PROCESS_DIFFER", key)
    episodes = files[0]["episodes"]
    seen = set()
    for e in episodes:
        f, s = e["family"], e["seed_public_fit_role"]
        assert (f, s) not in seen
        seen.add((f, s))
        assert (s in P["train_original_fit_seed_ids"].get(f, []) or
                s in P["internal_FIT_check_seed_ids"].get(f, [])), "SOURCE_ROLE_DRIFT"
        assert e["rows_sha256"] == hashlib.sha256(canonical(e["rows"])).hexdigest()
        assert e["n_selected_actions"] == len(e["rows"]) > 0
        for i, row in enumerate(e["rows"]):
            assert row["source_step"] == i
            _public(row["before"], row["selected_action"], row["returned_after"])
            if i:
                assert row["before"] == e["rows"][i - 1]["returned_after"]
    assert len(episodes) == 16
    expected_roles = {(family, seed) for block in
        ("train_original_fit_seed_ids", "internal_FIT_check_seed_ids")
        for family, seeds in P[block].items() for seed in seeds}
    assert seen == expected_roles
    return episodes


def cold_exact(model, b, action):
    cls = type(model)
    cp = model.checkpoint()
    restored = cls.restore(cp)
    assert restored.checkpoint() == cp
    assert restored.predict(b, action) == model.predict(b, action)
    name = cls.__name__
    program = (
      "import json,sys;"
      "from research.optimizer_o22p.effect_models import "
      "NativePlasticCells,ConventionalBayesianEffects;"
      "w=json.loads(sys.stdin.buffer.read());"
      "m=globals()[w['cls']].restore(w['bytes'].encode());"
      "print(json.dumps({'predict':m.predict(w['before'],w['action']),"
      "'proposal':m.proposal(w['before']),'events':m.events}))"
    )
    wire = canonical({"cls": name, "bytes": cp.decode(),
                      "before": b, "action": action})
    subprocess_env = dict(os.environ, PYTHONPATH=str(ROOT), PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-B", "-c", program], input=wire,
                       capture_output=True, timeout=20, cwd=ROOT, env=subprocess_env)
    assert r.returncode == 0, r.stderr.decode()
    got = json.loads(r.stdout)
    assert got["predict"] == list(model.predict(b, action))
    assert got["proposal"] == model.proposal(b)
    assert got["events"] == model.events
    return len(cp)


def train_rows(episodes, model, swap=False):
    t0 = time.process_time()
    n = 0
    for e in episodes:
        for row in e["rows"]:
            a = row["selected_action"]
            if swap and a in (0, 1):
                a = 1 - a
            model.learn(row["before"], a, row["returned_after"])
            n += 1
    return n, round(time.process_time() - t0, 8)


def scored(episodes, model):
    scores = [0.0, 0.0]
    actions = {"0": 0, "1": 0, "2": 0}
    n = 0
    per_family = {}
    for e in episodes:
        fam = e["family"]
        rec = per_family.setdefault(fam, {"n": 0, "brier_sum": [0.0, 0.0]})
        for row in e["rows"]:
            a = row["selected_action"]
            y = _public(row["before"], a, row["returned_after"])
            p = model.predict(row["before"], a)
            assert len(p) == 2 and all(0 <= v <= 1 for v in p)
            for j in range(2):
                q = (p[j] - y[j]) ** 2
                scores[j] += q
                rec["brier_sum"][j] += q
            actions[str(a)] += 1
            n += 1
            rec["n"] += 1
    assert n > 0
    return {"n_selected_source_actions": n, "by_action": actions,
            "brier": [round(q / n, 9) for q in scores],
            "families": {f: {"n": v["n"],
                       "brier": [round(s / v["n"], 9) for s in v["brier_sum"]]}
                        for f, v in per_family.items()}}


def proposals_on_fit(episodes, native, shuffled, conventional):
    rows = [r for e in episodes for r in e["rows"] if r["selected_action"] in (0, 1)]
    # Source selected states are public and recorded; these are OFF-POLICY
    # alternate TURN proposals only, NOT interventions with measured reward.
    cnt = {"tested_original_selected_turn_contexts": len(rows),
           "native_proposals": 0, "conventional_proposals": 0,
           "native_versus_conventional_different": 0,
           "native_versus_shuffled_different": 0,
           "native_versus_frozen_different": 0,
           "native_versus_no_cell_different": 0}
    for row in rows:
        b = row["before"]
        p = native.proposal(b)
        baseline = conventional.proposal(b)
        neg = shuffled.proposal(b)
        if p is not None:
            cnt["native_proposals"] += 1
        if baseline is not None:
            cnt["conventional_proposals"] += 1
        cnt["native_versus_conventional_different"] += int(p != baseline)
        cnt["native_versus_shuffled_different"] += int(p != neg)
        cnt["native_versus_frozen_different"] += int(p is not None)
        cnt["native_versus_no_cell_different"] += int(p is not None)
    return cnt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--authentic-fit-artifact-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    source = read_source(args.authentic_fit_artifact_dir)
    training = [e for e in source if e["seed_public_fit_role"] in
                P["train_original_fit_seed_ids"][e["family"]]]
    internal = [e for e in source if e["seed_public_fit_role"] in
                P["internal_FIT_check_seed_ids"][e["family"]]]
    assert len(training) == 12 and len(internal) == 4

    native, conv, shuffled = NativePlasticCells(), ConventionalBayesianEffects(), NativePlasticCells()
    expected = sum(len(e["rows"]) for e in training)
    native_n, native_cpu = train_rows(training, native)
    conventional_n, conventional_cpu = train_rows(training, conv)
    shuffle_n, shuffle_cpu = train_rows(training, shuffled, swap=True)
    assert native_n == conventional_n == shuffle_n == expected
    assert native.actions == conv.actions
    assert all(native.actions[str(a)] > 0 for a in (0, 1, 2))

    native_score = scored(internal, native)
    conventional_score = scored(internal, conv)
    initial = scored(internal, NativePlasticCells())
    shuffled_score = scored(internal, shuffled)
    decision_cases = proposals_on_fit(training, native, shuffled, conv)
    first = internal[0]["rows"][0]
    native_bytes = cold_exact(native, first["before"], first["selected_action"])
    conv_bytes = cold_exact(conv, first["before"], first["selected_action"])
    shuffled_bytes = cold_exact(shuffled, first["before"], first["selected_action"])

    native_better_both = all(a < b for a, b in zip(native_score["brier"], conventional_score["brier"]))
    meaningful = (decision_cases["native_versus_shuffled_different"] > 0 and
                  decision_cases["native_versus_frozen_different"] > 0)
    # Never confuse an off-policy proposal with source-observed action value.
    if not native_better_both:
        decision = "NO_GO_CONVENTIONAL_BETTER_BOTH_OVERALL_FIT_CHECK_LABELS"
    elif not meaningful:
        decision = "NO_GO_NATIVE_ACTION_CONDITIONING_NOT_DEMONSTRATED"
    else:
        decision = "FIT_ONLY_PREDICTION_SIGNAL_NOT_TRUE_CAUSAL_VALUE"
    result = {
        "schema": "optimizer.o22p.authentic-original-FIT-only-prediction.v1",
        "source_run_id": EXPECTED["run_id"],
        "source_fit_artifact_id": EXPECTED["artifact_id"],
        "source_original_events": 549,
        "split": {"train_episodes": 12, "held_back_INTERNAL_FIT_episodes": 4,
                  "trained_events_each": expected,
                  "internal_check_events": native_score["n_selected_source_actions"]},
        "native": native_score,
        "independent_conventional": conventional_score,
        "shuffled_action_native": shuffled_score,
        "untrained_constant": initial,
        "source_public_proposals_NOT_actual_executed_alternate_turns": decision_cases,
        "measurements": {
            "native_training_cpu_s": native_cpu,
            "conventional_training_cpu_s": conventional_cpu,
            "shuffled_training_cpu_s": shuffle_cpu,
            "native_checkpoint_bytes": native_bytes,
            "conventional_checkpoint_bytes": conv_bytes,
            "shuffled_checkpoint_bytes": shuffled_bytes,
            "process_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        },
        "source_dev_and_protected_actions_added": 0,
        "full_original_world_action_value": "NOT_TESTED",
        "scientific_admission": decision,
    }
    args.out.write_bytes(canonical(result) + b"\n")
    print("O22P_AUTHENTIC_SELECTED_ACTION_FIT_BLOBS=PASS", flush=True)
    print("O22P_EQUAL_TRAINED_SOURCE_ACTIONS=" + str(expected), flush=True)
    print("O22P_INTERNAL_FIT_NATIVE_BRIER=" + json.dumps(native_score["brier"]), flush=True)
    print("O22P_INTERNAL_FIT_CONVENTIONAL_BRIER=" + json.dumps(conventional_score["brier"]), flush=True)
    print("O22P_INTERNAL_FIT_ACTION_PROPOSALS=" + json.dumps(decision_cases, sort_keys=True), flush=True)
    print("O22P_COLD_NATIVE_CONVENTIONAL=PASS", flush=True)
    print("O22P_SCIENTIFIC_DECISION=" + decision, flush=True)
    print("O22P_NO_NEW_DEV_OR_PROTECTED_SOURCE_ACTIONS=PASS", flush=True)


if __name__ == "__main__":
    main()
