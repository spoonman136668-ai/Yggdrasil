#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import numpy as np

P8_NAME = "h191_p8_sequential_triggered_micropatch_v1.py"
WORLD_START = 20260925000000
WORLD_COUNT = 8
OOD_CAP = 8
OOD_CENTER = np.asarray([0.0, 0.0], dtype=np.float64)
OOD_SD = 0.10
OOD_RADIUS_MAX = 0.30
OOD_FREQ_MIN = 5.0
OOD_FREQ_MAX = 8.0


def load_p8():
    path = Path(__file__).resolve().parent / P8_NAME
    spec = importlib.util.spec_from_file_location("h191_p8_base", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sample_ood_context(rng, n):
    chunks = []
    have = 0
    while have < n:
        draw_n = max(64, (n - have) * 3)
        p = rng.normal(loc=OOD_CENTER, scale=OOD_SD, size=(draw_n, 2))
        keep = np.sum(p * p, axis=1) <= OOD_RADIUS_MAX * OOD_RADIUS_MAX
        p = p[keep]
        if len(p):
            take = min(n - have, len(p))
            chunks.append(p[:take])
            have += take
    return np.concatenate(chunks, axis=0)


def source_params_9(base, rng):
    centers = base.uniform_disk(rng, 8)
    sigmas = rng.uniform(0.12, 0.42, size=8)
    dec = rng.normal(0.0, 1.0, size=(8, 9))
    sins = []
    for cap_i in range(9):
        a = rng.uniform(0.5, 1.5)
        if cap_i == OOD_CAP:
            wx = rng.uniform(OOD_FREQ_MIN, OOD_FREQ_MAX)
            wy = rng.uniform(OOD_FREQ_MIN, OOD_FREQ_MAX)
        else:
            wx = rng.uniform(1.0, 4.0)
            wy = rng.uniform(1.0, 4.0)
        phase = rng.uniform(0.0, 2.0 * math.pi)
        sins.append((a, wx, wy, phase))
    return centers, sigmas, dec, sins


def raw_residual(base, x, cap_i, params):
    centers, sigmas, dec, sins = params
    z = base.gaussian_features(x, centers, sigmas)
    shared = z @ dec[:, cap_i]
    a, wx, wy, phase = sins[cap_i]
    extra = 0.10 * a * np.sin(wx * x[:, 0] + wy * x[:, 1] + phase)
    return shared + extra


def build_world_data(p5, base, seed):
    rng = np.random.default_rng(np.random.PCG64(seed))
    ring_centers = p5.context_centers(8)
    params = source_params_9(base, rng)

    dist_x = []
    held_x = []
    dist_y = []
    held_y = []

    for cap_i in range(9):
        if cap_i < 8:
            pts = p5.sample_context(rng, ring_centers, cap_i, 128 + 512)
        else:
            pts = sample_ood_context(rng, 128 + 512)
        xd = pts[:128]
        xh = pts[128:]
        yd = raw_residual(base, xd, cap_i, params)
        yh = raw_residual(base, xh, cap_i, params)
        scale = float(np.sqrt(np.mean(yd * yd)))
        if scale < 1e-12:
            scale = 1.0
        dist_x.append(xd)
        held_x.append(xh)
        dist_y.append(yd / scale)
        held_y.append(yh / scale)

    return dist_x, held_x, dist_y, held_y


def develop_p8_core(p8, p7, p6, p5, base, dist_x, held_x, dist_y, held_y):
    support = p6.recruit_support(p5, base, dist_x, dist_y, p8.OLD_CAPS)
    decoders = {}
    cap_supports = {}
    held_predictions = {}
    patch_records = []

    for i in p8.OLD_CAPS:
        beta = p6.fit_decoder(p5, base, dist_x[i], dist_y[i], support)
        decoders[i] = beta.copy()
        cap_supports[i] = list(support)
        held_predictions[i] = p6.predict_decoder(
            p5, base, held_x[i], beta, cap_supports[i]
        )

    for new_cap in p8.ADDITION_ORDER:
        pre_support = list(support)
        beta_try = p6.fit_decoder(
            p5, base, dist_x[new_cap], dist_y[new_cap], pre_support
        )
        pd_try = p6.predict_decoder(
            p5, base, dist_x[new_cap], beta_try, pre_support
        )
        decoder_only_dist_nmse = base.nmse(pd_try, dist_y[new_cap])
        triggered = bool(decoder_only_dist_nmse > p8.TRIGGER_NMSE)

        if triggered:
            idx = p7.one_patch_step(
                p6, p5, base,
                dist_x[new_cap], dist_y[new_cap],
                support, set(support),
            )
            support = list(support) + [idx]
            patch_records.append({
                "triggering_capability": int(new_cap),
                "candidate": int(idx),
            })

        beta_new = p6.fit_decoder(
            p5, base, dist_x[new_cap], dist_y[new_cap], support
        )
        decoders[new_cap] = beta_new.copy()
        cap_supports[new_cap] = list(support)
        held_predictions[new_cap] = p6.predict_decoder(
            p5, base, held_x[new_cap], beta_new, cap_supports[new_cap]
        )

    old_held_nmse = {}
    old_dist_nmse = {}
    old_ops = {}
    for i in range(8):
        pd = p6.predict_decoder(
            p5, base, dist_x[i], decoders[i], cap_supports[i]
        )
        ph = p6.predict_decoder(
            p5, base, held_x[i], decoders[i], cap_supports[i]
        )
        old_dist_nmse[i] = base.nmse(pd, dist_y[i])
        old_held_nmse[i] = base.nmse(ph, held_y[i])
        old_ops[i] = 2 * len(cap_supports[i])

    return {
        "support": list(support),
        "decoders": decoders,
        "cap_supports": cap_supports,
        "held_predictions": held_predictions,
        "patch_records": patch_records,
        "patch_count": len(patch_records),
        "old_held_nmse": old_held_nmse,
        "old_dist_nmse": old_dist_nmse,
        "old_ops": old_ops,
    }


def fit_policy(p6, p5, base, support, dist_x, held_x, dist_y, held_y):
    beta = p6.fit_decoder(
        p5, base, dist_x[OOD_CAP], dist_y[OOD_CAP], support
    )
    pd = p6.predict_decoder(
        p5, base, dist_x[OOD_CAP], beta, support
    )
    ph = p6.predict_decoder(
        p5, base, held_x[OOD_CAP], beta, support
    )
    return {
        "beta": beta,
        "dist_nmse": base.nmse(pd, dist_y[OOD_CAP]),
        "held_nmse": base.nmse(ph, held_y[OOD_CAP]),
        "prediction": ph,
    }


def factor_meta(p7, p5, base, idx, pre_support, local8_support, joint_support):
    centers, widths = p7.dictionary(p5, base)
    center = centers[idx]
    pre_centers = centers[pre_support]
    nearest = float(np.min(np.sqrt(np.sum(
        (pre_centers - center[None, :]) ** 2, axis=1
    ))))
    return {
        "candidate": int(idx),
        "center_index": int(idx // 3),
        "scale_slot": int(idx % 3),
        "width": float(widths[idx]),
        "nearest_prepatch_center_distance": nearest,
        "in_ood_local8_support": bool(idx in set(local8_support)),
        "in_joint_refit8_support": bool(idx in set(joint_support)),
    }


def evaluate_old_preservation(p6, p5, base, developed, held_x):
    drift = 0.0
    for i in range(8):
        ph = p6.predict_decoder(
            p5, base, held_x[i],
            developed["decoders"][i],
            developed["cap_supports"][i],
        )
        drift = max(
            drift,
            p6.normalized_prediction_drift(
                base, developed["held_predictions"][i], ph
            ),
        )
    return float(drift)


def one_world(p8, p7, p6, p5, base, seed):
    dist_x, held_x, dist_y, held_y = build_world_data(p5, base, seed)
    developed = develop_p8_core(
        p8, p7, p6, p5, base,
        dist_x, held_x, dist_y, held_y,
    )
    developed_support = list(developed["support"])

    local8_support = p6.recruit_support(
        p5, base, dist_x, dist_y, (OOD_CAP,)
    )
    local8 = fit_policy(
        p6, p5, base, local8_support,
        dist_x, held_x, dist_y, held_y,
    )

    joint_support = p6.recruit_support(
        p5, base, dist_x, dist_y, tuple(range(9))
    )
    joint = fit_policy(
        p6, p5, base, joint_support,
        dist_x, held_x, dist_y, held_y,
    )

    patch0 = fit_policy(
        p6, p5, base, developed_support,
        dist_x, held_x, dist_y, held_y,
    )

    idx1 = p7.one_patch_step(
        p6, p5, base,
        dist_x[OOD_CAP], dist_y[OOD_CAP],
        developed_support, set(developed_support),
    )
    support1 = developed_support + [idx1]
    patch1 = fit_policy(
        p6, p5, base, support1,
        dist_x, held_x, dist_y, held_y,
    )

    idx2 = p7.one_patch_step(
        p6, p5, base,
        dist_x[OOD_CAP], dist_y[OOD_CAP],
        support1, set(support1),
    )
    support2 = support1 + [idx2]
    patch2 = fit_policy(
        p6, p5, base, support2,
        dist_x, held_x, dist_y, held_y,
    )

    old_vals = [developed["old_held_nmse"][i] for i in range(8)]
    old_drift = evaluate_old_preservation(
        p6, p5, base, developed, held_x
    )

    def finalize(policy, support, patch_count):
        vals = old_vals + [policy["held_nmse"]]
        reduction = (
            (patch0["held_nmse"] - policy["held_nmse"])
            / (patch0["held_nmse"] + 1e-12)
        )
        return {
            "ood_dist_nmse": float(policy["dist_nmse"]),
            "ood_held_nmse": float(policy["held_nmse"]),
            "ood_generalization_gap": float(
                policy["held_nmse"] - policy["dist_nmse"]
            ),
            "ood_error_reduction_vs_patch0": float(reduction),
            "ood_gap_vs_local8": float(
                policy["held_nmse"] - local8["held_nmse"]
            ),
            "ood_gap_vs_joint_refit8": float(
                policy["held_nmse"] - joint["held_nmse"]
            ),
            "world_mean_nmse": float(np.mean(vals)),
            "world_worst_nmse": float(np.max(vals)),
            "old_prediction_drift_max": old_drift,
            "old_decoder_max_abs_change": 0.0,
            "factor_count": int(len(support)),
            "ood_decoder_scalars": int(len(support)),
            "ood_residual_ops": int(2 * len(support)),
            "shared_factor_growth": int(patch_count),
        }

    p0 = finalize(patch0, developed_support, 0)
    p1 = finalize(patch1, support1, 1)
    p2 = finalize(patch2, support2, 2)

    return {
        "seed": int(seed),
        "pre_ood": {
            "in_distribution_patch_count": int(developed["patch_count"]),
            "developed_shared_factor_count": int(len(developed_support)),
            "old_cap_residual_ops": {
                str(i): int(developed["old_ops"][i]) for i in range(8)
            },
        },
        "PATCH0": p0,
        "PATCH1": p1,
        "PATCH2": p2,
        "PATCH1_factor": factor_meta(
            p7, p5, base, idx1, developed_support,
            local8_support, joint_support,
        ),
        "PATCH2_factors": [
            factor_meta(
                p7, p5, base, idx1, developed_support,
                local8_support, joint_support,
            ),
            factor_meta(
                p7, p5, base, idx2, support1,
                local8_support, joint_support,
            ),
        ],
        "OOD_LOCAL8": {
            "ood_dist_nmse": float(local8["dist_nmse"]),
            "ood_held_nmse": float(local8["held_nmse"]),
            "support": p6.support_meta(local8_support),
        },
        "JOINT_REFIT8": {
            "ood_dist_nmse": float(joint["dist_nmse"]),
            "ood_held_nmse": float(joint["held_nmse"]),
            "support": p6.support_meta(joint_support),
        },
    }


def q(values, p):
    return float(np.quantile(np.asarray(values, dtype=np.float64), p))


def policy_summary(rows, name):
    pr = [r[name] for r in rows]
    return {
        "ood_dist_nmse_median": q([r["ood_dist_nmse"] for r in pr], 0.5),
        "ood_held_nmse_median": q([r["ood_held_nmse"] for r in pr], 0.5),
        "ood_held_nmse_p90": q([r["ood_held_nmse"] for r in pr], 0.90),
        "ood_generalization_gap_median": q([
            r["ood_generalization_gap"] for r in pr
        ], 0.5),
        "ood_error_reduction_vs_patch0_median": q([
            r["ood_error_reduction_vs_patch0"] for r in pr
        ], 0.5),
        "ood_gap_vs_local8_median": q([
            r["ood_gap_vs_local8"] for r in pr
        ], 0.5),
        "ood_gap_vs_joint_refit8_median": q([
            r["ood_gap_vs_joint_refit8"] for r in pr
        ], 0.5),
        "world_mean_nmse_median": q([r["world_mean_nmse"] for r in pr], 0.5),
        "world_worst_nmse_median": q([r["world_worst_nmse"] for r in pr], 0.5),
        "old_prediction_drift_max": float(np.max([
            r["old_prediction_drift_max"] for r in pr
        ])),
        "old_decoder_max_abs_change": float(np.max([
            r["old_decoder_max_abs_change"] for r in pr
        ])),
        "factor_count_median": q([r["factor_count"] for r in pr], 0.5),
        "ood_residual_ops_median": q([r["ood_residual_ops"] for r in pr], 0.5),
    }


def robust_elastic(s):
    return (
        s["ood_held_nmse_median"] <= 0.05
        and s["ood_error_reduction_vs_patch0_median"] >= 0.50
        and s["ood_gap_vs_local8_median"] <= 0.04
        and s["old_prediction_drift_max"] <= 1e-12
        and s["old_decoder_max_abs_change"] == 0.0
        and s["ood_generalization_gap_median"] <= 0.05
    )


def summarize(rows):
    local8_med = q([
        r["OOD_LOCAL8"]["ood_held_nmse"] for r in rows
    ], 0.5)
    joint_med = q([
        r["JOINT_REFIT8"]["ood_held_nmse"] for r in rows
    ], 0.5)

    policies = {
        name: policy_summary(rows, name)
        for name in ("PATCH0", "PATCH1", "PATCH2")
    }

    dictionary_capable = bool(local8_med <= 0.05)
    p1_ok = dictionary_capable and robust_elastic(policies["PATCH1"])
    p2_ok = dictionary_capable and robust_elastic(policies["PATCH2"])

    if not dictionary_capable:
        classification = "DICTIONARY_FAMILY_LIMIT"
    elif p1_ok:
        classification = "PATCH1_ROBUST_ELASTIC"
    elif p2_ok:
        classification = "PATCH2_ROBUST_ELASTIC"
    elif (
        policies["PATCH2"]["ood_held_nmse_median"] > 0.05
        or policies["PATCH2"]["ood_gap_vs_local8_median"] > 0.04
    ):
        classification = "PATCH_BUDGET_LIMIT"
    else:
        classification = "MIXED"

    patch1_meta = [r["PATCH1_factor"] for r in rows]
    patch2_meta = [f for r in rows for f in r["PATCH2_factors"]]

    return {
        "worlds": len(rows),
        "dictionary_capable": dictionary_capable,
        "classification": classification,
        "pre_ood_in_distribution_patch_count_median": q([
            r["pre_ood"]["in_distribution_patch_count"] for r in rows
        ], 0.5),
        "pre_ood_shared_factor_count_median": q([
            r["pre_ood"]["developed_shared_factor_count"] for r in rows
        ], 0.5),
        "oldest_cap_residual_ops_median": q([
            r["pre_ood"]["old_cap_residual_ops"]["0"] for r in rows
        ], 0.5),
        "newest_pre_ood_cap_residual_ops_median": q([
            r["pre_ood"]["old_cap_residual_ops"]["7"] for r in rows
        ], 0.5),
        "OOD_LOCAL8": {
            "ood_held_nmse_median": local8_med,
            "ood_dist_nmse_median": q([
                r["OOD_LOCAL8"]["ood_dist_nmse"] for r in rows
            ], 0.5),
        },
        "JOINT_REFIT8": {
            "ood_held_nmse_median": joint_med,
            "ood_dist_nmse_median": q([
                r["JOINT_REFIT8"]["ood_dist_nmse"] for r in rows
            ], 0.5),
        },
        "policies": policies,
        "patch1_geometry": {
            "scale_slot_counts": {
                "S0_0p22": int(sum(f["scale_slot"] == 0 for f in patch1_meta)),
                "S1_0p44": int(sum(f["scale_slot"] == 1 for f in patch1_meta)),
                "S2_0p88": int(sum(f["scale_slot"] == 2 for f in patch1_meta)),
            },
            "nearest_prepatch_center_distance_median": q([
                f["nearest_prepatch_center_distance"] for f in patch1_meta
            ], 0.5),
            "ood_local8_overlap_rate": float(np.mean([
                f["in_ood_local8_support"] for f in patch1_meta
            ])),
            "joint_refit8_overlap_rate": float(np.mean([
                f["in_joint_refit8_support"] for f in patch1_meta
            ])),
        },
        "patch2_geometry": {
            "scale_slot_counts": {
                "S0_0p22": int(sum(f["scale_slot"] == 0 for f in patch2_meta)),
                "S1_0p44": int(sum(f["scale_slot"] == 1 for f in patch2_meta)),
                "S2_0p88": int(sum(f["scale_slot"] == 2 for f in patch2_meta)),
            },
            "nearest_prepatch_center_distance_median": q([
                f["nearest_prepatch_center_distance"] for f in patch2_meta
            ], 0.5),
            "ood_local8_overlap_rate": float(np.mean([
                f["in_ood_local8_support"] for f in patch2_meta
            ])),
            "joint_refit8_overlap_rate": float(np.mean([
                f["in_joint_refit8_support"] for f in patch2_meta
            ])),
        },
    }


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run():
    p8 = load_p8()
    p7 = p8.load_p7()
    p6 = p7.load_p6()
    p5 = p6.load_p5()
    base = p5.load_base()
    rows = [
        one_world(p8, p7, p6, p5, base, WORLD_START + i)
        for i in range(WORLD_COUNT)
    ]
    return {
        "schema": "yggdrasil.h191-p9-ood-elastic-core-expansion.v1",
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
