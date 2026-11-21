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
import bayes
import sparse_bayes
import dense_reference
import full_reference
import world

SELF = Path(__file__).resolve()
MODES = ("active", "forced")
MODEL_ARMS = core.ARMS + bayes.ARMS + sparse_bayes.ARMS + dense_reference.ARMS
# Public, branch-frozen policy seeds, NOT hidden-world generator seeds.
CORE_POLICY_SEEDS = {arm: 28100 + i * 17 for i, arm in enumerate(core.ARMS)}


def _new_model(arm: str) -> dict:
    return (dense_reference.new(arm) if arm in dense_reference.ARMS else
            sparse_bayes.new(arm) if arm in sparse_bayes.ARMS else
            bayes.new(arm) if arm in bayes.ARMS else
            core.new(CORE_POLICY_SEEDS[arm], arm))


def _model(s: dict):
    return (dense_reference if s["arm"] in dense_reference.ARMS else
            sparse_bayes if s["arm"] in sparse_bayes.ARMS else
            bayes if s["arm"] in bayes.ARMS else core)


def _observe(s: dict, row, meter: core.Work) -> None:
    if s["arm"] in dense_reference.ARMS:
        dense_reference.observe(s, row.context, row.intermediates,
                                row.action, row.consequence, meter)
    elif s["arm"] in sparse_bayes.ARMS:
        sparse_bayes.observe(s, row.context, row.intermediates,
                             row.action, row.consequence, meter)
    elif s["arm"] in bayes.ARMS:
        bayes.observe(s, row.context, row.intermediates, row.action, row.consequence, meter)
    else:
        core.observe(s, row.context, row.action, row.consequence, meter)


def _unpack(raw: bytes) -> dict:
    doc = json.loads(raw)
    return (dense_reference.unpack(raw) if doc.get("payload", {}).get("schema") == dense_reference.SCHEMA else
            sparse_bayes.unpack(raw) if doc.get("payload", {}).get("schema") == sparse_bayes.SCHEMA else
            bayes.unpack(raw) if doc.get("payload", {}).get("schema") == bayes.SCHEMA else
            core.unpack(raw))

DIAGNOSTIC_MIN = 900000
DIAGNOSTIC_MAX = 909999


def require_diagnostic(seed: int) -> None:
    if type(seed) is not int or not DIAGNOSTIC_MIN <= seed <= DIAGNOSTIC_MAX:
        raise ValueError("G28_PRIMARY_SEEDS_RESERVED: diagnostic-only evaluator")


def file_for(root: Path, arm: str, mode: str) -> Path:
    if arm not in MODEL_ARMS or mode not in MODES:
        raise ValueError("INVALID_STATE_KEY")
    return root / (arm + "." + mode + ".json")


def source_readouts(s: dict) -> str:
    if s["source"] is None:
        raise ValueError("SOURCE_UNFROZEN")
    data = []
    for mask in (3, 19, 37, 51, 88, 171, 238):
        for action in range(core.N_ACTIONS):
            data.append(round(_model(s).source_predict(
                s, core.as_bits(mask), action, core.Work()), 9))
    return hashlib.sha256(core.canonical(data)).hexdigest()


def _update_source(w: world.HiddenWorld, arm: str) -> tuple[dict, dict]:
    s = _new_model(arm)
    worst_work = 0
    for step in range(96):
        row = w.source(step)
        meter = core.Work()
        _observe(s, row, meter)
        worst_work = max(worst_work, meter.count)
    _model(s).seal_source(s)
    return s, {"steps": 96, "source_digest": s["source"]["digest"],
               "functional_source": source_readouts(s),
               "worst_work": worst_work, "state_bytes": len(_model(s).pack(s))}


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
            action = _model(s).choose(s, x, meter)
        else:
            action = w.forced_action(phase, step)
        forecast = _model(s).predict(s, x, action, meter)
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
        _observe(s, row, meter)
        max_work = max(max_work, meter.count)
        total_work += meter.count
    preheld_step = s["step"]
    held_reward = 0
    held_brier = 0.0
    for query in range(32):
        x = w.held_context(phase, query)
        meter = core.Work()
        a = _model(s).choose(s, x, meter)
        pred = _model(s).predict(s, x, a, meter)
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
             "state_bytes": len(_model(s).pack(s)),
             "model_step": s["step"],
             "edits": s["edits"], "attempts": s["attempts"]}
    return s, stats


def require_forced_parity(metrics: dict) -> str:
    """Require identical actual interventions and outcomes for EVERY model arm.

    A matching subset of local learners cannot prove equality for the
    fully trained Bayesian and sparse causal controls.
    """
    try:
        digests = {metrics[arm + ".forced"]["exposure_sha256"]
                   for arm in MODEL_ARMS}
    except (KeyError, TypeError) as exc:
        raise ValueError("EQUAL_EXPOSURE_PARITY_FAIL") from exc
    if len(digests) != 1:
        raise ValueError("EQUAL_EXPOSURE_PARITY_FAIL")
    return next(iter(digests))


def _child(root: Path, seed: int, phase: str) -> dict:
    require_diagnostic(seed)
    if phase not in world.PHASES or not root.is_dir():
        raise ValueError("INVALID_STAGE_OR_ROOT")
    w = world.HiddenWorld(seed, diagnostic=True)
    metrics = {}
    for arm in MODEL_ARMS:
        if phase == "A":
            s, source = _update_source(w, arm)
            for mode in MODES:
                file_for(root, arm, mode).write_bytes(_model(s).pack(s))
                metrics[arm + "." + mode] = source
            continue
        for mode in MODES:
            target = file_for(root, arm, mode)
            if not target.is_file():
                raise ValueError("MISSING_COLD_CHECKPOINT")
            s = _unpack(target.read_bytes())
            expected_step = 96 if phase == "B" else 160
            if s["step"] != expected_step:
                raise ValueError("COLD_STAGE_ORDER_OR_REPLAY")
            old_source = s["source"]["digest"]
            old_function = source_readouts(s)
            s, stats = _update_shift(w, phase, mode, s)
            if (old_source != s["source"]["digest"] or
                    old_function != source_readouts(s)):
                raise ValueError("SOURCE_CAPABILITY_NOT_PRESERVED")
            target.write_bytes(_model(s).pack(s))
            metrics[arm + "." + mode] = stats
    if phase in ("B", "R"):
        require_forced_parity(metrics)
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
        for arm in MODEL_ARMS:
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
                cold = _unpack(file_for(root, arm, mode).read_bytes())
                if cold["step"] != 224:
                    raise ValueError("FINAL_STATE_INCOMPLETE")
        return {"status": "G28_DIAGNOSTIC_COLD_PROCESS_PASS",
                "seed": seed, "primary_scored": False,
                "stages": [s["phase"] for s in stages],
                "distinct_processes": len(set(pids)),
                "arms": list(MODEL_ARMS), "modes": list(MODES),
                "forced_B_exposure_hash": stages[1]["metrics"]["fixed.forced"]["exposure_sha256"],
                "forced_R_exposure_hash": stages[2]["metrics"]["fixed.forced"]["exposure_sha256"],
                "max_rule_work": max(s["metrics"][a + "." + m].get(
                    "max_work", s["metrics"][a + "." + m].get("worst_work", 0))
                    for s in stages for a in MODEL_ARMS for m in MODES),
                "max_checkpoint_bytes": max(
                    s["metrics"][a + "." + m]["state_bytes"]
                    for s in stages for a in MODEL_ARMS for m in MODES),
                "science": "NOT_RUN_NO_INDEPENDENTLY_QUALIFIED_STRONG_MATCHED_CONTROL"}



def compare_controls(seed: int = 900071,
                     diagnostic_cohort: str = "diagnostic_shifted") -> dict:
    """Diagnostic equal-action comparison, NEVER primary science.

    All arms fit the identical A/B/R public exposures. For held rows an
    evaluator scores identical forced actions and, separately, each arm's
    action preference. None of those held outcomes is observed by a model.
    The full-grammar reference is deliberately unconstrained/secondary.
    """
    import time

    require_diagnostic(seed)
    w = world.HiddenWorld(seed, diagnostic=True,
                          diagnostic_cohort=diagnostic_cohort)
    selected = ("adaptive", "fixed", "causal_bayes_reward",
                "sparse_causal_reward", "dense_causal_reward",
                "dense_causal_nullmix", "full_reference_reward")
    modules = {arm: (full_reference if arm in full_reference.ARMS else
                     dense_reference if arm in dense_reference.ARMS else
                     sparse_bayes if arm in sparse_bayes.ARMS else
                     bayes if arm in bayes.ARMS else core)
               for arm in selected}
    states = {arm: (core.new(CORE_POLICY_SEEDS[arm], arm)
                    if arm in core.ARMS else modules[arm].new(arm))
              for arm in selected}
    reference = "full_reference_reward"
    measured = {arm: {"cpu_ns": 0, "peak_rule_work": 0,
                      "total_rule_work": 0, "prequential_loss": {},
                      "source_digest": None}
                for arm in selected}
    phases = {}
    for phase in world.PHASES:
        public_rows = []
        for step in range(96 if phase == "A" else 64):
            row = (w.source(step) if phase == "A" else
                   w.feedback(phase, step, w.forced_action(phase, step)))
            public_rows.append([list(row.context), list(row.intermediates),
                                row.action, row.consequence])
            for arm in selected:
                module = modules[arm]
                state = states[arm]
                meter = (full_reference.Meter() if arm == reference
                         else core.Work())
                start = time.process_time_ns()
                if phase != "A":
                    prediction = module.predict(state, row.context,
                                                row.action, meter)
                    measured[arm]["prequential_loss"].setdefault(
                        phase, []).append((prediction - row.consequence) ** 2)
                if arm in core.ARMS:
                    module.observe(state, row.context, row.action,
                                   row.consequence, meter)
                else:
                    module.observe(state, row.context, row.intermediates,
                                   row.action, row.consequence, meter)
                measured[arm]["cpu_ns"] += time.process_time_ns() - start
                work = (meter.evaluations if arm == reference else meter.count)
                measured[arm]["peak_rule_work"] = max(
                    measured[arm]["peak_rule_work"], work)
                measured[arm]["total_rule_work"] += work
        phases[phase] = {"public_exposure_sha256": hashlib.sha256(
            core.canonical(public_rows)).hexdigest(),
            "public_exposures": len(public_rows)}
        if phase == "A":
            for arm in selected:
                modules[arm].seal_source(states[arm])
                measured[arm]["source_digest"] = states[arm]["source"]["digest"]
                measured[arm]["source_edits"] = states[arm].get("edits", 0)
                measured[arm]["source_attempts"] = states[arm].get("attempts", 0)
        else:
            phase_results = {}
            for arm in selected:
                module, state = modules[arm], states[arm]
                total_brier = 0.0
                selected_reward = 0
                for query in range(32):
                    context = w.held_context(phase, query)
                    equal_action = w.forced_action(phase, query)
                    meter = (full_reference.Meter() if arm == reference
                             else core.Work())
                    start = time.process_time_ns()
                    forecast = module.predict(state, context,
                                              equal_action, meter)
                    chosen = module.choose(state, context, meter)
                    measured[arm]["cpu_ns"] += time.process_time_ns() - start
                    forced_row = w.held_query(phase, query, equal_action)
                    selected_row = w.held_query(phase, query, chosen)
                    if (forced_row.context != context or
                            selected_row.context != context):
                        raise ValueError("HELD_CONTEXT_PARITY")
                    total_brier += (forecast - forced_row.consequence) ** 2
                    selected_reward += selected_row.consequence
                    work = (meter.evaluations if arm == reference else meter.count)
                    measured[arm]["peak_rule_work"] = max(
                        measured[arm]["peak_rule_work"], work)
                    measured[arm]["total_rule_work"] += work
                if state["step"] != (160 if phase == "B" else 224):
                    raise ValueError("INVALID_TRAINING_EXPOSURE_COUNT")
                if (state["source"]["digest"] !=
                        measured[arm]["source_digest"]):
                    raise ValueError("SOURCE_CHANGED_UNDER_INTERFERENCE")
                packed = module.pack(state)
                if module.pack(module.unpack(packed)) != packed:
                    raise ValueError("CHECKPOINT_COLD_FUNCTION_MISMATCH")
                if arm != reference and (
                        len(packed) > core.MAX_STATE_BYTES or
                        measured[arm]["peak_rule_work"] > core.MAX_RULE_EVALS):
                    raise ValueError("MATCHED_RESOURCE_BUDGET")
                states[arm] = module.unpack(packed)
                phase_results[arm] = {
                    "equal_action_held_brier": round(total_brier / 32, 9),
                    "selected_held_reward": selected_reward,
                    "prequential_brier": round(sum(
                        measured[arm]["prequential_loss"][phase]) / 64, 9),
                    "checkpoint_bytes": len(packed),
                    "peak_rule_work": measured[arm]["peak_rule_work"],
                    "cpu_ms_accumulated": round(
                        measured[arm]["cpu_ns"] / 1000000, 3)}
                if arm in core.ARMS:
                    phase_results[arm]["post_source_edits"] = (
                        state["edits"] - measured[arm]["source_edits"])
                    phase_results[arm]["post_source_attempts"] = (
                        state["attempts"] - measured[arm]["source_attempts"])
            phases[phase]["scores"] = phase_results
    for phase in ("B", "R"):
        full = phases[phase]["scores"][reference]["equal_action_held_brier"]
        for arm in selected:
            phases[phase]["scores"][arm]["delta_brier_vs_full"] = round(
                full - phases[phase]["scores"][arm]["equal_action_held_brier"],
                9)
    return {
        "status": "G28_EQUAL_EXPOSURE_CONTROL_DIAGNOSTIC_ONLY",
        "seed": seed, "cohort": diagnostic_cohort,
        "models": list(selected),
        "full_reference_is_unconstrained": True,
        "strongest_matched_control_adequacy": "UNVERIFIED",
        "scientific_primary_scored": False,
        "original_world_first_use": False,
        "independent_reproduction": False,
        "phases": phases}



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
