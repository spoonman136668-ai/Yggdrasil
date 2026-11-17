"""Frozen same-address cumulative-constraint audit on reused CKAD02 fixtures."""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import NativeContextBasis, canonical, digest
from yggdrasil.native_context_accumulator import NativeContextAccumulator


def need(value, reason):
    if not value:raise RuntimeError('CKAD06_' + reason)


def old_module():
    spec = importlib.util.spec_from_file_location('ckad06_qualified_controls', HERE.parent/'CKAD-02/campaign.py')
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def predictions(model, slot, masks):
    address, retained = (slot, False) if slot < 7 else (slot - 7, True)
    return [model.predict(address, x & 1023, x >> 10, retained=retained) for x in masks]


def cold(path, slot, expected):
    script = '''import json,sys
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_context_basis import digest,canonical
p=json.load(sys.stdin);raw=open(p['path'],'rb').read()
m=NativeContextAccumulator.restore(raw,p['sha'])
a,r=(p['slot'],False) if p['slot']<7 else (p['slot']-7,True)
answers=[m.predict(a,x&1023,x>>10,retained=r) for x in range(2048)]
print(json.dumps({'count':len(answers),'answers_sha256':digest(canonical(answers)),'checkpoint_sha256':digest(m.checkpoint())}))
'''
    pin = digest(path.read_bytes())
    p = subprocess.run([sys.executable,'-B','-c',script],input=canonical({'path':str(path),'sha':pin,'slot':slot}),
        capture_output=True,check=True,timeout=30,cwd=path.parent,
        env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
    d = json.loads(p.stdout)
    need(d['count']==2048 and d['answers_sha256']==digest(canonical(expected)) and d['checkpoint_sha256']==pin,'COLD_DRIFT')
    return d


def run(out):
    started = time.monotonic();old = old_module()
    previous = json.loads((HERE.parent/'CKAD-02/result.json').read_text())
    pins = {(c['seed'],c['address']):c['source_sha256'] for c in previous['CKAD02_cases']}
    sources = {};cart = {}
    for seed in (101,202,303):
        for slot in range(16):
            rows, held, truth, degree = old.dataset(seed,slot)
            need(digest(canonical(rows))==pins[seed,slot],'QUALIFIED_SOURCE_DRIFT')
            sources[seed,slot] = (rows,held,truth,degree)
            for n in (64,128,256,512):
                answers,cost = old.cart_fit(rows[:n],held,seed)
                cart[seed,slot,n] = dict(cost,score=old.score(answers,truth))
    cases = []
    for degree in (11,3):  # Complete model class before narrower diagnosis.
        for seed in (101,202,303):
            for slot in range(16):
                rows,held,truth,true_degree = sources[seed,slot]
                address,retained = old.address(slot)
                model = NativeContextAccumulator();previous_answers = [None]*2048
                stopped = False;offset = 0;steps = []
                for n in (64,128,256,512):
                    need(time.monotonic()-started<600,'FROZEN_WALL_BUDGET')
                    chunk = rows[offset:n];frozen = model.checkpoint();error = None
                    t = time.monotonic()
                    if not stopped:
                        try:model = model.stage_update(address,chunk,digest(canonical(chunk)),max_degree=degree,retained=retained)
                        except ValueError as exc:
                            need(str(exc) in ('CKAD_NATIVE_MODEL_CLASS_INADEQUATE','CKAD_NATIVE_CUMULATIVE_MODEL_INADEQUATE'), 'UNEXPECTED_UPDATE_FAILURE')
                            error = str(exc);stopped = True
                            need(model.checkpoint()==frozen,'FAILED_STAGE_MUTATED_OLD_STATE')
                    update_seconds = time.monotonic()-t
                    t=time.monotonic()
                    try:batch = old.fit(NativeContextBasis(),slot,rows[:n],degree);batch_valid=True
                    except ValueError as exc:
                        need(str(exc)=='CKAD_NATIVE_MODEL_CLASS_INADEQUATE','BATCH_FAILURE')
                        batch=NativeContextBasis();batch_valid=False
                    batch_seconds=time.monotonic()-t
                    t=time.monotonic();exact=old.ExactSymbolic(rows[:n],degree);symbolic_fit=time.monotonic()-t
                    need(batch_valid==exact.consistent,'SYMBOLIC_CONSISTENCY_DRIFT')
                    t=time.monotonic();answers=predictions(model,slot,range(2048));native_infer=time.monotonic()-t
                    if batch_valid:
                        need(not stopped and answers==predictions(batch,slot,range(2048)),'CUMULATIVE_BATCH_DRIFT')
                        t=time.monotonic();independent=[exact.predict(x) for x in range(2048)];symbolic_infer=time.monotonic()-t
                        need(answers==independent,'INDEPENDENT_CONTROL_DRIFT')
                    else:
                        need(stopped,'INCONSISTENT_PREFIX_ACCEPTED');symbolic_infer=0
                    lost=sum(a is not None and a!=b for a,b in zip(previous_answers,answers))
                    need(lost==0,'PRIOR_IDENTIFIED_ANSWER_LOST')
                    try:replacement=old.fit(NativeContextBasis(),slot,chunk,degree)
                    except ValueError:replacement=NativeContextBasis()
                    replacement_answers=predictions(replacement,slot,range(2048))
                    seen_masks=[c|(a<<10) for c,a,y in rows[:n]]
                    held_answers=[answers[x] for x in held]
                    if degree==11:need(all(x is None for x in held_answers),'COMPLETE_BASIS_EXTRAPOLATED')
                    if degree==3 and true_degree<=3:need(old.score(held_answers,truth)['incorrect']==0,'COMPATIBLE_SOURCE_FALSE_ANSWER')
                    steps.append({'exposures':n,'new_chunk':len(chunk),'accepted_prefix':batch_valid,'first_rejection':error,
                        'rank':model.profile_info(address,retained=retained)['rank'],
                        'accepted_records':model.profile_info(address,retained=retained)['source_records'],
                        'native':old.score(held_answers,truth),
                        'batch_native':old.score(predictions(batch,slot,held),truth),
                        'symbolic':old.score([independent[x] for x in held] if batch_valid else [None]*len(held),truth),
                        'fully_trained_cart':cart[seed,slot,n],
                        'replacement':old.score([replacement_answers[x] for x in held],truth),
                        'retrieval_only':old.score([None]*len(held),truth),
                        'prior_identified':sum(a is not None for a in previous_answers),'prior_lost':lost,
                        'replacement_prior_lost':sum(a is not None and a!=b for a,b in zip(previous_answers,replacement_answers)),
                        'all_seen_inputs_answered':sum(answers[x] is not None for x in seen_masks),
                        'checkpoint_bytes':len(model.checkpoint()),'native_update_seconds':update_seconds,
                        'native_inference_seconds':native_infer,'batch_native_fit_seconds':batch_seconds,
                        'symbolic_fit_seconds':symbolic_fit,'symbolic_inference_seconds':symbolic_infer})
                    previous_answers=answers;offset=n
                if degree==3 and true_degree<=3:need(steps[-1]['rank']==232,'COMPATIBLE_FINAL_RANK')
                raw=model.checkpoint();name=f'seed-{seed}-slot-{slot}-degree-{degree}.json'
                path=out/name;path.write_bytes(raw);fresh=cold(path,slot,previous_answers)
                cases.append({'seed':seed,'slot':slot,'degree':degree,'true_fixture_degree':true_degree,
                    'source_sha256':digest(canonical(rows)),'steps':steps,'final_stopped':stopped,
                    'checkpoint_name':name,'checkpoint_sha256':digest(raw),'cold':fresh})
    compatible=[c for c in cases if c['degree']==3 and c['true_fixture_degree']<=3]
    need(sum(c['steps'][-1]['native']['correct'] for c in compatible)>sum(c['steps'][0]['native']['correct'] for c in compatible),'NO_PRESET_DEVELOPMENT_GAIN')
    return {'schema':'yggdrasil.ckad06.cumulative.result.v1','classification':'NATIVE_CUMULATIVE_SUFFICIENT_STATISTICS_SUPPORTED',
        'scientific_pass':False,'accepted_native':False,'source_grounding':'REUSED_SYNTHETIC_FIXTURES_ONLY',
        'original_source_actions':0,'cases':cases,'wall_seconds':time.monotonic()-started}


def stable(d):
    if isinstance(d,dict):return {k:stable(v) for k,v in d.items() if not k.endswith('_seconds') and k not in ('environment','source_candidate_sha','stable_sha256')}
    if isinstance(d,list):return [stable(v) for v in d]
    return d


def receipt(d):
    rows=[]
    for degree in (11,3):
        for n in (64,128,256,512):
            selected=[c['steps'][i] for c in d['cases'] if c['degree']==degree for i in range(4) if c['steps'][i]['exposures']==n]
            rows.append({'degree':degree,'exposures':n,'native':{key:sum(s['native'][key] for s in selected) for key in ('correct','incorrect','abstained','questions')},
                'cart_correct':sum(s['fully_trained_cart']['score']['correct'] for s in selected),
                'valid_profiles':sum(s['accepted_prefix'] for s in selected),'prior_lost':sum(s['prior_lost'] for s in selected),
                'replacement_prior_lost':sum(s['replacement_prior_lost'] for s in selected)})
    return {'classification':d['classification'],'stable_sha256':d['stable_sha256'],'curve':rows,'cold_queries':sum(c['cold']['count'] for c in d['cases'])}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-directory',type=Path,required=True);p.add_argument('--verify-env',action='store_true');args=p.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True)
    d=run(args.output_directory.resolve())
    d['source_candidate_sha']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    d['environment']={'python':platform.python_version(),'platform':platform.platform()}
    d['stable_sha256']=digest(canonical(stable(d)))
    if args.verify_env:need(receipt(d)==json.loads(os.environ['CKAD06_EXPECTED_RESULT']),'WINDOWS_REPLICATION_DRIFT')
    (args.output_directory/'campaign-result.json').write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
    compact=canonical(receipt(d)).decode('ascii');print(compact)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as stream:stream.write('result='+compact+'\n')
