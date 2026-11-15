"""ST4 native eight-cell causal-credit hypothesis memory, frozen DEV candidate.

Only eight PUBLIC bits, prior observed change bits and ANNOUNCED actions.
No hidden law, trial, arm, actor seed, pending effect or source API imported.
A disclosed shift-1/2/3 physical inductive prior is fitted through observed
public transitions. This is NOT a generalizable representation proof.

Nine bounded hypothesis banks; 3 rotation candidates x 8 native output
cells x 4 current actions x 2 prior intervention contexts x 2 uint8 residual
counts = 3,456 learned evidence bytes. Each actual public consequence updates
AFTER the preaction forecast. All state, including bank allocation, is
serialized with integer-only semantics. No new neural/tokens/transformers.
"""
import json

SCHEMA="yggdrasil.nci04.st4.integer-causal-native8.v1"
ROTS=(1,2,3)
N=8
ACTIONS=4
BANKS=9
MAX=255
MAX_CLOCK=10000000
VARIANTS=("causal","no_delay","sham","erase","label_shuffle")


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False)


def bits(v):
    if (type(v) not in (list,tuple) or len(v)!=N or
        any(type(i) is not int or i not in (0,1) for i in v)):
        raise ValueError("ST4_NATIVE_BAD_PUBLIC_BITS")


def action_ok(a):
    if type(a) is not int or a not in range(ACTIONS):
        raise ValueError("ST4_NATIVE_BAD_ANNOUNCED_ACTION")


def shifted(raw,k,index):
    return raw[(index-k)%N]


def make_bank():
    return {
        "counts":[[
            [[[0,0] for _ in range(2)] for _ in range(ACTIONS)]
            for _ in range(N)
        ] for _ in ROTS],
        "seen":0,"last":0,"mistakes":0,
    }


def condition(previous,variant,for_update):
    if previous is not None:
        action_ok(previous)
    if variant=="no_delay":
        return 0
    if variant=="sham" and for_update:
        return int(previous==3)
    return int(previous==2)


def rotate_candidates(before,after):
    bits(before);bits(after)
    return tuple(r for r in ROTS if all(
        shifted(before,r,i)==after[i] for i in range(N)
    ))


def residual(before,target,i,rot):
    # After-action observed public delta makes y_next = old XOR delta.
    return before[i]^target[i]^shifted(before,rot,i)


def prob(row):
    yes,no=row
    return (yes+1)/(yes+no+2)


def increment(pair,value):
    if MAX in pair:
        pair[0]//=2
        pair[1]//=2
    pair[0 if value else 1]+=1


class NativeCausal8:
    """Bounded learned intervention history; no private source handles."""

    def __init__(self,variant="causal"):
        if variant not in VARIANTS:
            raise ValueError("ST4_NATIVE_BAD_VARIANT")
        self.variant=variant
        self.banks=[None]*BANKS
        self.active=None
        self.rotation=None
        self.prior=None
        self.previous_change=[0]*N
        self.step=0
        self.clock=0
        self.updates=0
        self.forks=0
        self.retrievals=0
        self.bad_streak=0

    def reset_episode(self):
        if self.variant=="erase":
            self.banks=[None]*BANKS
            self.active=None
        self.rotation=None
        self.prior=None
        self.previous_change=[0]*N
        self.step=0
        # Contradiction repair must persist across bounded two-action arms.
        # Erasing it here made a 3-consecutive-probe repair impossible.
        if self.variant=="erase":
            self.bad_streak=0

    def _select(self,rot,force_new=False):
        # Shift is inferred from the ACTUAL first source action outcome, not
        # hidden task law/rotation. Rotation-less ambiguities are retained.
        available=[
            (i,b) for i,b in enumerate(self.banks)
            if b is not None and sum(sum(
                sum(sum(pair) for pair in modes)
                for modes in actions)
                for actions in b["counts"][rot-1])>0
        ]
        if available and not force_new:
            if self.active is not None and self.banks[self.active] is not None:
                return
            self.active=min(available,key=lambda t:(
                -t[1]["seen"],t[0]
            ))[0]
            self.retrievals+=1
        else:
            try:
                slot=self.banks.index(None)
            except ValueError:
                slot=min(range(BANKS),key=lambda j:(
                    self.banks[j]["last"],j
                ))
            self.banks[slot]=make_bank()
            self.active=slot
            self.forks+=1

    def predict(self,public,action):
        bits(public);action_ok(action)
        if self.active is None or self.rotation is None:
            return [0.5]*N
        bank=self.banks[self.active]
        if bank is None:
            raise ValueError("ST4_NATIVE_INTERNAL_MISSING_BANK")
        mode=condition(self.prior,self.variant,False)
        return [
            (1.-prob(bank["counts"][self.rotation-1][i][action][mode])
             if public[i]^shifted(public,self.rotation,i)
             else prob(bank["counts"][self.rotation-1][i][action][mode]))
            for i in range(N)
        ]

    def observe(self,public,action,target,next_public,*,train=True):
        bits(public);bits(target);bits(next_public);action_ok(action)
        if [a^b for a,b in zip(public,next_public)]!=list(target):
            raise ValueError("ST4_NATIVE_UNAUTHENTIC_SOURCE_TARGET")
        if type(train) is not bool or self.step>=2 or self.clock>=MAX_CLOCK:
            raise ValueError("ST4_NATIVE_INVALID_MODE_OR_LIMIT")
        forecast=self.predict(public,action)
        if train:
            self.clock+=1
            if self.rotation is None and action in (2,3):
                found=rotate_candidates(public,next_public)
                if found:
                    self.rotation=found[0]
                    self._select(self.rotation)
            elif self.rotation is not None and self.active is not None:
                bank=self.banks[self.active]
                mode=condition(self.prior,self.variant,True)
                fail=sum(
                    (y==0 and p>.75) or (y==1 and p<.25)
                    for p,y in zip(forecast,target)
                )
                self.bad_streak=self.bad_streak+1 if fail>=4 else 0
                if self.bad_streak>=3:
                    # Preserve the old bank for cold recall; allocate a
                    # new bounded hypothesis only on repeated REAL public
                    # contradictory consequences, never on source law ID.
                    self.active=None
                    self._select(self.rotation,force_new=True)
                    bank=self.banks[self.active]
                    self.bad_streak=0
                for i,y in enumerate(target):
                    v=residual(public,target,i,self.rotation)
                    if self.variant=="label_shuffle":
                        v^=(i+action)%2
                    increment(bank["counts"][self.rotation-1][i][action][mode],v)
                bank["seen"]+=1
                bank["last"]=self.clock
                bank["mistakes"]+=fail
            self.updates+=1
        else:
            # Nontraining inference is allowed to resolve an observable
            # public shift but cannot allocate/modify learned counters.
            if self.rotation is None and action in (2,3):
                found=rotate_candidates(public,next_public)
                if found:
                    self.rotation=found[0]
                    available=[
                        (j,b) for j,b in enumerate(self.banks)
                        if b is not None and b["seen"]>0
                    ]
                    if available:
                        self.active=min(available,key=lambda t:(
                            -t[1]["seen"],t[0]
                        ))[0]
        self.prior=action
        self.previous_change=list(target)
        self.step+=1
        return forecast

    def snapshot(self):
        return canonical({
            "schema":SCHEMA,"variant":self.variant,
            "banks":self.banks,"active":self.active,"rotation":self.rotation,
            "prior":self.prior,"previous_change":self.previous_change,
            "step":self.step,"clock":self.clock,"updates":self.updates,
            "forks":self.forks,"retrievals":self.retrievals,
            "bad_streak":self.bad_streak,
        })

    @classmethod
    def restore(cls,payload):
        if type(payload) is not str or len(payload)>350000:
            raise ValueError("ST4_NATIVE_INVALID_CHECKPOINT_SIZE")
        try:
            d=json.loads(payload)
            keys={"schema","variant","banks","active","rotation","prior",
                  "previous_change","step","clock","updates","forks",
                  "retrievals","bad_streak"}
            if (type(d) is not dict or set(d)!=keys or d["schema"]!=SCHEMA or
                d["variant"] not in VARIANTS or
                type(d["banks"]) is not list or len(d["banks"])!=BANKS or
                (d["active"] is not None and
                 (type(d["active"]) is not int or
                  d["active"] not in range(BANKS))) or
                (d["rotation"] is not None and
                 (type(d["rotation"]) is not int or
                  d["rotation"] not in ROTS)) or
                (d["prior"] is not None and
                 (type(d["prior"]) is not int or
                  d["prior"] not in range(ACTIONS))) or
                any(type(d[k]) is not int or not 0<=d[k]<=MAX_CLOCK for k in
                    ("step","clock","updates","forks","retrievals","bad_streak")) or
                d["step"]>2):
                raise ValueError("ST4_NATIVE_INVALID_CHECKPOINT_SHAPE")
            bits(d["previous_change"])
            if d["active"] is not None and d["banks"][d["active"]] is None:
                raise ValueError("ST4_NATIVE_BROKEN_ACTIVE")
            for bank in d["banks"]:
                if bank is None:
                    continue
                if (type(bank) is not dict or set(bank)!={
                    "counts","seen","last","mistakes"
                } or any(type(bank[k]) is not int or
                    not 0<=bank[k]<=MAX_CLOCK
                    for k in ("seen","last","mistakes")) or
                    type(bank["counts"]) is not list or
                    len(bank["counts"])!=3):
                    raise ValueError("ST4_NATIVE_INVALID_BANK")
                for rotation in bank["counts"]:
                    if type(rotation) is not list or len(rotation)!=N:
                        raise ValueError("ST4_NATIVE_BAD_ROTATION")
                    for cell in rotation:
                        if type(cell) is not list or len(cell)!=ACTIONS:
                            raise ValueError("ST4_NATIVE_BAD_CELL")
                        for mode in cell:
                            if type(mode) is not list or len(mode)!=2:
                                raise ValueError("ST4_NATIVE_BAD_MODE")
                            for pair in mode:
                                if (type(pair) is not list or len(pair)!=2 or
                                    any(type(v) is not int or v not in
                                        range(MAX+1) for v in pair)):
                                    raise ValueError("ST4_NATIVE_BAD_COUNTER")
            obj=cls(d["variant"])
            for k in keys-{"schema","variant"}:
                setattr(obj,k,d[k])
            if obj.snapshot()!=payload:
                raise ValueError("ST4_NATIVE_NOT_CANONICAL")
            return obj
        except (KeyError,TypeError,OverflowError) as exc:
            raise ValueError("ST4_NATIVE_BAD_CHECKPOINT") from exc

    def accounting(self):
        return {
            "native_cells":N,"banks":BANKS,
            "learned_uint8_counter_bytes":BANKS*3*N*ACTIONS*2*2,
            "extra_neural_coefficients":0,
            "architectural_prior":"three disclosed fixed public rotations",
            "checkpoint_json_bytes":len(self.snapshot().encode()),
            "integer_state_only":True,"privileged_source_access":False,
        }
