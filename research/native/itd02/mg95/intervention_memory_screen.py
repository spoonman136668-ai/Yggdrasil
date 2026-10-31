"""MG95-A: causal intervention memory under distractor interference.

Synthetic, deterministic, offline development screen. No native architecture
claim. Both learners see identical training events and use two 2-bit counters.
An intervention flag is public; one learner conditions on it, the conventional
unconditional learner does not. Outcome is a deterministic XOR gate.
"""
from itertools import product
import json

def environment(action, context, intervention):
    # An intervention replaces the visible context's ordinary causal influence.
    return action ^ (context if not intervention else 0)

class TwoCounters:
    def __init__(self, gate):
        self.gate=gate
        self.ones=[0,0]
        self.total=[0,0]
    def key(self, action, context, intervention):
        # Two counters only: causal action effects vs observational context.
        return action if self.gate else context
    def predict(self, action, context, intervention):
        k=self.key(action,context,intervention)
        return int(self.ones[k]*2 >= self.total[k] and self.total[k]>0)
    def observe(self, action, context, intervention, outcome):
        k=self.key(action,context,intervention)
        if self.total[k] >= 3:
            self.ones[k] = (self.ones[k]+outcome+1)//2
        else:
            self.ones[k]+=outcome
            self.total[k]+=1

def trial(model, stream, train):
    correct=0
    for action,context,intervention in stream:
        outcome=environment(action,context,intervention)
        correct+=model.predict(action,context,intervention)==outcome
        if train: model.observe(action,context,intervention,outcome)
    return correct

def run():
    training=list(product((0,1),(0,1),(0,1)))*3
    # Pure intervened holdout; a distractor reversal in observed context.
    holdout=[(a,1-c,True) for a,c,_ in training]
    output={}
    for name,gate in (("action_memory",True),("context_memory",False)):
        learner=TwoCounters(gate)
        trial(learner,training,True)
        frozen=(learner.ones[:],learner.total[:])
        score=trial(learner,holdout,False)
        assert frozen==(learner.ones,learner.total)
        output[name]={"correct":score,"total":len(holdout),"state":frozen}
    return output

if __name__=="__main__":
    print(json.dumps(run(),indent=2,sort_keys=True))
