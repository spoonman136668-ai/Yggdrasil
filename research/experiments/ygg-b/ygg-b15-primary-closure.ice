TITLE: YGG-B15 Two-Entity Fixed-Load Structural Binding Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC NEGATIVE
LANE: YGG-B
PREREGISTRATION: 18efc0ea2734d23e20e9306264300c864bf02921
PARENT_CLOSURE: dd5254209f72785ac27389171589b0f0bb74b6db
EXECUTION_HEAD: 8bdd2af598849259c0098501c4388238f233cc36
WORKFLOW_RUN_ID: 36136282694
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: b54dbc134b55bae8abf6d269cc6df8c28e4887e79b9110187904769dc94f3b59

QUALIFICATION
YGG_B15_TWO_ENTITY_FIXED_LOAD_BINDING=false
all_64_holdout_quadruples_scored=true
all_causal_direction=true
max_reset_le_035=true
min_gap_ge_050=true
min_role_flip_drop_ge_040=true
min_slot_flip_drop_ge_040=true
min_value_shuffle_drop_ge_040=true
no_holdout_quadruple_in_training=true
parameter_count_exactly_104=true
state_exactly_24=true
median_persistent_ge_095=false
min_persistent_ge_090=false

OOD PERSISTENT ACCURACY
111=0.81005859375
222=0.796875
333=0.821044921875
444=0.808349609375
555=0.802734375

INTERPRETATION
At the exact four-binding load solved perfectly by B14, introducing a second entity reduces OOD accuracy to about 0.80 while every causal control remains healthy. Therefore entity multiplicity itself is a major contributor to the B13 boundary.
B10 already showed that a fixed low-coherence joint codebook with a one-dimensional value channel is insufficient, while B11/B12 showed that the two-dimensional value channel is a necessary rescue mechanism.

NEXT QUESTION
Keep B15's two-entity/four-binding task and proven two-dimensional value channel, but replace learned entity vectors with a fixed factorized entity sign-mask code that composes multiplicatively with the frozen ROLE and SLOT masks. This directly tests whether learned entity-address interference is causal.

BOUNDARY
Do not retune B15.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
