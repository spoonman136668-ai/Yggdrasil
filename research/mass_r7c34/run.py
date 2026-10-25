"""Mass R7-C34: physically verify original DoorKey goal-facing missed terminal actions.

RETROSPECTIVE already exposed FIT only. Never feed evaluator world clones or
hidden cells to any policy. The intervention is a one-step source affordance
control, NOT trained native navigation.
"""
import copy,hashlib,json,os,resource,sys,time,zipfile
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(Path(os.environ["OWNER_R12_ROOT"]).resolve()))
from research.native.itd02.r10 import public_adapter as owner
P=json.loads((HERE/"PROTOCOL.json").read_text())
ORIGINAL_ARCHIVE_SHA=P["source"]["artifactZipSha256"]

def normalized(obs):
    import numpy as np
    assert type(obs)is dict and set(obs)=={"image","direction","mission"}
    d=obs["direction"]
    if type(d)is not int:
        assert isinstance(d,np.integer)
        d=int(d)
    return owner.public_observation({"image":obs["image"],"direction":d,"mission":obs["mission"]})

def cues(obs):
    return owner.public_cues(normalized(obs))

def load_original(path):
    raw=Path(path).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==ORIGINAL_ARCHIVE_SHA,"ORIGINAL_ARTIFACT_DRIFT"
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None,"SOURCE_ZIP_CRC"
        a=json.loads(z.read("run-1.json"))
        b=json.loads(z.read("run-2.json"))
        assert a["original_episode_and_step_evidence"]==b["original_episode_and_step_evidence"],"ORIGINAL_RUN_REPLAY_DIFF"
        assert a["per_arm_actual_source"]==b["per_arm_actual_source"]
        assert a["source_original"]==P["source"]["miniGrid"]
        assert a["native_owner_head"]==P["source"]["originalOwner"].split("@")[-1]
        assert a["owner_source_changed"] is False
        assert a["protected_first_use"] is False and a["source_dev_episodes_consumed"]==0
        records=a["original_episode_and_step_evidence"]
        native=[x for x in records if x["arm"]=="native_local_effect_delegation"]
        conv=[x for x in records if x["arm"]=="conventional_equal_learned_effect_delegation"]
        assert len(native)==len(conv)==1
        assert native[0]["complete_original_public_step_records"]==conv[0]["complete_original_public_step_records"]
        return native[0]["complete_original_public_step_records"]

def replay_one(record,first_t):
    import gymnasium as gym
    original=record["events"]
    seed=record["seed"]
    env=gym.make("MiniGrid-DoorKey-8x8-v0")
    try:
        obs,_=env.reset(seed=seed)
        prefix=[]
        for t in range(first_t+1):
            old=original[t]
            assert old["t"]==t
            before=cues(obs)
            assert before["observation_sha256"]==old["public_before_sha256"],("ORIGINAL_PREFIX_PUBLIC_HASH_DRIFT",seed,t)
            assert before["front"]==old["front_before"]
            assert old["a"] in range(7)
            if t==first_t:
                assert before["front"][0]==P["source"]["constantGoalObjectIndex"]
                # The external evaluator alone forks the exact authenticated
                # original source physical world at the *verified* public goal.
                source_clone=copy.deepcopy(env)
                try:
                    forced_obs,forced_r,forced_term,forced_trunc,_=source_clone.step(2)
                    forced_after=cues(forced_obs)
                finally:source_clone.close()
            next_obs,reward,done,trunc,_=env.step(old["a"])
            after=cues(next_obs)
            assert after["observation_sha256"]==old["public_after_sha256"],("ORIGINAL_PREFIX_AFTER_DRIFT",seed,t)
            assert after["front"]==old["front_after"],("ORIGINAL_FRONT_AFTER_DRIFT",seed,t)
            assert float(reward)==float(old["r"]) and bool(done)==old["done"] and bool(trunc)==old["trunc"],("ORIGINAL_SOURCE_REWARD_DRIFT",seed,t)
            assert old["a"]==old["collector_a"]
            prefix.append([t,old["a"],before["observation_sha256"],
                           after["observation_sha256"],float(reward),bool(done),bool(trunc)])
            obs=next_obs
            assert not(done or trunc) or t==first_t
        assert first_t==len(prefix)-1
        assert bool(forced_term) and float(forced_r)>0 and not forced_trunc,("VISIBLE_GOAL_FORWARD_NOT_TERMINAL",seed,first_t,forced_r,forced_term,forced_trunc)
        assert old["a"]==2 or (not done and float(reward)==0),("ORIGINAL_RECORDED_NON_GOAL_TURN_NOT_REPRODUCED",seed)
        if old["a"]==2:
            assert float(reward)==float(forced_r)
            assert after["observation_sha256"]==forced_after["observation_sha256"]
        return {"seed":seed,"first_goal_front_t":first_t,
            "archive_selected_action":old["a"],
            "archive_turn_before_goal":bool(old["a"]==1),
            "original_one_step_reward":float(reward),
            "original_one_step_terminal":bool(done),
            "source_forward_one_step_reward":float(forced_r),
            "source_forward_one_step_terminal":bool(forced_term),
            "source_forward_after_public_sha256":forced_after["observation_sha256"],
            "first_public_before_sha256":before["observation_sha256"],
            "source_prefix_verified_selected_actions":len(prefix),
            "replayed_original_source_prefix_sha256":hashlib.sha256(owner.canonical(prefix)).hexdigest()}
    finally:env.close()

def main():
    import minigrid
    from minigrid.core.constants import OBJECT_TO_IDX
    assert owner.UPSTREAM_MINIGRID_COMMIT==P["source"]["miniGrid"].split("@")[-1]
    assert OBJECT_TO_IDX["goal"]==8==P["source"]["constantGoalObjectIndex"]
    t0=time.process_time()
    records=load_original(sys.argv[1])
    assert [e["seed"] for e in records]==P["originalFITSeeds"]
    audit=[];selected=[]
    for r in records:
        ev=r["events"]
        openings=[i for i,x in enumerate(ev) if x["opened"]]
        assert len(openings)>=1,("MISSING_REAL_DOOR_OPEN",r["seed"])
        first=openings[0]
        after=[(i,x) for i,x in enumerate(ev) if i>first]
        goalfront=[(i,x) for i,x in after if x["front_before"][0]==8]
        successful=any(x["r"]>0 for x in ev)
        relevant={"seed":r["seed"],"original_goal":successful,
             "real_door_open_at":first,
             "total_after_door_source_actions":len(after),
             "goal_visible_front_occasions":len(goalfront),
             "front_goal_original_actions":dict(sorted(Counter(x["a"] for _,x in goalfront).items())),
             "first_goal_front_t":goalfront[0][0] if goalfront else None,
             "all_goal_front_event_source_sha256":hashlib.sha256(owner.canonical([
                   [i,x["a"],x["public_before_sha256"],x["r"],x["done"]] for i,x in goalfront])).hexdigest()}
        audit.append(relevant)
        if goalfront:
            selected.append(replay_one(r,goalfront[0][0]))
    failures=[x for x in audit if not x["original_goal"]]
    positives=[x for x in audit if x["original_goal"]]
    assert len(failures)==10 and len(positives)==2
    assert len(selected)==5,("RETRO_SOURCE_ELIGIBILITY_DRIFT",len(selected))
    result={"schema":P["schema"],
        "scientific_category":P["scientific_role"],
        "authenticated_original_source":P["source"]["miniGrid"],
        "authentic_original_artifact_sha256":ORIGINAL_ARCHIVE_SHA,
        "source_owner_r12":P["source"]["originalOwner"],
        "protocol_sha256":hashlib.sha256((HERE/"PROTOCOL.json").read_bytes()).hexdigest(),
        "two_original_independent_source_science_runs_match":True,
        "no_new_source_fit_or_dev_roles":True,
        "old_original_FIT_replays_only":True,
        "protected_first_use":False,
        "archived_cases":audit,"original_source_physically_replayed_cases":selected,
        "failed_after_door":len(failures),
        "failed_cases_actually_saw_goal_directly_ahead":sum(x["goal_visible_front_occasions"]>0 for x in failures),
        "failed_after_door_goal_directly_ahead_occurrences":sum(x["goal_visible_front_occasions"] for x in failures),
        "failed_goal_front_actions":dict(Counter({str(k):sum(x["front_goal_original_actions"].get(k,0) for x in failures) for k in (0,1,2)})),
        "positive_controls_forward_from_goal_visible":sum(e["original_goal"] and e["front_goal_original_actions"].get(2,0)>0 for e in positives),
        "physically_forced_forward_positive_original_goal":sum(e["source_forward_one_step_terminal"] and e["source_forward_one_step_reward"]>0 for e in selected),
        "physically_rescuable_recorded_failed_seed_count":sum(e["archive_turn_before_goal"] and e["source_forward_one_step_terminal"] for e in selected),
        "total_actual_original_source_replayed_actions":sum(e["source_prefix_verified_selected_actions"] for e in selected),
        "total_additional_counterfactual_source_steps":len(selected),
        "source_cpu_seconds":round(time.process_time()-t0,6),
        "source_full_python_peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "scientific_disposition":"RETROSPECTIVE_EXACT_PUBLIC_GOAL_AFFORDANCE_FAILURE_VERIFIED_NOT_NATIVE_LEARNED_POLICY_GAIN"}
    Path(sys.argv[2]).write_bytes(owner.canonical(result)+b"\n")
    print("R7C34_ORIGINAL_SOURCE_SHA_EVENT_REPLAY=PASS")
    print("R7C34_SOURCE_PHYSICAL_GOAL_FRONT_INTERVENTIONS="+str(len(selected)))
    print("R7C34_FAILED_GOAL_DIRECTLY_AHEAD_OCCURRENCES="+str(result["failed_after_door_goal_directly_ahead_occurrences"]))
    print("R7C34_FAILED_ORIGINAL_SOURCE_RESCUABLE="+str(result["physically_rescuable_recorded_failed_seed_count"]))
    print("R7C34_SCIENTIFIC_DISPOSITION="+result["scientific_disposition"])
if __name__=="__main__":main()
