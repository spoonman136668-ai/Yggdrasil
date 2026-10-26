"""Source-free state-conditioned local R7 plasticity candidate.

Each observed public state owns seven independent R7 local cells. No planner,
hidden state, source episodes, or global gradient is used.
"""
import hashlib
from native_cells_r7 import LocalCell

class StateLocalActionCells:
    def __init__(self, max_states=128):
        if type(max_states) is not int or not 1 <= max_states <= 128:
            raise ValueError("STATE_CAP_INVALID")
        self.max_states = max_states
        self.cells = {}
        self.current = None

    def observe(self, public_frame, legal_actions):
        if not isinstance(public_frame, bytes):
            raise ValueError("PUBLIC_FRAME_REQUIRED")
        legal = tuple(legal_actions)
        if not legal or len(set(legal)) != len(legal) or any(type(a) is not int or a not in range(7) for a in legal):
            raise ValueError("LEGAL_ACTIONS_REQUIRED")
        state = hashlib.sha256(public_frame).hexdigest()
        self.current = (state, legal)

    def choose(self):
        if self.current is None:
            raise ValueError("OBSERVE_FIRST")
        state, legal = self.current
        cells = self.cells.get(state)
        if cells is None:
            return min(legal)
        return max(legal, key=lambda a: (cells[a].signal(True), -a))

    def learn(self, chosen_action, next_public_frame, reward, done):
        if self.current is None or chosen_action not in self.current[1]:
            raise ValueError("OWNED_ACTION_REQUIRED")
        if not isinstance(next_public_frame, bytes) or type(reward) not in (int, float) or type(done) is not bool:
            raise ValueError("PUBLIC_CONSEQUENCE_REQUIRED")
        state, _ = self.current
        if state not in self.cells:
            if len(self.cells) >= self.max_states:
                raise ValueError("STATE_CAP_REACHED")
            self.cells[state] = [LocalCell() for _ in range(7)]
        self.cells[state][chosen_action].feel(True, reward > 0)
        self.current = None
