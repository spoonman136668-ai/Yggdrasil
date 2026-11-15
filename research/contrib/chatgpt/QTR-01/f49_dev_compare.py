#!/usr/bin/env python3
"""F49 frozen DEV runner, separated from pre-DEV engineering and source fitting.

Protected seeds cannot be requested. The sole true-law evaluator is private to
this module; learning arms get only public two-step trajectories and noisy bits.
Run with --development-first-use ONLY after source-exact full regression and the
frozen protocol's positive controls are independently qualified.
"""
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
from time import perf_counter, process_time

import f49_worlds as world
import f49_discrete_learners as discrete
import f49_conventional_controls as conventional
import f49_predev_custody as custody
import f49_source_pretrain as source_fit

CHECKPOINTS = (8, 16, 32)
CONTROL_KINDS = ("conventional_mlp", "conventional_logistic",
                 "exact_bank_bayes", "compositional_bayes", "random", "uniform")
ABLATION_KINDS = custody.ABLATIONS
ALL_KINDS = ("native", *CONTROL_KINDS, *("ablation_"+k for k in ABLATION_KINDS))
BASELINE_RUN = 43743198013
BASELINE_SHA = "e9714f125e73050cdac3114559f58b4b2f8e738b"
MINIMUM_SIZE = min(world.BANK_SIZES)
MAX_WORLDS = len(world.BANK_SIZES) * len(world.SEEDS)
SCHEMA = "yggdrasil.qtr01.f49.frozen-development-results.v1"


class ComparisonRejected(world.F49Rejected):
    pass


def truth_from_rule(rule, trajectory):
    """No outcome-noise and no model oracle: evaluator-only clean truth."""
    t = discrete._check_trajectory(trajectory)
    return (world.evaluate(rule, t[0], 0, t[2]),
            world.evaluate(rule, t[1], t[0], t[2]))


class OutcomeService:
    """A scoped evaluator whose laws never enter an arm state or output record."""

    def __init__(self, size, seed, *, fixture_rule=None):
        if type(size) is not int or size not in world.BANK_SIZES:
            raise ComparisonRejected("F49_UNREGISTERED_BANK")
        if type(seed) is not int or seed not in world.SEEDS:
            raise ComparisonRejected("F49_PROTECTED_SEED_REFUSED")
        world.freeze()
        self.size, self.seed = size, seed
        self.pool, self.evaluation = world._trajectories_for_world(size, seed)
        self._rule = fixture_rule if fixture_rule is not None else world.target_ast(size, seed)
        if world.ast_depth(self._rule) > 4:
            raise ComparisonRejected("F49_EVALUATOR_BAD_RULE")
        self._calls = {}
        self._evaluations = 0

    def answer(self, arm_key, query_index, trajectory):
        if (type(arm_key) is not str or arm_key not in ALL_KINDS
            or type(query_index) is not int or not 0 <= query_index < len(self.pool)
            or discrete._check_trajectory(trajectory) != self.pool[query_index]):
            raise ComparisonRejected("F49_ACTION_NOT_FROM_PUBLIC_POOL")
        seen = self._calls.setdefault(arm_key, set())
        if query_index in seen or len(seen) >= 32:
            raise ComparisonRejected("F49_REPLAY_OR_BUDGET_EXCEEDED")
        seen.add(query_index)
        true_bits = truth_from_rule(self._rule, trajectory)
        return tuple(
            y ^ int(world.random_uint("F49/obs/v1", self.size, self.seed,
                                      query_index, step, 0) < world.NOISE_BOUND)
            for step, y in enumerate(true_bits))

    def evaluate_probabilities(self, predict):
        """Only test on evaluator-held-out trajectories; never return truth."""
        accurate, sq_error, total = 0, 0.0, 0
        for tr in self.evaluation:
            probabilities = predict(tr)
            if type(probabilities) is not tuple or len(probabilities) != 2:
                raise ComparisonRejected("F49_MODEL_OUTPUT_NOT_TWO_BITS")
            true = truth_from_rule(self._rule, tr)
            for p, expected in zip(probabilities, true):
                if (not isinstance(p, (int, float))
                    or not math.isfinite(p) or p < 0 or p > 1):
                    raise ComparisonRejected("F49_INVALID_PROBABILITY")
                accurate += int((p >= 0.5) == expected)
                sq_error += (float(p)-expected)**2
                total += 1
        self._evaluations += total
        return {"accuracy": round(accurate/total, 12),
                "brier": round(sq_error/total, 12),
                "test_bits": total}


def load_baselines(folder, size):
    """Check every reused model against the original completed source-only run."""
    folder = Path(folder)
    receipt = json.loads((folder/"f49-source-pretrain-receipt.json").read_text())
    if (receipt.get("schema") != source_fit.SCHEMA
        or receipt.get("source_commit") != BASELINE_SHA
        or receipt.get("prereg_blob") != world.FROZEN_BLOB
        or receipt.get("full_source_fits") != 6
        or receipt.get("dev_target_observations") != 0
        or receipt.get("scientific_pass") is not False
        or receipt.get("protected_first_use") is not False):
        raise ComparisonRejected("F49_SOURCE_BASELINE_RECEIPT_REJECTED")
    if [(x["size"], x["kind"]) for x in receipt["results"]] != [
        (b,k) for b in world.BANK_SIZES for k in source_fit.KINDS]:
        raise ComparisonRejected("F49_SOURCE_BASELINE_COVERAGE_INCOMPLETE")
    pair = {}
    for record in receipt["results"]:
        if record["size"] != size:
            continue
        if record["source_rows"] != size*128 or not record["cold_restore"]:
            raise ComparisonRejected("F49_SOURCE_PRETRAIN_NOT_FULL")
        name = record["checkpoint"]
        if name != f"f49-source-{size}-{record['kind']}.npz":
            raise ComparisonRejected("F49_SOURCE_BASELINE_FILE_UNEXPECTED")
        pair[record["kind"]] = source_fit.load_checkpoint(
            folder / name, record["checkpoint_sha256"], BASELINE_SHA)
        if pair[record["kind"]].source_observations != size*128:
            raise ComparisonRejected("F49_SOURCE_PRETRAIN_OBSERVATIONS_MISMATCH")
    if set(pair) != set(source_fit.KINDS):
        raise ComparisonRejected("F49_SOURCE_MODELS_MISSING")
    return pair


def assemble(size, seed, fitted):
    arms = {}
    for kind in discrete.KINDS:
        arms[kind] = discrete.PublicArm(kind, size, seed)
    for kind in source_fit.KINDS:
        arms[kind] = conventional.ConventionalArm(fitted[kind], seed)
    for mode in ABLATION_KINDS:
        arms["ablation_"+mode] = custody.NativeAblation(mode, size, seed)
    if set(arms) != set(ALL_KINDS):
        raise ComparisonRejected("F49_ARM_INVENTORY_INVALID")
    return arms


def stats_for_arm(kind, arm):
    if kind.startswith("ablation_"):
        engine = arm.arm.engine
        return {"bits": arm.observed_bits,
                "proposals": arm.charged_proposals,
                "prediction_accesses": engine.prediction_accesses +
                                       arm.arm.selector_accesses}
    if isinstance(arm, conventional.ConventionalArm):
        return {"bits": arm.observed_bits,
                "source_rows": arm.source_observations,
                "prediction_accesses": arm.model.prediction_accesses,
                "source_train_seconds": arm.pretraining_seconds}
    eng = arm.engine
    return {"bits": arm.observed_bits,
            "proposals": eng.proposals if hasattr(eng, "proposals") else 0,
            "prediction_accesses": eng.prediction_accesses + arm.selector_accesses}


def model_prediction(kind, arm):
    if kind.startswith("ablation_"):
        return arm.arm.engine.probability
    if isinstance(arm, conventional.ConventionalArm):
        return arm.probability
    return arm.engine.probability


def select_and_observe(kind, arm, oracle):
    index, tr = arm.select()
    result = oracle.answer(kind, index, tr)
    arm.observe(index, result)


def check_cold(kind, arm, fitted):
    """Cold check outside timed adaptation; report cost separately."""
    start = process_time()
    if kind.startswith("ablation_"):
        return {"cold_bit_exact": None, "reason": "not preregistered for ablation",
                "cpu_seconds": 0.0, "bytes": 0}
    if isinstance(arm, conventional.ConventionalArm):
        stored = custody.cold_conventional(arm, fitted[kind])
        restore = custody.restore_conventional(stored, fitted[kind])
        equivalent = stored == custody.cold_conventional(restore, fitted[kind])
    else:
        stored = custody.cold_public(arm)
        restore = custody.restore_public(stored)
        equivalent = stored == custody.cold_public(restore)
    corrupted = stored[:-1] + bytes([stored[-1] ^ 1])
    rejected = False
    try:
        if isinstance(arm, conventional.ConventionalArm):
            custody.restore_conventional(corrupted, fitted[kind])
        else:
            custody.restore_public(corrupted)
    except discrete.ControlRejected:
        rejected = True
    return {"cold_bit_exact": equivalent, "corruption_rejected": rejected,
            "cpu_seconds": round(process_time()-start, 8),
            "bytes": len(stored)}


def run_world(size, seed, baselines, *, fixture_rule=None, events=32):
    """Single fixed world; reuses all trained controls, never mutates source."""
    if events not in CHECKPOINTS:
        raise ComparisonRejected("F49_BUDGET_NOT_FROZEN")
    oracle = OutcomeService(size, seed, fixture_rule=fixture_rule)
    fitted = load_baselines(baselines, size)
    arms = assemble(size, seed, fitted)
    receipts = {k: {"checkpoints": {}} for k in arms}
    for kind, arm in arms.items():
        timer = process_time()
        for step in range(1, events+1):
            select_and_observe(kind, arm, oracle)
            if step in CHECKPOINTS:
                scores = oracle.evaluate_probabilities(model_prediction(kind, arm))
                scores.update(stats_for_arm(kind, arm))
                # Include source fitting (not a free trained model).
                scores["process_seconds_cumulative"] = round(process_time()-timer +
                    (arm.pretraining_seconds if isinstance(arm, conventional.ConventionalArm) else 0.0), 7)
                if step == 16:
                    scores["cold"] = check_cold(kind, arm, fitted)
                receipts[kind]["checkpoints"][str(step)] = scores
    assert all(len(oracle._calls[k]) == events for k in ALL_KINDS)
    return {"size": size, "seed": seed, "public_pool": len(oracle.pool),
            "eval_pool": len(oracle.evaluation), "arms": receipts,
            "information_fairness_warning": (
                "Conventional MLP and logistic encode trajectories but not explicit source AST; "
                "native/exact-bank/compositional controls can read source programs. "
                "No unqualified scientific equivalence claim permitted."),
            "scientific_pass": False}


def classify(world_results):
    """Frozen nine-world DEV classification. Scientific pass remains FALSE."""
    prereg = world.freeze()["prereg_metrics"]
    if (len(world_results) != MAX_WORLDS or [(w["size"],w["seed"]) for w in world_results]
        != [(size,seed) for size in world.BANK_SIZES for seed in world.SEEDS]):
        return {"classification": "DEV_INCOMPLETE_NOT_SCIENTIFIC_PASS",
                "scientific_pass": False}
    def acc(w, kind, budget):
        return w["arms"][kind]["checkpoints"][str(budget)]["accuracy"]
    native = [acc(w,"native",16) for w in world_results]
    control_mean = {k: sum(acc(w,k,16) for w in world_results)/9
                    for k in CONTROL_KINDS}
    best_name = max(CONTROL_KINDS, key=lambda k: control_mean[k])
    gain = sum(native)/9 - control_mean[best_name]
    per_family = {str(seed): sum(acc(w,"native",16) - max(acc(w,k,16) for k in CONTROL_KINDS)
                                 for w in world_results if w["seed"]==seed)/3
                  for seed in world.SEEDS}
    full32 = sum(acc(w,"native",32) - max(acc(w,k,32) for k in CONTROL_KINDS)
                 for w in world_results)/9
    admission = ("TASK_HEADROOM_INVALID"
        if (all(acc(w,k,16) >= .95 for w in world_results for k in ("native",*CONTROL_KINDS))
            or max(control_mean[k] for k in ("conventional_mlp","conventional_logistic")) < .55)
        else "TASK_ADMITTED")
    cold_ok = all(
        w["arms"][k]["checkpoints"]["16"]["cold"]["cold_bit_exact"] is True and
        w["arms"][k]["checkpoints"]["16"]["cold"]["corruption_rejected"] is True
        for w in world_results for k in ("native", *CONTROL_KINDS))
    requirements = prereg["requirements"]
    development_criteria = (
        admission=="TASK_ADMITTED"
        and gain >= requirements["b16_gain_over_best_single_control_min"]
        and all(x >= requirements["b16_gain_each_unseen_family_min"] for x in per_family.values())
        and full32 >= requirements["b32_native_vs_strongest_control_regression_floor"]
        and cold_ok)
    # Other preregistered requirements, especially CPU parity, interference,
    # and ablation outcomes must be audited separately before DEV_GO.
    return {"classification": ("TASK_HEADROOM_INVALID" if admission!="TASK_ADMITTED"
           else "DEV_F49_NUMERIC_GATE_PASS_NEEDS_COST_AND_ABLATION_AUDIT"
                if development_criteria else "DEV_F49_NO_GO"),
            "strongest_control": best_name,
            "native_b16_mean": round(sum(native)/9,8),
            "control_b16_means": {k:round(v,8) for k,v in control_mean.items()},
            "gain_against_strongest_control": round(gain,8),
            "per_family_gain_vs_worldwise_best":per_family,
            "native_b32_vs_worldwise_best":round(full32,8),
            "cold_valid":cold_ok,
            "scientific_pass": False}


def run_all(folder, path):
    world.freeze()
    results=[]
    # High-first only; any error halts, no resampling or changing seeds.
    for size in world.BANK_SIZES:
        for seed in world.SEEDS:
            results.append(run_world(size, seed, folder))
            print(f"F49_DEV_WORLD_RECORDED_SIZE={size}_SEED={seed}", flush=True)
    summary=classify(results)
    record = {"schema":SCHEMA,"candidate_source_sha":None,
              "source_baseline_sha":BASELINE_SHA,
              "source_baseline_run":BASELINE_RUN,
              "frozen_prereg_blob":world.FROZEN_BLOB,
              "worlds":results,"decision":summary,"scientific_pass":False,
              "main_or_accepted_weights_mutated":False,
              "protected_first_use":False}
    path = Path(path)
    if path.exists():
        raise ComparisonRejected("F49_REFUSE_OVERWRITE_FROZEN_RESULTS")
    path.write_text(json.dumps(record,sort_keys=True,indent=2)+"\n")
    return summary


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--development-first-use",action="store_true")
    parser.add_argument("--baselines",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if not args.development_first_use:
        parser.error("F49_DEV_FIRST_USE_REQUIRES_EXPLICIT_FROZEN_MODE")
    result=run_all(args.baselines,args.out)
    print("F49_DEV_CLASSIFICATION="+result["classification"])


if __name__=="__main__":
    main()
