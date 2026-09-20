#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
import numpy as np

WIDTH=128; LOGICAL_BLOCKS=12; LOGICAL_BITS=48; LOCAL74_BITS=84
POST_STEPS=32; DAMAGE_AFTER_STEPS=1024; WORLD_START=20260926054000; WORLD_COUNT=8
HORIZONS=(1,4,8,16,32); MIX_RULES=np.asarray([90,150,110,22,30],dtype=np.uint16)
METHODS=("SYNDROME_TRIGGER","NEIGHBOR_TRIGGER","HYBRID_TRIGGER","ONE_SIDE_TRIGGER","DETECT_ONLY")
MAPPED_BLOCKS=np.asarray([1,3,5,7,9,11],dtype=np.int64); DAMAGE_BLOCKS=(2,6,10); DIST_BLOCKS=(2,10)
DATA_OFF=(2,4,5,6)
EXPECTED={"THREE_DATA3_SILENT":3,"TWO_DATA2":2,"LEFT_CHECK1_ONLY":1,"BOTH_CHECK1_CORRELATED":2,"DATA3_PLUS_LEFT_CHECK1":4,"DISTRIBUTED_SILENT3":6}


def eca_step_mixed(s,r):
    l=np.roll(s,1); rr=np.roll(s,-1); idx=(l<<2)|(s<<1)|rr
    return ((r>>idx)&1).astype(np.uint8)
def mixed_rules(rng,w):
    reps=w//len(MIX_RULES); rem=w%len(MIX_RULES)
    a=np.concatenate((np.tile(MIX_RULES,reps),MIX_RULES[:rem])).astype(np.uint16); rng.shuffle(a); return a

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
def cross_index(edge,k): return LOCAL74_BITS+edge*4+k

def encode_tissue(logical):
    out=np.zeros(WIDTH,dtype=np.uint8)
    for b in range(LOGICAL_BLOCKS): out[b*7:b*7+7]=h74_encode4(logical[b*4:(b+1)*4])
    for e in range(LOGICAL_BLOCKS-1): out[LOCAL74_BITS+e*4:LOCAL74_BITS+(e+1)*4]=logical[e*4:(e+1)*4]^logical[(e+1)*4:(e+2)*4]
    return out
def decode(state):
    x=np.empty(LOGICAL_BITS,dtype=np.uint8)
    for b in range(LOGICAL_BLOCKS): x[b*4:(b+1)*4]=h74_decode7(state[b*7:b*7+7])
    return x

def init_tel(): return {"syndrome_positive":0,"neighbor_agreement":0,"neighbor_disagreement":0,"repairs":0,"false_repairs":0,"abstentions":0,"syndrome_led_repairs":0,"syndrome_blind_repairs":0}

def repair(state,method,ref_logical,tel):
    decoded=decode(state); cross=state[LOCAL74_BITS:].copy()
    for b in range(1,LOGICAL_BLOCKS-1):
        local=decoded[b*4:(b+1)*4]; syn=syndrome7(state[b*7:b*7+7])
        if syn: tel["syndrome_positive"]+=1
        left=decoded[(b-1)*4:b*4]^cross[(b-1)*4:b*4]
        right=decoded[(b+1)*4:(b+2)*4]^cross[b*4:(b+1)*4]
        agree=np.array_equal(left,right)
        if agree: tel["neighbor_agreement"]+=1
        else: tel["neighbor_disagreement"]+=1
        proposal=None; mode=None
        if method=="DETECT_ONLY": continue
        if method=="SYNDROME_TRIGGER":
            if syn!=0:
                if agree: proposal=left; mode="syndrome"
                else: tel["abstentions"]+=1
        elif method in ("NEIGHBOR_TRIGGER","HYBRID_TRIGGER"):
            if agree and not np.array_equal(local,left):
                proposal=left; mode="syndrome" if syn!=0 else "blind"
            elif not agree and (syn!=0 or method=="NEIGHBOR_TRIGGER"):
                tel["abstentions"]+=1
        elif method=="ONE_SIDE_TRIGGER":
            if not np.array_equal(local,left): proposal=left; mode="syndrome" if syn!=0 else "blind"
        if proposal is None: continue
        if ref_logical is not None and not np.array_equal(proposal,ref_logical[b*4:(b+1)*4]): tel["false_repairs"]+=1
        state[b*7:b*7+7]=h74_encode4(proposal); tel["repairs"]+=1
        if mode=="syndrome": tel["syndrome_led_repairs"]+=1
        else: tel["syndrome_blind_repairs"]+=1

def step(state,bit,mapped,rules,method,ref_logical=None,tel=None):
    if tel is None: tel=init_tel()
    repair(state,method,ref_logical,tel); logical=decode(state); logical[mapped]=np.uint8(bit); logical=eca_step_mixed(logical,rules); state[:]=encode_tissue(logical)
    return tel
def prefix(u,mapped,rules,method):
    s=encode_tissue(np.zeros(LOGICAL_BITS,dtype=np.uint8))
    for t in range(DAMAGE_AFTER_STEPS): step(s,int(u[t]),mapped,rules,method)
    return s
def mapped_phys(mapped): return np.asarray([tissue_phys_for_logical(int(lp)) for lp in mapped],dtype=np.int64)

def lesion_scenarios():
    out=[]
    for b in DAMAGE_BLOCKS:
        base=b*7
        out.append(("THREE_DATA3_SILENT",(base+2,base+4,base+5)))
        out.append(("TWO_DATA2",(base+2,base+4)))
        out.append(("LEFT_CHECK1_ONLY",(cross_index(b-1,0),)))
        out.append(("BOTH_CHECK1_CORRELATED",(cross_index(b-1,0),cross_index(b,0))))
        out.append(("DATA3_PLUS_LEFT_CHECK1",(base+2,base+4,base+5,cross_index(b-1,0))))
    inds=[]
    for b in DIST_BLOCKS:
        base=b*7; inds.extend((base+2,base+4,base+5))
    out.append(("DISTRIBUTED_SILENT3",tuple(inds)))
    return out

def no_damage(pre,future,mapped,rules,method):
    a=pre.copy(); b=pre.copy()
    for bit in future:
        la=decode(a).copy(); lb=decode(b).copy(); step(a,int(bit),mapped,rules,method,ref_logical=la); step(b,int(bit),mapped,rules,method,ref_logical=lb)
        if np.any(a!=b): return False
    return True

def one_scenario(pre,future,mapped,rules,method,fam,inds,mp):
    inds=np.asarray(inds,dtype=np.int64); assert len(inds)==EXPECTED[fam]; assert len(np.unique(inds))==EXPECTED[fam]; assert not np.any(np.isin(inds,mp))
    ref=pre.copy(); dmg=pre.copy(); dmg[inds]^=1; pmask=np.zeros(WIDTH,dtype=bool); pmask[inds]=True; outside=~pmask
    telr=init_tel(); teld=init_tel(); pcurve=[]; lcurve=[]; flags=[]; hm={}
    for h,bit in enumerate(future,start=1):
        ref_log=decode(ref).copy(); step(ref,int(bit),mapped,rules,method,ref_logical=None,tel=telr); step(dmg,int(bit),mapped,rules,method,ref_logical=ref_log,tel=teld)
        pd=dmg!=ref; ld=decode(dmg)!=decode(ref); pdiv=float(np.mean(pd)); ldiv=float(np.mean(ld)); rec=float(1-np.mean(pd[pmask])); outdiv=float(np.mean(pd[outside])); exact=bool(not np.any(ld)); pcurve.append(pdiv); lcurve.append(ldiv); flags.append(exact)
        if h in HORIZONS: hm[f"h{h}"]={"whole_state_divergence":pdiv,"damaged_site_recovery":rec,"logical_data_divergence":ldiv,"outside_lesion_divergence":outdiv,"exact_logical_match":exact}
    rt=None
    for h in range(1,POST_STEPS+1):
        if all(flags[h-1:]):rt=h;break
    delta={k:int(teld[k]-telr[k]) for k in telr}
    return {"family":fam,"lesion_indices":[int(x) for x in inds],"actual_lesion_cardinality":int(len(inds)),"horizons":hm,"physical_divergence_area":float(np.sum(pcurve)),"logical_divergence_area":float(np.sum(lcurve)),"sustained_exact_logical_recovery":bool(rt is not None),"logical_recovery_time":rt,"repair_delta":delta}
def one_world(seed):
    rng=np.random.default_rng(np.random.PCG64(seed)); u=rng.integers(0,2,size=DAMAGE_AFTER_STEPS+POST_STEPS,dtype=np.uint8); mapped=mapped_logical(rng); rules=mixed_rules(rng,LOGICAL_BITS); future=u[DAMAGE_AFTER_STEPS:]; mp=mapped_phys(mapped); methods={}
    for m in METHODS:
        pre=prefix(u,mapped,rules,m); ctl=no_damage(pre,future,mapped,rules,m); sc=[one_scenario(pre,future,mapped,rules,m,fam,inds,mp) for fam,inds in lesion_scenarios()]; methods[m]={"no_damage_control":bool(ctl),"scenarios":sc}
    return {"seed":int(seed),"mapped_logical":[int(x) for x in mapped],"methods":methods}
def q(v,p):return float(np.quantile(np.asarray(v,dtype=np.float64),p))
def famrows(rows,m,f):return [s for r in rows for s in r["methods"][m]["scenarios"] if s["family"]==f]
def summarize_family(scs):
    o={"scenario_count":len(scs),"horizons":{}}
    for h in HORIZONS:
        k=f"h{h}"; o["horizons"][k]={"logical_data_divergence_median":q([s["horizons"][k]["logical_data_divergence"] for s in scs],.5),"whole_state_divergence_median":q([s["horizons"][k]["whole_state_divergence"] for s in scs],.5),"outside_lesion_divergence_median":q([s["horizons"][k]["outside_lesion_divergence"] for s in scs],.5),"exact_logical_match_rate":float(np.mean([s["horizons"][k]["exact_logical_match"] for s in scs]))}
    o["logical_divergence_area_median"]=q([s["logical_divergence_area"] for s in scs],.5); o["physical_divergence_area_median"]=q([s["physical_divergence_area"] for s in scs],.5); o["sustained_exact_logical_recovery_rate"]=float(np.mean([s["sustained_exact_logical_recovery"] for s in scs]))
    for key in ("syndrome_positive","neighbor_agreement","neighbor_disagreement","repairs","false_repairs","abstentions","syndrome_led_repairs","syndrome_blind_repairs"):
        vals=[s["repair_delta"][key] for s in scs]; o[key+"_sum"]=int(np.sum(vals)); o[key+"_median"]=q(vals,.5)
    o["false_repair_fraction"]=float(o["false_repairs_sum"]/o["repairs_sum"]) if o["repairs_sum"] else 0.0
    return o
def summarize(rows):
    valid=all(r["methods"][m]["no_damage_control"] for r in rows for m in METHODS); o={"worlds":len(rows),"mechanical_valid":bool(valid),"methods":{}}
    fams=("THREE_DATA3_SILENT","TWO_DATA2","LEFT_CHECK1_ONLY","BOTH_CHECK1_CORRELATED","DATA3_PLUS_LEFT_CHECK1","DISTRIBUTED_SILENT3")
    for m in METHODS:o["methods"][m]={f:summarize_family(famrows(rows,m,f)) for f in fams}
    signals=[]
    for m in ("NEIGHBOR_TRIGGER","HYBRID_TRIGGER"):
        x=o["methods"][m]["THREE_DATA3_SILENT"]
        if x["horizons"]["h1"]["logical_data_divergence_median"]==0 and x["sustained_exact_logical_recovery_rate"]>=.9 and x["false_repair_fraction"]<=.01 and x["logical_divergence_area_median"]==0:signals.append(m)
    d=o["methods"]["HYBRID_TRIGGER"]["DISTRIBUTED_SILENT3"]
    dist=(d["horizons"]["h4"]["logical_data_divergence_median"]==0 and d["sustained_exact_logical_recovery_rate"]>=.75)
    l=o["methods"]["HYBRID_TRIGGER"]["LEFT_CHECK1_ONLY"]; safety=(l["false_repairs_sum"]==0 and l["horizons"]["h4"]["logical_data_divergence_median"]==0)
    corr=[]
    for m in ("NEIGHBOR_TRIGGER","HYBRID_TRIGGER"):
        x=o["methods"][m]["BOTH_CHECK1_CORRELATED"]
        if x["false_repair_fraction"]>.10:corr.append(m)
    o["syndrome_blind_repair_signal"]=bool(signals); o["syndrome_blind_signal_methods"]=signals; o["distributed_self_diagnosis_signal"]=bool(dist); o["one_source_damage_safety"]=bool(safety); o["correlated_consensus_failure_methods"]=corr
    return o
def encode(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def run():
    rows=[one_world(WORLD_START+i) for i in range(WORLD_COUNT)]; return {"schema":"yggdrasil.dg1r-05d-syndrome-blind-neighbor-trigger.v1","rows":rows,"summary":summarize(rows),"worlds":len(rows),"seed_start":WORLD_START,"seed_end":WORLD_START+WORLD_COUNT-1}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",required=True); a=ap.parse_args(); obj=run(); raw=(encode(obj)+"\n").encode(); Path(a.out).write_bytes(raw); print(encode({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"summary":obj["summary"],"worlds":obj["worlds"]}))
if __name__=="__main__":main()