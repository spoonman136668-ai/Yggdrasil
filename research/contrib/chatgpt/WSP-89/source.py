"""WSP89 one-shot CC0 Wikidata source capture; never used during model eval."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import urllib.error
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
PREREG = HERE / "prereg.json"
DATA = HERE / "data" / "wikidata-frozen.json"
URL = "https://www.wikidata.org/w/api.php"
LICENSE = "https://www.wikidata.org/wiki/Wikidata:Licensing"
USER_AGENT = "WSP89Research/0.1 (+https://github.com/spoonman136668-ai/Yggdrasil)"

def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")

def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()

def check_identifier(v: object, prefix: str) -> str:
    if not isinstance(v, str) or not re.fullmatch(prefix + r"[1-9][0-9]*", v):
        raise ValueError("invalid external Wikidata ID: " + repr(v))
    return v

def get_batch(ids: tuple[str, ...]) -> dict:
    params = urllib.parse.urlencode({
        "action": "wbgetentities", "ids": "|".join(ids),
        "props": "claims|labels|info", "languages": "en",
        "format": "json", "formatversion": 2,
    })
    req = urllib.request.Request(
        URL + "?" + params,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=35) as response:
        if response.status != 200:
            raise ValueError("Wikidata returned HTTP " + str(response.status))
        raw = response.read(32 * 1024 * 1024 + 1)
    if len(raw) > 32 * 1024 * 1024:
        raise ValueError("Wikidata payload too large")
    parsed = json.loads(raw)
    if not isinstance(parsed.get("entities"), dict):
        raise ValueError("missing Wikidata entities object")
    return {"payload": parsed, "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "request_ids": list(ids)}

def capture(out: pathlib.Path = DATA) -> dict:
    if out.exists():
        raise FileExistsError("one-shot source exists; refusing overwrite")
    spec = json.loads(PREREG.read_text(encoding="utf-8"))
    source = spec["source_collection"]
    ids = tuple(check_identifier(v, "Q") for v in source["source_ids"])
    predicates = tuple(check_identifier(v, "P") for v in source["predicates"])
    if len(ids) != len(set(ids)) or len(ids) > 24:
        raise ValueError("entity ID set invalid")
    batches = [get_batch(ids[i:i + 12]) for i in range(0, len(ids), 12)]
    entities = {}
    rows = []
    for batch in batches:
        for qid in batch["request_ids"]:
            entity = batch["payload"]["entities"].get(qid)
            if not isinstance(entity, dict) or entity.get("id") != qid:
                raise ValueError("missing/mismatched entity: " + qid)
            rev = entity.get("lastrevid")
            if type(rev) is not int or rev <= 0:
                raise ValueError("missing source revision " + qid)
            label = entity.get("labels", {}).get("en", {}).get("value")
            if not isinstance(label, str) or not label.strip():
                raise ValueError("missing verified English label " + qid)
            entities[qid] = {
                "id": qid, "label": label, "revision": rev,
                "revision_url": ("https://www.wikidata.org/wiki/Special:EntityData/"
                                 + qid + ".json?revision=" + str(rev)),
            }
            props = entity.get("claims", {})
            if not isinstance(props, dict):
                raise ValueError("bad claims mapping " + qid)
            for pid in predicates:
                statements = props.get(pid, [])
                if not isinstance(statements, list):
                    raise ValueError("bad property array")
                usable = []
                for claim in statements:
                    if claim.get("rank") == "deprecated":
                        continue
                    main = claim.get("mainsnak", {})
                    if (main.get("property") != pid or
                        main.get("snaktype") != "value" or
                        main.get("datatype") != "wikibase-item"):
                        continue
                    dv = main.get("datavalue", {})
                    value = dv.get("value", {})
                    if dv.get("type") != "wikibase-entityid" or not isinstance(value, dict):
                        continue
                    obj = value.get("id")
                    check_identifier(obj, "Q")
                    statement = claim.get("id")
                    if not isinstance(statement, str) or not statement.startswith(qid + "$"):
                        raise ValueError("missing original statement identity")
                    usable.append((claim["rank"], obj, statement))
                if not usable:
                    continue
                ranks = {x[0] for x in usable}
                rank = "preferred" if "preferred" in ranks else "normal"
                for _, obj, sid in usable:
                    if _ == rank:
                        rows.append({
                            "subject": qid, "predicate": pid, "object": obj,
                            "statement_id": sid, "revision": rev,
                            "source_url": entities[qid]["revision_url"],
                            "source_type": "wikidata_cc0_verified_snapshot",
                        })
    rows.sort(key=lambda x:(x["subject"], x["predicate"], x["object"],
                            x["statement_id"]))
    if len(rows) != len({x["statement_id"] for x in rows}):
        raise ValueError("duplicate source statement")
    involved = {x["subject"] for x in rows}
    rels = {x["predicate"] for x in rows}
    if (len(involved) < source["min_subjects"] or
        len(rows) < source["min_total_claims"] or
        len(rels) < source["min_predicates"]):
        raise ValueError("frozen source coverage criteria failed")
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    data = {
        "schema": "wsp89.wikidata-cc0-frozen-claim-source.v1",
        "license": "CC0-1.0", "license_url": LICENSE,
        "captured_utc": now, "endpoint": URL,
        "prereg_source_ids": list(ids), "prereg_predicates": list(predicates),
        "batches": [{"ids": x["request_ids"], "raw_sha256": x["raw_sha256"]}
                    for x in batches],
        "entities": [entities[q] for q in ids],
        "claims": rows,
        "claims_sha256": digest(rows),
        "source_use_limit": "WSP89 development only; not an independent heldout claim",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(json.dumps(data, sort_keys=True, indent=2,
                               ensure_ascii=True).encode("ascii") + b"\n")
    return {"schema": data["schema"], "subjects_with_claims": len(involved),
            "claims": len(rows), "predicates": sorted(rels),
            "claims_sha256": data["claims_sha256"],
            "frozen_file_sha256": hashlib.sha256(out.read_bytes()).hexdigest()}

def read_frozen(path: pathlib.Path = DATA, *, min_coverage: bool = True) -> dict:
    corpus = json.loads(path.read_text(encoding="utf-8"))
    spec = json.loads(PREREG.read_text(encoding="utf-8"))
    source = spec["source_collection"]
    if (corpus.get("schema") != "wsp89.wikidata-cc0-frozen-claim-source.v1" or
        corpus.get("license") != "CC0-1.0" or
        corpus.get("prereg_source_ids") != source["source_ids"] or
        corpus.get("prereg_predicates") != source["predicates"]):
        raise ValueError("corpus/protocol mismatch")
    rows = corpus["claims"]
    if digest(rows) != corpus["claims_sha256"]:
        raise ValueError("claim source hash invalid")
    entries = {x["id"]: x for x in corpus["entities"]}
    for row in rows:
        q = check_identifier(row["subject"], "Q")
        p = check_identifier(row["predicate"], "P")
        check_identifier(row["object"], "Q")
        if q not in entries or p not in source["predicates"]:
            raise ValueError("out-of-protocol claim")
        if (row["revision"] != entries[q]["revision"] or
            row["source_url"] != entries[q]["revision_url"] or
            not row["statement_id"].startswith(q + "$") or
            row["source_type"] != "wikidata_cc0_verified_snapshot"):
            raise ValueError("bad source attribution")
    if len(rows) != len({r["statement_id"] for r in rows}):
        raise ValueError("duplicate source statement IDs")
    if min_coverage and (len({r["subject"] for r in rows}) < source["min_subjects"]
                         or len(rows) < source["min_total_claims"]
                         or len({r["predicate"] for r in rows}) < source["min_predicates"]):
        raise ValueError("source coverage below prereg")
    return corpus

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-once", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.capture_once == args.verify:
        parser.error("choose exactly one action")
    report = capture() if args.capture_once else {
        "claim_count": len(read_frozen()["claims"]),
        "file_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
    }
    print("WSP89_SOURCE_RECEIPT=" + json.dumps(report, sort_keys=True))

if __name__ == "__main__":
    main()
