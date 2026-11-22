"""WSCM-01 development-only W=16 delayed-credit proposal ring.

This is a source-free engineering fixture, not an authenticated action witness,
a causal attribution proof, or a learning update. Caller-asserted source flags
do not authenticate the observation. No Genome or native state can be written.
"""

WINDOW = 16
SCALE = 256
SURPRISE_THRESHOLD = 128
MAX_ID = (1 << 63) - 1


def _integer(value, low, high, reason):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(reason)


class DelayedCreditRing:
    """Bounded, deterministic retrospective *proposals*, never weight edits."""

    def __init__(self):
        self._events = ()
        self._reveals = ()
        self._last_event_id = -1
        self._last_outcome_id = -1

    def stage(self, event_id, action_id, predicted_q8, candidate_role=None):
        _integer(event_id, 0, MAX_ID, "WSCM_EVENT_ID")
        _integer(action_id, 0, MAX_ID, "WSCM_ACTION_ID")
        _integer(predicted_q8, 0, SCALE, "WSCM_PREDICTION_Q8")
        if candidate_role is not None:
            _integer(candidate_role, 0, 15, "WSCM_ROLE_CAPACITY")
        row = (event_id, action_id, predicted_q8, candidate_role)
        if self._events and event_id == self._last_event_id and row == self._events[-1]:
            return self
        if event_id <= self._last_event_id:
            raise ValueError("WSCM_EVENT_REPLAY_OR_REORDER")
        self._events = (self._events + (row,))[-WINDOW:]
        retained = {event[0] for event in self._events}
        self._reveals = tuple(r for r in self._reveals if r[0] in retained)
        self._last_event_id = event_id
        return self

    def reveal(self, target_event_id, outcome_id, observed, *, charged, controlled):
        """Produce proposed eligibility on signed surprise only.

        The supplied booleans are development assertions, not source-owner
        authentication. Eligibility magnitude is not causal identification.
        """
        _integer(target_event_id, 0, MAX_ID, "WSCM_TARGET_ID")
        _integer(outcome_id, 0, MAX_ID, "WSCM_OUTCOME_ID")
        _integer(observed, 0, 1, "WSCM_BINARY_OUTCOME")
        if charged is not True or controlled is not True:
            raise ValueError("WSCM_SOURCE_AUTHORITY_ABSENT")
        prior = next((row for row in self._reveals if row[0] == target_event_id), None)
        if prior is not None:
            if prior[1] == outcome_id and prior[2] == observed:
                return prior[3]
            raise ValueError("WSCM_CONFLICTING_REVEAL")
        if outcome_id <= self._last_outcome_id:
            raise ValueError("WSCM_OUTCOME_REORDER")
        index = next((i for i, row in enumerate(self._events)
                      if row[0] == target_event_id), None)
        if index is None:
            raise ValueError("WSCM_TARGET_EXPIRED_OR_UNKNOWN")
        error = SCALE * observed - self._events[index][2]
        proposals = ()
        if abs(error) >= SURPRISE_THRESHOLD:
            proposals = tuple(
                # (prior event ID, hypothetical role, lag, q15 eligibility, signed error)
                (event_id, role, index - j, 1 << (15 - (index - j)), error)
                for j, (event_id, _, _, role) in enumerate(self._events[:index + 1])
            )
        self._reveals += ((target_event_id, outcome_id, observed, proposals),)
        self._last_outcome_id = outcome_id
        return proposals

    def snapshot(self):
        return (self._last_event_id, self._last_outcome_id,
                self._events, self._reveals)

    @classmethod
    def restore(cls, snapshot):
        if type(snapshot) is not tuple or len(snapshot) != 4:
            raise ValueError("WSCM_SNAPSHOT_CONTRACT")
        last_event, last_outcome, events, reveals = snapshot
        _integer(last_event, -1, MAX_ID, "WSCM_SNAPSHOT_EVENT_ID")
        _integer(last_outcome, -1, MAX_ID, "WSCM_SNAPSHOT_OUTCOME_ID")
        if (type(events) is not tuple or len(events) > WINDOW
                or type(reveals) is not tuple or len(reveals) > WINDOW):
            raise ValueError("WSCM_SNAPSHOT_CAPACITY")
        obj = cls()
        for event in events:
            if type(event) is not tuple or len(event) != 4:
                raise ValueError("WSCM_SNAPSHOT_EVENT")
            obj.stage(*event)
        if (obj._last_event_id > last_event or (not events and last_event != -1)
                or (events and obj._last_event_id != last_event)):
            raise ValueError("WSCM_SNAPSHOT_EVENT_ID")
        for entry in reveals:
            if type(entry) is not tuple or len(entry) != 4:
                raise ValueError("WSCM_SNAPSHOT_REVEAL")
            target_id, outcome_id, observed, proposals = entry
            rebuilt = obj.reveal(target_id, outcome_id, observed,
                                 charged=True, controlled=True)
            if rebuilt != proposals:
                raise ValueError("WSCM_SNAPSHOT_PROPOSALS")
        if obj._last_outcome_id > last_outcome:
            raise ValueError("WSCM_SNAPSHOT_OUTCOME_ID")
        # Old outcome IDs may legitimately outlive expired ring entries.
        obj._last_outcome_id = last_outcome
        if obj.snapshot() != snapshot:
            raise ValueError("WSCM_NONCANONICAL_SNAPSHOT")
        return obj
