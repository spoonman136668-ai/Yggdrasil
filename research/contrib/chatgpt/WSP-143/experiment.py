"""WSP143 source-safe prospective hierarchical causal composition trial.

Learners get only the SAME 32 actual public input/effect pairs per world.
The evaluator is the only module allowed to import the private source. All 64
predictions are frozen BEFORE selecting/scoring held observations.
"""
from hashlib import sha256
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
from types import SimpleNamespace
import sys,time,tracemalloc
import source as S
import concepts as H
import flat_control as F

ROOT=Path(__file__).resolve().parents[1]
def ancestor(alias,folder,file):
    spec=spec_from_file_location(alias,ROOT/folder/file)
    obj=module_from_spec(spec);sys.modules[alias]=obj;spec.loader.exec_module(obj)
    return obj
D=ancestor('_wsp143_pinned_wsp142_weights','WSP-142','direct_weights.py')
N=ancestor('_wsp143_pinned_wsp135_latent','WSP-135','learner.py')
B=ancestor('_wsp143_pinned_wsp135_cart','WSP-135','controls.py')

FAMILIES=(('known',tuple(sorted(S.KNOWN))),('three',tuple(sorted(S.UNFAMILIAR))),
          ('five',tuple(sorted(S.SWITCH))),('cross',tuple(sorted(S.CROSS))),
          ('off',tuple(sorted(S.OFF))))
METHODS=('hierarchical','equal_prior_flat','coarse_only','original_3term',
         'original_latent','fully_fitted_cart','no_update')
def zero():return {'correct':0,'wrong_confident':0,'abstained':0,'held':0}
def add(a,b):
    for k in a:a[k]+=b[k]
def score(out,truth,inputs):
    r=zero()
    for x in inputs:
        y=out[x]
        r['held']+=1
        if y is None:r['abstained']+=1
        elif type(y) is not int or y not in (0,1):
            raise AssertionError('WSP143_NONBINARY_CONFIDENT_ANSWER')
        elif y==truth[x]:r['correct']+=1
        else:r['wrong_confident']+=1
    return r
def future_questions(seed,unseen):
    return tuple(sorted(unseen,key=lambda x:(
       sha256(('WSP143|FUTURE|'+str(seed)+'|'+str(x)).encode()).digest(),x))[:16])
def pct(r,k):return 100*r[k]/r['held'] if r['held'] else 0

def run():
    start=time.perf_counter();cpu=time.process_time();tracemalloc.start()
    fixed=N.schedule()
    if len(fixed)!=32 or len(set(fixed))!=32 or len(D.FEATURES)!=63:
        raise AssertionError('WSP143_SOURCE_INDEPENDENT_PREDECESSOR_DRIFT')
    if tuple(sorted(set(m for lev in H.LEVELS.values() for m in lev)))!=tuple(D.FEATURES):
        raise AssertionError('WSP143_CONCEPT_LATTICE_NOT_COMPLETE')
    data={family:{method:{'future':zero(),'all_unseen':zero()}
            for method in METHODS} for family,seeds in FAMILIES}
    per_world=[]
    sources=[]
    saved_known={}
    model_time={method:0 for method in METHODS if method!='no_update'}
    source_events=0
    unique_levels={}
    for family,seeds in FAMILIES:
        for seed in seeds:
            view=S.world(seed);cust=S.Custodian(view,seed)
            rows=[]
            for x in fixed:
                e=cust.query(view.subject(x))
                if (e.law_id,e.subject,e.input)!=(view.law_id,view.subject(x),x):
                    raise AssertionError('WSP143_BAD_SOURCE_PUBLIC_EVENT')
                rows.append((e.input,e.effect))
            rows=tuple(rows)
            source_events+=32
            programs={}
            begin=time.process_time_ns()
            h=H.fit(rows)
            model_time['hierarchical']+=time.process_time_ns()-begin
            begin=time.process_time_ns()
            flat=F.symbolic_fit(rows)
            model_time['equal_prior_flat']+=time.process_time_ns()-begin
            if (h['level'],h['terms'],h['degree'],h['tied_count'],h['overflow'])!=(
                flat['level'],flat['terms'],flat['degree'],flat['count'],flat['overflow']):
                raise AssertionError(('WSP143_FULL_GRAMMAR_RANK_MISMATCH',family,seed))
            begin=time.process_time_ns()
            coarse=H.fit(rows,max_depth=2)
            model_time['coarse_only']+=time.process_time_ns()-begin
            begin=time.process_time_ns()
            direct=D.fit(rows)
            model_time['original_3term']+=time.process_time_ns()-begin
            begin=time.process_time_ns()
            latent=N.fit(rows)
            model_time['original_latent']+=time.process_time_ns()-begin
            tree=B.FullyFitCART()
            begin=time.process_time_ns()
            for law,subject,x,y in cust.events:
                tree.observe(view,SimpleNamespace(law_id=law,subject=subject,input=x,effect=y))
            tree.fit(view)
            model_time['fully_fitted_cart']+=time.process_time_ns()-begin
            if view.law_id not in tree.models or len(tree.examples[view.law_id])!=32:
                raise AssertionError('WSP143_CONVENTIONAL_CONTROL_NOT_FULLY_FITTED')
            outs={m:{} for m in METHODS}
            for x in range(64):
                a=H.predict(h,x);b=F.symbolic_predict(flat,x)
                if a!=b:
                    raise AssertionError(('WSP143_EQUAL_INFORMATION_SYMBOLIC_PREDICTION_DRIFT',family,seed,x))
                outs['hierarchical'][x]=a
                outs['equal_prior_flat'][x]=b
                outs['coarse_only'][x]=H.predict(coarse,x)
                outs['original_3term'][x]=D.predict(direct,x)
                outs['original_latent'][x]=N.predict(latent,x)
                outs['fully_fitted_cart'][x]=tree.infer(view,view.subject(x))
                outs['no_update'][x]=None
            unseen=tuple(x for x in range(64) if x not in fixed)
            future=future_questions(seed,unseen)
            if len(future)!=16 or not set(future)<=set(unseen):
                raise AssertionError('WSP143_BAD_UNSEEN_QUESTIONS')
            for m in METHODS:
                add(data[family][m]['future'],score(outs[m],cust.truth,future))
                add(data[family][m]['all_unseen'],score(outs[m],cust.truth,unseen))
            actual=cust.score_once({subject:outs['hierarchical'][x] for subject,x in cust.held()})
            if actual!=dict(score(outs['hierarchical'],cust.truth,unseen),source_calls=32):
                raise AssertionError('WSP143_CUSTODIAN_SCORE_DIFFERS_FROM_FROZEN')
            unique_levels[str(h['level'])]=unique_levels.get(str(h['level']),0)+1
            per_world.append({'family':family,'seed':seed,'level':h['level'],
                 'term_count':h['terms'],'degree':h['degree'],
                 'candidate_count':h['tied_count'],'overflow':h['overflow'],
                 'fit_sha256':H.digest(h),
                 'scores':{m:score(outs[m],cust.truth,future) for m in METHODS}})
            sources.append([family,seed,cust.receipt,H.digest(rows),H.digest(future),
                            H.digest([outs[m][x] for m in METHODS for x in range(64)])])
            if family=='known':
                saved_known[view.law_id]={'rows':rows,'state':h,'view':view,
                    'original_answers':outs['hierarchical']}
    if source_events!=1792 or len(per_world)!=56:
        raise AssertionError('WSP143_SOURCE_ACTION_BUDGET_DRIFT')
    for law,rec in saved_known.items():
        original=rec['original_answers']
        cold=H.restore(H.canon(rec['state']),rec['rows'])
        if any(H.predict(cold,x)!=original[x] for x in range(64)):
            raise AssertionError('WSP143_OLD_LAW_INTERFERENCE')
    cold_match=0
    cold_score=zero()
    for seed in sorted(S.TRANSFER):
        v=S.world(seed);c=S.Custodian(v,seed)
        rec=saved_known.get(v.law_id)
        if rec is None or c.budget!=0 or c.events:
            raise AssertionError('WSP143_NOT_ZERO_EFFECT_RELABELED_LAW')
        cold=H.restore(H.canon(rec['state']),rec['rows'])
        restored={}
        for x in range(64):
            y=H.predict(cold,x)
            cold_match+=int(y==rec['original_answers'][x])
            restored[x]=y
        add(cold_score,score(restored,c.truth,range(64)))
        c.score_once({subject:restored[x] for subject,x in c.held()})
    if cold_match!=256:
        raise AssertionError('WSP143_COLD_RESTORED_OUTPUT_NOT_IDENTICAL')
    stronger={}
    gains={}
    coverage={}
    errors={}
    for family,seeds in FAMILIES:
        choices=('original_3term','original_latent','fully_fitted_cart')
        strongest=max(choices,key=lambda m:(data[family][m]['future']['correct'],m))
        stronger[family]=strongest
        c=data[family]['hierarchical']['future']
        gains[family]=100*(c['correct']-data[family][strongest]['future']['correct'])/c['held']
        coverage[family]=100*(c['correct']+c['wrong_confident'])/c['held']
        errors[family]=pct(c,'wrong_confident')
    rules=(gains['three']>=10 and gains['five']>=10 and gains['cross']>=10
           and errors['three']<=1 and errors['five']<=1 and errors['cross']<=1
           and coverage['three']>=85 and coverage['five']>=65 and coverage['cross']>=75
           and gains['known']>=-5 and errors['off']<=2)
    _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    return {'schema':'wsp143.hierarchical-tokenless-causal-concept-development-result.v1',
       'status':'DEVELOPMENT_HIERARCHICAL_COMPOSITION_SUPPORTED' if rules else 'DEVELOPMENT_HIERARCHICAL_COMPOSITION_NO_GO',
       'scientific_pass':False,'native_yggdrasil_admission':False,
       'original_first_use_effects':0,'source_safe_public_effects':source_events,
       'cohort_worlds':{name:len(seeds) for name,seeds in FAMILIES},
       'zero_source_cold_relabels':len(S.TRANSFER),
       'shared_public_interventions_sha256':H.digest(fixed),
       'new_computational_primitives_invented':False,
       'candidate_and_independent_symbolic_exact_tie':True,
       'max_sparse_terms':4,'concept_depths':[2,3,4,5],
       'concept_level_counts':unique_levels,
       'scores':data,'strongest_original_by_family':stronger,
       'hierarchical_gain_over_strongest_original_pp':gains,
       'hierarchical_confident_error_pct':errors,'hierarchical_coverage_pct':coverage,
       'per_world':per_world,'source_receipts_sha256':H.digest(sources),
       'cold_relabel_exact_identity':cold_match,'cold_relabel_groundtruth':cold_score,
       'old_known_laws_unchanged':True,
       'resource':{'whole_trial_cpu_seconds':round(time.process_time()-cpu,3),
           'whole_trial_wall_seconds':round(time.perf_counter()-start,3),
           'peak_tracemalloc_bytes':peak,
           'per_arm_fit_cpu_seconds':{k:round(v/1e9,6) for k,v in model_time.items()},
           'energy':'NOT_MEASURED'},
       'limitations':['Public synthetic source, no original causal-world first-use',
           'Sparse AND/XOR primitives and compositional depth limits pre-supplied',
           'Hierarchical direct model ties equal-prior independently implemented flat symbolic',
           'No unique numerical-weight intelligence or transformer/text-token NCM replication',
           '16 worlds per hard family; correlated held states not 16 independent replications',
           'No independently trained deep recurrent control or matched whole-process power/energy evidence']}
if __name__=='__main__':
    print('WSP143_RESULT_JSON='+S.canon(run()))
