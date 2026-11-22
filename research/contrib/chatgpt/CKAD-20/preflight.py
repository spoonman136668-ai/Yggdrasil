"""Focused negative and state-join qualification using toy witnesses only."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner, EXPERIENCE_SOURCE
from yggdrasil.native_episode_experience import NativeEpisodeExperience


def rejects(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("unqualified episode was admitted")


def main():
    memory = NativeEpisodeExperience()
    # The stable feature is deliberately in coordinate 1 and disagrees with
    # the evaluator's initial-state field. The learner must use the views.
    for index in range(24):
        value = index % 2
        views = ((0, value), (1, value))
        bit = 1 - value
        row = {"s1": bit, "x1": 0, "s2": value, "x2": 0, "y": value}
        identifier = digest(canonical(["toy", index]))
        memory = memory.observe(identifier, views, row)
    assert memory.info()["projection"] == 1
    assert memory.info()["transition_hypothesis"] == "full"
    assert memory.forecast((0, 0), 0, full=True) == memory.forecast((1, 0), 0, full=True)
    before = memory.checkpoint()
    assert memory.observe(identifier, views, row) is memory
    rejects(lambda: memory.observe(identifier, views, dict(row, y=1-row["y"])))
    assert memory.consolidate().checkpoint() == before
    assert NativeEpisodeExperience.restore(before, digest(before)).checkpoint() == before
    forged = json.loads(before)
    forged["state_sha256"] = "0" * 64
    forged = canonical(forged)
    rejects(lambda: NativeEpisodeExperience.restore(forged, digest(forged)))

    root = ROOT / "research/contrib/chatgpt/CKAD-18"
    raw = (root / "seed-101-full-scope-native.json").read_bytes()
    model = NativeCumulativeLearner.restore(raw, digest(raw))
    assert model.checkpoint() == raw
    packet = digest(canonical([identifier, views, row]))
    rejects(lambda: model.observe_experience(identifier, views, row, source_sha256="0" * 64, packet_sha256=packet))
    rejects(lambda: model.observe_experience(identifier, views, row, source_sha256=EXPERIENCE_SOURCE, packet_sha256="0"*64))
    candidate = model.observe_experience(identifier, views, row, source_sha256=EXPERIENCE_SOURCE, packet_sha256=packet)
    stored = candidate.checkpoint()
    assert model.checkpoint() == raw
    assert candidate.consolidate_experience().checkpoint() == stored
    restored = NativeCumulativeLearner.restore(stored, digest(stored))
    assert restored.checkpoint() == stored and restored.dtr_plan(0) == model.dtr_plan(0)
    assert restored.experience_plan(views[0]) == candidate.experience_plan(views[0])
    print("CKAD20_TOY_SCOPE_AND_CHECKPOINT_NEGATIVES=PASS")


if __name__ == "__main__":
    main()
