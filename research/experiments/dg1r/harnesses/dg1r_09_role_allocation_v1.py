#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
import time
from pathlib import Path

import numpy as np

PARENT_NAME = "dg1r_08_redeployment_v1.py"
WORKERS = 103
MAINT_BITS = 25
DEV_STEPS = 512
SEQ_LEN = 4096
REPAIR_PRE = 1024
REPAIR_POST = 32
WORLD_START = 20260926090000
WORLD_COUNT = 8
HORIZONS = (1, 4, 8, 16, 32)
METHODS = (
    "UNIFORM103",
    "RANDOM_ROLE103",
    "PERIODIC_ROLE103",
    "DEVELOPMENTAL_ROLE103",
)
PROCESSOR = 0
RETENTION = 1
RELAY = 2
ROLE_NAMES = {
    PROCESSOR: "PROCESSOR",
    RETENTION: "RETENTION",
    RELAY: "RELAY",
}
RETENTION_COUNT = 26
RELAY_COUNT = 26
PROCESSOR_COUNT = 51


def load_parent():
    path = Path(__file__).resolve().parent / PARENT_NAME
    spec = importlib.util.spec_from_file_location("dg1r08_parent", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rule90_step(state):
    left = np.roll(state, 1)
    right = np.roll(state, -1)
    return (left ^ right).astype(np.uint8)


def initialize_state(parent):
    workers = np.zeros(WORKERS, dtype=np.uint8)
    maint = np.zeros(MAINT_BITS, dtype=np.uint8)
    parent.encode_all(workers, maint)
    return workers, maint


def scan_clean(parent, workers, maint, control=None, telemetry=None):
    if telemetry is None:
        telemetry = parent.empty_telemetry()
    before = dict(telemetry)
    event = parent.scan_and_repair(workers, maint, telemetry)
    if control is not None and event:
        control["clean"] = False
        control["pre_step_events"] += 1
    if control is not None:
        control["syndrome_detections"] += (
            telemetry["syndrome_detections"] - before["syndrome_detections"]
        )
        control["out_of_range_syndromes"] += (
            telemetry["out_of_range_syndromes"] - before["out_of_range_syndromes"]
        )
    return telemetry


def uniform_step(parent, workers, maint, bit, mapped, rules, control=None):
    scan_clean(parent, workers, maint, control=control)
    workers[mapped] = np.uint8(bit)
    workers[:] = parent.eca_step_mixed(workers, rules)
    parent.encode_all(workers, maint)


def role_step(
    parent,
    workers,
    maint,
    bit,
    mapped,
    rules,
    roles,
    external_step,
    control=None,
    telemetry=None,
):
    telemetry = scan_clean(
        parent, workers, maint, control=control, telemetry=telemetry
    )
    workers[mapped] = np.uint8(bit)
    mixed_candidate = parent.eca_step_mixed(workers, rules)
    relay_candidate = rule90_step(workers)
    out = workers.copy()

    processor_mask = roles == PROCESSOR
    relay_mask = roles == RELAY
    retention_mask = roles == RETENTION
    out[processor_mask] = mixed_candidate[processor_mask]
    out[relay_mask] = relay_candidate[relay_mask]
    if external_step % 4 == 3:
        out[retention_mask] = mixed_candidate[retention_mask]

    workers[:] = out
    parent.encode_all(workers, maint)
    return telemetry


def developmental_prefix(parent, dev_u, mapped, rules):
    workers, maint = initialize_state(parent)
    trace = np.empty((DEV_STEPS, WORKERS), dtype=np.uint8)
    control = {
        "clean": True,
        "pre_step_events": 0,
        "syndrome_detections": 0,
        "out_of_range_syndromes": 0,
    }
    previous = workers.copy()
    flips = np.zeros(WORKERS, dtype=np.float64)
    ones = np.zeros(WORKERS, dtype=np.float64)
    disagreement = np.zeros(WORKERS, dtype=np.float64)

    for t, bit in enumerate(dev_u):
        uniform_step(parent, workers, maint, int(bit), mapped, rules, control)
        trace[t] = workers
        flips += workers != previous
        ones += workers
        disagreement += 0.5 * (
            (workers != np.roll(workers, 1)).astype(np.float64)
            + (workers != np.roll(workers, -1)).astype(np.float64)
        )
        previous = workers.copy()

    metrics = {
        "flip_rate": flips / DEV_STEPS,
        "one_fraction": ones / DEV_STEPS,
        "local_disagreement": disagreement / DEV_STEPS,
    }
    return workers, maint, metrics, control


def blank_roles():
    return np.full(WORKERS, PROCESSOR, dtype=np.int8)


def random_roles(permutation):
    roles = blank_roles()
    roles[permutation[:RETENTION_COUNT]] = RETENTION
    roles[permutation[RETENTION_COUNT:RETENTION_COUNT + RELAY_COUNT]] = RELAY
    return roles


def periodic_roles():
    roles = blank_roles()
    retention = [i for i in range(WORKERS) if i % 4 == 0][:RETENTION_COUNT]
    roles[retention] = RETENTION
    relay_candidates = [
        i for i in range(WORKERS)
        if roles[i] == PROCESSOR and i % 4 == 2
    ]
    if len(relay_candidates) < RELAY_COUNT:
        relay_candidates.extend(
            i for i in range(WORKERS)
            if roles[i] == PROCESSOR and i not in relay_candidates
        )
    relay = relay_candidates[:RELAY_COUNT]
    roles[relay] = RELAY
    return roles


def developmental_roles(metrics):
    roles = blank_roles()
    persistence = 1.0 - metrics["flip_rate"]
    relay_score = metrics["flip_rate"] * (
        0.5 + metrics["local_disagreement"]
    )
    indices = list(range(WORKERS))
    retention = sorted(indices, key=lambda i: (-persistence[i], i))[:RETENTION_COUNT]
    roles[retention] = RETENTION
    remaining = [i for i in indices if roles[i] == PROCESSOR]
    relay = sorted(remaining, key=lambda i: (-relay_score[i], i))[:RELAY_COUNT]
    roles[relay] = RELAY
    return roles


def roles_for(method, permutation, metrics):
    if method == "UNIFORM103":
        return blank_roles()
    if method == "RANDOM_ROLE103":
        return random_roles(permutation)
    if method == "PERIODIC_ROLE103":
        return periodic_roles()
    if method == "DEVELOPMENTAL_ROLE103":
        return developmental_roles(metrics)
    raise ValueError(method)


def role_telemetry(roles, metrics, mapped):
    out = {
        "counts": {},
        "mean_flip_rate": {},
        "mean_one_fraction": {},
        "mean_local_disagreement": {},
        "mapped_fraction": {},
        "post_freeze_role_transition_count": 0,
    }
    for role in (PROCESSOR, RETENTION, RELAY):
        name = ROLE_NAMES[role]
        mask = roles == role
        out["counts"][name] = int(np.sum(mask))
        out["mean_flip_rate"][name] = float(np.mean(metrics["flip_rate"][mask])) if np.any(mask) else 0.0
        out["mean_one_fraction"][name] = float(np.mean(metrics["one_fraction"][mask])) if np.any(mask) else 0.0
        out["mean_local_disagreement"][name] = float(np.mean(metrics["local_disagreement"][mask])) if np.any(mask) else 0.0
        out["mapped_fraction"][name] = float(np.mean(roles[mapped] == role))
    return out


def capability_trace(
    parent,
    start_w,
    start_m,
    eval_u,
    mapped,
    rules,
    roles,
):
    workers = start_w.copy()
    maint = start_m.copy()
    x = np.empty((SEQ_LEN, WORKERS), dtype=np.uint8)
    control = {
        "clean": True,
        "pre_step_events": 0,
        "syndrome_detections": 0,
        "out_of_range_syndromes": 0,
    }
    for t, bit in enumerate(eval_u):
        role_step(
            parent, workers, maint, int(bit), mapped, rules,
            roles, t, control=control,
        )
        x[t] = workers
    return x, control


def repair_prefix(
    parent,
    start_w,
    start_m,
    eval_u,
    mapped,
    rules,
    roles,
):
    workers = start_w.copy()
    maint = start_m.copy()
    control = {
        "clean": True,
        "pre_step_events": 0,
        "syndrome_detections": 0,
        "out_of_range_syndromes": 0,
    }
    for t in range(REPAIR_PRE):
        role_step(
            parent, workers, maint, int(eval_u[t]), mapped, rules,
            roles, t, control=control,
        )
    return workers, maint, control


def lesion_workers(base, lesion_size):
    offsets = (2, 3, 4) if lesion_size == "SMALL3" else (1, 2, 3, 4, 5)
    return np.asarray([base + off for off in offsets], dtype=np.int64)


def no_damage_control(parent, pre_w, pre_m, eval_u, mapped, rules, roles):
    wa, ma = pre_w.copy(), pre_m.copy()
    wb, mb = pre_w.copy(), pre_m.copy()
    max_div = 0.0
    for h in range(1, REPAIR_POST + 1):
        t = REPAIR_PRE + h - 1
        bit = int(eval_u[t])
        role_step(parent, wa, ma, bit, mapped, rules, roles, t)
        role_step(parent, wb, mb, bit, mapped, rules, roles, t)
        a = np.concatenate((wa, ma))
        b = np.concatenate((wb, mb))
        max_div = max(max_div, float(np.mean(a != b)))
    return float(max_div)


def repair_scenario(
    parent,
    pre_w,
    pre_m,
    eval_u,
    mapped,
    rules,
    roles,
    base,
    lesion_size,
):
    lesion = lesion_workers(base, lesion_size)
    assert not np.any(np.isin(lesion, mapped))
    rw, rm = pre_w.copy(), pre_m.copy()
    dw, dm = pre_w.copy(), pre_m.copy()
    dw[lesion] ^= 1
    ref_tel = parent.empty_telemetry()
    dmg_tel = parent.empty_telemetry()
    horizons = {}
    area = []

    for h in range(1, REPAIR_POST + 1):
        t = REPAIR_PRE + h - 1
        bit = int(eval_u[t])
        ref_tel = role_step(
            parent, rw, rm, bit, mapped, rules, roles, t,
            telemetry=ref_tel,
        )
        dmg_tel = role_step(
            parent, dw, dm, bit, mapped, rules, roles, t,
            telemetry=dmg_tel,
        )
        wdiff = dw != rw
        fdiff = np.concatenate((dw, dm)) != np.concatenate((rw, rm))
        area.append(float(np.mean(wdiff)))
        if h in HORIZONS:
            horizons[f"h{h}"] = {
                "exact_worker_recovery": bool(not np.any(wdiff)),
                "exact_full_recovery": bool(not np.any(fdiff)),
                "worker_divergence": float(np.mean(wdiff)),
            }

    return {
        "lesion_base": int(base),
        "lesion_size": lesion_size,
        "horizons": horizons,
        "worker_divergence_area": float(np.sum(area)),
        "telemetry_delta": {
            key: int(dmg_tel[key] - ref_tel[key])
            for key in dmg_tel
        },
    }


def one_world(parent, seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    dev_u = rng.integers(0, 2, size=DEV_STEPS, dtype=np.uint8)
    eval_u = rng.integers(0, 2, size=SEQ_LEN, dtype=np.uint8)
    mapped = parent.mapped_positions(rng)
    rules = parent.mixed_rule_assignment_103(rng)
    permutation = rng.permutation(WORKERS)
    targets = parent.build_targets(eval_u)

    dev_w, dev_m, metrics, dev_control = developmental_prefix(
        parent, dev_u, mapped, rules
    )

    methods = {}
    for method in METHODS:
        roles = roles_for(method, permutation, metrics)
        tel = role_telemetry(roles, metrics, mapped)
        x, cap_control = capability_trace(
            parent, dev_w, dev_m, eval_u, mapped, rules, roles
        )
        capability = parent.capability_metrics(x, targets)
        pre_w, pre_m, repair_control = repair_prefix(
            parent, dev_w, dev_m, eval_u, mapped, rules, roles
        )
        nd = no_damage_control(
            parent, pre_w, pre_m, eval_u, mapped, rules, roles
        )
        scenarios = []
        for base in parent.LESION_BASES:
            for lesion_size in parent.LESION_SIZES:
                scenarios.append(
                    repair_scenario(
                        parent, pre_w, pre_m, eval_u, mapped, rules,
                        roles, base, lesion_size,
                    )
                )
        methods[method] = {
            "roles": [int(v) for v in roles],
            "role_telemetry": tel,
            "capability": capability,
            "capability_encoding_control": cap_control,
            "repair_encoding_control": repair_control,
            "no_damage_control_max_divergence": nd,
            "scenarios": scenarios,
        }

    return {
        "seed": int(seed),
        "mapped_positions": [int(v) for v in mapped],
        "development_encoding_control": dev_control,
        "methods": methods,
    }


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def flatten_scenarios(rows, method, lesion_size=None):
    out = []
    for row in rows:
        for sc in row["methods"][method]["scenarios"]:
            if lesion_size is None or sc["lesion_size"] == lesion_size:
                out.append(sc)
    return out


def summarize_repair(scenarios):
    out = {"scenario_count": len(scenarios), "horizons": {}}
    for h in HORIZONS:
        key = f"h{h}"
        ew = [sc["horizons"][key]["exact_worker_recovery"] for sc in scenarios]
        ef = [sc["horizons"][key]["exact_full_recovery"] for sc in scenarios]
        wd = [sc["horizons"][key]["worker_divergence"] for sc in scenarios]
        out["horizons"][key] = {
            "exact_worker_recovery_rate": float(np.mean(ew)),
            "exact_full_recovery_rate": float(np.mean(ef)),
            "worker_divergence_median": q(wd, 0.5),
        }
    area = [sc["worker_divergence_area"] for sc in scenarios]
    out["worker_divergence_area_median"] = q(area, 0.5)
    for key in (
        "syndrome_detections",
        "corrected_data_bits",
        "corrected_parity_bits",
        "out_of_range_syndromes",
    ):
        vals = [sc["telemetry_delta"][key] for sc in scenarios]
        out.setdefault("telemetry_delta", {})[key] = {
            "median": q(vals, 0.5),
            "p90": q(vals, 0.90),
        }
    return out


def summarize_capability(rows, method, parent):
    caps = [row["methods"][method]["capability"] for row in rows]
    tasks = {}
    for task in parent.TASKS:
        vals = [c["tasks"][task] for c in caps]
        tasks[task] = {"median": q(vals, 0.5), "p10": q(vals, 0.10)}
    return {
        "tasks": tasks,
        "memory_score": {
            "median": q([c["memory_score"] for c in caps], 0.5),
            "p10": q([c["memory_score"] for c in caps], 0.10),
        },
        "nonlinear_score": {
            "median": q([c["nonlinear_score"] for c in caps], 0.5),
            "p10": q([c["nonlinear_score"] for c in caps], 0.10),
        },
        "state_entropy": {
            "median": q([c["state_entropy"] for c in caps], 0.5),
            "p10": q([c["state_entropy"] for c in caps], 0.10),
        },
        "feature_rank": {
            "median": q([c["feature_rank"] for c in caps], 0.5),
            "p10": q([c["feature_rank"] for c in caps], 0.10),
        },
        "feature_rank_fraction": {
            "median": q([c["feature_rank_fraction"] for c in caps], 0.5),
            "p10": q([c["feature_rank_fraction"] for c in caps], 0.10),
        },
    }


def summarize_roles(rows, method):
    out = {"counts": {}, "mean_flip_rate": {}, "mean_local_disagreement": {}, "mapped_fraction": {}}
    for role in (PROCESSOR, RETENTION, RELAY):
        name = ROLE_NAMES[role]
        for field in ("counts", "mean_flip_rate", "mean_local_disagreement", "mapped_fraction"):
            vals = [row["methods"][method]["role_telemetry"][field][name] for row in rows]
            out[field][name] = {"median": q(vals, 0.5), "p10": q(vals, 0.10)}
    out["post_freeze_role_transition_count_max"] = int(max(
        row["methods"][method]["role_telemetry"]["post_freeze_role_transition_count"]
        for row in rows
    ))
    return out


def paired_delta(rows, a, b, key):
    vals = [
        row["methods"][a]["capability"][key]
        - row["methods"][b]["capability"][key]
        for row in rows
    ]
    return {"median": q(vals, 0.5), "p10": q(vals, 0.10)}


def repair_preserved(summary_method, no_damage, encoding):
    return bool(
        summary_method["SMALL3"]["horizons"]["h1"]["exact_full_recovery_rate"] >= 0.95
        and summary_method["LARGE5"]["horizons"]["h1"]["exact_full_recovery_rate"] >= 0.95
        and summary_method["COMBINED"]["horizons"]["h32"]["exact_full_recovery_rate"] >= 0.95
        and no_damage
        and encoding
    )


def summarize(rows, parent):
    development_clean = all(row["development_encoding_control"]["clean"] for row in rows)
    out = {"worlds": len(rows), "development_encoding_control_pass": bool(development_clean), "methods": {}}

    for method in METHODS:
        no_damage = all(row["methods"][method]["no_damage_control_max_divergence"] == 0.0 for row in rows)
        encoding = all(
            row["methods"][method]["capability_encoding_control"]["clean"]
            and row["methods"][method]["repair_encoding_control"]["clean"]
            for row in rows
        ) and development_clean
        sm = {
            "capability": summarize_capability(rows, method, parent),
            "roles": summarize_roles(rows, method),
            "no_damage_control_pass": bool(no_damage),
            "encoding_control_pass": bool(encoding),
            "SMALL3": summarize_repair(flatten_scenarios(rows, method, "SMALL3")),
            "LARGE5": summarize_repair(flatten_scenarios(rows, method, "LARGE5")),
            "COMBINED": summarize_repair(flatten_scenarios(rows, method, None)),
        }
        sm["repair_preserved"] = repair_preserved(sm, no_damage, encoding)
        out["methods"][method] = sm

    comparisons = {
        "random_minus_uniform": {},
        "periodic_minus_random": {},
        "developmental_minus_random": {},
        "developmental_minus_uniform": {},
    }
    for label, a, b in (
        ("random_minus_uniform", "RANDOM_ROLE103", "UNIFORM103"),
        ("periodic_minus_random", "PERIODIC_ROLE103", "RANDOM_ROLE103"),
        ("developmental_minus_random", "DEVELOPMENTAL_ROLE103", "RANDOM_ROLE103"),
        ("developmental_minus_uniform", "DEVELOPMENTAL_ROLE103", "UNIFORM103"),
    ):
        comparisons[label]["memory_score"] = paired_delta(rows, a, b, "memory_score")
        comparisons[label]["nonlinear_score"] = paired_delta(rows, a, b, "nonlinear_score")
        comparisons[label]["feature_rank"] = paired_delta(rows, a, b, "feature_rank")
    out["paired_comparisons"] = comparisons

    rnd = comparisons["random_minus_uniform"]
    per = comparisons["periodic_minus_random"]
    devr = comparisons["developmental_minus_random"]
    devu = comparisons["developmental_minus_uniform"]
    rnd_ok = out["methods"]["RANDOM_ROLE103"]["repair_preserved"]
    per_ok = out["methods"]["PERIODIC_ROLE103"]["repair_preserved"]
    dev_ok = out["methods"]["DEVELOPMENTAL_ROLE103"]["repair_preserved"]

    out["heterogeneity_gain"] = bool(
        rnd_ok
        and rnd["memory_score"]["median"] >= -0.05
        and rnd["nonlinear_score"]["median"] >= -0.05
        and (rnd["memory_score"]["median"] >= 0.02 or rnd["nonlinear_score"]["median"] >= 0.02)
    )
    out["spatial_mixing_gain"] = bool(
        per_ok
        and per["memory_score"]["median"] >= -0.05
        and per["nonlinear_score"]["median"] >= -0.05
        and (per["memory_score"]["median"] >= 0.02 or per["nonlinear_score"]["median"] >= 0.02)
    )
    out["developmental_placement_gain"] = bool(
        dev_ok
        and devr["memory_score"]["median"] >= -0.05
        and devr["nonlinear_score"]["median"] >= -0.05
        and (devr["memory_score"]["median"] >= 0.02 or devr["nonlinear_score"]["median"] >= 0.02)
    )
    dev_cap = out["methods"]["DEVELOPMENTAL_ROLE103"]["capability"]
    out["functional_specialization_signal"] = bool(
        dev_ok
        and devu["memory_score"]["median"] >= -0.05
        and devu["nonlinear_score"]["median"] >= -0.05
        and (devu["memory_score"]["median"] >= 0.03 or devu["nonlinear_score"]["median"] >= 0.03)
        and dev_cap["state_entropy"]["median"] >= 0.20
    )
    out["long_memory_signal"] = bool(
        dev_cap["tasks"]["D16"]["median"] >= 0.60
        or dev_cap["tasks"]["D32"]["median"] >= 0.60
    )
    out["strong_developmental_role_signal"] = bool(
        out["functional_specialization_signal"]
        and out["developmental_placement_gain"]
    )
    return out


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    parent = load_parent()
    rows = [one_world(parent, WORLD_START + i) for i in range(WORLD_COUNT)]
    return {
        "schema": "yggdrasil.dg1r-09-developmental-role-allocation.v1",
        "rows": rows,
        "summary": summarize(rows, parent),
        "worlds": len(rows),
        "seed_start": WORLD_START,
        "seed_end": WORLD_START + WORLD_COUNT - 1,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--runtime-out")
    args = ap.parse_args()
    t0 = time.perf_counter()
    obj = run()
    elapsed = float(time.perf_counter() - t0)
    raw = (encode(obj) + "
").encode("utf-8")
    Path(args.out).write_bytes(raw)
    if args.runtime_out:
        Path(args.runtime_out).write_text(
            json.dumps(
                {"schema": "yggdrasil.dg1r-09-runtime-sidecar.v1", "seconds": elapsed},
                sort_keys=True,
                indent=2,
            ) + "
",
            encoding="utf-8",
        )
    print(encode({
        "output": args.out,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "summary": obj["summary"],
        "worlds": obj["worlds"],
    }))


if __name__ == "__main__":
    main()
