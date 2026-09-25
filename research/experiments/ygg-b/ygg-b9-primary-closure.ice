TITLE: YGG-B9 Orthogonal Role-Subspace Primary Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC NEGATIVE
LANE: YGG-B
PREREGISTRATION: fed57a858ff0c42415236813261d97d50fb6ee6e
PARENT_CLOSURE: 7e9640e2328eebeb154ca4baf7cdb26553b9a0a7
EXECUTION_HEAD: b7089730bb8d406fc426956440ea2878cb8668d8
WORKFLOW_RUN_ID: 36120664735
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: 947f7d169f131bad3479a5bed1f4396982fd9a4a0be20250e8e3b6422c160f38

QUALIFICATION
YGG_B9_ROLE_SUBSPACE_BINDING=false
all_32_holdout_triples_scored=true
all_causal_direction=true
max_reset_le_035=true
min_gap_ge_050=true
min_role_flip_drop_ge_040=true
min_value_shuffle_drop_ge_040=true
no_holdout_triple_in_training=true
parameter_count_exactly_88=true
state_exactly_16=true
median_persistent_ge_095=false
min_persistent_ge_090=false

GEOMETRY
Cross-role address cosine is exactly zero by construction on every seed.
Same-role maximum absolute address cosine remained:
seed 111: 0.9977750182151794
seed 222: 0.9997021555900574
seed 333: 0.9993374347686768
seed 444: 0.9989197850227356
seed 555: 0.9998485445976257

OOD PERSISTENT ACCURACY
seed 111: 0.712890625
seed 222: 0.781494140625
seed 333: 0.86376953125
seed 444: 0.8759765625
seed 555: 0.90283203125

INTERPRETATION
Eliminating cross-role interference is insufficient.
The learned address geometry collapsed almost completely within each role subspace, while persistent state remained causally useful and all control-separation gates passed.
The next discriminating question is whether fixing the joint entity-role address geometry at low coherence removes this failure, or whether the remaining boundary lies in the scalar value channel / superposition readout itself.

BOUNDARY
Do not retune B9.
Do not relax thresholds.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
