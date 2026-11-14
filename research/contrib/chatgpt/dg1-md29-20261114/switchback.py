"""MD29 SwitchbackRelay-v1: charged, two-stage causal interference study.

Original deterministic stdlib-only research simulator. Policies only access
public observation and physically charged action-effect transitions. Toy-only:
no registered first-use path. The strongest trained baseline uses factorized
maximum likelihood and a two-state Bayesian flip prediction.
"""
import hashlib
import itertools
import json
import math
import statistics
import time
from pathlib import Path

PREREG_SHA="401a70dd89f5989c8a32943804d856705c06e7f8"
PARENT="a50effb77d6b05d92207984344b9e8216db2aec1"
TRAIN_NORMAL=tuple(range(1060001,1060241))
TRAIN_INTERFERENCE=tuple(range(1061001,1061241))
TOY=tuple(range(201,233))
COLD=tuple(range(233,249))
RESERVED=tuple(range(1070001,1070097))
TRAIN_CONTEXTS=((0,0),(1,0),(1,1))
UNSEEN=(0,1)
ARMS=("regime_gated_memory","trained_factorized_bayes",
      "nongated_global_memory","trained_joint_regime",
      "trained_logistic_regime","always_stage2_probe",
      "never_stage2_probe","scripted_physics_ceiling")
ACTIONS=("probe","apply_A","apply_B")
PROBE_1=.04
PROBE_2=.16
APPLY_COST=.03
WIN=1.
LOSE=-.5
HAZARD={0:.01,1:.50}


def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True)


def random_unit(seed,label):
    d=hashlib.sha256(("SwitchbackRelay-v1|"+str(seed)+"|"+label).encode()).digest()
    return int.from_bytes(d[:8],"big")/(2**64)


def random_sign(seed,label):
    return 1 if random_unit(seed,label)<.5 else -1


def relative_physics(p,a,mode):
    return -1 if (p^a^mode) else 1


def protocol():
    x=json.loads(Path(__file__).with_name("prereg.json").read_text())
    w=x["world"];q=x["qualifications"]
    if (x["schema"]!="yggdrasil.dg1-md29-prereg.v1"
        or x["experiment_id"]!="DG1-MD29-20261114"
        or x["status"]!="PREREGISTERED_BEFORE_SOURCE_OR_TOY_FIRST_USE"
        or x["parent_sha"]!=PARENT
        or w["train_normal"]!=[1060001,1060240]
        or w["train_interference"]!=[1061001,1061240]
        or w["toy_heldout"]!=[201,232]
        or w["cold_replay"]!=[233,248]
        or w["registered_heldout_reserved"]!=[1070001,1070096]
        or tuple(x["arms"])!=ARMS
        or q["toy_training_actions_expected"]!=1920):
        raise AssertionError("MD29_FROZEN_PREREG_DRIFT")
    all_seed=TRAIN_NORMAL+TRAIN_INTERFERENCE+TOY+COLD+RESERVED
    if len(set(all_seed))!=len(all_seed):
        raise AssertionError("MD29_COHORT_OVERLAP")
    return x


def guard(seed,role):
    valid={"normal":TRAIN_NORMAL,"interference":TRAIN_INTERFERENCE,
           "toy":TOY,"cold":COLD}
    if role not in valid or type(seed) is not int or seed not in valid[role]:
        raise AssertionError("MD29_REGISTERED_SEED_USE_FORBIDDEN_"+role)


class Switchback:
    def __init__(self,seed,context,mode,latent_override=None,flip_override=None):
        if tuple(context) not in TRAIN_CONTEXTS+(UNSEEN,) or mode not in (0,1):
            raise ValueError("MD29_INVALID_CONTEXT_OR_MODE")
        self.context=tuple(context)
        self.mode=mode
        self.hazard=seed%2
        self.goal1=random_sign(seed,"goal1")
        self.goal2=random_sign(seed,"goal2")
        self._polarity=(random_sign(seed,"polarity") if latent_override is None
                        else latent_override)
        if self._polarity not in (-1,1):raise ValueError("MD29_BAD_HIDDEN_CAUSE")
        self._flip=(random_unit(seed,"change")<HAZARD[self.hazard]
                    if flip_override is None else bool(flip_override))
        self.phase="s1"
        self.probe1=None
        self.probe2=None
        self.effect1=None
        self.effect2=None
        self.action1=None
        self.ledger=[]
        self.total=0.

    def observe(self):
        return {"probe_wiring":self.context[0],
                "actuator_wiring":self.context[1],
                "interference_mode":self.mode,"flip_hazard":self.hazard,
                "stage":self.phase,"goal_sign":
                    self.goal1 if self.phase in ("s1","s1_probed") else self.goal2,
                "stage1_probe_effect":self.probe1,
                "stage1_actuator_effect":self.effect1,
                "stage1_action":self.action1,
                "stage2_probe_effect":self.probe2,
                "stage2_actuator_effect":self.effect2}

    def step(self,action):
        if (action not in ACTIONS or self.phase=="done" or
            len(self.ledger)>=4):
            raise AssertionError("MD29_ILLEGAL_OR_UNPAID_ACTION")
        before=self.observe()
        if action=="probe":
            if self.phase=="s1":
                self.probe1=self._polarity*(-1 if self.context[0] else 1)
                self.phase="s1_probed"
                reward=-PROBE_1
            elif self.phase=="s2":
                self.probe2=self._polarity*(-1 if self.context[0] else 1)
                self.phase="s2_probed"
                reward=-PROBE_2
            else:
                raise AssertionError("MD29_REPEAT_OR_INVALID_PHYSICAL_PROBE")
        else:
            if self.phase not in ("s1","s1_probed","s2","s2_probed"):
                raise AssertionError("MD29_INVALID_TERMINAL_ACTION")
            effect=self._polarity*(-1 if self.context[1]^self.mode else 1)
            if action=="apply_B":effect=-effect
            target=self.goal1 if self.phase in ("s1","s1_probed") else self.goal2
            reward=(WIN if effect==target else LOSE)-APPLY_COST
            if self.phase in ("s1","s1_probed"):
                self.effect1=effect
                self.action1=action
                if self._flip:self._polarity=-self._polarity
                self.phase="s2"
            else:
                self.effect2=effect
                self.phase="done"
        reward=round(reward,8)
        self.total=round(self.total+reward,8)
        after=self.observe()
        self.ledger.append({"before":before,"action":action,"after":after,
                            "reward":reward})
        return after,reward,self.phase=="done"

    def receipt(self):
        if self.phase!="done" or not 2<=len(self.ledger)<=4:
            raise AssertionError("MD29_MISSING_CHARGED_TWO_STAGE_TERMINATION")
        actions=[row["action"] for row in self.ledger]
        if sum(x!="probe" for x in actions)!=2:
            raise AssertionError("MD29_ACTION_CUSTODY_INCOMPLETE")
        stage1=(self.ledger[-1]["after"]["stage1_actuator_effect"]
                ==self.goal1)
        stage2=self.effect2==self.goal2
        return {"goals":int(stage1)+int(stage2),
                "net_utility":self.total,"paid_steps":len(self.ledger),
                "actions":actions,"physical_sha256":
                    hashlib.sha256(canon(self.ledger).encode()).hexdigest(),
                "trace":self.ledger}


def teacher(seed,index,mode):
    guard(seed,"normal" if mode==0 else "interference")
    context=TRAIN_CONTEXTS[index%3]
    env=Switchback(seed,context,mode)
    p1=env.step("probe")[0]["stage1_probe_effect"]
    a1="apply_A" if index%2 else "apply_B"
    eff1=env.step(a1)[0]["stage1_actuator_effect"]
    p2=env.step("probe")[0]["stage2_probe_effect"]
    a2="apply_B" if index%2 else "apply_A"
    eff2=env.step(a2)[0]["stage2_actuator_effect"]
    rec=env.receipt()
    if rec["paid_steps"]!=4:raise AssertionError("MD29_TRAIN_UNCHARGED")
    return {"mode":mode,"context":context,"hazard":env.hazard,
            "signed_observations":(
                p1*eff1*(1 if a1=="apply_A" else -1),
                p2*eff2*(1 if a2=="apply_A" else -1)),
            "observed_flip":int(p1!=p2),
            "physical_sha256":rec["physical_sha256"],
            "paid_steps":rec["paid_steps"],
            "raw_public_trace":rec["trace"]}


def dataset():
    spec=protocol()
    normal=[teacher(seed,i,0) for i,seed in enumerate(TRAIN_NORMAL)]
    opposite=[teacher(seed,i,1) for i,seed in enumerate(TRAIN_INTERFERENCE)]
    rows=normal+opposite
    coverage={str((mode,context,ha)):
              sum(row["mode"]==mode and row["context"]==context
                  and row["hazard"]==ha for row in rows)
              for mode in (0,1) for context in TRAIN_CONTEXTS for ha in (0,1)}
    if (min(coverage.values())<spec["qualifications"]["toy_training_context_mode_pairs_min"]
        or sum(x["paid_steps"] for x in rows)!=1920):
        raise AssertionError("MD29_PHYSICAL_TRAIN_COVERAGE")
    return rows,coverage,hashlib.sha256(canon(rows).encode()).hexdigest()


def majority(v):
    return 1 if sum(v)>=0 else -1


class Memory:
    """Comparable 2-state Bayesian and regime-gated event-memory policies."""
    def __init__(self,name):
        if name not in ARMS:raise ValueError("MD29_UNKNOWN_ARM")
        self.name=name
        self.regime_cells={}
        self.global_cells={}
        self.hazard_counts={0:{"n":0,"flipped":0},1:{"n":0,"flipped":0}}
        self.strong={"base":1,"probe":1,"act":1,"mode":1}
        self.logistic={0:[0.,0.,0.],1:[0.,0.,0.]}
        self.trained_rows=0
        self.normal_before_interference=None

    def learned_sign(self,mode,key):
        obj=self.regime_cells.get(mode,{}).get(key)
        if obj is None:return None
        return 1 if obj["positive"]>=obj["negative"] else -1

    def train(self,rows):
        # Training is sequential: normal then contradictory interference.
        pairs={0:{},1:{}}
        aggregated={}
        experiences=[]
        for i,row in enumerate(rows):
            mode=row["mode"]
            key="%d%d"%row["context"]
            pairs[mode].setdefault(key,[]).extend(row["signed_observations"])
            aggregated.setdefault(key,[]).extend(row["signed_observations"])
            self.hazard_counts[row["hazard"]]["n"]+=1
            self.hazard_counts[row["hazard"]]["flipped"]+=row["observed_flip"]
            experiences.extend([(mode,row["context"],s) for s in row["signed_observations"]])
            if i==239:
                self.normal_before_interference={
                    k:majority(v) for k,v in pairs[0].items()}
        self.regime_cells={
            mode:{k:{"positive":sum(s==1 for s in values),
                     "negative":sum(s==-1 for s in values)}
                  for k,values in sorted(cells.items())}
            for mode,cells in pairs.items()}
        self.global_cells={k:{"positive":sum(s==1 for s in arr),
                              "negative":sum(s==-1 for s in arr)}
                           for k,arr in sorted(aggregated.items())}
        self.trained_rows=len(rows)
        # Strongest conventional model exhaustively fits all 16 possible
        # signed factor models from the SAME physical observations.
        best=None
        for base,pf,af,mf in itertools.product((-1,1),repeat=4):
            correct=sum(base*(pf if p else 1)*(af if a else 1)*
                        (mf if mode else 1)==s
                        for mode,(p,a),s in experiences)
            x=(correct,base,pf,af,mf)
            if best is None or x>best:best=x
        self.strong={"base":best[1],"probe":best[2],"act":best[3],
                     "mode":best[4]}
        for mode in (0,1):
            data=[(c,s) for mod,c,s in experiences if mod==mode]
            w=[0.,0.,0.]
            for _ in range(120):
                g=[0.,0.,0.]
                for (p,a),s in data:
                    f=(1.,float(p),float(a))
                    score=sum(v*t for v,t in zip(w,f))
                    e=-s/(1.+math.exp(max(-60.,min(60.,s*score))))
                    for j in range(3):g[j]+=e*f[j]
                w=[round(w[j]-.1*(g[j]/len(data)+
                                 (0 if j==0 else .01*w[j])),12)
                   for j in range(3)]
            self.logistic[mode]=w

    def relative(self,mode,p,a):
        k="%d%d"%(p,a)
        if self.name=="scripted_physics_ceiling":
            return relative_physics(p,a,mode)
        if self.name in ("trained_factorized_bayes","always_stage2_probe",
                         "never_stage2_probe"):
            f=self.strong
            return f["base"]*(f["probe"] if p else 1)*(
                f["act"] if a else 1)*(f["mode"] if mode else 1)
        if self.name=="regime_gated_memory":
            matched=self.learned_sign(mode,k)
            if matched is not None:return matched
            v=[self.learned_sign(mode,key) for key in ("00","10","11")]
            if None in v:raise AssertionError("MD29_INSUFFICIENT_GATED_MEMORY")
            return math.prod(v)
        if self.name=="nongated_global_memory":
            v=[]
            for key in ("00","10","11"):
                o=self.global_cells[key]
                v.append(1 if o["positive"]>=o["negative"] else -1)
            return math.prod(v)
        if self.name=="trained_joint_regime":
            answer=self.learned_sign(mode,k)
            if answer is not None:return answer
            total=sum(x["positive"]-x["negative"]
                      for x in self.regime_cells[mode].values())
            return 1 if total>=0 else -1
        if self.name=="trained_logistic_regime":
            w=self.logistic[mode]
            return 1 if w[0]+w[1]*p+w[2]*a>=0 else -1
        raise ValueError("MD29_POLICY_NOT_FOUND")

    def flip_rate(self,h):
        if self.name=="scripted_physics_ceiling":return HAZARD[h]
        d=self.hazard_counts[h]
        if not d["n"]:raise AssertionError("MD29_HAZARD_UNTRAINED")
        return (d["flipped"]+1)/(d["n"]+2)

    def requires_stage2_probe(self,obs):
        if self.name=="always_stage2_probe":return True
        if self.name=="never_stage2_probe":return False
        # True two-state Bayesian action policy: compute best posterior modal
        # sign for a non-probed stage2 and its expected loss, then compare
        # to physical paid post-probe cost.
        flip=self.flip_rate(obs["flip_hazard"])
        miss=min(flip,1-flip)
        cost_missed=(WIN-LOSE)*miss
        return cost_missed>PROBE_2

    def act(self,obs):
        phase=obs["stage"]
        if phase=="done":raise AssertionError("MD29_POST_TERMINAL_POLICY")
        if phase=="s1":return "probe"
        if phase=="s2" and self.requires_stage2_probe(obs):
            return "probe"
        if phase in ("s1_probed","s2_probed"):
            sign_seen=(obs["stage1_probe_effect"] if phase=="s1_probed"
                       else obs["stage2_probe_effect"])
            if sign_seen not in (-1,1):
                raise AssertionError("MD29_NO_UNPAID_CAUSAL_EVIDENCE")
            predicted=sign_seen*self.relative(
                obs["interference_mode"],obs["probe_wiring"],
                obs["actuator_wiring"])
        elif phase=="s2":
            effect=obs["stage1_actuator_effect"]
            action=obs["stage1_action"]
            if effect not in (-1,1) or action not in ("apply_A","apply_B"):
                raise AssertionError("MD29_NO_STAGE1_PAID_ACTUATOR_EVIDENCE")
            predicted=effect*(1 if action=="apply_A" else -1)
            if self.flip_rate(obs["flip_hazard"])>.5:predicted=-predicted
        else:
            raise AssertionError("MD29_INVALID_POLICY_STAGE")
        return "apply_A" if predicted==obs["goal_sign"] else "apply_B"

    def checkpoint(self):
        x={"name":self.name,"regime_cells":self.regime_cells,
           "global_cells":self.global_cells,"hazard_counts":self.hazard_counts,
           "strong":self.strong,"logistic":self.logistic,
           "trained_rows":self.trained_rows,
           "normal_before_interference":self.normal_before_interference}
        b=canon(x).encode()
        if len(b)>16384:raise AssertionError("MD29_CHECKPOINT_SIZE")
        return b

    @classmethod
    def restore(cls,blob):
        x=json.loads(blob)
        m=cls(x["name"])
        for k in ("global_cells","strong","trained_rows",
                  "normal_before_interference"):
            setattr(m,k,x[k])
        m.regime_cells={int(k):v for k,v in x["regime_cells"].items()}
        m.hazard_counts={int(k):v for k,v in x["hazard_counts"].items()}
        m.logistic={int(k):v for k,v in x["logistic"].items()}
        if m.checkpoint()!=blob:
            raise AssertionError("MD29_COLD_RESTORE_MISMATCH")
        return m


def fit(rows):
    models={name:Memory(name) for name in ARMS}
    for m in models.values():
        m.train(rows)
        if m.trained_rows!=480:raise AssertionError("MD29_UNTRAINED_STRONG_CONTROL")
    return models


def execute(m,seeds,role):
    frozen=m.checkpoint()
    receipts=[]
    for seed in seeds:
        guard(seed,role)
        mode=(seed//2)%2
        w=Switchback(seed,UNSEEN,mode)
        decision_ns=0
        while w.phase!="done":
            obs=w.observe()
            start=time.perf_counter_ns()
            action=m.act(obs)
            decision_ns+=time.perf_counter_ns()-start
            after,reward,done=w.step(action)
            if done!=(w.phase=="done"):
                raise AssertionError("MD29_TERMINAL_ACCOUNTING_DRIFT")
        x=w.receipt()
        x.update(seed=seed,mode=mode,hazard=w.hazard,
                 decision_cpu_ns=decision_ns)
        receipts.append(x)
    if m.checkpoint()!=frozen:
        raise AssertionError("MD29_HELDOUT_MUTATED_PERSISTENT_MODEL")
    return receipts


def score(rows):
    return {"episodes":len(rows),
            "goals":sum(x["goals"] for x in rows),
            "mean_net_utility":round(statistics.mean(x["net_utility"] for x in rows),8),
            "paid_steps":sum(x["paid_steps"] for x in rows),
            "stage2_probes":sum(x["actions"].count("probe")==2 for x in rows),
            "total_decision_cpu_ns":sum(x["decision_cpu_ns"] for x in rows)}


def toy_study():
    frozen=protocol()
    rows,coverage,train_hash=dataset()
    models=fit(rows)
    snapshots={name:m.checkpoint() for name,m in models.items()}
    if any(Memory.restore(blob).checkpoint()!=blob for blob in snapshots.values()):
        raise AssertionError("MD29_COLD_CHECKPOINT_PARITY")
    all_rec={name:execute(model,TOY,"toy") for name,model in models.items()}
    scores={name:score(receipts) for name,receipts in all_rec.items()}
    control=all_rec["nongated_global_memory"]
    main=all_rec["regime_gated_memory"]
    strict=sum(x["net_utility"]>y["net_utility"]+1e-8
               for x,y in zip(main,control))
    def diff(other):
        return round(scores["regime_gated_memory"]["mean_net_utility"]-
                     scores[other]["mean_net_utility"],8)
    cold1=execute(models["regime_gated_memory"],COLD,"cold")
    cold2=execute(Memory.restore(snapshots["regime_gated_memory"]),COLD,"cold")
    cold_ok=all(a["physical_sha256"]==b["physical_sha256"]
                for a,b in zip(cold1,cold2))
    test=frozen["qualifications"]
    low_count=sum(x["hazard"]==0 and x["actions"].count("probe")==1 for x in main)
    high_count=sum(x["hazard"]==1 and x["actions"].count("probe")==2 for x in main)
    gates={
        "training_coverage":min(coverage.values())>=test["toy_training_context_mode_pairs_min"],
        "training_real_actions":sum(x["paid_steps"] for x in rows)==test["toy_training_actions_expected"],
        "heldout_successes":scores["regime_gated_memory"]["goals"]>=test["toy_candidate_correct_terminal_actions_min"],
        "beats_interference_ablation":diff("nongated_global_memory")>=test["toy_candidate_mean_utility_advantage_over_nongated_min"],
        "beats_always_reprobe":diff("always_stage2_probe")>=test["toy_candidate_mean_utility_advantage_over_always_stage2_probe_min"],
        "beats_never_reprobe":diff("never_stage2_probe")>=test["toy_candidate_mean_utility_advantage_over_never_stage2_probe_min"],
        "noninferior_strong":-diff("trained_factorized_bayes")<=test["toy_candidate_mean_utility_deficit_vs_strong_max"],
        "noninferior_oracle":-diff("scripted_physics_ceiling")<=test["toy_candidate_mean_utility_deficit_vs_oracle_max"],
        "strict_paired_interference_wins":strict>=test["toy_candidate_strict_paired_reward_wins_over_nongated_min"],
        "low_hazard_skips_post":low_count>=test["toy_candidate_real_low_hazard_skip_probe_min"],
        "high_hazard_pays_post":high_count>=test["toy_candidate_real_high_hazard_use_probe_min"],
        "cold_checkpoint_action_reward":cold_ok,
        "all_arm_full_training":all(m.trained_rows==480 for m in models.values()),
        "charged_action_ledger":all(2<=x["paid_steps"]<=4 and
            x["paid_steps"]==len(x["actions"])==len(x["trace"])
            for r in all_rec.values() for x in r)
    }
    original=frozen["novel_mechanism_gate"]
    novelty={
        "strong_gain":diff("trained_factorized_bayes")>=original["candidate_mean_utility_margin_over_strong_min"],
        "strong_strict_reward_wins":sum(x["net_utility"]>y["net_utility"]+1e-8
            for x,y in zip(main,all_rec["trained_factorized_bayes"]))>=
            original["candidate_strict_paired_episode_reward_wins_over_strong_min"]
    }
    if not all(gates.values()):
        status="TOY_NO_GO"
    elif not all(novelty.values()):
        status="DEVELOPMENT_VALID_TASK_NO_NOVEL_GAIN"
    else:
        status="TOY_NOVELTY_CANDIDATE_PENDING_INDEPENDENT_QUALIFICATION"
    return {"schema":"yggdrasil.dg1-md29-toy.v1",
            "classification":status,"registered_firstuse_executed":False,
            "training":{"episodes":len(rows),"paid_steps":sum(x["paid_steps"] for x in rows),
                        "coverage":coverage,"physical_sha256":train_hash},
            "frozen_task_gates":gates,"frozen_novelty_gates":novelty,
            "strong_baseline_mean_gain":diff("trained_factorized_bayes"),
            "nongated_ablation_mean_gain":diff("nongated_global_memory"),
            "always_reprobe_mean_gain":diff("always_stage2_probe"),
            "never_reprobe_mean_gain":diff("never_stage2_probe"),
            "paired_nongated_strict_wins":strict,
            "cold_trace_parity":cold_ok,
            "scores":scores,
            "checkpoint_sha256":{name:hashlib.sha256(blob).hexdigest()
                                  for name,blob in snapshots.items()},
            "physical_toy_episodes":all_rec}


if __name__=="__main__":
    print(canon(toy_study()))
