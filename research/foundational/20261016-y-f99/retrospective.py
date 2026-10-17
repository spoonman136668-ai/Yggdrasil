#!/usr/bin/env python3
"""F99 retrospective-only native closure feasibility on *retired* F76 cohorts.

No first-use source, model fitting, online selector, or execution authority.
The eventual question/answer is passed only to the separate outcome auditor,
AFTER all query-blind native prefix decisions and counterfactuals are frozen.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parent
PREREG_SHA = "9abcfbde16137d15248e8ce1229660a46b853dc1"
F99_SHA = "5de08fe74eb74dd917a7559cc3a8755185aac823"
F94_SHA = "0284a3ed1cd5f263dc4ad7cf3f3f21969bb665ad"
F96_SHA = "2cf14367527c9790661af65a84d15cbe11132bc7"
F98_HOLDOUT_SHA = "be61a466d7e1eafd635e2ebc31a4c103444aec02"
F76_SHA = "5b8928b0399ce9f869854beadeab04b29c8703a5"
F62_SHA = "7ed72deca5584d7c0b6562d74456fa7d4bee6712"
F85_SHA = "e4eb4bfbd6a01212f8c1eebc38af09b15c6d9cc3"
FAMILIES = (-2, -1)
# These ranges were irrevocably consumed by F93B/F94, F96 or F98.
RETIRED = {
    "f93b_guard": (-6041, -6057, False, 32),
    "f96_holdout": (-6241, -6257, True, 64),
    "f98_validation": (-6421, -6429, True, 32),
    "f98_guard": (-6441, -6457, True, 64),
}
FOUR = "within_component_4_steps"
SIX = "crosslink_reach_6_steps"


def git_blob(path):
    raw = Path(path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def load_checked(name, path, sha):
    if git_blob(path) != sha:
        raise AssertionError("F99_FROZEN_SOURCE_DRIFT:" + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def assert_retired_source(mode, seed, family, arrival):
    start, stop, paired, _ = RETIRED[mode]
    if type(seed) is not int or type(family) is not int or \
            seed not in range(start, stop, -1) or family not in FAMILIES:
        raise ValueError("F99_UNREGISTERED_SOURCE_DENIED")
    if arrival not in ("original", "local_rotate4"):
        raise ValueError("F99_ARRIVAL_DENIED")
    if not paired and arrival != ("original" if family == -2 else "local_rotate4"):
        raise ValueError("F99_HISTORICAL_TREATMENT_DENIED")


def dependencies():
    # Exact immutable historical methods, without invoking cohort generation.
    for rel, sha in (
        ("20261016-y-f94/single_deviation_feasibility.py", F94_SHA),
        ("20261016-y-f96/paired_order_probe.py", F96_SHA),
        ("20261016-y-f98/holdout.py", F98_HOLDOUT_SHA),
        ("20261016-y-f76/source.py", F76_SHA),
        ("20261015-y-f62/source_pilot.py", F62_SHA),
        ("20261016-y-f85/global_solver.py", F85_SHA),
    ):
        if git_blob(ROOT / rel) != sha:
            raise AssertionError("F99_HISTORICAL_DEPENDENCY_DRIFT:" + rel)
    if git_blob(P / "prereg.json") != PREREG_SHA:
        raise AssertionError("F99_PREREG_DRIFT")
    C = load_checked("f99_retired_exact_closure", P / "causal_closure.py", F99_SHA)
    F97, F96, F83, F84, F85, F62, pack = C.frozen_dependencies()
    assert F83.M.SOURCE is not None and pack is not None
    assert F62.CAP * F62.RECORD_BYTES == 144
    return C, F96, F83, F84, F85, F62, pack


def prepare_public_prefixes(public, C, native, pack):
    """Causal prefix-only action/closure preparation; NO question or answer.

    All future source events are used only afterwards by the separate fixed
    suffix evaluator. The live online action/closure checks see current
    event, previous baseline native memory, and exact index only.
    """
    if len(public) != 72 or any(len(event) != 3 for event in public):
        raise ValueError("F99_PUBLIC_PREFIX_LENGTH")
    memory = ()
    trace = []
    alternatives = []
    counts = dict(public_prefixes=0, native_alternatives=0,
                  source_resource_ineligible=0, closure_preserving=0,
                  closure_eligible=0)
    for index, event in enumerate(public):
        baseline = native._f60_step(memory, event, pack)
        actions = native.actions(memory, event, index, pack)
        if sum(1 for action in actions if action[3] == baseline) != 1:
            raise AssertionError("F99_F60_NATIVE_PARITY")
        native._valid_memory(baseline, pack)
        if len(baseline) > 12:
            raise AssertionError("F99_NATIVE_CAP")
        if index < 48:
            for action_index, action in enumerate(actions):
                after = action[3]
                if after == baseline:
                    continue
                native._valid_memory(after, pack)
                if sum(len(pack.pack(*rec)) for rec in after) > 144:
                    raise AssertionError("F99_NATIVE_BYTE_CAP")
                counts["native_alternatives"] += 1
                try:
                    comp = C.eligible_closure(baseline, after)
                except C.ClosureLimitExceeded:
                    counts["source_resource_ineligible"] += 1
                    continue
                if not comp["short_signatures_preserved"]:
                    continue
                counts["closure_preserving"] += 1
                counts["closure_eligible"] += int(comp["eligible"])
                alternatives.append((index, action_index, after, comp))
        trace.append(tuple(pack.pack(*rec).hex() for rec in baseline))
        memory = baseline
        counts["public_prefixes"] += 1
    assert len(trace) == counts["public_prefixes"] == 72
    assert len(memory) <= 12
    return memory, tuple(trace), tuple(alternatives), counts


def audit_offline_outcomes(prepared, public, question, F85, native, pack):
    """Offline ONLY: eventual question and future suffix never select actions."""
    baseline, trace, candidates, counts = prepared
    qonly = {"start": question["start"], "ops": question["ops"]}
    base_prediction, base_diag = F85.solve_global(baseline, qonly, pack)
    if base_diag["resource_cap_triggered"] or base_diag["persistent_memory_bytes"] > 144:
        raise AssertionError("F99_F85_BASELINE_RESOURCE_LIMIT")
    if base_prediction not in (None, question["answer"]):
        raise AssertionError("F99_NONPUBLIC_BASELINE_ANSWER")
    baseline_correct = base_prediction == question["answer"]
    scores = dict(counts)
    scores.update(f60_correct=int(baseline_correct), eligible_rescue_actions=0,
                  closure_preserving_harm_actions=0, eligible_harm_actions=0,
                  candidate_f85_audits=0)
    for index, action_index, after, comparison in candidates:
        terminal = native._finish_fixed(after, public[index + 1:], pack)
        native._valid_memory(terminal, pack)
        prediction, diag = F85.solve_global(terminal, qonly, pack)
        if diag["resource_cap_triggered"] or diag["persistent_memory_bytes"] > 144:
            raise AssertionError("F99_F85_COUNTERFACTUAL_RESOURCE_LIMIT")
        if prediction not in (None, question["answer"]):
            raise AssertionError("F99_NONPUBLIC_COUNTERFACTUAL_ANSWER")
        correct = prediction == question["answer"]
        scores["candidate_f85_audits"] += 1
        scores["eligible_rescue_actions"] += int(
            comparison["eligible"] and not baseline_correct and correct)
        scores["closure_preserving_harm_actions"] += int(
            baseline_correct and not correct)
        scores["eligible_harm_actions"] += int(
            comparison["eligible"] and baseline_correct and not correct)
    return scores


def summarize(rows):
    """Fixed preregistered rule. No threshold fitting or retrospective tuning."""
    if not rows:
        raise ValueError("F99_EMPTY_RETROSPECTIVE")
    def sums(subset):
        return dict(episodes=len(subset),
                    f60_correct=sum(r["f60_correct"] for r in subset),
                    native_alternatives=sum(r["native_alternatives"] for r in subset),
                    closure_preserving=sum(r["closure_preserving"] for r in subset),
                    closure_eligible=sum(r["closure_eligible"] for r in subset),
                    eligible_rescue_actions=sum(r["eligible_rescue_actions"] for r in subset),
                    closure_preserving_harm_actions=sum(
                        r["closure_preserving_harm_actions"] for r in subset),
                    eligible_harm_actions=sum(r["eligible_harm_actions"] for r in subset),
                    source_resource_ineligible=sum(
                        r["source_resource_ineligible"] for r in subset))
    overall = sums(rows)
    six = [r for r in rows if r["kind"] == SIX]
    four = [r for r in rows if r["kind"] == FOUR]
    witness = sum(r["f60_correct"] == 0 and
                  r["eligible_rescue_actions"] > 0 for r in six)
    resource = overall["source_resource_ineligible"]
    classification = ("SOURCE_RESOURCE_INELIGIBLE" if resource else
                      "RETROSPECTIVE_FEASIBLE_ONLY" if witness else
                      "RETROSPECTIVE_NO_WITNESS")
    return dict(classification=classification,
                six_step_failed_episodes_rescuable=witness,
                overall=overall, six_step=sums(six), four_step=sums(four),
                by_order={order: sums([r for r in rows if r["arrival"] == order])
                          for order in ("original", "local_rotate4")},
                by_cohort={mode: sums([r for r in rows if r["cohort"] == mode])
                           for mode in RETIRED})


def evaluate(mode):
    if mode not in RETIRED:
        raise ValueError("F99_CONSUMED_COHORT_ALLOWLIST")
    C, F96, F83, F84, F85, native, pack = dependencies()
    source = F83.M.SOURCE
    start, stop, paired, episodes = RETIRED[mode]
    rows = []
    for seed in range(start, stop, -1):
        for family in FAMILIES:
            observed, question, metadata = source.source(seed, family)
            original, rotated = F96.matched_orders(
                observed, metadata["arrival_regime"], source)
            if collections.Counter(original) != collections.Counter(rotated):
                raise AssertionError("F99_PAIRED_GRAPH_DRIFT")
            if len(original) != 72 or question["answer"] is None:
                raise AssertionError("F99_PAIRED_SOURCE_INVALID")
            orders = (("original", original), ("local_rotate4", rotated)) if paired else (
                (metadata["arrival_regime"], observed),)
            for arrival, public in orders:
                assert_retired_source(mode, seed, family, arrival)
                # Prepare all decisions and fixed alternatives before q is
                # passed to ANY offline scorer, solver or public audit.
                prepared = prepare_public_prefixes(public, C, native, pack)
                baseline, trace, alternatives, counts = prepared
                if baseline != F84.audit_f60(F83, public, question):
                    raise AssertionError("F99_FULL_F60_PARITY_DRIFT")
                independent = F83.M.AUDITOR.verify(public, question, trace)
                if independent["prefixes"] != 72 or independent["max_payload_bytes"] > 144:
                    raise AssertionError("F99_72_PREFIX_AUDIT_FAILURE")
                if F84.independently_resolve_public(public, question)[0] != frozenset(
                        {question["answer"]}):
                    raise AssertionError("F99_INDEPENDENT_PUBLIC_WITNESS_FAILED")
                scores = audit_offline_outcomes(
                    prepared, public, question, F85, native, pack)
                rows.append(dict(cohort=mode, seed=seed, family=family,
                                 arrival=arrival, kind=metadata["question_type"],
                                 **scores))
    if len(rows) != episodes:
        raise AssertionError("F99_CONSUMED_CASE_COUNT_DRIFT")
    summary = summarize(rows)
    return dict(schema="yggdrasil.f99.retired-closure-feasibility.v1",
                stage="CONSUMED_SOURCE_RETROSPECTIVE_ONLY_NOT_ACCEPTED",
                scope=mode, source_identity=dict(
                    f99_prereg_blob=PREREG_SHA, f99_closure_blob=F99_SHA,
                    f94_historical_blob=F94_SHA, f96_paired_blob=F96_SHA,
                    f98_holdout_blob=F98_HOLDOUT_SHA, f76_source_blob=F76_SHA,
                    f62_native_blob=F62_SHA, f85_solver_blob=F85_SHA),
                exact_native_72_prefixes=True, native_memory_limit_bytes=144,
                future_question_never_used_in_online_choice=True,
                paired_source_matches=True, fitting_executed=False,
                new_first_use=False, protected_FIT_DIAG_ORIGINAL_F3=False,
                valid_online_selector=False, scientific_accepted=False,
                optimizer_promotion=False, controller_mutation=False,
                **summary, rows=rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--consumed", choices=tuple(RETIRED), required=True)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.consumed), sort_keys=True))


if __name__ == "__main__":
    main()
