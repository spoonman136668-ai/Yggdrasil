"""WSP146: frozen query-blind, source-feedback-conditioned causal acquisition.

The original source owner remains the only truth reader and post-seal evaluator.
Candidate and conventional learners receive exactly their arm's 32 paid public
action/consequence pairs and return 64 predictions before any held x is chosen.
"""
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
from time import perf_counter_ns,process_time_ns
import sys,tracemalloc

import source as S
import challenge as Q

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    sp=spec_from_file_location(name,ROOT/path)
    m=module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m)
    return m
P=load('_wsp146_pinned_wsp145_acq','WSP-145/selector.py')
H=P.H
F=load('_wsp146_independent_exact_symbolic','WSP-143/flat_control.py')
D=load('_wsp146_pinned_three_term_direct','WSP-142/direct_weights.py')
N=load('_wsp146_pinned_native_style_latent','WSP-135/learner.py')
C=load('_wsp146_pinned_fully_fitted_cart','WSP-135/controls.py')

POLICIES=('fixed','random','adaptive')
METHODS=('hierarchical','equal_prior_symbolic','original_3term',
         'original_latent','fully_fitted_cart','no_update','challenged','depth_only')
FAMILIES=(('known',tuple(sorted(S.KNOWN))),
          ('three',tuple(sorted(S.UNFAMILIAR))),
          ('five',tuple(sorted(S.SWITCH))),
          ('cross',tuple(sorted(S.CROSS))),
          ('off',tuple(sorted(S.OFF))))
def zero():
    return {'correct':0,'wrong_confident':0,'abstained':0,'held':0}
def accumulate(a,b):
    for k in a:a[k]+=b[k]
def percent(v,k):
    return 100*v[k]/v['held'] if v['held'] else 0.0

def train_from_paid(rows,view):
    if len(rows)!=32 or len(set(x for x,y in rows))!=32:
        raise AssertionError('WSP146_UNQUALIFIED_TRAIN_ROWS')
    t0=process_time_ns()
    model=H.fit(rows)
    raw_all=tuple(H.predict(model,x) for x in range(64))
    raw_cpu_s=round((process_time_ns()-t0)/1e9,6)
    symbolic=F.symbolic_fit(rows)
    if (model['level'],model['terms'],model['degree'],
        model['tied_count'],model['overflow'])!=(
        symbolic['level'],symbolic['terms'],symbolic['degree'],
        symbolic['count'],symbolic['overflow']):
        raise AssertionError('WSP146_INDEPENDENT_SYMBOLIC_STRUCTURE_MISMATCH')
    direct=D.fit(rows)
    latent=N.fit(rows)
    cart=C.FullyFitCART()
    for x,y in rows:
        cart.observe(view,SimpleNamespace(law_id=view.law_id,
                              subject=view.subject(x),input=x,effect=y))
    cart.fit(view)
    if view.law_id not in cart.models or len(cart.examples[view.law_id])!=32:
        raise AssertionError('WSP146_CONVENTIONAL_NOT_FULLY_FITTED')
    out={m:[] for m in METHODS}
    for x in range(64):
        a=H.predict(model,x)
        b=F.symbolic_predict(symbolic,x)
        if a!=b:
            raise AssertionError(('WSP146_SYMB_PARITY',view.law_id,x))
        out['hierarchical'].append(a)
        out['equal_prior_symbolic'].append(b)
        out['original_3term'].append(D.predict(direct,x))
        out['original_latent'].append(N.predict(latent,x))
        out['fully_fitted_cart'].append(cart.infer(view,view.subject(x)))
        out['no_update'].append(None)
    risk=Q.measured_challenge(rows)
    if risk['original']!=raw_all or tuple(out['hierarchical'])!=raw_all:
        raise AssertionError('WSP146_ORIGINAL_HIERARCHICAL_DRIFT')
    out['challenged']=list(risk['challenged'])
    out['depth_only']=list(risk['depth_only'])
    return model,{key:tuple(v) for key,v in out.items()},dict(
        raw_cpu_s=raw_cpu_s,challenge_cpu_s=risk['cpu_s'],
        challenge_wall_s=risk['wall_s'],counterhypotheses=risk['alternatives'],
        challenge_overflow=risk['overflow'])

def charge_arm(view,seed,name):
    cust=S.Custodian(view,seed)
    t0=perf_counter_ns();c0=process_time_ns()
    rows=[]
    def charge(x):
        if type(x) is not int or not 0<=x<64:
            raise PermissionError('WSP146_INVALID_TYPED_INTERVENTION')
        event=cust.query(view.subject(x))
        if (event.law_id,event.input,event.subject)!=(
                view.law_id,x,view.subject(x)):
            raise AssertionError('WSP146_INVALID_SOURCE_PUBLIC_RECEIPT')
        rows.append((x,event.effect))
        return event.effect
    if name=='fixed': actions=P.fixed_schedule()
    elif name=='random': actions=P.random_schedule(view.law_id)
    elif name=='adaptive': actions=None
    else:raise ValueError('WSP146_UNKNOWN_POLICY')
    if actions is None:
        active=P.adaptive_schedule(view.law_id,charge)
        if active!=tuple(rows):
            raise AssertionError('WSP146_ADAPTIVE_ACTION_HISTORY_DRIFT')
    else:
        for x in actions:charge(x)
    if len(rows)!=32 or tuple(x for x,y in rows[:20])!=P.WARM:
        raise AssertionError('WSP146_SOURCE_CHARGE_BUDGET_OR_WARM_DRIFT')
    model,output,risk=train_from_paid(tuple(rows),view)
    elapsed={'wall_s':round((perf_counter_ns()-t0)/1e9,6),
             'cpu_s':round((process_time_ns()-c0)/1e9,6)}
    elapsed.update(risk)
    return cust,tuple(rows),model,output,elapsed

def run():
    start_wall=perf_counter_ns();start_cpu=process_time_ns()
    tracemalloc.start()
    if (len(P.FIXED)!=32 or P.WARM!=P.FIXED[:20]
        or len(P.MASKS)!=63 or len(N.templates())!=17640
        or len(D.FEATURES)!=63):
        raise AssertionError('WSP146_INHERITED_MODEL_DRIFT')
    data={f:{p:{m:{'paired':zero(),'arm_unseen32':zero()}
                 for m in METHODS}
             for p in POLICIES} for f,seeds in FAMILIES}
    per_world=[]
    witnesses=[]
    known={p:{} for p in POLICIES}
    costs={p:{'cpu_s':0.0,'wall_s':0.0,'raw_cpu_s':0.0,
              'challenge_cpu_s':0.0,'challenge_wall_s':0.0} for p in POLICIES}
    events={p:0 for p in POLICIES}
    withheld_sha=[]
    for family,seeds in FAMILIES:
        for seed in seeds:
            view=S.world(seed)
            paid={};rows_by={};states={};predictions={};trial_timing={}
            for policy in POLICIES:
                c,rows,model,output,timing=charge_arm(view,seed,policy)
                paid[policy]=c
                rows_by[policy]=rows
                states[policy]=model
                predictions[policy]=output
                trial_timing[policy]=timing
                costs[policy]['cpu_s']+=timing['cpu_s']
                costs[policy]['wall_s']+=timing['wall_s']
                for extra in ('raw_cpu_s','challenge_cpu_s','challenge_wall_s'):
                    costs[policy][extra]+=timing[extra]
                events[policy]+=len(rows)
                if family=='known':
                    known[policy][view.law_id]={'rows':rows,'state':model,
                        'outputs':output['hierarchical'],
                        'risk_outputs':output['challenged']}
            # No selector/learner is called after the owner receives all
            # fully frozen 64-state output vectors for all arms/controls.
            owner=S.OwnerPostCommit(view,seed,paid)
            decision=owner.score_once(predictions)
            held=decision['held_queries_after_all_output_seals']
            corroborate=P.hidden_future_questions(view.law_id,
                {p:tuple(x for x,y in rows_by[p]) for p in POLICIES},
                {p:{x:predictions[p]['hierarchical'][x] for x in range(64)}
                 for p in POLICIES})
            if tuple(held)!=tuple(corroborate) or len(held)!=8:
                raise AssertionError('WSP146_OWNER_POSTSEAL_QUERIES_DISAGREE')
            if decision['source_paid_events']!=96:
                raise AssertionError('WSP146_BAD_PER_WORLD_ACTION_BUDGET')
            withheld_sha.append([family,seed,decision['held_sha256'],
                                  decision['prediction_seal_sha256']])
            for p in POLICIES:
                for m in METHODS:
                    for split in ('paired','arm_unseen32'):
                        accumulate(data[family][p][m][split],
                                   decision['source_private_scores'][p][m][split])
            per_world.append({'family':family,'seed':seed,
                'common_held_sha256':decision['held_sha256'],
                'prediction_seal_sha256':decision['prediction_seal_sha256'],
                'disjoint_unseen_count':len(set(range(64))-
                    set().union(*(set(x for x,y in rows_by[p]) for p in POLICIES))),
                'per_policy':{p:{
                    'action_history_sha256':S.digest(rows_by[p]),
                    'state_sha256':H.digest(states[p]),
                    'level':states[p]['level'],
                    'tied':states[p]['tied_count'],
                    'paired_scores':decision['source_private_scores'][p],
                    'elapsed':trial_timing[p]
                    } for p in POLICIES}})
            witnesses.append([family,seed,
                decision['source_effect_receipts_sha256'],
                decision['prediction_seal_sha256'],decision['held_sha256']])
    if (events!={p:2048 for p in POLICIES}
        or len(per_world)!=64):
        raise AssertionError('WSP146_UNAUTHORIZED_OR_INCOMPLETE_PUBLIC_SOURCE')
    # All worlds learned; prove old paid facts still replay bit-for-bit.
    for p in POLICIES:
        for law,rec in known[p].items():
            after=H.restore(H.canon(rec['state']),rec['rows'])
            if any(H.predict(after,x)!=rec['outputs'][x] for x in range(64)):
                raise AssertionError('WSP146_OLD_WORLD_INTERFERENCE')
    cold={p:0 for p in POLICIES}
    cold_scores={p:zero() for p in POLICIES}
    for seed in sorted(S.TRANSFER):
        view=S.world(seed)
        for p in POLICIES:
            cust=S.Custodian(view,seed)
            if cust.budget!=0 or cust.events:
                raise AssertionError('WSP146_RELABELED_SOURCE_CHARGED')
            old=known[p][view.law_id]
            restored=H.restore(H.canon(old['state']),old['rows'])
            output=tuple(H.predict(restored,x) for x in range(64))
            risk=Q.challenge(old['rows'],restored)
            if risk['challenged']!=old['risk_outputs']:
                raise AssertionError('WSP146_COLD_RISK_CONSISTENCY_FAIL')
            cold[p]+=sum(output[x]==old['outputs'][x] for x in range(64))
            # Owner-only cold scoring, not candidate feedback.
            outcome=cust.score_once({s:output[x] for s,x in cust.held()})
            accumulate(cold_scores[p],{k:outcome[k] for k in zero()})
    if cold!={p:512 for p in POLICIES}:
        raise AssertionError('WSP146_COLD_KNOWLEDGE_IDENTITY_FAIL')
    five_raw={p:data['five'][p]['hierarchical']['paired'] for p in POLICIES}
    five_risk=data['five']['adaptive']['challenged']['paired']
    five_depth=data['five']['adaptive']['depth_only']['paired']
    best=max(('fixed','random'),key=lambda p:(five_raw[p]['correct'],p))
    raw_loss=100*(five_raw['adaptive']['correct']-five_risk['correct'])/256
    best_loss=100*(five_raw[best]['correct']-five_risk['correct'])/256
    error_reduction=five_raw['adaptive']['wrong_confident']-five_risk['wrong_confident']
    cpu_baseline=sum(costs[p]['raw_cpu_s'] for p in POLICIES)
    cpu_challenge=sum(costs[p]['challenge_cpu_s'] for p in POLICIES)
    cpu_ratio=cpu_challenge/cpu_baseline if cpu_baseline else float('inf')
    others={f:{'challenged':data[f]['adaptive']['challenged']['paired'],
               'best_baseline_correct':max(data[f][p]['hierarchical']['paired']['correct']
                   for p in ('fixed','random'))}
            for f in ('known','three','cross')}
    eligible=(percent(five_risk,'wrong_confident')<=1 and raw_loss<=2.5 and best_loss<=5
        and five_risk['correct']>five_depth['correct'] and error_reduction>0
        and cpu_ratio<=3
        and all(100*(v['best_baseline_correct']-v['challenged']['correct'])
                /v['challenged']['held']<=5
            and percent(v['challenged'],'wrong_confident')<=1
            for v in others.values())
        and percent(data['off']['adaptive']['challenged']['paired'],'wrong_confident')<=2)
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        'schema':'wsp146.outcome-adaptive-queryblind-causal-development-result.v1',
        'status':'DEVELOPMENT_SHALLOW_CHALLENGE_CONFIDENCE_SUPPORTED' if eligible
                  else 'DEVELOPMENT_SHALLOW_CHALLENGE_CONFIDENCE_NO_GO',
        'scientific_pass':False,'native_admission':False,
        'source_safe_charged_public_effects':sum(events.values()),
        'protected_original_effects':0,
        'per_policy_charged_source_effects':events,
        'cohorts':{f:len(seeds) for f,seeds in FAMILIES},
        'all_64_predictions_committed_before_any_held_selection':True,
        'actual_queryblind_unseen_questions_per_world':8,
        'equal_prior_independent_flat_symbolic_tie_all':True,
        'all_policies_budget_32':True,
        'exact_cold_old_law_retention':cold,
        'cold_relabel_truth_scores':cold_scores,
        'scores':data,
        'five_challenged_correct_loss_vs_raw_adaptive_pp':raw_loss,
        'five_challenged_correct_loss_vs_best_fixed_or_random_pp':best_loss,
        'five_original_minus_challenged_confident_errors':error_reduction,
        'five_original_adaptive_wrong_confident_pct':percent(five_raw['adaptive'],'wrong_confident'),
        'five_challenged_wrong_confident_pct':percent(five_risk,'wrong_confident'),
        'five_strongest_acquisition_baseline':best,
        'challenge_to_original_fit_readout_cpu_ratio':round(cpu_ratio,6),
        'other_family_noninferiority':others,
        'source_owner_receipts_sha256':S.digest(witnesses),
        'private_future_selection_sha256':S.digest(withheld_sha),
        'per_world':per_world,
        'resource':{'total_wall_s':round((perf_counter_ns()-start_wall)/1e9,3),
            'total_cpu_s':round((process_time_ns()-start_cpu)/1e9,3),
            'peak_tracemalloc_bytes':peak,
            'per_policy_acquisition_plus_full_fit_and_readout':{
                p:{k:round(v,6) for k,v in costs[p].items()}
                for p in POLICIES},
            'energy':'NOT_MEASURED'},
        'limitations':[
          'Public synthetic fixed AND/XOR class; no newly invented primitive',
          'Hidden x selected after prediction seals from action-disjoint union, but selection depends on policy acquisition',
          'Each within-law eight held queries is correlated, worlds/seeds are primary units',
          'Independent equally informed full symbolic control ties every numerical prediction',
          'Fully fitted CART is conventional only, not independent fully trained recurrent comparator',
          'No original CausalGym/DTR/MDP source first-use or native model promotion',
          'CPU and tracked allocations measured; RSS, GPU energy and true original scientific improvement unverified'
        ]
    }

if __name__=='__main__':
    print('WSP146_RESULT_JSON='+S.canon(run()))
