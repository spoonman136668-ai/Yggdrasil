"""AAI-11C frozen read-only causal prediction-versus-decision diagnostic.

No learner modification, new training experiment, or scientific first use.
Privileged simulator probes ONLY live in this evaluator; never passed to
original AAI-11B or graph_recent8 learner as learning data.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"AAI-11P"))
sys.path.insert(0,str(HERE.parent/"AAI-11A"))
sys.path.insert(0,str(HERE.parent/"AAI-11B"))
import world,controls,admission
import learner as graph
import fixture as previous_fixture
import contrast,dev as previous_dev

EXPECTED_CANDIDATE=2.084722222
EXPECTED_CONTROL=2.134027778
THRESHOLD=1e-6
METHODS=("aai11b_intervention_tournament","graph_recent8")


class PerfectPredictorDiagnostic:
    """PRIVILEGED scoring-only known-law adapter. Never a learner."""

    def __init__(self,law):
        if law not in world.LAWS:
            raise ValueError("unknown private diagnostic law")
        self._law=law

    def predict(self,x):
        return tuple(float(v) for v in world.intermediates(self._law,x))


def perfect_planner_rollout(law,x,goal):
    """Run the exact unchanged public planner with perfect diagnostic forecasts."""
    diagnostic=PerfectPredictorDiagnostic(law)
    current=world.copy_public(world.start(law,x,goal))
    actions=[]
    for _ in range(2):
        chosen=controls.plan(diagnostic,world.copy_public(current))
        if chosen is None:
            break
        if chosen not in world.ACTIONS:
            raise AssertionError("perfect forecast selected invalid do-action")
        current=world.copy_public(world.do(law,current,chosen))
        actions.append(world.ACTIONS.index(chosen))
    return current["reward"],tuple(actions)


def predict_bits(actor,x):
    probabilities=actor.predict(x)
    if len(probabilities)!=3 or any(not 0.<=v<=1. for v in probabilities):
        raise AssertionError("invalid predictor")
    return tuple(int(v>=.5) for v in probabilities)


def probe(actor,law):
    """Evaluate identical hidden-fact test grids. Never call actor.observe."""
    factual=[0,0,0]
    flips=[0,0,0]
    exact_flips=0
    changed_flips=[0,0,0]
    changed_exact=0
    changed_n=0
    for x in world.INPUTS:
        true=world.intermediates(law,x)
        inferred=predict_bits(actor,x)
        for bit in range(3):
            factual[bit]+=int(inferred[bit]==true[bit])
        for action in world.ACTIONS:
            x2=world.setbit(x,action)
            actual_second=world.intermediates(law,x2)
            inferred_second=predict_bits(actor,x2)
            actual_flip=tuple(a^b for a,b in zip(true,actual_second))
            predicted_flip=tuple(a^b for a,b in zip(inferred,inferred_second))
            for bit in range(3):
                flips[bit]+=int(predicted_flip[bit]==actual_flip[bit])
            exact_flips+=int(predicted_flip==actual_flip)
            if x!=x2:
                changed_n+=1
                for bit in range(3):
                    changed_flips[bit]+=int(predicted_flip[bit]==actual_flip[bit])
                changed_exact+=int(predicted_flip==actual_flip)
    n_x=len(world.INPUTS)
    n_do=n_x*len(world.ACTIONS)
    if changed_n!=n_do//2:
        raise AssertionError("nontrivial do-action count mismatches six-bit world")
    return {
        "factual_bit_accuracy":sum(factual)/(n_x*3),
        "factual_each_mediator":[q/n_x for q in factual],
        "intervention_flip_bit_accuracy":sum(flips)/(n_do*3),
        "intervention_flip_exact_three_bit_rate":exact_flips/n_do,
        "changed_input_flip_bit_accuracy":sum(changed_flips)/(changed_n*3),
        "changed_input_exact_three_bit_rate":changed_exact/changed_n,
        "evaluated_inputs":n_x,
        "evaluated_do_actions":n_do,
        "changed_do_actions":changed_n,
    }


def retained_contrasts(model):
    if len(model.rows)!=len(model.action_counts):
        raise ValueError("invalid action feedback alignment")
    count=0
    for index in range(1,len(model.rows)):
        if (model.action_counts[index]==model.action_counts[index-1]+1 and
            model.rows[index][0]!=model.rows[index-1][0]):
            count+=1
    return count


def compare_condition(key,law,budget,candidate_postB,baseline_postB):
    """Strongest conventional and frozen candidate on identical source and data."""
    world.fixture(key)
    if law not in world.TRANSFER or budget not in (2,4):
        raise ValueError("only frozen transfer diagnostic conditions")
    new_snapshot=previous_dev.challenge(candidate_postB,law,key,budget)
    old_snapshot=previous_fixture.challenge("graph_recent8",baseline_postB,
                                            law,key,budget)
    candidate=contrast.restore(new_snapshot)
    baseline=graph.restore("graph_recent8",old_snapshot)

    # Selected-rule disagreement is diagnostic only: not read by planner or model.
    disagreement=sum(a!=b for a,b in zip(candidate._selection(),
                                         graph.selected(baseline.stats)))
    candidate_metrics=probe(candidate,law)
    baseline_metrics=probe(baseline,law)

    if contrast.checkpoint(candidate)!=new_snapshot:
        raise AssertionError("candidate diagnostic probe mutated source")
    if graph.checkpoint("graph_recent8",baseline)!=old_snapshot:
        raise AssertionError("control diagnostic probe mutated source")

    episode_records=[]
    for x,g in admission.contexts(key,law,12):
        cand=previous_dev.episode(new_snapshot,law,x,g)
        ref=previous_fixture.episode("graph_recent8",old_snapshot,law,x,g)
        perfect,perfect_actions=perfect_planner_rollout(law,x,g)
        oracle=world.exact_oracle(law,x,g)
        if perfect>oracle+1e-10 or cand[0]>oracle+1e-10 or ref[0]>oracle+1e-10:
            raise AssertionError("action outcomes exceeded two-step exact oracle")
        episode_records.append({
            "candidate_reward":cand[0],
            "baseline_reward":ref[0],
            "perfect_planner_reward":perfect,
            "oracle_reward":oracle,
            "candidate_goal_correct":cand[1],
            "baseline_goal_correct":ref[1],
            "candidate_actions":tuple(cand[2]),
            "baseline_actions":tuple(ref[2]),
            "perfect_actions":perfect_actions,
        })
    if contrast.checkpoint(contrast.restore(new_snapshot))!=new_snapshot:
        raise AssertionError("candidate cold source changed after scored episodes")
    if graph.checkpoint("graph_recent8",
                        graph.restore("graph_recent8",old_snapshot))!=old_snapshot:
        raise AssertionError("baseline cold source changed after scored episodes")
    return {
        "candidate":candidate_metrics,
        "control":baseline_metrics,
        "selected_rules_different":disagreement,
        "retained_public_do_pairs":retained_contrasts(candidate),
        "episodes":episode_records
    }


def _mean(values):
    if not values:
        raise ValueError("empty diagnostic")
    return sum(values)/len(values)


def classification(candidate,control,perfect_gap,reward_gap):
    if perfect_gap>.05+1e-10:
        return "PLANNER_LIMITATION_DETECTED"
    if (reward_gap<=-.03 and (
        candidate["factual_bit_accuracy"] <= control["factual_bit_accuracy"]-.01 or
        candidate["intervention_flip_bit_accuracy"] <=
        control["intervention_flip_bit_accuracy"]-.01)):
        return "HYPOTHESIS_SELECTION_LIMIT_DIAGNOSTIC"
    if (reward_gap<=-.03 and
        candidate["factual_bit_accuracy"]>=control["factual_bit_accuracy"]-.01 and
        candidate["intervention_flip_bit_accuracy"]>=
        control["intervention_flip_bit_accuracy"]-.01):
        return "POLICY_OR_CALIBRATION_MISMATCH_DIAGNOSTIC"
    return "MIXED_OR_INCONCLUSIVE_DIAGNOSTIC"


def mechanical_attribution():
    prereg=json.loads((HERE/"prereg.json").read_text(encoding="utf8"))
    if (prereg["id"]!="AAI-11C" or prereg["science"]["cohorts_consumed"] or
        prereg["science"]["science_first_use_authorized"]):
        raise PermissionError("AAI11C SCIENTIFIC FIRST USE DISARMED")
    all_episodes=[]
    probes={"candidate":[],"control":[]}
    rule_diffs=[]
    public_pairs=[]
    conditions=[]
    receipt=[]
    for key in world.FIXTURES:
        cand_postB,cand_rows,_=previous_dev.train(key)
        baseline_posts,base_rows,_=previous_fixture.common_training(
            key,names=("graph_recent8",))
        if cand_rows!=base_rows:
            raise AssertionError("candidate and baseline did not see identical training")
        initial_candidate_hash=hashlib.sha256(cand_postB.encode()).hexdigest()
        initial_baseline_hash=hashlib.sha256(baseline_posts["graph_recent8"].encode()).hexdigest()
        for law in world.TRANSFER:
            for n in (2,4):
                result=compare_condition(key,law,n,cand_postB,
                                         baseline_posts["graph_recent8"])
                conditions.append((key,law,n))
                rule_diffs.append(result["selected_rules_different"])
                public_pairs.append(result["retained_public_do_pairs"])
                for name in probes:
                    probes[name].append(result[name])
                all_episodes.extend(result["episodes"])
        if hashlib.sha256(cand_postB.encode()).hexdigest()!=initial_candidate_hash:
            raise AssertionError("trained candidate checkpoint changed")
        if hashlib.sha256(baseline_posts["graph_recent8"].encode()).hexdigest()!=initial_baseline_hash:
            raise AssertionError("trained baseline checkpoint changed")
        receipt.append([key,initial_candidate_hash,initial_baseline_hash])
    if len(conditions)!=24 or len(all_episodes)!=288:
        raise AssertionError("unfrozen public fixture topology")
    c_reward=_mean([z["candidate_reward"] for z in all_episodes])
    b_reward=_mean([z["baseline_reward"] for z in all_episodes])
    if (abs(c_reward-EXPECTED_CANDIDATE)>THRESHOLD or
        abs(b_reward-EXPECTED_CONTROL)>THRESHOLD):
        raise AssertionError("original immutable development reward not reproduced")
    oracle=_mean([z["oracle_reward"] for z in all_episodes])
    perfect=_mean([z["perfect_planner_reward"] for z in all_episodes])
    aggregates={}
    for name in probes:
        aggregates[name]={
            "mean_factual_bit_accuracy":_mean([z["factual_bit_accuracy"] for z in probes[name]]),
            "factual_each_mediator":[_mean([z["factual_each_mediator"][i]
                                           for z in probes[name]]) for i in range(3)],
            "mean_flip_bit_accuracy":_mean([z["intervention_flip_bit_accuracy"]
                                            for z in probes[name]]),
            "mean_changed_input_flip_bit_accuracy":_mean(
                [z["changed_input_flip_bit_accuracy"] for z in probes[name]]),
            "mean_changed_input_exact_flip_accuracy":_mean(
                [z["changed_input_exact_three_bit_rate"] for z in probes[name]]),
            "mean_all_exact_flip_accuracy":_mean(
                [z["intervention_flip_exact_three_bit_rate"] for z in probes[name]]),
        }
    reward_gap=c_reward-b_reward
    perfect_gap=oracle-perfect
    diag=classification({
        "factual_bit_accuracy":aggregates["candidate"]["mean_factual_bit_accuracy"],
        "intervention_flip_bit_accuracy":aggregates["candidate"]["mean_flip_bit_accuracy"]},
        {"factual_bit_accuracy":aggregates["control"]["mean_factual_bit_accuracy"],
         "intervention_flip_bit_accuracy":aggregates["control"]["mean_flip_bit_accuracy"]},
        perfect_gap,reward_gap)
    paired=[z["candidate_reward"]-z["baseline_reward"] for z in all_episodes]
    return {
        "schema":"yggdrasil.contrib.aai11c.diagnostic.v1",
        "status":"SYNTHETIC_SOURCE_DIAG_ONLY_NOT_SCIENCE",
        "diagnostic_class":diag,
        "candidate_reward":round(c_reward,9),
        "control_reward":round(b_reward,9),
        "candidate_minus_control":round(reward_gap,9),
        "oracle_reward":round(oracle,9),
        "perfect_predictor_shared_planner_reward":round(perfect,9),
        "oracle_minus_perfect_planner":round(perfect_gap,9),
        "oracle_minus_candidate":round(oracle-c_reward,9),
        "oracle_minus_control":round(oracle-b_reward,9),
        "candidate_goal_success":round(_mean([z["candidate_goal_correct"] for z in all_episodes]),9),
        "control_goal_success":round(_mean([z["baseline_goal_correct"] for z in all_episodes]),9),
        "prediction":aggregates,
        "mean_rule_index_disagreements":_mean(rule_diffs),
        "conditions_with_any_different_selected_rule":sum(x>0 for x in rule_diffs),
        "mean_retained_public_contrast_pairs":_mean(public_pairs),
        "conditions_no_retained_public_contrast_pairs":sum(x==0 for x in public_pairs),
        "candidate_better_episodes":sum(x>1e-10 for x in paired),
        "candidate_worse_episodes":sum(x< -1e-10 for x in paired),
        "paired_same_reward_episodes":sum(abs(x)<=1e-10 for x in paired),
        "score_trace_sha256":hashlib.sha256(
            controls.canonical(all_episodes).encode()).hexdigest(),
        "snapshot_trace_sha256":hashlib.sha256(
            controls.canonical(receipt).encode()).hexdigest(),
        "worlds":list(world.FIXTURES),"condition_count":len(conditions),
        "episode_count":len(all_episodes),
        "factual_queries_per_method":len(conditions)*64,
        "do_action_queries_per_method":len(conditions)*64*12,
        "science_cohorts_used":0,"first_use_authorized":False,
        "native_model_changed":False,
        "interpretation":"PRIVATE_EVALUATION_PROBES_NEVER_LEARNER_TRAINING",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mechanical-diagnostic",action="store_true")
    p.add_argument("--primary",action="store_true")
    args=p.parse_args()
    if args.primary:
        p.error("AAI11C SCIENTIFIC FIRST USE DISARMED")
    if not args.mechanical_diagnostic:
        p.error("only three frozen synthetic diagnostic fixtures supported")
    print("AAI11C_DIAGNOSTIC="+json.dumps(mechanical_attribution(),sort_keys=True),
          flush=True)


if __name__=="__main__":
    main()
