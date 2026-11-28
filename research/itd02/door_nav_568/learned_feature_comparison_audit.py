"""Matched outcome-driven local selection versus conventional linear model.

Inputs and public labels are identical. The conventional control uses a
four-feature online perceptron with deterministic update rule. The second
control is a tabular learner. No model receives the withheld test labels.
"""
import json
from time import process_time_ns
from specialization_scaling_audit import families
from local_feature_selector import LocalFeatureSelector
from sliding_tabular_control import SlidingTabularControl
from local_feature_sufficiency_audit import conflicts

class LinearControl:
    def __init__(self):
        self.weights=[0]*5
        self.updates=0

    def predict(self,bits):
        value=self.weights[4]+sum(self.weights[i]*(1 if bits[i] else -1)
                                  for i in range(4))
        return None if value==0 else value>0

    def observe(self,bits,result):
        actual=self.predict(bits)
        if actual is None or actual!=result:
            sign=1 if result else -1
            for i in range(4):
                self.weights[i]+=sign*(1 if bits[i] else -1)
            self.weights[4]+=sign
        self.updates+=1

def grade(fn,cases):
    values=[fn(bits) for bits,_ in cases]
    return {"correct":sum(v is not None and v==y for v,(_,y) in zip(values,cases)),
            "wrong":sum(v is not None and v!=y for v,(_,y) in zip(values,cases)),
            "abstentions":sum(v is None for v in values)}

def trial(seed,count,rule="parity"):
    cases=families(seed)
    if rule=="first_bit":
        cases=[(bits,bits[0]) for bits,_ in cases]
    elif rule!="parity":
        raise ValueError("UNKNOWN_FIXTURE_RULE")
    train,hold=cases[:count],cases[count:]
    native=LocalFeatureSelector()
    tabular=SlidingTabularControl(capacity=16)
    linear=LinearControl()
    times={"native":0,"tabular":0,"linear":0}
    for _ in range(2):
        for bits,label in train:
            for name,model in (("native",native),("tabular",tabular),("linear",linear)):
                start=process_time_ns()
                if name=="tabular":
                    model.observe((bytes(map(int,bits)),0),b"1" if label else b"0")
                else:
                    model.observe(bits,label)
                times[name]+=process_time_ns()-start
    def tab(bits):
        result=tabular.predict((bytes(map(int,bits)),0))
        return None if result is None else result==b"1"
    policies={"native":native.predict,"tabular":tab,"linear":linear.predict}
    return {"seed":seed,"count":count,"rule":rule,"actions":2*count,
            "updates":{"native":native.updates,"tabular":tabular.examples,
                       "linear":linear.updates},
            "trained":{name:grade(fn,train) for name,fn in policies.items()},
            "heldout":{name:grade(fn,hold) for name,fn in policies.items()},
            "native_records":native.records(),
            "native_conflicts":conflicts(train),
            "cpu_ns":times}

def run():
    return {"experiments":[trial(seed,n,rule) for rule in ("parity","first_bit")
                            for seed in (3,17,41) for n in (4,8,12)],
            "scope":"Outcome-driven local feature choice vs matched tabular and online linear models",
            "limits":"Synthetic 4-bit public frames, handcrafted candidate receptive fields, no original DoorKey or autonomous feature discovery."}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
