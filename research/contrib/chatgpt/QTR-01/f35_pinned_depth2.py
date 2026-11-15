#!/usr/bin/env python3
"""QTR-01 F35: prospective pinned, source-witnessed depth-two association screening.

Five expansion subjects are determined exclusively by the original CC0 source
graph and their *original* archived revision SHA256. No recipient weights,
first-use scientific data, Qwen activations or model training are touched.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

from f26_semantic_association import NotAdmitted, ITEM_RE, qnum, stable_json, digest, dryrun
from f27_versioned_entitydata import LiveEntityData
from f31_all_language_associations import source_label

ROOT = Path(__file__).parent
SOURCE = ROOT / "evidence" / "f32_source_snapshot.json"
POLICY = ROOT / "f35_prereg.json"
SOURCE_DIGEST = "e9ead9ac15e4ecbe4d99216cda43657e1aeb030d22f59fd852f8b99fa0d440eb"
SCHEMA = "yggdrasil.qtr01.f35.pinned-witnessed-depth2-source-dev.v1"
FROZEN = "e89403f04c6780ae716dd167f9ea83049fc969a2"
PINNED = (
    ("Q36180", 2567832181, "8c1f1c03e9ff0a767e52d2525d875ee03e90ca273bf22685fc6bffe6b6675f71"),
    ("Q214917", 2562932926, "daab1d8a6d6a1320fc04787900072434d70f6489c05c1e940953fffacefa6dc5"),
    ("Q245068", 2562304271, "13df1ed5acd706f6e00c97a2f08f614f89b8324a03d8d8201d5be134dd2198f4"),
    ("Q639669", 2567834956, "9b2f320bed02b221bb5e3c339880f60054e577abe841bf8777c03c16355b9561"),
    ("Q154954", 2557745429, "c2ea57720648b45927540efe0c96e98ce528f85f6555b560c3b24a92d2974a6e"),
)
PREDICATES = ("P31", "P279")
ENDPOINT_MAX = 16
CLAIMS_MAX = 160
SOURCE_CAP = 8388608
RECEIPT_CAP = 393216


def preflight():
    p = json.loads(POLICY.read_text(encoding="utf-8"))
    tuples = [(x["qid"], x["revision"], x["canonical_entity_sha256"])
              for x in p["expanded_source_expected_revision_sha256"]]
    if (p.get("schema") != SCHEMA
        or p.get("stage") != "PREREG_FROZEN_BEFORE_NEW_DATA_OR_CODE"
        or p.get("existing_source_sha256") != SOURCE_DIGEST
        or p.get("existing_source_blob") != "453dad0363689cff785c26db5441555c6841f95d"
        or p.get("original_source_rows") != 13
        or p.get("expanded_subjects") != [x[0] for x in PINNED]
        or tuples != list(PINNED)
        or p.get("expansion_predicates") != list(PREDICATES)
        or p["caps"]["new_endpoint_reads"] != ENDPOINT_MAX
        or p["caps"]["per_http_bytes"] != 4194304
        or p["caps"]["total_http_bytes"] != SOURCE_CAP
        or p["caps"]["new_claims_max"] != CLAIMS_MAX
        or p["caps"]["receipt_bytes_max"] != RECEIPT_CAP
        or p["caps"]["no_network_retries"] is not True
        or p["acceptance"]["real_graph_twohop_queries_min"] != 1
        or p["authority"] !=
        "Contributor isolated QTR draft branch and public CI, no model runtime/weights, no scientific original first-use, paid API, new controller/scheduler, other owner branch, acceptance or merge."):
        raise NotAdmitted("F35_PREREG_OR_SOURCE_SCOPE_CHANGED")
    return p


def original_snapshot(raw):
    if type(raw) is not bytes or sha256(raw).hexdigest() != SOURCE_DIGEST:
        raise NotAdmitted("F35_ORIGINAL_FIRST_PARTY_SHA_MISMATCH")
    d = json.loads(raw)
    old = d.get("typed_source_rows")
    if (d.get("schema") != "yggdrasil.qtr01.f31.first-party-all-language-fact-custody.v1"
        or type(old) is not list or len(old) != 13
        or len(d.get("source_request_receipts", [])) != 25
        or d["matched_symbolic_numeric_control"]["actual_observed_twohop_queries"] != 0
        or d.get("scientific_pass") is not False
        or d.get("native_recipient_model_weights_edited") is not False):
        raise NotAdmitted("F35_SOURCE_ARCHIVE_SHAPE_DRIFT")
    # The five source expansion subjects were fixed from these witnessed edges.
    occupations = sorted(
        {r["o"] for r in old if r["s"] == "Q42" and r["p"] == "P106"},
        key=lambda x: qnum(x, "Q")
    )[:4]
    human_types = sorted(
        {r["o"] for r in old if r["s"] == "Q5" and r["p"] == "P279"},
        key=lambda x: qnum(x, "Q")
    )[:1]
    if occupations + human_types != [x[0] for x in PINNED]:
        raise NotAdmitted("F35_ARCHIVED_WITNESS_SELECTION_DRIFT")
    by_id = {x["entity"]: x for x in d["source_request_receipts"]}
    for qid, rev, sha in PINNED:
        if (qid not in by_id or by_id[qid]["revision"] != rev or
            by_id[qid]["entity_canonical_sha256"] != sha):
            raise NotAdmitted("F35_ORIGINAL_FIRST_PARTY_ENTITY_CUSTODY_MISSING")
    return d


def check_pinned(qid, source_entity, returned_digest, revision, expected_digest):
    if (type(source_entity) is not dict
        or source_entity.get("id") != qid
        or type(source_entity.get("lastrevid")) is not int
        or source_entity["lastrevid"] != revision
        or returned_digest != expected_digest
        or source_label(source_entity) is None):
        raise NotAdmitted("F35_ORIGINAL_ENTITY_REVISION_OR_SOURCE_DIGEST_DRIFT")
    if type(source_entity.get("claims")) is not dict:
        raise NotAdmitted("F35_ORIGINAL_ENTITY_CLAIMS_MISSING")


def extract_new_edges(entities):
    if set(entities) != {x[0] for x in PINNED}:
        raise NotAdmitted("F35_EXPANSION_SOURCE_SET_DRIFT")
    proposed, invalid = [], 0
    for qid, rev, _ in PINNED:
        obj = entities[qid]
        label = source_label(obj)
        if not label or obj["lastrevid"] != rev:
            raise NotAdmitted("F35_SOURCE_ENTITY_IDENTITY_OR_LABEL_NOT_PINNED")
        for pid in PREDICATES:
            claims = obj["claims"].get(pid, [])
            if type(claims) is not list:
                raise NotAdmitted("F35_MALFORMED_SOURCE_CLAIMS")
            for claim in claims:
                if type(claim) is not dict:
                    invalid += 1
                    continue
                claimid = claim.get("id")
                if (type(claimid) is not str or not claimid.startswith(qid + "$")
                    or len(claimid) > 180 or claim.get("rank") not in ("normal", "preferred")
                    or "qualifiers" in claim):
                    invalid += 1
                    continue
                mainsnak = claim.get("mainsnak")
                if type(mainsnak) is not dict or mainsnak.get("snaktype") != "value":
                    invalid += 1
                    continue
                dv = mainsnak.get("datavalue")
                value = dv.get("value") if type(dv) is dict else None
                if (type(value) is not dict or value.get("entity-type") != "item"
                    or type(value.get("id")) is not str
                    or not ITEM_RE.fullmatch(value["id"])):
                    invalid += 1
                    continue
                proposed.append({
                    "s": qid, "p": pid, "o": value["id"],
                    "s_label": label["label"], "s_language": label["source_language"],
                    "source_claim": claimid, "source_revision": rev
                })
    proposed.sort(key=lambda x: (qnum(x["s"], "Q"), qnum(x["p"], "P"),
                                 qnum(x["o"], "Q"), x["source_claim"]))
    unique = []
    seen = set()
    for row in proposed:
        key = (row["s"], row["p"], row["o"])
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique[:CLAIMS_MAX], {"all_eligible_unique": len(unique),
                                  "excluded_unqualified_or_invalid": invalid,
                                  "truncated_to_frozen_max": len(unique) > CLAIMS_MAX}


def source_label_cache(snapshot):
    # Labels and exact source-language strings here are individually witnessed
    # by the ORIGINAL archived QTR first-party response (not invented).
    cache = {}
    for row in snapshot["typed_source_rows"]:
        for role in ("s", "o"):
            qid = row[role]
            value = (row[f"{role}_label"], row[f"{role}_language"])
            if qid in cache and cache[qid] != value:
                raise NotAdmitted("F35_SOURCE_ARCHIVE_CONFLICTING_LABELS")
            cache[qid] = value
    predicate_cache = {}
    for row in snapshot["typed_source_rows"]:
        pid = row["p"]
        value = (row["p_label"], row["p_language"])
        if pid in predicate_cache and predicate_cache[pid] != value:
            raise NotAdmitted("F35_ARCHIVED_PREDICATE_LABEL_CONFLICT")
        predicate_cache[pid] = value
    for predicate in PREDICATES:
        if predicate not in predicate_cache:
            raise NotAdmitted("F35_SOURCE_PREVIOUS_PREDICATE_LABEL_MISSING")
    return cache, predicate_cache


def missing_object_queries(rows, original_cache, seen_subjects):
    objects = {row["o"] for row in rows}
    return sorted(objects - set(original_cache) - set(seen_subjects),
                  key=lambda q: qnum(q, "Q"))[:ENDPOINT_MAX]


def complete_new_labels(rows, original_cache, props, endpoints):
    newrows, skipped = [], 0
    for row in rows:
        s = original_cache[row["s"]]
        pred = props[row["p"]]
        if row["o"] in original_cache:
            o = original_cache[row["o"]]
        elif row["o"] in endpoints:
            label = source_label(endpoints[row["o"]])
            if label is None:
                skipped += 1
                continue
            o = label["label"], label["source_language"]
        else:
            skipped += 1
            continue
        newrows.append({
            "s": row["s"], "p": row["p"], "o": row["o"],
            "s_label": s[0], "s_language": s[1],
            "p_label": pred[0], "p_language": pred[1],
            "o_label": o[0], "o_language": o[1],
            "source_claim": row["source_claim"],
            "source_revision": row["source_revision"],
        })
    return newrows, skipped


def twohop_analysis(original, added):
    raw = original + added
    keys = [(qnum(row["s"], "Q"), qnum(row["p"], "P"), qnum(row["o"], "Q"))
            for row in raw]
    if len(keys) != len(set(keys)):
        raise NotAdmitted("F35_DUPLICATE_FIRST_PARTY_CLAIMS")
    # The strongest exactly informed control is the original symbolic graph,
    # joined over the same verified Q/P/Q triples; no causal learning inferred.
    control = {}
    for s, p, o in keys:
        control.setdefault(s, []).append((p, o))
    paths = []
    for s, p1, mid in keys:
        for p2, obj in control.get(mid, ()):
            paths.append((s, p1, mid, p2, obj))
    paths.sort()
    normalized = [dict(
        s=row["s"], p=row["p"], o=row["o"],
        s_label=row["s_label"], p_label=row["p_label"],
        o_label=row["o_label"], source_claim=row["source_claim"],
        source_revision=row["source_revision"]) for row in raw]
    numeric = dryrun(normalized)
    queries = sorted({(s, p1, p2) for s, p1, _, p2, _ in paths})
    if (numeric["twohop_compositions_checked"] != len(queries)
        or not numeric["equal_info_symbolic_control_parity"]
        or not numeric["cold_restore_exact"]):
        raise NotAdmitted("F35_NUMERIC_VS_EXACT_SOURCE_SYMBOLIC_COMPOSITION_DRIFT")
    return {
        "total_witnessed_triples": len(raw),
        "new_witnessed_triples": len(added),
        "real_twohop_queries": len(queries),
        "real_twohop_paths": len(paths),
        "depth_two_paths": [{
            "source": f"Q{s}", "first_property": f"P{p1}", "intermediate": f"Q{mid}",
            "second_property": f"P{p2}", "result": f"Q{o}"
        } for s, p1, mid, p2, o in paths[:80]],
        "matched_exact_source_symbolic_parity": True,
        "canonical_numeric_cold_restore": True,
        "metadata_and_source_labels_not_stored_in_numeric_payload": True,
        "neural_weights_edited": False,
        "scientific_pass": False,
    }


def capture(reader=None):
    preflight()
    original = original_snapshot(SOURCE.read_bytes())
    reader = LiveEntityData() if reader is None else reader
    expansions = {}
    for qid, revision, expected in PINNED:
        entity, canonical_sha = reader.fetch(qid, revision)
        check_pinned(qid, entity, canonical_sha, revision, expected)
        expansions[qid] = entity
        if reader.total_bytes > SOURCE_CAP:
            raise NotAdmitted("F35_ORIGINAL_REVISION_SOURCE_BUDGET_EXCEEDED")
    newraw, inv = extract_new_edges(expansions)
    objects, props = source_label_cache(original)
    # Recovered original frozen source label must be consistent with exact
    # revision-addressed response selected by original snapshot.
    for qid, entity in expansions.items():
        src = source_label(entity)
        if (src["label"], src["source_language"]) != objects[qid]:
            raise NotAdmitted("F35_ORIGINAL_LABEL_AND_ENTITY_DIGEST_CONTRADICT")
    endpoint_ids = missing_object_queries(newraw, objects, expansions)
    endpoint_entities = {}
    for qid in endpoint_ids:
        ent, _ = reader.fetch(qid)
        endpoint_entities[qid] = ent
        if reader.total_bytes > SOURCE_CAP:
            raise NotAdmitted("F35_EXTERNAL_ENDPOINT_SOURCE_BUDGET_EXCEEDED")
    newer, unadmitted = complete_new_labels(newraw, objects, props, endpoint_entities)
    if not newer:
        raise NotAdmitted("F35_NO_ADMITTED_SOURCE_EXPANSION")
    proof = twohop_analysis(original["typed_source_rows"], newer)
    if proof["real_twohop_queries"] < 1:
        raise NotAdmitted("F35_FROZEN_REAL_SOURCE_TWOHOP_HEADROOM_NO_GO")
    obj = {
        "schema": SCHEMA,
        "preregistration_commit": FROZEN,
        "original_source_snapshot_sha256": SOURCE_DIGEST,
        "source_license": "Wikidata structured source CC0",
        "source_selection": [x[0] for x in PINNED],
        "source_subjects_fully_pinned": True,
        "new_source_claim_inventory": inv,
        "new_endpoint_label_read_count": len(endpoint_ids),
        "unlabeled_or_budget_excluded_new_edges": unadmitted,
        "read_only_first_party_receipts": reader.receipts,
        "new_http_source_bytes": reader.total_bytes,
        "added_witnessed_source_rows": newer,
        "new_rows_sha256": digest(newer),
        "composition": proof,
        "original_snapshot_rows_unchanged": True,
        "mixed_label_revisions_for_new_endpoints": bool(endpoint_entities),
        "no_native_model_edits": True,
        "scientific_pass": False,
        "source_dev_status": "F35_REAL_FIRST_PARTY_DEPTH2_IDENTIFIABLE_NOT_NATIVE_LEARNING",
    }
    if len(stable_json(obj)) > RECEIPT_CAP:
        raise NotAdmitted("F35_OUTPUT_SOURCE_RECEIPT_TOO_LARGE")
    return obj


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen-pinned-source-only", required=True, action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        d = capture()
    except (NotAdmitted, OSError, ValueError, TimeoutError, UnicodeError, OverflowError) as exc:
        print("F35_SOURCE_SCREEN_NO_GO=" + type(exc).__name__ + ":" + str(exc), file=sys.stderr)
        return 2
    raw = stable_json(d) + b"\n"
    args.output.write_bytes(raw)
    proof = d["composition"]
    print("F35_SOURCE_DEPTH2_SCREEN=PASS")
    print("F35_ADDED_WITNESSED_RELATIONS=" + str(proof["new_witnessed_triples"]))
    print("F35_JOINED_TWOHOP_QUERIES=" + str(proof["real_twohop_queries"]))
    print("F35_JOINED_TWOHOP_PATHS=" + str(proof["real_twohop_paths"]))
    print("F35_PINNED_ENTITY_GETS=" + str(len(PINNED)))
    print("F35_NEW_ENDPOINT_GETS=" + str(d["new_endpoint_label_read_count"]))
    print("F35_READ_SOURCE_BYTES=" + str(d["new_http_source_bytes"]))
    print("F35_SOURCE_RECEIPT_SHA256=" + sha256(raw).hexdigest())
    print("F35_SCIENCE_AND_NATIVE_WEIGHT_EDIT=NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
