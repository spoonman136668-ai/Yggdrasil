"""V37 opt-in public-residual pairwise credit on ORIGINAL eight-cell V22 ring.

This is an externally designed scalar learning rule, not native learned
identity or verified unselected-action reward. All target weights reside
only in the original 163 V22 weights/biases and are updated from one actually
selected public terminal reward and public endogenous rival predictions.
"""
import hashlib
import json
from .itd02_v17_neighbor_carried_learner_dev import ACTIONS,canonical
from .itd02_v18_intermediate_plasticity_dev import _valid_finite,REWARD_LIMITS
from .itd02_v22_shared_context_ring_dev import (
    SharedContextRingDev,LEARNED_SCALARS,HEAD_FEATURES,CELLS,
    EDGE_SIGNAL_PER_PASS,WEIGHT_BOUND
)

SCHEMA="ygg.itd02.v37.public_pairwise_credit.source_only.v1"
MARGIN=0.25
STEP_RATE=0.30
MAX_REWARD_GAP=1.5
MAX_CHECKPOINT=12288
assert LEARNED_SCALARS==163 and HEAD_FEATURES==20 and CELLS==8


class PublicPairwiseCreditRingDev(SharedContextRingDev):
    def __init__(self):
        super().__init__(mode="shared")
        self.margin_updates=0
        self.margin_edge_messages=0
        self.margin_frozen_sha=None

    def _metadata_sha(self):
        return hashlib.sha256(canonical({
            "margin_updates":self.margin_updates,
            "margin_edge_messages":self.margin_edge_messages,
        })).hexdigest()

    def _check_frozen(self):
        super()._check_frozen()
        if (getattr(self,"margin_frozen_sha",None) is not None and
            self._metadata_sha()!=self.margin_frozen_sha):
            raise ValueError("V37_FROZEN_MARGIN_METADATA_CHANGED")

    def accept_second(self,selected,public_reward,*,learning=True,terminal=True):
        self._check_frozen()
        if type(selected) is not str or selected not in ACTIONS:
            raise ValueError("V37_INVALID_SELECTED_PUBLIC_SECOND")
        if not _valid_finite(public_reward,*REWARD_LIMITS):
            raise ValueError("V37_INVALID_SELECTED_TERMINAL_REWARD")
        if type(learning) is not bool or type(terminal) is not bool or not terminal:
            raise ValueError("V37_ILLEGAL_PUBLIC_TERMINAL")
        if self.cue is None or self.first is None:
            raise ValueError("V37_MISSING_ACTUAL_PUBLIC_FIRST")
        if learning and self.frozen_sha is not None:
            raise ValueError("V37_FROZEN_TRAINING_DISALLOWED")
        adjustment=None
        if learning:
            # Scores and both LOCAL gradient coefficients are computed solely
            # from the actual public cue, first, and proposed second actions.
            scores=self.scores()
            j=ACTIONS.index(selected)
            rival=max((k for k in range(3) if k!=j),
                      key=lambda k:(scores[k],-k))
            selected_score=scores[j]
            rival_score=scores[rival]
            outcome=float(public_reward)
            direction=0
            magnitude=0.0
            if outcome>=rival_score+MARGIN and selected_score<=rival_score:
                direction=+1
                magnitude=min(MAX_REWARD_GAP,outcome-rival_score)
            elif outcome<=rival_score-MARGIN and selected_score>=rival_score:
                direction=-1
                magnitude=min(MAX_REWARD_GAP,rival_score-outcome)
            if direction:
                features=self._features()
                coeff_s=self._coefficients(selected)
                coeff_r=self._coefficients(ACTIONS[rival])
                gradients=[[ (coeff_s[c]-coeff_r[c])*features[c][k]
                             for k in range(HEAD_FEATURES)]
                           for c in range(CELLS)]
                norm=2.0+sum(g*g for row in gradients for g in row)
                adjustment=(j,rival,direction*STEP_RATE*magnitude/norm,gradients)
        # Original native V22 exact selected-feedback update and original
        # accounting first; if learning=False, no additional margin update.
        super().accept_second(selected,public_reward,learning=learning,terminal=terminal)
        if adjustment is not None:
            j,r,step,gradients=adjustment
            for c in range(CELLS):
                self.cell_weights[c]=[
                    max(-WEIGHT_BOUND,min(WEIGHT_BOUND,weight+step*gradient))
                    for weight,gradient in zip(self.cell_weights[c],gradients[c])]
            self.action_biases[j]=max(-WEIGHT_BOUND,min(WEIGHT_BOUND,
                                                       self.action_biases[j]+step))
            self.action_biases[r]=max(-WEIGHT_BOUND,min(WEIGHT_BOUND,
                                                       self.action_biases[r]-step))
            self.margin_updates+=1
            # Original V22 already accounts its selected-site reverse route.
            # The second original ring route for the predicted rival is
            # separately accounted here, never misrepresented as V22 updates.
            self.margin_edge_messages+=EDGE_SIGNAL_PER_PASS
        self._check_frozen()

    def start_frozen_evaluation(self):
        self._check_frozen()
        super().start_frozen_evaluation()
        self.margin_frozen_sha=self._metadata_sha()

    def checkpoint(self):
        self._check_frozen()
        native=json.loads(super().checkpoint())
        body={
            "schema":SCHEMA,"native_v22":native,
            "margin_updates":self.margin_updates,
            "margin_edge_messages":self.margin_edge_messages,
            "margin_frozen_sha":self.margin_frozen_sha,
            "rate":STEP_RATE,"threshold":MARGIN,
            "max_gap":MAX_REWARD_GAP,
        }
        payload=canonical(body)
        packet=canonical({"body":body,"sha256":hashlib.sha256(payload).hexdigest()})
        if len(packet)>MAX_CHECKPOINT:
            raise ValueError("V37_CHECKPOINT_EXCEEDS_BUDGET")
        return packet

    @classmethod
    def restore(cls,data):
        try:
            if type(data) is not bytes or not 0<len(data)<=MAX_CHECKPOINT:
                raise ValueError("V37_INVALID_CHECKPOINT_LENGTH")
            packet=json.loads(data)
            if type(packet) is not dict or set(packet)!={"body","sha256"}:
                raise ValueError("V37_INVALID_ENVELOPE")
            body=packet["body"]
            keys={"schema","native_v22","margin_updates",
                  "margin_edge_messages","margin_frozen_sha",
                  "rate","threshold","max_gap"}
            if (type(body) is not dict or set(body)!=keys
                or body["schema"]!=SCHEMA
                or body["rate"]!=STEP_RATE
                or body["threshold"]!=MARGIN
                or body["max_gap"]!=MAX_REWARD_GAP
                or type(packet["sha256"]) is not str
                or hashlib.sha256(canonical(body)).hexdigest()!=packet["sha256"]):
                raise ValueError("V37_INVALID_SCHEMA_OR_BASIS_RULE")
            base=SharedContextRingDev.restore(canonical(body["native_v22"]))
            if base.mode!="shared":
                raise ValueError("V37_EXPECTED_SHARED_V22_ONLY")
            n=body["margin_updates"]
            messages=body["margin_edge_messages"]
            if (type(n) is not int or not 0<=n<=base.updates or
                type(messages) is not int or messages!=n*EDGE_SIGNAL_PER_PASS):
                raise ValueError("V37_MARGIN_MESSAGE_PROVENANCE")
            obj=cls.__new__(cls)
            obj.__dict__.update(base.__dict__)
            obj.margin_updates=n
            obj.margin_edge_messages=messages
            obj.margin_frozen_sha=body["margin_frozen_sha"]
            if (obj.margin_frozen_sha is not None and
                (type(obj.margin_frozen_sha) is not str or
                 len(obj.margin_frozen_sha)!=64 or
                 base.frozen_sha is None or
                 obj._metadata_sha()!=obj.margin_frozen_sha)):
                raise ValueError("V37_FROZEN_MARGIN_SHA_DRIFT")
            if obj.checkpoint()!=data:
                raise ValueError("V37_NONCANONICAL_CHECKPOINT")
            return obj
        except (ValueError,TypeError,KeyError,AttributeError,OverflowError) as exc:
            raise ValueError("UNTRUSTED_V37_PAIRWISE_CHECKPOINT") from exc
