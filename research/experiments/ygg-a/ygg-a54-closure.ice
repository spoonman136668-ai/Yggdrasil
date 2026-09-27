YGG-A54 CLOSURE
Run 36310814545 SHA 169a0b6c1c843af73f9a764fb9446ddc0fabb204
Classification: MIXED_OUTER_CONTEXT
Valid: true. Duplicate SHA256 0a908122ca5be10c6dea5ffb206345f8c66281044d39879f5cd7140a11fcf12e.
Both U_A0 and U_A25 produced:
NATIVE 116..121=C,S,C,S,C,S -> collapse
FLIP_116_ONLY S,S,C,S,C,S -> no collapse
FLIP_121_ONLY C,S,C,S,C,C -> collapse
FLIP_116_121 S,S,C,S,C,C -> collapse
The required 118..120=C,S,C triplet remained fixed in every arm.
Interpretation: the triplet is not sufficient under the single 116 C->S perturbation, but the effect disappears when 121 is also flipped. Because the single 116 flip changes the aggregate phase3 C/S count while the double flip restores it, local-history and phase-count explanations remain confounded.
Plain speak: changing request116 alone prevents failure, but compensating with the opposite change at121 brings failure back. We therefore cannot yet say request116 itself is special; the total stream balance may matter.
Next: repeat the 116 C->S perturbation with a distant same-phase S->C compensation at request97, leaving the local 117..121 neighborhood otherwise native. This distinguishes local request116 causality from phase3 stream-count balance.
