"""F100R2 PRESTO: query-blind native memory observational equivalence.

Not a learned policy, a scientific result, or an executor. Its only additional
persistent state is one one-bit deviation latch. No query, answer, future event
or raw historical event buffer enters any selection function.
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PREREG_R2_SHA = "65065cadc268d5169dd3fe9fd2bb37987db92357"
PREREG_P0_SHA = "a09e20ea3d8c33b8b180a52c52a60c1376bfab30"
F99_SHA = "5de08fe74eb74dd917a7559cc3a8755185aac823"
F62_SHA = "7ed72deca5584d7c0b6562d74456fa7d4bee6712"
F85_SHA = "e4eb4bfbd6a01212f8c1eebc38af09b15c6d9cc3"
MAX_SIGN = 250_000
RECORD_BYTES = 12
RECORD_CAP = 12
MAX_DEVIATIONS = 1
MAX_REPLAY_EVENTS = 12


def blob(path):
    raw = Path(path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def checked_module(name, path, digest):
    if blob(path) != digest:
        raise AssertionError("F100_FROZEN_SOURCE_DRIFT:" + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def frozen_sources():
    if blob(HERE / "prereg_r2.json") != PREREG_R2_SHA:
        raise AssertionError("F100_R2_PREREG_DRIFT")
    if blob(HERE / "prereg.json") != PREREG_P0_SHA:
        raise AssertionError("F100_P0_HISTORICAL_PREREG_DRIFT")
    if blob(ROOT / "20261015-y-f62" / "source_pilot.py") != F62_SHA:
        raise AssertionError("F100_NATIVE_F62_DRIFT")
    if blob(ROOT / "20261016-y-f85" / "global_solver.py") != F85_SHA:
        raise AssertionError("F100_F85_CONTROL_DRIFT")
    f99 = checked_module("f100_exact_immutable_f99",
                         ROOT / "20261016-y-f99" / "causal_closure.py", F99_SHA)
    f99.frozen_dependencies()  # Assert frozen F98 ancestry; never reads cohorts.
    return f99


def singleton_self_replay_events(baseline, current_event):
    """Only events encoded by native baseline singleton records. No history."""
    if len(current_event) != 3:
        raise ValueError("F100_EVENT_SHAPE")
    choices = set()
    for u, v, codes in baseline:
        if len(codes) != 1:
            continue
        code = codes[0]
        if type(code) is not int or not 0 <= code < 8:
            raise ValueError("F100_NATIVE_ROLE")
        event = (u, code // 2, v) if code % 2 == 0 else (v, code // 2, u)
        if event != tuple(current_event):
            choices.add(event)
    return (tuple(current_event),) + tuple(sorted(choices)[:MAX_REPLAY_EVENTS - 1])


def valid(mem, pack, native):
    native._valid_memory(mem, pack)
    if len(mem) > RECORD_CAP:
        raise AssertionError("F100_NATIVE_RECORD_CAP")
    if sum(len(pack.pack(*r)) for r in mem) != RECORD_CAP * RECORD_BYTES * 0 + RECORD_BYTES * len(mem):
        raise AssertionError("F100_PACKED_NATIVE_12B")
    return mem


def signatures(mem, f99):
    all_rows = f99.closure(mem, max_hops=6, max_signatures=MAX_SIGN)
    short = frozenset(r for r in all_rows if len(r[1]) <= 4)
    long = frozenset(r for r in all_rows if 5 <= len(r[1]) <= 6)
    return short, long


def replay_invariant(baseline, after, current_event, pack, native, f99):
    """Replay ONLY current input + singleton edges derived from native memory."""
    replay = singleton_self_replay_events(baseline, current_event)
    b = baseline
    a = after
    for event in replay:
        b = valid(native._f60_step(b, event, pack), pack, native)
        a = valid(native._f60_step(a, event, pack), pack, native)
        bshort, _ = signatures(b, f99)
        ashort, _ = signatures(a, f99)
        if bshort != ashort:
            return False
    return True


def select(memory, event, index, used_deviation, pack, native, f99):
    """One streaming online choice with no past-event history or future task.

    Returns (new_native_memory, new_one_bit_latch, bounded_accounting).
    The f99 argument is exact frozen path logic, not outcomes or a learner.
    """
    if type(index) is not int or not 0 <= index < 72:
        raise ValueError("F100_INDEX_BOUNDS")
    if type(used_deviation) is not bool:
        raise ValueError("F100_ONE_BIT_LATCH")
    if len(event) != 3 or any(type(x) is not int for x in event):
        raise ValueError("F100_PUBLIC_EVENT_ONLY")
    valid(memory, pack, native)
    baseline = valid(native._f60_step(memory, event, pack), pack, native)
    legal = native.actions(memory, event, index, pack)
    if sum(action[3] == baseline for action in legal) != 1:
        raise AssertionError("F100_EXACT_F60_ACTION_PARITY")
    stats = dict(native_alternatives=0, current_equal=0,
                 long_gain_eligible=0, replay_pass=0,
                 resource_rejections=0, intervened=False,
                 selected_native_action_index=None)
    if used_deviation or index >= 48:
        return baseline, used_deviation, stats
    try:
        base_short, base_long = signatures(baseline, f99)
    except f99.ClosureLimitExceeded:
        stats["resource_rejections"] += 1
        return baseline, used_deviation, stats
    best = None
    for j, action in enumerate(legal):
        after = action[3]
        if after == baseline:
            continue
        stats["native_alternatives"] += 1
        valid(after, pack, native)
        try:
            short, long = signatures(after, f99)
            if short != base_short:
                continue
            stats["current_equal"] += 1
            gain = len(long - base_long)
            if gain <= 0:
                continue
            stats["long_gain_eligible"] += 1
            if not replay_invariant(baseline, after, event, pack, native, f99):
                continue
        except f99.ClosureLimitExceeded:
            stats["resource_rejections"] += 1
            continue
        stats["replay_pass"] += 1
        shared = sum(rec in baseline for rec in after)
        rank = (gain, shared, -j)
        if best is None or rank > best[0]:
            best = (rank, j, after)
    if best is None:
        return baseline, used_deviation, stats
    _, index_selected, selected = best
    stats["intervened"] = True
    stats["selected_native_action_index"] = index_selected
    return selected, True, stats


def online(stream, pack, native, f99, trace=False):
    """Driver uses only each observed prefix in order. No source labels/queries."""
    memory, used = (), False
    log = []
    totals = dict(native_alternatives=0, current_equal=0,
                  long_gain_eligible=0, replay_pass=0,
                  resource_rejections=0, interventions=0,
                  max_retained_native_bytes=0, extra_latch_bits=1,
                  persistent_raw_event_history_bytes=0, learned_parameter_bytes=0)
    for index, event in enumerate(stream):
        memory, used, stats = select(memory, event, index, used, pack, native, f99)
        for key in ("native_alternatives", "current_equal", "long_gain_eligible",
                    "replay_pass", "resource_rejections"):
            totals[key] += stats[key]
        totals["interventions"] += int(stats["intervened"])
        totals["max_retained_native_bytes"] = max(
            totals["max_retained_native_bytes"], len(memory) * RECORD_BYTES)
        if trace:
            log.append(tuple(pack.pack(*row).hex() for row in memory))
    if index != 71:
        raise ValueError("F100_EXPECTED_72_PUBLIC_EVENTS")
    assert totals["interventions"] <= MAX_DEVIATIONS
    return memory, tuple(log), totals
