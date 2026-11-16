"""CUE-01: read-only source-blind public-intervention selection for native causal memory.

This API NEVER receives a world/task/slot identity, selects no privileged causal
oracle, does not execute interventions, and NEVER authenticates or promotes a
stored match. Each observed consequence must be provided by the caller after
actually performing the proposed intervention. SHA alone is not authenticity.

A unique matching slot is a *provisional hypothesis*, not learned independent
task identity: other, unobserved worlds may be observationally identical.
"""
from __future__ import annotations

from yggdrasil.native_cumulative_action_bank import NativeCumulativeActionBank
from yggdrasil.native_intervention_repair import features
from yggdrasil.public_causal_cells import PublicCausalCells

MAX_PUBLIC_CUES = 8
MIN_PROVISIONAL_CUES = 4
ALL_ACTIONS = tuple((x, a) for x in range(16) for a in (0, 1))


def _bank(value):
    if not isinstance(value, NativeCumulativeActionBank):
        raise ValueError("CUE01_NATIVE_BANK_REQUIRED")
    return value


def _read_cues(cues):
    if type(cues) not in (list, tuple) or len(cues) > MAX_PUBLIC_CUES:
        raise ValueError("CUE01_PUBLIC_CUE_BUDGET")
    seen = set()
    rows = []
    for row in cues:
        if type(row) not in (list, tuple) or len(row) != 3:
            raise ValueError("CUE01_PUBLIC_CUE_SHAPE")
        x, action, outcome = row
        features(x, action)  # NKR-11 original strict typed public-input guard.
        if type(outcome) is not int or outcome not in (0, 1):
            raise ValueError("CUE01_PUBLIC_OUTCOME_INVALID")
        if (x, action) in seen:
            raise ValueError("CUE01_REPLAYED_ACTION_CUE")
        seen.add((x, action))
        rows.append((x, action, outcome))
    return tuple(rows)


def _prediction(bank, slot, context, action):
    # An explicit slot is used only *internally* while inspecting stored
    # hypotheses. The caller cannot submit a slot or true-world identity.
    active = PublicCausalCells.ACTIVE_SLOTS
    if type(slot) is not int or not 0 <= slot < 16:
        raise ValueError("CUE01_NATIVE_SLOT_INVALID")
    addr = slot if slot < active else slot - active
    result = bank.predict(addr, context, action, retained=slot >= active)
    predicted = result["public_outcome"]
    if predicted is not None and (type(predicted) is not int or predicted not in (0, 1)):
        raise ValueError("CUE01_STORED_PREDICTION_INVALID")
    return predicted


def _survivors(bank, cues):
    candidates = []
    for slot in bank.stored_slots:
        unsupported = 0
        for context, action, truth in cues:
            candidate = _prediction(bank, slot, context, action)
            if candidate is None:
                unsupported += 1
            elif candidate != truth:
                break
        else:
            candidates.append((slot, unsupported))
    return tuple(candidates)


def select(bank, public_cues):
    """Return a *provisional* native memory slot, or conservative abstention."""
    bank = _bank(bank)
    cues = _read_cues(public_cues)
    candidates = _survivors(bank, cues)
    ids = [slot for slot, _ in candidates]
    common = {
        "remaining_slots": ids, "used_public_probes": len(cues),
        "source_authenticity": "UNVERIFIED_PUBLIC_OBSERVATION_CLAIM",
        "native_accepted": False, "scientific_pass": False,
        "write_to_accepted_model": False,
        "learned_task_identity_verified": False,
    }
    if not bank.stored_slots:
        classification = "NO_STORED_RELATIONSHIPS_ABSTAIN"
    elif not candidates:
        classification = "NO_COMPATIBLE_MEMORY_ABSTAIN"
    elif (len(candidates) == 1 and len(cues) >= MIN_PROVISIONAL_CUES
          and candidates[0][1] == 0):
        classification = "PROVISIONAL_UNVERIFIED_SLOT_MATCH"
    elif len(candidates) == 1 and candidates[0][1] != 0:
        classification = "UNIDENTIFIABLE_OBSERVATIONS_ABSTAIN"
    else:
        classification = "AMBIGUOUS_MEMORY_ABSTAIN"
    return {
        **common, "classification": classification,
        "provisional_slot": ids[0] if classification ==
        "PROVISIONAL_UNVERIFIED_SLOT_MATCH" else None,
    }


def propose(bank, public_cues):
    """Propose one source-free actual public do-context/action probe.

    Across the retained compatible set, choose a query splitting the known
    0/1 consequences as evenly as possible. When only one candidate remains,
    instead seek a confirmation query disagreeing with as many discarded
    stored hypotheses as possible. The source caller MUST execute the action
    and supply the real consequence separately. No hidden labels are read.
    """
    bank = _bank(bank)
    cues = _read_cues(public_cues)
    decision = select(bank, cues)
    taken = {(x, action) for x, action, _ in cues}
    if len(cues) >= MAX_PUBLIC_CUES or not decision["remaining_slots"]:
        return {"classification": "NO_MORE_SAFE_PROBES",
                "context": None, "action": None,
                "native_accepted": False, "scientific_pass": False}
    remaining = tuple(decision["remaining_slots"])
    candidates = []
    for context, action in ALL_ACTIONS:
        if (context, action) in taken:
            continue
        outcomes = [_prediction(bank, slot, context, action)
                    for slot in remaining]
        zeros = outcomes.count(0)
        ones = outcomes.count(1)
        unknown = outcomes.count(None)
        if len(remaining) > 1:
            # Higher first component means better split, then better
            # identified coverage. Unknown never earns information credit.
            score = (min(zeros, ones), zeros+ones, -unknown)
        else:
            target = outcomes[0]
            # Additional post-uniqueness cues try to refute mistaken identity
            # by choosing actions disagreeing with non-surviving memories.
            refutations = (sum(_prediction(bank, slot, context, action) != target
                               for slot in bank.stored_slots
                               if slot not in remaining
                               and _prediction(bank, slot, context, action)
                               is not None)
                           if target is not None else 0)
            score = (refutations, int(target is not None), -unknown)
        candidates.append((score, context, action))
    if not candidates:
        return {"classification": "NO_MORE_SAFE_PROBES",
                "context": None, "action": None,
                "native_accepted": False, "scientific_pass": False}
    best = max(score for score, _, _ in candidates)
    if len(remaining) > 1 and best[0] == 0:
        return {"classification": "NON_IDENTIFIABLE_NO_DISCRIMINATING_PROBE",
                "context": None, "action": None,
                "native_accepted": False, "scientific_pass": False}
    _, context, action = min(((-1, x, a) for score, x, a in candidates
                              if score == best))
    return {
        "classification": "PUBLIC_PROBE_PROPOSED_NOT_EXECUTED",
        "context": context, "action": action,
        "used_public_probes": len(cues), "remaining_slots": list(remaining),
        "native_accepted": False, "scientific_pass": False,
    }
