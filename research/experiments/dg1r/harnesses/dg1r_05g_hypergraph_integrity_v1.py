#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
import numpy as np

WIDTH=128; BLOCKS=12; LOGICAL_BITS=48; CHECK_SLOTS=20
POST_STEPS=32; DAMAGE_AFTER_STEPS=1024; WORLD_START=20260926057000; WORLD_COUNT=8
HORIZONS=(1,4,8,16,32); MIX_RULES=np.asarray([90,150,110,22,30],dtype=np.uint16)
METHODS=("PAIR20_MAJORITY_48","HYPER20_MAJORITY_48","HYPER20_UNANIMOUS_48","HYPER20_DETECT_ONLY")
MAPPED_BLOCKS=np.asarray([1,4,7,10],dtype=np.int64)
PAIR_EDGES=[(i,(i+1)%12) for i in range(12)]+[(i,i+6) for i in range(6)]+[(0,3),(6,9)]
HYPER_EDGES=[
(0,2,7,9),(1,3,6,11),(4,5,9,10),(2,3,5,8),(0,1,4,8),
(6,7,8,10),(2,4,6,11),(0,3,5,7),(1,7,10,11),(1,5,6,9),
(3,8,9,10),(0,4,8,11),(0,2,6,10),(1,3,4,7),(2,5,7,11),
(2,3,4,10),(0,1,5,10),(0,3,9,11),(1,2,8,9),(4,6,7,9),
]
EXPECTED_DEG_HYPER=(7,7,7,7,7,6,6,7,6,7,7,6)
FAMILIES=(
"LOCAL_DATA2_D6","CHECK2_CORRELATED_D6","CHECK3_CORRELATED_D6","CHECK4_CORRELATED_D6",
"DATA2_PLUS_CHECK2_D6","DATA2_PLUS_CHECK3_D7","CHECK4_CORRELATED_D7","DISTRIBUTED_LOCAL_DATA2")


def eca_step_mixed(s,r):
    l=np.roll(s,1); rr=np.roll(s,-1); idx=(l<<2)|(s<<1)|rr
    return ((r>>idx)&1).astype(np.uint8)
def mixed_rules(rng,w):
    reps=w//len(MIX_RULES); rem=w%len(MIX_RULES)
    a=np.concatenate((np.tile(MIX_RULES,reps),MIX_RULES[:rem])).astype(np.uint16); rng.shuffle(a); return a
def mapped_logical(rng):
    offs=rng.integers(0,4,size=len(MAPPED_BLOCKS),dtype=np.int64)
    return np.asarray([int(b*4+o) for b,o in zip(MAPPED_BLOCKS,offs)],dtype=np.int64)
def relation_set(method): return PAIR_EDGES if method=="PAIR20_MAJORITY_48" else HYPER_EDGES
def degree(edges,b): return sum(1 for e in edges if b in e)
def incident_slots(edges,b): return [i for i,e in enumerate(edges) if b in e]
def encode_state(logical,method):
    out=np.zeros(WIDTH,dtype=np.uint8); out[:48]=logical; edges=relation_set(method)
    for i,e in enumerate(edges):
        v=np.zeros(4,dtype=np.uint8)
        for b in e: v ^= logical[b*4:(b+1)*4]
        out[48+i*4:48+(i+1)*4]=v
    return out
def decode_state(state): return state[:48].copy()
def candidates(state,method,b):
    logical=decode_state(state); edges=relation_set(method); out=[]
    for i,e in enumerate(edges):
        if b not in e: continue
        v=state[48+i*4:48+(i+1)*4].copy()
        for other in e:
            if other!=b: v ^= logical[other*4:(other+1)*4]
        out.append(v)
    return out
def group_candidates(cands):
    groups=[]
    for c in cands:
        for g in groups:
            if np.array_equal(c,g[0]): g[1]+=1; break
        else: groups.append([c.copy(),1])
    groups.sort(key=lambda z:z[1],reverse=True)
    return groups
def init_tel(): return {"repairs":0,"false_repairs":0,"abstentions":0,"winning_vote_sum":0,"winning_vote_max":0,"candidate_groups_sum":0}
def repair(state,method,ref,tel):
    detect_only=method=="HYPER20_DETECT_ONLY"; unanimous=method=="HYPER20_UNANIMOUS_48"
    for b in range(BLOCKS):
        cands=candidates(state,method,b); groups=group_candidates(cands); best=groups[0]; deg=len(cands)
        tel["candidate_groups_sum"] += len(groups)
        if unanimous: qualified=(best[1]==deg)
        else: qualified=(best[1] > deg/2)
        if not qualified:
            tel["abstentions"] += 1; continue
        tel["winning_vote_sum"] += best[1]; tel["winning_vote_max"] = max(tel["winning_vote_max"],best[1])
        proposal=best[0]; cur=state[b*4:(b+1)*4]
        if detect_only or np.array_equal(cur,proposal): continue
        if ref is not None and not np.array_equal(proposal,ref[b*4:(b+1)*4]): tel["false_repairs"] += 1
        state[b*4:(b+1)*4]=proposal; tel["repairs"] += 1
def step(state,bit,mapped,rules,method,ref=None,tel=None):
    if tel is None: tel=init_tel()
    repair(state,method,ref,tel); logical=decode_state(state); logical[mapped]=np.uint8(bit); logical=eca_step_mixed(logical,rules); state[:]=encode_state(logical,method); return tel
def prefix(u,mapped,rules,method):
    s=encode_state(np.zeros(LOGICAL_BITS,dtype=np.uint8),method)
    for t in range(DAMAGE_AFTER_STEPS): step(s,int(u[t]),mapped,rules,method)
    return s

def data_pos(b,k): return b*4+k
def check_pos(slot,k): return 48+slot*4+k
def first_incident(edges,b,n):
    xs=incident_slots(edges,b); assert len(xs)>=n; return xs[:n]
def build_scenario(method,fam):
    edges=relation_set(method); hyper=method!="PAIR20_MAJORITY_48"
    logical=[]; checks=[]
    if fam=="LOCAL_DATA2_D6":
        b=5 if hyper else 2; logical=[data_pos(b,0),data_pos(b,1)]
    elif fam=="CHECK2_CORRELATED_D6":
        b=5 if hyper else 2; checks=[check_pos(s,0) for s in first_incident(edges,b,2)]
    elif fam=="CHECK3_CORRELATED_D6":
        if not hyper: return None
        b=5; checks=[check_pos(s,0) for s in first_incident(edges,b,3)]
    elif fam=="CHECK4_CORRELATED_D6":
        if not hyper: return None
        b=5; checks=[check_pos(s,0) for s in first_incident(edges,b,4)]
    elif fam=="DATA2_PLUS_CHECK2_D6":
        b=5 if hyper else 2; logical=[data_pos(b,0),data_pos(b,1)]; checks=[check_pos(s,0) for s in first_incident(edges,b,2)]
    elif fam=="DATA2_PLUS_CHECK3_D7":
        b=2 if hyper else 3; logical=[data_pos(b,0),data_pos(b,1)]; checks=[check_pos(s,0) for s in first_incident(edges,b,3)]
    elif fam=="CHECK4_CORRELATED_D7":
        if not hyper: return None
        b=2; checks=[check_pos(s,0) for s in first_incident(edges,b,4)]
    elif fam=="DISTRIBUTED_LOCAL_DATA2":
        logical=[data_pos(2,0),data_pos(2,1),data_pos(8,0),data_pos(8,1)]
    else: raise KeyError(fam)
    return tuple(logical+checks),len(logical),len(checks)

def validate_design():
    assert len(PAIR_EDGES)==20 and len(HYPER_EDGES)==20
    assert tuple(degree(HYPER_EDGES,b) for b in range(12))==EXPECTED_DEG_HYPER
    pair_counts={}
    for e in HYPER_EDGES:
        for i,a in enumerate(e):
            for b in e[i+1:]:
                p=tuple(sorted((a,b))); pair_counts[p]=pair_counts.get(p,0)+1
    assert max(pair_counts.values())<=2
    assert degree(PAIR_EDGES,2)==3 and degree(PAIR_EDGES,3)==4
    assert degree(HYPER_EDGES,5)==6 and degree(HYPER_EDGES,2)==7

def no_damage(pre,future,mapped,rules,method):
    a=pre.copy(); b=pre.copy()
    for bit in future:
        ra=decode_state(a).copy(); rb=decode_state(b).copy(); step(a,int(bit),mapped,rules,method,ref=ra); step(b,int(bit),mapped,rules,method,ref=rb)
        if np.any(a!=b): return False
    return True

def one_scenario(pre,future,mapped,rules,method,fam,spec):
    inds,logical_count,check_count=spec; inds=np.asarray(inds,dtype=np.int64)
    assert len(inds)==logical_count+check_count; assert len(np.unique(inds))==len(inds)
    assert int(np.sum(inds<48))==logical_count; assert int(np.sum(inds>=48))==check_count
    assert not np.any(np.isin(inds[inds<48],mapped))
    ref=pre.copy(); dmg=pre.copy(); dmg[inds]^=1; telr=init_tel(); teld=init_tel(); pc=[]; lc=[]; flags=[]; hm={}
    for h,bit in enumerate(future,start=1):
        rlog=decode_state(ref).copy(); step(ref,int(bit),mapped,rules,method,ref=None,tel=telr); step(dmg,int(bit),mapped,rules,method,ref=rlog,tel=teld)
        pd=dmg!=ref; ld=decode_state(dmg)!=decode_state(ref); p=float(np.mean(pd)); l=float(np.mean(ld)); exact=bool(not np.any(ld)); pc.append(p); lc.append(l); flags.append(exact)
        if h in HORIZONS: hm[f"h{h}"]={"physical_divergence":p,"logical_divergence":l,"exact_logical_match":exact}
    rt=None
    for h in range(1,POST_STEPS+1):
        if all(flags[h-1:]): rt=h; break
    delta={k:int(teld[k]-telr[k]) for k in telr}
    return {"family":fam,"lesion_indices":[int(x) for x in inds],"logical_flip_count":logical_count,"integrity_flip_count":check_count,"actual_lesion_cardinality":int(len(inds)),"horizons":hm,"physical_divergence_area":float(np.sum(pc)),"logical_divergence_area":float(np.sum(lc)),"sustained_exact_logical_recovery":bool(rt is not None),"logical_recovery_time":rt,"repair_delta":delta}
def one_world(seed):
    validate_design(); rng=np.random.default_rng(np.random.PCG64(seed)); u=rng.integers(0,2,size=DAMAGE_AFTER_STEPS+POST_STEPS,dtype=np.uint8); mapped=mapped_logical(rng); rules=mixed_rules(rng,LOGICAL_BITS); future=u[DAMAGE_AFTER_STEPS:]; methods={}
    for m in METHODS:
        pre=prefix(u,mapped,rules,m); ctl=no_damage(pre,future,mapped,rules,m); scenarios=[]
        for fam in FAMILIES:
            spec=build_scenario(m,fam)
            if spec is not None: scenarios.append(one_scenario(pre,future,mapped,rules,m,fam,spec))
        methods[m]={"no_damage_control":bool(ctl),"scenarios":scenarios}
    return {"seed":int(seed),"mapped_logical":[int(x) for x in mapped],"methods":methods}
def q(v,p): return float(np.quantile(np.asarray(v,dtype=np.float64),p))
def fr(rows,m,f): return [s for r in rows for s in r["methods"][m]["scenarios"] if s["family"]==f]
def sf(scs):
    if not scs:return None
    o={"scenario_count":len(scs),"horizons":{}}
    for h in HORIZONS:
        k=f"h{h}";o["horizons"][k]={"logical_divergence_median":q([s["horizons"][k]["logical_divergence"] for s in scs],.5),"physical_divergence_median":q([s["horizons"][k]["physical_divergence"] for s in scs],.5),"exact_logical_match_rate":float(np.mean([s["horizons"][k]["exact_logical_match"] for s in scs]))}
    o["logical_divergence_area_median"]=q([s["logical_divergence_area"] for s in scs],.5);o["physical_divergence_area_median"]=q([s["physical_divergence_area"] for s in scs],.5);o["sustained_exact_logical_recovery_rate"]=float(np.mean([s["sustained_exact_logical_recovery"] for s in scs]))
    for key in ("repairs","false_repairs","abstentions","winning_vote_sum","winning_vote_max","candidate_groups_sum"):
        vals=[s["repair_delta"][key] for s in scs];o[key+"_sum"]=int(np.sum(vals));o[key+"_median"]=q(vals,.5)
    o["false_repair_fraction"]=float(o["false_repairs_sum"]/o["repairs_sum"]) if o["repairs_sum"] else 0.0
    return o
def summarize(rows):
    valid=all(r["methods"][m]["no_damage_control"] for r in rows for m in METHODS);o={"worlds":len(rows),"mechanical_valid":bool(valid),"methods":{}}
    for m in METHODS:o["methods"][m]={f:sf(fr(rows,m,f)) for f in FAMILIES if fr(rows,m,f)}
    h=o["methods"]["HYPER20_MAJORITY_48"];p=o["methods"]["PAIR20_MAJORITY_48"]
    x=h["DATA2_PLUS_CHECK2_D6"];px=p["DATA2_PLUS_CHECK2_D6"]
    cap=(x["horizons"]["h1"]["logical_divergence_median"]==0 and x["logical_divergence_area_median"]==0 and x["sustained_exact_logical_recovery_rate"]>=.90 and x["false_repair_fraction"]<=.01 and not (px["horizons"]["h1"]["logical_divergence_median"]==0 and px["logical_divergence_area_median"]==0 and px["sustained_exact_logical_recovery_rate"]>=.90 and px["false_repair_fraction"]<=.01))
    y=h["DATA2_PLUS_CHECK3_D7"];three=(y["horizons"]["h1"]["logical_divergence_median"]==0 and y["sustained_exact_logical_recovery_rate"]>=.90 and y["false_repair_fraction"]<=.01)
    t=h["CHECK3_CORRELATED_D6"];tie=(t["repairs_sum"]==0 and t["false_repairs_sum"]==0 and t["horizons"]["h4"]["logical_divergence_median"]==0)
    d=h["DISTRIBUTED_LOCAL_DATA2"];dist=(d["horizons"]["h4"]["logical_divergence_median"]==0 and d["sustained_exact_logical_recovery_rate"]>=.90 and d["false_repair_fraction"]<=.01)
    bounds=[f for f in ("CHECK4_CORRELATED_D6","CHECK4_CORRELATED_D7") if h[f]["false_repair_fraction"]>.10]
    o["hypergraph_capacity_signal"]=bool(cap);o["three_witness_tolerance_signal"]=bool(three);o["tie_safety_signal"]=bool(tie);o["distributed_hypergraph_repair_signal"]=bool(dist);o["compression_advantage"]=bool(cap);o["correlated_fault_boundary_families"]=bounds
    o["capacity"]={"logical_bits":48,"integrity_bits":80,"total_bits":128,"pairwise_witness_incidence":40,"hypergraph_witness_incidence":80,"hypergraph_min_degree":6,"hypergraph_max_degree":7}
    return o
def encode_json(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def run():
    rows=[one_world(WORLD_START+i) for i in range(WORLD_COUNT)];return {"schema":"yggdrasil.dg1r-05g-compressed-hypergraph-integrity.v1","rows":rows,"summary":summarize(rows),"worlds":len(rows),"seed_start":WORLD_START,"seed_end":WORLD_START+WORLD_COUNT-1}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",required=True);a=ap.parse_args();obj=run();raw=(encode_json(obj)+"\n").encode();Path(a.out).write_bytes(raw);print(encode_json({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"summary":obj["summary"],"worlds":obj["worlds"]}))
if __name__=="__main__":main()