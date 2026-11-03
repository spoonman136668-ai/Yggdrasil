"""G38: synthetic development-only closed-loop DG1A native-policy fixture.

A fixed external periodicity readout and the existing supervised-gradient
plasticity are engineered scaffolding, NOT native reward understanding.
The environment's hidden correct action stays inside the world adapter;
learner updates receive only chosen actions and sensory waveforms.
No G35 protected data, scientific acceptance, or production use.
"""
from dataclasses import dataclass
import math
from native_dg1a import DG1APrototype, seeded_genome
from matched_feedback import PATTERN, matched_feedback

CONDITIONS = frozenset(("mapped", "reversed", "sham", "no_feedback"))
ROUNDS, FRAMES, GRADIENT_CALLS = 16, 16, 8
CUES, NOVEL_CUES = (-1.0, 1.0), (-0.5, 0.5)
CENTER, MARGIN = (1, 1), 0.09

@dataclass(frozen=True)
class DevelopmentResult:
    condition: str
    baseline_score: float
    post_train_score: float
    novel_magnitude_score: float
    genome: object
    interactions: int
    feedback_frames: int
    gradient_calls: int
    cellular_step_calls: int
    evidence_class: str = "SYNTHETIC_DEVELOPMENT_ONLY_NOT_PRIMARY_SCIENCE"

def sensory(sample):
    if type(sample) not in (int, float) or not math.isfinite(sample) or abs(sample) > 1:
        raise ValueError("YGG_G38_SENSORY_INVALID")
    return tuple(tuple(float(sample) if (y, x) == CENTER else 0.0
                       for x in range(4)) for y in range(4))

def value(model, genome, cue):
    return model.step(model.initial_state(), sensory(cue), genome)[1][1][2]

def action(model, genome, cue):
    return 1 if value(model, genome, cue) >= 0.0 else -1

def world_feedback(cue, chosen, condition, round_index):
    """Private-to-world synthetic correct action; only waveform is returned."""
    correct = 1 if cue > 0 else -1
    return matched_feedback(int(chosen == correct), condition,
                            length=FRAMES, seed=100 + round_index)

def perceived_valence(model, genome, waveform):
    """Read a periodicity tag from native local sensory responses.

    This is an engineered decoder, NOT a learned temporal representation.
    A zero-energy waveform is a separate ablation, never energy matched.
    """
    if type(waveform) is not tuple or len(waveform) != FRAMES or any(
            type(v) not in (int, float) or not math.isfinite(v) for v in waveform):
        raise ValueError("YGG_G38_WAVE_INVALID")
    if waveform == (0.0,) * FRAMES:
        return 0
    if sorted(waveform) != sorted(PATTERN * (FRAMES // 4)):
        raise ValueError("YGG_G38_MARGINAL_DRIFT")
    state = model.initial_state()
    response = tuple(model.step(state, sensory(v), genome)[1][1][2] for v in waveform)
    if len(set(response)) != 3:
        raise ValueError("YGG_G38_SENSORY_COLLAPSED")
    return 1 if all(response[i] == response[i + 4]
                    for i in range(FRAMES - 4)) else -1

def score(model, genome, cues):
    """Evaluator only, not a learning input."""
    return sum(action(model, genome, cue) == (1 if cue > 0 else -1)
               for cue in cues) / len(cues)

def run_development(condition):
    if type(condition) is not str or condition not in CONDITIONS:
        raise ValueError("YGG_G38_CONTROL_INVALID")
    model, genome = DG1APrototype(), seeded_genome(17)
    initial = model.initial_state()
    baseline = score(model, genome, CUES)
    for i in range(ROUNDS):
        for cue in CUES:
            chosen = action(model, genome, cue)
            if i % 4 == 0:  # fixed and equally budgeted exploration
                chosen = -chosen
            wave = world_feedback(cue, chosen, condition, i)
            feedback = perceived_valence(model, genome, wave)
            # No source answer, outcome bit, or protected labels in the update.
            target = (chosen * feedback * MARGIN if feedback
                      else value(model, genome, cue))
            for _ in range(GRADIENT_CALLS):
                genome = model.fit_one_cell(initial, sensory(cue), genome,
                                            1, 1, target, learning_rate=0.5)
    count = ROUNDS * len(CUES)
    return DevelopmentResult(condition, baseline,
                             score(model, genome, CUES),
                             score(model, genome, NOVEL_CUES),
                             genome, count, count * FRAMES,
                             count * GRADIENT_CALLS,
                             count * (1 + FRAMES) + 4)
