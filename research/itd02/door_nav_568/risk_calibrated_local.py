"""Risk-calibrated prediction from independent local sensory evidence.

Only completed PUBLIC training observations calibrate the gate. No hidden
regime labels or held-out targets are available to threshold selection.
Calibration uses prequential predictions before subsequent observations.
"""
from local_feature_selector import LocalFeatureSelector

class RiskCalibratedLocal(LocalFeatureSelector):
    def __init__(self, min_support=2, max_error=0.2):
        super().__init__()
        if type(min_support) is not int or not 2 <= min_support <= 8:
            raise ValueError("MIN_SUPPORT_INVALID")
        if not isinstance(max_error,(float,int)) or not 0 <= max_error <= 0.5:
            raise ValueError("MAX_ERROR_INVALID")
        self.min_support=min_support
        self.max_error=max_error
        self.calibration={threshold:[0,0] for threshold in (0.5,0.75,1.0)}
        self.calibration_examples=0

    def candidate(self,bits):
        self.validate(bits)
        votes=[]
        for i,cell in enumerate(self.cells):
            options=[]
            for distance in (1,2):
                counts=cell.get((distance,bits[i],bits[(i+distance)%4]),(0,0))
                total=sum(counts)
                if total < self.min_support: continue
                fraction=max(counts)/total
                if fraction <= 0.5: continue
                options.append((fraction,total,-distance,counts[1]>counts[0]))
            if options: votes.append(max(options)[3])
        if len(votes)<3: return None,0.0
        yes=votes.count(True)
        no=len(votes)-yes
        if yes==no: return None,0.0
        return yes>no,max(yes,no)/len(votes)

    def observe_calibration(self,bits,label):
        self.validate(bits)
        if type(label) is not bool: raise ValueError("PUBLIC_LABEL_REQUIRED")
        prediction,confidence=self.candidate(bits)
        for cutoff,data in self.calibration.items():
            if prediction is not None and confidence >= cutoff:
                data[0]+=1
                data[1]+=int(prediction != label)
        self.calibration_examples+=1
        self.observe(bits,label)

    def cutoff(self):
        # Wilson upper 90%-bound; fail closed on small samples.
        from math import sqrt
        for threshold in (0.5,0.75,1.0):
            n,errors=self.calibration[threshold]
            if n<5: continue
            z=1.645
            p=errors/n
            bound=(p+z*z/(2*n)+z*sqrt((p*(1-p)+z*z/(4*n))/n))/(1+z*z/n)
            if bound<=self.max_error: return threshold
        return None

    def predict(self,bits):
        selected=self.cutoff()
        if selected is None: return None
        value,confidence=self.candidate(bits)
        return value if value is not None and confidence >= selected else None
