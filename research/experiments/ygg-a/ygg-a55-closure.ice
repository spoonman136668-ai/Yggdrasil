YGG-A55 CLOSURE
Run 36312696296 SHA 20604196f3450d0954cfbf7487e5b8fef5f3d115
Classification: DISTANT_97_EFFECT
Valid: true. Duplicate SHA256 19cf061c7ec60ef2c2c1aea9570cf83e3c5ec00634d023b053e3c5ceb419c212.
Both U_A0 and U_A25 produced:
NATIVE: request97=S,116=C, phase3 counts C16/S16 -> collapse.
FLIP_116_ONLY: 97=S,116=S, counts C15/S17 -> no collapse.
FLIP_97_ONLY: 97=C,116=C, counts C17/S15 -> no collapse.
FLIP_116_PLUS_97: 97=C,116=S, counts restored C16/S16 -> no collapse.
The local117..121 neighborhood remained native in every arm.
Interpretation: aggregate phase3 C/S count does not explain the A54 effect. Two widely separated stream-label perturbations, request97 and request116, can independently abolish the same collapse, and count compensation does not restore it. The causal dependency is therefore distributed across phase3 stream history rather than confined to the 118..120 local triplet or a simple count statistic.
Plain speak: failure depends on the exact history of where C and S requests occur, not just how many there are. Changing a stream label far away at97 is enough to stop the same failure.
Next: exhaustively flip each single phase3 stream label one at a time to map how distributed this schedule sensitivity actually is.
