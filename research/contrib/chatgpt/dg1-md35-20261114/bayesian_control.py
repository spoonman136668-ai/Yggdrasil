"""MD35 4096-particle, factorized latent Bayesian physical-response control.

Fitted statistics and block-local particle posteriors arise only from public
charged outcomes. Latent arrays are model hypotheses sampled independently
of the harness's inaccessible laws, never hidden labels.
"""
import copy
import numpy as np

from public_actions import PublicEpisode, require_public_blocks
from negative_supervision import REAL, SHUFFLED, training_targets

PARTICLES = 4096
PARTICLE_SEED = 35031
ALPHA = 1.0


def _valid_episode(episode):
    if type(episode) is not PublicEpisode:
        raise AssertionError("MD35_BAYES_NONPUBLIC_EPISODE")
    return episode


class BayesianControl:
    def __init__(self):
        self.prior_success = np.zeros((4, 2, 4), dtype=np.float64)
        self.prior_failure = np.zeros((4, 2, 4), dtype=np.float64)
        self.prior_probe = np.zeros((3, 4, 2), dtype=np.float64)
        self.fitted_episodes = 0
        self.training_target_mode = REAL
        self._rng = np.random.default_rng(PARTICLE_SEED)
        self._hypotheses = None
        self._weights = None
        self._block_episodes = 0
        self._last_block_events = ()

    def fit(self, blocks, *, shuffled_training=False):
        # The protected cohort is not created by this class; the entrypoint
        # and ledger/first-use custody must authorize collection separately.
        source = require_public_blocks(blocks, expected_count=384)
        mode = SHUFFLED if shuffled_training is True else REAL
        if type(shuffled_training) is not bool:
            raise AssertionError("MD35_BAYES_INVALID_SHUFFLE_SELECTOR")
        labels = training_targets(source, mode=mode)
        if self.fitted_episodes:
            raise AssertionError("MD35_BAYES_RETRAIN_FORBIDDEN")
        for block, label_block in zip(source, labels):
            for ep, label in zip(block, label_block):
                c, r = ep.context, ep.route()
                guess = ep.terminal()[2]
                if label.terminal_reward == 0.98:
                    self.prior_success[c, r, guess] += 1
                elif label.terminal_reward == -0.52:
                    self.prior_failure[c, r, guess] += 1
                else:
                    raise AssertionError("MD35_BAYES_INVALID_TERMINAL_REWARD")
                d = ep.diagnostic()
                if d is not None:
                    key = (d[0], c if d[0] == 0 else d[2] if d[0] == 1 else r)
                    self.prior_probe[key[0], key[1], label.diagnostic_bit] += 1
                self.fitted_episodes += 1
        if self.fitted_episodes != 1536:
            raise AssertionError("MD35_BAYES_TRAIN_COUNT_MISMATCH")
        self.training_target_mode = mode
        return self

    def begin_block(self):
        # All structural permutations are possible hypotheses; no source
        # hidden permutation or family list enters the model.
        self._hypotheses = {
            name: np.argsort(self._rng.random((PARTICLES, 4)), axis=1)
            for name in ("encoder", "route", "decoder")
        }
        self._hypotheses["offset"] = self._rng.integers(0, 4, PARTICLES)
        self._hypotheses["changed"] = self._rng.integers(0, 2, PARTICLES)
        self._weights = np.full(PARTICLES, 1.0 / PARTICLES, dtype=np.float64)
        self._block_episodes = 0
        self._last_block_events = ()

    def _ensure_block(self):
        if self._hypotheses is None:
            raise AssertionError("MD35_BAYES_BLOCK_BOUNDARY_REQUIRED")

    def _latent(self, context, route):
        self._ensure_block()
        if type(context) is not int or context not in range(4) or route not in (0, 1):
            raise AssertionError("MD35_BAYES_ILLEGAL_PUBLIC_DECISION")
        idx = np.arange(PARTICLES)
        h = self._hypotheses["encoder"][:, context]
        x = (self._hypotheses["route"][idx, h] + route) % 4
        y = (self._hypotheses["decoder"][idx, x] +
             self._hypotheses["offset"] + self._hypotheses["changed"]) % 4
        return h, x, y

    def predict_target(self, context, route):
        """Marginal four-way terminal posterior, no private law access."""
        _, _, y = self._latent(context, route)
        # Laplace/Dirichlet learned marginal acts as a source-family prior;
        # posterior particles express within-block intervention evidence.
        empirical = ((self.prior_success[context, route] + ALPHA) /
                     (self.prior_success[context, route] +
                      self.prior_failure[context, route] + 2 * ALPHA))
        probs = np.bincount(y, weights=self._weights, minlength=4) * empirical
        s = float(probs.sum())
        if not np.isfinite(s) or s <= 0:
            raise AssertionError("MD35_BAYES_INVALID_POSTERIOR")
        return tuple(float(x / s) for x in probs)

    def update(self, episode):
        ep = _valid_episode(episode)
        self._ensure_block()
        if self._block_episodes >= 4 or ep.context != self._block_episodes:
            raise AssertionError("MD35_BAYES_PUBLIC_CONTEXT_OR_BLOCK_DRIFT")
        route = ep.route()
        h, x, y = self._latent(ep.context, route)
        diagnostic = ep.diagnostic()
        if diagnostic is not None:
            stage, _, channel, _, bit = diagnostic
            if stage == 0:
                hypothesis = h % 2
            elif stage == 1:
                # Route diagnostic is observed before a separate route choice;
                # its channel 0 or 1 is the *probed* route, not the chosen one.
                idx = np.arange(PARTICLES)
                hypothesis = ((self._hypotheses["route"][idx, h] +
                               channel) % 4) % 2
            elif stage == 2:
                hypothesis = y % 2
            else:
                raise AssertionError("MD35_BAYES_UNKNOWN_PAID_STAGE")
            self._condition(hypothesis == bit)
        terminal = ep.terminal()
        self._condition((y == terminal[2]) if terminal[3] == 0.98
                        else (y != terminal[2]))
        self._block_episodes += 1
        self._last_block_events += (ep.trace_sha256,)

    def _condition(self, matching):
        # Beta(1,1) one charged binary piece of evidence: 2/3 vs 1/3.
        self._weights *= np.where(matching, 2.0, 1.0)
        total = self._weights.sum()
        if not np.isfinite(total) or total <= 0:
            raise AssertionError("MD35_BAYES_POSTERIOR_COLLAPSE")
        self._weights /= total

    def checkpoint(self):
        if self.fitted_episodes != 1536:
            raise AssertionError("MD35_BAYES_NOT_TRAINED")
        return {
            "schema": "md35.bayes-4096-public-latent.v1",
            "particle_seed": PARTICLE_SEED,
            "particle_cap": PARTICLES,
            "dirichlet_alpha": ALPHA,
            "fitted_public_episodes": self.fitted_episodes,
            "training_target_mode": self.training_target_mode,
            "success": self.prior_success.tolist(),
            "failure": self.prior_failure.tolist(),
            "probe": self.prior_probe.tolist(),
        }

    @classmethod
    def restore(cls, checkpoint):
        if (type(checkpoint) is not dict or
                checkpoint.get("schema") != "md35.bayes-4096-public-latent.v1" or
                checkpoint.get("particle_seed") != PARTICLE_SEED or
                checkpoint.get("particle_cap") != PARTICLES or
                checkpoint.get("dirichlet_alpha") != ALPHA or
                checkpoint.get("fitted_public_episodes") != 1536 or
                checkpoint.get("training_target_mode") not in (REAL, SHUFFLED)):
            raise AssertionError("MD35_BAYES_COLD_CHECKPOINT_INVALID")
        obj = cls()
        obj.prior_success = np.asarray(checkpoint["success"], dtype=np.float64)
        obj.prior_failure = np.asarray(checkpoint["failure"], dtype=np.float64)
        obj.prior_probe = np.asarray(checkpoint["probe"], dtype=np.float64)
        if (obj.prior_success.shape != (4, 2, 4) or
                obj.prior_failure.shape != (4, 2, 4) or
                obj.prior_probe.shape != (3, 4, 2) or
                any(np.any(counts < 0) or
                    np.any(~np.isfinite(counts)) for counts in
                    (obj.prior_success, obj.prior_failure, obj.prior_probe))):
            raise AssertionError("MD35_BAYES_COLD_COUNTS_INVALID")
        obj.fitted_episodes = 1536
        obj.training_target_mode = checkpoint["training_target_mode"]
        if obj.checkpoint() != checkpoint:
            raise AssertionError("MD35_BAYES_COLD_BYTES_DIFFER")
        return obj
