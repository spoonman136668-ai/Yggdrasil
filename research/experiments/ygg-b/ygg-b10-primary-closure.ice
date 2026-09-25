TITLE: YGG-B10 Fixed Low-Coherence Joint Address Primary Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC NEGATIVE
LANE: YGG-B
PREREGISTRATION: c95906c9d26b58272a3a195e5cbbe2c6eaa3d611
PARENT_CLOSURE: 540d004b8a99b3b909f074e143fd699f3c9a367d
EXECUTION_HEAD: df12c027e9f507878055a4cf097c1cbb11b75c51
WORKFLOW_RUN_ID: 36121572089
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: b1dc3a814c6c80a1cf5986ab297c93b7920e1cee137f2a00dc315c7ca8d4bf98

MECHANICAL
all_pass=true
max_abs_offdiag_address_cosine=0.4999999701976776
sixteen_unique_addresses=true
unit_norm=true
no_antipodal_pair=true
persistent_state_scalars=16
learned_parameters=24
codebook_requires_grad=false

QUALIFICATION
YGG_B10_FIXED_LOW_COHERENCE_JOINT_ADDRESS=false
all_32_holdout_triples_scored=true
all_causal_direction=true
max_reset_le_035=true
no_holdout_triple_in_training=true
parameter_count_exactly_24=true
state_exactly_16=true
median_persistent_ge_095=false
min_persistent_ge_090=false
min_gap_ge_050=false
min_role_flip_drop_ge_040=false
min_value_shuffle_drop_ge_040=false

OOD PERSISTENT ACCURACY
111: 0.32568359375
222: 0.3583984375
333: 0.342041015625
444: 0.32177734375
555: 0.3203125

INTERPRETATION
Bounding address coherence at 0.5 by construction did not recover role-conditioned generalization and performed materially worse than the learned B7-B9 geometries.
Therefore high cosine interference is not, by itself, the causal explanation for the B6-B9 capability boundary.
The learned address geometry appears to carry useful task structure despite its collisions.

NEXT QUESTION
Return to B9's exact orthogonal role-subspace address mechanism and expand only the value channel from one scalar to two dimensions.
This tests whether the remaining bottleneck is the scalar value/superposition readout rather than address geometry.

BOUNDARY
Do not retune B10.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
