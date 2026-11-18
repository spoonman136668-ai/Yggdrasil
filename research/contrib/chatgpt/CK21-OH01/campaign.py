"""CK21-OH01: source-informed, NON-clairvoyant causal policy reference.

This is evaluator-side development analysis of ALREADY CONSUMED CKAD21
synthetic held episodes. Never use this reference as learner features or
equate its privileged source-family knowledge with matched information.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / "CKAD-20"))

from synthetic_world import make_episode, rollout, FAMILIES

SEEDS = (101, 202, 303)
SESSIONS = (("invariant",0),("context_switch",1),("context_switch",0),
            ("invariant",0),("context_switch",1),("terminal_switch",1))
PIN_SOURCE = "20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"
PIN_RESULT = "c986dd9dc63ace08f4a0185f80258099971e22ff50884cf6a7ec58e9b1ad650e"
P_INITIAL_FLIP = Fraction(1,4)
P_REWARD_FLIP = Fraction(1,16)
BITS = (0,1)


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")


def digest(obj):
    return sha256(obj).hexdigest()


def require(ok, code):
    if not ok:
        raise ValueError("CK21_OH01_" + code)


def informed_first(initial, family, regime):
    """Only public initial s1 and evaluator-supplied family/regime."""
    require(type(initial) is int and initial in BITS,"FIRST_PUBLIC")
    require(family in FAMILIES and type(regime) is int and regime in BITS,"FIRST_DOMAIN")
    return regime ^ (initial if family=="context_switch" else 0)


def informed_second(initial, first, next_state, family, regime):
    """Contingent action uses only actual public s2, never hidden/noise."""
    require(all(type(x) is int and x in BITS for x in (initial,first,next_state,regime))
            and family in FAMILIES,"SECOND_PUBLIC")
    return initial ^ next_state ^ (first ^ regime if family=="terminal_switch" else 0)


def joint_reward(initial, family, regime, first, next_state, second):
    """Independent exact rational marginal over H, transition and reward noise.

    s1 = H xor Bernoulli(1/4) and H is Bernoulli(1/2).
    Expected realized Y is 15/16 if ready and second action matches
    the generative causal target, else 1/16. No private draw is inspected.
    """
    require(all(type(x) is int and x in BITS for x in (initial,regime,first,next_state,second))
            and family in FAMILIES,"JOINT_ARGS")
    orientation = regime ^ (initial if family=="context_switch" else 0)
    noise_bit = next_state ^ first ^ orientation
    target = initial ^ next_state ^ (first ^ regime if family=="terminal_switch" else 0)
    total = Fraction(0)
    for hidden in BITS:
        p_hidden_given_initial = (1-P_INITIAL_FLIP if hidden==initial else P_INITIAL_FLIP)
        flip_p = Fraction(1,8) if hidden==0 else Fraction(1,4)
        p_transition = flip_p if noise_bit else 1-flip_p
        ready = next_state==0 or hidden==1
        expected_y = (1-P_REWARD_FLIP if ready and second==target else P_REWARD_FLIP)
        total += p_hidden_given_initial*p_transition*expected_y
    return total


def independent_exact_plan(initial, family, regime):
    """Exhaustive source-informed expected-value reference, independent of compact plan."""
    candidates=[]
    for first in BITS:
        contingent=[]
        v=Fraction(0)
        for state in BITS:
            scores=[joint_reward(initial,family,regime,first,state,second) for second in BITS]
            action=int(scores[1]>scores[0])
            contingent.append(action)
            v+=scores[action]
        candidates.append((v,first,tuple(contingent)))
    chosen=candidates[int(candidates[1][0]>candidates[0][0])]
    return chosen[1],chosen[2],chosen[0]


def mathematical_controls():
    need=0
    policies=[]
    for family in FAMILIES:
        for regime in BITS:
            for initial in BITS:
                a1,second,optimal=independent_exact_plan(initial,family,regime)
                first=informed_first(initial,family,regime)
                require(first==a1,"EXHAUSTIVE_FIRST_MISMATCH")
                for state in BITS:
                    require(informed_second(initial,first,state,family,regime)==second[state],
                            "EXHAUSTIVE_SECOND_MISMATCH")
                expected=Fraction(219 if initial==0 else 233,256)
                require(optimal==expected,"EXPECTED_OPTIMUM")
                need+=1
                policies.append([family,regime,initial,first,list(second),
                                 [optimal.numerator,optimal.denominator]])
    require(need==12,"DOMAIN_SCOPE")
    return policies


def run():
    started=time.monotonic()
    source_path=HERE.parent/"CKAD-20"/"synthetic_world.py"
    source_raw=source_path.read_bytes()
    require(digest(source_raw)==PIN_SOURCE,"SOURCE_PIN")
    protocol=json.loads((HERE/"prereg.json").read_bytes())
    require(protocol["source_fixture_sha256"]==PIN_SOURCE and
            protocol["source_commit"]=="392f6c5d66adfff3b79d6a6a2910b6557dfccbdc",
            "PREREG_LOCK")
    source_result=json.loads((HERE.parent/"CKAD-21"/"result.json").read_bytes())
    require(source_result["stable_sha256"]==PIN_RESULT and
            source_result["scientific_pass"] is False,"HISTORICAL_RESULT_PIN")
    all_policies=mathematical_controls()
    by_seed=[]
    for seed_report in source_result["seeds"]:
        seed=seed_report["seed"]
        require(seed in SEEDS,"SEED_PIN")
        sessions=[]
        require(len(seed_report["sessions"])==6,"SESSION_COUNT")
        for session,(family,regime) in enumerate(SESSIONS):
            old=seed_report["sessions"][session]
            require(old["family"]==family and old["regime"]==regime
                    and old["held_cohort"]==f"ckad21-held-{session}","HISTORICAL_COHORT")
            require(all(old["evaluation"][name]["episodes"]==96 for name in
                        ("context_active","context_random","pooled_replay")),
                    "HISTORICAL_DENOMINATOR")
            evidence=[]
            for index in range(96):
                episode=make_episode(cohort=f"ckad21-held-{session}",seed=seed,
                                     index=index,family=family,regime=regime)
                row=rollout(episode,
                            lambda initial:frozen_first(initial,family,regime),
                            lambda initial,first,state:
                                frozen_second(initial,first,state,family,regime))
                evidence.append([row[k] for k in ("s1","x1","s2","x2","y")])
            oracle=sum(row[-1] for row in evidence)
            sessions.append({
                "session":session,"family":family,"regime":regime,
                "oracle_reward":oracle,
                "active_reward":old["evaluation"]["context_active"]["reward_sum"],
                "random_reward":old["evaluation"]["context_random"]["reward_sum"],
                "pooled_reward":old["evaluation"]["pooled_replay"]["reward_sum"],
                "episodes":96,
                "oracle_trace_sha256":digest(canonical(evidence))
            })
        by_seed.append({"seed":seed,"sessions":sessions})
    require(sorted(v["seed"] for v in by_seed)==list(SEEDS),"SEEDS")
    by_session=[]
    for i,(family,regime) in enumerate(SESSIONS):
        rows=[s["sessions"][i] for s in by_seed]
        by_session.append({
            "session":i,"family":family,"regime":regime,"episodes":288,
            **{name:sum(row[name] for row in rows) for name in
               ("oracle_reward","active_reward","random_reward","pooled_reward")},
        })
    returning=[by_session[i] for i in (0,3)]
    sums={name:sum(row[name] for row in returning) for name in
          ("oracle_reward","active_reward","random_reward","pooled_reward")}
    require(sums["active_reward"]==497 and sums["pooled_reward"]==477,
            "RETURNING_HISTORICAL_BASELINE_DRIFT")
    required_increment=29
    required_absolute=sums["pooled_reward"]+required_increment
    headroom=sums["oracle_reward"]-sums["pooled_reward"]
    result={
       "schema":"yggdrasil.ck21oh01.oracle-headroom.result.v1",
       "source_parent":"392f6c5d66adfff3b79d6a6a2910b6557dfccbdc",
       "source_fixture_sha256":PIN_SOURCE,
       "historical_ckad21_result_sha256":PIN_RESULT,
       "oracle_information":"evaluator-only family+regime, public s1 and observed s2, no private exogenous outcomes",
       "exact_expectation":[113,128],
       "independent_domain_policy_checks":need_policies_count(all_policies),
       "oracle_policy_table":all_policies,
       "by_seed":by_seed,"by_session":by_session,
       "returning":{**sums,"total_episodes":576,"required_above_pooled":required_increment,
                    "required_absolute_successes":required_absolute,
                    "reference_oracle_meets_frozen_5pp_margin":headroom>=required_increment,
                    "oracle_minus_active":sums["oracle_reward"]-sums["active_reward"],
                    "oracle_minus_pooled":headroom,
                    "expected_optimum_successes":[1017,2]},
       "interpretation":"Reference is source-informed Bayes-optimal in expectation, NOT clairvoyant, not a strict finite-cohort realized upper bound, and not a matched-information native control.",
       "new_training_updates":0,"held_training_updates":0,
       "original_source_actions":0,"protected_first_use":0,
       "scientific_pass":False,"accepted_native":False,"deployment":"NONE"
    }
    result["classification"]=("ORACLE_REFERENCE_ATTAINED_5PP" if headroom>=required_increment
                               else "ORACLE_REFERENCE_BELOW_5PP")
    result["stable_sha256"]=digest(canonical(result))
    result["whole_wall_seconds"]=time.monotonic()-started
    require(result["whole_wall_seconds"]<60,"WALL_BUDGET")
    return result


def frozen_first(initial,family,regime):
    return informed_first(initial,family,regime)


def frozen_second(initial,first,state,family,regime):
    return informed_second(initial,first,state,family,regime)


def need_policies_count(table):
    return len(table)


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--output-directory",required=True,type=Path)
    args=cli.parse_args()
    args.output_directory.mkdir(parents=True,exist_ok=True)
    result=run()
    (args.output_directory/"result.json").write_text(
        json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in
                      ("classification","returning","by_session",
                       "stable_sha256","whole_wall_seconds")},sort_keys=True))
