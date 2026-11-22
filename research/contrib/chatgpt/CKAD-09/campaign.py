"""Exploratory knowledge-to-provisional-hypothesis test; no new source calls."""
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
from yggdrasil.native_context_quarantine import NativeContextQuarantine
from yggdrasil.native_prior_hypothesis import NativePriorHypothesis


def need(ok,reason):
    if not ok:raise RuntimeError('CKAD09_'+reason)


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def order(mask):return hashlib.sha256(f'ckad09:input-order:{mask}'.encode('ascii')).digest()


def independent(rows):
    """Independent bool-matrix residual optimizer, no native programming code."""
    import numpy as np
    n=len(rows);fit_n=3*n//4;masks=np.arange(2048,dtype=np.uint16)
    xs=np.array([x for x,y in rows],dtype=np.uint16);ys=np.array([y for x,y in rows],dtype=bool)
    design=(xs[:,None]&masks[None,:])==masks[None,:]
    residual=ys[:fit_n].copy();weights=np.zeros(2048,dtype=bool);writes=[]
    for _ in range(16):
        losses=np.count_nonzero(np.logical_xor(design[:fit_n],residual[:,None]),axis=0)
        gains=np.count_nonzero(residual)-losses
        choices=np.flatnonzero(gains>0)
        if not len(choices):break
        best=min((int(x) for x in choices),key=lambda x:(-int(gains[x]),x.bit_count(),x))
        residual=np.logical_xor(residual,design[:fit_n,best]);weights[best]=not weights[best];writes.append(best)
    active=np.flatnonzero(weights)
    calibration=np.count_nonzero((np.count_nonzero(design[fit_n:,active],axis=1)%2).astype(bool)!=ys[fit_n:])
    return {'weights':sum(1<<int(m) for m in active),'writes':writes,'fit_errors':int(np.count_nonzero(residual)),
        'calibration_errors':int(calibration),'eligible':not np.any(residual) and calibration==0}


def control_predictions(control,masks):
    if not control['eligible']:return [None]*len(masks)
    active=[m for m in range(2048) if control['weights']&(1<<m)]
    return [sum((x&m)==m for m in active)&1 for x in masks]


def cold(path,expected):
    script='''import json,sys
from yggdrasil.native_prior_hypothesis import NativePriorHypothesis
from yggdrasil.native_context_basis import canonical,digest
p=json.load(sys.stdin);raw=open(p['path'],'rb').read();m=NativePriorHypothesis.restore(raw,p['sha'])
answers=[m.predict_provisional(x&1023,x>>10) for x in range(2048)]
print(json.dumps({'count':len(answers),'answers_sha256':digest(canonical(answers)),'checkpoint_sha256':digest(m.checkpoint())}))
'''
    raw=path.read_bytes()
    p=subprocess.run([sys.executable,'-B','-c',script],input=canonical({'path':str(path),'sha':digest(raw)}),
        capture_output=True,check=True,timeout=30,cwd=path.parent,
        env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
    d=json.loads(p.stdout)
    need(d['count']==2048 and d['answers_sha256']==digest(canonical(expected)) and d['checkpoint_sha256']==digest(raw),'COLD_DRIFT')
    return d


def aggregate(cases):
    result={}
    for n in (512,128):
        for condition in ('REAL','SHUFFLED'):
            selected=[c for c in cases if c['exposure']==n and c['condition']==condition]
            scores={k:sum(c['native'][k] for c in selected) for k in ('correct','incorrect','abstained','questions')}
            result[f'{condition}_{n}']={'native':scores,'cart':{k:sum(c['fully_trained_cart'][k] for c in selected) for k in scores},
                'admitted':sum(c['fit']['eligible'] for c in selected),'exact_fits':sum(c['fit']['fit_errors']==0 for c in selected)}
    return result


def run(out):
    started=time.monotonic();old=load('ckad09_evaluator',HERE.parent/'CKAD-02/campaign.py')
    parent=json.loads((HERE.parent/'CKAD-08/result.json').read_text())
    old_controls=json.loads((HERE.parent/'CKAD-06/result.json').read_text())
    cart_refs={(c['seed'],c['slot']):c for c in old_controls['cases'] if c['degree']==11}
    sources={};pins={}
    for c in parent['cases']:
        raw=(HERE.parent/'CKAD-08'/c['checkpoint_name']).read_bytes();need(digest(raw)==c['checkpoint_sha256'],'SOURCE_PIN')
        sources[c['seed']]=NativeContextQuarantine.restore(raw,c['checkpoint_sha256']);pins[c['seed']]=raw
    cases=[]
    for n in (512,128):  # Widest retained knowledge first; rule/edit budget fixed.
        for condition in ('REAL','SHUFFLED'):
            for seed in (101,202,303):
                source=sources[seed]
                for slot in (12,13,14,15):
                    need(time.monotonic()-started<900,'FROZEN_BUDGET')
                    address,retained=old.address(slot)
                    profile=source._native._model._profiles[slot]
                    need(profile.degree==11 and profile.unique_inputs==512 and not source._failures[slot],'COMPLETE_REPAIRED_SOURCE')
                    rows,held,truth,source_degree=old.dataset(seed,slot)
                    need(digest(canonical(rows))==cart_refs[seed,slot]['source_sha256'],'QUALIFIED_FIXTURE_PIN')
                    seen=source._native._seen[slot]
                    masks=sorted((x for x in range(2048) if seen&(1<<x)),key=order)[:n]
                    values={x:source.predict(address,x&1023,x>>10,retained=retained) for x in masks}
                    original_by_x={c|(a<<10):y for c,a,y in rows}
                    need(all(values[x]==original_by_x[x] for x in masks),'NATIVE_OBSERVED_KNOWLEDGE_DRIFT')
                    if condition=='SHUFFLED':
                        shuffled=sorted(masks,key=lambda x:hashlib.sha256(f'ckad09:shuffle:{x}'.encode('ascii')).digest())
                        values=dict(zip(masks,[values[x] for x in shuffled]))
                    public_rows=[[x&1023,x>>10,values[x]] for x in masks]
                    t=time.monotonic()
                    view=NativeContextAccumulator().stage_update(0,public_rows,digest(canonical(public_rows)),max_degree=11)
                    view_raw=view.checkpoint();compile_seconds=time.monotonic()-t
                    name=f'{seed}-{slot}-{n}-{condition.lower()}'
                    view_name='view-'+name+'.json';(out/view_name).write_bytes(view_raw)
                    t=time.monotonic();model=NativePriorHypothesis.fit_checkpoint(view_raw,digest(view_raw));native_fit_seconds=time.monotonic()-t
                    ordered=[(x,values[x]) for x in masks]
                    t=time.monotonic();control=independent(ordered);independent_fit_seconds=time.monotonic()-t
                    info=model.info()
                    need(info['writes']==control['writes'] and info['fit_errors']==control['fit_errors']
                         and info['calibration_errors']==control['calibration_errors'] and info['eligible']==bool(control['eligible'])
                         and model._weights==control['weights'],'INDEPENDENT_FIT_DRIFT')
                    t=time.monotonic();answers=[model.predict_provisional(x&1023,x>>10) for x in range(2048)];inference_seconds=time.monotonic()-t
                    independent_answers=control_predictions(control,list(range(2048)))
                    need(answers==independent_answers,'INDEPENDENT_PREDICTION_DRIFT')
                    need(view.checkpoint()==view_raw and sources[seed].checkpoint()==pins[seed],'KNOWLEDGE_MUTATED')
                    identified=[view.predict(0,x&1023,x>>10) for x in held]
                    need(all(a is None for a in identified),'IDENTIFIED_READOUT_CHANGED')
                    if n==512 and condition=='REAL':
                        cart_score=cart_refs[seed,slot]['steps'][-1]['fully_trained_cart']['score']
                        cart_cost={'source':'REUSED_EXACT_QUALIFIED_CKAD06_CART512','training_accuracy':1.0}
                    else:
                        cart_answers,cart_cost=old.cart_fit(public_rows,held,seed);cart_score=old.score(cart_answers,truth)
                        cart_cost['source']='NEW_DATA_VIEW_FULLY_TRAINED_CART'
                    raw=model.checkpoint();checkpoint_name='hypothesis-'+name+'.json';path=out/checkpoint_name;path.write_bytes(raw)
                    fresh=cold(path,answers)
                    cases.append({'seed':seed,'slot':slot,'exposure':n,'condition':condition,
                        'parent_native_checkpoint_sha256':digest(pins[seed]),'public_rows_sha256':digest(canonical(public_rows)),
                        'view_checkpoint_name':view_name,'view_checkpoint_sha256':digest(view_raw),'view_checkpoint_bytes':len(view_raw),
                        'fit':info,'native':old.score([answers[x] for x in held],truth),
                        'same_prior_independent':old.score([independent_answers[x] for x in held],truth),
                        'identified_only':old.score(identified,truth),'memorization':old.score([None]*len(held),truth),
                        'zero_update':old.score([0]*len(held),truth),'fully_trained_cart':cart_score,'cart_cost':cart_cost,
                        'checkpoint_name':checkpoint_name,'checkpoint_sha256':digest(raw),'checkpoint_bytes':len(raw),'cold':fresh,
                        'compile_seconds':compile_seconds,'native_fit_seconds':native_fit_seconds,
                        'independent_fit_seconds':independent_fit_seconds,'native_inference_seconds':inference_seconds})
    summary=aggregate(cases);a=summary['REAL_512']['native'];small=summary['REAL_128']['native'];null=summary['SHUFFLED_512']['native'];q=a['questions']
    gates={'coverage':a['correct']*2>=q,'wrong_answered':a['incorrect']*100<=a['correct']+a['incorrect'],
        'wrong_total':a['incorrect']*100<=q,'knowledge_gain':10*(a['correct']-small['correct'])>=q,
        'conventional_gain':20*(a['correct']-summary['REAL_512']['cart']['correct'])>=q,
        'negative_admission':summary['SHUFFLED_512']['admitted']<=1,'negative_wrong':null['incorrect']*100<=q,
        'negative_gap':4*(a['correct']-null['correct'])>=q}
    return {'schema':'yggdrasil.ckad09.result.v1','classification':'DEVELOPMENT_KNOWLEDGE_TO_HYPOTHESIS_SUPPORTED' if all(gates.values()) else 'DEVELOPMENT_KNOWLEDGE_TO_HYPOTHESIS_NO_GO',
        'scientific_pass':False,'accepted_native':False,'inference_status':'PROVISIONAL_ONLY','gates':gates,'summary':summary,
        'cases':cases,'new_original_source_actions':0,'whole_wall_seconds':time.monotonic()-started}


def stable(d):
    if isinstance(d,dict):return {k:stable(v) for k,v in d.items() if not k.endswith('_seconds') and k not in ('environment','source_candidate_sha','stable_sha256')}
    if isinstance(d,list):return [stable(v) for v in d]
    return d


def receipt(d):
    return {'classification':d['classification'],'stable_sha256':d['stable_sha256'],'summary':d['summary'],'gates':d['gates'],
        'cold_queries':sum(c['cold']['count'] for c in d['cases'])}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-directory',type=Path,required=True);p.add_argument('--verify-env',action='store_true');args=p.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True);d=run(args.output_directory.resolve())
    d['source_candidate_sha']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    d['environment']={'python':platform.python_version(),'platform':platform.platform()};d['stable_sha256']=digest(canonical(stable(d)))
    compact=receipt(d)
    if args.verify_env:need(compact==json.loads(os.environ['CKAD09_EXPECTED_RESULT']),'WINDOWS_DRIFT')
    (args.output_directory/'campaign-result.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    line=canonical(compact).decode('ascii');print(line)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('result='+line+'\n')
