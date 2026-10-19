"""T16B Yggdrasil node-dictionary edge-arena, NOT a fragment pool.

Reuses exact 24-bit IDs once per retained connected set, edges carry two
5-bit dictionary indices and two role bits (12 bits in 2 bytes). Persistent
state is a <=144-byte immutable bytestring including all 20 TRAIN-only
int8 coefficients and 4 byte counters. Public-only single pass; never reads
future OPEN queries or source truth.

Python object heap and scratch are NOT bounded by 144B. Original source
identifiers are never instantiated by this module.
"""
HEADER=2
WEIGHT_BYTES=20
COUNTER_BYTES=4
TOTAL=144
ARENA=TOTAL-WEIGHT_BYTES-COUNTER_BYTES
MAX_NODES=32

def pack_edges(edges):
    """Fixed lossless 24-bit ID dictionary, 2-byte indexed typed edges."""
    ids=[];positions={}
    for a,role,b in edges:
        assert 0<=a<1<<24 and 0<=b<1<<24 and 0<=role<4
        for node in (a,b):
            if node not in positions:
                positions[node]=len(ids)
                ids.append(node)
    if len(ids)>MAX_NODES or len(edges)>255:
        return None
    blob=bytes((len(ids),len(edges)))
    blob+=b"".join(z.to_bytes(3,"big") for z in ids)
    for a,role,b in edges:
        blob+=((positions[a]<<7)|(positions[b]<<2)|role).to_bytes(2,"big")
    if len(blob)>ARENA:
        return None
    return blob

def unpack_edges(blob):
    assert type(blob) is bytes and len(blob)<=ARENA and len(blob)>=HEADER
    n,e=blob[:2]
    assert n<=MAX_NODES and len(blob)==HEADER+3*n+2*e
    ids=[int.from_bytes(blob[HEADER+3*j:HEADER+3*j+3],"big") for j in range(n)]
    assert len(set(ids))==n
    offset=HEADER+3*n
    records=[]
    for j in range(e):
        v=int.from_bytes(blob[offset+2*j:offset+2*j+2],"big")
        assert v<1<<12
        a,b,role=(v>>7)&31,(v>>2)&31,v&3
        assert a<n and b<n
        records.append((ids[a],role,ids[b]))
    assert pack_edges(records)==blob
    return tuple(records)

def initial_state(coeff=None):
    if coeff is None:coeff=bytes(WEIGHT_BYTES)
    assert type(coeff) is bytes and len(coeff)==WEIGHT_BYTES
    state=coeff+bytes(COUNTER_BYTES)+bytes((0,0))
    assert len(state)==26
    return state

def unpack_state(state):
    assert type(state) is bytes and len(state)<=TOTAL and len(state)>=26
    coeff=state[:WEIGHT_BYTES]
    count,evicted,joins,reserved=state[WEIGHT_BYTES:WEIGHT_BYTES+COUNTER_BYTES]
    records=unpack_edges(state[WEIGHT_BYTES+COUNTER_BYTES:])
    return coeff,(count,evicted,joins,reserved),records

def feature(a,role,b,edges):
    """No private target, no future query; public junction and direction."""
    inbound=sum(x[2]==a for x in edges)
    outbound=sum(x[0]==b for x in edges)
    return (int(inbound>0),int(outbound>0),int(inbound>1),
            int(outbound>1),int(a==b),int(role%2==0))

def score(edge,others,weights):
    a,role,b=edge
    features=feature(a,role,b,others)
    # Distinct edge representation; TRAIN-learned weights affect only
    # information-value retention, never fabricate a causal relation.
    return (sum(w*f for w,f in zip(weights[0:6],features))
            +weights[6+role]+2*sum(f[:2] for f in [features])
            +sum(x[2]==a or x[0]==b for x in others))

def observe(state,event):
    weights,counters,old=unpack_state(state)
    assert len(old)<=60
    a,role,b=event
    assert 0<=a<1<<24 and 0<=b<1<<24 and 0<=role<4
    rows=list(old)
    if event not in rows:rows.append(event)
    removed=0
    while True:
        encoded=pack_edges(rows)
        if encoded is not None:break
        assert rows
        victim=min(range(len(rows)),key=lambda i:(
            score(rows[i],rows[:i]+rows[i+1:],weights),i))
        rows.pop(victim)
        removed+=1
    count,evicted,joins,reserved=counters
    count=(count+1)&255
    evicted=(evicted+removed)&255
    joins=(joins+sum(x[2]==a or x[0]==b for x in old))&255
    new=weights+bytes((count,evicted,joins,reserved))+encoded
    assert len(new)<=TOTAL
    assert unpack_state(new)[2]==tuple(rows)
    return new

def train_coeff(train_examples):
    """TRAIN examples: (public 72-event stream, TRAIN-only delayed labels).
    Delayed labels may be derived from TRAIN after-stream query resolution;
    they are forbidden at OPEN execution. Exactly twenty signed int8 units.
    """
    weights=[0]*WEIGHT_BYTES
    updates=0
    for events,credited_public_edges in train_examples:
        seen=[]
        assert set(credited_public_edges).issubset(set(events))
        for a,role,b in events:
            feat=feature(a,role,b,seen)
            target=1 if (a,role,b) in credited_public_edges else -1
            x=feat+(int(role==0),int(role==1),int(role==2),int(role==3))
            margin=sum(weights[j]*v for j,v in enumerate(x))
            if target*margin<=0:
                for j,v in enumerate(x):
                    weights[j]=max(-127,min(127,weights[j]+target*v))
                updates+=1
            seen.append((a,role,b))
    return bytes(w&255 for w in weights),updates

def solve(state,question):
    """Return a destination only for a unique graph-reachable typed path."""
    _,_,edges=unpack_state(state)
    op=tuple(role for role,direction in question["ops"])
    assert all(direction==1 for role,direction in question["ops"])
    nodes={question["start"]}
    for role in op:
        nxt=set()
        for a,r,b in edges:
            if r==role and a in nodes:nxt.add(b)
        nodes=nxt
        if not nodes:return None
    return next(iter(nodes)) if len(nodes)==1 else None
