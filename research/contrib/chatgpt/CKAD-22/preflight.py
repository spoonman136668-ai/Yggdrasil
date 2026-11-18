"""Toy-only novel hypothesis learning and backward compatibility checks."""
from pathlib import Path
import json
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner


def reject(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Malformed novel-context operation succeeded")


def main():
    memory = NativeEpisodeExperience(repair=False)
    for index in range(64):
        first, second, state = index & 1, (index >> 1) & 1, (index >> 2) & 1
        row = dict(s1=state, x1=first, s2=first, x2=second, y=second)
        memory = memory.observe(digest(canonical(["novel-toy-base", index])),
                                ((state, 0), (state, 1)), row)
    old = memory.checkpoint()
    reject(lambda: memory.begin_context(novel=1))
    novel = memory.begin_context(novel=True)
    initial = novel.checkpoint()
    assert novel.info()["context"]["novel_enabled"] is True
    assert novel.info()["context"]["novel_prior"] == [1, 8]
    old_models = [model.checkpoint() for _, _, _, model in novel._context_models[:-1]]
    for index in range(24):
        first, second, state = index & 1, (index >> 1) & 1, (index >> 2) & 1
        row = dict(s1=state, x1=first, s2=1-first, x2=second, y=1-second)
        novel = novel.observe(digest(canonical(["novel-toy-observation", index])),
                              ((state, 0), (state, 1)), row)
    assert [model.checkpoint() for _, _, _, model in novel._context_models[:-1]] == old_models
    assert novel._context_weights[-1] > novel._context_weights[0]
    saved = novel.checkpoint()
    restored = NativeEpisodeExperience.restore(saved, digest(saved))
    assert restored.checkpoint() == saved == novel.consolidate().checkpoint()
    assert memory.checkpoint() == old
    assert NativeEpisodeExperience.restore(initial, digest(initial)).checkpoint() == initial
    legacy_context = memory.begin_context()
    raw = legacy_context.checkpoint()
    assert NativeEpisodeExperience.restore(raw, digest(raw)).checkpoint() == raw

    path = HERE.parent / "CKAD-21/seed-101-context-native.json"
    raw = path.read_bytes()
    parent = NativeCumulativeLearner.restore(raw, digest(raw))
    assert parent.checkpoint() == raw
    candidate = parent.begin_experience_context(novel=True)
    stored = candidate.checkpoint()
    cold = NativeCumulativeLearner.restore(stored, digest(stored))
    assert cold.checkpoint() == stored
    assert cold.experience_context_plan((0, 0)) == candidate.experience_context_plan((0, 0))
    assert parent.checkpoint() == raw
    print("CKAD22_TOY_NOVEL_LEARNING_AND_COMPATIBILITY=PASS")


if __name__ == "__main__":
    main()
