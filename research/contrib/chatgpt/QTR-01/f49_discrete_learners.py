#!/usr/bin/env python3
"""F49 bounded native/grammar/exact-bank learners: model-side only, no target oracle.

All feedback is caller-supplied public (trajectory, two observed bits). No
protected seeds, evaluator truth, or held-out outcomes are accessible here.
Source-bank knowledge is public to every arm. First DEV comparison is separate.
"""
import hashlib
import json
import math
from functools import lru_cache

import f49_worlds as world

MAX_BUDGET = 32
PROPOSALS_PER_EVENT = 1024
BEAM = 64
KINDS = ("native", "compositional_bayes", "exact_bank_bayes", "random", "uniform")


class ControlRejected(world.F49Rejected):
    pass


def _check_trajectory(tr):
    if (type(tr) not in (tuple, list) or len(tr) != 3
        or any(type(x) is not int for x in tr)
        or not (0 < tr[0] < 256 and 0 < tr[1] < 256 and tr[0] != tr[1]
                and 0 <= tr[2] < 4)):
        raise ControlRejected("F49_INVALID_PUBLIC_TRAJECTORY")
    return tuple(tr)


def _check_bits(pair):
    if type(pair) not in (list, tuple) or len(pair) != 2 or any(type(v) is not int or v not in (0, 1) for v in pair):
        raise ControlRejected("F49_INVALID_PUBLIC_OUTCOME_BITS")
    return tuple(pair)


def _to_tuple(x):
    return tuple(_to_tuple(v) for v in x) if isinstance(x, list) else x


def _size(node):
    return 1 if node[0] == "leaf" else 1 + sum(_size(ch) for ch in node[1:])


def _predict_rule(node, tr):
    a, b, context = tr
    return (world.evaluate(node, a, 0, context),
            world.evaluate(node, b, a, context))


def _key(node):
    return json.dumps(node, separators=(",", ":"))


@lru_cache(maxsize=3)
def _initial_rules(bank_size):
    return (*world.source_bank(bank_size), *(world.leaf(i) for i in range(18)),
            *(("not", world.leaf(i)) for i in range(18)))


class GrammarLearner:
    """Integer mismatch/description-length learner or bounded grammar Bayes."""

    def __init__(self, bank_size, *, bayesian=False, random_proposals=False):
        world.freeze()
        if type(bank_size) is not int or bank_size not in world.BANK_SIZES:
            raise ControlRejected("F49_INVALID_SOURCE_BANK")
        self.bank_size = bank_size
        self.bayesian = bool(bayesian)
        self.random_proposals = bool(random_proposals)
        self.history = []
        self.rules = tuple(_initial_rules(bank_size))
        self.proposals = 0
        self.prediction_accesses = 0
        self._rank()

    def _rank(self):
        scored = []
        for node in self.rules:
            mismatches = 0
            for trajectory, outcome in self.history:
                prediction = _predict_rule(node, trajectory)
                self.prediction_accesses += 2
                mismatches += int(prediction[0] != outcome[0]) + int(prediction[1] != outcome[1])
            nodes = _size(node)
            if self.bayesian:
                # Negative log posterior up to a constant at observation-flip p=.10.
                score = mismatches * math.log(9) + 1.5 * nodes
            else:
                score = mismatches * 1000 + nodes
            scored.append((score, nodes, _key(node), node, mismatches))
        scored.sort(key=lambda x: (x[0], x[1], x[2]))
        self.best = tuple((entry[3], entry[4]) for entry in scored[:BEAM])
        self.rules = tuple(item[0] for item in self.best)

    def _proposal(self, step, i):
        # Public-only deterministic proposals, identical for native and grammar Bayes.
        seed = world.random_uint("F49/grammar-proposals/v1", self.bank_size, step, i)
        base = _initial_rules(self.bank_size)
        retained = self.rules
        lhs = (base if (seed & 3) == 0 else retained)[(seed >> 5) % (len(base) if (seed & 3) == 0 else len(retained))]
        rhs = (base if ((seed >> 3) & 3) == 0 else retained)[(seed >> 13) % (len(base) if ((seed >> 3) & 3) == 0 else len(retained))]
        op = ("xor", "and", "or", "not")[(seed >> 21) & 3]
        candidate = ("not", lhs) if op == "not" else (op, lhs, rhs)
        if world.ast_depth(candidate) > 4:
            return ("xor", world.leaf((seed >> 31) % 18), world.leaf((seed >> 39) % 18))
        return candidate

    def observe(self, tr, pair):
        tr = _check_trajectory(tr)
        pair = _check_bits(pair)
        if len(self.history) >= MAX_BUDGET:
            raise ControlRejected("F49_OBSERVATION_BUDGET_EXHAUSTED")
        # Inputs are checked before state mutation.
        step = len(self.history)
        additions = []
        for i in range(PROPOSALS_PER_EVENT):
            additions.append(self._proposal(step, i))
        self.proposals += PROPOSALS_PER_EVENT
        seen = set()
        combined = []
        for node in (*self.rules, *additions):
            k = _key(node)
            if k not in seen:
                seen.add(k)
                combined.append(node)
        self.history.append((tr, pair))
        self.rules = tuple(combined)
        self._rank()

    def probability(self, trajectory):
        tr = _check_trajectory(trajectory)
        if not self.history:
            return (0.5, 0.5)
        if not self.bayesian:
            result = _predict_rule(self.best[0][0], tr)
            self.prediction_accesses += 2
            return tuple(float(x) for x in result)
        logw = [-math.log(9) * mismatch - 1.5 * _size(node)
                for node, mismatch in self.best]
        normal = max(logw)
        weights = [math.exp(v - normal) for v in logw]
        outputs = [_predict_rule(node, tr) for node, _ in self.best]
        self.prediction_accesses += 2 * len(outputs)
        total = sum(weights)
        return tuple(sum(w * (0.9 if z[k] else 0.1)
                         for w, z in zip(weights, outputs)) / total for k in range(2))

    def cold_checkpoint(self):
        data = {"schema": "f49.grammar-cold.v1", "bank_size": self.bank_size,
                "bayesian": self.bayesian, "random_proposals": self.random_proposals,
                "events": [[list(t), list(y)] for t, y in self.history],
                "proposals": self.proposals}
        raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
        return raw + b"." + hashlib.sha256(raw).hexdigest().encode("ascii")

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or b"." not in raw:
            raise ControlRejected("F49_CHECKPOINT_REJECTED")
        body, checksum = raw.rsplit(b".", 1)
        if hashlib.sha256(body).hexdigest().encode("ascii") != checksum:
            raise ControlRejected("F49_CHECKPOINT_REJECTED")
        try:
            state = json.loads(body)
            if state.get("schema") != "f49.grammar-cold.v1":
                raise ValueError("schema")
            for k in ("bayesian", "random_proposals"):
                if type(state[k]) is not bool:
                    raise ValueError(k)
            obj = cls(state["bank_size"], bayesian=state["bayesian"],
                      random_proposals=state["random_proposals"])
            for tr, outcomes in state["events"]:
                obj.observe(tr, outcomes)
            if obj.proposals != state["proposals"] or obj.cold_checkpoint() != raw:
                raise ValueError("counter or canonical bytes")
            return obj
        except (ValueError, KeyError, TypeError, IndexError) as e:
            raise ControlRejected("F49_CHECKPOINT_REJECTED") from e


class ExactBankBayes:
    """Full noise-likelihood posterior on every known source program."""

    def __init__(self, size):
        world.freeze()
        if type(size) is not int or size not in world.BANK_SIZES:
            raise ControlRejected("F49_INVALID_SOURCE_BANK")
        self.size = size
        self.rules = world.source_bank(size)
        self.mismatch = [0] * size
        self.events = []
        self.prediction_accesses = 0

    def observe(self, tr, pair):
        tr, pair = _check_trajectory(tr), _check_bits(pair)
        if len(self.events) >= MAX_BUDGET:
            raise ControlRejected("F49_OBSERVATION_BUDGET_EXHAUSTED")
        new = []
        for index, ast in enumerate(self.rules):
            result = _predict_rule(ast, tr)
            self.prediction_accesses += 2
            new.append(self.mismatch[index] + sum(result[k] != pair[k] for k in range(2)))
        self.mismatch = new
        self.events.append((tr, pair))

    def probability(self, tr):
        tr = _check_trajectory(tr)
        lo = min(self.mismatch)
        weights = [9 ** (lo - mismatch) for mismatch in self.mismatch]
        total = sum(weights)
        output = [0.0, 0.0]
        for ast, weight in zip(self.rules, weights):
            pred = _predict_rule(ast, tr)
            self.prediction_accesses += 2
            for k in range(2):
                output[k] += weight * (0.9 if pred[k] else 0.1)
        return tuple(x / total for x in output)


class PublicArm:
    """Query-budget guard; only public trajectory indices and observed bits enter."""

    def __init__(self, kind, bank_size, dev_seed):
        world.freeze()
        if kind not in KINDS or type(dev_seed) is not int or dev_seed not in world.SEEDS:
            raise ControlRejected("F49_UNREGISTERED_ARM_OR_SEED")
        self.kind = kind
        self.bank_size, self.seed = bank_size, dev_seed
        self.queries = world.public_query_pool(bank_size, dev_seed)
        self.engine = (ExactBankBayes(bank_size) if kind == "exact_bank_bayes"
                       else GrammarLearner(bank_size, bayesian=(kind == "compositional_bayes"),
                                           random_proposals=False))
        self.used = []
        self.awaiting = None
        self.selector_accesses = 0

    def select(self):
        if self.awaiting is not None or len(self.used) >= MAX_BUDGET:
            raise ControlRejected("F49_QUERY_STATE_INVALID")
        remaining = [i for i in range(len(self.queries)) if i not in self.used]
        if self.kind == "uniform":
            choice = remaining[0]
        elif self.kind == "random":
            index = world.random_uint("F49/random/v1", self.bank_size, self.seed, len(self.used)) % len(remaining)
            choice = remaining[index]
        elif self.kind == "native":
            # Four best competing constructed explanations and disagreement.
            rules = self.engine.best[:4]
            def witness_score(index):
                preds = [_predict_rule(ast, self.queries[index]) for ast, _ in rules]
                self.selector_accesses += len(preds) * 2
                return tuple(abs(2 * sum(row[k] for row in preds) - len(preds)) for k in range(2))
            # Minimal summed balance has maximal disagreement (deterministic tie).
            choice = min(remaining, key=lambda idx: (sum(witness_score(idx)), idx))
        else:
            # Two-bit independent predictive entropy under same public candidate pool.
            def entropy_score(index):
                ps = self.engine.probability(self.queries[index])
                self.selector_accesses += 2
                return sum(-(p*math.log(p, 2)+(1-p)*math.log(1-p, 2))
                           for p in ps if 0 < p < 1)
            choice = min(remaining, key=lambda idx: (-entropy_score(idx), idx))
        self.awaiting = choice
        return choice, self.queries[choice]

    def observe(self, index, outcome):
        if type(index) is not int or self.awaiting is None or index != self.awaiting or index in self.used:
            raise ControlRejected("F49_UNAUTHORIZED_OR_REPLAYED_PUBLIC_EVENT")
        validated = _check_bits(outcome)
        self.engine.observe(self.queries[index], validated)
        self.used.append(index)
        self.awaiting = None

    @property
    def observed_bits(self):
        return 2 * len(self.used)


if __name__ == "__main__":
    print("F49_DISCRETE_ARMS_READY_NO_TARGET_FIRST_USE")
