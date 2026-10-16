"""F77 two-arrival frozen causal intervention feasibility — unregistered only.

Scientific diagnostic, not a learned model. An unfair offline oracle uses
synthetic answers only to classify already source-legal alternatives.
Actual online controls are frozen F60; no registered first use.
"""
from __future__ import annotations
import collections
import hashlib
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent

def gitblob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def load(name, path, expected):
    assert gitblob(path) == expected, ("F77_FROZEN_IDENTITY_DRIFT", name)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

assert gitblob(HERE / "prereg.json") == "ba33bb2622b10ccabb6ff81bd08f9b3651377db6"
F76 = load(
    "f77_immutable_two_arrival_source",
    HERE.parent / "20261016-y-f76" / "source.py",
    "5b8928b0399ce9f869854beadeab04b29c8703a5",
)
F71 = load(
    "f77_immutable_public_feature_source",
    HERE.parent / "20261016-y-f71" / "early_scheduler.py",
    "edddfedb04af27dac7332ca85cc742aef5772a4b",
)
F60 = F76.ACTION
PACK = F76.PACK
AUDIT = F76.AUDITOR

def one_override_trace(public, q, intervention_index, after):
    mem = ()
    trace = []
    for index, event in enumerate(public):
        fixed = F60._f60_step(mem, event, PACK)
        if index == intervention_index:
            legal = tuple(option[3] for option in F60.actions(mem, event, index, PACK))
            assert after in legal and after != fixed, "UNAUTHORIZED_COUNTERFACTUAL"
            mem = after
        else:
            mem = fixed
        F60._valid_memory(mem, PACK)
        trace.append(tuple(PACK.pack(*record).hex() for record in mem))
    claim = AUDIT.verify(public, q, trace)
    assert claim["prefixes"] == 72
    assert claim["max_payload_bytes"] <= 144
    assert PACK.solve(mem, q) == q["answer"], "UNJUSTIFIED_ORACLE_RESCUE"
    return True

def evaluate():
    experiment = json.loads((HERE / "prereg.json").read_text())
    cohort = experiment["unregistered_synthetic"]
    assert cohort["negative_seed_start"] == -4301
    assert cohort["negative_seed_last_inclusive"] == -4316
    assert cohort["families"] == [-2, -1]
    signatures = collections.defaultdict(collections.Counter)
    global_labels = collections.Counter()
    regime_labels = collections.defaultdict(collections.Counter)
    summaries = []
    all_candidates = 0

    for seed in range(-4301, -4317, -1):
        for family in (-2, -1):
            public, question, meta = F76.source(seed, family)
            assert len(public) == 72
            assert F76.BASE.public_witness(public, question) == {question["answer"]}
            regime = meta["arrival_regime"]
            memory = ()
            trace = []
            sample_counts = collections.Counter()
            earliest = None
            for i, event in enumerate(public):
                baseline, choices = F71.native_alternatives(memory, event, i)
                if choices:
                    control_terminal = F60._finish_fixed(
                        baseline, public[i + 1:], PACK
                    )
                    control_good = (
                        PACK.solve(control_terminal, question) == question["answer"]
                    )
                    for action, drop, after, features in choices:
                        assert len(features) == 12
                        terminal = F60._finish_fixed(after, public[i + 1:], PACK)
                        other_good = (
                            PACK.solve(terminal, question) == question["answer"]
                        )
                        if other_good and not control_good:
                            label = "beneficial"
                            if earliest is None:
                                earliest = (i, after)
                        elif control_good and not other_good:
                            label = "harmful"
                        else:
                            label = "neutral"
                        signature = tuple(round(float(v), 8) for v in features)
                        signatures[signature][label] += 1
                        sample_counts[label] += 1
                        regime_labels[regime][label] += 1
                        global_labels[label] += 1
                        all_candidates += 1
                memory = baseline
                F60._valid_memory(memory, PACK)
                trace.append(tuple(PACK.pack(*record).hex() for record in memory))
            causal = AUDIT.verify(public, question, trace)
            assert causal["prefixes"] == 72 and causal["max_payload_bytes"] <= 144
            frozen_correct = PACK.solve(memory, question) == question["answer"]
            certified = False
            if earliest:
                certified = one_override_trace(public, question, *earliest)
            if frozen_correct:
                assert earliest is None, "BENEFICIAL_OVERRIDE_WHEN_FIXED_SUCCEEDED"
            summaries.append(dict(
                seed=seed, family=family, regime=regime,
                kind=meta["question_type"],
                frozen_F60_correct=bool(frozen_correct),
                beneficial_legal_actions=sample_counts["beneficial"],
                harmful_legal_actions=sample_counts["harmful"],
                neutral_legal_actions=sample_counts["neutral"],
                earliest_beneficial_intervention_index=earliest[0] if earliest else None,
                earliest_beneficial_intervention_independently_verified=certified,
            ))
    conflicting = [
        counts for counts in signatures.values()
        if counts["beneficial"] and counts["harmful"]
    ]
    by_regime = {}
    for regime in ("original", "local_rotate4"):
        group = [r for r in summaries if r["regime"] == regime]
        assert len(group) == 16
        failed = [r for r in group if not r["frozen_F60_correct"]]
        rescue = [r for r in failed if r["earliest_beneficial_intervention_independently_verified"]]
        by_regime[regime] = dict(
            cases=len(group),
            frozen_F60_correct=sum(x["frozen_F60_correct"] for x in group),
            frozen_F60_failures=len(failed),
            independently_verified_one_step_rescues=len(rescue),
            one_step_unresolved_failures=len(failed) - len(rescue),
            eligible_alternative_label_counts=dict(regime_labels[regime]),
            by_question_type={
                kind: dict(
                    cases=sum(x["kind"] == kind for x in group),
                    frozen_F60_correct=sum(x["frozen_F60_correct"]
                                           for x in group if x["kind"] == kind),
                    rescued_failures=sum(x["earliest_beneficial_intervention_independently_verified"]
                                         for x in group if x["kind"] == kind),
                )
                for kind in sorted({x["kind"] for x in group})
            },
        )
    out = dict(
        schema="yggdrasil.f77.two-arrival-native-action-feasibility.synthetic.v1",
        stage="PREREGISTERED_SYNTHETIC_OFFLINE_UNFAIR_ORACLE",
        source_was_adaptively_selected_after_F75=True,
        cases=len(summaries),
        by_arrival_regime=by_regime,
        total_legal_alternative_candidates=all_candidates,
        candidate_labels=dict(global_labels),
        public_F71_12_feature_unique_signatures=len(signatures),
        conflicting_beneficial_harmful_feature_signatures=len(conflicting),
        beneficial_examples_with_a_harmful_identical_signature=sum(
            c["beneficial"] for c in conflicting
        ),
        independent_every_frozen_F60_prefix_audited=True,
        every_claimed_one_step_rescue_independently_audited=True,
        unfair_question_aware_oracle_is_NONCOMPETITIVE=True,
        learned_model_trained=False,
        scientific_improvement_qualified=False,
        FIT_TRAIN_used=False,
        FIT_VALIDATE_used=False,
        DIAG_used=False,
        ORIGINAL_used=False,
        F3=False,
        optimizer_promotion=False,
        rows=summaries,
    )
    assert len(summaries) == 32 and sum(global_labels.values()) == all_candidates
    print(json.dumps(out, sort_keys=True))

if __name__ == "__main__":
    assert sys.argv[1:] == ["--synthetic-only"]
    evaluate()
