"""ITD-01 NLD-02: one actual shared 10-cell learner, no family input to learners.

Only the R9 already-public smoke seed 3 is reused. This is not scientific first use.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

R9_PATH = Path(__file__).resolve().parents[1] / "r9"
sys.path.insert(0, str(R9_PATH))
from action_cells import (  # noqa: E402
    Cell, DELAY, PublicSource, canonical, check_action, features,
)

SEED = 3
FIT = 128
EVAL = 64
SCHEMA = "itd01.nld02.familyblind-singlebank-public-smoke.v1"
PATTERNS = tuple(itertools.product((False, True), repeat=4))


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def source_only_correct_action(family, sensors):
    """Private source/scorer path only. This function must never be called by an arm."""
    from action_cells import hidden_target
    return hidden_target(family, sensors)


def public_sensor_key(sensors):
    features(sensors)
    return "".join(str(int(b)) for b in sensors)


class SharedLocalCells:
    name = "shared-native-ten-cell"
    def __init__(self):
        self.cells = [Cell() for _ in range(10)]
        self.bias = 0.0
        self.pending = {}
        self.feedback_updates = 0
        self.weight_changes = 0

    def choose(self, sensors, use_neighbors=True):
        x = features(sensors)
        contributions = [c.response(z) for c, z in zip(self.cells, x)]
        v = self.bias + sum(contributions)
        if use_neighbors:
            for i, own in enumerate(contributions):
                v += .025 * own * contributions[(i+1) % 10]
        return int(v > 0)

    def observe_public_action(self, token, sensors, action, tick):
        features(sensors)
        check_action(action)
        if type(token) is not str or not token or token in self.pending:
            raise ValueError("NLD02_INVALID_OR_DUPLICATE_TOKEN")
        if type(tick) is not int or tick < 0:
            raise ValueError("NLD02_INVALID_EVENT_TICK")
        self.pending[token] = (tuple(sensors), action, tick)

    def learn_delayed(self, token, success, tick):
        if token not in self.pending:
            raise ValueError("NLD02_FEEDBACK_MISSING_PUBLIC_ACTION")
        if type(success) is not bool or type(tick) is not int:
            raise ValueError("NLD02_FEEDBACK_INVALID_FORMAT")
        sensors, action, born = self.pending[token]
        if tick - born != DELAY:
            raise ValueError("NLD02_FEEDBACK_EARLY_OR_LATE")
        correct = action if success else 1 - action
        expected = 1 if correct else -1
        mistake = self.choose(sensors) != correct
        for c, phi in zip(self.cells, features(sensors)):
            c.adjust(expected, phi, mistake)
        if mistake:
            self.bias = max(-8.0, min(8.0, self.bias + .4 * expected))
            self.weight_changes += 1
        self.feedback_updates += 1
        del self.pending[token]

    def snapshot(self):
        if self.pending:
            raise ValueError("NLD02_PENDING_PUBLIC_FEEDBACK")
        return {"schema": SCHEMA, "cells": [
            {"fast": c.fast, "slow": c.slow, "updates": c.public_updates}
            for c in self.cells], "bias": self.bias,
            "feedback_updates": self.feedback_updates,
            "weight_changes": self.weight_changes}

    def save(self):
        body = self.snapshot()
        return canonical({"payload": body, "sha256": digest(body)})

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or len(raw) > 32768 or not raw:
            raise ValueError("NLD02_CHECKPOINT_SIZE")
        try:
            outer = json.loads(raw)
            payload = outer["payload"]
            expected = outer["sha256"]
        except (ValueError, TypeError, KeyError):
            raise ValueError("NLD02_CHECKPOINT_STRUCTURE")
        if type(expected) is not str or digest(payload) != expected:
            raise ValueError("NLD02_CHECKPOINT_HASH")
        if (type(payload) is not dict or
                set(payload) != {"schema","cells","bias","feedback_updates","weight_changes"} or
                payload["schema"] != SCHEMA or
                type(payload["cells"]) is not list or len(payload["cells"]) != 10):
            raise ValueError("NLD02_CHECKPOINT_IDENTITY")
        m = cls()
        cs = []
        for item in payload["cells"]:
            if type(item) is not dict or set(item) != {"fast","slow","updates"}:
                raise ValueError("NLD02_CELL_SHAPE")
            if (type(item["updates"]) is not int or item["updates"] < 0 or
                any(type(item[k]) not in (int,float) or not math.isfinite(item[k])
                    for k in ("fast","slow")) or
                not (-32 <= item["fast"] <= 32)):
                raise ValueError("NLD02_CELL_DATA")
            cs.append(Cell(item["fast"], item["slow"], item["updates"]))
        m.cells = cs
        bias = payload["bias"]
        if type(bias) not in (int, float) or not math.isfinite(bias) or not -8 <= bias <= 8:
            raise ValueError("NLD02_BIAS_INVALID")
        m.bias = bias
        for k in ("feedback_updates", "weight_changes"):
            v = payload[k]
            if type(v) is not int or v < 0:
                raise ValueError("NLD02_COUNTER_INVALID")
            setattr(m, k, v)
        if m.save() != raw:
            raise ValueError("NLD02_CHECKPOINT_NONCANONICAL")
        return m


class SharedPerceptron:
    name = "trained-shared-pairwise-perceptron"
    def __init__(self):
        self.weights = [0.] * 10
        self.bias = 0.
        self.pending = {}
        self.feedback_updates = 0
        self.weight_changes = 0
    def choose(self, sensors):
        return int(self.bias + sum(w*x for w,x in zip(self.weights,features(sensors))) > 0)
    def observe_public_action(self,token,sensors,action,tick):
        features(sensors);check_action(action)
        if token in self.pending:raise ValueError("NLD02_PAIRWISE_DUP_TOKEN")
        self.pending[token] = (tuple(sensors),action,tick)
    def learn_delayed(self,token,success,tick):
        if token not in self.pending:raise ValueError("NLD02_PAIRWISE_UNMATCHED_FEEDBACK")
        sensors,a,start=self.pending[token]
        if type(success) is not bool or tick-start != DELAY:
            raise ValueError("NLD02_PAIRWISE_WRONG_DELAY")
        correct = a if success else 1-a
        if self.choose(sensors)!=correct:
            d=1 if correct else -1
            self.weights=[w+d*x for w,x in zip(self.weights,features(sensors))]
            self.bias+=d
            self.weight_changes+=1
        self.feedback_updates+=1
        del self.pending[token]
    def save(self):
        if self.pending:raise ValueError("NLD02_PAIRWISE_PENDING")
        return canonical({"weights":self.weights,"bias":self.bias,
            "feedback_updates":self.feedback_updates,"weight_changes":self.weight_changes})


class SharedEpisodic:
    name = "trained-shared-episodic-action-memory"
    def __init__(self):
        self.memory={}
        self.pending={}
        self.feedback_updates=0
        self.weight_changes=0
    def choose(self,sensors):
        return self.memory.get(public_sensor_key(sensors),0)
    def observe_public_action(self,token,sensors,action,tick):
        public_sensor_key(sensors);check_action(action)
        if token in self.pending:raise ValueError("NLD02_EPISODIC_DUP_TOKEN")
        self.pending[token]=(tuple(sensors),action,tick)
    def learn_delayed(self,token,success,tick):
        if token not in self.pending:raise ValueError("NLD02_EPISODIC_UNMATCHED_FEEDBACK")
        s,a,born=self.pending[token]
        if type(success) is not bool or tick-born!=DELAY:
            raise ValueError("NLD02_EPISODIC_WRONG_DELAY")
        key=public_sensor_key(s)
        correct=a if success else 1-a
        self.weight_changes+=int(self.memory.get(key)!=correct)
        self.memory[key]=correct
        self.feedback_updates+=1
        del self.pending[token]
    def save(self):
        if self.pending:raise ValueError("NLD02_EPISODIC_PENDING")
        return canonical({"memory":self.memory,"feedback_updates":self.feedback_updates,
                          "weight_changes":self.weight_changes})


class ConstantZero:
    name="untrained-current-only-zero"
    def choose(self,sensors):
        features(sensors)
        return 0


def fit_public(arms, family, seed=SEED, n=FIT):
    if type(seed) is not int or seed != SEED or family not in ("A","B") or n!=FIT:
        raise ValueError("NLD02_FROZEN_EXISTING_SMOKE_SOURCE_ONLY")
    role="FIT_"+family
    src=PublicSource(seed,role,family)
    due={}
    trace=[]
    count=0
    for tick in range(n+DELAY):
        for token,action,sensors,success in due.pop(tick,[]):
            for a in arms:a.learn_delayed(token,success,tick)
            trace.append({"token":token,"feedback_tick":tick,"success":success})
            count+=1
        if tick>=n:continue
        sensors=src.next_sensors()
        action=(sum(sensors)+tick)%2
        # Source knows the disclosed correct action; candidate arms do not.
        success=bool(action==source_only_correct_action(family,sensors))
        token=f"NLD02-R9-SMOKE-{seed}-{role}-{tick}"
        for a in arms:a.observe_public_action(token,sensors,action,tick)
        due.setdefault(tick+DELAY,[]).append((token,action,sensors,success))
        trace.append({"token":token,"tick":tick,"sensors":sensors,"action":action})
    if due or count!=n or src.calls!=n or any(a.pending for a in arms):
        raise AssertionError("NLD02_PUBLIC_FEEDBACK_NOT_DRAINED")
    return {"role":role,"public_actions":n,"delayed_feedback":count,
            "source_calls":src.calls,"shared_public_trace_sha256":digest(trace)}


def score_public(arms, family, role, seed=SEED, n=EVAL):
    if type(seed) is not int or seed!=SEED or n!=EVAL or (
        (family,role) not in {("A","VALID_A_PRE"),("A","VALID_A_POST"),
                              ("A","DEV_A_RETAINED"),("B","VALID_B")}):
        raise ValueError("NLD02_SCORE_SOURCE_ROLE_INVALID")
    src=PublicSource(seed,role,family)
    erased=SharedLocalCells()
    score={a.name:0 for a in arms}
    score["erased-native-state"]=0
    disagreements=0
    stored={a.name: a.save() for a in arms if hasattr(a,"save")}
    for _ in range(n):
        sensors=src.next_sensors()
        truth=source_only_correct_action(family,sensors)
        for a in arms:
            chosen=a.choose(sensors)
            check_action(chosen)
            score[a.name]+=int(chosen==truth)
        erase=erased.choose(sensors)
        score["erased-native-state"]+=int(erase==truth)
        disagreements+=int(arms[0].choose(sensors)!=erase)
    if any(stored[name]!=a.save() for a in arms if (name:=a.name) in stored):
        raise AssertionError("NLD02_EVAL_CHANGED_MODEL")
    return {"role":role,"n":n,"family_scoring_only":family,
            "family_label_given_to_learner":False,
            "accuracy":{name:v/n for name,v in score.items()},
            "native_vs_erased_action_disagreements":disagreements,
            "no_model_updates_on_score":True,
            "source_role_sha256":digest({"seed":seed,"family":family,"role":role,"n":n})}


def checkpoint(native):
    raw=native.save()
    restored=SharedLocalCells.restore(raw)
    prediction_count=0
    for sensors in PATTERNS:
        if native.choose(sensors)!=restored.choose(sensors):
            raise AssertionError("NLD02_COLD_PREDICTION_DIFFERENT")
        prediction_count+=1
    if native.save()!=restored.save():
        raise AssertionError("NLD02_COLD_RESTORE_INEXACT")
    return {"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),
            "matching_16_public_decisions":prediction_count,"cold_restore_exact":True}


def alias_certificate():
    conflict=sum(source_only_correct_action("A",p)!=source_only_correct_action("B",p)
                 for p in PATTERNS)
    if conflict!=8:raise AssertionError("NLD02_ORIGINAL_SOURCE_ALIAS_COUNT_DRIFT")
    return {"public_four_bit_patterns":16,
        "different_A_B_action_targets_without_task_cue":conflict,
        "max_joint_correct_on_balanced_uniform_A_B":(32-conflict)/32,
        "target_rule_visible_to_learner":False,
        "causal_identifiability_without_task_cue":"ALIASED_FOR_SIMULTANEOUS_A_B"}


def run(seed=SEED):
    if type(seed) is not int or seed!=SEED:
        raise ValueError("NLD02_REUSE_ONLY_PRIOR_PUBLIC_SEED_3")
    native=SharedLocalCells()
    controls=[SharedPerceptron(),SharedEpisodic()]
    arms=[native]+controls
    views=arms+[ConstantZero()]
    pre=score_public(views,"A","VALID_A_PRE")
    fit_a=fit_public(arms,"A")
    after_a=checkpoint(native)
    a_post=score_public(views,"A","VALID_A_POST")
    fit_b=fit_public(arms,"B")
    after_b=checkpoint(native)
    a_retained=score_public(views,"A","DEV_A_RETAINED")
    b_post=score_public(views,"B","VALID_B")
    if any(a.feedback_updates!=2*FIT for a in arms):
        raise AssertionError("NLD02_EQUAL_INFORMATION")
    comparisons={
        "a_gain":a_post["accuracy"][native.name]-pre["accuracy"][native.name],
        "a_after_b_minus_erased":a_retained["accuracy"][native.name]-
              a_retained["accuracy"]["erased-native-state"],
        "a_after_b_minus_a_after_fit":a_retained["accuracy"][native.name]-
              a_post["accuracy"][native.name],
    }
    if any(not x["no_model_updates_on_score"] or x["family_label_given_to_learner"]
           for x in (pre,a_post,a_retained,b_post)):
        raise AssertionError("NLD02_SCORE_INFORMATION_LEAK")
    return {
        "schema":SCHEMA,"original_nld01_parent":"71a31aaa98efa639265baa81ae021c261458aa19",
        "only_reused_development_smoke_seed":seed,
        "original_r9_101_211_307_reused":False,
        "scientific_first_use":False,
        "source_first_use":"PREVIOUSLY_EXPOSED_PUBLIC_R9_SMOKE",
        "native_input_has_family_or_task_identity":False,
        "active_native_cell_banks":1,"active_native_cells":10,
        "public_fitting":[fit_a,fit_b],
        "native_actual_weight_changes":native.weight_changes,
        "feedback_updates_per_arm":{a.name:a.feedback_updates for a in arms},
        "cold_after_a":after_a,"cold_after_b":after_b,
        "checkpoint_bytes_per_arm":{a.name:len(a.save()) for a in arms},
        "views":{"a_pre":pre,"a_post":a_post,"a_after_b":a_retained,"b_post":b_post},
        "contrasts":comparisons,
        "known_source_alias_certificate":alias_certificate(),
        "representation":"OBSERVE_A_GAIN_AND_STATE_DEPENDENCE_SEPARATELY",
        "retention":"REPORT_A_AFTER_B_AND_CONTEXT_ALIAS_SEPARATELY",
        "causal_composition":"NOT_TESTED_HANDDESIGNED_PAIR_FEATURES",
        "unfamiliar_transfer":"NOT_TESTED_ORIGINAL_R9_ZERO_SHOT_NO_GO",
        "native_superiority_over_controls":"NOT_ASSUMED_OR_CLAIMED",
        "matched_per_model_resource_costs":False,
        "ckb_admission":"NOT_OBSERVED",
        "disposition":"NLD02_SHARED_BANK_EXISTING_SOURCE_DEV_DIAGNOSTIC_RETAIN_ALL_RESULTS",
    }


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--smoke",action="store_true",required=True)
    a.parse_args()
    print(json.dumps(run(),sort_keys=True,separators=(",",":"),allow_nan=False))
