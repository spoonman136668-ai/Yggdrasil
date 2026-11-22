"""Toy-only public-boundary and context checkpoint regression checks."""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from yggdrasil.native_episode_experience import NativeEpisodeExperience


def reject(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Invalid context operation succeeded")


def main():
    memory = NativeEpisodeExperience(repair=False)
    reject(memory.begin_context)
    reject(lambda: memory.context_forecast((0, 0), 0))
    for index in range(64):
        state, first, second = (index >> 2) & 1, index & 1, (index >> 1) & 1
        next_state = first ^ int(index >= 32)
        row = dict(s1=state, x1=first, s2=next_state, x2=second, y=second ^ next_state)
        memory = memory.observe(digest(canonical(["context-toy", index])),
                                ((state, 0), (state, 1)), row)
    original = memory.checkpoint()
    context = memory.begin_context()
    assert context.info()["context"]["candidate_count"] == 2
    for index in range(4):
        row = dict(s1=0, x1=0, s2=1, x2=0, y=1)
        context = context.observe(digest(canonical(["context-probe-toy", index])),
                                  ((0, 0), (0, 1)), row)
    info = context.info()["context"]
    assert info["weights"][1][0] * info["weights"][0][1] > info["weights"][0][0] * info["weights"][1][1]
    raw = context.checkpoint()
    assert context.consolidate().checkpoint() == raw
    restored = NativeEpisodeExperience.restore(raw, digest(raw))
    assert restored.checkpoint() == raw
    assert memory.checkpoint() == original
    assert NativeEpisodeExperience.restore(original, digest(original)).checkpoint() == original
    for value in (True, -1, 2, "0"):
        reject(lambda: restored.context_forecast((0, 1), value))
    bad = json.loads(raw)
    bad["context_start"] -= 1
    bad = canonical(bad)
    reject(lambda: NativeEpisodeExperience.restore(bad, digest(bad)))

    parent_path = HERE.parent / "CKAD-20/seed-101-unified-native.json"
    parent_raw = parent_path.read_bytes()
    parent = NativeCumulativeLearner.restore(parent_raw, digest(parent_raw))
    assert parent.checkpoint() == parent_raw
    candidate = parent.begin_experience_context()
    saved = candidate.checkpoint()
    cold = NativeCumulativeLearner.restore(saved, digest(saved))
    assert cold.checkpoint() == saved
    for state in (0, 1):
        assert cold.dtr_plan(state) == parent.dtr_plan(state)
        view = (state, 0)
        assert cold.experience_context_plan(view) == candidate.experience_context_plan(view)
    assert candidate.consolidate_experience().checkpoint() == saved
    assert parent.checkpoint() == parent_raw
    print("CKAD21_TOY_CONTEXT_AND_BACKWARD_COMPATIBILITY=PASS")


if __name__ == "__main__":
    main()
