"""Independent hidden vector equation generator for frozen WSP43."""
import hashlib
import random
from model import NumericModel

def rng_for(tag):return random.Random(int.from_bytes(hashlib.sha256(tag.encode()).digest(),'big'))

class World:
    def __init__(self,width,family,tag):
        self.width=width
        rng=rng_for(tag)
        self.rows=[];self.biases=[];self.nonlinear=[];self.groups=[]
        for action in range(2):
            rows=tuple(tuple(rng.sample(range(width),4)) for _ in range(width))
            bias=rng.getrandbits(width)
            nonlinear=[];used=set()
            count={'eight_nonlinear':8,'sixteen_nonlinear':16,'thirtytwo_nonlinear':32}[family]
            while len(used)<count:
                indices=tuple(sorted(rng.sample(range(width),rng.randint(2,4))))
                if indices in used:continue
                used.add(indices)
                nonlinear.append((indices,rng.randrange(1,1<<width)))
            self.rows.append(rows);self.biases.append(bias);self.nonlinear.append(tuple(nonlinear))
            coefficients={0:bias} if bias else {}
            for output,inputs in enumerate(rows):
                for index in inputs:coefficients[1<<index]=coefficients.get(1<<index,0)^(1<<output)
            for indices,coefficient in nonlinear:coefficients[sum(1<<i for i in indices)]=coefficient
            self.groups.append(tuple(sorted((m,c) for m,c in coefficients.items() if c)))

    def apply(self,action,state):
        # Teacher evaluates independent output equations, never numerical model.
        result=self.biases[action]
        for bit,inputs in enumerate(self.rows[action]):
            parity=0
            for i in inputs:parity^=state>>i&1
            result^=parity<<bit
        for inputs,coefficient in self.nonlinear[action]:
            if all(state>>i&1 for i in inputs):result^=coefficient
        return result

    rollout=NumericModel.rollout

