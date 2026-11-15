"""FKP-03 fresh causal intervention source. Source-owner only, no production model.

Source-selected hidden laws are never inputs to fitting or action-selection.
Protected primary/negative worlds require an external evaluator-owned key and
MUST NOT be instantiated by research jobs. The DEV source is public synthetic.
"""
from __future__ import annotations
import hashlib
import hmac
import random
from dataclasses import dataclass

N_INPUT=12
FOUNDATION_SIZE=256
N_POOL=64
N_PAID=16
N_HELD=128
SPEC=("FKP03-SRC-V1|12-binary-causal-inputs|1-effect-bit|256-foundation-worlds-64-probes|"
"dev=400..415|primary=1400..1463|neg=2400..2415|held=128|pool=64|paid=16|"
"unknown-mux3-majority3|HMAC-evaluator-key|learn-2input-foundation-then-3input-closure|"
"active-vs-random-vs-balanced-vs-known-family-reference")
SPEC_SHA256="3ce2d43c77ec55523d6bbe6872b4dc6a9481db719124ccbfe02c40c6f6637246"
assert hashlib.sha256(SPEC.encode()).hexdigest()==SPEC_SHA256
DEV_KEY=hashlib.sha256(b"FKP03-PUBLIC-DEV-NOT-PROTECTED-EVALUATOR").digest()


def cohort(seed: int) -> str:
    if type(seed) is not int:
        raise ValueError("FKP03_SEED_INVALID")
    if 10000 <= seed <= 10255:
        return "foundation"
    if 400 <= seed <= 415:
        return "development"
    if 1400 <= seed <= 1463:
        return "primary"
    if 2400 <= seed <= 2415:
        return "negative"
    raise ValueError("FKP03_SEED_NOT_REGISTERED")


def public_pool(seed: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    cohort(seed)
    rng=random.Random(seed ^ 0x5338E21)
    pool=tuple(rng.sample(range(1 << N_INPUT), N_POOL))
    rng2=random.Random(seed ^ 0x89C99F8)
    occupied=set(pool)
    held=[]
    while len(held)<N_HELD:
        v=rng2.randrange(1 << N_INPUT)
        if v not in occupied:
            occupied.add(v); held.append(v)
    return pool,tuple(held)


@dataclass(frozen=True)
class PublicView:
    intervention_choices: tuple[int, ...]
    held_inputs: tuple[int, ...]
    input_bits: int


class CausalWorld:
    __slots__=("_cohort","_rule","_pool","_held","_observed","_paid")

    def __init__(self, seed: int, *, protected_key: bytes | None = None):
        group=cohort(seed)
        if group in ("primary","negative"):
            if type(protected_key) is not bytes or len(protected_key)<32:
                raise PermissionError("FKP03_PROTECTED_KEY_REQUIRED")
            key=protected_key
        else:
            if protected_key is not None:
                raise ValueError("FKP03_DEV_KEY_MISMATCH")
            key=DEV_KEY
        self._cohort=group
        digest=hmac.new(key,f"FKP03-LAW:{group}:{seed}".encode(),hashlib.sha256).digest()
        r=random.Random(int.from_bytes(digest,"big"))
        if group=="foundation":
            typ=("AND","OR","XOR","NAND")[r.randrange(4)]
            parents=tuple(r.sample(range(N_INPUT),2))
        elif group=="negative":
            typ="XOR4"
            parents=tuple(r.sample(range(N_INPUT),4))
        else:
            typ="MUX3" if r.randrange(2)==0 else "MAJ3"
            parents=tuple(r.sample(range(N_INPUT),3))
        self._rule=(typ,parents)
        self._pool,self._held=public_pool(seed)
        self._observed=set()
        self._paid=0

    def public_view(self) -> PublicView:
        return PublicView(self._pool,self._held,N_INPUT)

    def _consequence(self, value: int) -> int:
        typ,parents=self._rule
        bits=tuple((value>>p)&1 for p in parents)
        if typ=="AND": return bits[0]&bits[1]
        if typ=="OR": return bits[0]|bits[1]
        if typ=="XOR": return bits[0]^bits[1]
        if typ=="NAND": return 1 ^ (bits[0]&bits[1])
        if typ=="MUX3": return bits[1] if bits[0] else bits[2]
        if typ=="MAJ3": return int(sum(bits)>=2)
        if typ=="XOR4":return bits[0]^bits[1]^bits[2]^bits[3]
        raise ValueError("FKP03_RULE_INVALID")

    def observe(self, public_action: int) -> int:
        if type(public_action) is not int or public_action not in self._pool:
            raise ValueError("FKP03_ACTION_NOT_PUBLIC")
        cap=N_POOL if self._cohort=="foundation" else N_PAID
        if self._paid>=cap:
            raise PermissionError("FKP03_ACTION_BUDGET_EXCEEDED")
        if public_action in self._observed:
            raise PermissionError("FKP03_DUPLICATE_ACTION")
        self._observed.add(public_action)
        self._paid+=1
        return self._consequence(public_action)

    def development_only_labels(self, inputs: tuple[int, ...]) -> tuple[int, ...]:
        if self._cohort!="development":
            raise PermissionError("FKP03_HELD_LABELS_DEV_ONLY")
        if type(inputs) is not tuple or inputs!=self._held:
            raise ValueError("FKP03_EVALUATOR_INPUT_DRIFT")
        return tuple(self._consequence(x) for x in inputs)

    @property
    def charged_actions(self) -> int:
        return self._paid


def dev_preflight() -> dict:
    rows=[]
    for seed in (400,401,10000,10001):
        a,b=CausalWorld(seed),CausalWorld(seed)
        p=a.public_view()
        assert p==b.public_view()
        assert len(p.intervention_choices)==64 and len(set(p.intervention_choices))==64
        assert len(p.held_inputs)==128 and len(set(p.held_inputs))==128
        assert not set(p.held_inputs).intersection(p.intervention_choices)
        n=64 if cohort(seed)=="foundation" else 16
        x=p.intervention_choices[:n]
        y=tuple(a.observe(i) for i in x)
        assert y==tuple(b.observe(i) for i in x)
        rows.append({"cohort":cohort(seed),"paid_actions":len(y),
                     "public_pool_sha256":hashlib.sha256(str(p.intervention_choices).encode()).hexdigest()})
    for seed in (1400,1463,2400,2415):
        try:CausalWorld(seed)
        except PermissionError:pass
        else:raise AssertionError("FKP03_PROTECTED_WORLD_LEAK")
    return {"schema":"fkp03.source-dev-preflight.v1","public_dev_only":True,
            "protected_first_use":False,"spec_sha256":SPEC_SHA256,"fixtures":rows}

if __name__=="__main__":
    import json
    print(json.dumps(dev_preflight(),sort_keys=True))
