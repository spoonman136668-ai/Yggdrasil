"""V31M-OPT: external bounded reuse of IDENTICAL public ring computations.

Preregistered engineering counterfactual, NOT native learner or science.
The V22 source and all original model/checkpoint code remain unmodified.
"""
from __future__ import annotations

from collections import OrderedDict
from contextlib import contextmanager, nullcontext
import gc
import hashlib
import json
import math
import statistics
import time
import tracemalloc

from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v31i_cold_restart_audit import replay
from research.itd02_v31j_executed_edge_ledger_audit import (
    EXPECTED_CHECKPOINT_SHA, EXPECTED_TRACE_SHA, meter_executed_edges,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import canonical
import yggdrasil.itd02_v22_shared_context_ring_dev as v22


@contextmanager
def bounded_ring_cache():
    """Read-only, ephemeral memoization; validate keys, clone mutable results."""
    old_site = v22._site_features
    old_mix = v22._mix_scalars
    features = OrderedDict()
    mixes = OrderedDict()
    stats = {"feature_hits": 0, "feature_misses": 0,
             "mix_hits": 0, "mix_misses": 0, "max_feature_keys": 0,
             "max_mix_keys": 0}

    def site(cue, first):
        if type(cue) is not str or cue not in v22.PUBLIC_CUES or (
                type(first) is not str or first not in v22.ACTIONS):
            return old_site(cue, first)  # Preserve source's failure semantics.
        key = (cue, first)
        if key in features:
            stats["feature_hits"] += 1
            features.move_to_end(key)
            return [list(row) for row in features[key]]
        value = old_site(cue, first)
        stats["feature_misses"] += 1
        features[key] = tuple(tuple(row) for row in value)
        if len(features) > 36:
            features.popitem(last=False)
        stats["max_feature_keys"] = max(stats["max_feature_keys"], len(features))
        return value

    def mix(values, hops=v22.HOPS):
        if (type(values) is not list or len(values) != v22.CELLS or
                type(hops) is not int or not 0 <= hops <= v22.HOPS or
                any(type(x) not in (int, float) or not math.isfinite(x) or
                    abs(x) > 10000 for x in values)):
            return old_mix(values, hops)  # No invalid-input cache bypass.
        key = (tuple(values), hops)
        if key in mixes:
            stats["mix_hits"] += 1
            mixes.move_to_end(key)
            saved_values, saved_count = mixes[key]
            return list(saved_values), saved_count
        result, count = old_mix(values, hops)
        stats["mix_misses"] += 1
        mixes[key] = (tuple(result), count)
        if len(mixes) > 64:
            mixes.popitem(last=False)
        stats["max_mix_keys"] = max(stats["max_mix_keys"], len(mixes))
        return result, count

    v22._site_features = site
    v22._mix_scalars = mix
    try:
        yield stats
    finally:
        v22._site_features = old_site
        v22._mix_scalars = old_mix


def run(source, optimized, cold=False):
    with (bounded_ring_cache() if optimized else nullcontext()):
        return replay(source, cold)


def verify(rows, checkpoint, original_rows, original_checkpoint):
    if rows != original_rows or checkpoint != original_checkpoint:
        raise AssertionError("V31M_OPT_MODEL_OR_CHECKPOINT_PARITY_BROKEN")
    if len(rows) != 24:
        raise AssertionError("V31M_OPT_PUBLIC_EVENT_COUNT_DRIFT")
    if (hashlib.sha256(canonical(rows)).hexdigest() != EXPECTED_TRACE_SHA or
            hashlib.sha256(checkpoint).hexdigest() != EXPECTED_CHECKPOINT_SHA):
        raise AssertionError("V31M_OPT_FROZEN_V31I_IDENTITY_DRIFT")


def meter_once(source, optimized, original_rows, original_checkpoint):
    with meter_executed_edges() as counts:
        if optimized:
            with bounded_ring_cache() as caches:
                rows, checkpoint = replay(source, False)
        else:
            rows, checkpoint = replay(source, False)
            caches = None
    verify(rows, checkpoint, original_rows, original_checkpoint)
    return dict(counts), None if caches is None else dict(caches)


def measure_peak(source, optimized, original_rows, original_checkpoint):
    gc.collect()
    tracemalloc.start()
    try:
        rows, checkpoint = run(source, optimized, False)
        _current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    verify(rows, checkpoint, original_rows, original_checkpoint)
    return peak


def benchmark(source, original_rows, original_checkpoint):
    for optimized in (False, True):  # fixed one-shot warm-up per arm
        rows, checkpoint = run(source, optimized, False)
        verify(rows, checkpoint, original_rows, original_checkpoint)
    cpu = {"baseline": [], "cache": []}
    paired = []
    for i in range(9):  # locked alternating AB/BA order
        order = (False, True) if i % 2 == 0 else (True, False)
        samples = {}
        for optimized in order:
            gc.collect()  # outside measured interval
            start = time.process_time_ns()
            rows, checkpoint = run(source, optimized, False)
            elapsed = time.process_time_ns() - start
            verify(rows, checkpoint, original_rows, original_checkpoint)
            if elapsed <= 0:
                raise AssertionError("V31M_OPT_CPU_CLOCK_RESOLUTION")
            samples["cache" if optimized else "baseline"] = elapsed
        for arm in ("baseline", "cache"):
            cpu[arm].append(samples[arm])
        paired.append(samples["cache"] / samples["baseline"])
    return {
        "baseline_cpu_median_ns": int(statistics.median(cpu["baseline"])),
        "cache_cpu_median_ns": int(statistics.median(cpu["cache"])),
        "paired_cpu_ratio_median": round(statistics.median(paired), 8),
        "cpu_trials_per_arm": 9,
        "paired_cpu_ratios": [round(value, 8) for value in paired],
    }


def main():
    source = train_source()["pretrained_shared"]
    original_rows, original_checkpoint = run(source, False)
    verify(original_rows, original_checkpoint, original_rows, original_checkpoint)
    for optimized in (False, True):
        for cold in (False, True):
            rows, checkpoint = run(source, optimized, cold)
            verify(rows, checkpoint, original_rows, original_checkpoint)
    baseline, _ = meter_once(source, False, original_rows, original_checkpoint)
    optimized, cache_stats = meter_once(source, True, original_rows, original_checkpoint)
    expected = {"input_calls": 264, "input_scalar_hops": 118272,
                "mix_calls": 480, "mix_scalar_hops": 30720}
    if baseline != expected:
        raise AssertionError("V31M_OPT_V31J_EXECUTED_BASELINE_MISMATCH")
    for field in ("input_scalar_hops", "mix_scalar_hops"):
        if not 0 <= optimized[field] < baseline[field]:
            raise AssertionError("V31M_OPT_NO_ACTUAL_SIMULATED_RING_REDUCTION")
    if (cache_stats["feature_hits"] <= 0 or cache_stats["mix_hits"] <= 0 or
            cache_stats["max_feature_keys"] > 36 or
            cache_stats["max_mix_keys"] > 64):
        raise AssertionError("V31M_OPT_UNBOUNDED_OR_UNUSED_CACHE")
    bench = benchmark(source, original_rows, original_checkpoint)
    baseline_peak = measure_peak(source, False, original_rows, original_checkpoint)
    optimized_peak = measure_peak(source, True, original_rows, original_checkpoint)
    memory_ratio = optimized_peak / baseline_peak if baseline_peak else math.inf
    # Frozen outcome gate: resource-negative is not a CI failure or silent waiver.
    resource_positive = (bench["paired_cpu_ratio_median"] <= .95 and
                         memory_ratio <= 1.25)
    report = {
        "schema": "yggdrasil.itd02.v31m_opt.external_ring_cache.v1",
        "classification": ("V31M_OPT_HOST_RESOURCE_POSITIVE__NO_SCIENCE"
                           if resource_positive else
                           "V31M_OPT_NO_RESOURCE_WIN__NO_SCIENCE"),
        "source_only": True, "scientific_first_use": False,
        "reserved_q_holdout_evaluated": False,
        "native_model_modified": False, "original_v22_modified": False,
        "host_and_trial_specific_performance": True,
        "physical_wire_bytes_measured": False,
        "retail_all_in_performance_qualified": False,
        "ephemeral_non_native_cache": True,
        "events_per_trial": 24,
        "original_trace_sha256": EXPECTED_TRACE_SHA,
        "original_checkpoint_sha256": EXPECTED_CHECKPOINT_SHA,
        "baseline_executed": baseline,
        "cache_executed": optimized,
        "saved_input_scalar_hops": baseline["input_scalar_hops"]-optimized["input_scalar_hops"],
        "saved_mix_scalar_hops": baseline["mix_scalar_hops"]-optimized["mix_scalar_hops"],
        "cache_stats": cache_stats,
        "resource": {**bench, "baseline_tracemalloc_peak_bytes": baseline_peak,
                     "cache_tracemalloc_peak_bytes": optimized_peak,
                     "tracemalloc_peak_ratio": round(memory_ratio, 8)},
        "continuous_and_cold_restart_byte_identical": True,
    }
    print(json.dumps(report, sort_keys=True, separators=(",", ":"),
                     allow_nan=False))


if __name__ == "__main__":
    main()
