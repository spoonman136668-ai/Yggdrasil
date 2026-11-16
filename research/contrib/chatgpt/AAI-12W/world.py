"""AAI-12W privileged mechanical recurrent worlds. Never imported by learner.py."""
import hashlib

FIXTURES = ('mechanical:alpha','mechanical:beta')
NOVEL = (150,232,210,108,182,60,202,99,113,121,42,173)
FAMILIAR = ('xor','and','or','xnor')
NEGATIVE = ('parity4','majority4','exactly_two4','xor_and_xor4')
WORLDS = {'novel':NOVEL,'familiar':FAMILIAR,'negative':NEGATIVE}

def digest(*args):
    return hashlib.sha256(('AAI12W|'+'|'.join(map(str,args))).encode('ascii')).digest()

def number(*args):
    return int.from_bytes(digest(*args)[:8],'big')

def guard(fixture,phase,world):
    if fixture not in FIXTURES or phase not in WORLDS or type(world) is not int or not 0 <= world < len(WORLDS[phase]):
        raise PermissionError('AAI12W SCIENTIFIC FIRST USE DISARMED')

def roles(fixture,phase,world):
    guard(fixture,phase,world)
    return tuple(sorted(range(8),key=lambda i:(digest(fixture,phase,world,'role',i),i)))

def effect(fixture,phase,world,x):
    rr=roles(fixture,phase,world)
    if phase=='novel':
        code=4*x[rr[0]]+2*x[rr[1]]+x[rr[2]]
        return (WORLDS[phase][world]>>code)&1
    if phase=='familiar':
        a,b=x[rr[0]],x[rr[1]]
        mode=WORLDS[phase][world]
        return {'xor':a^b,'and':a&b,'or':a|b,'xnor':1^(a^b)}[mode]
    a,b,c,d=(x[i] for i in rr[:4]);mode=WORLDS[phase][world]
    return {'parity4':a^b^c^d,'majority4':int(a+b+c+d>=3),
            'exactly_two4':int(a+b+c+d==2),'xor_and_xor4':(a^b)&(c^d)}[mode]

def output_port(fixture,phase,world):
    return roles(fixture,phase,world)[{'novel':3,'familiar':2,'negative':4}[phase]]

def bits(n):
    return tuple((n>>i)&1 for i in range(8))

def flip(x,i):
    y=list(x);y[i]^=1;return tuple(y)

def true_step(fixture,phase,world,x,y,action):
    k=output_port(fixture,phase,world)
    xx=flip(x,action)
    return xx, y^x[k]^effect(fixture,phase,world,x)^xx[k]

def ranking(fixture,phase,world):
    guard(fixture,phase,world)
    return tuple(sorted(range(256),key=lambda n:(digest(fixture,phase,world,'x',n),n)))

def train(fixture,phase,world):
    choices=ranking(fixture,phase,world)[:48]
    rows=[]
    for n in choices:
        x=bits(n)
        y=digest(fixture,phase,world,'train-y',n)[0]&1
        action=number(fixture,phase,world,'train-action',n)%8
        xx,yy=true_step(fixture,phase,world,x,y,action)
        rows.append({'x':list(x),'y':y,'xnext':list(xx),'ynext':yy,'flipped_index':action})
    assert len(rows)==48 and len(set(tuple(r['x']) for r in rows))==48
    return tuple(rows)

def evaluations(fixture,phase,world):
    train_states=set(ranking(fixture,phase,world)[:48])
    cases=[]
    for n in ranking(fixture,phase,world)[48:]:
        x=bits(n);ys=digest(fixture,phase,world,'eval-y',n)[0]&1
        actions=tuple(number(fixture,phase,world,'eval-action',n,step)%8 for step in range(3))
        path=[x];now=x
        for act in actions:
            now=flip(now,act);path.append(now)
        if any(sum(v<<i for i,v in enumerate(state)) in train_states for state in path[:3]):
            continue
        y=ys;curr=x
        for act in actions:curr,y=true_step(fixture,phase,world,curr,y,act)
        cases.append({'x0':list(x),'y0':ys,'actions':list(actions),'truth_y3':y,
                      'predecessor_path':[list(v) for v in path[:3]]})
        if len(cases)==64:break
    if len(cases)!=64:raise AssertionError('not enough novel heldout predecessor contexts')
    return tuple(cases)
