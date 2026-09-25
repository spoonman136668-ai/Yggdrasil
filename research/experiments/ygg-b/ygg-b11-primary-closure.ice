TITLE: YGG-B11 Two-Dimensional Value-Channel Capacity Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC POSITIVE
LANE: YGG-B
PREREGISTRATION: 877d650658f88072eb18992c9f4d1ad9cdef7205
PARENT_CLOSURE: 4d5ad6590f2f4fa9e8454cd81c61a2c78f932f6a
STRUCTURAL_PARENT: YGG-B9
EXECUTION_HEAD: 3cee59473c99c117f4abce3a2626069c00c28835
WORKFLOW_RUN_ID: 36122090022
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: 36bfff18fe7b7acff692351275b0a793f0d6f5a0246a7c43efcb7ea6be81ba09

MECHANICAL
all_pass=true
value_dimension=2
memory_shape=2x8
persistent_state_scalars=24
learned_parameters=104
cross_role_address_cosine=0.0
role_masks_exact_b9=true

QUALIFICATION
YGG_B11_VALUE_CHANNEL_2D=true
all_32_holdout_triples_scored=true
all_causal_direction=true
max_reset_le_035=true
median_persistent_ge_095=true
min_gap_ge_050=true
min_persistent_ge_090=true
min_role_flip_drop_ge_040=true
min_value_shuffle_drop_ge_040=true
no_holdout_triple_in_training=true
parameter_count_exactly_104=true
state_exactly_24=true

PER-SEED OOD PERSISTENT ACCURACY
111: 0.907958984375
222: 0.96630859375
333: 0.95556640625
444: 0.96044921875
555: 0.973388671875

PER-SEED MAX ADDRESS COSINE
111: 0.5206223726272583
222: 0.5059236884117126
333: 0.4905717074871063
444: 0.5036386847496033
555: 0.4849929213523865

INTERPRETATION
Expanding only the value representation/readout from one dimension to two dimensions converts the B9 role-subspace task from a scientific negative into a full frozen-gate positive.
The address mechanism remains the exact B9 disjoint-role construction and every held-out entity/role/value triple remains unseen in training.
This strongly supports scalar value/superposition capacity as the dominant B9 boundary.
The result is a diagnostic state-budget expansion from 16 to 24 persistent scalars and is not a compact-model promotion.

NEXT QUESTION
Cross-confirm the value-channel mechanism under B7's full-width multiplicative role geometry while holding the two-dimensional value channel, 24-state budget, data, controls, seeds, and thresholds fixed.
This distinguishes a general value-width effect from a specific interaction with B9's disjoint role subspaces.

BOUNDARY
Do not retune B11.
Do not relabel B6-B10.
No shared-baseline promotion from B11 alone.
No online adaptation.
No recursive self-modification.
