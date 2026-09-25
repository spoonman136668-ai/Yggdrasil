TITLE: YGG-B5 Cartesian Holdout Compositional Binding Primary Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC POSITIVE
LANE: YGG-B
PARENT_CLOSURE: f32f387b2048c7c2423346f4d509f2e44774637b
PREREGISTRATION: 626476e479cd8283625c6d45d36a28a994f61135
EXECUTION_HEAD: 664171adaf5b2909f6e40182be1bc2b8b3e58a4b
WORKFLOW_RUN_ID: 36107274496
ARTIFACT_ZIP_SHA256: f4549b652ffdeeb9a7eb675fdde47e1c529bf2fa546ed17bc3bccc2caae44019
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: a8bc8f09a4c76ad62d0f42de36c9620991bf897fe517042b699cfd7e073136f8

QUALIFICATION
YGG_B5_CARTESIAN_HOLDOUT_COMPOSITION=true
all_16_holdout_pairs_scored=true
all_causal_direction=true
max_reset_le_035=true
median_persistent_ge_095=true
min_gap_ge_050=true
min_persistent_ge_090=true
min_shuffle_drop_ge_040=true
no_holdout_pair_in_training=true
parameter_count_exactly_88=true
state_exactly_16=true

PER-SEED RESULTS
seed 111: persistent_ood=1.0 reset=0.12939453125 binding_shuffle=0.348388671875 gap=0.87060546875 shuffle_degradation=0.651611328125 heldout_pairs=16 train_holdout_bindings=0
seed 222: persistent_ood=1.0 reset=0.127685546875 binding_shuffle=0.365234375 gap=0.872314453125 shuffle_degradation=0.634765625 heldout_pairs=16 train_holdout_bindings=0
seed 333: persistent_ood=1.0 reset=0.12060546875 binding_shuffle=0.358154296875 gap=0.87939453125 shuffle_degradation=0.641845703125 heldout_pairs=16 train_holdout_bindings=0
seed 444: persistent_ood=1.0 reset=0.128173828125 binding_shuffle=0.356689453125 gap=0.871826171875 shuffle_degradation=0.643310546875 heldout_pairs=16 train_holdout_bindings=0
seed 555: persistent_ood=1.0 reset=0.125244140625 binding_shuffle=0.35205078125 gap=0.874755859375 shuffle_degradation=0.64794921875 heldout_pairs=16 train_holdout_bindings=0

INTERPRETATION
B5 is a preregistered scientific positive.
The frozen B4 factorized relational memory generalizes perfectly on all five seeds when the queried key/value composition is drawn from a deterministic 16-pair Cartesian holdout never present in training.
Every constituent key and value remains familiar; the scored relation is novel.
The reset and binding-shuffle controls remain strongly separated, so the result depends on persistent relational state rather than terminal token statistics alone.

BOUNDARY
Do not retune B5 after observing this result.
Do not relabel B2 or B3 as PASS.
No shared-baseline promotion from this lane alone.
No learned developmental C/S authority.
No online adaptation.
No recursive self-modification.

NEXT QUESTION
The B lane has now established persistent sequence state, controlled relational binding, and Cartesian holdout composition under the 16-state/88-parameter B4/B5 budget.
The next language-bridge experiment should increase structural composition depth or role structure rather than retest the same pairwise binding task.
