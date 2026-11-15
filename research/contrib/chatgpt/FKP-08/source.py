"""FKP-08 owner-only synthetic action/consequence source; protected first-use fenced."""
from __future__ import annotations
import hashlib
import hmac
import random
from dataclasses import dataclass

CONTEXTS=tuple(range(800,832))
PAID=16
STATES=256
DEV_KEY=hashlib.sha256(b"FKP08-PUBLIC-DEV-NOT-PROTECTED-KEY").digest()
PAIRS=tuple((a,b) for a in range(8) for b in range(a+1,8))
MOTIFS=tuple((a,b,ab) for a,b in PAIRS for ab in range(4))
assert len(MOTIFS)==112

def function_mask(motif:tuple[int,int,int])->int:
    a,b,ab=motif
    return sum(int((((state>>a)&1)|(((state>>b)&1)<<1))==ab)<<state for state in range(STATES))

MOTIF_MASKS=tuple(function_mask(m) for m in MOTIFS)

def cohort(context:int)->str:
    if type(context) is not int:raise ValueError("FKP08_CONTEXT_TYPE_INVALID")
    if 700<=context<=703:return "fixture"
    if context in CONTEXTS:return "development"
    if 1800<=context<=1863:return "primary"
    if 2800<=context<=2815:return "negative"
    raise ValueError("FKP08_CONTEXT_NOT_REGISTERED")

@dataclass(frozen=True)
class PublicView:
    context:int
    revision:int
    choices:tuple[int,...]
    held:tuple[int,...]

class Source:
    """The source must live in a separate evaluator process for real science."""
    __slots__=("_key","_contexts")
    def __init__(self,*,protected_key:bytes|None=None):
        if protected_key is not None and (type(protected_key) is not bytes or len(protected_key)<32):
            raise PermissionError("FKP08_OWNER_KEY_TOO_SHORT")
        self._key=protected_key
        self._contexts={}
    def _digest(self,context:int,revision:int,label:str)->bytes:
        kind=cohort(context)
        if kind not in ("development","fixture") and self._key is None:
            raise PermissionError("FKP08_PROTECTED_EVALUATOR_KEY_REQUIRED")
        key=DEV_KEY if kind in ("development","fixture") else self._key
        return hmac.new(key,f"FKP08:{label}:{context}:{revision}".encode(),hashlib.sha256).digest()
    def _base(self,context:int)->int:
        # One unstructured source-private 256-bit rule; no learner oracle.
        return int.from_bytes(b"".join(self._digest(context,0,f"base-{i}") for i in range(1)),"big")
    def _delta(self,context:int,revision:int)->int:
        if not 1<=revision<=3:raise ValueError("FKP08_BAD_REVISION")
        r=random.Random(int.from_bytes(self._digest(context,revision,"delta"),"big"))
        a,b=r.sample(range(len(MOTIFS)),2)
        return MOTIF_MASKS[a]^MOTIF_MASKS[b]
    def _law(self,context:int,revision:int)->int:
        if type(revision) is not int or not 0<=revision<=3:
            raise ValueError("FKP08_REVISION_INVALID")
        result=self._base(context)
        for r in range(1,revision+1):result^=self._delta(context,r)
        return result
    def view(self,context:int,revision:int)->PublicView:
        kind=cohort(context)
        if kind not in ("development","fixture") and self._key is None:
            raise PermissionError("FKP08_PROTECTED_EVALUATOR_KEY_REQUIRED")
        if type(revision) is not int or not 0<=revision<=3:raise ValueError("FKP08_BAD_REVISION")
        if revision==0:return PublicView(context,revision,tuple(range(STATES)),())
        # Deterministic public pool split: 128 paid choices and 128 held, no overlap.
        r=random.Random((context<<9)^revision^0x7249A0)
        first=tuple(r.sample(range(STATES),STATES))
        return PublicView(context,revision,first[:128],first[128:])
    def observe(self,context:int,revision:int,action:int)->int:
        view=self.view(context,revision)
        if type(action) is not int or action not in view.choices:
            raise ValueError("FKP08_ACTION_NOT_PUBLIC")
        key=(context,revision)
        seen=self._contexts.setdefault(key,set())
        max_allowed=STATES if revision==0 else PAID
        if len(seen)>=max_allowed:raise PermissionError("FKP08_ACTION_LIMIT_EXCEEDED")
        if action in seen:raise PermissionError("FKP08_ACTION_ALREADY_PAID")
        seen.add(action)
        return (self._law(context,revision)>>action)&1
    def held_dev(self,context:int,revision:int,values:tuple[int,...])->tuple[int,...]:
        if cohort(context)!="development":raise PermissionError("FKP08_HELD_DEV_ONLY")
        view=self.view(context,revision)
        if revision==0 or values!=view.held or type(values) is not tuple:
            raise ValueError("FKP08_HELD_INPUT_DRIFT")
        law=self._law(context,revision)
        return tuple((law>>x)&1 for x in values)
    def charged(self,context:int,revision:int)->int:
        return len(self._contexts.get((context,revision),set()))
