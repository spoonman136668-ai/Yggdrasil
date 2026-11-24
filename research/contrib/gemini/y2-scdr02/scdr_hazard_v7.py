"""
SCDR-RoleCell-v7 (Cycles 8-9):
1. HazardSinkhornRoleCellV7: Bayesian Changepoint Hazard Flooring in probability space (h=0.015)
   before Sub-Stochastic Sinkhorn Soft-Exclusion, enabling rapid mid-episode re-binding after
   silent action-permutation swaps without stationary accuracy loss.
2. LatchAndBonferroniH1Sheet: Bonferroni-corrected Multi-Lag H1 Sheaf Splitting (lags 1..3)
   paired with an Event-Triggered Variable-Lag Causal Witness Latch.

Pure Python stdlib, strictly public-only interface.
"""

from __future__ import annotations

from scdr_sinkhorn_v6 import (
    FreshOnlineKBit,
    _mean,
    multichannel_brier_nbits,
    parse_public_event,
    sinkhorn_sub_stochastic,
)


class HazardSinkhornRoleCellV7:
    """
    Bayesian Changepoint Hazard-Floored Sinkhorn Role Binding.
    Applies p_prior(r) = (1 - h) * p_post(r) + h / (|A| + 1) in probability space
    so silent mid-episode gauge shifts re-bind in ~2-3 action uses instead of getting
    trapped by accumulated log-odds.
    """

    def __init__(self, sheets: list, n_bits: int, n_actions: int, *, hazard: float = 0.015, sinkhorn_iters: int = 3):
        self.sheets = sheets
        self.n_bits = n_bits
        self.n_states = 1 << n_bits
        self.n_actions = n_actions
        self.hazard = hazard
        self.sinkhorn_iters = sinkhorn_iters

    def score_stream(self, trace: list[dict]) -> dict:
        sheet = self.sheets[0]
        n_cols = self.n_actions + 1
        init_row = [1.0 / (self.n_actions + 0.6)] * self.n_actions + [0.6 / (self.n_actions + 0.6)]
        s0 = sum(init_row)
        init_row = [x / s0 for x in init_row]
        beliefs = [list(init_row) for _ in range(self.n_actions)]
        fresh = FreshOnlineKBit(self.n_bits, self.n_actions)
        losses = []

        for ev in trace:
            po, pa, pno = parse_public_event(ev, self.n_states, self.n_actions)
            eff_rows = sinkhorn_sub_stochastic(beliefs, self.n_actions, iters=self.sinkhorn_iters)
            aws = eff_rows[pa]
            fresh_p = fresh.predict(po, pa)
            role_preds = [sheet.predict(None, po, r) for r in range(self.n_actions)] + [fresh_p]

            mix = [0.0] * self.n_states
            for ri in range(n_cols):
                w = aws[ri]
                rp = role_preds[ri]
                for c in range(self.n_states):
                    mix[c] += w * rp[c]
            losses.append(multichannel_brier_nbits(mix, pno, self.n_bits))

            post = [beliefs[pa][ri] * max(1e-6, role_preds[ri][pno]) for ri in range(n_cols)]
            ps = sum(post)
            post = [x / ps for x in post]
            unif = 1.0 / n_cols
            beliefs[pa] = [(1.0 - self.hazard) * x + self.hazard * unif for x in post]
            fresh.update(po, pa, pno)

        return {
            "losses": losses,
            "brier_mean": _mean(losses),
            "abstain_per_action": [row[self.n_actions] for row in beliefs],
        }


class LatchAndBonferroniH1Sheet:
    """
    2-bit, 3-action causal contract sheet combining:
    - Bonferroni-corrected Multi-Lag H1 Sheaf Splitting (lags 1..3, hurdle = 0.42 + 0.12*(lag-1))
    - Variable-Lag Event-Triggered Causal Witness Latch (hurdle = max(0.45, 0.0045*N))
    """

    def __init__(self, max_lag: int = 3):
        self.max_lag = max_lag
        self.base_counts = [[[0.5] * 4 for _ in range(3)] for _ in range(4)]
        self.lag_splits: dict[int, tuple[int, dict[tuple[int, int], int]]] = {}
        self.lag_counts: dict[tuple[int, int], list[list[float]]] = {}
        self.latch_action: int | None = None
        self.latch_counts: list[list[list[list[float]]]] | None = None

    def _base_probs(self, o: int, a: int) -> list[float]:
        c = self.base_counts[o][a]
        tot = sum(c)
        return [x / tot for x in c]

    def fit(self, trace: list[dict]) -> dict:
        parsed = [parse_public_event(e, 4, 3) for e in trace]
        for o, a, no in parsed:
            self.base_counts[o][a][no] += 1.0

        split_idx = int(len(parsed) * 0.6)
        tr_p, va_p = parsed[:split_idx], parsed[split_idx:]
        local_base = [[[0.5] * 4 for _ in range(3)] for _ in range(4)]
        for o, a, no in tr_p:
            local_base[o][a][no] += 1.0

        best_latch = None
        for a_star in range(3):
            base_c = [[[0.5] * 4 for _ in range(3)] for _ in range(4)]
            lat_c = [[[[0.5] * 4 for _ in range(3)] for _ in range(4)] for _ in range(4)]
            lv: int | None = None
            for eo, ea, eno in tr_p:
                base_c[eo][ea][eno] += 1.0
                if lv is not None:
                    lat_c[lv][eo][ea][eno] += 1.0
                if ea == a_star:
                    lv = eno

            bl = ll = 0.0
            nv = 0
            lv = None
            for eo, ea, eno in va_p:
                if lv is not None:
                    bt = sum(base_c[eo][ea])
                    bp = [x / bt for x in base_c[eo][ea]]
                    lc = lat_c[lv][eo][ea]
                    lt = sum(lc)
                    w = max(0.0, (lt - 2.0) / (lt + 3.0))
                    lp = [w * (x / lt) + (1.0 - w) * b for x, b in zip(lc, bp)]
                    bl += multichannel_brier_nbits(bp, eno, 2)
                    ll += multichannel_brier_nbits(lp, eno, 2)
                    nv += 1
                    lat_c[lv][eo][ea][eno] += 1.0
                base_c[eo][ea][eno] += 1.0
                if ea == a_star:
                    lv = eno

            gain = bl - ll
            hurdle = max(0.45, 0.0045 * nv)
            if nv >= 40 and gain > hurdle:
                if best_latch is None or gain > best_latch[0]:
                    best_latch = (gain, a_star, lat_c)

        if best_latch is not None:
            _, a_star, lat_c = best_latch
            self.latch_action = a_star
            self.latch_counts = lat_c

        for o in range(4):
            best_for_o = None
            for lag in range(1, self.max_lag + 1):
                local_pred: dict[tuple[int, int], list[list[float]]] = {}
                for i in range(lag, len(tr_p)):
                    eo, ea, eno = tr_p[i]
                    if eo != o:
                        continue
                    po, pa, _ = tr_p[i - lag]
                    tbl = local_pred.setdefault((po, pa), [[0.0] * 4 for _ in range(3)])
                    tbl[ea][eno] += 1.0

                preds, vecs = [], []
                for pk, tbl in local_pred.items():
                    if sum(sum(r) for r in tbl) < 8:
                        continue
                    vec = []
                    for a in range(3):
                        s = sum(tbl[a])
                        if s > 0:
                            vec.extend([x / s for x in tbl[a]])
                        else:
                            bt = sum(local_base[o][a])
                            vec.extend([x / bt for x in local_base[o][a]])
                    preds.append(pk)
                    vecs.append(vec)
                if len(preds) < 2:
                    continue

                bp, bd = (0, 1), -1.0
                for i in range(len(vecs)):
                    for j in range(i + 1, len(vecs)):
                        d = sum(abs(x - y) for x, y in zip(vecs[i], vecs[j]))
                        if d > bd:
                            bd, bp = d, (i, j)
                c0, c1 = list(vecs[bp[0]]), list(vecs[bp[1]])
                assign = [0] * len(preds)
                for _ in range(8):
                    na = [
                        0 if sum(abs(x - y) for x, y in zip(v, c0)) <= sum(abs(x - y) for x, y in zip(v, c1)) else 1
                        for v in vecs
                    ]
                    if na == assign:
                        break
                    assign = na
                    for cid in (0, 1):
                        mem = [vecs[k] for k, c in enumerate(assign) if c == cid]
                        if mem:
                            avg = [sum(m[d] for m in mem) / len(mem) for d in range(len(c0))]
                            if cid == 0:
                                c0 = avg
                            else:
                                c1 = avg
                if len(set(assign)) < 2:
                    continue
                mapping = {preds[k]: assign[k] for k in range(len(preds))}

                base_c = [[0.5] * 4 for _ in range(3)]
                spl_c = [[[0.5] * 4 for _ in range(3)], [[0.5] * 4 for _ in range(3)]]
                for i in range(lag, len(tr_p)):
                    eo, ea, eno = tr_p[i]
                    if eo == o:
                        base_c[ea][eno] += 1.0
                        pk = (tr_p[i - lag][0], tr_p[i - lag][1])
                        if pk in mapping:
                            spl_c[mapping[pk]][ea][eno] += 1.0

                bl = sl = 0.0
                nv = 0
                for i in range(lag, len(va_p)):
                    eo, ea, eno = va_p[i]
                    if eo == o:
                        pk = (va_p[i - lag][0], va_p[i - lag][1])
                        if pk in mapping:
                            cid = mapping[pk]
                            bt = sum(base_c[ea])
                            st = sum(spl_c[cid][ea])
                            bl += multichannel_brier_nbits([x / bt for x in base_c[ea]], eno, 2)
                            sl += multichannel_brier_nbits([x / st for x in spl_c[cid][ea]], eno, 2)
                            base_c[ea][eno] += 1.0
                            spl_c[cid][ea][eno] += 1.0
                            nv += 1

                gain = bl - sl
                hurdle = max(0.42 + 0.12 * (lag - 1), 0.004 * nv)
                if nv >= 15 and gain > hurdle:
                    if best_for_o is None or gain > best_for_o[0]:
                        best_for_o = (gain, lag, mapping, spl_c)

            if best_for_o is not None:
                _, lag, mapping, spl_c = best_for_o
                self.lag_splits[o] = (lag, mapping)
                self.lag_counts[(o, 0)] = spl_c[0]
                self.lag_counts[(o, 1)] = spl_c[1]

        return {
            "lag_splits": len(self.lag_splits),
            "latch_fired": 1 if self.latch_action is not None else 0,
            "latch_action": self.latch_action,
        }

    def score(self, trace: list[dict]) -> float:
        parsed = [parse_public_event(e, 4, 3) for e in trace]
        losses = []
        lv: int | None = None
        for i, (o, a, no) in enumerate(parsed):
            p = self._base_probs(o, a)
            if self.latch_action is not None and self.latch_counts is not None and lv is not None:
                lc = self.latch_counts[lv][o][a]
                lt = sum(lc)
                w = max(0.0, (lt - 2.0) / (lt + 3.0))
                p = [w * (x / lt) + (1.0 - w) * b for x, b in zip(lc, p)]
            if o in self.lag_splits:
                lag, mapping = self.lag_splits[o]
                if i >= lag:
                    pk = (parsed[i - lag][0], parsed[i - lag][1])
                    cid = mapping.get(pk)
                    if cid is not None:
                        c = self.lag_counts[(o, cid)][a]
                        tot = sum(c)
                        if tot > 2.5:
                            w = (tot - 2.0) / (tot + 2.0)
                            sp = [x / tot for x in c]
                            p = [w * s + (1.0 - w) * b for s, b in zip(sp, p)]
            losses.append(multichannel_brier_nbits(p, no, 2))
            if self.latch_action is not None and a == self.latch_action:
                lv = no
        return _mean(losses)
