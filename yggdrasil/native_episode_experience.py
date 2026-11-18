"""Bounded public episode memory using the existing native causal counters.

The ordered ledger contains only witnessed interventions. Forecasts and
proposals are pure reads. A repair is local to a counter cell and can be
reconstructed from the immutable episode evidence.
"""
from fractions import Fraction
import json

from yggdrasil.native_context_basis import canonical, digest, pin, require
from yggdrasil.public_causal_cells import PublicCausalCells

SCHEMA = "yggdrasil.ckad.native-episode-experience.v1"
MAX_EPISODES = 1024
MAX_CHECKPOINT_BYTES = 160 * 1024
PROJECTION_WITNESSES = 8
MIN_LOCAL_WITNESSES = 12
CONTRADICTION_STREAK = 3
ROW_FIELDS = ("s1", "x1", "s2", "x2", "y")


def _view(value):
    require(type(value) is tuple and len(value) == 2, "EPISODE_PUBLIC_VIEW")
    return tuple(PublicCausalCells._bit(bit, "VIEW") for bit in value)


def _views(value):
    require(type(value) is tuple and len(value) == 2, "EPISODE_PAIRED_VIEWS")
    return tuple(_view(view) for view in value)


def _ratio(value):
    return [value.numerator, value.denominator]


def _terminal_slots(context, first, next_state):
    if context is None:
        return (12 + next_state, 12 + next_state)
    return (context + 2 * first + 4 * next_state, 8 + context + 2 * next_state)


def _probability(bank, slot, action):
    return Fraction(*bank.outcome_probability(slot if slot < 7 else slot - 7,
                                             action, retained=slot >= 7))


def _observe_count(bank, slot, action, outcome):
    bank.observe(slot if slot < 7 else slot - 7, action, outcome, retained=slot >= 7)


class NativeEpisodeExperience:
    """An immutable episode component carried by the cumulative learner."""

    __slots__ = (
        "_repair_enabled", "_ledger", "_ids", "_projection", "_mismatches",
        "_transition", "_terminal", "_transition_loss", "_terminal_loss",
        "_streaks", "_repairs",
    )

    def __init__(self, *, repair=True):
        require(type(repair) is bool, "EPISODE_REPAIR_FLAG")
        self._repair_enabled = repair
        self._ledger = ()
        self._ids = {}
        self._projection = None
        self._mismatches = [0, 0]
        self._transition = PublicCausalCells()
        self._terminal = PublicCausalCells()
        self._transition_loss = [Fraction(0), Fraction(0)]
        self._terminal_loss = [Fraction(0), Fraction(0)]
        self._streaks = {}
        self._repairs = ()

    @staticmethod
    def _selected(loss):
        # Prefer the smaller conditioning set on exact evidence ties.
        return 0 if loss[0] < loss[1] else 1

    def _context(self, views):
        projection = self._projection
        if projection is None:
            return None
        first, second = (view[projection] for view in views)
        return first if first == second else None

    def _clone(self):
        candidate = NativeEpisodeExperience(repair=self._repair_enabled)
        candidate._ledger = self._ledger
        candidate._ids = self._ids.copy()
        candidate._projection = self._projection
        candidate._mismatches = self._mismatches.copy()
        candidate._transition = PublicCausalCells.restore(self._transition.snapshot())
        candidate._terminal = PublicCausalCells.restore(self._terminal.snapshot())
        candidate._transition_loss = self._transition_loss.copy()
        candidate._terminal_loss = self._terminal_loss.copy()
        candidate._streaks = self._streaks.copy()
        candidate._repairs = self._repairs
        return candidate

    def observe(self, identifier, views, row):
        """Return an updated copy from one revealed public intervention episode.

        The evaluator-format initial state is validated then discarded. Only
        paired views supply the initial-state features for learning.
        """
        require(pin(identifier), "EPISODE_ID")
        views = _views(views)
        require(type(row) is dict and set(row) == set(ROW_FIELDS), "EPISODE_PUBLIC_ROW")
        bits = [PublicCausalCells._bit(row[name], name.upper()) for name in ROW_FIELDS]
        event = (identifier, views, *bits[1:])
        previous = self._ids.get(identifier)
        if previous is not None:
            require(previous == event, "EPISODE_CONFLICTING_REPLAY")
            return self
        require(len(self._ledger) < MAX_EPISODES, "EPISODE_CAPACITY")
        candidate = self._clone()
        candidate._append(event)
        return candidate

    def _append(self, event):
        identifier, views, first, next_state, second, reward = event
        context = self._context(views)
        transition_slot = 2 if context is None else context
        terminal_full, terminal_pooled = _terminal_slots(context, first, next_state)
        transition_selected = self._selected(self._transition_loss)
        terminal_selected = self._selected(self._terminal_loss)
        for index, slot in enumerate((transition_slot, 2)):
            self._transition_loss[index] += (_probability(self._transition, slot, first) - next_state) ** 2
        for index, slot in enumerate((terminal_full, terminal_pooled)):
            self._terminal_loss[index] += (_probability(self._terminal, slot, second) - reward) ** 2

        _observe_count(self._transition, 2, first, next_state)
        _observe_count(self._terminal, 12 + next_state, second, reward)
        if context is not None:
            self._learn_projected(event, context, transition_selected == 0, terminal_selected == 0)
        self._ledger += (event,)
        self._ids[identifier] = event

        if len(self._ledger) <= PROJECTION_WITNESSES:
            for coordinate in (0, 1):
                self._mismatches[coordinate] += views[0][coordinate] != views[1][coordinate]
            if len(self._ledger) == PROJECTION_WITNESSES and self._mismatches[0] != self._mismatches[1]:
                self._projection = int(self._mismatches[1] < self._mismatches[0])
                # The projection becomes visible only after these outcomes
                # were scored prequentially. Reuse only verified paired rows.
                for old_event in self._ledger:
                    projected = self._context(old_event[1])
                    if projected is not None:
                        self._learn_projected(old_event, projected, False, False)

    def _learn_projected(self, event, context, repair_transition, repair_terminal):
        identifier, _, first, next_state, second, reward = event
        full, pooled = _terminal_slots(context, first, next_state)
        self._learn_local("transition", self._transition, context, first, next_state,
                          identifier, repair_transition)
        self._learn_local("terminal", self._terminal, full, second, reward,
                          identifier, repair_terminal)
        _observe_count(self._terminal, pooled, second, reward)

    def _learn_local(self, target, bank, slot, action, outcome, identifier, selected):
        key = (target, slot, action)
        failures, successes = bank._counts[slot][action]
        running = self._streaks.get(key)
        if running is None and self._repair_enabled and selected:
            total = failures + successes
            majority = int(successes > failures)
            if (total >= MIN_LOCAL_WITNESSES and max(failures, successes) * 5 >= total * 4
                    and outcome != majority):
                running = (majority, (), (failures, successes))
        if running is not None:
            majority, identifiers, old_counts = running
            if outcome == majority:
                self._streaks.pop(key, None)
            else:
                identifiers += (identifier,)
                if len(identifiers) == CONTRADICTION_STREAK:
                    new_counts = (CONTRADICTION_STREAK if outcome == 0 else 0,
                                  CONTRADICTION_STREAK if outcome == 1 else 0)
                    bank._counts[slot][action] = list(new_counts)
                    self._streaks.pop(key, None)
                    self._repairs += ((target, slot, action, majority, identifiers, old_counts, new_counts),)
                    return
                self._streaks[key] = (majority, identifiers, old_counts)
        _observe_count(bank, slot, action, outcome)

    def _cell_choices(self, view, first, next_state, second):
        """Return bank, candidate slots, current losses and evaluated action."""
        view = _view(view)
        first = PublicCausalCells._bit(first, "X1")
        context = None if self._projection is None else view[self._projection]
        if next_state is None:
            require(second is None, "EPISODE_TRANSITION_HISTORY")
            full = 2 if context is None else context
            return self._transition, (full, 2), self._transition_loss, first
        next_state = PublicCausalCells._bit(next_state, "S2")
        second = PublicCausalCells._bit(second, "X2")
        return self._terminal, _terminal_slots(context, first, next_state), self._terminal_loss, second

    def forecast(self, view, first, next_state=None, second=None, *, full=False):
        """Return an exact one-step probability for the selected native model."""
        require(type(full) is bool, "EPISODE_FULL_FLAG")
        bank, slots, loss, action = self._cell_choices(view, first, next_state, second)
        return _probability(bank, slots[0 if full else self._selected(loss)], action)

    def propose(self, view, first=None, next_state=None):
        """Use public history to pick the most discriminating action."""
        require((first is None) == (next_state is None), "EPISODE_PROPOSAL_HISTORY")
        priorities = []
        for action in (0, 1):
            args = (action, None, None) if first is None else (first, next_state, action)
            bank, slots, loss, arm = self._cell_choices(view, *args)
            full, pooled = (_probability(bank, slot, arm) for slot in slots)
            slot = slots[self._selected(loss)]
            current = _probability(bank, slot, arm)
            trials = sum(bank._counts[slot][arm])
            priorities.append((abs(full - pooled), -abs(current - Fraction(1, 2)), -trials))
        return int(priorities[1] > priorities[0])

    def consolidate(self):
        """Rebuild the native banks from the unique, ordered witness ledger."""
        rebuilt = NativeEpisodeExperience(repair=self._repair_enabled)
        for event in self._ledger:
            rebuilt._append(event)
        require(rebuilt._state_digest() == self._state_digest(), "EPISODE_REPLAY_DRIFT")
        return rebuilt

    def _repair_info(self):
        return [
            {"target": target, "slot": slot, "action": action,
             "prior_majority": majority, "evidence": list(identifiers),
             "old_counts": list(old), "new_counts": list(new)}
            for target, slot, action, majority, identifiers, old, new in self._repairs
        ]

    def _state_digest(self):
        return digest(canonical({
            "projection": self._projection, "mismatches": self._mismatches,
            "transition_bank_sha256": digest(self._transition.snapshot()),
            "terminal_bank_sha256": digest(self._terminal.snapshot()),
            "transition_loss": [_ratio(loss) for loss in self._transition_loss],
            "terminal_loss": [_ratio(loss) for loss in self._terminal_loss],
            "pending_streaks": sorted(self._streaks.items()), "repairs": self._repair_info(),
        }))

    def info(self):
        choices = ("full", "pooled")
        state_pin = self._state_digest()
        return {
            "count": len(self._ledger), "projection": self._projection,
            "transition_hypothesis": choices[self._selected(self._transition_loss)],
            "terminal_hypothesis": choices[self._selected(self._terminal_loss)],
            "repairs": self._repair_info(), "state_sha256": state_pin,
            "derived_state_sha256": state_pin,
        }

    def checkpoint(self):
        raw = canonical({
            "schema": SCHEMA, "repair": self._repair_enabled,
            "episodes": self._ledger, "state_sha256": self._state_digest(),
        })
        require(len(raw) <= MAX_CHECKPOINT_BYTES, "EPISODE_CHECKPOINT_CAPACITY")
        return raw

    @classmethod
    def restore(cls, raw, expected_sha256):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_CHECKPOINT_BYTES
                and pin(expected_sha256) and digest(raw) == expected_sha256, "EPISODE_CHECKPOINT_PIN")
        try:
            data = json.loads(raw.decode("ascii"))
            require(type(data) is dict and set(data) == {"schema", "repair", "episodes", "state_sha256"}
                    and data["schema"] == SCHEMA and canonical(data) == raw, "EPISODE_CHECKPOINT_CONTRACT")
            episodes = data["episodes"]
            require(type(episodes) is list and len(episodes) <= MAX_EPISODES, "EPISODE_CHECKPOINT_COUNT")
            candidate = cls(repair=data["repair"])
            for event in episodes:
                require(type(event) is list and len(event) == 6, "EPISODE_CHECKPOINT_ROW")
                identifier, views, *row = event
                require(pin(identifier) and identifier not in candidate._ids, "EPISODE_CHECKPOINT_ID")
                require(type(views) is list and all(type(view) is list for view in views),
                        "EPISODE_CHECKPOINT_VIEWS")
                pair = _views(tuple(tuple(view) for view in views))
                bits = [PublicCausalCells._bit(bit, name.upper()) for name, bit in zip(ROW_FIELDS[1:], row)]
                candidate._append((identifier, pair, *bits))
            require(candidate.checkpoint() == raw, "EPISODE_CHECKPOINT_REPLAY")
            return candidate
        except (AttributeError, KeyError, TypeError, ValueError, RecursionError) as exc:
            raise ValueError("CKAD_NATIVE_EPISODE_CHECKPOINT_REJECTED") from exc
