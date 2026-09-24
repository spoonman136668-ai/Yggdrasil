TITLE: YGG-B3 Factorized Relational State Primary Closure
DATE: 2026-09-24
STATUS: CLOSED / SCIENTIFIC NEGATIVE WITH STRONG MECHANISTIC GAIN
LANE: YGG-B
PARENT_RESULT: 6b39bf573b2b0a758ac0525aa6a49f5ef6807f1b
PREREGISTRATION: 970d3b52c3fed6a8085d1224a98c5616c996f29b
EXECUTION_HEAD: 930a39db8119a8ca2fe3abf8ffde944c77a36996
WORKFLOW_RUN_ID: 36074323790
ARTIFACT_ID: 10840140206
ARTIFACT_SHA256: 664b44d16997368b4975f7877d79933752defa5c6867a2c94b66d3808caa944f
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: e425776013ec2c062bd0896e61ddae5f5b5dfd9b1884e550023040fc7f2e5e77

QUALIFICATION
YGG_B3_FACTORIZED_RELATIONAL_STATE=false
state_exactly_16=true
all_causal_direction=true
max_reset_le_035=true
min_gap_ge_050=true
min_shuffle_drop_ge_040=true
min_persistent_ge_090=false
median_persistent_ge_095=false

PER-SEED RESULTS
seed 111: persistent=0.839111328125 reset=0.126953125 binding_shuffle=0.29541015625 reset_gap=0.712158203125 shuffle_degradation=0.543701171875
seed 222: persistent=0.806640625 reset=0.129638671875 binding_shuffle=0.300537109375 reset_gap=0.677001953125 shuffle_degradation=0.506103515625
seed 333: persistent=0.819091796875 reset=0.11572265625 binding_shuffle=0.299072265625 reset_gap=0.703369140625 shuffle_degradation=0.52001953125
seed 444: persistent=0.831787109375 reset=0.12451171875 binding_shuffle=0.3076171875 reset_gap=0.707275390625 shuffle_degradation=0.524169921875
seed 555: persistent=0.82275390625 reset=0.126953125 binding_shuffle=0.302001953125 reset_gap=0.69580078125 shuffle_degradation=0.520751953125

MODEL
parameter_count=88
persistent_state_scalars=16
relational_matrix=3x4
pending_key_register=4

INTERPRETATION
B3 materially changes the B2 failure mode.
The factorized relational state is strongly sensitive to the correct key/value pairing: deranging bindings degrades accuracy by 0.506 to 0.544 on every seed.
Persistent state also exceeds reset by 0.677 to 0.712 on every seed.
Therefore explicit relational binding recovered causal association that generic 16-state recurrence did not.

The preregistered capability claim still fails because persistent held-out accuracy remains 0.807 to 0.839, below the required 0.90 minimum and 0.95 median.

HYPOTHESIS GENERATED FOR FOLLOW-UP
The remaining error is consistent with interference from compressing eight possible keys into a four-dimensional normalized key space while superposing four bindings in a 3x4 matrix.
A new experiment may test a different 16-scalar factorization that allocates more dimensions to key addressability while keeping total persistent state fixed.

BOUNDARY
Do not retune B3 dimensions, thresholds, epochs, seeds, or training data.
Do not relabel B3 as PASS.
No shared-baseline promotion.
No learned developmental C/S authority.
No online adaptation or recursive self-modification.
