"""MG94-J source-free two-state Bayesian change-point control; not native science."""
import json
from fractions import Fraction
STREAMS={"stable_zero":[0]*16,"stable_one":[1]*16,"one_reversal":[1]*8+[0]*8,"two_reversals":[1]*6+[0]*6+[1]*6}
HAZARD=Fraction(1,8)
RELIABILITY=Fraction(7,8)
def bayes(hist):
    p=Fraction(1,2)
    for bit in hist:
        prior=p*(1-HAZARD)+(1-p)*HAZARD
        one=RELIABILITY if bit else (1-RELIABILITY)
        p=prior*one/(prior*one+(1-prior)*(1-one))
    next_p=p*(1-HAZARD)+(1-p)*HAZARD
    return None if next_p==Fraction(1,2) else int(next_p>Fraction(1,2))
def cumulative(hist):
    if not hist:return None
    return None if 2*sum(hist)==len(hist) else int(2*sum(hist)>len(hist))
def window4(hist):
    if not hist:return None
    x=hist[-4:]
    return None if 2*sum(x)==len(x) else int(2*sum(x)>len(x))
def discounted(hist):
    if not hist:return None
    w=sum(Fraction(x,2**(len(hist)-i-1)) for i,x in enumerate(hist))
    t=sum(Fraction(1,2**(len(hist)-i-1)) for i in range(len(hist)))
    return None if 2*w==t else int(2*w>t)
def run():
    methods={"cumulative":cumulative,"window4":window4,"discount_half":discounted,"bayesian_hmm_fixed":bayes}
    results={}
    for name,events in STREAMS.items():
        results[name]={}
        for label,method in methods.items():
            predictions=[method(events[:i]) for i in range(len(events))]
            results[name][label]={"correct":sum(a==b for a,b in zip(predictions,events)),"abstain":sum(a is None for a in predictions),"total":len(events)}
    report={"schema":"mg94.change_point_controls.source_free.v1","classification":"SYNTHETIC_DEVELOPMENT_ONLY","model":"fixed two-state Bayesian HMM, hazard=1/8, public emission reliability=7/8","native_advantage":"UNTESTED","original_world":"NOT_EXECUTED","results":results}
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=="__main__":run()
