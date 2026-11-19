"""Source-exact archival JEPA2-05 context-reset diagnostic, POSTHOC ONLY.

No new source, new cohorts, accepted checkpoints, timers, controllers or merges.
Reconstruct the consumed 16-event suffix on an isolated development clone.
Fail closed if original historical Brier or final original learned core differs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_jepa_future import NativeFutureStateLearner

HERE = Path(__file__).resolve().parent
HIST = HERE.parent / "YGG-RET01"
JEPA = HERE.parent / "YGG-JEPA2-05"
OLD_PIN = {
    14071: "c9bd78d4636d9b71e5bca42a3cf52afcfb9a58267d83c3e7727deceab667e690",
    14072: "724cc155863d2ac88265ddb3006a90702049ed54a53e52881939f063c002a31b",
}
EXPECTED_CONTEXT_RESET = {14071: 11, 14072: 5}
PROBE_COUNT = 32
MAX_ABS_REPRODUCTION_ERROR = 1e-10

SOURCE_BLOBS = {
    "yggdrasil/native_episode_experience.py":
        "94b7e033aff18080e65d48b479a7ae4bb3aba1c8",
    "yggdrasil/native_jepa_temporal.py":
        "4d3ac978e525f367daf5b80f7e29497b87c0faf7",
    "yggdrasil/native_jepa_future.py":
        "d5b557e2561428dcfb802b72a7cbba543f7b3db9",
    "research/contrib/chatgpt/YGG-RET01/seed-14071-state.json":
        "e2912ca930ad99ed23bfee4ce18d1e3945f6780a",
    "research/contrib/chatgpt/YGG-RET01/seed-14072-state.json":
        "3f076a393a15911769c0a40d37ccafc06dfaf2b7",
    "research/contrib/chatgpt/YGG-JEPA2-05/result.json":
        "3db6647b6eb89624e2ca4ff990b2c48cb95b5a4b",
}
CONTINUED_BLOBS = {
    "linux": {
        14071: "33b648ef36e381a2eb753094f930a4722570b448",
        14072: "5b9df452e45a1ebc3faadb265ceeffbc580ed7bf",
    },
    "windows": {
        14071: "57c89a43764b9a35cec24ef9133a606b4939292a",
        14072: "a753d9c3caa36e6983d1478693cf1db566d449c6",
    },
}


def check(truth, code):
    if not truth:
        raise ValueError("JEPA2_RESET_REPRODUCTION_FAIL_" + code)


def git_blob(path):
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD:" + path.as_posix()],
        cwd=ROOT, text=True, timeout=20).strip()


def audited_archive(platform):
    for relative, sha in SOURCE_BLOBS.items():
        check(git_blob(Path(relative)) == sha, "PIN_" + Path(relative).name)
    for seed, sha in CONTINUED_BLOBS[platform].items():
        path = Path("research/contrib/chatgpt/YGG-JEPA2-05/original") / platform / (
            "seed-%s-state.json" % seed)
        check(git_blob(path) == sha, "CONTINUED_BLOB_" + str(seed))


def native_score(native, original_rows):
    """Unchanged native_old() metric on exactly 32 original old-world rows."""
    check(len(original_rows) == PROBE_COUNT, "OLD_PROBES_COUNT")
    total = 0.0
    for _, views, a, state, b, outcome in original_rows:
        view = views[0]
        first = float(native.context_forecast(view, a))
        last = float(native.context_forecast(view, a, state, b))
        total += ((first - state) ** 2 + (last - outcome) ** 2) / 2
    return total / PROBE_COUNT


def load_original(seed):
    archive = json.loads((HIST / ("seed-%s-state.json" % seed)).read_bytes())
    reader_raw = archive["reader_ascii"].encode("ascii")
    check(digest(reader_raw) == archive["reader_sha256"], "READER_PIN")
    reader = json.loads(reader_raw)
    raw = reader["current_ascii"].encode("ascii")
    check(reader["current_sha256"] == OLD_PIN[seed]
          == archive["new_model_cold_sha256"], "OLD_MODEL_PIN")
    check(digest(raw) == OLD_PIN[seed], "OLD_BYTES_PIN")
    model = NativeFutureStateLearner.restore(raw, OLD_PIN[seed])
    check(model.checkpoint() == raw, "OLD_COLD_RESTORE")
    return model


def load_continued(seed, platform):
    path = JEPA / "original" / platform / ("seed-%s-state.json" % seed)
    archive = json.loads(path.read_bytes())
    raw = archive["model_ascii"].encode("ascii")
    check(archive["old_model_sha256"] == OLD_PIN[seed], "CONTINUED_OLD_PARENT")
    check(digest(raw) == archive["model_sha256"], "CONTINUED_STATE_PIN")
    final = NativeFutureStateLearner.restore(raw, archive["model_sha256"])
    check(final.checkpoint() == raw, "CONTINUED_COLD_RESTORE")
    return final, archive["model_sha256"]


def inspect(seed, platform, published):
    start = time.process_time()
    old = load_original(seed)
    final, final_sha = load_continued(seed, platform)
    begin_native = old.original.base.native
    continued_native = final.original.base.native
    old_events = begin_native._ledger
    final_events = continued_native._ledger
    check(final_events[:len(old_events)] == old_events,
          "ORIGINAL_EPISODE_PREFIX")
    check(len(final_events) == len(old_events) + 16,
          "CONSUMED_SUFFIX_COUNT")
    probes = old_events[-PROBE_COUNT:]
    measured_before = native_score(begin_native, probes)
    check(abs(measured_before -
              published["historic_readonly_native_before"]) <=
          MAX_ABS_REPRODUCTION_ERROR, "OLD_BRIER")
    check(digest(begin_native.checkpoint()) ==
          published["original_native_sha256"], "OLD_NATIVE_EXACT_HASH")
    future_head_frozen = canonical([
        old.sensory.checkpoint(), old.reward.checkpoint()])
    original_temporal_raw = old.original.checkpoint()
    resets = []
    for ordinal, event in enumerate(final_events[len(old_events):], 1):
        identifier, views, first, state, second, reward = event
        before = old.original.base.native
        before_brier = native_score(before, probes)
        row = {
            "s1": views[0][0], "x1": first, "s2": state,
            "x2": second, "y": reward,
        }
        old.observe_native(identifier, views, row)
        after = old.original.base.native
        check(after._ledger == final_events[:len(old_events)+ordinal],
              "ORDERED_WITNESS_SUFFIX_" + str(ordinal))
        if before._context_start != after._context_start:
            # Counterfactual: exact same witnessed next event, but do NOT
            # execute the subsequent detector-triggered _load_context reset.
            # This is a disposable DEV clone, never an accepted model state.
            without_reset = before._clone()
            without_reset._append(event)
            without_reset._update_context(event)
            check(without_reset._ledger == after._ledger,
                  "SHADOW_SHARED_WITNESS")
            check(without_reset._context_start == before._context_start,
                  "SHADOW_OLD_CONTEXT")
            shadow_brier = native_score(without_reset, probes)
            actual_brier = native_score(after, probes)
            resets.append({
                "new_witness_ordinal": ordinal,
                "old_context_start": before._context_start,
                "new_context_start": after._context_start,
                "old_brier_before_witness": before_brier,
                "same_update_no_reset_brier": shadow_brier,
                "actual_after_context_reset_brier": actual_brier,
                "ordinary_update_effect": shadow_brier - before_brier,
                "isolated_reset_effect": actual_brier - shadow_brier,
                "one_witness_total_effect": actual_brier - before_brier,
            })
    check(len(resets) == 1 and
          resets[0]["new_witness_ordinal"] == EXPECTED_CONTEXT_RESET[seed],
          "EXPECTED_CONTEXT_RESET")
    # Test exact authentic native + original four trained JEPA heads, excluding
    # the separately trained two future heads, from already consumed evidence.
    check(old.original.checkpoint() == final.original.checkpoint(),
          "FOUR_HEADS_AND_NATIVE_REPLAY")
    check(canonical([old.sensory.checkpoint(),
                     old.reward.checkpoint()]) == future_head_frozen,
          "UNUSED_TWO_FUTURE_HEADS_CHANGED")
    check(original_temporal_raw != old.original.checkpoint(),
          "NO_CUMULATIVE_PROGRESS")
    measured_after = native_score(old.original.base.native, probes)
    check(abs(measured_after -
              published["historic_readonly_native_after"]) <=
          MAX_ABS_REPRODUCTION_ERROR, "FINAL_BRIER")
    check(measured_after == native_score(continued_native, probes),
          "COLD_RESTORED_FINAL_READOUT")
    return {
        "old_seed": seed,
        "new_development_seed": published["seed"],
        "original_native_sha256":
            published["original_native_sha256"],
        "archived_final_model_sha256": final_sha,
        "old_witnesses": len(old_events),
        "continued_witnesses": len(final_events),
        "old_model_brier": measured_before,
        "published_old_model_brier":
            published["historic_readonly_native_before"],
        "after_model_brier": measured_after,
        "published_after_model_brier":
            published["historic_readonly_native_after"],
        "whole_continuation_old_brier_delta":
            measured_after - measured_before,
        "resets": resets,
        "source_actions": 0,
        "runtime_cpu_seconds": time.process_time() - start,
        "science_pass": False,
        "accepted_native": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=("linux", "windows"),
                        required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audited_archive(args.platform)
    results = json.loads((JEPA / "result.json").read_bytes())
    records = {d["old_seed"]: d for d in results["replicas"]}
    check(set(records) == set(OLD_PIN), "ORIGINAL_SEEDS")
    output = {
        "schema": "yggdrasil.jepa2-05.posthoc-reset-diagnostic.v1",
        "platform": args.platform,
        "exact_parent_sha": "7b0d9fd8c16b8e0433a632666cec88d8d008c19f",
        "research_classification": "UNPREREGISTERED_POSTHOC",
        "science_pass": False,
        "accepted_native": False,
        "source_first_use": False,
        "source_actions": 0,
        "deployment": "NONE",
        "seeds": [],
    }
    try:
        for seed in OLD_PIN:
            output["seeds"].append(inspect(seed, args.platform, records[seed]))
        output["status"] = "ARCHIVED_REPRODUCTION_PASS"
    except Exception as exc:
        output["status"] = "REPRODUCTION_FAIL"
        output["failure_reason"] = str(exc)
        raise
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canonical(output))
        print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
