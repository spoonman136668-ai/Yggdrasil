#!/usr/bin/env python3
"""QTR F26: bounded CC0 factual association custody and numeric IR, DEV ONLY.

The original Qwen atlas provides correlated direction IDs, not semantic facts.
This code obtains semantic relationships only from independently published
Wikidata entity statements/labels, not model outputs. Its packed numeric rows
are a portable OFFLINE carrier, NOT edited Yggdrasil/Wingless/Hybrid weights.
"""
import argparse
from collections import defaultdict, Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import struct
import sys
from urllib.parse import urlencode, urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler

PREREG_COMMIT = "d730681989445adf90ff1fb9c22f6e8085f94bd2"
POLICY = Path(__file__).with_name("f26_prereg.json")
SCHEMA = "yggdrasil.qtr01.f26.association-source-custody.v1"
ALLOWED_SOURCE = "https://www.wikidata.org/w/api.php"
ITEM_RE = re.compile(r"Q[1-9][0-9]*\Z")
PROP_RE = re.compile(r"P[1-9][0-9]*\Z")
SOURCE_ITEMS = ("Q2", "Q5", "Q17", "Q30", "Q42", "Q64", "Q76", "Q80",
                "Q90", "Q95", "Q142", "Q183", "Q312", "Q1490")
PROPS = ("P17", "P19", "P27", "P31", "P36", "P47", "P50", "P69",
         "P106", "P131", "P159", "P279", "P361", "P463", "P527")
MAX_RESPONSE = 4194304
MAX_TRANSFER = 16777216
MAX_EDGES = 1600
MAX_ENDPOINTS = 128
MAX_LABEL = 384


class NotAdmitted(ValueError):
    """Fail closed on source drift, unproven rights or malformed facts."""


def stable_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("utf-8")


def digest(obj):
    return sha256(stable_json(obj)).hexdigest()


def qnum(value, prefix):
    valid = ITEM_RE if prefix == "Q" else PROP_RE
    if not isinstance(value, str) or not valid.fullmatch(value):
        raise NotAdmitted("INVALID_ENTITY_OR_PROPERTY_ID")
    return int(value[1:])


def policy_preflight():
    obj = json.loads(POLICY.read_text(encoding="utf-8"))
    if (obj.get("schema") != SCHEMA or
        obj.get("status") != "FROZEN_BEFORE_SOURCE_CAPTURE_OR_IMPLEMENTATION" or
        obj.get("source_api") != ALLOWED_SOURCE or
        obj.get("source_items") != list(SOURCE_ITEMS) or
        obj.get("allowed_properties") != list(PROPS) or
        obj.get("api_max_bytes_per_response") != MAX_RESPONSE or
        obj.get("api_total_cap_bytes") != MAX_TRANSFER or
        obj.get("max_statements") != MAX_EDGES or
        obj.get("max_endpoint_labels") != MAX_ENDPOINTS or
        obj.get("fences", {}).get("no_model_weight_edit") is not True):
        raise NotAdmitted("F26_PREREG_OR_SOURCE_SCOPE_DRIFT")
    return obj


def safe_label(label):
    if (type(label) is not str or not label.strip() or
        len(label.encode("utf-8")) > MAX_LABEL or
        any(ord(x) < 32 or ord(x) == 127 for x in label)):
        raise NotAdmitted("BAD_SEMANTIC_SOURCE_LABEL")
    if ITEM_RE.fullmatch(label.strip()) or PROP_RE.fullmatch(label.strip()):
        raise NotAdmitted("UNINFORMATIVE_QP_LABEL")
    return label.strip()


def label_from_entity(entity):
    value = entity.get("labels", {}).get("en")
    if not isinstance(value, dict) or value.get("language") != "en":
        return None
    return safe_label(value.get("value"))


def parse_entity_batch(blob, requested_ids):
    obj = json.loads(blob.decode("utf-8"))
    if isinstance(obj, dict) and "error" in obj:
        error = obj.get("error")
        code = error.get("code") if type(error) is dict else "UNKNOWN"
        safe_code = re.sub(r"[^A-Za-z0-9_.-]", "", str(code))[:72]
        raise NotAdmitted("SOURCE_API_ERROR_CODE_" + safe_code)
    if not isinstance(obj, dict) or type(obj.get("entities")) is not dict:
        raise NotAdmitted("SOURCE_API_BAD_ENTITIES")
    found = obj["entities"]
    if set(found) != set(requested_ids):
        raise NotAdmitted("SOURCE_ENTITY_REPLY_MISMATCH")
    for key, value in found.items():
        if not isinstance(value, dict) or value.get("id") != key or "missing" in value:
            raise NotAdmitted("SOURCE_ENTITY_MISSING_OR_MISMATCH")
    return found


def extract_seed_edges(entities):
    """Read only independently sourced unqualified main Q->P->Q claims."""
    if set(entities) != set(SOURCE_ITEMS):
        raise NotAdmitted("F26_SOURCE_SEED_SET_CHANGED")
    rows = []
    inspected = 0
    for subject in SOURCE_ITEMS:
        source = entities[subject]
        if label_from_entity(source) is None:
            raise NotAdmitted("SOURCE_SEED_NO_ENGLISH_LABEL")
        revision = source.get("lastrevid")
        if type(revision) is not int or revision <= 0:
            raise NotAdmitted("SOURCE_REVISION_MISSING")
        claims = source.get("claims")
        if type(claims) is not dict:
            raise NotAdmitted("SOURCE_CLAIMS_MISSING")
        for predicate in PROPS:
            statements = claims.get(predicate, [])
            if type(statements) is not list:
                raise NotAdmitted("INVALID_CLAIMS_SHAPE")
            for claim in statements:
                inspected += 1
                if type(claim) is not dict or not isinstance(claim.get("id"), str):
                    raise NotAdmitted("INVALID_SOURCE_STATEMENT")
                if not claim["id"].startswith(subject + "$") or len(claim["id"]) > 180:
                    raise NotAdmitted("CLAIM_WITNESS_NOT_BOUND_TO_SUBJECT")
                if claim.get("rank") not in ("normal", "preferred", "deprecated"):
                    raise NotAdmitted("INVALID_RANK")
                if claim.get("rank") == "deprecated" or claim.get("qualifiers"):
                    continue
                snak = claim.get("mainsnak")
                if type(snak) is not dict or snak.get("snaktype") != "value":
                    continue
                dv = snak.get("datavalue", {})
                val = dv.get("value") if type(dv) is dict else None
                if (type(val) is not dict or val.get("entity-type") != "item" or
                    type(val.get("id")) is not str or
                    not ITEM_RE.fullmatch(val["id"])):
                    continue
                rows.append({
                    "s": subject, "p": predicate, "o": val["id"],
                    "s_label": label_from_entity(source),
                    "claim": claim["id"], "source_revision": revision
                })
    # Strict frozen maximum with declared stable precedence, not label-dependent.
    rows.sort(key=lambda x:(qnum(x["s"], "Q"), qnum(x["p"], "P"),
                            qnum(x["o"], "Q"), x["claim"]))
    seen = set()
    distinct = []
    for row in rows:
        triple = (row["s"], row["p"], row["o"])
        if triple not in seen:
            seen.add(triple)
            distinct.append(row)
    return distinct[:MAX_EDGES], {"claim_rows_inspected": inspected,
                                  "unqualified_item_edges": len(distinct),
                                  "truncated_to_frozen_budget": len(distinct) > MAX_EDGES}


def complete_labels(rows, entities, property_entities, endpoint_entities):
    all_english = {}
    for source in (entities, endpoint_entities):
        for qid, value in source.items():
            qnum(qid, "Q")
            if value.get("id") != qid or "missing" in value:
                raise NotAdmitted("ENDPOINT_ID_MISMATCH")
            label = label_from_entity(value)
            if label:
                if qid in all_english and label != all_english[qid]:
                    raise NotAdmitted("CONTRADICTORY_SNAPSHOT_LABEL")
                all_english[qid] = label
    prop_labels = {}
    for pid, entity in property_entities.items():
        if pid not in PROPS or entity.get("id") != pid:
            raise NotAdmitted("PROPERTY_REPLY_MISMATCH")
        label = label_from_entity(entity)
        if label:
            prop_labels[pid] = label
    admitted = []
    excluded_missing = 0
    for row in rows:
        if row["s"] not in all_english or row["o"] not in all_english or row["p"] not in prop_labels:
            excluded_missing += 1
            continue
        admitted.append({
            "s": row["s"], "p": row["p"], "o": row["o"],
            "s_label": all_english[row["s"]],
            "p_label": prop_labels[row["p"]],
            "o_label": all_english[row["o"]],
            "source_claim": row["claim"],
            "source_revision": row["source_revision"],
        })
    if not admitted:
        raise NotAdmitted("NO_SEMANTICALLY_LABELED_FACTS")
    validate_rows(admitted)
    return admitted, excluded_missing


def validate_rows(rows):
    if (type(rows) is not list or not 0 < len(rows) <= MAX_EDGES):
        raise NotAdmitted("INVALID_SOURCE_ROW_COUNT")
    observed = set()
    for row in rows:
        if type(row) is not dict or set(row) != {
            "s", "p", "o", "s_label", "p_label", "o_label", "source_claim", "source_revision"
        }:
            raise NotAdmitted("INVALID_ROW_SCHEMA")
        for k, prefix in (("s", "Q"), ("p", "P"), ("o", "Q")):
            qnum(row[k], prefix)
        if row["s"] not in SOURCE_ITEMS or row["p"] not in PROPS:
            raise NotAdmitted("NOT_FROZEN_SOURCE_OR_RELATION")
        for key in ("s_label", "p_label", "o_label"):
            safe_label(row[key])
        if (type(row["source_claim"]) is not str or
            not row["source_claim"].startswith(row["s"] + "$") or
            len(row["source_claim"]) > 180 or
            type(row["source_revision"]) is not int or row["source_revision"] <= 0):
            raise NotAdmitted("MISSING_PROVENANCE_WITNESS")
        triple = row["s"], row["p"], row["o"]
        if triple in observed:
            raise NotAdmitted("DUPLICATE_RELATIONSHIP")
        observed.add(triple)
    return True


class PackedAssociationWeights:
    """Integer adjacency coordinates; NOT recipient neural weights or causal learning."""
    def __init__(self, triples):
        expected = sorted(set(triples))
        if not expected or len(expected) != len(triples):
            raise NotAdmitted("INVALID_NUMERIC_RELATIONSHIP_SET")
        self.triples = tuple(expected)
        self.blob = b"".join(struct.pack("<III", *t) for t in self.triples)
        self.edges = set(self.triples)
        self.by_sp = defaultdict(set)
        for s, p, o in self.triples:
            self.by_sp[(s, p)].add(o)

    @classmethod
    def from_rows(cls, rows):
        validate_rows(rows)
        return cls([(qnum(x["s"], "Q"), qnum(x["p"], "P"), qnum(x["o"], "Q")) for x in rows])

    @classmethod
    def restore(cls, blob):
        if type(blob) is not bytes or len(blob) == 0 or len(blob) % 12:
            raise NotAdmitted("BAD_NUMERIC_SNAPSHOT")
        triples = [struct.unpack_from("<III", blob, offset)
                   for offset in range(0, len(blob), 12)]
        if not all(all(value > 0 for value in t) for t in triples):
            raise NotAdmitted("INVALID_NUMERIC_ID")
        candidate = cls(triples)
        if candidate.blob != blob:
            raise NotAdmitted("NONCANONICAL_NUMERIC_SNAPSHOT")
        return candidate

    def twohop(self, subject, predicate1, predicate2):
        found = set()
        for intermediate in self.by_sp.get((subject, predicate1), ()):
            found.update(self.by_sp.get((intermediate, predicate2), ()))
        return found


def symbolic_twohop(rows, subject, p1, p2):
    outgoing = {(qnum(r["s"], "Q"), qnum(r["p"], "P"), qnum(r["o"], "Q"))
                for r in rows}
    via = {o for s, p, o in outgoing if s == subject and p == p1}
    return {o for s, p, o in outgoing if s in via and p == p2}


def dryrun(rows):
    weights = PackedAssociationWeights.from_rows(rows)
    cold = PackedAssociationWeights.restore(weights.blob)
    queries = set()
    for a in weights.triples:
        for b in weights.triples:
            if a[2] == b[0]:
                queries.add((a[0], a[1], b[1]))
    if any(weights.twohop(*q) != symbolic_twohop(rows, *q) for q in queries):
        raise NotAdmitted("NUMERIC_VS_SYMBOLIC_COMPOSITION_MISMATCH")
    if cold.triples != weights.triples or cold.blob != weights.blob:
        raise NotAdmitted("NUMERIC_COLD_DRIFT")
    return {
        "admitted_semantic_edges": len(rows),
        "entities_with_english_labels": len(set(r["s"] for r in rows) | set(r["o"] for r in rows)),
        "distinct_predicates": len(set(r["p"] for r in rows)),
        "numeric_carrier_bytes": len(weights.blob),
        "numeric_snapshot_sha256": sha256(weights.blob).hexdigest(),
        "twohop_compositions_checked": len(queries),
        "equal_info_symbolic_control_parity": True,
        "cold_restore_exact": True,
        "architecture_native_weights_edited": False,
        "semantic_source_is_distinct_from_qwen_atlas": True,
        "causal_intervention_or_native_learning_proven": False,
    }


class RejectRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise NotAdmitted("HTTP_REDIRECT_NOT_ALLOWED")


class CustodyHTTP:
    def __init__(self):
        self.total = 0
        self.receipts = []
        self.opener = build_opener(RejectRedirect)

    def get(self, ids, props):
        if (type(ids) not in (tuple, list) or not ids or len(ids) > 20 or
            type(props) is not str or props not in ("info|claims|labels", "labels") or
            any(not isinstance(x, str) or not (ITEM_RE.fullmatch(x) or PROP_RE.fullmatch(x)) for x in ids)):
            raise NotAdmitted("UNFROZEN_REQUEST")
        parameters = {
            "action": "wbgetentities", "ids": "|".join(ids),
            "props": props, "languages": "en", "format": "json", "maxlag": "5"
        }
        url = ALLOWED_SOURCE + "?" + urlencode(parameters)
        parsed = urlparse(url)
        if parsed.hostname != "www.wikidata.org" or parsed.path != "/w/api.php":
            raise NotAdmitted("SOURCE_HOST_CHANGED")
        req = Request(url, headers={"User-Agent": "Yggdrasil-QTR-F26-CC0-Custody/1.0 (non-commercial bounded research; contact: GitHub repository issues)",
                                    "Accept": "application/json", "Accept-Encoding": "identity"})
        with self.opener.open(req, timeout=18) as resp:
            if resp.status != 200 or resp.headers.get("Content-Encoding", "identity").lower() != "identity":
                raise NotAdmitted("SOURCE_RESPONSE_STATUS_OR_ENCODING")
            blob = resp.read(MAX_RESPONSE + 1)
        if not 0 < len(blob) <= MAX_RESPONSE:
            raise NotAdmitted("SOURCE_RESPONSE_TOO_LARGE")
        self.total += len(blob)
        if self.total > MAX_TRANSFER:
            raise NotAdmitted("SOURCE_TRANSFER_EXCEEDED")
        self.receipts.append({"ids": list(ids), "props": props,
                              "url": url, "bytes": len(blob), "sha256": sha256(blob).hexdigest()})
        return parse_entity_batch(blob, ids)


def batched(items, n):
    for i in range(0, len(items), n):
        yield tuple(items[i:i+n])


def capture():
    policy_preflight()
    transfer = CustodyHTTP()
    seed_entities = {}
    for batch in batched(SOURCE_ITEMS, 2):
        seed_entities.update(transfer.get(batch, "info|claims|labels"))
    rows, inventory = extract_seed_edges(seed_entities)
    endpoint_ids = sorted(
        {r["o"] for r in rows if r["o"] not in SOURCE_ITEMS},
        key=lambda q: qnum(q, "Q")
    )[:MAX_ENDPOINTS]
    endpoints = {}
    for batch in batched(endpoint_ids, 20):
        endpoints.update(transfer.get(batch, "labels"))
    properties = {}
    for batch in batched(PROPS, 15):
        properties.update(transfer.get(batch, "labels"))
    admitted, excluded = complete_labels(rows, seed_entities, properties, endpoints)
    assessment = dryrun(admitted)
    witness = {
        "schema": SCHEMA, "preregistration_commit": PREREG_COMMIT,
        "source": "Wikidata first-party structured item/property claims",
        "license": "CC0 structured namespaces only",
        "license_policy": "https://www.wikidata.org/wiki/Wikidata:Licensing",
        "license_not_equivalent_to_source_claim_accuracy": True,
        "read_only_api": ALLOWED_SOURCE, "source_request_receipts": transfer.receipts,
        "total_source_bytes": transfer.total, "inventoried": inventory,
        "endpoints_label_queries": len(endpoint_ids), "excluded_missing_labels": excluded,
        "admitted_rows": admitted,
        "semantic_source_sha256": digest(admitted),
        "summary": assessment, "source_facts_not_causal_laws": True,
        "Qwen_feature_coordinate_alignment_verified": False,
        "model_weights_modified": False, "scientific_pass": False,
        "classification": "DEV_CC0_SEMANTIC_SOURCE_CUSTODY_ONLY",
    }
    if len(stable_json(witness)) > 524288:
        raise NotAdmitted("SEMANTIC_RECEIPT_TOO_LARGE")
    return witness


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--source-custody-only", action="store_true", required=True)
    cli.add_argument("--output", required=True, type=Path)
    args = cli.parse_args()
    try:
        witness = capture()
    except (NotAdmitted, ValueError, OSError, TimeoutError, UnicodeError) as exc:
        print("F26_SOURCE_CUSTODY_BLOCKED=" + type(exc).__name__ + ":" + str(exc), file=sys.stderr)
        return 2
    raw = stable_json(witness) + b"\n"
    args.output.write_bytes(raw)
    print("F26_SOURCE_CUSTODY=PASS")
    print("F26_SEMANTIC_EDGES=" + str(witness["summary"]["admitted_semantic_edges"]))
    print("F26_DISTINCT_PROPERTIES=" + str(witness["summary"]["distinct_predicates"]))
    print("F26_TWOHOP_PARITY=" + str(witness["summary"]["twohop_compositions_checked"]))
    print("F26_RELATIONSHIP_SNAPSHOT_SHA256=" + witness["semantic_source_sha256"])
    print("F26_RECEIPT_SHA256=" + sha256(raw).hexdigest())
    print("F26_NO_SCIENCE_OR_WEIGHT_EDIT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
