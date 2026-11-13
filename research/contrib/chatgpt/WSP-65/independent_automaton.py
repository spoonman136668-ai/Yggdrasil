"""Independent latent-parity empirical automaton control for WSP65.

Same 128 charged public experiences and a comparable binary mode/toggle
hypothesis prior, but *no* numerical Boolean polynomial fit, no WSP65 learner
imports and no evaluator source import. This is the stronger history-memory
control for the mode-sensitive new-history probes, added before first outcome.
"""
from __future__ import annotations

ACTIONS=(0,1,2,3)


class LatentModeLookup:
    def __init__(self,charged):
        self.dimension=len(charged[0][0])
        models=[]
        for toggle in (*ACTIONS,None):
            h=0
            rows={}
            consistent=True
            for before,action,after in charged:
                key=(before,h,action)
                if key in rows and rows[key]!=after:
                    consistent=False
                    break
                rows[key]=after
                if action==toggle:
                    h^=1
            if consistent:
                models.append((toggle,rows))
        self.models=tuple(models)

    def predict(self,history,current,action):
        if type(current) is not tuple or len(current)!=self.dimension:
            raise ValueError("invalid public visible sensor tuple")
        observed=[]
        for toggle,table in self.models:
            h=sum(row.action==toggle for row in history)%2 if toggle is not None else 0
            value=table.get((current,h,action))
            if value is None:
                return None
            observed.append(value)
        if not observed or len(set(observed))!=1:
            return None
        return observed[0]

    def candidate_togglers(self):
        return tuple(toggle for toggle,table in self.models)
