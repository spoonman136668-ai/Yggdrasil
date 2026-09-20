#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
import numpy as np

WIDTH=128; BLOCKS=12; LOGICAL_BITS=48; CHECK_SLOTS=20
POST_STEPS=32; DAMAGE_AFTER_STEPS=1024; WORLD_START=20260926058000; WORLD_COUNT=8
HORIZONS=(1,4,8,16,32); MIX_RULES=np.asarray([90,150,110,22,30],dtype=np.uint16)
METHODS=("NAIVE_MAJORITY","MW_UNIQUE","GREEDY_SYNDROME","GREEDY_SINGLE_PASS")
MAPPED_BLOCKS=np.asarray([1,4,7,10],dtype=np.int64)
HYPER_EDGES=[
(0,2,7,9),(1,3,6,11),(4,5,9,10),(2,3,5,8),(0,1,4,8),
(6,7,8,10),(2,4,6,11),(0,3,5,7),(1,7,10,11),(1,5,6,9),
(3,8,9,10),(0,4,8,11),(0,2,6,10),(1,3,4,7),(2,5,7,11),
(2,3,4,10),(0,1,5,10),(0,3,9,11),(1,2,8,9),(4,6,7,9),
]
EXPECTED_DEG=(7,7,7,7,7,6,6,7,6,7,7,6)
FAMILIES=("LOCAL_DATA2_D6","CHECK2_CORRELATED_D6","CHECK3_CORRELATED_D6","CHECK4_CORRELATED_D6","DATA2_PLUS_CHECK2_D6","DATA2_PLUS_CHECK3_D7","CHECK4_CORRELATED_D7","DISTRIBUTED_LOCAL_DATA2")
H=np.zeros((20,12),dtype=np.uint8)
for i,e in enumerate(HYPER_EDGES): H[i,list(e)]=1
MASKS=np.empty((1<<12,12),dtype=np.uint8)
for m in range(1<<12): MASKS[m]=[(m>>j)&1 for j in range(12)]
MASK_WEIGHT=np.sum(MASKS,axis=1,dtype=np.int16)
PRED_SYND=((MASKS@H.T)&1).astype(np.uint8)


def eca_step_mixed(s,r):
    l=np.roll(s,1); rr=np.roll(s,-1); idx=(l<<2)|(s<<1)|rr
    return ((r>>idx)&1).astype(np.uint8)
def mixed_rules(rng,w):
    reps=w//len(MIX_RULES); rem=w%len(MIX_RULES)
    a=np.concatenate((np.tile(MIX_RULES,reps),MIX_RULES[:rem])).astype(np.uint16); rng.shuffle(a); return a
def mapped_logical(rng):
    offs=rng.integers(0,4,size=len(MAPPED_BLOCKS),dtype=np.int64)
    return np.asarray([int(b*4+o) for b,o in zip(MAPPED_BLOCKS,offs)],dtype=np.int64)
def degree(b): return sum(1 for e in HYPER_EDGES if b in e)
def incident_slots(b): return [i for i,e in enumerate(HYPER_EDGES) if b in e]
def encode_state(logical):
    out=np.zeros(WIDTH,dtype=np.uint8); out[:48]=logical
    for i,e in enumerate(HYPER_EDGES):
        v=np.zeros(4,dtype=np.uint8)
        for b in e: v ^= logical[b*4:(b+1)*4]
        out[48+i*4:48+(i+1)*4]=v
    return out
def decode_state(state): return state[:48].copy()
def syndrome_matrix(state):
    logical=decode_state(state).reshape(12,4)
    checks=state[48:].reshape(20,4)
    pred=(H@logical)&1
    return checks ^ pred

def init_tel(): return {"repair_events":0,"inferred_logical_flips":0,"false_logical_flips":0,"ambiguous_mw_bitplanes":0,"final_syndrome_weight":0,"decoder_iterations":0,"abstentions":0}
def apply_flip_matrix(state,flips,ref,tel):
    logical=decode_state(state).reshape(12,4)
    refm=None if ref is None else ref.reshape(12,4)
    changed=0; false=0
    for b in range(12):
        for k in range(4):
            if flips[b,k]:
                changed+=1; post=int(logical[b,k]^1)
                if refm is not None and post!=int(refm[b,k]): false+=1
                logical[b,k]^=1
    if changed:
        tel["repair_events"]+=1; tel["inferred_logical_flips"]+=changed; tel["false_logical_flips"]+=false
        state[:48]=logical.reshape(48)
def naive_repair(state,ref,tel):
    logical=decode_state(state)
    proposals=[]
    for b in range(12):
        cands=[]
        for i,e in enumerate(HYPER_EDGES):
            if b not in e: continue
            v=state[48+i*4:48+(i+1)*4].copy()
            for o in e:
                if o!=b: v ^= logical[o*4:(o+1)*4]
            cands.append(v)
        groups=[]
        for c in cands:
            for g in groups:
                if np.array_equal(c,g[0]): g[1]+=1; break
            else: groups.append([c.copy(),1])
        groups.sort(key=lambda z:z[1],reverse=True); best=groups[0]
        if best[1] > len(cands)/2 and not np.array_equal(best[0],logical[b*4:(b+1)*4]): proposals.append((b,best[0]))
        elif best[1] <= len(cands)/2: tel["abstentions"]+=1
    # Frozen 05G semantics were sequential. Preserve them exactly by applying in block order
    # and recomputing later candidates from the mutated state would require in-loop updates.
    # Therefore implement exact sequential reference separately below.
    if proposals:
        pass

def naive_repair_sequential(state,ref,tel):
    for b in range(12):
        logical=decode_state(state); cands=[]
        for i,e in enumerate(HYPER_EDGES):
            if b not in e: continue
            v=state[48+i*4:48+(i+1)*4].copy()
            for o in e:
                if o!=b: v ^= logical[o*4:(o+1)*4]
            cands.append(v)
        groups=[]
        for c in cands:
            for g in groups:
                if np.array_equal(c,g[0]): g[1]+=1; break
            else: groups.append([c.copy(),1])
        groups.sort(key=lambda z:z[1],reverse=True); best=groups[0]
        if best[1] <= len(cands)/2:
            tel["abstentions"]+=1; continue
        cur=state[b*4:(b+1)*4]
        if np.array_equal(cur,best[0]): continue
        flips=np.zeros((12,4),dtype=np.uint8); flips[b]=cur^best[0]; apply_flip_matrix(state,flips,ref,tel)

def mw_unique_repair(state,ref,tel):
    syn=syndrome_matrix(state)
    flips=np.zeros((12,4),dtype=np.uint8)
    for k in range(4):
        s=syn[:,k]
        if not np.any(s): continue
        residual=PRED_SYND ^ s[None,:]
        weights=MASK_WEIGHT + np.sum(residual,axis=1,dtype=np.int16)
        wmin=int(weights.min()); winners=np.flatnonzero(weights==wmin)
        # unique logical mask only
        if len(winners)!=1:
            tel["ambiguous_mw_bitplanes"]+=1; tel["abstentions"]+=1; tel["final_syndrome_weight"]+=int(np.sum(s)); continue
        mask=int(winners[0]); flips[:,k]=MASKS[mask]
        tel["final_syndrome_weight"]+=int(np.sum(residual[mask]))
    apply_flip_matrix(state,flips,ref,tel)

def greedy_repair(state,ref,tel,max_flips):
    syn=syndrome_matrix(state)
    flips=np.zeros((12,4),dtype=np.uint8)
    for k in range(4):
        s=syn[:,k].copy(); used=np.zeros(12,dtype=bool); it=0
        while it<max_flips:
            cur=int(np.sum(s)); best_red=0; best_j=None
            for j in range(12):
                if used[j]: continue
                red=cur-int(np.sum(s ^ H[:,j]))
                if red>best_red:
                    best_red=red; best_j=j
            if best_j is None or best_red<=0: break
            used[best_j]=True; flips[best_j,k]^=1; s ^= H[:,best_j]; it+=1
        tel["decoder_iterations"]+=it; tel["final_syndrome_weight"]+=int(np.sum(s))
        if np.any(s) and it==0: tel["abstentions"]+=1
    apply_flip_matrix(state,flips,ref,tel)
def repair(state,method,ref,tel):
    if method=="NAIVE_MAJORITY": naive_repair_sequential(state,ref,tel)
    elif method=="MW_UNIQUE": mw_unique_repair(state,ref,tel)
    elif method=="GREEDY_SYNDROME": greedy_repair(state,ref,tel,4)
    elif method=="GREEDY_SINGLE_PASS": greedy_repair(state,ref,tel,1)
    else: raise KeyError(method)
def step(state,bit,mapped,rules,method,ref=None,tel=None):
    if tel is None: tel=init_tel()
    repair(state,method,ref,tel); logical=decode_state(state); logical[mapped]=np.uint8(bit); logical=eca_step_mixed(logical,rules); state[:]=encode_state(logical); return tel
def prefix(u,mapped,rules,method):
    s=encode_state(np.zeros(LOGICAL_BITS,dtype=np.uint8))
    for t in range(DAMAGE_AFTER_STEPS): step(s,int(u[t]),mapped,rules,method)
    return s

def data_pos(b,k): return b*4+k
def check_pos(slot,k): return 48+slot*4+k
def first_incident(b,n):
    xs=incident_slots(b); assert len(xs)>=n; return xs[:n]
def scenario(fam):
    logical=[]; checks=[]
    if fam=="LOCAL_DATA2_D6": logical=[data_pos(5,0),data_pos(5,1)]
    elif fam=="CHECK2_CORRELATED_D6": checks=[check_pos(s,0) for s in first_incident(5,2)]
    elif fam=="CHECK3_CORRELATED_D6": checks=[check_pos(s,0) for s in first_incident(5,3)]
    elif fam=="CHECK4_CORRELATED_D6": checks=[check_pos(s,0) for s in first_incident(5,4)]
    elif fam=="DATA2_PLUS_CHECK2_D6": logical=[data_pos(5,0),data_pos(5,1)]; checks=[check_pos(s,0) for s in first_incident(5,2)]
    elif fam=="DATA2_PLUS_CHECK3_D7": logical=[data_pos(2,0),data_pos(2,1)]; checks=[check_pos(s,0) for s in first_incident(2,3)]
    elif fam=="CHECK4_CORRELATED_D7": checks=[check_pos(s,0) for s in first_incident(2,4)]
    elif fam=="DISTRIBUTED_LOCAL_DATA2": logical=[data_pos(2,0),data_pos(2,1),data_pos(8,0),data_pos(8,1)]
    else: raise KeyError(fam)
    return tuple(logical+checks),len(logical),len(checks)
def validate_design():
    assert len(HYPER_EDGES)==20; assert tuple(degree(b) for b in range(12))==EXPECTED_DEG
    pc={}
    for e in HYPER_EDGES:
        for i,a in enumerate(e):
            for b in e[i+1:]: pc[tuple(sorted((a,b)))]=pc.get(tuple(sorted((a,b))),0)+1
    assert max(pc.values())<=2
    assert degree(5)==6 and degree(2)==7
    for fam in FAMILIES:
        inds,lc,cc=scenario(fam); assert len(inds)==lc+cc and len(set(inds))==len(inds)
def no_damage(pre,future,mapped,rules,method):
    a=pre.copy(); b=pre.copy()
    for bit in future:
        ra=decode_state(a).copy(); rb=decode_state(b).copy(); step(a,int(bit),mapped,rules,method,ref=ra); step(b,int(bit),mapped,rules,method,ref=rb)
        if np.any(a!=b): return False
    return True
def one_scenario(pre,future,mapped,rules,method,fam):
    inds,lc,cc=scenario(fam); inds=np.asarray(inds,dtype=np.int64); assert int(np.sum(inds<48))==lc and int(np.sum(inds>=48))==cc and not np.any(np.isin(inds[inds<48],mapped))
    ref=pre.copy(); dmg=pre.copy(); dmg[inds]^=1; telr=init_tel(); teld=init_tel(); pc=[]; lc_curve=[]; flags=[]; hm={}
    for h,bit in enumerate(future,start=1):
        rlog=decode_state(ref).copy(); step(ref,int(bit),mapped,rules,method,ref=None,tel=telr); step(dmg,int(bit),mapped,rules,method,ref=rlog,tel=teld)
        pd=dmg!=ref; ld=decode_state(dmg)!=decode_state(ref); p=float(np.mean(pd)); l=float(np.mean(ld)); exact=bool(not np.any(ld)); pc.append(p); lc_curve.append(l); flags.append(exact)
        if h in HORIZONS: hm[f"h{h}"]={"physical_divergence":p,"logical_divergence":l,"exact_logical_match":exact}
    rt=None
    for h in range(1,POST_STEPS+1):
        if all(flags[h-1:]): rt=h; break
    delta={k:int(teld[k]-telr[k]) for k in telr}
    return {"family":fam,"lesion_indices":[int(x) for x in inds],"logical_flip_count":int(np.sum(inds<48)),"integrity_flip_count":int(np.sum(inds>=48)),"horizons":hm,"physical_divergence_area":float(np.sum(pc)),"logical_divergence_area":float(np.sum(lc_curve)),"sustained_exact_logical_recovery":bool(rt is not None),"logical_recovery_time":rt,"decoder_delta":delta}
def one_world(seed):
    validate_design(); rng=np.random.default_rng(np.random.PCG64(seed)); u=rng.integers(0,2,size=DAMAGE_AFTER_STEPS+POST_STEPS,dtype=np.uint8); mapped=mapped_logical(rng); rules=mixed_rules(rng,LOGICAL_BITS); future=u[DAMAGE_AFTER_STEPS:]; methods={}
    for m in METHODS:
        pre=prefix(u,mapped,rules,m); ctl=no_damage(pre,future,mapped,rules,m); methods[m]={"no_damage_control":bool(ctl),"scenarios":[one_scenario(pre,future,mapped,rules,m,f) for f in FAMILIES]}
    return {"seed":int(seed),"mapped_logical":[int(x) for x in mapped],"methods":methods}
def q(v,p): return float(np.quantile(np.asarray(v,dtype=np.float64),p))
def fr(rows,m,f): return [s for r in rows for s in r["methods"][m]["scenarios"] if s["family"]==f]
def sf(scs):
    o={"scenario_count":len(scs),"horizons":{}}
    for h in HORIZONS:
        k=f"h{h}";o["horizons"][k]={"logical_divergence_median":q([s["horizons"][k]["logical_divergence"] for s in scs],.5),"physical_divergence_median":q([s["horizons"][k]["physical_divergence"] for s in scs],.5),"exact_logical_match_rate":float(np.mean([s["horizons"][k]["exact_logical_match"] for s in scs]))}
    o["logical_divergence_area_median"]=q([s["logical_divergence_area"] for s in scs],.5);o["physical_divergence_area_median"]=q([s["physical_divergence_area"] for s in scs],.5);o["sustained_exact_logical_recovery_rate"]=float(np.mean([s["sustained_exact_logical_recovery"] for s in scs]))
    for key in ("repair_events","inferred_logical_flips","false_logical_flips","ambiguous_mw_bitplanes","final_syndrome_weight","decoder_iterations","abstentions"):
        vals=[s["decoder_delta"][key] for s in scs];o[key+"_sum"]=int(np.sum(vals));o[key+"_median"]=q(vals,.5)
    o["false_logical_flip_fraction"]=float(o["false_logical_flips_sum"]/o["inferred_logical_flips_sum"]) if o["inferred_logical_flips_sum"] else 0.0
    return o
def passes_dist(x): return x["horizons"]["h1"]["logical_divergence_median"]==0 and x["logical_divergence_area_median"]==0 and x["sustained_exact_logical_recovery_rate"]>=.90 and x["false_logical_flip_fraction"]<=.01
def summarize(rows):
    valid=all(r["methods"][m]["no_damage_control"] for r in rows for m in METHODS);o={"worlds":len(rows),"mechanical_valid":bool(valid),"methods":{}}
    for m in METHODS:o["methods"][m]={f:sf(fr(rows,m,f)) for f in FAMILIES}
    naive=o["methods"]["NAIVE_MAJORITY"]["DISTRIBUTED_LOCAL_DATA2"];mw=o["methods"]["MW_UNIQUE"]["DISTRIBUTED_LOCAL_DATA2"];gr=o["methods"]["GREEDY_SYNDROME"]["DISTRIBUTED_LOCAL_DATA2"];sp=o["methods"]["GREEDY_SINGLE_PASS"]["DISTRIBUTED_LOCAL_DATA2"]
    dist_mw=passes_dist(mw) and not passes_dist(naive); dist_gr=passes_dist(gr) and not passes_dist(naive)
    local_gr=passes_dist(o["methods"]["GREEDY_SYNDROME"]["DATA2_PLUS_CHECK2_D6"]) and passes_dist(o["methods"]["GREEDY_SYNDROME"]["DATA2_PLUS_CHECK3_D7"])
    iter_val=(gr["logical_divergence_area_median"]<sp["logical_divergence_area_median"] and gr["false_logical_flip_fraction"]<=sp["false_logical_flip_fraction"])
    o["distributed_localization_signal"]=[m for m,v in (("MW_UNIQUE",dist_mw),("GREEDY_SYNDROME",dist_gr)) if v]
    o["representation_sufficient_signal"]=bool(dist_mw);o["local_decoder_signal"]=bool(dist_gr and local_gr);o["iteration_value_signal"]=bool(iter_val)
    o["mw_ambiguity"]={f:o["methods"]["MW_UNIQUE"][f]["ambiguous_mw_bitplanes_sum"] for f in FAMILIES}
    o["correlated_boundary_false_flip_fraction"]={m:{f:o["methods"][m][f]["false_logical_flip_fraction"] for f in ("CHECK4_CORRELATED_D6","CHECK4_CORRELATED_D7")} for m in METHODS}
    return o
def encode_json(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def run():
    rows=[one_world(WORLD_START+i) for i in range(WORLD_COUNT)];return {"schema":"yggdrasil.dg1r-05h-hypergraph-syndrome-localization.v1","rows":rows,"summary":summarize(rows),"worlds":len(rows),"seed_start":WORLD_START,"seed_end":WORLD_START+WORLD_COUNT-1}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",required=True);a=ap.parse_args();obj=run();raw=(encode_json(obj)+"\n").encode();Path(a.out).write_bytes(raw);print(encode_json({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"summary":obj["summary"],"worlds":obj["worlds"]}))
if __name__=="__main__":main()