"""WSP143: new 3-way and 5-way causal compositions from actual paid effects.

Source custodian is kept separate from both candidate and independent symbolic
fitters. No source generator or family identity reaches a learner. The source
scorer chooses future held questions only AFTER all model readouts are frozen.
This is public synthetic development, never original benchmark first-use.
"""
from hashlib import sha256
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
import sys,time,tracemalloc
import source as S
import direct_weights as D
import symbolic_control as C

ROOT=Path(__file__).resolve().parents[1]
def pin(alias,file,study="WSP-135"):
    spec=spec_from_file_location(alias,ROOT/study/file)
    m=module_from_spec(spec);sys.modules[alias]=m;spec.loader.exec_module(m)
    return m
N=pin("_wsp143_original_wsp135_weights","learner.py")
OLD=pin("_wsp143_original_wsp135_cart","controls.py")
THREE=pin("_wsp143_original_wsp142_threeterm","direct_weights.py","WSP-142")
SOURCE_FAMILIES=(
 ("known",tuple(sorted(S.KNOWN))),
 ("three",tuple(sorted(S.UNFAMILIAR))),
 ("five",tuple(sorted(S.SWITCH))),
 ("off",tuple(sorted(S.OFF))))
METHODS=("direct","independent_symbolic","original_three","wsp135","cart","no_update")
def empty():return {"correct":0,"wrong_confident":0,"abstained":0,"held":0}
def add(a,b):
    for key in a:a[key]+=b[key]
def score(answers,truth,questions):
    d=empty()
    for x in questions:
        value=answers[x]
        d["held"]+=1
        if value is None:d["abstained"]+=1
        elif type(value) is not int or value not in (0,1):
            raise AssertionError("WSP143_INVALID_CONFIDENT_PREDICTION")
        elif value==truth[x]:d["correct"]+=1
        else:d["wrong_confident"]+=1
    return d
def question_set(seed,unqueried):
    # Called only by evaluator after all learners have produced all64 readouts.
    return tuple(sorted(unqueried,key=lambda x:(
        sha256(("WSP143|FUTURE|"+str(seed)+"|"+str(x)).encode()).digest(),x))[:16])
def pct(d,k):
    return 100*d[k]/d["held"] if d["held"] else 0

def run():
    started_wall=time.perf_counter()
    started_cpu=time.process_time()
    tracemalloc.start()
    if len(D.FEATURES)!=63 or D.FEATURES[0]!=0 or D.FEATURES[-1]!=62:
        raise AssertionError("WSP143_SPARSE_FEATURE_CONTRACT_DRIFT")
    schedule=N.schedule()
    if len(schedule)!=32 or len(set(schedule))!=32:
        raise AssertionError("WSP143_ORIGINAL_ACTION_SCHEDULE_DRIFT")
    if len(N.templates())!=17640:
        raise AssertionError("WSP143_WSP135_REFERENCE_DRIFT")
    scores={f:{m:{"future":empty(),"all_unseen":empty()} for m in METHODS}
            for f,seeds in SOURCE_FAMILIES}
    per_world=[]
    saved={}
    source_receipts=[]
    future_answers=[]
    cold={}
    known_snapshot=None
    source_effects=0
    for family,seeds in SOURCE_FAMILIES:
        for seed in seeds:
            view=S.world(seed)
            cust=S.Custodian(view,seed)
            rows=[]
            for x in schedule:
                e=cust.query(view.subject(x))
                if e.input!=x or e.subject!=view.subject(x) or e.law_id!=view.law_id:
                    raise AssertionError("WSP143_SOURCE_RECEIPT_WRONG_LAW_OR_TYPED_INPUT")
                rows.append((e.input,e.effect))
            if len(rows)!=32 or len(cust.events)!=32 or len({x for x,y in rows})!=32:
                raise AssertionError("WSP143_INCOMPLETE_ACTUAL_SOURCE")
            source_effects+=32

            # All four FULLY fitted methods see the EXACT same charged source
            # consequence observations, with no true grammar/generator labels.
            direct=D.fit(tuple(rows))
            symbolic=C.solve(tuple(rows))
            if direct!=symbolic:
                raise AssertionError("WSP143_DIFFERENT_NUMERIC_AND_SYMBOLIC_OPTIMA")
            original_three=THREE.fit(tuple(rows))
            latent=N.fit(tuple(rows))
            tree=OLD.FullyFitCART()
            for row in cust.events:
                from types import SimpleNamespace
                e=SimpleNamespace(law_id=row[0],subject=row[1],input=row[2],
                                  effect=row[3],receipt="")
                tree.observe(view,e)
            tree.fit(view)
            if view.law_id not in tree.models or len(tree.examples[view.law_id])!=32:
                raise AssertionError("WSP143_CONVENTIONAL_CART_NOT_FITTED")
            # Greedy CART can legitimately leave XOR training errors. Keep them
            # as evidence of a comparator limitation; never fail the harness.
            outputs={m:{} for m in METHODS}
            for x in range(64):
                dn=D.predict(direct,x)
                sym=C.infer(symbolic,x)
                if dn!=sym:
                    raise AssertionError("WSP143_EQUAL_PRIOR_INDEPENDENT_SYMBOLIC_PARITY_FAIL")
                outputs["direct"][x]=dn
                outputs["independent_symbolic"][x]=sym
                outputs["original_three"][x]=THREE.predict(original_three,x)
                outputs["wsp135"][x]=N.predict(latent,x)
                outputs["cart"][x]=tree.infer(view,view.subject(x))
                outputs["no_update"][x]=None

            # For all models, freeze ALL64 predictions BEFORE scoring unseen
            # typed contexts. The source's original 32 paid actions are excluded.
            unseen=tuple(sorted(x for x in range(64) if x not in set(schedule)))
            if len(unseen)!=32:
                raise AssertionError("WSP143_UNSEEN_SOURCE_TASK_COUNT_WRONG")
            future=question_set(seed,unseen)
            if len(future)!=16 or not set(future)<=set(unseen):
                raise AssertionError("WSP143_PRIVATE_POSTFIT_FUTURE_TASK_ERROR")
            truth=cust.truth
            scored={}
            for model in METHODS:
                future_score=score(outputs[model],truth,future)
                all_score=score(outputs[model],truth,unseen)
                add(scores[family][model]["future"],future_score)
                add(scores[family][model]["all_unseen"],all_score)
                scored[model]={"future":future_score,"all_unseen":all_score}
            source_score=cust.score_once({
                subject:outputs["direct"][x] for subject,x in cust.held()})
            if source_score!=dict(scored["direct"]["all_unseen"],source_calls=32):
                raise AssertionError("WSP143_SOURCE_OWNED_SCORING_DISAGREEMENT")
            saved[view.law_id]={"seed":seed,"view":view,
                                "rows":tuple(rows),"direct":direct,"symbolic":symbolic,
                                "original_three":original_three,"outputs":outputs}
            source_receipts.append([seed,family,cust.receipt,[list(r) for r in rows]])
            future_answers.append([seed,family,list(future),
                [[m,[outputs[m][x] for x in future]] for m in METHODS]])
            per_world.append({"seed":seed,"family":family,
                              "source_calls":32,"candidate_optimum_count":len(direct[0]),
                              "witness_fenced_future":sum(D.witness_missing(x,tuple(z for z,y in rows)) for x in future),
                              "candidate_weights_sha256":D.fingerprint(direct),
                              "held_future_hash":S.digest(future),
                              "direct_future":scored["direct"]["future"],
                              "strongest_original_future_correct":max(
                                    scored["original_three"]["future"]["correct"],
                                    scored["wsp135"]["future"]["correct"],
                                    scored["cart"]["future"]["correct"]),
                              "scores":scored})
        if family=="known":
            known_snapshot={law:dict(record["outputs"]["direct"])
                 for law,record in saved.items()}
    # No global mutable state and no use of later outcomes can alter old law
    # predictions; recompute the actual retained weights independently.
    for law,original in known_snapshot.items():
        record=saved[law]
        ret=D.fit(record["rows"])
        if ret!=record["direct"] or any(
             D.predict(ret,x)!=original[x] for x in range(64)):
            raise AssertionError("WSP143_PREVIOUS_KNOWLEDGE_INTERFERENCE")
    cold_identity={"direct":0,"independent_symbolic":0,"original_three":0,"wsp135":0,"cart":0}
    transfer_scores={m:empty() for m in cold_identity}
    for seed in sorted(S.TRANSFER):
        view=S.world(seed)
        cust=S.Custodian(view,seed)
        if len(cust.events) or cust.budget!=0 or view.law_id not in saved:
            raise AssertionError("WSP143_ZERO_EFFECT_RESTORE_NOT_COLD")
        prev=saved[view.law_id]
        rebuilt_direct=D.fit(prev["rows"])
        rebuilt_symbolic=C.solve(prev["rows"])
        rebuilt_three=THREE.fit(prev["rows"])
        rebuilt_wsp=N.fit(prev["rows"])
        old_tree=OLD.FullyFitCART()
        for x,y in prev["rows"]:
            from types import SimpleNamespace
            old_tree.observe(view,SimpleNamespace(law_id=view.law_id,
               subject=view.subject(x),input=x,effect=y))
        old_tree.fit(view)
        regenerated={
          "direct":{x:D.predict(rebuilt_direct,x) for x in range(64)},
          "independent_symbolic":{x:C.infer(rebuilt_symbolic,x) for x in range(64)},
          "original_three":{x:THREE.predict(rebuilt_three,x) for x in range(64)},
          "wsp135":{x:N.predict(rebuilt_wsp,x) for x in range(64)},
          "cart":{x:old_tree.infer(view,view.subject(x)) for x in range(64)}}
        for model in cold_identity:
            before=prev["outputs"][model]
            cold_identity[model]+=sum(regenerated[model][x]==before[x] for x in range(64))
            add(transfer_scores[model],score(regenerated[model],cust.truth,range(64)))
        cust.score_once({s:regenerated["direct"][x] for s,x in cust.held()})
    if cold_identity!={m:256 for m in cold_identity}:
        raise AssertionError("WSP143_COLD_ZERO_EFFECT_RELABEL_DRIFT")
    if source_effects!=1536:
        raise AssertionError("WSP143_SOURCE_EFFECT_BUDGET_MISMATCH")
    stronger={f:max(("original_three","wsp135","cart"),key=lambda m:
              (scores[f][m]["future"]["correct"],m)) for f,seeds in SOURCE_FAMILIES}
    gains={}
    for f,seeds in SOURCE_FAMILIES:
        cand=scores[f]["direct"]["future"]
        ctrl=scores[f][stronger[f]]["future"]
        if cand["held"]!=16*len(seeds) or ctrl["held"]!=cand["held"]:
            raise AssertionError("WSP143_FROZEN_DENOMINATOR_CHANGED")
        gains[f]=100*(cand["correct"]-ctrl["correct"])/cand["held"]
    def err(f):return pct(scores[f]["direct"]["future"],"wrong_confident")
    def cover(f):
        d=scores[f]["direct"]["future"]
        return 100*(d["correct"]+d["wrong_confident"])/d["held"]
    passed=(gains["three"]>=10 and gains["five"]>=-5
            and err("three")<=1 and err("five")<=1
            and cover("three")>=85 and cover("five")>=85
            and gains["known"]>=-5 and err("off")<=1)
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {"schema":"wsp143.four-term-witness-public-development-result.v1",
      "status":"DEVELOPMENT_FOUR_TERM_WITNESS_SUPPORTED" if passed
          else "DEVELOPMENT_FOUR_TERM_WITNESS_NO_GO",
      "scientific_pass":False,"native_yggdrasil_qualified":False,
      "original_firstuse_source_effects":0,
      "generic_and_xor_primitives_presupplied":True,
      "no_predefined_complete_relationships":True,
      "rare_five_way_witness_guard":True,
      "original_wsp142_three_term_frozen_baseline":True,
      "source_calls":source_effects,"source_action_schedule_sha256":S.digest(schedule),
      "cohorts":{"known":8,"three":16,"five":16,"off":8,"zero_effect_cold":4},
      "max_induced_sparse_terms":4,"feature_dictionary_size":len(D.FEATURES),
      "source_blind_equal_information_symbolic_exact_tie":True,
      "stronger_original_baseline_by_family":stronger,
      "direct_gain_over_stronger_original_pp":gains,
      "candidate_confident_wrong_pct":{f:err(f) for f,seeds in SOURCE_FAMILIES},
      "candidate_coverage_pct":{f:cover(f) for f,seeds in SOURCE_FAMILIES},
      "scores":scores,"per_world":per_world,
      "cold_relabel_exact_identity":cold_identity,
      "cold_relabel_groundtruth_scores":transfer_scores,
      "previous_known_world_predictions_preserved":True,
      "source_effect_receipts_sha256":S.digest(source_receipts),
      "future_question_predictions_sha256":S.digest(future_answers),
      "resource":{"cpu_seconds":round(time.process_time()-started_cpu,3),
                  "wall_seconds":round(time.perf_counter()-started_wall,3),
                  "peak_tracemalloc_bytes":peak,"energy":"UNQUALIFIED"},
      "limitations":["Public synthetic six-bit source with prescribed AND/XOR primitives",
         "16 independent worlds per new family, not 256 independent trials",
         "Strong equal-information independent symbolic solver ties numerical",
         "High degree5 rare interventions may be information-insufficient under fixed32; witness gate is source blind and not proof of source grammar",
         "No original source first-use, native model, fully trained deep control, causal-world grounding or scientific pass"]}
if __name__=="__main__":print("WSP143_RESULT_JSON="+S.canon(run()))
