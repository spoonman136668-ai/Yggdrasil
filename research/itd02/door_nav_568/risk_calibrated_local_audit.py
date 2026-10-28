"""Matched public-action evidence with prequential risk calibration.

Calibration runs predict-before-update on each second-pass public outcome;
baseline learners receive the exact same action/observation sequence.
A gate with zero held-out coverage FAILS scientific usefulness regardless
of zero errors. This audit never uses held-out labels to choose thresholds.
"""
import json
from time import process_time_ns
from risk_calibrated_local import RiskCalibratedLocal
from local_feature_selector import LocalFeatureSelector
from learned_feature_comparison_audit import LinearControl,grade
from specialization_scaling_audit import families

def trial(seed,count,rule):
    cases=families(seed)
    if rule=="first_bit":
        cases=[(bits,bits[0]) for bits,_ in cases]
    train,hold=cases[:count],cases[count:]
    adaptive=RiskCalibratedLocal()
    raw=LocalFeatureSelector()
    linear=LinearControl()
    cpu={"calibrated":0,"raw":0,"linear":0}
    for repeat in range(2):
        for bits,target in train:
            for name,learner in (("calibrated",adaptive),("raw",raw),("linear",linear)):
                begin=process_time_ns()
                if name=="calibrated" and repeat==1:
                    learner.observe_calibration(bits,target)
                else: learner.observe(bits,target)
                cpu[name]+=process_time_ns()-begin
    return {"seed":seed,"count":count,"rule":rule,"actions":2*count,
            "updates":{"calibrated":adaptive.updates,"raw":raw.updates,"linear":linear.updates},
            "calibration_actions":adaptive.calibration_examples,
            "calibration_counts":adaptive.calibration,
            "chosen_cutoff":adaptive.cutoff(),
            "train":{"calibrated":grade(adaptive.predict,train),
                     "raw":grade(raw.predict,train),"linear":grade(linear.predict,train)},
            "heldout":{"calibrated":grade(adaptive.predict,hold),
                       "raw":grade(raw.predict,hold),"linear":grade(linear.predict,hold)},
            "cpu_ns":cpu}
def run():
    rows=[trial(seed,count,rule) for rule in ("parity","first_bit")
          for seed in (3,17,41) for count in (4,8,12)]
    return {"experiments":rows,
            "scope":"Prequential confidence calibration from public completed observations only",
            "limitations":"Small synthetic families; a zero-coverage safe gate is NOT learning success; no original DoorKey, hardware or persistent-memory gain."}
if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
