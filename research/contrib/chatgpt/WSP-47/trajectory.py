"""Numerical least-visit policy; learning uses unchanged WSP45 machine."""
import random
from frozen_numeric import NumericLearner,ActionModel,step


class TrajectoryAgent(ActionModel):
    def __init__(self,width,policy='numeric'):
        if policy not in ('numeric','random'):raise ValueError('policy')
        super().__init__([NumericLearner(width) for _ in range(2)])
        self.width=width;self.size=1<<width;self.policy=policy
        self.visits=[[0]*self.size for _ in range(2)];self.current=0
        self.rows=[];self.resets=0;self.policy_thresholds=0;self.rng=random.Random(2711+width)

    def choose_action(self):
        x=tuple(self.current>>j&1 for j in range(self.width))
        matches=[step(sum((2*b-1)*v for b,v in zip(address,x))-sum(address)) for address in self.learners[0].addresses]
        counts=[sum(g*w for g,w in zip(matches,row)) for row in self.visits]
        choose0=step(counts[1]-counts[0]);self.policy_thresholds+=self.size+1
        return 1-choose0 if self.policy=='numeric' else self.rng.randrange(2)

    def transition(self,source):
        t=len(self.rows)
        if t and t%64==0:self.current=0;self.resets+=1
        state=self.current;action=self.choose_action();answer=source(action,state)
        self.learners[action].observe(state,answer)
        x=tuple(state>>j&1 for j in range(self.width))
        matches=[step(sum((2*b-1)*v for b,v in zip(address,x))-sum(address)) for address in self.learners[0].addresses]
        self.visits=[[old+g*step(-abs(a-action)) for old,g in zip(row,matches)] for a,row in enumerate(self.visits)]
        self.rows.append((action,state,answer));self.current=answer
        return action,state,answer


class MembershipAgent(ActionModel):
    def __init__(self,width):
        super().__init__([NumericLearner(width) for _ in range(2)]);self.rows=[]
    def transition(self,source):
        action=len(self.rows)%2;state=self.learners[action].choose()
        if state is None:state=0
        answer=source(action,state);self.learners[action].observe(state,answer)
        self.rows.append((action,state,answer));return action,state,answer


class TrainedOneHot(ActionModel):
    def __init__(self,rows):
        self.facts={(a,x):y for a,x,y in rows}
        self.training_errors=sum(self.apply(a,x)!=y for a,x,y in rows)
    def apply(self,action,state):return self.facts.get((action,state),0)
