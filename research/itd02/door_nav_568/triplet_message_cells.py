"""Independent local triplet messages for a bounded synthetic transfer pilot.

Four cells each own a three-sensor receptive field, excluding one public
sensor. Cells exchange only a vote and support count at inference.
No full four-bit answer table, global gradient, hidden regime or future data.
"""
class TripletMessageCells:
    def __init__(self, capacity=8, support=2):
        if type(capacity) is not int or not 1<=capacity<=8:
            raise ValueError("CELL_CAP_INVALID")
        if type(support) is not int or not 2<=support<=8:
            raise ValueError("SUPPORT_INVALID")
        self.capacity=capacity
        self.support=support
        self.cells=[{} for _ in range(4)]
        self.updates=0

    def observe(self,bits,outcome):
        if type(bits) is not tuple or len(bits)!=4 or any(type(x) is not bool for x in bits) or type(outcome) is not bool:
            raise ValueError("PUBLIC_TRAINING_REQUIRED")
        keys=[tuple(bits[j] for j in range(4) if j!=i) for i in range(4)]
        if any(key not in self.cells[i] and len(self.cells[i])>=self.capacity for i,key in enumerate(keys)):
            raise ValueError("CELL_RECORD_LIMIT")
        for i,key in enumerate(keys):
            bucket=self.cells[i].setdefault(key,[0,0])
            bucket[int(outcome)]+=1
        self.updates+=1

    def predict(self,bits,min_votes=3):
        if type(bits) is not tuple or len(bits)!=4 or any(type(x) is not bool for x in bits):
            raise ValueError("PUBLIC_FRAME_REQUIRED")
        if type(min_votes) is not int or not 2<=min_votes<=4:
            raise ValueError("VOTE_THRESHOLD_INVALID")
        votes=[]
        for i,cell in enumerate(self.cells):
            key=tuple(bits[j] for j in range(4) if j!=i)
            bucket=cell.get(key)
            if bucket is None: continue
            if sum(bucket)<self.support or bucket[0]==bucket[1]: continue
            votes.append(bucket[1]>bucket[0])
        if len(votes)<min_votes: return None
        yes=votes.count(True)
        no=len(votes)-yes
        if yes>=min_votes and yes>no: return True
        if no>=min_votes and no>yes: return False
        return None

    def records(self):
        return sum(len(cell) for cell in self.cells)
