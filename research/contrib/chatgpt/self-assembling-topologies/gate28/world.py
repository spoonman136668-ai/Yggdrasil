"""Gate28 synthetic causal worlds (research-only; no primary scoring).

The generator separates private causal rules from public learner observations.
Full learner, trained controls and evaluator must freeze before first-use.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from typing import NamedTuple

SCHEMA = "yggdrasil.gate28.causal-world.v1"
ACTIONS = tuple(range(13))  # 0..11 do(mediator,value), 12 passive
PHASES = ("A", "B", "R")
EXOGENOUS, MEDIATORS = 8, 6
RULE_DICTIONARY = ("xor", "and", "or", "nand", "maj3", "compose", "lag_xor")
SEED_COHORTS = {
    "shifted": range(501000, 501048),
    "stationary": range(502000, 502024),
    "independent_noise": range(503000, 503024),
}
PHASE_LENGTHS = {"A": 96, "B": 64, "R": 64}
HELD_LENGTHS = {"B": 32, "R": 32}


def _bits(seed: int, domain: str, *parts: object) -> int:
    data = ("gate28-world-v1|" + str(seed) + "|" + domain + "|" +
            "|".join(str(part) for part in parts)).encode("ascii")
    return int.from_bytes(sha256(data).digest(), "big")


def _pick(seed: int, domain: str, size: int, *parts: object) -> int:
    if size <= 0:
        raise ValueError("EMPTY_DOMAIN")
    return _bits(seed, domain, *parts) % size


def cohort_for(seed: int) -> str:
    for cohort, seeds in SEED_COHORTS.items():
        if seed in seeds:
            return cohort
    raise ValueError("NONPRIMARY_SEED: diagnostic constructor required")


class PublicExposure(NamedTuple):
    """Only values exposed to a learner; never hidden causal labels."""
    context: tuple[int, ...]
    intermediates: tuple[int, ...]
    action: int
    consequence: int


@dataclass(frozen=True)
class _Rule:
    kind: str
    parents: tuple[int, ...]
    invert: int


def _apply(kind: str, vals: tuple[int, ...]) -> int:
    if kind in ("xor", "lag_xor"):
        return vals[0] ^ vals[1]
    if kind == "and":
        return vals[0] & vals[1]
    if kind == "or":
        return vals[0] | vals[1]
    if kind == "nand":
        return 1 ^ (vals[0] & vals[1])
    if kind == "maj3":
        return int(sum(vals[:3]) >= 2)
    if kind == "compose":
        return (vals[0] ^ vals[1]) & vals[2]
    raise ValueError("UNKNOWN_RULE")


def _rule(seed: int, layer: str, i: int) -> _Rule:
    kind = (("maj3", "compose", "lag_xor")[i % 3] if layer == "B"
            else ("xor", "and", "or", "nand")[i % 4])
    pool = 8 + i
    count = 3 if kind in ("maj3", "compose") else 2
    parents: list[int] = []
    for j in range(count):
        raw = _pick(seed, "parent", pool, layer, i, j)
        while raw in parents:
            raw = (raw + 1) % pool
        parents.append(raw)
    if i >= 2 and i % 2 == 0:
        parents[0] = 8 + i - 1
        # Keep every causal parent distinct, including the third parent
        # in majority/compose. The old pair-only collision repair could
        # silently duplicate parents[0] and parents[2].
        used = {parents[0]}
        for j in range(1, len(parents)):
            while parents[j] in used:
                parents[j] = (parents[j] + 1) % pool
            used.add(parents[j])
    return _Rule(kind, tuple(parents), _pick(seed, "invert", 2, layer, i))


def _outcome_rule(seed: int, layer: str) -> _Rule:
    kind = ("maj3" if layer == "B" else
            ("xor", "and", "or", "nand")[_pick(seed, "out-kind", 4)])
    parents = (8, 10, 13) if layer == "B" else (8, 13)
    return _Rule(kind, parents, _pick(seed, "out-invert", 2, layer))


def _context_partition(seed: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    contexts = list(range(256))
    for i in range(255, 0, -1):
        j = _pick(seed, "context-shuffle", i + 1, i)
        contexts[i], contexts[j] = contexts[j], contexts[i]
    return tuple(contexts[:128]), tuple(contexts[128:])


def _as_context(value: int) -> tuple[int, ...]:
    return tuple((value >> bit) & 1 for bit in range(EXOGENOUS))


class HiddenWorld:
    """Evaluator-owned world; never give the instance to learner callbacks."""

    def __init__(self, seed: int, *, diagnostic: bool = False,
                 diagnostic_cohort: str = "diagnostic_shifted"):
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise ValueError("INVALID_SEED")
        if diagnostic:
            if not 900000 <= seed <= 909999:
                raise ValueError("PRIMARY_SEEDS_RESERVED")
            if diagnostic_cohort not in (
                    "diagnostic_shifted", "stationary", "independent_noise"):
                raise ValueError("INVALID_DIAGNOSTIC_COHORT")
            self.cohort = diagnostic_cohort
        else:
            if diagnostic_cohort != "diagnostic_shifted":
                raise ValueError("DIAGNOSTIC_COHORT_REQUIRES_DIAGNOSTIC")
            self.cohort = cohort_for(seed)
        self.seed = seed
        self._training, self._held = _context_partition(seed)
        self._rules = {layer: tuple(_rule(seed, layer, i)
                                    for i in range(MEDIATORS))
                       for layer in ("A", "B")}
        self._outputs = {layer: _outcome_rule(seed, layer)
                         for layer in ("A", "B")}

    def _layer(self, phase: str) -> str:
        if phase not in PHASES:
            raise ValueError("INVALID_PHASE")
        return ("B" if phase == "B" and
                self.cohort in ("shifted", "diagnostic_shifted") else "A")

    def _context(self, phase: str, step: int, *, held: bool) -> tuple[int, ...]:
        length = HELD_LENGTHS.get(phase) if held else PHASE_LENGTHS.get(phase)
        if length is None or not 0 <= step < length:
            raise ValueError("INVALID_PHASE_STEP")
        if held:
            return _as_context(self._held[(0 if phase == "B" else 32) + step])
        return _as_context(self._training[_pick(
            self.seed, "train-context", 128, phase, step)])

    def _previous_context(self, phase: str, step: int,
                          *, held: bool) -> tuple[int, ...]:
        if held:
            # The held evaluator runs after the 64 public B/R updates. A
            # lagged rule must use that last PUBLIC context, which the
            # learner has stored, rather than a private held partition value
            # unavailable to every policy at prediction time.
            return self._context(phase, PHASE_LENGTHS[phase] - 1, held=False)
        if step == 0:
            # B and R start after a PUBLIC prior phase. The learner's
            # persisted last_context is A95 or B63, respectively.
            if phase in ("B", "R"):
                preceding = "A" if phase == "B" else "B"
                return self._context(preceding,
                                     PHASE_LENGTHS[preceding] - 1,
                                     held=False)
            # A has no lagged rules; keep deterministic initial context.
            return _as_context(self._training[_pick(
                self.seed, "train-previous", 128, phase)])
        return self._context(phase, step - 1, held=False)

    def _sample(self, phase: str, step: int, action: int,
                *, held: bool) -> PublicExposure:
        if action not in ACTIONS:
            raise ValueError("INVALID_ACTION")
        x = self._context(phase, step, held=held)
        prev = self._previous_context(phase, step, held=held)
        layer = self._layer(phase)
        do_index, do_value = divmod(action, 2) if action < 12 else (-1, -1)
        cells = list(x)
        for i, rule in enumerate(self._rules[layer]):
            if i == do_index:
                bit = do_value
            else:
                vals = tuple((prev[p % 8] if rule.kind == "lag_xor" and j == 0
                              else cells[p])
                             for j, p in enumerate(rule.parents))
                bit = _apply(rule.kind, vals) ^ rule.invert
            cells.append(bit)
        out = self._outputs[layer]
        y = _apply(out.kind, tuple(cells[p] for p in out.parents)) ^ out.invert
        if self.cohort == "independent_noise":
            y = _pick(self.seed,
                      "independent-outcome-held" if held else "independent-outcome",
                      2, phase, step)
        elif _pick(self.seed, "flip-held" if held else "flip-feedback",
                   10, phase, step) == 0:
            y ^= 1
        return PublicExposure(x, tuple(cells[8:]), action, y)

    def public_context(self, phase: str, step: int) -> tuple[int, ...]:
        """Public pre-intervention context; no hidden graph, phase cue or outcome."""
        if phase not in ("B", "R"):
            raise ValueError("INVALID_PUBLIC_PREACTION_PHASE")
        return self._context(phase, step, held=False)

    def source_action(self, step: int) -> int:
        if not 0 <= step < 96:
            raise ValueError("INVALID_A_STEP")
        return _pick(self.seed, "shared-A-intervention", 13, step)

    def forced_action(self, phase: str, step: int) -> int:
        if phase not in ("B", "R") or not 0 <= step < 64:
            raise ValueError("INVALID_FORCED_STEP")
        return _pick(self.seed, "equal-exposure-forced", 13, phase, step)

    def source(self, step: int) -> PublicExposure:
        return self._sample("A", step, self.source_action(step), held=False)

    def feedback(self, phase: str, step: int, action: int) -> PublicExposure:
        if phase not in ("B", "R"):
            raise ValueError("INVALID_ADAPTIVE_PHASE")
        return self._sample(phase, step, action, held=False)

    def held_context(self, phase: str, step: int) -> tuple[int, ...]:
        if phase not in ("B", "R"):
            raise ValueError("INVALID_HELD_PHASE")
        return self._context(phase, step, held=True)

    def held_query(self, phase: str, step: int, action: int) -> PublicExposure:
        """Evaluator-only: its consequence must never reach a learner updater."""
        if phase not in ("B", "R"):
            raise ValueError("INVALID_HELD_PHASE")
        return self._sample(phase, step, action, held=True)


def validate_diagnostic() -> dict[str, object]:
    """Structural diagnostics only on an out-of-protocol seed, never scoring."""
    assert sum(len(v) for v in SEED_COHORTS.values()) == 96
    world = HiddenWorld(900001, diagnostic=True)
    source = [world.source(i) for i in range(96)]
    forced = [world.feedback("B", i, world.forced_action("B", i))
              for i in range(64)]
    held = [world.held_context(p, i) for p in ("B", "R")
            for i in range(32)]
    training_contexts = {row.context for row in source + forced}
    assert len(set(held)) == 64 and not training_contexts.intersection(held)
    assert all(row == HiddenWorld(900001, diagnostic=True).source(i)
               for i, row in enumerate(source))
    assert all(set(row.context + row.intermediates +
                   (row.consequence,)) <= {0, 1} for row in source + forced)
    assert all(row.action in ACTIONS for row in source + forced)
    assert all(world.feedback("B", i, a).context ==
               world.feedback("B", i, 12).context
               for i in range(8) for a in ACTIONS)
    return {"status": "DIAGNOSTIC_GENERATOR_PASS", "diagnostic_seed": 900001,
            "primary_consumed": False,
            "cohorts": {k: len(v) for k, v in SEED_COHORTS.items()},
            "source_rows": len(source), "B_forced_rows": len(forced),
            "unique_held_contexts": len(set(held))}


if __name__ == "__main__":
    import json
    print(json.dumps(validate_diagnostic(), sort_keys=True))
