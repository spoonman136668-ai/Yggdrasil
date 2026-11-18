"""YGG-JEPA2-02: train BOTH latent specialists inside the actual native learner.

Input is the immutable original CKAD37 source-owned sequence of revealed public
causal interventions. The simulator, hidden regime labels, held answers, and
original source actor are NOT used. Each prediction precedes each update.
Source pilots were already consumed by CKAD37: DEV comparison, never new science.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_jepa2_multilearner import (
    ActionLatentSpecialist, NativeMultiLearner, STEPS,
)

HERE = Path(__file__).resolve().parent
SOURCE_DIR = HERE.parent / "CKAD-37"
PINS = {
    14071: "7f57794658a305e061d236ff15efca6cba1c4950",
    14072: "4ea587d99ea3852f396f9d79dfcafab64c3ab4f8",
}
EXPECTED_COUNT = {14071: 467, 14072: 452}
EVAL_PHASES = ("stable_A", "early_B", "late_B", "early_return_A", "late_return_A")
EVAL_ARMS = (
    "mixed", "jepa", "mispaired", "native_stream", "native_global",
    "beta_full", "beta_window24", "beta_window48", "beta_discount95", "sham",
)
CONTROL_ARMS = (
    "beta_full", "beta_window24", "beta_window48", "beta_discount95",
)
SCHEMA = "yggdrasil.jepa2-02.actual-native-source-development.v1"
PREREG = "f00d39793bff2091b7c74c05192a873725e675c2"
PARENT = "60634ab8c46b13039e021f28f8fa70bb6b69db96"


def check(test, label):
    if not test:
        raise RuntimeError("YGG_JEPA2_02_" + label)


def verify_source_blob(seed):
    path = SOURCE_DIR / f"pilot-{seed}.json"
    relative = path.relative_to(ROOT).as_posix()
    actual = subprocess.check_output(
        ["git", "rev-parse", "HEAD:" + relative], cwd=ROOT,
        text=True, timeout=20).strip()
    check(actual == PINS[seed], "IMMUTABLE_CKAD37_SOURCE_BLOB")
    payload = json.loads(path.read_text(encoding="utf8"))
    check(payload["seed"] == seed and payload["mode"] == "pilot"
          and payload["primary_scored"] is False and payload["case"]["seed"] == seed
          and payload["case"]["total_authentic_episodes"] == EXPECTED_COUNT[seed],
          "ORIGINAL_SOURCE_CUSTODY")
    return payload["case"]


def extract(entry):
    check(set(entry) >= {
        "source_id", "public_views", "public_row", "world", "index", "phase",
        "forecasts", "prequential_brier"
    }, "RECEIPT_FIELDS")
    views = tuple(tuple(v) for v in entry["public_views"])
    row = entry["public_row"]
    check(type(row) is dict and set(row) == {"s1", "x1", "s2", "x2", "y"},
          "PUBLIC_ROW_SHAPE")
    return entry["source_id"], views, row


def loss(p, q, row):
    check(0 <= p <= 1 and 0 <= q <= 1, "PREQUENTIAL_PROBABILITIES")
    return ((p - row["s2"]) ** 2 + (q - row["y"]) ** 2) / 2


def pack_scores(values):
    return {
        arm: {"brier": sum(v[arm] for v in values) / len(values),
              "episodes": len(values)}
        for arm in EVAL_ARMS
    }


def run_seed(seed, original):
    begun = time.perf_counter()
    cpu = time.process_time()
    events = original["original_episode_receipts"]
    check(len(events) == EXPECTED_COUNT[seed], "EPISODE_COUNT")
    grouped = {}
    for event in events:
        grouped.setdefault(event["world"], []).append(event)
    check(set(grouped) == {0, 1}, "SOURCE_WORLD_COUNT")
    results = []
    states = []
    all_scores = []
    for world in (0, 1):
        bundle = NativeMultiLearner()
        sham_t, sham_r = ActionLatentSpecialist("transition"), ActionLatentSpecialist("reward")
        prev = (0, 0)
        ids = set()
        world_scores = []
        rows = grouped[world]
        check(len(rows) == original["worlds"][world]["episodes"], "WORLD_EXACT_EPISODES")
        for t, entry in enumerate(rows):
            check(entry["world"] == world and entry["index"] == t,
                  "SOURCE_SEQUENCE_OR_ORDER")
            if t == 48:
                bundle = bundle.begin_stream()
                raw = bundle.checkpoint()
                bundle = NativeMultiLearner.restore(raw, digest(raw))
            identifier, views, row = extract(entry)
            check(identifier not in ids, "DUPLICATE_PUBLIC_RECEIPT")
            ids.add(identifier)
            predicted = bundle.predict(
                views, row["x1"], row["s2"], row["x2"], stream=t >= 48)
            # The same NativeEpisodeExperience instance must reproduce
            # CKAD37's original, source-locked prequential native predictions.
            original_p, original_q = entry["forecasts"]["native_stream"]
            check(abs(predicted["native"][0] - original_p) <= 1e-12 and
                  abs(predicted["native"][1] - original_q) <= 1e-12,
                  "ORIGINAL_NATIVE_PREQUENTIAL_FORECAST_PARITY")
            negative = (
                sham_t.probability(views, row["x1"]),
                sham_r.probability(views, row["x1"], row["s2"], row["x2"]),
            )
            values = {
                "mixed": loss(*predicted["mixed"], row),
                "jepa": loss(*predicted["jepa"], row),
                "mispaired": loss(*negative, row),
            }
            for arm in EVAL_ARMS[3:]:
                values[arm] = loss(*entry["forecasts"][arm], row)
                check(abs(values[arm] - entry["prequential_brier"][arm]) <= 1e-12,
                      "ORIGINAL_CONTROL_SOURCE_SCORE")
            phase = entry["phase"]
            check(phase in EVAL_PHASES + ("warm",), "EVALUATOR_PHASE")
            world_scores.append({"world": world, "source_id": identifier,
                                 "index": t, "phase": phase, "scores": values})
            all_scores.append({"world": world, "index": t, "phase": phase,
                               "source_id": identifier, "scores": values})
            # Train from OBSERVED native consequences, never future labels.
            bundle = bundle.observe(identifier, views, row)
            sham_t.observe(views, (row["x1"],), prev[0])
            sham_r.observe(views, (row["x1"], row["s2"], row["x2"]), prev[1])
            prev = (row["s2"], row["y"])
        check(bundle.native.info()["count"] == len(rows), "NATIVE_SOURCE_COUNT")
        original_native_sha = original["worlds"][world]["final_state_sha256"]
        check(digest(bundle.native.checkpoint()) == original_native_sha,
              "ORIGINAL_NATIVE_BYTE_EXACT_COLD_PRESERVATION")
        before = bundle.checkpoint()
        bundle = NativeMultiLearner.restore(before, digest(before))
        check(bundle.checkpoint() == before, "NEW_SPECIALISTS_COLD_REPLAY")
        check(bundle.transition.steps == len(rows) * STEPS and
              bundle.reward.steps == len(rows) * STEPS and
              sham_t.steps == len(rows) * STEPS and
              sham_r.steps == len(rows) * STEPS,
              "MATCHED_SPECIALIST_TRAINING_BUDGET")
        identifier, views, row = extract(rows[-1])
        check(bundle.observe(identifier, views, row) is bundle,
              "DUPLICATE_REPLAY_MUTATION")
        mutated = dict(row)
        mutated["y"] ^= 1
        try:
            bundle.observe(identifier, views, mutated)
        except ValueError:
            pass
        else:
            raise RuntimeError("YGG_JEPA2_02_CONFLICTING_REPLAY_NOT_REJECTED")
        check(bundle.checkpoint() == before, "CONFLICTING_REPLAY_CHANGED_LEARNER")
        result = {
            "world": world, "source_events": len(rows),
            "native_original_sha256": original_native_sha,
            "native_replayed_sha256": digest(bundle.native.checkpoint()),
            "multi_learner_sha256": digest(before),
            "multi_learner_bytes": len(before),
            "native_source_unchanged": True, "specialist_cold_restore": True,
            "learned_updates_per_specialist": bundle.transition.steps,
            "negative_updates_per_specialist": sham_t.steps,
            "last_source_id": identifier,
        }
        results.append(result)
        states.append({
            "world": world,
            "native_original_sha256": original_native_sha,
            "multi_learner_sha256": digest(before),
            "multi_learner_ascii": before.decode("ascii"),
            "negative": {"transition": sham_t.as_data(), "reward": sham_r.as_data()},
        })
    def aggregate(phase):
        relevant = [r["scores"] for r in all_scores if r["phase"] == phase]
        check(bool(relevant), "EVALUATION_PHASE_EMPTY")
        return pack_scores(relevant)
    metrics = {phase: aggregate(phase) for phase in EVAL_PHASES}
    pooled = [r["scores"] for r in all_scores
              if r["phase"] in ("late_B", "late_return_A")]
    metrics["pooled_late"] = pack_scores(pooled)
    primary = metrics["pooled_late"]
    early, returning = metrics["early_B"], metrics["late_return_A"]
    strong = min(primary[arm]["brier"] for arm in CONTROL_ARMS)
    b = primary["mixed"]["brier"]
    native = primary["native_stream"]["brier"]
    preds = {
        "vs_native": b <= native - 0.005,
        "vs_conventional": b <= strong - 0.010,
        "early_shift_nonregression": (
            early["mixed"]["brier"] <= early["native_stream"]["brier"] + 0.010),
        "old_world_return_nonregression": (
            returning["mixed"]["brier"] <= returning["native_stream"]["brier"] + 0.010),
        "true_pairing_signal": (
            primary["jepa"]["brier"] <= primary["mispaired"]["brier"] - 0.010),
    }
    check(sum(row["world"] in (0, 1) for row in all_scores) == EXPECTED_COUNT[seed],
          "COMPLETE_PREQUENTIAL_ACCOUNTING")
    return {
        "seed": seed, "source_blob": PINS[seed],
        "source_original_episode_count": EXPECTED_COUNT[seed],
        "source_outcome_count": 2 * EXPECTED_COUNT[seed],
        "worlds": results, "metrics": metrics,
        "strongest_control_brier": strong, "predicates": preds,
        "development_go": all(preds.values()),
        "science_pass": False,
        "resource_accounting": {
            "wall_seconds": time.perf_counter() - begun,
            "cpu_seconds": time.process_time() - cpu,
        },
    }, states, all_scores


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", required=True)
    args = parser.parse_args()
    output = Path(args.output_directory).resolve()
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for seed in (14071, 14072):
        original = verify_source_blob(seed)
        report, states, trace = run_seed(seed, original)
        (output / f"seed-{seed}-states.json").write_bytes(canonical(states))
        (output / f"seed-{seed}-trace.json").write_bytes(canonical(trace))
        results.append(report)
        print("YGG_JEPA2_02_SEED", seed,
              "training_outputs", report["source_original_episode_count"],
              "development_go", report["development_go"], flush=True)
    final = {
        "schema": SCHEMA, "prereg_first_sha": PREREG, "source_parent": PARENT,
        "source_blobs": PINS, "seeds": results,
        "development_go": all(r["development_go"] for r in results),
        "science_pass": False, "accepted_native": False,
        "deployment": "NONE", "source_first_use": False,
        "note": "Actual opt-in NativeEpisodeExperience plus independently trained latent specialists; CKAD37 source previously used and fully public, not a new scientific first-use."
    }
    (output / "result.json").write_bytes(canonical(final))
    print("YGG_JEPA2_02_NATIVE_TRAINING_COMPLETE",
          "DEVELOPMENT_GO" if final["development_go"] else "DEVELOPMENT_NO_GO",
          "SCIENCE_NOT_PASS", flush=True)


if __name__ == "__main__":
    main()

