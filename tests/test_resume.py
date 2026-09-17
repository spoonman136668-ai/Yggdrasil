from copy import deepcopy

import torch

from yggdrasil.nca import NCAConfig, NeuralCellularAutomaton, make_seed_state
from yggdrasil.resume import ResumableTrainingSession
from yggdrasil.target import TargetSpec, make_target
from yggdrasil.training import TrainingConfig, train


def _fixture(variant="regeneration", iterations=6):
    torch.manual_seed(123)
    model = NeuralCellularAutomaton(
        NCAConfig(state_channels=8, hidden_channels=16, fire_rate=0.5, max_steps=8)
    )
    seed = make_seed_state(batch_size=1, channels=8, height=15, width=15)
    target = make_target(
        batch_size=1,
        channels=8,
        height=15,
        width=15,
        spec=TargetSpec(radius=3),
    )
    cfg = TrainingConfig(
        variant=variant,
        iterations=iterations,
        learning_rate=1e-3,
        steps_min=2,
        steps_max=3,
        batch_size=2,
        pool_size=4,
        damage_probability=0.5,
        damage_min_active_cells=4,
        record_every=1,
        seed=9,
    )
    return model, seed, target, cfg


def _assert_models_equal(left, right):
    for (left_name, left_value), (right_name, right_value) in zip(
        left.state_dict().items(), right.state_dict().items()
    ):
        assert left_name == right_name
        assert torch.equal(left_value, right_value), left_name


def test_resumable_uninterrupted_matches_existing_train_semantics():
    base, seed, target, cfg = _fixture()
    reference = deepcopy(base)
    candidate = deepcopy(base)

    reference_summary = train(
        model=reference,
        seed_state=seed,
        target=target,
        config=cfg,
    )
    session = ResumableTrainingSession(candidate, seed, target, cfg)
    session.advance(cfg.iterations)
    candidate_summary = session.summary()

    _assert_models_equal(reference, candidate)
    assert reference_summary.history == candidate_summary.history


def test_checkpoint_restore_matches_uninterrupted_training():
    base, seed, target, cfg = _fixture(iterations=8)
    uninterrupted = deepcopy(base)
    resumed = deepcopy(base)

    full = ResumableTrainingSession(uninterrupted, seed, target, cfg)
    full.advance(8)

    first = ResumableTrainingSession(resumed, seed, target, cfg)
    first.advance(3)
    checkpoint = first.checkpoint_state()

    restored_model = deepcopy(base)
    restored = ResumableTrainingSession(restored_model, seed, target, cfg)
    restored.load_checkpoint_state(checkpoint)
    restored.advance(5)

    _assert_models_equal(uninterrupted, restored_model)
    assert full.summary().history == restored.summary().history


def test_pool_checkpoint_is_deep_copy():
    model, seed, target, cfg = _fixture(iterations=2)
    session = ResumableTrainingSession(model, seed, target, cfg)
    session.advance(1)
    state = session.checkpoint_state()

    assert state["pool_state_dict"] is not None
    before = state["pool_state_dict"]["storage"].clone()
    session.advance(1)

    assert torch.equal(state["pool_state_dict"]["storage"], before)


def test_resumable_training_supports_balanced_loss_mode() -> None:
    torch.manual_seed(12)
    model = NeuralCellularAutomaton(
        NCAConfig(state_channels=8, hidden_channels=16, fire_rate=1.0, max_steps=6)
    )
    seed = make_seed_state(batch_size=1, channels=8, height=9, width=9)
    target = torch.zeros_like(seed)
    target[:, :4, 3:6, 3:6] = 1.0
    config = TrainingConfig(
        variant="regeneration",
        iterations=2,
        learning_rate=1e-3,
        steps_min=2,
        steps_max=2,
        batch_size=2,
        pool_size=4,
        damage_min_active_cells=4,
        loss_mode="balanced_fg_bg",
        record_every=1,
        seed=5,
    )
    session = ResumableTrainingSession(model, seed, target, config)

    session.advance(2)
    summary = session.summary()

    assert summary.loss_mode == "balanced_fg_bg"
    assert "global_morphology_mse" in summary.history[-1]
