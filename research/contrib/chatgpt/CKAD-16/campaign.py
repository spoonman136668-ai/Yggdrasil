"""Frozen second-source learning; each update resumes in a fresh process."""
import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from yggdrasil.native_dtr_history import SOURCE_PIN


def need(ok,why):
    if not ok:raise RuntimeError('CKAD16_'+why)


def core(m):return [[m.predict(s,x&1023,x>>10) for x in range(2048)] for s in range(16)]
def mdp(m):return [m.history_forecast(w,c,a,r) for w in range(4) for c in range(2) for a in range(2) for r in range(2)]


def child(script,payload):
    p=subprocess.run([sys.executable,'-B','-c',script],input=canonical(payload),capture_output=True,
        check=True,timeout=90,env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
    return json.loads(p.stdout)


def fresh_train(parent_path,pin,cache,stop,output):
    return child('''import sys,json,time
from pathlib import Path
sys.modules['scipy']=None
from yggdrasil.native_context_basis import digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
p=json.load(sys.stdin);start=time.process_time();raw=Path(p['parent']).read_bytes()
m=NativeCumulativeLearner.restore(raw,p['sha'])
m=m.observe_cached_dtr(Path(p['cache']).read_bytes(),p['source_pin'],p['stop'])
raw=m.checkpoint();Path(p['output']).write_bytes(raw)
print(json.dumps({'input_checkpoint_sha256':p['sha'],'output_checkpoint_sha256':digest(raw),
 'fresh_process_training':True,'solver_imported':False,'cpu_seconds':time.process_time()-start}))
''',{'parent':str(parent_path),'sha':pin,'cache':str(cache),'source_pin':SOURCE_PIN,'stop':stop,'output':str(output)})


def cold(path,raw):
    return child('''import sys,json,time
from pathlib import Path
sys.modules['scipy']=None
start=time.process_time()
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
p=json.load(sys.stdin);raw=Path(p['path']).read_bytes();m=NativeCumulativeLearner.restore(raw,p['sha'])
a=[[m.predict(s,x&1023,x>>10) for x in range(2048)] for s in range(16)]
h=[m.history_forecast(w,c,a,r) for w in range(4) for c in range(2) for a in range(2) for r in range(2)]
d=[m.dtr_transition_forecast(s,a) for s in range(2) for a in range(2)]+[m.dtr_terminal_forecast(s,a,t,b) for s in range(2) for a in range(2) for t in range(2) for b in range(2)]
print(json.dumps({'checkpoint_sha256':digest(m.checkpoint()),'core_sha256':digest(canonical(a)),
 'mdp_sha256':digest(canonical(h)),'dtr_sha256':digest(canonical(d)),'cpu_seconds':time.process_time()-start}))
''',{'path':str(path),'sha':digest(raw)})


def fitted_controls(rows,held):
    import numpy as np
    from sklearn.tree import DecisionTreeClassifier
    answers=[];cost=[]
    for fields,target in ((('s1','x1'),'s2'),(('s1','x1','s2','x2'),'y')):
        x=np.asarray([[r[k] for k in fields] for r in rows]);y=np.asarray([r[target] for r in rows])
        query=np.asarray([[r[k] for k in fields] for r in held]);start=time.monotonic()
        m=DecisionTreeClassifier(random_state=0,max_depth=None,min_samples_leaf=1,ccp_alpha=0.)
        m.fit(x,y);fit_seconds=time.monotonic()-start
        one=list(m.classes_).index(1);pred=m.predict_proba(query)[:,one].tolist()
        table={}
        for r in rows:table.setdefault(tuple(r[k] for k in fields),[]).append(r[target])
        training=m.predict_proba(x)[:,one]
        need(all(abs(float(p)-sum(table[tuple(r[k] for k in fields)])/len(table[tuple(r[k] for k in fields)]))<1e-12
                 for p,r in zip(training,rows)),'CONVENTIONAL_NOT_FULLY_FITTED')
        answers.append(pred);cost.append({'fit_seconds':fit_seconds,'nodes':int(m.tree_.node_count),
            'all_observed_condition_means_fitted':True})
    return list(zip(*answers)),cost


def rational(value):return {'numerator':value.numerator,'denominator':value.denominator,'value':float(value)}


def run(out):
    start=time.monotonic();cpu=time.process_time()
    previous=json.loads((HERE.parent/'CKAD-15/result.json').read_text());old=previous['stages'][-1]
    parent_path=HERE.parent/'CKAD-15'/old['checkpoint_name'];raw=parent_path.read_bytes()
    need(digest(raw)==old['checkpoint_sha256'],'PARENT_PIN')
    m=NativeCumulativeLearner.restore(raw,digest(raw));original_core=digest(canonical(core(m)));original_mdp=digest(canonical(mdp(m)))
    fixed=json.loads(raw);source=HERE/'source_public_fit.json';cache=source.read_bytes();need(digest(cache)==SOURCE_PIN,'SOURCE_CUSTODY')
    replicas=json.loads(cache)['replicas'];held=[r for part in replicas for r in part['fit'][192:]]
    need(len(held)==192,'FROZEN_HELD_COUNT');stages=[];pin=digest(raw)
    for stop in (0,64,128,192):
        stage_start=time.monotonic();name=f'seed-101-dtr-{stop:03}.json';path=out/name;input_pin=pin
        if stop:
            training=fresh_train(parent_path,input_pin,source,stop,path);raw=path.read_bytes()
            need(training['output_checkpoint_sha256']==digest(raw),'TRAIN_CHILD_PIN')
            m=NativeCumulativeLearner.restore(raw,digest(raw))
        else:
            path.write_bytes(raw);training={'fresh_process_training':False,'input_checkpoint_sha256':pin}
        state=json.loads(raw)
        for key in ('properties_ascii','source_ascii','hypotheses_ascii','quarantined','events','repairs','history_ascii'):
            need(state[key]==fixed[key],'RETAINED_COMPONENT_CHANGED')
        need(digest(canonical(core(m)))==original_core and digest(canonical(mdp(m)))==original_mdp,'KNOWLEDGE_FORGETTING')
        rows=[r for p in replicas for r in p['fit'][:stop]];tables=({},{} )
        for r in rows:
            tables[0].setdefault((r['s1'],r['x1']),[]).append(r['s2'])
            tables[1].setdefault((r['s1'],r['x1'],r['s2'],r['x2']),[]).append(r['y'])
        cart,cost=fitted_controls(rows,held) if stop else ([(.5,.5)]*len(held),[])
        losses=[Fraction(0),Fraction(0)];cart_loss=[0.,0.];trace=[];mismatch=0
        for r,cp in zip(held,cart):
            keys=((r['s1'],r['x1']),(r['s1'],r['x1'],r['s2'],r['x2']))
            preds=(m.dtr_transition_forecast(*keys[0]),m.dtr_terminal_forecast(*keys[1]))
            truth=(r['s2'],r['y']);exact=[]
            for target,k in enumerate(keys):
                ys=tables[target].get(k,[]);q=(sum(ys)+1,len(ys)+2);exact.append(q)
                mismatch+=preds[target]!=q
                losses[target]+=(Fraction(*preds[target])-truth[target])**2
                cart_loss[target]+=(cp[target]-truth[target])**2
            trace.append({'seed':r['seed'],'forecasts':preds,'exact_beta':exact,'cart':cp,'truth':truth})
        need(mismatch==0,'INDEPENDENT_BETA_MISMATCH')
        fresh=cold(path,raw);need(fresh['checkpoint_sha256']==digest(raw)
            and fresh['core_sha256']==original_core and fresh['mdp_sha256']==original_mdp,'COLD_STATE')
        if stop:need(m.observe_cached_dtr(cache,SOURCE_PIN,stop) is m,'PREFIX_REPLAY_INCREMENTED')
        stages.append({'prefix_episodes_per_replica':stop,'input_checkpoint_sha256':input_pin,
            'checkpoint_name':name,'checkpoint_sha256':digest(raw),'checkpoint_bytes':len(raw),
            'training':training,'cold':fresh,'training_episodes':3*stop,'held_training_updates':0,
            'dtr_info':None if m._dtr is None else m._dtr.info(),'exact_beta_mismatches':mismatch,
            'brier_transition':rational(losses[0]/192),'brier_terminal':rational(losses[1]/192),
            'brier_pooled':rational(sum(losses)/384),'cart_brier_pooled':sum(cart_loss)/384,
            'cart_cost':cost,'trace':trace,'stage_wall_seconds':time.monotonic()-stage_start})
        pin=digest(raw);parent_path=path
    gain=.25-stages[-1]['brier_pooled']['value']
    gates={'probability_learning':gain>=.025 and stages[-1]['brier_pooled']['value']<=.225,
        'exact_beta':all(s['exact_beta_mismatches']==0 for s in stages),'retention':True,
        'no_held_training':all(s['held_training_updates']==0 for s in stages),
        'fresh_process_continuation':all(s['training']['fresh_process_training'] for s in stages[1:])}
    need(time.monotonic()-start<180,'WALL_BUDGET')
    try:
        import resource
        rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except ImportError:rss=None
    return {'schema':'yggdrasil.ckad16.result.v1',
        'classification':'CUMULATIVE_SECOND_SOURCE_DEVELOPMENT_SUPPORTED' if all(gates.values()) else 'CUMULATIVE_SECOND_SOURCE_DEVELOPMENT_NO_GO',
        'gates':gates,'stages':stages,'parent_checkpoint_name':old['checkpoint_name'],
        'parent_checkpoint_sha256':old['checkpoint_sha256'],'source_canonical_sha256':SOURCE_PIN,
        'original_source_actions':0,'held_training_updates':0,'training_episodes':576,'outcome_updates':1152,
        'scientific_pass':False,'accepted_native':False,'deployment':'NONE',
        'whole_wall_seconds':time.monotonic()-start,'parent_cpu_seconds':time.process_time()-cpu,
        'child_cpu_seconds':sum(s['cold']['cpu_seconds']+s['training'].get('cpu_seconds',0) for s in stages),
        'peak_parent_rss_platform_units':rss}


def stable(d):
    if isinstance(d,dict):return {k:stable(v) for k,v in d.items() if not k.endswith('_seconds')
        and k not in ('environment','source_candidate_sha','stable_sha256','peak_parent_rss_platform_units')}
    if isinstance(d,list):return [stable(x) for x in d]
    return d


def receipt(d):return {'classification':d['classification'],'gates':d['gates'],
    'final_brier':d['stages'][-1]['brier_pooled'],'stable_sha256':d['stable_sha256']}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-directory',type=Path,required=True);p.add_argument('--verify-env',action='store_true');args=p.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True);d=run(args.output_directory.resolve())
    d['source_candidate_sha']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    d['environment']={'python':platform.python_version(),'platform':platform.platform()};d['stable_sha256']=digest(canonical(stable(d)))
    (args.output_directory/'campaign-result.json').write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
    line=canonical(receipt(d)).decode('ascii');print(line)
    if args.verify_env:need(receipt(d)==json.loads(os.environ['CKAD16_EXPECTED_RESULT']),'PLATFORM_DRIFT')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('result='+line+'\n')
