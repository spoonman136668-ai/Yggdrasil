"""Independent batch set-based GF2 fit and model-relative query reduction."""
import itertools
from equations import BankModel


class BatchBank:
    def __init__(self,width,degree,rows):
        self.width=width;limit=width if degree=='full' else degree
        self.features=tuple(c for k in range(limit+1) for c in itertools.combinations(range(width),k))
        self.facts=dict(rows);self.pivots={};self.fault=False
        for x,y in rows:
            active={i for i,c in enumerate(self.features) if all(x>>j&1 for j in c)};rhs=y
            while active:
                key=min(active)
                if key not in self.pivots:self.pivots[key]=(set(active),rhs);break
                other,value=self.pivots[key];active.symmetric_difference_update(other);rhs^=value
            if not active and rhs:self.fault=True
    def predict(self,state):
        if state in self.facts:return self.facts[state]
        active={i for i,c in enumerate(self.features) if all(state>>j&1 for j in c)};answer=0
        while active:
            key=min(active)
            if key not in self.pivots:return None
            other,value=self.pivots[key];active.symmetric_difference_update(other);answer^=value
        return None if self.fault else answer


class BatchModel(BankModel):pass


class BatchAdaptive(BankModel):
    def __init__(self,models):self.models=models
    def apply(self,action,state):
        for model in self.models:
            if not model.banks[action].fault:return model.banks[action].predict(state)
        return self.models[-1].banks[action].facts.get(state)
