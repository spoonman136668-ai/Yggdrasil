"""KNOW33: source-only eight-cell metaplastic memory and local support comparison.

Pre-registered BEFORE this source and before any held observations:
a2faced60dfcd7b13de5e3ae41f4c16623ea4127.
Research contributor; not the native DG-1 substrate, original first use, or owner model.
Never run proof() from focused tests.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
import time
from collections import deque
from pathlib import Path

SCHEMA = "yggdrasil.know33.local-metaplastic-cells-result.dev.v1"
PROTO = "yggdrasil.know33.local-metaplastic-cell-memory-prereg.v1"
PROTO_BLOB = "ce158248954a137c6540ab5b8c505dc392ea7483"
PREREG = "a2faced60dfcd7b13de5e3ae41f4c16623ea4127"
SEEDS = (18101,18109,18121,18127,18133,18143,18149,18169,18181,18191,18211,18217,
         18301,18307,18311,18313,18329,18341,18353,18367,18371,18379,18397,18401)
ARMS = ("candidate","hmm","no_neighbor","rolling","single")
MODE = "engineering_fixture_only"
MAX_STEPS = 192
FIRST = 64
MIDDLE_END = 128
HAZARD = 1.0 / 32.0


def require(x, error):
    if not x:
        raise ValueError("YGG_KNOW33_" + error)


def canonical(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=True,
                      allow_nan=False, separators=(",", ":")).encode("ascii")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def protocol():
    raw = Path(__file__).with_name("know33_local_metaplastic_protocol.json").read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    require(blob == PROTO_BLOB, "PROTOCOL_BLOB")
    p = json.loads(raw)
    require(p["schema"] == PROTO and p["source"]["mode"] == MODE
            and p["source"]["seeds"] == list(SEEDS)
            and p["budgets"]["world_pairs"] == 24
            and p["budgets"]["unique_source_witnesses"] == 7680
            and p["budgets"]["model_level_observations_per_method_across_forks"] == 9216
            and p["role"]["new_original_world_first_use"] is False
            and p["role"]["accepted_checkpoint_change"] is False, "PROTOCOL")
    return p


def public_tape(t):
    require(type(t) is int and 0 <= t < MAX_STEPS, "TAPE")
    c, a = t % 8, (t // 8) % 2
    return c, a, c ^ (a << 1)


def law_bit(law, x):
    require(law in ("A", "B1", "B2") and type(x) is int and 0 <= x < 8,
            "PRIVATE_LAW")
    x0, x1, x2 = x & 1, (x >> 1) & 1, (x >> 2) & 1
    if law == "A":
        return x0 ^ x1 ^ (x0 & x2)
    if law == "B1":
        return 1 ^ x0 ^ (x1 & x2)
    return x2 ^ (x0 & x1)


def family(seed):
    require(type(seed) is int and seed in SEEDS, "SEED")
    return "B1" if SEEDS.index(seed) < 12 else "B2"


def private_witness(seed, t, branch, *, source_mode=MODE):
    """Evaluator-only witness; true law/phase and coin never reach a cell."""
    require(source_mode == MODE and type(seed) is int and seed in SEEDS
            and type(t) is int and 0 <= t < MAX_STEPS
            and branch in ("control_A", "treatment_B"), "PRIVATE_WITNESS")
    _, _, x = public_tape(t)
    law = family(seed) if branch == "treatment_B" and FIRST <= t < MIDDLE_END else "A"
    q = .85 if law_bit(law, x) else .15
    coin = hashlib.sha256(f"know33:private:coin:v1:{seed}:{t}".encode("ascii")).digest()
    return int(int.from_bytes(coin[:8], "big") / (1 << 64) < q)


class Beta:
    def __init__(self, a=1.0, b=1.0):
        require(type(a) in (float,int) and type(b) in (float,int)
                and 0 < a < 1000 and 0 < b < 1000, "BETA")
        self.a, self.b = float(a), float(b)

    def prob(self):
        return self.a / (self.a + self.b)

    def update(self, y, weight=1.0):
        require(type(y) is int and y in (0,1)
                and type(weight) is float and 0 <= weight <= 1
                and math.isfinite(weight), "UPDATE")
        self.a += weight * y
        self.b += weight * (1-y)

    def state(self):
        return [self.a, self.b]


class Cells:
    """8 local binary-outcome cells. Neighbors are only (0,1),(2,3),(4,5),(6,7).

    No cell receives any phase, seed, target law or other cell's private outcome.
    Candidate and no-neighbor use the same fixed shared metaplastic update law.
    """
    def __init__(self, kind):
        require(kind in ARMS, "MODEL_KIND")
        self.kind = kind
        self.slow = [Beta() for _ in range(8)]
        self.fast = [Beta() for _ in range(8)]
        self.n = [0] * 8
        self.received = 0
        self.mode_prob_a = [.95] * 8
        slots = 4 if kind == "candidate" else 8
        self.support_score = [2.0] * slots
        self.support_mode = ["slow"] * slots
        self.history = [[] for _ in range(8)]
        self.switch_fast_events = 0
        self.local_messages = 0
        self.quarantined = 0

    def group(self, x):
        return x // 2 if self.kind == "candidate" else x

    def prob(self, x):
        require(type(x) is int and 0 <= x < 8, "FORECAST_X")
        if self.kind == "single":
            return self.slow[x].prob()
        if self.kind == "rolling":
            h = self.history[x][-8:]
            return (1 + sum(h)) / (2 + len(h))
        if self.kind == "hmm":
            pa = self.mode_prob_a[x] * (1-HAZARD) + (1-self.mode_prob_a[x]) * HAZARD
            return pa * self.slow[x].prob() + (1-pa) * self.fast[x].prob()
        return (self.slow[x] if self.support_mode[self.group(x)] == "slow"
                else self.fast[x]).prob()

    def observe(self, t, x, y, *, source_mode=MODE):
        require(source_mode == MODE and type(t) is int and t == self.received
                and t < MAX_STEPS and type(x) is int and 0 <= x < 8
                and type(y) is int and y in (0,1), "PUBLIC_EVENT")
        self.received += 1
        if self.kind == "single":
            self.slow[x].update(y)
        elif self.kind == "rolling":
            self.history[x].append(y)
            if len(self.history[x]) > 8:
                del self.history[x][0]
        elif self.n[x] < 6:
            self.slow[x].update(y)
        elif self.kind == "hmm":
            pa = self.mode_prob_a[x] * (1-HAZARD) + (1-self.mode_prob_a[x]) * HAZARD
            qa, qb = self.slow[x].prob(), self.fast[x].prob()
            la = qa if y else 1-qa
            lb = qb if y else 1-qb
            den = pa*la + (1-pa)*lb
            require(den > 0, "HMM_DEN")
            p = pa*la/den
            self.slow[x].update(y,float(p))
            self.fast[x].update(y,float(1-p))
            self.mode_prob_a[x] = p
        else:
            # Identical update rule for neighborhood support and its no-neighbor ablation.
            q_s, q_f = self.slow[x].prob(), self.fast[x].prob()
            like_s = q_s if y else 1-q_s
            like_f = q_f if y else 1-q_f
            g = self.group(x)
            self.support_score[g] = max(-8.0, min(8.0,
                .8 * self.support_score[g] + math.log(like_s/like_f)))
            self.local_messages += 1 if self.kind == "candidate" else 0
            before = self.support_mode[g]
            if self.support_score[g] < -2:
                self.support_mode[g] = "fast"
            elif self.support_score[g] > 2:
                self.support_mode[g] = "slow"
            if before != "fast" and self.support_mode[g] == "fast":
                self.switch_fast_events += 1
            if self.support_mode[g] == "fast":
                self.fast[x].update(y)
            elif like_s >= like_f:
                self.slow[x].update(y)
            else:
                self.quarantined += 1
        self.n[x] += 1

    def slow_digest(self):
        return digest(canonical([z.state() for z in self.slow]))

    def state(self):
        return {"schema":"yggdrasil.know33.cells-state.v1",
                "kind":self.kind,
                "slow":[z.state() for z in self.slow],
                "fast":[z.state() for z in self.fast],
                "n":self.n,
                "received":self.received,
                "mode_prob_a":self.mode_prob_a,
                "support_score":self.support_score,
                "support_mode":self.support_mode,
                "history":self.history,
                "switch_fast_events":self.switch_fast_events,
                "local_messages":self.local_messages,
                "quarantined":self.quarantined,
                "original_source":False}

    def checkpoint(self):
        raw = canonical(self.state())
        require(len(raw) < 8192, "BYTE_BUDGET")
        return raw

    @classmethod
    def restore(cls, raw, sha):
        require(type(raw) is bytes and len(raw) < 8192
                and digest(raw) == sha, "COLD_DIGEST")
        try:
            def reject_duplicates(pairs):
                out={}
                for k,v in pairs:
                    require(k not in out,"DUPLICATE_KEY")
                    out[k]=v
                return out
            d=json.loads(raw.decode("ascii"), object_pairs_hook=reject_duplicates)
            fresh=cls(d["kind"])
            require(d["schema"]=="yggdrasil.know33.cells-state.v1"
                    and d["original_source"] is False
                    and set(d) == set(fresh.state())
                    and len(d["slow"])==len(d["fast"])==len(d["n"])==8
                    and len(d["history"])==8
                    and all(type(n) is int and 0<=n<=MAX_STEPS for n in d["n"])
                    and type(d["received"]) is int and 0<=d["received"]<=MAX_STEPS
                    and sum(d["n"]) == d["received"],"COLD_CONTRACT")
            fresh.slow=[Beta(*row) for row in d["slow"]]
            fresh.fast=[Beta(*row) for row in d["fast"]]
            fresh.n=d["n"]
            fresh.received=d["received"]
            fresh.mode_prob_a=d["mode_prob_a"]
            fresh.support_score=d["support_score"]
            fresh.support_mode=d["support_mode"]
            fresh.history=d["history"]
            fresh.switch_fast_events=d["switch_fast_events"]
            fresh.local_messages=d["local_messages"]
            fresh.quarantined=d["quarantined"]
            require(fresh.checkpoint()==raw and
                    all(math.isfinite(v) and 0<=v<=1 for v in fresh.mode_prob_a)
                    and all(math.isfinite(v) and -8<=v<=8 for v in fresh.support_score)
                    and all(z in ("slow","fast") for z in fresh.support_mode)
                    and all(len(h)<=8 and all(type(y) is int and y in (0,1) for y in h)
                            for h in fresh.history)
                    and all(type(v) is int and v>=0 for v in
                            (fresh.switch_fast_events,fresh.local_messages,
                             fresh.quarantined)), "COLD_VALIDATION")
            return fresh
        except (ValueError,TypeError,KeyError,OverflowError,UnicodeError) as exc:
            raise ValueError("YGG_KNOW33_COLD_REJECT") from exc


def old_A_brier(m, law="A"):
    # Evaluator only; exactly 16 evenly weighted (public context, action) pairs.
    return sum((lambda p,q: q*(1-q)+(p-q)**2)(
        m.prob(c ^ (a << 1)),
        .85 if law_bit(law,c^(a<<1)) else .15)
        for c in range(8) for a in range(2)) / 16


def cold(m):
    raw=m.checkpoint()
    restored=Cells.restore(raw,digest(raw))
    require(restored.checkpoint()==raw and
            [restored.prob(x) for x in range(8)] ==
            [m.prob(x) for x in range(8)], "COLD_FUNCTION")
    return restored


def public_prefix(seed, witness):
    arms={name:Cells(name) for name in ARMS}
    calls=0
    for t in range(FIRST):
        _,_,x=public_tape(t)
        y=witness(seed,t,"control_A")
        require(type(y) is int and y in (0,1),"WITNESS_TYPE")
        calls+=1
        for m in arms.values():
            m.observe(t,x,y)
    require(calls==FIRST and all(m.received==FIRST for m in arms.values()),
            "PREFIX_CUSTODY")
    return arms,calls


def world(seed, witness=private_witness):
    """HELD uses private_witness. Focused unit tests MUST use an injected toy witness."""
    require(type(seed) is int and seed in SEEDS, "WORLD_ID")
    prefix,calls=public_prefix(seed,witness)
    initial={name:old_A_brier(m) for name,m in prefix.items()}
    old_slow=prefix["candidate"].slow_digest()
    branches={}
    for branch in ("control_A","treatment_B"):
        arms={name:cold(m) for name,m in prefix.items()}
        b_scores={name:[] for name in ARMS}
        k={name:{} for name in ARMS}
        at128=None
        for t in range(FIRST,MAX_STEPS):
            if t==MIDDLE_END:
                at128={"old_slow_digest":arms["candidate"].slow_digest(),
                       "old_A_brier":{name:old_A_brier(m) for name,m in arms.items()}}
                arms={name:cold(m) for name,m in arms.items()}
            _,_,x=public_tape(t)
            if FIRST<=t<MIDDLE_END and branch=="treatment_B":
                for name,m in arms.items():
                    b_scores[name].append(old_A_brier(m,family(seed)))
            y=witness(seed,t,branch)
            require(type(y) is int and y in (0,1),"WITNESS_TYPE")
            calls+=1
            for m in arms.values():
                m.observe(t,x,y)
            after=t+1-MIDDLE_END
            if after in (8,16,32,64):
                for name,m in arms.items():
                    k[name][str(after)] = old_A_brier(m)
        require(at128 is not None and
                all(set(z)=={"8","16","32","64"} for z in k.values()),
                "READOUT_K")
        for m in arms.values():
            require(m.received==MAX_STEPS,"BUDGET")
            cold(m)
        branches[branch]={
            "at128":at128,
            "return_A_after_k":k,
            "B_stage_mean_brier":
                {name:sum(v)/len(v) for name,v in b_scores.items()}
                if branch=="treatment_B" else None,
            "false_fast_events":arms["candidate"].switch_fast_events,
            "message_count":arms["candidate"].local_messages,
            "final_bytes":{name:len(m.checkpoint()) for name,m in arms.items()},
            "final_A_slow_digest":arms["candidate"].slow_digest()
        }
    require(calls==320,"SOURCE_CALL_COUNT")
    kept = branches["treatment_B"]["at128"]["old_slow_digest"]==old_slow
    return {"seed":seed,"family":family(seed),
            "one_shot_source_calls":calls,"A_after_prefix":initial,
            "t64_live_slow_digest":old_slow,
            "live_old_A_kept_during_B":kept,
            "branches":branches}


def proof():
    start=time.monotonic()
    protocol()
    tape=[public_tape(t) for t in range(16)]
    require(len(set((c,a) for c,a,_ in tape))==16 and
            {x for _,_,x in tape}==set(range(8)) and
            all(sum(1 for _,_,u in tape if u==x)==2 for x in range(8)),
            "PUBLIC_ACTION_COVERAGE")
    rows=[world(s) for s in SEEDS]
    require(len(rows)==24 and sum(r["one_shot_source_calls"] for r in rows)==7680,
            "HELD_SOURCE_BUDGET")
    family_metrics={}
    for law in ("B1","B2"):
        subset=[r for r in rows if r["family"]==law]
        require(len(subset)==12,"FAMILY_COUNT")
        m={}
        for arm in ARMS:
            m[arm]={"prefix_A":sum(r["A_after_prefix"][arm] for r in subset)/12,
                    "B_stage":sum(r["branches"]["treatment_B"]["B_stage_mean_brier"][arm]
                                  for r in subset)/12,
                    "return":{str(k):sum(r["branches"]["treatment_B"]
                                         ["return_A_after_k"][arm][str(k)]
                                         for r in subset)/12
                              for k in (8,16,32,64)}}
        wins={control:sum(
                r["branches"]["treatment_B"]["return_A_after_k"]["candidate"]["32"] <
                r["branches"]["treatment_B"]["return_A_after_k"][control]["32"]
                for r in subset)
              for control in ("hmm","rolling","no_neighbor")}
        family_metrics[law]={"methods":m,"candidate_wins_k32":wins}
    first_A=sum(r["A_after_prefix"]["candidate"] for r in rows)/24
    retained=sum(r["live_old_A_kept_during_B"] for r in rows)
    false_worlds=sum(r["branches"]["control_A"]["false_fast_events"]>0
                     for r in rows)
    h={
        "P0_public_support_and_sources":len(rows)==24,
        "P1_A_genuinely_learned":all(
            family_metrics[f]["methods"]["candidate"]["prefix_A"]<=.235
            for f in ("B1","B2")),
        "H1_return_advantage_over_hmm_rolling_ablation":all(
            family_metrics[f]["methods"]["candidate"]["return"][str(k)] <=
            family_metrics[f]["methods"][ctrl]["return"][str(k)]-.005
            for f in ("B1","B2") for k in (16,32)
            for ctrl in ("hmm","rolling","no_neighbor")) and all(
            family_metrics[f]["candidate_wins_k32"]["hmm"]>=9
            for f in ("B1","B2")),
        "H2_live_slow_memory_exact_20of24":retained>=20,
        "H3_B_learning_nondegradation":all(
            family_metrics[f]["methods"]["candidate"]["B_stage"] <=
            family_metrics[f]["methods"]["hmm"]["B_stage"]+.005
            for f in ("B1","B2")),
        "H4_sham_false_fast_at_most_two_worlds_and_cold":false_worlds<=2
    }
    return {"schema":SCHEMA,"protocol_blob":PROTO_BLOB,"prereg_commit":PREREG,
            "mode":MODE,"held_world_pairs":24,"unique_source_events":7680,
            "per_arm_observations_across_forks":9216,
            "observed_A_prefix_expected_brier":first_A,
            "live_A_preserved_worlds":retained,
            "false_sham_fast_worlds":false_worlds,
            "family_metrics":family_metrics,"frozen_hypotheses":h,
            "worlds":rows,
            "development_verdict":"SOURCE_ONLY_DEV_SUPPORTED" if all(h.values())
                 else "SOURCE_ONLY_DEV_NO_GO_OR_MIXED",
            "scientific":"SCIENTIFIC_NO_GO_NOT_NATIVE",
            "original_first_use_426":False,
            "accepted_native_modified":False,"deployment":"NONE",
            "script_wall_seconds":round(time.monotonic()-start,5)}


if __name__=="__main__":
    print(json.dumps(proof(),sort_keys=True))
