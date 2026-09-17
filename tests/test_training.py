import torch

from yggdrasil.nca import NCAConfig, NeuralCellularAutomaton, make_seed_state
from yggdrasil.target import TargetSpec, make_target
from yggdrasil.training import (
    TrainingConfig,
    evaluate_growth_and_recovery,
    evaluate_persistence,
    train,
)


def test_tiny_growth_training_executes_and_records() -> None:
    torch.manual_seed(0)
    model = NeuralCellularAutomaton(
        NCAConfig(state_channels=8, hidden_channels=16, fire_rate=1.0, max_steps=8)
    )
    seed = make_seed_state(batch_size=1, channels=8, height=15, width=15)
    target = make_target(
        batch_size=1,
        channels=8,
        height=15,
        width=15,
        spec=TargetSpec(radius=3),
    )
    config = TrainingConfig(
        iterations=3,
        learning_rate=1e-3,
        steps_min=2,
        steps_max=3,
        batch_size=2,
        pool_size=4,
        record_every=1,
        seed=0,
    )

    summary = train(model=model, seed_state=seed, target=target, config=config)

    assert summary.iterations == 3
    assert len(summary.history) == 3
    assert summary.final_recorded_loss >= 0


def test_tiny_persistence_and_regeneration_training_execute() -> None:
    for variant in ("persistence", "regeneration"):
        torch.manual_seed(0)
        model = NeuralCellularAutomaton(
            NCAConfig(state_channels=8, hidden_channels=16, fire_rate=1.0, max_steps=8)
        )
        seed = make_seed_state(batch_size=1, channels=8, height=15, width=15)
        target = make_target(
            batch_size=1,
            channels=8,
            height=15,
            width=15,
            spec=TargetSpec(radius=3),
        )
        config = TrainingConfig(
            variant=variant,
            iterations=2,
            learning_rate=1e-3,
            steps_min=2,
            steps_max=2,
            batch_size=2,
            pool_size=4,
            record_every=1,
            seed=0,
        )

        summary = train(model=model, seed_state=seed, target=target, config=config)

        assert summary.variant == variant


def test_evaluation_emits_recovery_resource_and_lesion_validity_fields() -> None:
    model = NeuralCellularAutomaton(
        NCAConfig(state_channels=8, hidden_channels=16, fire_rate=1.0, max_steps=8)
    )
    seed = make_seed_state(batch_size=1, channels=8, height=15, width=15)
    target = make_target(
        batch_size=1,
        channels=8,
        height=15,
        width=15,
        spec=TargetSpec(radius=3),
    )

    result = evaluate_growth_and_recovery(
        model=model,
        seed_state=seed,
        target=target,
        growth_steps=2,
        recovery_steps=2,
        seed=1,
        lesion_height_fraction=0.5,
        lesion_width_fraction=0.5,
    )

    assert len(result["recovery_error_curve"]) == 3
    assert len(result["recovery_active_cell_curve"]) == 3
    assert result["pre_damage_active_cells"] >= result["post_damage_active_cells"]
    assert 0.0 <= result["active_cell_removal_fraction"] <= 1.0
    assert "relative_damage_effect" in result
    assert "resources" in result


def test_persistence_evaluation_emits_drift_fields() -> None:
    model = NeuralCellularAutomaton(
        NCAConfig(state_channels=8, hidden_channels=16, fire_rate=1.0, max_steps=8)
    )
    seed = make_seed_state(batch_size=1, channels=8, height=15, width=15)
    target = make_target(
        batch_size=1,
        channels=8,
        height=15,
        width=15,
        spec=TargetSpec(radius=3),
    )

    result = evaluate_persistence(
        model=model,
        seed_state=seed,
        target=target,
        growth_steps=2,
        persistence_steps=2,
        seed=2,
    )

    assert len(result["error_curve"]) == 3
    assert len(result["active_cell_curve"]) == 3
    assert "visible_state_drift_mse" in result
    assert "max_error_degradation" in result
    assert "resources" in result


def test_training_balanced_loss_mode_records_global_mse_telemetry() -> None:
    torch.manual_seed(7)
    model = NeuralCellularAutomaton(
        NCAConfig(state_channels=8, hidden_channels=16, fire_rate=1.0, max_steps=6)
    )
    seed = make_seed_state(batch_size=1, channels=8, height=9, width=9)
    target = torch.zeros_like(seed)
    target[:, :4, 3:6, 3:6] = 1.0
    config = TrainingConfig(
        variant="growth_only",
        iterations=2,
        learning_rate=1e-3,
        steps_min=2,
        steps_max=2,
        batch_size=2,
        pool_size=2,
        loss_mode="balanced_fg_bg",
        record_every=1,
        seed=3,
    )

    summary = train(model=model, seed_state=seed, target=target, config=config)

    assert summary.loss_mode == "balanced_fg_bg"
    assert "global_morphology_mse" in summary.history[-1]
    assert summary.history[-1]["morphology_loss"] != summary.history[-1]["global_morphology_mse"]
