"""KNOW25: new x2-intervention structural identification from single witnesses.

Preregistered BEFORE source/score at 9155e5d62d6d5a0eb4f79fef22953e9e5e4f25da.
Source-only independent research prototype. This DOES NOT modify accepted native
Yggdrasil weights, original-world custody, training controller or checkpoint.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import time
from pathlib import Path

from anf_causal_identifiability_dev import (
    ANF, HYPOTHESES, KNOWN_PAIR_TABLES, TruthPosterior,
    fitted_prior, source_context, effective, hidden_bit,
    expected_brier, MODE, P_LOW, P_HIGH, canonical, digest, require,
)

SCHEMA = "yggdrasil.know25.x2-intervention-result.v1"
PROTO = "yggdrasil.know25.x2-intervention-causal-identification-frozen-dev.v1"
COLD_SCHEMA = "yggdrasil.know25.probe-posterior-cold.v1"
PREREG = "9155e5d62d6d5a0eb4f79fef22953e9e5e4f25da"
PAIRINGS = (
    ("x0", "x0_xor_x2", (11711,11717,11719)),
    ("xor01", "xor01_xor_x2", (11801,11807,11813)),
    ("and01", "and01_xor_x2", (11903,11909,11911)),
)
POLICIES = (
    "learned_anf_active_x2", "learned_anf_no_x2",
    "learned_anf_passive", "learned_anf_random",
    "learned_anf_forced_x2", "untrained_anf_active_x2",
    "uniform_full_bayes_active_x2", "known_family_bayes_active_x2",
    "low_context_beta", "source_only",
)
FLIP = (0,1,2,4)
ALL_SEEDS = frozenset(s for a,b,seeds in PAIRINGS for s in seeds)
STEPS = 24


def effective4(c,a):
    require(type(c) is int and 0 <= c < 8 and
            type(a) is int and a in (0,1,2,3), "ACTION")
    return c ^ FLIP[a]


def frozen_protocol():
    p=json.loads(Path(__file__).with_name("know25_protocol.json")
                 .read_text(encoding="utf-8"))
    require(p.get("schema")==PROTO and
            [(r["base"],r["variant"],tuple(r["seeds"]))
             for r in p["held_pairs"]]==list(PAIRINGS) and
            p["held_steps"]==24 and p["scoring"]["worlds"]==18
            and p["scoring"]["held_witnesses_per_policy"]==432 and
            p["scoring"]["high_expected_evaluator_queries_per_policy"]==216
            and p["fit"]["source"].startswith("Exactly three previous")
            and "matched no-x2" in p["hypotheses"]["H4"].lower(),
            "PROTOCOL_DRIFT")
    return p


def private_coin(seed,step):
    require(type(seed) is int and seed in ALL_SEEDS and
            type(step) is int and 0 <= step < STEPS,
            "PRIVATE_COIN")
    raw=f"know25:private:witness:v1:{seed}:{step}".encode("ascii")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8],"big")/2**64


def witnessed(seed,op,step,c,action):
    require(any(seed in seeds and op in (a,b)
                for a,b,seeds in PAIRINGS)
            and c==source_context(step) and c<4,
            "PRIVATE_PAIR_CUSTODY")
    q=P_HIGH if hidden_bit(op,effective4(c,action)) else P_LOW
    return int(private_coin(seed,step)<q)


def q_true(op,c,action):
    return P_HIGH if hidden_bit(op,effective4(c,action)) else P_LOW


class ProbePosterior(TruthPosterior):
    """Exact 256-table/6-table Bayes with x2-flip action (no teacher)."""

    def prob(self,c,action):
        target=effective4(c,action)
        weights=self._weights()
        return P_LOW+(P_HIGH-P_LOW)*sum(
            w for h,w in weights.items() if (h>>target)&1)

    def choose(self,c,strategy,rng=None):
        require(type(c) is int and 0<=c<4 and
                strategy in ("active","no_x2","passive",
                             "random","forced_x2"),"CHOOSE")
        if strategy=="passive":
            return 0
        if strategy=="forced_x2":
            return 3
        if strategy=="random":
            require(isinstance(rng,random.Random),"RNG")
            return rng.randrange(4)
        allowed=(0,1,2) if strategy=="no_x2" else (0,1,2,3)
        return min(allowed,key=lambda a:
                   (abs(self.prob(c,a)-.5),a))

    def observe(self,step,c,action,y,*,source_mode=MODE):
        require(source_mode==MODE and
                type(step) is int and step==len(self.events)
                and 0<=step<STEPS and c==source_context(step)
                and type(y) is int and y in (0,1),
                "OBSERVED_WITNESS")
        target=effective4(c,action)
        for h in self.family:
            q=P_HIGH if (h>>target)&1 else P_LOW
            self.logw[h]+=math.log(q if y else 1-q)
        self.events.append([step,c,action,y])

    def checkpoint(self):
        raw=canonical({
            "schema":COLD_SCHEMA,"mode":MODE,"prior":self.prior,
            "family":self.family,"events":self.events,
            "accepted_native":False,"science_qualified":False
        })
        require(len(raw)<=8192,"CHECKPOINT_CAP")
        return raw

    @classmethod
    def restore(cls,raw,expected_sha):
        require(type(raw) is bytes and 0<len(raw)<=8192 and
                type(expected_sha) is str and digest(raw)==expected_sha,
                "CHECKPOINT_DIGEST")
        def unique(pairs):
            result={}
            for key,value in pairs:
                require(key not in result,"DUPLICATE_JSON")
                result[key]=value
            return result
        try:
            d=json.loads(raw.decode("ascii"),object_pairs_hook=unique)
            require(type(d) is dict and set(d)=={
                "schema","mode","prior","family","events",
                "accepted_native","science_qualified"}
                and d["schema"]==COLD_SCHEMA and d["mode"]==MODE
                and d["accepted_native"] is False
                and d["science_qualified"] is False
                and type(d["events"]) is list and
                len(d["events"])<=STEPS and canonical(d)==raw,
                "CHECKPOINT_CONTRACT")
            z=cls(d["prior"],family=d["family"])
            for step,row in enumerate(d["events"]):
                require(type(row) is list and len(row)==4 and
                        all(type(x) is int for x in row) and
                        row[0]==step,"CHECKPOINT_EVENTS")
                z.observe(*row)
            require(z.checkpoint()==raw,"COLD_REPLAY")
            return z
        except (ValueError,TypeError,KeyError,UnicodeError,OverflowError) as exc:
            raise ValueError("YGG_KNOW25_CHECKPOINT_REJECTED") from exc


class PublicTargetBeta:
    def __init__(self):
        self.counts=[[0,0] for _ in range(8)]
        self.events=[]

    def prob(self,c,action):
        successes,total=self.counts[effective4(c,action)]
        return (1+successes)/(2+total)

    def choose(self,c,strategy,rng=None):
        return min(range(4),key=lambda a:(abs(self.prob(c,a)-.5),a))

    def observe(self,step,c,action,y,*,source_mode=MODE):
        require(source_mode==MODE and
                type(step) is int and step==len(self.events)
                and step<STEPS and c==source_context(step)
                and type(y) is int and y in (0,1),
                "TARGET_WITNESS")
        counts=self.counts[effective4(c,action)]
        counts[0]+=y
        counts[1]+=1
        self.events.append([step,c,action,y])

    def checkpoint(self):
        raw=canonical({"counts":self.counts,"events":self.events})
        replay=PublicTargetBeta()
        for row in self.events: replay.observe(*row)
        require(replay.counts==self.counts and
                replay.events==self.events,"BETA_COLD")
        return raw


class SourceOnly:
    def __init__(self):
        self.events=[]
    def prob(self,c,action):
        effective4(c,action)
        return .5
    def choose(self,c,strategy,rng=None):
        return 0
    def observe(self,step,c,action,y,*,source_mode=MODE):
        require(source_mode==MODE and
                type(step) is int and step==len(self.events)
                and step<STEPS and c==source_context(step)
                and type(y) is int and y in (0,1),"SOURCE_WITNESS")
        self.events.append([step,c,action,y])
    def checkpoint(self):
        return canonical(self.events)


def model_for(name,prior):
    require(name in POLICIES and
            type(prior) is list and len(prior)==8,"MODEL")
    if name in ("learned_anf_active_x2","learned_anf_no_x2",
                "learned_anf_passive","learned_anf_random",
                "learned_anf_forced_x2"):
        return ProbePosterior(list(prior))
    if name=="untrained_anf_active_x2":
        return ProbePosterior([.25]*8)
    if name=="uniform_full_bayes_active_x2":
        return ProbePosterior([.5]*8)
    if name=="known_family_bayes_active_x2":
        return ProbePosterior([.5]*8,family=KNOWN_PAIR_TABLES)
    if name=="low_context_beta":
        return PublicTargetBeta()
    return SourceOnly()


def strategy_for(name):
    return {
        "learned_anf_no_x2":"no_x2",
        "learned_anf_passive":"passive",
        "learned_anf_random":"random",
        "learned_anf_forced_x2":"forced_x2",
        "source_only":"passive",
    }.get(name,"active")


def one_world(name,seed,op,pair_index,prior):
    require(name in POLICIES and
            any(seed in seeds and op in (a,b) for a,b,seeds in PAIRINGS)
            and type(pair_index) is int and 0<=pair_index<9,
            "HELD_WORLD")
    z=model_for(name,prior)
    strategy=strategy_for(name)
    # Explicit public pair index, not private hidden law.
    rng=random.Random(20071*pair_index+193)
    transcript=[]
    counts=[0,0,0,0]
    for t in range(STEPS):
        c=source_context(t)
        a=z.choose(c,strategy,rng)
        effective4(c,a)
        counts[a]+=1
        y=witnessed(seed,op,t,c,a)
        z.observe(t,c,a,y)
        transcript.append([c,a,y])
    raw=z.checkpoint()
    if isinstance(z,ProbePosterior):
        clone=ProbePosterior.restore(raw,digest(raw))
        require(clone.checkpoint()==raw and
                all(clone.prob(c,a)==z.prob(c,a)
                    for c in range(8) for a in range(4)),
                "SOURCE_COLD_RESTORE")
    elif isinstance(z,PublicTargetBeta):
        require(z.checkpoint()==raw,"BETA_CHECKPOINT")
    else:
        require(len(z.events)==STEPS,"SOURCE_COUNT")

    all_high=[(c,a) for c in range(4,8) for a in (0,1,2)]
    all_low=[(c,a) for c in range(4) for a in (0,1,2)]
    forecast_high=[z.prob(c,a) for c,a in all_high]
    forecast_low=[z.prob(c,a) for c,a in all_low]
    require(len(forecast_high)==len(forecast_low)==12 and
            all(math.isfinite(p) and 0<=p<=1
                for p in forecast_high+forecast_low),
            "EVALUATOR_PREDICTIONS")
    return {
        "transcript":transcript,
        "forecasts_high":forecast_high,
        "high_sum":sum(expected_brier(p,q_true(op,c,a))
                       for p,(c,a) in zip(forecast_high,all_high)),
        "low_sum":sum(expected_brier(p,q_true(op,c,a))
                      for p,(c,a) in zip(forecast_low,all_low)),
        "action_counts":counts,
        "checkpoint_bytes":len(raw),
        "witnesses":len(transcript)
    }


def proof():
    started=time.monotonic()
    frozen_protocol()
    prior,oldfit=fitted_prior()
    # Original fit is unchanged. Each state restored without private labels.
    fit_hashes=[digest(z.checkpoint()) for z in oldfit]
    require(len(oldfit)==3 and
            all(type(p) is float for p in prior),"FROZEN_FIT")
    totals={}
    paired={}
    nox2_equal=True
    min_nox2_pair_brier=1.0
    for name in POLICIES:
        rows=[]
        pairs=[]
        for f,(base,variant,seeds) in enumerate(PAIRINGS):
            for j,seed in enumerate(seeds):
                idx=f*3+j
                a=one_world(name,seed,base,idx,prior)
                b=one_world(name,seed,variant,idx,prior)
                rows.extend((a,b))
                if name=="learned_anf_no_x2":
                    same=(a["transcript"]==b["transcript"]
                          and a["forecasts_high"]==b["forecasts_high"])
                    nox2_equal &= same
                    min_nox2_pair_brier=min(
                        min_nox2_pair_brier,(a["high_sum"]+b["high_sum"])/24)
                pairs.append({
                    "family_index":f,"seed":seed,
                    "shared_trace":a["transcript"]==b["transcript"],
                    "x2_probes_base":a["action_counts"][3],
                    "x2_probes_variant":b["action_counts"][3],
                    "high_forecast_mean_abs_pair_delta":round(
                        sum(abs(u-v) for u,v in zip(
                            a["forecasts_high"],b["forecasts_high"]))/12,8)
                })
        require(len(rows)==18 and
                sum(z["witnesses"] for z in rows)==432,"WITNESS_BUDGET")
        totals[name]={
            "high_expected_brier":round(sum(z["high_sum"] for z in rows)/216,8),
            "low_expected_brier":round(sum(z["low_sum"] for z in rows)/216,8),
            "actions":[sum(z["action_counts"][i] for z in rows)
                       for i in range(4)],
            "mean_checkpoint_bytes":round(
                sum(z["checkpoint_bytes"] for z in rows)/18,2),
            "worlds_with_x2_probe":sum(z["action_counts"][3]>0 for z in rows)
        }
        paired[name]=pairs
    assert not any(v["actions"][3]>0
                   for n,v in totals.items()
                   if n in ("learned_anf_no_x2","learned_anf_passive",
                            "source_only"))
    cand=totals["learned_anf_active_x2"]
    nox2=totals["learned_anf_no_x2"]
    passive=totals["learned_anf_passive"]
    nofit=totals["untrained_anf_active_x2"]
    uniform=totals["uniform_full_bayes_active_x2"]
    h={
        "H1_no_x2_pair_identity":nox2_equal,
        "H2_no_x2_pair_bound":min_nox2_pair_brier>=.25-1e-8,
        "H3_x2_probe_coverage":cand["worlds_with_x2_probe"]==18
                               and cand["actions"][3]>=72,
        "H4_active_vs_no_x2_gain":cand["high_expected_brier"]<=
                                  nox2["high_expected_brier"]-.02,
        "H5_active_vs_passive_gain":cand["high_expected_brier"]<=
                                    passive["high_expected_brier"]-.02,
        "H6_high_expected_brier_target":cand["high_expected_brier"]<=.2,
        "H7_fit_vs_no_fit_gain":cand["high_expected_brier"]<=
                                nofit["high_expected_brier"]-.005,
        "H8_vs_uniform_full_bayes_gain":cand["high_expected_brier"]<=
                                        uniform["high_expected_brier"]-.01
    }
    require(h["H1_no_x2_pair_identity"] and
            h["H2_no_x2_pair_bound"],"SOURCE_LEAK_OR_MATH")
    good=sum(h[k] for k in (
        "H3_x2_probe_coverage","H4_active_vs_no_x2_gain",
        "H5_active_vs_passive_gain","H6_high_expected_brier_target"))
    verdict=("DEVELOPMENT_X2_IDENTIFICATION_SUPPORTED" if good==4
             else "DEVELOPMENT_MIXED" if good else "DEVELOPMENT_NO_GO")
    return {
        "schema":SCHEMA,"prereg_commit":PREREG,
        "fit_witnesses":72,"held_worlds":18,"held_witnesses_per_policy":432,
        "high_expected_queries_per_policy":216,
        "low_expected_queries_per_policy":216,
        "learned_anf_coeff_prior":prior,
        "original_fit_cold_sha256":fit_hashes,
        "held_policy_results":totals,
        "paired_causal_world_diagnostics":paired,
        "no_x2_min_pair_expected_brier":round(min_nox2_pair_brier,8),
        "frozen_hypotheses":h,"development_verdict":verdict,
        "engineering_gate":"PASS",
        "scientific_gate":"SCIENCE_NO_GO_SYNTHETIC_NOT_ORIGINAL_NATIVE",
        "accepted_native_modified":False,
        "protected_original_first_use":False,
        "canonical_checkpoint_changed":False,"deployment":"NONE",
        "isolated_wall_seconds":round(time.monotonic()-started,6)
    }


if __name__=="__main__":
    print(json.dumps(proof(),sort_keys=True,indent=2))
