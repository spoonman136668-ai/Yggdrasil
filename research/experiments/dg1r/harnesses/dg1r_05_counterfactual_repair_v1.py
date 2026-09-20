#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
import time
from pathlib import Path

import numpy as np

PARENT_NAME = "dg1r_04_software_nanite_v1.py"
WORLD_START = 20260926050000
WORLD_COUNT = 8
DAMAGE_AFTER_STEPS = 1024
POST_STEPS = 32
HORIZONS = (1, 4, 8, 16, 32)
PRIMARY_METHODS = (
    "SLOW128_MIXED1",
    "N16_H5",
    "N16_H6",
    "N16_H6_REPAIR",
)
NEGATIVE_CONTROL = "N16_H6_DAMP"
METHODS = PRIMARY_METHODS + (NEGATIVE_CONTROL,)
LESION_SIZES = ("SMALL3", "LARGE5")
LESION_COMPARTMENTS = (0, 2, 4, 6)


def load_parent():
    path = Path(__file__).resolve().parent / PARENT_NAME
    spec = importlib.util.spec_from_file_location("dg1r04_parent", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def init_post_telemetry(parent, state):
    tel = parent.init_telemetry()
    tel["prev_nanite_bits"] = state[parent.NANITE_SITES].copy()
    tel["nanite_run_lengths"][:] = 0
    tel["completed_run_lengths"] = []
    return tel


def evolve_prefix(parent, u, mapped, mixed_rules, method):
    state = np.zeros(parent.WIDTH, dtype=np.uint8)
    for t in range(DAMAGE_AFTER_STEPS):
        parent.evolve_one_external(
            state,
            int(u[t]),
            mapped,
            mixed_rules,
            method,
            telemetry=None,
            record=None,
        )
    return state


def unmapped_sibling_block_start(mapped, compartment_index):
    comp_start = compartment_index * 16
    p = int(mapped[compartment_index])
    if p < comp_start + 8:
        return comp_start + 8
    return comp_start


def lesion_workers(block_start, lesion_size):
    if lesion_size == "SMALL3":
        offsets = (2, 3, 4)
    elif lesion_size == "LARGE5":
        offsets = (1, 2, 3, 4, 5)
    else:
        raise ValueError(lesion_size)
    return np.asarray(
        [block_start + off for off in offsets],
        dtype=np.int64,
    )


def no_damage_control(parent, pre_state, u, mapped, mixed_rules, method):
    a = pre_state.copy()
    b = pre_state.copy()
    max_div = 0.0
    for h in range(1, POST_STEPS + 1):
        bit = int(u[DAMAGE_AFTER_STEPS + h - 1])
        parent.evolve_one_external(
            a, bit, mapped, mixed_rules, method,
            telemetry=None, record=None,
        )
        parent.evolve_one_external(
            b, bit, mapped, mixed_rules, method,
            telemetry=None, record=None,
        )
        div = float(np.mean(a != b))
        max_div = max(max_div, div)
    return float(max_div)


def post_damage_telemetry_delta(parent, ref_tel, dmg_tel, method):
    if method == "SLOW128_MIXED1":
        return {
            "nanite_bit_changes_delta": 0,
            "damp_suppressed_transitions_delta": 0,
            "repair_attempts_delta": 0,
            "repair_state_changes_delta": 0,
        }

    ref = parent.finalize_telemetry(ref_tel)
    dmg = parent.finalize_telemetry(dmg_tel)
    return {
        "nanite_bit_changes_delta": int(
            dmg["nanite_bit_changes"] - ref["nanite_bit_changes"]
        ),
        "damp_suppressed_transitions_delta": int(
            dmg["damp_suppressed_transitions"]
            - ref["damp_suppressed_transitions"]
        ),
        "repair_attempts_delta": int(
            dmg["repair_attempts"] - ref["repair_attempts"]
        ),
        "repair_state_changes_delta": int(
            dmg["repair_state_changes"] - ref["repair_state_changes"]
        ),
    }


def one_scenario(
    parent,
    pre_state,
    u,
    mapped,
    mixed_rules,
    method,
    compartment_index,
    lesion_size,
):
    block_start = unmapped_sibling_block_start(
        mapped, compartment_index
    )
    lesion = lesion_workers(block_start, lesion_size)
    assert not np.any(np.isin(lesion, mapped))
    assert not np.any(np.isin(lesion, parent.NANITE_SITES))

    ref = pre_state.copy()
    dmg = pre_state.copy()
    dmg[lesion] ^= 1

    ref_tel = (
        None if method == "SLOW128_MIXED1"
        else init_post_telemetry(parent, ref)
    )
    dmg_tel = (
        None if method == "SLOW128_MIXED1"
        else init_post_telemetry(parent, dmg)
    )

    horizon_metrics = {}
    whole_curve = []
    full_flags = []
    lesion_mask = np.zeros(parent.WIDTH, dtype=bool)
    lesion_mask[lesion] = True
    outside_mask = ~lesion_mask

    for h in range(1, POST_STEPS + 1):
        bit = int(u[DAMAGE_AFTER_STEPS + h - 1])
        parent.evolve_one_external(
            ref, bit, mapped, mixed_rules, method,
            telemetry=ref_tel, record=None,
        )
        parent.evolve_one_external(
            dmg, bit, mapped, mixed_rules, method,
            telemetry=dmg_tel, record=None,
        )

        diff = dmg != ref
        whole = float(np.mean(diff))
        lesion_div = float(np.mean(diff[lesion_mask]))
        outside_div = float(np.mean(diff[outside_mask]))
        spread_count = int(np.sum(diff[outside_mask]))
        full = bool(not np.any(diff))

        whole_curve.append(whole)
        full_flags.append(full)

        if h in HORIZONS:
            horizon_metrics[f"h{h}"] = {
                "whole_state_divergence": whole,
                "lesion_divergence": lesion_div,
                "lesion_recovery": float(1.0 - lesion_div),
                "outside_lesion_divergence": outside_div,
                "damage_spread_count": spread_count,
                "full_recovery": full,
            }

    recovery_time = None
    for h in range(1, POST_STEPS + 1):
        if all(full_flags[h - 1:]):
            recovery_time = h
            break

    tel_delta = post_damage_telemetry_delta(
        parent, ref_tel, dmg_tel, method
    )

    return {
        "compartment_index": int(compartment_index),
        "block_start": int(block_start),
        "lesion_size": lesion_size,
        "lesion_workers": [int(v) for v in lesion],
        "horizons": horizon_metrics,
        "excess_divergence_area": float(np.sum(whole_curve)),
        "recovery_time": (
            None if recovery_time is None else int(recovery_time)
        ),
        "sustained_full_recovery": bool(recovery_time is not None),
        "exact_match_h32": bool(full_flags[-1]),
        "intervention_delta": tel_delta,
    }


def one_world(parent, seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    u = rng.integers(
        0, 2, size=DAMAGE_AFTER_STEPS + POST_STEPS,
        dtype=np.uint8,
    )
    mapped = parent.mapped_positions(rng)
    mixed_rules = parent.mixed_rule_assignment(rng)

    method_rows = {}
    controls = {}

    for method in METHODS:
        pre = evolve_prefix(
            parent, u, mapped, mixed_rules, method
        )
        controls[method] = no_damage_control(
            parent, pre, u, mapped, mixed_rules, method
        )

        scenarios = []
        for compartment in LESION_COMPARTMENTS:
            for lesion_size in LESION_SIZES:
                scenarios.append(
                    one_scenario(
                        parent,
                        pre,
                        u,
                        mapped,
                        mixed_rules,
                        method,
                        compartment,
                        lesion_size,
                    )
                )
        method_rows[method] = {
            "no_damage_control_max_divergence": controls[method],
            "scenarios": scenarios,
        }

    return {
        "seed": int(seed),
        "mapped_positions": [int(v) for v in mapped],
        "nanite_sites": [int(v) for v in parent.NANITE_SITES],
        "mixed_rule_counts": {
            str(int(r)): int(np.sum(mixed_rules == r))
            for r in parent.MIX_RULES
        },
        "methods": method_rows,
    }


def q(values, p):
    return float(
        np.quantile(np.asarray(values, dtype=np.float64), p)
    )


def flatten_scenarios(rows, method, lesion_size=None):
    out = []
    for row in rows:
        for sc in row["methods"][method]["scenarios"]:
            if lesion_size is None or sc["lesion_size"] == lesion_size:
                out.append(sc)
    return out


def summarize_scenarios(scenarios):
    out = {
        "scenario_count": len(scenarios),
        "horizons": {},
    }

    for h in HORIZONS:
        key = f"h{h}"
        whole = [
            sc["horizons"][key]["whole_state_divergence"]
            for sc in scenarios
        ]
        lesion_recovery = [
            sc["horizons"][key]["lesion_recovery"]
            for sc in scenarios
        ]
        outside = [
            sc["horizons"][key]["outside_lesion_divergence"]
            for sc in scenarios
        ]
        spread = [
            sc["horizons"][key]["damage_spread_count"]
            for sc in scenarios
        ]
        exact = [
            sc["horizons"][key]["full_recovery"]
            for sc in scenarios
        ]
        out["horizons"][key] = {
            "whole_state_divergence_median": q(whole, 0.5),
            "whole_state_divergence_p90": q(whole, 0.90),
            "lesion_recovery_median": q(lesion_recovery, 0.5),
            "lesion_recovery_p10": q(lesion_recovery, 0.10),
            "outside_lesion_divergence_median": q(outside, 0.5),
            "outside_lesion_divergence_p90": q(outside, 0.90),
            "damage_spread_count_median": q(spread, 0.5),
            "damage_spread_count_p90": q(spread, 0.90),
            "exact_match_rate": float(np.mean(exact)),
        }

    auc = [sc["excess_divergence_area"] for sc in scenarios]
    sustained = [sc["sustained_full_recovery"] for sc in scenarios]
    exact32 = [sc["exact_match_h32"] for sc in scenarios]
    recovered_times = [
        sc["recovery_time"]
        for sc in scenarios
        if sc["recovery_time"] is not None
    ]

    out["excess_divergence_area_median"] = q(auc, 0.5)
    out["excess_divergence_area_p90"] = q(auc, 0.90)
    out["full_recovery_rate"] = float(np.mean(sustained))
    out["exact_match_rate_h32"] = float(np.mean(exact32))
    out["recovered_scenario_count"] = len(recovered_times)
    out["recovery_time_median_recovered"] = (
        q(recovered_times, 0.5)
        if recovered_times else None
    )

    intervention_keys = (
        "nanite_bit_changes_delta",
        "damp_suppressed_transitions_delta",
        "repair_attempts_delta",
        "repair_state_changes_delta",
    )
    out["intervention_delta"] = {}
    for key in intervention_keys:
        vals = [
            sc["intervention_delta"][key]
            for sc in scenarios
        ]
        out["intervention_delta"][key] = {
            "median": q(vals, 0.5),
            "p10": q(vals, 0.10),
            "p90": q(vals, 0.90),
        }

    return out


def relative_reduction(value, reference):
    if reference <= 1e-15:
        return 0.0
    return float((reference - value) / reference)


def summarize(rows):
    mechanical_valid = all(
        row["methods"][method]["no_damage_control_max_divergence"] == 0.0
        for row in rows
        for method in METHODS
    )

    out = {
        "worlds": len(rows),
        "mechanical_valid": bool(mechanical_valid),
        "methods": {},
        "relative_to_slow128": {},
    }

    for method in METHODS:
        out["methods"][method] = {
            "SMALL3": summarize_scenarios(
                flatten_scenarios(rows, method, "SMALL3")
            ),
            "LARGE5": summarize_scenarios(
                flatten_scenarios(rows, method, "LARGE5")
            ),
            "COMBINED": summarize_scenarios(
                flatten_scenarios(rows, method, None)
            ),
        }

    ref = out["methods"]["SLOW128_MIXED1"]["COMBINED"]
    nanites = ("N16_H5", "N16_H6", "N16_H6_REPAIR")

    for method in nanites + (NEGATIVE_CONTROL,):
        cur = out["methods"][method]["COMBINED"]
        auc_reduction = relative_reduction(
            cur["excess_divergence_area_median"],
            ref["excess_divergence_area_median"],
        )
        out16_reduction = relative_reduction(
            cur["horizons"]["h16"][
                "outside_lesion_divergence_median"
            ],
            ref["horizons"]["h16"][
                "outside_lesion_divergence_median"
            ],
        )
        out32_reduction = relative_reduction(
            cur["horizons"]["h32"][
                "outside_lesion_divergence_median"
            ],
            ref["horizons"]["h32"][
                "outside_lesion_divergence_median"
            ],
        )
        lesion_gain16 = (
            cur["horizons"]["h16"]["lesion_recovery_median"]
            - ref["horizons"]["h16"]["lesion_recovery_median"]
        )
        lesion_gain32 = (
            cur["horizons"]["h32"]["lesion_recovery_median"]
            - ref["horizons"]["h32"]["lesion_recovery_median"]
        )

        containment = (
            auc_reduction >= 0.25
            and out16_reduction >= 0.25
            and cur["horizons"]["h32"][
                "outside_lesion_divergence_median"
            ]
            <= ref["horizons"]["h32"][
                "outside_lesion_divergence_median"
            ]
        )
        repair = (
            (lesion_gain16 >= 0.10 or lesion_gain32 >= 0.10)
            and cur["excess_divergence_area_median"]
            <= ref["excess_divergence_area_median"]
        )
        strong = (
            cur["horizons"]["h16"][
                "whole_state_divergence_median"
            ] <= 0.05
            and cur["horizons"]["h32"][
                "whole_state_divergence_median"
            ] <= 0.03
            and cur["horizons"]["h32"][
                "lesion_recovery_median"
            ] >= 0.80
            and cur["horizons"]["h32"][
                "outside_lesion_divergence_median"
            ] <= 0.02
            and cur["full_recovery_rate"] >= 0.25
            and auc_reduction >= 0.25
        )

        out["relative_to_slow128"][method] = {
            "excess_divergence_area_reduction_fraction": auc_reduction,
            "outside_h16_reduction_fraction": out16_reduction,
            "outside_h32_reduction_fraction": out32_reduction,
            "lesion_recovery_gain_h16": float(lesion_gain16),
            "lesion_recovery_gain_h32": float(lesion_gain32),
            "containment_signal": bool(containment),
            "repair_signal": bool(repair),
            "strong_counterfactual_recovery": bool(strong),
            "eligible_primary_candidate": bool(method in nanites),
            "homeostatic_repair_candidate": bool(
                method in nanites and containment and repair
            ),
        }

    out["homeostatic_repair_candidates"] = [
        method
        for method in nanites
        if out["relative_to_slow128"][method][
            "homeostatic_repair_candidate"
        ]
    ]
    out["full_self_repair_signal"] = bool(
        mechanical_valid
        and any(
            out["relative_to_slow128"][method][
                "homeostatic_repair_candidate"
            ]
            and out["relative_to_slow128"][method][
                "strong_counterfactual_recovery"
            ]
            for method in nanites
        )
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
    runtimes = []
    for i in range(WORLD_COUNT):
        seed = WORLD_START + i
        t0 = time.perf_counter()
        row = one_world(parent, seed)
        runtimes.append({
            "seed": seed,
            "world_seconds": float(time.perf_counter() - t0),
        })
        rows.append(row)

    canonical = {
        "schema": (
            "yggdrasil.dg1r-05-local-damage-"
            "counterfactual-recovery.v1"
        ),
        "rows": rows,
        "summary": summarize(rows),
        "worlds": len(rows),
        "seed_start": WORLD_START,
        "seed_end": WORLD_START + WORLD_COUNT - 1,
        "damage_after_steps": DAMAGE_AFTER_STEPS,
        "post_steps": POST_STEPS,
    }
    runtime = {
        "schema": "yggdrasil.dg1r-05-runtime-sidecar.v1",
        "rows": runtimes,
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
            json.dumps(runtime, sort_keys=True, indent=2) + "\n",
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
