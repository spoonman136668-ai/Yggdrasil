#!/usr/bin/env python3
"""ENERGY-33 postscore outcome audit; does not import experimental implementation.
Reaggregates all case receipts, freezes lineage and checks decision logic.
Does not independently reconstruct each causal posterior or certify science.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys

ARMS = ('cp_energy','cp_bayes','fixed_hazard','recent16','full_history')
SCENARIOS = ('stationary','novel_change','familiar_switch')
SEEDS = (6067,6073,6089,6101)
SOURCE_SHA='c9cd0ebcd1ef2d0e9c85c8ea481bd4b5bf5a90e3f4eb876dfc1c9bb90d0c4ce3'

def audit(source):
    b=Path(source).read_bytes(); x=json.loads(b)
    checks=0
    def ok(p,what):
        nonlocal checks
        checks+=1
        if not p:raise AssertionError(what)
    ok(x['mode']=='primary','mode')
    ok(x['source_sha256']==SOURCE_SHA,'source hash')
    ok(x['schema']=='yggdrasil.energy33.score.v1','schema')
    ok(x['seeds']==list(SEEDS),'seeds')
    ok(x['cases']==240==len(x['details']),'total worlds')
    ok(x['held_per_world']==12,'held count')
    ok(x['observations_per_world']==40,'observed count')
    seen=set();totals={s:{a:0 for a in ARMS} for s in SCENARIOS}
    false=0; maxparity=0.0
    for c in x['details']:
        key=(c['seed'],c['old'],c['scenario'])
        ok(c['seed'] in SEEDS,'seed identity')
        ok(c['old'] in range(0,40,2),'old law identity')
        ok(c['scenario'] in SCENARIOS,'scenario identity')
        ok(key not in seen,'duplicate case'); seen.add(key)
        ok(c['target_family']==('novel' if c['scenario']=='novel_change' else 'familiar'),'target family')
        ok(0<=c['alarm']<=1,'alarm probability')
        ok(0<=c['parity_error']<=1e-10,'posterior parity')
        maxparity=max(maxparity,c['parity_error'])
        for a in ARMS:
            n=c['correct'][a]
            ok(type(n) is int and 0<=n<=12,'case correct count')
            totals[c['scenario']][a]+=n
        ok(c['correct']['cp_energy']==c['correct']['cp_bayes'],'matched Bayesian predictions')
        if c['scenario']=='stationary':false+=int(c['alarm']>.5)
    expected={(s,o,c) for s in SEEDS for o in range(0,40,2) for c in SCENARIOS}
    ok(seen==expected,'complete population')
    ok(totals==x['scenario_totals'],'aggregate score')
    ok(all(x['scenario_denominators'][s]==960 for s in SCENARIOS),'denominators')
    ok(false==x['false_alarms'] and x['false_alarm_worlds']==80,'false alarms')
    ok(abs(maxparity-x['max_parity_error']) < 1e-18,'parity error aggregate')
    g=x['gates']; denom=x['scenario_denominators']
    checkg={
      'novel_gain_over_strongest': (totals['novel_change']['cp_energy']-max(totals['novel_change'][a] for a in ARMS[2:]))/960>=.03,
      'familiar_gain_over_strongest': (totals['familiar_switch']['cp_energy']-max(totals['familiar_switch'][a] for a in ARMS[2:]))/960>=.03,
      'stationary_retention': totals['stationary']['cp_energy']/960>=.95 and totals['stationary']['cp_energy']>=totals['stationary']['full_history']-.01*960,
      'false_alarm_at_most_10pct': false/80<=.10,
      'exact_energy_bayes_parity':maxparity<=1e-10,
      'energy_distinctive':False,
    }
    ok(g==checkg,'frozen gates')
    ok(x['classification']=='DEVELOPMENT_NO_GO' if not all(checkg.values()) else x['classification']=='DEVELOPMENT_GO','classification')
    ok(x['scientific_pass'] is False and x['native_checkpoint_run'] is False and x['deployment']=='NONE','authority boundary')
    return {'audit':'PASS','checks':checks,'results_sha256':sha256(b).hexdigest(),'case_count':len(seen),
            'scenario_totals':totals,'false_alarms':false,'gates':g,
            'boundary':'Outcome reaggregation only; not an independent posterior reconstruction or native acceptance.'}

if __name__=='__main__':
    report=audit(sys.argv[1] if len(sys.argv)>1 else 'scored.json')
    Path('audit_result.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='scenario_totals'},indent=2,sort_keys=True))
