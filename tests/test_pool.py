import torch

from yggdrasil.nca import make_seed_state
from yggdrasil.pool import StatePool


def test_pool_sample_update_and_reset() -> None:
    seed = make_seed_state(batch_size=1, channels=8, height=9, width=9)
    pool = StatePool(seed, capacity=4)

    indices, batch = pool.sample(
        2,
        generator=torch.Generator().manual_seed(1),
        device="cpu",
    )
    batch = batch + 2
    pool.update(indices, batch)

    all_indices, all_states = pool.sample(
        4,
        generator=torch.Generator().manual_seed(2),
        device="cpu",
    )
    assert all_states.shape == (4, 8, 9, 9)

    pool.reset(all_indices[:1], seed)
