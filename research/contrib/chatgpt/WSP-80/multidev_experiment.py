"""WSP80 exploratory eight-world UNREGISTERED developer heterogeneity screen.

This intentionally does NOT execute the 16 registered frozen SELFTEST seeds.
The eight development configurations and diagnostics were separately frozen
before this source file (dev_multi_prereg.json at commit 63a5dfe4...).

World construction and private evaluator scoring live only in this harness.
The writer, policies, controls and neural baseline see only physically paid
public before/action/after rows. Private labels are produced ONLY after the
prediction bundle is committed to its SHA256 prelabel envelope.

No run-time tuning, no acceptance/promotion, no scheduler, no disk artifacts.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import product
import json
import os
from pathlib import Path
from random import Random
import subprocess
import sys
from time import process_time_ns, perf_counter_ns

import acquisition
import source
from controls import (
    ConventionalAdam384, PaidMemorization, SparsePublicControl, paid_rows
)
from developer_cost_process import peak_rss_bytes
from frozen_scoring import PUBLIC, freeze_public_outputs, score_frozen
from independent_symbolic import IndependentConditionalSymbolic
from numerical_controls import FixedSparseNumeric
from structural_weights import PaidStructuralWeightEditor

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
FROZEN_DEV_PREREG_COMMIT = "63a5dfe439b1fd23a9936729dea5bcdf1ff87805"
FROZEN_DEV_PREREG_BLOB = "a99784a63315d25c34c0fdc6606852b72b2cef61"
FROZEN_REGISTERED_PREREG_BLOB = "0e96f4e0eff1ced7f87b754a2ad4fbb75c7b3d58"
FROZEN_REGISTERED_SOURCE_BLOB = "c5d0ab0dcf38b2f2dec1e60d7d8346eb2c2697d2"
FROZEN_ADAM_BLOB = "90bca703948c71e482892d2be830682201342368"
DEVELOPMENT = (
    (9101, "degree2_control"), (9102, "degree2_control"),
    (9103, "degree3_control"), (9104, "degree3_control"),
    (9105, "quartic_positive"), (9106, "quartic_positive"),
    (9107, "quartic_complemented"), (9108, "quartic_complemented"),
)
PROTECTED = frozenset(source.SEEDS)
if frozenset(seed for seed, _ in DEVELOPMENT) & PROTECTED:
    raise PermissionError("developer/protected cohort overlap")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return sha256(canonical(value).encode("ascii")).hexdigest()


def git(*args):
    return subprocess.run(("git",) + args, cwd=REPO, text=True,
                          capture_output=True, check=True).stdout.strip()


def validate_source_custody():
    current = git("rev-parse", "HEAD")
    if (len(current) != 40
            or (os.getenv("GITHUB_SHA") and os.environ["GITHUB_SHA"] != current)
            or git("status", "--porcelain")):
        raise RuntimeError("source SHA/clean checkout mismatch")
    files = {
        "research/contrib/chatgpt/WSP-80/dev_multi_prereg.json":
            FROZEN_DEV_PREREG_BLOB,
        "research/contrib/chatgpt/WSP-80/prereg.json":
            FROZEN_REGISTERED_PREREG_BLOB,
        "research/contrib/chatgpt/WSP-80/source.py":
            FROZEN_REGISTERED_SOURCE_BLOB,
        "research/contrib/chatgpt/WSP-77/fully_trained_mlp6.py":
            FROZEN_ADAM_BLOB,
    }
    for path, expected in files.items():
        if git("rev-parse", "HEAD:" + path) != expected:
            raise RuntimeError("source or developer protocol changed: " + path)
    if git("rev-parse", FROZEN_DEV_PREREG_COMMIT + "^") != (
            "29d800c8cea6e4de66a56bd824a645a75fb5a1f0"):
        raise RuntimeError("developer prereg did not precede implementation")
    if git("rev-parse", FROZEN_DEV_PREREG_COMMIT + ":" +
           "research/contrib/chatgpt/WSP-80/dev_multi_prereg.json") != (
            FROZEN_DEV_PREREG_BLOB):
        raise RuntimeError("prereg first commit proof invalid")
    raw = (HERE / "dev_multi_prereg.json").read_text("utf-8")
    dev = json.loads(raw)
    if (dev["schema"] != "wsp80.unregistered-multiworld-dev-prereg.v1"
            or dev["source"]["cohort"] !=
                [{"seed": s, "family": f} for s, f in DEVELOPMENT]
            or dev["source"]["paid_action_budget_all_worlds"] != 6144
            or dev["source"]["primary_and_protected_first_use"] is not False
            or dev["status"] !=
                "FROZEN_BEFORE_UNREGISTERED_MULTIWORLD_EXPERIMENT_IMPLEMENTATION_AND_OUTCOMES"
            or dev["authority"]["registered_first_use"] is not False):
        raise RuntimeError("developer prereg contract invalid")
    return {"head_sha": current, "blobs": files,
            "developer_protocol_first_commit": FROZEN_DEV_PREREG_COMMIT}


def roles_channels(seed, family):
    if (seed, family) not in DEVELOPMENT:
        raise PermissionError("only eight preregistered unprotected developer worlds")
    raw = sha256(f"WSP80|MULTIDEV|{seed}|roles-channels-v1".encode("ascii")).digest()
    rng = Random(int.from_bytes(raw, "big"))
    roles = list(range(6))
    channels = list(range(6))
    rng.shuffle(roles)
    rng.shuffle(channels)
    if len(set(roles)) != 6 or len(set(channels)) != 6:
        raise AssertionError("private role/channel bijection not established")
    return tuple(roles), tuple(channels)


def paid_sessions(world, seed):
    sessions = {"active": world.training_session(), "random": world.training_session()}
    policies = {"active": acquisition.InterventionPolicy(),
                "random": acquisition.UniformRandomPolicy(seed)}
    writers = {"active": PaidStructuralWeightEditor(),
               "random": PaidStructuralWeightEditor()}
    stage_a_snapshot = None
    for index in range(384):
        if index < 144:
            action = acquisition.stage_a_action(seed, index)
            actions = {"active": action, "random": action}
        else:
            actions = {
                "active": policies["active"].choose(sessions["active"].current),
                "random": policies["random"].choose(sessions["random"].current),
            }
        rows = {name: session.step(actions[name])
                for name, session in sessions.items()}
        if index < 144 and rows["active"] != rows["random"]:
            raise AssertionError("independently paid StageA mismatch")
        for name, observation in rows.items():
            policies[name].observe(observation)
            writers[name].charge(observation.before, observation.action,
                                 observation.after, observation.action_cost)
        if index == 143:
            writers["active"].compile()
            stage_a_snapshot = writers["active"].snapshot()
    if (stage_a_snapshot is None or
            any(len(s.ledger) != 384 for s in sessions.values())):
        raise AssertionError("incomplete charged sessions")
    candidate = tuple(sessions["active"].ledger)
    random = tuple(sessions["random"].ledger)
    paid_rows(candidate)
    paid_rows(random)
    return candidate, random, writers, stage_a_snapshot


def freeze_one(seed, family, candidate_rows, random_rows, writers, stage_a):
    # Every model/policy below sees ONLY physically paid public rows.
    compile_start = process_time_ns()
    cdiag = writers["active"].compile()
    rdiag = writers["random"].compile()
    candidate = PaidStructuralWeightEditor.restore(writers["active"].snapshot())
    random = PaidStructuralWeightEditor.restore(writers["random"].snapshot())
    stage_a_model = PaidStructuralWeightEditor.restore(stage_a)
    fixed = FixedSparseNumeric("fixed_degree3")
    fixed_info = fixed.fit(candidate_rows)
    fixed = FixedSparseNumeric.restore(fixed.snapshot())
    always = FixedSparseNumeric("always_degree4")
    always_info = always.fit(candidate_rows)
    always = FixedSparseNumeric.restore(always.snapshot())
    stage_a_fixed = FixedSparseNumeric("fixed_degree3")
    stage_a_fixed.fit(candidate_rows[:144])
    stage_a_fixed = FixedSparseNumeric.restore(stage_a_fixed.snapshot())
    symbolic = IndependentConditionalSymbolic.from_paid_ledger(candidate_rows)
    memory = PaidMemorization(candidate_rows)
    sham = SparsePublicControl(candidate_rows, mode="sham_novelty")
    compiler_cpu_ns = process_time_ns() - compile_start
    mlp = ConventionalAdam384(seed)
    t = process_time_ns()
    mlp_receipt = mlp.fit(candidate_rows)  # Genuine 3-restart Adam; never faked.
    adam_cpu_ns = process_time_ns() - t
    stats = {
        "candidate_compiler_CPU_ns": compiler_cpu_ns,
        "MLP_train_CPU_ns": adam_cpu_ns,
        "MLP_updates": mlp_receipt["gradient_updates_total"],
        "MLP_trained": mlp_receipt["fully_trained"],
        "MLP_best_train_accuracy": mlp_receipt["best_train_exact"],
        "candidate_features": cdiag["learned_numerical_relu_features"],
        "candidate_parameters": cdiag["numeric_parameters"],
        "fixed_numeric_parameters": fixed_info["numeric_parameters"],
        "always_numeric_parameters": always_info["numeric_parameters"],
        "random_numeric_parameters": rdiag["numeric_parameters"],
        "charged_actions_each": 384,
        "MLP_restarts": tuple(mlp_receipt["trials"]),
    }
    predictors = {
        "candidate": candidate.predict,
        "stage_a": stage_a_model.predict,
        "fixed_degree3": fixed.predict,
        "always_degree4": always.predict,
        "symbolic": symbolic.predict,
        "paid_memory": memory.predict,
        "sham_novelty": sham.predict,
        "frozen_readout": stage_a_fixed.predict,
        "random_candidate": random.predict,
        "mlp_forced": lambda s, a: mlp.predict(s, a, confidence=False),
        "mlp_native": lambda s, a: mlp.predict(s, a, confidence=True),
    }
    # The first source-private evaluator labels are deliberately not available yet.
    prelabel = freeze_public_outputs(candidate_rows, predictors,
                                     mlp.winner.probability, stats)
    return {
        "prelabel": prelabel,
        "prelabel_sha256": sha256(prelabel.encode("ascii")).hexdigest(),
        "candidate_diag": cdiag,
        "conventional": mlp_receipt,
        "numerical_cold_restore_bytes": len(candidate.snapshot()),
        "random_ledger_sha256": digest([
            [x.before, x.action, x.after, x.action_cost] for x in random_rows]),
        "candidate_ledger_sha256": digest([
            [x.before, x.action, x.after, x.action_cost] for x in candidate_rows]),
    }


def evaluator_after_freeze(world, seed, frozen):
    # No model is called after label access. All predictions were hashed first.
    if (seed not in {x for x, _ in DEVELOPMENT}
            or sha256(frozen["prelabel"].encode("ascii")).hexdigest()
               != frozen["prelabel_sha256"]):
        raise PermissionError("prelabel identity invalid or world not registered as developer")
    truth = {(state, action): world._step_oracle(state, action)
             for state, action in PUBLIC}
    rng = Random(int.from_bytes(
        sha256(f"WSP80|MULTIDEV|{seed}|two-action-v1".encode("ascii")).digest(),
        "big"))
    compositions = []
    for _ in range(32):
        state = source.STATES[rng.randrange(64)]
        first, second = rng.randrange(6), rng.randrange(6)
        finish = world._step_oracle(world._step_oracle(state, first), second)
        compositions.append((state, first, second, finish))
    score = score_frozen(frozen["prelabel"], truth, tuple(compositions))
    prelabel = json.loads(frozen["prelabel"])
    if score["prelabel_sha256"] != prelabel["sha256"]:
        raise AssertionError("evaluator prelabel/score digest mismatch")
    return score


def summarize_metrics(score):
    return {name: {
        "correct": data["physical"]["correct"],
        "wrong_confident": data["physical"]["wrong_confident"],
        "abstain": data["physical"]["abstain"],
        "never_paid_correct": data["genuinely_unpaid"]["correct"],
        "two_action_correct": data["two_action"]["correct"],
    } for name, data in sorted(score["scores"].items())}


def diagnostic_classification(records, prereg):
    thresholds = prereg["predeclared_development_diagnostics"]
    low = [r for r in records if "degree" in r["family"]]
    high = [r for r in records if "quartic" in r["family"]]
    def sum_metric(rows, arm, metric):
        return sum(r["metrics"][arm][metric] for r in rows)
    if len(low) != 4 or len(high) != 4:
        raise AssertionError("wrong developer family assignment")
    checks = {
        "lowdegree_no_false_paid_incompatibility":
            sum(r["paid_incompatible_action_count"] for r in low)
                <= thresholds["lowdegree_false_paid_incompatibilities_max"],
        "independent_symbolic_exact_parity":
            sum(r["symbolic_matches_candidate_all_public"] for r in records)
                >= thresholds["symbolic_exact_parity_worlds_min"],
        "quartic_paid_incompatibility":
            sum(r["paid_incompatible_action_count"] > 0 for r in high)
                >= thresholds["quartic_worlds_with_paid_incompatibility_min"],
        "quartic_gain_over_fixed":
            sum_metric(high, "candidate", "correct")
            - sum_metric(high, "fixed_degree3", "correct")
                >= thresholds["quartic_programmed_minus_fixed_degree3_correct_confident_aggregate_min"],
        "quartic_genuine_never_paid":
            sum_metric(high, "candidate", "never_paid_correct")
                >= thresholds["quartic_programmed_correct_confident_never_paid_aggregate_min"],
        "quartic_active_minus_random":
            sum_metric(high, "candidate", "correct")
            - sum_metric(high, "random_candidate", "correct")
                >= thresholds["quartic_active_minus_random_correct_confident_aggregate_min"],
        "conventional_fully_trained":
            sum(r["adam_converged"] for r in records)
                >= thresholds["best_Adam_converged_worlds_min"],
        "gain_vs_matched_MLP":
            sum_metric(records, "candidate", "correct")
            - sum_metric(records, "mlp_matched", "correct")
                >= thresholds["aggregate_programmed_minus_Adam_matched_coverage_correct_min"],
        "stage_a_retention":
            sum(r["stageA_correct_retained"] for r in records) /
                max(1, sum(r["stageA_preverified_confident_correct"] for r in records))
                >= thresholds["stageA_correct_confident_retained_fraction_min"],
        "registered_first_use_zero": True,
    }
    return {"classification": ("DEV_MULTIWORLD_DIAGNOSTICS_PASS"
                               if all(checks.values()) else
                               "DEV_MULTIWORLD_DIAGNOSTICS_NEGATIVE"),
            "checks": checks, "passed_count": sum(checks.values()),
            "total_checks": len(checks)}


def run():
    if sys.argv[1:] != ["--unregistered-developer-multiworld"]:
        raise PermissionError("only frozen unregistered developer worlds admitted")
    custody = validate_source_custody()
    prereg = json.loads((HERE / "dev_multi_prereg.json").read_text("utf8"))
    started_cpu, started_wall = process_time_ns(), perf_counter_ns()
    records = []
    for seed, family in DEVELOPMENT:
        roles, channels = roles_channels(seed, family)
        # Direct construction for explicitly allowed unregistered seeds ONLY.
        world = source.World(seed, family, roles, channels)
        t = process_time_ns()
        candidate_rows, random_rows, writers, stage_a = paid_sessions(world, seed)
        charged_cpu_ns = process_time_ns() - t
        frozen = freeze_one(seed, family, candidate_rows, random_rows,
                            writers, stage_a)
        # THE ONLY arbitrary-state private evaluator access happens now:
        scored = evaluator_after_freeze(world, seed, frozen)
        data = json.loads(frozen["prelabel"])["payload"]["outputs"]
        symbolic_matches = all(
            data["candidate"][i] == data["symbolic"][i]
            for i in range(384))
        incompatible = frozen["candidate_diag"]["paid_incompatible_action_channels"]
        metrics = summarize_metrics(scored)
        record = {
            "seed": seed, "family": family,
            "private_world_receipt_sha256": world.receipt()["hidden_source_sha256"],
            "private_role_channel_configuration_sha256":
                digest([roles, channels]),
            "candidate_charged_ledger_sha256": frozen["candidate_ledger_sha256"],
            "random_charged_ledger_sha256": frozen["random_ledger_sha256"],
            "stageA_paid_actions_each": 144,
            "total_paid_actions_each": 384,
            "paid_incompatible_action_count": len(incompatible),
            "paid_incompatible_action_ids": list(incompatible),
            "symbolic_matches_candidate_all_public": int(symbolic_matches),
            "stageA_preverified_confident_correct":
                scored["stageA_true_correct_confident"],
            "stageA_correct_retained":
                scored["stageA_retained_true_correct_confident"],
            "adam_converged": frozen["conventional"]["fully_trained"],
            "adam_best_charged_exact":
                frozen["conventional"]["best_train_exact"],
            "adam_total_gradient_updates":
                frozen["conventional"]["gradient_updates_total"],
            "paid_acquisition_cpu_ns": charged_cpu_ns,
            "model_training_and_scoring_cost_receipt":
                scored["cost_receipts"],
            "cold_snapshot_bytes": frozen["numerical_cold_restore_bytes"],
            "frozen_prediction_bundle_sha256": frozen["prelabel_sha256"],
            "metrics": metrics,
        }
        if (sum(metrics["candidate"][k] for k in ("correct","wrong_confident","abstain")) != 384
                or not symbolic_matches):
            # Parity is reportable negative; only invalid score totals invalidate.
            if sum(metrics["candidate"][k] for k in ("correct","wrong_confident","abstain")) != 384:
                raise AssertionError("incomplete 384-query result")
        records.append(record)
    result = {
        "schema": "wsp80.unregistered-multiworld-dev-result.v1",
        "classification": "DEVELOPMENT_ONLY_NOT_REGISTERED_SCIENCE",
        "source_sha": custody["head_sha"],
        "dev_prereg_blob": FROZEN_DEV_PREREG_BLOB,
        "developer_protocol_first_commit": FROZEN_DEV_PREREG_COMMIT,
        "unchanged_registered_prereg_blob": FROZEN_REGISTERED_PREREG_BLOB,
        "registered_seed_count_consumed": 0,
        "unregistered_worlds": len(records),
        "developer_paid_actions": 6144,
        "process_cpu_ns": process_time_ns()-started_cpu,
        "process_wall_ns": perf_counter_ns()-started_wall,
        "peak_process_rss_bytes": peak_rss_bytes(),
        "results": records,
        "predeclared_diagnostics": diagnostic_classification(records,prereg),
        "registered_science_status": "NOT_EXECUTED",
        "new_architecture_or_AGI_claim": False,
        "source_history_custody_authenticated": False,
        "first_use_authorized": False,
    }
    print("WSP80_MULTIDEV_RESULT=" + canonical(result), flush=True)


if __name__ == "__main__":
    run()
