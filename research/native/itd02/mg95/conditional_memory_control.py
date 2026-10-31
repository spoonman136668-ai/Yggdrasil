"""MG95-B conditional causal memory, honest capacity-matched screening.

All features (action, context, intervention) are public. The conditional
lookup is a conventional baseline, NOT a Yggdrasil-native learning result.
State capacities include all stored outcome bits and validity bits.
"""
from itertools import product
from intervention_memory_screen import environment
import json

TRAIN=list(product((0,1),repeat=3))*3
TEST=[(a,1-c,1) for a,c,i in TRAIN]

class Lookup:
    def __init__(self,key):
        self.key=key
        self.out=[0]*8
        self.seen=[0]*8
    def index(self,a,c,i):
        if self.key=="full":return (a<<2)|(c<<1)|i
        if self.key=="action":return a
        if self.key=="context":return c
        raise ValueError("key")
    def predict(self,a,c,i):
        k=self.index(a,c,i)
        return self.out[k] if self.seen[k] else 0
    def learn(self,a,c,i,y):
        k=self.index(a,c,i)
        self.out[k]=y
        self.seen[k]=1
    def size_bits(self):
        return len(self.out)+len(self.seen)

def measure(key):
    model=Lookup(key)
    for a,c,i in TRAIN:model.learn(a,c,i,environment(a,c,i))
    before=(tuple(model.out),tuple(model.seen))
    correct=sum(model.predict(a,c,i)==environment(a,c,i) for a,c,i in TEST)
    assert before==(tuple(model.out),tuple(model.seen))
    return {"correct":correct,"total":len(TEST),"allocated_bits":model.size_bits()}

def run():
    return {"full_conditional":measure("full"),"action_only":measure("action"),
            "context_only":measure("context"),
            "interpretation":"Full conditional lookup is conventional; allocate parity before scientific comparison."}
if __name__=="__main__":print(json.dumps(run(),indent=2,sort_keys=True))
