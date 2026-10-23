"""ITD01 R9: native action-observing delayed-credit local cellular learner.

Original Yggdrasil R7 remains untouched; public developmental data only.
No inherited R7 cohorts, MiniGrid/Pycolab, transformer, GRU, or Wingless weights.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Protocol

MASK = (1 << 64) - 1
FAMILIES = ("A", "B", "C")
SEEDS = (101, 211, 307)
FEATURE_COUNT = 10
DELAY = 2
SCHEMA = "ygg.itd01.r9.action-causal-native.v1"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def features(sensors):
    if (type(sensors) not in (list, tuple) or len(sensors) != 4 or
            any(type(bit) is not bool for bit in sensors)):
        raise ValueError("R9_PUBLIC_SENSOR_SHAPE")
    z = [1 if s else -1 for s in sensors]
    return tuple(z) + tuple(z[i]*z[j] for i in range(4)
                           for j in range(i+1, 4))


def check_family(family):
    if family not in FAMILIES:
        raise ValueError("R9_PUBLIC_FAMILY_INVALID")


def check_action(action):
    if type(action) is not int or action not in (0, 1):
        raise ValueError("R9_BINARY_ACTION_REQUIRED")


def hidden_target(family, sensors):
    """Private source-only causal law; never used by fitted model algorithms."""
    check_family(family)
    features(sensors)
    if family == "A":
        return int(sensors[0] != sensors[1])
    if family == "B":
        return int(sensors[2] != sensors[3])
    return int(sensors[0] != sensors[3])


def source_seed(seed, role, family):
    if type(seed) is not int or role not in (
            "FIT_A", "FIT_B", "FIT_C", "VALID_A_PRE", "VALID_A_POST",
            "VALID_B", "VALID_C_ZERO", "DEV_C_POST", "DEV_A_RETAINED"):
        raise ValueError("R9_SOURCE_ROLE_INVALID")
    check_family(family)
    h = hashlib.sha256(
        f"ITD01-R9-ROLE:{seed}:{role}:{family}".encode("ascii")
    ).digest()
    return int.from_bytes(h[:8], "big") or 1


class PublicSource:
    """Deterministic simulator. Generator rule and target remain private."""

    def __init__(self, seed, role, family):
        self.state = source_seed(seed, role, family)
        self.family = family
        self.calls = 0

    def next_u64(self):
        s = self.state
        s ^= (s << 13) & MASK
        s ^= s >> 7
        s ^= (s << 17) & MASK
        self.state = s & MASK
        return self.state

    def next_sensors(self):
        self.calls += 1
        word = self.next_u64()
        return tuple(bool((word >> i) & 1) for i in range(4))


@dataclass
class Cell:
    fast: float = 0.
    slow: float = 0.
    public_updates: int = 0

    def response(self, phi):
        return (0.75*self.fast + 0.25*self.slow)*phi

    def adjust(self, signed_target, phi, mistake):
        if mistake:
            self.fast = max(-32., min(32., self.fast + signed_target*phi))
        self.slow = 0.92*self.slow + 0.08*self.fast
        self.public_updates += 1


class LocalActionColony:
    name = "ygg-native-action-cellular"

    def __init__(self):
        self.cells = {f:[Cell() for _ in range(FEATURE_COUNT)]
                      for f in FAMILIES}
        self.bias = {f:0. for f in FAMILIES}
        self.pending = {}
        self.feedback_updates = 0
        self.weight_changes = 0
        self.neighbor_contributions = 0
        self.message_evaluations = 0

    def choose(self, family, sensors, use_neighbors=True):
        check_family(family)
        x = features(sensors)
        local = [c.response(z) for c,z in zip(self.cells[family], x)]
        vote = self.bias[family] + sum(local)
        if use_neighbors:
            # NONLINEAR and NONUNIFORM actual nearest-neighbor interaction.
            # This cannot algebraically reduce to (1+gain)*sum(local),
            # unlike original Ygg R7. No claim of beneficial causality:
            # zero-message counterfactual must still be measured.
            for i, own in enumerate(local):
                pair = own*local[(i+1) % FEATURE_COUNT]
                vote += 0.025*pair
                self.neighbor_contributions += int(abs(pair)>1e-14)
                self.message_evaluations += 1
        return int(vote > 0.)

    def observe_public_action(self, token, family, sensors, action, tick):
        check_family(family)
        features(sensors)
        check_action(action)
        if token in self.pending or type(tick) is not int or tick < 0:
            raise ValueError("R9_PENDING_ACTION_IDENTITY")
        self.pending[token] = (family, tuple(sensors), action, tick)

    def learn_delayed(self, token, success, tick):
        if token not in self.pending:
            raise ValueError("R9_FEEDBACK_WITHOUT_PRIOR_PUBLIC_ACTION")
        if type(success) is not bool or type(tick) is not int:
            raise ValueError("R9_FEEDBACK_FORMAT_INVALID")
        f,sensors,action,start = self.pending[token]
        if tick - start != DELAY:
            raise ValueError("R9_EARLY_OR_STALE_FEEDBACK_BLOCKED")
        # Public chosen action + public success jointly identify a TARGET.
        # No private generator target, hidden cause or source state is read.
        inferred_correct = action if success else 1-action
        expected = 1 if inferred_correct else -1
        guess = self.choose(f, sensors)
        mistake = int(guess != inferred_correct)
        xx = features(sensors)
        for cell, phi in zip(self.cells[f], xx):
            cell.adjust(expected, phi, mistake)
        if mistake:
            self.bias[f] += 0.4*expected
            self.bias[f] = max(-8.,min(8.,self.bias[f]))
            self.weight_changes += 1
        self.feedback_updates += 1
        del self.pending[token]

    def checkpoint(self):
        if self.pending:
            raise ValueError("R9_PENDING_PUBLIC_FEEDBACK_AT_CHECKPOINT")
        return {
            "schema": SCHEMA,
            "cells": {
                f: [{"fast":c.fast, "slow":c.slow, "updates":c.public_updates}
                    for c in self.cells[f]]
                for f in FAMILIES
            },
            "bias": dict(self.bias),
            "feedback_updates":self.feedback_updates,
            "weight_changes":self.weight_changes,
            "message_evaluations":self.message_evaluations,
            "neighbor_contributions":self.neighbor_contributions,
        }

    def save(self):
        body = self.checkpoint()
        raw = canonical(body)
        if len(raw)>32768:
            raise ValueError("R9_NATIVE_CHECKPOINT_BUDGET")
        return canonical({"payload":body, "sha256":hashlib.sha256(raw).hexdigest()})

    @classmethod
    def restore(cls, blob):
        if type(blob) is not bytes or len(blob) == 0 or len(blob)>32768:
            raise ValueError("R9_NATIVE_CHECKPOINT_SIZE")
        try:
            container = json.loads(blob)
            body = container["payload"]
            expected = container["sha256"]
        except (ValueError,TypeError,KeyError):
            raise ValueError("R9_NATIVE_CHECKPOINT_STRUCTURE")
        if type(expected) is not str or len(expected)!=64 or \
                hashlib.sha256(canonical(body)).hexdigest()!=expected:
            raise ValueError("R9_NATIVE_CHECKPOINT_HASH")
        if body.get("schema")!=SCHEMA or set(body["cells"])!=set(FAMILIES) \
                or set(body["bias"])!=set(FAMILIES):
            raise ValueError("R9_NATIVE_CHECKPOINT_SOURCE_IDENTITY")
        model = cls()
        for f in FAMILIES:
            if len(body["cells"][f])!=FEATURE_COUNT:
                raise ValueError("R9_CELL_COUNT_DRIFT")
            learned=[]
            for v in body["cells"][f]:
                if set(v)!={"fast","slow","updates"} or \
                     type(v["updates"]) is not int or v["updates"]<0 or \
                     not all(type(v[k]) in (int,float) and math.isfinite(v[k])
                             for k in ("fast","slow")) or \
                     not -32<=v["fast"]<=32:
                    raise ValueError("R9_CELL_STATE_INVALID")
                learned.append(Cell(v["fast"],v["slow"],v["updates"]))
            model.cells[f]=learned
            bias=body["bias"][f]
            if type(bias) not in (int,float) or \
                    not math.isfinite(bias) or not -8<=bias<=8:
                raise ValueError("R9_CELL_BIAS_INVALID")
            model.bias[f]=bias
        for label in ("feedback_updates","weight_changes",
                      "message_evaluations","neighbor_contributions"):
            n=body[label]
            if type(n) is not int or n<0:
                raise ValueError("R9_COUNTER_INVALID")
            setattr(model,label,n)
        return model


class PairwisePerceptron:
    name = "conventional-pairwise-perceptron"

    def __init__(self):
        self.weights={f:[0.]*FEATURE_COUNT for f in FAMILIES}
        self.bias={f:0. for f in FAMILIES}
        self.pending={}
        self.feedback_updates=0
        self.weight_changes=0

    def choose(self, family, sensors):
        check_family(family)
        return int(self.bias[family] +
                   sum(w*x for w,x in zip(self.weights[family],
                                          features(sensors))) > 0)

    def observe_public_action(self,token,family,sensors,action,tick):
        check_family(family)
        features(sensors)
        check_action(action)
        if token in self.pending:
            raise ValueError("R9_CONTROL_TOKEN_REPEAT")
        self.pending[token]=(family,tuple(sensors),action,tick)

    def learn_delayed(self,token,success,tick):
        if token not in self.pending:
            raise ValueError("R9_CONTROL_MISSING_ACTION")
        f,s,a,t=self.pending[token]
        if tick-t!=DELAY or type(success) is not bool:
            raise ValueError("R9_CONTROL_DELAY_INVALID")
        label=a if success else 1-a
        if self.choose(f,s)!=label:
            d=1 if label else -1
            self.weights[f]=[w+d*x for w,x in zip(self.weights[f],features(s))]
            self.bias[f]+=d
            self.weight_changes+=1
        self.feedback_updates+=1
        del self.pending[token]

    def save(self):
        if self.pending:
            raise ValueError("R9_CONTROL_PENDING_FEEDBACK")
        return canonical({"weights":self.weights,"bias":self.bias,
                          "feedback_updates":self.feedback_updates,
                          "weight_changes":self.weight_changes})


class EpisodicActionMemory:
    name = "conventional-episodic-action-memory"

    def __init__(self):
        self.memory={f:{} for f in FAMILIES}
        self.pending={}
        self.feedback_updates=0
        self.weight_changes=0

    def choose(self,family,sensors):
        check_family(family)
        features(sensors)
        return self.memory[family].get("".join(str(int(z)) for z in sensors),0)

    def observe_public_action(self,token,family,sensors,action,tick):
        check_family(family)
        features(sensors)
        check_action(action)
        if token in self.pending:
            raise ValueError("R9_CASE_PENDING_DUPLICATE")
        self.pending[token]=(family,tuple(sensors),action,tick)

    def learn_delayed(self,token,success,tick):
        if token not in self.pending:
            raise ValueError("R9_CASE_UNMATCHED_FEEDBACK")
        f,s,a,t=self.pending[token]
        if tick-t!=DELAY or type(success) is not bool:
            raise ValueError("R9_CASE_WRONG_DELAY")
        key="".join(str(int(z)) for z in s)
        new=a if success else 1-a
        self.weight_changes+=int(self.memory[f].get(key)!=new)
        self.memory[f][key]=new
        self.feedback_updates+=1
        del self.pending[token]

    def save(self):
        if self.pending:
            raise ValueError("R9_CASE_PENDING_FEEDBACK")
        return canonical({"memory":self.memory,
                          "feedback_updates":self.feedback_updates,
                          "weight_changes":self.weight_changes})


class CurrentOnlyZero:
    name = "untrained-current-only-zero"

    def choose(self,family,sensors):
        check_family(family)
        features(sensors)
        return 0


def train_equal_public_interventions(agents,seed,role,family,n):
    if role not in ("FIT_A","FIT_B","FIT_C") or n < 1:
        raise ValueError("R9_FIT_ROLE_OR_BUDGET_INVALID")
    source=PublicSource(seed,role,family)
    due={}
    messages=[]
    actions=0
    observations=0
    cpu=time_process_time()
    for tick in range(n+DELAY):
        for token, sensors,action,success in due.pop(tick,[]):
            for agent in agents:
                agent.learn_delayed(token,success,tick)
            messages.append({
                "id":token,"success":success,
                "observed_at_tick":tick,
            })
            observations+=1
        if tick>=n:
            continue
        sensors=source.next_sensors()
        action=(sum(sensors)+tick)%2
        success=bool(action==hidden_target(family,sensors))
        token=f"R9-PUBLIC-{seed}-{role}-{family}-{tick}"
        for agent in agents:
            agent.observe_public_action(token,family,sensors,action,tick)
        due.setdefault(tick+DELAY,[]).append(
            (token,sensors,action,success))
        messages.append({"id":token,"tick":tick,"public_sensors":sensors,
                         "public_action":action})
        actions+=1
    if due or actions!=n or observations!=n:
        raise AssertionError("R9_PUBLIC_EXPERIENCE_COUNT_DRIFT")
    for agent in agents:
        if agent.pending:
            raise AssertionError("R9_FEEDBACK_NOT_DRAINED")
    return {
        "public_fit_interactions":actions,
        "public_delayed_feedback":observations,
        "public_intervention_trace_sha256":sha(messages),
        "source_draws":source.calls,
        "shared_fit_process_cpu_seconds":time_process_time()-cpu,
    }


def time_process_time():
    import time
    return time.process_time()


def evaluate(agents,seed,role,family,n,checkpoint=None):
    if role not in ("VALID_A_PRE","VALID_A_POST","VALID_B",
                    "VALID_C_ZERO","DEV_C_POST","DEV_A_RETAINED") or n<1:
        raise ValueError("R9_EVAL_ROLE_OR_BUDGET")
    src=PublicSource(seed,role,family)
    actual={agent.name:0 for agent in agents}
    ablate={"native_no_neighbor":0,"native_erased_state":0}
    disagreement=0
    shadow=LocalActionColony()
    native=agents[0]
    original_bytes=native.save()
    for _ in range(n):
        sensors=src.next_sensors()
        truth=hidden_target(family,sensors)
        labels={}
        for agent in agents:
            a=agent.choose(family,sensors)
            check_action(a)
            labels[agent.name]=a
            actual[agent.name]+=int(a==truth)
        no_message=native.choose(family,sensors,use_neighbors=False)
        erase=shadow.choose(family,sensors,use_neighbors=False)
        check_action(no_message)
        check_action(erase)
        ablate["native_no_neighbor"]+=int(no_message==truth)
        ablate["native_erased_state"]+=int(erase==truth)
        disagreement+=int(no_message!=labels[native.name])
    # Inference can increment message counters but not trained cell weights.
    restored=LocalActionColony.restore(native.save())
    if native.save()!=restored.save():
        raise AssertionError("R9_NATIVE_COLD_RESTORE_CHANGED")
    if any(getattr(a, "pending", {}) for a in agents):
        raise AssertionError("R9_EVAL_PENDING_FEEDBACK")
    return {
        "role":role,"family":family,"n":n,
        "success":{k:v/n for k,v in actual.items()},
        "native_no_neighbor_success":ablate["native_no_neighbor"]/n,
        "native_erased_state_success":ablate["native_erased_state"]/n,
        "native_neighbor_action_disagreement":disagreement,
        "all_actions_legal":True,
        "public_observation_seed_sha256":sha({
            "seed":seed,"role":role,"family":family,"n":n,
            "source_role_identity":source_seed(seed,role,family)
        }),
        "eval_parameter_updates":0,
    }
