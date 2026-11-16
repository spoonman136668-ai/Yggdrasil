"""AAI-12W tokenless learner + fully fitted recurrent controls; public fields only."""
from __future__ import annotations
import hashlib
import itertools
import json
import math

METHODS=('ternary_causal','fixed_pair_relation_grammar','fully_fitted_id3_depth7',
         'logistic_degree2_fullbatch200','hamming_knn5','persistence_no_memory')
GATES=('xor','and','or','nand','nor','xnor')
PAIRS=tuple(itertools.combinations(range(17),2))
NF=1+17+len(PAIRS)
assert NF==154
PUBLIC={'x','y','xnext','ynext','flipped_index'}

def check(row):
    if type(row)!=dict or set(row)!=PUBLIC:raise ValueError('private or missing public fields')
    x=row['x'];nextx=row['xnext'];act=row['flipped_index'];y=row['y'];yn=row['ynext']
    if (type(x)!=list or type(nextx)!=list or len(x)!=8 or len(nextx)!=8
        or any(type(v)!=int or v not in (0,1) for v in (*x,*nextx))
        or type(act)!=int or not 0<=act<8 or type(y)!=int or y not in (0,1)
        or type(yn)!=int or yn not in (0,1) or sum(a!=b for a,b in zip(x,nextx))!=1
        or x[act]==nextx[act] or any(x[i]!=nextx[i] for i in range(8) if i!=act)):
        raise ValueError('public real do event invalid')
    return tuple(x),tuple(nextx)

def target(row,k):
    x,xx=check(row)
    return row['y']^row['ynext']^x[k]^xx[k]

def code(x,abc):
    return 4*x[abc[0]]+2*x[abc[1]]+x[abc[2]]

def fit_ternary(rows):
    choices=[]
    for k in range(8):
        residual=[target(r,k) for r in rows]
        for abc in itertools.permutations((i for i in range(8) if i!=k),3):
            n0=[0]*8;n1=[0]*8
            for r,value in zip(rows,residual):
                u=code(r['x'],abc)
                if value:n1[u]+=1
                else:n0[u]+=1
            mask=sum(int(n1[i]>n0[i])<<i for i in range(8))
            errors=sum(min(n0[i],n1[i]) for i in range(8))
            covered=sum((n0[i]+n1[i])>0 for i in range(8))
            choices.append((errors,-covered,k,*abc,mask))
    _,_,k,a,b,c,mask=min(choices)
    return {'k':k,'abc':[a,b,c],'mask':mask}

def op(tag,a,b):
    if tag=='xor':return a^b
    if tag=='and':return a&b
    if tag=='or':return a|b
    if tag=='nand':return 1-(a&b)
    if tag=='nor':return 1-(a|b)
    if tag=='xnor':return 1-(a^b)
    raise ValueError('unregistered fixed operation')

def fit_pair(rows):
    best=None
    for k in range(8):
        targets=[target(r,k) for r in rows]
        for a,b in itertools.permutations((v for v in range(8) if v!=k),2):
            for tag in GATES:
                error=sum(op(tag,r['x'][a],r['x'][b])!=t for r,t in zip(rows,targets))
                item=(error,k,a,b,GATES.index(tag))
                if best is None or item<best:best=item
    _,k,a,b,i=best
    return {'k':k,'a':a,'b':b,'op':GATES[i]}

def features(x,nextx,y):
    return tuple(x)+tuple(nextx)+(y,)

def nonzero(t):
    active=[i for i,v in enumerate(t) if v]
    active_set=set(active)
    return (0,*(i+1 for i in active),*(18+j for j,(a,b) in enumerate(PAIRS) if a in active_set and b in active_set))

def fit_logistic(rows):
    corpus=[(nonzero(features(*check(r),r['y'])),r['ynext']) for r in rows]
    weights=[0.]*NF
    for epoch in range(200):
        grad=[0.]*NF
        for positions,y in corpus:
            z=sum(weights[i] for i in positions)
            p=1./(1.+math.exp(-max(-30.,min(30.,z))))
            residual=p-y
            for i in positions:grad[i]+=residual
        for i in range(NF):weights[i]-=.4*(grad[i]/len(corpus)+(.01*weights[i] if i else 0.))
    return {'weights':weights}

def entropy(values):
    if not values:return 0.
    p=sum(values)/len(values)
    return 0. if p in (0.,1.) else -p*math.log2(p)-(1.-p)*math.log2(1.-p)

def id3(data,remaining,depth):
    if not data:return ['leaf',0]
    labs=[y for _,y in data]
    if depth==0 or not remaining or entropy(labs)==0:
        return ['leaf',int(2*sum(labs)>=len(labs))]
    base=entropy(labs);best=None
    for col in remaining:
        left=[r for r in data if r[0][col]==0]
        right=[r for r in data if r[0][col]==1]
        if not left or not right:continue
        gain=base-(len(left)*entropy([y for _,y in left])+len(right)*entropy([y for _,y in right]))/len(data)
        if best is None or gain>best[0]+1e-12:best=(gain,col,left,right)
    if best is None:return ['leaf',int(2*sum(labs)>=len(labs))]
    _,col,lft,rgt=best
    rem=tuple(i for i in remaining if i!=col)
    return ['branch',col,id3(lft,rem,depth-1),id3(rgt,rem,depth-1)]

def train(name,rows):
    if name not in METHODS or type(rows) not in (tuple,list) or len(rows)!=48:
        raise ValueError('wrong method or fixed training count')
    for row in rows:check(row)
    if name=='ternary_causal':model=fit_ternary(rows)
    elif name=='fixed_pair_relation_grammar':model=fit_pair(rows)
    elif name=='fully_fitted_id3_depth7':model={'tree':id3([(features(*check(r),r['y']),r['ynext']) for r in rows],tuple(range(17)),7)}
    elif name=='logistic_degree2_fullbatch200':model=fit_logistic(rows)
    elif name=='hamming_knn5':model={'rows':list(rows)}
    else:model={}
    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'schema':'aai12w.cold.v1','name':name,'model':model,'training_sha256':digest}

def canonical(state):return json.dumps(state,sort_keys=True,separators=(',',':'),allow_nan=False)

def checkpoint(state):
    raw=canonical(state)
    return canonical({'state':state,'sha256':hashlib.sha256(raw.encode()).hexdigest()})

def restore(snapshot):
    env=json.loads(snapshot)
    if type(env)!=dict or set(env)!={'state','sha256'} or canonical(env)!=snapshot:raise ValueError('bad cold envelope')
    state=env['state']
    if hashlib.sha256(canonical(state).encode()).hexdigest()!=env['sha256']:
        raise ValueError('cold model tampering')
    if state['schema']!='aai12w.cold.v1' or state['name'] not in METHODS or type(state['model'])!=dict or len(state['training_sha256'])!=64:
        raise ValueError('bad cold model')
    return state

def predict_step(state,x,y,action):
    name=state['name'];m=state['model']
    if len(x)!=8 or type(y)!=int or y not in (0,1) or type(action)!=int or not 0<=action<8:
        raise ValueError('bad prediction input')
    nextx=list(x);nextx[action]^=1
    if name=='ternary_causal':
        k=m['k'];u=code(x,m['abc']);n=y^x[k]^((m['mask']>>u)&1)^nextx[k]
    elif name=='fixed_pair_relation_grammar':
        k=m['k'];n=y^x[k]^op(m['op'],x[m['a']],x[m['b']])^nextx[k]
    elif name=='fully_fitted_id3_depth7':
        t=features(x,nextx,y);node=m['tree']
        while node[0]=='branch':node=node[2+t[node[1]]]
        n=node[1]
    elif name=='logistic_degree2_fullbatch200':
        ps=nonzero(features(x,nextx,y));n=int(sum(m['weights'][j] for j in ps)>=0.)
    elif name=='hamming_knn5':
        t=features(x,nextx,y)
        near=sorted(enumerate(m['rows']),key=lambda item:(sum(a!=b for a,b in zip(t,features(item[1]['x'],item[1]['xnext'],item[1]['y']))),item[0]))[:5]
        n=int(sum(z['ynext'] for _,z in near)>=3)
    else:n=y
    return tuple(nextx),n

def forecast(state,x,y,actions):
    if len(actions)!=3:raise ValueError('three real interventions required')
    now=tuple(x)
    for action in actions:now,y=predict_step(state,now,y,action)
    return y
