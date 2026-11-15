#!/usr/bin/env python3
"""F43 source-known graph-routed native public-consequence learning DEV.

Native PublicCausalCells is a fixed-budget published control, not a full Yggdrasil
intelligence substrate. All CC0 IDs and edges are from previously used source.
Public actions/observed consequences here are deterministic synthetic DEV data.
"""
from hashlib import sha1, sha256
import json
from pathlib import Path
import struct
from yggdrasil.public_causal_cells import PublicCausalCells

from f26_semantic_association import NotAdmitted
from f40_component_isolation_audit import build_components, audit
from f42_exact_index_dev import ExactIndex, source_facts

HERE=Path(__file__).resolve().parent
PREREG=HERE/"f43_prereg.json"
PREREG_BLOB="f05f65d461d1c8981cc7b40b0c3ae3d9716794e0"
SCHEMA="yggdrasil.qtr01.f43.known-graph-native-public-consequence-routing-dev.v1"
RESULT_SCHEMA="yggdrasil.qtr01.f43.native-known-component-public-action-dev-result.v1"
TRAIN_ROOTS=("Q2","Q5","Q17","Q42","Q64","Q76","Q90")
RESERVED=frozenset(("Q142","Q183","Q312","Q1490"))
FROZEN_PREF=(0,1,0,1,0,1,0)
FROZEN_F42_SHA="81882893e2760070bd2fd04fea3644d3e501e7f6b04598d122877e873f03fc53"


def preregistration(path=PREREG):
    raw=Path(path).read_bytes()
    gitsha=sha1(b"blob "+str(len(raw)).encode("ascii")+b"\x00"+raw).hexdigest()
    if gitsha!=PREREG_BLOB:
        raise NotAdmitted("F43_PREREG_GIT_BLOB_DRIFT")
    d=json.loads(raw)
    pins=d.get("source_pins",{})
    freeze=d.get("frozen_metrics",{})
    restrictions=d.get("fences",{})
    identity=d.get("input_graph",{})
    native=d.get("native",{})
    if (d.get("schema")!=SCHEMA
        or d.get("status")!="FROZEN_BEFORE_F43_IMPLEMENTATION_OR_MEASUREMENTS"
        or d.get("source_exact_parent")!="9ee47d2fa569e0f1cec772fce50ef75fb44cee2e"
        or pins.get("f42_snapshot_sha256")!=FROZEN_F42_SHA
        or pins.get("f42_exact_index_blob")!="997d2d13c4725d5b33d993d252aac7108304b529"
        or pins.get("public_causal_cells_blob")!="5c9a9904e31688bebc2e53723569e1fb988a981f"
        or pins.get("f40_archived_component_audit_blob")!="ae6ab67997d230de58e22645a61e976b4b4a21b5"
        or [identity.get(k) for k in ("frozen_triples","entities","predicates","connected_components","known_graph_entity_holdouts")]!=[82,78,8,7,71]
        or identity.get("component_training_nodes")!=list(TRAIN_ROOTS)
        or native.get("training_public_outcome_law_by_component_slot")!=list(FROZEN_PREF)
        or native.get("active_slots")!=7 or native.get("retained_slots")!=9
        or native.get("learned_counter_bytes")!=128 or native.get("sha256_checkpoint_bytes")!=164
        or any(freeze.get(k)!=v for k,v in {
           "source_graph_components":7,
           "source_graph_known_identity_holdouts":71,
           "public_training_active_events":56,
           "public_interference_retained_events":72,
           "native_known_graph_heldout_coverage_min":71,
           "native_known_graph_heldout_accuracy_min":71,
           "matched_conventional_heldout_coverage_min":71,
           "matched_conventional_heldout_accuracy_min":71,
           "native_advantage_over_equal_information_conventional_min":1,
           "strict_scientific_gain_expected":False,
           "cold_native_checkpoint_parity":True,
           "retained_interference_no_active_change":True,
           "mismapped_control_all_heldout_correct":False,
           "no_unknown_source_or_reserved_qid_first_use":True
           }.items())
        or not restrictions or any(flag is not True for flag in restrictions.values())):
        raise NotAdmitted("F43_FROZEN_CONTRACT_DRIFT")
    return d


def _qid_sort(qid):
    return int(qid[1:])


def graph_contexts():
    """Route from a cold F42 exact graph, not learned from future query rewards."""
    preregistration()
    ar=audit()
    if (ar["distinct_triples"]!=82 or ar["local_graph_components"]!=7
        or ar["global_historical_first_use_certified"] is not False
        or ar["new_source_requests"]!=0 or ar["scientific_pass"] is not False):
        raise NotAdmitted("F43_F40_ARCHIVE_AUDIT_CHANGED")
    q,p,old,new=source_facts()
    memory=ExactIndex(q,p)
    for r in old+new:
        memory.insert(r)
    snapshot=memory.snapshot()
    if sha256(snapshot).hexdigest()!=FROZEN_F42_SHA or len(snapshot)!=630:
        raise NotAdmitted("F43_F42_SNAPSHOT_IDENTITY_DRIFT")
    graph=ExactIndex.restore(snapshot).decoded_triples()
    comp_map, comps=build_components(
        [(f"Q{s}",f"P{relation}",f"Q{o}") for s,relation,o in graph])
    if len(graph)!=82 or len(comps)!=7:
        raise NotAdmitted("F43_COMPONENT_IDENTITY_CHANGED")
    route={}
    trainees=[]
    targets=[]
    sizes=[]
    for slot,(_,nodes) in enumerate(comps):
        if len(nodes)<2:
            raise NotAdmitted("F43_NO_HELDOUT_IN_COMPONENT")
        nodes=sorted(nodes,key=_qid_sort)
        trainees.append(nodes[0])
        targets.extend(nodes[1:])
        sizes.append(len(nodes))
        for qid in nodes:
            if qid in route or qid in RESERVED:
                raise NotAdmitted("F43_GRAPH_RESERVED_OR_DUPLICATE_ENTITY")
            route[qid]=slot
    if (tuple(trainees)!=TRAIN_ROOTS or len(route)!=78 or len(targets)!=71
        or sorted(sizes)!=[5,5,7,8,8,22,23]
        or len(set(route.values()))!=7):
        raise NotAdmitted("F43_FROZEN_GRAPH_SPLIT_DRIFT")
    return route,tuple(trainees),tuple(targets),tuple(sizes),snapshot


def route_entity(route,qid):
    if type(qid) is not str or qid in RESERVED or qid not in route:
        raise NotAdmitted("F43_UNSEEN_OR_RESERVED_ENTITY_NOT_ADMITTED")
    return route[qid]


class ConventionalCounts:
    """Equal 16x2x2 int16 count learner using the same public observations.

    This is a fully updated empirical conventional two-arm comparator. It has
    exactly 128 learned counter bytes, same as PublicCausalCells, and identical
    component routing/experiences. No privileged outcome labels are received.
    """
    def __init__(self):
        self.counts=[[[0,0] for _ in range(2)] for _ in range(16)]

    def observe(self, slot,action,outcome,*,retained=False):
        if (type(slot) is not int or type(retained) is not bool
            or not 0<=slot<(9 if retained else 7)
            or type(action) is not int or action not in (0,1)
            or type(outcome) is not int or outcome not in (0,1)):
            raise ValueError("F43_INVALID_EMPIRICAL_PUBLIC_OBSERVATION")
        addr=slot+(7 if retained else 0)
        self.counts[addr][action][outcome]=min(65535,self.counts[addr][action][outcome]+1)

    def choose(self,slot,*,retained=False):
        if type(slot) is not int or type(retained) is not bool or not 0<=slot<(9 if retained else 7):
            raise ValueError("F43_INVALID_EMPIRICAL_CONTEXT")
        a,b=self.counts[slot+(7 if retained else 0)]
        n0,n1=sum(a),sum(b)
        if not n0 or not n1 or a[1]*n1==b[1]*n0:
            return None
        return 0 if a[1]*n1>b[1]*n0 else 1

    def learned_state(self):
        return b"".join(struct.pack(">H",n) for cell in self.counts
                        for arm in cell for n in arm)


def outcome(action,preferred):
    """World reveals only THIS ACTION's synthetic consequence after it is tried."""
    if type(action) is not int or action not in (0,1) or preferred not in (0,1):
        raise ValueError("F43_UNADMITTED_WORLD_ACTION")
    return int(action==preferred)


def query_known_entities(model,route,targets,preference=FROZEN_PREF,shift=0):
    correct=0
    covered=0
    wrong=0
    abstain=0
    for qid in targets:
        true_slot=route_entity(route,qid)
        routed=(true_slot+shift)%7
        selected=model.choose(routed)
        if selected is None:
            abstain+=1
        else:
            covered+=1
            if selected==preference[true_slot]:
                correct+=1
            else:
                wrong+=1
    return {"queries":len(targets),"covered":covered,"correct":correct,
            "wrong":wrong,"abstained":abstain}


def run():
    policy=preregistration()
    route,train,target,sizes,graph_snapshot=graph_contexts()
    native=PublicCausalCells()
    conventional=ConventionalCounts()
    exact_observed_rule={}
    per_qid_training={}
    if (PublicCausalCells.LEARNED_BYTES!=128
        or PublicCausalCells.CHECKPOINT_BYTES!=164
        or PublicCausalCells.ACTIVE_SLOTS!=7
        or PublicCausalCells.RETAINED_SLOTS!=9):
        raise NotAdmitted("F43_NATIVE_BUDGET_CHANGED")
    for slot,qid in enumerate(train):
        preferred=FROZEN_PREF[slot]
        # 8 actual action-consequence observations per component.
        for _ in range(4):
            for action in (0,1):
                result=outcome(action,preferred)
                native.observe(slot,action,result)
                conventional.observe(slot,action,result)
        # Symbolic empirical exact table gets the same observed action/outcomes.
        exact_observed_rule[slot]=conventional.choose(slot)
        per_qid_training[qid]=exact_observed_rule[slot]
    active_count=7*4*2
    checkpoint_before=native.snapshot()
    # We never observe outcomes at any of the 71 test QIDs.
    warm_native=query_known_entities(native,route,target)
    warm_control=query_known_entities(conventional,route,target)
    raw_id_coverage=sum(q in per_qid_training for q in target)
    exact_symbolic_correct=sum(
        exact_observed_rule[route_entity(route,q)]==FROZEN_PREF[route_entity(route,q)]
        for q in target)
    mistaken_component=query_known_entities(native,route,target,shift=1)
    # Nine independent retained slots receive distinct, opposite action
    # experiences; check no collateral changes to 7 active contexts.
    for slot in range(9):
        preferred=(slot+1)%2
        for _ in range(4):
            for action in (0,1):
                result=outcome(action,preferred)
                native.observe(slot,action,result,retained=True)
                conventional.observe(slot,action,result,retained=True)
    retained_count=9*4*2
    if (tuple(native.choose(i,retained=True) for i in range(9))
        !=tuple((i+1)%2 for i in range(9))):
        raise NotAdmitted("F43_RETAINED_PUBLIC_OUTCOME_LEARNING_FAILED")
    if len(conventional.learned_state())!=128:
        raise NotAdmitted("F43_CONVENTIONAL_STATE_BUDGET_DRIFT")
    cold=PublicCausalCells.restore(native.snapshot())
    cold_native=query_known_entities(cold,route,target)
    after_native=query_known_entities(native,route,target)
    after_control=query_known_entities(conventional,route,target)
    if (warm_native!=cold_native or warm_native!=after_native
        or warm_control!=after_control or warm_native!=warm_control
        or len(native.snapshot())!=164
        or checkpoint_before[:4]!=b"YPC1"):
        raise NotAdmitted("F43_NATIVE_RETENTION_OR_CONVENTIONAL_PARITY_DRIFT")
    if (len(graph_snapshot)!=630 or any(q in train for q in target)
        or set(target)&RESERVED or any(q in RESERVED for q in train)):
        raise NotAdmitted("F43_SOURCE_OR_EVALUATION_LEAKAGE")
    result={
        "schema":RESULT_SCHEMA,
        "frozen_precode_source":"73fac0ff4aa8ce4fb5ed65ad067e5dc035c7cd92",
        "f42_cold_source_sha256":sha256(graph_snapshot).hexdigest(),
        "classification":"DEV_NATIVE_ROUTING_NO_GO",
        "source_triples":82,"graph_entities":78,"components":len(train),
        "component_sizes":list(sizes),
        "training_graph_entities":list(train),
        "query_graph_entities_heldout_from_actions":len(target),
        "known_source_graph_unseen_externally":False,
        "public_train_events":active_count,
        "retained_interference_events":retained_count,
        "total_observed_action_consequence_events":active_count+retained_count,
        "native_learned_bytes":PublicCausalCells.LEARNED_BYTES,
        "native_checkpoint_bytes":PublicCausalCells.CHECKPOINT_BYTES,
        "conventional_learned_bytes":len(conventional.learned_state()),
        "graph_serialized_bytes":len(graph_snapshot),
        "native_and_exact_graph_snapshot_bytes":len(graph_snapshot)+len(native.snapshot()),
        "native_warm_known_component_entity_queries":warm_native,
        "native_cold_known_component_entity_queries":cold_native,
        "native_after_retained_interference":after_native,
        "equal_information_trained_conventional":after_control,
        "exact_symbolic_observed_action_rule_correct":exact_symbolic_correct,
        "identity_only_source_heldout_coverage":raw_id_coverage,
        "wrong_component_mapping_negative":mistaken_component,
        "native_checkpoint_sha256":sha256(native.snapshot()).hexdigest(),
        "native_and_conventional_predictions_identical":warm_native==warm_control,
        "learned_graph_relations_natively":False,
        "transfer_to_new_source_graph":False,
        "fully_trained_conventional_comparison_performed":True,
        "scientific_pass":False,
        "native_accepted_source_modified":False,
        "protected_scientific_first_use_consumed":False,
        "external_source_requests":0,
        "new_scheduled_tasks":0
    }
    gates=policy["frozen_metrics"]
    if (len(train)==gates["source_graph_components"]
        and len(target)==gates["source_graph_known_identity_holdouts"]
        and active_count==gates["public_training_active_events"]
        and retained_count==gates["public_interference_retained_events"]
        and all(v["covered"]>=71 and v["correct"]>=71
                for v in (warm_native,cold_native,after_native,after_control))
        and warm_native==after_control
        and exact_symbolic_correct==71
        and raw_id_coverage==0
        and mistaken_component["correct"]<71):
        result["classification"]="DEV_NATIVE_ROUTING_PARITY_ONLY"
    return result


def main():
    result=run()
    print("F43_SOURCE_KNOWN_NATIVE_ACTION_CONSEQUENCE_DEV_RESULT="+
          json.dumps(result,sort_keys=True,separators=(",",":")))
    print("F43_NATIVE_SCIENTIFIC_PASS=FALSE")
    if result["classification"]!="DEV_NATIVE_ROUTING_PARITY_ONLY":
        raise SystemExit(2)


if __name__=="__main__":
    main()
