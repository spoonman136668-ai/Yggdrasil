"""Frozen WSP82 unregistered temporal-feature development experiment.

One exact 384-paid-action continuous trajectory/world. No protected WSP80
scientific first use. All model predictions freeze (hash + complete bytes)
before ANY evaluator-private truth query. Preserves negative control and
nonconvergent matched-history Adam receipts.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter_ns, process_time_ns

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.append(str(HERE.parent / "WSP-81"))

import source
from temporal_weights import PaidTemporalFeatureEditor
from independent_symbolic import IndependentTemporalSymbolic
from history_adam import EndToEndAdamControl
from history_weights import PaidHistoryNumeric as OldWSP81HypothesisModel

PRE_COMMIT = "4bff9a0d576e04d8123a902545680d2b78e176da"
PRE_PARENT = "329990675dab926663aaf697383d812525b13600"
FROZEN = {
    "research/contrib/chatgpt/WSP-82/prereg.json":
        "4c16e604593f6c1c556512327942e0626ff3ddfb",
    "research/contrib/chatgpt/WSP-82/source.py":
        "081180827de282c2c2ab4cc756f7e7a91f5e070d",
    "research/contrib/chatgpt/WSP-82/temporal_weights.py":
        "79e5fcce5df0954d1ac818cb4b2797eab6a82392",
    "research/contrib/chatgpt/WSP-82/independent_symbolic.py":
        "8b2de938d46ecfb273edb0895e02f8bd773c6e94",
    "research/contrib/chatgpt/WSP-82/history_adam.py":
        "1c5b63c69a8cc6d1b1c1cb353347f0aa40deae5c",
    "research/contrib/chatgpt/WSP-81/history_weights.py":
        "c03272439b2c74fbab1ccfcdd3bfd03232830a83",
    "research/contrib/chatgpt/WSP-80/prereg.json":
        "0e96f4e0eff1ced7f87b754a2ad4fbb75c7b3d58",
    "research/contrib/chatgpt/WSP-80/source.py":
        "c5d0ab0dcf38b2f2dec1e60d7d8346eb2c2697d2",
    "research/contrib/chatgpt/WSP-77/fully_trained_mlp6.py":
        "90bca703948c71e482892d2be830682201342368",
}
CONTEXTS = source.CONTEXTS
PUBLIC = tuple((state, action, context)
               for context in CONTEXTS
               for state in source.STATES for action in source.ACTIONS)
assert len(PUBLIC) == 1536


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(obj):
    return sha256(canonical(obj).encode("ascii")).hexdigest()


def git(*args):
    return subprocess.run(("git",) + args, cwd=REPO,
                          check=True, text=True, capture_output=True).stdout.strip()


def validate_readonly_custody():
    head = git("rev-parse", "HEAD")
    expected = os.getenv("GITHUB_SHA")
    if os.getenv("GITHUB_EVENT_NAME") == "pull_request":
        expected = os.getenv("WSP82_CHECKOUT_HEAD_SHA")
        if not expected:
            raise RuntimeError("missing PR checkout head custody")
    if len(head) != 40 or (expected and head != expected) or git("status", "--porcelain"):
        raise RuntimeError("checkout SHA or cleanliness drift")
    if git("rev-parse", PRE_COMMIT + "^") != PRE_PARENT:
        raise RuntimeError("WSP82 prereg was not prospective")
    first_path = "research/contrib/chatgpt/WSP-82/prereg.json"
    if git("rev-parse", PRE_COMMIT + ":" + first_path) != FROZEN[first_path]:
        raise RuntimeError("WSP82 prereg-only commit changed")
    for path, blob in FROZEN.items():
        if git("rev-parse", "HEAD:" + path) != blob:
            raise RuntimeError("frozen source, strong control or prereg drift: " + path)
    prereg = json.loads((HERE / "prereg.json").read_text("utf8"))
    if (prereg["schema"] != "wsp82.temporal-feature-induction-dev-prereg.v1"
            or prereg["status"] !=
                "FROZEN_BEFORE_NEW_SOURCE_LEARNER_CONTROL_IMPLEMENTATION_OR_OUTCOMES"
            or prereg["parent"]["sha"] != PRE_PARENT
            or prereg["source"]["cohort"] != [
                {"seed": s, "family": source.COHORT[s]} for s in (9701,9702,9703,9704)]
            or prereg["source"]["total_paid_actions"] != 1536
            or prereg["source"]["query_count_total"] != 6144
            or prereg["source"]["protected_source_first_use"] is not False
            or prereg["authority"]["registered_first_use"] is not False):
        raise RuntimeError("scientific/development protocol changed")
    return head, prereg


def charged_source_trajectory(world):
    session = world.session()
    learned = PaidTemporalFeatureEditor()
    old = OldWSP81HypothesisModel()
    history_rows = []
    for step in range(384):
        action = source.fixed_action(world.seed, step)
        previous = tuple(session.actions)
        event = session.step(action)
        if event.action_cost != 1:
            raise ValueError("unpaid source observation")
        learned.charge(event.before, event.action, event.after, event.action_cost)
        old.charge(event.before, event.action, event.after, event.action_cost)
        history_rows.append((event.before, event.action, previous, event.after))
    if len(session.ledger) != 384 or learned.charges != 384:
        raise AssertionError("incomplete physical paid source")
    return tuple(session.ledger), tuple(history_rows), learned, old


def _lookup(ledger):
    answers = {}
    history = []
    for row in ledger:
        key = (row.before, row.action, tuple(history[-2:]))
        previous = answers.get(key)
        answers[key] = row.after if previous is None or previous == row.after else None
        history.append(row.action)
    def predict(state, action, context):
        return answers.get((state, action, tuple(context[-2:])))
    return predict


def _memoryless(state, action):
    out = list(state)
    out[action] ^= 1
    return tuple(out)


def train_and_freeze(world, ledger, history_rows, learned, old):
    t = process_time_ns()
    numeric_info = learned.compile()
    numeric = PaidTemporalFeatureEditor.restore(learned.snapshot())
    snapshot = numeric.snapshot()
    symbolic = IndependentTemporalSymbolic(ledger)
    fit_numeric_cpu = process_time_ns() - t
    old_rejected = False
    old_diagnostic = None
    try:
        old_diagnostic = old.compile()
    except ValueError:
        old_rejected = True
    trained = EndToEndAdamControl(world.seed)
    t = process_time_ns()
    adam_receipt = trained.fit(history_rows)
    fit_adam_cpu = process_time_ns() - t
    memorizer = _lookup(ledger)
    outputs = {}
    for model in ("numeric", "symbolic", "memoryless", "charged_lookup",
                  "recurrent_adam_forced", "recurrent_adam_native"):
        readings = []
        for state, action, context in PUBLIC:
            if model == "numeric":
                val = numeric.predict(state, action, context)
            elif model == "symbolic":
                val = symbolic.predict(state, action, context)
            elif model == "memoryless":
                val = _memoryless(state, action)
            elif model == "charged_lookup":
                val = memorizer(state, action, context)
            elif model == "recurrent_adam_forced":
                val = trained.predict(state, action, context, confidence=False)
            else:
                val = trained.predict(state, action, context, confidence=True)
            if val is not None and (type(val) is not tuple or len(val) != 6
                    or any(type(x) is not int or x not in (0,1) for x in val)):
                raise ValueError("nonbinary or undefined public prediction")
            readings.append(list(val) if val is not None else None)
        outputs[model] = readings
    if len(outputs) != 6 or any(len(v) != 1536 for v in outputs.values()):
        raise AssertionError("missing prediction portfolio")
    paid_pairs = sorted({tuple(x.before) + (x.action,) for x in ledger})
    payload = {
        "schema": "wsp82.frozen-public-predictions-before-truth.v1",
        "seed": world.seed,
        "paid_action_count": len(ledger),
        "public_query_count": len(PUBLIC),
        "paid_pairs": [list(x) for x in paid_pairs],
        "outputs": outputs,
    }
    frozen_bytes = canonical(payload)
    return {
        "prelabel": frozen_bytes,
        "prelabel_digest": sha256(frozen_bytes.encode("ascii")).hexdigest(),
        "numeric_info": numeric_info,
        "numeric_fit_CPU_ns": fit_numeric_cpu,
        "numeric_snapshot_digest": sha256(snapshot.encode("ascii")).hexdigest(),
        "numeric_cold_readout_match": all(
            numeric.predict(s,a,h) == learned.predict(s,a,h)
            for s,a,h in PUBLIC),
        "symbolic_exact_parity": outputs["numeric"] == outputs["symbolic"],
        "old_WSP81_model_rejected": old_rejected,
        "old_WSP81_compile_diag": old_diagnostic,
        "Adam_receipt": adam_receipt,
        "Adam_fit_CPU_ns": fit_adam_cpu,
        "unlabeled_coverage": {
            name: sum(v is not None for v in readings)
            for name, readings in outputs.items()
        },
    }


def score_only_after_freeze(world, frozen):
    digest_before = sha256(frozen["prelabel"].encode("ascii")).hexdigest()
    if digest_before != frozen["prelabel_digest"]:
        raise AssertionError("prelabel predictions not frozen")
    payload = json.loads(frozen["prelabel"])
    if (payload["seed"] != world.seed or payload["paid_action_count"] != 384
            or payload["public_query_count"] != len(PUBLIC)):
        raise AssertionError("private evaluator source or budget mismatch")
    # FIRST AND ONLY private arbitrary state/context truth used for scoring.
    truth = [world._truth(context, state, action) for state,action,context in PUBLIC]
    paid = {tuple(p) for p in payload["paid_pairs"]}
    results = {}
    for name, predictions in payload["outputs"].items():
        metrics = {"correct":0, "wrong_confident":0, "abstain":0,
                   "unpaid_correct":0, "unpaid_total":0}
        for i, pred in enumerate(predictions):
            state, action, _context = PUBLIC[i]
            if pred is None:
                category = "abstain"
            elif tuple(pred) == truth[i]:
                category = "correct"
            else:
                category = "wrong_confident"
            metrics[category] += 1
            if tuple(state) + (action,) not in paid:
                metrics["unpaid_total"] += 1
                if category == "correct":
                    metrics["unpaid_correct"] += 1
        if sum(metrics[k] for k in ("correct","wrong_confident","abstain")) != 1536:
            raise AssertionError("unscored public evaluator queries")
        results[name] = metrics
    return results


def classify(records, prereg):
    t = prereg["thresholds"]
    novel = [x for x in records if x["family"] == "equal_lag_two"]
    controls = [x for x in records if x["family"] == "memoryless_control"]
    if len(novel) != 2 or len(controls) != 2:
        raise AssertionError("not the fixed source cohort")
    check = {
        "old_WSP81_misspecified": sum(x["old_WSP81_model_rejected"] for x in novel)
            >= t["new_worlds_with_old_WSP81_incompatible_min"],
        "old_WSP81_control_no_false_conflict":
            sum(not x["old_WSP81_model_rejected"] for x in controls)
            >= t["memoryless_controls_without_old_WSP81_incompatible_min"],
        "novel_correct": all(x["scores"]["numeric"]["correct"] >=
            t["new_worlds_correct_confident_per_world_min"] for x in novel),
        "novel_no_confident_errors": all(x["scores"]["numeric"]["wrong_confident"] <=
            t["new_worlds_wrong_confident_per_world_max"] for x in novel),
        "novel_over_memoryless": sum(
            x["scores"]["numeric"]["correct"]-x["scores"]["memoryless"]["correct"]
            for x in novel) >= t["new_worlds_aggregate_correct_gain_vs_markov_min"],
        "never_paid_correct": sum(x["scores"]["numeric"]["unpaid_correct"]
                                  for x in novel) >=
            t["new_worlds_aggregate_correct_unpaid_min"],
        "memoryless_controls_perfect": sum(
            x["scores"]["numeric"]["correct"] == 1536 for x in controls) >=
            t["controls_perfect_1536_min"],
        "independent_symbolic_parity": sum(
            x["symbolic_exact_parity"] for x in records) >=
            t["numerical_symbolic_prediction_parity_worlds_min"],
        "learned_temporal_feature": sum(
            x["numeric_info"]["nonconstant_temporal_weight_selected"]
            for x in novel) >= t["new_feature_nonconstant_selected_worlds_min"],
        "cold_restore": all(x["numeric_cold_readout_match"] for x in records),
        "paid_exact": sum(x["paid_actions"] for x in records) ==
            t["paid_source_actions_exact"],
        "recurrent_adam_converged": sum(
            x["Adam_receipt"]["fully_trained"] for x in records) >=
            t["recurrent_Adam_converged_worlds_min"],
        "registered_source_unused": True,
    }
    return {"classification":
        "DEV_TEMPORAL_FEATURE_DIAGNOSTICS_PASS" if all(check.values())
        else "DEV_TEMPORAL_FEATURE_DIAGNOSTICS_NEGATIVE",
        "checks": check, "passed": sum(check.values()), "total": len(check)}


def run():
    if sys.argv[1:] != ["--frozen-unregistered-dev-only"]:
        raise PermissionError("protected scientific first use not admitted")
    sha, protocol = validate_readonly_custody()
    start_cpu, start_wall = process_time_ns(), perf_counter_ns()
    records = []
    for spec in protocol["source"]["cohort"]:
        world = source.World(spec["seed"])
        if world.family != spec["family"]:
            raise AssertionError("frozen family mismatch")
        t = process_time_ns()
        ledger, history_rows, learned, old = charged_source_trajectory(world)
        acquisition_cpu_ns = process_time_ns() - t
        freeze = train_and_freeze(world, ledger, history_rows, learned, old)
        scored = score_only_after_freeze(world, freeze)
        record = {
            "seed": world.seed, "family": world.family,
            "hidden_source_sha256": world.private_receipt(),
            "charged_ledger_sha256": digest([
                [x.before,x.action,x.after,x.action_cost] for x in ledger]),
            "paid_actions": len(ledger),
            "numerical_snapshot_sha256": freeze["numeric_snapshot_digest"],
            "prelabel_sha256": freeze["prelabel_digest"],
            "old_WSP81_model_rejected": freeze["old_WSP81_model_rejected"],
            "old_WSP81_compile_diag": freeze["old_WSP81_compile_diag"],
            "numeric_info": freeze["numeric_info"],
            "numeric_cold_readout_match": freeze["numeric_cold_readout_match"],
            "symbolic_exact_parity": freeze["symbolic_exact_parity"],
            "Adam_receipt": freeze["Adam_receipt"],
            "source_acquisition_cpu_ns": acquisition_cpu_ns,
            "numeric_fit_cpu_ns": freeze["numeric_fit_CPU_ns"],
            "recurrent_adam_fit_cpu_ns": freeze["Adam_fit_CPU_ns"],
            "scores": scored,
        }
        records.append(record)
    classified = classify(records, protocol)
    result = {
        "schema":"wsp82.temporal-feature-developer-result.v1",
        "source_commit_sha":sha,
        "prereg_first_commit":PRE_COMMIT,
        "prereg_sha1_git_blob":FROZEN["research/contrib/chatgpt/WSP-82/prereg.json"],
        "unregistered_dev_worlds":len(records),
        "paid_actions_total":sum(x["paid_actions"] for x in records),
        "private_scored_queries_total":len(PUBLIC)*len(records),
        "protected_WSP80_first_use":False,
        "cpu_ns_all_control_portfolios":process_time_ns()-start_cpu,
        "wall_ns_all_control_portfolios":perf_counter_ns()-start_wall,
        "worlds":records,
        "predeclared_diagnostics":classified,
        "scientific_acceptance":"UNVERIFIED",
        "open_ended_mechanism_invention":False,
        "result_not_agI":True,
    }
    print("WSP82_DEV_RESULT="+canonical(result),flush=True)


if __name__ == "__main__":
    run()
