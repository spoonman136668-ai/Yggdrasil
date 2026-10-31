"""MG94-AD frozen train/eval routing-selection conventional control.

No native learner, no original-world access. Development-only prospective screen.
Select either unconditional routing or no routing using *training* net reward.
Frozen selection applied to held-out streams without adaptation or reselection.
"""
from consequential_routing import Cells
import json

TRAIN = {
  "train_irregular": [0,1,0,0,1,1]*5,
  "train_blocks": [0,0,1,1]*7,
}
HELDOUT = {
  "heldout_irregular_shift": [1,0,0,1,1,0]*4,
  "heldout_blocks_shift": [1,1,0,0]*6,
  "heldout_alternating": [1,0]*12,
  "heldout_stable": [1]*24,
}
COST = 1

def score(seq, route):
    model = Cells(route)
    correct = sum(model.step(bit) == bit for bit in seq)
    return {"correct": correct, "messages": model.messages,
            "net": correct-COST*model.messages}

def run():
    train = {name:{str(route):score(seq,route)
             for route in (False,True)} for name,seq in TRAIN.items()}
    off_net = sum(result["False"]["net"] for result in train.values())
    on_net = sum(result["True"]["net"] for result in train.values())
    frozen_route = on_net > off_net # tie goes to cheaper disabled control
    heldout = {name:{"selected":score(seq,frozen_route),
                     "disabled":score(seq,False),
                     "always":score(seq,True)}
               for name,seq in HELDOUT.items()}
    assert set(TRAIN).isdisjoint(HELDOUT)
    assert not frozen_route if on_net <= off_net else frozen_route
    return {"schema":"mg94.frozen_routing_selector.v1",
            "classification":"SYNTHETIC_DEVELOPMENT_ONLY",
            "cost_per_message":COST,
            "train":train,"train_net_off":off_net,"train_net_on":on_net,
            "frozen_route":frozen_route,"heldout":heldout,
            "native_scientific_claim":"NONE","original_world":"NOT_EXECUTED"}
if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
