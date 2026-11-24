"""
SCDR-Planner-v8 (Cycles 18-19):
Exact H-step Value Iteration (dynamic programming) over SCDR's Hazard-Floored Sinkhorn
transferred transition model for arbitrary (n_bits, n_actions) unfamiliar worlds.

Combines:
- Sub-Stochastic Sinkhorn Soft-Exclusion (O(|A|^2), un-competed Fresh_a novelty column)
- Bayesian Changepoint Hazard Flooring + 2-Step Confirmed Coupled Broadcast Hazard
- Exact H-step Bellman Value Iteration + EVGI epistemic exploration bonus

Pure Python stdlib, strictly public-only interface.
"""

from __future__ import annotations

from scdr_sinkhorn_v6 import (
    FreshOnlineKBit,
    GeneralSheetKBit,
    sinkhorn_sub_stochastic,
)


class SCDRMultiStepPlannerV8:
    """Multi-step causal planner over Sinkhorn-transferred world models."""

    def __init__(
        self,
        sheet: GeneralSheetKBit,
        *,
        horizon: int = 3,
        gamma: float = 0.90,
        hazard: float = 0.015,
        broadcast_pulse: float = 0.35,
        explore_weight: float = 0.60,
        sinkhorn_iters: int = 3,
    ):
        self.sheet = sheet
        self.n_bits = sheet.n_bits
        self.n_states = sheet.n_states
        self.n_actions = sheet.n_actions
        self.horizon = horizon
        self.gamma = gamma
        self.hazard = hazard
        self.broadcast_pulse = broadcast_pulse
        self.explore_weight = explore_weight
        self.sinkhorn_iters = sinkhorn_iters

        self.beliefs: list[list[float]] = []
        self.fresh: FreshOnlineKBit | None = None
        self.steps = 0
        self._surprise_window: list[int] = []
        self._last_broadcast = -100
        self.reset_episode()

    def reset_episode(self) -> None:
        n_a = self.n_actions
        init_row = [1.0 / (n_a + 0.6)] * n_a + [0.6 / (n_a + 0.6)]
        s0 = sum(init_row)
        init_row = [x / s0 for x in init_row]
        self.beliefs = [list(init_row) for _ in range(n_a)]
        self.fresh = FreshOnlineKBit(self.n_bits, n_a)
        self.steps = 0
        self._surprise_window = []
        self._last_broadcast = -100

    def _effective_rows(self) -> list[list[float]]:
        return sinkhorn_sub_stochastic(self.beliefs, self.n_actions, iters=self.sinkhorn_iters)

    def _transition_tensor(self, eff_rows: list[list[float]]) -> list[list[list[float]]]:
        """Build current expected transition matrix T[s][a][s'] in O(|S|*|A|^2)."""
        assert self.fresh is not None
        T = []
        for s in range(self.n_states):
            row_s = []
            for a in range(self.n_actions):
                aws = eff_rows[a]
                fp = self.fresh.predict(s, a)
                mix = [0.0] * self.n_states
                for r in range(self.n_actions):
                    w = aws[r]
                    if w > 1e-6:
                        rp = self.sheet.predict(None, s, r)
                        for ns in range(self.n_states):
                            mix[ns] += w * rp[ns]
                wf = aws[self.n_actions]
                if wf > 1e-6:
                    for ns in range(self.n_states):
                        mix[ns] += wf * fp[ns]
                row_s.append(mix)
            T.append(row_s)
        return T

    def _evgi_at(self, eff_rows: list[list[float]], s: int, a: int) -> float:
        assert self.fresh is not None
        aws = eff_rows[a]
        rpreds = [self.sheet.predict(None, s, r) for r in range(self.n_actions)] + [self.fresh.predict(s, a)]
        mix = [sum(aws[i] * rpreds[i][ns] for i in range(self.n_actions + 1)) for ns in range(self.n_states)]
        # Total variation / L2 epistemic disagreement across hypotheses
        evgi = 0.0
        for i, rp in enumerate(rpreds):
            w = aws[i]
            if w > 1e-6:
                evgi += w * sum((rp[ns] - mix[ns]) ** 2 for ns in range(self.n_states))
        # Add within-fresh uncertainty bonus weighted by fresh mass
        c = self.fresh.counts[s][a]
        tot = sum(c)
        evgi += aws[self.n_actions] * (1.0 / (tot + 1.0))
        return evgi

    def choose_action(self, obs_code: int, goal_code: int) -> int:
        eff_rows = self._effective_rows()
        T = self._transition_tensor(eff_rows)

        # Exact H-step Bellman Value Iteration
        V = [1.0 if s == goal_code else 0.0 for s in range(self.n_states)]
        for _ in range(max(0, self.horizon - 1)):
            new_V = [0.0] * self.n_states
            for s in range(self.n_states):
                best_q = max(
                    sum(T[s][a][ns] * V[ns] for ns in range(self.n_states))
                    for a in range(self.n_actions)
                )
                new_V[s] = (1.0 if s == goal_code else 0.0) + self.gamma * best_q
            V = new_V

        best_a = 0
        best_score = -1e9
        for a in range(self.n_actions):
            q_val = sum(T[obs_code][a][ns] * V[ns] for ns in range(self.n_states))
            score = q_val + self.explore_weight * self._evgi_at(eff_rows, obs_code, a)
            if score > best_score:
                best_score = score
                best_a = a
        return best_a

    def update(self, obs_code: int, action: int, next_obs_code: int) -> None:
        assert self.fresh is not None
        n_cols = self.n_actions + 1
        old_map = max(range(n_cols), key=lambda r: self.beliefs[action][r])
        eff_rows = self._effective_rows()
        aws = eff_rows[action]
        rpreds = [self.sheet.predict(None, obs_code, r) for r in range(self.n_actions)] + [
            self.fresh.predict(obs_code, action)
        ]
        pred_prob = sum(aws[i] * rpreds[i][next_obs_code] for i in range(n_cols))

        post = [self.beliefs[action][ri] * max(1e-6, rpreds[ri][next_obs_code]) for ri in range(n_cols)]
        ps = sum(post)
        post = [x / ps for x in post]
        unif = 1.0 / n_cols
        self.beliefs[action] = [(1.0 - self.hazard) * x + self.hazard * unif for x in post]
        new_map = max(range(n_cols), key=lambda r: self.beliefs[action][r])

        # 2-Step Confirmed Broadcast Changepoint Hazard
        is_surp = 1 if (pred_prob < 0.15 or new_map != old_map) else 0
        self._surprise_window.append(is_surp)
        if len(self._surprise_window) > 4:
            self._surprise_window.pop(0)

        if (
            self.hazard > 0.0
            and self.steps >= 15
            and sum(self._surprise_window) >= 2
            and (self.steps - self._last_broadcast) >= 10
        ):
            pulse = self.broadcast_pulse
            for other_a in range(self.n_actions):
                if other_a != action:
                    self.beliefs[other_a] = [(1.0 - pulse) * x + pulse * unif for x in self.beliefs[other_a]]
            self._last_broadcast = self.steps
            self._surprise_window.clear()

        self.fresh.update(obs_code, action, next_obs_code)
        self.steps += 1
