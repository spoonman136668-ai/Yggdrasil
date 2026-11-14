"""WSP81 one-shot out-of-WSP80-Markov-grammar developer falsification.

Only unregistered seeds 9401..9406. Frozen prereg SHA predates this source.
All learning (including ordinary Adam and symbolic) uses charged PUBLIC rows
only; evaluator-private hidden-regime labels are accessed after model output
SHA256 freeze. Outcomes, including negative scientific/development results,
stay in GitHub CI logs. No protected scientific first use, merge or promotion.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys
from time import process_time_ns, perf_counter_ns

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
WSP80 = HERE.parent / "WSP-80"
sys.path.append(str(WSP80))

import source
from history_weights import PaidHistoryNumeric
from independent_control import IndependentHistorySymbolic
from controls import ConventionalAdam384
from structural_weights import PaidStructuralWeightEditor

SCHEMA = "wsp81.out-of-markov-dev-result.v1"
PRE_COMMIT = "a3782028045759994a5a3c3de3765a1d939ed6e3"
PRE_PARENT = "e2a363943d3ac81875cbcc237f2cc53b4b594112"
PINNED = {
    "research/contrib/chatgpt/WSP-81/prereg.json":
        "954041015a52a3cc215964511be04abebec114fd",
    "research/contrib/chatgpt/WSP-81/source.py":
        "33cd96813a9f6be43583eb33a8c749cbcfc38019",
    "research/contrib/chatgpt/WSP-81/history_weights.py":
        "c03272439b2c74fbab1ccfcdd3bfd03232830a83",
    "research/contrib/chatgpt/WSP-81/independent_control.py":
        "a2cde59cb9644784d5d5fe11a3cdcfc06b3fedc3",
    "research/contrib/chatgpt/WSP-80/prereg.json":
        "0e96f4e0eff1ced7f87b754a2ad4fbb75c7b3d58",
    "research/contrib/chatgpt/WSP-80/source.py":
        "c5d0ab0dcf38b2f2dec1e60d7d8346eb2c2697d2",
    "research/contrib/chatgpt/WSP-77/fully_trained_mlp6.py":
        "90bca703948c71e482892d2be830682201342368",
}
CONTEXTS = ((), (0, 1, 2, 3, 4, 5))
PUBLIC = tuple((s, a, h) for h in CONTEXTS
               for s in source.STATES for a in source.ACTIONS)
assert len(PUBLIC) == 768


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(obj):
    return sha256(canonical(obj).encode("ascii")).hexdigest()


def git(*args):
    return subprocess.run(("git",) + args, cwd=REPO,
                          text=True, check=True, capture_output=True).stdout.strip()


def validate_custody():
    head = git("rev-parse", "HEAD")
    expected = os.environ.get("GITHUB_SHA")
    if os.environ.get("GITHUB_EVENT_NAME") == "pull_request":
        expected = os.environ.get("WSP81_CHECKOUT_HEAD_SHA")
        if not expected:
            raise RuntimeError("PR checkout identity not supplied")
    if len(head) != 40 or (expected and head != expected):
        raise RuntimeError("candidate SHA mismatch")
    if git("status", "--porcelain"):
        raise RuntimeError("dirty exact-source tree")
    if git("rev-parse", PRE_COMMIT + "^") != PRE_PARENT:
        raise RuntimeError("developer prereg parent source changed")
    if git("rev-parse", PRE_COMMIT + ":research/contrib/chatgpt/WSP-81/prereg.json") != PINNED[
            "research/contrib/chatgpt/WSP-81/prereg.json"]:
        raise RuntimeError("first frozen WSP81 prereg blob changed")
    for path, frozen in PINNED.items():
        if git("rev-parse", "HEAD:" + path) != frozen:
            raise RuntimeError("frozen source or control drift: " + path)
    reg = json.loads((HERE / "prereg.json").read_text("utf8"))
    if (reg["schema"] != "wsp81.history-dependent-dev-prereg.v1"
            or reg["state"] != "FROZEN_BEFORE_SOURCE_IMPLEMENTATION_OR_RESULTS"
            or reg["provenance"]["parent_commit"] != PRE_PARENT
            or reg["source"]["paid_actions_per_world"] != 384
            or reg["source"]["total_paid_actions"] != 2304
            or [w["seed"] for w in reg["source"]["seeds"]] != list(range(9401, 9407))
            or reg["source"]["seed_reuse_or_registered_access"] is not False
            or reg["constraints"]["zero_registered_source_first_use"] is not True):
        raise RuntimeError("WSP81 prereg threshold or cohort drift")
    return head, reg


def charged_trajectory(world):
    session = world.session()
    writer = PaidHistoryNumeric()
    legacy = PaidStructuralWeightEditor()
    legacy_rejected = False
    seen = {}
    contradicting_pairs = set()
    actions = []
    for step in range(384):
        action = source.fixed_action(world.seed, step)
        event = session.step(action)
        if event.action_cost != 1 or event.before != writer.current:
            raise AssertionError("unpaid or noncontinuous trajectory")
        writer.charge(event.before, event.action, event.after, event.action_cost)
        key = (event.before, event.action)
        if key in seen and seen[key] != event.after:
            contradicting_pairs.add(key)
        seen[key] = event.after
        if not legacy_rejected:
            try:
                legacy.charge(event.before, event.action, event.after, event.action_cost)
            except ValueError:
                legacy_rejected = True
        actions.append(action)
    if len(session.ledger) != 384 or len(actions) != 384:
        raise AssertionError("wrong paid budget")
    return tuple(session.ledger), writer, legacy_rejected, len(contradicting_pairs)


def paid_lookup(ledger):
    pairs = {}
    conflicting = set()
    for event in ledger:
        key = (event.before, event.action)
        if key in pairs and pairs[key] != event.after:
            conflicting.add(key)
        pairs[key] = event.after

    def predictor(state, action):
        key = (state, action)
        return None if key in conflicting else pairs.get(key)
    return predictor


def memoryless(state, action):
    result = list(state)
    result[action] ^= 1
    return tuple(result)


def freeze_world(ledger, writer, legacy_rejected, conflicts, seed):
    t = process_time_ns()
    diagnostic = writer.compile()
    writer = PaidHistoryNumeric.restore(writer.snapshot())
    numeric_snapshot = writer.snapshot()
    symbolic = IndependentHistorySymbolic(ledger)
    numeric_cpu_ns = process_time_ns() - t
    lookup = paid_lookup(ledger)
    adam = ConventionalAdam384(seed)
    t = process_time_ns()
    adam_receipt = adam.fit(ledger)
    adam_cpu_ns = process_time_ns() - t
    outputs = {}
    for name in ("numeric", "symbolic", "memoryless", "paid_lookup",
                 "adam_forced", "adam_native"):
        readings = []
        for state, action, context in PUBLIC:
            if name == "numeric":
                value = writer.predict(state, action, context)
            elif name == "symbolic":
                value = symbolic.predict(state, action, context)
            elif name == "memoryless":
                value = memoryless(state, action)
            elif name == "paid_lookup":
                value = lookup(state, action)
            elif name == "adam_forced":
                value = adam.predict(state, action, confidence=False)
            else:
                value = adam.predict(state, action, confidence=True)
            if value is not None and (type(value) is not tuple or
                                      len(value) != 6 or
                                      any(b not in (0, 1) for b in value)):
                raise AssertionError("invalid frozen public prediction")
            readings.append(list(value) if value is not None else None)
        outputs[name] = readings
    if len(outputs) != 6 or any(len(x) != 768 for x in outputs.values()):
        raise AssertionError("missing frozen model query")
    seen = {(x.before, x.action) for x in ledger}
    payload = {
        "schema": "wsp81.prelabel-history-context.v1",
        "seed": seed,
        "public_queries": len(PUBLIC),
        "paid_actions": len(ledger),
        "seen_paid_pairs": sorted([list(s) + [a] for s, a in seen]),
        "outputs": outputs,
    }
    before_labels = canonical(payload)
    frozen_hash = sha256(before_labels.encode("ascii")).hexdigest()
    return {"prelabel": before_labels, "prelabel_sha256": frozen_hash,
            "model_diagnostic": diagnostic,
            "numeric_weights_snapshot_sha256": sha256(
                numeric_snapshot.encode("ascii")).hexdigest(),
            "numeric_cpu_ns": numeric_cpu_ns,
            "adam_train_cpu_ns": adam_cpu_ns,
            "adam_receipt": adam_receipt,
            "legacy_markov_rejected": legacy_rejected,
            "paid_markov_conflicting_pairs": conflicts,
            "numeric_symbolic_exact_parity": (
                outputs["numeric"] == outputs["symbolic"]),
            "numeric_cold_restored": True}


def evaluate_postfreeze(world, frozen):
    if sha256(frozen["prelabel"].encode("ascii")).hexdigest() != frozen["prelabel_sha256"]:
        raise AssertionError("prelabel source custody was not frozen")
    payload = json.loads(frozen["prelabel"])
    if payload["seed"] != world.seed or payload["public_queries"] != 768:
        raise AssertionError("mismatched evaluator source")
    answers = [world._truth_for_context(context, state, action)
               for state, action, context in PUBLIC]
    paid_pairs = {tuple(row) for row in payload["seen_paid_pairs"]}
    scores = {}
    for name, predictions in payload["outputs"].items():
        count = {"correct": 0, "wrong_confident": 0, "abstain": 0,
                 "unpaid_correct": 0, "unpaid_total": 0}
        for i, observed in enumerate(predictions):
            state, action, _context = PUBLIC[i]
            category = ("abstain" if observed is None else
                        "correct" if tuple(observed) == answers[i] else
                        "wrong_confident")
            count[category] += 1
            if tuple(state) + (action,) not in paid_pairs:
                count["unpaid_total"] += 1
                if category == "correct":
                    count["unpaid_correct"] += 1
        if sum(count[k] for k in ("correct", "wrong_confident", "abstain")) != 768:
            raise AssertionError("incomplete private evaluator scoring")
        scores[name] = count
    return scores


def classify(records, prereg):
    t = prereg["thresholds"]
    hidden = [r for r in records if r["family"] == "hidden_two_mode"]
    controls = [r for r in records if r["family"] == "memoryless_control"]
    if len(hidden) != 4 or len(controls) != 2:
        raise AssertionError("invalid frozen family cohort")
    checks = {
        "hidden_public_markov_falsified":
            sum(r["paid_markov_conflicting_pairs"] > 0 for r in hidden) >=
            t["hidden_worlds_with_paid_public_deterministic_conflicts_min"],
        "control_no_false_markov_falsification":
            sum(r["paid_markov_conflicting_pairs"] > 0 for r in controls) <=
            t["deterministic_controls_with_conflicts_max"],
        "latent_700_correct":
            sum(r["scores"]["numeric"]["correct"] >= 700 for r in hidden) >=
            t["latent_worlds_700_plus_correct_of_768_min"],
        "latent_zero_confident_errors":
            sum(r["scores"]["numeric"]["wrong_confident"] > 0 for r in hidden) <=
            t["latent_worlds_any_wrong_confident_max"],
        "controls_768_correct":
            sum(r["scores"]["numeric"]["correct"] == 768 for r in controls) >=
            t["controls_perfect_768_of_768_min"],
        "independent_symbolic_full_parity":
            sum(r["numeric_symbolic_exact_parity"] for r in records) >=
            t["history_numeric_symbolic_exact_parity_worlds_min"],
        "history_correct_over_memoryless":
            sum(r["scores"]["numeric"]["correct"] -
                r["scores"]["memoryless"]["correct"] for r in hidden) >=
            t["latent_correct_gain_over_memoryless_aggregate_min"],
        "genuinely_unpaid_correct":
            sum(r["scores"]["numeric"]["unpaid_correct"] for r in records) >=
            t["correct_on_unpaid_public_pairs_min"],
        "cold_restoration":
            all(r["numeric_cold_restored"] for r in records),
        "charged_budget":
            all(r["paid_actions"] == 384 for r in records),
        "registered_first_use_zero": True,
    }
    return {
        "classification": ("DEV_HIDDEN_HISTORY_DIAGNOSTICS_PASS"
                           if all(checks.values()) else
                           "DEV_HIDDEN_HISTORY_DIAGNOSTICS_NEGATIVE"),
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
    }


def main():
    if sys.argv[1:] != ["--frozen-unregistered-dev-only"]:
        raise PermissionError("protected or undefined experiment refused")
    sha, protocol = validate_custody()
    start_cpu, start_wall = process_time_ns(), perf_counter_ns()
    records = []
    for spec in protocol["source"]["seeds"]:
        seed, family = spec["seed"], spec["family"]
        world = source.World.developer(seed)
        if world.family != family:
            raise AssertionError("source family misassigned")
        t = process_time_ns()
        ledger, writer, refused, conflicts = charged_trajectory(world)
        acquisition_cpu = process_time_ns() - t
        frozen = freeze_world(ledger, writer, refused, conflicts, seed)
        # First and ONLY evaluator-private access after all model outputs frozen.
        score = evaluate_postfreeze(world, frozen)
        record = {
            "seed": seed, "family": family,
            "private_source_hash": world.private_receipt(),
            "charged_public_ledger_hash": digest([
                [e.before, e.action, e.after, e.action_cost] for e in ledger]),
            "paid_actions": len(ledger),
            "paid_markov_conflicting_pairs": conflicts,
            "legacy_WSP80_markov_editor_rejected": refused,
            "numeric_symbolic_exact_parity":
                frozen["numeric_symbolic_exact_parity"],
            "numeric_cold_restored": frozen["numeric_cold_restored"],
            "learned_mechanism_survivors":
                frozen["model_diagnostic"]["surviving_mechanisms"],
            "numeric_parameters":
                frozen["model_diagnostic"]["numerical_parameters"],
            "snapshot_digest": frozen["numeric_weights_snapshot_sha256"],
            "prelabel_sha256": frozen["prelabel_sha256"],
            "real_adam_trained": frozen["adam_receipt"]["fully_trained"],
            "real_adam_paid_train_accuracy":
                frozen["adam_receipt"]["best_train_exact"],
            "real_adam_gradient_updates":
                frozen["adam_receipt"]["gradient_updates_total"],
            "paid_acquisition_cpu_ns": acquisition_cpu,
            "numeric_model_fit_cpu_ns": frozen["numeric_cpu_ns"],
            "adam_train_cpu_ns": frozen["adam_train_cpu_ns"],
            "scores": score,
        }
        records.append(record)
    diagnostic = classify(records, protocol)
    report = {
        "schema": SCHEMA,
        "classification": "UNREGISTERED_DEVELOPMENT_ONLY_NOT_SCIENCE",
        "source_commit": sha,
        "frozen_prereg_first_commit": PRE_COMMIT,
        "frozen_prereg_blob": PINNED["research/contrib/chatgpt/WSP-81/prereg.json"],
        "registered_WSP80_seed_count_consumed": 0,
        "development_worlds": len(records),
        "physically_paid_actions": sum(r["paid_actions"] for r in records),
        "private_query_count": len(PUBLIC) * len(records),
        "cpu_total_ns": process_time_ns() - start_cpu,
        "wall_total_ns": perf_counter_ns() - start_wall,
        "world_results": records,
        "preregistered_developer_diagnostics": diagnostic,
        "actual_unforeseen_law_discovery": False,
        "general_intelligence_claim": False,
        "scientific_acceptance": "UNVERIFIED",
    }
    print("WSP81_HIDDEN_DEV_RESULT=" + canonical(report), flush=True)


if __name__ == "__main__":
    main()
