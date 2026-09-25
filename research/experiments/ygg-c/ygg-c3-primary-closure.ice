TITLE: YGG-C3 Doubled Resource-Pressure Capability Retention Primary Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC POSITIVE
LANE: YGG-C
PREREGISTRATION: 3165d352485dfcc5614ed53fcc90fccfc4ed2110
PARENT_CLOSURE: f1befdb1476b7ec9b7f3d36d471d996393370619
SHARED_BASELINE: 878464cf84833d06a1ac7e45988bfb79608547dc
LU2VF1: e832853554e813db2e185d6b607543541f32d887
EXECUTION_HEAD: 9e2bf6289c5eb71d7c33c950bc53973b853066d4
WORKFLOW_RUN_ID: 36119173752
DUPLICATE_SHA256: 1e28140c96e43d4e5b82ebcbbe78457c4a6963dab9944a54d7ac593b8e043ad0

VALIDITY
valid=true
duplicate_complete_sweep_byte_identical=true
frozen_lineage_intact=true
l8_exact_inherited_lesion=true
l8_parent_execution_identity=true
nonlesion_manifest_fields_frozen=true
pressure_sets_nested=true
all_matching_integrity=true

PRIMARY
YGG_C3_DOUBLED_RESOURCE_PRESSURE_RETENTION=true
primary_lesion_cells=16
substrate_cells=64
primary_lesion_fraction=0.25
L8_A25_completion_area=1436
L16_A25_completion_area=1440
L16_retention_ratio_vs_L8=1.0027855153203342
L16_incorrect_done=0
L16_maturity_pass_count=10
L16_matching_integrity=true
L16_stream_noncollapse=true

PRESSURE FRONTIER
L8: retained=true, ratio=1.0, backlog=164
L12: retained=false, ratio=0.9958217270194986, backlog=170, failure=stream_noncollapse
L16: retained=true, ratio=1.0027855153203342, backlog=160
L24: retained=false, ratio=1.0, backlog=164, failure=stream_noncollapse
L32: retained=false, ratio=0.9993036211699164, backlog=165, failure=stream_noncollapse
max_tested_retained_lesion_cells=16

INTERPRETATION
The frozen LU-2V mechanism preserves the preregistered aggregate capability envelope when temporary distributed lesion pressure is doubled from 8 to 16 of 64 cells.
The result is not monotonic in lesion cardinality: L12 fails stream non-collapse while L16 passes, and L24/L32 fail stream non-collapse despite near-baseline aggregate completion area.
This indicates that resource-pressure tolerance depends on lesion topology and stream-specific routing geometry, not cardinality alone.

BOUNDARY
This does not show universal tolerance to 25-percent loss.
It is a deterministic nested-lesion result under the frozen C3 construction.
No shared-baseline promotion from this lane alone.
No online adaptation.
No recursive self-modification.

NEXT QUESTION
Hold lesion cardinality fixed and vary lesion topology/geometry to determine whether capability retention is controlled by spatial arrangement, stream asymmetry, or local redundancy rather than lesion count alone.
