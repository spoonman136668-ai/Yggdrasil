#!/usr/bin/env python3
import argparse, hashlib, importlib.util, json, time
from pathlib import Path
import numpy as np

PARENT='dg1r_04_nanite_stabilization_v1.py'; START=20260926050000; N=8
METHODS=('SLOW128_MIXED1','INERT112_16_FAST4','REFRACTORY112_16_FAST4_T50','REFRACTORY112_16_FAST4_T35','BUDGET112_16_FAST4_K1','BUDGET112_16_FAST4_K2','RAW32','RANDOM512')
ACTIVE=METHODS[2:6]; RECA=METHODS[:6]

def load_parent():
    p=Path(__file__).resolve().parent/PARENT; s=importlib.util.spec_from_file_location('p',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def cfg(name):
    return {'REFRACTORY112_16_FAST4_T50':('r',.50),'REFRACTORY112_16_FAST4_T35':('r',.35),'BUDGET112_16_FAST4_K1':('b',1),'BUDGET112_16_FAST4_K2':('b',2)}[name]

def step(base,p,w,c,rules,name,stats=None):
    mode,arg=cfg(name); prop=base.eca_step_mixed(w,rules); old=w.copy(); flips=np.array([np.sum(prop[j*7:(j+1)*7]!=old[j*7:(j+1)*7]) for j in range(16)],dtype=int)
    veto=0; forced=0; realized=0
    if mode=='r':
        for j,f in enumerate(flips):
            a,b=j*7,(j+1)*7
            if c[j]: w[a:b]=prop[a:b]; c[j]=0; realized+=int(f); forced+=1
            elif f/7>arg: c[j]=1; veto+=1
            else: w[a:b]=prop[a:b]; c[j]=0; realized+=int(f)
    else:
        elig=[j for j,f in enumerate(flips) if f>0]; elig.sort(key=lambda j:(-int(flips[j]),j)); blocked=set(elig[:int(arg)]); c.fill(0)
        for j,f in enumerate(flips):
            a,b=j*7,(j+1)*7
            if j in blocked: c[j]=1; veto+=1
            else: w[a:b]=prop[a:b]; realized+=int(f)
    if stats is not None:
        stats['dec']+=16; stats['veto']+=veto; stats['forced']+=forced; stats['prop']+=int(flips.sum()); stats['real']+=realized; stats['bits']+=112; stats['vpm'].append(veto)

def evolve(base,p,w,c,bit,mapped,rules,name,rec=None,stats=None):
    w[mapped]=np.uint8(bit)
    for micro in range(4):
        step(base,p,w,c,rules,name,stats)
        if rec is not None:
            off=micro*128; rec[off:off+112]=w; rec[off+112:off+128]=c

def features(base,p,u,mapped,rules,name):
    w=np.zeros(112,np.uint8); c=np.zeros(16,np.uint8); x=np.empty((len(u),512),np.uint8); st={'dec':0,'veto':0,'forced':0,'prop':0,'real':0,'bits':0,'vpm':[]}; snap=None
    for t,bit in enumerate(u):
        evolve(base,p,w,c,int(bit),mapped,rules,name,x[t],st)
        if t==512: snap=np.r_[w.copy(),c.copy()]
    mode,_=cfg(name); tele={'veto_fraction':st['veto']/st['dec'],'proposed_worker_change_fraction':st['prop']/st['bits'],'realized_worker_change_fraction':st['real']/st['bits'],'forced_release_fraction':st['forced']/st['dec'] if mode=='r' else None,'mean_vetoes_per_active_microtick':float(np.mean(st['vpm'])),'max_vetoes_per_active_microtick':int(max(st['vpm']))}
    return x,snap,tele

def perturb(base,p,u,mapped,rules,name,snap):
    aw=snap[:112].copy(); ac=snap[112:].copy(); bw=aw.copy(); bc=ac.copy(); bw[98]^=1; out={}
    for h in range(1,17):
        bit=int(u[512+h]); evolve(base,p,aw,ac,bit,mapped,rules,name); evolve(base,p,bw,bc,bit,mapped,rules,name)
        if h in (1,4,8,16): out[f'h{h}']=float(np.mean(np.r_[aw,ac]!=np.r_[bw,bc]))
    return out

def resources(base,p,name):
    if name=='SLOW128_MIXED1': return base.resource_record(name)
    if name=='INERT112_16_FAST4': return p.resource_record(base,name)
    return {'persistent_state_bits':128,'worker_state_bits':112,'controller_state_bits':16,'readout_feature_bits':512,'worker_ca_updates_per_external_step':448,'controller_decisions_per_external_step':64,'mapped_overwrite_writes_per_external_step':8,'trainable_reservoir_parameters':0,'trainable_readout_scalars_per_task':513}

def world(p,seed):
    b=p.load_base(); rng=np.random.default_rng(np.random.PCG64(seed)); u=rng.integers(0,2,size=b.SEQ_LEN,dtype=np.uint8); mapped=p.worker_mapped_positions(rng); mixed=b.mixed_rule_assignment(rng); rules=mixed[:112].copy(); rw=rng.choice(np.array([-1,1],np.int8),size=(32,512)); rb=rng.integers(-4,5,size=512,dtype=np.int16); y=b.build_targets(u); out={}; rt={}
    t=time.perf_counter(); x,s=b.run_reca_features(u,mapped,mixed,'SLOW128_MIXED1'); rt['SLOW128_MIXED1']=time.perf_counter()-t; m=b.method_metrics(x,y,b.perturbation_profile(u,mapped,mixed,'SLOW128_MIXED1',s)); m['resources']=resources(b,p,'SLOW128_MIXED1'); m['stabilizer_telemetry']=None; out['SLOW128_MIXED1']=m
    t=time.perf_counter(); x,s,tele=p.run_nanite_features(b,u,mapped,rules,'INERT112_16_FAST4'); rt['INERT112_16_FAST4']=time.perf_counter()-t; m=b.method_metrics(x,y,p.perturbation_nanite(b,u,mapped,rules,'INERT112_16_FAST4',s)); m['resources']=resources(b,p,'INERT112_16_FAST4'); m['stabilizer_telemetry']=tele; out['INERT112_16_FAST4']=m
    for name in ACTIVE:
        t=time.perf_counter(); x,s,tele=features(b,p,u,mapped,rules,name); rt[name]=time.perf_counter()-t; m=b.method_metrics(x,y,perturb(b,p,u,mapped,rules,name,s)); m['resources']=resources(b,p,name); m['stabilizer_telemetry']=tele; out[name]=m
    t=time.perf_counter(); raw=b.raw32_features(u); rt['RAW32']=time.perf_counter()-t; out['RAW32']=b.method_metrics(raw,y,None); out['RAW32']['resources']=b.resource_record('RAW32'); out['RAW32']['stabilizer_telemetry']=None
    t=time.perf_counter(); rnd=b.random512_features(raw,rw,rb); rt['RANDOM512']=time.perf_counter()-t; out['RANDOM512']=b.method_metrics(rnd,y,None); out['RANDOM512']['resources']=b.resource_record('RANDOM512'); out['RANDOM512']['stabilizer_telemetry']=None
    return {'seed':int(seed),'mapped_worker_positions':[int(v) for v in mapped],'methods':out},rt

def q(v,p): return float(np.quantile(np.asarray(v,float),p))
def summethod(p,rows,name):
    b=p.load_base(); mr=[r['methods'][name] for r in rows]; s={'tasks':{t:{'median':q([x['tasks'][t] for x in mr],.5),'p10':q([x['tasks'][t] for x in mr],.1)} for t in b.TASKS},'memory_score':{'median':q([x['memory_score'] for x in mr],.5)},'nonlinear_score':{'median':q([x['nonlinear_score'] for x in mr],.5)},'state_entropy':{'median':q([x['state_entropy'] for x in mr],.5)},'feature_rank':{'median':q([x['feature_rank'] for x in mr],.5)},'feature_rank_fraction':{'median':q([x['feature_rank_fraction'] for x in mr],.5)},'resources':mr[0]['resources']}
    if name in RECA:
        s['perturbation']={f'h{h}':{'median':q([x['perturbation'][f'h{h}'] for x in mr],.5)} for h in (1,4,8,16)}; mem=s['memory_score']['median']>=.70 and s['tasks']['D16']['median']>=.70; nh=sum(s['tasks'][t]['median']>=.60 for t in ('XOR3_11','PARITY5','MOTIF2_12')); non=s['nonlinear_score']['median']>=.60 and nh>=2; bal=.20<=s['state_entropy']['median']<=.95 and .01<=s['perturbation']['h16']['median']<=.75; s['classification']={'memory_capable':mem,'nonlinear_capable':non,'dynamically_balanced':bal,'temporal_substrate_candidate':mem and non and bal}
    tele=[x['stabilizer_telemetry'] for x in mr if x['stabilizer_telemetry'] is not None]
    if tele:
        s['stabilizer_telemetry']={'veto_fraction':{'median':q([x['veto_fraction'] for x in tele],.5)},'proposed_worker_change_fraction':{'median':q([x['proposed_worker_change_fraction'] for x in tele],.5)},'realized_worker_change_fraction':{'median':q([x['realized_worker_change_fraction'] for x in tele],.5)}}
        if name.startswith('REFRACTORY'): s['stabilizer_telemetry']['forced_release_fraction']={'median':q([x['forced_release_fraction'] for x in tele],.5)}
        if name.startswith('BUDGET'): s['stabilizer_telemetry']['mean_vetoes_per_active_microtick']={'median':q([x['mean_vetoes_per_active_microtick'] for x in tele],.5)}; s['stabilizer_telemetry']['max_vetoes_per_active_microtick']=int(max(x['max_vetoes_per_active_microtick'] for x in tele))
    else: s['stabilizer_telemetry']=None
    s['plasticity_recovery']=bool(s['state_entropy']['median']>=.20 and s['feature_rank_fraction']['median']>=.15) if name in ACTIVE else None
    return s

def delta(rows,name,ref):
    d={}
    for k in ('D1','D4','D8','D16','D32'): d[k]={'median':q([r['methods'][name]['tasks'][k]-r['methods'][ref]['tasks'][k] for r in rows],.5)}
    for k in ('memory_score','nonlinear_score'): d[k]={'median':q([r['methods'][name][k]-r['methods'][ref][k] for r in rows],.5)}
    return d

def summary(p,rows):
    s={'worlds':len(rows),'methods':{n:summethod(p,rows,n) for n in METHODS},'relative_to_inert':{},'relative_to_slow128':{}}
    for n in ACTIVE: s['relative_to_inert'][n]=delta(rows,n,'INERT112_16_FAST4'); s['relative_to_slow128'][n]=delta(rows,n,'SLOW128_MIXED1')
    s['bounded_stabilization_signal']=any((s['relative_to_inert'][n]['D16']['median']>=.10 or s['relative_to_inert'][n]['D32']['median']>=.10) and s['relative_to_inert'][n]['nonlinear_score']['median']>=-.05 for n in ACTIVE)
    s['passive_comparison_signal']=any((s['relative_to_slow128'][n]['D16']['median']>=.10 or s['relative_to_slow128'][n]['D32']['median']>=.10) and s['relative_to_slow128'][n]['nonlinear_score']['median']>=-.05 for n in ACTIVE)
    s['nanite_memory_recovery']=any(s['methods'][n]['classification']['memory_capable'] for n in ACTIVE) and not s['methods']['INERT112_16_FAST4']['classification']['memory_capable'] and not s['methods']['SLOW128_MIXED1']['classification']['memory_capable']
    s['plasticity_recovery_methods']=[n for n in ACTIVE if s['methods'][n]['plasticity_recovery']]; s['temporal_substrate_candidates']=[n for n in RECA if s['methods'][n]['classification']['temporal_substrate_candidate']]; return s

def enc(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def run():
    p=load_parent(); rows=[]; rt=[]
    for i in range(N): r,t=world(p,START+i); rows.append(r); rt.append({'seed':r['seed'],'feature_generation_seconds':t})
    return {'schema':'yggdrasil.dg1r-05-bounded-intervention.v1','rows':rows,'summary':summary(p,rows),'worlds':N,'seed_start':START,'seed_end':START+N-1},{'schema':'yggdrasil.dg1r-05-runtime.v1','rows':rt}
def main():
    a=argparse.ArgumentParser(); a.add_argument('--out',required=True); a.add_argument('--runtime-out'); z=a.parse_args(); o,r=run(); raw=(enc(o)+'\n').encode(); Path(z.out).write_bytes(raw); Path(z.runtime_out).write_text(json.dumps(r,sort_keys=True,indent=2)+'\n') if z.runtime_out else None; print(enc({'output':z.out,'sha256':hashlib.sha256(raw).hexdigest(),'summary':o['summary'],'worlds':N}))
if __name__=='__main__': main()
