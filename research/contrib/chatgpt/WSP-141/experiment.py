"""WSP141: real paid-source three-policy trial with independent future task questions.

The WSP137 chooser and WSP135 structural learner are used unchanged.
No future-test locations, true labels or source family reach a chooser.
This is public synthetic development, not native original-science first-use.
"""
from hashlib import sha256
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import json, random, sys, time, tracemalloc
import source as S

BASE=Path(__file__).resolve().parents[1]
def pinned(alias,dir_name,file):
    spec=spec_from_file_location(alias,BASE/dir_name/file)
    module=module_from_spec(spec)
    sys.modules[alias]=module
    spec.loader.exec_module(module)
    return module
P=pinned("_wsp141_pinned_wsp137_policy","WSP-137","policy.py")
C=pinned("_wsp141_pinned_wsp137_symbolic","WSP-137","controls.py")
O=pinned("_wsp141_privileged_reference_only","WSP-136","oracle.py")

POLICIES=("active","fixed","random")
MODELS=("numeric","symbolic","cart","privileged_oracle","memo_only","no_update")
GROUPS=("known","unfamiliar","switch","off")
ALL=frozenset(range(64))
def blank():return {"correct":0,"wrong_confident":0,"abstained":0,"held":0}
def add(a,b):
    for k in a:a[k]+=b[k]
def score(pred,truth,xs):
    out=blank()
    for x in xs:
        y=pred[x]
        out["held"]+=1
        if y is None:out["abstained"]+=1
        elif type(y) is not int or y not in (0,1):raise AssertionError("WSP141_NONBINARY_READOUT")
        elif y==truth[x]:out["correct"]+=1
        else:out["wrong_confident"]+=1
    return out
def random_schedule(law_id):
    if type(law_id) is not int:raise ValueError("WSP141_BAD_PUBLIC_ID")
    key=sha256(("WSP141|RANDOM32|"+str(law_id)).encode()).digest()
    return tuple(random.Random(int.from_bytes(key,"big")).sample(range(64),32))
def future_questions(seed):
    # Only the scorer calls this AFTER all policies have frozen predictions.
    return tuple(sorted(range(64),key=lambda x:(sha256(
       ("WSP141|FUTURE|"+str(seed)+"|"+str(x)).encode()).digest(),x))[:16])

class Arm:
    def __init__(self,policy,view):
        self.policy=policy
        self.rows=[]
        self.actual=[]
        self.chooser=P.ActivePolicy() if policy=="active" else None
        self.schedule=(tuple(P.fixed_schedule()) if policy=="fixed"
                       else random_schedule(view.law_id) if policy=="random" else None)
        self.law_id=view.law_id
        self.out=None
        self.chosen=None
        self.symbolic=None
        self.receipt=None
    def choose(self):
        if len(self.rows)>=32:raise PermissionError("WSP141_OVER_BUDGET")
        x=(self.chooser.choose(ALL) if self.policy=="active"
           else self.schedule[len(self.rows)])
        if type(x) is not int or x not in ALL or any(v==x for v,y in self.rows):
            raise AssertionError("WSP141_DUPLICATE_OR_OUT_OF_DOMAIN")
        return x
    def observe(self,x,e):
        if (e.input!=x or e.law_id!=self.law_id
           or len(self.rows)>=32 or any(q==x for q,z in self.rows)):
            raise ValueError("WSP141_WRONG_REAL_EFFECT")
        if self.policy=="active":
            if self.chooser.pending!=x:raise ValueError("WSP141_ACTION_ARRIVAL_MISMATCH")
            self.chooser.observe(x,e.effect)
        elif x!=self.schedule[len(self.rows)]:
            raise ValueError("WSP141_NOT_ORIGINAL_POLICY_ORDER")
        self.rows.append((x,e.effect))
        self.actual.append(e)
        self.receipt=e.receipt
    def freeze(self,view,oracle,allow_oracle):
        if len(self.rows)!=32 or len({x for x,y in self.rows})!=32:
            raise AssertionError("WSP141_INCOMPLETE_ACTUAL_ACTIONS")
        self.chosen=P.N.fit(tuple(self.rows))
        self.symbolic=C.fit_symbolic(tuple(self.rows))
        memory=dict(self.rows)
        conventional=C.BASE.FullyFitCART()
        for e in self.actual:conventional.observe(view,e)
        conventional.fit(view)
        reference=oracle.begin() if allow_oracle else None
        if reference is not None:
            for x,y in self.rows:reference.observe(x,y)
            if reference.restore().snapshot()!=reference.snapshot():
                raise AssertionError("WSP141_REFERENCE_COLD_STATE_DRIFT")
        self.out={m:{} for m in MODELS}
        for x in range(64):
            has_fact=x in memory
            numeric=memory[x] if has_fact else P.N.predict(self.chosen,x)
            symbolic=memory[x] if has_fact else C.infer_symbolic(self.symbolic,x)
            if numeric!=symbolic:raise AssertionError("WSP141_NUMERIC_SYMBOLIC_SAME_INPUT_MISMATCH")
            cart=memory[x] if has_fact else conventional.infer(view,view.subject(x))
            oracle_y=(memory[x] if has_fact else reference.infer(x)) if reference is not None else (memory[x] if has_fact else None)
            self.out["numeric"][x]=numeric
            self.out["symbolic"][x]=symbolic
            self.out["cart"][x]=cart
            self.out["privileged_oracle"][x]=oracle_y
            self.out["memo_only"][x]=memory[x] if has_fact else None
            self.out["no_update"][x]=None
        if P.N.fit(tuple(self.rows))!=self.chosen:
            raise AssertionError("WSP141_DIRECT_WEIGHT_COLD_FIT_DRIFT")
        cold_symbolic=C.fit_symbolic(tuple(self.rows))
        if cold_symbolic!=self.symbolic:raise AssertionError("WSP141_SYMBOLIC_COLD_DRIFT")
        for x in range(64):
            expected=memory[x] if x in memory else P.N.predict(self.chosen,x)
            if expected!=self.out["numeric"][x]:
                raise AssertionError("WSP141_NUMERIC_COLD_OUTPUT_DRIFT")
        return self.out

def run():
    start=time.perf_counter()
    cpu=time.process_time()
    tracemalloc.start()
    if len(P.N.templates())!=17640 or len(C.BASE.codebooks())!=17640:
        raise AssertionError("WSP141_ORIGINAL_LATENT_GRAMMAR_DRIFT")
    base_schedule=P.fixed_schedule()
    if len(base_schedule)!=32 or len(set(base_schedule))!=32:
        raise AssertionError("WSP141_INVALID_FIXED_CONTROL")
    oracle=O.ExactOracle(O.candidate_bank())
    if len(oracle.bank)!=7062:raise AssertionError("WSP141_REFERENCE_UNIVERSE_CHANGED")
    scores={g:{p:{m:{seg:blank() for seg in ("future","seen","unseen","all64","joint_unseen")}
                  for m in MODELS} for p in POLICIES} for g in GROUPS}
    per_world=[]
    source_receipts=[]
    future_observations=[]
    arms_by_law={}
    known_frozen={}
    source_calls={p:0 for p in POLICIES}
    oracle_law_membership={"known":0,"unfamiliar":0,"switch":"NOT_REFERENCE_GRAMMAR","off":"NOT_REFERENCE_GRAMMAR"}
    for family,seeds in (("known",sorted(S.KNOWN)),("unfamiliar",sorted(S.UNFAMILIAR)),
                         ("switch",sorted(S.SWITCH)),("off",sorted(S.OFF))):
        for seed in seeds:
            v=S.world(seed)
            world_arms={p:Arm(p,v) for p in POLICIES}
            custodians={p:S.Custodian(v,seed) for p in POLICIES}
            # Every action must be chosen solely from 64 typed publicly available x
            # and earlier actual paid effects. Future 16 task questions NOT chosen here.
            for pol in POLICIES:
                a=world_arms[pol]
                cust=custodians[pol]
                for step in range(32):
                    x=a.choose()
                    e=cust.query(v.subject(x))
                    a.observe(x,e)
                a.freeze(v,oracle,allow_oracle=family in ("known","unfamiliar"))
                source_calls[pol]+=len(cust.events)
                if len(cust.events)!=32 or len(cust.held())!=32:
                    raise AssertionError("WSP141_UNPAID_OR_OVERPAID_ACTIONS")
            # ONLY now may source evaluator draw future task questions.
            future=future_questions(seed)
            if len(future)!=16 or len(set(future))!=16:
                raise AssertionError("WSP141_BAD_UNCONDITIONAL_FUTURE_DISTRIBUTION")
            truth=custodians["fixed"].truth
            if any(c.truth!=truth for c in custodians.values()):
                raise AssertionError("WSP141_SOURCE_LAW_MISMATCH")
            if family in ("known","unfamiliar"):
                truthword=sum(z<<x for x,z in enumerate(truth))
                if truthword not in oracle.bank:
                    raise AssertionError("WSP141_SOURCE_LAW_OUTSIDE_INFORMATIONAL_REFERENCE")
                oracle_law_membership[family]+=1
            unseen_joint=ALL-set().union(*(set(x for x,y in a.rows) for a in world_arms.values()))
            world_result={}
            for pol in POLICIES:
                a=world_arms[pol]
                seen=frozenset(x for x,y in a.rows)
                unseen_task=tuple(x for x in future if x not in seen)
                seen_task=tuple(x for x in future if x in seen)
                if len(seen_task)+len(unseen_task)!=16:raise AssertionError("WSP141_FUTURE_PARTITION_ERROR")
                world_result[pol]={"seen_future":len(seen_task),"unseen_future":len(unseen_task),
                                   "scores":{}}
                for model in MODELS:
                    d={}
                    for label,subset in (("future",future),("seen",seen_task),("unseen",unseen_task),
                                         ("all64",tuple(range(64))),("joint_unseen",tuple(sorted(unseen_joint)))):
                        result=score(a.out[model],truth,subset)
                        add(scores[family][pol][model][label],result)
                        if label in ("future","seen","unseen","joint_unseen"):d[label]=result
                    world_result[pol]["scores"][model]=d
                # Score single predeclared full32 non-observed effect set ONCE with source-owned scorer.
                expected=custodians[pol].score_once({s:a.out["numeric"][x]
                                                      for s,x in custodians[pol].held()})
                manual=score(a.out["numeric"],truth,tuple(x for s,x in custodians[pol].held()))
                if expected!=dict(manual,source_calls=32):
                    raise AssertionError("WSP141_CUSTODIAN_SCORE_DISAGREEMENT")
                source_receipts.append([seed,family,pol,a.receipt,list(a.rows)])
            future_observations.append([seed,family,list(future),
                [[p,[world_arms[p].out["numeric"][x] for x in future]] for p in POLICIES]])
            per_world.append({"seed":seed,"family":family,"future_sha256":S.digest(future),
                              "joint_unseen_count":len(unseen_joint),"arms":world_result})
            arms_by_law[v.law_id]={"seed":seed,"view":v,"arms":world_arms}
        if family=="known":
            known_frozen={p:{(law,x):a["arms"][p].out["numeric"][x]
                          for law,a in arms_by_law.items() for x in range(64)}
                          for p in POLICIES}
    for pol in POLICIES:
        now={(law,x):z["arms"][pol].out["numeric"][x]
             for law,z in arms_by_law.items() if z["seed"] in S.KNOWN for x in range(64)}
        if now!=known_frozen[pol]:
            raise AssertionError("WSP141_KNOWN_RELATIONSHIP_INTERFERENCE")
    transfer={p:blank() for p in POLICIES}
    transfer_identity={p:0 for p in POLICIES}
    for seed in sorted(S.TRANSFER):
        view=S.world(seed)
        c=S.Custodian(view,seed)
        if view.law_id not in arms_by_law:raise AssertionError("WSP141_TRANSFER_WRONG_LAW_ID")
        for pol in POLICIES:
            prior=arms_by_law[view.law_id]["arms"][pol]
            rebuilt=P.N.fit(tuple(prior.rows))
            stored=dict(prior.rows)
            output={x:(stored[x] if x in stored else P.N.predict(rebuilt,x)) for x in range(64)}
            transfer_identity[pol]+=sum(output[x]==prior.out["numeric"][x] for x in range(64))
            add(transfer[pol],score(output,c.truth,tuple(range(64))))
        c.score_once({s:arms_by_law[view.law_id]["arms"]["active"].out["numeric"][x]
                       for s,x in c.held()})
    if transfer_identity!={"active":256,"fixed":256,"random":256}:
        raise AssertionError("WSP141_COLD_RELABEL_EXACT_PREDICTIONS_FAIL")
    if source_calls!={"active":896,"fixed":896,"random":896}:
        raise AssertionError("WSP141_SOURCE_EFFECT_COUNTS_UNEQUAL")
    def pct(fam,pol,model,key="correct",seg="future"):
        v=scores[fam][pol][model][seg]
        return 100*v[key]/v["held"] if v["held"] else 0.0
    strong={f:max((p for p in ("fixed","random")),
                  key=lambda p:(pct(f,p,"numeric"),p)) for f in GROUPS}
    gain={f:pct(f,"active","numeric")-pct(f,strong[f],"numeric") for f in GROUPS}
    def unseen_wrong(f):
        return pct(f,"active","numeric","wrong_confident","unseen")
    passed=(gain["unfamiliar"]>=5 and gain["switch"]>=5
            and gain["known"]>=-5
            and unseen_wrong("unfamiliar")<=1
            and unseen_wrong("switch")<=1
            and unseen_wrong("off")<=10)
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
      "schema":"wsp141.unconditional-future-three-policy-public-result.v1",
      "status":"DEVELOPMENT_RANDOM_CONTROL_FUTURE_UTILITY_SUPPORTED" if passed
               else "DEVELOPMENT_RANDOM_CONTROL_FUTURE_UTILITY_NO_GO",
      "scientific_pass":False,"native_admission":False,"original_source_first_use":False,
      "worlds":{"known":8,"unfamiliar":8,"switch":8,"off":4,"transfer":4},
      "policy_options_public":64,"future_tasks_world":16,
      "future_distribution_independent_of_actions":True,
      "future_seen_and_unseen_reported_separately":True,
      "model":"EXACT_WSP137_ACTIVE_POLICY_AND_WSP135_NUMERIC_FIT_READOUT",
      "random32_independent_of_source_and_future":True,
      "source_calls":source_calls,"total_charged_public_effects":sum(source_calls.values()),
      "strongest_reference_by_family":strong,
      "active_gain_over_strongest_control_pp":gain,
      "unseen_active_wrong_confident_pct":{f:unseen_wrong(f) for f in GROUPS},
      "source_oracle_membership":oracle_law_membership,
      "scores":scores,"per_world":per_world,
      "transfer":transfer,"transfer_identity":transfer_identity,
      "known_readouts_unchanged":True,"cold_recompute":True,"symbolic_equal_information_tie":True,
      "source_receipts_sha256":S.digest(source_receipts),
      "future_questions_answers_sha256":S.digest(future_observations),
      "oracle_bank_sha256":oracle.bank_hash,
      "resource":{"cpu_seconds":round(time.process_time()-cpu,3),
                  "wall_seconds":round(time.perf_counter()-start,3),
                  "tracemalloc_peak_bytes":peak,"energy":"UNQUALIFIED"},
      "limitations":["Only eight independent public synthetic worlds per positive family",
         "Unconditional future task utility includes observed source facts; separate seen/unseen reported",
         "No unseen input dimension or unsupplied primitive discovery; supplied 17640 latent templates",
         "Independently coded same-information symbolic ties numerical, not native numerical advantage",
         "No fully trained deep comparator or authentic external causal source first-use",
         "Original Yggdrasil native model/accepted main unaffected, no SCIENTIFIC_PASS"]
    }
if __name__=="__main__":print("WSP141_RESULT_JSON="+S.canon(run()))
