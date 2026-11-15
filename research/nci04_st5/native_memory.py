"""ST5 independent bounded native eight-cell causal-law recall substrate.

All learned knowledge arrives from actual PUBLIC five-step consequences;
not source law IDs, private delayed masks, actor seed/trial, or a donor
model. Fixed architectural prior: shifts 1/2/3 and one-step intervention
residual XOR. Report as task-aligned prior, not discovered physics.

Each of 16 banks stores [observed public rotation, observed action0 mask,
observed action1 mask], 8 independent integer Bernoulli counters for the
delayed action2 residual, and bounded deterministic freshness metadata.
At a novel cue the model abstains with P=.5, not an invented law guess.
"""
import json

SCHEMA="yggdrasil.nci04.st5.native-cue-retention.v1"
N=8
SLOTS=16
COUNT_MAX=255
CLOCK_MAX=100000000
ACTOR=(3,0,1,2,3)
VARIANTS=("causal","no_cue","erase","sham_key")


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)


def validate_bits(data):
    if (type(data) not in (list,tuple) or len(data)!=N or
        any(type(k) is not int or k not in (0,1) for k in data)):
        raise ValueError("ST5_NATIVE_INVALID_PUBLIC_BITS")


def validate_action(action):
    if type(action) is not int or action not in (0,1,2,3):
        raise ValueError("ST5_NATIVE_INVALID_ACTION")


def pack(bits):
    validate_bits(bits)
    return sum(x<<i for i,x in enumerate(bits))


def rot(value,r):
    if (type(value) is not int or value not in range(256) or
        type(r) is not int or r not in (1,2,3)):
        raise ValueError("ST5_NATIVE_INVALID_ROTATION")
    return ((value<<r)|(value>>(8-r)))&255


def observed_rotation(before,after):
    x=pack(before);y=pack(after)
    candidates=[r for r in (1,2,3) if rot(x,r)==y]
    return candidates[0] if len(candidates)==1 else None


def signature_ok(v):
    return (type(v) in (list,tuple) and len(v)==3 and
            type(v[0]) is int and v[0] in (1,2,3) and
            all(type(x) is int and x in range(256) for x in v[1:]))


def fresh_bank(signature,clock):
    if not signature_ok(signature):
        raise ValueError("ST5_NATIVE_UNKNOWN_SIGNATURE")
    return {"key":list(signature),
            "counts":[[0,0] for _ in range(N)],
            "last":clock,"observations":0}


def update_count(pair,is_one):
    if type(is_one) is not int or is_one not in (0,1):
        raise ValueError("ST5_NATIVE_BAD_LEARNED_BIT")
    if COUNT_MAX in pair:
        pair[0]//=2
        pair[1]//=2
    pair[0 if is_one else 1]+=1


def probability(pair):
    return (pair[0]+1)/(pair[0]+pair[1]+2)


class NativeCausalRecall8:
    def __init__(self,variant="causal"):
        if variant not in VARIANTS:
            raise ValueError("ST5_NATIVE_BAD_VARIANT")
        self.variant=variant
        self.banks=[None]*SLOTS
        self.rotation=None
        self.mask0=None
        self.mask1=None
        self.prior_action=None
        self.last_change=[0]*N
        self.step=0
        self.learned_probes=0
        self.clock=0
        self.forks=0
        self.retrievals=0
        self.misses=0
        self.ambiguous=0

    def reset_episode(self):
        if self.variant=="erase":
            self.banks=[None]*SLOTS
        self.rotation=None
        self.mask0=None
        self.mask1=None
        self.prior_action=None
        self.last_change=[0]*N
        self.step=0

    def cue(self):
        if (self.rotation is None or self.mask0 is None or
            self.mask1 is None):
            return None
        return (self.rotation,self.mask0,self.mask1)

    def _find(self,cue):
        if cue is None:
            return None
        if self.variant=="no_cue":
            populated=[(i,b) for i,b in enumerate(self.banks)
                       if b is not None]
            if not populated:
                return None
            return min(populated,key=lambda e:(-e[1]["last"],e[0]))[0]
        matches=[i for i,b in enumerate(self.banks)
                 if b is not None and tuple(b["key"])==cue]
        if len(matches)>1:
            raise ValueError("ST5_NATIVE_AMBIGUOUS_DUPLICATE_CUE")
        return matches[0] if matches else None

    def _reserve(self,cue):
        if not signature_ok(cue):
            raise ValueError("ST5_NATIVE_CANNOT_LEARN_UNIDENTIFIED_LAW")
        if self.variant=="sham_key":
            cue=(cue[0],cue[1]^0xA5,cue[2])
        matches=[i for i,b in enumerate(self.banks)
                 if b is not None and tuple(b["key"])==cue]
        if len(matches)>1:
            raise ValueError("ST5_NATIVE_DUPLICATE_PROFILE_CORRUPTION")
        if matches:
            return matches[0]
        try:
            index=self.banks.index(None)
        except ValueError:
            index=min(range(SLOTS),key=lambda j:(
                self.banks[j]["last"],j
            ))
        self.banks[index]=fresh_bank(cue,self.clock)
        self.forks+=1
        return index

    def predict(self,public,action):
        validate_bits(public);validate_action(action)
        if self.step>=len(ACTOR) or action!=ACTOR[self.step]:
            raise ValueError("ST5_NATIVE_ACTOR_STEP_DRIFT")
        if self.step!=4:
            return [.5]*N
        cue=self.cue()
        i=self._find(cue)
        if i is None or self.rotation is None:
            return [.5]*N
        bank=self.banks[i]
        x=pack(public)
        rotated=rot(x,self.rotation)
        return [
            probability(bank["counts"][k]) if
            (((x>>k)&1)^((rotated>>k)&1))==0 else
            1.-probability(bank["counts"][k])
            for k in range(N)
        ]

    def observe(self,public,action,target,after,*,train=True):
        validate_bits(public);validate_bits(target);validate_bits(after)
        validate_action(action)
        if (type(train) is not bool or self.step>=len(ACTOR) or
            action!=ACTOR[self.step] or
            [a^b for a,b in zip(public,after)]!=list(target)):
            raise ValueError("ST5_NATIVE_UNAUTHENTIC_TRANSITION")
        predicted=self.predict(public,action)
        r=self.rotation
        if self.step==0:
            r=observed_rotation(public,after)
            if r is None:
                self.ambiguous+=1
            self.rotation=r
        elif self.step==1:
            if r is not None:
                self.mask0=pack(after)^rot(pack(public),r)
        elif self.step==2:
            if r is not None:
                self.mask1=pack(after)^rot(pack(public),r)
        elif self.step==4:
            cue=self.cue()
            if cue is not None and train:
                if self.clock>=CLOCK_MAX:
                    raise ValueError("ST5_NATIVE_LEARNED_CLOCK_OVERFLOW")
                self.clock+=1
                slot=self._reserve(cue)
                bank=self.banks[slot]
                residual=pack(after)^rot(pack(public),r)
                for k in range(N):
                    update_count(bank["counts"][k],(residual>>k)&1)
                bank["observations"]+=1
                bank["last"]=self.clock
                self.learned_probes+=1
            elif cue is None:
                self.misses+=1
            else:
                if self._find(cue) is None:
                    self.misses+=1
                else:
                    self.retrievals+=1
        self.prior_action=action
        self.last_change=list(target)
        self.step+=1
        return predicted

    def snapshot(self):
        return canonical({
            "schema":SCHEMA,"variant":self.variant,
            "banks":self.banks,"rotation":self.rotation,
            "mask0":self.mask0,"mask1":self.mask1,
            "prior_action":self.prior_action,
            "last_change":self.last_change,"step":self.step,
            "learned_probes":self.learned_probes,
            "clock":self.clock,"forks":self.forks,
            "retrievals":self.retrievals,"misses":self.misses,
            "ambiguous":self.ambiguous
        })

    @classmethod
    def restore(cls,payload):
        if type(payload) is not str or len(payload)>80000:
            raise ValueError("ST5_NATIVE_INVALID_CHECKPOINT_SIZE")
        try:
            d=json.loads(payload)
            expected={"schema","variant","banks","rotation","mask0",
                      "mask1","prior_action","last_change","step",
                      "learned_probes","clock","forks","retrievals",
                      "misses","ambiguous"}
            if (type(d) is not dict or set(d)!=expected or
                d["schema"]!=SCHEMA or d["variant"] not in VARIANTS or
                type(d["banks"]) is not list or len(d["banks"])!=SLOTS or
                (d["rotation"] is not None and
                 (type(d["rotation"]) is not int or
                  d["rotation"] not in (1,2,3))) or
                any(d[k] is not None and
                    (type(d[k]) is not int or d[k] not in range(256))
                    for k in ("mask0","mask1")) or
                (d["prior_action"] is not None and
                 (type(d["prior_action"]) is not int or
                  d["prior_action"] not in (0,1,2,3))) or
                any(type(d[k]) is not int or not 0<=d[k]<=CLOCK_MAX
                    for k in ("step","learned_probes","clock","forks",
                              "retrievals","misses","ambiguous")) or
                d["step"]>len(ACTOR)):
                raise ValueError("ST5_NATIVE_INVALID_CHECKPOINT_SHAPE")
            validate_bits(d["last_change"])
            keys=[]
            for bank in d["banks"]:
                if bank is None:
                    continue
                if (type(bank) is not dict or set(bank)!={
                    "key","counts","last","observations"
                } or not signature_ok(bank["key"]) or
                    type(bank["counts"]) is not list or
                    len(bank["counts"])!=N or
                    any(type(pair) is not list or len(pair)!=2 or
                        any(type(z) is not int or z not in range(COUNT_MAX+1)
                            for z in pair)
                        for pair in bank["counts"]) or
                    any(type(bank[k]) is not int or
                        not 0<=bank[k]<=d["clock"]
                        for k in ("last","observations"))):
                    raise ValueError("ST5_NATIVE_INVALID_CAUSAL_BANK")
                keys.append(tuple(bank["key"]))
            if len(keys)!=len(set(keys)):
                raise ValueError("ST5_NATIVE_DUPLICATE_PROFILE_KEY")
            obj=cls(d["variant"])
            for k in expected-{"schema","variant"}:
                setattr(obj,k,d[k])
            if obj.snapshot()!=payload:
                raise ValueError("ST5_NATIVE_NONCANONICAL_CHECKPOINT")
            return obj
        except (TypeError,KeyError,OverflowError) as exc:
            raise ValueError("ST5_NATIVE_COLD_RESTORE_INVALID") from exc

    def accounting(self):
        return {
            "native_binary_cells":N,
            "bounded_profile_slots":SLOTS,
            "learned_uint8_counter_capacity_bytes":SLOTS*N*2,
            "signature_bytes_per_bank":3,
            "extra_trainable_neural_coefficients":0,
            "fixed_structural_prior":"one-step delayed XOR & 3 public rotations",
            "checkpoint_json_bytes":len(self.snapshot().encode("utf-8")),
            "source_law_seed_trial_seen":False,
            "integer_state_only":True,
        }
