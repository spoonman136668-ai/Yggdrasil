"""SCDR-A/B: source-free constant-F2 sheaf obstruction and latent-state diagnosis.

On a 3-cycle graph, the constant F2 cellular sheaf has C0=F2^3,
C1=F2^3, d0(x)=(x0+x1,x1+x2,x2+x0). H1=C1/im(d0).
The cycle parity of an observed 1-cochain is the obstruction class.
This experiment cannot prove a physical hidden cause or full native learning.
"""
from __future__ import annotations
import argparse, hashlib, json, math, random, statistics
from collections import defaultdict

P_SENSOR = .10
P_SWITCH = .08
Q_DEFECT = (1-(1-2*P_SENSOR)**3)/2
LENGTH = 24
TRAIN=(300001,300161)
A=(310001,310097)
B=(320001,320097)
NULL=(330001,330097)
STOP_CONF=.95

def rng(*parts):
    h=hashlib.sha256(':'.join(map(str,parts)).encode()).digest()
    return random.Random(int.from_bytes(h[:16],'big'))

def delta(x):
    assert len(x)==3
    return (x[0]^x[1],x[1]^x[2],x[2]^x[0])

def defect(edge_cochain):
    assert len(edge_cochain)==3
    return edge_cochain[0]^edge_cochain[1]^edge_cochain[2]

def cohomology():
    image={delta((x0,x1,x2)) for x0 in (0,1) for x1 in (0,1) for x2 in (0,1)}
    C1=set((b0,b1,b2) for b0 in (0,1) for b1 in (0,1) for b2 in (0,1))
    H1={0:sorted([b for b in C1 if defect(b)==0]),1:sorted([b for b in C1 if defect(b)==1])}
    assert len(image)==4 and H1[0]==sorted(image) and len(H1[1])==4
    return {'constant_F2_stalks_vertices':3,'constant_F2_stalks_edges':3,
            'C0_cardinality':8,'C1_cardinality':8,'d0_rank':2,
            'H1_dimension':1,'coboundaries':sorted(image),
            'nontrivial_cohomology_class_representatives':H1[1]}

def sample_world(seed, cohort, null=False):
    r=rng('world',seed,cohort)
    state=int(r.random()<.5) if not null else 0
    records=[]
    for t in range(LENGTH):
        if t and not null and r.random()<P_SWITCH: state^=1
        g=[int(r.random()<.5) for _ in range(3)]
        clean=list(delta(g)); clean[2]^=state
        observed=tuple(bit^int(r.random()<P_SENSOR) for bit in clean)
        records.append((state,observed))
    return records

def train():
    # Strong supervised 2-state raw-observation HMM with *more information*
    # (state labels on training worlds). Candidate's tau uses no state labels.
    transitions=[0,0]
    symbols=[[1]*8,[1]*8] # Laplace-smoothed categorical emissions.
    for seed in range(*TRAIN):
        trajectory=sample_world(seed,'train')
        prev=None
        for state,obs in trajectory:
            symbol=(obs[0]<<2)|(obs[1]<<1)|obs[2]
            symbols[state][symbol]+=1
            if prev is not None:
                transitions[state!=prev]+=1
            prev=state
    tau_supervised=(transitions[1]+1)/(sum(transitions)+2)
    likelihoods=[[v/sum(row) for v in row] for row in symbols]
    # Unsupervised candidate estimates state-transition rate from *observed* parity
    # transitions and known independent sensor-noise calibration.
    empirical=[]
    for seed in range(*TRAIN):
        parity=[defect(obs) for _,obs in sample_world(seed,'train')]
        empirical.extend([parity[t]!=parity[t-1] for t in range(1,len(parity))])
    p_raw=sum(empirical)/len(empirical)
    mismatch=2*Q_DEFECT*(1-Q_DEFECT)
    tau_est=max(0.,min(.49,(p_raw-mismatch)/(1-2*mismatch)))
    return {'tau_supervised':tau_supervised,'tau_unsupervised':tau_est,
            'likelihoods':likelihoods,'train_worlds':TRAIN[1]-TRAIN[0],
            'calibrated_sensor_noise':P_SENSOR}

def filter_sheaf(sequence,tau,with_memory):
    p=0.5; estimates=[]
    for _,edges in sequence:
        if with_memory:p=tau+(1-2*tau)*p
        else:p=.5
        d=defect(edges)
        like1=1-Q_DEFECT if d else Q_DEFECT
        like0=Q_DEFECT if d else 1-Q_DEFECT
        p=p*like1/(p*like1+(1-p)*like0)
        estimates.append(p)
    return estimates

def filter_raw_hmm(sequence,model):
    p=.5;pred=[]
    tau=model['tau_supervised']
    for _,edges in sequence:
        p=tau+(1-2*tau)*p
        symbol=(edges[0]<<2)|(edges[1]<<1)|edges[2]
        like0=model['likelihoods'][0][symbol]
        like1=model['likelihoods'][1][symbol]
        p=p*like1/(p*like1+(1-p)*like0)
        pred.append(p)
    return pred

def filter_naive_closing(sequence):
    # Closing-edge bit alone has no information under random local gauges.
    return [0.5]*len(sequence)

def predictions(sequence,model):
    return {'SCDR_A':filter_sheaf(sequence,0.,False),
            'SCDR_B':filter_sheaf(sequence,model['tau_unsupervised'],True),
            'HMM_SUPERVISED':filter_raw_hmm(sequence,model),
            'BAYES_ORACLE':filter_sheaf(sequence,P_SWITCH,True),
            'CLOSING_ONLY':filter_naive_closing(sequence)}

def eval_one(split,model):
    seedrange={'A':A,'B':B}[split]
    names=('SCDR_A','HMM_SUPERVISED','BAYES_ORACLE','CLOSING_ONLY') if split=='A' else ('SCDR_A','SCDR_B','HMM_SUPERVISED','BAYES_ORACLE','CLOSING_ONLY')
    buckets={m:{'brier':[],'accuracy':[],'confident_fp':[],'confident_tp':[]} for m in names}
    for seed in range(*seedrange):
        trajectory=sample_world(seed,split)
        vals=predictions(trajectory,model)
        for name in names:
            for (true,_),prob in zip(trajectory,vals[name]):
                buckets[name]['brier'].append((prob-true)**2)
                buckets[name]['accuracy'].append(int((prob>=.5)==true))
                if true==0: buckets[name]['confident_fp'].append(int(prob>=STOP_CONF))
                else: buckets[name]['confident_tp'].append(int(prob>=STOP_CONF))
    # Null: same-valued gauge observations with no latent switching, not a new holdout.
    null_rates={}
    for name in names:
        fprs=[]
        for seed in range(*NULL):
            tr=sample_world(seed,'null',True)
            vals=predictions(tr,model)[name]
            fprs.extend(int(p>=STOP_CONF) for p in vals)
        null_rates[name]=sum(fprs)/len(fprs)
    metrics={}
    for name,fields in buckets.items():
        metrics[name]={k:round(sum(z)/len(z),8) if z else None for k,z in fields.items()}
        metrics[name]['null_confident_false_positive_rate']=round(null_rates[name],8)
    eligible=['HMM_SUPERVISED','BAYES_ORACLE']
    strongest=min(eligible,key=lambda name:metrics[name]['brier'])
    selected='SCDR_A' if split=='A' else 'SCDR_B'
    best=metrics[strongest]['brier']; ours=metrics[selected]['brier']
    relative_gain=(best-ours)/best
    target=relative_gain>=.05 and metrics[selected]['accuracy']>=metrics[strongest]['accuracy']-.02 and metrics[selected]['null_confident_false_positive_rate']<=.05
    return {'split':split,'worlds':seedrange[1]-seedrange[0],'frames':(seedrange[1]-seedrange[0])*LENGTH,
            'null_worlds':NULL[1]-NULL[0],'model':{'tau_unsupervised':round(model['tau_unsupervised'],8),'tau_supervised':round(model['tau_supervised'],8),
                'defect_noise':round(Q_DEFECT,8)},'metrics':metrics,
            'strongest_control':strongest,'relative_brier_gain_vs_best':round(relative_gain,8),
            'verdict':'DEVELOPMENT_SIGNAL' if target else 'DEVELOPMENT_NO_GO'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--split',choices=['A','B'],required=True)
    args=parser.parse_args()
    model=train()
    result={'schema':'ynca08.scdr.development.v1','cohomology':cohomology(),
            'results':eval_one(args.split,model),'claims':{'native_trained':False,'scientific_pass':False,'deployed':False}}
    print(json.dumps(result,sort_keys=True,indent=2))
if __name__=='__main__':main()
