YGG-A52 CLOSURE
Run 36309892412 SHA 3e29836be8ed6db9735edc7bb3643cd0ebac66cd
Classification: BOTH_LABELS_INDEPENDENTLY_REQUIRED
Valid: true. Duplicate SHA256 811d18e86a51f9f3a7e02d008828aa4c330b93e5b3bd2a0d66ac30bd47bbb7da.
Both U_A0 and U_A25 produced:
NATIVE 118=C,119=S -> collapse
FLIP_118_ONLY 118=S,119=S -> no collapse
FLIP_119_ONLY 118=C,119=C -> no collapse
FLIP_BOTH 118=S,119=C -> no collapse
Bits/program identities, rid/t, corruption set [16,38,146,118], and the other158 arrivals remained fixed.
Interpretation: both labels of the ordered 118=C -> 119=S pair are independently necessary for the observed failure.
Plain speak: it is not just request118 being C or request119 being S. The exact C-then-S pair at that moment is required; changing either side breaks the failure.
Next: preserve 118=C,119=S and perturb only the immediate outer neighbors117 and120 to test whether the pair is locally sufficient or depends on a broader four-request stream context.
