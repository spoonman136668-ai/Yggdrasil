#!/usr/bin/env python3
"""F84-D5 read-only post-result diagnosis of D4 solver interference.

Reports WHY an already-frozen D4 action sequence fails. No changes to D4
selector, no alternative choice/tuning, and no new science first use.
The question is deliberately visible for forensic labeling ONLY.
"""
from __future__ import annotations
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
D4_BLOB = "72e5c58be0c3df0b7972bb77a1284753d62fbf03"
F84_BLOB = "0465a0612640520a695a98a0d3fd7b255174142e"


def git_blob(p):
    b = p.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()


def load(name, path, expected):
    assert git_blob(path) == expected, ("FROZEN_READ_ONLY_METHOD_DRIFT", str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def unchanged_action_trace(d4, f, public, question):
    """Independently reproduce the exact D4 chosen candidate in each prefix."""
    packing = f.M.PACK
    targets = frozenset(packing.edge_record(edge)
                        for edge in d4.query_path_in_original_public(public, question))
    order = {packing.edge_record(edge): i for i, edge in enumerate(public)}
    memory = ()
    for index, event in enumerate(public):
        options = f.M.F62.actions(memory, event, index, packing)
        append_only = [x for x in options if x[0] == "append" and x[1] == -1]
        assert append_only
        def k(candidate):
            after = candidate[3]
            return (len(frozenset(after)&targets),
                    sum(order.get(rec, -100000) for rec in after if rec not in targets))
        item = max(enumerate(append_only),
                   key=lambda pair:(k(pair[1]), -pair[0]))[1]
        assert item[3] in {x[3] for x in options}
        memory = item[3]
    return memory, targets


def independent_solver_trace(codec, records, question):
    remaining = tuple(2*role+int(direction == -1)
                      for role,direction in question["ops"])
    at = question["start"]
    steps = []
    visited = set()
    while remaining:
        eligible = set()
        for record in records:
            for candidate in (record,codec.mirrored(record)):
                a,b,codes = candidate
                if a == at and tuple(remaining[:len(codes)]) == tuple(codes):
                    eligible.add(candidate)
        if len(eligible) != 1:
            return {"failure_kind":"missing" if not eligible else "ambiguous",
                    "unresolved_hops":len(remaining),"eligible_count":len(eligible),
                    "retained_records":len(records),"consumed_steps":len(steps)}
        a,at,codes = next(iter(eligible))
        remaining = remaining[len(codes):]
        if (at,remaining) in visited:
            return {"failure_kind":"cycle","retained_records":len(records),
                    "unresolved_hops":len(remaining),"eligible_count":len(eligible),
                    "consumed_steps":len(steps)}
        visited.add((at,remaining))
        steps.append(len(codes))
    return {"failure_kind":"none","retained_records":len(records),
            "unresolved_hops":0,"eligible_count":0,"consumed_steps":len(steps),
            "final_node":at}


def run():
    d4 = load("f84_d4_immutable_readonly", HERE/"native_legal_action_witness.py", D4_BLOB)
    f84 = load("f84_codec_immutable_readonly", HERE/"forensic_reachability.py", F84_BLOB)
    f84.assert_frozen()
    f = f84.load_f83()
    rows = []
    for seed in range(-5121, -5137, -1):
        for family in (-2,-1):
            public,q,meta = f.M.SOURCE.source(seed,family)
            if meta["question_type"] != "crosslink_reach_6_steps":
                continue
            original = d4.query_aware_legal_append_witness(f,public,q)
            memory,targets = unchanged_action_trace(d4,f,public,q)
            retained = frozenset(memory) & targets
            assert len(retained)==original["retained_raw_path_edges"]==6
            independent = independent_solver_trace(f.M.PACK,memory,q)
            reproduced = (f.M.PACK.solve(memory,q)==q["answer"])
            assert reproduced==original["query_aware_offline_oracle_correct"]
            assert (independent["failure_kind"]=="none")==reproduced
            target_only = f.M.PACK.solve(tuple(rec for rec in memory if rec in targets),q)
            assert target_only==q["answer"],"FROZEN_TARGET_ONLY_SOLVER_INVALID"
            assert f.M.AUDITOR.solve(memory,q)==f.M.PACK.solve(memory,q)
            rows.append(dict(seed=seed,family=family,
                observed_D4_solved=reproduced,
                isolated_target_path_solved=(target_only==q["answer"]),
                all_six_targets_present=True,
                off_target_final_records=len(memory)-len(retained),
                solver_analysis=independent))
    assert len(rows)==8
    assert sum(row["observed_D4_solved"] for row in rows)==5
    assert sum(not row["observed_D4_solved"] for row in rows)==3
    summary=collections.Counter(row["solver_analysis"]["failure_kind"] for row in rows)
    return dict(
        schema="yggdrasil.f84.d5-frozen-legal-trace-solver-forensics.v1",
        stage="POSTRESULT_EXPOSED_SYNTHETIC_READ_ONLY",
        d4_frozen_git_blob=D4_BLOB, f84_frozen_git_blob=F84_BLOB,
        cases=8, all_six_legal_raw_path_edges_present=8,
        target_only_solver_correct=8,
        legal_action_trace_solver_correct=5,
        failed_full_state_solver_cases=3,
        failure_kinds=dict(summary),
        no_source_or_policy_mutation=True,
        no_new_science_first_use=True,
        no_optimizer_promotion=True,
        no_FIT=True,no_DIAG=True,no_original=True,no_F3=True,
        rows=rows)


if __name__=="__main__":
    if sys.argv[1:]!=["--frozen-exposed-d4-only"]:
        raise SystemExit("F84 D5 requires already-observed D4 frozen synthetic")
    print(json.dumps(run(),sort_keys=True))
