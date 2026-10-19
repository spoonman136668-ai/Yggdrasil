"""T4 Yggdrasil real TRAIN-only delayed causal credit, paired open-source native test.

TRAIN source evaluator may label a future path ONLY for offline credit
training. The online learner receives public 72-event triples exclusively.
The distinct OPEN diagnostic source evaluator is never supplied to policy;
it is consulted after learning and retention for blinded answer scoring.
Original YNS protected cohorts remain inaccessible.
"""
from __future__ import annotations
import json,importlib.util,sys,time,tracemalloc
from pathlib import Path
HERE=Path(__file__).resolve().parent
T3=HERE/"20261018-yggdrasil-t3-fast-native.py"
FREEZE=HERE/"20261018-yggdrasil-t4-frozen-train-only.json"
def need(ok,tag):
    if not ok:raise ValueError("YGG_T4_"+tag)
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod
def measure(fn):
    tracemalloc.start();start=time.process_time_ns()
    result=fn()
    cost={"cpu_ns":time.process_time_ns()-start,
          "python_peak_bytes":tracemalloc.get_traced_memory()[1]}
    tracemalloc.stop()
    return result,cost
def source_teacher_path(events,evaluator):
    """TRAIN-only source oracle, never model input; fail on uncertain witness."""
    cur={evaluator["start"]:((),())}
    for role,direction in evaluator["ops"]:
        nxt={}
        for node,(edges,nodes) in sorted(cur.items()):
            for j,(a,r,b) in enumerate(events):
                if r!=role:continue
                neighbor=(b if a==node else None) if direction==1 else (a if b==node else None)
                if neighbor is None:continue
                if neighbor not in nxt:
                    nxt[neighbor]=(edges+(j,),nodes+(neighbor,))
        cur=nxt
        need(len(cur)<=512,"SOURCE_WITNESS_BOUNDED")
    end=evaluator["answer"]
    need(end in cur and len(cur[end][0])==8,
         "AUTHENTIC_TRAIN_ONLY_EIGHT_HOP_PATH")
    return frozenset(cur[end][0])
def training(t3,t2,f62,kernel,src,packing):
    events,evaluator=src.build_fixture(-920)
    credit=source_teacher_path(events,evaluator)
    recs=[]
    examples=[]
    for i,event in enumerate(events):
        record=packing.edge_record(event)
        features=kernel.public_features(recs,packing.pack(*record),i)
        examples.append((features,1 if i in credit else -1))
        recs=(recs+[record])[-10:]
    need(len(examples)==72 and sum(y==1 for _,y in examples)==8,
         "TRAIN_ONLY_LABELS_8_HOP")
    return kernel.fit_train_only(examples),{"TRAIN_teacher_positive":8,
        "TRAIN_teacher_negative":64,"true_future_seen_in_training_only":True}
def public_solver(records,question,packing):
    """Same bounded eight-op public answer rules, accepts full F60 12 records."""
    need(len(records)<=12 and len(question["ops"])==8,"EQUAL_PUBLIC_SOLVER")
    codes=tuple(2*r+int(d==-1) for r,d in question["ops"])
    oriented=set()
    for rec in records:
        oriented.add(rec);oriented.add(packing.mirrored(rec))
    states={0:{question["start"]}}
    scanned=0
    for step in range(8):
        for n in tuple(sorted(states.get(step,()))):
            for a,b,roles in sorted(oriented):
                scanned+=1
                need(scanned<=4096,"SOLVER_BUDGET_BOUND")
                if a==n and step+len(roles)<=8 and roles==codes[step:step+len(roles)]:
                    states.setdefault(step+len(roles),set()).add(b)
                    need(sum(map(len,states.values()))<=512,"SOLVER_STATE_BOUND")
    destinations=states.get(8,set())
    return next(iter(destinations)) if len(destinations)==1 else None
def main():
    frozen=json.loads(FREEZE.read_text())
    need(frozen["schema"]=="research.northstar.t4.train-only-learning-resource-parity.v1"
         and frozen["frozen_parent_head"]=="f9ee6c601b5d2b80b61ca1f867ba1c491eb2e9a2"
         and not frozen["original_protected_holdouts_allowed"],"SOURCE_FROZEN")
    t3=load(T3,"ygg_t4_fast")
    t2=t3.load(t3.T2,"ygg_t4_t2")
    f62,kernel,src=t2.modules()
    t2.materialize_ephemeral_canonical_native_sources(f62)
    packing=f62.codec()
    (learn_result,receipt),traincost=measure(lambda:training(t3,t2,f62,kernel,src,packing))
    weights,fit=learn_result
    need(type(weights) is bytes and len(weights)==20,"ACTUAL_20BYTE_WEIGHTS")
    public,evaluator=src.build_fixture(-921)
    question={"start":evaluator["start"],"ops":evaluator["ops"]}
    def candidate(w):
        memory,stats=t3.fast_online(public,w,packing,t2,f62)
        return public_solver(memory,question,packing),stats
    (prediction,policy),cost=measure(lambda:candidate(weights))
    (zero_prediction,zero_policy),zero_cost=measure(lambda:candidate(bytes(20)))
    f60=f62.controls()[0]
    def original():
        rec=f60.online_fixed(public)
        return public_solver(rec,question,packing),len(rec)
    (baseline,baseline_count),baseline_cost=measure(original)
    result={"schema":"ygg.t4.true-train-credit-open-native-parity.v1",
      "training_source_id":"negative_fixture_-920","open_source_id":"negative_fixture_-921",
      "registered_original_train_holdouts_used":0,"original_protected_first_use":False,
      "offline_teacher_examples":72,"train_credit_positives":receipt["TRAIN_teacher_positive"],
      "training_parameter_updates":fit["training_parameter_updates"],
      "trained_weights_nonzero":any(weights),
      "weights_bytes":20,"complete_native_persistent_bytes":144,
      "open_source_expected_answer":evaluator["answer"],
      "learned_answer":prediction,"zero_weight_answer":zero_prediction,
      "frozen_F60_answer":baseline,
      "learned_correct":prediction==evaluator["answer"],
      "zero_weight_correct":zero_prediction==evaluator["answer"],
      "frozen_F60_correct":baseline==evaluator["answer"],
      "candidate":policy,"zero_control":zero_policy,
      "baseline_records":baseline_count,
      "training_cpu_peak":traincost,"candidate_online_and_solver":cost,
      "zero_online_and_solver":zero_cost,
      "F60_online_and_eight_step_solver":baseline_cost,
      "amortized_candidate_cpu_32_open_tasks":
            cost["cpu_ns"]+traincost["cpu_ns"]/32,
      "candidate_complete_peak_lower_bound":
            max(traincost["python_peak_bytes"],cost["python_peak_bytes"]),
      "measured_cpu_nonincrease_after_train_amortization":
            cost["cpu_ns"]+traincost["cpu_ns"]/32<=baseline_cost["cpu_ns"],
      "measured_peak_nonincrease":
            max(traincost["python_peak_bytes"],cost["python_peak_bytes"])<=baseline_cost["python_peak_bytes"],
      "learning_strictly_changes_inference":prediction!=zero_prediction,
      "scientific_resource_parity_acceptance":False,
      "real_unseen_transfer_claim":False}
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
