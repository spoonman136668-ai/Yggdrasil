"""
SCDR-RoleCell (v4): Unconventional, stdlib-only causal contract learner for Yggdrasil Y2-CCE06.

Strictly public-only interface: observes ONLY {'observation': [b0, b1], 'action': a, 'next_observation': [nb0, nb1]}.
Never accesses hidden state, world family names, oracle diagnostics, or locked CAL seeds.

Core mechanisms:
1. Calibrated H1 Sheaf-Cycle Defect Splitting (out-of-sample prequential hurdle).
2. Immutable Anchor-to-Genesis Quine Ledger (prevents multi-absorb cumulative forgetting).
3. Gauge-Deduplicated Sheet Compression (reuses existing sheets via action-permutation pointers).
4. Bayesian Epistemic Abstention Guard (competing FreshOnlineContract for out-of-family worlds).
5. Charged-Probe EVGI On-Policy Exploration (decay=1.0 + unified OOD Dirichlet fallback probing).
"""

from __future__ import annotations

import itertools
import math
from typing import Iterable

ACTIONS = (0, 1, 2)
COST = (0, 1, 1)


def obs_code(obs) -> int:
    if len(obs) != 2 or obs[0] not in (0, 1) or obs[1] not in (0, 1):
        raise ValueError("SCDR_INVALID_OBSERVATION")
    return (int(obs[0]) << 1) | int(obs[1])


def validate_public_event(ev: dict) -> tuple[int, int, int]:
    if not isinstance(ev, dict) or set(ev.keys()) != {"observation", "action", "next_observation"}:
        raise ValueError("SCDR_NON_PUBLIC_EVENT_SCHEMA")
    o = obs_code(ev["observation"])
    a = ev["action"]
    if type(a) is not int or a not in ACTIONS:
        raise ValueError("SCDR_INVALID_ACTION")
    no = obs_code(ev["next_observation"])
    return o, a, no


def multichannel_brier(probs: list[float], target: int) -> float:
    tot = sum(probs)
    if tot <= 0.0:
        raise ValueError("SCDR_INVALID_PROBS")
    norm = [x / tot for x in probs]
    p0 = norm[2] + norm[3]
    p1 = norm[1] + norm[3]
    return 0.5 * ((p0 - (target // 2)) ** 2 + (p1 - (target % 2)) ** 2)


def channel_l2(p: list[float], q: list[float]) -> float:
    p0, p1 = p[2] + p[3], p[1] + p[3]
    q0, q1 = q[2] + q[3], q[1] + q[3]
    return 0.5 * ((p0 - q0) ** 2 + (p1 - q1) ** 2)


def _mean(vals: Iterable[float]) -> float:
    lst = list(vals)
    return sum(lst) / len(lst) if lst else 0.0


def _l1(p: list[float], q: list[float]) -> float:
    return sum(abs(a - b) for a, b in zip(p, q))


class GenesisContractSheet:
    """Single causal contract sheet with H1 Sheaf Splitting and an immutable Genesis Quine Ledger."""

    def __init__(self, max_splits: int = 4, split_hurdle_min: float = 0.40, split_hurdle_rate: float = 0.004):
        self.max_splits = max_splits
        self.split_hurdle_min = split_hurdle_min
        self.split_hurdle_rate = split_hurdle_rate
        self.base_counts = [[[0.5] * 4 for _ in range(3)] for _ in range(4)]
        self.splits: dict[int, dict[tuple[int, int], int]] = {}
        self.split_counts: dict[tuple[int, int], list[list[float]]] = {}
        self.quine_ledger: list[list[tuple[tuple[int, int] | None, int, int, list[float]]]] = []
        self.frozen = False

    def _base_probs(self, o: int, a: int) -> list[float]:
        c = self.base_counts[o][a]
        tot = sum(c)
        return [x / tot for x in c]

    def predict(self, prev_ctx: tuple[int, int] | None, o: int, a: int, perm: tuple[int, int, int] = (0, 1, 2)) -> list[float]:
        ca = perm[a]
        if o in self.splits and prev_ctx is not None:
            mapped_prev = (prev_ctx[0], perm[prev_ctx[1]])
            cid = self.splits[o].get(mapped_prev)
            if cid is not None:
                c = self.split_counts[(o, cid)][ca]
                tot = sum(c)
                if tot > 2.5:
                    w = (tot - 2.0) / (tot + 2.0)
                    bp = self._base_probs(o, ca)
                    sp = [x / tot for x in c]
                    return [w * s + (1.0 - w) * b for s, b in zip(sp, bp)]
        return self._base_probs(o, ca)

    def fit_batch(self, trace: list[dict]) -> None:
        if self.frozen:
            return
        parsed = [validate_public_event(ev) for ev in trace]
        for o, a, no in parsed:
            self.base_counts[o][a][no] += 1.0
        self._discover_sheaf_splits(parsed)

    def _discover_sheaf_splits(self, parsed: list[tuple[int, int, int]]) -> None:
        split_idx = int(len(parsed) * 0.6)
        train_part = parsed[:split_idx]
        val_part = parsed[split_idx:]
        local_pred: list[dict[tuple[int, int], list[list[float]]]] = [{} for _ in range(4)]
        local_base = [[[0.5] * 4 for _ in range(3)] for _ in range(4)]
        pctx = None
        for o, a, no in train_part:
            local_base[o][a][no] += 1.0
            if pctx is not None:
                tbl = local_pred[o].setdefault(pctx, [[0.0] * 4 for _ in range(3)])
                tbl[a][no] += 1.0
            pctx = (o, a)

        candidates = []
        for o in range(4):
            preds, vecs = [], []
            for pctx_k, tbl in local_pred[o].items():
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
                preds.append(pctx_k)
                vecs.append(vec)
            if len(preds) < 2:
                continue

            best_pair, best_d = (0, 1), -1.0
            for i in range(len(vecs)):
                for j in range(i + 1, len(vecs)):
                    d = _l1(vecs[i], vecs[j])
                    if d > best_d:
                        best_d, best_pair = d, (i, j)
            c0, c1 = list(vecs[best_pair[0]]), list(vecs[best_pair[1]])
            assign = [0] * len(preds)
            for _ in range(8):
                new_assign = [0 if _l1(v, c0) <= _l1(v, c1) else 1 for v in vecs]
                if new_assign == assign:
                    break
                assign = new_assign
                for cid in (0, 1):
                    members = [vecs[k] for k, c in enumerate(assign) if c == cid]
                    if members:
                        avg = [sum(m[d] for m in members) / len(members) for d in range(len(c0))]
                        if cid == 0:
                            c0 = avg
                        else:
                            c1 = avg
            if len(set(assign)) < 2:
                continue
            mapping = {preds[k]: assign[k] for k in range(len(preds))}

            base_c = [[0.5] * 4 for _ in range(3)]
            spl_c = [[[0.5] * 4 for _ in range(3)], [[0.5] * 4 for _ in range(3)]]
            pctx = None
            for eo, ea, eno in train_part:
                if eo == o:
                    base_c[ea][eno] += 1.0
                    if pctx in mapping:
                        spl_c[mapping[pctx]][ea][eno] += 1.0
                pctx = (eo, ea)

            base_loss = spl_loss = 0.0
            n_val = 0
            pctx = None
            for eo, ea, eno in val_part:
                if eo == o and pctx in mapping:
                    cid = mapping[pctx]
                    bt = sum(base_c[ea])
                    st = sum(spl_c[cid][ea])
                    base_loss += multichannel_brier([x / bt for x in base_c[ea]], eno)
                    spl_loss += multichannel_brier([x / st for x in spl_c[cid][ea]], eno)
                    base_c[ea][eno] += 1.0
                    spl_c[cid][ea][eno] += 1.0
                    n_val += 1
                pctx = (eo, ea)

            gain = base_loss - spl_loss
            hurdle = max(self.split_hurdle_min, self.split_hurdle_rate * n_val)
            if n_val >= 15 and gain > hurdle:
                candidates.append((gain, o, mapping, spl_c))

        candidates.sort(reverse=True, key=lambda x: x[0])
        for _, o, mapping, spl_c in candidates[: self.max_splits]:
            self.splits[o] = mapping
            self.split_counts[(o, 0)] = spl_c[0]
            self.split_counts[(o, 1)] = spl_c[1]

    def commit_quine_to_ledger(self, trace: list[dict], k: int = 8) -> None:
        support: dict[tuple[tuple[int, int] | None, int, int], int] = {}
        pctx = None
        for ev in trace:
            o, a, _ = validate_public_event(ev)
            key = (pctx if o in self.splits else None, o, a)
            support[key] = support.get(key, 0) + 1
            pctx = (o, a)
        scored = []
        for (kpctx, o, a), cnt in support.items():
            if cnt < 10:
                continue
            probs = self.predict(kpctx, o, a)
            scored.append((max(probs) * math.log1p(cnt), kpctx, o, a, probs))
        scored.sort(reverse=True, key=lambda x: x[0])
        quine = [(kpctx, o, a, list(probs)) for _, kpctx, o, a, probs in scored[:k]]
        if quine:
            self.quine_ledger.append(quine)

    def max_ledger_drift(self, reference_ledger: list[list[tuple[tuple[int, int] | None, int, int, list[float]]]]) -> float:
        if not reference_ledger:
            return 0.0
        return max(
            _mean(channel_l2(self.predict(kpctx, o, a), ref_p) for kpctx, o, a, ref_p in q)
            for q in reference_ledger
        )

    def clone(self) -> "GenesisContractSheet":
        c = GenesisContractSheet(self.max_splits, self.split_hurdle_min, self.split_hurdle_rate)
        c.base_counts = [[list(row) for row in mat] for mat in self.base_counts]
        c.splits = {o: dict(m) for o, m in self.splits.items()}
        c.split_counts = {k: [list(row) for row in mat] for k, mat in self.split_counts.items()}
        c.quine_ledger = [[(kp, o, a, list(p)) for kp, o, a, p in q] for q in self.quine_ledger]
        c.frozen = self.frozen
        return c


class FreshOnlineContract:
    """Lightweight online Dirichlet fallback hypothesis for Epistemic Abstention."""

    def __init__(self):
        self.counts = [[[0.5] * 4 for _ in range(3)] for _ in range(4)]

    def predict(self, o: int, a: int) -> list[float]:
        c = self.counts[o][a]
        tot = sum(c)
        return [x / tot for x in c]

    def update(self, o: int, a: int, no: int) -> None:
        self.counts[o][a][no] += 1.0


class SCDRRoleCell:
    """SCDR-RoleCell-v4: H1 Sheaf Splitting + Genesis Quine Ledger + Gauge Compression + Epistemic Guard."""

    def __init__(
        self,
        *,
        use_quine_guard: bool = True,
        use_genesis_ledger: bool = True,
        use_gauge_dedup: bool = True,
        use_gauge: bool = True,
        use_epistemic_guard: bool = True,
        drift_budget: float = 0.02,
        gauge_tol: float = 0.012,
    ):
        self.use_quine_guard = use_quine_guard
        self.use_genesis_ledger = use_genesis_ledger
        self.use_gauge_dedup = use_gauge_dedup
        self.use_gauge = use_gauge
        self.use_epistemic_guard = use_epistemic_guard
        self.drift_budget = drift_budget
        self.gauge_tol = gauge_tol
        self.sheets: list[GenesisContractSheet] = []
        self.gauge_pointers: list[tuple[int, tuple[int, int, int]]] = []

    def _sheet_trace_brier(self, sheet: GenesisContractSheet, trace: list[dict], perm: tuple[int, int, int]) -> float:
        losses, pctx = [], None
        for ev in trace:
            o, a, no = validate_public_event(ev)
            losses.append(multichannel_brier(sheet.predict(pctx, o, a, perm=perm), no))
            pctx = (o, a)
        return _mean(losses)

    def train_regime(self, trace: list[dict]) -> dict:
        if not self.sheets:
            s = GenesisContractSheet()
            s.fit_batch(trace)
            s.commit_quine_to_ledger(trace)
            self.sheets.append(s)
            return {"action": "init", "num_sheets": 1, "num_pointers": 0, "splits": len(s.splits)}

        if not self.use_quine_guard:
            self.sheets[0].frozen = False
            self.sheets[0].fit_batch(trace)
            return {"action": "overwrite", "num_sheets": 1, "num_pointers": 0, "splits": len(self.sheets[0].splits)}

        if self.use_gauge_dedup:
            val_split = int(len(trace) * 0.7)
            tr_head, tr_tail = trace[:val_split], trace[val_split:]
            fresh_cand = GenesisContractSheet()
            fresh_cand.fit_batch(tr_head)
            fresh_brier = self._sheet_trace_brier(fresh_cand, tr_tail, (0, 1, 2))
            best_match, best_brier = None, 1e9
            for si, sheet in enumerate(self.sheets):
                for perm in itertools.permutations(ACTIONS):
                    b = self._sheet_trace_brier(sheet, tr_tail, perm)
                    if b < best_brier:
                        best_brier, best_match = b, (si, perm)
            if best_match is not None and (best_brier - fresh_brier) <= self.gauge_tol:
                if best_match not in self.gauge_pointers:
                    self.gauge_pointers.append(best_match)
                return {
                    "action": "gauge_reuse",
                    "matched_sheet": best_match[0],
                    "matched_perm": list(best_match[1]),
                    "num_sheets": len(self.sheets),
                    "num_pointers": len(self.gauge_pointers),
                }

        ref_sheet = self.sheets[-1]
        trial = ref_sheet.clone()
        trial.frozen = False
        trial.fit_batch(trace)
        ref_ledger = ref_sheet.quine_ledger if self.use_genesis_ledger else ref_sheet.quine_ledger[-1:]
        max_drift = trial.max_ledger_drift(ref_ledger)

        if max_drift > self.drift_budget:
            ref_sheet.frozen = True
            new_sheet = GenesisContractSheet()
            new_sheet.fit_batch(trace)
            new_sheet.commit_quine_to_ledger(trace)
            self.sheets.append(new_sheet)
            return {
                "action": "speciate",
                "max_ledger_drift": round(max_drift, 6),
                "num_sheets": len(self.sheets),
                "num_pointers": len(self.gauge_pointers),
                "splits": len(new_sheet.splits),
            }
        trial.commit_quine_to_ledger(trace)
        self.sheets[-1] = trial
        return {
            "action": "absorb",
            "max_ledger_drift": round(max_drift, 6),
            "num_sheets": len(self.sheets),
            "num_pointers": len(self.gauge_pointers),
            "splits": len(trial.splits),
        }

    def score_stream(self, trace: list[dict], *, allow_gauge: bool = False) -> tuple[float, list[float], float]:
        perms = list(itertools.permutations(ACTIONS)) if (allow_gauge and self.use_gauge) else [(0, 1, 2)]
        hyps = [("sheet", si, p) for si in range(len(self.sheets)) for p in perms]
        fresh = FreshOnlineContract()
        if allow_gauge and self.use_epistemic_guard:
            hyps.append(("fresh", -1, (0, 1, 2)))

        log_w = [0.0] * len(hyps)
        losses, pctx, last_abstain = [], None, 0.0
        for ev in trace:
            o, a, no = validate_public_event(ev)
            m = max(log_w)
            ws = [math.exp(lw - m) for lw in log_w]
            sw = sum(ws)
            ws = [w / sw for w in ws]

            mix = [0.0, 0.0, 0.0, 0.0]
            hyp_preds = []
            for idx, (kind, si, perm) in enumerate(hyps):
                hp = self.sheets[si].predict(pctx, o, a, perm=perm) if kind == "sheet" else fresh.predict(o, a)
                if kind == "fresh":
                    last_abstain = ws[idx]
                hyp_preds.append(hp)
                w = ws[idx]
                for c in range(4):
                    mix[c] += w * hp[c]

            losses.append(multichannel_brier(mix, no))
            for idx, hp in enumerate(hyp_preds):
                log_w[idx] = 0.92 * log_w[idx] + math.log(max(1e-6, hp[no]))
            fresh.update(o, a, no)
            pctx = (o, a)
        return _mean(losses), losses, last_abstain


class ChargedProbeGaugePolicy:
    """Stationary-episode on-policy Charged-Probe Gauge Policy (decay=1.0 + unified OOD probing)."""

    def __init__(self, cell: SCDRRoleCell, *, probe_penalty: float = 0.012):
        self.cell = cell
        self.probe_penalty = probe_penalty
        self.hyps = [
            ("sheet", si, p) for si in range(len(cell.sheets)) for p in itertools.permutations(ACTIONS)
        ] + [("fresh", -1, (0, 1, 2))]
        self.fresh = FreshOnlineContract()
        self.log_w = [0.0] * len(self.hyps)
        self.current: list[int] | None = None
        self.pctx: tuple[int, int] | None = None
        self.budget = 0
        self.spent = 0

    def start(self, observed: list[int], *, paid_budget: int) -> None:
        obs_code(observed)
        if type(paid_budget) is not int or paid_budget < 0:
            raise ValueError("SCDR_INVALID_BUDGET")
        self.current = list(observed)
        self.budget = paid_budget
        self.spent = 0

    def weights(self) -> list[float]:
        m = max(self.log_w)
        ws = [math.exp(lw - m) for lw in self.log_w]
        sw = sum(ws)
        return [w / sw for w in ws]

    def _hyp_pred(self, kind: str, si: int, perm: tuple[int, int, int], pctx, o: int, a: int) -> list[float]:
        return self.cell.sheets[si].predict(pctx, o, a, perm=perm) if kind == "sheet" else self.fresh.predict(o, a)

    def _fresh_brier_gain(self, o: int, a: int) -> float:
        c = self.fresh.counts[o][a]
        s = sum(c)
        p = [x / s for x in c]
        p0, p1 = p[2] + p[3], p[1] + p[3]
        return 0.5 * (p0 * (1.0 - p0) + p1 * (1.0 - p1)) / ((s + 1.0) ** 2) * 4.0

    def choose(self) -> int:
        if self.current is None:
            raise ValueError("SCDR_POLICY_NOT_STARTED")
        o = obs_code(self.current)
        ws = self.weights()
        w_fresh = ws[-1]
        avail = [a for a in ACTIONS if self.spent + COST[a] <= self.budget]
        best_a, best_u = 0, -1e9
        for a in avail:
            preds = [self._hyp_pred(k, si, perm, self.pctx, o, a) for k, si, perm in self.hyps]
            mix = [sum(ws[i] * preds[i][c] for i in range(len(self.hyps))) for c in range(4)]
            m0, m1 = mix[2] + mix[3], mix[1] + mix[3]
            evgi = sum(
                ws[i] * 0.5 * (((p[2] + p[3]) - m0) ** 2 + ((p[1] + p[3]) - m1) ** 2)
                for i, p in enumerate(preds)
            )
            u = evgi + w_fresh * self._fresh_brier_gain(o, a) - self.probe_penalty * COST[a]
            if u > best_u:
                best_u, best_a = u, a
        self.spent += COST[best_a]
        return best_a

    def update(self, ev: dict) -> None:
        o, a, no = validate_public_event(ev)
        for idx, (kind, si, perm) in enumerate(self.hyps):
            hp = self._hyp_pred(kind, si, perm, self.pctx, o, a)
            self.log_w[idx] += math.log(max(1e-6, hp[no]))
        self.fresh.update(o, a, no)
        self.pctx = (o, a)
        self.current = list(ev["next_observation"])

    def score_audit(self, audit_trace: list[dict]) -> float:
        ws = self.weights()
        losses, pctx = [], None
        for ev in audit_trace:
            o, a, no = validate_public_event(ev)
            mix = [0.0, 0.0, 0.0, 0.0]
            for idx, (kind, si, perm) in enumerate(self.hyps):
                hp = self._hyp_pred(kind, si, perm, pctx, o, a)
                w = ws[idx]
                for c in range(4):
                    mix[c] += w * hp[c]
            losses.append(multichannel_brier(mix, no))
            pctx = (o, a)
        return _mean(losses)
