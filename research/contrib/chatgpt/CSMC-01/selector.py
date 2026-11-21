"""CSMC-01: causal-structure-aware FIT-only replay compression experiment.

Independent external research lane. No protected first use, held scoring,
source mutation, native checkpoint promotion or scientific claim.

The first local exploratory result preceded this Git prereg commit; it is
NOT confirmatory preregistered science. Frozen local prereg SHA256:
49c9c00d4b6752d28ff9ce934b6405c9b16b9fdc1bce70375579a57a6dcc4612

Reused verbatim source helpers from tests/test_pcer02_native_fit.py at blob:
4ce67f66b5c96a200d0af2abdef1adaeaf5737ea
"""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

TRACE = (Path(__file__).resolve().parents[3] /
         "research/contrib/chatgpt/CAUSAL-AMALGAM/selection-dev-01/trace.json")
TRACE_PIN = "36f535c451c813dd56afd58c4f1833ac8e5fca98627d898a571e40c8bc8a0114"
COHORT = "amalgam-selection-transition-local-dev-v1"
CAPACITY = 20
EVAL_BUDGET = 2500

def fit():
    raw = TRACE.read_bytes()
    if sha256(raw).hexdigest() != TRACE_PIN:
        raise ValueError("PCER02_SOURCE_DRIFT")
    trace = json.loads(raw)
    if type(trace) is not list or len(trace) != 96:
        raise ValueError("PCER02_TRACE_SHAPE")
    rows = []
    for i, event in enumerate(trace[:50]):
        phase, index = divmod(i, 32)
        ident = digest(canonical([COHORT, (764013, 764029)[phase], index]))
        if event["id"] != ident or event["phase"] != phase:
            raise ValueError("PCER02_IDENTITY")
        views = tuple(tuple(v) for v in event["views"])
        row = event["row"]
        if (len(views) != 2 or any(len(v) != 2 for v in views) or
                any(type(b) is not int or b not in (0, 1)
                    for v in views for b in v) or
                set(row) != {"s1", "x1", "s2", "x2", "y"} or
                any(type(row[k]) is not int or row[k] not in (0, 1)
                    for k in ("s1", "x1", "s2", "x2", "y")) or
                views[0][0] != views[1][0] or row["s1"] != views[0][0]):
            raise ValueError("PCER02_PUBLIC_ROW")
        rows.append((ident, views, row))
    return rows



class Compact:
    """Two-stage conventional counts and prequential losses; no witness ledger."""

    def __init__(self):
        self.t = [[[0, 0] for _ in range(2)] for _ in range(3)]
        self.y = [[[0, 0] for _ in range(2)] for _ in range(14)]
        self.tloss = [Fraction(0), Fraction(0)]
        self.yloss = [Fraction(0), Fraction(0)]
        self.projection = None
        self.mismatch = [0, 0]
        self.n = 0
        self.buffer = []

    @staticmethod
    def p(bank, slot, action):
        fails, wins = bank[slot][action]
        return Fraction(wins + 1, fails + wins + 2)

    @staticmethod
    def selected(loss):
        return 0 if loss[0] < loss[1] else 1

    @staticmethod
    def slots(context, first, state):
        return ((12 + state, 12 + state) if context is None else
                (context + 2 * first + 4 * state, 8 + context + 2 * state))

    def context(self, views):
        if self.projection is None:
            return None
        a, b = (v[self.projection] for v in views)
        return a if a == b else None

    def projected(self, views, first, state, second, reward):
        context = self.context(views)
        if context is not None:
            full, pooled = self.slots(context, first, state)
            self.t[context][first][state] += 1
            self.y[full][second][reward] += 1
            self.y[pooled][second][reward] += 1

    def observe(self, views, row):
        first, state, second, reward = (row[k] for k in ("x1", "s2", "x2", "y"))
        context = self.context(views)
        full, pooled = self.slots(context, first, state)
        for i, slot in enumerate((2 if context is None else context, 2)):
            self.tloss[i] += (self.p(self.t, slot, first) - state) ** 2
        for i, slot in enumerate((full, pooled)):
            self.yloss[i] += (self.p(self.y, slot, second) - reward) ** 2
        self.t[2][first][state] += 1
        self.y[12 + state][second][reward] += 1
        self.projected(views, first, state, second, reward)
        self.n += 1
        if self.n <= 8:
            self.buffer.append((views, first, state, second, reward))
            for pos in (0, 1):
                self.mismatch[pos] += int(views[0][pos] != views[1][pos])
            if self.n == 8 and self.mismatch[0] != self.mismatch[1]:
                self.projection = int(self.mismatch[1] < self.mismatch[0])
                for event in self.buffer:
                    self.projected(*event)
                self.buffer.clear()

    def forecast(self, view, first, state=None, second=None):
        context = None if self.projection is None else view[self.projection]
        if state is None:
            if second is not None:
                raise ValueError("PCER02_STAGE_ONE")
            slots, bank, losses, action = ((2 if context is None else context, 2),
                                          self.t, self.tloss, first)
        else:
            if second is None:
                raise ValueError("PCER02_STAGE_TWO")
            slots, bank, losses, action = (self.slots(context, first, state),
                                          self.y, self.yloss, second)
        return self.p(bank, slots[self.selected(losses)], action)

    def checkpoint(self):
        if self.buffer:
            raise ValueError("PCER02_INCOMPLETE_PROJECTION")
        return canonical({"t": self.t, "y": self.y,
                          "tloss": [[x.numerator, x.denominator] for x in self.tloss],
                          "yloss": [[x.numerator, x.denominator] for x in self.yloss],
                          "projection": self.projection, "mismatch": self.mismatch,
                          "count": self.n})

    @classmethod
    def restore(cls, raw, pin):
        if type(raw) is not bytes or digest(raw) != pin:
            raise ValueError("PCER02_COMPACT_PIN")
        obj = cls()
        d = json.loads(raw)
        if set(d) != {"t", "y", "tloss", "yloss", "projection", "mismatch", "count"}:
            raise ValueError("PCER02_COMPACT_SHAPE")
        obj.t, obj.y = d["t"], d["y"]
        obj.tloss = [Fraction(*pair) for pair in d["tloss"]]
        obj.yloss = [Fraction(*pair) for pair in d["yloss"]]
        obj.projection, obj.mismatch, obj.n = d["projection"], d["mismatch"], d["count"]
        if obj.checkpoint() != raw:
            raise ValueError("PCER02_COMPACT_RESTORE")
        return obj



def terminal_cell(event):
    _, views, r = event
    return views[0][0], r["x1"], r["s2"], r["x2"]


def make_compact(rows, indices):
    result = Compact()
    for i in sorted(indices):
        _, views, row = rows[i]
        result.observe(views, row)
    return result


def propose_compact(model, context, first=None, state=None):
    priorities = []
    for action in (0, 1):
        if first is None:
            bank, slots, loss = model.t, (context if model.projection is not None else 2, 2), model.tloss
        else:
            bank = model.y
            slots = model.slots(context if model.projection is not None else None, first, state)
            loss = model.yloss
        full, pooled = (model.p(bank, slot, action) for slot in slots)
        slot = slots[model.selected(loss)]
        current = model.p(bank, slot, action)
        trials = sum(bank[slot][action])
        priorities.append((abs(full - pooled), -abs(current - Fraction(1, 2)), -trials))
    return int(priorities[1] > priorities[0])


def readout(model):
    stage1 = tuple(model.forecast((c, 0), a) for c in (0, 1) for a in (0, 1))
    stage2 = tuple(model.forecast((c, 0), a, s, x)
                   for c in (0, 1) for a in (0, 1)
                   for s in (0, 1) for x in (0, 1))
    decisions = (tuple(propose_compact(model, c) for c in (0, 1)) +
                 tuple(propose_compact(model, c, a, s) for c in (0, 1)
                       for a in (0, 1) for s in (0, 1)))
    return stage1, stage2, decisions


def objective(reference, model, indices):
    a, b, decisions = reference
    a2, b2, decisions2 = readout(model)
    return (sum(x != y for x, y in zip(decisions, decisions2)),
            max(abs(x - y) for x, y in zip(b, b2)),
            max(abs(x - y) for x, y in zip(a, a2)),
            sum(abs(x - y) for x, y in zip(a + b, a2 + b2)) / 20,
            tuple(sorted(indices)))


def select(rows):
    """Frozen design: 8 projection anchors, 15 mechanism cells, greedy and two swaps."""
    if len(rows) != 50:
        raise ValueError("CSMC01_FIT_COUNT")
    all_cells = {terminal_cell(event) for event in rows}
    if len(all_cells) != 15:
        raise ValueError("CSMC01_TERMINAL_CELL_COUNT")
    full = make_compact(rows, range(50))
    reference = readout(full)
    selected = set(range(8))
    for cell in sorted(all_cells):
        if cell not in {terminal_cell(rows[i]) for i in selected}:
            selected.add(next(i for i, event in enumerate(rows)
                              if terminal_cell(event) == cell))
    if len(selected) > CAPACITY:
        raise ValueError("CSMC01_CAPACITY_COVERAGE_IMPOSSIBLE")
    evaluations = 0
    while len(selected) < CAPACITY:
        candidates = []
        for i in range(50):
            if i in selected:
                continue
            prospect = selected | {i}
            candidates.append((objective(reference, make_compact(rows, prospect),
                                         prospect), i))
            evaluations += 1
            if evaluations > EVAL_BUDGET:
                raise ValueError("CSMC01_EVALUATION_BUDGET")
        selected.add(min(candidates)[1])
    for _ in range(2):
        before = objective(reference, make_compact(rows, selected), selected)
        best = None
        for remove in sorted(selected - set(range(8))):
            for add in range(50):
                if add in selected:
                    continue
                prospect = (selected - {remove}) | {add}
                if {terminal_cell(rows[i]) for i in prospect} != all_cells:
                    continue
                merit = objective(reference, make_compact(rows, prospect),
                                  prospect)
                evaluations += 1
                if evaluations > EVAL_BUDGET:
                    raise ValueError("CSMC01_EVALUATION_BUDGET")
                if merit < before and (best is None or merit < best[0]):
                    best = (merit, remove, add)
        if best is None:
            break
        selected.remove(best[1])
        selected.add(best[2])
    return tuple(sorted(selected)), evaluations, reference


def make_native(rows, indices):
    state = NativeEpisodeExperience()
    for i in sorted(indices):
        ident, views, row = rows[i]
        state = state.observe(ident, views, row)
    return state


def verify_native(rows, indices):
    """Run exact original Yggdrasil native class as a separate readout control."""
    state = make_native(rows, indices)
    compact = make_compact(rows, indices)
    a, b, decisions = readout(compact)
    if state._projection != compact.projection:
        raise ValueError("CSMC01_NATIVE_PROJECTION_MISMATCH")
    originals = tuple(state.forecast((c, 0), a) for c in (0, 1) for a in (0, 1))
    terminals = tuple(state.forecast((c, 0), x, s, y)
                      for c in (0, 1) for x in (0, 1)
                      for s in (0, 1) for y in (0, 1))
    choices = tuple(state.propose((c, 0)) for c in (0, 1)) + tuple(
        state.propose((c, 0), x, s)
        for c in (0, 1) for x in (0, 1) for s in (0, 1))
    if (originals, terminals, choices) != (a, b, decisions):
        raise ValueError("CSMC01_NATIVE_COMPACT_MISMATCH")
    checkpoint = state.checkpoint()
    raw, pin = checkpoint
    restored = NativeEpisodeExperience.restore(raw, pin)
    if restored.checkpoint() != checkpoint:
        raise ValueError("CSMC01_NATIVE_COLD_RESTORE")
    if restored.consolidate().checkpoint() != checkpoint:
        raise ValueError("CSMC01_NATIVE_CONSOLIDATION")
    return state


def evaluate():
    rows = fit()
    indices, count, reference = select(rows)
    compact = make_compact(rows, indices)
    actions, tmax, smax, mean, _ = objective(reference, compact, indices)
    native50 = verify_native(rows, range(50))
    native20 = verify_native(rows, indices)
    cells = {terminal_cell(rows[i]) for i in indices}
    passed = (len(indices) == 20 and len(cells) == 15 and actions == 0
              and smax <= Fraction(1, 10) and tmax <= Fraction(15, 100))
    return {
        "schema": "yggdrasil.csmc01.native-fit-diagnostic.v1",
        "source_sha256": TRACE_PIN,
        "selected_indices": list(indices),
        "search_evaluations": count,
        "terminal_coverage": len(cells),
        "action_disagreements": actions,
        "stage1_max_gap": [smax.numerator, smax.denominator],
        "stage2_max_gap": [tmax.numerator, tmax.denominator],
        "mean_gap": [mean.numerator, mean.denominator],
        "native_full_checkpoint_bytes": len(native50.checkpoint()[0]),
        "native_reduced_checkpoint_bytes": len(native20.checkpoint()[0]),
        "engineering_gate_pass": passed,
        "science": "UNVERIFIED", "deployment": "NONE",
        "held_evaluated": False, "new_original_actions": 0,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), sort_keys=True, indent=2))
