"""Single-attempt frozen sparse repair, from the accumulated CKAD13 state."""
import argparse
import hashlib
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
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from yggdrasil.native_sparse_hypothesis import NativeSparseHypothesis
from yggdrasil.native_prior_hypothesis import input_order


def need(ok,why):
    if not ok:raise RuntimeError('CKAD14_'+why)


def readouts(m):return [[m.predict(s,x&1023,x>>10) for x in range(2048)] for s in range(16)]


def cold(path,raw,expected):
    script='''import sys,json,time
from pathlib import Path
sys.modules['scipy']=None
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from yggdrasil.native_context_basis import canonical,digest
start=time.process_time();p=json.load(sys.stdin);raw=Path(p['path']).read_bytes();m=NativeCumulativeLearner.restore(raw,p['sha'])
a=[[m.predict(s,x&1023,x>>10) for x in range(2048)] for s in range(16)]
print(json.dumps({'checkpoint_sha256':digest(m.checkpoint()),'readouts_sha256':digest(canonical(a)),'cpu_seconds':time.process_time()-start}))
'''
    p=subprocess.run([sys.executable,'-B','-c',script],input=canonical({'path':str(path),'sha':digest(raw)}),
        capture_output=True,check=True,timeout=90,env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
    d=json.loads(p.stdout)
    need(d['checkpoint_sha256']==digest(raw) and d['readouts_sha256']==digest(canonical(expected)),'COLD_WITHOUT_SOLVER')
    return d


def score(pred,truth):
    return {'correct':sum(p==y for p,y in zip(pred,truth)),
        'incorrect':sum(p is not None and p!=y for p,y in zip(pred,truth)),
        'abstained':sum(p is None for p in pred),'questions':len(truth),
        'prediction_sha256':digest(canonical(pred))}


def run(out):
    start=time.monotonic();cpu=time.process_time()
    prior=json.loads((HERE.parent/'CKAD-13/result.json').read_text())
    spec=importlib.util.spec_from_file_location('ckad14_consumed_evaluator',HERE.parent/'CKAD-02/campaign.py')
    evaluator=importlib.util.module_from_spec(spec);spec.loader.exec_module(evaluator)
    cases=[];parents=[]
    for seed in (101,202,303):
        pc=next(c for c in prior['cases'] if c['seed']==seed)
        name=pc['final_checkpoint_name'];raw=(HERE.parent/'CKAD-13'/name).read_bytes()
        need(digest(raw)==pc['stages'][-1]['checkpoint_sha256'],'PARENT_PIN')
        m=NativeCumulativeLearner.restore(raw,digest(raw));need(m.checkpoint()==raw,'LEGACY_COLD_BYTES')
        before=readouts(m);parent_source=m._source.checkpoint();parent_facts=m._properties.checkpoint()
        seed_cases=[]
        for slot in (12,13):
            need(not m._quarantined[slot] and not m._hypotheses[slot].eligible,'FROZEN_FAILED_SCOPE')
            view_raw=m._view(slot);rows=m._rows(slot)
            need(len(rows)==512,'NO_ADDITIONAL_OBSERVATIONS')
            for arm in ('REAL','SHUFFLED'):
                need(time.monotonic()-start<600,'WALL_BUDGET')
                t=time.monotonic()
                if arm=='REAL':
                    candidate,hyp,cost=m.repair_sparse(slot)
                    m=candidate
                else:
                    masks=[c|(a<<10) for c,a,y in rows]
                    permutation=sorted(range(len(rows)),key=lambda i:hashlib.sha256(f'ckad14:shuffle:{masks[i]}'.encode()).digest())
                    shuffled=[[c,a,rows[j][2]] for (c,a,y),j in zip(rows,permutation)]
                    view=NativeContextAccumulator().stage_update(0,shuffled,digest(canonical(shuffled)),max_degree=11)
                    sr=view.checkpoint();hyp,cost=NativeSparseHypothesis.fit_checkpoint(sr,digest(sr))
                hraw=hyp.checkpoint();hname=f'hypothesis-{seed}-{slot}-{arm.lower()}.json';(out/hname).write_bytes(hraw)
                # Evaluator is accessed after FIT/calibration; original consumed
                # witnesses must match every decoded parent observation.
                original,held,truth,degree=evaluator.dataset(seed,slot)
                need({c|(a<<10):y for c,a,y in original}=={c|(a<<10):y for c,a,y in rows},'WITNESS_IDENTITY')
                pred=[hyp.predict_provisional(x&1023,x>>10) for x in held]
                old=pc['stages'][-1]['metrics'][str(slot)]
                row={'seed':seed,'slot':slot,'arm':arm,'source_view_sha256':digest(view_raw),
                    'info':hyp.info(),'solver_cost':cost,'native_sparse':score(pred,truth),
                    'legacy_native':old['native'],'fully_trained_cart':old['controls']['cart'],
                    'independent_exact_hierarchy':old['controls']['exact'],
                    'checkpoint_name':hname,'checkpoint_sha256':digest(hraw),'checkpoint_bytes':len(hraw),
                    'case_wall_seconds':time.monotonic()-t,'real_adopted':arm=='REAL' and hyp.eligible}
                cases.append(row);seed_cases.append(row)
        after=readouts(m);prior_lost=sum(a is not None and a!=b for aa,bb in zip(before,after) for a,b in zip(aa,bb))
        need(prior_lost==0 and m._source.checkpoint()==parent_source
            and m._properties.checkpoint()==parent_facts,'REPAIR_CHANGED_RETAINED_STATE')
        final=m.checkpoint();fname=f'seed-{seed}-continued-native.json';path=out/fname;path.write_bytes(final)
        fresh=cold(path,final,after)
        parents.append({'seed':seed,'parent_name':name,'parent_sha256':digest(raw),'checkpoint_name':fname,
            'checkpoint_sha256':digest(final),'checkpoint_bytes':len(final),'prior_answered':sum(x is not None for a in before for x in a),
            'prior_answer_changes':prior_lost,'source_bytes_unchanged':True,'property_bytes_unchanged':True,
            'adopted_repairs':sum(c['real_adopted'] for c in seed_cases),'cold':fresh})
    real=[c for c in cases if c['arm']=='REAL'];neg=[c for c in cases if c['arm']=='SHUFFLED']
    totals={k:sum(c['native_sparse'][k] for c in real) for k in ('correct','incorrect','abstained','questions')}
    gates={'real_admission':sum(c['info']['eligible'] for c in real)>=5,
        'coverage':100*totals['correct']>=95*totals['questions'],'wrong':totals['incorrect']==0,
        'shuffled_denied':all(not c['info']['eligible'] for c in neg),'retention':all(p['prior_answer_changes']==0 for p in parents)}
    try:
        import resource
        rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except ImportError:rss=None
    return {'schema':'yggdrasil.ckad14.result.v1',
        'classification':'SPARSE_NATIVE_REPAIR_DEVELOPMENT_SUPPORTED' if all(gates.values()) else 'SPARSE_NATIVE_REPAIR_DEVELOPMENT_NO_GO',
        'gates':gates,'real_totals':totals,'cases':cases,'parents':parents,
        'scientific_pass':False,'accepted_native':False,'deployment':'NONE','new_original_source_actions':0,
        'solver_attempts':len(cases),'whole_wall_seconds':time.monotonic()-start,'parent_cpu_seconds':time.process_time()-cpu,
        'peak_parent_rss_platform_units':rss}


def stable(d):
    if isinstance(d,dict):return {k:stable(v) for k,v in d.items() if not k.endswith('_seconds')
        and k not in ('environment','source_candidate_sha','stable_sha256','peak_parent_rss_platform_units','solver_cost')}
    if isinstance(d,list):return [stable(x) for x in d]
    return d


def receipt(d):return {'classification':d['classification'],'stable_sha256':d['stable_sha256'],
    'real_totals':d['real_totals'],'gates':d['gates'],'adopted_repairs':sum(p['adopted_repairs'] for p in d['parents'])}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-directory',type=Path,required=True);p.add_argument('--verify-env',action='store_true');args=p.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True);d=run(args.output_directory.resolve())
    d['source_candidate_sha']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    d['environment']={'python':platform.python_version(),'platform':platform.platform()};d['stable_sha256']=digest(canonical(stable(d)))
    (args.output_directory/'campaign-result.json').write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
    line=canonical(receipt(d)).decode('ascii');print(line)
    if args.verify_env:need(receipt(d)==json.loads(os.environ['CKAD14_EXPECTED_RESULT']),'PLATFORM_DRIFT')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('result='+line+'\n')
