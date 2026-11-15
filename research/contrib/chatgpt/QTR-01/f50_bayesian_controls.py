#!/usr/bin/env python3
"""F50 Bayesian public-action controls, without target graph or evaluator access.

Two independent comparators: posterior over the entire exact FIT source bank,
and bounded compositional-grammar posterior with 2,048 proposals per observed
public trajectory. Source DAGs and training rows are available through the
same PublicFIT interface used by native/conventional controls. The target law
is *not* in the exact source bank by preregistration. No target first use here.
"""
from hashlib import sha256
import json
import math

import numpy as np

import f50_public_corpus as public
import f50_worlds as world

SCHEMA = "yggdrasil.qtr01.f50.bayesian-public-cold.v1"
KINDS = ("exact_source_bank_bayes", "compositional_grammar_bayes")
MAX_QUERIES = 64
PROPOSALS = 2048
BEAM = 64
LOG_ODDS = math.log(9)


class BayesianRejected(public.PublicSourceRejected):
    pass


def _prediction(rule, episode):
    a, b, c, ctx = world.validate_trajectory(episode)
    return (world.evaluate(rule, a, 0, 0, ctx),
            world.evaluate(rule, b, a, 0, ctx),
            world.evaluate(rule, c, b, a, ctx))


def _nodes(node):
    return 1 if node[0] == "leaf" else 1 + sum(_nodes(x) for x in node[1:])


def _key(node):
    return json.dumps(node, separators=(",", ":"))


class BayesianPublicArm:
    def __init__(self, size, seed, kind):
        world.freeze()
        world._check_bank_size(size)
        world._check_dev_seed(seed)
        if kind not in KINDS:
            raise BayesianRejected("F50_BAYES_UNREGISTERED_KIND")
        self.size, self.seed, self.kind = size, seed, kind
        self.corpus = public.PublicFIT(size)
        self.pool = world.public_candidate_pool(size, seed)
        self.fit_ids = self.corpus.ids
        self.source_graph_sha = self.corpus.digest_for_fit_graphs()
        self.used = []
        self.awaiting = None
        self.events = []
        self.proposals = 0
        self.prediction_accesses = 0
        self.optimizer_steps = 0
        self.target_graph_available = False
        self._matrix = None
        if kind == "exact_source_bank_bayes":
            # Entire public FIT source graph bank, not a cherry-picked subset.
            self.rules = tuple(public.decode_source_graph(self.corpus.source_graph(i))
                               for i in self.fit_ids)
        else:
            # Full FIT graph access; initial beam is an outcome-independent draw.
            ordered = sorted(self.fit_ids,
                             key=lambda i: (world.digest("F50/grammar-init/v1", size, i), i))
            self.rules = tuple(public.decode_source_graph(self.corpus.source_graph(i))
                               for i in ordered[:BEAM])
        self.errors = [0] * len(self.rules)

    def _weights(self):
        scores = [LOG_ODDS * err + (1.5 * _nodes(rule)
                  if self.kind == "compositional_grammar_bayes" else 0.0)
                  for rule, err in zip(self.rules, self.errors)]
        best = min(scores)
        raw = np.exp(-np.asarray(scores, dtype=np.float64) + best)
        return raw / raw.sum()

    def _pool_cube(self):
        if self._matrix is None:
            cube = np.empty((len(self.rules), len(self.pool), 3), dtype=np.uint8)
            for i, rule in enumerate(self.rules):
                for j, episode in enumerate(self.pool):
                    cube[i, j] = _prediction(rule, episode)
            cube.flags.writeable = False
            self._matrix = cube
            self.prediction_accesses += int(cube.size)
        return self._matrix

    def probabilities(self, episodes):
        if (type(episodes) not in (list, tuple) or not episodes
            or len(episodes) > world.PUBLIC_QUERIES):
            raise BayesianRejected("F50_BAYES_PREDICTION_BATCH_INVALID")
        valid = tuple(world.validate_trajectory(x) for x in episodes)
        weights = self._weights()
        if self.kind == "exact_source_bank_bayes" and all(x in self.pool for x in valid):
            indices = [self.pool.index(x) for x in valid]
            truth = self._pool_cube()[:, indices, :]
            probabilities = 0.1 + 0.8 * np.einsum(
                "i,ijk->jk", weights, truth, optimize=False)
        else:
            probabilities = np.zeros((len(valid), 3), dtype=np.float64)
            for rule, weight in zip(self.rules, weights):
                for j, episode in enumerate(valid):
                    probabilities[j] += weight * (0.1 + 0.8 * np.asarray(
                        _prediction(rule, episode), dtype=np.float64))
                    self.prediction_accesses += 3
        return tuple(tuple(float(x) for x in row) for row in probabilities)

    def probability(self, episode):
        return self.probabilities((episode,))[0]

    def select(self):
        if self.awaiting is not None or len(self.used) >= MAX_QUERIES:
            raise BayesianRejected("F50_BAYES_QUERY_STATE_INVALID")
        available = [i for i in range(len(self.pool)) if i not in self.used]
        weights = self._weights()
        if self.kind == "exact_source_bank_bayes":
            cube = self._pool_cube()[:, available, :]
            p = 0.1 + 0.8 * np.einsum("i,ijk->jk", weights, cube,
                                         optimize=False)
        else:
            p = np.zeros((len(available), 3), dtype=np.float64)
            for rule, weight in zip(self.rules, weights):
                p += weight * (0.1 + 0.8 * np.asarray(
                    [_prediction(rule, self.pool[i]) for i in available],
                    dtype=np.float64))
            self.prediction_accesses += 3 * len(self.rules) * len(available)
        p = np.clip(p, 1e-12, 1 - 1e-12)
        ent = -np.sum(p * np.log2(p) + (1 - p) * np.log2(1 - p), axis=1)
        self.awaiting = available[int(np.argmax(ent))]
        return self.awaiting, self.pool[self.awaiting]

    def _proposal(self, step, ordinal):
        value = world.random_uint("F50/grammar-bayes-propose/v1",
                                  self.size, self.seed, step, ordinal)
        take_beam = self.rules and (value & 3) != 0
        if take_beam:
            base = self.rules[(value >> 3) % len(self.rules)]
        else:
            index = self.fit_ids[(value >> 3) % len(self.fit_ids)]
            base = public.decode_source_graph(self.corpus.source_graph(index))
        x = world.leaf((value >> 17) % 33)
        y = world.leaf((value >> 24) % 33)
        operation = ("xor", "and", "or")[(value >> 31) % 3]
        variant = (value >> 35) % 4
        rule = ((operation, base, x) if variant == 0 else
                (operation, x, base) if variant == 1 else
                ("not", (operation, base, x)) if variant == 2 else
                ("xor", base, ("and", x, y)))
        if world.ast_depth(rule) > 6:
            rule = ("xor", x, ("and", y, world.leaf((value >> 42) % 33)))
        return rule

    def _grammar_update(self):
        step = len(self.events) - 1
        proposals = [self._proposal(step, i) for i in range(PROPOSALS)]
        self.proposals += PROPOSALS
        seen = set()
        scored = []
        for rule in (*self.rules, *proposals):
            signature = world.anf(rule)
            if signature in seen:
                continue
            seen.add(signature)
            errors = 0
            for episode, outcomes in self.events:
                predicted = _prediction(rule, episode)
                self.prediction_accesses += 3
                errors += sum(a != b for a, b in zip(predicted, outcomes))
            scored.append((LOG_ODDS * errors + 1.5 * _nodes(rule),
                           _nodes(rule), _key(rule), rule, errors))
        scored.sort(key=lambda x: (x[0], x[1], x[2]))
        retained = scored[:BEAM]
        self.rules = tuple(x[3] for x in retained)
        self.errors = [x[4] for x in retained]

    def observe(self, index, outcomes):
        if (type(index) is not int or index != self.awaiting
            or index in self.used or len(self.used) >= MAX_QUERIES):
            raise BayesianRejected("F50_BAYES_UNAUTHORIZED_OR_REPLAY")
        episode, bits = public.observed_episode(self.pool[index], outcomes)
        if self.kind == "exact_source_bank_bayes":
            cube = self._pool_cube()[:, index, :]
            diff = np.count_nonzero(cube != np.asarray(bits)[None, :], axis=1)
            self.errors = [old + int(n) for old, n in zip(self.errors, diff)]
            self.prediction_accesses += 3 * len(self.rules)
        self.events.append((episode, bits))
        if self.kind == "compositional_grammar_bayes":
            self._grammar_update()
        self.used.append(index)
        self.awaiting = None

    @property
    def observed_bits(self):
        return 3 * len(self.used)

    def cold_checkpoint(self):
        if self.awaiting is not None:
            raise BayesianRejected("F50_BAYES_COLD_PENDING_QUERY")
        payload = {"schema": SCHEMA, "kind": self.kind, "size": self.size,
                   "seed": self.seed, "source_graph_sha": self.source_graph_sha,
                   "used": self.used,
                   "events": [[list(t), list(y)] for t, y in self.events],
                   "proposals": self.proposals,
                   "prediction_accesses": self.prediction_accesses,
                   "optimizer_steps": self.optimizer_steps,
                   "target_graph_available": False}
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
        return raw + b"." + sha256(raw).hexdigest().encode("ascii")

    @classmethod
    def restore(cls, checkpoint):
        if type(checkpoint) is not bytes or b"." not in checkpoint:
            raise BayesianRejected("F50_BAYES_COLD_ENVELOPE_REJECTED")
        body, checksum = checkpoint.rsplit(b".", 1)
        if sha256(body).hexdigest().encode("ascii") != checksum:
            raise BayesianRejected("F50_BAYES_COLD_CHECKSUM_REJECTED")
        try:
            state = json.loads(body)
            arm = cls(state["size"], state["seed"], state["kind"])
            if (state["schema"] != SCHEMA or state["source_graph_sha"] != arm.source_graph_sha
                or state["target_graph_available"] is not False
                or state["optimizer_steps"] != 0
                or type(state["used"]) is not list
                or len(state["used"]) != len(state["events"])
                or len(state["used"]) > MAX_QUERIES):
                raise ValueError("custody")
            for index, event in zip(state["used"], state["events"]):
                proposed, episode = arm.select()
                admitted, bits = public.observed_episode(*event)
                if type(index) is not int or proposed != index or episode != admitted:
                    raise ValueError("event mismatch")
                arm.observe(index, bits)
            # Prediction-only calls are not replayable from feedback receipts;
            # preserve their explicitly reported logical access count.
            if (arm.proposals != state["proposals"]
                or type(state["prediction_accesses"]) is not int
                or state["prediction_accesses"] < arm.prediction_accesses):
                raise ValueError("counter integrity")
            arm.prediction_accesses = state["prediction_accesses"]
            if arm.cold_checkpoint() != checkpoint:
                raise ValueError("noncanonical")
            return arm
        except (KeyError, TypeError, ValueError, IndexError, OverflowError,
                world.F50Rejected, public.PublicSourceRejected) as exc:
            raise BayesianRejected("F50_BAYES_COLD_REJECTED") from exc


if __name__ == "__main__":
    world.freeze()
    print("F50_BAYESIAN_CONTROLS_READY_NO_TARGET_FIRST_USE")
