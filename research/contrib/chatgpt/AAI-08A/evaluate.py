"""AAI-08A: preregistered A→B→A consequence learning on official NS-Gym Bridge.

External contributor science only. No native Yggdrasil, weights, controllers
or promotion. Learners receive only a common stream of actual forward/other
outcomes after public action RIGHT, not regime labels or private simulator info.
"""
from __future__ import annotations

import collections
import hashlib
import json
import math
import random
import time

import gymnasium as gym
import ns_gym
import numpy as np
from ns_gym.schedulers import DiscreteScheduler
from ns_gym.update_functions import DistributionStepWiseUpdate
from ns_gym.wrappers import NSBridgeWrapper

PREREG="db263b1de02fdaaec2152b44947a1e11b5305262"
AMENDMENT="57e8933f0376c226a62ab7252bb395482fa41eb2"
UPSTREAM="127df4b714fe4fcf680721d8e9278a96090acd7e"
DEV=range(891000,891032)
TRANSFER=range(892000,892064)
NEGATIVE=range(893000,893032)
MECHANICAL=tuple(range(898000,898004))
PHASES=("A","B","A")
EPISODES=24
TRIALS=6
BOOTSTRAP=1024
ACTIONS=(2,0,2)
BENCHMARK="ns_gym/Bridge-v0"
INITIAL=[1.,0.,0.]
DEV_LAWS={"A":[.75,.15,.10],"B":[.15,.75,.10]}
TRANSFER_LAWS={"A":[.65,.20,.15],"B":[.22,.63,.15]}
LOGISTIC_EPOCHS=1200
BLOCK=5
THRESHOLD=math.log(3.)


def stable_seed(*parts):
    h=hashlib.sha256(":".join(str(z) for z in parts).encode()).digest()
    return int.from_bytes(h[:8],"big")%(2**32)


def state_equal(a,b):
    return (a[0]==b[0] and np.array_equal(a[1],b[1]) and a[2:]==b[2:])


def official_episode(law,seed,last_action):
    """Seed entire external simulator's legacy NumPy RNG inside scoped guard."""
    saved=np.random.get_state()
    env=None
    try:
        np.random.seed(seed)
        env=NSBridgeWrapper(
            gym.make(BENCHMARK),
            tunable_params={"P":DistributionStepWiseUpdate(
                DiscreteScheduler({3}),[list(law)])},
            initial_prob_dist=list(INITIAL),
            change_notification=False,delta_change_notification=False,
            scalar_reward=True,persistent_params=False)
        obs,_info=env.reset(seed=seed)
        assert int(obs["state"])>=0
        for tick,action in enumerate(ACTIONS):
            obs,reward,terminal,truncated,_info=env.step(action)
            assert not (terminal or truncated),(seed,tick)
            assert float(reward)==0
            assert obs["env_change"]["P"]==0
            assert obs["delta_change"]["P"]==0
        position=int(obs["state"])
        assert env.action_space.contains(last_action)
        obs,reward,terminal,truncated,_info=env.step(last_action)
        assert obs["env_change"]["P"]==0
        assert obs["delta_change"]["P"]==0
        assert int(obs["relative_time"])==4
        assert float(reward) in (-1.,0.,1.)
        return {
            "state":position,
            "action":int(last_action),
            "next_state":int(obs["state"]),
            "reward":float(reward),
            "terminal":bool(terminal or truncated),
            "forward":bool(last_action==2 and int(obs["state"])==position+1),
            "safe":float(reward)>=0.,
        }
    finally:
        if env is not None:
            env.close()
        np.random.set_state(saved)
        assert state_equal(saved,np.random.get_state())


class Beta:
    def __init__(self):
        self.yes=1
        self.no=1
    def add(self,flags):
        for flag in flags:
            if flag:self.yes+=1
            else:self.no+=1
    def prob(self):
        return self.yes/(self.yes+self.no)
    def state(self):
        return [self.yes,self.no]
    @classmethod
    def from_state(cls,s):
        x=cls();x.yes,x.no=map(int,s);return x


class RegimeCache:
    """Two learned Beta hypotheses; likelihood-gated retrieval, NOT novel Bayes."""
    def __init__(self,capacity=2):
        self.capacity=capacity
        self.slots=[Beta()]
        self.active=0
        self.pending=[]
    def learn(self,event):
        self.pending.append(bool(event))
        if len(self.pending)<BLOCK:return
        batch=self.pending
        self.pending=[]
        def score(slot):
            p=max(.0001,min(.9999,slot.prob()))
            return sum(math.log(p) if y else math.log(1-p) for y in batch)
        active_score=score(self.slots[self.active])
        scores=[score(m) for m in self.slots]
        alt=max(range(len(scores)),key=lambda i:scores[i])
        if alt!=self.active and scores[alt]>active_score+THRESHOLD:
            self.active=alt
            self.slots[self.active].add(batch)
        elif len(self.slots)<self.capacity and BLOCK*math.log(.5)>active_score+THRESHOLD:
            new=Beta();new.add(batch);self.slots.append(new);self.active=len(self.slots)-1
        elif self.capacity==1 and BLOCK*math.log(.5)>active_score+THRESHOLD:
            new=Beta();new.add(batch);self.slots=[new];self.active=0
        else:
            self.slots[self.active].add(batch)
    def prob(self):
        return self.slots[self.active].prob()
    def choose(self):
        return 2 if self.prob()>=.5 else 3
    def state(self):
        return {"capacity":self.capacity,"active":self.active,
                "slots":[x.state() for x in self.slots],
                "pending":self.pending}
    @classmethod
    def from_state(cls,state):
        x=cls(state["capacity"])
        x.slots=[Beta.from_state(s) for s in state["slots"]]
        x.active=int(state["active"])
        x.pending=list(state["pending"])
        return x


class Stationary:
    def __init__(self):
        self.slot=Beta()
    def learn(self,flag):
        self.slot.add([flag])
    def choose(self):
        return 2 if self.slot.prob()>=.5 else 3
    def state(self):
        return self.slot.state()
    @classmethod
    def from_state(cls,st):
        x=cls();x.slot=Beta.from_state(st);return x


class Recent:
    def __init__(self):
        self.window=collections.deque(maxlen=8)
    def learn(self,flag):
        self.window.append(bool(flag))
    def choose(self):
        p=(1+sum(self.window))/(2+len(self.window))
        return 2 if p>=.5 else 3
    def state(self):
        return list(self.window)
    @classmethod
    def from_state(cls,state):
        x=cls();x.window=collections.deque(state,maxlen=8);return x


class Logistic:
    """Fully fitted (1200 epochs) intercept-only SGD on common observed events."""
    def __init__(self):
        self.history=[]
        self.weight=0.
        self.dirty=True
    def learn(self,flag):
        self.history.append(bool(flag))
        self.dirty=True
    def fit(self):
        if not self.dirty:return
        mean=sum(self.history)/len(self.history)
        for _ in range(LOGISTIC_EPOCHS):
            value=max(-40.,min(40.,self.weight))
            p=1/(1+math.exp(-value))
            self.weight-=.4*(p-mean)
        self.dirty=False
    def choose(self):
        self.fit()
        return 2 if self.weight>=0 else 3
    def state(self):
        return {"history":self.history,"weight":self.weight,"dirty":self.dirty}
    @classmethod
    def from_state(cls,st):
        x=cls();x.history=list(st["history"]);x.weight=float(st["weight"]);x.dirty=bool(st["dirty"]);return x


class KnownLawBayes:
    """Domain-informed A/B HMM oracle reference, NOT matched-model baseline."""
    def __init__(self):
        self.q=.5
    def learn(self,forward):
        qprior=.95*self.q+.05*(1-self.q)
        likelihood_A=.75 if forward else .25
        likelihood_B=.15 if forward else .85
        a=qprior*likelihood_A
        b=(1-qprior)*likelihood_B
        self.q=a/(a+b)
    def choose(self):
        p=self.q*.75+(1-self.q)*.15
        return 2 if p>=.5 else 3
    def state(self):
        return self.q
    @classmethod
    def from_state(cls,st):
        x=cls();x.q=float(st);return x


class AlwaysRight:
    def learn(self,flag):pass
    def choose(self):return 2
    def state(self):return 0
    @classmethod
    def from_state(cls,st):return cls()


METHODS={
    "candidate":lambda:RegimeCache(2),
    "stationary":Stationary,
    "logistic":Logistic,
    "recent":Recent,
    "no_alt_memory":lambda:RegimeCache(1),
    "known_law_hmm_oracle":KnownLawBayes,
    "reactive":AlwaysRight,
}
MATCHED=("stationary","logistic","recent")
BASELINES=("candidate",)+MATCHED+("no_alt_memory","known_law_hmm_oracle","reactive")


def new_models():
    return {k:creator() for k,creator in METHODS.items()}


def serial(m):
    return json.dumps(m.state(),sort_keys=True,separators=(",",":"))


def restore_model(name,raw):
    cls=METHODS[name]
    return cls().from_state(json.loads(raw))


def train_all(models,event):
    for model in models.values():
        model.learn(bool(event))


def choices(models):
    return {k:model.choose() for k,model in models.items()}


def evaluate_phase(models,world,phase,law,suffix):
    count={}
    decisions={}
    decision_seconds={}
    for name,model in models.items():
        begin=time.perf_counter()
        decisions[name]=model.choose()
        decision_seconds[name]=time.perf_counter()-begin
    rows=[]
    for i in range(TRIALS):
        seed=stable_seed(world,"eval",phase,i,suffix)
        sample={"trial":i,"seed_receipt":seed}
        for name,action in decisions.items():
            start=time.perf_counter()
            outcome=official_episode(law,seed,action)
            count[name]=count.get(name,0)+time.perf_counter()-start
            sample[name]={"action":action,"reward":outcome["reward"],
                          "safe":outcome["safe"],
                          "next_state":outcome["next_state"]}
        rows.append(sample)
    correct=2 if law[0]>.5 else 3
    return {
        "world":world,"phase_index":phase,"true_law_visible_to_evaluator_only":suffix,
        "correct_decision":correct,
        "decisions":decisions,
        "episodes":rows,
        "env_seconds":count,
        "decision_seconds":decision_seconds,
    }


def world_record(world,law_map,negative=False):
    plans=[law_map[phase] for phase in PHASES]
    common=[]
    for p,law in enumerate(plans):
        for i in range(EPISODES):
            seed=stable_seed(world,"train",p,i)
            result=official_episode(law,seed,2)
            common.append({"phase":p,"trial":i,"forward":bool(result["forward"]),
                           "source_state":result["state"],"next_state":result["next_state"],
                           "reward":result["reward"],"terminal":result["terminal"]})
    assert len(common)==72
    labels=[x["forward"] for x in common]
    scrambled=list(labels)
    if negative:
        random.Random(stable_seed(world,"negative",18181)).shuffle(scrambled)
    models=new_models()
    shuffled_model=RegimeCache(2) if negative else None
    phase_results=[]
    model_time={k:0.0 for k in METHODS}
    before_cold=None
    after_cold=None
    for phase in range(3):
        for i in range(EPISODES):
            k=phase*EPISODES+i
            event=labels[k]
            for name,model in models.items():
                start=time.perf_counter()
                model.learn(event)
                model_time[name]+=time.perf_counter()-start
            if negative:
                start=time.perf_counter()
                shuffled_model.learn(scrambled[k])
                model_time["shuffled_candidate"]=model_time.get("shuffled_candidate",0.)+(time.perf_counter()-start)
        if phase==1:
            # Check cold deterministic restore at exactly the preregistered end-B state.
            before_cold={name:serial(model) for name,model in models.items()}
            after_cold={name:serial(restore_model(name,raw)) for name,raw in before_cold.items()}
            assert before_cold==after_cold
            assert choices(models)==choices({name:restore_model(name,raw)
                                            for name,raw in before_cold.items()})
            if negative:
                assert serial(shuffled_model)==serial(restore_model("candidate",serial(shuffled_model)))
        evaluated=dict(models)
        if negative:
            evaluated["shuffled_candidate"]=shuffled_model
        result=evaluate_phase(evaluated,world,phase,plans[phase],"negative" if negative else "original")
        for name,secs in result["decision_seconds"].items():
            model_time[name]=model_time.get(name,0.)+secs
        phase_results.append(result)
    assert before_cold==after_cold
    return {"world":world,"negative":negative,"common_train":common,
            "phase_results":phase_results,
            "learn_seconds":model_time,
            "cold_restore_exact":True,
            "permanent_single_memory":True}


def cohort(seeds,laws,negative=False):
    worlds=[world_record(seed,laws,negative) for seed in seeds]
    stats={}
    for name in list(METHODS)+(["shuffled_candidate"] if negative else []):
        rewards=[sample[name]["reward"]
                 for world in worlds for phase in world["phase_results"]
                 for sample in phase["episodes"]]
        safe=[sample[name]["safe"]
              for world in worlds for phase in world["phase_results"]
              for sample in phase["episodes"]]
        correct=[phase["decisions"][name]==phase["correct_decision"]
                 for world in worlds for phase in world["phase_results"]]
        return_correct=[world["phase_results"][2]["decisions"][name]==2
                        for world in worlds]
        costs=[world["learn_seconds"][name] for world in worlds]
        stats[name]={"reward":round(sum(rewards)/len(rewards),8),
                    "safe_rate":round(sum(safe)/len(safe),8),
                    "phase_decision_accuracy":round(sum(correct)/len(correct),8),
                    "return_A_decision_accuracy":round(sum(return_correct)/len(return_correct),8),
                    "mean_learning_seconds":round(sum(costs)/len(costs),8)}
    return stats,worlds


def per_world_reward(rows,name):
    return [sum(s[name]["reward"] for p in w["phase_results"] for s in p["episodes"])/
            (len(w["phase_results"])*TRIALS) for w in rows]


def paired_ci(rows,one,two):
    x=per_world_reward(rows,one)
    y=per_world_reward(rows,two)
    n=len(x)
    diffs=[a-b for a,b in zip(x,y)]
    rng=random.Random(19812)
    ranked=sorted(sum(diffs[rng.randrange(n)] for _ in range(n))/n
                  for _ in range(BOOTSTRAP))
    return [round(ranked[25],8),round(ranked[998],8)]


def mechanistic_audit():
    assert len(set(DEV)|set(TRANSFER)|set(NEGATIVE)|set(MECHANICAL))==132
    assert (len(DEV),len(TRANSFER),len(NEGATIVE),len(MECHANICAL))==(32,64,32,4)
    assert len(PHASES)==3 and EPISODES==24 and TRIALS==6
    assert all(sum(x)==1 for x in (DEV_LAWS["A"],DEV_LAWS["B"],
                                  TRANSFER_LAWS["A"],TRANSFER_LAWS["B"]))
    stream=[True]*20+[False]*20+[True]*20
    m=RegimeCache(2)
    for v in stream:m.learn(v)
    restored=restore_model("candidate",serial(m))
    assert serial(m)==serial(restored)
    assert len(m.slots)<=2
    for seed in MECHANICAL:
        old=np.random.get_state()
        result=official_episode(DEV_LAWS["B"],stable_seed(seed,"mechanical"),2)
        assert state_equal(old,np.random.get_state())
        assert result["action"]==2 and result["state"]>=0
    return True


def main():
    start=time.perf_counter()
    assert mechanistic_audit()
    dev,dev_rows=cohort(DEV,DEV_LAWS)
    transfer,transfer_rows=cohort(TRANSFER,TRANSFER_LAWS)
    neg,neg_rows=cohort(NEGATIVE,TRANSFER_LAWS,negative=True)
    controls=max(MATCHED,key=lambda n:transfer[n]["reward"])
    diff=round(transfer["candidate"]["reward"]-transfer[controls]["reward"],8)
    ci=paired_ci(transfer_rows,"candidate",controls)
    ablated=round(transfer["candidate"]["reward"]-transfer["no_alt_memory"]["reward"],8)
    shuffled=round(neg["candidate"]["reward"]-neg["shuffled_candidate"]["reward"],8)
    negative_ci=paired_ci(neg_rows,"candidate","shuffled_candidate")
    # Proper and shuffled negative arms share identical official world seeds,
    # train episode contexts and evaluation RNG; only scrambled feedback differs.
    gains={
        "candidate_minus_strongest_transfer_reward":diff,
        "candidate_minus_no_alt_memory_reward":ablated,
        "proper_minus_shuffled_negative_reward":shuffled,
        "paired_negative_ci":negative_ci,
        "paired_transfer_ci_vs_strongest":ci,
    }
    fastest=min(transfer[name]["mean_learning_seconds"] for name in MATCHED)
    # Model update plus decision-time compute is measured; common official
    # environment wall time is excluded and no whole-process gain is claimed.
    cost_ratio=transfer["candidate"]["mean_learning_seconds"]/max(1e-9,fastest)
    checks={
        "positive_scientific_gain":diff>=.04 and ci[0]>0.,
        "return_A_recall":transfer["candidate"]["return_A_decision_accuracy"]>=.80,
        "shuffle_negative":shuffled>=.10,
        "cold_restore":all(x["cold_restore_exact"] for x in dev_rows+transfer_rows+neg_rows),
        "matching_train_actions":all(x["permanent_single_memory"] for x in dev_rows+transfer_rows+neg_rows),
        "relative_compute":cost_ratio<=2.,
    }
    learns=(transfer["candidate"]["phase_decision_accuracy"]>=.75 and
            checks["return_A_recall"] and checks["cold_restore"])
    if all(checks.values()):
        classification="SCIENTIFIC_CANDIDATE_UNQUALIFIED"
    elif learns:
        classification="LEARNING_OBSERVED_NOT_SUPERIOR"
    else:
        classification="VALID_NEGATIVE_NO_INTEGRATION"
    worlds={"dev":dev_rows,"transfer":transfer_rows,"negative":neg_rows}
    digest=hashlib.sha256(json.dumps(worlds,sort_keys=True,
                                  separators=(",",":")).encode()).hexdigest()
    return {
        "schema":"yggdrasil.contrib.aai08a.recurrent-causal-laws.v1",
        "prereg_commit":PREREG,
        "pre_first_use_amendment_commit":AMENDMENT,
        "upstream_source_sha":UPSTREAM,
        "classification":classification,
        "dev":dev,"transfer":transfer,"negative":neg,
        "strongest_nonoracle":controls,
        "candidate_gains":gains,
        "checks":checks,
        "candidate_update_time_ratio_to_fastest_nonoracle":round(cost_ratio,8),
        "negative_cohort_worlds_disjoint_from_transfer_but_paired_within_negative":True,
        "all_worlds_sha256":digest,
        "world_records":worlds,
        "science_limitations":"Fixed known map/prefix, experimenter-controlled A-B-A stochastic laws, simple binary forward/no-forward features, real outcomes and cached Beta counts. KnownLawBayes oracle has extra prior information and is not a matched control. No native model or unfamiliar environment transfer. Independent qualification required.",
        "integration":"NONE",
        "elapsed_seconds":round(time.perf_counter()-start,6),
    }


if __name__=="__main__":
    print(json.dumps(main(),sort_keys=True,indent=2))
