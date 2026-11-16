"""WSP-121 source-free, fail-closed reducer for independently scored transfer.

Never generates/opens public or protected worlds, queries source, trains a model,
or authorizes first-use. A SOURCE-FREE reduction cannot certify science.
"""
from __future__ import annotations

from math import isfinite
from random import Random

SCHEMA = "wsp121.sourcefree-transfer-evaluator.v1"
FAMILIES = (0, 1, 2)
ARMS = ("NUMERIC_FAST", "NUMERIC_RESET", "SYMBOLIC_TABLE_STRONG",
        "SYMBOLIC_ENUM", "TRAINED_MLP", "NO_UPDATE")
PRIMARY = "NUMERIC_FAST"
CONTROLS = ("NUMERIC_RESET", "SYMBOLIC_TABLE_STRONG", "TRAINED_MLP")
ORIGINAL_FIT_SEEDS = tuple(range(121000, 121024))
ORIGINAL_TRANSFER_SEEDS = tuple(range(121024, 121048))
RESERVED = set(range(121800, 121864)) | set(range(120800, 120864))
ENGINEERING = set(range(121900, 121904))
BOOTSTRAPS = 10000
BOOTSTRAP_SEED = 1210
HELD = 24
WORLDS = 24
MIN_TRANSFER_RATE = 0.8
MIN_RESET_GAIN = 0.25
MIN_SCIENCE_GAIN = 0.05
MIN_COST_SAVINGS = 0.5  # twofold matched time improvement


def _deny(name):
    raise ValueError("WSP121_REDUCER_" + name)


def _hex64(value):
    return (type(value) is str and len(value) == 64 and
            all(c in "0123456789abcdef" for c in value))


def _number(value):
    return type(value) in (float, int) and isfinite(value) and value >= 0


def _quantile(sorted_values, p):
    point = (len(sorted_values) - 1) * p
    i = int(point)
    j = min(i + 1, len(sorted_values) - 1)
    w = point - i
    return sorted_values[i] * (1.0 - w) + sorted_values[j] * w


def _stratified_paired_bootstrap(differences):
    """Paired transfer worlds, stratified into three shared-gate families."""
    if (type(differences) is not dict or set(differences) != set(FAMILIES)
            or any(len(differences[f]) != 8 for f in FAMILIES)):
        _deny("BOOTSTRAP_FAMILY_WORLD_COUNT")
    rng = Random(BOOTSTRAP_SEED)
    samples = []
    for _ in range(BOOTSTRAPS):
        samples.append(sum(
            differences[f][rng.randrange(8)] for f in FAMILIES
            for _ in range(8)
        ) / WORLDS)
    samples.sort()
    observed = sum(sum(differences[f]) for f in FAMILIES) / WORLDS
    return {"mean": observed, "ci95_lower": _quantile(samples, 0.025),
            "ci95_upper": _quantile(samples, 0.975), "resamples": BOOTSTRAPS,
            "seed": BOOTSTRAP_SEED, "unit": "paired_transfer_world_by_family"}


def _validate_cost(record):
    parts = record.get("wall_parts_seconds")
    if type(parts) is not dict or set(parts) != {
            "source", "train", "infer", "cold_restore"}:
        _deny("COST_PHASES")
    if any(not _number(v) for v in parts.values()):
        _deny("COST_PHASE_VALUE")
    total = record.get("wall_seconds")
    if not _number(total) or not (total > 0 and
            abs(total - sum(parts.values())) <= max(1e-6, total*1e-6)):
        _deny("COST_TOTAL")
    rss = record.get("peak_rss_bytes")
    if type(rss) is not int or rss <= 0:
        _deny("COST_PEAK_RSS")
    # A proxy is an approximate source, NOT direct calibrated energy evidence.
    energy = record.get("energy_proxy_joules")
    if not _number(energy) or energy <= 0:
        _deny("COST_ENERGY_PROXY")
    bytes_ = record.get("model_bytes")
    if type(bytes_) is not int or bytes_ < 0:
        _deny("COST_MODEL_BYTES")


def _validate_arm(name, record, budget):
    if type(record) is not dict:
        _deny("ARM_TYPE")
    for field in ("correct", "wrong_confident", "abstained",
                  "held", "source_calls"):
        if type(record.get(field)) is not int or record[field] < 0:
            _deny("ARM_COUNTS")
    if (record["held"] != HELD or record["source_calls"] != budget
            or sum(record[k] for k in
                   ("correct", "wrong_confident", "abstained")) != HELD):
        _deny("ARM_BUDGET_OR_HELD")
    if not _hex64(record.get("source_sha256")) or not _hex64(
            record.get("held_predictions_sha256")):
        _deny("ARM_RECEIPTS")
    if not _hex64(record.get("environment_sha256")):
        _deny("ARM_ENVIRONMENT")
    if name in ("NUMERIC_FAST", "NUMERIC_RESET"):
        if record.get("cold_ok") is not True or record.get("model_bytes") != 64:
            _deny("NUMERIC_COLD_OR_BYTES")
    if name == "TRAINED_MLP":
        if (record.get("converged") is not True
                or record.get("model_bytes") != 10000
                or record.get("trained_seeds") != [121951, 121952, 121953]
                or record.get("training_accuracy") != 1.0
                or not _number(record.get("training_loss"))
                or record["training_loss"] > 0.005):
            _deny("MLP_NOT_QUALIFIED")
    _validate_cost(record)


def _index_rows(rows):
    if type(rows) not in (list, tuple) or len(rows) != 48:
        _deny("ROW_COUNT")
    mapping, platforms = {}, set()
    for row in rows:
        if type(row) is not dict:
            _deny("ROW_TYPE")
        seed, fam, phase = row.get("seed"), row.get("family"), row.get("phase")
        if type(seed) is not int or type(fam) is not int or fam not in FAMILIES:
            _deny("WORLD_ID")
        if seed in RESERVED or seed in ENGINEERING or not (
                seed in ORIGINAL_FIT_SEEDS or seed in ORIGINAL_TRANSFER_SEEDS):
            _deny("PROTECTED_OR_UNREGISTERED_WORLD")
        expected_family = ((seed - 121000) if seed < 121024
                           else (seed - 121024)) // 8
        expected_phase = "fit" if seed < 121024 else "transfer"
        budget = 8 if expected_phase == "fit" else 4
        if (fam != expected_family or phase != expected_phase
                or type(row.get("visible_edges")) is not int
                or row["visible_edges"] != 384
                or row.get("legal_subjects") != 40
                or row.get("held_subjects") != HELD):
            _deny("FROZEN_SPLIT_OR_CONFIGURATION")
        if seed in mapping:
            _deny("DUPLICATE_WORLD")
        if not _hex64(row.get("fit_lineage_sha256")):
            _deny("FIT_LINEAGE")
        if row.get("held_labels_used_in_training") is not False:
            _deny("HELD_TRAINING_LEAK")
        platform = row.get("platform")
        if platform not in ("ubuntu-latest", "windows-2022"):
            _deny("PLATFORM")
        platforms.add(platform)
        arms = row.get("arms")
        if type(arms) is not dict or set(arms) != set(ARMS):
            _deny("STRONG_CONTROL_MISSING")
        for name in ARMS:
            _validate_arm(name, arms[name], budget)
        if len({arms[name]["source_sha256"] for name in ARMS}) != 1:
            _deny("UNMATCHED_SOURCE_OBSERVATIONS")
        if len({arms[name]["environment_sha256"] for name in ARMS}) != 1:
            _deny("UNMATCHED_MACHINE_ENVIRONMENT")
        mapping[seed] = row
    if len(platforms) != 1 or set(mapping) != set(
            ORIGINAL_FIT_SEEDS + ORIGINAL_TRANSFER_SEEDS):
        _deny("PLATFORM_OR_WORLD_SET")
    for fam in FAMILIES:
        lineage = {mapping[s]["fit_lineage_sha256"] for s in mapping
                   if mapping[s]["family"] == fam}
        if len(lineage) != 1:
            _deny("FAMILY_FIT_CUSTODY")
    return mapping, next(iter(platforms))


def _paired(mapping, control, metric):
    rows = {f: [] for f in FAMILIES}
    for seed in ORIGINAL_TRANSFER_SEEDS:
        row = mapping[seed]
        a, b = row["arms"][PRIMARY], row["arms"][control]
        if metric == "accuracy":
            diff = (a["correct"] - b["correct"]) / HELD
        elif metric == "time_savings":
            diff = 1.0 - a["wall_seconds"] / b["wall_seconds"]
        else:
            _deny("METRIC")
        rows[row["family"]].append(diff)
    return _stratified_paired_bootstrap(rows)


def reduce_scored_summaries(rows):
    """Offline diagnostics on externally supplied summaries, not source access."""
    data, platform = _index_rows(rows)
    transfer = [data[s] for s in ORIGINAL_TRANSFER_SEEDS]
    total_correct = {a: sum(row["arms"][a]["correct"] for row in transfer)
                     for a in ARMS}
    total_error = {a: sum(row["arms"][a]["wrong_confident"] for row in transfer)
                   for a in ARMS}
    accuracy = {a: total_correct[a] / (WORLDS * HELD) for a in ARMS}
    paired_accuracy = {name: _paired(data, name, "accuracy")
                       for name in CONTROLS}
    paired_savings = {name: _paired(data, name, "time_savings")
                      for name in ("SYMBOLIC_TABLE_STRONG", "TRAINED_MLP")}
    reset = paired_accuracy["NUMERIC_RESET"]
    development = (
        accuracy[PRIMARY] >= MIN_TRANSFER_RATE
        and reset["mean"] >= MIN_RESET_GAIN
        and reset["ci95_lower"] > 0
        and total_error[PRIMARY] == 0
        and all(row["arms"][PRIMARY]["cold_ok"] for row in transfer)
    )
    acc_advantage = all(
        paired_accuracy[c]["mean"] >= MIN_SCIENCE_GAIN and
        paired_accuracy[c]["ci95_lower"] > 0
        for c in ("SYMBOLIC_TABLE_STRONG", "TRAINED_MLP"))
    time_advantage = all(
        paired_savings[c]["ci95_lower"] >= MIN_COST_SAVINGS and
        accuracy[PRIMARY] >= accuracy[c]
        for c in ("SYMBOLIC_TABLE_STRONG", "TRAINED_MLP"))
    # Never promote from untrusted summaries, even if contrived summaries
    # trigger a candidate signal. Independent validation is external.
    return {
        "schema": SCHEMA, "source_accessed_by_reducer": False,
        "scientific_status": "UNVERIFIED", "scientific_pass": False,
        "native_admission": False,
        "development_signal": "PASS_CANDIDATE" if development else "NO_SIGNAL",
        "scientific_candidate": (
            "ACCURACY_CANDIDATE" if acc_advantage else
            "COST_CANDIDATE" if time_advantage else "NO_SUPERIORITY_CANDIDATE"
        ), "platform": platform, "fit_worlds": 24, "transfer_worlds": WORLDS,
        "transfer_held_per_arm": WORLDS * HELD,
        "total_verified_source_queries": 24*8 + 24*4,
        "total_correct": total_correct, "wrong_confident": total_error,
        "accuracy": accuracy, "paired_accuracy": paired_accuracy,
        "paired_wall_time_savings": paired_savings,
        "caveats": [
            "Input summary hashes are syntactically checked, not authenticated",
            "No independent source custody or first-use authorization is established",
            "Energy proxy is not measured calibrated energy",
            "Three shared gate families induce dependence; bootstrap stratified",
            "Cost advantage still requires verified process and machine parity",
            "No unsupplied computational primitive is proven",
        ]
    }


def compare_platforms(ubuntu_rows, windows_rows):
    """Source/held prediction parity gate; never normalizes away disagreement."""
    linux, lplatform = _index_rows(ubuntu_rows)
    windows, wplatform = _index_rows(windows_rows)
    if lplatform != "ubuntu-latest" or wplatform != "windows-2022":
        _deny("PLATFORM_PAIR")
    differences = []
    for seed in ORIGINAL_FIT_SEEDS + ORIGINAL_TRANSFER_SEEDS:
        if linux[seed]["fit_lineage_sha256"] != windows[seed]["fit_lineage_sha256"]:
            differences.append({"seed": seed, "kind": "FIT_LINEAGE_MISMATCH"})
        for name in ARMS:
            a, b = linux[seed]["arms"][name], windows[seed]["arms"][name]
            if a["source_sha256"] != b["source_sha256"]:
                differences.append({"seed": seed, "arm": name,
                                    "kind": "SOURCE_MISMATCH"})
            if a["held_predictions_sha256"] != b["held_predictions_sha256"]:
                differences.append({"seed": seed, "arm": name,
                                    "kind": "PREDICTION_MISMATCH"})
            if any(a[k] != b[k] for k in
                   ("correct", "wrong_confident", "abstained")):
                differences.append({"seed": seed, "arm": name,
                                    "kind": "SCORE_MISMATCH"})
    return {"schema": SCHEMA, "comparison": "SOURCE_FREE_PLATFORM_PARITY",
            "status": "INVALID" if differences else "DIAGNOSTIC_PARITY",
            "differences": differences, "scientific_pass": False,
            "source_accessed_by_reducer": False, "native_admission": False}
