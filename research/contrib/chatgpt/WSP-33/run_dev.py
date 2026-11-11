"""Broader public DEV: every programmed route, all missing source facts.

Only this evaluator sees true completions and recipes. The native model never
imports the symbolic certifier and receives only actually selected source answers.
"""
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
from broad_model import BroadModel,PlasticNand,CONFIGS,context,SOURCE_KNOWN,PUBLIC,HIDDEN,MODES,BUDGETS
from certifier import certify
ROOT=Path(__file__).resolve().parent
sys.path.append(str(ROOT.parent/'WSP-31'))
from control_baseline import FitCache,RAW,predict,feature_table,OPT_SOURCE
sys.path.append(str(ROOT.parent/'WSP-30'))
from diagnostic import read_verified,validate_trace,RESULT_HASH,MODULE_HASH,truth_table,response_tables
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
    tables=model.effective_tables();first=model.first.index(1);outer=model.outer.index(1);inject=model.inject.index(1)
    x=list(context(i));x[inject]=tables[first][i]
    return tables[outer][sum(v<<j for j,v in enumerate(x))]


def run():
    start=time.perf_counter();prior=ROOT.parent/'WSP-29'
    old=json.loads(read_verified(prior/'result.json',RESULT_HASH));validate_trace(old['traces'])
    modules=json.loads(read_verified(prior/'modules.json',MODULE_HASH))['records']
    payloads=[];observations=[]
    for record in modules:
        raw=bytes.fromhex(record['checkpoint_hex']);m=Routed.restore(raw)
        if m.snapshot()!=raw:raise AssertionError('WSP33_SOURCE_CUSTODY')
        p=PlasticNand();p.rows=m.rows;payloads.append(p.snapshot())
        observations.append(tuple((context(i),(record['target']>>j)&1) for j,i in enumerate(SOURCE_KNOWN)))
    cache=FitCache();provenance={p.name:hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest() for p in (ROOT/'broad_model.py',ROOT.parent/'WSP-31/control_baseline.py')};provenance['optimizer']=OPT_SOURCE
    scores={a:{'native':0} for a in MODES};scores['source_four'].update(shared_gradient=0,full_gradient=0,symbolic_majority=0)
    stats={k:0 for k in ('worlds','answers','phase_checks','old_fact_checks','acquired_fact_checks','cold_restores','replays','base_checks','source_locality_checks','symbolic_checks','counterfactual_states','planner_passes','question_invariance_checks','output_invariance_checks')}
    cert_stats={k:0 for k in ('source_label_checks','true_config_checks','certified_labels','certified_correct','ambiguous_labels','ambiguous_correct','fully_identifiable_worlds','partly_identifiable_worlds','unidentifiable_worlds')}
    signature_hist={};traces=[];question_seen={};output_seen={};hashes={a:hashlib.sha256() for a in MODES};sizes=set();resident=0
    recipe_scores={str(i):{a:0 for a in MODES} for i in range(12)}
    for pair in range(60):
        banks=tuple(payloads[2*pair:2*pair+2]);source=tuple(observations[2*pair:2*pair+2]);upstream=[hashlib.sha256(p).hexdigest() for p in banks]
        for completion in range(16):
            truth=(truth_table(modules[2*pair]['target'],completion&3),truth_table(modules[2*pair+1]['target'],completion>>2));targets=response_tables(truth)
            for ri,recipe in enumerate(CONFIGS):
                target=targets[ri];obs=tuple((context(i),target[i]) for i in PUBLIC)
                row=[pair,completion,ri];certificate=None
                for mode in MODES:
                    model=BroadModel(banks,source,obs,mode);acquired=[];phases=[]
                    for step in range(BUDGETS[mode]+1):
                        if step:
                            key=canon([upstream,model.source_known,model.source_labels,model.target_known,model.target_labels,mode])
                            q=model.query()
                            if key in question_seen and question_seen[key]!=q:raise AssertionError('WSP33_QUERY_LEAK')
                            question_seen[key]=q;stats['question_invariance_checks']+=1
                            if q is None or q[0]!='s':raise AssertionError('WSP33_BAD_QUERY')
                            stats['planner_passes']+=model.plan_evaluations;stats['counterfactual_states']+=2*(5-step)
                            before=model.effective_tables();answer=truth[q[1]][q[2]]
                            model.answer(q,answer);acquired.append((q,answer));stats['answers']+=1
                            after=model.effective_tables()
                            for b in range(2):
                                for i in range(8):
                                    if (b,i)!=(q[1],q[2]) and before[b][i]!=after[b][i]:raise AssertionError('WSP33_LOCALITY')
                                    stats['source_locality_checks']+=1
                        for b in range(2):
                            for x,y in source[b]:
                                if model._source(b,x)!=y:raise AssertionError('WSP33_OLD_SOURCE_LOST')
                                stats['old_fact_checks']+=1
                        for x,y in obs:
                            if model.predict(x)!=y:raise AssertionError('WSP33_OLD_TARGET_LOST')
                            stats['old_fact_checks']+=1
                        for q,y in acquired:
                            if model._source(q[1],context(q[2]))!=y:raise AssertionError('WSP33_NEW_FACT_LOST')
                            stats['acquired_fact_checks']+=1
                        predictions=tuple(model.predict(context(i)) for i in range(8))
                        for i in range(8):
                            if symbolic(model,i)!=predictions[i]:raise AssertionError('WSP33_SYMBOLIC_DISAGREEMENT')
                            stats['symbolic_checks']+=1
                        raw=model.snapshot();cold=BroadModel.restore(raw)
                        if cold.snapshot()!=raw or tuple(cold.predict(context(i)) for i in range(8))!=predictions:raise AssertionError('WSP33_COLD_DRIFT')
                        if cold.payloads()!=banks:raise AssertionError('WSP33_BASE_DRIFT')
                        for q,y in acquired:
                            model.answer(q,y)
                            if model.snapshot()!=raw:raise AssertionError('WSP33_REPLAY_MUTATION')
                            stats['replays']+=1
                        stats['cold_restores']+=1;stats['base_checks']+=1;stats['phase_checks']+=1
                        sizes.add(len(raw));resident=max(resident,deep_size(model.__dict__)+sys.getsizeof(model))
                        phases.append([acquired[-1] if step else None,list(predictions),hashlib.sha256(raw).hexdigest()]);model=cold
                    if model.query() is not None:raise AssertionError('WSP33_OVER_BUDGET')
                    knowledge={'upstream':upstream,'source_known':model.source_known,'source_labels':model.source_labels,'target_known':model.target_known,'target_labels':model.target_labels,'provenance':provenance}
                    outputs=[]
                    if mode=='source_four':
                        if len({q for q,y in acquired})!=4:raise AssertionError('WSP33_SOURCE_NOT_COMPLETE')
                        for b in range(2):
                            for i in range(8):
                                if not model.source_known[b][i] or model._source(b,context(i))!=truth[b][i]:raise AssertionError('WSP33_SOURCE_CLOSURE')
                                cert_stats['source_label_checks']+=1
                        certificate=certify(model)
                        if ri not in certificate['compatible_configs']:raise AssertionError('WSP33_TRUE_CONNECTION_DISCARDED')
                        cert_stats['true_config_checks']+=1;ncert=sum(y is not None for y in certificate['certified_predictions'])
                        cert_stats['fully_identifiable_worlds' if ncert==3 else 'unidentifiable_worlds' if ncert==0 else 'partly_identifiable_worlds']+=1
                        sig=str(len(certificate['possible_hidden_signatures']));signature_hist[sig]=signature_hist.get(sig,0)+1
                        for i,y in zip(HIDDEN,certificate['certified_predictions']):
                            if y is not None:
                                cert_stats['certified_labels']+=1
                                if y!=target[i] or predictions[i]!=y:raise AssertionError('WSP33_FALSE_CERTIFICATE_OR_INFERENCE_ERROR')
                                cert_stats['certified_correct']+=1
                            else:
                                cert_stats['ambiguous_labels']+=1;cert_stats['ambiguous_correct']+=int(predictions[i]==target[i])
                        scores[mode]['symbolic_majority']+=sum(y==target[i] for i,y in zip(HIDDEN,certificate['majority_predictions']))
                        gradient_tables=[]
                        for b in range(2):
                            train=tuple((RAW[i],model.source_labels[b][i]) for i in range(8) if model.source_known[b][i])
                            w=cache.fit(train,8,{**knowledge,'representation':'source8hot','slot':b});gradient_tables.append(tuple(predict(w,RAW[i]) for i in range(8)))
                        for kind,tables in (('shared',model.effective_tables()),('full',gradient_tables)):
                            features=feature_table(tables);train=tuple((features[i],model.target_labels[i]) for i in range(8) if model.target_known[i])
                            w=cache.fit(train,20,{**knowledge,'representation':kind+'20head'});outputs.append(tuple(predict(w,features[i]) for i in range(8)))
                        for label,values in zip(('shared_gradient','full_gradient'),outputs):scores[mode][label]+=sum(values[i]==target[i] for i in HIDDEN)
                    key=canon(knowledge);out=(predictions,tuple(outputs))
                    if key in output_seen and output_seen[key]!=out:raise AssertionError('WSP33_OUTPUT_LEAK')
                    output_seen[key]=out;stats['output_invariance_checks']+=1
                    correct=sum(predictions[i]==target[i] for i in HIDDEN);scores[mode]['native']+=correct;recipe_scores[str(ri)][mode]+=correct
                    hashes[mode].update(raw);row.append([phases,*[list(v) for v in outputs]])
                row.append(certificate);traces.append(row);stats['worlds']+=1
        print(f'WSP33_PAIR {pair+1}/60',file=sys.stderr,flush=True)
    required=(stats['worlds']==11520 and stats['answers']==69120 and stats['phase_checks']==stats['cold_restores']==stats['base_checks']==103680 and stats['old_fact_checks']==1762560 and stats['acquired_fact_checks']==stats['replays']==149760 and stats['source_locality_checks']==1105920 and stats['symbolic_checks']==829440 and stats['question_invariance_checks']==69120 and stats['output_invariance_checks']==34560 and stats['planner_passes']==69120 and stats['counterfactual_states']==391680 and cache.logical_fits==46080 and cache.max_BCE<=.01 and cert_stats['source_label_checks']==184320 and cert_stats['true_config_checks']==11520 and cert_stats['certified_labels']==cert_stats['certified_correct'] and cert_stats['certified_labels']+cert_stats['ambiguous_labels']==34560)
    gains={a:scores['source_four']['native']-scores[a]['native'] for a in ('source_two','no_query')};control_gains={a:scores['source_four']['native']-scores['source_four'][a] for a in ('symbolic_majority','shared_gradient','full_gradient')}
    supported=required and scores['source_four']['native']>=32832 and gains['source_two']>=346 and gains['no_query']>=692 and all(v>=-345 for v in control_gains.values())
    report={'schema':'wsp33.broad-knowledge-completion.v1','engineering':'PASS' if required else 'FAIL','source_fact_closure':'PASS' if required else 'INVALID','predictive_completion_hypothesis':('DEV_SUPPORTED' if supported else 'SCIENTIFIC_NEGATIVE') if required else 'INVALID','scores_of34560':scores,'gains_native':gains,'gains_vs_same_information_controls':control_gains,'stats':stats,'identifiability':cert_stats,'compatible_hidden_signature_count_histogram':signature_hist,'recipe_native_scores_of2880':recipe_scores,'gradient_cache':{'logical_fits':cache.logical_fits,'fresh_fits':cache.fresh_fits,'hits':cache.hits,'updates':cache.updates,'max_BCE':cache.max_BCE,'python_bytes':deep_size(cache.cache)},'checkpoint_digest':{a:h.hexdigest() for a,h in hashes.items()},'checkpoint_bytes':sorted(sizes),'native_postwrite_python_bytes_max':resident,'persistent_value_bits':209,'derived_bits_max':24,'total_seconds':time.perf_counter()-start,'environment':{'python':sys.version,'platform':platform.platform()},'trace_sha256':hashlib.sha256(canon(traces)).hexdigest(),'trace_columns':['pair','completion','recipe_evaluator_only',*MODES,'full_source_symbolic_certificate_evaluator_only'],'traces':traces,'limitations':'Authored public finite family; all12 supplied routing rules, not arbitrary primitive discovery or protected unfamiliar-world evaluation. Source closure certifies actual source facts, not ambiguous unqueried target knowledge. Full-source answer order cannot improve final information over any complete order. Symbolic certainty conditional on grammar; majority uniform-config prior supplied. Gradient controls fully trained/yoked to source_four only; capacity/priors/work differ. No complete training, SCIENTIFIC_PASS, lifelong memory, universal gradient advantage or efficiency/deployment claim.'}
    print(json.dumps(report,sort_keys=True,indent=2))
    if not required:raise SystemExit(1)
    return report
if __name__=='__main__':run()
