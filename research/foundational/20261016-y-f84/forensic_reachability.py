#!/usr/bin/env python3
"""F84 read-only hindsight and causal-baseline analysis on EXPOSED F83 guard.

This is a diagnostic on already-consumed synthetic negatives, NOT an independent
scientific experiment, a fitted policy, a new validation cohort, or an acceptance.
In particular, the query-aware single-record oracle deliberately leaks the
future question and answer; it is NEVER an admissible online model comparison.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
F83 = ROOT.parent / "20261016-y-f83"
EXPOSED_SEEDS = range(-5121, -5137, -1)
EXPOSED_FAMILIES = (-2, -1)
F83_METHOD_BLOB = "68138887c8bc42a17f8866df96cbede8e2594325"
F83_PREREG_BLOB = "2c47c4116bcad183ef2e3f327b9760b8ea95b3c1"
F83_FORENSIC_PREREG_BLOB = "9d4333afe6baf45025decf19e9cfad3319981a22"
DESIGN_BLOB = "9030779a855f241a090a2cba089c6ec979f300fa"


def blob(path):
    data = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(data)).encode() + b"\0" + data
    ).hexdigest()


def assert_frozen():
    assert blob(F83 / "pairwise_learner.py") == F83_METHOD_BLOB
    assert blob(F83 / "prereg.json") == F83_PREREG_BLOB
    assert blob(F83 / "forensic_prereg.json") == F83_FORENSIC_PREREG_BLOB
    assert blob(ROOT / "reachability-precode-advisory.json") == DESIGN_BLOB
    plan = json.loads((ROOT / "reachability-precode-advisory.json").read_text())
    assert plan["stage"] == "DIAGNOSTIC_DESIGN_NO_NEW_SEEDS_NO_RUN"
    assert plan["authority_flags"]["ORIGINAL"] is False
    frozen = json.loads((F83 / "forensic_prereg.json").read_text())
    weights = tuple(frozen["parents"]["frozen_weights"])
    assert len(weights) == 24
    assert hashlib.sha256(bytes(x % 256 for x in weights)).hexdigest() == (
        frozen["parents"]["weights_sha256"]
    )
    return weights


def load_f83():
    name = "f84_unchanged_f83_exposed_source"
    path = F83 / "pairwise_learner.py"
    assert blob(path) == F83_METHOD_BLOB
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def independently_resolve_public(public, question):
    """Fresh directed typed-edge adjacency evaluator, not SOURCE.public_witness."""
    assert len(public) == 72 and len(set(public)) == 72
    transitions = {}
    for left, role, right in public:
        assert 0 <= role <= 3
        transitions.setdefault((left, role, 1), set()).add(right)
        transitions.setdefault((right, role, -1), set()).add(left)
    frontier = {question["start"]}
    frontier_counts = [len(frontier)]
    for role, direction in question["ops"]:
        assert 0 <= role <= 3 and direction in (-1, 1)
        frontier = {
            target for state in frontier
            for target in transitions.get((state, role, direction), ())
        }
        frontier_counts.append(len(frontier))
    return frozenset(frontier), frontier_counts


def hindsight_encoded_path(question, codec):
    """Deliberate query-aware upper bound: not a causal/legal-action witness."""
    codes = tuple(2 * role + int(direction == -1)
                  for role, direction in question["ops"])
    assert len(codes) in (4, 6)
    record = (question["start"], question["answer"], codes)
    payload = codec.pack(*record)
    assert len(payload) == 12
    assert codec.unpack(payload) == record
    assert codec.solve((record,), question) == question["answer"]
    return record


def audit_f60(f, public, question):
    memory = ()
    trace = []
    for event in public:
        memory = f.M.F62._f60_step(memory, event, f.M.PACK)
        f.M.F62._valid_memory(memory, f.M.PACK)
        trace.append(tuple(f.M.PACK.pack(*r).hex() for r in memory))
    audit = f.M.AUDITOR.verify(public, question, tuple(trace))
    assert audit["prefixes"] == 72 and audit["max_payload_bytes"] <= 144
    assert memory == f.M.F62.controls()[0].online_fixed(public)
    return memory


def diagnostic():
    frozen = assert_frozen()
    f = load_f83()
    rows = []
    for seed in EXPOSED_SEEDS:
        for family in EXPOSED_FAMILIES:
            public, question, metadata = f.M.SOURCE.source(seed, family)
            assert metadata["question_type"] in (
                "crosslink_reach_6_steps", "within_component_4_steps"
            )
            full_answers, frontier_counts = independently_resolve_public(
                public, question
            )
            # Compare two separately implemented public answer evaluators.
            assert full_answers == frozenset({question["answer"]})
            assert full_answers == f.M.SOURCE.BASE.public_witness(public, question)
            oracle_record = hindsight_encoded_path(question, f.M.PACK)
            baseline = audit_f60(f, public, question)
            learned, learned_trace, _ = f.online(public, frozen, True, True)
            proof = f.M.AUDITOR.verify(public, question, learned_trace)
            assert proof["prefixes"] == 72 and proof["max_payload_bytes"] <= 144
            rows.append(dict(
                seed=seed, family=family,
                question_type=metadata["question_type"],
                arrival_regime=metadata["arrival_regime"],
                hops=len(question["ops"]),
                independent_full_history_unique=True,
                full_history_frontier_cardinalities=frontier_counts,
                hindsight_oracle_one_record_bytes=len(f.M.PACK.pack(*oracle_record)),
                hindsight_oracle_correct=True,
                hindsight_oracle_uses_future_question_and_answer=True,
                online_baseline_F60_correct=int(
                    f.M.PACK.solve(baseline, question) == question["answer"]
                ),
                online_F83_correct=int(
                    f.M.PACK.solve(learned, question) == question["answer"]
                ),
            ))
    assert len(rows) == 32
    assert sum(x["online_baseline_F60_correct"] for x in rows) == 19
    assert sum(x["online_F83_correct"] for x in rows) == 10
    cross = [x for x in rows if x["question_type"] == "crosslink_reach_6_steps"]
    assert len(cross) == 8
    assert all(x["hops"] == 6 for x in cross)
    assert all(x["online_baseline_F60_correct"] == 0
               and x["online_F83_correct"] == 0 for x in cross)
    assert all(x["hindsight_oracle_one_record_bytes"] == 12 for x in cross)
    return dict(
        schema="yggdrasil.f84.exposed-guard-reachability-forensics.v1",
        status="SOURCE_ONLY_READER_NOT_PROSPECTIVE_QUALIFICATION",
        exposed_guard_cases=32, six_step_cases=8,
        independent_full_public_unique_cases=32,
        six_step_query_aware_12_byte_encodable_cases=8,
        frozen_F60_six_step_correct=0,
        frozen_F83_six_step_correct=0,
        # This proves representation/codec capacity, NOT reachable causal actions.
        causal_legal_action_reachability_established=False,
        actual_trainable_online_policy_improvement_established=False,
        query_aware_oracle_is_not_equal_information_control=True,
        no_training=True, no_new_source_cases=True, no_original=True,
        no_DIAG=True, no_FIT=True, no_F3=True, no_optimizer_promotion=True,
        rows=rows
    )


if __name__ == "__main__":
    if sys.argv[1:] != ["--already-exposed-synthetic-only"]:
        raise SystemExit("F84: only exposed F83 synthetic guard forensics are permitted")
    print(json.dumps(diagnostic(), sort_keys=True))
