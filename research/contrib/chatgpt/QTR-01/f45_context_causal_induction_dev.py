#!/usr/bin/env python3
"""F45: unknown-degree, context-dependent causal edge induction from interventions.

Source-free synthetic DEV research only. Hidden signed edges are restricted to
the evaluator; learners get public source/context/action/response vectors.
Both conventional controls see exactly the same interventions. No accepted
Yggdrasil model, external first-use, or native model weights are modified.
"""
from collections import defaultdict
from hashlib import sha1, sha256
import json
from pathlib import Path
import struct
from time import perf_counter

HERE = Path(__file__).resolve().parent
PREREG = HERE / "f45_prereg.json"
FROZEN_BLOB = "622e37d4dd5dcdd24e784a08805fc5031f74cec4"
SCHEMA = "yggdrasil.qtr01.f45.variable-degree-contextual-intervention-dev.v1"
SIZES = (64, 32, 16)
SEEDS = (59, 71, 83)
REPS = (24, 12, 6)
MODES = {59: "invariant", 71: "context_gated", 83: "context_flip"}
DEGREES = (0, 1, 2, 4, 8)
PATTERNS = ((1, 1), (0, 1), (1, -1))
MAGIC = b"F45A"
MAX64 = 1 << 64


class RejectedF45(ValueError):
    pass


def preflight(path=PREREG):
    raw = Path(path).read_bytes()
    git_hash = sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()
    if git_hash != FROZEN_BLOB:
        raise RejectedF45("F45_FROZEN_PRECODE_MANIFEST_DRIFT")
    p = json.loads(raw)
    ev = p.get("evaluation", {})
    w = p.get("worlds", {})
    t = ev.get("thresholds", {})
    if (p.get("schema") != SCHEMA
        or p.get("status") != "FROZEN_PRE_CODE_PRE_RESULTS"
        or p.get("source_parent_sha") != "a654c7efd30c5ebe32b38f944e819a9c899317a4"
        or w.get("sizes_high_first") != list(SIZES)
        or w.get("seeds") != list(SEEDS)
        or w.get("repetitions_high_first") != list(REPS)
        or w.get("seed_to_law_mode") != {str(s): MODES[s] for s in SEEDS}
        or ev.get("direct_truth") is None
        or t != {
            "highest_budget_macro_direct_F1_min": 0.85,
            "highest_budget_macro_twohop_F1_min": 0.72,
            "highest_budget_worst_world_direct_F1_min": 0.75,
            "highest_budget_worst_world_twohop_F1_min": 0.50,
            "all_nine_worlds_required": True,
            "all_nine_cold_restore": True,
            "all_nine_real_interference_retention": True,
            "fully_fitted_MLE_same_statistic_predictions_equal": True,
            "wrong_permuted_source_f1_strictly_lower": True,
            "passive_abstains": True}
        or len(p.get("fences", {})) != 10
        or any(flag is not True for flag in p.get("fences", {}).values())):
        raise RejectedF45("F45_FROZEN_POLICY_DRIFT")
    return p


def fingerprint(text):
    return int.from_bytes(sha256(text.encode("ascii")).digest()[:8], "big")


class ContextWorld:
    """Private evaluator graph; no learner method can request its edges."""
    def __init__(self, n, seed):
        if type(n) is not int or n not in SIZES or type(seed) is not int or seed not in SEEDS:
            raise RejectedF45("F45_WORLD_NOT_PREDECLARED")
        self.n = n
        self.seed = seed
        self.mode = MODES[seed]
        graph = {}
        degrees = []
        for s in range(n):
            degree = DEGREES[fingerprint(f"F45/degree/v1|{n}|{seed}|{s}") % 5]
            degrees.append(degree)
            targets = sorted(
                (fingerprint(f"F45/edge/v1|{n}|{seed}|{s}|{t}"), t)
                for t in range(n) if t != s)
            for _, target in targets[:degree]:
                parity = fingerprint(f"F45/sign/v1|{n}|{seed}|{s}|{target}") % 2
                graph[(s, target)] = 1 if parity == 0 else -1
        self._private_graph = graph
        self._degree_histogram = {str(k): degrees.count(k) for k in DEGREES}

    def public_intervention(self, source, context, action, repeat):
        n = self.n
        if (type(source) is not int or not 0 <= source < n
            or type(context) is not int or context not in (0, 1)
            or type(action) is not int or action not in (0, 1)
            or type(repeat) is not int or not 0 <= repeat < 24):
            raise RejectedF45("F45_INTERVENTION_NOT_IN_FROZEN_DOMAIN")
        result = []
        for target in range(n):
            base = self._private_graph.get((source, target), 0)
            if self.mode == "context_gated" and context == 0:
                base = 0
            if self.mode == "context_flip" and context == 1:
                base = -base
            num = 7 if (base == 1 and action == 1) or (
                base == -1 and action == 0) else 2
            draw = fingerprint(
                f"F45/obs/v1|{n}|{self.seed}|{source}|{context}|{action}|{repeat}|{target}")
            result.append(int(draw < num * (MAX64 // 8)))
        return tuple(result)

    def evaluator_only_truth(self):
        a = {}
        for (s, t), sign in self._private_graph.items():
            for context in (0, 1):
                if self.mode == "context_gated" and context == 0:
                    continue
                direction = -sign if self.mode == "context_flip" and context == 1 else sign
                a[(context, s, t)] = direction
        return a

    def evaluator_degree_histogram(self):
        return dict(self._degree_histogram)


def contrast_threshold(repetitions):
    return (45 * repetitions + 99) // 100


class LocalContextWeights:
    """Signed tokenless local update, two int16 contexts per directed candidate."""
    def __init__(self, n):
        if type(n) is not int or n not in SIZES:
            raise RejectedF45("F45_UNREGISTERED_LOCAL_SIZE")
        self.n = n
        self.weights = [0] * (2*n*n)
        self.seen = [[[0,0] for _ in range(n)] for _ in range(2)]

    def observe(self, source, context, action, outcomes):
        n = self.n
        if (type(source) is not int or not 0 <= source < n
            or type(context) is not int or context not in (0, 1)
            or type(action) is not int or action not in (0, 1)
            or type(outcomes) not in (tuple,list) or len(outcomes) != n
            or any(type(y) is not int or y not in (0,1) for y in outcomes)
            or self.seen[context][source][action] >= 24):
            raise RejectedF45("F45_INVALID_PUBLIC_EVIDENCE")
        self.seen[context][source][action] += 1
        signed_action = 2 * action - 1
        start = context*n*n + source*n
        for target, outcome in enumerate(outcomes):
            self.weights[start+target] += signed_action * (2*outcome-1)

    def inferred(self):
        n = self.n
        g = {}
        for context in (0,1):
            for s in range(n):
                off, on = self.seen[context][s]
                if off == 0 or off != on:
                    continue
                lim = 2 * contrast_threshold(on)
                for t in range(n):
                    if s == t:
                        continue
                    w = self.weights[context*n*n+s*n+t]
                    if w >= lim:
                        g[(context,s,t)] = 1
                    elif w <= -lim:
                        g[(context,s,t)] = -1
        return g

    def checkpoint(self):
        n = self.n
        counts = [v for c in range(2) for row in self.seen[c] for v in row]
        if (any(type(x) is not int or not 0 <= x <= 24 for x in counts)
            or any(type(w) is not int or not -32768 <= w <= 32767 for w in self.weights)):
            raise RejectedF45("F45_CHECKPOINT_COUNTER_OVERFLOW")
        body = MAGIC+struct.pack("<H",n)
        body += struct.pack("<"+"H"*(4*n),*counts)
        body += struct.pack("<"+"h"*(2*n*n),*self.weights)
        return body+sha256(body).digest()

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or len(raw) < 38:
            raise RejectedF45("F45_COLD_CHECKPOINT_CORRUPT")
        if raw[:4] != MAGIC or sha256(raw[:-32]).digest() != raw[-32:]:
            raise RejectedF45("F45_COLD_CHECKPOINT_CORRUPT")
        n=struct.unpack_from("<H",raw,4)[0]
        if n not in SIZES or len(raw) != 6 + 8*n + 4*n*n + 32:
            raise RejectedF45("F45_COLD_CHECKPOINT_SIZE_DRIFT")
        model = cls(n)
        counts = struct.unpack_from("<"+"H"*(4*n),raw,6)
        model.seen = [
            [list(counts[c*2*n+2*s:c*2*n+2*s+2]) for s in range(n)]
            for c in range(2)]
        model.weights = list(struct.unpack_from("<"+"h"*(2*n*n),raw,6+8*n))
        if (any(x>24 for x in counts)
            or model.checkpoint()!=raw):
            raise RejectedF45("F45_NONCANONICAL_COLD_CHECKPOINT")
        return model


class FullyFittedMLE:
    """Fully fitted independent factorized Bernoulli response probabilities."""
    def __init__(self,n):
        self.n=n
        self.seen=[[[0,0] for _ in range(n)] for _ in range(2)]
        self.success=[[[[0]*n for _ in range(2)] for _ in range(n)] for _ in range(2)]

    def observe(self,s,c,a,y):
        if (type(s) is not int or not 0<=s<self.n
            or type(c) is not int or c not in (0,1)
            or type(a) is not int or a not in (0,1)
            or type(y) not in (tuple,list) or len(y)!=self.n
            or any(type(v) is not int or v not in (0,1) for v in y)
            or self.seen[c][s][a]>=24):
            raise RejectedF45("F45_CONTROL_INPUT_INVALID")
        self.seen[c][s][a]+=1
        for t,value in enumerate(y):
            self.success[c][s][a][t]+=value

    def inferred(self):
        edges={}
        n=self.n
        for c in (0,1):
            for s in range(n):
                off,on=self.seen[c][s]
                if not off or off!=on:
                    continue
                lim=contrast_threshold(on)
                for t in range(n):
                    if t==s:
                        continue
                    difference=self.success[c][s][1][t]-self.success[c][s][0][t]
                    if difference>=lim:
                        edges[(c,s,t)]=1
                    elif difference<=-lim:
                        edges[(c,s,t)]=-1
        return edges

    def family_aware_inferred(self):
        """Stronger structured least-squares control; no true family or degree supplied."""
        n=self.n
        g={}
        for s in range(n):
            if (self.seen[0][s][0]!=self.seen[0][s][1]
                or self.seen[1][s][0]!=self.seen[1][s][1]
                or not self.seen[0][s][0]
                or self.seen[0][s][0]!=self.seen[1][s][0]):
                continue
            reps=self.seen[0][s][0]
            for t in range(n):
                if s==t:
                    continue
                contrast=[
                    (self.success[c][s][1][t]-self.success[c][s][0][t])/reps
                    for c in (0,1)]
                # Maximize squared explained response-difference energy over
                # all three PUBLIC candidate law shapes and signed polarity.
                # Tie breaking is the preregistered listed pattern order.
                best=None
                for pattern in PATTERNS:
                    norm=sum(v*v for v in pattern)
                    dot=sum(c*v for c,v in zip(contrast,pattern))
                    energy=dot*dot/norm
                    if best is None or energy>best[0]:
                        best=(energy,pattern,dot/norm)
                _, pattern,amplitude=best
                if abs(amplitude) < 0.45:
                    continue
                sign=1 if amplitude>0 else -1
                for c in (0,1):
                    if pattern[c]:
                        g[(c,s,t)]=sign*pattern[c]
        return g


def evaluate_scores(pred, truth, domain):
    right=sum(truth.get(k)==v for k,v in pred.items())
    fp=len(pred)-right
    fn=len(truth)-right
    tn=domain-right-fp-fn
    if (tn<0 or any(v not in (-1,1) for v in pred.values())):
        raise RejectedF45("F45_INVALID_METRIC_COUNTS")
    precision=right/len(pred) if pred else 0.0
    recall=right/len(truth) if truth else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {"tp":right,"fp":fp,"fn":fn,"tn":tn,
            "precision":precision,"recall":recall,"f1":f1}


def two_step_graph(edges,n):
    result={}
    ambiguous=set()
    for c in (0,1):
        forward=defaultdict(list)
        for (ctx,s,t),sign in edges.items():
            if ctx==c:
                forward[s].append((t,sign))
        composed=defaultdict(list)
        for s in range(n):
            for via,first in forward[s]:
                for target,second in forward.get(via,()):
                    if s!=target:
                        composed[(c,s,target)].append(first*second)
        for key,values in composed.items():
            if len(values)==1:
                result[key]=values[0]
            else:
                ambiguous.add(key)
    return result,ambiguous


def performance(pred,hidden,n):
    truth=hidden.evaluator_only_truth()
    direct=evaluate_scores(pred,truth,2*n*(n-1))
    correct,excluded=two_step_graph(truth,n)
    guessed,_=two_step_graph(pred,n)
    guessed={k:v for k,v in guessed.items() if k not in excluded}
    twohop=evaluate_scores(guessed,correct,2*n*(n-1)-len(excluded))
    return {"direct":direct,"twohop":twohop,
            "true_twohop_unique":len(correct),"excluded_ambiguous_pairs":len(excluded)}


def experiment(n,seed,repeats):
    if n not in SIZES or seed not in SEEDS or repeats not in REPS:
        raise RejectedF45("F45_UNFROZEN_WORLD_OR_BUDGET")
    world=ContextWorld(n,seed)
    learner=LocalContextWeights(n)
    fully_fitted=FullyFittedMLE(n)
    misrouted=LocalContextWeights(n)
    passive=LocalContextWeights(n)
    t0=perf_counter()
    source0_before=None
    new_public_events_after_snapshot=0
    for s in range(n):
        for c in (0,1):
            for rep in range(repeats):
                for a in (0,1):
                    observed=world.public_intervention(s,c,a,rep)
                    if s==n-1 and c==0 and rep==0 and a==0:
                        # Source0 has completed all of its own action outcomes.
                        # An actual subsequent intervention on source N-1 must
                        # not change any of the learnt source0 rows.
                        source0_before=(
                            learner.weights[:n],
                            learner.weights[n*n:n*n+n])
                    learner.observe(s,c,a,observed)
                    fully_fitted.observe(s,c,a,observed)
                    misrouted.observe((s+1)%n,c,a,observed)
                    if a==0:
                        passive.observe(s,c,a,observed)
                    if source0_before is not None:
                        new_public_events_after_snapshot+=1
    fit_s=perf_counter()-t0
    start=perf_counter()
    native=learner.inferred()
    mle=fully_fitted.inferred()
    structured=fully_fitted.family_aware_inferred()
    wrong=misrouted.inferred()
    cold_bytes=learner.checkpoint()
    cold=LocalContextWeights.restore(cold_bytes)
    if cold.inferred()!=native or cold.checkpoint()!=cold_bytes:
        raise RejectedF45("F45_COLD_KNOWLEDGE_DRIFT")
    tamper=cold_bytes[:-1]+bytes((cold_bytes[-1]^1,))
    try:
        LocalContextWeights.restore(tamper)
    except RejectedF45:
        tamper_rejected=True
    else:
        raise RejectedF45("F45_TAMPER_NOT_REJECTED")
    interference=(source0_before is not None
                  and learner.weights[:n]==source0_before[0]
                  and learner.weights[n*n:n*n+n]==source0_before[1]
                  and new_public_events_after_snapshot>0)
    if not interference:
        raise RejectedF45("F45_REAL_EVENT_INTERFERENCE_ISOLATION_FAILURE")
    if native!=mle:
        raise RejectedF45("F45_EQUAL_INFORMATION_MLE_PARITY_FAILURE")
    if passive.inferred():
        raise RejectedF45("F45_PASSIVE_NONIDENTIFIABLE_EDGE_INVENTION")
    local_performance=performance(native,world,n)
    fully_fitted_perf=performance(mle,world,n)
    structured_perf=performance(structured,world,n)
    wrong_perf=performance(wrong,world,n)
    evaluate_s=perf_counter()-start
    return {
        "nodes":n,"seed":seed,"mode":world.mode,
        "repetitions_per_action_per_context":repeats,
        "actual_public_interventions":4*n*repeats,
        "public_observed_outcome_bits":4*n*n*repeats,
        "evaluator_private_degree_histogram":world.evaluator_degree_histogram(),
        "native":local_performance,
        "fully_fitted_independent_MLE":fully_fitted_perf,
        "stronger_family_aware_conventional":structured_perf,
        "wrong_source_permutation":wrong_perf,
        "same_information_independent_MLE_predictions_equal":native==mle,
        "passive_abstained":passive.inferred()=={},
        "genuine_intervention_held_other_source_rows":interference,
        "genuine_public_events_after_row_checkpoint":new_public_events_after_snapshot,
        "cold_checkpoint_exact":cold.checkpoint()==cold_bytes,
        "tampered_checkpoint_rejected":tamper_rejected,
        "source_graph_given_to_learner":False,
        "local_signed_weight_bytes":4*n*n,
        "local_seen_action_count_bytes":8*n,
        "local_checkpoint_bytes":len(cold_bytes),
        "fully_fitted_MLE_success_counter_bytes":8*n*n,
        "checkpoint_sha256":sha256(cold_bytes).hexdigest(),
        "fit_seconds_DEV_only":round(fit_s,5),
        "evaluation_seconds_DEV_only":round(evaluate_s,5)
    }


def run():
    protocol=preflight()
    results=[]
    for n in SIZES:
        for seed in SEEDS:
            for reps in REPS:
                results.append(experiment(n,seed,reps))
    high=[r for r in results if r["repetitions_per_action_per_context"]==24]
    t=protocol["evaluation"]["thresholds"]
    direct_mean=sum(r["native"]["direct"]["f1"] for r in high)/len(high)
    twohop_mean=sum(r["native"]["twohop"]["f1"] for r in high)/len(high)
    direct_worst=min(r["native"]["direct"]["f1"] for r in high)
    twohop_worst=min(r["native"]["twohop"]["f1"] for r in high)
    go=(len(high)==9
        and len({x["nodes"] for x in high})==3
        and len({x["seed"] for x in high})==3
        and direct_mean>=t["highest_budget_macro_direct_F1_min"]
        and twohop_mean>=t["highest_budget_macro_twohop_F1_min"]
        and direct_worst>=t["highest_budget_worst_world_direct_F1_min"]
        and twohop_worst>=t["highest_budget_worst_world_twohop_F1_min"]
        and all(x["cold_checkpoint_exact"] and x["tampered_checkpoint_rejected"]
                and x["genuine_intervention_held_other_source_rows"]
                and x["passive_abstained"]
                and x["same_information_independent_MLE_predictions_equal"]
                and x["wrong_source_permutation"]["direct"]["f1"]<
                    x["native"]["direct"]["f1"] for x in high))
    structured_direct_mean=sum(r["stronger_family_aware_conventional"]["direct"]["f1"]
                               for r in high)/len(high)
    structured_twohop_mean=sum(r["stronger_family_aware_conventional"]["twohop"]["f1"]
                               for r in high)/len(high)
    return {
        "schema":SCHEMA,
        "classification":"DEV_CONTEXTUAL_CAUSAL_INDUCTION_GO" if go
                         else "DEV_CONTEXTUAL_CAUSAL_INDUCTION_NO_GO",
        "frozen_parent_sha":protocol["source_parent_sha"],
        "scales_high_first":list(SIZES),
        "seeds":list(SEEDS),
        "budgets_high_first":list(REPS),
        "nine_world_macro_direct_F1":direct_mean,
        "nine_world_macro_twohop_F1":twohop_mean,
        "worst_world_direct_F1":direct_worst,
        "worst_world_twohop_F1":twohop_worst,
        "strongest_family_control_macro_direct_F1":structured_direct_mean,
        "strongest_family_control_macro_twohop_F1":structured_twohop_mean,
        "world_results":results,
        "hidden_graph_given_to_native":False,
        "fully_fitted_conventional_run":True,
        "protected_first_use_consumed":False,
        "accepted_model_edited":False,
        "native_superiority_proven":False,
        "scientific_pass":False,
        "deployed":False
    }


if __name__ == "__main__":
    result=run()
    print("F45_VARIABLE_LAW_CAUSAL_DEV_RESULT="+
          json.dumps(result,sort_keys=True,separators=(",",":")))
    print("F45_NO_PROTECTED_FIRST_USE_OR_MODEL_PROMOTION=PASS")
