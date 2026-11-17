"""Native representation selection; all scientific claims remain exploratory."""
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
from yggdrasil.native_property_knowledge import NativePropertyKnowledge
from yggdrasil.native_prior_hypothesis import input_order
from yggdrasil.native_degree_hypothesis import NativeDegreeHypothesis


def need(ok,reason):
    if not ok:raise RuntimeError('CKAD12_'+reason)


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def read(stage):return json.loads((HERE.parent/f'CKAD-{stage:02}'/'result.json').read_text())


def independent(old,rows):
    fit=rows[:3*len(rows)//4];cal=rows[3*len(rows)//4:];chosen=None
    for degree in range(1,12):
        candidate=old.ExactSymbolic(fit,degree)
        if candidate.consistent:chosen=candidate;break
    need(chosen is not None,'COMPLETE_INDEPENDENT_CLASS')
    preds=[chosen.predict(c|(a<<10)) for c,a,y in cal]
    wrong=sum(p is not None and p!=r[2] for p,r in zip(preds,cal));unknown=sum(p is None for p in preds)
    eligible=wrong==0 and unknown==0
    return chosen,{'selected_degree':degree,'rejected_fit_degrees':list(range(1,degree)),
        'calibration_wrong':wrong,'calibration_unidentified':unknown,'eligible':eligible}


def cold(path,expected):
    script='''import json,sys
from yggdrasil.native_degree_hypothesis import NativeDegreeHypothesis
from yggdrasil.native_context_basis import canonical,digest
p=json.load(sys.stdin);raw=open(p['path'],'rb').read();m=NativeDegreeHypothesis.restore(raw,p['sha'])
a=[m.predict_provisional(x&1023,x>>10) for x in range(2048)]
print(json.dumps({'count':len(a),'answers_sha256':digest(canonical(a)),'checkpoint_sha256':digest(m.checkpoint())}))
'''
    raw=path.read_bytes();p=subprocess.run([sys.executable,'-B','-c',script],input=canonical({'path':str(path),'sha':digest(raw)}),
        capture_output=True,check=True,timeout=30,cwd=path.parent,env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
    d=json.loads(p.stdout);need(d['count']==2048 and d['answers_sha256']==digest(canonical(expected))
        and d['checkpoint_sha256']==digest(raw),'COLD_DRIFT');return d


def aggregate(cases):
    result={};keys=('correct','incorrect','abstained','questions')
    for recipe,large in (('WIDE',512),('MAJORITY',384)):
        for n in (large,128):
            for condition in ('REAL','SHUFFLED'):
                selected=[c for c in cases if (c['recipe'],c['exposure'],c['condition'])==(recipe,n,condition)]
                result[f'{recipe}_{condition}_{n}']={'admitted':sum(c['fit']['eligible'] for c in selected),
                    'eligible_degree_matches':sum(c['fit']['eligible'] and c['fit']['selected_degree']==c['truth_degree'] for c in selected),
                    'selected_degree_counts':{str(d):sum(c['fit']['selected_degree']==d for c in selected) for d in range(1,12)},
                    'held':{m:{k:sum(c['held'][m][k] for c in selected) for k in keys} for m in ('native','independent','cart','complete_basis','memorization','zero_update')},
                    'strict_novel':{m:{k:sum(c['strict_novel'][m][k] for c in selected) for k in keys} for m in ('native','independent','cart','complete_basis','memorization','zero_update')}}
    return result


def run(out):
    started=time.monotonic();old=load('ckad12_evaluator',HERE.parent/'CKAD-02/campaign.py')
    parents=read(8);prior9={(c['seed'],c['slot'],c['exposure'],c['condition']):c for c in read(9)['cases']}
    prior11={(c['seed'],c['exposure'],c['condition']):c for c in read(11)['cases']}
    cart6={(c['seed'],c['slot']):c for c in read(6)['cases'] if c['degree']==11}
    sources={};pins={};evaluation={};cases=[];cart_reused=0;cart_fitted=0
    for c in parents['cases']:
        raw=(HERE.parent/'CKAD-08'/c['checkpoint_name']).read_bytes();need(digest(raw)==c['checkpoint_sha256'],'PARENT_PIN')
        sources[c['seed']]=NativeContextQuarantine.restore(raw,digest(raw));pins[c['seed']]=raw
    prop={}
    for c in read(5)['cases']:
        raw=(HERE.parent/'CKAD-05'/f"seed-{c['seed']}-complete-native-knowledge.json").read_bytes()
        need(digest(raw)==c['checkpoint_sha256'],'PROPERTY_PIN');prop[c['seed']]=NativePropertyKnowledge.restore(raw,digest(raw))
    # Widest first, no parameter change between recipe, exposure or condition.
    for recipe,scales in (('WIDE',(512,128)),('MAJORITY',(384,128))):
        for n in scales:
            for condition in ('REAL','SHUFFLED'):
                for seed in (101,202,303):
                    for slot in (range(16) if recipe=='WIDE' else (0,)):
                        need(time.monotonic()-started<600,'FROZEN_BUDGET');t=time.monotonic()
                        if recipe=='WIDE':
                            source=sources[seed];address,retained=old.address(slot);seen=source._native._seen[slot]
                            need(seen.bit_count()==512 and not source._failures[slot],'REPAIRED_OBSERVED_SOURCE')
                            masks=sorted((x for x in range(2048) if seen&(1<<x)),key=input_order)[:n]
                            values={x:source.predict(address,x&1023,x>>10,retained=retained) for x in masks}
                            need(all(type(y) is int for y in values.values()),'OBSERVED_SOURCE_OUTCOME')
                            if condition=='SHUFFLED':
                                permutation=sorted(masks,key=lambda x:hashlib.sha256(f'ckad09:shuffle:{x}'.encode('ascii')).digest())
                                values=dict(zip(masks,[values[x] for x in permutation]))
                            rows=[[x&1023,x>>10,values[x]] for x in masks]
                            view=NativeContextAccumulator().stage_update(0,rows,digest(canonical(rows)),max_degree=11);view_raw=view.checkpoint()
                            source_pin=digest(pins[seed]);old_case=prior9.get((seed,slot,n,condition))
                        else:
                            old_case=prior11[seed,n,condition];view_raw=(HERE.parent/'CKAD-11'/old_case['view_checkpoint_name']).read_bytes()
                            need(digest(view_raw)==old_case['view_checkpoint_sha256'],'MAJORITY_VIEW_PIN')
                            view=NativeContextAccumulator.restore(view_raw,digest(view_raw))
                            masks=sorted((x for x in range(2048) if view._seen[0]&(1<<x)),key=input_order)
                            rows=[[x&1023,x>>10,view.predict(0,x&1023,x>>10)] for x in masks]
                            source_pin=old_case['parent_native_checkpoint_sha256']
                        compile_seconds=time.monotonic()-t
                        t=time.monotonic();model=NativeDegreeHypothesis.fit_checkpoint(view_raw,digest(view_raw));native_fit_seconds=time.monotonic()-t
                        t=time.monotonic();symbolic,ind=independent(old,rows);independent_fit_seconds=time.monotonic()-t;info=model.info()
                        need(all(info[k]==v for k,v in ind.items()),'INDEPENDENT_SELECTION_DRIFT')
                        answers=[model.predict_provisional(x&1023,x>>10) for x in range(2048)]
                        independent_answers=[symbolic.predict(x) if ind['eligible'] else None for x in range(2048)]
                        need(answers==independent_answers,'INDEPENDENT_FULL_DOMAIN_DRIFT')
                        if recipe=='WIDE':
                            if (seed,slot) not in evaluation:
                                original_rows,held,truth,degree=old.dataset(seed,slot)  # Evaluator ONLY, after native fit.
                                need(digest(canonical(original_rows))==cart6[seed,slot]['source_sha256'],'QUALIFIED_EVALUATOR_SOURCE_PIN')
                                need({c|(a<<10) for c,a,y in original_rows}=={x for x in range(2048) if seen&(1<<x)},'NATIVE_OBSERVED_SET_DRIFT')
                                need(all(source.predict(address,c,a,retained=retained)==y for c,a,y in original_rows),'NATIVE_SOURCE_LABEL_DRIFT')
                                evaluation[seed,slot]=(original_rows,held,truth,degree)
                            original_rows,held,truth,degree=evaluation[seed,slot];novel=list(range(len(held)))
                        else:
                            p=prop[seed];contexts=[int(p._values[e]) for e in range(6144,8192)]
                            held=[x|1024 for x in contexts];truth=[int(sum((x>>b)&1 for b in (4,5,6))>=2) for x in contexts];degree=2
                            # Strict split hash/count already qualified byCKAD11.
                            trained={int(p._values[e])|1024 for e in sorted(range(4096),key=lambda e:int.from_bytes(hashlib.sha256(f'{seed}:train:{e}'.encode()).digest()[:8],'big'))[:512]}
                            novel=[i for i,x in enumerate(held) if x not in trained]
                            need(digest(canonical([6144+i for i in novel]))==old_case['strict_novel_entity_ids_sha256'],'MAJORITY_NOVEL_SPLIT')
                        if old_case is not None:
                            need(digest(view_raw)==old_case['view_checkpoint_sha256'],'REUSED_CONTROL_VIEW_DRIFT')
                            cart_score=old_case['fully_trained_cart'] if recipe=='WIDE' else old_case['all_held_entities']['fully_trained_cart']
                            cart_novel=cart_score if recipe=='WIDE' else old_case['strict_novel_features']['fully_trained_cart']
                            cart_cost={'source':'REUSED_EXACT_CKAD09_VIEW' if recipe=='WIDE' else 'REUSED_EXACT_CKAD11_VIEW'};cart_reused+=1
                        elif n==512 and condition=='REAL':
                            need(digest(canonical(sorted(rows,key=lambda r:r[0]|(r[1]<<10))))==cart6[seed,slot]['source_sha256'],'REUSED_CART512_SOURCE_SET')
                            cart_score=cart6[seed,slot]['steps'][-1]['fully_trained_cart']['score'];cart_novel=cart_score
                            cart_cost={'source':'REUSED_EXACT_CKAD06_OBSERVATION_SET'};cart_reused+=1
                        else:
                            predictions,cart_cost=old.cart_fit(rows,held,seed);cart_score=old.score(predictions,truth)
                            cart_novel=old.score([predictions[i] for i in novel],[truth[i] for i in novel]);cart_fitted+=1
                            cart_cost['source']='NEW_DISTINCT_VIEW_FULLY_TRAINED_CART'
                        values={c|(a<<10):y for c,a,y in rows}
                        predictions={'native':[answers[x] for x in held],'independent':[independent_answers[x] for x in held],
                            'complete_basis':[view.predict(0,x&1023,x>>10) for x in held],
                            'memorization':[values.get(x) for x in held],'zero_update':[0]*len(held)}
                        groups={}
                        for subset,indices in (('held',list(range(len(held)))),('strict_novel',novel)):
                            groups[subset]={m:old.score([a[i] for i in indices],[truth[i] for i in indices]) for m,a in predictions.items()}
                            groups[subset]['cart']=cart_score if subset=='held' else cart_novel
                        raw=model.checkpoint();name=f'hypothesis-{recipe.lower()}-{seed}-{slot}-{n}-{condition.lower()}.json';path=out/name;path.write_bytes(raw)
                        fresh=cold(path,answers)
                        cases.append({'recipe':recipe,'seed':seed,'slot':slot,'exposure':n,'condition':condition,'truth_degree':degree,
                            'source_checkpoint_sha256':source_pin,'view_checkpoint_sha256':digest(view_raw),'view_rows_sha256':digest(canonical(rows)),
                            'fit':info,**groups,'cart_cost':cart_cost,
                            'stopped_greedy':None if old_case is None else (old_case['native'] if recipe=='WIDE' else old_case['strict_novel_features']['native']),
                            'checkpoint_name':name,'checkpoint_sha256':digest(raw),'checkpoint_bytes':len(raw),'cold':fresh,
                            'compile_seconds':compile_seconds,'native_fit_seconds':native_fit_seconds,'independent_fit_seconds':independent_fit_seconds})
    need(len(cases)==204 and cart_fitted==108 and cart_reused==96,'FROZEN_TRIAL_AND_CONTROL_ACCOUNTING')
    need(all(sources[s].checkpoint()==pins[s] for s in sources),'NATIVE_KNOWLEDGE_MUTATION')
    for s,p in prop.items():need(p.checkpoint()==(HERE.parent/'CKAD-05'/f'seed-{s}-complete-native-knowledge.json').read_bytes(),'PROPERTY_MUTATION')
    summary=aggregate(cases);a=summary['WIDE_REAL_512']['held']['native'];small=summary['WIDE_REAL_128']['held']['native'];q=a['questions']
    maj=summary['MAJORITY_REAL_384']['strict_novel']['native'];cart=summary['WIDE_REAL_512']['held']['cart']
    gates={'wide_coverage':10*a['correct']>=7*q,'wide_wrong_answered':100*a['incorrect']<=a['correct']+a['incorrect'],
        'wide_wrong_total':100*a['incorrect']<=q,'wide_knowledge_gain':10*(a['correct']-small['correct'])>=q,
        'wide_class_matches':summary['WIDE_REAL_512']['admitted']==summary['WIDE_REAL_512']['eligible_degree_matches'],
        'not_worse_than_complete':a['correct']>=summary['WIDE_REAL_512']['held']['complete_basis']['correct'],
        'majority_coverage':20*maj['correct']>=19*maj['questions'],'majority_wrong':maj['incorrect']==0,
        'negative_admission':all(v['admitted']==0 for k,v in summary.items() if 'SHUFFLED' in k),
        'negative_wrong':all(v['held']['native']['incorrect']==0 for k,v in summary.items() if 'SHUFFLED' in k)}
    need(time.monotonic()-started<600,'FROZEN_BUDGET')
    return {'schema':'yggdrasil.ckad12.result.v1','classification':'EVIDENCE_SELECTED_REPRESENTATION_DEVELOPMENT_SUPPORTED' if all(gates.values()) else 'EVIDENCE_SELECTED_REPRESENTATION_DEVELOPMENT_NO_GO',
        'gates':gates,'conventional_superiority':20*(a['correct']-cart['correct'])>=q and a['incorrect']<=cart['incorrect'],
        'symbolic_superiority':False,'scientific_pass':False,'accepted_native':False,'summary':summary,'cases':cases,
        'controls_fitted':cart_fitted,'controls_reused':cart_reused,'parents_byte_exact':True,'properties_retained_per_seed':100000,
        'new_original_source_actions':0,'historical_rescans':0,'new_worlds':0,'whole_wall_seconds':time.monotonic()-started}


def stable(d):
    if isinstance(d,dict):return {k:stable(v) for k,v in d.items() if not k.endswith('_seconds') and k not in ('environment','source_candidate_sha','stable_sha256')}
    if isinstance(d,list):return [stable(v) for v in d]
    return d


def receipt(d):return {'classification':d['classification'],'stable_sha256':d['stable_sha256'],'gates':d['gates'],
    'summary':d['summary'],'cold_queries':sum(c['cold']['count'] for c in d['cases']),
    'conventional_superiority':d['conventional_superiority'],'controls_fitted':d['controls_fitted'],'controls_reused':d['controls_reused']}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-directory',type=Path,required=True);p.add_argument('--verify-env',action='store_true');args=p.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True);d=run(args.output_directory.resolve())
    d['source_candidate_sha']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    d['environment']={'python':platform.python_version(),'platform':platform.platform()};d['stable_sha256']=digest(canonical(stable(d)))
    compact=receipt(d)
    if args.verify_env:need(compact==json.loads(os.environ['CKAD12_EXPECTED_RESULT']),'WINDOWS_DRIFT')
    (args.output_directory/'campaign-result.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    line=canonical(compact).decode('ascii');print(line)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('result='+line+'\n')
