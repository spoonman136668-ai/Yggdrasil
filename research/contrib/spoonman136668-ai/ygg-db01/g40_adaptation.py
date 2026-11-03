"""G40: synthetic rule-reversal adaptation diagnostic; no primary transfer science.

The environment alone owns the reversed task rule. The learner sees only
action, local cue and matched feedback samples. Its reward decoder remains
explicitly engineered; this is not self-organizing reward comprehension.
"""
from dataclasses import dataclass
from native_dg1a import DG1APrototype, seeded_genome
from matched_feedback import matched_feedback
from g38_native_learning import (CUES, NOVEL_CUES, ROUNDS, FRAMES,
                                 GRADIENT_CALLS, MARGIN, action, sensory,
                                 perceived_valence, value)

CONDITIONS = ("mapped", "reversed", "sham", "no_feedback", "decoder_ablation")

@dataclass(frozen=True)
class G40Result:
    condition: str
    pretrained: bool
    source_before: float
    target_before: float
    target_after: float
    interactions: int
    frames: int
    gradient_calls: int
    genome: object
    evidence_class: str = "SYNTHETIC_DEV_ADAPTATION_NOT_SCIENTIFIC_TRANSFER"

def accuracy(model, genome, cues, rule):
    return sum(action(model, genome, cue) == rule * (1 if cue > 0 else -1)
               for cue in cues) / len(cues)

def adapt(condition, pretrained=True):
    if type(condition) is not str or condition not in CONDITIONS:
        raise ValueError("YGG_G40_CONDITION")
    if type(pretrained) is not bool:
        raise ValueError("YGG_G40_PRETRAINED")
    model = DG1APrototype()
    if pretrained:
        # G38 source-task learning is a separate synthetic training phase.
        from g38_native_learning import run_development
        genome = run_development("mapped").genome
    else:
        genome = seeded_genome(17)
    before_source = accuracy(model, genome, NOVEL_CUES, 1)
    before_target = accuracy(model, genome, NOVEL_CUES, -1)
    initial = model.initial_state()
    for i in range(ROUNDS):
        for cue in CUES:
            chosen = action(model, genome, cue)
            if i % 4 == 0:   # same bounded exploration schedule as G38
                chosen = -chosen
            # Private target-task world rule is reversed; only waveform leaves it.
            correct = -(1 if cue > 0 else -1)
            wave = matched_feedback(int(chosen == correct),
                                    "no_feedback" if condition == "decoder_ablation"
                                    else condition, length=FRAMES, seed=100 + i)
            decoded = 0 if condition == "decoder_ablation" else perceived_valence(model, genome, wave)
            target = (chosen * decoded * MARGIN if decoded else
                      value(model, genome, cue))
            for _ in range(GRADIENT_CALLS):
                genome = model.fit_one_cell(initial, sensory(cue), genome, 1, 1,
                                            target, learning_rate=0.5)
    interactions = ROUNDS * len(CUES)
    return G40Result(condition, pretrained, before_source, before_target,
                     accuracy(model, genome, NOVEL_CUES, -1), interactions,
                     interactions * FRAMES, interactions * GRADIENT_CALLS,
                     genome)
