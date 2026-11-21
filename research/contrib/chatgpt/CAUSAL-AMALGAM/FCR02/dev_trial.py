"""Frozen FCR02 engineering fixture. No original-world, source actor or new training authority."""
from __future__ import annotations

from hashlib import sha256
from statistics import mean
from time import process_time
import json

from mask_index import StageMaskIndex,Q,canonical,digest

SEEDS=(215001,215002,215003,215004)
PHASES=('A_train','B_train','C_recombined_test')
EPISODES_PER_PHASE=64
PIN='a'*64


def bit(seed,episode,field):
    return sha256(f'{seed}/{episode}/{field}'.encode('ascii')).digest()[0]&1


def fixture(seed):
    output=[]
    for i in range(3*EPISODES_PER_PHASE):
        c=bit(seed,i,'context');x1=bit(seed,i,'x1');x2=bit(seed,i,'x2')
        phase=i//EPISODES_PER_PHASE
        s2=(x1^c) if phase in (0,2) else x1
        y=s2^x2^(c if phase in (1,2) else 0)
        # Phase is NOT passed to any candidate or control.
        output.append((f'{seed*10000+i:064x}',c,x1,s2,x2,y))
    return output


class FullBeta:
    def __init__(self, pooled=False, trailing=False):
        self.pooled=pooled;self.trailing=trailing
        self.count_t={};self.count_r={};self.recent=[]

    def keys(self,c,x1,s2,x2):
        if self.pooled:return (x1,),(x2,)
        return (c,x1),(c,x1,s2,x2)

    def prob(self,cnts,key):
        failures,successes=cnts.get(key,(0,0))
        return (2*successes+1)*Q//(2*(successes+failures+1))

    def forecast_transition(self,c,x1):
        return self.prob(self.count_t,self.keys(c,x1,0,0)[0])

    def forecast_reward(self,c,x1,s2,x2):
        return self.prob(self.count_r,self.keys(c,x1,s2,x2)[1])

    def observe(self,identifier,c,x1,s2,x2,y):
        kt,kr=self.keys(c,x1,s2,x2)
        for counts,key,target in ((self.count_t,kt,s2),(self.count_r,kr,y)):
            cell=counts.setdefault(key,[0,0]);cell[target]+=1
        self.recent.append((kt,kr,s2,y))
        if self.trailing and len(self.recent)>32:
            old_kt,old_kr,old_s2,old_y=self.recent.pop(0)
            for counts,key,target in ((self.count_t,old_kt,old_s2),(self.count_r,old_kr,old_y)):
                counts[key][target]-=1


def score(model,world,mode):
    t=[];r=[];total_cpu=0.
    anchors=[]
    for i,(identifier,c,x1,s2,x2,y) in enumerate(world):
        if i==64:anchors.append((model.forecast_transition(0,0),model.forecast_reward(0,0,1,0)))
        t0=process_time()
        pt=model.forecast_transition(c,x1)
        pr=model.forecast_reward(c,x1,s2,x2)
        if mode=='candidate': model.observe_admitted_fixture(identifier,c,x1,s2,x2,y)
        else: model.observe(identifier,c,x1,s2,x2,y)
        total_cpu+=process_time()-t0
        t.append(((pt/Q-s2)**2))
        r.append(((pr/Q-y)**2))
    after=(model.forecast_transition(0,0),model.forecast_reward(0,0,1,0))
    return {'brier_t_c':mean(t[128:]),'brier_r_c':mean(r[128:]),
            'brier_t_a':mean(t[:64]),'brier_r_a':mean(r[:64]),
            'cpu_seconds':total_cpu,'anchor_probe_a64':anchors[0],
            'end_probe_a192':after}


def run():
    outcome=[]
    for seed in SEEDS:
        world=fixture(seed)
        arms={
          'mask_index':(StageMaskIndex(),'candidate'),
          'full_beta':(FullBeta(),'control'),
          'pooled_beta':(FullBeta(pooled=True),'control'),
          'trailing32_beta':(FullBeta(trailing=True),'control')}
        scored={}
        for n,(model,mode) in arms.items():
            scored[n]=score(model,world,mode)
            if n=='mask_index':
                raw=model.checkpoint(PIN)
                cold=StageMaskIndex.restore(model._ledger,raw,digest(raw),PIN)
                assert cold.checkpoint(PIN)==raw
                scored[n]['checkpoint_bytes']=len(raw)
                scored[n]['selected_mask_transition']=model.transition.masks[model.transition.choice()]
                scored[n]['selected_mask_reward']=model.reward.masks[model.reward.choice()]
        outcome.append({'seed':seed,'scores':scored})
    def avg(arm,metric):return mean(r['scores'][arm][metric] for r in outcome)
    metrics={arm:{m:round(avg(arm,m),8) for m in ('brier_t_c','brier_r_c','brier_t_a','brier_r_a','cpu_seconds')}
             for arm in ('mask_index','full_beta','pooled_beta','trailing32_beta')}
    best_t=min(metrics[c]['brier_t_c'] for c in metrics if c!='mask_index')
    best_r=min(metrics[c]['brier_r_c'] for c in metrics if c!='mask_index')
    cand=metrics['mask_index'];
    result={
      'schema':'yggdrasil.fcr02.dev-result.v1',
      'source_free_fixture':True,'scientific_gain_verified':False,
      'seeds':SEEDS,'episodes_total':len(SEEDS)*192,
      'held_c_brier_best_fitted_control_t':best_t,
      'held_c_brier_best_fitted_control_r':best_r,
      'candidate_beats_or_ties_best_t':cand['brier_t_c']<=best_t,
      'candidate_beats_or_ties_best_r':cand['brier_r_c']<=best_r,
      'metrics':metrics,
      'per_seed':outcome,
      'classification':'DEV_GO' if cand['brier_t_c']<=best_t and cand['brier_r_c']<=best_r else 'DEV_NO_GO',
      'native_cpu_ratio':'UNVERIFIED_NO_PINNED_FULL_NATIVE_EXECUTION',
      'source_authority':'NONE',
      'cross_os':'NOT_RUN', 'full_final_regression':'NOT_RUN'
    }
    return result

if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
