"""Synthetic-only MD33 custody wrapper around immutable MD32 physics.

Only this harness constructs hidden-law world specs. Model controllers must
receive World.observe()/World.step() public outputs, never spec or seed.
No MD32 fixture, MD29-31, or official MD32 first-use seed can enter.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "dg1-md32-20261114"))
from compositional_relay import (BASES, TRAIN, TRANSFER, RelayWorld, ZERO,
                                 canonical, digest, run_public_two_probe)

LOCK = json.loads((ROOT / "prereg.json").read_text("utf-8"))
assert LOCK["schema"] == "yggdrasil.dg1-md33-conventional-controls-prereg.v1"
assert LOCK["status"] == "FROZEN_BEFORE_NEW_GENERATOR_BASELINES_OR_OUTCOMES"
COHORTS = LOCK["synthetic_cohorts"]
STARTS = {
    name: (cfg["first"], cfg["last"], tuple(cfg["motifs"]))
    for name, cfg in COHORTS.items()
    if isinstance(cfg, dict) and {"first", "last", "motifs"} <= set(cfg)
}
assert set(STARTS) == {"train", "validation", "transfer", "cold"}
assert STARTS["train"] == (11000, 11767, TRAIN)
assert STARTS["validation"] == (12000, 12191, TRAIN)
assert STARTS["transfer"] == (13000, 13191, TRANSFER)
assert STARTS["cold"] == (14000, 14095, TRANSFER)


def valid_allocation(seed):
    if type(seed) is not int:
        raise AssertionError("MD33_UNAUTHORIZED_OR_OFFICIAL_FIRST_USE_SEED")
    for name, (start, finish, motifs) in STARTS.items():
        if start <= seed <= finish:
            block, context = divmod(seed - start, 4)
            motif = motifs[block % 3]
            offset = (block // 3) % 4
            rewire = (block // 12) % 2 == 1
            spec = {
                "required_precursor": context,
                "encoder": BASES[motif][0],
                "decoder": BASES[motif][1],
                "offset": offset,
            }
            return name, block, motif, rewire, spec
    raise AssertionError("MD33_UNAUTHORIZED_OR_OFFICIAL_FIRST_USE_SEED")


def synthetic_world(seed):
    """Harness only; never pass returned spec/metadata into model decision."""
    _, _, _, rewire, spec = valid_allocation(seed)
    return RelayWorld(spec, rewire=rewire)


def public_teacher_blocks(cohort):
    """Collect only physically charged public sensor/action traces.

    Each block comprises 4 episodes with 8 actual charged diagnostics and
    8 actual charged actuations. No graph/offset/rewire labels are returned.
    """
    if cohort not in ("train", "validation"):
        raise AssertionError("MD33_NO_HOLDOUT_LEARNING")
    first, last, _ = STARTS[cohort]
    blocks = []
    receipts_sha = hashlib.sha256()
    physical_steps = 0
    for first_seed in range(first, last + 1, 4):
        block = []
        for context in range(4):
            world = synthetic_world(first_seed + context)
            receipt = run_public_two_probe(world)
            if receipt["paid_steps"] != 4 or receipt["net_utility"] != 0.8:
                raise AssertionError("MD33_TRAIN_NOT_PHYSICALLY_PAID")
            rows = receipt["trace"]
            if ([r["action"]["kind"] for r in rows] !=
                    ["diagnostic", "actuator", "diagnostic", "actuator"]):
                raise AssertionError("MD33_TRAIN_PHYSICAL_TRACE_SHAPE")
            event_a, event_b = rows[0], rows[2]
            def public_channel(row):
                obs = row["sensor_vector"]
                if (len(obs) != 4 or sum(obs) != 1 or
                        any(type(x) is not int or x not in (0, 1)
                            for x in obs)):
                    raise AssertionError("MD33_NONPUBLIC_OR_INVALID_SENSOR")
                return obs.index(1)
            block.append((
                ("encoder", event_a["action"]["channel"], public_channel(event_a)),
                ("decoder", event_b["action"]["channel"], public_channel(event_b)),
            ))
            receipts_sha.update((receipt["public_trace_sha256"] + "\n").encode("ascii"))
            physical_steps += len(rows)
        blocks.append(tuple(block))
    if len(blocks) * 16 != physical_steps:
        raise AssertionError("MD33_DATA_CUSTODY_MISMATCH")
    if cohort == "train" and (len(blocks), physical_steps) != (192, 3072):
        raise AssertionError("MD33_FROZEN_TRAIN_ACTION_BUDGET")
    if cohort == "validation" and (len(blocks), physical_steps) != (48, 768):
        raise AssertionError("MD33_FROZEN_VALIDATION_ACTION_BUDGET")
    return tuple(blocks), {
        "cohort": cohort,
        "blocks": len(blocks),
        "episodes": len(blocks) * 4,
        "charged_actions": physical_steps,
        "public_physical_sha256": receipts_sha.hexdigest(),
    }


def structural_split_audit():
    metas = {}
    for name in ("train", "validation", "transfer", "cold"):
        first, last, motifs = STARTS[name]
        combinations = {}
        for seed in range(first, last + 1, 4):
            group, _, motif, rewire, spec = valid_allocation(seed)
            assert group == name
            key = f"{motif}|{spec['offset']}|{int(rewire)}"
            combinations[key] = combinations.get(key, 0) + 1
        expected = {"train": 8, "validation": 2,
                    "transfer": 2, "cold": 1}[name]
        if len(combinations) != 24 or set(combinations.values()) != {expected}:
            raise AssertionError("MD33_BAD_SPLIT_FACTORIAL_BALANCE")
        metas[name] = {
            "first": first, "last": last,
            "episodes": last - first + 1,
            "blocks": (last - first + 1) // 4,
            "motifs": list(motifs),
            "combinations": len(combinations),
            "repetitions_per_combination": expected,
            "manifest_sha256": digest(combinations),
        }
    if set(TRAIN) & set(TRANSFER):
        raise AssertionError("MD33_TRANSFER_MOTIF_OVERLAP")
    return {"schema": "md33.synthetic-split-audit.v1",
            "status": "ALLOCATION_ONLY_NO_HOLDOUT_EVALUATION",
            "official_first_use": False,
            "splits": metas,
            "training_transfer_motif_disjoint": True}


if __name__ == "__main__":
    print(canonical(structural_split_audit()))
