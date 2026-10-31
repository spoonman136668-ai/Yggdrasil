"""MG94-T distributed-local-cell negative control; source-free development.

Two independent 2-bit cells learn public selected transition outcomes. Their
local updates have NO cross-cell communication. This is a conventional baseline,
not evidence of novel distributed intelligence.
"""
from packed_state_controls import Markov, STREAMS

class LocalCells:
    def __init__(self):
        self.cells = [1, 1]
        self.previous = None

    def step(self, observed):
        assert observed in (0, 1)
        prediction = None if self.previous is None else int(self.cells[self.previous] >= 2)
        if self.previous is not None:
            old = self.cells[self.previous]
            self.cells[self.previous] = min(3,old+1) if observed else max(0,old-1)
        self.previous = observed
        return prediction

def run():
    result = {}
    for name, events in STREAMS.items():
        distributed, conventional = LocalCells(), Markov()
        left, right = [], []
        for observed in events:
            left.append(distributed.step(observed))
            right.append(conventional.step(observed))
        assert left == right, (name, left, right)
        result[name] = {'equivalent':True,'correct':sum(p == y for p,y in zip(left,events))}
    return result

if __name__ == '__main__':
    import json
    print(json.dumps(run(), sort_keys=True))
