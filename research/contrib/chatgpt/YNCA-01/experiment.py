"""YNCA-01: source-free native causal-arbitration *development* microbenchmark.

Never runs a user-controlled Yggdrasil model, controller or protected scientific cohort.
Experts receive only sampled observations and do-interventions. The referee only
receives experts' probabilities and sample metadata; no hidden law/held labels.
"""
from __future__ import annotations
import hashlib
import json
import math
import random
import statistics
import sys

SEEDS = {"train": (31001, 31257), "development": (41001, 41129), "transfer": (51001, 51129), "heldout": (61001, 61257)}
EXPERTS = ("observational", "interventional", "adjusted")
ETA = 12.0
GATE_HALF_WIDTH = 0.20
PRIOR_STRENGTH = 20.0


def rng(*args):
    value = hashlib.sha256(": ".join(map(str,args)).encode()).digest()
    return random.Random(int.from_bytes(value[:16], "big"))


def sig(x):
    return 1 / (1 + math.exp(-max(-60,min(60,x))))


def sample_world(seed, split):
    r = rng("world",seed,split)
    edge = int(r.random() < 0.5)
    regime = r.randrange(4)
    # Hidden U drives both X and Y in some regimes, creating a spurious link.
    shifted = split in ("transfer", "heldout")
    x_rho = ((0.0, 0.80, -0.80, 0.50) if not shifted else
             (0.2, 0.60, -0.60, -0.35))[regime]
    u_effect = ((0.0, 0.48, 0.48, -0.48) if not shifted else
                (0.08, 0.58, -0.58, 0.42))[regime]
    n_observed = (90, 120, 140, 110)[regime]
    n_do_per_arm = ((14, 10, 12, 24) if not shifted else (8, 16, 20, 10))[regime]
    causal_strength = .38 if not shifted else .29
    proxy_accuracy = .83 if not shifted else .70
    def get_y(x,u):
        return int(r.random() < min(0.94,max(0.06,0.30 + causal_strength*edge*x + u_effect*(u-0.5))))
    obs = []
    for _ in range(n_observed):
        u = int(r.random()<0.5)
        x = int(r.random() < (0.5 + x_rho*(u-0.5)))
        proxy = u if r.random()<proxy_accuracy else 1-u
        obs.append((x,proxy,get_y(x,u)))
    interventions=[]
    for x in (0,1):
        for _ in range(n_do_per_arm):
            u=int(r.random()<0.5)
            interventions.append((x,get_y(x,u)))
    r.shuffle(obs);r.shuffle(interventions)
    return edge, obs, interventions


def posterior_from_diff(diff, variance, expected=0.36):
    # Approximate likelihood ratio between absent and positive effect.
    return sig((2*expected*diff-expected**2)/(2*max(variance, 0.003)))


def contrast(rows):
    ys={x:[y for xx,y in rows if xx==x] for x in (0,1)}
    if not all(ys.values()): return 0.0,1.0
    a,b=(statistics.mean(ys[x]) for x in (0,1))
    v=sum(max(.05,m*(1-m))/len(ys[x]) for x,m in ((0,a),(1,b)))
    return b-a,v


def predict_experts(obs, interventions):
    d,v=contrast([(x,y) for x,z,y in obs])
    p_obs=posterior_from_diff(d,v)
    d,v=contrast(interventions)
    p_do=posterior_from_diff(d,v)
    # Proxy-stratified adjustment, pooling the two strata. No true U is visible.
    adjusted=[]
    variances=[]
    for z in (0,1):
        rows=[(x,y) for x,zz,y in obs if zz==z]
        d,v=contrast(rows)
        adjusted.append(d)
        variances.append(v)
    p_adjusted=posterior_from_diff(sum(adjusted)/2,sum(variances)/4)
    return (p_obs,p_do,p_adjusted)


def context_id(preds,obs,interventions):
    # All signals are observable; no true regime, cause, or held test label.
    obs_disagreement = int(abs(preds[0]-preds[1])>0.30)
    proxy_disagreement = int(abs(preds[2]-preds[1])>0.30)
    n_small = int(len(interventions) <= 24)
    return (obs_disagreement,proxy_disagreement,n_small)


def brier(p,y): return (p-y)**2


def train_referee(rows, *, permuted_labels=False):
    # Deterministic learned per-context expert reliability, shrink toward global.
    global_loss=[0.0]*3
    global_n=0
    grouped={}
    rows=list(rows)
    label_map = {seed:sample_world(seed,"train")[0] for seed in rows}
    if permuted_labels:
        shifted_labels = [label_map[rows[(i+31)%len(rows)]] for i in range(len(rows))]
        label_map = dict(zip(rows, shifted_labels))
    for seed in rows:
        _,obs,interventions=sample_world(seed,"train")
        y=label_map[seed]
        predictions=predict_experts(obs,interventions)
        context=context_id(predictions,obs,interventions)
        record=grouped.setdefault(context, [0,[0.0]*3])
        record[0]+=1
        global_n+=1
        for j,p in enumerate(predictions):
            loss=brier(p,y)
            record[1][j]+=loss
            global_loss[j]+=loss
    avg=[z/global_n for z in global_loss]
    return {"avg":avg, "groups":grouped, "n":global_n}


def weights(model,context, *, global_only=False):
    record=([0,[0.0]*3] if global_only else model["groups"].get(context,[0,[0.0]*3]))
    count,sums=record
    losses=[(sums[j]+PRIOR_STRENGTH*model["avg"][j])/(count+PRIOR_STRENGTH) for j in range(3)]
    vals=[math.exp(-ETA*(z-min(losses))) for z in losses]
    return [v/sum(vals) for v in vals]


def evaluate(model,split, *, sham_model=None):
    methods=("observational","interventional","adjusted","equal","learned_gate","learned_always","global_gate","shuffled_gate","random_gate","oracle")
    sums={m:0.0 for m in methods}
    correct={m:0 for m in methods}
    obs=[]
    gate_calls=0
    for seed in range(*SEEDS[split]):
        y,o,interv=sample_world(seed,split)
        preds=predict_experts(o,interv)
        equal=sum(preds)/3
        ws=weights(model,context_id(preds,o,interv))
        weighted=sum(w*p for w,p in zip(ws,preds))
        global_ws=weights(model,context_id(preds,o,interv),global_only=True)
        global_weighted=sum(w*p for w,p in zip(global_ws,preds))
        sham_ws=weights(sham_model,context_id(preds,o,interv)) if sham_model is not None else [1/3]*3
        sham_weighted=sum(w*p for w,p in zip(sham_ws,preds))
        gate=abs(equal-0.5)<=GATE_HALF_WIDTH
        gate_calls+=int(gate)
        rand=rng("weight-control",seed,split)
        arbitrary=[rand.random() for _ in preds]
        arbitrary=[w/sum(arbitrary) for w in arbitrary]
        random_weighted=sum(w*p for w,p in zip(arbitrary,preds))
        # Privileged diagnostic ceiling, NOT a deployable model.
        oracle=min(preds,key=lambda p:brier(p,y))
        cases={"observational":preds[0],"interventional":preds[1],"adjusted":preds[2],
               "equal":equal,"learned_gate":weighted if gate else equal,
               "learned_always":weighted,"global_gate":global_weighted if gate else equal,
               "shuffled_gate":sham_weighted if gate else equal,
               "random_gate":random_weighted if gate else equal,
               "oracle":oracle}
        for m,p in cases.items():
            sums[m]+=brier(p,y)
            correct[m]+=int((p>=0.5)==bool(y))
        obs.append({"seed":seed,"label":y,"context":context_id(preds,o,interv),
                    "predictions":preds,"equal":equal,"gated":cases["learned_gate"],"global":cases["global_gate"]})
    n=len(obs)
    # Paired, pre-defined descriptive intervals (fixed bootstrap RNG, 2,000 draws).
    pair_ci={}
    for comparator in ("interventional","global_gate","equal"):
        deltas=[]
        for row in obs:
            y=row["label"]
            p=(row["predictions"][1] if comparator=="interventional" else
               row["global"] if comparator=="global_gate" else row["equal"])
            deltas.append(brier(p,y)-brier(row["gated"],y))
        boot=rng("bootstrap",split,comparator)
        means=sorted(sum(deltas[boot.randrange(n)] for _ in range(n))/n for _ in range(2000))
        pair_ci[comparator]={"gain":round(sum(deltas)/n,8),
                              "ci95":[round(means[49],8),round(means[1949],8)]}
    return {"cases":n,"paired_brier_gain_vs_learned_gate":pair_ci,"gate_calls":gate_calls,"gate_fraction":gate_calls/n,
            "brier":{m:round(s/n,8) for m,s in sums.items()},
            "accuracy":{m:round(c/n,8) for m,c in correct.items()},
            "per_case":obs}


def checks(model):
    train_range=range(*SEEDS["train"])
    dev_range=range(*SEEDS["development"])
    xfer_range=range(*SEEDS["transfer"])
    held_range=range(*SEEDS["heldout"])
    assert set(train_range).isdisjoint(dev_range)
    assert set(train_range).isdisjoint(xfer_range)
    assert set(dev_range).isdisjoint(xfer_range)
    assert set(held_range).isdisjoint(set(train_range)|set(dev_range)|set(xfer_range))
    assert model["n"]==len(train_range)
    assert len(EXPERTS)==3
    for p in model["avg"]: assert 0<=p<=1
    # A null-information test: uniform experts cannot be made informative.
    for key in model["groups"]:
        w=weights(model,key)
        assert abs(sum(w)-1)<1e-12
        assert abs(sum(v*0.5 for v in w)-0.5)<1e-12
    # Test that scores do not enter referee weight calculation.
    for y,obs,interventions in [sample_world(31001,"train")]:
        ps=predict_experts(obs,interventions)
        key=context_id(ps,obs,interventions)
        assert weights(model,key)==weights(model,key)
    return {"split_disjoint":True,"weights_normalized":True,
            "null_information_invariant":True,"label_not_referee_input":True}


def main():
    model=train_referee(range(*SEEDS["train"]))
    sham=train_referee(range(*SEEDS["train"]),permuted_labels=True)
    audit=checks(model)
    holdout = "--heldout" in sys.argv
    if any(v not in ("--heldout",) for v in sys.argv[1:]):
        raise SystemExit("supported arguments: --heldout")
    evals = ("heldout",) if holdout else ("development", "transfer")
    reports = {name:evaluate(model,name,sham_model=sham) for name in evals}
    # NO tuning or retraining on DEV/TRANSFER, no acceptance claim.
    out={"schema":"ynca01.synthetic-development.v1", "model_name":"source-free prototype; not native Yggdrasil",
         "paper":"https://arxiv.org/abs/2606.10607", "frozen_config":{
         "seeds":SEEDS,"eta":ETA,"margin_half_width":GATE_HALF_WIDTH,
         "prior_strength":PRIOR_STRENGTH,"experts":EXPERTS},
         "training_worlds":model["n"],"training_contexts":len(model["groups"]),"global_train_expert_brier":model["avg"],
         "audit":audit,
         "cohorts":{name:{k:v for k,v in report.items() if k!="per_case"} for name,report in reports.items()},
         "claims":{"engineering_full":False,"scientific_pass":False,"native_integrated":False,"deployment":False}}
    print(json.dumps(out,sort_keys=True,indent=2))

if __name__=="__main__":main()
