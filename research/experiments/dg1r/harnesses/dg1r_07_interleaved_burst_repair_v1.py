#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
import time
from pathlib import Path

import numpy as np

PARENT_NAME = "dg1r_06_secded_nanite_repair_v1.py"
WIDTH = 128
CODEWORDS = 16
CODE_BITS = 8
DATA_PER_WORD = 4
DATA_OFFSETS = (2, 4, 5, 6)
WORLD_START = 20260926070000
WORLD_COUNT = 8
HEALTHY_STEPS = 1024
POST_STEPS = 32
HORIZONS = (1, 4, 8, 16, 32)
BURSTS = (3, 5, 8, 9)

METHODS = (
    "CONTIG_PASSIVE",
    "CONTIG_SECDED",
    "INTERLEAVE8_PASSIVE",
    "INTERLEAVE8_SECDED",
)


def load_parent():
    path = Path(__file__).resolve().parent / PARENT_NAME
    spec = importlib.util.spec_from_file_location("dg1r06_parent", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def layout_of(method):
    return "INTERLEAVE8" if method.startswith("INTERLEAVE8") else "CONTIG"


def repair_enabled(method):
    return method.endswith("SECDED")


def code_positions(layout, word):
    if layout == "CONTIG":
        return np.arange(word * 8, word * 8 + 8, dtype=np.int64)
    region = (word // 8) * 64
    c = word % 8
    return np.asarray(
        [region + bit * 8 + c for bit in range(8)],
        dtype=np.int64,
    )


def data_physical_sites(layout):
    out = []
    for word in range(CODEWORDS):
        pos = code_positions(layout, word)
        out.extend(int(pos[o]) for o in DATA_OFFSETS)
    return np.asarray(out, dtype=np.int64)


def logical_input_indices(rng):
    return np.asarray(
        [comp * 8 + int(rng.integers(0, 8)) for comp in range(8)],
        dtype=np.int64,
    )


def input_physical_sites(layout, logical_indices):
    data_sites = data_physical_sites(layout)
    return data_sites[logical_indices]


def encode_state(parent, logical_data, layout):
    state = np.zeros(WIDTH, dtype=np.uint8)
    for word in range(CODEWORDS):
        data4 = logical_data[word * 4:word * 4 + 4]
        code = parent.encode_block_from_data(data4)
        state[code_positions(layout, word)] = code
    return state


def extract_logical_data(state, layout):
    return state[data_physical_sites(layout)].copy()


def healthy_valid(parent, state, layout):
    for word in range(CODEWORDS):
        code = state[code_positions(layout, word)]
        syn, overall = parent.syndrome(code)
        if syn != 0 or overall != 0:
            return False
    return True


def init_telemetry():
    return {
        "single_error_corrections": 0,
        "corrections_on_original_burst": 0,
        "corrections_outside_original_burst": 0,
        "detected_double_errors": 0,
        "syndrome_nonzero_events": 0,
        "corrected_codewords": set(),
        "outside_corrected_codewords": set(),
    }


def inspect_or_repair(
    parent,
    state,
    layout,
    word,
    enabled,
    telemetry=None,
    burst_set=None,
):
    pos = code_positions(layout, word)
    code = state[pos].copy()
    syn, overall = parent.syndrome(code)

    if telemetry is not None and syn != 0:
        telemetry["syndrome_nonzero_events"] += 1

    if not enabled:
        if telemetry is not None and syn != 0 and overall == 0:
            telemetry["detected_double_errors"] += 1
        return

    physical = None
    if syn != 0 and overall == 1:
        physical = int(pos[syn - 1])
    elif syn == 0 and overall == 1:
        physical = int(pos[7])
    elif syn != 0 and overall == 0:
        if telemetry is not None:
            telemetry["detected_double_errors"] += 1
        return
    else:
        return

    state[physical] ^= 1
    if telemetry is not None:
        telemetry["single_error_corrections"] += 1
        telemetry["corrected_codewords"].add(int(word))
        if burst_set is not None and physical in burst_set:
            telemetry["corrections_on_original_burst"] += 1
        else:
            telemetry["corrections_outside_original_burst"] += 1
            telemetry["outside_corrected_codewords"].add(int(word))


def evolve_one(
    parent,
    state,
    bit,
    logical_inputs,
    rules64,
    method,
    telemetry=None,
    burst_set=None,
):
    layout = layout_of(method)
    enabled = repair_enabled(method)

    for word in range(CODEWORDS):
        inspect_or_repair(
            parent,
            state,
            layout,
            word,
            enabled,
            telemetry=telemetry,
            burst_set=burst_set,
        )

    data = extract_logical_data(state, layout)
    data[logical_inputs] = np.uint8(bit)
    data = parent.eca_step_mixed(data, rules64)
    state[:] = encode_state(parent, data, layout)


def evolve_prefix(parent, u, logical_inputs, rules64, method):
    state = encode_state(
        parent,
        np.zeros(CODEWORDS * DATA_PER_WORD, dtype=np.uint8),
        layout_of(method),
    )
    for t in range(HEALTHY_STEPS):
        evolve_one(
            parent,
            state,
            int(u[t]),
            logical_inputs,
            rules64,
            method,
        )
    return state


def no_damage_control(
    parent,
    pre,
    u,
    logical_inputs,
    rules64,
    method,
):
    a = pre.copy()
    b = pre.copy()
    max_div = 0.0
    for h in range(1, POST_STEPS + 1):
        bit = int(u[HEALTHY_STEPS + h - 1])
        evolve_one(parent, a, bit, logical_inputs, rules64, method)
        evolve_one(parent, b, bit, logical_inputs, rules64, method)
        max_div = max(max_div, float(np.mean(a != b)))
    return max_div


def choose_burst_starts(seed, mapped_union):
    rng = np.random.default_rng(
        np.random.PCG64(seed ^ 0x5A17D107)
    )
    out = {}
    mapped_set = set(int(v) for v in mapped_union)
    for length in BURSTS:
        starts = []
        for region_start in (0, 64):
            valid = []
            last = region_start + 64 - length
            for start in range(region_start, last + 1):
                cells = set(range(start, start + length))
                if cells.isdisjoint(mapped_set):
                    valid.append(start)
            if len(valid) < 2:
                raise RuntimeError(
                    f"insufficient burst starts for length {length}"
                )
            chosen = rng.choice(
                np.asarray(valid, dtype=np.int64),
                size=2,
                replace=False,
            )
            starts.extend(int(v) for v in chosen)
        out[length] = sorted(starts)
    return out


def initial_load(layout, burst_positions):
    burst_set = set(int(v) for v in burst_positions)
    counts = []
    for word in range(CODEWORDS):
        positions = set(int(v) for v in code_positions(layout, word))
        counts.append(len(positions & burst_set))
    return {
        "damaged_codeword_count": int(sum(v > 0 for v in counts)),
        "max_errors_per_codeword": int(max(counts)),
        "single_error_codeword_count": int(sum(v == 1 for v in counts)),
        "multi_error_codeword_count": int(sum(v >= 2 for v in counts)),
        "error_counts_per_codeword": [int(v) for v in counts],
    }


def sustained_recovery_time(flags):
    for h in range(1, len(flags) + 1):
        if all(flags[h - 1:]):
            return h
    return None


def current_codeword_metrics(
    ref,
    dmg,
    layout,
    originally_hit_words,
):
    divergent = []
    for word in range(CODEWORDS):
        pos = code_positions(layout, word)
        if np.any(ref[pos] != dmg[pos]):
            divergent.append(word)
    divergent_set = set(divergent)
    spread_words = divergent_set - set(originally_hit_words)
    return len(divergent), len(spread_words)


def one_scenario(
    parent,
    pre,
    u,
    logical_inputs,
    rules64,
    method,
    burst_start,
    burst_length,
):
    layout = layout_of(method)
    burst = np.arange(
        burst_start,
        burst_start + burst_length,
        dtype=np.int64,
    )
    burst_set = set(int(v) for v in burst)
    load = initial_load(layout, burst)
    originally_hit_words = [
        i
        for i, count in enumerate(load["error_counts_per_codeword"])
        if count > 0
    ]

    ref = pre.copy()
    dmg = pre.copy()
    dmg[burst] ^= 1
    telemetry = init_telemetry()

    outside = np.ones(WIDTH, dtype=bool)
    outside[burst] = False

    logical_curve = []
    whole_curve = []
    full_flags = []
    data_flags = []
    horizons = {}

    for h in range(1, POST_STEPS + 1):
        bit = int(u[HEALTHY_STEPS + h - 1])
        evolve_one(
            parent,
            ref,
            bit,
            logical_inputs,
            rules64,
            method,
        )
        evolve_one(
            parent,
            dmg,
            bit,
            logical_inputs,
            rules64,
            method,
            telemetry=telemetry,
            burst_set=burst_set,
        )

        diff = dmg != ref
        ref_data = extract_logical_data(ref, layout)
        dmg_data = extract_logical_data(dmg, layout)
        logical_diff = dmg_data != ref_data

        whole = float(np.mean(diff))
        logical = float(np.mean(logical_diff))
        outside_div = float(np.mean(diff[outside]))
        full = bool(not np.any(diff))
        data_full = bool(not np.any(logical_diff))
        damaged_words, spread_words = current_codeword_metrics(
            ref, dmg, layout, originally_hit_words
        )

        whole_curve.append(whole)
        logical_curve.append(logical)
        full_flags.append(full)
        data_flags.append(data_full)

        if h in HORIZONS:
            horizons[f"h{h}"] = {
                "whole_physical_divergence": whole,
                "logical_data_divergence": logical,
                "outside_physical_burst_divergence": outside_div,
                "damage_spread_count": int(np.sum(diff[outside])),
                "damaged_codeword_count": int(damaged_words),
                "miscorrected_codeword_count": int(spread_words),
                "exact_full_state_match": full,
                "exact_logical_data_match": data_full,
            }

    full_time = sustained_recovery_time(full_flags)
    data_time = sustained_recovery_time(data_flags)

    return {
        "burst_start": int(burst_start),
        "burst_length": int(burst_length),
        "burst_positions": [int(v) for v in burst],
        "initial_layout_load": load,
        "horizons": horizons,
        "excess_logical_data_divergence_area": float(
            np.sum(logical_curve)
        ),
        "excess_whole_divergence_area": float(
            np.sum(whole_curve)
        ),
        "sustained_full_recovery": bool(full_time is not None),
        "sustained_logical_data_recovery": bool(
            data_time is not None
        ),
        "recovery_time_full": (
            None if full_time is None else int(full_time)
        ),
        "recovery_time_data": (
            None if data_time is None else int(data_time)
        ),
        "ecc_telemetry": {
            "single_error_corrections": int(
                telemetry["single_error_corrections"]
            ),
            "corrections_on_original_burst": int(
                telemetry["corrections_on_original_burst"]
            ),
            "corrections_outside_original_burst": int(
                telemetry["corrections_outside_original_burst"]
            ),
            "detected_double_errors": int(
                telemetry["detected_double_errors"]
            ),
            "syndrome_nonzero_events": int(
                telemetry["syndrome_nonzero_events"]
            ),
            "corrected_codeword_count": int(
                len(telemetry["corrected_codewords"])
            ),
            "outside_corrected_codeword_count": int(
                len(telemetry["outside_corrected_codewords"])
            ),
        },
    }


def q(values, p):
    return float(
        np.quantile(np.asarray(values, dtype=np.float64), p)
    )


def flatten(rows, method, burst_length=None):
    out = []
    for row in rows:
        for sc in row["methods"][method]["scenarios"]:
            if burst_length is None or sc["burst_length"] == burst_length:
                out.append(sc)
    return out


def summarize_scenarios(scenarios):
    out = {
        "scenario_count": len(scenarios),
        "horizons": {},
    }

    for h in HORIZONS:
        key = f"h{h}"
        metrics = (
            "whole_physical_divergence",
            "logical_data_divergence",
            "outside_physical_burst_divergence",
            "damage_spread_count",
            "damaged_codeword_count",
            "miscorrected_codeword_count",
        )
        row = {}
        for metric in metrics:
            vals = [sc["horizons"][key][metric] for sc in scenarios]
            row[f"{metric}_median"] = q(vals, 0.5)
            row[f"{metric}_p90"] = q(vals, 0.90)
        row["exact_full_state_match_rate"] = float(
            np.mean([
                sc["horizons"][key]["exact_full_state_match"]
                for sc in scenarios
            ])
        )
        row["exact_logical_data_match_rate"] = float(
            np.mean([
                sc["horizons"][key]["exact_logical_data_match"]
                for sc in scenarios
            ])
        )
        out["horizons"][key] = row

    for metric in (
        "excess_logical_data_divergence_area",
        "excess_whole_divergence_area",
    ):
        vals = [sc[metric] for sc in scenarios]
        out[f"{metric}_median"] = q(vals, 0.5)
        out[f"{metric}_p90"] = q(vals, 0.90)

    out["sustained_full_recovery_rate"] = float(
        np.mean([sc["sustained_full_recovery"] for sc in scenarios])
    )
    out["sustained_logical_data_recovery_rate"] = float(
        np.mean([
            sc["sustained_logical_data_recovery"]
            for sc in scenarios
        ])
    )

    full_times = [
        sc["recovery_time_full"]
        for sc in scenarios
        if sc["recovery_time_full"] is not None
    ]
    data_times = [
        sc["recovery_time_data"]
        for sc in scenarios
        if sc["recovery_time_data"] is not None
    ]
    out["recovery_time_full_median_recovered"] = (
        q(full_times, 0.5) if full_times else None
    )
    out["recovery_time_data_median_recovered"] = (
        q(data_times, 0.5) if data_times else None
    )

    load_metrics = (
        "damaged_codeword_count",
        "max_errors_per_codeword",
        "single_error_codeword_count",
        "multi_error_codeword_count",
    )
    out["initial_layout_load"] = {}
    for metric in load_metrics:
        vals = [sc["initial_layout_load"][metric] for sc in scenarios]
        out["initial_layout_load"][metric] = {
            "median": q(vals, 0.5),
            "p90": q(vals, 0.90),
        }

    telemetry_metrics = (
        "single_error_corrections",
        "corrections_on_original_burst",
        "corrections_outside_original_burst",
        "detected_double_errors",
        "syndrome_nonzero_events",
        "corrected_codeword_count",
        "outside_corrected_codeword_count",
    )
    out["ecc_telemetry"] = {}
    for metric in telemetry_metrics:
        vals = [sc["ecc_telemetry"][metric] for sc in scenarios]
        out["ecc_telemetry"][metric] = {
            "median": q(vals, 0.5),
            "p90": q(vals, 0.90),
        }
    return out


def relative_reduction(value, reference):
    if reference <= 1e-15:
        return 0.0
    return float((reference - value) / reference)


def one_world(parent, seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    u = rng.integers(
        0, 2, size=HEALTHY_STEPS + POST_STEPS,
        dtype=np.uint8,
    )
    logical_inputs = logical_input_indices(rng)
    rules64 = parent.mixed_rule_assignment_n(rng, 64)

    contig_input = input_physical_sites(
        "CONTIG", logical_inputs
    )
    inter_input = input_physical_sites(
        "INTERLEAVE8", logical_inputs
    )
    mapped_union = np.unique(
        np.concatenate((contig_input, inter_input))
    )
    burst_starts = choose_burst_starts(seed, mapped_union)

    methods = {}
    pre_states = {}

    for method in METHODS:
        pre = evolve_prefix(
            parent, u, logical_inputs, rules64, method
        )
        pre_states[method] = pre
        control = no_damage_control(
            parent,
            pre,
            u,
            logical_inputs,
            rules64,
            method,
        )
        scenarios = []
        for length in BURSTS:
            for start in burst_starts[length]:
                scenarios.append(
                    one_scenario(
                        parent,
                        pre,
                        u,
                        logical_inputs,
                        rules64,
                        method,
                        start,
                        length,
                    )
                )
        methods[method] = {
            "healthy_code_valid": bool(
                healthy_valid(
                    parent,
                    pre,
                    layout_of(method),
                )
            ),
            "no_damage_control_max_divergence": float(control),
            "scenarios": scenarios,
        }

    contig_data = extract_logical_data(
        pre_states["CONTIG_SECDED"],
        "CONTIG",
    )
    inter_data = extract_logical_data(
        pre_states["INTERLEAVE8_SECDED"],
        "INTERLEAVE8",
    )

    return {
        "seed": int(seed),
        "logical_input_indices": [
            int(v) for v in logical_inputs
        ],
        "contig_input_positions": [
            int(v) for v in contig_input
        ],
        "interleaved_input_positions": [
            int(v) for v in inter_input
        ],
        "burst_starts": {
            str(k): [int(v) for v in vals]
            for k, vals in burst_starts.items()
        },
        "healthy_cross_layout_logical_data_equal": bool(
            np.array_equal(contig_data, inter_data)
        ),
        "methods": methods,
    }


def summarize(rows):
    mechanical_valid = all(
        row["methods"][method][
            "no_damage_control_max_divergence"
        ] == 0.0
        for row in rows
        for method in METHODS
    )
    healthy_valid = all(
        row["methods"][method]["healthy_code_valid"]
        for row in rows
        for method in METHODS
    )
    cross_layout = all(
        row["healthy_cross_layout_logical_data_equal"]
        for row in rows
    )

    out = {
        "worlds": len(rows),
        "mechanical_valid": bool(mechanical_valid),
        "healthy_code_valid": bool(healthy_valid),
        "healthy_cross_layout_logical_data_equal": bool(
            cross_layout
        ),
        "methods": {},
    }

    for method in METHODS:
        out["methods"][method] = {}
        for length in BURSTS:
            out["methods"][method][f"BURST{length}"] = (
                summarize_scenarios(
                    flatten(rows, method, length)
                )
            )
        out["methods"][method]["ALL"] = summarize_scenarios(
            flatten(rows, method, None)
        )

    inter5 = out["methods"]["INTERLEAVE8_SECDED"]["BURST5"]
    inter8 = out["methods"]["INTERLEAVE8_SECDED"]["BURST8"]
    contig5 = out["methods"]["CONTIG_SECDED"]["BURST5"]
    passive9 = out["methods"]["INTERLEAVE8_PASSIVE"]["BURST9"]
    inter9 = out["methods"]["INTERLEAVE8_SECDED"]["BURST9"]

    def exact_signal(summary):
        return bool(
            summary["horizons"]["h1"][
                "logical_data_divergence_median"
            ] == 0.0
            and summary["horizons"]["h1"][
                "whole_physical_divergence_median"
            ] == 0.0
            and summary["sustained_full_recovery_rate"] >= 0.95
            and summary["initial_layout_load"][
                "max_errors_per_codeword"
            ]["median"] == 1.0
            and summary["ecc_telemetry"][
                "corrections_outside_original_burst"
            ]["median"] == 0.0
        )

    burst5_exact = exact_signal(inter5)
    burst8_exact = exact_signal(inter8)

    advantage_auc = relative_reduction(
        inter5["excess_logical_data_divergence_area_median"],
        contig5["excess_logical_data_divergence_area_median"],
    )
    advantage_recovery = (
        inter5["sustained_full_recovery_rate"]
        - contig5["sustained_full_recovery_rate"]
    )
    advantage = bool(
        advantage_auc >= 0.90
        and advantage_recovery >= 0.75
    )

    burst9_ratio = (
        inter9["excess_logical_data_divergence_area_median"]
        / (
            passive9["excess_logical_data_divergence_area_median"]
            + 1e-15
        )
    )
    burst9_safe = bool(burst9_ratio <= 1.10)

    out["burst5_exact_repair"] = bool(burst5_exact)
    out["burst8_exact_repair"] = bool(burst8_exact)
    out["interleaving_advantage_auc_reduction_fraction"] = float(
        advantage_auc
    )
    out["interleaving_advantage_recovery_gain"] = float(
        advantage_recovery
    )
    out["interleaving_advantage"] = bool(advantage)
    out["burst9_secded_to_passive_data_auc_ratio"] = float(
        burst9_ratio
    )
    out["burst9_safe"] = bool(burst9_safe)
    out["full_interleaved_burst_repair_signal"] = bool(
        mechanical_valid
        and healthy_valid
        and cross_layout
        and burst5_exact
        and burst8_exact
        and advantage
    )
    return out


def encode(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def run():
    parent = load_parent()
    rows = []
    runtime_rows = []
    for i in range(WORLD_COUNT):
        seed = WORLD_START + i
        t0 = time.perf_counter()
        row = one_world(parent, seed)
        runtime_rows.append({
            "seed": seed,
            "world_seconds": float(
                time.perf_counter() - t0
            ),
        })
        rows.append(row)

    canonical = {
        "schema": (
            "yggdrasil.dg1r-07-interleaved-"
            "secded-burst-repair.v1"
        ),
        "rows": rows,
        "summary": summarize(rows),
        "worlds": len(rows),
        "seed_start": WORLD_START,
        "seed_end": WORLD_START + WORLD_COUNT - 1,
        "healthy_steps": HEALTHY_STEPS,
        "post_steps": POST_STEPS,
    }
    runtime = {
        "schema": "yggdrasil.dg1r-07-runtime-sidecar.v1",
        "rows": runtime_rows,
    }
    return canonical, runtime


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--runtime-out")
    args = ap.parse_args()

    obj, runtime = run()
    raw = (encode(obj) + "\n").encode("utf-8")
    Path(args.out).write_bytes(raw)

    if args.runtime_out:
        Path(args.runtime_out).write_text(
            json.dumps(runtime, sort_keys=True, indent=2)
            + "\n",
            encoding="utf-8",
        )

    digest = hashlib.sha256(raw).hexdigest()
    print(encode({
        "output": args.out,
        "sha256": digest,
        "summary": obj["summary"],
        "worlds": obj["worlds"],
    }))


if __name__ == "__main__":
    main()
