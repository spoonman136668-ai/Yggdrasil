"""NUM05 disjoint synthetic numerical causal DEV; NO external source use.

This file defines fixed A/B/A public source, independent online controls and
prequential scoring. Registered DEV is gated by a separately committed one-use
admission marker after dual-platform engineering qualification.
"""
import argparse
from collections import deque
import hashlib
import json
import math
import os
from pathlib import Path
import random
import time

from num05 import (Bank, NumericRegimeMemory, SOURCE_TAG, canonical, digest,
                   public_row, target, error, region)

HERE = Path(__file__).resolve().parent
SCHEMA = "yggdrasil.num05.scored-dev.v1"
STAGES = {"novel_late": (240, 320), "familiar_return": (352, 416)}
FIXTURE_SEED = 520009
DEV_SEEDS = (520117, 520131)
NULL_SEED = 520211
MAX_EPISODES = 416


def source_rows(seed, *, null=False, count=MAX_EPISODES):
    if seed in DEV_SEEDS + (NULL_SEED,) and count != MAX_EPISODES:
        raise ValueError("NUM05_REGISTERED_SEED_PARTIAL_USE_FORBIDDEN")
    if seed not in DEV_SEEDS + (NULL_SEED, FIXTURE_SEED):
        raise ValueError("NUM05_UNREGISTERED_SOURCE_ID")
    rng = random.Random(seed)
    for index in range(count):
        action = index % 5
        q = (index // 5) % 4
        sx = 1 if q & 1 else -1
        sy = 1 if q & 2 else -1
        observation = (sx * (0.68 + 0.20 * rng.random()),
                       sy * (0.68 + 0.20 * rng.random()))
        base = (action - 2) * .13
        parity = 1 if action % 2 else -1
        da = (
            base + .34 * sx + .11 * sy * parity,
            -base + .34 * sy - .12 * sx * (-parity),
        )
        ra = .45 * da[0] - .30 * da[1] + .20 * sx * sy + .14 * (action % 3 - 1)
        if (not null) and (160 <= index < 320):
            db = (
                -.45 * sx - base + .25 * sy * (-parity) + .20 * parity,
                -.43 * sy + base - .27 * sx * (-parity) - .10 * (action % 3 - 1),
            )
            rb = -.50 * db[0] + .28 * db[1] - .30 * sx * sy + .20 * ((action + 1) % 3 - 1)
            dx, dy, reward = db[0], db[1], rb
        else:
            dx, dy, reward = da[0], da[1], ra
        dx += rng.gauss(0, .02)
        dy += rng.gauss(0, .02)
        reward += rng.gauss(0, .02)
        next_observation = (observation[0] + dx, observation[1] + dy)
        identifier = digest(f"num05:{seed}:{index}:source-public".encode("ascii"))
        yield public_row(identifier, observation, action,
                         next_observation, reward, False, False, source_tag=SOURCE_TAG)


class CellHistory:
    def __init__(self, *, window=None):
        self.window = window
        self.rows = []

    def predict(self, observation, action):
        chosen = self.rows if self.window is None else self.rows[-self.window:]
        cell = region(observation)
        values = [target(row) for row in chosen
                  if row["action"] == action and region(row["observation"]) == cell]
        n = len(values)
        return [sum(v[k] for v in values) / (n + 1) for k in range(3)]

    def observe(self, row):
        self.rows.append(row)


class KNNHistory:
    def __init__(self, *, window=None):
        self.window = window
        self.rows = []

    def predict(self, observation, action):
        chosen = self.rows if self.window is None else self.rows[-self.window:]
        x, y = observation
        matches = []
        for index, row in enumerate(chosen):
            if row["action"] != action:
                continue
            u, v = row["observation"]
            matches.append(((x-u)**2 + (y-v)**2, index, target(row)))
        matches.sort(key=lambda p: (p[0], p[1]))
        picked = [z for _, _, z in matches[:8]]
        if not picked:
            return [0.0]*3
        return [sum(v[k] for v in picked) / (len(picked) + 1) for k in range(3)]

    def observe(self, row):
        self.rows.append(row)


def _solve_ridge(matrix, rhs):
    # Tiny fixed 3x3 positive-definite least-squares normal system.
    rows = [matrix[i][:] + [rhs[i]] for i in range(3)]
    for col in range(3):
        pivot = max(range(col, 3), key=lambda k: abs(rows[k][col]))
        rows[col], rows[pivot] = rows[pivot], rows[col]
        if abs(rows[col][col]) < 1e-12:
            raise ValueError("NUM05_RIDGE_SINGULAR")
        d = rows[col][col]
        for k in range(col, 4):
            rows[col][k] /= d
        for i in range(3):
            if i == col:
                continue
            f = rows[i][col]
            for k in range(col, 4):
                rows[i][k] -= f * rows[col][k]
    return [rows[i][3] for i in range(3)]


class RidgeHistory:
    """Independent fully refitted per-action (1,x,y) conventional regression."""
    def __init__(self):
        self.rows = []

    def predict(self, observation, action):
        selected = [row for row in self.rows if row["action"] == action]
        if not selected:
            return [0.0]*3
        gram = [[0.1 if i == j else 0.0 for j in range(3)] for i in range(3)]
        rhs = [[0.0]*3 for _ in range(3)]
        for row in selected:
            features = [1.0, *row["observation"]]
            z = target(row)
            for i in range(3):
                for j in range(3):
                    gram[i][j] += features[i] * features[j]
                for k in range(3):
                    rhs[k][i] += features[i] * z[k]
        weights = [_solve_ridge(gram, values) for values in rhs]
        features = [1.0, *observation]
        return [sum(w[i] * features[i] for i in range(3)) for w in weights]

    def observe(self, row):
        self.rows.append(row)


class ZeroPredictor:
    def predict(self, observation, action):
        return [0.0]*3

    def observe(self, row):
        pass


def models():
    return {
        "num05_dual": NumericRegimeMemory(),
        "ablation_single_bank": NumericRegimeMemory(single_bank=True),
        "cell_full": CellHistory(),
        "cell_recent80": CellHistory(window=80),
        "cell_recent40": CellHistory(window=40),
        "knn_full": KNNHistory(),
        "knn_recent80": KNNHistory(window=80),
        "ridge_full": RidgeHistory(),
        "zero_sham": ZeroPredictor(),
    }


def one_study(seed, *, null=False):
    arms = models()
    sums = {stage: {name: 0.0 for name in arms} for stage in STAGES}
    source_digest = hashlib.sha256()
    n_scored = {key: 0 for key in STAGES}
    bank_before = None
    bank_after = None
    old_return_predictions = 0
    t0 = time.perf_counter()
    cpu0 = time.process_time()
    for index, row in enumerate(source_rows(seed, null=null)):
        if index == 160:
            bank_before = arms["num05_dual"].info()["old_bank_sha256"]
        if index == 320:
            bank_after = arms["num05_dual"].info()["old_bank_sha256"]
        if 368 <= index < 416 and arms["num05_dual"].active == 0:
            old_return_predictions += 1
        source_digest.update(canonical(row))
        z = target(row)
        pre = {name: model.predict(row["observation"], row["action"])
               if hasattr(model, "predict") else model.forecast(row["observation"], row["action"])
               for name, model in arms.items()}
        for stage, (start, stop) in STAGES.items():
            if start <= index < stop:
                for name, pred in pre.items():
                    sums[stage][name] += error(pred, z)
                n_scored[stage] += 1
        for name, model in arms.items():
            model.observe(row)
    for name, model in arms.items():
        if isinstance(model, NumericRegimeMemory):
            raw = model.checkpoint()
            restored = NumericRegimeMemory.restore(raw, digest(raw))
            if restored.checkpoint() != raw:
                raise ValueError("NUM05_COLD_RESTORE_DRIFT")
    result = {
        "seed": seed, "is_null": null, "source_sha256": source_digest.hexdigest(),
        "source_rows": MAX_EPISODES, "source_actions": MAX_EPISODES,
        "scores": {stage: {name: sums[stage][name] / n_scored[stage]
                           for name in arms}
                   for stage in STAGES},
        "pooled": {name: (sums["novel_late"][name] +
                         sums["familiar_return"][name]) / 144
                   for name in arms},
        "old_bank_sha_at_160": bank_before,
        "old_bank_sha_at_320": bank_after,
        "old_bank_retained": bank_before == bank_after,
        "return_last48_old_bank_fraction": old_return_predictions / 48,
        "learner_info": arms["num05_dual"].info(),
        "ablation_info": arms["ablation_single_bank"].info(),
        "candidate_checkpoint_sha256": digest(arms["num05_dual"].checkpoint()),
        "cpu_seconds": round(time.process_time()-cpu0, 5),
        "wall_seconds": round(time.perf_counter()-t0, 5),
    }
    return result


CONVENTIONAL = ("cell_full", "cell_recent80", "cell_recent40",
                "knn_full", "knn_recent80", "ridge_full", "zero_sham",
                "ablation_single_bank")


def classify(dev, null):
    checks = []
    for r in dev:
        best_pool = min(r["pooled"][k] for k in CONVENTIONAL)
        checks.append({
            "seed": r["seed"],
            "candidate_pooled": r["pooled"]["num05_dual"],
            "strongest_control_pooled": best_pool,
            "gain": best_pool-r["pooled"]["num05_dual"],
            "pooled_margin": best_pool-r["pooled"]["num05_dual"] >= .005,
            "novel_guard": (r["scores"]["novel_late"]["num05_dual"] <=
                            min(r["scores"]["novel_late"][k] for k in CONVENTIONAL) + .01),
            "return_guard": (r["scores"]["familiar_return"]["num05_dual"] <=
                             min(r["scores"]["familiar_return"][k] for k in CONVENTIONAL) + .01),
            "retained": r["old_bank_retained"],
            "two_banks": r["learner_info"]["bank_count"] == 2,
            "returned_to_old_bank": r["return_last48_old_bank_fraction"] >= .80,
        })
    no_null_false_alarm = null["learner_info"]["bank_count"] == 1
    go = (all(all(v for k,v in ch.items()
                  if k in ("pooled_margin","novel_guard","return_guard","retained",
                           "two_banks","returned_to_old_bank")) for ch in checks)
          and no_null_false_alarm)
    return {
        "classification": "DEV_FEASIBLE_NOT_SCIENTIFIC" if go else "DEV_NO_GO",
        "no_null_false_alarm": no_null_false_alarm, "per_seed": checks,
        "scientific_gain_verified": False, "native_integration": False,
        "original_external_first_use": False,
    }


def source_free_fixture():
    # Non-reserved fixture exercises five-action, nonlinear numeric learning
    # but cannot access registered DEV source outcomes.
    model = NumericRegimeMemory()
    rows = list(source_rows(FIXTURE_SEED, null=True, count=80))
    for row in rows:
        model.observe(row)
    raw=model.checkpoint()
    assert NumericRegimeMemory.restore(raw,digest(raw)).checkpoint()==raw
    assert model.info()["bank_count"]==1
    assert len(model.rows)==80
    return {"fixture_rows":80,"fixture_sha256":digest(b"".join(map(canonical,rows))),
            "archive_sha256":digest(raw),"pass":True}


def _verify_primary_admission():
    if os.environ.get("NUM05_SINGLE_USE_DEV") != "1":
        raise ValueError("NUM05_PRIMARY_REQUIRES_OWNER_AUTHORIZED_WORKFLOW")
    admit = HERE / "primary.admit"
    if not admit.is_file():
        raise ValueError("NUM05_PRIMARY_NOT_ADMITTED")
    data = json.loads(admit.read_text(encoding="utf8"))
    if (set(data) != {"schema","qualified_parent_sha","science_source_sha",
                       "dev_seeds","admitted_for_synthetic_dev"}
            or data["schema"] != "yggdrasil.num05.one-shot-sourcefree-dev.v1"
            or data["dev_seeds"] != list(DEV_SEEDS)
            or data["admitted_for_synthetic_dev"] is not True
            or type(data["qualified_parent_sha"]) is not str
            or type(data["science_source_sha"]) is not str):
        raise ValueError("NUM05_PRIMARY_MARKER_INVALID")


def main():
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fixture",action="store_true")
    group.add_argument("--primary",action="store_true")
    args=parser.parse_args()
    if args.fixture:
        print("NUM05_ENGINEERING_FIXTURE="+json.dumps(source_free_fixture(),sort_keys=True))
        return
    _verify_primary_admission()
    evidence = [one_study(seed) for seed in DEV_SEEDS]
    negative = one_study(NULL_SEED, null=True)
    outcome = classify(evidence,negative)
    receipt={"schema":SCHEMA,"dev":evidence,"null":negative,"decision":outcome,
             "original_external_source_actions":0,"source_owner_authenticated":False,
             "native_model_unchanged":True}
    blob=canonical(receipt)
    print("NUM05_REGISTERED_DEV_RECEIPT_SHA256="+digest(blob))
    print("NUM05_REGISTERED_DEV_RECEIPT_JSON="+blob.decode("ascii"))


if __name__=="__main__":
    main()
