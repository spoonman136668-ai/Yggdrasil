"""Matched synthetic comparisons, with errors and abstentions retained."""
import json
from feedback_public_loop import FeedbackPublicLoop
from native_public_loop import PublicWorld

def arm(enabled, recovery=False):
    learner = FeedbackPublicLoop(enabled=enabled, recovery=recovery)
    rounds = [("A", True, False), ("B", False, True),
              ("A", False, False), ("B", False, False)]
    out = []
    for regime, surprise, recheck in rounds:
        observation = learner.episode(PublicWorld(regime, surprise), recheck=recheck)
        out.append({
            "expected": "snapshot" if regime == "A" else "active",
            "selected": observation["selected"],
            "actions": observation["actions"],
            "correct": observation["selected"] ==
                       ("snapshot" if regime == "A" else "active"),
            "abstained": observation["selected"] is None,
            "false_selection": observation["selected"] is not None and
                       observation["selected"] !=
                       ("snapshot" if regime == "A" else "active"),
            "online_changes": observation["online_changes"],
            "online_examples": observation["online_examples"],
            "online_records": observation["online_records"],
            "decision_ns": observation.get("decision_ns"),
            "fallback_used": observation.get("fallback_used", False),
            "candidate_count": observation.get("candidate_count"),
        })
    return {
        "rounds": out,
        "correct": sum(x["correct"] for x in out),
        "abstentions": sum(x["abstained"] for x in out),
        "wrong": sum(x["false_selection"] for x in out),
        "actions": sum(x["actions"] for x in out),
        "online_records": len(learner.learned.links),
        "archive_unchanged": learner.model.archived_links[
            (b"M1-intermediate", 2)] == b"R3-positive",
    }

def run():
    return {
        "frozen_selector_control": arm(False),
        "online_feedback": arm(True),
        "feedback_with_qualified_fallback": arm(True, recovery=True),
        "scope": "Synthetic public feedback only; identical sequence and budgets; fallback uses frozen prior hypothesis pool only after lost candidate coverage",
        "caveat": "Wall-clock nanoseconds are descriptive on shared CI runners, not energy or retail-hardware qualification",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
