"""T8 Yggdrasil: source-family-wide public endpoint uniqueness by invariant.

This is a new generator, not a repair/replay of consumed T7 identities.
Only synthetic fixture -18000 exists here; NO real prospective T8 source
identities are born. For any selection of unique node IDs and role labels,
target-reachable state at step j has EXACTLY one outgoing edge matching
the required role, proving one eight-hop endpoint by induction.
"""
from __future__ import annotations
import random,json,importlib.util,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
FREEZE=HERE/"20261019-yggdrasil-t8-source-freeze.json"
T6=HERE/"20261018-yggdrasil-t6-audit.py"
def need(ok,n):
    if not ok:raise ValueError("YGG_T8_"+n)
def load(p,name):
    spec=importlib.util.spec_from_file_location(name,p)
    obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj
    spec.loader.exec_module(obj);return obj
def born(seed):
    need(seed==-18000,"FIRST_USE_NOT_AUTHORIZED_AND_T7_CONSUMED")
    rng=random.Random(18181818+abs(seed)*173)
    allocated=set()
    def fresh():
        while True:
            n=rng.randrange(1,2147000000)
            if n not in allocated:allocated.add(n);return n
    corridors=[tuple(fresh() for i in range(9)) for _ in range(4)]
    roles=tuple((i%4,1) for i in range(8))
    edges=[]
    for lane in range(4):
        for i in range(8):
            edges.append((corridors[lane][i],i%4,corridors[lane][i+1]))
    # Eight cross-corridor joins: four originate at target path positions
    # with a WRONG next role, four enter target from non-target corridors.
    for i in range(8):
        j=i%8
        if i%2==0:
            edges.append((corridors[0][j],(j+1)%4,
                          corridors[1+(i%3)][(j+2)%9]))
        else:
            edges.append((corridors[1+(i%3)][j],(j+2)%4,
                          corridors[0][(j+1)%9]))
    # Sixteen incoming-to-target distractors; sixteen disconnected edges.
    for i in range(32):
        if i<16:
            edges.append((fresh(),rng.randrange(4),corridors[0][i%9]))
        else:
            edges.append((fresh(),rng.randrange(4),fresh()))
    need(len(edges)==72 and len(set(edges))==72,"NATIVE_72_EVENT_SOURCE")
    rng.shuffle(edges)
    evaluator={"start":corridors[0][0],"ops":roles,
               "answer":corridors[0][8],"fixture_only":True}
    return tuple(edges),evaluator,tuple(corridors[0])
def family_proof(events,question,target_nodes):
    # No extra same-role outgoing edges at target path state at each j.
    # This is a structural proof valid for ALL source instances that
    # satisfy our edge construction, regardless of their RNG/seed.
    for j in range(8):
        source=target_nodes[j]
        role=question["ops"][j][0]
        compatible=tuple((a,r,b) for a,r,b in events
                         if a==source and r==role)
        need(len(compatible)==1 and compatible[0][2]==target_nodes[j+1],
             "NONUNIQUE_NEXT_PUBLIC_RELATION_AT_STAGE_"+str(j))
    need(len(set(target_nodes))==9,"TARGET_PATH_NODES_DISTINCT")
    return {"certified_public_steps":8,"unique_successor_at_each_step":True,
            "proof_does_not_assume_a_specific_random_seed":True}
def relabel(events,question,target_nodes,offset):
    # Distinct bijective numeric node renaming. No model fitting/selection.
    nodes=set([x for a,r,b in events for x in (a,b)])
    ordered=sorted(nodes)
    index={v:i for i,v in enumerate(ordered)}
    # affine permutation of node indices, since multiplier is coprime with N
    n=len(ordered)
    import math
    multiplier=next(k for k in range(3,n,2) if math.gcd(k,n)==1)
    mapping={v:(index[v]*multiplier+offset)%n+1000 for v in ordered}
    transformed=tuple((mapping[a],r,mapping[b]) for a,r,b in events)
    query={"start":mapping[question["start"]],"ops":question["ops"],
           "answer":mapping[question["answer"]]}
    target=tuple(mapping[x] for x in target_nodes)
    return transformed,query,target
def preflight():
    f=json.loads(FREEZE.read_text())
    need(f["schema"]=="northstar.t8.qualified-causal-transfer-source.v1"
         and f["parent_exact_head"]=="d00c0caa6e620e689be4b72f074ceb053bf51bde"
         and f["authorization"]["prospective_source_first_use"] is False,
         "PREREGISTERED_SOURCE_PARENT")
    source,private,target=born(-18000)
    proof=family_proof(source,private,target)
    t6=load(T6,"ygg_t8_public_fullgraph")
    unique,receipt=t6.fullgraph(source,private)
    need(unique==[private["answer"]],"GENERIC_PUBLIC_GRAPH_MUST_MATCH_PROOF")
    for shift in (5,37,101):
        events,query,target2=relabel(source,private,target,shift)
        family_proof(events,query,target2)
        eps,_=t6.fullgraph(events,query)
        need(eps==[query["answer"]],"ISOMORPHIC_SOURCE_INVARIANT")
    for forbidden in (-16000,-16001,-16002,-18001,-18002,892001):
        try:born(forbidden)
        except ValueError:pass
        else:raise AssertionError("CONSUMED_OR_PROSPECTIVE_SOURCE_OPENED")
    return {"schema":"ygg.t8.inductive-unique-public-source.v1",
       "public_fixture_events":len(source),
       "proof":proof,
       "independent_node_renamings_qualified":3,
       "public_complete_endpoints":unique,
       "public_truth_uniquely_identifiable":True,
       "generic_fullgraph_candidates_examined":receipt["examined"],
       "native_original_YNS_protected_used":0,
       "T7_consumed_source_replayed":False,
       "T8_prospective_source_created":False,
       "scientific_accepted":False}
if __name__=="__main__":print(json.dumps(preflight(),sort_keys=True))
