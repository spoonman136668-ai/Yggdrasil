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
BASE_DEG=(7,7,7,7,7,6,6,7,6,7,7,6)
BLOCKS=12
CHECKS=20
PLANES=4
BASE_GLOBAL_FLOOR=3
BASE_WEIGHT4_FALSE_EXCLUDE=60
K05_MOVE=(5,3,6)


def normalize_edges(edges):
    return tuple(tuple(sorted(e)) for e in edges)


def columns(edges):
    out=[0]*BLOCKS
    for i,e in enumerate(edges):
        for b in e: out[b] |= 1<<i
    return tuple(out)


def degrees(edges):
    d=[0]*BLOCKS
    for e in edges:
        for b in e: d[b]+=1
    return tuple(d)


def arities(edges): return tuple(len(e) for e in edges)


def pair_max(edges):
    c=Counter()
    for e in edges:
        for a,b in itertools.combinations(e,2): c[tuple(sorted((a,b)))]+=1
    return max(c.values()) if c else 0


def gf2_rank(vs):
    basis={}
    for x in vs:
        v=int(x)
        while v:
            p=v.bit_length()-1
            if p in basis: v ^= basis[p]
            else:
                basis[p]=v
                break
    return len(basis)


def logical_syndromes(cols):
    syn=[0]*(1<<BLOCKS)
    for m in range(1,1<<BLOCKS):
        lsb=m & -m
        b=lsb.bit_length()-1
        syn[m]=syn[m^lsb]^cols[b]
    return syn


def atomic_moves():
    out=[]
    for b in range(BLOCKS):
        for i,e in enumerate(BASE_EDGES):
            if b not in e: continue
            for j,t in enumerate(BASE_EDGES):
                if i==j or b in t: continue
                out.append((b,i,j))
    return tuple(out)


def apply_pair(m1,m2):
    b1,i1,j1=m1; b2,i2,j2=m2
    assert len({i1,j1,i2,j2})==4
    edges=[list(e) for e in BASE_EDGES]
    for b,i,j in (m1,m2):
        assert b in edges[i]
        assert b not in edges[j]
        edges[i].remove(b)
        edges[j].append(b)
    ed=normalize_edges(edges)
    ars=arities(ed)
    assert len(ed)==CHECKS
    assert sum(ars)==80
    assert degrees(ed)==BASE_DEG
    assert sum(x==3 for x in ars)==2
    assert sum(x==5 for x in ars)==2
    assert sum(x==4 for x in ars)==16
    return ed


def candidate_family():
    moves=atomic_moves()
    seen={}
    structural_pairs=0
    for a in range(len(moves)):
        m1=moves[a]
        for b in range(a+1,len(moves)):
            m2=moves[b]
            if len({m1[1],m1[2],m2[1],m2[2]})!=4: continue
            structural_pairs+=1
            ed=apply_pair(m1,m2)
            witness=tuple(sorted((m1,m2)))
            old=seen.get(ed)
            if old is None or witness<old: seen[ed]=witness
    return moves,structural_pairs,seen


def topology_primary(edges):
    cols=columns(edges)
    rank=gf2_rank(cols)
    pm=pair_max(edges)
    single=min(c.bit_count() for c in cols)
    two=min((cols[a]^cols[b]).bit_count() for a,b in itertools.combinations(range(BLOCKS),2))
    if rank<12:
        return {'rank':rank,'kernel_count':(1<<(BLOCKS-rank))-1,'max_pair_cooccurrence':pm,'single_floor':single,'two_floor':two,'global_positive_floor':None,'global_evaluated':False}
    if pm>2 or single<6 or two<8:
        return {'rank':rank,'kernel_count':0,'max_pair_cooccurrence':pm,'single_floor':single,'two_floor':two,'global_positive_floor':None,'global_evaluated':False}
    syn=logical_syndromes(cols)
    g=min(x.bit_count() for x in syn[1:])
    return {'rank':rank,'kernel_count':0,'max_pair_cooccurrence':pm,'single_floor':single,'two_floor':two,'global_positive_floor':g,'global_evaluated':True}


def enumerate_primary():
    moves,structural_pairs,seen=candidate_family()
    rows=[]
    global_eval_count=0
    for ed,witness in sorted(seen.items(),key=lambda kv:kv[1]):
        m=topology_primary(ed)
        global_eval_count += int(m['global_evaluated'])
        feasible=(m['rank']==12 and m['kernel_count']==0 and m['max_pair_cooccurrence']<=2 and m['single_floor']>=6 and m['two_floor']>=8 and m['global_positive_floor'] is not None and m['global_positive_floor']>=3)
        rows.append({'witness':[list(x) for x in witness],'metrics':m,'frontier_feasible':bool(feasible),'edges':ed})
    return moves,structural_pairs,seen,rows,global_eval_count


def select_candidate(rows):
    fs=[r for r in rows if r['frontier_feasible']]
    if not fs: return None
    return sorted(fs,key=lambda r:(-r['metrics']['global_positive_floor'],-r['metrics']['two_floor'],-r['metrics']['single_floor'],r['metrics']['max_pair_cooccurrence'],tuple(tuple(x) for x in r['witness'])))[0]


def geometry(edges):
    cols=columns(edges); syn=logical_syndromes(cols)
    mult=Counter(syn); by_w={w:[] for w in range(1,BLOCKS+1)}
    kernel=[]
    for m in range(1,1<<BLOCKS):
        sw=syn[m].bit_count(); by_w[m.bit_count()].append(sw)
        if syn[m]==0: kernel.append(m)
    return {
        'rank':gf2_rank(cols),
        'kernel_masks':kernel,
        'distinct_syndromes':len(mult),
        'multiplicity_histogram':{str(k):int(v) for k,v in sorted(Counter(mult.values()).items())},
        'single_floor':min(c.bit_count() for c in cols),
        'two_floor':min((cols[a]^cols[b]).bit_count() for a,b in itertools.combinations(range(BLOCKS),2)),
        'global_positive_floor':min(s.bit_count() for s in syn[1:] if s),
        'max_pair_cooccurrence':pair_max(edges),
        'minimum_positive_by_logical_weight':{str(w):{'minimum':min((x for x in by_w[w] if x>0),default=None),'zero_syndrome_count':sum(x==0 for x in by_w[w])} for w in range(1,BLOCKS+1)},
    }


def make_arrays(edges):
    cols=columns(edges)
    syndromes=np.asarray(logical_syndromes(cols),dtype=np.uint32)
    lw=np.asarray([m.bit_count() for m in range(1<<BLOCKS)],dtype=np.int16)
    pop=np.fromiter((x.bit_count() for x in range(1<<CHECKS)),dtype=np.uint8,count=1<<CHECKS)
    return syndromes,lw,pop


def check_only_boundary(edges):
    syn,lw,pop=make_arrays(edges); out={}
    for w in range(1,5):
        c=Counter(); n=0
        for comb in itertools.combinations(range(CHECKS),w):
            s=sum(1<<x for x in comb); n+=1
            rw=pop[np.bitwise_xor(syn,np.uint32(s))].astype(np.int16)
            costs=lw+rw; mc=int(costs.min()); mins=np.flatnonzero(costs==mc); z=bool(np.any(mins==0))
            if z and len(mins)==1: c['zero_unique']+=1
            elif z: c['zero_tied']+=1
            else: c['all_minima_nonzero']+=1
        assert n==math.comb(CHECKS,w)
        out[str(w)]={'patterns':n,'zero_unique':int(c['zero_unique']),'zero_tied':int(c['zero_tied']),'all_minima_nonzero':int(c['all_minima_nonzero'])}
    return out


def classify(s,true_mask,syn,lw,pop):
    rw=pop[np.bitwise_xor(syn,np.uint32(s))].astype(np.int16); costs=lw+rw
    mc=int(costs.min()); mins=np.flatnonzero(costs==mc); inside=bool(np.any(mins==true_mask))
    if inside and len(mins)==1: cls='TRUE_EXPLANATION_UNIQUE_MINIMUM'
    elif inside: cls='TRUE_EXPLANATION_TIED_MINIMUM'
    else: cls='TRUE_EXPLANATION_NOT_MINIMUM'
    return {'classification':cls,'minimum_cost':mc,'minimum_count':int(len(mins)),'true_cost':int(costs[true_mask])}


def incident(edges,b): return [i for i,e in enumerate(edges) if b in e]


def check4_tests(edges):
    syn,lw,pop=make_arrays(edges); out={}
    for name,b in [('CHECK4_INCIDENT_D6',5),('CHECK4_INCIDENT_D7',2)]:
        xs=incident(edges,b)[:4]; s=sum(1<<x for x in xs)
        out[name]={'block':b,'checks':xs,'classification':classify(s,0,syn,lw,pop)}
    return out


def crossplane(edges):
    cols=columns(edges); rows=[]; all_exact=True
    for b in range(BLOCKS):
        inc=incident(edges,b); cm=sum(1<<i for i in inc)
        for p in range(1,PLANES+1):
            eq=cols[b]==cm; all_exact &= eq
            rows.append({'block':b,'planes':p,'degree':len(inc),'logical_fault_bit_count':p,'integrity_fault_bit_count':len(inc)*p,'integrity_channel_event_count':len(inc),'exact_syndrome_equality':bool(eq)})
    return {'rows':rows,'all_constructed_exact':bool(all_exact)}


def k05_edges():
    b,i,j=K05_MOVE
    e=[list(x) for x in BASE_EDGES]; e[i].remove(b); e[j].append(b)
    return normalize_edges(e)


def validate_baselines():
    assert len(BASE_EDGES)==20 and len(set(BASE_EDGES))==20
    assert sum(arities(BASE_EDGES))==80 and degrees(BASE_EDGES)==BASE_DEG and pair_max(BASE_EDGES)==2
    g=geometry(BASE_EDGES)
    assert g['rank']==11 and g['kernel_masks']==[4095] and g['single_floor']==6 and g['two_floor']==8 and g['global_positive_floor']==3
    kg=geometry(k05_edges())
    assert kg['rank']==12 and kg['kernel_masks']==[] and kg['single_floor']==6 and kg['two_floor']==8 and kg['global_positive_floor']==2 and kg['max_pair_cooccurrence']==2


def run():
    validate_baselines()
    moves,structural_pairs,seen,rows,global_eval_count=enumerate_primary()
    selected=select_candidate(rows)
    out={
        'schema':'yggdrasil.dg1r-05l-topology-distance-frontier.v1',
        'mechanical_valid':True,
        'atomic_move_count':len(moves),
        'structural_pair_count':structural_pairs,
        'unique_topology_count':len(seen),
        'global_distance_evaluated_count':global_eval_count,
        'frontier_feasible_count':sum(r['frontier_feasible'] for r in rows),
        'baseline':geometry(BASE_EDGES),
        'k05_selected':geometry(k05_edges()),
        'selected':None,
        'signals':{},
        'canonical_scientific_execution':False,
        'stab18_r1_touched':False,
    }
    if selected is None:
        out['signals']={
            'distance_frontier_feasible':False,'selected_full_rank':False,'selected_kernel_free':False,
            'local_floors_preserved':False,'pair_cooccurrence_preserved':False,
            'global_distance_at_least_baseline':False,'global_distance_improved_over_baseline':False,
            'check4_equal_cost_not_worse':False,'crossplane_arbitrary_correlation_solved':False,
        }
        return out
    ed=tuple(tuple(x) for x in selected['edges'])
    sm=geometry(ed); hold=check_only_boundary(ed); base_hold=check_only_boundary(BASE_EDGES); k_hold=check_only_boundary(k05_edges())
    c4=check4_tests(ed); base_c4=check4_tests(BASE_EDGES); k_c4=check4_tests(k05_edges()); cross=crossplane(ed)
    out['selected']={
        'witness':selected['witness'],'edges':[list(e) for e in ed],'arities':list(arities(ed)),'metrics':sm,
        'holdout':{
            'equal_cost_check_only_weights_1_to_4':hold,
            'baseline_equal_cost_check_only_weights_1_to_4':base_hold,
            'k05_equal_cost_check_only_weights_1_to_4':k_hold,
            'check4_incident':c4,'baseline_check4_incident':base_c4,'k05_check4_incident':k_c4,
            'crossplane_exact_collision_lift':cross,
        },
    }
    w4=hold['4']['all_minima_nonzero']
    out['signals']={
        'distance_frontier_feasible':True,
        'selected_full_rank':sm['rank']==12,
        'selected_kernel_free':len(sm['kernel_masks'])==0,
        'local_floors_preserved':sm['single_floor']>=6 and sm['two_floor']>=8,
        'pair_cooccurrence_preserved':sm['max_pair_cooccurrence']<=2,
        'global_distance_at_least_baseline':sm['global_positive_floor']>=3,
        'global_distance_improved_over_baseline':sm['global_positive_floor']>3,
        'check4_equal_cost_not_worse':w4<=BASE_WEIGHT4_FALSE_EXCLUDE,
        'crossplane_arbitrary_correlation_solved':not cross['all_constructed_exact'],
    }
    return out


def enc(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',required=True); a=ap.parse_args()
    o=run(); raw=(enc(o)+'\n').encode('utf-8'); Path(a.out).write_bytes(raw)
    print(enc({
        'output':a.out,'sha256':hashlib.sha256(raw).hexdigest(),
        'atomic_move_count':o['atomic_move_count'],'structural_pair_count':o['structural_pair_count'],
        'unique_topology_count':o['unique_topology_count'],'global_distance_evaluated_count':o['global_distance_evaluated_count'],
        'frontier_feasible_count':o['frontier_feasible_count'],'signals':o['signals'],
        'selected_witness':None if o['selected'] is None else o['selected']['witness'],
        'selected_metrics':None if o['selected'] is None else o['selected']['metrics'],
    }))

if __name__=='__main__': main()
