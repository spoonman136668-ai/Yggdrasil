"""Frozen whole-state application audit; no hypothesis training/source action."""
import argparse
from functools import lru_cache
import importlib.util
import itertools
import json
import os
from pathlib import Path
import platform
import struct
import subprocess
import sys
import time
from unittest.mock import patch

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_context_quarantine import NativeContextQuarantine
from yggdrasil.native_knowledge_readout import NativeKnowledgeReadout,IDENTIFIED,PROVISIONAL,UNKNOWN


def need(ok,reason):
    if not ok:raise RuntimeError('CKAD10_'+reason)


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


@lru_cache(maxsize=4096)
def independent_row(x,degree):
    active=[i for i in range(11) if x&(1<<i)]
    return sum(1<<sum(1<<i for i in group) for size in range(min(degree,len(active))+1)
               for group in itertools.combinations(active,size))


def decode_base(raw):
    g=json.loads(raw);a=json.loads(g['native_accumulator_ascii']);d=json.loads(a['native_basis_ascii']);out=[]
    for p in d['profiles']:
        terms=[m for m in range(2048) if m.bit_count()<=p['degree']]
        weights=struct.unpack('<'+'f'*len(terms),bytes.fromhex(p['weights_float32_le']))
        out.append((p['degree'],sum(int(w)<<m for m,w in zip(terms,weights)),
            {int(s,16).bit_length()-1:int(s,16) for s in p['support_rows']}))
    return g,out


def independent_answers(base,slot,prior):
    g,profiles=base;degree,weights,space=profiles[slot];p=None
    if prior is not None:
        d=json.loads(prior);vs=struct.unpack('<'+'f'*2048,bytes.fromhex(d['weights_float32_le']))
        p=(d['fit_errors']==0 and d['calibration_errors']==0,sum(int(v)<<i for i,v in enumerate(vs)))
    values=[];statuses=[]
    for x in range(2048):
        row=independent_row(x,degree);remaining=row
        while remaining:
            v=space.get(remaining.bit_length()-1)
            if v is None:break
            remaining^=v
        if remaining==0 and not g['contradiction_batch_sha256'][slot]:
            values.append((weights&row).bit_count()&1);statuses.append(IDENTIFIED)
        elif p is not None and p[0]:
            values.append((p[1]&independent_row(x,11)).bit_count()&1);statuses.append(PROVISIONAL)
        else:values.append(None);statuses.append(UNKNOWN)
    return values,statuses


def fit_cart(rows,seed):
    import numpy as np
    from sklearn.tree import DecisionTreeClassifier
    xs=np.array([[((c|(a<<10))>>i)&1 for i in range(11)] for c,a,y in rows],dtype=np.uint8)
    ys=np.array([y for c,a,y in rows],dtype=np.uint8)
    query=np.array([[(x>>i)&1 for i in range(11)] for x in range(2048)],dtype=np.uint8)
    model=DecisionTreeClassifier(criterion='gini',max_depth=None,min_samples_split=2,min_samples_leaf=1,ccp_alpha=0.,random_state=seed)
    t=time.monotonic();model.fit(xs,ys);seconds=time.monotonic()-t
    need((model.predict(xs)==ys).all(),'CART_NOT_FULLY_FITTED')
    answers=model.predict(query).astype(int).tolist();tree=model.tree_
    snapshot={'schema':'ckad10.frozen-cart-tree.v1','classes':model.classes_.astype(int).tolist(),
        'children_left':tree.children_left.astype(int).tolist(),'children_right':tree.children_right.astype(int).tolist(),
        'feature':tree.feature.astype(int).tolist(),'threshold':tree.threshold.tolist(),
        'labels':[int(model.classes_[int(np.argmax(tree.value[i][0]))]) for i in range(tree.node_count)],
        'training_accuracy':1.,'seed':seed,'source_rows_sha256':digest(canonical(rows)),
        'predictions':answers,'predictions_sha256':digest(canonical(answers))}
    traversed=[]
    for x in range(2048):
        node=0
        while snapshot['feature'][node]>=0:
            feature=snapshot['feature'][node];value=(x>>feature)&1
            node=snapshot['children_left'][node] if value<=snapshot['threshold'][node] else snapshot['children_right'][node]
        traversed.append(snapshot['labels'][node])
    need(traversed==answers,'INDEPENDENT_CART_TRAVERSAL_DRIFT')
    return answers,snapshot,seconds


def decision_scores(predictions,truth,seen,*,unfamiliar_only=False):
    result={k:0 for k in ('contexts','true_sensitive','recommendations','correct_preference','wrong_preference',
        'unnecessary_recommendations','missed_sensitive','unknown_forecasts','tied_forecasts','policy_reward','best_reward','regret')}
    for c in range(1024):
        if unfamiliar_only and ((seen&(1<<c)) or (seen&(1<<(c|1024)))):continue
        p0,p1=predictions[c],predictions[c|1024];y0,y1=truth[c],truth[c|1024]
        sensitive=y0!=y1;recommend=None
        result['contexts']+=1;result['true_sensitive']+=sensitive
        if p0 is None or p1 is None:result['unknown_forecasts']+=1
        elif p0==p1:result['tied_forecasts']+=1
        else:
            recommend=int(p1>p0);result['recommendations']+=1
            if sensitive:
                result['correct_preference']+=recommend==int(y1>y0)
                result['wrong_preference']+=recommend!=int(y1>y0)
            else:result['unnecessary_recommendations']+=1
        if recommend is None and sensitive:result['missed_sensitive']+=1
        action=0 if recommend is None else recommend
        reward=y1 if action else y0;best=max(y0,y1)
        result['policy_reward']+=reward;result['best_reward']+=best;result['regret']+=best-reward
    return result


def cold(path,expected):
    script='''import json,sys
from unittest.mock import patch
from yggdrasil.native_knowledge_readout import NativeKnowledgeReadout
from yggdrasil.native_context_basis import canonical,digest
p=json.load(sys.stdin);raw=open(p['path'],'rb').read()
with patch('yggdrasil.native_prior_hypothesis.program_weights',side_effect=RuntimeError('HYPOTHESIS_RETRAIN_FORBIDDEN')):
 m=NativeKnowledgeReadout.restore(raw,p['sha']);out=[]
 for slot in range(16):
  a,r=(slot,False) if slot<7 else (slot-7,True)
  out.extend(m.readout(a,x&1023,x>>10,retained=r) for x in range(2048))
 print(json.dumps({'count':len(out),'readouts_sha256':digest(canonical(out)),'checkpoint_sha256':digest(m.checkpoint())}))
'''
    raw=path.read_bytes();p=subprocess.run([sys.executable,'-B','-c',script],input=canonical({'path':str(path),'sha':digest(raw)}),
        capture_output=True,check=True,timeout=90,cwd=path.parent,env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
    d=json.loads(p.stdout)
    need(d['count']==32768 and d['readouts_sha256']==digest(canonical(expected)) and d['checkpoint_sha256']==digest(raw),'COLD_DRIFT')
    return d


def aggregate(cases):
    result={}
    for method in ('base','combined','cart','fixed0'):
        for subset in ('all','unfamiliar'):
            rows=[s['decisions'][method][subset] for c in cases for s in c['relations']]
            result[f'{method}_{subset}']={k:sum(r[k] for r in rows) for k in rows[0]}
    held={}
    for method in ('base','combined','cart'):
        rows=[s['held'][method] for c in cases for s in c['relations']]
        held[method]={k:sum(r[k] for r in rows) for k in ('correct','incorrect','abstained','questions')}
    return {'decisions':result,'held':held,'identified_preserved':sum(c['identified_preserved'] for c in cases),
        'statuses':{k:sum(c['statuses'][k] for c in cases) for k in (IDENTIFIED,PROVISIONAL,UNKNOWN)}}


def audit(out):
    start=time.monotonic();old=load('ckad10_evaluator',HERE.parent/'CKAD-02/campaign.py')
    bases=json.loads((HERE.parent/'CKAD-08/result.json').read_text())
    priors=json.loads((HERE.parent/'CKAD-09/result.json').read_text())
    selected={(c['seed'],c['slot']):c for c in priors['cases'] if c['condition']=='REAL' and c['exposure']==512}
    need(len(selected)==12,'FROZEN_PRIOR_COHORT')
    control=json.loads((HERE.parent/'CKAD-06/result.json').read_text())
    refs={(c['seed'],c['slot']):c for c in control['cases'] if c['degree']==11}
    cases=[]
    for c in bases['cases']:
        seed=c['seed'];raw=(HERE.parent/'CKAD-08'/c['checkpoint_name']).read_bytes();need(digest(raw)==c['checkpoint_sha256'],'BASE_PIN')
        base=NativeContextQuarantine.restore(raw,c['checkpoint_sha256']);bundle=NativeKnowledgeReadout(base)
        original=base.checkpoint();prior_raws={}
        for slot in range(16):
            case=selected.get((seed,slot))
            if case is None:continue
            p=(HERE.parent/'CKAD-09'/case['checkpoint_name']).read_bytes();need(digest(p)==case['checkpoint_sha256'],'PRIOR_PIN')
            a,r=old.address(slot);bundle=bundle.with_prior(a,p,case['checkpoint_sha256'],retained=r);prior_raws[slot]=p
        need(base.checkpoint()==original and bundle._base.checkpoint()==original,'BASE_MUTATED')
        independent_base=decode_base(raw);relations=[];all_readouts=[];preserved=0;statuses={k:0 for k in (IDENTIFIED,PROVISIONAL,UNKNOWN)}
        for slot in range(16):
            need(time.monotonic()-start<600,'FROZEN_BUDGET')
            a,r=old.address(slot);rows,held,held_truth,degree=old.dataset(seed,slot)
            need(digest(canonical(rows))==refs[seed,slot]['source_sha256'],'QUALIFIED_SOURCE_DRIFT')
            truth={c|(b<<10):y for c,b,y in rows};truth.update(zip(held,held_truth));need(len(truth)==2048,'COMPLETE_TRUTH_CONTEXT')
            base_values=[base.predict(a,x&1023,x>>10,retained=r) for x in range(2048)]
            readouts=[bundle.readout(a,x&1023,x>>10,retained=r) for x in range(2048)]
            combined=[x['value'] for x in readouts];status=[x['status'] for x in readouts]
            iv,istatus=independent_answers(independent_base,slot,prior_raws.get(slot))
            need(combined==iv and status==istatus,'INDEPENDENT_READOUT_DRIFT')
            for before,after in zip(base_values,readouts):
                if before is not None:
                    need(after['value']==before and after['status']==IDENTIFIED,'IDENTIFIED_KNOWLEDGE_LOST');preserved+=1
                statuses[after['status']]+=1
            cart,snapshot,cart_seconds=fit_cart(rows,seed)
            score=old.score([cart[x] for x in held],held_truth)
            need(score==refs[seed,slot]['steps'][-1]['fully_trained_cart']['score'],'QUALIFIED_CART_RECONSTRUCTION_DRIFT')
            snapshot_name=f'cart-{seed}-{slot}.json';snapshot_raw=canonical(snapshot);(out/snapshot_name).write_bytes(snapshot_raw)
            seen=base._native._seen[slot];methods={'base':base_values,'combined':combined,'cart':cart,'fixed0':[0]*2048}
            decisions={m:{'all':decision_scores(v,truth,seen),'unfamiliar':decision_scores(v,truth,seen,unfamiliar_only=True)} for m,v in methods.items()}
            relations.append({'slot':slot,'source_sha256':digest(canonical(rows)),
                'held':{m:old.score([methods[m][x] for x in held],held_truth) for m in ('base','combined','cart')},
                'statuses':{k:status.count(k) for k in statuses},'decisions':decisions,
                'cart_snapshot_name':snapshot_name,'cart_snapshot_sha256':digest(snapshot_raw),'cart_fit_seconds':cart_seconds,
                'base_values_sha256':digest(canonical(base_values)),'combined_readouts_sha256':digest(canonical(readouts))})
            all_readouts.extend(readouts)
        path=out/f'seed-{seed}-source-bound-readout.json';saved=bundle.checkpoint();path.write_bytes(saved);fresh=cold(path,all_readouts)
        cases.append({'seed':seed,'original_base_sha256':c['checkpoint_sha256'],'base_unchanged':True,'bound_priors':len(prior_raws),
            'identified_preserved':preserved,'statuses':statuses,'relations':relations,'checkpoint_name':path.name,
            'checkpoint_sha256':digest(saved),'checkpoint_bytes':len(saved),'cold':fresh})
    summary=aggregate(cases);d=summary['decisions']
    gates={'new_unfamiliar_correct_preferences':d['combined_unfamiliar']['correct_preference']-d['base_unfamiliar']['correct_preference']>=16,
        'zero_wrong_preferences':d['combined_all']['wrong_preference']==0,
        'default_policy_reward_gain':d['combined_all']['policy_reward']-d['base_all']['policy_reward']>=8}
    need(summary['identified_preserved']==79872 and summary['held']['combined']=={'correct':64512,'incorrect':0,'abstained':9216,'questions':73728},'FROZEN_PREDICTION_APPLICATION_DRIFT')
    return {'schema':'yggdrasil.ckad10.result.v1','classification':'FROZEN_KNOWLEDGE_APPLICATION_SUPPORTED' if all(gates.values()) else 'APPLICATION_NO_GO',
        'scientific_pass':False,'accepted_native':False,'new_hypothesis_training_calls':0,'new_original_source_actions':0,
        'gates':gates,'summary':summary,'cases':cases,'whole_wall_seconds':time.monotonic()-start}


def stable(d):
    if isinstance(d,dict):return {k:stable(v) for k,v in d.items() if not k.endswith('_seconds') and k not in ('environment','source_candidate_sha','stable_sha256')}
    if isinstance(d,list):return [stable(v) for v in d]
    return d


def receipt(d):
    return {'classification':d['classification'],'stable_sha256':d['stable_sha256'],'gates':d['gates'],'summary':d['summary'],
        'cold_queries':sum(c['cold']['count'] for c in d['cases'])}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-directory',type=Path,required=True);p.add_argument('--verify-env',action='store_true');args=p.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True)
    with patch('yggdrasil.native_prior_hypothesis.program_weights',side_effect=RuntimeError('HYPOTHESIS_RETRAIN_FORBIDDEN')):
        d=audit(args.output_directory.resolve())
    d['source_candidate_sha']=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    d['environment']={'python':platform.python_version(),'platform':platform.platform()};d['stable_sha256']=digest(canonical(stable(d)))
    compact=receipt(d)
    if args.verify_env:need(compact==json.loads(os.environ['CKAD10_EXPECTED_RESULT']),'WINDOWS_DRIFT')
    (args.output_directory/'campaign-result.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    line=canonical(compact).decode('ascii');print(line)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('result='+line+'\n')
