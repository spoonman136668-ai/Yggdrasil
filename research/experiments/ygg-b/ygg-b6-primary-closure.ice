TITLE: YGG-B6 Role-Conditioned Cartesian Holdout Binding Primary Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC NEGATIVE
LANE: YGG-B
PREREGISTRATION: 7667a338a63b16b3468f8e0e2b201b3725572151
PARENT_CLOSURE: a40e007cf7b3bce6b2a88da78ee91a420f2fd532
EXECUTION_HEAD: 9b888625646067bf6cf02f39d91a52871a03a0f1
WORKFLOW_RUN_ID: 36118167766
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: a1454b6655b7371a43c70677f41165db825495a4bdbcf4b4b3561b60dbf4cdcd

QUALIFICATION
YGG_B6_ROLE_CONDITIONED_HOLDOUT=false
all_32_holdout_triples_scored=true
all_causal_direction=true
max_reset_le_035=true
no_holdout_triple_in_training=true
parameter_count_exactly_104=true
state_exactly_16=true
median_persistent_ge_095=false
min_persistent_ge_090=false
min_gap_ge_050=false
min_role_flip_drop_ge_040=false
min_value_shuffle_drop_ge_040=false

PER-SEED SUMMARY
seed 111: persistent=0.42626953125 reset=0.1298828125 value_shuffle=0.214599609375 role_flip=0.184326171875 max_address_cosine=0.7677783966064453
seed 222: persistent=0.40966796875 reset=0.11865234375 value_shuffle=0.216796875 role_flip=0.193359375 max_address_cosine=0.7736589312553406
seed 333: persistent=0.38134765625 reset=0.122314453125 value_shuffle=0.204345703125 role_flip=0.138671875 max_address_cosine=0.5862419009208679
seed 444: persistent=0.415771484375 reset=0.125 value_shuffle=0.21240234375 role_flip=0.161865234375 max_address_cosine=0.8940739035606384
seed 555: persistent=0.41845703125 reset=0.123779296875 value_shuffle=0.21337890625 role_flip=0.176513671875 max_address_cosine=0.6736259460449219

INTERPRETATION
Persistent state remains causally useful because persistent accuracy exceeds reset, value-shuffle, and role-flip controls on every seed, but the additive key-plus-role address construction does not support the preregistered role-sensitive compositional accuracy target under the compact state budget.
The large learned address cosines are consistent with substantial address interference and motivate a new representation hypothesis rather than threshold tuning.

NEXT QUESTION
Test whether an explicit multiplicative or otherwise role-binding address operator can reduce role-address interference while preserving the 16-scalar persistent-state budget and controlled holdout task.

BOUNDARY
Do not retune B6 thresholds, training schedule, state budget, holdout rule, or observed additive address mechanism.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
