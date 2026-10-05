"""Packaging-only fresh-context screen for Y091.

This script inspects only exact source identity, accounting validity, and the
pre-outcome LOCAL_ONLY selector key. It does not execute any Y090/Y091 child
outcome evaluation or inspect target results.
"""
import hashlib
import importlib.util
import itertools
import json
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

Y075_PATH = Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-retained-state-incompatibility-gate-075.py")
PREFIX = {"code": 41453, "structured": 14365, "technical-prose": 1454}

BY_DOMAIN = {
    "code": [
        {"repo":"apache/flink","commit":"953f843d578572cc74343c1f1a1ddb64d5c5d3e5","path":"flink-runtime/src/main/java/org/apache/flink/runtime/jobmaster/JobMaster.java","git_blob":"39a29191b9761bf70fdeec265605e404d47d3e6d"},
        {"repo":"godotengine/godot","commit":"c016f22009aa773f0b2e6fce72baec168746491f","path":"scene/main/node.cpp","git_blob":"0dfe2995e5c78480e528f0b841ffff88d82d40bc"},
        {"repo":"blender/blender","commit":"0211557186502fa9b707501376ae8dc491ef386d","path":"source/blender/blenkernel/intern/object.cc","git_blob":"4a21291d56d24816d9f039957e05fd4ea3a53ae0"},
    ],
    "structured": [
        {"repo":"tauri-apps/tauri","commit":"79d3537620ddd136b81896b2048207e7c15e08b9","path":"Cargo.lock","git_blob":"a68f439de5de3c3c1ac0bb64892f275cfb4faf49"},
        {"repo":"vitejs/vite","commit":"10033218d239c927cdc375970b5741cce408e81b","path":"pnpm-lock.yaml","git_blob":"1429512d32326cad970a993ab6832080e5579292"},
        {"repo":"microsoft/playwright","commit":"ece43bfc2ba06bf310ddca1f984e5f11fcbb24f8","path":"package-lock.json","git_blob":"2b9d34577d8917800fb44fb3a3ed02128c059dd0"},
    ],
    "technical-prose": [
        {"repo":"scikit-learn/scikit-learn","commit":"c1f21786a8dc523c56ebb24f53b09dc14a57ea4d","path":"README.rst","git_blob":"cf30a4b3289a096a273ca490e1a846cf4c088795"},
        {"repo":"tensorflow/tensorflow","commit":"1d968a6e886854cd650b7c378baee96effdef3dc","path":"README.md","git_blob":"2ada91b134b2bc6daa60ca6265f1290f38a748c1"},
        {"repo":"fastapi/fastapi","commit":"52159d7e7018df55b57a0b8fdd6c1193e48b2b57","path":"README.md","git_blob":"3db2f525237857e1ab125615b28533e288d1833a"},
    ],
}

_FETCH_CACHE = {}

def load_y075():
    spec = importlib.util.spec_from_file_location("y075_y091_screen", Y075_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Y075_IMPORT_SPEC_FAILED")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def metrics():
    return {
        "target_source_identity_mismatch_count": 0.0,
        "target_source_count": 0.0,
        "target_total_source_bytes": 0.0,
        "base_training_identity_mismatch_count": 0.0,
        "history_byte_budget_mismatch_count": 0.0,
        "donor_row_count": 0.0,
        "induction_source_bytes": 0.0,
        "eligible_candidate_count": 0.0,
        "invalid_evaluation_rows": 0.0,
    }

def fetch_exact(domain, src):
    key = (domain, src["repo"], src["commit"], src["path"], src["git_blob"])
    if key in _FETCH_CACHE:
        return _FETCH_CACHE[key]
    url = f"https://raw.githubusercontent.com/{src['repo']}/{src['commit']}/{urllib.parse.quote(src['path'])}"
    data = urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent":"yggdrasil-y091-packaging"}),
        timeout=90,
    ).read()
    blob = hashlib.sha1((f"blob {len(data)}\0").encode() + data).hexdigest()
    if blob != src["git_blob"]:
        raise RuntimeError(f"BLOB_MISMATCH:{src['repo']}:{src['path']}:{blob}")
    n = PREFIX[domain]
    if len(data) < n:
        raise RuntimeError(f"SOURCE_TOO_SHORT:{src['repo']}:{src['path']}:{len(data)}:{n}")
    out = data[:n]
    _FETCH_CACHE[key] = out
    return out

def screen(y075, idx, combo):
    with tempfile.TemporaryDirectory(prefix="y091-screen-") as td:
        root = Path(td)
        mapped = {}
        file_for = {"code":"code.bin","structured":"structured.bin","technical-prose":"technical-prose.bin"}
        key_for = {"code":"A","structured":"B","technical-prose":"C"}
        frozen = []
        for domain, src in combo:
            data = fetch_exact(domain, src)
            filename = file_for[domain]
            (root / filename).write_bytes(data)
            mapped[key_for[domain]] = {"file":filename,"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data)}
            frozen.append({"domain":domain, **src, "prefix_bytes":len(data), "prefix_sha256":hashlib.sha256(data).hexdigest()})
        y075.TARGET_SOURCES = mapped
        m = metrics()
        pool = list(y075.build_pool(root, m))
        local = sorted(pool, key=y075.local_rank)[0] if pool else None
        accounting_ok = (
            local is not None
            and m["target_source_identity_mismatch_count"] == 0
            and m["target_source_count"] == 3
            and m["target_total_source_bytes"] == 57272
            and m["base_training_identity_mismatch_count"] == 0
            and m["history_byte_budget_mismatch_count"] == 0
            and m["donor_row_count"] == 16
            and m["invalid_evaluation_rows"] == 0
        )
        return {
            "name": f"y091-fresh-{idx:02d}",
            "sources": frozen,
            "local_only_key": list(local["key"]) if local is not None else None,
            "eligible_candidate_count": int(m["eligible_candidate_count"]),
            "accounting_ok": bool(accounting_ok),
        }

def main():
    y075 = load_y075()
    rows = []
    selected = []
    used = set()
    combos = list(itertools.product(
        [("code", x) for x in BY_DOMAIN["code"]],
        [("structured", x) for x in BY_DOMAIN["structured"]],
        [("technical-prose", x) for x in BY_DOMAIN["technical-prose"]],
    ))
    for idx, combo in enumerate(combos):
        row = screen(y075, idx, combo)
        rows.append(row)
        if not row["accounting_ok"]:
            continue
        ids = {(s["repo"],s["commit"],s["path"],s["git_blob"],s["prefix_bytes"]) for s in row["sources"]}
        if used.isdisjoint(ids):
            selected.append(row)
            used.update(ids)
            if len(selected) == 2:
                break
    out = {
        "schema":"yggdrasil.y091-fresh-selector-screen.v1",
        "screening_basis":"outcome-blind accounting validity and LOCAL_ONLY selector existence; deterministic 3x3x3 source cross-product; first two pairwise source-disjoint valid contexts admitted",
        "candidate_universe_count":len(combos),
        "screened_count":len(rows),
        "selected":[x["name"] for x in selected],
        "selected_source_disjoint":len(selected)==2,
        "rows":rows,
        "child_outcome_use_count":0,
        "target_answer_disclosure_count":0,
        "target_context_mapping_disclosure_count":0,
    }
    Path("y091-fresh-selector-screen.json").write_text(json.dumps(out,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print(json.dumps(out,sort_keys=True,separators=(",",":")))
    if len(selected)!=2:
        raise SystemExit(2)

if __name__=="__main__":
    main()
