"""FCR03 pre-registered source-free developer comparison, one frozen run.

Same action-consequence evidence, before-outcome forecasts, no phase sent to
learners. Strongest controls include two hazard-Bayes affine mixtures in the
identical representational class. This is not original-world science.
"""
from __future__ import annotations
import hashlib
import json
import platform
import sys
import time
from collections import deque
from statistics import mean
from pathlib import Path

from mechanism_recall import (StagewiseRecall, bit, canonical, digest, evaluate,
                              laws, CONFIDENCE_HIGH, CONFIDENCE_LOW)

SOURCE_SHA="86264b41a08d49f558418c0fba367f3a2636befa"
SEEDS=(317101,317102,317103,317104,317105,317106,317107,317108)
PHASE_LENGTHS=(("A_familiar",80),("B_changed",80),("A_return",80),
               ("C_recombination",80),("D_nonlinear_unknown",48))
ARMS=("mechanism_recall","beta_full","beta32","beta16",
      "affine_full","affine_hazard_32","affine_hazard_8")


def draw(seed,index,field):
    return hashlib.sha256(f"{seed}/{index}/{field}".encode("ascii")).digest()[0] & 1


def fixture(seed):
    phase_index=0; boundary=PHASE_LENGTHS[0][1]
    for i in range(sum(s for _,s in PHASE_LENGTHS)):
        if i>=boundary:
            phase_index+=1
            boundary+=PHASE_LENGTHS[phase_index][1]
        name=PHASE_LENGTHS[phase_index][0]
        c=draw(seed,i,'context'); x1=draw(seed,i,'x1'); x2=draw(seed,i,'x2')
        s2=x1 ^ (c if phase_index in (0,2,3,4) else 0)
        if phase_index in (0,2): y=s2^x2
        elif phase_index in (1,3): y=s2^x2^c
        else: y=(c&x1)^x2
        identifier=hashlib.sha256(f"{seed}/{i}/witness".encode()).hexdigest()
        # This name is kept ONLY by the evaluator, never passed to any arm.
        yield name,(identifier,c,x1,s2,x2,y)


class BetaHead:
    """Full or time-bounded exact input-conditional Jeffreys-Beta counts."""
    def __init__(self,depth=None):
        self.counts={}; self.depth=depth; self.window=deque()
    def forecast(self,key):
        n0,n1=self.counts.get(key,(0,0))
        return (n1+0.5)/(n0+n1+1)
    def observe(self,key,y):
        bit(y)
        cell=self.counts.setdefault(key,[0,0]);cell[y]+=1
        self.window.append((key,y))
        if self.depth is not None and len(self.window)>self.depth:
            old,old_y=self.window.popleft()
            self.counts[old][old_y]-=1


class BetaModel:
    def __init__(self,depth=None):
        self.transition=BetaHead(depth);self.reward=BetaHead(depth)
    def transition_forecast(self,c,x1):return self.transition.forecast((c,x1))
    def reward_forecast(self,c,x1,s2,x2):return self.reward.forecast((c,x1,s2,x2))
    def admit_fixture(self,identifier,c,x1,s2,x2,y):
        self.transition.observe((c,x1),s2)
        self.reward.observe((c,x1,s2,x2),y)


class AffineHead:
    """Matched hypothesis-class posterior, hazard fixed share with equal prior."""
    def __init__(self,dimension,hazard):
        self.hypotheses=laws(dimension)
        self.weights=[1/len(self.hypotheses)]*len(self.hypotheses)
        self.hazard=hazard
    def forecast(self,features):
        return sum(weight*(CONFIDENCE_HIGH if evaluate(law,features) else CONFIDENCE_LOW)
                   for weight,law in zip(self.weights,self.hypotheses))
    def observe(self,features,y):
        unnormalized=[w*(CONFIDENCE_HIGH if evaluate(law,features)==y else CONFIDENCE_LOW)
                      for w,law in zip(self.weights,self.hypotheses)]
        normalizer=sum(unnormalized)
        assert normalizer>0
        posterior=[v/normalizer for v in unnormalized]
        prior_share=self.hazard/len(self.hypotheses)
        self.weights=[(1-self.hazard)*v+prior_share for v in posterior]
        assert abs(sum(self.weights)-1)<1e-9


class AffineModel:
    def __init__(self,hazard=0):
        self.transition=AffineHead(2,hazard);self.reward=AffineHead(4,hazard)
    def transition_forecast(self,c,x1):return self.transition.forecast((c,x1))
    def reward_forecast(self,c,x1,s2,x2):return self.reward.forecast((c,x1,s2,x2))
    def admit_fixture(self,identifier,c,x1,s2,x2,y):
        self.transition.observe((c,x1),s2)
        self.reward.observe((c,x1,s2,x2),y)


def new_models():
    return {
      "mechanism_recall":StagewiseRecall(),
      "beta_full":BetaModel(),
      "beta32":BetaModel(32),
      "beta16":BetaModel(16),
      "affine_full":AffineModel(0),
      "affine_hazard_32":AffineModel(1/32),
      "affine_hazard_8":AffineModel(1/8),
    }


def single(seed):
    cases=tuple(fixture(seed))
    assert len(cases)==368
    scores={}
    for name,model in new_models().items():
        phase_errors={phase:{'transition':[],'reward':[]} for phase,_ in PHASE_LENGTHS}
        start=time.process_time()
        for phase,(identifier,c,x1,s2,x2,y) in cases:
            pt=model.transition_forecast(c,x1)
            pr=model.reward_forecast(c,x1,s2,x2)
            assert 0<=pt<=1 and 0<=pr<=1
            phase_errors[phase]['transition'].append((pt-s2)**2)
            phase_errors[phase]['reward'].append((pr-y)**2)
            # Only a witnessed public row, without phase identifier.
            model.admit_fixture(identifier,c,x1,s2,x2,y)
        cpu=time.process_time()-start
        score={phase:{k:mean(v) for k,v in pair.items()}
               for phase,pair in phase_errors.items()}
        record={'brier':score,'cpu_seconds':cpu}
        if name=='mechanism_recall':
            raw=model.checkpoint(SOURCE_SHA)
            restored=StagewiseRecall.restore(model.ledger,raw,digest(raw),SOURCE_SHA)
            assert restored.checkpoint(SOURCE_SHA)==raw
            for c in (0,1):
                for x1 in (0,1):
                    assert restored.transition_forecast(c,x1)==model.transition_forecast(c,x1)
            record['checkpoint_bytes']=len(raw)
            record['cold_replay_pass']=True
            record['stage_summary']={'transition':model.transition.summary(),
                                     'reward':model.reward.summary()}
        scores[name]=record
    return {'seed':seed,'arms':scores}


def trial():
    runs=[single(seed) for seed in SEEDS]
    means={name:{phase:{stage:mean(run['arms'][name]['brier'][phase][stage] for run in runs)
                              for stage in ('transition','reward')}
                 for phase,_ in PHASE_LENGTHS}
           for name in ARMS}
    controls=[name for name in ARMS if name!='mechanism_recall']
    c=means['mechanism_recall']
    best={phase:{stage:min(means[name][phase][stage] for name in controls)
                 for stage in ('transition','reward')}
          for phase in ('A_return','C_recombination')}
    c_pass=all(c['C_recombination'][head]<=best['C_recombination'][head]+1e-12
               for head in ('transition','reward'))
    a_pass=all(c['A_return'][head]<=best['A_return'][head]+0.02+1e-12
               for head in ('transition','reward'))
    return {
      'schema':'yggdrasil.fcr03.dev-result.v1',
      'source_free_fixture':True,'source_parent':SOURCE_SHA,
      'scientific_gain_verified':False,'accepted_native':False,
      'seed_count':len(SEEDS),'seeds':SEEDS,
      'events_per_seed':368,'total_events':368*len(SEEDS),
      'consumed_trials':1,'classification':'DEV_GO' if c_pass and a_pass else 'DEV_NO_GO',
      'c_meets_strongest_control':c_pass,'a_return_drift_within_0_02':a_pass,
      'matched_best':best,'means':means,'per_seed':runs,
      'native_cpu_ratio':'UNVERIFIED',
      'full_windows_linux_regression':'NOT_RUN',
      'science_first_use':'NOT_AUTHORIZED',
      'runtime':{'python':sys.version.split()[0],'platform':platform.platform()},
    }


if __name__=='__main__':
    print(json.dumps(trial(),indent=2,sort_keys=True))
