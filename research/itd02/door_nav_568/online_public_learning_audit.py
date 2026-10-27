"""Source-free online public learning measurements after owned interventions."""
import json
from online_public_learning import LearningPublicLoop
from native_public_loop import PublicWorld

def run():
    agent = LearningPublicLoop()
    frozen = dict(agent.model.active_links)
    sessions = [agent.episode(PublicWorld("A", surprise=True)),
                agent.episode(PublicWorld("B"), recheck=True),
                agent.episode(PublicWorld("A"))]
    return {
        "selected": [s["selected"] for s in sessions],
        "actions": [s["actions"] for s in sessions],
        "online_changes": sessions[-1]["online_changes"],
        "online_examples": sessions[-1]["online_examples"],
        "online_records": sessions[-1]["online_records"],
        "frozen_model_unchanged": agent.model.active_links == frozen,
        "fitted_second_hop": agent.learned.links[(b"M1-intermediate", 2)].decode(),
        "scope": "Public synthetic owned-action feedback; post-session updates only",
        "caveat": "Model evidence is supervised by synthetic public outcomes; transfer and CPU cost not independently established",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
