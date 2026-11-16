"""CB7 frozen PUBLIC source actual interventions and exact expected-value audit."""
from __future__ import annotations
from hashlib import sha256
import json
import random
import statistics
import time
from public_world import SEEDS, CHANNELS, World, public_config
from policies import DirectOneStep, ExactBayesianDP, ConfirmAscending, NoProbe, RandomOrder

ARMS = ('DIRECT_GREEDY','EXACT_BAYES','FIXED_CB5','NO_PROBE','RANDOM')


def run_one(seed, hidden, name):
    env = World(seed, hidden)
    options = {'DIRECT_GREEDY':lambda:DirectOneStep(env.prior,env.costs),
               'EXACT_BAYES':lambda:ExactBayesianDP(env.prior,env.costs),
               'FIXED_CB5':lambda:ConfirmAscending(env.prior,env.costs),
               'NO_PROBE':lambda:NoProbe(env.prior,env.costs),
               'RANDOM':lambda:RandomOrder(env.prior,env.costs,seed+1900)}
    agent = options[name]()
    while (channel := agent.next_probe()) is not None:
        event = env.probe(channel)
        agent.observe(event)
    answer = agent.choose_answer()
    returned, correct = env.terminal(answer)
    return {'hidden_owner_only':hidden,'name':name,'terminal':answer,
            'net_earned':returned,'correct':int(correct),
            'paid_probe_actions':len(env.events),'paid_total_cost':env.cost,
            'public_event_receipt':agent.public_receipt()}


def one_world(seed):
    prior, costs = public_config(seed)
    rolls = {name:[run_one(seed, hidden, name) for hidden in range(CHANNELS)] for name in ARMS}
    for key in ARMS:
        for hidden, r in enumerate(rolls[key]):
            if r['hidden_owner_only'] != hidden:
                raise AssertionError('CB7_CUSTODY')
    summary = {}
    for name, traces in rolls.items():
        summary[name] = {
            'expected_net_value':sum(prior[i]*traces[i]['net_earned'] for i in range(CHANNELS)),
            'expected_paid_probe_count':sum(prior[i]*traces[i]['paid_probe_actions'] for i in range(CHANNELS)),
            'expected_paid_cost':sum(prior[i]*traces[i]['paid_total_cost'] for i in range(CHANNELS)),
            'expected_correct':sum(prior[i]*traces[i]['correct'] for i in range(CHANNELS)),
            'real_source_action_count':sum(t['paid_probe_actions'] for t in traces),
        }
    if summary['DIRECT_GREEDY']['expected_net_value'] > summary['EXACT_BAYES']['expected_net_value']+1e-10:
        raise AssertionError('CB7_BAYES_OPTIMALITY_CONTRADICTION')
    return {'seed':seed,'public_prior':prior,'public_probe_costs':costs,
            'summary':summary,'source_private_trial_receipts':rolls}


def study():
    start=time.perf_counter()
    worlds=[one_world(s) for s in SEEDS]
    keys=('expected_net_value','expected_paid_probe_count','expected_paid_cost','expected_correct','real_source_action_count')
    mean={arm:{k:statistics.mean(w['summary'][arm][k] for w in worlds) for k in keys} for arm in ARMS}
    diffs=[w['summary']['DIRECT_GREEDY']['expected_net_value']-w['summary']['EXACT_BAYES']['expected_net_value'] for w in worlds]
    rng=random.Random(82670)
    boot=sorted(statistics.mean(rng.choices(diffs,k=len(diffs))) for _ in range(1000))
    checks={
      'actual_intervention_executed_per_counterfactual':all(len(w['source_private_trial_receipts'][arm])==6 for w in worlds for arm in ARMS),
      'greedy_net_plus_0_02_over_fixed':mean['DIRECT_GREEDY']['expected_net_value']-mean['FIXED_CB5']['expected_net_value']>=.02,
      'greedy_net_plus_0_01_over_no_probe':mean['DIRECT_GREEDY']['expected_net_value']-mean['NO_PROBE']['expected_net_value']>=.01,
      'greedy_expected_regret_to_bayes_at_most_0_02':mean['EXACT_BAYES']['expected_net_value']-mean['DIRECT_GREEDY']['expected_net_value']<=.02,
      'greedy_greater_than_bayes_by_0_01':statistics.mean(diffs)>=.01,
      'paired_bootstrap_lower_gt_0':boot[24]>0,
    }
    stable=json.dumps(worlds,sort_keys=True,separators=(',',':')).encode('ascii')
    return {'schema':'yggdrasil.cb7.public-cost-probe-result.v1',
      'classification':'PUBLIC_DEV_POLICY_REGRET_OR_TIE_NO_SCIENTIFIC_ADVANTAGE',
      'source_class':'NEW_PUBLIC_SYNTHETIC_FIRST_DEV_NOW_CONSUMED',
      'worlds':32,'source_private_hypotheses_per_world':6,'arms':ARMS,
      'total_real_source_probes':sum(w['summary'][arm]['real_source_action_count'] for w in worlds for arm in ARMS),
      'mean':mean,'candidate_minus_bayes_mean':statistics.mean(diffs),
      'paired_world_bootstrap_95':[boot[24],boot[975]],
      'frozen_predicates':checks,'scientific_pass':False,'native_promotion':False,
      'source_private_scored_records_sha256':sha256(stable).hexdigest(),
      'wall_seconds':time.perf_counter()-start,'worlds_detail':worlds}


if __name__ == '__main__':
    print(json.dumps(study(),sort_keys=True,indent=2))
