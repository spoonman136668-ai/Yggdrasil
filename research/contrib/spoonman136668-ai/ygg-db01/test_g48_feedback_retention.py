"""G48: synthetic native-feedback learning and checkpoint controls.

G38's engineered periodicity decoder is retained; no native reward-learning
claim, held-out transfer, or scientific acceptance follows from this test.
"""
import json
import unittest

from native_dg1a import DG1APrototype, GENOME_PARAMETER_COUNT, INPUTS, HIDDEN, SharedGenome
from g38_native_learning import (CUES, NOVEL_CUES, ROUNDS, FRAMES,
                                 GRADIENT_CALLS, MARGIN, action, sensory,
                                 perceived_valence, run_development, value)
from matched_feedback import matched_feedback
from g40_adaptation import accuracy
from test_g39_retention_transfer import freeze_genome, restore_genome

ARMS = ("matched", "antithetic", "no_feedback", "frozen")
CHECKPOINTS = (0, 4, 8, 16)


def run(arm, attenuation="full", seed_offset=0, feedback_condition="mapped"):
    if type(arm) is not str or arm not in ARMS:
        raise ValueError("YGG_G48_ARM")
    if type(attenuation) is not str or attenuation not in (
            "full", "sensory_half", "second_half"):
        raise ValueError("YGG_G53_INVALID_ATTENUATION")
    if type(seed_offset) is not int or seed_offset not in (0, 4096):
        raise ValueError("YGG_G54_SEED_PROFILE")
    if type(feedback_condition) is not str or feedback_condition not in (
            "mapped", "phase_shift"):
        raise ValueError("YGG_G54_WAVEFORM_PROFILE")
    model = DG1APrototype()
    genome = run_development("mapped").genome
    initial = model.initial_state()
    checkpoints = []
    diagnostics = []
    g51_genomes = []
    start_genome = genome
    parts = ("first", "first_bias", "second", "second_bias")
    drift = lambda a, b: sum((x - y) ** 2 for name in parts for x, y in zip(getattr(a, name), getattr(b, name))) ** 0.5

    def record(rounds):
        blob = freeze_genome(genome)
        restored = restore_genome(blob)
        g51_genomes.append(restored)
        diagnostics.append({
            "rounds": rounds,
            "per_cue": [{"cue": cue, "signed_output": round(value(model, restored, cue), 12),
                         "chosen_action": action(model, restored, cue),
                         "correct_reversed_action": -1 if cue > 0 else 1}
                        for cue in (-1.0, -0.5, -0.25, 0.25, 0.5, 1.0)],
            "parameter_distance_from_start": round(drift(start_genome, restored), 12)
        })
        checkpoints.append({
            "rounds": rounds,
            "source": accuracy(model, restored, NOVEL_CUES, 1),
            "reversed": accuracy(model, restored, NOVEL_CUES, -1),
            "interpolation": accuracy(model, restored, (-0.25, 0.25), -1),
            "checkpoint_size": len(blob),
            "restored_equal": restored == genome
        })

    record(0)
    for rnd in range(ROUNDS):
        for cue in CUES:
            chosen = action(model, genome, cue)
            if rnd % 4 == 0:
                chosen = -chosen
            # The world owns the reversed answer. The learner only receives
            # chosen action, local cue and the returned waveform.
            correct = int(chosen == -(1 if cue > 0 else -1))
            if arm == "antithetic":
                correct = 1 - correct
            condition = ("no_feedback" if arm == "no_feedback"
                         else feedback_condition)
            waveform = matched_feedback(correct, condition,
                                        length=FRAMES, seed=100 + rnd + seed_offset)
            valence = perceived_valence(model, genome, waveform)
            target = chosen * valence * MARGIN if valence else value(
                model, genome, cue)
            for _ in range(GRADIENT_CALLS):
                candidate = model.fit_one_cell(
                    initial, sensory(cue), genome, 1, 1,
                    target, learning_rate=0.5)
                if arm != "frozen":
                    genome = (candidate if attenuation == "full" else
                              g53_attenuate(genome, candidate, attenuation))
        if rnd + 1 in CHECKPOINTS:
            record(rnd + 1)
    interactions = ROUNDS * len(CUES)
    return {
        "arm": arm, "checkpoints": checkpoints,
        "interactions": interactions,
        "feedback_frames": interactions * FRAMES,
        "gradient_calls": interactions * GRADIENT_CALLS,
        "genome_parameters": genome.parameter_count,
        "genome": genome,
        "g49_diagnostics": diagnostics,
        "g51_genomes": g51_genomes
    }


def build_report():
    rows = []
    for arm in ARMS:
        row = run(arm)
        row.pop("genome")
        row.pop("g49_diagnostics")
        row.pop("g51_genomes")
        rows.append(row)
    return {
        "schema": "yggdrasil.g48.synthetic-native-feedback-retention.v1",
        "evidence": "SELF_AUTHORED_SYNTHETIC_DEV_ONLY",
        "fixed_engineered_feedback_decoder": True,
        "antithetic_control_is_not_random_shuffling": True,
        "scientific_acceptance": "NO_GO",
        "genuine_transfer": "UNVERIFIED",
        "primary_execution_allowed": False,
        "rows": rows
    }


def build_g49_report():
    rows = []
    for arm in ARMS:
        r = run(arm)
        rows.append({"arm": arm, "checkpoints": r["g49_diagnostics"],
                     "interactions": r["interactions"],
                     "gradient_calls": r["gradient_calls"],
                     "genome_parameters": r["genome_parameters"]})
    return {
        "schema": "yggdrasil.g49.synthetic-cue-margin-diagnostic.v1",
        "evidence": "SELF_AUTHORED_SYNTHETIC_DEV_ONLY",
        "scientific_acceptance": "NO_GO",
        "reward_decoder": "EXTERNALLY_ENGINEERED",
        "primary_execution_allowed": False,
        "rows": rows
    }


def g50_boundary_from_checkpoint(checkpoint):
    """Descriptive endpoint secant, not a claim of globally linear behavior."""
    cues = checkpoint["per_cue"]
    if len(cues) != 6 or [x["cue"] for x in cues] != [-1.0, -0.5, -0.25, 0.25, 0.5, 1.0]:
        raise ValueError("YGG_G50_CUE_GRID")
    outputs = [x["signed_output"] for x in cues]
    if any(type(x) not in (float, int) for x in outputs):
        raise ValueError("YGG_G50_NONNUMERIC")
    import math
    if not all(math.isfinite(x) for x in outputs):
        raise ValueError("YGG_G50_NONFINITE")
    intercept = (outputs[0] + outputs[-1]) / 2.0
    slope = (outputs[-1] - outputs[0]) / 2.0
    crossings = []
    for left, right in zip(cues, cues[1:]):
        y1, y2 = left["signed_output"], right["signed_output"]
        if (y1 <= 0 < y2) or (y2 <= 0 < y1):
            x1, x2 = left["cue"], right["cue"]
            crossings.append(round(x1 - y1 * (x2 - x1) / (y2 - y1), 12))
    return {
        "rounds": checkpoint["rounds"],
        "endpoint_intercept": round(intercept, 12),
        "endpoint_slope": round(slope, 12),
        "endpoint_zero_crossing": round(-intercept / slope, 12)
                                  if abs(slope) > 1e-12 else None,
        "observed_bracketed_crossings": crossings,
        "all_negative": all(x < 0 for x in outputs),
        "all_positive": all(x >= 0 for x in outputs),
        "parameter_distance_from_start": checkpoint["parameter_distance_from_start"]
    }


def build_g50_report(results):
    rows = []
    for arm in ARMS:
        checkpoints = results[arm]["g49_diagnostics"]
        rows.append({"arm": arm,
                     "checkpoints": [g50_boundary_from_checkpoint(c)
                                     for c in checkpoints],
                     "genome_parameters": results[arm]["genome_parameters"],
                     "gradient_calls": results[arm]["gradient_calls"]})
    return {
        "schema": "yggdrasil.g50.synthetic-decision-boundary-diagnostic.v1",
        "interpretation": "ENDPOINT_SECANT_AND_OBSERVED_SIGN_BRACKETS_ONLY",
        "evidence": "SELF_AUTHORED_SYNTHETIC_DEV_ONLY",
        "fixed_engineered_feedback_decoder": True,
        "scientific_acceptance": "NO_GO",
        "primary_execution_allowed": False,
        "rows": rows
    }


def g51_groups(before, after):
    """Partition an unchanged 398-parameter genome by interpretable coordinates."""
    import math
    sensory_indices = set(j * INPUTS + INPUTS - 1 for j in range(HIDDEN))
    components = {
        "sensory_input_weights": [(a - b) ** 2 for i, (a, b) in enumerate(
            zip(before.first, after.first)) if i in sensory_indices],
        "other_first_layer_weights": [(a - b) ** 2 for i, (a, b) in enumerate(
            zip(before.first, after.first)) if i not in sensory_indices],
        "hidden_bias": [(a - b) ** 2 for a, b in zip(before.first_bias, after.first_bias)],
        "second_layer_weights": [(a - b) ** 2 for a, b in zip(before.second, after.second)],
        "output_bias": [(a - b) ** 2 for a, b in zip(before.second_bias, after.second_bias)]
    }
    counts = {name: len(values) for name, values in components.items()}
    if sum(counts.values()) != GENOME_PARAMETER_COUNT:
        raise ValueError("YGG_G51_BAD_PARAMETER_PARTITION")
    return {name: {"parameters": counts[name], "l2_change": round(math.sqrt(sum(vals)), 15)}
            for name, vals in components.items()}


def build_g51_report(results):
    """Counterfactual single-step probes, discarded after measurement.

    Feedback waveform is generated in the synthetic world from the chosen action.
    No rule label is supplied to fit_one_cell, which still uses the engineered G38
    periodicity decoder. All probe arms reuse identical frozen checkpoints.
    """
    model = DG1APrototype()
    initial = model.initial_state()
    rows = []
    for trained_arm in ("matched", "antithetic"):
        for round_index, genome in zip(CHECKPOINTS, results[trained_arm]["g51_genomes"]):
            before_negative = value(model, genome, -1.0)
            before_positive = value(model, genome, 1.0)
            for cue in CUES:
                policy_action = action(model, genome, cue)
                # Match the G48 exploration schedule when the checkpoint
                # begins an actual training round. Round 16 is post-horizon.
                exploration_applied = round_index < ROUNDS and round_index % 4 == 0
                chosen = -policy_action if exploration_applied else policy_action
                correct = int(chosen == -(1 if cue > 0 else -1))
                for feedback in ("matched", "antithetic", "no_feedback"):
                    outcome = 1 - correct if feedback == "antithetic" else correct
                    condition = "no_feedback" if feedback == "no_feedback" else "mapped"
                    wave = matched_feedback(outcome, condition, length=FRAMES, seed=100 + round_index)
                    decoded = perceived_valence(model, genome, wave)
                    target = chosen * decoded * MARGIN if decoded else value(model, genome, cue)
                    updated = model.fit_one_cell(initial, sensory(cue), genome, 1, 1,
                                                 target, learning_rate=0.5)
                    after_negative = value(model, updated, -1.0)
                    after_positive = value(model, updated, 1.0)
                    rows.append({
                        "trained_arm": trained_arm, "rounds": round_index,
                        "training_cue": cue, "feedback": feedback,
                        "policy_action": policy_action, "chosen_action": chosen,
                        "exploration_applied": exploration_applied,
                        "post_training_probe": round_index >= ROUNDS,
                        "decoded_valence": decoded,
                        "delta_intercept": round(((after_negative + after_positive) -
                                                 (before_negative + before_positive)) / 2.0, 15),
                        "delta_slope": round(((after_positive - after_negative) -
                                             (before_positive - before_negative)) / 2.0, 15),
                        "delta_output_negative": round(after_negative - before_negative, 15),
                        "delta_output_positive": round(after_positive - before_positive, 15),
                        "parameter_groups": g51_groups(genome, updated)
                    })
    return {
        "schema": "yggdrasil.g51.synthetic-counterfactual-update-attribution.v1",
        "evidence": "SELF_AUTHORED_SYNTHETIC_DEV_ONLY",
        "probe_updates_committed_to_learner": False,
        "probe_gradient_calls": len(rows),
        "feedback_decoder": "EXTERNALLY_ENGINEERED_G38",
        "source_training_budget_unchanged": True,
        "G48_exploration_schedule_replicated_for_in_horizon_probes": True,
        "round_16_is_post_training_probe": True,
        "scientific_acceptance": "NO_GO",
        "genuine_transfer": "UNVERIFIED",
        "primary_execution_allowed": False,
        "rows": rows
    }


G52_ARMS = ("full", "omit_output_bias", "omit_hidden_bias",
            "omit_sensory_weights", "omit_other_first_weights",
            "omit_second_weights", "no_update")


def g52_counterfactual_genome(before, candidate, arm):
    """Revert one disjoint parameter group's one-step delta, without retraining."""
    if type(arm) is not str or arm not in G52_ARMS:
        raise ValueError("YGG_G52_INVALID_ARM")
    if arm == "full":
        return candidate
    if arm == "no_update":
        return before
    first = list(candidate.first)
    first_bias = candidate.first_bias
    second = candidate.second
    second_bias = candidate.second_bias
    if arm == "omit_sensory_weights":
        for j in range(HIDDEN):
            first[j * INPUTS + INPUTS - 1] = before.first[j * INPUTS + INPUTS - 1]
    if arm == "omit_other_first_weights":
        for j in range(HIDDEN):
            for k in range(INPUTS - 1):
                first[j * INPUTS + k] = before.first[j * INPUTS + k]
    if arm == "omit_hidden_bias":
        first_bias = before.first_bias
    if arm == "omit_second_weights":
        second = before.second
    if arm == "omit_output_bias":
        second_bias = before.second_bias
    return SharedGenome(tuple(first), first_bias, second, second_bias)


def build_g52_report(results):
    """Remove single groups from the SAME frozen counterfactual update.

    Nonlinear group interactions forbid treating these differences as additive
    causal decompositions or as evidence of native reward comprehension.
    """
    model = DG1APrototype()
    initial = model.initial_state()
    rows = []
    for trained_arm in ("matched", "antithetic"):
        for round_index, genome in zip(CHECKPOINTS, results[trained_arm]["g51_genomes"]):
            old_neg = value(model, genome, -1.0)
            old_pos = value(model, genome, 1.0)
            for cue in CUES:
                policy_action = action(model, genome, cue)
                explore = round_index < ROUNDS and round_index % 4 == 0
                chosen = -policy_action if explore else policy_action
                correct = int(chosen == -(1 if cue > 0 else -1))
                for feedback in ("matched", "antithetic"):
                    outcome = 1 - correct if feedback == "antithetic" else correct
                    wave = matched_feedback(outcome, "mapped",
                                            length=FRAMES, seed=100 + round_index)
                    valence = perceived_valence(model, genome, wave)
                    target = chosen * valence * MARGIN
                    candidate = model.fit_one_cell(initial, sensory(cue), genome,
                                                   1, 1, target, learning_rate=0.5)
                    for arm in G52_ARMS:
                        modified = g52_counterfactual_genome(genome, candidate, arm)
                        new_neg = value(model, modified, -1.0)
                        new_pos = value(model, modified, 1.0)
                        rows.append({
                            "trained_arm": trained_arm,
                            "rounds": round_index, "training_cue": cue,
                            "feedback": feedback, "arm": arm,
                            "chosen_action": chosen,
                            "exploration_applied": explore,
                            "delta_intercept": round(
                                (new_neg + new_pos - old_neg - old_pos) / 2.0, 15),
                            "delta_slope": round(
                                (new_pos - new_neg - old_pos + old_neg) / 2.0, 15),
                            "delta_negative": round(new_neg - old_neg, 15),
                            "delta_positive": round(new_pos - old_pos, 15),
                            "genome_parameters": modified.parameter_count
                        })
    return {
        "schema": "yggdrasil.g52.synthetic-single-group-delta-reversal.v1",
        "evidence": "SELF_AUTHORED_SYNTHETIC_DEV_ONLY",
        "parameter_groups_are_nonadditive": True,
        "probe_updates_committed_to_learner": False,
        "unmodified_learning_rule": True,
        "diagnostic_updates_per_source_feedback": 1,
        "diagnostic_gradient_calls": len(rows) // len(G52_ARMS),
        "scientific_acceptance": "NO_GO",
        "genuine_transfer": "UNVERIFIED",
        "primary_execution_allowed": False,
        "rows": rows
    }


G53_INTERVENTIONS = ("sensory_half", "second_half")
G53_CONTROL_ARMS = ("matched", "antithetic", "no_feedback", "frozen")


def g53_attenuate(before, candidate, variant):
    """Scale only one weight-group update by 0.5; leave other deltas untouched.

    The original model architecture, feedback decoder, and gradient budget
    remain fixed. This is a development-only training ablation.
    """
    if variant not in G53_INTERVENTIONS or type(variant) is not str:
        raise ValueError("YGG_G53_INVALID_ATTENUATION")
    if before.parameter_count != GENOME_PARAMETER_COUNT or (
            candidate.parameter_count != GENOME_PARAMETER_COUNT):
        raise ValueError("YGG_G53_CAPACITY_DRIFT")
    if variant == "sensory_half":
        first = list(candidate.first)
        for j in range(HIDDEN):
            ix = j * INPUTS + INPUTS - 1
            first[ix] = before.first[ix] + (candidate.first[ix] - before.first[ix]) * 0.5
        return SharedGenome(tuple(first), candidate.first_bias,
                            candidate.second, candidate.second_bias)
    second = tuple(a + (b - a) * 0.5 for a, b in
                   zip(before.second, candidate.second))
    return SharedGenome(candidate.first, candidate.first_bias,
                        second, candidate.second_bias)


def build_g53_report(baseline):
    """Frozen-budget training-level comparison; no protected transfer."""
    if any(arm not in baseline for arm in G53_CONTROL_ARMS):
        raise ValueError("YGG_G53_MISSING_CONTROLS")
    rows = []
    for arm in G53_CONTROL_ARMS:
        orig = baseline[arm]
        runs = (("full", orig),)
        if arm in ("matched", "antithetic"):
            runs += tuple((variant, run(arm, variant)) for variant in G53_INTERVENTIONS)
        for variant, result in runs:
            if (result["genome_parameters"] != GENOME_PARAMETER_COUNT or
                result["interactions"] != ROUNDS * len(CUES) or
                result["gradient_calls"] != ROUNDS * len(CUES) * GRADIENT_CALLS):
                raise ValueError("YGG_G53_BUDGET_DRIFT")
            rows.append({
                "arm": arm, "variant": variant,
                "interactions": result["interactions"],
                "feedback_frames": result["feedback_frames"],
                "gradient_calls": result["gradient_calls"],
                "genome_parameters": result["genome_parameters"],
                "checkpoints": [{
                    "rounds": cp["rounds"],
                    "source": cp["source"], "reversed": cp["reversed"],
                    "interpolation": cp["interpolation"],
                    "restored_equal": cp["restored_equal"],
                    "endpoint_slope": g50_boundary_from_checkpoint(diag)["endpoint_slope"],
                    "endpoint_intercept": g50_boundary_from_checkpoint(diag)["endpoint_intercept"],
                    "parameter_distance_from_start": diag["parameter_distance_from_start"]
                } for cp, diag in zip(result["checkpoints"], result["g49_diagnostics"])]
            })
    return {
        "schema": "yggdrasil.g53.synthetic-training-group-attenuation.v1",
        "evidence": "SELF_AUTHORED_SYNTHETIC_DEV_ONLY",
        "frozen_variants": list(G53_INTERVENTIONS),
        "attenuation_fraction": 0.5,
        "baseline_controls_reused_without_retraining": True,
        "matched_training_budgets": True,
        "fixed_engineered_feedback_decoder": True,
        "scientific_acceptance": "NO_GO",
        "genuine_transfer": "UNVERIFIED",
        "primary_execution_allowed": False,
        "rows": rows
    }


# G54 frozen development-only factorial; do not tune against these results.
G54_GRID = (-1.0, -0.75, -0.5, -0.25, -0.125,
            0.125, 0.25, 0.5, 0.75, 1.0)
G54_PROFILES = ((0, "mapped"), (4096, "mapped"),
                (0, "phase_shift"), (4096, "phase_shift"))
G54_VARIANTS = (("matched", "full"), ("matched", "sensory_half"),
                ("antithetic", "full"))


def g54_evaluate(model, genome):
    """Signed decision margins on predeclared unfamiliar evaluation cues."""
    points = []
    for cue in G54_GRID:
        signed_output = value(model, genome, cue)
        expected = -1 if cue > 0 else 1
        points.append({
            "cue": cue, "signed_output": round(signed_output, 12),
            "expected_reversed_action": expected,
            "chosen_action": action(model, genome, cue),
            "signed_reversed_margin": round(expected * signed_output, 12)
        })
    return {
        "correct": sum(int(p["chosen_action"] == p["expected_reversed_action"])
                       for p in points),
        "total": len(points),
        "small_magnitude_correct": sum(
            int(p["chosen_action"] == p["expected_reversed_action"])
            for p in points if abs(p["cue"]) <= 0.25),
        "small_magnitude_total": 4,
        "minimum_signed_margin": min(p["signed_reversed_margin"] for p in points),
        "points": points
    }


def build_g54_report(baseline):
    """Test fixed G53 attenuation across seed/waveform changes without retuning."""
    model = DG1APrototype()
    rows = []
    for offset, waveform in G54_PROFILES:
        for arm, attenuation in G54_VARIANTS:
            if offset == 0 and waveform == "mapped" and attenuation == "full":
                result = baseline[arm]
            else:
                result = run(arm, attenuation=attenuation,
                             seed_offset=offset, feedback_condition=waveform)
            if (result["interactions"] != ROUNDS * len(CUES) or
                    result["feedback_frames"] != ROUNDS * len(CUES) * FRAMES or
                    result["gradient_calls"] != ROUNDS * len(CUES) * GRADIENT_CALLS or
                    result["genome_parameters"] != GENOME_PARAMETER_COUNT):
                raise ValueError("YGG_G54_BUDGET_OR_ARCHITECTURE_DRIFT")
            row = {
                "training_arm": arm, "variant": attenuation,
                "waveform": waveform, "seed_offset": offset,
                "interactions": result["interactions"],
                "feedback_frames": result["feedback_frames"],
                "gradient_calls": result["gradient_calls"],
                "genome_parameters": result["genome_parameters"],
                "start": g54_evaluate(model, result["g51_genomes"][0]),
                "end": g54_evaluate(model, result["genome"]),
                "checkpoint_reversed": [c["reversed"] for c in result["checkpoints"]]
            }
            rows.append(row)
    return {
        "schema": "yggdrasil.g54.synthetic-fixed-attenuation-factorial.v1",
        "evidence": "SELF_AUTHORED_SYNTHETIC_DEV_ONLY",
        "predeclared_seed_offsets": [0, 4096],
        "predeclared_waveform_profiles": ["mapped", "phase_shift"],
        "predeclared_cue_grid": list(G54_GRID),
        "attenuation_fraction": 0.5,
        "trained_profile_count": len(G54_PROFILES),
        "control_arms": ["matched_full", "antithetic_full",
                         "no_feedback_g53", "frozen_g53"],
        "no_feedback_and_frozen_reuse_G53": True,
        "architecture_unchanged": True,
        "training_budget_unchanged": True,
        "scientific_acceptance": "NO_GO",
        "genuine_transfer": "UNVERIFIED",
        "primary_execution_allowed": False,
        "rows": rows
    }


class G48NativeFeedbackDiagnostics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = {arm: run(arm) for arm in ARMS}

    def test_budgets_and_capacity(self):
        for arm, row in self.results.items():
            with self.subTest(arm=arm):
                self.assertEqual(row["interactions"], ROUNDS * len(CUES))
                self.assertEqual(row["feedback_frames"],
                                 ROUNDS * len(CUES) * FRAMES)
                self.assertEqual(row["gradient_calls"],
                                 ROUNDS * len(CUES) * GRADIENT_CALLS)
                self.assertEqual(row["genome_parameters"],
                                 GENOME_PARAMETER_COUNT)

    def test_checkpoint_roundtrip_and_frozen_control(self):
        source = run_development("mapped").genome
        self.assertEqual(self.results["frozen"]["genome"], source)
        self.assertEqual(self.results["no_feedback"]["genome"], source)
        for arm, row in self.results.items():
            with self.subTest(arm=arm):
                self.assertEqual(tuple(x["rounds"] for x in row["checkpoints"]),
                                 CHECKPOINTS)
                self.assertTrue(all(x["restored_equal"]
                                    for x in row["checkpoints"]))
                self.assertEqual(row["checkpoints"][0]["source"], 1.0)
                for x in row["checkpoints"]:
                    self.assertEqual(x["source"] + x["reversed"], 1.0)

    def test_report_does_not_assert_positive_learning(self):
        report = build_report()
        self.assertEqual(report["scientific_acceptance"], "NO_GO")
        self.assertEqual(report["genuine_transfer"], "UNVERIFIED")
        self.assertEqual([r["arm"] for r in report["rows"]], list(ARMS))
        self.assertEqual(json.loads(json.dumps(report)), report)
        print("YGG_G48_DEV_FEEDBACK_JSON=" + json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False), flush=True)

    def test_g49_per_cue_margin_and_interference_receipt(self):
        report = build_g49_report()
        self.assertEqual(report["scientific_acceptance"], "NO_GO")
        self.assertEqual(len(report["rows"]), len(ARMS))
        for row in report["rows"]:
            self.assertEqual(len(row["checkpoints"]), len(CHECKPOINTS))
            for checkpoint in row["checkpoints"]:
                self.assertEqual(len(checkpoint["per_cue"]), 6)
                self.assertGreaterEqual(checkpoint["parameter_distance_from_start"], 0)
        for row in report["rows"]:
            if row["arm"] in ("frozen", "no_feedback"):
                self.assertTrue(all(c["parameter_distance_from_start"] == 0
                                    for c in row["checkpoints"]))
        print("YGG_G49_DEV_CUE_DIAGNOSTIC_JSON=" +
              json.dumps(report, sort_keys=True, separators=(",", ":"),
                         allow_nan=False), flush=True)

    def test_g50_boundary_instrumentation(self):
        report = build_g50_report(self.results)
        self.assertEqual(report["scientific_acceptance"], "NO_GO")
        self.assertEqual([r["arm"] for r in report["rows"]], list(ARMS))
        for r in report["rows"]:
            self.assertEqual(len(r["checkpoints"]), len(CHECKPOINTS))
            for c in r["checkpoints"]:
                self.assertIsInstance(c["endpoint_slope"], float)
                self.assertIsInstance(c["endpoint_intercept"], float)
                self.assertEqual(len(c["observed_bracketed_crossings"]) <= 5, True)
        matched = report["rows"][0]["checkpoints"]
        self.assertEqual(matched[0]["rounds"], 0)
        self.assertFalse(matched[0]["all_negative"])
        self.assertTrue(matched[-1]["all_negative"])
        self.assertEqual(matched[-1]["observed_bracketed_crossings"], [])
        for r in report["rows"][2:]:
            self.assertTrue(all(c["parameter_distance_from_start"] == 0
                                for c in r["checkpoints"]))
        print("YGG_G50_DEV_BOUNDARY_JSON=" +
              json.dumps(report, sort_keys=True, separators=(",", ":"),
                         allow_nan=False), flush=True)

    def test_g51_counterfactual_update_attribution(self):
        report = build_g51_report(self.results)
        self.assertEqual(report["scientific_acceptance"], "NO_GO")
        self.assertFalse(report["probe_updates_committed_to_learner"])
        self.assertEqual(report["probe_gradient_calls"], 48)
        self.assertEqual(len(report["rows"]), 48)
        for row in report["rows"]:
            self.assertEqual(sum(v["parameters"] for v in row["parameter_groups"].values()),
                             GENOME_PARAMETER_COUNT)
            self.assertIn(row["decoded_valence"], (-1, 0, 1))
            if row["rounds"] in (0, 4, 8):
                self.assertTrue(row["exploration_applied"])
                self.assertFalse(row["post_training_probe"])
                self.assertEqual(row["chosen_action"], -row["policy_action"])
            else:
                self.assertEqual(row["rounds"], 16)
                self.assertFalse(row["exploration_applied"])
                self.assertTrue(row["post_training_probe"])
                self.assertEqual(row["chosen_action"], row["policy_action"])
            if row["feedback"] == "no_feedback":
                self.assertTrue(all(v["l2_change"] < 1e-12
                                    for v in row["parameter_groups"].values()))
        self.assertEqual(self.results["matched"]["genome"],
                         run("matched")["genome"])
        print("YGG_G51_DEV_ATTRIBUTION_JSON=" +
              json.dumps(report, sort_keys=True, separators=(",", ":"),
                         allow_nan=False), flush=True)

    def test_g52_group_delta_reversal_at_frozen_checkpoints(self):
        report = build_g52_report(self.results)
        self.assertEqual(report["scientific_acceptance"], "NO_GO")
        self.assertFalse(report["probe_updates_committed_to_learner"])
        self.assertEqual(report["diagnostic_gradient_calls"], 32)
        self.assertEqual(len(report["rows"]), 32 * len(G52_ARMS))
        for i in range(0, len(report["rows"]), len(G52_ARMS)):
            trial = report["rows"][i:i + len(G52_ARMS)]
            self.assertEqual([r["arm"] for r in trial], list(G52_ARMS))
            self.assertTrue(all(r["genome_parameters"] == GENOME_PARAMETER_COUNT
                                for r in trial))
            no_update = trial[-1]
            self.assertEqual(no_update["delta_slope"], 0)
            self.assertEqual(no_update["delta_intercept"], 0)
            self.assertEqual(no_update["delta_negative"], 0)
            self.assertEqual(no_update["delta_positive"], 0)
            self.assertTrue(all(trial[0]["trained_arm"] == r["trained_arm"] and
                                trial[0]["rounds"] == r["rounds"] and
                                trial[0]["feedback"] == r["feedback"] and
                                trial[0]["training_cue"] == r["training_cue"]
                                for r in trial))
        print("YGG_G52_DEV_GROUP_DELTA_JSON=" + json.dumps(
            report, sort_keys=True, separators=(",", ":"), allow_nan=False),
            flush=True)

    def test_g53_frozen_training_group_attenuation(self):
        model = DG1APrototype()
        before = self.results["matched"]["g51_genomes"][0]
        candidate = model.fit_one_cell(model.initial_state(), sensory(-1.0),
                                       before, 1, 1, -MARGIN,
                                       learning_rate=0.5)
        for variant in G53_INTERVENTIONS:
            changed = g53_attenuate(before, candidate, variant)
            self.assertEqual(changed.parameter_count, GENOME_PARAMETER_COUNT)
            self.assertNotEqual(changed, before)
            self.assertNotEqual(changed, candidate)
            if variant == "sensory_half":
                self.assertEqual(changed.second, candidate.second)
                self.assertEqual(changed.first_bias, candidate.first_bias)
                self.assertEqual(changed.second_bias, candidate.second_bias)
                for j in range(HIDDEN):
                    i = j * INPUTS + INPUTS - 1
                    self.assertAlmostEqual(
                        changed.first[i] - before.first[i],
                        (candidate.first[i] - before.first[i]) * 0.5,
                        places=14)
            else:
                self.assertEqual(changed.first, candidate.first)
                self.assertEqual(changed.first_bias, candidate.first_bias)
                self.assertEqual(changed.second_bias, candidate.second_bias)
                for a, b, c in zip(before.second, candidate.second, changed.second):
                    self.assertAlmostEqual(c - a, 0.5 * (b - a), places=14)
        with self.assertRaises(ValueError):
            g53_attenuate(before, candidate, "invalid")
        report = build_g53_report(self.results)
        self.assertEqual(len(report["rows"]), 8)
        self.assertEqual(report["scientific_acceptance"], "NO_GO")
        for row in report["rows"]:
            self.assertEqual(row["genome_parameters"], GENOME_PARAMETER_COUNT)
            self.assertEqual(row["gradient_calls"], ROUNDS * len(CUES) * GRADIENT_CALLS)
            self.assertEqual(len(row["checkpoints"]), len(CHECKPOINTS))
            self.assertEqual([c["rounds"] for c in row["checkpoints"]], list(CHECKPOINTS))
            self.assertTrue(all(c["restored_equal"] for c in row["checkpoints"]))
        self.assertEqual(
            [(r["arm"], r["variant"]) for r in report["rows"]],
            [("matched", "full"), ("matched", "sensory_half"),
             ("matched", "second_half"),
             ("antithetic", "full"), ("antithetic", "sensory_half"),
             ("antithetic", "second_half"), ("no_feedback", "full"),
             ("frozen", "full")])
        self.assertEqual(report["rows"][-1]["checkpoints"],
                         report["rows"][-2]["checkpoints"])
        print("YGG_G53_DEV_TRAINING_ATTENUATION_JSON=" + json.dumps(
            report, sort_keys=True, separators=(",", ":"), allow_nan=False),
            flush=True)

    def test_g54_fixed_robustness_factorial(self):
        for kw in ({"seed_offset": -1},
                   {"seed_offset": 123},
                   {"feedback_condition": "protected"},
                   {"feedback_condition": "sham"}):
            with self.assertRaises(ValueError):
                run("matched", **kw)
        report = build_g54_report(self.results)
        self.assertEqual(report["scientific_acceptance"], "NO_GO")
        self.assertEqual(len(report["rows"]), 12)
        self.assertEqual(report["attenuation_fraction"], 0.5)
        for profile in G54_PROFILES:
            sub = [r for r in report["rows"] if
                   (r["seed_offset"], r["waveform"]) == profile]
            self.assertEqual(len(sub), 3)
            self.assertEqual([(r["training_arm"], r["variant"]) for r in sub],
                             list(G54_VARIANTS))
            for row in sub:
                self.assertEqual(row["genome_parameters"], GENOME_PARAMETER_COUNT)
                self.assertEqual(row["gradient_calls"],
                                 ROUNDS * len(CUES) * GRADIENT_CALLS)
                self.assertEqual(row["end"]["total"], len(G54_GRID))
                self.assertEqual(row["end"]["small_magnitude_total"], 4)
                self.assertEqual(len(row["end"]["points"]), len(G54_GRID))
                self.assertEqual(row["start"]["points"],
                                 report["rows"][0]["start"]["points"])
                self.assertEqual(len(row["checkpoint_reversed"]), len(CHECKPOINTS))
                for point in row["end"]["points"]:
                    self.assertEqual(point["expected_reversed_action"],
                                     -1 if point["cue"] > 0 else 1)
        self.assertEqual(report["rows"][0]["checkpoint_reversed"],
                         [c["reversed"] for c in self.results["matched"]["checkpoints"]])
        print("YGG_G54_DEV_FIXED_ROBUSTNESS_JSON=" + json.dumps(
            report, sort_keys=True, separators=(",", ":"), allow_nan=False),
            flush=True)

    def test_fail_closed(self):
        for invalid in (None, "", "protected", "heldout", 7):
            with self.assertRaises(ValueError):
                run(invalid)


if __name__ == "__main__":
    print("YGG_G48_DEV_FEEDBACK_JSON=" +
          json.dumps(build_report(), sort_keys=True,
                     separators=(",", ":"), allow_nan=False), flush=True)
    unittest.main()
