"""Source-free tokenless causal hypothesis portfolio.

Research-only bounded native integer candidate weights, immutable cumulative
world slots, and cold-restorable structural uncertainty. No acceptance/authority.
All program terms are an explicit supplied inductive grammar, NOT discovered
primitive mechanisms or grounded original-world causal truth.
"""
from functools import lru_cache
import hashlib
import json

SCHEMA="yggdrasil.ckad.portfolio-v1.v1"
SOURCE_MODE="engineering_fixture_only"
GATES=tuple(g for g in range(1,32) if g.bit_count() in (1,2))
CANDIDATES=64*len(GATES)*2
ALL_CANDIDATES=(1<<CANDIDATES)-1
MAX_BYTES=256*1024

def require(condition,code):
    if not condition:
        raise ValueError("NATIVE_PORTFOLIO_"+code)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),
                      ensure_ascii=True,allow_nan=False).encode("ascii")

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def pin(s):
    return type(s) is str and len(s)==64 and all(c in "0123456789abcdef" for c in s)

def grammar():
    return tuple((linear,gate,bias)
                 for linear in range(64)
                 for gate in GATES
                 for bias in (0,1))

def evaluate_program(input_mask,linear,gate,bias):
    require(type(input_mask) is int and 0<=input_mask<64,"INPUT")
    return ((input_mask&linear).bit_count()&1) ^ int(
        bool(input_mask&32) and (input_mask&gate)==gate) ^ bias

@lru_cache(maxsize=1)
def votes():
    """For each public binary input, bitset of candidate programs yielding 1."""
    out=[0]*64
    for i,(linear,gate,bias) in enumerate(grammar()):
        for m in range(64):
            if evaluate_program(m,linear,gate,bias):
                out[m] |= 1<<i
    return tuple(out)

BANK_SHA256=digest(canonical(grammar()))

class NativeHypothesisPortfolio:
    __slots__=("_slots",)
    def __init__(self,slots=None):
        self._slots={} if slots is None else slots

    def _state(self,slot):
        require(type(slot) is int and 0<=slot<128,"SLOT")
        return self._slots.get(slot,(ALL_CANDIDATES,0,0,0))

    def observe(self,slot,input_mask,outcome,source_digest):
        """One witnessed source-free effect, no original source action."""
        state,seen,ones,n=self._state(slot)
        require(type(input_mask) is int and 0<=input_mask<64,"INPUT")
        require(type(outcome) is int and outcome in (0,1),"OUTCOME")
        require(pin(source_digest) and source_digest==digest(canonical(
            [slot,input_mask,outcome,SOURCE_MODE])),"FIXTURE_DIGEST")
        bit=1<<input_mask
        require(not(seen&bit),"DUPLICATE_WITNESS")
        selected=votes()[input_mask]
        next_state=state & (selected if outcome else (ALL_CANDIDATES^selected))
        updated=dict(self._slots)
        updated[slot]=(next_state,seen|bit,ones|(bit if outcome else 0),n+1)
        return NativeHypothesisPortfolio(updated)

    def count(self,slot):
        return self._state(slot)[0].bit_count()

    def predict(self,slot,input_mask):
        state,_,_,_=self._state(slot)
        require(type(input_mask) is int and 0<=input_mask<64,"INPUT")
        if not state:
            return None
        positive=state&votes()[input_mask]
        if positive==0:
            return 0
        if positive==state:
            return 1
        return None

    def vector(self,slot):
        return tuple(self.predict(slot,m) for m in range(64))

    def details(self,slot):
        bits,seen,ones,n=self._state(slot)
        return {"hypotheses":bits.bit_count(),"observations":n,
                "seen":seen.bit_count(),"contradictions":int(bits==0),
                "provisional":True,"accepted_native":False}

    def checkpoint(self):
        entries=[{"slot":slot,"live_hex":format(t[0],"x"),
                  "seen_hex":format(t[1],"x"),
                  "ones_hex":format(t[2],"x"),"observations":t[3]}
                 for slot,t in sorted(self._slots.items())]
        raw=canonical({"schema":SCHEMA,"grammar_sha256":BANK_SHA256,
                       "source_mode":SOURCE_MODE,"accepted_native":False,
                       "scientific_pass":False,"entries":entries})
        require(len(raw)<=MAX_BYTES,"CHECKPOINT_CAPACITY")
        return raw

    @classmethod
    def restore(cls,raw,expected_sha256):
        require(type(raw) is bytes and 0<len(raw)<=MAX_BYTES
                and pin(expected_sha256) and digest(raw)==expected_sha256,
                "CHECKPOINT_SHA")
        def unique(pairs):
            out={}
            for k,v in pairs:
                require(k not in out,"DUPLICATE_JSON_KEY")
                out[k]=v
            return out
        try:
            document=json.loads(raw.decode("ascii"),object_pairs_hook=unique)
            require(type(document) is dict and
                    set(document)=={"schema","grammar_sha256","source_mode",
                                    "accepted_native","scientific_pass","entries"}
                    and document["schema"]==SCHEMA
                    and document["grammar_sha256"]==BANK_SHA256
                    and document["source_mode"]==SOURCE_MODE
                    and document["accepted_native"] is False
                    and document["scientific_pass"] is False
                    and type(document["entries"]) is list
                    and len(document["entries"])<=128,"CONTRACT")
            slots={}
            for e in document["entries"]:
                require(type(e) is dict and
                    set(e)=={"slot","live_hex","seen_hex","ones_hex","observations"}
                    and type(e["slot"]) is int and 0<=e["slot"]<128
                    and e["slot"] not in slots,"ENTRY")
                for k in ("live_hex","seen_hex","ones_hex"):
                    require(type(e[k]) is str and len(e[k])>0 and
                            len(e[k])<=512 and all(c in "0123456789abcdef" for c in e[k]),
                            "HEX")
                state=int(e["live_hex"],16)
                seen=int(e["seen_hex"],16)
                ones=int(e["ones_hex"],16)
                n=e["observations"]
                require(type(n) is int and 1<=n<=64
                        and seen.bit_count()==n and 0<=ones<=seen
                        and not (ones&~seen)
                        and (state&~ALL_CANDIDATES)==0
                        and seen.bit_length()<=64,"ENTRY_COUNTS")
                expected=ALL_CANDIDATES
                for mask in range(64):
                    if seen&(1<<mask):
                        selected=votes()[mask]
                        expected &= selected if ones&(1<<mask) else (ALL_CANDIDATES^selected)
                require(state==expected,"FALSE_CANDIDATE_WEIGHTS")
                slots[e["slot"]]=(state,seen,ones,n)
            model=cls(slots)
            require(model.checkpoint()==raw,"COLD_BYTES")
            return model
        except (TypeError,ValueError,KeyError,UnicodeError,AttributeError) as ex:
            raise ValueError("NATIVE_PORTFOLIO_COLD_REJECTED") from ex
