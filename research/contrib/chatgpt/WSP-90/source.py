"""One-shot bounded CC BY-SA Wikipedia lead capture; never used during evaluation."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
SPEC = HERE / "prereg.json"
DATA = HERE / "data" / "wikipedia-leads-frozen.json"
API = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "WSP90Research/0.1 (+https://github.com/spoonman136668-ai/Yggdrasil; public noncommercial research)"

def canonical(v: object) -> bytes:
    return json.dumps(v, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")

def sha(v: object) -> str:
    return hashlib.sha256(canonical(v)).hexdigest()

def expected_titles() -> tuple[str, ...]:
    cfg = json.loads(SPEC.read_text(encoding="utf-8"))["source"]
    titles = []
    for group in ("fixture_pairs", "reserved_dev_pairs"):
        for row in cfg[group]:
            titles.extend((row["capital"], row["control"]))
    if len(titles) != 40 or len({t.casefold() for t in titles}) != 40:
        raise ValueError("expected 40 distinct frozen city page titles")
    return tuple(titles)

def fetch_batch(names: tuple[str, ...]) -> dict:
    if not names or len(names) > 20:
        raise ValueError("bounded request only")
    query = urllib.parse.urlencode({
        "action": "query", "prop": "extracts|revisions",
        "titles": "|".join(names), "exintro": "1", "explaintext": "1",
        "exchars": "1100", "exlimit": "20", "rvprop": "ids|timestamp",
        "redirects": "1", "formatversion": "2", "format": "json",
    })
    request = urllib.request.Request(API + "?" + query,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=50) as reply:
        if reply.status != 200:
            raise ValueError("Wikipedia API response " + str(reply.status))
        raw = reply.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError("oversized Wikipedia response")
    data = json.loads(raw)
    if "error" in data or not isinstance(data.get("query", {}).get("pages"), list):
        raise ValueError("Wikipedia API response malformed")
    return {"request": list(names), "response_sha256": hashlib.sha256(raw).hexdigest(),
            "query": data["query"]}

def capture(path: pathlib.Path = DATA) -> dict:
    if path.exists():
        raise FileExistsError("source snapshot already exists; refusing overwrite")
    names = expected_titles()
    fetched = [fetch_batch(names[i:i+20]) for i in range(0, 40, 20)]
    docs = []
    for batch in fetched:
        redirects = {}
        query = batch["query"]
        for change in query.get("normalized", []) + query.get("redirects", []):
            a, b = change.get("from"), change.get("to")
            if not isinstance(a,str) or not isinstance(b,str):
                raise ValueError("unexpected MediaWiki redirect/normalization")
            redirects[a] = b
        def resolve(v: str) -> str:
            seen = set()
            while v in redirects:
                if v in seen:
                    raise ValueError("redirect cycle")
                seen.add(v)
                v = redirects[v]
            return v
        pages = {page["title"]:page for page in query["pages"] if "title" in page}
        for title in batch["request"]:
            target = resolve(title)
            page = pages.get(target)
            if page is None or page.get("missing") or page.get("invalid"):
                raise ValueError(f"missing selected Wikipedia article: {title} -> {target}")
            if page.get("ns") != 0 or type(page.get("pageid")) is not int:
                raise ValueError("unexpected page namespace/ID")
            revisions = page.get("revisions", [])
            if len(revisions) != 1 or type(revisions[0].get("revid")) is not int:
                raise ValueError("missing article revision metadata")
            text = page.get("extract")
            if not isinstance(text,str) or len(text.strip()) < 90:
                raise ValueError("missing/too-short article lead: " + title)
            if len(text) > 1350:
                raise ValueError("article lead exceeded maximum extraction")
            docs.append({
                "requested_title": title, "resolved_title": page["title"],
                "text": text, "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "page_id": page["pageid"],
                "reported_revision_id": revisions[0]["revid"],
                "reported_revision_timestamp": revisions[0].get("timestamp"),
                "source_page_url": "https://en.wikipedia.org/wiki/" + urllib.parse.quote(page["title"].replace(" ","_")),
                "reported_revision_url": "https://en.wikipedia.org/w/index.php?oldid=" + str(revisions[0]["revid"]),
                "contributors_url": "https://en.wikipedia.org/w/index.php?title=" +
                    urllib.parse.quote(page["title"].replace(" ","_")) + "&action=history",
                "license": "CC BY-SA 4.0", "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            })
    if {d["requested_title"] for d in docs} != set(names) or len(docs) != 40:
        raise ValueError("Wikipedia title coverage incomplete/duplicated")
    docs.sort(key=lambda x:x["requested_title"])
    snapshot = {
        "schema":"wsp90.wikipedia-leads-frozen.v1",
        "license":"CC BY-SA 4.0",
        "notice":"English Wikipedia text copied under CC BY-SA 4.0, retain attribution and share-alike. Reported revision is capture-time metadata; the stored text/hash is the exact immutable experimental input and cannot guarantee historic extract API text equals all content of that revision.",
        "captured_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_api":API,
        "requests":[{"titles":b["request"],"response_sha256":b["response_sha256"]} for b in fetched],
        "titles":list(names), "documents":docs,
        "documents_sha256":sha(docs),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(snapshot,sort_keys=True,indent=2,ensure_ascii=True).encode("ascii")+b"\n")
    return {"file_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "documents_sha256":snapshot["documents_sha256"],
            "captured":len(docs), "raw_source_requests":len(fetched)}

def read_frozen(path: pathlib.Path = DATA) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if (data.get("schema") != "wsp90.wikipedia-leads-frozen.v1" or
        data.get("license") != "CC BY-SA 4.0" or
        data.get("titles") != list(expected_titles())):
        raise ValueError("frozen corpus differs from prospective protocol")
    docs = data.get("documents")
    if (not isinstance(docs,list) or len(docs) != 40 or
        sha(docs) != data.get("documents_sha256") or
        {r.get("requested_title") for r in docs} != set(expected_titles())):
        raise ValueError("frozen source integrity/coverage failure")
    for row in docs:
        if (hashlib.sha256(row["text"].encode("utf-8")).hexdigest() != row["text_sha256"]
            or row.get("license") != "CC BY-SA 4.0"
            or row.get("reported_revision_id",0) <= 0
            or not row.get("source_page_url","").startswith("https://en.wikipedia.org/wiki/")
            or len(row["text"].strip()) < 90):
            raise ValueError("missing source attribution or text hash")
        if any(key in row for key in ("capital","control","is_capital","label")):
            raise ValueError("ground-truth label present in source snapshot")
    return data

def main() -> None:
    a = argparse.ArgumentParser()
    group = a.add_mutually_exclusive_group(required=True)
    group.add_argument("--capture-once", action="store_true")
    group.add_argument("--verify", action="store_true")
    opts = a.parse_args()
    receipt = capture() if opts.capture_once else {
        "documents":len(read_frozen()["documents"]),
        "source_file_sha256":hashlib.sha256(DATA.read_bytes()).hexdigest()
    }
    print("WSP90_SOURCE_RECEIPT=" + json.dumps(receipt,sort_keys=True))

if __name__ == "__main__":
    main()
