#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
import numpy as np

WIDTH=128; BLOCKS=12; LOGICAL_BITS=48; POST_STEPS=32; DAMAGE_AFTER_STEPS=1024
WORLD_START=20260926059000; WORLD_COUNT=8; HORIZONS=(1,4,8,16,32); SUPPORT_THRESHOLD=2
MIX_RULES=np.asarray([90,150,110,22,30],dtype=np.uint16)
METHODS=("GREEDY_BASELINE","CROSSPLANE2_GATE","CROSSPLANE2_DETECT_ONLY")
MAPPED_BLOCKS=np.asarray([1,4,7,10],dtype=np.int64)
HYPER_EDGES=[
(0,2,7,9),(1,3,6,11),(4,5,9,10),(2,3,5,8),(0,1,4,8),
(6,7,8,10),(2,4,6,11),(0,3,5,7),(1,7,10,11),(1,5,6,9),
(3,8,9,10),(0,4,8,11),(0,2,6,10),(1,3,4,7),(2,5,7,11),
(2,3,4,10),(0,1,5,10),(0,3,9,11),(1,2,8,9),(4,6,7,9),]
H=np.zeros((20,12),dtype=np.uint8)
for i,e in enumerate(HYPER_EDGES):H[i,list(e)]=1
FAMILIES=("LOCAL_DATA2_D6","DISTRIBUTED_DATA2","DATA2_PLUS_CHECK2_D6","DATA2_PLUS_CHECK3_D7","CHECK4_BIT0_D6","CHECK4_BIT0_D7","CHECK4_BITS01_D6","SINGLE_DATA1_D6")
EXPECTED={
"LOCAL_DATA2_D6":(2,0),"DISTRIBUTED_DATA2":(4,0),"DATA2_PLUS_CHECK2_D6":(2,2),"DATA2_PLUS_CHECK3_D7":(2,3),
"CHECK4_BIT0_D6":(0,4),"CHECK4_BIT0_D7":(0,4),"CHECK4_BITS01_D6":(0,8),"SINGLE_DATA1_D6":(1,0)}


def eca_step_mixed(s,r):
    l=np.roll(s,1);rr=np.roll(s,-1);idx=(l<<2)|(s<<1)|rr
    return ((r>>idx)&1).astype(np.uint8)
def mixed_rules(rng,w):
    reps=w//len(MIX_RULES);rem=w%len(MIX_RULES);a=np.concatenate((np.tile(MIX_RULES,reps),MIX_RULES[:rem])).astype(np.uint16);rng.shuffle(a);return a
def mapped_logical(rng):
    offs=rng.integers(0,4,size=len(MAPPED_BLOCKS),dtype=np.int64);return np.asarray([int(b*4+o) for b,o in zip(MAPPED_BLOCKS,offs)],dtype=np.int64)
def incident_slots(b):return [i for i,e in enumerate(HYPER_EDGES) if b in e]
def encode_state(logical):
    out=np.zeros(WIDTH,dtype=np.uint8);out[:48]=logical
    for i,e in enumerate(HYPER_EDGES):
        v=np.zeros(4,dtype=np.uint8)
        for b in e:v^=logical[b*4:(b+1)*4]
        out[48+i*4:48+(i+1)*4]=v
    return out
def decode_state(state):return state[:48].copy()
def syndrome_matrix(state):
    logical=decode_state(state).reshape(12,4);checks=state[48:].reshape(20,4);return checks^((H@logical)&1)

def infer_greedy(state):
    syn=syndrome_matrix(state);flips=np.zeros((12,4),dtype=np.uint8);final_syn=0;iters=0
    for k in range(4):
        s=syn[:,k].copy();used=np.zeros(12,dtype=bool);it=0
        while it<4:
            cur=int(np.sum(s));best_red=0;best_j=None
            for j in range(12):
                if used[j]:continue
                red=cur-int(np.sum(s^H[:,j]))
                if red>best_red:best_red=red;best_j=j
            if best_j is None or best_red<=0:break
            used[best_j]=True;flips[best_j,k]^=1;s^=H[:,best_j];it+=1
        iters+=it;final_syn+=int(np.sum(s))
    return flips,final_syn,iters

def init_tel():return {"inferred_flips":0,"applied_flips":0,"abstained_inferred_flips":0,"false_inferred_flips":0,"false_applied_flips":0,"final_syndrome_weight":0,"decoder_iterations":0,"support_hist_0":0,"support_hist_1":0,"support_hist_2":0,"support_hist_3":0,"support_hist_4":0,"max_plane_support_sum":0}

def repair(state,method,ref,tel):
    flips,final_syn,iters=infer_greedy(state);support=np.sum(flips,axis=1,dtype=np.int64);logical=decode_state(state).reshape(12,4);refm=None if ref is None else ref.reshape(12,4)
    tel["final_syndrome_weight"]+=int(final_syn);tel["decoder_iterations"]+=int(iters);tel["max_plane_support_sum"]+=int(np.max(support) if len(support) else 0)
    for v in support:tel[f"support_hist_{int(v)}"]+=1
    for b in range(12):
        for k in range(4):
            if not flips[b,k]:continue
            tel["inferred_flips"]+=1;post=int(logical[b,k]^1)
            if refm is not None and post!=int(refm[b,k]):tel["false_inferred_flips"]+=1
            apply=False
            if method=="GREEDY_BASELINE":apply=True
            elif method=="CROSSPLANE2_GATE":apply=bool(support[b]>=SUPPORT_THRESHOLD)
            elif method=="CROSSPLANE2_DETECT_ONLY":apply=False
            else:raise KeyError(method)
            if not apply:
                tel["abstained_inferred_flips"]+=1;continue
            if refm is not None and post!=int(refm[b,k]):tel["false_applied_flips"]+=1
            logical[b,k]^=1;tel["applied_flips"]+=1
    state[:48]=logical.reshape(48)
def step(state,bit,mapped,rules,method,ref=None,tel=None):
    if tel is None:tel=init_tel()
    repair(state,method,ref,tel);logical=decode_state(state);logical[mapped]=np.uint8(bit);logical=eca_step_mixed(logical,rules);state[:]=encode_state(logical);return tel
def prefix(u,mapped,rules,method):
    s=encode_state(np.zeros(LOGICAL_BITS,dtype=np.uint8))
    for t in range(DAMAGE_AFTER_STEPS):step(s,int(u[t]),mapped,rules,method)
    return s

def data_pos(b,k):return b*4+k
def check_pos(slot,k):return 48+slot*4+k
def first_incident(b,n):
    x=incident_slots(b);assert len(x)>=n;return x[:n]
def scenario(fam):
    logical=[];checks=[]
    if fam=="LOCAL_DATA2_D6":logical=[data_pos(5,0),data_pos(5,1)]
    elif fam=="DISTRIBUTED_DATA2":logical=[data_pos(2,0),data_pos(2,1),data_pos(8,0),data_pos(8,1)]
    elif fam=="DATA2_PLUS_CHECK2_D6":logical=[data_pos(5,0),data_pos(5,1)];checks=[check_pos(i,0) for i in first_incident(5,2)]
    elif fam=="DATA2_PLUS_CHECK3_D7":logical=[data_pos(2,0),data_pos(2,1)];checks=[check_pos(i,0) for i in first_incident(2,3)]
    elif fam=="CHECK4_BIT0_D6":checks=[check_pos(i,0) for i in first_incident(5,4)]
    elif fam=="CHECK4_BIT0_D7":checks=[check_pos(i,0) for i in first_incident(2,4)]
    elif fam=="CHECK4_BITS01_D6":
        for i in first_incident(5,4):checks.extend([check_pos(i,0),check_pos(i,1)])
    elif fam=="SINGLE_DATA1_D6":logical=[data_pos(5,0)]
    else:raise KeyError(fam)
    return tuple(logical+checks),len(logical),len(checks)
def validate_design():
    deg=tuple(int(np.sum(H[:,b])) for b in range(12));assert deg==(7,7,7,7,7,6,6,7,6,7,7,6)
    for f in FAMILIES:
        inds,lc,cc=scenario(f);assert (lc,cc)==EXPECTED[f];assert len(inds)==lc+cc;assert len(set(inds))==len(inds)
def no_damage(pre,future,mapped,rules,method):
    a=pre.copy();b=pre.copy()
    for bit in future:
        ra=decode_state(a).copy();rb=decode_state(b).copy();step(a,int(bit),mapped,rules,method,ref=ra);step(b,int(bit),mapped,rules,method,ref=rb)
        if np.any(a!=b):return False
    return True
def one_scenario(pre,future,mapped,rules,method,fam):
    inds,lc,cc=scenario(fam);inds=np.asarray(inds,dtype=np.int64);assert int(np.sum(inds<48))==lc;assert int(np.sum(inds>=48))==cc;assert not np.any(np.isin(inds[inds<48],mapped))
    ref=pre.copy();dmg=pre.copy();dmg[inds]^=1;tr=init_tel();td=init_tel();pc=[];lc_curve=[];flags=[];hm={}
    first_support=None
    for h,bit in enumerate(future,start=1):
        if h==1:
            fl,_,_=infer_greedy(dmg);first_support=[int(x) for x in np.sum(fl,axis=1,dtype=np.int64)]
        rlog=decode_state(ref).copy();step(ref,int(bit),mapped,rules,method,ref=None,tel=tr);step(dmg,int(bit),mapped,rules,method,ref=rlog,tel=td)
        pd=dmg!=ref;ld=decode_state(dmg)!=decode_state(ref);p=float(np.mean(pd));l=float(np.mean(ld));exact=bool(not np.any(ld));pc.append(p);lc_curve.append(l);flags.append(exact)
        if h in HORIZONS:hm[f"h{h}"]={"physical_divergence":p,"logical_divergence":l,"exact_logical_match":exact}
    rt=None
    for h in range(1,POST_STEPS+1):
        if all(flags[h-1:]):rt=h;break
    delta={k:int(td[k]-tr[k]) for k in tr}
    return {"family":fam,"lesion_indices":[int(x) for x in inds],"logical_flip_count":lc,"integrity_flip_count":cc,"first_plane_support":first_support,"horizons":hm,"logical_divergence_area":float(np.sum(lc_curve)),"physical_divergence_area":float(np.sum(pc)),"sustained_exact_logical_recovery":bool(rt is not None),"logical_recovery_time":rt,"decoder_delta":delta}
def one_world(seed):
    validate_design();rng=np.random.default_rng(np.random.PCG64(seed));u=rng.integers(0,2,size=DAMAGE_AFTER_STEPS+POST_STEPS,dtype=np.uint8);mapped=mapped_logical(rng);rules=mixed_rules(rng,LOGICAL_BITS);future=u[DAMAGE_AFTER_STEPS:];methods={}
    for m in METHODS:
        pre=prefix(u,mapped,rules,m);ctl=no_damage(pre,future,mapped,rules,m);methods[m]={"no_damage_control":bool(ctl),"scenarios":[one_scenario(pre,future,mapped,rules,m,f) for f in FAMILIES]}
    return {"seed":int(seed),"mapped_logical":[int(x) for x in mapped],"methods":methods}
def q(v,p):return float(np.quantile(np.asarray(v,dtype=np.float64),p))
def fr(rows,m,f):return [s for r in rows for s in r["methods"][m]["scenarios"] if s["family"]==f]
def sf(scs):
    o={"scenario_count":len(scs),"horizons":{}}
    for h in HORIZONS:
        k=f"h{h}";o["horizons"][k]={"logical_divergence_median":q([s["horizons"][k]["logical_divergence"] for s in scs],.5),"physical_divergence_median":q([s["horizons"][k]["physical_divergence"] for s in scs],.5),"exact_logical_match_rate":float(np.mean([s["horizons"][k]["exact_logical_match"] for s in scs]))}
    o["logical_divergence_area_median"]=q([s["logical_divergence_area"] for s in scs],.5);o["physical_divergence_area_median"]=q([s["physical_divergence_area"] for s in scs],.5);o["sustained_exact_logical_recovery_rate"]=float(np.mean([s["sustained_exact_logical_recovery"] for s in scs]))
    for k in ("inferred_flips","applied_flips","abstained_inferred_flips","false_inferred_flips","false_applied_flips","final_syndrome_weight","decoder_iterations"):
        vals=[s["decoder_delta"][k] for s in scs];o[k+"_sum"]=int(np.sum(vals));o[k+"_median"]=q(vals,.5)
    o["false_applied_flip_fraction"]=float(o["false_applied_flips_sum"]/o["applied_flips_sum"]) if o["applied_flips_sum"] else 0.0
    o["first_plane_supports"]=[s["first_plane_support"] for s in scs]
    return o
def passes(x):return x["logical_divergence_area_median"]==0 and x["sustained_exact_logical_recovery_rate"]>=.9 and x["false_applied_flip_fraction"]<=.01
def summarize(rows):
    valid=all(r["methods"][m]["no_damage_control"] for r in rows for m in METHODS);o={"worlds":len(rows),"mechanical_valid":bool(valid),"methods":{}}
    for m in METHODS:o["methods"][m]={f:sf(fr(rows,m,f)) for f in FAMILIES}
    g=o["methods"]["CROSSPLANE2_GATE"];b=o["methods"]["GREEDY_BASELINE"]
    suppress=(g["CHECK4_BIT0_D6"]["false_applied_flips_sum"]==0 and g["CHECK4_BIT0_D6"]["logical_divergence_area_median"]==0 and g["CHECK4_BIT0_D7"]["false_applied_flips_sum"]==0 and g["CHECK4_BIT0_D7"]["logical_divergence_area_median"]==0 and (b["CHECK4_BIT0_D6"]["false_applied_flips_sum"]>0 or b["CHECK4_BIT0_D7"]["false_applied_flips_sum"]>0))
    preserve=all(passes(g[f]) for f in ("LOCAL_DATA2_D6","DISTRIBUTED_DATA2","DATA2_PLUS_CHECK2_D6","DATA2_PLUS_CHECK3_D7"))
    corr=(g["CHECK4_BITS01_D6"]["false_applied_flips_sum"]>0 or g["CHECK4_BITS01_D6"]["logical_divergence_area_median"]>0)
    single_cost={m:o["methods"][m]["SINGLE_DATA1_D6"] for m in ("GREEDY_BASELINE","CROSSPLANE2_GATE")}
    o["crossplane_false_repair_suppression"]=bool(suppress);o["logical_repair_preservation"]=bool(preserve);o["crossplane_confidence_signal"]=bool(suppress and preserve);o["crossplane_correlated_failure"]=bool(corr);o["single_bit_sensitivity_cost"]={m:{"logical_divergence_area_median":x["logical_divergence_area_median"],"sustained_exact_logical_recovery_rate":x["sustained_exact_logical_recovery_rate"],"false_applied_flips_sum":x["false_applied_flips_sum"]} for m,x in single_cost.items()};o["support_threshold"]=SUPPORT_THRESHOLD
    return o
def encode_json(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def run():
    rows=[one_world(WORLD_START+i) for i in range(WORLD_COUNT)];return {"schema":"yggdrasil.dg1r-05i-crossplane-confidence.v1","rows":rows,"summary":summarize(rows),"worlds":len(rows),"seed_start":WORLD_START,"seed_end":WORLD_START+WORLD_COUNT-1}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",required=True);a=ap.parse_args();obj=run();raw=(encode_json(obj)+"\n").encode();Path(a.out).write_bytes(raw);print(encode_json({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"summary":obj["summary"],"worlds":obj["worlds"]}))
if __name__=="__main__":main()