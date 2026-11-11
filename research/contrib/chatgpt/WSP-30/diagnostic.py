"""Evaluator-only oracle diagnosis. No candidate consumes oracle tables/routes."""
import hashlib
import itertools
import json
import platform
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.append(str(ROOT.parent/'WSP-29'))
from composition import Composition,PlasticNand,CONFIGS,route_bits,context
sys.path.append(str(ROOT.parent/'WSP-27'))
from routed import Routed
PUBLIC=(0,1,2,4,7);HIDDEN=(3,5,6);RECIPES=((0,1,0),(1,0,2))
RESULT_HASH='fc55e04786909cde54fb39917744cac6cbb1c3a63e0ea47efa1e5f08bbd073d8'
MODULE_HASH='db4492e7372a6e580c72c4de5a0e53eb69bf5a093fb84491a5bff1b1c536041a'
SCIENCE_HASHES={'composition.py':'074063c24145e888609e3ba4a0974107f4a4e778a539ce3853e9b5cdca856eb5','controls.py':'675e92358f59ba76abce50f9dac3a5be0fa7997b5ddcd6130af7cd6467468768','run_dev.py':'da097476947d04242c4a991b8c7d088b39e2f436de257f5b801aca1fe15d97f3'}
CONDITIONS=('actual_native','learned_tie_oracle','learned_language_oracle','perfect_source_five_rule','perfect_source_tie_oracle')

def canon(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def read_verified(path,expected):
    raw=Path(path).read_bytes().replace(b'\r\n',b'\n')
    if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('WSP30_SOURCE_HASH_REJECTED')
    return raw

def validate_trace(traces):
    if type(traces) is not list or len(traces)!=1920:raise ValueError('WSP30_BAD_TRACE_COUNT')
    for n,row in enumerate(traces):
        if type(row) is not list or len(row)!=11 or row[:3]!=[n//32,(n%32)//2,n%2]:raise ValueError('WSP30_BAD_TRACE_IDENTITY')
        if any(type(v) is not int for v in row[:4]) or not 0<=row[3]<32 or type(row[9]) is not int or not 0<=row[9]<12:raise ValueError('WSP30_BAD_TRACE_VALUE')
        if any(type(p) is not list or len(p)!=8 or any(type(v) is not int or v not in (0,1) for v in p) for p in row[4:9]):raise ValueError('WSP30_BAD_TRACE_PREDICTIONS')
        if type(row[10]) is not str or len(row[10])!=64 or any(v not in '0123456789abcdef' for v in row[10]):raise ValueError('WSP30_BAD_TRACE_CHECKPOINT')
    return traces

def truth_table(target,hidden):
    values=[0]*8
    for j,i in enumerate(PUBLIC+(3,)):values[i]=(target>>j)&1
    values[5]=hidden&1;values[6]=(hidden>>1)&1
    return tuple(values)

def response_tables(banks):
    return tuple(tuple(banks[b][(i&~(1<<j))|(banks[a][i]<<j)] for i in range(8)) for a,b,j in CONFIGS)

def fit(pred,target,indices):return sum(pred[i]==target[i] for i in indices)
def select_diagnostics(responses,target):
    observed=[fit(p,target,PUBLIC) for p in responses];held=[fit(p,target,HIDDEN) for p in responses]
    maximum=max(observed);ties=[i for i,v in enumerate(observed) if v==maximum]
    first=ties[0]
    tie_oracle=min(ties,key=lambda i:(-held[i],i))
    language_oracle=min(range(len(responses)),key=lambda i:(-held[i],-observed[i],i))
    return first,tie_oracle,language_oracle

def majority_bound(rows,refined=False):
    groups={}
    for pair,completion,evidence,target in rows:
        key=(pair,completion,evidence) if refined else (pair,evidence)
        if key not in groups:groups[key]=[0,[0,0,0]]
        groups[key][0]+=1
        for j,v in enumerate(target):groups[key][1][j]+=v
    return sum(sum(max(n,count-n) for n in ones) for count,ones in groups.values())

def independent_bound(rows,refined=False):
    # Enumerate all eight possible three-output predictions,not a majority formula.
    groups={}
    for pair,completion,evidence,target in rows:
        key=(pair,completion,evidence) if refined else (pair,evidence)
        groups.setdefault(key,[]).append(target)
    return sum(max(sum(sum(a==b for a,b in zip(pred,truth)) for truth in values) for pred in itertools.product((0,1),repeat=3)) for values in groups.values())

def information_partition(total,original,refined):
    if not 0<=original<=refined<=total:raise ValueError('WSP30_INVALID_GROUP_REFINEMENT')
    return {'original_irreducible':total-original,'source_information_value_bound':refined-original,'remaining_connection_information_ambiguity':total-refined}

def run():
    start=time.perf_counter();prior=ROOT.parent/'WSP-29'
    for name,sha in SCIENCE_HASHES.items():read_verified(prior/name,sha)
    old=json.loads(read_verified(prior/'result.json',RESULT_HASH));modules=json.loads(read_verified(prior/'modules.json',MODULE_HASH))
    validate_trace(old['traces'])
    if hashlib.sha256(canon(old['traces'])).hexdigest()!=old['trace_sha256']:raise AssertionError('WSP30_PRIOR_TRACE_DIGEST')
    if modules['schema']!='wsp29.acquired-module-checkpoints.v1' or len(modules['records'])!=120:raise ValueError('WSP30_BAD_MODULE_ARTIFACT')
    old28=json.loads((ROOT.parent/'WSP-28/result.json').read_text());expected={(c['seed'],c['signature']):c for c in old28['traces']}
    payloads=[];tables=[];source_fit=imperfect=0
    for record in modules['records']:
        seed,sig,target=record['seed'],record['signature'],record['target'];raw=bytes.fromhex(record['checkpoint_hex'])
        if hashlib.sha256(raw).hexdigest()!=expected[seed,sig]['arms']['error_routed']['checkpoint_sha256']:raise AssertionError('WSP30_MODULE_CUSTODY')
        restored=Routed.restore(raw)
        if restored.snapshot()!=raw:raise AssertionError('WSP30_MODULE_NONCANONICAL')
        base=PlasticNand();base.rows=restored.rows;payloads.append(base.snapshot());table=tuple(base.predict(context(i)) for i in range(8));tables.append(table)
        if list(table)!=expected[seed,sig]['arms']['error_routed']['predictions']:raise AssertionError('WSP30_MODULE_OUTPUT_DRIFT')
        correct=sum(table[i]==((target>>j)&1) for j,i in enumerate(PUBLIC+(3,)));source_fit+=correct;imperfect+=correct<6
    fit_counts=sum(v['fits'] for v in old['gradient_controls'].values())
    if fit_counts!=5880 or any(v['max_BCE']>.01 for v in old['gradient_controls'].values()):raise AssertionError('WSP30_PRIOR_CONVENTIONAL_FIT_INVALID')
    scores={a:{'observed_correct':0,'heldout_correct':0,'native_correct_observed_points_lost':0} for a in CONDITIONS};rows=[];traces=[];native_hash=hashlib.sha256()
    stats={'native_cold_restores':0,'banks_preserved':0,'base_predictions_preserved':0,'learned_graph_response_checks':0,'prior_trace_checks':0,'worlds':0}
    source_regression_worlds=0
    for pair in range(60):
        left,right=2*pair,2*pair+1;bank=(payloads[left],payloads[right]);bank_model=Composition(bank);base_outputs=bank_model.base_outputs()
        learned_responses=response_tables((tables[left],tables[right]))
        # Every cached response is independently checked against the generic graph circuit.
        probe=Composition(bank);probe.occupied=1
        for cfg,pred in zip(CONFIGS,learned_responses):
            probe.first,probe.outer,probe.inject=route_bits(cfg)
            for i in range(8):
                if probe.predict(context(i))!=pred[i]:raise AssertionError('WSP30_GRAPH_ENUMERATION_DRIFT')
                stats['learned_graph_response_checks']+=1
        for completion in range(16):
            source_truth=(truth_table(modules['records'][left]['target'],completion&3),truth_table(modules['records'][right]['target'],completion>>2))
            true_responses=response_tables(source_truth)
            for recipe_index,recipe in enumerate(RECIPES):
                n=pair*32+completion*2+recipe_index;prior_trace=old['traces'][n]
                target=true_responses[CONFIGS.index(recipe)];observed=tuple((context(i),target[i]) for i in PUBLIC);evidence=sum(target[i]<<j for j,i in enumerate(PUBLIC))
                actual=Composition(bank).learn(observed);pred=tuple(actual.predict(context(i)) for i in range(8));raw=actual.snapshot();cold=Composition.restore(raw)
                if list(pred)!=prior_trace[4] or evidence!=prior_trace[3] or hashlib.sha256(raw).hexdigest()!=prior_trace[10]:raise AssertionError('WSP30_ACTUAL_PREDICTION_CUSTODY')
                if cold.snapshot()!=raw or tuple(cold.predict(context(i)) for i in range(8))!=pred:raise AssertionError('WSP30_ACTUAL_COLD_DRIFT')
                if actual.payloads()!=bank or cold.payloads()!=bank or cold.base_outputs()!=base_outputs:raise AssertionError('WSP30_BANK_RETENTION_FAILURE')
                native_hash.update(raw);stats['native_cold_restores']+=1;stats['banks_preserved']+=1;stats['base_predictions_preserved']+=16;stats['prior_trace_checks']+=1;stats['worlds']+=1
                first,tie,language=select_diagnostics(learned_responses,target);true_first,true_tie,_=select_diagnostics(true_responses,target)
                if first!=prior_trace[9] or pred!=learned_responses[first]:raise AssertionError('WSP30_FIRST_SELECTION_DRIFT')
                selected={'actual_native':pred,'learned_tie_oracle':learned_responses[tie],'learned_language_oracle':learned_responses[language],'perfect_source_five_rule':true_responses[true_first],'perfect_source_tie_oracle':true_responses[true_tie]}
                held=[fit(selected[a],target,HIDDEN) for a in CONDITIONS]
                if not held[0]<=held[1]<=held[2] or held[4]!=3 or fit(selected['perfect_source_tie_oracle'],target,PUBLIC)!=5 or fit(selected['perfect_source_five_rule'],target,PUBLIC)!=5:raise AssertionError('WSP30_ORACLE_BOUND_INVALID')
                source_regression_worlds+=held[3]<held[0]
                native_valid=[i for i in PUBLIC if pred[i]==target[i]];summary=[]
                for arm in CONDITIONS:
                    p=selected[arm];o,h=fit(p,target,PUBLIC),fit(p,target,HIDDEN);lost=sum(p[i]!=target[i] for i in native_valid)
                    scores[arm]['observed_correct']+=o;scores[arm]['heldout_correct']+=h;scores[arm]['native_correct_observed_points_lost']+=lost;summary.extend((o,h,lost))
                rows.append((pair,completion,evidence,tuple(target[i] for i in HIDDEN)))
                traces.append([pair,completion,recipe_index,first,tie,language,true_first,true_tie]+summary)
        print(f'WSP30_PAIR {pair+1}/60',file=sys.stderr,flush=True)
    original=majority_bound(rows);refined=majority_bound(rows,True)
    if original!=independent_bound(rows) or refined!=independent_bound(rows,True):raise AssertionError('WSP30_INDEPENDENT_GROUP_CHECK_FAILED')
    partition=information_partition(5760,original,refined)
    if partition['source_information_value_bound']+partition['remaining_connection_information_ambiguity']!=partition['original_irreducible']:raise AssertionError('WSP30_PARTITION_FAILURE')
    required=(original==4672 and scores['actual_native']['heldout_correct']==4000 and scores['actual_native']['observed_correct']==8760 and scores['perfect_source_tie_oracle']['heldout_correct']==5760 and source_fit==707 and imperfect==13 and stats['worlds']==1920 and stats['base_predictions_preserved']==30720 and stats['native_cold_restores']==stats['banks_preserved']==stats['prior_trace_checks']==1920 and stats['learned_graph_response_checks']==5760 and native_hash.hexdigest()==old['native_checkpoint_digest_sha256'] and all(v['heldout_correct']<=original for v in old['scores'].values()))
    supported=partition['source_information_value_bound']>=partition['remaining_connection_information_ambiguity']
    report={'schema':'wsp30.composition-limit-diagnostic.v1','engineering':'PASS' if required else 'FAIL','frozen_hypothesis':'DIAGNOSTIC_SUPPORTED' if supported else 'DIAGNOSTIC_NEGATIVE','learning_improvement_claim':False,'scientific_superiority':'NONE;oracle diagnosis on unchanged public finite cohort','scores':scores,'original_information_ceiling_of5760':original,'source_refined_information_ceiling_of5760':refined,'information_partition':partition,'actual_native_error_count':1760,'actual_native_gap_below_original_information_ceiling':672,'perfect_source_five_rule_regression_worlds':source_regression_worlds,'stats':stats,'source_modules':120,'source_observed_correct_of720':source_fit,'imperfect_source_modules_included':imperfect,'prior_conventional_fit_count_reused':fit_counts,'prior_conventional_scores_reused':{a:v for a,v in old['scores'].items() if a.startswith('trained_')},'new_gradient_fits_executed':0,'new_source_adaptations_executed':0,'prior_result_sha256':RESULT_HASH,'module_artifact_sha256':MODULE_HASH,'native_checkpoint_digest_sha256':native_hash.hexdigest(),'trace_sha256':hashlib.sha256(canon(traces)).hexdigest(),'trace_columns':['pair','completion','recipe_evaluator_only','actual_config','learned_tie_oracle_config','learned_any_oracle_config','perfect_source_five_config','perfect_source_tie_oracle_config']+[a+'_'+m for a in CONDITIONS for m in ('observed_correct','heldout_correct','native_correct_observed_points_lost')],'traces':traces,'total_seconds':time.perf_counter()-start,'environment':{'python':sys.version,'platform':platform.platform()},'limitations':'All oracle selections/true tables are evaluator-only,not supplied to unchanged native learner or stored as learned checkpoints. Source truth substitution adds information AND implementation capacity. Only information-group partition is additive;oracle condition gains cannot be added or claimed achievable under original data/circuit budget. Teacher recipe inclusion makes perfect-source full oracle structural by construction. Shared authored taskfamily,all imperfect modules retained,no new learning/independent scientific superiority/complete training/promotion/deployment.'}
    print(json.dumps(report,sort_keys=True,indent=2))
    if not required:raise SystemExit(1)
    return report
if __name__=='__main__':run()
