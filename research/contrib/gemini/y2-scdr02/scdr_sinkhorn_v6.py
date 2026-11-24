"""
SCDR-RoleCell-v6: Sub-Stochastic Sinkhorn Soft-Exclusion Factorized Role Binding
+ Joint Sensory-Motor Symmetry Gauge + Selective Per-Action Epistemic Abstention.

Pure Python stdlib, O(|A|^2) scaling to arbitrary |A|-action and k-bit public observation spaces.
Strictly public-only interface; never accesses hidden state or locked CAL seeds.
"""

from __future__ import annotations

import math
from typing import Iterable

OBS_SYMMETRIES = [(sw, xm) for sw in (False, True) for xm in range(4)]


def _mean(vals: Iterable[float]) -> float:
    lst = list(vals)
    return sum(lst) / len(lst) if lst else 0.0


def apply_obs_sym(code_val: int, sym: tuple[bool, int]) -> int:
    sw, xm = sym
    b0, b1 = (code_val >> 1) & 1, code_val & 1
    if sw:
        b0, b1 = b1, b0
    return ((b0 << 1) | b1) ^ xm


def invert_obs_sym(code_val: int, sym: tuple[bool, int]) -> int:
    sw, xm = sym
    u = code_val ^ xm
    b0, b1 = (u >> 1) & 1, u & 1
    if sw:
        b0, b1 = b1, b0
    return (b0 << 1) | b1


def map_probs_by_sym(probs: list[float], sym: tuple[bool, int]) -> list[float]:
    out = [0.0, 0.0, 0.0, 0.0]
    for canon_o, p in enumerate(probs):
        out[apply_obs_sym(canon_o, sym)] = p
    return out


def multichannel_brier_nbits(probs: list[float], target: int, n_bits: int) -> float:
    tot = sum(probs)
    if tot <= 0.0:
        raise ValueError("SCDR_V6_INVALID_PROBS")
    norm = [x / tot for x in probs]
    n_states = 1 << n_bits
    err = 0.0
    for b in range(n_bits):
        shift = n_bits - 1 - b
        pb = sum(norm[s] for s in range(n_states) if (s >> shift) & 1)
        yb = (target >> shift) & 1
        err += (pb - yb) ** 2
    return err / n_bits


def sinkhorn_sub_stochastic(raw_rows: list[list[float]], n_actions: int, iters: int = 3) -> list[list[float]]:
    """
    Sub-stochastic Sinkhorn soft-exclusion over the |A|x|A| known-role block.
    - Leaves column n_actions (Fresh_a) un-competed so brand-new actions abstain freely.
    - Caps column sums with max(1.0, col_sum) so claimed roles are suppressed for undecided actions
      without forcing novel actions onto unused roles.
    """
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


def parse_public_event(ev: dict, n_states: int, n_actions: int) -> tuple[int, int, int]:
    if not isinstance(ev, dict):
        raise ValueError("SCDR_V6_INVALID_EVENT")
    if set(ev.keys()) == {"obs_code", "action", "next_obs_code"}:
        o, a, no = ev["obs_code"], ev["action"], ev["next_obs_code"]
    elif set(ev.keys()) == {"observation", "action", "next_observation"}:
        obs, nobs = ev["observation"], ev["next_observation"]
        if len(obs) != 2 or len(nobs) != 2:
            raise ValueError("SCDR_V6_INVALID_OBS_BITS")
        o = (int(obs[0]) << 1) | int(obs[1])
        no = (int(nobs[0]) << 1) | int(nobs[1])
        a = ev["action"]
    else:
        raise ValueError("SCDR_V6_NON_PUBLIC_EVENT_SCHEMA")
    if type(o) is not int or not (0 <= o < n_states):
        raise ValueError("SCDR_V6_INVALID_OBS_CODE")
    if type(no) is not int or not (0 <= no < n_states):
        raise ValueError("SCDR_V6_INVALID_NEXT_OBS_CODE")
    if type(a) is not int or not (0 <= a < n_actions):
        raise ValueError("SCDR_V6_INVALID_ACTION")
    return o, a, no


class GeneralSheetKBit:
    """Arbitrary (n_bits, n_actions) public causal contract sheet."""

    def __init__(self, n_bits: int, n_actions: int):
        self.n_bits = n_bits
        self.n_states = 1 << n_bits
        self.n_actions = n_actions
        self.counts = [[[0.5] * self.n_states for _ in range(n_actions)] for _ in range(self.n_states)]

    def fit(self, trace: list[dict]) -> None:
        for ev in trace:
            o, a, no = parse_public_event(ev, self.n_states, self.n_actions)
            self.counts[o][a][no] += 1.0

    def predict(self, prev_ctx, o: int, a: int) -> list[float]:
        c = self.counts[o][a]
        tot = sum(c)
        return [x / tot for x in c]


class FreshOnlineKBit:
    """Online Dirichlet fallback contract for novel actions or out-of-family worlds."""

    def __init__(self, n_bits: int, n_actions: int):
        self.n_states = 1 << n_bits
        self.counts = [[[0.5] * self.n_states for _ in range(n_actions)] for _ in range(self.n_states)]

    def predict(self, o: int, a: int) -> list[float]:
        c = self.counts[o][a]
        tot = sum(c)
        return [x / tot for x in c]

    def update(self, o: int, a: int, no: int) -> None:
        self.counts[o][a][no] += 1.0


class SinkhornRoleCellV6:
    """
    O(|A|^2) Factorized Per-Action Role Binding with:
    - Sub-Stochastic Sinkhorn Soft-Exclusion (iters=3)
    - Optional 2-bit sensory symmetry gauge (bit-swap + XOR)
    - MAP-inferred canonical predecessor mapping for H1-split sheets
    - Selective per-action epistemic abstention via un-competed Fresh_a column
    """

    def __init__(
        self,
        sheets: list,
        n_bits: int,
        n_actions: int,
        *,
        use_sinkhorn: bool = True,
        sinkhorn_iters: int = 3,
        use_obs_symmetry: bool = False,
        decay: float = 0.97,
    ):
        self.sheets = sheets
        self.n_bits = n_bits
        self.n_states = 1 << n_bits
        self.n_actions = n_actions
        self.use_sinkhorn = use_sinkhorn
        self.sinkhorn_iters = sinkhorn_iters
        self.obs_syms = OBS_SYMMETRIES if (use_obs_symmetry and n_bits == 2) else [(False, 0)]
        self.decay = decay

    def score_stream(self, trace: list[dict]) -> dict:
        outer_hyps = [(si, sym) for si in range(len(self.sheets)) for sym in self.obs_syms]
        n_outer = len(outer_hyps)
        outer_log_w = [0.0] * (n_outer + 1)

        action_log_w = [
            [[0.0] * self.n_actions + [-0.4] for _ in range(self.n_actions)]
            for _ in range(n_outer)
        ]
        fresh = FreshOnlineKBit(self.n_bits, self.n_actions)
        losses = []
        per_action_abstain = [0.0] * self.n_actions
        prev_obs: int | None = None
        prev_action: int | None = None

        for ev in trace:
            po, pa, pno = parse_public_event(ev, self.n_states, self.n_actions)

            om = max(outer_log_w)
            ows = [math.exp(lw - om) for lw in outer_log_w]
            osw = sum(ows)
            ows = [w / osw for w in ows]

            fresh_p = fresh.predict(po, pa)
            outer_preds = []
            abstain_mass = ows[-1]

            for oi, (si, sym) in enumerate(outer_hyps):
                sheet = self.sheets[si]
                canon_o = invert_obs_sym(po, sym) if self.n_bits == 2 else po

                canon_pctx = None
                if prev_obs is not None and prev_action is not None:
                    prev_alw = action_log_w[oi][prev_action]
                    best_prev_r = max(range(self.n_actions + 1), key=lambda r: prev_alw[r])
                    if best_prev_r < self.n_actions:
                        cpo = invert_obs_sym(prev_obs, sym) if self.n_bits == 2 else prev_obs
                        canon_pctx = (cpo, best_prev_r)

                raw_rows = []
                for a_idx in range(self.n_actions):
                    alw = action_log_w[oi][a_idx]
                    am = max(alw)
                    r = [math.exp(lw - am) for lw in alw]
                    rs = sum(r)
                    raw_rows.append([x / rs for x in r])

                eff_rows = (
                    sinkhorn_sub_stochastic(raw_rows, self.n_actions, iters=self.sinkhorn_iters)
                    if self.use_sinkhorn
                    else raw_rows
                )
                aws = eff_rows[pa]

                if self.n_bits == 2:
                    role_preds = [
                        map_probs_by_sym(sheet.predict(canon_pctx, canon_o, r), sym)
                        for r in range(self.n_actions)
                    ] + [fresh_p]
                else:
                    role_preds = [sheet.predict(canon_pctx, canon_o, r) for r in range(self.n_actions)] + [fresh_p]

                op = [0.0] * self.n_states
                for ri in range(self.n_actions + 1):
                    w = aws[ri]
                    rp = role_preds[ri]
                    for c in range(self.n_states):
                        op[c] += w * rp[c]
                outer_preds.append((op, role_preds))
                abstain_mass += ows[oi] * aws[self.n_actions]

            mix = [0.0] * self.n_states
            for oi, (op, _) in enumerate(outer_preds):
                w = ows[oi]
                for c in range(self.n_states):
                    mix[c] += w * op[c]
            w_ood = ows[-1]
            for c in range(self.n_states):
                mix[c] += w_ood * fresh_p[c]

            losses.append(multichannel_brier_nbits(mix, pno, self.n_bits))
            per_action_abstain[pa] = abstain_mass

            for oi, (op, role_preds) in enumerate(outer_preds):
                outer_log_w[oi] = self.decay * outer_log_w[oi] + math.log(max(1e-6, op[pno]))
                for ri in range(self.n_actions + 1):
                    action_log_w[oi][pa][ri] = self.decay * action_log_w[oi][pa][ri] + math.log(max(1e-6, role_preds[ri][pno]))
            outer_log_w[-1] = self.decay * outer_log_w[-1] + math.log(max(1e-6, fresh_p[pno]))
            fresh.update(po, pa, pno)
            prev_obs, prev_action = po, pa

        return {
            "brier_mean": _mean(losses),
            "brier_30": _mean(losses[:30]),
            "brier_60": _mean(losses[:60]),
            "brier_120": _mean(losses[:120]),
            "abstain_per_action": per_action_abstain,
            "ood_outer_w": ows[-1] if trace else 0.0,
        }
