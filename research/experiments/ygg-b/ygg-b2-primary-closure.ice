TITLE: YGG-B2 Content-Addressed Binding Primary Closure
DATE: 2026-09-24
STATUS: CLOSED / SCIENTIFIC NEGATIVE
LANE: YGG-B
PARENT_RESULT: b33daf3538c987a10df6826a826c057f08ba9476
PREREGISTRATION: 4713b8d26aa9328ee6a6cebaf0a9fa07169d4d49
EXECUTION_HEAD: 5294cf404a35464883dc3741c5738d69cd0b3b01
WORKFLOW_RUN_ID: 36073643944
ARTIFACT_ID: 10839038785
ARTIFACT_SHA256: 6ad89cab76f110c67eb4d14b6b64bc4b054ce7e5cb3d8e8548ddf4c5479630dd

DUPLICATE EVIDENCE
byte_identical=true
sha256=8b197010cfa2cba1ece16280a5ea6fbe69a4ff511e4827b1d5d8e913b2242b7a

QUALIFICATION
YGG_B2_CONTENT_ADDRESSED_BINDING=false
min_persistent_ge_090=false
median_persistent_ge_095=false
max_reset_le_035=true
min_gap_ge_050=false
min_shuffle_drop_ge_040=false
all_causal_direction=false

PER-SEED RESULTS
seed 111: persistent=0.3916015625 reset=0.124267578125 binding_shuffle=0.37841796875 persistent_reset_gap=0.267333984375 shuffle_degradation=0.01318359375
seed 222: persistent=0.3818359375 reset=0.125732421875 binding_shuffle=0.38427734375 persistent_reset_gap=0.256103515625 shuffle_degradation=-0.00244140625
seed 333: persistent=0.404541015625 reset=0.11962890625 binding_shuffle=0.376220703125 persistent_reset_gap=0.284912109375 shuffle_degradation=0.0283203125
seed 444: persistent=0.40283203125 reset=0.133056640625 binding_shuffle=0.394287109375 persistent_reset_gap=0.269775390625 shuffle_degradation=0.008544921875
seed 555: persistent=0.3994140625 reset=0.12255859375 binding_shuffle=0.407470703125 persistent_reset_gap=0.27685546875 shuffle_degradation=-0.008056640625

INTERPRETATION
Persistent state materially outperformed reset-state chance, so the cell did retain useful sequence information.
However binding-shuffle accuracy was essentially unchanged from intact accuracy and exceeded intact accuracy on two seeds.
Therefore the frozen YGG-B2 recurrent state did not demonstrate content-addressed key-to-value binding. Its useful memory was largely insensitive to which value was paired with which key.

SCIENTIFIC IMPLICATION
The next uncertainty is not whether more raw persistent memory helps. YGG-B1 already established persistence and YGG-B2 shows persistence alone is insufficient for relational binding.
The next experiment should test an explicit bounded relational/binding mechanism while keeping total state small and controls causal.

BOUNDARY
Do not retune YGG-B2 thresholds, width, training schedule, seeds, or dataset after this result.
Do not relabel this run as infrastructure failure.
No shared-baseline promotion.
No learned developmental C/S authority.
No online adaptation or recursive self-modification.
