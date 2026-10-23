"""P0F-C1: Prospective PUBLIC-only original-source exact-categorical history test.

Never a blind first-use experiment or an accepted native-cognition result.
Keeps original MR34E source acquisition/action law unchanged. Predicts SHA256
of the entire original next public frame, not the coarsened eight change bits.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import json
import math
import random
import sys
import time

from research.mr34e.public_alias import (
    ENGINES, raw_episode, source, peak_rss, canon
)

FROZEN = Path(__file__).with_name("FROZEN_PUBLIC_DEV_CONTRACT.json")
SCHEMA = "charter.p0fc1.original-public-discrete-conditional-history.dev.v1"
MASS_GLOBAL = 1.0
MASS_CURRENT = 8.0
MASS_HISTORY = 8.0
UNIFORM = 2.0 ** -256


def contract():
    d = json.loads(FROZEN.read_text(encoding="utf-8"))
    tr, dev = d["train_seeds"], d["development_seeds"]
    if (d.get("schema") != SCHEMA
        or d.get("predecessor_mr34e") != "3d952e897768b052a5bd89851f2aa0e354f97193"
        or d.get("sources") != {k: v["sha"] for k, v in ENGINES.items()}
        or len(tr) != 30 or len(dev) != 12
        or len(set(tr + dev)) != 42
        or any(type(v) is not int for v in tr + dev)
        or d.get("actions_per_reset_max") != 96
        or d.get("protected_first_use") is not False
        or d.get("no_hidden_state") is not True
        or d.get("no_native_model_training") is not True):
        raise ValueError("P0FC1_FROZEN_ROLE_SOURCE_OR_FIRST_USE_DRIFT")
    return d


def validate_row(r):
    if set(r) != {"seed", "step", "current_key", "history_key", "next_key"}:
        raise ValueError("P0FC1_EVENT_SCHEMA_DRIFT")
    if (not isinstance(r["current_key"], bytes)
        or len(r["current_key"]) != 33
        or not isinstance(r["history_key"], bytes)
        or len(r["history_key"]) != 99
        or not r["history_key"].startswith(r["current_key"])
        or not isinstance(r["next_key"], bytes)
        or len(r["next_key"]) != 32
        or type(r["seed"]) is not int or type(r["step"]) is not int):
        raise ValueError("P0FC1_ORIGINAL_PUBLIC_EVENT_BYTES_INVALID")


def train(rows):
    g = Counter()
    c = defaultdict(Counter)
    h = defaultdict(Counter)
    for r in rows:
        validate_row(r)
        y = r["next_key"]
        g[y] += 1
        c[r["current_key"]][y] += 1
        h[r["history_key"]][y] += 1
    if not g:
        raise ValueError("P0FC1_NO_TRAIN_ORIGINAL_SOURCE_EVENTS")
    return {"g": g, "c": dict(c), "h": dict(h), "n": sum(g.values())}


def probs(fit, r):
    validate_row(r)
    y = r["next_key"]
    g = (fit["g"][y] + MASS_GLOBAL * UNIFORM) / (fit["n"] + MASS_GLOBAL)
    cur = fit["c"].get(r["current_key"], {})
    nc = sum(cur.values())
    pc = (cur.get(y, 0) + MASS_CURRENT * g) / (nc + MASS_CURRENT)
    history = fit["h"].get(r["history_key"], {})
    nh = sum(history.values())
    ph = (history.get(y, 0) + MASS_HISTORY * pc) / (nh + MASS_HISTORY)
    if not (0 < pc <= 1 and 0 < ph <= 1):
        raise ValueError("P0FC1_PREDICTIVE_PROBABILITY_INVALID")
    return pc, ph, bool(nc), bool(nh)


def score(fit, held):
    scored = []
    for r in held:
        pc, ph, nc, nh = probs(fit, r)
        scored.append({
            "seed": r["seed"],
            "current_nats": -math.log(pc),
            "history_nats": -math.log(ph),
            "current_seen": nc,
            "history_seen": nh,
        })
    return scored


def cluster_review(scored):
    by_seed = defaultdict(list)
    for r in scored:
        by_seed[r["seed"]].append(r)
    if not by_seed:
        raise ValueError("P0FC1_NO_ORIGINAL_HELD_SOURCE_EVENTS")
    seeds = sorted(by_seed)
    deltas = []
    for seed in seeds:
        group = by_seed[seed]
        deltas.append(sum(z["current_nats"] - z["history_nats"]
                          for z in group) / len(group))
    rng = random.Random(2901)
    values = []
    for _ in range(1000):
        values.append(sum(deltas[rng.randrange(len(deltas))]
                          for _ in deltas) / len(deltas))
    values.sort()
    return {
        "independent_source_reset_clusters": len(seeds),
        "paired_seed_mean_nats_advantage": sum(deltas) / len(deltas),
        "paired_seed_95_percentile_bootstrap_interval": [
            values[24], values[974]
        ],
        "independent_seed_deltas_nats": deltas,
        "history_contexts_seen_in_original_train": sum(z["history_seen"] for z in scored),
        "current_contexts_seen_in_original_train": sum(z["current_seen"] for z in scored),
        "original_held_events": len(scored),
        "average_current_full_public_logloss_nats": sum(z["current_nats"] for z in scored) / len(scored),
        "average_two_step_public_history_logloss_nats": sum(z["history_nats"] for z in scored) / len(scored),
    }


def role_rows(engine, seeds):
    rows, receipts = [], []
    for seed in seeds:
        events, receipt = raw_episode(engine, None, seed, 96)
        if len(events) != receipt["native_original_source_steps"]:
            raise ValueError("P0FC1_ORIGINAL_EPISODE_SOURCE_COUNT_DRIFT")
        if any(r["seed"] != seed for r in events):
            raise ValueError("P0FC1_ORIGINAL_RESET_IDENTITY_LEAKAGE")
        rows.extend(events)
        receipts.append(receipt)
    return rows, receipts


def identity(rows):
    h = sha256()
    for r in rows:
        validate_row(r)
        h.update(r["current_key"])
        h.update(r["history_key"])
        h.update(r["next_key"])
        h.update(int(r["seed"]).to_bytes(4, "big"))
        h.update(int(r["step"]).to_bytes(4, "big"))
    return h.hexdigest()


def main(farama, pycolab):
    cfg = contract()
    roots = {k: source(farama if k == "FaramaMiniGridDoorKey8" else pycolab, k)
             for k in ENGINES}
    sys.path.insert(0, str(roots["FaramaMiniGridDoorKey8"]))
    sys.path.insert(0, str(roots["DeepMindPycolabApprehend"]))
    from research.mr27.natural_memory import source_guard
    source_guard(roots["FaramaMiniGridDoorKey8"])
    elapsed = time.process_time_ns()
    out = {}
    for engine in ENGINES:
        fit_rows, fit_receipts = role_rows(engine, cfg["train_seeds"])
        fitted = train(fit_rows)
        frozen_train_id = identity(fit_rows)
        dev_rows, dev_receipts = role_rows(engine, cfg["development_seeds"])
        scored = score(fitted, dev_rows)
        review = cluster_review(scored)
        if review["independent_source_reset_clusters"] != 12:
            raise ValueError("P0FC1_INDEPENDENT_HELD_CLUSTER_DRIFT")
        review.update({
            "original_fit_episodes": len(fit_receipts),
            "original_fit_steps": len(fit_rows),
            "original_dev_episodes": len(dev_receipts),
            "original_dev_steps": len(dev_rows),
            "frozen_fit_observation_action_outcome_sha256": frozen_train_id,
            "held_observation_action_outcome_sha256": identity(dev_rows),
            "original_fit_receipts_sha256": sha256(canon(fit_receipts).encode()).hexdigest(),
            "original_dev_receipts_sha256": sha256(canon(dev_receipts).encode()).hexdigest(),
            "source_commit": ENGINES[engine]["sha"],
        })
        if not review["history_contexts_seen_in_original_train"]:
            decision = "INSUFFICIENT_HELD_HISTORY_COVERAGE"
        elif review["paired_seed_95_percentile_bootstrap_interval"][0] > 0:
            decision = "BOUNDED_PUBLIC_HISTORY_LOGSCORE_SIGNAL_ONLY"
        else:
            decision = "HISTORY_ADVANTAGE_NOT_SHOWN_FOR_FROZEN_EXACT_CONTEXT_MODEL"
        review["local_public_development_disposition"] = decision
        out[engine] = review
    for k in ENGINES:
        source(roots[k], k)
    status = ("TWO_SOURCE_BOUNDED_DIAGNOSTIC_SIGNAL_NOT_FULL_P0FC1"
              if all(x["local_public_development_disposition"] ==
                     "BOUNDED_PUBLIC_HISTORY_LOGSCORE_SIGNAL_ONLY" for x in out.values())
              else "TWO_SOURCE_P0FC1_CONVENTIONAL_HISTORY_ADVANTAGE_UNPROVEN")
    print("P0FC1_ORIGINAL_CATEGORICAL_HISTORY=" + canon({
        "schema": SCHEMA,
        "frozen_protocol_sha256": sha256(FROZEN.read_bytes()).hexdigest(),
        "source_dev_reports": out,
        "public_source_cpu_ns": time.process_time_ns() - elapsed,
        "whole_process_peak_rss_bytes": peak_rss(),
        "source_bytes_labels_are_full_next_original_public_sha256": True,
        "model_selection_from_dev": False,
        "source_private_state_used": False,
        "protected_independent_first_use_consumed": False,
        "fully_trained_recurrent_pixelwise_control_present": False,
        "native_memory_cognition_demonstrated": False,
        "scientific_admission": "NOT_QUALIFIED",
        "disposition": status,
    }))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python -m research.p0fc1.original_history FARAMA PYCOLAB")
    main(sys.argv[1], sys.argv[2])
