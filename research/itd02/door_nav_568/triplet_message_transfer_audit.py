"""Matched local triplet messages against conventional triple-feature control.

Each intervention supplies the same completed public outcome to both.
All unknowns count as abstention. Three-cell consensus is a predeclared
candidate, not a calibrated or proven scientific improvement.
"""
import json
from time import process_time_ns
from specialization_scaling_audit import families
from triplet_message_cells import TripletMessageCells
from learned_feature_comparison_audit import LinearControl, grade
from sliding_tabular_control import SlidingTabularControl

class ConventionalTripletVote:
    def __init__(self,support=2):
        self.counts={}
        self.support=support
        self.updates=0

    def observe(self,bits,result):
        # Conventional full-frame dictionary of four triplet projections.
        for dropped in range(4):
            key=(dropped,tuple(bits[i] for i in range(4) if i!=dropped))
            bucket=self.counts.setdefault(key,[0,0])
            bucket[int(result)]+=1
        self.updates+=1

    def predict(self,bits):
        values=[]
        for dropped in range(4):
            key=(dropped,tuple(bits[i] for i in range(4) if i!=dropped))
            bucket=self.counts.get(key,[0,0])
            if sum(bucket)<self.support or bucket[0]==bucket[1]: continue
            values.append(bucket[1]>bucket[0])
        if len(values)<3:return None
        yes=values.count(True)
        no=len(values)-yes
        return True if yes>=3 else False if no>=3 else None

def trial(seed,count,rule):
    all_cases=families(seed)
    if rule=="first_bit":
        all_cases=[(bits,bits[0]) for bits,_ in all_cases]
    elif rule!="parity":
        raise ValueError("RULE_INVALID")
    train,test=all_cases[:count],all_cases[count:]
    agents={"local":TripletMessageCells(),"triplet_table":ConventionalTripletVote(),
            "linear":LinearControl(),"tabular":SlidingTabularControl(capacity=16)}
    cpu={name:0 for name in agents}
    for _ in range(2):
        for bits,value in train:
            for name,agent in agents.items():
                start=process_time_ns()
                if name=="tabular":
                    agent.observe((bytes(map(int,bits)),0),b"1" if value else b"0")
                else:agent.observe(bits,value)
                cpu[name]+=process_time_ns()-start
    def conventional(bits):
        answer=agents["tabular"].predict((bytes(map(int,bits)),0))
        return None if answer is None else answer==b"1"
    predict={name:agent.predict for name,agent in agents.items() if name!="tabular"}
    predict["tabular"]=conventional
    return {"seed":seed,"count":count,"rule":rule,"actions":2*count,
            "updates":{name:agent.examples if name=="tabular" else agent.updates for name,agent in agents.items()},
            "train":{name:grade(fn,train) for name,fn in predict.items()},
            "heldout":{name:grade(fn,test) for name,fn in predict.items()},
            "local_records":agents["local"].records(),
            "tabular_triplet_records":len(agents["triplet_table"].counts),
            "cpu_ns":cpu}

def run():
    return {
        "experiments":[trial(seed,count,rule) for rule in ("parity","first_bit")
                       for seed in (3,17,41) for count in (4,8,12)],
        "scope":"4 independent three-sensor cell maps and conventional triplet control, identical completed public observations",
        "limits":"Synthetic binary frames, no learned compositional operations; triplet projections are predefined and conventional control uses the same information.",
    }

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
