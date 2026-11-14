"""MD35 allocation/custody preflight. No reserved cohort is generated or opened.

The MD35 preregistration precedes this module. This module may inspect
allocation arithmetic, not perform physical interventions or train models.
A later authoritative ledger collision check and independent first-use
authorization are required before a separate execution entry point exists.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCK = json.loads((HERE / "prereg.json").read_text("utf-8"))
assert LOCK["schema"] == "yggdrasil.dg1-md35-strong-conventional-controls-prereg.v1"
assert LOCK["status"] == "PREREGISTRATION_ONLY_BEFORE_MD35_MODEL_SOURCE_DATA_OR_SCORES"

SPLITS = {
    name: LOCK["reserved_cohorts_not_opened"][name]
    for name in ("train", "validation", "unfamiliar_transfer", "independent_cold")
}
FAMILIES = {
    "train": ("relay", "fork", "collider"),
    "validation": ("relay", "fork", "collider"),
    "unfamiliar_transfer": ("braid", "inhibitor", "crossbridge"),
    "independent_cold": ("braid", "inhibitor", "crossbridge"),
}
BLOCK_SIZES = {"train": 384, "validation": 96,
               "unfamiliar_transfer": 96, "independent_cold": 48}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def private_allocation(seed):
    """Harness-only allocation metadata. NEVER pass to a policy or trainer."""
    if type(seed) is not int:
        raise AssertionError("MD35_UNALLOCATED_OR_PROTECTED_COHORT")
    for cohort, spec in SPLITS.items():
        if spec["first"] <= seed <= spec["last"]:
            block, context = divmod(seed - spec["first"], 4)
            return {
                "cohort": cohort,
                "block": block,
                "context": context,
                "family": FAMILIES[cohort][block % 3],
                "offset": (block // 3) % 4,
                "rewire": (block // 12) % 2 == 1,
            }
    raise AssertionError("MD35_UNALLOCATED_OR_PROTECTED_COHORT")


def split_preflight():
    """Deterministic arithmetic only: does not import or instantiate MD34."""
    if set(SPLITS) != set(FAMILIES):
        raise AssertionError("MD35_COHORT_SCHEMA_DRIFT")
    intervals = []
    report = {}
    for cohort, spec in SPLITS.items():
        first, last = spec["first"], spec["last"]
        blocks = BLOCK_SIZES[cohort]
        if (last - first + 1 != blocks * 4 or
                spec["episodes"] != blocks * 4 or
                spec["blocks"] != blocks or
                tuple(spec["families"]) != FAMILIES[cohort] or
                (cohort in ("unfamiliar_transfer", "independent_cold") and
                 spec.get("unopened") is not True)):
            raise AssertionError("MD35_FROZEN_COHORT_ALLOCATION_CHANGED")
        intervals.append((first, last))
        matrix = {}
        for block in range(blocks):
            rows = [private_allocation(first + 4 * block + i)
                    for i in range(4)]
            if ([row["context"] for row in rows] != [0, 1, 2, 3] or
                    len({(row["family"], row["offset"], row["rewire"])
                         for row in rows}) != 1):
                raise AssertionError("MD35_BLOCK_CONTEXT_OR_LAW_DRIFT")
            key = (rows[0]["family"], rows[0]["offset"], rows[0]["rewire"])
            matrix[key] = matrix.get(key, 0) + 1
        expected = blocks // 24
        if len(matrix) != 24 or set(matrix.values()) != {expected}:
            raise AssertionError("MD35_FACTORIAL_ALLOCATION_IMBALANCED")
        report[cohort] = {
            "episodes": blocks * 4, "blocks": blocks,
            "families": list(FAMILIES[cohort]),
            "factorial_combinations": 24,
            "repetitions_per_combination": expected,
            "first": first, "last": last,
        }
    for i, (first, last) in enumerate(sorted(intervals)):
        if i and first <= sorted(intervals)[i - 1][1]:
            raise AssertionError("MD35_COLLIDING_SPLITS")
    if set(FAMILIES["train"]) & set(FAMILIES["unfamiliar_transfer"]):
        raise AssertionError("MD35_TRAIN_TRANSFER_FAMILY_LEAK")
    if intervals != [(61000, 62535), (63000, 63383),
                     (64000, 64383), (65000, 65191)]:
        raise AssertionError("MD35_FROZEN_RESERVED_RANGE_DRIFT")
    return {
        "schema": "md35.allocation-only-preflight.v1",
        "status": "ALLOCATION_ONLY_NOT_FIRST_USE",
        "worlds_instantiated": 0,
        "physical_actions": 0,
        "training_executed": False,
        "transfer_opened": False,
        "cold_opened": False,
        "source_parent_sha": LOCK["parent"]["exact_parent_sha"],
        "splits": report,
        "allocation_sha256": hashlib.sha256(canonical(report).encode("ascii")).hexdigest(),
    }


def require_first_use_clearance(*_args, **_kwargs):
    """Deliberate hard stop until ledger authority and first-use exist.

    No caller-supplied boolean, seed, token or fabricated ledger unlocks this
    boundary. The future source-locked run must use a separately approved
    entry point; it must not weaken this preflight after seeing results.
    """
    raise PermissionError("MD35_AUTHORITATIVE_LEDGER_AND_FIRST_USE_NOT_VERIFIED")


if __name__ == "__main__":
    print(canonical(split_preflight()))
