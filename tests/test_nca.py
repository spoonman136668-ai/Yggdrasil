import pytest
import torch

from yggdrasil.nca import NCAConfig, NeuralCellularAutomaton, make_seed_state


def test_seed_state_activates_only_center_alpha() -> None:
    state = make_seed_state(batch_size=2, channels=16, height=9, width=11)

    assert state.shape == (2, 16, 9, 11)
    assert torch.count_nonzero(state) == 2
    assert torch.all(state[:, 3, 4, 5] == 1.0)


def test_perception_preserves_spatial_shape_and_triples_channels() -> None:
    model = NeuralCellularAutomaton(NCAConfig(state_channels=16, fire_rate=1.0))
    state = make_seed_state(batch_size=2, channels=16, height=8, width=10, dtype=torch.float64)
    model = model.to(dtype=torch.float64)

    perceived = model.perceive(state)

    assert perceived.shape == (2, 48, 8, 10)
    assert perceived.dtype == torch.float64


def test_zero_initialized_residual_rule_preserves_seed() -> None:
    model = NeuralCellularAutomaton(NCAConfig(fire_rate=1.0))
    state = make_seed_state(batch_size=1, channels=16, height=9, width=9)

    next_state = model.step(state)

    assert torch.equal(next_state, state)


def test_step_is_deterministic_with_equal_generators() -> None:
    model = NeuralCellularAutomaton(NCAConfig(fire_rate=0.5))
    final_layer = model.update_net[-1]
    assert isinstance(final_layer, torch.nn.Conv2d)
    with torch.no_grad():
        final_layer.weight.fill_(0.05)

    state = make_seed_state(batch_size=1, channels=16, height=9, width=9)
    generator_a = torch.Generator().manual_seed(1234)
    generator_b = torch.Generator().manual_seed(1234)

    result_a = model.step(state, generator=generator_a)
    result_b = model.step(state, generator=generator_b)

    assert torch.equal(result_a, result_b)


def test_run_never_changes_fixed_grid_shape() -> None:
    model = NeuralCellularAutomaton(NCAConfig(fire_rate=1.0, max_steps=10))
    state = make_seed_state(batch_size=3, channels=16, height=7, width=13)

    result = model.run(state, steps=10)

    assert result.shape == state.shape


def test_run_rejects_steps_over_hard_limit() -> None:
    model = NeuralCellularAutomaton(NCAConfig(max_steps=4))
    state = make_seed_state(batch_size=1, channels=16, height=5, width=5)

    with pytest.raises(ValueError, match="steps must be between"):
        model.run(state, steps=5)


def test_alive_mask_marks_neighboring_cells_of_live_seed() -> None:
    model = NeuralCellularAutomaton(NCAConfig(fire_rate=1.0))
    state = make_seed_state(batch_size=1, channels=16, height=7, width=7)

    alive = model.alive_mask(state)

    assert alive.shape == (1, 1, 7, 7)
    assert int(alive.sum().item()) == 9


def test_invalid_state_channel_count_fails_closed() -> None:
    model = NeuralCellularAutomaton(NCAConfig(state_channels=16))
    wrong = torch.zeros((1, 8, 5, 5), dtype=torch.float32)

    with pytest.raises(ValueError, match="expected 16"):
        model.step(wrong)
