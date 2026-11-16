"""NKR-11: source-held-out, subject-disjoint rule transfer diagnostic.

Engineering/dev audit of the PREVIOUSLY CONSUMED historical TRAIN graph.
No protected original labels, no causal knowledge claim, no accepted weights.
The predictor is only given (subject, target P); direct target objects are
an evaluator-only observation and never passed to model readout.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import json
import time

from yggdrasil.native_knowledge_activation import (
    PINNED_PACKED_SHA, PINNED_ROWS, PINNED_TRAIN_SHA, open_installed_session,
)

MAX_ANCHORS = 65_536
MAX_EDGES = 8
MAX_JOINS = 4_194_304
MAX_KEYS = 4_096
MAX_RULES = 128
MAX_PROPOSALS = 256
MIN_SUPPORT = 6
MAX_SECONDS = 180.0


def _row(w, i):
    triple = w.row_at(i)
    if (not isinstance(triple, (tuple, list)) or len(triple) != 3
            or any(type(x) is not int or not 1 <= x <= 0xffffffff
                   for x in triple)):
        raise ValueError("NKR11_UNTYPED_SOURCE_TRIPLE")
    return tuple(triple)


def _anchors(n):
    if type(n) is not int or n < 1:
        raise ValueError("NKR11_EMPTY_SOURCE")
    k = min(MAX_ANCHORS, n)
    if k == 1:
        return (0,)
    return tuple(i * (n - 1) // (k - 1) for i in range(k))


def _bucket(subject):
    if type(subject) is not int or not 1 <= subject <= 0xffffffff:
        raise ValueError("NKR11_SUBJECT_TYPE")
    return hashlib.sha256(
        ("nkr11-subject-v1:" + str(subject)).encode("ascii")
    ).digest()[0] % 4


def _source_outgoing(w):
    """Bounded sorted outgoing rows for *training mining only*.

    This source adapter is not given to prediction. Prediction may retrieve
    only (s,p1) and (mid,p2) from selected rules, never the target (s,p3).
    """
    n = len(w)

    @lru_cache(maxsize=65_536)
    def outgoing(subject):
        lo, hi = 0, n
        while lo < hi:
            mid = (lo + hi) // 2
            if _row(w, mid)[0] < subject:
                lo = mid + 1
            else:
                hi = mid
        out = []
        while lo < n and len(out) < MAX_EDGES:
            s, p, o = _row(w, lo)
            if s != subject:
                break
            out.append((p, o))
            lo += 1
        return tuple(out)

    return outgoing


def _mine_training(w, train, deadline):
    outgoing = _source_outgoing(w)
    support = defaultdict(set)
    freq = defaultdict(Counter)
    seen_train = set()
    joins = 0
    for n, (s, p3, z) in enumerate(train):
        if n % 128 == 0 and time.monotonic() > deadline:
            raise TimeoutError("NKR11_BUDGET_WALL")
        if (s, p3, z) in seen_train:
            continue
        seen_train.add((s, p3, z))
        freq[p3][z] += 1
        for p1, mid in outgoing(s):
            if p1 == p3:
                continue
            for p2, z2 in outgoing(mid):
                joins += 1
                if joins > MAX_JOINS:
                    raise ValueError("NKR11_JOIN_BUDGET")
                if p2 == p3 or z2 != z:
                    continue
                support[(p3, p1, p2)].add(s)
                if len(support) > MAX_KEYS:
                    raise ValueError("NKR11_RULE_KEY_BUDGET")
    rules = sorted(
        ([*key, len(subjects)] for key, subjects in support.items()
         if len(subjects) >= MIN_SUPPORT),
        key=lambda x: (-x[3], x[0], x[1], x[2]),
    )[:MAX_RULES]
    prior = {
        p: [obj for obj, count in sorted(
            counts.items(), key=lambda x: (-x[1], x[0]))[:10]]
        for p, counts in freq.items()
    }
    return rules, prior, joins


def _independent_fit(w, train, deadline):
    """Independent set-based exact symbolic rule learner, not NKR-10 miner."""
    outgoing = _source_outgoing(w)
    quadruples = set()
    for i, (s, p3, z) in enumerate(train):
        if i % 128 == 0 and time.monotonic() > deadline:
            raise TimeoutError("NKR11_REFERENCE_WALL")
        for p1, mid in outgoing(s):
            if p1 == p3:
                continue
            for p2, obj in outgoing(mid):
                if p2 != p3 and obj == z:
                    quadruples.add((s, p3, p1, p2))
    counts = Counter((p3, p1, p2) for _, p3, p1, p2 in quadruples)
    return sorted(
        ([*key, amount] for key, amount in counts.items()
         if amount >= MIN_SUPPORT),
        key=lambda x: (-x[3], x[0], x[1], x[2]),
    )[:MAX_RULES]


def _native_predict(w, subject, target_relation, rules):
    """Rule-transfer readout: never retrieves direct target-relation objects."""
    ranked = {}
    for p3, p1, p2, strength in rules:
        if p3 != target_relation:
            continue
        if p1 == target_relation or p2 == target_relation:
            raise AssertionError("NKR11_TARGET_PASSED_TO_PREDICTOR")
        for mid in w.objects(subject, p1, limit=MAX_EDGES):
            for obj in w.objects(mid, p2, limit=MAX_EDGES):
                ranked[obj] = max(ranked.get(obj, 0), strength)
                if len(ranked) > MAX_PROPOSALS:
                    raise ValueError("NKR11_HYPOTHESIS_BUDGET")
    return [obj for obj, strength in sorted(
        ranked.items(), key=lambda x: (-x[1], x[0]))[:10]]


def _symbolic_predict(w, subject, target_relation, rules):
    """Independent readout using a per-object multiset of path weights."""
    independently_grouped = defaultdict(list)
    for row in rules:
        if row[0] != target_relation:
            continue
        first, second, evidence = row[1], row[2], row[3]
        if first == target_relation or second == target_relation:
            raise AssertionError("NKR11_CONTROL_TARGET_READ")
        neighbors = w.objects(subject, first, limit=MAX_EDGES)
        for intermediate in neighbors:
            targets = w.objects(intermediate, second, limit=MAX_EDGES)
            for destination in targets:
                independently_grouped[destination].append(evidence)
    if len(independently_grouped) > MAX_PROPOSALS:
        raise ValueError("NKR11_SYMBOLIC_HYPOTHESIS_BUDGET")
    return sorted(
        independently_grouped,
        key=lambda obj: (-max(independently_grouped[obj]), obj)
    )[:10]


def run_dev(w, *, max_seconds=MAX_SECONDS):
    """Frozen source-safe diagnostic; all eligible and abstaining groups count."""
    if type(max_seconds) not in (float, int) or not 0 < max_seconds <= MAX_SECONDS:
        raise ValueError("NKR11_WALL_LIMIT_INVALID")
    start = time.monotonic()
    deadline = start + max_seconds
    indices = _anchors(len(w))
    train = []
    cold = defaultdict(set)
    previous = None
    train_subjects = set()
    cold_subjects = set()
    for i, index in enumerate(indices):
        if i % 256 == 0 and time.monotonic() > deadline:
            raise TimeoutError("NKR11_SOURCE_SCAN_WALL")
        s, p3, z = _row(w, index)
        if previous is not None and (s, p3, z) < previous:
            raise ValueError("NKR11_IMAGE_NOT_SORTED")
        previous = (s, p3, z)
        if _bucket(s) == 0:
            cold[(s, p3)].add(z)  # evaluator ONLY, never predictor argument
            cold_subjects.add(s)
        else:
            train.append((s, p3, z))
            train_subjects.add(s)
    if train_subjects & cold_subjects:
        raise AssertionError("NKR11_SUBJECT_LEAK")
    rules, frequency_prior, joins = _mine_training(w, train, deadline)
    exact_control = _independent_fit(w, train, deadline)
    if rules != exact_control:
        raise AssertionError("NKR11_FITTED_SYMBOLIC_MISMATCH")
    count = len(cold)
    covered = 0
    native1 = native10 = symbolic10 = baseline10 = 0
    native_minus_prior_wins = prior_minus_native_wins = 0
    predicted_proposals = 0
    first_query = time.monotonic()
    for i, ((subject, p3), hidden_targets) in enumerate(sorted(cold.items())):
        if i % 128 == 0 and time.monotonic() > deadline:
            raise TimeoutError("NKR11_EVALUATION_WALL")
        # Target objects live exclusively in hidden_targets and are never
        # passed to either prediction function.
        proposal = _native_predict(w, subject, p3, rules)
        symbolic = _symbolic_predict(w, subject, p3, exact_control)
        if proposal != symbolic:
            raise AssertionError("NKR11_EXACT_SYMBOLIC_READOUT_MISMATCH")
        if proposal:
            covered += 1
            predicted_proposals += len(proposal)
        n1 = bool(proposal[:1] and proposal[0] in hidden_targets)
        n10 = any(obj in hidden_targets for obj in proposal)
        b10 = any(obj in hidden_targets for obj in frequency_prior.get(p3, ()))
        native1 += n1
        native10 += n10
        symbolic10 += any(obj in hidden_targets for obj in symbolic)
        baseline10 += b10
        native_minus_prior_wins += (n10 and not b10)
        prior_minus_native_wins += (b10 and not n10)
    query_wall = time.monotonic() - first_query
    if time.monotonic() > deadline:
        raise TimeoutError("NKR11_TOTAL_BUDGET_WALL")
    if (native10 != symbolic10 or native_minus_prior_wins -
            prior_minus_native_wins != native10 - baseline10):
        raise AssertionError("NKR11_PAIRED_SCORE_INCONSISTENT")
    return {
        "schema":"yggdrasil.nkr11.cross-subject-transfer-development-result.v1",
        "classification":"HISTORICAL_TRAIN_SUBJECT_DISJOINT_DEV_ONLY",
        "sampled_anchor_rows":len(indices),
        "distinct_train_subjects":len(train_subjects),
        "distinct_heldout_subjects":len(cold_subjects),
        "train_anchor_rows":len(train),
        "heldout_positive_groups":count,
        "training_join_witnesses":joins,
        "rule_templates_selected":len(rules),
        "selected_rules_p3_p1_p2_support":rules,
        "heldout_covered_groups":covered,
        "all_heldout_hits1":int(native1),
        "all_heldout_hits10":int(native10),
        "symbolic_hits10":int(symbolic10),
        "frequency_hits10":int(baseline10),
        "native_win_prior_loss":int(native_minus_prior_wins),
        "prior_win_native_loss":int(prior_minus_native_wins),
        "candidate_minus_frequency_pp":(100.0*(native10-baseline10)/count if count else 0.0),
        "all_heldout_recall10":(native10/count if count else 0.0),
        "conditional_covered_recall10":(native10/covered if covered else 0.0),
        "proposals_returned":predicted_proposals,
        "frozen_dev_threshold_pass":bool(
            count and covered>=64 and native10*10>=count
            and (native10-baseline10)*20>=count
        ),
        "frozen_threshold":"covered>=64 AND all-heldout-recall@10>=10pct AND gain-vs-frequency>=5pp",
        "source_mode":"PREVIOUSLY_CONSUMED_HISTORICAL_TRAIN",
        "original_scientific_first_use":False,
        "source_subjects_disjoint":True,
        "predictor_direct_target_labels_visible":False,
        "no_absent_edge_negatives":True,
        "verified_new_real_world_facts":0,
        "identified_causal_laws":0,
        "native_accepted":False,
        "scientific_pass":False,
        "query_wall_seconds":query_wall,
        "whole_dev_wall_seconds":time.monotonic()-start,
    }


def run_full_image(path):
    with open_installed_session(path) as session:
        w=session._weights
        if (len(w)!=PINNED_ROWS or
                w.manifest["packed_sha256"]!=PINNED_PACKED_SHA or
                w.manifest["source_train_sha256"]!=PINNED_TRAIN_SHA):
            raise ValueError("NKR11_SOURCE_PIN_DRIFT")
        before=(w.row_at(0),w.row_at(len(w)-1))
        result=run_dev(w)
        if before!=(w.row_at(0),w.row_at(len(w)-1)):
            raise AssertionError("NKR11_SOURCE_MUTATED")
        result.update({
            "historical_train_rows":PINNED_ROWS,
            "historical_image_sha256":PINNED_PACKED_SHA,
            "historical_train_sha256":PINNED_TRAIN_SHA,
            "original_historical_image_unchanged":True,
        })
        return result


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--installed-session",required=True)
    args=parser.parse_args()
    print("NKR11_HISTORICAL_TRANSFER="+json.dumps(
        run_full_image(args.installed_session),
        sort_keys=True,separators=(",",":")),flush=True)
