"""Frozen witness-only repair; source/control artifacts are reused unchanged."""
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
from yggdrasil.native_context_repair import repair_quarantined_basis


def need(ok,reason):
    if not ok:raise RuntimeError('CKAD08_'+reason)


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def run(source,out):
    started=time.monotonic();old=load('ckad08_source',HERE.parent/'CKAD-02/campaign.py')
    frozen=json.loads((source/'campaign-result.json').read_text())
    need(frozen==json.loads((HERE.parent/'CKAD-06/result.json').read_text()),'CACHED_SOURCE_DRIFT')
    need(frozen['stable_sha256']=='119c4bd5b6e906d26bcc6d97a505de6ce42710f4d37ae119ecc6efb735a78d07','CACHED_SOURCE_PIN')
    controls={(c['seed'],c['slot']):c for c in frozen['cases'] if c['degree']==11}
    prior=json.loads((HERE.parent/'CKAD-07/result.json').read_text());cases=[]
    for case in prior['cases']:
        seed=case['seed'];original_raw=(HERE.parent/'CKAD-07'/case['checkpoint_name']).read_bytes()
        need(digest(original_raw)==case['checkpoint_sha256'],'GUARDED_CHECKPOINT_PIN')
        original=NativeContextQuarantine.restore(original_raw,case['checkpoint_sha256'])
        model=original;repairs=[]
        for slot,failure_pin in enumerate(original._failures):
            if not failure_pin:continue
            rows,held,truth,true_degree=old.dataset(seed,slot)
            control=controls[seed,slot]
            need(digest(canonical(rows))==control['source_sha256'],'QUALIFIED_DATASET_PIN')
            address,retained=old.address(slot)
            # Only the384 newly delivered outcomes cross the repair interface.
            # The first128 source rows are evaluator-only old-witness checks.
            packets=[{'records':rows[128:256],'sha256':digest(canonical(rows[128:256]))},
                     {'records':rows[256:512],'sha256':digest(canonical(rows[256:512]))}]
            need(packets[0]['sha256']==failure_pin,'REJECTED_PACKET_PIN')
            raw=model.checkpoint();t=time.monotonic()
            candidate,lineage=repair_quarantined_basis(raw,digest(raw),address,packets,max_degree=11,retained=retained)
            update_seconds=time.monotonic()-t
            need(model.checkpoint()==raw,'PRIOR_GUARD_MUTATED')
            need(lineage['retained_observed_inputs']==128 and lineage['old_raw_rows_received']==0,'WITNESS_ONLY_INTERFACE')
            model=candidate
            training=[model.predict(address,c,a,retained=retained) for c,a,y in rows]
            need(training==[y for c,a,y in rows],'OBSERVED_KNOWLEDGE_LOSS')
            cached=(source/control['checkpoint_name']).read_bytes()
            need(digest(cached)==control['checkpoint_sha256'],'EXACT_CONTROL_CHECKPOINT_PIN')
            exact=NativeContextAccumulator.restore(cached,control['checkpoint_sha256'])
            all_answers=[model.predict(address,x&1023,x>>10,retained=retained) for x in range(2048)]
            need(all_answers==[exact.predict(address,x&1023,x>>10,retained=retained) for x in range(2048)],'QUALIFIED_CONTROL_DRIFT')
            reset=NativeContextAccumulator()
            for p in packets:
                reset=reset.stage_update(address,p['records'],p['sha256'],max_degree=11,retained=retained)
            reset_old=[reset.predict(address,c,a,retained=retained) for c,a,y in rows[:128]]
            need(all(x is None for x in reset_old),'NO_MEMORY_ABLATION_IDENTIFIED_UNSEEN')
            repairs.append({'slot':slot,'source_sha256':control['source_sha256'],'lineage':lineage,
                'old_observed_correct':sum(training[i]==rows[i][2] for i in range(128)),
                'new_observed_correct':sum(training[i]==rows[i][2] for i in range(128,512)),
                'observed_questions':512,'no_memory_old_abstained':sum(x is None for x in reset_old),
                'held':old.score([all_answers[x] for x in held],truth),
                'all_answers_sha256':digest(canonical(all_answers)),
                'cached_exact_checkpoint_sha256':control['checkpoint_sha256'],'update_seconds':update_seconds})
        need(len(repairs)==4 and not any(model._failures),'QUARANTINE_NOT_REPAIRED')
        held_scores=[];all_answers=[]
        for slot in range(16):
            address,retained=old.address(slot);rows,held,truth,true_degree=old.dataset(seed,slot)
            before=[original.predict(address,x&1023,x>>10,retained=retained) for x in held]
            after=[model.predict(address,x&1023,x>>10,retained=retained) for x in held]
            need(before==after,'UNCHANGED_HELD_EXPECTATION_FAILED')
            if not original._failures[slot]:
                need(model._native._model._profiles[slot]==original._native._model._profiles[slot]
                     and model._native._batches[slot]==original._native._batches[slot]
                     and model._native._seen[slot]==original._native._seen[slot],'UNAFFECTED_STATE_CHANGED')
            held_scores.append(old.score(after,truth))
            all_answers.extend(model.predict(address,x&1023,x>>10,retained=retained) for x in range(2048))
        raw=model.checkpoint();path=out/f'seed-{seed}-witness-repaired-native.json';path.write_bytes(raw)
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
        p=subprocess.run([sys.executable,'-B','-c',script],input=canonical({'path':str(path),'sha':digest(raw)}),capture_output=True,check=True,timeout=90,cwd=out,
            env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
        cold=json.loads(p.stdout)
        need(cold['count']==32768 and cold['answers_sha256']==digest(canonical(all_answers)) and cold['checkpoint_sha256']==digest(raw),'COLD_DRIFT')
        cases.append({'seed':seed,'original_checkpoint_sha256':case['checkpoint_sha256'],'repairs':repairs,
            'unaffected_profiles_unchanged':12,'held_scores':held_scores,'cold':cold,'checkpoint_name':path.name,
            'checkpoint_sha256':digest(raw),'checkpoint_bytes':len(raw)})
    result={'schema':'yggdrasil.ckad08.repair.result.v1','engineering_classification':'WITNESS_PRESERVING_REPRESENTATION_REPAIR_SUPPORTED',
        'scientific_classification':'UNFAMILIAR_FAMILY_RECOVERY_NO_GO','scientific_pass':False,'accepted_native':False,
        'new_original_source_actions':0,'source_grounding':'REUSED_SYNTHETIC_FIXTURES_ONLY','cases':cases,'wall_seconds':time.monotonic()-started}
    need(result['wall_seconds']<300,'FROZEN_WALL_BUDGET')
    return result


def stable(d):
    if isinstance(d,dict):return {k:stable(v) for k,v in d.items() if not k.endswith('_seconds') and k not in ('environment','source_candidate_sha','stable_sha256')}
    if isinstance(d,list):return [stable(v) for v in d]
    return d


def receipt(d):
    repairs=[r for c in d['cases'] for r in c['repairs']];held=[s for c in d['cases'] for s in c['held_scores']]
    return {'engineering':d['engineering_classification'],'science':d['scientific_classification'],'stable_sha256':d['stable_sha256'],
        'old_observed_correct':sum(r['old_observed_correct'] for r in repairs),'new_observed_correct':sum(r['new_observed_correct'] for r in repairs),
        'no_memory_old_abstained':sum(r['no_memory_old_abstained'] for r in repairs),
        'held':{k:sum(s[k] for s in held) for k in ('correct','incorrect','abstained','questions')},
        'repaired_addresses':len(repairs),'cold_queries':sum(c['cold']['count'] for c in d['cases'])}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-directory',type=Path,required=True);p.add_argument('--verify-env',action='store_true');args=p.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True)
    d=run(Path(os.environ['CKAD08_SOURCE_DIRECTORY']),args.output_directory.resolve())
    d['source_candidate_sha']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    d['environment']={'python':platform.python_version(),'platform':platform.platform()}
    d['stable_sha256']=digest(canonical(stable(d)))
    compact=receipt(d)
    need(compact['old_observed_correct']==1536 and compact['new_observed_correct']==4608 and compact['no_memory_old_abstained']==1536
         and compact['held']=={'correct':55296,'incorrect':0,'abstained':18432,'questions':73728},'PRESET_QUALIFICATION_OUTCOME')
    if args.verify_env:need(compact==json.loads(os.environ['CKAD08_EXPECTED_RESULT']),'WINDOWS_DRIFT')
    (args.output_directory/'campaign-result.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    line=canonical(compact).decode('ascii');print(line)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('result='+line+'\n')
