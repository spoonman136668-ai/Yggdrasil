from __future__ import annotations

from dataclasses import dataclass, asdict

from torch import Tensor, nn


@dataclass(frozen=True)
class ResourceSnapshot:
    genome_parameters: int
    genome_parameter_bytes: int
    resident_state_bytes: int
    active_cells: int
    active_state_bytes_estimate: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


def tensor_nbytes(tensor: Tensor) -> int:
    return tensor.numel() * tensor.element_size()


def model_parameter_count(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters())


def model_parameter_nbytes(model: nn.Module) -> int:
    return sum(parameter.numel() * parameter.element_size() for parameter in model.parameters())


def snapshot_resources(
    *,
    model: nn.Module,
    state: Tensor,
    active_cells: int,
) -> ResourceSnapshot:
    if active_cells < 0:
        raise ValueError("active_cells must be non-negative")
    cells_total = state.shape[0] * state.shape[-2] * state.shape[-1]
    if active_cells > cells_total:
        raise ValueError("active_cells exceeds fixed phenotype grid capacity")

    bytes_per_cell = state.shape[1] * state.element_size()
    return ResourceSnapshot(
        genome_parameters=model_parameter_count(model),
        genome_parameter_bytes=model_parameter_nbytes(model),
        resident_state_bytes=tensor_nbytes(state),
        active_cells=active_cells,
        active_state_bytes_estimate=active_cells * bytes_per_cell,
    )
