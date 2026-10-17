"""Y-F104: TRAIN-only structural causal credit, with teacher/on-policy ablations.

The F104 frozen prereg precedes this source. Offline TRAIN teacher may inspect
future answer paths. All online policies receive ONLY public native 72-event
streams, native candidate features, and fixed TRAIN-fitted weights. GUARD uses
fresh negative-seed synthetic sources, NEVER protected FIT/DIAG/ORIGINAL.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PREREG_BLOB="60757f68e275a9af7c4179fe54a26b3406be8de7"
F103_BLOB="a9f58b5d96e4ba15283961bc4bc2db6ed09ccf0a"
F102_BLOB="8686390483c1e367c5cc1016a865a15c926b8376"
PARENT_SHA="bf844517215e5e8374c7a5409cc417a04943eb5b"
TRAIN=((-15001,-61,"raw",0),(-15101,-62,"raw",8))
GUARD=((-16001,-71,"raw",16),(-16101,-72,"swap_roles_and_invert",24),
       (-16201,-73,"reverse_order",32))
CHECKPOINTS=(11,23,35,47,59,71)
SCHEMA="yggdrasil.f104.structural-credit-onpolicy-public.v1"
class Rejected(ValueError): pass
def require(ok,code):
    if not ok:raise Rejected("F104_"+code)
def blob(path):
    data=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def load():
    require(blob(HERE/"prereg.json")==PREREG_BLOB and
            blob(ROOT/"20261017-y-f103"/"diagnose.py")==F103_BLOB and
            blob(ROOT/"20261017-y-f102"/"delayed_credit.py")==F102_BLOB,
            "PREREG_OR_FROZEN_PARENT_DRIFT")
    cfg=json.loads((HERE/"prereg.json").read_text())
    require(cfg["schema"]=="yggdrasil.f104.causal-structural-credit-precode.v1" and
            cfg["parent"]["f103_exact_head"]==PARENT_SHA and
            all(v is True for v in cfg["authority"].values()) and
            cfg["source"]["train"][0]["seeds"]==[-15001,-15008] and
            cfg["source"]["guard"][2]["seeds"]==[-16201,-16208],
            "FROZEN_CASES_OR_AUTHORITY_DRIFT")
    spec=importlib.util.spec_from_file_location(
        "yf104_frozen_f103",ROOT/"20261017-y-f103"/"diagnose.py")
    parent=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=parent
    spec.loader.exec_module(parent)
    _,f102,native=parent.load()
    return cfg,parent,f102,native

def source_groups(f102,native,definitions):
    result=[]
    for first,family,mode,namespace in definitions:
        episodes=[]
        for offset in range(8):
            seed=first-offset
            public,question,identity=f102.episode(native,seed,family,
                                                    mode,namespace+offset)
            require(len(public)==72 and seed<0 and family<0,
                    "PROTECTED_OR_NONNATIVE_SOURCE")
            episodes.append((seed,public,question,identity))
        result.append(tuple(episodes))
    return tuple(result)

def source_path(public,q):
    """TRAIN-only: exact native directed/signed walk to eventual known answer.

    Returned path contains ground-truth edge orientations but never becomes
    input to an online scorer or a GUARD policy.
    """
    by_node={}
    for a,r,b in public:
        by_node.setdefault(a,[]).append((r,1,b))
        by_node.setdefault(b,[]).append((r,-1,a))
    for edges in by_node.values():
        edges.sort()
    ops=tuple(q["ops"])
    result=[]
    def walk(node,index,nodes):
        if index==len(ops):
            return tuple(nodes) if node==q["answer"] else None
        role,direction=ops[index]
        for r,d,dest in by_node.get(node,()):
            if r==role and d==direction and dest not in nodes:
                candidate=walk(dest,index+1,nodes+(dest,))
                if candidate is not None:return candidate
        return None
    nodes=walk(q["start"],0,(q["start"],))
    require(nodes is not None and len(nodes)==len(ops)+1,
            "SOURCE_ANSWER_PATH_NOT_REPRODUCIBLE")
    return nodes,tuple(2*r+int(d==-1) for r,d in ops)

def subpaths(nodes,codes):
    # Supports multi-role atomic native records only when their REAL endpoints
    # and complete ordered signed role sequence match a contiguous source path.
    spans=set()
    for start in range(len(codes)):
        for finish in range(start+1,min(len(codes),start+6)+1):
            spans.add((nodes[start],nodes[finish],tuple(codes[start:finish])))
    return spans

def structural_retained_score(mem,spans,native):
    score=0
    for record in mem:
        u,v,roles=record
        if (u,v,tuple(roles)) in spans:
            score+=len(roles)
        # Reverse traversal describes the same structural support, counted
        # once per retained native record, never inventing another memory cell.
        elif (v,u,tuple(code^1 for code in reversed(roles))) in spans:
            score+=len(roles)
    return score

def action_deltas(parent,actions,baseline):
    return parent.diff_actions(actions,baseline)

def online_teacher_and_explorer(native,pack,public,weights,checkpoints=True):
    """Track true independent source-native F60 and F102-fitted memories."""
    teacher=()
    explorer=()
    states=[]
    for i,event in enumerate(public):
        tm=teacher
        em=explorer
        ta=native.actions(tm,event,i,pack)
        tnext=native._f60_step(tm,event,pack)
        ea=native.actions(em,event,i,pack)
        ebase=native._f60_step(em,event,pack)
        edeltas=action_deltas(PARENT,ea,ebase)
        choose=max(range(len(ea)),key=lambda j:(
            sum(w*x for w,x in zip(weights,edeltas[j])),-j))
        if checkpoints and i in CHECKPOINTS:
            states.append((i,
                 ("F60_teacher",tm,ta,tnext),
                 ("F102_onpolicy",em,ea,ebase)))
        teacher=tnext
        explorer=ea[choose][3]
        native._valid_memory(teacher,pack)
        native._valid_memory(explorer,pack)
    return tuple(states),teacher,explorer

# Set only after a verified import of the frozen F103 parent, NEVER mutated by
# any GUARD case. All code paths use the same exact F62 source and codec.
PARENT=None

def collect_examples(native,pack,train,f102,parent,old_weights):
    global PARENT
    PARENT=parent
    teacher_rows=[]
    onpolicy_rows=[]
    receipts=[]
    for group_index,group in enumerate(train):
        for episode_index,(seed,public,q,sourceid) in enumerate(group):
            nodes,codes=source_path(public,q)
            spans=subpaths(nodes,codes)
            checkpoints,_,_=online_teacher_and_explorer(
                native,pack,public,old_weights)
            for t,teachers,explorers in checkpoints:
                for label,(origin,memory,legal,baseline) in enumerate(
                    (teachers,explorers)):
                    diffs=action_deltas(parent,legal,baseline)
                    base_reward=structural_retained_score(
                        baseline,spans,native)
                    count=Counter()
                    for delta,action in zip(diffs,legal):
                        other_reward=structural_retained_score(
                            action[3],spans,native)
                        advantage=1 if other_reward>base_reward else (
                            -1 if other_reward<base_reward else 0)
                        count[advantage]+=1
                        if label==0:teacher_rows.append((delta,advantage))
                        else:onpolicy_rows.append((delta,advantage))
                    receipts.append(dict(
                        source_sha256=sourceid,source_group=group_index,
                        episode_index=episode_index,checkpoint=t,
                        collection_mode=origin,actions=len(legal),
                        baseline_structural_overlap=base_reward,
                        native_memory_before=len(memory),
                        credit_neg=count[-1],credit_zero=count[0],
                        credit_pos=count[1],
                        training_oracle_exclusive=True,
                        query_visible_to_online_scorer=False))
    require(len(receipts)==16*6*2 and
            len(teacher_rows)>0 and len(onpolicy_rows)>0,
            "TRAIN_CREDIT_ROWS_MISSING")
    return tuple(teacher_rows),tuple(onpolicy_rows),receipts

def support_report(rows):
    count=Counter(label for _,label in rows)
    collisions={}
    for x,label in rows:
        k=tuple(round(v,12) for v in x)
        collisions.setdefault(k,set()).add(label)
    return dict(total=len(rows),positive=count[1],negative=count[-1],
                zero=count[0],
                positive_fraction=round(count[1]/len(rows),8),
                zero_fraction=round(count[0]/len(rows),8),
                conflicting_feature_vectors=sum(len(v)>1 for v in collisions.values()),
                distinct_feature_vectors=len(collisions))

def policy_memory(native,pack,public,weights):
    return F102.learned_online(native,public,pack,
        lambda diff:sum(w*x for w,x in zip(weights,diff)))[0]

F102=None

def evaluate(head):
    require(isinstance(head,str) and len(head)==40 and
            all(x in "0123456789abcdef" for x in head),
            "INVALID_GIT_HEAD")
    global F102,PARENT
    cfg,PARENT,F102,native=load()
    pack=native.codec()
    train=source_groups(F102,native,TRAIN)
    # Only replicate original F102 TRAIN for frozen control weights: do not
    # call original source_split(), as it materializes consumed GUARD cases.
    original_train=[]
    for group_index,family in enumerate((-31,-32)):
        for i in range(8):
            seed=F102.TRAIN_START-i
            stream,q,sourceid=F102.episode(native,seed,family,"raw",
                                           group_index*8+i)
            original_train.append((seed,family,stream,q,sourceid))
    old_labeled=F102.train_examples(native,pack,original_train)
    old_weights,_=F102.train_linear(old_labeled,"raw")
    teacher_rows,explorer_rows,teacher_receipts=collect_examples(
         native,pack,train,F102,PARENT,old_weights)
    mixed_rows=teacher_rows+explorer_rows
    teacher_weights,teacher_train_curve=F102.train_linear(teacher_rows,"raw")
    mixed_weights,mixed_train_curve=F102.train_linear(mixed_rows,"raw")
    support=dict(teacher=support_report(teacher_rows),
                 onpolicy=support_report(explorer_rows),
                 mixed=support_report(mixed_rows))
    # Freeze ALL fitted variants BEFORE the first F104 GUARD question exists.
    guard=source_groups(F102,native,GUARD)
    blocks=[]
    for family_index,group in enumerate(guard):
        cases=[]
        for index,(seed,public,q,sourceid) in enumerate(group):
            fixed=()
            for event in public:
                fixed=native._f60_step(fixed,event,pack)
            outcomes={
              "F60_fixed":F102.terminal_score(pack,fixed,q),
              "F102_original_raw":F102.terminal_score(
                  pack,policy_memory(native,pack,public,old_weights),q),
              "F104_teacher_credit":F102.terminal_score(
                  pack,policy_memory(native,pack,public,teacher_weights),q),
              "F104_mixed_onpolicy_credit":F102.terminal_score(
                  pack,policy_memory(native,pack,public,mixed_weights),q),
              "F62_zero":F102.terminal_score(
                  pack,policy_memory(native,pack,public,(0.,)*12),q)}
            require(all(x in (0,1) for x in outcomes.values()),
                    "BAD_TERMINAL_SCORE")
            cases.append(dict(case_id=f"{family_index}:{index}",
                              identity_sha256=sourceid,events=len(public),
                              requested_role_hops=len(q["ops"]),
                              outcome=outcomes,source_seed_OFFLINE_ONLY=seed,
                              question_visible_to_online_policy=False,
                              memory_budget_bytes=144))
        names=tuple(cases[0]["outcome"])
        blocks.append(dict(name=cfg["source"]["guard"][family_index]["name"],
             cases=cases,correct={
                 a:sum(row["outcome"][a] for row in cases) for a in names}))
    total={a:sum(b["correct"][a] for b in blocks)
           for a in blocks[0]["correct"]}
    teacher_signal=(support["mixed"]["positive"]>0 and
                    support["mixed"]["negative"]>0)
    onpolicy_value=total["F104_mixed_onpolicy_credit"] >= (
        total["F104_teacher_credit"]+3) and all(
         b["correct"]["F104_mixed_onpolicy_credit"]>=
         b["correct"]["F104_teacher_credit"] for b in blocks)
    positive=teacher_signal and total["F104_mixed_onpolicy_credit"] >= (
         total["F60_fixed"]+4) and all(
         b["correct"]["F104_mixed_onpolicy_credit"]>=
         b["correct"]["F60_fixed"] for b in blocks) and (
         total["F104_mixed_onpolicy_credit"]>
         max(total["F102_original_raw"],total["F62_zero"]))
    return dict(
      schema="yggdrasil.f104.causal-credit-teacher-onpolicy-public.v1",
      exact_head=head,parent_F103_exact_sha=PARENT_SHA,
      prereg_git_blob=PREREG_BLOB,
      frozen_F102_git_blob=F102_BLOB,
      source_kind="SOURCE_ONLY_PUBLIC_SYNTHETIC_NEW_FAMILIES_NOT_PROTECTED",
      original_F102_F103_GUARD_never_loaded=True,
      TRAIN_episodes=16,GUARD_episodes=24,GUARD_blocks=blocks,
      native_actions_and_144byte_record_cap_unchanged=True,
      all_future_queries_hidden_from_online_policy=True,
      training_supervision="OFFLINE_TRAIN_ONLY_STRUCTURAL_OVERLAP_NOT_FUTURE_ANSWER_GAIN",
      training_support=support,TRAIN_causal_credit_receipts=teacher_receipts,
      TRAIN_teacher_curve=teacher_train_curve,
      TRAIN_mixed_curve=mixed_train_curve,
      F102_original_raw_weights=[round(x,9) for x in old_weights],
      F104_teacher_weights=[round(x,9) for x in teacher_weights],
      F104_mixed_weights=[round(x,9) for x in mixed_weights],
      totals=total,positive_and_negative_signal_available=teacher_signal,
      onpolicy_data_collection_gain=onpolicy_value,
      delayed_answer_superiority_screen_passed=positive,
      disposition=("PUBLIC_DELAYED_GAIN_PRELIMINARY_NOT_ACCEPTED" if positive
           else "PUBLIC_DELAYED_CREDIT_NO_QUALIFIED_GAIN"),
      learning_source_transfer_not_independently_proven=True,
      protected_first_use=False,scientific_acceptance=False,
      accepted_ref_mutation=False,optimizer_promotion=False,
      CKB_connected=False,Codex_used=False,MindPalace_written=False)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-ref",required=True)
    args=parser.parse_args()
    print(json.dumps(evaluate(args.source_ref),sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
