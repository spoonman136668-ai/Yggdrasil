#!/usr/bin/env python3
"""CS06 original POPGym CountRecallHard: prospectively bounded public memory audit.

Only original reset/step, public observation and reward are exposed. The original
source returns privileged info["counts"]; it is deliberately discarded and is
never supplied to any learner or used to construct training labels.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import time

FIRST="ff46052e70a8f74f977a2c3bffee90494b8e0a16"
PIN="410d5aa626dae8024f498354d8781a0d1870c399"
BLOBS={
"popgym/envs/count_recall.py":"48dee2a5ca400021582cdf8638bb5c500d021f00",
"popgym/core/deck.py":"12bcabfa9a96fd1261809ef0a446c74d3f3bfa86",
"popgym/core/env.py":"26a20ba3531730b76e135f48e8fc25bb6b620984",
"pyproject.toml":"20bd0e278a519452d66c57f2fbbff58fdcdce5c8"}
REPS=(0,1,2)
N={"FIT":16,"VALID":8,"DEV":16}
STEPS=207
SYMBOLS=13
ACTION_LIMIT=16
ALPHAS=(0.0,.25,.5,.75,1.0)
CANDIDATE="fit_learned_recurrent_retention_alpha"
COUNTER="conventional_exact_public_counter"
BLIND="fit_trained_current_query_and_elapsed"
RECENT="conventional_last_eight_public_symbols"
ERASED="learned_alpha_midway_state_erased"
ZERO="fixed_zero"
ARMS=(CANDIDATE,COUNTER,BLIND,RECENT,ERASED,ZERO)

def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def canonical(x):
    return json.dumps(x,separators=(",",":"),sort_keys=True,allow_nan=False)
def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()
def seed(role,rep,i):
    return {"FIT":1110000,"VALID":1120000,"DEV":1130000}[role]+rep*1000+i
def original_source(root):
    def call(args):
        r=subprocess.run(args,text=True,capture_output=True,cwd=root,timeout=25)
        return r.returncode,r.stdout.strip()
    c,s=call(["git","rev-parse","HEAD"])
    require(c==0 and s==PIN,"ORIGINAL_POPGYM_HEAD_DRIFT")
    for name,sha in BLOBS.items():
        c,s=call(["git","hash-object","--",name])
        require(c==0 and s==sha,"ORIGINAL_POPGYM_BLOB_DRIFT:"+name)
    c,_=call(["git","diff","--exit-code","--","popgym","pyproject.toml"])
    require(c==0,"ORIGINAL_UPSTREAM_SOURCE_TRACKED_DIFF")
    return {"source":"proroklab/popgym","git_sha":PIN,"original_git_blobs":BLOBS}
def public_obs(obs):
    """Original two-element public dealt/query rank only. Never private info."""
    import numpy as np
    a=np.asarray(obs)
    require(a.shape==(2,) and np.issubdtype(a.dtype,np.integer),
            "ORIGINAL_PUBLIC_OBSERVATION_INVALID")
    dealt,query=(int(x) for x in a)
    require(0<=dealt<SYMBOLS and 0<=query<SYMBOLS,
            "ORIGINAL_PUBLIC_RANK_OUT_OF_RANGE")
    return dealt,query
class RecurrentAlpha:
    def __init__(self,alpha):
        self.alpha=float(alpha)
        self.history=[0.0]*SYMBOLS
    def observe(self,dealt,step):
        for j in range(SYMBOLS):
            self.history[j]*=self.alpha
        self.history[dealt]+=1.0
    def act(self,query,step):
        return min(ACTION_LIMIT,max(0,int(self.history[query]+0.5)))
class ExactCounter:
    def __init__(self):
        self.history=[0]*SYMBOLS
    def observe(self,dealt,step):
        self.history[dealt]+=1
    def act(self,query,step):
        return min(ACTION_LIMIT,self.history[query])
class RecentEight:
    def __init__(self):
        self.history=collections.deque(maxlen=8)
    def observe(self,dealt,step):
        self.history.append(dealt)
    def act(self,query,step):
        return sum(v==query for v in self.history)
class BlindedMarginal:
    def __init__(self,cell_models):
        self.cell_models=cell_models
    def observe(self,dealt,step):pass
    def act(self,query,step):
        # Public query and time only; never even current dealt rank.
        cell=(query,step//32)
        if cell not in self.cell_models:
            return 0
        return self.cell_models[cell]
class Zero:
    def observe(self,dealt,step):pass
    def act(self,query,step):return 0
class AlphaErasure(RecurrentAlpha):
    def observe(self,dealt,step):
        if step==104:
            self.history=[0.0]*SYMBOLS
        super().observe(dealt,step)

def source_episode(Source,episode_seed,policy,label_fit=False):
    """Execute original source, returns public-only observed trace and source reward.

    Never pass returned reset/step info to policy or fitting. An independent
    observation-prefix counter checks reward sign; never env.get_state().
    """
    source=Source()
    try:
        raw,_excluded_reset_info=source.reset(seed=episode_seed)
        current=public_obs(raw)
        public_prefix=[0]*SYMBOLS
        raw_episodes=[]
        successes=0
        reward_sum=0.0
        total_steps=0
        for t in range(STEPS):
            dealt,query=current
            public_prefix[dealt]+=1
            policy.observe(dealt,t)
            label=public_prefix[query] # prefix-only self-supervision
            require(0<=label<=ACTION_LIMIT,"PUBLIC_PREFIX_LABEL_ILLEGAL")
            action=policy.act(query,t)
            require(type(action) is int and 0<=action<=ACTION_LIMIT,
                    "ILLEGAL_ORIGINAL_SOURCE_ACTION")
            nxt,r,term,trunc,_excluded_private_info=source.step(action)
            total_steps+=1
            expected_reward=(1 if action==label else -1)/STEPS
            require(abs(float(r)-expected_reward)<1e-9,
                    "ORIGINAL_SOURCE_REWARD_PUBLIC_HISTORY_DISAGREEMENT")
            require(bool(term)==(t==STEPS-1) and not bool(trunc),
                    "ORIGINAL_SOURCE_EPISODE_TERMINATION_DRIFT")
            good=int(action==label)
            successes+=good
            reward_sum+=float(r)
            if label_fit:
                raw_episodes.append({"t":t,"dealt":dealt,"query":query,
                                     "public_prefix_count_label":label,
                                     "action":action,"source_reward":float(r)})
            current=public_obs(nxt)
        require(total_steps==STEPS,"ORIGINAL_SOURCE_DECISION_BUDGET_DRIFT")
        return {"seed":episode_seed,"correct_actions":successes,
                "source_reward_sum":reward_sum,"source_action_calls":total_steps,
                "public_trace":raw_episodes}
    finally:
        source.close()
def fit_public(FIT,rep):
    traces=[]
    for i in range(N["FIT"]):
        episode=source_episode(FIT,seed("FIT",rep,i),Zero(),True)
        require(len(episode["public_trace"])==STEPS,"FIT_TRACE_TRUNCATED")
        traces.append(episode)
    labels=[x for ep in traces for x in ep["public_trace"]]
    counts=collections.defaultdict(lambda:collections.Counter())
    for rec in labels:
        counts[(rec["query"],rec["t"]//32)][rec["public_prefix_count_label"]]+=1
    marginal={}
    for cell,hist in counts.items():
        # Laplace+1 tie break to smallest legal count; equates maximization
        marginal[cell]=max(range(17),key=lambda i:(hist[i]+1,-i))
    sse={}
    for alpha in ALPHAS:
        err=0.
        k=0
        for ep in traces:
            mem=[0.0]*SYMBOLS
            for r in ep["public_trace"]:
                for j in range(SYMBOLS):mem[j]*=alpha
                mem[r["dealt"]]+=1
                delta=mem[r["query"]]-r["public_prefix_count_label"]
                err+=delta*delta;k+=1
        require(k==N["FIT"]*STEPS,"ALPHA_FIT_HISTORY_INVALID")
        sse[str(alpha)]=float(err)
    selected=min(ALPHAS,key=lambda x:(sse[str(x)],x))
    require(selected in ALPHAS,"LEARNED_ALPHA_NOT_FROZEN_CANDIDATE")
    return traces,selected,sse,marginal
def policy_for(name,alpha,marginal):
    if name==CANDIDATE:return RecurrentAlpha(alpha)
    if name==COUNTER:return ExactCounter()
    if name==BLIND:return BlindedMarginal(marginal)
    if name==RECENT:return RecentEight()
    if name==ERASED:return AlphaErasure(alpha)
    if name==ZERO:return Zero()
    raise RuntimeError("UNKNOWN_ARM")
def score(Source,role,rep,alpha,marginal):
    n=N[role]
    values={}
    for name in ARMS:
        cnt=0;returns=0.;actions=0;cpu=0
        hash_obj=hashlib.sha256()
        for i in range(n):
            t0=time.process_time_ns()
            result=source_episode(Source,seed(role,rep,i),policy_for(name,alpha,marginal))
            cpu+=time.process_time_ns()-t0
            cnt+=result["correct_actions"]
            returns+=result["source_reward_sum"]
            actions+=result["source_action_calls"]
            hash_obj.update((canonical(result)+"\n").encode())
        require(actions==n*STEPS,"INVALID_SCORED_SOURCE_BUDGET")
        values[name]={"episodes":n,"source_native_action_calls":actions,
                      "correct_count_predictions":cnt,"accuracy":cnt/actions,
                      "source_reward_sum":returns,"process_cpu_ns_with_original_source":cpu,
                      "result_trace_sha256":hash_obj.hexdigest()}
    return values
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"mass.cs06.original_popgym_public_prefix_retention.v1",
      "frozen_FIRST_prereg_sha":FIRST,"original_upstream_source_sha":PIN,
      "source_role":"PUBLIC_DEVELOPMENT_ONLY",
      "reset_step_info_is_privileged_and_not_used":True,
      "FIT_labels_from_public_prefix_only":True,
      "retention_structure_hand_specified":True,
      "fitted_retention_coefficient_not_native_learned_memory_formation":True,
      "actual_native_yggdrasil_or_wingless_learner_used":False,
      "protected_heldout_or_scientific_first_use":False,
      "independent_unfamiliar_family_transfer_tested":False,
      "model_cpu_and_RSS_completely_matched":False,
      "disposition":"PUBLIC_CS06_INVALID_OR_INFO_LEAK",
      "replicas":[]}
    raw={"schema":"mass.cs06.shared_public_fit_observations.v1","replicas":[]}
    try:
        root=Path(args.upstream).resolve()
        receipt["original_source"]=original_source(root)
        from popgym.envs.count_recall import CountRecallHard
        import inspect
        require(Path(inspect.getfile(CountRecallHard)).resolve()==root/"popgym"/"envs"/"count_recall.py",
                "NOT_ORIGINAL_SOURCE_ENV_CLASS")
        observed_seeds=set()
        for rep in REPS:
            fit,alpha,sse,marginal=fit_public(CountRecallHard,rep)
            for role in N:
                for i in range(N[role]):
                    s=seed(role,rep,i)
                    require(s not in observed_seeds,"SOURCE_ROLE_SEED_COLLISION")
                    observed_seeds.add(s)
            raw["replicas"].append({"replica":rep,"source_fit_episode_rows":fit})
            stable=canonical({"alpha":alpha,"marginal":sorted([[list(k),v] for k,v in marginal.items()])})
            valid=score(CountRecallHard,"VALID",rep,alpha,marginal)
            dev=score(CountRecallHard,"DEV",rep,alpha,marginal)
            require(stable==canonical({"alpha":alpha,"marginal":sorted([[list(k),v] for k,v in marginal.items()])}),
                    "FIT_PARAMETERS_MUTATED_AFTER_FIT")
            rate=lambda name:dev[name]["accuracy"]
            passed=(rate(CANDIDATE)>=.95 and rate(COUNTER)>=.99
                    and rate(CANDIDATE)-rate(BLIND)>=.2
                    and rate(CANDIDATE)-rate(ERASED)>=.2)
            item={"replica":rep,
               "FIT_source_episodes":N["FIT"],
               "FIT_original_public_actions":N["FIT"]*STEPS,
               "FIT_original_public_sha256":digest(fit),
               "FIT_alpha_squared_error":sse,
               "fitted_selected_retention_alpha":alpha,
               "trained_query_time_marginal_num_cells":len(marginal),
               "model_serialized_state_bytes":{
                   CANDIDATE:len(canonical({"alpha":alpha,"public_rank_state_slots":SYMBOLS}).encode()),
                   COUNTER:len(canonical({"public_integer_counter_slots":SYMBOLS}).encode()),
                   BLIND:len(stable.encode()),
                   RECENT:len(canonical({"recent_window":8}).encode()),
                   ERASED:len(canonical({"alpha":alpha,"reset_step":104}).encode()),
                   ZERO:len(canonical({"constant_action":0}).encode())},
               "VALID":valid,"DEV":dev,
               "candidate_minus_trained_current_frame_pp":100*(rate(CANDIDATE)-rate(BLIND)),
               "candidate_minus_midway_erasure_pp":100*(rate(CANDIDATE)-rate(ERASED)),
               "candidate_minus_exact_public_counter_pp":100*(rate(CANDIDATE)-rate(COUNTER)),
               "frozen_public_decision_criterion_passed":passed,
               "process_inclusive_peak_rss_kib_not_isolated_model":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
            receipt["replicas"].append(item)
            print("CS06_REPLICA="+str(rep)+" alpha="+str(alpha)+" DEV="+canonical({
                   arm:dev[arm]["correct_count_predictions"] for arm in ARMS}),flush=True)
        require(len(observed_seeds)==3*(16+8+16),"ALL_SPLIT_SEED_COUNT_DRIFT")
        receipt["public_original_episode_instances"]=3*(16+6*(8+16))
        receipt["public_original_source_actions"]=receipt["public_original_episode_instances"]*STEPS
        receipt["full_public_fit_history_sha256"]=digest(raw)
        receipt["disposition"]=(
            "PUBLIC_CS06_FITTED_RETENTION_USE_SUPPORTED_NOT_NATIVE"
            if all(r["frozen_public_decision_criterion_passed"] for r in receipt["replicas"])
            else "PUBLIC_CS06_NO_FITTED_RETENTION_ADVANTAGE")
        receipt["novel_native_cognition_advantage"]="NOT_ESTABLISHED_CONVENTIONAL_COUNTER_AVAILABLE"
    except Exception as exc:
        receipt["first_failure"]=type(exc).__name__+":"+str(exc)[:750]
    finally:
        (out/"cs06-public-fit-history.json").write_text(canonical(raw)+"\n")
        (out/"cs06-original-source-receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("CS06_DISPOSITION="+receipt["disposition"],flush=True)
    return 2 if receipt["disposition"]=="PUBLIC_CS06_INVALID_OR_INFO_LEAK" else 0
if __name__=="__main__":
    raise SystemExit(main())
