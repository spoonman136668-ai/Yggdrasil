"""CKAD25-R: read-only, retrospective replay of native sparse repair.

No new source actions, policy authority, code-path change to the learner, or
fresh scientific evaluation. The original CKAD25 four held rows were consumed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from yggdrasil.native_ckad_dev_campaign import witnessed
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "research/contrib/chatgpt/CKAD-25/qualified-development-runs/44331408493"
CHECKPOINT_SHA = "c52681bf26f08817b3747647472913fa792da2de33f74b8fa7c0f2b0e78c119f"
EXPECTED_SOURCE = "d743aafea7446d89a20d24fb3a7bdf5fa9c62c72"


def need(ok, reason):
    if not ok:
        raise ValueError("CKAD25R_" + reason)


def read_frozen():
    left = (EVIDENCE/"linux/stage-02.native.json").read_bytes()
    right = (EVIDENCE/"windows/stage-02.native.json").read_bytes()
    need(left == right and digest(left) == CHECKPOINT_SHA, "SOURCE_CHECKPOINT_DRIFT")
    left_eval = (EVIDENCE/"linux/evaluation.json").read_bytes()
    need(left_eval == (EVIDENCE/"windows/evaluation.json").read_bytes(), "PLATFORM_EVAL_DRIFT")
    evaluation = json.loads(left_eval)
    need(evaluation["checkpoint_sha256"] == CHECKPOINT_SHA and
         evaluation["metrics"]["answered"] == 0 and
         evaluation["metrics"]["correct"] == 0 and
         evaluation["metrics"]["held"] == 4 and
         evaluation["metrics"]["constant_zero_correct"] == 3 and
         evaluation["metrics"]["constant_one_correct"] == 1 and
         evaluation["scientific_pass"] is False, "HISTORICAL_BASELINE_DRIFT")
    for platform in ("linux", "windows"):
        record = json.loads((EVIDENCE/platform/"campaign-result.json").read_bytes())
        need(record["source_sha"] == EXPECTED_SOURCE and
             record["final_checkpoint_sha256"] == CHECKPOINT_SHA and
             record["observations"] == 12 and
             record["scientific_first_use"] is False and
             record["scientific_pass"] is False, "SOURCE_OWNER_EVIDENCE_DRIFT")
    return left, evaluation


def score(predictions, held):
    answered = sum(p is not None for p in predictions)
    correct = sum(p is not None and p == row[2] for p, row in zip(predictions, held))
    incorrect = sum(p is not None and p != row[2] for p, row in zip(predictions, held))
    return {"answered": answered, "correct": correct, "incorrect": incorrect,
            "total": len(held), "predictions": predictions}


def run():
    raw, historical = read_frozen()
    native = NativeCumulativeLearner.restore(raw, CHECKPOINT_SHA)
    old_raw = native.checkpoint()
    held = witnessed()[12:]
    need(len(held) == 4 and
         digest(canonical([[c,a] for c,a,_ in held])) == historical["held_inputs_sha256"] and
         digest(canonical([y for _,_,y in held])) == historical["held_truth_sha256"],
         "HISTORICAL_EVALUATOR_DRIFT")
    baseline = score([native.predict(0,c,a) for c,a,_ in held], held)
    need(baseline["answered"] == 0 and baseline["correct"] == 0, "BASELINE_REPLAY_DRIFT")
    observed = native.info()["observed_inputs"]
    need(observed[0] == 12 and native.info()["events"] == 2, "SOURCE_OBSERVATIONS_DRIFT")
    state, hyp, cost = native.repair_sparse(0)
    need(native.checkpoint() == old_raw and
         state._source.checkpoint() == native._source.checkpoint() and
         state._properties.checkpoint() == native._properties.checkpoint() and
         state._events == native._events and
         state._quarantined == native._quarantined and
         state.info()["observed_inputs"] == observed, "OLD_KNOWLEDGE_OR_SOURCE_CHANGED")
    after_raw = state.checkpoint()
    cold = NativeCumulativeLearner.restore(after_raw, digest(after_raw))
    need(cold.checkpoint() == after_raw and cold.info() == state.info(),
         "COLD_REPAIR_NOT_IDENTICAL")
    repaired = score([cold.predict(0,c,a) for c,a,_ in held], held)
    positive = (hyp.eligible and state is not native and
                repaired["answered"] == 4 and repaired["correct"] == 4)
    result = {
        "schema": "yggdrasil.ckad25r.retrospective-repair-result.v1",
        "source_checkpoint_sha256": CHECKPOINT_SHA,
        "source_original_training_commit": EXPECTED_SOURCE,
        "source_execution": "previously-consumed-CKAD25-12-row-engineering-fixture",
        "input_observations": observed[0],
        "additional_source_observations": 0,
        "original_held_results_already_consumed": True,
        "unmodified": baseline, "repaired": repaired,
        "constant_zero_correct": 3, "constant_one_correct": 1,
        "sparse_eligible": bool(hyp.eligible),
        "solver_status": int(hyp.info()["solver_status"]),
        "sparse_active_weights": hyp.info()["active_weights"],
        "fitted_sparse_coefficients_sha256": digest(hyp.checkpoint()),
        "old_snapshot_unchanged": native.checkpoint() == old_raw,
        "output_checkpoint_sha256": digest(after_raw),
        "cold_restore_verified": True,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "disposition": "RETROSPECTIVE_DIAGNOSTIC_POSITIVE" if positive else "RETROSPECTIVE_DIAGNOSTIC_NEGATIVE",
        "strongest_conventional_control": "same native repair_sparse conventional minimum-support MILP",
        "superiority_over_matched_conventional_control": False,
        "new_model_training": False,
        "source_first_use": False,
        "scientific_pass": False,
        "promotion_authorized": False,
        "deployment_authorized": False,
    }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical(result))
    print("CKAD25R_VERDICT=" + result["disposition"])
    print("CKAD25R_REPAIRED=" + json.dumps(result["repaired"], sort_keys=True))
    print("CKAD25R_FROZEN_SOURCE=" + result["source_checkpoint_sha256"])
    print("CKAD25R_RESULT_SHA256=" + digest(canonical(result)))


if __name__ == "__main__":
    main()
