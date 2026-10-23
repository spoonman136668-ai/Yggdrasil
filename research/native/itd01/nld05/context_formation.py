"""NLD-05 source-free DEV: create context slots from public prediction errors.

Input to learner: public phase reset, four sensor Booleans, action and delayed
public success. Never a source task name, private target, future probe answer.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "nld03"))
sys.path.insert(0, str(BASE / "nld04"))
from cued_state import (CueNative, CuePerceptron, CueEpisodic, CUE, FIT,
                        SEED, EVAL, PATTERNS, PublicSource,
                        source_only_correct_action, digest)
from action_cells import DELAY, canonical, check_action
from history_context import PROBES, SCORED

SCHEMA = "itd01.nld05.error-formed-context-slot-dev.v1"
FIT_DIAGNOSTIC = 16
NEW_CONTEXT_ERROR_THRESHOLD = 3
MAX_CONTEXTS = 2
PUBLIC_CODES = (-1, 1)
KNOWN_SOURCE_SHA = {
    "FIT_A": "02b355fcc4caf86e37802d746e45fbd1395920b8d3d594f34a3da55e29ccc463",
    "FIT_B": "7a300dfe9bcb7b8c1222eae4b00a88c46cfd3d72ddefb145e3248f4942d69299",
}


def public_correct(record):
    """Only public chosen action and delayed binary feedback, not hidden targets."""
    if set(record) != {"token", "sensors", "action", "success", "tick", "feedback_tick"}:
        raise ValueError("NLD05_PUBLIC_EVENT_SHAPE")
    if type(record["success"]) is not bool or (
            type(record["tick"]) is not int or
            type(record["feedback_tick"]) is not int or
            record["feedback_tick"] - record["tick"] != DELAY):
        raise ValueError("NLD05_PUBLIC_OUTCOME_OR_DELAY_INVALID")
    check_action(record["action"])
    return record["action"] if record["success"] else 1-record["action"]


class ErrorContextFormer:
    """Hand-coded bounded discrepancy controller, not learned context representation."""
    def __init__(self, disabled_spawning=False):
        if type(disabled_spawning) is not bool:
            raise ValueError("NLD05_SPAWN_SETTING")
        self.codes = []
        self.disabled_spawning = disabled_spawning
        self.history = []

    def form(self, policy, prefix):
        if len(prefix) != FIT_DIAGNOSTIC:
            raise ValueError("NLD05_NEED_EXACT_SIXTEEN_PUBLIC_DIAGNOSTICS")
        if len({r["token"] for r in prefix}) != len(prefix):
            raise ValueError("NLD05_DUPLICATE_PUBLIC_PROBE")
        truth = [public_correct(r) for r in prefix]
        if not self.codes:
            self.codes.append(PUBLIC_CODES[0])
            entry = {"created": True, "code": self.codes[0],
                     "best_prediction_errors": None, "existing_slot_errors": [],
                     "prefix_size": len(prefix),
                     "reason": "NO_PREVIOUS_LEARNED_CONTEXT"}
        else:
            errs = [sum(policy.choose(tuple(r["sensors"]), code) != target
                        for r,target in zip(prefix,truth)) for code in self.codes]
            best_index = min(range(len(errs)), key=lambda i:(errs[i],i))
            best_error = errs[best_index]
            new = (best_error >= NEW_CONTEXT_ERROR_THRESHOLD and
                   not self.disabled_spawning)
            if new and len(self.codes) >= MAX_CONTEXTS:
                raise ValueError("NLD05_CONTEXT_CAPACITY_EXCEEDED")
            if new:
                self.codes.append(PUBLIC_CODES[len(self.codes)])
                selected = self.codes[-1]
            else:
                selected = self.codes[best_index]
            entry = {"created": bool(new), "code": selected,
                     "best_prediction_errors": best_error,
                     "existing_slot_errors": errs,
                     "prefix_size": len(prefix),
                     "reason": ("PREDICTION_ERROR_TRIGGER" if new else
                                "EXISTING_CONTEXT_BEST_MATCH")}
        self.history.append(entry)
        return entry

    def choose_from_public_probes(self, policy, probes):
        if len(probes) != PROBES or not self.codes:
            raise ValueError("NLD05_EXACT_EIGHT_PROBES_AND_DISCOVERED_SLOTS_REQUIRED")
        if len({p["token"] for p in probes}) != PROBES:
            raise ValueError("NLD05_DUPLICATE_EVAL_PROBE")
        correct = [public_correct(p) for p in probes]
        errors = [sum(policy.choose(tuple(p["sensors"]), code) != target
                      for p, target in zip(probes, correct)) for code in self.codes]
        choice = min(range(len(errors)), key=lambda i:(errors[i],i))
        disagreement = (sum(policy.choose(tuple(p["sensors"]), self.codes[0]) !=
                            policy.choose(tuple(p["sensors"]), self.codes[1])
                            for p in probes) if len(self.codes) == 2 else 0)
        return {"selected_slot": self.codes[choice], "slot_prediction_errors": errors,
                "diagnostic_model_disagreements": disagreement,
                "ambiguous_tie": errors.count(min(errors)) > 1,
                "distinct_formed_contexts": len(self.codes),
                "public_delayed_probes": len(probes)}

    def state(self):
        return {"schema": SCHEMA, "codes": self.codes,
                "disabled_spawning": self.disabled_spawning,
                "phase_decisions": self.history,
                "threshold": NEW_CONTEXT_ERROR_THRESHOLD,
                "max_contexts": MAX_CONTEXTS}
    def save(self):
        value=self.state()
        return canonical({"payload": value, "sha256": digest(value)})
    @classmethod
    def restore(cls, blob):
        if type(blob) is not bytes or not 0 < len(blob) < 16384:
            raise ValueError("NLD05_CONTEXT_CHECKPOINT_SIZE")
        try:
            wrapped=json.loads(blob)
            v=wrapped["payload"]
            sig=wrapped["sha256"]
        except (KeyError, ValueError, TypeError):
            raise ValueError("NLD05_CONTEXT_CHECKPOINT_STRUCTURE")
        if (type(wrapped) is not dict or set(wrapped) != {"payload","sha256"} or
                type(v) is not dict or
                set(v) != {"schema","codes","disabled_spawning","phase_decisions",
                           "threshold","max_contexts"} or
                v["schema"] != SCHEMA or
                v["threshold"] != NEW_CONTEXT_ERROR_THRESHOLD or
                v["max_contexts"] != MAX_CONTEXTS or
                v["codes"] not in ([],[-1],[-1,1]) or
                type(v["disabled_spawning"]) is not bool or
                type(v["phase_decisions"]) is not list or
                len(v["phase_decisions"]) > 2 or digest(v) != sig):
            raise ValueError("NLD05_CONTEXT_CHECKPOINT_IDENTITY")
        out=cls(v["disabled_spawning"])
        out.codes=list(v["codes"])
        out.history=list(v["phase_decisions"])
        if out.save()!=blob:
            raise ValueError("NLD05_CONTEXT_CHECKPOINT_NONCANONICAL")
        return out


def source_fit_phase_private(stage):
    """Source names deliberately stay only on private generation side."""
    if stage not in (0, 1):
        raise ValueError("NLD05_ONLY_FROZEN_TWO_SOURCE_PHASES")
    family=("A","B")[stage]
    role="FIT_"+family
    source=PublicSource(SEED,role,family)
    due={}
    records=[]
    source_trace=[]
    delivered=0
    for tick in range(FIT+DELAY):
        for item in due.pop(tick, []):
            # Original immutable trace digest, private, never passed to learner.
            source_trace.append({"token": item["private_token"],
                                 "feedback_tick":tick,"success":item["success"]})
            delivered+=1
        if tick >= FIT: continue
        sensors=source.next_sensors()
        action=(sum(sensors)+tick)%2
        success=bool(action==source_only_correct_action(family,sensors))
        private_token=f"NLD02-R9-SMOKE-{SEED}-{role}-{tick}"
        source_trace.append({"token":private_token,"tick":tick,
                             "sensors":sensors,"action":action})
        record={"token":f"PUBLIC-FEEDBACK-{stage}-{tick}",
                "sensors":list(sensors),"action":action,"success":success,
                "tick":tick,"feedback_tick":tick+DELAY}
        records.append(record)
        due.setdefault(tick+DELAY,[]).append(
            {"private_token":private_token,"success":success})
    digest_original=digest(source_trace)
    if (due or source.calls!=FIT or delivered!=FIT or
            digest_original!=KNOWN_SOURCE_SHA[role]):
        raise AssertionError("NLD05_ORIGINAL_SOURCE_CUSTODY_DRIFT")
    return records,{"source_role_private_only":role,"original_source_sha256":digest_original,
                    "legal_public_actions":FIT,"delayed_public_outcomes":delivered}


def replay_public(model, records, slot):
    """Buffered phase: original feedback order, no task name sent to model."""
    due={}
    for tick in range(FIT+DELAY):
        for item in due.pop(tick,[]):
            model.learn_delayed(item["token"],item["success"],tick)
        if tick >= FIT:continue
        item=records[tick]
        public_correct(item)
        model.observe_public_action(item["token"],tuple(item["sensors"]),slot,
                                    item["action"],tick)
        due.setdefault(item["feedback_tick"],[]).append(item)
    if due or model.pending:
        raise AssertionError("NLD05_REPLAY_FEEDBACK_NOT_DRAINED")


def source_eval_private(stage):
    if stage not in (0,1):
        raise ValueError("NLD05_PROTECTED_EVALUATION_ROLE_DENIED")
    family=("A","B")[stage]
    role=("DEV_A_RETAINED","VALID_B")[stage]
    source=PublicSource(SEED,role,family)
    due={}
    public=[]
    for tick in range(PROBES+DELAY):
        public.extend(due.pop(tick,[]))
        if tick>=PROBES:continue
        sensors=source.next_sensors()
        action=(sum(sensors)+tick)%2
        success=bool(action==source_only_correct_action(family,sensors))
        due.setdefault(tick+DELAY,[]).append(
            {"token":f"EVAL-PUBLIC-{stage}-{tick}",
             "sensors":list(sensors),"action":action,"success":success,
             "tick":tick,"feedback_tick":tick+DELAY})
    if due or len(public)!=PROBES:
        raise AssertionError("NLD05_PUBLIC_EVAL_CAUSALITY")
    scoring=[source.next_sensors() for _ in range(SCORED)]
    # Truth retained only by evaluator; not given to router/models.
    private_targets=[source_only_correct_action(family,s) for s in scoring]
    if source.calls!=EVAL:
        raise AssertionError("NLD05_EXCEEDS_ORIGINAL_DEV_ROLE_BUDGET")
    return public,scoring,private_targets


def verify_checkpoint(model,router):
    policy_blob=model.save()
    router_blob=router.save()
    model_copy=CueNative.restore(policy_blob)
    router_copy=ErrorContextFormer.restore(router_blob)
    if router_copy.save()!=router_blob:
        raise AssertionError("NLD05_ROUTER_COLD_MISMATCH")
    for cue in PUBLIC_CODES:
        for sensors in PATTERNS:
            if model.choose(sensors,cue)!=model_copy.choose(sensors,cue):
                raise AssertionError("NLD05_LEARNED_STATE_COLD_MISMATCH")
    return {"policy_sha256":hashlib.sha256(policy_blob).hexdigest(),
            "policy_bytes":len(policy_blob),
            "context_sha256":hashlib.sha256(router_blob).hexdigest(),
            "context_bytes":len(router_blob),"cold_predictions_checked":32}


def run(seed=SEED):
    if type(seed) is not int or seed!=SEED:
        raise ValueError("NLD05_PREVIOUSLY_EXPOSED_DEV_SEED_3_ONLY")
    native=CueNative(True)
    percept=CuePerceptron(True)
    episod=CueEpisodic(True)
    no_spawn=CueNative(True)
    oracle=CueNative(True)
    participants=[("native_dynamic",native,ErrorContextFormer()),
                  ("perceptron_dynamic",percept,ErrorContextFormer()),
                  ("episodic_dynamic",episod,ErrorContextFormer()),
                  ("native_no_new_slot",no_spawn,ErrorContextFormer(disabled_spawning=True))]
    source_records=[]
    for stage in range(2):
        events,receipt=source_fit_phase_private(stage)
        source_records.append(receipt)
        for _,model,route in participants:
            decision=route.form(model,events[:FIT_DIAGNOSTIC])
            replay_public(model,events,decision["code"])
        # Privileged known-family cue uses same public source without extra draws.
        replay_public(oracle,events,PUBLIC_CODES[stage])
    if any(m.feedback_updates!=2*FIT for _,m,_ in participants) or (
            oracle.feedback_updates!=2*FIT):
        raise AssertionError("NLD05_EQUAL_TRAINING_FEEDBACK")
    cold=verify_checkpoint(native,participants[0][2])
    comparisons={}
    for stage in range(2):
        public,scoring,targets=source_eval_private(stage)
        models_saved={name:(m.save(),route.save()) for name,m,route in participants}
        decisions={}
        predictions={}
        for name,model,route in participants:
            selected=route.choose_from_public_probes(model,public)
            selected_slot=selected["selected_slot"]
            num=sum(model.choose(s,selected_slot)==target
                    for s,target in zip(scoring,targets))
            decisions[name]=selected
            predictions[name]=num
        predictions["oracle_known_source_context"]=sum(
            oracle.choose(s,PUBLIC_CODES[stage])==target
            for s,target in zip(scoring,targets))
        if any(m.save()!=models_saved[name][0] or
               route.save()!=models_saved[name][1]
               for name,m,route in participants):
            raise AssertionError("NLD05_NO_SCORING_OR_DIAGNOSTIC_TRAINING")
        comparisons["stage_"+str(stage)]={
            "private_source_identity_for_audit_only":("A","B")[stage],
            "public_unscored_probes":PROBES,
            "public_scored_steps":SCORED,
            "public_delayed_history_sha256":digest(public),
            "context_decisions":decisions,
            "correct_scored_of_56":predictions,
            "true_slot_used_only_for_oracle_and_private_audit":PUBLIC_CODES[stage],
        }
    formed=participants[0][2]
    return {
        "schema":SCHEMA,
        "original_nld04_head":"2b11b0156afb516ef7b52e411aae6a82921344d7",
        "already_exposed_public_R9_seed":SEED,
        "protected_first_use":False,
        "original_frozen_r9_101_211_307_run":False,
        "public_unlabeled_phase_resets":2,
        "source_fit_receipts":source_records,
        "public_fit_feedback_per_model":{name:m.feedback_updates for name,m,_ in participants},
        "public_fit_feedback_privileged_oracle":oracle.feedback_updates,
        "phase_formation":{name:route.history for name,_,route in participants},
        "native_context_slot_count":len(formed.codes),
        "native_slot_names_generated_from_prediction_error_only":True,
        "native_two_slot_cap_prospectively_frozen":MAX_CONTEXTS,
        "formation_diagnostic_outcome_cost_each_phase":FIT_DIAGNOSTIC,
        "formation_offline_buffered_phase":True,
        "eval_unscored_probe_cost_each_role":PROBES,
        "native_checkpoint":cold,
        "saved_model_and_context_bytes":{
            name:len(m.save())+len(route.save()) for name,m,route in participants},
        "evaluation":comparisons,
        "representation":"CONTEXT_SLOT_RULE_HANDCODED_POLICY_PREDICTIONS_LEARNED",
        "retention":"REPORT_A_AFTER_B_AND_NO_SLOT_ABLATION",
        "causal_composition":"NOT_TESTED_PREDEFINED_FEATURE_MAP_TWO_SLOT_LIMIT",
        "unfamiliar_transfer":"NOT_TESTED_R9_ZERO_SHOT_NO_GO_PRESERVED",
        "native_better_than_trained_conventional":"NOT_PRESUMED",
        "per_model_cpu_rss_parity":False,
        "authenticated_ckb_scientific_admission":"NOT_OBSERVED",
        "disposition":"NLD05_REUSED_PUBLIC_DEV_ERROR_FORMED_CONTEXT_RECORD_ALL_NEGATIVES",
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--smoke",action="store_true",required=True)
    parser.parse_args()
    print(json.dumps(run(),sort_keys=True,separators=(",",":"),allow_nan=False))
