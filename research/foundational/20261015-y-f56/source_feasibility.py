"""Y-F56 source-only FIT feasibility: online component memory during arrivals.

Source creates four eight-edge variable-binding components and shorter
distractor components, 72 public role edges total. The future question is
hidden until *after* the online controller's 12 losslessly coded 12-byte
records have frozen. Clustered / bounded-interleave arrival distributions
are public, never action-time labels. This module refuses DIAG execution.
"""
from __future__ import annotations
import importlib.util,json,random,sys
from pathlib import Path
p=Path(__file__).resolve().parent.parent/"20261015-y-f52"/"source_pilot.py"
s=importlib.util.spec_from_file_location("y56_codec",p)
codec=importlib.util.module_from_spec(s);sys.modules[s.name]=codec;s.loader.exec_module(codec)
FIT=range(631000,631016)
DIAG=range(631100,631116)
FIT_FAMILIES=(1160,1161,1162,1163)
DIAG_FAMILIES=(1164,1165,1166,1167)
ORIGINAL=range(632000,632016)
CAP=12
def source(seed,family):
    if seed not in FIT or family not in FIT_FAMILIES:
        raise ValueError("Only F56 FIT source authorized; DIAG and original not used")
    rng=random.Random(seed*18097+family*3407+56003)
    used=set()
    def fresh():
        while True:
            n=rng.randrange(1000,1500000000)
            if n not in used:used.add(n);return n
    paths=[]
    for k in range(4):
        nodes=[fresh() for i in range(9)]
        if nodes[0]>nodes[8]:nodes.reverse()
        events=[];ops=[]
        for j in range(8):
            role=rng.choice([r for r in range(4) if not ops or r!=ops[-1][0]])
            direction=1 if rng.random()<.5 else -1
            a,b=nodes[j],nodes[j+1]
            events.append((a,role,b) if direction==1 else (b,role,a))
            ops.append((role,direction))
        paths.append((tuple(nodes),tuple(ops),tuple(events)))
    distract=[]
    # Eight 3-edge disconnected components + eight 2-edge components.
    # The source intentionally leaves the public structural witness
    # possible, rather than teaching importance through public tags.
    for k in range(8):
        v=[fresh() for i in range(4)]
        for j in range(3):
            a,b=v[j],v[j+1]
            if rng.random()<.5:a,b=b,a
            distract.append((a,rng.randrange(4),b))
    for k in range(8):
        v=[fresh() for i in range(3)]
        for j in range(2):
            a,b=v[j],v[j+1]
            if rng.random()<.5:a,b=b,a
            distract.append((a,rng.randrange(4),b))
    assert len(distract)==40
    order=list(range(4));rng.shuffle(order)
    regime="clustered" if family%2==0 else "bounded_interleave"
    core=[]
    if regime=="clustered":
        for k in order:core.extend(paths[k][2])
        stream=core[:]
        stream[8:8]=distract[:2]
        stream[18:18]=distract[2:4]
        stream[28:28]=distract[4:6]
        stream.extend(distract[6:])
    else:
        # Publicly observable partial clusters in a shifted stream.
        stream=[]
        for block in range(4):
            for k in order:
                stream.extend(paths[k][2][2*block:2*block+2])
                stream.extend(distract[(block*4+order.index(k))*2:(block*4+order.index(k))*2+2])
        stream.extend(distract[32:])
    assert len(stream)==72 and len(set(stream))==72
    # Balanced tags are recorded for falsification but not policy inputs.
    core_set={e for nodes,ops,edges in paths for e in edges}
    core_tags=[1]*16+[0]*16;noise_tags=[1]*20+[0]*20
    rng.shuffle(core_tags);rng.shuffle(noise_tags)
    core_it=iter(core_tags);noise_it=iter(noise_tags)
    tagged=tuple((*e,next(core_it) if e in core_set else next(noise_it)) for e in stream)
    chosen=paths[rng.randrange(4)]
    hops=(4,6,8)[(seed+family)%3]
    q=dict(start=chosen[0][0],ops=chosen[1][:hops],answer=chosen[0][hops])
    return tagged,q,regime
def offline_public_witness(public):
    """Full 72-edge scan; noncompetitive offline observation-work."""
    edges=[tuple(e[:3]) for e in public]
    adj={}
    for i,(a,r,b) in enumerate(edges):
        adj.setdefault(a,[]).append((b,i))
        adj.setdefault(b,[]).append((a,i))
    done=set();paths=[]
    for node in sorted(adj):
        if node in done:continue
        stack=[node];seen={node};indices=set()
        while stack:
            u=stack.pop()
            for v,i in adj[u]:
                indices.add(i)
                if v not in seen:seen.add(v);stack.append(v)
        done.update(seen)
        if len(seen)==9 and len(indices)==8:
            leaves=sorted(x for x in seen if len(adj[x])==1)
            if len(leaves)!=2:continue
            at=leaves[0];before=None;nodes=[at];ops=[]
            while len(ops)<8:
                links=[(other,i) for other,i in adj[at] if other!=before]
                if len(links)!=1:raise AssertionError("non-path witness")
                nxt,i=links[0];a,r,b=edges[i]
                ops.append(2*r+(a!=at))
                before,at=at,nxt;nodes.append(at)
            paths.append((nodes,ops))
    assert len(paths)==4
    records=[]
    for nodes,ops in paths:
        for offset,size in ((0,4),(4,4)):
            records.append((nodes[offset],nodes[offset+size],tuple(ops[offset:offset+size])))
    assert len(records)==8
    assert len(records)*12<=144
    return records
def online_fixed(public):
    """Causal fixed merge-and-evict policy: only retained memory + new edge."""
    memory=[]
    for i,event in enumerate(public):
        incoming=codec.edge_record(event[:3])
        proposals=[]
        for at,merged in codec.candidates(memory,incoming):
            if len(merged[2])<=4:proposals.append((at,merged))
        if proposals:
            selected,composed=max(proposals,key=lambda t:(len(t[1][2]),-t[0]))
            memory=[r for j,r in enumerate(memory) if j!=selected]
            incoming=composed
        memory.append(incoming)
        if len(memory)>CAP:
            # Longer connected public chains carry larger query-blind
            # structural value than isolated distractors.
            evict=min(range(len(memory)),key=lambda k:(len(memory[k][2]),k))
            memory.pop(evict)
        assert len(memory)<=CAP
        assert all(codec.unpack(codec.pack(*r))==r for r in memory)
    return tuple(memory)
def fit_report():
    rows=[]
    for seed in FIT:
        for family in FIT_FAMILIES:
            public,q,regime=source(seed,family)
            core_pos=sum(e[3] for e in public)
            assert core_pos==36
            online=online_fixed(public)
            offline=offline_public_witness(public)
            rows.append(dict(seed=seed,family=family,regime=regime,
               online_correct=int(codec.solve(online,q)==q["answer"]),
               offline_correct=int(codec.solve(offline,q)==q["answer"]),
               online_records=len(online),online_bytes=12*len(online),
               offline_bytes=12*len(offline)))
    fit_online=sum(z["online_correct"] for z in rows)
    fit_offline=sum(z["offline_correct"] for z in rows)
    return dict(schema="yggdrasil.f56.online-constructive-arrival.fitonly.v1",
      FIT_seeds=[FIT.start,FIT.stop],FIT_families=list(FIT_FAMILIES),
      cases=len(rows),source_query_hidden_until_retention=True,
      online_constructive_correct=fit_online,offline_reference_correct=fit_offline,
      online_accuracy=fit_online/len(rows),offline_accuracy=fit_offline/len(rows),
      online_min_gate=.25,offline_min_gate=.85,
      frozen_fit_gate_met=fit_online/len(rows)>=.25 and fit_offline/len(rows)>=.85,
      all_DIAG_untouched=True,originals_untouched=True,
      source_independent_F3=False,native_total_576B_unverified=True,rows=rows)
if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1]!="--fit-only":
        raise SystemExit("Only --fit-only allowed. No diagnostic access.")
    print(json.dumps(fit_report(),sort_keys=True))
