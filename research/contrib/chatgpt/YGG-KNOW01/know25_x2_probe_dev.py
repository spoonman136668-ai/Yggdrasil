"""KNOW25: preregistered independent synthetic x2 causal intervention proof.
Frozen before implementation: 219e59cdff6c26383fa4fb5277cad459f9caf0cf
Neither canonical Yggdrasil model nor protected original source is executed.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import time
from pathlib import Path

from anf_causal_identifiability_dev import ANF, hidden_bit, op_table

SCHEMA = "yggdrasil.know25.x2-probe-science-boundary.dev.v1"
PROTO_SCHEMA = "yggdrasil.know25.x2-intervention-identifiability-frozen-dev.v1"
PREREG = "219e59cdff6c26383fa4fb5277cad459f9caf0cf"
MODE = "engineering_fixture_only"
FIT = ((12021,"x0",24),(12029,"x1",24),(12047,"xor01",24))
PAIRS = (("x0","x0_xor_x2",(12111,12117,12121)),
         ("xor01","xor01_xor_x2",(12211,12217,12221)),
         ("and01","and01_xor_x2",(12311,12319,12327)))
FAMILIES = tuple(dict.fromkeys(op for a,b,_ in PAIRS for op in (a,b)))
FAMILY_TABLES = tuple(op_table(op) for op in FAMILIES)
POLICIES = ("trained_anf_fixed_x2", "trained_anf_no_x2",
            "untrained_anf_fixed_x2", "uniform_full_bayes_fixed_x2",
            "trained_anf_active_x2", "trained_anf_random_x2",
            "context_beta_fixed_x2", "known_family_bayes_fixed_x2",
            "uninformed_p05")
FLIPS = (0,1,2,4)
FLOOR = .15
SPAN = .70


def require(condition, tag):
    if not condition:
        raise ValueError("YGG_KNOW25_"+tag)


def canonical(obj):
    return json.dumps(obj,sort_keys=True,ensure_ascii=True,allow_nan=False,
                      separators=(",",":")).encode("ascii")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def protocol():
    d=json.loads(Path(__file__).with_name("know25_x2_probe_protocol.json")
                 .read_text("utf-8"))
    require(d.get("schema")==PROTO_SCHEMA
            and [(x["seed"],x["operator"],x["steps"]) for x in d["fit"]]==list(FIT)
            and [(x["a"],x["b"],tuple(x["seeds"]))
                 for x in d["held_pairs"]]==list(PAIRS)
            and d["frozen_hypotheses"]["H2"].startswith(
                "Trained fixed-x2 Bayes high expected Brier <= .23000")
            and d["source_mode"]==MODE,
            "FROZEN_PROTOCOL")
    return d


def context(t):
    require(type(t) is int and 0<=t<48,"PUBLIC_STEP")
    return t%4


def effective(c,a):
    require(type(c) is int and 0<=c<8 and
            type(a) is int and 0<=a<4,"PUBLIC_ACTION")
    return c^FLIPS[a]


def prob_law(op, c, a):
    require(op in FAMILIES+("x1",) and
            type(c) is int and 0<=c<8,
            "PRIVATE_LAW")
    return FLOOR+SPAN*hidden_bit(op,effective(c,a))


def coin(seed,t):
    seeds={s for s,_,_ in FIT}|{s for _,_,ss in PAIRS for s in ss}
    require(type(seed) is int and seed in seeds and
            type(t) is int and 0<=t<48,"PRIVATE_COIN")
    raw=hashlib.sha256(
        f"know25:private:witness:v1:{seed}:{t}".encode("ascii")).digest()
    return int.from_bytes(raw[:8],"big")/2**64


def witnessed(seed,op,t,c,a):
    require(c==context(t) and op in FAMILIES+("x1",),"PRIVATE_CONTEXT")
    return int(coin(seed,t)<prob_law(op,c,a))


def score(p,q):
    return q*(1-q)+(p-q)**2


class TruthPosterior:
    """256 finite hypotheses, optional prior-rich six-law family control."""
    def __init__(self, prior, family=None, family_prior=None):
        require(type(prior) is list and len(prior)==8 and
                all(type(v) is float and .01<=v<=.99 for v in prior),"PRIOR")
        self.prior=list(prior)
        self.family=tuple(range(256) if family is None else family)
        require(len(self.family) in (6,256) and
                len(set(self.family))==len(self.family) and
                all(type(h) is int and 0<=h<256 for h in self.family),
                "FAMILY")
        if family_prior is None:
            self.family_prior=[1/len(self.family)]*len(self.family)
            if len(self.family)==256:
                logs=[sum(math.log(p if ANF[h][j] else 1-p)
                          for j,p in enumerate(self.prior))
                      for h in self.family]
                mx=max(logs)
                un=[math.exp(x-mx) for x in logs]
                total=sum(un)
                self.family_prior=[x/total for x in un]
        else:
            require(type(family_prior) is list and
                    len(family_prior)==len(self.family) and
                    all(type(v) is float and 0<v<=1 for v in family_prior) and
                    abs(sum(family_prior)-1)<1e-10,"FAMILY_PRIOR")
            self.family_prior=list(family_prior)
        self.logs=[math.log(x) for x in self.family_prior]
        self.tape=[]

    def weights(self):
        mx=max(self.logs)
        u=[math.exp(x-mx) for x in self.logs]
        z=sum(u)
        require(z>0 and math.isfinite(z),"NORM")
        return [x/z for x in u]

    def predict(self,c,a):
        target=effective(c,a)
        return FLOOR+SPAN*sum(w for h,w in zip(self.family,self.weights())
                              if (h>>target)&1)

    def choose(self,c):
        return min(range(4),key=lambda a:
                   (abs(self.predict(c,a)-.5),a))

    def observe(self,t,c,a,y,*,mode=MODE):
        require(mode==MODE and type(t) is int and
                t==len(self.tape) and 0<=t<48 and c==context(t) and
                type(y) is int and y in (0,1),"WITNESS_REPLAY")
        target=effective(c,a)
        for i,h in enumerate(self.family):
            q=FLOOR+SPAN*((h>>target)&1)
            self.logs[i]+=math.log(q if y else 1-q)
        self.tape.append([t,c,a,y])

    def coeff_marginals(self):
        w=self.weights()
        return [sum(z for h,z in zip(self.family,w) if ANF[h][j])
                for j in range(8)]

    def checkpoint(self):
        raw=canonical({"schema":"yggdrasil.know25.posterior.cold.v1",
                       "source_mode":MODE,"prior":self.prior,
                       "family":self.family,"family_prior":self.family_prior,
                       "tape":self.tape,"accepted_native":False,
                       "scientific_gain_verified":False})
        require(len(raw)<8192,"COLD_BUDGET")
        return raw

    @classmethod
    def restore(cls,raw,sha):
        require(type(raw) is bytes and type(sha) is str and
                0<len(raw)<8192 and digest(raw)==sha,"COLD_HASH")
        def unique(pairs):
            result={}
            for k,v in pairs:
                require(k not in result,"DUPLICATE_KEY")
                result[k]=v
            return result
        try:
            d=json.loads(raw.decode("ascii"),object_pairs_hook=unique)
            require(type(d) is dict and set(d)=={
                "schema","source_mode","prior","family","family_prior",
                "tape","accepted_native","scientific_gain_verified"
            } and d["schema"]=="yggdrasil.know25.posterior.cold.v1"
                    and d["source_mode"]==MODE
                    and d["accepted_native"] is False
                    and d["scientific_gain_verified"] is False
                    and canonical(d)==raw, "COLD_SCHEMA")
            m=cls(d["prior"],family=d["family"],
                  family_prior=d["family_prior"])
            require(type(d["tape"]) is list and len(d["tape"])<=48,
                    "COLD_TAPE")
            for step,row in enumerate(d["tape"]):
                require(type(row) is list and len(row)==4 and
                        all(type(x) is int for x in row) and
                        row[0]==step,"COLD_ROW")
                m.observe(*row)
            require(m.checkpoint()==raw,"COLD_REPLAY")
            return m
        except (ValueError,TypeError,KeyError,UnicodeError,OverflowError) as e:
            raise ValueError("YGG_KNOW25_BAD_CHECKPOINT") from e


class ContextBeta:
    def __init__(self):
        self.counts=[[0,0] for _ in range(8)]
        self.tape=[]
    def predict(self,c,a):
        s,n=self.counts[effective(c,a)]
        return (s+1)/(n+2)
    def observe(self,t,c,a,y,*,mode=MODE):
        require(mode==MODE and t==len(self.tape) and
                c==context(t) and type(y) is int and y in (0,1),
                "BETA_REPLAY")
        z=self.counts[effective(c,a)]
        z[0]+=y
        z[1]+=1
        self.tape.append([t,c,a,y])


class Passive:
    def predict(self,c,a): return .5
    def observe(self,t,c,a,y,*,mode=MODE):
        require(mode==MODE and type(y) is int and y in (0,1),
                "PASSIVE_SOURCE")


def fit():
    protocol()
    sparse=[]
    uniform=[]
    family=[]
    beta_counts=[[0,0] for _ in range(8)]
    for seed,op,n in FIT:
        a=TruthPosterior([.25]*8)
        u=TruthPosterior([.5]*8)
        f=TruthPosterior([.5]*8,family=FAMILY_TABLES)
        for t in range(n):
            c=t%4
            y=int(coin(seed,t)<prob_law(op,c,0))
            a.observe(t,c,0,y)
            u.observe(t,c,0,y)
            f.observe(t,c,0,y)
            z=beta_counts[c]
            z[0]+=y
            z[1]+=1
        sparse.append(a)
        uniform.append(u)
        family.append(f)
    def combine(models):
        return [float(min(.92,max(.08,
                 (.5+sum(m.coeff_marginals()[j] for m in models))/5)))
                for j in range(8)]
    prior=combine(sparse)
    uniform_prior=combine(uniform)
    fam=[float((1/len(FAMILY_TABLES)+
                sum(m.weights()[j] for m in family))/4)
         for j in range(len(FAMILY_TABLES))]
    sm=sum(fam)
    fam=[float(v/sm) for v in fam]
    # All x2-containing monomials are unaffected by low-only FIT evidence.
    for m in sparse:
        require(all(abs(m.coeff_marginals()[j]-.25)<1e-12
                    for j in range(4,8)),"FIT_X2_UNIDENTIFIABLE")
        raw=m.checkpoint()
        require(TruthPosterior.restore(raw,digest(raw)).checkpoint()==raw,
                "FIT_COLD")
    return {"trained":prior,"uniform":uniform_prior,"family":fam,
            "beta":beta_counts,"fit_witnesses":72,
            "fit_x2_coefficients":[prior[j] for j in range(4,8)],
            "fit_checkpoint_bytes":[len(m.checkpoint()) for m in sparse]}


def model_for(name,fit_bundle):
    if name=="uninformed_p05":return Passive()
    if name=="context_beta_fixed_x2":
        z=ContextBeta()
        z.counts=[list(x) for x in fit_bundle["beta"]]
        return z
    if name=="known_family_bayes_fixed_x2":
        return TruthPosterior([.5]*8,family=FAMILY_TABLES,
                              family_prior=fit_bundle["family"])
    if name=="uniform_full_bayes_fixed_x2":
        return TruthPosterior(fit_bundle["uniform"])
    if name=="untrained_anf_fixed_x2":
        return TruthPosterior([.25]*8)
    return TruthPosterior(fit_bundle["trained"])


def run_world(name, world, pair_id, fit_bundle):
    require(name in POLICIES and
            type(world) is tuple and len(world)==2 and
            type(world[0]) is int and
            any(world[0] in seeds and world[1] in (a,b)
                for a,b,seeds in PAIRS) and
            type(pair_id) is int and 0<=pair_id<9,"FROZEN_HELD")
    seed,op=world
    m=model_for(name,fit_bundle)
    rng=random.Random(pair_id*27041+53)
    trace=[]
    choices=[0,0,0,0]
    for t in range(48):
        c=context(t)
        if name=="trained_anf_no_x2":
            action=t%3
        elif name=="trained_anf_active_x2":
            action=m.choose(c)
        elif name=="trained_anf_random_x2":
            action=rng.randrange(4)
        else:
            action=3 if t%3==0 else t%3-1
        y=witnessed(seed,op,t,c,action)
        m.observe(t,c,action,y)
        trace.append([t,c,action,y])
        choices[action]+=1
    if isinstance(m,TruthPosterior):
        raw=m.checkpoint()
        cold=TruthPosterior.restore(raw,digest(raw))
        require(cold.checkpoint()==raw,"HELD_COLD")
        num_bytes=len(raw)
        x2=[float(x) for x in m.coeff_marginals()[4:]]
    else:
        num_bytes=len(canonical(getattr(m,"counts",{})))
        x2=None
    high=[m.predict(c,a) for c in range(4,8) for a in range(3)]
    low=[m.predict(c,a) for c in range(4) for a in range(3)]
    require(len(trace)==48 and len(high)==len(low)==12 and
            all(math.isfinite(z) and 0<=z<=1 for z in high+low),
            "BUDGET_FORECAST")
    return {"trace":trace,"high":high,"low":low,
            "high_sum":sum(score(z,prob_law(op,c,a))
                           for z,(c,a) in zip(high,((c,a) for c in range(4,8)
                                                       for a in range(3)))),
            "low_sum":sum(score(z,prob_law(op,c,a))
                          for z,(c,a) in zip(low,((c,a) for c in range(4)
                                                      for a in range(3)))),
            "choices":choices,"bytes":num_bytes,"x2_posterior":x2}


def proof():
    started=time.monotonic()
    fitted=fit()
    result={}
    pair_status={}
    raw_by_policy={}
    for name in POLICIES:
        pairs=[]
        rows=[]
        for gi,(a,b,seeds) in enumerate(PAIRS):
            for si,seed in enumerate(seeds):
                pid=gi*3+si
                left=run_world(name,(seed,a),pid,fitted)
                right=run_world(name,(seed,b),pid,fitted)
                rows.extend((left,right))
                identical=(left["trace"]==right["trace"] and
                           left["high"]==right["high"])
                paired=(left["high_sum"]+right["high_sum"])/24
                pairs.append({"identical":identical,
                              "pair_high_loss":round(paired,8),
                              "pair_group":gi,"seed":seed})
        require(len(rows)==18 and all(len(x["trace"])==48 for x in rows),
                "HELD_ACTION_BUDGET")
        require(name not in ("trained_anf_fixed_x2",
                            "untrained_anf_fixed_x2",
                            "uniform_full_bayes_fixed_x2",
                            "context_beta_fixed_x2",
                            "known_family_bayes_fixed_x2",
                            "uninformed_p05") or
                all(x["choices"][3]==16 and
                    [sum(1 for t,c,a,y in x["trace"] if a==3 and c==j)
                     for j in range(4)]==[4]*4 for x in rows),
                "FORCED_PROBES")
        result[name]={
            "high_expected_brier":round(sum(x["high_sum"] for x in rows)/216,8),
            "low_expected_brier":round(sum(x["low_sum"] for x in rows)/216,8),
            "action_counts":[sum(x["choices"][j] for x in rows)
                              for j in range(4)],
            "avg_checkpoint_bytes":round(sum(x["bytes"] for x in rows)/18,2),
            "avg_x2_coefficient_posterior":[
                 round(sum(x["x2_posterior"][j] for x in rows)/18,8)
                 for j in range(4)
            ] if all(x["x2_posterior"] is not None for x in rows) else None
        }
        pair_status[name]=pairs
    nofit=result["untrained_anf_fixed_x2"]["high_expected_brier"]
    trained=result["trained_anf_fixed_x2"]["high_expected_brier"]
    nox=result["trained_anf_no_x2"]["high_expected_brier"]
    uniform=result["uniform_full_bayes_fixed_x2"]["high_expected_brier"]
    active=result["trained_anf_active_x2"]["high_expected_brier"]
    h={
      "H1_no_x2_pairs_identical_and_floor":
        all(z["identical"] and z["pair_high_loss"]>=.25-1e-8
            for z in pair_status["trained_anf_no_x2"]),
      "H2_x2_probing_gain":
        trained<=.23000 and nox-trained>=.02000,
      "H3_fitted_vs_uniform_full_bayes_tolerance":
        trained<=uniform+.01000,
      "H4_FIT_prior_value_over_same_no_FIT":
        trained<=nofit-.00500,
      "H5_entropy_active_value_over_forced":
        active<=trained-.00500,
    }
    require(h["H1_no_x2_pairs_identical_and_floor"],
            "NO_X2_INFORMATION_BOUND")
    successes=sum(h.values())
    return {
      "schema":SCHEMA,"prereg_commit":PREREG,"source_mode":MODE,
      "fit_witnesses":fitted["fit_witnesses"],
      "held_worlds":18,"held_witnesses_per_policy":864,
      "high_eval_queries_per_policy":216,"low_eval_queries_per_policy":216,
      "fit_x2_ANF_coefficient_prior":fitted["fit_x2_coefficients"],
      "fit_checkpoint_bytes":fitted["fit_checkpoint_bytes"],
      "metrics":result,"no_x2_pair_custody":pair_status["trained_anf_no_x2"],
      "frozen_hypotheses":h,
      "frozen_margins":{"x2_probe_gain":round(nox-trained,8),
                         "vs_uniform":round(uniform-trained,8),
                         "FIT_gain":round(nofit-trained,8),
                         "active_gain":round(trained-active,8)},
      "development_verdict":(
        "CAUSAL_PROBE_SUPPORTED_DEV" if successes==5 else
        "MIXED_CAUSAL_PROBE_DEV" if successes>1 else
        "CAUSAL_PROBE_NO_GO"),
      "engineering_gate":"PASS",
      "science_gate":"SCIENCE_NO_GO_SYNTHETIC_NOT_NATIVE",
      "accepted_native_modified":False,"first_use_426":False,
      "deployment":"NONE",
      "isolated_wall_seconds_no_checkout":round(time.monotonic()-started,6)
    }


if __name__=="__main__":
    print("YGG_KNOW25_RECEIPT="+json.dumps(proof(),sort_keys=True))
