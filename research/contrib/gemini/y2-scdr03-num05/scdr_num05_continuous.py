"""
SCDR-NUM Continuous 5-Action Causal Memory (y2-scdr03-num05):
Transfers SCDR's Sub-Stochastic Sinkhorn Soft-Exclusion + Coupled Broadcast Changepoint Hazard
from discrete binary worlds onto NUM05's continuous 5-action, 4-quadrant, 3-output (dx, dy, reward)
numerical causal schema.

Pure Python stdlib; strictly public-only; zero edits to NUM05 files or reserved seeds.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

NUM05_DIR = Path(__file__).resolve().parents[2] / "chatgpt" / "CAUSAL-AMALGAM" / "NUM05"
if NUM05_DIR.exists() and str(NUM05_DIR) not in sys.path:
    sys.path.insert(0, str(NUM05_DIR))

from num05 import Bank, canonical, digest, error, region, target


def sinkhorn_sub_stochastic(raw_rows: list[list[float]], n_actions: int, iters: int = 3) -> list[list[float]]:
    K = [row[:n_actions] for row in raw_rows]
    fresh_col = [row[n_actions] for row in raw_rows]
    row_mass = [sum(r) for r in K]
    for _ in range(iters):
        for c in range(n_actions):
            csum = sum(K[r][c] for r in range(n_actions))
            if csum > 1.0:
                inv = 1.0 / csum
                for r in range(n_actions):
                    K[r][c] *= inv
        for r in range(n_actions):
            rsum = sum(K[r])
            if rsum > 1e-12 and row_mass[r] > 1e-12:
                scale = row_mass[r] / rsum
                for c in range(n_actions):
                    K[r][c] *= scale
    return [K[r] + [fresh_col[r]] for r in range(n_actions)]


class SCDRNumContinuous:
    """
    Continuous Gaussian Sub-Stochastic Sinkhorn + Self-Calibrated Surprise Gate + Frozen Bank 0 Archive.
    - Preserves Bank 0 byte-exact upon archival.
    - Self-calibrated relative surprise threshold min(0.15, max(0.025, 8.0 * ema_mse)) detects
      moderate-MSE action permutations without false alarms on stationary noise.
    - Selectively transfers permuted continuous operators via Sinkhorn while isolating novel
      operators into Bank 1 via the un-competed Fresh_a column.
    """

    def __init__(self, *, sigma: float = 0.14, hazard: float = 0.025, broadcast_pulse: float = 0.45):
        self.sigma = sigma
        self.hazard = hazard
        self.broadcast_pulse = broadcast_pulse

        self.bank0 = Bank()
        self.bank1 = Bank()
        self.archived = False
        self.events_seen = 0
        self.consec_contradictions = 0
        self.ema_mse = 0.005
        self.bank0_frozen_signature: str | None = None

        self.beliefs: list[list[float]] = []
        self._surprise_win: list[int] = []
        self._last_bcast = -100

    def _init_sinkhorn(self) -> None:
        row = [1.0 / 6.0] * 6
        self.beliefs = [list(row) for _ in range(5)]

    def _gauss_lik(self, pred: list[float], actual: tuple[float, float, float], sigma: float) -> float:
        mse = error(pred, actual)
        return math.exp(-1.5 * mse / (sigma * sigma)) + 1e-8

    def forecast(self, observation, action: int) -> list[float]:
        if not self.archived:
            return self.bank0.predict(observation, action)
        eff = sinkhorn_sub_stochastic(self.beliefs, 5, iters=3)
        aws = eff[action]
        preds = [self.bank0.predict(observation, r) for r in range(5)] + [self.bank1.predict(observation, action)]
        out = [0.0, 0.0, 0.0]
        for ri in range(6):
            w = aws[ri]
            pr = preds[ri]
            for k in range(3):
                out[k] += w * pr[k]
        return out

    def predict(self, observation, action: int) -> list[float]:
        return self.forecast(observation, action)

    def observe(self, row: dict) -> None:
        obs = row["observation"]
        act = int(row["action"])
        y = target(row)
        pred = self.forecast(obs, act)
        mse = error(pred, y)

        if not self.archived:
            cell_count = self.bank0.count(obs, act)
            rel_thresh = min(0.15, max(0.025, 8.0 * self.ema_mse))
            if self.events_seen >= 100 and cell_count >= 3 and mse > rel_thresh:
                self.consec_contradictions += 1
                if self.consec_contradictions >= 3:
                    self.archived = True
                    self.bank0_frozen_signature = self.bank0.signature()
                    self._init_sinkhorn()
                    self._update_archived(row, obs, act, y, mse)
                    self.events_seen += 1
                    return
            else:
                self.consec_contradictions = 0
            if self.events_seen >= 40 and self.consec_contradictions == 0:
                self.ema_mse = 0.95 * self.ema_mse + 0.05 * mse
            self.bank0.observe(row)
            self.events_seen += 1
            return

        self._update_archived(row, obs, act, y, mse)
        self.events_seen += 1

    def _update_archived(self, row: dict, obs, act: int, y: tuple[float, float, float], pred_mse: float) -> None:
        old_map = max(range(6), key=lambda r: self.beliefs[act][r])
        preds_b0 = [self.bank0.predict(obs, r) for r in range(5)]
        pred_b1 = self.bank1.predict(obs, act)

        n_b1 = self.bank1.count(obs, act)
        sig_b1 = self.sigma * (2.2 if n_b1 < 2 else (1.4 if n_b1 < 5 else 1.0))

        liks = [self._gauss_lik(p, y, self.sigma) for p in preds_b0] + [self._gauss_lik(pred_b1, y, sig_b1)]
        post = [self.beliefs[act][i] * liks[i] for i in range(6)]
        ps = sum(post)
        post = [x / ps for x in post]
        unif = 1.0 / 6.0
        self.beliefs[act] = [(1.0 - self.hazard) * x + self.hazard * unif for x in post]
        new_map = max(range(6), key=lambda r: self.beliefs[act][r])

        if self.beliefs[act][5] > 0.25:
            self.bank1.observe(row)

        self._surprise_win.append(1 if (pred_mse > 0.12 or new_map != old_map) else 0)
        if len(self._surprise_win) > 4:
            self._surprise_win.pop(0)
        if sum(self._surprise_win) >= 2 and (self.events_seen - self._last_bcast) >= 10:
            pulse = self.broadcast_pulse
            for oa in range(5):
                if oa != act:
                    self.beliefs[oa] = [(1.0 - pulse) * x + pulse * unif for x in self.beliefs[oa]]
            self._last_bcast = self.events_seen
            self._surprise_win.clear()


    def checkpoint(self) -> dict:
        """Canonical cold checkpoint matching NUM05's cold-replay contract."""
        return {
            "schema": "yggdrasil.scdr_num05.checkpoint.v1",
            "sigma": self.sigma,
            "hazard": self.hazard,
            "broadcast_pulse": self.broadcast_pulse,
            "bank0": self.bank0.snapshot(),
            "bank1": self.bank1.snapshot(),
            "archived": self.archived,
            "events_seen": self.events_seen,
            "consec_contradictions": self.consec_contradictions,
            "ema_mse": self.ema_mse,
            "bank0_frozen_signature": self.bank0_frozen_signature,
            "beliefs": [row[:] for row in self.beliefs],
            "surprise_win": self._surprise_win[:],
            "last_bcast": self._last_bcast,
        }

    def checkpoint_digest(self) -> str:
        return digest(canonical(self.checkpoint()))

    @classmethod
    def restore(cls, state: dict) -> "SCDRNumContinuous":
        if state.get("schema") != "yggdrasil.scdr_num05.checkpoint.v1":
            raise ValueError("SCDR_NUM05_BAD_CHECKPOINT_SCHEMA")
        obj = cls(
            sigma=float(state["sigma"]),
            hazard=float(state["hazard"]),
            broadcast_pulse=float(state["broadcast_pulse"]),
        )
        obj.bank0.cells = {k: [int(v[0]), [float(x) for x in v[1]]] for k, v in state["bank0"].items()}
        obj.bank1.cells = {k: [int(v[0]), [float(x) for x in v[1]]] for k, v in state["bank1"].items()}
        obj.archived = bool(state["archived"])
        obj.events_seen = int(state["events_seen"])
        obj.consec_contradictions = int(state["consec_contradictions"])
        obj.ema_mse = float(state["ema_mse"])
        obj.bank0_frozen_signature = state["bank0_frozen_signature"]
        obj.beliefs = [[float(x) for x in row] for row in state["beliefs"]]
        obj._surprise_win = [int(x) for x in state["surprise_win"]]
        obj._last_bcast = int(state["last_bcast"])
        return obj
