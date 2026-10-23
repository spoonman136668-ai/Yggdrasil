#!/usr/bin/env python3
"""CS18 genuine original POPGym CountRecall source-only relevance screen.

No proposed native learning integration until source information-sufficiency
admission; never read step() info['counts'] or env hidden state into policy.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib,importlib,inspect,json,math
from pathlib import Path
import resource,subprocess,sys,time,types

UPSTREAM="proroklab/popgym@410d5aa626dae8024f498354d8781a0d1870c399"
SOURCE_BLOBS={
 "popgym/envs/count_recall.py":"48dee2a5ca400021582cdf8638bb5c500d021f00",
 "popgym/core/deck.py":"12bcabfa9a96fd1261809ef0a446c74d3f3bfa86",
 "popgym/core/env.py":"26a20ba3531730b76e135f48e8fc25bb6b620984",
}
FIRST="cc4ddbba70b411b85f7b1e1d602a4a503c2dadf2"
K=3
TYPES=("ranks","suits","colors")
CATS=(13,4,2)
REPS=(0,1)
N_PER_REP=32
ARMS=("full_public_histogram","source_FIT_frequency_topK_static",
      "firstK_public_fixed","current_frame_only")
def need(x,error):
    if not x:raise RuntimeError(error)
def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(x):return hashlib.sha256(canon(x).encode()).hexdigest()
def gitblob(path):
    p=subprocess.run(["git","hash-object",str(path)],capture_output=True,text=True,timeout=20)
    need(p.returncode==0,"ORIGINAL_EXTERNAL_GIT_BLOB_UNAVAILABLE")
    return p.stdout.strip()
def source_class(root):
    for filename,expected in SOURCE_BLOBS.items():
        need(gitblob(root/filename)==expected,"UPSTREAM_ORIGINAL_BLOB_DRIFT:"+filename)
    # Scoped module namespaces avoid importing unrelated source providers,
    # but *all actual CountRecall/Deck/Env source is imported unchanged*.
    for name,rel in (("popgym","popgym"),("popgym.envs","popgym/envs"),
                     ("popgym.core","popgym/core")):
        pkg=types.ModuleType(name);pkg.__path__=[str(root/rel)]
        pkg.__package__=name;sys.modules[name]=pkg
    for name in list(sys.modules):
        if name.startswith("popgym.") and name not in ("popgym.envs","popgym.core"):
            del sys.modules[name]
    module=importlib.import_module("popgym.envs.count_recall")
    need(Path(inspect.getfile(module.CountRecall)).resolve()==
         (root/"popgym/envs/count_recall.py").resolve(),
         "ORIGINAL_COUNTRECALL_CLASS_NOT_SOURCE_OWNED")
    return module.CountRecall
def seed(role,ti,rep,i):
    base=4100000 if role=="FIT" else 4500000
    return base+100000*ti+10000*rep+i
def actions(chosen,n):
    if chosen=="full_public_histogram":return tuple(range(n))
    if chosen=="source_FIT_frequency_topK_static":return tuple(range(min(K,n)))
    if chosen=="firstK_public_fixed":return tuple(range(min(K,n)))
    if chosen=="current_frame_only":return ()
    raise RuntimeError("NONFROZEN_SOURCE_ACTION_ARM")
def source_episode(cls,deck_type,ncat,role,ti,rep,i,policy,keep):
    env=cls(num_decks=1,deck_type=deck_type)
    initial,unused_reset_info=env.reset(seed=seed(role,ti,rep,i))
    need(env.max_episode_length==51 and env.action_space.n in (5,14,27),
         "ORIGINAL_DECK_SOURCE_SIZE_OR_ACTION_SPEC_CHANGED")
    # Never inspect/reset_info or step info: they may expose private counts.
    del unused_reset_info
    obs=[int(x) for x in initial]
    need(len(obs)==2 and all(0<=z<ncat for z in obs),"SOURCE_RESET_PUBLIC_OBSERVATION_INVALID")
    observations=[obs]
    dealt=[0]*ncat
    query_frequency=[0]*ncat
    score=0.
    exact_count=0
    chosen_set=set(keep)
    rewards=[]
    actions_taken=[]
    t=time.process_time_ns()
    for step in range(51):
        card,query=obs
        dealt[card]+=1
        query_frequency[query]+=1
        if policy=="current_frame_only":act=0
        elif query in chosen_set:act=dealt[query]
        else:act=0
        need(env.action_space.contains(act),"ORIGINAL_SOURCE_ACTION_OUTSIDE_SPEC")
        next_obs,reward,terminated,truncated,ignored_info=env.step(act)
        # Info explicitly ignored, never used for score or policy.
        del ignored_info
        next_obs=[int(x) for x in next_obs]
        need(len(next_obs)==2 and all(0<=z<ncat for z in next_obs),
             "ORIGINAL_POST_STEP_PUBLIC_OBS_NOT_VALID")
        need(float(reward) in (-1/51,1/51) and
             bool(terminated)==(step==50) and truncated is False,
             "ORIGINAL_SOURCE_REWARD_OR_TERMINAL_INVALID")
        reward=float(reward);score+=reward
        exact_count+=int(reward>0)
        rewards.append(round(reward,12))
        actions_taken.append(int(act))
        obs=next_obs;observations.append(obs)
    # Source supplies next query on final step, although it will never be asked.
    dealt[obs[0]]+=1;query_frequency[obs[1]]+=1
    need(len(observations)==52 and sum(query_frequency)==52 and
         sum(dealt)==52,"ORIGINAL_SOURCE_DECK_PUBLIC_OBSERVATION_COUNT_INVALID")
    expected=52//ncat
    need(all(v==expected for v in query_frequency) and
         all(v==expected for v in dealt),"ORIGINAL_QUERY_OR_DEALT_DECK_NOT_EXACTLY_UNIFORM")
    return {
      "source_role":role,"original_external_seed":seed(role,ti,rep,i),
      "source_deck_type":deck_type,"source_actual_steps":51,
      "public_original_dealt_counts":dealt,
      "public_original_query_counts":query_frequency,
      "genuine_source_total_reward":round(score,12),
      "genuine_source_correct_source_action_count":exact_count,
      "source_actual_terminal_reward_signed":rewards[-1],
      "source_actions_sha256":sha(actions_taken),
      "source_public_obs_SHA256":sha(observations),
      "source_real_native_reward_trace_SHA256":sha(rewards),
      "source_and_policy_CPU_ns":time.process_time_ns()-t,
    }
def main():
    a=argparse.ArgumentParser();a.add_argument("--upstream",required=True)
    a.add_argument("--out",required=True);args=a.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"mass.cs18.actual_POPGym_stable_relevance_screen.v1",
      "immutable_original_FIRST_prereg":FIRST,
      "source_seed_prospective_pre_execution_corrigendum":"CS18_SEED_CORRIGENDUM.md",
      "external_original_source":UPSTREAM,
      "original_hidden_env_state_or_info_consumed":False,
      "actual_native_model_trained_or_integrated":False,
      "independently_sealed_unfamiliar_first_use":False,
      "original_R7_final_integration_gate":"FAIL_UNCHANGED",
      "disposition":"PUBLIC_CS18_SOURCE_PROTOCOL_INVALID",
      "levels":[]}
    t0=time.process_time_ns()
    try:
        cls=source_class(Path(args.upstream).resolve())
        ids=[seed(role,ti,rep,i) for role in ("FIT","DEV")
             for ti in range(3) for rep in REPS for i in range(N_PER_REP)]
        need(len(ids)==len(set(ids))==384,"ORIGINAL_PUBLIC_FIT_DEV_SOURCE_SEED_ID_COLLISION")
        for ti,(name,ncat) in enumerate(zip(TYPES,CATS)):
            fit=[source_episode(cls,name,ncat,"FIT",ti,rep,i,
                                "full_public_histogram",tuple(range(ncat)))
                 for rep in REPS for i in range(N_PER_REP)]
            learned_frequencies=[sum(z["public_original_query_counts"][k] for z in fit)
                                 for k in range(ncat)]
            ordering=tuple(sorted(range(ncat),key=lambda k:(-learned_frequencies[k],k)))
            learned_keep=ordering[:min(K,ncat)]
            need(len(fit)==64 and len(set(learned_frequencies))==1,
                 "ORIGINAL_SOURCE_FIT_STABLE_QUERY_FREQUENCY_NOT_UNIFORM")
            roles={}
            for arm in ARMS:
                keep=learned_keep if arm==ARMS[1] else actions(arm,ncat)
                episodes=[source_episode(cls,name,ncat,"DEV",ti,rep,i,arm,keep)
                          for rep in REPS for i in range(N_PER_REP)]
                roles[arm]={
                  "original_source_DEV_episode_count":len(episodes),
                  "original_source_real_action_count":len(episodes)*51,
                  "mean_original_native_reward":sum(x["genuine_source_total_reward"] for x in episodes)/64,
                  "mean_original_native_correct_action_rate":sum(x["genuine_source_correct_source_action_count"]
                                          for x in episodes)/(64*51),
                  "retained_categories":list(keep),
                  "genuine_SOURCE_original_DEV_episode_records":episodes}
            for k in range(64):
                need(len({roles[arm]["genuine_SOURCE_original_DEV_episode_records"][k]["source_public_obs_SHA256"]
                    for arm in ARMS})==1,"ORIGINAL_PAIRED_SOURCE_OBSERVATION_STREAM_DIFFERS_ACROSS_ARMS")
            trained=roles[ARMS[1]]["genuine_SOURCE_original_DEV_episode_records"]
            fixed=roles[ARMS[2]]["genuine_SOURCE_original_DEV_episode_records"]
            need(all(x["genuine_source_total_reward"]==y["genuine_source_total_reward"]
                     and x["source_actions_sha256"]==y["source_actions_sha256"]
                     for x,y in zip(trained,fixed)),
                 "EXACTLY_UNIFORM_SOURCE_BUT_STATIC_QUERY_PRIOR_GAINED_REAL_REWARD")
            need(roles[ARMS[0]]["mean_original_native_correct_action_rate"]==1.,
                 "ORIGINAL_PUBLIC_HISTOGRAM_NOT_FULLY_SUFFICIENT_FOR_SOURCE_REWARD")
            receipt["levels"].append({
              "original_source_deck_family":name,"public_categories":ncat,
              "source_original_per_episode_exact_query_frequency":52//ncat,
              "FIT_original_source_episodes":64,"FIT_original_native_steps":64*51,
              "public_fit_learned_query_counts":learned_frequencies,
              "source_fit_relevance_prior_uniform":True,
              "source_learned_static_topK":list(learned_keep),
              "source_original_FIT_trace_SHA256":sha(fit),
              "real_original_source_original_FIT_records":fit,
              "real_original_source_DEV_arm_receipts":roles,
              "source_stable_query_relevance_not_learnable_from_FIT":True})
            print("CS18_ORIGINAL_DECK="+name+" reward="+canon({
                 arm:round(roles[arm]["mean_original_native_reward"],4) for arm in ARMS}),flush=True)
        receipt["source_original_FIT_resets"]=3*64
        receipt["source_original_DEV_resets"]=3*4*64
        receipt["original_real_total_reset_episodes"]=960
        receipt["original_real_TOTAL_step_actions"]=960*51
        receipt["full_histogram_all_original_rewards_correct"]=True
        receipt["native_selective_gate_deployment_warranted"]=False
        receipt["disposition"]="PUBLIC_CS18_NO_LEARNABLE_STATIC_RELEVANCE_SIGNAL"
    except Exception as e:
        receipt["first_failure"]=type(e).__name__+":"+str(e)[:900]
    finally:
        receipt["original_source_and_models_CPU_ns"]=time.process_time_ns()-t0
        receipt["process_RSS_KiB_not_model_isolated"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        (out/"cs18-real-original-POPgym-relevance-receipt.json").write_text(
              json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print("CS18_DISPOSITION="+receipt["disposition"],flush=True)
    return 2 if receipt["disposition"]=="PUBLIC_CS18_SOURCE_PROTOCOL_INVALID" else 0
if __name__=="__main__":raise SystemExit(main())
