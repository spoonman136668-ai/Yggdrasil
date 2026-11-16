"""AAI-12X privileged synthetic source. Learners must never import this module."""
import hashlib

FIXTURES = ('mechanical:gamma', 'mechanical:delta', 'mechanical:epsilon')
PREVIOUS_MASKS = frozenset((150, 232, 210, 108, 182, 60, 202, 99, 113, 121, 42, 173))
FAMILIAR = ('xor', 'and', 'or', 'xnor')
NEGATIVE = ('parity4', 'majority4', 'exactly_two4', 'xor_and_xor4')

def digest(*args):
    return hashlib.sha256(('AAI12X|'+'|'.join(map(str,args))).encode('ascii')).digest()

def number(*args):
    return int.from_bytes(digest(*args)[:8], 'big')

def essential(mask):
    return all(any(((mask >> code)&1) != ((mask >> (code ^ (1<<bit)))&1)
                   for code in range(8)) for bit in range(3))

NOVEL = tuple(m for m in sorted(range(256), key=lambda m:(digest('novel-mask',m),m))
              if essential(m) and m not in PREVIOUS_MASKS)[:16]
WORLDS = {'novel': NOVEL, 'familiar': FAMILIAR, 'negative': NEGATIVE}

def guard(fixture, phase, wid):
    if fixture not in FIXTURES or phase not in WORLDS or type(wid) is not int or not 0 <= wid < len(WORLDS[phase]):
        raise PermissionError('AAI12X SCIENTIFIC FIRST USE DISARMED')

def roles(fixture, phase, wid):
    guard(fixture,phase,wid)
    return tuple(sorted(range(8),key=lambda i:(digest(fixture,phase,wid,'role',i),i)))

def function(fixture,phase,wid,x):
    rr = roles(fixture,phase,wid)
    if phase == 'novel':
        a,b,c = (x[i] for i in rr[:3])
        return (WORLDS[phase][wid] >> (4*a+2*b+c))&1
    if phase == 'familiar':
        a,b = (x[i] for i in rr[:2]); mode=WORLDS[phase][wid]
        return {'xor':a^b,'and':a&b,'or':a|b,'xnor':1^(a^b)}[mode]
    a,b,c,d = (x[i] for i in rr[:4]); mode = WORLDS[phase][wid]
    return {'parity4':a^b^c^d,'majority4':int(a+b+c+d>=3),
            'exactly_two4':int(a+b+c+d==2),'xor_and_xor4':(a^b)&(c^d)}[mode]

def k_port(fixture,phase,wid):
    return roles(fixture,phase,wid)[{'novel':3,'familiar':2,'negative':4}[phase]]

def bits(n):
    return tuple((n>>i)&1 for i in range(8))

def flip(x,i):
    y=list(x);y[i]^=1;return tuple(y)

def true_step(fixture,phase,wid,x,y,action):
    k=k_port(fixture,phase,wid)
    xx=flip(x,action)
    return xx,y^x[k]^function(fixture,phase,wid,x)^xx[k]

def ranking(fixture,phase,wid):
    guard(fixture,phase,wid)
    return tuple(sorted(range(256),key=lambda n:(digest(fixture,phase,wid,'x',n),n)))

def train(fixture,phase,wid):
    chosen=ranking(fixture,phase,wid)[:48]
    rows=[]
    for n in chosen:
        x=bits(n)
        y=digest(fixture,phase,wid,'train-y',n)[0]&1
        action=number(fixture,phase,wid,'train-action',n)%8
        xx,yy=true_step(fixture,phase,wid,x,y,action)
        rows.append({'x':list(x),'y':y,'xnext':list(xx),'ynext':yy,'flipped_index':action})
    assert len(rows)==48 and len({tuple(r['x']) for r in rows})==48
    return tuple(rows)

def evaluations(fixture,phase,wid):
    train_states=set(ranking(fixture,phase,wid)[:48])
    trials=[]
    for n in ranking(fixture,phase,wid)[48:]:
        x=bits(n); y0=digest(fixture,phase,wid,'eval-y',n)[0]&1
        actions=tuple(number(fixture,phase,wid,'eval-action',n,s)%8 for s in range(3))
        curr=x;path=[]
        for action in actions:
            path.append(curr)
            curr=flip(curr,action)
        if any(sum(v<<i for i,v in enumerate(state)) in train_states for state in path):
            continue
        y=y0;curr=x
        for action in actions:curr,y=true_step(fixture,phase,wid,curr,y,action)
        trials.append({'x0':list(x),'y0':y0,'actions':list(actions),'truth_y3':y,
                       'predecessor_path':[list(v) for v in path]})
        if len(trials)==64:break
    if len(trials)!=64:raise AssertionError('AAI12X INVALID: insufficient disjoint heldouts')
    return tuple(trials)
