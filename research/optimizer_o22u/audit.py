"""O22-U: read-only re-analysis of already executed C32 original-world actions.

Every replay step uses the ACTUAL selected historical action and source-public
return; an alternative veto action is never executed, assigned a future
reward, or fed into the subsequent public state of the original trace.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import io
import json
from pathlib import Path
import zipfile

from research.optimizer_o22u.cycle_veto import SelectedActionGuard

HERE = Path(__file__).resolve().parent
P = json.loads((HERE / "PREREG.json").read_text())


def canonical(s):
    return json.dumps(s,sort_keys=True,separators=(",",":"),allow_nan=False).encode()


def _pos(p):
    return (p["x"],p["y"],p["direction"])


def episode_check(e, expected_seed):
    assert int(e["seed"]) == expected_seed
    rows = e["source_actual_actions"]
    assert len(rows) == e["steps"] and rows
    assert hashlib.sha256(canonical(rows)).hexdigest() == e["source_trace_sha256"]
    guard = SelectedActionGuard()
    result = {"episodes":1, "historical_actions":len(rows),
              "historical_substitutions":0, "retrospective_vetoable_substitutions":0,
              "actual_opposite_turn_windows":0,"actual_four_turn_cycles":0,
              "unchanged_r3_original_actions":0,
              "audited_decisions":0, "would_change_original_source_stream":False}
    for i, row in enumerate(rows):
        assert row["t"] == i
        a,b,c = row["original_r3_proposed"],row["executed"],row["before"]
        original, flag = guard.decide(c,i,a,b)
        assert original in (0,1,2)
        assert not flag or (a in (0,1) and b in (0,1) and a!=b
                            and original==a)
        assert b==a or (b in (0,1) and a in (0,1) and b!=a)
        if b==a:
            result["unchanged_r3_original_actions"] += 1
            assert original==a
        else:
            result["historical_substitutions"] += 1
        result["retrospective_vetoable_substitutions"] += int(flag)
        if i>0:
            last=rows[i-1]
            assert _pos(last["after"]) == _pos(row["before"]), "ORIGINAL_PUBLIC_POSE_CHAIN"
            if (last["executed"] in (0,1) and b in (0,1)
                and b!=last["executed"] and
                (_pos(last["before"])[:2]==_pos(row["after"])[:2])):
                result["actual_opposite_turn_windows"] += 1
        if i>=3:
            four=rows[i-3:i+1]
            turns=[q["executed"] for q in four]
            if (turns in ([0,1,0,1],[1,0,1,0]) and
                _pos(four[0]["before"]) == _pos(four[-1]["after"])):
                result["actual_four_turn_cycles"] += 1
        guard.observe_actual(i,c,b,row["after"])
        result["audited_decisions"]+=1
        assert guard.seen==i+1
    assert (not e["source_goal"] or rows[-1]["reward"]>0)
    assert (not e["source_collision"] or rows[-1]["reward"]<0)
    assert e["native_real_turn_changes"]==result["historical_substitutions"]
    return result


def audited_source(zipbytes):
    assert hashlib.sha256(zipbytes).hexdigest()==P["C32_archive_sha256"]
    z=zipfile.ZipFile(io.BytesIO(zipbytes))
    assert z.testzip() is None
    assert set(z.namelist()) == {
        "comparison.json","process-a.json","process-b.json",
        "process-a.log","process-b.log"}
    comp=json.loads(z.read("comparison.json"))
    assert comp["science_identical"] is True
    assert comp["scientific_accepted"] is False and comp["scientific_first_use"] is False
    assert comp["result"]=="NO_REPEATABLE_C32_REAL_SOURCE_NATIVE_EFFECT_DECISION_ADVANTAGE"
    procs=[json.loads(z.read(n)) for n in ("process-a.json","process-b.json")]
    first,second=procs
    for p in procs:
        assert p["source_DEV_or_protected_episodes"]==0
        assert p["verdict"]=="NO_C32_REAL_SOURCE_NATIVE_EFFECT_DECISION_ADVANTAGE"
        assert p["original_upstream"]==P["original_farama"]
        assert len(p["original_world_episode_records"])==P["expected_c32_episodes_per_process"]
        assert sum(e["steps"] for e in p["original_world_episode_records"])==P["expected_c32_physical_actions_per_process"]
        assert p["all_actor_actions_physically_executed"] is True
    keys=set(first)-{"resources"}
    assert keys==set(second)-{"resources"}
    assert all(first[k]==second[k] for k in keys),"C32_DOUBLE_SOURCE_PROCESS_SCIENCE_DRIFT"
    by_actor=defaultdict(lambda:defaultdict(int))
    by_family=defaultdict(lambda:defaultdict(int))
    per_episode=[]
    expected={
        "MiniGrid-FourRooms-v0": {62021,62023,62027,62029},
        "MiniGrid-Dynamic-Obstacles-8x8-v0": {62121,62123,62127,62129}
    }
    seen=set()
    for e in first["original_world_episode_records"]:
        fam,arm,seed=e["family"],e["arm"],e["seed"]
        assert seed in expected[fam]
        identity=(fam,arm,seed)
        assert identity not in seen
        seen.add(identity)
        o=episode_check(e,seed)
        per_episode.append({"family":fam,"arm":arm,"seed":seed,
                            "trace_sha256":e["source_trace_sha256"],"counters":o})
        for key,v in o.items():
            if type(v) is int:
                by_actor[arm][key]+=v
                by_family[fam+"|"+arm][key]+=v
    assert len(seen)==56
    actual={k:dict(v) for k,v in by_actor.items()}
    for arm,ref in first["source_actor_summary"].items():
        assert actual[arm]["historical_actions"]==ref["real_actions"]
        assert actual[arm]["historical_substitutions"]==ref["actually_executed_turn_substitutions"]
    assert actual["native"]["historical_substitutions"]==430
    assert actual["native"]["retrospective_vetoable_substitutions"]==418
    assert actual["r3_original"]["historical_substitutions"]==0
    assert actual["native_frozen"]["historical_substitutions"]==0
    return {
        "schema":P["schema"],"prior_original_C32_source_run":P["C32_run_id"],
        "original_source_ZIP_sha256":P["C32_archive_sha256"],
        "already_consumed_original_FIT_only":True,
        "two_independent_original_world_runs_science_identical":True,
        "original_environment_new_steps_or_resets":0,
        "historical_actor_counts":actual,
        "historical_actor_family_counts":{k:dict(v) for k,v in by_family.items()},
        "per_episode_historical_source_trace_checks":per_episode,
        "source_observed_native_goals":first["source_actor_summary"]["native"]["real_goals"],
        "source_observed_original_r3_goals":first["source_actor_summary"]["r3_original"]["real_goals"],
        "simulated_guard_alternative_policy_return":"NOT_EXECUTED_NOT_OBSERVED",
        "novel_native_advantage":"NO_GO",
        "scientific_gate":"RETROSPECTIVE_LOOP_VETO_SAFETY_PRECONDITION_ONLY"
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-zip",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    arg=ap.parse_args()
    result=audited_source(arg.source_zip.read_bytes())
    arg.out.write_bytes(canonical(result)+b"\n")
    print("O22U_AUTHENTIC_SOURCE_TWO_PROCESS_RECEIPTS=PASS",flush=True)
    for arm,c in sorted(result["historical_actor_counts"].items()):
        print("O22U_"+arm.upper()+"_RETROSPECTIVE_VETO="+
            str(c["retrospective_vetoable_substitutions"])+
            "/"+str(c["historical_substitutions"]),flush=True)
    print("O22U_NO_NEW_SOURCE_EPISODES=PASS",flush=True)
    print("O22U_NO_ACTUAL_ALTERNATIVE_REWARD_CLAIM=PASS",flush=True)
    print("O22U_SCIENTIFIC_DECISION="+result["scientific_gate"],flush=True)


if __name__=="__main__":
    main()
