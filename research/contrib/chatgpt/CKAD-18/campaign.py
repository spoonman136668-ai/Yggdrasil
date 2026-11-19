"""Complete the retained witnessed scope without changing the native learner."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_context_quarantine import NativeContextQuarantine
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner,coordinates
from yggdrasil.native_prior_hypothesis import input_order

SEEDS=(101,202,303)
NEW=(3,6,7,9,10,11,14,15)
OLD=(0,1,2,4,5,8,12,13)
MDP_PIN='e994f6adb0733c05eeae8dd19b0a4a36bb13946e1090b241023630b468276d1f'
DTR_PIN='016bf254ade33b936386abf7829ff90d765da71105e2beebcb130c95febe7d1d'
CONTROL_BLOB='845dc6fe3e39f1b59ff61b81ab98774c5efd76d8'


def need(ok,why):
    if not ok:raise RuntimeError('CKAD18_'+why)


def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def parent(seed):
    if seed==101:
        d=json.loads((HERE.parent/'CKAD-17/result.json').read_text())
        return HERE.parent/'CKAD-17'/d['checkpoint_name'],d['checkpoint_sha256']
    d=json.loads((HERE.parent/'CKAD-14/result.json').read_text())
    p=next(p for p in d['parents'] if p['seed']==seed)
    return HERE.parent/'CKAD-14'/p['checkpoint_name'],p['checkpoint_sha256']


def witness(seed):
    d=json.loads((HERE.parent/'CKAD-08/result.json').read_text())
    p=next(p for p in d['cases'] if p['seed']==seed);raw=(HERE.parent/'CKAD-08'/p['checkpoint_name']).read_bytes()
    need(digest(raw)==p['checkpoint_sha256'],'WITNESS_PIN')
    return raw,NativeContextQuarantine.restore(raw,digest(raw))


def rows_for(w,slot):
    a,r=coordinates(slot);seen=w._native._seen[slot]
    need(not w._failures[slot] and seen.bit_count()==512,'QUALIFIED_WITNESSES')
    return [[x&1023,x>>10,w.predict(a,x&1023,x>>10,retained=r)]
        for x in sorted(range(2048),key=input_order) if seen&(1<<x)]


def core(m):return [[m.predict(s,x&1023,x>>10) for x in range(2048)] for s in range(16)]


def probabilities(m):
    return {'mdp':[m.history_forecast(w,c,a,p) for w in range(4) for c in range(2) for a in range(2) for p in range(2)],
        'mdp_backoff':[m.history_forecast_backoff(w,c,a,p) for w in range(4) for c in range(2) for a in range(2) for p in range(2)],
        'dtr':[m.dtr_transition_forecast(s,a) for s in range(2) for a in range(2)]+
              [m.dtr_terminal_forecast(s,a,t,b) for s in range(2) for a in range(2) for t in range(2) for b in range(2)]}


def retained(before,after):
    for k in ('properties_ascii','quarantined'):
        need(before[k]==after[k],'OLD_'+k)
    need(after['events'][:len(before['events'])]==before['events'],'NEGATIVE_EVENT_ERASURE')
    need(after['repairs'][:len(before['repairs'])]==before['repairs'],'OLD_REPAIR_ERASURE')
    for k in ('history_ascii','dtr_ascii'):
        if k in before:need(before[k]==after[k],'OLD_'+k)
    sa=json.loads(before['source_ascii']);sb=json.loads(after['source_ascii'])
    ba=json.loads(sa['native_basis_ascii']);bb=json.loads(sb['native_basis_ascii'])
    for slot in OLD:
        need(before['hypotheses_ascii'][slot]==after['hypotheses_ascii'][slot]
            and ba['profiles'][slot]==bb['profiles'][slot]
            and sa['observed_input_masks'][slot]==sb['observed_input_masks'][slot]
            and sa['batch_ledgers'][slot]==sb['batch_ledgers'][slot],'OLD_RELATION_MUTATION')
    need(after['quarantined']==[s==5 for s in range(16)],'QUARANTINE_CHANGED')


def train(seed,out):
    start=time.monotonic();cpu=time.process_time();p,pin=parent(seed);raw=p.read_bytes()
    need(digest(raw)==pin,'TRAINED_PARENT_PIN')
    m=NativeCumulativeLearner.restore(raw,pin);before=json.loads(raw)
    source,w=witness(seed);cases=[];attempts=0
    for slot in NEW:
        need(m._hypotheses[slot] is None and m._source._seen[slot]==0,'EMPTY_SCOPE')
        rows=rows_for(w,slot);packet=digest(canonical(rows));frozen=m.checkpoint()
        try:m.observe(slot,rows,'0'*64,source_ref=digest(source))
        except ValueError:pass
        else:raise RuntimeError('CKAD18_TAMPER_ADMITTED')
        need(m.checkpoint()==frozen,'TAMPER_MUTATION')
        m=m.observe(slot,rows,packet,source_ref=digest(source));initial=m._hypotheses[slot].info()
        repair=None
        if not m._hypotheses[slot].eligible and attempts<2:
            attempts+=1
            m,h,cost=m.repair_sparse(slot);repair={'hypothesis':h.info(),'solver_cost':cost,'adopted':h.eligible}
        need(m.observe(slot,rows,packet,source_ref=digest(source)) is m,'REPLAY_MUTATION')
        cases.append({'slot':slot,'packet_sha256':packet,'source_ref':digest(source),
            'witnesses':len(rows),'initial':initial,'repair':repair,'final':m._hypotheses[slot].info()})
    frozen=m.checkpoint();row=rows_for(w,5)[:1]
    try:m.observe(5,row,digest(canonical(row)),source_ref=digest(source))
    except ValueError as e:need(str(e)=='CKAD_NATIVE_INTEGRATED_QUARANTINED','WRONG_QUARANTINE_REJECTION')
    else:raise RuntimeError('CKAD18_QUARANTINED_UPDATE_ADMITTED')
    need(m.checkpoint()==frozen,'QUARANTINE_MUTATION')
    repeated=0
    if m._history is None:
        cache=(HERE.parent/'NKR-20/source_fixture.json').read_bytes()
        for n in (8,16,23):m=m.observe_cached_history(cache,MDP_PIN,n)
        repeated+=92
    if m._dtr is None:
        cache=(HERE.parent/'CKAD-16/source_public_fit.json').read_bytes()
        for n in (64,128,192):m=m.observe_cached_dtr(cache,DTR_PIN,n)
        repeated+=576
    final=m.checkpoint();retained(before,json.loads(final))
    path=out/f'seed-{seed}-full-scope-native.json';path.write_bytes(final)
    return {'seed':seed,'parent_name':p.name,'parent_sha256':pin,'checkpoint_name':path.name,
        'checkpoint_sha256':digest(final),'checkpoint_bytes':len(final),'source_sha256':digest(source),
        'fresh_process_training':True,'new_slots':cases,'repeated_historical_events':repeated,
        'tamper_denied':True,'quarantine_update_denied':True,'replay_idempotent':True,
        'wall_seconds':time.monotonic()-start,'cpu_seconds':time.process_time()-cpu}


def cold(path,pin):
    script='''import sys,json,time
from pathlib import Path
sys.modules['scipy']=None
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
start=time.process_time();p=json.load(sys.stdin);raw=Path(p['path']).read_bytes();m=NativeCumulativeLearner.restore(raw,p['sha'])
a=[[m.predict(s,x&1023,x>>10) for x in range(2048)] for s in range(16)]
h=[m.history_forecast(w,c,a,r) for w in range(4) for c in range(2) for a in range(2) for r in range(2)]
b=[m.history_forecast_backoff(w,c,a,r) for w in range(4) for c in range(2) for a in range(2) for r in range(2)]
d=[m.dtr_transition_forecast(s,a) for s in range(2) for a in range(2)]+[m.dtr_terminal_forecast(s,a,t,z) for s in range(2) for a in range(2) for t in range(2) for z in range(2)]
print(json.dumps({'checkpoint_sha256':digest(m.checkpoint()),'core_sha256':digest(canonical(a)),
 'probabilities_sha256':digest(canonical({'mdp':h,'mdp_backoff':b,'dtr':d})),'solver_imported':False,'cpu_seconds':time.process_time()-start}))
'''
    p=subprocess.run([sys.executable,'-B','-c',script],input=canonical({'path':str(path),'sha':pin}),capture_output=True,
        check=True,timeout=90,env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
    return json.loads(p.stdout)


def score(pred,truth):
    return {'correct':sum(p==y for p,y in zip(pred,truth)),'incorrect':sum(p is not None and p!=y for p,y in zip(pred,truth)),
        'abstained':sum(p is None for p in pred),'questions':len(truth),'prediction_sha256':digest(canonical(pred))}


def totals(rows,key,eligible):
    use=[c for c in rows if not eligible or c['slot']!=5]
    return {k:sum(c[key][k] for c in use) for k in ('correct','incorrect','abstained','questions')}


def run(out):
    start=time.monotonic();cpu=time.process_time();training=[];cases=[];parents=[]
    cb=(HERE.parent/'CKAD-06/result.json').read_bytes()
    import hashlib
    need(hashlib.sha1(b'blob '+str(len(cb)).encode()+b'\0'+cb).hexdigest()==CONTROL_BLOB,'CONTROL_CUSTODY')
    controls={(c['seed'],c['slot']):c for c in json.loads(cb)['cases'] if c['degree']==11}
    for seed in SEEDS:
        need(time.monotonic()-start<600,'WALL_BUDGET')
        p=subprocess.run([sys.executable,'-B',str(HERE/'campaign.py'),'--train-seed',str(seed),'--output-directory',str(out)],
            capture_output=True,check=True,timeout=210,env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
        training.append(json.loads(p.stdout))
    # Evaluation code/labels become visible only after all training finishes.
    ev=module('ckad18_consumed_evaluator',HERE.parent/'CKAD-02/campaign.py')
    rd14=module('ckad18_raw14',HERE.parent/'CKAD-14/independent_audit.py')
    rd13=module('ckad18_raw13',HERE.parent/'CKAD-13/independent_audit.py')
    reference_probabilities=None
    for t in training:
        seed=t['seed'];p,pin=parent(seed);old=p.read_bytes();raw=(out/t['checkpoint_name']).read_bytes()
        need(digest(old)==pin and digest(raw)==t['checkpoint_sha256'],'PROCESS_LINEAGE')
        a=NativeCumulativeLearner.restore(old,pin);b=NativeCumulativeLearner.restore(raw,digest(raw))
        before=core(a);after=core(b);retained(json.loads(old),json.loads(raw))
        changed=sum(x is not None and x!=y for aa,bb in zip(before,after) for x,y in zip(aa,bb))
        need(changed==0,'CATASTROPHIC_FORGETTING')
        reader=rd14.state_readers(json.loads(raw),rd13)
        need(all(reader(s,x)==after[s][x] for s in range(16) for x in range(2048)),'RAW_NATIVE_DISAGREEMENT')
        pr=probabilities(b);psha=digest(canonical(pr))
        if seed==101:
            need(pr==probabilities(a),'PREVIOUS_PROBABILITY_CHANGED');reference_probabilities=psha
        need(psha==reference_probabilities,'REPEATED_CACHE_REPLICA_DRIFT')
        source,w=witness(seed)
        for slot in range(16):
            rows,held,truth,degree=ev.dataset(seed,slot);wrows=rows_for(w,slot)
            need(sorted(rows)==sorted(wrows),'WITNESS_IDENTITY')
            ctrl=controls[seed,slot];need(ctrl['source_sha256']==digest(canonical(rows))
                and ctrl['steps'][-1]['exposures']==512,'MATCHED_CONTROL_INFORMATION')
            if slot!=5:need(sorted(b._rows(slot))==sorted(rows),'TRAINING_SCOPE')
            cached=ctrl['steps'][-1]['fully_trained_cart']
            cases.append({'seed':seed,'slot':slot,'newly_acquired':slot in NEW,'source_sha256':digest(canonical(rows)),
                'native':score([after[slot][x] for x in held],truth),
                'parent_native':score([before[slot][x] for x in held],truth),
                'fully_trained_cart':cached['score'],'cart_historical_training_seconds':cached['training_seconds'],
                'cart_information_matched':slot!=5,'quarantined':slot==5})
        fresh=cold(out/t['checkpoint_name'],digest(raw))
        need(fresh['checkpoint_sha256']==digest(raw) and fresh['core_sha256']==digest(canonical(after))
            and fresh['probabilities_sha256']==psha,'COLD_READOUT_DRIFT')
        parents.append(dict(t,prior_answered=sum(x is not None for aa in before for x in aa),
            prior_answer_changes=changed,property_bytes_unchanged=True,old_relation_bytes_unchanged=True,cold=fresh,
            properties=b.info()['stored_properties'],observed_inputs=b.info()['observed_inputs']))
    eligible=totals(cases,'native',True);full=totals(cases,'native',False)
    admitted=sum(c['final']['eligible'] for t in training for c in t['new_slots'])
    attempts=sum(c['repair'] is not None for t in training for c in t['new_slots'])
    need(attempts<=6,'SPARSE_BUDGET')
    gates={'all_new_slots_admitted':admitted==24,'coverage':eligible['correct']>=.95*eligible['questions'],
        'confident_errors':full['incorrect']==0,'quarantine_preserved':full['abstained']==eligible['abstained']+4608,
        'retention':all(p['prior_answer_changes']==0 for p in parents),'properties':all(p['properties']==100000 for p in parents),
        'cold':True,'negative_source_controls':all(t['tamper_denied'] and t['quarantine_update_denied'] and t['replay_idempotent'] for t in training)}
    need(time.monotonic()-start<600,'WALL_BUDGET')
    try:
        import resource
        rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except ImportError:rss=None
    return {'schema':'yggdrasil.ckad18.result.v1',
        'classification':'COMPLETE_RETAINED_WITNESS_SCOPE_SUPPORTED' if all(gates.values()) else 'COMPLETE_RETAINED_WITNESS_SCOPE_NO_GO',
        'gates':gates,'eligible_totals':eligible,'full_totals':full,'parent_totals':totals(cases,'parent_native',False),
        'cart_eligible_totals':totals(cases,'fully_trained_cart',True),'parents':parents,'cases':cases,
        'new_slot_admissions':admitted,'sparse_attempts':attempts,'reused_witness_acquisitions':12288,
        'repeated_historical_events':sum(t['repeated_historical_events'] for t in training),
        'original_source_actions':0,'held_training_updates':0,'scientific_pass':False,'accepted_native':False,'deployment':'NONE',
        'whole_wall_seconds':time.monotonic()-start,'parent_cpu_seconds':time.process_time()-cpu,
        'child_cpu_seconds':sum(p['cpu_seconds']+p['cold']['cpu_seconds'] for p in parents),
        'peak_parent_rss_platform_units':rss,'control_git_blob':CONTROL_BLOB,'probabilities_sha256':reference_probabilities}


def stable(d):
    if isinstance(d,dict):return {k:stable(v) for k,v in d.items() if not k.endswith('_seconds')
        and k not in ('environment','source_candidate_sha','stable_sha256','peak_parent_rss_platform_units','solver_cost')}
    if isinstance(d,list):return [stable(x) for x in d]
    return d


def receipt(d):return {'classification':d['classification'],'gates':d['gates'],'eligible_totals':d['eligible_totals'],
    'full_totals':d['full_totals'],'stable_sha256':d['stable_sha256']}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-directory',type=Path,required=True)
    p.add_argument('--verify-env',action='store_true');p.add_argument('--train-seed',type=int,choices=SEEDS);args=p.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True);out=args.output_directory.resolve()
    if args.train_seed:
        print(json.dumps(train(args.train_seed,out),sort_keys=True));sys.exit(0)
    d=run(out);d['source_candidate_sha']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    d['environment']={'python':platform.python_version(),'platform':platform.platform()};d['stable_sha256']=digest(canonical(stable(d)))
    (out/'campaign-result.json').write_text(json.dumps(d,sort_keys=True,indent=2)+'\n');line=canonical(receipt(d)).decode('ascii');print(line)
    if args.verify_env:need(receipt(d)==json.loads(os.environ['CKAD18_EXPECTED_RESULT']),'PLATFORM_DRIFT')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('result='+line+'\n')
