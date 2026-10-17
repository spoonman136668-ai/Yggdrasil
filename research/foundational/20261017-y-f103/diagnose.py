"""Y-F103: source-only diagnosis of delayed credit and on-policy state shift.

Never trains on F102 GUARD, any F103 diagnostic, or reserved F62 cohorts.
Offline future-answer interventions happen AFTER the online decisions freeze.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PREREG_BLOB="dfd19d39dbdd4efc82e73c5bf7948ea508257f72"
F102_BLOB="8686390483c1e367c5cc1016a865a15c926b8376"
F102_PREREG_BLOB="4f3a8bf295a2f695a039d6b71d87d3bff3939e76"
CHECKPOINTS=(11,23,35,47,59,71)
DIAGS=((-14001,-51,"raw",48),(-14101,-52,"swap_roles_and_invert",56))
SCHEMA="yggdrasil.f103.credit-support-onpolicy-shift-public.v1"

class Invalid(ValueError): pass
def require(flag,reason):
    if not flag:raise Invalid("F103_"+reason)
def gitblob(path):
    b=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def load():
    require(gitblob(HERE/"prereg.json")==PREREG_BLOB and
            gitblob(ROOT/"20261017-y-f102"/"delayed_credit.py")==F102_BLOB and
            gitblob(ROOT/"20261017-y-f102"/"prereg.json")==F102_PREREG_BLOB,
            "PREREG_OR_F102_FROZEN_SOURCE_DRIFT")
    prereg=json.loads((HERE/"prereg.json").read_text())
    require(prereg["schema"]==
           "yggdrasil.f103.credit-sparsity-onpolicy-support-prereg.v1" and
           prereg["parent"]["F102_exact_head"]==
           "c412b42b5aa5d9222343696bd14e3a76656ce33e" and
           all(x is True for x in prereg["authority"].values()),
           "PREREG_AUTHORITY_OR_PARENT_INVALID")
    spec=importlib.util.spec_from_file_location("yf103_f102_frozen",
             ROOT/"20261017-y-f102"/"delayed_credit.py")
    src=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=src
    spec.loader.exec_module(src)
    cfg,f101,f99,native=src.source_modules()
    return prereg,src,native

def digest(mem,pack):
    return hashlib.sha256(b"".join(pack.pack(*rec) for rec in mem)).hexdigest()

def diff_actions(actions,baseline):
    basis=[a[4] for a in actions if a[3]==baseline]
    require(len(basis)==1,"F60_BASELINE_NOT_IN_NATIVE_ACTIONS")
    return tuple(tuple(round(a-b,12) for a,b in zip(act[4],basis[0]))
                 for act in actions)

def dot(weights,x):
    require(len(weights)==12 and len(x)==12,"NATIVE_FEATURE_DIMENSION")
    return sum(w*v for w,v in zip(weights,x))

def nearest(feature,training_pool):
    require(training_pool,"EMPTY_TRAIN_SUPPORT")
    dist=min(math.sqrt(sum((a-b)**2 for a,b in zip(feature,reference)))
             for reference in training_pool)
    return dist

@dataclass(frozen=True)
class FrozenDecision:
    index:int
    prefix_mem:tuple
    native_states:tuple
    chosen_index:int
    baseline_index:int
    chosen_delta:tuple
    teacher_state_hash:str
    current_state_hash:str
    scored_native_count:int
    policy_memory_after:tuple

def public_rollout(native,pack,stream,weights):
    """No future query, answer, seed, family, offline labels or graph truth."""
    require(len(stream)==72 and
            all(type(edge) is tuple and len(edge)==3 for edge in stream),
            "SOURCE_PUBLIC_EVENT_ONLY")
    memory=()
    teacher=()
    selected=[]
    trace=[]
    for index,event in enumerate(stream):
        teacher_actions=native.actions(teacher,event,index,pack)
        teacher_base=native._f60_step(teacher,event,pack)
        teacher_delta=diff_actions(teacher_actions,teacher_base)
        tchoice=max(range(len(teacher_actions)),
                    key=lambda j:(dot(weights,teacher_delta[j]),-j))
        actions=native.actions(memory,event,index,pack)
        baseline=native._f60_step(memory,event,pack)
        deltas=diff_actions(actions,baseline)
        choice=max(range(len(actions)),
                   key=lambda j:(dot(weights,deltas[j]),-j))
        require(len(actions)>0 and
                0<=choice<len(actions),"INVALID_ONLINE_ACTION")
        if index in CHECKPOINTS:
            trace.append((FrozenDecision(
                index,tuple(memory),tuple(a[3] for a in actions),
                choice,next(j for j,a in enumerate(actions) if a[3]==baseline),
                deltas[choice],
                digest(teacher,pack),digest(memory,pack),
                len(actions),tuple(actions[choice][3])),
                dict(
                checkpoint=index,
                teacher_and_learner_memory_identical=(memory==teacher),
                teacher_chosen_action_delta=teacher_delta[tchoice],
                teacher_native_actions=len(teacher_actions),
                learner_chosen_action_delta=deltas[choice],
                learner_native_actions=len(actions),
                learner_action_index=choice,
                teacher_action_index=tchoice,
                teacher_prefix_sha256=digest(teacher,pack),
                learner_prefix_sha256=digest(memory,pack),
                selected_memory_sha256=digest(actions[choice][3],pack),
                online_future_question_visible=False,
                source_native_memory_bytes=12*len(actions[choice][3]))))
        teacher=teacher_base
        memory=actions[choice][3]
        native._valid_memory(memory,pack)
    require(len(trace)==len(CHECKPOINTS),"CHECKPOINT_MISSING")
    return memory,teacher,tuple(trace),tuple(selected)

def offline_counterfactual(native,pack,stream,question,point):
    """Evaluate hidden answer only after rollout has chosen memory/actions."""
    need=point.index
    outcomes=[]
    for candidate in point.native_states:
        finish=native._finish_fixed(candidate,stream[need+1:],pack)
        outcomes.append(int(pack.solve(finish,question)==question["answer"]))
    chosen=outcomes[point.chosen_index]
    base=outcomes[point.baseline_index]
    return dict(
        actual_chosen_correct_under_F60_suffix=chosen,
        F60_baseline_correct_under_F60_suffix=base,
        any_better_alternative=(max(outcomes)>chosen),
        best_available_local_counterfactual=max(outcomes),
        native_action_rewards=outcomes,
        any_nonzero_local_advantage=any(x!=base for x in outcomes),
        chosen_action_delta_from_local_F60=chosen-base,
        offline_future_answer_exclusively_here=True)

def summarize_labels(rows):
    counts=Counter(y for x,y in rows)
    require(set(counts)<=set((-1,0,1)) and sum(counts.values())==len(rows),
            "MALFORMED_TRAIN_LABELS")
    collisions={}
    for x,y in rows:
        key=tuple(round(v,12) for v in x)
        collisions.setdefault(key,set()).add(y)
    zero_key=(0.,)*12
    zero=Counter(y for x,y in rows if tuple(x)==zero_key)
    return dict(total=len(rows),neg=counts[-1],zero=counts[0],
                pos=counts[1],zero_fraction=round(counts[0]/len(rows),8),
                sparse_over_90_percent=counts[0]/len(rows)>.9,
                conflicting_same_features=sum(len(y)>1 for y in collisions.values()),
                zero_feature_reward_counts={str(k):zero[k] for k in (-1,0,1)},
                distinct_delta_vectors=len(collisions))

def evaluate(commit):
    require(type(commit) is str and len(commit)==40 and
            all(c in "0123456789abcdef" for c in commit),
            "EXACT_GIT_COMMIT_REQUIRED")
    cfg,f102,native=load()
    pack=native.codec()
    # Reconstruct ONLY the exact 16 frozen F102 TRAIN episodes. We do NOT
    # call F102.source_split(), which would unnecessarily materialize the
    # consumed F102 GUARD cases. Their identities and outcomes are untouched.
    train=[]
    for family_index,family in enumerate((-31,-32)):
        for offset in range(8):
            seed=f102.TRAIN_START-offset
            stream,q,identity=f102.episode(native,seed,family,"raw",
                                            family_index*8+offset)
            train.append((seed,family,stream,q,identity))
    train=tuple(train)
    require(len(train)==16 and len(set(x[4] for x in train))==16,
            "PARENT_TRAIN_IDENTITY")
    examples=f102.train_examples(native,pack,train)
    training_pool=frozenset(tuple(round(v,12) for v in x) for x,y in examples)
    label_stats=summarize_labels(examples)
    weights,train_curve=f102.train_linear(examples,"raw")
    require(len(weights)==12 and len(train_curve)==4,"TRAIN_FIT_DRIFT")
    blocks=[]
    for block_index,(first,family,mode,namespace) in enumerate(DIAGS):
        episodes=[]
        for offset in range(8):
            seed=first-offset
            stream,q,identity=f102.episode(native,seed,family,mode,
                                            namespace+offset)
            learned_memory,F60_memory,checkpoints,_=public_rollout(
                native,pack,stream,weights)
            correct_l=int(pack.solve(learned_memory,q)==q["answer"])
            correct_f=int(pack.solve(F60_memory,q)==q["answer"])
            rows=[]
            for point,record in checkpoints:
                local=offline_counterfactual(native,pack,stream,q,point)
                # Original frozen F102 TRAIN action-delta support only.
                learner=tuple(round(v,12) for v in record[
                    "learner_chosen_action_delta"])
                teacher=tuple(round(v,12) for v in record[
                    "teacher_chosen_action_delta"])
                rows.append({**record,**local,
                    "learner_delta_exact_in_TRAIN_teacher_support":
                        learner in training_pool,
                    "teacher_delta_exact_in_TRAIN_teacher_support":
                        teacher in training_pool,
                    "learner_min_euclidean_to_TRAIN_support":
                        round(nearest(learner,training_pool),9),
                    "teacher_min_euclidean_to_TRAIN_support":
                        round(nearest(teacher,training_pool),9)})
            require(len(rows)==6 and
                    all(x["source_native_memory_bytes"]<=144 for x in rows),
                    "MISSING_OR_OVERBUDGET_CHECKPOINT")
            episodes.append(dict(
                source_seed_OFFLINE_ONLY=seed,
                graph_structural_sha256=identity,
                events=72,
                terminal_correct_F60=correct_f,
                terminal_correct_learned=correct_l,
                retained_F60_sha256=digest(F60_memory,pack),
                retained_learned_sha256=digest(learned_memory,pack),
                checkpoints=rows))
        blocks.append(dict(name=cfg["source"]["NEW_F103_DIAGNOSTIC"][block_index]["name"],
                           policy_change_mode=mode,
                           episodes=episodes))
    flatten=[c for block in blocks for row in block["episodes"]
             for c in row["checkpoints"]]
    total=len(flatten)
    learner_out=sum(not x["learner_delta_exact_in_TRAIN_teacher_support"]
                    for x in flatten)
    teach_out=sum(not x["teacher_delta_exact_in_TRAIN_teacher_support"]
                  for x in flatten)
    ldist=sum(x["learner_min_euclidean_to_TRAIN_support"] for x in flatten)/total
    tdist=sum(x["teacher_min_euclidean_to_TRAIN_support"] for x in flatten)/total
    result=dict(
      schema="yggdrasil.f103.teacher-credit-onpolicy-diagnostic.v1",
      exact_head=commit,
      source_kind="PUBLIC_SYNTHETIC_DIAG_NOT_UNTOUCHED_SCIENCE",
      inherited_F102_head=cfg["parent"]["F102_exact_head"],
      parent_code_git_blob=F102_BLOB,
      prereg_git_blob=PREREG_BLOB,
      train_source_count=len(train),training_examples=len(examples),
      label_support=label_stats,training_cycle_diagnostics=train_curve,
      native_parameter_count=12,
      fresh_F103_diagnostic_episodes=16,
      F102_GUARD_not_read_for_training_or_selection=True,
      reserved_F62_source_sets_untouched=True,
      all_future_queries_hidden_from_online_scorer=True,
      native_memory_limit_bytes=144,
      blocks=blocks,
      checkpoint_count=total,
      teacher_checkpoint_out_of_TRAIN_support=teach_out,
      learned_checkpoint_out_of_TRAIN_support=learner_out,
      teacher_mean_nearest_TRAIN_distance=round(tdist,9),
      learner_mean_nearest_TRAIN_distance=round(ldist,9),
      fraction_learner_out_of_TRAIN_support=round(learner_out/total,8),
      learned_vs_teacher_state_mismatch_count=sum(
          not x["teacher_and_learner_memory_identical"] for x in flatten),
      learner_local_retro_counterfactual_regret_count=sum(
          x["any_better_alternative"] for x in flatten),
      some_local_action_has_nonzero_F60_suffix_advantage=sum(
          x["any_nonzero_local_advantage"] for x in flatten),
      F103_terminal_correct_frozen_F60=sum(
          ep["terminal_correct_F60"] for block in blocks for ep in block["episodes"]),
      F103_terminal_correct_frozen_F102_raw=sum(
          ep["terminal_correct_learned"] for block in blocks for ep in block["episodes"]),
      sparsity_precommitted_threshold_met=label_stats["sparse_over_90_percent"],
      onpolicy_shift_precommitted_threshold_met=(
          learner_out/total>.25 and ldist>tdist),
      interpretation="DIAGNOSE_ONLY_NO_GUARD_MODEL_SELECTION_OR_NEW_LEARNER",
      causation_of_F102_failure_not_established=True,
      independent_scientific_firstuse=False,
      protected_science_accepted=False,
      optimizer_promoted=False,
      accepted_ref_mutations=0,
      external_CKB_controller_access=False,
      Codex_used=False,MindPalace_written=False)
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-ref",required=True)
    args=parser.parse_args()
    print(json.dumps(evaluate(args.source_ref),sort_keys=True,separators=(",",":")))
if __name__=="__main__": main()
