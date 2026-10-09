"""Y-SYN02: independently seeded synthetic-only replication of Y-SYN01.

Primary outcomes are *not* run by default. Official CKB scientific authority
must bind a separate frozen preregistration, qualified code SHA and run receipt.
This module cannot authorize source admission, classification or promotion.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

REGIMES = (
    ("coherent-reliable", (4, 5), (11, 20), (9, 10), (4, 5)),
    ("coherent-adversarial", (1, 5), (7, 10), (9, 10), (4, 5)),
    ("incoherent", (1, 2), (13, 20), (1, 5), (1, 2)),
)
SEEDS = (401, 409, 419, 421)
ARMS = ("A0", "A1", "A2")
CAPACITY = (16, 7, 9)
TOTAL_CASES = 3072
TOTAL_PROJECTIONS = 9216


class Generator:
    def __init__(self, seed: int, regime_index: int):
        self.x = (seed ^ 0x9E3779B9 ^ ((regime_index + 1) * 0x85EBCA6B)) & 0xFFFFFFFF
        if self.x == 0:
            self.x = 1

    def uniform(self) -> float:
        x = self.x
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        self.x = x & 0xFFFFFFFF
        return self.x / 4294967296.0


def _prob(value: float, ratio: tuple[int, int]) -> bool:
    return value < ratio[0] / ratio[1]


def make_case(gen: Generator, regime: tuple, index: int) -> tuple[int, dict, dict]:
    _, retained_p, target_p, coherent_p, majority_p = regime
    truth = int(gen.uniform() < 0.5)
    retained_best = truth if _prob(gen.uniform(), retained_p) else 1 - truth
    target_best = truth if _prob(gen.uniform(), target_p) else 1 - truth
    retained_map = retained_best if _prob(gen.uniform(), coherent_p) else 1 - retained_best
    retained_count = 7 if _prob(gen.uniform(), majority_p) else 3
    baseline = dict(total=9, consistency=0.0, utility=0.0, key=(index + 1,))
    target = dict(baseline, best=target_best, map_best=target_best, best_count=5)
    retained = dict(baseline, best=retained_best, map_best=retained_map, best_count=retained_count)
    return truth, target, retained


def _load_qualified_mechanism():
    research = Path(__file__).resolve().parents[3]
    path = research / "applications/plane/exp-dgr-external-cumulative-dependent-pipeline-retained-majority-decision-gate-095.py"
    if not path.is_file():
        raise ValueError("SYN_Y01_FROZEN_Y095_MECHANISM_ABSENT")
    spec = importlib.util.spec_from_file_location("frozen_y095_mechanism", path)
    if spec is None or spec.loader is None:
        raise ValueError("SYN_Y01_MECHANISM_LOADER")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if (module.CAPACITY, module.ARMS, module.LEARNED_SCALARS, module.EXTERNAL_MODEL_CALLS) != ((16, 7, 9), ARMS, 0, 0):
        raise ValueError("SYN_Y01_FROZEN_MECHANISM_DRIFT")
    return module.project_consumer


def evaluate():
    project = _load_qualified_mechanism()
    results = []
    pooled = {regime[0]: {arm: [0, 0] for arm in ARMS} for regime in REGIMES}
    n = 0
    for index, regime in enumerate(REGIMES):
        for seed in SEEDS:
            gen = Generator(seed, index)
            counts = {arm: 0 for arm in ARMS}
            chosen = 0
            for case_index in range(256):
                truth, target, retained = make_case(gen, regime, case_index)
                for arm in ARMS:
                    projected = project(target, retained, arm)
                    if projected["key"] != retained["key"] or projected["total"] != 9 or projected["best_count"] != retained["best_count"]:
                        raise ValueError("SYN_Y01_CAPACITY_OR_STATE_DRIFT")
                    if arm == "A2" and projected["best"] == retained["best"] and (retained["best"] == retained["map_best"]) and retained["best_count"] == 7:
                        chosen += 1
                    counts[arm] += int(projected["best"] == truth)
                    pooled[regime[0]][arm][0] += int(projected["best"] == truth)
                    pooled[regime[0]][arm][1] += 1
                    n += 1
            results.append({
                "regime": regime[0], "seed": seed,
                "cases": 256, "correct": counts,
                "accuracy": {arm: counts[arm] / 256 for arm in ARMS},
                "coherent_retained_majority_choices": chosen,
            })
    if n != TOTAL_PROJECTIONS:
        raise ValueError("SYN_Y01_EVAL_BUDGET_DRIFT")
    def gap(regime):
        p = pooled[regime]
        return p["A2"][0] / p["A2"][1] - p["A0"][0] / p["A0"][1]
    reliable_gap = gap("coherent-reliable")
    adversarial_gap = gap("coherent-adversarial")
    passes = (reliable_gap >= 0.10, adversarial_gap <= -0.20)
    classification = "SUPPORTED" if all(passes) else ("MIXED" if any(passes) else "NEGATIVE")
    return {
        "schema": "ckb.synthetic-pilot-result.v1",
        "experiment": "Y-SYN02-INDEPENDENT-SEED-COHERENT-CORRUPTION-REPLICATION",
        "data_class": "SYNTHETIC_ONLY",
        "source_origin_external_claim": False,
        "official_ckb_acceptance": False,
        "classification": classification,
        "reliable_a2_minus_a0": reliable_gap,
        "adversarial_a2_minus_a0": adversarial_gap,
        "capacity": CAPACITY, "learned_scalars": 0, "model_calls": 0,
        "cases": TOTAL_CASES, "projections": TOTAL_PROJECTIONS, "seed_rows": results,
    }


if __name__ == "__main__":
    if os.environ.get("CKB_SYN_Y02_QUALIFIED_RUN") != "yes":
        raise SystemExit("PRIMARY_NOT_ADMITTED_BY_CKB: no evaluation attempted")
    print(json.dumps(evaluate(), sort_keys=True, indent=2))
