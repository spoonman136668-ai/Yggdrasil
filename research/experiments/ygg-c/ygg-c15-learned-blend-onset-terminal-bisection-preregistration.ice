TITLE: YGG-C15 Learned-Blend Onset Terminal Bisection Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_CLOSURE: af45f83cb0b40270e500749afff552a2ab48dc05
PARENT_EXPERIMENT: YGG-C14

QUESTION
Which half of the accepted onset bracket (0.134765625, 0.13671875] contains the learned-control interaction onset?

FROZEN
All C9-C14 manifests, C6 factorial lesions, learned weights, task, retention definition, interaction classification, duplicate checks, restoration checks, and lineage gates remain exact.

TEST ALPHAS
0.134765625
0.1357421875
0.13671875

ANCHORS
alpha=.134765625 duplicate SHA:
4a649d00ea49a990248a0f258c49d360808085577cb3927c88bba951c936e947
must remain non-interaction.

alpha=.13671875 duplicate SHA:
90f0869984ed21292635bdad3be26859645f3a837b325eb22e083b4a1a24414b
must remain interaction-driven with context slots A,C.

CLASSIFICATION
If alpha=.1357421875 is interaction-driven:
ONSET_BETWEEN_0134765625_AND_01357421875
Else:
ONSET_BETWEEN_01357421875_AND_013671875

TERMINAL CRITERION
After classification, bracket width is exactly 0.0009765625.
Close the fine onset-bisection series after C15; do not continue decimal bisection absent a new scientific need.

SUCCESS
YGG_C15_LEARNED_BLEND_ONSET_TERMINAL_BISECTION=true iff all anchor, validity, duplicate, matching, lineage, restoration, and classification gates pass.

FAILURE
Do not alter alpha values, lesions, weights, thresholds, seeds, task, or classification rules after results.

BOUNDARY
No accepted source mutation, weight update, online adaptation, or recursive self-modification.
