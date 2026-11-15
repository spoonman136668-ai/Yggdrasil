#!/usr/bin/env python3
"""F38: source-exact CC0 two-hop composition with F34 direct bit weights.

DEV comparison only. The weights are a fixed membership filter, not trained
neural model parameters, a source for new facts, or a generalizing recipient.
"""
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path

from f26_semantic_association import NotAdmitted, qnum
from f34_direct_bitweights import DirectBitWeights, BITS, K, BYTES

HERE = Path(__file__).resolve().parent
POLICY = HERE / "f38_prereg.json"
OLD = HERE / "evidence/f32_source_snapshot.json"
NEW = HERE / "evidence/f35_source_depth2_snapshot.json"
SCHEMA = "yggdrasil.qtr01.f38.source-exact-direct-bit-depth2-composition-dev.v1"
FROZEN = "5a41908fdb5f00eaae4b5e192def521958f67dcc"
SHA_OLD = "e9ead9ac15e4ecbe4d99216cda43657e1aeb030d22f59fd852f8b99fa0d440eb"
SHA_NEW = "cf5ffeab63384a61e66e30930f16ce3af07df81cb28472b0142f7a5c6b673954"
ROOTS = ("Q5", "Q42")


def verified_sources(old=OLD, new=NEW, policy=POLICY):
    p = json.loads(Path(policy).read_text(encoding="utf-8"))
    if (p.get("schema") != SCHEMA
        or p.get("status") != "FROZEN_BEFORE_F38_CODE_OR_RESULT"
        or p.get("source_parent_commit") != "c72207a6077954128cef54ac201a8fac7f824def"
        or p.get("original_source_sha256") != SHA_OLD
        or p.get("extension_source_sha256") != SHA_NEW
        or p.get("original_fact_count") != 13
        or p.get("extension_fact_count") != 20
        or p.get("composed_witnessed_paths") != 20
        or p.get("composed_query_templates") != 4
        or p.get("fixed_bitweight_bits") != BITS or BITS != 512
        or p.get("fixed_bitweight_hashes") != K or K != 3
        or p.get("fixed_bitweight_bytes") != BYTES or BYTES != 64
        or p.get("fixed_root_ids") != list(ROOTS)
        or p.get("go_thresholds", {}).get("bitweight_twohop_fpr_max") != 0.05
        or p.get("go_thresholds", {}).get("bitweight_twohop_recall_min") != 1.0
        or any(p.get("fences", {}).get(x) is not True for x in (
            "source_free_execution","no_external_source_calls",
            "no_donor_or_chatgpt_model_training_data", "no_neural_recipient_weights",
            "no_trainable_conventional_or_native_model_claim", "no_protected_first_use",
            "no_main_or_accepted_refs","no_merge","no_controller_or_scheduled_task",
            "no_paid_api","no_user_library_artifact"))):
        raise NotAdmitted("F38_PROTOCOL_DRIFT")
    raw0 = Path(old).read_bytes()
    raw1 = Path(new).read_bytes()
    if hashlib.sha256(raw0).hexdigest() != SHA_OLD or hashlib.sha256(raw1).hexdigest() != SHA_NEW:
        raise NotAdmitted("F38_EXACT_SOURCE_SHA_MISMATCH")
    d0, d1 = json.loads(raw0), json.loads(raw1)
    if (d0.get("schema") != "yggdrasil.qtr01.f31.first-party-all-language-fact-custody.v1"
        or d1.get("schema") != "yggdrasil.qtr01.f35.pinned-witnessed-depth2-source-dev.v1"
        or d0.get("scientific_pass") is not False
        or d1.get("scientific_pass") is not False
        or d0.get("native_recipient_model_weights_edited") is not False
        or d1.get("no_native_model_edits") is not True
        or d1.get("source_subjects_fully_pinned") is not True
        or d1.get("original_snapshot_rows_unchanged") is not True
        or d1.get("original_source_snapshot_sha256") != SHA_OLD
        or d1.get("composition", {}).get("real_twohop_paths") != 20
        or d1.get("composition", {}).get("real_twohop_queries") != 4):
        raise NotAdmitted("F38_ARCHIVE_CUSTODY_MISMATCH")
    first = d0.get("typed_source_rows")
    second = d1.get("added_witnessed_source_rows")
    if type(first) is not list or len(first) != 13 or type(second) is not list or len(second) != 20:
        raise NotAdmitted("F38_SOURCE_TRIPLES_COUNT_DRIFT")
    seen = set()
    for row in first + second:
        if (type(row) is not dict
            or any(type(row.get(k)) is not str or not row[k] for k in (
                "s", "p", "o", "s_label", "p_label", "o_label",
                "s_language", "p_language", "o_language", "source_claim"))
            or type(row.get("source_revision")) is not int
            or row["source_revision"] <= 0
            or not row["source_claim"].startswith(row["s"]+"$")):
            raise NotAdmitted("F38_SOURCE_WITNESS_OR_LANGUAGE_MISSING")
        triple = (qnum(row["s"], "Q"), qnum(row["p"], "P"), qnum(row["o"], "Q"))
        if triple in seen:
            raise NotAdmitted("F38_DUPLICATED_SOURCE_TRIPLE")
        seen.add(triple)
    a = sorted((qnum(r["s"], "Q"), qnum(r["p"], "P"), qnum(r["o"], "Q")) for r in first)
    b = sorted((qnum(r["s"], "Q"), qnum(r["p"], "P"), qnum(r["o"], "Q")) for r in second)
    return p, a, b


def exact_source_paths(triples):
    by_subject = defaultdict(list)
    for s, p, o in triples:
        by_subject[s].append((p, o))
    paths = set()
    for s, p1, mid in triples:
        for p2, target in by_subject.get(mid, ()):
            paths.add((s, p1, mid, p2, target))
    return paths


def exact_answer_set(triples, roots, predicates, nodes):
    by_sp = defaultdict(set)
    for s, p, o in triples:
        by_sp[(s, p)].add(o)
    answers = set()
    for s, p1, p2 in itertools.product(roots, predicates, predicates):
        for mid in by_sp.get((s, p1), ()):
            for target in by_sp.get((mid, p2), ()):
                if target in nodes:
                    answers.add((s, p1, p2, target))
    return answers


def bit_answer_set(weight, roots, predicates, nodes):
    # Only the vocabulary of IDs is provided; the bit representation has no
    # edge list, and no original rows are consulted during this composition.
    answers = set()
    first_edges = {}
    for s, p1 in itertools.product(roots, predicates):
        first_edges[(s, p1)] = tuple(mid for mid in nodes if weight.contains((s, p1, mid)))
    second_edges = {}
    for mid, p2 in itertools.product(nodes, predicates):
        second_edges[(mid, p2)] = tuple(target for target in nodes if weight.contains((mid, p2, target)))
    for s, p1, p2 in itertools.product(roots, predicates, predicates):
        for mid in first_edges[(s, p1)]:
            for target in second_edges[(mid, p2)]:
                answers.add((s, p1, p2, target))
    return answers


def shuffled_control(old, additions):
    # Synthetic-only non-fact control: deterministic one-position rotation of
    # all second-stage objects, never promoted to first-party factual claims.
    return [(s, p, additions[(i + 1) % len(additions)][2])
            for i, (s, p, _) in enumerate(additions)]


def evaluate():
    p, old, additions = verified_sources()
    graph = old + additions
    original_paths = exact_source_paths(old)
    merged_paths = exact_source_paths(graph)
    if original_paths or len(merged_paths) != 20:
        raise NotAdmitted("F38_SOURCE_PATH_COUNT_DRIFT")
    nodes = tuple(sorted({x for s, _, o in graph for x in (s, o)}))
    predicates = tuple(sorted({p for _, p, _ in graph}))
    roots = tuple(qnum(r, "Q") for r in ROOTS)
    domain_size = len(roots) * len(predicates) ** 2 * len(nodes)
    truth = exact_answer_set(graph, roots, predicates, nodes)
    templates = {(s, p1, p2) for s, p1, p2, _ in truth}
    if len(templates) != 4:
        raise NotAdmitted("F38_SOURCE_QUERY_TEMPLATE_DRIFT")
    exact_path_answers = {(s, p1, p2, target)
                          for s, p1, mid, p2, target in merged_paths if s in roots}
    if truth != exact_path_answers:
        raise NotAdmitted("F38_EXACT_SYMBOLIC_PATH_RECONSTRUCTION_DRIFT")

    direct = DirectBitWeights()
    for triple in old:
        direct.program(triple)
    old_snapshot = direct.snapshot()
    cold_old = DirectBitWeights(old_snapshot)
    if any(not direct.contains(t) or not cold_old.contains(t) for t in old):
        raise NotAdmitted("F38_OLD_COLD_SNAPSHOT_FAILURE")
    for triple in additions:
        direct.program(triple)
    final_snapshot = direct.snapshot()
    cold = DirectBitWeights(final_snapshot)
    retained = sum(direct.contains(x) and cold.contains(x) for x in old)
    new_hits = sum(direct.contains(x) and cold.contains(x) for x in additions)
    if final_snapshot != cold.snapshot() or retained != 13 or new_hits != 20:
        raise NotAdmitted("F38_ADD_OR_COLD_RESTORE_LOSS")
    predicted = bit_answer_set(direct, roots, predicates, nodes)
    restored = bit_answer_set(cold, roots, predicates, nodes)
    if predicted != restored:
        raise NotAdmitted("F38_COMPOSITION_COLD_DRIFT")
    tp = len(predicted & truth)
    fn = len(truth - predicted)
    fp = len(predicted - truth)
    tn = domain_size - len(truth) - fp
    if tn < 0 or tp + fn != len(truth):
        raise NotAdmitted("F38_QUERY_CONFUSION_MATRIX_INVALID")
    recall = tp/len(truth) if truth else 0.0
    precision = tp/(tp+fp) if tp+fp else 0.0
    fpr = fp/(domain_size - len(truth)) if domain_size > len(truth) else 0.0
    sham = exact_answer_set(old + shuffled_control(old, additions),
                            roots, predicates, nodes)
    if sham == truth:
        raise NotAdmitted("F38_SHUFFLED_OBJECT_NEGATIVE_INEFFECTIVE")
    passed = (len(truth) > 0 and fn == 0 and recall == 1.0 and fpr <= 0.05)
    return {
        "schema": SCHEMA, "classification": "DEV_DIRECT_BITWEIGHT_COMPOSITION_GO" if passed else "DEV_DIRECT_BITWEIGHT_COMPOSITION_NO_GO",
        "preregistered_commit": FROZEN,
        "source_f32_sha256": SHA_OLD, "source_f35_sha256": SHA_NEW,
        "original_source_facts": len(old), "new_source_facts": len(additions),
        "source_witnessed_twohop_paths": len(merged_paths),
        "source_positive_twohop_queries": len(truth),
        "source_positive_query_templates": len(templates),
        "candidate_node_count": len(nodes), "candidate_predicate_count": len(predicates),
        "candidate_query_count": domain_size,
        "old_positive_memberships_retained": retained,
        "new_positive_memberships_recognized": new_hits,
        "old_snapshot_bytes": len(old_snapshot), "direct_bit_payload_bytes": len(final_snapshot),
        "exact_sparse_triplet_coordinate_bytes": 12 * len(graph),
        "candidate_id_coordinate_lower_bound_bytes": 4 * (len(nodes) + len(predicates)),
        "direct_bit_true_positives": tp, "direct_bit_false_negatives": fn,
        "direct_bit_false_positives": fp, "direct_bit_true_negatives": tn,
        "direct_bit_twohop_precision": precision, "direct_bit_twohop_recall": recall,
        "direct_bit_twohop_false_positive_rate": fpr,
        "exact_symbolic_twohop_false_positives": 0, "exact_symbolic_twohop_false_negatives": 0,
        "exact_cold_bit_query_parity": True,
        "shuffled_endpoint_negative_changes_answers": True,
        "bitweight_cannot_enumerate_edges_without_candidate_ids": True,
        "source_labels_provenance_and_candidate_vocabulary_not_in_64B": True,
        "source_absent_query_not_global_falsehood": True,
        "neural_recipient_weights_edited": False,
        "trained_recipient_comparison_performed": False,
        "protected_scientific_first_use_consumed": False,
        "scientific_pass": False
    }


def main():
    report = evaluate()
    print("F38_SOURCE_EXACT_COMPOSITION_RESULT="+json.dumps(report, sort_keys=True, separators=(",", ":")))
    print("F38_SOURCE_ONLY_NO_NATIVE_LEARNING=PASS")


if __name__ == "__main__":
    main()
