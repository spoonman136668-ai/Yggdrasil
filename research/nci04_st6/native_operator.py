"""ST6 tokenless eight-cell native causal OPERATOR hypothesis memory.

No private world or source import. A learner is given only public 8-bit
before, announced action, and after-observed changed bits. It first
derives r, A, B from the three real diagnostic public transitions.
It forecasts the final delayed action consequence BEFORE world.step.
After the genuine source result, update bounded integer mismatch counts
for eight explicitly admitted task-aligned hypothesis operators.

Not a general causal discovery engine; the right operator is deliberately
in the frozen menu. Exact same-menu trained symbolic comparator is a
scientific equivalence control, not an oracle or superiority claim.
"""
import json

SCHEMA="yggdrasil.nci04.st6.native-operation-selector.v1"
ACTOR=(3,0,1,2,3)
N=8
K=8
MAX_COUNT=2**31-1
VARIANTS=("causal","no_b","erase","shuffle")


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)


def check_bits(seq):
    if (type(seq) not in (list,tuple) or len(seq)!=8 or
        any(type(v) is not int or v not in (0,1) for v in seq)):
        raise ValueError("ST6_NATIVE_INVALID_PUBLIC_BITS")


def pack(seq):
    check_bits(seq)
    return sum(v<<i for i,v in enumerate(seq))


def rotate(n,k):
    if type(n) is not int or n not in range(256) or type(k) is not int or k not in (1,2,3,7):
        raise ValueError("ST6_NATIVE_INVALID_PUBLIC_ROTATION")
    return ((n<<k)|(n>>(8-k)))&255


def menu(a,b):
    if type(a) is not int or a not in range(256) or type(b) is not int or b not in range(256):
        raise ValueError("ST6_NATIVE_BAD_DIAGNOSTIC")
    return (a^rotate(b,1),a^b,a|b,a&b,(a+b)&255,
            a^rotate(b,2),a&(~b&255),a^rotate(b,7))


class NativeOperator8:
    def __init__(self,variant="causal"):
        if variant not in VARIANTS:
            raise ValueError("ST6_NATIVE_INVALID_VARIANT")
        self.variant=variant
        self.mismatches=[0]*K
        self.support=[0]*K
        self.r=None;self.a=None;self.b=None
        self.step=0
        self.training_probes=0
        self.retrievals=0
        self.misses=0
        self.ambiguous=0

    def reset_episode(self):
        if self.variant=="erase":
            self.mismatches=[0]*K
            self.support=[0]*K
        self.r=None;self.a=None;self.b=None
        self.step=0

    def _pick(self):
        if not any(self.support):
            return None
        return min(range(K),key=lambda j:(self.mismatches[j],j))

    def predict(self,public,action):
        check_bits(public)
        if type(action) is not int or action not in (0,1,2,3) or self.step>=5 or action!=ACTOR[self.step]:
            raise ValueError("ST6_NATIVE_BAD_PUBLIC_ACTION")
        if self.step!=4 or None in (self.r,self.a,self.b):
            return [.5]*N
        j=self._pick()
        if j is None:
            return [.5]*N
        g=menu(self.a,0 if self.variant=="no_b" else self.b)[j]
        before=pack(public)
        expected=before^rotate(before,self.r)^g
        # Confidence deliberately capped, calibrated from observed public
        # support only. Never peek at the future outcome.
        conf=min(.99,(self.support[j]+1)/(self.support[j]+2))
        return [conf if (expected>>k)&1 else 1.-conf for k in range(N)]

    def observe(self,public,action,target,after,*,train=True):
        check_bits(public);check_bits(target);check_bits(after)
        if (type(train) is not bool or self.step>=5 or
            type(action) is not int or action!=ACTOR[self.step] or
            [x^y for x,y in zip(public,after)]!=list(target)):
            raise ValueError("ST6_NATIVE_UNAUTHENTIC_ACTION_RESULT")
        pred=self.predict(public,action)
        x=pack(public);y=pack(after)
        if self.step==0:
            candidates=[r for r in (1,2,3) if rotate(x,r)==y]
            self.r=candidates[0] if len(candidates)==1 else None
            self.ambiguous+=int(self.r is None)
        elif self.step==1 and self.r is not None:
            self.a=y^rotate(x,self.r)
        elif self.step==2 and self.r is not None:
            self.b=y^rotate(x,self.r)
        elif self.step==4:
            if None in (self.r,self.a,self.b):
                self.misses+=1
            elif train:
                if any(z>MAX_COUNT-8 for z in self.support):
                    # Deterministic bounded renormalization of all models.
                    self.support=[z//2 for z in self.support]
                    self.mismatches=[z//2 for z in self.mismatches]
                real_g=y^rotate(x,self.r)
                a,b=(self.b,self.a) if self.variant=="shuffle" else (
                    self.a,0 if self.variant=="no_b" else self.b
                )
                guesses=menu(a,b)
                for j,guess in enumerate(guesses):
                    self.mismatches[j]+=(real_g^guess).bit_count()
                    self.support[j]+=8
                self.training_probes+=1
            else:
                self.retrievals+=int(self._pick() is not None)
        self.step+=1
        return pred

    def snapshot(self):
        return canonical({
            "schema":SCHEMA,"variant":self.variant,
            "mismatches":self.mismatches,"support":self.support,
            "r":self.r,"a":self.a,"b":self.b,"step":self.step,
            "training_probes":self.training_probes,
            "retrievals":self.retrievals,"misses":self.misses,
            "ambiguous":self.ambiguous
        })

    @classmethod
    def restore(cls,payload):
        if type(payload) is not str or len(payload)>3500:
            raise ValueError("ST6_NATIVE_CHECKPOINT_TOO_LARGE")
        try:
            x=json.loads(payload)
            keys={"schema","variant","mismatches","support","r","a",
                  "b","step","training_probes","retrievals","misses",
                  "ambiguous"}
            if (type(x) is not dict or set(x)!=keys or
                x["schema"]!=SCHEMA or x["variant"] not in VARIANTS or
                any(type(x[k]) is not list or len(x[k])!=8 or
                    any(type(v) is not int or not 0<=v<=MAX_COUNT for v in x[k])
                    for k in ("mismatches","support")) or
                (x["r"] is not None and
                 (type(x["r"]) is not int or x["r"] not in (1,2,3))) or
                any(x[k] is not None and
                    (type(x[k]) is not int or x[k] not in range(256))
                    for k in ("a","b")) or
                any(type(x[k]) is not int or not 0<=x[k]<=MAX_COUNT
                    for k in ("step","training_probes","retrievals","misses",
                              "ambiguous")) or x["step"]>5 or
                any(err>supp for err,supp in zip(
                    x["mismatches"],x["support"]))
                ):
                raise ValueError("ST6_NATIVE_INVALID_CHECKPOINT")
            obj=cls(x["variant"])
            for k in keys-{"schema","variant"}:
                setattr(obj,k,x[k])
            if obj.snapshot()!=payload:
                raise ValueError("ST6_NATIVE_NONCANONICAL_COLD_STATE")
            return obj
        except (TypeError,KeyError,OverflowError) as e:
            raise ValueError("ST6_NATIVE_RESTORE_FAILED") from e

    def accounting(self):
        return {
            "native_binary_cells":N,
            "number_hypotheses":K,
            "learned_uint32_error_support_bytes":K*2*4,
            "fixed_task_aligned_operator_menu":8,
            "checkpoint_json_bytes":len(self.snapshot().encode("utf-8")),
            "private_source_or_law_access":False,
            "integer_only_cold_state":True
        }
