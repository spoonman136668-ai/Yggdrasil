TITLE: YGG-C13 Learned-Blend Onset Fourth Bisection Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_CLOSURE: 1b46add5bab664782399a82afc780e6999591340
PARENT_EXPERIMENT: YGG-C12

QUESTION
Which half of the accepted onset bracket (0.1328125, 0.140625] contains the learned-control interaction onset?

FROZEN
All C9-C12 manifests, C6 factorial lesions, learned weights, task, retention definition, interaction classification, duplicate checks, restoration checks, and lineage gates remain exact.

TEST ALPHAS
0.1328125
0.13671875
0.140625

ANCHORS
alpha=.1328125 duplicate SHA:
35a4341d528efdee8dd14320b132f1d01727987dcadb1c4cd3bd903a8d856a55
must remain non-interaction.

alpha=.140625 duplicate SHA:
8e1d685d6eb4242ed271475002708c95773b1c1cda13622f42ac1739fd8f70ff
must remain interaction-driven with context slots A,C.

CLASSIFICATION
If alpha=.13671875 is interaction-driven:
ONSET_BETWEEN_01328125_AND_013671875
Else:
ONSET_BETWEEN_013671875_AND_0140625

SUCCESS
YGG_C13_LEARNED_BLEND_ONSET_FOURTH_BISECTION=true iff all anchor, validity, duplicate, matching, lineage, restoration, and classification gates pass.

FAILURE
Do not alter alpha values, lesions, weights, thresholds, seeds, task, or classification rules after results.

BOUNDARY
No accepted source mutation, weight update, online adaptation, or recursive self-modification.
