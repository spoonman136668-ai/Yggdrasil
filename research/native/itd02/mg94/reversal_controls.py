"""MG94-I: synthetic equal-information reversal controls, not original-world science."""
import json
from fractions import Fraction
STREAMS={"stable_zero":[0]*16,"stable_one":[1]*16,"one_reversal":[1]*8+[0]*8,"two_reversals":[1]*6+[0]*6+[1]*6}
def predict(hist,method):
    if not hist:return None
    if method=="cumulative": s=hist
    elif method=="window4": s=hist[-4:]
    elif method=="discount_half":
        w=sum(Fraction(x,2**(len(hist)-1-i)) for i,x in enumerate(hist))
        total=sum(Fraction(1,2**(len(hist)-1-i)) for i in range(len(hist)))
        return None if 2*w==total else int(2*w>total)
    else:raise ValueError(method)
    return None if 2*sum(s)==len(s) else int(2*sum(s)>len(s))
def run():
    outcomes={}
    for name,sequence in STREAMS.items():
        outcomes[name]={}
        for method in ("cumulative","window4","discount_half"):
            predictions=[predict(sequence[:i],method) for i in range(len(sequence))]
            outcomes[name][method]={"correct":sum(p==y for p,y in zip(predictions,sequence)),"abstain":sum(p is None for p in predictions),"total":len(sequence),"final_prediction_after_last_event":predict(sequence,method)}
    assert predict(STREAMS["one_reversal"],"cumulative") is None
    assert predict(STREAMS["one_reversal"],"window4")==0
    assert predict(STREAMS["one_reversal"],"discount_half")==0
    result={"schema":"mg94.reversal.controls.source_free.v1","classification":"SYNTHETIC_DEVELOPMENT_ONLY","streams":STREAMS,"outcomes":outcomes,"bayesian_change_point_control":"NOT_IMPLEMENTED","native_distributed_learner":"NOT_IMPLEMENTED","original_environment":"NOT_EXECUTED","scientific_gain":"UNVERIFIED"}
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":run()
