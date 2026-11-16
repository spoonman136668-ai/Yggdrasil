"""AAI-12V source-only fixed Boolean causal worlds. PRIVILEGED: never imported by the learner."""
import hashlib
from itertools import product

FIXTURES=("mechanical:alpha","mechanical:beta")
PORTS={"donor":(0,1,2,3),"interference":(2,4,5,1),"receiver":(1,3,6,0)}
GROUPS=(
 ("reuse",232,150,232),("reuse",104,95,104),("reuse",202,41,202),("reuse",41,212,41),
 ("reuse",23,75,23),("reuse",113,166,113),("reuse",107,194,107),("reuse",75,23,75),
 ("changed",23,150,212),("changed",113,95,75),("changed",104,41,202),("changed",232,23,107),
 ("novel",232,150,53),("novel",104,95,194),("novel",202,41,166),("novel",41,212,107),
 ("familiar",150,232,150),("familiar",95,104,95),("familiar",212,41,212),("familiar",194,107,194),
)
def digest(*fields):
    return hashlib.sha256(("AAI12V|"+"|".join(map(str,fields))).encode("ascii")).digest()
def identity(fix,group,phase):
    if fix not in FIXTURES or type(group)!=int or not 0<=group<len(GROUPS) or phase not in PORTS:
        raise PermissionError("AAI12V SCIENTIFIC FIRST USE DISARMED")
def truth(mask,port,x):
    a,b,c,f=port
    return ((mask>>(4*x[a]+2*x[b]+x[c]))&1)^x[f]
def make_pair(fix,group,phase,code):
    identity(fix,group,phase)
    if type(code)!=int or not 0<=code<8:raise ValueError("unknown source code")
    ports=PORTS[phase]
    mask=GROUPS[group][{"donor":1,"interference":2,"receiver":3}[phase]]
    free=tuple(i for i in range(8) if i not in ports)
    ctx=int.from_bytes(digest(fix,group,phase,code)[:8],"big")%8
    x=[0]*8
    for i,bit in enumerate(free):x[bit]=(ctx>>i)&1
    for i,bit in zip(ports[:3],((code>>2)&1,(code>>1)&1,code&1)):x[i]=bit
    x[ports[3]]=0
    y=x.copy();y[ports[3]]=1
    def row(z,step):return {"x":z,"y":truth(mask,ports,z),"ports":list(ports),"do_step":step}
    return (row(x,0),row(y,1))
def initial_codes(fix,group):
    identity(fix,group,"receiver")
    return tuple(sorted(range(8),key=lambda c:(digest(fix,group,"receiver_code",c),c))[:2])
def train_rows(fix,group,phase):
    identity(fix,group,phase)
    codes=initial_codes(fix,group) if phase=="receiver" else range(8)
    return tuple(r for code in codes for r in make_pair(fix,group,phase,code))
def heldout(fix,group):
    identity(fix,group,"receiver")
    ports=PORTS["receiver"];mask=GROUPS[group][3]
    free=tuple(i for i in range(8) if i not in ports)
    tests=[]
    for code,ctx,fvalue in product(range(8),range(8,16),(0,1)):
        x=[0]*8
        for i,bit in enumerate(free):x[bit]=(ctx>>i)&1
        for i,bit in zip(ports[:3],((code>>2)&1,(code>>1)&1,code&1)):x[i]=bit
        x[ports[3]]=fvalue
        tests.append((tuple(x),truth(mask,ports,x)))
    assert len(tests)==128
    return tuple(tests)
