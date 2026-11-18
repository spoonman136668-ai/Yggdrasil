"""WSP169: immutable read-only pre-original-source scientific-admission audit.

This is NOT an original-world experiment, first-use actor, policy,
scheduler, runner, lease mint, source oracle, or research promotion route.

Only five ALREADY EXPOSED metadata/report JSON Git blobs are permitted. No
simulator source, privileged world state, original held targets or cohort
rows are read. The audit CAN ONLY DENY admission to the historical record;
future independent owner evidence needs the existing source owner route.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[4]
PINNED=(
  ("cvh09","07b213891dc6424b9ea1aa685b0ff77014f49080",
   "research/contrib/chatgpt/CVH-09/result.json",
   "c08acf08f11960e9183d4d42b97a684df14eac01",
   "yggdrasil.cvh09.owner-preflight-and-analytic-headroom.v1"),
  ("cvh10","6dc08b3b8180301116e6162f414e043a7d418623",
   "research/contrib/chatgpt/CVH-10/result.json",
   "c95062c0115259feefe59e9a6db9c98bc69f4b73",
   "yggdrasil.cvh10.real-upstream-dtr-public-two-stage-sourcefree-qualification.v1"),
  ("ckad16","08fbe556d7ac134d3662f7003af5bc4430013ac1",
   "research/contrib/chatgpt/CKAD-16/provenance.json",
   "c79c47ecb42279ee9ec3121e6bea68a8fff0676b",
   "yggdrasil.ckad16.provenance.v1"),
  ("ckad20","08fbe556d7ac134d3662f7003af5bc4430013ac1",
   "research/contrib/chatgpt/CKAD-20/result.json",
   "a98e2e4cb17b41ab380c1fa30169151315e87d56",
   "yggdrasil.ckad20.shared-episode-development.result.v1"),
  ("wsp158","ebd094153976878b0408b72739288a53e23599c2",
   "research/contrib/chatgpt/WSP-158/result.json",
   "2ffbd7b811c0cd0a3d2a8851090d5dbb6b65e5c4",
   "wsp158.original-consumed-public-DTR-stage-calibration-develop-result.v1")
)
AUDIT_SCHEMA="yggdrasil.wsp169.historical-source-admission-denied.v1"
SOURCE="CausalAILab/Causal-Gymnasium"
SOURCE_SHA="c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
EXPECTED_DTR_RUN=39932201242
APPROVED_BUT_CONDITIONAL_BUDGET=13312
USED_DTR_EPISODES=768
EXPECTED_BRIER_GAIN=.000081809767
EXPECTED_FROZEN_GAIN=.005


def _git(*args):
    try:
        result=subprocess.run(["git",*args],cwd=ROOT,check=True,
                              timeout=15,capture_output=True)
    except (OSError,subprocess.SubprocessError) as exc:
        raise ValueError("WSP169_PINNED_GIT_UNAVAILABLE") from exc
    return result.stdout


def load_pinned_records():
    """No branch aliases, remote URLs, new data, or arbitrary paths."""
    result={}
    for key,commit,path,blob,schema in PINNED:
        name=(commit+":"+path)
        actual=_git("rev-parse","--verify",name).strip().decode("ascii")
        if actual!=blob:
            raise ValueError("WSP169_PINNED_BLOB_MISMATCH")
        raw=_git("show",name)
        if len(raw)>2_000_000:
            raise ValueError("WSP169_OVERSIZE_REPORT")
        try:
            record=json.loads(raw)
        except (UnicodeError,ValueError) as exc:
            raise ValueError("WSP169_INVALID_JSON") from exc
        if type(record) is not dict or record.get("schema")!=schema:
            raise ValueError("WSP169_SCHEMA_DRIFT")
        result[key]=record
    return result


def _expect(condition, label):
    if not condition:
        raise ValueError("WSP169_HISTORICAL_EVIDENCE_DRIFT:"+label)


def _exact_false(value):
    return value is False


def _exact_zero(value):
    return type(value) is int and value==0


def _strict_float(x):
    _expect(type(x) in (float,int) and math.isfinite(x),"metric_type")
    return float(x)


def audit_historical_admission(records):
    """Deny-only. No field of records can grant owner/source first use.

    Historical owner denial and known prior exposed DTR runs are independent
    source-of-truth blockers. An apparent replacement approval is evidence
    drift, never automatic reauthorization. All claims in this audit are
    anchored to the immutable Git SHA/blob set in PINNED.
    """
    _expect(type(records) is dict and set(records)==set(k for k,*_ in PINN),
            "report_set")
    r=copy.deepcopy(records)
    for key,_,_,_,schema in PINNED:
        _expect(type(r[key]) is dict and r[key].get("schema")==schema,
                key+"_schema")

    cvh09=r["cvh09"]
    h=cvh09.get("headroom")
    roster=cvh09.get("roster_denied")
    _expect(type(h) is dict and type(roster) is dict,"cvh09_shapes")
    _expect(cvh09.get("source_original_firstuse")==
            "BLOCKED_NO_OWNER_QUALIFIED_VIRGIN_COHORT","owner_denial")
    _expect(cvh09.get("approved_action_ceiling")==
            APPROVED_BUT_CONDITIONAL_BUDGET,"approved_ceiling")
    _expect(_exact_zero(cvh09.get("physical_original_source_actions_executed")),
            "cvh09_no_original_source_actions")
    _expect(_exact_false(roster.get("owner_signature_qualified")),
            "owner_signature_absent")
    _expect(roster.get("independent_owner_lease") is None,"lease_absent")
    _expect(_exact_false(roster.get("source_effect_journal_verified")),
            "journal_absent")
    _expect(roster.get("original_source_one_shot_runner_id") is None,
            "one_shot_actor_absent")
    _expect(roster.get("train_seeds")==[],"no_train_roster")
    _expect(type(roster.get("held_seeds_by_arm")) is dict and
            all(v==[] for v in roster["held_seeds_by_arm"].values()) and
            len(roster["held_seeds_by_arm"])==4,"no_held_roster")
    _expect(type(roster.get("transfer_seeds_by_arm")) is dict and
            all(v==[] for v in roster["transfer_seeds_by_arm"].values()) and
            len(roster["transfer_seeds_by_arm"])==4,"no_transfer_roster")
    _expect(_exact_false(h.get("same_mdppch_seed_transfer_is_unfamiliar_family")),
            "same_mdppch_is_not_novel_family")
    _expect(h.get("optimal_reward_per_source_do")=="41/50","mdp_reward_bound")

    cvh10=r["cvh10"]
    owner=cvh10.get("source_owner_firstuse_authority")
    _expect(type(owner) is dict,"cvh10_owner")
    _expect(cvh10.get("original_source_commit")==SOURCE_SHA,
            "CVH10_source_identity")
    _expect(_exact_false(owner.get("first_use_execution_allowed")),
            "CVH10_firstuse_denied")
    _expect(_exact_zero(owner.get("owner_qualified_virgin_seeds")),
            "CVH10_virgin_cohort_absent")
    _expect(owner.get("user_authorized_original_action_ceiling")==
            APPROVED_BUT_CONDITIONAL_BUDGET,"CVH10_ceiling_parity")
    _expect(_exact_zero(cvh10.get("new_original_source_construct_reset_or_do_calls")),
            "CVH10_source_actions")
    _expect(_exact_zero(cvh10.get("original_source_seeds_reserved")),
            "CVH10_no_seeds_reserved")
    _expect(_exact_zero(cvh10.get("original_DTR_observations_train_held_transfer")),
            "CVH10_no_new_dtr_exposure")
    _expect(_exact_false(cvh10.get("scientific_pass")),
            "CVH10_no_scientific_pass")

    ckad16=r["ckad16"]
    _expect(ckad16.get("original_run")==EXPECTED_DTR_RUN,
            "DTR_original_receipt_id")
    _expect(ckad16.get("original_artifact")==12492506361,"DTR_original_artifact")
    _expect(ckad16.get("original_zip_sha256")==
            "ada547777ba2ba49070fe2606ac99c8d9248532f1cb16c8a0f8eab0f4001508c",
            "DTR_original_archive_custody")
    _expect(_exact_false(ckad16.get("scientific_pass")) and
            _exact_false(ckad16.get("accepted_native")),
            "ckad16_source_is_retrospective")

    wsp=r["wsp158"]
    source=wsp.get("source")
    scores=wsp.get("result")
    _expect(type(source) is dict and type(scores) is dict,
            "wsp158_source_and_scores")
    _expect(source.get("original_source_commit")==SOURCE_SHA,
            "WSP158_same_original_source")
    _expect(source.get("original_dtr02_run")==EXPECTED_DTR_RUN,
            "WSP158_same_consumed_original_run")
    _expect(source.get("episodes")==USED_DTR_EPISODES,
            "WSP158_exposed_episode_count")
    _expect(_exact_false(source.get("virgin")) and
            _exact_zero(source.get("new_original_do")),
            "WSP158_not_virgin")
    native=_strict_float(scores["pooled_Brier"]["native_programmed"]["pooled"])
    independent=_strict_float(
        scores["pooled_Brier"]["independent_fitted_same_calibration"]["pooled"])
    mle=_strict_float(scores["pooled_Brier"]["fully_fitted_saturated_MLE"]["pooled"])
    gain=_strict_float(scores.get("gain_over_MLE_absolute"))
    target=_strict_float(scores.get("frozen_minimum_gain_vs_MLE"))
    _expect(native==independent,"WSP158_ties_independent_control")
    _expect(abs((mle-native)-gain)<1e-11,
            "WSP158_metric_difference")
    _expect(abs(gain-EXPECTED_BRIER_GAIN)<1e-12 and
            abs(target-EXPECTED_FROZEN_GAIN)<1e-12 and
            gain<target,"WSP158_no_strong_control_headroom")
    _expect(_exact_false(wsp.get("scientific",{}).get("scientific_pass",False)),
            "WSP158_not_scientifically_qualified")

    ckad20=r["ckad20"]
    _expect(ckad20.get("classification")=="DEVELOPMENT_NO_GO",
            "CKAD20_negative")
    gates=ckad20.get("development_gates")
    _expect(type(gates) is dict and len(gates)==3 and
            all(_exact_false(v) for v in gates.values()),
            "CKAD20_three_failure_gates")
    _expect(_exact_zero(ckad20.get("scope",{}).get("original_source_actions")),
            "CKAD20_original_action_zero")
    _expect(_exact_false(ckad20.get("scientific_pass")),
            "CKAD20_no_scientific_pass")

    pinned_refs=[{"key":key,"commit":commit,"blob":blob}
                 for key,commit,_,blob,_ in PINNED]
    return {
        "schema":AUDIT_SCHEMA,
        "classification":"FIRST_USE_DENIED_HISTORICAL_READONLY",
        "first_use_execution_allowed":False,
        "scientific_pass":False,
        "deployment":"NONE",
        "original_source_actions_this_gate":0,
        "owner_signature_verified":False,
        "independent_source_lease_verified":False,
        "virgin_train_held_transfer_cohorts_verified":False,
        "qualified_one_shot_actor_and_effect_journal_verified":False,
        "approved_but_unspent_conditional_source_action_ceiling":
            APPROVED_BUT_CONDITIONAL_BUDGET,
        "same_law_MDP_new_seeds_count_as_unfamiliar":False,
        "previously_consumed_original_dtr_episodes":USED_DTR_EPISODES,
        "original_dtr_run":EXPECTED_DTR_RUN,
        "DTR_native_pooled_Brier":native,
        "DTR_independent_same_fit_Brier":independent,
        "DTR_fully_fit_MLE_pooled_Brier":mle,
        "DTR_native_gain_over_MLE":gain,
        "DTR_frozen_required_gain":target,
        "DTR_fraction_of_required_gain":gain/target,
        "CKAD20_passed_development_gates":0,
        "CKAD20_total_development_gates":len(gates),
        "pinned_evidence":pinned_refs,
        "admission_next_source_owner_step":
            "An independent original source owner must authenticate a genuinely virgin new-family cohort, disjoint train/held/transfer roster, source-code identity, qualified one-shot actor and durable no-replay effects journal. Validate against owner-native policy before any protected original source call.",
        "historical_scope_note":
            "A read-only historical denial does not determine the state of a future owner-issued lease; reverify LIVE owner/source authority separately. This audit can NEVER authorize an original action."
    }


def main():
    result=audit_historical_admission(load_pinned_records())
    print("WSP169_ORIGINAL_SOURCE_ADMISSION_AUDIT="+
          json.dumps(result,sort_keys=True,separators=(",",":")))
    if result["first_use_execution_allowed"] or result["scientific_pass"]:
        raise RuntimeError("WSP169_NO_FIRSTUSE_PERMITTED")


if __name__=="__main__":
    main()
