TITLE: YGG-B7 Multiplicative Role-Binding Cartesian Holdout Primary Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC NEGATIVE WITH STRONG DIRECTIONAL IMPROVEMENT
LANE: YGG-B
PREREGISTRATION: 246cdc87bdced07e910b7072e1ac7a5a42c794a3
PARENT_CLOSURE: ec43ed86a3adc889a0ebec36dccccf97f1827fe4
EXECUTION_HEAD: 86a27a85fbb8bbf781baf6374e54c1baea5f7b7c
WORKFLOW_RUN_ID: 36119284555
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: 95a32f9b2ae2cc4df196602c0067fd8c961405399e1a2e1426ed348e1d773430

QUALIFICATION
YGG_B7_MULTIPLICATIVE_ROLE_BINDING=false
all_32_holdout_triples_scored=true
all_causal_direction=true
max_reset_le_035=true
min_gap_ge_050=true
min_role_flip_drop_ge_040=true
no_holdout_triple_in_training=true
parameter_count_exactly_88=true
state_exactly_16=true
median_persistent_ge_095=false
min_persistent_ge_090=false
min_value_shuffle_drop_ge_040=false

PER-SEED
seed 111: persistent=0.84814453125 reset=0.13232421875 value_shuffle=0.317138671875 role_flip=0.15234375 value_drop=0.531005859375 role_drop=0.69580078125 max_address_cosine=0.9982658624649048
seed 222: persistent=0.664306640625 reset=0.1259765625 value_shuffle=0.282958984375 role_flip=0.16064453125 value_drop=0.38134765625 role_drop=0.503662109375 max_address_cosine=0.7928149104118347
seed 333: persistent=0.721435546875 reset=0.122314453125 value_shuffle=0.279052734375 role_flip=0.1416015625 value_drop=0.4423828125 role_drop=0.579833984375 max_address_cosine=0.9924407005310059
seed 444: persistent=0.8046875 reset=0.126220703125 value_shuffle=0.295166015625 role_flip=0.144775390625 value_drop=0.509521484375 role_drop=0.659912109375 max_address_cosine=0.9933547973632812
seed 555: persistent=0.82373046875 reset=0.130126953125 value_shuffle=0.307861328125 role_flip=0.158203125 value_drop=0.515869140625 role_drop=0.66552734375 max_address_cosine=0.9987735748291016

INTERPRETATION
Replacing additive key-plus-role addresses with fixed multiplicative sign binding produced a large and repeatable improvement over B6 while preserving the 16-scalar state budget and reducing learned parameters from 104 to 88.
Persistent state and role identity remain strongly causal on every seed.
The frozen capability target is nevertheless not met.
Very high maximum address cosine remains on four of five seeds, consistent with unresolved address-geometry interference.

NEXT QUESTION
Test a fixed globally mixing orthogonal role transform rather than elementwise sign masking, while keeping the B6/B7 task, state budget, training schedule, holdout, seeds, controls, and thresholds unchanged.

BOUNDARY
Do not retune B7.
Do not relax the frozen thresholds.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
