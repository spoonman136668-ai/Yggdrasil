"""MG94-R conventional packed predictors; development only."""
STREAMS={"stable":[0]*24,"reversal":[0]*8+[1]*16,"recurrence":[0]*8+[1]*8+[0]*8,"alternating":[0,1]*12,"blocks2":[0,0,1,1]*6}
class Markov:
    state_bits=6
    def __init__(self): self.state=5
    def step(self,value):
        s=self.state
        prior=(s>>4)&1
        initialized=(s>>5)&1
        prediction=None if not initialized else int(((s>>(2*prior))&3)>=2)
        if initialized:
            shift=2*prior
            count=(s>>shift)&3
            count=min(3,count+1) if value else max(0,count-1)
            s=(s&~(3<<shift))|(count<<shift)
        self.state=(s&15)|(value<<4)|32
        assert 0<=self.state<64
        return prediction
class Recent:
    state_bits=7
    def __init__(self): self.state=0
    def step(self,value):
        n=(self.state>>4)&7
        previous=self.state&15
        ones=(previous&((1<<n)-1)).bit_count()
        prediction=None if not n or ones*2==n else int(ones*2>n)
        self.state=(((previous<<1)|value)&15)|(min(4,n+1)<<4)
        assert 0<=self.state<128
        return prediction
def run():
    results={}
    for name,sequence in STREAMS.items():
        results[name]={}
        for cls in (Markov,Recent):
            actor=cls()
            predictions=[actor.step(bit) for bit in sequence]
            results[name][cls.__name__]={"correct":sum(a==b for a,b in zip(predictions,sequence)),"total":24,"state_bits":cls.state_bits}
    return results
if __name__=="__main__":
    import json
    print(json.dumps(run(),sort_keys=True))
