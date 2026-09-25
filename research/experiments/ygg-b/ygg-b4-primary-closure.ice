TITLE: YGG-B4 Address-Dimension Reallocation Primary Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC POSITIVE
LANE: YGG-B
PARENT_RESULT: ad853adb938a4f992cbd19e2624674107987c924
PREREGISTRATION: f4a67d36b972efe2406c5323ae7f45ee45e0a57f
EXECUTION_HEAD: cbb6218cb618041c4902dd102c1cd471e5682a0e
WORKFLOW_RUN_ID: 36082042970
ARTIFACT_ID: 10842178160
DUPLICATE_BYTE_IDENTICAL: true
DUPLICATE_SHA256: dc759e5ab89c97c37926ba29ce21217fc1f657218299e05723ede03ded75273b

QUALIFICATION
YGG_B4_ADDRESS_DIMENSION_REALLOCATION=true
state_exactly_16=true
parameter_count_exactly_88=true
all_causal_direction=true
max_reset_le_035=true
min_gap_ge_050=true
min_shuffle_drop_ge_040=true
min_persistent_ge_090=true
median_persistent_ge_095=true

PER-SEED RESULTS
seed 111: persistent=1.0 reset=0.120361328125 binding_shuffle=0.344482421875 reset_gap=0.879638671875 shuffle_degradation=0.655517578125 max_abs_offdiag_key_cosine=0.0054616779088974
seed 222: persistent=1.0 reset=0.127197265625 binding_shuffle=0.34716796875 reset_gap=0.872802734375 shuffle_degradation=0.65283203125 max_abs_offdiag_key_cosine=0.00380590558052063
seed 333: persistent=1.0 reset=0.1259765625 binding_shuffle=0.346923828125 reset_gap=0.8740234375 shuffle_degradation=0.653076171875 max_abs_offdiag_key_cosine=0.008256673812866211
seed 444: persistent=1.0 reset=0.12109375 binding_shuffle=0.3427734375 reset_gap=0.87890625 shuffle_degradation=0.6572265625 max_abs_offdiag_key_cosine=0.002798784524202347
seed 555: persistent=1.0 reset=0.126953125 binding_shuffle=0.345703125 reset_gap=0.873046875 shuffle_degradation=0.654296875 max_abs_offdiag_key_cosine=0.004245936870574951

MODEL
parameter_count=88
persistent_state_scalars=16
key_dimension=8
value_dimension=1
relational_matrix=1x8
pending_key_register=8

INTERPRETATION
B4 is a preregistered scientific positive.
The same 16 persistent scalars and 88 learned parameters that failed the B3 accuracy thresholds reach perfect held-out persistent accuracy on every frozen seed when address dimensionality is reallocated from four key dimensions to eight.

The reset and binding-shuffle controls remain strongly separated from persistent performance, and all five seeds preserve the required causal direction.
The learned normalized key embeddings are nearly orthogonal by the preregistered diagnostic.

Together with the negative B3 result, this supports the preregistered hypothesis that B3's remaining error was primarily key-address interference rather than total persistent-state or learned-parameter capacity.

MECHANICAL NOTE
The first B4 workflow attempt failed before scientific execution because of a source syntax defect.
The defect was repaired without changing the frozen scientific treatment, thresholds, seeds, data, state budget, or parameter budget.
The repaired frozen execution passed and was byte-identical across duplicate complete execution.

NEXT SCIENTIFIC QUESTION
Having established persistent sequence memory and controlled relational binding under the frozen B4 budget, the next B-lane experiment should test compositional generalization under held-out role/filler or relation combinations rather than further retuning B4.

BOUNDARY
Do not retune B4 dimensions, thresholds, epochs, seeds, or training data.
Do not relabel B2 or B3 as PASS.
No shared-baseline promotion from this lane alone.
No learned developmental C/S authority.
No online adaptation.
No recursive self-modification.
