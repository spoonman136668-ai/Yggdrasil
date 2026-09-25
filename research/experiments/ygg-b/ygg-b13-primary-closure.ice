TITLE: YGG-B13 Two-Factor Structural Binding Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC NEGATIVE
LANE: YGG-B
PREREGISTRATION: 36b09c008efa7fd538f77be2a92e98642d887646
PARENT_CLOSURE: 2e3ab27ad17ff3d55665c24d491b8d941f601ac4
EXECUTION_HEAD: 9fe41df523cc61fc73bddd60917ac217973dd24e
WORKFLOW_RUN_ID: 36125913802
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: b7b4f2551c267cada819a760707409905ae8337e8f34b95cdfc839eebb0ba92d

QUALIFICATION
YGG_B13_TWO_FACTOR_STRUCTURAL_BINDING=false
all_64_holdout_quadruples_scored=true
all_causal_direction=true
max_reset_le_035=true
min_role_flip_drop_ge_040=true
min_slot_flip_drop_ge_040=true
no_holdout_quadruple_in_training=true
parameter_count_exactly_104=true
state_exactly_24=true
median_persistent_ge_095=false
min_gap_ge_050=false
min_persistent_ge_090=false
min_value_shuffle_drop_ge_040=false

OOD PERSISTENT ACCURACY
111=0.5703125
222=0.635986328125
333=0.62548828125
444=0.59814453125
555=0.6533203125

INTERPRETATION
The B12 two-dimensional value channel remains causally useful, and both ROLE and SLOT controls materially affect retrieval, but the same 24-scalar state does not sustain the B13 two-factor task at eight simultaneous bindings. The remaining boundary could be eight-binding superposition load, structural-depth/address interference, or both.

NEXT QUESTION
Keep ROLE×SLOT depth, masks, value width, state budget, thresholds, seeds, and holdout rule fixed while reducing each sequence from two entities/eight bindings to one entity/four bindings. This isolates concurrent superposition load from structural depth.

BOUNDARY
Do not retune B13.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
