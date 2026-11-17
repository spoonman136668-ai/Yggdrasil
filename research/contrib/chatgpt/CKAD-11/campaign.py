"""Frozen learner falsification on witnessed CKAD01 native property knowledge.

No source generator, new world, hidden outcome or environment action is used.
The majority definition is confined to held evaluator truth, after fitting.
"""
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
from yggdrasil.native_property_knowledge import NativePropertyKnowledge
from yggdrasil.native_property_observations import observed_property_view
from yggdrasil.native_prior_hypothesis import NativePriorHypothesis,input_order


def need(ok,reason):
    if not ok:raise RuntimeError('CKAD11_'+reason)


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def training_keys(seed):
    # Original ordering; only reconstruct recorded identities, not properties.
    ids=sorted(range(4096),key=lambda e:int.from_bytes(hashlib.sha256(f'{seed}:train:{e}'.encode('ascii')).digest()[:8],'big'))[:512]
    return [[e,1] for e in ids]


def cold(path,contexts,expected):
    script='''import json,sys
from yggdrasil.native_prior_hypothesis import NativePriorHypothesis
from yggdrasil.native_context_basis import canonical,digest
p=json.load(sys.stdin);raw=open(p['path'],'rb').read();m=NativePriorHypothesis.restore(raw,p['sha'])
answers=[m.predict_provisional(x,1) for x in p['contexts']]
print(json.dumps({'count':len(answers),'answers_sha256':digest(canonical(answers)),'checkpoint_sha256':digest(m.checkpoint())}))
'''
    raw=path.read_bytes()
    p=subprocess.run([sys.executable,'-B','-c',script],input=canonical({'path':str(path),'sha':digest(raw),'contexts':contexts}),
        capture_output=True,check=True,timeout=30,cwd=path.parent,
        env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
    d=json.loads(p.stdout)
    need(d['count']==len(contexts) and d['answers_sha256']==digest(canonical(expected))
         and d['checkpoint_sha256']==digest(raw),'COLD_DRIFT')
    return d


def aggregate(cases):
    result={};keys=('correct','incorrect','abstained','questions')
    for n in (384,128):
        for condition in ('REAL','SHUFFLED'):
            selected=[c for c in cases if c['exposure']==n and c['condition']==condition]
            groups={}
            for subset in ('all_held_entities','strict_novel_features'):
                groups[subset]={method:{k:sum(c[subset][method][k] for c in selected) for k in keys}
                    for method in ('native','same_prior_independent','fully_trained_cart','context_memorization','zero_update','qualified_native_reference')}
            result[f'{condition}_{n}']={**groups,'admitted':sum(c['fit']['eligible'] for c in selected),
                'exact_fits':sum(c['fit']['fit_errors']==0 for c in selected)}
    return result


def run(out):
    started=time.monotonic();old=load('ckad11_scoring',HERE.parent/'CKAD-02/campaign.py')
    ctrl=load('ckad11_independent',HERE.parent/'CKAD-09/campaign.py')
    prereg=json.loads((HERE/'prereg.json').read_text())
    need(digest((HERE.parent/'CKAD-02/reference-ckad01/CKAD-01-experiment.py').read_bytes())==prereg['inputs']['source_sha256'],'ORIGINAL_RECIPE_PIN')
    parents=json.loads((HERE.parent/'CKAD-05/result.json').read_text());sources={};pins={}
    for c in parents['cases']:
        seed=c['seed'];raw=(HERE.parent/'CKAD-05'/f'seed-{seed}-complete-native-knowledge.json').read_bytes()
        need(digest(raw)==c['checkpoint_sha256'],'NATIVE_PROPERTY_PIN')
        source=NativePropertyKnowledge.restore(raw,c['checkpoint_sha256'])
        need(source.property_count==100000 and source._bits==10,'FULL_KNOWLEDGE')
        need(all(source._known[e]==1023 for e in range(10000)),'PROPERTY_COVERAGE')
        sources[seed]=source;pins[seed]=raw
    need(set(sources)=={101,202,303},'SEEDS')
    cases=[]
    for n in (384,128):
        for condition in ('REAL','SHUFFLED'):
            for seed in (101,202,303):
                need(time.monotonic()-started<600,'FROZEN_BUDGET')
                source=sources[seed];keys=training_keys(seed)
                t=time.monotonic()
                real_raw,witness=observed_property_view(pins[seed],digest(pins[seed]),0,keys,observations=n)
                view=NativeContextAccumulator.restore(real_raw,digest(real_raw))
                masks=sorted((x for x in range(2048) if view._seen[0]&(1<<x)),key=input_order)
                values={x:view.predict(0,x&1023,x>>10) for x in masks}
                need(len(masks)==n and all(type(v) is int for v in values.values()),'WITNESSED_VIEW')
                if condition=='SHUFFLED':
                    shuffled=sorted(masks,key=lambda x:hashlib.sha256(f'ckad09:shuffle:{x}'.encode('ascii')).digest())
                    values=dict(zip(masks,[values[x] for x in shuffled]))
                rows=[[x&1023,x>>10,values[x]] for x in masks]
                view_raw=(real_raw if condition=='REAL' else NativeContextAccumulator().stage_update(
                    0,rows,digest(canonical(rows)),max_degree=11).checkpoint())
                compile_seconds=time.monotonic()-t
                name=f'{seed}-{n}-{condition.lower()}';view_name='view-'+name+'.json';(out/view_name).write_bytes(view_raw)
                t=time.monotonic();model=NativePriorHypothesis.fit_checkpoint(view_raw,digest(view_raw));fit_seconds=time.monotonic()-t
                t=time.monotonic();ind=ctrl.independent([(x,values[x]) for x in masks]);independent_fit_seconds=time.monotonic()-t
                info=model.info()
                need(model._weights==ind['weights'] and info['writes']==ind['writes'] and info['fit_errors']==ind['fit_errors']
                     and info['calibration_errors']==ind['calibration_errors'] and info['eligible']==bool(ind['eligible']),'INDEPENDENT_FIT_DRIFT')
                full_answers=[model.predict_provisional(x&1023,x>>10) for x in range(2048)]
                need(full_answers==ctrl.control_predictions(ind,list(range(2048))),'INDEPENDENT_PARAMETER_PREDICTION_DRIFT')
                # Evaluator only: no truth/relevant-feature information enters fit.
                contexts=[int(source._values[e]) for e in range(6144,8192)]
                held_masks=[x|1024 for x in contexts]
                truth=[int(sum((x>>p)&1 for p in (4,5,6))>=2) for x in contexts]
                reference=[source.predict_entity(0,e,1) for e in range(6144,8192)]
                need(reference==truth,'QUALIFIED_NATIVE_REFERENCE_DRIFT')
                all_witness_masks={int(source._values[e])|1024 for e,a in keys}
                novel=[i for i,x in enumerate(held_masks) if x not in all_witness_masks]
                expected_unique={101:400,202:393,303:397}[seed]
                expected_novel={101:1258,202:1261,303:1235}[seed]
                need(len(all_witness_masks)==expected_unique and len(novel)==expected_novel
                     and witness['unique_witnessed_contexts']==expected_unique,'QUALIFIED_SPLIT_DRIFT')
                answers=[full_answers[x] for x in held_masks]
                t=time.monotonic();cart,cart_cost=old.cart_fit(rows,held_masks,seed);cart_seconds=time.monotonic()-t
                predictions={'native':answers,'same_prior_independent':[ctrl.control_predictions(ind,[x])[0] for x in held_masks],
                    'fully_trained_cart':cart,'context_memorization':[values.get(x) for x in held_masks],
                    'zero_update':[0]*len(truth),'qualified_native_reference':reference}
                groups={}
                for subset,indices in (('all_held_entities',list(range(2048))),('strict_novel_features',novel)):
                    groups[subset]={method:old.score([a[i] for i in indices],[truth[i] for i in indices]) for method,a in predictions.items()}
                raw=model.checkpoint();checkpoint_name='hypothesis-'+name+'.json';path=out/checkpoint_name;path.write_bytes(raw)
                fresh=cold(path,contexts,answers)
                need(source.checkpoint()==pins[seed] and NativeContextAccumulator.restore(view_raw,digest(view_raw)).checkpoint()==view_raw,'PARENT_OR_VIEW_MUTATION')
                cases.append({'seed':seed,'exposure':n,'condition':condition,'witness_export':witness,
                    'parent_native_checkpoint_sha256':digest(pins[seed]),'event_keys_sha256':digest(canonical(keys)),
                    'all_source_context_masks_sha256':digest(canonical(sorted(all_witness_masks))),
                    'held_contexts_sha256':digest(canonical(contexts)),'strict_novel_entity_ids_sha256':digest(canonical([6144+i for i in novel])),
                    'view_checkpoint_name':view_name,'view_checkpoint_sha256':digest(view_raw),'view_checkpoint_bytes':len(view_raw),
                    'view_rows_sha256':digest(canonical(rows)),'fit':info,**groups,'cart_cost':cart_cost,
                    'checkpoint_name':checkpoint_name,'checkpoint_sha256':digest(raw),'checkpoint_bytes':len(raw),'cold':fresh,
                    'compile_seconds':compile_seconds,'native_fit_seconds':fit_seconds,'independent_fit_seconds':independent_fit_seconds,
                    'cart_total_seconds':cart_seconds,'parent_properties_retained':100000})
    summary=aggregate(cases);a=summary['REAL_384']['strict_novel_features']['native'];small=summary['REAL_128']['strict_novel_features']['native']
    conventional=summary['REAL_384']['strict_novel_features']['fully_trained_cart'];q=a['questions']
    gates={'coverage':5*a['correct']>=4*q,'wrong_answered':100*a['incorrect']<=a['correct']+a['incorrect'],
        'wrong_total':100*a['incorrect']<=q,'conventional_deficit':20*(conventional['correct']-a['correct'])<=q,
        'knowledge_gain':10*(a['correct']-small['correct'])>=q,
        'negative_admission':summary['SHUFFLED_384']['admitted']==0,
        'negative_wrong':summary['SHUFFLED_384']['strict_novel_features']['native']['incorrect']==0}
    need(time.monotonic()-started<600,'FROZEN_BUDGET')
    return {'schema':'yggdrasil.ckad11.result.v1','classification':'DISJOINT_KNOWLEDGE_LEARNER_SUPPORTED' if all(gates.values()) else 'DISJOINT_KNOWLEDGE_LEARNER_NO_GO',
        'scientific_pass':False,'accepted_native':False,'inference_status':'PROVISIONAL_ONLY','gates':gates,'summary':summary,'cases':cases,
        'new_original_source_actions':0,'historical_rescans':0,'new_worlds':0,'whole_wall_seconds':time.monotonic()-started}


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
    if args.verify_env:need(compact==json.loads(os.environ['CKAD11_EXPECTED_RESULT']),'WINDOWS_DRIFT')
    (args.output_directory/'campaign-result.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    line=canonical(compact).decode('ascii');print(line)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('result='+line+'\n')
