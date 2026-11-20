"""NCI-NOVEL-03: source-free out-of-grammar critic and matched public controls.

No imports from Yggdrasil runtime, native owner, or Causal-Gymnasium. A completely
synthetic evaluator is defined in SourceWorld. Learners see only public inputs,
chosen actual actions, and observed outcomes. This module MUST be pinned to
GitHub before the reserved primary seeds are consumed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from collections import defaultdict
from itertools import combinations
from pathlib import Path

NOISE = 0.06
FAMILIES = (
    'novel_toggle', 'novel_guard', 'novel_parity4',
    'outside_rank2', 'outside_mux', 'outside_entangle',
    'unchanged', 'unidentifiable_x3',
)
OOD = frozenset({'outside_rank2','outside_mux','outside_entangle'})
SEEDS = (693101,693131,693157,693181)
PILOT_SEED = 693001
PHASES = {'OLD_FIT':64,'NEW_FIT':512,'CALIBRATION_PUBLIC':128,'HELD_SHARED':128,'OLD_RETURN':64}
STAGES = ('t','y')


def serial(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def hashed(*parts):
    raw='|'.join(map(str, ('nci-novel03', *parts))).encode('ascii')
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], 'big')


def signatures(n):
    """Exactly the NCI-NOVEL-02 hypothesis signatures, costs and source priors."""
    if n not in (5, 6): raise ValueError('GRAMMAR_DIMENSION')
    count=1<<n
    basis=[sum(((j>>i)&1)<<j for j in range(count)) for i in range(n)]
    universe=(1<<count)-1
    unique={}
    def add(signature,cost):
        for sig in (signature,signature^universe):
            unique[sig]=min(cost,unique.get(sig,100))
    add(0,0)
    for basis_i in basis:add(basis_i,1)
    for length in range(2,5):
        for indices in combinations(range(n),length):
            sig=0
            for i in indices:sig^=basis[i]
            add(sig,length-1)
    for i,j in combinations(range(n),2):
        for op in (basis[i]&basis[j],basis[i]|basis[j]):
            add(op,2)
            for third in range(n):
                if third not in (i,j):add(op^basis[third],3)
    return tuple(sorted(unique.items()))

TEMPLATES={n:signatures(n) for n in (5,6)}


def bitindex(features):
    if len(features) not in (5,6) or any(type(x)!=int or x not in (0,1) for x in features):
        raise ValueError('NONBINARY_PUBLIC_FEATURE')
    return sum(x<<i for i,x in enumerate(features))


def safeprob(p):
    if not math.isfinite(p) or not (0.0 < p < 1.0):raise ValueError('INVALID_PROBABILITY')
    return p


class ExactGrammarBMA:
    def __init__(self,dim):
        self.dim=dim
        self.template=TEMPLATES[dim]
        self.scores=[-0.55*cost for _,cost in self.template]
        self.observations=0

    def predict(self,features):
        ix=bitindex(features)
        if len(features)!=self.dim:raise ValueError('STAGE_DIMENSION')
        peak=max(self.scores)
        weights=[math.exp(s-peak) for s in self.scores]
        denom=sum(weights)
        positive=sum(w for w,(mask,_) in zip(weights,self.template) if mask>>ix&1)
        return safeprob(NOISE+(1-2*NOISE)*positive/denom)

    def learn(self,features,outcome):
        ix=bitindex(features)
        if type(outcome)!=int or outcome not in (0,1):raise ValueError('OUTCOME')
        ok=math.log(1-NOISE)
        miss=math.log(NOISE)
        self.scores=[s+(ok if ((mask>>ix)&1)==outcome else miss) for s,(mask,cost) in zip(self.scores,self.template)]
        self.observations+=1

    def fourth_factor_support(self):
        peak=max(self.scores)
        weights=[math.exp(s-peak) for s in self.scores]
        mass=sum(weights)
        # Variable 3 must change at least one truth-table output for this rule.
        value=0
        for weight,(mask,cost) in zip(weights,self.template):
            if any(((mask>>ix)&1)!=((mask>>(ix^(1<<3)))&1) for ix in range(1<<self.dim)):
                value+=weight
        return value/mass

    def snapshot(self):
        return {'dim':self.dim,'observations':self.observations,'scores':[v.hex() for v in self.scores]}


class FullBeta:
    def __init__(self,dim):
        self.dim=dim
        self.counts=defaultdict(lambda:[0,0])
        self.observations=0
    def predict(self,features):
        if len(features)!=self.dim:raise ValueError('STAGE_DIMENSION')
        counts=self.counts.get(tuple(features),(0,0))
        return safeprob((counts[1]+.5)/(counts[0]+counts[1]+1))
    def learn(self,features,outcome):
        if type(outcome)!=int or outcome not in (0,1):raise ValueError('OUTCOME')
        bitindex(features)
        self.counts[tuple(features)][outcome]+=1
        self.observations+=1
    def snapshot(self):
        return {'dim':self.dim,'observations':self.observations,'counts':[(list(k),list(v)) for k,v in sorted(self.counts.items())]}


class BackoffBeta:
    """Independently fitted conventional all-subsets context/count control."""
    def __init__(self,dim):
        self.dim=dim
        self.counts=defaultdict(lambda:[0,0]);self.observations=0
    def keys(self,features):
        if len(features)!=self.dim:raise ValueError('STAGE_DIMENSION')
        return [(mask,tuple(features[j] for j in range(self.dim) if mask>>j&1)) for mask in range(1<<self.dim)]
    def predict(self,features):
        scores=[]
        for mask,key in self.keys(features):
            zero,one=self.counts.get((mask,key),(0,0))
            weight=(one+zero+1)/(one+zero+4)/2**mask.bit_count()
            scores.append(((one+.5)/(one+zero+1),weight))
        return safeprob(sum(p*w for p,w in scores)/sum(w for _,w in scores))
    def learn(self,features,outcome):
        if type(outcome)!=int or outcome not in (0,1):raise ValueError('OUTCOME')
        for key in self.keys(features): self.counts[key][outcome]+=1
        self.observations+=1
    def snapshot(self):
        return {'dim':self.dim,'observations':self.observations,'cells':len(self.counts)}


class SourceWorld:
    """Evaluator ONLY. Not reachable from predictor class or its API."""
    def __init__(self,seed,family):
        if seed not in (*SEEDS,PILOT_SEED):raise ValueError('SOURCE_SEED_NOT_REGISTERED')
        if family not in FAMILIES:raise ValueError('SOURCE_FAMILY')
        self.seed,self.family=seed,family
        self.realized=[]

    def public_context(self,phase,i):
        x=tuple(hashed(self.seed,self.family,phase,i,'context',k)&1 for k in range(4))
        if self.family=='unidentifiable_x3' and phase not in ('OLD_FIT','OLD_RETURN'):
            return x[:3]+(0,)
        return x

    def action(self,phase,i,stage):
        return hashed(self.seed,self.family,phase,i,stage,'chosen_action')&1

    def _truth(self,phase,x,a1,s2=None,a2=None):
        x0,x1,x2,x3=x
        if phase in ('OLD_FIT','OLD_RETURN') or self.family in ('unchanged',):
            return (x0^a1) if s2 is None else (x1^s2^a2)
        if self.family=='unidentifiable_x3':
            return (x0^x3^a1) if s2 is None else (x1^x3^s2^a2)
        if self.family=='novel_toggle':
            return (x3^a1) if s2 is None else (x3^s2^a2)
        if self.family=='novel_guard':
            return (x0^(x3&a1)) if s2 is None else ((x3&s2)^a2)
        if self.family=='novel_parity4':
            return (x3^x0^x1^a1) if s2 is None else (x3^x1^s2^a2)
        if self.family=='outside_rank2':
            return ((x3&x0)^(x1&a1)) if s2 is None else ((x3&s2)^(x2&a2))
        if self.family=='outside_mux':
            return (((x3&x0)|((1-x3)&x1))^a1) if s2 is None else (((x3&s2)|((1-x3)&x2))^a2)
        if self.family=='outside_entangle':
            return ((x3^x0)&(x2^a1)) if s2 is None else ((x3^s2)&(x1^a2))
        raise AssertionError('unrecognized family')

    def reveal(self,phase,i,a1,a2):
        """Returns source-public episode after BOTH actually chosen interventions."""
        if phase not in PHASES or not 0<=i<PHASES[phase]:raise ValueError('PHASE_OR_INDEX')
        if a1 not in (0,1) or a2 not in (0,1):raise ValueError('ACTION_RANGE')
        x=self.public_context(phase,i)
        t=self._truth(phase,x,a1)
        y=self._truth(phase,x,a1,t,a2)
        # Stage-one response must be independent of the FUTURE stage-two action.
        f1=hashed(self.seed,self.family,phase,i,'public-noise-t',a1)%10000<600
        f2=hashed(self.seed,self.family,phase,i,'public-noise-y',a1,a2)%10000<600
        t^=int(f1)
        # Reward observes ACTUAL intermediate state, not counterfactual noiseless t.
        y=self._truth(phase,x,a1,t,a2)^int(f2)
        witness=digest(serial(['NCI-NOVEL-03',self.seed,self.family,phase,i,a1,a2]))
        self.realized.append(witness)
        return {'context':x,'a1':a1,'s2':t,'a2':a2,'y':y,'witness':witness,
                'public_factor_ids':tuple(('old' if phase in ('OLD_FIT','OLD_RETURN') else 'new')+'.x'+str(j) for j in range(4))}


def score(prob,y):
    p=safeprob(prob)
    if type(y)!=int or y not in (0,1):raise ValueError('RESULT_NONBINARY')
    return {'brier':(p-y)**2,'logloss':-(math.log(p) if y else math.log(1-p))}


def averaged(values):
    if not values:return None
    return sum(values)/len(values)


def predict_episode(models,episode):
    x,a1,s2,a2=episode['context'],episode['a1'],episode['s2'],episode['a2']
    return (models['t'].predict((*x,a1)), models['y'].predict((*x,s2,a2)))


def train(models,episode):
    x,a1,s2,a2,y=episode['context'],episode['a1'],episode['s2'],episode['a2'],episode['y']
    models['t'].learn((*x,a1),s2)
    models['y'].learn((*x,s2,a2),y)


def all_models():
    return {kind:{'t':cls(5),'y':cls(6)} for kind,cls in (
        ('BMA',ExactGrammarBMA),('FULL',FullBeta),('BACKOFF',BackoffBeta))}


def run_world(seed,family):
    world=SourceWorld(seed,family)
    old={'t':ExactGrammarBMA(5),'y':ExactGrammarBMA(6)}
    old_actions=0
    for i in range(PHASES['OLD_FIT']):
        e=world.reveal('OLD_FIT',i,world.action('OLD_FIT',i,'t'),world.action('OLD_FIT',i,'y'))
        train(old,e);old_actions+=2
    old_pin=digest(serial({name:model.snapshot() for name,model in sorted(old.items())}))
    models=all_models()
    training_actions=0
    public_x3_counts=[0,0]
    for i in range(PHASES['NEW_FIT']):
        e=world.reveal('NEW_FIT',i,world.action('NEW_FIT',i,'t'),world.action('NEW_FIT',i,'y'))
        public_x3_counts[e['context'][3]]+=1
        for model in models.values():train(model,e)
        training_actions+=2
    training_state_sha=digest(serial({k:{s:m.snapshot() for s,m in m2.items()} for k,m2 in models.items()}))
    # Holdout explicitly named CALIBRATION_PUBLIC and never fed to learner.
    evidence={kind:{'brier':[],'logloss':[]} for kind in ('BMA','FULL','BACKOFF')}
    for i in range(PHASES['CALIBRATION_PUBLIC']):
        e=world.reveal('CALIBRATION_PUBLIC',i,world.action('CALIBRATION_PUBLIC',i,'t'),world.action('CALIBRATION_PUBLIC',i,'y'))
        for kind,model in models.items():
            t,y=predict_episode(model,e)
            for prob,target in ((t,e['s2']),(y,e['y'])):
                r=score(prob,target)
                for metric in ('brier','logloss'):evidence[kind][metric].append(r[metric])
    calibration={kind:{name:averaged(v) for name,v in d.items()} for kind,d in evidence.items()}
    loss_gain=calibration['BMA']['logloss']-calibration['FULL']['logloss']
    brier_gain=calibration['BMA']['brier']-calibration['FULL']['brier']
    alarm=loss_gain>=.08 and brier_gain>=.025
    support={stage:models['BMA'][stage].fourth_factor_support() for stage in STAGES}
    if alarm:
        identity='UNKNOWN_OUTSIDE_GRAMMAR'
    elif min(public_x3_counts)==0:
        identity='UNKNOWN_NONIDENTIFIABLE_X3'
    elif min(support.values())>=.90:
        identity='PUBLIC_FACTOR_SUPPORTED_WITHIN_GRAMMAR_NOT_CERTIFIED'
    else:
        identity='UNKNOWN_OR_IRRELEVANT_X3'
    # The critic is a fixed classifier of the model class; it does not learn a new physical operator.
    out={k:[] for k in ('CRITIC','BMA','FULL','BACKOFF')}
    for i in range(PHASES['HELD_SHARED']):
        e=world.reveal('HELD_SHARED',i,world.action('HELD_SHARED',i,'t'),world.action('HELD_SHARED',i,'y'))
        pred={kind:predict_episode(model,e) for kind,model in models.items()}
        pred['CRITIC']=pred['FULL' if alarm else 'BMA']
        for kind,(t,y) in pred.items():
            out[kind].extend([score(t,e['s2'])['brier'],score(y,e['y'])['brier']])
        # Prequential: same publicly revealed intervention updates every fitted control AFTER predictions.
        for model in models.values():train(model,e)
    held={kind:averaged(values) for kind,values in out.items()}
    return_scores=[]
    for i in range(PHASES['OLD_RETURN']):
        e=world.reveal('OLD_RETURN',i,world.action('OLD_RETURN',i,'t'),world.action('OLD_RETURN',i,'y'))
        prob=predict_episode(old,e)
        return_scores.extend([score(prob[0],e['s2'])['brier'],score(prob[1],e['y'])['brier']])
    old_pin_after=digest(serial({name:model.snapshot() for name,model in sorted(old.items())}))
    if old_pin!=old_pin_after:raise AssertionError('OLD_BANK_MUTATION')
    if len(world.realized)!=sum(PHASES.values()):raise AssertionError('SOURCE_EPISODE_MISMATCH')
    return {'seed':seed,'family':family,'truth_tag':'EVALUATOR_ONLY_'+('OUTSIDE' if family in OOD else 'IN_CLASS'),
        'source_episodes':len(world.realized),'source_actions':2*len(world.realized),
        'source_witness_root':digest(serial(world.realized)),
        'old_training_actions':old_actions,'new_training_actions':training_actions,
        'calibration_evidence_only_actions':2*PHASES['CALIBRATION_PUBLIC'],
        'alarm':alarm,'relation_identity':identity,'public_x3_counts':public_x3_counts,
        'new_fourth_factor_support':support,
        'logloss_full_advantage':loss_gain,'brier_full_advantage':brier_gain,
        'calibration':calibration,'held':held,'cold_old_unchanged':old_pin==old_pin_after,
        'old_parent_sha256':old_pin,'research_new_fit_sha256':training_state_sha,
        'old_return_brier':averaged(return_scores),
        'note':'OUTSIDE truth_tag is withheld evaluator-only, not any learner input'}


def result_summary(worlds, elapsed, cpu):
    true_ood=[w for w in worlds if w['family'] in OOD]
    in_grammar=[w for w in worlds if w['family'] not in OOD]
    alarm_ood=sum(w['alarm'] for w in true_ood)
    false_alert=sum(w['alarm'] for w in in_grammar)
    critic_brier=averaged([w['held']['CRITIC'] for w in true_ood])
    bma_brier=averaged([w['held']['BMA'] for w in true_ood])
    full_brier=averaged([w['held']['FULL'] for w in true_ood])
    backoff_brier=averaged([w['held']['BACKOFF'] for w in true_ood])
    # The result keeps separate frozen representation/selection criteria.
    return {'worlds':len(worlds),'ood_worlds':len(true_ood),'known_worlds':len(in_grammar),
        'true_ood_alarms':alarm_ood,'false_ood_alarms':false_alert,
        'ood_held_brier':{'CRITIC':critic_brier,'BMA':bma_brier,'FULL':full_brier,'BACKOFF':backoff_brier},
        'old_parent_sha_stable':all(w['cold_old_unchanged'] for w in worlds),
        'mean_old_return_brier':averaged([w['old_return_brier'] for w in worlds]),
        'source_free_actions_per_arm':sum(w['source_actions'] for w in worlds),
        'wall_seconds':elapsed,'cpu_seconds':cpu,
        'alarm_gate_pass':alarm_ood>=10 and false_alert==0,
        'forecast_gate_pass':critic_brier<=min(bma_brier,full_brier)+0.015,
        'science_status':'SOURCE_FREE_DEV_ONLY_NO_INDEPENDENT_SCIENTIFIC_PASS',
        'deployment':False}


def run(seeds, families):
    wall=time.monotonic();cpu=time.process_time()
    worlds=[run_world(seed,family) for seed in seeds for family in families]
    elapsed=time.monotonic()-wall;spent=time.process_time()-cpu
    return {'schema':'nci-novel03.source-free-research-result.v1',
        'seeds':list(seeds),'families':list(families),
        'source_mode':'SELF_AUTHORED_SYNTHETIC_DEV',
        'owner_canonical_model_accessed':False,
        'worlds':worlds,'summary':result_summary(worlds,elapsed,spent)}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pilot',action='store_true')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    seed=(PILOT_SEED,) if args.pilot else SEEDS
    families=('novel_guard','outside_rank2') if args.pilot else FAMILIES
    result=run(seed,families)
    args.output.write_bytes(serial(result)+b'\n')
    print(json.dumps({**result['summary'],'pilot':args.pilot,'cohorts':result['seeds']},sort_keys=True))


if __name__=='__main__':main()
