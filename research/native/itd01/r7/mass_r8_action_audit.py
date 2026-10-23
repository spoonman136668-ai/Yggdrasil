"""Mass Research R8: public-action omission and observational indistinguishability.

Synthetic paired interventions only. This does not call the frozen R7 generator,
cohort study, scientific first-use authority, controller, or source-family H1/H2.
"""
from __future__ import annotations

import hashlib
import inspect
import itertools
import json
import time
import tracemalloc

from native_cells import Colony

SOURCE_PARENT = "f3cdabdb3420bb8604e41dda9903ae65eba008e7"
SCHEMA = "mass.r8.public-action-information.v1"
FAMILIES = ("constant_required_action", "sensor_composed_required_action")
SENSORS = tuple(itertools.product((False, True), repeat=4))
N_REPEATS = 2
DELAY = 2


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


class ActionAwareEpisodicControl:
    """Public-action/outcome memory. No hidden model, reward oracle or rule."""

    def __init__(self):
        self.successful = {}
        self.public_updates = 0

    def observe_completed(self, sensors, public_action, public_success):
        # This model receives only the public action and its delayed success.
        if type(public_action) is not int or public_action not in (0, 1):
            raise ValueError("MASS_R8_CONTROL_INVALID_ACTION")
        if type(public_success) is not bool:
            raise ValueError("MASS_R8_CONTROL_INVALID_PUBLIC_SUCCESS")
        desired = public_action if public_success else 1-public_action
        key = tuple(sensors)
        if key in self.successful and self.successful[key] != desired:
            raise AssertionError("MASS_R8_INCONSISTENT_PUBLIC_EPISODIC_EVIDENCE")
        self.successful[key] = desired
        self.public_updates += 1

    def choose(self, sensors):
        key = tuple(sensors)
        if key not in self.successful:
            raise ValueError("MASS_R8_CONTROL_UNTRAINED_SENSOR")
        return self.successful[key]


def _target(family, mode, sensors):
    if family not in FAMILIES or mode not in (0, 1):
        raise ValueError("MASS_R8_UNREGISTERED_WORLD")
    # The target is PRIVATE environment scoring logic; never passed to a model.
    structural = (int(sensors[0] and sensors[2]) ^ int(sensors[1])
                  if family == "sensor_composed_required_action" else 0)
    return mode ^ structural


def _public_result(family, mode, sensors, action):
    if type(action) is not int or action not in (0, 1):
        raise ValueError("MASS_R8_INVALID_PUBLIC_ACTION")
    return bool(action == _target(family, mode, sensors))


def _native_inference(colony, context, sensors):
    return int(colony.predict(context, sensors))


def paired_worlds(family):
    if family not in FAMILIES:
        raise ValueError("MASS_R8_FROZEN_FAMILY_ONLY")
    context = "A" if family == FAMILIES[0] else "B"
    native = [Colony(), Colony()]
    informed = [ActionAwareEpisodicControl(), ActionAwareEpisodicControl()]
    due = [[], []]
    raw_public = [[], []]
    to_native = [[], []]
    first_feedback_tick = [None, None]
    paired_checkpoints = []
    offered = 0
    released = 0
    for tick in range(len(SENSORS)*N_REPEATS+DELAY):
        # First release genuinely mature consequences. Neither native learner
        # can be updated at t or t+1 for an action performed at time t.
        for world in (0, 1):
            released_items = [item for item in due[world] if item["due"] == tick]
            for item in released_items:
                if item["due"]-item["action_tick"] != DELAY:
                    raise AssertionError("MASS_R8_CAUSAL_DELAY_BROKEN")
                native[world].learn_completed_public_feedback(
                    context, item["sensors"], item["success"], DELAY)
                informed[world].observe_completed(
                    item["sensors"], item["action"], item["success"])
                to_native[world].append({
                    "context": context, "sensors": list(item["sensors"]),
                    "observed_success": item["success"],
                    "feedback_delay": DELAY,
                    "release_tick": tick,
                })
                if first_feedback_tick[world] is None:
                    first_feedback_tick[world] = tick
                released += 1
            due[world] = [item for item in due[world]
                          if item["due"] != tick]
        if native[0].checkpoint() != native[1].checkpoint():
            raise AssertionError("MASS_R8_IDENTICAL_INPUT_DIFFERENT_LEARNED_STATE")
        paired_checkpoints.append(digest([
            native[0].checkpoint().decode(), native[1].checkpoint().decode()
        ]))
        if tick >= len(SENSORS)*N_REPEATS:
            continue
        index = tick % len(SENSORS)
        rep = tick // len(SENSORS)
        sensors = SENSORS[index]
        a0 = (sum(sensors) + rep) % 2
        actions = (a0, 1-a0)
        if _native_inference(native[0], context, sensors) != \
                _native_inference(native[1], context, sensors):
            raise AssertionError("MASS_R8_ACTION_ONLY_DIFFERS_NATIVE_INPUT")
        successes = [
            _public_result(family, world, sensors, actions[world])
            for world in (0, 1)
        ]
        if successes[0] != successes[1]:
            raise AssertionError("MASS_R8_PAIR_REWARD_NOT_INDISTINGUISHABLE")
        for world in (0, 1):
            raw_public[world].append({
                "action_tick": tick, "context": context,
                "sensors": list(sensors), "public_action": actions[world],
                "public_success_revealed_at_tick": tick + DELAY,
                "observed_success_when_released": successes[world],
            })
            due[world].append({
                "due": tick+DELAY, "action_tick":tick,
                "sensors": sensors, "action":actions[world],
                "success":successes[world],
            })
            offered += 1
    if any(due) or offered != 64 or released != 64:
        raise AssertionError("MASS_R8_PUBLIC_INTERACTION_BUDGET_DRIFT")
    if first_feedback_tick != [DELAY, DELAY]:
        raise AssertionError("MASS_R8_EARLY_OUTCOME_DISCLOSURE")
    if to_native[0] != to_native[1]:
        raise AssertionError("MASS_R8_LEARNER_INPUTS_NOT_IDENTICAL")
    if raw_public[0] == raw_public[1]:
        raise AssertionError("MASS_R8_PUBLIC_INTERVENTIONS_NOT_DISTINCT")
    if native[0].checkpoint() != native[1].checkpoint():
        raise AssertionError("MASS_R8_FINAL_PRIVATE_STATE_NOT_IDENTICAL")

    # Strictly no feedback after fitting. This is same-sensor future episode
    # consistency, NOT unfamiliar sensor value or new causal-family transfer.
    test = list(reversed(SENSORS))
    scores = [0, 0]
    informed_scores = [0, 0]
    for sensors in test:
        native_choice = [_native_inference(n, context, sensors)
                         for n in native]
        if native_choice[0] != native_choice[1]:
            raise AssertionError("MASS_R8_NATIVE_PAIRED_CHOICE_DIVERGED")
        t = [_target(family, mode, sensors) for mode in (0,1)]
        if t[0] == t[1]:
            raise AssertionError("MASS_R8_HIDDEN_CAUSAL_MODES_NOT_OPPOSED")
        for world in (0,1):
            scores[world] += int(native_choice[world] == t[world])
            informed_scores[world] += int(informed[world].choose(sensors)
                                          == t[world])

    if sum(scores) != len(test) or informed_scores != [16,16]:
        raise AssertionError("MASS_R8_INFORMATION_SUFFICIENCY_CONTROL_DRIFT")

    return {
        "family":family, "native_public_context":context,
        "worlds":2, "paired_public_action_interventions_per_world":32,
        "paired_delayed_public_outcomes_per_world":32,
        "first_public_feedback_tick":first_feedback_tick,
        "native_inputs_sha256":[digest(x) for x in to_native],
        "public_action_histories_sha256":[digest(x) for x in raw_public],
        "native_checkpoint_sha256":[hashlib.sha256(n.checkpoint()).hexdigest()
                                    for n in native],
        "all_paired_learned_states_equal_each_tick": len(paired_checkpoints)==34,
        "native_eval_success_per_world":[v/16 for v in scores],
        "native_paired_mean_success":sum(scores)/32,
        "action_aware_control_updates_per_world":
            [x.public_updates for x in informed],
        "action_aware_control_success_per_world":
            [v/16 for v in informed_scores],
        "independent_unfamiliar_task_family_transfer":False,
        "native_three_seed_r7_retention_gate":"UNCHANGED_NO_GO_NOT_RERUN",
    }


def audit():
    # Signature is evidence of omitted causal input, not hidden source lookup.
    pred = inspect.signature(Colony.predict)
    fit = inspect.signature(Colony.learn_completed_public_feedback)
    if "action" in pred.parameters or "action" in fit.parameters:
        raise ValueError("MASS_R8_NATIVE_ACTION_INTERFACE_CHANGED")
    started = time.process_time()
    tracemalloc.start()
    family_results = {family: paired_worlds(family) for family in FAMILIES}
    _, heap_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed = time.process_time() - started
    if elapsed <= 0 or heap_peak <= 0:
        raise AssertionError("MASS_R8_RESOURCE_METER_EMPTY")
    return {
        "schema":SCHEMA, "r7_native_exact_parent":SOURCE_PARENT,
        "scope":"SYNTHETIC_ACTION_INTERVENTION_INFORMATION_SCREEN_ONLY",
        "tested_causal_law_families":list(FAMILIES),
        "original_r7_cohorts_rerun":False,
        "independently_unfamiliar_original_source_first_use":False,
        "native_wingless_executed":False,
        "native_yggdrasil_new_model_implemented":False,
        "original_Ygg_R7_frozen_science":"NO_GO_UNCHANGED",
        "public_action_observable_to_action_aware_control":True,
        "public_action_observable_to_original_ygg_native":False,
        "measured_process_cpu_seconds":round(elapsed,6),
        "python_tracemalloc_peak_bytes_not_whole_process_rss":heap_peak,
        "per_model_cpu_or_rss_parity":"NOT_QUALIFIED",
        "scientific_admission":"NONE",
        "family_results":family_results,
        "disposition":
            "YGG_R7_ACTION_OMITTED_CAUSAL_HISTORY_NONIDENTIFIABILITY_PROVED",
    }


if __name__ == "__main__":
    print(json.dumps(audit(),sort_keys=True,separators=(",",":")))
