"""CK22-SR01: source-pinned, read-only seed-level robustness audit.

CKAD22 was already scored before this audit protocol was frozen. This is
post-result diagnostics, not independent preregistration of scientific gains.
It NEVER executes a generator, fits a learner, changes a native checkpoint,
or claims repeated held outcomes are independent seed groups.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/"CKAD-22"
SEEDS=(101,202,303)
FAMILIES=(("terminal_switch",0),("invariant",1),("terminal_switch",0),("invariant",0))
ARMS=("novel_active","retrieval_only","novel_random","pooled_replay",
      "beta","trailing_mle","exact_mixture")
EXPECTED_SHA="4b20ef3b9229eddfd509e5897e6aa8f8d5226288ab331c4a98f8a7bc46fbccc2"
EXPECTED_SOURCE="de1c3daac160c0ef24f352ce238558b1356c06dd"
SCHEMA="yggdrasil.ck22.seed-robustness-audit.v1"


def canonical(d):
    return json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")


def sha(raw):
    return sha256(raw).hexdigest()


def require(ok,code):
    if not ok:
        raise ValueError("CK22_SR01_"+code)


def semantic(obj):
    if isinstance(obj,dict):
        return {k:semantic(v) for k,v in obj.items()
                if not k.endswith("_seconds")
                and k not in {"source_candidate_sha","stable_sha256","parent_peak_rss_bytes"}}
    if isinstance(obj,list):
        return [semantic(v) for v in obj]
    return obj


def exact_signflip(values):
    require(type(values) in (tuple,list) and len(values)==3 and
            all(type(v) is int for v in values),"SIGNFLIP_SOURCE")
    observed=abs(sum(values))
    count=sum(abs(sum(sign*value for sign,value in zip(signs,values)))>=observed
              for signs in product((-1,1),repeat=3))
    return [Fraction(count,8).numerator,Fraction(count,8).denominator]


def ratio(v):
    return [v.numerator,v.denominator]


def validate(data):
    require(data.get("schema")=="yggdrasil.ckad22.adaptive-context-development.result.v1",
            "SOURCE_SCHEMA")
    require(data.get("source_candidate_sha")==EXPECTED_SOURCE,"SOURCE_COMMIT")
    require(data.get("stable_sha256")==EXPECTED_SHA,"SOURCE_STABLE_EXPECTED")
    require(sha(canonical(semantic(data)))==EXPECTED_SHA,"SOURCE_STABLE_RECOMPUTED")
    require(data.get("classification")=="DEVELOPMENT_GO" and
            data.get("development_pass") is True and
            all(data.get("development_gates",{}).values()),"FROZEN_GATES")
    require(data.get("scientific_pass") is False and data.get("accepted_native") is False
            and data.get("deployment")=="NONE","NONPROMOTION")
    require(data.get("scope",{}).get("held_updates")==0 and
            data.get("scope",{}).get("original_source_actions")==0 and
            data.get("scope",{}).get("protected_first_use")==0,"SOURCE_CUSTODY")
    require(data.get("scope",{}).get("matched_held_rollouts")==1152 and
            data.get("scope",{}).get("probe_rollouts")==768,"SCOPE_COUNT")
    seeds=data.get("seeds")
    require(type(seeds) is list and [x.get("seed") for x in seeds]==list(SEEDS),
            "SEED_IDENTITY")
    per_seed=[]
    for record in seeds:
        seed=record["seed"]
        require(record.get("source_seed")==seed+7000,"SEED_OFFSET")
        source_sessions=record.get("sessions")
        require(type(source_sessions) is list and len(source_sessions)==4,"SESSION_LENGTH")
        session_rows=[]
        for stage,(family,regime) in enumerate(FAMILIES):
            item=source_sessions[stage]
            require((item.get("session"),item.get("family"),item.get("regime"))==
                    (stage,family,regime),"SESSION_DOMAIN")
            require(item.get("probe_cohort")==f"ckad22-probe-{stage}" and
                    item.get("held_cohort")==f"ckad22-held-{stage}" and
                    item.get("training_episodes")==320+32*(stage+1),"COHORTS")
            evaluation=item.get("evaluation",{})
            require(set(ARMS).issubset(evaluation),"ARM_COVERAGE")
            reward={}
            for arm in ARMS:
                stats=evaluation[arm]
                require(stats.get("episodes")==96,"HELD_DENOMINATOR")
                score=stats.get("reward_sum")
                require(type(score) is int and 0<=score<=96,"REWARD_COUNT")
                reward[arm]=score
            require(evaluation["novel_active"]==evaluation["exact_mixture"],"EXACT_MATCHED_MIXTURE")
            novelty=item.get("adaptive_candidate",{})
            trace=novelty.get("weight_trace")
            require(type(trace) is list and len(trace)==33 and
                    novelty.get("training_episodes")==32,"ADAPTIVE_TRAINING_COUNT")
            weights=[]
            for pair in trace:
                require(type(pair) is list and len(pair)==2 and
                        all(type(z) is int for z in pair) and pair[1]>0
                        and 0<=pair[0]<=pair[1],"ADAPTIVE_WEIGHT")
                weights.append(Fraction(pair[0],pair[1]))
            require(weights[0]==Fraction(1,8),"ADAPTIVE_PRIOR")
            states=item.get("states",{})
            require("novel_active" in states and "retrieval_only" in states,
                    "NATIVE_STATES")
            context=states["novel_active"]["experience"]["context"]
            require(Fraction(*context["weights"][-1])==weights[-1],
                    "NATIVE_POSTERIOR_MISMATCH")
            require(states["novel_active"]["roundtrip_verified"] is True and
                    states["retrieval_only"]["roundtrip_verified"] is True,"ROUNDTRIP")
            require(item.get("parity",{}).get("mismatches")==0,"HYPOTHESIS_PARITY")
            session_rows.append({
              "session":stage,"family":family,"regime":regime,"held_episodes":96,
              "rewards":reward,
              "novel_gain_vs_retrieval":reward["novel_active"]-reward["retrieval_only"],
              "novel_gain_vs_random":reward["novel_active"]-reward["novel_random"],
              "novel_gain_vs_mle":reward["novel_active"]-reward["trailing_mle"],
              "posterior_novel_mass_initial":[1,8],
              "posterior_novel_mass_final_decimal":format(float(weights[-1]),".10g"),
              "online_candidate_probe_updates":32
            })
        per_seed.append({"seed":seed,"sessions":session_rows})
    stages=[]
    for stage in range(4):
        rows=[s["sessions"][stage] for s in per_seed]
        stages.append({
          "session":stage,"family":FAMILIES[stage][0],"regime":FAMILIES[stage][1],
          "cases":288,
          "rewards":{arm:sum(item["rewards"][arm] for item in rows) for arm in ARMS},
          "gain_vs_retrieval":sum(item["novel_gain_vs_retrieval"] for item in rows),
          "gain_vs_random_probe":sum(item["novel_gain_vs_random"] for item in rows),
        })
    metrics={
      "unfamiliar_reward":Fraction(sum(stages[i]["rewards"]["novel_active"] for i in (0,1)),576),
      "unfamiliar_delta_retrieval":Fraction(sum(stages[i]["gain_vs_retrieval"] for i in (0,1)),576),
      "unfamiliar_delta_mle":Fraction(sum(stages[i]["rewards"]["novel_active"]-
                                           stages[i]["rewards"]["trailing_mle"] for i in (0,1)),576),
      "returning_new_reward":Fraction(stages[2]["rewards"]["novel_active"],288),
      "returning_old_reward":Fraction(stages[3]["rewards"]["novel_active"],288),
      "returning_old_delta_retrieval":Fraction(stages[3]["gain_vs_retrieval"],288)
    }
    require({k:ratio(v) for k,v in metrics.items()}==data["development_metrics"],
            "HISTORICAL_METRIC_PARITY")
    gates={
      "unfamiliar_vs_retrieval":metrics["unfamiliar_delta_retrieval"]>=Fraction(1,20),
      "unfamiliar_vs_mle":metrics["unfamiliar_delta_mle"]>=0,
      "returning_new_reward":metrics["returning_new_reward"]>=Fraction(4,5),
      "returning_old_reward":metrics["returning_old_reward"]>=Fraction(4,5),
      "returning_old_vs_retrieval":metrics["returning_old_delta_retrieval"]>=-Fraction(1,20)
    }
    require(gates==data["development_gates"],"FROZEN_GATE_RECOMPUTE")
    group_diff={
      other:[sum(row["sessions"][stage]["rewards"]["novel_active"]-
                 row["sessions"][stage]["rewards"][other] for stage in (0,1))
             for row in per_seed]
      for other in ("retrieval_only","trailing_mle","novel_random","beta","pooled_replay")
    }
    positives=[max(x,0) for x in group_diff["retrieval_only"]]
    concentration=Fraction(max(positives),sum(positives)) if sum(positives)>0 else None
    analysis={
      "schema":SCHEMA,
      "analysis_class":"POST_RESULT_INDEPENDENT_DIAGNOSTIC_NOT_SCIENTIFIC_PASS",
      "source_candidate_sha":EXPECTED_SOURCE,
      "source_stable_sha256":EXPECTED_SHA,
      "source_development":"DEVELOPMENT_GO",
      "source_qualified_run":44266448951,
      "source_case_count":1152,"independent_seed_groups":3,
      "original_ckad22_metrics_verified":{k:ratio(v) for k,v in metrics.items()},
      "per_seed":per_seed,"per_session":stages,
      "unfamiliar_0_1_group_differences":group_diff,
      "unfamiliar_group_exact_two_sided_signflip_p":{
           other:exact_signflip(values) for other,values in group_diff.items()},
      "unfamiliar_positive_retrieval_gain_largest_seed_share":
          ratio(concentration) if concentration is not None else None,
      "notes":[
          "Three independent seed groups imply exact two-sided sign-flip p cannot be below 0.25.",
          "Nominal episode count cannot substitute for independent seed-level replication.",
          "Novel-vs-retrieval policies share the actual 32-per-session active probe receipts.",
          "Novel-vs-random policies use independently chosen probes and do not isolate novelty alone.",
          "Original scores preceded this post-result audit; associations and concentration are descriptive.",
          "Exact independent online-mixture policy matches native readout and is not evidence of superiority.",
          "No new source rolls, training, tokens, source actor calls or held adaptation."
      ],
      "scientific_pass":False,"accepted_native":False,"deployment":"NONE"
    }
    analysis["stable_sha256"]=sha(canonical(analysis))
    return analysis


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,default=BASE/"result.json")
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    prereg=json.loads((HERE/"prereg.json").read_bytes())
    require(prereg["source_stable_sha256"]==EXPECTED_SHA and
            prereg["source_commit"]=="f04cfcac2aa07806a6b942d968119de87bfb6aaf",
            "AUDIT_PROTOCOL")
    d=json.loads(args.input.read_text(encoding="utf-8"))
    result=validate(d)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in
        ("analysis_class","original_ckad22_metrics_verified",
         "unfamiliar_0_1_group_differences",
         "unfamiliar_group_exact_two_sided_signflip_p",
         "unfamiliar_positive_retrieval_gain_largest_seed_share",
         "stable_sha256")},sort_keys=True))


if __name__=="__main__":
    main()
