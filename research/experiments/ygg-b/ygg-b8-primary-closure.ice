TITLE: YGG-B8 Orthogonal Role-Transform Cartesian Holdout Primary Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC NEGATIVE
LANE: YGG-B
PREREGISTRATION: ed5ea35c4c075110083189b99180083480ce45cd
PARENT_CLOSURE: 152c32eb62f4310e149d878bc38915be6806068e
EXECUTION_HEAD: 65e6258098d53d836cfc13fe67f68cd0fa89e8e4
WORKFLOW_RUN_ID: 36119833986
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: 170900590e7abeffb279d708d3bbaa2f1d603030e05fd622c7f957f7daeda64b

QUALIFICATION
YGG_B8_ORTHOGONAL_ROLE_TRANSFORM=false
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
seed 111: persistent=0.661865234375 reset=0.12158203125 value_shuffle=0.261962890625 role_flip=0.136962890625 max_address_cosine=0.9804404973983765
seed 222: persistent=0.759765625 reset=0.1259765625 value_shuffle=0.31005859375 role_flip=0.16845703125 max_address_cosine=0.6852242946624756
seed 333: persistent=0.78173828125 reset=0.122314453125 value_shuffle=0.299560546875 role_flip=0.143798828125 max_address_cosine=0.6788403987884521
seed 444: persistent=0.664794921875 reset=0.126220703125 value_shuffle=0.27392578125 role_flip=0.14013671875 max_address_cosine=0.978489875793457
seed 555: persistent=0.852783203125 reset=0.130126953125 value_shuffle=0.31201171875 role_flip=0.15966796875 max_address_cosine=0.9983144402503967

INTERPRETATION
A fixed globally mixing orthogonal role transform did not resolve the B6/B7 role-conditioned generalization boundary.
Persistent state and explicit role identity remain causally useful on every seed, but high address cosine interference persists on several seeds and the frozen accuracy gates remain unmet.
The result argues against further arbitrary rotations of one fully shared eight-dimensional address space.

NEXT QUESTION
Partition the fixed eight-dimensional address state into explicit orthogonal role subspaces so cross-role addresses cannot interfere by construction, while preserving the same total persistent-state budget, task, controls, seeds, and frozen thresholds.

BOUNDARY
Do not retune B8.
Do not relax thresholds.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
