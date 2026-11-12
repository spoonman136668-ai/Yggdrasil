"""Frozen equation inference with numerical least-visit action selection."""
from equations import EquationBank,BankModel,AdaptiveModel,step

class Observer(AdaptiveModel):
    def __init__(self,width):
        self.width=width;self.size=1<<width;super().__init__([BankModel([EquationBank(width,d) for _ in range(2)]) for d in (1,2,3,'full')])
        self.visits=[[0]*self.size for _ in range(2)];self.state=0;self.steps=0;self.resets=0;self.rows=[]
    def transition(self,source):
        if self.steps and self.steps%64==0:self.state=0;self.resets+=1
        x=self.state;a=step(self.visits[0][x]-self.visits[1][x]-1);y=source(a,x)
        self.visits[a][x]+=1
        for model in self.models:model.banks[a].observe(x,y)
        self.state=y;self.rows.append((a,x,y));self.steps+=1
        return a,x,y
