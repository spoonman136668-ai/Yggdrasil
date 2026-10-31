"""MG94-Q source-free four-bit adaptive transition control. NOT native science.

Two public-context bits each own a two-bit saturating counter (four learned bits).
Uses only previous public outcome; no privileged state, labels, oracle or reward.
This is a standard conventional finite-state predictor, NOT native cognition.
"""
from collections import deque
import json
import random

STREAMS={'stable':[0]*24,'reversal':[0]*8+[1]*16,'recurrence':[0]*8+[1]*8+[0]*8,'alternating':[0,1]*12,'blocks2':[0,0,1,1]*6}
BUDGET=4
SEED=1904

def vote(bits):
    if not bits or 2*sum(bits)==len(bits): return None
    return int(2*sum(bits)>len(bits))

def conventional(seq,policy):
    sample=[];recent=deque(maxlen=4);rng=random.Random(SEED);correct=0;abstain=0
    for i,actual in enumerate(seq):
        pred=vote(list(recent) if policy=='recent' else sample)
        correct+=pred==actual;abstain+=pred is None
        recent.append(actual)
        if len(sample)<4: sample.append(actual)
        elif policy=='reservoir':
            j=rng.randrange(i+1)
            if j<4:sample[j]=actual
        elif policy=='recent':sample=list(recent)
        elif policy!='first':raise ValueError(policy)
    return {'correct':correct,'abstain':abstain}

def adaptive(seq):
    counters=[1,1] # two 2-bit weak-0 counters, 4 learned bits
    previous=None;correct=0;abstain=0;steps=0
    for actual in seq:
        pred=None if previous is None else int(counters[previous]>=2)
        correct+=pred==actual;abstain+=pred is None
        if previous is not None:
            counters[previous]=min(3,counters[previous]+1) if actual else max(0,counters[previous]-1)
            steps+=1
        previous=actual
        assert all(0<=v<=3 for v in counters)
    return {'correct':correct,'abstain':abstain,'final_counters':counters,'trained_updates':steps}

def run():
    result={k:{**{p:conventional(s,p) for p in ('first','recent','reservoir')},'two_bit_context':adaptive(s)} for k,s in STREAMS.items()}
    assert all(len(s)==24 for s in STREAMS.values())
    assert adaptive(STREAMS['alternating'])['correct']>conventional(STREAMS['alternating'],'recent')['correct']
    print(json.dumps({'schema':'mg94.four_bit_markov_control.v1','classification':'DEVELOPMENT_ONLY_CONVENTIONAL_FINITE_STATE_CONTROL','bits':4,'seed':SEED,'results':result,'original_world':'NOT_EXECUTED','scientific_gain':'NOT_ESTABLISHED'},indent=2,sort_keys=True))
if __name__=='__main__':run()
