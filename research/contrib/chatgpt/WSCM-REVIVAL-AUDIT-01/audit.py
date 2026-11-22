"""WSCM-REVIVAL-AUDIT-01: retrospective read-only native forecast gate.

No model training, new outcomes, original-world actions, or prospective claim.
Input files are the original frozen Amalgam public development traces, on the
same parent branch, verified by Git blob identity. Selector sees only losses
of already revealed previous outcomes; phase is report metadata, never an input.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

PARENT_AMALGAM = "86264b41a08d49f558418c0fba367f3a2636befa"
SCALE = 1_000_000
LOSS_DENOM = 2 * SCALE * SCALE
WINDOW = 16
MIN_COUNT = 4
MIN_GAIN_NUMERATOR = 1
MIN_GAIN_DENOMINATOR = 100
SEED_INPUTS = {
    818621: "7b3f2ff0b120d6557d4630de3461276d892b503f",
    818653: "bac19fb71d2a9918bd4ede1d3f2e6bae7b81dc48",
    818687: "449a186109b0b30ec98352b5b4565e2e96435b14",
}
EXPERTS = ("pinned", "unguarded", "fit_full", "fit_trailing", "fit_change_point", "guarded", "prequential_gate")
FITTED_CONTROLS = ("fit_full", "fit_trailing", "fit_change_point")
STAGE_COUNT = 3
STAGE_LENGTH = 24


def _git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _loss_pair(forecast, row):
    if (type(forecast) is not list or len(forecast) != 2
            or any(type(p) is not int or not 0 <= p <= SCALE for p in forecast)
            or type(row) is not dict or not {"s2", "y"}.issubset(row)
            or any(type(row[y]) is not int or row[y] not in (0, 1) for y in ("s2", "y"))):
        raise ValueError("REVIVAL_PUBLIC_FORECAST_CONTRACT")
    return sum((p - SCALE * y) ** 2 for p, y in zip(forecast, (row["s2"], row["y"]), strict=True))


def _score(loss_sum: int, count: int) -> float:
    return round(loss_sum / (LOSS_DENOM * count), 9)


def audit_rows(rows):
    """Compute prequential two-expert selector without labels/future rows."""
    if type(rows) is not list or len(rows) != STAGE_COUNT * STAGE_LENGTH:
        raise ValueError("REVIVAL_ROW_COUNT")
    history = []
    phases = {i: {"count": 0, "loss_sums": {k: 0 for k in EXPERTS}, "selected_unguarded": 0}
              for i in (1, 2, 3)}
    switches = 0
    previous = "pinned"
    unguarded_selected = 0
    seen = set()
    for i, receipt in enumerate(rows):
        if type(receipt) is not dict or receipt.get("stage") != 1 + i // STAGE_LENGTH:
            raise ValueError("REVIVAL_STAGE_CONTRACT")
        if type(receipt.get("id")) is not str or len(receipt["id"]) != 64 or receipt["id"] in seen:
            raise ValueError("REVIVAL_RECEIPT_CONTRACT")
        seen.add(receipt["id"])
        forecast = receipt.get("forecast")
        if type(forecast) is not dict or set(forecast) != set(EXPERTS) - {"prequential_gate"}:
            raise ValueError("REVIVAL_EXPERT_CONTRACT")
        prior = history[-WINDOW:]
        # Exact comparison of an average difference of squared errors, using
        # the same rational 0.01 gate for every seed; never read this outcome.
        gain_sum = sum(p - u for p, u in prior)
        choose_unguarded = (len(prior) >= MIN_COUNT and
                            gain_sum * MIN_GAIN_DENOMINATOR >=
                            MIN_GAIN_NUMERATOR * LOSS_DENOM * len(prior))
        chosen = "unguarded" if choose_unguarded else "pinned"
        if i and chosen != previous:
            switches += 1
        previous = chosen
        current = {k: _loss_pair(forecast[k], receipt.get("row")) for k in EXPERTS if k != "prequential_gate"}
        current["prequential_gate"] = current[chosen]
        phase = phases[receipt["stage"]]
        phase["count"] += 1
        if choose_unguarded:
            unguarded_selected += 1
            phase["selected_unguarded"] += 1
        for k in EXPERTS:
            phase["loss_sums"][k] += current[k]
        history.append((current["pinned"], current["unguarded"]))
    report = {}
    for stage, phase in phases.items():
        scores = {k: _score(phase["loss_sums"][k], phase["count"]) for k in EXPERTS}
        report[str(stage)] = {
            "episodes": phase["count"],
            "mean_brier": scores,
            "selected_unguarded": phase["selected_unguarded"],
            "best_fitted_control_brier_posthoc": min(scores[k] for k in FITTED_CONTROLS),
            "revival_gain_vs_pinned": round(scores["pinned"] - scores["prequential_gate"], 9),
        }
    return {"phases": report, "selected_unguarded": unguarded_selected, "switches": switches}


def source_trace_path(root: Path, seed: int) -> Path:
    return root / "research/contrib/chatgpt/CAUSAL-AMALGAM/staged-retention-dev-01" / f"seed-{seed}" / "trace.json"


def audit_sources(root: Path):
    seeds = []
    for seed, expected_blob in SEED_INPUTS.items():
        path = source_trace_path(root, seed)
        raw = path.read_bytes()
        if _git_blob(raw) != expected_blob:
            raise ValueError("REVIVAL_SOURCE_BLOB_MISMATCH")
        data = json.loads(raw)
        report = audit_rows(data)
        seeds.append({"seed": seed, "source_git_blob": expected_blob, **report})
    return {
        "schema": "yggdrasil.wscm.revival-audit-01.v1",
        "classification": "RETROSPECTIVE_SELECTOR_NO_GO",
        "parent_amalgam_sha": PARENT_AMALGAM,
        "frozen_window": WINDOW,
        "frozen_min_count": MIN_COUNT,
        "frozen_min_gain": "1/100",
        "score": "equal mean Brier over transition (s2) and reward (y)",
        "witnesses_reused": len(SEED_INPUTS) * STAGE_COUNT * STAGE_LENGTH,
        "new_world_outcomes": 0,
        "real_native_weights_modified": False,
        "prospective_science": False,
        "seeds": seeds,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    opts = parser.parse_args()
    result = audit_sources(opts.repo)
    opts.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("RETROSPECTIVE_SELECTOR_NO_GO: preserved consumed evidence; no new trials")


if __name__ == "__main__":
    main()
