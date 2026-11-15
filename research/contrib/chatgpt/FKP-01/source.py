"""FKP-01 original PUBLIC source boundary; synthetic, tokenless, stdlib only.

This is a development-only source implementation. It does not train a learner,
inspect protected primary labels, or authorize a scientific first-use.
The original evaluator MUST be independently qualified and frozen before
using seeds 1000..1063 or 2000..2015 for a primary result.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import random
from typing import NamedTuple

STATES = 128
PRIMITIVES = 16
ACTIONS = 16
SPEC = (
    "FKP01-SRC-V1|python=3.12|states=128|primitive_maps=16|"
    "public_primitive_edges=2048|"
    "law=ordered_composition_of_3_or_4_primitive_maps|"
    "foundation_seeds=100..131|development_worlds=200..215|"
    "primary_worlds=1000..1063|negative_worlds=2000..2015|"
    "intervention_indices=16_per_world|held_indices=all_128|"
    "worlds_fixed_split|no_private_rule_access"
)
SPEC_SHA256 = "e98f286817ed3e242cafc839a07ea14b05d7af8a34d2e5d170dcc632b5f65cfa"
if hashlib.sha256(SPEC.encode("utf-8")).hexdigest() != SPEC_SHA256:
    raise RuntimeError("FKP01_SOURCE_SPEC_IDENTITY_INVALID")


class PublicView(NamedTuple):
    """Only source-public graph data, never coefficients, law or seed."""

    relation_maps: tuple[tuple[int, ...], ...]
    intervention_inputs: tuple[int, ...]


def cohort_for_seed(seed: int) -> str:
    if type(seed) is not int:
        raise ValueError("FKP01_SEED_INVALID")
    if 100 <= seed <= 131:
        return "foundation"
    if 200 <= seed <= 215:
        return "development"
    if 1000 <= seed <= 1063:
        return "protected_primary"
    if 2000 <= seed <= 2015:
        return "protected_negative"
    if 3000 <= seed <= 3015:
        return "retention"
    raise ValueError("FKP01_SEED_NOT_PREREGISTERED")


def _private_rule_length(seed: int, cohort: str) -> int:
    if cohort == "protected_primary":
        return 3 if seed <= 1031 else 4
    if cohort in ("foundation", "retention"):
        return 3
    return 3 if seed % 2 == 0 else 4


def _public_maps(seed: int) -> tuple[tuple[int, ...], ...]:
    # Isolated public stream; the hidden rule is sampled separately.
    rng = random.Random(seed)
    maps = []
    for _ in range(PRIMITIVES):
        permutation = list(range(STATES))
        rng.shuffle(permutation)
        maps.append(tuple(permutation))
    return tuple(maps)


def _public_probes(maps: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    # Public-only SHA selection: the hidden law cannot affect probe selection.
    raw = json.dumps(maps, separators=(",", ":")).encode("ascii")
    digest = hashlib.sha256(raw).digest()
    rng = random.Random(int.from_bytes(digest[:16], "big"))
    return tuple(rng.sample(range(STATES), ACTIONS))


class PublicCausalWorld:
    """A source process. Give learners ONLY public_view() and observe()."""

    __slots__ = ("_seed", "_cohort", "_maps", "_private_law", "_negative_map", "_probes")

    def __init__(self, seed: int, *, protected_key: bytes | None = None):
        cohort = cohort_for_seed(seed)
        maps = _public_maps(seed)
        if cohort in ("protected_primary", "protected_negative", "retention"):
            # Source-owner evaluator provides a fresh 32+ byte private key.
            # This key MUST stay outside candidate code/repo/CI/learner inputs.
            # Otherwise public map facts let an arm identify the small known
            # seed range and trivially reconstruct source-private rule labels.
            if type(protected_key) is not bytes or len(protected_key) < 32:
                raise PermissionError("FKP01_PROTECTED_EVALUATOR_KEY_REQUIRED")
            law_digest = hmac.new(
                protected_key, f"FKP01-LAW-V1:{seed}".encode("ascii"),
                hashlib.sha256
            ).digest()
            private_seed = int.from_bytes(law_digest[:16], "big")
        else:
            if protected_key is not None:
                raise ValueError("FKP01_DEV_MUST_NOT_RECEIVE_EVAL_KEY")
            private_seed = seed ^ 0x6D2B79F5
        private_rng = random.Random(private_seed)
        length = _private_rule_length(seed, cohort)
        private_law = tuple(private_rng.randrange(PRIMITIVES) for _ in range(length))
        negative_map = None
        if cohort == "protected_negative":
            permutation = list(range(STATES))
            private_rng.shuffle(permutation)
            negative_map = tuple(permutation)
        self._seed = seed
        self._cohort = cohort
        self._maps = maps
        self._private_law = private_law
        self._negative_map = negative_map
        self._probes = _public_probes(maps)

    def public_view(self) -> PublicView:
        # Immutable data prevents a caller from mutating shared source state.
        return PublicView(self._maps, self._probes)

    def observe(self, intervention_input: int) -> int:
        if type(intervention_input) is not int or not 0 <= intervention_input < STATES:
            raise ValueError("FKP01_PUBLIC_INTERVENTION_INVALID")
        if self._negative_map is not None:
            return self._negative_map[intervention_input]
        value = intervention_input
        for op in self._private_law:
            value = self._maps[op][value]
        return value

    def previously_unobserved_inputs(self) -> tuple[int, ...]:
        observed = frozenset(self._probes)
        return tuple(x for x in range(STATES) if x not in observed)

    def public_action_experiences(self) -> tuple[tuple[int, int], ...]:
        # This is the ONLY action-outcome API used for fitting; 16 source actions.
        return tuple((x, self.observe(x)) for x in self._probes)

    def evaluator_only_identity(self) -> tuple[int, tuple[int, ...] | None]:
        """Private source audit ONLY. Do not pass to learners or predictors."""
        return self._seed, None if self._negative_map is not None else self._private_law


def development_source_audit() -> dict[str, object]:
    """Source-only public DEV fixtures; never opens protected cohorts."""
    examples = []
    for seed in (200, 201, 202, 203):
        first = PublicCausalWorld(seed)
        repeat = PublicCausalWorld(seed)
        view = first.public_view()
        experiences = first.public_action_experiences()
        assert len(view.relation_maps) == PRIMITIVES
        assert all(len(x) == STATES and len(set(x)) == STATES
                   for x in view.relation_maps)
        assert len(set(view.intervention_inputs)) == ACTIONS
        assert len(first.previously_unobserved_inputs()) == STATES - ACTIONS
        assert view == repeat.public_view()
        assert experiences == repeat.public_action_experiences()
        assert set(view.intervention_inputs).isdisjoint(
            first.previously_unobserved_inputs())
        assert all(x in range(STATES) and y in range(STATES)
                   for x, y in experiences)
        examples.append({
            "cohort": cohort_for_seed(seed),
            "public_edge_count": STATES * PRIMITIVES,
            "paid_action_count": len(experiences),
            "unseen_input_count": len(first.previously_unobserved_inputs()),
            "public_view_sha256": hashlib.sha256(
                json.dumps(view, separators=(",", ":")).encode("ascii")
            ).hexdigest(),
        })
    return {
        "schema": "fkp01.source-development-audit.v1",
        "source_spec_sha256": SPEC_SHA256,
        "dev_only": True,
        "protected_labels_opened": False,
        "fixtures": examples,
    }


if __name__ == "__main__":
    print(json.dumps(development_source_audit(), sort_keys=True, indent=2))
