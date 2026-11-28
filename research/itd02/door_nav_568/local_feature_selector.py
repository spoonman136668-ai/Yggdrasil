"""Learned local receptive selection, experimental (not production R7).

Each of four cells owns two adjacent public sensor-pair candidates. Every
completed public outcome updates local pair-value evidence independently.
Each cell selects the candidate with lowest empirical label conflict,
abstaining for insufficient evidence or tied conflicting labels. Predictions
aggregate locally learned votes; no global state-to-answer table or oracle.
"""
from collections import defaultdict

class LocalFeatureSelector:
    def __init__(self, cap=16):
        if type(cap) is not int or not 1<=cap<=16:
            raise ValueError("LOCAL_FEATURE_CAP")
        self.cap=cap
        self.cells=[{}, {}, {}, {}]
        self.updates=0

    @staticmethod
    def validate(bits):
        if type(bits) is not tuple or len(bits)!=4 or any(type(x) is not bool for x in bits):
            raise ValueError("FOUR_PUBLIC_BITS_REQUIRED")

    def observe(self,bits,label):
        self.validate(bits)
        if type(label) is not bool:
            raise ValueError("PUBLIC_LABEL_REQUIRED")
        for i,cell in enumerate(self.cells):
            for distance in (1,2):
                key=(distance,bits[i],bits[(i+distance)%4])
                if key not in cell and len(cell)>=self.cap:
                    raise ValueError("LOCAL_FEATURE_CAP_REACHED")
        for i,cell in enumerate(self.cells):
            for distance in (1,2):
                key=(distance,bits[i],bits[(i+distance)%4])
                counts=cell.setdefault(key,[0,0])
                counts[int(label)]+=1
        self.updates+=1

    def predict(self,bits):
        self.validate(bits)
        votes=[]
        for i,cell in enumerate(self.cells):
            options=[]
            for distance in (1,2):
                key=(distance,bits[i],bits[(i+distance)%4])
                counts=cell.get(key,[0,0])
                total=sum(counts)
                if total<2:
                    continue
                confidence=abs(counts[1]-counts[0])/total
                if confidence==0:
                    continue
                options.append((confidence,total,-distance,counts[1]>counts[0]))
            if options:
                votes.append(max(options)[3])
        if len(votes)<3:
            return None
        yes=votes.count(True)
        no=len(votes)-yes
        if yes>=3 and yes>no:
            return True
        if no>=3 and no>yes:
            return False
        return None

    def records(self):
        return sum(len(x) for x in self.cells)
