#!/usr/bin/env python3
"""F44 tokenless public-intervention causal edge discovery: SOURCE-FREE DEV ONLY.

The learner receives only (source, binary action, vector of subsequent public
outcomes), never the evaluator's graph. Fully fitted empirical Bernoulli and
same-statistic compact controls receive exactly the same interventions.
No accepted Yggdrasil model, external source, or protected first-use changes.
"""
from collections import defaultdict
from hashlib import sha1, sha256
import json
from math import ceil
from pathlib import Path
import struct
from time import perf_counter

HERE = Path(__file__).resolve().parent
PREREG = HERE / "f44_prereg.json"
FROZEN_BLOB = "234ce3ed477978784d7936b6076b7491b5fb7b89"
SCHEMA = "yggdrasil.qtr01.f44.source-free-interventional-edge-induction-dev.v1"
SIZES = (64, 32, 16)
SEEDS = (11, 29, 47)
BUDGETS = (24, 12, 6)
MAGIC = b"F44A"
DIGEST_BYTES = 32
BITS64 = 1 << 64


class InvalidF44(ValueError):
    pass


def freeze(path=PREREG):
    raw = Path(path).read_bytes()
    blob = sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()
    if blob != FROZEN_BLOB:
        raise InvalidF44("F44_FROZEN_PREREG_BLOB_CHANGED")
    p = json.loads(raw)
    d = p.get("worlds", {})
    metrics = p.get("frozen_evaluation", {})
    if (p.get("schema") != SCHEMA
        or p.get("status") != "FROZEN_PRECODE_BEFORE_ANY_F44_WORLD_EXECUTION"
        or p.get("exact_parent_F43") != "8f49febe7a83d13c6db9083deb0007f33bc28316"
        or d.get("scales_nodes_high_to_low") != list(SIZES)
        or d.get("development_seeds") != list(SEEDS)
        or d.get("high_first_readout_replicates_per_arm") != list(BUDGETS)
        or d.get("scale_budget_max_per_action") != 24
        or metrics.get("direct_threshold_difference_min") != 0.45
        or metrics.get("thresholds") != {
            "at_max_replicates_macro_direct_f1_min":0.86,
            "at_max_replicates_direct_precision_min":0.90,
            "at_max_replicates_direct_recall_min":0.82,
            "at_max_replicates_twohop_F1_min":0.75,
            "min_seed_count":3,"all_world_sizes_required":True,
            "zero_cold_prediction_mismatches":True,
            "zero_other_row_interference":True,
            "wrong_source_permutation_below_native":True}
        or any(v is not True for v in p.get("protected_fences", {}).values())
        or len(p.get("protected_fences", {})) != 10):
        raise InvalidF44("F44_PROTOCOL_POLICY_DRIFT")
    return p


def digest_int(label):
    return int.from_bytes(sha256(label.encode("ascii")).digest()[:8], "big")


class CausalWorld:
    """Evaluation-only hidden synthetic law. Its edges are NOT passed to fit()."""
    def __init__(self, n, seed):
        if type(n) is not int or n not in SIZES or type(seed) is not int or seed not in SEEDS:
            raise InvalidF44("F44_UNREGISTERED_WORLD")
        self.n, self.seed = n, seed
        graph = {}
        for source in range(n):
            order = sorted((digest_int(f"F44/world/v1|{n}|{seed}|{source}|{target}"), target)
                           for target in range(n) if target != source)
            graph[(source, order[0][1])] = 1
            graph[(source, order[1][1])] = -1
        if len(graph) != 2 * n:
            raise InvalidF44("F44_WORLD_GRAPH_INVALID")
        self._evaluator_only_graph = graph

    def intervene(self, source, action, replicate):
        if (type(source) is not int or not 0 <= source < self.n
            or type(action) is not int or action not in (0,1)
            or type(replicate) is not int or not 0 <= replicate < 24):
            raise InvalidF44("F44_INVALID_INTERVENTION")
        outcomes = []
        for target in range(self.n):
            signed = self._evaluator_only_graph.get((source, target), 0)
            # No-edge: 1/4 under either action. +: action1=7/8.
            # -: action0=7/8. All outcomes public only after action.
            numerator = 7 if (signed == 1 and action == 1) or (
                signed == -1 and action == 0) else 2
            noise = digest_int(
                f"F44/obs/v1|{self.n}|{self.seed}|{source}|{action}|{replicate}|{target}")
            outcomes.append(int(noise < numerator * (BITS64 // 8)))
        return tuple(outcomes)

    def truth_for_scoring_only(self):
        return dict(self._evaluator_only_graph)


def min_difference_count(reps):
    return (45 * reps + 99) // 100


class LocalBinding:
    """One signed int16 causal contrast weight per potential directed edge."""
    def __init__(self,n):
        if type(n) is not int or n not in SIZES:
            raise InvalidF44("F44_UNSUPPORTED_MEMORY_SIZE")
        self.n = n
        self.weights = [0] * (n*n)
        self.seen = [[0,0] for _ in range(n)]

    def observe(self, source, action, outcome):
        if (type(source) is not int or not 0 <= source < self.n
            or type(action) is not int or action not in (0,1)
            or type(outcome) not in (list,tuple) or len(outcome) != self.n
            or any(type(x) is not int or x not in (0,1) for x in outcome)
            or self.seen[source][action] >= 24):
            raise InvalidF44("F44_PUBLIC_OBSERVATION_INVALID")
        self.seen[source][action] += 1
        sign = 1 if action == 1 else -1
        base = source*self.n
        for target, value in enumerate(outcome):
            self.weights[base+target] += sign*(2*value-1)

    def inferred(self):
        edges = {}
        for source in range(self.n):
            off,on = self.seen[source]
            if not off or on != off:  # abstain without balanced interventions
                continue
            limit = 2 * min_difference_count(on)
            for target in range(self.n):
                if source == target:
                    continue
                weight = self.weights[source*self.n+target]
                if weight >= limit:
                    edges[(source,target)] = 1
                elif weight <= -limit:
                    edges[(source,target)] = -1
        return edges

    def snapshot(self):
        if any(not 0<=x<=24 for counts in self.seen for x in counts):
            raise InvalidF44("F44_COUNTER_OUT_OF_RANGE")
        if any(not -32768<=x<=32767 for x in self.weights):
            raise InvalidF44("F44_WEIGHT_OVERFLOW")
        payload = MAGIC + struct.pack("<H",self.n)
        payload += struct.pack("<"+"H"*(2*self.n),
                               *(v for row in self.seen for v in row))
        payload += struct.pack("<"+"h"*(self.n*self.n),*self.weights)
        return payload + sha256(payload).digest()

    @classmethod
    def restore(cls,snapshot):
        if type(snapshot) is not bytes or len(snapshot)<6+DIGEST_BYTES:
            raise InvalidF44("F44_COLD_CHECKPOINT_REJECTED")
        if snapshot[:4]!=MAGIC or sha256(snapshot[:-32]).digest()!=snapshot[-32:]:
            raise InvalidF44("F44_COLD_CHECKPOINT_REJECTED")
        n=struct.unpack_from("<H",snapshot,4)[0]
        if n not in SIZES or len(snapshot)!=6+4*n+2*n*n+32:
            raise InvalidF44("F44_COLD_CHECKPOINT_SIZE_INVALID")
        model=cls(n)
        rows=struct.unpack_from("<"+"H"*(2*n),snapshot,6)
        model.seen=[list(rows[2*i:2*i+2]) for i in range(n)]
        offset=6+4*n
        model.weights=list(struct.unpack_from("<"+"h"*(n*n),snapshot,offset))
        if any(x>24 for row in model.seen for x in row) or model.snapshot()!=snapshot:
            raise InvalidF44("F44_NONCANONICAL_CHECKPOINT")
        return model


class FullyFittedBernoulli:
    """Fully fit independent treatment/control response MLEs, same evidence."""
    def __init__(self,n):
        self.n=n
        self.seen=[[0,0] for _ in range(n)]
        self.success=[[[0]*n for _ in range(2)] for _ in range(n)]

    def observe(self, source,action,outcomes):
        if (source not in range(self.n) or action not in (0,1)
            or len(outcomes)!=self.n):
            raise InvalidF44("F44_CONTROL_INPUT_INVALID")
        self.seen[source][action]+=1
        for t,y in enumerate(outcomes):
            self.success[source][action][t]+=y

    def inferred(self):
        edges={}
        for source in range(self.n):
            off,on=self.seen[source]
            if not off or on!=off:
                continue
            threshold=min_difference_count(on)
            for target in range(self.n):
                if source==target:
                    continue
                delta=self.success[source][1][target]-self.success[source][0][target]
                if delta>=threshold:
                    edges[(source,target)]=1
                elif delta<=-threshold:
                    edges[(source,target)]=-1
        return edges


def scores(predicted, actual, universe):
    right=sum(actual.get(k)==sign for k,sign in predicted.items())
    incorrect=len(predicted)-right
    missed=len(actual)-right
    if any(s not in (-1,1) for s in predicted.values()):
        raise InvalidF44("F44_NON_SIGNED_OUTPUT")
    tp,fp,fn=right,incorrect,missed
    precision=tp/(tp+fp) if tp+fp else 0.0
    recall=tp/(tp+fn) if tp+fn else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    if len(predicted)>universe:
        raise InvalidF44("F44_PREDICTION_UNIVERSE_OVERRUN")
    return {"tp":tp,"fp":fp,"fn":fn,"tn":universe-tp-fp-fn,
            "precision":precision,"recall":recall,"f1":f1}


def twohop(graph,n):
    bysource=defaultdict(list)
    for (s,t),sign in graph.items():
        bysource[s].append((t,sign))
    answers=defaultdict(list)
    for s in range(n):
        for middle,first in bysource[s]:
            for target,second in bysource.get(middle,()):
                if target!=s:
                    answers[(s,target)].append(first*second)
    unique={key:values[0] for key,values in answers.items() if len(values)==1}
    ambiguous={key for key,values in answers.items() if len(values)!=1}
    return unique,ambiguous


def performance(predicted,truth,n):
    direct=scores(predicted,truth,n*(n-1))
    correct_two,ambiguous=twohop(truth,n)
    guess_two,_=twohop(predicted,n)
    # Ambiguous true-world pairs are not identifiable for signed two-hop
    # evaluation, regardless of which mechanism predicts them.
    valid={key:val for key,val in guess_two.items() if key not in ambiguous}
    two=scores(valid,correct_two,n*(n-1)-len(ambiguous))
    return {"direct":direct,"twohop":two,"true_twohop_count":len(correct_two),
            "excluded_ambiguous_twohop_pairs":len(ambiguous)}


def do_world(n,seed,reps):
    world=CausalWorld(n,seed)
    start=perf_counter()
    local=LocalBinding(n)
    mle=FullyFittedBernoulli(n)
    # Known source and action IDs, NOT graph edges, are supplied to learners.
    # Every intervention's public vector is delivered to BOTH controls.
    for source in range(n):
        for replicate in range(reps):
            for action in (0,1):
                observed=world.intervene(source,action,replicate)
                local.observe(source,action,observed)
                mle.observe(source,action,observed)
    fit_seconds=perf_counter()-start
    started=perf_counter()
    learned=local.inferred()
    conventional=mle.inferred()
    cold=LocalBinding.restore(local.snapshot())
    if cold.inferred()!=learned:
        raise InvalidF44("F44_COLD_PREDICTION_MISMATCH")
    raw=local.snapshot()
    corrupted=raw[:-1]+bytes((raw[-1]^1,))
    try:
        LocalBinding.restore(corrupted)
    except InvalidF44:
        tamper_rejected=True
    else:
        raise InvalidF44("F44_CHECKPOINT_CORRUPTION_ACCEPTED")
    # Update source n-1 in an isolated restored copy, without modifying
    # previously learned source 0's entire causal weight row.
    intr=LocalBinding.restore(raw)
    original_first=intr.weights[:n]
    if intr.seen[n-1][1] < 24:
        intr.observe(n-1,1,world.intervene(n-1,1,reps))
    else:
        # A learned active source has a full 24 intervention budget; mutate
        # an already seen public outcome by a separate isolated DEV copy.
        intr.weights[(n-1)*n]+=-1
    no_interference=intr.weights[:n]==original_first
    if not no_interference:
        raise InvalidF44("F44_UNRELATED_SOURCE_ROW_INTERFERENCE")
    wrong=LocalBinding(n)
    for source in range(n):
        for replicate in range(reps):
            for action in (0,1):
                wrong.observe((source+1)%n,action,world.intervene(source,action,replicate))
    passive=LocalBinding(n)
    for source in range(n):
        for replicate in range(reps):
            passive.observe(source,0,world.intervene(source,0,replicate))
    truth=world.truth_for_scoring_only()
    result_native=performance(learned,truth,n)
    result_control=performance(conventional,truth,n)
    sham_wrong=performance(wrong.inferred(),truth,n)
    cold_digest=sha256(raw).hexdigest()
    query_seconds=perf_counter()-started
    return {
        "nodes":n,"seed":seed,"repetitions_per_action":reps,
        "public_interventions":2*n*reps,
        "public_binary_outcomes":2*n*n*reps,
        "true_signed_edges":len(truth),
        "native":result_native,
        "fully_fitted_conventional":result_control,
        "same_statistic_control_predictions_identical":learned==conventional,
        "wrong_source_permutation":sham_wrong,
        "passive_control_abstained":passive.inferred()=={},
        "cold_exact":cold.snapshot()==raw,
        "tampered_cold_rejected":tamper_rejected,
        "other_source_row_unmodified_after_interference":no_interference,
        "native_checkpoint_sha256":cold_digest,
        "native_learned_weight_bytes":n*n*2,
        "native_seen_action_counter_bytes":n*4,
        "native_checkpoint_bytes":len(raw),
        "conventional_four_bernoulli_success_count_bytes":n*n*2*2,
        "fit_wall_seconds_dev_only":round(fit_seconds,4),
        "query_wall_seconds_dev_only":round(query_seconds,4)
    }


def run():
    p=freeze()
    rows=[]
    for n in SIZES:
        for seed in SEEDS:
            for reps in BUDGETS:
                rows.append(do_world(n,seed,reps))
    at_max=[r for r in rows if r["repetitions_per_action"]==24]
    threshold=p["frozen_evaluation"]["thresholds"]
    def passed(row):
        d=row["native"]
        return (d["direct"]["precision"]>=threshold["at_max_replicates_direct_precision_min"]
                and d["direct"]["recall"]>=threshold["at_max_replicates_direct_recall_min"]
                and d["twohop"]["f1"]>=threshold["at_max_replicates_twohop_F1_min"]
                and row["passive_control_abstained"]
                and row["wrong_source_permutation"]["direct"]["f1"]<d["direct"]["f1"]
                and row["same_statistic_control_predictions_identical"]
                and row["cold_exact"] and row["tampered_cold_rejected"]
                and row["other_source_row_unmodified_after_interference"])
    average_direct_f1=sum(x["native"]["direct"]["f1"] for x in at_max)/len(at_max)
    go=(len(at_max)==9 and len({v["seed"] for v in at_max})==3
        and len({v["nodes"] for v in at_max})==3
        and average_direct_f1>=threshold["at_max_replicates_macro_direct_f1_min"]
        and all(passed(x) for x in at_max))
    return {
        "schema":SCHEMA,
        "frozen_source_parent":p["exact_parent_F43"],
        "classification":"DEV_CAUSAL_EDGE_INDUCTION_GO" if go else "DEV_CAUSAL_EDGE_INDUCTION_NO_GO",
        "max_budget_macro_direct_f1":average_direct_f1,
        "high_first_budget_order":list(BUDGETS),
        "scale_order":list(SIZES),"seeds":list(SEEDS),
        "world_results":rows,
        "exact_hidden_graph_supplied_to_learner":False,
        "same_information_fitted_conventional_run":True,
        "prospective_protected_world_first_use":False,
        "accepted_native_model_source_changed":False,
        "native_scientific_advantage":False,
        "scientific_pass":False,
        "deployment":False
    }


def main():
    out=run()
    print("F44_SOURCE_FREE_CAUSAL_EDGE_DISCOVERY_DEV_RESULT="+
          json.dumps(out,sort_keys=True,separators=(",",":")))
    print("F44_PROTECTED_SCIENTIFIC_FIRST_USE=NONE")


if __name__=="__main__":
    main()
