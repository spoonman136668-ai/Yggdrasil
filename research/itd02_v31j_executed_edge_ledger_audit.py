"""V31J: audit executed V22 ring scalar-hop work without modifying the learner.

Source-only, public development streams; not model promotion or science acceptance.
"""
from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager

from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v31i_cold_restart_audit import replay
from research.itd02_v31i_cold_restart_codec import restore
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import canonical
from yggdrasil.itd02_v31d_distinct_return_dev import DistinctReturnRingDev
import yggdrasil.itd02_v22_shared_context_ring_dev as v22

EXPECTED_TRACE_SHA = "84427bdfa27b0a43e30a699548877a9184413e62e0a6ec6de491fb5ed184b7ff"
EXPECTED_CHECKPOINT_SHA = "0b03b83f999afdab24eb71805a24766fa6b98c069151d14bccfa949602b63c48"
COUNTERS = ("forward_input_messages", "forward_output_messages", "reverse_credit_messages")


def counter_snapshot(model):
    model.bank._guard()
    return {name: {
        field: getattr(bank, field) for field in COUNTERS
    } for name, bank in (("source", model.bank.slow), ("fast", model.bank.fast))}


def counter_delta(before, after):
    delta = {field: sum(after[bank][field] - before[bank][field]
                        for bank in ("source", "fast"))
             for field in COUNTERS}
    if any(type(n) is not int or n < 0 for n in delta.values()):
        raise AssertionError("V31J_COUNTER_REGRESSED_OR_MALFORMED")
    return delta


@contextmanager
def meter_executed_edges():
    # Instrument only module-global functions used by the UNCHANGED V22 code.
    # This measures simulated Python scalar hops, not physical transport bytes.
    old_forward = v22.forward_local
    old_mix = v22._mix_scalars
    counts = {"input_calls": 0, "input_scalar_hops": 0,
              "mix_calls": 0, "mix_scalar_hops": 0}

    def forward(*args, **kwargs):
        value = old_forward(*args, **kwargs)
        if (not isinstance(value, (tuple, list)) or len(value) != 3 or
                type(value[2]) is not int or value[2] < 0):
            raise AssertionError("V31J_INVALID_FORWARD_TRANSPORT")
        counts["input_calls"] += 1
        counts["input_scalar_hops"] += value[2]
        return value

    def mix(*args, **kwargs):
        value = old_mix(*args, **kwargs)
        if (not isinstance(value, (tuple, list)) or len(value) != 2 or
                type(value[1]) is not int or value[1] < 0):
            raise AssertionError("V31J_INVALID_NEIGHBOR_TRANSPORT")
        counts["mix_calls"] += 1
        counts["mix_scalar_hops"] += value[1]
        return value

    v22.forward_local, v22._mix_scalars = forward, mix
    try:
        yield counts
    finally:
        v22.forward_local, v22._mix_scalars = old_forward, old_mix


def audited_replay(source, with_restart):
    initial = counter_snapshot(DistinctReturnRingDev(source))
    with meter_executed_edges() as measured:
        rows, checkpoint = replay(source, with_restart)
    terminal = restore(checkpoint)
    nominal = counter_delta(initial, counter_snapshot(terminal))
    executed = dict(measured)
    if len(rows) != 24 or terminal.bank.source_sha != DistinctReturnRingDev(source).bank.source_sha:
        raise AssertionError("V31J_SOURCE_OR_EVENT_IDENTITY_DRIFT")
    if any(executed[k] < 0 for k in executed):
        raise AssertionError("V31J_NEGATIVE_METER")
    if executed["input_scalar_hops"] < nominal["forward_input_messages"]:
        raise AssertionError("V31J_INPUT_METER_MISSING_TRANSPORT")
    expected_nominal_mix = (nominal["forward_output_messages"] +
                            nominal["reverse_credit_messages"])
    if executed["mix_scalar_hops"] < expected_nominal_mix:
        raise AssertionError("V31J_MIX_METER_MISSING_TRANSPORT")
    audit = {
        "recorded_nominal": nominal,
        "executed_observed": executed,
        "unmetered_input_scalar_hops": (executed["input_scalar_hops"] -
                                         nominal["forward_input_messages"]),
        "unmetered_mix_scalar_hops": (executed["mix_scalar_hops"] -
                                       expected_nominal_mix),
    }
    return rows, checkpoint, audit


def main():
    source = train_source()["pretrained_shared"]
    baseline_rows, baseline_checkpoint = replay(source, False)
    if hashlib.sha256(canonical(baseline_rows)).hexdigest() != EXPECTED_TRACE_SHA:
        raise AssertionError("V31I_TRACE_IDENTITY_DRIFT")
    if hashlib.sha256(baseline_checkpoint).hexdigest() != EXPECTED_CHECKPOINT_SHA:
        raise AssertionError("V31I_CHECKPOINT_IDENTITY_DRIFT")

    rows_a, checkpoint_a, audit_a = audited_replay(source, False)
    rows_b, checkpoint_b, audit_b = audited_replay(source, True)
    if (rows_a != baseline_rows or rows_b != baseline_rows or
            checkpoint_a != baseline_checkpoint or checkpoint_b != baseline_checkpoint or
            audit_a != audit_b):
        raise AssertionError("V31J_MEASUREMENT_CHANGED_MODEL_OR_COLD_RESTART")

    misses = audit_a["unmetered_input_scalar_hops"] + audit_a["unmetered_mix_scalar_hops"]
    classification = ("V31J_UNMETERED_RECOMPUTATION_FOUND__NO_SCIENCE" if misses
                      else "V31J_LEDGER_CONSISTENT__NO_SCIENCE")
    report = {
        "schema": "yggdrasil.itd02.v31j.executed_edge_ledger.v1",
        "classification": classification,
        "events": 24,
        "source_only": True,
        "scientific_first_use": False,
        "reserved_q_holdout_evaluated": False,
        "native_model_modified": False,
        "physical_transport_bytes_measured": False,
        "retail_performance_measured": False,
        "continuous_and_cold_restart_identical": True,
        "canonical_trace_sha256": EXPECTED_TRACE_SHA,
        "checkpoint_sha256": EXPECTED_CHECKPOINT_SHA,
        **audit_a,
    }
    print(json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main()
