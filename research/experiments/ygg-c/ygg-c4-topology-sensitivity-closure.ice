TITLE: YGG-C4 Fixed-Cardinality Lesion Topology Sensitivity Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC NEGATIVE
LANE: YGG-C
PREREGISTRATION: 03a1a58172326e86e33f834d8a2d3d25d4a862aa
PARENT_EXPERIMENT: YGG-C3
EXECUTION_HEAD: e7baf769ec7ed1766cc8870efb1aa39df0c18691
WORKFLOW_RUN_ID: 36119964708
DUPLICATE_SHA256: 9a4f1775e0cc5639cfe603bbf44414f34191e81b56c40515fb4f8469fdb4094a
PARENT_REFERENCE_SHA256: 7b6ea7e6bea1d80f718c0581669ed23adbe95488db4f75d84637388c71010ae1

VALIDITY
valid=true
duplicate_complete_execution_byte_identical=true
parent_reference_hash_exact=true
all_topologies_cardinality_16=true
all_matching_integrity=true

QUALIFICATION
YGG_C4_TOPOLOGY_SENSITIVITY=false
at_least_one_retained=true
at_least_one_not_retained=false

TOPOLOGY RESULTS
HASH16: retained=true, A25 retention_ratio=1.0027855153203342, stream_noncollapse=true
CONTIGUOUS16: retained=true, A25 retention_ratio=0.9993036211699164, stream_noncollapse=true
EVEN16: retained=true, A25 retention_ratio=1.0006963788300836, stream_noncollapse=true
TWO_ARC16: retained=true, A25 retention_ratio=0.9979108635097493, stream_noncollapse=true
FOUR_ARC16: retained=true, A25 retention_ratio=0.9993036211699164, stream_noncollapse=true

INTERPRETATION
All five preregistered 16-cell lesion geometries preserved the frozen C3 capability envelope.
The preregistered hypothesis that coarse spatial topology at fixed L16 materially determines retained/not-retained classification is therefore falsified for these topology families.
Together with C3's nested L12 failure and L16 recovery, this shifts the next question from coarse topology toward the detailed cardinality transition and possible reorganization threshold between 8 and 16 cells.

NEXT QUESTION
Map every nested hash-ranked lesion cardinality from 8 through 16 under the exact C3 construction and determine whether the L12-to-L16 recovery forms a threshold-like retained plateau or an irregular alternating transition.

BOUNDARY
Do not retune C4.
No accepted LU-2V mutation.
No shared-baseline promotion.
No online adaptation.
No recursive self-modification.
