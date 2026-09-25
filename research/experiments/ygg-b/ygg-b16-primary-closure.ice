TITLE: YGG-B16 Fixed Factorized Entity-Code Binding Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC NEGATIVE
LANE: YGG-B
PREREGISTRATION: 14553de49c1cc2fdc0af18c54a0a7c1fec835e30
PARENT_CLOSURE: 1dc476cb2d6f4597a7fae39bdef2440fe74614fb
EXECUTION_HEAD: c002d9c6123d5fa66005ad737596ecc212402929
WORKFLOW_RUN_ID: 36143120540
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: b8194f139e5ddd23d8d5fbcef24c573527abce332d600014549dfdf6e0b1eeff

MECHANICAL
all_pass=true
joint_addresses_unique_32=true
joint_max_abs_cosine=0.5000000596046448
no_antipodal_duplicates=true
learned_parameters=40
persistent_state_scalars=24

QUALIFICATION
YGG_B16_FIXED_FACTORIZED_ENTITY_CODE=false
all_64_holdout_quadruples_scored=true
all_causal_direction=true
max_reset_le_035=true
min_gap_ge_050=true
min_role_flip_drop_ge_040=true
min_slot_flip_drop_ge_040=true
min_value_shuffle_drop_ge_040=true
no_holdout_quadruple_in_training=true
parameter_count_exactly_40=true
state_exactly_24=true
median_persistent_ge_095=false
min_persistent_ge_090=false

OOD PERSISTENT ACCURACY
111=0.767333984375
222=0.737060546875
333=0.767822265625
444=0.74951171875
555=0.76123046875

INTERPRETATION
Replacing learned entity vectors with a fixed factorized code that bounds joint-address coherence at 0.5 does not rescue the two-entity B15 task and performs worse than B15's learned entity geometry. Learned entity structure is therefore useful rather than the sole source of the boundary.
Combined with B11/B12, the remaining evidence points back toward value/superposition capacity under multiple entities.

NEXT QUESTION
Restore B15's learned entity geometry and increase only the value channel from 2 dimensions to 3, preserving the exact two-entity/four-binding task and all control thresholds.

BOUNDARY
Do not retune B16.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
