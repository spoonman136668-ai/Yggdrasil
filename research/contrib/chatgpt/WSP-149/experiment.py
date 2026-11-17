"""WSP149 prospective public-synthetic prior-transfer experiment, owner-only scoring.

The source owner alone has truth/labels; all policies receive ONLY their
own paid 32 (x,effect) pairs and the 16 earlier FIT histories. Nothing
learned from TRANSFER or selected future query targets is fed into memory.
"""
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
from time import perf_counter_ns,process_time_ns
from hashlib import sha256
import sys,tracemalloc

import source as S
import exact_weights as W
ROOT=Path(__file__).resolve().parents[1]

def load(name,path):
    spec=spec_from_file_location(name,ROOT/path)
    mod=module_from_spec(spec);sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod

P=load('_wsp149_pinned_wsp145_selector','WSP-145/selector.py')
Z=load('_wsp149_independent_full_gf2','WSP-147/poly_control.py')
C=load('_wsp149_pinned_fully_fitted_cart','WSP-135/controls.py')
R=load('_wsp149_prior_greedy','WSP-148/repair.py')
H=P.H
F=load('_wsp149_independent_equal_prior_symbolic','WSP-143/flat_control.py')
D=load('_wsp149_pinned_three_term','WSP-142/direct_weights.py')
N=load('_wsp149_pinned_latent','WSP-135/learner.py')

POLICIES=('fixed','random','adaptive')
METHODS=('learned_prior','no_memory','permuted_memory','full_poly_symbolic',
         'fully_fitted_cart','fit_prototype','greedy_block','hierarchical',
         'equal_prior_symbolic','direct3','latent','no_update')
FAMILIES=(('fit',tuple(sorted(S.FIT))),
          ('transfer',tuple(sorted(S.NOVEL))),
          ('known',tuple(sorted(S.KNOWN))),
          ('off',tuple(sorted(S.OFF))))

def zero():return {'correct':0,'wrong_confident':0,'abstained':0,'held':0}
def plus(a,b):
    for k in a:a[k]+=b[k]
def percentage(a,key):
    return 100*a[key]/a['held'] if a['held'] else 0.0

def prototype(rows,prior_models):
    """Fully exposed 16-world no-grammar case-memory conventional control."""
    if not prior_models:return (None,)*64
    j=min(range(len(prior_models)),
          key=lambda i:(sum(prior_models[i][x]!=y for x,y in rows),i))
    return tuple(prior_models[j])

def train(rows,view,prior,prior_models):
    if len(rows)!=32 or len({x for x,y in rows})!=32:
        raise AssertionError('WSP149_BAD_CHARGED_TRAIN_SET')
    a=W.fit(rows,prior)
    b=W.fit(rows)
    c=W.fit(rows,W.mismatched_memory(prior)) if prior['frozen'] else b
    z=Z.fit(rows)
    block=R.program(rows,block_width=2)
    h=H.fit(rows)
    f=F.symbolic_fit(rows)
    if (h['level'],h['terms'],h['degree'],h['tied_count'],h['overflow'])!=(
        f['level'],f['terms'],f['degree'],f['count'],f['overflow']):
        raise AssertionError('WSP149_INDEPENDENT_HIERARCHICAL_SYMBOLIC_DRIFT')
    d=D.fit(rows);latent=N.fit(rows)
    cart=C.FullyFitCART()
    for x,y in rows:
        cart.observe(view,SimpleNamespace(law_id=view.law_id,
                      subject=view.subject(x),input=x,effect=y))
    cart.fit(view)
    if view.law_id not in cart.models or len(cart.examples[view.law_id])!=32:
        raise AssertionError('WSP149_CART_NOT_FULLY_FITTED')
    output={
        'learned_prior':W.predictions(a),
        'no_memory':W.predictions(b),
        'permuted_memory':W.predictions(c),
        'full_poly_symbolic':Z.predictions(z),
        'fully_fitted_cart':tuple(cart.infer(view,view.subject(x)) for x in range(64)),
        'fit_prototype':prototype(rows,prior_models),
        'greedy_block':R.predictions(block),
        'hierarchical':tuple(H.predict(h,x) for x in range(64)),
        'equal_prior_symbolic':tuple(F.symbolic_predict(f,x) for x in range(64)),
        'direct3':tuple(D.predict(d,x) for x in range(64)),
        'latent':tuple(N.predict(latent,x) for x in range(64)),
        'no_update':(None,)*64
    }
    if output['hierarchical']!=output['equal_prior_symbolic']:
        raise AssertionError('WSP149_FLAT_CONTROL_PARITY')
    if any(W.predict(a,x)!=y or W.predict(b,x)!=y or
           W.predict(c,x)!=y or Z.predict(z,x)!=y for x,y in rows):
        raise AssertionError('WSP149_REPRESENTATION_CAPACITY_NOT_EXACT')
    if a['rank']!=32 or b['rank']!=32 or c['rank']!=32:
        raise AssertionError('WSP149_NOT_FULL_RANK')
    return a,output,{
        'rank':a['rank'],'active_coefficients':a['active_coefficients'],
        'prior_sha256':prior['digest'],
        'learned_cpu_s':a['cpu_s'],'no_memory_cpu_s':b['cpu_s'],
        'permuted_cpu_s':c['cpu_s'],'poly_cpu_s':z['cpu_s'],
        'greedy_cpu_s':block['cpu_s'],
        'greedy_exact_fit':block['has_exact_fit'],
        'greedy_residual':block['residual_errors'],
        'prototype_count':len(prior_models)
    }

def charge_arm(view,seed,policy,prior,prior_models):
    cust=S.Custodian(view,seed)
    cpu=process_time_ns();wall=perf_counter_ns()
    rows=[]
    def query(x):
        if type(x) is not int or not 0<=x<64:
            raise PermissionError('WSP149_INVALID_CHARGED_ACTION')
        event=cust.query(view.subject(x))
        if (event.law_id,event.subject,event.input)!=(
                view.law_id,view.subject(x),x):
            raise AssertionError('WSP149_PUBLIC_SOURCE_RECEIPT_MISMATCH')
        rows.append((x,event.effect))
        return event.effect
    if policy=='fixed':
        for x in P.fixed_schedule():query(x)
    elif policy=='random':
        for x in P.random_schedule(view.law_id):query(x)
    elif policy=='adaptive':
        if P.adaptive_schedule(view.law_id,query)!=tuple(rows):
            raise AssertionError('WSP149_ADAPTIVE_ACTION_HISTORY_DRIFT')
    else:
        raise ValueError('WSP149_UNKNOWN_ACTION_POLICY')
    if len(rows)!=32 or tuple(x for x,y in rows[:20])!=P.WARM:
        raise AssertionError('WSP149_SOURCE_ACTION_BUDGET_VIOLATION')
    model,out,more=train(tuple(rows),view,prior,prior_models)
    timing={'wall_s':round((perf_counter_ns()-wall)/1e9,6),
            'cpu_s':round((process_time_ns()-cpu)/1e9,6),**more}
    return cust,tuple(rows),model,out,timing

def _world_ci(differences,draws=1024):
    """Deterministic bootstrap over independent WORLD units, never query rows."""
    if len(differences)!=32:
        raise AssertionError('WSP149_BOOTSTRAP_WORLD_UNIT_DRIFT')
    samples=[]
    for trial in range(draws):
        value=0
        for k in range(32):
            h=sha256(('WSP149|BOOTSTRAP-UNIT|'+str(trial)+'|'+str(k)).encode()).digest()
            value+=differences[int.from_bytes(h[:4],'big')%32]
        samples.append(100*value/256)
    samples.sort()
    return [samples[int(0.025*draws)],samples[int(0.975*draws)]]

def run():
    wall0=perf_counter_ns();cpu0=process_time_ns()
    tracemalloc.start()
    if (len(P.FIXED)!=32 or len(P.WARM)!=20 or
        len(S.FIT)!=16 or len(S.NOVEL)!=32 or
        len(N.templates())!=17640):
        raise AssertionError('WSP149_INHERITED_EXPERIMENT_DRIFT')
    totals={fam:{p:{m:{'paired':zero(),'arm_unseen32':zero()} for m in METHODS}
                 for p in POLICIES} for fam,seeds in FAMILIES}
    memory={p:W.empty_memory() for p in POLICIES}
    prototypes={p:[] for p in POLICIES}
    old_known={p:{} for p in POLICIES}
    costs={p:{'cpu_s':0.,'wall_s':0.,'learned_cpu_s':0.,
              'no_memory_cpu_s':0.,'permuted_cpu_s':0.,
              'poly_cpu_s':0.,'greedy_cpu_s':0.} for p in POLICIES}
    calls={p:0 for p in POLICIES}
    receipts=[];held_hash=[];worlds=[]
    exact=0;greedy_exact=0;prior_frozen_hash=None
    for fam,seeds in FAMILIES:
        for seed in seeds:
            view=S.world(seed)
            paid={};history={};state={};outputs={};times={}
            for policy in POLICIES:
                cust,rows,model,out,timing=charge_arm(
                    view,seed,policy,memory[policy],prototypes[policy])
                paid[policy]=cust
                history[policy]=rows
                state[policy]=model
                outputs[policy]=out
                times[policy]=timing
                exact+=int(timing['rank']==32)
                greedy_exact+=int(timing['greedy_exact_fit'])
                calls[policy]+=len(rows)
                costs[policy]['cpu_s']+=timing['cpu_s']
                costs[policy]['wall_s']+=timing['wall_s']
                for k in ('learned_cpu_s','no_memory_cpu_s','permuted_cpu_s',
                          'poly_cpu_s','greedy_cpu_s'):
                    costs[policy][k]+=timing[k]
                if fam=='fit' and seed in sorted(S.FIT)[:8]:
                    old_known[policy][view.law_id]={
                        'rows':rows,'model':model,'prior':memory[policy],
                        'full_output':out['learned_prior']}
            owner=S.OwnerPostCommit(view,seed,paid)
            decision=owner.score_once(outputs)
            union=set().union(*(set(x for x,y in history[p]) for p in POLICIES))
            unseen=set(range(64))-union
            corroborate=tuple(sorted(unseen,key=lambda x:(
                sha256(('WSP149|HELD|'+str(view.law_id)+'|'+str(x)).encode()).digest(),x))[:8])
            held=decision['held_queries_after_all_output_seals']
            if len(unseen)<8 or tuple(held)!=corroborate or len(held)!=8:
                raise AssertionError('WSP149_OWNER_POSTSEAL_HELD_DISAGREE')
            if decision['source_paid_events']!=96:
                raise AssertionError('WSP149_SOURCE_RECEIPT_BUDGET_MISMATCH')
            for p in POLICIES:
                for m in METHODS:
                    for scope in ('paired','arm_unseen32'):
                        plus(totals[fam][p][m][scope],
                             decision['source_private_scores'][p][m][scope])
            worlds.append({
                'family':fam,'seed':seed,
                'held_sha256':decision['held_sha256'],
                'prediction_seal_sha256':decision['prediction_seal_sha256'],
                'per_policy':{p:{
                    'action_sha256':S.digest(history[p]),
                    'coefficient_weight_sha256':S.digest(state[p]['weights']),
                    'prior_sha256':times[p]['prior_sha256'],
                    'learned_active_coefficients':times[p]['active_coefficients'],
                    'greedy_exact_fit':times[p]['greedy_exact_fit'],
                    'paired_scores':decision['source_private_scores'][p],
                    'resource':times[p]} for p in POLICIES}
            })
            receipts.append((fam,seed,decision['source_effect_receipts_sha256'],
                             decision['prediction_seal_sha256'],decision['held_sha256']))
            held_hash.append((fam,seed,decision['held_sha256']))
            if fam=='fit':
                # Only earlier fully paid FIT histories update causal prior.
                for p in POLICIES:
                    updated,check=W.remember(memory[p],history[p])
                    if check['weights']!=state[p]['weights']:
                        raise AssertionError('WSP149_PRIOR_UPDATER_DRIFT')
                    memory[p]=updated
                    prototypes[p].append(outputs[p]['learned_prior'])
                if seed==max(S.FIT):
                    for p in POLICIES:
                        memory[p]=W.freeze_memory(memory[p])
                        if len(prototypes[p])!=16:
                            raise AssertionError('WSP149_FIT_EXPOSURE_INCOMPLETE')
                    prior_frozen_hash=S.digest({p:memory[p]['digest'] for p in POLICIES})
            else:
                if any(not memory[p]['frozen'] or memory[p]['worlds']!=16 for p in POLICIES):
                    raise AssertionError('WSP149_TRANSFER_WITH_UNFROZEN_PRIOR')
                if S.digest({p:memory[p]['digest'] for p in POLICIES})!=prior_frozen_hash:
                    raise AssertionError('WSP149_POST_FIT_PRIOR_MUTATED')
    if calls!={p:2048 for p in POLICIES} or exact!=192 or len(worlds)!=64:
        raise AssertionError('WSP149_INCOMPLETE_OR_MISMATCHED_SOURCE_BUDGET')
    # Identity-only cold restore of eight prior FIT experiences per policy.
    cold={p:0 for p in POLICIES}
    cold_scores={p:zero() for p in POLICIES}
    for seed in sorted(S.TRANSFER):
        view=S.world(seed)
        for p in POLICIES:
            cust=S.Custodian(view,seed)
            if cust.budget!=0 or cust.events:
                raise AssertionError('WSP149_ZERO_EFFECT_RELABEL_CHARGED')
            rec=old_known[p][view.law_id]
            restored=W.restore_model(rec['model'],rec['rows'],rec['prior'])
            output=W.predictions(restored)
            if output!=rec['full_output']:
                raise AssertionError('WSP149_COLD_RELABEL_MEMORY_DRIFT')
            cold[p]+=sum(output[x]==rec['full_output'][x] for x in range(64))
            # Scoring is private owner readback, never an acquisition update.
            score=cust.score_once({s:output[x] for s,x in cust.held()})
            plus(cold_scores[p],{k:score[k] for k in zero()})
    if cold!={p:512 for p in POLICIES}:
        raise AssertionError('WSP149_COLD_RESTORE_INCOMPLETE')
    fam='transfer'
    cand=totals[fam]['adaptive']['learned_prior']['paired']
    strong={k:totals[fam]['adaptive'][k]['paired'] for k in (
        'no_memory','full_poly_symbolic','fully_fitted_cart')}
    best=max(strong,key=lambda k:(strong[k]['correct'],k))
    base=strong[best]
    gain=100*(cand['correct']-base['correct'])/256
    nm_gain=100*(cand['correct']-strong['no_memory']['correct'])/256
    perm=totals[fam]['adaptive']['permuted_memory']['paired']
    perm_gain=100*(cand['correct']-perm['correct'])/256
    prior_cpu=costs['adaptive']['learned_cpu_s']
    no_prior_cpu=costs['adaptive']['no_memory_cpu_s']
    cost_ratio=prior_cpu/no_prior_cpu if no_prior_cpu>0 else float('inf')
    known=totals['known']['adaptive']['learned_prior']['paired']
    known_best=max(totals['known']['adaptive'][p]['paired']['correct']
                   for p in ('fully_fitted_cart','full_poly_symbolic','no_memory'))
    off=totals['off']['adaptive']['learned_prior']['paired']
    diff=[]
    for w in worlds:
        if w['family']=='transfer':
            s=w['per_policy']['adaptive']['paired_scores']
            diff.append(s['learned_prior']['paired']['correct']-
                        s[best]['paired']['correct'])
    ci=_world_ci(diff)
    eligible=(exact==192 and cand['correct']>=160 and gain>=3
        and nm_gain>=5 and perm_gain>=5 and percentage(cand,'wrong_confident')<=1
        and 100*(known_best-known['correct'])/64<=5
        and percentage(off,'wrong_confident')<=2
        and cost_ratio<=3 and all(v==512 for v in cold.values()))
    _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    return {
        'schema':'wsp149.exact-gf2-coefficient-memory-transfer-development-result.v1',
        'status':('DEVELOPMENT_EXACT_WEIGHT_MEMORY_TRANSFER_SUPPORTED' if eligible
                  else 'DEVELOPMENT_EXACT_WEIGHT_MEMORY_TRANSFER_NO_GO'),
        'scientific_pass':False,'native_admission':False,
        'source_safe_charged_public_effects':sum(calls.values()),
        'protected_original_effects':0,
        'per_policy_charged_source_effects':calls,
        'cohorts':{k:len(seeds) for k,seeds in FAMILIES},
        'all_policies_budget_32':True,
        'all_64_predictions_committed_before_any_held_selection':True,
        'postseal_queryblind_held_per_world':8,
        'all_exact_fits_32_effects':exact,
        'greedy_exact_fits':greedy_exact,
        'prior_memory_frozen_receipt_sha256':prior_frozen_hash,
        'fit_experience_count_each_arm':{p:memory[p]['worlds'] for p in POLICIES},
        'cold_relabel_512':cold,
        'cold_relabel_scores':cold_scores,
        'transfer_model_correct':cand['correct'],
        'transfer_model_wrong_confident':cand['wrong_confident'],
        'transfer_strongest_same_arm_control':best,
        'transfer_gain_pp_vs_best':gain,
        'transfer_gain_pp_vs_no_memory':nm_gain,
        'transfer_gain_pp_vs_permuted_memory':perm_gain,
        'world_bootstrap_95_percent_pp':ci,
        'trained_model_cpu_ratio_vs_no_memory':round(cost_ratio,6),
        'source_owner_receipts_sha256':S.digest(receipts),
        'postseal_held_receipts_sha256':S.digest(held_hash),
        'scores':totals,
        'per_world':worlds,
        'resource':{
            'wall_s':round((perf_counter_ns()-wall0)/1e9,3),
            'cpu_s':round((process_time_ns()-cpu0)/1e9,3),
            'peak_tracemalloc_bytes':peak,
            'by_policy':{p:{k:round(v,6) for k,v in costs[p].items()}
                         for p in POLICIES},
            'energy':'NOT_MEASURED'
        },
        'limitations':[
            'Only public synthetic held world transfer across designer-generated novel nested conditional composition; not unknown physics or causal intervention discovery',
            'The 16 FIT worlds teach coefficient frequency, not source truth or full causal law structures',
            'Exact interpolation of 32 observations is guaranteed by GF2 feature rank, and does not establish future accuracy',
            'Numerical weight updates are equivalent to symbolic Gaussian elimination; no numerical-only intelligence claim',
            'Each eight within-world queries is correlated; independent TRANSFER world is bootstrap unit',
            'Fully fitted CART, source-exposed FIT prototypes and independent symbolic baselines are compared on matched own policy action receipts',
            'Unknown grammar judged on 32 independent novel laws but all public six-bit factors supplied',
            'End-to-end CPU/wall measured, energy/GPU/native model transfer unmeasured',
            'No protected original source first-use, merge, accepted main or native Yggdrasil promotion'
        ]
    }

if __name__=='__main__':
    print('WSP149_RESULT_JSON='+S.canon(run()))
