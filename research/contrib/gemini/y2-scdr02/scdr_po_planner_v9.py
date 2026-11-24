"""
SCDR-PO-Planner-v9 (Cycles 20-21):
1. Deterministic Cold-Save / Cold-Restore JSON serialization with SHA-256 custody receipt
   for GeneralSheetKBit and SCDRMultiStepPlannerV8 (bit-exact mid-episode reload).
2. Partially Observable 2-Mode Latent-State SCDR Planner (POHiddenModePlannerV9):
   - Discovers 2 latent dynamical modes (e.g., locked vs. unlocked) purely from PUBLIC
     passive transitions using 2-component Baum-Welch / EM over action-conditioned transitions
     (zero hidden/oracle labels ever exposed!).
   - Transfers the 2-mode causal model into an unfamiliar permuted |A|-action world using
     Hazard-Floored Sub-Stochastic Sinkhorn Soft-Exclusion.
   - Plans via exact H-step Value Iteration over the 2*|S|-state (obs, latent_mode) product MDP!

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
    """
    Discovers 2 latent dynamical modes (z in {0, 1}) purely from PUBLIC (obs, action, next_obs)
    sequences via compact action-conditioned 2-state EM (Baum-Welch):
    - Mode transition: M[z][a][z'] = P(z_{t+1} = z' | z_t = z, action = a)
    - Observation transition: E[z][s][a][s'] = P(s_{t+1} = s' | z_t = z, s_t = s, action = a)
    Zero oracle/hidden labels are ever passed.
    """

    def __init__(self, n_bits: int, n_actions: int, seed: int = 7):
        self.n_bits = n_bits
        self.n_states = 1 << n_bits
        self.n_actions = n_actions
        self.seed = seed
        # M[z][a][nz]
        self.M = [[[0.85 if z == nz else 0.15 for nz in range(2)] for _ in range(n_actions)] for z in range(2)]
        # E[z][s][a][ns]
        self.E = [[[[1.0 / self.n_states] * self.n_states for _ in range(n_actions)] for _ in range(self.n_states)] for _ in range(2)]

    def fit_em(self, trace: list[dict], *, iters: int = 12) -> None:
        rng = random.Random(self.seed)
        parsed = [(int(e["obs_code"]), int(e["action"]), int(e["next_obs_code"])) for e in trace]
        n = len(parsed)
        ns = self.n_states
        na = self.n_actions

        # Initialize E with empirical base counts + small asymmetric noise to break mode symmetry
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
            # Forward pass
            alpha = [[0.5, 0.5] for _ in range(n)]
            scales = [1.0] * n
            for t, (o, a, no) in enumerate(parsed):
                if t == 0:
                    pred = [0.5, 0.5]
                else:
                    pa = parsed[t - 1][1]
                    pred = [
                        alpha[t - 1][0] * self.M[0][pa][0] + alpha[t - 1][1] * self.M[1][pa][0],
                        alpha[t - 1][0] * self.M[0][pa][1] + alpha[t - 1][1] * self.M[1][pa][1],
                    ]
                a0 = pred[0] * max(1e-6, self.E[0][o][a][no])
                a1 = pred[1] * max(1e-6, self.E[1][o][a][no])
                sc = a0 + a1
                if sc <= 1e-12:
                    a0, a1, sc = 0.5, 0.5, 1.0
                alpha[t] = [a0 / sc, a1 / sc]
                scales[t] = sc

            # Backward pass
            beta = [[1.0, 1.0] for _ in range(n)]
            for t in range(n - 2, -1, -1):
                _, a_t, _ = parsed[t]
                o_n, a_n, no_n = parsed[t + 1]
                e0 = max(1e-6, self.E[0][o_n][a_n][no_n])
                e1 = max(1e-6, self.E[1][o_n][a_n][no_n])
                b0 = self.M[0][a_t][0] * e0 * beta[t + 1][0] + self.M[0][a_t][1] * e1 * beta[t + 1][1]
                b1 = self.M[1][a_t][0] * e0 * beta[t + 1][0] + self.M[1][a_t][1] * e1 * beta[t + 1][1]
                bs = b0 + b1
                if bs <= 1e-12:
                    b0, b1, bs = 0.5, 0.5, 1.0
                beta[t] = [b0 / bs, b1 / bs]

            # M-step
            m_acc = [[[0.5, 0.5] for _ in range(na)] for _ in range(2)]
            e_acc = [[[[0.25] * ns for _ in range(na)] for _ in range(ns)] for _ in range(2)]
            for t, (o, a, no) in enumerate(parsed):
                g0 = alpha[t][0] * beta[t][0]
                g1 = alpha[t][1] * beta[t][1]
                gs = g0 + g1
                if gs > 1e-12:
                    g0 /= gs
                    g1 /= gs
                else:
                    g0 = g1 = 0.5
                e_acc[0][o][a][no] += g0
                e_acc[1][o][a][no] += g1

                if t < n - 1:
                    o_n, a_n, no_n = parsed[t + 1]
                    e0 = max(1e-6, self.E[0][o_n][a_n][no_n])
                    e1 = max(1e-6, self.E[1][o_n][a_n][no_n])
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


class POHiddenModePlannerV9:
    """
    Partially Observable 2-Mode Latent-State SCDR Planner:
    - Tracks online latent mode belief b_z = [P(z=0), P(z=1)] simultaneously with
      Hazard-Floored Sub-Stochastic Sinkhorn action-role beliefs!
    - Plans over the 2*|S|-state (obs, z) product MDP using exact H-step Value Iteration.
    """

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
        ns = self.n_states
        na = self.n_actions

        # Build 16-state (z, s) expected transition tensor under current Sinkhorn role beliefs
        # State index = z * ns + s
        n_prod = 2 * ns
        # Expected obs transition E_hat[z][s][a][s'] and mode transition M_hat[z][a][z']
        E_hat = [[[[0.0] * ns for _ in range(na)] for _ in range(ns)] for _ in range(2)]
        M_hat = [[[0.0, 0.0] for _ in range(na)] for _ in range(2)]
        for z in range(2):
            for a in range(na):
                aws = eff_rows[a]
                # Mode transition
                m0 = sum(aws[r] * self.po_sheet.M[z][r][0] for r in range(na)) + aws[na] * (1.0 if z == 0 else 0.0)
                m1 = 1.0 - m0
                M_hat[z][a] = [max(0.0, min(1.0, m0)), max(0.0, min(1.0, m1))]
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

        # Exact H-step Bellman Value Iteration over 2*|S| product states!
        V = [1.0 if (idx % ns) == goal_code else 0.0 for idx in range(n_prod)]
        for _ in range(self.horizon - 1):
            new_V = [0.0] * n_prod
            for z in range(2):
                for s in range(ns):
                    best_q = -1e9
                    for a in range(na):
                        eh = E_hat[z][s][a]
                        mh = M_hat[z][a]
                        q = 0.0
                        for k in range(ns):
                            if eh[k] > 1e-6:
                                q += eh[k] * (mh[0] * V[k] + mh[1] * V[ns + k])
                        if q > best_q:
                            best_q = q
                    new_V[z * ns + s] = (1.0 if s == goal_code else 0.0) + self.gamma * best_q
            V = new_V

        # Score actions at current (z_belief, obs_code) + EVGI exploration
        best_a, best_score = 0, -1e9
        for a in range(na):
            q_val = 0.0
            for z in range(2):
                eh = E_hat[z][obs_code][a]
                mh = M_hat[z][a]
                qz = sum(eh[k] * (mh[0] * V[k] + mh[1] * V[ns + k]) for k in range(ns))
                q_val += self.z_belief[z] * qz

            # EVGI across roles weighted by z_belief
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
            score = q_val + self.explore_weight * evgi
            if score > best_score:
                best_score, best_a = score, a
        return best_a

    def update(self, obs_code: int, action: int, next_obs_code: int) -> None:
        na = self.n_actions
        n_cols = na + 1
        eff_rows = self._effective_rows()
        aws = eff_rows[action]
        fp = self.fresh.predict(obs_code, action)

        # 1. Update role beliefs marginalized over current z_belief
        role_liks = []
        for r in range(na):
            p_r = (
                self.z_belief[0] * self.po_sheet.E[0][obs_code][r][next_obs_code]
                + self.z_belief[1] * self.po_sheet.E[1][obs_code][r][next_obs_code]
            )
            role_liks.append(max(1e-6, p_r))
        role_liks.append(max(1e-6, fp[next_obs_code]))

        post_r = [self.role_beliefs[action][i] * role_liks[i] for i in range(n_cols)]
        pr_s = sum(post_r)
        post_r = [x / pr_s for x in post_r]
        unif = 1.0 / n_cols
        self.role_beliefs[action] = [(1.0 - self.hazard) * x + self.hazard * unif for x in post_r]

        # 2. Update latent mode belief z_belief (Bayes filter + propagate via M_hat)
        z_lik = [0.0, 0.0]
        for z in range(2):
            p_z = sum(aws[r] * self.po_sheet.E[z][obs_code][r][next_obs_code] for r in range(na)) + aws[na] * fp[next_obs_code]
            z_lik[z] = self.z_belief[z] * max(1e-6, p_z)
        zs = z_lik[0] + z_lik[1]
        z_post = [z_lik[0] / zs, z_lik[1] / zs] if zs > 1e-12 else [0.5, 0.5]

        # Propagate z_post -> z_next via learned mode transition M
        next_z = [0.0, 0.0]
        for z in range(2):
            m0 = sum(aws[r] * self.po_sheet.M[z][r][0] for r in range(na)) + aws[na] * (1.0 if z == 0 else 0.0)
            next_z[0] += z_post[z] * m0
            next_z[1] += z_post[z] * (1.0 - m0)
        # Small floor so latent mode stays responsive to silent resets (e.g. relock on goal hit)
        self.z_belief = [0.95 * next_z[0] + 0.025, 0.95 * next_z[1] + 0.025]
        self.fresh.update(obs_code, action, next_obs_code)
