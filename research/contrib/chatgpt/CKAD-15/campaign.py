"""Frozen probability integration from an accumulated trained native state."""
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
from yggdrasil.native_stochastic_history import SOURCE_PIN


def need(ok,why):
    if not ok:raise RuntimeError('CKAD15_'+why)


def deterministic(m):return [[m.predict(s,x&1023,x>>10) for x in range(2048)] for s in range(16)]


def cold(path,raw,expected):
    script='''import sys,json,time
from pathlib import Path
sys.modules['scipy']=None
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
start=time.process_time();p=json.load(sys.stdin);raw=Path(p['path']).read_bytes();m=NativeCumulativeLearner.restore(raw,p['sha'])
a=[[m.predict(s,x&1023,x>>10) for x in range(2048)] for s in range(16)]
f=[m.history_forecast(w,c,a,r) for w in range(4) for c in range(2) for a in range(2) for r in range(2)]
print(json.dumps({'checkpoint_sha256':digest(m.checkpoint()),'deterministic_sha256':digest(canonical(a)),
 'probability_sha256':digest(canonical(f)),'cpu_seconds':time.process_time()-start}))
'''
    p=subprocess.run([sys.executable,'-B','-c',script],input=canonical({'path':str(path),'sha':digest(raw)}),
        capture_output=True,check=True,timeout=60,env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
    d=json.loads(p.stdout);need(d['checkpoint_sha256']==digest(raw) and d['deterministic_sha256']==expected,'COLD_STATE')
    return d


def exact_table(episodes,stop):
    table={}
    for world,rows in enumerate(episodes):
        for i in range(1,stop+1):
            v=rows[i];key=(world,v>>5,(v>>4)&1,(rows[i-1]>>3)&1)
            for target,y in enumerate(((v>>3)&1,(v>>2)&1)):
                values=table.setdefault((key,target),[]);values.append(y)
    return table


def run(out):
    start=time.monotonic();cpu=time.process_time()
    parent_result=json.loads((HERE.parent/'CKAD-14/result.json').read_text())
    p=next(p for p in parent_result['parents'] if p['seed']==101)
    raw=(HERE.parent/'CKAD-14'/p['checkpoint_name']).read_bytes();need(digest(raw)==p['checkpoint_sha256'],'TRAINED_PARENT_PIN')
    m=NativeCumulativeLearner.restore(raw,digest(raw));source=m._source.checkpoint();facts=m._properties.checkpoint()
    hypotheses=[h.checkpoint() if h is not None else None for h in m._hypotheses]
    original=digest(canonical(deterministic(m)));parent_pin=digest(raw)
    cache=(HERE.parent/'NKR-20/source_fixture.json').read_bytes();need(digest(cache)==SOURCE_PIN,'AUTHENTICATED_CACHE')
    episodes=[bytes.fromhex(e['rows_hex']) for e in json.loads(cache)['episodes']]
    stages=[];previous=parent_pin
    for stop in (0,8,16,23):
        t=time.monotonic();input_pin=digest(m.checkpoint())
        if stop:m=m.observe_cached_history(cache,SOURCE_PIN,stop)
        need(m._source.checkpoint()==source and m._properties.checkpoint()==facts
            and [h.checkpoint() if h is not None else None for h in m._hypotheses]==hypotheses,'CORE_COMPONENT_CHANGED')
        need(input_pin==previous,'NOT_CUMULATIVE')
        native=digest(canonical(deterministic(m)));need(native==original,'DETERMINISTIC_READOUT_LOSS')
        table=exact_table(episodes,stop);trace=[];native_loss=Fraction(0);exact_loss=Fraction(0);mismatches=0
        for world,rows in enumerate(episodes):
            for i in range(24,31):
                v=rows[i];key=(world,v>>5,(v>>4)&1,(rows[i-1]>>3)&1)
                forecasts=m.history_forecast(*key)
                exact=[]
                for target in range(2):
                    values=table.get((key,target),[]);exact.append((sum(values)+1,len(values)+2))
                mismatches+=forecasts!=tuple(exact)
                truth=((v>>3)&1,(v>>2)&1)
                for q,r,y in zip(forecasts,exact,truth):
                    native_loss+=(Fraction(*q)-y)**2;exact_loss+=(Fraction(*r)-y)**2
                trace.append({'world':world,'held_index':i,'forecasts':forecasts,'exact_beta':exact,'truth':truth})
        need(mismatches==0 and native_loss==exact_loss,'EXACT_CONTROL_MISMATCH')
        loss=native_loss/56
        raw=m.checkpoint();name=f'seed-101-history-{stop:02}.json';path=out/name;path.write_bytes(raw)
        fresh=cold(path,raw,original)
        if stop:
            need(m.observe_cached_history(cache,SOURCE_PIN,stop) is m,'REPLAY_INCREMENTED')
        stages.append({'prefix_rows_per_world':stop,'input_checkpoint_sha256':input_pin,
            'previous_checkpoint_sha256':previous,'checkpoint_name':name,'checkpoint_sha256':digest(raw),
            'checkpoint_bytes':len(raw),'deterministic_readout_sha256':native,'cold':fresh,
            'brier':{'numerator':loss.numerator,'denominator':loss.denominator,'value':float(loss)},
            'exact_beta_mismatches':mismatches,'training_events':4*stop,'held_training_updates':0,
            'history':None if m._history is None else m._history.info(),'trace':trace,'stage_wall_seconds':time.monotonic()-t})
        previous=digest(raw)
    need(m._history.info()['native_counter_sha256']=='5f35402435acccc835644d717c0107ede73354f9f2ff6c6bdbf4fe03abd2f4a7',
         'QUALIFIED_NKR20_COUNTER_BYTES')
    gates={'probability_learning':stages[-1]['brier']['value']<=.225
            and stages[0]['brier']['value']-stages[-1]['brier']['value']>=.025,
        'exact_beta':all(s['exact_beta_mismatches']==0 for s in stages),
        'native_retention':all(s['deterministic_readout_sha256']==original for s in stages),
        'legitimate_variation_counted':m._history.info()['counter_keys_with_both_outcomes']>0,
        'no_held_training':all(s['held_training_updates']==0 for s in stages)}
    need(time.monotonic()-start<120,'WALL_BUDGET')
    return {'schema':'yggdrasil.ckad15.result.v1',
        'classification':'CUMULATIVE_STOCHASTIC_INTEGRATION_SUPPORTED' if all(gates.values()) else 'CUMULATIVE_STOCHASTIC_INTEGRATION_NO_GO',
        'gates':gates,'stages':stages,'parent_checkpoint_sha256':parent_pin,
        'parent_checkpoint_name':p['checkpoint_name'],'source_cache_sha256':SOURCE_PIN,
        'source_rows_previously_consumed':124,'training_event_identities':92,'outcome_updates':184,
        'new_original_source_actions':0,'held_training_updates':0,'scientific_pass':False,'accepted_native':False,
        'controls':{'untrained_brier':.25,'qualified_state_beta_brier':.18306255304168106,
            'qualified_hierarchical_backoff_brier':.17735505429327192,'exact_history_beta_brier':stages[-1]['brier']['value']},
        'whole_wall_seconds':time.monotonic()-start,'parent_cpu_seconds':time.process_time()-cpu}


def stable(d):
    if isinstance(d,dict):return {k:stable(v) for k,v in d.items() if not k.endswith('_seconds')
        and k not in ('environment','source_candidate_sha','stable_sha256')}
    if isinstance(d,list):return [stable(x) for x in d]
    return d


def receipt(d):return {'classification':d['classification'],'gates':d['gates'],
    'final_brier':d['stages'][-1]['brier'],'stable_sha256':d['stable_sha256']}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-directory',type=Path,required=True);p.add_argument('--verify-env',action='store_true');args=p.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True);d=run(args.output_directory.resolve())
    d['source_candidate_sha']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    d['environment']={'python':platform.python_version(),'platform':platform.platform()};d['stable_sha256']=digest(canonical(stable(d)))
    (args.output_directory/'campaign-result.json').write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
    line=canonical(receipt(d)).decode('ascii');print(line)
    if args.verify_env:need(receipt(d)==json.loads(os.environ['CKAD15_EXPECTED_RESULT']),'PLATFORM_DRIFT')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('result='+line+'\n')
