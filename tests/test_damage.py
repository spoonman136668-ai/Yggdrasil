import torch

from yggdrasil.damage import center_lesion, dropout_live_cells, rectangular_lesion


def _live_square() -> torch.Tensor:
    state = torch.zeros((1, 8, 9, 9), dtype=torch.float32)
    state[:, :, 2:7, 2:7] = 1.0
    return state


def test_rectangular_lesion_zeros_region_without_mutating_source() -> None:
    state = _live_square()
    original = state.clone()

    damaged = rectangular_lesion(state, top=3, left=4, height=2, width=3)

    assert torch.equal(state, original)
    assert torch.count_nonzero(damaged[:, :, 3:5, 4:7]) == 0
    assert torch.count_nonzero(damaged) < torch.count_nonzero(state)


def test_center_lesion_targets_active_bounding_box() -> None:
    state = _live_square()

    damaged = center_lesion(state, height_fraction=0.4, width_fraction=0.4, alive_channel=3)

    assert torch.count_nonzero(damaged[:, :, 3:5, 3:5]) == 0
    assert torch.count_nonzero(damaged[:, :, 2, 2]) > 0


def test_dropout_fraction_zero_is_identity_copy() -> None:
    state = _live_square()
    damaged = dropout_live_cells(state, fraction=0.0, alive_channel=3)

    assert torch.equal(damaged, state)
    assert damaged.data_ptr() != state.data_ptr()


def test_dropout_fraction_one_removes_every_live_cell() -> None:
    state = _live_square()
    damaged = dropout_live_cells(state, fraction=1.0, alive_channel=3)

    assert torch.count_nonzero(damaged) == 0


def test_seeded_dropout_is_deterministic() -> None:
    state = _live_square()
    generator_a = torch.Generator().manual_seed(99)
    generator_b = torch.Generator().manual_seed(99)

    damaged_a = dropout_live_cells(state, fraction=0.4, generator=generator_a)
    damaged_b = dropout_live_cells(state, fraction=0.4, generator=generator_b)

    assert torch.equal(damaged_a, damaged_b)
