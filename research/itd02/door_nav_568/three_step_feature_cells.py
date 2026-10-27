"""Bounded three-step public successor composition over native R7 reward cells.

Extension of the verified two-step feature-cell mechanism. It traverses only
successors inferred from FIT data and *observed* representative public states.
Unknown/tied consequences and cycles have zero projected reward. No hidden
state, hard-coded goal direction, original DoorKey data, or goal oracle.
"""
from feature_cell_lookahead import FeatureCellLookahead

class ThreeStepFeatureCells(FeatureCellLookahead):
    def _value(self, frame, action, depth, visited):
        cell = self.terminal.get((frame[0], action))
        if cell is not None:
            return cell.signal(True)
        if depth <= 1 or self.model.selected_position is None:
            return 0.0
        position = self.model.selected_position
        if len(frame) <= position:
            return 0.0
        counts = self.model.buckets.get((frame[position], action))
        if not counts:
            return 0.0
        best_count = max(counts.values())
        possible = [label for label, count in counts.items()
                    if count == best_count]
        if len(possible) != 1:
            return 0.0
        label = possible[0]
        if label in visited or label not in self.representatives:
            return 0.0
        next_frame, legal = self.representatives[label]
        if not legal:
            return 0.0
        return 0.9 * max(self._value(next_frame, next_action, depth - 1,
                                     visited | {label}) for next_action in legal)

    def choose(self, horizon=3):
        if (self.current is None or type(horizon) is not int or
                horizon not in (1, 2, 3)):
            raise ValueError("OBSERVE_AND_HORIZON_REQUIRED")
        frame, legal = self.current
        return max(legal, key=lambda a:
                   (self._value(frame, a, horizon, {frame[0]}), -a))
