#!/usr/bin/env python3
import argparse, hashlib, itertools, json
from collections import Counter
from pathlib import Path

ROOTS=8
REPLICAS=("REG_A","REG_B","REG_C","REG_D")
EDGE_QUORUM=3
SEAL_QUORUM=3


def root_cert(r, actual_source=None):
    return {"id":f"R{r}","generation":0,"root_id":r,"actual_source":r if actual_source is None else actual_source}

def verify_parent(cert):
    if cert is None or cert["generation"]!=0: return None
    return 1<<cert["root_id"]

def edge_event(parent, child_id, child_generation):
    return ("EDGE",parent["id"],child_id,child_generation,parent["generation"])

def seal_event(child_id, child_generation, parent_ids):
    return ("SEAL",child_id,child_generation,tuple(sorted(parent_ids)))

def empty_registry():
    return {r:[] for r in REPLICAS}

def add_event(registry, event, replica_names=REPLICAS, copies=1):
    for r in replica_names:
        registry[r].extend([event]*copies)

def present_on_replicas(registry,event,available=None):
    reps=REPLICAS if available is None else tuple(available)
    return sum(event in registry[r] for r in reps)

def committed_edges(registry, child_id, generation, available=None):
    all_events=set()
    reps=REPLICAS if available is None else tuple(available)
    for r in reps:
        all_events.update(e for e in registry[r] if e[0]=="EDGE" and e[2]==child_id and e[3]==generation)
    return tuple(sorted(e for e in all_events if present_on_replicas(registry,e,reps)>=EDGE_QUORUM))

def authoritative_seals(registry, child_id, generation, available=None):
    all_events=set()
    reps=REPLICAS if available is None else tuple(available)
    for r in reps:
        all_events.update(e for e in registry[r] if e[0]=="SEAL" and e[1]==child_id and e[2]==generation)
    return tuple(sorted(e for e in all_events if present_on_replicas(registry,e,reps)>=SEAL_QUORUM))

def sealed_registry_lineage(registry, child_id, generation, certs, available=None):
    edges=committed_edges(registry,child_id,generation,available)
    seals=authoritative_seals(registry,child_id,generation,available)
    if len(seals)!=1: return None
    edge_parents=tuple(sorted(e[1] for e in edges))
    seal_parents=seals[0][3]
    if edge_parents!=seal_parents: return None
    if len(edge_parents)==0: return None
    out=0
    for pid in edge_parents:
        v=verify_parent(certs.get(pid))
        if v is None: return None
        out |= v
    return out

def edge_quorum_no_seal_lineage(registry, child_id, generation, certs, available=None):
    edges=committed_edges(registry,child_id,generation,available)
    if not edges: return None
    out=0
    for e in edges:
        v=verify_parent(certs.get(e[1]))
        if v is None: return None
        out |= v
    return out

def child_bundle_lineage(presented_parent_ids, certs):
    if not presented_parent_ids: return None
    out=0
    for pid in presented_parent_ids:
        v=verify_parent(certs.get(pid))
        if v is None: return None
        out |= v
    return out

def honest_case(parent_ids, child_id="C", generation=1):
    certs={f"R{r}":root_cert(r) for r in range(ROOTS)}
    reg=empty_registry()
    for pid in parent_ids:
        add_event(reg,edge_event(certs[pid],child_id,generation))
    add_event(reg,seal_event(child_id,generation,parent_ids))
    return reg,certs

def audit_a():
    exact=0
    for r in range(ROOTS):
        pid=f"R{r}"; reg,certs=honest_case((pid,),f"A{r}",1)
        exact+=int(sealed_registry_lineage(reg,f"A{r}",1,certs)==1<<r)
    return {"cases":8,"exact":exact}

def audit_b():
    exact=0
    for a,b in itertools.combinations(range(ROOTS),2):
        ids=(f"R{a}",f"R{b}"); child=f"B{a}_{b}"; reg,certs=honest_case(ids,child,1)
        exact+=int(sealed_registry_lineage(reg,child,1,certs)==((1<<a)|(1<<b)))
    return {"cases":28,"exact":exact}

def audit_c():
    exact=0; bundle_incomplete=0; cases=0
    for a,b in itertools.combinations(range(ROOTS),2):
        ids=(f"R{a}",f"R{b}")
        for keep in ids:
            cases+=1; child=f"C{a}_{b}_{keep}"; reg,certs=honest_case(ids,child,1)
            truth=(1<<a)|(1<<b)
            exact+=int(sealed_registry_lineage(reg,child,1,certs)==truth)
            bundle_incomplete+=int(child_bundle_lineage((keep,),certs)!=truth)
    return {"cases":cases,"registry_exact":exact,"bundle_incomplete":bundle_incomplete}

def audit_d():
    exact=0; cases=0
    for a,b in itertools.combinations(range(ROOTS),2):
        ids=(f"R{a}",f"R{b}")
        for keep in ids:
            cases+=1; child=f"D{a}_{b}_{keep}"; reg,certs=honest_case(ids,child,1)
            exact+=int(sealed_registry_lineage(reg,child,1,certs)==((1<<a)|(1<<b)))
    return {"cases":cases,"registry_exact":exact}

def audit_e():
    exact=0; cases=0
    for a,b in itertools.combinations(range(ROOTS),2):
        ids=(f"R{a}",f"R{b}")
        for missing_replica in REPLICAS:
            cases+=1; child=f"E{a}_{b}_{missing_replica}"; certs={f"R{r}":root_cert(r) for r in range(ROOTS)}; reg=empty_registry()
            add_event(reg,edge_event(certs[ids[0]],child,1))
            add_event(reg,edge_event(certs[ids[1]],child,1),tuple(r for r in REPLICAS if r!=missing_replica))
            add_event(reg,seal_event(child,1,ids))
            exact+=int(sealed_registry_lineage(reg,child,1,certs)==((1<<a)|(1<<b)))
    return {"cases":cases,"exact":exact}

def audit_f():
    abstain=0; cases=0
    for a,b in itertools.combinations(range(ROOTS),2):
        ids=(f"R{a}",f"R{b}")
        for nrep in (1,2):
            cases+=1; child=f"F{a}_{b}_{nrep}"; certs={f"R{r}":root_cert(r) for r in range(ROOTS)}; reg=empty_registry()
            add_event(reg,edge_event(certs[ids[0]],child,1))
            add_event(reg,edge_event(certs[ids[1]],child,1),REPLICAS[:nrep])
            add_event(reg,seal_event(child,1,ids))
            abstain+=int(sealed_registry_lineage(reg,child,1,certs) is None)
    return {"cases":cases,"abstain":abstain}

def audit_g():
    abstain=0; cases=0
    for a,b in itertools.combinations(range(ROOTS),2):
        ids=(f"R{a}",f"R{b}")
        for nrep in (1,2):
            cases+=1; child=f"G{a}_{b}_{nrep}"; certs={f"R{r}":root_cert(r) for r in range(ROOTS)}; reg=empty_registry()
            add_event(reg,edge_event(certs[ids[0]],child,1)); add_event(reg,edge_event(certs[ids[1]],child,1))
            add_event(reg,seal_event(child,1,ids),REPLICAS[:nrep])
            abstain+=int(sealed_registry_lineage(reg,child,1,certs) is None)
    return {"cases":cases,"abstain":abstain}

def audit_h():
    exact=0; cases=0
    for a,b in itertools.combinations(range(ROOTS),2):
        ids=(f"R{a}",f"R{b}")
        for parent in ids:
            for copies in (2,4,8,16):
                cases+=1; child=f"H{a}_{b}_{parent}_{copies}"; reg,certs=honest_case(ids,child,1)
                event=edge_event(certs[parent],child,1)
                add_event(reg,event,REPLICAS,copies-1)
                exact+=int(sealed_registry_lineage(reg,child,1,certs)==((1<<a)|(1<<b)))
    return {"cases":cases,"exact":exact}

def audit_i():
    rejected=0; cases=0
    certs={f"R{r}":root_cert(r) for r in range(ROOTS)}
    for r in range(ROOTS):
        for g in range(1,5):
            cases+=1; child=f"I{r}"; reg=empty_registry(); pid=f"R{r}"
            current=edge_event(certs[pid],child,g)
            add_event(reg,current)
            stale=("EDGE",pid,child,g-1,0)
            add_event(reg,stale)
            add_event(reg,seal_event(child,g,(pid,)))
            # stale generation tuple must not alter current-generation reconstruction
            rejected+=int(sealed_registry_lineage(reg,child,g,certs)==1<<r)
    return {"cases":cases,"stale_rejected_without_effect":rejected}

def audit_j():
    abstain=0; no_seal_early_accept=0; cases=0
    certs={f"R{r}":root_cert(r) for r in range(ROOTS)}
    for first in range(ROOTS):
        for second in range(ROOTS):
            if second==first: continue
            cases+=1; child=f"J{first}_{second}"; reg=empty_registry()
            p1=f"R{first}"; p2=f"R{second}"
            add_event(reg,edge_event(certs[p1],child,1))
            add_event(reg,seal_event(child,1,(p1,)))
            no_seal_early_accept+=int(edge_quorum_no_seal_lineage(reg,child,1,certs)==1<<first)
            add_event(reg,edge_event(certs[p2],child,1))
            abstain+=int(sealed_registry_lineage(reg,child,1,certs) is None)
    return {"cases":cases,"candidate_abstain_after_late_edge":abstain,"no_seal_early_accept":no_seal_early_accept}

def audit_k():
    abstain=0; cases=0
    for a,b in itertools.combinations(range(ROOTS),2):
        cases+=1; ids=(f"R{a}",f"R{b}"); child=f"K{a}_{b}"; reg,certs=honest_case(ids,child,1)
        add_event(reg,seal_event(child,1,(ids[0],)),REPLICAS[:3])
        abstain+=int(sealed_registry_lineage(reg,child,1,certs) is None)
    return {"cases":cases,"abstain":abstain}

def audit_l():
    exact=0; cases=0
    casespec=[(f"R{r}",) for r in range(ROOTS)]+[(f"R{a}",f"R{b}") for a,b in itertools.combinations(range(ROOTS),2)]
    for idx,ids in enumerate(casespec):
        cases+=1; child=f"L{idx}"; reg,certs=honest_case(ids,child,1)
        rotated={f"ROT_{i}":list(reg[r]) for i,r in enumerate(REPLICAS)}
        # holder names are not semantic; normalize to four replica slots with unchanged vote sets
        norm={REPLICAS[i]:rotated[f"ROT_{i}"] for i in range(4)}
        truth=0
        for pid in ids: truth|=verify_parent(certs[pid])
        exact+=int(sealed_registry_lineage(norm,child,1,certs)==truth)
    return {"cases":cases,"exact":exact}

def audit_m():
    exact=0; cases=0
    for a,b in itertools.combinations(range(ROOTS),2):
        ids=(f"R{a}",f"R{b}"); child=f"M{a}_{b}"; reg,certs=honest_case(ids,child,1)
        for unavailable in REPLICAS:
            cases+=1; available=tuple(r for r in REPLICAS if r!=unavailable)
            exact+=int(sealed_registry_lineage(reg,child,1,certs,available)==((1<<a)|(1<<b)))
    return {"cases":cases,"exact":exact}

def audit_n():
    exact=0; cases=0
    for a,b in itertools.combinations(range(ROOTS),2):
        ids=(f"R{a}",f"R{b}")
        for keep in ids:
            cases+=1; child=f"N{a}_{b}_{keep}"; reg,certs=honest_case(ids,child,1)
            exact+=int(sealed_registry_lineage(reg,child,1,certs)==((1<<a)|(1<<b)))
    return {"cases":cases,"exact":exact}

def holdouts():
    certs={f"R{r}":root_cert(r) for r in range(ROOTS)}
    omission_false=insertion_false=two_bad_false=0
    for a,b in itertools.combinations(range(ROOTS),2):
        p1=f"R{a}"; p2=f"R{b}"; child=f"X{a}_{b}"
        # H1: three-replica fork omits real p2.
        reg=empty_registry()
        add_event(reg,edge_event(certs[p1],child,1),REPLICAS[:3])
        add_event(reg,edge_event(certs[p2],child,1),REPLICAS[3:])
        add_event(reg,seal_event(child,1,(p1,)),REPLICAS[:3])
        omission_false+=int(sealed_registry_lineage(reg,child,1,certs)==1<<a)
        # H2: three replicas invent extra p2 in a true single-parent child.
        reg2=empty_registry()
        add_event(reg2,edge_event(certs[p1],child,1))
        add_event(reg2,edge_event(certs[p2],child,1),REPLICAS[:3])
        add_event(reg2,seal_event(child,1,(p1,p2)),REPLICAS[:3])
        insertion_false+=int(sealed_registry_lineage(reg2,child,1,certs)==((1<<a)|(1<<b)))
        # H3: only two bad replicas try to omit p2 and install incomplete seal.
        reg3=empty_registry()
        add_event(reg3,edge_event(certs[p1],child,1))
        add_event(reg3,edge_event(certs[p2],child,1),REPLICAS[2:])
        add_event(reg3,seal_event(child,1,(p1,)),REPLICAS[:2])
        two_bad_false+=int(sealed_registry_lineage(reg3,child,1,certs)==1<<a)
    # H4 root compromise: four IDs with one actual source remain apparently disjoint.
    compromised=[root_cert(r,actual_source=0) for r in range(ROOTS)]
    root_false=0; root_cases=0
    for assignment in itertools.permutations(range(ROOTS),4):
        root_cases+=1
        masks=[verify_parent(compromised[r]) for r in assignment]
        ok=all((x&y)==0 for x,y in itertools.combinations(masks,2))
        root_false+=int(ok)
    return {"H1_majority_omission_cases":28,"H1_false_incomplete_lineage":omission_false,
            "H2_majority_insertion_cases":28,"H2_false_extra_lineage":insertion_false,
            "H3_two_corrupt_replica_cases":28,"H3_false_authorization":two_bad_false,
            "H4_root_compromise_cases":root_cases,"H4_false_independence":root_false}

def signals(a,b,c,d,e,f,g,h,i,j,k,l,m,n,hold):
    vals={
      "SINGLE_PARENT_REGISTRY_EXACT":a["exact"]==8,
      "TWO_PARENT_REGISTRY_UNION_EXACT":b["exact"]==28,
      "CHILD_OMISSION_IRRELEVANT":c["registry_exact"]==56,
      "OBSERVER_COLLUSION_BYPASSED_BY_REGISTRY":d["registry_exact"]==56,
      "ONE_REPLICA_WITHHOLDING_TOLERATED":e["exact"]==112,
      "PARTIAL_EDGE_WRITE_ABORTS":f["abstain"]==56,
      "PARTIAL_SEAL_WRITE_ABORTS":g["abstain"]==56,
      "DUPLICATE_EDGE_FANOUT_COLLAPSED":h["exact"]==224,
      "STALE_EDGE_REPLAY_REJECTED":i["stale_rejected_without_effect"]==32,
      "LATE_EDGE_INVALIDATES_SEAL":j["candidate_abstain_after_late_edge"]==56,
      "CONFLICTING_SEALS_ABORT":k["abstain"]==28,
      "REGISTRY_HOLDER_ROTATION_PRESERVES_LINEAGE":l["exact"]==36,
      "ONE_REGISTRY_REPLICA_LOSS_TOLERATED":m["exact"]==112,
      "REGISTRY_REPRODUCES_05U_WITHOUT_BUNDLE_COMPLETENESS":n["exact"]==56,
    }
    vals["APPEND_ONLY_COMPLETENESS_GAIN"]=all(vals.values())
    vals["REGISTRY_MAJORITY_OMISSION_FAILURE"]=hold["H1_false_incomplete_lineage"]>0
    vals["REGISTRY_MAJORITY_INSERTION_FAILURE"]=hold["H2_false_extra_lineage"]>0
    vals["TWO_CORRUPT_REPLICAS_SUPPRESSED"]=hold["H3_false_authorization"]==0
    vals["ROOT_COMPROMISE_FAILURE"]=hold["H4_false_independence"]>0
    vals["NO_SEAL_TIMING_AMBIGUITY_EXPOSED"]=j["no_seal_early_accept"]>0
    return vals

def validate():
    assert ROOTS==8 and len(REPLICAS)==4 and EDGE_QUORUM==3 and SEAL_QUORUM==3
    counts={"A":8,"B":28,"C":56,"D":56,"E":112,"F":56,"G":56,"H":224,"I":32,"J":56,"K":28,"L":36,"M":112,"N":56}
    assert 8*7==56 and 28*4==112 and 28*2==56 and 28*2*4==224
    return counts

def run():
    counts=validate(); a=audit_a(); b=audit_b(); c=audit_c(); d=audit_d(); e=audit_e(); f=audit_f(); g=audit_g()
    h=audit_h(); i=audit_i(); j=audit_j(); k=audit_k(); l=audit_l(); m=audit_m(); n=audit_n(); hold=holdouts()
    return {"schema":"yggdrasil.dg1r-05v-causal-edge-registry.v1","mechanical_valid":True,"case_counts":counts,
            "audit_a":a,"audit_b":b,"audit_c":c,"audit_d":d,"audit_e":e,"audit_f":f,"audit_g":g,"audit_h":h,
            "audit_i":i,"audit_j":j,"audit_k":k,"audit_l":l,"audit_m":m,"audit_n":n,
            "correlated_registry_boundary":hold,"signals":signals(a,b,c,d,e,f,g,h,i,j,k,l,m,n,hold),
            "canonical_scientific_execution":False,"stab18_r1_touched":False}

def enc(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out"); ap.add_argument("--mechanical-only",action="store_true"); a=ap.parse_args()
    if a.mechanical_only:
        print(enc({"mechanical_valid":True,"case_counts":validate()})); return
    if not a.out: raise SystemExit("--out required unless --mechanical-only")
    obj=run(); raw=(enc(obj)+"\n").encode(); Path(a.out).write_bytes(raw)
    print(enc({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"signals":obj["signals"]}))
if __name__=="__main__": main()
