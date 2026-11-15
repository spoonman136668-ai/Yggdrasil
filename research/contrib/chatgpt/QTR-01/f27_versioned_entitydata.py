#!/usr/bin/env python3
"""QTR-01 F27: first-party fixed-revision semantic association source custody.

No native Yggdrasil/Wingless/Hybrid weights, donor activations, model inference,
WSP science, training or accepted state are read or altered.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, build_opener, HTTPRedirectHandler

from f26_semantic_association import (
    SOURCE_ITEMS, PROPS, NotAdmitted, extract_seed_edges,
    complete_labels, dryrun, stable_json, digest, qnum,
)

FROZEN = "a808c2784f44c73d026abce2600a6a472530d47f"
SCHEMA = "yggdrasil.qtr01.f27.fixed-revision-entitydata-semantic-source.v1"
POLICY_PATH = Path(__file__).with_name("f27_prereg.json")
HOST = "www.wikidata.org"
PREFIX = "/wiki/Special:EntityData/"
SOURCE_CAP = 16777216
PER_ENTITY_CAP = 4194304
ENDPOINT_CAP = 48
RECEIPT_CAP = 786432
NO_RETRY = True
ID = re.compile(r"(?:Q|P)[1-9][0-9]*\Z")


def preflight():
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    selection = policy["selection"]
    limits = policy["limits"]
    if (policy.get("schema") != SCHEMA or policy.get("status") !=
        "FROZEN_BEFORE_CAPTURE_AND_CODE" or
        policy.get("source_host") != HOST or
        selection["seed_items"] != list(SOURCE_ITEMS) or
        selection["properties"] != list(PROPS) or
        selection["endpoint_max"] != ENDPOINT_CAP or
        selection["admitted_unique_triples_max"] != 1600 or
        limits["max_bytes_total"] != SOURCE_CAP or
        limits["max_bytes_per_response"] != PER_ENTITY_CAP or
        limits["max_triples"] != 1600 or
        limits["request_timeout_seconds"] != 15 or
        limits["output_receipt_max_bytes"] != RECEIPT_CAP or
        policy["scope_fences"].get("no_native_weights_or_owner_branch_edits") is not True):
        raise NotAdmitted("F27_FROZEN_POLICY_OR_SOURCE_SCOPE_DRIFT")
    return policy


def good_path(url, id_, revision=None):
    parsed = urlparse(url)
    desired_path = PREFIX + id_ + ".json"
    if parsed.scheme != "https" or parsed.netloc != HOST or parsed.path != desired_path:
        return False
    if parsed.username or parsed.password or parsed.fragment:
        return False
    if revision is None:
        return not parsed.query
    return parse_qs(parsed.query) == {"revision": [str(revision)]}


class SameHostRevisionOnly(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        before = urlparse(req.full_url)
        after = urlparse(newurl)
        if (after.scheme != "https" or after.netloc != HOST or
            after.path != before.path or after.query != before.query or
            code not in (301, 302, 307, 308)):
            raise NotAdmitted("F27_UNEXPECTED_ENTITY_SOURCE_REDIRECT")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class LiveEntityData:
    def __init__(self, opener=None):
        self.opener = opener if opener is not None else build_opener(SameHostRevisionOnly)
        self.receipts = []
        self.total_bytes = 0
        self.requested = set()

    def fetch(self, id_, revision=None):
        if not isinstance(id_, str) or not ID.fullmatch(id_):
            raise NotAdmitted("F27_INVALID_QID_OR_PID")
        if revision is not None and (type(revision) is not int or revision <= 0):
            raise NotAdmitted("F27_INVALID_PINNED_REVISION")
        unique = (id_, revision)
        if unique in self.requested:
            raise NotAdmitted("F27_DUPLICATE_SOURCE_REQUEST")
        self.requested.add(unique)
        url = "https://" + HOST + PREFIX + id_ + ".json"
        if revision is not None:
            url += "?revision=" + str(revision)
        if not good_path(url, id_, revision):
            raise NotAdmitted("F27_SOURCE_URL_NOT_FROZEN")
        request = Request(url, headers={
            "User-Agent": "Yggdrasil-QTR-01-F27/1.0 (public noncommercial research; contact GitHub project issues)",
            "Accept": "application/json",
            "Accept-Encoding": "identity",
        })
        with self.opener.open(request, timeout=15) as resp:
            if resp.status != 200 or resp.headers.get("Content-Encoding", "identity").lower() != "identity":
                raise NotAdmitted("F27_SOURCE_HTTP_STATUS_OR_ENCODING")
            blob = resp.read(PER_ENTITY_CAP + 1)
        if not 0 < len(blob) <= PER_ENTITY_CAP:
            raise NotAdmitted("F27_SOURCE_ENTITY_BYTES_OUT_OF_BOUND")
        self.total_bytes += len(blob)
        if self.total_bytes > SOURCE_CAP:
            raise NotAdmitted("F27_TOTAL_SOURCE_BYTES_OUT_OF_BOUND")
        try:
            parsed = json.loads(blob.decode("utf-8"))
        except (UnicodeError, ValueError) as exc:
            raise NotAdmitted("F27_INVALID_ENTITY_JSON") from exc
        if type(parsed) is not dict or "error" in parsed or type(parsed.get("entities")) is not dict:
            raise NotAdmitted("F27_FIRST_PARTY_ENTITY_DATA_ERROR")
        items = parsed["entities"]
        if set(items) != {id_}:
            raise NotAdmitted("F27_ENTITY_KEY_MISMATCH")
        entity = items[id_]
        if (type(entity) is not dict or entity.get("id") != id_ or
            "missing" in entity or "redirects" in entity or
            type(entity.get("lastrevid")) is not int or entity["lastrevid"] <= 0):
            raise NotAdmitted("F27_ENTITY_ID_OR_REVISION_MISSING")
        if revision is not None and entity["lastrevid"] != revision:
            raise NotAdmitted("F27_EXACT_PINNED_REVISION_MISMATCH")
        entity_digest = digest(entity)
        self.receipts.append({
            "entity": id_, "revision": entity["lastrevid"],
            "revision_pinned_read": revision is not None,
            "url": url, "raw_sha256": hashlib.sha256(blob).hexdigest(),
            "entity_canonical_sha256": entity_digest, "bytes": len(blob),
        })
        return entity, entity_digest


def capture(reader=None):
    preflight()
    reader = reader if reader is not None else LiveEntityData()
    seeds = {}
    # Keep all seeded identities fixed, with no label/statement-dependent
    # source scope change. F26 excludes unlabeled and unverifiable claims.
    for qid in SOURCE_ITEMS:
        seeds[qid] = reader.fetch(qid)[0]
    rows, inventory = extract_seed_edges(seeds)

    # Reread each source claim-bearing seed at its *exact* first-party revision.
    # This verifies every source statement against a stable URI and content hash.
    for qid in SOURCE_ITEMS:
        prior = reader.receipts[[r["entity"] for r in reader.receipts].index(qid)]
        pinned, pinned_sha = reader.fetch(qid, prior["revision"])
        if (pinned_sha != prior["entity_canonical_sha256"] or
            pinned != seeds[qid]):
            raise NotAdmitted("F27_PINNED_SEED_CONTENT_DIVERGENCE")

    # Source-blind deterministic bounded endpoint/predicate name lookup.
    endpoints = sorted(
        {row["o"] for row in rows if row["o"] not in seeds},
        key=lambda q: qnum(q, "Q")
    )[:ENDPOINT_CAP]
    endpoint_entities = {}
    for qid in endpoints:
        endpoint_entities[qid] = reader.fetch(qid)[0]
    prop_entities = {}
    for pid in PROPS:
        prop_entities[pid] = reader.fetch(pid)[0]

    admitted, missing = complete_labels(rows, seeds, prop_entities, endpoint_entities)
    result = dryrun(admitted)
    if result["admitted_semantic_edges"] <= 0:
        raise NotAdmitted("F27_NO_ADMITTED_FACTS")
    if not result["cold_restore_exact"] or not result["equal_info_symbolic_control_parity"]:
        raise NotAdmitted("F27_COLD_OR_SYMBOLIC_PARITY_MISMATCH")
    snapshot = {
        "schema": SCHEMA, "preregistration_commit": FROZEN,
        "source": "Wikidata first-party Special:EntityData JSON",
        "structured_data_license": "CC0", "first_party_license_url":
            "https://www.wikidata.org/wiki/Wikidata:Licensing",
        "source_original_f26_api_failure": "SOURCE_API_ERROR_CODE_maxlag",
        "source_item_order": list(SOURCE_ITEMS),
        "source_properties": list(PROPS),
        "selected_endpoint_count": len(endpoints),
        "source_read_receipts": reader.receipts, "source_bytes": reader.total_bytes,
        "inventory": inventory, "unlabeled_or_missing_endpoint_excluded": missing,
        "admitted_rows": admitted, "admitted_rows_sha256": digest(admitted),
        "association_carrier": result, "semantic_graph_not_causal_or_weight_learning": True,
        "actual_recipient_weights_edited": False, "scientific_pass": False,
        "classification": "DEV_FIRST_PARTY_VERSIONED_SEMANTIC_ASSOCIATION_SOURCE_ONLY",
    }
    if len(stable_json(snapshot)) > RECEIPT_CAP:
        raise NotAdmitted("F27_RECEIPT_SIZE_EXCEEDED")
    return snapshot


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--frozen-source-read-only", action="store_true", required=True)
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    try:
        obj = capture()
    except (NotAdmitted, OSError, TimeoutError, ValueError, UnicodeError) as exc:
        print("F27_SOURCE_BLOCKED=" + type(exc).__name__ + ":" + str(exc), file=sys.stderr)
        return 2
    raw = stable_json(obj) + b"\n"
    args.output.write_bytes(raw)
    print("F27_VERSIONED_FIRST_PARTY_CUSTODY=PASS")
    print("F27_ADMITTED_LABELED_ASSOCIATIONS=" + str(obj["association_carrier"]["admitted_semantic_edges"]))
    print("F27_EQUIVALENT_SYMBOLIC_2HOP_QUERIES=" + str(obj["association_carrier"]["twohop_compositions_checked"]))
    print("F27_NUMERIC_BYTES=" + str(obj["association_carrier"]["numeric_carrier_bytes"]))
    print("F27_SOURCE_RAW_BYTES=" + str(obj["source_bytes"]))
    print("F27_ARCHIVE_SHA256=" + hashlib.sha256(raw).hexdigest())
    print("F27_NO_MODEL_WEIGHTS_NO_SCIENTIFIC_PASS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
