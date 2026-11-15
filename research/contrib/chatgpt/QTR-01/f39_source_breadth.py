#!/usr/bin/env python3
"""F39: source-witnessed multi-domain FIT graph breadth, source-only DEV.

One preregistered bounded Wikidata CC0 read. Reserved unseen roots are never
fetched nor included as graph identities. No model training or science test.
"""
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys

from f26_semantic_association import NotAdmitted, ITEM_RE, qnum, digest, stable_json
from f27_versioned_entitydata import LiveEntityData
from f31_all_language_associations import source_label

ROOT = Path(__file__).resolve().parent
POLICY = ROOT / "f39_prereg.json"
SCHEMA = "yggdrasil.qtr01.f39.prospective-breadth-source-fit-only.v1"
FROZEN = "8498a05b24157e322502ac43527738688756cebd"
ROOTS = ("Q2","Q17","Q30","Q64","Q76","Q80","Q90","Q95")
GROUPS = ("planetary","country","country","city","person","person","city","organization")
RESERVED = ("Q142","Q183","Q312","Q1490")
PROPS = ("P17","P19","P27","P31","P36","P50","P69","P106","P131","P159","P279","P361")
MAX_GETS = 100
MAX_BYTES = 25165824
MAX_RECEIPT = 786432
MAX_PRIMARY = 4
MAX_SECONDARY = 3
MAX_EXPANSIONS_PER_ROOT = 2
MAX_EXPANSIONS = 16
MAX_ENDPOINTS = 32


def preflight(path=POLICY):
    p = json.loads(Path(path).read_text(encoding="utf-8"))
    if (p.get("schema") != SCHEMA
        or p.get("status") != "FROZEN_BEFORE_F39_SOURCE_CODE_OR_NEW_SOURCE_READ"
        or p.get("parent") != "8849236b7f682c8e1eea9808b308b3cab264425f"
        or [(x["id"],x["group"]) for x in p.get("fit_roots", [])] != list(zip(ROOTS,GROUPS))
        or [x["id"] for x in p.get("reserved_unseen_roots", [])] != list(RESERVED)
        or p.get("claim_predicates") != list(PROPS)
        or p.get("source_reader_blob") != "db561564c949ffe1a15c99dc460d18d0143588d1"
        or p.get("source_label_blob") != "6746518963f07f8355fc4bd66716d86547183005"
        or p.get("caps") != {
            "max_fit_roots":8,"max_expansion_subjects":16,
            "max_selected_primary_per_root":4,
            "max_selected_secondary_per_subject":3,
            "max_additional_endpoints":32,"max_predicate_labels":12,
            "max_total_gets":100,"max_each_http_bytes":4194304,
            "max_total_http_bytes":25165824,
            "max_receipt_bytes":786432,"per_http_timeout_sec":15,"retries":0}
        or p.get("headroom") != {
            "min_distinct_fit_roots_with_composable_paths":5,
            "min_distinct_first_second_predicate_pairs":4,
            "min_distinct_source_query_signatures":12,
            "min_distinct_fit_groups_with_paths":3}
        or any(p.get("fences", {}).get(flag) is not True for flag in (
            "no_read_reserved_root_or_related_id","no_model_weights",
            "no_native_recipient_inference_or_training","no_new_scientific_first_use",
            "no_protected_original_science","no_donor_or_llm_training_data",
            "no_main_or_acceptance_ref_edits","no_merge","no_production_or_scheduled_tasks",
            "no_paid_api","no_user_library_files","no_source_retry"))):
        raise NotAdmitted("F39_FROZEN_POLICY_DRIFT")
    return p


def extract(entity, subject, limit):
    if (subject in RESERVED or entity.get("id") != subject
        or type(entity.get("lastrevid")) is not int
        or entity["lastrevid"] <= 0 or type(entity.get("claims")) is not dict
        or source_label(entity) is None):
        raise NotAdmitted("F39_SUBJECT_ID_REVISION_LABEL_OR_CLAIM_MISSING")
    rows = []
    bad = 0
    for pid in PROPS:
        claims = entity["claims"].get(pid, [])
        if type(claims) is not list:
            raise NotAdmitted("F39_MALFORMED_CLAIM_COLLECTION")
        for claim in claims:
            if type(claim) is not dict:
                bad += 1
                continue
            claimid = claim.get("id")
            if (type(claimid) is not str or not claimid.startswith(subject+"$")
                or len(claimid) > 180 or claim.get("rank") not in ("normal","preferred")
                or "qualifiers" in claim):
                bad += 1
                continue
            snak = claim.get("mainsnak")
            if type(snak) is not dict or snak.get("snaktype") != "value":
                bad += 1
                continue
            dv = snak.get("datavalue")
            val = dv.get("value") if type(dv) is dict else None
            if (type(val) is not dict or val.get("entity-type") != "item"
                or type(val.get("id")) is not str or not ITEM_RE.fullmatch(val["id"])):
                bad += 1
                continue
            rows.append({"s":subject,"p":pid,"o":val["id"],
                         "source_claim":claimid,
                         "source_revision":entity["lastrevid"]})
    rows.sort(key=lambda r:(qnum(r["p"],"P"),qnum(r["o"],"Q"),r["source_claim"]))
    seen, unique = set(), []
    for r in rows:
        key = (r["s"],r["p"],r["o"])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    selected = unique[:limit]
    # No backfill after observing that a selected object is reserved.
    admitted = [r for r in selected if r["o"] not in RESERVED]
    return admitted, {"unqualified_unique":len(unique),
                      "source_selected_before_reserved_exclusion":len(selected),
                      "selected_after_reserved_exclusion":len(admitted),
                      "rejected_invalid":bad,"reserved_discarded":len(selected)-len(admitted),
                      "truncated":len(unique)>limit}


def paths_for(rows):
    by_subject = defaultdict(list)
    for r in rows:
        by_subject[r["s"]].append(r)
    result = set()
    for first in rows:
        for second in by_subject.get(first["o"], ()):
            if (first["source_claim"] == second["source_claim"]
                or second["o"] in RESERVED):
                continue
            result.add((first["s"],first["p"],first["o"],second["p"],second["o"]))
    return sorted(result)


def capture(reader=None):
    policy = preflight()
    reader = LiveEntityData() if reader is None else reader
    sources, verified = {}, {}
    def checked_get(qid, rev=None):
        if qid in RESERVED:
            raise NotAdmitted("F39_RESERVED_ROOT_SOURCE_LEAK")
        obj, digest_ = reader.fetch(qid,rev)
        if len(reader.receipts)>MAX_GETS or reader.total_bytes>MAX_BYTES:
            raise NotAdmitted("F39_SOURCE_NETWORK_LIMIT_EXCEEDED")
        if obj.get("id")!=qid or type(obj.get("lastrevid")) is not int:
            raise NotAdmitted("F39_SOURCE_ID_REVISION_MISMATCH")
        if rev is not None and obj["lastrevid"] != rev:
            raise NotAdmitted("F39_PINNED_REVISION_MISMATCH")
        return obj,digest_

    def pin_subject(qid):
        if qid in verified:
            return sources[qid]
        original,orig_sha = checked_get(qid)
        replica,replica_sha = checked_get(qid, original["lastrevid"])
        if original != replica or orig_sha != replica_sha:
            raise NotAdmitted("F39_SOURCE_REVISION_PIN_DIGEST_DRIFT")
        if source_label(original) is None or type(original.get("claims")) is not dict:
            raise NotAdmitted("F39_SOURCE_NOT_SEMANTICALLY_LABELED")
        sources[qid] = original
        verified[qid] = {"revision":original["lastrevid"],"canonical_sha256":orig_sha}
        return original

    for qid in ROOTS:
        pin_subject(qid)
    primary, inventory = [], {}
    for qid in ROOTS:
        rows,stats = extract(sources[qid],qid,MAX_PRIMARY)
        inventory[qid] = stats
        primary.extend(rows)

    expand = []
    for qid in ROOTS:
        choices = []
        for row in primary:
            if row["s"]==qid and row["o"] not in choices:
                choices.append(row["o"])
        for target in choices[:MAX_EXPANSIONS_PER_ROOT]:
            if target not in expand:
                expand.append(target)
    if len(expand)>MAX_EXPANSIONS:
        raise NotAdmitted("F39_EXPANSION_SCOPE_VIOLATED")
    for qid in expand:
        pin_subject(qid)
    secondary, secondary_inventory = [], {}
    for qid in expand:
        rows,stats = extract(sources[qid],qid,MAX_SECONDARY)
        secondary.extend(rows)
        secondary_inventory[qid] = stats

    raw = []
    seen = set()
    for row in primary + secondary:
        key = (row["s"],row["p"],row["o"])
        if key not in seen:
            seen.add(key)
            raw.append(row)
    # Do not consume reserved root identities as source/target/labels,
    # including when a previously seen source entity pointed at one.
    if any(x["s"] in RESERVED or x["o"] in RESERVED for x in raw):
        raise NotAdmitted("F39_RESERVED_ENTITY_ADMITTED")

    endpoint_ids = sorted({r["o"] for r in raw if r["o"] not in sources},
                          key=lambda q:qnum(q,"Q"))[:MAX_ENDPOINTS]
    endpoint_entities = {qid:checked_get(qid)[0] for qid in endpoint_ids}
    props = {pid:checked_get(pid)[0] for pid in PROPS}
    resolved = {**sources,**endpoint_entities}
    labels = []
    for row in raw:
        a = source_label(resolved[row["s"]])
        b = source_label(resolved[row["o"]]) if row["o"] in resolved else None
        c = source_label(props[row["p"]])
        if a is None or b is None or c is None:
            continue
        labels.append({**row,
            "s_label":a["label"],"s_language":a["source_language"],
            "p_label":c["label"],"p_language":c["source_language"],
            "o_label":b["label"],"o_language":b["source_language"]})
    if not labels:
        raise NotAdmitted("F39_NO_SOURCE_LABELED_RELATIONSHIP")
    if any(x["s"] in RESERVED or x["o"] in RESERVED for x in labels):
        raise NotAdmitted("F39_RESERVED_SOURCE_BROKEN")
    graph_paths = paths_for(labels)
    fitpaths = [x for x in graph_paths if x[0] in ROOTS]
    root_set = sorted({x[0] for x in fitpaths},key=lambda x:qnum(x,"Q"))
    group_map = dict(zip(ROOTS,GROUPS))
    group_set = sorted({group_map[x] for x in root_set})
    pair_set = sorted({(x[1],x[3]) for x in fitpaths})
    key_set = sorted({(x[0],x[1],x[3]) for x in fitpaths})
    headroom = policy["headroom"]
    eligible = (len(root_set)>=headroom["min_distinct_fit_roots_with_composable_paths"]
        and len(pair_set)>=headroom["min_distinct_first_second_predicate_pairs"]
        and len(key_set)>=headroom["min_distinct_source_query_signatures"]
        and len(group_set)>=headroom["min_distinct_fit_groups_with_paths"])
    result = {
        "schema":SCHEMA,"preregistered_commit":FROZEN,
        "data_stage":"SOURCE_ONLY_FIT_NOT_SCIENCE",
        "source":"Wikidata first-party revision-addressed CC0",
        "fit_roots":list(ROOTS),"fit_groups":list(GROUPS),
        "reserved_unseen_roots_NOT_READ":list(RESERVED),
        "fit_root_inventory":inventory,"expansion_inventory":secondary_inventory,
        "verified_source_revisions":verified,
        "source_primary_selected":len(primary),"source_secondary_selected":len(secondary),
        "unique_prelabel_admission_rows":len(raw),"labeled_witnessed_rows":len(labels),
        "witnessed_rows":labels,"witnessed_rows_sha256":digest(labels),
        "graph_all_composable_path_count":len(graph_paths),
        "graph_fit_root_twohop_paths":len(fitpaths),
        "graph_fit_root_twohop_examples":[{"s":x[0],"p1":x[1],"via":x[2],"p2":x[3],"o":x[4]} for x in fitpaths[:64]],
        "fit_roots_with_twohop":root_set,"fit_groups_with_twohop":group_set,
        "fit_relation_pairs":[list(x) for x in pair_set],
        "fit_query_signatures":[list(x) for x in key_set],
        "headroom_status":"FIT_SOURCE_BREADTH_PRESENT" if eligible else "INSUFFICIENT_SOURCE_HEADROOM",
        "source_receipts":reader.receipts,"source_http_get_count":len(reader.receipts),
        "source_http_bytes":reader.total_bytes,
        "mixed_revision_caveat":True,"reserved_unseen_read_count":0,
        "native_model_weights_edited":False,
        "trained_conventional_or_native_baseline_run":False,
        "scientific_pass":False,
        "unfamiliar_transfer_evaluated":False,
        "protected_scientific_first_use_consumed":False
    }
    if len(stable_json(result))>MAX_RECEIPT:
        raise NotAdmitted("F39_OUTPUT_RECEIPT_TOO_LARGE")
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--frozen-fit-source-once",action="store_true",required=True)
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    try:
        d=capture()
    except (NotAdmitted,OSError,TimeoutError,ValueError,UnicodeError,OverflowError) as e:
        print("F39_SOURCE_BLOCKED="+type(e).__name__+":"+str(e),file=sys.stderr)
        return 2
    raw=stable_json(d)+b"\n"
    a.output.write_bytes(raw)
    print("F39_HEADROOM="+d["headroom_status"])
    print("F39_LABELED_RELATIONS="+str(d["labeled_witnessed_rows"]))
    print("F39_FIT_ROOTS_COMPOSABLE="+str(len(d["fit_roots_with_twohop"])))
    print("F39_FIT_QUERY_SIGNATURES="+str(len(d["fit_query_signatures"])))
    print("F39_FIT_OPERATOR_PAIRS="+str(len(d["fit_relation_pairs"])))
    print("F39_FIT_GROUPS="+str(len(d["fit_groups_with_twohop"])))
    print("F39_SOURCE_GETS="+str(d["source_http_get_count"]))
    print("F39_SOURCE_BYTES="+str(d["source_http_bytes"]))
    print("F39_SOURCE_RECEIPT_SHA256="+sha256(raw).hexdigest())
    print("F39_NO_RESERVED_SCIENCE_DATA_OR_MODEL_FIRST_USE=PASS")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
