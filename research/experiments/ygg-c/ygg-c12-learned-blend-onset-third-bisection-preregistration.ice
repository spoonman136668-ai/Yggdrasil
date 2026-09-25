TITLE: YGG-C12 Learned-Blend Onset Third Bisection Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_CLOSURE: a05b34d574d5c16d31bc33d9eb89e6e7640f2c8b
PARENT_EXPERIMENT: YGG-C11

QUESTION
Which half of the accepted onset bracket (0.125, 0.140625] contains the learned-control interaction onset?

FROZEN
All C9-C11 manifests, C6 factorial lesions, learned weights, task, retention definition, interaction classification, duplicate checks, restoration checks, and lineage gates remain exact.

TEST ALPHAS
0.125
0.1328125
0.140625

ANCHORS
alpha=.125 duplicate SHA:
9f6a7bf9f64ee726a1f705a17cce22c99a9996d2dfa883c0740c3d2fc8bbfc26
must remain non-interaction.

alpha=.140625 duplicate SHA:
8e1d685d6eb4242ed271475002708c95773b1c1cda13622f42ac1739fd8f70ff
must remain interaction-driven with context slots A,C.

CLASSIFICATION
If alpha=.1328125 is interaction-driven:
ONSET_BETWEEN_0125_AND_01328125
Else:
ONSET_BETWEEN_01328125_AND_0140625

SUCCESS
YGG_C12_LEARNED_BLEND_ONSET_THIRD_BISECTION=true iff all anchor, validity, duplicate, matching, lineage, restoration, and classification gates pass.

FAILURE
Do not alter alpha values, lesions, weights, thresholds, seeds, task, or classification rules after results.

BOUNDARY
No accepted source mutation.
No weight update.
No online adaptation.
No recursive self-modification.
