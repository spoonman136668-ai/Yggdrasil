"""WSCM-INTERFERENCE-01: source-pinned, read-only causal-cell error decomposition.

Reuses previously consumed Amalgam native prequential forecasts. This code
cannot generate outcomes, adapt a model, choose an action, or tune a selector.
Source and stage labels serve read-only forensic aggregation, not model inputs.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

SCALE = 1_000_000
SQUARED_SCALE = SCALE * SCALE
PARENT_SHA = "86264b41a08d49f558418c0fba367f3a2636befa"
SOURCES = {
    818621: "7b3f2ff0b120d6557d4630de3461276d892b503f",
    818653: "bac19fb71d2a9918bd4ede1d3f2e6bae7b81dc48",
    818687: "449a186109b0b30ec98352b5b4565e2e96435b14",
}


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def score(old: int, changed: int, outcome: int) -> int:
    if any(type(x) is not int for x in (old, changed, outcome)):
        raise ValueError("WSCM_CELL_TYPE")
    if not 0 <= old <= SCALE or not 0 <= changed <= SCALE or outcome not in (0, 1):
        raise ValueError("WSCM_CELL_RANGE")
    return (changed - outcome * SCALE) ** 2 - (old - outcome * SCALE) ** 2


def aggregate(rows: list) -> dict:
    """No choice or prediction: decompose the existing paired loss differences."""
    if type(rows) is not list or len(rows) != 72:
        raise ValueError("WSCM_CELL_ROW_COUNT")
    acc = {}
    stage_acc = {}
    seen = set()
    for i, record in enumerate(rows):
        if type(record) is not dict:
            raise ValueError("WSCM_CELL_RECORD")
        stage = record.get("stage")
        if type(stage) is not int or stage != 1 + i // 24:
            raise ValueError("WSCM_CELL_STAGE")
        ident = record.get("id")
        if (type(ident) is not str or len(ident) != 64
                or any(c not in "0123456789abcdef" for c in ident)
                or ident in seen):
            raise ValueError("WSCM_CELL_RECEIPT")
        seen.add(ident)
        views, row, forecast = record.get("views"), record.get("row"), record.get("forecast")
        if (type(views) is not list or len(views) != 2
                or any(type(v) is not list or len(v) != 2
                       or any(type(x) is not int or x not in (0, 1) for x in v)
                       for v in views) or type(row) is not dict or type(forecast) is not dict):
            raise ValueError("WSCM_CELL_INPUT")
        context = views[0][0]  # observed public coordinate; NOT a regime label
        action = row.get("x1")
        if type(action) is not int or action not in (0, 1):
            raise ValueError("WSCM_CELL_ACTION")
        if type(row.get("s1")) is not int or row["s1"] != context:
            raise ValueError("WSCM_CELL_PUBLIC_COORDINATE")
        old, new = forecast.get("pinned"), forecast.get("unguarded")
        if (type(old) is not list or type(new) is not list
                or len(old) != 2 or len(new) != 2):
            raise ValueError("WSCM_CELL_PREDICTION")
        delta = [score(old[j], new[j], row.get(field))
                 for j, field in enumerate(("s2", "y"))]
        for key, registry in [((stage, context, action), acc), ((stage,), stage_acc)]:
            stats = registry.setdefault(key, {"count": 0, "transition_delta_raw": 0, "reward_delta_raw": 0})
            stats["count"] += 1
            stats["transition_delta_raw"] += delta[0]
            stats["reward_delta_raw"] += delta[1]

    def present(registry):
        return [{"coordinates": list(k), "count": d["count"],
                 "transition_delta": round(d["transition_delta_raw"] / (SQUARED_SCALE * d["count"]), 9),
                 "reward_delta": round(d["reward_delta_raw"] / (SQUARED_SCALE * d["count"]), 9),
                 "transition_sum_raw": str(d["transition_delta_raw"]),
                 "reward_sum_raw": str(d["reward_delta_raw"])}
                for k, d in sorted(registry.items())]
    return {"cells": present(acc), "stages": present(stage_acc)}


def audit(root: Path) -> dict:
    results = []
    for seed, source_blob in SOURCES.items():
        path = root / ("research/contrib/chatgpt/CAUSAL-AMALGAM/"
                       f"staged-retention-dev-01/seed-{seed}/trace.json")
        raw = path.read_bytes()
        if git_blob(raw) != source_blob:
            raise ValueError("WSCM_CELL_SOURCE_BLOB")
        results.append({"seed": seed, "source_git_blob": source_blob,
                        **aggregate(json.loads(raw))})
    return {"schema": "yggdrasil.wscm.interference-01.v1",
            "source_parent_commit": PARENT_SHA,
            "development_trace_count": 216,
            "source_new_actions": 0, "new_training": 0,
            "unpreregistered_retrospective": True,
            "scientific_gain_verified": False,
            "seeds": results}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    args.out.write_text(json.dumps(audit(args.repo), indent=2, sort_keys=True) + "\n")
    print("WSCM_INTERFERENCE_RETROSPECTIVE: 3 original traces, no new actions")
