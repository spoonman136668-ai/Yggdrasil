"""F61 source-free first-FIT validation audit: public role path and 144B receipts.

No imports from experiment source, no generator, no learned policy, and no
ability to dispatch another experiment. Reconstructs all stored 12-byte
lossless relation paths against actual 72 public observations; recomposes all
reported terminal answers and frozen per-family/nondegradation gates.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
ARMS=("learned_query_value_retention","F60_like_fixed_online",
      "frozen_F59_deferred","frozen_F58_frontier",
      "fixed_pair_triple_DAG","FIFO_hash",
      "offline_public_noncompetitive","future_query_oracle_unfair")
def need(pred,why):
    if not pred:raise AssertionError("F61_"+why)
def unpack(s):
    raw=bytes.fromhex(s)
    need(len(raw)==12,"PAYLOAD_LENGTH")
    a=int.from_bytes(raw[:4],"little")
    b=int.from_bytes(raw[4:8],"little")
    codes=int.from_bytes(raw[8:11],"little")
    n=raw[11]
    need(1<=n<=6 and codes>>(3*n)==0,"PACKED_ROLE_DECODER")
    return a,b,tuple((codes>>(3*i))&7 for i in range(n))
def inverse(rec):
    a,b,c=rec
    return b,a,tuple(v^1 for v in reversed(c))
def prove_public_path(rec,public):
    a,b,c=rec
    need(a!=b and all(0<=v<=7 for v in c),"INVALID_RECORD")
    current={a}
    for code in c:
        role=code//2
        reverse=bool(code&1)
        nxt=set()
        for at in current:
            for first,r,last in public:
                if r==role and (last if reverse else first)==at:
                    nxt.add(first if reverse else last)
        need(bool(nxt),"UNSUPPORTED_ROLE_PATH_PREFIX")
        current=nxt
    need(b in current,"UNSUPPORTED_PUBLIC_PATH")
def solve(memory,q):
    target=tuple(2*role+int(direction==-1) for role,direction in q["ops"])
    at=q["start"];seen=set()
    while target:
        choices=set()
        for rec in memory:
            for option in (rec,inverse(rec)):
                a,b,c=option
                if a==at and target[:len(c)]==c:
                    choices.add(option)
        if len(choices)!=1:return None
        a,b,c=next(iter(choices))
        at=b;target=target[len(c):]
        if (at,target) in seen:return None
        seen.add((at,target))
    return at
def audit(d,p):
    need(p["schema"]=="yggdrasil.f61.learned-future-task-value-retention.prereg.v1","PREREG_ID")
    need(p["stage"]=="PRECODE_FROZEN_NO_FIT_USE","FROZEN_ORIGINAL_PRECODE")
    need(d["schema"]=="yggdrasil.f61.learned-query-utility.fit-validation.v1","RESULT_SCHEMA")
    need(d["stage"]=="ONCE_ONLY_DISJOINT_WITHIN_FIT_VALIDATION_NO_DIAG_NO_ORIGINAL","STAGE")
    need(d["fit_training_seeds"]==p["fit"]["training"] and
         d["fit_validation_seeds"]==p["fit"]["validation"] and
         d["fit_families"]==p["fit"]["families"],"FIT_COHORT_DRIFT")
    need(d["diagnostic_seeds_NOT_AUTHORIZED"]==p["diagnostic_NOT_AUTHORIZED"]["seeds"]
         and d["original_seeds_NOT_RESERVED"]==p["original_NOT_RESERVED"]["seeds"],
         "FUTURE_COHORT_DRIFT")
    need(list(ARMS)==p["frozen_controls"],"FROZEN_ARM_DRIFT")
    need(d["model_parameter_bytes"]==12 and
         d["serialized_memory_max_bytes"]==144 and
         d["serialized_record_bytes"]==12 and
         len(d["learned_int8_parameters"])==12 and
         all(type(x)==int and -127<=x<=127 for x in d["learned_int8_parameters"]),
         "MODEL_OR_MEMORY_BUDGET")
    need(d["cases"]==len(d["rows"])==32,"CASE_COUNT")
    need(d["training_examples"]>1000 and d["training_positive_labels"]>0,
         "NO_GENUINE_LEARNING")
    for flag in ("independent_F3","primary_original_executed","accepted_ref_mutation",
                 "live_optimizer_promotion","physically_qualified_whole_native_576B",
                 "paid_API_or_Codex"):
        need(d[flag] is False,"FALSE_AUTHORITY_"+flag)
    need(d["query_hidden_until_retention_complete"] is True and
         d["public_full_graph_reference_noncompetitive"] is True,
         "QUESTION_LEAK_OR_UNFAIR_REFERENCE")
    counts={a:0 for a in ARMS}
    by={str(f):{a:0 for a in ARMS} for f in p["fit"]["families"]}
    ablated=0;seen=set()
    for row in d["rows"]:
        seed,fam=row["seed"],row["family"]
        need((seed,fam) not in seen and
             p["fit"]["validation"][0]<=seed<p["fit"]["validation"][1] and
             fam in p["fit"]["families"],"VALIDATION_ROW_IDENTITY")
        seen.add((seed,fam))
        public=[tuple(e) for e in row["public_events"]]
        need(len(public)==72 and len(set(public))==72 and
             all(len(e)==3 and 0<=e[1]<=3 for e in public),
             "SOURCE_PUBLIC_OBSERVATIONS")
        tags=row["public_tags"]
        need(len(tags)==72 and sum(tags)==36 and all(x in (0,1) for x in tags),
             "PRIVATE_TAG_BALANCE")
        q=row["question"]
        need(len(q["ops"]) in (4,6,8) and
             all(role in (0,1,2,3) and direction in (-1,1)
                 for role,direction in q["ops"]),"FUTURE_QUERY")
        need(set(row["retained_record_receipts"])==set(ARMS[:7]) and
             set(row["answers"])==set(ARMS) and
             row["answers"][ARMS[-1]]==1,
             "CONTROL_COMPLETENESS")
        for arm in ARMS[:7]:
            receipts=row["retained_record_receipts"][arm]
            need(len(receipts)<=12,"RECORD_CAP_"+arm)
            records=[unpack(x) for x in receipts]
            for rec in records:prove_public_path(rec,public)
            correct=int(solve(records,q)==q["answer"])
            need(row["answers"][arm]==correct,
                 "INDEPENDENT_QUERY_RECOUNT_"+arm)
            counts[arm]+=correct;by[str(fam)][arm]+=correct
            if arm==ARMS[0]:
                actual_ablation=int(solve(
                    [r for r in records if len(r[2])==1],q)==q["answer"])
                need(row["learned_retrieval_without_composed_records"]==actual_ablation,
                     "ABLATION_ROW_RECOUNT")
                need(row["learned_online_candidate_proposals"]>=0,"WORK_RECEIPT")
                ablated+=actual_ablation
        counts[ARMS[-1]]+=1;by[str(fam)][ARMS[-1]]+=1
    need(len(seen)==32 and all(
            sum(seed==s for seed,f in seen)==4 for s in range(741008,741016)),
         "FULL_DISTINCT_FIT_VALIDATION")
    need(by==d["by_family"] and counts==d["scores"],"SUMMARY_RECOUNT")
    fair=ARMS[1:6]
    strongest=max(fair,key=lambda a:counts[a])
    gain=(counts[ARMS[0]]-counts[strongest])/32
    no_reg=all(by[str(f)][ARMS[0]]>=max(by[str(f)][a] for a in fair)
               for f in p["fit"]["families"])
    ablation=(counts[ARMS[0]]-ablated)/32
    offline_ok=counts[ARMS[6]]/32>=p["source_feasibility"]["offline_public_witness_min_accuracy"]
    fixed_ok=counts[ARMS[1]]/32>=p["source_feasibility"]["causal_fixed_online_min_accuracy"]
    passed=(offline_ok and fixed_ok and
            gain>=p["learning_acceptance"]["gain_vs_strongest_144B_online_min"] and
            no_reg and ablation>0)
    need(d["strongest_equal_byte_online_control"]==strongest and
         math.isclose(d["learned_gain_over_strongest"],gain,abs_tol=1e-12) and
         math.isclose(d["composed_retrieval_ablation_gain"],ablation,abs_tol=1e-12) and
         d["family_nondegradation"]==no_reg and
         d["public_offline_source_feasible"]==offline_ok and
         d["fixed_online_source_feasible"]==fixed_ok and
         d["frozen_fit_learning_gate_met"]==passed,
         "FROZEN_DECISION_RECOUNT")
    need(d["verdict"]==("FIT_VALIDATION_LEARNED_QUERY_VALUE_SUPPORTED_NOT_F3"
                         if passed else "FIT_VALIDATION_LEARNED_QUERY_VALUE_NEGATIVE"),
         "VERDICT_MISCLASSIFICATION")
    return dict(schema="yggdrasil.f61.independent-fit-validation-audit.v1",
        validated_rows=len(seen),learned_correct=counts[ARMS[0]],
        strongest_fair=strongest,strongest_correct=counts[strongest],
        offline_public_correct=counts[ARMS[6]],
        improvement_pp=round(100*gain,6),
        ablation_gain_pp=round(100*ablation,6),
        family_nondegradation=no_reg,
        frozen_FIT_learning_gate_met=passed,
        source_independent_F3=False,primary_original_executed=False)
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("report");parser.add_argument("prereg")
    args=parser.parse_args()
    d=json.loads(Path(args.report).read_text());p=json.loads(Path(args.prereg).read_text())
    print(json.dumps(audit(d,p),sort_keys=True))
