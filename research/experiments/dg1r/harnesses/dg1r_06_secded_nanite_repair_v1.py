#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
import time
from pathlib import Path

import numpy as np

PARENT_NAME = "dg1r_04_software_nanite_v1.py"

WIDTH = 128
BLOCK_SIZE = 8
BLOCK_COUNT = 16
DATA_OFFSETS = (2, 4, 5, 6)
CHECK_OFFSETS = (0, 1, 3, 7)
DATA_SITES = np.asarray(
    [b * BLOCK_SIZE + o for b in range(BLOCK_COUNT) for o in DATA_OFFSETS],
    dtype=np.int64,
)
CHECK_SITES = np.asarray(
    [b * BLOCK_SIZE + o for b in range(BLOCK_COUNT) for o in CHECK_OFFSETS],
    dtype=np.int64,
)
WORLD_START = 20260926060000
WORLD_COUNT = 8
HEALTHY_STEPS = 1024
POST_STEPS = 32
HORIZONS = (1, 4, 8, 16, 32)
MIX_RULES = np.asarray([90, 150, 110, 22, 30], dtype=np.uint16)

SECDED_METHODS = (
    "RAW64_CODE_PASSIVE",
    "SECDED_NANITE",
    "SECDED_NANITE_QUARANTINE",
)
EXTERNAL_METHOD = "N16_H6_REPAIR"
METHODS = SECDED_METHODS + (EXTERNAL_METHOD,)

LESION_COMPARTMENTS = (0, 2, 4, 6)
LESION_FAMILIES = (
    "SINGLE_DATA1",
    "SINGLE_CHECK1",
    "DOUBLE_ADJ2",
    "CLUSTER3",
    "CLUSTER5",
)


def load_parent():
    path = Path(__file__).resolve().parent / PARENT_NAME
    spec = importlib.util.spec_from_file_location("dg1r04_parent", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def eca_step_mixed(state, rules):
    left = np.roll(state, 1)
    right = np.roll(state, -1)
    idx = (left << 2) | (state << 1) | right
    return ((rules >> idx) & 1).astype(np.uint8)


def mixed_rule_assignment_n(rng, n):
    reps = n // len(MIX_RULES)
    rem = n % len(MIX_RULES)
    arr = np.concatenate(
        (np.tile(MIX_RULES, reps), MIX_RULES[:rem])
    ).astype(np.uint16)
    rng.shuffle(arr)
    return arr


def secded_mapped_positions(rng):
    out = []
    for compartment in range(8):
        start = compartment * 16
        choices = [
            start + off
            for off in (
                2, 4, 5, 6,
                10, 12, 13, 14,
            )
        ]
        out.append(int(rng.choice(np.asarray(choices, dtype=np.int64))))
    return np.asarray(out, dtype=np.int64)


def block_start(index):
    return int(index) * BLOCK_SIZE


def encode_block_from_data(data4):
    d1, d2, d3, d4 = [int(v) & 1 for v in data4]
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p4 = d2 ^ d3 ^ d4
    first7 = np.asarray(
        [p1, p2, d1, p4, d2, d3, d4],
        dtype=np.uint8,
    )
    overall = int(np.bitwise_xor.reduce(first7))
    return np.concatenate(
        (first7, np.asarray([overall], dtype=np.uint8))
    )


def syndrome(block):
    b = block.astype(np.uint8, copy=False)
    s1 = int(b[0] ^ b[2] ^ b[4] ^ b[6])
    s2 = int(b[1] ^ b[2] ^ b[5] ^ b[6])
    s4 = int(b[3] ^ b[4] ^ b[5] ^ b[6])
    syn = s1 + 2 * s2 + 4 * s4
    overall = int(np.bitwise_xor.reduce(b))
    return syn, overall


def reencode_all(state):
    for bi in range(BLOCK_COUNT):
        start = block_start(bi)
        data = state[start + np.asarray(DATA_OFFSETS, dtype=np.int64)]
        state[start:start + BLOCK_SIZE] = encode_block_from_data(data)


def healthy_valid(state):
    for bi in range(BLOCK_COUNT):
        start = block_start(bi)
        syn, overall = syndrome(state[start:start + BLOCK_SIZE])
        if syn != 0 or overall != 0:
            return False
    return True


def init_ecc_telemetry():
    return {
        "single_error_corrections": 0,
        "parity_nanite_corrections": 0,
        "detected_double_errors": 0,
        "syndrome_nonzero_events": 0,
        "quarantine_block_steps": 0,
        "corrections_on_original_lesion": 0,
        "corrections_outside_original_lesion": 0,
    }


def inspect_or_repair_block(
    state,
    bi,
    method,
    telemetry=None,
    lesion_set=None,
):
    start = block_start(bi)
    view = state[start:start + BLOCK_SIZE]
    syn, overall = syndrome(view)

    if telemetry is not None and syn != 0:
        telemetry["syndrome_nonzero_events"] += 1

    if method == "RAW64_CODE_PASSIVE":
        if telemetry is not None and syn != 0 and overall == 0:
            telemetry["detected_double_errors"] += 1
        return False

    if syn != 0 and overall == 1:
        local = syn - 1
        physical = start + local
        state[physical] ^= 1
        if telemetry is not None:
            telemetry["single_error_corrections"] += 1
            if local in (0, 1, 3):
                telemetry["parity_nanite_corrections"] += 1
            if lesion_set is not None and physical in lesion_set:
                telemetry["corrections_on_original_lesion"] += 1
            else:
                telemetry["corrections_outside_original_lesion"] += 1
        return False

    if syn == 0 and overall == 1:
        physical = start + 7
        state[physical] ^= 1
        if telemetry is not None:
            telemetry["single_error_corrections"] += 1
            telemetry["parity_nanite_corrections"] += 1
            if lesion_set is not None and physical in lesion_set:
                telemetry["corrections_on_original_lesion"] += 1
            else:
                telemetry["corrections_outside_original_lesion"] += 1
        return False

    if syn != 0 and overall == 0:
        if telemetry is not None:
            telemetry["detected_double_errors"] += 1
        return method == "SECDED_NANITE_QUARANTINE"

    return False


def evolve_secded_one(
    state,
    bit,
    mapped,
    rules64,
    method,
    telemetry=None,
    lesion_set=None,
):
    quarantined = set()
    for bi in range(BLOCK_COUNT):
        q = inspect_or_repair_block(
            state,
            bi,
            method,
            telemetry=telemetry,
            lesion_set=lesion_set,
        )
        if q:
            quarantined.add(bi)

    if telemetry is not None:
        telemetry["quarantine_block_steps"] += len(quarantined)

    state[mapped] = np.uint8(bit)
    data = state[DATA_SITES].copy()
    candidate = eca_step_mixed(data, rules64)

    if quarantined:
        for bi in quarantined:
            logical = slice(bi * 4, bi * 4 + 4)
            candidate[logical] = data[logical]

    state[DATA_SITES] = candidate
    reencode_all(state)


def initialize_secded_state():
    state = np.zeros(WIDTH, dtype=np.uint8)
    reencode_all(state)
    return state


def evolve_secded_prefix(u, mapped, rules64, method):
    state = initialize_secded_state()
    for t in range(HEALTHY_STEPS):
        evolve_secded_one(
            state,
            int(u[t]),
            mapped,
            rules64,
            method,
            telemetry=None,
            lesion_set=None,
        )
    return state


def secded_unmapped_sibling_block(mapped, compartment):
    start = compartment * 16
    p = int(mapped[compartment])
    return start + 8 if p < start + 8 else start


def secded_lesion(block_start_value, family):
    offsets = {
        "SINGLE_DATA1": (2,),
        "SINGLE_CHECK1": (0,),
        "DOUBLE_ADJ2": (2, 3),
        "CLUSTER3": (2, 3, 4),
        "CLUSTER5": (1, 2, 3, 4, 5),
    }[family]
    return np.asarray(
        [block_start_value + o for o in offsets],
        dtype=np.int64,
    )


def parent_unmapped_sibling_block(mapped, compartment):
    start = compartment * 16
    p = int(mapped[compartment])
    return start + 8 if p < start + 8 else start


def parent_lesion(block_start_value, family):
    offsets = {
        "SINGLE_DATA1": (3,),
        "SINGLE_CHECK1": (2,),
        "DOUBLE_ADJ2": (2, 3),
        "CLUSTER3": (2, 3, 4),
        "CLUSTER5": (1, 2, 3, 4, 5),
    }[family]
    return np.asarray(
        [block_start_value + o for o in offsets],
        dtype=np.int64,
    )


def evolve_parent_prefix(parent, u, mapped, rules128):
    state = np.zeros(parent.WIDTH, dtype=np.uint8)
    for t in range(HEALTHY_STEPS):
        parent.evolve_one_external(
            state,
            int(u[t]),
            mapped,
            rules128,
            EXTERNAL_METHOD,
            telemetry=None,
            record=None,
        )
    return state


def no_damage_control_secded(
    pre,
    u,
    mapped,
    rules64,
    method,
):
    a = pre.copy()
    b = pre.copy()
    max_div = 0.0
    for h in range(1, POST_STEPS + 1):
        bit = int(u[HEALTHY_STEPS + h - 1])
        evolve_secded_one(a, bit, mapped, rules64, method)
        evolve_secded_one(b, bit, mapped, rules64, method)
        max_div = max(max_div, float(np.mean(a != b)))
    return max_div


def no_damage_control_parent(
    parent,
    pre,
    u,
    mapped,
    rules128,
):
    a = pre.copy()
    b = pre.copy()
    max_div = 0.0
    for h in range(1, POST_STEPS + 1):
        bit = int(u[HEALTHY_STEPS + h - 1])
        parent.evolve_one_external(
            a, bit, mapped, rules128, EXTERNAL_METHOD,
            telemetry=None, record=None,
        )
        parent.evolve_one_external(
            b, bit, mapped, rules128, EXTERNAL_METHOD,
            telemetry=None, record=None,
        )
        max_div = max(max_div, float(np.mean(a != b)))
    return max_div


def sustained_recovery_time(flags):
    for h in range(1, len(flags) + 1):
        if all(flags[h - 1:]):
            return h
    return None


def secded_scenario(
    pre,
    u,
    mapped,
    rules64,
    method,
    compartment,
    family,
):
    bstart = secded_unmapped_sibling_block(mapped, compartment)
    lesion = secded_lesion(bstart, family)
    assert not np.any(np.isin(lesion, mapped))

    ref = pre.copy()
    dmg = pre.copy()
    dmg[lesion] ^= 1
    lesion_set = set(int(v) for v in lesion)
    tel = init_ecc_telemetry()

    lesion_block_mask = np.zeros(WIDTH, dtype=bool)
    lesion_block_mask[bstart:bstart + BLOCK_SIZE] = True
    outside_block = ~lesion_block_mask

    whole_curve = []
    data_curve = []
    full_flags = []
    data_flags = []
    horizons = {}

    for h in range(1, POST_STEPS + 1):
        bit = int(u[HEALTHY_STEPS + h - 1])
        evolve_secded_one(
            ref, bit, mapped, rules64, method,
            telemetry=None, lesion_set=None,
        )
        evolve_secded_one(
            dmg, bit, mapped, rules64, method,
            telemetry=tel, lesion_set=lesion_set,
        )

        diff = dmg != ref
        data_diff = diff[DATA_SITES]
        whole = float(np.mean(diff))
        data_div = float(np.mean(data_diff))
        check_div = float(np.mean(diff[CHECK_SITES]))
        block_div = float(np.mean(diff[lesion_block_mask]))
        outside_div = float(np.mean(diff[outside_block]))
        spread = int(np.sum(diff[outside_block]))
        full = bool(not np.any(diff))
        data_full = bool(not np.any(data_diff))

        whole_curve.append(whole)
        data_curve.append(data_div)
        full_flags.append(full)
        data_flags.append(data_full)

        if h in HORIZONS:
            horizons[f"h{h}"] = {
                "whole_state_divergence": whole,
                "data_state_divergence": data_div,
                "check_state_divergence": check_div,
                "lesion_codeword_divergence": block_div,
                "outside_lesion_block_divergence": outside_div,
                "damage_spread_count": spread,
                "exact_full_state_match": full,
                "exact_data_state_match": data_full,
            }

    full_time = sustained_recovery_time(full_flags)
    data_time = sustained_recovery_time(data_flags)

    return {
        "compartment_index": int(compartment),
        "block_start": int(bstart),
        "lesion_family": family,
        "lesion_positions": [int(v) for v in lesion],
        "horizons": horizons,
        "excess_whole_divergence_area": float(np.sum(whole_curve)),
        "excess_data_divergence_area": float(np.sum(data_curve)),
        "sustained_full_recovery": bool(full_time is not None),
        "sustained_data_recovery": bool(data_time is not None),
        "recovery_time_full": None if full_time is None else int(full_time),
        "recovery_time_data": None if data_time is None else int(data_time),
        "ecc_telemetry": {
            **{k: int(v) for k, v in tel.items()},
            "miscorrection_outside_lesion": int(
                tel["corrections_outside_original_lesion"]
            ),
        },
    }


def parent_scenario(
    parent,
    pre,
    u,
    mapped,
    rules128,
    compartment,
    family,
):
    bstart = parent_unmapped_sibling_block(mapped, compartment)
    lesion = parent_lesion(bstart, family)
    assert not np.any(np.isin(lesion, mapped))
    assert not np.any(np.isin(lesion, parent.NANITE_SITES))

    ref = pre.copy()
    dmg = pre.copy()
    dmg[lesion] ^= 1

    lesion_block_mask = np.zeros(parent.WIDTH, dtype=bool)
    lesion_block_mask[bstart:bstart + 8] = True
    outside_block = ~lesion_block_mask
    worker_sites = parent.WORKER_SITES

    whole_curve = []
    data_curve = []
    full_flags = []
    data_flags = []
    horizons = {}

    for h in range(1, POST_STEPS + 1):
        bit = int(u[HEALTHY_STEPS + h - 1])
        parent.evolve_one_external(
            ref, bit, mapped, rules128, EXTERNAL_METHOD,
            telemetry=None, record=None,
        )
        parent.evolve_one_external(
            dmg, bit, mapped, rules128, EXTERNAL_METHOD,
            telemetry=None, record=None,
        )

        diff = dmg != ref
        data_diff = diff[worker_sites]
        whole = float(np.mean(diff))
        data_div = float(np.mean(data_diff))
        check_div = float(np.mean(diff[parent.NANITE_SITES]))
        block_div = float(np.mean(diff[lesion_block_mask]))
        outside_div = float(np.mean(diff[outside_block]))
        spread = int(np.sum(diff[outside_block]))
        full = bool(not np.any(diff))
        data_full = bool(not np.any(data_diff))

        whole_curve.append(whole)
        data_curve.append(data_div)
        full_flags.append(full)
        data_flags.append(data_full)

        if h in HORIZONS:
            horizons[f"h{h}"] = {
                "whole_state_divergence": whole,
                "data_state_divergence": data_div,
                "check_state_divergence": check_div,
                "lesion_codeword_divergence": block_div,
                "outside_lesion_block_divergence": outside_div,
                "damage_spread_count": spread,
                "exact_full_state_match": full,
                "exact_data_state_match": data_full,
            }

    full_time = sustained_recovery_time(full_flags)
    data_time = sustained_recovery_time(data_flags)

    return {
        "compartment_index": int(compartment),
        "block_start": int(bstart),
        "lesion_family": family,
        "lesion_positions": [int(v) for v in lesion],
        "horizons": horizons,
        "excess_whole_divergence_area": float(np.sum(whole_curve)),
        "excess_data_divergence_area": float(np.sum(data_curve)),
        "sustained_full_recovery": bool(full_time is not None),
        "sustained_data_recovery": bool(data_time is not None),
        "recovery_time_full": None if full_time is None else int(full_time),
        "recovery_time_data": None if data_time is None else int(data_time),
        "ecc_telemetry": {
            "single_error_corrections": 0,
            "parity_nanite_corrections": 0,
            "detected_double_errors": 0,
            "syndrome_nonzero_events": 0,
            "quarantine_block_steps": 0,
            "corrections_on_original_lesion": 0,
            "corrections_outside_original_lesion": 0,
            "miscorrection_outside_lesion": 0,
        },
    }


def one_world(parent, seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    u = rng.integers(
        0, 2, size=HEALTHY_STEPS + POST_STEPS,
        dtype=np.uint8,
    )
    mapped = secded_mapped_positions(rng)
    rules64 = mixed_rule_assignment_n(rng, 64)
    rules128 = parent.mixed_rule_assignment(rng)

    methods = {}

    for method in SECDED_METHODS:
        pre = evolve_secded_prefix(
            u, mapped, rules64, method
        )
        valid = healthy_valid(pre)
        control = no_damage_control_secded(
            pre, u, mapped, rules64, method
        )
        scenarios = []
        for compartment in LESION_COMPARTMENTS:
            for family in LESION_FAMILIES:
                scenarios.append(
                    secded_scenario(
                        pre,
                        u,
                        mapped,
                        rules64,
                        method,
                        compartment,
                        family,
                    )
                )
        methods[method] = {
            "healthy_code_valid": bool(valid),
            "no_damage_control_max_divergence": float(control),
            "scenarios": scenarios,
        }

    pre_parent = evolve_parent_prefix(
        parent, u, mapped, rules128
    )
    control_parent = no_damage_control_parent(
        parent, pre_parent, u, mapped, rules128
    )
    scenarios_parent = []
    for compartment in LESION_COMPARTMENTS:
        for family in LESION_FAMILIES:
            scenarios_parent.append(
                parent_scenario(
                    parent,
                    pre_parent,
                    u,
                    mapped,
                    rules128,
                    compartment,
                    family,
                )
            )
    methods[EXTERNAL_METHOD] = {
        "healthy_code_valid": None,
        "no_damage_control_max_divergence": float(control_parent),
        "scenarios": scenarios_parent,
    }

    return {
        "seed": int(seed),
        "mapped_positions": [int(v) for v in mapped],
        "rules64_counts": {
            str(int(r)): int(np.sum(rules64 == r))
            for r in MIX_RULES
        },
        "methods": methods,
    }


def q(values, p):
    return float(
        np.quantile(np.asarray(values, dtype=np.float64), p)
    )


def flatten(rows, method, families=None):
    if families is None:
        family_set = None
    else:
        family_set = set(families)
    out = []
    for row in rows:
        for sc in row["methods"][method]["scenarios"]:
            if family_set is None or sc["lesion_family"] in family_set:
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
            "whole_state_divergence",
            "data_state_divergence",
            "check_state_divergence",
            "lesion_codeword_divergence",
            "outside_lesion_block_divergence",
            "damage_spread_count",
        )
        hrow = {}
        for metric in metrics:
            vals = [sc["horizons"][key][metric] for sc in scenarios]
            hrow[f"{metric}_median"] = q(vals, 0.5)
            hrow[f"{metric}_p90"] = q(vals, 0.90)
        hrow["exact_full_state_match_rate"] = float(
            np.mean([
                sc["horizons"][key]["exact_full_state_match"]
                for sc in scenarios
            ])
        )
        hrow["exact_data_state_match_rate"] = float(
            np.mean([
                sc["horizons"][key]["exact_data_state_match"]
                for sc in scenarios
            ])
        )
        out["horizons"][key] = hrow

    for name in (
        "excess_whole_divergence_area",
        "excess_data_divergence_area",
    ):
        vals = [sc[name] for sc in scenarios]
        out[f"{name}_median"] = q(vals, 0.5)
        out[f"{name}_p90"] = q(vals, 0.90)

    out["sustained_full_recovery_rate"] = float(
        np.mean([sc["sustained_full_recovery"] for sc in scenarios])
    )
    out["sustained_data_recovery_rate"] = float(
        np.mean([sc["sustained_data_recovery"] for sc in scenarios])
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

    telemetry_keys = (
        "single_error_corrections",
        "parity_nanite_corrections",
        "detected_double_errors",
        "syndrome_nonzero_events",
        "quarantine_block_steps",
        "corrections_on_original_lesion",
        "corrections_outside_original_lesion",
        "miscorrection_outside_lesion",
    )
    out["ecc_telemetry"] = {}
    for metric in telemetry_keys:
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


def summarize(rows):
    mechanical_valid = all(
        row["methods"][method]["no_damage_control_max_divergence"] == 0.0
        for row in rows
        for method in METHODS
    )
    healthy_validity = all(
        row["methods"][method]["healthy_code_valid"] is True
        for row in rows
        for method in SECDED_METHODS
    )

    out = {
        "worlds": len(rows),
        "mechanical_valid": bool(mechanical_valid),
        "healthy_secded_valid": bool(healthy_validity),
        "methods": {},
    }

    family_groups = {
        "SINGLE_DATA1": ("SINGLE_DATA1",),
        "SINGLE_CHECK1": ("SINGLE_CHECK1",),
        "SINGLE_COMBINED": ("SINGLE_DATA1", "SINGLE_CHECK1"),
        "DOUBLE_ADJ2": ("DOUBLE_ADJ2",),
        "CLUSTER3": ("CLUSTER3",),
        "CLUSTER5": ("CLUSTER5",),
        "MULTIBIT_STRESS": ("CLUSTER3", "CLUSTER5"),
        "ALL": None,
    }

    for method in METHODS:
        out["methods"][method] = {}
        for label, families in family_groups.items():
            out["methods"][method][label] = summarize_scenarios(
                flatten(rows, method, families)
            )

    passive_single = out["methods"]["RAW64_CODE_PASSIVE"]["SINGLE_COMBINED"]
    secded_single = out["methods"]["SECDED_NANITE"]["SINGLE_COMBINED"]

    single_auc_reduction = relative_reduction(
        secded_single["excess_whole_divergence_area_median"],
        passive_single["excess_whole_divergence_area_median"],
    )
    single_error_reconstruction = bool(
        secded_single["horizons"]["h1"]["data_state_divergence_median"] == 0.0
        and secded_single["horizons"]["h1"]["whole_state_divergence_median"] == 0.0
        and secded_single["sustained_full_recovery_rate"] >= 0.95
        and single_auc_reduction >= 0.90
    )

    passive_double = out["methods"]["RAW64_CODE_PASSIVE"]["DOUBLE_ADJ2"]
    quarantine_double = out["methods"]["SECDED_NANITE_QUARANTINE"]["DOUBLE_ADJ2"]
    double_auc_reduction = relative_reduction(
        quarantine_double["excess_data_divergence_area_median"],
        passive_double["excess_data_divergence_area_median"],
    )
    double_out16_reduction = relative_reduction(
        quarantine_double["horizons"]["h16"][
            "outside_lesion_block_divergence_median"
        ],
        passive_double["horizons"]["h16"][
            "outside_lesion_block_divergence_median"
        ],
    )
    double_error_containment = bool(
        double_auc_reduction >= 0.25
        and double_out16_reduction >= 0.25
        and quarantine_double["ecc_telemetry"][
            "miscorrection_outside_lesion"
        ]["median"] == 0.0
    )

    safe = True
    stress_details = {}
    for family in ("CLUSTER3", "CLUSTER5"):
        passive = out["methods"]["RAW64_CODE_PASSIVE"][family]
        quarantine = out["methods"]["SECDED_NANITE_QUARANTINE"][family]
        secded = out["methods"]["SECDED_NANITE"][family]
        ratio = (
            quarantine["excess_data_divergence_area_median"]
            / (passive["excess_data_divergence_area_median"] + 1e-15)
        )
        q_mis = quarantine["ecc_telemetry"][
            "miscorrection_outside_lesion"
        ]["median"]
        s_mis = secded["ecc_telemetry"][
            "miscorrection_outside_lesion"
        ]["median"]
        ok = ratio <= 1.10 and q_mis <= s_mis + 1.0
        safe = safe and ok
        stress_details[family] = {
            "quarantine_to_passive_data_auc_ratio": float(ratio),
            "quarantine_miscorrection_outside_lesion_median": float(q_mis),
            "secded_miscorrection_outside_lesion_median": float(s_mis),
            "stress_safe": bool(ok),
        }

    out["single_error_auc_reduction_fraction"] = float(single_auc_reduction)
    out["single_error_reconstruction"] = bool(single_error_reconstruction)
    out["double_error_data_auc_reduction_fraction"] = float(double_auc_reduction)
    out["double_error_outside_h16_reduction_fraction"] = float(
        double_out16_reduction
    )
    out["double_error_containment"] = bool(double_error_containment)
    out["multibit_stress_safe"] = bool(safe)
    out["multibit_stress_details"] = stress_details
    out["full_redundancy_aided_repair_signal"] = bool(
        mechanical_valid
        and healthy_validity
        and single_error_reconstruction
        and double_error_containment
    )
    return out


def exhaustive_single_error_control():
    failures = []
    for word in range(16):
        data = np.asarray(
            [(word >> i) & 1 for i in range(4)],
            dtype=np.uint8,
        )
        original = encode_block_from_data(data)
        for bit_index in range(8):
            state = original.copy()
            state[bit_index] ^= 1
            full = np.zeros(WIDTH, dtype=np.uint8)
            full[:8] = state
            telemetry = init_ecc_telemetry()
            inspect_or_repair_block(
                full,
                0,
                "SECDED_NANITE",
                telemetry=telemetry,
                lesion_set={bit_index},
            )
            if not np.array_equal(full[:8], original):
                failures.append({
                    "word": word,
                    "bit_index": bit_index,
                })
    return {
        "cases": 16 * 8,
        "failures": failures,
        "pass": len(failures) == 0,
    }


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
            "world_seconds": float(time.perf_counter() - t0),
        })
        rows.append(row)

    canonical = {
        "schema": (
            "yggdrasil.dg1r-06-local-secded-"
            "nanite-repair.v1"
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
        "schema": "yggdrasil.dg1r-06-runtime-sidecar.v1",
        "rows": runtime_rows,
    }
    return canonical, runtime


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--runtime-out")
    ap.add_argument(
        "--exhaustive-single-error-control",
        action="store_true",
    )
    args = ap.parse_args()

    if args.exhaustive_single_error_control:
        result = exhaustive_single_error_control()
        print(encode(result))
        return

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
