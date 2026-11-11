"""Frozen WSP-36 synthetic DEV / PRIMARY evaluation (not a general-rule learner)."""
import argparse
import hashlib
import json
import platform
import sys
import time
from model import (
    GATES, N_INPUTS, MASKS, NumericCircuit, GateTrainCache,
    THREE, TWO, FOUR, table, source_spec, learned_weights
)

WORLD_COUNTS = {"DEV": 64, "PRIMARY": 256}
TARGETS = tuple(tuple((n >> k) & 1 for k in range(N_INPUTS)) for n in range(8))

def generate(cohort, world):
    """Exact inherited WSP35 generator; PRIMARY is never used to tune a model."""
    if cohort not in WORLD_COUNTS or type(world) is not int or not 0 <= world < WORLD_COUNTS[cohort]:
        raise ValueError("WSP36_BAD_COHORT")
    records = []
    for i in range(GATES):
        d = hashlib.sha256(("WSP35-V1|" + cohort + "|" + str(world) + "|" + str(i)).encode("ascii")).digest()
        left = d[1] % 3 if i == 0 else (
            3 + i - 2 if cohort == "PRIMARY" and i > 1 and i % 2 else 3 + i - 1)
        right = d[2] % (3 + i)
        records.append((left, right, table(MASKS[d[0] % len(MASKS)])))
    return source_spec(tuple(records))

def independent_oracle(spec, x):
    source_spec(spec)
    vals = list(x)
    for left, right, truth in spec:
        vals.append(truth[2 * vals[left] + vals[right]])
    return vals[-1]

def novel_rule(spec):
    """Change ONLY an unobserved truth-table bit on the final gate."""
    updated = list(spec)
    left, right, truth = updated[-1]
    new_truth = list(truth)
    new_truth[2] = 1 - new_truth[2]
    updated[-1] = (left, right, tuple(new_truth))
    return source_spec(tuple(updated))

def cold(program):
    raw = program.snapshot()
    restored = NumericCircuit.restore(raw)
    if raw != restored.snapshot() or restored.rows != program.rows:
        raise AssertionError("WSP36_COLD_RESTORE")
    return restored, len(raw)

def run(cohort="DEV"):
    if cohort not in WORLD_COUNTS:
        raise ValueError("WSP36_BAD_COHORT")
    started = time.perf_counter()
    count = WORLD_COUNTS[cohort]
    names = ("direct_3", "direct_2", "direct_0", "trained_3", "full4")
    gates = dict.fromkeys(names, 0)
    composed = dict.fromkeys(names, 0)
    train = GateTrainCache()
    trace = hashlib.sha256()
    probe_counts = {"three": 0, "two": 0, "four": 0, "ood_three": 0, "ood_four": 0}
    checks = {"worlds": 0, "cold": 0, "source_replays": 0, "oracle_parity": 0, "gate_rows": 0, "composed_outputs": 0}
    ood = {"three_gate7_correct": 0, "four_gate7_correct": 0, "gate7_rows": 0}
    max_checkpoint_bytes = 0
    for world in range(count):
        spec = generate(cohort, world)
        written3, recovered3, q3 = learned_weights(spec, THREE)
        written2, recovered2, q2 = learned_weights(spec, TWO)
        written4, recovered4, q4 = learned_weights(spec, FOUR)
        restored3, n3 = cold(written3)
        restored2, n2 = cold(written2)
        restored4, n4 = cold(written4)
        null = NumericCircuit()
        matched_trained, nt = cold(train.trained_circuit(recovered3))
        max_checkpoint_bytes = max(max_checkpoint_bytes, n3, n2, n4, nt)
        probe_counts["three"] += len(q3)
        probe_counts["two"] += len(q2)
        probe_counts["four"] += len(q4)
        checks["cold"] += 4
        if (written3.snapshot() != learned_weights(spec, THREE)[0].snapshot()
                or recovered4 != spec):
            raise AssertionError("WSP36_SOURCE_REPLAY")
        checks["source_replays"] += 1
        for gate in range(GATES):
            truth = spec[gate][2]
            for row in FOUR:
                predicted = {
                    "direct_3": recovered3[gate][2][row],
                    "direct_2": recovered2[gate][2][row],
                    "direct_0": 0,
                    "trained_3": recovered3[gate][2][row],
                    "full4": recovered4[gate][2][row]
                }
                for name, bit in predicted.items():
                    gates[name] += int(bit == truth[row])
                trace.update(json.dumps(["gate", world, gate, row, truth[row], predicted],
                                        sort_keys=True, separators=(",", ":")).encode("ascii"))
                checks["gate_rows"] += 1
        for x in TARGETS:
            true = independent_oracle(spec, x)
            predicted = {
                "direct_3": restored3.predict(x),
                "direct_2": restored2.predict(x),
                "direct_0": null.predict(x),
                "trained_3": matched_trained.predict(x),
                "full4": restored4.predict(x)
            }
            if predicted["full4"] != true:
                raise AssertionError("WSP36_ORACLE_MISMATCH")
            checks["oracle_parity"] += 1
            for name, bit in predicted.items():
                composed[name] += int(bit == true)
            checks["composed_outputs"] += 1
            trace.update(json.dumps(["composed", world, x, true, predicted],
                                    sort_keys=True, separators=(",", ":")).encode("ascii"))
        unknown = novel_rule(spec)
        out3, known3, qo3 = learned_weights(unknown, THREE)
        out4, known4, qo4 = learned_weights(unknown, FOUR)
        out3, _ = cold(out3)
        out4, _ = cold(out4)
        probe_counts["ood_three"] += len(qo3)
        probe_counts["ood_four"] += len(qo4)
        checks["cold"] += 2
        for row in FOUR:
            actual = unknown[-1][2][row]
            p3 = known3[-1][2][row]
            p4 = known4[-1][2][row]
            ood["three_gate7_correct"] += int(p3 == actual)
            ood["four_gate7_correct"] += int(p4 == actual)
            ood["gate7_rows"] += 1
            trace.update(json.dumps(["ood", world, row, actual, p3, p4],
                                    separators=(",", ":")).encode("ascii"))
        checks["worlds"] += 1
    gate_labels = count * GATES * 4
    output_labels = count * len(TARGETS)
    expected_queries = {name: count * GATES * n for name, n in (
        ("three", 3), ("two", 2), ("four", 4), ("ood_three", 3), ("ood_four", 4))}
    valid = (checks["worlds"] == count
             and checks["gate_rows"] == gate_labels
             and checks["composed_outputs"] == output_labels
             and checks["oracle_parity"] == output_labels
             and checks["source_replays"] == count
             and checks["cold"] == 6*count
             and probe_counts == expected_queries
             and ood["gate7_rows"] == 4*count
             and ood["three_gate7_correct"] == 3*count
             and ood["four_gate7_correct"] == 4*count
             and train.worst_bce <= 0.01
             and train.fresh_fits + train.hits == count*GATES)
    min_gates = 7783 if cohort == "PRIMARY" else 1946
    min_outputs = 1946 if cohort == "PRIMARY" else 487
    min_margin = 820 if cohort == "PRIMARY" else 205
    margin = gates["direct_3"] - gates["direct_2"]
    if not valid:
        status = "INVALID"
    elif (gates["direct_3"] >= min_gates and composed["direct_3"] >= min_outputs
          and margin >= min_margin):
        status = "DEV_SUPPORTED"
    elif margin > 0:
        status = "MIXED"
    else:
        status = "SCIENTIFIC_NEGATIVE"
    result = {
        "schema": "wsp36.partial-evidence-weight-acquisition.v1",
        "cohort": cohort, "scientific_status": status,
        "engineering": "PASS" if valid else "FAIL",
        "scores_gate_rows": gates, "gate_row_denominator": gate_labels,
        "scores_composed": composed, "composed_denominator": output_labels,
        "two_to_three_probe_gate_gain": margin,
        "thresholds": {"gate_correct": min_gates, "composed_correct": min_outputs,
                       "gate_gain": min_margin},
        "query_counts": probe_counts, "checks": checks, "ood": ood,
        "conventional": {"fresh_converged_fits": train.fresh_fits,
                         "cache_hits": train.hits, "actual_gradient_updates": train.updates,
                         "worst_bce": train.worst_bce,
                         "limitation": "Both arms use identical fixed family prior; trained gate tables use floats and unmatched total cost."},
        "capacity": {"direct_writable_bits": 216, "max_serialized_bytes": max_checkpoint_bytes,
                     "runtime": "WSP35 generic numerical interpreter, authored Python prior inference; cost not matched to training"},
        "trace_sha256": trace.hexdigest(), "seconds": round(time.perf_counter()-started, 6),
        "environment": {"python": sys.version, "platform": platform.platform()},
        "limits": "Known-family rule induction only; OOD unobserved row guaranteed wrong; no arbitrary unknown knowledge, universal model, measured overall training replacement, or independent SCIENTIFIC_PASS."
    }
    if not valid:
        raise AssertionError("WSP36_INVALID_CUSTODY")
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", choices=WORLD_COUNTS, default="DEV")
    opt = parser.parse_args()
    print(json.dumps(run(opt.cohort), sort_keys=True, indent=2))
