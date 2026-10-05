"""Packaging-only selector-separation screen for Y089-FIXA.

This script may inspect only exact source identity and the pre-outcome
SOURCE_CONDITIONED/LOCAL_ONLY selector keys. It must not execute Y089 outcome
evaluation or inspect any target result.
"""
import hashlib
import importlib.util
import json
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

Y075_PATH = Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-retained-state-incompatibility-gate-075.py")
PREFIX = {"code": 41453, "structured": 14365, "technical-prose": 1454}

CANDIDATES = [
    {
        "name": "fixa-candidate-a",
        "sources": [
            {"domain":"code","repo":"apache/spark","commit":"2f4102c8117a087aba1324d52b268f7966670136","path":"core/src/main/scala/org/apache/spark/SparkContext.scala","git_blob":"f1cc057ef920e7349eb6b2ce9859fca1db854589"},
            {"domain":"structured","repo":"hashicorp/terraform","commit":"d8e7252bce0f6b363c3c5ef26eb6d343395b5f5f","path":"go.sum","git_blob":"be62f6851c7544d66cc825f2ebcbb3097f816d01"},
            {"domain":"technical-prose","repo":"curl/curl","commit":"efcbd5607896d509c6fd77a740b8f8eb9f7586b6","path":"docs/libcurl/curl_easy_setopt.md","git_blob":"23eda35203339b36d08956d1c17d8ea8924ae65d"},
        ],
    },
    {
        "name": "fixa-candidate-b",
        "sources": [
            {"domain":"code","repo":"apache/cassandra","commit":"b15526b4816518e415aa1046d7eb98232a0c1151","path":"src/java/org/apache/cassandra/db/ColumnFamilyStore.java","git_blob":"d69cf7354513d3444777b4c425d0147826c24953"},
            {"domain":"structured","repo":"denoland/deno","commit":"b4f08f127652d8442b4d3dbabc277aca3840bc1d","path":"Cargo.lock","git_blob":"c9c8358b30d3a3731d9b506140077c5ab54e39b7"},
            {"domain":"technical-prose","repo":"apache/spark","commit":"2f4102c8117a087aba1324d52b268f7966670136","path":"README.md","git_blob":"b57b53688f542a737acae3c6effa447ddb566fc5"},
        ],
    },
    {
        "name": "fixa-candidate-c",
        "sources": [
            {"domain":"code","repo":"apache/kafka","commit":"a81595abe8d48b0edd2ca9d42b221eb9465e8bad","path":"core/src/main/scala/kafka/server/KafkaApis.scala","git_blob":"b688a933e7635855c1869828a08cddbc22c2a7b1"},
            {"domain":"structured","repo":"rustdesk/rustdesk","commit":"e5bc204fe4dacc4db9c3cdb1f1338813986c89e7","path":"Cargo.lock","git_blob":"727ef11d78aa3347d96218dc273dc83179bb1a7f"},
            {"domain":"technical-prose","repo":"denoland/deno","commit":"b4f08f127652d8442b4d3dbabc277aca3840bc1d","path":"README.md","git_blob":"8173eb951062916cc112a8fb7c0e120b1c945975"},
        ],
    },
    {
        "name": "fixa-candidate-d",
        "sources": [
            {"domain":"code","repo":"dotnet/runtime","commit":"cd6580ff499dd9ae37656edcf2239bbab2362251","path":"src/coreclr/vm/methodtable.cpp","git_blob":"53a9c914dbc30764b218b59923645e1c4953a388"},
            {"domain":"structured","repo":"grafana/grafana","commit":"26f3b3bf5136ccbb2359b2ab62a06396a8b88f06","path":"go.sum","git_blob":"f02129429d6ad82a01dcd42eebdff40cff715fd9"},
            {"domain":"technical-prose","repo":"qemu/qemu","commit":"d7a65d1793d691d356a56833620f7d1e6f5d653b","path":"docs/system/introduction.rst","git_blob":"8d9ef61d262b276250aa2bc102c6834adcd96be2"},
        ],
    },
]

def load_y075():
    spec = importlib.util.spec_from_file_location("y075_fixa_screen", Y075_PATH)
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

def fetch_exact(src):
    url = f"https://raw.githubusercontent.com/{src['repo']}/{src['commit']}/{urllib.parse.quote(src['path'])}"
    req = urllib.request.Request(url, headers={"User-Agent":"yggdrasil-y089-fixa-packaging"})
    data = urllib.request.urlopen(req, timeout=90).read()
    blob = hashlib.sha1((f"blob {len(data)}\0").encode() + data).hexdigest()
    if blob != src["git_blob"]:
        raise RuntimeError(f"BLOB_MISMATCH:{src['repo']}:{src['path']}:{blob}")
    n = PREFIX[src["domain"]]
    if len(data) < n:
        raise RuntimeError(f"SOURCE_TOO_SHORT:{src['repo']}:{src['path']}:{len(data)}:{n}")
    return data[:n]

def screen(y075, candidate):
    with tempfile.TemporaryDirectory(prefix="y089-fixa-screen-") as td:
        root = Path(td)
        mapped = {}
        file_for = {"code":"code.bin","structured":"structured.bin","technical-prose":"technical-prose.bin"}
        key_for = {"code":"A","structured":"B","technical-prose":"C"}
        frozen_sources = []
        for src in candidate["sources"]:
            p = fetch_exact(src)
            (root / file_for[src["domain"]]).write_bytes(p)
            mapped[key_for[src["domain"]]] = {
                "file": file_for[src["domain"]],
                "sha256": hashlib.sha256(p).hexdigest(),
                "bytes": len(p),
            }
            frozen_sources.append({**src, "prefix_bytes": len(p), "prefix_sha256": hashlib.sha256(p).hexdigest()})
        y075.TARGET_SOURCES = mapped
        m = metrics()
        pool = list(y075.build_pool(root, m))
        if not pool:
            raise RuntimeError("EMPTY_SELECTOR_POOL:"+candidate["name"])
        source = sorted(pool, key=y075.source_rank)[0]
        local = sorted(pool, key=y075.local_rank)[0]
        accounting_ok = (
            m["target_source_identity_mismatch_count"] == 0
            and m["target_source_count"] == 3
            and m["target_total_source_bytes"] == 57272
            and m["base_training_identity_mismatch_count"] == 0
            and m["history_byte_budget_mismatch_count"] == 0
            and m["donor_row_count"] == 16
            and m["invalid_evaluation_rows"] == 0
        )
        return {
            "name": candidate["name"],
            "sources": frozen_sources,
            "selector_separated": tuple(source["key"]) != tuple(local["key"]),
            "source_conditioned_key": list(source["key"]),
            "local_only_key": list(local["key"]),
            "eligible_candidate_count": int(m["eligible_candidate_count"]),
            "accounting_ok": bool(accounting_ok),
        }

def main():
    y075 = load_y075()
    rows = [screen(y075, c) for c in CANDIDATES]
    eligible = [r for r in rows if r["accounting_ok"] and r["selector_separated"]]
    selected = eligible[:2]
    out = {
        "schema": "yggdrasil.y089-fixa-selector-screen.v1",
        "screening_basis": "outcome-blind selector separation only; candidate order frozen before screen",
        "candidate_count": len(rows),
        "eligible_count": len(eligible),
        "selected": [r["name"] for r in selected],
        "rows": rows,
        "child_outcome_use_count": 0,
        "target_answer_disclosure_count": 0,
        "target_context_mapping_disclosure_count": 0,
    }
    Path("y089-fixa-selector-screen.json").write_text(json.dumps(out, sort_keys=True, separators=(",",":"))+"\n", encoding="utf-8")
    print(json.dumps(out, sort_keys=True, separators=(",",":")))
    if len(selected) != 2:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
