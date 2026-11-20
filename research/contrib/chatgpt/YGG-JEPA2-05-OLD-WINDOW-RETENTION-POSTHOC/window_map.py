"""Five disjoint old-episode windows of native retrospective forgetting.

POSTHOC development forensic only. No new source, model, owner or checkpoint.
The native is an isolated, exact-source copy; all witnesses were consumed.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import canonical, digest

HERE = Path(__file__).resolve().parent
S = spec_from_file_location(
    "jepa2_archival_frozen_native",
    HERE.parent / "YGG-JEPA2-05-RESET-POSTHOC" / "diagnose.py")
D = module_from_spec(S)
S.loader.exec_module(D)

PREREG_FIRST = "d47182e97750ffecfd3a656a8ecd3db0ec640b62"
EXACT_FROZEN_ORIGINAL = "7b0d9fd8c16b8e0433a632666cec88d8d008c19f"
PROBE_SIZE = D.PROBE_COUNT
WINDOW_COUNT = 5
ALARM_TOLERANCE = 0.03
ORIGINAL_N = {14071: 1006, 14072: 981}


def check(condition, code):
    D.check(condition, "OLD_WINDOW_" + code)


def windows(rows):
    n = len(rows)
    check(n >= (WINDOW_COUNT * PROBE_SIZE),
          "NO_DISJOINT_WINDOWS")
    starts = [(k * (n - PROBE_SIZE)) // (WINDOW_COUNT - 1)
              for k in range(WINDOW_COUNT)]
    result = [(start, tuple(rows[start:start+PROBE_SIZE]))
              for start in starts]
    check(starts[-1] == n - PROBE_SIZE and
          all(starts[i+1] >= starts[i] + PROBE_SIZE
              for i in range(len(starts)-1)), "WINDOW_OVERLAP")
    check(all(len(rows) == PROBE_SIZE for _, rows in result),
          "WINDOW_SIZE")
    return result


def score_all(model, blocks):
    return [D.native_score(model, block) for _, block in blocks]


def at_event(native, event):
    ident, views, first, state, second, reward = event
    return native.observe(ident, views, {
        "s1": views[0][0],
        "x1": first, "s2": state, "x2": second, "y": reward,
    })


def inspect(seed, platform, published):
    start_time = time.process_time()
    old_model = D.load_original(seed)
    final_model, outer_sha = D.load_continued(seed, platform)
    begin = old_model.original.base.native
    final = final_model.original.base.native
    initial = begin._ledger
    total = final._ledger
    check(len(initial) == ORIGINAL_N[seed], "ORIGINAL_ROW_COUNT")
    check(total[:len(initial)] == initial, "IMMUTABLE_PREFIX")
    check(len(total) == len(initial)+16, "AUTHENTIC_SUFFIX_COUNT")
    check(digest(begin.checkpoint()) ==
          published["original_native_sha256"], "OLD_NATIVE_SHA")
    blocks = windows(initial)
    before = score_all(begin, blocks)
    check(abs(before[-1] -
              published["historic_readonly_native_before"]) <=
          D.MAX_ABS_REPRODUCTION_ERROR, "PUBLISHED_BEFORE_LAST32")
    check(blocks[-1][1] == initial[-PROBE_SIZE:],
          "LAST32_IDENTITY")
    native = begin
    resets = []
    for ordinal, event in enumerate(total[len(initial):], 1):
        old_native = native
        next_native = at_event(old_native, event)
        check(next_native._ledger ==
              total[:len(initial)+ordinal],
              "EXACT_EVENT_" + str(ordinal))
        if old_native._context_start != next_native._context_start:
            # The same public outcome is appended and learned normally,
            # but only the context reset re-partition is suppressed.
            without = old_native._clone()
            without._append(event)
            without._update_context(event)
            check(without._ledger == next_native._ledger,
                  "SAME_RESET_WITNESS")
            check(without._context_start == old_native._context_start,
                  "RESET_SUPPRESSION_ONLY")
            b_pre = score_all(old_native, blocks)
            b_plain = score_all(without, blocks)
            b_reset = score_all(next_native, blocks)
            resets.append({
                "ordinal": ordinal,
                "old_context_start": old_native._context_start,
                "new_context_start": next_native._context_start,
                "before_reset_event": b_pre,
                "same_update_no_reset": b_plain,
                "actual_after_reset": b_reset,
                "ordinary_update_effect":
                    [x - y for x, y in zip(b_plain, b_pre)],
                "isolated_context_reset_effect":
                    [x - y for x, y in zip(b_reset, b_plain)],
            })
        native = next_native
    check(len(resets) == 1 and
          resets[0]["ordinal"] == D.EXPECTED_CONTEXT_RESET[seed],
          "ACTUAL_CONTEXT_RESET")
    check(native.checkpoint() == final.checkpoint(),
          "FINAL_EXACT_NATIVE_CHECKPOINT")
    completed = score_all(native, blocks)
    check(abs(completed[-1] -
              published["historic_readonly_native_after"]) <=
          D.MAX_ABS_REPRODUCTION_ERROR, "PUBLISHED_AFTER_LAST32")
    check(completed == score_all(final, blocks),
          "COLD_FINAL_READOUT")
    delta = [new - old for old, new in zip(before, completed)]
    matched = [x > ALARM_TOLERANCE for x in delta]
    return {
        "old_seed": seed,
        "continuation_seed": published["seed"],
        "original_old_witnesses": len(initial),
        "new_source_observations": 16,
        "original_trained_model_sha256": D.OLD_PIN[seed],
        "original_native_sha256": published["original_native_sha256"],
        "continued_original_model_sha256": outer_sha,
        "continued_native_sha256": digest(native.checkpoint()),
        "windows": [
            {
                "label": "historical_window_%d" % k,
                "start": start, "stop_exclusive": start + PROBE_SIZE,
                "original_seen_example_brier": before[k],
                "continued_seen_example_brier": completed[k],
                "change": delta[k],
                "exceeds_original_drift_tolerance": matched[k],
            }
            for k, (start, _) in enumerate(blocks)
        ],
        "reset": resets[0],
        "windows_exceeding_tolerance": sum(matched),
        "window_count": len(blocks),
        "broad_under_frozen_criterion": sum(matched) >= 4,
        "cpu_process_seconds": time.process_time() - start_time,
        "source_actions": 0,
        "scientific_pass": False,
        "accepted_native": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--platform", choices=("linux", "windows"),
                   required=True)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    D.audited_archive(args.platform)
    published = json.loads((D.JEPA/"result.json").read_bytes())
    check(published["development_go"] is False and
          published["science_pass"] is False,
          "PUBLISHED_DEV_NO_GO")
    old = {x["old_seed"]: x for x in published["replicas"]}
    check(set(old) == set(D.OLD_PIN), "PUBLISHED_SEED_IDENTITY")
    out = {
        "schema": "yggdrasil.jepa2-05.retrospective-old-windows.v1",
        "qualified_original_source": EXACT_FROZEN_ORIGINAL,
        "posthoc_protocol_commit": PREREG_FIRST,
        "platform": args.platform,
        "classification": "UNPREREGISTERED_POSTHOC",
        "scientific_pass": False,
        "source_first_use": False,
        "accepted_native": False,
        "source_actions": 0,
        "deployment": "NONE",
        "records": [],
    }
    try:
        for seed in (14071, 14072):
            out["records"].append(
                inspect(seed, args.platform, old[seed]))
        out["verdict"] = (
            "BROAD_ARCHIVAL_INTERFERENCE_NOT_SCIENCE"
            if all(r["broad_under_frozen_criterion"]
                   for r in out["records"])
            else "LOCALIZED_OR_HETEROGENEOUS_ARCHIVAL_INTERFERENCE")
        out["status"] = "ARCHIVAL_FIVE_WINDOW_REPRODUCTION_PASS"
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
