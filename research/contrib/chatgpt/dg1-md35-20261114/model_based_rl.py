"""MD35 empirical history-conditioned physical model-based RL control.

Five public-data bootstrap transition/reward models; exactly forty Bellman
backups over finite physical horizons. No future World.step() or oracle.
"""
import time
import numpy as np
from public_actions import PublicEpisode, require_public_blocks

ENSEMBLE = 5
SEED = 35041
SWEEPS = 40
ALPHA = 1.0
FIT_CPU_CAP = 900.0


class ModelBasedRL:
    def __init__(self):
        self.success = np.zeros((ENSEMBLE, 4, 2, 4), dtype=np.float64)
        self.failure = np.zeros_like(self.success)
        self.diagnostic = np.zeros((ENSEMBLE, 3, 4, 2), dtype=np.float64)
        self.fitted_episodes = 0
        self.fitted_backups = 0
        self._fitted_q = None
        self._local_success = np.zeros((4, 2, 4), dtype=np.float64)
        self._local_failure = np.zeros_like(self._local_success)
        self._local_probe = np.zeros((3, 4, 2), dtype=np.float64)
        self._block_episodes = None
        self.fitting_cpu_seconds = None

    @staticmethod
    def _record(episode, success, failure, diagnostic):
        if type(episode) is not PublicEpisode:
            raise AssertionError("MD35_RL_NONPUBLIC_PHYSICAL_EPISODE")
        c, route = episode.context, episode.route()
        terminal = episode.terminal()
        if terminal[3] == 0.98:
            success[c, route, terminal[2]] += 1
        elif terminal[3] == -0.52:
            failure[c, route, terminal[2]] += 1
        else:
            raise AssertionError("MD35_RL_NONPHYSICAL_TERMINAL")
        diag = episode.diagnostic()
        if diag is not None:
            index = c if diag[0] == 0 else diag[2] if diag[0] == 1 else route
            diagnostic[diag[0], index, diag[4]] += 1

    def fit(self, blocks):
        source = require_public_blocks(blocks, expected_count=384)
        if self.fitted_episodes:
            raise AssertionError("MD35_RL_RETRAIN_FORBIDDEN")
        start = time.process_time()
        rng = np.random.default_rng(SEED)
        # Each member sees only a resampling of the SAME 384 charged blocks.
        for member in range(ENSEMBLE):
            indices = rng.integers(0, len(source), len(source))
            for idx in indices:
                for episode in source[int(idx)]:
                    self._record(episode, self.success[member],
                                 self.failure[member], self.diagnostic[member])
            if time.process_time() - start > FIT_CPU_CAP:
                raise TimeoutError("MD35_RL_FITTING_CPU_CAP")
        self.fitted_episodes = 1536
        # Real finite-horizon Bellman backups are performed, rather than a
        # label-oracle action shortcut. They use fitted public reward rates.
        self._bellman()
        self.fitting_cpu_seconds = time.process_time() - start
        if self.fitting_cpu_seconds > FIT_CPU_CAP:
            raise TimeoutError("MD35_RL_FITTING_CPU_CAP")
        return self

    def begin_block(self):
        self._local_success.fill(0.0)
        self._local_failure.fill(0.0)
        self._local_probe.fill(0.0)
        self._block_episodes = 0

    def predict_target(self, context, route):
        if self._block_episodes is None:
            raise AssertionError("MD35_RL_BLOCK_BOUNDARY_REQUIRED")
        if type(context) is not int or context not in range(4) or route not in (0, 1):
            raise AssertionError("MD35_RL_INVALID_PUBLIC_ACTION")
        # Beta(1,1) posterior for observed action-success rates with
        # retained within-block (but never global-heldout) scratch evidence.
        successes = self.success[:, context, route, :] + self._local_success[context, route, :]
        failures = self.failure[:, context, route, :] + self._local_failure[context, route, :]
        rates = (successes + ALPHA) / (successes + failures + 2 * ALPHA)
        probs = rates / rates.sum(axis=1, keepdims=True)
        return tuple(float(x) for x in probs.mean(axis=0))

    @staticmethod
    def _terminal_value(p):
        # Bellman boundary: real terminal reward +0.98 or -0.52.
        no_probe = 1.5 * max(p) - 0.52
        # A terminal parity observation is physically binary and costs 0.09.
        with_probe = 1.5 * (max(p[0], p[2]) + max(p[1], p[3])) - 0.52 - 0.09
        return max(no_probe, with_probe)

    def _bellman(self):
        if self.fitted_episodes != 1536:
            raise AssertionError("MD35_RL_UNTRAINED_BACKUPS")
        self.begin_block()
        # Terminal, optional paid terminal-parity intervention, route and
        # precursor values are backed up through the finite physical horizon.
        q_terminal = np.zeros((4, 2, 4), dtype=np.float64)
        q_diagnostic = np.zeros((4, 2), dtype=np.float64)
        q_route = np.zeros((4, 2), dtype=np.float64)
        q_precursor = np.zeros(4, dtype=np.float64)
        for _ in range(SWEEPS):
            for context in range(4):
                for route in (0, 1):
                    p = self.predict_target(context, route)
                    q_terminal[context, route] = [
                        1.5 * p[guess] - 0.52 for guess in range(4)
                    ]
                    # A real diagnostic costs 0.09 and reveals only parity.
                    q_diagnostic[context, route] = (
                        1.5 * (max(p[0], p[2]) + max(p[1], p[3]))
                        - 0.52 - 0.09
                    )
                    continuation = max(
                        float(q_terminal[context, route].max()),
                        q_diagnostic[context, route],
                    )
                    q_route[context, route] = continuation - (
                        0.02 if route == 0 else 0.05
                    )
                q_precursor[context] = -0.02 + q_route[context].max()
            if (not np.isfinite(q_precursor).all() or
                    not np.isfinite(q_route).all()):
                raise AssertionError("MD35_RL_INVALID_BELLMAN_VALUE")
        self._fitted_q = q_route.copy()
        self.fitted_backups = SWEEPS
        self.begin_block()

    def plan_route(self, context):
        if self.fitted_backups != SWEEPS or self._fitted_q is None:
            raise AssertionError("MD35_RL_BELLMAN_NOT_FITTED")
        if type(context) is not int or context not in range(4):
            raise AssertionError("MD35_RL_INVALID_PUBLIC_ACTION")
        if self._block_episodes == 0:
            values = self._fitted_q[context]
        else:
            # History-conditioned replanning from charged within-block data.
            values = [
                (-0.02 if r == 0 else -0.05) +
                self._terminal_value(self.predict_target(context, r))
                for r in (0, 1)
            ]
        return int(values[1] > values[0])

    def plan_terminal(self, context, route, parity_bit=None):
        p = self.predict_target(context, route)
        if parity_bit is not None:
            if parity_bit not in (0, 1):
                raise AssertionError("MD35_RL_INVALID_PUBLIC_BIT")
            choices = (0, 2) if parity_bit == 0 else (1, 3)
            return False, max(choices, key=lambda i: (p[i], -i))
        best = max(range(4), key=lambda i: (p[i], -i))
        gain = (max(p[0], p[2]) + max(p[1], p[3]) - p[best]) * 1.5
        return gain > 0.09, best

    def update(self, episode):
        if self._block_episodes is None or self._block_episodes >= 4:
            raise AssertionError("MD35_RL_PUBLIC_BLOCK_REQUIRED")
        if type(episode) is not PublicEpisode or episode.context != self._block_episodes:
            raise AssertionError("MD35_RL_BLOCK_CONTEXT_DRIFT")
        self._record(episode, self._local_success,
                     self._local_failure, self._local_probe)
        self._block_episodes += 1

    def checkpoint(self):
        if self.fitted_episodes != 1536 or self.fitted_backups != SWEEPS:
            raise AssertionError("MD35_RL_UNTRAINED_CHECKPOINT")
        return {
            "schema": "md35.empirical-fitted-q-public.v1",
            "ensemble": ENSEMBLE, "seed": SEED, "sweeps": SWEEPS,
            "smoothing": ALPHA, "fitted_episodes": self.fitted_episodes,
            "success": self.success.tolist(), "failure": self.failure.tolist(),
            "diagnostic": self.diagnostic.tolist(),
        }

    @classmethod
    def restore(cls, checkpoint):
        if (type(checkpoint) is not dict or
                checkpoint.get("schema") != "md35.empirical-fitted-q-public.v1" or
                checkpoint.get("ensemble") != ENSEMBLE or
                checkpoint.get("seed") != SEED or
                checkpoint.get("sweeps") != SWEEPS or
                checkpoint.get("smoothing") != ALPHA or
                checkpoint.get("fitted_episodes") != 1536):
            raise AssertionError("MD35_RL_COLD_CHECKPOINT_INVALID")
        obj = cls()
        obj.success = np.asarray(checkpoint["success"], dtype=np.float64)
        obj.failure = np.asarray(checkpoint["failure"], dtype=np.float64)
        obj.diagnostic = np.asarray(checkpoint["diagnostic"], dtype=np.float64)
        if (obj.success.shape != (ENSEMBLE, 4, 2, 4) or
                obj.failure.shape != (ENSEMBLE, 4, 2, 4) or
                obj.diagnostic.shape != (ENSEMBLE, 3, 4, 2) or
                any(np.any(~np.isfinite(x)) or np.any(x < 0) for x in
                    (obj.success, obj.failure, obj.diagnostic))):
            raise AssertionError("MD35_RL_COLD_MODEL_INVALID")
        obj.fitted_episodes = 1536
        obj._bellman()
        if obj.checkpoint() != checkpoint:
            raise AssertionError("MD35_RL_COLD_BYTES_DIFFER")
        return obj
