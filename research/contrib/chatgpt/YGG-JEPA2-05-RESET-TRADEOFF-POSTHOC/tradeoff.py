"""Posthoc native retention-vs-adaptation ablation; consumed witnesses only.

No source-generator invocation, fresh experiment, owner data mutation,
promotion, controller, second official learner or new model parameters.
The no-reset arm is a temporary diagnostic clone. All forecasts prequential.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "YGG-JEPA2-05-RESET-POSTHOC"
SPEC = spec_from_file_location("jepa2_archived_reset", PARENT / "diagnose.py")
D = module_from_spec(SPEC)
SPEC.loader.exec_module(D)

PREREG_PARENT = "acb7df218d0e41415187041e725904173a9eec10"
FROZEN_PARENT = "6cef0688a2c70cee2c60f38a2774f83661c7e3ef"
FULL_SOURCE_PARENT = "7b0d9fd8c16b8e0433a632666cec88d8d008c19f"
EXPECTED_POSTRESET_COUNT = {14071: 5, 14072: 11}


def check(cond, marker):
    D.check(cond, "TRADEOFF_" + marker)


def loss(native, event):
    """Prequential public transition and conditional reward Brier, two outcomes."""
    _, views, first, nxt, second, reward = event
    view = views[0]
    transition = float(native.context_forecast(view, first))
    terminal = float(native.context_forecast(view, first, nxt, second))
    return ((transition - nxt) ** 2 + (terminal - reward) ** 2) / 2


def phase(index_zero_based):
    if index_zero_based < 6:
        return "A_initial"
    if index_zero_based < 11:
        return "B_change"
    return "A_return"


def receive(model, event):
    identity, views, first, nxt, second, reward = event
    return model.observe(identity, views, {
        "s1": views[0][0], "x1": first,
        "s2": nxt, "x2": second, "y": reward,
    })


def run_seed(seed, platform, replica):
    began = time.process_time()
    original_full = D.load_original(seed)
    final_full, final_sha = D.load_continued(seed, platform)
    original = original_full.original.base.native
    final = final_full.original.base.native
    old_rows = original._ledger
    later = final._ledger
    count = len(old_rows)
    check(later[:count] == old_rows, "PREFIX")
    check(len(later) - count == 16, "SUFFIX")
    probes = old_rows[-D.PROBE_COUNT:]
    check(abs(D.native_score(original, probes) -
              replica["historic_readonly_native_before"]) <
          D.MAX_ABS_REPRODUCTION_ERROR, "ORIGINAL_OLD_BRIER")

    actual = NativeEpisodeExperience.restore(
        original.checkpoint(), digest(original.checkpoint()))
    sham = NativeEpisodeExperience.restore(
        original.checkpoint(), digest(original.checkpoint()))
    shadow = None
    reset_at = D.EXPECTED_CONTEXT_RESET[seed]
    actual_resets = []
    shadow_resets = []
    by_phase = defaultdict(lambda: {"count": 0, "actual": [], "no_reset": []})
    every_new = []

    for ordinal, event in enumerate(later[count:], 1):
        before = actual
        check(actual.checkpoint() == sham.checkpoint(),
              "SHAM_MATCH_PRE_" + str(ordinal))
        if shadow is not None:
            # Both forecasts made before the target is learned by either arm.
            key = phase(ordinal - 1)
            actual_loss = loss(actual, event)
            shadow_loss = loss(shadow, event)
            pair = by_phase[key]
            pair["count"] += 1
            pair["actual"].append(actual_loss)
            pair["no_reset"].append(shadow_loss)
            every_new.append({
                "witness_ordinal": ordinal,
                "phase": key,
                "actual_brier": actual_loss,
                "no_reset_brier": shadow_loss,
            })

        actual = receive(actual, event)
        sham = receive(sham, event)
        check(actual.checkpoint() == sham.checkpoint(),
              "SHAM_MATCH_POST_" + str(ordinal))
        if actual._context_start != before._context_start:
            actual_resets.append(ordinal)

        if ordinal == reset_at:
            check(before._context_start != actual._context_start,
                  "EXPECTED_RESET_NOT_FIRED")
            check(shadow is None, "EARLY_SHADOW")
            # Same event, same pre-reset model and observed information;
            # skip only the context-repartition/reprioritization step.
            shadow = before._clone()
            shadow._append(event)
            shadow._update_context(event)
            check(shadow._ledger == actual._ledger,
                  "RESET_SUPPRESSION_SOURCE_PARITY")
            check(shadow._context_start == before._context_start,
                  "RESET_SUPPRESSION_OLD_CONTEXT")
        elif shadow is not None:
            previous_start = shadow._context_start
            shadow = receive(shadow, event)
            if shadow._context_start != previous_start:
                shadow_resets.append(ordinal)
        check(actual._ledger == later[:count+ordinal],
              "ACTUAL_WITNESSED_SUFFIX_" + str(ordinal))
        if shadow is not None:
            check(shadow._ledger == later[:count+ordinal],
                  "SHADOW_WITNESSED_SUFFIX_" + str(ordinal))

    check(actual.checkpoint() == final.checkpoint(), "AUTHENTIC_FINAL_NATIVE")
    check(actual_resets == [reset_at], "EXACT_ONE_ARCHIVED_RESET")
    check(len(every_new) == EXPECTED_POSTRESET_COUNT[seed],
          "EXACT_POSTRESET_COUNT")
    end_old_actual = D.native_score(actual, probes)
    end_old_shadow = D.native_score(shadow, probes)
    check(abs(end_old_actual -
              replica["historic_readonly_native_after"]) <
          D.MAX_ABS_REPRODUCTION_ERROR, "PUBLISHED_FINAL_READOUT")
    check(abs(end_old_actual -
              D.native_score(final, probes)) <
          D.MAX_ABS_REPRODUCTION_ERROR, "RESTORED_FINAL_READOUT")

    phases = {}
    for label in ("A_initial", "B_change", "A_return"):
        values = by_phase.get(label)
        if values is None:
            phases[label] = {"count": 0, "actual_brier": None,
                             "no_reset_brier": None, "no_reset_minus_actual": None}
        else:
            n = values["count"]
            a = sum(values["actual"]) / n
            s = sum(values["no_reset"]) / n
            phases[label] = {"count": n, "actual_brier": a,
                             "no_reset_brier": s, "no_reset_minus_actual": s - a}

    n = len(every_new)
    actual_new = sum(r["actual_brier"] for r in every_new) / n
    shadow_new = sum(r["no_reset_brier"] for r in every_new) / n
    return {
        "original_seed": seed,
        "new_development_seed": replica["seed"],
        "original_model_sha256": D.OLD_PIN[seed],
        "archived_continued_model_sha256": final_sha,
        "original_native_sha256": digest(original.checkpoint()),
        "authentic_final_native_sha256": digest(actual.checkpoint()),
        "shadow_final_native_sha256": digest(shadow.checkpoint()),
        "observed_suffix_count": 16,
        "postreset_count": n,
        "actual_reset_ordinals": actual_resets,
        "shadow_later_reset_ordinals": shadow_resets,
        "postreset_prequential_actual_brier": actual_new,
        "postreset_prequential_no_reset_brier": shadow_new,
        "prequential_no_reset_minus_actual": shadow_new - actual_new,
        "original_old_brier": D.native_score(original, probes),
        "final_old_brier_actual": end_old_actual,
        "final_old_brier_no_reset": end_old_shadow,
        "final_old_brier_no_reset_minus_actual": end_old_shadow - end_old_actual,
        "phases": phases,
        "prequential_ledger": every_new,
        "process_cpu_seconds": time.process_time() - began,
        "archived_reproduction_pass": True,
        "scientific_pass": False,
        "source_actions": 0,
    }


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--platform", choices=("linux", "windows"), required=True)
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    D.audited_archive(args.platform)
    original_results = json.loads((D.JEPA / "result.json").read_bytes())
    check(original_results["development_go"] is False and
          original_results["science_pass"] is False, "FROZEN_DEVELOPMENT_STATUS")
    replicas = {x["old_seed"]: x for x in original_results["replicas"]}
    check(set(replicas) == set(D.OLD_PIN), "REPLICAS")
    out = {
        "schema": "yggdrasil.jepa2-05.reset-tradeoff-posthoc.v1",
        "qualified_source_parent": FULL_SOURCE_PARENT,
        "exact_isolated_research_parent": FROZEN_PARENT,
        "posthoc_protocol_parent_sha": PREREG_PARENT,
        "platform": args.platform,
        "classification": "UNPREREGISTERED_POSTHOC",
        "scientific_pass": False,
        "accepted_native": False,
        "source_first_use": False,
        "source_actions": 0,
        "deployment": "NONE",
        "records": [],
    }
    try:
        for seed in D.OLD_PIN:
            out["records"].append(run_seed(seed, args.platform, replicas[seed]))
        out["status"] = "ARCHIVAL_TRADEOFF_REPLAY_PASS"
    except Exception as exc:
        out["status"] = "REPRODUCTION_FAIL"
        out["error"] = str(exc)
        raise
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canonical(out))
        print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
