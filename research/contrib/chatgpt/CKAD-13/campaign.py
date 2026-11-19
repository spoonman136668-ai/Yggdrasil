"""Frozen cumulative native A-F development; no original source execution."""
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
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_context_quarantine import NativeContextQuarantine
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner, coordinates
from yggdrasil.native_prior_hypothesis import input_order

SLOTS = (0, 2, 4, 8, 1, 5, 12, 13)
ACTIVE = (0, 2, 4, 8, 1, 12, 13)


def need(value, reason):
    if not value:
        raise RuntimeError('CKAD13_' + reason)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec); spec.loader.exec_module(obj)
    return obj


def answers(m, slot):
    return [m.predict(slot, x & 1023, x >> 10) for x in range(2048)]


def cold(path, raw):
    script = '''import json,sys,time
from pathlib import Path
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
start=time.process_time();p=json.load(sys.stdin);raw=Path(p['path']).read_bytes()
m=NativeCumulativeLearner.restore(raw,p['sha']);a=[[m.predict(s,x&1023,x>>10) for x in range(2048)] for s in p['slots']]
print(json.dumps({'raw':m.checkpoint().decode('ascii'),'answers_sha256':digest(canonical(a)),'cpu_seconds':time.process_time()-start}))
'''
    p = subprocess.run([sys.executable,'-B','-c',script], input=canonical({'path':str(path),'sha':digest(raw),'slots':SLOTS}),
        check=True,capture_output=True,timeout=90,env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
    d=json.loads(p.stdout); restored=d.pop('raw').encode('ascii')
    need(restored==raw,'COLD_BYTES')
    return NativeCumulativeLearner.restore(restored,digest(restored)),d


def exact(old, rows, held):
    ordered=sorted(rows,key=lambda r:input_order(r[0]|(r[1]<<10)))
    fit=ordered[:3*len(ordered)//4]; calibration=ordered[3*len(ordered)//4:]
    chosen=None
    for degree in range(1,12):
        candidate=old.ExactSymbolic(fit,degree)
        if candidate.consistent:
            chosen=candidate;break
    need(chosen is not None,'SYMBOLIC_COMPLETE_CLASS')
    eligible=all(chosen.predict(c|(a<<10))==y for c,a,y in calibration)
    return [chosen.predict(x) if eligible else None for x in held]


def run(out):
    start=time.monotonic();cpu=time.process_time();cold_cpu=0.0
    old=module('ckad13_original_controls',HERE.parent/'CKAD-02/campaign.py')
    result5=json.loads((HERE.parent/'CKAD-05/result.json').read_text())
    result8=json.loads((HERE.parent/'CKAD-08/result.json').read_text())
    cases=[];control_cache={};all_checkpoints=[]
    for seed in (101,202,303):
        p=(HERE.parent/'CKAD-05'/f'seed-{seed}-complete-native-knowledge.json').read_bytes()
        pc=next(c for c in result5['cases'] if c['seed']==seed)
        need(digest(p)==pc['checkpoint_sha256'],'PROPERTY_SOURCE_PIN')
        sc=next(c for c in result8['cases'] if c['seed']==seed)
        source_raw=(HERE.parent/'CKAD-08'/sc['checkpoint_name']).read_bytes()
        need(digest(source_raw)==sc['checkpoint_sha256'],'WITNESS_SOURCE_PIN')
        source=NativeContextQuarantine.restore(source_raw,digest(source_raw))
        # Source lookup contains ONLY previously witnessed inputs/outcomes.
        pool={}
        for slot in SLOTS:
            a,r=coordinates(slot);seen=source._native._seen[slot]
            need(seen.bit_count()==512 and not source._failures[slot],'SOURCE_SCOPE')
            pool[slot]={x:source.predict(a,x&1023,x>>10,retained=r)
                        for x in range(2048) if seen&(1<<x)}
            need(all(type(y) is int for y in pool[slot].values()),'SOURCE_UNIDENTIFIED')
        m=NativeCumulativeLearner(p,digest(p)); acquired={s:[] for s in SLOTS}
        stages=[];previous_pin=None;before_D=None;at128={};evaluator={}
        seed_start=time.monotonic()
        for stage,slots in (('A',()),('B',(0,2)),('C',(4,8)),('D',(1,5)),('E',(12,13)),('F',ACTIVE)):
            need(time.monotonic()-start<600,'WALL_BUDGET')
            stage_start=time.monotonic();input_pin=digest(m.checkpoint());train_start=time.monotonic()
            zero_shot=None;selection=[]
            if stage=='E':
                zero_shot={str(s):answers(m,s) for s in slots}
            for slot in slots:
                if stage=='F':
                    chosen=m.propose(slot,[[x&1023,x>>10] for x in pool[slot]],384)
                    masks=[c|(a<<10) for c,a in chosen]
                    need(len(masks)==384 and len(set(masks))==384,'CONTINUATION_BUDGET')
                else:
                    masks=sorted(pool[slot],key=input_order)[:128]
                rows=[[x&1023,x>>10,pool[slot][x]] for x in masks]
                selection.append({'slot':slot,'selected_inputs_sha256':digest(canonical(masks)),
                                  'revealed_rows_sha256':digest(canonical(rows)),'observations':len(rows)})
                m=m.observe(slot,rows,digest(canonical(rows)),source_ref=digest(source_raw))
                acquired[slot]+=rows
            if stage=='D':
                row=acquired[5][0];bad=[[row[0],row[1],1-row[2]]]
                m=m.observe(5,bad,digest(canonical(bad)),source_ref=digest(source_raw))
                need(m._quarantined[5],'CONTRADICTION_NOT_QUARANTINED')
            training_seconds=time.monotonic()-train_start
            raw=m.checkpoint();name=f'seed-{seed}-stage-{stage}.json';path=out/name;path.write_bytes(raw)
            pre_cold=[answers(m,s) for s in SLOTS];m,fresh=cold(path,raw);cold_cpu+=fresh['cpu_seconds']
            need(fresh['answers_sha256']==digest(canonical(pre_cold)),'COLD_READOUT_DRIFT')
            need(m._properties.checkpoint()==p and m.info()['stored_properties']==100000,'FACT_LOSS')
            need(previous_pin is None or input_pin==previous_pin,'STAGE_NOT_CUMULATIVE')
            current={s:answers(m,s) for s in SLOTS}
            if stage=='C':before_D={s:current[s] for s in (0,2,4,8)}
            retained_D=None
            if stage=='D':
                retained_D=sum(a!=b for s,aa in before_D.items() for a,b in zip(aa,current[s]))
                need(retained_D==0,'UNAFFECTED_INTERFERENCE_LOSS')
            metrics={};control_start=time.monotonic()
            for slot in SLOTS:
                # Evaluator reconstructed ONLY after source acquisition/fitting.
                if slot not in evaluator:
                    original,held,truth,degree=old.dataset(seed,slot)
                    need({c|(a<<10):y for c,a,y in original}==pool[slot],'ORIGINAL_WITNESS_IDENTITY')
                    evaluator[slot]=(held,truth,degree)
                held,truth,degree=evaluator[slot];rows=acquired[slot]
                native=old.score([current[slot][x] for x in held],truth)
                if rows:
                    key=(seed,slot,digest(canonical(rows)))
                    if key not in control_cache:
                        t=time.monotonic();sy=exact(old,rows,held);exact_seconds=time.monotonic()-t
                        ca,cost=old.cart_fit(rows,held,seed)
                        replacement=rows[-384:] if len(rows)==512 else rows
                        ra=exact(old,replacement,held)
                        control_cache[key]={'exact':old.score(sy,truth),'cart':old.score(ca,truth),
                            'replacement':old.score(ra,truth),'cost':cost,'exact_fit_inference_seconds':exact_seconds}
                    controls=control_cache[key]
                else:
                    controls={k:old.score([None]*len(held),truth) for k in ('exact','cart','replacement')}
                metrics[str(slot)]={'observations':len(rows),'native':native,'controls':controls,
                    'witnessed_lookup':old.score([None]*len(held),truth),
                    'quarantined':m._quarantined[slot], 'truth_degree_evaluator_only':degree}
                if len(rows)==128 and not m._quarantined[slot]:at128[slot]=current[slot]
                if zero_shot is not None and slot in slots:
                    metrics[str(slot)]['zero_shot_before_adaptation']=old.score([zero_shot[str(slot)][x] for x in held],truth)
                if stage=='F' and slot in ACTIVE:
                    earlier=at128[slot]
                    metrics[str(slot)]['earlier_answer_changes']=sum(a is not None and a!=b for a,b in zip(earlier,current[slot]))
                    metrics[str(slot)]['retained128']=old.score([earlier[x] for x in held],truth)
            control_seconds=time.monotonic()-control_start
            invalid_rejected=True
            if stage=='B':
                oldraw=m.checkpoint();sample=acquired[0][:4]
                try:m.observe(0,sample,digest(canonical(sample)),source_ref=digest(source_raw),source_kind='correlation_only')
                except ValueError:pass
                else:invalid_rejected=False
                need(invalid_rejected and m.checkpoint()==oldraw,'CORRELATION_ADMISSION')
            receipt={'seed':seed,'stage':stage,'input_checkpoint_sha256':input_pin,
                'previous_stage_checkpoint_sha256':previous_pin,'checkpoint_name':name,'checkpoint_sha256':digest(raw),
                'checkpoint_bytes':len(raw),'info':m.info(),'metrics':metrics,'selection':selection,
                'cold':fresh,'training_seconds':training_seconds,'controls_seconds':control_seconds,
                'whole_stage_seconds':time.monotonic()-stage_start,'unaffected_D_readout_changes':retained_D,
                'correlation_rejected':invalid_rejected}
            stages.append(receipt);all_checkpoints.append({'name':name,'sha256':digest(raw)})
            previous_pin=digest(raw)
        final=stages[-1]['metrics'];correct=sum(final[str(s)]['native']['correct'] for s in ACTIVE)
        earlier=sum(final[str(s)]['retained128']['correct'] for s in ACTIVE)
        wrong=sum(final[str(s)]['native']['incorrect'] for s in ACTIVE if evaluator[s][2]<=3)
        cases.append({'seed':seed,'property_source_sha256':digest(p),'witness_source_sha256':digest(source_raw),
            'stages':stages,'final_checkpoint_name':stages[-1]['checkpoint_name'],'gain_correct':correct-earlier,
            'supported_wrong':wrong,'seed_wall_seconds':time.monotonic()-seed_start})
    need(time.monotonic()-start<600,'WALL_BUDGET')
    try:
        import resource
        rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except ImportError:rss=None
    return {'schema':'yggdrasil.ckad13.result.v1','classification':'CUMULATIVE_NATIVE_ENGINEERING_DEVELOPMENT_COMPLETED',
        'scientific_pass':False,'accepted_native':False,'deployment':'NONE','cases':cases,'checkpoints':all_checkpoints,
        'development_gain_pass':all(c['gain_correct']>0 and c['supported_wrong']==0 for c in cases),
        'new_original_source_actions':0,'data_class':'CONSUMED_SYNTHETIC_WITNESSES_ONLY',
        'control_views_fitted':len(control_cache),'whole_wall_seconds':time.monotonic()-start,
        'parent_cpu_seconds':time.process_time()-cpu,'cold_child_cpu_seconds':cold_cpu,
        'peak_parent_rss_platform_units':rss,'rss_units':'KiB on Linux; not available via resource on Windows'}


def stable(d):
    if isinstance(d,dict):return {k:stable(v) for k,v in d.items() if not k.endswith('_seconds')
        and k not in ('environment','source_candidate_sha','stable_sha256','peak_parent_rss_platform_units','rss_units')}
    if isinstance(d,list):return [stable(x) for x in d]
    return d


def receipt(d):
    return {'stable_sha256':d['stable_sha256'],'classification':d['classification'],
        'development_gain_pass':d['development_gain_pass'],
        'seed_gains':[c['gain_correct'] for c in d['cases']],
        'checkpoints':len(d['checkpoints']),'scientific_pass':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-directory',type=Path,required=True)
    parser.add_argument('--verify-env',action='store_true');args=parser.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True);d=run(args.output_directory.resolve())
    d['source_candidate_sha']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    d['environment']={'python':platform.python_version(),'platform':platform.platform()}
    d['stable_sha256']=digest(canonical(stable(d)))
    if args.verify_env:need(receipt(d)==json.loads(os.environ['CKAD13_EXPECTED_RESULT']),'PLATFORM_DRIFT')
    (args.output_directory/'campaign-result.json').write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
    compact=canonical(receipt(d)).decode('ascii');print(compact)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('result='+compact+'\n')
