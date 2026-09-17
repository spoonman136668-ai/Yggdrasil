import math

import pytest
import torch

from yggdrasil.metrics import (
    active_cell_count,
    balanced_morphology_mse,
    ensure_finite,
    mean_update_magnitude,
    morphology_mse,
    normalized_recovery_auc,
    normalized_recovery_fraction,
    recovery_fraction,
    recovery_threshold_step,
    stable_recovery_threshold_step,
)


def test_morphology_mse_uses_visible_channels_only() -> None:
    state = torch.zeros((1, 8, 2, 2), dtype=torch.float32)
    target = torch.zeros_like(state)
    state[:, 0] = 2.0
    state[:, 6] = 100.0

    error = morphology_mse(state, target, visible_channels=4)

    assert error.item() == pytest.approx(1.0)


def test_active_cell_count_uses_alpha_threshold() -> None:
    state = torch.zeros((1, 8, 3, 3), dtype=torch.float32)
    state[:, 3, 0, 0] = 0.2
    state[:, 3, 1, 1] = 0.11
    state[:, 3, 2, 2] = 0.1

    assert active_cell_count(state, alive_channel=3, alive_threshold=0.1) == 2


def test_mean_update_magnitude() -> None:
    before = torch.zeros((1, 4, 2, 2), dtype=torch.float32)
    after = torch.ones_like(before)

    assert mean_update_magnitude(before, after) == pytest.approx(1.0)


def test_recovery_fraction_for_lower_is_better_error() -> None:
    value = recovery_fraction(pre_error=0.1, post_damage_error=0.5, recovered_error=0.3)

    assert value == pytest.approx(0.5)


def test_normalized_recovery_fraction_clamps_over_recovery() -> None:
    value = normalized_recovery_fraction(
        pre_error=0.1,
        post_damage_error=0.5,
        recovered_error=0.0,
    )

    assert value == pytest.approx(1.0)


def test_recovery_fraction_is_nan_when_damage_has_no_effect() -> None:
    value = recovery_fraction(pre_error=0.2, post_damage_error=0.2, recovered_error=0.1)

    assert math.isnan(value)


def test_recovery_threshold_step_returns_first_crossing() -> None:
    step = recovery_threshold_step(
        [0.5, 0.4, 0.3, 0.2, 0.1],
        pre_error=0.1,
        post_damage_error=0.5,
        fraction=0.5,
    )

    assert step == 2


def test_stable_threshold_rejects_transient_crossing() -> None:
    step = stable_recovery_threshold_step(
        [0.5, 0.2, 0.4],
        pre_error=0.1,
        post_damage_error=0.5,
        fraction=0.5,
    )

    assert step is None


def test_stable_threshold_returns_first_persistent_crossing() -> None:
    step = stable_recovery_threshold_step(
        [0.5, 0.4, 0.25, 0.2],
        pre_error=0.1,
        post_damage_error=0.5,
        fraction=0.5,
    )

    assert step == 2


def test_normalized_recovery_auc_is_bounded_for_monotonic_recovery() -> None:
    value = normalized_recovery_auc(
        [0.5, 0.4, 0.3, 0.2, 0.1],
        pre_error=0.1,
        post_damage_error=0.5,
    )

    assert value == pytest.approx(0.5)


def test_non_finite_state_fails_closed() -> None:
    state = torch.zeros((1, 4, 2, 2), dtype=torch.float32)
    state[0, 0, 0, 0] = float("nan")

    with pytest.raises(FloatingPointError, match="non-finite"):
        ensure_finite(state)


def test_balanced_morphology_mse_equalizes_target_regions() -> None:
    state = torch.zeros((1, 4, 2, 2), dtype=torch.float32)
    target = torch.zeros_like(state)
    target[:, :, 0, 0] = 1.0

    value = balanced_morphology_mse(state, target, visible_channels=4)

    assert value.item() == pytest.approx(0.5)


def test_balanced_morphology_mse_rejects_missing_foreground() -> None:
    state = torch.zeros((1, 4, 2, 2), dtype=torch.float32)
    target = torch.zeros_like(state)

    with pytest.raises(ValueError, match="no foreground"):
        balanced_morphology_mse(state, target, visible_channels=4)
