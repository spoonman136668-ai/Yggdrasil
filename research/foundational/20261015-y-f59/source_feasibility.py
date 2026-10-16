"""Y-F59 FIT-only deferred-component open-frontier source and online construction.

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

FIT=range(711000,711016)
FAMILY=(1360,1361,1362,1363)
DIAG=range(711100,711116)
PROTECTED=range(712000,712016)
RECORD_CAP=12
RECORD_BYTES=12
EVENTS=72

def source(seed:int,family:int):
    if seed not in FIT or family not in FAMILY:
        raise ValueError("F59 source only permits the frozen FIT fold")
    r=random.Random(seed*33913+family*5209+59037)
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
    # F59 source families test two genuinely distinct causal schedules:
    # very-late component heads and simultaneous open frontiers whose
    # attachment edges arrive only after competing distractors.
    if family%2==0:
        regime="late_core_heads"
        stream=[]
        core=[e for lane in order for e in paths[lane][2][1:]]
        for j,e in enumerate(core):
            stream.append(e)
            if (j+1)%4==0 and j<28:
                off=((j+1)//4-1)*4
                stream.extend(distractors[off:off+4])
        stream.extend(distractors[28:])
        stream.extend(paths[lane][2][0] for lane in order)
    else:
        regime="overlapping_component_frontiers"
        stream=[]
        # Each path opens 2-step fronts, but interior links to extend
        # those fronts become separated by competing public observations.
        for step in range(0,8,2):
            for lane in order:
                stream.extend(paths[lane][2][step:step+2])
            stream.extend(distractors[(step//2)*10:(step//2+1)*10])
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

def frontier_online(public):
    """Causal open-boundary controller; 12 lossless records only.

    The policy is allowed to scan its own *retained* records to join
    inbound edges and preserve endpoints with attachment opportunity.
    No complete-graph access, private path membership or query oracle.
    """
    memory=[]
    for event in public:
        memory.append(edge_record(event))
        # Allow the new observation to complete chains whose partial
        # boundaries were retained, not just merge a single greedy pair.
        for _ in range(RECORD_CAP):
            choices=[]
            for i in range(len(memory)):
                for j in range(len(memory)):
                    if i==j:continue
                    for a in (memory[i],inverse(memory[i])):
                        for b in (memory[j],inverse(memory[j])):
                            merged=concat(a,b)
                            if merged is not None:
                                rank=(len(merged[2]),int(i==len(memory)-1 or j==len(memory)-1),-min(i,j),-max(i,j))
                                choices.append((rank,i,j,merged))
            if not choices:break
            _,i,j,merged=max(choices,key=lambda x:x[0])
            memory=[x for k,x in enumerate(memory) if k not in (i,j)]+[merged]
        if len(memory)>RECORD_CAP:
            # Open frontiers: prefer records which still have matching
            # boundaries in *currently retained public memory*.
            endpoints={}
            for a,b,c in memory:
                endpoints[a]=endpoints.get(a,0)+1
                endpoints[b]=endpoints.get(b,0)+1
            index=min(range(len(memory)),key=lambda k:(
                len(memory[k][2])*2+
                min(2,endpoints.get(memory[k][0],0)-1)+
                min(2,endpoints.get(memory[k][1],0)-1),k))
            memory.pop(index)
        assert len(memory)<=RECORD_CAP
        assert all(unpack(pack(r))==r for r in memory)
    return tuple(memory)

def fixed_deferred_component_buffer(public):
    """Causal lossless open-frontier construction without private labels.

    Only the active 12 retained compact records and the current public
    edge are available; no side-store of evicted graph or extra indices.
    This controller prioritizes retained endpoint variety over length.
    """
    memory=[]
    for observation in public:
        memory.append(edge_record(observation[:3]))
        # Multi-pair completion after each arrival within the byte cap.
        for step in range(RECORD_CAP):
            possible=[]
            for i in range(len(memory)):
                for j in range(i+1,len(memory)):
                    for left in (memory[i],inverse(memory[i])):
                        for right in (memory[j],inverse(memory[j])):
                            for a,b in ((left,right),(right,left)):
                                joined=concat(a,b)
                                if joined is None:continue
                                # A joined path retains its true public
                                # endpoints and supports future attachment.
                                rank=(len(joined[2]),-min(i,j),-max(i,j))
                                possible.append((rank,i,j,joined))
            if not possible:break
            _,i,j,rec=max(possible,key=lambda x:x[0])
            memory=[x for k,x in enumerate(memory) if k not in (i,j)]+[rec]
        if len(memory)>RECORD_CAP:
            endpoints={}
            for a,b,codes in memory:
                endpoints[a]=endpoints.get(a,0)+1
                endpoints[b]=endpoints.get(b,0)+1
            def retention_value(rec):
                a,b,codes=rec
                # Query-blind, public-only potential of open endpoints,
                # preserving diverse frontier anchors under delayed joins.
                return (3*len(codes)+
                    2*int(endpoints[a]>1)+2*int(endpoints[b]>1)-
                    int(a==b))
            drop=min(range(len(memory)),key=lambda k:(
                 retention_value(memory[k]),k))
            memory.pop(drop)
        assert len(memory)<=RECORD_CAP
        assert all(unpack(pack(r))==r for r in memory)
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
        for fam in FAMILY:
            public,q,regime=source(seed,fam)
            assert len(public)==72 and sum(e[3] for e in public)==36
            arms={
                "qualified_fixed_component_buffer":fixed_deferred_component_buffer(public),
                "frozen_F58_causal_frontier":frontier_online(public),
                "frozen_F57_incremental":causal_online(public,"incremental_boundary_merge"),
                "public_full_graph_offline_noncompetitive":full_public_reference(public)}
            d={name:solve(records,q) for name,records in arms.items()}
            rows.append(dict(seed=seed,family=fam,regime=regime,
               public_events=[list(e[:3]) for e in public],
               question=dict(start=q["start"],ops=[list(x) for x in q["ops"]],answer=q["answer"]),
               predictions=d,retained_records={a:[pack(x).hex() for x in recs] for a,recs in arms.items()},
               serialized_bytes={a:12*len(recs) for a,recs in arms.items()}))
    count={a:sum(row["predictions"][a] for row in rows) for a in rows[0]["predictions"]}
    gate=count["qualified_fixed_component_buffer"]/64>=.25 and count["public_full_graph_offline_noncompetitive"]/64>=.85
    return dict(schema="yggdrasil.f59.deferred-attachment-FIT-source.v1",
       stage="F59_NEW_FIT_SOURCE_ONLY_NO_LEARNED_USE",
       fit_seeds=[FIT.start,FIT.stop],fit_families=list(FAMILY),
       cases=len(rows),rows=rows,correct=count,
       offline_extra_work_noncompetitive=True,
       online_query_hidden_until_retention_complete=True,
       frozen_FIT_source_gate_met=gate,
       DIAG_untouched=True,originals_untouched=True,
       native_total_576B_unverified=True,independent_F3=False,
       accepted_refs_unchanged=True)
if __name__=="__main__":
    if sys.argv[1:]!=["--fit-only"]:
        raise SystemExit("FIT-only source; no diagnostic or original")
    print(json.dumps(fit_preview(),sort_keys=True))
