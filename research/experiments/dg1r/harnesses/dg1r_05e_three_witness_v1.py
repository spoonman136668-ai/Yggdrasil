#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
import numpy as np

WIDTH=128; LOGICAL_BLOCKS=12; LOGICAL_BITS=48; LOCAL74_BITS=84
POST_STEPS=32; DAMAGE_AFTER_STEPS=1024; WORLD_START=20260926055000; WORLD_COUNT=8
HORIZONS=(1,4,8,16,32); MIX_RULES=np.asarray([90,150,110,22,30],dtype=np.uint16)
METHODS=("PAIR2","UNANIMOUS3","MAJORITY3","DETECT_ONLY")
MAPPED_BLOCKS=np.asarray([1,3,5,7,9,11],dtype=np.int64)
TARGETS=(2,6,10)
EDGES=((2,0),(2,1),(2,3),(6,4),(6,5),(6,7),(10,8),(10,9),(10,11),(3,4),(7,8))
TARGET_EDGE_ORDER={2:(0,1,2),6:(3,4,5),10:(6,7,8)}
EXPECTED={
    "SILENT_DATA3":3,
    "SILENT_DATA3_PLUS_ONE_WITNESS1":4,
    "SILENT_DATA3_PLUS_TWO_WITNESS2":5,
    "ONE_WITNESS1_ONLY":1,
    "TWO_WITNESS2_ONLY":2,
    "DISTRIBUTED_SILENT3":9,
    "DISTRIBUTED_ONE_BAD_WITNESS":12,
}
DATA_OFF=(2,4,5,6)


def eca_step_mixed(s,r):
    l=np.roll(s,1); rr=np.roll(s,-1); idx=(l<<2)|(s<<1)|rr
    return ((r>>idx)&1).astype(np.uint8)

def mixed_rules(rng,w):
    reps=w//len(MIX_RULES); rem=w%len(MIX_RULES)
    a=np.concatenate((np.tile(MIX_RULES,reps),MIX_RULES[:rem])).astype(np.uint16)
    rng.shuffle(a); return a

def h74_encode4(d):
    d1,d2,d3,d4=[int(x) for x in d]; o=np.empty(7,dtype=np.uint8)
    o[0]=d1^d2^d4; o[1]=d1^d3^d4; o[2]=d1; o[3]=d2^d3^d4; o[4]=d2; o[5]=d3; o[6]=d4
    return o

def h74_decode7(c): return c[[2,4,5,6]].copy()

def syndrome7(c):
    return int(c[0]^c[2]^c[4]^c[6])+2*int(c[1]^c[2]^c[5]^c[6])+4*int(c[3]^c[4]^c[5]^c[6])

def mapped_logical(rng):
    offs=rng.integers(0,4,size=len(MAPPED_BLOCKS),dtype=np.int64)
    return np.asarray([int(b*4+o) for b,o in zip(MAPPED_BLOCKS,offs)],dtype=np.int64)

def tissue_phys_for_logical(lp):
    b=int(lp//4); off=int(lp%4); return b*7+DATA_OFF[off]

def cross_index(edge_idx,k): return LOCAL74_BITS+edge_idx*4+k

def encode_state(logical):
    out=np.zeros(WIDTH,dtype=np.uint8)
    for b in range(LOGICAL_BLOCKS): out[b*7:b*7+7]=h74_encode4(logical[b*4:(b+1)*4])
    for ei,(a,b) in enumerate(EDGES):
        out[LOCAL74_BITS+ei*4:LOCAL74_BITS+(ei+1)*4]=logical[a*4:(a+1)*4]^logical[b*4:(b+1)*4]
    return out

def decode_state(state):
    x=np.empty(LOGICAL_BITS,dtype=np.uint8)
    for b in range(LOGICAL_BLOCKS): x[b*4:(b+1)*4]=h74_decode7(state[b*7:b*7+7])
    return x

def init_tel():
    return {"syndrome_positive":0,"repairs":0,"false_repairs":0,"abstentions":0,"unanimous_candidates":0,"majority2_candidates":0,"all_different":0}

def witness_candidate(decoded,cross,target,edge_idx):
    a,b=EDGES[edge_idx]
    if a==target: n=b
    elif b==target: n=a
    else: raise ValueError((target,edge_idx,EDGES[edge_idx]))
    cv=cross[edge_idx*4:(edge_idx+1)*4]
    return decoded[n*4:(n+1)*4]^cv

def choose_candidate(cands,method,tel):
    eq01=np.array_equal(cands[0],cands[1]); eq02=np.array_equal(cands[0],cands[2]); eq12=np.array_equal(cands[1],cands[2])
    if eq01 and eq02:
        tel["unanimous_candidates"]+=1
        if method in ("PAIR2","UNANIMOUS3","MAJORITY3"): return cands[0]
        return None
    if eq01 or eq02 or eq12:
        tel["majority2_candidates"]+=1
        if method=="MAJORITY3":
            if eq01 or eq02: return cands[0]
            return cands[1]
        if method=="PAIR2":
            if eq01: return cands[0]
            tel["abstentions"]+=1; return None
        if method=="UNANIMOUS3":
            tel["abstentions"]+=1; return None
        return None
    tel["all_different"]+=1
    if method!="DETECT_ONLY": tel["abstentions"]+=1
    return None

def repair(state,method,ref_logical,tel):
    decoded=decode_state(state); cross=state[LOCAL74_BITS:].copy()
    for target in TARGETS:
        syn=syndrome7(state[target*7:target*7+7])
        if syn: tel["syndrome_positive"]+=1
        cands=[witness_candidate(decoded,cross,target,ei) for ei in TARGET_EDGE_ORDER[target]]
        proposal=choose_candidate(cands,method,tel)
        if method=="DETECT_ONLY" or proposal is None: continue
        local=decoded[target*4:(target+1)*4]
        if np.array_equal(local,proposal): continue
        if ref_logical is not None and not np.array_equal(proposal,ref_logical[target*4:(target+1)*4]): tel["false_repairs"]+=1
        state[target*7:target*7+7]=h74_encode4(proposal); decoded[target*4:(target+1)*4]=proposal; tel["repairs"]+=1

def step(state,bit,mapped,rules,method,ref_logical=None,tel=None):
    if tel is None: tel=init_tel()
    repair(state,method,ref_logical,tel)
    logical=decode_state(state); logical[mapped]=np.uint8(bit); logical=eca_step_mixed(logical,rules); state[:]=encode_state(logical)
    return tel

def prefix(u,mapped,rules,method):
    s=encode_state(np.zeros(LOGICAL_BITS,dtype=np.uint8))
    for t in range(DAMAGE_AFTER_STEPS): step(s,int(u[t]),mapped,rules,method)
    return s

def mapped_phys(mapped): return np.asarray([tissue_phys_for_logical(int(lp)) for lp in mapped],dtype=np.int64)

def local_silent_inds(target):
    base=target*7; return (base+2,base+4,base+5)

def first_edge_check(target): return cross_index(TARGET_EDGE_ORDER[target][0],0)

def second_edge_check(target): return cross_index(TARGET_EDGE_ORDER[target][1],0)

def lesion_scenarios():
    out=[]
    for t in TARGETS:
        local=local_silent_inds(t); e1=first_edge_check(t); e2=second_edge_check(t)
        out.append(("SILENT_DATA3",tuple(local)))
        out.append(("SILENT_DATA3_PLUS_ONE_WITNESS1",tuple(local)+(e1,)))
        out.append(("SILENT_DATA3_PLUS_TWO_WITNESS2",tuple(local)+(e1,e2)))
        out.append(("ONE_WITNESS1_ONLY",(e1,)))
        out.append(("TWO_WITNESS2_ONLY",(e1,e2)))
    inds=[]
    for t in TARGETS: inds.extend(local_silent_inds(t))
    out.append(("DISTRIBUTED_SILENT3",tuple(inds)))
    inds=[]
    for t in TARGETS:
        inds.extend(local_silent_inds(t)); inds.append(first_edge_check(t))
    out.append(("DISTRIBUTED_ONE_BAD_WITNESS",tuple(inds)))
    return out

def no_damage(pre,future,mapped,rules,method):
    a=pre.copy(); b=pre.copy()
    for bit in future:
        la=decode_state(a).copy(); lb=decode_state(b).copy()
        step(a,int(bit),mapped,rules,method,ref_logical=la); step(b,int(bit),mapped,rules,method,ref_logical=lb)
        if np.any(a!=b): return False
    return True

def one_scenario(pre,future,mapped,rules,method,fam,inds,mp):
    inds=np.asarray(inds,dtype=np.int64)
    assert len(inds)==EXPECTED[fam],(fam,len(inds),EXPECTED[fam])
    assert len(np.unique(inds))==EXPECTED[fam],(fam,inds)
    assert not np.any(np.isin(inds,mp)),(fam,inds,mp)
    if fam.startswith("SILENT_DATA3"):
        # Every local three-data pattern used here must be syndrome-silent pre-repair.
        target=int(inds[0]//7)
        tmp=pre[target*7:target*7+7].copy(); base=target*7
        for gi in inds:
            if base <= gi < base+7: tmp[int(gi-base)]^=1
        assert syndrome7(tmp)==0,(fam,target,syndrome7(tmp))
    ref=pre.copy(); dmg=pre.copy(); dmg[inds]^=1
    pmask=np.zeros(WIDTH,dtype=bool); pmask[inds]=True; outside=~pmask
    telr=init_tel(); teld=init_tel(); pcurve=[]; lcurve=[]; flags=[]; hm={}
    for h,bit in enumerate(future,start=1):
        ref_log=decode_state(ref).copy()
        step(ref,int(bit),mapped,rules,method,ref_logical=None,tel=telr)
        step(dmg,int(bit),mapped,rules,method,ref_logical=ref_log,tel=teld)
        pd=dmg!=ref; ld=decode_state(dmg)!=decode_state(ref)
        pdiv=float(np.mean(pd)); ldiv=float(np.mean(ld)); outdiv=float(np.mean(pd[outside])); exact=bool(not np.any(ld))
        pcurve.append(pdiv); lcurve.append(ldiv); flags.append(exact)
        if h in HORIZONS: hm[f"h{h}"]={"logical_data_divergence":ldiv,"whole_state_divergence":pdiv,"outside_lesion_divergence":outdiv,"exact_logical_match":exact}
    rt=None
    for h in range(1,POST_STEPS+1):
        if all(flags[h-1:]): rt=h; break
    delta={k:int(teld[k]-telr[k]) for k in telr}
    return {"family":fam,"lesion_indices":[int(x) for x in inds],"actual_lesion_cardinality":int(len(inds)),"horizons":hm,"physical_divergence_area":float(np.sum(pcurve)),"logical_divergence_area":float(np.sum(lcurve)),"sustained_exact_logical_recovery":bool(rt is not None),"logical_recovery_time":rt,"repair_delta":delta}

def one_world(seed):
    rng=np.random.default_rng(np.random.PCG64(seed)); u=rng.integers(0,2,size=DAMAGE_AFTER_STEPS+POST_STEPS,dtype=np.uint8)
    mapped=mapped_logical(rng); rules=mixed_rules(rng,LOGICAL_BITS); future=u[DAMAGE_AFTER_STEPS:]; mp=mapped_phys(mapped); methods={}
    for m in METHODS:
        pre=prefix(u,mapped,rules,m); ctl=no_damage(pre,future,mapped,rules,m)
        sc=[one_scenario(pre,future,mapped,rules,m,fam,inds,mp) for fam,inds in lesion_scenarios()]
        methods[m]={"no_damage_control":bool(ctl),"scenarios":sc}
    return {"seed":int(seed),"mapped_logical":[int(x) for x in mapped],"methods":methods}

def q(v,p): return float(np.quantile(np.asarray(v,dtype=np.float64),p))

def famrows(rows,m,f): return [s for r in rows for s in r["methods"][m]["scenarios"] if s["family"]==f]

def summarize_family(scs):
    o={"scenario_count":len(scs),"horizons":{}}
    for h in HORIZONS:
        k=f"h{h}"; o["horizons"][k]={
            "logical_data_divergence_median":q([s["horizons"][k]["logical_data_divergence"] for s in scs],.5),
            "whole_state_divergence_median":q([s["horizons"][k]["whole_state_divergence"] for s in scs],.5),
            "outside_lesion_divergence_median":q([s["horizons"][k]["outside_lesion_divergence"] for s in scs],.5),
            "exact_logical_match_rate":float(np.mean([s["horizons"][k]["exact_logical_match"] for s in scs]))}
    o["logical_divergence_area_median"]=q([s["logical_divergence_area"] for s in scs],.5)
    o["physical_divergence_area_median"]=q([s["physical_divergence_area"] for s in scs],.5)
    o["sustained_exact_logical_recovery_rate"]=float(np.mean([s["sustained_exact_logical_recovery"] for s in scs]))
    for key in ("syndrome_positive","repairs","false_repairs","abstentions","unanimous_candidates","majority2_candidates","all_different"):
        vals=[s["repair_delta"][key] for s in scs]; o[key+"_sum"]=int(np.sum(vals)); o[key+"_median"]=q(vals,.5)
    o["false_repair_fraction"]=float(o["false_repairs_sum"]/o["repairs_sum"]) if o["repairs_sum"] else 0.0
    return o

def summarize(rows):
    fams=tuple(EXPECTED.keys())
    valid=all(r["methods"][m]["no_damage_control"] for r in rows for m in METHODS)
    o={"worlds":len(rows),"mechanical_valid":bool(valid),"methods":{}}
    for m in METHODS: o["methods"][m]={f:summarize_family(famrows(rows,m,f)) for f in fams}
    x=o["methods"]["MAJORITY3"]["SILENT_DATA3"]
    repair_signal=(x["horizons"]["h1"]["logical_data_divergence_median"]==0 and x["sustained_exact_logical_recovery_rate"]>=.9 and x["false_repair_fraction"]<=.01 and x["logical_divergence_area_median"]==0)
    m=o["methods"]["MAJORITY3"]["SILENT_DATA3_PLUS_ONE_WITNESS1"]
    u=o["methods"]["UNANIMOUS3"]["SILENT_DATA3_PLUS_ONE_WITNESS1"]
    onebad=(m["horizons"]["h1"]["logical_data_divergence_median"]==0 and m["sustained_exact_logical_recovery_rate"]>=.9 and m["false_repair_fraction"]<=.01 and u["sustained_exact_logical_recovery_rate"]<m["sustained_exact_logical_recovery_rate"])
    hs=o["methods"]["MAJORITY3"]["ONE_WITNESS1_ONLY"]
    safety=(hs["false_repairs_sum"]==0 and hs["horizons"]["h4"]["logical_data_divergence_median"]==0)
    d=o["methods"]["MAJORITY3"]["DISTRIBUTED_ONE_BAD_WITNESS"]
    dist=(d["horizons"]["h4"]["logical_data_divergence_median"]==0 and d["sustained_exact_logical_recovery_rate"]>=.75)
    bad=[]
    for meth in ("PAIR2","UNANIMOUS3","MAJORITY3"):
        for fam in ("SILENT_DATA3_PLUS_TWO_WITNESS2","TWO_WITNESS2_ONLY"):
            if o["methods"][meth][fam]["false_repair_fraction"]>.10:
                bad.append(meth); break
    us=o["methods"]["UNANIMOUS3"]["TWO_WITNESS2_ONLY"]
    unanimity_safe=(us["false_repairs_sum"]==0 and us["horizons"]["h4"]["logical_data_divergence_median"]==0)
    o["three_witness_repair_signal"]=bool(repair_signal)
    o["one_bad_witness_tolerance_signal"]=bool(onebad)
    o["one_bad_witness_healthy_target_safety"]=bool(safety)
    o["distributed_quorum_signal"]=bool(dist)
    o["two_bad_witness_boundary_methods"]=sorted(set(bad))
    o["unanimous_safety_signal"]=bool(unanimity_safe)
    return o

def encode_json(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def run():
    rows=[one_world(WORLD_START+i) for i in range(WORLD_COUNT)]
    return {"schema":"yggdrasil.dg1r-05e-three-witness-quorum.v1","rows":rows,"summary":summarize(rows),"worlds":len(rows),"seed_start":WORLD_START,"seed_end":WORLD_START+WORLD_COUNT-1}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",required=True); a=ap.parse_args(); obj=run(); raw=(encode_json(obj)+"\n").encode(); Path(a.out).write_bytes(raw); print(encode_json({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"summary":obj["summary"],"worlds":obj["worlds"]}))

if __name__=="__main__": main()