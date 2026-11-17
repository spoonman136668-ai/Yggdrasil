"""WSP134 source-safe trial: generic graph induction outside enumerated gate IDs.

Public synthetic only. No original science, no accepted model or native admission.
"""
from __future__ import annotations
from hashlib import sha256
import json
import time
import tracemalloc
import source as S
import learner as N
import controls as C

ARMS=("DIRECT_GROW","INDEPENDENT_SYMBOLIC","FULLY_FITTED_CART","FIXED32_DIRECT","NO_UPDATE")
FIELDS=("correct","wrong_confident","abstained","held","source_calls")
SEEDS=tuple(range(174000,174064))+tuple(range(175000,175032))

def blank():
    return {key:{name:{field:0 for field in FIELDS} for name in ARMS}
            for key in ("known","unfamiliar","transfer")}
def add(dst,item):
    for key in FIELDS:dst[key]+=item[key]

def run_development():
    start_wall=time.perf_counter()
    start_cpu=time.process_time()
    tracemalloc.start()
    if S.ALLOWED & S.PROTECTED:
        raise PermissionError("WSP134_PROTECTED_SOURCE_COHORT_OVERLAP")
    direct=N.DirectStructuralGrowth()
    exact=C.IndependentSymbolicTree()
    cart=C.FullyFitCART()
    fixed=N.DirectStructuralGrowth()
    none=C.NoUpdate()
    models={"DIRECT_GROW":direct,"INDEPENDENT_SYMBOLIC":exact,
            "FULLY_FITTED_CART":cart,"FIXED32_DIRECT":fixed,"NO_UPDATE":none}
    scores=blank()
    digests=[]
    views={}
    per_world=[]
    original_known_states={}
    old_outputs={}
    for seed in SEEDS:
        view=S.world(seed)
        views[view.law_id]=view
        condition="known" if seed in S.KNOWN else "unfamiliar"
        custodians={name:S.Custodian(view,seed) for name in ARMS}
        remaining=set(view.legal)
        remaining_exact=set(view.legal)
        fixed_seen=set()
        for step in range(32):
            active=direct.choose(view,remaining)
            reference=exact.choose(view,remaining_exact)
            if active!=reference or active not in remaining or reference not in remaining_exact:
                raise AssertionError("WSP134_STRONG_SYMBOLIC_QUERY_POLICY_NONPARITY")
            remaining.remove(active)
            remaining_exact.remove(reference)
            fixed_id=view.subject(step)
            if step in fixed_seen:raise AssertionError("WSP134_DUPLICATE_FIXED_PROBE")
            fixed_seen.add(step)
            for name,cu in custodians.items():
                action=fixed_id if name=="FIXED32_DIRECT" else active
                evidence=cu.query(action)
                if name=="DIRECT_GROW":direct.observe(view,evidence)
                elif name=="INDEPENDENT_SYMBOLIC":exact.observe(view,evidence)
                elif name=="FULLY_FITTED_CART":cart.observe(view,evidence)
                elif name=="FIXED32_DIRECT":fixed.observe(view,evidence)
        if len(remaining)!=32 or direct.choose(view,remaining) is not None:
            raise AssertionError("WSP134_PAID_BUDGET_INCORRECT")
        cart.fit(view)
        r={}
        outputs={}
        for name,model in models.items():
            cu=custodians[name]
            if len(cu.events)!=32 or len(cu.held())!=32:
                raise AssertionError("WSP134_INEQUAL_PAID_SOURCE_CALLS")
            pred={sub:model.infer(view,sub) for sub,x in cu.held()}
            outputs[name]=pred
            r[name]=cu.score_once(pred)
            add(scores[condition][name],r[name])
        if (outputs["DIRECT_GROW"]!=outputs["INDEPENDENT_SYMBOLIC"] or
            r["DIRECT_GROW"]!=r["INDEPENDENT_SYMBOLIC"]):
            raise AssertionError("WSP134_EXACT_INDEPENDENT_SYMBOLIC_NONPARITY")
        if len({custodians[name].receipt for name in
                ("DIRECT_GROW","INDEPENDENT_SYMBOLIC","FULLY_FITTED_CART","NO_UPDATE")})!=1:
            raise AssertionError("WSP134_SAME_ACTION_SOURCE_TRANSCRIPT_MISMATCH")
        if seed in S.KNOWN:
            original_known_states[view.law_id]=json.loads(direct.snapshot())["payload"]["states"][str(view.law_id)]
            old_outputs[view.law_id]=tuple(direct.infer(view,view.subject(x)) for x in range(64))
        digests.append([seed,condition,custodians["DIRECT_GROW"].receipt,
                        custodians["FIXED32_DIRECT"].receipt,
                        [r[name] for name in ARMS]])
        per_world.append([seed,r["DIRECT_GROW"]["correct"],
                          r["DIRECT_GROW"]["wrong_confident"],
                          r["DIRECT_GROW"]["abstained"]])
    after=json.loads(direct.snapshot())["payload"]["states"]
    old_unchanged=all(after[str(law)]==original_known_states[law] for law in original_known_states)
    if not old_unchanged:
        raise AssertionError("WSP134_OLDER_LEARNED_STRUCTURE_MUTATED")
    snapshot=direct.snapshot()
    cold=N.DirectStructuralGrowth.restore(snapshot,views)
    if cold.snapshot()!=snapshot:
        raise AssertionError("WSP134_COLD_RECONSTRUCTION_NONDETERMINISTIC")
    for law,view in views.items():
        for x in range(64):
            sub=view.subject(x)
            if cold.infer(view,sub)!=direct.infer(view,sub):
                raise AssertionError("WSP134_COLD_RETENTION_OUTPUT_CHANGED")
    transfer_exact_matches=0
    transfer_records=[]
    for seed in range(176000,176016):
        v=S.world(seed)
        orig=views[v.law_id]
        world={}
        for name,model in models.items():
            cu=S.Custodian(v,seed)
            if cu.budget or cu.events or v.legal:
                raise PermissionError("WSP134_TRANSFER_NOT_ZERO_SOURCE")
            pred={sub:model.infer(v,sub) for sub,x in cu.held()}
            world[name]=cu.score_once(pred)
            add(scores["transfer"][name],world[name])
        actual=tuple(direct.infer(v,v.subject(x)) for x in range(64))
        if actual!=old_outputs[v.law_id]:
            raise AssertionError("WSP134_ZERO_SOURCE_OPAQUE_ID_RELABEL_DRIFT")
        transfer_exact_matches+=len(actual)
        if world["DIRECT_GROW"]!=world["INDEPENDENT_SYMBOLIC"]:
            raise AssertionError("WSP134_TRANSFER_INDEPENDENT_SYMBOLIC_NONPARITY")
        transfer_records.append([seed,v.law_id,world])
    known=scores["known"]["DIRECT_GROW"]
    unknown=scores["unfamiliar"]["DIRECT_GROW"]
    status_supported=(known["correct"]*100>=65*2048 and
                      unknown["correct"]*100>=35*1024 and
                      unknown["wrong_confident"]*100<=15*1024 and
                      old_unchanged and transfer_exact_matches==1024)
    status=("DEVELOPMENT_OPEN_STRUCTURE_SUPPORTED_WITHIN_GENERIC_SPLIT_PRIOR"
            if status_supported else "DEVELOPMENT_OPEN_STRUCTURE_NO_GO")
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    node_count=sum(len(s.nodes) for s in direct.states.values())
    return {
      "schema":"wsp134.open-structure.source-safe.development-result.v1",
      "status":status,"scientific_pass":False,"native_admission":False,
      "original_first_use":False,"development_source_only":True,
      "unprovided_task_specific_gate_labels":True,
      "generic_split_leaf_primitive_supplied":True,
      "hypothesis_membership_pre_enumerated":False,
      "same_action_independent_symbolic_parity":True,
      "old_structures_unchanged":old_unchanged,
      "cold_restore_pass":True,
      "transfer_exact_prediction_match":transfer_exact_matches,
      "worlds":{"known":64,"unfamiliar":32,"transfer":16},
      "paid_actions_per_world_per_arm":32,
      "total_target_actions_per_arm":3072,
      "scores":scores,
      "strongest_control_note":"Independently implemented generic tree ties direct on same transcript; fully fitted greedy CART is a separate conventional control, not a fully trained deep model.",
      "unqualified":{"independent_science":True,"trained_deep_strong_baseline":True,
                     "whole_process_energy_parity":True,"real_world_causal_grounding":True},
      "score_sha256":S.digest(digests),
      "transfer_sha256":S.digest(transfer_records),
      "per_world_sha256":S.digest(per_world),
      "learned_graph_sha256":N.digest(snapshot),
      "resource":{"wall_seconds":round(time.perf_counter()-start_wall,3),
                  "cpu_seconds":round(time.process_time()-start_cpu,3),
                  "peak_tracemalloc_bytes":peak,
                  "direct_node_count":node_count,
                  "source_effects_per_arm":3072,
                  "energy":"UNQUALIFIED"}
    }

if __name__=="__main__":
    print("WSP134_SOURCE_SAFE_RESULT_JSON="+S.canon(run_development()))
