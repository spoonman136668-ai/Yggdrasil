"""DG1-MD27 CausalRelay-v1: consequential, paid action, identifiable causal transfer.

A separate original procedural simulator using Python standard library only.
All policies receive only the public observation dict and actual world.step
consequences. The environment never reveals _polarity to a policy. The strongest
control is a fully trained conventional factorized maximum-likelihood model.
No registered heldout seed is used by default or by any unit test.
"""
import hashlib
import json
import math
import statistics
import time
from pathlib import Path

PREREG_SHA="148e20fedcea143344a9c596dd84d7ebe8fa6c93"
EXACT_PARENT="66d2afffb1cdc7a00edbd4caa5c02302cf21224b"
ARMS=("causal_composition","trained_factorized_mle","trained_joint_lookup",
      "trained_logistic","probe_then_fixed","no_probe","oracle_public")
TRAIN_SEEDS=tuple(range(1020001,1020241))
TOY_SEEDS=tuple(range(121,145))
COLD_SEEDS=tuple(range(145,157))
REGISTERED=tuple(range(1030001,1030097))
TRAIN_CONTEXTS=((0,0),(1,0),(1,1))
HOLDOUT=(0,1)
VALID=("probe","apply_A","apply_B")
MAX_STEPS=2


def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True)


def sign(seed,role):
    digest=hashlib.sha256(("CausalRelay-v1:"+str(seed)+":"+role).encode()).digest()
    return 1 if digest[0]&1 else -1


def product(*args):
    out=1
    for a in args:out*=a
    return out


def validate():
    x=json.loads(Path(__file__).with_name("prereg.json").read_text())
    if (x["schema"]!="yggdrasil.dg1-md27-prereg.v1" or
        x["experiment_id"]!="DG1-MD27-20261114" or
        x["status"]!="PREREG_BEFORE_IMPLEMENTATION_AND_FIRST_USE" or
        x["parent_sha"]!=EXACT_PARENT or
        tuple(x["arms"])!=ARMS or
        x["world"]["training_seeds"]!=[1020001,1020240] or
        x["world"]["toy_eval_seeds"]!=[121,144] or
        x["world"]["cold_replay_seeds"]!=[145,156] or
        x["world"]["registered_eval_seeds"]!=[1030001,1030096] or
        x["world"]["context_holdout"]!=[0,1] or
        x["budgets"]["toy_episodes_per_arm"]!=24):
        raise AssertionError("MD27_FROZEN_PROTOCOL_DRIFT")
    all_s=TRAIN_SEEDS+TOY_SEEDS+COLD_SEEDS+REGISTERED
    if len(all_s)!=len(set(all_s)):
        raise AssertionError("MD27_COHORT_OVERLAP")
    return x


def seed_fence(seed,role):
    allowed={"train":TRAIN_SEEDS,"toy":TOY_SEEDS,"cold":COLD_SEEDS}
    if role not in allowed or type(seed) is not int or seed not in allowed[role]:
        raise AssertionError("MD27_REGISTERED_FIRSTUSE_FORBIDDEN_"+role)


class RelayWorld:
    """Three physically charged actions. Terminal interventions are irreversible."""
    def __init__(self,seed,context,forced_polarity=None):
        if context not in TRAIN_CONTEXTS+(HOLDOUT,):
            raise ValueError("MD27_INVALID_WIRING")
        self.context=tuple(context)
        self._polarity=sign(seed,"physical_polarity") if forced_polarity is None else forced_polarity
        if self._polarity not in (-1,1):raise ValueError("MD27_BAD_POLARITY")
        self.goal=sign(seed,"public_target")
        self.phase="start"
        self.probe_effect=None
        self.terminal_effect=None
        self.reward=0.
        self.paid=[]
        self.cumulative=0.

    def observe(self):
        # No identifier, seed, hidden polarity, actions' true effect or oracle.
        return {"probe_wiring":self.context[0],
                "actuator_wiring":self.context[1],
                "goal_sign":self.goal,
                "phase":self.phase,
                "probe_effect":self.probe_effect,
                "terminal_effect":self.terminal_effect}

    def step(self,action):
        if action not in VALID or self.phase=="done" or len(self.paid)>=MAX_STEPS:
            raise AssertionError("MD27_ILLEGAL_UNCHARGED_ACTION")
        before=self.observe()
        if action=="probe":
            if self.phase!="start":raise AssertionError("MD27_REPEATED_PROBE")
            self.probe_effect=self._polarity * (-1 if self.context[0] else 1)
            reward=-0.08
            self.phase="probed"
        else:
            self.terminal_effect=self._polarity * (-1 if self.context[1] else 1)
            if action=="apply_B":self.terminal_effect=-self.terminal_effect
            reward=round(-0.03+(1 if self.terminal_effect==self.goal else -0.4),8)
            self.phase="done"
        self.cumulative=round(self.cumulative+reward,8)
        after=self.observe()
        self.paid.append({"before":before,"action":action,"after":after,"reward":reward})
        return after,reward,self.phase=="done"

    def receipt(self):
        if self.phase!="done":raise AssertionError("MD27_UNFINISHED_PHYSICAL_EPISODE")
        trace=self.paid
        if len(trace) not in (1,2):raise AssertionError("MD27_PHYSICAL_BUDGET")
        return {"steps":len(trace),"goal_success":int(self.terminal_effect==self.goal),
                "utility":self.cumulative,
                "actions":[x["action"] for x in trace],
                "physical_trace_sha256":hashlib.sha256(canon(trace).encode()).hexdigest(),
                "trace":trace}


def train_teacher(seed,index):
    seed_fence(seed,"train")
    context=TRAIN_CONTEXTS[index%len(TRAIN_CONTEXTS)]
    env=RelayWorld(seed,context)
    initial=env.observe()
    probe,probe_reward,done=env.step("probe")
    if done:raise AssertionError("MD27_PROBE_TERMINAL")
    action="apply_A" if index%2==0 else "apply_B"
    terminal,reward,done=env.step(action)
    if not done:raise AssertionError("MD27_TEACHER_MISSING_ACTUATOR")
    receipt=env.receipt()
    if receipt["steps"]!=2 or len(receipt["trace"])!=2:
        raise AssertionError("MD27_TEACHER_ACTION_LEDGER")
    return {"context":list(context),"initial":initial,
            "probe_effect":probe["probe_effect"],"action":action,
            "terminal_effect":terminal["terminal_effect"],
            "goal_sign":initial["goal_sign"],
            "reward":receipt["utility"],"physical_trace_sha256":receipt["physical_trace_sha256"],
            "relative_sign":probe["probe_effect"]*terminal["terminal_effect"]*
                           (1 if action=="apply_A" else -1),
            "charged_steps":receipt["steps"]}


def train_dataset():
    x=validate()
    rows=[train_teacher(seed,i) for i,seed in enumerate(TRAIN_SEEDS)]
    by_context={str(c):sum(tuple(r["context"])==c for r in rows)
                for c in TRAIN_CONTEXTS}
    needed=x["toy_gates"]["per_training_context_real_probe_terminal_pairs_min"]
    if min(by_context.values())<needed or sum(r["charged_steps"] for r in rows)!=480:
        raise AssertionError("MD27_TEACHER_PHYSICAL_COVERAGE")
    digest=hashlib.sha256(canon(rows).encode()).hexdigest()
    return rows,by_context,digest


def majority(values):
    return 1 if sum(values)>=0 else -1


class Policy:
    """All arms share the same physical training data and action interface."""
    def __init__(self,name):
        if name not in ARMS:raise ValueError("MD27_BAD_ARM")
        self.name=name
        self.counts={}
        self.global_sign=1
        self.mle={"base":1,"probe_flip":1,"act_flip":1}
        self.logistic=[0.,0.,0.]
        self.trained_count=0

    def train(self,rows):
        # Exhaust complete shared physical outcomes, no hidden polarity labels.
        cells={}
        for row in rows:
            key="%d%d"%tuple(row["context"])
            cells.setdefault(key,[]).append(row["relative_sign"])
            if row["relative_sign"] not in (-1,1):
                raise AssertionError("MD27_BAD_PAID_EFFECT")
        self.counts={k:{"positive":sum(y==1 for y in v),
                        "negative":sum(y==-1 for y in v)}
                     for k,v in sorted(cells.items())}
        self.trained_count=len(rows)
        self.global_sign=majority([r["relative_sign"] for r in rows])
        base=majority(cells.get("00",[1]))
        scores=[]
        for probe_flip in (-1,1):
            for act_flip in (-1,1):
                correct=sum((base*
                             (probe_flip if r["context"][0] else 1)*
                             (act_flip if r["context"][1] else 1))==
                            r["relative_sign"] for r in rows)
                scores.append((correct,probe_flip,act_flip))
        best=max(scores)
        self.mle={"base":base,"probe_flip":best[1],"act_flip":best[2]}
        # Full-batch trained conventional logistic, no hand-coded XOR features.
        w=[0.,0.,0.]
        for epoch in range(120):
            grad=[0.,0.,0.]
            for row in rows:
                features=(1.,float(row["context"][0]),float(row["context"][1]))
                y=row["relative_sign"]
                score=sum(a*b for a,b in zip(w,features))
                mistake=-y/(1.+math.exp(max(-60.,min(60.,y*score))))
                for j in range(3):grad[j]+=mistake*features[j]
            w=[round(w[j]-0.1*(grad[j]/len(rows)+
                                (0 if j==0 else 0.01*w[j])),12)
               for j in range(3)]
        self.logistic=w

    def signed_cell(self,key):
        row=self.counts.get(key)
        if row is None:return None
        return 1 if row["positive"]>=row["negative"] else -1

    def predict_relative(self,probe_wire,act_wire):
        key="%d%d"%(probe_wire,act_wire)
        if self.name=="oracle_public":
            return -1 if probe_wire!=act_wire else 1
        if self.name=="trained_factorized_mle":
            return product(self.mle["base"],
                           self.mle["probe_flip"] if probe_wire else 1,
                           self.mle["act_flip"] if act_wire else 1)
        if self.name=="causal_composition":
            known=self.signed_cell(key)
            if known is not None:return known
            a,b,c=(self.signed_cell(x) for x in ("00","10","11"))
            if None in (a,b,c):return self.global_sign
            return a*b*c
        if self.name=="trained_joint_lookup":
            return self.signed_cell(key) or self.global_sign
        if self.name=="trained_logistic":
            w=self.logistic
            return 1 if w[0]+w[1]*probe_wire+w[2]*act_wire>=0 else -1
        return self.global_sign

    def act(self,public):
        phase=public["phase"]
        if phase=="done":raise AssertionError("MD27_POLICY_POST_TERMINAL")
        if phase=="start" and self.name!="no_probe":
            return "probe"
        if self.name=="no_probe":
            # Public goal alone cannot identify equiprobable hidden polarity.
            sign_a=1
        else:
            probe=public["probe_effect"]
            if probe not in (-1,1):
                raise AssertionError("MD27_HIDDEN_REGIME_MUST_BE_PROBED")
            sign_a=probe*self.predict_relative(
                public["probe_wiring"],public["actuator_wiring"])
        return "apply_A" if sign_a==public["goal_sign"] else "apply_B"

    def checkpoint(self):
        data={"name":self.name,"counts":self.counts,
              "global_sign":self.global_sign,"mle":self.mle,
              "logistic":self.logistic,"trained_count":self.trained_count}
        blob=canon(data).encode()
        if len(blob)>16384:raise AssertionError("MD27_CHECKPOINT_OVERSIZED")
        return blob

    @staticmethod
    def restore(blob):
        x=json.loads(blob)
        model=Policy(x["name"])
        for key in ("counts","global_sign","mle","logistic","trained_count"):
            setattr(model,key,x[key])
        if model.checkpoint()!=blob:raise AssertionError("MD27_NONCANONICAL_CHECKPOINT")
        return model


def fit_models(rows):
    models={}
    for name in ARMS:
        model=Policy(name)
        model.train(rows)
        if model.trained_count!=len(rows):
            raise AssertionError("MD27_UNDERTRAINED_CONTROL")
        models[name]=model
    return models


def physical_evaluation(model,seeds,role):
    before=model.checkpoint()
    rows=[]
    for seed in seeds:
        seed_fence(seed,role)
        env=RelayWorld(seed,HOLDOUT)
        decision_cpu_ns=0
        while env.phase!="done":
            obs=env.observe()
            t0=time.perf_counter_ns()
            action=model.act(obs)
            decision_cpu_ns+=time.perf_counter_ns()-t0
            after,reward,done=env.step(action)
            if done!= (env.phase=="done"):
                raise AssertionError("MD27_CHARGED_TERMINATION")
        receipt=env.receipt()
        receipt.update(seed=seed,decision_cpu_ns=decision_cpu_ns)
        rows.append(receipt)
    if model.checkpoint()!=before:
        raise AssertionError("MD27_PERSISTENT_HELDOUT_UPDATE_"+model.name)
    return rows


def eval_summary(rows):
    return {"episodes":len(rows),
            "official_goals":sum(x["goal_success"] for x in rows),
            "charged_steps":sum(x["steps"] for x in rows),
            "mean_utility":round(statistics.mean(x["utility"] for x in rows),8),
            "decision_cpu_ns":sum(x["decision_cpu_ns"] for x in rows),
            "actual_probe_actions":sum("probe" in x["actions"] for x in rows)}


def toy_study():
    frozen=validate()
    rows,coverage,sha=train_dataset()
    models=fit_models(rows)
    snapshots={n:p.checkpoint() for n,p in models.items()}
    for n,raw in snapshots.items():
        if Policy.restore(raw).checkpoint()!=raw:
            raise AssertionError("MD27_COLD_SNAPSHOT_DRIFT")
    scores={name:physical_evaluation(model,TOY_SEEDS,"toy")
            for name,model in models.items()}
    summary={n:eval_summary(v) for n,v in scores.items()}
    causal=scores["causal_composition"]
    lookup=scores["trained_joint_lookup"]
    nonprobe=scores["no_probe"]
    strongest=scores["trained_factorized_mle"]
    oracle=scores["oracle_public"]
    utility=lambda name:summary[name]["mean_utility"]
    paired_wins=sum(a["goal_success"]>b["goal_success"]
                    for a,b in zip(causal,lookup))
    diff=lambda name:round(utility("causal_composition")-utility(name),8)
    cold_original=physical_evaluation(models["causal_composition"],COLD_SEEDS,"cold")
    cold_loaded=physical_evaluation(Policy.restore(snapshots["causal_composition"]),
                                    COLD_SEEDS,"cold")
    stable=all(a["physical_trace_sha256"]==b["physical_trace_sha256"]
               for a,b in zip(cold_original,cold_loaded))
    toy=frozen["toy_gates"]
    gates={
      "trainer_physical_coverage":min(coverage.values())>=
          toy["per_training_context_real_probe_terminal_pairs_min"],
      "candidate_goals":summary["causal_composition"]["official_goals"]>=
          toy["candidate_success_min"],
      "joint_utility_advantage":diff("trained_joint_lookup")>=
          toy["candidate_mean_utility_margin_over_joint_min"],
      "no_probe_utility_advantage":diff("no_probe")>=
          toy["candidate_mean_utility_margin_over_no_probe_min"],
      "paired_goal_wins":paired_wins>=
          toy["candidate_strict_paired_goal_wins_vs_joint_min"],
      "trained_factorized_noninferiority":-diff("trained_factorized_mle")<=
          toy["candidate_mean_utility_deficit_vs_factorized_max"],
      "oracle_noninferiority":-diff("oracle_public")<=
          toy["candidate_mean_utility_deficit_vs_oracle_max"],
      "cold_checkpoint_and_trace":stable,
      "charged_action_ledger":all(all(x["steps"]==len(x["trace"]) and
            0<x["steps"]<=2 and
            x["actions"]==[t["action"] for t in x["trace"]]
            for x in score) for score in scores.values()),
      "all_controls_trained":all(model.trained_count==240
                                for model in models.values())
    }
    return {"schema":"yggdrasil.dg1-md27-toy.v1",
            "classification":("TOY_READY_FOR_FURTHER_QUALIFICATION"
                              if all(gates.values()) else "TOY_NO_GO"),
            "registered_seeds_touched":False,
            "train_teacher_episode_count":len(rows),
            "train_physical_steps":sum(r["charged_steps"] for r in rows),
            "teacher_coverage":coverage,"training_trace_sha256":sha,
            "toy_gates":gates,"by_arm":summary,
            "paired_goal_wins":paired_wins,
            "candidate_margin_over_joint":diff("trained_joint_lookup"),
            "candidate_margin_over_no_probe":diff("no_probe"),
            "candidate_margin_over_strong":diff("trained_factorized_mle"),
            "candidate_margin_over_oracle":diff("oracle_public"),
            "cold_exact_trace_parity":stable,
            "checkpoint_sha256":{k:hashlib.sha256(v).hexdigest()
                                  for k,v in snapshots.items()},
            "toy_episodes":scores}


if __name__=="__main__":
    print(canon(toy_study()))
