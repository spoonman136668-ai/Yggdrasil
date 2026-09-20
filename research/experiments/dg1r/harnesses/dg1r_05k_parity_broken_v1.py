#!/usr/bin/env python3
import argparse
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

BASE_EDGES = [
    (0,2,7,9),(1,3,6,11),(4,5,9,10),(2,3,5,8),(0,1,4,8),
    (6,7,8,10),(2,4,6,11),(0,3,5,7),(1,7,10,11),(1,5,6,9),
    (3,8,9,10),(0,4,8,11),(0,2,6,10),(1,3,4,7),(2,5,7,11),
    (2,3,4,10),(0,1,5,10),(0,3,9,11),(1,2,8,9),(4,6,7,9),
]
BASE_DEG = (7,7,7,7,7,6,6,7,6,7,7,6)
BLOCKS = 12
CHECKS = 20
PLANES = 4
BASE_GLOBAL_FLOOR = 3
BASE_WEIGHT4_FALSE_EXCLUDE = 60


def columns(edges):
    out=[0]*BLOCKS
    for i,e in enumerate(edges):
        for b in e:
            out[b] |= 1 << i
    return tuple(out)


def gf2_rank(vs):
    basis={}
    for x in vs:
        v=int(x)
        while v:
            p=v.bit_length()-1
            if p in basis:
                v ^= basis[p]
            else:
                basis[p]=v
                break
    return len(basis)


def logical_syndrome(mask, cols):
    s=0
    for b in range(BLOCKS):
        if (mask >> b) & 1:
            s ^= cols[b]
    return s


def pair_max(edges):
    c=Counter()
    for e in edges:
        for a,b in itertools.combinations(e,2):
            c[tuple(sorted((a,b)))] += 1
    return max(c.values()) if c else 0


def degrees(edges):
    d=[0]*BLOCKS
    for e in edges:
        for b in e:
            d[b]+=1
    return tuple(d)


def arities(edges):
    return tuple(len(e) for e in edges)


def all_metrics(edges, include_geometry=False):
    cols=columns(edges)
    syn=[]
    by_w={w:[] for w in range(1,BLOCKS+1)}
    kernel=[]
    for mask in range(1,1<<BLOCKS):
        s=logical_syndrome(mask,cols)
        sw=s.bit_count()
        lw=mask.bit_count()
        syn.append((mask,lw,s,sw))
        by_w[lw].append(sw)
        if s==0:
            kernel.append(mask)
    single=min(cols[b].bit_count() for b in range(BLOCKS))
    pair=min((cols[a]^cols[b]).bit_count() for a,b in itertools.combinations(range(BLOCKS),2))
    pos=[sw for _,_,_,sw in syn if sw>0]
    o={
        "rank":gf2_rank(cols),
        "kernel_count":len(kernel),
        "kernel_masks":kernel,
        "max_pair_cooccurrence":pair_max(edges),
        "single_floor":single,
        "two_floor":pair,
        "global_positive_floor":min(pos) if pos else None,
        "zero_syndrome_nonzero_count":len(kernel),
    }
    if include_geometry:
        mult=Counter(s for _,_,s,_ in syn)
        mult[0] += 1
        o["distinct_syndromes"]=len(mult)
        o["multiplicity_histogram"]={str(k):int(v) for k,v in sorted(Counter(mult.values()).items())}
        o["minimum_positive_by_logical_weight"]={
            str(w): {
                "minimum":min(x for x in by_w[w] if x>0) if any(x>0 for x in by_w[w]) else None,
                "zero_syndrome_count":sum(x==0 for x in by_w[w]),
            }
            for w in range(1,BLOCKS+1)
        }
    return o


def transfer_candidate(block, src, dst):
    edges=[list(e) for e in BASE_EDGES]
    assert block in edges[src] and block not in edges[dst] and src != dst
    edges[src].remove(block)
    edges[dst].append(block)
    return tuple(tuple(sorted(e)) for e in edges)


def enumerate_candidates():
    rows=[]
    for b in range(BLOCKS):
        for i,e in enumerate(BASE_EDGES):
            if b not in e:
                continue
            for j,t in enumerate(BASE_EDGES):
                if i==j or b in t:
                    continue
                ed=transfer_candidate(b,i,j)
                ars=arities(ed)
                assert len(ed)==CHECKS
                assert sum(ars)==80
                assert degrees(ed)==BASE_DEG
                assert ars[i]==3 and ars[j]==5
                assert all(ars[k]==4 for k in range(CHECKS) if k not in (i,j))
                m=all_metrics(ed,False)
                feasible=(
                    m["rank"]==12 and
                    m["kernel_count"]==0 and
                    m["max_pair_cooccurrence"]<=2 and
                    m["single_floor"]>=6 and
                    m["two_floor"]>=8
                )
                rows.append({
                    "block":b,
                    "source_check":i,
                    "target_check":j,
                    "metrics":m,
                    "feasible":bool(feasible),
                })
    return rows


def select_candidate(rows):
    fs=[r for r in rows if r["feasible"]]
    if not fs:
        return None
    return sorted(
        fs,
        key=lambda r:(
            -r["metrics"]["global_positive_floor"],
            -r["metrics"]["two_floor"],
            -r["metrics"]["single_floor"],
            r["metrics"]["max_pair_cooccurrence"],
            r["block"],
            r["source_check"],
            r["target_check"],
        ),
    )[0]


def make_arrays(edges):
    cols=columns(edges)
    syndromes=np.asarray([logical_syndrome(mask,cols) for mask in range(1<<BLOCKS)],dtype=np.uint32)
    lw=np.asarray([mask.bit_count() for mask in range(1<<BLOCKS)],dtype=np.int16)
    pop=np.fromiter((x.bit_count() for x in range(1<<CHECKS)),dtype=np.uint8,count=1<<CHECKS)
    return cols,syndromes,lw,pop


def classify(s,true_mask,syndromes,lw,pop):
    rw=pop[np.bitwise_xor(syndromes,np.uint32(s))].astype(np.int16)
    costs=lw+rw
    mc=int(costs.min())
    mins=np.flatnonzero(costs==mc)
    inside=bool(np.any(mins==true_mask))
    if inside and len(mins)==1:
        cls="TRUE_EXPLANATION_UNIQUE_MINIMUM"
    elif inside:
        cls="TRUE_EXPLANATION_TIED_MINIMUM"
    else:
        cls="TRUE_EXPLANATION_NOT_MINIMUM"
    return {
        "classification":cls,
        "minimum_cost":mc,
        "minimum_count":int(len(mins)),
        "true_cost":int(costs[true_mask]),
    }


def check_only_boundary(edges):
    _,syndromes,lw,pop=make_arrays(edges)
    out={}
    for w in range(1,5):
        c=Counter()
        n=0
        for comb in itertools.combinations(range(CHECKS),w):
            s=sum(1<<x for x in comb)
            n+=1
            rw=pop[np.bitwise_xor(syndromes,np.uint32(s))].astype(np.int16)
            costs=lw+rw
            mc=int(costs.min())
            mins=np.flatnonzero(costs==mc)
            z=bool(np.any(mins==0))
            if z and len(mins)==1:
                c["zero_unique"]+=1
            elif z:
                c["zero_tied"]+=1
            else:
                c["all_minima_nonzero"]+=1
        out[str(w)]={
            "patterns":n,
            "zero_unique":c["zero_unique"],
            "zero_tied":c["zero_tied"],
            "all_minima_nonzero":c["all_minima_nonzero"],
        }
    return out


def incident(edges,b):
    return [i for i,e in enumerate(edges) if b in e]


def check4_tests(edges):
    _,syndromes,lw,pop=make_arrays(edges)
    out={}
    for name,b in [("CHECK4_INCIDENT_D6",5),("CHECK4_INCIDENT_D7",2)]:
        xs=incident(edges,b)[:4]
        s=sum(1<<x for x in xs)
        out[name]={
            "block":b,
            "checks":xs,
            "classification":classify(s,0,syndromes,lw,pop),
        }
    return out


def crossplane(edges):
    cols=columns(edges)
    rows=[]
    all_exact=True
    for b in range(BLOCKS):
        inc=incident(edges,b)
        check_mask=sum(1<<i for i in inc)
        for p in range(1,PLANES+1):
            eq=(cols[b]==check_mask)
            all_exact &= eq
            rows.append({
                "block":b,
                "planes":p,
                "degree":len(inc),
                "logical_fault_bit_count":p,
                "integrity_fault_bit_count":len(inc)*p,
                "integrity_channel_event_count":len(inc),
                "exact_syndrome_equality":bool(eq),
            })
    return {"rows":rows,"all_constructed_exact":bool(all_exact)}


def baseline_exact():
    assert len(BASE_EDGES)==20 and len(set(BASE_EDGES))==20
    assert degrees(BASE_EDGES)==BASE_DEG
    assert sum(arities(BASE_EDGES))==80
    assert pair_max(BASE_EDGES)==2
    m=all_metrics(BASE_EDGES,False)
    assert m["rank"]==11
    assert m["kernel_count"]==1
    assert m["kernel_masks"]==[4095]
    assert m["single_floor"]==6
    assert m["two_floor"]==8
    assert m["global_positive_floor"]==3


def run():
    baseline_exact()
    rows=enumerate_candidates()
    selected=select_candidate(rows)
    base=all_metrics(BASE_EDGES,True)
    out={
        "schema":"yggdrasil.dg1r-05k-parity-broken-topology.v1",
        "mechanical_valid":True,
        "candidate_count":len(rows),
        "feasible_count":sum(r["feasible"] for r in rows),
        "baseline":base,
        "selected":None,
        "signals":{},
        "canonical_scientific_execution":False,
        "stab18_r1_touched":False,
    }
    if selected is None:
        out["signals"]={
            "parity_broken_feasible":False,
            "selected_full_rank":False,
            "selected_kernel_free":False,
            "local_floors_preserved":False,
            "pair_cooccurrence_preserved":False,
            "global_distance_improved":False,
            "check4_equal_cost_not_worse":False,
            "crossplane_arbitrary_correlation_solved":False,
        }
        return out
    ed=transfer_candidate(selected["block"],selected["source_check"],selected["target_check"])
    sm=all_metrics(ed,True)
    hold=check_only_boundary(ed)
    base_hold=check_only_boundary(BASE_EDGES)
    c4=check4_tests(ed)
    base_c4=check4_tests(BASE_EDGES)
    cross=crossplane(ed)
    weight4=hold["4"]["all_minima_nonzero"]
    base_weight4=base_hold["4"]["all_minima_nonzero"]
    out["selected"]={
        "move":{
            "block":selected["block"],
            "source_check":selected["source_check"],
            "target_check":selected["target_check"],
        },
        "edges":[list(e) for e in ed],
        "arities":list(arities(ed)),
        "metrics":sm,
        "holdout":{
            "equal_cost_check_only_weights_1_to_4":hold,
            "baseline_equal_cost_check_only_weights_1_to_4":base_hold,
            "check4_incident":c4,
            "baseline_check4_incident":base_c4,
            "crossplane_exact_collision_lift":cross,
        },
    }
    out["signals"]={
        "parity_broken_feasible":True,
        "selected_full_rank":sm["rank"]==12,
        "selected_kernel_free":sm["kernel_count"]==0,
        "local_floors_preserved":sm["single_floor"]>=6 and sm["two_floor"]>=8,
        "pair_cooccurrence_preserved":sm["max_pair_cooccurrence"]<=2,
        "global_distance_improved":sm["global_positive_floor"]>BASE_GLOBAL_FLOOR,
        "check4_equal_cost_not_worse":weight4<=BASE_WEIGHT4_FALSE_EXCLUDE and weight4<=base_weight4,
        "crossplane_arbitrary_correlation_solved":not cross["all_constructed_exact"],
    }
    return out


def enc(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    o=run()
    raw=(enc(o)+"\n").encode("utf-8")
    Path(a.out).write_bytes(raw)
    print(enc({
        "output":a.out,
        "sha256":hashlib.sha256(raw).hexdigest(),
        "candidate_count":o["candidate_count"],
        "feasible_count":o["feasible_count"],
        "signals":o["signals"],
        "selected_move":None if o["selected"] is None else o["selected"]["move"],
        "selected_metrics":None if o["selected"] is None else o["selected"]["metrics"],
    }))


if __name__=="__main__":
    main()
