"""Source-blind, direct int32 causal factor programming for WSP123.

NO import of source.py. The row/column XOR prior is supplied; it does not
invent the XOR primitive or give unique capability over optimized symbolic.
"""
from __future__ import annotations
from array import array
from hashlib import sha256
import json

SCHEMA = "wsp123.numeric-causal-factor-weights.v1"
FIT = frozenset(range(123900,123904))


def _canon(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"))


def _sha(v):
    return sha256(_canon(v).encode()).hexdigest()


def _row_ok(row):
    return (type(row) is list and len(row) == 7
            and type(row[0]) is int and row[0] in FIT
            and type(row[1]) is int and row[1] == row[0]-123900
            and type(row[2]) is int and row[2] >= 0
            and all(type(x) is int and 0 <= x < 8 for x in row[3:6])
            and type(row[6]) is str and len(row[6]) == 64
            and all(c in "0123456789abcdef" for c in row[6]))


class NumericCausalBank:
    def __init__(self):
        self.events: list[list] = []
        self._seen = set()
        self.weights = {d: array("i", [-1] * 16) for d in range(4)}

    def _rebuild(self):
        groups = {d: {} for d in range(4)}
        for row in self.events:
            if not _row_ok(row):
                raise ValueError("WSP123_COLD_EVENT_FORMAT")
            seed, d, subject, a, b, effect, _ = row
            if (seed, subject) in self._seen and (d,a,b) not in groups[d]:
                # A separate duplicate verification precedes rebuilding.
                pass
            previous = groups[d].get((a,b))
            if previous is not None and previous != effect:
                raise ValueError("WSP123_CAUSAL_CONTRADICTION")
            groups[d][a,b] = effect
        new_weights = {}
        for domain, answers in groups.items():
            bank = array("i",[-1]*16)
            if (0,0) in answers:
                base = answers[0,0]
                for a in range(8):
                    if (a,0) in answers:
                        bank[a] = answers[a,0] ^ base
                for b in range(8):
                    if (0,b) in answers:
                        bank[8+b] = answers[0,b]
                for (a,b),value in answers.items():
                    if bank[a] != -1 and bank[8+b] != -1:
                        if (bank[a] ^ bank[8+b]) != value:
                            raise ValueError("WSP123_CAUSAL_CONTRADICTION")
            new_weights[domain] = bank
        self.weights = new_weights

    def observe(self, view, evidence):
        if (getattr(view,"domain",None) not in range(4)
                or getattr(view,"seed",None) not in FIT
                or getattr(evidence,"seed",None) != view.seed
                or getattr(evidence,"domain",None) != view.domain
                or type(getattr(evidence,"subject",None)) is not int
                or evidence.subject not in view.legal
                or (getattr(evidence,"left",None),getattr(evidence,"right",None))
                   != view.pair(evidence.subject)
                or type(getattr(evidence,"effect",None)) is not int
                or not 0 <= evidence.effect < 8
                or type(getattr(evidence,"source_sha256",None)) is not str):
            raise ValueError("WSP123_UNVERIFIED_OR_UNAUTHORIZED_OBSERVATION")
        row=[evidence.seed,evidence.domain,evidence.subject,
             evidence.left,evidence.right,evidence.effect,evidence.source_sha256]
        if not _row_ok(row):
            raise ValueError("WSP123_BAD_OBSERVATION_RECEIPT")
        key=(row[0],row[2])
        if key in self._seen:
            raise ValueError("WSP123_DUPLICATE_OBSERVATION")
        if any(old[1]==row[1] and old[3:5]==row[3:5] and old[5]!=row[5]
               for old in self.events):
            raise ValueError("WSP123_CAUSAL_CONTRADICTION")
        self.events.append(row)
        self._seen.add(key)
        try:
            self._rebuild()
        except Exception:
            self.events.pop()
            self._seen.remove(key)
            self._rebuild()
            raise

    def choose(self, view, available):
        if view.seed not in FIT:
            raise PermissionError("WSP123_ONLY_FIT_INTERVENTION")
        by_pair = {view.pair(s): s for s in available if s in view.legal}
        sequence = ([(0,b) for b in range(8)] +
                    [(a,0) for a in range(1,8)])
        for a,b in sequence:
            subject=by_pair.get((a,b))
            if subject is not None and (view.seed,subject) not in self._seen:
                return subject
        return None

    def infer_pair(self, domain, left, right):
        if (type(domain) is not int or domain not in range(4)
                or type(left) is not int or not 0 <= left < 8
                or type(right) is not int or not 0 <= right < 8):
            raise ValueError("WSP123_INVALID_PUBLIC_CAUSAL_PAIR")
        w=self.weights[domain]
        if w[left] < 0 or w[8+right] < 0:
            return None
        return w[left] ^ w[8+right]

    def infer(self, view, subject):
        a,b=view.pair(subject)
        return self.infer_pair(view.domain,a,b)

    def snapshot(self):
        body={"schema":SCHEMA,"events":self.events,
              "weights":{str(d):list(w) for d,w in self.weights.items()}}
        return _canon({"payload":body,"sha256":_sha(body)})

    @classmethod
    def restore(cls, contents):
        try:
            outer=json.loads(contents)
            body=outer["payload"]
            if body.get("schema")!=SCHEMA or outer.get("sha256")!=_sha(body):
                raise ValueError("WSP123_COLD_DIGEST_INVALID")
            rows=body["events"]
            if type(rows) is not list:
                raise ValueError("WSP123_COLD_EVENT_FORMAT")
            result=cls()
            for row in rows:
                if not _row_ok(row):
                    raise ValueError("WSP123_COLD_EVENT_FORMAT")
                key=(row[0],row[2])
                if key in result._seen:
                    raise ValueError("WSP123_COLD_DUPLICATE")
                result.events.append(row)
                result._seen.add(key)
            result._rebuild()
            if body["weights"]!={str(d):list(w) for d,w in result.weights.items()}:
                raise ValueError("WSP123_COLD_WEIGHT_PROVENANCE")
            return result
        except (KeyError,TypeError,IndexError,AttributeError) as exc:
            raise ValueError("WSP123_COLD_FORMAT_INVALID") from exc
