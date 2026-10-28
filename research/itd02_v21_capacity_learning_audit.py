"""V21 bounded source-only forensic audit of local transport vs readout fit.

NO learner modifications. Only public source-tag pulses and V18 external toy
feedback. Reports information capacity and supervised ridge upper bounds;
not native learning, original-world first-use, or scientific admission.
"""
import hashlib
import itertools
import json
import math
import subprocess
from pathlib import Path

from research.itd02_v18_intermediate_plasticity_audit import (
    target, ridge_predict, linear_solve, RIDGE,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, ACTION_SITES, PUBLIC_CUES, CELLS, CHANNELS, site_pulses,
)
from yggdrasil.itd02_v18_intermediate_plasticity_dev import (
    HEAD_FEATURES, HOPS, INITIAL_GAIN, forward_local,
)
from yggdrasil.itd02_v20_causal_credit_dev import (
    ResponsibilityGatedRingDev,
)

PARENT = "f5fd77ef7b56c84cf7d8e848a05eee3e2411e56f"
PREREG = "2cfff46b41ea63083e155f2595ac1ce9c8dec1e9"
ORIGINAL_BLOBS = {
    "yggdrasil/itd02_native_task_bridge_dev.py":
        "71eff80e3cfabb627e9d08d558b63f4043ce1fd5",
    "yggdrasil/itd02_local_ring_memory_dev.py":
        "1db0835d5c99456bcf99a013d4836f49314a9d39",
    "yggdrasil/itd02_v17_neighbor_carried_learner_dev.py":
        "4e3c77797e66df3a26742d23d18f038644891e55",
    "yggdrasil/itd02_v18_intermediate_plasticity_dev.py":
        "711391944be7bd94f1898005d1233bfe52a6f216",
    "research/itd02_v18_intermediate_plasticity_audit.py":
        "7a8f361ff13cf75f716c544add192c2ff9c5aae9",
    "yggdrasil/itd02_v20_causal_credit_dev.py":
        "c7eb9cfc0a4820400fb3c8b78febeb11ae035570",
    "research/itd02_v20_responsibility_gated_audit.py":
        "5ebcfc262016999c39e3b34a48e732d7dabebbb7",
}
PUBLIC_HISTORIES = tuple(itertools.product(PUBLIC_CUES, ACTIONS))
CONTEXTS = tuple(itertools.product(PUBLIC_CUES, ACTIONS, ACTIONS))
GAIN = [[INITIAL_GAIN] * CHANNELS for _ in range(CELLS)]
ROUND_DIGITS = 12


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def git(*args):
    return subprocess.check_output(
        ("git",) + args, cwd=Path(__file__).resolve().parents[1],
        text=True,
    ).strip()


def verify_source():
    for sha in (PARENT, PREREG):
        assert git("merge-base", "--is-ancestor", sha, "HEAD") == ""
    for path, expected_blob in ORIGINAL_BLOBS.items():
        assert git("hash-object", path) == expected_blob, (
            "FROZEN_LEARNER_OR_TOY_SOURCE_DRIFT", path)
    assert CELLS == 8 and CHANNELS == 7 and HOPS == 4
    assert ACTION_SITES == (0, 2, 5) and HEAD_FEATURES == 20
    assert len(PUBLIC_HISTORIES) == 12 and len(CONTEXTS) == 36
    assert RIDGE == 1e-6


def local_channels(cue, first, action, *, hops, retained):
    """Original source-site pulses, zero-mask chosen tags, original forward_local."""
    if not 0 <= hops <= HOPS:
        raise ValueError("INVALID_HOP_COUNT")
    if type(retained) not in (tuple, list) or any(
            type(j) is not int or j not in range(CHANNELS) for j in retained):
        raise ValueError("INVALID_MASK_CHANNEL")
    retained_set = set(retained)
    if len(retained_set) != len(retained):
        raise ValueError("DUPLICATE_MASK_CHANNEL")
    source = site_pulses(cue, first)
    for row in source:
        for j in range(CHANNELS):
            if j not in retained_set:
                row[j] = 0.0
    result, _eligibility, messages = forward_local(source, GAIN, hops=hops)
    assert messages == CELLS * 2 * CHANNELS * hops
    return result[ACTION_SITES[ACTIONS.index(action)]]


def design_features(cue, first, action, *, hops=4, retained=tuple(range(7))):
    """EXACT original V18/V20 reward-head feature sequence, no world law."""
    channels = local_channels(cue, first, action, hops=hops, retained=retained)
    features = [1.0] + list(channels) + [
        channels[cue_idx] * channels[4 + first_idx]
        for cue_idx in range(4) for first_idx in range(3)
    ]
    assert len(features) == HEAD_FEATURES
    assert all(math.isfinite(v) for v in features)
    return features


def rank(rows, *, tol=1e-9):
    """Deterministic Gaussian row-rank; source-only numerical witness."""
    if not rows:
        return 0
    columns = len(rows[0])
    assert all(len(row) == columns for row in rows)
    a = [list(map(float, row)) for row in rows]
    next_row = 0
    for column in range(columns):
        candidates = range(next_row, len(a))
        if next_row >= len(a):
            break
        pivot = max(candidates, key=lambda r: (abs(a[r][column]), -r))
        if abs(a[pivot][column]) <= tol:
            continue
        a[next_row], a[pivot] = a[pivot], a[next_row]
        div = a[next_row][column]
        for col in range(column, columns):
            a[next_row][col] /= div
        for row in range(next_row + 1, len(a)):
            ratio = a[row][column]
            if ratio:
                for col in range(column, columns):
                    a[row][col] -= ratio * a[next_row][col]
        next_row += 1
    return next_row


def capacity(*, hops, retained):
    """Distinct site-level public context codes and design matrix rank."""
    result = {}
    for action in ACTIONS:
        local_vectors = [
            local_channels(cue, first, action, hops=hops, retained=retained)
            for cue, first in PUBLIC_HISTORIES
        ]
        identities = len({tuple(v) for v in local_vectors})
        features = [
            design_features(cue, first, action, hops=hops, retained=retained)
            for cue, first in PUBLIC_HISTORIES
        ]
        result[action] = {
            "action_site": ACTION_SITES[ACTIONS.index(action)],
            "distinct_local_histories": identities,
            "local_feature_rank": rank(features),
        }
    return result


def ridge_head_predict(rows, targets, probe):
    """A conventional supervised optimizer on the SAME local V20 feature rows."""
    assert len(rows) == len(targets) and rows and len(probe) == HEAD_FEATURES
    assert all(len(row) == HEAD_FEATURES for row in rows)
    gram = [
        [
            sum(x[i] * x[j] for x in rows) + (RIDGE if i == j else 0.0)
            for j in range(HEAD_FEATURES)
        ]
        for i in range(HEAD_FEATURES)
    ]
    rhs = [sum(x[i] * y for x, y in zip(rows, targets))
           for i in range(HEAD_FEATURES)]
    weights = linear_solve(gram, rhs)
    predicted = sum(x * w for x, w in zip(probe, weights))
    assert math.isfinite(predicted)
    return predicted


def all_data_fit(*, nonlinear, hops, retained):
    """Fits on all 12 identities *per head*; capacity only, not transfer."""
    total = 0.0
    for action in ACTIONS:
        train = [
            design_features(cue, first, action, hops=hops, retained=retained)
            for cue, first in PUBLIC_HISTORIES
        ]
        values = [target(cue, first, action, nonlinear=nonlinear)
                  for cue, first in PUBLIC_HISTORIES]
        # Ordinary full-data fit must not be reported as heldout performance.
        for index, probe in enumerate(train):
            pred = ridge_head_predict(train, values, probe)
            total += abs(pred - values[index])
    return total


def leave_one_out(*, nonlinear, hops):
    """Same selected reward head gets 11 examples, not other heads' 24."""
    evidence = []
    for heldout in CONTEXTS:
        cue, first, action = heldout
        same_head_training = [
            (c, f) for c, f in PUBLIC_HISTORIES if (c, f) != (cue, first)
        ]
        assert len(same_head_training) == 11
        rows = [
            design_features(c, f, action, hops=hops)
            for c, f in same_head_training
        ]
        values = [
            target(c, f, action, nonlinear=nonlinear)
            for c, f in same_head_training
        ]
        pred = ridge_head_predict(
            rows, values, design_features(cue, first, action, hops=hops))
        expected = target(*heldout, nonlinear=nonlinear)
        evidence.append({
            "cue": cue, "actual_first": first,
            "selected_second": action, "heldout_reward": round(expected, 12),
            "local_ridge_prediction": round(pred, 12),
            "local_absolute_error": round(abs(expected - pred), 12),
            "same_head_training_count": len(same_head_training),
            "other_action_training_count_disallowed": 24,
        })
    return evidence


def main():
    verify_source()
    # Strict empirical cold checkpoint for original V20, with native identity.
    unchanged = ResponsibilityGatedRingDev()
    identity = unchanged.native_ids
    checkpoint = unchanged.checkpoint()
    assert ResponsibilityGatedRingDev.restore(checkpoint).checkpoint() == checkpoint
    assert unchanged.native_ids == identity

    hops = {}
    for h in range(HOPS + 1):
        hops[str(h)] = capacity(hops=h, retained=tuple(range(CHANNELS)))
    masks_by_budget = {str(k): 0 for k in range(CHANNELS + 1)}
    valid_masks = []
    for k in range(CHANNELS + 1):
        for mask in itertools.combinations(range(CHANNELS), k):
            current = capacity(hops=HOPS, retained=mask)
            if all(
                value["distinct_local_histories"] == len(PUBLIC_HISTORIES) and
                value["local_feature_rank"] == len(PUBLIC_HISTORIES)
                for value in current.values()
            ):
                masks_by_budget[str(k)] += 1
                valid_masks.append(mask)
    best_mask = min(valid_masks, key=lambda mask: (len(mask), mask)) if valid_masks else None

    all_fit = {}
    loo = {}
    records = []
    for family, nonlinear in (("additive", False), ("nonadditive", True)):
        all_fit[family] = {
            str(h): all_data_fit(
                nonlinear=nonlinear, hops=h, retained=tuple(range(CHANNELS)))
            for h in range(HOPS + 1)
        }
        loo[family] = {}
        for h in range(HOPS + 1):
            rows = leave_one_out(nonlinear=nonlinear, hops=h)
            loo[family][str(h)] = sum(r["local_absolute_error"] for r in rows)
            records += [{
                "family": family, "hops": h, **r
            } for r in rows]
        pooled = []
        for heldout in CONTEXTS:
            train = [case for case in CONTEXTS if case != heldout]
            assert len(train) == 35
            predicted = ridge_predict(train, heldout, nonlinear=nonlinear)
            pooled.append(abs(target(*heldout, nonlinear=nonlinear) - predicted))
        loo[family]["pooled_public_interaction_35"] = sum(pooled)

    compressed_fit = None
    if best_mask is not None:
        compressed_fit = {
            family: all_data_fit(
                nonlinear=(family == "nonadditive"),
                hops=HOPS, retained=best_mask)
            for family in ("additive", "nonadditive")
        }
    all_full = all(v["distinct_local_histories"] == 12 and
                   v["local_feature_rank"] == 12
                   for v in hops[str(HOPS)].values())
    classification = (
        "V21_FULL_HOP_CAPACITY_SUFFICIENT_LEARNING_FAILURE_DOWNSTREAM__NO_SCIENCE"
        if all_full else
        "V21_TRANSPORT_REPRESENTATION_BOTTLENECK_FOUND__NO_SCIENCE"
    )
    receipt = {
        "schema": "ygg.itd02.v21.transport_capacity_and_head_fragmentation.source_only.v1",
        "classification": classification,
        "source_only": True, "scientific_first_use": False,
        "original_world_training": False, "original_native_model_unchanged": True,
        "native_ring_cells": CELLS, "fixed_source_public_channels": CHANNELS,
        "public_history_count_per_head": len(PUBLIC_HISTORIES),
        "full_contexts": len(CONTEXTS),
        "max_neighbor_hops": HOPS,
        "per_hop_per_head_capacity": hops,
        "exhaustive_channel_subsets_checked": 2**CHANNELS,
        "identity_and_rank_preserving_masks_by_budget": masks_by_budget,
        "min_mask_channels_for_all_site_full_rank": (
            None if best_mask is None else len(best_mask)),
        "lexicographic_min_mask": best_mask,
        "all_data_per_head_ridge_error": all_fit,
        "all_data_compressed_min_mask_ridge_error": compressed_fit,
        "loo_per_head_and_pooled_ridge_error": loo,
        "source_only_record_sha256": hashlib.sha256(canonical(records)).hexdigest(),
        "unmodified_v20_checkpoint_bytes": len(checkpoint),
        "unmodified_v20_checkpoint_cold_equal": True,
        "source_original_v20_model_blob": ORIGINAL_BLOBS[
            "yggdrasil/itd02_v20_causal_credit_dev.py"],
        "qualifier": "REPRESENTATION_AND_CONVENTIONAL_READOUT_DIAGNOSTIC_NOT_NATIVE_SCIENCE",
    }
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
