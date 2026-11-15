#!/usr/bin/env python3
"""F31 first-party source-native language associations, QTR source-only DEV.

Never translate a label, infer model activations, train native weights or run
protected scientific evaluation. Source labels retain exact source-language tags.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

from f26_semantic_association import (
    NotAdmitted, ITEM_RE, safe_label, qnum, stable_json, digest,
)
from f27_versioned_entitydata import LiveEntityData
from f30_multilingual_associations import (
    endpoint_order, source_free_numeric_control,
)

SCHEMA="yggdrasil.qtr01.f31.first-party-all-language-fact-custody.v1"
FROZEN="211b1f4c77df7129bbbdf9f8936bb01e6c0ee1c2"
SEEDS=("Q42","Q5")
PROPS=("P31","P279","P106","P19","P69","P27","P50","P463")
TAG=re.compile(r"^[a-z]{2,8}(?:-[a-z0-9]{2,8})*$")
MAX_ROWS=160
MAX_ENDPOINTS=24
MAX_RECEIPT=393216
POLICY=Path(__file__).with_name("f31_prereg.json")


def preflight():
    p=json.loads(POLICY.read_text(encoding="utf-8"))
    if (p.get("schema")!=SCHEMA or p.get("state")!="PREREGISTERED_BEFORE_NEW_EXECUTABLE_AND_SOURCE"
        or p.get("seed_qids")!=list(SEEDS)
        or p.get("allowed_predicates")!=list(PROPS)
        or p.get("label_selection")!=
            "First exact valid source labels.en if safe; otherwise lexicographically smallest valid BCP-47-like lowercase language tag with a first-party label whose language field exactly equals the key and whose string passes safe_label. Preserve original label and exact source language. Never synthesize or translate."
        or p.get("language_tag_regex")!=TAG.pattern
        or p.get("statements_max")!=MAX_ROWS
        or p.get("endpoints_max")!=MAX_ENDPOINTS
        or p.get("per_http_max_bytes")!=4194304
        or p.get("total_http_max_bytes")!=16777216
        or p.get("output_receipt_max_bytes")!=MAX_RECEIPT
        or p.get("read_timeout_seconds")!=15
        or p.get("network_retries")!=0
        or p["scope_fences"].get("no_native_recipient_model_weights") is not True):
        raise NotAdmitted("F31_SOURCE_PRE_REGISTRATION_DRIFT")
    return p


def source_label(entity):
    labels=entity.get("labels")
    if type(labels) is not dict:
        return None
    preferred=["en"] if "en" in labels else []
    ordering=preferred+sorted(k for k in labels if k!="en" and type(k) is str and TAG.fullmatch(k))
    for language in ordering:
        if not TAG.fullmatch(language):
            continue
        rec=labels[language]
        if type(rec) is not dict or rec.get("language") != language:
            continue
        label=rec.get("value")
        if type(label) is not str:
            continue
        try:
            cleaned=safe_label(label)
        except NotAdmitted:
            continue
        return {"source_language":language,"label":cleaned}
    return None


def witnessed_rows(seed_data):
    if set(seed_data)!=set(SEEDS):
        raise NotAdmitted("F31_SOURCE_SEEDS_DIFFER_FROM_PRE_REGISTRATION")
    raw=[]
    rejected=0
    audit={}
    for qid in SEEDS:
        source=seed_data[qid]
        selected=source_label(source)
        if selected is None:
            raise NotAdmitted("F31_NO_QUALIFIED_FIRST_PARTY_LABEL_FOR_SEED")
        audit[qid]=selected["source_language"]
        revision=source.get("lastrevid")
        if type(revision) is not int or revision<=0 or type(source.get("claims")) is not dict:
            raise NotAdmitted("F31_SEED_NOT_FIRST_PARTY_REVISIONED_CLAIMS")
        for pid in PROPS:
            claims=source["claims"].get(pid,[])
            if type(claims) is not list:
                raise NotAdmitted("F31_CLAIM_COLLECTION_CORRUPT")
            for item in claims:
                if (type(item) is not dict
                    or type(item.get("id")) is not str
                    or not item["id"].startswith(qid+"$")
                    or len(item["id"])>180
                    or item.get("rank") not in ("normal","preferred")
                    or "qualifiers" in item):
                    rejected+=1
                    continue
                snak=item.get("mainsnak")
                if type(snak) is not dict or snak.get("snaktype")!="value":
                    rejected+=1
                    continue
                dv=snak.get("datavalue")
                val=dv.get("value") if type(dv) is dict else None
                if (type(val) is not dict or val.get("entity-type")!="item"
                    or type(val.get("id")) is not str or not ITEM_RE.fullmatch(val["id"])):
                    rejected+=1
                    continue
                raw.append({
                    "s":qid,"p":pid,"o":val["id"],
                    "s_label":selected["label"],
                    "s_language":selected["source_language"],
                    "source_claim":item["id"],"source_revision":revision,
                })
    raw.sort(key=lambda x:(qnum(x["s"],"Q"),qnum(x["p"],"P"),qnum(x["o"],"Q"),x["source_claim"]))
    distinct=[]
    used=set()
    for item in raw:
        triple=item["s"],item["p"],item["o"]
        if triple not in used:
            used.add(triple)
            distinct.append(item)
    return distinct[:MAX_ROWS], {
        "unique_eligible_claims":len(distinct),
        "excluded_unwitnessed_or_non_item_claims":rejected,
        "truncated":len(distinct)>MAX_ROWS,
        "seed_source_languages":audit,
    }


def attach_labels(rows,seeds,endpoints,properties):
    items={**seeds,**endpoints}
    result=[]
    skipped=0
    for row in rows:
        s=source_label(items[row["s"]])
        o=source_label(items[row["o"]]) if row["o"] in items else None
        p=source_label(properties[row["p"]]) if row["p"] in properties else None
        if not s or not o or not p:
            skipped+=1
            continue
        result.append({
            "s":row["s"],"p":row["p"],"o":row["o"],
            "s_label":s["label"],"s_language":s["source_language"],
            "p_label":p["label"],"p_language":p["source_language"],
            "o_label":o["label"],"o_language":o["source_language"],
            "source_claim":row["source_claim"],"source_revision":row["source_revision"],
        })
    if not result:
        raise NotAdmitted("F31_NO_FIRST_PARTY_SEMANTIC_ASSOCIATIONS")
    return result,skipped


def capture(reader=None):
    preflight()
    reader=LiveEntityData() if reader is None else reader
    seeds={}
    baseline={}
    for qid in SEEDS:
        seeds[qid],baseline[qid]=reader.fetch(qid)
    rows,inventory=witnessed_rows(seeds)
    for qid in SEEDS:
        pinned,sha=reader.fetch(qid,seeds[qid]["lastrevid"])
        if pinned!=seeds[qid] or sha!=baseline[qid]:
            raise NotAdmitted("F31_REVISED_SOURCE_CLAIMS_CHANGED_AT_PINNED_REVISION")
    endpoints={}
    for qid in endpoint_order(rows):
        endpoints[qid]=reader.fetch(qid)[0]
    properties={}
    for pid in PROPS:
        properties[pid]=reader.fetch(pid)[0]
    labeled,skipped=attach_labels(rows,seeds,endpoints,properties)
    ctrl=source_free_numeric_control(labeled)
    if not ctrl["canonical_cold_restore"] or not ctrl["numeric_vs_equal_info_symbolic_2hop_parity"]:
        raise NotAdmitted("F31_ORIGINAL_ASSOCIATIONS_MISMATCH_EQUAL_INFO_SYMBOLIC")
    summary={
        "schema":SCHEMA,"frozen_protocol_commit":FROZEN,
        "source":"Wikidata first-party revisioned Special:EntityData",
        "structured_data_license":"CC0",
        "license_reference":"https://www.wikidata.org/wiki/Wikidata:Licensing",
        "source_only":True,"first_party_ids":list(SEEDS),"allowed_properties":list(PROPS),
        "source_inventory":inventory,
        "source_excluded_missing_label_count":skipped,
        "source_request_receipts":reader.receipts,
        "original_bytes_read":reader.total_bytes,
        "typed_source_rows":labeled,
        "typed_source_rows_sha256":digest(labeled),
        "matched_symbolic_numeric_control":ctrl,
        "source_languages_were_not_translated_or_inferred":True,
        "qwen_activation_feature_alignment_claimed":False,
        "native_recipient_model_weights_edited":False,
        "scientific_pass":False,
        "status":"DEVELOPMENT_SOURCE_ASSOCIATIONS_ONLY_NOT_NEURAL_LEARNING",
    }
    if len(stable_json(summary))>MAX_RECEIPT:
        raise NotAdmitted("F31_SOURCE_CUSTODY_REPORT_EXCEEDS_FROZEN_SIZE")
    return summary


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--frozen-first-party-only",action="store_true",required=True)
    cli.add_argument("--output",type=Path,required=True)
    args=cli.parse_args()
    try:
        obj=capture()
    except (NotAdmitted,OSError,TimeoutError,ValueError,UnicodeError,OverflowError) as exc:
        print("F31_FIRST_PARTY_SOURCE_BLOCKED="+type(exc).__name__+":"+str(exc),file=sys.stderr)
        return 2
    b=stable_json(obj)+b"\n"
    args.output.write_bytes(b)
    s=obj["matched_symbolic_numeric_control"]
    print("F31_LABELED_FIRST_PARTY_ASSOCIATIONS=PASS")
    print("F31_TYPED_ASSOCIATION_COUNT="+str(s["source_labeled_rows"]))
    print("F31_VERIFIED_SOURCE_LANGUAGES="+json.dumps(s["source_label_languages"],sort_keys=True))
    print("F31_ACTUAL_COMPOSED_TWOHOP_QUERIES="+str(s["actual_observed_twohop_queries"]))
    print("F31_NUMBER_CARRIER_BYTES="+str(s["typed_integer_carrier_bytes"]))
    print("F31_TOTAL_SOURCE_BYTES="+str(obj["original_bytes_read"]))
    print("F31_PINNED_SOURCE_RECEIPT_SHA256="+sha256(b).hexdigest())
    print("F31_NO_NATIVE_WEIGHTS_OR_SCIENCE=PASS")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
