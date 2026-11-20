"""RD05 source-only retrospective exact-context support audit.

Independent regeneration of the two *already scored* RD04 synthetic sources.
No CAP04 model, control or owner is imported/trained and no novel source is used.
Frozen contract: RD05-FROZEN-RETROSPECTIVE-SUPPORT.md.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

SCHEMA = "yggdrasil.cap04.rd05.retrospective-context-support.v1"
SOURCES = ("cap04-rd04-source-a", "cap04-rd04-source-b")
EXPECTED_SOURCE = {
    SOURCES[0]: "a3a06178c1bc0955bb7e5258284aaaa90691c556cd832310d146373f703339be",
    SOURCES[1]: "4ed6c8044fa88c4667c3b6194c93f74480ed18462e9720b0e1dba9a718a7cdf3",
}
ARMS = ((0, 0), (0, 1), (1, 0), (1, 1))
SEGMENTS = {"a_first": (0, 64), "b_full": (64, 192),
            "b_scored": (96, 192), "a_return": (192, 256)}
N = 256
ROOT = Path(__file__).resolve().parents[4]
PREDICTOR_PATH = ROOT / "yggdrasil/native_predictive_state_split.py"
FROZEN_PROTOCOL = "research/contrib/chatgpt/YGG-CAP04/RD05-FROZEN-RETROSPECTIVE-SUPPORT.md"


def require(ok, tag):
    if not ok:
        raise ValueError("CAP04_RD05_" + tag)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def first_byte(s):
    return hashlib.sha256(s.encode("ascii")).digest()[0]


def source(name):
    """Independent transcription of already frozen RD04 public source law."""
    require(type(name) is str and name in SOURCES, "SOURCE")
    u, v, w = (first_byte(f"cap04/rd04/{name}/start/{i}") & 1
               for i in range(3))
    old_action = (0, 0)
    records = []
    for t in range(N):
        views = ((u, v), (v, w))
        current = ARMS[first_byte(f"cap04/rd04/{name}/{t}/action") & 3]
        s2 = first_byte(f"cap04/rd04/{name}/{t}/intermediate") & 1
        # Private law is exposed ONLY to post-hoc source auditor, never to
        # a learner or new trial. It exactly reproduces consumed RD04 data.
        y = s2 ^ old_action[int(name == SOURCES[1])] if 64 <= t < 192 else s2
        post = (v ^ current[0], s2, w ^ current[1])
        identifier = sha(f"cap04/rd04/{name}/witness/{t}".encode("ascii"))
        records.append({"id": identifier, "views": views, "action": current,
                        "s2": s2, "y": y, "post": post})
        u, v, w = post
        old_action = current
    require(len(records) == N and len({r["id"] for r in records}) == N,
            "WITNESS_IDS")
    require(sha(canonical(records)) == EXPECTED_SOURCE[name],
            "ORIGINAL_SOURCE_CHANGED")
    return tuple(records)


def keys(rows):
    """Only source-witnessed current public data and preceding chosen action."""
    out = []
    previous = (0, 0)
    for t, row in enumerate(rows):
        views = row["views"]
        require(views[0][1] == views[1][0], "PUBLIC_VIEW")
        st = (views[0][0], views[0][1], views[1][1])
        base = (st, row["action"], row["s2"])
        out.append((base, (base, previous), row["y"]))
        previous = row["action"]
    return tuple(out)


def structural_invariant():
    """AST inspection, not model import or learned-state invocation."""
    raw = PREDICTOR_PATH.read_bytes()
    tree = ast.parse(raw.decode("utf-8"), filename=str(PREDICTOR_PATH))
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)
               and n.name == "PredictiveStateSplit"]
    require(len(classes) == 1, "PREDICTOR_CLASS")
    cls = classes[0]
    methods = {n.name: n for n in cls.body
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    require({"_winner", "observe", "_estimate"} <= set(methods),
            "PREDICTOR_METHOD")
    winner = ast.unparse(methods["_winner"])
    observe = ast.unparse(methods["observe"])
    require("self.routing_mode == 'recent32'" in winner and
            "self._recent_gains[kind][f]" in winner and
            "self._evidence[kind][f]" in winner and
            "self._recent_gains[kind][feature]" in observe,
            "ROUTER_NOT_PINNED")
    # Both pooled and split count accumulation occurs outside the branch
    # that gates recent-evidence bookkeeping.
    last_pool = observe.rfind("self._pool[base_key] =")
    last_split = observe.rfind("self._split[key] =")
    recent_if = observe.find("if self.routing_mode == 'recent32':")
    assert last_pool >= 0 and last_split >= 0 and recent_if >= 0
    recent_end = observe.find("key = (kind, conditioned", recent_if)
    require(0 <= recent_if < recent_end < last_split < last_pool,
            "LIFETIME_ESTIMATOR_DRIFT")
    require("self._pool.clear" not in observe and
            "self._split.clear" not in observe and
            "self._pool = {}" not in observe and
            "self._split = {}" not in observe,
            "UNEXPECTED_COUNTER_RESET")
    return {"predictor_file_sha256": sha(raw),
            "recent32_selects_only": "winner_via_last32_prequential_gains",
            "pool_and_split_counters": "lifetime_no_reset_in_observe",
            "model_imported": False}


def support_report(name):
    rows = source(name)
    k = keys(rows)
    phase_unique = {}
    for phase, (a, b) in SEGMENTS.items():
        sample = k[a:b]
        phase_unique[phase] = {
            "events": b-a,
            "unique_base": len({z[0] for z in sample}),
            "unique_historical": len({z[1] for z in sample}),
        }

    prior_all, prior_a, prior_b = Counter(), Counter(), Counter()
    histories = []
    for t, (_, joint, _) in enumerate(k):
        if 96 <= t < 192:
            histories.append({"prior_all": prior_all[joint],
                              "prior_b": prior_b[joint],
                              "prior_a": prior_a[joint]})
        prior_all[joint] += 1
        if t < 64:
            prior_a[joint] += 1
        elif t < 192:
            prior_b[joint] += 1
    require(len(histories) == 96, "SUPPORT_CLOCK")
    support = {
        metric: {"zero_support_rows": sum(h[metric] == 0 for h in histories),
                 "total_prior_witnesses": sum(h[metric] for h in histories),
                 "mean_prior_witnesses": sum(h[metric] for h in histories)/96}
        for metric in ("prior_all", "prior_b", "prior_a")
    }

    A, B = defaultdict(set), defaultdict(set)
    for a,b,labels in ((0,64,A),(64,192,B)):
        for base,full,y in k[a:b]:
            labels[full].add(y)
    conflicting = {cell for cell in A.keys() & B.keys()
                   if any(a != b for a in A[cell] for b in B[cell])}
    contrasted_b_rows = sum(k[t][1] in conflicting
                            for t in range(96, 192))
    base_to_history = defaultdict(set)
    for t in range(96,192):
        base_to_history[k[t][0]].add(k[t][1][1])
    ambiguous_bases = {base for base, prev in base_to_history.items()
                       if len(prev) >= 2}
    alias_rows = sum(k[t][0] in ambiguous_bases for t in range(96,192))
    return {
        "schema": SCHEMA, "evidence_class": "RETROSPECTIVE_SYNTHETIC_ONLY",
        "source": name, "source_sha256": EXPECTED_SOURCE[name],
        "rows": N, "original_source_first_use": False,
        "scientific_pass": False, "accepted_model_updated": False,
        "base_key_capacity": 64, "historical_key_capacity": 256,
        "phase_unique": phase_unique, "b_scored_prior_support": support,
        "contradictory_a_b_exact_historical_keys": len(conflicting),
        "b_scored_rows_on_cross_phase_contradictory_keys": contrasted_b_rows,
        "b_scored_ambiguous_base_cells": len(ambiguous_bases),
        "b_scored_rows_with_ambiguous_current_base": alias_rows,
        "previous_pair_selections_historical_rd04": 0,
        "predictor_structure": structural_invariant(),
    }


def audit(raw):
    """Exact replay of known source and immutable count report."""
    require(type(raw) is bytes and len(raw) < 50000, "AUDIT_LIMIT")
    try:
        doc = json.loads(raw.decode("ascii"))
        require(type(doc) is dict and canonical(doc) == raw
                and doc["schema"] == SCHEMA
                and doc["evidence_class"] == "RETROSPECTIVE_SYNTHETIC_ONLY"
                and doc["original_source_first_use"] is False
                and doc["scientific_pass"] is False
                and doc["accepted_model_updated"] is False,
                "AUDIT_SCOPE")
        require(canonical(support_report(doc["source"])) == raw,
                "AUDIT_REPLAY")
        return {"source": doc["source"], "source_sha256": doc["source_sha256"],
                "receipt_sha256": sha(raw),
                "b_scored_prior_support": doc["b_scored_prior_support"],
                "phase_unique": doc["phase_unique"],
                "contradictory_a_b_exact_historical_keys":
                    doc["contradictory_a_b_exact_historical_keys"],
                "b_scored_rows_on_cross_phase_contradictory_keys":
                    doc["b_scored_rows_on_cross_phase_contradictory_keys"],
                "b_scored_ambiguous_base_cells":
                    doc["b_scored_ambiguous_base_cells"],
                "b_scored_rows_with_ambiguous_current_base":
                    doc["b_scored_rows_with_ambiguous_current_base"],
                "predictor_file_sha256":
                    doc["predictor_structure"]["predictor_file_sha256"],
                "scientific_pass": False}
    except (KeyError, ValueError, TypeError, IndexError, OverflowError,
            UnicodeError, ArithmeticError) as exc:
        raise ValueError("CAP04_RD05_AUDIT_INVALID") from exc


if __name__ == "__main__":
    for name in SOURCES:
        result = support_report(name)
        receipt = audit(canonical(result))
        print("CAP04_RD05_RETROSPECTIVE=" +
              canonical(receipt).decode("ascii"), flush=True)
