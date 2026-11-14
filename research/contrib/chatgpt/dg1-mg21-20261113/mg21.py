"""DG1-MG21: independent reward-bearing demonstrations; separate original seed cohort.
Reuses and pins MG20 source entirely unchanged from exact committed research parent.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

SRC=Path(__file__).resolve().parents[1]/"dg1-mg20-20261113"/"mg20.py"
spec=importlib.util.spec_from_file_location("mg20_frozen",str(SRC))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

FREEZE="36d6155a9b3c254f31c05bdb5f1e3469fcff616b"
PARENT="9477ea4b366f2287eb316460514726cd6d2dfa7e"
CORE_SOURCE="9477ea4b366f2287eb316460514726cd6d2dfa7e"
MANIFEST_HASH="2f254e2a115fee9bd7d68e130d013479acb3804fd584348cce980dba7802db7f"
SCHEMA="yggdrasil.dg1-mg21-original.v1"
TRAIN_SEEDS=tuple(range(830001,830025))
INTERFERENCE_SEEDS=tuple(range(840001,840013))
COLD_SEEDS=tuple(range(850001,850013))
SIZE_SEEDS=tuple(range(860001,860013))
FAMILY_SEEDS=tuple(range(870001,870013))


def manifest():
    return {"schema":"yggdrasil.dg1-mg21-successful-training-action-plan.v1",
        "train_seeds":list(TRAIN_SEEDS),
        "interference_seeds":list(INTERFERENCE_SEEDS),
        "cold_seeds":list(COLD_SEEDS),
        "unseen_size_seeds":list(SIZE_SEEDS),
        "unseen_family_seeds":list(FAMILY_SEEDS),
        "train_envs":list(m.TRAIN_ENVS),
        "interference_env":m.INTERFERENCE_ENV,
        "cold_env":m.COLD_ENV,
        "unseen_size_env":m.SIZE_ENV,
        "unseen_family_env":m.FAMILY_ENV,
        "max_steps":m.MAX_STEPS,
        "arms":list(m.ARMS),
        "training_behaviour":"coldstart_public_causal_map_teacher_each_episode"}


def verify_manifest():
    if m.digest(manifest())!=MANIFEST_HASH:
        raise AssertionError("MG21_REGISTERED_MANIFEST_DRIFT")
    if m.SCHEMA!="yggdrasil.dg1-mg20-original.v1":
        raise AssertionError("MG21_FROZEN_CORE_CHANGED")


def teacher_trace(env,seed):
    """Only a freshly reset public-input navigator. Exactly one real env trajectory."""
    return m.make_trace(env,seed,policy_model=m.MapPolicy("causal_map"))


def train_on_positive_teacher(agents,seed_set,envs,stage):
    observations=[]
    successes=0
    paid=0
    for env in envs:
        for seed in seed_set:
            episode=teacher_trace(env,seed)
            if episode["steps"]!=len(episode["transitions"]):
                raise AssertionError("MG21_UNCHARGED_TEACHER_EVENTS")
            successes+=episode["success"]
            paid+=episode["steps"]
            observations.append(m.episode_receipt(episode,None))
            m.train_on_shared(agents,episode,stage)
    return observations,successes,paid


def per_seed_wins(part):
    controls=[a for a in m.ARMS if a!="causal_map"]
    best=max(controls,key=lambda a:(part["metrics"][a]["mean_official_return"],a))
    own={x["seed"]:x["discounted_reward"] for x in part["episodes"]["causal_map"]}
    rival={x["seed"]:x["discounted_reward"] for x in part["episodes"][best]}
    if set(own)!=set(rival) or len(own)!=12:
        raise AssertionError("MG21_INCOMPLETE_HELDOUT_SEEDS")
    return best,sum(own[s]>rival[s]+1e-8 for s in own)


def run():
    verify_manifest()
    import minigrid,gymnasium,numpy
    if (minigrid.__version__!="3.2.0" or gymnasium.__version__!="1.4.0"
            or numpy.__version__!="2.3.4"):
        raise AssertionError("MG21_PACKAGE_DRIFT")
    agents={k:m.make_agent(k) for k in m.ARMS}
    training,successes,train_steps=train_on_positive_teacher(
        agents,TRAIN_SEEDS,m.TRAIN_ENVS,"train")
    if len(training)!=48:raise AssertionError("MG21_TRAIN_EPISODE_COUNT")
    cold_before=m.score(agents,m.COLD_ENV,COLD_SEEDS)
    interference,interference_goals,interference_steps=train_on_positive_teacher(
        agents,INTERFERENCE_SEEDS,(m.INTERFERENCE_ENV,),"interference")
    if len(interference)!=12:raise AssertionError("MG21_INTERFERENCE_COUNT")
    cold_after=m.score(agents,m.COLD_ENV,COLD_SEEDS)
    size=m.score(agents,m.SIZE_ENV,SIZE_SEEDS)
    family=m.score(agents,m.FAMILY_ENV,FAMILY_SEEDS)
    eval_splits={"cold_before":cold_before,"cold_after":cold_after,
                 "unseen_size":size,"unseen_family":family}
    total_steps=train_steps+interference_steps+sum(x["counted_env_steps"]
                                                  for x in eval_splits.values())
    if total_steps>38400 or len(training)+len(interference)!=60:
        raise AssertionError("MG21_PHYSICAL_ACTION_BUDGET_DRIFT")
    for stage,part in eval_splits.items():
        if len(part["seeds"])!=12 or len(part["episodes"])!=5 or any(
           len(eps)!=12 for eps in part["episodes"].values()):
            raise AssertionError("MG21_HELDOUT_EPISODE_COUNT")
    coverage={k:sum(part["metrics"][a]["success_count"] for a in m.ARMS)
        for k,part in (("unseen_size",size),("unseen_family",family))}
    valid_coverage=successes>=24 and all(v>=3 for v in coverage.values())
    gates={}
    wins={}
    control_winners={}
    for k,part in (("unseen_size",size),("unseen_family",family)):
        winner,num=per_seed_wins(part)
        wins[k]=num
        control_winners[k]=winner
        candidate=part["metrics"]["causal_map"]
        baseline=part["metrics"][winner]
        gates[k+"_reward_margin"]=candidate["mean_official_return"]>=baseline["mean_official_return"]+.04
        best_goals=max(part["metrics"][a]["success_count"] for a in m.ARMS if a!="causal_map")
        gates[k+"_success_nondegradation"]=candidate["success_count"]>=best_goals-1
        gates[k+"_per_seed_reward_wins"]=num>=5
    before=cold_before["metrics"]["causal_map"]["success_count"]
    after=cold_after["metrics"]["causal_map"]["success_count"]
    gates["cold_success_retention"]=after>=before-1
    gates["cold_vs_reactive"]=after>=cold_after["metrics"]["reactive"]["success_count"]
    cpu_ratio=round((size["metrics"]["causal_map"]["decision_cpu_ns"]+
                     family["metrics"]["causal_map"]["decision_cpu_ns"])/
                     max(1,size["metrics"]["recurrent_imitation"]["decision_cpu_ns"]+
                          family["metrics"]["recurrent_imitation"]["decision_cpu_ns"]),6)
    gates["cpu_vs_recurrent"]=cpu_ratio<=3.
    gates["checkpoint_bounded"]=all(len(m.save(v))<=65536 for v in agents.values())
    train_counts={"tabular_q":agents["tabular_q"].count,
                  "recurrent_imitation":agents["recurrent_imitation"].count,
                  "causal_map":agents["causal_map"].train_calls,
                  "sham_map":agents["sham_map"].train_calls}
    gates["both_controls_trained"]=all(v>=48 for v in train_counts.values())
    primary=valid_coverage and all(gates.values())
    partial=(
        any(part["metrics"]["causal_map"]["success_count"]>=
            part["metrics"][c]["success_count"]+2
            for part in (size,family)
            for c in m.ARMS if c!="causal_map") or
        (after>=before-1 and after>=11))
    classification=("INVALID_TASK_COVERAGE" if not valid_coverage else
                    "DEVELOPMENT_SIGNAL_ONLY" if primary else
                    "MIXED_DEV" if partial else "NEGATIVE_DEV")
    return {
        "schema":SCHEMA,"freeze_sha":FREEZE,"parent_sha":PARENT,
        "source_dependency_parent":CORE_SOURCE,"manifest_sha256":MANIFEST_HASH,
        "classification":classification,"primary_pass":primary,
        "scientific_acceptance":"UNVERIFIED",
        "training_teacher_goal_successes":successes,
        "interference_teacher_goal_successes":interference_goals,
        "training_episodes":48,"interference_episodes":12,
        "heldout_episodes":240,"total_episodes":300,
        "paid_training_steps":train_steps,"paid_interference_steps":interference_steps,
        "charged_total_steps":total_steps,"heldout_goal_coverage":coverage,
        "control_winners":control_winners,"per_seed_reward_wins":wins,
        "gates":gates,"cpu_ratio":cpu_ratio,"training_parameter_update_counts":train_counts,
        "training_traces":training,"interference_traces":interference,
        "checkpoint_sha256":{k:hashlib.sha256(m.save(v)).hexdigest() for k,v in agents.items()},
        "checkpoint_bytes":{k:len(m.save(v)) for k,v in agents.items()},
        "cold_before":cold_before,"cold_after":cold_after,
        "unseen_size":size,"unseen_family":family,
        "native_model_changed":False}


if __name__=="__main__":
    print(m.canon(run()))
