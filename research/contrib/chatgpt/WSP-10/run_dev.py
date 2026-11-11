"""WSP-10 frozen public development evaluator; no external calls."""
import json
import time
from crossbar import DirectCrossbar, GRADIENT_STEPS


def execute():
    t0 = time.perf_counter()
    count = exact = baseline = ablations = restores = zero_mismatches = wires = 0
    lengths = []
    for n in (2, 3):
        for mask in range(1 << (1 << n)):
            circuit = DirectCrossbar.from_spec(n, mask)
            empty = DirectCrossbar(n)
            before = circuit.programmed_sha256()
            for index in range(1 << n):
                bits = tuple((index >> k) & 1 for k in range(n))
                expected = (mask >> index) & 1
                exact += circuit.evaluate(bits) == expected
                baseline += expected == ((mask >> index) & 1)
                zero_mismatches += empty.evaluate(bits) != expected
                count += 1
            raw = circuit.snapshot()
            restored = DirectCrossbar.restore(raw)
            restores += (restored.snapshot() == raw and
                         restored.programmed_sha256() == before)
            lengths.append(len(raw))
            wires += circuit.active_connections()
            if mask:
                first_positive = next(i for i in range(1 << n)
                                      if (mask >> i) & 1)
                wires_before = circuit.active_connections()
                circuit.weights[first_positive * circuit.stride + 2*n] = 0
                bits = tuple((first_positive >> k) & 1 for k in range(n))
                ablations += (circuit.evaluate(bits) == 0 and
                              circuit.active_connections() == wires_before - 1)
    sensitive = DirectCrossbar.from_spec(3, 2)
    permuted_negative = (sensitive.evaluate((1, 0, 0)) == 1 and
                         sensitive.evaluate((0, 1, 0)) == 0)
    metrics = {
        "schema": "wsp10.public-dev-result.v1",
        "specifications": 272,
        "queries": count,
        "crossbar_exact": exact,
        "independent_symbolic_exact": baseline,
        "cold_restores": restores,
        "nonzero_mask_ablations_detected": ablations,
        "unprogrammed_zero_circuit_mismatches": zero_mismatches,
        "permuted_input_negative_detected": permuted_negative,
        "total_active_programmed_edges_across_worlds": wires,
        "checkpoint_min_bytes": min(lengths),
        "checkpoint_max_bytes": max(lengths),
        "gradient_steps": GRADIENT_STEPS,
        "local_elapsed_seconds_not_a_speed_comparison": round(time.perf_counter()-t0,6),
        "scientific_classification": "UNVERIFIED: full task specifications supplied; no independent novelty or information savings",
    }
    required = (count==2112 and exact==count and baseline==count and
                restores==272 and ablations==270 and zero_mismatches==1056 and
                wires==4192 and permuted_negative and GRADIENT_STEPS==0)
    metrics["focused_engineering"] = "PASS" if required else "FAIL"
    print(json.dumps(metrics, sort_keys=True, indent=2))
    if not required:
        raise SystemExit(1)
    return metrics

if __name__ == "__main__":
    execute()
