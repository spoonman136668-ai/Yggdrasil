from __future__ import annotations

import hashlib
import statistics

import torch
import torch.nn.functional as F

DOMAIN = b"DG1A_P0_STAB18_R1_CAUSAL_PROBE_V1"
P = 0.25
H = W = 40
RADIUS = 6


def domain_seed(g: torch.Generator) -> int:
    state = bytes(g.get_state().cpu().tolist())
    digest = hashlib.sha256(state + DOMAIN).digest()
    return int.from_bytes(digest[:8], "big") & ((1 << 63) - 1)


def disk_mask() -> torch.Tensor:
    yy, xx = torch.meshgrid(torch.arange(H), torch.arange(W), indexing="ij")
    cy, cx = H // 2, W // 2
    return (((yy - cy) ** 2 + (xx - cx) ** 2) <= RADIUS ** 2)[None, None]


def phi_binary(a: torch.Tensor, b: torch.Tensor) -> float:
    a = a.flatten().to(torch.float64)
    b = b.flatten().to(torch.float64)
    am, bm = a.mean(), b.mean()
    av = a - am
    bv = b - bm
    den = torch.sqrt((av * av).sum() * (bv * bv).sum())
    return 0.0 if float(den) == 0.0 else float((av * bv).sum() / den)


def minimal_support_probe(trials: int = 5000) -> dict[str, float]:
    live = disk_mask()
    selected_counts = []
    removed_counts = []
    trials_with_removed = 0
    for seed in range(trials):
        main = torch.Generator(device="cpu").manual_seed(seed)
        probe = torch.Generator(device="cpu").manual_seed(domain_seed(main))
        selected = live & (torch.rand((1, 1, H, W), generator=probe) < P)
        remaining = live & ~selected
        eligible = F.max_pool2d(remaining.float(), 3, stride=1, padding=1) > 0.0
        removed = selected & ~eligible
        ns = int(selected.sum())
        nr = int(removed.sum())
        selected_counts.append(ns)
        removed_counts.append(nr)
        trials_with_removed += int(nr > 0)
    total_selected = sum(selected_counts)
    total_removed = sum(removed_counts)
    return {
        "trials": trials,
        "disk_live_cells": int(live.sum()),
        "selected_mean": statistics.mean(selected_counts),
        "selected_sd": statistics.pstdev(selected_counts),
        "selected_min": min(selected_counts),
        "selected_max": max(selected_counts),
        "retained_update_eligibility_fraction": 1.0 - total_removed / total_selected,
        "structurally_removed_fraction": total_removed / total_selected,
        "trials_with_any_structural_removal_fraction": trials_with_removed / trials,
        "mean_structurally_removed_sites": statistics.mean(removed_counts),
    }


def rng_horizon_audit(seeds: int = 1000, horizon: int = 16) -> dict[str, object]:
    overlap_by_t = [[] for _ in range(horizon)]
    phi_by_t = [[] for _ in range(horizon)]
    probe_fractions = []
    for seed in range(seeds):
        main = torch.Generator(device="cpu").manual_seed(seed)
        probe = torch.Generator(device="cpu").manual_seed(domain_seed(main))
        pmask = torch.rand((1, 1, H, W), generator=probe) < P
        probe_fractions.append(float(pmask.float().mean()))
        for t in range(horizon):
            fire = torch.rand((1, 1, H, W), generator=main) <= 0.5
            overlap_by_t[t].append(float(fire[pmask].float().mean()))
            phi_by_t[t].append(phi_binary(pmask, fire))
    mean_overlap = [statistics.mean(x) for x in overlap_by_t]
    mean_phi = [statistics.mean(x) for x in phi_by_t]
    return {
        "seeds": seeds,
        "horizon": horizon,
        "probe_fraction_mean": statistics.mean(probe_fractions),
        "mean_overlap_by_step": mean_overlap,
        "mean_phi_by_step": mean_phi,
        "max_abs_overlap_deviation_from_0_5": max(abs(x - 0.5) for x in mean_overlap),
        "max_abs_mean_phi": max(abs(x) for x in mean_phi),
    }


def cpu_schedule() -> dict[str, object]:
    g = torch.Generator(device="cpu").manual_seed(0)
    damage = []
    steps = []
    for _ in range(200):
        torch.randperm(64, generator=g)[:8]
        damage.append(float(torch.rand((), generator=g)) < 0.5)
        steps.append(int(torch.randint(64, 97, (1,), generator=g)))
    return {
        "iterations": 200,
        "damage_mode_requests": sum(damage),
        "damage_mode_fraction": sum(damage) / 200,
        "max_lesion_candidate_opportunities": sum(damage) * 7,
        "rollout_steps_mean": statistics.mean(steps),
        "rollout_steps_min": min(steps),
        "rollout_steps_max": max(steps),
    }


def group_credit_toy(
    n: int = 704,
    p: float = 0.25,
    q_harmful: float = 0.5,
    trials: int = 100000,
) -> dict[str, float]:
    """Equal-magnitude additive toy only: harmful=-1, beneficial=+1."""
    g = torch.Generator(device="cpu").manual_seed(20260918)
    harmful_pruned = 0
    beneficial_pruned = 0
    done = 0
    chunk = 1000
    while done < trials:
        m = min(chunk, trials - done)
        signs = torch.where(
            torch.rand((m, n - 1), generator=g) < q_harmful,
            -torch.ones((m, n - 1), dtype=torch.int8),
            torch.ones((m, n - 1), dtype=torch.int8),
        )
        selected = torch.rand((m, n - 1), generator=g) < p
        other = (signs * selected).sum(dim=1)
        harmful_pruned += int(((other - 1) <= 0).sum())
        beneficial_pruned += int(((other + 1) <= 0).sum())
        done += m
    ph = harmful_pruned / trials
    pb = beneficial_pruned / trials
    return {
        "n": n,
        "p": p,
        "q_harmful": q_harmful,
        "trials": trials,
        "p_prune_given_included_harmful": ph,
        "p_prune_given_included_beneficial": pb,
        "selectivity_gap": ph - pb,
    }


if __name__ == "__main__":
    print(
        "reference_domain_seed_main_manual_seed_1",
        domain_seed(torch.Generator().manual_seed(1)),
    )
    print("minimal_support_probe", minimal_support_probe())
    print("rng_horizon_audit", rng_horizon_audit())
    print("cpu_schedule", cpu_schedule())
    print("group_credit_toy", group_credit_toy())
