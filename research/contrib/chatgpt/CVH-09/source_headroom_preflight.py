"""CVH09 pinned original-source mechanism headroom and future cohort safety.

No causal_gym imports, constructor, reset/do, source action, or learner
updates. Analysis is a mathematical audit of publicly inspectable upstream
code, *not* secret source physics passed into a policy.
"""
from __future__ import annotations
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ORIGINAL_SHA="c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
MDP_BLOB_SHA="6264ec5450754c009e98c3e85f6d5927ece0a9ab"
UPSTREAM="CausalAILab/Causal-Gymnasium"
MAX_DO=13312
ARMS=("native","fourcell","recurrent","explorer")
KNOWN_CONSUMED=frozenset([996100,996101,996102,996103])
PROTECTED=tuple(range(996500,996532))+tuple(range(996600,996664))


def _canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),
                      allow_nan=False,ensure_ascii=True).encode("ascii")


def exact_public_source_expected_reward(state,action):
    """Enumerate original MDPSCM.step reward law and pinned exogenous odds.

    Original source: y = ((s != x) != u1) != u3;
       u1 ~ Bern(0.9), u3 ~ Bern(0.1), independent;
    u2 only changes NEXT state. Neither any source do nor a transcript replay.
    """
    if type(state) is not int or state not in (0,1) or type(action) is not int or action not in (0,1):
        raise ValueError("CVH09_EXPECTED_REWARD_BINARY_STATE_ACTION_ONLY")
    probs1=(Fraction(1,10),Fraction(9,10))
    probs3=(Fraction(9,10),Fraction(1,10))
    prob=Fraction(0,1)
    for u1 in (0,1):
        for u3 in (0,1):
            y=int(bool((state != action) != bool(u1)) != bool(u3))
            prob+=probs1[u1]*probs3[u3]*y
    return prob


def theoretical_headroom():
    expected={(s,a):exact_public_source_expected_reward(s,a)
              for s in (0,1) for a in (0,1)}
    correct=expected[(0,0)]
    wrong=expected[(0,1)]
    if not (correct==expected[(1,1)]==Fraction(41,50) and
            wrong==expected[(1,0)]==Fraction(9,50)):
        raise AssertionError("CVH09_ORIGINAL_PINNED_REWARD_DERIVATION_DRIFT")
    target=Fraction(1,20)
    result={
        "schema":"yggdrasil.cvh09.static-original-mdp-analytic-headroom.v1",
        "upstream_repo":UPSTREAM,"upstream_commit":ORIGINAL_SHA,
        "source_git_blob_sha":MDP_BLOB_SHA,
        "source_module":"causal_gym/envs/mdp.py",
        "p_u1_1":"9/10","p_u3_1":"1/10",
        "reward_boolean_equation":"((state != action) != u1) != u3",
        "reward_when_action_equals_state":"41/50",
        "reward_when_action_differs_from_state":"9/50",
        "optimal_action_public_rule":"action = observed_binary_state",
        "optimal_reward_per_source_do":"41/50",
        "frozen_native_reward_gain_target":"1/20",
        "best_control_ceiling_for_native_to_win_at_frozen_threshold":"77/100",
        "exact_per_step_expected_reward_limit":"41/50",
        "source_initial_distribution_changes_law":False,
        "distinct_original_mdp_random_seed_alters_causal_equations":False,
        "same_mdppch_seed_transfer_is_unfamiliar_family":False,
        "source_first_use_actions_here":0,
        "scientific_result":"PROSPECTIVE_MDP_ONLY_UNFAMILIAR_FAMILY_TRANSFER_NOT_IDENTIFIABLE",
        "scientific_pass":False,
        "deployment":False
    }
    result["digest_sha256"]=sha256(_canonical(result)).hexdigest()
    return result


def blank_owner_cohort():
    """No numerical seed reservation or counterfeit authority is created."""
    return {
        "schema":"yggdrasil.cvh09.first-use-owner-roster-UNVERIFIED.v1",
        "status":"SOURCE_FIRST_USE_DENIED_NO_AUTHENTICATED_OWNER_COHORT",
        "user_authorized_cap":13312,
        "user_scope_approved":True,
        "original_source_sha":ORIGINAL_SHA,
        "independent_owner_lease":None,
        "owner_signature_qualified":False,
        "independent_source_ledger_sha":None,
        "transfer_family_original_blob_sha":None,
        "transfer_family_verified_distinct_from_mdppch":False,
        "train_seeds":[],
        "held_seeds_by_arm":{a:[] for a in ARMS},
        "transfer_seeds_by_arm":{a:[] for a in ARMS},
        "real_source_train_events_captured":0,
        "real_original_interventions_executed":0,
        "original_source_one_shot_runner_id":None,
        "source_effect_journal_verified":False,
        "first_use_execution_permitted":False
    }


def audit_future_seed_shapes(roster):
    """Only a STRUCTURAL preflight; never turns a file into owner approval.

    A future owner must authenticate both source seed first-use and family
    provenance *outside* this data-only function. Fake contents are untrusted.
    """
    if type(roster) is not dict or set(roster)!={"train","held","transfer","held_family","transfer_family"}:
        raise ValueError("CVH09_ROSTER_STRICT_SHAPE")
    held,transfer=roster["held"],roster["transfer"]
    if (type(held) is not dict or type(transfer) is not dict or
            set(held)!=set(ARMS) or set(transfer)!=set(ARMS) or
            type(roster["held_family"]) is not str or
            type(roster["transfer_family"]) is not str or
            not roster["held_family"] or not roster["transfer_family"]):
        raise ValueError("CVH09_ROSTER_ARM_FAMILY_SHAPE")
    all_groups=[("train",roster["train"],64)]+[
        ("held:"+a,held[a],64) for a in ARMS]+[
        ("transfer:"+a,transfer[a],24) for a in ARMS]
    seen=set()
    for name,group,n in all_groups:
        if type(group) is not list or len(group)!=n:
            raise ValueError("CVH09_ROSTER_WRONG_COHORT_SIZE:"+name)
        for value in group:
            if type(value) is not int or value<0 or value>2**63-1:
                raise ValueError("CVH09_ROSTER_SEED_NOT_BOUNDED_INTEGER")
            if value in seen:
                raise ValueError("CVH09_ROSTER_DUPLICATE_SEED")
            if value in KNOWN_CONSUMED or value in PROTECTED:
                raise PermissionError("CVH09_PROTECTED_OR_CONSUMED_FIRST_USE")
            seen.add(value)
    if roster["held_family"]==roster["transfer_family"]:
        raise ValueError("CVH09_SAME_FAMILY_IS_NOT_UNFAMILIAR_TRANSFER")
    if len(seen)!=416 or len(seen)*32!=MAX_DO:
        raise AssertionError("CVH09_MAXIMUM_PHYSICAL_ACTION_CEILING_DRIFT")
    return {
        "structurally_distinct_seed_count":len(seen),
        "physical_actions_reserved_MAX_ONLY":MAX_DO,
        "source_original_seed_virginity_VERIFIED":False,
        "source_owner_approval_VERIFIED":False,
        "family_transference_VERIFIED":False,
        "real_source_first_use_PERMITTED":False,
    }


def preflight():
    data=blank_owner_cohort()
    prereg=json.loads((HERE/"prereg.json").read_text(encoding="utf-8"))
    if (prereg["user_authorization"]["maximum_original_physical_do"]!=MAX_DO
            or prereg["required_source_custody"]["original_owner_lease_ref"] is not None
            or prereg["required_source_custody"]["owner_actor_qualified"] is not False
            or prereg["current_gate"]["first_use_permitted_now"] is not False
            or prereg["current_gate"]["science_action_run"] is not False
            or data["first_use_execution_permitted"] or
            data["real_original_interventions_executed"] or
            any(data["held_seeds_by_arm"].values()) or
            any(data["transfer_seeds_by_arm"].values())):
        raise PermissionError("CVH09_APPROVAL_HAS_NO_OWNER_FIRST_USE_LEASE")
    record={"schema":"yggdrasil.cvh09.owner-preflight-and-analytic-headroom.v1",
            "source_original_firstuse":"BLOCKED_NO_OWNER_QUALIFIED_VIRGIN_COHORT",
            "approved_action_ceiling":MAX_DO,
            "physical_original_source_actions_executed":0,
            "approved_user_scope_but_owner_rights_unverified":True,
            "source_family_transfer_not_achievable_by_mdppch_seed_changes":True,
            "headroom":theoretical_headroom(),
            "roster_denied":data,
            "scientific_pass":False,"native_promoted":False,"deployment":False}
    record["digest_sha256"]=sha256(_canonical(record)).hexdigest()
    return record


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-json",required=True)
    args=parser.parse_args()
    report=preflight()
    dest=Path(args.output_json)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("CVH09_SOURCE_FIRSTUSE_PREFLIGHT="+json.dumps({
        "status":report["source_original_firstuse"],
        "max_budget":report["approved_action_ceiling"],
        "actual_source_actions":0,
        "source_analytic_reward_ceiling":report["headroom"]["optimal_reward_per_source_do"],
        "source_seed_only_transfer":False,
        "sha":report["digest_sha256"]
    },sort_keys=True,separators=(",",":")),flush=True)
