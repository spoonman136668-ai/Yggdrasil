"""CAP04 source-only clock shortcut certificate. No original/registered source use.

RETROSPECTIVE engineering only; 16 observed action labels fit a clock table.
There are NO simulation calls, actions, witnesses, rewards or model updates.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import importlib.util
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
SOURCE_FILE = HERE / "prospective_source.py"
SOURCE_GIT_BLOB = "04d143797ec0c727882e9172df6dbb87e8a931de"
PREREG_GIT_BLOB = "1d79e222685ea1a6889bff49e5bf405a9aed9580"


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def source_guard():
    raw = SOURCE_FILE.read_bytes()
    prereg = (HERE / "prereg.json").read_bytes()
    if git_blob_sha(raw) != SOURCE_GIT_BLOB or git_blob_sha(prereg) != PREREG_GIT_BLOB:
        raise ValueError("CAP04_CLOCK_ORIGINAL_SOURCE_DRIFT")
    spec = importlib.util.spec_from_file_location("_cap04_frozen_schedule", SOURCE_FILE)
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    if (
        source.SCHEMA != "yggdrasil.cap04.prospective-source.v2"
        or source.EPISODES != 96
        or source.BOUNDARIES != (0, 32, 72, 96)
        or len(source.ACTIONS) != 4
        or len(source.ACTION_BLOCKS) != 4
        or source.REGISTERED_DEV != (99917, 99931)
        or source.REGISTERED_PILOT != (100017, 100031)
        or source.REGISTERED_PRIMARY != (100117, 100131, 100151)
        or json.loads(prereg)["authority"]["scientific_first_use_not_authorized"] is not True
    ):
        raise ValueError("CAP04_CLOCK_SOURCE_CONTRACT_DRIFT")
    return source


def action_majority(actions, *, stop=16):
    if type(stop) is not int or not 2 <= stop <= len(actions):
        raise ValueError("CAP04_CLOCK_INVALID_FIT_WINDOW")
    counts = {}
    for t in range(1, stop):
        counts.setdefault(actions[t], Counter())[actions[t - 1]] += 1
    # Deterministic lexical tie break; no hidden source reward or phase.
    return {key: sorted(ct, key=lambda a: (-ct[a], a))[0] for key, ct in counts.items()}


def census():
    source = source_guard()
    actions = tuple(source.action_at(t) for t in range(source.EPISODES))
    if len(actions) != 96 or len(set(actions)) != 4:
        raise ValueError("CAP04_CLOCK_BUDGET_DRIFT")
    if any(actions[t] != actions[t % 16] for t in range(16, 96)):
        raise ValueError("CAP04_CLOCK_PERIOD_DRIFT")
    if any(set(actions[t:t + 4]) != set(source.ACTIONS) for t in range(0, 96, 4)):
        raise ValueError("CAP04_CLOCK_BLOCK_BALANCE_DRIFT")

    first_16 = actions[:16]  # The only public action labels learned.
    action_map = action_majority(actions, stop=16)
    clock_table = {t: first_16[t] for t in range(16)}
    clock4 = {r: action_majority_by_clock(actions, r, 4, stop=16) for r in range(4)}
    expected = {k: 0 for k in ("clock16", "current_action_only", "clock4", "clock16_shifted")}
    phases = {}
    for name, start, end in (
        ("familiar_continuation", 16, 32),
        ("unfamiliar", 32, 72),
        ("return", 72, 96),
    ):
        subtotal = dict.fromkeys(expected, 0)
        for t in range(start, end):
            truth = actions[t - 1]
            answers = {
                "clock16": clock_table[(t - 1) % 16],
                "current_action_only": action_map[actions[t]],
                "clock4": clock4[t % 4],
                "clock16_shifted": clock_table[t % 16],
            }
            for key, prediction in answers.items():
                subtotal[key] += (prediction == truth)
                expected[key] += (prediction == truth)
        phases[name] = {"n": end - start, "correct": subtotal}
    if expected != {"clock16": 80, "current_action_only": 35,
                    "clock4": 35, "clock16_shifted": 5}:
        raise ValueError("CAP04_CLOCK_FIXED_NUMERIC_DRIFT")
    if expected["clock4"] >= 80 or expected["clock16_shifted"] >= 80:
        raise ValueError("CAP04_CLOCK_NEGATIVE_CONTROL_COLLAPSE")
    # Experiment-stage tags are an evaluator-only *design clock oracle*,
    # not a learned source-facing classifier or a science baseline.
    original_period_16 = all(actions[t] == first_16[t % 16] for t in range(96))
    assert original_period_16
    result = {
        "schema": "yggdrasil.cap04.clock-only-retrospective-certificate.v1",
        "source_blob": SOURCE_GIT_BLOB,
        "source_episodes_generated": 0,
        "registered_source_actions": 0,
        "learner_training_steps": 0,
        "early_public_actions_fit": 16,
        "evaluation_public_action_indices": [16, 96],
        "phase_boundaries_public_protocol": list(source.BOUNDARIES),
        "source_protocol_clock_stage_identifiable": True,
        "clock_stage_is_unavailable_oracle": True,
        "fixed_16_step_period": original_period_16,
        "results": {"n": 80, "correct": expected, "phases": phases},
        "conclusion": "CAP04_CLOCK_ALIAS_CONFIRMED",
        "native_history_gain_verified": False,
        "scientific_gain_verified": False,
        "protected_first_use": False,
    }
    return result


def action_majority_by_clock(actions, remainder, period, *, stop):
    counts = Counter(actions[t - 1] for t in range(1, stop)
                     if t % period == remainder)
    if not counts:
        raise ValueError("CAP04_CLOCK_EMPTY_CLOCK_CONTROL")
    return sorted(counts, key=lambda a: (-counts[a], a))[0]


def main():
    result = census()
    print("CAP04_CLOCK_ONLY_RETROSPECTIVE=" +
          json.dumps(result, sort_keys=True, separators=(",", ":")))
    print("CAP04_NO_REGISTERED_SCIENCE_NO_NATIVE_LEARNING")


if __name__ == "__main__":
    main()
