"""
SCDR-Grid5 Epistemic Observer (y2-scdr04-wscm-grid5):
Read-only, source-free compatibility observer bridging SCDR's Sub-Stochastic Sinkhorn
Soft-Exclusion directly onto `yggdrasil.native_grid5_evidence.NativeGrid5Evidence`
and `WSCM-EPISTEMIC-GUARD-01/guard.py`.

Safety invariants:
- Strictly non-mutating: never alters `evidence.checkpoint()` or `evidence.public_plan(...)`.
- Always delegates to WSCM `unfamiliar_family_readout(...)` first so NativeGrid5Evidence
  validators are never bypassed and `action_admissible` remains `False` when unauthenticated.
- Adds per-action Sub-Stochastic Sinkhorn soft-exclusion over the 5 canonical Grid5
  displacements {(0,0), (1,0), (-1,0), (0,1), (0,-1)} + an un-competed NOVEL column,
  so a single contradicting action (which collapses global 120-permutation role forecasting
  to CONTRADICTION) is isolated cleanly without erasing the other 4 consistent actions.
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

SCHEMA = "yggdrasil.scdr04.wscm-grid5-observer.dev.v1"
GRID5_DELTAS = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))
GRID5_ROLE_NAMES = ("STAY", "PLUS_X", "MINUS_X", "PLUS_Y", "MINUS_Y", "NOVEL_OR_CONTRADICTED")

_GUARD_PATH = Path(__file__).resolve().parents[2] / "chatgpt" / "WSCM-EPISTEMIC-GUARD-01" / "guard.py"
_SPEC = spec_from_file_location("wscm_epistemic_guard01_ref", _GUARD_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_WSCM_GUARD = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_WSCM_GUARD)


def sinkhorn_sub_stochastic(raw_rows: list[list[float]], n_actions: int = 5, iters: int = 3) -> list[list[float]]:
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


def _expected_grid5_after(before: tuple[int, int], delta: tuple[int, int], size: int = 5) -> tuple[int, int]:
    nx = max(0, min(size - 1, before[0] + delta[0]))
    ny = max(0, min(size - 1, before[1] + delta[1]))
    return (nx, ny)


class SCDRGrid5Observer:
    """
    Read-only Sub-Stochastic Sinkhorn diagnostic observer over public Grid5 transitions
    paired with WSCM's fail-closed `unfamiliar_family_readout`.
    """

    def __init__(self, *, grid_size: int = 5, match_lik: float = 0.92, mismatch_lik: float = 0.02, novel_lik: float = 0.20):
        self.grid_size = grid_size
        self.match_lik = match_lik
        self.mismatch_lik = mismatch_lik
        self.novel_lik = novel_lik
        init = [0.18, 0.18, 0.18, 0.18, 0.18, 0.10]
        self.beliefs: list[list[float]] = [list(init) for _ in range(5)]

    def observe_transition(self, before: tuple[int, int], action: int, after: tuple[int, int]) -> None:
        if type(action) is not int or not (0 <= action < 5):
            raise ValueError("SCDR_GRID5_INVALID_ACTION")
        liks = []
        for delta in GRID5_DELTAS:
            exp = _expected_grid5_after(before, delta, size=self.grid_size)
            liks.append(self.match_lik if exp == after else self.mismatch_lik)
        liks.append(self.novel_lik)
        post = [self.beliefs[action][i] * liks[i] for i in range(6)]
        s = sum(post)
        self.beliefs[action] = [x / s for x in post]

    def effective_beliefs(self) -> list[list[float]]:
        return sinkhorn_sub_stochastic(self.beliefs, n_actions=5, iters=3)

    def guarded_diagnostic_readout(self, evidence, state, action, *, episode_id) -> dict:
        """
        Delegates to WSCM's `unfamiliar_family_readout` first (enforcing all native validators
        and `action_admissible=False`), then attaches read-only Sinkhorn per-action diagnostics.
        """
        base_guard = _WSCM_GUARD.unfamiliar_family_readout(evidence, state, action, episode_id=episode_id)
        eff = self.effective_beliefs()[action]
        best_idx = max(range(6), key=lambda i: eff[i])
        return {
            **base_guard,
            "observer_schema": SCHEMA,
            "scdr_action_role_map": GRID5_ROLE_NAMES[best_idx],
            "scdr_action_role_confidence": round(eff[best_idx], 6),
            "scdr_action_novel_abstain": round(eff[5], 6),
            "scdr_per_action_distribution": [round(x, 6) for x in eff],
            # Safety invariant explicitly preserved: observer never grants action authority!
            "action_admissible": False,
            "actionable_next_state": None,
            "family_authenticated": False,
        }
