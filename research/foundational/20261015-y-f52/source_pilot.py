"""Y-F52 genuine bounded online relation chunking; synthetic TRAIN only.

Retention receives public events and currently retained 12-byte records. It
cannot see future queries or core labels. A training-stage supervised ranking
model learns FIT-only utility. A record represents up to six composed directed
role operations with 32-bit endpoints and 18-bit operator code, exactly 12
serialized payload bytes including the length/decoder tag. Python process
memory and diagnostic audit rows are NOT native 576-byte residency evidence.
"""
from __future__ import annotations
import json,math,random,struct
from collections import Counter

FIT=range(551000,551016)
DIAG=range(551100,551116)
FIT_FAM=(960,961,962,963)
DIAG_FAM=(964,965,966,967)
RESERVED=range(552000,552016)
LIMIT=12
EVENTS=72
ARMS=("learned_relation_chunking","fixed_public_greedy_pair_chunks",
      "fixed_public_greedy_triple_chunks","raw_degree_priority",
      "raw_connected_component","raw_FIFO","public_hash",
      "private_future_question_oracle_unfair")
DIMS=7

def source(seed,fam):
    if not ((seed in FIT and fam in FIT_FAM) or
            (seed in DIAG and fam in DIAG_FAM)):
        raise ValueError("unregistered FIT, diagnostic or protected original")
    rng=random.Random(seed*19073+fam*3179+52031)
    occupied=set()
    def node():
        while True:
            n=rng.randrange(1000,1500000000)
            if n not in occupied:occupied.add(n);return n
    ev=[];paths=[]
    for k in range(4):
        start=cur=node();ops=[];members=[]
        for j in range(6):
            nxt=node();r=rng.randrange(4);d=1 if rng.random()<.5 else -1
            raw=(cur,r,nxt) if d==1 else (nxt,r,cur)
            ev.append(raw);ops.append((r,d));members.append(raw);cur=nxt
        paths.append(dict(start=start,answer=cur,ops=tuple(ops),edges=tuple(members)))
    if fam in FIT_FAM:
        for k in range(24):
            a,b,c=node(),node(),node()
            ev.extend(((a,rng.randrange(4),b),(b,rng.randrange(4),c)))
    else:
        for k in range(12):
            a,b,c=node(),node(),node()
            ev.extend(((a,rng.randrange(4),b),(b,rng.randrange(4),c),
                       (c,rng.randrange(4),a)))
        for k in range(6):
            a,b,c=node(),node(),node()
            ev.extend(((a,rng.randrange(4),b),(b,rng.randrange(4),c)))
    assert len(ev)==EVENTS
    rng.shuffle(ev)
    query=paths[rng.randrange(4)]
    length=6 if fam%2 else 4
    # Shorter future questions require exact reachable intermediate endpoint.
    if length==4:
        at=query["start"]
        for r,d in query["ops"][:4]:
            found=[(a,b,c) for a,b,c in query["edges"]
                   if b==r and (a if d==1 else c)==at]
            assert len(found)==1
            a,b,c=found[0];at=c if d==1 else a
        goal=at
    else:goal=query["answer"]
    future=dict(start=query["start"],ops=query["ops"][:length],answer=goal)
    return tuple(ev),future,tuple(paths)

def pack(start,end,codes):
    if not 1<=len(codes)<=6:raise ValueError("invalid chunk length")
    if not (0<=start<2**32 and 0<=end<2**32):raise ValueError("node overflow")
    val=0
    for i,code in enumerate(codes):
        if not 0<=code<=7:raise ValueError("invalid coded role")
        val|=(code<<(3*i))
    return struct.pack("<II",start,end)+val.to_bytes(3,"little")+bytes([len(codes)])

def unpack(payload):
    if len(payload)!=12:raise ValueError("incorrect persistent payload size")
    start,end=struct.unpack("<II",payload[:8])
    val=int.from_bytes(payload[8:11],"little")
    n=payload[11]
    if not 1<=n<=6 or val>>(3*n):raise ValueError("invalid record/decoder")
    codes=tuple((val>>(3*i))&7 for i in range(n))
    return (start,end,codes)

def edge_record(edge):
    a,r,b=edge
    return (a,b,(2*r,))

def mirrored(record):
    a,b,codes=record
    return (b,a,tuple(code^1 for code in reversed(codes)))

def join(a,b):
    if a[1]!=b[0] or len(a[2])+len(b[2])>6:return None
    return (a[0],b[1],a[2]+b[2])

def candidates(records,new):
    options=[]
    for i,item in enumerate(records):
        for left,right in ((item,new),(new,item),(mirrored(item),new),
                           (new,mirrored(item)),(item,mirrored(new)),
                           (mirrored(new),item)):
            merged=join(left,right)
            if merged is not None:options.append((i,merged))
    return options

def features(record,memory,index):
    a,b,codes=record
    endpoints=Counter()
    for x,y,ops in memory:
        endpoints[x]+=1;endpoints[y]+=1
    observed=max(endpoints[a],endpoints[b])
    diversity=len({c//2 for c in codes})
    return (1.,len(codes)/6,observed/12,diversity/4,
            index/71,float(len(codes)>=2),
            float(a in endpoints and b in endpoints))

def model_value(record,memory,index,w):
    feat=features(record,memory,index)
    return sum(x*y for x,y in zip(w,feat))

def hash_value(record):
    a,b,c=record
    return random.Random(a*19+b*79+sum((i+1)*x for i,x in enumerate(c))*37).random()

def score(record,memory,index,mode,w):
    f=features(record,memory,index)
    if mode=="learned_relation_chunking":return model_value(record,memory,index,w)
    if mode=="fixed_public_greedy_pair_chunks":
        return min(len(record[2]),2)*4+.01*f[2]+.00001*index
    if mode=="fixed_public_greedy_triple_chunks":
        return min(len(record[2]),3)*4+.01*f[2]+.00001*index
    if mode=="raw_degree_priority":return f[2]*3+f[3]
    if mode=="raw_connected_component":return f[6]*3+f[2]
    if mode=="raw_FIFO":return index/71
    if mode=="public_hash":return hash_value(record)
    raise ValueError("invalid policy")

def memory_after_stream(events,mode,w):
    records=[]
    for index,e in enumerate(events):
        new=edge_record(e)
        allow_merge=mode in ("learned_relation_chunking",
                         "fixed_public_greedy_pair_chunks",
                         "fixed_public_greedy_triple_chunks")
        if allow_merge:
            opts=candidates(records,new)
            if opts:
                if mode=="fixed_public_greedy_pair_chunks":
                    opts=[(i,r) for i,r in opts if len(r[2])<=2]
                if mode=="fixed_public_greedy_triple_chunks":
                    opts=[(i,r) for i,r in opts if len(r[2])<=3]
                if opts:
                    best=max(opts,key=lambda q:(score(q[1],records,index,mode,w),
                             len(q[1][2]),-q[0]))
                    i,combined=best
                    records=[r for k,r in enumerate(records) if k!=i]
                    new=combined
        records.append(new)
        if len(records)>LIMIT:
            idx=min(range(len(records)),key=lambda i:(score(records[i],records,index,mode,w),i))
            records.pop(idx)
        assert len(records)<=LIMIT
        # Enforce every persistent record is losslessly encoded as a 12B
        # payload; no side-car index/decoder table is retained by the policy.
        assert all(unpack(pack(*record))==record for record in records)
    return tuple(records)

def solve(records,question):
    remaining=tuple(2*role+(direction==-1) for role,direction in question["ops"])
    at=question["start"]
    visited=set()
    while remaining:
        choices=[]
        for record in records:
            for candidate in (record,mirrored(record)):
                a,b,c=candidate
                if a==at and remaining[:len(c)]==c:
                    choices.append(candidate)
        if not choices:return None
        unique={(a,b,c) for a,b,c in choices}
        if len(unique)!=1:return None
        a,b,c=next(iter(unique))
        at=b;remaining=remaining[len(c):]
        state=at,remaining
        if state in visited:return None
        visited.add(state)
    return at

def train():
    data=[]
    for seed in FIT:
      for fam in FIT_FAM:
        events,question,paths=source(seed,fam)
        core=set(x for p in paths for x in p["edges"])
        mem=[]
        for i,e in enumerate(events):
            record=edge_record(e)
            feat=features(record,mem,i)
            data.append((feat,int(e in core)))
            mem.append(record)
            if len(mem)>LIMIT:mem.pop(0)
    weights=[0.]*DIMS
    for epoch in range(24):
        for f,target in data:
            z=sum(w*x for w,x in zip(weights,f))
            p=1/(1+math.exp(-max(-15,min(15,z))))
            for k in range(DIMS):
                weights[k]-=.027*((p-target)*(4 if target else 1)*f[k]+.0003*weights[k])
    return weights,len(data)

def run():
    assert set(FIT).isdisjoint(DIAG) and set(FIT_FAM).isdisjoint(DIAG_FAM)
    assert set(RESERVED).isdisjoint(DIAG)
    weights,nfit=train()
    rows=[]
    for seed in DIAG:
      for fam in DIAG_FAM:
        events,question,paths=source(seed,fam)
        results={};receipts={}
        for arm in ARMS[:-1]:
            records=memory_after_stream(events,arm,weights)
            answer=solve(records,question)
            results[arm]=int(answer==question["answer"])
            receipts[arm]=[pack(*rec).hex() for rec in records]
        results["private_future_question_oracle_unfair"]=int(
            solve([edge_record(e) for e in question_edges(events,question)],question)==question["answer"])
        rows.append(dict(seed=seed,family=fam,public_events=[list(e) for e in events],
                         query=dict(start=question["start"],ops=[list(x) for x in question["ops"]],
                                    answer=question["answer"]),
                         receipts=receipts,results=results))
    scores={arm:dict(correct=sum(row["results"][arm] for row in rows),total=len(rows))
            for arm in ARMS}
    for a in scores.values():a["accuracy"]=a["correct"]/a["total"]
    strata={str(f):{a:sum(row["results"][a] for row in rows if row["family"]==f)
                     for a in ARMS} for f in DIAG_FAM}
    strongest=max(ARMS[1:-1],key=lambda a:scores[a]["accuracy"])
    gain=scores["learned_relation_chunking"]["accuracy"]-scores[strongest]["accuracy"]
    protected=all(strata[str(f)]["learned_relation_chunking"]>=
          max(strata[str(f)][a] for a in ARMS[1:-1]) for f in DIAG_FAM)
    passed=gain>=.05 and protected
    return dict(schema="yggdrasil.f52.online-relation-chunks.trainonly.v1",
       stage="TRAIN_ONLY_DISJOINT_TOPOLOGY_AND_MEMORY_NOT_ORIGINAL",
       fit_seeds=[FIT.start,FIT.stop],fit_families=list(FIT_FAM),
       diagnostic_seeds=[DIAG.start,DIAG.stop],diagnostic_families=list(DIAG_FAM),
       original_seeds_NOT_RESERVED=[RESERVED.start,RESERVED.stop],
       train_examples=nfit,weights=weights,cases=len(rows),rows=rows,
       records_max=LIMIT,record_bytes=12,total_payload_max_bytes=144,
       query_hidden_until_memory_frozen=True,scores=scores,by_family=strata,
       strongest_equal_byte_fair_control=strongest,candidate_gain=gain,
       family_nondegradation=protected,frozen_gate_met=passed,
       verdict="TRAIN_ONLY_RELATION_CHUNKING_SUPPORTED" if passed else
               "TRAIN_ONLY_RELATION_CHUNKING_NEGATIVE",
       independent_F3=False,primary_original_executed=False,
       native_576B_total_unverified=True,accepted_ref_mutation=False,paid_api_calls=0)

def question_edges(events,question):
    # Evaluator-only oracle reconstructs chosen path from all original
    # observed events *after* retention; never part of a public policy.
    at=question["start"]
    result=[]
    for role,direction in question["ops"]:
        candidates=[(a,r,b) for a,r,b in events if r==role and
                    (a if direction==1 else b)==at]
        if len(candidates)!=1:
            return []
        e=candidates[0]
        result.append(e)
        at=e[2] if direction==1 else e[0]
    return result

if __name__=="__main__":print(json.dumps(run(),indent=2,sort_keys=True))
