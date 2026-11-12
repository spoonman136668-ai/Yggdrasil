"""WSP53 learner-visible negative controls: no hidden source/cohort imports."""
import hashlib
import json

MAX_ACTIONS = 60

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

def state(x, family):
    if family not in ("anchored_effect", "noncommuting_order"):
        raise ValueError("unknown physics family")
    n = 16 if family == "anchored_effect" else 8
    mod = 4 if family == "anchored_effect" else 7
    if type(x) is not tuple or len(x) != n or any(type(v) is not int for v in x):
        raise ValueError("invalid physical state")
    if any(v < 0 or v >= mod for v in x[:8]):
        raise ValueError("invalid location")
    if family == "anchored_effect" and any(v < 0 or v >= 3 for v in x[8:]):
        raise ValueError("invalid orientation")
    return x

def bits(x):
    if type(x) is not str or not 12 <= len(x) <= 18 or set(x) - {"0","1"}:
        raise ValueError("invalid raw acoustic stream")
    return x

def observation(row, family):
    before = state(row.before, family)
    after = state(row.after, family)
    acoustic = bits(row.acoustic_bits)
    if type(row.action_cost) is not int or row.action_cost != 1 or type(row.reset_cost) is not int or row.reset_cost != 0:
        raise ValueError("invalid action accounting")
    return before, acoustic, after

class WholeStreamTable:
    """Exact observed (before, raw binary stream)->after; no composition."""
    def __init__(self, *, family):
        state((0,)*(16 if family == "anchored_effect" else 8), family)
        self.family = family
        self.actions = 0
        self.facts = {}
        self.conflicts = set()

    def observe(self, row):
        before, acoustic, after = observation(row, self.family)
        if self.actions >= MAX_ACTIONS:
            raise ValueError("action budget exceeded")
        key = (before, acoustic)
        if key in self.facts and self.facts[key] != after:
            self.conflicts.add(key)
            self.facts[key] = None
        elif key not in self.facts:
            self.facts[key] = after
        self.actions += 1

    def predict(self, before, acoustic):
        return self.facts.get((state(before, self.family), bits(acoustic)))

    def snapshot(self):
        payload = {
            "schema":"wsp53.whole-stream.v1", "family":self.family, "actions":self.actions,
            "facts":[[list(b),s,None if a is None else list(a)] for (b,s),a in sorted(self.facts.items())],
            "conflicts":[[list(b),s] for b,s in sorted(self.conflicts)],
        }
        raw = canonical(payload)
        if len(raw) > 100000:
            raise OverflowError("snapshot cap exceeded")
        return canonical({"payload":payload,"sha256":hashlib.sha256(raw.encode("ascii")).hexdigest()})

    @classmethod
    def restore(cls, text):
        if type(text) is not str or len(text) > 200000:
            raise ValueError("invalid snapshot")
        try:
            item = json.loads(text)
            if type(item) is not dict or set(item) != {"payload","sha256"}:
                raise ValueError("invalid envelope")
            p = item["payload"]
            if (type(p) is not dict or set(p) != {"schema","family","actions","facts","conflicts"} or
                p["schema"] != "wsp53.whole-stream.v1" or
                hashlib.sha256(canonical(p).encode("ascii")).hexdigest() != item["sha256"]):
                raise ValueError("bad snapshot schema or checksum")
            obj = cls(family=p["family"])
            if type(p["actions"]) is not int or not 0 <= p["actions"] <= MAX_ACTIONS:
                raise ValueError("bad evidence counter")
            if type(p["facts"]) is not list or type(p["conflicts"]) is not list:
                raise ValueError("bad records")
            for entry in p["facts"]:
                if type(entry) is not list or len(entry) != 3:
                    raise ValueError("bad fact")
                b,s,a = entry
                if type(b) is not list or (a is not None and type(a) is not list):
                    raise ValueError("bad state")
                key = (state(tuple(b),obj.family),bits(s))
                if key in obj.facts:
                    raise ValueError("duplicate fact")
                obj.facts[key] = None if a is None else state(tuple(a),obj.family)
            for entry in p["conflicts"]:
                if type(entry) is not list or len(entry) != 2 or type(entry[0]) is not list:
                    raise ValueError("bad conflict")
                b,s = entry
                key = (state(tuple(b),obj.family),bits(s))
                if key not in obj.facts or obj.facts[key] is not None or key in obj.conflicts:
                    raise ValueError("unjustified conflict")
                obj.conflicts.add(key)
            if any(a is None and k not in obj.conflicts for k,a in obj.facts.items()):
                raise ValueError("unmarked conflict")
            obj.actions = p["actions"]
            if len(obj.facts) > obj.actions or obj.snapshot() != text:
                raise ValueError("noncanonical snapshot")
            return obj
        except (KeyError, TypeError, IndexError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid snapshot") from exc

    def capacity_bits(self):
        return 8 * len(self.snapshot().encode("ascii"))

class ErasedControl:
    """Charges observations, retains no evidence, always abstains."""
    def __init__(self, *, family):
        state((0,)*(16 if family == "anchored_effect" else 8),family)
        self.family = family
        self.actions = 0
    def observe(self, row):
        observation(row,self.family)
        if self.actions >= MAX_ACTIONS:
            raise ValueError("action budget exceeded")
        self.actions += 1
    def predict(self,before,acoustic):
        state(before,self.family)
        bits(acoustic)
        return None
    def capacity_bits(self):
        return len(self.family)*8 + 16
