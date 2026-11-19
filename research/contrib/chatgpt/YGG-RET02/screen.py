"""YGG-RET02: one preregistered retrospective context-addressed retrieval screen.

Uses already-consumed RET01 prequential traces. Does NOT train the native
learner, access new scientific data, or qualify integration.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PARENT = ROOT / "research/contrib/chatgpt/YGG-RET01"
BLOBS = {
    14071: ("6950dbecb1db8f3a5d3450d2678e604e0c0a8062",
            "058a0ef06154961677261a022824e52bcbd61295"),
    14072: ("2aa21a5a3565c608f3ddd117c158f51b3861d494",
            "9e8b3bbae6ac817c76e07c3797205273349a78e1"),
}
PRIOR = 0.125
LO, HI = 1 / 32, 31 / 32
BETAS = ("beta_full", "beta_window24", "beta_window32", "beta_discount95")
LATE = ("late_B", "late_return_A")

def require(value: bool, label: str):
    if not value:
        raise ValueError("YGG_RET02_" + label)

def git_blob(path: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD:" + path.relative_to(ROOT).as_posix()],
        cwd=ROOT, text=True, timeout=20).strip()

def inputs(seed: int):
    require(seed in BLOBS, "UNREGISTERED_SEED")
    paths = (PARENT / f"seed-{seed}-trace.json",
             PARENT / f"seed-{seed}-old-probe.json")
    for path, expected in zip(paths, BLOBS[seed]):
        require(git_blob(path) == expected, "SOURCE_BLOB_PIN")
    new, old = (json.loads(path.read_text("utf-8")) for path in paths)
    require(len(new) == 64 and len(old) == 32, "EXACT_TRACE_COUNTS")
    return new, old

def brier(pred, row):
    return ((pred[0] - row["s2"]) ** 2 +
            (pred[1] - row["y"]) ** 2) / 2

def likelihood(pred, row):
    p, q = pred
    return (p if row["s2"] else 1 - p) * (q if row["y"] else 1 - q)

def advance(weight, archive, live, row):
    a = weight * likelihood(archive, row)
    b = (1 - weight) * likelihood(live, row)
    require(a + b > 0, "ZERO_LIKELIHOOD")
    return min(HI, max(LO, a / (a + b)))

def public_key(record):
    views, row = record["public_views"], record["row"]
    require(type(views) is list and len(views) == 2 and
            all(type(v) is list and len(v) == 2 and
                all(type(bit) is int and bit in (0, 1) for bit in v)
                for v in views), "PUBLIC_VIEWS")
    require(type(row) is dict and set(row) == {"s1", "x1", "s2", "x2", "y"}
            and all(type(v) is int and v in (0, 1) for v in row.values())
            and row["s1"] == views[0][0], "PUBLIC_ROW")
    return tuple(views[0]), row["x1"]

def oracle_score(archive, live, row):
    # HINDSIGHT ceiling only. Never used by the learnable selector.
    ys = (row["s2"], row["y"])
    direction = [a - b for a, b in zip(archive, live)]
    norm = sum(d * d for d in direction)
    w = (min(1., max(0., -sum((b - y) * d for b, y, d
                            in zip(live, ys, direction)) / norm))
         if norm > 1e-14 else 0.)
    return brier([w * a + (1 - w) * b
                  for a, b in zip(archive, live)], row)

def mean(values):
    require(bool(values), "EMPTY_COHORT")
    return sum(values) / len(values)

def screen_seed(seed, new, old):
    weights = {}
    new_scores, old_scores = [], []
    seen = set()
    for section, events, output in (("new", new, new_scores),
                                    ("old", old, old_scores)):
        for i, event in enumerate(events):
            require(type(event) is dict and
                    type(event.get("source_id")) is str and
                    len(event["source_id"]) == 64 and
                    all(ch in "0123456789abcdef" for ch in event["source_id"]),
                    "PUBLIC_SOURCE_ID")
            require(event["source_id"] not in seen, "DUPLICATE_ID")
            seen.add(event["source_id"])
            if section == "new":
                require(event["old_seed"] == seed and
                        event["index"] == i % 32 and
                        event["world"] == i // 32, "SOURCE_SEQUENCE")
            else:
                require(event["old_seed"] == seed and
                        event["order"] == i and
                        event.get("already_consumed_diagnostic") is True,
                        "HISTORIC_DIAGNOSTIC_CUSTODY")
            key = public_key(event)
            a = event["forecasts"]["archive"]
            b = event["forecasts"]["live"]
            require(len(a) == len(b) == 2 and
                    all(type(v) in (int, float) and math.isfinite(v) and
                        0 <= v <= 1 for v in a + b), "FORECAST_RANGE")
            for name in ("archive", "live", "gate"):
                require(abs(brier(event["forecasts"][name], event["row"]) -
                            event["losses"][name]) < 1e-13,
                        "INPUT_NUMERIC_CUSTODY")
            weight = weights.get(key, PRIOR)
            forecast = [weight * aa + (1 - weight) * bb
                        for aa, bb in zip(a, b)]
            this = {
                "source_id": event["source_id"],
                "key": list(key[0]) + [key[1]],
                "weight_before": weight,
                "loss": brier(forecast, event["row"]),
                "archive": event["losses"]["archive"],
                "live": event["losses"]["live"],
                "global": event["losses"]["gate"],
                "mispaired": event["losses"]["mispaired_gate"],
                "oracle": oracle_score(a, b, event["row"]),
            }
            if section == "new":
                this["late"] = event["phase"] in LATE
                for arm in BETAS:
                    this[arm] = event["losses"][arm]
            # The witnessed outcomes affect only FUTURE predictions for
            # their own public address. Hidden phase/world/seed never keys.
            weights[key] = advance(weight, a, b, event["row"])
            this["weight_after"] = weights[key]
            output.append(this)
    late = [r for r in new_scores if r["late"]]
    require(len(late) == 16, "LATE_COHORT")
    new_means = {key: mean([r[key] for r in late])
                 for key in ("loss", "archive", "live", "global",
                             "mispaired", "oracle") + BETAS}
    best_beta = min(new_means[arm] for arm in BETAS)
    old_means = {key: mean([r[key] for r in old_scores])
                 for key in ("loss", "archive", "live", "global", "mispaired")}
    conditions = {
        "new_vs_global": new_means["loss"] <= new_means["global"] - .005,
        "new_vs_strongest_beta": new_means["loss"] <= best_beta - .005,
        "new_vs_mispaired": new_means["loss"] <= new_means["mispaired"] - .005,
        "old_vs_live": old_means["loss"] <= old_means["live"] - .01,
        "old_near_archive": old_means["loss"] <= old_means["archive"] + .03,
        "oracle_ceiling_not_exceeded": new_means["oracle"] <=
                                       new_means["loss"] + 1e-13,
    }
    return {
        "seed": seed, "events_new": 64,
        "already_consumed_old_probes": 32,
        "public_addresses_used": len(weights),
        "late": new_means,
        "best_beta": best_beta,
        "old": old_means,
        "conditions": conditions,
        "development_go": all(conditions.values()),
        "scored_new": new_scores,
        "scored_old": old_scores,
    }

def run():
    cohorts = []
    for seed in sorted(BLOBS):
        new, old = inputs(seed)
        cohorts.append(screen_seed(seed, new, old))
    return {
        "schema": "yggdrasil.ret02.context-addressed-retrospective.result.v1",
        "parent_sha": "f3b906c03730f7f3efb64683d77e00ba631dd409",
        "prereg_first_sha": "651fb51d4b2d03b0a639af92978ee8903f367e2c",
        "already_consumed": True,
        "native_training_performed": False,
        "science_pass": False,
        "deployment": "NONE",
        "replicas": cohorts,
        "development_go": all(x["development_go"] for x in cohorts),
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = run()
    body = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output:
        args.output.write_text(body, encoding="utf-8")
    print("YGG_RET02_" + ("DEVELOPMENT_GO" if report["development_go"]
                          else "DEVELOPMENT_NO_GO") +
          " RETROSPECTIVE_ONLY SCIENCE_NOT_PASS")
    for x in report["replicas"]:
        print(x["seed"], "keyed", "%.9f" % x["late"]["loss"],
              "global", "%.9f" % x["late"]["global"],
              "best_beta", "%.9f" % x["best_beta"],
              "oracle", "%.9f" % x["late"]["oracle"],
              "history", "%.9f" % x["old"]["loss"])

if __name__ == "__main__":
    main()
