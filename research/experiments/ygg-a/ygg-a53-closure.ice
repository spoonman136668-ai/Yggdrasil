YGG-A53 CLOSURE
Run 36310331783 SHA a8d03bd19c01a8738cafb9ba4849cdef29d939dc
Classification: RIGHT_NEIGHBOR_REQUIRED
Valid: true. Duplicate SHA256 3a56b13dd8cb0b2dd0e8f3f26cc6d84539e578dae1493683f0f6dd127db863d6.
Both U_A0 and U_A25 produced:
NATIVE [117..120]=S,C,S,C -> collapse
FLIP_117_ONLY C,C,S,C -> collapse
FLIP_120_ONLY S,C,S,S -> no collapse
FLIP_117_120 C,C,S,S -> no collapse
The required 118=C,119=S pair was held fixed in every arm.
Interpretation: request117 is not required, but request120=C is required. The local causal stream pattern therefore extends directionally to the right as 118=C -> 119=S -> 120=C.
Plain speak: the failure needs C-S-C across requests118-120. What happened immediately before that at117 does not matter.
Next: preserve 118-120=C,S,C and perturb the next-right request121, with request116 as a matched left-context control, to test whether the causal history extends farther right.
