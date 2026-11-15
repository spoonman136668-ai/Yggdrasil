#!/usr/bin/env python3
"""F48: consequential two-layer Boolean intervention tournaments, DEV only.

No source documents or accepted Yggdrasil native model weights are touched.
Hidden target-law ID is evaluator-only; all arms know the same candidate pool.
"""
from functools import lru_cache
from hashlib import sha1, sha256
from math import log2
from pathlib import Path
from time import perf_counter
import json
import random
import struct

HERE = Path(__file__).resolve().parent
PREREG = HERE / "f48_prereg.json"
FROZEN_BLOB = "3ed03d9b6a65e48b4e7c85dcb7ed044503487e14"
SCHEMA = "yggdrasil.qtr01.f48.counterfactual-witness-vs-bayesian-active-dev.v1"
HYPOTHESES = (256, 128, 64)
SEEDS = (149, 151, 157)
BUDGETS = (32, 16, 8)
POLICIES = ("native_witness", "bayes_information_gain", "uniform", "random")
MAGIC = b"F48A"
N_ACTIONS = 256
MAX_QUERY = 32
CONTROL_EXTRA_LIMIT = 1
TWO64 = 1 << 64


class F48Rejected(ValueError):
    pass


def freeze(path=PREREG):
    raw = Path(path).read_bytes()
    blob = sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()
    if blob != FROZEN_BLOB:
        raise F48Rejected("F48_FROZEN_PREREG_BLOB_CHANGED")
    p = json.loads(raw)
    w = p.get("worlds", {})
    arm = p.get("arms", {})
    score = p.get("frozen_metrics", {}).get("positive_criteria", {})
    if (p.get("schema") != SCHEMA
        or p.get("status") != "FROZEN_PRE_CODE_PRE_WORLD_OUTCOMES"
        or p.get("source_parent") != "5d9f930317905e61751ebff62e1b650dcb234011"
        or w.get("hypothesis_counts_high_first") != list(HYPOTHESES)
        or w.get("fixed_development_seeds") != list(SEEDS)
        or w.get("action_space_size") != N_ACTIONS
        or w.get("budgets_high_first") != list(BUDGETS)
        or set(arm) != set(POLICIES)
        or score != {
            "nine_worlds_required": True,
            "cold_restore_identical_all": True,
            "invalid_query_and_corruption_rejected": True,
            "real_extra_public_observation_other_hypothesis_weight_isolation": True,
            "b16_native_unseen_accuracy_gain_vs_bayes_min": 0.03,
            "b8_native_unseen_accuracy_gain_vs_uniform_min": 0.04,
            "b16_native_prediction_accesses_fraction_of_bayes_max": 0.50}
        or len(p.get("safety", {})) != 9
        or not all(v is True for v in p["safety"].values())):
        raise F48Rejected("F48_PROTOCOL_POLICY_DRIFT")
    return p


def hash64(data):
    return int.from_bytes(sha256(data.encode("ascii")).digest()[:8], "big")


@lru_cache(maxsize=256)
def law_params(index):
    if type(index) is not int or not 0 <= index < 256:
        raise F48Rejected("F48_INVALID_CAUSAL_LAW_ID")
    raw = sha256(f"F48/law/v1|{index}".encode("ascii")).digest()
    return (tuple(raw[j] % 8 for j in range(4)),
            tuple(raw[4+j] & 1 for j in range(4)),
            (raw[8] % 3, raw[9] % 3), raw[11] & 1)


def gate(kind, a, b):
    return a & b if kind == 0 else a ^ b if kind == 1 else a | b


def consequence(index, action):
    """Two hidden non-linear causal gates plus an index-encoded direct path.

    The nonlinear contribution is jointly triggered by intervention bits 0,1;
    it vanishes on one-hot interventions, making the 256 candidate truth
    tables provably distinct via their 8 index-selected direct input effects.
    No true law label or hidden graph outcome is made available to learners.
    """
    if type(action) is not int or not 0 <= action < N_ACTIONS:
        raise F48Rejected("F48_INVALID_ACTION")
    parents, polarity, kinds, bias = law_params(index)
    bits = [(action >> k) & 1 for k in range(8)]
    x = [bits[parents[k]] ^ polarity[k] for k in range(4)]
    h0 = gate(kinds[0], x[0], x[1])
    h1 = gate(kinds[1], x[2], x[3])
    # A local causal interaction plus eight possible direct signed pathways.
    return ((index & action).bit_count() & 1) ^ (
        bits[0] & bits[1] & (h0 ^ h1 ^ bias))


@lru_cache(maxsize=3)
def candidate_table(count):
    if type(count) is not int or count not in HYPOTHESES:
        raise F48Rejected("F48_NON_FROZEN_HYPOTHESIS_COUNT")
    tables = tuple(bytes(consequence(h, a) for a in range(N_ACTIONS))
                   for h in range(count))
    if len(set(tables)) != count:
        raise F48Rejected("F48_CANDIDATE_CAUSAL_LAWS_NOT_IDENTIFIABLE")
    return tables


class HiddenWorld:
    """Evaluator-only true-law ID; intervention returns public noisy bit."""
    def __init__(self, count, seed):
        if type(count) is not int or count not in HYPOTHESES or type(seed) is not int or seed not in SEEDS:
            raise F48Rejected("F48_UNREGISTERED_DEVELOPMENT_WORLD")
        self.count, self.seed = count, seed
        self._tables = candidate_table(count)
        self._hidden = hash64(f"F48/true/v1|{count}|{seed}") % count

    def intervene(self, action, replicate):
        if (type(action) is not int or not 0 <= action < N_ACTIONS
            or type(replicate) is not int or not 0 <= replicate < MAX_QUERY + CONTROL_EXTRA_LIMIT):
            raise F48Rejected("F48_PUBLIC_INTERVENTION_OUT_OF_SCOPE")
        clean = self._tables[self._hidden][action]
        flipped = hash64(f"F48/obs/v1|{self.count}|{self.seed}|{action}|{replicate}") < TWO64 // 10
        return clean ^ int(flipped)

    def evaluator_truth_only(self):
        return self._hidden, self._tables[self._hidden]


class MismatchWeights:
    """Tokenless local integer mismatch penalties; no gradients."""
    def __init__(self, count):
        self.table = candidate_table(count)
        self.count = count
        self.mismatch = [0]*count
        self.action_seen = [0]*N_ACTIONS
        self.total = 0

    def observe(self, action, outcome):
        if (type(action) is not int or not 0 <= action < N_ACTIONS
            or type(outcome) is not int or outcome not in (0,1)
            or self.action_seen[action] >= MAX_QUERY + CONTROL_EXTRA_LIMIT
            or self.total >= MAX_QUERY + CONTROL_EXTRA_LIMIT):
            raise F48Rejected("F48_UNTRUSTED_OR_EXCESS_OBSERVATION")
        for h, row in enumerate(self.table):
            self.mismatch[h] += int(row[action] != outcome)
        self.action_seen[action] += 1
        self.total += 1

    def map_id(self):
        return min(range(self.count), key=lambda h:(self.mismatch[h],h))

    def weights(self):
        minimum = min(self.mismatch)
        scores = [(1/9) ** (e-minimum) for e in self.mismatch]
        total = sum(scores)
        return [s/total for s in scores]

    def checkpoint(self):
        if (self.total > MAX_QUERY + CONTROL_EXTRA_LIMIT or any(not 0<=v<=self.total for v in self.mismatch)
            or any(not 0<=v<=MAX_QUERY + CONTROL_EXTRA_LIMIT for v in self.action_seen)
            or sum(self.action_seen) != self.total):
            raise F48Rejected("F48_INVALID_COUNTER_STATE")
        body = MAGIC + struct.pack("<HH",self.count,self.total)
        body += struct.pack("<"+"H"*self.count,*self.mismatch)
        body += struct.pack("<"+"H"*N_ACTIONS,*self.action_seen)
        return body + sha256(body).digest()

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or len(raw) < 40 or raw[:4] != MAGIC:
            raise F48Rejected("F48_COLD_CHECKPOINT_REJECTED")
        if sha256(raw[:-32]).digest() != raw[-32:]:
            raise F48Rejected("F48_COLD_CHECKPOINT_REJECTED")
        count,total = struct.unpack_from("<HH",raw,4)
        if (count not in HYPOTHESES or
            len(raw) != 8 + 2*count + 2*N_ACTIONS + 32):
            raise F48Rejected("F48_COLD_CHECKPOINT_SHAPE_INVALID")
        saved = cls(count)
        saved.total = total
        saved.mismatch = list(struct.unpack_from("<"+"H"*count,raw,8))
        saved.action_seen = list(struct.unpack_from("<"+"H"*N_ACTIONS,raw,8+2*count))
        if saved.checkpoint() != raw:
            raise F48Rejected("F48_NONCANONICAL_COLD_CHECKPOINT")
        return saved


class ActiveArm:
    def __init__(self, kind, count, seed):
        if kind not in POLICIES or type(seed) is not int or seed not in SEEDS:
            raise F48Rejected("F48_UNREGISTERED_POLICY")
        self.kind,self.count,self.seed = kind,count,seed
        self.model=MismatchWeights(count)
        self.rng=random.Random(100003*seed+count)
        self.chosen = []
        self.prediction_accesses = 0
        self.selector_seconds = 0.0
        self.total_seconds = 0.0

    def select(self):
        t = self.model.total
        if t >= MAX_QUERY:
            raise F48Rejected("F48_SCORED_ACTION_LIMIT_EXHAUSTED")
        if self.kind == "uniform":
            return (73*t) % N_ACTIONS
        if self.kind == "random":
            return self.rng.randrange(N_ACTIONS)
        table = self.model.table
        if self.kind == "native_witness":
            best_four = sorted(range(self.count),
                               key=lambda h:(self.model.mismatch[h],h))[:4]
            best_a,best_score=0,-1
            for a in range(N_ACTIONS):
                ones = sum(table[h][a] for h in best_four)
                score = ones*(4-ones)
                self.prediction_accesses += 4
                if score > best_score:
                    best_a,best_score = a,score
            return best_a
        # Fully fitted conventional Bayesian expected information gain:
        # H(Y|action) - H(Y|hidden law, action). The second term is fixed
        # H_2(0.1), so maximizing predictive Bernoulli entropy is exact IG.
        # Exact rational posterior: each mismatch multiplies likelihood by
        # 1/9. Therefore P(h) is proportional to 9**(max_mismatch-mismatch[h]).
        # Binary predictive entropy is maximal exactly when weighted positives
        # are closest to half the total. Integer ties are OS-independent.
        top=max(self.model.mismatch)
        posterior=[9**(top-mis) for mis in self.model.mismatch]
        total=sum(posterior)
        best_a,best_distance=0,None
        for a in range(N_ACTIONS):
            positives=sum(posterior[h]*table[h][a] for h in range(self.count))
            self.prediction_accesses += self.count
            distance=abs(total-2*positives)
            if best_distance is None or distance < best_distance:
                best_a,best_distance=a,distance
        return best_a

    def act(self,world):
        start=perf_counter()
        a=self.select()
        self.selector_seconds += perf_counter()-start
        response = world.intervene(a,self.model.action_seen[a])
        self.model.observe(a,response)
        self.chosen.append(a)
        self.total_seconds+=perf_counter()-start
        return (a,response)

    def evaluate(self,world):
        raw = self.model.checkpoint()
        restored = MismatchWeights.restore(raw)
        if restored.checkpoint()!=raw or restored.map_id()!=self.model.map_id():
            raise F48Rejected("F48_COLD_RESTORE_MISMATCH")
        corrupt=raw[:-1]+bytes((raw[-1]^1,))
        try:
            MismatchWeights.restore(corrupt)
        except F48Rejected:
            corrupted_rejected=True
        else:
            raise F48Rejected("F48_CORRUPT_CHECKPOINT_ACCEPTED")
        # One additional *real* public action/outcome event on a separate
        # negative-control clone. Explicitly account for it outside the scored
        # policy's 8/16/32 observations; original weight state is immutable.
        cloned=MismatchWeights.restore(raw)
        actual_a=255
        observed=world.intervene(actual_a,cloned.action_seen[actual_a])
        cloned.observe(actual_a,observed)
        changed=cloned.checkpoint()!=raw and self.model.checkpoint()==raw
        if not changed:
            raise F48Rejected("F48_CLONE_UPDATES_ORIGINAL_MEMORY")
        hidden,true=world.evaluator_truth_only()
        known=set(self.chosen)
        unqueried=[a for a in range(N_ACTIONS) if a not in known]
        if len(unqueried) < N_ACTIONS-MAX_QUERY:
            raise F48Rejected("F48_HELDOUT_EVALUATION_LEAKAGE")
        prediction=self.model.table[self.model.map_id()]
        correct=sum(prediction[a] == true[a] for a in unqueried)
        pw=self.model.weights()
        entropy=round(-sum(p*log2(p) for p in pw if p),10)
        return {
            "arm":self.kind,
            "total_real_action_observations":self.model.total,
            "public_observed_outcome_bits":self.model.total,
            "unqueried_action_count":len(unqueried),
            "heldout_counterfactual_MAP_accuracy":correct/len(unqueried),
            "exact_hidden_law_identified":self.model.map_id()==hidden,
            "posterior_entropy_bits":entropy,
            "local_weight_payload_bytes":2*self.count,
            "public_action_counter_payload_bytes":2*N_ACTIONS,
            "checkpoint_bytes":len(raw),
            "cold_checkpoint_sha256":sha256(raw).hexdigest(),
            "cold_restore_prediction_exact":True,
            "tamper_rejected":corrupted_rejected,
            "isolated_clone_public_update_unchanged_original":changed,
            "isolated_control_extra_public_actions":1,
            "isolated_control_extra_public_outcome_bits":1,
            "candidate_action_prediction_accesses":self.prediction_accesses,
            "selection_seconds_DEV_only":round(self.selector_seconds,6),
            "total_arm_seconds_DEV_only":round(self.total_seconds,6),
        }


def run_one(count,seed):
    world=HiddenWorld(count,seed)
    arms={kind:ActiveArm(kind,count,seed) for kind in POLICIES}
    results=[]
    for step in range(MAX_QUERY):
        for arm in arms.values():
            arm.act(world)
        if step+1 in BUDGETS:
            observations={name:arm.evaluate(world) for name,arm in arms.items()}
            assert all(x["total_real_action_observations"]==step+1
                       for x in observations.values())
            results.append({
                "hypothesis_count":count,"seed":seed,
                "action_budget":step+1,
                "observed_public_outcomes_per_arm":step+1,
                "arms":observations
            })
    return sorted(results,key=lambda d:-d["action_budget"])


def run():
    p=freeze()
    rows=[]
    for h in HYPOTHESES:
        for seed in SEEDS:
            rows.extend(run_one(h,seed))
    def avg(b,arm,key):
        q=[v for v in rows if v["action_budget"]==b]
        if len(q)!=9:
            raise F48Rejected("F48_NINE_WORLD_COMPLETENESS_FAILED")
        return sum(v["arms"][arm][key] for v in q)/len(q)
    native_b16=avg(16,"native_witness","heldout_counterfactual_MAP_accuracy")
    bayes_b16=avg(16,"bayes_information_gain","heldout_counterfactual_MAP_accuracy")
    native_b8=avg(8,"native_witness","heldout_counterfactual_MAP_accuracy")
    uniform_b8=avg(8,"uniform","heldout_counterfactual_MAP_accuracy")
    native_access=avg(16,"native_witness","candidate_action_prediction_accesses")
    bayes_access=avg(16,"bayes_information_gain","candidate_action_prediction_accesses")
    flags=p["frozen_metrics"]["positive_criteria"]
    cold=all(x["cold_restore_prediction_exact"] and x["tamper_rejected"]
             and x["isolated_clone_public_update_unchanged_original"]
             for w in rows for x in w["arms"].values())
    equal=all(len({x["total_real_action_observations"]
                   for x in w["arms"].values()})==1 for w in rows)
    go=(len(rows)==27 and cold and equal
        and native_b16-bayes_b16>=flags["b16_native_unseen_accuracy_gain_vs_bayes_min"]
        and native_b8-uniform_b8>=flags["b8_native_unseen_accuracy_gain_vs_uniform_min"]
        and native_access/bayes_access<=flags["b16_native_prediction_accesses_fraction_of_bayes_max"])
    return {
        "schema":SCHEMA,
        "classification":"DEV_COUNTERFACTUAL_WITNESS_GO" if go
                         else "DEV_COUNTERFACTUAL_WITNESS_NO_GO",
        "hypothesis_counts_high_first":list(HYPOTHESES),
        "seeds":list(SEEDS),"budgets_high_first":list(BUDGETS),
        "native_b16_unseen_accuracy":native_b16,
        "bayes_b16_unseen_accuracy":bayes_b16,
        "native_b8_unseen_accuracy":native_b8,
        "uniform_b8_unseen_accuracy":uniform_b8,
        "native_b16_prediction_accesses":native_access,
        "bayes_b16_prediction_accesses":bayes_access,
        "cold_and_tamper_all":cold,
        "action_budgets_equal":equal,
        "world_results":rows,
        "protected_first_use":False,
        "accepted_native_Yggdrasil_model_edited":False,
        "scientific_pass":False,
        "deployed":False
    }


if __name__ == "__main__":
    result=run()
    print("F48_COUNTERFACTUAL_WITNESS_DEV_RESULT="+
          json.dumps(result,sort_keys=True,separators=(",",":")))
    print("F48_NO_PROTECTED_WORLD_OR_ACCEPTED_MODEL_FIRST_USE=PASS")
