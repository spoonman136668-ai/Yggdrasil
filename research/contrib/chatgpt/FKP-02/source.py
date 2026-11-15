"""FKP-02 source-only multi-parent causal worlds; stdlib, tokenless, no primary science.

Open source does NOT imply the private source law is visible to a learner.
The protected evaluator key must be supplied by a separate source owner
process and must NEVER be passed into model training, logs, CI or this repo.
The source instance itself is NOT a secure learner/evaluator process boundary.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import hmac
import random

INPUT_BITS = 16
EFFECT_BITS = 4
PUBLIC_PROBES = 64
PAID_PROBES = 16
HELD_PROBES = 128
SPEC = (
    "FKP02-SRC-V1|stdlib-python3.12|16-intervention-bits|4-observed-effect-bits|"
    "256-foundation-worlds-64-probes-each|foundation-gates=and2,or2,xor2,nand2|"
    "dev=200..215|primary=1000..1063|negative=2000..2015|"
    "retention=3000..3015|disjoint-private-hmac|held-gates=mux3,majority3|"
    "16-first-actions|64-dev-identifiability-audit-actions|"
    "128-cold-held-probes|same-information-baselines|no-protected-first-use"
)
SPEC_SHA256 = "ad594dac9ab0a3fbc9d7690cb84f13286f3551a06a1331fb1656f4868fb75428"
assert hashlib.sha256(SPEC.encode("utf-8")).hexdigest() == SPEC_SHA256
PUBLIC_DEVELOPMENT_KEY = hashlib.sha256(
    b"FKP02-FREE-PUBLIC-DEV-AND-FOUNDATION-KEY-NOT-SCIENTIFIC"
).digest()
FOUNDATION_GATES = ("and2", "or2", "xor2", "nand2")


def cohort(seed: int) -> str:
    if type(seed) is not int:
        raise ValueError("FKP02_SEED_TYPE_INVALID")
    if 10000 <= seed <= 10255:
        return "foundation"
    if 200 <= seed <= 215:
        return "development"
    if 1000 <= seed <= 1063:
        return "primary"
    if 2000 <= seed <= 2015:
        return "negative"
    if 3000 <= seed <= 3015:
        return "retention"
    raise ValueError("FKP02_SEED_NOT_REGISTERED")


def public_actions(seed: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Public-only fixed action list and 128 distinct held inputs."""
    cohort(seed)
    rng = random.Random(seed ^ 0x9C3C7799)
    actions = tuple(rng.sample(range(1 << INPUT_BITS), PUBLIC_PROBES))
    assert len(set(actions)) == PUBLIC_PROBES
    held_rng = random.Random(seed ^ 0xA17C41FE)
    taken = set(actions)
    held = []
    while len(held) < HELD_PROBES:
        value = held_rng.randrange(1 << INPUT_BITS)
        if value not in taken:
            taken.add(value)
            held.append(value)
    return actions, tuple(held)


@dataclass(frozen=True)
class PublicView:
    """No private operator, hidden parents, target labels, seed or key."""
    input_bits: int
    effect_bits: int
    allowed_actions: tuple[int, ...]
    held_inputs: tuple[int, ...]


def _select_hidden_rule(seed: int, owner_key: bytes, group: str):
    digest = hmac.new(owner_key, ("FKP02:PRIVATE-LAW:" + group + ":" +
                      str(seed)).encode("ascii"), hashlib.sha256).digest()
    rng = random.Random(int.from_bytes(digest, "big"))
    rules = []
    for output in range(EFFECT_BITS):
        if group == "foundation":
            gate = FOUNDATION_GATES[rng.randrange(len(FOUNDATION_GATES))]
            parents = tuple(rng.sample(range(INPUT_BITS), 2))
        elif group == "negative":
            if seed % 2 == 0:
                gate = "xor4"
                parents = tuple(rng.sample(range(INPUT_BITS), 4))
            else:
                gate = "lagxor"
                parents = tuple(rng.sample(range(INPUT_BITS), 2))
        else:
            gate = "mux3" if (seed % 2 == 0 if group != "primary"
                              else seed <= 1031) else "majority3"
            parents = tuple(rng.sample(range(INPUT_BITS), 3))
        rules.append((gate, parents))
    return tuple(rules)


def evaluate_gate(bits: int, gate: str, parents: tuple[int, ...],
                  previous_input: int = 0) -> int:
    """Source-owner rule application; DO NOT give rule identities to learners."""
    xs = [(bits >> p) & 1 for p in parents]
    if gate == "and2":
        return xs[0] & xs[1]
    if gate == "or2":
        return xs[0] | xs[1]
    if gate == "xor2":
        return xs[0] ^ xs[1]
    if gate == "nand2":
        return 1 ^ (xs[0] & xs[1])
    if gate == "mux3":
        return xs[1] if xs[0] else xs[2]
    if gate == "majority3":
        return (xs[0] & xs[1]) | (xs[0] & xs[2]) | (xs[1] & xs[2])
    if gate == "xor4":
        return xs[0] ^ xs[1] ^ xs[2] ^ xs[3]
    if gate == "lagxor":
        return xs[0] ^ ((previous_input >> parents[1]) & 1)
    raise ValueError("FKP02_OPERATOR_INVALID")


class PublicCausalWorld:
    """Source-owner only. Return public vectors and observed after-action bits."""

    __slots__ = ("_seed", "_group", "_private_rules", "_probes", "_held",
                 "_charged", "_previous_action")

    def __init__(self, seed: int, *, protected_key: bytes | None = None):
        group = cohort(seed)
        if group in ("primary", "negative", "retention"):
            if type(protected_key) is not bytes or len(protected_key) < 32:
                raise PermissionError("FKP02_PROTECTED_EVALUATOR_KEY_REQUIRED")
            key = protected_key
        else:
            if protected_key is not None:
                raise ValueError("FKP02_DEV_AND_FOUNDATION_OWNER_KEY_PROHIBITED")
            key = PUBLIC_DEVELOPMENT_KEY
        self._seed = seed
        self._group = group
        self._private_rules = _select_hidden_rule(seed, key, group)
        self._probes, self._held = public_actions(seed)
        self._charged = set()
        self._previous_action = 0

    def public_view(self) -> PublicView:
        return PublicView(INPUT_BITS, EFFECT_BITS, self._probes, self._held)

    def _source_only_outcome(self, bits: int, previous_input: int = 0) -> int:
        effect = 0
        for i, (gate, parents) in enumerate(self._private_rules):
            effect |= evaluate_gate(bits, gate, parents, previous_input) << i
        return effect

    def observe(self, bits: int) -> int:
        """Real action consequence, charged and constrained to public action order."""
        if type(bits) is not int or bits not in self._probes:
            raise ValueError("FKP02_ACTION_NOT_PUBLIC_OR_INVALID")
        limit = PAID_PROBES if self._group in ("primary", "negative", "retention") else PUBLIC_PROBES
        if bits not in self._probes[:limit]:
            raise PermissionError("FKP02_ACTION_EXCEEDS_BUDGET")
        if bits in self._charged:
            raise PermissionError("FKP02_ACTION_DUPLICATE")
        # No reward before the actual observed source intervention.
        if bits != self._probes[len(self._charged)]:
            raise PermissionError("FKP02_ACTION_ORDER_INVALID")
        self._charged.add(bits)
        effect = self._source_only_outcome(bits, self._previous_action)
        self._previous_action = bits
        return effect

    def development_only_eval(self, bits: int) -> int:
        """Separated source-owner DEV diagnostic; PROHIBITED on protected cohorts."""
        if self._group != "development":
            raise PermissionError("FKP02_DEVELOPMENT_EVAL_ONLY")
        if type(bits) is not int or not 0 <= bits < (1 << INPUT_BITS):
            raise ValueError("FKP02_DEV_EVAL_INPUT_INVALID")
        return self._source_only_outcome(bits)


def source_preflight() -> dict[str, object]:
    """Public development/foundation integrity only; NO protected first-use."""
    manifests = []
    for seed in (200, 201, 202, 203, 10000, 10001):
        a = PublicCausalWorld(seed)
        b = PublicCausalWorld(seed)
        assert a.public_view() == b.public_view()
        view = a.public_view()
        assert len(view.allowed_actions) == PUBLIC_PROBES
        assert len(view.held_inputs) == HELD_PROBES
        assert set(view.held_inputs).isdisjoint(view.allowed_actions)
        assert len(set(view.allowed_actions)) == PUBLIC_PROBES
        assert len(set(view.held_inputs)) == HELD_PROBES
        results = [a.observe(bits) for bits in view.allowed_actions]
        results2 = [b.observe(bits) for bits in view.allowed_actions]
        assert results == results2 and all(0 <= y < 1 << EFFECT_BITS for y in results)
        manifests.append({"cohort":cohort(seed), "source_steps":len(results),
                          "held_states":len(view.held_inputs),
                          "public_action_sha256":hashlib.sha256(
                              repr(view.allowed_actions).encode("ascii")).hexdigest()})
    return {"schema":"fkp02.source-dev-preflight.v1",
            "source_spec_sha256":SPEC_SHA256,"dev_only":True,
            "protected_data_unopened":True, "manifests":manifests}


if __name__ == "__main__":
    import json
    print(json.dumps(source_preflight(), sort_keys=True, indent=2))
