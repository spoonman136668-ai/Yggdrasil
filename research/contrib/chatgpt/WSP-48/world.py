"""Frozen WSP45 generator, new WSP46 world tags supplied by evaluator."""
import random
import hashlib
from frozen_numeric import ActionModel

def rng_for(tag):return random.Random(int.from_bytes(hashlib.sha256(tag.encode()).digest(),'big'))


class World:
    def __init__(self,width,family,tag):
        self.width,self.family,self.tag=width,family,tag
        rng=rng_for(tag);self.rows=[];self.bias=[];self.terms=[]
        for action in range(2):
            self.rows.append(tuple(tuple(rng.sample(range(width),4)) for _ in range(width)))
            self.bias.append(rng.randrange(1<<width));terms=[];used=set()
            degree={'linear':0,'quadratic':2,'cubic_ood':3,'arbitrary_hash':0}[family]
            while degree and len(used)<4:
                indices=tuple(sorted(rng.sample(range(width),degree)))
                if indices in used:continue
                used.add(indices);terms.append((indices,rng.randrange(1,1<<width)))
            self.terms.append(tuple(terms))

    def apply(self,action,state):
        if self.family=='arbitrary_hash':return hashlib.sha256(f'{self.tag}|{action}|{state}'.encode()).digest()[0]&((1<<self.width)-1)
        out=self.bias[action]
        for bit,inputs in enumerate(self.rows[action]):out^=(sum(state>>i&1 for i in inputs)%2)<<bit
        for inputs,c in self.terms[action]:
            if all(state>>i&1 for i in inputs):out^=c
        return out

    rollout=ActionModel.rollout

