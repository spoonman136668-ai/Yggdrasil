"""WSP-200 source-free reference implementation, NOT licensed GFP training.

Synthetic/development use only. This deliberately accepts a caller-supplied stream
of abstract interaction targets; it does not fetch or parse the original dataset.
The frozen WSP-200 preregistration, not this module, governs scientific evaluation.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import random
from statistics import fmean
from typing import Iterable

VERSION = "wsp200.source-free.v1"
LAMBDA = 10.0
PAIR_SALT = "WSP200-GFP-PAIR-v1"
STREAM_SALT = "WSP200-FIT-STREAM-v1"
INIT_SALT = "WSP200-INIT-v1"
RANDOM_SALT = "WSP200-RANDOM-v1"
MODES = frozenset({"contradiction", "full_refit", "always", "surprise", "random", "no_update", "shuffled_negative"})


def _digest_int(*fields: object) -> int:
    data = "\0".join(map(str, fields)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(data).digest()[:8], "big")


def pair_group(gene: str, pos_a: int, pos_b: int) -> str:
    if not gene or not all(isinstance(p, int) and p >= 0 for p in (pos_a, pos_b)) or pos_a == pos_b:
        raise ValueError("invalid source-free site-pair identity")
    a, b = sorted((pos_a, pos_b))
    return f"{gene}\0{a}\0{b}"


def group_bucket(group: str) -> str:
    v = _digest_int(PAIR_SALT, *group.split("\0")) % 100
    return "FIT" if v < 65 else "VALID" if v < 80 else "PUBLIC_DEV" if v < 90 else "RESERVED_UNTOUCHED"


def fit_stage(group: str) -> int:
    if group_bucket(group) != "FIT":
        raise ValueError("non-FIT group is not training evidence")
    return _digest_int(STREAM_SALT, *group.split("\0")) % 4


def _address_parts(address: str) -> tuple[str, str, str, str]:
    parts = address.split("\0")
    if len(parts) != 4 or not parts[0] or not parts[1].isdigit() or not parts[2] or not parts[3] or parts[2] == parts[3]:
        raise ValueError("invalid mutation address")
    return (parts[0], parts[1], parts[2], parts[3])


@dataclass(frozen=True)
class Sample:
    sample_id: str
    group: str
    left: str
    right: str
    target: float

    def validate(self, stage: int) -> None:
        if not self.sample_id or not math.isfinite(self.target):
            raise ValueError("nonfinite or unidentified observation")
        a = _address_parts(self.left)
        b = _address_parts(self.right)
        parts = self.group.split("\0")
        if len(parts) != 3 or not parts[1].isdigit() or not parts[2].isdigit() or int(parts[1]) >= int(parts[2]):
            raise ValueError("invalid canonical pair group")
        if a[0] != parts[0] or b[0] != parts[0] or sorted((int(a[1]), int(b[1]))) != [int(parts[1]), int(parts[2])]:
            raise ValueError("address/group disagreement")
        if group_bucket(self.group) != "FIT" or fit_stage(self.group) != stage:
            raise ValueError("held or future-stage evidence forbidden")


def _initial(address: str, rank: int) -> list[float]:
    return [0.01 if hashlib.sha256(f"{INIT_SALT}\0{address}\0{k}".encode()).digest()[-1] & 1 else -0.01
            for k in range(rank)]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x*y for x, y in zip(a, b))


def _solve_cholesky(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    """Small deterministic symmetric positive-definite solve, no optimizer gradients."""
    n = len(rhs)
    for attempt in (0.0, 1e-9):
        lower = [[0.0] * n for _ in range(n)]
        try:
            for i in range(n):
                for j in range(i + 1):
                    residue = matrix[i][j] - sum(lower[i][k] * lower[j][k] for k in range(j))
                    if i == j:
                        val = residue + attempt
                        if val <= 0 or not math.isfinite(val):
                            raise ArithmeticError("non-positive normal matrix")
                        lower[i][j] = math.sqrt(val)
                    else:
                        lower[i][j] = residue / lower[j][j]
            y = [0.0] * n
            for i in range(n):
                y[i] = (rhs[i] - sum(lower[i][j]*y[j] for j in range(i))) / lower[i][i]
            x = [0.0] * n
            for i in range(n-1, -1, -1):
                x[i] = (y[i] - sum(lower[j][i]*x[j] for j in range(i+1, n))) / lower[i][i]
            if not all(map(math.isfinite, x)):
                raise ArithmeticError("nonfinite solution")
            return x
        except (ArithmeticError, ZeroDivisionError, OverflowError):
            if attempt:
                raise ArithmeticError("normal equations unsolvable with fixed jitter")
    raise AssertionError("unreachable")


class Learner:
    """Cumulative per-background factor memory with deterministic source-free controls."""

    def __init__(self, source_digest: str, mode: str = "contradiction", rank: int = 4):
        if mode not in MODES or (rank not in (4, 8) if mode == "full_refit" else rank != 4):
            raise ValueError("unsupported frozen mode/rank")
        if len(source_digest) != 64 or any(c not in "0123456789abcdef" for c in source_digest):
            raise ValueError("source digest must be lowercase SHA256")
        self.source_digest = source_digest
        self.mode = mode
        self.rank = rank
        self.stage = -1
        self.mean: float | None = None
        self.sd: float | None = None
        self.weights: dict[str, list[float]] = {}
        self.samples: list[Sample] = []
        self.receipts: set[str] = set()
        self.solves = 0
        self.changed_by_stage: list[list[str]] = []
        self.convergence: list[dict[str, object]] = []

    def predict(self, left: str, right: str) -> float:
        return _dot(self.weights[left] if left in self.weights else _initial(left, self.rank),
                    self.weights[right] if right in self.weights else _initial(right, self.rank))

    def _objective(self) -> float:
        assert self.mean is not None and self.sd is not None
        error = sum((self.predict(s.left, s.right) - (s.target-self.mean)/self.sd)**2 for s in self.samples)
        penalty = LAMBDA * sum(_dot(w, w) for w in self.weights.values())
        return error + penalty

    def _sweep(self, active: set[str]) -> None:
        assert self.mean is not None and self.sd is not None
        # Build a transient adjacency view for this sweep.  Preserve the
        # original observation ordering exactly, so every floating reduction
        # and checkpoint is bitwise equivalent to the naive full scan.
        by_address: dict[str, list[Sample]] = {address: [] for address in active}
        for obs in self.samples:
            if obs.left in by_address:
                by_address[obs.left].append(obs)
            if obs.right in by_address and obs.right != obs.left:
                by_address[obs.right].append(obs)
        for addr in sorted(active):
            mat = [[0.0]*self.rank for _ in range(self.rank)]
            rhs = [0.0]*self.rank
            for i in range(self.rank):
                mat[i][i] = LAMBDA
            for obs in by_address[addr]:
                other = obs.right if addr == obs.left else obs.left
                features = self.weights[other]
                target = (obs.target-self.mean)/self.sd
                for i in range(self.rank):
                    rhs[i] += target*features[i]
                    for j in range(self.rank):
                        mat[i][j] += features[i]*features[j]
            self.weights[addr] = _solve_cholesky(mat, rhs)
            self.solves += 1

    def _choose(self, new: list[Sample], stage: int,
                reference_write_count: int | None) -> set[str]:
        if self.mode == "no_update":
            return set()
        if self.mode in ("full_refit", "shuffled_negative"):
            return set(self.weights)
        addresses = {s.left for s in new} | {s.right for s in new}
        if self.mode == "always":
            return addresses
        by_addr: dict[str, list[tuple[str, float]]] = {a: [] for a in addresses}
        for obs in new:
            residual = (obs.target-self.mean)/self.sd-self.predict(obs.left, obs.right)
            for a in (obs.left, obs.right):
                by_addr[a].append((obs.sample_id, residual))
        eligible = []
        contradicted = []
        for addr, evidence in by_addr.items():
            if len({e[0] for e in evidence}) < 2:
                continue
            errs = [v for _,v in evidence]
            nz = [v for v in errs if v != 0]
            avg = fmean(errs)
            entry = (addr, avg, fmean(map(abs, errs)))
            eligible.append(entry)
            if nz and max(sum(v > 0 for v in nz), sum(v < 0 for v in nz))/len(nz) >= 0.75 and abs(avg) >= 1:
                contradicted.append(entry)
        # The same qualifying-address pool and write count is shared by the gated arms.
        budget = (len(addresses) + 3)//4
        selected_count = min(budget, len(contradicted))
        if self.mode in ("surprise", "random"):
            if reference_write_count is None or not isinstance(reference_write_count, int):
                raise ValueError("gated control requires candidate write count")
            if reference_write_count < 0 or reference_write_count > min(budget, len(eligible)):
                raise ValueError("gated control cannot match candidate write count")
            selected_count = reference_write_count
        if self.mode == "contradiction":
            ordered = sorted(contradicted, key=lambda e: (-abs(e[1]), e[0].encode("utf-8")))
        elif self.mode == "surprise":
            ordered = sorted(eligible, key=lambda e: (-e[2], e[0].encode("utf-8")))
        else:
            ordered = sorted(eligible, key=lambda e: (hashlib.sha256(f"{RANDOM_SALT}\0{stage}\0{e[0]}".encode()).digest(), e[0].encode("utf-8")))
        return {a for a,_,_ in ordered[:selected_count]}

    def advance(self, stage: int, batch: Iterable[Sample],
                *, reference_write_count: int | None = None) -> dict[str, object]:
        # Transactional: failures (including comparator nonconvergence) cannot
        # partially consume evidence or damage a recoverable checkpoint.
        proposed = self.restore(self.checkpoint(), self.source_digest)
        receipt = proposed._advance_uncommitted(stage, batch, reference_write_count)
        self.__dict__.update(proposed.__dict__)
        return receipt

    def _advance_uncommitted(self, stage: int, batch: Iterable[Sample],
                             reference_write_count: int | None) -> dict[str, object]:
        if stage != self.stage + 1 or stage not in range(4):
            raise ValueError("stage order or replay invalid")
        new = sorted(list(batch), key=lambda sample: sample.sample_id)
        if reference_write_count is not None and (stage == 0 or self.mode not in ("surprise", "random")):
            raise ValueError("reference write count only allowed on gated controls after B0")
        if not new:
            raise ValueError("empty stage")
        ids = [s.sample_id for s in new]
        if len(ids) != len(set(ids)) or set(ids) & self.receipts:
            raise ValueError("duplicate observation receipt")
        identities = [(s.group, s.left, s.right) for s in new]
        existing = {(s.group, s.left, s.right) for s in self.samples}
        if len(identities) != len(set(identities)) or set(identities) & existing:
            raise ValueError("duplicate genotype identity")
        for s in new:
            s.validate(stage)
        groups_new = {s.group for s in new}
        if len({s.group.split("\0")[0] for s in new + self.samples}) != 1:
            raise ValueError("cross-background pooling forbidden")
        if groups_new & {s.group for s in self.samples}:
            raise ValueError("site-pair group replay across stages")
        if self.mode == "shuffled_negative":
            seed = int.from_bytes(hashlib.sha256(
                f"WSP200-SHUFFLE-v1\0{20031}\0{stage}\0{new[0].group.split(chr(0))[0]}".encode()
            ).digest()[:8], "big")
            values = [s.target for s in new]
            random.Random(seed).shuffle(values)
            new = [Sample(s.sample_id, s.group, s.left, s.right, y)
                   for s, y in zip(new, values)]
        if stage == 0:
            self.mean = fmean(s.target for s in new)
            self.sd = math.sqrt(fmean((s.target-self.mean)**2 for s in new))
            if self.sd <= 1e-12 or not math.isfinite(self.sd):
                raise ValueError("B0 normalization invalid")
        for s in new:
            for a in (s.left, s.right):
                if a not in self.weights:
                    self.weights[a] = _initial(a, self.rank)
        # Gate on new observations *before* cumulative exposure or any factor writes.
        active = self._choose(new, stage, reference_write_count) if stage else set(self.weights)
        self.samples.extend(new)
        if stage == 0 and self.mode not in ("full_refit", "shuffled_negative"):
            for _ in range(16):
                self._sweep(active)
            self.convergence.append({"stage":stage, "converged":None, "sweeps":16})
        elif self.mode in ("full_refit", "shuffled_negative"):
            prev = self._objective()
            streak = 0
            for step in range(1, 101):
                self._sweep(active)
                curr = self._objective()
                reduction = (prev-curr) / max(abs(prev), 1e-12)
                if reduction < -1e-9:
                    raise ArithmeticError("refit objective increased")
                streak = streak+1 if 0 <= reduction <= 1e-6 else 0
                prev = curr
                if streak == 3:
                    break
            if streak != 3:
                raise ArithmeticError("full refit control not converged within 100 sweeps")
            self.convergence.append({"stage":stage, "converged":True, "sweeps":step})
        else:
            for _ in range(2):
                self._sweep(active)
            self.convergence.append({"stage":stage, "converged":None, "sweeps":2})
        self.receipts.update(ids)
        self.stage = stage
        self.changed_by_stage.append(sorted(active))
        return {"stage":stage, "new_observations":len(new), "address_writes":len(active), "solves":self.solves}

    def checkpoint(self) -> bytes:
        state = {"schema":VERSION, "source_digest":self.source_digest, "mode":self.mode, "rank":self.rank,
                 "stage":self.stage, "mean":self.mean, "sd":self.sd,
                 "weights":self.weights, "samples":[vars(s) for s in self.samples],
                 "receipts":sorted(self.receipts), "solves":self.solves,
                 "changed_by_stage":self.changed_by_stage, "convergence":self.convergence}
        raw = json.dumps(state, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        state["state_sha256"] = hashlib.sha256(raw).hexdigest()
        return json.dumps(state, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

    @classmethod
    def restore(cls, data: bytes, expected_source_digest: str) -> Learner:
        obj = json.loads(data)
        if obj.get("schema") != VERSION or obj.get("source_digest") != expected_source_digest:
            raise ValueError("checkpoint version or source digest changed")
        checksum = obj.pop("state_sha256", None)
        raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        if checksum != hashlib.sha256(raw).hexdigest():
            raise ValueError("checkpoint state hash mismatch")
        learned = cls(obj["source_digest"], obj["mode"], obj["rank"])
        learned.stage = obj["stage"]
        learned.mean, learned.sd = obj["mean"], obj["sd"]
        learned.weights = obj["weights"]
        learned.samples = [Sample(**s) for s in obj["samples"]]
        learned.receipts = set(obj["receipts"])
        learned.solves = obj["solves"]
        learned.changed_by_stage = obj["changed_by_stage"]
        learned.convergence = obj["convergence"]
        if learned.checkpoint() != data or len(learned.receipts) != len(learned.samples):
            raise ValueError("noncanonical or corrupted checkpoint")
        return learned
