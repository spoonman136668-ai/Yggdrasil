"""Experimental composition of learned successor features and native R7 reward cells.

Public-only supervised FIT. Learned feature successor predictions provide
one-hop connections to *observed* representative public states; R7 cells learn
action-owned terminal reward on those states. Horizon=2 evaluates a predicted
intermediate action and its terminal value. It is a bounded lookahead hybrid,
NOT evidence of autonomous native planning or original DoorKey success.
"""
from learned_successor_features import LearnedSuccessorFeatures
from native_cells_r7 import LocalCell

class FeatureCellLookahead:
    def __init__(self, positions=2, capacity=128):
        self.model = LearnedSuccessorFeatures(positions=positions, capacity=capacity)
        self.capacity = capacity
        self.representatives = {}
        self.terminal = {}
        self.current = None

    def observe(self, frame, actions):
        self.model.observe(frame, actions)
        self.current = (frame, tuple(actions))
        if frame[0] not in self.representatives:
            if len(self.representatives) >= self.capacity:
                raise ValueError("REPRESENTATIVE_CAP_REACHED")
            self.representatives[frame[0]] = (frame, tuple(actions))

    def learn(self, action, next_frame, reward, done):
        if self.current is None or action not in self.current[1]:
            raise ValueError("OWNED_ACTION_REQUIRED")
        frame, _ = self.current
        self.model.learn(action, next_frame, reward, done)
        if done:
            key = (frame[0], action)
            if key not in self.terminal:
                if len(self.terminal) >= self.capacity:
                    raise ValueError("REWARD_CAP_REACHED")
                self.terminal[key] = LocalCell()
            self.terminal[key].feel(True, reward > 0)
        self.current = None

    def _score(self, action, horizon):
        frame, _ = self.current
        key = (frame[0], action)
        if key in self.terminal:
            return self.terminal[key].signal(True)
        if horizon <= 1:
            return 0.0
        predicted = self.model.predict_successor_label(action)
        if predicted is None or predicted not in self.representatives:
            return 0.0
        next_frame, legal = self.representatives[predicted]
        # The second hop uses only a recorded public representative and
        # action-conditioned R7 reward memory; no hidden state.
        return 0.9 * max((self.terminal.get((next_frame[0], a), LocalCell()).signal(True)
                          for a in legal), default=0.0)

    def choose(self, horizon=2):
        if self.current is None or type(horizon) is not int or horizon not in (1, 2):
            raise ValueError("OBSERVE_AND_HORIZON_REQUIRED")
        _, legal = self.current
        return max(legal, key=lambda a: (self._score(a, horizon), -a))
