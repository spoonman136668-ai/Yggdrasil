"""NUM06 source-independent, conjugate Gaussian two-regime control.

This is a FIT-tunable comparator, not a new Yggdrasil native learner or an
original-world source adapter. Forecasts use only previously witnessed public
NUM05-compatible observations/action/reward packets. The regime is latent:
no true task label, phase clock, unseen action result or privileged source.
"""
from __future__ import annotations

import itertools
import json
import math

from num05 import (ACTIONS, MAX_ROWS, SOURCE_TAG, canonical, digest, error,
                   public_action, public_row, public_state, region, target)

SCHEMA = "yggdrasil.num06.bayes-two-bank-public.v1"
HAZARDS = (0.005, 0.02, 0.08)
NOISE_SIGMAS = (0.04, 0.15)
PRIOR_STDS = (0.5, 1.0)
HYPER_GRID = tuple(itertools.product(HAZARDS, NOISE_SIGMAS, PRIOR_STDS))


class BayesianTwoBank:
    """Posterior-predictive mixture of two learned public consequence banks.

    Per bank and action-quadrant cell, assume a Gaussian outcome with an
    independent Normal(0, prior_std^2) mean prior and known noise variance.
    Maintain soft weighted sufficient statistics. A symmetric, source-blind
    Markov hazard lets the posterior return to an archived law. This is a
    fitted Bayesian *filter*, not an exact posterior over all bank histories.
    """

    def __init__(self, *, hazard=0.02, noise_sigma=0.04, prior_std=0.5):
        if any(type(v) is not float or not math.isfinite(v) for v in
               (hazard, noise_sigma, prior_std)):
            raise ValueError("NUM06_HYPERPARAM_TYPE")
        if not 0 < hazard < 0.5 or not 0 < noise_sigma <= 1.0 or not 0 < prior_std <= 2:
            raise ValueError("NUM06_HYPERPARAM_BOUNDS")
        self.hazard = hazard
        self.noise_sigma = noise_sigma
        self.prior_std = prior_std
        self.banks = [{}, {}]
        self.posterior = [1.0, 0.0]
        self.rows = []
        self.seen = set()
        self.mode_switches = []
        self.active = 0

    @staticmethod
    def _key(observation, action):
        return str(region(observation)) + ":" + str(public_action(action))

    def _parameters(self, bank, observation, action):
        key = self._key(observation, action)
        n, sums = self.banks[bank].get(key, [0.0, [0.0, 0.0, 0.0]])
        noise2 = self.noise_sigma ** 2
        post_var = 1.0 / (1.0 / self.prior_std ** 2 + n / noise2)
        center = [post_var * s / noise2 for s in sums]
        return center, noise2 + post_var

    def _prior_mass(self):
        if len(self.rows) < 100:
            return [1.0, 0.0]
        h = self.hazard
        return [(1-h)*self.posterior[0] + h*self.posterior[1],
                (1-h)*self.posterior[1] + h*self.posterior[0]]

    def predict(self, observation, action):
        public_state(observation)
        public_action(action)
        mass = self._prior_mass()
        centers = [self._parameters(i, observation, action)[0] for i in range(2)]
        return [mass[0]*centers[0][j] + mass[1]*centers[1][j]
                for j in range(3)]

    def observe(self, row):
        if type(row) is not dict or set(row) != {
                "id", "source_tag", "observation", "action", "successor",
                "reward", "terminated", "truncated"}:
            raise ValueError("NUM06_ROW_SCHEMA")
        exact = public_row(row["id"], row["observation"], row["action"],
                           row["successor"], row["reward"], row["terminated"],
                           row["truncated"], source_tag=row["source_tag"])
        if row != exact or canonical(row) != canonical(exact):
            raise ValueError("NUM06_NONCANONICAL_ROW")
        if row["id"] in self.seen:
            raise ValueError("NUM06_DUPLICATE_OR_REORDERED_SOURCE")
        if len(self.rows) >= MAX_ROWS:
            raise ValueError("NUM06_CAPACITY")
        before = self.predict(row["observation"], row["action"])
        z = target(row)
        prior = self._prior_mass()
        log_joint = []
        for i in range(2):
            center, variance = self._parameters(i, row["observation"], row["action"])
            loglike = -0.5 * sum((z[k]-center[k])**2 / variance +
                                 math.log(2*math.pi*variance) for k in range(3))
            log_joint.append(math.log(max(prior[i], 1e-300)) + loglike)
        peak = max(log_joint)
        weights = [math.exp(v-peak) for v in log_joint]
        total = sum(weights)
        mass = [w/total for w in weights]
        if len(self.rows) < 100:
            mass = [1.0, 0.0]
        key = self._key(row["observation"], row["action"])
        for i in range(2):
            n, sums = self.banks[i].get(key, [0.0, [0.0, 0.0, 0.0]])
            w = mass[i]
            if w > 0:
                self.banks[i][key] = [n+w, [s+w*z[k] for k,s in enumerate(sums)]]
        self.posterior = mass
        new_active = 1 if mass[1] > 0.8 else 0 if mass[0] > 0.8 else self.active
        if new_active != self.active:
            self.mode_switches.append([len(self.rows)+1, new_active])
            self.active = new_active
        self.seen.add(row["id"])
        self.rows.append(exact)
        return before

    def info(self):
        return {"rows": len(self.rows), "posterior": self.posterior[:],
                "active": self.active, "mode_switches": self.mode_switches[:],
                "regime_1_evidence": sum(v[0] for v in self.banks[1].values()),
                "source_owner_authenticated": False,
                "native_admission": False, "scientific_gain_verified": False}

    def checkpoint(self):
        state = {
            "schema": SCHEMA,
            "params": [self.hazard, self.noise_sigma, self.prior_std],
            "banks": [{k: value for k, value in sorted(bank.items())}
                      for bank in self.banks],
            "posterior": self.posterior,
            "active": self.active,
            "mode_switches": self.mode_switches,
            "rows": self.rows,
            "source_owner_authenticated": False,
            "native_admission": False,
            "scientific_gain_verified": False,
        }
        raw = canonical(state)
        if len(raw) > 300000:
            raise ValueError("NUM06_CHECKPOINT_BYTES")
        return raw

    @classmethod
    def restore(cls, raw, sha256):
        if type(raw) is not bytes or type(sha256) is not str or len(raw) > 300000 or digest(raw) != sha256:
            raise ValueError("NUM06_CHECKPOINT_HASH")
        try:
            state = json.loads(raw)
            if (type(state) is not dict or state["schema"] != SCHEMA or
                    state["source_owner_authenticated"] is not False or
                    state["native_admission"] is not False or
                    state["scientific_gain_verified"] is not False or
                    canonical(state) != raw):
                raise ValueError("NUM06_CHECKPOINT_FORMAT")
            model = cls(hazard=float(state["params"][0]),
                        noise_sigma=float(state["params"][1]),
                        prior_std=float(state["params"][2]))
            for row in state["rows"]:
                model.observe(row)
            if model.checkpoint() != raw:
                raise ValueError("NUM06_CHECKPOINT_REPLAY_MISMATCH")
            return model
        except (KeyError, TypeError, IndexError, OverflowError, RecursionError) as exc:
            raise ValueError("NUM06_CHECKPOINT_FORMAT") from exc


def prequential_score(rows, settings):
    """Rows are already-witnessed public packets, never generated here."""
    model = BayesianTwoBank(hazard=settings[0],
                            noise_sigma=settings[1], prior_std=settings[2])
    total = 0.0
    count = 0
    for row in rows:
        total += error(model.predict(row["observation"], row["action"]), target(row))
        model.observe(row)
        count += 1
    if not count:
        raise ValueError("NUM06_EMPTY_COHORT")
    return total/count


def fit_hyperparameters(fit_cohorts, validation_cohorts):
    """FIT/VALID only. Never inspect held trials or source private phase labels.

    Each cohort is one full publicly witnessed ordered stream, consumed by
    an independent fresh model; ties favor canonical grid order.
    """
    if not fit_cohorts or not validation_cohorts:
        raise ValueError("NUM06_MISSING_FIT_OR_VALID")
    ranked = []
    for settings in HYPER_GRID:
        fit = [prequential_score(rows, settings) for rows in fit_cohorts]
        valid = [prequential_score(rows, settings) for rows in validation_cohorts]
        ranked.append(((sum(fit)/len(fit) + sum(valid)/len(valid))/2, settings))
    ranked.sort(key=lambda x: (x[0], x[1]))
    return {"settings": list(ranked[0][1]), "selection_mse": ranked[0][0],
            "cohort_counts": [len(fit_cohorts), len(validation_cohorts)],
            "grid_size": len(HYPER_GRID), "held_used": False,
            "scientific_gain_verified": False}
