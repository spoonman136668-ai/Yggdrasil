"""WSP-144: source-blind diagnostic observation of rare causal conjunctions.

Same unchanged hierarchical WSP143 learner for fixed32, diagnostic32, random32.
All three arms use 32 actual independent public paid source effects per world;
all arms are evaluated on the exact same 16 held inputs excluded in advance.
Unknown original-source experiments remain explicitly denied.
"""
from hashlib import sha256
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
import sys,time,tracemalloc
import source as S

ROOT=Path(__file__).resolve().parents[1]
def pin(name,relative):
    spec=spec_from_file_location(name,ROOT/relative)
    obj=module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj);return obj
H=pin('_wsp144_pinned_hierarchical','WSP-143/concepts.py')
F=pin('_wsp144_independent_flat','WSP-143/flat_control.py')
D=pin('_wsp144_original_weight_three','WSP-142/direct_weights.py')
N=pin('_wsp144_original_wsp135_numeric','WSP-135/learner.py')
C=pin('_wsp144_fully_fitted_conventional','WSP-135/controls.py')

POLICIES=('fixed','diagnostic','random')
METHODS=('hierarchical','equal_prior_symbolic','original_3term','original_latent','fully_fitted_cart','coarse_only','no_update')
FAMILIES=(('known',tuple(sorted(S.KNOWN))),('three',tuple(sorted(S.UNFAMILIAR))),
 ('five',tuple(sorted(S.SWITCH))),('cross',tuple(sorted(S.CROSS))),
 ('off',tuple(sorted(S.OFF))))
ANCHORS=(47,59,61,63)
CHALLENGE=(31,55,62)

def schedules():
    original=N.schedule()
    if len(original)!=32 or len(set(original))!=32 or 47 not in original:
        raise AssertionError('WSP144_PINNED_ORIGINAL_SCHEDULE_DRIFT')
    diagnostic=ANCHORS+tuple(x for x in original if x not in ANCHORS)[:28]
    if len(diagnostic)!=32 or len(set(diagnostic))!=32:
        raise AssertionError('WSP144_DIAGNOSTIC_SCHEDULE_ERROR')
    assert not set(CHALLENGE)&(set(original)|set(diagnostic))
    remaining=set(range(64))-set(original)-set(diagnostic)-set(CHALLENGE)
    extra=tuple(sorted(remaining,key=lambda x:(
       sha256(('WSP144|COMMON|'+str(x)).encode()).digest(),x))[:13])
    common=tuple(sorted(CHALLENGE+extra))
    legal=frozenset(set(range(64))-set(common))
    if len(common)!=16 or len(legal)!=48 or set(common)&(set(original)|set(diagnostic)):
        raise AssertionError('WSP144_COMMON_HELD_NOT_UNPAID')
    for xset in (original,diagnostic):
        if any(x not in legal for x in xset):raise AssertionError('WSP144_PUBLIC_ACTION_ELIGIBILITY_CHANGED')
    original_activation=[sum(1 for x in original if x&m==m) for m in (31,47,55,59,61,62)]
    diag_activation=[sum(1 for x in diagnostic if x&m==m) for m in (31,47,55,59,61,62)]
    if original_activation!=[0,1,0,0,0,0] or diag_activation!=[1,2,1,2,2,1]:
        raise AssertionError(('WSP144_PRECOMMITTED_DEGREE5_COVERAGE_DRIFT',original_activation,diag_activation))
    return original,diagnostic,common,legal

def choose_random(view,legal):
    return tuple(sorted(legal,key=lambda x:(
        sha256(('WSP144|RANDOM|'+str(view.law_id)+'|'+str(x)).encode()).digest(),x))[:32])

def zero():return {'correct':0,'wrong_confident':0,'abstained':0,'held':0}
def add(a,b):
    for k in a:a[k]+=b[k]
def score(outputs,truth,contexts):
    r=zero()
    for x in contexts:
        y=outputs[x];r['held']+=1
        if y is None:r['abstained']+=1
        elif type(y) is not int or y not in (0,1):
            raise AssertionError('WSP144_NONBINARY_CONFIDENT_ANSWER')
        elif y==truth[x]:r['correct']+=1
        else:r['wrong_confident']+=1
    return r
def pct(row,k):return 100*row[k]/row['held'] if row['held'] else 0

def train(readings,view):
    rows=tuple(readings)
    t0=time.process_time_ns()
    h=H.fit(rows)
    f=F.symbolic_fit(rows)
    if (h['level'],h['terms'],h['degree'],h['tied_count'],h['overflow'])!=(
        f['level'],f['terms'],f['degree'],f['count'],f['overflow']):
        raise AssertionError('WSP144_INDEPENDENT_FULL_FIT_RANK_MISMATCH')
    base=D.fit(rows)
    latent=N.fit(rows)
    tree=C.FullyFitCART()
    for x,y in rows:
        tree.observe(view,SimpleNamespace(law_id=view.law_id,
                   subject=view.subject(x),input=x,effect=y))
    tree.fit(view)
    if view.law_id not in tree.models or len(tree.examples[view.law_id])!=32:
        raise AssertionError('WSP144_CONVENTIONAL_NOT_FULLY_TRAINED')
    coarse=H.fit(rows,max_depth=2)
    outs={m:{} for m in METHODS}
    for x in range(64):
        a=H.predict(h,x);b=F.symbolic_predict(f,x)
        if a!=b:raise AssertionError('WSP144_INDEPENDENT_SAME_INFO_SYMBOLIC_TIE_FAIL')
        outs['hierarchical'][x]=a;outs['equal_prior_symbolic'][x]=b
        outs['original_3term'][x]=D.predict(base,x)
        outs['original_latent'][x]=N.predict(latent,x)
        outs['fully_fitted_cart'][x]=tree.infer(view,view.subject(x))
        outs['coarse_only'][x]=H.predict(coarse,x)
        outs['no_update'][x]=None
    return h,outs,time.process_time_ns()-t0

def run():
    trial_wall=time.perf_counter();trial_cpu=time.process_time()
    tracemalloc.start()
    fixed,diag,common,eligible=schedules()
    if len(H.LEVELS)!=6 or len(N.templates())!=17640 or len(D.FEATURES)!=63:
        raise AssertionError('WSP144_INHERITED_FEATURE_INTERFACE_DRIFT')
    scores={family:{policy:{m:{'paired':zero(),'unseen32':zero()} for m in METHODS}
                   for policy in POLICIES}
            for family,seeds in FAMILIES}
    details=[];receipts=[];known={p:{} for p in POLICIES}
    fits_ns={p:0 for p in POLICIES}
    source_counts={p:0 for p in POLICIES}
    for family,seeds in FAMILIES:
        for seed in seeds:
            view=S.world(seed)
            policies={'fixed':fixed,'diagnostic':diag,'random':choose_random(view,eligible)}
            for p,actions in policies.items():
                if len(actions)!=32 or len(set(actions))!=32 or any(x not in eligible for x in actions):
                    raise AssertionError('WSP144_ARM_UNQUALIFIED_ACTIONS')
                cust=S.Custodian(view,seed)
                rows=[]
                for x in actions:
                    receipt=cust.query(view.subject(x))
                    if (receipt.law_id,receipt.input,receipt.subject)!=(view.law_id,x,view.subject(x)):
                        raise AssertionError('WSP144_PAID_PUBLIC_SOURCE_IDENTITY')
                    rows.append((receipt.input,receipt.effect))
                source_counts[p]+=len(rows)
                h,outs,cpu_ns=train(rows,view)
                fits_ns[p]+=cpu_ns
                held=tuple(x for x in range(64) if x not in set(actions))
                if len(held)!=32 or not set(common)<=set(held):
                    raise AssertionError('WSP144_PAIRED_HELD_NOT_COMMON')
                for m in METHODS:
                    add(scores[family][p][m]['paired'],score(outs[m],cust.truth,common))
                    add(scores[family][p][m]['unseen32'],score(outs[m],cust.truth,held))
                owner=cust.score_once({subject:outs['hierarchical'][x] for subject,x in cust.held()})
                if owner!=dict(score(outs['hierarchical'],cust.truth,held),source_calls=32):
                    raise AssertionError('WSP144_SOURCE_OWNER_SCORING_WRONG')
                details.append({'family':family,'seed':seed,'policy':p,
                    'level':h['level'],'terms':h['terms'],'degree':h['degree'],
                    'tied':h['tied_count'],'overflow':h['overflow'],
                    'paired':{m:score(outs[m],cust.truth,common) for m in METHODS}})
                receipts.append([family,seed,p,cust.receipt,
                       H.digest(rows),H.digest([outs[m][x] for m in METHODS for x in range(64)])])
                if family=='known':
                    known[p][view.law_id]={'rows':tuple(rows),'state':h,
                                              'outs':outs['hierarchical']}
    if source_counts!={p:1536 for p in POLICIES} or len(details)!=144:
        raise AssertionError('WSP144_PAID_SOURCE_BUDGET_NOT_EXACT')
    for p in POLICIES:
        for law,record in known[p].items():
            cold=H.restore(H.canon(record['state']),record['rows'])
            if any(H.predict(cold,x)!=record['outs'][x] for x in range(64)):
                raise AssertionError('WSP144_RETENTION_DRIFT')
    cold_counts={p:0 for p in POLICIES}
    cold_scores={p:zero() for p in POLICIES}
    for seed in sorted(S.TRANSFER):
        view=S.world(seed)
        for p in POLICIES:
            cust=S.Custodian(view,seed)
            if cust.budget or cust.events:raise AssertionError('WSP144_COLD_SOURCE_BUDGET_CHANGED')
            old=known[p][view.law_id]
            restored=H.restore(H.canon(old['state']),old['rows'])
            outs={x:H.predict(restored,x) for x in range(64)}
            cold_counts[p]+=sum(outs[x]==old['outs'][x] for x in range(64))
            add(cold_scores[p],score(outs,cust.truth,range(64)))
            cust.score_once({s:outs[x] for s,x in cust.held()})
    if cold_counts!={p:256 for p in POLICIES}:
        raise AssertionError('WSP144_COLD_RELABEL_NOT_EXACT')
    # The strongest acquisition control, from the same hierarchical learner:
    five={p:scores['five'][p]['hierarchical']['paired'] for p in POLICIES}
    strongest=max(('fixed','random'),key=lambda p:(five[p]['correct'],p))
    improvement_pp=100*(five['diagnostic']['correct']-five[strongest]['correct'])/256
    cart=scores['five']['diagnostic']['fully_fitted_cart']['paired']
    other={f: {
      'diagnostic':scores[f]['diagnostic']['hierarchical']['paired'],
      'best_control_correct':max(scores[f][p]['hierarchical']['paired']['correct'] for p in ('fixed','random'))}
      for f in ('known','three','cross')}
    supported=(improvement_pp>=3 and pct(five['diagnostic'],'wrong_confident')<=1
      and five['diagnostic']['correct']>=cart['correct']
      and all(100*(v['best_control_correct']-v['diagnostic']['correct'])/v['diagnostic']['held']<=5
              and pct(v['diagnostic'],'wrong_confident')<=1 for v in other.values())
      and pct(scores['off']['diagnostic']['hierarchical']['paired'],'wrong_confident')<=2)
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {'schema':'wsp144.diagnostic-highorder-sourceblind-acquisition.v1',
       'status':'DEVELOPMENT_DIAGNOSTIC_HIGHORDER_ACQUISITION_SUPPORTED' if supported else
                'DEVELOPMENT_DIAGNOSTIC_HIGHORDER_ACQUISITION_NO_GO',
       'scientific_pass':False,'native_model_promoted':False,'original_protected_first_use':0,
       'new_public_source_effects':sum(source_counts.values()),'source_actions_per_arm':source_counts,
       'cohorts':{family:len(seeds) for family,seeds in FAMILIES},'cold_source_views':len(S.TRANSFER),
       'full_same_information_symbolic_prediction_parity':True,
       'all_arms_use_32_public_eligible_effects':True,
       'common_held_inputs':list(common),'original_fixed_actions_sha256':H.digest(fixed),
       'diagnostic_actions_sha256':H.digest(diag),'degree5_probe_anchors':list(ANCHORS),
       'five_way_activations_fixed':dict((str(m),sum((x&m)==m for x in fixed)) for m in (31,47,55,59,61,62)),
       'five_way_activations_diagnostic':dict((str(m),sum((x&m)==m for x in diag)) for m in (31,47,55,59,61,62)),
       'five_gain_vs_best_fixed_or_random_pp':improvement_pp,
       'five_strongest_original_acquisition_policy':strongest,
       'scores':scores,'other_family_noninferiority':other,'per_world':details,
       'source_receipts_sha256':H.digest(receipts),
       'cold_relabel_exact_identity':cold_counts,'cold_relabel_groundtruth':cold_scores,
       'previous_known_knowledge_unchanged':True,
       'resource':{'whole_trial_wall_s':round(time.perf_counter()-trial_wall,3),
          'whole_trial_cpu_s':round(time.process_time()-trial_cpu,3),
          'peak_tracemalloc_bytes':peak,
          'per_policy_fit_and_all_readout_cpu_s':{p:round(n/1e9,6) for p,n in fits_ns.items()},
          'energy':'NOT_MEASURED'},
       'limitations':['Public synthetic six-bit source with generic AND/XOR primitives; not original DTR/CausalGym',
         'Common 16 held public action locations are known (TRANSDUCTIVE), labels unknown',
         'All 3 policies each spend 32 public effects per world; repeated same x across arms is charged separately',
         'Same-prior independent exact symbolic always tied to hierarchical numerical',
         'Native first-use, new primitive invention, independent fully trained recurrent and energy parity not proven']}
if __name__=='__main__':
    print('WSP144_RESULT_JSON='+S.canon(run()))
