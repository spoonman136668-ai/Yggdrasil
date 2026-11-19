"""Archived JEPA2 native evidence-gated re-entry, strictly posthoc.

The active native learner evolves exactly as source-defined. A frozen copy of
the previously trained native context policy is a read-only *readout*, not a
second trainer or a canonical checkpoint. One predeclared scalar fixed-share
Bayesian weight uses ONLY preceding public action consequences to select a
probabilistically coherent transition/terminal forecast.

All environments and source outcomes were previously consumed. No source
generator, fresh episode, accepted state change, deployment or science pass.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from importlib.util import module_from_spec, spec_from_file_location
import json
from math import isfinite
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

HERE = Path(__file__).resolve().parent
S = spec_from_file_location(
    "jepa2_archival_native", HERE.parent /
    "YGG-JEPA2-05-RESET-POSTHOC" / "diagnose.py")
D = module_from_spec(S)
S.loader.exec_module(D)

PARENT_SHA = "594c553d2d6033598d37859d81b9ee25481ec4c6"
PREREG_SHA = "4e6768cca5b5c9d998e9ef0ccda316a66827933b"
WEIGHT_INITIAL = 0.5
FIXED_SHARE_ALPHA = 1.0 / 8.0
PROBE_COUNT = 32


def check(condition, label):
    D.check(condition, "REENTRY_" + label)


def forecast(native, event):
    """Evaluate outcome-free transition and observed-transition-conditional terminal."""
    _, views, first, next_state, second, reward = event
    view = views[0]
    t = float(native.context_forecast(view, first))
    r = float(native.context_forecast(view, first, next_state, second))
    check(all(isfinite(p) and 0 <= p <= 1 for p in (t, r)), "EXPERT_PROBABILITY")
    return t, r


def mix(old_forecast, active_forecast, weight_old, observed_next_state):
    """Mixture of JOINT action-consequence laws, then condition terminal on s2.

    The observed transition may be used for terminal readout, but reward and
    transition outcomes never affect the *pre-transition* gate prior.
    """
    ot, orw = old_forecast
    at, arw = active_forecast
    check(0.0 <= weight_old <= 1.0, "WEIGHT_BOUND")
    transition = weight_old * ot + (1.0 - weight_old) * at
    old_tlike = ot if observed_next_state else (1.0 - ot)
    active_tlike = at if observed_next_state else (1.0 - at)
    evidence_transition = (
        weight_old * old_tlike +
        (1.0 - weight_old) * active_tlike)
    check(evidence_transition > 0, "TRANSITION_MIX_SUPPORT")
    posterior_old_given_transition = (
        weight_old * old_tlike / evidence_transition)
    conditional_reward = (
        posterior_old_given_transition * orw +
        (1.0 - posterior_old_given_transition) * arw)
    check(all(isfinite(p) and 0 <= p <= 1
              for p in (transition, conditional_reward)),
          "MIXED_PROBABILITY")
    return transition, conditional_reward


def brier(pair, event):
    _, _, _, state, _, reward = event
    return ((pair[0] - state) ** 2 + (pair[1] - reward) ** 2) / 2.0


def next_weight(weight_old, old_prediction, live_prediction, event):
    """Fixed-share Bayesian posterior only AFTER the complete charged witness."""
    _, _, _, state, _, reward = event
    ot, orw = old_prediction
    at, arw = live_prediction
    old_likelihood = (ot if state else 1.0 - ot) * (
        orw if reward else 1.0 - orw)
    live_likelihood = (at if state else 1.0 - at) * (
        arw if reward else 1.0 - arw)
    joint_evidence = (
        weight_old * old_likelihood +
        (1.0 - weight_old) * live_likelihood)
    check(joint_evidence > 0, "JOINT_EVIDENCE_SUPPORT")
    posterior = weight_old * old_likelihood / joint_evidence
    shared = (
        (1.0 - 2.0 * FIXED_SHARE_ALPHA) * posterior +
        FIXED_SHARE_ALPHA)
    check(FIXED_SHARE_ALPHA <= shared <= 1.0-FIXED_SHARE_ALPHA,
          "WEIGHT_SHARE_BOUND")
    return shared


def phase(index):
    if index < 6:
        return "A_initial"
    if index < 11:
        return "B_change"
    return "A_return"


def score_old_probes(anchor, live, probes, weight):
    totals = {name: 0.0 for name in ("active", "anchor", "constant_half", "fixed_share")}
    for event in probes:
        old_pair = forecast(anchor, event)
        live_pair = forecast(live, event)
        constant = mix(old_pair, live_pair, 0.5, event[3])
        gated = mix(old_pair, live_pair, weight, event[3])
        values = {
            "active": live_pair, "anchor": old_pair,
            "constant_half": constant, "fixed_share": gated}
        for name, pair in values.items():
            totals[name] += brier(pair, event)
    return {name: value / len(probes) for name, value in totals.items()}


def run_seed(seed, platform, archived):
    began = time.process_time()
    original_six_head = D.load_original(seed)
    continued_six_head, final_pin = D.load_continued(seed, platform)
    original = original_six_head.original.base.native
    final = continued_six_head.original.base.native
    original_raw = original.checkpoint()
    check(digest(original_raw) == archived["original_native_sha256"],
          "ORIGINAL_NATIVE_PIN")
    initial_len = len(original._ledger)
    later = final._ledger
    check(later[:initial_len] == original._ledger, "ACCEPTED_PREFIX")
    check(len(later) - initial_len == 16, "OBSERVED_SUFFIX_16")
    probes = original._ledger[-PROBE_COUNT:]
    check(abs(D.native_score(original, probes) -
              archived["historic_readonly_native_before"]) <=
          D.MAX_ABS_REPRODUCTION_ERROR, "ORIGINAL_BRIER")

    # Never mutate anchor: it is not a second trained learner.
    anchor = NativeEpisodeExperience.restore(original_raw, digest(original_raw))
    active = NativeEpisodeExperience.restore(original_raw, digest(original_raw))
    sham = NativeEpisodeExperience.restore(original_raw, digest(original_raw))
    weight = WEIGHT_INITIAL
    aggregate = defaultdict(list)
    phase_detail = defaultdict(lambda: defaultdict(list))
    ledger = []
    for ordinal, event in enumerate(later[initial_len:], 1):
        check(active.checkpoint() == sham.checkpoint(),
              "SHAM_PRE_STEP_" + str(ordinal))
        old_pair = forecast(anchor, event)
        live_pair = forecast(active, event)
        fixed_pair = mix(old_pair, live_pair, 0.5, event[3])
        gated_pair = mix(old_pair, live_pair, weight, event[3])
        values = {
            "active": live_pair,
            "anchor": old_pair,
            "constant_half": fixed_pair,
            "fixed_share": gated_pair}
        label = phase(ordinal - 1)
        scores = {name: brier(pair, event)
                  for name, pair in values.items()}
        for name, v in scores.items():
            aggregate[name].append(v)
            phase_detail[label][name].append(v)
        before_weight = weight
        # The event is charged AFTER all 4 arms have given their predictions.
        weight = next_weight(weight, old_pair, live_pair, event)
        ledger.append({
            "ordinal": ordinal, "phase_for_audit_only": label,
            "old_weight_before_outcome": before_weight,
            "old_weight_after_outcome": weight,
            "prequential_brier": scores,
        })
        identifier, views, first, next_state, second, reward = event
        row = {"s1": views[0][0], "x1": first,
               "s2": next_state, "x2": second, "y": reward}
        active = active.observe(identifier, views, row)
        sham = sham.observe(identifier, views, row)
        check(active.checkpoint() == sham.checkpoint(),
              "SHAM_POST_STEP_" + str(ordinal))
        check(active._ledger == later[:initial_len + ordinal],
              "EXACT_EVENT_REPLAY_" + str(ordinal))
    check(active.checkpoint() == final.checkpoint(),
          "AUTHENTIC_FINAL_NATIVE_CHECKPOINT")
    check(anchor.checkpoint() == original_raw, "FROZEN_OLD_CONTEXT_MUTATED")
    check(abs(D.native_score(active, probes) -
              archived["historic_readonly_native_after"]) <=
          D.MAX_ABS_REPRODUCTION_ERROR, "PUBLISHED_FINAL_BRIER")
    summaries = {
        name: sum(series) / len(series)
        for name, series in aggregate.items()}
    by_phase = {
        label: {
            name: sum(phase_detail[label][name]) /
                  len(phase_detail[label][name])
            for name in aggregate}
        for label in ("A_initial", "B_change", "A_return")
    }
    final_old = score_old_probes(anchor, active, probes, weight)
    check(abs(final_old["anchor"] -
              archived["historic_readonly_native_before"]) <=
          D.MAX_ABS_REPRODUCTION_ERROR, "ANCHOR_READOUT_IDENTITY")
    check(abs(final_old["active"] -
              archived["historic_readonly_native_after"]) <=
          D.MAX_ABS_REPRODUCTION_ERROR, "ACTIVE_READOUT_IDENTITY")
    check(len(ledger) == 16 and len(set(e["ordinal"] for e in ledger)) == 16,
          "PREQUENTIAL_ACCOUNTING")
    return {
        "seed": archived["seed"], "old_seed": seed,
        "original_model_sha256": D.OLD_PIN[seed],
        "authentic_final_model_sha256": final_pin,
        "original_native_sha256": digest(original_raw),
        "final_native_sha256": digest(active.checkpoint()),
        "old_weight_after_16": weight,
        "prequential_16_brier": summaries,
        "by_phase_brier": by_phase,
        "final_old_32_probe_brier": final_old,
        "old_retention_limit": archived["historic_readonly_native_before"] + 0.03,
        "gate_minus_adaptive_prequential":
            summaries["fixed_share"] - summaries["active"],
        "gate_minus_constant_half_prequential":
            summaries["fixed_share"] - summaries["constant_half"],
        "step_details": ledger,
        "source_actions": 0,
        "process_cpu_seconds": time.process_time() - began,
        "scientific_pass": False,
    }


def classify(records):
    # Strict frozen posthoc feasibility diagnostic; not a science/admission pass.
    passes = [
        r["final_old_32_probe_brier"]["fixed_share"] <= r["old_retention_limit"]
        and r["gate_minus_adaptive_prequential"] <= 0.005
        for r in records]
    behind_both = all(
        r["gate_minus_constant_half_prequential"] >= 0
        for r in records)
    if all(passes):
        return "ARCHIVED_DIAGNOSTIC_PROMISING_NOT_SCIENCE"
    if behind_both:
        return "ARCHIVED_NEGATIVE"
    return "ARCHIVED_MIXED_OR_NEGATIVE"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=("linux", "windows"),
                        required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    D.audited_archive(args.platform)
    history = json.loads((D.JEPA / "result.json").read_bytes())
    check(history["development_go"] is False
          and history["science_pass"] is False, "CONSUMED_DEV_NO_GO")
    replicas = {row["old_seed"]: row for row in history["replicas"]}
    check(set(replicas) == set(D.OLD_PIN), "EXACT_ORIGINAL_SEED_SET")
    out = {
        "schema": "yggdrasil.jepa2-05.evidence-reentry-posthoc.v1",
        "source_parent_sha": PARENT_SHA,
        "preregistered_posthoc_sha": PREREG_SHA,
        "platform": args.platform,
        "source_actions": 0,
        "source_first_use": False,
        "native_model_modified": False,
        "scientific_pass": False,
        "deployment": "NONE",
        "research_status": "UNPREREGISTERED_POSTHOC",
        "fixed_prior_old_weight": WEIGHT_INITIAL,
        "fixed_share_alpha": FIXED_SHARE_ALPHA,
        "results": [],
    }
    try:
        for seed in D.OLD_PIN:
            out["results"].append(run_seed(
                seed, args.platform, replicas[seed]))
        out["verdict"] = classify(out["results"])
        out["status"] = "ARCHIVAL_REENTRY_REPLAY_PASS"
    except Exception as exc:
        out["status"] = "REPRODUCTION_FAIL"
        out["error"] = str(exc)
        raise
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canonical(out))
        print(json.dumps(out, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
