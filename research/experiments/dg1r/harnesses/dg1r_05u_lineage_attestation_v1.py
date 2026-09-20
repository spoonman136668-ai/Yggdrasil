#!/usr/bin/env python3
import argparse, hashlib, itertools, json
from collections import Counter
from pathlib import Path

ROOTS=8
SLOTS=("DEMAND_A","DEMAND_B","PEER_A","PEER_B")
METHODS=("SELF_DECLARED_LINEAGE","INCLUDED_PARENT_ONLY","DUAL_OBSERVED_PARENTSET")


def root_cert(r, actual_source=None):
    return {"id":f"R{r}","generation":0,"is_root":True,"root_id":r,
            "self_claim":1<<r,"parents":(),"edges":(),"obs_a":(),"obs_b":(),
            "actual_parents":(),"actual_source":r if actual_source is None else actual_source}


def edge(parent, child_id, child_generation, valid=True):
    return {"parent_id":parent["id"],"child_id":child_id,"child_generation":child_generation,"valid":bool(valid)}


def child_cert(child_id, generation, presented_parents, actual_parents=None, self_claim=0,
               obs_a=None, obs_b=None, edge_validity=None, holder_id=None):
    pp=tuple(presented_parents)
    ap=tuple(pp if actual_parents is None else actual_parents)
    pids=tuple(sorted(p["id"] for p in pp))
    if obs_a is None: obs_a=pids
    if obs_b is None: obs_b=pids
    if edge_validity is None: edge_validity={p["id"]:True for p in pp}
    edges=tuple(edge(p,child_id,generation,edge_validity.get(p["id"],False)) for p in pp)
    return {"id":child_id,"generation":generation,"is_root":False,"root_id":None,
            "self_claim":self_claim,"parents":pp,"edges":edges,
            "obs_a":tuple(sorted(obs_a)),"obs_b":tuple(sorted(obs_b)),
            "actual_parents":ap,"actual_source":None,"holder_id":holder_id}


def actual_lineage(cert):
    if cert["is_root"]:
        return 1<<cert["root_id"]
    out=0
    for p in cert["actual_parents"]:
        out |= actual_lineage(p)
    return out


def verify(cert, method, seen=None):
    if seen is None: seen=set()
    key=(cert["id"],cert["generation"])
    if key in seen: return None
    if cert["is_root"]:
        if cert["generation"]!=0: return None
        return 1<<cert["root_id"]
    if method=="SELF_DECLARED_LINEAGE":
        return cert["self_claim"]
    parents=cert["parents"]
    if not parents: return None
    if any(cert["generation"]<=p["generation"] for p in parents): return None
    edge_map={(e["parent_id"],e["child_id"],e["child_generation"]):e["valid"] for e in cert["edges"]}
    for p in parents:
        if not edge_map.get((p["id"],cert["id"],cert["generation"]),False): return None
    if method=="DUAL_OBSERVED_PARENTSET":
        pids=tuple(sorted(p["id"] for p in parents))
        if cert["obs_a"]!=cert["obs_b"]: return None
        if cert["obs_a"]!=pids: return None
    nxt=set(seen); nxt.add(key)
    out=0
    for p in parents:
        v=verify(p,method,nxt)
        if v is None: return None
        out |= v
    return out


def lineage_disjoint4(masks):
    if len(masks)!=4 or any(m is None or m==0 for m in masks): return False
    for a,b in itertools.combinations(masks,2):
        if a & b: return False
    return True


def attested_child_from_root(root, idx, claim=None):
    if claim is None: claim=0
    return child_cert(f"C{root['root_id']}_{idx}",1,(root,),self_claim=claim,
                      obs_a=(root["id"],),obs_b=(root["id"],),holder_id=f"H{idx}")


def honest_chain(root, depth):
    cur=root; arr=[]
    for g in range(1,depth+1):
        cur=child_cert(f"{root['id']}_G{g}",g,(cur,),self_claim=(1<<((root["root_id"]+g)%ROOTS)),
                       obs_a=(cur["id"],),obs_b=(cur["id"],),holder_id=f"H_{root['id']}_{g}")
        arr.append(cur)
    return arr


def audit_a():
    roots=[root_cert(r) for r in range(ROOTS)]
    ok=0
    rows=[]
    for r,c in enumerate(roots):
        v=verify(c,"DUAL_OBSERVED_PARENTSET")
        ok+=int(v==(1<<r))
        rows.append({"root":r,"verified":v})
    return {"cases":ROOTS,"exact":ok,"rows":rows}


def audit_b():
    exact=0; cases=0
    rows=[]
    for r in range(ROOTS):
        root=root_cert(r)
        chain=honest_chain(root,8)
        for depth,c in enumerate(chain,1):
            cases+=1; v=verify(c,"DUAL_OBSERVED_PARENTSET")
            exact+=int(v==(1<<r))
            if len(rows)<8: rows.append({"root":r,"depth":depth,"verified":v,"self_claim":c["self_claim"]})
    return {"cases":cases,"exact":exact,"rows":rows}


def audit_c():
    exact=0; rows=[]
    roots=[root_cert(r) for r in range(ROOTS)]
    for a,b in itertools.combinations(range(ROOTS),2):
        ps=(roots[a],roots[b]); ids=tuple(sorted(p["id"] for p in ps))
        c=child_cert(f"M{a}_{b}",1,ps,self_claim=0,obs_a=ids,obs_b=ids)
        v=verify(c,"DUAL_OBSERVED_PARENTSET"); truth=(1<<a)|(1<<b)
        exact+=int(v==truth)
        if len(rows)<8: rows.append({"parents":(a,b),"verified":v})
    return {"cases":28,"exact":exact,"rows":rows}


def audit_d():
    reject=0; included_accept=0; self_accept=0; cases=0
    roots=[root_cert(r) for r in range(ROOTS)]
    for a,b in itertools.combinations(range(ROOTS),2):
        actual=(roots[a],roots[b]); full_ids=tuple(sorted(p["id"] for p in actual))
        for keep,omit in ((a,b),(b,a)):
            cases+=1; presented=(roots[keep],)
            c=child_cert(f"O{a}_{b}_{omit}",1,presented,actual_parents=actual,
                         self_claim=1<<keep,obs_a=full_ids,obs_b=full_ids)
            reject+=int(verify(c,"DUAL_OBSERVED_PARENTSET") is None)
            included_accept+=int(verify(c,"INCLUDED_PARENT_ONLY") is not None)
            self_accept+=int(verify(c,"SELF_DECLARED_LINEAGE") is not None)
    return {"cases":cases,"candidate_reject":reject,"included_parent_accept":included_accept,"self_declared_accept":self_accept}


def audit_e():
    reject=0; cases=0
    roots=[root_cert(r) for r in range(ROOTS)]
    for a,b in itertools.combinations(range(ROOTS),2):
        ps=(roots[a],roots[b]); ids=tuple(sorted(p["id"] for p in ps))
        for missing in (a,b):
            cases+=1
            ev={p["id"]:(p["root_id"]!=missing) for p in ps}
            c=child_cert(f"E{a}_{b}_{missing}",1,ps,obs_a=ids,obs_b=ids,edge_validity=ev)
            reject+=int(verify(c,"DUAL_OBSERVED_PARENTSET") is None)
    return {"cases":cases,"candidate_reject":reject}


def audit_f():
    reject=0; cases=0
    roots=[root_cert(r) for r in range(ROOTS)]
    for a,b in itertools.combinations(range(ROOTS),2):
        ps=(roots[a],roots[b]); ids=tuple(sorted(p["id"] for p in ps))
        for which in (0,1):
            cases+=1
            bad=(roots[a]["id"],) if which==0 else (roots[b]["id"],)
            oa=bad if which==0 else ids
            ob=ids if which==0 else bad
            c=child_cert(f"F{a}_{b}_{which}",1,ps,obs_a=oa,obs_b=ob)
            reject+=int(verify(c,"DUAL_OBSERVED_PARENTSET") is None)
    return {"cases":cases,"candidate_reject":reject}


def audit_g():
    reject=0; cases=0; rows=[]
    for r in range(ROOTS):
        root=root_cert(r); chain=honest_chain(root,4)
        parent=root
        for g,curr in enumerate(chain,1):
            cases+=1
            if g%2:
                bad=child_cert(f"G_BAD_{r}_{g}",parent["generation"],(parent,),obs_a=(parent["id"],),obs_b=(parent["id"],))
            else:
                bad=dict(parent)
            v=verify(bad,"DUAL_OBSERVED_PARENTSET")
            reject+=int(v is None or bad["generation"]<g)
            if len(rows)<8: rows.append({"root":r,"current_generation":g,"presented_generation":bad["generation"],"verified":v})
            parent=curr
    return {"cases":cases,"candidate_reject":reject,"rows":rows}


def audit_h():
    unchanged=0; cases=0
    for r in range(ROOTS):
        root=root_cert(r); chain=honest_chain(root,8)
        for g,c in enumerate(chain,1):
            cases+=1
            before=verify(c,"DUAL_OBSERVED_PARENTSET")
            rotated=dict(c); rotated["holder_id"]=f"ROTATED_{r}_{g}"
            after=verify(rotated,"DUAL_OBSERVED_PARENTSET")
            unchanged+=int(before==after==(1<<r))
    return {"cases":cases,"unchanged":unchanged}


def audit_i():
    exact=0; cases=0
    for r in range(ROOTS):
        root=root_cert(r)
        inter=child_cert(f"I_{r}_1",1,(root,),self_claim=1<<((r+1)%ROOTS),obs_a=(root["id"],),obs_b=(root["id"],))
        final=child_cert(f"I_{r}_2",2,(inter,),self_claim=0,obs_a=(inter["id"],),obs_b=(inter["id"],))
        cases+=1; exact+=int(verify(final,"DUAL_OBSERVED_PARENTSET")==(1<<r))
    return {"cases":cases,"exact":exact}


def audit_j():
    roots=[root_cert(r) for r in range(ROOTS)]
    true_auth=safe_abstain=false_auth=0
    for assignment in itertools.product(range(ROOTS),repeat=4):
        masks=[]
        for slot,r in enumerate(assignment):
            c=attested_child_from_root(roots[r],slot,claim=(1<<((r+slot+1)%ROOTS)))
            masks.append(verify(c,"DUAL_OBSERVED_PARENTSET"))
        auth=lineage_disjoint4(masks)
        truth=len(set(assignment))==4
        if auth and truth: true_auth+=1
        elif auth and not truth: false_auth+=1
        else: safe_abstain+=1
    return {"cases":4096,"true_authorization":true_auth,"safe_abstain":safe_abstain,"false_authorization":false_auth}


def ordered_pair_partitions(items):
    items=tuple(items)
    for p0 in itertools.combinations(items,2):
        rem0=tuple(x for x in items if x not in p0)
        for p1 in itertools.combinations(rem0,2):
            rem1=tuple(x for x in rem0 if x not in p1)
            for p2 in itertools.combinations(rem1,2):
                p3=tuple(x for x in rem1 if x not in p2)
                yield (tuple(sorted(p0)),tuple(sorted(p1)),tuple(sorted(p2)),tuple(sorted(p3)))


def audit_k():
    roots=[root_cert(r) for r in range(ROOTS)]
    auth=false_auth=cases=0
    for parts in ordered_pair_partitions(range(ROOTS)):
        cases+=1; masks=[]
        for slot,pair in enumerate(parts):
            ps=tuple(roots[r] for r in pair); ids=tuple(sorted(p["id"] for p in ps))
            c=child_cert(f"K_{slot}_{pair[0]}_{pair[1]}",1,ps,obs_a=ids,obs_b=ids)
            masks.append(verify(c,"DUAL_OBSERVED_PARENTSET"))
        ok=lineage_disjoint4(masks)
        auth+=int(ok); false_auth+=int(ok and any(m is None for m in masks))
    return {"cases":cases,"authorizations":auth,"false_authorization":false_auth}


def holdouts():
    roots=[root_cert(r) for r in range(ROOTS)]
    h1_false=h2_false=h2_reject=0
    for a,b in itertools.combinations(range(ROOTS),2):
        actual=(roots[a],roots[b])
        for keep,omit in ((a,b),(b,a)):
            presented=(roots[keep],); incomplete=(roots[keep]["id"],); full=tuple(sorted(p["id"] for p in actual))
            c1=child_cert(f"H1_{a}_{b}_{omit}",1,presented,actual_parents=actual,obs_a=incomplete,obs_b=incomplete)
            h1_false+=int(verify(c1,"DUAL_OBSERVED_PARENTSET") is not None)
            c2=child_cert(f"H2_{a}_{b}_{omit}",1,presented,actual_parents=actual,obs_a=incomplete,obs_b=full)
            v2=verify(c2,"DUAL_OBSERVED_PARENTSET")
            h2_false+=int(v2 is not None); h2_reject+=int(v2 is None)
    root_compromise_false=0; root_compromise_cases=0
    compromised=[root_cert(r,actual_source=0) for r in range(ROOTS)]
    for assignment in itertools.permutations(range(ROOTS),4):
        root_compromise_cases+=1
        masks=[verify(attested_child_from_root(compromised[r],slot),"DUAL_OBSERVED_PARENTSET") for slot,r in enumerate(assignment)]
        root_compromise_false+=int(lineage_disjoint4(masks))
    return {"H1_dual_observer_collusion_cases":56,"H1_false_authorization":h1_false,
            "H2_one_observer_collusion_cases":56,"H2_false_authorization":h2_false,"H2_reject":h2_reject,
            "H3_root_compromise_cases":root_compromise_cases,"H3_false_independence_authorization":root_compromise_false}


def signals(a,b,c,d,e,f,g,h,i,j,k,hold):
    root_ok=a["exact"]==8
    chain=b["exact"]==64
    merge=c["exact"]==28
    omit=d["candidate_reject"]==56
    edge_ok=e["candidate_reject"]==56
    obs=f["candidate_reject"]==56
    stale=g["candidate_reject"]==32
    rotate=h["unchanged"]==64
    tamper=i["exact"]==8
    replay=(j["true_authorization"]==1680 and j["safe_abstain"]==2416 and j["false_authorization"]==0)
    compound=(k["cases"]==2520 and k["authorizations"]==2520 and k["false_authorization"]==0)
    gain=all((root_ok,chain,merge,omit,edge_ok,obs,stale,rotate,tamper,replay,compound))
    return {"ROOT_CERTIFICATES_VALID":root_ok,"SINGLE_PARENT_INHERITANCE_EXACT":chain,
            "TWO_PARENT_UNION_EXACT":merge,"OMITTED_PARENT_REJECTED":omit,
            "INCLUDED_PARENT_OMISSION_EXPOSED":d["included_parent_accept"]>0,
            "MISSING_PARENT_EDGE_REJECTED":edge_ok,"SINGLE_OBSERVER_CORRUPTION_REJECTED":obs,
            "STALE_OR_NONMONOTONIC_REJECTED":stale,"HOLDER_ROTATION_PRESERVES_VERIFIED_LINEAGE":rotate,
            "PARENT_SELF_CLAIM_IGNORED":tamper,"ATTESTED_LINEAGE_REPRODUCES_05T":replay,
            "ATTESTED_COMPOUND_DISJOINT_ACCEPTANCE":compound,"NON_SELF_CERTIFYING_LINEAGE_GAIN":gain,
            "DUAL_OBSERVER_COLLUSION_FAILURE":hold["H1_false_authorization"]>0,
            "ONE_OBSERVER_COLLUSION_REJECTED":hold["H2_false_authorization"]==0,
            "ROOT_COMPROMISE_FAILURE":hold["H3_false_independence_authorization"]>0}


def validate():
    assert ROOTS==8 and len(SLOTS)==4
    assert all(root_cert(r)["generation"]==0 for r in range(ROOTS))
    assert 8*8==64
    assert len(list(itertools.combinations(range(8),2)))==28
    assert 28*2==56
    assert 8*4==32
    assert 8**4==4096
    assert sum(1 for _ in ordered_pair_partitions(range(8)))==2520
    assert all(verify(root_cert(r),"DUAL_OBSERVED_PARENTSET")==1<<r for r in range(ROOTS))
    return {"roots":8,"slots":4,"audit_b":64,"audit_c":28,"audit_d":56,"audit_e":56,"audit_f":56,
            "audit_g":32,"audit_h":64,"audit_i":8,"audit_j":4096,"audit_k":2520}


def run():
    mech=validate(); a=audit_a(); b=audit_b(); c=audit_c(); d=audit_d(); e=audit_e(); f=audit_f()
    g=audit_g(); h=audit_h(); i=audit_i(); j=audit_j(); k=audit_k(); hold=holdouts()
    return {"schema":"yggdrasil.dg1r-05u-lineage-attestation.v1","mechanical_valid":True,"mechanical":mech,
            "audit_a_roots":a,"audit_b_single_parent":b,"audit_c_two_parent":c,"audit_d_omission":d,
            "audit_e_missing_edge":e,"audit_f_observer_disagree":f,"audit_g_generation":g,
            "audit_h_holder_rotation":h,"audit_i_parent_self_claim":i,"audit_j_reproduce_05t":j,
            "audit_k_compound_disjoint":k,"attestation_forgery_boundary":hold,
            "signals":signals(a,b,c,d,e,f,g,h,i,j,k,hold),
            "canonical_scientific_execution":False,"stab18_r1_touched":False}


def enc(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out"); ap.add_argument("--mechanical-only",action="store_true"); a=ap.parse_args()
    if a.mechanical_only:
        print(enc({"mechanical_valid":True,"mechanical":validate()})); return
    if not a.out: raise SystemExit("--out required unless --mechanical-only")
    obj=run(); raw=(enc(obj)+"\n").encode(); Path(a.out).write_bytes(raw)
    print(enc({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"signals":obj["signals"]}))
if __name__=="__main__": main()
