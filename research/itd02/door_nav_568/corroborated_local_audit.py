"""Held-out risk and coverage of independently corroborated local prediction.

Compare against prior native voting, a deterministic online linear control,
and a tabular abstention control, with identical completed public examples.
Abstention is not scored as correctness; zero-risk trivial abstention is not
presented as successful generalization.
"""
import json
from time import process_time_ns
from corroborated_local_selector import CorroboratedLocalSelector
from local_feature_selector import LocalFeatureSelector
from learned_feature_comparison_audit import LinearControl, grade
from specialization_scaling_audit import families
from sliding_tabular_control import SlidingTabularControl

def trial(seed, count, rule):
    cases = families(seed)
    if rule == "first_bit":
        cases = [(bits, bits[0]) for bits,_ in cases]
    elif rule != "parity":
        raise ValueError("UNSUPPORTED_PUBLIC_RULE")
    trained,heldout = cases[:count],cases[count:]
    candidates = {
        "original":LocalFeatureSelector(),
        "corroborated":CorroboratedLocalSelector(),
        "linear":LinearControl(),
        "tabular":SlidingTabularControl(capacity=16),
    }
    cpu = {key:0 for key in candidates}
    for _ in range(2):
        for bits,value in trained:
            for name,policy in candidates.items():
                start=process_time_ns()
                if name=="tabular":
                    policy.observe((bytes(map(int,bits)),0),b"1" if value else b"0")
                else:
                    policy.observe(bits,value)
                cpu[name]+=process_time_ns()-start
    def tabular_predict(bits):
        answer=candidates["tabular"].predict((bytes(map(int,bits)),0))
        return None if answer is None else answer==b"1"
    prediction = {name:policy.predict for name,policy in candidates.items()
                  if name!="tabular"}
    prediction["tabular"]=tabular_predict
    return {
        "seed":seed,"count":count,"rule":rule,"actions":2*count,
        "updates":{name:policy.updates if name!="tabular" else policy.examples
                   for name,policy in candidates.items()},
        "training":{name:grade(fn,trained) for name,fn in prediction.items()},
        "heldout":{name:grade(fn,heldout) for name,fn in prediction.items()},
        "records":{name:policy.records() for name,policy in candidates.items()
                   if name in ("original","corroborated","tabular")},
        "cpu_ns":cpu,
    }

def run():
    rows=[trial(seed,n,rule) for rule in ("parity","first_bit")
          for seed in (3,17,41) for n in (4,8,12)]
    return {
        "experiments":rows,
        "scope":"Matched train/test partitions, same public observations, risk/coverage for strict local corroboration",
        "limitation":"Handcrafted four-bit worlds, no causal transfer guarantee or original DoorKey evidence.",
    }

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
