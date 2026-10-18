"""T2 Yggdrasil independently specified cross-corridor topology source.

A completely different graph grammar from F62's disconnected corridors:
new public 72-edge stream has at least eight cross-path joins between four
real 8-edge causal corridors, plus branching distractor edges. The hidden
question and positive answer remain evaluator-only, never online policy.
Registered TRAIN/SCREEN/UNSEEN/REPLICA identities cannot be constructed.
"""
from __future__ import annotations
import json,random
from pathlib import Path

ROOT=Path(__file__).resolve().parent
FREEZE=ROOT/"20261018-yggdrasil-t2-source-freeze.json"
RESERVED=tuple(range(890001,890025))+tuple(range(891001,891017))+tuple(range(892001,892033))+tuple(range(893001,893033))
FIXTURES=(-920,-921)

def need(x,tag):
    if not x:raise ValueError("YGG_T2_"+tag)

def build_fixture(seed):
    need(seed in FIXTURES,"SEALED_SOURCE_ID_NOT_CONSTRUCTIBLE")
    rng=random.Random(74447+seed*1103)
    used=set()
    def unique():
        while True:
            v=rng.randrange(1000,1500000000)
            if v not in used:
                used.add(v);return v
    corridors=[];public=[];joins=[]
    for k in range(4):
        nodes=[unique() for _ in range(9)]
        ops=[]
        for i in range(8):
            role=rng.randrange(4)
            direction=rng.choice((-1,1))
            a,b=nodes[i],nodes[i+1]
            event=(a,role,b) if direction==1 else (b,role,a)
            ops.append((role,direction))
            public.append(event)
        corridors.append({"nodes":tuple(nodes),"ops":tuple(ops)})
    for i in range(8):
        left=i%4;right=(left+1+i//4)%4
        if left==right:right=(right+1)%4
        a=corridors[left]["nodes"][2+(i%4)]
        b=corridors[right]["nodes"][3+((i+1)%4)]
        event=(a,rng.randrange(4),b)
        need(event not in public,"UNIQUE_CROSS_CORRIDOR_JOIN")
        joins.append(event)
        public.append(event)
    # 32 additional public distractors, graph-branching yet source-blind.
    for j in range(32):
        node=unique()
        if j<16:
            at=corridors[j%4]["nodes"][1+(j//4)]
            event=(node,rng.randrange(4),at) if j%2 else (at,rng.randrange(4),node)
        else:
            a=unique();b=unique()
            event=(a,rng.randrange(4),b)
        public.append(event)
    need(len(public)==72 and len(set(public))==72
         and len(joins)==8 and all(len(x["ops"])==8 for x in corridors),
         "UNSEEN_TOPOLOGY_CONSTRUCTION_INVARIANT")
    rng.shuffle(public)
    # None of the following evaluator-only fields enters online inference.
    picked=rng.randrange(4)
    target=corridors[picked]
    evaluator={"start":target["nodes"][0],"ops":target["ops"],
               "answer":target["nodes"][8],"source_fixture_id":seed,
               "cross_corridor_join_count":len(joins)}
    return tuple(public),evaluator

def attest():
    d=json.loads(FREEZE.read_text())
    need(d["schema"]=="northstar.t2.yggdrasil.unseen-topology-source.v1"
         and d["registered_cohorts_not_constructed"] is True
         and d["source_anchor_head"]=="19635df877372268ca66a268ea56fdd4787522f9",
         "IMMUTABLE_T2_BIRTH")
    need(not set(FIXTURES).intersection(RESERVED),"DISJOINT_SOURCE")
    for seed in (890001,891001,892001,893001):
        try:build_fixture(seed)
        except ValueError:pass
        else:raise AssertionError("scientific cohort construction prohibited")
    source,private=build_fixture(-920)
    need(len(source)==72 and all(len(x)==3 and 0<=x[1]<4 for x in source)
         and len(private["ops"])==8
         and private["cross_corridor_join_count"]==8,"SOURCE_SHAPE")
    return {"schema":"ygg.t2.topology-nonconsuming.v1",
            "synthetic_fixture_events":72,
            "synthetic_true_corridors":4,
            "cross_corridor_joins":8,
            "new_topology_grammar_not_F62_disconnected":True,
            "sealed_cohort_born":0,
            "native_F85_can_solve_8_ops":False,
            "scientific_transfer_ready":False}
if __name__=="__main__":print(json.dumps(attest(),sort_keys=True))
