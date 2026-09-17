import pytest
import torch

from yggdrasil.nca import NCAConfig, NeuralCellularAutomaton, make_seed_state
from yggdrasil.resources import (
    model_parameter_count,
    model_parameter_nbytes,
    snapshot_resources,
    tensor_nbytes,
)


def test_tensor_nbytes_matches_shape_and_dtype() -> None:
    tensor = torch.zeros((2, 3, 4), dtype=torch.float32)

    assert tensor_nbytes(tensor) == 2 * 3 * 4 * 4


def test_model_parameter_accounting_is_positive_and_consistent() -> None:
    model = NeuralCellularAutomaton(NCAConfig(state_channels=16, hidden_channels=32))

    count = model_parameter_count(model)
    nbytes = model_parameter_nbytes(model)

    assert count > 0
    assert nbytes == count * 4
    assert model.parameter_count() == count


def test_resource_snapshot_separates_genome_resident_and_active_state() -> None:
    model = NeuralCellularAutomaton(NCAConfig(state_channels=16, hidden_channels=32))
    state = make_seed_state(batch_size=1, channels=16, height=10, width=10)

    snapshot = snapshot_resources(model=model, state=state, active_cells=1)

    assert snapshot.genome_parameters == model_parameter_count(model)
    assert snapshot.resident_state_bytes == 1 * 16 * 10 * 10 * 4
    assert snapshot.active_state_bytes_estimate == 16 * 4
    assert snapshot.active_cells == 1


def test_resource_snapshot_rejects_impossible_active_cell_count() -> None:
    model = NeuralCellularAutomaton()
    state = make_seed_state(batch_size=1, channels=16, height=5, width=5)

    with pytest.raises(ValueError, match="exceeds fixed phenotype grid capacity"):
        snapshot_resources(model=model, state=state, active_cells=26)
