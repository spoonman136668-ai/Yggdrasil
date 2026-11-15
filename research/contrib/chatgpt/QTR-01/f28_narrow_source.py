#!/usr/bin/env python3
"""QTR-01 F28 reduced first-party CC0 knowledge snapshot, source custody only."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from f26_semantic_association import (
    NotAdmitted, complete_labels, dryrun, label_from_entity, qnum,
    safe_label, stable_json, digest, ITEM_RE,
)
from f27_versioned_entitydata import LiveEntityData

SCHEMA="yggdrasil.qtr01.f28.versioned-narrow-knowledge-snapshot.v1"
FROZEN="8754fba54b077885d2d7132c26789ba5a60fa18f"
SEEDS=("Q42","Q5")
PROPS=("P31","P279","P106","P19","P69","P27","P50","P463")
MAX_ENDPOINTS=24
MAX_STATEMENTS=160
MAX_RECEIPT=393216
POLICY=Path(__file__).with_name("f28_prereg.json")


def preflight():
    c=json.loads(POLICY.read_text(encoding="utf-8"))
    if (c.get("schema")!=SCHEMA or c.get("stage")!="FROZEN_BEFORE_SOURCE_AND_CODE"
        or c.get("seed_qids")!=list(SEEDS) or c.get("predicates")!=list(PROPS)
        or c.get("endpoint_budget")!=MAX_ENDPOINTS
        or c.get("statement_budget")!=MAX_STATEMENTS
        or c.get("max_total_bytes")!=16777216
        or c.get("max_per_source_bytes")!=4194304
        or c.get("max_receipt_bytes")!=MAX_RECEIPT
        or c.get("request_timeout_seconds")!=15
        or c.get("never_retry") is not True):
        raise NotAdmitted("F28_PREREG_SOURCE_DRIFT")
    return c


def source_rows(seed_entities):
    if set(seed_entities)!=set(SEEDS):
        raise NotAdmitted("F28_SEED_SCOPE_CHANGED")
    out=[]
    dropped=0
    for sid in SEEDS:
        ent=seed_entities[sid]
        name=label_from_entity(ent)
        if name is None:
            raise NotAdmitted("F28_UNLABELED_SEED")
        revision=ent.get("lastrevid")
        if type(revision) is not int or revision<=0:
            raise NotAdmitted("F28_SEED_REVISION_MISSING")
        claims=ent.get("claims")
        if type(claims) is not dict:
            raise NotAdmitted("F28_CLAIMS_MISSING")
        for pid in PROPS:
            candidates=claims.get(pid,[])
            if type(candidates) is not list:
                raise NotAdmitted("F28_BAD_CLAIM_ARRAY")
            for item in candidates:
                if type(item) is not dict or type(item.get("id")) is not str:
                    dropped+=1
                    continue
                if (not item["id"].startswith(sid+"$") or len(item["id"])>180
                    or item.get("rank") not in ("normal","preferred")
                    or item.get("qualifiers")):
                    dropped+=1
                    continue
                snak=item.get("mainsnak")
                if type(snak) is not dict or snak.get("snaktype")!="value":
                    dropped+=1
                    continue
                dv=snak.get("datavalue")
                value=dv.get("value") if type(dv) is dict else None
                if (type(value) is not dict or value.get("entity-type")!="item"
                    or type(value.get("id")) is not str
                    or not ITEM_RE.fullmatch(value["id"])):
                    dropped+=1
                    continue
                out.append({"s":sid,"p":pid,"o":value["id"],
                            "s_label":safe_label(name),
                            "claim":item["id"],"source_revision":revision})
    out.sort(key=lambda x:(qnum(x["s"],"Q"),qnum(x["p"],"P"),qnum(x["o"],"Q"),x["claim"]))
    dedup={}
    for row in out:
        dedup.setdefault((row["s"],row["p"],row["o"]),row)
    sorted_rows=list(dedup.values())
    return sorted_rows[:MAX_STATEMENTS], {
        "all_verified_distinct_source_edges":len(sorted_rows),
        "truncated":len(sorted_rows)>MAX_STATEMENTS,
        "excluded_invalid_or_unqualified_claims":dropped,
    }


def endpoints_prioritizing_bridge(rows):
    # Prioritize documented Q42 --P31--> Q5 --P279--> x, then numeric QID.
    has_bridge=any(r["s"]=="Q42" and r["p"]=="P31" and r["o"]=="Q5" for r in rows)
    prioritized = (
        {r["o"] for r in rows if has_bridge and r["s"]=="Q5" and r["p"]=="P279"}
    )
    allids={r["o"] for r in rows if r["o"] not in SEEDS}
    prioritized &= allids
    order=lambda xs:sorted(xs,key=lambda q:qnum(q,"Q"))
    return (order(prioritized)+order(allids-prioritized))[:MAX_ENDPOINTS]


def capture(reader=None):
    preflight()
    live=reader if reader is not None else LiveEntityData()
    seeds={}
    seed_digests={}
    for id_ in SEEDS:
        seeds[id_],seed_digests[id_]=live.fetch(id_)
    rows,inventory=source_rows(seeds)
    for id_ in SEEDS:
        entity,hash_=live.fetch(id_,seeds[id_]["lastrevid"])
        if hash_!=seed_digests[id_] or entity!=seeds[id_]:
            raise NotAdmitted("F28_PINNED_SEED_REVISION_CONTENT_DRIFT")
    endpoint_ids=endpoints_prioritizing_bridge(rows)
    endpoints={}
    for id_ in endpoint_ids:
        endpoints[id_]=live.fetch(id_)[0]
    properties={}
    for id_ in PROPS:
        properties[id_]=live.fetch(id_)[0]
    admitted,excluded=complete_labels(rows,seeds,properties,endpoints)
    summary=dryrun(admitted)
    if summary["twohop_compositions_checked"]<1:
        raise NotAdmitted("F28_SOURCE_NO_IDENTIFIABLE_TWO_HOP")
    if not summary["equal_info_symbolic_control_parity"] or not summary["cold_restore_exact"]:
        raise NotAdmitted("F28_ASSOCIATION_CARRIER_PARITY_DRIFT")
    obj={
        "schema":SCHEMA, "frozen_protocol_commit":FROZEN,
        "source":"Wikidata Special:EntityData original first-party structured JSON",
        "structured_data_license":"CC0","license_source":"https://www.wikidata.org/wiki/Wikidata:Licensing",
        "prior_F27_source_budget_failure":"F27_TOTAL_SOURCE_BYTES_OUT_OF_BOUND",
        "seed_source_ids":list(SEEDS),"property_ids":list(PROPS),
        "endpoint_count":len(endpoint_ids), "source_inventory":inventory,
        "source_request_receipts":live.receipts,"source_bytes":live.total_bytes,
        "unlabeled_or_missing_edges_excluded":excluded,
        "admitted_rows":admitted,"admitted_source_sha256":digest(admitted),
        "carrier_summary":summary, "real_source_semantic_facts":True,
        "native_model_weights_edited":False,"source_donor_Qwen_alignment_verified":False,
        "scientific_pass":False,
        "classification":"DEV_REAL_CC0_ASSOCIATION_CUSTODY_ONLY",
    }
    if len(stable_json(obj))>MAX_RECEIPT:
        raise NotAdmitted("F28_OUTPUT_RECEIPT_OVER_CAP")
    return obj


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-custody-only",action="store_true",required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    try:
        obj=capture()
    except (NotAdmitted,TimeoutError,OSError,ValueError,UnicodeError) as exc:
        print("F28_SOURCE_BLOCKED="+type(exc).__name__+":"+str(exc),file=sys.stderr)
        return 2
    data=stable_json(obj)+b"\n"
    args.output.write_bytes(data)
    print("F28_REAL_FIRST_PARTY_SEMANTIC_FACTS=PASS")
    print("F28_REAL_ADMITTED_RELATIONSHIPS="+str(obj["carrier_summary"]["admitted_semantic_edges"]))
    print("F28_REAL_TWOHOP_COMPOSITIONS="+str(obj["carrier_summary"]["twohop_compositions_checked"]))
    print("F28_CANONICAL_NUMERIC_CARRIER_BYTES="+str(obj["carrier_summary"]["numeric_carrier_bytes"]))
    print("F28_SOURCE_READ_BYTES="+str(obj["source_bytes"]))
    print("F28_EXACT_SOURCE_RECEIPT_SHA256="+hashlib.sha256(data).hexdigest())
    print("F28_SCIENCE_AND_NATIVE_WEIGHT_EDIT=NONE")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
