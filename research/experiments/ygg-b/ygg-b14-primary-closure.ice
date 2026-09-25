TITLE: YGG-B14 Reduced-Load Two-Factor Structural Binding Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC POSITIVE
LANE: YGG-B
PREREGISTRATION: 772e247101e692bfcb6832d5ab6b0583dc6cf94f
PARENT_CLOSURE: 48f00fbecefbe54e86c38dd0663fcd6bd116218e
EXECUTION_HEAD: e8868e1a4331aa911ee03f4a71e772fdb1ce822b
WORKFLOW_RUN_ID: 36135652939
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: f92a6a2472583d186e49a52fabe487fb028f3581ce9f05a4295049f8dc9b736b

QUALIFICATION
YGG_B14_REDUCED_LOAD_TWO_FACTOR_BINDING=true
all_64_holdout_quadruples_scored=true
all_causal_direction=true
max_reset_le_035=true
median_persistent_ge_095=true
min_gap_ge_050=true
min_persistent_ge_090=true
min_role_flip_drop_ge_040=true
min_slot_flip_drop_ge_040=true
min_value_shuffle_drop_ge_040=true
no_holdout_quadruple_in_training=true
parameter_count_exactly_104=true
state_exactly_24=true

OOD PERSISTENT ACCURACY
seed111=1.0
seed222=1.0
seed333=1.0
seed444=1.0
seed555=1.0

INTERPRETATION
ROLE×SLOT structural depth is fully supported at four concurrent bindings under the exact B13 memory/state/parameter budget.
B13's failure at eight bindings is therefore not caused by structural depth alone.
The remaining ambiguity is whether the boundary is primarily total concurrent superposition load or interference introduced by carrying more than one entity at once.

NEXT QUESTION
Hold total concurrent bindings at four while increasing from one entity to two entities, assigning two structural addresses to each entity. This isolates entity-count interference from binding-load interference before testing an intermediate six-binding load.

BOUNDARY
No shared-baseline promotion from B14 alone.
No online adaptation.
No recursive self-modification.
