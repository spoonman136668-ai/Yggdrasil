"""Gate28 isolated synthetic evaluator: diagnostic-only A/B/R cold subprocesses.

This module makes no claims about Bayesian-control parity, true causal
mediation, science results, original primary first-use, or native acceptance.
Run ONLY diagnostic seeds (900000..909999). All held/counterfactual reads
remain in evaluator code and are never sent to candidate learner updaters.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import core
import world

SELF = Path(__file__).resolve()
MODES = ("active", "forced")
DIAGNOSTIC_MIN = 900000
DIAGNOSTIC_MAX = 909999


def require_diagnostic(seed: int) -> None:
    if type(seed) is not int or not DIAGNOSTIC_MIN <= seed <= DIAGNOSTIC_MAX:
        raise ValueError("G28_PRIMARY_SEEDS_RESERVED: diagnostic-only evaluator")


def file_for(root: Path, arm: str, mode: str) -> Path:
    if arm not in core.ARMS or mode not in MODES:
        raise ValueError("INVALID_STATE_KEY")
    return root / (arm + "." + mode + ".json")


def source_readouts(s: dict) -> str:
    if s["source"] is None:
        raise ValueError("SOURCE_UNFROZEN")
    data = []
    for mask in (3, 19, 37, 51, 88, 171, 238):
        for action in range(core.N_ACTIONS):
            data.append(round(core.source_predict(
                s, core.as_bits(mask), action, core.Work()), 9))
    return hashlib.sha256(core.canonical(data)).hexdigest()


def _update_source(w: world.HiddenWorld, arm: str) -> tuple[dict, dict]:
    s = core.new(w.seed, arm)
    worst_work = 0
    for step in range(96):
        row = w.source(step)
        meter = core.Work()
        core.observe(s, row.context, row.action, row.consequence, meter)
        worst_work = max(worst_work, meter.count)
    core.seal_source(s)
    return s, {"steps": 96, "source_digest": s["source"]["digest"],
               "functional_source": source_readouts(s),
               "worst_work": worst_work, "state_bytes": len(core.pack(s))}


def _update_shift(w: world.HiddenWorld, phase: str, mode: str,
                  s: dict) -> tuple[dict, dict]:
    total_reward = 0
    total_regret = 0
    total_brier = 0.0
    max_work = 0
    total_work = 0
    exposures = []
    for step in range(64):
        # The caller sees the current public state BEFORE choosing a do-action.
        x = w.public_context(phase, step)
        meter = core.Work()
        if mode == "active":
            action = core.choose(s, x, meter)
        else:
            action = w.forced_action(phase, step)
        forecast = core.predict(s, x, action, meter)
        row = w.feedback(phase, step, action)
        if row.context != x:
            raise ValueError("PREACTION_CONTEXT_PARITY_FAILURE")
        # Oracle counterfactuals are evaluator-only, never learner observations.
        oracle = max(w.feedback(phase, step, a).consequence
                     for a in world.ACTIONS)
        total_regret += oracle - row.consequence
        total_reward += row.consequence
        total_brier += (forecast - row.consequence) ** 2
        exposures.append([list(x), list(row.intermediates),
                          action, row.consequence])
        core.observe(s, row.context, row.action, row.consequence, meter)
        max_work = max(max_work, meter.count)
        total_work += meter.count
    preheld_step = s["step"]
    held_reward = 0
    held_brier = 0.0
    for query in range(32):
        x = w.held_context(phase, query)
        meter = core.Work()
        a = core.choose(s, x, meter)
        pred = core.predict(s, x, a, meter)
        outcome = w.held_query(phase, query, a)
        if outcome.context != x:
            raise ValueError("HELD_CONTEXT_PARITY_FAILURE")
        held_reward += outcome.consequence
        held_brier += (pred - outcome.consequence) ** 2
        max_work = max(max_work, meter.count)
        total_work += meter.count
        # No observe on held outcomes. Only this evaluator reads held_query.
    if s["step"] != preheld_step:
        raise ValueError("HELD_QUERY_TRAINING_LEAK")
    if preheld_step != (160 if phase == "B" else 224):
        raise ValueError("MISSING_OR_DUPLICATED_EXPOSURES")
    exp_digest = hashlib.sha256(core.canonical(exposures)).hexdigest()
    stats = {"steps": 64, "mode": mode, "phase": phase,
             "reward": total_reward, "regret": total_regret,
             "prequential_brier": round(total_brier / 64, 9),
             "held_reward": held_reward, "held_queries": 32,
             "held_brier": round(held_brier / 32, 9),
             "exposure_sha256": exp_digest,
             "max_work": max_work, "total_work": total_work,
             "source_digest": s["source"]["digest"],
             "functional_source": source_readouts(s),
             "state_bytes": len(core.pack(s)),
             "model_step": s["step"],
             "edits": s["edits"], "attempts": s["attempts"]}
    return s, stats


def _child(root: Path, seed: int, phase: str) -> dict:
    require_diagnostic(seed)
    if phase not in world.PHASES or not root.is_dir():
        raise ValueError("INVALID_STAGE_OR_ROOT")
    w = world.HiddenWorld(seed, diagnostic=True)
    metrics = {}
    for arm in core.ARMS:
        if phase == "A":
            s, source = _update_source(w, arm)
            for mode in MODES:
                file_for(root, arm, mode).write_bytes(core.pack(s))
                metrics[arm + "." + mode] = source
            continue
        for mode in MODES:
            target = file_for(root, arm, mode)
            if not target.is_file():
                raise ValueError("MISSING_COLD_CHECKPOINT")
            s = core.unpack(target.read_bytes())
            expected_step = 96 if phase == "B" else 160
            if s["step"] != expected_step:
                raise ValueError("COLD_STAGE_ORDER_OR_REPLAY")
            old_source = s["source"]["digest"]
            old_function = source_readouts(s)
            s, stats = _update_shift(w, phase, mode, s)
            if (old_source != s["source"]["digest"] or
                    old_function != source_readouts(s)):
                raise ValueError("SOURCE_CAPABILITY_NOT_PRESERVED")
            target.write_bytes(core.pack(s))
            metrics[arm + "." + mode] = stats
    if phase in ("B", "R"):
        forced_digests = {metrics[arm + ".forced"]["exposure_sha256"]
                          for arm in core.ARMS}
        if len(forced_digests) != 1:
            raise ValueError("EQUAL_EXPOSURE_PARITY_FAIL")
    return {"phase": phase, "seed": seed, "pid": __import__("os").getpid(),
            "state_keys": len(metrics), "metrics": metrics,
            "primary_scored": False, "mode": "synthetic_diagnostic_only"}


def diagnostic(seed: int = 900007) -> dict:
    require_diagnostic(seed)
    stages = []
    with tempfile.TemporaryDirectory(prefix="ygg-g28-diagnostic-") as dirname:
        root = Path(dirname)
        for phase in world.PHASES:
            cmd = [sys.executable, "-B", str(SELF), "--child", phase,
                   "--seed", str(seed), "--root", str(root)]
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    check=True)
            stage = json.loads(result.stdout.strip())
            if stage["phase"] != phase or stage["primary_scored"]:
                raise ValueError("UNEXPECTED_STAGE_RESULT")
            stages.append(stage)
        pids = [stage["pid"] for stage in stages]
        if len(set(pids)) != 3:
            raise ValueError("NOT_TRUE_PROCESS_EXIT_RESTORE")
        for arm in core.ARMS:
            for mode in MODES:
                key = arm + "." + mode
                source = stages[0]["metrics"][key]
                b, r = (stage["metrics"][key] for stage in stages[1:])
                for obs in (b, r):
                    if (source["functional_source"] != obs["functional_source"]
                            or source["source_digest"] != obs["source_digest"]):
                        raise ValueError("COLD_SOURCE_RETENTION_FAIL")
                    if obs["max_work"] > core.MAX_RULE_EVALS or (
                            obs["state_bytes"] > core.MAX_STATE_BYTES):
                        raise ValueError("BOUNDED_RESOURCE_FAIL")
                cold = core.unpack(file_for(root, arm, mode).read_bytes())
                if cold["step"] != 224:
                    raise ValueError("FINAL_STATE_INCOMPLETE")
        return {"status": "G28_DIAGNOSTIC_COLD_PROCESS_PASS",
                "seed": seed, "primary_scored": False,
                "stages": [s["phase"] for s in stages],
                "distinct_processes": len(set(pids)),
                "arms": list(core.ARMS), "modes": list(MODES),
                "forced_B_exposure_hash": stages[1]["metrics"]["fixed.forced"]["exposure_sha256"],
                "forced_R_exposure_hash": stages[2]["metrics"]["fixed.forced"]["exposure_sha256"],
                "max_rule_work": max(s["metrics"][a + "." + m].get(
                    "max_work", s["metrics"][a + "." + m].get("worst_work", 0))
                    for s in stages for a in core.ARMS for m in MODES),
                "max_checkpoint_bytes": max(
                    s["metrics"][a + "." + m]["state_bytes"]
                    for s in stages for a in core.ARMS for m in MODES),
                "science": "NOT_RUN_NO_BAYESIAN_OR_CAUSAL_MEDIATOR_CONTROL"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diagnostic", action="store_true")
    parser.add_argument("--child", choices=world.PHASES)
    parser.add_argument("--seed", type=int, default=900007)
    parser.add_argument("--root", type=Path)
    opts = parser.parse_args()
    require_diagnostic(opts.seed)
    if opts.child:
        if opts.diagnostic or opts.root is None:
            raise ValueError("INVALID_CHILD_REQUEST")
        result = _child(opts.root, opts.seed, opts.child)
    elif opts.diagnostic and opts.root is None:
        result = diagnostic(opts.seed)
    else:
        raise ValueError("DIAGNOSTIC_ONLY_NO_PRIMARY_ENTRYPOINT")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
