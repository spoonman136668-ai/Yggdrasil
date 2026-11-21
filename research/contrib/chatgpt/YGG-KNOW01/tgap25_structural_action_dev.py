"""TGAP25: adaptive causal interventions from a bounded structural archive.

Research-only synthetic experiment. Preregistered BEFORE implementation at
f9cd943662740eccc0e8017b1d1198c3e5d18d77. Hand-supplied affine grammar
is an inductive bias, NOT independently discovered native intelligence.
Amalgam canonical model, accepted checkpoint and protected first-use untouched.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import time
from pathlib import Path

PREREG = "f9cd943662740eccc0e8017b1d1198c3e5d18d77"
SCHEMA = "yggdrasil.tgap25.structural-archive-result.v1"
PROTOCOL = "yggdrasil.tgap25.structural-archive-adaptive-action-prereg.v1"
MODE = "engineering_fixture_only"
FIT = ((11101, "x0"), (11107, "x1"))
HELD = (
    (11201, "x0"), (11209, "x0"), (11213, "x0"),
    (11303, "x1"), (11311, "x1"), (11317, "x1"),
    (11401, "parity3"), (11411, "parity3"), (11423, "parity3"),
    (11501, "majority3"), (11503, "majority3"), (11519, "majority3"),
)
GROUPS = ("x0", "x1", "parity3", "majority3")
ARMS = (
    "archive_fit", "archive_no_fit", "affine_bayes_pooled_fit",
    "fulltruth_bayes_archive_fit", "context_beta_fit",
    "context_rolling_fit", "source_only", "privileged_oracle",
)
P_HIGH, P_LOW = .8, .2
REGRET = P_HIGH - P_LOW


def require(ok, code):
    if not ok:
        raise ValueError("YGG_TGAP25_" + code)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def public(t):
    require(type(t) is int and 0 <= t < 64, "PUBLIC_STEP")
    return t % 8


def fixed_action(t):
    return (t // 8) % 2


def truth(rule, c):
    require(rule in GROUPS and type(c) is int and 0 <= c < 8,
            "PRIVATE_OPERATOR")
    x0, x1, x2 = c & 1, (c >> 1) & 1, (c >> 2) & 1
    return {"x0": x0, "x1": x1, "parity3": x0 ^ x1 ^ x2,
            "majority3": int(x0 + x1 + x2 >= 2)}[rule]


def affine_law(code, c):
    return ((code & 1) ^ (((code >> 1) & 1) & (c & 1)) ^
            (((code >> 2) & 1) & ((c >> 1) & 1)) ^
            (((code >> 3) & 1) & ((c >> 2) & 1)))


def law_bit(code, c, size):
    return affine_law(code, c) if size == 16 else (code >> c) & 1


def private_coin(seed, rule, step):
    require(type(seed) is int and 0 < seed and rule in GROUPS
            and type(step) is int and 0 <= step < 64, "PRIVATE_RANDOM")
    data = hashlib.sha256(
        f"tgap25:private:outcome:v1:{seed}:{rule}:{step}".encode("ascii")
    ).digest()
    return int.from_bytes(data[:8], "big") / (1 << 64)


def consequence(seed, rule, step, action):
    require(type(action) is int and action in (0, 1), "ACTION")
    p = P_HIGH if action == truth(rule, public(step)) else P_LOW
    return int(private_coin(seed, rule, step) < p)


class Posterior:
    """Finite binary-law hypothesis belief, updated by ONE witnessed action."""
    def __init__(self, size):
        require(type(size) is int and size in (16, 256), "HYPOTHESIS_COUNT")
        self.size = size
        self.logw = [0.0] * size
        self.seen = 0

    def weights(self):
        hi = max(self.logw)
        row = [math.exp(v - hi) for v in self.logw]
        norm = sum(row)
        require(norm > 0 and math.isfinite(norm), "NORMALIZATION")
        return [v / norm for v in row]

    def best1(self, c):
        return sum(w for i, w in enumerate(self.weights())
                   if law_bit(i, c, self.size))

    def witness_likelihood(self, c, action, observed):
        require(type(c) is int and 0 <= c < 8
                and type(action) is int and action in (0, 1)
                and type(observed) is int and observed in (0, 1),
                "WITNESS_TYPES")
        out = 0.0
        for idx, weight in enumerate(self.weights()):
            p = P_HIGH if action == law_bit(idx, c, self.size) else P_LOW
            out += weight * (p if observed else 1 - p)
        require(0 < out < 1, "NONZERO_LIKELIHOOD")
        return out

    def observe(self, c, action, outcome):
        self.witness_likelihood(c, action, outcome)
        for idx in range(self.size):
            p = P_HIGH if action == law_bit(idx, c, self.size) else P_LOW
            self.logw[idx] += math.log(p if outcome else 1 - p)
        self.seen += 1

    def raw(self):
        return {"size": self.size, "seen": self.seen,
                "logw": self.logw}

    @classmethod
    def from_raw(cls, doc):
        require(type(doc) is dict and set(doc) == {"size", "seen", "logw"}
                and type(doc["size"]) is int and doc["size"] in (16, 256)
                and type(doc["seen"]) is int and 0 <= doc["seen"] <= 128
                and type(doc["logw"]) is list
                and len(doc["logw"]) == doc["size"]
                and all(type(v) is float and math.isfinite(v)
                        and -600 < v <= 0
                        for v in doc["logw"]), "POSTERIOR_COLD")
        p = cls(doc["size"])
        p.seen, p.logw = doc["seen"], doc["logw"]
        return p


class Archive:
    """Two immutable FIT posteriors + fresh episode posterior, no law labels."""
    def __init__(self, episodes, size=16):
        require(type(episodes) is list and len(episodes) == 2
                and all(type(x) is Posterior and x.size == size
                        for x in episodes), "ARCHIVE_COMPONENTS")
        self.archives = [copy.deepcopy(x) for x in episodes]
        self.fresh = Posterior(size)
        self.mix = [1/3] * 3
        self.size = size
        self.next_step = 0
        self._archive_sha = sha(canonical([p.raw() for p in self.archives]))

    def archived_sha(self):
        return sha(canonical([p.raw() for p in self.archives]))

    def best1(self, c):
        comps = [*self.archives, self.fresh]
        return sum(w * p.best1(c) for w, p in zip(self.mix, comps))

    def observe(self, step, c, action, reward, *, mode=MODE):
        require(mode == MODE and type(step) is int
                and step == self.next_step and c == public(step)
                and type(action) is int and action in (0, 1)
                and type(reward) is int and reward in (0, 1),
                "EVENT_SOURCE_REPLAY")
        comps = [*self.archives, self.fresh]
        like = [p.witness_likelihood(c, action, reward) for p in comps]
        weighted = [w * l for w, l in zip(self.mix, like)]
        normal = sum(weighted)
        require(normal > 0, "META_POSTERIOR")
        self.mix = [v / normal for v in weighted]
        self.fresh.observe(c, action, reward)
        self.next_step += 1
        require(self.archived_sha() == self._archive_sha, "ARCHIVE_MUTATION")

    def checkpoint(self):
        raw = canonical({
            "schema": "yggdrasil.tgap25.affine-archive.cold.v1",
            "mode": MODE, "size": self.size, "next_step": self.next_step,
            "archives": [p.raw() for p in self.archives],
            "fresh": self.fresh.raw(), "mix": self.mix,
            "archive_sha": self._archive_sha,
            "accepted_native": False, "scientific_gain_verified": False,
        })
        require(len(raw) <= 65536, "ARCHIVE_CAPACITY")
        return raw

    @classmethod
    def restore(cls, raw, expected):
        require(type(raw) is bytes and 0 < len(raw) <= 65536
                and sha(raw) == expected, "COLD_DIGEST")
        def no_dupes(pairs):
            out = {}
            for k, v in pairs:
                require(k not in out, "DUPLICATE_COLD_KEY")
                out[k] = v
            return out
        try:
            d = json.loads(raw, object_pairs_hook=no_dupes)
            require(type(d) is dict and set(d) == {
                "schema", "mode", "size", "next_step", "archives",
                "fresh", "mix", "archive_sha",
                "accepted_native", "scientific_gain_verified",
            } and d["schema"] == "yggdrasil.tgap25.affine-archive.cold.v1"
                    and d["mode"] == MODE
                    and d["accepted_native"] is False
                    and d["scientific_gain_verified"] is False
                    and type(d["archives"]) is list
                    and len(d["archives"]) == 2
                    and type(d["mix"]) is list and len(d["mix"]) == 3
                    and all(type(x) is float and math.isfinite(x) and
                            0 <= x <= 1 for x in d["mix"])
                    and abs(sum(d["mix"]) - 1) < 1e-12
                    and type(d["next_step"]) is int
                    and 0 <= d["next_step"] <= 64
                    and canonical(d) == raw, "COLD_SCHEMA")
            a = [Posterior.from_raw(x) for x in d["archives"]]
            m = cls(a, d["size"])
            m.fresh = Posterior.from_raw(d["fresh"])
            m.mix = d["mix"]
            m.next_step = d["next_step"]
            require(m.fresh.seen == m.next_step
                    and m._archive_sha == d["archive_sha"]
                    and m.checkpoint() == raw, "COLD_REPLAY")
            return m
        except (TypeError, ValueError, KeyError, OverflowError) as e:
            raise ValueError("YGG_TGAP25_COLD_REJECT") from e


class ContextualBeta:
    """Fully FIT, standard per context-action success/trial or rolling evidence."""
    def __init__(self, rolling=False):
        self.rows = [[[] for _ in range(2)] for _ in range(8)]
        self.rolling = rolling
        self.seen = 0

    def best1(self, c):
        def p(a):
            vals = self.rows[c][a]
            return (sum(vals)+1)/(len(vals)+2)
        return .5 + .5*(p(1)-p(0))

    def observe(self, step, c, action, reward, *, mode=MODE):
        require(mode == MODE and type(step) is int and
                type(c) is int and 0 <= c < 8 and
                type(action) is int and action in (0, 1)
                and type(reward) is int and reward in (0, 1),
                "BETA_SOURCE")
        self.rows[c][action].append(reward)
        if self.rolling:
            self.rows[c][action] = self.rows[c][action][-8:]
        self.seen += 1


class PlainAffine:
    def __init__(self, posterior):
        self.posterior = copy.deepcopy(posterior)
        self.next_step = 0

    def best1(self, c):
        return self.posterior.best1(c)

    def observe(self, step, c, action, reward, *, mode=MODE):
        require(mode == MODE and step == self.next_step, "PLAIN_REPLAY")
        self.posterior.observe(c,action,reward)
        self.next_step += 1


class FixedNoLearn:
    def best1(self, c):
        return .5
    def observe(self, step, c, action, reward, *, mode=MODE):
        require(mode == MODE, "NEGATIVE_SOURCE")


def train_episode(seed, law, size, fitted_controls):
    """Only factual public actions and witnessed rewards enter fitted models."""
    posterior = Posterior(size)
    for step in range(64):
        c = public(step)
        action = fixed_action(step)
        reward = consequence(seed, law, step, action)
        posterior.observe(c, action, reward)
        if fitted_controls is not None:
            for control in fitted_controls:
                if type(control) is Posterior:
                    control.observe(c, action, reward)
                else:
                    control.observe(step, c, action, reward)
    require(posterior.seen == 64, "FIT_ACTION_BUDGET")
    return posterior


def fit():
    contextual = ContextualBeta()
    rolling = ContextualBeta(rolling=True)
    plain = Posterior(16)
    fitted = [contextual, rolling, plain]
    affine_a = train_episode(*FIT[0], 16, fitted)
    affine_b = train_episode(*FIT[1], 16, fitted)
    full_a = train_episode(*FIT[0], 256, None)
    full_b = train_episode(*FIT[1], 256, None)
    require(contextual.seen == rolling.seen == plain.seen == 128
            and affine_a.seen == affine_b.seen == 64, "FIT_EQUAL_SOURCE")
    archive = Archive([affine_a,affine_b])
    full = Archive([full_a,full_b],size=256)
    frozen_archive = archive.archived_sha()
    raw = archive.checkpoint()
    require(Archive.restore(raw,sha(raw)).checkpoint() == raw,
            "FIT_COLD")
    return {"archive":archive,"fulltruth":full,"contextual":contextual,
            "rolling":rolling,"plain":plain,
            "source_fit_actions":128,
            "old_archive":frozen_archive,
            "archive_bytes":len(raw),
            "fulltruth_bytes":len(full.checkpoint())}


def evaluate_world(fitted, world):
    require(type(world) is tuple and world in HELD, "HELD_WORLD")
    seed, rule = world
    models = {
        "archive_fit": copy.deepcopy(fitted["archive"]),
        "archive_no_fit": Archive([Posterior(16),Posterior(16)]),
        "affine_bayes_pooled_fit": PlainAffine(fitted["plain"]),
        "fulltruth_bayes_archive_fit": copy.deepcopy(fitted["fulltruth"]),
        "context_beta_fit": copy.deepcopy(fitted["contextual"]),
        "context_rolling_fit": copy.deepcopy(fitted["rolling"]),
        "source_only": FixedNoLearn(),
    }
    total_regret = {k:0.0 for k in ARMS}
    total_rewards = {k:0 for k in ARMS}
    action_records = {k:0 for k in ARMS}
    for step in range(64):
        c = public(step)
        for name in ARMS:
            model = models.get(name)
            if name == "privileged_oracle":
                action = truth(rule,c) # evaluator-only upper bound
            elif step < 16:
                action = fixed_action(step) # equal 16 warmup actions
            else:
                p = model.best1(c)
                require(type(p) is float and math.isfinite(p)
                        and 0 <= p <= 1, "POLICY_PROBABILITY")
                action = int(p > .5) if p != .5 else step % 2
            reward = consequence(seed,rule,step,action)
            if step >= 16:
                total_regret[name] += REGRET * (action != truth(rule,c))
                total_rewards[name] += reward
            if name != "privileged_oracle":
                model.observe(step,c,action,reward)
            action_records[name] += 1
    require(set(action_records.values()) == {64}, "MATCHED_ACTION_COUNT")
    mem = models["archive_fit"]
    raw = mem.checkpoint()
    require(Archive.restore(raw,sha(raw)).checkpoint() == raw
            and mem.archived_sha() == fitted["old_archive"], "COLD_OLD_A_B")
    return {"seed":seed, "rule":rule, "regret_sum":total_regret,
            "rewards":total_rewards,"actions_per_policy":64,
            "scored_per_policy":48,
            "archive_unchanged":mem.archived_sha() == fitted["old_archive"],
            "candidate_bytes":len(raw)}


def proof():
    started = time.monotonic()
    doc = json.loads(Path(__file__).with_name(
        "tgap25_protocol.json").read_text(encoding="utf-8"))
    require(doc["schema"] == PROTOCOL
            and [(x["seed"],x["rule"]) for x in
                 doc["private_world"]["fit_worlds"]] == list(FIT)
            and [(x["seed"],x["rule"]) for x in
                 doc["private_world"]["held_worlds"]] == list(HELD)
            and doc["private_world"]["scored_actions_per_policy"] == 576
            and doc["private_world"]["fit_actions_per_policy"] == 128
            and doc["candidate"]["no_fit"].startswith(
                "Same three-component archive reader"), "PREREG_DRIFT")
    fitted = fit()
    results = [evaluate_world(fitted,w) for w in HELD]
    require(len(results) == 12 and
            sum(x["scored_per_policy"] for x in results) == 576, "SCORED_BUDGET")
    all_regret = {
        arm: round(sum(w["regret_sum"][arm] for w in results)/576,8)
        for arm in ARMS
    }
    family_regret = {
        rule: {arm:round(
            sum(w["regret_sum"][arm] for w in results
                if w["rule"] == rule) / 144,8)
                for arm in ARMS}
        for rule in GROUPS
    }
    realized = {
        arm:round(sum(w["rewards"][arm] for w in results)/576,8)
        for arm in ARMS
    }
    recurrence_fit_gain = round(
        ((family_regret["x0"]["archive_no_fit"] +
          family_regret["x1"]["archive_no_fit"]) -
         (family_regret["x0"]["archive_fit"] +
          family_regret["x1"]["archive_fit"]))/2,8)
    affine_gain = round(
        family_regret["parity3"]["context_rolling_fit"] -
        family_regret["parity3"]["archive_fit"],8)
    majority_harm = round(
        family_regret["majority3"]["archive_fit"] -
        family_regret["majority3"]["context_rolling_fit"],8)
    equal_affine_gain = round(
        all_regret["affine_bayes_pooled_fit"] -
        all_regret["archive_fit"],8)
    h = {
        "H1_recurring_rules_fit_gain_point06":
            recurrence_fit_gain >= .06,
        "H2_new_affine_vs_rolling_gain_point06":
            affine_gain >= .06,
        "H3_majority_not_worse_point06":
            majority_harm <= .06,
        "H4_archived_A_B_unchanged_cold":
            all(w["archive_unchanged"] for w in results),
        "H5_overall_vs_fitted_pooled_affine_point03":
            equal_affine_gain >= .03,
    }
    passes = sum(h.values())
    return {
        "schema":SCHEMA, "prereg_commit":PREREG,
        "mode":MODE, "fit_actions_per_policy":fitted["source_fit_actions"],
        "held_actions_per_policy":sum(w["actions_per_policy"] for w in results),
        "held_warmup_per_policy":12*16,"held_scored_per_policy":576,
        "held_worlds":12, "mean_expected_regret":all_regret,
        "mean_realized_reward":realized,
        "regret_by_hidden_family_scoring_only":family_regret,
        "frozen_margins":{
            "H1_recurrence_gain":recurrence_fit_gain,
            "H2_affine_gain":affine_gain,
            "H3_majority_harm":majority_harm,
            "H5_pooled_affine_gain":equal_affine_gain,
        },
        "frozen_hypotheses":h,
        "development_verdict":
            "DEV_STRUCTURAL_ARCHIVE_SUPPORTED" if passes == 5 else
            "DEV_MIXED_STRUCTURAL_ARCHIVE" if passes else
            "STRUCTURAL_ARCHIVE_NO_GO",
        "archive_A_B_retention_by_construction":True,
        "fit_archive_checkpoint_bytes":fitted["archive_bytes"],
        "fit_fulltruth_checkpoint_bytes":fitted["fulltruth_bytes"],
        "max_held_archive_bytes":max(w["candidate_bytes"] for w in results),
        "engineering_gate":"PASS", "science_gate":"SCIENCE_NO_GO_SYNTHETIC",
        "native_model_changed":False, "protected_first_use":False,
        "deploy":"NONE",
        "elapsed_no_checkout_s":round(time.monotonic()-started,6),
    }


if __name__ == "__main__":
    print("YGG_TGAP25_RECEIPT="+json.dumps(proof(),sort_keys=True))
