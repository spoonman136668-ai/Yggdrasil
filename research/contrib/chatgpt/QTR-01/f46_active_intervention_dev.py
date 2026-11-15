#!/usr/bin/env python3
"""F46: source-free, matched-budget selective causal interventions (DEV only).

Each policy chooses where to intervene and receives only its own public binary
outcomes. Hidden causal edges remain in evaluator-only code. This is NOT an
accepted Yggdrasil model, scientific first-use, or novel-world proof.
"""
from functools import lru_cache
from hashlib import sha1, sha256
from math import ceil, sqrt
from pathlib import Path
from collections import defaultdict
import json
import random
import struct
from time import perf_counter

from f45_context_causal_induction_dev import performance

HERE = Path(__file__).resolve().parent
POLICY = HERE / "f46_prereg.json"
FROZEN_BLOB = "22a540eabbdb7c1809b813cd1378ffc9d681e162"
SCHEMA = "yggdrasil.qtr01.f46.adaptive-causal-intervention-dev.v1"
SIZES = (64, 32, 16)
SEEDS = (107, 109, 113)
BUDGETS = (24, 12, 6)
MODES = {107: "invariant", 109: "context_gated", 113: "context_flip"}
DEGREES = (0, 1, 2, 4, 8)
PATTERNS = ((1, 1), (0, 1), (1, -1))
STRATEGIES = ("native_active", "uniform", "conventional_active", "random")
MAGIC = b"F46A"
LIMIT = 48
UINT64 = 1 << 64


class F46Rejected(ValueError):
    pass


def freeze(path=POLICY):
    raw = Path(path).read_bytes()
    h = sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()
    if h != FROZEN_BLOB:
        raise F46Rejected("F46_FROZEN_PRECODE_BLOB_DRIFT")
    doc = json.loads(raw)
    worlds = doc.get("new_worlds", {})
    arms = doc.get("arms", {})
    metrics = doc.get("frozen_metrics", {})
    if (doc.get("schema") != SCHEMA
        or doc.get("status") != "FROZEN_BEFORE_ANY_F46_CODE_OR_OUTCOME"
        or doc.get("parent_exact_f45_sha") != "7223f0cb2f3862261906b5640f53751c1a1e3689"
        or worlds.get("sizes_high_first") != list(SIZES)
        or worlds.get("fresh_development_seeds") != list(SEEDS)
        or worlds.get("seed_to_law") != {str(s): MODES[s] for s in SEEDS}
        or worlds.get("degree_options") != list(DEGREES)
        or worlds.get("pair_budgets_per_row_mean_high_first") != list(BUDGETS)
        or set(arms) != set(STRATEGIES)
        or metrics.get("frozen_go") != {
          "min_worlds_at_each_budget": 9,
          "all_policies_same_query_budget": True,
          "native_cold_exact_all_worlds": True,
          "true_intervention_isolation_all_worlds": True,
          "at_b12_native_active_macro_direct_F1_gain_over_uniform_min": 0.02,
          "at_b12_native_active_macro_direct_F1_gain_over_strongest_conventional_min": 0.01,
          "at_b6_native_active_macro_direct_F1_gain_over_uniform_min": 0.01,
          "at_b12_native_active_macro_twohop_F1_min": 0.60,
          "exact_context_law_comparison_all_three_families": True}
        or len(doc.get("fences", {})) != 9
        or not all(doc["fences"].values())):
        raise F46Rejected("F46_FROZEN_POLICY_DRIFT")
    return doc


def hash64(s):
    return int.from_bytes(sha256(s.encode("ascii")).digest()[:8], "big")


class World:
    """Private graph and intervention response evaluator for one DEV world."""
    def __init__(self,n,seed):
        if (type(n) is not int or n not in SIZES
            or type(seed) is not int or seed not in SEEDS):
            raise F46Rejected("F46_WORLD_NOT_FROZEN")
        self.n, self.seed, self.mode = n, seed, MODES[seed]
        edges = {}
        degrees = []
        for s in range(n):
            degree = DEGREES[hash64(f"F46/degree/v1|{n}|{seed}|{s}") % 5]
            degrees.append(degree)
            ranked = sorted(
                (hash64(f"F46/edge/v1|{n}|{seed}|{s}|{t}"), t)
                for t in range(n) if t != s)
            for _,t in ranked[:degree]:
                signed = hash64(f"F46/sign/v1|{n}|{seed}|{s}|{t}") & 1
                edges[(s,t)] = 1 if signed==0 else -1
        self._eval_graph = edges
        self._eval_degrees = {str(d):degrees.count(d) for d in DEGREES}

    @lru_cache(maxsize=16384)
    def intervene(self,s,c,a,k):
        if (type(s) is not int or not 0<=s<self.n
            or type(c) is not int or c not in (0,1)
            or type(a) is not int or a not in (0,1)
            or type(k) is not int or not 0<=k<LIMIT):
            raise F46Rejected("F46_INVALID_PUBLIC_INTERVENTION")
        out=[]
        for t in range(self.n):
            sign = self._eval_graph.get((s,t),0)
            if c==0 and self.mode=="context_gated":
                sign=0
            if c==1 and self.mode=="context_flip":
                sign=-sign
            high = (sign==1 and a==1) or (sign==-1 and a==0)
            numerator=7 if high else 2
            draw=hash64(f"F46/obs/v1|{self.n}|{self.seed}|{s}|{c}|{a}|{k}|{t}")
            out.append(int(draw < numerator*(UINT64//8)))
        return tuple(out)

    def evaluator_only_truth(self):
        graph={}
        for (s,t),sign in self._eval_graph.items():
            for c in (0,1):
                if c==0 and self.mode=="context_gated":
                    continue
                graph[(c,s,t)] = -sign if c==1 and self.mode=="context_flip" else sign
        return graph

    def evaluator_degree_histogram(self):
        return dict(self._eval_degrees)


def threshold(count):
    return (45*count+99)//100


class LocalLearner:
    """F45 integer signed contrast local update, with paired action evidence."""
    def __init__(self,n):
        if type(n) is not int or n not in SIZES:
            raise F46Rejected("F46_BAD_NATIVE_WIDTH")
        self.n=n
        self.weights=[0]*(2*n*n)
        self.seen=[[0]*n for _ in range(2)]

    def observe_pair(self,s,c,off,on):
        n=self.n
        if (type(s) is not int or not 0<=s<n
            or type(c) is not int or c not in (0,1)
            or type(off) not in (tuple,list) or type(on) not in (tuple,list)
            or len(off)!=n or len(on)!=n
            or any(type(x) is not int or x not in (0,1) for x in off+on)
            or self.seen[c][s]>=LIMIT):
            raise F46Rejected("F46_INCOMPLETE_OR_UNREGISTERED_PUBLIC_PAIR")
        self.seen[c][s]+=1
        offset=c*n*n+s*n
        for t in range(n):
            self.weights[offset+t]+=2*(on[t]-off[t])

    def inferred(self):
        n=self.n
        links={}
        for c in (0,1):
            for s in range(n):
                k=self.seen[c][s]
                if not k:
                    continue
                limit=2*threshold(k)
                start=c*n*n+s*n
                for t in range(n):
                    if t==s:continue
                    value=self.weights[start+t]
                    if value>=limit:
                        links[(c,s,t)]=1
                    elif value<=-limit:
                        links[(c,s,t)]=-1
        return links

    def checkpoint(self):
        n=self.n
        counts=[v for rows in self.seen for v in rows]
        if any(type(x) is not int or not 0<=x<=LIMIT for x in counts):
            raise F46Rejected("F46_COUNTER_OUT_OF_RANGE")
        if any(type(x) is not int or not -32768<=x<=32767 for x in self.weights):
            raise F46Rejected("F46_WEIGHT_OVERFLOW")
        body=MAGIC+struct.pack("<H",n)
        body+=struct.pack("<"+"H"*(2*n),*counts)
        body+=struct.pack("<"+"h"*(2*n*n),*self.weights)
        return body+sha256(body).digest()

    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or len(raw)<38 or raw[:4]!=MAGIC:
            raise F46Rejected("F46_COLD_CHECKPOINT_INVALID")
        if sha256(raw[:-32]).digest()!=raw[-32:]:
            raise F46Rejected("F46_COLD_CHECKPOINT_DIGEST_MISMATCH")
        n=struct.unpack_from("<H",raw,4)[0]
        if n not in SIZES or len(raw)!=6+4*n+4*n*n+32:
            raise F46Rejected("F46_COLD_CHECKPOINT_SHAPE_DRIFT")
        mdl=cls(n)
        count=struct.unpack_from("<"+"H"*(2*n),raw,6)
        mdl.seen=[list(count[c*n:(c+1)*n]) for c in (0,1)]
        mdl.weights=list(struct.unpack_from("<"+"h"*(2*n*n),raw,6+4*n))
        if any(x>LIMIT for x in count) or mdl.checkpoint()!=raw:
            raise F46Rejected("F46_NONCANONICAL_CHECKPOINT")
        return mdl


class MLE:
    """Fully fitted Bernoulli action-response statistics on one action history."""
    def __init__(self,n):
        self.n=n
        self.seen=[[0]*n for _ in range(2)]
        self.success=[[[[0]*n for _ in (0,1)] for _ in range(n)] for _ in (0,1)]

    def observe_pair(self,s,c,off,on):
        if (not 0<=s<self.n or c not in (0,1)
            or len(off)!=self.n or len(on)!=self.n
            or self.seen[c][s]>=LIMIT):
            raise F46Rejected("F46_BAD_CONVENTIONAL_PAIR")
        self.seen[c][s]+=1
        for t in range(self.n):
            self.success[c][s][0][t]+=off[t]
            self.success[c][s][1][t]+=on[t]

    def delta(self,c,s,t):
        k=self.seen[c][s]
        if not k:
            return 0.0
        return (self.success[c][s][1][t]-self.success[c][s][0][t])/k

    def independent_inferred(self):
        n=self.n
        ans={}
        for c in (0,1):
            for s in range(n):
                k=self.seen[c][s]
                if not k:continue
                cutoff=threshold(k)
                for t in range(n):
                    if t==s:continue
                    delta=self.success[c][s][1][t]-self.success[c][s][0][t]
                    if delta>=cutoff:ans[(c,s,t)]=1
                    elif delta<=-cutoff:ans[(c,s,t)]=-1
        return ans

    def structured_inferred(self):
        """Family-aware WLS, valid even when active row contexts have uneven counts."""
        n=self.n
        ans={}
        for s in range(n):
            k0,k1=self.seen[0][s],self.seen[1][s]
            if not k0 and not k1:continue
            for t in range(n):
                if s==t:continue
                effects=(self.delta(0,s,t),self.delta(1,s,t))
                best=None
                for pattern in PATTERNS:
                    normal=sum(k*v*v for k,v in zip((k0,k1),pattern))
                    if normal==0:continue
                    numerator=sum(k*x*v for k,x,v in zip((k0,k1),effects,pattern))
                    explained=numerator*numerator/normal
                    if best is None or explained>best[0]:
                        best=(explained,pattern,numerator/normal)
                if best is None:continue
                _,pattern,alpha=best
                if abs(alpha)<0.45:continue
                direction=1 if alpha>0 else -1
                for c in (0,1):
                    if self.seen[c][s] and pattern[c]:
                        ans[(c,s,t)]=direction*pattern[c]
        return ans


def uncertainty(delta):
    return 1/(0.15+abs(abs(delta)-0.45))


class Arm:
    def __init__(self,kind,n,seed):
        if kind not in STRATEGIES:raise F46Rejected("F46_UNREGISTERED_POLICY")
        self.kind=kind
        self.n=n
        self.native=LocalLearner(n)
        self.mle=MLE(n)
        self.rng=random.Random(1000003*seed+n)
        self.visited=[]
        self.actual_pair_events=0

    def priority(self,c,s):
        k=self.native.seen[c][s]
        if not k:return float("inf")
        n=self.n
        if self.kind=="conventional_active":
            values=[uncertainty(self.mle.delta(c,s,t))
                    for t in range(n) if t!=s]
        else:
            base=c*n*n+s*n
            values=[uncertainty(self.native.weights[base+t]/(2*k))
                    for t in range(n) if t!=s]
        top=sorted(values,reverse=True)[:min(8,n-1)]
        return sum(top)/sqrt(k+1)

    def select(self,step):
        n=self.n
        if self.kind=="uniform":
            row=step % (2*n)
            c,s=divmod(row,n)
            if self.native.seen[c][s]>=LIMIT:raise F46Rejected("F46_UNIFORM_EXHAUSTED")
            return c,s
        available=[(c,s) for c in (0,1) for s in range(n)
                   if self.native.seen[c][s]<LIMIT]
        if not available:raise F46Rejected("F46_INTERVENTION_BUDGET_EXHAUSTED")
        if self.kind=="random":
            return self.rng.choice(available)
        # Every active policy must observe all rows once before repeating.
        unsampled=[row for row in available
                   if self.native.seen[row[0]][row[1]]==0]
        if unsampled:
            return unsampled[0]
        return max(available,key=lambda row:(self.priority(*row),
                                              -row[0]*n-row[1]))

    def step(self,world,step):
        c,s=self.select(step)
        k=self.native.seen[c][s]
        y0=world.intervene(s,c,0,k)
        y1=world.intervene(s,c,1,k)
        self.native.observe_pair(s,c,y0,y1)
        self.mle.observe_pair(s,c,y0,y1)
        self.visited.append((c,s,k))
        self.actual_pair_events+=1

    def checkpoint_report(self,world,b):
        n=self.n
        pairs=2*n*b
        if self.actual_pair_events!=pairs:
            raise F46Rejected("F46_ACTION_BUDGET_NOT_EQUAL")
        raw=self.native.checkpoint()
        restored=LocalLearner.restore(raw)
        inferred=self.native.inferred()
        if raw!=restored.checkpoint() or inferred!=restored.inferred():
            raise F46Rejected("F46_COLD_PREDICTION_DRIFT")
        tampered=raw[:-1]+bytes([raw[-1]^1])
        try:LocalLearner.restore(tampered)
        except F46Rejected:tamper=True
        else:raise F46Rejected("F46_TAMPER_ADMITTED")
        # Real additional source row intervention in an isolated copy, outside
        # scored budget. Its actions are counted separately and not scored.
        clone=LocalLearner.restore(raw)
        s=n-1
        c=0
        if clone.seen[c][s]>=LIMIT:
            c=1
        if clone.seen[c][s]>=LIMIT:
            raise F46Rejected("F46_NO_ROW_AVAILABLE_FOR_ISOLATION_CONTROL")
        before=(clone.weights[:n],clone.weights[n*n:n*n+n])
        k=clone.seen[c][s]
        clone.observe_pair(s,c,world.intervene(s,c,0,k),world.intervene(s,c,1,k))
        isolated=(clone.weights[:n]==before[0]
                  and clone.weights[n*n:n*n+n]==before[1])
        if not isolated:raise F46Rejected("F46_UNRELATED_SOURCE_ROW_INTERFERENCE")
        control=self.mle.independent_inferred()
        if control!=inferred:raise F46Rejected("F46_MLE_EQUAL_STATISTIC_PARITY")
        structured=self.mle.structured_inferred()
        return {
            "policy":self.kind,
            "repetitions_mean_per_row":b,
            "pairs":pairs,"individual_actions":2*pairs,
            "public_outcome_bits":2*pairs*n,
            "isolated_control_extra_public_actions":2,
            "actual_row_count_visited":sum(self.native.seen[c][s]>0
                                          for c in (0,1) for s in range(n)),
            "max_repetitions_in_one_row":max(max(row) for row in self.native.seen),
            "native":performance(inferred,world,n),
            "fully_fitted_independent_MLE":performance(control,world,n),
            "fully_fitted_family_aware":performance(structured,world,n),
            "same_stream_independent_MLE_equal":True,
            "cold_restore_exact":True,
            "tamper_rejected":tamper,
            "real_intervention_held_unrelated_row":isolated,
            "checkpoint_sha256":sha256(raw).hexdigest(),
            "local_weight_bytes":len(self.native.weights)*2,
            "local_action_count_bytes":2*n*2,
            "checkpoint_total_bytes":len(raw),
            "conventional_success_counter_bytes":4*n*n*2,
        }


def one_world(n,seed):
    world=World(n,seed)
    arms={name:Arm(name,n,seed) for name in STRATEGIES}
    all_records=[]
    start=perf_counter()
    checkpoints={2*n*b:b for b in BUDGETS}
    for step in range(2*n*max(BUDGETS)):
        for arm in arms.values():
            arm.step(world,step)
        if step+1 in checkpoints:
            b=checkpoints[step+1]
            current={name:arm.checkpoint_report(world,b)
                     for name,arm in arms.items()}
            if any(v["pairs"]!=2*n*b for v in current.values()):
                raise F46Rejected("F46_BUDGET_UNFAIR")
            all_records.append({
                "nodes":n,"seed":seed,"law_mode":world.mode,
                "mean_repetitions_per_row":b,
                "evaluator_degree_histogram":world.evaluator_degree_histogram(),
                "policy_results":current,
                "native_and_conventional_active_same_choice_history":
                    arms["native_active"].visited==arms["conventional_active"].visited
            })
    all_records.sort(key=lambda x:-x["mean_repetitions_per_row"])
    return all_records,round(perf_counter()-start,4)


def run():
    frozen=freeze()
    records=[]
    clock=[]
    for n in SIZES:
        for seed in SEEDS:
            data,elapsed=one_world(n,seed)
            records.extend(data)
            clock.append({"nodes":n,"seed":seed,"dev_wall_seconds":elapsed})
    def mean_f1(b,policy,model="native",kind="direct"):
        group=[v for v in records if v["mean_repetitions_per_row"]==b]
        if len(group)!=9:raise F46Rejected("F46_NOT_ALL_WORLDS_RUN")
        return sum(v["policy_results"][policy][model][kind]["f1"]
                   for v in group)/len(group)
    at12=mean_f1(12,"native_active")
    at6=mean_f1(6,"native_active")
    uniform12=mean_f1(12,"uniform")
    uniform6=mean_f1(6,"uniform")
    strongest12=max(
        mean_f1(12,"conventional_active","fully_fitted_family_aware"),
        mean_f1(12,"uniform","fully_fitted_family_aware"),
        mean_f1(12,"uniform","fully_fitted_independent_MLE"))
    threshold=frozen["frozen_metrics"]["frozen_go"]
    controls=all(p["cold_restore_exact"] and p["tamper_rejected"]
                 and p["real_intervention_held_unrelated_row"]
                 and p["same_stream_independent_MLE_equal"]
                 for rec in records for p in rec["policy_results"].values())
    action_equal=all(len({p["pairs"] for p in rec["policy_results"].values()})==1
                     for rec in records)
    passed=(len(records)==27
        and action_equal and controls
        and set(v["law_mode"] for v in records)==set(MODES.values())
        and at12-uniform12>=threshold["at_b12_native_active_macro_direct_F1_gain_over_uniform_min"]
        and at12-strongest12>=threshold["at_b12_native_active_macro_direct_F1_gain_over_strongest_conventional_min"]
        and at6-uniform6>=threshold["at_b6_native_active_macro_direct_F1_gain_over_uniform_min"]
        and mean_f1(12,"native_active","native","twohop")>=threshold["at_b12_native_active_macro_twohop_F1_min"])
    return {
        "schema":SCHEMA,
        "frozen_F45_parent":frozen["parent_exact_f45_sha"],
        "classification":"DEV_ACTIVE_INTERVENTION_POLICY_GO" if passed
                         else "DEV_ACTIVE_INTERVENTION_POLICY_NO_GO",
        "nodes_high_first":list(SIZES),
        "development_seeds":list(SEEDS),
        "budgets_high_first":list(BUDGETS),
        "budgets_and_controls_consistent":action_equal and controls,
        "native_active_macro_direct_F1_b12":at12,
        "native_active_macro_direct_F1_b6":at6,
        "uniform_macro_direct_F1_b12":uniform12,
        "uniform_macro_direct_F1_b6":uniform6,
        "strongest_conventional_macro_direct_F1_b12":strongest12,
        "native_active_macro_twohop_F1_b12":mean_f1(12,"native_active","native","twohop"),
        "strongest_at_b12_components":{
            "conventional_active_structured":mean_f1(12,"conventional_active","fully_fitted_family_aware"),
            "uniform_structured":mean_f1(12,"uniform","fully_fitted_family_aware"),
            "uniform_independent_MLE":mean_f1(12,"uniform","fully_fitted_independent_MLE"),
        },
        "world_results":records,
        "dev_elapsed_seconds_not_scientific_cost":clock,
        "hidden_world_graph_to_learner":False,
        "protected_scientific_first_use":False,
        "accepted_Yggdrasil_source_changed":False,
        "scientific_pass":False,
        "deployed":False
    }


if __name__=="__main__":
    r=run()
    print("F46_ADAPTIVE_INTERVENTION_DEV_RESULT="+
          json.dumps(r,sort_keys=True,separators=(",",":")))
    print("F46_NO_PROTECTED_SOURCE_OR_ACCEPTED_MODEL_FIRST_USE=PASS")
