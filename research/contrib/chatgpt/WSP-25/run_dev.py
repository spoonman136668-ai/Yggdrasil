"""Frozen public DEV evaluator. Only this file can access truth/fixture IDs."""
import hashlib
import itertools
import json
import platform
import sys
import time
from pathlib import Path
from repair import LocalRepair,PAIRS
from controls import symbolic,trained
from world import World

ROOT=Path(__file__).resolve().parent
INPUTS=tuple(itertools.product((0,1),repeat=3))

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def y_state(model):return [model.base.viable[0][:],model.base.coeff[0][:],model.base.known[0][:]]
def retained(model):return (model.base.snapshot(),model.weights[:],model.occupied,model.residual,model.seen[:],model.labels[:])
def y_score(model,world):return sum(model.predict_y(u,x)==world.event(u,1,x)[2] for u,x in PAIRS)
def actual(world,query,pair):
    u,mask,x,y=query
    return world.event(u,mask,x,y,flip_pair=pair)
def acquire(world,pair):
    model=LocalRepair();events=[];chosen=[]
    for u in (0,1):
        e=world.event(u,flip_pair=pair);events.append(e);model.observe(e)
    for _ in range(2):
        action=model.choose()
        if action is None:break
        u,mask,value=action
        e=world.event(u,mask,value if mask==1 else 0,value if mask==2 else 0,flip_pair=pair)
        chosen.append(action);events.append(e);model.observe(e)
    return model,events,chosen

def run():
    tick=time.perf_counter();parent=json.loads((ROOT.parent/'WSP-24/result.json').read_text())
    c={key:0 for key in ('cases','prefix_events','prefix_interventions','validation_queries','joint_correct','allocated_nonlinear','false_affine_growth','old_Z_preserved','Y_states_preserved','Y_correct','cold','replay','no_probe_affine_correct','no_probe_nonlinear_correct','no_probe_confident_errors','disabled_affine_correct','disabled_nonlinear_abstentions','symbolic_correct','trained_correct','trained_fits','trained_steps','conflict_faults','conflict_Y_correct','conflict_memory_preserved','noise_wrong','noise_corrections','noise_clean_repeat_faults','noise_Y_preserved')}
    timings={'acquisition':0.,'candidate_update':0.,'symbolic':0.,'trained':0.};states=[];traces=[];functions=set();maxloss=0.;sizes=[]
    for record in parent['traces']:
        world=World(record['world'])
        for alternate in (0,1):
            pair=tuple(record['missing_pair']) if alternate else None
            start=time.perf_counter();model,events,chosen=acquire(world,pair);timings['acquisition']+=time.perf_counter()-start
            if events!=[tuple(e) for e in record['events']] or chosen!=[tuple(a) for a in record['chosen']] or not model.base.complete() or sum(model.seen)!=3:raise AssertionError('PREFIX_CUSTODY')
            c['cases']+=1;c['prefix_events']+=len(events);c['prefix_interventions']+=len(chosen)
            before=model.snapshot();old_y=y_state(model);old=tuple((i,label) for i,(s,label) in enumerate(zip(model.seen,model.labels)) if s)
            for u,x,y in INPUTS:
                p=model.joint(u,x,y);target=world.event(u,3,x,y,flip_pair=pair)[3]
                c['no_probe_nonlinear_correct' if alternate else 'no_probe_affine_correct']+=p==target
                c['no_probe_confident_errors']+=p is not None and p!=target
            query=model.validation_query()
            if query is None or query[2:]!=tuple(record['missing_pair']):raise AssertionError('SELF_SELECTED_QUERY')
            e=actual(world,query,pair);c['validation_queries']+=1
            start=time.perf_counter();model.observe(e);timings['candidate_update']+=time.perf_counter()-start
            events.append(e)
            if model.validation_query() is not None or model.fault_z:raise AssertionError('VALIDATION_BUDGET_OR_FAULT')
            c['allocated_nonlinear']+=alternate*model.occupied
            c['false_affine_growth']+=(1-alternate)*model.occupied
            c['Y_states_preserved']+=y_state(model)==old_y;c['Y_correct']+=y_score(model,world)
            c['old_Z_preserved']+=sum(model.joint(0,*PAIRS[i])==label for i,label in old)
            raw=model.snapshot();restored=LocalRepair.restore(raw);c['cold']+=restored.snapshot()==raw;states.append(raw);sizes.append(len(raw))
            restored.observe(e);c['replay']+=restored.snapshot()==raw
            start=time.perf_counter();table=symbolic(events);timings['symbolic']+=time.perf_counter()-start
            start=time.perf_counter();weights,steps,loss=trained(events);timings['trained']+=time.perf_counter()-start
            c['trained_fits']+=1;c['trained_steps']+=steps;maxloss=max(maxloss,loss)
            disabled=LocalRepair.restore(before);disabled.growth_enabled=0;disabled.observe(e)
            targets=[];predictions=[]
            for u,x,y in INPUTS:
                target=world.event(u,3,x,y,flip_pair=pair)[3];targets.append(target)
                p=model.joint(u,x,y);predictions.append(p)
                if restored.joint(u,x,y)!=p:raise AssertionError('COLD_OUTPUT')
                c['joint_correct']+=p==target;c['symbolic_correct']+=table[x,y]==target;c['trained_correct']+=int(weights[2*x+y]>=0)==target
                c['disabled_nonlinear_abstentions' if alternate else 'disabled_affine_correct']+=(disabled.joint(u,x,y) is None) if alternate else disabled.joint(u,x,y)==target
            if disabled.occupied:raise AssertionError('DISABLED_ALLOCATED')
            functions.add(tuple(world._c[:3])+tuple(targets[:4]))
            # Conflict on an original protected point: no knowledge overwrite.
            clone=LocalRepair.restore(raw);old_memory=retained(clone)
            a,b=PAIRS[old[0][0]];wrong=list(world.event(0,3,a,b,flip_pair=pair));wrong[3]^=1;clone.observe(tuple(wrong))
            c['conflict_faults']+=clone.fault_z==1 and all(clone.joint(*q) is None for q in INPUTS)
            c['conflict_memory_preserved']+=retained(clone)==old_memory;c['conflict_Y_correct']+=y_score(clone,world)
            if not alternate:
                noisy=LocalRepair.restore(before);corrupt=list(e);corrupt[3]^=1;noisy.observe(tuple(corrupt));c['noise_corrections']+=noisy.occupied
                c['noise_wrong']+=sum(noisy.joint(u,x,y)!=world.event(u,3,x,y)[3] for u,x,y in INPUTS)
                noisy.observe(e);c['noise_clean_repeat_faults']+=noisy.fault_z==1;c['noise_Y_preserved']+=y_score(noisy,world)==4
            traces.append({'world':record['world'],'alternate':alternate,'query':query,'prefix_actions':chosen,'prefix_events':events[:-1],'validation_event':e,'weights':model.weights,'occupied':model.occupied,'predictions':predictions,'checkpoint_sha256':hashlib.sha256(raw).hexdigest(),'trained_steps':steps,'trained_loss':loss})
    expected={'cases':128,'prefix_events':448,'prefix_interventions':192,'validation_queries':128,'joint_correct':1024,'allocated_nonlinear':64,'false_affine_growth':0,'old_Z_preserved':384,'Y_states_preserved':128,'Y_correct':512,'cold':128,'replay':128,'no_probe_affine_correct':512,'no_probe_nonlinear_correct':384,'no_probe_confident_errors':128,'disabled_affine_correct':512,'disabled_nonlinear_abstentions':512,'symbolic_correct':1024,'trained_correct':1024,'trained_fits':128,'conflict_faults':128,'conflict_Y_correct':512,'conflict_memory_preserved':128,'noise_wrong':128,'noise_corrections':64,'noise_clean_repeat_faults':64,'noise_Y_preserved':64}
    failures={key:{'actual':c[key],'expected':v} for key,v in expected.items() if c[key]!=v}
    report={'schema':'wsp25.local-causal-repair.v1','engineering':'PASS' if not failures else 'FAIL','frozen_hypothesis':'DEV_SUPPORTED' if not failures else 'NEGATIVE','scientific_classification':'Finite public DEV only; strongest symbolic and trained controls tie. No SCIENTIFIC_PASS.', 'counts':c,'failures':failures,'unique_causal_functions':len(functions),'trained_max_final_BCE':maxloss,'resident_binary_task_scalars':53,'extra_task_bits_vs_parent':16,'candidate_gradient_steps':0,'primary_actual_events':c['prefix_events']+c['validation_queries'],'negative_extra_feedback_events':256,'checkpoint_bytes_range':[min(sizes),max(sizes)],'checkpoint_digest_sha256':hashlib.sha256(b''.join(states)).hexdigest(),'trace_sha256':digest(traces),'timings_seconds':timings,'total_seconds':time.perf_counter()-tick,'environment':{'python':sys.version,'platform':platform.platform()},'traces':traces,'limitations':'Preprogrammed exact-parent correction template; reserved capacity, known causal order and extra validation feedback. All four Z-parent combinations observed before final score: no unseen-parent extrapolation. Noise produces 128 confident errors; later conflict causes local abstention. Authored deterministic finite worlds; no general primitive invention, superiority, production integration or arbitrary knowledge programming.'}
    print(json.dumps(report,sort_keys=True,indent=2))
    if failures:raise SystemExit(1)
    return report

if __name__=='__main__':run()
