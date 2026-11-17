"""WSP139 prospective post-action query-blind, equal-budget source-safe test.

Runs unchanged WSP137 source-blind active chooser (all 64 actions eligible)
and unchanged WSP135 fitted numeric weights; source-only evaluator selects
jointly unqueried questions AFTER both policies have frozen predictions.
Nothing here is native Yggdrasil scientific first-use or a learned primitive.
"""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys, time, tracemalloc
import source as S

ROOT=Path(__file__).resolve().parents[1]
def pinned(name,sub,path):
    spec=spec_from_file_location(name,ROOT/sub/path)
    obj=module_from_spec(spec)
    sys.modules[name]=obj
    spec.loader.exec_module(obj)
    return obj

P=pinned("_wsp139_exact_parent_wsp137_policy","WSP-137","policy.py")
C=pinned("_wsp139_exact_parent_wsp137_symbolic","WSP-137","controls.py")
O=pinned("_wsp139_privileged_oracle_only","WSP-136","oracle.py")
POLICIES=("fixed","active")
FAMILIES=("known","unfamiliar","switch","off")
ARMS=("numeric","symbolic","cart","privileged_oracle","no_update")
ALL=frozenset(range(64))

def empty():return {"correct":0,"wrong_confident":0,"abstained":0,"held":0}
def add(a,b):
    for k in a:a[k]+=b[k]
def score_on(pred,truth,xs):
    z=empty()
    for x in xs:
        y=pred[x]
        z["held"]+=1
        if y is None:z["abstained"]+=1
        elif type(y) is not int or y not in (0,1):raise AssertionError("WSP139_NON_BINARY")
        elif y==truth[x]:z["correct"]+=1
        else:z["wrong_confident"]+=1
    return z
def word(truth):return sum(int(z)<<x for x,z in enumerate(truth))

class SourceBlindArm:
    def __init__(self,kind):
        self.kind=kind
        self.chooser=P.ActivePolicy() if kind=="active" else None
        self.fixed=P.fixed_schedule()
        self.rows=[]
        self.evidence=[]
        self.chosen=None
        self.symbolic=None
        self.outputs=None
        self.cart=None
        self.oracle=None
        self.receipt=None
    def choose(self):
        if len(self.rows)>=32:raise PermissionError("WSP139_OVER_BUDGET")
        if self.kind=="active":return self.chooser.choose(ALL)
        return self.fixed[len(self.rows)]
    def observe(self,e):
        if len(self.rows)>=32 or any(x==e.input for x,y in self.rows):
            raise PermissionError("WSP139_DUPLICATE_OR_EXCESS")
        if self.kind=="active":
            if self.chooser.pending!=e.input:raise ValueError("WSP139_ACTIVE_CHOICE_DRIFT")
            self.chooser.observe(e.input,e.effect)
        elif e.input!=self.fixed[len(self.rows)]:
            raise ValueError("WSP139_FIXED_CHOICE_DRIFT")
        self.rows.append((e.input,e.effect))
        self.evidence.append(e)
        self.receipt=e.receipt
    def freeze(self,v,oracle,do_oracle):
        if len(self.rows)!=32 or len(set(x for x,y in self.rows))!=32:
            raise AssertionError("WSP139_INCOMPLETE_SOURCE_BUDGET")
        self.chosen=P.N.fit(tuple(self.rows))
        self.symbolic=C.fit_symbolic(tuple(self.rows))
        cart=C.BASE.FullyFitCART()
        for e in self.evidence:cart.observe(v,e)
        cart.fit(v)
        version=oracle.begin() if do_oracle else None
        if version is not None:
            for x,y in self.rows:version.observe(x,y)
            if version.restore().snapshot()!=version.snapshot():raise AssertionError("WSP139_ORACLE_COLD_DRIFT")
        self.cart=cart
        self.oracle=version
        out={m:{} for m in ARMS}
        for x in range(64):
            n=P.N.predict(self.chosen,x)
            c=C.infer_symbolic(self.symbolic,x)
            if n!=c:raise AssertionError("WSP139_EQUAL_INFORMATION_SYMBOLIC_TIE_FAILED")
            out["numeric"][x]=n
            out["symbolic"][x]=c
            out["cart"][x]=cart.infer(v,v.subject(x))
            out["privileged_oracle"][x]=version.infer(x) if version is not None else None
            out["no_update"][x]=None
        self.outputs=out
        return out
    def cold_rebuild(self):
        if self.chosen!=P.N.fit(tuple(self.rows)):
            raise AssertionError("WSP139_DIRECT_WEIGHT_COLD_REBUILD_DRIFT")
        sym=C.fit_symbolic(tuple(self.rows))
        if sym!=self.symbolic:raise AssertionError("WSP139_SYMBOLIC_COLD_REBUILD_DRIFT")
        for x in range(64):
            if P.N.predict(self.chosen,x)!=C.infer_symbolic(sym,x):
                raise AssertionError("WSP139_COLD_OUTPUT_DRIFT")
        return True

def run():
    start=time.perf_counter()
    cpu=time.process_time()
    tracemalloc.start()
    if len(P.N.templates())!=17640 or len(C.BASE.codebooks())!=17640:
        raise AssertionError("WSP139_PINNED_GENERIC_LATENT_PRIOR_CHANGED")
    bank=O.candidate_bank()
    oracle=O.ExactOracle(bank)
    if len(bank)!=7062:raise AssertionError("WSP139_ORACLE_PRIOR_DRIFT")
    original_schedule=P.fixed_schedule()
    if len(original_schedule)!=32 or len(set(original_schedule))!=32:
        raise AssertionError("WSP139_BAD_PINNED_FIXED_SCHEDULE")
    scores={f:{p:{a:{"paired":empty(),"arm_unqueried":empty()}
                     for a in ARMS} for p in POLICIES} for f in FAMILIES}
    views={}
    old_known={}
    saved={}
    per_world=[]
    queried_per_policy={"active":0,"fixed":0}
    insufficient=[]
    source_members={"known":0,"unfamiliar":0,"switch":"NOT_IN_ORACLE_SCOPE","off":"NOT_IN_ORACLE_SCOPE"}
    source_receipts=[]
    paired_records=[]
    for family,seeds in (("known",sorted(S.KNOWN)),("unfamiliar",sorted(S.UNFAMILIAR)),
                         ("switch",sorted(S.SWITCH)),("off",sorted(S.OFF))):
        for seed in seeds:
            v=S.world(seed)
            views[v.law_id]=v
            source={p:S.Custodian(v,seed) for p in POLICIES}
            arms={p:SourceBlindArm(p) for p in POLICIES}
            # Critically, nothing (not even the future evaluator-only selection)
            # removes an x from the public legal action universe here.
            for p in POLICIES:
                cust=source[p]
                arm=arms[p]
                for i in range(32):
                    x=arm.choose()
                    if type(x) is not int or x not in ALL:raise AssertionError("BAD_SOURCE_BLIND_ACTION")
                    e=cust.query(v.subject(x))
                    arm.observe(e)
                arm.freeze(v,oracle,do_oracle=(family in ("known","unfamiliar")))
                if arm.cold_rebuild() is not True:raise AssertionError("COLD_REPLAY_FAILURE")
                queried_per_policy[p]+=len(cust.events)
            # ALL model outputs and action choices have been frozen now.
            queried={p:frozenset(x for x,y in arms[p].rows) for p in POLICIES}
            common=ALL-queried["fixed"]-queried["active"]
            future=tuple(sorted(common,key=lambda x:(sha256(
                ("WSP139|POSTACTION|"+str(seed)+"|"+str(x)).encode()).digest(),x))[:12])
            if len(common)<8:insufficient.append(seed)
            truth=source["fixed"].truth
            if truth!=source["active"].truth:raise AssertionError("WSP139_DIFFERENT_ORIGINAL_TRUTH")
            if family in ("known","unfamiliar"):
                if word(truth) not in bank:raise AssertionError("WSP139_SOURCE_NOT_IN_REFERENCE_GRAMMAR")
                source_members[family]+=1
            world_receipt=[seed,family,len(common),list(future)]
            scored={}
            for p in POLICIES:
                c=source[p]
                arm=arms[p]
                held=frozenset(x for s,x in c.held())
                if len(held)!=32 or not set(future)<=held:
                    raise AssertionError("WSP139_POSTACTION_EVALUATION_LEAK")
                scored[p]={}
                for m in ARMS:
                    a=score_on(arm.outputs[m],truth,future)
                    b=score_on(arm.outputs[m],truth,held)
                    add(scores[family][p][m]["paired"],a)
                    add(scores[family][p][m]["arm_unqueried"],b)
                    scored[p][m]={"paired":a,"arm_unqueried":b}
                expected=c.score_once({s:arm.outputs["numeric"][x] for s,x in c.held()})
                chk=dict(scored[p]["numeric"]["arm_unqueried"],source_calls=32)
                if expected!=chk:raise AssertionError("WSP139_SOURCE_OWNED_SCORE_DISAGREEMENT")
                source_receipts.append([seed,p,c.receipt,[[x,y] for x,y in arm.rows]])
            saved[v.law_id]={"seed":seed,"view":v,"arms":arms}
            per_world.append({"seed":seed,"family":family,"common_unseen_count":len(common),
                              "paired_count":len(future),"paired_choice_sha256":S.digest(future),
                              "scores":scored})
            paired_records.append([seed,family,world_receipt,
               [[p,[arms[p].outputs["numeric"][x] for x in future]] for p in POLICIES]])
        if family=="known":
            old_known={p:{(law,x):P.N.predict(s["arms"][p].chosen,x)
                           for law,s in saved.items() for x in range(64)} for p in POLICIES}
    for p in POLICIES:
        still={(law,x):P.N.predict(s["arms"][p].chosen,x)
                for law,s in saved.items() if s["seed"] in S.KNOWN for x in range(64)}
        if still!=old_known[p]:raise AssertionError("WSP139_PREVIOUS_KNOWLEDGE_DRIFT")
    identity={p:0 for p in POLICIES}
    transfer={p:empty() for p in POLICIES}
    for seed in sorted(S.TRANSFER):
        v=S.world(seed)
        cust=S.Custodian(v,seed)
        source_law=saved[v.law_id]
        for p in POLICIES:
            arm=source_law["arms"][p]
            probe=tuple(P.N.predict(P.N.fit(tuple(arm.rows)),x) for x in range(64))
            identity[p]+=sum(probe[x]==arm.outputs["numeric"][x] for x in range(64))
            add(transfer[p],score_on(probe,cust.truth,range(64)))
        cust.score_once({s:P.N.predict(source_law["arms"]["active"].chosen,x)
                         for s,x in cust.held()})
    if identity!={"active":256,"fixed":256}:raise AssertionError("WSP139_COLD_RELABEL_IDENTITY_FAILED")
    if queried_per_policy!={"active":896,"fixed":896}:raise AssertionError("WSP139_SOURCE_ACTION_OVERSPEND")
    def rate(group,p,k):
        d=scores[group][p]["numeric"]["paired"]
        return 100*d[k]/d["held"] if d["held"] else 0
    def gain(group):return rate(group,"active","correct")-rate(group,"fixed","correct")
    succeed=(not insufficient and gain("unfamiliar")>=5 and gain("switch")>=5
             and rate("unfamiliar","active","wrong_confident")<=1
             and rate("switch","active","wrong_confident")<=1
             and -gain("known")<=5 and rate("off","active","wrong_confident")<=10)
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
      "schema":"wsp139.postaction-queryblind-public-development-result.v1",
      "status":"DEVELOPMENT_POSTACTION_QUERYBLIND_SUPPORTED" if succeed else "DEVELOPMENT_POSTACTION_QUERYBLIND_NO_GO",
      "scientific_pass":False,"native_admission":False,"firstuse_original_effects":0,
      "source_safe":True,"original_input_pool_size":64,"no_preexcluded_test_x":True,
      "future_query_positions_chosen_after_both_policies":True,
      "paired_selection_conditioned_on_common_unseen":True,
      "model":"UNCHANGED_WSP137_ACTIVE_CHOICE_AND_WSP135_READOUT",
      "worlds":{"known":8,"unfamiliar":8,"switch":8,"off":4,"transfer":4},
      "source_calls_by_policy":queried_per_policy,
      "total_charged_synthetic_actions":sum(queried_per_policy.values()),
      "insufficient_common_unseen_world_seeds":insufficient,
      "paired_gain_pp":{f:gain(f) for f in FAMILIES},
      "source_oracle_membership":source_members,
      "scores":scores,"per_world":per_world,"transfer":transfer,
      "transfer_identity":identity,"old_known_state_unchanged":True,
      "independent_symbolic_parity":True,"cold_recomputed":True,
      "source_receipts_sha256":S.digest(source_receipts),
      "paired_future_readouts_sha256":S.digest(paired_records),
      "oracle_bank_sha256":oracle.bank_hash,
      "resource":{"cpu_seconds":round(time.process_time()-cpu,3),
                  "wall_seconds":round(time.perf_counter()-start,3),
                  "peak_tracemalloc_bytes":peak,"energy":"UNQUALIFIED"},
      "limitations":["Synthetic source only and only eight independent worlds per positive family",
                     "Paired questions are post-action but conditioned on both policy query sets",
                     "WSP137 structural prior and model readout unchanged; not novel primitive",
                     "Independent equal-information symbolic exact parity; no unique numerical advantage",
                     "Fully trained deep conventional baseline and matched process-energy unavailable",
                     "No native admission, authentic causal grounding, SCIENTIFIC_PASS or protected original first-use"]
    }
if __name__=="__main__":
    print("WSP139_RESULT_JSON="+S.canon(run()))
