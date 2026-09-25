TITLE: YGG-C14 Learned-Blend Onset Fifth Bisection Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_CLOSURE: e9373550e946396aa8e6d0c3af529a77e1a75994
PARENT_EXPERIMENT: YGG-C13

QUESTION
Which half of the accepted onset bracket (0.1328125, 0.13671875] contains the learned-control interaction onset?

FROZEN
All C9-C13 manifests, C6 factorial lesions, learned weights, task, retention definition, interaction classification, duplicate checks, restoration checks, and lineage gates remain exact.

TEST ALPHAS
0.1328125
0.134765625
0.13671875

ANCHORS
alpha=.1328125 duplicate SHA:
35a4341d528efdee8dd14320b132f1d01727987dcadb1c4cd3bd903a8d856a55
must remain non-interaction.

alpha=.13671875 duplicate SHA:
90f0869984ed21292635bdad3be26859645f3a837b325eb22e083b4a1a24414b
must remain interaction-driven with context slots A,C.

CLASSIFICATION
If alpha=.134765625 is interaction-driven:
ONSET_BETWEEN_01328125_AND_0134765625
Else:
ONSET_BETWEEN_0134765625_AND_013671875

SUCCESS
YGG_C14_LEARNED_BLEND_ONSET_FIFTH_BISECTION=true iff all anchor, validity, duplicate, matching, lineage, restoration, and classification gates pass.

FAILURE
Do not alter alpha values, lesions, weights, thresholds, seeds, task, or classification rules after results.

BOUNDARY
No accepted source mutation.
No weight update.
No online adaptation.
No recursive self-modification.
