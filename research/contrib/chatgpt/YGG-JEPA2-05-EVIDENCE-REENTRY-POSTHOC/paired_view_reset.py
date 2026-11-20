"""Archived current-event paired-view perturbation: mechanism diagnostic, NOT science.

For each already-witnessed JEPA2-05 episode, hold the pinned pre-event native
learner, first public view, actions and observed consequences *exactly fixed*.
Flip ONLY the second view's selected projected coordinate in a disposable
copy of that one event. Compare source-exact immediate stream score/reset.

The modified pair violates the original synthetic public-state continuity;
therefore this is a *white-box functional counterfactual* and not a valid
new source event or independent causal-world scientific experiment.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import canonical, digest

HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location(
    "jepa2_pinned_native_archive",
    HERE.parent / "YGG-JEPA2-05-RESET-POSTHOC" / "diagnose.py")
D = module_from_spec(SPEC)
SPEC.loader.exec_module(D)


def check(condition, mark):
    D.check(condition, "PAIR_FLIP_" + mark)


def event_row(event):
    _, views, x1, s2, x2, y = event
    return {"s1": views[0][0], "x1": x1, "s2": s2, "x2": x2, "y": y}


def detector_likelihood(pre, event):
    """Copy exactly the pre-update score in original NativeEpisodeExperience._accept."""
    _, views, first, state, second, reward = event
    check(pre._stream_start is not None, "STREAM_REQUIRED")
    a = pre.context_forecast(views[0], first)
    b = pre.context_forecast(views[0], first, state, second)
    p = (a if state else 1-a) * (b if reward else 1-b)
    check(p > 0, "STREAM_POSITIVE_PROB")
    return p


def altered_second_view(pre, event):
    name, views, x1, s2, x2, y = event
    coordinate = pre._projection
    check(coordinate in (0, 1), "PINNED_PROJECTION")
    second = list(views[1])
    second[coordinate] ^= 1
    new_views = (views[0], tuple(second))
    check(new_views != views and new_views[0] == views[0],
          "ONLY_SECOND_VIEW_CHANGED")
    check((views[0][coordinate] == views[1][coordinate]) !=
          (new_views[0][coordinate] == new_views[1][coordinate]),
          "ELIGIBILITY_TOGGLED")
    return (name, new_views, x1, s2, x2, y)


def run_seed(seed, platform, published):
    began = time.process_time()
    original = D.load_original(seed)
    final, final_sha = D.load_continued(seed, platform)
    state = original.original.base.native
    archived = final.original.base.native
    old_rows = state._ledger
    after = archived._ledger
    check(after[:len(old_rows)] == old_rows and
          len(after) == len(old_rows)+16, "PINNED_OBSERVATION_SUFFIX")
    probes = old_rows[-D.PROBE_COUNT:]
    check(abs(D.native_score(state, probes) -
              published["historic_readonly_native_before"]) <=
          D.MAX_ABS_REPRODUCTION_ERROR, "FROZEN_OLD_BRIER")
    stats = {
        "episodes_tested": 0, "initial_agreement": 0,
        "initial_disagreement": 0, "reset_actual": 0, "reset_flip": 0,
        "detector_joint_probability_exact_matches": 0,
        "immediate_score_exact_matches": 0, "detection_receipt_exact_matches": 0,
        "different_disposable_final_state": 0,
    }
    receipts = []
    for number, event in enumerate(after[len(old_rows):], 1):
        check(state._projection == 0, "ORIGINAL_PROJECTION")
        alternate = altered_second_view(state, event)
        p_a = detector_likelihood(state, event)
        p_b = detector_likelihood(state, alternate)
        check(p_a == p_b, "CURRENT_SECOND_VIEW_SCORE_INVARIANCE_" + str(number))
        pre_score = state._stream_score
        next_score_a = max(Fraction(1), pre_score / (4*p_a))
        next_score_b = max(Fraction(1), pre_score / (4*p_b))
        check(next_score_a == next_score_b, "DETECTOR_SCORE_IDENTITY_" + str(number))
        check(state._ledger == after[:len(old_rows)+number-1],
              "BASE_PRE_EVENT_" + str(number))
        actual = state.observe(event[0], event[1], event_row(event))
        flipped = state.observe(alternate[0], alternate[1], event_row(alternate))
        reset_a = actual._context_start != state._context_start
        reset_b = flipped._context_start != state._context_start
        check(reset_a == reset_b, "RESET_DECISION_IDENTITY_" + str(number))
        check(actual._stream_detections == flipped._stream_detections,
              "RESET_RECEIPT_IDENTITY_" + str(number))
        check(actual._stream_score == flipped._stream_score,
              "ACTUAL_STREAM_SCORE_IDENTITY_" + str(number))
        check(actual._ledger[-1] == event and flipped._ledger[-1] == alternate,
              "ISOLATED_ONE_EVENT_CHANGE_" + str(number))
        check(actual.checkpoint() != flipped.checkpoint(),
              "TRAINING_SOURCE_DIFFERENCE_IS_REAL_" + str(number))
        original_agreed = event[1][0][0] == event[1][1][0]
        stats["episodes_tested"] += 1
        stats["initial_agreement" if original_agreed else "initial_disagreement"] += 1
        stats["reset_actual"] += int(reset_a)
        stats["reset_flip"] += int(reset_b)
        stats["detector_joint_probability_exact_matches"] += 1
        stats["immediate_score_exact_matches"] += 1
        stats["detection_receipt_exact_matches"] += 1
        stats["different_disposable_final_state"] += 1
        if reset_a or number in (1, 6, 7, 11, 12, 16):
            receipts.append({
                "new_witness_ordinal": number,
                "public_projection_agreed_before_flip": original_agreed,
                "pre_event_stream_score": [pre_score.numerator, pre_score.denominator],
                "unchanged_joint_outcome_likelihood": [p_a.numerator, p_a.denominator],
                "score_after_detectors_pre_reset": [next_score_a.numerator, next_score_a.denominator],
                "actual_context_reset": reset_a,
                "flipped_second_view_context_reset": reset_b,
                "actual_context_start": actual._context_start,
                "flipped_context_start": flipped._context_start,
                "actual_familiar_brier_after": D.native_score(actual, probes) if reset_a else None,
                "flipped_familiar_brier_after": D.native_score(flipped, probes) if reset_b else None,
            })
        state = actual

    check([v["new_witness_ordinal"] for v in receipts
           if v["actual_context_reset"]] == [D.EXPECTED_CONTEXT_RESET[seed]],
          "EXPECTED_AUTHENTIC_RESET")
    check(state.checkpoint() == archived.checkpoint(),
          "EXACT_AUTHENTIC_NATIVE_FINAL")
    check(abs(D.native_score(state, probes) -
              published["historic_readonly_native_after"]) <=
          D.MAX_ABS_REPRODUCTION_ERROR, "AUTHENTIC_FINAL_HISTORICAL_BRIER")
    check(stats["episodes_tested"] == 16 and
          stats["detector_joint_probability_exact_matches"] == 16 and
          stats["reset_actual"] == stats["reset_flip"] == 1,
          "ALL_SIXTEEN_DECISIONS_VERIFIED")
    return {
        "old_seed": seed,
        "development_seed": published["seed"],
        "source_exact_previous_native_sha256": published["original_native_sha256"],
        "archived_final_six_head_sha256": final_sha,
        "source_exact_final_native_sha256": digest(state.checkpoint()),
        "root_model_original_witnesses": len(old_rows),
        "source_suffix_observations": 16,
        "source_actions": 0,
        "stats": stats,
        "selected_event_receipts": receipts,
        "process_cpu_seconds": time.process_time() - began,
        "science_pass": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--platform", required=True, choices=("linux","windows"))
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    D.audited_archive(args.platform)
    results = json.loads((D.JEPA/"result.json").read_bytes())
    check(results["science_pass"] is False and
          results["development_go"] is False, "CONSUMED_DEV_NO_GO")
    records = {x["old_seed"]: x for x in results["replicas"]}
    check(set(records) == set(D.OLD_PIN), "SEED_SET")
    out = {
        "schema": "yggdrasil.jepa2-05.paired-view-current-event-flip-posthoc.v1",
        "platform": args.platform,
        "source_sha": "7b0d9fd8c16b8e0433a632666cec88d8d008c19f",
        "source_first_use": False,
        "source_actions": 0,
        "scientific_pass": False,
        "deployment": "NONE",
        "classification": "POSTHOC_WHITEBOX_DETECTOR_SENSITIVITY_ONLY",
        "source_valid_counterfactual": False,
        "results": [],
    }
    try:
        for seed in D.OLD_PIN:
            out["results"].append(run_seed(seed, args.platform, records[seed]))
        out["status"] = "ARCHIVAL_DETECTOR_INVARIANCE_PASS"
    except Exception as exc:
        out["status"] = "ARCHIVAL_DETECTOR_INVARIANCE_FAIL"
        out["failure"] = str(exc)
        raise
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canonical(out))
        print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
