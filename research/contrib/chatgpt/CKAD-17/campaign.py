"""Known NKR21 readout integration; zero new observations or learning."""
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


def need(ok,why):
    if not ok:raise RuntimeError('CKAD17_'+why)


def legacy(m):
    c=[[m.predict(s,x&1023,x>>10) for x in range(2048)] for s in range(16)]
    h=[m.history_forecast(w,c,a,p) for w in range(4) for c in range(2) for a in range(2) for p in range(2)]
    d=[m.dtr_transition_forecast(s,a) for s in range(2) for a in range(2)]+[m.dtr_terminal_forecast(s,a,t,b) for s in range(2) for a in range(2) for t in range(2) for b in range(2)]
    return {'core':digest(canonical(c)),'mdp':digest(canonical(h)),'dtr':digest(canonical(d))}


def run(out):
    start=time.monotonic();cpu=time.process_time()
    old=json.loads((HERE.parent/'CKAD-16/result.json').read_text());p=old['stages'][-1]
    raw=(HERE.parent/'CKAD-16'/p['checkpoint_name']).read_bytes()
    need(digest(raw)==p['checkpoint_sha256']=='1705aca1ea9fba2a6ef1ac81e642c6e180649c47b75fad0890416a55f1c0b1e6','TRAINED_PARENT_PIN')
    m=NativeCumulativeLearner.restore(raw,digest(raw));before=legacy(m)
    cache=(HERE.parent/'NKR-20/source_fixture.json').read_bytes()
    need(digest(cache)=='e994f6adb0733c05eeae8dd19b0a4a36bb13946e1090b241023630b468276d1f','SOURCE_CUSTODY')
    episodes=[bytes.fromhex(e['rows_hex']) for e in json.loads(cache)['episodes']]
    tables={}
    for w,rows in enumerate(episodes):
        for i in range(1,24):
            v=rows[i];key=(w,v>>5,(v>>4)&1,(rows[i-1]>>3)&1)
            for t,y in enumerate(((v>>3)&1,(v>>2)&1)):tables.setdefault((key,t),[]).append(y)
    loss=Fraction(0);old_loss=Fraction(0);trace=[];mismatch=0
    for w,rows in enumerate(episodes):
        for i in range(24,31):
            v=rows[i];before_state=v>>5;a=(v>>4)&1;prev=(rows[i-1]>>3)&1;key=(w,before_state,a,prev)
            pred=m.history_forecast_backoff(*key);baseline=m.history_forecast(*key);exact=[]
            for t,y in enumerate(((v>>3)&1,(v>>2)&1)):
                observed=tables.get((key,t),[])
                pooled=tables.get(((w,before_state,a,0),t),[])+tables.get(((w,before_state,a,1),t),[])
                parent=Fraction(sum(pooled)+1,len(pooled)+2)
                q=(sum(observed)+4*parent)/(len(observed)+4)
                exact.append((q.numerator,q.denominator));mismatch+=Fraction(*pred[t])!=q
                loss+=(Fraction(*pred[t])-y)**2;old_loss+=(Fraction(*baseline[t])-y)**2
            trace.append({'world':w,'held_index':i,'new_forecasts':pred,'exact_backoff':exact,
                'legacy_forecasts':baseline,'truth':((v>>3)&1,(v>>2)&1)})
    need(mismatch==0,'EXACT_CONTROL')
    loss/=56;old_loss/=56
    need(loss==Fraction(147509914254743,831720950060000),'EXISTING_QUALIFIED_SCORE_DRIFT')
    need(m.checkpoint()==raw and legacy(m)==before,'LEARNED_OR_LEGACY_STATE_CHANGED')
    path=out/'seed-101-qualified-full-state.json';path.write_bytes(raw)
    script='''import sys,json
from pathlib import Path
sys.modules['scipy']=None
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
p=json.load(sys.stdin);raw=Path(p['path']).read_bytes();m=NativeCumulativeLearner.restore(raw,p['sha'])
a=[m.history_forecast_backoff(w,c,a,r) for w in range(4) for c in range(2) for a in range(2) for r in range(2)]
print(json.dumps({'checkpoint_sha256':digest(m.checkpoint()),'backoff_sha256':digest(canonical(a))}))
'''
    p2=subprocess.run([sys.executable,'-B','-c',script],input=canonical({'path':str(path),'sha':digest(raw)}),
        capture_output=True,check=True,timeout=60,env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
    cold=json.loads(p2.stdout);new=[m.history_forecast_backoff(w,c,a,r) for w in range(4) for c in range(2) for a in range(2) for r in range(2)]
    need(cold['checkpoint_sha256']==digest(raw) and cold['backoff_sha256']==digest(canonical(new)),'COLD_READOUT')
    gates={'known_exact_readout_reproduced':mismatch==0,'legacy_preserved':True,'learned_bytes_unchanged':True,
           'gain_over_legacy':float(old_loss-loss)>=.005}
    need(time.monotonic()-start<120,'WALL_BUDGET')
    return {'schema':'yggdrasil.ckad17.result.v1','classification':'QUALIFIED_BACKOFF_READOUT_INTEGRATION_SUPPORTED' if all(gates.values()) else 'QUALIFIED_BACKOFF_READOUT_INTEGRATION_NO_GO',
        'gates':gates,'brier':{'numerator':loss.numerator,'denominator':loss.denominator,'value':float(loss)},
        'legacy_brier':float(old_loss),'gain':float(old_loss-loss),'trace':trace,'cold':cold,'legacy':before,
        'parent_checkpoint_name':'seed-101-dtr-192.json','checkpoint_name':path.name,
        'checkpoint_sha256':digest(raw),'checkpoint_bytes':len(raw),'training_updates':0,'new_original_source_actions':0,
        'scientific_pass':False,'accepted_native':False,'deployment':'NONE',
        'whole_wall_seconds':time.monotonic()-start,'parent_cpu_seconds':time.process_time()-cpu}


def stable(d):
    if isinstance(d,dict):return {k:stable(v) for k,v in d.items() if not k.endswith('_seconds')
        and k not in ('environment','source_candidate_sha','stable_sha256')}
    if isinstance(d,list):return [stable(x) for x in d]
    return d


def receipt(d):return {'classification':d['classification'],'gates':d['gates'],'brier':d['brier'],'stable_sha256':d['stable_sha256']}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-directory',type=Path,required=True);p.add_argument('--verify-env',action='store_true');args=p.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True);d=run(args.output_directory.resolve())
    d['source_candidate_sha']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    d['environment']={'python':platform.python_version(),'platform':platform.platform()};d['stable_sha256']=digest(canonical(stable(d)))
    (args.output_directory/'campaign-result.json').write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
    line=canonical(receipt(d)).decode('ascii');print(line)
    if args.verify_env:need(receipt(d)==json.loads(os.environ['CKAD17_EXPECTED_RESULT']),'PLATFORM_DRIFT')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('result='+line+'\n')
