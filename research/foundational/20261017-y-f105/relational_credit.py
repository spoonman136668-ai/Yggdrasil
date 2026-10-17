"""Y-F105: inspectable online graph-state features + delayed multi-action TRAIN credit.

PUBLIC synthetic negative-seed development, NOT scientific originals.
Precode prereg: 9a00bd7356c44fb37ced06fa5a04a1226bca9e32.
Parent F104 and F62 native action substrate are never changed.
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
FREEZE="77cc10c614f37ca03604bb16f76a944455ef5f2c"
F104_BLOB="dd1f7bb2fd7288b5933f7a23085196c8a62e17b8"
F104_PREREG="60757f68e275a9af7c4179fe54a26b3406be8de7"
PARENT_HEAD="25cf621aa36c34d9b40f024fb248acb3e1f8c9a2"
SCHEMA="yggdrasil.f105.online-relational-state-eightstep-credit-public.v1"
TRAIN=((-17001,-81,"raw",0),(-17101,-82,"raw",8))
GUARD=((-18001,-91,"raw",16),(-18101,-92,"swap_roles_and_invert",24),
       (-18201,-93,"reverse_order",32),(-18301,-94,"phase_and_roles",40))
CHECKPOINTS=(11,23,35,47,59,71)
PARAMS=20

class IntegrityError(ValueError):pass
def need(v,reason):
    if not v:raise IntegrityError("F105_"+reason)
def blob(p):
    data=Path(p).read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def load():
    need(blob(HERE/"prereg.json")==FREEZE and
         blob(ROOT/"20261017-y-f104"/"causal_credit.py")==F104_BLOB and
         blob(ROOT/"20261017-y-f104"/"prereg.json")==F104_PREREG,
         "PREREG_F104_SOURCE_CHANGED")
    cfg=json.loads((HERE/"prereg.json").read_text())
    need(cfg["schema"]=="yggdrasil.f105.frozen-online-relational-state-multistep-credit.v1"
         and cfg["source_parent"]["exact_F104_head"]==PARENT_HEAD and
         cfg["case_splits"]["TRAIN"][0]["first_seed"]==-17001 and
         cfg["case_splits"]["GUARD"][3]["first_seed"]==-18301 and
         all(cfg["authority"].values()),"PREREG_IDENTITY_CHANGED")
    spec=importlib.util.spec_from_file_location("yf105_f104_source",
                ROOT/"20261017-y-f104"/"causal_credit.py")
    f104=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=f104
    spec.loader.exec_module(f104)
    _cfg,parent,f102,native=f104.load()
    return cfg,f104,parent,f102,native

def cohorts(f104,f102,native,definitions):
    groups=f104.source_groups(f102,native,definitions)
    need(all(len(g)==8 for g in groups),"SOURCE_COUNT_CHANGED")
    return groups

def orient(mem):
    return tuple((i,u,v,tuple(code)) for i,(u,v,code) in enumerate(mem))+tuple(
       (i,v,u,tuple(c^1 for c in reversed(code)))
       for i,(u,v,code) in enumerate(mem))

def state_eight(mem,public_edge):
    """Online inspectable numerical structure, no eventual query, path or label.

    Native memory records are the ONLY persistent state. The 8 features
    summarize those exact records; they are ephemeral compute at action time.
    """
    need(len(mem)<=12,"MEMORY_OVER_BUDGET")
    vertices=set()
    pair_counts=Counter()
    for u,v,codes in mem:
        need(1<=len(codes)<=6 and all(0<=c<=7 for c in codes),
             "MALFORMED_NATIVE_RECORD")
        vertices.update((u,v))
        pair_counts[(u,v)]+=1
    arcs=orient(mem)
    out={}
    for idx,u,v,codes in arcs:
        out.setdefault(u,[]).append((idx,v,codes))
    joins2=0
    joins3=0
    for i,u,v,codes in arcs:
        for j,head,code2 in out.get(v,()):
            if i==j or len(codes)+len(code2)>6:
                continue
            joins2+=1
            for k,last,code3 in out.get(head,()):
                if k in (i,j) or len(codes)+len(code2)+len(code3)>6:
                    continue
                joins3+=1
    a,_,b=public_edge
    return (float(len(mem)),
            float(sum(len(x[2]) for x in mem)),
            float(sum(len(x[2])>1 for x in mem)),
            float(len(vertices)),
            float(joins2),
            float(joins3),
            float(sum(u in (a,b) for r in mem for u in (r[0],r[1]))),
            float(sum(count-1 for count in pair_counts.values())))

def features(parent,legal,baseline,event):
    old=[a[4] for a in legal if a[3]==baseline]
    need(len(old)==1,"NATIVE_F60_BASELINE_UNIQUE")
    basestate=state_eight(baseline,event)
    result=[]
    for a in legal:
        d12=tuple(float(x-y) for x,y in zip(a[4],old[0]))
        d8=tuple(x-y for x,y in zip(state_eight(a[3],event),basestate))
        need(len(d12)==12 and len(d8)==8,"FEATURE_COUNT")
        result.append(d12+d8)
    return tuple(result)

def teacher_span_potential(f104,mem,spans,native):
    return f104.structural_retained_score(mem,spans,native)

def teacher_examples(f104,parent,f102,native,pack,train):
    records=[]
    rows=[]
    for group,g in enumerate(train):
        for index,(seed,stream,q,source_id) in enumerate(g):
            nodes,codes=f104.source_path(stream,q)  # offline TRAIN only
            spans=f104.subpaths(nodes,codes)
            mem=()
            for t,event in enumerate(stream):
                legal=native.actions(mem,event,t,pack)
                fixed=native._f60_step(mem,event,pack)
                if t in CHECKPOINTS:
                    all_features=features(parent,legal,fixed,event)
                    # Every candidate gets the SAME next-8-event fixed F60
                    # continuation. The eventual answer path is TRAIN-only.
                    future=stream[t+1:min(72,t+9)]
                    reward=[]
                    for a in legal:
                        later=native._finish_fixed(a[3],future,pack)
                        reward.append(teacher_span_potential(f104,later,spans,native))
                    reference=next(i for i,a in enumerate(legal) if a[3]==fixed)
                    labels=tuple((1 if x>reward[reference] else
                                  (-1 if x<reward[reference] else 0))
                                 for x in reward)
                    rows.extend(zip(all_features,labels))
                    counts=Counter(labels)
                    records.append(dict(source_sha256=source_id,group=group,
                        episode=index,checkpoint=t,candidates=len(legal),
                        teacher_lookahead_events=len(future),
                        reference_potential=reward[reference],
                        pos=counts[1],neg=counts[-1],neutral=counts[0],
                        before_native_records=len(mem),future_label_only_offline=True))
                mem=fixed
                native._valid_memory(mem,pack)
    need(len(records)==16*6 and len(rows)>0,"TRAIN_EXAMPLES_MISSING")
    return tuple(rows),tuple(records)

def fit(rows,width):
    need(width in (12,20) and len(rows)>0,"FIT_DIM_OR_SOURCE")
    weights=[0.]*width
    trace=[]
    for epoch in range(4):
        loss=0.
        for x,truth in rows:
            relevant=x[:width]
            guess=math.tanh(sum(w*v for w,v in zip(weights,relevant)))
            loss+=(guess-truth)**2
            for j,v in enumerate(relevant):
                weights[j]=max(-7.9375,min(7.9375,
                    weights[j]+.04*(truth-guess)*v))
        norm=math.sqrt(sum(w*w for w in weights))
        need(math.isfinite(norm) and math.isfinite(loss),"NONFINITE_TRAIN")
        trace.append(dict(cycle=epoch+1,mse=round(loss/len(rows),7),
                          weight_norm=round(norm,7),nonfinite=0))
    return tuple(weights),tuple(trace)

def online(native,parent,pack,stream,weights,ablated=False,keep_trace=False):
    need(len(weights) in (12,20) and len(stream)==72,"ONLINE_SHAPE")
    mem=()
    checkpoints=[]
    for t,event in enumerate(stream):
        legal=native.actions(mem,event,t,pack)
        reference=native._f60_step(mem,event,pack)
        allfeatures=features(parent,legal,reference,event)
        def score(x):
            if len(weights)==12:
                return sum(w*v for w,v in zip(weights,x[:12]))
            if ablated:
                return sum(w*v for w,v in zip(weights[:12],x[:12]))
            return sum(w*v for w,v in zip(weights,x))
        choice=max(range(len(legal)),key=lambda j:(score(allfeatures[j]),-j))
        selected=legal[choice]
        if keep_trace and t in CHECKPOINTS:
            checkpoints.append(dict(t=t,chosen=choice,
                native_legal_actions=len(legal),native_records_before=len(mem),
                chosen_feature20=[round(x,7) for x in allfeatures[choice]],
                native_record_endpoints=[
                  [a,b,list(c)] for a,b,c in selected[3]],
                current_event=list(event),
                chosen_model_score=round(score(allfeatures[choice]),8),
                chosen_memory_sha256=hashlib.sha256(b"".join(
                    pack.pack(*record) for record in selected[3])).hexdigest()))
        mem=selected[3]
        native._valid_memory(mem,pack)
    return mem,tuple(checkpoints)

def distribution(rows):
    counts=Counter(y for x,y in rows)
    seen={}
    for x,y in rows:
        key=tuple(round(v,10) for v in x)
        seen.setdefault(key,set()).add(y)
    return dict(total=len(rows),positive=counts[1],negative=counts[-1],
                zero=counts[0],conflicting_same_features=sum(
                    len(values)>1 for values in seen.values()),
                distinct_feature_vectors=len(seen))

def original_f102_weights(f102,native,pack):
    # Replay exactly F102 original TRAIN; never construct F102 GUARD.
    train=[]
    for gi,family in enumerate((-31,-32)):
        for offset in range(8):
            seed=f102.TRAIN_START-offset
            stream,q,identity=f102.episode(native,seed,family,"raw",gi*8+offset)
            train.append((seed,family,stream,q,identity))
    labels=f102.train_examples(native,pack,train)
    weights,_=f102.train_linear(labels,"raw")
    return weights

def evaluate(head):
    need(type(head) is str and len(head)==40 and
         all(ch in "0123456789abcdef" for ch in head),"INVALID_EXACT_HEAD")
    cfg,f104,parent,f102,native=load()
    pack=native.codec()
    train=cohorts(f104,f102,native,TRAIN)
    training,training_records=teacher_examples(f104,parent,f102,native,pack,train)
    old_weights=original_f102_weights(f102,native,pack)
    smaller,small_curve=fit(training,12)
    richer,rich_curve=fit(training,20)
    signal=distribution(training)
    # All models and credits frozen BEFORE any GUARD case constructed.
    guard=cohorts(f104,f102,native,GUARD)
    groups=[]
    fullnames=("F60_fixed","F102_old_raw","F105_12_feature",
          "F105_20_relational","F105_20_ablated","F62_zero")
    for family,group in enumerate(guard):
        cases=[]
        for index,(seed,public,q,identity) in enumerate(group):
            fixed=()
            for event in public:
                fixed=native._f60_step(fixed,event,pack)
            memory12,trace12=online(native,parent,pack,public,smaller,
                                   keep_trace=index==0)
            memory20,trace20=online(native,parent,pack,public,richer,
                                   keep_trace=index==0)
            ablated,_=online(native,parent,pack,public,richer,ablated=True)
            old=f102.learned_online(native,public,pack,lambda d:sum(w*x for w,x in zip(old_weights,d)))[0]
            zero=f102.learned_online(native,public,pack,lambda d:0.)[0]
            arms=(fixed,old,memory12,memory20,ablated,zero)
            for mem in arms: native._valid_memory(mem,pack)
            result={name:int(pack.solve(mem,q)==q["answer"])
                    for name,mem in zip(fullnames,arms)}
            cases.append(dict(case_id=f"{family}:{index}",
                 source_sha256=identity,
                 source_seed_OFFLINE_ONLY=seed,
                 events=72,
                 requested_hops=len(q["ops"]),
                 question_hidden_during_online_inference=True,
                 max_native_persistent_bytes=144,
                 scores=result,
                 native_final_bytes_by_arm={name:len(mem)*12
                     for name,mem in zip(fullnames,arms)},
                 bounded_online_trace_12=trace12,
                 bounded_online_trace_20=trace20))
        groups.append(dict(name=cfg["case_splits"]["GUARD"][family]["label"],
            episodes=len(cases),cases=cases,
            correct={name:sum(c["scores"][name] for c in cases)
                     for name in fullnames}))
    totals={name:sum(b["correct"][name] for b in groups)
            for name in fullnames}
    compare=all(b["correct"]["F105_20_relational"]>=b["correct"]["F105_12_feature"]
                for b in groups) and (
      totals["F105_20_relational"]>=totals["F105_12_feature"]+4)
    causal_ablation=sum(
        c["scores"]["F105_20_relational"]!=c["scores"]["F105_20_ablated"]
        for b in groups for c in b["cases"])
    compare=compare and causal_ablation>0
    positive=(compare and totals["F105_20_relational"]>=totals["F60_fixed"]+4
              and all(b["correct"]["F105_20_relational"]>=b["correct"]["F60_fixed"]
                      for b in groups)
              and totals["F105_20_relational"]>totals["F102_old_raw"])
    return dict(schema=SCHEMA,head=head,parent_F104_head=PARENT_HEAD,
       prereg_git_blob=FREEZE,parent_F104_git_blob=F104_BLOB,
       source_kind="PUBLIC_SYNTHETIC_NEGATIVE_SEEDS_NOT_PROTECTED",
       F102_to_F104_consumed_GUARD_untouched=True,
       train_episodes=16,guard_episodes=32,native_memory_bytes=144,
       training_examples=signal,training_receipts=training_records,
       source_only_train_labels=True,
       teacher_lookahead_at_most_events=8,
       train_loss_12=small_curve,train_loss_20=rich_curve,
       learned_12_weights=[round(w,8) for w in smaller],
       learned_20_weights=[round(w,8) for w in richer],
       online_feature_names=[
         "native_delta_"+str(i) for i in range(12)]+
         ["delta_records","delta_role_hops","delta_multirole",
          "delta_vertices","delta_two_join","delta_three_join",
          "delta_arrived_endpoint_incidence","delta_redundant_pairs"],
       graph_feature_ablation_different_outcomes=causal_ablation,
       all_guards_tested_after_train=True,
       train_signal_with_both_signs=signal["positive"]>0 and signal["negative"]>0,
       representation_gain_screen_passed=compare,
       delayed_memory_superiority_screen_passed=positive,
       blocks=groups,totals=totals,
       disposition=("PUBLIC_DELTA_REPRESENTATION_GAIN_ONLY_NOT_SCIENCE" if positive
                    else "NO_QUALIFIED_RELATIONAL_STATE_GENERALIZATION_GAIN"),
       no_independent_task_topology_transfer=True,
       no_parameter_or_compute_matched_neural_baseline=True,
       protected_firstuse=False,independent_science_acceptance=False,
       optimizer_promotion=False,accepted_ref_changes=0,
       Codex_calls=0,CKB_dependency=False,MindPalace_written=False)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-ref",required=True)
    args=parser.parse_args()
    print(json.dumps(evaluate(args.source_ref),sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
