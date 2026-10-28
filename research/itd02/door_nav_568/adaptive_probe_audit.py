"""Matched adaptive public-probe audit with first-step failure and caps."""
import json
from adaptive_probe_scheduler import AdaptiveProbeScheduler
from two_hop_evidence_audit import build, SECOND

def trial(world="A", first_failure=False, budget=6, restrict_second_start=False):
    native = build()
    starts = [(b"xA-training", (0, 1))]
    if not restrict_second_start:
        starts.append((b"xB-training", (0, 1)))
    scheduler = AdaptiveProbeScheduler(native.active_links, native.archived_links,
                                       starts, limit=budget)
    second = {(middle, action): (old if world == "A" else new)
              for middle, action, old, new in SECOND}
    failed = False
    while scheduler.decision() is None:
        action = scheduler.next_probe()
        if action is None:
            break
        expected = native.active_links[action]
        if first_failure and not failed:
            observed = b"Z9-unexpected"
            failed = True
        else:
            observed = expected
        follow = scheduler.first_outcome(observed)
        if follow is None:
            continue
        scheduler.second_outcome(second[follow])
    return {
        "selected": scheduler.decision(),
        "expected": "snapshot" if world == "A" else "active",
        "interventions": scheduler.actions,
        "confirmed_chains": len(scheduler.confirmed),
        "rejected_first_hops": len(scheduler.rejected),
        "candidate_count": len(scheduler.candidates),
        "stored_examples": native.stored_examples(),
        "transition_records": len(native.active_links) + len(native.archived_links),
    }

def run():
    return {
        "clean_A": trial("A"),
        "clean_B": trial("B"),
        "recover_after_first_failure": trial("A", first_failure=True),
        "low_budget": trial("A", first_failure=True, budget=4),
        "one_start_only": trial("A", restrict_second_start=True),
        "scope": "Synthetic physically owned public transitions; bounded adaptive probe scheduler",
        "limitation": "Unexpected first step is detected, not learned as a new transition; repeated/common-mode corruption remains unresolved",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
