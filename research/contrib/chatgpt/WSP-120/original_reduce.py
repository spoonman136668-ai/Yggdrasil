"""WSP120 read-only original result reduction and cross-platform custody."""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys

import diagnostic_reducer as D

SEEDS = tuple(range(120000, 120024))
TIERS = (192, 288, 384)
EXPOSURES = (0, 4, 8, 16, 32)
ARMS = D.ARMS
PLATFORMS = ("Linux", "Windows")
SHARDS = 8


def _fail(reason):
    raise ValueError("WSP120_ORIGINAL_INVALID_" + reason)


def read_results(directory):
    base = Path(directory)
    parts = {}
    for os_name in PLATFORMS:
        for shard in range(SHARDS):
            p = base / ("result-" + os_name + "-" + str(shard) + ".json")
            doc = json.loads(p.read_text())
            if (doc.get("schema") != "wsp120.original-public-shard.v1"
                    or doc.get("platform") != os_name or doc.get("shard") != shard
                    or doc.get("first_use") is not True
                    or doc.get("native_model_modified") is not False
                    or doc.get("protected_source_opened") is not False
                    or doc.get("seed_list") != list(SEEDS[shard::SHARDS])):
                _fail("SHARD_CUSTODY")
            parts[(os_name, shard)] = doc
    shas = {part["source_sha"] for part in parts.values()}
    if len(shas) != 1 or not next(iter(shas)):
        _fail("SOURCE_COMMIT_MISMATCH")
    return parts, next(iter(shas))


def reduce_original(directory):
    parts, source_sha = read_results(directory)
    platforms = {}
    for os_name in PLATFORMS:
        rows = {}
        for shard in range(SHARDS):
            for item in parts[(os_name, shard)]["rows"]:
                key = (item["seed"], item["tier"], item["family"],
                       item["exposure"])
                if key in rows:
                    _fail("DUPLICATE_ROW")
                if (key[0] not in SEEDS or key[1] not in TIERS
                        or key[2] not in (0, 1, 2)
                        or key[3] not in EXPOSURES):
                    _fail("OUTSIDE_FROZEN_SCOPE")
                arms = item.get("arms")
                required = set(ARMS) | (
                    {"TRAINED_GRU_PASSIVE"} if key[3] == 32 else set())
                if type(arms) is not dict or set(arms) != required:
                    _fail("MISSING_ARM")
                for arm, record in arms.items():
                    if (record.get("source_calls") != key[3]
                            or record.get("held") != 24
                            or record.get("correct", -1) < 0
                            or record.get("correct", 0)
                            + record.get("wrong_confident", 0)
                            + record.get("abstained", 0) != 24
                            or len(record.get("predictions", [])) != 24):
                        _fail("MALFORMED_COUNTS")
                rows[key] = item
        expected = {
            (seed, tier, fam, exp)
            for seed in SEEDS for tier in TIERS
            for fam in (0, 1, 2) for exp in EXPOSURES
        }
        if set(rows) != expected:
            _fail("INCOMPLETE_WORLD_COHORT")
        platforms[os_name] = rows

    # Source and numeric/symbolic predictions MUST reproduce across OS.
    disagreements = 0
    gru_disagreements = 0
    for key, a in platforms["Linux"].items():
        b = platforms["Windows"][key]
        for arm in ARMS:
            first, other = a["arms"][arm], b["arms"][arm]
            keys = ("correct", "wrong_confident", "abstained", "held",
                    "predictions", "source_calls", "source_sha256", "cold_ok",
                    "numeric_bytes", "law_declared",
                    "full_function_identified")
            if any(first.get(k) != other.get(k) for k in keys):
                disagreements += 1
        if key[3] == 32:
            g1, g2 = a["arms"]["TRAINED_GRU_PASSIVE"], b["arms"]["TRAINED_GRU_PASSIVE"]
            if any(g1.get(k) != g2.get(k) for k in
                   ("converged", "correct", "predictions")):
                gru_disagreements += 1
    if disagreements:
        _fail("CROSS_PLATFORM_NUMERIC_OR_SOURCE_DISAGREEMENT")

    linux = platforms["Linux"]
    diagnostic = D.reduce_frozen_16_call_diagnostic(
        [row for key, row in linux.items() if key[1] == 384 and key[3] == 16])
    counts = {}
    for tier in TIERS:
        counts[str(tier)] = {}
        for exposure in EXPOSURES:
            cases = [row for key, row in linux.items()
                     if key[1] == tier and key[3] == exposure]
            totals = {}
            for arm in ARMS:
                totals[arm] = {
                    "correct": sum(x["arms"][arm]["correct"] for x in cases),
                    "wrong_confident": sum(x["arms"][arm]["wrong_confident"]
                                           for x in cases),
                    "abstained": sum(x["arms"][arm]["abstained"] for x in cases),
                    "held": len(cases) * 24,
                    "full_function_identified": sum(bool(x["arms"][arm]
                        .get("full_function_identified")) for x in cases),
                }
            if exposure == 32:
                totals["TRAINED_GRU_PASSIVE"] = {
                    "correct": sum(x["arms"]["TRAINED_GRU_PASSIVE"]["correct"]
                                   for x in cases),
                    "converged": sum(bool(x["arms"]["TRAINED_GRU_PASSIVE"][
                        "converged"]) for x in cases),
                    "cases": len(cases),
                }
            counts[str(tier)][str(exposure)] = totals
    grus = [row["arms"]["TRAINED_GRU_PASSIVE"]
            for key, row in linux.items() if key[3] == 32]
    failures = sum(not g["converged"] for g in grus)
    source_calls = {name: 216 * 32 for name in ARMS}
    if any(len(parts[(os_name, shard)]["rows"]) != 3 * 3 * 5 * 3
           for os_name in PLATFORMS for shard in range(SHARDS)):
        _fail("SHARD_COUNTS")

    science = ("COMPARISON_INVALID_GRU_NONCONVERGENCE" if failures else
               "COMPARISON_INVALID_GRU_PLATFORM_DISAGREEMENT"
               if gru_disagreements else
               "PUBLIC_DEV_DIAGNOSTIC_ONLY_NO_NATIVE_ADVANTAGE_PROVEN")
    report = {
        "schema": "wsp120.original-public-aggregated.v1",
        "source_commit": source_sha,
        "original_worlds": list(SEEDS),
        "reserved_or_protected_source_opened": False,
        "native_model_modified": False,
        "world_tasks_per_platform": 216,
        "cross_platform_numeric_source_differences": disagreements,
        "cross_platform_gru_prediction_differences": gru_disagreements,
        "paired_full_graph_16_call": diagnostic,
        "coverage_checkpoints": counts,
        "full_32call_gru_nonconverged_cases": failures,
        "source_calls_per_arm_per_platform": source_calls,
        "development_classification": diagnostic["mechanism_signal"],
        "scientific_status": science,
        "scientific_pass": False,
        "limitations": (
            "Only supplied known grammar; no unsupplied primitive invention. "
            "Energy and whole-process resource parity, independent native "
            "retention/interference and external transfer unverified. "
            "A GRU nonconvergence invalidates scientific comparisons."
        ),
    }
    return report


def main():
    report = reduce_original(sys.argv[1])
    out = Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(report, sort_keys=True, separators=(",", ":"))
    out.write_text(raw + "\n")
    print("WSP120_ORIGINAL_PUBLIC=" + raw)
    print("WSP120_RESULT_SHA256=" + sha256(raw.encode()).hexdigest())


if __name__ == "__main__":
    main()
