"""Independent symbolic and genuinely gradient-trained matched-prior controls."""
import math
from knowledge import ACTIONS,PRIOR,event_checked,features_for


def symbolic_event(h,action):
    u,mask,value=action
    by,uy,xy,bz,xz,yz=((h>>j)&1 for j in range(6))
    x=value if mask==1 else u
    y=value if mask==2 else by^(uy&u)^(xy&x)
    z=bz^(xz&x)^(yz&y)
    return u,x,y,z,mask


class SymbolicKnowledge:
    def __init__(self):self.possible=set(range(64));self.used=set()
    def observe(self,event):
        u,x,y,z,mask=event_checked(event)
        kept=set()
        for h in self.possible:
            by,uy,xy,bz,xz,yz=((h>>j)&1 for j in range(6))
            py=y if mask&2 else by^(uy&u)^(xy&x)
            pz=bz^(xz&x)^(yz&y)
            if py==y and pz==z:kept.add(h)
        self.possible=kept
        if mask in (1,2):self.used.add((u,mask,x if mask==1 else y))
    def choose(self):
        if len(self.possible)<=1:return None
        choices=[];n=len(self.possible)
        for i,a in enumerate(ACTIONS):
            if a in self.used:continue
            counts={}
            for h in self.possible:
                e=symbolic_event(h,a);out=e[2],e[3];counts[out]=counts.get(out,0)+1
            score=sum(c*(n-c) for c in counts.values());choices.append((score,-i,a))
        return max(choices)[2] if choices else None
    def joint(self,u,x,y):
        possible={((h>>3)&1)^(((h>>4)&1)&x)^(((h>>5)&1)&y) for h in self.possible}
        return next(iter(possible)) if len(possible)==1 else None


def train_bucket(examples):
    """8-logit mixture of affine experts, direct outcome likelihood Adam."""
    theta=[0.]*8;first=[0.]*8;second=[0.]*8
    outputs=[[((sum(a*b for a,b in zip(h,x)))%2) for h in PRIOR] for x,y in examples]
    for step in range(1,4097):
        largest=max(theta);exps=[math.exp(t-largest) for t in theta];normal=sum(exps)
        probs=[t/normal for t in exps];gradient=[0.]*8;loss=0.
        for (x,y),votes in zip(examples,outputs):
            p=sum(w*v for w,v in zip(probs,votes));p=max(1e-12,min(1-1e-12,p))
            loss-=((math.log(p) if y else math.log1p(-p))/len(examples))
            error=(p-y)/(p*(1-p)*len(examples))
            for j in range(8):gradient[j]+=error*probs[j]*(votes[j]-p)
        if loss<=.01:return probs,step-1,loss
        for j,g in enumerate(gradient):
            first[j]=.9*first[j]+.1*g;second[j]=.999*second[j]+.001*g*g
            theta[j]-=.1*(first[j]/(1-.9**step))/(math.sqrt(second[j]/(1-.999**step))+1e-8)
    return probs,4096,loss


def trained_control(events):
    examples=[[],[]]
    for event in events:
        for j,(x,y,gate) in enumerate(features_for(event)):
            if gate:examples[j].append((x,y))
    fitted=[train_bucket(e) for e in examples]
    if any(loss>.01 or steps>4096 for p,steps,loss in fitted):raise AssertionError('WSP24_TRAINED_BASELINE_NOT_CONVERGED')
    return fitted


def trained_joint(fitted,x,y):
    p=sum(prob*((h[0]+h[1]*x+h[2]*y)%2) for prob,h in zip(fitted[1][0],PRIOR))
    return 1 if p>=.95 else 0 if p<=.05 else None
