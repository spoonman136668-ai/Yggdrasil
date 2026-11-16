"""Source-free WSP-120 frozen 16-call, 24-world paired diagnostic.

This reducer never imports a world generator, invokes a learner, or qualifies
first-use. It cannot independently authenticate supplied summaries.
"""
from __future__ import annotations
from random import Random

ARMS = ("NUMERIC_GROW_ACTIVE", "NUMERIC_GROW_PASSIVE", "NUMERIC_FIXED3",
        "SYMBOLIC_ACTIVE", "NO_UPDATE")
FAMILIES = (0, 1, 2)
WORLD_COUNT, HELD, EXPOSURE, TIER = 24, 24, 16, 384
BOOTSTRAPS, BOOTSTRAP_SEED = 10000, 1200


def _invalid(reason):
    raise ValueError("WSP120_DIAGNOSTIC_" + reason)


def _quantile(sorted_values, p):
    x = p * (len(sorted_values) - 1)
    i = int(x)
    j = min(i + 1, len(sorted_values) - 1)
    return sorted_values[i] * (1 - (x - i)) + sorted_values[j] * (x - i)


def _paired_ci(differences):
    if len(differences) != WORLD_COUNT:
        _invalid("WORLD_COUNT")
    rng = Random(BOOTSTRAP_SEED)
    samples = [
        sum(differences[rng.randrange(WORLD_COUNT)]
            for _ in range(WORLD_COUNT)) / WORLD_COUNT
        for _ in range(BOOTSTRAPS)
    ]
    samples.sort()
    return {"mean_difference": sum(differences) / WORLD_COUNT,
            "ci95_lower": _quantile(samples, 0.025),
            "ci95_upper": _quantile(samples, 0.975),
            "resamples": BOOTSTRAPS, "seed": BOOTSTRAP_SEED,
            "sampling_unit": "paired_world"}


def _valid_arm(name, result):
    if type(result) is not dict:
        _invalid("ARM_TYPE")
    for field in ("correct", "wrong_confident", "abstained",
                  "held", "source_calls"):
        if type(result.get(field)) is not int or result[field] < 0:
            _invalid("ARM_COUNT")
    if (result["held"] != HELD or result["source_calls"] != EXPOSURE
            or sum(result[f] for f in
                   ("correct", "wrong_confident", "abstained")) != HELD):
        _invalid("ARM_INVARIANTS")
    receipt = result.get("source_sha256")
    if (type(receipt) is not str or len(receipt) != 64
            or any(c not in "0123456789abcdef" for c in receipt)):
        _invalid("SOURCE_RECEIPT")
    if name == "SYMBOLIC_ACTIVE":
        if result.get("cold_ok") is not None:
            _invalid("SYMBOLIC_COLD")
    elif result.get("cold_ok") is not True:
        _invalid("COLD_INTEGRITY")


def reduce_frozen_16_call_diagnostic(rows):
    """Compute the frozen DEV signal from previously scored summaries only.

    Required: 24 distinct world IDs, each with 3 law families, all 5 arms,
    384 visible edges, 16 verified queries and 24 held subjects per family.
    Bootstrap samples worlds (not family-world rows), seed 1200, 10k times.
    """
    if type(rows) not in (list, tuple) or len(rows) != WORLD_COUNT * 3:
        _invalid("ROW_COUNT")
    worlds = {}
    totals = {name: 0 for name in ARMS}
    confident_errors = 0
    for row in rows:
        if type(row) is not dict:
            _invalid("ROW_TYPE")
        seed, family = row.get("seed"), row.get("family")
        if type(seed) is not int or type(family) is not int:
            _invalid("WORLD_ID")
        if (family not in FAMILIES or type(row.get("tier")) is not int
                or row["tier"] != TIER
                or type(row.get("exposure")) is not int
                or row["exposure"] != EXPOSURE):
            _invalid("FROZEN_CONFIGURATION")
        arms = row.get("arms")
        if type(arms) is not dict or set(arms) != set(ARMS):
            _invalid("MATCHED_ARMS")
        if family in worlds.setdefault(seed, {}):
            _invalid("DUPLICATE_PAIR")
        for name in ARMS:
            _valid_arm(name, arms[name])
            totals[name] += arms[name]["correct"]
        passive_receipt = arms["NUMERIC_GROW_PASSIVE"]["source_sha256"]
        if any(arms[name]["source_sha256"] != passive_receipt
               for name in ("NUMERIC_FIXED3", "NO_UPDATE")):
            _invalid("PASSIVE_RECEIPTS_DIFFER")
        confident_errors += arms["NUMERIC_GROW_ACTIVE"]["wrong_confident"]
        worlds[seed][family] = {
            name: arms[name]["correct"] / HELD for name in ARMS}
    if (len(worlds) != WORLD_COUNT
            or any(set(v) != set(FAMILIES) for v in worlds.values())):
        _invalid("WORLD_PAIRS_INCOMPLETE")
    world_rates = {
        seed: {name: sum(fams[f][name] for f in FAMILIES) / 3
               for name in ARMS}
        for seed, fams in sorted(worlds.items())
    }
    comparisons = {
        "ACTIVE_MINUS_" + name: _paired_ci([
            rates["NUMERIC_GROW_ACTIVE"] - rates[name]
            for rates in world_rates.values()])
        for name in ("NUMERIC_FIXED3", "NUMERIC_GROW_PASSIVE", "SYMBOLIC_ACTIVE")
    }
    active_rate = totals["NUMERIC_GROW_ACTIVE"] / (WORLD_COUNT * 3 * HELD)
    fixed_gap = comparisons["ACTIVE_MINUS_NUMERIC_FIXED3"]
    signal = (active_rate >= 0.60 and fixed_gap["mean_difference"] >= 0.15
              and fixed_gap["ci95_lower"] > 0 and confident_errors == 0)
    return {
        "schema": "wsp120.sourcefree-frozen16-diagnostic.v1",
        "source_accessed": False,
        "scientific_status": "UNVERIFIED",
        "native_admission": False,
        "mechanism_signal": "DEVELOPMENT_SIGNAL" if signal
                            else "NO_DEVELOPMENT_SIGNAL",
        "worlds": WORLD_COUNT, "families": len(FAMILIES),
        "held_per_family": HELD, "source_calls": EXPOSURE, "tier": TIER,
        "correct_counts": totals, "active_accuracy": active_rate,
        "active_wrong_confident": confident_errors,
        "comparisons": comparisons,
        "note": "No original first-use, 32-call GRU, full resource-cost or "
                "unfamiliar-operator scientific evidence is established."
    }
