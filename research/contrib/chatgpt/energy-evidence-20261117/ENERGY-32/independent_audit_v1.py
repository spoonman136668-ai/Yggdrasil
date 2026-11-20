#!/usr/bin/env python3
"""Independent ENERGY-32 evidence reconstruction. No scorer imports.

Audits the source-side causal truths and exogenous draws and refits all six
learner readouts in scalar Python, not the scorer's NumPy matrix machinery.
"""
import argparse, hashlib, itertools, json, math
from pathlib import Path
D=Path(__file__).resolve().parent

def tag(*parts):return hashlib.sha256('/'.join(str(v) for v in ('energy32-v1',*parts)).encode('ascii')).digest()
def choose(*parts,modulus):return int.from_bytes(tag(*parts)[:8],'big')%modulus

rules=[]
for ids in itertools.combinations(range(6),3):
    for sign in (0,1):rules.append((ids,(),sign))
for ids in itertools.combinations(range(6),3):
    remain=[x for x in range(6) if x not in ids]
    for pair in itertools.combinations(remain,2):
        for sign in (0,1):rules.append((ids,pair,sign))
assert len(rules)==160

def truth(rule_id, action):
    t,p,s=rules[rule_id]
    return (sum((action>>b)&1 for b in t)&1) ^ (int(all((action>>b)&1 for b in p)) if p else 0) ^ s

prior=[7/8/40]*40 + [1/8/120]*120

def update(weights, action, outcome, hazard=0):
    if hazard:weights=[(1-hazard)*wi+hazard*pi for wi,pi in zip(weights,prior)]
    out=[wi*(.85 if truth(i,action)==outcome else .15) for i,wi in enumerate(weights)]
    z=math.fsum(out)
    return [v/z for v in out]

def estimate(w,action):return math.fsum(w[i] for i in range(160) if truth(i,action))

def train(rows):
    w=list(prior)
    for action,label in rows:w=update(w,action,label)
    return w

def public_case(seed,original,scenario):
    order=sorted(range(64), key=lambda a:tag('split',seed,original,scenario,a))
    first=order[:24]; challenger=sorted(order[24:32], key=lambda a:tag('order',seed,original,scenario,a)); held=order[32:44]
    if scenario=='stationary_null':target=original
    elif scenario=='novel_change':target=40+choose('new',seed,original,modulus=120)
    else:target=(original+2+2*choose('switch',seed,original,modulus=19))%40
    def observe(action,which,position,hidden):
        u=int.from_bytes(tag('noise',seed,original,scenario,which,position,action)[:8],'big')/2**64
        return [action,truth(hidden,action)^int(u<.15)]
    first_rows=[observe(a,'old',n,original) for n,a in enumerate(first)]
    second_rows=[observe(a,'new',2*n+j,target) for n,a in enumerate(challenger) for j in (0,1)]
    return first_rows,second_rows,held,target

def evaluate(first_rows,second_rows,scenario,held):
    initial=train(first_rows)
    arms={'no_reset':train(first_rows+second_rows),'recent16':train(second_rows)}
    arms['privileged_phase_oracle']=arms['no_reset'] if scenario=='stationary_null' else arms['recent16']
    p=list(prior)
    for a,y in first_rows+second_rows:p=update(p,a,y,1/48)
    arms['fixed_hazard']=p
    p=list(initial); alarm_single=None
    for idx,(a,y) in enumerate(second_rows):
        if alarm_single is None:
            conf=estimate(p,a)
            if (conf if y else 1-conf)<.18:
                alarm_single=idx+1
                p=train(second_rows[:idx+1]);continue
        p=update(p,a,y)
    arms['single_surprise']=p
    p=list(initial);alarm_pair=None
    for idx in range(0,len(second_rows),2):
        a,y=second_rows[idx];b,z=second_rows[idx+1];assert a==b
        if alarm_pair is None:
            q=estimate(p,a)
            if (q>=.80 and y==0 and z==0) or (q<=.20 and y==1 and z==1):
                alarm_pair=idx+2
                p=train(second_rows[:idx+2]);continue
        p=update(update(p,a,y),b,z)
    arms['paired_confirmation']=p
    return {arm:[int(estimate(w,a)>.5) for a in held] for arm,w in arms.items()},alarm_single,alarm_pair,{arm:sum(w[40:]) for arm,w in arms.items()}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('scored',nargs='?',default='scored.json');a=parser.parse_args()
    data=json.loads((D/a.scored).read_bytes());protocol=json.loads((D/'protocol.json').read_bytes())
    assert data['schema']=='yggdrasil.energy32.score.v1' and data['seeds']==([99991] if data['mode']=='smoke' else protocol['seeds'])
    n=0;checks=0;false_alarms={'paired':0,'single':0};totals={s:{arm:0 for arm in protocol['arms']} for s in protocol['scenarios']};per_seed={}
    for scored in data['cases']:
        seed=scored['seed'];old=scored['old'];scenario=scored['scenario']
        first,second,held,true_id=public_case(seed,old,scenario)
        assert scored['prefix']==first;assert scored['stream']==second;assert scored['held']==held
        assert scored['true_rule']==true_id
        assert len(set(a for a,y in first))==24 and len(set(a for a,y in second))==8 and len(set(held))==12
        assert not set(a for a,y in first).intersection(held)
        assert not set(a for a,y in second).intersection(held)
        assert not set(a for a,y in first).intersection(a for a,y in second)
        preds,single,paired,novel=evaluate(first,second,scenario,held)
        assert scored['single_alarm']==single and scored['paired_alarm']==paired
        for arm,observed in preds.items():
            assert observed==scored['predictions'][arm], (seed,old,scenario,arm)
            count=sum(v==truth(true_id,k) for k,v in zip(held,observed))
            assert count==scored['correct'][arm]
            assert abs(novel[arm]-scored['belief_novel'][arm])<1e-10
            totals[scenario][arm]+=count
            checks+=len(held)*2+1
        checks+=len(first)+len(second)+len(held)+10
        if scenario=='stationary_null':
            false_alarms['paired']+=paired is not None
            false_alarms['single']+=single is not None
        per_seed.setdefault(str(seed),{}).setdefault(scenario,{})
        for arm in preds:per_seed[str(seed)][scenario][arm]=per_seed[str(seed)][scenario].get(arm,0)+scored['correct'][arm]
        n+=1
    assert n==data['case_count']
    assert totals==data['scenario_totals']
    assert false_alarms==data['false_alarms']
    assert per_seed==data['per_seed']
    den=data['scenario_denominators'];gates={
      'new_change_vs_single':all((totals[s]['paired_confirmation']-totals[s]['single_surprise'])/den[s]>=.03 for s in ('novel_change','familiar_switch')),
      'false_alarm':false_alarms['paired']/(den['stationary_null']/12)<=.10,
      'full_bayes':all(totals[s]['paired_confirmation']>=totals[s]['fixed_hazard'] for s in protocol['scenarios']),
      'stationary_retention':totals['stationary_null']['paired_confirmation']/den['stationary_null']>=.95}
    assert gates==data['gates'];assert ('DEVELOPMENT_GO' if all(gates.values()) else 'DEVELOPMENT_NO_GO')==data['classification']
    assert data['scientific_pass'] is False and data['native_checkpoint_run'] is False and data['deployment']=='NONE'
    report={'status':'PASS','checks':checks,'cases':n,'held_prediction_crosschecks':n*12*6,'witness_source_checks':n*40,'totals':totals,'false_alarms':false_alarms,'gates':gates,'science_pass':False}
    path=D/('audit_smoke.json' if data['mode']=='smoke' else 'audit_result.json')
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
