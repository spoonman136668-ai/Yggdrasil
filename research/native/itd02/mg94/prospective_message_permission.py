"""MG94-AB: prospective, prequential public-message policy screening.

Development-only conventional online policy. The policy decides before the
next outcome, learns only from previously observed outcomes, and pays for
messages. No use of paired future counterfactual labels for online decisions.
"""
from consequential_routing import Cells

STREAMS = {
    "train_repetition": [0,1,0,0,1,1]*8,
    "stable": [0]*24,
    "reversal": [0]*8+[1]*16,
    "alternating": [0,1]*12,
    "blocks2": [0,0,1,1]*6,
}

class LearnedPermission(Cells):
    def __init__(self):
        super().__init__(False)
        self.value = [0,0]  # two public-context signed evidence counters
    def step(self,bit):
        if self.previous is None:
            return super().step(bit)
        receiver=self.previous
        predicted=int(self.counter[receiver]>=2)
        wrong=int(predicted!=bit)
        old=self.counter[receiver]
        result=super().step(bit)
        # A permission can only depend on already observed past mistakes.
        if self.alert[receiver]==3 and self.value[receiver]>0:
            peer=1-receiver
            self.counter[peer]=min(3,self.counter[peer]+1) if bit else max(0,self.counter[peer]-1)
            self.messages+=1
        # Proxy is public error reduction at this cell, not future message value.
        self.value[receiver]=max(-3,min(3,self.value[receiver]+(1 if wrong and old in (1,2) else -1)))
        return result

def assess(seq, actor):
    correct=0
    for outcome in seq:
        correct+= actor.step(outcome)==outcome
    return {"correct":correct,"messages":actor.messages,
            "net":correct-actor.messages}

def run():
    result={}
    for name,seq in STREAMS.items():
        off=assess(seq,Cells(False))
        on=assess(seq,Cells(True))
        learned=assess(seq,LearnedPermission())
        result[name]={"off":off,"on":on,"learned_proxy":learned}
    return result
if __name__=="__main__":
    import json
    print(json.dumps(run(),sort_keys=True,indent=2))
