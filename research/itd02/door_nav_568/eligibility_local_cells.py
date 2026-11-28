"""Bounded action-owned eligibility trace over state-local R7 cells.

Experimental delayed-credit mechanism; no original-source scientific claim.
"""
import hashlib
from state_local_cells import StateLocalActionCells

class EligibilityLocalCells(StateLocalActionCells):
    def __init__(self, max_states=128, trace_limit=4):
        super().__init__(max_states=max_states)
        if type(trace_limit) is not int or not 1 <= trace_limit <= 8:
            raise ValueError("TRACE_LIMIT_INVALID")
        self.trace_limit = trace_limit
        self.trace = []

    def learn(self, chosen_action, next_public_frame, reward, done):
        if self.current is None or chosen_action not in self.current[1]:
            raise ValueError("OWNED_ACTION_REQUIRED")
        if not isinstance(next_public_frame, bytes) or type(reward) not in (int, float) or type(done) is not bool:
            raise ValueError("PUBLIC_CONSEQUENCE_REQUIRED")
        state, _ = self.current
        if state not in self.cells:
            if len(self.cells) >= self.max_states:
                raise ValueError("STATE_CAP_REACHED")
            from native_cells_r7 import LocalCell
            self.cells[state] = [LocalCell() for _ in range(7)]
        self.trace.append((state, chosen_action))
        self.trace = self.trace[-self.trace_limit:]
        if reward > 0:
            for previous_state, previous_action in self.trace:
                self.cells[previous_state][previous_action].feel(True, True)
            self.trace.clear()
        elif done:
            for previous_state, previous_action in self.trace:
                self.cells[previous_state][previous_action].feel(True, False)
            self.trace.clear()
        self.current = None
