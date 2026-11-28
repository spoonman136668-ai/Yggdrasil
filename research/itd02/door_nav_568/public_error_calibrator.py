"""Prequential risk calibration from earlier completed public-world episodes.

No target ground truth enters the calibration model at prediction time.
A Wilson upper bound on observed wrong predictions gates transfer.
The learned risk applies to a shared public feature: surviving-memory
count and the number of public target probes.
"""
from math import sqrt

class PublicErrorCalibrator:
    def __init__(self,min_predictions=5,max_upper_error=0.20):
        if type(min_predictions) is not int or min_predictions<1:
            raise ValueError("INVALID_MIN_HISTORY")
        if not 0<=max_upper_error<=1:
            raise ValueError("INVALID_RISK_LIMIT")
        self.minimum=min_predictions
        self.maximum=max_upper_error
        self.history={}

    def record_completed(self,key,prediction,outcome):
        if (type(key) is not tuple or len(key)!=2 or
            type(key[0]) is not int or type(key[1]) is not int or
            key[0]<0 or key[1]<0 or type(prediction) is not bool or
            type(outcome) is not bool):
            raise ValueError("PUBLIC_COMPLETED_FEEDBACK_REQUIRED")
        bucket=self.history.setdefault(key,[0,0])
        bucket[0]+=1
        bucket[1]+=int(prediction!=outcome)

    def upper_error(self,key):
        n,errors=self.history.get(key,(0,0))
        if n<self.minimum:return 1.0
        z=1.6448536269514722
        p=errors/n
        denominator=1+z*z/n
        return min(1.0,(p+z*z/(2*n)+z*sqrt((p*(1-p)+z*z/(4*n))/n))/denominator)

    def accept(self,key,prediction):
        if prediction is None:return None
        if type(prediction) is not bool:raise ValueError("BOOLEAN_PREDICTION_REQUIRED")
        return prediction if self.upper_error(key)<=self.maximum else None

    def total(self):
        return sum(n for n,_ in self.history.values())
