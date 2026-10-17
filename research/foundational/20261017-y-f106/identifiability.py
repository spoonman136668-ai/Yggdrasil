"""Y-F106: diagnose native delayed-credit feature non-identifiability.

No new policy or training: F105 teacher TRAIN labels are reproduced exactly,
then F106 public new diagnostic cohorts are *consumed for diagnosis* only.
Original F105 GUARD untouched. No original science/Codex/CKB/Mind Palace writes.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PREREG_GIT_BLOB="cdac6913e3999d89e1046f2d2fdb5e9c940ba547"
F105_GIT_BLOB="f78cae2150b48b4c7ffb1274f80392a563bd64ce"
F105_PREREG_GIT_BLOB="77cc10c614f37ca03604bb16f76a944455ef5f2c"
F104_GIT_BLOB="dd1f7bb2fd7288b5933f7a23085196c8a62e17b8"
F105_HEAD="84c2060d0b9634586f19e028867f6cb7fab423be"
NEW=((-19001,-101,"raw",48),(-19101,-102,"swap_roles_and_invert",56))
SCHEMA="yggdrasil.f106.native-credit-identifiability-public.v1"

class Invalid(ValueError):pass
def need(value,reason):
    if not value:raise Invalid("F106_"+reason)
def gitblob(path):
    data=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def load():
    need(gitblob(HERE/"prereg.json")==PREREG_GIT_BLOB and
         gitblob(ROOT/"20261017-y-f105"/"relational_credit.py")==F105_GIT_BLOB and
         gitblob(ROOT/"20261017-y-f105"/"prereg.json")==F105_PREREG_GIT_BLOB and
         gitblob(ROOT/"20261017-y-f104"/"causal_credit.py")==F104_GIT_BLOB,
         "PREREG_OR_FROZEN_PARENT_DRIFT")
    cfg=json.loads((HERE/"prereg.json").read_text())
    need(cfg["schema"]==
         "yggdrasil.f106.precode-relational-credit-identifiability-public.v1"
         and cfg["parent"]["exact_F105_head"]==F105_HEAD
         and cfg["source"]["new_F106_DIAGNOSTIC"][0]["seed_start"]==-19001
         and cfg["source"]["new_F106_DIAGNOSTIC"][1]["seed_start"]==-19101
         and all(cfg["authority"].values()),
         "PREREG_CASES_OR_AUTHORITY_DRIFT")
    spec=importlib.util.spec_from_file_location(
       "y_f106_pinned_f105",ROOT/"20261017-y-f105"/"relational_credit.py")
    f105=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=f105
    spec.loader.exec_module(f105)
    _,f104,parent,f102,native=f105.load()
    return cfg,f105,f104,parent,f102,native

def digest_json(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,
        separators=(",",":")).encode()).hexdigest()

def native_memory_hash(memory,pack):
    return hashlib.sha256(b"".join(pack.pack(*record) for record in memory)).hexdigest()

def collect(f105,f104,parent,f102,native,pack,groups):
    """Regenerate exact frozen F105 eight-event label teacher, offline only.

    Native memory is the F60 prefix. No future info becomes a learner input,
    and no learner is trained from these diagnostic outcomes.
    """
    rows=[]
    receipts=[]
    for family,group in enumerate(groups):
        for episode,(seed,stream,q,source_id) in enumerate(group):
            path,role_codes=f104.source_path(stream,q)
            spans=f104.subpaths(path,role_codes)
            memory=()
            for t,event in enumerate(stream):
                legal=native.actions(memory,event,t,pack)
                fixed=native._f60_step(memory,event,pack)
                if t in f105.CHECKPOINTS:
                    vectors=f105.features(parent,legal,fixed,event)
                    forward=stream[t+1:min(len(stream),t+9)]
                    scores=[f104.structural_retained_score(
                        native._finish_fixed(a[3],forward,pack),spans,native)
                        for a in legal]
                    original=next(i for i,a in enumerate(legal)
                                  if a[3]==fixed)
                    baseline=scores[original]
                    group_counts=Counter()
                    for index,(action,vector,score) in enumerate(
                         zip(legal,vectors,scores)):
                        outcome=(1 if score>baseline else
                                (-1 if score<baseline else 0))
                        group_counts[outcome]+=1
                        # Full source-state ID is *not* offered as a fitted
                        # policy input; it is a non-transferable identity key.
                        local_visible=dict(
                            memory=[list((u,v,list(c))) for u,v,c in memory],
                            arrived_event=list(event),
                            action_memory=[list((u,v,list(c))) for u,v,c in action[3]])
                        rows.append(dict(
                            record_id=f"{family}:{episode}:{t}:{index}",
                            source_identity_sha256=source_id,
                            cohort=family,episode=episode,checkpoint=t,
                            native_action_index=index,
                            current_memory_sha256=native_memory_hash(memory,pack),
                            candidate_memory_sha256=native_memory_hash(action[3],pack),
                            current_event_sha256=digest_json(event),
                            exact_visible_local_state_sha256=digest_json(local_visible),
                            source_native_12=list(vector[:12]),
                            online_graph_delta_8=list(vector[12:]),
                            label_OFFLINE_TRAIN_OR_DIAGNOSTIC_ONLY=outcome,
                            baseline_structural_potential=baseline,
                            candidate_structural_potential=score,
                            source_native_memory_bytes=len(action[3])*12,
                            future_events_in_offline_teacher=len(forward),
                            future_path_never_online=True))
                    receipts.append(dict(source_identity_sha256=source_id,
                       cohort=family,episode=episode,checkpoint=t,
                       native_legal_actions=len(legal),
                       sign_counts={"negative":group_counts[-1],
                                    "neutral":group_counts[0],
                                    "positive":group_counts[1]},
                       original_F60_native_memory_sha256=native_memory_hash(memory,pack)))
                memory=fixed
                native._valid_memory(memory,pack)
    need(all(len(row["source_native_12"])==12 and
             len(row["online_graph_delta_8"])==8 and
             row["source_native_memory_bytes"]<=144
             for row in rows),"MALFORMED_ONLINE_NATIVE_FEATURE")
    need(len(receipts)==len(groups)*8*6,"MISSING_FROZEN_CHECKPOINT")
    return rows,receipts

def equivalences(rows,key):
    """Empirical deterministic classification bound for one fixed feature map."""
    buckets=defaultdict(list)
    for row in rows:
        if key=="12":
            signature=tuple(row["source_native_12"])
        elif key=="20":
            signature=tuple(row["source_native_12"]+
                            row["online_graph_delta_8"])
        elif key=="exact":
            signature=row["exact_visible_local_state_sha256"]
        elif key=="prefix":
            signature=(row["source_identity_sha256"],row["checkpoint"],
                       row["current_memory_sha256"],
                       row["current_event_sha256"])
        else:
            raise Invalid("INVALID_EQUIVALENCE_TYPE")
        buckets[signature].append(row)
    group_summaries=[]
    correct=0
    for signature,members in sorted(
         buckets.items(),key=lambda x:repr(x[0])):
        labels=Counter(x["label_OFFLINE_TRAIN_OR_DIAGNOSTIC_ONLY"]
                       for x in members)
        peak=max(labels.values())
        correct+=peak
        if len(labels)>1:
            group_summaries.append(dict(
                feature_sha256=digest_json(signature),
                class_size=len(members),
                sign_histogram={str(v):labels[v] for v in (-1,0,1)},
                members=[dict(record_id=m["record_id"],label=m[
                    "label_OFFLINE_TRAIN_OR_DIAGNOSTIC_ONLY"],
                    source_sha256=m["source_identity_sha256"],
                    checkpoint=m["checkpoint"],
                    memory_sha256=m["current_memory_sha256"])
                    for m in members]))
    count=len(rows)
    need(correct<=count and
         sum(len(group["members"]) for group in group_summaries)<=count,
         "INCORRECT_EQUIVALENCE_BOUND")
    return dict(row_count=count,equivalence_classes=len(buckets),
           conflicting_classes=len(group_summaries),
           conflicting_members=sum(g["class_size"] for g in group_summaries),
           empirical_majority_correct=correct,
           empirical_unavoidable_label_disagreements=count-correct,
           empirical_majority_accuracy=round(correct/count,8) if count else None,
           conflicting_classes_detail=group_summaries)

def patterns(rows):
    return {kind:equivalences(rows,kind) for kind in ("12","20","exact","prefix")}

def witness_audit(f105,f104,parent,f102,native,pack,groups):
    """Read-only F101 removal-necessity on a bounded first stream of each set."""
    cfg,f101,f99,_=f102.source_modules()
    receipts=[]
    for g in groups:
        seed,stream,q,source_id=g[0]
        mem=()
        for event in stream: mem=native._f60_step(mem,event,pack)
        if len(q["ops"])<=6:
            signed=tuple(2*role+int(direction==-1)
                         for role,direction in q["ops"])
            out=f101.explain(mem,(q["start"],signed,q["answer"]),f99)
            need(out["retained_native_bytes"]<=144 and
                 out["result_scope"]==
                 "OFFLINE_NATIVE_MEMORY_STRUCTURE_NOT_BEHAVIORAL_CAUSAL_ACCURACY",
                 "F101_SOURCE_WITNESS_SCOPE")
            receipts.append(dict(graph_sha256=source_id,
                 requested_hops=len(signed),F60_memory_sha256=native_memory_hash(
                    mem,pack),witness=out))
        else:
            receipts.append(dict(graph_sha256=source_id,
                 requested_hops=len(q["ops"]),
                 skipped_reason="F101_FROZEN_MAX_SIX_HOPS_NO_FAKE_WITNESS"))
    return receipts

def evaluate(head):
    need(type(head) is str and len(head)==40 and
         all(c in "0123456789abcdef" for c in head),
         "EXACT_GIT_HEAD_REQUIRED")
    cfg,f105,f104,parent,f102,native=load()
    pack=native.codec()
    prior_train=f105.cohorts(f104,f102,native,f105.TRAIN)
    old_rows,old_receipts=collect(f105,f104,parent,f102,native,
                                  pack,prior_train)
    # Verify our independent reimplementation matches exact F105 TRAIN
    # teacher's original order and label/vector byte representations.
    old_original,_=f105.teacher_examples(
        f104,parent,f102,native,pack,prior_train)
    need(len(old_original)==len(old_rows) and
         all(tuple(row["source_native_12"]+
                       row["online_graph_delta_8"])==vec and
             row["label_OFFLINE_TRAIN_OR_DIAGNOSTIC_ONLY"]==label
             for row,(vec,label) in zip(old_rows,old_original)),
         "F105_FROZEN_TRAIN_REPLAY_DISAGREEMENT")
    original12,_=f105.fit(old_original,12)
    original20,_=f105.fit(old_original,20)
    # Old fitted original TRAIN weights were fully determined BEFORE these
    # new F106 diagnostic sources are created. No F105 GUARD is accessed.
    diagnostic=f105.cohorts(f104,f102,native,NEW)
    blocks=[]
    for i,group in enumerate(diagnostic):
        rows,receipts=collect(f105,f104,parent,f102,native,pack,(group,))
        # Compare frozen prior model and fixed baseline only. These 16 cases
        # can never be used to choose new weights afterwards.
        cases=[]
        for seed,stream,q,identity in group:
            fixed=()
            for event in stream:
                fixed=native._f60_step(fixed,event,pack)
            m12,_=f105.online(native,parent,pack,stream,original12)
            m20,_=f105.online(native,parent,pack,stream,original20)
            cases.append(dict(source_sha256=identity,
              seed_OFFLINE_ONLY=seed,
              F60_correct=int(pack.solve(fixed,q)==q["answer"]),
              original_F105_12_correct=int(pack.solve(m12,q)==q["answer"]),
              original_F105_20_correct=int(pack.solve(m20,q)==q["answer"]),
              retained_memory_bytes=[12*len(m) for m in (fixed,m12,m20)]))
        blocks.append(dict(name=cfg["source"]["new_F106_DIAGNOSTIC"][i]["name"],
              count=len(group),actions=len(rows),label_counts={
                    str(c):sum(row["label_OFFLINE_TRAIN_OR_DIAGNOSTIC_ONLY"]==c
                        for row in rows) for c in (-1,0,1)},
              equiv=patterns(rows),online_controls=cases,
              checkpoint_receipts=receipts,per_action_records=rows))
    old_patterns=patterns(old_rows)
    return dict(schema=SCHEMA,exact_head=head,
       frozen_F105_exact_parent=F105_HEAD,
       frozen_F105_git_blob=F105_GIT_BLOB,
       precode_freeze_git_blob=PREREG_GIT_BLOB,
       source="PUBLIC_SYNTHETIC_F105_TRAIN_REPLAY_PLUS_NEW_DIAGNOSTIC_NOT_ORIGINAL",
       frozen_F105_TRAIN_reproduced=True,
       old_F105_TRAIN_actions=len(old_rows),
       old_F105_TRAIN_label_counts={
          str(c):sum(r["label_OFFLINE_TRAIN_OR_DIAGNOSTIC_ONLY"]==c for r in old_rows)
          for c in (-1,0,1)},
       old_F105_TRAIN_equivalence=old_patterns,
       new_public_diagnostic_episodes=16,
       new_D106_blocks=blocks,
       source_only_native_F101_removal_witnesses=witness_audit(
           f105,f104,parent,f102,native,pack,diagnostic),
       F102_F103_F104_F105_GUARD_not_loaded=True,
       no_F106_retraining_or_model_selection=True,
       same_source_native_144byte_limit=True,
       learned_training_scorers_used_original_F105_TRAIN_only=True,
       frozen_screen_12_feature_aliasing=old_patterns["12"]["conflicting_classes"]>0,
       frozen_screen_20_feature_aliasing=old_patterns["20"]["conflicting_classes"]>0,
       fresh_cross_mode_20_aliasing_replicated=all(
          b["equiv"]["20"]["conflicting_classes"]>0 for b in blocks),
       improvement_over_F60_not_claimed=True,
       independent_science_accepted=False,protected_firstuse=False,
       accepted_ref_mutations=0,Codex_calls=0,CKB_connected=False,
       MindPalace_written=False,optimizer_promotion=False)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-ref",required=True)
    args=p.parse_args()
    print(json.dumps(evaluate(args.source_ref),sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
