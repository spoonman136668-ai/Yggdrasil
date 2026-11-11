"""Frozen acquired-module composition; world identities/truth remain evaluator-only."""
import argparse
import hashlib
import json
import sys
import platform
import time
from pathlib import Path
from composition import Composition,PlasticNand,CONFIGS,context,forward
from controls import symbolic,symbolic_predict,feature_table,RAW,trained,predict
ROOT=Path(__file__).resolve().parent
sys.path.append(str(ROOT.parent/'WSP-27'))
from routed import Routed
sys.path.append(str(ROOT.parent/'WSP-28'))
from cases import load_manifest
PUBLIC=(0,1,2,4,7);HIDDEN=(3,5,6);RECIPES=((0,1,0),(1,0,2))
ARMS=('native','composition_disabled','symbolic','trained_raw','trained_shared','trained_gradient_base')

def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def deep_size(value,seen=None):
    seen=set() if seen is None else seen
    if id(value) in seen:return 0
    seen.add(id(value));n=sys.getsizeof(value)
    if isinstance(value,dict):n+=sum(deep_size(k,seen)+deep_size(v,seen) for k,v in value.items())
    elif isinstance(value,(list,tuple)):n+=sum(deep_size(v,seen) for v in value)
    return n

def source_truth(target,hidden):
    result=[0]*8
    for j,i in enumerate(PUBLIC+(3,)):result[i]=(target>>j)&1
    result[5]=hidden&1;result[6]=(hidden>>1)&1
    return result

def compose_truth(tables,recipe):
    a,b,j=recipe
    return tuple(tables[b][(i&~(1<<j))|(tables[a][i]<<j)] for i in range(8))

def run(write_modules=None):
    start=time.perf_counter();cases=load_manifest()['cases'];parent=json.loads((ROOT.parent/'WSP-28/result.json').read_text())
    expected={(c['seed'],c['signature']):c for c in parent['traces']}
    payloads=[];native_tables=[];gradient_tables=[];module_records=[];imperfect=source_fit=0
    times={a:0. for a in ARMS};times.update(native_module_acquisition=0.,gradient_source_acquisition=0.,native_feature_cache=0.,gradient_feature_cache=0.)
    fits={a:{'fits':0,'updates':0,'max_BCE':0.,'dot_multiplications':0,'gradient_multiplications':0} for a in ('sources','trained_raw','trained_shared','trained_gradient_base')}
    def fit_arm(examples,width,arm):
        w,n,loss=trained(examples,width);r=fits[arm];r['fits']+=1;r['updates']+=n;r['max_BCE']=max(r['max_BCE'],loss)
        r['dot_multiplications']+=len(examples)*width*(n+1);r['gradient_multiplications']+=len(examples)*width*n
        return w
    for c in cases:
        seed,sig,target=c['seed'],c['signature'],c['target'];obs=tuple((context(i),(target>>j)&1) for j,i in enumerate(PUBLIC+(3,)))
        tick=time.perf_counter();initial=PlasticNand().learn(obs[:5],seed);learned=Routed(initial.snapshot(),'error_routed').adapt(obs,seed)
        raw=learned.snapshot()
        if hashlib.sha256(raw).hexdigest()!=expected[seed,sig]['arms']['error_routed']['checkpoint_sha256']:raise AssertionError('WSP29_MODULE_CUSTODY')
        model=PlasticNand();model.rows=learned.rows;payloads.append(model.snapshot())
        table=tuple(model.predict(context(i)) for i in range(8));native_tables.append(table)
        fit=sum(table[i]==y for (x,y),i in zip(obs,PUBLIC+(3,)));source_fit+=fit;imperfect+=fit<6
        times['native_module_acquisition']+=time.perf_counter()-tick
        module_records.append({'seed':seed,'signature':sig,'target':target,'checkpoint_hex':raw.hex()})
        tick=time.perf_counter();w=fit_arm(tuple((RAW[i],y) for i,(x,y) in zip(PUBLIC+(3,),obs)),8,'sources')
        gradient_tables.append(tuple(predict(w,RAW[i]) for i in range(8)));times['gradient_source_acquisition']+=time.perf_counter()-tick
        print(f'WSP29_MODULE seed={seed} signature={sig}',file=sys.stderr,flush=True)
    module_artifact={'schema':'wsp29.acquired-module-checkpoints.v1','records':module_records}
    module_bytes=(json.dumps(module_artifact,sort_keys=True,indent=2)+'\n').encode()
    if write_modules is not None:Path(write_modules).write_bytes(module_bytes)
    committed=ROOT/'modules.json'
    if committed.exists() and json.loads(committed.read_text())!=module_artifact:raise AssertionError('WSP29_MODULE_ARTIFACT_DRIFT')
    scores={a:{'observed_correct':0,'heldout_correct':0} for a in ARMS};stats={k:0 for k in ('worlds','bank_retained','base_predictions_preserved','lesion_bank_retained','cold','lesion_cold','symbolic_checks','evidence_custody_checks')}
    traces=[];checkpoint_hash=hashlib.sha256();lesion_hash=hashlib.sha256();sizes=set();maxmemory=0;feature_bytes=0;info_ceiling=0;cfg_hist=[0]*12
    for pair in range(60):
        left,right=2*pair,2*pair+1
        if cases[left]['seed']!=cases[right]['seed']:raise AssertionError('WSP29_PAIR_CROSSED_SEED')
        bank=(payloads[left],payloads[right]);base=Composition(bank);bank_before=base.payloads();base_before=base.base_outputs()
        tick=time.perf_counter();nf=feature_table((native_tables[left],native_tables[right]));times['native_feature_cache']+=time.perf_counter()-tick
        tick=time.perf_counter();gf=feature_table((gradient_tables[left],gradient_tables[right]));times['gradient_feature_cache']+=time.perf_counter()-tick
        feature_bytes=max(feature_bytes,deep_size(nf)+deep_size(gf));groups={}
        for completion in range(16):
            truth=(source_truth(cases[left]['target'],completion&3),source_truth(cases[right]['target'],completion>>2))
            for recipe_index,recipe in enumerate(RECIPES):
                target=compose_truth(truth,recipe);obs=tuple((context(i),target[i]) for i in PUBLIC)
                tick=time.perf_counter();model=Composition(bank).learn(obs);native=tuple(model.predict(context(i)) for i in range(8));times['native']+=time.perf_counter()-tick
                tick=time.perf_counter();lesion=Composition(bank,0).learn(obs);disabled=tuple(lesion.predict(context(i)) for i in range(8));times['composition_disabled']+=time.perf_counter()-tick
                tick=time.perf_counter();choice=symbolic(model.banks,obs);sym=tuple(symbolic_predict(model.banks,choice,context(i)) for i in range(8));times['symbolic']+=time.perf_counter()-tick
                if sym!=native:raise AssertionError('WSP29_SYMBOLIC_DISAGREEMENT')
                stats['symbolic_checks']+=1;cfg_hist[CONFIGS.index(choice)]+=1
                raw=model.snapshot();restored=Composition.restore(raw)
                if restored.snapshot()!=raw or tuple(restored.predict(context(i)) for i in range(8))!=native:raise AssertionError('WSP29_COLD_OUTPUT')
                if model.payloads()!=bank_before or restored.payloads()!=bank_before or restored.base_outputs()!=base_before:raise AssertionError('WSP29_BASE_BANK_DAMAGED')
                stats['bank_retained']+=1;stats['base_predictions_preserved']+=16;stats['cold']+=1
                lr=lesion.snapshot();lc=Composition.restore(lr)
                if lc.snapshot()!=lr or tuple(lc.predict(context(i)) for i in range(8))!=disabled or lc.payloads()!=bank_before:raise AssertionError('WSP29_LESION_COLD_OR_BANK')
                stats['lesion_bank_retained']+=1;stats['lesion_cold']+=1
                checkpoint_hash.update(raw);lesion_hash.update(lr);sizes.add(len(raw));maxmemory=max(maxmemory,deep_size(model.__dict__)+sys.getsizeof(model))
                predictions={'native':native,'composition_disabled':disabled,'symbolic':sym}
                for arm,features,width in (('trained_raw',RAW,8),('trained_shared',nf,20),('trained_gradient_base',gf,20)):
                    tick=time.perf_counter();w=fit_arm(tuple((features[i],target[i]) for i in PUBLIC),width,arm)
                    predictions[arm]=tuple(predict(w,features[i]) for i in range(8));times[arm]+=time.perf_counter()-tick
                for arm,pred in predictions.items():
                    scores[arm]['observed_correct']+=sum(pred[i]==target[i] for i in PUBLIC)
                    scores[arm]['heldout_correct']+=sum(pred[i]==target[i] for i in HIDDEN)
                # Same actual evidence must produce same predictions,regardless of true hidden recipe/completion.
                key=tuple(target[i] for i in PUBLIC);answer=tuple(predictions[a] for a in ARMS)
                if key not in groups:groups[key]={'count':0,'ones':[0]*3,'answer':answer}
                elif groups[key]['answer']!=answer:raise AssertionError('WSP29_HIDDEN_EVIDENCE_LEAK')
                groups[key]['count']+=1
                for j,i in enumerate(HIDDEN):groups[key]['ones'][j]+=target[i]
                stats['evidence_custody_checks']+=1;stats['worlds']+=1
                traces.append([pair,completion,recipe_index,sum(target[i]<<j for j,i in enumerate(PUBLIC)),list(native),list(disabled),list(predictions['trained_raw']),list(predictions['trained_shared']),list(predictions['trained_gradient_base']),CONFIGS.index(choice),hashlib.sha256(raw).hexdigest()])
        info_ceiling+=sum(sum(max(n,g['count']-n) for n in g['ones']) for g in groups.values())
        print(f'WSP29_PAIR {pair+1}/60',file=sys.stderr,flush=True)
    fit_valid=(fits['sources']['fits']==120 and all(fits[a]['fits']==1920 for a in ('trained_raw','trained_shared','trained_gradient_base')) and all(f['max_BCE']<=.01 for f in fits.values()))
    required=(source_fit==707 and imperfect==13 and len(module_records)==120 and stats['worlds']==1920 and stats['base_predictions_preserved']==30720 and all(stats[k]==1920 for k in ('bank_retained','lesion_bank_retained','cold','lesion_cold','symbolic_checks','evidence_custody_checks')) and fit_valid and all(r['heldout_correct']<=info_ceiling for r in scores.values()))
    gains={a:scores['native']['heldout_correct']-scores[a]['heldout_correct'] for a in ('composition_disabled','trained_raw','trained_shared','trained_gradient_base')}
    supported=(scores['native']['observed_correct']>=8640 and gains['composition_disabled']>=288 and gains['trained_raw']>=288 and gains['trained_shared']>=-57 and gains['trained_gradient_base']>=-57 and required)
    report={'schema':'wsp29.acquired-module-composition.v1','engineering':'PASS' if required else 'FAIL','frozen_hypothesis':'DEV_SUPPORTED' if supported else 'SCIENTIFIC_NEGATIVE','scientific_superiority':'UNVERIFIED; finite supplied12routing language,authored correlated fixtures,capacity/representation/compute differ','scores':scores,'heldout_gains_native_minus_control':gains,'stats':stats,'source_modules':120,'source_observed_correct_of720':source_fit,'imperfect_source_modules_included':imperfect,'gradient_controls':fits,'heldout_information_ceiling_of5760':info_ceiling,'inference_binary_task_scalars':158,'static_configuration_bits':84,'native_route_learning_graph_forwards':1920*12*5*4,'native_route_learning_NAND_evaluations':1920*12*5*4*6,'candidate_continuous_gradient_steps':0,'feature_cache_max_python_bytes':feature_bytes,'native_retained_model_max_python_bytes':maxmemory,'checkpoint_bytes':sorted(sizes),'module_artifact_sha256':hashlib.sha256(module_bytes).hexdigest(),'native_checkpoint_digest_sha256':checkpoint_hash.hexdigest(),'lesion_checkpoint_digest_sha256':lesion_hash.hexdigest(),'configuration_histogram':cfg_hist,'trace_sha256':hashlib.sha256(canon(traces)).hexdigest(),'times_seconds':times,'total_seconds':time.perf_counter()-start,'environment':{'python':sys.version,'platform':platform.platform()},'trace_columns':['pair','completion','recipe_evaluator_only','five_observed_label_signature','native8','disabled8','trained_raw8','trained_shared8','trained_gradient_base8','learned_config_index','checkpoint_sha256'],'traces':traces,'limitations':'Native scores all12 supplied routings from5actual target examples. True recipe,source hidden labels and target heldouts are evaluator-only. All120actually acquired modules including13imperfect retained. Base-skill retention only,not memory for multiple composed heads/context discovery. Strongtrained heads really converged;capacity,float optimizer memory and featurecache differ. Source/target acquisition,featurebuild,search,checkpoint/retention and gradientcosts included in whole time;no universal speed or gradient-training superiority,unknown-world transfer,independent SCIENTIFIC_PASS or complete training.'}
    print(json.dumps(report,sort_keys=True,indent=2))
    if not required:raise SystemExit(1)
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write-modules',type=Path);args=p.parse_args();run(args.write_modules)
