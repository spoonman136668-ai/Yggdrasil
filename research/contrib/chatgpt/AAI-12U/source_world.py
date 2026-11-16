"""Privileged fixed mechanical source; never import from learners.py."""
from __future__ import annotations
import hashlib

FIXTURES=('mechanical:alpha','mechanical:beta')
PORTS={'donor':(0,1,2,3),'interference':(2,4,5,1),'recipient':(1,3,5,0)}
GROUPS=(
    ('reuse',232,150,232),('reuse',104,95,104),
    ('reuse',202,41,202),('reuse',41,212,41),
    ('changed',23,150,212),('changed',113,95,75),
    ('familiar',150,232,150),('familiar',95,104,95),
)

def digest_int(*parts):
    return int.from_bytes(hashlib.sha256(('AAI12U|'+'|'.join(str(p) for p in parts)).encode('ascii')).digest()[:8],'big')

def function(mask,ports,x):
    a,b,c,f=ports
    code=4*x[a]+2*x[b]+x[c]
    return ((mask>>code)&1)^x[f]

def pair(mask,ports,code,fixture,group,phase):
    assert fixture in FIXTURES and 0<=group<8 and phase in PORTS and 0<=code<8 and 0<=mask<256
    basis=digest_int(fixture,group,phase,code,'baseline')
    x=[(basis>>i)&1 for i in range(6)]
    a,b,c,f=ports
    x[a]=(code>>2)&1;x[b]=(code>>1)&1;x[c]=code&1
    before=list(x)
    after=list(x);after[f]=1-after[f]
    def row(arr,edge):
        return {'x':arr,'y':function(mask,ports,arr),'ports':list(ports),'edge':edge}
    return row(before,0),row(after,1)

def source_rows(fixture,group,phase):
    assert fixture in FIXTURES and 0<=group<8 and phase in PORTS
    _,donor,interference,recipient=GROUPS[group]
    mask={'donor':donor,'interference':interference,'recipient':recipient}[phase]
    ports=PORTS[phase]
    codes=range(8) if phase!='recipient' else sorted(range(8),key=lambda c:(digest_int(fixture,group,c,'code'),c))[:2]
    rows=tuple(row for c in codes for row in pair(mask,ports,c,fixture,group,phase))
    assert len(rows)==(4 if phase=='recipient' else 16)
    assert all(sum(v!=w for v,w in zip(a['x'],b['x']))==1 and a['y']^b['y']==1
               for a,b in zip(rows[::2],rows[1::2]))
    return rows

def withheld(fixture,group):
    seen={tuple(r['x']) for r in source_rows(fixture,group,'recipient')}
    assert len(seen)==4
    ports=PORTS['recipient'];truth=GROUPS[group][3]
    return tuple((tuple((n>>i)&1 for i in range(6)), function(truth,ports,tuple((n>>i)&1 for i in range(6))))
                 for n in range(64) if tuple((n>>i)&1 for i in range(6)) not in seen)

