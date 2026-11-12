"""Programmed numerical factual-graph exploration; fixed WSP47 inference."""
from collections import deque
from equations import EquationBank,BankModel,AdaptiveModel,step

class Agent(AdaptiveModel):
    def __init__(self,width,policy):
        if policy not in ('frontier','least_visit'):raise ValueError('policy')
        self.width=width;self.size=1<<width;self.policy=policy
        super().__init__([BankModel([EquationBank(width,d) for _ in range(2)]) for d in (1,2,3,'full')])
        self.visits=[[0]*self.size for _ in range(2)];self.predecessors=[0]*self.size
        self.state=0;self.steps=0;self.resets=0;self.rows=[];self.wave_rounds=0
    def fallback(self):return step(self.visits[0][self.state]-self.visits[1][self.state]-1)
    def fact(self,a,x):return self.models[-1].banks[a].fact(x)
    def choose(self):
        if self.policy=='least_visit':return self.fallback()
        known=[self.fact(a,self.state)[1] for a in range(2)]
        if not known[0]:return 0
        if not known[1]:return 1
        seen=[self.models[-1].banks[a].seen for a in range(2)]
        wave=((1<<self.size)-1)^(seen[0]&seen[1])
        for _ in range(self.size):
            previous=wave
            for target in range(self.size):wave|=self.predecessors[target]*((previous>>target)&1)
            self.wave_rounds+=1
            if wave>>self.state&1:
                for a in range(2):
                    y,k=self.fact(a,self.state)
                    if k and previous>>y&1:return a
                raise AssertionError('wave without predecessor')
            if wave==previous:break
        return self.fallback()
    def shadow(self):
        """Independent queue/sets reference, only observed transition facts."""
        queue=deque([(self.state,None)]);seen={self.state}
        while queue:
            x,first=queue.popleft()
            for a in range(2):
                _,known=self.fact(a,x)
                if not known:return a if first is None else first
            for a in range(2):
                y,_=self.fact(a,x)
                if y not in seen:seen.add(y);queue.append((y,a if first is None else first))
        return self.fallback()
    def transition(self,source):
        if self.steps and self.steps%64==0:self.state=0;self.resets+=1
        a=self.choose()
        if self.policy=='frontier':assert a==self.shadow(),'SHADOW_ACTION_PARITY'
        x=self.state;y=source(a,x)
        self.visits[a][x]+=1;self.predecessors[y]|=1<<x
        for model in self.models:model.banks[a].observe(x,y)
        self.rows.append((a,x,y));self.steps+=1;self.state=y
        return a,x,y
