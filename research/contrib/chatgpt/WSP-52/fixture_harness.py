"""WSP52 non-scientific fixture harness with an explicit learner/evaluator seam.

Do not expose the generator World or evaluation records to a learner's
constructor, observe() or predict(); all unseen cases stay with evaluator.
This is not a security sandbox or an accepted science run.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from source import Observation, SourceWorld
from controls import WholeStreamTable, ErasedControl
from direct_writer import DirectWeightWriter


@dataclass(frozen=True)
class Score:
    total: int
    correct: int
    abstentions: int
    wrong_confident: int

    def __post_init__(self):
        assert self.correct + self.abstentions + self.wrong_confident == self.total


def learn_observations(learner, evidence: tuple[Observation, ...]) -> None:
    """Pass only the documented, immutable learner-facing observations."""
    for row in evidence:
        assert type(row) is Observation
        learner.observe(row)


def score_observations(learner, heldout: tuple[Observation, ...]) -> Score:
    """The learner gets before + undelimited raw bits, never target after."""
    correct = unknown = wrong = 0
    for item in heldout:
        response = learner.predict(item.before, item.acoustic_bits)
        if response is None:
            unknown += 1
        elif type(response) is tuple and response == item.after:
            correct += 1
        else:
            wrong += 1
    return Score(len(heldout), correct, unknown, wrong)


def run_selftest_controls(world: SourceWorld) -> dict:
    """Allowed ONLY on SELFTEST worlds; does not run registered DEV/PRIMARY."""
    if world.cohort != "SELFTEST":
        raise PermissionError("fixtures cannot access registered research cohorts")
    receipts = {"source": world.source_receipt(), "arms": {}}
    for name, model in (("whole_stream", WholeStreamTable()),
                        ("erased", ErasedControl())):
        learn_observations(model, world.phase_a)
        phase_a = score_observations(model, world.heldout_a)
        learn_observations(model, world.phase_b)
        phase_b = score_observations(model, world.heldout_b)
        retention = score_observations(model, world.heldout_a)
        arm = {"phase_a": asdict(phase_a), "phase_b": asdict(phase_b),
               "a_retention_after_b": asdict(retention),
               "exposed_actions": model.action_experiences,
               "persistent_capacity_bits_upper_bound": model.capacity_bits()}
        if name == "whole_stream":
            restored = WholeStreamTable.restore(model.snapshot())
            if (score_observations(restored, world.heldout_a) != retention
                or score_observations(restored, world.heldout_b) != phase_b):
                raise AssertionError("cold restore changed predictions")
            arm["cold_restore_parity"] = True
        receipts["arms"][name] = arm
    return receipts

def run_selftest_writer(world: SourceWorld) -> dict:
    """Only fixture seeds, no DEV/PRIMARY scientific execution."""
    if world.cohort != 'SELFTEST':
        raise PermissionError('registered research cohorts are not fixtures')
    model = DirectWeightWriter()
    learn_observations(model, world.phase_a)
    a = score_observations(model, world.heldout_a)
    learn_observations(model, world.phase_b)
    b = score_observations(model, world.heldout_b)
    retention = score_observations(model, world.heldout_a)
    restored = DirectWeightWriter.restore(model.snapshot())
    if (score_observations(restored, world.heldout_a) != retention or
            score_observations(restored, world.heldout_b) != b):
        raise AssertionError('direct weight writer cold restore changed predictions')
    return {'source':world.source_receipt(),
            'arm': 'pure_direct_heuristic',
            'phase_a': asdict(a), 'phase_b': asdict(b),
            'a_retention_after_b': asdict(retention),
            'exposed_actions': model.actions,
            'informative_experiences': model.informative,
            'gradient_steps': 0,
            'numeric_weights': model.numeric_weight_count(),
            'persistent_capacity_bits_upper_bound': model.capacity_bits(),
            'cold_restore_parity': True}
