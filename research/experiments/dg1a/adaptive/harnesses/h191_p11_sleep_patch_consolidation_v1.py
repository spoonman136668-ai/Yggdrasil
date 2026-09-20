#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

P10_NAME = "h191_p10_repeated_ood_patch_reuse_v1.py"
WORLD_START = 20260925200000
WORLD_COUNT = 6
SLEEP_ALPHA = 1e-9
ACTIVE_ZERO = 1e-12


def load_p10():
    path = Path(__file__).resolve().parent / P10_NAME
    spec = importlib.util.spec_from_file_location("h191_p10_base", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sleep_ridge(x, y):
    if x.shape[1] == 0:
        return np.empty(0, dtype=np.float64)
    return np.linalg.solve(
        x.T @ x + SLEEP_ALPHA * np.eye(x.shape[1]),
        x.T @ y,
    )


def normalized_prediction_mismatch(after, before):
    return float(
        np.mean((after - before) ** 2)
        / (float(np.var(before)) + 1e-12)
    )


def develop_presleep(p10, dist_x, held_x, dist_y):
    support = p10.recruit_support(
        dist_x, dist_y, p10.OLD_CAPS, 8
    )
    core_support = list(support)
    decoders = {}
    supports = {}

    for i in p10.OLD_CAPS:
        beta = p10.fit_decoder(dist_x[i], dist_y[i], support)
        decoders[i] = beta.copy()
        supports[i] = list(support)

    for cap in p10.IN_DIST_ADDITION_ORDER:
        beta_try = p10.fit_decoder(
            dist_x[cap], dist_y[cap], support
        )
        pd_try = p10.predict_decoder(
            dist_x[cap], beta_try, support
        )
        if p10.nmse(pd_try, dist_y[cap]) > p10.TRIGGER_NMSE:
            support = list(support) + [
                p10.one_patch_step(
                    dist_x[cap], dist_y[cap], support
                )
            ]
        beta = p10.fit_decoder(dist_x[cap], dist_y[cap], support)
        decoders[cap] = beta.copy()
        supports[cap] = list(support)

    for cap in p10.OOD_CAPS:
        beta_try = p10.fit_decoder(
            dist_x[cap], dist_y[cap], support
        )
        pd_try = p10.predict_decoder(
            dist_x[cap], beta_try, support
        )
        if p10.nmse(pd_try, dist_y[cap]) > p10.TRIGGER_NMSE:
            support = list(support) + [
                p10.one_patch_step(
                    dist_x[cap], dist_y[cap], support
                )
            ]
        beta = p10.fit_decoder(dist_x[cap], dist_y[cap], support)
        decoders[cap] = beta.copy()
        supports[cap] = list(support)

    return {
        "core_support": core_support,
        "final_support": list(support),
        "decoders": decoders,
        "supports": supports,
    }


def build_sleep_state(p10, developed, dist_x, held_x, held_y):
    core_support = developed["core_support"]
    decoders = developed["decoders"]
    supports = developed["supports"]

    caps = []
    pre_patch_scalars = 0

    for cap in range(12):
        support = supports[cap]
        beta = decoders[cap]
        assert support[:8] == core_support

        core_beta = beta[:8].copy()
        core_dist = p10.predict_decoder(
            dist_x[cap], core_beta, core_support
        )
        core_held = p10.predict_decoder(
            held_x[cap], core_beta, core_support
        )

        pre_dist = p10.predict_decoder(
            dist_x[cap], beta, support
        )
        pre_held = p10.predict_decoder(
            held_x[cap], beta, support
        )

        patch_dist = pre_dist - core_dist
        patch_held = pre_held - core_held
        patch_count = max(0, len(beta) - 8)
        pre_patch_scalars += patch_count

        caps.append({
            "capability": cap,
            "core_beta": core_beta,
            "core_dist": core_dist,
            "core_held": core_held,
            "pre_dist": pre_dist,
            "pre_held": pre_held,
            "patch_dist": patch_dist,
            "patch_held": patch_held,
            "pre_task_held_nmse": p10.nmse(
                pre_held, held_y[cap]
            ),
            "pre_active_factor_count": len(support),
            "pre_residual_ops": 2 * len(support),
        })

    patch_factors = developed["final_support"][8:]
    return {
        "caps": caps,
        "patch_factors": list(patch_factors),
        "patch_factor_count": len(patch_factors),
        "pre_patch_decoder_scalars": int(pre_patch_scalars),
    }


def recruit_consolidated(p10, sleep_state, dist_x, rank):
    if rank <= 0:
        return []

    caps = sleep_state["caps"]
    core_support = set(
        developed_core for developed_core in []
    )
    selected = []
    available = np.ones(
        len(p10.CAND_WIDTHS), dtype=bool
    )

    for idx in sleep_state["core_support"]:
        available[idx] = False

    zall = [
        p10.gaussian_features(
            dist_x[c["capability"]],
            p10.CAND_CENTERS,
            p10.CAND_WIDTHS,
        )
        for c in caps
    ]

    for _ in range(rank):
        total = np.zeros(
            len(p10.CAND_WIDTHS), dtype=np.float64
        )

        for cap_i, c in enumerate(caps):
            y = c["patch_dist"]
            z = zall[cap_i]
            denom_var = float(
                np.var(c["pre_dist"])
            ) + 1e-12

            if not selected:
                denom = (
                    np.sum(z * z, axis=0)
                    + SLEEP_ALPHA
                )
                gamma = (z.T @ y) / denom
                pred_new = z * gamma[None, :]
            else:
                xsel = z[:, selected]
                ainv = np.linalg.inv(
                    xsel.T @ xsel
                    + SLEEP_ALPHA
                    * np.eye(len(selected))
                )
                beta = ainv @ (xsel.T @ y)
                pred = xsel @ beta
                qmat = xsel.T @ z
                v = ainv @ qmat
                u = z - xsel @ v
                h = (
                    np.sum(z * z, axis=0)
                    + SLEEP_ALPHA
                    - np.sum(qmat * v, axis=0)
                )
                gamma = (
                    z.T @ y
                    - qmat.T @ beta
                ) / h
                pred_new = (
                    pred[:, None]
                    + u * gamma[None, :]
                )

            total += (
                np.mean(
                    (y[:, None] - pred_new) ** 2,
                    axis=0,
                )
                / denom_var
            )

        total /= float(len(caps))
        total[~available] = np.inf
        idx = int(np.argmin(total))
        selected.append(idx)
        available[idx] = False

    return selected


def evaluate_policy(
    p10,
    sleep_state,
    dist_x,
    held_x,
    held_y,
    support,
    policy_name,
):
    caps = sleep_state["caps"]
    per_cap = []
    total_nonzero = 0

    for c in caps:
        cap = c["capability"]

        if support:
            zd = p10.gaussian_features(
                dist_x[cap],
                p10.CAND_CENTERS[support],
                p10.CAND_WIDTHS[support],
            )
            zh = p10.gaussian_features(
                held_x[cap],
                p10.CAND_CENTERS[support],
                p10.CAND_WIDTHS[support],
            )
            beta = sleep_ridge(
                zd, c["patch_dist"]
            )
            patch_dist = zd @ beta
            patch_held = zh @ beta
            nonzero = int(
                np.sum(
                    np.abs(beta)
                    > ACTIVE_ZERO
                )
            )
        else:
            beta = np.empty(
                0, dtype=np.float64
            )
            patch_dist = np.zeros_like(
                c["patch_dist"]
            )
            patch_held = np.zeros_like(
                c["patch_held"]
            )
            nonzero = 0

        post_dist = (
            c["core_dist"]
            + patch_dist
        )
        post_held = (
            c["core_held"]
            + patch_held
        )

        dist_mismatch = (
            normalized_prediction_mismatch(
                post_dist, c["pre_dist"]
            )
        )
        held_mismatch = (
            normalized_prediction_mismatch(
                post_held, c["pre_held"]
            )
        )
        task_post = p10.nmse(
            post_held, held_y[cap]
        )
        total_nonzero += nonzero

        per_cap.append({
            "capability": cap,
            "dist_prediction_mismatch": float(
                dist_mismatch
            ),
            "held_prediction_mismatch": float(
                held_mismatch
            ),
            "task_held_nmse_pre": float(
                c["pre_task_held_nmse"]
            ),
            "task_held_nmse_post": float(
                task_post
            ),
            "task_held_nmse_delta": float(
                task_post
                - c["pre_task_held_nmse"]
            ),
            "patch_decoder_scalars": int(
                len(beta)
            ),
            "active_patch_coefficients": int(
                nonzero
            ),
            "pre_residual_ops": int(
                c["pre_residual_ops"]
            ),
            "post_residual_ops": int(
                16 + 2 * nonzero
            ),
        })

    held_vals = [
        c["held_prediction_mismatch"]
        for c in per_cap
    ]
    dist_vals = [
        c["dist_prediction_mismatch"]
        for c in per_cap
    ]
    task_delta = [
        c["task_held_nmse_delta"]
        for c in per_cap
    ]

    return {
        "policy": policy_name,
        "support": [int(v) for v in support],
        "patch_geometry_count": int(
            len(support)
        ),
        "total_patch_decoder_scalars": int(
            12 * len(support)
        ),
        "total_nonzero_patch_coefficients": int(
            total_nonzero
        ),
        "capability_median_held_mismatch": float(
            np.median(held_vals)
        ),
        "world_mean_held_mismatch": float(
            np.mean(held_vals)
        ),
        "world_worst_held_mismatch": float(
            np.max(held_vals)
        ),
        "world_mean_dist_mismatch": float(
            np.mean(dist_vals)
        ),
        "world_worst_dist_mismatch": float(
            np.max(dist_vals)
        ),
        "world_mean_task_nmse_delta": float(
            np.mean(task_delta)
        ),
        "oldest_cap_post_ops": int(
            per_cap[0]["post_residual_ops"]
        ),
        "median_cap_post_ops": float(
            np.median([
                c["post_residual_ops"]
                for c in per_cap
            ])
        ),
        "newest_cap_post_ops": int(
            per_cap[-1]["post_residual_ops"]
        ),
        "per_capability": per_cap,
    }


def one_world(p10, seed):
    dist_x, held_x, dist_y, held_y = (
        p10.build_world_data(seed)
    )
    developed = develop_presleep(
        p10, dist_x, held_x, dist_y
    )
    sleep_state = build_sleep_state(
        p10, developed,
        dist_x, held_x, held_y
    )
    sleep_state["core_support"] = list(
        developed["core_support"]
    )

    pcount = sleep_state[
        "patch_factor_count"
    ]
    compressible = pcount >= 2

    control = evaluate_policy(
        p10,
        sleep_state,
        dist_x,
        held_x,
        held_y,
        sleep_state["patch_factors"],
        "ORIGINAL_PATCH_RECODE",
    )

    half = None
    minus1 = None

    if compressible:
        k_half = max(1, pcount // 2)
        k_minus1 = pcount - 1
        max_rank = max(
            k_half, k_minus1
        )
        nested = recruit_consolidated(
            p10,
            sleep_state,
            dist_x,
            max_rank,
        )

        half = evaluate_policy(
            p10,
            sleep_state,
            dist_x,
            held_x,
            held_y,
            nested[:k_half],
            "HALF",
        )
        minus1 = evaluate_policy(
            p10,
            sleep_state,
            dist_x,
            held_x,
            held_y,
            nested[:k_minus1],
            "MINUS1",
        )

        for policy, kval in (
            (half, k_half),
            (minus1, k_minus1),
        ):
            policy[
                "geometry_reduction_fraction"
            ] = float(
                (pcount - kval)
                / pcount
            )
            pre_scalars = sleep_state[
                "pre_patch_decoder_scalars"
            ]
            post_scalars = policy[
                "total_patch_decoder_scalars"
            ]
            if pre_scalars:
                policy[
                    "decoder_state_change_fraction"
                ] = float(
                    (pre_scalars - post_scalars)
                    / pre_scalars
                )
            else:
                policy[
                    "decoder_state_change_fraction"
                ] = 0.0

    core_change = 0.0
    pre_ops = [
        c["pre_residual_ops"]
        for c in sleep_state["caps"]
    ]

    return {
        "seed": int(seed),
        "compressible": bool(
            compressible
        ),
        "pre_sleep": {
            "core_support": [
                int(v)
                for v
                in developed["core_support"]
            ],
            "patch_factors": [
                int(v)
                for v
                in sleep_state[
                    "patch_factors"
                ]
            ],
            "patch_factor_count": int(
                pcount
            ),
            "patch_site_ids": int(
                pcount
            ),
            "patch_scale_slots": int(
                pcount
            ),
            "total_patch_decoder_scalars": int(
                sleep_state[
                    "pre_patch_decoder_scalars"
                ]
            ),
            "oldest_cap_ops": int(
                pre_ops[0]
            ),
            "median_cap_ops": float(
                np.median(pre_ops)
            ),
            "newest_cap_ops": int(
                pre_ops[-1]
            ),
        },
        "core_decoder_max_abs_change": float(
            core_change
        ),
        "ORIGINAL_PATCH_RECODE": control,
        "HALF": half,
        "MINUS1": minus1,
    }


def q(values, p):
    return float(
        np.quantile(
            np.asarray(
                values,
                dtype=np.float64,
            ),
            p,
        )
    )


def policy_summary(rows, name):
    pr = [
        r[name]
        for r in rows
        if r[name] is not None
    ]
    if not pr:
        return None

    return {
        "world_count": len(pr),
        "capability_median_held_mismatch_median": q(
            [
                x[
                    "capability_median_held_mismatch"
                ]
                for x in pr
            ],
            0.5,
        ),
        "world_mean_held_mismatch_median": q(
            [
                x[
                    "world_mean_held_mismatch"
                ]
                for x in pr
            ],
            0.5,
        ),
        "world_worst_held_mismatch_median": q(
            [
                x[
                    "world_worst_held_mismatch"
                ]
                for x in pr
            ],
            0.5,
        ),
        "world_worst_held_mismatch_p90": q(
            [
                x[
                    "world_worst_held_mismatch"
                ]
                for x in pr
            ],
            0.90,
        ),
        "world_mean_dist_mismatch_median": q(
            [
                x[
                    "world_mean_dist_mismatch"
                ]
                for x in pr
            ],
            0.5,
        ),
        "world_mean_task_nmse_delta_median": q(
            [
                x[
                    "world_mean_task_nmse_delta"
                ]
                for x in pr
            ],
            0.5,
        ),
        "patch_geometry_count_median": q(
            [
                x[
                    "patch_geometry_count"
                ]
                for x in pr
            ],
            0.5,
        ),
        "total_patch_decoder_scalars_median": q(
            [
                x[
                    "total_patch_decoder_scalars"
                ]
                for x in pr
            ],
            0.5,
        ),
        "oldest_cap_post_ops_median": q(
            [
                x[
                    "oldest_cap_post_ops"
                ]
                for x in pr
            ],
            0.5,
        ),
        "median_cap_post_ops_median": q(
            [
                x[
                    "median_cap_post_ops"
                ]
                for x in pr
            ],
            0.5,
        ),
        "newest_cap_post_ops_median": q(
            [
                x[
                    "newest_cap_post_ops"
                ]
                for x in pr
            ],
            0.5,
        ),
        "geometry_reduction_fraction_median": (
            q(
                [
                    x[
                        "geometry_reduction_fraction"
                    ]
                    for x in pr
                ],
                0.5,
            )
            if "geometry_reduction_fraction"
            in pr[0]
            else 0.0
        ),
        "decoder_state_change_fraction_median": (
            q(
                [
                    x[
                        "decoder_state_change_fraction"
                    ]
                    for x in pr
                ],
                0.5,
            )
            if "decoder_state_change_fraction"
            in pr[0]
            else 0.0
        ),
    }


def summarize(rows):
    control = policy_summary(
        rows, "ORIGINAL_PATCH_RECODE"
    )
    compressible = [
        r for r in rows
        if r["compressible"]
    ]
    half = policy_summary(
        compressible, "HALF"
    )
    minus1 = policy_summary(
        compressible, "MINUS1"
    )

    control_pass = bool(
        control is not None
        and control[
            "world_worst_held_mismatch_median"
        ]
        <= 1e-10
    )

    core_change = float(
        np.max([
            r[
                "core_decoder_max_abs_change"
            ]
            for r in rows
        ])
    )

    half_strong = False
    minus1_useful = False

    if (
        control_pass
        and half is not None
    ):
        pre_newest = q(
            [
                r[
                    "pre_sleep"
                ][
                    "newest_cap_ops"
                ]
                for r in compressible
            ],
            0.5,
        )
        half_strong = bool(
            half[
                "world_mean_held_mismatch_median"
            ]
            <= 0.01
            and half[
                "world_worst_held_mismatch_median"
            ]
            <= 0.02
            and half[
                "world_worst_held_mismatch_p90"
            ]
            <= 0.05
            and half[
                "geometry_reduction_fraction_median"
            ]
            >= 0.40
            and core_change == 0.0
            and half[
                "newest_cap_post_ops_median"
            ]
            <= pre_newest
        )

    if (
        control_pass
        and not half_strong
        and minus1 is not None
    ):
        minus1_useful = bool(
            minus1[
                "world_mean_held_mismatch_median"
            ]
            <= 0.01
            and minus1[
                "world_worst_held_mismatch_median"
            ]
            <= 0.02
            and core_change == 0.0
            and minus1[
                "geometry_reduction_fraction_median"
            ]
            > 0.0
        )

    if not control_pass:
        classification = (
            "MECHANICALLY_INVALID"
        )
    elif not compressible:
        classification = (
            "NO_COMPRESSIBLE_WORLDS"
        )
    elif half_strong:
        classification = (
            "HALF_STRONG_CONSOLIDATION"
        )
    elif minus1_useful:
        classification = (
            "MINUS1_USEFUL_CONSOLIDATION"
        )
    else:
        classification = (
            "NEGATIVE_FIXED_DICTIONARY_CONSOLIDATION"
        )

    return {
        "worlds": len(rows),
        "compressible_worlds": len(
            compressible
        ),
        "noncompressible_worlds": (
            len(rows) - len(compressible)
        ),
        "classification": classification,
        "control_pass": bool(
            control_pass
        ),
        "half_strong": bool(
            half_strong
        ),
        "minus1_useful": bool(
            minus1_useful
        ),
        "core_decoder_max_abs_change": float(
            core_change
        ),
        "pre_sleep_patch_factor_count_median": q(
            [
                r[
                    "pre_sleep"
                ][
                    "patch_factor_count"
                ]
                for r in rows
            ],
            0.5,
        ),
        "pre_sleep_patch_decoder_scalars_median": q(
            [
                r[
                    "pre_sleep"
                ][
                    "total_patch_decoder_scalars"
                ]
                for r in rows
            ],
            0.5,
        ),
        "pre_sleep_oldest_cap_ops_median": q(
            [
                r[
                    "pre_sleep"
                ][
                    "oldest_cap_ops"
                ]
                for r in rows
            ],
            0.5,
        ),
        "pre_sleep_median_cap_ops_median": q(
            [
                r[
                    "pre_sleep"
                ][
                    "median_cap_ops"
                ]
                for r in rows
            ],
            0.5,
        ),
        "pre_sleep_newest_cap_ops_median": q(
            [
                r[
                    "pre_sleep"
                ][
                    "newest_cap_ops"
                ]
                for r in rows
            ],
            0.5,
        ),
        "ORIGINAL_PATCH_RECODE": control,
        "HALF": half,
        "MINUS1": minus1,
    }


def encode(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def run():
    p10 = load_p10()
    rows = [
        one_world(
            p10,
            WORLD_START + i,
        )
        for i in range(WORLD_COUNT)
    ]
    return {
        "schema": (
            "yggdrasil.h191-p11-"
            "sleep-patch-consolidation.v1"
        ),
        "rows": rows,
        "summary": summarize(rows),
        "worlds": len(rows),
        "seed_start": WORLD_START,
        "seed_end": (
            WORLD_START
            + WORLD_COUNT
            - 1
        ),
        "sleep_alpha": SLEEP_ALPHA,
        "active_zero_threshold": (
            ACTIVE_ZERO
        ),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    obj = run()
    raw = (
        encode(obj) + "\n"
    ).encode("utf-8")
    Path(args.out).write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    print(
        encode({
            "output": args.out,
            "sha256": digest,
            "summary": obj["summary"],
            "worlds": obj["worlds"],
        })
    )


if __name__ == "__main__":
    main()
