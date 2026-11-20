"""KNOW34 source-only local contradiction-gated cell memory experiment.

Frozen preregistration aa46a0482da74213089506e51d3a2c40615e7656
was committed before this source, tests, and any held outcomes.
Never call proof() from unit tests; use an injected mock witness instead.
No native checkpoints, owner model, protected #426 source, or new controller.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

from know33_local_metaplastic_dev import (
    Beta, Cells, canonical, cold as old_cold, digest,
)

SCHEMA = "yggdrasil.know34.local-contradiction-memory-result.dev.v1"
PROTO = "yggdrasil.know34.contradiction-gated-cell-memory-prereg.v1"
PROTO_BLOB = "79c1c9376567de777f2cb0aad9874a8547fbb961"
PREREG = "aa46a0482da74213089506e51d3a2c40615e7656"
SEEDS = (
    19403,19411,19417,19421,19427,19433,19441,19447,
    19457,19463,19469,19471,19501,19507,19511,19519,
    19531,19541,19543,19553,19559,19571,19577,19583,
)
ARMS = ("local","rewired","old_local","hmm","rolling","single")
MODE = "fresh_synthetic_local_cell_regimes_not_original"
N = 192
PREFIX = 64
B_END = 128
WINDOW = 6
HIGH = 6.0
LOW = 1.0


def require(test, label):
    if not test:
        raise ValueError("YGG_KNOW34_" + label)


def protocol():
    raw = Path(__file__).with_name("know34_local_contradiction_protocol.json").read_bytes()
    blob = hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()
    require(blob == PROTO_BLOB, "PROTOCOL_BLOB")
    p = json.loads(raw)
    s = p["source"]
    b = p["budgets"]
    require(p["schema"] == PROTO and s["seeds"] == list(SEEDS)
            and s["kind"] == MODE and b["paired_worlds"] == 24
            and b["unique_source_events_total"] == 7680
            and b["per_method_model_event_occurrences"] == 9216
            and p["candidate"]["cell_count"] == 8
            and p["candidate"]["local_gate"].find(">=6.0") >= 0
            and p["authority"]["protected_original_world_first_use"] is False
            and p["authority"]["native_model_changed"] is False,
            "PREREG_DRIFT")
    return p


def public_tape(t):
    require(type(t) is int and 0 <= t < N, "PUBLIC_TAPE")
    c, a = t % 8, (t // 8) % 2
    return c, a, c ^ (a << 1)


def private_law_bit(law, x):
    require(law in ("A","B1","B2") and type(x) is int and 0 <= x < 8,
            "LAW")
    x0,x1,x2 = (x & 1), (x >> 1) & 1, (x >> 2) & 1
    if law == "A":
        return x0 ^ (x1 & x2)
    if law == "B1":
        return x0 ^ x2 ^ (x1 & x2)
    return (x0 & x1) ^ (1-x2)


def family(seed):
    require(type(seed) is int and seed in SEEDS, "SEED")
    return "B1" if SEEDS.index(seed) < 12 else "B2"


def private_witness(seed, t, branch, *, source_mode=MODE):
    """Evaluator only. Callers must pass the public action to cell observers."""
    require(source_mode == MODE and type(seed) is int and seed in SEEDS
            and type(t) is int and 0 <= t < N
            and branch in ("control_A","treatment_B"), "PRIVATE_SOURCE")
    _c, _a, x = public_tape(t)
    law = family(seed) if branch == "treatment_B" and PREFIX <= t < B_END else "A"
    q = .85 if private_law_bit(law,x) else .15
    raw = hashlib.sha256(f"know34:private:coin:v1:{seed}:{t}".encode("ascii")).digest()
    return int(int.from_bytes(raw[:8], "big") / (1 << 64) < q)


class GuardedCells:
    """Eight local slow Beta heads + six-event ring per cell + four support gates.

    Only own and one neighboring cell's local evidence enter each gate.
    The six-witness slow-head consolidation is a declared startup assumption.
    No hidden phase, seed, source law or global phase controller enters updates.
    """
    def __init__(self, kind):
        require(kind in ("local","rewired"), "KIND")
        self.kind = kind
        self.slow = [Beta() for _ in range(8)]
        self.windows = [[] for _ in range(8)]
        self.n = [0 for _ in range(8)]
        self.received = 0
        self.mode = ["slow"] * 4
        self.fast_switches = 0
        self.slow_returns = 0
        self.messages = 0

    def pair(self, x):
        require(type(x) is int and 0 <= x < 8, "PAIR")
        return x//2 if self.kind=="local" else x%4

    def partners(self, g):
        require(type(g) is int and 0 <= g < 4, "GROUP")
        if self.kind == "local":
            return (g*2,g*2+1)
        return (g,g+4)

    def log_bayes_factor(self, x):
        window = self.windows[x]
        n,k = len(window),sum(window)
        if n == 0:
            return 0.0
        p = max(.05,min(.95,self.slow[x].prob()))
        log_alt = (math.lgamma(1+k)+math.lgamma(1+n-k)
                   -math.lgamma(n+2))
        log_stable = k*math.log(p)+(n-k)*math.log(1-p)
        return log_alt-log_stable

    def prob(self, x):
        require(type(x) is int and 0 <= x < 8, "READOUT")
        if self.mode[self.pair(x)] == "slow":
            return self.slow[x].prob()
        h = self.windows[x]
        return (1+sum(h))/(2+len(h))

    def observe(self, t, x, y, *, source_mode=MODE):
        require(source_mode == MODE and type(t) is int and t == self.received
                and t < N and type(x) is int and 0 <= x < 8
                and type(y) is int and y in (0,1), "EVENT")
        prev = self.n[x]
        if prev < WINDOW:
            self.slow[x].update(y,1.0)
        h = self.windows[x]
        h.append(y)
        if len(h)>WINDOW:
            h.pop(0)
        self.n[x]+=1
        self.received+=1
        g = self.pair(x)
        a,b=self.partners(g)
        # Both cells must have consolidated their initial slow state first.
        if self.n[a]>=WINDOW and self.n[b]>=WINDOW:
            strength=self.log_bayes_factor(a)+self.log_bayes_factor(b)
            self.messages+=2
            if self.mode[g]=="slow" and strength>=HIGH:
                self.mode[g]="fast"
                self.fast_switches+=1
            elif self.mode[g]=="fast" and strength<=LOW:
                self.mode[g]="slow"
                self.slow_returns+=1

    def slow_sha(self):
        return digest(canonical([cell.state() for cell in self.slow]))

    def state(self):
        return {
            "schema":"yggdrasil.know34.cell-state.v1",
            "kind":self.kind,
            "slow":[z.state() for z in self.slow],
            "windows":self.windows,
            "n":self.n,
            "received":self.received,
            "mode":self.mode,
            "fast_switches":self.fast_switches,
            "slow_returns":self.slow_returns,
            "messages":self.messages,
            "original_source":False,
        }

    def checkpoint(self):
        raw=canonical(self.state())
        require(len(raw)<8192,"CHECKPOINT_BYTES")
        return raw

    @classmethod
    def restore(cls, raw, expected_sha):
        require(type(raw) is bytes and len(raw)<8192 and
                digest(raw)==expected_sha,"CHECKSUM")
        try:
            def no_duplicates(pairs):
                ans={}
                for k,v in pairs:
                    require(k not in ans,"DUPLICATE_KEY")
                    ans[k]=v
                return ans
            d=json.loads(raw.decode("ascii"),object_pairs_hook=no_duplicates)
            restored=cls(d["kind"])
            require(set(d)==set(restored.state())
                    and d["schema"]=="yggdrasil.know34.cell-state.v1"
                    and d["original_source"] is False
                    and type(d["received"]) is int and 0<=d["received"]<=N
                    and len(d["slow"])==len(d["windows"])==len(d["n"])==8
                    and len(d["mode"])==4
                    and all(type(z) is int and 0<=z<=N for z in d["n"])
                    and sum(d["n"])==d["received"]
                    and all(type(z) is list and
                            len(z)<=min(WINDOW,d["n"][i]) and
                            all(type(v) is int and v in (0,1) for v in z)
                            for i,z in enumerate(d["windows"]))
                    and all(v in ("slow","fast") for v in d["mode"])
                    and all(type(d[key]) is int and 0<=d[key]<=2*N for key in
                            ("fast_switches","slow_returns","messages")),
                    "STATE_CONTRACT")
            restored.slow=[Beta(*row) for row in d["slow"]]
            restored.windows=d["windows"]
            restored.n=d["n"]
            restored.received=d["received"]
            restored.mode=d["mode"]
            restored.fast_switches=d["fast_switches"]
            restored.slow_returns=d["slow_returns"]
            restored.messages=d["messages"]
            require(restored.checkpoint()==raw,"NON_CANONICAL")
            return restored
        except (KeyError,ValueError,TypeError,OverflowError,UnicodeError) as exc:
            raise ValueError("YGG_KNOW34_COLD_REJECT") from exc


def new_models():
    return {
        "local":GuardedCells("local"),
        "rewired":GuardedCells("rewired"),
        "old_local":Cells("candidate"),
        "hmm":Cells("hmm"),
        "rolling":Cells("rolling"),
        "single":Cells("single"),
    }


def cold(m):
    if isinstance(m,GuardedCells):
        raw=m.checkpoint()
        restored=GuardedCells.restore(raw,digest(raw))
    else:
        restored=old_cold(m)
        raw=m.checkpoint()
    require(restored.checkpoint()==raw
            and [restored.prob(x) for x in range(8)] ==
            [m.prob(x) for x in range(8)],"COLD_READBACK")
    return restored


def score(model, law="A"):
    """Evaluator-only expected Brier on exactly 16 public (c,a) pairs."""
    return sum(
        (lambda q,p:q*(1-q)+(p-q)**2)(
            .85 if private_law_bit(law,c^(a<<1)) else .15,
            model.prob(c^(a<<1)))
        for c in range(8) for a in range(2)
    )/16


def public_prefix(seed, witness):
    models=new_models()
    count=0
    for t in range(PREFIX):
        _c,_a,x=public_tape(t)
        y=witness(seed,t,"control_A")
        require(type(y) is int and y in (0,1),"WITNESS_TYPE")
        count+=1
        for m in models.values():
            m.observe(t,x,y)
    require(count==PREFIX and
            all(m.received==PREFIX for m in models.values()),
            "PREFIX_BUDGET")
    return models,count


def paired_world(seed,witness=private_witness):
    """Main scorer consumes HELD only with private_witness; tests must inject."""
    require(type(seed) is int and seed in SEEDS,"WORLD_ID")
    prefix,count=public_prefix(seed,witness)
    old_A=prefix["local"].slow_sha()
    t64={name:score(model,"A") for name,model in prefix.items()}
    branches={}
    for branch in ("control_A","treatment_B"):
        models={name:cold(m) for name,m in prefix.items()}
        bstage={name:[] for name in ARMS}
        returns={name:{} for name in ARMS}
        t128=None
        for t in range(PREFIX,N):
            if t==B_END:
                t128={
                    "slow_A_sha":models["local"].slow_sha(),
                    "A_scores":{name:score(m) for name,m in models.items()}
                }
                models={name:cold(m) for name,m in models.items()}
            _c,_a,x=public_tape(t)
            if PREFIX<=t<B_END and branch=="treatment_B":
                for name,m in models.items():
                    bstage[name].append(score(m,family(seed)))
            y=witness(seed,t,branch)
            require(type(y) is int and y in (0,1),"WITNESS_TYPE")
            count+=1
            for m in models.values():
                m.observe(t,x,y)
            k=t+1-B_END
            if k in (16,32,48,64):
                for name,m in models.items():
                    returns[name][str(k)]=score(m,"A")
        require(t128 is not None and
                all(set(v)=={"16","32","48","64"} for v in returns.values()),
                "READOUT_COUNT")
        for m in models.values():
            require(m.received==N,"MODEL_OBSERVATIONS")
            cold(m)
        branches[branch]={
            "t128":t128,
            "return_A":returns,
            "B_prequential":(
                {name:sum(x)/len(x) for name,x in bstage.items()}
                if branch=="treatment_B" else None
            ),
            "sham_fast_events":models["local"].fast_switches,
            "sham_rewired_fast_events":models["rewired"].fast_switches,
            "sham_local_messages":models["local"].messages,
            "state_bytes":{name:len(m.checkpoint()) for name,m in models.items()},
        }
    require(count==320,"SOURCE_EVENTS")
    return {
        "seed":seed,"family":family(seed),"source_calls":count,
        "t64_A":t64,"t64_slow_A_hash":old_A,
        "treatment_slow_A_unchanged":branches["treatment_B"]["t128"]["slow_A_sha"]==old_A,
        "branches":branches,
    }


def proof():
    start=time.monotonic()
    protocol()
    for begin in range(0,N,16):
        pairs=[public_tape(t) for t in range(begin,begin+16)]
        require(len({(c,a) for c,a,_x in pairs})==16
                and all(sum(x==i for _,_,x in pairs)==2 for i in range(8)),
                "FULL_PUBLIC_SUPPORT")
    worlds=[paired_world(seed) for seed in SEEDS]
    require(len(worlds)==24 and sum(w["source_calls"] for w in worlds)==7680,
            "PROSPECTIVE_FIRST_USE_BUDGET")
    families={}
    for law in ("B1","B2"):
        rows=[w for w in worlds if w["family"]==law]
        require(len(rows)==12,"COHORT")
        means={}
        for name in ARMS:
            means[name]={
                "A_prefix":sum(w["t64_A"][name] for w in rows)/12,
                "B_prequential":sum(
                    w["branches"]["treatment_B"]["B_prequential"][name]
                    for w in rows)/12,
                "return":{
                    str(k):sum(w["branches"]["treatment_B"]["return_A"][name][str(k)]
                               for w in rows)/12
                    for k in (16,32,48,64)
                },
                "mean_final_state_bytes":sum(
                    w["branches"]["treatment_B"]["state_bytes"][name]
                    for w in rows)/12,
            }
        wins={
            ctrl:sum(
                w["branches"]["treatment_B"]["return_A"]["local"]["48"] <
                w["branches"]["treatment_B"]["return_A"][ctrl]["48"]
                for w in rows)
            for ctrl in ("rewired","hmm")
        }
        families[law]={"means":means,"k48_paired_wins":wins}
    retained=sum(w["treatment_slow_A_unchanged"] for w in worlds)
    sham_false=sum(w["branches"]["control_A"]["sham_fast_events"]>0
                   for w in worlds)
    h={
        "P0_public_support":len(worlds)==24,
        "P1_early_A_learned":all(
            families[f]["means"]["local"]["A_prefix"]<=.21
            for f in ("B1","B2")),
        "H1_return_k32_k48_beats_HMM_and_rewired":(
            all(
                families[f]["means"]["local"]["return"][str(k)] <=
                families[f]["means"][ctrl]["return"][str(k)]-.005
                for f in ("B1","B2") for k in (32,48)
                for ctrl in ("hmm","rewired")
            ) and all(
                families[f]["k48_paired_wins"][ctrl]>=9
                for f in ("B1","B2") for ctrl in ("hmm","rewired")
            )
        ),
        "H2_live_slow_A_state_24_of_24":retained==24,
        "H3_B_stage_nondegradation_vs_HMM":all(
            families[f]["means"]["local"]["B_prequential"] <=
            families[f]["means"]["hmm"]["B_prequential"]+.005
            for f in ("B1","B2")),
        "H4_sham_false_switch_at_most_2":sham_false<=2,
    }
    return {
        "schema":SCHEMA,"prereg_commit":PREREG,"prereg_blob":PROTO_BLOB,
        "mode":MODE,"held_world_pairs":24,"unique_source_events":7680,
        "model_event_occurrences_per_arm":9216,
        "frozen_hypotheses":h,"families":families,
        "live_slow_A_preserved":retained,
        "sham_false_switch_worlds":sham_false,"worlds":worlds,
        "development_verdict":(
            "SOURCE_ONLY_DEV_SUPPORTED" if all(h.values())
            else "SOURCE_ONLY_DEV_NO_GO_OR_MIXED"
        ),
        "scientific":"SCIENCE_NO_GO_SYNTHETIC_NOT_NATIVE",
        "protected_original_world_first_use":False,
        "accepted_model_changed":False,"deployment":"NONE",
        "script_seconds":round(time.monotonic()-start,6),
    }


if __name__=="__main__":
    print(json.dumps(proof(),sort_keys=True))
