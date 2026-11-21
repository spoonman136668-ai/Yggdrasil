"""KNOW41: source-free causal-identifiability diagnostic and active table control.

No synthetic FIT/HELD sampler, native training, or protected-world interaction.
"""
import hashlib
import json
from pathlib import Path

PROTO_BLOB = "40b54a9fff183a54243c530cff0f7be34785faca"
PROTO_FILE = (Path(__file__).resolve().parents[3] / "roadmap" /
              "YGG_KNOW41_ACTIVE_CAUSAL_IDENTIFIABILITY_PROTOCOL_2026-11-20.json")


def need(value, reason):
    if not value:
        raise ValueError("YGG_KNOW41_" + reason)


def protocol():
    raw = PROTO_FILE.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    need(blob == PROTO_BLOB, "PROTO_DRIFT")
    p = json.loads(raw)
    need(p["schema"] == "yggdrasil.know41.active-identifiability-proposal.v1"
         and p["status"] == "PREREGISTERED_ONLY_NO_HELD_FIRST_USE"
         and p["authority"]["original_world_issue_426"] == "NO_NEW_FIRST_USE",
         "PROTO_POLICY")
    return p


def key(c, a):
    need(type(c) is int and 0 <= c < 8 and type(a) is int and a in (0, 1), "KEY")
    return c + 8 * a


def expected_milli(graph, c, a, theta):
    """Evaluator-only probability, never supplied to learner or used to sample y."""
    key(c, a)
    need(graph in ("CHAIN", "FORK") and type(theta) is int
         and theta in (0, 1), "SCM")
    if a == 0:
        return 350
    c0, c1, c2 = c & 1, (c >> 1) & 1, (c >> 2) & 1
    m1 = c0 ^ theta
    if graph == "CHAIN":
        return 150 + 400 * m1
    return 150 + 200 * (m1 + (c1 ^ c2 ^ theta))


def _no_duplicate(pairs):
    d = {}
    for k, v in pairs:
        need(k not in d, "DUPLICATE")
        d[k] = v
    return d


class ChosenActionTable:
    """Conventional active 16-cell Beta(1,1) table, a CONTROL not the novel candidate."""
    def __init__(self):
        self.n = [0] * 16
        self.s = [0] * 16
        self.received = 0
        self.pending = None

    def prob(self, c, a):
        k = key(c, a)
        return (self.s[k] + 1) / (self.n[k] + 2)

    def choose(self, t, c):
        need(type(t) is int and t == self.received
             and self.pending is None, "CHOOSE")
        key(c, 0)
        visits = self.n[c] + self.n[c + 8]
        a = 1 if visits % 4 == 0 else int(self.prob(c, 1) - 0.05 > self.prob(c, 0))
        self.pending = [t, c, a]
        return a

    def observe(self, t, c, a, y):
        need(type(y) is int and y in (0, 1) and
             self.pending == [t, c, a], "UNWITNESSED_ACTION")
        k = key(c, a)
        self.n[k] += 1
        self.s[k] += y
        self.received += 1
        self.pending = None

    def checkpoint(self):
        return json.dumps({"n": self.n, "s": self.s, "received": self.received,
                           "pending": self.pending}, sort_keys=True, separators=(",", ":"))

    @classmethod
    def cold(cls, raw):
        need(type(raw) is str and len(raw) < 4096, "CHECKPOINT_SIZE")
        d = json.loads(raw, object_pairs_hook=_no_duplicate)
        need(type(d) is dict and set(d) == {"n", "s", "received", "pending"}
             and d["pending"] is None and type(d["received"]) is int
             and 0 <= d["received"] <= 256 and
             all(type(d[k]) is list and len(d[k]) == 16 for k in ("n", "s")),
             "CHECKPOINT_SHAPE")
        need(all(type(n) is int and type(s) is int and 0 <= s <= n <= 256
                 for n, s in zip(d["n"], d["s"])) and
             sum(d["n"]) == d["received"], "CHECKPOINT_DATA")
        out = cls()
        out.n, out.s, out.received = d["n"], d["s"], d["received"]
        need(out.checkpoint() == raw, "CHECKPOINT_NONCANONICAL")
        return out
