"""Independent, whole-task WSP80 developer pipeline CPU/RSS qualification.

Registered first-use remains blocked. Each arm is a FRESH OS PROCESS that
independently pays 384 physical public actions on the unregistered seed 9001,
selects the SAME public-only policy at each step, learns, cold-predicts
all 384 public queries (forced + native), and accounts for the entire
script body including source, policy, training and readout. The parent times
subprocess lifetime as an inclusive wall-clock metric. No evaluator labels.
"""
from __future__ import annotations
from time import process_time_ns, perf_counter_ns
_SCRIPT_START_CPU = process_time_ns()
_SCRIPT_START_WALL = perf_counter_ns()

from hashlib import sha256
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
DEVELOPER_SEED = 9001
PAID_ACTIONS = 384
COMMON_STAGE_A = 144
REFERENCE_LEDGER = "56b2f5d64834caa279257e8d9333ba9bd4277c127ad71837bb4f3b9473002598"
REFERENCE_PREDICTION = {
    "programmed": "f6fb0f328280c8d06a8b35817a242f87952d25d77024dcacccf3de487cbe05a4",
    "adam": "507475fe6510515da0bf8bd1d30de498a62bffde06b05749f32798af5953d00e",
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return sha256(canonical(value).encode("ascii")).hexdigest()


def validate_arm(arm):
    if arm not in REFERENCE_PREDICTION:
        raise PermissionError("only two developer matched-action arms admitted")
    return arm


def validate_paid_receipt(result, arm, sha):
    if (type(result) is not dict or result.get("schema") != "wsp80.full-dev-arm.v1"
            or result.get("arm") != arm
            or result.get("source_commit_sha") != sha
            or result.get("developer_seed") != DEVELOPER_SEED
            or result.get("registered_seed_consumed") is not False
            or result.get("paid_actions") != PAID_ACTIONS
            or result.get("common_stageA_actions") != COMMON_STAGE_A
            or result.get("ledger_digest") != REFERENCE_LEDGER
            or result.get("prediction_digest") != REFERENCE_PREDICTION[arm]
            or result.get("public_queries") != 384
            or result.get("prediction_modes_per_query") != 2
            or result.get("script_process_cpu_ns", 0) <= 0
            or result.get("peak_process_rss_bytes", 0) <= 0):
        raise ValueError("full developer arm receipt invalid")
    if arm == "adam":
        t = result.get("adam_training_trials")
        if (type(t) is not list or len(t) != 3
                or sorted(x.get("restart") for x in t) != [0, 1, 2]
                or not all(1 <= x.get("gradient_updates", 0) <= 6000 for x in t)
                or result.get("adam_trained_at_least_95pct") is not True):
            raise ValueError("conventional real training incomplete")
    return True


def child(arm):
    validate_arm(arm)
    if os.environ.get("WSP80_DEV_SOURCE_ONLY") != "9001":
        raise PermissionError("developer source not admitted")
    from scientific_admission import audit_static_readonly
    from developer_cost_process import peak_rss_bytes
    from acquisition import InterventionPolicy, stage_a_action
    from source import World
    from controls import ConventionalAdam384
    from structural_weights import PaidStructuralWeightEditor

    custody = audit_static_readonly()
    world = World(DEVELOPER_SEED, "quartic_positive",
                  tuple(range(6)), tuple(range(6)))
    session = world.training_session()
    policy = InterventionPolicy()
    if arm == "programmed":
        model = PaidStructuralWeightEditor()
    else:
        model = None
    before_collection_cpu = process_time_ns()
    for index in range(PAID_ACTIONS):
        current = session.current
        action = (stage_a_action(DEVELOPER_SEED, index) if index < COMMON_STAGE_A
                  else policy.choose(current))
        event = session.step(action)
        policy.observe(event)
        if event.before != current or event.action_cost != 1:
            raise AssertionError("discontinuous or unpaid physical public action")
        if model is not None:
            model.charge(event.before, event.action, event.after, event.action_cost)
            if index == COMMON_STAGE_A - 1:
                model.compile()
                if model.charges != COMMON_STAGE_A:
                    raise AssertionError("missing StageA physical custody")
    after_acquisition_cpu = process_time_ns()
    if len(session.ledger) != PAID_ACTIONS:
        raise AssertionError("developer action budget incomplete")
    serialized_rows = [[list(x.before), x.action, list(x.after), x.action_cost]
                       for x in session.ledger]
    ledger_hash = digest(serialized_rows)
    if ledger_hash != REFERENCE_LEDGER:
        raise AssertionError("developer source/action/ledger changed unexpectedly")
    before_fit_cpu = process_time_ns()
    if arm == "programmed":
        model.compile()
        model = PaidStructuralWeightEditor.restore(model.snapshot())
        trained = None
    else:
        model = ConventionalAdam384(DEVELOPER_SEED)
        trained = model.fit(session.ledger)
    after_fit_cpu = process_time_ns()
    output = []
    for state in product((0, 1), repeat=6):
        for action in range(6):
            if arm == "programmed":
                forced = model.predict(state, action, force=True)
                native = model.predict(state, action)
            else:
                forced = model.predict(state, action, confidence=False)
                native = model.predict(state, action, confidence=True)
            output.append([forced, native])
    after_eval_cpu = process_time_ns()
    result = {
        "schema": "wsp80.full-dev-arm.v1",
        "arm": arm,
        "source_commit_sha": custody["head_sha"],
        "developer_seed": DEVELOPER_SEED,
        "registered_seed_consumed": False,
        "paid_actions": len(session.ledger),
        "common_stageA_actions": COMMON_STAGE_A,
        "ledger_digest": ledger_hash,
        "prediction_digest": digest(output),
        "public_queries": 384,
        "prediction_modes_per_query": 2,
        "script_process_cpu_ns": process_time_ns() - _SCRIPT_START_CPU,
        "script_wall_ns": perf_counter_ns() - _SCRIPT_START_WALL,
        "paid_source_policy_acquisition_cpu_ns":
            after_acquisition_cpu - before_collection_cpu,
        "fit_and_cold_restore_cpu_ns": after_fit_cpu - before_fit_cpu,
        "forced_and_native_readout_cpu_ns": after_eval_cpu - after_fit_cpu,
        "peak_process_rss_bytes": peak_rss_bytes(),
        "adam_training_trials": trained["trials"] if trained is not None else None,
        "adam_trained_at_least_95pct":
            trained["fully_trained"] if trained is not None else None,
        "original_frozen_parent_unchanged": True,
    }
    print("WSP80_FULL_DEV_ARM=" + canonical(result), flush=True)


def parent():
    if sys.argv[1:] != ["--developer-only"]:
        raise PermissionError("registered scientific sources are not executable")
    from scientific_admission import audit_static_readonly
    custody = audit_static_readonly()
    sha = custody["head_sha"]
    run_order = ("programmed", "adam", "adam", "programmed")
    results = []
    for arm in run_order:
        start = perf_counter_ns()
        child_process = subprocess.run(
            (sys.executable, str(HERE / "developer_full_pipeline.py"), "--child", arm),
            capture_output=True, text=True, check=True, timeout=1600,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
                 "PYTHONHASHSEED": "0", "WSP80_DEV_SOURCE_ONLY": "9001"})
        subprocess_wall = perf_counter_ns() - start
        lines = child_process.stdout.splitlines()
        matches = [line.removeprefix("WSP80_FULL_DEV_ARM=")
                   for line in lines if line.startswith("WSP80_FULL_DEV_ARM=")]
        if len(matches) != 1:
            raise AssertionError("child did not produce exactly one source receipt")
        item = json.loads(matches[0])
        validate_paid_receipt(item, arm, sha)
        item["inclusive_subprocess_wall_ns"] = subprocess_wall
        results.append(item)
    grouped = {arm: [v for v in results if v["arm"] == arm]
               for arm in REFERENCE_PREDICTION}
    if any(len(v) != 2 for v in grouped.values()):
        raise AssertionError("ABBA repeats are incomplete")
    ratios = []
    for repeat in range(2):
        a = grouped["programmed"][repeat]["script_process_cpu_ns"]
        b = grouped["adam"][repeat]["script_process_cpu_ns"]
        ratios.append(a / b)
    report = {
        "schema": "wsp80.full-task-developer-evidence.v1",
        "classification": "DEV_ONLY_STATIC_CUSTODY_PASS_SCIENTIFIC_UNVERIFIED",
        "source_commit": sha,
        "source_static_admission": custody,
        "registered_first_use_authorized": False,
        "registered_source_access_count": 0,
        "fresh_independent_paid_sessions": 4,
        "total_developer_paid_actions": 4 * PAID_ACTIONS,
        "run_order": run_order,
        "matched_ledger": REFERENCE_LEDGER,
        "arms": results,
        "script_body_CPU_ratios_per_ABBA_pair": ratios,
        "scientific_whole_process_compute_qualified": False,
        "reason_not_science":
            "Unregistered seed9001 only; script CPU starts after Python bootstrap; "
            "one source family; no 16-world first use, protected-source admission "
            "or independent scientific acceptance.",
    }
    print("WSP80_FULL_TASK_DEV_RESULT=" + canonical(report), flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--child"]:
        if len(sys.argv) != 3:
            raise PermissionError("invalid developer child")
        child(sys.argv[2])
    else:
        parent()
