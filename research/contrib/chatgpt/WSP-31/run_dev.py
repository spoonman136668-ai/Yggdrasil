"""Frozen one-actual-query assay;true hidden world data live only here."""
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
from fact_model import FactModel,PlasticNand,Composition,CONFIGS,context,SOURCE_KNOWN,PUBLIC,HIDDEN,MODES
from control_baseline import FitCache,RAW,predict,feature_table,OPT_SOURCE
ROOT=Path(__file__).resolve().parent
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

def run():
    start=time.perf_counter();prior=ROOT.parent/'WSP-29';old=json.loads(read_verified(prior/'result.json',RESULT_HASH));modules=json.loads(read_verified(prior/'modules.json',MODULE_HASH))['records'];validate_trace(old['traces'])
    bank_payloads=[];source_obs=[]
    for record in modules:
        raw=bytes.fromhex(record['checkpoint_hex']);m=Routed.restore(raw)
        if m.snapshot()!=raw:raise AssertionError('WSP31_SOURCE_CUSTODY')
        p=PlasticNand();p.rows=m.rows;bank_payloads.append(p.snapshot())
        source_obs.append(tuple((context(i),(record['target']>>j)&1) for j,i in enumerate(SOURCE_KNOWN)))
    cache=FitCache();code_provenance={'fact_model':hashlib.sha256((ROOT/'fact_model.py').read_bytes().replace(b'\r\n',b'\n')).hexdigest(),'baseline':hashlib.sha256((ROOT/'control_baseline.py').read_bytes().replace(b'\r\n',b'\n')).hexdigest(),'prior_optimizer':OPT_SOURCE}
    scores={a:{'native_common_correct':0,'shared_gradient_common_correct':0,'full_gradient_common_correct':0} for a in MODES};times={a:0. for a in MODES};times.update(shared_initial_planning=0.,conventional_fits_and_features=0.)
    stats={'worlds':0,'actual_query_answers':0,'old_fact_checks':0,'query_fact_checks':0,'cold_restores':0,'base_banks_retained':0,'source_locality_checks':0,'queried_evidence_replays':0,'initial_evidence_invariance_checks':0,'augmented_evidence_invariance_checks':0,'shared_planner_computations':0,'counterfactual_answer_states':0,'old_native_custody_checks':0}
    query_hist={a:{} for a in MODES};hashes={a:hashlib.sha256() for a in MODES};sizes=set();traces=[];initial_history={};augmented_history={};retained_bytes=0;old_common=0;gradient_max_loss=0.
    for pair in range(60):
        left,right=pair*2,pair*2+1;payloads=(bank_payloads[left],bank_payloads[right]);source=(source_obs[left],source_obs[right]);upstream=[hashlib.sha256(p).hexdigest() for p in payloads]
        for completion in range(16):
            truth=(truth_table(modules[left]['target'],completion&3),truth_table(modules[right]['target'],completion>>2));targets=response_tables(truth)
            for ri,recipe in enumerate(RECIPES):
                n=pair*32+completion*2+ri;target=targets[CONFIGS.index(recipe)];obs=tuple((context(i),target[i]) for i in PUBLIC)
                original=Composition(payloads).learn(obs);rawold=original.snapshot()
                if hashlib.sha256(rawold).hexdigest()!=old['traces'][n][10] or [original.predict(context(i)) for i in range(8)]!=old['traces'][n][4]:raise AssertionError('WSP31_OLD_NATIVE_CUSTODY')
                stats['old_native_custody_checks']+=1
                tick=time.perf_counter();initial=FactModel(payloads,source,obs);initial.plan();times['shared_initial_planning']+=time.perf_counter()-tick
                stats['shared_planner_computations']+=initial.plan_evaluations;stats['counterfactual_answer_states']+=14
                connection_question=initial.clone('connection_impact').query();evaluation=tuple(i for i in HIDDEN if i!=connection_question[2])
                if len(evaluation)!=2:raise AssertionError('WSP31_QUERIED_POINT_IN_SCORE')
                questions=tuple(initial.clone(a).query() for a in MODES);initial_key=canon([upstream,initial.source_known,initial.source_labels,initial.target_known,initial.target_labels])
                if initial_key in initial_history and initial_history[initial_key]!=questions:raise AssertionError('WSP31_QUERY_HIDDEN_INFO_LEAK')
                initial_history[initial_key]=questions;stats['initial_evidence_invariance_checks']+=1
                old_common+=sum(old['traces'][n][4][i]==target[i] for i in evaluation)
                record=[pair,completion,ri,list(evaluation)];source_before=initial.effective_tables()
                for mode,q in zip(MODES,questions):
                    tick=time.perf_counter();model=initial.clone(mode);answer=None
                    if q is not None:
                        answer=truth[q[1]][q[2]] if q[0]=='s' else target[q[2]]
                        model.answer(q,answer);stats['actual_query_answers']+=1
                        if not model.query_used or model.query() is not None:raise AssertionError('WSP31_QUERY_BUDGET')
                        current=model.effective_tables()[q[1]][q[2]] if q[0]=='s' else model.predict(context(q[2]))
                        if current!=answer:raise AssertionError('WSP31_QUERY_FACT_NOT_STORED')
                        stats['query_fact_checks']+=1
                    elif mode!='no_query' or model.query_used:raise AssertionError('WSP31_UNANSWERED_QUERY')
                    for b in range(2):
                        for x,y in source[b]:
                            i=sum(v<<j for j,v in enumerate(x))
                            if model.effective_tables()[b][i]!=y:raise AssertionError('WSP31_OLD_SOURCE_FACT_LOST')
                            stats['old_fact_checks']+=1
                    for x,y in obs:
                        if model.predict(x)!=y:raise AssertionError('WSP31_OLD_TARGET_FACT_LOST')
                        stats['old_fact_checks']+=1
                    for b in range(2):
                        for i in range(8):
                            if q is None or q[0]!='s' or (b,i)!=(q[1],q[2]):
                                if model.effective_tables()[b][i]!=source_before[b][i]:raise AssertionError('WSP31_UNQUERIED_SOURCE_CHANGED')
                            stats['source_locality_checks']+=1
                    predictions=tuple(model.predict(context(i)) for i in range(8));raw=model.snapshot();cold=FactModel.restore(raw)
                    if cold.snapshot()!=raw or tuple(cold.predict(context(i)) for i in range(8))!=predictions or cold.effective_tables()!=model.effective_tables():raise AssertionError('WSP31_COLD_DRIFT')
                    if model.payloads()!=payloads or cold.payloads()!=payloads:raise AssertionError('WSP31_BASE_GRAPH_CHANGED')
                    stats['cold_restores']+=1;stats['base_banks_retained']+=1;hashes[mode].update(raw);sizes.add(len(raw));retained_bytes=max(retained_bytes,deep_size(model.__dict__)+sys.getsizeof(model))
                    if q is not None:
                        model.answer(q,answer)
                        if model.snapshot()!=raw:raise AssertionError('WSP31_EVIDENCE_REPLAY_MUTATION')
                        stats['queried_evidence_replays']+=1
                    qkey='none' if q is None else ':'.join(map(str,q));query_hist[mode][qkey]=query_hist[mode].get(qkey,0)+1
                    times[mode]+=time.perf_counter()-tick
                    # Baselines see ONLY the actual known facts and same question/answer.
                    tick=time.perf_counter();knowledge={'upstream':upstream,'source_known':model.source_known,'source_labels':model.source_labels,'target_known':model.target_known,'target_labels':model.target_labels,'provenance':code_provenance}
                    gradient_tables=[]
                    for b in range(2):
                        train=tuple((RAW[i],model.source_labels[b][i]) for i in range(8) if model.source_known[b][i])
                        w=cache.fit(train,8,{**knowledge,'representation':'source8hot','slot':b});gradient_tables.append(tuple(predict(w,RAW[i]) for i in range(8)))
                    nf=feature_table(model.effective_tables());gf=feature_table(gradient_tables);baseline_predictions=[]
                    for kind,features in (('shared',nf),('full',gf)):
                        train=tuple((features[i],model.target_labels[i]) for i in range(8) if model.target_known[i]);w=cache.fit(train,20,{**knowledge,'representation':kind+'20head'})
                        baseline_predictions.append(tuple(predict(w,features[i]) for i in range(8)))
                    times['conventional_fits_and_features']+=time.perf_counter()-tick
                    aug_key=canon(knowledge);out=(predictions,tuple(baseline_predictions))
                    if aug_key in augmented_history and augmented_history[aug_key]!=out:raise AssertionError('WSP31_AUGMENTED_HIDDEN_INFO_LEAK')
                    augmented_history[aug_key]=out;stats['augmented_evidence_invariance_checks']+=1
                    scores[mode]['native_common_correct']+=sum(predictions[i]==target[i] for i in evaluation)
                    scores[mode]['shared_gradient_common_correct']+=sum(baseline_predictions[0][i]==target[i] for i in evaluation)
                    scores[mode]['full_gradient_common_correct']+=sum(baseline_predictions[1][i]==target[i] for i in evaluation)
                    record.append([q,answer,list(predictions),list(baseline_predictions[0]),list(baseline_predictions[1]),hashlib.sha256(raw).hexdigest()])
                traces.append(record);stats['worlds']+=1
        print(f'WSP31_PAIR {pair+1}/60',file=sys.stderr,flush=True)
    required=(stats['worlds']==1920 and stats['actual_query_answers']==5760 and stats['old_fact_checks']==130560 and stats['query_fact_checks']==5760 and stats['cold_restores']==stats['base_banks_retained']==stats['augmented_evidence_invariance_checks']==7680 and stats['queried_evidence_replays']==5760 and stats['old_native_custody_checks']==stats['initial_evidence_invariance_checks']==stats['shared_planner_computations']==1920 and stats['counterfactual_answer_states']==26880 and stats['source_locality_checks']==122880 and cache.logical_fits==30720 and cache.fresh_fits+cache.hits==30720 and cache.max_BCE<=.01)
    source_score=scores['source_impact']['native_common_correct'];gains={a:source_score-scores[a]['native_common_correct'] for a in ('no_query','connection_impact','source_first')}
    conventional_gains={a:source_score-scores['source_impact'][a] for a in ('shared_gradient_common_correct','full_gradient_common_correct')}
    supported=(gains['no_query']>=77 and gains['connection_impact']>=39 and gains['source_first']>=0 and all(v>=-38 for v in conventional_gains.values()) and required)
    report={'schema':'wsp31.one-query-fact-acquisition.v1','engineering':'PASS' if required else 'FAIL','frozen_hypothesis':'DEV_SUPPORTED' if supported else 'SCIENTIFIC_NEGATIVE','scientific_superiority':'UNVERIFIED;publicfinitefamily,newmemory/hand-designedimpactproxy,unequalgradientcapacity/cost','scores_common_of3840':scores,'source_impact_gains_native':gains,'source_impact_gains_vs_yoked_gradient_heads':conventional_gains,'old_WSP29_native_on_same_common_points':old_common,'noquery_representation_only_gain_on_same_points':scores['no_query']['native_common_correct']-old_common,'stats':stats,'query_histograms':query_hist,'gradient_cache':{'logical_fits':cache.logical_fits,'fresh_fits':cache.fresh_fits,'cache_hits':cache.hits,'updates_executed':cache.updates,'max_BCE':cache.max_BCE,'dot_multiplications_executed':cache.dot_multiplications,'gradient_multiplications_executed':cache.gradient_multiplications,'cache_entries':len(cache.cache),'cache_python_bytes':deep_size(cache.cache)},'writable_persistent_binary_scalars':207,'derived_fallback_bits':16,'derived_impact_cache_bits_max':14,'resident_value_bits_max':237,'static_routing_descriptor_bits':84,'retained_native_max_python_bytes':retained_bytes,'checkpoint_bytes':sorted(sizes),'source_module_artifact_sha256':MODULE_HASH,'checkpoint_digest_sha256':{a:h.hexdigest() for a,h in hashes.items()},'trace_sha256':hashlib.sha256(canon(traces)).hexdigest(),'times_seconds':times,'total_seconds':time.perf_counter()-start,'environment':{'python':sys.version,'platform':platform.platform()},'trace_columns':['pair','completion','recipe_evaluator_only','common_unqueried_inputs']+list(MODES),'traces':traces,'limitations':'Known facts are faithfully stored with49additionalwritablebits vsWSP29,pluscountedderivedcaches. Representation-only gain separate fromactualquerygain. One actual binary answer perqueryarm,noquery0;queriedtargetinput excludedforallarms. Queryimpact is supplied sensitivityproxy,notoptimalinformationpolicy. Conventionalheads yoked to same actualqueryanswers,notindependentactivequerypolicies. Same data not same prior/capacity/optimizer/FLOPs;modelcache exact semantic evidence/provenance only. Alloracletables evaluator-only,onlyselectedbitprovidedtolearner. No generalnoise/lifelongmemory/unknownworld/complete-training/universaldirect-gradientadvantageclaim.'}
    print(json.dumps(report,sort_keys=True,indent=2))
    if not required:raise SystemExit(1)
    return report
if __name__=='__main__':run()
