"""TGAP22: frozen causal-switch attribution on a research-only numeric learner.

The preregistration was committed before this file:
0201c733501b8dfe20e6f1e07ea016542814928a.
Evaluator-only privileged interventions are diagnostic controls, NOT native
Yggdrasil training, standalone science gains, or deployable decision policies.
"""
from __future__ import annotations

import copy
import json
import time
from pathlib import Path

from tgap21_same_address_dev import (
    TwoSlotMemory, Uninformed, witness, digest, brier,
)
from noisy_regime_memory_dev import RollingBeta, BayesianHMM

PREREG = "0201c733501b8dfe20e6f1e07ea016542814928a"
SOURCE = "engineering_fixture_only"
FIT = (8501, 0, 24, 48, 72)
HELD = (
    (8603, 0, 15, 40),
    (8621, 0, 21, 44),
    (8647, 0, 17, 35),
    (8663, 1, 15, 40),
    (8681, 1, 21, 44),
    (8699, 1, 17, 35),
)
ARMS = (
    "baseline_fit", "no_fit", "restore_only_oracle",
    "route_only_oracle", "route_plus_restore_oracle",
    "full_phase_oracle", "rolling_8", "bayes_hmm", "source_only"
)
PRIVILEGED = frozenset((
    "restore_only_oracle", "route_only_oracle",
    "route_plus_restore_oracle", "full_phase_oracle"
))


def require(ok, tag):
    if not ok:
        raise ValueError("YGG_TGAP22_" + tag)


def fit():
    """Single, one-address source-only FIT A->B->A with no oracle interventions."""
    seed, role, first, second, n = FIT
    research = TwoSlotMemory()
    controls = {"rolling_8": RollingBeta(), "bayes_hmm": BayesianHMM()}
    frozen_A_slot = None
    snapshot_after_B = None
    tape = []
    for t in range(n):
        action = t % 2
        result = witness(seed, role, t, action, first, second)
        tape.append((t, action, result))
        research.observe(t, action, result)
        for control in controls.values():
            control.observe(action, result)
        if t == first - 1:
            frozen_A_slot = copy.deepcopy(research.slots[0])
        if t == second - 1:
            snapshot_after_B = copy.deepcopy(research)
    require(frozen_A_slot is not None and snapshot_after_B is not None
            and len(tape) == 72 and research.next_step == 72,
            "FIT_SEQUENCE")
    frozen_bytes = research.checkpoint()
    restored = TwoSlotMemory.restore(frozen_bytes, digest(frozen_bytes))
    require(restored.checkpoint() == frozen_bytes, "FIT_COLD")
    a_after_B = copy.deepcopy(snapshot_after_B.slots[0])
    a_after_return = copy.deepcopy(restored.slots[0])
    old_drifts = [
        int(frozen_A_slot[a] != a_after_B[a]) for a in (0, 1)
    ]
    return {
        "model": restored,
        "controls": controls,
        "pristine_A_slot": frozen_A_slot,
        "A_after_B": a_after_B,
        "A_after_return": a_after_return,
        "old_A_drift": sum(old_drifts),
        "fit_witnesses": len(tape),
        "checkpoint_size": len(frozen_bytes),
        "checkpoint_sha256": digest(frozen_bytes),
        "checkpoint_restored_exactly": True,
    }


def states_for_world(bundle):
    """Separate cloned ledgers, all receiving the same witnessed consequences."""
    states = {
        arm: bundle["model"].new_public_world()
        for arm in ARMS
        if arm in ("baseline_fit", "restore_only_oracle",
                   "route_only_oracle", "route_plus_restore_oracle",
                   "full_phase_oracle")
    }
    states["no_fit"] = TwoSlotMemory()
    states["rolling_8"] = copy.deepcopy(bundle["controls"]["rolling_8"])
    states["bayes_hmm"] = copy.deepcopy(bundle["controls"]["bayes_hmm"])
    states["source_only"] = Uninformed()
    require(set(states) == set(ARMS), "ARMS")
    return states


def evaluator_only_intervention(arm, state, t, first, second,
                                pristine_A_slot):
    """This function deliberately uses private boundaries ONLY for oracle arms."""
    if arm not in PRIVILEGED:
        return
    if arm in ("restore_only_oracle", "route_plus_restore_oracle") and t == second:
        state.slots[0] = copy.deepcopy(pristine_A_slot)
    if arm == "full_phase_oracle":
        state.active = 1 if first <= t < second else 0
    elif arm in ("route_only_oracle", "route_plus_restore_oracle") and t >= second:
        state.active = 0


def evaluate_one_world(bundle, seed, role, first, second):
    require((seed, role, first, second) in HELD, "HELD_WORLD")
    states = states_for_world(bundle)
    scores = {name: {"all": [], "return": []} for name in ARMS}
    routing = {name: {"return_steps": 0, "selected_A": 0,
                      "heuristic_switches": 0} for name in ARMS
               if isinstance(states[name], TwoSlotMemory)}
    tape = []
    for t in range(64):
        action = t % 2
        consequence = witness(seed, role, t, action, first, second)
        tape.append((t, action, consequence))
        for name in ARMS:
            state = states[name]
            if name in PRIVILEGED:
                evaluator_only_intervention(
                    name, state, t, first, second, bundle["pristine_A_slot"])
            if isinstance(state, TwoSlotMemory):
                before = state.switches
                if t >= second:
                    routing[name]["return_steps"] += 1
                    routing[name]["selected_A"] += int(state.active == 0)
            prediction = state.predict(action)
            require(type(prediction) is float and 0 <= prediction <= 1,
                    "PREDICTION_BOUNDS")
            loss = brier(prediction, consequence)
            scores[name]["all"].append(loss)
            if t >= second:
                scores[name]["return"].append(loss)
            if isinstance(state, TwoSlotMemory):
                state.observe(t, action, consequence)
                routing[name]["heuristic_switches"] += state.switches - before
            else:
                state.observe(action, consequence)
    require(len(tape) == 64 and
            all(len(x["all"]) == 64 and
                len(x["return"]) == 64 - second
                for x in scores.values()), "HELD_COUNTS")
    return scores, routing, tuple(tape)


def aggregate(bundle):
    grouped = []
    for w in HELD:
        score, routing, tape = evaluate_one_world(bundle, *w)
        grouped.append((w, score, routing, tape))
    totals = {name: {} for name in ARMS}
    for arm in ARMS:
        for phase in ("all", "return"):
            losses = [x for _, s, _, _ in grouped for x in s[arm][phase]]
            totals[arm][phase] = round(sum(losses) / len(losses), 8)
    role_results = {}
    for role in (0, 1):
        role_results[str(role)] = {
            arm: round(
                sum(v for w, s, _, _ in grouped if w[1] == role
                    for v in s[arm]["return"]) /
                sum(len(s[arm]["return"]) for w, s, _, _ in grouped
                    if w[1] == role),
                8,
            ) for arm in ARMS
        }
    baseline_routing = {
        "return_steps": sum(r["baseline_fit"]["return_steps"]
                            for _, _, r, _ in grouped),
        "selected_A": sum(r["baseline_fit"]["selected_A"]
                          for _, _, r, _ in grouped),
        "heuristic_switches": sum(r["baseline_fit"]["heuristic_switches"]
                                  for _, _, r, _ in grouped),
    }
    baseline = totals["baseline_fit"]["return"]
    improvements = {
        name: round(baseline - totals[name]["return"], 8)
        for name in ("restore_only_oracle", "route_only_oracle",
                     "route_plus_restore_oracle", "full_phase_oracle")
    }
    det = improvements["route_only_oracle"] >= .01
    corrupt = improvements["restore_only_oracle"] >= .01
    joint = (not det and not corrupt and
             improvements["route_plus_restore_oracle"] >= .01)
    return {
        "brier": totals,
        "by_initial_role_return_brier": role_results,
        "privileged_delta_vs_baseline_return": improvements,
        "diagnostics": {
            "route_selection_contributes_on_fixture": det,
            "slot_contamination_contributes_on_fixture": corrupt,
            "combined_interaction_on_fixture": joint,
            "oracle_variants_are_not_fair_learners": True,
        },
        "baseline_routing": baseline_routing,
        "held_witnesses_per_policy": sum(len(tape)
                                        for _, _, _, tape in grouped),
        "return_witnesses_per_policy": sum(64 - w[3] for w, _, _, _ in grouped),
        "worlds": len(grouped)
    }


def proof():
    started = time.monotonic()
    protocol = json.loads(Path(__file__).with_name(
        "tgap22_protocol.json").read_text(encoding="utf-8"))
    require(
        protocol["schema"] ==
        "yggdrasil.tgap22.slot-detection-vs-selection-vs-contamination.frozen-dev.v1"
        and protocol["fit"]["seed"] == FIT[0]
        and protocol["fit"]["initial_role"] == FIT[1]
        and protocol["fit"]["switches"] == list(FIT[2:4])
        and protocol["fit"]["steps"] == FIT[4]
        and [(x["seed"], x["role"], *x["switches"])
             for x in protocol["held"]["worlds"]] == list(HELD)
        and protocol["held"]["held_witnesses_per_arm"] == 384
        and protocol["controls_and_custody"]["no_candidate_algorithm_change"] is True,
        "FROZEN_CONTRACT",
    )
    fitted = fit()
    obs = aggregate(fitted)
    require(obs["held_witnesses_per_policy"] == 384
            and obs["return_witnesses_per_policy"] == 146
            and obs["worlds"] == 6
            and all(t["all"] == .25 and t["return"] == .25
                    for name, t in obs["brier"].items()
                    if name == "source_only"), "SCORING_CONTRACT")
    return {
        "schema": "yggdrasil.tgap22.sealed-synthetic-diagnostic.v1",
        "prereg_commit": PREREG,
        "source_mode": SOURCE,
        "fit_witnessed_actions": fitted["fit_witnesses"],
        "fit_checkpoint_bytes": fitted["checkpoint_size"],
        "fit_checkpoint_sha256": fitted["checkpoint_sha256"],
        "fit_cold_exact": fitted["checkpoint_restored_exactly"],
        "old_A_slot_actions_changed_after_B": fitted["old_A_drift"],
        "old_A_slot_snapshot": fitted["pristine_A_slot"],
        "old_A_slot_after_B": fitted["A_after_B"],
        "old_A_slot_after_return": fitted["A_after_return"],
        **obs,
        "engineering_gate": "PASS",
        "scientific_gate": "DEV_NO_GO_SYNTHETIC_ORACLE_ATTRIBUTION",
        "canonical_native_modified": False,
        "protected_first_use": False,
        "deployment": "NONE",
        "wall_clock_seconds_excluding_checkout": round(
            time.monotonic() - started, 6),
    }


if __name__ == "__main__":
    print("YGG_TGAP22_RESULT=" + json.dumps(proof(), sort_keys=True))
