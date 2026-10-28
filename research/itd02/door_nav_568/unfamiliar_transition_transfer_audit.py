"""Matched unfamiliar-successor transfer: public owned calibration, then blind probe.

The conventional frozen selector and online learner receive IDENTICAL calibration
interactions, and costs are counted. Novel successor values are not hard-coded
in either policy: only the synthetic world returns them after an action.
Results preserve abstentions, errors, resource use, and return-to-A retention.
"""
import json
from feedback_public_loop import FeedbackPublicLoop
from native_public_loop import PublicWorld
from two_hop_evidence_audit import SECOND

class NovelPublicWorld(PublicWorld):
    def __init__(self):
        super().__init__("B")
    def step(self, frame, action):
        for middle, second, old, shifted in SECOND:
            if (frame, action) == (middle, second):
                self.actions += 1
                return b"N7-novel" if middle.startswith(b"M") else b"P8-novel"
        return super().step(frame, action)

CALIBRATION = ((b"xA-training", 1), (b"xB-training", 1))

def calibrated_arm(enabled, repetitions=2):
    learner = FeedbackPublicLoop(enabled=enabled, recovery=True)
    env = NovelPublicWorld()
    before = dict(learner.learned.links)
    calibration = 0
    # Public state/action continuity: second action starts at the FIRST
    # observed successor. The learner gets no world identifier or answer key.
    for _ in range(repetitions):
        for first in CALIBRATION:
            middle = env.step(*first)
            learner.learned.observe(first, middle)
            second = (middle, 2)
            final = env.step(*second)
            learner.learned.observe(second, final)
            calibration += 2
    decision = learner.episode(NovelPublicWorld())
    retained = learner.episode(PublicWorld("A"))
    return {
        "selected_novel": decision["selected"],
        "novel_actions": decision["actions"],
        "novel_correct": decision["selected"] == "active",
        "novel_abstained": decision["selected"] is None,
        "novel_wrong": decision["selected"] not in ("active", None),
        "retention_selected": retained["selected"],
        "retention_correct": retained["selected"] == "snapshot",
        "retention_actions": retained["actions"],
        "calibration_actions": calibration,
        "total_actions": calibration + decision["actions"] + retained["actions"],
        "learned_changes": learner.learned.changes,
        "online_examples": learner.learned.examples(),
        "online_records": len(learner.learned.links),
        "archive_unchanged": learner.model.archived_links[
            (b"M1-intermediate", 2)] == b"R3-positive",
        "first_hop_unchanged": before[
            (b"xA-training", 1)] == learner.learned.links[(b"xA-training", 1)],
    }

def run():
    return {
        "frozen_control": calibrated_arm(False, 2),
        "online_feedback": calibrated_arm(True, 2),
        "one_sample_negative": calibrated_arm(True, 1),
        "scope": "Source-free new successor family, matched public action-owned calibration",
        "caveat": "Synthetic reachable states supplied by harness; no original DoorKey or autonomous world discovery",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
