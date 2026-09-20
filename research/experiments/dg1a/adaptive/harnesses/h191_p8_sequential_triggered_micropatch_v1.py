#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

P7_NAME = "h191_p7_bounded_shared_core_micropatch_v1.py"
WORLD_START = 20260924900000
WORLD_COUNT = 8
TRIGGER_NMSE = 0.02
OLD_CAPS = (0, 1, 2)
ADDITION_ORDER = (3, 4, 5, 6, 7)
STAGE_LABELS = ("CAP4", "CAP5", "CAP6", "CAP7", "CAP8")


def load_p7():
    path = Path(__file__).resolve().parent / P7_NAME
    spec = importlib.util.spec_from_file_location("h191_p7_base", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def decoder_predictions(p6, p5, base, support, beta, xd, xh):
    pd = p6.predict_decoder(p5, base, xd, beta, support)
    ph = p6.predict_decoder(p5, base, xh, beta, support)
    return pd, ph


def evaluate_joint_refit(p6, p5, base, dist_x, held_x, dist_y, held_y, active):
    support = p6.recruit_support(p5, base, dist_x, dist_y, tuple(active))
    held_nmse = {}
    dist_nmse = {}
    for i in active:
        beta = p6.fit_decoder(p5, base, dist_x[i], dist_y[i], support)
        pd, ph = decoder_predictions(
            p6, p5, base, support, beta, dist_x[i], held_x[i]
        )
        dist_nmse[i] = base.nmse(pd, dist_y[i])
        held_nmse[i] = base.nmse(ph, held_y[i])
    vals = [held_nmse[i] for i in active]
    return {
        "support": support,
        "held_nmse": held_nmse,
        "dist_nmse": dist_nmse,
        "world_mean_nmse": float(np.mean(vals)),
        "world_worst_nmse": float(np.max(vals)),
    }


def patch_meta(p7, p5, base, idx, pre_support, joint_support, cap_i):
    centers, widths = p7.dictionary(p5, base)
    center = centers[idx]
    pre_centers = centers[pre_support]
    nearest = float(np.min(np.sqrt(np.sum((pre_centers - center[None, :]) ** 2, axis=1))))
    return {
        "triggering_capability": int(cap_i),
        "candidate": int(idx),
        "center_index": int(idx // 3),
        "scale_slot": int(idx % 3),
        "width": float(widths[idx]),
        "nearest_prepatch_center_distance": nearest,
        "in_same_stage_joint_refit8_support": bool(idx in set(joint_support)),
    }


def one_world(p7, p6, p5, base, seed):
    dist_x, held_x, dist_y, held_y = p6.build_world_data(p5, base, seed)

    support = p6.recruit_support(p5, base, dist_x, dist_y, OLD_CAPS)
    core_support = list(support)
    decoders = {}
    cap_supports = {}
    held_predictions = {}

    for i in OLD_CAPS:
        beta = p6.fit_decoder(p5, base, dist_x[i], dist_y[i], support)
        decoders[i] = beta.copy()
        cap_supports[i] = list(support)
        held_predictions[i] = p6.predict_decoder(
            p5, base, held_x[i], beta, cap_supports[i]
        )

    stages = {}
    patch_records = []
    patch_count = 0

    for label, new_cap in zip(STAGE_LABELS, ADDITION_ORDER):
        active = list(range(new_cap + 1))
        old_caps = list(range(new_cap))

        joint = evaluate_joint_refit(
            p6, p5, base, dist_x, held_x, dist_y, held_y, active
        )

        pre_support = list(support)
        beta_try = p6.fit_decoder(
            p5, base, dist_x[new_cap], dist_y[new_cap], pre_support
        )
        pd_try, _ = decoder_predictions(
            p6, p5, base, pre_support, beta_try,
            dist_x[new_cap], held_x[new_cap]
        )
        decoder_only_dist_nmse = base.nmse(pd_try, dist_y[new_cap])
        triggered = bool(decoder_only_dist_nmse > TRIGGER_NMSE)
        patch = None

        if triggered:
            idx = p7.one_patch_step(
                p6, p5, base,
                dist_x[new_cap], dist_y[new_cap],
                support, set(support),
            )
            support = list(support) + [idx]
            patch_count += 1
            patch = patch_meta(
                p7, p5, base, idx, pre_support, joint["support"], new_cap
            )
            patch_records.append(patch)

        beta_new = p6.fit_decoder(
            p5, base, dist_x[new_cap], dist_y[new_cap], support
        )
        decoders[new_cap] = beta_new.copy()
        cap_supports[new_cap] = list(support)

        old_drift = 0.0
        old_decoder_change = 0.0
        current_held = {}
        current_dist = {}
        active_factor_counts = {}
        active_ops = {}

        for i in active:
            supp_i = cap_supports[i]
            beta_i = decoders[i]
            pd, ph = decoder_predictions(
                p6, p5, base, supp_i, beta_i, dist_x[i], held_x[i]
            )
            current_dist[i] = base.nmse(pd, dist_y[i])
            current_held[i] = base.nmse(ph, held_y[i])
            active_factor_counts[i] = len(supp_i)
            active_ops[i] = 2 * len(supp_i)
            if i in old_caps:
                old_drift = max(
                    old_drift,
                    p6.normalized_prediction_drift(base, held_predictions[i], ph),
                )

        for i in old_caps:
            old_decoder_change = max(old_decoder_change, 0.0)

        held_predictions = {
            i: p6.predict_decoder(
                p5, base, held_x[i], decoders[i], cap_supports[i]
            ).copy()
            for i in active
        }

        vals = [current_held[i] for i in active]
        new_held = current_held[new_cap]
        new_dist = current_dist[new_cap]
        joint_new_held = joint["held_nmse"][new_cap]

        stages[label] = {
            "active_capabilities": [int(i) for i in active],
            "new_capability": int(new_cap),
            "decoder_only_dist_nmse": float(decoder_only_dist_nmse),
            "triggered_patch": triggered,
            "patch": patch,
            "cumulative_patch_count": int(patch_count),
            "shared_factor_count": int(len(support)),
            "candidate": {
                "held_nmse": {str(i): float(current_held[i]) for i in active},
                "dist_nmse": {str(i): float(current_dist[i]) for i in active},
                "new_cap_held_nmse": float(new_held),
                "new_cap_dist_nmse": float(new_dist),
                "world_mean_nmse": float(np.mean(vals)),
                "world_worst_nmse": float(np.max(vals)),
            },
            "joint_refit8": {
                "held_nmse": {str(i): float(joint["held_nmse"][i]) for i in active},
                "new_cap_held_nmse": float(joint_new_held),
                "world_mean_nmse": float(joint["world_mean_nmse"]),
                "world_worst_nmse": float(joint["world_worst_nmse"]),
                "support": p6.support_meta(joint["support"]),
            },
            "developmental_cost": {
                "new_cap_gap": float(new_held - joint_new_held),
                "world_mean_gap": float(np.mean(vals) - joint["world_mean_nmse"]),
                "world_worst_gap": float(np.max(vals) - joint["world_worst_nmse"]),
            },
            "preservation": {
                "old_prediction_drift_max": float(old_drift),
                "old_decoder_max_abs_change": float(old_decoder_change),
            },
            "active_factor_counts": {str(i): int(active_factor_counts[i]) for i in active},
            "residual_ops": {str(i): int(active_ops[i]) for i in active},
            "shared_geometry": {
                "factor_count": int(len(support)),
                "site_ids": int(len(support)),
                "scale_slots": int(len(support)),
            },
        }

    return {
        "seed": int(seed),
        "core_support": p6.support_meta(core_support),
        "stages": stages,
        "patch_records": patch_records,
        "final_patch_count": int(patch_count),
        "final_shared_factor_count": int(len(support)),
        "patches_per_new_capability": float(patch_count / len(ADDITION_ORDER)),
    }


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def stage_summary(rows, label):
    sr = [r["stages"][label] for r in rows]
    held = [s["candidate"]["new_cap_held_nmse"] for s in sr]
    new_gap = [s["developmental_cost"]["new_cap_gap"] for s in sr]
    mean_gap = [s["developmental_cost"]["world_mean_gap"] for s in sr]
    drift = [s["preservation"]["old_prediction_drift_max"] for s in sr]
    dchange = [s["preservation"]["old_decoder_max_abs_change"] for s in sr]

    held_med = q(held, 0.5)
    new_gap_med = q(new_gap, 0.5)
    mean_gap_med = q(mean_gap, 0.5)
    drift_max = float(np.max(drift))
    dchange_max = float(np.max(dchange))

    if (
        held_med <= 0.05
        and new_gap_med <= 0.04
        and mean_gap_med <= 0.03
        and drift_max <= 1e-12
        and dchange_max == 0.0
    ):
        regime = "ROBUST"
    elif new_gap_med > 0.08 and mean_gap_med > 0.06:
        regime = "OVER_CAPACITY"
    elif (0.04 < new_gap_med <= 0.08) or (0.03 < mean_gap_med <= 0.06):
        regime = "TRANSITION"
    else:
        regime = "MIXED_UNCLASSIFIED"

    return {
        "mechanical_regime": regime,
        "patch_trigger_rate": float(np.mean([s["triggered_patch"] for s in sr])),
        "cumulative_patch_count_median": q([s["cumulative_patch_count"] for s in sr], 0.5),
        "shared_factor_count_median": q([s["shared_factor_count"] for s in sr], 0.5),
        "decoder_only_dist_nmse_median": q([s["decoder_only_dist_nmse"] for s in sr], 0.5),
        "post_rule_new_cap_dist_nmse_median": q([s["candidate"]["new_cap_dist_nmse"] for s in sr], 0.5),
        "post_rule_new_cap_held_nmse_median": held_med,
        "post_rule_new_cap_held_nmse_p90": q(held, 0.90),
        "new_cap_gap_median": new_gap_med,
        "world_mean_gap_median": mean_gap_med,
        "old_prediction_drift_max": drift_max,
        "old_decoder_max_abs_change": dchange_max,
        "new_cap_active_factor_count_median": q([
            s["active_factor_counts"][str(s["new_capability"])] for s in sr
        ], 0.5),
        "new_cap_residual_ops_median": q([
            s["residual_ops"][str(s["new_capability"])] for s in sr
        ], 0.5),
        "oldest_cap_residual_ops_median": q([s["residual_ops"]["0"] for s in sr], 0.5),
    }


def summarize(rows):
    stages = {label: stage_summary(rows, label) for label in STAGE_LABELS}
    final_patches = [r["final_patch_count"] for r in rows]
    final_factors = [r["final_shared_factor_count"] for r in rows]
    med_patches = q(final_patches, 0.5)
    all_avoid_over = all(
        stages[label]["mechanical_regime"] != "OVER_CAPACITY"
        for label in STAGE_LABELS
    )
    all_robust = all(
        stages[label]["mechanical_regime"] == "ROBUST"
        for label in STAGE_LABELS
    )
    drift_max = max(stages[label]["old_prediction_drift_max"] for label in STAGE_LABELS)
    dchange_max = max(stages[label]["old_decoder_max_abs_change"] for label in STAGE_LABELS)

    supports_bounded = (
        all_avoid_over
        and drift_max <= 1e-12
        and dchange_max == 0.0
        and med_patches < len(ADDITION_ORDER)
    )
    strong = all_robust and med_patches <= 3.0

    patches = [p for r in rows for p in r["patch_records"]]
    slot_counts = {
        "S0_0p22": int(sum(p["scale_slot"] == 0 for p in patches)),
        "S1_0p44": int(sum(p["scale_slot"] == 1 for p in patches)),
        "S2_0p88": int(sum(p["scale_slot"] == 2 for p in patches)),
    }

    return {
        "worlds": len(rows),
        "stages": stages,
        "final_patch_count_median": med_patches,
        "final_patch_count_p90": q(final_patches, 0.90),
        "final_shared_factor_count_median": q(final_factors, 0.5),
        "patches_per_new_capability_median": q([
            r["patches_per_new_capability"] for r in rows
        ], 0.5),
        "sequential_scaling_encouragement": bool(supports_bounded),
        "strong_mechanical_signal": bool(strong),
        "patch_scale_slot_counts": slot_counts,
        "patch_joint_refit8_support_overlap_rate": (
            float(np.mean([p["in_same_stage_joint_refit8_support"] for p in patches]))
            if patches else 0.0
        ),
        "patch_nearest_prepatch_center_distance_median": (
            q([p["nearest_prepatch_center_distance"] for p in patches], 0.5)
            if patches else 0.0
        ),
        "old_prediction_drift_max": float(drift_max),
        "old_decoder_max_abs_change": float(dchange_max),
    }


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    p7 = load_p7()
    p6 = p7.load_p6()
    p5 = p6.load_p5()
    base = p5.load_base()
    rows = [one_world(p7, p6, p5, base, WORLD_START + i) for i in range(WORLD_COUNT)]
    return {
        "schema": "yggdrasil.h191-p8-sequential-triggered-micropatch.v1",
        "rows": rows,
        "summary": summarize(rows),
        "worlds": len(rows),
        "seed_start": WORLD_START,
        "seed_end": WORLD_START + WORLD_COUNT - 1,
        "trigger_nmse": TRIGGER_NMSE,
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
