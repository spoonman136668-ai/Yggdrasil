"""
SpatialSymSCDRNumV3 (Cycles 30-32):
Factorized Continuous D4 Spatial-Symmetry x Sub-Stochastic Sinkhorn Causal Memory for NUM05.

Generalizes SCDR's discrete sensory-motor gauge transfer to continuous 2D physics:
1. Exact equivariance over the 8-element dihedral group D4 acting jointly on input (x, y)
   and displacement (dx, dy) while keeping scalar reward invariant:
     y_hat_{b,g,r}(s') = (g(dx_b(g^-1(s'), r), dy_b(g^-1(s'), r)), rew_b(g^-1(s'), r)).
2. Hierarchical O(|D4| * |A|^2) posterior: outer posterior over (frozen_bank, g in D4) + Fresh
   Active Bank updated via exact Rao-Blackwellized mixture marginal likelihood, paired with inner
   5x6 Sub-Stochastic Sinkhorn Soft-Exclusion (un-competed Fresh_a novelty column).
3. Pre-archive contradiction quarantine buffer: holds high-error transition rows prior to
   archival so frozen banks suffer zero pre-freeze contamination and disjoint cold-start matches
   NUM05_Native Phase 2 MSE exactly.
4. Mild diagonal prior on (bank, id) for fast Phase-3 return, precision-gated readout truncation
   (floor=0.03), reward-maximizing action selection, and byte-exact canonical cold checkpointing.

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

D4_NAMES: tuple[str, ...] = (
    "id",
    "rot90",
    "rot180",
    "rot270",
    "flip_x",
    "flip_y",
    "swap_xy",
    "anti_diag",
)
D4_INV: tuple[int, ...] = (0, 3, 2, 1, 4, 5, 6, 7)


def apply_d4(g: int, x: float, y: float) -> tuple[float, float]:
    """Apply dihedral symmetry g in D4 (0..7) to 2D vector (x, y)."""
    if g == 0:
        return (x, y)
    if g == 1:
        return (-y, x)
    if g == 2:
        return (-x, -y)
    if g == 3:
        return (y, -x)
    if g == 4:
        return (-x, y)
    if g == 5:
        return (x, -y)
    if g == 6:
        return (y, x)
    if g == 7:
        return (-y, -x)
    raise ValueError(f"SCDR_NUM05_BAD_D4_ELEMENT: {g}")


class SpatialSymSCDRNumV3:
    """Factorized D4 x Sub-Stochastic Sinkhorn continuous causal memory with quarantine freezing."""

    def __init__(
        self,
        *,
        max_frozen_banks: int = 4,
        sigma: float = 0.14,
        hazard: float = 0.025,
        readout_floor: float = 0.03,
    ):
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
        self._quarantine: list[dict] = []
        self._surprise_win: list[int] = []
        self._last_bcast = -100

    def _gauss_lik(self, pred: list[float], actual: list[float] | tuple[float, float, float], sigma: float) -> float:
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

    def _init_inner_matrix(self, g: int) -> list[list[float]]:
        if g == 0:
            mat = []
            for a in range(5):
                row = [0.12] * 6
                row[a] = 0.40
                mat.append(row)
            return mat
        return [[1.0 / 6.0] * 6 for _ in range(5)]

    def _equivariant_role_preds(self, bi: int, g: int, obs) -> list[list[float]]:
        inv_obs = apply_d4(D4_INV[g], float(obs[0]), float(obs[1]))
        bank = self.frozen_banks[bi]
        out = []
        for r in range(5):
            dx, dy, rew = bank.predict(inv_obs, r)
            rdx, rdy = apply_d4(g, dx, dy)
            out.append([rdx, rdy, rew])
        return out

    def _hyp_action_pred(self, hi: int, obs, act: int) -> tuple[list[float], list[list[float]], list[float]]:
        bi = hi // 8
        g = hi % 8
        eff = sinkhorn_sub_stochastic(self.inner_beliefs[hi], 5, iters=3)
        aws = eff[act]
        aws_read = self._truncate_norm(aws)
        preds = self._equivariant_role_preds(bi, g, obs) + [self.active_bank.predict(obs, act)]
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
        n_h = len(self.frozen_banks) * 8
        out = [0.0, 0.0, 0.0]
        for hi in range(n_h):
            w = ow_read[hi]
            if w > 0.0:
                p, _, _ = self._hyp_action_pred(hi, observation, action)
                for k in range(3):
                    out[k] += w * p[k]
        wf = ow_read[-1]
        if wf > 0.0:
            pf = self.active_bank.predict(observation, action)
            for k in range(3):
                out[k] += wf * pf[k]
        return out

    def predict(self, observation, action: int) -> list[float]:
        return self.forecast(observation, action)

    def action_abstain_prob(self, action: int) -> float:
        """Posterior probability that `action` is novel relative to all frozen (bank, D4) roles."""
        if not self.frozen_banks:
            return 0.0
        n_h = len(self.frozen_banks) * 8
        p_novel = self.outer_beliefs[-1]
        for hi in range(n_h):
            if self.outer_beliefs[hi] > 1e-6:
                eff = sinkhorn_sub_stochastic(self.inner_beliefs[hi], 5, iters=3)
                p_novel += self.outer_beliefs[hi] * eff[action][5]
        return p_novel

    def map_gauge(self) -> tuple[int, str] | None:
        if not self.frozen_banks:
            return None
        best = max(range(len(self.outer_beliefs)), key=lambda i: self.outer_beliefs[i])
        if best == len(self.outer_beliefs) - 1:
            return (-1, "fresh_active")
        return (best // 8, D4_NAMES[best % 8])

    def choose_action_for_reward(self, observation, *, explore_weight: float = 0.25) -> int:
        if not self.frozen_banks:
            return max(range(5), key=lambda a: self.active_bank.predict(observation, a)[2])
        n_h = len(self.frozen_banks) * 8
        best_hi = max(range(n_h), key=lambda i: self.outer_beliefs[i])
        eff = sinkhorn_sub_stochastic(self.inner_beliefs[best_hi], 5, iters=3)
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
        n_h = len(self.frozen_banks) * 8
        p_fresh = 0.25
        p_hyp = (1.0 - p_fresh) / n_h
        self.outer_beliefs = [p_hyp] * n_h + [p_fresh]
        self.inner_beliefs = [self._init_inner_matrix(hi % 8) for hi in range(n_h)]

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
                self._quarantine.append(row)
                self.consec_contradictions = len(self._quarantine)
                if self.consec_contradictions >= 3:
                    q_rows = self._quarantine[:]
                    self._quarantine.clear()
                    self.archive_active_bank()
                    for qr in q_rows:
                        qobs = qr["observation"]
                        qact = int(qr["action"])
                        qy = target(qr)
                        qmse = error(self.forecast(qobs, qact), qy)
                        self._update_hierarchical(qr, qobs, qact, qy, qmse)
                    self.events_seen += 1
                    return
                self.events_seen += 1
                return
            else:
                if self._quarantine:
                    for qr in self._quarantine:
                        self.active_bank.observe(qr)
                        self.active_events += 1
                    self._quarantine.clear()
                self.consec_contradictions = 0
            if self.active_events >= 40 and self.consec_contradictions == 0:
                self.ema_mse = 0.95 * self.ema_mse + 0.05 * mse
            self.active_bank.observe(row)
            self.active_events += 1
            self.events_seen += 1
            return

        active_resp = self.outer_beliefs[-1] + sum(
            self.outer_beliefs[hi] * self.inner_beliefs[hi][act][5]
            for hi in range(len(self.frozen_banks) * 8)
        )
        if active_resp > 0.5 and self.active_events >= 80 and self.active_bank.count(obs, act) >= 3:
            act_mse = error(self.active_bank.predict(obs, act), y)
            rel_thresh = min(0.15, max(0.025, 8.0 * self.ema_mse))
            if act_mse > rel_thresh:
                best_frozen_mse = min(
                    min(error(p, y) for p in self._equivariant_role_preds(bi, g, obs))
                    for bi in range(len(self.frozen_banks))
                    for g in range(8)
                )
                if best_frozen_mse > rel_thresh:
                    self._quarantine.append(row)
                    self.consec_contradictions = len(self._quarantine)
                    if self.consec_contradictions >= 3 and len(self.frozen_banks) < self.max_frozen_banks:
                        q_rows = self._quarantine[:]
                        self._quarantine.clear()
                        self.archive_active_bank()
                        for qr in q_rows:
                            qobs = qr["observation"]
                            qact = int(qr["action"])
                            qy = target(qr)
                            qmse = error(self.forecast(qobs, qact), qy)
                            self._update_hierarchical(qr, qobs, qact, qy, qmse)
                        self.events_seen += 1
                        return
                    self.events_seen += 1
                    return
                else:
                    self._quarantine.clear()
                    self.consec_contradictions = 0
            else:
                self._quarantine.clear()
                self.consec_contradictions = 0
                if self.active_events >= 40:
                    self.ema_mse = 0.95 * self.ema_mse + 0.05 * act_mse

        self._update_hierarchical(row, obs, act, y, mse)
        self.events_seen += 1

    def _update_hierarchical(self, row: dict, obs, act: int, y: list[float], pred_mse: float) -> None:
        n_h = len(self.frozen_banks) * 8
        pred_act = self.active_bank.predict(obs, act)
        n_act = self.active_bank.count(obs, act)
        sig_act = self.sigma * (2.2 if n_act < 2 else (1.4 if n_act < 5 else 1.0))
        lik_act = self._gauss_lik(pred_act, y, sig_act)

        old_outer_map = max(range(n_h + 1), key=lambda i: self.outer_beliefs[i])
        any_flip = False

        hyp_liks = []
        for hi in range(n_h):
            old_im = max(range(6), key=lambda r: self.inner_beliefs[hi][act][r])
            _, rpreds, aws = self._hyp_action_pred(hi, obs, act)
            il = [self._gauss_lik(rpreds[r], y, self.sigma) for r in range(5)] + [lik_act]
            hyp_liks.append(sum(aws[i] * il[i] for i in range(6)))

            ip = [self.inner_beliefs[hi][act][i] * il[i] for i in range(6)]
            ips = sum(ip)
            ip = [x / ips for x in ip]
            if hi % 8 == 0:
                prior_row = [0.12] * 6
                prior_row[act] = 0.40
                self.inner_beliefs[hi][act] = [
                    (1.0 - self.hazard) * ip[i] + self.hazard * prior_row[i] for i in range(6)
                ]
            else:
                self.inner_beliefs[hi][act] = [
                    (1.0 - self.hazard) * ip[i] + self.hazard * (1.0 / 6.0) for i in range(6)
                ]
            new_im = max(range(6), key=lambda r: self.inner_beliefs[hi][act][r])
            if new_im != old_im and self.outer_beliefs[hi] > 0.35:
                any_flip = True

        op = [self.outer_beliefs[hi] * hyp_liks[hi] for hi in range(n_h)] + [self.outer_beliefs[-1] * lik_act]
        ops = sum(op)
        op = [x / ops for x in op]
        p_fresh = 0.25
        p_hyp = (1.0 - p_fresh) / n_h
        outer_prior = [p_hyp] * n_h + [p_fresh]
        self.outer_beliefs = [(1.0 - self.hazard) * op[i] + self.hazard * outer_prior[i] for i in range(n_h + 1)]
        if max(range(n_h + 1), key=lambda i: self.outer_beliefs[i]) != old_outer_map:
            any_flip = True

        active_resp = self.outer_beliefs[-1] + sum(
            self.outer_beliefs[hi] * self.inner_beliefs[hi][act][5] for hi in range(n_h)
        )
        write_gate = 0.15 if self.active_events < 20 else 0.30
        if active_resp > write_gate:
            self.active_bank.observe(row)
            self.active_events += 1

        self._surprise_win.append(1 if (pred_mse > 0.10 or any_flip) else 0)
        if len(self._surprise_win) > 4:
            self._surprise_win.pop(0)
        if sum(self._surprise_win) >= 2 and (self.events_seen - self._last_bcast) >= 10:
            pulse = 0.45
            for hi in range(n_h):
                for oa in range(5):
                    if oa != act:
                        if hi % 8 == 0:
                            pr = [0.12] * 6
                            pr[oa] = 0.40
                            self.inner_beliefs[hi][oa] = [
                                (1.0 - pulse) * self.inner_beliefs[hi][oa][i] + pulse * pr[i] for i in range(6)
                            ]
                        else:
                            self.inner_beliefs[hi][oa] = [
                                (1.0 - pulse) * x + pulse * (1.0 / 6.0) for x in self.inner_beliefs[hi][oa]
                            ]
            self._last_bcast = self.events_seen
            self._surprise_win.clear()

    def checkpoint(self) -> dict:
        return {
            "schema": "yggdrasil.scdr_num05_spatial_d4.checkpoint.v1",
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
            "quarantine": [dict(r) for r in self._quarantine],
            "surprise_win": self._surprise_win[:],
            "last_bcast": self._last_bcast,
        }

    def checkpoint_digest(self) -> str:
        return digest(canonical(self.checkpoint()))

    @classmethod
    def restore(cls, state: dict) -> "SpatialSymSCDRNumV3":
        if state.get("schema") != "yggdrasil.scdr_num05_spatial_d4.checkpoint.v1":
            raise ValueError("SCDR_NUM05_D4_BAD_CHECKPOINT_SCHEMA")
        obj = cls(
            max_frozen_banks=int(state["max_frozen_banks"]),
            sigma=float(state["sigma"]),
            hazard=float(state["hazard"]),
            readout_floor=float(state["readout_floor"]),
        )
        for snap in state["frozen_banks"]:
            b = Bank()
            b.cells = {k: [int(v[0]), [float(x) for x in v[1]]] for k, v in snap.items()}
            obj.frozen_banks.append(b)
        obj.frozen_sigs = list(state["frozen_sigs"])
        obj.active_bank.cells = {k: [int(v[0]), [float(x) for x in v[1]]] for k, v in state["active_bank"].items()}
        obj.active_events = int(state["active_events"])
        obj.events_seen = int(state["events_seen"])
        obj.consec_contradictions = int(state["consec_contradictions"])
        obj.ema_mse = float(state["ema_mse"])
        obj.outer_beliefs = [float(x) for x in state["outer_beliefs"]]
        obj.inner_beliefs = [[[float(x) for x in r] for r in mat] for mat in state["inner_beliefs"]]
        obj._quarantine = [dict(r) for r in state.get("quarantine", [])]
        obj._surprise_win = [int(x) for x in state["surprise_win"]]
        obj._last_bcast = int(state["last_bcast"])
        return obj
