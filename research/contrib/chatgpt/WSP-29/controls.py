"""Independent symbolic routing and genuinely converged full-batch Adam heads."""
import math
from composition import CONFIGS,context,forward

def symbolic(banks,examples):
    scores=[]
    for index,(a,b,j) in enumerate(CONFIGS):
        out=[]
        for x,y in examples:
            modified=list(x);modified[j]=forward(banks[a],x);out.append(forward(banks[b],tuple(modified)))
        scores.append((sum(p!=y for p,(x,y) in zip(out,examples)),index))
    return CONFIGS[min(scores)[1]]

def symbolic_predict(banks,cfg,x):
    a,b,j=cfg;modified=list(x);modified[j]=forward(banks[a],x)
    return forward(banks[b],tuple(modified))

def feature_table(tables):
    # Inferred source outputs only. No true hidden table/target recipe allowed.
    result=[]
    for i in range(8):
        x=context(i);features=[]
        for a,b,j in CONFIGS:
            address=(i&~(1<<j))|(tables[a][i]<<j);features.append(tables[b][address])
        result.append(tuple(features+[int(k==i) for k in range(8)]))
    return tuple(result)

RAW=tuple(tuple(int(i==j) for j in range(8)) for i in range(8))
def dot(w,x):return sum(a*b for a,b in zip(w,x))
def predict(w,x):return int(round(dot(w,x),12)>=0)
def sigmoid(z):
    if z>=0:return 1/(1+math.exp(-z))
    e=math.exp(z);return e/(1+e)

def trained(examples,width):
    w=[0.]*width;m=[0.]*width;v=[0.]*width
    for iteration in range(4097):
        logits=[dot(w,x) for x,y in examples]
        loss=sum(max(z,0)-z*y+math.log1p(math.exp(-abs(z))) for z,(x,y) in zip(logits,examples))/len(examples)
        if loss<=.01:return w,iteration,loss
        if iteration==4096:raise AssertionError('WSP29_TRAINED_NONCONVERGENCE')
        gradient=[0.]*width
        for z,(x,y) in zip(logits,examples):
            error=(sigmoid(z)-y)/len(examples)
            for j,value in enumerate(x):gradient[j]+=error*value
        t=iteration+1
        for j,g in enumerate(gradient):
            m[j]=.9*m[j]+.1*g;v[j]=.999*v[j]+.001*g*g
            w[j]-=.1*(m[j]/(1-.9**t))/(math.sqrt(v[j]/(1-.999**t))+1e-8)
