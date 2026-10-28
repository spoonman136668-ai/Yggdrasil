"""V35 opt-in action-conditioned local ring features, source-only engineering.

Same original 163 V22 locally learned scalars, same original 8-cell ring,
four-hop return-credit and optimizer. No original native code edited or new
trainable parameters. Action-conditioned feature basis is externally fixed,
not evidence of learned native action identities.
"""
import hashlib
import json

from .itd02_v17_neighbor_carried_learner_dev import ACTIONS, canonical
from .itd02_v22_shared_context_ring_dev import (
    SharedContextRingDev, CELLS, HEAD_FEATURES, LEARNED_SCALARS,
)

SCHEMA="ygg.itd02.v35.action_conditioned_ring.source_only.v1"
BASIS_RULE="interaction_gain=0.25+6.0*existing_original_four_hop_action_credit"
CHECKPOINT_MAX=12288
assert CELLS==8 and HEAD_FEATURES==20 and LEARNED_SCALARS==163


class LocalActionConditionedRingDev(SharedContextRingDev):
    """Original V22 cell weights, changed fixed public-action-local feature basis."""

    def __init__(self):
        super().__init__(mode="shared")
        self._output_action=None

    def _features(self):
        original=super()._features()
        action=self._output_action
        if action is None:
            return original
        if type(action) is not str or action not in ACTIONS:
            raise ValueError("V35_INVALID_PROSPECTIVE_ACTION")
        # Original original ring reverse credit, from the actual public
        # candidate second-action output site, not a hand-coded world label.
        credit=self._coefficients(action)
        assert len(credit)==8
        result=[]
        for cell,row in enumerate(original):
            assert len(row)==20
            gain=0.25+6.0*credit[cell]
            result.append(list(row[:8])+[gain*x for x in row[8:]])
        return result

    def score(self,action):
        old=self._output_action
        self._output_action=action
        try:
            return super().score(action)
        finally:
            self._output_action=old

    def accept_second(self,selected,public_reward,*,learning=True,terminal=True):
        old=self._output_action
        self._output_action=selected
        try:
            return super().accept_second(selected,public_reward,
                                         learning=learning,terminal=terminal)
        finally:
            self._output_action=old

    def checkpoint(self):
        if self._output_action is not None:
            raise ValueError("V35_ACTIVE_SCORE_BOUNDARY_NOT_SERIALIZABLE")
        native=json.loads(super().checkpoint())
        body={"schema":SCHEMA,"basis_rule":BASIS_RULE,"native_v22":native}
        raw=canonical(body)
        envelope=canonical({"body":body,"sha256":hashlib.sha256(raw).hexdigest()})
        if len(envelope)>CHECKPOINT_MAX:
            raise ValueError("V35_CHECKPOINT_OVER_BOUND")
        return envelope

    @classmethod
    def restore(cls,data):
        try:
            if type(data) is not bytes or not 0<len(data)<=CHECKPOINT_MAX:
                raise ValueError("V35_INVALID_LENGTH")
            packet=json.loads(data)
            if type(packet) is not dict or set(packet)!={"body","sha256"}:
                raise ValueError("V35_INVALID_ENVELOPE")
            body=packet["body"]
            if (type(body) is not dict or set(body)!={"schema","basis_rule","native_v22"}
                    or body["schema"]!=SCHEMA or body["basis_rule"]!=BASIS_RULE
                    or type(packet["sha256"]) is not str
                    or hashlib.sha256(canonical(body)).hexdigest()!=packet["sha256"]):
                raise ValueError("V35_INVALID_BASIS_SIGNATURE")
            original=SharedContextRingDev.restore(canonical(body["native_v22"]))
            if original.mode!="shared":
                raise ValueError("V35_FORBIDS_PARTITION_UNDER_WRAPPER")
            obj=cls.__new__(cls)
            obj.__dict__.update(original.__dict__)
            obj._output_action=None
            if obj.checkpoint()!=data:
                raise ValueError("V35_NONCANONICAL_CHECKPOINT")
            return obj
        except (ValueError,TypeError,KeyError,AttributeError,OverflowError) as exc:
            raise ValueError("UNTRUSTED_V35_ACTION_CONDITIONED_CHECKPOINT") from exc
