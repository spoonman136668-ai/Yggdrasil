"""NCI04E: distributed pre-lesion functional evidence, strictly ring-local.

Each surviving cell retains only local sensor -> immediate-neighbor observed
outcome counts. A newly blank cell can receive one-hop predictions from its
two neighbors; no original cell weights, hidden function labels, full-state
restore or post-lesion ground-truth output is available to the repair method.

This is a source-free *necessary-condition* demonstration, not a new
general-purpose developmental architecture or an efficiency victory.
"""
CELLS = 8

def _bits(items):
    if not isinstance(items,(list,tuple)) or len(items)!=CELLS or any(
        type(x) is not int or x not in (0,1) for x in items
    ):
        raise ValueError("expected 8 observed binary local signals")
    return list(items)

class DistributedSetpoint:
    def __init__(self):
        # [cell][direction 0=left,1=right][own sensor bit][neighbor outcome bit].
        self.shadow = [[[[0,0] for _ in range(2)] for _ in range(2)] for _ in range(CELLS)]
        self.alive = [True]*CELLS
        self.blank = [False]*CELLS
        self.inbox = [[None,None] for _ in range(CELLS)]
        self.steps = 0

    def observe(self, sensors, observed_next):
        x,y = _bits(sensors),_bits(observed_next)
        if self.steps >= 1000000:
            raise ValueError("bounded learning age exceeded")
        # Strict nearest-neighbor local learning. The target of a shadow
        # prediction is the adjacent cell's *observed* outcome, not a role label.
        for i in range(CELLS):
            if not self.alive[i]:
                continue
            for direction,neighbor in ((0,(i-1)%CELLS),(1,(i+1)%CELLS)):
                if self.alive[neighbor]:
                    self.shadow[i][direction][x[i]][y[neighbor]] += 1
        self.steps += 1

    def lesion(self, cell):
        if type(cell) is not int or not 0<=cell<CELLS:
            raise ValueError("invalid damaged cell")
        self.alive[cell] = False
        self.blank[cell] = True
        # Destroy exactly the injured cell's own remembered predictors.
        self.shadow[cell] = [[[0,0] for _ in range(2)] for _ in range(2)]
        self.inbox[cell] = [None,None]

    def regrow_blank(self, cell):
        if type(cell) is not int or not 0<=cell<CELLS or self.alive[cell]:
            raise ValueError("cell not missing")
        self.alive[cell] = True
        self.blank[cell] = True
        self.inbox[cell] = [None,None]

    def _predict_neighbor(self, own, direction, sensor):
        zero,one = self.shadow[own][direction][sensor]
        count=zero+one
        if count<8:
            return None
        p=(one+1)/(count+2)
        if p>=.80:
            return 1
        if p<=.20:
            return 0
        return None

    def exchange_one_hop(self, sensors):
        x = _bits(sensors)
        deliveries=[[None,None] for _ in range(CELLS)]
        # One synchronous hop: sender reads only own sensor and retained local
        # neighbor-response counts. Receiver does not forward in this round.
        for i in range(CELLS):
            if not self.alive[i]:
                continue
            left=(i-1)%CELLS
            right=(i+1)%CELLS
            if self.alive[left]:
                deliveries[left][1]=self._predict_neighbor(i,0,x[i])
            if self.alive[right]:
                deliveries[right][0]=self._predict_neighbor(i,1,x[i])
        self.inbox=deliveries

    def recovered_function(self, cell):
        if type(cell) is not int or not 0<=cell<CELLS:
            raise ValueError("invalid receiver")
        if not self.alive[cell] or not self.blank[cell]:
            return None
        left,right=self.inbox[cell]
        if left is None or right is None or left!=right:
            return None
        return left

    def has_neighbor_memory(self, cell):
        if type(cell) is not int or not 0<=cell<CELLS:
            raise ValueError("invalid receiver")
        left,right=(cell-1)%CELLS,(cell+1)%CELLS
        return sum(sum(self.shadow[left][1][k]) for k in range(2)),sum(
            sum(self.shadow[right][0][k]) for k in range(2))
