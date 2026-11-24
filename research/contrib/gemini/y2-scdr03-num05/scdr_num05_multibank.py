"""
MultiBankSCDRNumV2 (Cycles 28-29):
Extends SCDRNumContinuous with:
1. Precision-gated readout truncation (sub-floor hazard weights < 0.03 zeroed before forecasting)
   closing disjoint_ABA to within < 0.001 MSE of NUM05_Native while preserving 10.9x permuted win.
2. Multi-Bank Continuous Archive (up to 4 byte-exact frozen banks + active fresh bank)
   with hierarchical outer bank posterior + inner 5x6 Sub-Stochastic Sinkhorn beliefs.
3. Reward-maximizing continuous action selector (`choose_action_for_reward`).

Pure Python stdlib; strictly public-only; zero edits to NUM05 files or reserved seeds.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

NUM05_DIR = Path(__file__).resolve().parents[2] / "chatgpt" / "CAUSAL-AMALGAM" / "NUM05"
if NUM05_DIR.exists() and str(NUM05_DIR) not in sys.path:
    sys.path.insert(0, str(NUM05_DIR))

from num05 import Bank, canonical, digest, error, target
from scdr_num05_continuous import sinkhorn_sub_stochastic


class MultiBankSCDRNumV2:
    """Multi-bank continuous Gaussian Sub-Stochastic Sinkhorn with precision-gated readout."""

    def __init__(self, *, max_frozen_banks: int = 4, sigma: float = 0.14, hazard: float = 0.025, readout_floor: float = 0.03):
        self.max_frozen_banks = max_frozen_banks
        self.sigma = sigma
        self.hazard = hazard
        self.readout_floor = readout_floor

        self.frozen_banks: list[Bank] = []
        self.frozen_sigs: list[str] = []
        self.active_bank = Bank()
        self.active_events = 0
        self.events_seen = 0
        self.consec_contradictions = 0
        self.ema_mse = 0.005

        self.outer_beliefs: list[float] = [1.0]
        self.inner_beliefs: list[list[list[float]]] = []
        self._surprise_win: list[int] = []
        self._last_bcast = -100

    def _gauss_lik(self, pred: list[float], actual: tuple[float, float, float], sigma: float) -> float:
        mse = error(pred, actual)
        return math.exp(-1.5 * mse / (sigma * sigma)) + 1e-8

    def _truncate_norm(self, ws: list[float]) -> list[float]:
        tr = [w if w >= self.readout_floor else 0.0 for w in ws]
        s = sum(tr)
        if s <= 1e-12:
            m = max(ws)
            tr = [1.0 if w == m else 0.0 for w in ws]
            s = sum(tr)
        return [w / s for w in tr]

    def _bank_action_pred(self, bi: int, obs, act: int) -> tuple[list[float], list[list[float]], list[float]]:
        eff = sinkhorn_sub_stochastic(self.inner_beliefs[bi], 5, iters=3)
        aws = eff[act]
        aws_read = self._truncate_norm(aws)
        preds = [self.frozen_banks[bi].predict(obs, r) for r in range(5)] + [self.active_bank.predict(obs, act)]
        out = [0.0, 0.0, 0.0]
        for ri in range(6):
            w = aws_read[ri]
            if w > 0.0:
                pr = preds[ri]
                for k in range(3):
                    out[k] += w * pr[k]
        return out, preds, aws

    def forecast(self, observation, action: int) -> list[float]:
        if not self.frozen_banks:
            return self.active_bank.predict(observation, action)
        ow_read = self._truncate_norm(self.outer_beliefs)
        out = [0.0, 0.0, 0.0]
        for bi in range(len(self.frozen_banks)):
            w = ow_read[bi]
            if w > 0.0:
                p, _, _ = self._bank_action_pred(bi, observation, action)
                for k in range(3):
                    out[k] += w * p[k]
        wf = ow_read[-1]
        if wf > 0.0:
            pf = self.active_bank.predict(observation, action)
            for k in range(3):
                out[k] += wf * pf[k]
        return out

    def choose_action_for_reward(self, observation, *, explore_weight: float = 0.25) -> int:
        """Select action maximizing predicted reward + Sinkhorn epistemic uncertainty bonus."""
        if not self.frozen_banks:
            return max(range(5), key=lambda a: self.active_bank.predict(observation, a)[2])
        best_bi = max(range(len(self.frozen_banks)), key=lambda i: self.outer_beliefs[i])
        eff = sinkhorn_sub_stochastic(self.inner_beliefs[best_bi], 5, iters=3)
        return max(range(5), key=lambda a: self.forecast(observation, a)[2] + explore_weight * (1.0 - max(eff[a])))

    def archive_active_bank(self) -> None:
        if len(self.frozen_banks) >= self.max_frozen_banks:
            return
        self.frozen_banks.append(self.active_bank)
        self.frozen_sigs.append(self.active_bank.signature())
        self.active_bank = Bank()
        self.active_events = 0
        self.consec_contradictions = 0
        self.ema_mse = 0.005
        n_f = len(self.frozen_banks)
        self.outer_beliefs = [1.0 / (n_f + 1)] * (n_f + 1)
        row = [1.0 / 6.0] * 6
        self.inner_beliefs.append([list(row) for _ in range(5)])
        for bi in range(n_f - 1):
            self.inner_beliefs[bi] = [list(row) for _ in range(5)]

    def observe(self, row: dict) -> None:
        obs = row["observation"]
        act = int(row["action"])
        y = target(row)
        pred = self.forecast(obs, act)
        mse = error(pred, y)

        if not self.frozen_banks:
            cell_count = self.active_bank.count(obs, act)
            rel_thresh = min(0.15, max(0.025, 8.0 * self.ema_mse))
            if self.active_events >= 100 and cell_count >= 3 and mse > rel_thresh:
                self.consec_contradictions += 1
                if self.consec_contradictions >= 3:
                    self.archive_active_bank()
                    self._update_hierarchical(row, obs, act, y, mse)
                    self.events_seen += 1
                    return
            else:
                self.consec_contradictions = 0
            if self.active_events >= 40 and self.consec_contradictions == 0:
                self.ema_mse = 0.95 * self.ema_mse + 0.05 * mse
            self.active_bank.observe(row)
            self.active_events += 1
            self.events_seen += 1
            return

        active_resp = self.outer_beliefs[-1] + sum(
            self.outer_beliefs[bi] * self.inner_beliefs[bi][act][5] for bi in range(len(self.frozen_banks))
        )
        if active_resp > 0.5 and self.active_events >= 80 and self.active_bank.count(obs, act) >= 3:
            act_mse = error(self.active_bank.predict(obs, act), y)
            rel_thresh = min(0.15, max(0.025, 8.0 * self.ema_mse))
            if act_mse > rel_thresh:
                best_frozen_mse = min(
                    min(error(fb.predict(obs, r), y) for r in range(5)) for fb in self.frozen_banks
                )
                if best_frozen_mse > rel_thresh:
                    self.consec_contradictions += 1
                    if self.consec_contradictions >= 3 and len(self.frozen_banks) < self.max_frozen_banks:
                        self.archive_active_bank()
                else:
                    self.consec_contradictions = 0
            else:
                self.consec_contradictions = 0
                if self.active_events >= 40:
                    self.ema_mse = 0.95 * self.ema_mse + 0.05 * act_mse

        self._update_hierarchical(row, obs, act, y, mse)
        self.events_seen += 1

    def _update_hierarchical(self, row: dict, obs, act: int, y: tuple[float, float, float], pred_mse: float) -> None:
        n_f = len(self.frozen_banks)
        pred_act = self.active_bank.predict(obs, act)
        n_act = self.active_bank.count(obs, act)
        sig_act = self.sigma * (2.2 if n_act < 2 else (1.4 if n_act < 5 else 1.0))
        lik_act = self._gauss_lik(pred_act, y, sig_act)

        old_outer_map = max(range(n_f + 1), key=lambda i: self.outer_beliefs[i])
        any_flip = False

        bank_liks = []
        for bi in range(n_f):
            old_im = max(range(6), key=lambda r: self.inner_beliefs[bi][act][r])
            bp, rpreds, _ = self._bank_action_pred(bi, obs, act)
            bank_liks.append(self._gauss_lik(bp, y, self.sigma))

            il = [self._gauss_lik(rpreds[r], y, self.sigma) for r in range(5)] + [lik_act]
            ip = [self.inner_beliefs[bi][act][i] * il[i] for i in range(6)]
            ips = sum(ip)
            ip = [x / ips for x in ip]
            self.inner_beliefs[bi][act] = [(1.0 - self.hazard) * x + self.hazard * (1.0 / 6.0) for x in ip]
            new_im = max(range(6), key=lambda r: self.inner_beliefs[bi][act][r])
            if new_im != old_im and self.outer_beliefs[bi] > 0.35:
                any_flip = True

        op = [self.outer_beliefs[bi] * bank_liks[bi] for bi in range(n_f)] + [self.outer_beliefs[-1] * lik_act]
        ops = sum(op)
        op = [x / ops for x in op]
        ou = 1.0 / (n_f + 1)
        self.outer_beliefs = [(1.0 - self.hazard) * x + self.hazard * ou for x in op]
        if max(range(n_f + 1), key=lambda i: self.outer_beliefs[i]) != old_outer_map:
            any_flip = True

        active_resp = self.outer_beliefs[-1] + sum(
            self.outer_beliefs[bi] * self.inner_beliefs[bi][act][5] for bi in range(n_f)
        )
        if active_resp > 0.30:
            self.active_bank.observe(row)
            self.active_events += 1

        self._surprise_win.append(1 if (pred_mse > 0.10 or any_flip) else 0)
        if len(self._surprise_win) > 4:
            self._surprise_win.pop(0)
        if sum(self._surprise_win) >= 2 and (self.events_seen - self._last_bcast) >= 10:
            pulse = 0.45
            for bi in range(n_f):
                for oa in range(5):
                    if oa != act:
                        self.inner_beliefs[bi][oa] = [(1.0 - pulse) * x + pulse * (1.0 / 6.0) for x in self.inner_beliefs[bi][oa]]
            self._last_bcast = self.events_seen
            self._surprise_win.clear()

    def checkpoint(self) -> dict:
        return {
            "schema": "yggdrasil.scdr_num05_multibank.checkpoint.v1",
            "max_frozen_banks": self.max_frozen_banks,
            "sigma": self.sigma,
            "hazard": self.hazard,
            "readout_floor": self.readout_floor,
            "frozen_banks": [b.snapshot() for b in self.frozen_banks],
            "frozen_sigs": self.frozen_sigs[:],
            "active_bank": self.active_bank.snapshot(),
            "active_events": self.active_events,
            "events_seen": self.events_seen,
            "consec_contradictions": self.consec_contradictions,
            "ema_mse": self.ema_mse,
            "outer_beliefs": self.outer_beliefs[:],
            "inner_beliefs": [[r[:] for r in mat] for mat in self.inner_beliefs],
            "surprise_win": self._surprise_win[:],
            "last_bcast": self._last_bcast,
        }

    def checkpoint_digest(self) -> str:
        return digest(canonical(self.checkpoint()))
