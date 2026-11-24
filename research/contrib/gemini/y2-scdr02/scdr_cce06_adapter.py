"""
SCDR-CCE06 Policy Adapter (Cycles 11-13):
Implements the exact y2-cce06 `calibration_policy_frontier` on-policy contract
(`fit`, `start`, `choose`, `update`, `posterior`, `spent`, `actions_taken`, `pending`)
using Bayesian Changepoint Hazard-Floored Sinkhorn + EVGI Adaptive Re-Probing.

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
    Combines:
    - Factorized per-action role beliefs with Bayesian Changepoint Hazard Flooring (h=0.015)
    - 3-iteration Sub-Stochastic Sinkhorn Soft-Exclusion (un-competed Fresh_a novelty column)
    - EVGI + w_fresh Dirichlet Brier-reduction probing utility (wakes up paid probes on silent
      mid-episode shifts and shuts them off once locked).
    """

    def __init__(
        self,
        *,
        hazard: float = 0.015,
        probe_penalty: float = 0.012,
        sinkhorn_iters: int = 3,
    ):
        self.hazard = hazard
        self.probe_penalty = probe_penalty
        self.sinkhorn_iters = sinkhorn_iters
        self.sheet: GeneralSheetKBit | None = None
        self.fitted = False

        self.beliefs: list[list[float]] = []
        self.fresh: FreshOnlineKBit | None = None
        self.current: list[int] | None = None
        self.pending: tuple[list[int], int] | None = None
        self.budget = 0
        self.spent = 0
        self.actions_taken = 0

    def fit(self, train: list[list[dict]]) -> "SCDRCCE06PolicyAdapter":
        if not train:
            raise ValueError("SCDR_ADAPTER_EMPTY_TRAIN")
        sheet = GeneralSheetKBit(2, 3)
        for seq in train:
            if not seq:
                raise ValueError("SCDR_ADAPTER_EMPTY_SEQUENCE")
            sheet.fit(seq)
        self.sheet = sheet
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
        init_row = [1.0 / 3.6, 1.0 / 3.6, 1.0 / 3.6, 0.6 / 3.6]
        s0 = sum(init_row)
        init_row = [x / s0 for x in init_row]
        self.beliefs = [list(init_row) for _ in range(3)]
        self.fresh = FreshOnlineKBit(2, 3)
        self.current = list(observed)
        self.pending = None
        self.budget = paid_budget
        self.spent = 0
        self.actions_taken = 0

    def _effective_rows(self) -> list[list[float]]:
        return sinkhorn_sub_stochastic(self.beliefs, 3, iters=self.sinkhorn_iters)

    def _role_preds(self, o_code: int, a: int) -> list[list[float]]:
        assert self.sheet is not None and self.fresh is not None
        return [self.sheet.predict(None, o_code, r) for r in range(3)] + [self.fresh.predict(o_code, a)]

    def _fresh_brier_gain(self, o_code: int, a: int) -> float:
        assert self.fresh is not None
        c = self.fresh.counts[o_code][a]
        s = sum(c)
        p = [x / s for x in c]
        p0, p1 = p[2] + p[3], p[1] + p[3]
        return 0.5 * (p0 * (1.0 - p0) + p1 * (1.0 - p1)) / ((s + 1.0) ** 2) * 4.0

    def posterior(self, observed: list[int], action: int) -> tuple[float, float, float, float]:
        if not self.fitted or self.fresh is None or type(action) is not int or action not in ACTIONS:
            raise ValueError("SCDR_ADAPTER_NOT_READY_OR_BAD_ACTION")
        if len(observed) != 2 or observed[0] not in (0, 1) or observed[1] not in (0, 1):
            raise ValueError("SCDR_ADAPTER_INVALID_OBS")
        o_code = (int(observed[0]) << 1) | int(observed[1])
        aws = self._effective_rows()[action]
        rpreds = self._role_preds(o_code, action)
        mix = [0.0, 0.0, 0.0, 0.0]
        for ri in range(4):
            w = aws[ri]
            rp = rpreds[ri]
            for c in range(4):
                mix[c] += w * rp[c]
        tot = sum(mix)
        return tuple(x / tot for x in mix)  # type: ignore[return-value]

    def choose(self) -> int:
        if self.current is None or self.pending is not None or self.fresh is None:
            raise ValueError("SCDR_ADAPTER_PENDING_OR_NOT_STARTED")
        o_code = (int(self.current[0]) << 1) | int(self.current[1])
        eff_rows = self._effective_rows()
        avail = [a for a in ACTIONS if self.spent + COST[a] <= self.budget]
        best_a, best_u = 0, -1e9
        for a in avail:
            aws = eff_rows[a]
            rpreds = self._role_preds(o_code, a)
            mix = [sum(aws[i] * rpreds[i][c] for i in range(4)) for c in range(4)]
            m0, m1 = mix[2] + mix[3], mix[1] + mix[3]
            evgi = sum(
                aws[i] * 0.5 * (((p[2] + p[3]) - m0) ** 2 + ((p[1] + p[3]) - m1) ** 2)
                for i, p in enumerate(rpreds)
            )
            u = evgi + aws[3] * self._fresh_brier_gain(o_code, a) - self.probe_penalty * COST[a]
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

        old_map = max(range(4), key=lambda ri: self.beliefs[pa][ri])
        rpreds = self._role_preds(po, pa)
        post = [self.beliefs[pa][ri] * max(1e-6, rpreds[ri][pno]) for ri in range(4)]
        ps = sum(post)
        post = [x / ps for x in post]
        unif = 0.25
        self.beliefs[pa] = [(1.0 - self.hazard) * x + self.hazard * unif for x in post]
        new_map = max(range(4), key=lambda ri: self.beliefs[pa][ri])
        # Coupled Broadcast Changepoint Hazard: if action pa flips MAP role, wake up other actions for re-probing!
        if self.hazard > 0.0 and new_map != old_map and self.actions_taken >= 10:
            pulse = 0.35
            for other_a in ACTIONS:
                if other_a != pa:
                    self.beliefs[other_a] = [(1.0 - pulse) * x + pulse * unif for x in self.beliefs[other_a]]
        self.fresh.update(po, pa, pno)

        self.pending = None
        self.actions_taken += 1
        self.current = list(event["next_observation"])
