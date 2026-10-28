"""Independent conventional factorized and exact-pattern controls.

The factorized control has access to exactly the same public pair-feedback
and final outcomes as the interacting local-cell candidate. It does not
import or share the candidate's learning implementation.
"""
from itertools import product

class ConventionalFactorized:
    def __init__(self):
        self.pairs=({}, {})
        self.final={}
        self.observations=0

    def observe_pair(self,index,pair,outcome):
        records=self.pairs[index]
        bucket=records.setdefault(pair,[0,0])
        bucket[int(outcome)]+=1
        self.observations+=1

    def pair_message(self,index,pair):
        values=self.pairs[index].get(pair)
        if values is None or sum(values)<2 or values[0]==values[1]:
            return None
        return values[1]>values[0]

    def observe_final(self,bits,outcome):
        message=self.messages(bits)
        if None in message:raise ValueError("UNKNOWN_PUBLIC_SUBCAUSE")
        counts=self.final.setdefault(message,[0,0])
        counts[int(outcome)]+=1
        self.observations+=1

    def messages(self,bits):
        return (self.pair_message(0,bits[:2]),self.pair_message(1,bits[2:]))

    def predict(self,bits):
        message=self.messages(bits)
        if None in message:return None
        examples=[(a,b,counts[1]>counts[0]) for (a,b),counts in self.final.items()
                  if sum(counts)>=2 and counts[0]!=counts[1]]
        solutions=[]
        for bias,x,y in product((False,True),repeat=3):
            if all((bias ^ (x and a) ^ (y and b))==outcome for a,b,outcome in examples):
                solutions.append((bias,x,y))
        if len(solutions)!=1:return None
        bias,x,y=solutions[0]
        return bool(bias ^ (x and message[0]) ^ (y and message[1]))

class ConventionalExactTable:
    def __init__(self):
        self.values={}
        self.observations=0

    def observe_final(self,bits,outcome):
        bucket=self.values.setdefault(bits,[0,0])
        bucket[int(outcome)]+=1
        self.observations+=1

    def predict(self,bits):
        bucket=self.values.get(bits)
        if bucket is None or sum(bucket)<2 or bucket[0]==bucket[1]:
            return None
        return bucket[1]>bucket[0]
