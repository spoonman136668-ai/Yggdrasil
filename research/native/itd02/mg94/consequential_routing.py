"""MG94-X development-only consequence ablation; NOT scientific acceptance.

Local surprise sends a public outcome to peer's predictive counter at threshold.
Same public observation stream and fixed update budget; conventional mirrored
update control is algorithmically equivalent to routing-on.
"""
from itertools import product

class Cells:
    def __init__(self, route):
        self.route=route
        self.counter=[1,1]
        self.alert=[0,0]
        self.previous=None
        self.messages=0
    def step(self, bit):
        if type(bit) is not int or bit not in (0,1):
            raise ValueError('PUBLIC_BIT_REQUIRED')
        if self.previous is None:
            self.previous=bit
            return None
        cell=self.previous
        predicted=int(self.counter[cell]>=2)
        wrong=(predicted != bit)
        self.counter[cell]= min(3,self.counter[cell]+1) if bit else max(0,self.counter[cell]-1)
        self.alert[cell]=min(3,self.alert[cell]+1) if wrong else max(0,self.alert[cell]-1)
        if self.route and self.alert[cell]==3:
            peer=1-cell
            self.counter[peer]=min(3,self.counter[peer]+1) if bit else max(0,self.counter[peer]-1)
            self.messages+=1
        self.previous=bit
        return predicted

def compare(seq):
    on,off=Cells(True),Cells(False)
    po=[on.step(x) for x in seq]
    pf=[off.step(x) for x in seq]
    return {'messages':on.messages,'differences':sum(a!=b for a,b in zip(po,pf)),
            'on_correct':sum(p==v for p,v in zip(po,seq)),
            'off_correct':sum(p==v for p,v in zip(pf,seq))}

def run():
    activation=None
    divergence=None
    for n in range(1,13):
        for seq in product((0,1), repeat=n):
            r=compare(seq)
            if r['messages'] and activation is None:activation=(''.join(map(str,seq)),r)
            if r['differences'] and divergence is None:divergence=(''.join(map(str,seq)),r)
        if activation and divergence:break
    scenarios={'stable':[0]*24,'reversal':[0]*8+[1]*16,'recurrence':[0]*8+[1]*8+[0]*8,'alternating':[0,1]*12,'blocks2':[0,0,1,1]*6}
    results={k:compare(v) for k,v in scenarios.items()}
    assert activation and divergence
    return activation,divergence,results

if __name__=='__main__':
    import json
    a,d,r=run()
    print(json.dumps({'activation':a,'first_divergence':d,'scenarios':r},indent=2,sort_keys=True))
