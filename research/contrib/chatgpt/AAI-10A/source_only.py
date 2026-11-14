"""AAI-10A *source-only* candidate/control custody; no science first use.

Synthetic hand-authored cases are NOT any of the reserved DEV/TRANSFER/NEGATIVE
worlds. Primary is disarmed and no first_use callable exists in this module.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "AAI-10P"))
sys.path.insert(0, str(HERE))
import benchmark as b
import models as m


def source_only():
    learners = {name: m.create(name) for name in m.NAMES}
    # Explicit deterministic fixtures, no world-ID seeded generator.
    for law in ("A", "B"):
        for x in b.INPUTS:
            state = b.public_initial(law, x, (1, 0))
            outcome = b.public_step(law, state, b.ACTIONS[(sum(x) + x[0]) % 6])
            for model in learners.values():
                model.learn(state)
                model.learn(outcome)
    checkpoints = m.checkpoint(learners)
    cold = m.cold_restore(checkpoints)
    assert checkpoints == m.checkpoint(cold)
    decisions = {name: [model.choose(b.public_initial("A", x, (0, 1)))
                        for x in b.INPUTS]
                 for name, model in cold.items()}
    for name, model in cold.items():
        assert all(action is None or action in b.ACTIONS for action in decisions[name])
    trace = m.canonical({"checkpoints": checkpoints, "decisions": decisions})
    return {"schema": "yggdrasil.contrib.aai10a.mechanical-source-only.v1",
            "phase": "SOURCE_ONLY_NO_SCIENCE_FIRST_USE",
            "train_laws": "A_AND_B_MECHANICAL_FIXTURES_ONLY",
            "learning_methods": list(m.NAMES), "matched_methods": list(m.MATCHED),
            "all_methods_checkpoint_restored": True,
            "full_public_evidence_schema": "x,mediators,goal,reward,actions_taken",
            "source_trace_sha256": hashlib.sha256(trace.encode()).hexdigest(),
            "science_worlds_consumed": 0,
            "native_yggdrasil_modified": False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-only", action="store_true")
    p.add_argument("--primary", action="store_true")
    args = p.parse_args()
    if args.primary:
        p.error("AAI-10A SCIENCE FIRST USE DISARMED: requires new separate authorization")
    if not args.source_only:
        p.error("only source-only prefirstuse mode exists")
    print(json.dumps(source_only(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
