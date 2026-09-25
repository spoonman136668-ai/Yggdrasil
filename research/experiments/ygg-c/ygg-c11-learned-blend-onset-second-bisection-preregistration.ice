TITLE: YGG-C11 Learned-Blend Onset Second Bisection Preregistration
DATE: 2026-09-25
STATUS: PREREGISTERED
LANE: YGG-C
PARENT_CLOSURE: 2cbd1a453bcbd81d52c74ea9b6373bd309ab0757
PARENT_EXPERIMENT: YGG-C10

QUESTION
Which half of the accepted onset bracket (0.125, 0.15625] contains the learned-control interaction onset?

FROZEN
All C9/C10 manifests, C6 factorial lesions, learned weights, task, retention definition, interaction classification, duplicate checks, restoration checks, and lineage gates remain exact.

TEST ALPHAS
0.125
0.140625
0.15625

ANCHORS
alpha=.125 duplicate SHA:
9f6a7bf9f64ee726a1f705a17cce22c99a9996d2dfa883c0740c3d2fc8bbfc26
must remain non-interaction.

alpha=.15625 duplicate SHA:
8d45e4d0eec68f45b7816dea68a7d74e02b5db7e698cb6c6f1d524c15b840c89
must remain interaction-driven with context slots A,C.

CLASSIFICATION
If alpha=.140625 is interaction-driven:
ONSET_BETWEEN_0125_AND_0140625
Else:
ONSET_BETWEEN_0140625_AND_015625

SUCCESS
YGG_C11_LEARNED_BLEND_ONSET_SECOND_BISECTION=true iff all anchor, validity, duplicate, matching, lineage, restoration, and classification gates pass.

FAILURE
Do not alter alpha values, lesions, weights, thresholds, seeds, task, or classification rules after results.

BOUNDARY
No accepted source mutation.
No weight update.
No online adaptation.
No shared-baseline promotion.
No recursive self-modification.
