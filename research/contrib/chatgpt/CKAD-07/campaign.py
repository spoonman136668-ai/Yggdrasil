"""Post-result bounded repair audit; frozen CKAD06 controls are reused."""
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
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_context_quarantine import NativeContextQuarantine


def need(ok,reason):
    if not ok:raise RuntimeError('CKAD07_'+reason)


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def run(source,out):
    start=time.monotonic();old=load('ckad07_frozen_source',HERE.parent/'CKAD-02/campaign.py')
    prior=json.loads((source/'campaign-result.json').read_text())
    need(prior['stable_sha256']=='119c4bd5b6e906d26bcc6d97a505de6ce42710f4d37ae119ecc6efb735a78d07','SOURCE_RESULT_PIN')
    need(prior==json.loads((HERE.parent/'CKAD-06/result.json').read_text()),'SOURCE_RESULT_BYTES')
    cases=[]
    for seed in (101,202,303):
        selected=sorted((c for c in prior['cases'] if c['degree']==3 and c['seed']==seed),key=lambda c:c['slot'])
        need([c['slot'] for c in selected]==list(range(16)),'SLOT_SET')
        members=[]
        for c in selected:
            raw=(source/c['checkpoint_name']).read_bytes();need(digest(raw)==c['checkpoint_sha256'],'NATIVE_CHECKPOINT_PIN')
            members.append(NativeContextAccumulator.restore(raw,c['checkpoint_sha256']))
        # Each address is copied byte-for-byte from its frozen independent
        # profile, support, input mask and source ledger. No model is refitted.
        bundle=NativeContextAccumulator()
        bundle._model._profiles=tuple(m._model._profiles[i] for i,m in enumerate(members))
        bundle._seen=tuple(m._seen[i] for i,m in enumerate(members))
        bundle._batches=tuple(m._batches[i] for i,m in enumerate(members))
        before=bundle.checkpoint();guard=NativeContextQuarantine(bundle);contradictions=[]
        for c in selected:
            if not c['final_stopped']:continue
            rows,held,truth,degree=old.dataset(seed,c['slot'])
            need(digest(canonical(rows))==c['source_sha256'],'QUALIFIED_DATASET_PIN')
            failure=next(s for s in c['steps'] if s['first_rejection'])
            n=failure['exposures'];chunk=rows[n-failure['new_chunk']:n]
            address,retained=old.address(c['slot'])
            guard=guard.stage_checked_update(address,chunk,digest(canonical(chunk)),max_degree=3,retained=retained)
            contradictions.append({'slot':c['slot'],'observed_prefix':n,'batch_sha256':digest(canonical(chunk))})
        need(len(contradictions)==4 and sum(bool(s) for s in guard._failures)==4,'ADMISSION_COUNT')
        need(guard._native.checkpoint()==before,'FROZEN_NATIVE_STATE_CHANGED')
        rows_out=[];all_answers=[]
        for c in selected:
            rows,held,truth,degree=old.dataset(seed,c['slot']);address,retained=old.address(c['slot'])
            original=[bundle.predict(address,x&1023,x>>10,retained=retained) for x in held]
            after=[guard.predict(address,x&1023,x>>10,retained=retained) for x in held]
            need(old.score(original,truth)==c['steps'][-1]['native'],'FROZEN_PREDECESSOR_DRIFT')
            need(old.score(after,truth)==c['steps'][-1]['symbolic'],'EXACT_CONTROL_DRIFT')
            if c['final_stopped']:need(all(x is None for x in after),'DISPROVED_READOUT_USED')
            else:need(after==original,'COLLATERAL_LOSS')
            rows_out.append({'slot':c['slot'],'source_sha256':c['source_sha256'],'quarantined':bool(guard._failures[c['slot']]),
                'before':old.score(original,truth),'after':old.score(after,truth),
                'frozen_fully_trained_cart':c['steps'][-1]['fully_trained_cart']['score'],
                'frozen_exact_symbolic':c['steps'][-1]['symbolic']})
            all_answers.extend([guard.predict(address,x&1023,x>>10,retained=retained) for x in range(2048)])
        raw=guard.checkpoint();path=out/f'seed-{seed}-quarantined-native.json';path.write_bytes(raw)
        script='''import json,sys
from yggdrasil.native_context_quarantine import NativeContextQuarantine
from yggdrasil.native_context_basis import canonical,digest
p=json.load(sys.stdin);raw=open(p['path'],'rb').read();m=NativeContextQuarantine.restore(raw,p['sha'])
out=[]
for slot in range(16):
 a,r=(slot,False) if slot<7 else (slot-7,True)
 out.extend(m.predict(a,x&1023,x>>10,retained=r) for x in range(2048))
print(json.dumps({'count':len(out),'answers_sha256':digest(canonical(out)),'checkpoint_sha256':digest(m.checkpoint())}))
'''
        p=subprocess.run([sys.executable,'-B','-c',script],input=canonical({'path':str(path),'sha':digest(raw)}),capture_output=True,check=True,timeout=60,cwd=out,
            env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
        cold=json.loads(p.stdout)
        need(cold['count']==32768 and cold['answers_sha256']==digest(canonical(all_answers)) and cold['checkpoint_sha256']==digest(raw),'COLD_DRIFT')
        cases.append({'seed':seed,'contradictions':contradictions,'native_state_unchanged':True,'rows':rows_out,'cold':cold,
            'checkpoint_name':path.name,'checkpoint_sha256':digest(raw),'checkpoint_bytes':len(raw)})
    need(time.monotonic()-start<180,'FROZEN_BUDGET')
    result={'schema':'yggdrasil.ckad07.repair.result.v1','classification':'BOUNDED_STALE_READOUT_REPAIR_SUPPORTED',
        'scientific_pass':False,'accepted_native':False,'new_original_source_actions':0,'cases':cases,'wall_seconds':time.monotonic()-start}
    rows=[r for c in cases for r in c['rows']]
    need(sum(r['before']['incorrect'] for r in rows)==354 and sum(r['after']['incorrect'] for r in rows)==0
         and sum(r['after']['correct'] for r in rows)==55296 and sum(r['after']['abstained'] for r in rows)==18432,'PRESET_REPAIR_OUTCOME')
    return result


def stable(d):
    if isinstance(d,dict):return {k:stable(v) for k,v in d.items() if not k.endswith('_seconds') and k not in ('environment','source_candidate_sha','stable_sha256')}
    if isinstance(d,list):return [stable(v) for v in d]
    return d


def receipt(d):
    rows=[r for c in d['cases'] for r in c['rows']]
    return {'classification':d['classification'],'stable_sha256':d['stable_sha256'],
        'before':{k:sum(r['before'][k] for r in rows) for k in ('correct','incorrect','abstained','questions')},
        'after':{k:sum(r['after'][k] for r in rows) for k in ('correct','incorrect','abstained','questions')},
        'quarantined':sum(r['quarantined'] for r in rows),'cold_queries':sum(c['cold']['count'] for c in d['cases'])}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-directory',type=Path,required=True);p.add_argument('--verify-env',action='store_true');args=p.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True)
    d=run(Path(os.environ['CKAD07_SOURCE_DIRECTORY']),args.output_directory.resolve())
    d['source_candidate_sha']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    d['environment']={'python':platform.python_version(),'platform':platform.platform()}
    d['stable_sha256']=digest(canonical(stable(d)))
    if args.verify_env:need(receipt(d)==json.loads(os.environ['CKAD07_EXPECTED_RESULT']),'WINDOWS_DRIFT')
    (args.output_directory/'campaign-result.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    compact=canonical(receipt(d)).decode('ascii');print(compact)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('result='+compact+'\n')
