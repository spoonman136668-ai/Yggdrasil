#!/usr/bin/env python3
"""F41: source-free, high-to-low direct bit-association scaling DEV experiment.

No new source is inspected. No recipient neural model is run or changed. The
source-exact symbolic graph is the correctness ceiling; bit membership is not
learning or unseen-domain generalization.
"""
from hashlib import blake2b, sha1, sha256
from itertools import product
import json
from pathlib import Path
import struct
from time import perf_counter

from f26_semantic_association import NotAdmitted, qnum
from f34_direct_bitweights import DirectBitWeights
from f38_composition_dev import exact_source_paths, exact_answer_set, bit_answer_set
from f40_component_isolation_audit import audit, read_archives, validate

HERE = Path(__file__).resolve().parent
POLICY = HERE / "f41_prereg.json"
SCHEMA = "yggdrasil.qtr01.f41.archived-82-relations-bitweight-scaling-dev.v1"
PREREG_BLOB = "bec761a5189142056afb63336de0374077e3a4e4"
CAPACITIES = (8192, 4096, 2048, 1024, 512)
ROOTS = ("Q2", "Q5", "Q17", "Q30", "Q42", "Q64", "Q76", "Q80", "Q90", "Q95")
PERSON = b"QTRF34"


def get_protocol(path=POLICY):
    raw = Path(path).read_bytes()
    if sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest() != PREREG_BLOB:
        raise NotAdmitted("F41_FROZEN_PREREG_BLOB_MISMATCH")
    p = json.loads(raw)
    required = (
        p.get("schema") == SCHEMA,
        p.get("status") == "FROZEN_BEFORE_F41_EXECUTABLE_OR_RESULT",
        p.get("source_parent_sha") == "5a6420f8af8c2cca33d1a443c3317bfe3e963303",
        p.get("capacities_bits_high_to_low") == list(CAPACITIES),
        p.get("root_query_ids") == list(ROOTS),
        p.get("source_frozen_component_baseline") == {
            "triples": 82, "q_entities": 78, "subject_entities": 26,
            "undirected_components": 7, "prior_entity_overlap_with_fit": 4,
            "prior_source_complete": False},
        p.get("existing_native_bit_algorithm", {}).get("blob") == "2df50bedccc2fc674231f440891107ea5b96f6d9",
        p.get("existing_native_bit_algorithm", {}).get("k_hashes") == 3,
        p.get("existing_native_bit_algorithm", {}).get("digest_personalization") == "QTRF34",
        p.get("thresholds", {}).get("full_positive_recall_min") == 1.0,
        p.get("thresholds", {}).get("twohop_precision_min") == 0.95,
        p.get("thresholds", {}).get("twohop_false_positive_rate_max") == 0.01,
        p.get("thresholds", {}).get("cold_exact_parity") is True,
        p.get("thresholds", {}).get("lower_payload_than_exact_numeric_triples") is True,
        p.get("thresholds", {}).get("minimum_candidate_vocab_charged_bytes") == 340,
        [(v.get("sha256"), v.get("rows"), v.get("key"))
         for v in p.get("inputs", ())] == [
            ("e9ead9ac15e4ecbe4d99216cda43657e1aeb030d22f59fd852f8b99fa0d440eb", 13, "typed_source_rows"),
            ("cf5ffeab63384a61e66e30930f16ce3af07df81cb28472b0142f7a5c6b673954", 20, "added_witnessed_source_rows"),
            ("7d223dcb9d9082059cdc237d7a551c2a3a0f21ca81824318bec1624aa25c4044", 49, "witnessed_rows"),
        ],
        all(p.get("source_fences", {}).get(k) is True for k in (
            "no_network_or_unseen_source_read", "no_reserved_qid_first_use",
            "no_native_recipient_weight_edit", "no_donor_llm_or_qwen_calls",
            "no_protected_scientific_first_use",
            "no_new_scheduled_tasks_or_controllers", "no_paid_api",
            "no_main_or_accepted_ref", "no_merge_or_deployment",
            "no_claim_of_native_training_or_generalization")),
    )
    if not all(required):
        raise NotAdmitted("F41_FROZEN_POLICY_DRIFT")
    return p


ERRATUM = HERE / "f41_source_inventory_erratum.json"
ERRATUM_BLOB = "e6ef619f2397382c1e87ef1d947cabadfc0a6fcc"


def corrected_inventory(path=ERRATUM):
    raw = Path(path).read_bytes()
    if sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest() != ERRATUM_BLOB:
        raise NotAdmitted("F41_SOURCE_INVENTORY_ERRATUM_BLOB_MISMATCH")
    obj = json.loads(raw)
    actual = obj.get("mechanical_findings", {})
    if (obj.get("schema") != "yggdrasil.qtr01.f41.source-inventory-mechanical-erratum.v1"
        or obj.get("status") != "POST_PREQUALIFICATION_DIAGNOSTIC_MATH_CORRECTION_NO_THRESHOLD_OR_CAPACITY_CHANGE"
        or obj.get("original_prereg_blob") != PREREG_BLOB
        or obj.get("original_predeclared_capacity_bits") != list(CAPACITIES)
        or obj.get("original_precision_threshold_min") != 0.95
        or obj.get("original_false_positive_rate_threshold_max") != 0.01
        or obj.get("original_payload_less_than_raw_984_bytes_required") is not True
        or obj.get("original_declared_candidate_vocab_lower_bound_bytes") != 340
        or actual.get("observed_archived_source_predicate_ids") != [
            "P17","P19","P31","P69","P106","P279","P361","P463"]
        or actual.get("distinct_predicates") != 8
        or actual.get("distinct_entities") != 78
        or actual.get("corrected_candidate_vocab_lower_bound_bytes") != 344
        or any(obj.get("fences", {}).get(k) is not True for k in (
            "no_new_data_source","no_reserved_evaluation_first_use",
            "no_native_weights","no_threshold_tuning","no_capacity_tuning",
            "no_promotions","no_main","no_merge","no_paid_api","no_scheduler"))):
        raise NotAdmitted("F41_SOURCE_INVENTORY_ERRATUM_DRIFT")
    return obj


class ScaledBitAssociations:
    def __init__(self, bits, snapshot=None, digest=None):
        if bits not in CAPACITIES:
            raise NotAdmitted("F41_UNREGISTERED_BIT_CAPACITY")
        self.bits = bits
        if snapshot is None:
            self.data = bytearray(bits // 8)
        elif (type(snapshot) is bytes and len(snapshot) == bits // 8
              and type(digest) is str and sha256(snapshot).hexdigest() == digest):
            self.data = bytearray(snapshot)
        else:
            raise NotAdmitted("F41_SNAPSHOT_DIGEST_OR_SIZE_MISMATCH")

    def slots(self, triple):
        if (type(triple) is not tuple or len(triple) != 3
                or any(type(v) is not int or v <= 0 or v >= 2**32 for v in triple)):
            raise NotAdmitted("F41_INVALID_TRIPLE")
        key = struct.pack("<III", *triple)
        hashed = blake2b(key, digest_size=16, person=PERSON).digest()
        return tuple(struct.unpack_from("<I", hashed, 4*i)[0] % self.bits
                     for i in range(3))

    def program(self, triple):
        for bit in self.slots(triple):
            self.data[bit >> 3] |= 1 << (bit & 7)

    def contains(self, triple):
        return all(self.data[bit >> 3] & (1 << (bit & 7))
                   for bit in self.slots(triple))

    def snapshot(self):
        return bytes(self.data)

    def restore(self):
        snapshot = self.snapshot()
        return ScaledBitAssociations(self.bits, snapshot, sha256(snapshot).hexdigest())


def frozen_graph():
    get_protocol()
    prior = audit()
    if (prior["distinct_triples"] != 82
        or prior["distinct_entities"] != 78
        or prior["local_graph_components"] != 7
        or prior["scientific_pass"] is not False
        or prior["global_historical_first_use_certified"] is not False
        or prior["new_source_requests"] != 0):
        raise NotAdmitted("F41_F40_SOURCE_BASELINE_DRIFT")
    sources = read_archives()
    groups, triples, _ = validate(sources)
    if [len(g) for g in groups] != [13, 20, 49]:
        raise NotAdmitted("F41_SOURCE_GROUP_COUNT_DRIFT")
    fixed = [tuple(qnum(x, z) for x, z in zip(t, ("Q", "P", "Q"))) for t in triples]
    if len(set(fixed)) != 82:
        raise NotAdmitted("F41_DUPLICATE_FACT")
    return fixed[:33], fixed[33:]


def answers(triples, roots, predicates, nodes):
    truth = exact_answer_set(triples, roots, predicates, nodes)
    paths = exact_source_paths(triples)
    if not truth or not paths:
        raise NotAdmitted("F41_NO_COMPOSABLE_SOURCE")
    return truth, paths


def confusion(predicted, truth, total):
    tp, fp, fn = len(predicted & truth), len(predicted - truth), len(truth - predicted)
    tn = total - tp - fp - fn
    if tn < 0:
        raise NotAdmitted("F41_CONFUSION_MATRIX_OVERCOUNT")
    return {
        "tp":tp, "fp":fp, "fn":fn, "tn":tn,
        "precision":tp / (tp + fp) if tp + fp else 0.0,
        "recall":tp / len(truth) if truth else 0.0,
        "false_positive_rate":fp / (fp + tn) if fp + tn else 0.0
    }


def measure():
    p = get_protocol()
    erratum = corrected_inventory()
    original, added = frozen_graph()
    graph = original + added
    nodes = tuple(sorted({x for s, _, o in graph for x in (s, o)}))
    predicates = tuple(sorted({pr for _, pr, _ in graph}))
    roots = tuple(qnum(x, "Q") for x in ROOTS)
    if len(nodes) != 78 or len(predicates) != 8 or len(graph) != 82:
        raise NotAdmitted("F41_NODE_OR_PREDICATE_VOCABULARY_DRIFT")
    word_bytes = (len(nodes) + len(predicates)) * 4
    if word_bytes != erratum["mechanical_findings"]["corrected_candidate_vocab_lower_bound_bytes"]:
        raise NotAdmitted("F41_VOCABULARY_COST_DRIFT")
    truth, paths = answers(graph, roots, predicates, nodes)
    truth_members = set(graph)
    membership_total = len(nodes) ** 2 * len(predicates)
    query_total = len(roots) * len(predicates) ** 2 * len(nodes)
    if not truth.issubset(set(product(roots, predicates, predicates, nodes))):
        raise NotAdmitted("F41_OUT_OF_DOMAIN_PATH")
    exact_control_raw_coordinate_bytes = len(graph) * 12
    # Synthetic-only wrong-endpoint control. Rotating final objects changes
    # asserted rows; the resulting graph is never considered first-party truth.
    shuffled = [(s, pred, graph[(i+1) % len(graph)][2])
                for i, (s, pred, _) in enumerate(graph)]
    if set(shuffled) == truth_members:
        raise NotAdmitted("F41_SHUFFLED_NEGATIVE_INEFFECTIVE")
    result = []
    for m in CAPACITIES:
        started = perf_counter()
        memory = ScaledBitAssociations(m)
        for x in original:
            memory.program(x)
        old_snapshot = memory.snapshot()
        old_cold = memory.restore()
        if any(not old_cold.contains(x) for x in original):
            raise NotAdmitted("F41_ORIGINAL_COLD_RESTORE_LOSS")
        for x in added:
            memory.program(x)
        cold = memory.restore()
        old_preserved = sum(cold.contains(x) for x in original)
        new_written = sum(cold.contains(x) for x in added)
        if old_preserved != 33 or new_written != 49:
            raise NotAdmitted("F41_INCREMENTAL_SOURCE_FACT_LOSS")
        positive_members = set(graph)
        membership_positive_hits = sum(memory.contains(x) for x in positive_members)
        membership_false_positives = 0
        for triple in product(nodes, predicates, nodes):
            if triple not in positive_members and memory.contains(triple):
                membership_false_positives += 1
        predicted = bit_answer_set(memory, roots, predicates, nodes)
        restored = bit_answer_set(cold, roots, predicates, nodes)
        if predicted != restored or cold.snapshot() != memory.snapshot():
            raise NotAdmitted("F41_COLD_COMPOSITION_PARITY_FAILURE")
        score = confusion(predicted, truth, query_total)
        if m == 512:
            existing = DirectBitWeights()
            for x in graph:
                existing.program(x)
            if memory.snapshot() != existing.snapshot():
                raise NotAdmitted("F41_F34_512_BITS_ALGORITHM_DRIFT")
        if membership_positive_hits != len(graph) or score["fn"]:
            raise NotAdmitted("F41_POSITIVE_MEMBERSHIP_OR_COMPOSITION_LOSS")
        go = (score["recall"] >= p["thresholds"]["full_positive_recall_min"]
              and score["precision"] >= p["thresholds"]["twohop_precision_min"]
              and score["false_positive_rate"] <= p["thresholds"]["twohop_false_positive_rate_max"]
              and len(cold.snapshot()) < exact_control_raw_coordinate_bytes)
        result.append({
            "bits":m, "payload_bytes":len(cold.snapshot()),
            "payload_plus_vocab_lower_bound_bytes":len(cold.snapshot()) + word_bytes,
            "old_33_memberships_preserved":old_preserved,
            "new_49_memberships_written":new_written,
            "membership_true_positives":membership_positive_hits,
            "membership_false_positives":membership_false_positives,
            "membership_negative_candidate_count":membership_total - 82,
            "membership_fpr":membership_false_positives / (membership_total - 82),
            "twohop":score, "cold_query_parity":True,
            "direct_bit_capacity_go":go,
            "evaluation_wall_seconds_dev_only":round(perf_counter() - started, 4)
        })
    winners = [r for r in result if r["direct_bit_capacity_go"]]
    selected = min(winners, key=lambda x:x["bits"]) if winners else None
    return {
        "schema": SCHEMA,
        "classification":"DEV_CAPACITY_GO" if selected else "DEV_CAPACITY_NO_GO",
        "frozen_source_parent":p["source_parent_sha"],
        "frozen_input_sizes":[13,20,49], "source_triples":82,
        "distinct_entities":len(nodes), "distinct_predicates":len(predicates),
        "candidate_query_roots":len(roots), "witnessed_twohop_paths":len(paths),
        "source_positive_twohop_queries":len(truth),
        "membership_candidate_count":membership_total,
        "twohop_candidate_count":query_total,
        "exact_symbolic_tp":len(truth), "exact_symbolic_fp":0,
        "exact_symbolic_fn":0, "exact_symbolic_raw_triplet_bytes":exact_control_raw_coordinate_bytes,
        "minimum_candidate_vocabulary_bytes":word_bytes,
        "original_frozen_vocabulary_lower_bound_erroneous_bytes":p["thresholds"]["minimum_candidate_vocab_charged_bytes"],
        "mechanical_erratum_blob":ERRATUM_BLOB,
        "shuffled_endpoint_negative_changes_graph":set(shuffled) != truth_members,
        "capacities_tested_in_frozen_order":list(CAPACITIES),
        "capacity_results":result,
        "selected_smallest_passing_bits":selected["bits"] if selected else None,
        "vocab_labels_and_source_witness_receipts_excluded_from_payload_only_memory":True,
        "bounded_absent_path_not_worldwide_falsehood":True,
        "fully_trained_control_run":False,
        "native_recipient_weights_edited":False,
        "protected_first_use_consumed":False,
        "scientific_pass":False,
        "source_only_development":True
    }


def main():
    result = measure()
    print("F41_ARCHIVED_BIT_CAPACITY_RESULT=" +
          json.dumps(result,sort_keys=True,separators=(",", ":")))
    print("F41_NO_NEW_SOURCE_OR_NATIVE_MODEL_FIRST_USE=PASS")


if __name__ == "__main__":
    main()
