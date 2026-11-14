"""MD28 ShiftingRelay-v1: dynamic latent cause, charged information and decisions.

Only public observations pass to agents. Every physical action has a charged
step and observable consequence. Toy cohorts only; registered seeds guarded.
Pure stdlib Python 3.12 so independent of MiniGrid front-end architecture.
"""
import hashlib
import json
import math
import statistics
import time
from pathlib import Path

FREEZE="3b89e764ee859cc17ebaeea7bef6403cb770e3ea"
PARENT="9f9cc2e50837f60945694473f4ae51621a0b19e2"
TRAIN=tuple(range(1040001,1040241))
TOY=tuple(range(181,229))
COLD=tuple(range(229,241))
REGISTERED=tuple(range(1050001,1050097))
CONTEXTS=((0,0),(1,0),(1,1))
HOLDOUT=(0,1)
ARMS=("causal_adaptive","trained_factorized_adaptive_mle",
      "trained_joint_adaptive","trained_logistic_adaptive",
      "post_probe_always","pre_probe_skip_post_always","no_probe","oracle_public")
ACTIONS=("pre_probe","disturb","post_probe","apply_A","apply_B")
COST_PRE=.03
COST_DIST=.04
COST_POST=.20
COST_APPLY=.03
SUCCESS=1.
FAIL=-.5
DYNAMIC_PROB={0:.01,1:.5}


def canon(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True)


def randnum(seed,role):
    raw=hashlib.sha256(("ShiftingRelay-v1|"+str(seed)+"|"+role).encode()).digest()
    return int.from_bytes(raw[:8],"big")/2**64


def seeded_sign(seed,role):
    return 1 if randnum(seed,role)<.5 else -1


def signed_ratio(p,a):
    return -1 if p!=a else 1


def validate():
    x=json.loads(Path(__file__).with_name("prereg.json").read_text())
    d=x["data"]
    if (x["schema"]!="yggdrasil.dg1-md28-prereg.v1"
        or x["experiment_id"]!="DG1-MD28-20261114"
        or x["status"]!="PREREGISTRATION_ONLY_NO_TOY_OR_REGISTERED_RUN"
        or x["exact_parent_sha"]!=PARENT
        or d["training_seeds"]!=[1040001,1040240]
        or d["toy_eval_seeds"]!=[181,228]
        or d["cold_replay_seeds"]!=[229,240]
        or d["primary_seeds"]!=[1050001,1050096]
        or x["original_world"]["step_bound"]!=4
        or tuple(x["arms"])!=ARMS):
        raise AssertionError("MD28_PREREG_CUSTODY_DRIFT")
    cohorts=TRAIN+TOY+COLD+REGISTERED
    if len(cohorts)!=len(set(cohorts)):
        raise AssertionError("MD28_COHORT_OVERLAP")
    return x


def seed_fence(seed,role):
    allowed={"train":TRAIN,"toy":TOY,"cold":COLD}
    if role not in allowed or type(seed) is not int or seed not in allowed[role]:
        raise AssertionError("MD28_REGISTERED_FIRST_USE_FORBIDDEN_"+role)


class ShiftingRelay:
    def __init__(self,seed,context,polarity_override=None,flip_override=None):
        if context not in CONTEXTS+(HOLDOUT,):
            raise ValueError("MD28_INVALID_CONTEXT")
        self.context=tuple(context)
        self.hazard=seed%2
        self.goal=seeded_sign(seed,"goal")
        self._latent=(seeded_sign(seed,"polarity") if polarity_override is None
                      else polarity_override)
        if self._latent not in (-1,1):raise ValueError("MD28_BAD_POLARITY")
        self._will_flip=(randnum(seed,"physical_disturb")<DYNAMIC_PROB[self.hazard]
                         if flip_override is None else bool(flip_override))
        self.phase="start"
        self.pre_sign=None
        self.post_sign=None
        self.terminal_effect=None
        self.trace=[]
        self.total=0.
        self._disturbed=False

    def observe(self):
        return {"probe_wiring":self.context[0],
                "actuator_wiring":self.context[1],
                "hazard":self.hazard,
                "goal_sign":self.goal,
                "phase":self.phase,
                "pre_probe_effect":self.pre_sign,
                "post_probe_effect":self.post_sign,
                "terminal_effect":self.terminal_effect}

    def step(self,action):
        if action not in ACTIONS or self.phase=="done" or len(self.trace)>=4:
            raise AssertionError("MD28_ILLEGAL_OR_UNCHARGED_ACTION")
        before=self.observe()
        if action=="pre_probe":
            if self.phase!="start":raise AssertionError("MD28_INVALID_PRE_PROBE")
            self.pre_sign=self._latent*(-1 if self.context[0] else 1)
            self.phase="pre"
            reward=-COST_PRE
        elif action=="disturb":
            if self.phase not in ("start","pre"):raise AssertionError("MD28_DISTURB_ONCE")
            if self._will_flip:self._latent=-self._latent
            self._disturbed=True
            self.phase="disturbed"
            reward=-COST_DIST
        elif action=="post_probe":
            if self.phase!="disturbed":raise AssertionError("MD28_INVALID_POST_PROBE")
            self.post_sign=self._latent*(-1 if self.context[0] else 1)
            self.phase="post"
            reward=-COST_POST
        else:
            if self.phase not in ("disturbed","post"):
                raise AssertionError("MD28_TERMINAL_MUST_FOLLOW_DISTURBANCE")
            effect=self._latent*(-1 if self.context[1] else 1)
            if action=="apply_B":effect=-effect
            self.terminal_effect=effect
            reward=(SUCCESS if effect==self.goal else FAIL)-COST_APPLY
            self.phase="done"
        self.total=round(self.total+reward,8)
        after=self.observe()
        self.trace.append({"before":before,"action":action,"reward":round(reward,8),
                           "after":after})
        return after,round(reward,8),self.phase=="done"

    def receipt(self):
        if self.phase!="done":raise AssertionError("MD28_NONTERMINAL_RECEIPT")
        if not 2<=len(self.trace)<=4:raise AssertionError("MD28_PHYSICAL_BUDGET")
        if sum(x["action"]=="disturb" for x in self.trace)!=1:
            raise AssertionError("MD28_DISTURB_MISSING")
        return {"official_goal":int(self.terminal_effect==self.goal),
                "utility":self.total,"paid_steps":len(self.trace),
                "actions":[r["action"] for r in self.trace],
                "trace_sha256":hashlib.sha256(canon(self.trace).encode()).hexdigest(),
                "physical_trace":self.trace}


def teacher(seed,i):
    seed_fence(seed,"train")
    ctx=CONTEXTS[i%3]
    w=ShiftingRelay(seed,ctx)
    pre=w.step("pre_probe")[0]["pre_probe_effect"]
    w.step("disturb")
    post=w.step("post_probe")[0]["post_probe_effect"]
    action="apply_A" if i%2 else "apply_B"
    terminal=w.step(action)[0]["terminal_effect"]
    trace=w.receipt()
    if trace["paid_steps"]!=4:raise AssertionError("MD28_TRAIN_CHARGED_ACTIONS")
    relative=post*terminal*(1 if action=="apply_A" else -1)
    flip=int(pre!=post)
    if relative not in (-1,1):raise AssertionError("MD28_REAL_SIGN_INVALID")
    return {"context":ctx,"hazard":w.hazard,"relative_sign":relative,
            "physically_observed_flip":flip,
            "charged_steps":trace["paid_steps"],
            "trace_sha256":trace["trace_sha256"],
            "trace":trace["physical_trace"]}


def dataset():
    frozen=validate()
    rows=[teacher(s,i) for i,s in enumerate(TRAIN)]
    count={str(ctx)+":"+str(h):sum(r["context"]==ctx and r["hazard"]==h
                                      for r in rows)
           for ctx in CONTEXTS for h in (0,1)}
    if min(count.values())<frozen["frozen_gates"]["toy_train_real_coverage_min_per_pair_hazard"]:
        raise AssertionError("MD28_INSUFFICIENT_PUBLIC_TRAIN_COVERAGE")
    if sum(r["charged_steps"] for r in rows)!=960:
        raise AssertionError("MD28_CHARGED_TRAIN_MISMATCH")
    return rows,count,hashlib.sha256(canon(rows).encode()).hexdigest()


class Agent:
    def __init__(self,name):
        if name not in ARMS:raise ValueError("MD28_UNKNOWN_ARM")
        self.name=name
        self.cells={}
        self.flip_counts={0:{"n":0,"flips":0},1:{"n":0,"flips":0}}
        self.mle={"base":1,"probe":1,"actuator":1}
        self.logistic=[0.,0.,0.]
        self.n_training=0

    def train(self,rows):
        cells={}
        for r in rows:
            k="%d%d"%r["context"]
            cells.setdefault(k,[]).append(r["relative_sign"])
            f=self.flip_counts[r["hazard"]]
            f["n"]+=1
            f["flips"]+=r["physically_observed_flip"]
        self.cells={k:{"positive":sum(x==1 for x in arr),
                       "negative":sum(x==-1 for x in arr)}
                    for k,arr in sorted(cells.items())}
        self.n_training=len(rows)
        best=None
        for base in (-1,1):
            for probe in (-1,1):
                for act in (-1,1):
                    fit=sum(base*(probe if r["context"][0] else 1)*
                            (act if r["context"][1] else 1)==r["relative_sign"]
                            for r in rows)
                    result=(fit,base,probe,act)
                    if best is None or result>best:best=result
        self.mle={"base":best[1],"probe":best[2],"actuator":best[3]}
        w=[0.,0.,0.]
        for _ in range(120):
            gradient=[0.,0.,0.]
            for r in rows:
                x=(1.,float(r["context"][0]),float(r["context"][1]))
                y=r["relative_sign"]
                score=sum(a*b for a,b in zip(w,x))
                error=-y/(1.+math.exp(max(-60.,min(60.,y*score))))
                for i in range(3):gradient[i]+=error*x[i]
            w=[round(w[i]-.1*(gradient[i]/len(rows)+
                             (0 if i==0 else .01*w[i])),12) for i in range(3)]
        self.logistic=w

    def cell_sign(self,key):
        c=self.cells.get(key)
        if c is None:return None
        return 1 if c["positive"]>=c["negative"] else -1

    def relative_sign(self,p,a):
        name=self.name
        key="%d%d"%(p,a)
        if name=="oracle_public":
            return signed_ratio(p,a)
        # Give fixed-policy baselines the strongest learned factorization to
        # isolate diagnostic policy, not make them intentionally weak.
        if name in ("trained_factorized_adaptive_mle","post_probe_always",
                    "pre_probe_skip_post_always"):
            return self.mle["base"]*(self.mle["probe"] if p else 1)*(
                self.mle["actuator"] if a else 1)
        if name=="causal_adaptive":
            cell=self.cell_sign(key)
            if cell is not None:return cell
            signs=[self.cell_sign(k) for k in ("00","10","11")]
            if None in signs:raise AssertionError("MD28_CAUSAL_NOT_TRAINED")
            return math.prod(signs)
        if name=="trained_joint_adaptive":
            val=self.cell_sign(key)
            if val is not None:return val
            signs=[1]*self.cells["00"]["positive"]+[-1]*self.cells["00"]["negative"]
            # Equivalent to overall majority of complete physical training,
            # with no access to missing context.
            total=sum(c["positive"]-c["negative"] for c in self.cells.values())
            return 1 if total>=0 else -1
        if name=="trained_logistic_adaptive":
            w=self.logistic
            return 1 if (w[0]+w[1]*p+w[2]*a)>=0 else -1
        if name=="no_probe":return 1
        raise AssertionError("MD28_UNKNOWN_SIGN_POLICY")

    def flip_probability(self,h):
        if self.name=="oracle_public":return DYNAMIC_PROB[h]
        x=self.flip_counts[h]
        if not x["n"]:raise AssertionError("MD28_UNTRAINED_FLIP_PROBABILITY")
        return (x["flips"]+1)/(x["n"]+2)

    def strategy(self,obs):
        if self.name=="post_probe_always":return "post_only"
        if self.name=="pre_probe_skip_post_always":return "pre_only"
        if self.name=="no_probe":return "blind"
        p=self.flip_probability(obs["hazard"])
        error=min(p,1-p)
        pre_value=SUCCESS-COST_PRE-COST_DIST-COST_APPLY-(SUCCESS-FAIL)*error
        post_value=SUCCESS-COST_DIST-COST_POST-COST_APPLY
        return "pre_only" if pre_value>post_value else "post_only"

    def act(self,obs):
        phase=obs["phase"]
        if phase=="done":raise AssertionError("MD28_DECISION_AFTER_TERMINATION")
        mode=self.strategy(obs)
        if phase=="start":
            return "pre_probe" if mode=="pre_only" else "disturb"
        if phase=="pre":return "disturb"
        if phase=="disturbed" and mode=="post_only":return "post_probe"
        if phase=="disturbed" and mode=="pre_only":
            prior=obs["pre_probe_effect"]
            if prior not in (-1,1):raise AssertionError("MD28_UNPAID_PRE_INFO")
            p=self.flip_probability(obs["hazard"])
            # Predicted modal disturbance effect; rule is derived from learned
            # physical flip count and paid pre-probe sign.
            sensed=prior*(-1 if p>.5 else 1)
        elif phase=="post":
            sensed=obs["post_probe_effect"]
            if sensed not in (-1,1):raise AssertionError("MD28_UNPAID_POST_INFO")
        elif phase=="disturbed" and mode=="blind":
            sensed=None
        else:
            raise AssertionError("MD28_MISSING_PHYSICAL_PHASE")
        if sensed is None:
            predicted=1
        else:
            predicted=sensed*self.relative_sign(
                obs["probe_wiring"],obs["actuator_wiring"])
        return "apply_A" if predicted==obs["goal_sign"] else "apply_B"

    def checkpoint(self):
        d={"name":self.name,"cells":self.cells,"flip_counts":self.flip_counts,
           "mle":self.mle,"logistic":self.logistic,"n_training":self.n_training}
        b=canon(d).encode()
        if len(b)>16384:raise AssertionError("MD28_MODEL_TOO_LARGE")
        return b

    @classmethod
    def restore(cls,blob):
        d=json.loads(blob)
        m=cls(d["name"])
        for k in ("cells","mle","logistic","n_training"):
            setattr(m,k,d[k])
        m.flip_counts={int(k):v for k,v in d["flip_counts"].items()}
        if m.checkpoint()!=blob:raise AssertionError("MD28_CHECKPOINT_NOT_CANONICAL")
        return m


def fit(rows):
    models={n:Agent(n) for n in ARMS}
    for model in models.values():
        model.train(rows)
        if model.n_training!=len(rows):raise AssertionError("MD28_INCOMPLETE_BASELINE")
    return models


def evaluate(model,seeds,role):
    before=model.checkpoint()
    receipts=[]
    for seed in seeds:
        seed_fence(seed,role)
        w=ShiftingRelay(seed,HOLDOUT)
        total_ns=0
        while w.phase!="done":
            public=w.observe()
            t=time.perf_counter_ns()
            action=model.act(public)
            total_ns+=time.perf_counter_ns()-t
            obs,reward,done=w.step(action)
            if done!=(w.phase=="done"):raise AssertionError("MD28_ACTION_TERMINATION")
        x=w.receipt()
        x.update(seed=seed,hazard=w.hazard,decision_cpu_ns=total_ns)
        receipts.append(x)
    if model.checkpoint()!=before:raise AssertionError("MD28_HELDOUT_WEIGHT_CHANGE")
    return receipts


def summary(rows):
    return {"episodes":len(rows),"goals":sum(x["official_goal"] for x in rows),
            "mean_utility":round(statistics.mean(x["utility"] for x in rows),8),
            "paid_steps":sum(x["paid_steps"] for x in rows),
            "pre_probe_episodes":sum("pre_probe" in x["actions"] for x in rows),
            "post_probe_episodes":sum("post_probe" in x["actions"] for x in rows),
            "cpu_ns":sum(x["decision_cpu_ns"] for x in rows)}


def toy_study():
    x=validate()
    rows,coverage,train_hash=dataset()
    models=fit(rows)
    snapshots={name:m.checkpoint() for name,m in models.items()}
    for name,raw in snapshots.items():
        if Agent.restore(raw).checkpoint()!=raw:
            raise AssertionError("MD28_COLD_CHECKPOINT_INVALID")
    receipts={name:evaluate(model,TOY,"toy") for name,model in models.items()}
    scores={name:summary(v) for name,v in receipts.items()}
    candidate=receipts["causal_adaptive"]
    always_post=receipts["post_probe_always"]
    diff=lambda key:round(scores["causal_adaptive"]["mean_utility"]-
                          scores[key]["mean_utility"],8)
    strict=sum(c["utility"]>b["utility"]+1e-8
               for c,b in zip(candidate,always_post))
    before=evaluate(models["causal_adaptive"],COLD,"cold")
    after=evaluate(Agent.restore(snapshots["causal_adaptive"]),COLD,"cold")
    parity=all(a["trace_sha256"]==b["trace_sha256"]
               for a,b in zip(before,after))
    rules=x["frozen_gates"]
    gates={
      "teacher_coverage":min(coverage.values())>=rules["toy_train_real_coverage_min_per_pair_hazard"],
      "candidate_goals":scores["causal_adaptive"]["goals"]>=rules["candidate_toy_correct_interventions_min"],
      "post_probe_advantage":diff("post_probe_always")>=rules["candidate_toy_mean_utility_advantage_vs_post_probe_always_min"],
      "no_probe_advantage":diff("no_probe")>=rules["candidate_toy_mean_utility_advantage_vs_no_probe_min"],
      "strict_reward_wins":strict>=rules["candidate_toy_strict_reward_wins_vs_post_probe_always_min"],
      "low_hazard_pre":sum(x["hazard"]==0 and "pre_probe" in x["actions"] and
                          "post_probe" not in x["actions"] for x in candidate)>=rules["candidate_toy_low_hazard_pre_only_min"],
      "high_hazard_post":sum(x["hazard"]==1 and "post_probe" in x["actions"] and
                            "pre_probe" not in x["actions"] for x in candidate)>=rules["candidate_toy_high_hazard_post_only_min"],
      "factorized_mle_noninferior":-diff("trained_factorized_adaptive_mle")<=rules["candidate_toy_mean_utility_deficit_vs_trained_factorized_mle_max"],
      "oracle_noninferior":-diff("oracle_public")<=rules["candidate_toy_mean_utility_deficit_vs_oracle_max"],
      "cold_checkpoint_trace":parity,
      "real_paid_budget":all(2<=q["paid_steps"]<=4 and
                      len(q["actions"])==len(q["physical_trace"])==q["paid_steps"]
                      for arm in receipts.values() for q in arm),
      "identical_trained_dataset":all(m.n_training==240 for m in models.values())
    }
    if not all(gates.values()):
        classification="TOY_NO_GO_DO_NOT_CONSUME_REGISTERED_SEEDS"
    else:
        classification="TOY_READY_FOR_FURTHER_QUALIFICATION"
    return {"schema":"yggdrasil.dg1-md28-toy.v1",
            "classification":classification,"registered_seeds_used":False,
            "training":{"episodes":len(rows),"paid_steps":sum(z["charged_steps"] for z in rows),
                        "coverage":coverage,"sha256":train_hash},
            "toy_gates":gates,"strong_baseline_tie":diff("trained_factorized_adaptive_mle"),
            "advantage_over_post":diff("post_probe_always"),
            "advantage_over_no_probe":diff("no_probe"),
            "paired_strict_reward_wins":strict,"scores":scores,
            "cold_trace_parity":parity,
            "checkpoints":{name:hashlib.sha256(raw).hexdigest()
                           for name,raw in snapshots.items()},
            "physical_toy_traces":receipts}


if __name__=="__main__":
    print(canon(toy_study()))
