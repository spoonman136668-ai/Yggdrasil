"""Fail-closed local corroboration experiment, with no target-label access.

Each cell tests both independently acquired local sensor-pair observations,
requires two supporting examples per pair and an unequivocal winning label.
The four cells must independently concur. This is confidence gating, NOT
a demonstrated compositional mechanism; trained/held-out abstentions count.
"""
from local_feature_selector import LocalFeatureSelector

class CorroboratedLocalSelector(LocalFeatureSelector):
    def __init__(self, cap=16, min_support=2):
        super().__init__(cap=cap)
        if type(min_support) is not int or not 2 <= min_support <= 16:
            raise ValueError("CORROBORATION_SUPPORT_INVALID")
        self.min_support = min_support

    def predict(self, bits):
        self.validate(bits)
        cell_votes = []
        for i,cell in enumerate(self.cells):
            local = []
            for distance in (1,2):
                counts = cell.get((distance,bits[i],bits[(i+distance)%4]), [0,0])
                if sum(counts)<self.min_support or min(counts)>0:
                    return None
                local.append(counts[1]>counts[0])
            if local[0]!=local[1]:
                return None
            cell_votes.append(local[0])
        if all(v==cell_votes[0] for v in cell_votes):
            return cell_votes[0]
        return None
