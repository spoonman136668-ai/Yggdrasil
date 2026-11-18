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
CONTEXT_SCHEMA = "yggdrasil.ckad.native-episode-experience.v2"
MAX_EPISODES = 1024
MAX_CHECKPOINT_BYTES = 160 * 1024
PROJECTION_WITNESSES = 8
CONTEXT_BLOCK = 32
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
        "_context_start", "_context_models", "_context_weights",
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
        self._context_start = None
        self._context_models = ()
        self._context_weights = ()

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
        candidate._context_start = self._context_start
        candidate._context_models = self._context_models
        candidate._context_weights = self._context_weights
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
        if candidate._context_start is not None:
            candidate._update_context(event)
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

    def begin_context(self):
        """Retrieve models from ordered witness blocks with uniform prior mass."""
        require(len(self._ledger) >= PROJECTION_WITNESSES, "EPISODE_CONTEXT_SUPPORT")
        candidate = self._clone()
        candidate._load_context(len(candidate._ledger))
        return candidate

    def _load_context(self, context_start):
        require(type(context_start) is int
                and PROJECTION_WITNESSES <= context_start <= len(self._ledger),
                "EPISODE_CONTEXT_START")
        models = []
        for start in range(0, context_start, CONTEXT_BLOCK):
            stop = min(start + CONTEXT_BLOCK, context_start)
            block = self._ledger[start:stop]
            if len(block) < PROJECTION_WITNESSES:
                break
            model = NativeEpisodeExperience(repair=self._repair_enabled)
            for event in block:
                model._append(event)
            models.append((start, stop, digest(canonical(block)), model))
        self._context_start = context_start
        self._context_models = tuple(models)
        self._context_weights = (Fraction(1, len(models)),) * len(models)
        for event in self._ledger[context_start:]:
            self._update_context(event)

    def _update_context(self, event):
        _, views, first, next_state, second, reward = event
        view = views[0]
        products = []
        for weight, (_, _, _, model) in zip(self._context_weights, self._context_models):
            transition = model.forecast(view, first)
            terminal = model.forecast(view, first, next_state, second)
            transition_likelihood = transition if next_state else 1 - transition
            terminal_likelihood = terminal if reward else 1 - terminal
            products.append(weight * transition_likelihood * terminal_likelihood)
        total = sum(products, Fraction(0))
        self._context_weights = tuple(product / total for product in products)

    def _context_predictions(self, view, first, next_state, second):
        require(self._context_start is not None, "EPISODE_CONTEXT_REQUIRED")
        return tuple(
            model.forecast(view, first, next_state, second)
            for _, _, _, model in self._context_models
        )

    def _context_weights_for(self, view, first, next_state):
        if next_state is None:
            return self._context_weights
        next_state = PublicCausalCells._bit(next_state, "S2")
        probabilities = self._context_predictions(view, first, None, None)
        supported = tuple(
            weight * (probability if next_state else 1 - probability)
            for weight, probability in zip(self._context_weights, probabilities)
        )
        total = sum(supported, Fraction(0))
        return tuple(weight / total for weight in supported)

    def context_forecast(self, view, first, next_state=None, second=None):
        """Mix frozen forecasts, conditioning terminal reads on the public transition."""
        predictions = self._context_predictions(view, first, next_state, second)
        weights = self._context_weights_for(view, first, next_state)
        return sum((w * p for w, p in zip(weights, predictions)), Fraction(0))

    def context_explore(self, view, first=None, next_state=None):
        """Choose the intervention with greatest weighted forecast disagreement."""
        require((first is None) == (next_state is None), "EPISODE_CONTEXT_HISTORY")
        weights = self._context_weights_for(view, first, next_state)
        priorities = []
        for action in (0, 1):
            args = (action, None, None) if first is None else (first, next_state, action)
            predictions = self._context_predictions(view, *args)
            mean = sum((w * p for w, p in zip(weights, predictions)), Fraction(0))
            variance = sum((w * (p - mean) ** 2 for w, p in zip(weights, predictions)),
                           Fraction(0))
            priorities.append((variance, -abs(mean - Fraction(1, 2))))
        return int(priorities[1] > priorities[0])

    def consolidate(self):
        """Rebuild the native banks from the unique, ordered witness ledger."""
        rebuilt = NativeEpisodeExperience(repair=self._repair_enabled)
        for event in self._ledger:
            rebuilt._append(event)
        if self._context_start is not None:
            rebuilt._load_context(self._context_start)
        require(rebuilt._state_digest() == self._state_digest(), "EPISODE_REPLAY_DRIFT")
        return rebuilt

    def _repair_info(self):
        return [
            {"target": target, "slot": slot, "action": action,
             "prior_majority": majority, "evidence": list(identifiers),
             "old_counts": list(old), "new_counts": list(new)}
            for target, slot, action, majority, identifiers, old, new in self._repairs
        ]

    def _context_info(self, *, hex_weights=False):
        weights = [_ratio(weight) for weight in self._context_weights]
        if hex_weights:
            # Bound checkpoint serialization independently of Python's decimal
            # integer conversion limit during long exact posterior updates.
            weights = [[format(value, "x") for value in pair] for pair in weights]
        return {
            "context_start": self._context_start, "candidate_count": len(self._context_models),
            "weights": weights,
            "source_ranges": [
                {"start": start, "stop": stop, "sha256": source_pin}
                for start, stop, source_pin, _ in self._context_models
            ],
        }

    def _state_digest(self):
        state = {
            "projection": self._projection, "mismatches": self._mismatches,
            "transition_bank_sha256": digest(self._transition.snapshot()),
            "terminal_bank_sha256": digest(self._terminal.snapshot()),
            "transition_loss": [_ratio(loss) for loss in self._transition_loss],
            "terminal_loss": [_ratio(loss) for loss in self._terminal_loss],
            "pending_streaks": sorted(self._streaks.items()), "repairs": self._repair_info(),
        }
        if self._context_start is not None:
            state["context"] = self._context_info(hex_weights=True)
        return digest(canonical(state))

    def info(self):
        choices = ("full", "pooled")
        state_pin = self._state_digest()
        info = {
            "count": len(self._ledger), "projection": self._projection,
            "transition_hypothesis": choices[self._selected(self._transition_loss)],
            "terminal_hypothesis": choices[self._selected(self._terminal_loss)],
            "repairs": self._repair_info(), "state_sha256": state_pin,
            "derived_state_sha256": state_pin,
        }
        if self._context_start is not None:
            info["context"] = self._context_info()
        return info

    def checkpoint(self):
        data = {
            "schema": SCHEMA, "repair": self._repair_enabled,
            "episodes": self._ledger, "state_sha256": self._state_digest(),
        }
        if self._context_start is not None:
            data["schema"] = CONTEXT_SCHEMA
            data["context_start"] = self._context_start
        raw = canonical(data)
        require(len(raw) <= MAX_CHECKPOINT_BYTES, "EPISODE_CHECKPOINT_CAPACITY")
        return raw

    @classmethod
    def restore(cls, raw, expected_sha256):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_CHECKPOINT_BYTES
                and pin(expected_sha256) and digest(raw) == expected_sha256, "EPISODE_CHECKPOINT_PIN")
        try:
            data = json.loads(raw.decode("ascii"))
            require(type(data) is dict and data.get("schema") in (SCHEMA, CONTEXT_SCHEMA),
                    "EPISODE_CHECKPOINT_SCHEMA")
            keys = {"schema", "repair", "episodes", "state_sha256"}
            context = data["schema"] == CONTEXT_SCHEMA
            require(set(data) == (keys | {"context_start"} if context else keys)
                    and canonical(data) == raw, "EPISODE_CHECKPOINT_CONTRACT")
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
            if context:
                candidate._load_context(data["context_start"])
            require(candidate.checkpoint() == raw, "EPISODE_CHECKPOINT_REPLAY")
            return candidate
        except (AttributeError, KeyError, TypeError, ValueError, RecursionError) as exc:
            raise ValueError("CKAD_NATIVE_EPISODE_CHECKPOINT_REJECTED") from exc
