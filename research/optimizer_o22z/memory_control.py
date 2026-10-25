"""O22-Z: source-PUBLIC history memory admission ONLY, not real MiniGrid.

An independent conventional recency Beta control gets exactly the same
selected source-shaped turn-return effect rows as original R1 fast/slow cells.
No source-world simulator, seed, latent regime tag or hidden dynamics.
"""
from __future__ import annotations
import hashlib,json,math
from research.native.itd02.r1.native_policy import canonical
from research.optimizer_o22x.transition_belief import check_transition,check_public

SCHEMA="optimizer.o22z.conventional-conditional-recency-beta.v1"
DECAY=.92
LIMIT=1000

def key(public,action):
    check_public(public)
    if type(action) is not int or action not in (0,1):
        raise ValueError("O22Z_ONLY_ACTUALLY_SELECTED_LEGAL_TURN")
    return hashlib.sha256(canonical(public)+bytes([action])).hexdigest()

class ConditionalRecencyBeta:
    """Independently implemented causal-event conditional finite Beta memory.

    Prior Beta(1,1); recency discounts observed evidence only.  A key
    combines CURRENT SIX PUBLIC FIELDS and legal selected turn, never a
    hidden source world ID, fixture regime or future return.
    """

    def __init__(self):
        self.rows={}
        self.events=0

    def predict(self,current,action):
        k=key(current,action)
        row=self.rows.get(k)
        if row is None:
            return (.5,0.)
        count,blocked=row
        return ((1.+blocked)/(2.+count),count)

    def learn(self,before,action,returned_after):
        blocked,translation=check_transition(before,action,returned_after)
        if action not in (0,1) or translation:
            raise ValueError("O22Z_REAL_SELECTED_TURN_REQUIRED")
        if self.events>=LIMIT:
            raise ValueError("O22Z_FINITE_EXPERIENCE_LIMIT")
        k=key(before,action)
        count,positive=self.rows.get(k,(0.,0.))
        self.rows[k]=(DECAY*count+1.,DECAY*positive+float(blocked))
        self.events+=1

    def checkpoint(self):
        b={"schema":SCHEMA,"rows":self.rows,"events":self.events,"decay":DECAY}
        payload=canonical(b)
        return canonical({"state":b,"sha256":hashlib.sha256(payload).hexdigest()})

    @classmethod
    def restore(cls,raw):
        try:
            if type(raw) is not bytes or not 0<len(raw)<60000:
                raise ValueError("O22Z_MEMORY_SIZE")
            outer=json.loads(raw)
            if type(outer) is not dict or set(outer)!={"state","sha256"}:
                raise ValueError("O22Z_MEMORY_ENVELOPE")
            b=outer["state"]
            if (type(b) is not dict or set(b)!={"schema","rows","events","decay"} or
                b["schema"]!=SCHEMA or b["decay"]!=DECAY or
                hashlib.sha256(canonical(b)).hexdigest()!=outer["sha256"]):
                raise ValueError("O22Z_MEMORY_IDENTITY_OR_CHECKSUM")
            if (type(b["rows"]) is not dict or len(b["rows"])>100 or
                type(b["events"]) is not int or not 0<=b["events"]<=LIMIT):
                raise ValueError("O22Z_MEMORY_COUNTS")
            for k,row in b["rows"].items():
                if (type(k) is not str or len(k)!=64 or
                    type(row) is not list or len(row)!=2 or
                    any(type(v) not in (float,int) or not math.isfinite(v)
                        or not 0<=v<=LIMIT+1 for v in row) or row[1]>row[0]+1e-8):
                    raise ValueError("O22Z_MEMORY_ROW")
            obj=cls()
            obj.rows={k:tuple(v) for k,v in b["rows"].items()}
            obj.events=b["events"]
            return obj
        except (ValueError,TypeError,KeyError,OverflowError) as e:
            raise ValueError("O22Z_UNTRUSTED_MEMORY_COLD") from e

def choice(model,current,margin=.10):
    """Public front presently blocked; prefer a learned clear-side turn."""
    check_public(current)
    if not current["front_blocked"]:
        return None
    if isinstance(model,ConditionalRecencyBeta):
        left=model.predict(current,0)[0]
        right=model.predict(current,1)[0]
    else:
        left=model.predict(current,0)[0]
        right=model.predict(current,1)[0]
    if abs(left-right)<margin:
        return None
    return 0 if left<right else 1
