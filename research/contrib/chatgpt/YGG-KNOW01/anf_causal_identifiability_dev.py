"""KNOW24 — source-blinded GF(2) causal hypothesis/active intervention diagnostic.

Frozen prereg commit: 1454d7b58875f5a50429e33979b0edfa5a1c7e88.
Research-only exact 256-hypothesis Bayesian learners, not accepted Yggdrasil
native model or owner checkpoint. All model updates consume exactly ONE
witnessed (public context, chosen action, consequence), never hidden labels.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import time
from pathlib import Path

SCHEMA = "yggdrasil.know24.gf2-structural-identifiability-result.v1"
PROTOCOL = "yggdrasil.know24.anf-identifiability-active-interventions-frozen-dev.v1"
PREREG = "1454d7b58875f5a50429e33979b0edfa5a1c7e88"
MODE = "engineering_fixture_only"
FIT = ((11021, "x0", 24), (11029, "x1", 24), (11047, "xor01", 24))
PAIRS = (
    ("x0", "x0_xor_x2", (11311, 11317, 11321)),
    ("xor01", "xor01_xor_x2", (11411, 11417, 11421)),
    ("and01", "and01_xor_x2", (11511, 11519, 11527)),
)
OPS = ("x0", "x1", "xor01", "x0_xor_x2", "xor01_xor_x2",
       "and01", "and01_xor_x2")
POLICIES = (
    "trained_anf_active", "untrained_anf_active",
    "uniform_full_bayes_active", "trained_anf_passive",
    "trained_anf_random", "context_beta_active",
    "family_informed_bayes", "source_only",
)
MONOMIALS = tuple(range(8))
ACTION_FLIP = (0, 1, 2)
STEP_COUNT = 16
P_LOW = .15
P_HIGH = .85
HYPOTHESES = tuple(range(256))
PAIR_FAMILY = (0,)


def require(yes, code):
    if not yes:
        raise ValueError("YGG_KNOW24_" + code)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":"), allow_nan=False).encode("ascii")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def coeffs(table):
    require(type(table) is int and 0 <= table <= 255, "HYPOTHESIS")
    result = []
    for mask in MONOMIALS:
        v = 0
        subset = mask
        while True:
            v ^= (table >> subset) & 1
            if subset == 0:
                break
            subset = (subset - 1) & mask
        result.append(v)
    return tuple(result)


ANF = tuple(coeffs(h) for h in HYPOTHESES)


def hidden_bit(op, c):
    require(op in OPS and type(c) is int and 0 <= c < 8, "PRIVATE_LAW")
    x0, x1, x2 = c & 1, (c >> 1) & 1, (c >> 2) & 1
    return {
        "x0": x0,
        "x1": x1,
        "xor01": x0 ^ x1,
        "x0_xor_x2": x0 ^ x2,
        "xor01_xor_x2": x0 ^ x1 ^ x2,
        "and01": x0 & x1,
        "and01_xor_x2": (x0 & x1) ^ x2
    }[op]


def op_table(op):
    return sum(hidden_bit(op, c) << c for c in range(8))


OP_TABLE = {op: op_table(op) for op in OPS}
KNOWN_PAIR_TABLES = tuple(dict.fromkeys(
    OP_TABLE[op] for a, b, seeds in PAIRS for op in (a, b)
))


def source_context(t):
    require(type(t) is int and 0 <= t < 24, "PUBLIC_STEP")
    return t % 4


def effective(c, action):
    require(type(c) is int and 0 <= c < 8
            and type(action) is int and action in (0, 1, 2),
            "PUBLIC_INTERVENTION")
    return c ^ ACTION_FLIP[action]


def private_coin(seed, t):
    require(type(seed) is int and
            seed in {s for s, op, n in FIT} |
            {seed for a, b, seeds in PAIRS for seed in seeds}
            and type(t) is int and 0 <= t < 24, "PRIVATE_NOISE")
    raw = f"know24:private:witness:v1:{seed}:{t}".encode("ascii")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big") / 2**64


def consequence(seed, op, t, c, action):
    require(op in OPS and c == source_context(t) and c < 4,
            "PRIVATE_WITNESS_INPUT")
    p = P_HIGH if hidden_bit(op, effective(c, action)) else P_LOW
    return int(private_coin(seed, t) < p)


def probability(op, c, action):
    return P_HIGH if hidden_bit(op, effective(c, action)) else P_LOW


def expected_brier(p, q):
    return q*(1-q) + (p-q)*(p-q)


def source_protocol():
    d = json.loads(Path(__file__).with_name("know24_protocol.json")
                   .read_text(encoding="utf-8"))
    require(d.get("schema") == PROTOCOL
            and [(z["seed"], z["op"], z["n"]) for z in d["fit"]] == list(FIT)
            and [(z["a"], z["b"], tuple(z["seeds"]))
                 for z in d["held_pairs"]] == list(PAIRS)
            and d["budget"]["held_worlds"] == 18
            and d["budget"]["held_witnesses_per_policy"] == 288
            and d["budget"]["held_high_eval_queries_per_policy"] == 216
            and d["budget"]["fit_witnesses"] == 72
            and d["thresholds"]["H3"].endswith("<= .26000 (calibrated uncertainty, not knowledge)")
            and d["model"].startswith("256 exact Boolean truth tables"),
            "FROZEN_PROTOCOL")
    return d


class TruthPosterior:
    """Exact source-free finite Bayes, no teacher/oracle during inference."""

    def __init__(self, prior, *, family=None):
        require(type(prior) is list and len(prior) == 8
                and all(type(p) is float and math.isfinite(p)
                        and .01 <= p <= .99 for p in prior),
                "PRIOR")
        self.prior = list(prior)
        self.family = tuple(HYPOTHESES if family is None else family)
        require(self.family and len(set(self.family)) == len(self.family)
                and all(type(h) is int and 0 <= h <= 255
                        for h in self.family), "FAMILY")
        self.logw = {}
        for h in self.family:
            mon = ANF[h]
            self.logw[h] = sum(math.log(p if coeff else 1-p)
                               for coeff, p in zip(mon, self.prior))
        self.events = []

    def _weights(self):
        maximum = max(self.logw.values())
        weights = {h:math.exp(logw-maximum)
                   for h, logw in self.logw.items()}
        total = sum(weights.values())
        require(total > 0 and math.isfinite(total), "NORMALIZATION")
        return {h:value/total for h,value in weights.items()}

    def prob(self, c, action):
        pos = effective(c, action)
        w = self._weights()
        return P_LOW + (P_HIGH-P_LOW) * sum(
            v for h, v in w.items() if (h >> pos) & 1)

    def choose(self, c, kind, rng=None):
        require(c < 4 and kind in ("active", "passive", "random"),
                "CHOICE")
        if kind == "passive":
            return 0
        if kind == "random":
            require(isinstance(rng, random.Random), "PUBLIC_RNG")
            return rng.randrange(3)
        # Bernoulli observation information maximized by q*(1-q).
        return min(range(3), key=lambda a:
                   (abs(self.prob(c, a)-.5), a))

    def observe(self, step, c, action, witnessed, *, source_mode=MODE):
        require(source_mode == MODE and type(step) is int
                and step == len(self.events) and 0 <= step < 24
                and c == source_context(step)
                and type(witnessed) is int and witnessed in (0,1),
                "WITNESS_OR_REPLAY")
        pos = effective(c, action)
        for h in self.family:
            q = P_HIGH if (h >> pos) & 1 else P_LOW
            self.logw[h] += math.log(q if witnessed else 1-q)
        self.events.append([step,c,action,witnessed])

    def expected_coeff(self):
        weights = self._weights()
        return [sum(w for h,w in weights.items() if ANF[h][j])
                for j in MONOMIALS]

    def checkpoint(self):
        raw = canonical({"schema":"yggdrasil.know24.hypothesis-custody.v1",
                          "mode": MODE, "prior":self.prior,
                          "family":self.family, "events":self.events,
                          "accepted_native":False,
                          "scientific_gain_verified":False})
        require(len(raw) <= 8192, "CHECKPOINT_CAPACITY")
        return raw

    @classmethod
    def restore(cls, raw, sha):
        require(type(raw) is bytes and len(raw) <= 8192
                and type(sha) is str and digest(raw)==sha,
                "CHECKPOINT_DIGEST")
        def no_duplicates(pairs):
            d={}
            for k,v in pairs:
                require(k not in d,"DUPLICATE_KEY")
                d[k]=v
            return d
        try:
            obj=json.loads(raw.decode("ascii"),object_pairs_hook=no_duplicates)
            require(type(obj) is dict and set(obj)=={
                "schema","mode","prior","family","events",
                "accepted_native","scientific_gain_verified"}
                and obj["schema"]=="yggdrasil.know24.hypothesis-custody.v1"
                and obj["mode"]==MODE and
                obj["accepted_native"] is False and
                obj["scientific_gain_verified"] is False and
                canonical(obj)==raw, "CHECKPOINT_CONTRACT")
            model=cls(obj["prior"],family=obj["family"])
            require(type(obj["events"]) is list and len(obj["events"])<=24,
                    "EVENT_COUNT")
            for step,row in enumerate(obj["events"]):
                require(type(row) is list and len(row)==4
                        and all(type(x) is int for x in row)
                        and row[0]==step, "EVENT_TYPE")
                model.observe(*row)
            require(model.checkpoint()==raw,"COLD_REPLAY")
            return model
        except (ValueError, KeyError, TypeError, UnicodeError,
                OverflowError) as ex:
            raise ValueError("YGG_KNOW24_CHECKPOINT_REJECTED") from ex


class ContextBeta:
    def __init__(self):
        self.cells=[[0,0] for _ in range(4)]
        self.events=[]

    def prob(self,c,a):
        target=effective(c,a)
        require(target<4,"UNOBSERVED_TARGET")
        wins,total=self.cells[target]
        return (wins+1)/(total+2)

    def choose(self,c,kind,rng=None):
        if kind=="passive":return 0
        if kind=="random":
            require(isinstance(rng,random.Random),"RNG")
            return rng.randrange(3)
        return min(range(3),key=lambda a:
                   (abs(self.prob(c,a)-.5),a))

    def observe(self,step,c,a,y,*,source_mode=MODE):
        require(source_mode==MODE and type(step) is int
                and step==len(self.events) and 0<=step<24
                and c==source_context(step) and type(y) is int
                and y in (0,1),"BETA_WITNESS")
        z=self.cells[effective(c,a)]
        z[0]+=y
        z[1]+=1
        self.events.append([step,c,a,y])

    def cold(self):
        d=canonical({"cells":self.cells,"events":self.events})
        other=ContextBeta()
        for row in self.events:
            other.observe(*row)
        require(other.cells==self.cells and
                canonical({"cells":other.cells,"events":other.events})==d,
                "BETA_COLD")
        return digest(d),len(d)


class Constant:
    def prob(self,c,a): return .5
    def choose(self,c,kind,rng=None):return 0
    def observe(self,step,c,a,y,*,source_mode=MODE):
        require(source_mode==MODE and type(y) is int and y in (0,1),
                "SOURCE_NEGATIVE")


def fitted_prior():
    source_protocol()
    src_models=[]
    for seed,op,steps in FIT:
        model=TruthPosterior([.25]*8)
        for step in range(steps):
            c=source_context(step)
            a=0 # frozen FIT passive intervention policy
            y=consequence(seed,op,step,c,a)
            model.observe(step,c,a,y)
        raw=model.checkpoint()
        cold=TruthPosterior.restore(raw,digest(raw))
        require(raw==cold.checkpoint()
                and cold.expected_coeff()==model.expected_coeff(),
                "FIT_CUSTODY")
        src_models.append(cold)
    p=[min(.92,max(.08,(.5+sum(m.expected_coeff()[j]
                                  for m in src_models))/5))
       for j in MONOMIALS]
    require(len(src_models)==3 and all(.08<=x<=.92 for x in p),
            "LEARNED_PRIOR")
    return p,src_models


def make_policy(name,trained_p):
    if name in ("trained_anf_active","trained_anf_passive","trained_anf_random"):
        return TruthPosterior(list(trained_p))
    if name=="untrained_anf_active":
        return TruthPosterior([.25]*8)
    if name=="uniform_full_bayes_active":
        return TruthPosterior([.5]*8)
    if name=="family_informed_bayes":
        return TruthPosterior([.5]*8,family=KNOWN_PAIR_TABLES)
    if name=="context_beta_active":
        return ContextBeta()
    if name=="source_only":
        return Constant()
    raise ValueError("YGG_KNOW24_UNEXPECTED_POLICY")


def run_world(name,seed,op,public_id,trained_prior):
    require(name in POLICIES
            and any(seed in seeds and op in (a,b)
                    for a,b,seeds in PAIRS)
            and type(public_id) is int and 0<=public_id<9,
            "FROZEN_WORLD")
    model=make_policy(name,trained_prior)
    rng=random.Random(17041*public_id+137)
    mode=("passive" if name in ("trained_anf_passive","source_only")
          else "random" if name=="trained_anf_random" else "active")
    tape=[]
    counts=[0,0,0]
    for step in range(STEP_COUNT):
        c=source_context(step)
        action=model.choose(c,mode,rng)
        counts[action]+=1
        y=consequence(seed,op,step,c,action)
        tape.append([c,action,y])
        model.observe(step,c,action,y)
    if isinstance(model,TruthPosterior):
        raw=model.checkpoint()
        cold=TruthPosterior.restore(raw,digest(raw))
        require(raw==cold.checkpoint()
                and all(model.prob(c,a)==cold.prob(c,a)
                        for c in range(8) for a in range(3)),
                "HELD_COLD")
        byte_count=len(raw)
        entropy=-sum(w*math.log2(w) for w in model._weights().values()
                     if w>0)
    elif isinstance(model,ContextBeta):
        _,byte_count=model.cold()
        entropy=None
    else:
        byte_count=0
        entropy=None

    high_forecast=[model.prob(c,a) if isinstance(model,TruthPosterior)
                   else .5 for c in range(4,8) for a in range(3)]
    low_forecast=[model.prob(c,a) for c in range(4) for a in range(3)]
    require(len(high_forecast)==len(low_forecast)==12
            and all(math.isfinite(p) and 0<=p<=1
                    for p in high_forecast+low_forecast),
            "FORECAST")
    high_brier=[expected_brier(p,probability(op,c,a))
                for p,(c,a) in zip(
                    high_forecast,[(c,a) for c in range(4,8)
                                   for a in range(3)])]
    low_brier=[expected_brier(p,probability(op,c,a))
               for p,(c,a) in zip(
                   low_forecast,[(c,a) for c in range(4)
                                 for a in range(3)])]
    return {"trace":tape,"high":high_forecast,"low":low_forecast,
            "high_sum":sum(high_brier),"low_sum":sum(low_brier),
            "counts":counts,"bytes":byte_count,"entropy":entropy,
            "witnesses":len(tape)}


def prove():
    started=time.monotonic()
    prior,fit_models=fitted_prior()
    result={}
    per_pair={}
    paired_identical={k:True for k in POLICIES}
    min_pair_loss={k:1 for k in POLICIES}
    policy_counts={}
    for name in POLICIES:
        entries=[]
        group=[]
        for pi,(a,b,seeds) in enumerate(PAIRS):
            summaries=[]
            for j,seed in enumerate(seeds):
                public_id=pi*3+j
                x=run_world(name,seed,a,public_id,prior)
                z=run_world(name,seed,b,public_id,prior)
                entries.extend((x,z))
                same=x["trace"]==z["trace"] and x["high"]==z["high"]
                paired_identical[name] &= same
                # Both worlds are indistinguishable under learned evidence.
                pair_brier=(x["high_sum"]+z["high_sum"])/24
                min_pair_loss[name]=min(min_pair_loss[name],pair_brier)
                summaries.append({"identical":same,
                                  "mean_high_expected_brier":round(pair_brier,8),
                                  "joint_trace_digest":digest(canonical(x["trace"]))})
            group.append({"pair":pi,"seeds":len(seeds),"rows":summaries})
        require(len(entries)==18
                and sum(x["witnesses"] for x in entries)==288,
                "ACTION_BUDGET")
        result[name]={
            "high_expected_brier":round(sum(x["high_sum"] for x in entries)/216,8),
            "low_expected_brier":round(sum(x["low_sum"] for x in entries)/216,8),
            "average_model_bytes":round(sum(x["bytes"] for x in entries)/18,2),
            "action_counts":tuple(sum(x["counts"][i] for x in entries)
                                  for i in range(3)),
            "mean_posterior_entropy":round(sum(x["entropy"]
                 for x in entries if x["entropy"] is not None)/18,8)
                 if all(x["entropy"] is not None for x in entries) else None,
        }
        per_pair[name]=group
    require(all(paired_identical.values())
            and all(v>=.25-1e-8 for v in min_pair_loss.values()),
            "CAUSAL_SOURCE_INVARIANCE_OR_LEAK")
    q=result["trained_anf_active"]
    nofit=result["untrained_anf_active"]
    passive=result["trained_anf_passive"]
    pred={
        "H1_pairs_identical":all(paired_identical.values()),
        "H2_paired_lower_bound":all(x>=.25-1e-8
                                   for x in min_pair_loss.values()),
        "H3_calibrated_high":q["high_expected_brier"]<=.26000,
        "H4_fit_high_improvement":q["high_expected_brier"]<=
                nofit["high_expected_brier"]-.01000,
        "H5_active_low_improvement":q["low_expected_brier"]<=
                passive["low_expected_brier"]-.01000
    }
    require(pred["H1_pairs_identical"] and pred["H2_paired_lower_bound"],
            "ENGINEERING_IDENTITY")
    science="SCIENCE_NO_GO_SYNTHETIC_EXACT_CAUSAL_NONIDENTIFIABILITY"
    return {
        "schema":SCHEMA,"prereg_commit":PREREG,
        "source_mode":MODE,"held_worlds":18,
        "fit_witnesses":72,"held_witnesses_per_policy":288,
        "high_expected_queries_per_policy":216,
        "low_expected_queries_per_policy":216,
        "operator_family_pairs":3,
        "learned_anf_coeff_prior":prior,
        "fit_task_checkpoint_bytes":[len(m.checkpoint()) for m in fit_models],
        "fit_task_cold_exact":True,
        "held_policy_metrics":result,
        "per_pair":per_pair,
        "min_paired_expected_brier":min_pair_loss,
        "frozen_predicates":pred,
        "development_verdict":(
            "CALIBRATED_STRUCTURAL_DEV" if pred["H3_calibrated_high"] else
            "STRUCTURAL_UNCERTAINTY_NO_GO"),
        "information_limit":"EXACT_PAIRED_HIGH_BRIER_FLOOR_0.25",
        "engineering_gate":"PASS",
        "scientific_gate":science,
        "native_modified":False,
        "protected_original_first_use":False,
        "accepted_checkpoint_changed":False,
        "deployment":"NONE",
        "isolated_wall_seconds":round(time.monotonic()-started,6)
    }


if __name__=="__main__":
    print(json.dumps(prove(),sort_keys=True,indent=2))
