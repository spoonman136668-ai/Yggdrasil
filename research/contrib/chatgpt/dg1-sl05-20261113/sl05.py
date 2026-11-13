"""DG1-SL05: preregistered three-context cold-memory falsification.

No regime, seed, evaluator, counterfactual or uncharged evidence enters any
learner. The model is non-token, nongradient, symbolic synthetic DEV only.
Preregistration frozen at 10fa5ec7c983b871482b772ec54d7522ec3e3ac5.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import math
import random
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREEZE_SHA = "10fa5ec7c983b871482b772ec54d7522ec3e3ac5"
PARENT_SHA = "f440698b0d1e32bb029a43c204eb6fa3d189b236"
SCHEMA = "ygg.dg1-sl05.cold-three-bank.v1"
FULL = (1 << 40) - 1
SEEDS = {
    "ABCA": range(98001, 98009),
    "ABCB": range(98009, 98017),
    "STATIONARY": range(98017, 98025),
    "ABCD_OOD": range(98025, 98033),
}
FLIPS = (6, 14, 22, 30, 38, 46, 54, 62, 70, 78)
ARMS = (
    "cold_three_bank",
    "cold_three_bank_no_gate",
    "three_bank_forgetful_fifo",
    "conventional_three_bank_hmm",
    "conventional_three_bank_replay",
    "frozen_sl04_two_bank",
    "frozen_sl04_recent",
)

def load(label, relative):
    spec = importlib.util.spec_from_file_location(label, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

sl04 = load("sl05_frozen_sl04", "dg1-sl04-20261113/sl04.py")
native = sl04.native
control = sl04.conv

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")

def sealed(payload):
    raw = canonical({"payload": payload, "sha256": hashlib.sha256(canonical(payload)).hexdigest()})
    if len(raw) > 8192:
        raise ValueError("SL05_SNAPSHOT_CAPACITY")
    return raw

def unwrap(raw):
    try:
        if type(raw) is not bytes or not 0 < len(raw) <= 8192:
            raise ValueError("SL05_BAD_BYTES")
        wrapper = json.loads(raw)
        if type(wrapper) is not dict or set(wrapper) != {"payload", "sha256"}:
            raise ValueError("SL05_BAD_WRAPPER")
        payload = wrapper["payload"]
        if type(payload) is not dict or payload.get("schema") != SCHEMA or \
                hashlib.sha256(canonical(payload)).hexdigest() != wrapper["sha256"]:
            raise ValueError("SL05_BAD_HASH_OR_SCHEMA")
        if canonical(wrapper) != raw:
            raise ValueError("SL05_NONCANONICAL")
        return payload
    except (ValueError, TypeError, KeyError, OverflowError, UnicodeError) as exc:
        raise ValueError("SL05_BAD_CHECKPOINT") from exc

def verified(before, action, after):
    native.valid_state(before)
    native.valid_action(action)
    native.valid_state(after)
    if after not in (before, before ^ (1 << action)):
        raise ValueError("SL05_NONLOCAL_OBSERVATION")
    return [before, action, after]

def mask_update(mask, state, effect, family="native"):
    fn = native.effect if family == "native" else control.eval_rule
    return sum(1 << h for h in range(40)
               if mask & (1 << h) and fn(state, h) == effect)

def mask_prediction(mask, state, action, family="native"):
    native.valid_state(state)
    native.valid_action(action)
    z, o = (native.counts if family == "native" else control.posterior_counts)(mask, state)
    if (z and o) or not (z or o):
        return None
    return state ^ (int(bool(o)) << action)

def validate_banks(banks):
    if (type(banks) is not list or not 1 <= len(banks) <= 3 or
        any(type(bank) is not list or len(bank) != 4 or
            any(type(mask) is not int or not 0 < mask <= FULL for mask in bank)
            for bank in banks)):
        raise ValueError("SL05_BAD_BANKS")

def validate_history(history):
    if type(history) is not list or len(history) > 48:
        raise ValueError("SL05_BAD_HISTORY")
    for e in history:
        if type(e) is not list or len(e) != 3:
            raise ValueError("SL05_BAD_HISTORY_ENTRY")
        verified(*e)

class World:
    """Evaluator only. Agent constructors receive neither seed nor world."""
    def __init__(self, seed, group):
        if group not in SEEDS or seed not in SEEDS[group]:
            raise ValueError("SL05_UNREGISTERED_WORLD")
        self.seed, self.group, self.paid = seed, group, 0
        self.rules = [[0] * 4 for _ in range(3)]
        for action in range(4):
            used = set()
            for phase in range(3):
                r = random.Random(seed * 131 + phase * 719 + action * 47)
                h = r.randrange(40)
                while h in used:
                    h = (h + 1) % 40
                used.add(h)
                self.rules[phase][action] = h

    def phase(self, step):
        p = step // 20
        if self.group == "STATIONARY":
            return 0
        if p == 3:
            return {"ABCA": 0, "ABCB": 1, "ABCD_OOD": 3}[self.group]
        return p

    def _truth(self, state, action, phase):
        native.valid_state(state)
        native.valid_action(action)
        if type(phase) is not int or not 0 <= phase < 4:
            raise ValueError("SL05_BAD_PHASE")
        if phase == 3:
            bit = int(state == 15) ^ ((self.seed + action) & 1)
        else:
            bit = native.effect(state, self.rules[phase][action])
        return state ^ (bit << action)

    def step(self, state, step):
        if type(step) is not int or not 0 <= step < 80 or step != self.paid:
            raise ValueError("SL05_UNPAID_STEP")
        self.paid += 1
        if step in FLIPS:
            bit = (self.seed // 7 + step // 8) % 4
            return ("flip", bit, state ^ (1 << bit))
        action = (self.seed + step) % 4
        return ("causal", action, self._truth(state, action, self.phase(step)))

    def audit_truth(self, state, action, completed):
        if completed not in (20, 40, 60, 80):
            raise ValueError("SL05_UNREGISTERED_AUDIT")
        return self._truth(state, action, self.phase(completed - 1))

class ColdThreeBank:
    """Context-preserving, bounded symbolic memory; no hidden phase labels."""
    def __init__(self, gate=True, evict=False):
        if type(gate) is not bool or type(evict) is not bool:
            raise ValueError("SL05_BAD_MODE")
        self.gate, self.evict = gate, evict
        self.banks = [[FULL] * 4]
        self.active = 0
        self.hits = [0]
        self.last_used = [0]
        self.events = []
        self.clock = 0
        self.witness = []
        self.unresolved = False
        self.switches = 0
        self.allocations = 0
        self.abstain_reason = "untrained"
        self.rest_calls = 0

    def predict(self, state, action):
        native.valid_state(state)
        native.valid_action(action)
        if self.unresolved:
            return None
        if self.gate and (len(self.witness) < 2 or self.hits[self.active] < 2):
            return None
        return mask_prediction(self.banks[self.active][action], state, action)

    def observe(self, before, action, after):
        event = verified(before, action, after)
        physical_effect = int(after != before)
        self.events.append(event)
        self.events = self.events[-48:]
        self.clock += 1
        fits = [mask_update(bank[action], before, physical_effect)
                for bank in self.banks]
        selected = self.active
        if not fits[selected]:
            plausible = [i for i, bits in enumerate(fits) if i != selected and bits]
            if plausible:
                # Mature preserved memories are preferred over fresh/unfitted slots.
                selected = max(plausible,
                               key=lambda i: (self.hits[i], self.last_used[i], -i))
            elif len(self.banks) < 3:
                selected = len(self.banks)
                self.banks.append([FULL] * 4)
                self.hits.append(0)
                self.last_used.append(0)
                fits.append(mask_update(FULL, before, physical_effect))
                self.allocations += 1
            elif self.evict:
                # Negative forgetting control: overwrite the least recently used slot.
                selected = min(range(3), key=lambda i: (self.last_used[i], i))
                self.banks[selected] = [FULL] * 4
                self.hits[selected] = 0
                fits[selected] = mask_update(FULL, before, physical_effect)
            else:
                # Never erase a cold competency merely to explain a contradiction.
                self.unresolved = True
                self.witness = []
                self.abstain_reason = "all_banks_conflict"
                return False
        if selected != self.active:
            self.active = selected
            self.switches += 1
            self.witness = []
        self.banks[selected][action] = fits[selected]
        self.hits[selected] += 1
        self.last_used[selected] = self.clock
        if [before, action] not in self.witness:
            self.witness.append([before, action])
            self.witness = self.witness[-4:]
        self.unresolved = False
        self.abstain_reason = "pending_independent_witness" if self.gate and len(self.witness) < 2 else ""
        return True

    def rest(self):
        self.rest_calls += 1
        if len(self.events) < 4:
            return
        recent = self.events[-8:]
        scores = []
        for bank in self.banks:
            score = 0
            for before, action, after in recent:
                compatible = mask_update(bank[action], before, int(after != before))
                score += 2 if compatible else -3
            scores.append(score)
        ranked = sorted(range(len(scores)), key=lambda i:(scores[i], self.hits[i], -i), reverse=True)
        best = ranked[0]
        if best != self.active and scores[best] >= scores[self.active] + 4 and scores[best] >= 6:
            self.active = best
            self.switches += 1
            self.witness = []
            self.unresolved = False
            self.abstain_reason = "rest_cold_reactivation"

    def snapshot(self):
        payload = {"schema": SCHEMA, "kind":"cold", "gate":self.gate,
                   "evict":self.evict,"banks":self.banks,"active":self.active,
                   "hits":self.hits,"last_used":self.last_used,"events":self.events,
                   "clock":self.clock,"witness":self.witness,
                   "unresolved":self.unresolved,"switches":self.switches,
                   "allocations":self.allocations,"rest_calls":self.rest_calls,
                   "abstain_reason":self.abstain_reason}
        return sealed(payload)

    @classmethod
    def restore(cls, raw):
        try:
            p = unwrap(raw)
            if set(p) != {"schema","kind","gate","evict","banks","active","hits",
                          "last_used","events","clock","witness","unresolved",
                          "switches","allocations","rest_calls","abstain_reason"} or p["kind"] != "cold":
                raise ValueError("SL05_BAD_COLD_FIELDS")
            validate_banks(p["banks"])
            validate_history(p["events"])
            if (type(p["gate"]) is not bool or type(p["evict"]) is not bool
                or type(p["active"]) is not int or not 0 <= p["active"] < len(p["banks"])
                or type(p["unresolved"]) is not bool
                or type(p["abstain_reason"]) is not str or len(p["abstain_reason"]) > 64):
                raise ValueError("SL05_COLD_TYPE")
            for name in ("hits","last_used"):
                arr = p[name]
                if type(arr) is not list or len(arr)!=len(p["banks"]) or any(
                    type(x) is not int or not 0 <= x <= 100000 for x in arr):
                    raise ValueError("SL05_BAD_COUNTERS")
            for name in ("clock","switches","allocations","rest_calls"):
                if type(p[name]) is not int or not 0 <= p[name] <= 100000:
                    raise ValueError("SL05_BAD_COUNT")
            witness = p["witness"]
            if type(witness) is not list or len(witness)>4 or any(
                type(x) is not list or len(x)!=2 or
                type(x[0]) is not int or type(x[1]) is not int or
                not 0<=x[0]<16 or not 0<=x[1]<4 for x in witness):
                raise ValueError("SL05_BAD_WITNESS")
            out = cls(gate=p["gate"], evict=p["evict"])
            for name in ("banks","active","hits","last_used","events","clock","witness",
                         "unresolved","switches","allocations","rest_calls","abstain_reason"):
                setattr(out, name, p[name])
            if out.snapshot()!=raw:
                raise ValueError("SL05_COLD_NOT_CANONICAL")
            return out
        except (TypeError,ValueError,KeyError,OverflowError) as exc:
            raise ValueError("SL05_BAD_CHECKPOINT") from exc

class ConventionalHMM3:
    """Independently coded conventional 3-state hazard-filter control.

    Full fixed Bayesian model evidence for a short observation prefix is not
    possible with only a per-action mask; this is a disclosed HMM-style filter.
    Uses 3 additional floating posterior weights beyond 480 logical rule bits.
    """
    def __init__(self, replay=False):
        if type(replay) is not bool:
            raise ValueError("SL05_HMM_MODE")
        self.replay = replay
        self.banks = [[FULL]*4]
        self.weights = [1.0]
        self.hits = [0]
        self.active = 0
        self.events = []
        self.clock = 0
        self.unresolved = False
        self.rest_calls = 0
        self.switches = 0

    def predict(self, state, action):
        native.valid_state(state)
        native.valid_action(action)
        if self.unresolved or self.weights[self.active] < 0.60:
            return None
        return mask_prediction(self.banks[self.active][action], state, action, "control")

    def observe(self, before, action, after):
        event = verified(before, action, after)
        self.clock += 1
        self.events.append(event)
        self.events = self.events[-48:]
        eff = int(after != before)
        n = len(self.banks)
        prior = ([1.0] if n==1 else
                 [15*self.weights[i]/16 + (1-self.weights[i])/(16*(n-1))
                  for i in range(n)])
        fits = [control.survive(bank[action],before,eff) for bank in self.banks]
        if not any(fits) and n < 3:
            self.banks.append([FULL]*4)
            self.weights = [w*(1-1/16) for w in self.weights]+[1/16]
            self.hits.append(0)
            prior = self.weights[:]
            fits.append(control.survive(FULL,before,eff))
        if not any(fits):
            self.unresolved = True
            return False
        # Laplace-smoothed model evidence is based only on the paid observation.
        scores = [prior[i] * (fits[i].bit_count() + 1) /
                  (self.banks[i][action].bit_count() + 2) if fits[i] else 0.0
                  for i in range(len(fits))]
        normalizer = sum(scores)
        self.weights = [v/normalizer for v in scores]
        selected = max(range(len(fits)),key=lambda i:(self.weights[i],self.hits[i],-i))
        if selected != self.active:
            self.switches += 1
        self.active = selected
        self.banks[selected][action] = fits[selected]
        self.hits[selected] += 1
        self.unresolved = False
        return True

    def rest(self):
        self.rest_calls += 1
        if not self.replay or len(self.events)<4:
            return
        scores=[]
        for bank in self.banks:
            log_like=0.0
            for state,action,after in self.events[-8:]:
                fits=control.survive(bank[action],state,int(state!=after))
                if fits:
                    log_like += math.log((fits.bit_count()+1)/(bank[action].bit_count()+2))
                else:
                    log_like -= 3.0
            scores.append(log_like)
        best=max(scores)
        probabilities = [self.weights[i]*math.exp(max(-50.0,v-best))
                         for i,v in enumerate(scores)]
        normalizer=sum(probabilities)
        self.weights=[v/normalizer for v in probabilities]
        selected=max(range(len(scores)),key=lambda i:(self.weights[i],self.hits[i],-i))
        if selected!=self.active:
            self.switches+=1
        self.active=selected
        if self.weights[selected]<0.60:
            self.unresolved=True

    def snapshot(self):
        return sealed({"schema":SCHEMA,"kind":"conventional_hmm",
                       "replay":self.replay,"banks":self.banks,
                       "weights":self.weights,"hits":self.hits,"active":self.active,
                       "events":self.events,"clock":self.clock,
                       "unresolved":self.unresolved,"rest_calls":self.rest_calls,
                       "switches":self.switches})

    @classmethod
    def restore(cls, raw):
        try:
            p=unwrap(raw)
            if set(p)!={"schema","kind","replay","banks","weights","hits",
                         "active","events","clock","unresolved","rest_calls",
                         "switches"} or p["kind"]!="conventional_hmm":
                raise ValueError("SL05_HMM_SCHEMA")
            validate_banks(p["banks"])
            validate_history(p["events"])
            n=len(p["banks"])
            if (type(p["replay"]) is not bool or
                type(p["weights"]) is not list or len(p["weights"])!=n or
                any(type(w) not in (float,int) or not 0<=w<=1 for w in p["weights"]) or
                not abs(sum(p["weights"])-1)<1e-9 or
                type(p["hits"]) is not list or len(p["hits"])!=n or
                any(type(x) is not int or not 0<=x<=100000 for x in p["hits"]) or
                type(p["active"]) is not int or not 0<=p["active"]<n or
                type(p["unresolved"]) is not bool):
                raise ValueError("SL05_HMM_TYPES")
            for key in ("clock","rest_calls","switches"):
                if type(p[key]) is not int or not 0<=p[key]<=100000:
                    raise ValueError("SL05_HMM_COUNTS")
            out=cls(p["replay"])
            for key in ("banks","weights","hits","active","events","clock",
                        "unresolved","rest_calls","switches"):
                setattr(out,key,p[key])
            if out.snapshot()!=raw:
                raise ValueError("SL05_HMM_CANONICAL")
            return out
        except (TypeError,ValueError,KeyError,OverflowError) as exc:
            raise ValueError("SL05_BAD_CHECKPOINT") from exc

def make_arm(arm):
    if arm=="cold_three_bank":
        return ColdThreeBank(True,False)
    if arm=="cold_three_bank_no_gate":
        return ColdThreeBank(False,False)
    if arm=="three_bank_forgetful_fifo":
        return ColdThreeBank(True,True)
    if arm=="conventional_three_bank_hmm":
        return ConventionalHMM3(False)
    if arm=="conventional_three_bank_replay":
        return ConventionalHMM3(True)
    if arm=="frozen_sl04_two_bank":
        return sl04.new_learner("frozen_sl03_selective_sleep")
    if arm=="frozen_sl04_recent":
        return sl04.new_learner("conventional_recent_window")
    raise ValueError("SL05_BAD_ARM")

def restore_arm(arm, raw):
    if arm in ("cold_three_bank","cold_three_bank_no_gate","three_bank_forgetful_fifo"):
        obj=ColdThreeBank.restore(raw)
        if obj.gate != (arm!="cold_three_bank_no_gate") or \
           obj.evict != (arm=="three_bank_forgetful_fifo"):
            raise ValueError("SL05_WRONG_ARM_MODE")
        return obj
    if arm.startswith("conventional_three_bank_"):
        obj=ConventionalHMM3.restore(raw)
        if obj.replay != (arm=="conventional_three_bank_replay"):
            raise ValueError("SL05_WRONG_CONTROL_MODE")
        return obj
    if arm=="frozen_sl04_two_bank":
        return sl04.sl03.Learner.restore(raw)
    if arm=="frozen_sl04_recent":
        return sl04.restore_control(raw)
    raise ValueError("SL05_BAD_ARM")

def evaluate(agent, world, seen, point):
    out={x:0 for x in ("correct","wrong_confident","abstained",
                       "unseen_correct","unseen_wrong_confident","unseen_abstained")}
    for state in range(16):
        for action in range(4):
            truth=world.audit_truth(state,action,point)
            got=agent.predict(state,action)
            tag="abstained" if got is None else "correct" if got==truth else "wrong_confident"
            out[tag]+=1
            if (state,action) not in seen:
                out["unseen_"+tag]+=1
    return out

def one_world(seed, group):
    env=World(seed,group)
    agents={arm:make_arm(arm) for arm in ARMS}
    state=seed%16
    events_seen=set()
    charged=[]
    prequential={arm:{"correct":0,"wrong_confident":0,"abstained":0} for arm in ARMS}
    cold_check={arm:False for arm in ARMS}
    audits={arm:{} for arm in ARMS}
    durations={arm:0 for arm in ARMS}
    checkpoint_sizes={arm:{} for arm in ARMS}
    for step in range(80):
        before=state
        kind,action,after=env.step(state,step)
        if kind=="causal":
            for arm,agent in agents.items():
                begin=time.perf_counter_ns()
                got=agent.predict(before,action)
                key="abstained" if got is None else "correct" if got==after else "wrong_confident"
                prequential[arm][key]+=1
                agent.observe(before,action,after)
                durations[arm]+=time.perf_counter_ns()-begin
            events_seen.add((before,action))
        state=after
        charged.append([before,kind,action,after])
        if (step+1)%8==0:
            for arm,agent in agents.items():
                t0=time.perf_counter_ns()
                agent.rest()
                durations[arm]+=time.perf_counter_ns()-t0
        if step+1 in (20,40,60,80):
            for arm,agent in agents.items():
                audits[arm][str(step+1)]=evaluate(agent,env,events_seen,step+1)
        if step+1==60:
            # The resumed phase genuinely continues from persisted memory,
            # rather than the live object used to learn A/B/C.
            for arm,agent in list(agents.items()):
                snapshot=agent.snapshot()
                restored=restore_arm(arm,snapshot)
                if snapshot!=restored.snapshot() or any(
                    agent.predict(s,a)!=restored.predict(s,a)
                    for s in range(16) for a in range(4)):
                    raise AssertionError("SL05_COLD_RESTORE_DIVERGENCE")
                cold_check[arm]=True
                checkpoint_sizes[arm]["60"]=len(snapshot)
                agents[arm]=restored
    if env.paid!=80 or sum(row[1]=="flip" for row in charged)!=10:
        raise AssertionError("SL05_PHYSICAL_ACTION_MISMATCH")
    for arm,agent in agents.items():
        raw=agent.snapshot()
        restored=restore_arm(arm,raw)
        if raw!=restored.snapshot() or any(agent.predict(s,a)!=restored.predict(s,a)
                                          for s in range(16) for a in range(4)):
            raise AssertionError("SL05_FINAL_COLD_RESTORE_DIVERGENCE")
        checkpoint_sizes[arm]["80"]=len(raw)
        if len(raw)>8192:
            raise AssertionError("SL05_MEMORY_CAPACITY")
    return {
        "seed":seed,"group":group,"paid_actions":env.paid,"causal_observations":70,
        "paid_flips":10,"physical_trajectory_sha256":hashlib.sha256(canonical(charged)).hexdigest(),
        "cold_restore_at_60":cold_check,
        "audits":audits,"prequential":prequential,
        "snapshot_bytes":checkpoint_sizes,
        "whole_inference_update_rest_ns":durations
    }

def run():
    worlds=[one_world(seed,group) for group,seq in SEEDS.items() for seed in seq]
    keys=("correct","wrong_confident","abstained","unseen_correct",
          "unseen_wrong_confident","unseen_abstained")
    agg={group:{arm:{key:sum(w["audits"][arm]["80"][key] for w in worlds
                                   if w["group"]==group) for key in keys}
                for arm in ARMS} for group in SEEDS}
    controls=("conventional_three_bank_hmm","conventional_three_bank_replay")
    best={group:{
        "correct":max(agg[group][a]["correct"] for a in controls),
        "unseen_correct":max(agg[group][a]["unseen_correct"] for a in controls),
        "wrong_confident":min(agg[group][a]["wrong_confident"] for a in controls)
    } for group in SEEDS}
    candidate="cold_three_bank"
    abca=agg["ABCA"][candidate]
    abcb=agg["ABCB"][candidate]
    stationary=agg["STATIONARY"][candidate]
    ood=agg["ABCD_OOD"][candidate]
    primary=(abca["correct"]-best["ABCA"]["correct"]>=16
             and abca["unseen_correct"]-best["ABCA"]["unseen_correct"]>=8
             and abca["wrong_confident"]<=best["ABCA"]["wrong_confident"]+4
             and abcb["correct"]-best["ABCB"]["correct"]>=16
             and abcb["wrong_confident"]<=best["ABCB"]["wrong_confident"]+4
             and stationary["correct"]>=best["STATIONARY"]["correct"]-16
             and stationary["wrong_confident"]<=best["STATIONARY"]["wrong_confident"]+4
             and ood["wrong_confident"]<=best["ABCD_OOD"]["wrong_confident"]+4)
    gains=(abca["correct"]>best["ABCA"]["correct"] and
           abcb["correct"]>best["ABCB"]["correct"])
    category=("DEV_SIGNAL_NOT_SCIENCE" if primary else
              "MIXED_DEV" if gains else "NEGATIVE_DEV")
    return {
        "schema":"ygg.dg1-sl05.three-context-frozen-dev-result.v1",
        "prereg_sha":FREEZE_SHA,"source_parent_sha":PARENT_SHA,
        "classification":category,"primary_pass":primary,
        "scientific_acceptance":"UNVERIFIED",
        "native_specific_advantage_proven":False,
        "sleep_timing_advantage_proven":False,
        "same_physical_actions":True,"same_total_compute":False,
        "world_count":len(worlds),
        "physical_actions_total":sum(w["paid_actions"] for w in worlds),
        "baseline_envelope":best,"aggregate":agg,"worlds":worlds
    }

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,separators=(",",":")))
