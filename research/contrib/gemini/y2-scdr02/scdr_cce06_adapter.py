"""
SCDR-CCE06 Policy Adapter v2 (Cycles 11-17):
Implements the exact y2-cce06 `calibration_policy_frontier` on-policy contract
(`fit`, `start`, `choose`, `update`, `posterior`, `spent`, `actions_taken`, `pending`)
plus:
1. 2-Step Confirmed Coupled Broadcast Changepoint Hazard (eliminates stationary probe overshoot
   while preserving rapid wake-up after silent mid-episode shifts).
2. Multi-Sheet Hierarchical Posterior (`fit_regimes`) for silent cross-family + permuted shifts.
3. Goal-Directed Consequence Lookahead (`choose_for_goal`) using transferred causal contracts.

Pure Python stdlib, strictly public-only interface, zero edits to y2-cce06.
"""

from __future__ import annotations

from scdr_sinkhorn_v6 import (
    FreshOnlineKBit,
    GeneralSheetKBit,
    parse_public_event,
    sinkhorn_sub_stochastic,
)

ACTIONS = (0, 1, 2)
COST = {0: 0, 1: 1, 2: 1}


class SCDRCCE06PolicyAdapter:
    """
    Plug-compatible on-policy adapter for y2-cce06's `calibration_policy_frontier._episode`.
    Supports both single-sheet `fit(train)` and multi-sheet `fit_regimes(regime_traces)`.
    """

    def __init__(
        self,
        *,
        hazard: float = 0.015,
        outer_hazard: float = 0.015,
        probe_penalty: float = 0.012,
        sinkhorn_iters: int = 3,
        broadcast_pulse: float = 0.35,
    ):
        self.hazard = hazard
        self.outer_hazard = outer_hazard
        self.probe_penalty = probe_penalty
        self.sinkhorn_iters = sinkhorn_iters
        self.broadcast_pulse = broadcast_pulse

        self.sheets: list[GeneralSheetKBit] = []
        self.fitted = False

        # Hierarchical beliefs:
        # outer_beliefs: [sheet_0, ..., sheet_{S-1}, OOD_fresh]
        self.outer_beliefs: list[float] = []
        # inner_beliefs[si][action] = [Role_0, Role_1, Role_2, Fresh_a]
        self.inner_beliefs: list[list[list[float]]] = []
        self.fresh: FreshOnlineKBit | None = None

        self.current: list[int] | None = None
        self.pending: tuple[list[int], int] | None = None
        self.budget = 0
        self.spent = 0
        self.actions_taken = 0
        self._surprise_window: list[int] = []
        self._last_broadcast_step: int = -100

    def fit(self, train: list[list[dict]]) -> "SCDRCCE06PolicyAdapter":
        if not train:
            raise ValueError("SCDR_ADAPTER_EMPTY_TRAIN")
        sheet = GeneralSheetKBit(2, 3)
        for seq in train:
            if not seq:
                raise ValueError("SCDR_ADAPTER_EMPTY_SEQUENCE")
            sheet.fit(seq)
        self.sheets = [sheet]
        self.fitted = True
        return self

    def fit_regimes(self, regime_traces: list[list[dict]]) -> "SCDRCCE06PolicyAdapter":
        """Fit a multi-sheet causal library from multiple distinct regimes (one sheet per regime)."""
        if not regime_traces:
            raise ValueError("SCDR_ADAPTER_EMPTY_REGIMES")
        self.sheets = []
        for tr in regime_traces:
            if not tr:
                raise ValueError("SCDR_ADAPTER_EMPTY_SEQUENCE")
            s = GeneralSheetKBit(2, 3)
            s.fit(tr)
            self.sheets.append(s)
        self.fitted = True
        return self

    def start(self, observed: list[int], *, paid_budget: int) -> None:
        if (
            not self.fitted
            or self.pending is not None
            or type(paid_budget) is not int
            or not (0 <= paid_budget <= 100000)
        ):
            raise ValueError("SCDR_ADAPTER_INVALID_START")
        if len(observed) != 2 or observed[0] not in (0, 1) or observed[1] not in (0, 1):
            raise ValueError("SCDR_ADAPTER_INVALID_OBS")

        n_s = len(self.sheets)
        # Slight prior preference for stored sheets over OOD fresh
        raw_outer = [1.0] * n_s + [0.4]
        so = sum(raw_outer)
        self.outer_beliefs = [x / so for x in raw_outer]

        init_row = [1.0 / 3.6, 1.0 / 3.6, 1.0 / 3.6, 0.6 / 3.6]
        s0 = sum(init_row)
        init_row = [x / s0 for x in init_row]
        self.inner_beliefs = [[list(init_row) for _ in range(3)] for _ in range(n_s)]
        self.fresh = FreshOnlineKBit(2, 3)

        self.current = list(observed)
        self.pending = None
        self.budget = paid_budget
        self.spent = 0
        self.actions_taken = 0
        self._surprise_window = []
        self._last_broadcast_step = -100

    def _sheet_effective_rows(self, si: int) -> list[list[float]]:
        return sinkhorn_sub_stochastic(self.inner_beliefs[si], 3, iters=self.sinkhorn_iters)

    def _sheet_action_pred(self, si: int, o_code: int, a: int) -> tuple[list[float], list[list[float]], list[float]]:
        assert self.fresh is not None
        aws = self._sheet_effective_rows(si)[a]
        fresh_p = self.fresh.predict(o_code, a)
        rpreds = [self.sheets[si].predict(None, o_code, r) for r in range(3)] + [fresh_p]
        mix = [0.0, 0.0, 0.0, 0.0]
        for ri in range(4):
            w = aws[ri]
            rp = rpreds[ri]
            for c in range(4):
                mix[c] += w * rp[c]
        return mix, rpreds, aws

    def _fresh_brier_gain(self, o_code: int, a: int) -> float:
        assert self.fresh is not None
        c = self.fresh.counts[o_code][a]
        s = sum(c)
        p = [x / s for x in c]
        p0, p1 = p[2] + p[3], p[1] + p[3]
        return 0.5 * (p0 * (1.0 - p0) + p1 * (1.0 - p1)) / ((s + 1.0) ** 2) * 4.0

    def active_sheet_index(self) -> int:
        """Return MAP active sheet index (or -1 if OOD_fresh dominates)."""
        best = max(range(len(self.outer_beliefs)), key=lambda i: self.outer_beliefs[i])
        return best if best < len(self.sheets) else -1

    def posterior(self, observed: list[int], action: int) -> tuple[float, float, float, float]:
        if not self.fitted or self.fresh is None or type(action) is not int or action not in ACTIONS:
            raise ValueError("SCDR_ADAPTER_NOT_READY_OR_BAD_ACTION")
        if len(observed) != 2 or observed[0] not in (0, 1) or observed[1] not in (0, 1):
            raise ValueError("SCDR_ADAPTER_INVALID_OBS")
        o_code = (int(observed[0]) << 1) | int(observed[1])
        fresh_p = self.fresh.predict(o_code, action)
        mix = [0.0, 0.0, 0.0, 0.0]
        for si in range(len(self.sheets)):
            sp, _, _ = self._sheet_action_pred(si, o_code, action)
            ow = self.outer_beliefs[si]
            for c in range(4):
                mix[c] += ow * sp[c]
        ow_ood = self.outer_beliefs[-1]
        for c in range(4):
            mix[c] += ow_ood * fresh_p[c]
        tot = sum(mix)
        return tuple(x / tot for x in mix)  # type: ignore[return-value]

    def _evgi_for_action(self, o_code: int, a: int) -> tuple[float, float]:
        """Compute total expected multichannel disagreement (EVGI) across (sheet, role) hypotheses + w_fresh."""
        assert self.fresh is not None
        fresh_p = self.fresh.predict(o_code, a)
        # Flatten all (sheet, role) components weighted by outer * inner
        comp_w: list[float] = []
        comp_p: list[list[float]] = []
        w_fresh_total = self.outer_beliefs[-1]
        for si in range(len(self.sheets)):
            ow = self.outer_beliefs[si]
            _, rpreds, aws = self._sheet_action_pred(si, o_code, a)
            w_fresh_total += ow * aws[3]
            for ri in range(4):
                comp_w.append(ow * aws[ri])
                comp_p.append(rpreds[ri])
        comp_w.append(self.outer_beliefs[-1])
        comp_p.append(fresh_p)

        mix = [sum(comp_w[i] * comp_p[i][c] for i in range(len(comp_w))) for c in range(4)]
        m0, m1 = mix[2] + mix[3], mix[1] + mix[3]
        evgi = sum(
            comp_w[i] * 0.5 * (((p[2] + p[3]) - m0) ** 2 + ((p[1] + p[3]) - m1) ** 2)
            for i, p in enumerate(comp_p)
        )
        return evgi, w_fresh_total

    def choose(self) -> int:
        if self.current is None or self.pending is not None or self.fresh is None:
            raise ValueError("SCDR_ADAPTER_PENDING_OR_NOT_STARTED")
        o_code = (int(self.current[0]) << 1) | int(self.current[1])
        avail = [a for a in ACTIONS if self.spent + COST[a] <= self.budget]
        best_a, best_u = 0, -1e9
        for a in avail:
            evgi, w_fresh = self._evgi_for_action(o_code, a)
            u = evgi + w_fresh * self._fresh_brier_gain(o_code, a) - self.probe_penalty * COST[a]
            if u > best_u:
                best_u, best_a = u, a
        self.pending = (self.current[:], best_a)
        self.spent += COST[best_a]
        return best_a

    def choose_for_goal(self, goal_obs: list[int], *, explore_weight: float = 0.6) -> int:
        """
        Goal-directed 1-step consequence lookahead using transferred causal contracts:
        maximizes P(next_obs == goal | obs, a) + explore_weight * EVGI(obs, a).
        """
        if self.current is None or self.pending is not None or self.fresh is None:
            raise ValueError("SCDR_ADAPTER_PENDING_OR_NOT_STARTED")
        o_code = (int(self.current[0]) << 1) | int(self.current[1])
        g_code = (int(goal_obs[0]) << 1) | int(goal_obs[1])
        avail = [a for a in ACTIONS if self.spent + COST[a] <= self.budget]
        best_a, best_u = 0, -1e9
        for a in avail:
            p = self.posterior(self.current, a)
            evgi, w_fresh = self._evgi_for_action(o_code, a)
            u = p[g_code] + explore_weight * (evgi + w_fresh * self._fresh_brier_gain(o_code, a))
            if u > best_u:
                best_u, best_a = u, a
        self.pending = (self.current[:], best_a)
        self.spent += COST[best_a]
        return best_a

    def update(self, event: dict) -> None:
        if self.pending is None or self.fresh is None:
            raise ValueError("SCDR_ADAPTER_NO_PENDING_ACTION")
        po, pa, pno = parse_public_event(event, 4, 3)
        exp_obs, exp_a = self.pending
        if event["observation"] != exp_obs or pa != exp_a:
            raise ValueError("SCDR_ADAPTER_EVENT_MISMATCH")

        n_s = len(self.sheets)
        fresh_p = self.fresh.predict(po, pa)
        old_outer_map = self.active_sheet_index()
        old_inner_maps = [max(range(4), key=lambda ri: self.inner_beliefs[si][pa][ri]) for si in range(n_s)]

        # Pre-update predictive probability of observed outcome (for 2-step surprise confirmation)
        pred_prob = self.posterior(event["observation"], pa)[pno]

        # 1. Update outer beliefs across sheets + OOD_fresh with outer hazard floor
        sheet_liks = []
        sheet_rpreds = []
        for si in range(n_s):
            sp, rpreds, _ = self._sheet_action_pred(si, po, pa)
            sheet_liks.append(max(1e-6, sp[pno]))
            sheet_rpreds.append(rpreds)
        outer_post = [self.outer_beliefs[si] * sheet_liks[si] for si in range(n_s)] + [
            self.outer_beliefs[-1] * max(1e-6, fresh_p[pno])
        ]
        os_tot = sum(outer_post)
        outer_post = [x / os_tot for x in outer_post]
        o_unif = 1.0 / (n_s + 1)
        self.outer_beliefs = [(1.0 - self.outer_hazard) * x + self.outer_hazard * o_unif for x in outer_post]

        # 2. Update inner per-action beliefs for each sheet with hazard floor
        any_map_flip = False
        for si in range(n_s):
            rpreds = sheet_rpreds[si]
            post = [self.inner_beliefs[si][pa][ri] * max(1e-6, rpreds[ri][pno]) for ri in range(4)]
            ps = sum(post)
            post = [x / ps for x in post]
            self.inner_beliefs[si][pa] = [(1.0 - self.hazard) * x + self.hazard * 0.25 for x in post]
            new_map = max(range(4), key=lambda ri: self.inner_beliefs[si][pa][ri])
            if new_map != old_inner_maps[si] and self.outer_beliefs[si] > 0.35:
                any_map_flip = True

        new_outer_map = self.active_sheet_index()
        if new_outer_map != old_outer_map and new_outer_map != -1:
            any_map_flip = True

        # 3. 2-Step Confirmed Coupled Broadcast Hazard (eliminates stationary single-noise overshoot!)
        is_surprise = 1 if (pred_prob < 0.22 or any_map_flip) else 0
        self._surprise_window.append(is_surprise)
        if len(self._surprise_window) > 4:
            self._surprise_window.pop(0)

        if (
            self.hazard > 0.0
            and self.actions_taken >= 12
            and sum(self._surprise_window) >= 2
            and (self.actions_taken - self._last_broadcast_step) >= 8
        ):
            pulse = self.broadcast_pulse
            for si in range(n_s):
                for other_a in ACTIONS:
                    if other_a != pa:
                        self.inner_beliefs[si][other_a] = [
                            (1.0 - pulse) * x + pulse * 0.25 for x in self.inner_beliefs[si][other_a]
                        ]
            self._last_broadcast_step = self.actions_taken
            self._surprise_window.clear()

        self.fresh.update(po, pa, pno)
        self.pending = None
        self.actions_taken += 1
        self.current = list(event["next_observation"])
