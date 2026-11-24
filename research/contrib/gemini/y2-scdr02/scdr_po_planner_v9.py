"""
SCDR-PO-Planner-v9/v10 (Cycles 20-24):
1. Deterministic Cold-Save / Cold-Restore JSON serialization with SHA-256 custody receipt.
2. TwoModeLatentSheet & FactorizedStallTwoModeSheet (28-param factorized-stall 2-mode EM).
3. POHiddenModePlannerV9 (1-step filter) & POHiddenModePlannerV10 (exact 2-step retroactive
   mode-transition credit + mode-EVGI, breaking observational aliasing at symmetric states).

Pure Python stdlib, strictly public-only interface.
"""

from __future__ import annotations

import hashlib
import json
import random

from scdr_planner_v8 import SCDRMultiStepPlannerV8
from scdr_sinkhorn_v6 import FreshOnlineKBit, GeneralSheetKBit, sinkhorn_sub_stochastic


def serialize_planner_v8(planner: SCDRMultiStepPlannerV8) -> bytes:
    """Canonical deterministic JSON serialization for SCDRMultiStepPlannerV8."""
    assert planner.fresh is not None
    payload = {
        "schema": "yggdrasil.scdr.planner_v8.cold_state.v1",
        "n_bits": planner.n_bits,
        "n_actions": planner.n_actions,
        "horizon": planner.horizon,
        "gamma": planner.gamma,
        "hazard": planner.hazard,
        "broadcast_pulse": planner.broadcast_pulse,
        "explore_weight": planner.explore_weight,
        "sinkhorn_iters": planner.sinkhorn_iters,
        "sheet_counts": planner.sheet.counts,
        "beliefs": planner.beliefs,
        "fresh_counts": planner.fresh.counts,
        "steps": planner.steps,
        "surprise_window": planner._surprise_window,
        "last_broadcast": planner._last_broadcast,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def deserialize_planner_v8(raw: bytes) -> SCDRMultiStepPlannerV8:
    """Restore SCDRMultiStepPlannerV8 bit-exactly from canonical JSON bytes."""
    d = json.loads(raw.decode("utf-8"))
    if d.get("schema") != "yggdrasil.scdr.planner_v8.cold_state.v1":
        raise ValueError("SCDR_INVALID_COLD_STATE_SCHEMA")
    sheet = GeneralSheetKBit(int(d["n_bits"]), int(d["n_actions"]))
    sheet.counts = [[[float(x) for x in row] for row in mat] for mat in d["sheet_counts"]]
    p = SCDRMultiStepPlannerV8(
        sheet,
        horizon=int(d["horizon"]),
        gamma=float(d["gamma"]),
        hazard=float(d["hazard"]),
        broadcast_pulse=float(d["broadcast_pulse"]),
        explore_weight=float(d["explore_weight"]),
        sinkhorn_iters=int(d["sinkhorn_iters"]),
    )
    p.beliefs = [[float(x) for x in row] for row in d["beliefs"]]
    assert p.fresh is not None
    p.fresh.counts = [[[float(x) for x in row] for row in mat] for mat in d["fresh_counts"]]
    p.steps = int(d["steps"])
    p._surprise_window = [int(x) for x in d["surprise_window"]]
    p._last_broadcast = int(d["last_broadcast"])
    return p


def cold_state_sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class TwoModeLatentSheet:
    """Full 2-mode Baum-Welch sheet (Cycle 21 baseline)."""

    def __init__(self, n_bits: int, n_actions: int, seed: int = 7):
        self.n_bits = n_bits
        self.n_states = 1 << n_bits
        self.n_actions = n_actions
        self.seed = seed
        self.M = [[[0.85 if z == nz else 0.15 for nz in range(2)] for _ in range(n_actions)] for z in range(2)]
        self.E = [[[[1.0 / self.n_states] * self.n_states for _ in range(n_actions)] for _ in range(self.n_states)] for _ in range(2)]

    def fit_em(self, trace: list[dict], *, iters: int = 12) -> None:
        rng = random.Random(self.seed)
        parsed = [(int(e["obs_code"]), int(e["action"]), int(e["next_obs_code"])) for e in trace]
        n, ns, na = len(parsed), self.n_states, self.n_actions
        base = [[[0.5] * ns for _ in range(na)] for _ in range(ns)]
        for o, a, no in parsed:
            base[o][a][no] += 1.0
        for z in range(2):
            for s in range(ns):
                for a in range(na):
                    row = [base[s][a][k] * (0.85 + 0.30 * rng.random()) for k in range(ns)]
                    tot = sum(row)
                    self.E[z][s][a] = [x / tot for x in row]
        for _ in range(iters):
            alpha = [[0.5, 0.5] for _ in range(n)]
            for t, (o, a, no) in enumerate(parsed):
                pred = [0.5, 0.5] if t == 0 else [
                    alpha[t - 1][0] * self.M[0][parsed[t - 1][1]][0] + alpha[t - 1][1] * self.M[1][parsed[t - 1][1]][0],
                    alpha[t - 1][0] * self.M[0][parsed[t - 1][1]][1] + alpha[t - 1][1] * self.M[1][parsed[t - 1][1]][1],
                ]
                a0, a1 = pred[0] * max(1e-6, self.E[0][o][a][no]), pred[1] * max(1e-6, self.E[1][o][a][no])
                sc = a0 + a1
                alpha[t] = [a0 / sc, a1 / sc] if sc > 1e-12 else [0.5, 0.5]
            beta = [[1.0, 1.0] for _ in range(n)]
            for t in range(n - 2, -1, -1):
                _, a_t, _ = parsed[t]
                o_n, a_n, no_n = parsed[t + 1]
                e0, e1 = max(1e-6, self.E[0][o_n][a_n][no_n]), max(1e-6, self.E[1][o_n][a_n][no_n])
                b0 = self.M[0][a_t][0] * e0 * beta[t + 1][0] + self.M[0][a_t][1] * e1 * beta[t + 1][1]
                b1 = self.M[1][a_t][0] * e0 * beta[t + 1][0] + self.M[1][a_t][1] * e1 * beta[t + 1][1]
                bs = b0 + b1
                beta[t] = [b0 / bs, b1 / bs] if bs > 1e-12 else [0.5, 0.5]
            m_acc = [[[0.5, 0.5] for _ in range(na)] for _ in range(2)]
            e_acc = [[[[0.25] * ns for _ in range(na)] for _ in range(ns)] for _ in range(2)]
            for t, (o, a, no) in enumerate(parsed):
                g0, g1 = alpha[t][0] * beta[t][0], alpha[t][1] * beta[t][1]
                gs = g0 + g1
                g0, g1 = (g0 / gs, g1 / gs) if gs > 1e-12 else (0.5, 0.5)
                e_acc[0][o][a][no] += g0
                e_acc[1][o][a][no] += g1
                if t < n - 1:
                    o_n, a_n, no_n = parsed[t + 1]
                    e0, e1 = max(1e-6, self.E[0][o_n][a_n][no_n]), max(1e-6, self.E[1][o_n][a_n][no_n])
                    xi = [
                        [alpha[t][0] * self.M[0][a][0] * e0 * beta[t + 1][0], alpha[t][0] * self.M[0][a][1] * e1 * beta[t + 1][1]],
                        [alpha[t][1] * self.M[1][a][0] * e0 * beta[t + 1][0], alpha[t][1] * self.M[1][a][1] * e1 * beta[t + 1][1]],
                    ]
                    xs = xi[0][0] + xi[0][1] + xi[1][0] + xi[1][1]
                    if xs > 1e-12:
                        for z in range(2):
                            for nz in range(2):
                                m_acc[z][a][nz] += xi[z][nz] / xs
            for z in range(2):
                for a in range(na):
                    mt = sum(m_acc[z][a])
                    self.M[z][a] = [x / mt for x in m_acc[z][a]]
                for s in range(ns):
                    for a in range(na):
                        et = sum(e_acc[z][s][a])
                        self.E[z][s][a] = [x / et for x in e_acc[z][s][a]]


class FactorizedStallTwoModeSheet(TwoModeLatentSheet):
    """28-parameter factorized-stall 2-mode latent sheet (shared active transitions x per-mode stall rate)."""

    def fit_em(self, trace: list[dict], *, iters: int = 20) -> None:
        rng = random.Random(self.seed)
        parsed = [(int(e["obs_code"]), int(e["action"]), int(e["next_obs_code"])) for e in trace]
        n, ns, na = len(parsed), self.n_states, self.n_actions

        move_c = [[[0.1] * ns for _ in range(na)] for _ in range(ns)]
        for s in range(ns):
            for a in range(na):
                move_c[s][a][s] = 0.0
        for o, a, no in parsed:
            if no != o:
                move_c[o][a][no] += 1.0
        P_move = []
        for s in range(ns):
            row_s = []
            for a in range(na):
                tot = sum(move_c[s][a])
                row_s.append([x / tot for x in move_c[s][a]] if tot > 0 else [1.0 if k == s else 0.0 for k in range(ns)])
            P_move.append(row_s)

        p_stall = [
            [0.75 + 0.10 * rng.random() for _ in range(na)],
            [0.15 + 0.10 * rng.random() for _ in range(na)],
        ]

        def emit_p(z: int, o: int, a: int, no: int) -> float:
            ps = p_stall[z][a]
            return max(1e-6, ps if no == o else (1.0 - ps) * P_move[o][a][no])

        for _ in range(iters):
            alpha = [[0.5, 0.5] for _ in range(n)]
            for t, (o, a, no) in enumerate(parsed):
                pred = [0.5, 0.5] if t == 0 else [
                    alpha[t - 1][0] * self.M[0][parsed[t - 1][1]][0] + alpha[t - 1][1] * self.M[1][parsed[t - 1][1]][0],
                    alpha[t - 1][0] * self.M[0][parsed[t - 1][1]][1] + alpha[t - 1][1] * self.M[1][parsed[t - 1][1]][1],
                ]
                a0, a1 = pred[0] * emit_p(0, o, a, no), pred[1] * emit_p(1, o, a, no)
                sc = a0 + a1
                alpha[t] = [a0 / sc, a1 / sc] if sc > 1e-12 else [0.5, 0.5]
            beta = [[1.0, 1.0] for _ in range(n)]
            for t in range(n - 2, -1, -1):
                _, a_t, _ = parsed[t]
                o_n, a_n, no_n = parsed[t + 1]
                e0, e1 = emit_p(0, o_n, a_n, no_n), emit_p(1, o_n, a_n, no_n)
                b0 = self.M[0][a_t][0] * e0 * beta[t + 1][0] + self.M[0][a_t][1] * e1 * beta[t + 1][1]
                b1 = self.M[1][a_t][0] * e0 * beta[t + 1][0] + self.M[1][a_t][1] * e1 * beta[t + 1][1]
                bs = b0 + b1
                beta[t] = [b0 / bs, b1 / bs] if bs > 1e-12 else [0.5, 0.5]
            m_acc = [[[0.5, 0.5] for _ in range(na)] for _ in range(2)]
            st_num = [[0.5] * na for _ in range(2)]
            st_den = [[1.0] * na for _ in range(2)]
            for t, (o, a, no) in enumerate(parsed):
                g0, g1 = alpha[t][0] * beta[t][0], alpha[t][1] * beta[t][1]
                gs = g0 + g1
                g0, g1 = (g0 / gs, g1 / gs) if gs > 1e-12 else (0.5, 0.5)
                is_st = 1.0 if no == o else 0.0
                st_num[0][a] += g0 * is_st
                st_den[0][a] += g0
                st_num[1][a] += g1 * is_st
                st_den[1][a] += g1
                if t < n - 1:
                    o_n, a_n, no_n = parsed[t + 1]
                    e0, e1 = emit_p(0, o_n, a_n, no_n), emit_p(1, o_n, a_n, no_n)
                    xi = [
                        [alpha[t][0] * self.M[0][a][0] * e0 * beta[t + 1][0], alpha[t][0] * self.M[0][a][1] * e1 * beta[t + 1][1]],
                        [alpha[t][1] * self.M[1][a][0] * e0 * beta[t + 1][0], alpha[t][1] * self.M[1][a][1] * e1 * beta[t + 1][1]],
                    ]
                    xs = xi[0][0] + xi[0][1] + xi[1][0] + xi[1][1]
                    if xs > 1e-12:
                        for z in range(2):
                            for nz in range(2):
                                m_acc[z][a][nz] += xi[z][nz] / xs
            for z in range(2):
                for a in range(na):
                    mt = sum(m_acc[z][a])
                    self.M[z][a] = [x / mt for x in m_acc[z][a]]
                    p_stall[z][a] = max(0.02, min(0.98, st_num[z][a] / st_den[z][a]))

        for z in range(2):
            for s in range(ns):
                for a in range(na):
                    ps = p_stall[z][a]
                    self.E[z][s][a] = [ps if k == s else (1.0 - ps) * P_move[s][a][k] for k in range(ns)]


class POHiddenModePlannerV9:
    """1-step filtered 2-mode latent-state planner (Cycle 21-22)."""

    def __init__(
        self,
        po_sheet: TwoModeLatentSheet,
        *,
        horizon: int = 4,
        gamma: float = 0.90,
        hazard: float = 0.015,
        explore_weight: float = 0.55,
    ):
        self.po_sheet = po_sheet
        self.n_bits = po_sheet.n_bits
        self.n_states = po_sheet.n_states
        self.n_actions = po_sheet.n_actions
        self.horizon = horizon
        self.gamma = gamma
        self.hazard = hazard
        self.explore_weight = explore_weight

        n_a = self.n_actions
        init_row = [1.0 / (n_a + 0.5)] * n_a + [0.5 / (n_a + 0.5)]
        s0 = sum(init_row)
        init_row = [x / s0 for x in init_row]
        self.role_beliefs = [list(init_row) for _ in range(n_a)]
        self.z_belief = [0.5, 0.5]
        self.fresh = FreshOnlineKBit(self.n_bits, n_a)

    def _effective_rows(self) -> list[list[float]]:
        return sinkhorn_sub_stochastic(self.role_beliefs, self.n_actions, iters=3)

    def choose_action(self, obs_code: int, goal_code: int) -> int:
        eff_rows = self._effective_rows()
        ns, na = self.n_states, self.n_actions
        n_prod = 2 * ns
        E_hat = [[[[0.0] * ns for _ in range(na)] for _ in range(ns)] for _ in range(2)]
        M_hat = [[[0.0, 0.0] for _ in range(na)] for _ in range(2)]
        for z in range(2):
            for a in range(na):
                aws = eff_rows[a]
                m0 = sum(aws[r] * self.po_sheet.M[z][r][0] for r in range(na)) + aws[na] * (1.0 if z == 0 else 0.0)
                M_hat[z][a] = [max(0.0, min(1.0, m0)), max(0.0, min(1.0, 1.0 - m0))]
                for s in range(ns):
                    fp = self.fresh.predict(s, a)
                    mix = [0.0] * ns
                    for r in range(na):
                        w = aws[r]
                        if w > 1e-6:
                            rp = self.po_sheet.E[z][s][r]
                            for k in range(ns):
                                mix[k] += w * rp[k]
                    wf = aws[na]
                    if wf > 1e-6:
                        for k in range(ns):
                            mix[k] += wf * fp[k]
                    E_hat[z][s][a] = mix

        V = [1.0 if (idx % ns) == goal_code else 0.0 for idx in range(n_prod)]
        for _ in range(self.horizon - 1):
            new_V = [0.0] * n_prod
            for z in range(2):
                for s in range(ns):
                    best_q = -1e9
                    for a in range(na):
                        eh, mh = E_hat[z][s][a], M_hat[z][a]
                        q = sum(eh[k] * (mh[0] * V[k] + mh[1] * V[ns + k]) for k in range(ns) if eh[k] > 1e-6)
                        if q > best_q:
                            best_q = q
                    new_V[z * ns + s] = (1.0 if s == goal_code else 0.0) + self.gamma * best_q
            V = new_V

        best_a, best_score = 0, -1e9
        for a in range(na):
            q_val = 0.0
            for z in range(2):
                eh, mh = E_hat[z][obs_code][a], M_hat[z][a]
                q_val += self.z_belief[z] * sum(eh[k] * (mh[0] * V[k] + mh[1] * V[ns + k]) for k in range(ns))
            aws = eff_rows[a]
            fp = self.fresh.predict(obs_code, a)
            rpreds = [
                [
                    self.z_belief[0] * self.po_sheet.E[0][obs_code][r][k]
                    + self.z_belief[1] * self.po_sheet.E[1][obs_code][r][k]
                    for k in range(ns)
                ]
                for r in range(na)
            ] + [fp]
            mix = [sum(aws[i] * rpreds[i][k] for i in range(na + 1)) for k in range(ns)]
            evgi = sum(
                aws[i] * sum((rpreds[i][k] - mix[k]) ** 2 for k in range(ns))
                for i in range(na + 1)
                if aws[i] > 1e-6
            )
            # Mode-transition EVGI (breaks 1-step aliasing at symmetric states like 000!)
            m_preds = [
                self.z_belief[0] * self.po_sheet.M[0][r][1] + self.z_belief[1] * self.po_sheet.M[1][r][1]
                for r in range(na)
            ] + [self.z_belief[1]]
            m_mix = sum(aws[i] * m_preds[i] for i in range(na + 1))
            mode_evgi = sum(aws[i] * ((m_preds[i] - m_mix) ** 2) for i in range(na + 1) if aws[i] > 1e-6)

            score = q_val + self.explore_weight * (evgi + 0.8 * mode_evgi)
            if score > best_score:
                best_score, best_a = score, a
        return best_a

    def update(self, obs_code: int, action: int, next_obs_code: int) -> None:
        na = self.n_actions
        n_cols = na + 1
        eff_rows = self._effective_rows()
        aws = eff_rows[action]
        fp = self.fresh.predict(obs_code, action)

        role_liks = [
            max(
                1e-6,
                self.z_belief[0] * self.po_sheet.E[0][obs_code][r][next_obs_code]
                + self.z_belief[1] * self.po_sheet.E[1][obs_code][r][next_obs_code],
            )
            for r in range(na)
        ] + [max(1e-6, fp[next_obs_code])]

        post_r = [self.role_beliefs[action][i] * role_liks[i] for i in range(n_cols)]
        pr_s = sum(post_r)
        post_r = [x / pr_s for x in post_r]
        unif = 1.0 / n_cols
        self.role_beliefs[action] = [(1.0 - self.hazard) * x + self.hazard * unif for x in post_r]

        z_lik = [
            self.z_belief[z]
            * max(1e-6, sum(aws[r] * self.po_sheet.E[z][obs_code][r][next_obs_code] for r in range(na)) + aws[na] * fp[next_obs_code])
            for z in range(2)
        ]
        zs = z_lik[0] + z_lik[1]
        z_post = [z_lik[0] / zs, z_lik[1] / zs] if zs > 1e-12 else [0.5, 0.5]

        next_z = [0.0, 0.0]
        for z in range(2):
            m0 = sum(aws[r] * self.po_sheet.M[z][r][0] for r in range(na)) + aws[na] * (1.0 if z == 0 else 0.0)
            next_z[0] += z_post[z] * m0
            next_z[1] += z_post[z] * (1.0 - m0)
        self.z_belief = [0.95 * next_z[0] + 0.025, 0.95 * next_z[1] + 0.025]
        self.fresh.update(obs_code, action, next_obs_code)


class POHiddenModePlannerV10(POHiddenModePlannerV9):
    """
    Cycle 23-24 upgrade:
    Adds exact 1-step backward message passing (2-step retroactive mode-transition credit)
    + Coupled Broadcast Changepoint Hazard for mid-episode lever swaps.
    """

    def __init__(self, po_sheet: TwoModeLatentSheet, **kwargs):
        super().__init__(po_sheet, **kwargs)
        self._prev_action: int | None = None
        self._prev_z_post: list[float] = [0.5, 0.5]
        self._steps = 0
        self._surprise_win: list[int] = []
        self._last_bcast = -100

    def update(self, obs_code: int, action: int, next_obs_code: int) -> None:
        na = self.n_actions
        n_cols = na + 1
        eff_rows = self._effective_rows()
        aws = eff_rows[action]
        fp = self.fresh.predict(obs_code, action)
        old_map = max(range(n_cols), key=lambda r: self.role_beliefs[action][r])

        # Compute step-t emission likelihood under each latent mode z in {0, 1}
        ell_z = [
            max(1e-6, sum(aws[r] * self.po_sheet.E[z][obs_code][r][next_obs_code] for r in range(na)) + aws[na] * fp[next_obs_code])
            for z in range(2)
        ]
        pred_prob = self.z_belief[0] * ell_z[0] + self.z_belief[1] * ell_z[1]

        # 1. Exact 2-Step Retroactive Mode-Transition Credit for self._prev_action!
        # Breaks observational aliasing (e.g. swap(000)==noop(000)) when step t reveals mode z_t!
        if self._prev_action is not None:
            pa = self._prev_action
            pz0, pz1 = self._prev_z_post
            retro_liks = []
            for r in range(na):
                # sum_{z, z'} P(z_{t-1}=z) * M[z][r][z'] * ell_t(z')
                l_r = (
                    pz0 * (self.po_sheet.M[0][r][0] * ell_z[0] + self.po_sheet.M[0][r][1] * ell_z[1])
                    + pz1 * (self.po_sheet.M[1][r][0] * ell_z[0] + self.po_sheet.M[1][r][1] * ell_z[1])
                )
                retro_liks.append(max(1e-6, l_r))
            retro_liks.append(max(1e-6, pz0 * ell_z[0] + pz1 * ell_z[1]))
            pr_prev = [self.role_beliefs[pa][i] * retro_liks[i] for i in range(n_cols)]
            prs = sum(pr_prev)
            if prs > 1e-12:
                self.role_beliefs[pa] = [x / prs for x in pr_prev]

        # 2. Standard step-t role belief update + hazard floor
        role_liks = [
            max(
                1e-6,
                self.z_belief[0] * self.po_sheet.E[0][obs_code][r][next_obs_code]
                + self.z_belief[1] * self.po_sheet.E[1][obs_code][r][next_obs_code],
            )
            for r in range(na)
        ] + [max(1e-6, fp[next_obs_code])]
        post_r = [self.role_beliefs[action][i] * role_liks[i] for i in range(n_cols)]
        pr_s = sum(post_r)
        post_r = [x / pr_s for x in post_r]
        unif = 1.0 / n_cols
        self.role_beliefs[action] = [(1.0 - self.hazard) * x + self.hazard * unif for x in post_r]
        new_map = max(range(n_cols), key=lambda r: self.role_beliefs[action][r])

        # 3. 2-Step Confirmed Broadcast Hazard for silent mid-episode lever swaps
        self._surprise_win.append(1 if (pred_prob < 0.12 or new_map != old_map) else 0)
        if len(self._surprise_win) > 4:
            self._surprise_win.pop(0)
        if self.hazard > 0.0 and self._steps >= 20 and sum(self._surprise_win) >= 2 and (self._steps - self._last_bcast) >= 12:
            pulse = 0.30
            for oa in range(na):
                if oa != action:
                    self.role_beliefs[oa] = [(1.0 - pulse) * x + pulse * unif for x in self.role_beliefs[oa]]
            self._last_bcast = self._steps
            self._surprise_win.clear()

        # 4. Update & propagate z_belief
        z_lik = [self.z_belief[0] * ell_z[0], self.z_belief[1] * ell_z[1]]
        zs = z_lik[0] + z_lik[1]
        z_post = [z_lik[0] / zs, z_lik[1] / zs] if zs > 1e-12 else [0.5, 0.5]

        self._prev_action = action
        self._prev_z_post = list(z_post)

        next_z = [0.0, 0.0]
        for z in range(2):
            m0 = sum(aws[r] * self.po_sheet.M[z][r][0] for r in range(na)) + aws[na] * (1.0 if z == 0 else 0.0)
            next_z[0] += z_post[z] * m0
            next_z[1] += z_post[z] * (1.0 - m0)
        self.z_belief = [0.95 * next_z[0] + 0.025, 0.95 * next_z[1] + 0.025]
        self.fresh.update(obs_code, action, next_obs_code)
        self._steps += 1


def serialize_po_v10(planner: POHiddenModePlannerV10) -> bytes:
    """Canonical deterministic JSON serialization for POHiddenModePlannerV10."""
    payload = {
        "schema": "yggdrasil.scdr.po_v10.cold_state.v1",
        "n_bits": planner.n_bits,
        "n_actions": planner.n_actions,
        "horizon": planner.horizon,
        "gamma": planner.gamma,
        "hazard": planner.hazard,
        "explore_weight": planner.explore_weight,
        "M": planner.po_sheet.M,
        "E": planner.po_sheet.E,
        "role_beliefs": planner.role_beliefs,
        "z_belief": planner.z_belief,
        "fresh_counts": planner.fresh.counts,
        "prev_action": planner._prev_action,
        "prev_z_post": planner._prev_z_post,
        "steps": planner._steps,
        "surprise_win": planner._surprise_win,
        "last_bcast": planner._last_bcast,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def deserialize_po_v10(raw: bytes) -> POHiddenModePlannerV10:
    """Restore POHiddenModePlannerV10 bit-exactly from canonical JSON bytes."""
    d = json.loads(raw.decode("utf-8"))
    if d.get("schema") != "yggdrasil.scdr.po_v10.cold_state.v1":
        raise ValueError("SCDR_INVALID_PO_V10_SCHEMA")
    sheet = FactorizedStallTwoModeSheet(int(d["n_bits"]), int(d["n_actions"]))
    sheet.M = [[[float(x) for x in r] for r in mat] for mat in d["M"]]
    sheet.E = [[[[float(x) for x in row] for row in mat] for mat in st] for st in d["E"]]
    pl = POHiddenModePlannerV10(
        sheet,
        horizon=int(d["horizon"]),
        gamma=float(d["gamma"]),
        hazard=float(d["hazard"]),
        explore_weight=float(d["explore_weight"]),
    )
    pl.role_beliefs = [[float(x) for x in row] for row in d["role_beliefs"]]
    pl.z_belief = [float(x) for x in d["z_belief"]]
    pl.fresh.counts = [[[float(x) for x in row] for row in mat] for mat in d["fresh_counts"]]
    pl._prev_action = d["prev_action"]
    pl._prev_z_post = [float(x) for x in d["prev_z_post"]]
    pl._steps = int(d["steps"])
    pl._surprise_win = [int(x) for x in d["surprise_win"]]
    pl._last_bcast = int(d["last_bcast"])
    return pl
