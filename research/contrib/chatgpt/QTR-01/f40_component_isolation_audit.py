#!/usr/bin/env python3
"""F40: inspect only already-archived CC0 graph identities and component leakage.

This is a post-hoc source-custody DEV audit. It cannot certify global historical
first-use, independent science, native learning, model weights, or transfer.
No HTTP, model calls, or protected evaluation data are accessed.
"""
import hashlib
import json
from pathlib import Path
import re
from collections import defaultdict

HERE = Path(__file__).resolve().parent
PREREG = HERE / "f40_prereg.json"
SCHEMA = "yggdrasil.qtr01.f40.archived-component-isolation-dev-audit.v1"
PREREG_COMMIT = "a0be13414884e6a10b0cbec5d1dccfa8c39f6715"
SHA256 = (
    "e9ead9ac15e4ecbe4d99216cda43657e1aeb030d22f59fd852f8b99fa0d440eb",
    "cf5ffeab63384a61e66e30930f16ce3af07df81cb28472b0142f7a5c6b673954",
    "7d223dcb9d9082059cdc237d7a551c2a3a0f21ca81824318bec1624aa25c4044",
)
NAMES = (
    "f32_source_snapshot.json",
    "f35_source_depth2_snapshot.json",
    "f39_fit_breadth_source_snapshot.json",
)
SCHEMAS = (
    "yggdrasil.qtr01.f31.first-party-all-language-fact-custody.v1",
    "yggdrasil.qtr01.f35.pinned-witnessed-depth2-source-dev.v1",
    "yggdrasil.qtr01.f39.prospective-breadth-source-fit-only.v1",
)
KEYS = ("typed_source_rows", "added_witnessed_source_rows", "witnessed_rows")
COUNTS = (13, 20, 49)
RESERVED = ("Q142", "Q183", "Q312", "Q1490")
FIT = ("Q2", "Q17", "Q30", "Q64", "Q76", "Q80", "Q90", "Q95")
QID = re.compile(r"Q[1-9][0-9]*")
PID = re.compile(r"P[1-9][0-9]*")


class NotAdmitted(ValueError):
    pass


def qnum(qid):
    if not QID.fullmatch(qid):
        raise NotAdmitted("F40_INVALID_QID")
    return int(qid[1:])


def preregistration(path=PREREG):
    p = json.loads(Path(path).read_text(encoding="utf-8"))
    if (p.get("schema") != SCHEMA
        or p.get("status") != "PREDECLARED_SOURCE_FREE_AUDIT_OF_ALREADY_OBSERVED_F32_F35_F39"
        or p.get("audit_parent_sha") != "b3fc3c9c9f5ec396e8df5923b7fd0b9de745cff6"
        or p.get("audit_classification") != "POST_HOC_KNOWN_ARCHIVE_AUDIT_NOT_INDEPENDENT_PROSPECTIVE_SCIENCE"
        or p.get("reserved_evaluation_root_ids") != list(RESERVED)
        or p.get("fit_roots") != list(FIT)
        or p.get("f39_prereg_blob") != "2f103d7c596d710c6060450ccbcf9a955f4bd7bd"
        or len(p.get("source_archives", [])) != 3
        or [(x.get("sha256"), x.get("expected_rows"), x.get("rows_key"))
            for x in p["source_archives"]] != list(zip(SHA256, COUNTS, KEYS))
        or p.get("known_historical_boundary", {}).get("legacy_consumed_source_ledger_complete") is not False
        or p.get("known_historical_boundary", {}).get("historical_first_use_status") != "UNVERIFIED_IN_THIS_AUDIT_NOT_A_GLOBAL_ADMISSION"
        or any(p.get("fences", {}).get(f) is not True for f in (
            "no_external_data_requests", "no_heldout_source_first_use",
            "no_training_or_model_weight_edits", "no_native_recipient_execution",
            "no_donor_model_calls", "no_source_recapture",
            "no_main_or_accepted_ref_changes", "no_merges",
            "no_new_scheduled_tasks_or_controller_actions", "no_paid_apis",
            "no_user_files"))):
        raise NotAdmitted("F40_FROZEN_SCOPE_OR_FIRST_USE_POLICY_DRIFT")
    return p


def read_archives(paths=None):
    if paths is None:
        paths = [HERE / "evidence" / n for n in NAMES]
    if len(paths) != 3:
        raise NotAdmitted("F40_EXPECTS_EXACT_THREE_ARCHIVES")
    docs = []
    for i, path in enumerate(paths):
        raw = Path(path).read_bytes()
        if hashlib.sha256(raw).hexdigest() != SHA256[i]:
            raise NotAdmitted("F40_ARCHIVED_SOURCE_HASH_MISMATCH")
        try:
            doc = json.loads(raw)
        except (UnicodeError, ValueError) as e:
            raise NotAdmitted("F40_SOURCE_JSON_INVALID") from e
        if (doc.get("schema") != SCHEMAS[i] or type(doc.get(KEYS[i])) is not list
            or len(doc[KEYS[i]]) != COUNTS[i]
            or doc.get("scientific_pass") is not False):
            raise NotAdmitted("F40_SOURCE_SCHEMA_SCOPE_OR_COUNT_DRIFT")
        docs.append(doc)
    return docs


def validate(docs):
    if len(docs) != 3:
        raise NotAdmitted("F40_WRONG_ARCHIVE_COUNT")
    if (docs[0].get("native_recipient_model_weights_edited") is not False
        or docs[1].get("no_native_model_edits") is not True
        or docs[2].get("native_model_weights_edited") is not False
        or docs[2].get("trained_conventional_or_native_baseline_run") is not False
        or docs[2].get("protected_scientific_first_use_consumed") is not False
        or docs[2].get("reserved_unseen_read_count") != 0
        or docs[2].get("source_http_get_count") != 86
        or type(docs[2].get("source_receipts")) is not list
        or len(docs[2]["source_receipts"]) != 86):
        raise NotAdmitted("F40_SOURCE_FIRST_USE_OR_PROVENANCE_FENCE_MISSING")
    groups = [docs[i][KEYS[i]] for i in range(3)]
    if any(type(g) is not list or len(g) != COUNTS[i] for i, g in enumerate(groups)):
        raise NotAdmitted("F40_SOURCE_ROWS_CHANGED")
    seen, normalized, group_keys = set(), [], []
    reserved = set(RESERVED)
    for i, rows in enumerate(groups):
        receipt_key = ("source_request_receipts", "read_only_first_party_receipts", "source_receipts")[i]
        receipts = docs[i].get(receipt_key)
        if type(receipts) is not list:
            raise NotAdmitted("F40_SOURCE_RECEIPT_MISSING")
        witness = set()
        for r in receipts:
            if (type(r) is not dict or type(r.get("entity")) is not str
                or type(r.get("revision")) is not int or r["revision"] <= 0):
                raise NotAdmitted("F40_BAD_RECEIPT_ENTITY_REVISION")
            if r["entity"] in reserved:
                raise NotAdmitted("F40_RESERVED_ROOT_REQUEST_RECEIPT_FOUND")
            witness.add((r["entity"], r["revision"]))
        ids = set()
        for r in rows:
            if type(r) is not dict:
                raise NotAdmitted("F40_BAD_FACT_RECORD")
            s, p, o = r.get("s"), r.get("p"), r.get("o")
            if (type(s) is not str or type(p) is not str or type(o) is not str
                or not QID.fullmatch(s) or not QID.fullmatch(o)
                or not PID.fullmatch(p)):
                raise NotAdmitted("F40_MALFORMED_SOURCE_GRAPH_ID")
            if s in reserved or o in reserved:
                raise NotAdmitted("F40_RESERVED_HELDOUT_ID_APPEARS_IN_GRAPH")
            if (type(r.get("source_revision")) is not int
                or r["source_revision"] <= 0
                or type(r.get("source_claim")) is not str
                or not r["source_claim"].startswith(s+"$")
                or len(r["source_claim"]) > 180
                or (s, r["source_revision"]) not in witness):
                raise NotAdmitted("F40_SOURCE_CLAIM_REVISION_UNWITNESSED")
            if any(type(r.get(k)) is not str or not r[k]
                   for k in ("s_label","p_label","o_label",
                             "s_language","p_language","o_language")):
                raise NotAdmitted("F40_FIRST_PARTY_LANGUAGE_OR_LABEL_MISSING")
            key = (s, p, o)
            if key in seen:
                raise NotAdmitted("F40_DUPLICATE_OR_CROSS_ARCHIVE_TRIPLE")
            seen.add(key)
            ids.update((s, o))
            normalized.append(key)
        group_keys.append(ids)
    if len(seen) != 82:
        raise NotAdmitted("F40_SOURCE_TOTAL_COUNT_DRIFT")
    return groups, normalized, group_keys


def build_components(triples):
    adjacency = defaultdict(set)
    for s, p, o in triples:
        adjacency[s].add(o)
        adjacency[o].add(s)
    component_map = {}
    component_nodes = []
    for node in sorted(adjacency, key=qnum):
        if node in component_map:
            continue
        found = set()
        todo = [node]
        while todo:
            v = todo.pop()
            if v in found:
                continue
            found.add(v)
            todo.extend(adjacency[v] - found)
        ordered = sorted(found, key=qnum)
        anchor = ordered[0]
        for name in ordered:
            if name in component_map:
                raise NotAdmitted("F40_ENTITY_SHARED_ACROSS_COMPONENTS")
            component_map[name] = anchor
        component_nodes.append((anchor, ordered))
    component_nodes.sort(key=lambda x:qnum(x[0]))
    return component_map, component_nodes


def audit(docs=None):
    policy = preregistration()
    docs = read_archives() if docs is None else docs
    groups, triples, group_nodes = validate(docs)
    comp_map, components = build_components(triples)
    subjects = {s for s,_,_ in triples}
    all_nodes = set(comp_map)
    fit_roots = {r:comp_map[r] for r in FIT}
    reserved = set(RESERVED)
    if any(r in all_nodes for r in reserved):
        raise NotAdmitted("F40_HELDOUT_OVERLAP")
    overlaps = sorted(group_nodes[2] & (group_nodes[0] | group_nodes[1]), key=qnum)
    old_keys = {(r["s"],r["p"],r["o"]) for g in groups[:2] for r in g}
    new_keys = {(r["s"],r["p"],r["o"]) for r in groups[2]}
    root_components = {fit_roots[r] for r in FIT}
    if (len(all_nodes) != 78 or len(subjects) != 26 or len(components) != 7
        or len(root_components) != 7 or fit_roots["Q30"] != fit_roots["Q95"]
        or (new_keys & old_keys) or len(overlaps) != 4):
        raise NotAdmitted("F40_POST_HOC_ARCHIVE_GRAPH_TOPOLOGY_DRIFT")
    # Shadow development folds: structural leakage tests only; never claim
    # unseen scientific transfer merely because graph components differ.
    folds = []
    for anchor, nodes in components:
        hold = set(nodes)
        fit = all_nodes - hold
        heldout_rows = sum(s in hold for s,_,o in triples)
        trained_rows = sum(s in fit for s,_,o in triples)
        if (hold & fit or heldout_rows + trained_rows != len(triples)
            or any((s in hold) != (o in hold) for s,_,o in triples)):
            raise NotAdmitted("F40_DEV_COMPONENT_FOLD_ENTITY_LEAKAGE")
        folds.append({"fold_anchor_qid":anchor, "entity_count":len(nodes),
                      "source_triples_in_fold":heldout_rows,
                      "other_source_triples":trained_rows,
                      "fit_root_subjects":[q for q in FIT if q in hold],
                      "component_strictly_disjoint":True})
    result = {
        "schema": SCHEMA,
        "classification": "LOCAL_ARCHIVE_ISOLATION_PASS_GLOBAL_FIRST_USE_UNVERIFIED",
        "audit_is_post_hoc_development_only": True,
        "predeclared_source_free_audit_commit": PREREG_COMMIT,
        "source_exact_sha256": list(SHA256),
        "source_row_counts":[len(g) for g in groups],
        "distinct_triples":len(triples),
        "distinct_entities":len(all_nodes),
        "distinct_subject_entities":len(subjects),
        "local_graph_components":len(components),
        "local_fit_root_independent_components":len(root_components),
        "fit_root_component_anchors":fit_roots,
        "fit_root_known_component_collision":["Q30","Q95"],
        "f39_prior_exact_triple_overlap":len(old_keys & new_keys),
        "f39_prior_entity_identity_overlap_qids":overlaps,
        "reserved_root_ids_not_in_archived_rows_or_receipts":list(RESERVED),
        "reserved_root_archived_appearance_count":0,
        "component_rehearsal_folds":folds,
        "local_development_folds_only_not_protected_science":True,
        "r182_known_incomplete_historical_source_ledger":True,
        "global_historical_first_use_certified":False,
        "science_source_admitted_for_first_use":False,
        "fully_trained_conventional_or_native_baseline_compared":False,
        "scientific_pass":False,
        "native_model_weights_edited":False,
        "new_source_requests":0,
        "protected_scientific_first_use_consumed":False,
        "next_qualification_requirement":
            "Require a complete authority-verified prospective post-epoch source-witness and "
            "independent native/fully-trained controls before reserved source or heldout scientific first use."
    }
    return result


def main():
    print("F40_SOURCE_ISOLATION_RESULT=" +
          json.dumps(audit(),sort_keys=True,separators=(",", ":"),ensure_ascii=False))
    print("F40_GLOBAL_HISTORICAL_FIRST_USE=UNVERIFIED")
    print("F40_NO_SOURCE_REQUESTS_OR_MODEL_FIRST_USE=PASS")


if __name__=="__main__":
    main()
