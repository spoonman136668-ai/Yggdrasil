#!/usr/bin/env python3
"""QTR-01 F39: offline, fail-closed SOURCE HEADROOM screening; never science admission.

Only the separately captured development candidate is inspected. Protected
unseen-world outcomes, recipient models, network, and existing experiments are
out of scope. A successful screen cannot certify historical source disjointness.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
OLD = ROOT / "evidence/f32_source_snapshot.json"
EXT = ROOT / "evidence/f35_source_depth2_snapshot.json"
OLD_SHA = "e9ead9ac15e4ecbe4d99216cda43657e1aeb030d22f59fd852f8b99fa0d440eb"
EXT_SHA = "cf5ffeab63384a61e66e30930f16ce3af07df81cb28472b0142f7a5c6b673954"
SCHEMA = "yggdrasil.qtr01.f39.dev-claims-source-candidate.v1"
ITEM = re.compile(r"Q[1-9][0-9]*")
PROP = re.compile(r"P[1-9][0-9]*")
SAFE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}")
MINIMA = dict(verified_claims=1024, independent_root_groups=64,
              semantic_domains=4, distinct_predicate_ids=16,
              distinct_predicate_chains=8, witnessed_positive_queries=128)
MAX_BYTES = 4 * 1024 * 1024
MAX_CLAIMS = 8192


class Rejected(ValueError):
    pass


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def exact_archive(raw, expected, schema, rows_name, count):
    if sha256(raw) != expected:
        raise Rejected("PRIOR_SOURCE_HASH_MISMATCH")
    obj = json.loads(raw)
    rows = obj.get(rows_name)
    if obj.get("schema") != schema or type(rows) is not list or len(rows) != count:
        raise Rejected("PRIOR_SOURCE_SCHEMA_DRIFT")
    return rows


def prior_graph(old_raw, ext_raw):
    old = exact_archive(old_raw, OLD_SHA,
        "yggdrasil.qtr01.f31.first-party-all-language-fact-custody.v1",
        "typed_source_rows", 13)
    ext = exact_archive(ext_raw, EXT_SHA,
        "yggdrasil.qtr01.f35.pinned-witnessed-depth2-source-dev.v1",
        "added_witnessed_source_rows", 20)
    edges = {(r["s"], r["p"], r["o"]) for r in old + ext}
    if len(edges) != 33:
        raise Rejected("PRIOR_SOURCE_DUPLICATE")
    return edges, {x for s, _, o in edges for x in (s, o)}


def scan(candidate_raw, declared_sha256, old_raw, ext_raw):
    """Screen only already captured DEV facts; never request or select data."""
    if type(candidate_raw) is not bytes or len(candidate_raw) > MAX_BYTES:
        raise Rejected("CANDIDATE_BYTES_INVALID")
    if not re.fullmatch(r"[0-9a-f]{64}", str(declared_sha256)):
        raise Rejected("CANDIDATE_DIGEST_UNPINNED")
    if sha256(candidate_raw) != declared_sha256:
        raise Rejected("CANDIDATE_DIGEST_MISMATCH")
    prior_edges, prior_nodes = prior_graph(old_raw, ext_raw)
    obj = json.loads(candidate_raw)
    if (obj.get("schema") != SCHEMA
        or obj.get("stage") != "DEVELOPMENT_SOURCE_ONLY_NOT_SEALED"
        or obj.get("source") != "Wikidata structured claims"
        or obj.get("license") != "CC0"
        or obj.get("license_reference") != "https://www.wikidata.org/wiki/Wikidata:Licensing"
        or not isinstance(obj.get("immutable_source_revision"), str)
        or not obj["immutable_source_revision"].strip()):
        raise Rejected("SOURCE_IDENTITY_OR_LICENSE_UNVERIFIED")
    rows, receipts = obj.get("rows"), obj.get("subject_receipts")
    if (type(rows) is not list or not 0 < len(rows) <= MAX_CLAIMS
        or type(receipts) is not list or len(receipts) > MAX_CLAIMS):
        raise Rejected("INVALID_ROWS_OR_RECEIPTS")
    receipt_map = {}
    for receipt in receipts:
        if type(receipt) is not dict:
            raise Rejected("INVALID_RECEIPT")
        qid, rev, digest = (receipt.get(k) for k in ("qid", "revision", "raw_sha256"))
        if (type(qid) is not str or not ITEM.fullmatch(qid)
            or type(rev) is not int or rev <= 0
            or type(digest) is not str or not re.fullmatch("[0-9a-f]{64}", digest)
            or qid in receipt_map):
            raise Rejected("INVALID_OR_DUPLICATE_RECEIPT")
        receipt_map[qid] = rev
    groups = defaultdict(list)
    node_world = {}
    subjects = set()
    domains, predicates, edges, claim_ids = set(), set(), set(), set()
    for r in rows:
        if type(r) is not dict:
            raise Rejected("MALFORMED_ROW")
        s, p, o, world, domain = (r.get(k) for k in ("s", "p", "o", "world", "domain"))
        claim, revision, rank = (r.get(k) for k in ("source_claim", "source_revision", "rank"))
        if (not all(type(x) is str for x in (s, p, o, world, domain, claim, rank))
            or not ITEM.fullmatch(s) or not ITEM.fullmatch(o) or not PROP.fullmatch(p)
            or not SAFE.fullmatch(world) or not SAFE.fullmatch(domain)
            or not claim.startswith(s + "$") or len(claim) > 180
            or rank not in ("normal", "preferred")
            or r.get("qualifier_count") != 0
            or type(revision) is not int or receipt_map.get(s) != revision):
            raise Rejected("MALFORMED_OR_UNWITNESSED_CLAIM")
        e = (s, p, o)
        if e in edges or claim in claim_ids:
            raise Rejected("DUPLICATE_CANDIDATE_FACT")
        if e in prior_edges or s in prior_nodes or o in prior_nodes:
            raise Rejected("REUSED_PRIOR_SOURCE_ENTITY_OR_EDGE")
        for node in (s, o):
            if node in node_world and node_world[node] != world:
                raise Rejected("CROSS_WORLD_ENTITY_LEAK")
            node_world[node] = world
        claim_ids.add(claim)
        edges.add(e)
        groups[world].append(e)
        subjects.add(s)
        domains.add(domain)
        predicates.add(p)
    if set(receipt_map) != subjects:
        raise Rejected("UNUSED_OR_MISSING_SOURCE_RECEIPT")

    roots = set()
    chains = set()
    queries = set()
    for world, triples in groups.items():
        by_subject = defaultdict(list)
        for s, p, o in triples:
            by_subject[s].append((p, o))
        for s, p1, mid in triples:
            for p2, terminal in by_subject.get(mid, ()):
                roots.add((world, s))
                chains.add((p1, p2))
                queries.add((world, s, p1, p2, terminal))
    counts = dict(verified_claims=len(edges), independent_root_groups=len(roots),
                  semantic_domains=len(domains), distinct_predicate_ids=len(predicates),
                  distinct_predicate_chains=len(chains),
                  witnessed_positive_queries=len(queries))
    return {
        "schema": "yggdrasil.qtr01.f39.offline-headroom-screen.v1",
        "source_sha256": declared_sha256,
        "world_count": len(groups),
        "counts": counts,
        "proposed_minima_met": all(counts[k] >= n for k, n in MINIMA.items()),
        "prior_33_triple_overlap_rejected": True,
        "cross_world_node_leakage_rejected": True,
        "upstream_receipt_bytes_independently_authenticated": False,
        "complete_historical_consumed_source_ledger_verified": False,
        "heldout_families_sealed": False,
        "source_admitted": False,
        "scientific_first_use": False,
        "scientific_pass": False,
        "classification": "DEV_SOURCE_HEADROOM_ONLY_NOT_SCIENCE_ADMISSION"
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--sha256", required=True)
    args = parser.parse_args()
    try:
        result = scan(args.candidate.read_bytes(), args.sha256,
                      OLD.read_bytes(), EXT.read_bytes())
    except (Rejected, OSError, ValueError, KeyError, UnicodeError) as exc:
        print("F39_PRECHECK=BLOCKED:" + str(exc))
        return 2
    print("F39_PRECHECK=" + json.dumps(result, sort_keys=True, separators=(",", ":")))
    print("F39_NO_SOURCE_ADMISSION_OR_SCIENCE_FIRST_USE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
