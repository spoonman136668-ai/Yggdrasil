"""Y-F55: constructive public-only feasibility witness before learned memory.

A query-blind full-public structural witness discovers four eight-edge path
components from 72 public events, then emits at most 12 *losslessly encoded*
12-byte relation records (4+2+2 segments per recovered path). The future
question is generated independently from four equally likely paths and
revealed only after memory is constructed. This offline whole-graph scan is
NOT a same-work online fair baseline or a proven information bound.
"""
from __future__ import annotations
import importlib.util,json,random,sys
from collections import defaultdict,Counter
from pathlib import Path
base=Path(__file__).resolve().parent.parent/"20261015-y-f52"/"source_pilot.py"
spec=importlib.util.spec_from_file_location("y55_lossless_codec",base)
codec=importlib.util.module_from_spec(spec);sys.modules[spec.name]=codec;spec.loader.exec_module(codec)
FIT=range(611000,611016);DIAG=range(611100,611116)
FIT_FAM=(1120,1121,1122,1123);DIAG_FAM=(1124,1125,1126,1127)
ORIGINAL=range(612000,612016)
def source(seed,fam):
    fit=seed in FIT and fam in FIT_FAM
    diag=seed in DIAG and fam in DIAG_FAM
    if not (fit or diag):raise ValueError("unregistered source; original denied")
    rng=random.Random(seed*27077+fam*1163+55007)
    occupied=set()
    def fresh():
        while True:
            n=rng.randrange(1000,1500000000)
            if n not in occupied:occupied.add(n);return n
    paths=[];core=[];distractor=[]
    for j in range(4):
        nodes=[fresh() for _ in range(9)]
        # Rule: future questions start at smaller of two public component
        # leaves. This query-source bias is public, not privileged.
        if nodes[0]>nodes[-1]:nodes.reverse()
        steps=[];roles=[]
        for k in range(8):
            role=rng.choice([v for v in range(4) if not roles or v!=roles[-1]])
            d=1 if rng.random()<.5 else -1
            a,b=nodes[k],nodes[k+1]
            raw=(a,role,b) if d==1 else (b,role,a)
            steps.append((role,d));roles.append(role);core.append(raw)
        paths.append(dict(nodes=tuple(nodes),ops=tuple(steps),edges=tuple(core[-8:])))
    # Distractors are shorter isolated components; heldout uses triangles
    # with inverted role orientations, no future-label or tag information.
    if fit:
        for j in range(8):
            nodes=[fresh() for _ in range(4)]
            for k in range(3):
                a,b=nodes[k],nodes[k+1]
                if rng.random()<.5:a,b=b,a
                distractor.append((a,rng.randrange(4),b))
    else:
        for j in range(8):
            nodes=[fresh() for _ in range(3)]
            for a,b in ((0,1),(1,2),(2,0)):
                u,v=nodes[a],nodes[b]
                if rng.random()<.5:u,v=v,u
                distractor.append((u,rng.randrange(4),v))
    for j in range(8):
        a,b=fresh(),fresh()
        distractor.extend(((a,rng.randrange(4),b),(b,(rng.randrange(4)),fresh())))
    assert len(core)==32 and len(distractor)==40
    core_tag=[1]*16+[0]*16;dist_tag=[1]*20+[0]*20
    rng.shuffle(core_tag);rng.shuffle(dist_tag)
    obs=[(*e,t) for e,t in zip(core,core_tag)]
    obs.extend((*e,t) for e,t in zip(distractor,dist_tag))
    rng.shuffle(obs)
    selected=paths[rng.randrange(4)]
    hops=(4,6,8)[(seed+fam)%3]
    start=selected["nodes"][0]
    end=selected["nodes"][hops]
    question=dict(start=start,ops=selected["ops"][:hops],answer=end)
    return tuple(obs),question,tuple(paths)
def witness(public):
    # Only public edges are visible; no query, private family, tags, or
    # true path membership enter this procedure.
    edges=[tuple(e[:3]) for e in public]
    adjacent=defaultdict(list)
    for i,(a,r,b) in enumerate(edges):
        adjacent[a].append((b,i))
        adjacent[b].append((a,i))
    covered=set();components=[]
    for n in sorted(adjacent):
        if n in covered:continue
        discovered={n};stack=[n];eindices=set()
        while stack:
            u=stack.pop()
            for v,i in adjacent[u]:
                eindices.add(i)
                if v not in discovered:discovered.add(v);stack.append(v)
        covered.update(discovered)
        components.append((discovered,eindices))
    # High-length path components are structurally public: 8 edges, 9
    # nodes, exactly two leaves. Short distractors cannot counterfeit them.
    long=[]
    for nodes,indices in components:
        degree={n:len(adjacent[n]) for n in nodes}
        leaf=sorted(n for n,d in degree.items() if d==1)
        if len(nodes)==9 and len(indices)==8 and len(leaf)==2 and
           all(d in (1,2) for d in degree.values()):
            start=leaf[0];cur=start;prev=None
            ordered=[]
            while len(ordered)<8:
                links=[(v,i) for v,i in adjacent[cur] if v!=prev]
                if len(links)!=1:raise AssertionError("not a simple path")
                v,i=links[0];a,r,b=edges[i]
                ordered.append((r,1 if a==cur else -1))
                prev,cur=cur,v
            nodes_order=[start]
            cur=start;prev=None
            for role,dr in ordered:
                nxt=[v for v,i in adjacent[cur] if v!=prev]
                assert len(nxt)==1
                prev,cur=cur,nxt[0]
                nodes_order.append(cur)
            long.append((tuple(nodes_order),tuple(ordered)))
    # Each of four public structurally longest paths requires exactly three
    # query-prefix-compatible records: 4 steps then 2 and 2.
    if len(long)!=4:raise AssertionError("FIT source not public-feasible")
    records=[]
    for nodes,ordered in sorted(long,key=lambda x:x[0][0]):
        for start,width in ((0,4),(4,2),(6,2)):
            codes=tuple(2*role+(direction==-1) for role,direction in ordered[start:start+width])
            item=(nodes[start],nodes[start+width],codes)
            assert codec.unpack(codec.pack(*item))==item
            records.append(item)
    assert len(records)==12 and sum(len(codec.pack(*r)) for r in records)==144
    return tuple(records),len(edges)+sum(len(edges) for _ in components)
def fit_only_report():
    rows=[]
    for seed in FIT:
      for fam in FIT_FAM:
        public,q,paths=source(seed,fam)
        recovered,work=witness(public)
        correct=int(codec.solve(recovered,q)==q["answer"])
        rows.append(dict(seed=seed,family=fam,correct=correct,work=work,
                         serialized_bytes=sum(len(codec.pack(*r)) for r in recovered)))
    assert len(rows)==64
    n=sum(r["correct"] for r in rows)
    return dict(schema="yggdrasil.f55.public-memory-constructive-fit-only.v1",
      fit_seeds=[FIT.start,FIT.stop],fit_families=list(FIT_FAM),
      fit_streams=64,public_reference_correct=n,public_reference_accuracy=n/64,
      witness_threshold=0.25,witness_feasible=n>=16,
      memory_payload_bytes=144,record_bytes=12,records=12,
      extra_public_offline_work_noncompetitive=True,
      future_question_never_used_by_witness=True,
      disjoint_DIAG_unused=True,originals_unused=True,
      native_576B_total_unverified=True,rows=rows)
if __name__=="__main__":
    if len(sys.argv)!=2 or sys.argv[1]!="--fit-only":
        raise SystemExit("only --fit-only source witness is authorized")
    print(json.dumps(fit_only_report(),sort_keys=True))
