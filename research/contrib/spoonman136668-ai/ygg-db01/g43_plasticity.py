"""G43 bounded synthetic warm-start plasticity intervention, NOT primary science.

Three frozen mixing arms baseline/25%/50% seeded initial genome.
Original learned source genome and all original G38-G42 results unchanged.
The target rule remains private to the toy world; reward decoding is engineered.
"""
from dataclasses import dataclass
import json
from native_dg1a import DG1APrototype, SharedGenome, seeded_genome
from matched_feedback import matched_feedback
from g38_native_learning import (CUES, NOVEL_CUES, ROUNDS, FRAMES, GRADIENT_CALLS,
                                 MARGIN, action, sensory, perceived_valence,
                                 value, run_development)
from g40_adaptation import accuracy, adapt

ARMS = ("baseline", "blend_25", "blend_50")
MIX = {"baseline": 0.0, "blend_25": 0.25, "blend_50": 0.5}
CONDITIONS = ("mapped", "sham", "no_feedback")
SCHEMA = "yggdrasil.g43.synthetic-plasticity-v1"
PARTS = ("first", "first_bias", "second", "second_bias")

def mix_genomes(source, initial, fraction):
    if type(fraction) is not float or fraction not in (0.0, 0.25, 0.5):
        raise ValueError("YGG_G43_INVALID_FRACTION")
    return SharedGenome(*(tuple((1.0 - fraction) * s + fraction * i
                                 for s, i in zip(getattr(source, p), getattr(initial, p)))
                         for p in PARTS))

@dataclass(frozen=True)
class Result:
    arm: str
    condition: str
    source_before: float
    target_before: float
    source_after: float
    target_after: float
    interactions: int
    feedback_frames: int
    gradient_calls: int
    genome: object

def run(arm, condition):
    if type(arm) is not str or arm not in ARMS:
        raise ValueError("YGG_G43_ARM_INVALID")
    if type(condition) is not str or condition not in CONDITIONS:
        raise ValueError("YGG_G43_CONDITION_INVALID")
    model = DG1APrototype()
    original = run_development("mapped").genome
    genome = mix_genomes(original, seeded_genome(17), MIX[arm])
    source_before = accuracy(model, genome, NOVEL_CUES, 1)
    target_before = accuracy(model, genome, NOVEL_CUES, -1)
    initial = model.initial_state()
    for i in range(ROUNDS):
        for cue in CUES:
            chosen = action(model, genome, cue)
            if i % 4 == 0:
                chosen = -chosen
            correct = -(1 if cue > 0 else -1)
            wave = matched_feedback(int(chosen == correct), condition,
                                    length=FRAMES, seed=100 + i)
            decoded = perceived_valence(model, genome, wave)
            target = (chosen * decoded * MARGIN if decoded
                      else value(model, genome, cue))
            for _ in range(GRADIENT_CALLS):
                genome = model.fit_one_cell(initial, sensory(cue), genome,
                                            1, 1, target, learning_rate=0.5)
    count = ROUNDS * len(CUES)
    return Result(arm, condition, source_before, target_before,
                  accuracy(model, genome, NOVEL_CUES, 1),
                  accuracy(model, genome, NOVEL_CUES, -1),
                  count, count * FRAMES, count * GRADIENT_CALLS, genome)

def build_report():
    rows = []
    for arm in ARMS:
        for condition in CONDITIONS:
            r = run(arm, condition)
            rows.append({
                "arm": arm, "condition": condition,
                "source_before": r.source_before, "target_before": r.target_before,
                "source_after": r.source_after, "target_after": r.target_after,
                "target_delta": round(r.target_after - r.target_before, 12),
                "interactions": r.interactions, "feedback_frames": r.feedback_frames,
                "gradient_calls": r.gradient_calls,
            })
    get = lambda arm, cond: next(x for x in rows if x["arm"] == arm and x["condition"] == cond)
    baseline = get("baseline", "mapped")
    candidates = [get(a, "mapped") for a in ("blend_25", "blend_50")]
    # This classification is diagnostic only; preserve all losing arms and
    # explicitly account for source-task retention before and after.
    eligible = [r for r in candidates if
                r["target_after"] > baseline["target_after"] and
                r["source_before"] >= baseline["source_before"]]
    verdict = ("DEV_INTERVENTION_IMPROVES_TARGET_WITH_PRE_ADAPTATION_SOURCE_RETENTION"
               if eligible else "NO_QUALIFYING_DEVELOPMENT_IMPROVEMENT")
    return {
        "schema": SCHEMA, "evidence": "SELF_AUTHORED_SYNTHETIC_DEV_ONLY",
        "diagnostic_verdict": verdict,
        "primary_execution_allowed": False,
        "scientific_acceptance": "NO_GO",
        "genuine_transfer": "UNVERIFIED",
        "reward_decoder": "FIXED_ENGINEERED_PERIODICITY",
        "cost_caveat": "all arms include same G38 source pretraining; mixing itself adds arithmetic",
        "rows": rows,
    }

def report_json():
    return json.dumps(build_report(), sort_keys=True,
                      separators=(",", ":"), allow_nan=False)

if __name__ == "__main__":
    print("YGG_G43_DEV_PLASTICITY_JSON=" + report_json(), flush=True)
