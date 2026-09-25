TITLE: YGG-C8 Learned-Blend Interaction Dose Closure
DATE: 2026-09-25
STATUS: CLOSED / SCIENTIFIC POSITIVE
LANE: YGG-C
PREREGISTRATION: dfafdb34cd73f4a31bb6068f41bb92b871d0440e
PARENT_CLOSURE: c19a8f5bb5f0f446bf6b09dbd711b41b58ecbb4a
EXECUTION_HEAD: 9fd4a258c310d39906a73e6c22a4d974bf3ddfbb
WORKFLOW_RUN_ID: 36135868415
MECHANISM_CATEGORY: BLEND_REQUIRED_STABLE

VALIDITY
valid=true
alpha025_accepted_c7_map_exact=true
alpha_levels_exact=true
base_manifests_identical_across_alpha=true
factorial_and_matching_valid_each_alpha=true
learned_weight_identity_exact=true
runtime_alpha_restored_final=true

RESULT
alpha=0.0: PATH_NOT_REPRODUCED / interaction_driven=false
alpha=0.25: INTERACTION_DRIVEN / context slots A,C
alpha=0.50: INTERACTION_DRIVEN / context slots A,C
alpha 0.25 and 0.50 retained maps are identical.

INTERPRETATION
The C6/C7 A/C recovery interaction requires a nonzero learned-control blend and is stable from alpha=0.25 through alpha=0.50. It is therefore not a fixed-substrate geometry effect and is not strongly dose-modulated over the tested upper range.

NEXT QUESTION
Locate the onset below alpha=0.25 with frozen intermediate doses 0.0625, 0.125, and 0.1875 plus the accepted alpha=0.25 anchor.

BOUNDARY
No accepted LU-2V mutation.
No learned-weight update.
No online adaptation.
No shared-baseline promotion.
No recursive self-modification.
