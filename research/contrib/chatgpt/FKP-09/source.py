"""FKP-09 original public DEV source: actual shared-core changes and fixed conflicting laws.

Owner/source process only. The learner receives paid actions and consequences,
NEVER HMAC keys, hidden bit edits, context truth vectors or protected cohorts.
Public synthetic DEV cannot substitute for separately blinded owner first-use.
"""
from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass

BITS=128
CONTEXTS=tuple(range(900,916))
FIXTURE=tuple(range(850,854))
N_POOL=128
N_HELD=128
CONTEXT_PAID=32
CORE_PAID=128
DEV_KEY=hashlib.sha256(b"FKP09-public-development-only-source-not-owner").digest()
SPEC=("FKP09-SRC-V1|128-binary-causal-weights|16-contexts|32-paid-context-actions|"
"128-onehot-shared-base-actions-per-stage|4-global-stages|"
"2-context-flip-indices|2-stage-flip-indices|8-bit-adapter-capacity|"
"128-disjoint-held-per-context|12-vs-32-source-identifiability|"
"DEV=900..915|FIX=850..853|PROTECTED=1900..1963|"
"OWNER-PRIVATE-HMAC|NEGATIVE-16BIT-GLOBAL-SHIFT")
SPEC_SHA256="f5e32854fb5d179b33f06c51250c6d15b9db0b84e3e2679955f2d8848a9077c8"
assert hashlib.sha256(SPEC.encode()).hexdigest()==SPEC_SHA256


def cohort(context:int)->str:
    if type(context) is not int:raise ValueError("FKP09_CONTEXT_INVALID")
    if context in CONTEXTS:return "development"
    if context in FIXTURE:return "fixture"
    if 1900<=context<=1963:return "primary"
    if 2900<=context<=2915:return "negative"
    raise ValueError("FKP09_CONTEXT_NOT_REGISTERED")


def parity(value:int)->int:
    if type(value) is not int or not 0<=value<1<<BITS:
        raise ValueError("FKP09_CAUSAL_MASK_INVALID")
    return value.bit_count()&1


def public_masks(context:int)->tuple[tuple[int,...],tuple[int,...]]:
    cohort(context)
    # Public action identities are generated without access to secret source.
    used=set();samples=[]
    for n in range(N_POOL+N_HELD):
        raw=hashlib.sha256(f"FKP09-ACTION:{context}:{n}".encode()).digest()
        mask=int.from_bytes(raw[:16],"big")
        if not mask or mask in used:raise ValueError("FKP09_PUBLIC_ACTION_COLLISION")
        used.add(mask);samples.append(mask)
    return tuple(samples[:N_POOL]),tuple(samples[N_POOL:])


@dataclass(frozen=True)
class PublicView:
    context:int
    choices:tuple[int,...]
    held_masks:tuple[int,...]


class Source:
    """Only the actual source owner may read source-private causal laws."""

    def __init__(self,*,protected_key:bytes|None=None):
        if protected_key is not None and (type(protected_key) is not bytes or len(protected_key)<32):
            raise PermissionError("FKP09_OWNER_KEY_TOO_SHORT")
        self._key=protected_key
        self._core_paid={}
        self._context_paid={}

    def _scope(self,context:int)->str:
        group=cohort(context)
        if group in ("primary","negative"):
            if self._key is None:raise PermissionError("FKP09_PROTECTED_SOURCE_KEY_REQUIRED")
        elif self._key is not None:raise PermissionError("FKP09_PROTECTED_KEY_NOT_FOR_PUBLIC_DEV")
        return group

    def _digest(self,label:str)->bytes:
        key=DEV_KEY if self._key is None else self._key
        return hmac.new(key,label.encode(),hashlib.sha256).digest()

    def _original_core(self)->int:
        raw=b"".join(self._digest(f"ORIGINAL-CORE:{n}") for n in range(4))
        return int.from_bytes(raw,"big")

    def _stage_flip(self,stage:int)->int:
        if type(stage) is not int or not 1<=stage<=4:
            raise ValueError("FKP09_STAGE_INVALID")
        count=16 if stage==4 else 2
        # Source HMAC stream, never passed to learner.
        order=sorted(range(BITS),key=lambda x:self._digest(f"STAGE-{stage}:BIT:{x}"))
        return sum(1<<bit for bit in order[:count])

    def _shared_core(self,stage:int)->int:
        if type(stage) is not int or not 0<=stage<=4:
            raise ValueError("FKP09_STAGE_INVALID")
        value=self._original_core()
        for i in range(1,stage+1):value^=self._stage_flip(i)
        return value

    def _context_law(self,context:int)->int:
        self._scope(context)
        # Each genuinely independent context has a different but related law.
        order=sorted(range(BITS),key=lambda bit:self._digest(f"CONTEXT:{context}:BIT:{bit}"))
        return self._original_core()^(1<<order[0])^(1<<order[1])

    def public_view(self,context:int)->PublicView:
        self._scope(context)
        pool,held=public_masks(context)
        return PublicView(context,pool,held)

    def observe_core(self,stage:int,bit:int,*,fixture_shock:bool=False)->int:
        if type(stage) is not int or stage not in (0,1,2,3,4):
            raise ValueError("FKP09_SOURCE_STAGE_INVALID")
        if stage==4 and not fixture_shock:
            raise PermissionError("FKP09_STAGE4_FIXTURE_ONLY")
        if type(bit) is not int or not 0<=bit<BITS:
            raise ValueError("FKP09_CORE_ONEHOT_INVALID")
        paid=self._core_paid.setdefault(stage,set())
        if bit in paid:raise PermissionError("FKP09_CORE_DUPLICATE_ACTION")
        if len(paid)>=CORE_PAID:raise PermissionError("FKP09_CORE_BUDGET_EXCEEDED")
        paid.add(bit)
        return (self._shared_core(stage)>>bit)&1

    def observe_context(self,context:int,mask:int)->int:
        view=self.public_view(context)
        if type(mask) is not int or mask not in view.choices:
            raise ValueError("FKP09_CONTEXT_ACTION_NOT_PUBLIC")
        paid=self._context_paid.setdefault(context,set())
        if mask in paid:raise PermissionError("FKP09_CONTEXT_DUPLICATE_ACTION")
        if len(paid)>=CONTEXT_PAID:raise PermissionError("FKP09_CONTEXT_BUDGET_EXCEEDED")
        paid.add(mask)
        return parity(mask&self._context_law(context))

    def held_dev(self,context:int,masks:tuple[int,...])->tuple[int,...]:
        if self._scope(context)!="development":
            raise PermissionError("FKP09_HELD_DEV_ONLY")
        _,held=public_masks(context)
        if type(masks) is not tuple or masks!=held:
            raise ValueError("FKP09_HELD_INPUT_DRIFT")
        law=self._context_law(context)
        return tuple(parity(mask&law) for mask in masks)

    def core_charged(self,stage:int)->int:
        return len(self._core_paid.get(stage,set()))

    def context_charged(self,context:int)->int:
        return len(self._context_paid.get(context,set()))
