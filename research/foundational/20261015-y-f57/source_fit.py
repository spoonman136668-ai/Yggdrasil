"""Y-F57 FIT-only public component-state source and online construction.

Creates a new public 72-edge problem with disjoint long paths, fragmented
arrival, balanced non-informative tags, and a future query withheld until the
bounded 12-record memory is frozen. No diagnostic or protected originals.
The causal merge algorithm here is a prospective *fixed control*, not the
learned candidate and not an accepted scientific claim.
"""
from __future__ import annotations
import json
import random
import sys

FIT=range(671000,671016)
FAMILY=(1260,1261,1262,1263)
DIAG=range(671100,671116)
PROTECTED=range(672000,672016)
RECORD_CAP=12
RECORD_BYTES=12
EVENTS=72

def source(seed:int,family:int):
    if seed not in FIT or family not in FAMILY:
        raise ValueError("F57 source only permits the frozen FIT fold")
    r=random.Random(seed*31111+family*4909+57037)
    used=set()
    def node():
        while True:
            n=r.randrange(1000,2**31-1)
            if n not in used:
                used.add(n)
                return n
    paths=[]
    for _ in range(4):
        nodes=[node() for j in range(9)]
        if nodes[0]>nodes[-1]:
            nodes.reverse()
        chain=[]
        edges=[]
        for j in range(8):
            choices=[k for k in range(4) if not chain or chain[-1][0]!=k]
            role=r.choice(choices)
            direction=r.choice((-1,1))
            a,b=nodes[j:j+2]
            edges.append((a,role,b) if direction==1 else (b,role,a))
            chain.append((role,direction))
        paths.append((tuple(nodes),tuple(chain),tuple(edges)))
    distractors=[]
    for _ in range(8):
        nodes=[node() for j in range(4)]
        for j in range(3):
            a,b=nodes[j:j+2]
            if r.randrange(2):a,b=b,a
            distractors.append((a,r.randrange(4),b))
    for _ in range(8):
        nodes=[node() for j in range(3)]
        for j in range(2):
            a,b=nodes[j:j+2]
            if r.randrange(2):a,b=b,a
            distractors.append((a,r.randrange(4),b))
    assert len(distractors)==40
    order=list(range(4));r.shuffle(order)
    fragments=[]
    width=4 if family%2==0 else 2
    for off in range(0,8,width):
        for lane in order:
            fragments.extend(paths[lane][2][off:off+width])
    # Public arrivals remain fragmentary rather than revealing any
    # future-question-specific true-path labels.
    stream=[]
    for idx,edge in enumerate(fragments):
        stream.append(edge)
        if idx<32 and (idx+1)%4==0:
            stream.extend(distractors[((idx+1)//4-1)*4:((idx+1)//4)*4])
    stream.extend(distractors[32:])
    assert len(stream)==EVENTS and len(set(stream))==EVENTS
    core={e for _,_,es in paths for e in es}
    core_tags=[1]*16+[0]*16
    distract_tags=[1]*20+[0]*20
    r.shuffle(core_tags);r.shuffle(distract_tags)
    a=iter(core_tags);b=iter(distract_tags)
    public=tuple((*edge,next(a) if edge in core else next(b)) for edge in stream)
    chosen=paths[r.randrange(4)]
    hops=(4,6,8)[(seed+family)%3]
    question={"start":chosen[0][0],
              "ops":tuple(chosen[1][:hops]),
              "answer":chosen[0][hops]}
    regime="interleaved_components" if width==4 else "phase_shifted_partial_paths"
    return public,question,regime

def edge_record(edge):
    a,role,b=edge[:3]
    return (a,b,(2*role,))

def inverse(rec):
    a,b,codes=rec
    return (b,a,tuple(code^1 for code in reversed(codes)))

def concat(a,b):
    if a[1]!=b[0] or len(a[2])+len(b[2])>4:return None
    return a[0],b[1],a[2]+b[2]

def pack(rec):
    a,b,codes=rec
    if (not 0<=a<2**32 or not 0<=b<2**32
        or not 1<=len(codes)<=4 or any(not 0<=x<=7 for x in codes)):
        raise ValueError("invalid packed memory")
    bits=sum(c<<(3*i) for i,c in enumerate(codes))
    return a.to_bytes(4,"little")+b.to_bytes(4,"little")+bits.to_bytes(3,"little")+bytes([len(codes)])

def unpack(raw):
    if len(raw)!=12:raise ValueError("record must be 12 bytes")
    a=int.from_bytes(raw[:4],"little")
    b=int.from_bytes(raw[4:8],"little")
    bits=int.from_bytes(raw[8:11],"little")
    n=raw[11]
    if not 1<=n<=4 or bits>>(3*n):
        raise ValueError("invalid role or direction encoding")
    return a,b,tuple((bits>>(3*i))&7 for i in range(n))

def solve(memory,question):
    needed=tuple(2*r+(d==-1) for r,d in question["ops"])
    states={(question["start"],0)}
    for _ in range(len(needed)):
        nxt=set(states)
        for where,i in states:
            for rec in memory:
                for variant in (rec,inverse(rec)):
                    n=len(variant[2])
                    if where==variant[0] and needed[i:i+n]==variant[2]:
                        nxt.add((variant[1],i+n))
        if nxt==states:break
        states=nxt
    return int((question["answer"],len(needed)) in states)

def causal_online(public,mode):
    """Fixed public-only causal reference. Never accepts a future question."""
    if mode not in ("incremental_boundary_merge","frozen_greedy_merge","raw_fifo"):
        raise ValueError("unregistered source control")
    memory=[]
    for arrival in public:
        incoming=edge_record(arrival)
        if mode=="raw_fifo":
            memory=(memory+[incoming])[-RECORD_CAP:]
            continue
        if mode=="frozen_greedy_merge":
            options=[]
            for idx,old in enumerate(memory):
                for x,y in ((old,incoming),(inverse(old),incoming),
                            (incoming,old),(incoming,inverse(old))):
                    z=concat(x,y)
                    if z is not None:options.append((len(z[2]),idx,z))
            if options:
                _,idx,incoming=max(options,key=lambda x:(x[0],-x[1]))
                memory.pop(idx)
            memory.append(incoming)
            if len(memory)>RECORD_CAP:
                memory.pop(min(range(len(memory)),key=lambda k:(len(memory[k][2]),k)))
        else:
            # A different mechanism from static ranking: reconstruct
            # connectivity among the currently *retained* bounded records
            # and replace two records with a lossless role-path union.
            memory.append(incoming)
            for _ in range(RECORD_CAP):
                best=None
                for i in range(len(memory)):
                    for j in range(len(memory)):
                        if i==j:continue
                        for left in (memory[i],inverse(memory[i])):
                            for right in (memory[j],inverse(memory[j])):
                                combined=concat(left,right)
                                if combined is None:continue
                                rank=(len(combined[2]),-min(i,j),-max(i,j))
                                if best is None or rank>best[0]:
                                    best=(rank,i,j,combined)
                if best is None:break
                _,i,j,merged=best
                memory=[z for k,z in enumerate(memory) if k not in (i,j)]+[merged]
            # Retain the longest *actual* public chains. This is a
            # reference construction; the learned eviction policy is still
            # unavailable, and extra algorithmic work is recorded.
            if len(memory)>RECORD_CAP:
                memory=sorted(memory,key=lambda z:(len(z[2]),z[0],z[1]),reverse=True)[:RECORD_CAP]
        assert len(memory)<=RECORD_CAP
        assert all(unpack(pack(z))==z for z in memory)
    return tuple(memory)

def full_public_reference(public):
    """Offline noncompetitive witness; independent of future question."""
    edges=[tuple(e[:3]) for e in public]
    graph={}
    for a,r,b in edges:
        graph.setdefault(a,[]).append((b,r,a,b))
        graph.setdefault(b,[]).append((a,r,a,b))
    visited=set();long=[]
    for start in sorted(graph):
        if start in visited:continue
        stack=[start];nodes={start}
        while stack:
            at=stack.pop()
            for dest,role,a,b in graph[at]:
                if dest not in nodes:
                    nodes.add(dest);stack.append(dest)
        visited.update(nodes)
        leaves=sorted(n for n in nodes if len(graph[n])==1)
        if len(nodes)!=9 or len(leaves)!=2:continue
        u=leaves[0];previous=None
        ordered=[u];codes=[]
        for step in range(8):
            choices=[link for link in graph[u] if link[0]!=previous]
            if len(choices)!=1:raise AssertionError("non-path public witness")
            v,role,a,b=choices[0]
            codes.append(2*role+(u!=a))
            previous,u=u,v;ordered.append(u)
        long.append((ordered,codes))
    if len(long)!=4:raise AssertionError("public source not identifiable")
    records=[]
    for nodes,codes in long:
        for a,b in ((0,4),(4,6),(6,8)):
            records.append((nodes[a],nodes[b],tuple(codes[a:b])))
    assert len(records)==12 and all(unpack(pack(r))==r for r in records)
    return tuple(records)

def fit_preview():
    rows=[]
    for seed in FIT:
        for family in FAMILY:
            public,question,regime=source(seed,family)
            assert len(public)==72 and sum(e[3] for e in public)==36
            # No method sees question before its memory is frozen.
            memory={arm:causal_online(public,arm) for arm in
                    ("incremental_boundary_merge","frozen_greedy_merge","raw_fifo")}
            memory["full_public_offline_extra_work"]=full_public_reference(public)
            scored={arm:solve(m,question) for arm,m in memory.items()}
            rows.append({"seed":seed,"family":family,"regime":regime,
                "public_events":[list(e) for e in public],
                "question":{"start":question["start"],
                            "ops":[list(x) for x in question["ops"]],
                            "answer":question["answer"]},
                "retained_records":{arm:[pack(z).hex() for z in m]
                                    for arm,m in memory.items()},
                "scores":scored,
                "serialized_bytes":{arm:sum(len(pack(z)) for z in m)
                                    for arm,m in memory.items()}})
    arms=tuple(rows[0]["scores"])
    totals={arm:sum(row["scores"][arm] for row in rows) for arm in arms}
    return {"schema":"yggdrasil.f57.new-online-component-state.fitonly.v1",
        "stage":"FIT_ONLY_SOURCE_FEASIBILITY_NO_DIAG_OR_ORIGINAL",
        "fit_seeds":[FIT.start,FIT.stop],"fit_families":list(FAMILY),
        "rows":rows,"cases":len(rows),"correct":totals,
        "offline_reference_is_extra_work_noncompetitive":True,
        "future_question_hidden_during_ingestion":True,
        "diag_unconsumed":True,"original_unconsumed":True,
        "native_total_576B_unverified":True}

if __name__=="__main__":
    if sys.argv[1:]!=["--fit-only"]:
        raise SystemExit("FIT only; no diagnostic or protected original")
    print(json.dumps(fit_preview(),sort_keys=True))
