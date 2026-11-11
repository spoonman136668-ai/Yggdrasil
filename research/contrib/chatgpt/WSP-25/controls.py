"""Independent observed parent table and genuinely optimized one-hot logits."""
import math

def symbolic(events):
    table={}
    for u,x,y,z,mask in events:
        if (x,y) in table and table[x,y]!=z:raise ValueError('contradictory training data')
        table[x,y]=z
    return table

def trained(events):
    weights=[0.]*4;m=[0.]*4;v=[0.]*4
    for iteration in range(2049):
        loss=sum(max(weights[2*x+y],0)-weights[2*x+y]*z+math.log1p(math.exp(-abs(weights[2*x+y]))) for u,x,y,z,mask in events)/len(events)
        if loss<=.01:return weights,iteration,loss
        if iteration==2048:raise AssertionError('WSP25_TRAINED_NONCONVERGENCE')
        gradient=[0.]*4
        for u,x,y,z,mask in events:
            j=2*x+y;gradient[j]+=(1/(1+math.exp(-weights[j]))-z)/len(events)
        t=iteration+1
        for j,g in enumerate(gradient):
            m[j]=.9*m[j]+.1*g;v[j]=.999*v[j]+.001*g*g
            weights[j]-=.1*(m[j]/(1-.9**t))/(math.sqrt(v[j]/(1-.999**t))+1e-8)
