"""NLD-03: public task cue in one 20-cell shared native state.

Same already-exposed R9 smoke seed 3 and exact NLD-02 public episodes.
This code is a bounded development diagnostic, not new scientific first-use.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "nld02"))
from shared_bank import (  # noqa: E402
    SEED, FIT, EVAL, PATTERNS, PublicSource,
    source_only_correct_action, digest,
)
from action_cells import Cell, DELAY, canonical, features, check_action  # noqa: E402

SCHEMA = "itd01.nld03.public-task-cue-shared-native.v1"
KNOWN_FIT_TRACES = {
    "FIT_A": "02b355fcc4caf86e37802d746e45fbd1395920b8d3d594f34a3da55e29ccc463",
    "FIT_B": "7a300dfe9bcb7b8c1222eae4b00a88c46cfd3d72ddefb145e3248f4942d69299",
}
CUE = {"A": -1, "B": 1}
N = 20


def x20(sensors, cue, enabled):
    """One shared feature map; the cue is the *public supplied* task identifier."""
    if type(cue) is not int or cue not in (-1, 1):
        raise ValueError("NLD03_PUBLIC_CUE_REQUIRED")
    original = features(sensors)
    return original + tuple(cue * z if enabled else z for z in original)


class CueNative:
    def __init__(self, use_cue: bool):
        if type(use_cue) is not bool:
            raise ValueError("NLD03_CUE_MODE_INVALID")
        self.use_cue = use_cue
        self.name = "native-shared-public-cue" if use_cue else "native-shared-cue-blind"
        self.cells = [Cell() for _ in range(N)]
        self.bias = 0.
        self.pending = {}
        self.feedback_updates = 0
        self.weight_changes = 0

    def choose(self, sensors, cue):
        local = [c.response(phi) for c, phi in zip(
            self.cells, x20(sensors, cue, self.use_cue))]
        vote = self.bias + sum(local)
        for i in range(N):
            vote += .025 * local[i] * local[(i+1) % N]
        result = int(vote > 0)
        check_action(result)
        return result

    def observe_public_action(self, token, sensors, cue, action, tick):
        x20(sensors, cue, self.use_cue)
        check_action(action)
        if (type(token) is not str or not token or token in self.pending or
                type(tick) is not int or tick < 0):
            raise ValueError("NLD03_DUPLICATE_OR_INVALID_PUBLIC_EVENT")
        self.pending[token] = (tuple(sensors), cue, action, tick)

    def learn_delayed(self, token, success, tick):
        if token not in self.pending:
            raise ValueError("NLD03_FEEDBACK_MISSING_ACTION")
        if type(success) is not bool or type(tick) is not int:
            raise ValueError("NLD03_FEEDBACK_FORMAT")
        sensors, cue, action, start = self.pending[token]
        if tick - start != DELAY:
            raise ValueError("NLD03_EARLY_OR_LATE_FEEDBACK")
        correct = action if success else (1 - action)
        mismatch = self.choose(sensors, cue) != correct
        desired = 1 if correct else -1
        for cell, phi in zip(self.cells, x20(sensors, cue, self.use_cue)):
            cell.adjust(desired, phi, mismatch)
        if mismatch:
            self.bias = max(-8., min(8., self.bias + .4 * desired))
            self.weight_changes += 1
        self.feedback_updates += 1
        del self.pending[token]

    def state(self):
        if self.pending:
            raise ValueError("NLD03_PENDING_FEEDBACK_AT_CHECKPOINT")
        return {
            "schema": SCHEMA, "use_cue": self.use_cue,
            "cells": [{"fast": c.fast, "slow": c.slow, "updates": c.public_updates}
                      for c in self.cells],
            "bias": self.bias,
            "feedback_updates": self.feedback_updates,
            "weight_changes": self.weight_changes,
        }

    def save(self):
        payload = self.state()
        blob = canonical({"payload": payload, "sha256": digest(payload)})
        if len(blob) > 32768:
            raise ValueError("NLD03_CHECKPOINT_TOO_LARGE")
        return blob

    @classmethod
    def restore(cls, blob):
        if type(blob) is not bytes or not (0 < len(blob) <= 32768):
            raise ValueError("NLD03_CHECKPOINT_SIZE")
        try:
            outer = json.loads(blob)
            payload = outer["payload"]
            expected = outer["sha256"]
        except (ValueError, KeyError, TypeError):
            raise ValueError("NLD03_CHECKPOINT_STRUCTURE")
        if (type(outer) is not dict or set(outer) != {"payload", "sha256"} or
                type(expected) is not str or digest(payload) != expected):
            raise ValueError("NLD03_CHECKPOINT_HASH")
        if (type(payload) is not dict or
                set(payload) != {"schema", "use_cue", "cells", "bias",
                                 "feedback_updates", "weight_changes"} or
                payload["schema"] != SCHEMA or
                type(payload["use_cue"]) is not bool or
                type(payload["cells"]) is not list or
                len(payload["cells"]) != N):
            raise ValueError("NLD03_CHECKPOINT_SOURCE_IDENTITY")
        obj = cls(payload["use_cue"])
        obj.cells = []
        for state in payload["cells"]:
            if (type(state) is not dict or
                    set(state) != {"fast", "slow", "updates"} or
                    type(state["updates"]) is not int or state["updates"] < 0 or
                    any(type(state[key]) not in (int, float) or
                        not math.isfinite(state[key]) or
                        not (-32 <= state[key] <= 32) for key in ("fast", "slow"))):
                raise ValueError("NLD03_CELL_STATE_INVALID")
            obj.cells.append(Cell(state["fast"], state["slow"], state["updates"]))
        bias = payload["bias"]
        if type(bias) not in (int, float) or not math.isfinite(bias) or not -8 <= bias <= 8:
            raise ValueError("NLD03_BIAS_INVALID")
        obj.bias = bias
        for attr in ("feedback_updates", "weight_changes"):
            v = payload[attr]
            if type(v) is not int or v < 0:
                raise ValueError("NLD03_COUNTER_INVALID")
            setattr(obj, attr, v)
        if obj.save() != blob:
            raise ValueError("NLD03_CHECKPOINT_NONCANONICAL")
        return obj


class CuePerceptron:
    def __init__(self, use_cue: bool):
        self.use_cue = use_cue
        self.name = "trained-cue-perceptron" if use_cue else "trained-blind-perceptron"
        self.weights = [0.] * N
        self.bias = 0.
        self.pending = {}
        self.feedback_updates = 0

    def choose(self, sensors, cue):
        return int(self.bias + sum(w * z for w, z in zip(
            self.weights, x20(sensors, cue, self.use_cue))) > 0)

    def observe_public_action(self, token, sensors, cue, action, tick):
        x20(sensors, cue, self.use_cue)
        check_action(action)
        if token in self.pending:
            raise ValueError("NLD03_PERCEPTRON_DUPLICATE")
        self.pending[token] = (tuple(sensors), cue, action, tick)

    def learn_delayed(self, token, success, tick):
        if token not in self.pending:
            raise ValueError("NLD03_PERCEPTRON_MISSING")
        sensors, cue, action, born = self.pending[token]
        if type(success) is not bool or tick - born != DELAY:
            raise ValueError("NLD03_PERCEPTRON_FEEDBACK_INVALID")
        correct = action if success else 1 - action
        if self.choose(sensors, cue) != correct:
            desired = 1 if correct else -1
            self.weights = [w + desired * z for w, z in zip(
                self.weights, x20(sensors, cue, self.use_cue))]
            self.bias += desired
        self.feedback_updates += 1
        del self.pending[token]

    def save(self):
        if self.pending:
            raise ValueError("NLD03_PERCEPTRON_PENDING")
        return canonical({"weights": self.weights, "bias": self.bias,
                          "feedback_updates": self.feedback_updates,
                          "use_cue": self.use_cue})


class CueEpisodic:
    def __init__(self, use_cue: bool):
        self.use_cue = use_cue
        self.name = "trained-cue-episodic" if use_cue else "trained-blind-episodic"
        self.memory = {}
        self.pending = {}
        self.feedback_updates = 0

    def key(self, sensors, cue):
        x20(sensors, cue, self.use_cue)
        bits = "".join("1" if s else "0" for s in sensors)
        return str(cue) + ":" + bits if self.use_cue else bits

    def choose(self, sensors, cue):
        return self.memory.get(self.key(sensors, cue), 0)

    def observe_public_action(self, token, sensors, cue, action, tick):
        self.key(sensors, cue)
        check_action(action)
        if token in self.pending:
            raise ValueError("NLD03_EPISODIC_DUPLICATE")
        self.pending[token] = (tuple(sensors), cue, action, tick)

    def learn_delayed(self, token, success, tick):
        if token not in self.pending:
            raise ValueError("NLD03_EPISODIC_MISSING")
        sensors, cue, action, born = self.pending[token]
        if type(success) is not bool or tick - born != DELAY:
            raise ValueError("NLD03_EPISODIC_FEEDBACK_INVALID")
        self.memory[self.key(sensors, cue)] = action if success else 1 - action
        self.feedback_updates += 1
        del self.pending[token]

    def save(self):
        if self.pending:
            raise ValueError("NLD03_EPISODIC_PENDING")
        return canonical({"memory": self.memory, "feedback_updates": self.feedback_updates,
                          "use_cue": self.use_cue})


def train_public(arms, family):
    if family not in CUE:
        raise ValueError("NLD03_SOURCE_ROLE_INVALID")
    cue = CUE[family]
    role = "FIT_" + family
    src = PublicSource(SEED, role, family)
    due, trace = {}, []
    arrivals = 0
    for tick in range(FIT + DELAY):
        for token, action, sensors, success in due.pop(tick, []):
            for arm in arms:
                arm.learn_delayed(token, success, tick)
            trace.append({"token": token, "feedback_tick": tick, "success": success})
            arrivals += 1
        if tick >= FIT:
            continue
        sensors = src.next_sensors()
        action = (sum(sensors) + tick) % 2
        success = bool(action == source_only_correct_action(family, sensors))
        token = f"NLD02-R9-SMOKE-{SEED}-{role}-{tick}"
        for arm in arms:
            arm.observe_public_action(token, sensors, cue, action, tick)
        due.setdefault(tick + DELAY, []).append((token, action, sensors, success))
        trace.append({"token": token, "tick": tick,
                      "sensors": sensors, "action": action})
    actual_digest = digest(trace)
    if (due or arrivals != FIT or src.calls != FIT or
            actual_digest != KNOWN_FIT_TRACES[role] or
            any(arm.pending for arm in arms)):
        raise AssertionError("NLD03_ORIGINAL_PUBLIC_SOURCE_TRACE_DRIFT")
    return {"role": role, "public_actions": FIT,
            "delayed_feedback_events": arrivals,
            "trace_sha256": actual_digest, "source_draws": src.calls}


def evaluate(arms, family, role):
    if (family, role) not in {
        ("A", "VALID_A_PRE"), ("A", "VALID_A_POST"),
        ("A", "DEV_A_RETAINED"), ("B", "VALID_B")
    }:
        raise ValueError("NLD03_PUBLIC_SOURCE_ROLE_INVALID")
    src = PublicSource(SEED, role, family)
    cue = CUE[family]
    score = {a.name: 0 for a in arms}
    blank = CueNative(True)
    score["erased-public-cue-native"] = 0
    before = {a.name: a.save() for a in arms}
    differences = {"cue_native_vs_erased": 0,
                   "cue_native_vs_blind_native": 0}
    for _ in range(EVAL):
        sensors = src.next_sensors()
        truth = source_only_correct_action(family, sensors)
        choices = {}
        for arm in arms:
            action = arm.choose(sensors, cue)
            check_action(action)
            choices[arm.name] = action
            score[arm.name] += int(action == truth)
        erased = blank.choose(sensors, cue)
        score["erased-public-cue-native"] += int(erased == truth)
        differences["cue_native_vs_erased"] += int(
            choices["native-shared-public-cue"] != erased)
        differences["cue_native_vs_blind_native"] += int(
            choices["native-shared-public-cue"] !=
            choices["native-shared-cue-blind"])
    if src.calls != EVAL or any(a.save() != before[a.name] for a in arms):
        raise AssertionError("NLD03_READONLY_EVALUATION_DRIFT")
    return {"role": role, "cue_value_from_public_task_id": cue,
            "n": EVAL, "family_for_scoring_only": family,
            "accuracy": {name: value / EVAL for name, value in score.items()},
            "correct_counts": score,
            "public_role_sha256": digest({"seed": SEED, "family": family,
                                          "role": role, "n": EVAL}),
            "action_disagreements": differences, "updates_during_eval": 0}


def checkpoint(model):
    raw = model.save()
    restored = CueNative.restore(raw)
    decisions = []
    for cue in (-1, 1):
        for sensors in PATTERNS:
            original, replicated = model.choose(sensors, cue), restored.choose(sensors, cue)
            if original != replicated:
                raise AssertionError("NLD03_RESTORED_DECISION_DRIFT")
            decisions.append(original)
    if model.save() != restored.save():
        raise AssertionError("NLD03_RESTORED_BYTES_DRIFT")
    return {"checkpoint_bytes": len(raw),
            "checkpoint_sha256": hashlib.sha256(raw).hexdigest(),
            "matching_two_task_32_decisions": len(decisions),
            "decision_sha256": digest(decisions), "cold_restore_exact": True}


def run(seed=SEED):
    if type(seed) is not int or seed != SEED:
        raise ValueError("NLD03_EXISTING_PUBLIC_R9_SMOKE_SEED_3_ONLY")
    cue_native = CueNative(True)
    blind_native = CueNative(False)
    arms = [
        cue_native, blind_native, CuePerceptron(True), CuePerceptron(False),
        CueEpisodic(True), CueEpisodic(False),
    ]
    a_pre = evaluate(arms, "A", "VALID_A_PRE")
    fit_a = train_public(arms, "A")
    a_checkpoint = checkpoint(cue_native)
    a_post = evaluate(arms, "A", "VALID_A_POST")
    fit_b = train_public(arms, "B")
    b_checkpoint = checkpoint(cue_native)
    a_after_b = evaluate(arms, "A", "DEV_A_RETAINED")
    b_post = evaluate(arms, "B", "VALID_B")
    if any(arm.feedback_updates != 2*FIT for arm in arms):
        raise AssertionError("NLD03_EQUAL_PUBLIC_FEEDBACK")
    a_score = a_after_b["accuracy"]
    cue_gain = (a_score[cue_native.name] - a_score[blind_native.name])
    erase_gain = (a_score[cue_native.name] -
                  a_score["erased-public-cue-native"])
    switch_decisions = sum(cue_native.choose(s, -1) != cue_native.choose(s, 1)
                           for s in PATTERNS)
    same_capacity_cue_blind_switch = sum(
        blind_native.choose(s, -1) != blind_native.choose(s, 1)
        for s in PATTERNS)
    if same_capacity_cue_blind_switch != 0:
        raise AssertionError("NLD03_CUE_BLIND_CONTROL_LEAKED_TASK_ID")
    return {
        "schema": SCHEMA,
        "original_nld02_head": "1773c1da550ce6bc774d1310ea0f93e35afffefd",
        "source_seed": SEED,
        "existing_consumed_public_source_only": True,
        "first_use_heldout": False,
        "original_r9_frozen_101_211_307_replayed": False,
        "public_task_cue_used": "ORIGINAL_DISLOSED_R9_FAMILY_ID_A_MINUS1_B_PLUS1",
        "native_single_shared_cell_array_length": N,
        "native_per_family_bank_count": 0,
        "human_designed_context_interaction_features": True,
        "same_20_cell_capacity_for_cue_and_blind_native": True,
        "family_ids_known_before_each_action": True,
        "source_traces": [fit_a, fit_b],
        "fit_feedback_per_arm": {a.name: a.feedback_updates for a in arms},
        "fit_model_serialized_bytes": {a.name: len(a.save()) for a in arms},
        "cue_native_actual_weight_changes": cue_native.weight_changes,
        "blind_native_actual_weight_changes": blind_native.weight_changes,
        "cue_native_after_a_cold_restore": a_checkpoint,
        "cue_native_after_b_cold_restore": b_checkpoint,
        "scores": {"a_pre": a_pre, "a_after_a": a_post,
                   "a_after_b": a_after_b, "b_after_b": b_post},
        "cue_native_retained_A_advantage_over_blind": cue_gain,
        "cue_native_retained_A_advantage_over_erased": erase_gain,
        "cue_native_task_flip_policy_disagreements_of_16": switch_decisions,
        "blind_native_task_flip_policy_disagreements_of_16": same_capacity_cue_blind_switch,
        "native_context_information_supported": bool(
            cue_gain > 0 and erase_gain > 0 and switch_decisions > 0),
        "native_better_than_equally_informed_trained_controls": "NOT_PRESUMED",
        "representation": "MEASURE_FIT_A_AND_CONTEXT_CONDITIONED_DECISION_STATE",
        "retention": "MEASURE_A_AFTER_B_AGAINST_SAME_CAPACITY_CUE_BLIND",
        "causal_composition": "NOT_TESTED_HANDCODED_TASK_CUE_AND_FEATURES",
        "unfamiliar_transfer": "NOT_TESTED_R9_C_ZERO_SHOT_NEGATIVE_PRESERVED",
        "matched_cpu_rss_resource_efficiency": False,
        "ckb_scientific_admission": "NOT_OBSERVED",
        "disposition": "NLD03_PUBLIC_CUE_DEV_ONLY_RETAIN_RESULTS",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(run(), sort_keys=True, separators=(",", ":"), allow_nan=False))
