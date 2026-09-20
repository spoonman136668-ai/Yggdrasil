#!/usr/bin/env python3
import argparse, hashlib, json
from collections import Counter
from pathlib import Path
import itertools
import numpy as np

WIDTH=128; BLOCKS=12; LOGICAL_BITS=48; CHECK_SLOTS=20; PLANES=4
POST_STEPS=32; DAMAGE_AFTER_STEPS=1024; WORLD_START=20260926060000; WORLD_COUNT=12
HORIZONS=(1,4,8,16,32); MIX_RULES=np.asarray([90,150,110,22,30],dtype=np.uint16)
METHODS=("GREEDY_BASELINE","CROSSPLANE2_GATE")
TOPOLOGIES=("HYPER20_BASELINE","DIST3_05L","DIST4_05M")
MAPPED_BLOCKS=np.asarray([1,4,7,10],dtype=np.int64)
EXPECTED_DEG=(7,7,7,7,7,6,6,7,6,7,7,6)
BASE_EDGES=(
(0,2,7,9),(1,3,6,11),(4,5,9,10),(2,3,5,8),(0,1,4,8),
(6,7,8,10),(2,4,6,11),(0,3,5,7),(1,7,10,11),(1,5,6,9),
(3,8,9,10),(0,4,8,11),(0,2,6,10),(1,3,4,7),(2,5,7,11),
(2,3,4,10),(0,1,5,10),(0,3,9,11),(1,2,8,9),(4,6,7,9),
)
DIST3_MOVES=((1,8,14),(5,16,11))
DIST4_EDGES=(
(0,2,7,9),(1,3,6,11),(4,5,9,10,11),(2,3,5),(0,1,4,8),
(6,7,8,10),(2,4,6),(0,3,5,6,7),(1,7,10,11),(1,5,6,9),
(3,8,9,10),(0,4,8,11),(0,2,6,10),(1,3,4,7),(2,5,7,8,11),
(2,3,4,10),(0,1,5,10),(0,3,9,11),(1,2,8,9),(4,7,9),
)
FAMILIES=(
"LOCAL_DATA2_D6","DISTRIBUTED_DATA2","DATA2_PLUS_CHECK2_D6","DATA2_PLUS_CHECK3_D7",
"CHECK4_BIT0_D6","CHECK4_BIT0_D7","CHECK4_BITS01_D6","SINGLE_DATA1_D6",
"BASE_WEAK4_MASK1106","DIST3_WEAK5_MASK2243","DIST4_MIN6_MASK249",
)
CHALLENGE_BLOCKS={
"BASE_WEAK4_MASK1106":(1,4,6,10),
"DIST3_WEAK5_MASK2243":(0,1,6,7,11),
"DIST4_MIN6_MASK249":(0,3,4,5,6,7),
}
STATIC_EXPECTED={
"HYPER20_BASELINE":{"rank":11,"kernel_masks":[4095],"single_floor":6,"two_floor":8,"global_floor":3,"max_pair":2},
"DIST3_05L":{"rank":12,"kernel_masks":[],"single_floor":6,"two_floor":8,"global_floor":3,"max_pair":2},
"DIST4_05M":{"rank":12,"kernel_masks":[],"single_floor":6,"two_floor":8,"global_floor":4,"max_pair":2},
}


def norm(edges): return tuple(tuple(sorted(e)) for e in edges)
def apply_move(edges,move):
    b,i,j=move; x=[list(e) for e in edges]
    assert b in x[i] and b not in x[j] and i!=j
    x[i].remove(b); x[j].append(b)
    return norm(x)
def dist3_edges():
    e=norm(BASE_EDGES)
    for m in DIST3_MOVES: e=apply_move(e,m)
    return e
TOPO_EDGE_MAP={"HYPER20_BASELINE":norm(BASE_EDGES),"DIST3_05L":dist3_edges(),"DIST4_05M":norm(DIST4_EDGES)}

def matrix(edges):
    h=np.zeros((CHECK_SLOTS,BLOCKS),dtype=np.uint8)
    for i,e in enumerate(edges): h[i,list(e)]=1
    return h
HMAP={k:matrix(v) for k,v in TOPO_EDGE_MAP.items()}

def degree(edges,b): return sum(1 for e in edges if b in e)
def incident_slots(edges,b): return [i for i,e in enumerate(edges) if b in e]
def pair_max(edges):
    c=Counter()
    for e in edges:
        for a,b in itertools.combinations(e,2): c[tuple(sorted((a,b)))]+=1
    return max(c.values()) if c else 0

def gf2_rank(cols):
    basis={}
    for x in cols:
        v=int(x)
        while v:
            p=v.bit_length()-1
            if p in basis: v ^= basis[p]
            else: basis[p]=v; break
    return len(basis)
def columns(edges):
    out=[0]*BLOCKS
    for i,e in enumerate(edges):
        for b in e: out[b] |= 1<<i
    return tuple(out)
def logical_syndromes(cols):
    syn=[0]*(1<<BLOCKS)
    for m in range(1,1<<BLOCKS):
        lsb=m & -m; b=lsb.bit_length()-1; syn[m]=syn[m^lsb]^cols[b]
    return syn
def geometry(edges):
    cols=columns(edges); syn=logical_syndromes(cols); rank=gf2_rank(cols)
    kernel=[m for m in range(1,1<<BLOCKS) if syn[m]==0]
    return {
        "rank":rank,"kernel_masks":kernel,
        "single_floor":min(c.bit_count() for c in cols),
        "two_floor":min((cols[a]^cols[b]).bit_count() for a,b in itertools.combinations(range(BLOCKS),2)),
        "global_floor":min(x.bit_count() for x in syn[1:] if x),
        "max_pair":pair_max(edges),
        "degree_vector":tuple(degree(edges,b) for b in range(BLOCKS)),
        "incidences":sum(len(e) for e in edges),
    }


def eca_step_mixed(s,r):
    l=np.roll(s,1); rr=np.roll(s,-1); idx=(l<<2)|(s<<1)|rr
    return ((r>>idx)&1).astype(np.uint8)
def mixed_rules(rng,w):
    reps=w//len(MIX_RULES); rem=w%len(MIX_RULES)
    a=np.concatenate((np.tile(MIX_RULES,reps),MIX_RULES[:rem])).astype(np.uint16); rng.shuffle(a); return a
def mapped_logical(rng):
    offs=rng.integers(0,4,size=len(MAPPED_BLOCKS),dtype=np.int64)
    return np.asarray([int(b*4+o) for b,o in zip(MAPPED_BLOCKS,offs)],dtype=np.int64)

def encode_state(logical,edges):
    out=np.zeros(WIDTH,dtype=np.uint8); out[:LOGICAL_BITS]=logical
    for i,e in enumerate(edges):
        v=np.zeros(PLANES,dtype=np.uint8)
        for b in e: v ^= logical[b*PLANES:(b+1)*PLANES]
        out[LOGICAL_BITS+i*PLANES:LOGICAL_BITS+(i+1)*PLANES]=v
    return out
def decode_state(state): return state[:LOGICAL_BITS].copy()
def syndrome_matrix(state,h):
    logical=decode_state(state).reshape(BLOCKS,PLANES); checks=state[LOGICAL_BITS:].reshape(CHECK_SLOTS,PLANES)
    return checks ^ ((h@logical)&1)

def init_tel():
    d={"repair_events":0,"inferred_logical_flips":0,"applied_logical_flips":0,"abstained_inferred_flips":0,
       "false_inferred_logical_flips":0,"false_applied_logical_flips":0,"inference_residual_syndrome_weight":0,
       "final_syndrome_weight":0,"decoder_iterations":0,"max_plane_support":0}
    for i in range(5): d[f"support_hist_{i}"]=0
    return d

def greedy_infer(state,h):
    syn=syndrome_matrix(state,h); flips=np.zeros((BLOCKS,PLANES),dtype=np.uint8); iterations=0; residual=0
    for k in range(PLANES):
        s=syn[:,k].copy(); used=np.zeros(BLOCKS,dtype=bool); it=0
        while it<4:
            cur=int(np.sum(s)); best_red=0; best_j=None
            for j in range(BLOCKS):
                if used[j]: continue
                red=cur-int(np.sum(s ^ h[:,j]))
                if red>best_red:
                    best_red=red; best_j=j
            if best_j is None or best_red<=0: break
            used[best_j]=True; flips[best_j,k]=1; s ^= h[:,best_j]; it+=1
        iterations+=it; residual+=int(np.sum(s))
    return flips,iterations,residual

def evaluate_false(flips,logical,ref):
    if ref is None: return 0
    lm=logical.reshape(BLOCKS,PLANES); rm=ref.reshape(BLOCKS,PLANES); false=0
    for b in range(BLOCKS):
        for k in range(PLANES):
            if flips[b,k] and int(lm[b,k]^1)!=int(rm[b,k]): false+=1
    return false

def repair(state,method,ref,tel,h):
    inferred,it,residual=greedy_infer(state,h); support=np.sum(inferred,axis=1,dtype=np.int16)
    if method=="GREEDY_BASELINE": applied=inferred.copy()
    elif method=="CROSSPLANE2_GATE": applied=inferred.copy(); applied[support<2,:]=0
    else: raise KeyError(method)
    logical=decode_state(state); inferred_n=int(np.sum(inferred)); applied_n=int(np.sum(applied))
    false_inf=evaluate_false(inferred,logical,ref); false_app=evaluate_false(applied,logical,ref)
    tel["inferred_logical_flips"]+=inferred_n; tel["applied_logical_flips"]+=applied_n
    tel["abstained_inferred_flips"]+=inferred_n-applied_n; tel["false_inferred_logical_flips"]+=false_inf
    tel["false_applied_logical_flips"]+=false_app; tel["decoder_iterations"]+=it
    tel["inference_residual_syndrome_weight"]+=residual; tel["max_plane_support"]=max(tel["max_plane_support"],int(np.max(support)))
    for v in support: tel[f"support_hist_{int(v)}"]+=1
    if applied_n:
        tel["repair_events"]+=1; lm=logical.reshape(BLOCKS,PLANES); lm ^= applied; state[:LOGICAL_BITS]=lm.reshape(LOGICAL_BITS)
    tel["final_syndrome_weight"]+=int(np.sum(syndrome_matrix(state,h)))
    return support.copy()

def step(state,bit,mapped,rules,method,edges,h,ref=None,tel=None):
    if tel is None: tel=init_tel()
    support=repair(state,method,ref,tel,h); logical=decode_state(state); logical[mapped]=np.uint8(bit)
    logical=eca_step_mixed(logical,rules); state[:]=encode_state(logical,edges); return support

def prefix(u,mapped,rules,method,edges,h):
    s=encode_state(np.zeros(LOGICAL_BITS,dtype=np.uint8),edges)
    for t in range(DAMAGE_AFTER_STEPS): step(s,int(u[t]),mapped,rules,method,edges,h)
    return s

def data_pos(b,k): return b*PLANES+k
def check_pos(slot,k): return LOGICAL_BITS+slot*PLANES+k
def mapped_plane_by_block(mapped): return {int(p//PLANES):int(p%PLANES) for p in mapped}
def safe_plane(mapped,blocks):
    mp=mapped_plane_by_block(mapped); excluded={mp[b] for b in blocks if b in mp}
    for k in range(PLANES):
        if k not in excluded: return k
    raise AssertionError("no safe plane")

def scenario(edges,mapped,fam):
    logical=[]; checks=[]; safe=None
    inc=lambda b,n: incident_slots(edges,b)[:n]
    if fam=="LOCAL_DATA2_D6": logical=[data_pos(5,0),data_pos(5,1)]
    elif fam=="DISTRIBUTED_DATA2": logical=[data_pos(2,0),data_pos(2,1),data_pos(8,0),data_pos(8,1)]
    elif fam=="DATA2_PLUS_CHECK2_D6": logical=[data_pos(5,0),data_pos(5,1)]; checks=[check_pos(s,0) for s in inc(5,2)]
    elif fam=="DATA2_PLUS_CHECK3_D7": logical=[data_pos(2,0),data_pos(2,1)]; checks=[check_pos(s,0) for s in inc(2,3)]
    elif fam=="CHECK4_BIT0_D6": checks=[check_pos(s,0) for s in inc(5,4)]
    elif fam=="CHECK4_BIT0_D7": checks=[check_pos(s,0) for s in inc(2,4)]
    elif fam=="CHECK4_BITS01_D6":
        for s in inc(5,4): checks.extend((check_pos(s,0),check_pos(s,1)))
    elif fam=="SINGLE_DATA1_D6": logical=[data_pos(5,0)]
    elif fam in CHALLENGE_BLOCKS:
        bs=CHALLENGE_BLOCKS[fam]; safe=safe_plane(mapped,bs); logical=[data_pos(b,safe) for b in bs]
    else: raise KeyError(fam)
    inds=tuple(logical+checks)
    return inds,len(logical),len(checks),safe

def validate_scenario(edges,mapped,fam):
    inds,lc,cc,sp=scenario(edges,mapped,fam); assert len(inds)==lc+cc and len(set(inds))==len(inds)
    assert sum(i<LOGICAL_BITS for i in inds)==lc and sum(i>=LOGICAL_BITS for i in inds)==cc
    expected={"LOCAL_DATA2_D6":(2,0),"DISTRIBUTED_DATA2":(4,0),"DATA2_PLUS_CHECK2_D6":(2,2),
              "DATA2_PLUS_CHECK3_D7":(2,3),"CHECK4_BIT0_D6":(0,4),"CHECK4_BIT0_D7":(0,4),
              "CHECK4_BITS01_D6":(0,8),"SINGLE_DATA1_D6":(1,0),"BASE_WEAK4_MASK1106":(4,0),
              "DIST3_WEAK5_MASK2243":(5,0),"DIST4_MIN6_MASK249":(6,0)}
    assert (lc,cc)==expected[fam]
    if fam in CHALLENGE_BLOCKS:
        assert sp is not None
        mp=mapped_plane_by_block(mapped)
        for b in CHALLENGE_BLOCKS[fam]:
            if b in mp: assert sp!=mp[b]
    else:
        assert sp is None
        if lc: assert not np.any(np.isin(np.asarray([i for i in inds if i<LOGICAL_BITS],dtype=np.int64),mapped))
    if fam.startswith("CHECK4") or "PLUS_CHECK" in fam:
        check_slots=[(i-LOGICAL_BITS)//PLANES for i in inds if i>=LOGICAL_BITS]
        block=5 if "D6" in fam else 2
        assert all(block in edges[s] for s in check_slots)
    return inds,lc,cc,sp

def world_design(seed):
    rng=np.random.default_rng(np.random.PCG64(seed)); u=rng.integers(0,2,size=DAMAGE_AFTER_STEPS+POST_STEPS,dtype=np.uint8)
    mapped=mapped_logical(rng); rules=mixed_rules(rng,LOGICAL_BITS); return u,mapped,rules

def mechanical_precheck():
    geoms={}
    for name in TOPOLOGIES:
        e=TOPO_EDGE_MAP[name]; g=geometry(e); geoms[name]=g
        exp=STATIC_EXPECTED[name]
        assert len(e)==20 and g["incidences"]==80 and g["degree_vector"]==EXPECTED_DEG
        assert g["rank"]==exp["rank"] and g["kernel_masks"]==exp["kernel_masks"]
        assert g["single_floor"]==exp["single_floor"] and g["two_floor"]==exp["two_floor"]
        assert g["global_floor"]==exp["global_floor"] and g["max_pair"]==exp["max_pair"]
    assert TOPO_EDGE_MAP["DIST4_05M"]==norm(DIST4_EDGES)
    checks=0
    for wi in range(WORLD_COUNT):
        seed=WORLD_START+wi; u,mapped,rules=world_design(seed); future=u[DAMAGE_AFTER_STEPS:]
        prefixes={}
        logical_post_trajectories={}
        for topo in TOPOLOGIES:
            e=TOPO_EDGE_MAP[topo]; h=HMAP[topo]
            for fam in FAMILIES: validate_scenario(e,mapped,fam); checks+=1
            for method in METHODS:
                pre=prefix(u,mapped,rules,method,e,h); prefixes[(topo,method)]=pre
                a=pre.copy(); b=pre.copy(); logical_traj=[]
                for bit in future:
                    ra=decode_state(a).copy(); rb=decode_state(b).copy()
                    step(a,int(bit),mapped,rules,method,e,h,ref=ra); step(b,int(bit),mapped,rules,method,e,h,ref=rb)
                    assert np.array_equal(a,b)
                    logical_traj.append(decode_state(a).copy())
                logical_post_trajectories[(topo,method)]=np.stack(logical_traj,axis=0)
        logical_prefixes=[decode_state(v) for v in prefixes.values()]
        for x in logical_prefixes[1:]: assert np.array_equal(x,logical_prefixes[0])
        trajectories=list(logical_post_trajectories.values())
        for x in trajectories[1:]: assert np.array_equal(x,trajectories[0])
    return {"mechanical_valid":True,"worlds":WORLD_COUNT,"seed_start":WORLD_START,"seed_end":WORLD_START+WORLD_COUNT-1,
            "topologies":geoms,"scenario_validations":checks,"no_damage_topology_method_controls":WORLD_COUNT*len(TOPOLOGIES)*len(METHODS),
            "canonical_scientific_execution":False,"stab18_r1_touched":False}

def one_scenario(pre,future,mapped,rules,method,topo,fam):
    edges=TOPO_EDGE_MAP[topo]; h=HMAP[topo]; inds,lc,cc,sp=validate_scenario(edges,mapped,fam); inds=np.asarray(inds,dtype=np.int64)
    ref=pre.copy(); dmg=pre.copy(); dmg[inds]^=1; telr=init_tel(); teld=init_tel(); pc=[]; lc_curve=[]; flags=[]; hm={}; first_support=None
    for stepn,bit in enumerate(future,start=1):
        rlog=decode_state(ref).copy(); step(ref,int(bit),mapped,rules,method,edges,h,ref=None,tel=telr)
        sup=step(dmg,int(bit),mapped,rules,method,edges,h,ref=rlog,tel=teld)
        if first_support is None: first_support=[int(x) for x in sup]
        pd=dmg!=ref; ld=decode_state(dmg)!=decode_state(ref); p=float(np.mean(pd)); l=float(np.mean(ld)); exact=bool(not np.any(ld))
        pc.append(p); lc_curve.append(l); flags.append(exact)
        if stepn in HORIZONS: hm[f"h{stepn}"]={"physical_divergence":p,"logical_divergence":l,"exact_logical_match":exact}
    rt=None
    for hh in range(1,POST_STEPS+1):
        if all(flags[hh-1:]): rt=hh; break
    delta={k:int(teld[k]-telr[k]) for k in telr}
    return {"family":fam,"lesion_indices":[int(x) for x in inds],"logical_flip_count":lc,"integrity_flip_count":cc,"safe_plane":sp,
            "first_episode_plane_support":first_support,"horizons":hm,"physical_divergence_area":float(np.sum(pc)),
            "logical_divergence_area":float(np.sum(lc_curve)),"sustained_exact_logical_recovery":bool(rt is not None),
            "logical_recovery_time":rt,"decoder_delta":delta}

def one_world(seed):
    u,mapped,rules=world_design(seed); future=u[DAMAGE_AFTER_STEPS:]; topologies={}; prefix_logicals=[]
    for topo in TOPOLOGIES:
        edges=TOPO_EDGE_MAP[topo]; h=HMAP[topo]; methods={}
        for method in METHODS:
            pre=prefix(u,mapped,rules,method,edges,h); prefix_logicals.append(decode_state(pre))
            methods[method]={"scenarios":[one_scenario(pre,future,mapped,rules,method,topo,f) for f in FAMILIES]}
        topologies[topo]={"methods":methods}
    for x in prefix_logicals[1:]: assert np.array_equal(x,prefix_logicals[0])
    return {"seed":int(seed),"mapped_logical":[int(x) for x in mapped],"topologies":topologies}

def q(v,p): return float(np.quantile(np.asarray(v,dtype=np.float64),p))
def family_rows(rows,topo,method,fam):
    return [s for r in rows for s in r["topologies"][topo]["methods"][method]["scenarios"] if s["family"]==fam]
def sf(scs):
    o={"scenario_count":len(scs),"horizons":{}}
    for h in HORIZONS:
        k=f"h{h}"; o["horizons"][k]={
            "logical_divergence_median":q([s["horizons"][k]["logical_divergence"] for s in scs],.5),
            "physical_divergence_median":q([s["horizons"][k]["physical_divergence"] for s in scs],.5),
            "exact_logical_match_rate":float(np.mean([s["horizons"][k]["exact_logical_match"] for s in scs]))}
    o["logical_divergence_area_median"]=q([s["logical_divergence_area"] for s in scs],.5)
    o["physical_divergence_area_median"]=q([s["physical_divergence_area"] for s in scs],.5)
    o["sustained_exact_logical_recovery_rate"]=float(np.mean([s["sustained_exact_logical_recovery"] for s in scs]))
    times=[s["logical_recovery_time"] for s in scs if s["logical_recovery_time"] is not None]
    o["logical_recovery_time_median"]=q(times,.5) if times else None
    first=np.asarray([s["first_episode_plane_support"] for s in scs],dtype=np.int16)
    o["first_episode_plane_support_median_by_block"]=[float(x) for x in np.median(first,axis=0)]
    for key in ("repair_events","inferred_logical_flips","applied_logical_flips","abstained_inferred_flips","false_inferred_logical_flips","false_applied_logical_flips","inference_residual_syndrome_weight","final_syndrome_weight","decoder_iterations","max_plane_support"):
        vals=[s["decoder_delta"][key] for s in scs]; o[key+"_sum"]=int(np.sum(vals)); o[key+"_median"]=q(vals,.5)
    for i in range(5): o[f"support_hist_{i}_sum"]=int(np.sum([s["decoder_delta"][f"support_hist_{i}"] for s in scs]))
    o["false_inferred_logical_flip_fraction"]=float(o["false_inferred_logical_flips_sum"]/o["inferred_logical_flips_sum"]) if o["inferred_logical_flips_sum"] else 0.0
    o["false_applied_logical_flip_fraction"]=float(o["false_applied_logical_flips_sum"]/o["applied_logical_flips_sum"]) if o["applied_logical_flips_sum"] else 0.0
    return o

def leq(a,b): return a<=b+1e-15
def geq(a,b): return a+1e-15>=b
def summarize(rows):
    out={"worlds":len(rows),"mechanical_valid":True,"topologies":{}}
    for topo in TOPOLOGIES:
        out["topologies"][topo]={}
        for method in METHODS:
            out["topologies"][topo][method]={f:sf(family_rows(rows,topo,method,f)) for f in FAMILIES}
    b=out["topologies"]["HYPER20_BASELINE"]; d3=out["topologies"]["DIST3_05L"]; d4=out["topologies"]["DIST4_05M"]
    legacy=("LOCAL_DATA2_D6","DISTRIBUTED_DATA2","DATA2_PLUS_CHECK2_D6","DATA2_PLUS_CHECK3_D7")
    checks=("CHECK4_BIT0_D6","CHECK4_BIT0_D7","CHECK4_BITS01_D6")
    legacy_ok=True
    for m in METHODS:
        for f in legacy:
            x,y=d4[m][f],b[m][f]
            legacy_ok &= leq(x["logical_divergence_area_median"],y["logical_divergence_area_median"]) and geq(x["sustained_exact_logical_recovery_rate"],y["sustained_exact_logical_recovery_rate"]) and x["false_applied_logical_flips_sum"]<=y["false_applied_logical_flips_sum"]
    check_ok=True
    for m in METHODS:
        for f in checks:
            x,y=d4[m][f],b[m][f]
            check_ok &= leq(x["logical_divergence_area_median"],y["logical_divergence_area_median"]) and x["false_applied_logical_flips_sum"]<=y["false_applied_logical_flips_sum"]
    x,y=d4["GREEDY_BASELINE"]["BASE_WEAK4_MASK1106"],b["GREEDY_BASELINE"]["BASE_WEAK4_MASK1106"]
    base_gain=(x["logical_divergence_area_median"]<y["logical_divergence_area_median"] and geq(x["sustained_exact_logical_recovery_rate"],y["sustained_exact_logical_recovery_rate"]) and x["false_applied_logical_flips_sum"]<=y["false_applied_logical_flips_sum"])
    x,y=d4["GREEDY_BASELINE"]["DIST3_WEAK5_MASK2243"],d3["GREEDY_BASELINE"]["DIST3_WEAK5_MASK2243"]
    dist3_gain=(x["logical_divergence_area_median"]<y["logical_divergence_area_median"] and geq(x["sustained_exact_logical_recovery_rate"],y["sustained_exact_logical_recovery_rate"]) and x["false_applied_logical_flips_sum"]<=y["false_applied_logical_flips_sum"])
    x=d4["GREEDY_BASELINE"]["DIST4_MIN6_MASK249"]
    boundary=x["sustained_exact_logical_recovery_rate"]>0 and x["false_applied_logical_flip_fraction"]<=0.01
    corr=d4["CROSSPLANE2_GATE"]["CHECK4_BITS01_D6"]["false_applied_logical_flips_sum"]>0
    out["signals"]={"legacy_logical_no_regression":bool(legacy_ok),"check_only_no_regression":bool(check_ok),"base_weak_dynamic_gain":bool(base_gain),"dist3_weak_dynamic_gain":bool(dist3_gain),"dist4_boundary_preserved":bool(boundary),"dynamic_distance_transfer":bool(legacy_ok and check_ok and (base_gain or dist3_gain)),"crossplane_correlated_failure":bool(corr)}
    out["single_bit_sensitivity"]={t:out["topologies"][t]["CROSSPLANE2_GATE"]["SINGLE_DATA1_D6"] for t in TOPOLOGIES}
    return out

def run():
    rows=[one_world(WORLD_START+i) for i in range(WORLD_COUNT)]
    return {"schema":"yggdrasil.dg1r-05n-distance4-dynamic-transfer.v1","rows":rows,"summary":summarize(rows),"worlds":WORLD_COUNT,
            "seed_start":WORLD_START,"seed_end":WORLD_START+WORLD_COUNT-1,"canonical_scientific_execution":False,"stab18_r1_touched":False}
def enc(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out"); ap.add_argument("--precheck",action="store_true"); a=ap.parse_args()
    if a.precheck:
        obj=mechanical_precheck(); print(enc(obj)); return
    if not a.out: ap.error("--out is required unless --precheck")
    obj=run(); raw=(enc(obj)+"\n").encode("utf-8"); Path(a.out).write_bytes(raw)
    print(enc({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"summary":obj["summary"],"worlds":obj["worlds"]}))
if __name__=="__main__": main()
