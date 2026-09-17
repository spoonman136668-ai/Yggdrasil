import torch

from yggdrasil.target import TargetSpec, make_target, target_identity


def test_target_is_deterministic_and_hidden_channels_zero() -> None:
    spec = TargetSpec(radius=3)
    target_a = make_target(batch_size=1, channels=8, height=15, width=15, spec=spec)
    target_b = make_target(batch_size=1, channels=8, height=15, width=15, spec=spec)

    assert torch.equal(target_a, target_b)
    assert torch.count_nonzero(target_a[:, 4:]) == 0
    assert torch.count_nonzero(target_a[:, 3]) > 0


def test_target_identity_changes_with_geometry() -> None:
    spec = TargetSpec(radius=3)

    assert target_identity(spec, height=15, width=15) != target_identity(spec, height=17, width=15)
