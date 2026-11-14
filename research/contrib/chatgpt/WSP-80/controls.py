"""WSP80 frozen source-blind paid-row controls and conventional neural baseline.

Only public charged state/action/after ledgers enter here. No evaluator,
private source, test truth, numerical writer, or remote model is imported.
The conventional end-to-end Adam implementation is reused without changing
WSP77's frozen source or its optimizer. 384-action WSP80 fit is separate.
"""
from __future__ import annotations

from hashlib import sha256
import importlib.util
from pathlib import Path

from independent_symbolic import _ACTIONS, _LOW, _HIGH, _STATES, _solve


def paid_rows(experiences, allowed_lengths=(384,)):
    ledger = tuple(experiences)
    if len(ledger) not in allowed_lengths:
        raise ValueError("incomplete WSP80 physical ledger")
    expected = (0,) * 6
    rows = []
    for event in ledger:
        try:
            before, action, after, cost = (
                event.before, event.action, event.after, event.action_cost)
        except AttributeError as exc:
            raise ValueError("missing physical charge receipt") from exc
        if (type(before) is not tuple or before not in _STATES
                or type(after) is not tuple or after not in _STATES
                or type(action) is not int or action not in _ACTIONS
                or type(cost) is not int or cost != 1 or before != expected):
            raise ValueError("invalid/unpaid/noncontinuous charged observation")
        rows.append((before, action, after))
        expected = after
    return tuple(rows)


class SparsePublicControl:
    """Independent symbolic fixed-degree3, always-degree4, or sham-novelty control."""

    def __init__(self, ledger, mode="fixed_degree3", stage_a_only=False):
        if mode not in ("fixed_degree3", "always_degree4", "sham_novelty"):
            raise ValueError("unknown preregistered control")
        charged = paid_rows(ledger)
        self.training_actions = 144 if stage_a_only else 384
        self.mode = mode
        groups = [dict() for _ in _ACTIONS]
        for before, action, after in charged[:self.training_actions]:
            if before in groups[action] and groups[action][before] != after:
                raise ValueError("conflicting paid world transition")
            groups[action][before] = after
        self.terms, self.survivors, self.flagged_actions = [], [], []
        for action, group in enumerate(groups):
            rows = tuple(sorted(group.items()))
            low = _solve(rows, _LOW)
            bad = any(not options for options in low)
            if bad and mode == "sham_novelty":
                self.flagged_actions.append(action)
            terms = _HIGH if mode == "always_degree4" else _LOW
            self.terms.append(terms)
            self.survivors.append(_solve(rows, terms) if mode == "always_degree4" else low)

    def predict(self, state, action, force=False):
        if (type(state) is not tuple or state not in _STATES
                or type(action) is not int or action not in _ACTIONS
                or type(force) is not bool):
            raise ValueError("invalid public prediction query")
        terms = self.terms[action]
        feature = sum(1 << j for j, term in enumerate(terms)
                      if all(state[k] for k in term))
        predictions = []
        for bit, options in enumerate(self.survivors[action]):
            if not options:
                if not force:
                    return None
                predictions.append(state[bit])
                continue
            votes = {((guess & feature).bit_count() & 1) for guess in options}
            if len(votes) != 1 and not force:
                return None
            parity = (options[0] & feature).bit_count() & 1
            predictions.append(state[bit] ^ parity)
        return tuple(predictions)


class PaidMemorization:
    """Exact charged-pair lookup only; no physics queries or free generalization."""

    def __init__(self, ledger):
        rows = paid_rows(ledger)
        self.by_pair = {}
        for before, action, after in rows:
            key = (before, action)
            if key in self.by_pair and self.by_pair[key] != after:
                raise ValueError("contradictory deterministic paid rows")
            self.by_pair[key] = after

    def predict(self, state, action):
        if type(state) is not tuple or state not in _STATES or type(action) is not int or action not in _ACTIONS:
            raise ValueError("invalid public query")
        return self.by_pair.get((state, action))


def _load_frozen_adam():
    path = Path(__file__).resolve().parents[1] / "WSP-77" / "fully_trained_mlp6.py"
    spec = importlib.util.spec_from_file_location("wsp77_frozen_adam_for_wsp80", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("missing inherited conventional Adam control")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if (module.INPUTS, module.HIDDEN, module.OUTPUTS, module.RESTARTS,
            module.MAX_STEPS) != (12, 32, 6, 3, 6000):
        raise RuntimeError("inherited conventional MLP contract drift")
    return module


_OLD = _load_frozen_adam()


class ConventionalAdam384(_OLD.EndToEndAdamControl):
    """Fully train all 12->32 ReLU->6 sigmoid weights on 384 paid samples.

    Three independently seeded deterministic Adam restarts and up to 6000
    gradient updates per restart. Training can be expensive; all updates,
    convergence and CPU cost must be accounted for in scientific scoring.
    """

    def __init__(self, seed):
        super().__init__(seed)

    def fit(self, experiences):
        rows = paid_rows(experiences)
        if self.winner is not None or self.training_trials:
            raise ValueError("conventional baseline already fit")
        contenders = []
        for restart in range(_OLD.RESTARTS):
            fixed_seed = int.from_bytes(sha256(
                f"WSP80|Adam-384|{self.seed}|{restart}".encode("ascii")
            ).digest(), "big")
            net, train_exact, steps = self._train(fixed_seed, rows)
            if not 0 <= train_exact <= 1 or not 1 <= steps <= _OLD.MAX_STEPS:
                raise ArithmeticError("invalid conventional optimizer receipt")
            self.training_trials.append({
                "restart": restart,
                "train_exact": train_exact,
                "gradient_updates": steps,
                "converged": train_exact >= 0.95,
            })
            contenders.append((train_exact, -steps, -restart, net))
        best = max(contenders, key=lambda x: x[:3])
        self.winner = best[3]
        self.fully_trained = best[0] >= 0.95
        return {
            "architecture": "12->32 ReLU->6 sigmoid; full backpropagation/Adam",
            "paid_actions": 384,
            "restarts": _OLD.RESTARTS,
            "max_updates_per_restart": _OLD.MAX_STEPS,
            "fully_trained": self.fully_trained,
            "best_train_exact": best[0],
            "gradient_updates_total": sum(x["gradient_updates"] for x in self.training_trials),
            "trials": tuple(self.training_trials),
        }
