TITLE: YGG-B17 Three-Dimensional Value-Channel Entity Binding Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC POSITIVE
LANE: YGG-B
PREREGISTRATION: 29d5f861ecde882a2fa9e69fc7a94e49b757c672
PARENT_CLOSURE: 61110520572d9e43b976ff900fd0fd187274a5cf
EXECUTION_HEAD: ed1679af4c290b981453d39972d33166f3823d4d
WORKFLOW_RUN_ID: 36143839804
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: 08baab8ef17251fcb05b83c16db22bb7e144b1a8aa90497a36c7ae84bca2f048

QUALIFICATION
YGG_B17_VALUE3D_ENTITY_BINDING=true
all_64_holdout_quadruples_scored=true
all_causal_direction=true
max_reset_le_035=true
median_persistent_ge_095=true
min_gap_ge_050=true
min_persistent_ge_090=true
min_role_flip_drop_ge_040=true
min_slot_flip_drop_ge_040=true
min_value_shuffle_drop_ge_040=true
state_exactly_32=true
parameter_count_exactly_120=true

OOD PERSISTENT ACCURACY
111=1.0
222=1.0
333=1.0
444=0.984130859375
555=1.0

INTERPRETATION
Increasing only the value/superposition channel from 2D to 3D fully rescues the two-entity/four-binding task that failed in B15. Combined with B11/B12, this strongly supports value-channel capacity as the dominant multi-entity bottleneck.

NEXT QUESTION
Return to the full B13 two-entity/eight-binding structural task and change only the value channel from 2D to 3D. This directly tests whether the same mechanism rescues the full load rather than merely the reduced four-binding load.

BOUNDARY
Diagnostic state expansion only.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
