"""PAD-02 action-conditional, genuinely source-returned PUBLIC DEVELOPMENT falsifier.

Policy subprocess receives only chronological public FIT tuples and public DEV inputs.
No source module is imported by or shared with policy process.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

N_ACTIONS = 3
N_INPUTS = 6
ZERO = (0, 0, 0, 0, 0, 0)
PAIRS = tuple(itertools.combinations(range(6), 2))
TRIPLES = tuple(itertools.combinations(range(6), 3))
LAGS = tuple((i, j) for i in range(6) for j in range(6))


def checksum(obj):
    return hashlib.sha256(json.dumps(obj, separators=(",", ":"), sort_keys=True).encode()).hexdigest()


def bits(x, previous, kind, indexes):
    if kind == "pair":
        i, j = indexes
        return (x[i], x[j])
    if kind == "triple":
        i, j, k = indexes
        return (x[i], x[j], x[k])
    if kind == "lag":
        i, j = indexes
        return (previous[i], x[j])
    raise ValueError("INVALID_MODEL_STRUCTURE")


def index_for(seq):
    n = 0
    for b in seq:
        n = 2*n + int(b)
    return n


def score_table(rows, action, kind, indexes):
    n_cells = 8 if kind == "triple" else 4
    cells = [[0, 0] for _ in range(n_cells)]
    for x, previous, a, reward in rows:
        if a != action:
            continue
        k = index_for(bits(x, previous, kind, indexes))
        cells[k][0] += reward
        cells[k][1] += 1
    probs = tuple((count_yes + 1)/(count_total + 2) for count_yes, count_total in cells)
    loss = sum((reward - probs[index_for(bits(x, previous, kind, indexes))])**2
               for x, previous, a, reward in rows if a == action)
    loss += 0.025 * sum(c == 0 for _, c in cells)
    if kind == "triple":
        loss += 0.02
    return (loss, kind, tuple(indexes), probs)


def fit_conventional_sparse(rows, family_set):
    fits = []
    for a in range(N_ACTIONS):
        candidates = []
        if "pair" in family_set:
            candidates.extend(score_table(rows, a, "pair", idx) for idx in PAIRS)
        if "triple" in family_set:
            candidates.extend(score_table(rows, a, "triple", idx) for idx in TRIPLES)
        if "lag" in family_set:
            candidates.extend(score_table(rows, a, "lag", idx) for idx in LAGS)
        # Stable loss and source-free parameter ordering. No family labels or DEV use.
        fit = min(candidates, key=lambda t: (t[0], t[1], t[2]))
        fits.append((fit[1], fit[2], fit[3]))
    return fits


def choose_structural(model, x, previous):
    predictions = []
    for a, (kind, indexes, probs) in enumerate(model):
        predictions.append(probs[index_for(bits(x, previous, kind, indexes))])
    return max(range(N_ACTIONS), key=lambda a: (predictions[a], -a))


def policy_run(input_path, output_path, arm):
    # Deliberately no import of mass_pad02.source or other hidden/oracle modules.
    from research.native.itd01.mass_pad01 import run as pad
    data = json.loads(input_path.read_text())
    rows = [
        (tuple(x), tuple(previous), int(a), int(y))
        for x, previous, a, y in data["public_fit"]
    ]
    dev = [tuple(x) for x in data["public_dev_inputs"]]
    assert len(rows) == 192 and len(dev) == 128
    assert all(len(x) == 6 and len(previous) == 6 and a in range(3) and y in (0, 1)
               for x, previous, a, y in rows)
    # Parent source/simulator, seed, source-rule, family name never in child input.
    main_rows = [(x, a, y) for x, _, a, y in rows]
    started = time.process_time()
    if arm == "pad01_frozen_pair":
        model = pad.fit_sparse_pair(main_rows)
    elif arm == "credit_destroyed":
        bad_rows = [(x, (a+1)%3, y) for x, a, y in main_rows]
        model = pad.fit_sparse_pair(bad_rows)
    elif arm == "trained_pair_table":
        model = fit_conventional_sparse(rows, ("pair",))
    elif arm == "trained_structural_search":
        model = fit_conventional_sparse(rows, ("pair", "triple", "lag"))
    elif arm == "trained_episodic":
        model = tuple(main_rows)
    elif arm == "trained_action_prior":
        model = pad.fit_prior(main_rows)
    else:
        raise ValueError("INVALID_ARM")
    fit_cpu = time.process_time() - started
    chosen = []
    previous = ZERO
    for x in dev:
        if arm in ("pad01_frozen_pair", "credit_destroyed"):
            scores = [pad.predict_sparse(model, x, a) for a in range(N_ACTIONS)]
            action = max(range(N_ACTIONS), key=lambda a: (scores[a], -a))
        elif arm in ("trained_pair_table", "trained_structural_search"):
            action = choose_structural(model, x, previous)
        elif arm == "trained_episodic":
            scores = [pad.predict_episodic(main_rows, x, a) for a in range(N_ACTIONS)]
            action = max(range(N_ACTIONS), key=lambda a: (scores[a], -a))
        else:
            action = max(range(N_ACTIONS), key=lambda a: (model[a], -a))
        chosen.append(action)
        previous = x
    receipt = {
        "arm": arm,
        "fitted_public_fit_steps": len(rows),
        "actions": chosen,
        "fit_cpu_seconds": fit_cpu,
        "policy_total_cpu_seconds": time.process_time() - started,
        "policy_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "model_json_bytes": len(json.dumps(model, separators=(",", ":")).encode()),
        "model_sha256": checksum(model),
        "source_module_imported": "research.native.itd01.mass_pad02.source" in sys.modules
    }
    if receipt["source_module_imported"]:
        raise RuntimeError("LEARNER_IMPORTED_PRIVATE_SOURCE")
    output_path.write_text(json.dumps(receipt, sort_keys=True) + "\n")
    return 0


def evaluate(outdir):
    # Import hidden source only in evaluator, NEVER in policy subprocess.
    from research.native.itd01.mass_pad02 import source
    outdir.mkdir(parents=True, exist_ok=True)
    task_reports = []
    total_parent_cpu_before = time.process_time()
    total_parent_wall_before = time.perf_counter()
    for family in source.FAMILIES:
        for replica in source.REPLICAS:
            seed = source.seed_for(family, replica)
            rows, hidden_identity = source.fit_source(family, seed)
            dev = source.dev_public_inputs(seed)
            assert len(rows) == source.FIT and len(dev) == source.DEV
            # No hidden family/rule/custodian metadata passed to policy; only public roles.
            pub = {"public_fit": rows, "public_dev_inputs": dev}
            taskdir = outdir / (family + str(replica))
            taskdir.mkdir()
            public_path = taskdir / "input-public.json"
            public_path.write_text(json.dumps(pub, sort_keys=True) + "\n")
            arm_reports = {}
            total_source_steps = source.FIT
            for arm in source.ARMS:
                result_path = taskdir / (arm + "-policy.json")
                started = time.perf_counter()
                child = subprocess.run(
                    [sys.executable, "-B", "-m", "research.native.itd01.mass_pad02.compare",
                     "--policy", "--input", str(public_path), "--output", str(result_path),
                     "--arm", arm],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90, text=True,
                    check=False, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
                elapsed = time.perf_counter() - started
                if child.returncode != 0:
                    raise RuntimeError("POLICY_PROCESS_FAILED:" + arm + ":" + child.stderr[-800:])
                policy = json.loads(result_path.read_text())
                actions = policy["actions"]
                if len(actions) != source.DEV or any(a not in (0,1,2) for a in actions):
                    raise RuntimeError("ILLEGAL_OR_MISSING_PUBLIC_DEV_ACTION")
                if policy["source_module_imported"] or policy["fitted_public_fit_steps"] != source.FIT:
                    raise RuntimeError("PRIVATE_SOURCE_LEAK_OR_BAD_FIT")
                # Fresh source state, replay same public DEV observations for each arm.
                src = source.HiddenSource(family, seed)
                reward = [src.step(x, action) for x, action in zip(dev, actions)]
                if src.steps != source.DEV or src.identity() != hidden_identity:
                    raise RuntimeError("SOURCE_ORIGINAL_ACTION_IDENTITY_DRIFT")
                total_source_steps += src.steps
                arm_reports[arm] = {
                    "original_source_reward_mean": sum(reward)/len(reward),
                    "original_source_actual_rewards": reward,
                    "original_source_chosen_actions": actions,
                    "source_original_dev_steps": src.steps,
                    "source_private_rule_sha256_auditor_only": src.identity(),
                    "fit_cpu_seconds": policy["fit_cpu_seconds"],
                    "policy_cpu_seconds": policy["policy_total_cpu_seconds"],
                    "policy_fresh_process_peak_rss_kib": policy["policy_peak_rss_kib"],
                    "policy_process_wall_seconds": elapsed,
                    "policy_model_json_bytes": policy["model_json_bytes"],
                    "policy_model_sha256": policy["model_sha256"]
                }
            # Core comparison independently rechecks source actual actions and fairness.
            a = arm_reports["pad01_frozen_pair"]["original_source_chosen_actions"]
            b = arm_reports["trained_pair_table"]["original_source_chosen_actions"]
            if a != b:
                raise RuntimeError("EQUAL_FIT_MATCHED_SPARSE_CONTROL_NOT_EQUIVALENT")
            if total_source_steps != source.FIT + source.DEV*len(source.ARMS):
                raise RuntimeError("SOURCE_STEP_MISMATCH")
            task_reports.append({
                "family":family, "replica":replica,
                "source_rule_sha256_auditor_only":hidden_identity,
                "public_source_role_seed_auditor_only":seed,
                "public_fit_sha256":checksum(rows),
                "public_dev_inputs_sha256":checksum(dev),
                "original_fit_chosen_source_steps":source.FIT,
                "original_dev_chosen_source_steps":source.DEV*len(source.ARMS),
                "actions_frozen_vs_matched_pair_identical":True,
                "arms":arm_reports
            })
            # The FIT/DEV observations are not retained in the GitHub artifact.
            public_path.unlink()
            for arm in source.ARMS:
                (taskdir/(arm+"-policy.json")).unlink()
            taskdir.rmdir()
    per_family = {}
    for family in source.FAMILIES:
        tasks = [t for t in task_reports if t["family"] == family]
        means = {arm: sum(t["arms"][arm]["original_source_reward_mean"] for t in tasks)/len(tasks)
                 for arm in source.ARMS}
        per_family[family] = {
            "mean_source_reward": means,
            "matched_sparse_control_actions_identical": all(t["actions_frozen_vs_matched_pair_identical"] for t in tasks),
            "stronger_structural_minus_frozen": means["trained_structural_search"]-means["pad01_frozen_pair"],
            "sparse_candidate_minus_matched_pair": means["pad01_frozen_pair"]-means["trained_pair_table"]
        }
    supported = all(
        per_family[family]["matched_sparse_control_actions_identical"] and
        per_family[family]["stronger_structural_minus_frozen"] >= 0.05
        for family in source.FAMILIES
    )
    receipt = {
        "schema":"mass.pad02.internal-public-falsifier.v1",
        "frozen_parent_PAD01_head":"02e040f77b1b824dfe6a388b5df03fe33c6b8b09",
        "PAD02_first_only_commit":"5cb09132674a85b5f2ae8ee0e16ca8ac7b5017da",
        "candidate_PAD01_git_blob":"c6dc75ea14996d862fcbaa384156f1efd625effd",
        "source_description":"internally authored novel T and L grammars, not independent scientific first-use",
        "families":per_family,"tasks":task_reports,
        "source_fit_action_count":len(task_reports)*source.FIT,
        "source_dev_action_count":len(task_reports)*source.DEV*len(source.ARMS),
        "total_parent_process_cpu_seconds":time.process_time()-total_parent_cpu_before,
        "total_parent_wall_seconds":time.perf_counter()-total_parent_wall_before,
        "parent_peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "protected_first_use_count":0,
        "independent_external_source_replicated":False,
        "source_independent_cryptographic_blind":False,
        "scientific_promotion_authorized":False,
        "disposition":"PAD02_CONVENTIONAL_EXPLAINS_PRIOR_GAIN" if supported else "PAD02_FALSIFICATION_INCONCLUSIVE"
    }
    final = outdir/"receipt.json"
    final.write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    print("PAD02_DISPOSITION="+receipt["disposition"])
    print("PAD02_ORIGINAL_ACTIONS_FIT="+str(receipt["source_fit_action_count"]))
    print("PAD02_ORIGINAL_ACTIONS_DEV="+str(receipt["source_dev_action_count"]))
    print("PAD02_FAMILY_RESULTS="+json.dumps(per_family, sort_keys=True))
    print("PAD02_PROTECTED_FIRST_USE=0")
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--policy", action="store_true")
    p.add_argument("--input", type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--arm")
    p.add_argument("--outdir", type=Path)
    a = p.parse_args()
    if a.policy:
        if a.input is None or a.output is None or a.arm is None or a.outdir is not None:
            p.error("POLICY_INTERFACE_INVALID")
        return policy_run(a.input, a.output, a.arm)
    if a.outdir is None or a.input is not None or a.output is not None or a.arm is not None:
        p.error("EVALUATOR_INTERFACE_INVALID")
    return evaluate(a.outdir)


if __name__ == "__main__":
    raise SystemExit(main())
