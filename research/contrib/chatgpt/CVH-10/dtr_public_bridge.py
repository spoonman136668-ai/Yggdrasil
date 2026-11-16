"""CVH10 distinct-source DTRPCH *public-only* two-stage adapter, source FREE.

Pinned original CausalAILab/Causal-Gymnasium@c94e9a4cd3641588b6b8507e71ccee5c27032bdf
module causal_gym/envs/dtr.py blob 6af2371dce21804140ea141ccb7be14e003ba275.
Original DTRPCH.do first callback(s1); second callback(s1,x1,s2).
First do => (s2,0,False,False,private_info)
Second do => (None,y,True,False,private_info).

Source owner must independently authenticate untouched world seed/first-use and
isolate actor. This module DOES NOT create/import/open or call original source.
It grants NO source first-use permission. It only handles inert arguments a
future separately qualified source owner could pass after genuine actions.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
FKP=HERE.parent/"FKP-24"
CVH02=HERE.parent/"CVH-02"
for path in (FKP,CVH02):
    if str(path) not in sys.path:
        sys.path.insert(0,str(path))
from native_public_mdp import PublicConsequence,_binary
from public_policy import _event

SOURCE_REPO="CausalAILab/Causal-Gymnasium"
SOURCE_SHA="c94e9a4cd3641588b6b8507e71ccee5c27032bdf"
DTR_BLOB="6af2371dce21804140ea141ccb7be14e003ba275"
PUBLIC_FIELDS=tuple(PublicConsequence._fields)
MAX_PHYSICAL_ACTIONS=2
TERMINAL_ABSENT_OBSERVATION_SENTINEL=0


def public_report_digest(rows):
    """Hash solely a completed SIX-field public transcript, no source info."""
    return sha256(json.dumps(
        [list(_event(r)) for r in rows],sort_keys=True,separators=(",",":")
    ).encode("ascii")).hexdigest()


class SourceFreeDTRPublicBridge:
    """Policy-facing grammar adapter. Not an original source runner or lease.

    A *separately authorized* source controller, if ever qualified, may call:
        bridge.accept_reset(original_reset_return)
        env.do(bridge.stage0_action)
        bridge.accept_stage0_result(original_do_return)
        env.do(bridge.stage1_action)
        bridge.accept_stage1_result(original_do_return)
    This class ITSELF NEVER calls env/do/reset. Ambiguous external effects must
    remain pending and MUST NOT be replayed or auto-restarted.
    """
    def __init__(self,policy):
        if not callable(getattr(policy,"choose",None)) or not callable(getattr(policy,"observe",None)):
            raise ValueError("CVH10_PUBLIC_ONLY_CHOOSE_OBSERVE_REQUIRED")
        self.policy=policy
        self.phase="uninitialized"
        self.initial=None
        self.first=None
        self.seen=[]
        self.outstanding=None
        self.callback_calls=0

    def accept_reset(self,source_reset):
        if self.phase!="uninitialized":
            raise PermissionError("CVH10_RESET_REPLAY_OR_UNAUTHORIZED_EPISODE")
        if type(source_reset) not in (tuple,list) or len(source_reset)!=2:
            raise ValueError("CVH10_ORIGINAL_DTR_RESET_SHAPE")
        # source_reset[1] can contain private source metadata. Never touch it.
        self.initial=_binary(source_reset[0],"DTR_S1")
        self.phase="stage0_ready"
        return self.initial

    def stage0_action(self,observed_s1):
        if self.phase!="stage0_ready":
            raise PermissionError("CVH10_STAGE0_ACTION_ALREADY_SELECTED_OR_OUT_OF_ORDER")
        # A bad original source callback may already have consumed source
        # authority: fail CLOSED even if no valid action was returned.
        self.phase="blocked"
        if _binary(observed_s1,"DTR_CALLBACK_S1")!=self.initial:
            raise ValueError("CVH10_SOURCE_STAGE0_PUBLIC_STATE_MISMATCH")
        selected=self.policy.choose(self.initial,tuple())
        if type(selected) is not int or selected not in (0,1):
            raise ValueError("CVH10_POLICY_RETURNED_NONBINARY_ACTION")
        self.outstanding=(self.initial,selected)
        self.callback_calls=1
        self.phase="stage0_pending_unconfirmed"
        return selected

    def accept_stage0_result(self,source_do_result):
        if self.phase!="stage0_pending_unconfirmed" or self.callback_calls!=1:
            raise PermissionError("CVH10_NO_SINGLE_CONFIRMED_STAGE0_SOURCE_ACTION")
        if type(source_do_result) not in (tuple,list) or len(source_do_result)!=5:
            raise ValueError("CVH10_STAGE0_RESULT_SHAPE")
        s2=_binary(source_do_result[0],"DTR_S2")
        reward=_binary(source_do_result[1],"DTR_STAGE0_REWARD")
        term=_binary(source_do_result[2],"DTR_STAGE0_TERMINATED")
        trunc=_binary(source_do_result[3],"DTR_STAGE0_TRUNCATED")
        if reward!=0 or term!=0 or trunc!=0:
            raise ValueError("CVH10_UNEXPECTED_STAGE0_OUTCOME_OR_EARLY_END")
        # source_do_result[4] intentionally never accessed; it may include
        # stage, previous action, hidden confounder and private treatment info.
        row=PublicConsequence(self.initial,self.outstanding[1],0,s2,False,False)
        self.policy.observe(row)
        self.first=row
        self.seen.append(row)
        self.outstanding=None
        self.callback_calls=0
        self.phase="stage1_ready"
        return row

    def stage1_action(self,original_s1,original_x1,observed_s2):
        if self.phase!="stage1_ready" or self.first is None:
            raise PermissionError("CVH10_STAGE1_ACTION_ALREADY_SELECTED_OR_OUT_OF_ORDER")
        self.phase="blocked"
        # DTRPCH's original second do callback supplies s1,x1,s2 (public
        # historical s1,x1 and current observed s2), never exogenous u.
        if (_binary(original_s1,"DTR_STAGE1_ORIGINAL_S1")!=self.first.before or
            _binary(original_x1,"DTR_STAGE1_ORIGINAL_X1")!=self.first.action or
            _binary(observed_s2,"DTR_STAGE1_CURRENT_S2")!=self.first.after):
            raise ValueError("CVH10_STAGE1_SOURCE_CALLBACK_HISTORY_DRIFT")
        action=self.policy.choose(self.first.after,tuple(self.seen))
        if type(action) is not int or action not in (0,1):
            raise ValueError("CVH10_STAGE1_POLICY_NONBINARY_ACTION")
        self.outstanding=(self.first.after,action)
        self.callback_calls=1
        self.phase="stage1_pending_unconfirmed"
        return action

    def accept_stage1_result(self,source_do_result):
        if self.phase!="stage1_pending_unconfirmed" or self.callback_calls!=1:
            raise PermissionError("CVH10_NO_SINGLE_CONFIRMED_STAGE1_SOURCE_ACTION")
        if type(source_do_result) not in (tuple,list) or len(source_do_result)!=5:
            raise ValueError("CVH10_STAGE1_RESULT_SHAPE")
        if source_do_result[0] is not None:
            raise ValueError("CVH10_DTR_TERMINAL_SOURCE_OBSERVATION_MUST_BE_NONE")
        reward=_binary(source_do_result[1],"DTR_TERMINAL_Y")
        term=_binary(source_do_result[2],"DTR_STAGE1_TERMINATED")
        trunc=_binary(source_do_result[3],"DTR_STAGE1_TRUNCATED")
        if term!=1 or trunc!=0:
            raise ValueError("CVH10_NOT_EXACT_TWO_STAGE_ORIGINAL_DTR_TERMINAL")
        # After=0 here is a *terminal sentinel*, NOT an actual observed S2
        # or next state. The termination flag closes the policy episode.
        row=PublicConsequence(self.outstanding[0],self.outstanding[1],reward,
                              TERMINAL_ABSENT_OBSERVATION_SENTINEL,True,False)
        self.policy.observe(row)
        self.seen.append(row)
        self.outstanding=None
        self.callback_calls=0
        self.phase="completed"
        return row

    def completed_public_only_receipt(self):
        if self.phase!="completed" or len(self.seen)!=MAX_PHYSICAL_ACTIONS or self.outstanding is not None:
            raise PermissionError("CVH10_PARTIAL_OR_AMBIGUOUS_SOURCE_EFFECT_NO_RETRY")
        if [_event(r) for r in self.seen][0][4:]!=[False,False] or (
                [_event(r) for r in self.seen][1][4:]!=[True,False]):
            raise ValueError("CVH10_DTR_PUBLIC_TRANSCRIPT_CUSTODY_DRIFT")
        return {
            "schema":"yggdrasil.cvh10.public-DTR-two-step-sourcefree-adapter.v1",
            "source_commit":SOURCE_SHA,
            "source_dtr_blob":DTR_BLOB,
            "source_family":"DTRPCH_DTRSCM",
            "public_stage0_before":self.first.before,
            "public_earned_rewards":[r.reward for r in self.seen],
            "public_action_count":2,
            "source_first_use_owner_verified":False,
            "new_original_source_reset_or_do_by_this_module":0,
            "terminal_after_is_observation":False,
            "terminal_after_placeholder":0,
            "public_transitions_sha256":public_report_digest(tuple(self.seen)),
            "public_transitions":[list(_event(r)) for r in self.seen],
        }


def original_source_authority_preflight():
    prereg=json.loads((HERE/"prereg.json").read_text(encoding="utf-8"))
    deny=json.loads((HERE.parent/"CVH-09"/"result.json").read_text(encoding="utf-8"))
    if (not prereg["future_science"]["user_standing_authorization"]
            or prereg["source"]["blob"]!=DTR_BLOB
            or prereg["future_science"]["source_first_use_approved_to_run_now"] is not False
            or prereg["future_science"]["original_source_owner_lease"] is not None
            or prereg["future_science"]["original_seed_ids_verified"]!=[]
            or deny["physical_original_source_actions_executed"]!=0
            or deny["roster_denied"]["first_use_execution_permitted"] is not False):
        raise PermissionError("CVH10_ORIGINAL_SOURCE_OWNER_FIRST_USE_UNVERIFIED")
    return {
        "schema":"yggdrasil.cvh10.original-DTR-source-owner-admission.v1",
        "owner_qualified_virgin_seeds":0,
        "user_authorized_original_action_ceiling":13312,
        "new_original_DTR_reset_calls":0,
        "new_original_DTR_do_calls":0,
        "first_use_execution_allowed":False,
        "source_code_static_verified_family":"DTRPCH@"+DTR_BLOB,
        "public_adapter_source_qualification_only":True,
        "native_scientific_superiority_verified":False,
    }
