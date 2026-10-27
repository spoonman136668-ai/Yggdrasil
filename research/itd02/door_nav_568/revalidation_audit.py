"""Bounded synthetic rechecks of previously surprising public action outcomes."""
import json
from two_hop_evidence_audit import build
from remembering_probe_scheduler import PublicExceptionMemory
from revalidating_probe_scheduler import RevalidatingProbeScheduler

def run():
    model = build()
    starts = [(b"xA-training", (0, 1)), (b"xB-training", (0, 1))]
    memory = PublicExceptionMemory(capacity=2)
    original = dict(model.active_links)
    first = RevalidatingProbeScheduler(model.active_links, model.archived_links, starts, memory)
    failed = first.next_probe()
    first.first_outcome(b"Z9-unexpected")
    next_session = RevalidatingProbeScheduler(model.active_links, model.archived_links, starts, memory)
    avoided = failed not in [c[0] for c in next_session.candidates]
    recheck = next_session.request_recheck(failed)
    recovered = next_session.finish_recheck(original[failed])
    return {
        "failed_action_avoided": avoided,
        "physical_recheck_requested": recheck == failed,
        "revalidated": recovered,
        "action_cost": next_session.actions,
        "remaining_exceptions": len(memory.exceptions),
        "candidate_count_after_recheck": len(next_session.candidates),
        "model_unchanged": model.active_links == original,
        "stored_examples": model.stored_examples(),
        "scope": "Synthetic public action observations, no original DoorKey episodes",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
