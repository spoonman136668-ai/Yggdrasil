#!/usr/bin/env python3
"""F84-D4 source-native legal-action reachability witness on EXPOSED guard only.

A query/answer-aware offline oracle chooses ONLY F62's already-legal public
append/evict actions, never manufactures an arbitrary answer record. Each
transition is externally checked by the frozen independent prefix auditor.
This is a hindsight existence witness, NOT a causal online policy or eligible
experimental arm. All original/validation/FIT cohorts remain untouched.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
F84 = HERE / "forensic_reachability.py"
EXPOSED = range(-5121, -5137, -1)
FAMILIES = (-2, -1)


def load_f84():
    spec = importlib.util.spec_from_file_location("f84_original_exposed_reachability", F84)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def query_path_in_original_public(public, question):
    """Derive one full-history path from original public edges and sealed question.

    Information leakage is deliberate here and forbidden in any deployable
    memory action policy. The path is used to *search* for legal action traces;
    it is not inserted into memory.
    """
    ops = question["ops"]
    can_end = [set() for _ in range(len(ops)+1)]
    can_end[-1] = {question["answer"]}
    for step in range(len(ops)-1, -1, -1):
        role, direction = ops[step]
        for a,r,b in public:
            if r != role:
                continue
            source,target = (a,b) if direction == 1 else (b,a)
            if target in can_end[step+1]:
                can_end[step].add(source)
    assert question["start"] in can_end[0], "NO_FULL_PUBLIC_PATH"
    at = question["start"]
    path = []
    for step,(role,direction) in enumerate(ops):
        for edge in public:
            a,r,b = edge
            if r != role:
                continue
            source,target = (a,b) if direction == 1 else (b,a)
            if source == at and target in can_end[step+1]:
                path.append(edge)
                at = target
                break
        else:
            raise AssertionError("PATH_WITNESS_BROKEN")
    assert at == question["answer"]
    assert len(path) == len(ops)
    assert len(set(path)) == len(path), "REPEATED_PATH_EDGE_UNSUPPORTED"
    return tuple(path)


def query_aware_legal_append_witness(f, public, question):
    """Select only permitted native append/evict transitions, with hindsight.

    The first preference is maximal exact required-edge retention; the
    secondary preference cycles the oldest non-target raw events out of the
    twelve-record memory. All candidate states come from frozen F62.actions.
    """
    required = query_path_in_original_public(public, question)
    packing = f.M.PACK
    targets = frozenset(packing.edge_record(edge) for edge in required)
    assert len(targets) == len(required)
    order = {packing.edge_record(edge):i for i,edge in enumerate(public)}
    assert len(order) == len(public)
    memory = ()
    trace = []
    evictions = 0
    discarded_required = 0
    native_checks = 0
    for index,event in enumerate(public):
        candidates = f.M.F62.actions(memory, event, index, packing)
        # Never import a query-answer record as a native action.
        append_only = [c for c in candidates if c[0] == "append" and c[1] == -1]
        assert append_only, "NATIVE_APPEND_ACTION_NOT_REACHABLE"
        def key(candidate):
            after = candidate[3]
            retained = frozenset(after) & targets
            nonrequired_recency = sum(order.get(rec, -100000) for rec in after
                                      if rec not in targets)
            return len(retained), nonrequired_recency
        picked = max(enumerate(append_only), key=lambda p:(key(p[1]), -p[0]))[1]
        next_memory = picked[3]
        assert next_memory in {action[3] for action in candidates}
        assert picked[0] == "append"
        discarded_required += len((set(memory)&targets) - set(next_memory))
        evictions += int(picked[2] >= 0)
        f.M.F62._valid_memory(next_memory, packing)
        assert len(next_memory)*12 <= 144
        memory = next_memory
        trace.append(tuple(packing.pack(*r).hex() for r in memory))
        native_checks += 1
    assert native_checks == 72
    proof = f.M.AUDITOR.verify(public, question, tuple(trace))
    assert proof["prefixes"] == 72 and proof["max_payload_bytes"] <= 144
    assert tuple(packing.unpack(bytes.fromhex(x)) for x in trace[-1]) == memory
    assert packing.solve(memory, question) == proof["retained_question_prediction"]
    retained_targets = len(set(memory)&targets)
    solved = packing.solve(memory, question) == question["answer"]
    return dict(
        native_prefixes=72, max_payload_bytes=proof["max_payload_bytes"],
        target_edges=len(required), retained_raw_path_edges=retained_targets,
        dropped_target_events=discarded_required,
        native_append_eviction_count=evictions,
        query_aware_offline_oracle_correct=bool(solved),
        independent_prefix_action_and_public_witness_verified=True,
        query_and_future_leaked_into_action_selection=True,
        constructed_answer_record_injected=False,
        causal_online_learned_policy=False,
    )


def diagnostic():
    f84 = load_f84()
    frozen = f84.assert_frozen()
    assert len(frozen) == 24
    f = f84.load_f83()
    rows = []
    for seed in EXPOSED:
        for family in FAMILIES:
            public, question, meta = f.M.SOURCE.source(seed, family)
            if meta["question_type"] != "crosslink_reach_6_steps":
                continue
            full, _ = f84.independently_resolve_public(public, question)
            assert full == {question["answer"]}
            row = query_aware_legal_append_witness(f, public, question)
            row.update(seed=seed, family=family,
                       arrival_regime=meta["arrival_regime"],
                       question_type=meta["question_type"])
            rows.append(row)
    assert len(rows) == 8, "F83_CONSUMED_CROSSLINK_COHORT_DRIFT"
    native_rescued = sum(x["query_aware_offline_oracle_correct"] for x in rows)
    return dict(
        schema="yggdrasil.f84.legal-action-hindsight-reachability.v1",
        stage="ALREADY_EXPOSED_SYNTHETIC_FORENSICS_ONLY",
        exposed_six_step_cases=len(rows),
        legal_hindsight_reachable_cases=native_rescued,
        failure_to_find_is_not_proof_of_unreachability=True,
        legal_native_action_trace_checked_for_all_cases=True,
        independently_audited_prefixes=sum(x["native_prefixes"] for x in rows),
        query_aware_oracle_disallowed_online=True,
        equal_information_performance_claim=False,
        no_new_train_or_validation=True, no_original=True, no_DIAG=True,
        no_FIT=True, no_F3=True, no_optimizer_promotion=True,
        rows=rows,
    )


if __name__ == "__main__":
    if sys.argv[1:] != ["--already-exposed-synthetic-only"]:
        raise SystemExit("F84 D4 only permits consumed F83 negative synthetic guard")
    print(json.dumps(diagnostic(), sort_keys=True))
