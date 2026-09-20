#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

P11_NAME = "h191_p11_sleep_patch_consolidation_v1.py"
WORLD_START = 20260925300000
WORLD_COUNT = 6


def load_p11():
    path = Path(__file__).resolve().parent / P11_NAME
    spec = importlib.util.spec_from_file_location("h191_p11_base", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def recruit_capability(p10, p11, cap_state, dist_x, pool, rank):
    if rank <= 0 or not pool:
        return []
    rank = min(rank, len(pool))
    x = dist_x[cap_state["capability"]]
    y = cap_state["patch_dist"]
    zpool = p10.gaussian_features(
        x,
        p10.CAND_CENTERS[pool],
        p10.CAND_WIDTHS[pool],
    )
    selected_pos = []
    available = np.ones(len(pool), dtype=bool)
    denom_var = float(np.var(cap_state["pre_dist"])) + 1e-12

    for _ in range(rank):
        best_pos = None
        best_score = None
        for pos in range(len(pool)):
            if not available[pos]:
                continue
            trial = selected_pos + [pos]
            beta = p11.sleep_ridge(zpool[:, trial], y)
            pred = zpool[:, trial] @ beta
            score = float(np.mean((y - pred) ** 2) / denom_var)
            if best_score is None or score < best_score:
                best_score = score
                best_pos = pos
        selected_pos.append(int(best_pos))
        available[best_pos] = False

    return [int(pool[pos]) for pos in selected_pos]


def evaluate_policy(
    p10,
    p11,
    sleep_state,
    developed,
    dist_x,
    held_x,
    held_y,
    supports_by_cap,
    policy_name,
):
    per_cap = []
    total_active = 0
    total_selected = 0
    later_selected = 0
    caps_with_later = 0
    pre_total_active = 0

    for c in sleep_state["caps"]:
        cap = c["capability"]
        selected = list(supports_by_cap[cap])
        birth_patch = list(developed["supports"][cap][8:])
        birth_set = set(birth_patch)
        pre_total_active += len(birth_patch)

        if selected:
            zd = p10.gaussian_features(
                dist_x[cap],
                p10.CAND_CENTERS[selected],
                p10.CAND_WIDTHS[selected],
            )
            zh = p10.gaussian_features(
                held_x[cap],
                p10.CAND_CENTERS[selected],
                p10.CAND_WIDTHS[selected],
            )
            beta = p11.sleep_ridge(zd, c["patch_dist"])
            patch_dist = zd @ beta
            patch_held = zh @ beta
            nonzero_mask = np.abs(beta) > p11.ACTIVE_ZERO
            nonzero = int(np.sum(nonzero_mask))
            active_factors = [
                int(selected[i])
                for i in range(len(selected))
                if nonzero_mask[i]
            ]
        else:
            beta = np.empty(0, dtype=np.float64)
            patch_dist = np.zeros_like(c["patch_dist"])
            patch_held = np.zeros_like(c["patch_held"])
            nonzero = 0
            active_factors = []

        post_dist = c["core_dist"] + patch_dist
        post_held = c["core_held"] + patch_held
        dist_mismatch = p11.normalized_prediction_mismatch(
            post_dist, c["pre_dist"]
        )
        held_mismatch = p11.normalized_prediction_mismatch(
            post_held, c["pre_held"]
        )
        task_post = p10.nmse(post_held, held_y[cap])

        later = [f for f in active_factors if f not in birth_set]
        if later:
            caps_with_later += 1
        later_selected += len(later)
        total_active += nonzero
        total_selected += len(active_factors)

        per_cap.append({
            "capability": int(cap),
            "birth_patch_count": int(len(birth_patch)),
            "selected_patch_count": int(len(selected)),
            "active_patch_count": int(nonzero),
            "selected_patch_factors": [int(v) for v in selected],
            "active_patch_factors": active_factors,
            "later_born_active_factors": later,
            "dist_prediction_mismatch": float(dist_mismatch),
            "held_prediction_mismatch": float(held_mismatch),
            "task_held_nmse_pre": float(c["pre_task_held_nmse"]),
            "task_held_nmse_post": float(task_post),
            "task_held_nmse_delta": float(task_post - c["pre_task_held_nmse"]),
            "pre_residual_ops": int(c["pre_residual_ops"]),
            "post_residual_ops": int(16 + 2 * nonzero),
        })

    held_vals = [x["held_prediction_mismatch"] for x in per_cap]
    dist_vals = [x["dist_prediction_mismatch"] for x in per_cap]
    task_delta = [x["task_held_nmse_delta"] for x in per_cap]
    reduction = (
        float((pre_total_active - total_active) / pre_total_active)
        if pre_total_active > 0 else 0.0
    )

    return {
        "policy": policy_name,
        "shared_patch_geometry_count": int(sleep_state["patch_factor_count"]),
        "total_active_patch_coefficients": int(total_active),
        "total_routing_indices": int(total_selected),
        "pre_total_active_patch_factors": int(pre_total_active),
        "active_patch_count_reduction_fraction": reduction,
        "capability_median_held_mismatch": float(np.median(held_vals)),
        "world_mean_held_mismatch": float(np.mean(held_vals)),
        "world_worst_held_mismatch": float(np.max(held_vals)),
        "world_mean_dist_mismatch": float(np.mean(dist_vals)),
        "world_worst_dist_mismatch": float(np.max(dist_vals)),
        "world_mean_task_nmse_delta": float(np.mean(task_delta)),
        "oldest_cap_post_ops": int(per_cap[0]["post_residual_ops"]),
        "median_cap_post_ops": float(np.median([x["post_residual_ops"] for x in per_cap])),
        "newest_cap_post_ops": int(per_cap[-1]["post_residual_ops"]),
        "total_active_patch_evaluations": int(total_active),
        "capabilities_using_later_born_patch_fraction": float(caps_with_later / len(per_cap)),
        "later_born_patch_selection_fraction": float(later_selected / total_selected) if total_selected else 0.0,
        "core_decoder_max_abs_change": 0.0,
        "per_capability": per_cap,
    }


def one_world(p11, seed):
    p10 = p11.load_p10()
    dist_x, held_x, dist_y, held_y = p10.build_world_data(seed)
    developed = p11.develop_presleep(p10, dist_x, held_x, dist_y)
    sleep_state = p11.build_sleep_state(
        p10, developed, dist_x, held_x, held_y
    )
    sleep_state["core_support"] = list(developed["core_support"])
    global_pool = list(sleep_state["patch_factors"])

    control_supports = {}
    half_supports = {}
    minus1_supports = {}

    for c in sleep_state["caps"]:
        cap = c["capability"]
        birth_patch = list(developed["supports"][cap][8:])
        b = len(birth_patch)
        control_supports[cap] = birth_patch
        k_half = 0 if b == 0 else max(1, b // 2)
        k_minus1 = max(0, b - 1)
        max_rank = max(k_half, k_minus1)
        nested = recruit_capability(
            p10, p11, c, dist_x, global_pool, max_rank
        )
        half_supports[cap] = nested[:k_half]
        minus1_supports[cap] = nested[:k_minus1]

    control = evaluate_policy(
        p10, p11, sleep_state, developed,
        dist_x, held_x, held_y,
        control_supports, "ORIGINAL_BIRTH_RECODE",
    )
    half = evaluate_policy(
        p10, p11, sleep_state, developed,
        dist_x, held_x, held_y,
        half_supports, "HALF_ACTIVE",
    )
    minus1 = evaluate_policy(
        p10, p11, sleep_state, developed,
        dist_x, held_x, held_y,
        minus1_supports, "MINUS1_ACTIVE",
    )

    pre_active = sum(max(0, len(developed["supports"][i]) - 8) for i in range(12))
    pre_ops = [2 * len(developed["supports"][i]) for i in range(12)]

    return {
        "seed": int(seed),
        "pre_sleep": {
            "patch_geometry_count": int(len(global_pool)),
            "patch_factors": [int(v) for v in global_pool],
            "total_active_patch_factors": int(pre_active),
            "total_patch_decoder_scalars": int(pre_active),
            "oldest_cap_ops": int(pre_ops[0]),
            "median_cap_ops": float(np.median(pre_ops)),
            "newest_cap_ops": int(pre_ops[-1]),
        },
        "ORIGINAL_BIRTH_RECODE": control,
        "HALF_ACTIVE": half,
        "MINUS1_ACTIVE": minus1,
    }


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def policy_summary(rows, name):
    pr = [r[name] for r in rows]
    return {
        "world_count": len(pr),
        "capability_median_held_mismatch_median": q([x["capability_median_held_mismatch"] for x in pr], 0.5),
        "world_mean_held_mismatch_median": q([x["world_mean_held_mismatch"] for x in pr], 0.5),
        "world_worst_held_mismatch_median": q([x["world_worst_held_mismatch"] for x in pr], 0.5),
        "world_worst_held_mismatch_p90": q([x["world_worst_held_mismatch"] for x in pr], 0.90),
        "world_mean_dist_mismatch_median": q([x["world_mean_dist_mismatch"] for x in pr], 0.5),
        "world_mean_task_nmse_delta_median": q([x["world_mean_task_nmse_delta"] for x in pr], 0.5),
        "shared_patch_geometry_count_median": q([x["shared_patch_geometry_count"] for x in pr], 0.5),
        "total_active_patch_coefficients_median": q([x["total_active_patch_coefficients"] for x in pr], 0.5),
        "total_routing_indices_median": q([x["total_routing_indices"] for x in pr], 0.5),
        "active_patch_count_reduction_fraction_median": q([x["active_patch_count_reduction_fraction"] for x in pr], 0.5),
        "oldest_cap_post_ops_median": q([x["oldest_cap_post_ops"] for x in pr], 0.5),
        "median_cap_post_ops_median": q([x["median_cap_post_ops"] for x in pr], 0.5),
        "newest_cap_post_ops_median": q([x["newest_cap_post_ops"] for x in pr], 0.5),
        "total_active_patch_evaluations_median": q([x["total_active_patch_evaluations"] for x in pr], 0.5),
        "capabilities_using_later_born_patch_fraction_median": q([x["capabilities_using_later_born_patch_fraction"] for x in pr], 0.5),
        "later_born_patch_selection_fraction_median": q([x["later_born_patch_selection_fraction"] for x in pr], 0.5),
        "core_decoder_max_abs_change": float(np.max([x["core_decoder_max_abs_change"] for x in pr])),
    }


def summarize(rows):
    control = policy_summary(rows, "ORIGINAL_BIRTH_RECODE")
    half = policy_summary(rows, "HALF_ACTIVE")
    minus1 = policy_summary(rows, "MINUS1_ACTIVE")
    pre_total = q([r["pre_sleep"]["total_active_patch_factors"] for r in rows], 0.5)
    pre_newest = q([r["pre_sleep"]["newest_cap_ops"] for r in rows], 0.5)

    control_pass = bool(control["world_worst_held_mismatch_median"] <= 1e-10)
    half_strong = bool(
        control_pass
        and half["world_mean_held_mismatch_median"] <= 0.01
        and half["world_worst_held_mismatch_median"] <= 0.02
        and half["world_worst_held_mismatch_p90"] <= 0.05
        and half["active_patch_count_reduction_fraction_median"] >= 0.40
        and half["core_decoder_max_abs_change"] == 0.0
        and half["total_active_patch_evaluations_median"] < pre_total
        and half["newest_cap_post_ops_median"] <= pre_newest
    )
    minus1_useful = bool(
        control_pass
        and not half_strong
        and minus1["world_mean_held_mismatch_median"] <= 0.01
        and minus1["world_worst_held_mismatch_median"] <= 0.02
        and minus1["active_patch_count_reduction_fraction_median"] > 0.0
        and minus1["core_decoder_max_abs_change"] == 0.0
        and minus1["total_active_patch_evaluations_median"] < pre_total
    )

    if not control_pass:
        classification = "MECHANICALLY_INVALID"
    elif half_strong:
        classification = "HALF_ACTIVE_STRONG_HIBERNATION"
    elif minus1_useful:
        classification = "MINUS1_ACTIVE_USEFUL_HIBERNATION"
    else:
        classification = "NEGATIVE_CONDITIONAL_ROUTING"

    return {
        "worlds": len(rows),
        "classification": classification,
        "control_pass": control_pass,
        "half_strong": half_strong,
        "minus1_useful": minus1_useful,
        "pre_sleep_patch_geometry_count_median": q([r["pre_sleep"]["patch_geometry_count"] for r in rows], 0.5),
        "pre_sleep_total_active_patch_factors_median": pre_total,
        "pre_sleep_oldest_cap_ops_median": q([r["pre_sleep"]["oldest_cap_ops"] for r in rows], 0.5),
        "pre_sleep_median_cap_ops_median": q([r["pre_sleep"]["median_cap_ops"] for r in rows], 0.5),
        "pre_sleep_newest_cap_ops_median": pre_newest,
        "ORIGINAL_BIRTH_RECODE": control,
        "HALF_ACTIVE": half,
        "MINUS1_ACTIVE": minus1,
    }


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    p11 = load_p11()
    rows = [one_world(p11, WORLD_START + i) for i in range(WORLD_COUNT)]
    return {
        "schema": "yggdrasil.h191-p12-sleep-patch-hibernation-routing.v1",
        "rows": rows,
        "summary": summarize(rows),
        "worlds": len(rows),
        "seed_start": WORLD_START,
        "seed_end": WORLD_START + WORLD_COUNT - 1,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    obj = run()
    raw = (encode(obj) + "\n").encode("utf-8")
    Path(args.out).write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    print(encode({
        "output": args.out,
        "sha256": digest,
        "summary": obj["summary"],
        "worlds": obj["worlds"],
    }))


if __name__ == "__main__":
    main()
