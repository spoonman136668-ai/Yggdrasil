"""Frozen cumulative acquisition assay. Hidden truth belongs only to evaluator."""
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
from cumulative_model import CumulativeModel,PlasticNand,CONFIGS,context,SOURCE_KNOWN,PUBLIC,HIDDEN,MODES,BUDGETS
ROOT=Path(__file__).resolve().parent
sys.path.append(str(ROOT.parent/'WSP-31'))
from control_baseline import FitCache,RAW,predict,feature_table,OPT_SOURCE
sys.path.append(str(ROOT.parent/'WSP-30'))
from diagnostic import read_verified,validate_trace,RESULT_HASH,MODULE_HASH,truth_table,response_tables,RECIPES
from routed import Routed


def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def deep_size(value,seen=None):
    seen=set() if seen is None else seen
    if id(value) in seen:return 0
    seen.add(id(value));n=sys.getsizeof(value)
    if isinstance(value,dict):n+=sum(deep_size(k,seen)+deep_size(v,seen) for k,v in value.items())
    elif isinstance(value,(list,tuple)):n+=sum(deep_size(v,seen) for v in value)
    return n

def symbolic(model,i):
    if model.target_known[i]:return model.target_labels[i]
    tables=model.effective_tables()
    first=model.first.index(1);outer=model.outer.index(1);inject=model.inject.index(1)
    x=list(context(i));x[inject]=tables[first][i]
    return tables[outer][sum(v<<j for j,v in enumerate(x))]


def run():
    start=time.perf_counter();prior=ROOT.parent/'WSP-29'
    old=json.loads(read_verified(prior/'result.json',RESULT_HASH));validate_trace(old['traces'])
    modules=json.loads(read_verified(prior/'modules.json',MODULE_HASH))['records']
    payloads=[];observations=[]
    for record in modules:
        raw=bytes.fromhex(record['checkpoint_hex']);m=Routed.restore(raw)
        if m.snapshot()!=raw:raise AssertionError('WSP32_SOURCE_CUSTODY')
        p=PlasticNand();p.rows=m.rows;payloads.append(p.snapshot())
        observations.append(tuple((context(i),(record['target']>>j)&1) for j,i in enumerate(SOURCE_KNOWN)))
    cache=FitCache();provenance={p.name:hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest() for p in (ROOT/'cumulative_model.py',ROOT.parent/'WSP-31/control_baseline.py')};provenance['optimizer']=OPT_SOURCE
    scores={a:{'native':0,'shared_gradient':0,'full_gradient':0} for a in MODES}
    stats={k:0 for k in ('worlds','answers','phase_checks','old_fact_checks','acquired_fact_checks','cold_restores','replays','base_checks','source_locality_checks','symbolic_checks','counterfactual_states','planner_passes','question_invariance_checks','output_invariance_checks')}
    traces=[];question_seen={};output_seen={};hashes={a:hashlib.sha256() for a in MODES};sizes=set();resident=0
    for pair in range(60):
        banks=tuple(payloads[2*pair:2*pair+2]);source=tuple(observations[2*pair:2*pair+2]);upstream=[hashlib.sha256(p).hexdigest() for p in banks]
        for completion in range(16):
            truth=(truth_table(modules[2*pair]['target'],completion&3),truth_table(modules[2*pair+1]['target'],completion>>2));targets=response_tables(truth)
            for ri,recipe in enumerate(RECIPES):
                target=targets[CONFIGS.index(recipe)];obs=tuple((context(i),target[i]) for i in PUBLIC)
                row=[pair,completion,ri]
                for mode in MODES:
                    model=CumulativeModel(banks,source,obs,mode);acquired=[];phases=[]
                    for step in range(BUDGETS[mode]+1):
                        if step:
                            key=canon([upstream,model.source_known,model.source_labels,model.target_known,model.target_labels,mode])
                            q=model.query()
                            if key in question_seen and question_seen[key]!=q:raise AssertionError('WSP32_QUERY_LEAK')
                            question_seen[key]=q;stats['question_invariance_checks']+=1
                            if q is None or q[0]!='s':raise AssertionError('WSP32_BAD_QUERY')
                            stats['planner_passes']+=model.plan_evaluations
                            stats['counterfactual_states']+=2*(5-step)
                            before=model.effective_tables();answer=truth[q[1]][q[2]]
                            model.answer(q,answer);acquired.append((q,answer));stats['answers']+=1
                            after=model.effective_tables()
                            for b in range(2):
                                for i in range(8):
                                    if (b,i)!=(q[1],q[2]) and before[b][i]!=after[b][i]:raise AssertionError('WSP32_LOCALITY')
                                    stats['source_locality_checks']+=1
                        for b in range(2):
                            for x,y in source[b]:
                                if model._source(b,x)!=y:raise AssertionError('WSP32_OLD_SOURCE_LOST')
                                stats['old_fact_checks']+=1
                        for x,y in obs:
                            if model.predict(x)!=y:raise AssertionError('WSP32_OLD_TARGET_LOST')
                            stats['old_fact_checks']+=1
                        for q,y in acquired:
                            if model._source(q[1],context(q[2]))!=y:raise AssertionError('WSP32_NEW_FACT_LOST')
                            stats['acquired_fact_checks']+=1
                        predictions=tuple(model.predict(context(i)) for i in range(8))
                        for i in range(8):
                            if symbolic(model,i)!=predictions[i]:raise AssertionError('WSP32_SYMBOLIC_DISAGREEMENT')
                            stats['symbolic_checks']+=1
                        raw=model.snapshot();cold=CumulativeModel.restore(raw)
                        if cold.snapshot()!=raw or tuple(cold.predict(context(i)) for i in range(8))!=predictions:raise AssertionError('WSP32_COLD_DRIFT')
                        if cold.payloads()!=banks:raise AssertionError('WSP32_BASE_DRIFT')
                        for q,y in acquired:
                            model.answer(q,y)
                            if model.snapshot()!=raw:raise AssertionError('WSP32_REPLAY_MUTATION')
                            stats['replays']+=1
                        stats['cold_restores']+=1;stats['base_checks']+=1;stats['phase_checks']+=1
                        sizes.add(len(raw));resident=max(resident,deep_size(model.__dict__)+sys.getsizeof(model))
                        phases.append([acquired[-1] if step else None,list(predictions),hashlib.sha256(raw).hexdigest()])
                        # Continue from actual cold state, not the warm object's derived cache.
                        model=cold
                    if model.query() is not None:raise AssertionError('WSP32_OVER_BUDGET')
                    knowledge={'upstream':upstream,'source_known':model.source_known,'source_labels':model.source_labels,'target_known':model.target_known,'target_labels':model.target_labels,'provenance':provenance}
                    gradient_tables=[]
                    for b in range(2):
                        train=tuple((RAW[i],model.source_labels[b][i]) for i in range(8) if model.source_known[b][i])
                        w=cache.fit(train,8,{**knowledge,'representation':'source8hot','slot':b});gradient_tables.append(tuple(predict(w,RAW[i]) for i in range(8)))
                    outputs=[]
                    for kind,tables in (('shared',model.effective_tables()),('full',gradient_tables)):
                        features=feature_table(tables);train=tuple((features[i],model.target_labels[i]) for i in range(8) if model.target_known[i])
                        w=cache.fit(train,20,{**knowledge,'representation':kind+'20head'});outputs.append(tuple(predict(w,features[i]) for i in range(8)))
                    key=canon(knowledge);out=(predictions,tuple(outputs))
                    if key in output_seen and output_seen[key]!=out:raise AssertionError('WSP32_OUTPUT_LEAK')
                    output_seen[key]=out;stats['output_invariance_checks']+=1
                    for label,values in zip(('native','shared_gradient','full_gradient'),(predictions,*outputs)):
                        scores[mode][label]+=sum(values[i]==target[i] for i in HIDDEN)
                    hashes[mode].update(raw);row.append([phases,list(outputs[0]),list(outputs[1])])
                traces.append(row);stats['worlds']+=1
        print(f'WSP32_PAIR {pair+1}/60',file=sys.stderr,flush=True)
    required=(stats['worlds']==1920 and stats['answers']==9600 and stats['phase_checks']==stats['cold_restores']==stats['base_checks']==17280 and stats['old_fact_checks']==293760 and stats['acquired_fact_checks']==stats['replays']==13440 and stats['source_locality_checks']==153600 and stats['symbolic_checks']==138240 and stats['question_invariance_checks']==9600 and stats['output_invariance_checks']==7680 and cache.logical_fits==30720 and cache.max_BCE<=.01)
    gain={a:scores['source_two']['native']-scores[a]['native'] for a in ('source_one','no_query','source_first_two')}
    cgain={a:scores['source_two']['native']-scores['source_two'][a] for a in ('shared_gradient','full_gradient')}
    supported=required and gain['source_one']>=58 and gain['no_query']>=116 and gain['source_first_two']>=0 and all(v>=-57 for v in cgain.values())
    report={'schema':'wsp32.cumulative-acquisition.v1','engineering':'PASS' if required else 'FAIL','frozen_hypothesis':'DEV_SUPPORTED' if supported else 'SCIENTIFIC_NEGATIVE','scores_of5760':scores,'gains_native':gain,'gains_vs_yoked_gradient':cgain,'stats':stats,'gradient_cache':{'logical_fits':cache.logical_fits,'fresh_fits':cache.fresh_fits,'hits':cache.hits,'updates':cache.updates,'max_BCE':cache.max_BCE,'python_bytes':deep_size(cache.cache)},'checkpoint_digest':{a:h.hexdigest() for a,h in hashes.items()},'checkpoint_bytes':sorted(sizes),'native_python_bytes_max':resident,'persistent_value_bits':208,'derived_bits_max':24,'total_seconds':time.perf_counter()-start,'environment':{'python':sys.version,'platform':platform.platform()},'trace_sha256':hashlib.sha256(canon(traces)).hexdigest(),'trace_columns':['pair','completion','recipe_evaluator_only',*MODES],'traces':traces,'limitations':'Public finite-family DEV only; programmed planner/memory/router; symbolic execution tie; gradient controls yoked, different capacity/priors/cost. No complete-training, independent science, efficiency or deployment claim.'}
    print(json.dumps(report,sort_keys=True,indent=2))
    if not required:raise SystemExit(1)
    return report
if __name__=='__main__':run()
